import cv2 as cv
import numpy as np

cameraMatrix = np.array([[547.56017033, 0., 314.59740646], [0., 515.25051288, 221.47109663], [0., 0., 1.]])

distortion = np.array([[0.11310858, -0.41396994,  0.00936895,  0.00729492,  0.33124321]])


def calibrateFrame(frame):
    img = frame
    h, w = img.shape[:2]
    newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, distortion, (w,h), 1, (w,h))

    # Undistort
    dst = cv.undistort(img, cameraMatrix, distortion, None, newCameraMatrix)

    # # crop the image
    # x, y, w, h = roi
    # dst = dst[y:y+h, x:x+w]
    # cv.imwrite('caliResult1.png', dst)

    return dst
