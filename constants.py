
## CONFIG ##

## CONSTANTS ##


# Circle detection constants
# param1 is sensitivity (smaller == more circles)
# param2 is number of points in the circle (precision)
# minDist is the minimum distance between circles. Meant to prevent overlapping circles
# default ≈ param1=200, param2=13, minDist=9, minRadius=5, maxRadius=7
CIRCLE_PARAM_1 = 200
CIRCLE_PARAM_2 = 12 # old version
# CIRCLE_PARAM_2 = 6
CIRCLE_MIN_DIST = 9
CIRCLE_MIN_RADIUS = 5
CIRCLE_MAX_RADIUS = 7

# Real world height and width of the course in meters
COURSE_HEIGHT = 1.235
COURSE_WIDTH = 1.683

# Define the frames sampled and minimum number of frames
# that a circle has to be present to in to count as a ball
# SAVED_CIRCLE_DIFF dictates the minimum distance between two detected circles,
# before they count as distinct balls. Is smaller than the one distance specified in Houghcircles
SAVED_FRAMES = 10
CUTOFF = 2
ORANGE_CUTOFF = 1
SAVED_CIRCLE_DIST = 6

# Define color ranges for red wall detection (inverted to cyan)
LOWER_WALL_COLOR = (80, 70, 50)
UPPER_WALL_COLOR = (100, 255, 255)

# Wall area constants for wall detection
# default ≈ min=10000, max=195000
OUTER_WALL_AREA_MIN = 10000
OUTER_WALL_AREA_MAX = 195000

# default ≈ min=1000, max=1600
OBSTACLE_AREA_MIN = 900
OBSTACLE_AREA_MAX = 1600


# Used for rounding numbers of objects
ROUNDING_AMOUNT = 3

# Camera constants
# Distance from camera to floor
CAMERA_HEIGHT = 1.68 # Measure with each setup
CAMERA_DISTORT_X = 0.23 # Measure with each setup by testing for 3 ball positions.
CAMERA_DISTORT_Y = 0.195 # Measure with each setup by testing for 3 ball positions.

# Frame height in meter
FRAME_HEIGHT_METER = 1.49

# Pixel to meter
PIXEL_IN_METER = FRAME_HEIGHT_METER / 480

# Height of objects
BALL_HEIGHT = 0.04
WALL_HEIGHT = 0.071
ROBOT_HEIGHT = 0.205 # placeholder

# Length and width of objects
HALF_OF_ROBOT_WIDTH = 0.14
OBSTACLE_WIDTH = 0.015
OBSTACLE_LENGTH_FROM_MIDDLE = 0.085

# Determination constant for ball type detection
DETERMINATION_THRESHOLD = HALF_OF_ROBOT_WIDTH


AUTOMATED_AREA_DETECT = True

PRINT_COORDINATES = False
PRINT_NUMBER_OF_BALLS = False
STATIC_OUTER_WALLS = True
ENABLE_MULTI_FRAME_BALL_DETECTION = True

GOAL_SIDE_RELATIVE_TO_CAMERA = "left"
LIST_OF_ANCHOR_POINTS = [[COURSE_WIDTH*(1/4), COURSE_HEIGHT*(3/4)],
                         [COURSE_WIDTH*(3/4), COURSE_HEIGHT*(3/4)],
                         [COURSE_WIDTH*(3/4), COURSE_HEIGHT*(1/4)],
                         [COURSE_WIDTH*(1/4), COURSE_HEIGHT*(1/4)]]

# Select video capture device
VIDEO_CAPTURE_DEVICE = 0

# setup const
SETUP_MODE = False

