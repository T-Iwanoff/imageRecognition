import cv2 as cv
import numpy
import numpy as np
import array
from config import *
from constants import CIRCLE_MIN_DIST, CIRCLE_PARAM_1, CIRCLE_PARAM_2, CIRCLE_MIN_RADIUS, CIRCLE_MAX_RADIUS


def find_circles(frame, mask):

    # Create a grayFrame
    gray_frame = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)

    # NEW CODE THAT DOESN'T WORK YET  HSV range for mask = (30, (120 - 130), (170 - 200)), (255,255,255)
    #white_mask = cv.inRange(frame, (30, 130, 175), (255, 255, 255))
    # blurred_frame = cv.GaussianBlur(white_mask, (7,7), 0)
    # cv.imshow('white',blurred_frame)
    # END OF NEW CODE

    # OLD CODE THAT WORKS OK
    # Find ping pong balls
    circles = cv.HoughCircles(gray_frame, cv.HOUGH_GRADIENT, dp=1, minDist=CIRCLE_MIN_DIST,
                              param1=CIRCLE_PARAM_1, param2=CIRCLE_PARAM_2, minRadius=CIRCLE_MIN_RADIUS,
                              maxRadius=CIRCLE_MAX_RADIUS)
    # param1 is sensitivity (smaller == more circles)
    # param2 is number of points in the circle (precision)

    # Convert circles to array
    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = circles[0, :]
    return circles



def find_orange_circle(frame, mask):

    hsv = cv.cvtColor(mask, cv.COLOR_BGR2HSV)

    # old
    #low_orange = np.array([10, 80, 245])
    #high_orange = np.array([45, 255, 255])

    # new
    low_orange = np.array([16, 109, 221])
    high_orange = np.array([45, 255, 255])

    mask = cv.inRange(hsv, low_orange, high_orange)
    blur_mask = cv.GaussianBlur(mask, (17, 17), 0)

    circles = cv.HoughCircles(blur_mask, cv.HOUGH_GRADIENT, dp=1, minDist=CIRCLE_MIN_DIST,
                              param1=100, param2=3, minRadius=CIRCLE_MIN_RADIUS,
                              maxRadius=CIRCLE_MAX_RADIUS)
    # For testing - show mask
    # cv.imshow('balls', blur_mask)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = circles[0, :]
        circles = circles[0, :]
    return circles


def remove_ball_from_list(ball, list_of_balls):
    if ball is None or not len(ball) or list_of_balls is None or not len(list_of_balls):
        return list_of_balls

    dist = SAVED_CIRCLE_DIST
    balls = []
    for i in list_of_balls:
        if not (abs(int(ball[0]) - int(i[0])) <= dist) or not (abs(int(ball[1]) - int(i[1])) <= dist):
            balls.append(i)
    # Make it an array
    # for i in range(len(balls)):
    #     balls[i] = numpy.array(balls[i])
    # balls = numpy.array(balls)
    return balls


def find_repeated_coordinates(frames, cutoff):
    complete_list = []  # A list of all the balls
    repeated_list = []  # A list of the unique balls that occur at least 'cutoff' times
    for frame in frames:
        if type(frame[0]) is numpy.uint16:
            frame = [frame[:]]
        for coordinate in frame:
            complete_list.append(coordinate)  # Puts the found balls from all the provided frames in the same list
    if complete_list:
        for coordinate in complete_list:
            # Counts the number of times a ball is in the list (checks coordinates, but not size of ball)
            count = sum((x[0] == coordinate[0] and x[1] == coordinate[1]) for x in complete_list)

            # Checks whether a ball is on the repeat list and adds it
            listed = is_close(coordinate, repeated_list, SAVED_CIRCLE_DIST)
            if count >= cutoff and not listed:
                repeated_list.append(coordinate)
    return repeated_list


# Checks whether a coordinate is close to or equal to any coordinates in a list
def is_close(coord, coord_list, distance):
    for x in coord_list:
        if (abs(int(coord[0]) - int(x[0])) <= distance) and (abs(int(coord[1]) - int(x[1])) <= distance):
            return True
    return False

