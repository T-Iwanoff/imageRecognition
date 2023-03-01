import cv2 as cv
import numpy as np

videoCapture = cv.VideoCapture(1, cv.CAP_DSHOW)

while True:
    ret, frame = videoCapture.read()
    if not ret: break

    cv.imshow("frame", frame)
    if cv.waitKey(1) & 0xFF == ord('q'): break

videoCapture.release()
cv.destroyAllWindows()