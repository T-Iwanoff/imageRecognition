import cv2
import requests

"""
    This program uses two color masks to detect both ping pong
    balls and red walls. It then finds contours in each mask and draws a
    circle around each ping pong ball and a rectangle around each red wall.
    If the area of the contour is greater than 100 pixels, it sends the objects
    coordinates to a server via HTTP POST request
"""

# Set up camera capture
cap = cv2.VideoCapture(0)

# Define color ranges for ping pong ball and red wall detection
lower_ball_color = (29, 86, 6)
upper_ball_color = (255, 255, 255)

lower_wall_color = (80, 70, 50)
upper_wall_color = (100, 255, 255)

# Loop over frames from the camera
while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        break
    invFrame = cv2.bitwise_not(frame)
    # Convert the frame to the HSV color space
    hsv = cv2.cvtColor(invFrame, cv2.COLOR_BGR2HSV)

    # Apply color masks to the frame to detect the ping pong ball and red wall
    ball_mask = cv2.inRange(hsv, lower_ball_color, upper_ball_color)
    wall_mask = cv2.inRange(hsv, lower_wall_color, upper_wall_color)

    # Find contours in the ping pong ball mask
    ball_contours, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over the ping pong ball contours and draw a circle around each ball
    for ball_contour in ball_contours:
        ball_area = cv2.contourArea(ball_contour)
        if ball_area > 100:
            x, y, w, h = cv2.boundingRect(ball_contour)
            cv2.circle(frame, (int(x + w / 2), int(y + h / 2)), int((w + h) / 4), (0, 255, 0), 2)

            # Send ping pong ball coordinates to server via HTTP
            ball_coordinates = {'x': x, 'y': y}
            r = requests.post('http://example.com/ball_coordinates', data=ball_coordinates)

    # Find contours in the red wall mask
    wall_contours, _ = cv2.findContours(wall_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over the red wall contours and draw a rectangle around each wall
    for wall_contour in wall_contours:
        wall_area = cv2.contourArea(wall_contour)
        if wall_area > 100:
            x, y, w, h = cv2.boundingRect(wall_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Send red wall coordinates to server via HTTP
            wall_coordinates = {'x': x, 'y': y, 'w': w, 'h': h}
            r = requests.post('http://example.com/wall_coordinates', data=wall_coordinates)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
