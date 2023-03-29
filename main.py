import cv2 as cv
import numpy as np
from Coordinates import *

videoPath = 'Video/Balls3.mp4'
video = True

if video:
    videoCapture = cv.VideoCapture(videoPath)
    videoCapture.set(cv.CAP_PROP_FPS,1)
    videoCapture.set(3, 640)
    videoCapture.set(4, 480)

else:
    videoCapture = cv.VideoCapture(0, cv.CAP_DSHOW)

# TODO Sample multiple images for the circles, only mark circles that appear in multiple
# TODO Only map the border at the start, so the car can't obscure it
# TODO Turn rectangles into coordinates


if not videoCapture.isOpened():
    print("Video file or camera not found")

frameCounter = 0

# Define color ranges for red wall detection
lower_wall_color = (80, 70, 50)
upper_wall_color = (100, 255, 255)

# Loop over frames from the camera
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

    # Create a grayFrame
    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Convert the frame to the HSV color space
    blurFrame = cv.GaussianBlur(frame, (11, 11), 0)
    invFrame = cv.bitwise_not(frame)
    hsvFrame = cv.cvtColor(invFrame, cv.COLOR_BGR2HSV)
    # Apply color mask to the frame to detect the red walls
    wall_mask = cv.inRange(hsvFrame, lower_wall_color, upper_wall_color)

    # Find ping pong balls
    circles = cv.HoughCircles(grayFrame, cv.HOUGH_GRADIENT, 1, 3,
                            param1=80, param2=17, minRadius=3, maxRadius=9)
    # param1 is sensitivity (smaller == more circles)
    # param2 is number of points in the circle (precision)

    # Draw the circles
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            #Center of the circle
            cv.circle(frame, (i[0], i[1]), 1, (0, 0, 0), 2)

            #Outer circle
            cv.circle(frame, (i[0], i[1]), i[2], (255,0,255), 2)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Loop over the red wall contours and draw as appropriate
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the outer wall, draw a rectangle
        if 210000 > wall_area > 10000:
            # Old code: Straight rectangles
            # x, y, w, h = cv2.boundingRect(wall_contour)
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Draw an angled rectangle
            rect = cv.minAreaRect(wall_contour)
            box = cv.boxPoints(rect)
            box = np.intp(box)
            cv.drawContours(frame, [box], 0, (0, 255, 255), 2)

            # Warp image, code from https://thinkinfi.com/warp-perspective-opencv/
            # Pixel values in original image
            xy1 = [box[1][0], box[1][1]]
            xy2 = [box[2][0], box[2][1]]
            xy0 = [box[0][0], box[0][1]]
            xy3 = [box[3][0], box[3][1]]

            # Create point matrix
            point_matrix = np.float32([xy1, xy2, xy0, xy3])

            # Draw circle for each point
            cv.circle(frame, (xy1[0], xy1[1]), 10, (0, 0, 255), cv.FILLED)
            cv.circle(frame, (xy2[0], xy2[1]), 10, (0, 255, 0), cv.FILLED)
            cv.circle(frame, (xy3[0], xy3[1]), 10, (255, 0, 0), cv.FILLED)
            cv.circle(frame, (xy0[0], xy0[1]), 10, (0, 0, 0), cv.FILLED)

            # Output image size
            width, height = 640, 480

            # Desired points value in output images
            converted_red_pixel_value = [100, 100]
            converted_green_pixel_value = [width-100, 100]
            converted_black_pixel_value = [100, height-100]
            converted_blue_pixel_value = [width-100, height-100]

            # Convert points
            converted_points = np.float32([converted_red_pixel_value, converted_green_pixel_value,
                                           converted_black_pixel_value, converted_blue_pixel_value])

            # perspective transform
            perspective_transform = cv.getPerspectiveTransform(point_matrix, converted_points)
            frame = cv.warpPerspective(frame, perspective_transform, (width, height))



            # Converting to meter
            # halfPoint_x = (box[3][0] - box[0][0]) / 2
            # halfPoint_y = (box[0][1] + box[1][1]) / 2
            # coordinate_convertion(box, halfPoint_x, halfPoint_y)

        # For the cross obstacle, mark the corners
        if 1300 > wall_area > 1000:
            rect = cv.minAreaRect(wall_contour)
            box = cv.boxPoints(rect)
            box = np.intp(box)
            for coord in box:
                cv.circle(frame, (coord[0], coord[1]), 2, (0, 255, 255), 2)

            # Old code: Draw a rectangle around the cross
            # cv2.drawContours(frame, [box], 0, (0, 255, 255), 2)

            # Send red wall coordinates to server via HTTP
            # wall_coordinates = {'x': x, 'y': y, 'w': w, 'h': h}
            # r = requests.post('http://example.com/wall_coordinates', data=wall_coordinates)

    # Display the resulting frame
    cv.imshow('frame', frame)

    # If
    if cv.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
videoCapture.release()
cv.destroyAllWindows()
