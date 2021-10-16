import socket
import threading
import time


FORMAT = "utf-8"
SERVICE_HEADER = 10
FILE_HEADER = 64
TYPE_HEADER = 2
TIME_HEADER = 2
NICKNAME_HEADER = 2
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_COMMAND = "!DISCONNECT"
LOGIN_COMMAND = "!LOGIN"
ADD_FILE_COMMAND = "!ATTACH"
SEND_FILE_COMMAND = "!FILE COMES NEXT"
LOGIN_ERROR_MESSAGE = "YOU ARE NOT LOGGED INTO THE SERVER. RERUN THE EXECUTABLE FILE"
CONNECTION_ENDED_MESSAGE = "YOU ARE DISCONNECTED FROM THE SERVER"

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
            print(f"[{login}] DISCONNECTED FROM THE SERVER")
            assembly_message_to_send(conn, type='service', msg=CONNECTION_ENDED_MESSAGE)
            clients_online.remove(login)


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
            try:
                new = msg.decode(FORMAT)
                return new
            except UnicodeDecodeError:
                return msg

    except ConnectionResetError:
        disconnect(conn)
        return -1


"""
Gets a socket and message to send. Firstly sending the length of the message complemented to the HEADER's size to the
client's socket, secondly sending the message. If it is not possible to send disconnects current client from the server
"""


def send_message(conn, header, msg):
    try:
        if type(msg) == str:
            message = msg.encode(FORMAT)
        else:
            message = msg
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (header - len(send_length))
        conn.send(send_length)
        conn.send(message)
    except ConnectionResetError:
        disconnect(conn)


def assembly_message_to_send(conn, type, msg, nickname=None, file_name=None):
    send_message(conn=conn, header=TYPE_HEADER, msg=type)
    if type == 'usual' and nickname is not None:
        t = time.ctime(time.mktime(time.strptime(time.asctime())) - 3600)
        tz = str(-7200)
        send_message(conn=conn, header=TIME_HEADER, msg=t)
        send_message(conn=conn, header=TIME_HEADER, msg=tz)
        send_message(conn=conn, header=NICKNAME_HEADER, msg=nickname)
        send_message(conn=conn, header=HEADER, msg=msg)
    elif type == 'file' and file_name is not None:
        send_message(conn, HEADER, file_name)
        send_message(conn, FILE_HEADER, msg)
    elif type == 'service':
        send_message(conn, SERVICE_HEADER, msg)


def assembly_message_to_receive(conn):
    type = get_message(conn)
    msg = get_message(conn)
    if type == 'usual':
        return msg
    elif type == 'service':
        if msg == DISCONNECT_COMMAND:
            disconnect(conn)
            return -1
        elif msg == LOGIN_COMMAND:
            login = get_message(conn)
            if login in clients_online:
                return -1
            else:
                clients_list[login] = conn
                clients_online.append(login)
                return 1
    elif type == 'file':
        name = msg
        print(f"<{time.asctime()}> [{get_login_by_conn(conn)}] is sending a file {name}")
        file = get_message(conn)
        return name, file


"""
Main function that receives messages from clients and sends them back. Waits a LOGIN_COMMAND as first message and starts
to handle client if it is right. When user disconnects closing the connection. 
"""


def handle_client(conn, addr):
    global connected
    connected = True
    if assembly_message_to_receive(conn) != 1:
        assembly_message_to_send(conn, type='service', msg=LOGIN_ERROR_MESSAGE)
        connected = False
    else:
        login = get_login_by_conn(conn)
    if connected:
        print(f"\nNEW CONNECTION: {login} connected", end='\n')
        print(f"THE NUMBER OF CURRENT CONNECTIONS {threading.activeCount() - 1}")
        assembly_message_to_send(conn, 'service', "You are logged in")

    while connected:
        message = assembly_message_to_receive(conn)
        if message == -1:
            connected = False
            break
        elif type(message) == str:
            t = time.ctime(time.mktime(time.strptime(time.asctime())) - 3600)
            print(f"<{t}> [{login}] {message}")
            for man in clients_online:
                mutex.acquire()
                assembly_message_to_send(conn=clients_list[man], type='usual', msg=message, nickname=login)
                mutex.release()
        else:
            for man in clients_online:
                if man != login:
                    mutex.acquire()
                    assembly_message_to_send(conn=clients_list[man], type='file', msg=message[1], file_name=message[0])
                    assembly_message_to_send(conn=clients_list[man], type='service', msg=f"You've got a file named "
                                                                                        f"{message[0]} from {login}")
                    mutex.release()
                else:
                    mutex.acquire()
                    assembly_message_to_send(conn=clients_list[man], type='service', msg=f"Your file {message[0]} has "
                                                                                        f"been delivered")
                    mutex.release()

        connected = login in clients_online
    conn.close()


"""
This function makes the server listening for new connections. When it occurs starting a thread for each new client 
"""


def start():
    server.listen()
    print(f'SERVER IS LISTENING ON {SERVER}')
    while True:
        conn, addr = server.accept()  # Blocking and waiting for the new connection
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


print("STARTING SERVER")
start()
