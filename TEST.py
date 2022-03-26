st = "фывффв"
HEADER = 10
FORMAT = 'utf-8'
msg_length = len(st)
send_length = str(msg_length).encode(FORMAT)
send_length += b' ' * (HEADER - len(send_length))

print(send_length, len(send_length))
