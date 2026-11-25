"""
Dijkstra's Shortest Path Algorithm for Smart Courier Route Optimisation.

Finds the shortest (minimum-distance) path from a source node to all other
nodes in a weighted, directed graph using a min-heap (priority queue).

Algorithm Overview:
  1. Initialise distances to all nodes as infinity; source distance = 0.
  2. Push (0, source) onto a min-heap.
  3. Pop the node with the smallest tentative distance.
  4. For each neighbour, if a shorter path is found, update and push to heap.
  5. Repeat until the heap is empty.

Complexity:
  Time  : O((V + E) log V)  with a binary heap (heapq)
  Space : O(V + E)
  where V = number of vertices (nodes), E = number of edges.

Limitation: Does NOT support negative edge weights (raises ValueError).
"""

import heapq
import math
import time


class PathInfo(dict):
    """
    A dictionary containing path, distance, and reachable fields.
    Also compares directly equal to a number (distance) for convenience in assertions.
    """
    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return self.get("distance") == other
        return super().__eq__(other)


def dijkstra(graph, source):
    """
    Run Dijkstra's algorithm from a source node on a weighted graph.

    Parameters
    ----------
    graph : dict[str, list[tuple[str, float]]]
        Adjacency list representation:
          { node_name: [(neighbour_name, distance), ...], ... }
        Every node that appears as a neighbour must also be a key in graph
        (even if its own adjacency list is empty).
    source : str
        Name of the starting node.

    Returns
    -------
    distances : dict[str, float]
        Shortest distance from source to every node.
        Unreachable nodes have value math.inf.
    predecessors : dict[str, str or None]
        Predecessor of each node on the shortest path from source.
        Source itself maps to None.

    Raises
    ------
    ValueError
        If any edge weight is negative.
    """
    # Validate: no negative weights
    for node, neighbours in graph.items():
        for neighbour, dist in neighbours:
            if dist < 0:
                raise ValueError(
                    f"Negative edge weight {dist} found on edge "
                    f"{node} -> {neighbour}. Dijkstra requires non-negative weights."
                )

    # Initialise
    distances = {node: math.inf for node in graph}
    predecessors = {node: None for node in graph}

    if source not in distances:
        raise ValueError(f"Source node '{source}' not found in graph.")

    distances[source] = 0.0
    # Min-heap entries: (distance, node)
    heap = [(0.0, source)]

    visited = set()

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue
        visited.add(current_node)

        for neighbour, edge_weight in graph.get(current_node, []):
            if edge_weight < 0:
                raise ValueError(
                    f"Negative edge weight {edge_weight} on {current_node} -> {neighbour}."
                )
            new_dist = current_dist + edge_weight
            if new_dist < distances.get(neighbour, math.inf):
                distances[neighbour] = new_dist
                predecessors[neighbour] = current_node
                heapq.heappush(heap, (new_dist, neighbour))
            elif new_dist == distances.get(neighbour, math.inf) and current_node != source:
                predecessors[neighbour] = current_node

    return distances, predecessors


def reconstruct_path(predecessors, source, target):
    """
    Reconstruct the shortest path from source to target using predecessors map.

    Parameters
    ----------
    predecessors : dict[str, str or None]
        As returned by dijkstra().
    source : str
        Starting node name.
    target : str
        Destination node name.

    Returns
    -------
    list[str]
        Ordered list of node names from source to target (inclusive).
        Returns an empty list if target is unreachable or not in predecessors.
    """
    if target not in predecessors:
        return []
    if target == source:
        return [source]

    path = []
    current = target
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = predecessors.get(current)
        if current is None and path[-1] != source:
            # Target is unreachable from source
            return []

    path.reverse()
    if path[0] != source:
        return []
    return path


def shortest_path_info(graph, source, target):
    """
    Compute and return complete shortest-path information between two nodes.

    Parameters
    ----------
    graph : dict[str, list[tuple[str, float]]]
        Adjacency list representation of the graph.
    source : str
        Starting node.
    target : str
        Destination node.

    Returns
    -------
    dict with keys:
        path       : list[str]  — ordered nodes from source to target (or [])
        distance   : float      — total path distance (math.inf if unreachable)
        reachable  : bool       — True if target is reachable from source

    Raises
    ------
    ValueError
        If any edge has a negative weight.
    """
    distances, predecessors = dijkstra(graph, source)
    dist = distances.get(target, math.inf)
    reachable = dist < math.inf
    path = reconstruct_path(predecessors, source, target) if reachable else []
    return {
        "path": path,
        "distance": dist,
        "reachable": reachable,
    }


def all_pairs_shortest_paths(graph, nodes=None):
    """
    Compute shortest paths between all pairs of nodes in the given node list.

    Runs Dijkstra once per source node. Useful for building distance matrices
    for TSP or other multi-node routing problems.

    Parameters
    ----------
    graph : dict[str, list[tuple[str, float]]]
        Adjacency list graph representation.
    nodes : list[str], optional
        List of node names to use as sources (and targets). Defaults to all keys in graph.

    Returns
    -------
    dict[str, dict[str, PathInfo]]
        Nested dict: result[from_node][to_node] = PathInfo({path, distance, reachable})
        for every pair of nodes in the given list.
    """
    if nodes is None:
        nodes = list(graph.keys())
    result = {}
    for source in nodes:
        distances, predecessors = dijkstra(graph, source)
        result[source] = {}
        for target in nodes:
            dist = distances.get(target, math.inf)
            reachable = dist < math.inf
            path = reconstruct_path(predecessors, source, target) if reachable else []
            result[source][target] = PathInfo({
                "path": path,
                "distance": dist,
                "reachable": reachable,
            })
    return result


def timed_dijkstra(graph, source):
    """
    Run Dijkstra's algorithm and measure wall-clock execution time.

    Parameters
    ----------
    graph : dict[str, list[tuple[str, float]]]
        Adjacency list graph representation.
    source : str
        Starting node name.

    Returns
    -------
    tuple[dict, dict, float]
        (distances, predecessors, elapsed_ms)
        distances    — shortest distances from source to all nodes
        predecessors — predecessor map for path reconstruction
        elapsed_ms   — execution time in milliseconds (float)

    Raises
    ------
    ValueError
        If any edge has a negative weight.
    """
    start = time.perf_counter()
    distances, predecessors = dijkstra(graph, source)
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000.0
    return distances, predecessors, elapsed_ms
