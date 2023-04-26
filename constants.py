
# Circle detection constants
# ?? param1 is sensitivity (smaller == more circles)
# ?? param2 is number of points in the circle (precision)
# ?? default ≈ param1=80, param2=17, minDist=3, minRadius=3, maxRadius=9
# 1: 100-200 2: 20-30
CIRCLE_PARAM_1 = 200
CIRCLE_PARAM_2 = 13
CIRCLE_MIN_DIST = 9
CIRCLE_MIN_RADIUS = 5
CIRCLE_MAX_RADIUS = 7


# Real world height and width of the course in meters
COURSE_HEIGHT = 1.235
COURSE_WIDTH = 1.683

# Define the frames sampled and minimum number of frames
# that a circle has to be present to in to count as a ball
SAVED_FRAMES = 10
CUTOFF = 4

# Define color ranges for red wall detection (inverted to cyan)
LOWER_WALL_COLOR = (80, 70, 50)
UPPER_WALL_COLOR = (100, 255, 255)


# Wall area constants for wall detection
# default ≈ min=10000, max=195000
OUTER_WALL_AREA_MIN = 10000
OUTER_WALL_AREA_MAX = 195000

# default ≈ min=10000, max=195000
OBSTACLE_AREA_MIN = 10000
OBSTACLE_AREA_MAX = 195000

PRINT_COORDINATES = False
PRINT_NUMBER_OF_BALLS = True
