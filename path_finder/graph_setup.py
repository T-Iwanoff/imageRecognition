import time
import matplotlib.pyplot as plt
import networkx as nx
import random
import math
import numpy as np
import pandas as pd
from python_tsp.exact import solve_tsp_dynamic_programming
from shapely.geometry import LineString, box
from course import Course
from constants import *


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
        pos[0] = (course.robot_coords[0], course.robot_coords[1])

    for i in range(nmbr_of_nodes-1):
        x = course.ball_coords[i][0]
        y = course.ball_coords[i][1]
        G.add_node(i+1)
        pos[i+1] = (x, y)

    

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

        horizontal_obstacle_vector = [left_obstacle[0] -
                                      right_obstacle[0],
                                      left_obstacle[1] -
                                      right_obstacle[1]]
        vertical_obstacle_vector = [top_obstacle[0] -
                                    bottom_obstacle[0],
                                    top_obstacle[1] -
                                    bottom_obstacle[1]]

        horizontal_obstacle_vector_crossvector = [-horizontal_obstacle_vector[1], horizontal_obstacle_vector[0]]
        vertical_obstacle_vector_crossvector = [-vertical_obstacle_vector[1], vertical_obstacle_vector[0]]
        
        horizontal_wall_length_vector=[horizontal_obstacle_vector_crossvector[0]*0.075,horizontal_obstacle_vector_crossvector[1]*0.075]
        vertical_wall_length_vector=[vertical_obstacle_vector_crossvector[0]*0.075,vertical_obstacle_vector_crossvector[1]*0.075]
        
    ##TODO: Shapes instead of boxes

    if left_obstacle is not None:
        obstacle_1 = box(minx=left_obstacle[0]+horizontal_wall_length_vector[0], miny=left_obstacle[1]+horizontal_wall_length_vector[1],
                         maxx=right_obstacle[0]-horizontal_wall_length_vector[0], maxy=right_obstacle[1]-horizontal_wall_length_vector[1])

        obstacle_2 = box(minx=bottom_obstacle[0]+vertical_wall_length_vector[0], miny=bottom_obstacle[1]+vertical_wall_length_vector[1],
                         maxx=top_obstacle[0]-vertical_wall_length_vector[0], maxy=top_obstacle[1]-vertical_wall_length_vector[1])
        # obstacle_1 = box(minx=left_obstacle[0], miny=left_obstacle[1] - 0.015,
        #                  maxx=right_obstacle[0], maxy=right_obstacle[1] + 0.015)

        # obstacle_2 = box(minx=bottom_obstacle[0] - 0.015, miny=bottom_obstacle[1],
        #                  maxx=top_obstacle[0] + 0.015, maxy=top_obstacle[1])

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
                        if not edge_coords.intersects(obstacle_1) and not edge_coords.intersects(obstacle_2):
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
    nx.draw_networkx_nodes(G, pos, node_size=NODE_SIZE)

    # edges
    nx.draw_networkx_edges(G, pos, width=EDGE_WIDTH)
    if nmbr_of_nodes > 0:
        if nx.is_connected(G) and len(G.edges) > 0:
            nx.draw_networkx_edges(G, pos, edgelist=list(
                zip(tsp[0], tsp[0][1:])), width=EDGE_WIDTH, edge_color='r')
        elif len(G.edges) == 1 and len(G.nodes) == 2:
            ##TODO: Add visual edge?
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
        obstacle_patches = [plt.Rectangle((obstacle.bounds[0], obstacle.bounds[1]),
                                          obstacle.bounds[2] -
                                          obstacle.bounds[0],
                                          obstacle.bounds[3] -
                                          obstacle.bounds[1],
                                          fill=True, color="red", alpha=0.5) for obstacle in [obstacle_1, obstacle_2]]

        for patch in obstacle_patches:
            ax.add_patch(patch)

    # print the graph matrix
    # printGraphMatrix(G)

    # display the graph
    ax.tick_params(left=True, bottom=True, labelleft=True,
                   labelbottom=True)  # showing the axis numbers
    ax.margins(0.08)  # margin between the nodes and the axis
    plt.axis("on")
    plt.tight_layout()
    plt.show()

    # if nmbr_of_nodes > 0: return coords of first node in tsp
    if nmbr_of_nodes > 0:
        if nx.is_connected(G) and len(G.edges) > 0:
            return pos[tsp[0][1]]
        else:
            return None


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


# def calculateTSP(G):

#     # create dummy node
#     # G.add_node("dummy")
#     # G.add_edge("dummy", 0, weight=0)
#     # G.add_edge("dummy", G.number_of_nodes()-2, weight=0)

#     # Calculate the TSP
#     temp_tsp = nx.algorithms.approximation.traveling_salesman_problem(
#         G, weight="weight", cycle=False)

#     tsp_weight = 0

#     # Calculate the total weight of the TSP path
#     for i in range(len(temp_tsp) - 1):
#         tsp_weight += G[temp_tsp[i]][temp_tsp[i+1]]["weight"]

#     # Print the TSP and its weight
#     print("TSP path:", temp_tsp)
#     print("TSP weight:", tsp_weight)

#     return temp_tsp


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
