import asyncio

import cv2
from course import Course
from image_recognition.calibration import *
from image_recognition.analyse_frame import analyse_frame, analyse_walls
import path_finder.graph_setup as gt
from image_recognition.coordinates import remove_objects_outside_walls_from_list
from image_recognition.robotRecognition import robot_recognition
from constants import STATIC_OUTER_WALLS, ENABLE_MULTI_FRAME_BALL_DETECTION, VIDEO_CAPTURE_DEVICE
from next_move import NextMove
import robot_connection.socket_connection as sc


def analyse_image(path='Media/Video/MovingBalls.mp4', media='VIDEO', mac_camera=False, connect=False):

    # Connect to the robot
    connected = False
    if connect:
        socket_connection = sc.SocketConnection()

        if (socket_connection.connect()):
            print("Connected!")
            connected = True

    # Static picture
    if media == 'IMAGE':
        # TODO: Make robot part of graph
        # Get the current frame
        frame = cv.imread(path)

        # Find walls
        walls = analyse_walls(frame)

        # Make course
        course, ball_frame = analyse_frame(frame, walls)


        # Display the graph
        display_graph(course)

        # Show frame
        cv.imshow('frame', ball_frame)

        # Find the robot
        robot_recognition(frame, course.wall_coords)

        while True:
            if cv.waitKey(0) == ord('q'):
                break
            cv.destroyAllWindows()

    # Moving picture
    if media == 'CAMERA' or 'VIDEO':
        if media == 'VIDEO':
            video_capture = cv.VideoCapture(path)
        elif media == 'CAMERA':
            if mac_camera:
                video_capture = cv.VideoCapture(VIDEO_CAPTURE_DEVICE)
            else:
                video_capture = cv.VideoCapture(VIDEO_CAPTURE_DEVICE, cv.CAP_DSHOW)
            video_capture.set(3, 640)
            video_capture.set(4, 480)

        if not video_capture.isOpened():
            if media == 'VIDEO':
                print("Error: Video not found")
            elif media == 'CAMERA':
                print("Error: Camera not found")
            exit()

        # Find static outer walls
        static_wall_corners = get_static_outer_walls(
            video_capture) if STATIC_OUTER_WALLS else None

        frame_counter = 0

        if ENABLE_MULTI_FRAME_BALL_DETECTION:
            saved_data = []
            orange_balls = []
        else:
            saved_data = None
            orange_balls = None

        while True:
            # Get the current frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Frame not found")
                exit()


            # Analyse the frame
            if STATIC_OUTER_WALLS:
                course, ball_frame = analyse_frame(
                    frame, static_wall_corners, saved_data, orange_balls, frame_counter)
            else:
                course, ball_frame = analyse_frame(frame, saved_circles=saved_data, saved_orange=orange_balls,
                                                   counter=frame_counter)

            # Display robot coords on frame overlay
            course.robot_coords, course.robot_angle, frame_overlay = robot_recognition(
                ball_frame, static_wall_corners)

            if len(course.ball_coords):
                course.ball_coords = remove_objects_outside_walls_from_list(course.wall_coords, course.ball_coords)
            if len(course.robot_coords):
                course.robot_coords = remove_objects_outside_walls_from_list(course.wall_coords, course.robot_coords, "robot")

            if len(course.robot_coords):
                text = "(" + str(round(course.robot_coords[0], 2)) + ", " + str(round(course.robot_coords[1], 2)) + ")"
                cv.putText(frame_overlay, text, (5, 460), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
                text = "Angle: " + str(round(course.robot_angle))
                cv.putText(frame_overlay, text, (300, 460), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

            # Display the frames
            # frame_overlay = overlay_frames(ball_frame, robot_frame)
            cv.imshow('Frame', frame_overlay)



            # print the coordinates of the balls when g is pressed
            if cv.waitKey(1) == ord('g'):
                next_move = display_graph(course)
                next_move.robot_coords = course.robot_coords
                next_move.robot_angle = course.robot_angle
                print("The next move is:", next_move.to_json())
                if connected:
                    print("Sending next move to robot")
                    asyncio.run(
                        socket_connection.async_send_next_move(next_move))

            frame_counter += 1

            # If q is pressed, end the program
            if cv.waitKey(1) == ord('q'):
                break

        # Release the camera and close the window
        video_capture.release()
        cv.destroyAllWindows()


def display_graph(course: Course):
    # print coords with 2 decimal places

    if course.ball_coords is not None:
        ball_coords = [tuple(round(coord, 2) for coord in coords)
                       for coords in course.ball_coords]
        print(f"Ball coordinates: {ball_coords}")
    else:
        print("No ball coordinates found")
    if course.obstacle_coords is not None:
        obstacle_coords = [tuple(round(coord, 2) for coord in coords)
                           for coords in course.obstacle_coords]
        print(f"Obstacle coordinates: {obstacle_coords}")
    else:
        print("No obstacle coordinates found")
    if course.wall_coords is not None:
        wall_coords = [tuple(round(coord, 2) for coord in coords)
                       for coords in course.wall_coords]
        print(f"Wall coordinates: {wall_coords}")
    else:
        print("No wall coordinates found")
    if course.ball_types is not None:
        print(f"Ball types: {course.ball_types}")
    else:
        print("No ball types found")
    # create graph
    return gt.create_graph(course)


def get_static_outer_walls(video_capture):
    walls_detected = False
    while not walls_detected:
        # Get the current frame
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Frame not found")
            exit()
        static_outer_walls = analyse_walls(frame)
        if static_outer_walls is not None:
            walls_detected = True
    return static_outer_walls


def overlay_frames(frame1, frame2):
    # Check if both frames have the same shape
    if frame1.shape == frame2.shape:
        # overlay the images
        overlay = cv2.addWeighted(frame1, 0.5, frame2, 0.5, 0)
    else:
        print("Frames don't have the same shape")
        overlay = None
    return overlay
