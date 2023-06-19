import cv2 as cv
import numpy as np

# old camera matrix and distortion
# cameraMatrix = np.array([[547.56017033, 0., 314.59740646], [
#                         0., 515.25051288, 221.47109663], [0., 0., 1.]])
#
# distortion = np.array(
#     [[0.11310858, -0.41396994,  0.00936895,  0.00729492,  0.33124321]])

# new camera matrix and distortion
cameraMatrix = np.array([[537.88336182, 0., 319.16976047], [0., 506.01525879, 225.75126044], [0., 0., 1.]])
distortion = np.array([[0.11310855, -0.41396979, 0.00936896, 0.00729492, 0.33124294]])
mtx = np.array([[547.56015363, 0., 314.59741157], [0., 515.25049883, 221.47110369], [0., 0., 1.]])

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
