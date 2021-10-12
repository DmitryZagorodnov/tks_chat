import socket
import threading

FORMAT = "utf-8"
HEADER = 64
PORT = 5050
DISCONNECT_COMMAND = "!DISCONNECT"
ADD_FILE_COMMAND = "!ATTACH"
GET_FILE_COMMAND = "!FILE COMES NEXT"
SERVER = "172.29.192.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
connected = True


"""
Gets messages from the server. If message started with GET_FILE_COMMAND it is getting file's size and waiting for the
file to write 
"""


def get_message(conn):
    while True:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)  # Waits til some message will come throw the socket
            if not msg_length:
                break
            else:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT)
                if msg.startswith(GET_FILE_COMMAND):
                    name = msg.split()[3]
                    image_length = conn.recv(HEADER).decode(FORMAT)
                    image_length = int(image_length)
                    image = conn.recv(image_length)
                    with open(name, 'wb') as file:
                        file.write(image)
                    print(f"You got the file named {name}")
                else:
                    print(msg)
        except ConnectionAbortedError:
            print("Rerun the executable file")


"""
Converts the image to the string of bytes
"""


def attach_file(path):
    with open(path, 'rb') as image:
        file = image.read()
        return file


"""
Sends messages to the server. If it is ADD_FILE_COMMAND sends service message and file to the server
"""


def send():
    while True:
        try:
            msg = input()
            message = msg.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            client.send(message)
            if msg.startswith(ADD_FILE_COMMAND):
                path = msg.split()[1]
                image = attach_file(path)
                image_length = len(image)
                send_image_length = str(image_length).encode(FORMAT)
                send_image_length += b' ' * (HEADER - len(send_image_length))
                client.send(send_image_length)
                client.send(image)
        except ConnectionAbortedError:
            print("Rerun the executable file")


"""
Starting the threads to get and to send messages
"""

print("Write !LOGIN [name] to login the server")

while True:
    getting_thread = threading.Thread(target=get_message, args=(client, ))
    sending_thread = threading.Thread(target=send)
    getting_thread.start()
    sending_thread.start()
    getting_thread.join()
    sending_thread.join()
