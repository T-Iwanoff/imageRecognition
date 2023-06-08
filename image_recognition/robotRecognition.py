import math

import cv2
import numpy as np
from image_recognition.coordinates import coordinate_conversion, improve_coordinate_precision
from image_recognition.calibration import calibrate_frame
from image_recognition.coordinates import coordinate_conversion


def robot_recognition(frame, wall_corners):

    # Calibrate the frame
    # frame = calibrate_frame(frame)

    # define kernel size
    kernel = np.ones((7, 7), np.uint8)

    # convert to hsv colorspace
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower bound and upper bound for pointer color (light green)
    lower_bound_pointer = np.array([50, 50, 20]) # lego color
    upper_bound_pointer = np.array([80, 100, 255]) # lego color

    # lower bound and upper bound for center color (dark blue)
    # lower_bound_center = np.array([110,60,50])
    # upper_bound_center = np.array([140,255,255])

    # lower bound and upper bound for center color (dark blue)
    lower_bound_center = np.array([80,43,50])
    upper_bound_center = np.array([105,250,255])

    # find the colors within the boundaries from center
    mask_center = cv2.inRange(hsv, lower_bound_center, upper_bound_center)

    # Remove unnecessary noise from mask center
    mask_center = cv2.morphologyEx(mask_center, cv2.MORPH_CLOSE, kernel)
    mask_center = cv2.morphologyEx(mask_center, cv2.MORPH_OPEN, kernel)

    # Segment only the detected region from center
    segmented_img_center = cv2.bitwise_and(frame, frame, mask=mask_center)

    # Find contours from the mask from center
    contours_center, hierarchy = cv2.findContours(mask_center.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # output = cv2.drawContours(segmented_img_pointer, contours_pointers, -1, (0, 0, 255), 3)
    output = cv2.drawContours(segmented_img_center, contours_center, -1, (0, 0, 255), 3)

    # instantiate the coordinates for later usage
    cY_center = 0
    cX_center = 0
    cY_pointer = 0
    cX_pointer = 0

    for c in contours_center:
        # compute the center of the contour
        M = cv2.moments(c)
        cX_center = int(M["m10"] / M["m00"])
        cY_center = int(M["m01"] / M["m00"])
        # draw the contour and center of the shape on the image
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (cX_center, cY_center), 2, (255, 255, 255), -1)

        # check the coordinates found
        # print("center: x = " + str(cX_center) + " and " "y = " + str(cY_center))

    # draw a circle around the center of the robot
    cv2.circle(img=frame, center=(cX_center, cY_center), radius=45, color=(255, 0, 0), thickness=2)

    # find only pointers in a certain area
    # Circular ROI in original image; must be selected via an additional mask
    # link: https://stackoverflow.com/questions/59873870/crop-a-circle-area-roi-of-an-image-and-put-it-onto-a-white-mask
    roi = np.zeros(frame.shape[:2], np.uint8)
    roi = cv2.circle(roi, (cX_center, cY_center), 45, 255, cv2.FILLED)

    # Target image; white background
    mask = np.ones_like(frame) * 255
    # Copy ROI part from original image to target image
    mask = cv2.bitwise_and(mask, frame, mask=roi) + cv2.bitwise_and(mask, mask, mask=~roi)

    # pointer finding setup for region of interest ROI (won't find pointer outside of ROI)
    # convert to hsv colorspace
    hsvP = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
    # find the colors within the boundaries
    mask_pointer = cv2.inRange(hsvP, lower_bound_pointer, upper_bound_pointer)
    # Remove unnecessary noise from mask
    mask_pointer = cv2.morphologyEx(mask_pointer, cv2.MORPH_CLOSE, kernel)
    mask_pointer = cv2.morphologyEx(mask_pointer, cv2.MORPH_OPEN, kernel)

    # Segment only the detected region
    segmented_img_pointer = cv2.bitwise_and(frame, frame, mask=mask_pointer)
    # Find contours from the mask
    contours_pointers, hierarchy = cv2.findContours(mask_pointer.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    output = cv2.drawContours(segmented_img_pointer, contours_pointers, -1, (0, 0, 255), 3)

    # loop over the contours
    for c in contours_pointers:
        # compute the center of the contour
        M = cv2.moments(c)
        cX_pointer = int(M["m10"] / M["m00"])
        cY_pointer = int(M["m01"] / M["m00"])
        # draw the contour and center of the shape on the image
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (cX_pointer, cY_pointer), 2, (255, 255, 255), -1)

        # check the coordinates found
        # print("pointer: x = " + str(cX_pointer) + " and " "y = " + str(cY_pointer))

    # calculate angle
    def calculate_angle(x0, y0, x, y):
        # x0,y0 = the center of the robot : x,y = is the coordinate of the oriantation point
        angle = math.degrees(math.atan2(y0 - y, x - x0)) % 360
        # print(f'The angle is = {angle}')
        return angle

    # show mask for the center and pointer
    # cv2.imshow("center mask", mask_center)
    # cv2.imshow("pointer mask", mask_pointer)

    robot_coords = [cX_center, cY_center]
    print("robot xy: ", robot_coords)
    # Showing the output
    robot_pos = improve_coordinate_precision(wall_corners, robot_coords, "robot")
    print("Robot coords: ", robot_pos)
    robot_angle = calculate_angle(cX_center, cY_center, cX_pointer, cY_pointer)
    print("Robot angle: ", robot_angle)

    #cv2.imshow('robot-recognition', frame)

    return robot_pos, robot_angle, frame
