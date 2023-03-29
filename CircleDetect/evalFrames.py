import cv2 as cv
import numpy as np


def findRepeatedCoordinates(frames, cutoff):
    complete_list = []
    for frame in frames:
        for coordinate in frame:
            complete_list.add(coordinate)
    repeated_list = set()
    for coordinate in complete_list:
        count = complete_list.count(coordinate)
        if count >= cutoff and coordinate not in repeated_list:
            repeated_list.add(coordinate)
    return repeated_list
