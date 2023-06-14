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

    ### GRAPH CREATION ###
    G = nx.Graph()

    ### NODES ###

    # add nodes
    G.add_nodes_from(range(nmbr_of_nodes))

    pos = nx.random_layout(G, dim=2, center=None)
    # add nodes at ball coords

    if course.robot_coords is not None:
        print("adding robot node")
        G.add_node(0)
        if len(course.robot_coords) != 0:
            pos[0] = (course.robot_coords[0], course.robot_coords[1])

    for i in range(nmbr_of_nodes-1):
        x = course.ball_coords[i][0]
        y = course.ball_coords[i][1]
        G.add_node(i+1)
        pos[i+1] = (x, y)

    print("")
    print("")
    print("ball coords: ", course.ball_coords)
    print("pos: ", pos)

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

        # Obstacle length vector
        hor_obs_length_vector = [
            hor_obs_orthog_unit_vector[0]*OBSTACLE_WIDTH, hor_obs_orthog_unit_vector[1]*OBSTACLE_WIDTH]
        vert_obs_length_vector = [
            vert_obs_orthog_unit_vector[0]*OBSTACLE_WIDTH, vert_obs_orthog_unit_vector[1]*OBSTACLE_WIDTH]

        # Obstacle coords
        hor_obs_coords = [
            [left_obstacle[0] + hor_obs_length_vector[0],
                left_obstacle[1] + hor_obs_length_vector[1]],
            [right_obstacle[0]-hor_obs_length_vector[0],
                right_obstacle[1]-hor_obs_length_vector[1]],
            [left_obstacle[0]-hor_obs_length_vector[0],
                left_obstacle[1]-hor_obs_length_vector[1]],
            [right_obstacle[0]+hor_obs_length_vector[0],
                right_obstacle[1]+hor_obs_length_vector[1]]]

        vert_obs_coords = [
            [top_obstacle[0]+vert_obs_length_vector[0],
                top_obstacle[1]+vert_obs_length_vector[1]],
            [bottom_obstacle[0]-vert_obs_length_vector[0],
                bottom_obstacle[1]-vert_obs_length_vector[1]],
            [top_obstacle[0]-vert_obs_length_vector[0],
                top_obstacle[1]-vert_obs_length_vector[1]],
            [bottom_obstacle[0]+vert_obs_length_vector[0],
                bottom_obstacle[1]+vert_obs_length_vector[1]]]

        # Order obstacles coords
        hor_obs_coords = order_obstacles(hor_obs_coords)
        vert_obs_coords = order_obstacles(vert_obs_coords)

        # Create expanded obstacles
        middle_of_obstacle = [
            left_obstacle[0] - hor_obs_vector[0]/2], [left_obstacle[1] - hor_obs_vector[1]/2]
        print("middle_of_obstacle: ", middle_of_obstacle)

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
        # obs_expanded_lengths1 = []

        # Create expanded walls
        top_left_wall_expanded_point = [
            HALF_OF_ROBOT_WIDTH, COURSE_HEIGHT-HALF_OF_ROBOT_WIDTH,
        ]
        top_right_wall_expanded_point = [
            COURSE_WIDTH-HALF_OF_ROBOT_WIDTH, COURSE_HEIGHT-HALF_OF_ROBOT_WIDTH,
        ]
        bottom_left_wall_expanded_point = [
            HALF_OF_ROBOT_WIDTH, HALF_OF_ROBOT_WIDTH,
        ]
        bottom_right_wall_expanded_point = [
            COURSE_WIDTH-HALF_OF_ROBOT_WIDTH, HALF_OF_ROBOT_WIDTH,
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
        # walls expanded
        left_wall_expanded_poly = Polygon(left_wall_expanded)
        top_wall_expanded_poly = Polygon(top_wall_expanded)
        right_wall_expanded_poly = Polygon(right_wall_expanded)
        bottom_wall_expanded_poly = Polygon(bottom_wall_expanded)

    ### REPOSITION NODES ###
    short_extra_distance = 0.01
    # Reposition nodes if they intersect with obstacles
    if left_obstacle is not None:
        for i in range(nmbr_of_nodes-1):
            if course.ball_types[i] != "none":
                # If inside obs_expanded_corners_poly
                if obs_expanded_corners_poly.contains(Point(pos[i+1])):
                    print("pos[i]: ", pos[i+1])
                    pos[i + 1] = find_closest_corner(pos[i+1], obs_expanded_corners)
                    print("pos[i] after: ", pos[i+1])
                    pos[i + 1] = np.squeeze(move_away_from_obstacle(pos[i+1],
                                                                    middle_of_obstacle))
                    print("pos[i] after after: ", pos[i+1])
                    course.ball_coords[i] = pos[i+1]

                elif course.ball_types[i] == "lower_left_corner":
                    pos[i+1] = [HALF_OF_ROBOT_WIDTH +
                                short_extra_distance, HALF_OF_ROBOT_WIDTH+short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "lower_right_corner":
                    pos[i+1] = [COURSE_WIDTH -
                                HALF_OF_ROBOT_WIDTH-short_extra_distance, HALF_OF_ROBOT_WIDTH+short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "upper_left_corner":
                    pos[i+1] = [HALF_OF_ROBOT_WIDTH+short_extra_distance,
                                COURSE_HEIGHT - HALF_OF_ROBOT_WIDTH-short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "upper_right_corner":
                    pos[i+1] = [COURSE_WIDTH - HALF_OF_ROBOT_WIDTH-short_extra_distance,
                                COURSE_HEIGHT - HALF_OF_ROBOT_WIDTH-short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "left_edge":
                    pos[i+1] = [HALF_OF_ROBOT_WIDTH +
                                short_extra_distance, pos[i+1][1]]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "right_edge":
                    pos[i+1] = [COURSE_WIDTH -
                                HALF_OF_ROBOT_WIDTH-short_extra_distance, pos[i+1][1]]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "lower_edge":
                    pos[i+1] = [pos[i+1][0],
                                HALF_OF_ROBOT_WIDTH+short_extra_distance]
                    course.ball_coords[i] = pos[i+1]
                elif course.ball_types[i] == "upper_edge":
                    pos[i+1] = [pos[i+1][0], COURSE_HEIGHT -
                                HALF_OF_ROBOT_WIDTH-short_extra_distance]
                    course.ball_coords[i] = pos[i+1]

    ### EDGES ###
    edge_weights = {}
    # Add edges not intersecting with obstacles
    if left_obstacle is not None:
        # If not last ball left
        # if nmbr_of_nodes > 1:
        for i in range(nmbr_of_nodes):
            for j in range(i + 1, nmbr_of_nodes):
                if G.has_node(i) and G.has_node(j):
                    edge_coords = LineString([pos[i], pos[j]])
                    if not edge_coords.intersects(hor_obs_poly) and not edge_coords.intersects(vert_obs_poly) and not edge_coords.intersects(obs_expanded_corners_poly) and not edge_coords.intersects(left_wall_expanded_poly) and not edge_coords.intersects(top_wall_expanded_poly) and not edge_coords.intersects(right_wall_expanded_poly) and not edge_coords.intersects(bottom_wall_expanded_poly):
                        dist = math.sqrt((pos[i][0] - pos[j][0])
                                         ** 2 + (pos[i][1] - pos[j][1]) ** 2)
                        G.add_edge(i, j, weight=dist)
                        edge_weights[(i, j)] = dist
                    else:
                        # fake edge weight for algorithm
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
    nx.set_edge_attributes(G, edge_weights, "weight")

    ### SHORTEST PATH ###
    start_time = time.time()

    if nmbr_of_nodes > 0:
        if nx.is_connected(G) and len(G.edges) > 0 and nmbr_of_nodes > 2:
            tsp = solve_tsp(G)
        elif nmbr_of_nodes == 2 and len(G.edges) > 0:
            tsp = [[0, 1], math.dist(pos[0], pos[1])]
        else:
            print("Graph is not connected")

    #
    end_time = time.time()
    print(f"Algo took: {end_time - start_time} seconds to finish")

    # remove fake edges
    for edge in G.edges:
        if G[edge[0]][edge[1]]["weight"] == math.inf:
            G.remove_edge(edge[0], edge[1])

    ### GRAPH DISPLAY ###
    plt.figure(figsize=(DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # nodes
    print(pos)
    nx.draw_networkx_nodes(G, pos, node_size=NODE_SIZE)

    # edges
    nx.draw_networkx_edges(G, pos, width=EDGE_WIDTH)
    if nmbr_of_nodes > 0:
        if nx.is_connected(G) and len(G.edges) > 0:
            nx.draw_networkx_edges(G, pos, edgelist=list(
                zip(tsp[0], tsp[0][1:])), width=EDGE_WIDTH, edge_color='r')
        elif len(G.edges) == 1 and len(G.nodes) == 2:
            # TODO: Add visual edge?
            print("Graph has 1 ball left and is connected")

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

    if nx.is_connected(G) and len(G.edges) > 0:
        for i in range(len(tsp[0])):
            for j in range(len(course.ball_coords)):
                if pos[tsp[0][i]][0] == course.ball_coords[j][0]:
                    move_types_in_order.append(course.ball_types[j])

    print("pos: ", pos)
    print("course.ball_coords: ", course.ball_coords)

    print("move_types_in_order: " , move_types_in_order)

    # if nmbr_of_nodes > 0: return coords of first node in tsp
    if nmbr_of_nodes > 0:
        if nx.is_connected(G) and len(G.edges) > 0:
            return NextMove(pos[tsp[0][1]], move_types_in_order[0])
        else:
            print("Graph is not connected")
            return NextMove(move_type = "goal")


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

    print("Fastest path: " + str(new_tsp[0]))
    print("Fastest path length in meters: " + str(new_tsp[1]))

    # print(tsp)

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
    print(df)


def order_obstacles(obstacle_coords):

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
            bottom_left, bottom_right = sorted_coords[0], sorted_coords[2]
            top_left, top_right = sorted_coords[1], sorted_coords[3]
        else:
            bottom_left, bottom_right = sorted_coords[0], sorted_coords[1]
            top_left, top_right = sorted_coords[2], sorted_coords[3]

    return [top_left, top_right, bottom_right, bottom_left]


def expand_obstacle(obstacle_coords, unit_vector, orthog_unit_vector):

    expanded_obstacle_coords = []

    expanded_obstacle_coords.append(obstacle_coords[0] + unit_vector * 0.1)
    expanded_obstacle_coords.append(obstacle_coords[1] - unit_vector * 0.1)
    expanded_obstacle_coords.append(
        obstacle_coords[2] + orthog_unit_vector * 0.1)
    expanded_obstacle_coords.append(
        obstacle_coords[3] - orthog_unit_vector * 0.1)


def find_closest_corner(coords, obs_expanded_corners):

    # Four coordinates
    coord1 = obs_expanded_corners[0]
    coord2 = obs_expanded_corners[1]
    coord3 = obs_expanded_corners[2]
    coord4 = obs_expanded_corners[3]

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


def move_away_from_obstacle(corner_coords, middle_coords):
    # Coordinate to be moved
    coordinate = corner_coords

    # Reference coordinate
    reference = middle_coords

    # Length of move
    length_of_move = 0.2

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
