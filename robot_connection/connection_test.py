

from next_move import NextMove
from robot_connection.socket_connection import SocketConnection


def connection_test():
    conn = SocketConnection(retries=5, delay=2)

    if conn.connect():
        print("Connected!")

        next_move = NextMove(next_ball=[1, 1], robot_coords=[
            10, 10], robot_angle=10)
        conn.send_next_move(next_move)
        conn.close()
    else:
        print("Failed to connect after several attempts.")


