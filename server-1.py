import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 13337))
s.listen(5)

def handle_client(client_socket):
    data = client_socket.recv(1024)
    message = data.decode('utf-8')
    print(f"{str(client_socket)}:", message)
    client_socket.close()

while True:
    client_socket, addr = s.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()