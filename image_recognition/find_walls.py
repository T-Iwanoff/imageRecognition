import copy

import cv2 as cv
import numpy as np

from constants import LOWER_WALL_COLOR, UPPER_WALL_COLOR


def calibrate_wall_area(wall_area, find_obstacle):
    wall_area = sorted(wall_area, reverse=True)
    if find_obstacle and len(wall_area) > 2:
        max_area = wall_area[2]
    elif len(wall_area) > 1:
        max_area = wall_area[1]
    else:
        max_area = 100000
    return max_area


def frame_to_wall_mask(frame):
    # Convert the frame to the HSV color space
    inv_frame = cv.bitwise_not(frame)
    hsv_frame = cv.cvtColor(inv_frame, cv.COLOR_BGR2HSV)
    # Apply color mask to the frame to detect the red walls
    wall_mask = cv.inRange(hsv_frame, LOWER_WALL_COLOR, UPPER_WALL_COLOR)
    return wall_mask


def find_rectangle(wall, sort):
    rect = cv.minAreaRect(wall)
    box = cv.boxPoints(rect)
    box = np.intp(box)
    if sort:
        box = sort_walls(box)
    return box


def warp_frame(box, frame):
    if len(box) == 0:
        print("No walls detected")
        return
    if box[1][0] - box[0][0] == 0:  # If the walls are detected upside down, return nothing
        # print(box)
        print("Wall are upside down")
        return

    global converted_points
    # Warp image, code from https://thinkinfi.com/warp-perspective-opencv/
    # Pixel values in original image
    lower_left_point = box[3]  # Black
    upper_left_point = box[0]  # Red
    upper_right_point = box[1]  # Green
    lower_right_point = box[2]  # Blue
    # Create point matrix
    point_matrix = np.float32(
        [upper_left_point, upper_right_point, lower_left_point, lower_right_point])
    # Draw circle for each point
    # cv.circle(
    #     frame, (upper_left_point[0], upper_left_point[1]), 10, (0, 0, 255), cv.FILLED)
    # cv.circle(
    #     frame, (upper_right_point[0], upper_right_point[1]), 10, (0, 255, 0), cv.FILLED)
    # cv.circle(
    #     frame, (lower_right_point[0], lower_right_point[1]), 10, (255, 0, 0), cv.FILLED)
    # cv.circle(
    #     frame, (lower_left_point[0], lower_left_point[1]), 10, (0, 0, 0), cv.FILLED)
    # Output image size
    width, height = 640, 480
    # Desired points value in output images
    converted_ul_pixel_value = [0, 0]
    converted_ur_pixel_value = [width, 0]
    converted_ll_pixel_value = [0, height]
    converted_lr_pixel_value = [width, height]
    # Convert points
    converted_points = np.float32([converted_ul_pixel_value, converted_ur_pixel_value,
                                   converted_ll_pixel_value, converted_lr_pixel_value])
    # perspective transform
    perspective_transform = cv.getPerspectiveTransform(
        point_matrix, converted_points)
    frame = cv.warpPerspective(frame, perspective_transform, (width, height))
    return frame


# Sorts the points of the wall so its always upper-left, upper-right, lower-right, lower-left
def sort_walls(walls):
    sorted_walls = copy.deepcopy(walls)
    for point in walls:
        if (point[0] < 200) and (point[1] < 200):
            sorted_walls[0] = point  # Upper left
        if (point[0] > 200) and (point[1] < 200):
            sorted_walls[1] = point  # Upper right
        if (point[0] > 200) and (point[1] > 200):
            sorted_walls[2] = point  # Lower right
        if (point[0] < 200) and (point[1] > 200):
            sorted_walls[3] = point  # Lower left

    # print("Sorted walls:" + sorted_walls)
    return sorted_walls
