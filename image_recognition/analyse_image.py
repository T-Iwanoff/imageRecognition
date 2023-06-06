from course import Course
from image_recognition.calibration import *
from image_recognition.analyse_frame import analyse_frame, analyse_walls
import path_finder.graph_setup as gt
from image_recognition.robotRecognition import robot_recognition
from constants import STATIC_OUTER_WALLS, ENABLE_MULTI_FRAME_BALL_DETECTION
from next_move import NextMove
import robot_connection.socket_connection as sc


def analyse_image(path='Media/Video/MovingBalls.mp4', media='VIDEO', mac_camera=False, nmbr_of_balls=None):

    socket_connection = sc.SocketConnection()
    connected = False
    if (socket_connection.connect()):
        print("Connected!")
        connected = True

    course = Course()

    if media == 'IMAGE':
        # Get the current frame
        frame = cv.imread(path)

        course = analyse_frame(frame)

        display_graph(course)

        robot_recognition(frame)

        while True:
            if cv.waitKey(0) == ord('q'):
                break
            cv.destroyAllWindows()

    if media == 'CAMERA' or 'VIDEO':
        if media == 'VIDEO':
            video_capture = cv.VideoCapture(path)
        elif media == 'CAMERA':
            if mac_camera:
                video_capture = cv.VideoCapture(0)
            else:
                video_capture = cv.VideoCapture(0, cv.CAP_DSHOW)
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
                course = analyse_frame(frame, static_wall_corners, saved_data, orange_balls, frame_counter)
            else:
                course = analyse_frame(frame, saved_circles=saved_data, saved_orange=orange_balls,
                                       counter=frame_counter)


            course.robot_coords, course.robot_angle = robot_recognition(
                frame, static_wall_corners)

            # print the coordinates of the balls when g is pressed
            if cv.waitKey(1) == ord('g'):
                next_move = NextMove(display_graph(course))
                next_move.robot_coords = course.robot_coords
                next_move.robot_angle = course.robot_angle
                print(next_move.to_json())
                if connected:
                    socket_connection.send_next_move(next_move)

            frame_counter += 1

            # If q is pressed, end the program
            if cv.waitKey(1) == ord('q'):
                break

        # Release the camera and close the window
        video_capture.release()
        cv.destroyAllWindows()


def display_graph(course: Course):
    # print with 2 decimal places
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
    # create graph
    return gt.create_graph(course)
    # send coordinates
    # robot.send_coords(course.ball_coordinates[0][0], course.ball_coordinates[0][1])


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
