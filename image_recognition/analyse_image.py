from course import Course
from image_recognition.calibration import *
from image_recognition.analyse_frame import analyse_frame, analyse_walls
import path_finder.graph_setup as gt
from image_recognition.robotRecognition import robot_recognition
from constants import STATIC_OUTER_WALLS


def analyse_image(path='Media/Video/MovingBalls.mp4', media='VIDEO', nmbr_of_balls=None):

    course = Course()

    if media == 'IMAGE':
        # Get the current frame
        frame = cv.imread(path)

        course = analyse_frame(frame)

        display_graph(course)

        robot_recognition(frame)

        if cv.waitKey(0) == ord('q'):
            cv.destroyAllWindows()

    #####

    if media == 'VIDEO':
        video_capture = cv.VideoCapture(path)
        if not video_capture.isOpened():
            print("Error: Video not found")
            exit()

        frame_counter = 0
        saved_data = []
        orange_balls = []

        # Find static outer walls
        if STATIC_OUTER_WALLS:
            static_wall_corners = get_static_outer_walls(video_capture)

        while True:
            # If out of frames, reset the video
            # propertyID 7 is the number of frames in the video
            if frame_counter == video_capture.get(7):
                frame_counter = 0
                video_capture.set(1, 0)  # propertyID 1 is the current frame

            # Get the current frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Frame not found")
                exit()

            if STATIC_OUTER_WALLS:
                course = analyse_frame(frame, static_wall_corners, saved_data, orange_balls, frame_counter)
            else:
                course = analyse_frame(frame, saved_circles=saved_data, saved_orange=orange_balls, counter=frame_counter)

            # print the coordinates of the balls when g is pressed
            if cv.waitKey(1) == ord('g'):
                display_graph(course)

            robot_recognition(frame)

            frame_counter += 1

            # If q is pressed, end the program
            if cv.waitKey(1) == ord('q'):
                break

        # Release the camera and close the window
        video_capture.release()
        cv.destroyAllWindows()

    ######

    if media == 'CAMERA':

        video_capture = cv.VideoCapture(0, cv.CAP_DSHOW)
        video_capture.set(3, 640)
        video_capture.set(4, 480)

        if not video_capture.isOpened():
            print("Error: Camera not found")
            exit()

        frame_counter = 0
        saved_data = []

        # Find static outer walls
        if STATIC_OUTER_WALLS:
            static_wall_corners = get_static_outer_walls(video_capture)

        while True:
            # Get the current frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Frame not found")
                exit()

            if STATIC_OUTER_WALLS:
                course = analyse_frame(frame, static_wall_corners)
            else:
                course = analyse_frame(frame)

            # print the coordinates of the balls when g is pressed
            if cv.waitKey(1) == ord('g'):
                display_graph(course)

            robot_recognition(frame)

            frame_counter += 1

            # If q is pressed, end the program
            if cv.waitKey(1) == ord('q'):
                break

        # Release the camera and close the window
        video_capture.release()
        cv.destroyAllWindows()

    #####

    if media == 'ROBOT':
        video_capture = cv.VideoCapture(0, cv.CAP_DSHOW)
        video_capture.set(3, 640)
        video_capture.set(4, 480)

        if not video_capture.isOpened():
            print("Error: Camera not found")
            exit()

        frame_counter = 0
        saved_data = []

        course = Course()

        while True:
            # Get the current frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Frame not found")
                exit()

            course = analyse_frame(frame, saved_data, frame_counter)

            frame_counter += 1

            # If q is pressed, end the program
            if cv.waitKey(1) == ord('q'):
                break

        # Release the camera and close the window
        video_capture.release()
        cv.destroyAllWindows()

    #####

    if media == 'MAC_CAMERA':
        video_capture = cv.VideoCapture(0)
        video_capture.set(3, 640)
        video_capture.set(4, 480)

        if not video_capture.isOpened():
            print("Error: Camera not found")
            exit()

        frame_counter = 0
        saved_data = []

        while True:
            # Get the current frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Frame not found")
                exit()

            if STATIC_OUTER_WALLS:
                course = analyse_frame(frame, static_wall_corners)
            else:
                course = analyse_frame(frame)

            # print the coordinates of the balls when g is pressed
            if cv.waitKey(1) == ord('g'):
                display_graph(course)
                # socket_connection.send_coords(course.ball_coords[0][0], course.ball_coords[0][1])

            robot_recognition(frame)

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
    if course.obstacle_coords is not None:
        obstacle_coords = [tuple(round(coord, 2) for coord in coords)
                        for coords in course.obstacle_coords]
        print(f"Obstacle coordinates: {obstacle_coords}")
    if course.wall_coords is not None:
        wall_coords = [tuple(round(coord, 2) for coord in coords)
                    for coords in course.wall_coords]
        print(f"Wall coordinates: {wall_coords}")
    # create graph
    gt.create_graph(course)
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
