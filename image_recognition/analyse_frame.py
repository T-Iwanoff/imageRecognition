from course import Course
from image_recognition.coordinates import *
from image_recognition.find_circles import *
from image_recognition.find_walls import *
from image_recognition.calibration import *
from constants import *
from config import *
import cv2 as cv
from image_recognition.robotRecognition import robot_recognition


def analyse_walls(frame):
    walls = None

    # Make a mask for the wall
    wall_mask = frame_to_wall_mask(frame)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(
        wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Find the correct max area of the outer wall
    wall_area = []
    for wall_contour in wall_contours:
        wall_area.append(cv.contourArea(wall_contour))
    max_wall_area = calibrate_wall_area(wall_area, False) + 100

    # Loop over the wall contours and find walls
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        if (max_wall_area if AUTOMATED_AREA_DETECT else OUTER_WALL_AREA_MAX) > wall_area > OUTER_WALL_AREA_MIN:
            # print(wall_area)  # for calibration
            # Find the corners of the walls
            walls = find_rectangle(wall_contour, True)
    return walls


def analyse_obstacles(frame, wall_contours=None):
    obstacle = None

    # Make a mask for the obstacle
    obstacle_mask = frame_to_wall_mask(frame)

    # Find contours in the red wall mask
    obstacle_contours, _ = cv.findContours(
        obstacle_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Find the correct max area of the obstacle
    obstacle_area = []
    for contour in obstacle_contours:
        obstacle_area.append(cv.contourArea(contour))
    max_obstacle_area = calibrate_wall_area(obstacle_area, True) + 100

    # Loop over the obstacle contours and find obstacle
    for contour in obstacle_contours:
        wall_area = cv.contourArea(contour)
        if (max_obstacle_area if AUTOMATED_AREA_DETECT else OUTER_WALL_AREA_MAX) > wall_area > OBSTACLE_AREA_MIN:
            # print(wall_area) # For calibration
            # Find the corners of the obstacle
            obstacle = find_rectangle(contour, False)
    return obstacle


def analyse_balls(frame, saved_balls, mask):
    # Find the balls
    balls = find_circles(frame, mask)

    # Adds the balls to the list of previous balls
    if balls is not None and saved_balls is not None and ENABLE_MULTI_FRAME_BALL_DETECTION:
        if len(saved_balls) < SAVED_FRAMES:
            saved_balls.append(balls)
            balls = find_repeated_coordinates(saved_balls, CUTOFF)
        else:
            substitute_in_list(saved_balls, balls)
            balls = find_repeated_coordinates(saved_balls, CUTOFF)

    return balls


def analyse_orange_ball(frame, saved_balls, mask):
    # Find the orange ball
    ball = find_orange_circle(frame, mask)

    # Adds the ball to the list of previous balls
    if ball is not None and saved_balls is not None and ENABLE_MULTI_FRAME_BALL_DETECTION:
        if len(saved_balls) < SAVED_FRAMES:
            saved_balls.append(ball)
            ball = find_repeated_coordinates(saved_balls, ORANGE_CUTOFF)
        else:
            substitute_in_list(saved_balls, ball)
            ball = find_repeated_coordinates(saved_balls, ORANGE_CUTOFF)

        if ball is not None and bool(ball):
            ball = ball[0]

    return ball


# Deletes the first element in a list, moves every other element one index back
def substitute_in_list(list, value):
    length = len(list)
    for i in range(length - 1):
        n = length - i - 1
        list[n] = list[n - 1]
    list[0] = value
    return list


def analyse_frame(frame, walls=None, saved_balls=None, saved_oranges=None, saved_angle=None):

    

    # Calibrate the frame
    frame = calibrate_frame(frame)

    # Find the wall corners
    if not STATIC_OUTER_WALLS or walls is None or not len(walls):
        walls = analyse_walls(frame)

    # Find the obstacle points
    obstacle = analyse_obstacles(frame)

    if walls is not None and len(walls):
        # find only robot in a certain area
        roi = np.zeros(frame.shape[:2], np.uint8)
        # wall shape
        roi = cv.fillPoly(roi, np.array([walls]), (255, 255, 255))
        # Target image; white background
        mask = np.ones_like(frame) * 255
        # Copy ROI part from original image to target image
        frame_mask = cv.bitwise_and(mask, frame, mask=roi) + cv.bitwise_and(mask, mask, mask=~roi)

        # cv.imshow("course mask", frame_mask)

    # Find the balls
    if walls is not None and len(walls):
        balls = analyse_balls(frame, saved_balls, frame_mask)

        # Find the orange ball
        orange_ball = analyse_orange_ball(frame, saved_oranges, frame_mask)

        # Remove orange ball from list of balls
        balls = remove_ball_from_list(orange_ball, balls)

        #TODO: make balls contain all balls
        # balls.append(orange_ball)
    else:
        balls = None
        orange_ball = None


    # Find the robot
    if walls is not None and len(walls):
        robot_position, robot_heading = robot_recognition(frame, walls, frame_mask, saved_angle)
    else:
        robot_position = None
        robot_heading = None

    return Course(ball_coords=balls,
                  orange_ball=orange_ball,
                  obstacle_coords=obstacle,
                  wall_coords=walls,
                  robot_coords=robot_position,
                  robot_heading=robot_heading
                  ), frame
