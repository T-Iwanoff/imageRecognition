import cv2
import requests

# Read image file
image = cv2.imread('./images/1.png')

# Define color ranges for ping pong ball and red wall detection
lower_ball_color = (29, 86, 6)
upper_ball_color = (64, 255, 255)
lower_wall_color = (0, 0, 100)
upper_wall_color = (80, 80, 255)

# Convert the image to the HSV color space
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Apply color masks to the image to detect the ping pong ball and red wall
ball_mask = cv2.inRange(hsv, lower_ball_color, upper_ball_color)
wall_mask = cv2.inRange(hsv, lower_wall_color, upper_wall_color)

# Find contours in the ping pong ball mask
ball_contours, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Loop over the ping pong ball contours and draw a circle around each ball
for ball_contour in ball_contours:
    ball_area = cv2.contourArea(ball_contour)
    if ball_area > 100:
        x, y, w, h = cv2.boundingRect(ball_contour)
        cv2.circle(image, (int(x + w / 2), int(y + h / 2)), int((w + h) / 4), (0, 255, 0), 2)

        # Send ping pong ball coordinates to server via HTTP
        ball_coordinates = {'x': x, 'y': y}
        # r = requests.post('http://example.com/ball_coordinates', data=ball_coordinates)

# Find contours in the red wall mask
wall_contours, _ = cv2.findContours(wall_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Loop over the red wall contours and draw a rectangle around each wall
for wall_contour in wall_contours:
    wall_area = cv2.contourArea(wall_contour)
    if wall_area > 100:
        x, y, w, h = cv2.boundingRect(wall_contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Send red wall coordinates to server via HTTP
        wall_coordinates = {'x': x, 'y': y, 'w': w, 'h': h}
        # r = requests.post('http://example.com/wall_coordinates', data=wall_coordinates)

# Display the resulting image
cv2.imshow('image', image)
cv2.waitKey(0)

# Close the window
cv2.destroyAllWindows()