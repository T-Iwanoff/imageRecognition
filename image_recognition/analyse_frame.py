from image_recognition.coordinates import *
from image_recognition.find_circles import *
from image_recognition.find_walls import *
from image_recognition.calibration import *
from constants import *
import cv2 as cv


def analyse_frame(frame, saved_circles=None, counter=None, prev_number_of_balls=None):
    # Calibrate the frame
    frame = calibrate_frame(frame)

    # Make a mask for the wall
    wall_mask = frame_to_wall_mask(frame)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(
        wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # To prevent runtime error in meter conversion
    wall_corners = None

    # Loop over the wall contours and draw walls
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the outer wall, draw a rectangle
        if OUTER_WALL_AREA_MAX > wall_area > OUTER_WALL_AREA_MIN:
            # print(wall_area)  # for calibration
            # Draw an angled rectangle
            wall_corners = find_rectangle(wall_contour)
            cv.drawContours(frame, [wall_corners], 0, (0, 255, 255), 2)

            # Warp the frame to fit the outer wall
            # frame = warpFrame(box, frame)

    # print("---")  # For calibration
    # Find contours in the frame again (in case the warp above is used)
    # wall_mask = frameToWallMask(frame)
    # wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Loop over the wall contours and draw obstacle
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the cross obstacle, mark the corners
        if OBSTACLE_AREA_MAX > wall_area > OBSTACLE_AREA_MIN:
            # print(wall_area) # For calibration
            # Find the corners of the obstacle
            obstacle = find_rectangle(wall_contour)
            # cv.drawContours(frame, [obstacle], 0, (0, 255, 255), 2)
            # Draw the points of the obstacle
            for coord in obstacle:
                cv.circle(frame, (coord[0], coord[1]), 2, (0, 255, 255), 2)

    # Find the balls
    circles = find_circles(frame)
    # circles = find_white_circles(frame)
    # if counter is not None:
    #     if counter < SAVED_FRAMES:
    #         saved_circles.append(circles)
    #     else:
    #         saved_circles[counter % SAVED_FRAMES] = circles
    #     circles = find_repeated_coordinates(saved_circles, CUTOFF)

    # Draw the circles
    draw_circles(frame, circles)

    # Converting to meter
    if circles is not None and wall_corners is not None:
        for circle in circles:
            coordinate_conversion(wall_corners, circle[0], circle[1])

    if PRINT_NUMBER_OF_BALLS and circles is not None and prev_number_of_balls != len(circles):
        print(len(circles))
        prev_number_of_balls = len(circles)

    # Display the resulting frame
    cv.imshow('frame', frame)

    return prev_number_of_balls
