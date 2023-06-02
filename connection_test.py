

from robot_connection.socket_connection import SocketConnection


def connection_test():
    conn = SocketConnection(retries=5, delay=2)


    if conn.connect():
        print("Connected!")
        conn.send("Hello, world!")
        print(conn.receive())
        conn.close()
    else:
        print("Failed to connect after several attempts.")



