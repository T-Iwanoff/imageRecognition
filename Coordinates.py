import cv2 as cv
import numpy as np

def coordinate_convertion (box, frame_x, frame_y):
    x_scale = (box[2][0]-box[0][0])/1.8
    meter_x = frame_x/x_scale
    y_scale = (box[0][1]-box[2][1])/1.2
    meter_y = (box[0][1]-frame_y)/y_scale
    print("meter x: "+str(meter_x))
    print("meter y: " + str(meter_y))
    return meter_x, meter_y


# box = [[50, 400], [50, 30], [600, 30], [600, 400]]  # Straight box
box = [[47, 408], [55, 14], [592, 25], [584, 419]]  # Angled box
halfPoint_x = (box[3][0]-box[0][0])/2
halfPoint_y = (box[0][1]+box[1][1])/2
coordinate_convertion(box, halfPoint_x, halfPoint_y)