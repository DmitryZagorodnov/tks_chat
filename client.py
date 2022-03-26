import socket
import threading
import time
from commands import Command
from messages import Message

FORMAT = "utf-8"
HEADER = 10

SERVER = "192.168.0.107"
PORT = 5050
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


"""
Gets messages from the server. If message started with GET_FILE_COMMAND it is getting file's size and waiting for the
file to write 
"""


def get_message(conn):
    try:
        msg_length = conn.recv(HEADER).decode(FORMAT)  # Waits til some message will come throw the socket
        msg_length = int(msg_length)
        msg = conn.recv(msg_length)
        message = msg.decode(FORMAT)
        return message
    except ConnectionAbortedError:
        return "Rerun the executable file"


def get_file(conn):
    file_length = conn.recv(HEADER).decode(FORMAT)
    if not file_length:
        return -1
    else:
        file_length = int(file_length)
        file = b""
        current_length = 0
        while current_length < file_length:
            file += conn.recv(file_length - current_length)
            current_length = len(file)
    return file


def message_assembly():
    while True:
        msg_type = get_message(client)
        if msg_type == "usual":
            current_time = time.asctime()
            nickname = get_message(client)
            msg = get_message(client)
            print(f"<{current_time}> [{nickname}] {msg}")
        elif msg_type == "file":
            name = get_message(client)
            image = get_file(client)
            with open(name, 'wb') as file:
                file.write(image)
        elif msg_type == "service":
            msg = get_message(client)
            if msg == Message.LOGIN_ERROR_MESSAGE.value or msg == Message.CONNECTION_ENDED_MESSAGE.value:
                print(msg)
                break
            else:
                print(msg)


"""
Converts the image to the string of bytes
"""


def attach_file(path):
    with open(path, 'rb') as image:
        file = image.read()
        return file


def send(msg):
    try:
        if type(msg) == str:
            message = msg.encode(FORMAT)
        else:
            message = msg
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)
    except ConnectionResetError:
        print("Server is not available")


"""
Sends messages to the server. If it is ADD_FILE_COMMAND sends service message and file to the server
"""


def send_message():
    while True:
        try:
            msg = input()
            if msg.startswith(Command.LOGIN_COMMAND.value):
                send('service')
                send(Message.LOGIN_MESSAGE.value)
                send(msg.split()[len(msg.split())-1])
            elif msg.startswith(Command.DISCONNECT_COMMAND.value):
                send('service')
                send(Message.DISCONNECT_MESSAGE.value)
            elif msg.startswith(Command.ADD_FILE_COMMAND.value):
                path = msg.split()[1]
                image = attach_file(path)
                send('file')
                send(path)
                send(image)
            else:
                send('usual')
                send(msg)
        except ConnectionAbortedError:
            print("Rerun the executable file")


"""
Starting the threads to get and to send messages
"""

print(f"Write {Command.LOGIN_COMMAND.value} [name] to login the server")

while True:
    getting_thread = threading.Thread(target=message_assembly)
    sending_thread = threading.Thread(target=send_message)
    getting_thread.start()
    sending_thread.start()
    getting_thread.join()
    sending_thread.join()
