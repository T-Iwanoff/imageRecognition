import cv2 as cv
import numpy as np
from ultralytics import YOLO

videoCapture = cv.VideoCapture(1, cv.CAP_DSHOW)

while True:
    ret, frame = videoCapture.read()
    if not ret: break

    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #blurFrame = cv.GaussianBlur(grayFrame, (17,17), 0)
    #blurFrame = cv.blur(grayFrame, (5,5))

    clrFrame = cv.cvtColor(grayFrame, cv.COLOR_GRAY2BGR)

    circles = cv.HoughCircles(grayFrame, cv.HOUGH_GRADIENT, 1, 2,
                              param1=80, param2=17, minRadius=1, maxRadius=8) #Param1 = sensitivity (smaller == more circles), param2 = number of points in the circle (precision)

    showFrame = frame

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            #Center of the circle
            cv.circle(showFrame, (i[0], i[1]), 1, (0, 0, 0), 2)

            #Outer circle
            cv.circle(showFrame, (i[0], i[1]), i[2], (255,0,255), 2)

    cv.imshow("circles", showFrame)

    if cv.waitKey(1) & 0xFF == ord('q'): break

videoCapture.release()
cv.destroyAllWindows()