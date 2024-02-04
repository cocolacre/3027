import socket
import threading
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 13337))
s.listen(5)

def handle_client(client_socket, addr):
    data = client_socket.recv(1024)
    dwValue = int.from_bytes(data, "little")
    print("Received DWORD value:", dwValue)

    message = data.decode('utf-8')
    print(f"[{time.ctime()}][{addr}] CLIENT WAS IDLE FOR " + str(dwValue) + " milliseconds.")
    client_socket.close()

while True:
    client_socket, addr = s.accept()
    #print(dir(client_socket.r))
    client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_thread.start()