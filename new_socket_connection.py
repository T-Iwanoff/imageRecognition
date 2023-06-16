# echo-server.py
import json
import socket

from next_move import NextMove

HOST = "192.168.43.134"  # Standard loopback interface address (localhost)
# HOST = 'localhost'
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)
            with open('test.json') as f:
                data = json.load(f)
                f.close()
            # data = NextMove(next_ball=(1, 1), move_type="middle", robot_coords=(2, 2), robot_heading=200.0)
            print(data)
            next_move = (str(data) + '\n').encode()
            print(next_move)
            conn.send(next_move)

