import socket
import os
import logging

HOST, PORT = 'localhost', 8080
WWW_DIR = 'www'

# Configura il logging su file
logging.basicConfig(
    filename='server.log',         # Nome file di log
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_content_type(file_path):
    if file_path.endswith('.html'):
        return 'text/html'
    elif file_path.endswith('.css'):
        return 'text/css'
    elif file_path.endswith('.js'):
        return 'application/javascript'
    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        return 'image/jpeg'
    elif file_path.endswith('.png'):
        return 'image/png'
    elif file_path.endswith('.webp'):
        return 'image/webp'
    else:
        return 'application/octet-stream'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    logging.info(f"Server avviato su http://{HOST}:{PORT}")

    while True:
        client_connection, client_address = server_socket.accept()
        with client_connection:
            request = client_connection.recv(1024).decode('utf-8', errors='ignore')
            if not request:
                continue
            
            first_line = request.splitlines()[0]
            logging.info(f"Richiesta da {client_address}: {first_line}")

            try:
                method, path, _ = first_line.split()
            except ValueError:
                response = 'HTTP/1.1 400 Bad Request\r\n\r\nBad Request'
                client_connection.sendall(response.encode())
                logging.warning(f"Richiesta malformata da {client_address}")
                continue

            if method != 'GET':
                response = 'HTTP/1.1 405 Method Not Allowed\r\n\r\nMethod Not Allowed'
                client_connection.sendall(response.encode())
                logging.warning(f"Metodo non supportato da {client_address}: {method}")
                continue
            
            if path == '/':
                path = '/index.html'

            file_path = os.path.join(WWW_DIR, path.lstrip('/'))

            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                content_type = get_content_type(file_path)
                response_headers = (
                    'HTTP/1.1 200 OK\r\n'
                    f'Content-Type: {content_type}\r\n'
                    f'Content-Length: {len(content)}\r\n'
                    'Connection: close\r\n'
                    '\r\n'
                )
                client_connection.sendall(response_headers.encode() + content)
                logging.info(f"Servito {path} a {client_address}")
                
            else:
                response_body = '<h1>404 Not Found</h1>'
                response_headers = (
                    'HTTP/1.1 404 Not Found\r\n'
                    'Content-Type: text/html\r\n'
                    f'Content-Length: {len(response_body)}\r\n'
                    'Connection: close\r\n'
                    '\r\n'
                )
                client_connection.sendall(response_headers.encode() + response_body.encode())
                logging.warning(f"File non trovato {path} richiesto da {client_address}")
