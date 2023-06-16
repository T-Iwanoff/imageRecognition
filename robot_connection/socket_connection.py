

import json
import time
import socket
from config import ROBOT_IP
from next_move import NextMove
import asyncio
import concurrent.futures


ev3_host = ROBOT_IP
port = 10000  # Choose the same port number as in the Java program


class SocketConnection:

    def __init__(self, host=ev3_host, port=port, retries=3, delay=5):
        self.host = host
        self.port = port
        self.retries = retries
        self.delay = delay
        self.sock = None

    # def to_json(self):
    #     return json.dumps(self.__dict__)

    def connect(self):
        for x in range(self.retries):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                return True
            except socket.error as e:
                print(f"Attempt {x+1} failed. Error: {e}")
                time.sleep(self.delay)  # Wait for a while before retrying
        return False

    def close(self):
        if self.sock:
            self.sock.close()

    def send(self, msg):
        if not self.sock:
            raise RuntimeError("Socket connection is not established")
        self.sock.sendall(msg.encode())

    def receive(self, bufsize=1024):
        if not self.sock:
            raise RuntimeError("Socket connection is not established")
        return self.sock.recv(bufsize).decode()

    # def send_coords(self, x, y):
    #     self.sock.sendall(x.encode())
    #     self.sock.sendall(y.encode())

    def send_next_move(self, next_move: NextMove):
        print(next_move.to_json())
        if not self.sock:
            raise RuntimeError("Socket connection is not established")
        self.sock.sendall(next_move.to_json().encode())
    
    async def async_send_next_move(self, next_move: NextMove):
        print(next_move.to_json())
        if not self.sock:
            raise RuntimeError("Socket connection is not established")

        # Define a blocking function inside the asynchronous function
        def blocking_io():
            self.sock.send((next_move.to_json() + '\n').encode())

        # Run the blocking function in a separate thread
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, blocking_io)


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((ev3_host, port))

# def socket_connection():
#     ev3_host = '192.168.48.107'  # Replace with the IP address of your EV3 robot
#     # ev3_host = '10.0.1.1' # access point 1
#     # ev3_host = '192.168.48.208'  # access point+
#     # ev3_host = '0.0.0.0'
#     port = 10000  # Choose the same port number as in the Java program

#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((ev3_host, port))

#         while True:
#             x = input("Enter x: ") + "\n"
#             y = input("enter y: ") + "\n"
#             s.sendall(x.encode())
#             s.sendall(y.encode())

#             # if message == "quit":
#             #     break
