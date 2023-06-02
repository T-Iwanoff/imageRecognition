from course import Course
from image_recognition.coordinates import *
from image_recognition.find_circles import *
from image_recognition.find_walls import *
from image_recognition.calibration import *
from constants import *
import cv2 as cv

def analyse_walls(frame, wall_contours=None):
    # Find the correct max area of the outer wall
    global wall_corners
    wall_corners_detected = False

    if STATIC_OUTER_WALLS:
        # Calibrate the frame
        frame = calibrate_frame(frame)

        # Make a mask for the wall
        wall_mask = frame_to_wall_mask(frame)

        # Find contours in the red wall mask
        wall_contours, _ = cv.findContours(
            wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Make a list of wall contours
    wall_area = []
    for wall_contour in wall_contours:
        wall_area.append(cv.contourArea(wall_contour))

    max_wall_area = calibrate_wall_area(wall_area, False) + 100

    # Loop over the wall contours and draw walls
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the outer wall, draw a rectangle
        if (max_wall_area if AUTOMATED_AREA_DETECT else OUTER_WALL_AREA_MAX) > wall_area > OUTER_WALL_AREA_MIN:
            # print(wall_area)  # for calibration
            wall_corners = find_rectangle(wall_contour, True)
            wall_corners_detected = True
    if not wall_corners_detected:
        return
    else:
        return wall_corners


def analyse_obstacles(frame, wall_contours=None):
    obstacle_detected = False
    # Find the correct max area of the obstacle
    obstacle_area = []
    for wall_contour in wall_contours:
        obstacle_area.append(cv.contourArea(wall_contour))
    max_obstacle_area = calibrate_wall_area(obstacle_area, True) + 100

    # Loop over the wall contours and draw obstacle
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the cross obstacle, mark the corners
        if (max_obstacle_area if AUTOMATED_AREA_DETECT else OUTER_WALL_AREA_MAX) > wall_area > OBSTACLE_AREA_MIN:
            # print(wall_area) # For calibration
            # Find the corners of the obstacle
            obstacle = find_rectangle(wall_contour, False)
            obstacle_detected = True
    if not obstacle_detected:
        return
    else:
        return obstacle

def analyse_balls(frame, wall_corners, saved_circles=None, counter=None, prev_number_of_balls=None):
    # Find the balls
    circles = find_circles(frame)

    if counter is not None and circles is not None:
        if counter < SAVED_FRAMES:
            saved_circles.append(circles)
            circles = find_repeated_coordinates(saved_circles, CUTOFF)
        else:
            saved_circles[counter % SAVED_FRAMES] = circles
            circles = find_repeated_coordinates(saved_circles, CUTOFF)

    return circles

def analyse_frame(frame, static_wall_corners=None):

    # Calibrate the frame
    frame = calibrate_frame(frame)

    # Make a mask for the wall
    wall_mask = frame_to_wall_mask(frame)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(
        wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Find the outer wall corners
    if STATIC_OUTER_WALLS:
        wall_corners = static_wall_corners
    else:
        wall_corners = analyse_walls(frame, wall_contours)

    # Find the obstacle points
    obstacle = analyse_obstacles(frame, wall_contours)

    # Warp the frame to fit the outer wall
    # frame = warpFrame(box, frame)

    # print("---")  # For calibration
    # Find contours in the frame again (in case the warp above is used)
    # wall_mask = frameToWallMask(frame)
    # wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    circles = analyse_balls(frame, wall_corners)
    orange_circle = find_orange_circle(frame)
    circles = remove_circle_from_list(orange_circle, circles)

    # Converting to meter
    circles_in_meters = []
    orange_circle_in_meters = []
    obstacle_in_meters = []
    walls_in_meters = []

    if wall_corners is not None:
        if circles is not None:
            for circle in circles:
                converted_coords = coordinate_conversion(
                    wall_corners, circle[0], circle[1])
                circles_in_meters.append(converted_coords)

        if orange_circle is not None:
            orange_circle_in_meters = coordinate_conversion(
                wall_corners, orange_circle[0], orange_circle[1])

        if obstacle is not None:
            for coord in obstacle:
                converted_coords = coordinate_conversion(
                    wall_corners, coord[0], coord[1])
                obstacle_in_meters.append(converted_coords)

        if wall_corners is not None:
            for coord in wall_corners:
                converted_coords = coordinate_conversion(
                    wall_corners, coord[0], coord[1])
                walls_in_meters.append(converted_coords)

    # Round objects to 3 decimals
    circles_in_meters = round_coordinates(circles_in_meters, ROUNDING_AMOUNT)
    orange_circle_in_meters = round_coordinates(orange_circle_in_meters, ROUNDING_AMOUNT)
    walls_in_meters = round_coordinates(walls_in_meters, ROUNDING_AMOUNT)
    obstacle_in_meters = round_coordinates(walls_in_meters, ROUNDING_AMOUNT)

    # Determine order and type of the balls
    ball_list = determine_order_and_type(walls_in_meters,obstacle_in_meters,circles_in_meters,orange_circle_in_meters)

    # Draw on the frame
    if wall_corners is not None:
        cv.drawContours(frame, [wall_corners], 0, (255, 0, 0), 2)
    if obstacle is not None:
        for coord in obstacle:
            cv.circle(frame, (coord[0], coord[1]), 2, (0, 255, 255), 2)
    if circles is not None:
        for i in circles:
            cv.circle(frame, (i[0], i[1]), 1, (0, 0, 0), 2)  # Center of the circle
            cv.circle(frame, (i[0], i[1]), i[2], (255, 0, 255), 2)  # Outer circle
    if orange_circle is not None:
        cv.circle(frame, (orange_circle[0], orange_circle[1]), 1, (0, 0, 0), 2)  # Center of the circle
        cv.circle(frame, (orange_circle[0], orange_circle[1]), orange_circle[2], (100, 100, 255), 2)  # Outer circle

    # Display the frame
    cv.imshow('frame', frame)

    return Course(ball_list, obstacle_in_meters, walls_in_meters)

