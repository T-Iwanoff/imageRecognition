import asyncio
import platform
import cv2

from config import *
from course import *
from image_recognition.calibration import *
from image_recognition.analyse_frame import analyse_frame, analyse_walls
import path_finder.graph_setup as gt
from image_recognition.coordinates import remove_objects_outside_walls_from_list, improve_coordinate_precision, \
    determine_order_and_type
from image_recognition.robotRecognition import robot_recognition
from next_move import NextMove
import robot_connection.socket_connection as sc


def analyse_course(path=None, media='CAMERA'):
    if media == 'CAMERA':
        analyse_video()
    elif media == 'VIDEO':
        analyse_video(path, 'VIDEO')
    elif media == 'IMAGE':
        analyse_image(path)


#TODO Fix this method
def analyse_image(path='Media/Image/Bold2-165-84.5.jpg'):

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


def analyse_video(path=None, media='CAMERA'):

    # Connect to the robot
    connected = False
    if CONNECT_TO_SOCKET:
        socket_connection = sc.SocketConnection()
        if (socket_connection.connect()):
            print("Connected!")
            connected = True

    # Get video capture
    video_capture = open_video_capture(media, path)

    # Check video capture
    if not video_capture.isOpened():
        if media == 'VIDEO':
            print("Error: Video not found")
        elif media == 'CAMERA':
            print("Error: Camera not found")
        exit()

    # Create variables
    frame_counter = 0
    static_walls = None
    saved_balls = []
    saved_orange_balls = []

    # Analyse the frames
    while True:
        # Get the current frame
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Frame not found")
            exit()

        # Analyse the frame
        course, calibrated_frame = analyse_frame(frame, static_walls, saved_balls, saved_orange_balls)

        # Save data for future frames
        static_walls = course.wall_coords

        # Simplify variables. Temp?
        balls = course.ball_coords
        walls = course.wall_coords
        obstacle = course.obstacle_coords
        orange_ball = []

        # Convert to meter
        balls_in_meters = []
        orange_ball_in_meters = []
        obstacle_in_meters = []
        walls_in_meters = []

        # Convert to meters
        if course.wall_coords is not None:
            if balls is not None and len(balls):
                for ball in balls:
                    # Convert to meter
                    improved_coords = improve_coordinate_precision(walls, ball, "ball")
                    balls_in_meters.append(improved_coords)

            if orange_ball is not None and len(orange_ball):
                improved_coords = improve_coordinate_precision(walls, orange_ball, "ball")
                orange_ball_in_meters.append(improved_coords)

            if obstacle is not None and len(obstacle):
                for coord in obstacle:
                    # Convert to meter
                    improved_coords = improve_coordinate_precision(walls, coord, "ball")
                    obstacle_in_meters.append(improved_coords)

            if walls is not None and len(walls):
                for coord in walls:
                    # Convert to meter
                    improved_coords = improve_coordinate_precision(walls, coord, "ball")
                    walls_in_meters.append(improved_coords)

        # Draw on the frame
        draw_frame = draw_on_frame(frame=calibrated_frame, course=course, balls=balls_in_meters,
                                   orange_ball=orange_ball_in_meters)

        # TODO Lift robot draw out of robot_recognition
        # Display robot coords on frame overlay
        # course.robot_coords, course.robot_heading, frame_overlay = robot_recognition(
        #     draw_frame, static_walls)

        # Display the frames
        # frame_overlay = overlay_frames(ball_frame, robot_frame)
        cv.imshow('Frame', draw_frame)

        # print the coordinates of the balls when g is pressed
        if cv.waitKey(1) == ord('g'):
            next_move = display_graph(course)
            next_move.robot_coords = course.robot_coords
            next_move.robot_heading = course.robot_heading
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


