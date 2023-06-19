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
from path_finder.obs_calculation import *

### GRAPH SETTINGS ###
# display settings
NODE_SIZE = 200
EDGE_WIDTH = 1
DISPLAY_HEIGHT = 3.5
DISPLAY_WIDTH = 6


def create_graph1(course: Course):

    robot_on_course = False

    # create graph
    G = nx.Graph()

    ### NODES ###
    # add nodes and give temp random coordinates
    G.add_nodes_from(range(0, len(course.ball_coords)))
    pos = nx.random_layout(G, dim=2, center=None)

    # check for and set robot coords
    if course.robot_coords is not None and len(course.robot_coords) != 0:
        robot_on_course = True
        G.add_node(0)
        pos[0] = (course.robot_coords[0], course.robot_coords[1])

    # set ball coordinates
    for i in range(len(course.ball_coords)):
        x = course.ball_coords[i][0]
        y = course.ball_coords[i][1]
        G.add_node(i+1)
        pos[i+1] = (x, y)

    ### OBSTACLES ###
    left_obs_coords = course.obstacle_coords[0]
    right_obs_coords = course.obstacle_coords[2]
    top_obs_coords = course.obstacle_coords[1]
    bottom_obs_coords = course.obstacle_coords[3]

    hor_obs_coords = create_box_from_obs_coords(
        left_obs_coords, right_obs_coords, OBSTACLE_WIDTH)
    vert_obs_coords = create_box_from_obs_coords(
        top_obs_coords, bottom_obs_coords, OBSTACLE_WIDTH)

    hor_obs_coords = order_obstacles(hor_obs_coords)
    vert_obs_coords = order_obstacles(vert_obs_coords)

    ### EXPANDED OBSTACLES ###
    middle_of_obstacle = midpoint(left_obs_coords, right_obs_coords)

    # expanded obs
    expanded_obs_coords = create_expanded_box(
        left_obs_coords, right_obs_coords, top_obs_coords, bottom_obs_coords, middle_of_obstacle)

    # extended sides
    hor_extended_obs_coords = create_extended_box(hor_obs_coords)
    vert_extended_obs_coords = create_extended_box(vert_obs_coords)

    # expanded walls
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

    ### REPOSITION NODES ###
    # dictionary of polygons
    polygons = {
        'hor_obs': Polygon(hor_obs_coords),
        'vert_obs': Polygon(vert_obs_coords),
        'expanded_obs': Polygon(expanded_obs_coords),
        'hor_extended_obs': Polygon(hor_extended_obs_coords),
        'vert_extended_obs': Polygon(vert_extended_obs_coords),
        'left_wall_expanded': Polygon(left_wall_expanded),
        'top_wall_expanded': Polygon(top_wall_expanded),
        'right_wall_expanded': Polygon(right_wall_expanded),
        'bottom_wall_expanded': Polygon(bottom_wall_expanded),
    }

    # reposition nodes
    course, pos = reposition_nodes(course, pos, polygons, middle_of_obstacle)

    ### EDGES ###
    # add edges
    G, pos, edge_weights = add_edges(G, pos, course, polygons)
    nx.set_edge_attributes(G, edge_weights, "weight")

    ### SHORTES PATH ###
    # add fake edges for all nodes not connected to each other
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            if not G.has_edge(i, j):
                G.add_edge(i, j, weight=math.inf)

    start_time = time.time()

    if len(pos) > 0:
        if nx.is_connected(G) and len(G.edges) > 0 and len(pos) > 2:
            tsp = solve_tsp(G)
        elif len(pos) == 2 and len(G.edges) > 0:
            tsp = [[0, 1], math.dist(pos[0], pos[1])]
        else:
            print("Graph is not connected")

    
    end_time = time.time()
    # print("nx.connected: ", nx.is_connected(G))
    # print(f"Algo took: {end_time - start_time} seconds to finish")
    # print("Ball_types: ", course.ball_types)
    # print("---------------------------------")


    # remove fake edges
    for edge in G.edges:
        if G[edge[0]][edge[1]]["weight"] == math.inf:
            G.remove_edge(edge[0], edge[1])
    

    ### DISPLAY ###

    # patches
    hor_obs_patch = PolygonPatch(hor_obs_coords, color='red', alpha=0.5)
    vert_obs_patch = PolygonPatch(vert_obs_coords, color='red', alpha=0.5)

    expanded_obs_patch = PolygonPatch(
        expanded_obs_coords, color='red', alpha=0.2)
    hor_extended_obs_patch = PolygonPatch(
        hor_extended_obs_coords, color='red', alpha=0.2)
    vert_extended_obs_patch = PolygonPatch(
        vert_extended_obs_coords, color='red', alpha=0.2)

    left_wall_expanded_patch = PolygonPatch(
        left_wall_expanded, color='red', alpha=0.2)
    top_wall_expanded_patch = PolygonPatch(
        top_wall_expanded, color='red', alpha=0.2)
    right_wall_expanded_patch = PolygonPatch(
        right_wall_expanded, color='red', alpha=0.2)
    bottom_wall_expanded_patch = PolygonPatch(
        bottom_wall_expanded, color='red', alpha=0.2)

    # patches list
    patches = [hor_obs_patch, vert_obs_patch, expanded_obs_patch, hor_extended_obs_patch, vert_extended_obs_patch,
               left_wall_expanded_patch, top_wall_expanded_patch, right_wall_expanded_patch, bottom_wall_expanded_patch]

    show_display(G, pos, tsp, edge_weights, patches)

    ### RETURN ###
    move_types_in_order = []
    extra_point_in_order = []

    if nx.is_connected(G) and len(G.edges) > 0:
        for i in range(len(tsp[0])):
            for j in range(len(course.ball_coords)):
                if pos[tsp[0][i]][0] == course.ball_coords[j][0]:
                    move_types_in_order.append(course.ball_types[j])
                    extra_point_in_order.append(extra_points[j])

    if len(pos) > 0:
        if nx.is_connected(G) and len(G.edges) > 0:
            if move_types_in_order[0] == "middle_corner" or "middle_edge":
                # TODO: add to NextMove: extra_point=extra_points[0]
                return NextMove(next_ball=pos[tsp[0][1]], move_type=move_types_in_order[0])
            return NextMove(pos[tsp[0][1]], move_types_in_order[0])
        else:
            print("Graph is not connected")
            return NextMove(move_type="goal")


