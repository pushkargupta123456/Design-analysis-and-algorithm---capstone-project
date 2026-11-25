import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import tempfile

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PARCELS_SMALL = os.path.join(DATA_DIR, 'parcels_small.csv')
GRAPH_FILE = os.path.join(DATA_DIR, 'delivery_graph.json')

VEHICLE_CAPACITY = 50  # default capacity used by the pipeline


class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run the full pipeline once and cache the result."""
        from core.courier_planner import run_complete_pipeline
        cls.result = run_complete_pipeline(
            parcels_csv=PARCELS_SMALL,
            graph_json=GRAPH_FILE,
            vehicle_capacity=VEHICLE_CAPACITY,
        )

    def test_full_pipeline(self):
        """run_complete_pipeline returns a dict with all expected keys."""
        required_keys = ['sorted_parcels', 'knapsack_result', 'shortest_paths', 'tsp_result']
        for key in required_keys:
            self.assertIn(key, self.result,
                          f"Missing key '{key}' in pipeline result")

    def test_selected_parcels_within_capacity(self):
        """Knapsack total_weight must not exceed vehicle capacity."""
        knapsack = self.result['knapsack_result']
        self.assertLessEqual(knapsack['total_weight'], VEHICLE_CAPACITY)

    def test_shortest_paths_valid(self):
        """All destinations of selected parcels must appear in shortest_paths."""
        knapsack = self.result['knapsack_result']
        shortest_paths = self.result['shortest_paths']
        selected = knapsack.get('selected', [])
        destinations = {p['destination_node'] for p in selected}
        for dest in destinations:
            self.assertIn(dest, shortest_paths,
                          f"Destination '{dest}' missing from shortest_paths")

    def test_route_visits_all_destinations(self):
        """TSP route must visit all reachable selected destinations."""
        tsp = self.result['tsp_result']
        route = tsp['route']
        unreachable = set(tsp.get('unreachable_nodes', []))
        knapsack = self.result['knapsack_result']
        selected = knapsack.get('selected', [])
        reachable_dests = {p['destination_node'] for p in selected} - unreachable
        for dest in reachable_dests:
            self.assertIn(dest, route,
                          f"Reachable destination '{dest}' not in TSP route")

    def test_total_distance_positive(self):
        """TSP total distance should be > 0 when there are deliveries."""
        tsp = self.result['tsp_result']
        knapsack = self.result['knapsack_result']
        if knapsack.get('selected'):
            self.assertGreater(tsp['total_distance'], 0)

    def test_report_generated(self):
        """generate_report creates a non-empty file."""
        from core.courier_planner import generate_report
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
            report_path = f.name
        try:
            generate_report(self.result, output_path=report_path)
            self.assertTrue(os.path.exists(report_path))
            self.assertGreater(os.path.getsize(report_path), 0)
        finally:
            if os.path.exists(report_path):
                os.remove(report_path)


if __name__ == '__main__':
    unittest.main()
