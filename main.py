import cv2 as cv
import numpy as np

videoPath = 'Video/Balls.mp4'
video = True

if video:
    videoCapture = cv.VideoCapture(videoPath)
else:
    videoCapture = cv.VideoCapture(0, cv.CAP_DSHOW)

if not videoCapture.isOpened():
    print("Video file or camera not found")

frameCounter = 0

while True:
    if video:
        # If out of frames, reset the video
        if frameCounter == videoCapture.get(7):  # propertyID 7 is the number of frames in the video
            frameCounter = 0
            videoCapture.set(1, 0)  # propertyID 1 is the current frame
        frameCounter += 1

    # Get the current frame
    ret, frame = videoCapture.read()

    if not ret:
        break

    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    invFrame = cv.bitwise_not(frame)
    hsvFrame = cv.cvtColor(invFrame, cv.COLOR_BGR2HSV)

    # lower bound and upper bound for Cyan color
    lower_bound = np.array([80, 70, 50])
    upper_bound = np.array([100, 255, 255])

    # find the colors within the boundaries
    mask = cv.inRange(hsvFrame, lower_bound, upper_bound)

    showFrame = frame

    # find circles
    circles = cv.HoughCircles(grayFrame, cv.HOUGH_GRADIENT, 1, 1,
                              param1=70, param2=17, minRadius=1, maxRadius=8)  # Param1 = sensitivity (smaller == more circles), param2 = number of points in the circle (precision)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # Center of the circle
            cv.circle(showFrame, (i[0], i[1]), 1, (0, 0, 0), 2)

            # Outer circle
            cv.circle(showFrame, (i[0], i[1]), i[2], (255, 0, 255), 2)

    cv.imshow("Detection", mask)
    cv.imshow("Frame", showFrame)

    # Press Q on keyboard to exit
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

videoCapture.release()
cv.destroyAllWindows()
