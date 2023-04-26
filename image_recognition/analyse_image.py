from image_recognition.calibration import *
from image_recognition.analyse_frame import analyse_frame
from image_recognition.robotRecognition import robot_recognition


def analyse_image(path='Media/Video/MovingBalls.mp4', media='VIDEO', nmbr_of_balls=None):
    # TODO Only map the border at the start, so the robot can't obscure it

    if media == 'IMAGE':
        # Get the current frame
        frame = cv.imread(path)

        analyse_frame(frame)
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

        prev_number_of_balls = 0


        # Find static outer walls
        for i in range(10):
            # Get the current frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Frame not found")
                exit()
            analyse_frame(frame, saved_data, frame_counter)

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

            prev_number_of_balls = analyse_frame(frame, saved_data, frame_counter,
                                                 prev_number_of_balls)
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


        while True:
            # Get the current frame
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Frame not found")
                exit()

            analyse_frame(frame, saved_data, frame_counter)
            robot_recognition(frame)

            frame_counter += 1

            # If q is pressed, end the program
            if cv.waitKey(1) == ord('q'):
                break

        # Release the camera and close the window
        video_capture.release()
        cv.destroyAllWindows()
