#!/usr/bin/env python3

import socket
import threading
import argparse
import sys
import subprocess

listen = False
command = False
target = ""
port = 0
upload = ""
execute = ""

# Function to run command, send by client
def run_command(cmd):
    cmd = cmd.rstrip()
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    return output


# receive input from client & send back the output
def client_handler(client):
    global command
    global upload
    global execute

    if len(upload):
        client.send("Write".encode("utf-8"))

        file_buffer = b""
        while True:
            data = client.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client.send(b"Successfully saved file to %s\r\n" % upload)
        except:
            client.send(b"Failed to upload")

    if len(execute):
        output = run_command(execute)
        client.send(b"executed" + output)

    if command:
        while True:
            client.send("<BHP:#>".encode("utf-8"))
            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client.recv(1024)

            response = run_command(cmd_buffer)
            client.send(response)


# Server function
def server_loop():
    global target
    global port

    if not len(target):
        target = socket.gethostbyname(socket.gethostname())

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    print(f"Server listening on {target}:{port}")

    while True:
        client, addr = server.accept()
        server_thread = threading.Thread(target=client_handler, args=(client,))
        server_thread.start()


# Client Function, send commands & recieve ouput
def client_sender(buffer):
    global target
    global port

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))

        if len(buffer):
            client.send(buffer.encode("utf-8"))

        while True:
            recv_len = 1
            response = b""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print(response.decode("utf-8"))

            buffer = input()
            buffer += "\n"

            client.send(buffer.encode("utf-8"))

    except socket.error as err:

        print("[*] Exception ! Exiting.")
        print(f"[*] Caught exception socket.error:{err}")

        client.close()


def main():

    global listen
    global command
    global target
    global port
    global upload
    global execute

    if not len(sys.argv[:1]):
        print("type './bhpnet.py -h' to get help")
        exit(1)

    parser = argparse.ArgumentParser(description="Something")
    parser.add_argument("-l", "--listen", action="store_true")
    parser.add_argument("-t", "--target", default="")
    parser.add_argument("-p", "--port", default=0, type=int)
    parser.add_argument("-c", "--command", action="store_true")
    parser.add_argument("-u", "--upload", default="")
    parser.add_argument("-e", "--execute", default="")

    args = parser.parse_args()

    listen = args.listen
    command = args.command
    port = args.port
    target = args.target
    upload = args.upload
    execute = args.execute

    if not listen and len(target) and port > 0:
        # Press ^D to end reading from stdin ( bypass stdin read )
        buffer = sys.stdin.read()
        # Send the command to server
        client_sender(buffer)
    if listen:
        server_loop()


main()

