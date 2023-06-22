import time
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PolygonPatch
import networkx as nx
import random
import math
import numpy as np
import pandas as pd
from python_tsp.exact import solve_tsp_dynamic_programming
from shapely.geometry import LineString, box, shape, Polygon, Point
from course import Course
from constants import *
from next_move import NextMove
from config import *

### GRAPH SETTINGS ###
# display settings
NODE_SIZE = 200
EDGE_WIDTH = 1
DISPLAY_HEIGHT = 3.5
DISPLAY_WIDTH = 6

# global left_obstacle, right_obstacle, top_obstacle, bottom_obstacle
# left_obstacle = None
# right_obstacle = None
# top_obstacle = None
# bottom_obstacle = None


def create_graph(course: Course):

    nmbr_of_nodes = len(course.ball_coords)+1

    start_node = 0
    end_node = nmbr_of_nodes-1
    orange_ball = False

    ### GRAPH CREATION ###
    G = nx.Graph()

    ### NODES ###

    # add nodes
    G.add_nodes_from(range(nmbr_of_nodes))

    pos = nx.random_layout(G, dim=2, center=None)
    # add nodes at ball coords

    if course.robot_coords is not None:
        G.add_node(0)
        if len(course.robot_coords) != 0:
            pos[0] = (course.robot_coords[0], course.robot_coords[1])

    for i in range(nmbr_of_nodes-1):
        x = course.ball_coords[i][0]
        y = course.ball_coords[i][1]
        G.add_node(i+1)
        pos[i+1] = (x, y)

    if len(course.orange_ball) > 0 and course.orange_ball is not None:
        G.add_node(nmbr_of_nodes)
        pos[nmbr_of_nodes] = (course.orange_ball[0], course.orange_ball[1])
        nmbr_of_nodes += 1
        orange_ball = True

    # Randomize node positions
    # pos = nx.random_layout(G, dim=2, center=None)
    # for node, coords in pos.items():
    #     x = random.uniform(0, GRAPH_WIDTH)
    #     y = random.uniform(0, GRAPH_HEIGHT)
    #     pos[node] = (x, y)

    ### OBSTACLES ###
    # calculate the center of the plot
    center_x = COURSE_WIDTH/2
    center_y = COURSE_HEIGHT/2
    # create the obstacles
    # obstacle_1 = box(center_x - 10, center_y - 1.5,
    #                  center_x + 10, center_y + 1.5)
    # obstacle_2 = box(center_x - 1.5, center_y - 10,
    #                  center_x + 1.5, center_y + 10)

    left_obstacle, top_obstacle, right_obstacle, bottom_obstacle = None, None, None, None
    # check if there are obstacles
    if len(course.obstacle_coords) > 0:

        left_obstacle = course.obstacle_coords[0]
        top_obstacle = course.obstacle_coords[1]
        right_obstacle = course.obstacle_coords[2]
        bottom_obstacle = course.obstacle_coords[3]

        # TODO: ORDER THE OBSTACLES
        hor_obs_vector = [left_obstacle[0] -
                          right_obstacle[0],
                          left_obstacle[1] -
                          right_obstacle[1]]
        vert_obs_vector = [top_obstacle[0] -
                           bottom_obstacle[0],
                           top_obstacle[1] -
                           bottom_obstacle[1]]

        # Obstacle orthogonal vector
        hor_obs_orthog_vector = [
            -hor_obs_vector[1], hor_obs_vector[0]]
        vert_obs_orthog_vector = [
            -vert_obs_vector[1], vert_obs_vector[0]]

        # Obstacle orthogonal unit vectors
        hor_obs_orthog_unit_vector = [
            hor_obs_orthog_vector[0]/np.linalg.norm(hor_obs_orthog_vector),
            hor_obs_orthog_vector[1]/np.linalg.norm(hor_obs_orthog_vector)]
        vert_obs_orthog_unit_vector = [
            vert_obs_orthog_vector[0]/np.linalg.norm(vert_obs_orthog_vector),
            vert_obs_orthog_vector[1]/np.linalg.norm(vert_obs_orthog_vector)]

        # Obstacle unit vectors
        hor_obs_unit_vector = [
            hor_obs_vector[0]/np.linalg.norm(hor_obs_vector),
            hor_obs_vector[1]/np.linalg.norm(hor_obs_vector)]
        vert_obs_unit_vector = [
            vert_obs_vector[0]/np.linalg.norm(vert_obs_vector),
            vert_obs_vector[1]/np.linalg.norm(vert_obs_vector)]

        # Obstacle orthogonal length vector
        hor_obs_orthog_length_vector = [
            hor_obs_orthog_unit_vector[0]*OBSTACLE_WIDTH/2, hor_obs_orthog_unit_vector[1]*OBSTACLE_WIDTH/2]
        vert_obs_orthog_length_vector = [
            vert_obs_orthog_unit_vector[0]*OBSTACLE_WIDTH/2, vert_obs_orthog_unit_vector[1]*OBSTACLE_WIDTH/2]

        hor_obs_length_vector = [
            hor_obs_unit_vector[0]*HALF_ROBOT_LENGTH, hor_obs_unit_vector[1]*HALF_ROBOT_LENGTH]
        vert_obs_length_vector = [
            vert_obs_unit_vector[0]*HALF_ROBOT_LENGTH, vert_obs_unit_vector[1]*HALF_ROBOT_LENGTH]

        # Obstacle coords
        hor_obs_coords = [
            [left_obstacle[0] + hor_obs_orthog_length_vector[0],
                left_obstacle[1] + hor_obs_orthog_length_vector[1]],
            [right_obstacle[0]-hor_obs_orthog_length_vector[0],
                right_obstacle[1]-hor_obs_orthog_length_vector[1]],
            [left_obstacle[0]-hor_obs_orthog_length_vector[0],
                left_obstacle[1]-hor_obs_orthog_length_vector[1]],
            [right_obstacle[0]+hor_obs_orthog_length_vector[0],
                right_obstacle[1]+hor_obs_orthog_length_vector[1]]]

        vert_obs_coords = [
            [top_obstacle[0]+vert_obs_orthog_length_vector[0],
                top_obstacle[1]+vert_obs_orthog_length_vector[1]],
            [bottom_obstacle[0]-vert_obs_orthog_length_vector[0],
                bottom_obstacle[1]-vert_obs_orthog_length_vector[1]],
            [top_obstacle[0]-vert_obs_orthog_length_vector[0],
                top_obstacle[1]-vert_obs_orthog_length_vector[1]],
            [bottom_obstacle[0]+vert_obs_orthog_length_vector[0],
                bottom_obstacle[1]+vert_obs_orthog_length_vector[1]]]

        # Order obstacles coords
        hor_obs_coords = order_obstacles(hor_obs_coords)
        vert_obs_coords = order_obstacles(vert_obs_coords)

        # Create expanded obstacles
        middle_of_obstacle = [
            left_obstacle[0] - hor_obs_vector[0]/2], [left_obstacle[1] - hor_obs_vector[1]/2]

        obs_expanded_corners_point1 = [x + y for x, y in zip(
            middle_of_obstacle, [(x + y)/2 for x, y in zip(hor_obs_vector, vert_obs_vector)])]
        obs_expanded_corners_point2 = [x + y for x, y in zip(
            middle_of_obstacle, [(-x + y)/2 for x, y in zip(hor_obs_vector, vert_obs_vector)])]
        obs_expanded_corners_point3 = [x + y for x, y in zip(
            middle_of_obstacle, [(-x - y)/2 for x, y in zip(hor_obs_vector, vert_obs_vector)])]
        obs_expanded_corners_point4 = [x + y for x, y in zip(
            middle_of_obstacle, [(x - y)/2 for x, y in zip(hor_obs_vector, vert_obs_vector)])]

        obs_expanded_corners_point1 = np.squeeze(obs_expanded_corners_point1)
        obs_expanded_corners_point2 = np.squeeze(obs_expanded_corners_point2)
        obs_expanded_corners_point3 = np.squeeze(obs_expanded_corners_point3)
        obs_expanded_corners_point4 = np.squeeze(obs_expanded_corners_point4)

        obs_expanded_corners = [
            obs_expanded_corners_point1,
            obs_expanded_corners_point2,
            obs_expanded_corners_point3,
            obs_expanded_corners_point4
        ]

        # TODO: make obstacles more expanded
        # hor_obs_extended_top_left = [
        #     hor_obs_coords[0][0] - hor_obs_length_vector[0], hor_obs_coords[0][1] - hor_obs_length_vector[1]]
        # hor_obs_extended_top_right = [
        #     hor_obs_coords[1][0] - hor_obs_length_vector[0], hor_obs_coords[1][1] - hor_obs_length_vector[1]]
        # hor_obs_extended_bot_right = [
        #     hor_obs_coords[2][0] + hor_obs_length_vector[0], hor_obs_coords[2][1] + hor_obs_length_vector[1]]
        # hor_obs_extended_bot_left = [
        #     hor_obs_coords[3][0] + hor_obs_length_vector[0], hor_obs_coords[3][1] + hor_obs_length_vector[1]]
        hor_obs_extended_top_left = move_opposite(
            hor_obs_coords[0], hor_obs_coords[3], HALF_ROBOT_LENGTH*4)
        hor_obs_extended_top_right = move_opposite(
            hor_obs_coords[1], hor_obs_coords[2], HALF_ROBOT_LENGTH*4)
        hor_obs_extended_bot_right = move_opposite(
            hor_obs_coords[2], hor_obs_coords[1], HALF_ROBOT_LENGTH*4)
        hor_obs_extended_bot_left = move_opposite(
            hor_obs_coords[3], hor_obs_coords[0], HALF_ROBOT_LENGTH*4)

        hor_obs_extended = [
            hor_obs_extended_top_left,
            hor_obs_extended_top_right,
            hor_obs_extended_bot_right,
            hor_obs_extended_bot_left
        ]

        vert_obs_extended_top_left = move_opposite(
            vert_obs_coords[0], vert_obs_coords[3], HALF_ROBOT_LENGTH*4)
        vert_obs_extended_top_right = move_opposite(
            vert_obs_coords[1], vert_obs_coords[2], HALF_ROBOT_LENGTH*4)
        vert_obs_extended_bot_right = move_opposite(
            vert_obs_coords[2], vert_obs_coords[1], HALF_ROBOT_LENGTH*4)
        vert_obs_extended_bot_left = move_opposite(
            vert_obs_coords[3], vert_obs_coords[0], HALF_ROBOT_LENGTH*4)

        vert_obs_extended = [
            vert_obs_extended_top_left,
            vert_obs_extended_top_right,
            vert_obs_extended_bot_right,
            vert_obs_extended_bot_left
        ]

        # Create expanded walls
        top_left_wall_expanded_point = [
            HALF_ROBOT_LENGTH, COURSE_HEIGHT-HALF_ROBOT_LENGTH,
        ]
        top_right_wall_expanded_point = [
            COURSE_WIDTH-HALF_ROBOT_LENGTH, COURSE_HEIGHT-HALF_ROBOT_LENGTH,
        ]
        bottom_left_wall_expanded_point = [
            HALF_ROBOT_LENGTH, HALF_ROBOT_LENGTH,
        ]
        bottom_right_wall_expanded_point = [
            COURSE_WIDTH-HALF_ROBOT_LENGTH, HALF_ROBOT_LENGTH,
        ]

        left_wall_expanded = [
            [0, COURSE_HEIGHT],
            top_left_wall_expanded_point,
            bottom_left_wall_expanded_point,
            [0, 0]
        ]
        top_wall_expanded = [
            [0, COURSE_HEIGHT],
            [COURSE_WIDTH, COURSE_HEIGHT],
            top_right_wall_expanded_point,
            top_left_wall_expanded_point
        ]
        right_wall_expanded = [
            top_right_wall_expanded_point,
            [COURSE_WIDTH, COURSE_HEIGHT],
            [COURSE_WIDTH, 0],
            bottom_right_wall_expanded_point
        ]
        bottom_wall_expanded = [
            bottom_left_wall_expanded_point,
            bottom_right_wall_expanded_point,
            [COURSE_WIDTH, 0],
            [0, 0]
        ]

    if left_obstacle is not None:
        # obstacles
        hor_obs_poly = Polygon(hor_obs_coords)
        vert_obs_poly = Polygon(vert_obs_coords)
        # obstacles expanded
        obs_expanded_corners_poly = Polygon(obs_expanded_corners)
        hor_obs_extended_poly = Polygon(hor_obs_extended)
        vert_obs_extended_poly = Polygon(vert_obs_extended)
        # walls expanded
        left_wall_expanded_poly = Polygon(left_wall_expanded)
        top_wall_expanded_poly = Polygon(top_wall_expanded)
        right_wall_expanded_poly = Polygon(right_wall_expanded)
        bottom_wall_expanded_poly = Polygon(bottom_wall_expanded)

    ### REPOSITION NODES ###
    short_extra_distance = 0.01

    corner_extra_distance = 0.18
    edge_extra_distance = 0.27

    extra_point_distance = 0.55

    extra_points = []

    # Reposition nodes if they intersect with obstacles
    if left_obstacle is not None:
        middle_of_obstacle = np.squeeze(middle_of_obstacle)
        for i in range(nmbr_of_nodes-2 if orange_ball else nmbr_of_nodes-1):
            # If inside obs_extended_poly
            if hor_obs_extended_poly.contains(Point(pos[i+1])) or vert_obs_extended_poly.contains(Point(pos[i+1])):

                pos[i+1] = find_closest_obs_edge(pos[i+1],
                                                 hor_obs_extended, vert_obs_extended)

                pos[i+1] = np.squeeze(move_away_from_obstacle(pos[i+1],
                                                              middle_of_obstacle, edge_extra_distance)).tolist()
                course.ball_coords[i] = pos[i+1]
                course.ball_types[i] = "middle_edge"

                extra_points.append(np.squeeze(move_opposite(
                    pos[i+1], middle_of_obstacle, extra_point_distance)).tolist())

                # print("extra_point: ", extra_points_in_order)
                # print("extra_point:", extra_points_in_order)

            # If inside obs_expanded_corners_poly
            elif obs_expanded_corners_poly.contains(Point(pos[i+1])):

                pos[i +
                    1] = find_closest_obs_corner(pos[i+1], obs_expanded_corners)

                pos[i+1] = np.squeeze(move_away_from_obstacle(pos[i+1],
                                                              middle_of_obstacle, corner_extra_distance)).tolist()
                # print(pos[i+1])

                course.ball_coords[i] = pos[i+1]
                course.ball_types[i] = "middle_corner"

                extra_points.append(np.squeeze(move_opposite(
                    pos[i+1], middle_of_obstacle, extra_point_distance)).tolist())

            elif course.ball_types[i] == "none":
                extra_points.append([0, 0])
            elif course.ball_types[i] != "none":
                extra_points.append([0, 0])
                if course.ball_types[i] == "lower_left_corner":
                    pos[i+1] = [HALF_ROBOT_LENGTH +
                                short_extra_distance, HALF_ROBOT_LENGTH+short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "lower_right_corner":
                    pos[i+1] = [COURSE_WIDTH -
                                HALF_ROBOT_LENGTH-short_extra_distance, HALF_ROBOT_LENGTH+short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "upper_left_corner":
                    pos[i+1] = [HALF_ROBOT_LENGTH+short_extra_distance,
                                COURSE_HEIGHT - HALF_ROBOT_LENGTH-short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "upper_right_corner":
                    pos[i+1] = [COURSE_WIDTH - HALF_ROBOT_LENGTH-short_extra_distance,
                                COURSE_HEIGHT - HALF_ROBOT_LENGTH-short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "left_edge":
                    pos[i+1] = [HALF_ROBOT_LENGTH +
                                short_extra_distance, pos[i+1][1]]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "right_edge":
                    pos[i+1] = [COURSE_WIDTH -
                                HALF_ROBOT_LENGTH-short_extra_distance, pos[i+1][1]]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "lower_edge":
                    pos[i+1] = [pos[i+1][0],
                                HALF_ROBOT_LENGTH+short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "upper_edge":
                    pos[i+1] = [pos[i+1][0], COURSE_HEIGHT -
                                HALF_ROBOT_LENGTH-short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
    if orange_ball:
        # If inside obs_extended_poly
        if hor_obs_extended_poly.contains(Point(pos[nmbr_of_nodes-1])) or vert_obs_extended_poly.contains(Point(pos[nmbr_of_nodes-1])):

            pos[nmbr_of_nodes-1] = find_closest_obs_edge(pos[nmbr_of_nodes-1],
                                                         hor_obs_extended, vert_obs_extended)

            pos[nmbr_of_nodes-1] = np.squeeze(move_away_from_obstacle(pos[nmbr_of_nodes-1],
                                                                      middle_of_obstacle, edge_extra_distance)).tolist()

            course.orange_ball = pos[nmbr_of_nodes-1]

            course.ball_types[nmbr_of_nodes-2] = "middle_edge"

            extra_points.append(np.squeeze(move_opposite(
                pos[nmbr_of_nodes-1], middle_of_obstacle, extra_point_distance)).tolist())

        # If inside obs_expanded_corners_poly
        elif obs_expanded_corners_poly.contains(Point(pos[nmbr_of_nodes-1])):

            pos[nmbr_of_nodes-1] = find_closest_obs_corner(
                pos[nmbr_of_nodes-1], obs_expanded_corners)

            pos[nmbr_of_nodes-1] = np.squeeze(move_away_from_obstacle(pos[nmbr_of_nodes-1],
                                                                      middle_of_obstacle, corner_extra_distance)).tolist()

            course.orange_ball = pos[nmbr_of_nodes-1]
            course.ball_types[nmbr_of_nodes-2] = "middle_corner"

            extra_points.append(np.squeeze(move_opposite(
                pos[nmbr_of_nodes-1], middle_of_obstacle, extra_point_distance)).tolist())

        elif course.ball_types[nmbr_of_nodes-2] == "none":
            extra_points.append([0, 0])
        elif course.ball_types[nmbr_of_nodes-2] != "none":
            extra_points.append([0, 0])
            if course.ball_types[nmbr_of_nodes-2] == "lower_left_corner":
                pos[nmbr_of_nodes-1] = [HALF_ROBOT_LENGTH +
                                        short_extra_distance, HALF_ROBOT_LENGTH+short_extra_distance]
                course.orange_ball = pos[nmbr_of_nodes-1]
            elif course.ball_types[nmbr_of_nodes-2] == "lower_right_corner":
                pos[nmbr_of_nodes-1] = [COURSE_WIDTH -
                                        HALF_ROBOT_LENGTH-short_extra_distance, HALF_ROBOT_LENGTH+short_extra_distance]
                course.orange_ball = pos[nmbr_of_nodes-1]
            elif course.ball_types[nmbr_of_nodes-2] == "upper_left_corner":
                pos[nmbr_of_nodes-1] = [HALF_ROBOT_LENGTH+short_extra_distance,
                                        COURSE_HEIGHT - HALF_ROBOT_LENGTH-short_extra_distance]
                course.orange_ball = pos[nmbr_of_nodes-1]
            elif course.ball_types[nmbr_of_nodes-2] == "upper_right_corner":
                pos[nmbr_of_nodes-1] = [COURSE_WIDTH - HALF_ROBOT_LENGTH-short_extra_distance,
                                        COURSE_HEIGHT - HALF_ROBOT_LENGTH-short_extra_distance]
                course.orange_ball = pos[nmbr_of_nodes-1]
            elif course.ball_types[nmbr_of_nodes-2] == "left_edge":
                pos[nmbr_of_nodes-1] = [HALF_ROBOT_LENGTH +
                                        short_extra_distance, pos[nmbr_of_nodes-1][1]]
                course.orange_ball = pos[nmbr_of_nodes-1]
            elif course.ball_types[nmbr_of_nodes-2] == "right_edge":
                pos[nmbr_of_nodes-1] = [COURSE_WIDTH -
                                        HALF_ROBOT_LENGTH-short_extra_distance, pos[nmbr_of_nodes-1][1]]
                course.orange_ball = pos[nmbr_of_nodes-1]
            elif course.ball_types[nmbr_of_nodes-2] == "lower_edge":
                pos[nmbr_of_nodes-1] = [pos[nmbr_of_nodes-1][0],
                                        HALF_ROBOT_LENGTH+short_extra_distance]
                course.orange_ball = pos[nmbr_of_nodes-1]
            elif course.ball_types[nmbr_of_nodes-2] == "upper_edge":
                pos[nmbr_of_nodes-1] = [pos[nmbr_of_nodes-1][0], COURSE_HEIGHT -
                                        HALF_ROBOT_LENGTH-short_extra_distance]
                course.orange_ball = pos[nmbr_of_nodes-1]

    ### EDGES ###
    edge_weights = {}
    # Add edges not intersecting with obstacles
    if left_obstacle is not None:
        anchor_level = 0
        # If not last ball left
        # if nmbr_of_nodes > 1:
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                if G.has_node(i) and G.has_node(j):
                    edge_coords = LineString([pos[i], pos[j]])
                    if not edge_coords.intersects(hor_obs_poly) and not edge_coords.intersects(vert_obs_poly) and not edge_coords.intersects(obs_expanded_corners_poly) and not edge_coords.intersects(left_wall_expanded_poly) and not edge_coords.intersects(top_wall_expanded_poly) and not edge_coords.intersects(right_wall_expanded_poly) and not edge_coords.intersects(bottom_wall_expanded_poly) and not edge_coords.intersects(hor_obs_extended_poly) and not edge_coords.intersects(vert_obs_extended_poly):
                        dist = math.sqrt((pos[i][0] - pos[j][0])
                                         ** 2 + (pos[i][1] - pos[j][1]) ** 2)
                        G.add_edge(i, j, weight=dist)
                        edge_weights[(i, j)] = dist
                    # else:
                    #     # fake edge weight for algorithm
                    #     G.add_edge(i, j, weight=math.inf)
        # TODO: Is nx connected when only 2 nodes?
        # check if graph is connected and if node 0 is connected to at least 2 nodes
        robot_not_connected = True

        for i in G.nodes:
            if G.has_edge(0, i):
                robot_not_connected = False
                break
        while robot_not_connected and len(pos) > 1 and anchor_level < 5:
            for i in G.nodes:
                if G.has_edge(0, i):
                    robot_not_connected = False

            # remove all edges
            G.remove_edges_from(list(G.edges()))
            edge_weights = {}

            extra_points, course, pos, G = place_anchor_points(
                anchor_level, extra_points, course, pos, G)
            anchor_level += 1
            for i in range(len(pos)):
                for j in range(i + 1, len(pos)):
                    # if nodes exist
                    if G.has_node(i) and G.has_node(j):
                        edge_coords = LineString([pos[i], pos[j]])
                        if not edge_coords.intersects(hor_obs_poly) and not edge_coords.intersects(vert_obs_poly) and not edge_coords.intersects(obs_expanded_corners_poly) and not edge_coords.intersects(left_wall_expanded_poly) and not edge_coords.intersects(top_wall_expanded_poly) and not edge_coords.intersects(right_wall_expanded_poly) and not edge_coords.intersects(bottom_wall_expanded_poly) and not edge_coords.intersects(hor_obs_extended_poly) and not edge_coords.intersects(vert_obs_extended_poly):
                            dist = math.sqrt((pos[i][0] - pos[j][0])
                                             ** 2 + (pos[i][1] - pos[j][1]) ** 2)
                            G.add_edge(i, j, weight=dist)
                            edge_weights[(i, j)] = dist
        # while (not nx.is_connected(G) or G.degree[0] < 2) and len(pos) > 1 and anchor_level < 5:
        #     # remove all edges
        #     G.remove_edges_from(list(G.edges()))
        #     print("G.edges() after removing all edges: ", G.edges())
        #     edge_weights = {}

        #     extra_points, course, pos, G = place_anchor_points(anchor_level, extra_points, course, pos, G)
        #     anchor_level += 1
        #     for i in range(len(pos)):
        #         for j in range(i + 1, len(pos)):
        #             # if nodes exist
        #             if G.has_node(i) and G.has_node(j):
        #                 edge_coords = LineString([pos[i], pos[j]])
        #                 if not edge_coords.intersects(hor_obs_poly) and not edge_coords.intersects(vert_obs_poly) and not edge_coords.intersects(obs_expanded_corners_poly) and not edge_coords.intersects(left_wall_expanded_poly) and not edge_coords.intersects(top_wall_expanded_poly) and not edge_coords.intersects(right_wall_expanded_poly) and not edge_coords.intersects(bottom_wall_expanded_poly) and not edge_coords.intersects(hor_obs_extended_poly) and not edge_coords.intersects(vert_obs_extended_poly):
        #                     dist = math.sqrt((pos[i][0] - pos[j][0])
        #                                      ** 2 + (pos[i][1] - pos[j][1]) ** 2)
        #                     G.add_edge(i, j, weight=dist)
        #                     edge_weights[(i, j)] = dist
        #                 # else:
        #                 #     # fake edge weight for algorithm
        #                 #     G.add_edge(i, j, weight=math.inf)

        nx.set_edge_attributes(G, edge_weights, "weight")

        nmbr_of_nodes = len(pos)

        # add fake edges for all nodes not connected to each other
        for i in range(nmbr_of_nodes):
            for j in range(i + 1, nmbr_of_nodes):
                if not G.has_edge(i, j):
                    G.add_edge(i, j, weight=math.inf)

        # elif nmbr_of_nodes == 2:
        #     edge_coords = LineString([pos[0], pos[1]])
        #     if not edge_coords.intersects(obstacle_1) and not edge_coords.intersects(obstacle_2):
        #         dist = math.sqrt((pos[0][0] - pos[1][0])
        #                          ** 2 + (pos[0][1] - pos[1][1]) ** 2)
        #         G.add_edge(0, 1, weight=dist)
        #         edge_weights[(0, 1)] = dist

    # calculate edge weights based on distance between nodes

    # add edge weights to the graph

    ### SHORTEST PATH ###
    start_time = time.time()

    # if nmbr_of_nodes > 0:
    #     if nx.is_connected(G) and len(G.edges) > 0 and nmbr_of_nodes > 2:
    #         tsp = solve_tsp(G)
    #     elif nmbr_of_nodes == 2 and len(G.edges) > 0:
    #         print("2 nodesssssssssss")
    #         tsp = [[0, 1], math.dist(pos[0], pos[1])]

    # find closest node connected to node 0

    # # remove the node with the same number as closest_node
    # tsp[0].remove(closest_node)
    # tsp[0].insert(1, closest_node)

    # print("nx.connected: ", nx.is_connected(G))

    end_time = time.time()
    # print(f"Algo took: {end_time - start_time} seconds to finish")
    # print("Ball_types: ", course.ball_types)
    # print("---------------------------------")

    # remove fake edges
    for edge in G.edges:
        if G[edge[0]][edge[1]]["weight"] == math.inf:
            G.remove_edge(edge[0], edge[1])

    # check through all edges and if connected to 0 find closest node
    closest_node = None
    closest_node_dist = 0
    for i in G.nodes:
        if G.has_edge(0, i):
            if closest_node is None:
                closest_node = i
                closest_node_dist = edge_weights[(0, i)]
            elif edge_weights[(0, i)] < closest_node_dist:
                closest_node = i
                closest_node_dist = edge_weights[(0, i)]

    ### GRAPH DISPLAY ###
    if DISPLAY_GRAPH:
        plt.figure(figsize=(DISPLAY_WIDTH, DISPLAY_HEIGHT))

        # nodes
        nx.draw_networkx_nodes(G, pos, node_size=NODE_SIZE)

        # edges
        nx.draw_networkx_edges(G, pos, width=EDGE_WIDTH)
        # if nmbr_of_nodes > 0:
        #     if len(G.edges) > 0:
        #         nx.draw_networkx_edges(G, pos, edgelist=list(
        #             zip(tsp[0], tsp[0][1:])), width=EDGE_WIDTH, edge_color='r')
        #     elif len(G.edges) == 1 and len(G.nodes) == 2:
        #         # TODO: Add visual edge?
        #         print("Graph has 1 ball left and is connected")

        # node labels
        nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif")

        # edge weight labels
        edge_labels = {k: "{:.2f}".format(v) for k, v in edge_weights.items()}
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_size=6, label_pos=0.5, bbox=dict(boxstyle="round", fc="w", ec="1", alpha=0.9, pad=0.1))

        # create the graph display

        ax = plt.gca()

        # set the axis limits
        ax.set_xlim(0, COURSE_WIDTH)
        ax.set_ylim(0, COURSE_HEIGHT)

        # display the obstacles
        if left_obstacle is not None:

            # obstacle patches
            hor_obs_patch = PolygonPatch([(hor_obs_coords[0]),
                                          (hor_obs_coords[1]),
                                          (hor_obs_coords[2]),
                                          (hor_obs_coords[3])], alpha=0.5, color="red")

            vert_obs_patch = PolygonPatch([(vert_obs_coords[0]),
                                           (vert_obs_coords[1]),
                                           (vert_obs_coords[2]),
                                           (vert_obs_coords[3])], alpha=0.5, color="red")
            obs_expanded_corners_patch = PolygonPatch([(obs_expanded_corners[0]),
                                                       (obs_expanded_corners[1]),
                                                       (obs_expanded_corners[2]),
                                                       (obs_expanded_corners[3])], alpha=0.2, color="red")

            hor_obs_extented_patch = PolygonPatch([(hor_obs_extended_top_left),
                                                   (hor_obs_extended_top_right),
                                                   (hor_obs_extended_bot_right),
                                                   (hor_obs_extended_bot_left)], alpha=0.2, color="red")
            vert_obs_extended_patch = PolygonPatch([(vert_obs_extended_top_left),
                                                    (vert_obs_extended_top_right),
                                                    (vert_obs_extended_bot_right),
                                                    (vert_obs_extended_bot_left)], alpha=0.2, color="red")

            # wall patches
            left_wall_expanded_patch = PolygonPatch([(left_wall_expanded[0]),
                                                    (left_wall_expanded[1]),
                                                    (left_wall_expanded[2]),
                                                    (left_wall_expanded[3])], alpha=0.2, color="red")
            right_wall_expanded_patch = PolygonPatch([(right_wall_expanded[0]),
                                                      (right_wall_expanded[1]),
                                                      (right_wall_expanded[2]),
                                                      (right_wall_expanded[3])], alpha=0.2, color="red")
            top_wall_expanded_patch = PolygonPatch([(top_wall_expanded[0]),
                                                    (top_wall_expanded[1]),
                                                    (top_wall_expanded[2]),
                                                    (top_wall_expanded[3])], alpha=0.2, color="red")
            bottom_wall_expanded_patch = PolygonPatch([(bottom_wall_expanded[0]),
                                                       (bottom_wall_expanded[1]),
                                                       (bottom_wall_expanded[2]),
                                                       (bottom_wall_expanded[3])], alpha=0.2, color="red")

            ax.add_patch(left_wall_expanded_patch)
            ax.add_patch(right_wall_expanded_patch)
            ax.add_patch(top_wall_expanded_patch)
            ax.add_patch(bottom_wall_expanded_patch)

            ax.add_patch(hor_obs_patch)
            ax.add_patch(vert_obs_patch)
            ax.add_patch(obs_expanded_corners_patch)
            ax.add_patch(hor_obs_extented_patch)
            ax.add_patch(vert_obs_extended_patch)

        # print the graph matrix
        # printGraphMatrix(G)

        # display the graph
        ax.tick_params(left=True, bottom=True, labelleft=True,
                       labelbottom=True)  # showing the axis numbers
        ax.margins(0.08)  # margin between the nodes and the axis
        plt.axis("on")
        plt.tight_layout()

        plt.show()

    move_types_in_order = []
    extra_point_in_order = []

    # print("tsp: ", tsp)
    # print("course.ball_coords: ", course.ball_coords)

    # if len(G.edges) > 0:
    #     for i in range(len(tsp[0])):
    #         for j in range(len(course.ball_coords)):
    #             if pos[tsp[0][i]][0] == course.ball_coords[j][0]:
    #                 move_types_in_order.append(course.ball_types[j])
    #                 extra_point_in_order.append(extra_points[j])
    #         if orange_ball:
    #             if pos[tsp[0][i]][0] == course.orange_ball[0]:
    #                 move_types_in_order.append(
    #                     course.ball_types[len(course.ball_types) - 1])
    #                 extra_point_in_order.append(
    #                     extra_points[len(course.ball_types) - 1])

    # print("move_types_in_order: ", move_types_in_order)
    # print("extra_point_in_order: ", extra_point_in_order)

    # next_move = NextMove(next_ball = closest_node, move_type = move_types_in_order[0], extra_point = extra_point_in_order[0])

    # if nmbr_of_nodes > 0: return coords of first node in tsp

    # print("pos: ", pos)
    # if
    #     closest_dist = math.inf
    #     for node in G.nodes:
    #         if node != 0 and G.has_edge(0, node):
    #             dist = G[0][node]["weight"]
    #             if dist < closest_dist:
    #                 closest_dist = dist
    #                 closest_node = node

    # change tsp to go from closest node to node 0
    # print("closest node: ", closest_node)

    if nmbr_of_nodes > 0 and course.robot_coords != None:
        if len(course.robot_coords) > 0:
            if closest_node != None:
                next_move = NextMove(
                    next_ball=pos[closest_node], move_type=course.ball_types[closest_node-1], extra_point=extra_points[closest_node-1])
                print("next_move: ", next_move.next_ball,
                      next_move.move_type, next_move.extra_point)
                return next_move
            else:

                if GOAL_SIDE_RELATIVE_TO_CAMERA == "left":
                    # IF CLOSE ENOUGH
                    if math.dist(course.robot_coords, LEFT_GOAL_POINT) < 0.15:

                        return NextMove(move_type="goal")

                    # lower left
                    if course.robot_coords[0] < COURSE_WIDTH / 2 and course.robot_coords[1] < COURSE_HEIGHT / 2:
                        return NextMove(move_type="none", next_ball=LEFT_GOAL_POINT)
                    # lower right
                    elif course.robot_coords[0] > COURSE_WIDTH / 2 and course.robot_coords[1] < COURSE_HEIGHT / 2:

                        # if close enough to BOT_RIGHT_ANCHOR
                        if math.dist(course.robot_coords, BOT_RIGHT_ANCHOR) > 0.15:
                            return NextMove(move_type="none", next_ball=BOT_RIGHT_ANCHOR)
                        else:
                            return NextMove(move_type="none", next_ball=BOT_LEFT_ANCHOR)
                    # upper left
                    elif course.robot_coords[0] < COURSE_WIDTH / 2 and course.robot_coords[1] > COURSE_HEIGHT / 2:
                        return NextMove(move_type="none", next_ball=LEFT_GOAL_POINT)
                    # upper right
                    elif course.robot_coords[0] > COURSE_WIDTH / 2 and course.robot_coords[1] > COURSE_HEIGHT / 2:

                        # if close enough to TOP_RIGHT_ANCHOR
                        if math.dist(course.robot_coords, TOP_RIGHT_ANCHOR) > 0.15:
                            return NextMove(move_type="none", next_ball=TOP_RIGHT_ANCHOR)
                        else:
                            return NextMove(move_type="none", next_ball=TOP_LEFT_ANCHOR)
                elif GOAL_SIDE_RELATIVE_TO_CAMERA == "right":

                    # IF CLOSE ENOUGH
                    if math.dist(course.robot_coords, RIGHT_GOAL_POINT) < 0.15:
                        print("close enough to goal!!!")
                        return NextMove(move_type="goal")

                    # lower left
                    if course.robot_coords[0] < COURSE_WIDTH / 2 and course.robot_coords[1] < COURSE_HEIGHT / 2:

                        # if close enough to BOT_LEFT_ANCHOR
                        if math.dist(course.robot_coords, BOT_LEFT_ANCHOR) > 0.15:
                            return NextMove(move_type="none", next_ball=BOT_LEFT_ANCHOR)
                        else:
                            return NextMove(move_type="none", next_ball=BOT_RIGHT_ANCHOR)

                    # lower right
                    elif course.robot_coords[0] > COURSE_WIDTH / 2 and course.robot_coords[1] < COURSE_HEIGHT / 2:
                        return NextMove(move_type="none", next_ball=RIGHT_GOAL_POINT)
                    # upper left
                    elif course.robot_coords[0] < COURSE_WIDTH / 2 and course.robot_coords[1] > COURSE_HEIGHT / 2:

                        # if close enough to TOP_LEFT_ANCHOR
                        if math.dist(course.robot_coords, TOP_LEFT_ANCHOR) > 0.15:
                            return NextMove(move_type="none", next_ball=TOP_LEFT_ANCHOR)
                        else:
                            return NextMove(move_type="none", next_ball=TOP_RIGHT_ANCHOR)

                    # upper right
                    elif course.robot_coords[0] > COURSE_WIDTH / 2 and course.robot_coords[1] > COURSE_HEIGHT / 2:
                        return NextMove(move_type="none", next_ball=RIGHT_GOAL_POINT)

        else:
            print("GOING TO Goal")
            return NextMove(move_type="goal")

        # if nx.is_connected(G) and len(G.edges) > 0:
        #     print("tsp: ", tsp[0])
        #     print("nextMove: nextnode =" , tsp[0][1], "move_type = ", move_types_in_order[0], "extra_point = ", extra_point_in_order[0])
        #     if move_types_in_order[0] == "middle_corner" or "middle_edge":
        #         return NextMove(next_ball=pos[tsp[0][1]], move_type=move_types_in_order[0], extra_point=extra_point_in_order[0])
        #     return NextMove(pos[tsp[0][1]], move_types_in_order[0])
        # elif len(G.edges) > 0:
        #     print("tsp: ", tsp[0])
        #     print("nextMove: nextnode =" , tsp[0][1], "move_type = ", move_types_in_order[0], "extra_point = ", extra_point_in_order[0])
        #     if move_types_in_order[0] == "middle_corner" or "middle_edge":
        #         return NextMove(next_ball=pos[tsp[0][1]], move_type=move_types_in_order[0], extra_point=extra_point_in_order[0])
        #     return NextMove(pos[tsp[0][1]], move_types_in_order[0])
        # else:
        #     print("Graph is not connected3")
        #     print(nx.is_connected(G))
        #     return NextMove(move_type="goal")
    else:

        return NextMove(move_type="goal")


def solve_tsp(G):

    # create dummy node
    G.add_node("dummy")
    G.add_edge("dummy", 0, weight=-10000)
    G.add_edge("dummy", G.number_of_nodes()-2, weight=-10000)
    # change the edge weight between start node and end node
    if G.has_edge(0, G.number_of_nodes()-2):
        G[0][G.number_of_nodes()-2]["weight"] = math.inf

    # Calculate the TSP
    A1 = nx.to_numpy_matrix(G)
    tsp = solve_tsp_dynamic_programming(A1)

    # remove dummy node
    G.remove_node("dummy")

    # remove the last node "dummy" from the path
    tsp[0].remove(G.number_of_nodes())

    if (tsp[0][0] == 0 and tsp[0][1] == 11):
        flipped_list = tsp[0][::-1]
        new_tsp = ([0] + flipped_list[:-1], tsp[1]+20000)
    else:
        new_tsp = (tsp[0], tsp[1] + 20000)

    # print("Fastest path: " + str(new_tsp[0]))
    # print("Fastest path length in meters: " + str(new_tsp[1]))

    return new_tsp


def print_graph_matrix(G):
    # save the graph in a file
    # Relabel the nodes with letters
    node_labels = {i: i for i in range(G.number_of_nodes())}
    G = nx.relabel_nodes(G, node_labels)

    # Calculate the adjacency matrix of the graph
    adj_matrix_sparse = nx.adjacency_matrix(G)
    adj_matrix = adj_matrix_sparse.toarray()

    # Print the adjacency matrix using pandas
    df = pd.DataFrame(adj_matrix, columns=node_labels.values(),
                      index=node_labels.values())
    # print(df)


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


def order_obstacles1(obstacle_coords):

    # Sort the coordinates based on x-coordinate (left to right)
    sorted_coords = sorted(obstacle_coords, key=lambda c: c[0])

    if (sorted_coords[0][1] > sorted_coords[2][1] and sorted_coords[1][1] > sorted_coords[3][1]):
        if (sorted_coords[0][1] > sorted_coords[1][1]):
            top_left, top_right = sorted_coords[0], sorted_coords[2]
            bottom_left, bottom_right = sorted_coords[1], sorted_coords[3]

        else:
            top_left, top_right = sorted_coords[0], sorted_coords[1]
            bottom_left, bottom_right = sorted_coords[2], sorted_coords[3]

    elif (sorted_coords[0][1] < sorted_coords[2][1] and sorted_coords[1][1] < sorted_coords[3][1]):
        if (sorted_coords[0][1] < sorted_coords[1][1]):
            bottom_left, bottom_right = sorted_coords[0], sorted_coords[1]
            top_left, top_right = sorted_coords[2], sorted_coords[3]

        else:
            if (sorted_coords[2][0]-sorted_coords[0][0] > 0.1):
                top_left, top_right = sorted_coords[2], sorted_coords[3]
                bottom_left, bottom_right = sorted_coords[0], sorted_coords[1]

            else:
                top_left, top_right = sorted_coords[0], sorted_coords[2]
                bottom_left, bottom_right = sorted_coords[1], sorted_coords[3]
                print("5")

    return [top_left, top_right, bottom_right, bottom_left]


def expand_obstacle(obstacle_coords, unit_vector, orthog_unit_vector):

    expanded_obstacle_coords = []

    expanded_obstacle_coords.append(obstacle_coords[0] + unit_vector * 0.1)
    expanded_obstacle_coords.append(obstacle_coords[1] - unit_vector * 0.1)
    expanded_obstacle_coords.append(
        obstacle_coords[2] + orthog_unit_vector * 0.1)
    expanded_obstacle_coords.append(
        obstacle_coords[3] - orthog_unit_vector * 0.1)


def find_closest_obs_corner(coords, obs):

    # Four coordinates
    coord1 = obs[0]
    coord2 = obs[1]
    coord3 = obs[2]
    coord4 = obs[3]

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


def find_closest_obs_edge(coords, obs1, obs2):

    # Combine coordinates of both polygons
    coordinates = obs1 + obs2

    # Target coordinate
    target = coords

    # Calculate distances
    distances = [
        math.sqrt((coord[0] - target[0]) ** 2 + (coord[1] - target[1]) ** 2)
        for coord in coordinates
    ]

    # Find the indices of the two closest coordinates
    closest_indices = sorted(range(len(distances)),
                             key=lambda i: distances[i])[:2]

    # Get the two closest coordinates
    closest_coordinates = [coordinates[i] for i in closest_indices]

    # Calculate the coordinate in the middle
    middle_coordinate = [
        sum(coord[0] for coord in closest_coordinates) / 2,
        sum(coord[1] for coord in closest_coordinates) / 2
    ]

    # print("Middle coordinate: ", middle_coordinate)

    return middle_coordinate


def move_away_from_obstacle(corner_coords, middle_coords, length_of_move):
    # Coordinate to be moved
    coordinate = corner_coords

    # Reference coordinate
    reference = middle_coords

    # Calculate the vector from the reference coordinate to the coordinate
    vector = [coordinate[0] - reference[0], coordinate[1] - reference[1]]

    # Calculate the magnitude of the vector
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2)

    # Scale the vector to have a magnitude of 1 centimeter
    scaled_vector = [(length_of_move / magnitude) * vector[0],
                     (length_of_move / magnitude) * vector[1]]

    # Move the coordinate 1 centimeter away from the reference coordinate
    new_coordinate = [reference[0] + scaled_vector[0],
                      reference[1] + scaled_vector[1]]

    return new_coordinate


def move_opposite(coord1, coord2, length):
    # Calculate the differences between coordinates
    # print("coord1, x: ", coord1[0])
    # print("coord1, y: ", coord1[1])
    # print("coord2, x: ", coord2[0])
    # print("coord2, y: ", coord2[1])
    dx = coord2[0] - coord1[0]
    dy = coord2[1] - coord1[1]

    # Calculate the negated differences
    opposite_dx = -dx
    opposite_dy = -dy

    # Calculate the new coordinate
    new_coord = (coord1[0] + opposite_dx * length,
                 coord1[1] + opposite_dy * length)

    return new_coord


def place_anchor_points(anchor_level, extra_points, course: Course, pos, G):

    if course.robot_coords is None or len(course.robot_coords) == 0:
        return extra_points, course, pos, G

    # remove and save last node from pos
    last_node = pos.pop(len(pos) - 1)
    # remove last type from course.ball_types
    last_type = course.ball_types.pop(len(course.ball_types) - 1)
    # remove last extra point from extra_points
    last_extra_point = extra_points.pop(len(extra_points) - 1)

    # lower left
    if course.robot_coords[0] < COURSE_WIDTH / 2 and course.robot_coords[1] < COURSE_HEIGHT / 2:
        if anchor_level == 0:
            pos[len(pos)] = (TOP_LEFT_ANCHOR)

        if anchor_level == 1:
            pos[len(pos)] = (TOP_RIGHT_ANCHOR)

        if anchor_level == 2:
            pos[len(pos)] = (BOT_RIGHT_ANCHOR)

        if anchor_level == 3:
            pos[len(pos)] = (BOT_LEFT_ANCHOR)

        G.add_node(len(pos))
        course.ball_coords.append(pos[len(pos)-1])
        course.ball_types.append("none")
        extra_points.append([0, 0])
    # lower right
    elif course.robot_coords[0] > COURSE_WIDTH / 2 and course.robot_coords[1] < COURSE_HEIGHT / 2:
        if anchor_level == 0:
            pos[len(pos)] = (BOT_LEFT_ANCHOR)

        if anchor_level == 1:
            pos[len(pos)] = (TOP_LEFT_ANCHOR)

        if anchor_level == 3:
            pos[len(pos)] = (TOP_RIGHT_ANCHOR)

        if anchor_level == 4:
            pos[len(pos)] = (BOT_RIGHT_ANCHOR)

        G.add_node(len(pos))
        course.ball_coords.append(pos[len(pos)-1])
        course.ball_types.append("none")
        extra_points.append([0, 0])
    # upper left
    elif course.robot_coords[0] < COURSE_WIDTH / 2 and course.robot_coords[1] > COURSE_HEIGHT / 2:
        if anchor_level == 0:
            pos[len(pos)] = (TOP_RIGHT_ANCHOR)

        if anchor_level == 1:
            pos[len(pos)] = (BOT_RIGHT_ANCHOR)

        if anchor_level == 2:
            pos[len(pos)] = (BOT_LEFT_ANCHOR)

        if anchor_level == 3:
            pos[len(pos)] = (TOP_LEFT_ANCHOR)

        G.add_node(len(pos))
        course.ball_coords.append(pos[len(pos)-1])
        course.ball_types.append("none")
        extra_points.append([0, 0])
    # upper right
    elif course.robot_coords[0] > COURSE_WIDTH / 2 and course.robot_coords[1] > COURSE_HEIGHT / 2:
        if anchor_level == 0:
            pos[len(pos)] = (BOT_RIGHT_ANCHOR)

        if anchor_level == 1:
            pos[len(pos)] = (BOT_LEFT_ANCHOR)

        if anchor_level == 2:
            pos[len(pos)] = (TOP_LEFT_ANCHOR)

        if anchor_level == 3:
            pos[len(pos)] = (TOP_RIGHT_ANCHOR)

        G.add_node(len(pos))
        course.ball_coords.append(pos[len(pos)-1])
        course.ball_types.append("none")
        extra_points.append([0, 0])

    # add last node back to pos
    pos[len(pos)] = (last_node)
    # add last type back to course.ball_types
    course.ball_types.append(last_type)
    # add last extra point back to extra_points
    extra_points.append(last_extra_point)

    return extra_points, course, pos, G
