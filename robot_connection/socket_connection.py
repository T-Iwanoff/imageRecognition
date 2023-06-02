

import socket
from next_move import NextMove

ev3_host = '192.168.187.107'  # Replace with the IP address of your EV3 robot
# ev3_host = '10.0.1.1' # access point 1
# ev3_host = '192.168.48.208'  # access point+
# ev3_host = '0.0.0.0'
port = 10000  # Choose the same port number as in the Java program


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ev3_host, port))


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

def send_coords(x, y):
    s.sendall(x.encode())
    s.sendall(y.encode())

def send_next_move(next_move: NextMove):
    s.sendall(next_move.robot_coords[0].encode())
    s.sendall(next_move.robot_coords[1].encode())
    s.sendall(next_move.robot_angle.encode())
    s.sendall(next_move.next_ball[0].encode())
    s.sendall(next_move.next_ball[1].encode())

