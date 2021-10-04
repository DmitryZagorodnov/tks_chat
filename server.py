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

clients_list = {}

print(SERVER)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def send_message(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)


def handle_client(conn, addr):
    print("in hc")
    connected = True

    if addr not in clients_list:
        login_message = get_message(conn)
        if login_message.startswith(LOGIN_COMMAND):
            clients_list[addr] = [login_message.split()[1], 'connected', conn]
        else:
            connected = False
    else:
        clients_list[addr][1] = 'connected'

    print("b4 if conn")

    if connected:
        print(f"\nNEW CONNECTION: {clients_list[addr][0]} connected", end='\n')
        print(f"THE NUMBER OF CURRENT CONNECTIONS {threading.activeCount() - 1}")
        send_message(conn, "You are logged in")
        print(clients_list)

    while connected:
        message = get_message(conn)
        if message:
            ans = f"<{time.asctime()}> [{clients_list[addr][0]}] {message}"
            print(ans)
            for addr in clients_list:
                if clients_list[addr][1] == 'connected':
                    send_message(clients_list[addr][2], ans)

    conn.close()


def disconnect(conn):
    for addr in clients_list:
        if clients_list[addr][2] == conn:
            clients_list[addr][1] = 'disconnected'
            print(f"[{clients_list[addr][0]}] DISCONNECTED FROM THE SERVER")


def get_message(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)  # Waits til some message will come throw the socket
    if not msg_length:
        return ''
    else:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        if msg.startswith(DISCONNECT_COMMAND):
            disconnect(conn)
        else:
            return msg


def start():
    server.listen()
    print(f'SERVER IS LISTENING ON {SERVER}')
    while True:
        conn, addr = server.accept()            # Blocking and waiting for the new connection
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


print("STARTING SERVER")
start()
