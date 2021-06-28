import socket

target_host = "192.168.254.3"
target_port = 2008

print(target_host, target_port)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host, target_port))

client.send(b"Hello")

response = client.recv(4096)

client.close()

print(response)
