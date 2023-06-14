import math

import cv2 as cv
import numpy
import numpy as np
from constants import *
from config import *


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

    # Convert orange ball from numpy array to list for formatting
    # orange_ball = np.array(orange_ball)
    # orange_ball = orange_ball.tolist()
    # print(orange_ball)

    if len(walls) == 0:
        return
    if walls[1][0] - walls[0][0] == 0:  # If the walls are detected upside down, return nothing
        return

    for i in range(len(balls)):
        ball_type = check_type(balls[i], walls, obstacle)

        # Checking for corner ball
        if ball_type == "lower_left_corner":
            ball_list.append([balls[i], "lower_left_corner"])
        if ball_type == "upper_left_corner":
            ball_list.append([balls[i], "upper_left_corner"])
        if ball_type == "lower_right_corner":
            ball_list.append([balls[i], "lower_right_corner"])
        if ball_type == "upper_right_corner":
            ball_list.append([balls[i], "upper_right_corner"])

        # Checking for middle ball
        elif ball_type == "middle":
            ball_list.append([balls[i], "middle"])

        # Checking for edge balls
        elif ball_type == "left_edge":
            ball_list.append([balls[i], "left_edge"])
        elif ball_type == "right_edge":
            ball_list.append([balls[i], "right_edge"])
        elif ball_type == "lower_edge":
            ball_list.append([balls[i], "lower_edge"])
        elif ball_type == "upper_edge":
            ball_list.append([balls[i], "upper_edge"])

        elif ball_type == "none":
            ball_list.append([balls[i], "none"])

    # Determine type of orange ball and putting the orange ball in the end of the list
    if len(orange_ball) != 0:
        orange_ball_type = check_type(orange_ball[0], walls, obstacle)
        ball_list.append([orange_ball[0], orange_ball_type])

    return ball_list

def check_type(ball, walls, obstacle):
    if obstacle is None or len(obstacle) == 0:
        return "none"
    if ball is None or len(ball) == 0:
        return "none"
    ball_type = "none"

    if (ball[0] < DETERMINATION_THRESHOLD and # left lower corner
        ball[1] < DETERMINATION_THRESHOLD):
        ball_type = "lower_left_corner"
    elif (ball[0] < DETERMINATION_THRESHOLD and  # left upper corner
             ball[1] > walls[0][1] - DETERMINATION_THRESHOLD):
        ball_type = "upper_left_corner"
    elif (ball[0] > walls[2][0] - DETERMINATION_THRESHOLD and  # right lower corner
             ball[1] < DETERMINATION_THRESHOLD):
        ball_type = "lower_right_corner"
    elif (ball[0] > walls[1][0] - DETERMINATION_THRESHOLD and  # right upper corner
             ball[1] > walls[1][1] - DETERMINATION_THRESHOLD):
        ball_type = "upper_right_corner"

    # Checking for middle ball
    elif (ball[0] > obstacle[0][0] and ball[0] < obstacle[2][0]) and \
            (ball[1] > obstacle[3][1] and ball[1] < obstacle[1][1]):
        ball_type = "middle"

    # Checking for edge ball
    elif ball[0] < DETERMINATION_THRESHOLD:
        ball_type = "left_edge"
    elif ball[0] > (walls[2][0] - DETERMINATION_THRESHOLD):
        ball_type = "right_edge"
    elif ball[1] < DETERMINATION_THRESHOLD:
        ball_type = "lower_edge"
    elif ball[1] > (walls[0][1] - DETERMINATION_THRESHOLD):
        ball_type = "upper_edge"

    return ball_type

