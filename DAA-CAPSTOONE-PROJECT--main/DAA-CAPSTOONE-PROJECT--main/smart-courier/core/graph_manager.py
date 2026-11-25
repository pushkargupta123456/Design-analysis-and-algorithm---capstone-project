"""
core/graph_manager.py
Manages the delivery graph: loading from JSON, validation, and queries.
"""

import json
from collections import deque


class GraphManager:
    """
    Manages a weighted, undirected delivery graph.

    Internally stores:
        _nodes  : set of node names
        _edges  : list of (from, to, distance) tuples (each undirected pair stored once)
        _adj    : dict {node: [(neighbor, distance), ...]}  (both directions)
    """

    DEPOT = "Depot"

    def __init__(self):
        self._nodes: set  = set()
        self._edges: list = []        # (from, to, distance) – canonical direction
        self._adj:   dict = {}

    @property
    def graph(self):
        return self._adj

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_from_json(self, filepath: str) -> tuple:
        """
        Load a delivery graph from a JSON file.

        Expected format::

            {
                "nodes": ["Depot", "A", "B", ...],
                "edges": [
                    {"from": "Depot", "to": "A", "distance": 5},
                    ...
                ]
            }

        Validates:
        - No negative edge distances.
        - Both endpoints of every edge must exist in the nodes list.
        - Graph must be connected from "Depot".

        Returns (node_count, edge_count).
        Raises ValueError on bad data, FileNotFoundError if file missing.
        """
        try:
            with open(filepath, encoding="utf-8") as fh:
                data = json.load(fh)
        except FileNotFoundError:
            raise ValueError(f"Graph JSON file not found: '{filepath}'")
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in '{filepath}': {exc}") from exc

        if "nodes" not in data:
            raise ValueError("Graph JSON missing 'nodes' key.")
        if "edges" not in data:
            raise ValueError("Graph JSON missing 'edges' key.")

        # Reset
        self._nodes = set()
        self._edges = []
        self._adj   = {}

        # Load nodes
        for node in data["nodes"]:
            self.add_node(str(node))

        # Verify Depot exists
        if self.DEPOT not in self._nodes:
            raise ValueError(
                f"Graph must contain a '{self.DEPOT}' node."
            )

        # Load edges
        for idx, edge in enumerate(data["edges"]):
            frm = str(edge.get("from", "")).strip()
            to  = str(edge.get("to",   "")).strip()
            try:
                dist = float(edge["distance"])
            except (KeyError, TypeError, ValueError):
                raise ValueError(
                    f"Edge #{idx}: 'distance' is missing or not numeric."
                )

            if frm not in self._nodes:
                raise ValueError(
                    f"Edge #{idx}: from-node '{frm}' is not in the nodes list."
                )
            if to not in self._nodes:
                raise ValueError(
                    f"Edge #{idx}: to-node '{to}' is not in the nodes list."
                )
            if dist < 0:
                raise ValueError(
                    f"Edge #{idx} ({frm} -> {to}): distance must be >= 0 (got {dist})."
                )

            self.add_edge(frm, to, dist)

        # Connectivity check
        self.validate_graph()

        return len(self._nodes), len(self._edges)

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def add_node(self, name: str):
        """Add a node (idempotent)."""
        self._nodes.add(name)
        if name not in self._adj:
            self._adj[name] = []

    def add_edge(self, from_node: str, to_node: str, distance: float):
        """
        Add an undirected edge.  Validates existence of both nodes and
        non-negative distance.
        """
        if from_node not in self._nodes:
            raise ValueError(f"add_edge: node '{from_node}' does not exist.")
        if to_node not in self._nodes:
            raise ValueError(f"add_edge: node '{to_node}' does not exist.")
        if distance < 0:
            raise ValueError(
                f"add_edge: distance must be >= 0 (got {distance}) "
                f"for edge {from_node} <-> {to_node}."
            )

        self._edges.append((from_node, to_node, distance))
        self._adj[from_node].append((to_node, distance))
        self._adj[to_node].append((from_node, distance))

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_adjacency_list(self) -> dict:
        """
        Return adjacency list: {node: [(neighbor, distance), ...]}.
        Graph is undirected — both directions are present.
        """
        return {node: list(neighbors) for node, neighbors in self._adj.items()}

    def get_nodes(self) -> list:
        """Return sorted list of node names."""
        return sorted(self._nodes)

    def get_edges(self) -> list:
        """Return list of (from, to, distance) tuples (canonical direction)."""
        return list(self._edges)

    def is_reachable(self, source: str, target: str) -> bool:
        """BFS reachability check from source to target."""
        if source not in self._nodes or target not in self._nodes:
            return False
        if source == target:
            return True

        visited = {source}
        queue   = deque([source])
        while queue:
            current = queue.popleft()
            for neighbor, _ in self._adj.get(current, []):
                if neighbor == target:
                    return True
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    def get_graph_summary(self) -> dict:
        """Return dict: node_count, edge_count, nodes list, edges list."""
        return {
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "nodes":      self.get_nodes(),
            "edges":      self.get_edges(),
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_graph(self):
        """
        BFS from Depot to verify every node is reachable.
        Raises ValueError listing unreachable nodes.
        """
        if self.DEPOT not in self._nodes:
            raise ValueError(f"Graph has no '{self.DEPOT}' node.")

        visited = {self.DEPOT}
        queue   = deque([self.DEPOT])
        while queue:
            current = queue.popleft()
            for neighbor, _ in self._adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        unreachable = self._nodes - visited
        if unreachable:
            raise ValueError(
                f"Graph is disconnected. Nodes unreachable from '{self.DEPOT}': "
                f"{', '.join(sorted(unreachable))}"
            )
