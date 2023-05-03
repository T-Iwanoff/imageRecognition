import cv2 as cv
import numpy
import numpy as np
import array

from constants import CIRCLE_MIN_DIST, CIRCLE_PARAM_1, CIRCLE_PARAM_2, CIRCLE_MIN_RADIUS, CIRCLE_MAX_RADIUS


def find_circles(frame):
    # Create a grayFrame
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
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


def find_white_circles(frame):
    # Create a grayFrame
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Find white ping pong balls
    # Threshold for white color
    white_mask = cv.inRange(frame, (200, 200, 200), (255, 255, 255))
    white_circles = cv.HoughCircles(white_mask, cv.HOUGH_GRADIENT, dp=1, minDist=CIRCLE_MIN_DIST,
                                    param1=CIRCLE_PARAM_1, param2=CIRCLE_PARAM_2, minRadius=CIRCLE_MIN_RADIUS,
                                    maxRadius=CIRCLE_MAX_RADIUS)

    # Convert white circles to array
    if white_circles is not None:
        white_circles = np.uint16(np.around(white_circles))
        white_circles = white_circles[0, :]

    # Find ping pong balls in the grayFrame
    circles = cv.HoughCircles(gray_frame, cv.HOUGH_GRADIENT, dp=1, minDist=CIRCLE_MIN_DIST,
                              param1=CIRCLE_PARAM_1, param2=CIRCLE_PARAM_2, minRadius=CIRCLE_MIN_RADIUS,
                              maxRadius=CIRCLE_MAX_RADIUS)

    # Convert circles to array
    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = circles[0, :]

    # Mask the circles with the white mask to get only white circles
    if white_circles is not None and circles is not None:
        white_circles_mask = np.zeros_like(white_mask)
        for circle in white_circles:
            cv.circle(white_circles_mask,
                      (circle[0], circle[1]), circle[2], 255, -1)
        circles_masked = cv.bitwise_and(
            circles, circles, mask=white_circles_mask)
        if np.sum(circles_masked) == 0:
            circles = None
        else:
            # Sort circles by radius (largest first)
            circles = circles_masked[circles_masked[:, 2].argsort()[::-1]]

    return circles


def find_repeated_coordinates(frames, cutoff):
    complete_list = []  # A list of all the balls
    repeated_list = []  # A list of the unique balls that occur at least 'cutoff' times
    for frame in frames:
        for coordinate in frame:
            complete_list.append(coordinate)  # Puts the found balls from all the provided frames in the same list
    for coordinate in complete_list:
        # count = sum(all(x == coordinate) for x in complete_list)  # Counts the number of times a ball is in the list
        count = sum((x[0] == coordinate[0] and x[1] == coordinate[1]) for x in complete_list)

        circle_dist = 5
        # listed = any(all(x == coordinate) for x in repeated_list)  # Checks whether a ball is on the repeat list
        listed = is_close(coordinate, repeated_list, circle_dist)

        if count >= cutoff and not listed:
            repeated_list.append(coordinate)
    print("list: ", repeated_list)
    return repeated_list


# Checks whether a coordinate is close to or equal to any coordinates in a list
def is_close(coord, coord_list, distance):
    close = False
    for x in coord_list:
        if abs(coord[0] - x[0]) <= distance:
            close = True
        if abs(coord[1] - x[1]) <= distance:
            close = True
    return close


def draw_circles(frame, circles):
    if circles is None:
        return

    for i in circles:
        # Center of the circle
        cv.circle(frame, (i[0], i[1]), 1, (0, 0, 0), 2)

        # Outer circle
        cv.circle(frame, (i[0], i[1]), i[2], (255, 0, 255), 2)
