import math

import cv2 as cv
import numpy as np

cameraMatrix = np.array([[547.56017033, 0., 314.59740646], [
    0., 515.25051288, 221.47109663], [0., 0., 1.]])

distortion = np.array(
    [[0.11310858, -0.41396994, 0.00936895, 0.00729492, 0.33124321]])

# height in cm
robot_h = 20
camera_h = 175

# Coordinates for camera center, and a test point for the robot.
camera_point = [0, 0]
robot_test_point = [2, 2]


def calibrate_frame(frame):
    img = frame
    h, w = img.shape[:2]
    newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(
        cameraMatrix, distortion, (w, h), 1, (w, h))

    # Undistort
    dst = cv.undistort(img, cameraMatrix, distortion, None, newCameraMatrix)

    # # crop the image
    # x, y, w, h = roi
    # dst = dst[y:y+h, x:x+w]
    # cv.imwrite('caliResult1.png', dst)

    return dst


def triangulate_coordinates(coordinates):
    # triangulate the location with the help of basic trigonometry (look discord image recognition blackboard picture)
    # find angle of the point between the camera and the robot (tan(V)=mod/hos).
    # first remove robot height from the equation, so the camera and the found point is on the same level.
    temp_height = camera_h - robot_h
    # now find the length between the robot and the camera point.
    x_robot_cam = robot_test_point[0] - camera_point[0]
    y_robot_cam = robot_test_point[1] - camera_point[1]

    length_robot_cam = math.sqrt((x_robot_cam ** 2) * (y_robot_cam ** 2))

    # get the angle from the ground camera point to the robot point for later use (tan(V)=mod/hos).
    angle_robot_cam_ground = math.atan(y_robot_cam / x_robot_cam)

    # get the angle on near robot point (from camera top down to robot found point).
    angle_robot_cam = math.atan(temp_height / length_robot_cam)

    # then find the length between the actual point and the center of the bottom of the robot with (hos=mod/tan(V)).
    length_robot_cam_truth = camera_h / angle_robot_cam

    # now with the found knowledge find the true position of the robot.
    x_robot_truth = length_robot_cam_truth * math.acos(angle_robot_cam_ground)  # x = length * cos(angle)
    y_robot_truth = length_robot_cam_truth * math.asin(angle_robot_cam_ground)  # y = length * sin(angle)

    robot_coordinate_truth = [x_robot_truth, y_robot_truth]

    return robot_coordinate_truth
