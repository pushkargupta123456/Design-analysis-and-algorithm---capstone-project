# SMART COURIER: Intelligent Parcel Packing & Route Optimization System

> **B.Tech Design and Analysis of Algorithms (DAA) Capstone Project**  
> A complete, working demonstration of five core algorithms applied to a realistic courier-logistics domain.

---

## Problem Statement

Modern courier companies handle hundreds of parcels daily. Two fundamental challenges arise:

1. **Which parcels should be loaded** onto a vehicle of limited weight capacity to maximise delivery value?
2. **In what order should stops be visited** to minimise total travel distance?

Both problems are NP-hard in the general case. This project implements classical algorithmic solutions — merge sort, 0/1 knapsack, Dijkstra's shortest path, and a nearest-neighbour TSP approximation — and benchmarks them across small, medium, and large real-looking datasets to study real-world performance behaviour.

---

## Project Objectives

- Implement five algorithms from scratch in Python (no third-party algorithm libraries).
- Apply those algorithms end-to-end in a believable logistics pipeline.
- Demonstrate time/space complexity analysis with empirical benchmarks.
- Produce a clean, menu-driven terminal application that a non-technical evaluator can run.
- Generate visual performance charts and a human-readable delivery report.

---

## Features

- **Interactive terminal menu** with 11 functions accessible via number keys.
- **Merge Sort** – stable sort of parcel list by deadline, priority, and delivery value.
- **0/1 Knapsack DP** – optimal parcel selection under vehicle weight limit.
- **Dijkstra's Algorithm** – shortest road path from Depot to every delivery stop.
- **TSP Nearest-Neighbour Heuristic** – practical route that visits all stops and returns to Depot.
- **Performance Benchmarks** – automated timing across small / medium / large datasets.
- **Matplotlib Charts** – bar and line plots of execution time vs. dataset size.
- **Auto-generated Delivery Report** – text report saved to `reports/final_delivery_report.txt`.
- **Three dataset sizes** – 15, 150, and 700 parcels for scalability analysis.
- **Fully modular codebase** – algorithms, core managers, and UI cleanly separated.

---

## Technologies Used

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Algorithm library | Custom (stdlib only) |
| Priority queue | `heapq` (stdlib) |
| Data files | CSV (parcels) + JSON (graph) |
| Charting | `matplotlib` |
| Testing | `pytest` |
| OS | Windows (runs on Linux/macOS too) |

---

## System Architecture

```
smart-courier/
│
├── main.py                     ← Entry point & UI (SmartCourierApp)
│
├── algorithms/                 ← Pure algorithm implementations
│   ├── sorting.py              ← merge_sort, builtin_sort, timed_sort
│   ├── knapsack.py             ← knapsack_01, dp table, timed_knapsack
│   ├── dijkstra.py             ← dijkstra, reconstruct_path, shortest_path_info
│   └── tsp.py                  ← nearest_neighbour_tsp, timed_tsp
│
├── core/                       ← Orchestration & data management
│   ├── courier_planner.py      ← CourierPlanner — wires all algorithms together
│   ├── graph_manager.py        ← GraphManager  — load/query adjacency list
│   ├── parcel_manager.py       ← ParcelManager — load/filter parcels from CSV
│   └── performance.py          ← PerformanceBenchmark — timing + chart generation
│
├── data/                       ← Input files (CSV + JSON)
│   ├── parcels_small.csv
│   ├── parcels_medium.csv
│   ├── parcels_large.csv
│   └── delivery_graph.json
│
├── reports/                    ← Generated text output
│   ├── final_delivery_report.txt
│   ├── performance_report.txt
│   └── runtime_results.csv
│
├── charts/                     ← Generated PNG charts
├── tests/                      ← pytest unit tests
└── requirements.txt
```

---

## Workflow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                        SMART COURIER PIPELINE                        │
└──────────────────────────────────────────────────────────────────────┘

  [CSV Input]          [JSON Graph]
       │                    │
       ▼                    ▼
  ParcelManager       GraphManager
  (load parcels)      (build adjacency list)
       │
       ▼
  ┌─────────────────┐
  │   Merge Sort    │  ← Sort parcels by deadline / priority / value
  │  O(n log n)     │
  └────────┬────────┘
           │  sorted parcel list
           ▼
  ┌─────────────────┐
  │  0/1 Knapsack   │  ← Select best parcels under weight capacity
  │  O(n × W)       │
  └────────┬────────┘
           │  selected parcels + destination set
           ▼
  ┌─────────────────┐
  │   Dijkstra      │  ← Shortest road path: Depot → each destination
  │  O((V+E) log V) │
  └────────┬────────┘
           │  distance matrix between stops
           ▼
  ┌─────────────────┐
  │  TSP Heuristic  │  ← Nearest-Neighbour tour of all stops
  │  O(V²)          │
  └────────┬────────┘
           │  final ordered route
           ▼
  ┌─────────────────┐
  │  Report + Charts│  ← Save delivery report & performance plots
  └─────────────────┘
