import socket
import threading
import time

FORMAT = "utf-8"
SERVICE_HEADER = 10
FILE_HEADER = 64
TYPE_HEADER = 2
TIME_HEADER = 2
NICKNAME_HEADER = 2
MESSAGE_HEADER = 64
PORT = 5050
LOGIN_COMMAND = "!LOGIN"
DISCONNECT_COMMAND = "!DISCONNECT"
ADD_FILE_COMMAND = "!ATTACH"
GET_FILE_COMMAND = "!FILE COMES NEXT"
DISCONNECT_MESSAGE = "!DISCONNECT"
LOGIN_MESSAGE = "!LOGIN"
LOGIN_ERROR_MESSAGE = "YOU ARE NOT LOGGED INTO THE SERVER. RERUN THE EXECUTABLE FILE"
CONNECTION_ENDED_MESSAGE = "YOU ARE DISCONNECTED FROM THE SERVER"
SERVER = "172.29.192.1"
ADDR = (SERVER, PORT)
TIMEZONE = time.timezone
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
connected = True


"""
Gets messages from the server. If message started with GET_FILE_COMMAND it is getting file's size and waiting for the
file to write 
"""


def get_message(conn, header):
    try:
        msg_length = conn.recv(header).decode(FORMAT)  # Waits til some message will come throw the socket
        msg_length = int(msg_length)
        try:
            msg = conn.recv(msg_length).decode(FORMAT)
        except:
            msg = conn.recv(msg_length)
        return msg
    except ConnectionAbortedError:
        return "Rerun the executable file"
    except ValueError:
        return "You haven't logged to the server"
    except ConnectionResetError:
        return "Server is not available"


def message_assembly():
    while True:
        msg_type = get_message(client, TYPE_HEADER)
        if msg_type == "usual":
            t = get_message(client, TIME_HEADER)
            t = time.strptime(t)
            t = time.mktime(t)
            tz = get_message(client, TIME_HEADER)
            t += int(tz)
            t -= int(TIMEZONE)
            t = time.ctime(t)
            nickname = get_message(client, NICKNAME_HEADER)
            msg = get_message(client, MESSAGE_HEADER)
            print(f"<{t}> [{nickname}] {msg}")
        elif msg_type == "file":
            name = get_message(client, MESSAGE_HEADER)
            image = get_message(client, FILE_HEADER)
            with open(name, 'wb') as file:
                file.write(image)
            print(f"You received a file named {name}")
        elif msg_type == "service":
            msg = get_message(client, SERVICE_HEADER)
            if msg == LOGIN_ERROR_MESSAGE:
                print("Rerun the executable file and try to login correctly")
                break
            elif msg == CONNECTION_ENDED_MESSAGE:
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
        send_length += b' ' * (MESSAGE_HEADER - len(send_length))
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
            if msg.startswith(LOGIN_COMMAND):
                send('service')
                send(LOGIN_MESSAGE)
                send(msg.split()[1])
            elif msg.startswith(DISCONNECT_COMMAND):
                send('service')
                send(DISCONNECT_MESSAGE)
            elif msg.startswith(ADD_FILE_COMMAND):
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

print("Write !LOGIN [name] to login the server")

while True:
    getting_thread = threading.Thread(target=message_assembly)
    sending_thread = threading.Thread(target=send_message)
    getting_thread.start()
    sending_thread.start()
    getting_thread.join()
    sending_thread.join()
