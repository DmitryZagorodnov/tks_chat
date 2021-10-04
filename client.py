import socket
import threading
import os
import sys

FORMAT = "utf-8"
HEADER = 64
PORT = 5050
DISCONNECT_COMMAND = "!DISCONNECT"
SERVER = "192.168.0.5"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
connected = True


def get_message(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)  # Waits til some message will come throw the socket
    if not msg_length:
        print('')
    else:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


login_message = input("Write !LOGIN [name] to login the server\n")
send(login_message)

while True:
    try:
        get_message(client)
        msg = input()
        send(msg)
    except ConnectionAbortedError:
        print("You haven't logged to the server. Rerun the executable file")
    '''except ValueError:
        pass'''