```

---

## Data Structures Used

| Structure | Where | Why |
|-----------|-------|-----|
| **List of dicts** | Parcel storage | Simple, CSV-compatible, easy iteration |
| **2-D list (DP table)** | Knapsack | Standard bottom-up DP requires indexed rows/cols |
| **Adjacency list** (`dict` of `list`) | Graph | Sparse road graph; O(1) lookup of neighbours |
| **Min-heap** (`heapq`) | Dijkstra | Extract minimum-distance node in O(log V) |
| **Dictionary** | Dijkstra distances & predecessors | O(1) distance lookup by node name |
| **Stack (list)** | Path reconstruction | Reverse predecessor chain to get path |

---

## Algorithm Explanations

### 1. Merge Sort — `algorithms/sorting.py`

Merge sort is a **divide-and-conquer** algorithm. It recursively splits the list in half until each sub-list has one element, then **merges** sorted halves back together. During each merge, elements are compared and placed in the correct order.

For this project, parcels are sorted first by **delivery deadline** (earlier = higher priority), then by **priority score** (descending), then by **delivery value** (descending) as a tie-breaker.

### 2. 0/1 Knapsack — `algorithms/knapsack.py`

The vehicle can carry at most **W kg**. Each parcel has a weight and a delivery value. We want to pick a subset of parcels that fits in the vehicle and **maximises total value** — without splitting parcels (hence "0/1": either take it or leave it).

**Dynamic Programming approach:** build a table `dp[i][w]` = maximum value achievable using the first `i` parcels with a weight limit of `w`. Each cell is filled in O(1) using the recurrence:

```
dp[i][w] = max(dp[i-1][w],                    # don't take parcel i
               dp[i-1][w - weight[i]] + value[i])  # take parcel i (if it fits)
```

Backtracking through the table recovers which parcels were selected.

### 3. Dijkstra's Algorithm — `algorithms/dijkstra.py`

Finds the shortest road distance from the **Depot** to every other node in the graph. It maintains a **priority queue** of (distance, node) pairs. At each step it extracts the closest unvisited node, then **relaxes** (updates) the distances to its neighbours if a shorter path is found.

The algorithm terminates when every reachable node has been settled.

### 4. TSP Nearest-Neighbour Heuristic — `algorithms/tsp.py`

The Travelling Salesman Problem asks for the shortest tour that visits every stop exactly once and returns to the start. This is NP-hard, so an **exact** solution is infeasible for more than ~20 nodes.

The **nearest-neighbour heuristic** is a greedy approximation: start at the Depot, always move to the **closest unvisited stop** (using Dijkstra distances as edge weights), repeat until all stops are visited, then return to Depot. This typically gives a tour within 20–25 % of optimal in O(V²) time.

### 5. Merge vs. Insertion Sort (Benchmark Comparison)

The benchmark module also times Python's built-in `sorted()` (Timsort) against the custom merge sort to show that the theoretical complexity difference (both O(n log n)) translates to a small but consistent constant-factor difference in practice.

---

## Time and Space Complexity Table

| Algorithm | Time Complexity | Space Complexity | Notes |
|-----------|----------------|-----------------|-------|
| **Merge Sort** | O(n log n) | O(n) | Stable; n = parcel count |
| **0/1 Knapsack** | O(n × W) | O(n × W) | n = parcels, W = capacity |
| **Dijkstra (heap)** | O((V + E) log V) | O(V) | V = nodes, E = edges |
| **TSP Nearest-Neighbour** | O(V²) | O(V) | Heuristic, not optimal |
| **Benchmarking loop** | O(D × A) | O(1) | D = datasets, A = algorithms |

---

## Installation Instructions

> Requirements: **Python 3.10 or later**, **pip**, Windows terminal (CMD or PowerShell).

```bat
:: 1. Navigate to the project folder
cd "c:\Users\Anubhav\Desktop\DAA CAPSTONE\smart-courier"

:: 2. Create a virtual environment
python -m venv venv

:: 3. Activate it
venv\Scripts\activate

