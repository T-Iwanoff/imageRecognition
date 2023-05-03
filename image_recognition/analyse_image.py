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

            course = analyse_frame(frame, saved_data, frame_counter)

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

def display_graph(course):
    # print with 2 decimal places
    ball_coords = [tuple(round(coord, 2) for coord in coords)
                   for coords in course.ball_coordinates]
    print(f"Ball coordinates: {ball_coords}")
    obstacle_coords = [tuple(round(coord, 2) for coord in coords)
                       for coords in course.obstacle_coordinates]
    print(f"Obstacle coordinates: {obstacle_coords}")
    wall_coords = [tuple(round(coord, 2) for coord in coords)
                   for coords in course.wall_coordinates]
    print(f"Wall coordinates: {wall_coords}")
    # create graph
    gt.create_graph(course)
    # send coordinates
    # robot.send_coords(course.ball_coordinates[0][0], course.ball_coordinates[0][1])

def get_static_outer_walls(video_capture):
    for i in range(10):
        # Get the current frame
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Frame not found")
            exit()
        static_outer_walls = analyse_walls(frame)
        if static_outer_walls is not None:
            return static_outer_walls
        else:
            return None