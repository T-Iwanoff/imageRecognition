# echo-server.py
import json
import socket

from next_move import NextMove

# HOST = "192.168.43.134"  # Standard loopback interface address (localhost)
# HOST = '192.168.17.79' # insert pc ipv4 here (find in terminal with ipconfig command)
HOST = '192.168.17.232' # Mads
PORT = 10000  # Port to listen on, we are using 10000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            with open('test.json') as f:
                data = json.load(f)
                f.close()
            next_move = (str(data) + '\n').encode()
            conn.send(next_move)
            print(next_move)

