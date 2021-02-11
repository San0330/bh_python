import socket

target_host = socket.gethostbyname(socket.gethostname())
target_port = 9988

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host, target_port))

client.send(b"Hello, world. I am San.")

response = client.recv(4096)

client.close()

print(response)
