# TechVidvan Object detection of similar color

import cv2
import numpy as np
import math

# Reading the image

# 0-grader er til venstre og bevæger med uret rundt, hvor vandret er både 360 og 0 grader til venstre
img = cv2.imread('test-image-0grader.jpg')

# define kernel size
kernel = np.ones((7, 7), np.uint8)

# convert to hsv colorspace
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# lower bound and upper bound for Green color original
lower_bound_pointer = np.array([50, 20, 20])
upper_bound_pointer = np.array([70, 255, 255])

# lower bound and upper bound for Green color
lower_bound_center = np.array([80, 20, 20])
upper_bound_center = np.array([100, 255, 255])

# find the colors within the boundaries
mask_pointer = cv2.inRange(hsv, lower_bound_pointer, upper_bound_pointer)
mask_center = cv2.inRange(hsv, lower_bound_center, upper_bound_center)

# Remove unnecessary noise from mask
mask_pointer = cv2.morphologyEx(mask_pointer, cv2.MORPH_CLOSE, kernel)
mask_pointer = cv2.morphologyEx(mask_pointer, cv2.MORPH_OPEN, kernel)

mask_center = cv2.morphologyEx(mask_center, cv2.MORPH_CLOSE, kernel)
mask_center = cv2.morphologyEx(mask_center, cv2.MORPH_OPEN, kernel)

# Segment only the detected region
segmented_img_pointer = cv2.bitwise_and(img, img, mask=mask_pointer)
segmented_img_center = cv2.bitwise_and(img, img, mask=mask_center)

# Find contours from the mask
contours_pointers, hierarchy = cv2.findContours(mask_pointer.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours_center, hierarchy = cv2.findContours(mask_center.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

output = cv2.drawContours(segmented_img_pointer, contours_pointers, -1, (0, 0, 255), 3)
output = cv2.drawContours(segmented_img_center, contours_center, -1, (0, 0, 255), 3)

# loop over the contours
for c in contours_pointers:
    # compute the center of the contour
    M = cv2.moments(c)
    cX_pointer = int(M["m10"] / M["m00"])
    cY_pointer = int(M["m01"] / M["m00"])
    # draw the contour and center of the shape on the image
    cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
    cv2.circle(img, (cX_pointer, cY_pointer), 7, (255, 255, 255), -1)

    # check the coordinates found
    print("pointer: x = " + str(cX_pointer) + " and " "y = " + str(cY_pointer))

for c in contours_center:
    # compute the center of the contour
    M = cv2.moments(c)
    cX_center = int(M["m10"] / M["m00"])
    cY_center = int(M["m01"] / M["m00"])
    # draw the contour and center of the shape on the image
    cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
    cv2.circle(img, (cX_center, cY_center), 7, (255, 255, 255), -1)

    # check the coordinates found
    print("center: x = " + str(cX_center) + " and " "y = " + str(cY_center))


# calculate angle
def calculate_angle(x0, y0, x, y):
    # x0,y0 = the center of the robot : x,y = is the coordinate of the oriantation point
    angle = math.degrees(math.atan2(y0 - y, x0 - x)) % 360
    print(f'The angle is = {angle}')

# draw a circle around the center of the robot
cv2.circle(img=img, center=(cX_center, cY_center), radius=200, color=(255, 0, 0), thickness=5)

# Showing the output
calculate_angle(cX_center, cY_center, cX_pointer, cY_pointer)
cv2.imshow("Output", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
