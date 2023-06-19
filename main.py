from course import Course
from image_recognition.analyse_course import analyse_course
from path_finder.graph_setup1 import create_graph1
from robot_connection.connection_test import *

# IMAGE, VIDEO, CAMERA

# course = Course(ball_types= ["none", "none", "none"], ball_coords=[[0.3, 0.3], [0.4, 0.4], [
#                 0.5, 0.5]], robot_coords=[0.6, 0.6], robot_heading=0, obstacle_coords=[(0.09, 0.85), (0.15, 0.99), (0.31, 0.93), (0.24, 0.78)], wall_coords=[(0.03, 1.21), (1.64, 1.21), (1.65, 0.03), (0.04, 0.03)])

# create_graph1(course)

analyse_course(path='Media/Video/robot.mp4', media='VIDEO')

# analyse_course(path='Media/Image/Bold2-165-84.5.jpg', media='IMAGE')

# connection_test()