def show_display(G, pos, tsp, edge_weights, patches=None):
    ### DISPLAY ###
    # display size
    plt.figure(figsize=(DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=NODE_SIZE)

    # draw edges
    nx.draw_networkx_edges(G, pos, width=EDGE_WIDTH)
    if len(pos) > 0:
        if nx.is_connected(G) and len(G.edges) > 0:
            nx.draw_networkx_edges(G, pos, edgelist=list(
                zip(tsp[0], tsp[0][1:])), width=EDGE_WIDTH, edge_color='r')
        elif len(G.edges) == 1 and len(G.nodes) == 2:
            # TODO: Add visual edge?
            print("Graph has 1 ball left and is connected")


    # add node labels
    nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif")

    # add edge weight labels
    edge_labels = {k: "{:.2f}".format(v) for k, v in edge_weights.items()}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=6, label_pos=0.5, bbox=dict(boxstyle="round", fc="w", ec="1", alpha=0.9, pad=0.1))


    # add patches
    if patches is not None:
        for patch in patches:
            plt.gca().add_patch(patch)

    # axis settings
    ax = plt.gca()
    # set the axis limits
    ax.set_xlim(0, COURSE_WIDTH)
    ax.set_ylim(0, COURSE_HEIGHT)
    # showing the axis numbers
    ax.tick_params(left=True, bottom=True, labelleft=True,
                   labelbottom=True)
    # margin between the nodes and the axis
    ax.margins(0.08)

    # show graph
    plt.axis("on")
    plt.tight_layout()
    plt.show()