:: 4. Install dependencies
pip install -r requirements.txt
```

**requirements.txt** contains:
```
matplotlib>=3.7.0
pytest>=7.4.0
```

---

## Quick Start / Execution Steps

```bat
:: Make sure the venv is active (see Installation above)
python main.py
```

Recommended walkthrough for evaluation:

| Step | Menu Option | What to do |
|------|------------|------------|
| 1 | **1** | Load the **Small** dataset, accept default capacity |
| 2 | **2** | View the loaded parcels |
| 3 | **3** | Run Merge Sort — observe sorted order & timing |
| 4 | **4** | Run 0/1 Knapsack — see DP table, selected/rejected parcels |
| 5 | **5** | View the delivery graph nodes and edges |
| 6 | **6** | Run Dijkstra — see shortest paths to each destination |
| 7 | **7** | Run TSP — see the final delivery route |
| 8 | **8** | Run everything end-to-end, generate report |
| 9 | **9** | Run benchmarks across all three dataset sizes |
| 10 | **10** | Generate and save performance charts |
| 11 | **11** | View the final delivery report |

---

## Sample Input Format

### parcels_small.csv

```csv
parcel_id,parcel_name,weight,priority_score,delivery_deadline,destination_node,delivery_value
P001,Electronics Box,5,9,2024-01-10,A,450
P002,Clothing Bundle,3,6,2024-01-12,B,120
P003,Medical Supplies,8,10,2024-01-08,C,500
P004,Books Pack,4,4,2024-01-15,A,80
P005,Fragile Glassware,6,7,2024-01-11,D,200
```

### delivery_graph.json

```json
{
  "nodes": ["Depot", "A", "B", "C", "D", "E", "F", "G", "H"],
  "edges": [
    {"from": "Depot", "to": "A", "distance": 5},
    {"from": "Depot", "to": "B", "distance": 8},
    {"from": "A",     "to": "C", "distance": 4},
    {"from": "B",     "to": "D", "distance": 6},
    {"from": "C",     "to": "E", "distance": 3},
    {"from": "D",     "to": "F", "distance": 7}
  ]
}
```

---

## Algorithm Analysis

### Why Merge Sort and not Quick Sort?

Merge sort is **stable** — parcels with the same deadline retain their relative order, which matters when secondary and tertiary keys (priority, value) must also be respected. Quick sort's worst-case O(n²) on nearly-sorted data is also a risk in production scheduling contexts.

### Why 0/1 Knapsack and not Greedy?

A greedy strategy (pick by value/weight ratio) fails to find the globally optimal subset. The 0/1 DP always finds the **exact optimum**. The trade-off is O(n × W) pseudo-polynomial time, which is acceptable for n ≤ 700 and W ≤ 300.

### Why Dijkstra and not Bellman-Ford?

The road graph has **non-negative** edge weights (distances are always positive). Dijkstra runs in O((V + E) log V) with a binary heap, whereas Bellman-Ford is O(V × E) — significantly slower for dense graphs.

### Why Nearest-Neighbour TSP and not Brute-Force?

Brute-force TSP is O(n!). For 10 stops that is 3.6 million permutations; for 15 stops it's 1.3 trillion. Nearest-neighbour delivers a good-enough tour in O(V²), making it practical within seconds even for 36 nodes.

---

## Runtime Analysis

Actual empirical benchmark results obtained by executing the implemented algorithms across all datasets on Windows:

| Dataset | Parcel Count | Nodes | Vehicle Capacity | Merge Sort (ms) | Builtin Sort (ms) | Knapsack 0/1 (ms) | Dijkstra (ms) | TSP NN (ms) |
|---|---|---|---|---|---|---|---|---|
| **Small** | 15 | 9 | 51 kg | 0.044 ms | 0.006 ms | 0.595 ms | 0.031 ms | 0.027 ms |
| **Medium** | 150 | 9 | 1,205 kg | 0.614 ms | 0.064 ms | 89.638 ms | 0.053 ms | 0.037 ms |
| **Large** | 700 | 9 | 6,562 kg | 3.732 ms | 0.405 ms | 3,078.074 ms | 0.072 ms | 0.032 ms |

### Key Observations & Bottleneck Analysis:
1. **Knapsack DP dominates runtime**: Knapsack execution time grows from **0.595 ms to 3,078 ms** (~5,168× increase). This directly confirms the theoretical pseudo-polynomial time complexity **O(n × W)** as both parcel count $n$ and vehicle capacity $W$ scale.
2. **Merge Sort scales gracefully**: Increases from **0.044 ms to 3.732 ms**, confirming the **O(n log n)** divide-and-conquer complexity. Python's built-in Timsort is roughly 7–10× faster due to C-level optimizations (`PyList_Sort`).
3. **Dijkstra & TSP scale with graph size**: Dijkstra runs in **< 0.1 ms** with a min-heap priority queue ($O((V+E)\log V)$), and Nearest-Neighbor TSP approximation computes in **< 0.04 ms** ($O(k^2)$ on the distance matrix).

---

## Visual Evidence, Charts & Screenshots

All charts and screenshots were dynamically generated from actual application runs:

### Performance Charts (`charts/`):
- `charts/sorting_comparison.png` — Merge Sort vs. Python Built-in Sort (median of 5 runs).
- `charts/knapsack_performance.png` — 0/1 Knapsack runtime scaling across dataset capacities.
- `charts/dijkstra_performance.png` — Dijkstra shortest-path computation time.
- `charts/tsp_performance.png` — TSP Nearest Neighbor execution time.
- `charts/overall_runtime_comparison.png` — Side-by-side runtime comparison of all four algorithms.

### Actual Application Output Screenshots (`screenshots/actual_application_outputs/`):
- `main_menu.png` — Main application interactive menu.
- `sorted_parcels.png` — Merge sort prioritized parcel output (original vs. sorted).
- `knapsack_dp_selection.png` — 0/1 Knapsack DP table preview, selected/rejected items, packed stats.
- `delivery_graph_info.png` — Graph nodes, weighted edge list, connectivity summary.
- `dijkstra_shortest_paths.png` — Dijkstra shortest paths and travel distances from Depot.
- `tsp_delivery_route.png` — Nearest Neighbor approximate TSP tour with segment distances.
- `complete_courier_planning.png` — Automated end-to-end planning workflow execution.
- `benchmark_results.png` — Benchmark execution table across all three datasets.
- `final_delivery_report.png` — Generated final delivery report.
- `session_full_run.txt` — Full terminal session log with all 11 menu options executed.

---

## Project Structure

```
smart-courier/
├── main.py
├── requirements.txt
├── README.md
│
├── algorithms/
│   ├── __init__.py
│   ├── sorting.py
│   ├── knapsack.py
│   ├── dijkstra.py
│   └── tsp.py
│
├── core/
│   ├── __init__.py
│   ├── courier_planner.py
│   ├── graph_manager.py
│   ├── parcel_manager.py
│   └── performance.py
│
├── data/
│   ├── parcels_small.csv
│   ├── parcels_medium.csv
│   ├── parcels_large.csv
│   └── delivery_graph.json
│
├── reports/
│   ├── final_delivery_report.txt
│   ├── performance_report.txt
│   └── runtime_results.csv
│
├── charts/
│   ├── sorting_comparison.png
│   ├── knapsack_performance.png
│   ├── dijkstra_performance.png
│   ├── tsp_performance.png
│   └── overall_runtime_comparison.png
│
├── screenshots/
│   └── actual_application_outputs/
│       ├── main_menu.png
│       ├── sorted_parcels.png
│       ├── knapsack_dp_selection.png
│       ├── delivery_graph_info.png
│       ├── dijkstra_shortest_paths.png
│       ├── tsp_delivery_route.png
│       ├── complete_courier_planning.png
│       ├── benchmark_results.png
│       ├── final_delivery_report.png
│       └── session_full_run.txt
│
└── tests/
    ├── __init__.py
    ├── test_sorting.py
    ├── test_knapsack.py
    ├── test_dijkstra.py
    ├── test_tsp.py
    └── test_integration.py
