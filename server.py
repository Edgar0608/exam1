import socket
import json
import threading
import queue

HOST = 'localhost'
PORT = 12345
BOARD_SIZE = 100
WIN_COUNT = 5


board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
move_queue = queue.Queue(maxsize=50)  
board_lock = threading.Lock()

def check_win(x, y, symbol):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dx, dy in directions:
        count = 1
        for sign in [1, -1]:
            nx, ny = x, y
            while True:
                nx += dx * sign
                ny += dy * sign
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == symbol:
                    count += 1
                else:
                    break
        if count >= WIN_COUNT:
            return True
    return False

def worker_thread():
    """Потік, який послідовно обробляє чергу запитів"""
    while True:
        conn, move_data = move_queue.get()
        try:
            move = json.loads(move_data.decode())
            x, y, symbol = move['x'], move['y'], move['symbol'].upper()
            
            with board_lock: 
                if board[x][y] == '.':
                    board[x][y] = symbol
                    if check_win(x, y, symbol):
                        conn.send(f'Player {symbol} wins!'.encode())
                    else:
                        conn.send(b'Move accepted')
                else:
                    conn.send(b'Cell already occupied')
        except Exception as e:
            conn.send(f'Error processing: {e}'.encode())
        finally:
            move_queue.task_done()

def handle_client(conn, addr):
    """Потік для кожного підключеного клієнта"""
    print(f"Connected by {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data: break
                
               
                try:
                    move_queue.put((conn, data), timeout=2) 
                except queue.Full:
                    conn.send(b'Server queue is full. Try again later.')
            except:
                break
    print(f"Disconnected {addr}")


threading.Thread(target=worker_thread, daemon=True).start()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server started. Waiting for clients...")
    while True:
        conn, addr = s.accept()
        
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()