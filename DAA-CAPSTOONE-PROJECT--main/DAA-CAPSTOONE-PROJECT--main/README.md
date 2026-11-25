 # SMART COURIER: Intelligent Parcel Packing & Route Optimization System

> **B.Tech Design and Analysis of Algorithms (DAA) Capstone Project**  
> A complete, working Python application integrating Sorting Algorithms, Dynamic Programming, Graph Algorithms, Shortest Path Algorithms, TSP Approximation Techniques, and Empirical Runtime Analysis.

---

## 1. Problem Statement

Modern logistics and courier companies face two fundamental computational challenges daily:

1. **Parcel Prioritization & Selection (Packing Problem):** With hundreds of parcels possessing distinct deadlines, priority tiers, weights, and values, which optimal subset should be loaded into a vehicle with strict weight capacity limits to maximize total delivered value?
2. **Delivery Route Optimization (Routing Problem):** In what optimal sequence should delivery destinations be visited to minimize fuel consumption, driver travel time, and total transit distance before returning to the central distribution hub?

Both problems belong to classical computational complexity classes: the 0/1 Knapsack problem is NP-complete, and the Travelling Salesman Problem (TSP) is NP-hard. This application provides real, non-trivial, and mathematically rigorous algorithmic solutions executed dynamically on real input datasets.

---

## 2. Project Objectives

- **Algorithmic Correctness:** Implement pure algorithmic implementations from scratch without external black-box algorithm libraries.
- **End-to-End Modular Integration:** Connect parcel sorting, knapsack selection, shortest path extraction, and TSP routing into a single interactive terminal application.
- **Empirical Scalability Benchmarking:** Rigorously test and measure algorithm runtimes across Small (15 items), Medium (150 items), and Large (700 items) datasets.
- **Academic Standard Documentation:** Provide formal time and space complexity evaluations, mathematical formulations, and visual performance charts for viva and presentation evaluation.

---

## 3. Features

- **Interactive Terminal Interface:** Clean, robust 11-option terminal menu with graceful input validation.
- **Stable 3-Tier Merge Sort:** Sorts parcels by earliest deadline $\rightarrow$ highest priority score $\rightarrow$ highest delivery value.
- **Bottom-Up 0/1 Knapsack Dynamic Programming:** Computes the global optimum without fractional packing, complete with 2D DP table construction and backtracking.
- **Dijkstra's Algorithm with Min-Heap Priority Queue:** Computes shortest road network paths ($O((V+E)\log V)$) using `heapq`, handling multi-hop road networks.
- **Nearest Neighbor TSP Approximation:** Computes an approximate closed-loop delivery tour returning to the depot.
- **Automated Performance Benchmarking:** Computes median runtimes across repeated trials, saving results to CSV and structured text reports.
- **High-Resolution Visualizations:** Matplotlib charts illustrating runtime scaling and comparative performance.
- **Automated Comprehensive Reporting:** Detailed dispatch manifests containing packed parcels, rejected items, vehicle utilization, step-by-step route legs, and runtime breakdowns.

---

## 4. Technologies Used

| Category | Technology | Usage |
|---|---|---|
| **Programming Language** | Python 3.10+ | Core application logic and algorithms |
| **Data Structures** | Custom / Built-in (`heapq`, lists, dicts) | Min-priority queues, graphs, DP tables |
| **Data Formats** | CSV & JSON | Parcel manifests and road network definitions |
| **Visualization** | Matplotlib (Agg backend) | Performance comparison charts |
| **Runtime Benchmarking**| `time.perf_counter()` | Sub-millisecond timing measurements |
| **Testing Framework** | `unittest` / `pytest` | 38 automated test cases |

---

