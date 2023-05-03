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
            # Draw an angled rectangle
            wall_corners = find_rectangle(wall_contour)
            wall_corners_detected = True
            cv.drawContours(frame, [wall_corners], 0, (0, 255, 255), 2)
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
            obstacle = find_rectangle(wall_contour)
            obstacle_detected = True
            # cv.drawContours(frame, [obstacle], 0, (0, 255, 255), 2)
            # Draw the points of the obstacle
            for coord in obstacle:
                cv.circle(frame, (coord[0], coord[1]), 2, (255, 255, 0), 2)
    if not obstacle_detected:
        return
    else:
        return obstacle

def analyse_balls(frame, wall_corners, saved_circles=None, counter=None, prev_number_of_balls=None):
    # Find the balls
    # circles = find_circles(frame)
    circles = find_orange_circle(frame)
    # if counter is not None:
    #     if counter < SAVED_FRAMES:
    #         saved_circles.append(circles)
    #     else:
    #         saved_circles[counter % SAVED_FRAMES] = circles
    #     circles = find_repeated_coordinates(saved_circles, CUTOFF)

    # Draw the circles
    draw_circles(frame, circles)

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
        if wall_corners is not None:
            cv.drawContours(frame, [wall_corners], 0, (255, 0, 0), 2)
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

    circles_in_meters = []
    obstacle_in_meters = []
    walls_in_meters = []

    if wall_corners is not None:
        # Converting to meter
        if circles is not None:
            for circle in circles:
                converted_coords = coordinate_conversion(
                    wall_corners, circle[0], circle[1])
                circles_in_meters.append(converted_coords)

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

    cv.imshow('frame', frame)

    return Course(circles_in_meters, obstacle_in_meters, walls_in_meters)