def improve_coordinate_precision(walls, pixel_coordinates, obj):
    # Temporary fix for 320 in x and 240 in y for obstacles pixel coordinates
    if pixel_coordinates[0] == 320:
        pixel_coordinates[0] = 319
    if pixel_coordinates[1] == 240:
        pixel_coordinates[1] = 239


    camera_point_meter = [find_length_in_meter(walls, 320, "x"), find_length_in_meter(walls, 240, "y")]

    # Calculate point relative to the walls
    pixel_coordinates_meter = [find_length_in_meter(walls, pixel_coordinates[0], "x"),
                               find_length_in_meter(walls, 480, "y") - find_length_in_meter(walls, pixel_coordinates[1], "y")]

    # triangulate the location with the help of basic trigonometry (look discord image recognition blackboard picture)
    # find angle of the point between the camera and the robot (tan(V)=mod/hos).
    # first remove robot height from the equation, so the camera and the found point is on the same level.
    temp_height = 0

    if obj == "ball":
        temp_height = CAMERA_HEIGHT - -BALL_HEIGHT
    elif obj == "wall":
        temp_height = CAMERA_HEIGHT - WALL_HEIGHT
    elif obj == "robot":
        temp_height = CAMERA_HEIGHT - ROBOT_HEIGHT

    # now find the length between the robot and the camera point.
    x_obj_cam = pixel_coordinates_meter[0] - camera_point_meter[0]
    y_obj_cam = pixel_coordinates_meter[1] - camera_point_meter[1]
    dist_obj_cam = math.dist(pixel_coordinates_meter, camera_point_meter) # hypotenuse

    # truth or false if x or y is negative.
    x_negative = False
    y_negative = False

    if x_obj_cam < 0:
        x_negative = True
        x_obj_cam = x_obj_cam * (-1)

    if y_obj_cam < 0:
        y_negative = True
        y_obj_cam = y_obj_cam * (-1)

    # length_obj_cam = math.sqrt((x_obj_cam ** 2) * (y_obj_cam ** 2))
    # length_obj_cam = math.dist([x_obj_cam], [y_obj_cam])

    # get the angle from the ground camera point to the robot point for later use (tan(V)=mod/hos).
    if x_obj_cam == 0:
        x_obj_cam = 0.01
        print("NOTE!")
    angle_obj_cam_ground = math.degrees(math.atan(y_obj_cam / x_obj_cam))
    angle_obj_cam_ground = round(angle_obj_cam_ground, 2)

    # get the angle on near robot point (from camera top down to robot found point).
    angle_obj_cam = math.degrees(math.atan(CAMERA_HEIGHT / dist_obj_cam))
    angle_obj_cam = round(angle_obj_cam, 2)

    # then find the length between the camera ground point and the center of the bottom truth
    # of the robot with (hos=mod/tan(V)).
    length_obj_cam_truth = temp_height / math.tan(math.radians(angle_obj_cam))

    # now with the found knowledge find the true position of the robot.
    x_robot_truth = length_obj_cam_truth * math.cos(math.radians(angle_obj_cam_ground))  # x = length * cos(angle)
    y_robot_truth = length_obj_cam_truth * math.sin(math.radians(angle_obj_cam_ground))  # y = length * sin(angle)

    if x_negative:
        x_robot_truth = x_robot_truth * (-1)

    if y_negative:
        y_robot_truth = y_robot_truth * (-1)

    # robot_truth = true position of the object
    # camera_point_meter = the center point on the ground for the camera
    # camera_constant = the camera angle distortion constant(varies depending on the angle of the camera for true point)
    orego = [find_length_in_meter(walls, walls[3][0], "x"),
            find_length_in_meter(walls, 480, "y") - find_length_in_meter(walls, walls[3][1], "y")]

    obj_coordinate_truth = [x_robot_truth + camera_point_meter[0] - orego[0], y_robot_truth + camera_point_meter[1] - orego[1]]

    return obj_coordinate_truth


def find_length_in_meter(walls, pixel_coordinate, axis):
    if len(walls) == 0:
        print("No walls detected")
        return
    if walls[1][0] - walls[0][0] == 0:  # If the walls are detected upside down, return nothing
        print("Wall are upside down")
        return
    if axis == "x":
        wall_width = math.dist(walls[1], walls[0])
        x_scale = COURSE_WIDTH / wall_width
        return pixel_coordinate * x_scale
    if axis == "y":
        wall_height = math.dist(walls[3], walls[0])
        y_scale = COURSE_HEIGHT / wall_height
        return pixel_coordinate * y_scale
    return

def magnitude(vector):
    return math.sqrt(sum(pow(element, 2) for element in vector))


def find_goal_coordinates():
    goal_coordinates = None
    if GOAL_SIDE_RELATIVE_TO_CAMERA == "left":
        goal_coordinates = [0.14,
                            (COURSE_HEIGHT / 2)]
        print("goal left: ", goal_coordinates)
    if GOAL_SIDE_RELATIVE_TO_CAMERA == "right":
        goal_coordinates = [COURSE_WIDTH - 0.14,
                            (COURSE_HEIGHT / 2)]
        print("goal right: ", goal_coordinates)

    return goal_coordinates


def remove_objects_outside_walls(walls, object):
    object_list = []
    object = np.array(object)
    if object.ndim > 1:
        for ball in object:
            if not (ball[0] < walls[0][0] or ball[0] > walls[1][0] or ball[1] < walls[0][1] or ball[1] > walls[3][1]):
                object_list.append(ball)
        return object_list
    else:
        if object[0] < walls[0][0] or object[0] > walls[1][0] or object[1] < walls[0][1] or object[1] > walls[3][1]:
            return None
    return object

# TODO sensitivity?
def remove_objects_outside_walls_from_list(walls, obj_list, type=None):
    new_list = np.array(obj_list)
    sensitivity = 0.0

    if new_list.ndim == 1:
        new_list = [obj_list]
    else:
        new_list = obj_list
    for obj in new_list:
        if not ((obj[0] > (walls[0][0] - sensitivity) and obj[0] > (walls[3][0] - sensitivity) and obj[0] < (walls[2][0] + sensitivity) and obj[0] < (walls[1][0] + sensitivity)) and
                (obj[1] > (walls[3][1] - sensitivity) and obj[1] < (walls[0][1] + sensitivity) and obj[1] < (walls[1][1] + sensitivity) and obj[1] > (walls[2][1]) - sensitivity)):
            new_list.remove(obj)

    if type == "robot":
        temp_array = np.array(new_list).flatten()
        new_list = temp_array.tolist()

    return new_list