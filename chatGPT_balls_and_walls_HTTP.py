import cv2
import numpy as np

"""
    This program uses two color masks to detect both ping pong
    balls and red walls. It then finds contours in each mask and draws a
    circle around each ping pong ball and a rectangle around each red wall.
    If the area of the contour is greater than 100 pixels, it sends the objects
    coordinates to a server via HTTP POST request
"""

# Set up camera capture
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Define color ranges for red wall detection
lower_wall_color = (80, 70, 50)
upper_wall_color = (100, 255, 255)

# Loop over frames from the camera
while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        break

    # Create a grayFrame
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Convert the frame to the HSV color space
    blurFrame = cv2.GaussianBlur(frame, (11, 11), 0)
    invFrame = cv2.bitwise_not(frame)
    hsvFrame = cv2.cvtColor(invFrame, cv2.COLOR_BGR2HSV)
    # Apply color mask to the frame to detect the red walls
    wall_mask = cv2.inRange(hsvFrame, lower_wall_color, upper_wall_color)

    # Find ping pong balls
    circles = cv2.HoughCircles(grayFrame, cv2.HOUGH_GRADIENT, 1, 3,
                            param1=80, param2=17, minRadius=3, maxRadius=9)

    # Draw the circles
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            #Center of the circle
            cv2.circle(frame, (i[0], i[1]), 1, (0, 0, 0), 2)

            #Outer circle
            cv2.circle(frame, (i[0], i[1]), i[2], (255,0,255), 2)

    # Find contours in the red wall mask
    wall_contours, _ = cv2.findContours(wall_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over the red wall contours and draw a rectangle around each wall
    for wall_contour in wall_contours:
        wall_area = cv2.contourArea(wall_contour)
        if 210000 > wall_area > 1000:
            print(wall_area)
            x, y, w, h = cv2.boundingRect(wall_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Send red wall coordinates to server via HTTP
            # wall_coordinates = {'x': x, 'y': y, 'w': w, 'h': h}
            # r = requests.post('http://example.com/wall_coordinates', data=wall_coordinates)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
