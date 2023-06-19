
import math

from shapely.geometry import Polygon

from constants import HALF_ROBOT_LENGTH


def create_box_from_obs_coords(coord1, coord2, width):
    # Unpack coordinates
    x1, y1 = coord1
    x2, y2 = coord2

    # Calculate length (distance between points)
    length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # Calculate direction vector (dx, dy)
    dx = (x2 - x1) / length
    dy = (y2 - y1) / length

    # Calculate normal vector (perpendicular to direction)
    nx = -dy
    ny = dx

    # Calculate four corners of the box
    box_coords = [
        (x1 + width/2 * nx, y1 + width/2 * ny),  # Top-left corner
        (x2 + width/2 * nx, y2 + width/2 * ny),  # Top-right corner
        (x2 - width/2 * nx, y2 - width/2 * ny),  # Bottom-right corner
        (x1 - width/2 * nx, y1 - width/2 * ny)   # Bottom-left corner
    ]

    return box_coords


def create_expanded_box(left_obs_coords, right_obs_coords, top_obs_coords, bot_obs_coords, middle_of_obstacle):

    hor_obs_vector = [left_obs_coords[0] -
                      right_obs_coords[0],
                      left_obs_coords[1] -
                      right_obs_coords[1]]
    vert_obs_vector = [top_obs_coords[0] -
                       bot_obs_coords[0],
                       top_obs_coords[1] -
                       bot_obs_coords[1]]

    obs_expanded_coord1 = [x + y for x, y in zip(
        middle_of_obstacle, [(x + y)/2 for x, y in zip(hor_obs_vector, vert_obs_vector)])],
    obs_expanded_coord2 = [x + y for x, y in zip(
        middle_of_obstacle, [(-x + y)/2 for x, y in zip(hor_obs_vector, vert_obs_vector)])],
    obs_expanded_coord3 = [x + y for x, y in zip(
        middle_of_obstacle, [(-x - y)/2 for x, y in zip(hor_obs_vector, vert_obs_vector)])],
    obs_expanded_coord4 = [x + y for x, y in zip(
        middle_of_obstacle, [(x - y)/2 for x, y in zip(hor_obs_vector, vert_obs_vector)])],

    expanded_box_coords = [obs_expanded_coord1[0], obs_expanded_coord2[0],
                           obs_expanded_coord3[0], obs_expanded_coord4[0]]

    return expanded_box_coords


def create_extended_box(obs_coords):

    # extract coordinates
    top_left, top_right, bottom_right, bottom_left = obs_coords

    new_top_left = move_towards(top_left, bottom_left, -HALF_ROBOT_LENGTH)
    new_top_right = move_towards(top_right, bottom_right, -HALF_ROBOT_LENGTH)
    new_bottom_right = move_towards(
        bottom_right, top_right, -HALF_ROBOT_LENGTH)
    new_bottom_left = move_towards(bottom_left, top_left, -HALF_ROBOT_LENGTH)

    extended_box_coords = [new_top_left, new_top_right,
                           new_bottom_right, new_bottom_left]

    return extended_box_coords


def order_obstacles(obstacle_coords):
    # Sort the coordinates based on y-coordinate (bottom to top)
    sorted_coords = sorted(obstacle_coords, key=lambda c: c[1])

    if math.dist(sorted_coords[3], sorted_coords[2]) > 0.10:
        if sorted_coords[3][0] > sorted_coords[2][0]:
            top_left, top_right = sorted_coords[1], sorted_coords[3]
            bottom_left, bottom_right = sorted_coords[0], sorted_coords[2]
        else:
            top_left, top_right = sorted_coords[3], sorted_coords[1]
            bottom_left, bottom_right = sorted_coords[2], sorted_coords[0]
    elif math.dist(sorted_coords[3], sorted_coords[2]) < 0.10:
        if sorted_coords[3][0] > sorted_coords[2][0]:
            top_left, top_right = sorted_coords[3], sorted_coords[2]
            bottom_left, bottom_right = sorted_coords[1], sorted_coords[0]
        else:
            top_left, top_right = sorted_coords[2], sorted_coords[3]
            bottom_left, bottom_right = sorted_coords[0], sorted_coords[1]

    return [top_left, top_right, bottom_right, bottom_left]


def midpoint(coord1, coord2):
    # Unpack coordinates
    x1, y1 = coord1
    x2, y2 = coord2

    # Calculate and return midpoint
    midpoint_x = (x1 + x2) / 2
    midpoint_y = (y1 + y2) / 2

    return (midpoint_x, midpoint_y)


def mirror_coordinate(coord, mirror_point):
    # Unpack coordinates
    x, y = coord
    mx, my = mirror_point

    # Calculate mirrored coordinates
    mirrored_x = 2*mx - x
    mirrored_y = 2*my - y

    return (mirrored_x, mirrored_y)


def move_towards(coord, target, distance):
    # Unpack coordinates
    x1, y1 = coord
    x2, y2 = target

    # Calculate direction vector (dx, dy)
    direction_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    dx = (x2 - x1) / direction_length
    dy = (y2 - y1) / direction_length

    # Calculate new coordinates
    new_x = x1 + dx * distance
    new_y = y1 + dy * distance

    return (new_x, new_y)


def find_closest_obs_edge(coords, obs1: Polygon, obs2: Polygon):

    # Combine coordinates of both polygons
    point1 = midpoint(obs1.exterior.coords[0], obs1.exterior.coords[1])
    point2 = midpoint(obs1.exterior.coords[2], obs1.exterior.coords[3])

    point3 = midpoint(obs2.exterior.coords[0], obs2.exterior.coords[1])
    point4 = midpoint(obs2.exterior.coords[2], obs2.exterior.coords[3])

    coordinates = [[point1], [point2], [point3], [point4]]

    middle_coordinate = find_closest_obs_corner(coords, coordinates)

    return middle_coordinate


def find_closest_obs_corner(coords, obs):

    # Four coordinates
    coord1 = obs[0]
    coord2 = obs[1]
    coord3 = obs[2]
    coord4 = obs[3]

    print(obs)
    print(coord1, coord2, coord3, coord4)

    # Target coordinate
    target = coords

    # Calculate distances
    distances = [
        math.sqrt((coord[0] - target[0]) ** 2 + (coord[1] - target[1]) ** 2)
        for coord in [coord1, coord2, coord3, coord4]
    ]

    # Find the index of the closest coordinate
    closest_index = distances.index(min(distances))

    # Get the closest coordinate
    closest_coordinate = [coord1, coord2, coord3, coord4][closest_index]

    return closest_coordinate
