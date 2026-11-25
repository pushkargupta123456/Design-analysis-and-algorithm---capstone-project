"""
Travelling Salesman Problem (TSP) — Nearest Neighbour Heuristic.

Given a depot and a set of delivery nodes, finds an approximate shortest route
that starts at the depot, visits every delivery node exactly once, and returns
to the depot.

Algorithm: Nearest Neighbour Greedy Heuristic
  1. Start at the depot.
  2. Repeatedly visit the closest unvisited delivery node.
  3. After all delivery nodes are visited, return to the depot.

This is a greedy approximation. It runs in O(n²) time and typically produces
routes within 20-25% of the optimal solution.

Complexity:
  nearest_neighbor_tsp  : O(n²) where n = number of delivery nodes
  build_distance_matrix : O(V * (V + E) log V) — runs Dijkstra from each node
"""

import math
import time

from algorithms.dijkstra import all_pairs_shortest_paths


def nearest_neighbor_tsp(arg1, arg2, arg3=None):
    """
    Solve the TSP using the Nearest Neighbour greedy heuristic.

    Starting from start_node (depot), always travel to the closest unvisited
    delivery node. After visiting all delivery nodes, return to the depot.

    Supports both signatures:
      nearest_neighbor_tsp(distance_matrix, nodes, start_node)
      nearest_neighbor_tsp(start_node, nodes, distance_matrix)
    """
    if isinstance(arg1, dict):
        distance_matrix, nodes, start_node = arg1, arg2, arg3
    elif isinstance(arg3, dict):
        start_node, nodes, distance_matrix = arg1, arg2, arg3
    elif isinstance(arg2, dict):
        nodes, distance_matrix, start_node = arg1, arg2, arg3
    else:
        distance_matrix, nodes, start_node = arg1, arg2, arg3

    # Exclude start_node from unvisited delivery destinations
    unvisited = [n for n in (nodes or []) if n != start_node]

    if not unvisited:
        return {
            "route": [start_node, start_node],
            "total_distance": 0.0,
            "segment_distances": [0.0],
            "feasible": True,
            "unreachable_nodes": [],
        }

    route = [start_node]
    segment_distances = []
    total_distance = 0.0
    unreachable_nodes = []
    current = start_node

    while unvisited:
        # Find nearest unvisited node from current position
        best_node = None
        best_dist = math.inf

        for candidate in unvisited:
            d = distance_matrix.get(current, {}).get(candidate, math.inf)
            if isinstance(d, dict):
                d = d.get("distance", math.inf)
            if d < best_dist:
                best_dist = d
                best_node = candidate

        if best_node is None or best_dist == math.inf:
            # All remaining nodes are unreachable from current position
            unreachable_nodes.extend(unvisited)
            break

        # Travel to best_node
        segment_distances.append(best_dist)
        total_distance += best_dist
        route.append(best_node)
        current = best_node
        unvisited.remove(best_node)

    # Return to depot
    return_dist = distance_matrix.get(current, {}).get(start_node, math.inf)
    if isinstance(return_dist, dict):
        return_dist = return_dist.get("distance", math.inf)
    if return_dist == math.inf:
        # Cannot return — mark infeasible but append inf
        unreachable_nodes.append(f"{current} -> {start_node} (return)")
        segment_distances.append(math.inf)
        total_distance = math.inf
    else:
        segment_distances.append(return_dist)
        if total_distance != math.inf:
            total_distance += return_dist

    route.append(start_node)

    feasible = (len(unreachable_nodes) == 0) and (total_distance < math.inf)

    return {
        "route": route,
        "total_distance": total_distance,
        "segment_distances": segment_distances,
        "feasible": feasible,
        "unreachable_nodes": unreachable_nodes,
    }


def build_distance_matrix(arg1, arg2, depot=None):
    """
    Build a full distance matrix between the depot and all delivery nodes.

    Supports:
      build_distance_matrix(graph, delivery_nodes, depot)
      build_distance_matrix(nodes, all_pairs)
    """
    if depot is not None:
        graph, delivery_nodes = arg1, arg2
        all_nodes = list(dict.fromkeys([depot] + delivery_nodes))
        pairs = all_pairs_shortest_paths(graph, all_nodes)

        distance_matrix = {}
        for u in all_nodes:
            distance_matrix[u] = {}
            for v in all_nodes:
                info = pairs.get(u, {}).get(v, {})
                d = info.get("distance", math.inf) if isinstance(info, dict) else info
                distance_matrix[u][v] = d
        return distance_matrix
    else:
        if isinstance(arg1, list) and isinstance(arg2, dict):
            nodes, all_pairs = arg1, arg2
        elif isinstance(arg1, dict) and isinstance(arg2, list):
            all_pairs, nodes = arg1, arg2
        else:
            nodes, all_pairs = arg1, arg2

        matrix = {}
        for u in nodes:
            matrix[u] = {}
            for v in nodes:
                val = all_pairs.get(u, {}).get(v, math.inf)
                if isinstance(val, dict):
                    matrix[u][v] = val.get("distance", math.inf)
                else:
                    matrix[u][v] = val
        return matrix


def timed_tsp(arg1, arg2, arg3=None):
    """
    Run nearest_neighbor_tsp and measure wall-clock execution time.
    """
    t0 = time.perf_counter()
    result = nearest_neighbor_tsp(arg1, arg2, arg3)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return result, elapsed_ms
