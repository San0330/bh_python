#!/usr/bin/env python3

import sys
import socket
import threading


def hexdump(src, length=16):
    print(src)
    return src

    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i : i + length]
        hexa = b" ".join(["%0*X" % (digits, ord(str(x))) for x in s])
        text = b"".join([x if 0x20 <= ord(x) < 0x7F else b"." for x in s])
        result.append(b"%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))
        print(b"\n".join(result))


def receive_from(connection):
    buffer = b""

    # We set a 5 second time-out. Depending on your target this may need
    # to be adjusted
    connection.settimeout(5)

    try:

        # while True:
        data = connection.recv(4096)
        # if not data:
        #     break
        buffer += data

    except TimeoutError:
        pass

    return buffer


def request_handler(buffer):
    return buffer


def response_handler(buffer):
    return buffer


def proxy_handler(client_socket, remotehost, remoteport, receive_first):

    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remotehost, remoteport))

    if receive_first:

        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        remote_buffer = response_handler(remote_buffer)

        if len(remote_buffer):

            print(f"[<==] Sending {len(remote_buffer)} bytes to localhost")
            client_socket.send(remote_buffer)

    while True:

        local_buffer = receive_from(client_socket)

        print(local_buffer)

        if len(local_buffer):
            print(f"[==>] received {len(local_buffer)} bytes to localhost")

            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)

            remote_socket.send(local_buffer)

            print("[==>] sent to remote")

        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)

            client_socket.send(remote_buffer)

            print("[<==] send to localhost")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()

            print("[*] No more data, closing connections")
            break


def serverloop(localhost, localport, remotehost, remoteport, recvFirst):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((localhost, localport))
    except socket.error as exc:
        print("[!!] Failed to listen on %s:%d" % (localhost, localport))
        print("[!!] Check for other listening sockets or correct " "permissions.")
        print(f"[!!] Caught exception error: {exc}")
        sys.exit(0)

    print(f"Listening {localhost}:{localport}")

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print(f"[==>] Receiving connection from {addr[0]} {addr[1]}")

        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remotehost, remoteport, recvFirst),
        )
        proxy_thread.start()


def main():

    if len(sys.argv[1:]) != 5:
        print(
            "Usage ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]"
        )
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    localhost = sys.argv[1]
    localport = int(sys.argv[2])

    remotehost = sys.argv[3]
    remoteport = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    serverloop(localhost, localport, remotehost, remoteport, receive_first)


main()