```

---

## Limitations

- **TSP is a heuristic** — the nearest-neighbour route is not guaranteed to be optimal. It may be 10–25 % longer than the true optimum.
- **Knapsack pseudo-polynomial complexity** — if capacity W is very large (e.g., 100 000 kg), memory usage for the DP table becomes impractical.
- **Single vehicle** — the system does not model a fleet. All parcels that fit must go on one truck.
- **Static graph** — road distances are fixed; real-time traffic or road closures are not modelled.
- **No GUI** — the interface is entirely text-based; no map visualisation is provided.
- **CSV/JSON only** — no database backend; data is loaded fresh on each run.

---

## Future Scope

- **Multi-vehicle routing** — extend to Vehicle Routing Problem (VRP) with a fleet of trucks.
- **Dynamic traffic weighting** — integrate a live maps API (e.g., Google Maps Distance Matrix) for real-time edge weights.
- **Exact TSP for small instances** — add branch-and-bound or dynamic-programming TSP (O(2ⁿ × n)) for ≤ 20 nodes.
- **Web dashboard** — replace terminal UI with a Flask/FastAPI + React dashboard showing an interactive map.
- **ML-based priority scoring** — train a classifier to auto-assign priority scores based on historical delivery data.
- **Database integration** — persist parcels, routes, and reports to PostgreSQL for multi-session tracking.
- **Real-time delivery tracking** — WebSocket updates as the courier marks stops as delivered.

---

## Conclusion

The SMART COURIER system demonstrates that classical algorithms — merge sort, 0/1 knapsack DP, Dijkstra, and a TSP heuristic — can be composed into a coherent, practical application. The empirical benchmarks confirm the theoretical time complexities: Knapsack's O(n × W) is the dominant bottleneck, Dijkstra scales efficiently even on larger graphs, and merge sort comfortably handles 700-parcel lists in milliseconds.

The project fulfils the Design and Analysis of Algorithms capstone requirements by implementing algorithms from scratch, analysing their complexity, benchmarking them empirically, and presenting the results in a clean, evaluator-friendly terminal interface.

---

*Developed as part of the B.Tech DAA Capstone — Academic Year 2024–25.*
