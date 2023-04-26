from course import Course
from image_recognition.calibration import *
from image_recognition.analyse_frame import analyse_frame
import path_finder.graph_setup1 as gt


def analyse_image(path='Media/Video/MovingBalls.mp4', media='VIDEO', nmbr_of_balls=None):
    # TODO Only map the border at the start, so the robot can't obscure it

    course = Course()

    if media == 'IMAGE':
        # Get the current frame
        frame = cv.imread(path)

        course = analyse_frame(frame)

        # print the coordinates of the balls
        ball_coords = [tuple(round(coord, 2) for coord in coords)
                       for coords in course.ball_coordinates]
        print(f"Ball coordinates: {ball_coords}")
        obstacle_coords = [tuple(round(coord, 2) for coord in coords)
                           for coords in course.obstacle_coordinates]
        print(f"Obstacle coordinates: {obstacle_coords}")
        wall_coords = [tuple(round(coord, 2) for coord in coords)
                       for coords in course.wall_coordinates]
        print(f"Wall coordinates: {wall_coords}")
        # create graph and show the fastest path
        gt.create_graph(course)

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

            course = analyse_frame(frame, saved_data, frame_counter)

            # print the coordinates of the balls when g is pressed
            if cv.waitKey(1) == ord('g'):
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
                gt.create_graph(course)

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

        while True:
            # Get the current frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Frame not found")
                exit()

            course = analyse_frame(frame, saved_data, frame_counter)

            # print the coordinates of the balls when g is pressed
            if cv.waitKey(1) == ord('g'):
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
                gt.create_graph(course)

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
