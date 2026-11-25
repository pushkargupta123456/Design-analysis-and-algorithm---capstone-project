"""
core/performance.py
Benchmarking and chart generation for all algorithm modules.
"""

import csv
import os
import statistics
import time
from datetime import datetime

from core.parcel_manager import ParcelManager
from core.graph_manager import GraphManager

try:
    from algorithms.sorting import merge_sort, builtin_sort, timed_sort, default_sort_key
    from algorithms.knapsack import timed_knapsack
    from algorithms.dijkstra import timed_dijkstra
    from algorithms.tsp import timed_tsp
except ImportError as _imp_err:
    raise ImportError(
        f"Could not import algorithm modules: {_imp_err}. "
        "Ensure the 'algorithms/' package is on the Python path."
    ) from _imp_err

try:
    import matplotlib
    matplotlib.use("Agg")          # non-interactive backend
    import matplotlib.pyplot as plt
    _MATPLOTLIB_OK = True
except ImportError:
    _MATPLOTLIB_OK = False


class PerformanceBenchmark:
    """
    Benchmarks all four algorithms across small, medium and large datasets
    and produces CSV reports + matplotlib charts.
    """

    def __init__(
        self,
        small_csv:  str = None,
        medium_csv: str = None,
        large_csv:  str = None,
        graph_json: str = None,
    ):
        self.small_csv  = small_csv
        self.medium_csv = medium_csv
        self.large_csv  = large_csv
        self.graph_json = graph_json
        self._results: list = []

    # ------------------------------------------------------------------
    # Individual benchmarks
    # ------------------------------------------------------------------

    def benchmark_sorting(self, parcels_list: list) -> dict:
        """
        Run merge_sort and builtin_sort on a *copy* of parcels_list 5 times
        each.  Record the median elapsed time.

        Returns:
            {merge_sort_ms, builtin_sort_ms, parcel_count}
        """
        n = len(parcels_list)
        merge_times   = []
        builtin_times = []

        for _ in range(5):
            copy = list(parcels_list)
            _, ms = timed_sort(copy, merge_sort, default_sort_key)
            merge_times.append(ms)

            copy = list(parcels_list)
            _, ms = timed_sort(copy, builtin_sort, default_sort_key)
            builtin_times.append(ms)

        return {
            "merge_sort_ms":  statistics.median(merge_times),
            "builtin_sort_ms": statistics.median(builtin_times),
            "parcel_count":   n,
        }

    def benchmark_knapsack(self, parcels_list: list, capacity: int) -> dict:
        """
        Run timed_knapsack once.

        Returns:
            {elapsed_ms, parcel_count, capacity}
        """
        _, elapsed_ms = timed_knapsack(parcels_list, capacity)
        return {
            "elapsed_ms":   elapsed_ms,
            "parcel_count": len(parcels_list),
            "capacity":     capacity,
        }

    def benchmark_dijkstra(self, graph: dict, source: str, node_count: int) -> dict:
        """
        Run timed_dijkstra once from *source*.

        Returns:
            {elapsed_ms, node_count, edge_count}
        """
        edge_count = sum(len(v) for v in graph.values()) // 2
        *_, elapsed_ms = timed_dijkstra(graph, source)
        return {
            "elapsed_ms": elapsed_ms,
            "node_count": node_count,
            "edge_count": edge_count,
        }

    def benchmark_tsp(
        self, distance_matrix: dict, delivery_nodes: list, depot: str
    ) -> dict:
        """
        Run timed_tsp once.

        Returns:
            {elapsed_ms, node_count}
        """
        _, elapsed_ms = timed_tsp(distance_matrix, delivery_nodes, depot)
        return {
            "elapsed_ms": elapsed_ms,
            "node_count": len(delivery_nodes),
        }

    # ------------------------------------------------------------------
    # Full benchmark suite
    # ------------------------------------------------------------------

    def run_full_benchmark(
        self,
        small_csv:  str = None,
        medium_csv: str = None,
        large_csv:  str = None,
        graph_json: str = None,
    ) -> list:
        """
        Load small / medium / large datasets, run all benchmarks, write
        reports/runtime_results.csv and reports/performance_report.txt.

        Returns a list of result dicts (one per dataset × algorithm).
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        small_csv  = small_csv or self.small_csv or os.path.join(base_dir, "data", "parcels_small.csv")
        medium_csv = medium_csv or self.medium_csv or os.path.join(base_dir, "data", "parcels_medium.csv")
        large_csv  = large_csv or self.large_csv or os.path.join(base_dir, "data", "parcels_large.csv")
        graph_json = graph_json or self.graph_json or os.path.join(base_dir, "data", "delivery_graph.json")
        pm = ParcelManager()
        gm = GraphManager()

        # Load graph once
        node_count, _ec = gm.load_from_json(graph_json)
        graph = gm.get_adjacency_list()

        # Build a minimal distance matrix for TSP using graph nodes
        nodes = gm.get_nodes()
        distance_matrix, depot = self._build_distance_matrix(graph, nodes)

        datasets = [
            ("small",  small_csv),
            ("medium", medium_csv),
            ("large",  large_csv),
        ]

        all_results = []

        for label, csv_path in datasets:
            try:
                pm.clear()
                pm.load_from_csv(csv_path)
            except Exception as exc:
                print(f"[Benchmark] Skipping '{label}': {exc}")
                continue

            parcels = pm.get_all_parcels()
            capacity = max(int(sum(p["weight"] for p in parcels) * 0.6), 1)

            print(f"\n[Benchmark] === {label.upper()} dataset ({len(parcels)} parcels) ===")

            # -- Sorting --
            sort_res = self.benchmark_sorting(parcels)
            print(
                f"  sort   | merge={sort_res['merge_sort_ms']:.3f} ms  "
                f"builtin={sort_res['builtin_sort_ms']:.3f} ms"
            )
            all_results.append({
                "dataset":        label,
                "algorithm":      "merge_sort",
                "execution_time_ms": sort_res["merge_sort_ms"],
                "complexity":     "O(n log n)",
                "parcel_count":   len(parcels),
                "node_count":     node_count,
            })
            all_results.append({
                "dataset":        label,
                "algorithm":      "builtin_sort",
                "execution_time_ms": sort_res["builtin_sort_ms"],
                "complexity":     "O(n log n)",
                "parcel_count":   len(parcels),
                "node_count":     node_count,
            })

            # -- Knapsack --
            ks_res = self.benchmark_knapsack(parcels, capacity)
            print(f"  knapsack | {ks_res['elapsed_ms']:.3f} ms  cap={capacity}")
            all_results.append({
                "dataset":           label,
                "algorithm":         "knapsack_01",
                "execution_time_ms": ks_res["elapsed_ms"],
                "complexity":        "O(n * W)",
                "parcel_count":      len(parcels),
                "node_count":        node_count,
            })

            # -- Dijkstra --
            dijk_res = self.benchmark_dijkstra(graph, depot, node_count)
            print(f"  dijkstra | {dijk_res['elapsed_ms']:.3f} ms  nodes={node_count}")
            all_results.append({
                "dataset":           label,
                "algorithm":         "dijkstra",
                "execution_time_ms": dijk_res["elapsed_ms"],
                "complexity":        "O((V + E) log V)",
                "parcel_count":      len(parcels),
                "node_count":        node_count,
            })

            # -- TSP (delivery nodes from selected parcels) --
            delivery_nodes = list(distance_matrix.keys())
            tsp_res = self.benchmark_tsp(distance_matrix, delivery_nodes, depot)
            print(f"  tsp      | {tsp_res['elapsed_ms']:.3f} ms  nodes={tsp_res['node_count']}")
            all_results.append({
                "dataset":           label,
                "algorithm":         "tsp_nearest_neighbour",
                "execution_time_ms": tsp_res["elapsed_ms"],
                "complexity":        "O(n^2)",
                "parcel_count":      len(parcels),
                "node_count":        tsp_res["node_count"],
            })

        self._results = all_results

        # Save outputs
        reports_dir = os.path.join(
            os.path.dirname(os.path.abspath(graph_json)), "..", "reports"
        )
        reports_dir = os.path.normpath(reports_dir)
        os.makedirs(reports_dir, exist_ok=True)

        csv_path  = os.path.join(reports_dir, "runtime_results.csv")
        txt_path  = os.path.join(reports_dir, "performance_report.txt")

        self.save_runtime_csv(all_results, csv_path)
        self.generate_performance_report(all_results, txt_path)

        return all_results

    # ------------------------------------------------------------------
    # Chart generation
    # ------------------------------------------------------------------

    def generate_charts(self, results_list: list = None, charts_dir: str = None) -> str:
        """
        Generate 5 matplotlib charts and save as PNG to *charts_dir*.

        Charts produced:
        1. sorting_comparison.png       — merge sort vs builtin sort
        2. knapsack_performance.png     — knapsack time by dataset
        3. dijkstra_performance.png     — dijkstra time by dataset
        4. tsp_performance.png          — TSP time by node count
        5. overall_runtime_comparison.png — all algorithms side-by-side
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if charts_dir is None:
            charts_dir = os.path.join(base_dir, "charts")
        charts_dir = os.path.normpath(charts_dir)

        if results_list is None:
            results_list = self._results
            if not results_list:
                results_list = self.run_full_benchmark()

        if not _MATPLOTLIB_OK:
            print("[Benchmark] matplotlib not available — skipping chart generation.")
            return charts_dir

        os.makedirs(charts_dir, exist_ok=True)

        # Organise data
        datasets  = ["small", "medium", "large"]
        algo_map  = {}  # algo -> {dataset -> ms}
        for row in results_list:
            algo = row["algorithm"]
            ds   = row["dataset"]
            ms   = row["execution_time_ms"]
            algo_map.setdefault(algo, {})[ds] = ms

        counts = {}  # dataset -> parcel_count
        for row in results_list:
            counts[row["dataset"]] = row["parcel_count"]

        present = [d for d in datasets if d in counts]
        x_labels = [f"{d}\n({counts.get(d, '?')} parcels)" for d in present]
        x_pos = list(range(len(present)))

        # ---- 1. Sorting comparison ----
        merge_vals   = [algo_map.get("merge_sort",   {}).get(d, 0) for d in present]
        builtin_vals = [algo_map.get("builtin_sort", {}).get(d, 0) for d in present]

        fig, ax = plt.subplots(figsize=(8, 5))
        bar_w = 0.35
        bars1 = [xi - bar_w / 2 for xi in x_pos]
        bars2 = [xi + bar_w / 2 for xi in x_pos]
        ax.bar(bars1, merge_vals,   bar_w, label="Merge Sort",   color="#2196F3")
        ax.bar(bars2, builtin_vals, bar_w, label="Builtin Sort", color="#FF9800")
        ax.set_title("Sorting Algorithm Comparison (Median over 5 runs)")
        ax.set_xlabel("Dataset")
        ax.set_ylabel("Time (ms)")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        fig.savefig(os.path.join(charts_dir, "sorting_comparison.png"), dpi=150)
        plt.close(fig)

        # ---- 2. Knapsack performance ----
        ks_vals = [algo_map.get("knapsack_01", {}).get(d, 0) for d in present]

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(x_pos, ks_vals, color="#9C27B0", label="0/1 Knapsack DP")
        ax.set_title("0/1 Knapsack DP Performance")
        ax.set_xlabel("Dataset")
        ax.set_ylabel("Time (ms)")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        fig.savefig(os.path.join(charts_dir, "knapsack_performance.png"), dpi=150)
        plt.close(fig)

        # ---- 3. Dijkstra performance ----
        dijk_vals = [algo_map.get("dijkstra", {}).get(d, 0) for d in present]

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(x_pos, dijk_vals, color="#4CAF50", label="Dijkstra")
        ax.set_title("Dijkstra Shortest Path Performance")
        ax.set_xlabel("Dataset")
        ax.set_ylabel("Time (ms)")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        fig.savefig(os.path.join(charts_dir, "dijkstra_performance.png"), dpi=150)
        plt.close(fig)

        # ---- 4. TSP performance ----
        tsp_vals = [algo_map.get("tsp_nearest_neighbour", {}).get(d, 0) for d in present]
        node_counts = []
        for d in present:
            nc = next(
                (r["node_count"] for r in results_list
                 if r["dataset"] == d and r["algorithm"] == "tsp_nearest_neighbour"),
                0
            )
            node_counts.append(nc)
        tsp_x_labels = [f"{d}\n({nc} nodes)" for d, nc in zip(present, node_counts)]

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(x_pos, tsp_vals, color="#F44336", label="TSP Nearest Neighbour")
        ax.set_title("TSP Nearest Neighbour Performance")
        ax.set_xlabel("Dataset (node count)")
        ax.set_ylabel("Time (ms)")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(tsp_x_labels)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        fig.savefig(os.path.join(charts_dir, "tsp_performance.png"), dpi=150)
        plt.close(fig)

        # ---- 5. Overall runtime comparison ----
        algos = ["merge_sort", "knapsack_01", "dijkstra", "tsp_nearest_neighbour"]
        algo_labels = ["Merge Sort", "Knapsack DP", "Dijkstra", "TSP NN"]
        colors = ["#2196F3", "#9C27B0", "#4CAF50", "#F44336"]

        fig, ax = plt.subplots(figsize=(10, 6))
        n_algos = len(algos)
        group_w = 0.8
        bar_w   = group_w / len(present)
        offsets = [(i - (len(present) - 1) / 2) * bar_w for i in range(len(present))]

        for di, ds in enumerate(present):
            vals = [algo_map.get(a, {}).get(ds, 0) for a in algos]
            xs   = [ai + offsets[di] for ai in range(n_algos)]
            ax.bar(xs, vals, bar_w, label=ds.capitalize(), alpha=0.85)

        ax.set_title("Overall Runtime Comparison — All Algorithms & Datasets")
        ax.set_xlabel("Algorithm")
        ax.set_ylabel("Time (ms)")
        ax.set_xticks(range(n_algos))
        ax.set_xticklabels(algo_labels)
        ax.legend(title="Dataset")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        fig.savefig(os.path.join(charts_dir, "overall_runtime_comparison.png"), dpi=150)
        plt.close(fig)

        print(f"[Benchmark] 5 charts saved to '{charts_dir}'")
        return charts_dir

    # ------------------------------------------------------------------
    # CSV / text report helpers
    # ------------------------------------------------------------------

    def save_runtime_csv(self, results: list, filepath: str):
        """Append benchmark results to a CSV file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        file_exists = os.path.isfile(filepath)
        fieldnames  = [
            "dataset", "algorithm", "execution_time_ms",
            "complexity", "parcel_count", "node_count",
        ]

        with open(filepath, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            if not file_exists or os.path.getsize(filepath) == 0:
                writer.writeheader()
            for row in results:
                writer.writerow({k: row.get(k, "") for k in fieldnames})

        print(f"[Benchmark] Runtime CSV saved to '{filepath}'")

    def generate_performance_report(self, results: list, filepath: str):
        """Write a human-readable performance report."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        complexity_notes = {
            "merge_sort":           "O(n log n) — divide and conquer",
            "builtin_sort":         "O(n log n) — Timsort (Python built-in)",
            "knapsack_01":          "O(n × W)  — 0/1 DP, pseudo-polynomial",
            "dijkstra":             "O((V + E) log V) — min-heap priority queue",
            "tsp_nearest_neighbour": "O(n²)    — greedy nearest-neighbour heuristic",
        }

        lines = []
        sep   = "=" * 72
        lines += [
            sep,
            "       SMART COURIER — ALGORITHM PERFORMANCE REPORT",
            f"       Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            sep,
            "",
        ]

        # Group by algorithm
        by_algo: dict = {}
        for row in results:
            by_algo.setdefault(row["algorithm"], []).append(row)

        for algo, rows in by_algo.items():
            lines += [
                f"ALGORITHM: {algo.upper()}",
                f"  Complexity : {complexity_notes.get(algo, 'N/A')}",
                "  Results    :",
            ]
            for row in rows:
                lines.append(
                    f"    dataset={row['dataset']:<8}  "
                    f"parcels={row.get('parcel_count', 'N/A'):<6}  "
                    f"nodes={row.get('node_count', 'N/A'):<4}  "
                    f"time={row['execution_time_ms']:.3f} ms"
                )
            # Simple observation
            times = [r["execution_time_ms"] for r in rows if r["execution_time_ms"]]
            if len(times) >= 2:
                ratio = times[-1] / times[0] if times[0] > 0 else float("inf")
                lines.append(
                    f"  Observation: Runtime grew {ratio:.1f}× from smallest to largest dataset."
                )
            lines.append("")

        lines += [sep, "END OF PERFORMANCE REPORT", sep]

        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

        print(f"[Benchmark] Performance report saved to '{filepath}'")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_distance_matrix(graph: dict, nodes: list) -> tuple:
        """
        Build a full pairwise distance matrix using Dijkstra from each node.
        Returns (distance_matrix_dict, depot_node).
        """
        from algorithms.dijkstra import dijkstra as _dijkstra

        depot = "Depot" if "Depot" in nodes else nodes[0]
        matrix: dict = {}

        for src in nodes:
            distances, _ = _dijkstra(graph, src)
            matrix[src] = {tgt: distances.get(tgt, float("inf")) for tgt in nodes}

        return matrix, depot
