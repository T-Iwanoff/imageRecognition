import cv2 as cv
import numpy as np
from constants import *

def coordinate_conversion(box, frame_x, frame_y):
    # print(box)
    if len(box) == 0:
        return
    if box[1][0]-box[0][0] == 0:  # If the box is detected upside down, return nothing
        return

    inside_walls_x = frame_x - (box[0][0] + box[3][0])/2
    x_scale = COURSE_WIDTH/(box[1][0]-box[0][0])
    meter_x = inside_walls_x * x_scale

    inside_walls_y = frame_y - (box[0][1] + box[1][1])/2
    y_scale = COURSE_HEIGHT/(box[3][1]-box[0][1])
    meter_y = (box[2][1]-frame_y) * y_scale
    if (PRINT_COORDINATES):
        print("x: ", meter_x)
        print("y: ", meter_y)
    return [meter_x, meter_y]


# box = [[50, 400], [50, 30], [600, 30], [600, 400]]  # Straight box
# box = [[47, 408], [55, 14], [592, 25], [584, 419]]  # Angled box
# halfPoint_x = (box[3][0]-box[0][0])/2
# halfPoint_y = (box[0][1]+box[1][1])/2
# coordinate_convertion(box, halfPoint_x, halfPoint_y)