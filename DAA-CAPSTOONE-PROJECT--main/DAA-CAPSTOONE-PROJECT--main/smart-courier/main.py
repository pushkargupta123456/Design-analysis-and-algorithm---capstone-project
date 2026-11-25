import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.courier_planner import CourierPlanner
from core.performance import PerformanceBenchmark
from core.graph_manager import GraphManager
from core.parcel_manager import ParcelManager
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SMALL_CSV  = os.path.join(BASE_DIR, "data", "parcels_small.csv")
DEFAULT_MEDIUM_CSV = os.path.join(BASE_DIR, "data", "parcels_medium.csv")
DEFAULT_LARGE_CSV  = os.path.join(BASE_DIR, "data", "parcels_large.csv")
DEFAULT_GRAPH_JSON = os.path.join(BASE_DIR, "data", "delivery_graph.json")
DEFAULT_CAPACITY   = 150


class SmartCourierApp:
    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------
    def __init__(self):
        self.planner        = CourierPlanner(DEFAULT_CAPACITY)
        self.current_dataset = "small"
        self.results        = None

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------
    def display_menu(self):
        print("\n===========================================")
        print("         SMART COURIER SYSTEM")
        print(" Intelligent Parcel Packing & Route Planner")
        print("===========================================")
        print("1.  Load Sample Dataset")
        print("2.  View All Parcels")
        print("3.  Prioritize Parcels (Merge Sort)")
        print("4.  Optimize Package Selection (0/1 Knapsack)")
        print("5.  View Delivery Graph")
        print("6.  Calculate Shortest Paths (Dijkstra)")
        print("7.  Generate Optimized Delivery Route (TSP)")
        print("8.  Run Complete Courier Planning")
        print("9.  Run Performance Benchmarks")
        print("10. Generate Performance Charts")
        print("11. View Final Delivery Report")
        print("0.  Exit")
        print("===========================================")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def run(self):
        print("\nWelcome to the SMART COURIER SYSTEM!")
        print("Initialising application…")

        dispatch = {
            "1":  self.handle_load_dataset,
            "2":  self.handle_view_parcels,
            "3":  self.handle_prioritize,
            "4":  self.handle_knapsack,
            "5":  self.handle_view_graph,
            "6":  self.handle_shortest_paths,
            "7":  self.handle_delivery_route,
            "8":  self.handle_complete_planning,
            "9":  self.handle_benchmarks,
            "10": self.handle_charts,
            "11": self.handle_view_report,
            "0":  None,
        }

        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == "0":
                print("\nThank you for using Smart Courier System. Goodbye!")
                break

            handler = dispatch.get(choice)
            if handler is None:
                print(f"\n[!] Invalid option '{choice}'. Please enter a number from 0 to 11.")
            else:
                try:
                    handler()
                except KeyboardInterrupt:
                    print("\n[!] Operation cancelled by user.")
                except Exception as exc:
                    print(f"\n[ERROR] An unexpected error occurred: {exc}")
                    print("       Please try again or reload data.")

    # ------------------------------------------------------------------
    # Helper: check data loaded
    # ------------------------------------------------------------------
    def _require_data(self) -> bool:
        if not self.planner.parcel_manager.parcels:
            print("\n[!] No data loaded. Please use Option 1 to load a dataset first.")
            return False
        return True

    def _require_knapsack(self) -> bool:
        if self.results is None or "knapsack" not in self.results:
            print("\n[!] Knapsack not yet run. Please use Option 4 or Option 8 first.")
            return False
        return True

    # ------------------------------------------------------------------
    # Option 1 — Load Dataset
    # ------------------------------------------------------------------
    def handle_load_dataset(self):
        print("\n=== LOAD SAMPLE DATASET ===")
        print("Available datasets:")
        print("  [1] Small  (~15 parcels,  5 destinations)")
        print("  [2] Medium (~150 parcels, 15 destinations)")
        print("  [3] Large  (~700 parcels, 36 destinations)")

        ds_choice = input("\nSelect dataset (1/2/3) [default: 1]: ").strip() or "1"
        ds_map = {"1": ("small", DEFAULT_SMALL_CSV),
                  "2": ("medium", DEFAULT_MEDIUM_CSV),
                  "3": ("large", DEFAULT_LARGE_CSV)}

        if ds_choice not in ds_map:
            print("[!] Invalid selection. Defaulting to small dataset.")
            ds_choice = "1"

        self.current_dataset, csv_path = ds_map[ds_choice]

        cap_input = input(f"Enter vehicle capacity (default {DEFAULT_CAPACITY}): ").strip()
        try:
            capacity = int(cap_input) if cap_input else DEFAULT_CAPACITY
            if capacity <= 0:
                raise ValueError("Capacity must be positive.")
        except ValueError as e:
            print(f"[!] Invalid capacity ({e}). Using default {DEFAULT_CAPACITY}.")
            capacity = DEFAULT_CAPACITY

        # Re-create planner with chosen capacity
        self.planner = CourierPlanner(capacity)
        self.results = None

        try:
            print(f"\nLoading parcels from: {csv_path}")
            self.planner.load_parcels(csv_path)
            print(f"Loading delivery graph from: {DEFAULT_GRAPH_JSON}")
            self.planner.load_graph(DEFAULT_GRAPH_JSON)

            parcel_count = len(self.planner.parcel_manager.parcels)
            node_count   = len(self.planner.graph_manager.graph)
            print("\n--- Load Summary ---")
            print(f"  Dataset       : {self.current_dataset}")
            print(f"  Parcels loaded: {parcel_count}")
            print(f"  Graph nodes   : {node_count}")
            print(f"  Vehicle cap.  : {capacity} kg")
            print("--------------------")
            print("[✓] Data loaded successfully!")

        except FileNotFoundError as e:
            print(f"\n[ERROR] File not found: {e}")
            print("       Ensure data files exist in the 'data/' folder.")
        except Exception as e:
            print(f"\n[ERROR] Failed to load data: {e}")

    # ------------------------------------------------------------------
    # Option 2 — View Parcels
    # ------------------------------------------------------------------
    def handle_view_parcels(self):
        print("\n=== ALL LOADED PARCELS ===")
        if not self._require_data():
            return

        parcels = self.planner.parcel_manager.parcels
        header = (f"{'ID':<12} {'Name':<20} {'Weight':>8} {'Priority':>10} "
                  f"{'Deadline':<12} {'Dest':>6} {'Value':>8}")
        sep = "-" * len(header)
        print(header)
        print(sep)

        for p in parcels:
            print(f"{str(p.get('parcel_id','')):<12} "
                  f"{str(p.get('parcel_name','')):<20} "
                  f"{str(p.get('weight',''))!s:>8} "
                  f"{str(p.get('priority_score',''))!s:>10} "
                  f"{str(p.get('delivery_deadline','')):<12} "
                  f"{str(p.get('destination_node',''))!s:>6} "
                  f"{str(p.get('delivery_value',''))!s:>8}")

        print(sep)
        print(f"Total parcels: {len(parcels)}")

    # ------------------------------------------------------------------
    # Option 3 — Prioritize (Merge Sort)
    # ------------------------------------------------------------------
    def handle_prioritize(self):
        print("\n=== PRIORITIZE PARCELS (MERGE SORT) ===")
        if not self._require_data():
            return

        parcels = self.planner.parcel_manager.parcels
        print(f"\nSorting {len(parcels)} parcels by deadline → priority → value…")

        sorted_parcels, elapsed_ms = self.planner.prioritize_parcels()

        display_n = 10
        print(f"\n--- Original Order (first {min(display_n, len(parcels))}) ---")
        for p in parcels[:display_n]:
            print(f"  {p.get('parcel_id','')} | deadline={p.get('delivery_deadline','')} | "
                  f"priority={p.get('priority_score','')} | value={p.get('delivery_value','')}")

        print(f"\n--- Sorted Order (first {min(display_n, len(sorted_parcels))}) ---")
        for p in sorted_parcels[:display_n]:
            print(f"  {p.get('parcel_id','')} | deadline={p.get('delivery_deadline','')} | "
                  f"priority={p.get('priority_score','')} | value={p.get('delivery_value','')}")

        if len(sorted_parcels) > display_n:
            print(f"  … ({len(sorted_parcels) - display_n} more parcels not shown)")

        print(f"\n[✓] Merge Sort completed in {elapsed_ms:.4f} ms")

    # ------------------------------------------------------------------
    # Option 4 — Knapsack
    # ------------------------------------------------------------------
    def handle_knapsack(self):
        print("\n=== OPTIMIZE PACKAGE SELECTION (0/1 KNAPSACK) ===")
        if not self._require_data():
            return

        print(f"\nRunning 0/1 Knapsack with capacity={self.planner.capacity} kg…")
        result, elapsed_ms = self.planner.optimize_selection()

        # Store for downstream use
        if self.results is None:
            self.results = {}
        self.results["knapsack"] = result

        print("\n--- DP Table Preview ---")
        print(result.get("dp_table_preview", "N/A"))

        selected = result.get("selected", [])
        rejected = result.get("rejected", [])

        print("\n--- Selected Parcels ---")
        if selected:
            for p in selected:
                print(f"  [✓] {p.get('parcel_id','')} | weight={p.get('weight','')} | "
                      f"value={p.get('delivery_value','')} | dest={p.get('destination_node','')}")
        else:
            print("  None selected.")

        print("\n--- Rejected Parcels ---")
        if rejected:
            for p in rejected[:20]:
                print(f"  [✗] {p.get('parcel_id','')} | weight={p.get('weight','')} | "
                      f"value={p.get('delivery_value','')}")
            if len(rejected) > 20:
                print(f"  … ({len(rejected) - 20} more rejected parcels not shown)")
        else:
            print("  None rejected.")

        print("\n--- Statistics ---")
        print(f"  Total selected    : {len(selected)}")
        print(f"  Total rejected    : {len(rejected)}")
        print(f"  Total weight used : {result.get('total_weight', 0)} kg")
        print(f"  Remaining capacity: {result.get('remaining_capacity', 0)} kg")
        print(f"  Total value packed: {result.get('total_value', 0)}")
        print(f"  Execution time    : {elapsed_ms:.4f} ms")

    # ------------------------------------------------------------------
    # Option 5 — View Graph
    # ------------------------------------------------------------------
    def handle_view_graph(self):
        print("\n=== DELIVERY GRAPH ===")
        if not self._require_data():
            return

        graph = self.planner.graph_manager.graph
        nodes = list(graph.keys())
        print(f"\nNodes ({len(nodes)}): {', '.join(nodes)}")

        print("\n--- Edge List ---")
        edge_count = 0
        for node, neighbours in graph.items():
            for neighbour, dist in neighbours:
                print(f"  {node} ──[{dist}]──▶ {neighbour}")
                edge_count += 1

        print(f"\n--- Graph Summary ---")
        print(f"  Nodes : {len(nodes)}")
        print(f"  Edges : {edge_count}")
        avg_degree = edge_count / len(nodes) if nodes else 0
        print(f"  Avg degree: {avg_degree:.2f}")

    # ------------------------------------------------------------------
    # Option 6 — Shortest Paths (Dijkstra)
    # ------------------------------------------------------------------
    def handle_shortest_paths(self):
        print("\n=== SHORTEST PATHS (DIJKSTRA) ===")
        if not self._require_data():
            return

        # Determine target destinations
        if self.results and "knapsack" in self.results:
            selected = self.results["knapsack"].get("selected", [])
            destinations = list({p.get("destination_node") for p in selected
                                  if p.get("destination_node")})
            print(f"\nUsing destinations from selected parcels: {destinations}")
        else:
            parcels = self.planner.parcel_manager.parcels
            destinations = list({p.get("destination_node") for p in parcels
                                  if p.get("destination_node")})
            print(f"\nNo knapsack result found — using all destinations: {destinations}")

        if not destinations:
            print("[!] No destinations found.")
            return

        print("\nRunning Dijkstra from 'Depot'…")
        paths_result = self.planner.calculate_shortest_paths(destinations)

        if self.results is None:
            self.results = {}
        self.results["shortest_paths"] = paths_result

        print("\n--- Shortest Paths from Depot ---")
        for dest, info in paths_result.items():
            path = info.get("path", [])
            dist = info.get("distance", float("inf"))
            if path:
                print(f"  Depot → {dest}: {' → '.join(path)}  [distance: {dist}]")
            else:
                print(f"  Depot → {dest}: UNREACHABLE")

    # ------------------------------------------------------------------
    # Option 7 — Delivery Route (TSP)
    # ------------------------------------------------------------------
    def handle_delivery_route(self):
        print("\n=== OPTIMIZED DELIVERY ROUTE (TSP) ===")
        if not self._require_data():
            return

        print("\nRunning Nearest-Neighbour TSP approximation…")
        route_result = self.planner.generate_delivery_route()

        if self.results is None:
            self.results = {}
        self.results["tsp"] = route_result

        route    = route_result.get("route", [])
        segments = route_result.get("segments", [])
        total    = route_result.get("total_distance", 0)

        print("\n--- Delivery Route ---")
        if route:
            print("  " + " → ".join(route))
        else:
            print("  No route generated.")

        if segments:
            print("\n--- Segment Distances ---")
            for seg in segments:
                print(f"  {seg.get('from','')} → {seg.get('to','')}: {seg.get('distance', '?')} km")

        print(f"\n  Total route distance: {total} km")
        print(f"\n[✓] TSP route generated in {route_result.get('elapsed_ms', 0):.4f} ms")

    # ------------------------------------------------------------------
    # Option 8 — Complete Planning
    # ------------------------------------------------------------------
    def handle_complete_planning(self):
        print("\n=== RUN COMPLETE COURIER PLANNING ===")
        if not self._require_data():
            return

        print("\nRunning full pipeline: Sort → Knapsack → Dijkstra → TSP → Report")
        print("This may take a moment for large datasets…\n")

        try:
            self.results = self.planner.run_complete_planning()

            print("--- Step 1: Merge Sort ---")
            sort_res = self.results.get("sort", {})
            print(f"  Parcels sorted: {sort_res.get('count', 0)}  "
                  f"Time: {sort_res.get('elapsed_ms', 0):.4f} ms")

            print("\n--- Step 2: 0/1 Knapsack ---")
            ks = self.results.get("knapsack", {})
            print(f"  Selected: {len(ks.get('selected', []))}  "
                  f"Rejected: {len(ks.get('rejected', []))}  "
                  f"Value: {ks.get('total_value', 0)}  "
                  f"Weight: {ks.get('total_weight', 0)} kg")

            print("\n--- Step 3: Dijkstra Shortest Paths ---")
            sp = self.results.get("shortest_paths", {})
            for dest, info in sp.items():
                dist = info.get("distance", float("inf"))
                print(f"  Depot → {dest}: {dist}")

            print("\n--- Step 4: TSP Delivery Route ---")
            tsp = self.results.get("tsp", {})
            route = tsp.get("route", [])
            print(f"  Route: {' → '.join(route)}")
            print(f"  Total distance: {tsp.get('total_distance', 0)} km")

            print("\n--- Step 5: Report Generation ---")
            report_path = self.results.get("report_path", "")
            if report_path:
                print(f"  Report saved to: {report_path}")
            else:
                print("  Report path not available.")

            print("\n[✓] Complete planning finished successfully!")

        except Exception as e:
            print(f"\n[ERROR] Planning pipeline failed: {e}")

    # ------------------------------------------------------------------
    # Option 9 — Benchmarks
    # ------------------------------------------------------------------
    def handle_benchmarks(self):
        print("\n=== PERFORMANCE BENCHMARKS ===")
        print("Running benchmarks on all three datasets (small / medium / large).")
        print("This may take several seconds for the large dataset…\n")

        try:
            benchmark = PerformanceBenchmark(
                small_csv=DEFAULT_SMALL_CSV,
                medium_csv=DEFAULT_MEDIUM_CSV,
                large_csv=DEFAULT_LARGE_CSV,
                graph_json=DEFAULT_GRAPH_JSON,
            )
            bench_results = benchmark.run_full_benchmark()

            # Display timing table
            col_w = [12, 20, 12, 12, 12]
            header = (f"{'Dataset':<{col_w[0]}} {'Algorithm':<{col_w[1]}} "
                      f"{'Time (ms)':>{col_w[2]}} {'Complexity':<{col_w[3]}} {'Count':>{col_w[4]}}")
            sep = "-" * sum(col_w)
            print(header)
            print(sep)

            for row in bench_results:
                print(f"{str(row.get('dataset','')):<{col_w[0]}} "
                      f"{str(row.get('algorithm','')):<{col_w[1]}} "
                      f"{str(row.get('execution_time_ms',''))!s:>{col_w[2]}} "
                      f"{str(row.get('complexity','')):<{col_w[3]}} "
                      f"{str(row.get('parcel_count',''))!s:>{col_w[4]}}")

            print(sep)
            print(f"\n[✓] Benchmarks complete. {len(bench_results)} rows recorded.")

        except Exception as e:
            print(f"\n[ERROR] Benchmark failed: {e}")

    # ------------------------------------------------------------------
    # Option 10 — Charts
    # ------------------------------------------------------------------
    def handle_charts(self):
        print("\n=== GENERATE PERFORMANCE CHARTS ===")
        print("Generating charts from benchmark data…")

        try:
            benchmark = PerformanceBenchmark(
                small_csv=DEFAULT_SMALL_CSV,
                medium_csv=DEFAULT_MEDIUM_CSV,
                large_csv=DEFAULT_LARGE_CSV,
                graph_json=DEFAULT_GRAPH_JSON,
            )
            charts_dir = benchmark.generate_charts()
            print(f"\n[✓] Charts saved to: {charts_dir}")
            print("    Open the 'charts/' folder to view the PNG files.")

        except Exception as e:
            print(f"\n[ERROR] Chart generation failed: {e}")
            print("       Ensure matplotlib is installed: pip install matplotlib")

    # ------------------------------------------------------------------
    # Option 11 — View Report
    # ------------------------------------------------------------------
    def handle_view_report(self):
        print("\n=== FINAL DELIVERY REPORT ===")
        report_path = os.path.join(BASE_DIR, "reports", "final_delivery_report.txt")

        if not os.path.exists(report_path):
            print(f"[!] Report not found at: {report_path}")
            print("    Run Option 8 (Complete Planning) first to generate the report.")
            return

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()

            if content.strip():
                print(content)
            else:
                print("[!] Report file is empty. Run Option 8 to generate content.")

        except Exception as e:
            print(f"\n[ERROR] Could not read report: {e}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    SmartCourierApp().run()
