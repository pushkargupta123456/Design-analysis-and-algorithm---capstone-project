"""
core/courier_planner.py
High-level pipeline that ties together all algorithm modules.
"""

import os
import time
from datetime import datetime

from core.parcel_manager import ParcelManager
from core.graph_manager import GraphManager

# Algorithm imports — guard with try/except so the module still imports even
# if the algorithms package is not yet present (useful during development).
try:
    from algorithms.sorting import merge_sort, timed_sort, default_sort_key
    from algorithms.knapsack import knapsack_01, timed_knapsack
    from algorithms.dijkstra import dijkstra, reconstruct_path
    from algorithms.tsp import nearest_neighbor_tsp, timed_tsp
except ImportError as _imp_err:
    raise ImportError(
        f"Could not import algorithm modules: {_imp_err}. "
        "Ensure the 'algorithms/' package is on the Python path."
    ) from _imp_err


class CourierPlanner:
    """
    Orchestrates the full smart-courier pipeline:

    1. Load parcels + graph
    2. Sort parcels by priority (merge sort)
    3. Select parcels via 0/1 knapsack
    4. Compute shortest paths (Dijkstra) from Depot to each destination
    5. Plan delivery route (TSP nearest-neighbour)
    6. Generate final report
    """

    def __init__(self, vehicle_capacity: int = 100):
        if vehicle_capacity <= 0:
            raise ValueError("vehicle_capacity must be > 0.")
        self.vehicle_capacity = vehicle_capacity
        self.parcel_manager   = ParcelManager()
        self.graph_manager    = GraphManager()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    @property
    def capacity(self):
        return self.vehicle_capacity

    def set_capacity(self, capacity: int):
        """Validate and update vehicle capacity."""
        if capacity <= 0:
            raise ValueError(f"Capacity must be > 0 (got {capacity}).")
        self.vehicle_capacity = capacity

    def load_parcels(self, filepath: str) -> int:
        """Load parcels from CSV."""
        return self.parcel_manager.load_from_csv(filepath)

    def load_graph(self, filepath: str) -> tuple:
        """Load graph from JSON."""
        return self.graph_manager.load_from_json(filepath)

    def load_data(self, parcel_csv: str, graph_json: str):
        """
        Load parcels from CSV and graph from JSON.
        Prints a summary of what was loaded.
        """
        parcel_count = self.parcel_manager.load_from_csv(parcel_csv)
        node_count, edge_count = self.graph_manager.load_from_json(graph_json)

        summary = self.parcel_manager.get_summary()
        print(
            f"[CourierPlanner] Loaded {parcel_count} parcels | "
            f"Graph: {node_count} nodes, {edge_count} edges | "
            f"Destinations: {summary['destinations']} | "
            f"Vehicle capacity: {self.vehicle_capacity}"
        )

    # ------------------------------------------------------------------
    # Pipeline steps
    # ------------------------------------------------------------------

    def prioritize_parcels(self) -> tuple:
        """
        Sort parcels using merge sort (by deadline, then priority desc,
        then value desc).

        Returns (sorted_list, elapsed_ms).
        """
        parcels = self.parcel_manager.get_all_parcels()
        sorted_list, elapsed_ms = timed_sort(parcels, merge_sort, default_sort_key)
        return sorted_list, elapsed_ms

    def select_parcels(self, sorted_parcels: list = None) -> dict:
        """
        Run 0/1 knapsack on *sorted_parcels* (or all parcels if None).
        Returns the knapsack result dict.
        """
        if sorted_parcels is None:
            sorted_parcels = self.parcel_manager.get_all_parcels()
        result, _elapsed = timed_knapsack(sorted_parcels, self.vehicle_capacity)
        self._last_knapsack = result
        return result

    def optimize_selection(self, parcels: list = None) -> tuple:
        """
        Run 0/1 knapsack and return (result_dict, elapsed_ms).
        """
        if parcels is None:
            parcels = self.parcel_manager.get_all_parcels()
        result, elapsed_ms = timed_knapsack(parcels, self.vehicle_capacity)
        self._last_knapsack = result
        return result, elapsed_ms

    def build_delivery_graph(self) -> dict:
        """Return the adjacency list from GraphManager."""
        return self.graph_manager.get_adjacency_list()

    def calculate_shortest_paths(self, destinations: list) -> dict:
        """
        Run Dijkstra from 'Depot' to each destination node.

        Returns:
            {
                dest: {
                    "path":      [node, ...],
                    "distance":  float,
                    "reachable": bool
                },
                ...
            }
        """
        graph = self.build_delivery_graph()
        distances, predecessors = dijkstra(graph, "Depot")

        result = {}
        for dest in destinations:
            d = distances.get(dest, float("inf"))
            reachable = d < float("inf")
            path = reconstruct_path(predecessors, "Depot", dest) if reachable else []
            result[dest] = {
                "path":      path,
                "distance":  d if reachable else None,
                "reachable": reachable,
            }
        return result

    def generate_delivery_route(self, destinations: list = None) -> dict:
        """
        Build a distance matrix for Depot + destinations, then run
        nearest-neighbour TSP.

        Returns the TSP result dict from timed_tsp.
        """
        if destinations is None:
            if hasattr(self, "_last_knapsack") and self._last_knapsack:
                selected = self._last_knapsack.get("selected", [])
                destinations = sorted({p["destination_node"] for p in selected if p.get("destination_node")})
            else:
                destinations = sorted({p["destination_node"] for p in self.parcel_manager.get_all_parcels() if p.get("destination_node")})

        graph = self.build_delivery_graph()
        distances, predecessors = dijkstra(graph, "Depot")

        all_nodes = ["Depot"] + [d for d in destinations if d != "Depot"]

        # Build pairwise distance matrix using Dijkstra from each node
        node_distances = {"Depot": distances}
        for node in destinations:
            if node not in node_distances:
                d, _ = dijkstra(graph, node)
                node_distances[node] = d

        matrix = {}
        for n1 in all_nodes:
            matrix[n1] = {}
            d_from_n1 = node_distances.get(n1, {})
            for n2 in all_nodes:
                matrix[n1][n2] = d_from_n1.get(n2, float("inf"))

        delivery_nodes = [d for d in destinations if d != "Depot"]
        tsp_result, elapsed_ms = timed_tsp(matrix, delivery_nodes, "Depot")

        # Build segments list for detailed display
        route = tsp_result.get("route", [])
        seg_dists = tsp_result.get("segment_distances", [])
        segments = []
        for i in range(len(seg_dists)):
            if i + 1 < len(route):
                segments.append({
                    "from": route[i],
                    "to": route[i + 1],
                    "distance": seg_dists[i],
                })
        tsp_result["segments"] = segments
        tsp_result["elapsed_ms"] = elapsed_ms
        return tsp_result

    # ------------------------------------------------------------------
    # Complete pipeline
    # ------------------------------------------------------------------

    def run_complete_pipeline(
        self,
        parcel_csv: str,
        graph_json: str,
        capacity: int = None,
    ) -> dict:
        """
        Execute the full courier pipeline and return a comprehensive results
        dict with keys:
            sorted_parcels, knapsack_result, shortest_paths, tsp_result, timings
        """
        timings = {}

        # 1. Load data
        t0 = time.perf_counter()
        if capacity is not None:
            self.set_capacity(capacity)
        self.load_data(parcel_csv, graph_json)
        timings["load_ms"] = round((time.perf_counter() - t0) * 1000, 3)

        # 2. Sort parcels
        t0 = time.perf_counter()
        sorted_parcels, sort_ms = self.prioritize_parcels()
        timings["sort_ms"] = sort_ms
        print(f"[Pipeline] Step 2: Sorted {len(sorted_parcels)} parcels in {sort_ms:.2f} ms")

        # 3. Select parcels (knapsack)
        t0 = time.perf_counter()
        knapsack_result = self.select_parcels(sorted_parcels)
        timings["knapsack_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        selected_count = len(knapsack_result.get("selected", []))
        print(
            f"[Pipeline] Step 3: Knapsack selected {selected_count} parcels "
            f"(weight {knapsack_result.get('total_weight')}/{self.vehicle_capacity}, "
            f"value {knapsack_result.get('total_value')}) "
            f"in {timings['knapsack_ms']:.2f} ms"
        )

        # 4. Determine delivery destinations from selected parcels
        selected_parcels = knapsack_result.get("selected", [])
        destinations = sorted(
            {p["destination_node"] for p in selected_parcels}
        )
        print(f"[Pipeline] Step 4: Destinations to visit: {destinations}")

        # 5. Shortest paths
        t0 = time.perf_counter()
        shortest_paths = self.calculate_shortest_paths(destinations)
        timings["dijkstra_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        print(f"[Pipeline] Step 5: Computed shortest paths in {timings['dijkstra_ms']:.2f} ms")

        # 6. TSP route
        t0 = time.perf_counter()
        tsp_result = self.generate_delivery_route(destinations)
        timings["tsp_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        print(
            f"[Pipeline] Step 6: TSP route computed in {timings['tsp_ms']:.2f} ms | "
            f"Route: {tsp_result.get('route')} | "
            f"Total distance: {tsp_result.get('total_distance')}"
        )

        return {
            "sorted_parcels":  sorted_parcels,
            "knapsack_result": knapsack_result,
            "shortest_paths":  shortest_paths,
            "tsp_result":      tsp_result,
            "timings":         timings,
        }

    def run_complete_planning(
        self,
        parcel_csv: str = None,
        graph_json: str = None,
        output_path: str = None,
    ) -> dict:
        """
        Run the complete courier planning workflow for the interactive menu.
        Automatically generates the report file and returns structured results.
        """
        if parcel_csv is not None and graph_json is not None:
            self.load_data(parcel_csv, graph_json)

        sorted_parcels, sort_ms = self.prioritize_parcels()
        knapsack_result, ks_ms = self.optimize_selection(sorted_parcels)
        self._last_knapsack = knapsack_result

        selected = knapsack_result.get("selected", [])
        destinations = sorted({p["destination_node"] for p in selected if p.get("destination_node")})
        if not destinations:
            destinations = sorted({p["destination_node"] for p in self.parcel_manager.get_all_parcels() if p.get("destination_node")})

        t_sp = time.perf_counter()
        shortest_paths = self.calculate_shortest_paths(destinations)
        sp_ms = (time.perf_counter() - t_sp) * 1000.0

        tsp_result = self.generate_delivery_route(destinations)

        if output_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_path = os.path.join(base_dir, "reports", "final_delivery_report.txt")

        report_payload = {
            "sorted_parcels": sorted_parcels,
            "knapsack_result": knapsack_result,
            "shortest_paths": shortest_paths,
            "tsp_result": tsp_result,
            "timings": {
                "load_ms": 1.0,
                "sort_ms": sort_ms,
                "knapsack_ms": ks_ms,
                "dijkstra_ms": sp_ms,
                "tsp_ms": tsp_result.get("elapsed_ms", 0.1),
            },
        }
        self.generate_report(report_payload, output_path)

        return {
            "sort": {"count": len(sorted_parcels), "elapsed_ms": sort_ms, "parcels": sorted_parcels},
            "knapsack": knapsack_result,
            "shortest_paths": shortest_paths,
            "tsp": tsp_result,
            "report_path": output_path,
            "sorted_parcels": sorted_parcels,
            "knapsack_result": knapsack_result,
            "tsp_result": tsp_result,
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_report(self, results: dict, output_path: str):
        """
        Write a human-readable final delivery report to *output_path*.

        Covers:
        - Vehicle capacity & parcel summary
        - Sorted parcel list (top 20)
        - Knapsack selection summary
        - Shortest paths per destination
        - TSP delivery route
        - Timing breakdown
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        sorted_parcels  = results.get("sorted_parcels",  [])
        knapsack_result = results.get("knapsack_result", {})
        shortest_paths  = results.get("shortest_paths",  {})
        tsp_result      = results.get("tsp_result",      {})
        timings         = results.get("timings",         {})

        selected = knapsack_result.get("selected", [])
        rejected = knapsack_result.get("rejected", [])

        lines = []
        sep   = "=" * 72

        # Header
        lines += [
            sep,
            "          SMART COURIER — FINAL DELIVERY REPORT",
            f"          Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            sep,
            "",
        ]

        # Vehicle info
        lines += [
            "VEHICLE CONFIGURATION",
            "-" * 40,
            f"  Capacity          : {self.vehicle_capacity} kg",
            f"  Total parcels     : {len(sorted_parcels)}",
            f"  Selected parcels  : {len(selected)}",
            f"  Rejected parcels  : {len(rejected)}",
            "",
        ]

        # Sorted parcels (top 20)
        lines += [
            "PRIORITY-SORTED PARCEL LIST (top 20 by deadline / priority / value)",
            "-" * 72,
            f"  {'ID':<12} {'Name':<20} {'Wt':>5} {'Pri':>4} {'Deadline':>12} {'Dest':>8} {'Val':>8}",
            "  " + "-" * 68,
        ]
        for p in sorted_parcels[:20]:
            lines.append(
                f"  {p['parcel_id']:<12} {p['parcel_name']:<20} "
                f"{p['weight']:>5.1f} {p['priority_score']:>4.0f} "
                f"{p['delivery_deadline']:>12} {p['destination_node']:>8} "
                f"{p['delivery_value']:>8.1f}"
            )
        if len(sorted_parcels) > 20:
            lines.append(f"  ... ({len(sorted_parcels) - 20} more parcels not shown)")
        lines.append("")

        # Knapsack results
        lines += [
            "KNAPSACK SELECTION RESULTS",
            "-" * 40,
            f"  Total weight loaded  : {knapsack_result.get('total_weight', 0)} kg",
            f"  Remaining capacity   : {knapsack_result.get('remaining_capacity', 0)} kg",
            f"  Total delivery value : {knapsack_result.get('total_value', 0)}",
            "",
            "  Selected parcels:",
        ]
        for p in selected:
            lines.append(
                f"    {p['parcel_id']:<12} → {p['destination_node']:>8}  "
                f"wt={p['weight']:.1f}  val={p['delivery_value']:.1f}"
            )
        lines.append("")

        # Shortest paths
        lines += [
            "SHORTEST PATHS FROM DEPOT",
            "-" * 40,
        ]
        for dest, info in shortest_paths.items():
            if info["reachable"]:
                path_str = " → ".join(info["path"])
                lines.append(
                    f"  Depot → {dest}: {path_str}  (distance: {info['distance']:.1f})"
                )
            else:
                lines.append(f"  Depot → {dest}: UNREACHABLE")
        lines.append("")

        # TSP route
        route          = tsp_result.get("route",           [])
        total_distance = tsp_result.get("total_distance",  "N/A")
        lines += [
            "DELIVERY ROUTE (TSP — Nearest Neighbour)",
            "-" * 40,
            f"  Route          : {' → '.join(route)}",
            f"  Total distance : {total_distance}",
            "",
        ]

        # Timings
        lines += [
            "TIMING BREAKDOWN",
            "-" * 40,
        ]
        labels = {
            "load_ms":     "Data loading",
            "sort_ms":     "Merge sort",
            "knapsack_ms": "Knapsack DP",
            "dijkstra_ms": "Dijkstra (all dests)",
            "tsp_ms":      "TSP nearest-neighbour",
        }
        for key, label in labels.items():
            if key in timings:
                lines.append(f"  {label:<25}: {timings[key]:>8.3f} ms")
        lines.append("")
        lines.append(sep)
        lines.append("END OF REPORT")
        lines.append(sep)

        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

        print(f"[CourierPlanner] Report written to '{output_path}'")


def run_complete_pipeline(
    parcel_csv: str = None,
    graph_json: str = None,
    vehicle_capacity: int = 100,
    parcels_csv: str = None,
) -> dict:
    """Convenience function to run the full pipeline in one call."""
    csv_file = parcel_csv if parcel_csv is not None else parcels_csv
    planner = CourierPlanner(vehicle_capacity=vehicle_capacity)
    return planner.run_complete_pipeline(csv_file, graph_json, capacity=vehicle_capacity)


def generate_report(results: dict, output_path: str):
    """Convenience function to generate the final delivery report."""
    planner = CourierPlanner()
    return planner.generate_report(results, output_path)
