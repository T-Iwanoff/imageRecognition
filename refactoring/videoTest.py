import cv2 as cv

videoPath = 'Video/Sample_balls.mp4'

video = cv.VideoCapture(videoPath)

if not video.isOpened():
    print("Video file not found")

frameCounter = 0
# Repeat until window is closed
while True:
    # If out of frames, reset the video
    if frameCounter == video.get(7):    # propertyID 7 is the number of frames in the video
        frameCounter = 0
        video.set(1, 0)     # propertyID 1 is the current frame

    # Get the current frame
    ret, frame = video.read()
    frameCounter += 1

    if not ret:
        print("Video error")
        break

    # Press Q on keyboard to exit
    if cv.waitKey(25) & 0xFF == ord('q'):
        break

    cv.imshow('Video', frame)

video.release()
cv.destroyAllWindows()
