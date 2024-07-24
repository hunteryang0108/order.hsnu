import socket
import sys
import threading
from datetime import datetime as dt

addr = '0.0.0.0', 80
redirect = 'https://localhost/'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(addr)
server.listen(128)

print(f'[*] Serving on {addr[0]}:{addr[1]}')
print(f'[*] Redirect: {redirect}')

def handle_client(client_socket):
    try:
        client_socket.send(f'HTTP/1.1 302 Found\r\nLocation: {redirect}\r\nServer: Python/{sys.version.split(None, 1)[0]}\r\nDate: {dt.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}\r\nConnection: Close\r\n\r\n'.encode('UTF-8'))
        client_socket.close()
    except:
        client_socket.close()
    
while True:
    try:
        client, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()
    except:
        pass