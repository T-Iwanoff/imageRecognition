from course import Course
from image_recognition.coordinates import *
from image_recognition.find_circles import *
from image_recognition.find_walls import *
from image_recognition.calibration import *
from constants import *
from config import *
import cv2 as cv
from image_recognition.robotRecognition import robot_recognition


def analyse_walls(frame):
    walls = None

    # Make a mask for the wall
    wall_mask = frame_to_wall_mask(frame)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(
        wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Find the correct max area of the outer wall
    wall_area = []
    for wall_contour in wall_contours:
        wall_area.append(cv.contourArea(wall_contour))
    max_wall_area = calibrate_wall_area(wall_area, False) + 100

    # Loop over the wall contours and find walls
    for wall_contour in wall_contours:
        wall_area = cv.contourArea(wall_contour)
        if (max_wall_area if AUTOMATED_AREA_DETECT else OUTER_WALL_AREA_MAX) > wall_area > OUTER_WALL_AREA_MIN:
            # print(wall_area)  # for calibration
            # Find the corners of the walls
            walls = find_rectangle(wall_contour, True)
    return walls


def analyse_obstacles(frame, wall_contours=None):
    obstacle = None

    # Make a mask for the obstacle
    obstacle_mask = frame_to_wall_mask(frame)

    # Find contours in the red wall mask
    obstacle_contours, _ = cv.findContours(
        obstacle_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Find the correct max area of the obstacle
    obstacle_area = []
    for contour in obstacle_contours:
        obstacle_area.append(cv.contourArea(contour))
    max_obstacle_area = calibrate_wall_area(obstacle_area, True) + 100

    # Loop over the obstacle contours and find obstacle
    for contour in obstacle_contours:
        wall_area = cv.contourArea(contour)
        if (max_obstacle_area if AUTOMATED_AREA_DETECT else OUTER_WALL_AREA_MAX) > wall_area > OBSTACLE_AREA_MIN:
            # print(wall_area) # For calibration
            # Find the corners of the obstacle
            obstacle = find_rectangle(contour, False)
    return obstacle


def analyse_balls(frame, saved_balls):
    # Find the balls
    balls = find_circles(frame)

    # Adds the balls to the list of previous balls
    if balls is not None and saved_balls is not None and ENABLE_MULTI_FRAME_BALL_DETECTION:
        if len(saved_balls) < SAVED_FRAMES:
            saved_balls.append(balls)
            balls = find_repeated_coordinates(saved_balls, CUTOFF)
        else:
            substitute_in_list(saved_balls, balls)
            balls = find_repeated_coordinates(saved_balls, CUTOFF)

    return balls


def analyse_orange_ball(frame, saved_balls):
    # Find the orange ball
    ball = find_orange_circle(frame)

    # Adds the ball to the list of previous balls
    if ball is not None and saved_balls is not None and ENABLE_MULTI_FRAME_BALL_DETECTION:
        if len(saved_balls) < SAVED_FRAMES:
            saved_balls.append(ball)
            ball = find_repeated_coordinates(saved_balls, ORANGE_CUTOFF)
        else:
            substitute_in_list(saved_balls, ball)
            ball = find_repeated_coordinates(saved_balls, ORANGE_CUTOFF)

        if ball is not None and bool(ball):
            ball = ball[0]

    return ball


# Deletes the first element in a list, moves every other element one index back
def substitute_in_list(list, value):
    length = len(list)
    for i in range(length-1):
        list[i] = list[i+1]
    list[length-1] = value
    return list


def analyse_frame2(frame, static_wall_corners=None, saved_circles=None, saved_orange=None, counter=None):

    # Calibrate the frame
    frame = calibrate_frame(frame)

    # Make a mask for the wall
    wall_mask = frame_to_wall_mask(frame)

    # Find contours in the red wall mask
    wall_contours, _ = cv.findContours(
        wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # Find the outer wall corners
    if STATIC_OUTER_WALLS:
        wall_corners = static_wall_corners
    else:
        wall_corners = analyse_walls(frame, wall_contours)

    # Find the obstacle points
    obstacle = analyse_obstacles(frame, wall_contours)

    # Warp the frame to fit the outer wall
    # frame = warp_frame(wall_corners, frame)

    # print("---")  # For calibration
    # Find contours in the frame again (in case the warp above is used)
    # wall_mask = frameToWallMask(frame)
    # wall_contours, _ = cv.findContours(wall_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    circles = analyse_balls(frame, saved_circles, counter)
    # for showing the coords on frame
    # old_circles = circles

    orange_circle = analyse_orange_ball(frame, saved_orange, counter)
    circles = remove_circle_from_list(orange_circle, circles)

    # Converting to meter
    circles_in_meters = []
    orange_circle_in_meters = []
    obstacle_in_meters = []
    walls_in_meters = []
    ball_list = []

    if wall_corners is not None:
        if circles is not None and len(circles):
            for circle in circles:
                improved_coords = improve_coordinate_precision(wall_corners, circle, "ball")
                circles_in_meters.append(improved_coords)
                text = "(" + str(round(improved_coords[0], 2)) + ", " + str(round(improved_coords[1], 2)) + ")"
                # Draw coords on frame
                cv.putText(frame, text, (circle[0]-40, circle[1]-20), cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        if orange_circle is not None and len(orange_circle):
            improved_coords = improve_coordinate_precision(wall_corners, orange_circle, "ball")
            orange_circle_in_meters.append(improved_coords)
            text = "(" + str(round(improved_coords[0], 2)) + ", " + str(round(improved_coords[1], 2)) + ")"
            # Draw coords on frame
            cv.putText(frame, text, (orange_circle[0] - 40, orange_circle[1] - 20), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        if obstacle is not None and len(obstacle):
            for coord in obstacle:
                improved_coords = improve_coordinate_precision(wall_corners, coord, "ball")
                obstacle_in_meters.append(improved_coords)

        if wall_corners is not None and len(wall_corners):
            for coord in wall_corners:
                improved_coords = improve_coordinate_precision(wall_corners, coord, "ball")
                walls_in_meters.append(improved_coords)

    # Determine order and type of the balls
    # if len(obstacle_in_meters) != 0:
    #     # contains an array with a coordinate array and a string in each element
    #     ball_list = determine_order_and_type(walls_in_meters, obstacle_in_meters, circles_in_meters, orange_circle_in_meters)

    # Draw on the frame
    if wall_corners is not None:
        cv.drawContours(frame, [wall_corners], 0, (255, 0, 0), 2)
    if obstacle is not None:
        for coord in obstacle:
            cv.circle(frame, (coord[0], coord[1]), 2, (0, 255, 255), 2)
    if circles is not None:
        for i in circles:
            # Center of the circle
            cv.circle(frame, (i[0], i[1]), 1, (0, 0, 0), 2)
            cv.circle(frame, (i[0], i[1]), i[2],
                      (255, 0, 255), 2)  # Outer circle
    if orange_circle is not None and len(orange_circle):
        # Center of the circle
        cv.circle(frame, (orange_circle[0], orange_circle[1]), 1, (0, 0, 0), 2)
        cv.circle(frame, (orange_circle[0], orange_circle[1]),
                  orange_circle[2], (100, 100, 255), 2)  # Outer circle

    # Not working delete?
    # showing coords on top of balls on frame
    # if circles is not None:
    #     for i in old_circles:
    #         cv.putText(frame, str((circle[0], circle[1])), (i[0], i[1]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Display the frame
    # cv.imshow('frame', frame)

    ball_list = determine_order_and_type(
        walls_in_meters, obstacle_in_meters, circles_in_meters, orange_circle_in_meters)
    ball_coords_in_order = []
    ball_types_in_order = []
    if ball_list is not None:
        for i in ball_list:
            ball_coords_in_order.append(i[0])
            ball_types_in_order.append(i[1])

    return Course(ball_coords = ball_coords_in_order,
                  obstacle_coords = obstacle_in_meters,
                  wall_coords = walls_in_meters,
                  ball_types = ball_types_in_order), frame


def analyse_frame(frame, walls=None, saved_balls=None, saved_oranges=None):

    # Calibrate the frame
    frame = calibrate_frame(frame)

    # Find the wall corners
    if not STATIC_OUTER_WALLS or walls is None:
        walls = analyse_walls(frame)

    # Find the obstacle points
    obstacle = analyse_obstacles(frame)

    # Find the balls
    balls = analyse_balls(frame, saved_balls)

    # Find the orange ball
    orange_ball = analyse_orange_ball(frame, saved_oranges)

    # Remove orange ball from list of balls
    balls = remove_circle_from_list(orange_ball, balls)

    # Find the robot
    if walls is not None and len(walls):
        robot_position, robot_heading = robot_recognition(frame, walls)

    # TODO change this to pixels
    # Discard balls (and robot?) found outside the course
    # if len(balls):
    #     balls = remove_objects_outside_walls_from_list(walls, balls)
    # if len(course.robot_coords):
    #     course.robot_coords = remove_objects_outside_walls_from_list(course.wall_coords, course.robot_coords,
    #                                                                  "robot")

    # TODO Add ball type here?

    return Course(ball_coords=balls,
                  orange_ball=orange_ball,
                  obstacle_coords=obstacle,
                  wall_coords=walls,
                  robot_coords=robot_position,
                  robot_heading=robot_heading
                  ), frame
