
from course import Course
from image_recognition.analyse_image import analyse_image
from next_move import NextMove
from robot_connection.connection_test import *

# IMAGE, VIDEO, CAMERA or ROBOT
# analyse_image(path='Media/Video/MovingBalls.mp4', media='VIDEO')

# analyse_image(path='Media/Video/Balls3.mp4', media='VIDEO')

analyse_image(path='Media/Video/robot.mp4', media='VIDEO', mac_camera=False, connect=False)

# analyse_image(path='Media/Image/Corner2.jpg', media='IMAGE', connect=False)

# analyse_image(media='MAC_CAMERA')

# analyse_image(path='Media/Image/Cluster2.jpg', media='IMAGE')

# connection_test()
