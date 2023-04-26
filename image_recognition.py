import cv2 as cv
from coordinates import *
from refactoring.calibration import *
from constants import *


def analyse_frame(frame, savedCircles=None, counter=None, prev_number_of_balls=None):
    # Calibrate the frame
    frame = calibrate_frame(frame)

    # Make a mask for the wall
    wall_mask = frame_to_wall_mask(frame)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(
        wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # To prevent runtime error in meter conversion
    wall_corners = None

    # Loop over the wall contours and draw walls
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the outer wall, draw a rectangle
        if OUTER_WALL_AREA_MAX > wall_area > OUTER_WALL_AREA_MIN:
            # print(wall_area)  # for calibration
            # Draw an angled rectangle
            wall_corners = find_rectangle(wall_contour)
            cv.drawContours(frame, [wall_corners], 0, (0, 255, 255), 2)

            # Warp the frame to fit the outer wall
            # frame = warpFrame(box, frame)

    # print("---")  # For calibration
    # Find contours in the frame again (in case the warp above is used)
    # wall_mask = frameToWallMask(frame)
    # wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Loop over the wall contours and draw obstacle
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        # For the cross obstacle, mark the corners
        if OBSTACLE_AREA_MAX > wall_area > OBSTACLE_AREA_MIN:
            # print(wall_area) # For calibration
            # Find the corners of the obstacle
            obstacle = find_rectangle(wall_contour)
            # cv.drawContours(frame, [obstacle], 0, (0, 255, 255), 2)
            # Draw the points of the obstacle
            for coord in obstacle:
                cv.circle(frame, (coord[0], coord[1]), 2, (0, 255, 255), 2)

    # Find the balls
    circles = find_circles(frame)
    # circles = findWhiteCircles(frame)
    # if counter is not None:
    #     if counter < SAVED_FRAMES:
    #         savedCircles.append(circles)
    #     else:
    #         savedCircles[counter % SAVED_FRAMES] = circles
    #     circles = findRepeatedCoordinates(savedCircles, CUTOFF)

    # Draw the circles
    draw_circles(frame, circles)

    # Converting to meter
    if circles is not None and wall_corners is not None:
        for circle in circles:
            coordinate_conversion(wall_corners, circle[0], circle[1])

    if (PRINT_NUMBER_OF_BALLS and circles is not None and prev_number_of_balls != len(circles)):
        print(len(circles))
        prev_number_of_balls = len(circles)

    # Display the resulting frame
    cv.imshow('frame', frame)

    return prev_number_of_balls


def frame_to_wall_mask(frame):
    # Convert the frame to the HSV color space
    inv_frame = cv.bitwise_not(frame)
    hsv_frame = cv.cvtColor(inv_frame, cv.COLOR_BGR2HSV)
    # Apply color mask to the frame to detect the red walls
    wall_mask = cv.inRange(hsv_frame, LOWER_WALL_COLOR, UPPER_WALL_COLOR)
    return wall_mask


def find_rectangle(wall):
    rect = cv.minAreaRect(wall)
    box = cv.boxPoints(rect)
    box = np.intp(box)
    return box


def warp_frame(box, frame):
    global converted_points
    # Warp image, code from https://thinkinfi.com/warp-perspective-opencv/
    # Pixel values in original image
    lower_left_point = box[0]  # Black
    upper_left_point = box[1]  # Red
    upper_right_point = box[2]  # Green
    lower_right_point = box[3]  # Blue
    # Create point matrix
    point_matrix = np.float32(
        [upper_left_point, upper_right_point, lower_left_point, lower_right_point])
    # Draw circle for each point
    cv.circle(
        frame, (upper_left_point[0], upper_left_point[1]), 10, (0, 0, 255), cv.FILLED)
    cv.circle(
        frame, (upper_right_point[0], upper_right_point[1]), 10, (0, 255, 0), cv.FILLED)
    cv.circle(
        frame, (lower_right_point[0], lower_right_point[1]), 10, (255, 0, 0), cv.FILLED)
    cv.circle(
        frame, (lower_left_point[0], lower_left_point[1]), 10, (0, 0, 0), cv.FILLED)
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
    perspective_transform = cv.getPerspectiveTransform(
        point_matrix, converted_points)
    frame = cv.warpPerspective(frame, perspective_transform, (width, height))
    return frame


def find_circles(frame):
    # Create a grayFrame
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Find ping pong balls
    circles = cv.HoughCircles(gray_frame, cv.HOUGH_GRADIENT, dp=1, minDist=CIRCLE_MIN_DIST,
                              param1=CIRCLE_PARAM_1, param2=CIRCLE_PARAM_2, minRadius=CIRCLE_MIN_RADIUS,
                              maxRadius=CIRCLE_MAX_RADIUS)

    # Convert circles to array
    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = circles[0, :]
    return circles


def find_white_circles(frame):
    # Create a grayFrame
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Find white ping pong balls
    # Threshold for white color
    white_mask = cv.inRange(frame, (200, 200, 200), (255, 255, 255))
    white_circles = cv.HoughCircles(white_mask, cv.HOUGH_GRADIENT, dp=1, minDist=CIRCLE_MIN_DIST,
                                    param1=CIRCLE_PARAM_1, param2=CIRCLE_PARAM_2, minRadius=CIRCLE_MIN_RADIUS,
                                    maxRadius=CIRCLE_MAX_RADIUS)

    # Convert white circles to array
    if white_circles is not None:
        white_circles = np.uint16(np.around(white_circles))
        white_circles = white_circles[0, :]

    # Find ping pong balls in the grayFrame
    circles = cv.HoughCircles(gray_frame, cv.HOUGH_GRADIENT, dp=1, minDist=CIRCLE_MIN_DIST,
                              param1=CIRCLE_PARAM_1, param2=CIRCLE_PARAM_2, minRadius=CIRCLE_MIN_RADIUS,
                              maxRadius=CIRCLE_MAX_RADIUS)

    # Convert circles to array
    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles = circles[0, :]

    # Mask the circles with the white mask to get only white circles
    if white_circles is not None and circles is not None:
        white_circles_mask = np.zeros_like(white_mask)
        for circle in white_circles:
            cv.circle(white_circles_mask,
                      (circle[0], circle[1]), circle[2], 255, -1)
        circles_masked = cv.bitwise_and(
            circles, circles, mask=white_circles_mask)
        if np.sum(circles_masked) == 0:
            circles = None
        else:
            # Sort circles by radius (largest first)
            circles = circles_masked[circles_masked[:, 2].argsort()[::-1]]

    return circles


def find_repeated_coordinates(frames, cutoff):
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


def draw_circles(frame, circles):
    if circles is None:
        return

    for i in circles:
        # Center of the circle
        cv.circle(frame, (i[0], i[1]), 1, (0, 0, 0), 2)

        # Outer circle
        cv.circle(frame, (i[0], i[1]), i[2], (255, 0, 255), 2)
