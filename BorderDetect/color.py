import cv2 as cv
import numpy as np

videoCapture = cv.VideoCapture(0, cv.CAP_DSHOW)

while True:
    ret, frame = videoCapture.read()
    if not ret: break

    # invert colors
    invFrame = cv.bitwise_not(frame)

    # convert to hsv colorspace
    hsvFrame = cv.cvtColor(invFrame, cv.COLOR_BGR2HSV)

    # lower bound and upper bound for Cyan color
    lower_bound = np.array([80, 70, 50])
    upper_bound = np.array([100, 255, 255])

    # find the colors within the boundaries
    mask = cv.inRange(hsvFrame, lower_bound, upper_bound)

    # Showing the output
    cv.imshow("circles", mask)

    if cv.waitKey(1) & 0xFF == ord('q'): break

videoCapture.release()
cv.destroyAllWindows()
