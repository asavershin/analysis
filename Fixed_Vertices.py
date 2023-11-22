import csv
import gc

import networkx as nx
import time
import random
import numpy as np


def generate_weighted_graph(num_vertices, num_edges):
    G = nx.Graph()
    G.add_nodes_from(range(num_vertices))

    if num_edges < num_vertices - 1:
        raise ValueError("The graph must be connected. The number of edges should be at least num_vertices - 1.")

    # Соединяем вершины, чтобы граф был связным
    for i in range(1, num_vertices):
        edge = (i - 1, i)
        weight = random.randint(1, 10)
        G.add_edge(*edge, weight=weight)
        num_edges -= 1

    # Добавляем оставшиеся ребра случайным образом
    while num_edges > 0:
        nodes_list = list(G.nodes())
        edge = random.sample(nodes_list, 2)
        if not G.has_edge(*edge):
            weight = random.randint(1, 10)
            G.add_edge(*edge, weight=weight)
            num_edges -= 1

    return G


min_vertices = 50
max_vertices = 800
repetitions = 100
current_vertices = min_vertices
with open('results.csv', mode='w', newline='') as file:
    fieldnames = ['Vertices', 'Edges', 'AverageTime']
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()

    while current_vertices <= max_vertices:
        max_edges = current_vertices * (current_vertices - 1) // 2
        step_edges = (max_edges - current_vertices) // 10

        num_iterations = min(10, (max_edges - current_vertices) // step_edges)

        for i in range(num_iterations):
            num_edges = current_vertices + i * step_edges

            execution_times = []
            for _ in range(repetitions):
                gc.collect()
                graph = generate_weighted_graph(current_vertices, num_edges)

                start_time = time.time_ns()
                nx.minimum_spanning_tree(graph, algorithm="prim")
                end_time = time.time_ns()

                execution_time = (end_time - start_time)
                execution_times.append(execution_time)

            execution_times.sort()
            quantile_20 = int(0.20 * repetitions)
            quantile_80 = int(0.80 * repetitions)
            selected_times = execution_times[quantile_20:quantile_80]
            average_time = np.mean(selected_times)

            print(f"Vertices: {current_vertices}, Edges: {num_edges}, Average Execution Time: {average_time} ns")
            writer.writerow({'Vertices': current_vertices, 'Edges': num_edges, 'AverageTime': average_time})

        current_vertices *= 2