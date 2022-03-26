import socket
import threading
import time
from commands import Command
from messages import Message


FORMAT = "utf-8"
HEADER = 10
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


clients_list = {}
clients_online = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
mutex = threading.Lock()


def get_login_by_conn(conn):
    for login in clients_list:
        if clients_list[login] == conn:
            return login


"""
This function is needed to remove the disconnected users from the server. Also notifies them of disconnection 
"""


def disconnect(conn):
    for login in clients_list:
        if clients_list[login] == conn:
            if login in clients_online:
                clients_online.remove(login)
            print(f"[{login}] DISCONNECTED FROM THE SERVER")
            assembly_message_to_send(conn, msg_type='service', msg=Message.CONNECTION_ENDED_MESSAGE.value)
    return 0


"""
Gets a messages from the client's socket. Firstly gets a length of the message comes next, then it itself 
"""


def get_message(conn):
    try:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if not msg_length:
            return -1
        else:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            new = msg.decode(FORMAT)
            return new
    except ConnectionResetError:
        disconnect(conn)
        return -1


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


"""
Gets a socket and message to send. Firstly sending the length of the message complemented to the HEADER's size to the
client's socket, secondly sending the message. If it is not possible to send disconnects current client from the server
"""


def send_message(conn, msg):
    try:
        if type(msg) == str:
            message = msg.encode(FORMAT)
        else:
            message = msg
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)
        conn.send(message)
    except ConnectionResetError:
        return -1


def assembly_message_to_send(conn, msg_type, msg, nickname=None, file_name=None):
    send_message(conn=conn, msg=msg_type)
    if msg_type == 'usual' and nickname is not None:
        send_message(conn=conn, msg=nickname)
        send_message(conn=conn, msg=msg)
    elif msg_type == 'file' and file_name is not None:
        send_message(conn, file_name)
        send_message(conn, msg)
    elif msg_type == 'service':
        send_message(conn, msg)


def received_message_assembly(conn):
    msg_type = get_message(conn)
    msg = get_message(conn)
    if msg_type == 'usual':
        return msg
    elif msg_type == 'service':
        if msg == Command.DISCONNECT_COMMAND.value:
            disconnect(conn)
            return -1
        elif msg == Command.LOGIN_COMMAND.value:
            login = get_message(conn)
            if login in clients_online:
                return -1
            else:
                clients_list[login] = conn
                clients_online.append(login)
                return 1
    elif msg_type == 'file':
        name = msg
        file = get_file(conn)
        print(f"<{time.asctime()}> [{get_login_by_conn(conn)}] is sending a file {name}")
        return name, file


"""
Main function that receives messages from clients and sends them back. Waits a LOGIN_COMMAND as first message and starts
to handle client if it is right. When user disconnects closing the connection. 
"""


def handle_client(conn, address):
    if received_message_assembly(conn) != 1:
        assembly_message_to_send(conn, msg_type='service', msg=Message.LOGIN_ERROR_MESSAGE.value)
        conn.close()
    else:
        login = get_login_by_conn(conn)
        print(f"\nNEW CONNECTION: {login} connected", end='\n')
        print(f"THE NUMBER OF CURRENT CONNECTIONS {threading.activeCount() - 1}")
        assembly_message_to_send(conn, 'service', "You are logged in")

    while True:
        message = received_message_assembly(conn)
        if message == -1:
            break
        elif type(message) == str:
            t = time.asctime()
            print(f"<{t}> [{login}] {message}")
            for man in clients_online:
                with mutex:
                    assembly_message_to_send(conn=clients_list[man], msg_type='usual', msg=message, nickname=login)
        else:
            for man in clients_online:
                if man != login:
                    with mutex:
                        assembly_message_to_send(conn=clients_list[man], msg_type='file', msg=message[1],
                                                 file_name=message[0])
                        assembly_message_to_send(conn=clients_list[man], msg_type='service',
                                                 msg=f"You've got a file named {message[0]} from {login}")
                else:
                    with mutex:
                        assembly_message_to_send(conn=clients_list[man], msg_type='service', msg=f"Your file {message[0]} "
                                                                                             f"has been delivered")
        if login not in clients_online:
            break
    conn.close()


"""
This function makes the server listening for new connections. When it occurs starting a thread for each new client 
"""


def start():
    server.listen()
    print(f'SERVER IS LISTENING ON {SERVER}')
    while True:
        conn, address = server.accept()  # Blocking and waiting for the new connection
        thread = threading.Thread(target=handle_client, args=(conn, address))
        thread.start()


print("STARTING SERVER")
start()
