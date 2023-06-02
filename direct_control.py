

# import socket
# import sys
# import keyboard 


# def direct_control():
#     # IP address and port number of the EV3Server
#     server_ip = '192.168.187.107'  # Replace with the actual IP address
#     server_port = 10000  # Replace with the actual port number

#     # Connect to the server
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((server_ip, server_port))

#     # Function to send the key press event to the server

#     # Function to send the key press event to the server


#     def send_key_event(key):
#         s.sendall(key.encode())


#     # Start listening to arrow key events
#     keyboard.on_press_key('up', lambda _: send_key_event('forward'))
#     keyboard.on_press_key('down', lambda _: send_key_event('back'))
#     keyboard.on_press_key('left', lambda _: send_key_event('left'))
#     keyboard.on_press_key('right', lambda _: send_key_event('right'))
#     keyboard.on_press_key('q', lambda _: send_key_event('quit'))

#     # Keep the program running until 'q' is pressed
#     keyboard.wait('q')

#     # Close the connection
#     s.close()



