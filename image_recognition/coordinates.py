import cv2 as cv
import numpy as np
from constants import *


# Takes the walls of the course and the x and y coordinates of a point inside the course that you want to find
# the meter-coordinates for (distance to the lower left corner on the x- and y-axis)
def coordinate_conversion(walls, frame_x, frame_y):
    if len(walls) == 0:
        return
    if walls[1][0] - walls[0][0] == 0:  # If the walls are detected upside down, return nothing
        return

    inside_walls_x = frame_x - (walls[0][0] + walls[3][0]) / 2
    x_scale = COURSE_WIDTH / (walls[1][0] - walls[0][0])
    meter_x = inside_walls_x * x_scale

    inside_walls_y = frame_y - (walls[0][1] + walls[1][1]) / 2
    y_scale = COURSE_HEIGHT / (walls[3][1] - walls[0][1])
    meter_y = (walls[2][1] - frame_y) * y_scale
    if PRINT_COORDINATES:
        print("x: ", meter_x)
        print("y: ", meter_y)
    return [meter_x, meter_y]

def determine_order_and_type(walls, obstacle, balls, orange_ball):
    ball_list = []

    # Convert balls from numpy array to list to prevent error
    balls = np.array(balls)
    balls = balls.tolist()

    if len(walls) == 0:
        return
    if walls[1][0] - walls[0][0] == 0:  # If the walls are detected upside down, return nothing
        return

    for i in range(len(balls)):
        # Checking for corner ball
        if (balls[i][0] < DETERMINATION_THRESHOLD and # left lower corner
                balls[i][1] < DETERMINATION_THRESHOLD) or \
            (balls[i][0] < DETERMINATION_THRESHOLD and # left upper corner
                balls[i][1] > walls[0][1] - DETERMINATION_THRESHOLD) or \
            (balls[i][0] > walls[2][0] - DETERMINATION_THRESHOLD and # right lower corner
                balls[i][1] < DETERMINATION_THRESHOLD) or \
            (balls[i][0] > walls[1][0] - DETERMINATION_THRESHOLD and # right upper corner
                balls[i][1] > walls[1][1] - DETERMINATION_THRESHOLD):
            ball_list.append([balls[i], "corner"])

        # Checking for middle ball
        if (balls[i][0] > obstacle[0][0] and balls[i][0] < obstacle[2][0]) and \
            (balls[i][1] > obstacle[3][1] and balls[i][1] < obstacle[1][1]):
            ball_list.append([balls[i], "middle"])

        # Checking for edge ball
        if balls[i][0] < DETERMINATION_THRESHOLD or \
            balls[i][0] > walls[2][1] - DETERMINATION_THRESHOLD or \
            balls[i][1] < DETERMINATION_THRESHOLD or \
            balls[i][1] > walls[0][1] - DETERMINATION_THRESHOLD:
            # Checking that the ball is not on the list, since corner balls also meet the conditions
            for i in range(len(balls)):
                in_list = False
                for ball in ball_list:
                    if balls[i] == ball:
                        in_list = True
                        break
                if not in_list:
                    ball_list.append([balls[i], "edge"])

    # Determine type of orange ball and putting the orange ball in the end of the list

    return ball_list

def round_coordinates(object, amount):
    object = [[round(element, amount) for element in sublist] for sublist in object]
    return object