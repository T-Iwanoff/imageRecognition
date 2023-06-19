# Try to connect to the java leJos program
CONNECT_TO_SOCKET = False
# Find the outer walls only once
STATIC_OUTER_WALLS = True
# Count the balls over multiple frames to reduce fake circles
ENABLE_MULTI_FRAME_BALL_DETECTION = True
# Automatically adjust the area targeting for finding walls
AUTOMATED_AREA_DETECT = True
# Adds guiding lines for adjusting the camera
SETUP_MODE = False
# What side of the course is the goal on relative to the camera
GOAL_SIDE_RELATIVE_TO_CAMERA = "left"
# Display Graph
DISPLAY_GRAPH = True

# Select video capture device
VIDEO_CAPTURE_DEVICE = 0

# Define the frames sampled and minimum number of frames
# that a circle has to be present to in to count as a ball
# SAVED_CIRCLE_DIFF dictates the minimum distance between two detected circles,
# before they count as distinct balls. Is smaller than the one distance specified in Houghcircles
SAVED_FRAMES = 10
CUTOFF = 2
ORANGE_CUTOFF = 1
SAVED_CIRCLE_DIST = 6

# Socket connection
ROBOT_IP = '192.168.43.206'
# Thor: 192.168.43.206
# Mark: 192.168.222.107
# Jacob?: 192.168.48.208