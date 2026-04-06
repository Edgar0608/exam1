import socket
import json

HOST = 'localhost'
PORT = 12345

print("--- Клієнт гри Хрестики-Нолики 100x100 ---")

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Підключено до сервера.")

        while True:
            try:
                
                line_x = input("X (0-99) або 'exit': ")
                if line_x.lower() == 'exit': break
                
                x = int(line_x)
                y = int(input("Y (0-99): "))
                symbol = input("Символ (X або 0): ").upper()

                if symbol not in ['X', '0']:
                    print("Помилка: введіть X або 0.")
                    continue

                
                move = {"x": x, "y": y, "symbol": symbol}
                s.sendall(json.dumps(move).encode())

                
                response_data = s.recv(1024).decode()
                if not response_data:
                    print("Сервер розірвав з'єднання.")
                    break
                
                print(f"Відповідь сервера: {response_data}")

            
                if "wins" in response_data.lower() or "виграв" in response_data.lower():
                    print("Гру завершено!")
                    break

            except ValueError:
                print("Будь ласка, вводьте числа для координат.")
            except Exception as e:
                print(f"Виникла помилка: {e}")
                break

except ConnectionRefusedError:
    print("Не вдалося підключитися до сервера. Перевірте, чи він запущений.")

