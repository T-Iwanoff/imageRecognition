import cv2 as cv
from coordinates import *
from refactoring.calibration import *
from image_recognition import analyseFrame


def run_image_analysis(path='Media/Video/MovingBalls.mp4', media='VIDEO', nmbr_of_balls=None):
    # TODO Only map the border at the start, so the robot can't obscure it

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

        prev_number_of_balls = 0

        while True:
            # If out of frames, reset the video
            # propertyID 7 is the number of frames in the video
            if frameCounter == videoCapture.get(7):
                frameCounter = 0
                videoCapture.set(1, 0)  # propertyID 1 is the current frame

            # Get the current frame
            ret, frame = videoCapture.read()
            if not ret:
                print("Error: Frame not found")
                exit()

            prev_number_of_balls = analyseFrame(frame, savedData, frameCounter,
                                                prev_number_of_balls)

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
