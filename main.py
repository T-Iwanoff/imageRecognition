import cv2 as cv
from coordinates import *
from calibration import *

# TODO Only map the border at the start, so the robot can't obscure it

path = 'Image/Cluster1.jpg'
media = 'CAMERA'    # 'CAMERA', 'VIDEO' or 'IMAGE'

# Define the frames sampled and minimum number of frames
# that a circle has to be present to in to count as a ball
SAVED_FRAMES = 10
CUTOFF = 4

# Define color ranges for red wall detection (inverted to cyan)
lower_wall_color = (80, 70, 50)
upper_wall_color = (100, 255, 255)


def analyseFrame(frame, savedCircles=None, counter=None):
    # Calibrate the frame
    frame = calibrateFrame(frame)

    # Make a mask for the wall
    wall_mask = frameToWallMask(frame)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # To prevent runtime error in meter conversion
    wall_corners = None

    # Loop over the wall contours and draw walls
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the outer wall, draw a rectangle
        if 195000 > wall_area > 10000:
            # print(wall_area) # for calibration
            # Draw an angled rectangle
            wall_corners = findRectangle(wall_contour)
            cv.drawContours(frame, [wall_corners], 0, (0, 255, 255), 2)

            # Warp the frame to fit the outer wall
            # frame = warpFrame(box, frame)

    # print("---") # For calibration
    # Find contours in the frame again (in case the warp above is used)
    # wall_mask = frameToWallMask(frame)
    # wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Loop over the wall contours and draw obstacle
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the cross obstacle, mark the corners
        if 1800 > wall_area > 900:
            # print(wall_area) # For calibration
            # Find the corners of the obstacle
            obstacle = findRectangle(wall_contour)
            cv.drawContours(frame, [obstacle], 0, (0, 255, 255), 2)
            # Draw the points of the obstacle
            for coord in obstacle:
                cv.circle(frame, (coord[0], coord[1]), 2, (0, 255, 255), 2)

    # Find the balls
    circles = findCircles(frame)
    # if counter is not None:
    #     if counter < SAVED_FRAMES:
    #         savedCircles.append(circles)
    #     else:
    #         savedCircles[counter % SAVED_FRAMES] = circles
    #     circles = findRepeatedCoordinates(savedCircles, CUTOFF)

    # Draw the circles
    drawCircles(frame, circles)

    # Converting to meter
    if circles is not None and wall_corners is not None:
        for circle in circles:
            coordinate_conversion(wall_corners, circle[0], circle[1])

    # Display the resulting frame
    cv.imshow('frame', frame)


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
    circles = cv.HoughCircles(grayFrame, cv.HOUGH_GRADIENT, 1, 3,  # param1 is sensitivity (smaller == more circles)
                              param1=80, param2=17, minRadius=3,
                              maxRadius=9)  # param2 is number of points in the circle (precision)

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
    repeated_list = []
    for coordinate in complete_list:
        count = complete_list.count(coordinate)
        if count >= cutoff and coordinate not in repeated_list:
            repeated_list.append(coordinate)
    return repeated_list


def drawCircles(frame, circles):
    if circles is None:
        return

    for i in circles:
        # Center of the circle
        cv.circle(frame, (i[0], i[1]), 1, (0, 0, 0), 2)

        # Outer circle
        cv.circle(frame, (i[0], i[1]), i[2], (255, 0, 255), 2)


if media == 'IMAGE':
    # Get the current frame
    frame = cv.imread(path)

    analyseFrame(frame)

    if cv.waitKey(0) == ord('q'):
        cv.destroyAllWindows()

#####

if media == 'VIDEO':
    videoCapture = cv.VideoCapture(path)
    if not videoCapture.isOpened():
        print("Error: Video not found")
        exit()

    frameCounter = 0
    savedData = []

    while True:
        # If out of frames, reset the video
        if frameCounter == videoCapture.get(7):  # propertyID 7 is the number of frames in the video
            frameCounter = 0
            videoCapture.set(1, 0)  # propertyID 1 is the current frame

        # Get the current frame
        ret, frame = videoCapture.read()
        if not ret:
            print("Error: Frame not found")
            exit()

        analyseFrame(frame, savedData, frameCounter)

        frameCounter += 1

        # If q is pressed, end the program
        if cv.waitKey(1) == ord('q'):
            break

    # Release the camera and close the window
    videoCapture.release()
    cv.destroyAllWindows()

######

if media == 'CAMERA':
    videoCapture = cv.VideoCapture(0, cv.CAP_DSHOW)
    videoCapture.set(3, 640)
    videoCapture.set(4, 480)

    if not videoCapture.isOpened():
        print("Error: Camera not found")
        exit()

    frameCounter = 0
    savedData = []

    while True:
        # Get the current frame
        ret, frame = videoCapture.read()
        if not ret:
            print("Error: Frame not found")
            exit()

        analyseFrame(frame, savedData, frameCounter)

        frameCounter += 1

        # If q is pressed, end the program
        if cv.waitKey(1) == ord('q'):
            break

    # Release the camera and close the window
    videoCapture.release()
    cv.destroyAllWindows()