def reposition_nodes(course: Course, pos, polygons: dict, middle_of_obstacle):

    corner_extra_distance = 0.05
    edge_extra_distance = 0.05

    wall_extra_distance = 0.02

    

    extra_points = []

    for i in range(len(course.ball_coords)):

        if polygons.get('hor_extended_obs').contains(Point(pos[i+1])) or polygons.get('vert_extended_obs').contains(Point(pos[i+1])):
            
            pos[i+1] = find_closest_obs_edge(pos[i+1], polygons.get('hor_extended_obs'), polygons.get('vert_extended_obs'))
            pos[i+1] = move_towards(pos[i+1], middle_of_obstacle, -edge_extra_distance)

            course.ball_coords[i] = pos[i+1]
            course.ball_types[i] = 'middle_edge'

            extra_points.append(None)

        elif polygons.get('expanded_obs').contains(Point(pos[i+1])):

            pos[i+1] = find_closest_obs_corner(pos[i+1], polygons.get('expanded_obs'))
            pos[i+1] = move_towards(pos[i+1], middle_of_obstacle, -corner_extra_distance)

            course.ball_coords[i] = pos[i+1]
            course.ball_types[i] = 'middle_corner'

            extra_points.append(None)
        elif course.ball_types[i] == 'none':
            extra_points.append(None)

        elif course.ball_types[i] != 'none':
            extra_points.append(None)
            if course.ball_types[i] == "lower_left_corner":
                pos[i+1] = [HALF_ROBOT_LENGTH +
                            wall_extra_distance, HALF_ROBOT_LENGTH+wall_extra_distance]
                course.ball_coords[i] = pos[i+1]
            elif course.ball_types[i] == "lower_right_corner":
                pos[i+1] = [COURSE_WIDTH -
                            HALF_ROBOT_LENGTH-wall_extra_distance, HALF_ROBOT_LENGTH+wall_extra_distance]
                course.ball_coords[i] = pos[i+1]
            elif course.ball_types[i] == "upper_left_corner":
                pos[i+1] = [HALF_ROBOT_LENGTH+wall_extra_distance,
                            COURSE_HEIGHT - HALF_ROBOT_LENGTH-wall_extra_distance]
                course.ball_coords[i] = pos[i+1]
            elif course.ball_types[i] == "upper_right_corner":
                pos[i+1] = [COURSE_WIDTH - HALF_ROBOT_LENGTH-wall_extra_distance,
                            COURSE_HEIGHT - HALF_ROBOT_LENGTH-wall_extra_distance]
                course.ball_coords[i] = pos[i+1]
            elif course.ball_types[i] == "left_edge":
                pos[i+1] = [HALF_ROBOT_LENGTH +
                            wall_extra_distance, pos[i+1][1]]
                course.ball_coords[i] = pos[i+1]
            elif course.ball_types[i] == "right_edge":
                pos[i+1] = [COURSE_WIDTH -
                            HALF_ROBOT_LENGTH-wall_extra_distance, pos[i+1][1]]
                course.ball_coords[i] = pos[i+1]
            elif course.ball_types[i] == "lower_edge":
                pos[i+1] = [pos[i+1][0],
                            HALF_ROBOT_LENGTH+wall_extra_distance]
                course.ball_coords[i] = pos[i+1]
            elif course.ball_types[i] == "upper_edge":
                pos[i+1] = [pos[i+1][0], COURSE_HEIGHT -
                            HALF_ROBOT_LENGTH-wall_extra_distance]
                course.ball_coords[i] = pos[i+1]
    
    return course, pos

