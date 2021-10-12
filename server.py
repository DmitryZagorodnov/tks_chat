import socket
import threading
import time

FORMAT = "utf-8"
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_COMMAND = "!DISCONNECT"
LOGIN_COMMAND = "!LOGIN"
ADD_FILE_COMMAND = "!ATTACH"
SEND_FILE_COMMAND = "!FILE COMES NEXT"

clients_list = {}
clients_online = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
mutex = threading.Lock()

"""
This function is needed to remove the disconnected users from the server. Also notifies them of disconnection 
"""


def disconnect(conn):
    for login in clients_list:
        if clients_list[login] == conn:
            print(f"[{login}] DISCONNECTED FROM THE SERVER")
            send_message(conn, "YOU ARE DISCONNECTED FROM THE SERVER")
            clients_online.remove(login)


"""
Gets a messages from the client's socket. Firstly gets a length of the message comes next, then it itself 
"""


def get_message(conn):
    try:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if not msg_length:
            return ''
        else:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg.startswith(DISCONNECT_COMMAND):
                disconnect(conn)
                return -1
            else:
                return msg
    except ConnectionResetError:
        disconnect(conn)
        return -1


"""
Gets a socket and message to send. Firstly sending the length of the message complemented to the HEADER's size to the
client's socket, secondly sending the message. If it is not possible to send disconnects current client from the server
"""


def send_message(conn, msg):
    try:
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)
        conn.send(message)
    except ConnectionResetError:
        disconnect(conn)


"""
If you need to send the file, call this function. It firstly sends a service message with a name of the file, secondly 
sending a file size and thirdly the file itself like a string of bytes  
"""


def send_file(conn, name, file):
    send_message(conn, SEND_FILE_COMMAND + " " + name)
    file_length = len(file)
    send_length = str(file_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(file)


"""
Main function that receives messages from clients and sends them back. Waits a LOGIN_COMMAND as first message and starts
to handle client if it is right. When user disconnects closing the connection. 
"""


def handle_client(conn, addr):
    global connected
    connected = True

    login_message = get_message(conn)
    if login_message != -1 and login_message.startswith(LOGIN_COMMAND):
        login = login_message.split()[1]
        if login in clients_online:
            connected = False
        else:
            clients_online.append(login)
            clients_list[login] = conn
    else:
        send_message(conn, "YOU ARE NOT LOGGED INTO THE SERVER. RERUN THE EXECUTABLE FILE")
        connected = False

    if connected:
        print(f"\nNEW CONNECTION: {login} connected", end='\n')
        print(f"THE NUMBER OF CURRENT CONNECTIONS {threading.activeCount() - 1}")
        send_message(conn, "You are logged in")
    while connected:
        message = get_message(conn)
        if message == -1:
            connected = False
            break
        elif message.startswith(ADD_FILE_COMMAND):
            name = message.split()[1]
            print(f"<{time.asctime()}> [{login}] is sending a file {name}")
            image_length = conn.recv(HEADER).decode(FORMAT)
            image_length = int(image_length)
            image = conn.recv(image_length)
            mutex.acquire()
            for client in clients_online:
                if client != login:
                    send_file(clients_list[client], name, image)
                else:
                    send_message(clients_list[client], "Your file has been delivered")
            mutex.release()
        elif message:
            ans = f"<{time.asctime()}> [{login}] {message}"
            print(ans)
            mutex.acquire()
            for client in clients_online:
                send_message(clients_list[client], ans)
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
