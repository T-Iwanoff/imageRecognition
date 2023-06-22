import cv2
import cvzone
from cvzone import ColorFinder

# Code from group 4
cap = cv2.VideoCapture(0)

cf = ColorFinder(True)

hsvVals = "red"

while True:

    success, img = cap.read()

    imgColor, mask = cf.update(img, hsvVals)

    cv2.imshow("Image", imgColor)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