def add_edges(G, pos, course: Course, polygons: dict):
    anchor_level = 0

    while not nx.is_connected(G) and len(pos) > 1 and anchor_level < 3:


        G.remove_edges_from(list(G.edges()))
        edge_weights = {}

        if anchor_level > 0:
            pos, G = place_anchor_points(anchor_level, course, pos, G)
        
        anchor_level += 1

        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                if G.has_node(i) and G.has_node(j):
                    # check if edge intersects with obstacle
                    edge_coords = LineString([pos[i], pos[j]])
                    if all(not edge_coords.intersects(poly) for poly in polygons.values()):
                        dist = math.sqrt((pos[i][0] - pos[j][0])
                                        ** 2 + (pos[i][1] - pos[j][1]) ** 2)
                        G.add_edge(i, j, weight=dist)
                        edge_weights[(i, j)] = dist

    # TODO: Is nx connected when only 2 nodes?

    return G, pos, edge_weights


def place_anchor_points(anchor_level, course: Course, pos, G):

    if course.robot_coords is None or len(course.robot_coords) == 0:
        return pos, G

    # remove and save last node from pos
    last_node = pos.pop(len(pos) - 1)

    # lower left
    if course.robot_coords[0] < COURSE_WIDTH / 2 and course.robot_coords[1] < COURSE_HEIGHT / 2:
        if anchor_level == 0:
            pos[len(pos)] = (TOP_LEFT_ANCHOR)
            G.add_node(len(pos))
            pos[len(pos)] = (BOT_RIGHT_ANCHOR)
            G.add_node(len(pos))
        if anchor_level == 1:
            pos[len(pos)] = (TOP_RIGHT_ANCHOR)
            G.add_node(len(pos))
        if anchor_level == 2:
            pos[len(pos)] = (BOT_LEFT_ANCHOR)
            G.add_node(len(pos))
    # lower right
    elif course.robot_coords[0] > COURSE_WIDTH / 2 and course.robot_coords[1] < COURSE_HEIGHT / 2:
        if anchor_level == 0:
            pos[len(pos)] = (TOP_RIGHT_ANCHOR)
            G.add_node(len(pos))
            pos[len(pos)] = (BOT_LEFT_ANCHOR)
            G.add_node(len(pos))
        if anchor_level == 1:
            pos[len(pos)] = (TOP_LEFT_ANCHOR)
            G.add_node(len(pos))
        if anchor_level == 2:
            pos[len(pos)] = (BOT_RIGHT_ANCHOR)
            G.add_node(len(pos))
    # upper left
    elif course.robot_coords[0] < COURSE_WIDTH / 2 and course.robot_coords[1] > COURSE_HEIGHT / 2:
        if anchor_level == 0:
            pos[len(pos)] = (BOT_LEFT_ANCHOR)
            G.add_node(len(pos))
            pos[len(pos)] = (TOP_RIGHT_ANCHOR)
            G.add_node(len(pos))
        if anchor_level == 1:
            pos[len(pos)] = (BOT_RIGHT_ANCHOR)
            G.add_node(len(pos))
        if anchor_level == 2:
            pos[len(pos)] = (TOP_LEFT_ANCHOR)
            G.add_node(len(pos))
    # upper right
    elif course.robot_coords[0] > COURSE_WIDTH / 2 and course.robot_coords[1] > COURSE_HEIGHT / 2:
        if anchor_level == 0:
            pos[len(pos)] = (BOT_RIGHT_ANCHOR)
            G.add_node(len(pos))
            pos[len(pos)] = (TOP_LEFT_ANCHOR)
            G.add_node(len(pos))
        if anchor_level == 1:
            pos[len(pos)] = (BOT_LEFT_ANCHOR)
            G.add_node(len(pos))
        if anchor_level == 2:
            pos[len(pos)] = (TOP_RIGHT_ANCHOR)
            G.add_node(len(pos))

    # add last node back to pos
    pos[len(pos)] = (last_node)

    return pos, G


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

    return new_tsp
