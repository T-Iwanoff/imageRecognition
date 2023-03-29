import cv2 as cv
from Coordinates import *
from collections import Counter

videoPath = 'Video/Balls3.mp4'
useCamera = True

if useCamera:
    videoCapture = cv.VideoCapture(0, cv.CAP_DSHOW)
    videoCapture.set(3, 640)
    videoCapture.set(4, 480)
else:
    videoCapture = cv.VideoCapture(videoPath)

# TODO Sample multiple images for the circles, only mark circles that appear in multiple
# TODO Only map the border at the start, so the car can't obscure it
# TODO Turn rectangles into coordinates


if not videoCapture.isOpened():
    print("File or camera not found")

if useCamera is False:
    frameCounter = 0
    fileType = videoPath[-3]


# Define color ranges for red wall detection
lower_wall_color = (80, 70, 50)
upper_wall_color = (100, 255, 255)


def frameToWallMask(frame):
    # Convert the frame to the HSV color space
    invFrame = cv.bitwise_not(frame)
    hsvFrame = cv.cvtColor(invFrame, cv.COLOR_BGR2HSV)
    # Apply color mask to the frame to detect the red walls
    wall_mask = cv.inRange(hsvFrame, lower_wall_color, upper_wall_color)
    return wall_mask


def findRectangle(wall):
    rect = cv.minAreaRect(wall)
    box = cv.boxPoints(rect)
    box = np.intp(box)
    return box


def warpFrame(box, frame):
    global converted_points
    # Warp image, code from https://thinkinfi.com/warp-perspective-opencv/
    # Pixel values in original image
    lower_left_point = box[0]  # Black
    upper_left_point = box[1]  # Red
    upper_right_point = box[2]  # Green
    lower_right_point = box[3]  # Blue
    # Create point matrix
    point_matrix = np.float32([upper_left_point, upper_right_point, lower_left_point, lower_right_point])
    # Draw circle for each point
    cv.circle(frame, (upper_left_point[0], upper_left_point[1]), 10, (0, 0, 255), cv.FILLED)
    cv.circle(frame, (upper_right_point[0], upper_right_point[1]), 10, (0, 255, 0), cv.FILLED)
    cv.circle(frame, (lower_right_point[0], lower_right_point[1]), 10, (255, 0, 0), cv.FILLED)
    cv.circle(frame, (lower_left_point[0], lower_left_point[1]), 10, (0, 0, 0), cv.FILLED)
    # Output image size
    width, height = 640, 480
    # Desired points value in output images
    converted_ul_pixel_value = [0, 0]
    converted_ur_pixel_value = [width, 0]
    converted_ll_pixel_value = [0, height]
    converted_lr_pixel_value = [width, height]
    # Convert points
    converted_points = np.float32([converted_ul_pixel_value, converted_ur_pixel_value,
                                   converted_ll_pixel_value, converted_lr_pixel_value])
    # perspective transform
    perspective_transform = cv.getPerspectiveTransform(point_matrix, converted_points)
    frame = cv.warpPerspective(frame, perspective_transform, (width, height))
    return frame


def findCircles(frame):
    # Create a grayFrame
    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Find ping pong balls
    circles = cv.HoughCircles(grayFrame, cv.HOUGH_GRADIENT, 1, 3,        # param1 is sensitivity (smaller == more circles)
                        param1=80, param2=17, minRadius=3, maxRadius=9)  # param2 is number of points in the circle (precision)

    # Convert circles to array
    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = circles[0, :]
    return circles


def findRepeatedCoordinates(frames, cutoff):
    complete_list = []
    for frame in frames:
        for coordinate in frame:
            complete_list.append(coordinate)
    print("complete list "+ complete_list.)
    repeated_list = []
    counter_list = Counter(complete_list)
    print("counter list "+ counter_list.str)
    for coordinate in counter_list:
        count = complete_list.count(coordinate)
        if count >= cutoff and coordinate not in repeated_list:
            repeated_list.append(coordinate)
    return repeated_list


def drawCircles(frame, circles):
    for i in circles:
        # Center of the circle
        cv.circle(frame, (i[0], i[1]), 1, (0, 0, 0), 2)

        # Outer circle
        cv.circle(frame, (i[0], i[1]), i[2], (255, 0, 255), 2)


savedData = []
counter = 0

# Loop over frames from the camera
while True:
    if useCamera is False and fileType == 'mp4':
        # If out of frames, reset the video
        if frameCounter == videoCapture.get(7):  # propertyID 7 is the number of frames in the video
            frameCounter = 0
            videoCapture.set(1, 0)  # propertyID 1 is the current frame
        frameCounter += 1

    if useCamera is False and fileType == 'jpg' or 'png':
        frame = cv.imread(videoPath)

    # Get the current frame
    ret, frame = videoCapture.read()

    if not ret:
        print("Frame not found")
        break

    # Make a mask for the wall
    wall_mask = frameToWallMask(frame)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Loop over the wall contours and draw as appropriate
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the outer wall, draw a rectangle
        if 210000 > wall_area > 10000:
            # Draw an angled rectangle
            box = findRectangle(wall_contour)
            cv.drawContours(frame, [box], 0, (0, 255, 255), 2)

            # Warp the frame to fit the outer wall
            frame = warpFrame(box, frame)

    # Find contours in the warped frame
    wall_mask = frameToWallMask(frame)
    wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Loop over the wall contours and draw as appropriate
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)

        # For the cross obstacle, mark the corners
        if 1800 > wall_area > 1600:
            # Find the corners of the obstacle
            box = findRectangle(wall_contour)
            cv.drawContours(frame, [box], 0, (0, 255, 255), 2)

            # Draw the points of the obstacle
            for coord in box:
                cv.circle(frame, (coord[0], coord[1]), 2, (0, 255, 255), 2)

    # Find the balls
    circles = findCircles(frame)
    if counter < 5:
        savedData.append(circles)
    else:
        savedData[counter % 5] = circles
    counter = counter + 1
    circles = findRepeatedCoordinates(savedData, 3)

    # Draw the circles
    drawCircles(frame, circles)

    # Converting to meter
    # if circles is not None and converted_points is not None:
    #     for circle in circles:
    #         coordinate_conversion(converted_points, circle[0], circle[1])

    # Display the resulting frame
    cv.imshow('frame', frame)

    # If q is pressed, end the program
    if cv.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
videoCapture.release()
cv.destroyAllWindows()
