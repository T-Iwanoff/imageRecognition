import math

import cv2 as cv
import numpy as np
from constants import *




# Takes the walls of the course and the x and y coordinates of a point inside the course that you want to find
# the meter-coordinates for (distance to the lower left corner on the x- and y-axis)
def coordinate_conversion(walls, frame_x, frame_y):
    if len(walls) == 0:
        print("No walls detected")
        return
    if walls[1][0] - walls[0][0] == 0:  # If the walls are detected upside down, return nothing
        print(walls)
        print("Wall are upside down")
        return

    inside_walls_x = frame_x - (walls[0][0] + walls[3][0]) / 2
    x_scale = COURSE_WIDTH / (walls[1][0] - walls[0][0])
    #print("x scale: " , x_scale)
    meter_x = inside_walls_x * x_scale
    #meter_x = inside_walls_x

    #print("pixel in meter" , PIXEL_IN_METER)

    inside_walls_y = frame_y - (walls[0][1] + walls[1][1]) / 2
    y_scale = COURSE_HEIGHT / (walls[3][1] - walls[0][1])
    #print("y scale: " , y_scale)
    meter_y = (walls[2][1] - frame_y) * y_scale
    #meter_y = (walls[2][1] - frame_y)
    if PRINT_COORDINATES:
        print("x: ", meter_x)
        print("y: ", meter_y)
    return [meter_x, meter_y]

def determine_order_and_type(walls, obstacle, balls, orange_ball):
    ball_list = []

    # Convert balls from numpy array to list to prevent error
    balls = np.array(balls)
    balls = balls.tolist()

    # Convert orange ball from numpy array to list for formatting
    orange_ball = np.array(orange_ball)
    orange_ball = orange_ball.tolist()

    if len(walls) == 0:
        return
    if walls[1][0] - walls[0][0] == 0:  # If the walls are detected upside down, return nothing
        return

    for i in range(len(balls)):
        ball_type = check_type(balls[i], walls, obstacle)

        # Checking for corner ball
        if ball_type == "corner":
            ball_list.append([balls[i], "corner"])

        # Checking for middle ball
        if ball_type == "middle":
            ball_list.append([balls[i], "middle"])

        # Checking for edge ball
        if ball_type == "edge":
            ball_list.append([balls[i], "edge"])

        if ball_type == "none":
            ball_list.append([balls[i], "none"])

    # Determine type of orange ball and putting the orange ball in the end of the list
    if len(orange_ball) != 0:
        orange_ball_type = check_type(orange_ball, walls, obstacle)
        ball_list.append([orange_ball, orange_ball_type])

    print("ball list: ", ball_list)

    return ball_list

def check_type(ball, walls, obstacle):
    if obstacle is None or len(obstacle) == 0:
        return "none"
    ball_type = "none"

    # Checking for corner ball
    if (ball[0] < DETERMINATION_THRESHOLD and  # left lower corner
        ball[1] < DETERMINATION_THRESHOLD) or \
            (ball[0] < DETERMINATION_THRESHOLD and  # left upper corner
             ball[1] > walls[0][1] - DETERMINATION_THRESHOLD) or \
            (ball[0] > walls[2][0] - DETERMINATION_THRESHOLD and  # right lower corner
             ball[1] < DETERMINATION_THRESHOLD) or \
            (ball[0] > walls[1][0] - DETERMINATION_THRESHOLD and  # right upper corner
             ball[1] > walls[1][1] - DETERMINATION_THRESHOLD):
        ball_type = "corner"

    # Checking for middle ball
    elif (ball[0] > obstacle[0][0] and ball[0] < obstacle[2][0]) and \
            (ball[1] > obstacle[3][1] and ball[1] < obstacle[1][1]):
        ball_type = "middle"

    # Checking for edge ball
    elif (ball[0] < DETERMINATION_THRESHOLD) or \
            ball[0] > (walls[2][0] - DETERMINATION_THRESHOLD) or \
            (ball[1] < DETERMINATION_THRESHOLD) or \
            (ball[1] > (walls[0][1] - DETERMINATION_THRESHOLD)):
        ball_type = "edge"

    return ball_type

def improve_coordinate_precision(pixel_coordinates, obj, walls):
    camera_point_meter = [find_length_in_meter(320, walls), find_length_in_meter(240, walls)]
    pixel_coordinates_meter = [find_length_in_meter(pixel_coordinates[0], walls), find_length_in_meter(pixel_coordinates[1], walls)]
    print("camera point: ", camera_point_meter)
    print("pixel_coordinates_meter: ", pixel_coordinates_meter)
    hos_1 = math.dist(camera_point_meter, pixel_coordinates_meter)
    mod_1 = CAMERA_HEIGHT
    v = math.atan(mod_1 / hos_1)

    if obj == "ball":
        hos_2 = BALL_HEIGHT / math.tan(v)
    elif obj == "wall":
        hos_2 = WALL_HEIGHT / math.tan(v)
    elif obj == "robot":
        hos_2 = ROBOT_HEIGHT / math.tan(v)

    # Distance from camera point to object point
    d = hos_1 - hos_2

    ab_vector = np.array([[pixel_coordinates_meter[0] - camera_point_meter[0]], [pixel_coordinates_meter[1] - camera_point_meter[1]]])
    e_vector = (1 / magnitude(ab_vector)) * ab_vector

    improved_coordinates = np.array(e_vector) * d

    return improved_coordinates

def find_length_in_meter(pixel_length, walls):
    meter_length = pixel_length * scale_pixel_to_meter(walls)
    return meter_length

def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))

def scale_pixel_to_meter(walls): 

     x_scale = COURSE_WIDTH / (walls[1][0] - walls[0][0])

#     # y_scale = COURSE_HEIGHT / (walls[3][1] - walls[0][1])

     return x_scale

