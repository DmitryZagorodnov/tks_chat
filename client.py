import socket
import threading
import os
import sys

FORMAT = "utf-8"
HEADER = 64
PORT = 5050
DISCONNECT_COMMAND = "!DISCONNECT"
SERVER = "169.254.22.225"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
connected = True


def get_message(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)  # Waits til some message will come throw the socket
    print(msg_length)
    if not msg_length:
        print('')
    else:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        print(msg)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    if msg != DISCONNECT_COMMAND:
        print(client.recv(2048).decode(FORMAT))
    else:
        print("You are disconnected from the server")


input("Write !LOGIN [name] to login the server\n")

while True:
    try:
        get_message(client)
        msg = input()
        send(msg)
    except ConnectionAbortedError:
        print("You haven't logged to the server. Rerun the executable file")
    '''except ValueError:
        pass'''