## 5. System Architecture
smart-courier/ ├── main.py # Interactive terminal UI ├── requirements.txt # Python dependencies ├── README.md # Project documentation │ ├── algorithms/ # Pure algorithm implementations │ ├── init.py │ ├── sorting.py # Merge Sort & Timsort comparison │ ├── knapsack.py # 0/1 Knapsack DP & Backtracking │ ├── dijkstra.py # Dijkstra with heapq │ └── tsp.py # Nearest Neighbor TSP heuristic │ ├── core/ # Business logic and management │ ├── init.py │ ├── parcel_manager.py # CSV validation and ingestion │ ├── graph_manager.py # Graph adjacency list & BFS checks │ ├── courier_planner.py # Pipeline coordinator & reporter │ └── performance.py # Benchmarking & chart generator │ ├── data/ # Benchmark datasets │ ├── parcels_small.csv # 15 parcels │ ├── parcels_medium.csv # 150 parcels │ ├── parcels_large.csv # 700 parcels │ └── delivery_graph.json # 9-node, 20-edge weighted graph │ ├── reports/ # Generated reports │ ├── runtime_results.csv # Raw benchmark timings │ ├── performance_report.txt # Algorithmic analysis report │ └── final_delivery_report.txt # Final delivery manifest │ ├── charts/ # Performance visual charts │ ├── sorting_comparison.png │ ├── knapsack_performance.png │ ├── dijkstra_performance.png │ ├── tsp_performance.png │ └── overall_runtime_comparison.png │ ├── screenshots/actual_application_outputs/ # Captured execution outputs │ └── tests/ # Unit and integration tests ├── init.py ├── test_sorting.py ├── test_knapsack.py ├── test_dijkstra.py ├── test_tsp.py └── test_integration.py

---
## 6. System Workflow Diagram
 [Raw Parcel CSV]                 [Delivery Graph JSON]
          │                                   │
          ▼                                   ▼
   ParcelManager                        GraphManager
 (Input Validation)                 (Adjacency List Build)
          │                                   │
          ▼                                   │
 ┌─────────────────┐                          │
 │   Merge Sort    │                          │
 │  O(n log n)     │                          │
 └────────┬────────┘                          │
          │ (Prioritized Parcel List)         │
          ▼                                   │
 ┌─────────────────┐                          │
 │  0/1 Knapsack   │                          │
 │     DP Table    │                          │
 │    O(n × W)     │                          │
 └────────┬────────┘                          │
          │ (Optimal Packed Manifest)         │
          ▼                                   ▼
 ┌─────────────────────────────────────────────────┐
 │             Dijkstra's Algorithm                │
 │              O((V + E) log V)                   │
 │   Computes Shortest Pairwise Distance Matrix    │
 └────────────────────────┬────────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Nearest       │
                 │  Neighbor TSP   │
                 │     O(k²)       │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Final Delivery  │
                 │ Route & Reports │
                 └─────────────────┘
---
## 7. Data Structures Used
| Data Structure | Implementation | Algorithm / Component | Justification |
|---|---|---|---|
| **2D Dynamic Table** | `list[list[int]]` | 0/1 Knapsack DP | Enables $O(1)$ state lookups and backwards tracing for selected parcels. |
| **Min-Priority Queue** | `heapq` (Binary Heap) | Dijkstra's Algorithm | Guarantees $O(\log V)$ extraction of minimum tentative distance node. |
| **Adjacency List** | `dict[str, list[tuple]]` | Graph Representation | Efficient $O(1)$ vertex lookup and $O(\text{deg}(u))$ neighbor traversal for sparse road maps. |
| **Distance Matrix** | `dict[str, dict[str, float]]` | TSP Approximation | $O(1)$ lookup for nearest neighbor heuristic selection between visited stops. |
| **Queue** | `collections.deque` | Graph Validation (BFS) | $O(V + E)$ verification that all delivery locations are reachable from the Depot. |
---
## 8. Algorithm Explanations
### A. Merge Sort (Parcel Prioritization)
- **Principle:** Divide-and-conquer strategy recursively bisecting parcels into singletons and merging them in sorted order.
- **Comparison Rule:**
  1. Primary: Earlier `delivery_deadline` first (chronological string comparison).
  2. Secondary: Higher `priority_score` (1–10 descending).
  3. Tertiary: Higher `delivery_value` (descending).
- **Stability:** Merge Sort preserves original order of identical elements, preventing deadline jitter.
### B. 0/1 Knapsack Dynamic Programming (Optimal Box Packing)
- **Principle:** Given vehicle weight capacity $W$ and $n$ parcels each with weight $w_i$ and value $v_i$, determine the binary decision vector $x_i \in \{0, 1\}$ that maximizes $\sum v_i x_i$ subject to $\sum w_i x_i \le W$.
- **State Recurrence:**
  $$\text{DP}[i][w] = \begin{cases} \text{DP}[i-1][w] & \text{if } w_i > w \\ \max(\text{DP}[i-1][w], \text{DP}[i-1][w - w_i] + v_i) & \text{otherwise} \end{cases}$$