def draw_on_frame(frame, course: Course, balls, orange_ball):
    if course.wall_coords is not None and len(course.wall_coords):
        cv.drawContours(frame, [course.wall_coords], 0, (255, 0, 0), 2)

    if course.obstacle_coords is not None and len(course.obstacle_coords):
        for coord in course.obstacle_coords:
            cv.circle(frame, (coord[0], coord[1]), 2, (0, 255, 255), 2)

    if course.ball_coords is not None and len(course.ball_coords):
        for ball in course.ball_coords:
            cv.circle(frame, (ball[0], ball[1]), 1, (0, 0, 0), 2)  # Center of the circle
            cv.circle(frame, (ball[0], ball[1]), 6, (255, 0, 255), 2)  # Outer circle
            # Draw coords on frame
            text = "(" + str(round(balls[0], 2)) + ", " + str(round(balls[1], 2)) + ")"
            cv.putText(frame, text, (ball[0] - 40, ball[1] - 20), cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0),
                       1)

    if course.orange_ball is not None and len(course.orange_ball):
        cv.circle(frame, (course.orange_ball[0], course.orange_ball[1]), 1, (0, 0, 0), 2)  # Center of the circle
        cv.circle(frame, (course.orange_ball[0], course.orange_ball[1]), 6, (100, 100, 255), 2)  # Outer circle
        # Draw coords on frame
        text = "(" + str(round(orange_ball[0], 2)) + ", " + str(round(orange_ball[1], 2)) + ")"
        cv.putText(frame, text, (course.orange_ball[0] - 40, course.orange_ball[1] - 20),
                   cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    if course.robot_coords is not None and len(course.robot_coords):
        text = "(" + str(round(course.robot_coords[0], 2)) + ", " + str(round(course.robot_coords[1], 2)) + ")"
        cv.putText(frame, text, (5, 460), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

    if course.robot_heading is not None and len(course.robot_heading):
        text = "Angle: " + str(round(course.robot_heading))
        cv.putText(frame, text, (300, 460), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

    return frame


def open_video_capture(media='CAMERA', path=None):
    if media == 'VIDEO':
        video_capture = cv.VideoCapture(path)
    elif media == 'CAMERA':
        if platform.system() == 'Windows':
            video_capture = cv.VideoCapture(VIDEO_CAPTURE_DEVICE, cv.CAP_DSHOW)
        else:
            video_capture = cv.VideoCapture(VIDEO_CAPTURE_DEVICE)
        video_capture.set(3, 640)
        video_capture.set(4, 480)
    return video_capture


def old_analyse_course(path='Media/Video/MovingBalls.mp4', media='VIDEO'):

    # Connect to the robot
    connected = False
    if CONNECT_TO_SOCKET:
        socket_connection = sc.SocketConnection()
        if (socket_connection.connect()):
            print("Connected!")
            connected = True

    video_capture = open_video_capture(media, path)

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
            course, ball_frame = analyse_frame(frame, saved_balls=saved_data, saved_orange=orange_balls,
                                               counter=frame_counter)

        # Display robot coords on frame overlay
        course.robot_coords, course.robot_heading, frame_overlay = robot_recognition(
            ball_frame, static_wall_corners)

        if len(course.ball_coords):
            course.ball_coords = remove_objects_outside_walls_from_list(course.wall_coords, course.ball_coords)
        if len(course.robot_coords):
            course.robot_coords = remove_objects_outside_walls_from_list(course.wall_coords, course.robot_coords, "robot")

        if len(course.robot_coords):
            text = "(" + str(round(course.robot_coords[0], 2)) + ", " + str(round(course.robot_coords[1], 2)) + ")"
            cv.putText(frame_overlay, text, (5, 460), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
            text = "Angle: " + str(round(course.robot_heading))
            cv.putText(frame_overlay, text, (300, 460), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

        # Display the frames
        # frame_overlay = overlay_frames(ball_frame, robot_frame)
        cv.imshow('Frame', frame_overlay)



        # print the coordinates of the balls when g is pressed
        if cv.waitKey(1) == ord('g'):
            next_move = display_graph(course)
            next_move.robot_coords = course.robot_coords
            next_move.robot_heading = course.robot_heading
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
