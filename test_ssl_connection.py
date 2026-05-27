import ssl
import socket

hostname = 'smtp.gmail.com'
port = 465
context = ssl.create_default_context()

try:
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f"SSL connection established. SSL version: {ssock.version()}")
except Exception as e:
    print(f"Error: {e}")