- **Backtracking:** Traces from $\text{DP}[n][W]$ backwards to identify whether item $i$ was included ($\text{DP}[i][w] \neq \text{DP}[i-1][w]$).
### C. Dijkstra’s Algorithm (Shortest Path Finding)
- **Principle:** Greedy approach tracking the shortest known distance from the Depot to all vertices using edge relaxation.
- **Heap Invariant:** The min-heap stores `(tentative_distance, node)`. Visited nodes are finalized, skipping outdated duplicate entries in $O((V+E)\log V)$ time.
### D. Nearest Neighbor TSP Approximation (Delivery Route)
- **Principle:** Starting at the Depot, the courier iteratively advances to the closest unvisited delivery node based on Dijkstra-computed shortest road distances.
- **Tour Completion:** Once all selected delivery destinations are visited, the courier returns directly to the Depot, completing a full round-trip route.
---
## 9. Time and Space Complexity Analysis
| Algorithm | Role | Time Complexity | Space Complexity | Practical Limitations |
|---|---|---|---|---|
| **Merge Sort** | Prioritization | $O(n \log n)$ | $O(n)$ | Requires auxiliary memory for merging. |
| **Python `sorted()`** | Comparison | $O(n \log n)$ | $O(n)$ | Highly optimized C-level Timsort. |
| **0/1 Knapsack DP** | Parcel Packing | $O(n \cdot W)$ | $O(n \cdot W)$ | Pseudo-polynomial; large capacities increase table memory. |
| **Dijkstra (Heap)** | Shortest Paths | $O((V + E) \log V)$ | $O(V)$ | Negative edge weights are not allowed. |
| **Nearest Neighbor** | Route Tour | $O(k^2)$ | $O(k)$ | Heuristic upper bound ~20–25% above true optimal tour. |
---
## 10. Installation & Execution Guide
### Windows Setup
1. **Open PowerShell / Command Prompt:**
   ```powershell
   cd "c:\Users\Anubhav\Desktop\DAA CAPSTONE\smart-courier"

Create and Activate Virtual Environment:

powershell
python -m venv .venv
.venv\Scripts\activate

Install Dependencies:

powershell
pip install -r requirements.txt

Run Terminal Application:

powershell
python main.py

Run All Unit & Integration Tests:

powershell
python -m unittest discover -s tests -v
11. Empirical Benchmark Results

Measured on Windows using time.perf_counter():

Dataset	Parcels (
𝑛
n)	Nodes (
𝑉
V)	Vehicle Capacity (
𝑊
W)	Merge Sort (ms)	Builtin Sort (ms)	Knapsack 0/1 (ms)	Dijkstra (ms)	TSP NN (ms)
Small	15	9	51 kg	0.044 ms	0.006 ms	0.595 ms	0.031 ms	0.027 ms
Medium	150	9	1,205 kg	0.614 ms	0.064 ms	89.638 ms	0.053 ms	0.037 ms
Large	700	9	6,562 kg	3.732 ms	0.405 ms	3,078.074 ms	0.072 ms	0.032 ms
Key Observations:
Knapsack Scaling: Runtimes scale from 0.595 ms to 3,078 ms (~5,168× increase), confirming the 
𝑂
(
𝑛
⋅
𝑊
)
O(n⋅W) pseudo-polynomial complexity as both 
𝑛
n and 
𝑊
W expand.
Sorting Efficiency: Merge Sort processes 700 items in 3.73 ms, maintaining consistent 
𝑂
(
𝑛
log
⁡
𝑛
)
O(nlogn) scaling.
Graph Operations: Dijkstra and Nearest Neighbor execute in under 0.1 ms, confirming the efficiency of min-heap and adjacency list indexing.
12. Limitations & Future Scope
Limitations
Single-Vehicle Constraint: Models dispatch for one delivery vehicle rather than a heterogeneous fleet.
Static Distances: Graph edge weights represent fixed road distances without dynamic traffic congestion.
Pseudo-Polynomial Memory: 0/1 Knapsack DP table memory scales with vehicle weight capacity 
𝑊
W.
Future Scope
Capacitated Vehicle Routing Problem (CVRP): Extending routing to multi-vehicle fleet coordination.
Live Traffic Telemetry: Integrating Google Maps Distance Matrix API for dynamic edge weighting.
Genetic Algorithms & 2-Opt: Post-processing TSP tours with local search optimizations.
13. Academic Conclusion

The SMART COURIER system demonstrates how foundational Data Structures and Algorithms coalesce to solve complex logistics problems. The system provides mathematically optimal parcel packing via Dynamic Programming, reliable route generation via Dijkstra and TSP approximations, and empirical verification confirming theoretical time-complexity models.
