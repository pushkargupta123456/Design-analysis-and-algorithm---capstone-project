import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import unittest
from algorithms.tsp import nearest_neighbor_tsp, build_distance_matrix


class TestTSP(unittest.TestCase):

    def _simple_dist_matrix(self):
        """Distance matrix for Depot, A, B, C, D."""
        nodes = ['Depot', 'A', 'B', 'C', 'D']
        # symmetric matrix with known values
        dist = {
            'Depot': {'Depot': 0, 'A': 5, 'B': 8, 'C': 12, 'D': 15},
            'A':     {'Depot': 5, 'A': 0, 'B': 3, 'C': 7,  'D': 10},
            'B':     {'Depot': 8, 'A': 3, 'B': 0, 'C': 4,  'D': 7},
            'C':     {'Depot': 12,'A': 7, 'B': 4, 'C': 0,  'D': 5},
            'D':     {'Depot': 15,'A': 10,'B': 7, 'C': 5,  'D': 0},
        }
        return dist, nodes

    def test_single_destination(self):
        dist, _ = self._simple_dist_matrix()
        result = nearest_neighbor_tsp('Depot', ['A'], dist)
        route = result['route']
        self.assertEqual(route[0], 'Depot')
        self.assertEqual(route[-1], 'Depot')
        self.assertIn('A', route)
        self.assertEqual(len(route), 3)  # Depot → A → Depot

    def test_multiple_destinations(self):
        dist, _ = self._simple_dist_matrix()
        destinations = ['A', 'B', 'C', 'D']
        result = nearest_neighbor_tsp('Depot', destinations, dist)
        route = result['route']
        self.assertEqual(route[0], 'Depot')
        self.assertEqual(route[-1], 'Depot')
        for dest in destinations:
            self.assertIn(dest, route)

    def test_route_includes_all_nodes(self):
        dist, _ = self._simple_dist_matrix()
        destinations = ['B', 'C', 'D']
        result = nearest_neighbor_tsp('Depot', destinations, dist)
        route = result['route']
        for d in destinations:
            self.assertIn(d, route)

    def test_return_to_depot(self):
        dist, _ = self._simple_dist_matrix()
        result = nearest_neighbor_tsp('Depot', ['A', 'B'], dist)
        self.assertEqual(result['route'][0], result['route'][-1])
        self.assertEqual(result['route'][0], 'Depot')

    def test_unreachable_destination(self):
        dist, _ = self._simple_dist_matrix()
        # Make E unreachable by adding inf distances
        dist['Depot']['E'] = math.inf
        dist['E'] = {'Depot': math.inf, 'A': math.inf, 'B': math.inf,
                     'C': math.inf, 'D': math.inf, 'E': 0}
        for node in ['A', 'B', 'C', 'D']:
            dist[node]['E'] = math.inf
        result = nearest_neighbor_tsp('Depot', ['A', 'E'], dist)
        self.assertIn('unreachable_nodes', result)
        self.assertIn('E', result['unreachable_nodes'])

    def test_empty_destinations(self):
        dist = {'Depot': {'Depot': 0}}
        result = nearest_neighbor_tsp('Depot', [], dist)
        self.assertEqual(result['route'], ['Depot', 'Depot'])
        self.assertEqual(result['total_distance'], 0)

    def test_build_distance_matrix(self):
        """build_distance_matrix from all_pairs dict produces correct matrix."""
        all_pairs = {
            'Depot': {'Depot': 0, 'A': 5, 'B': 8},
            'A':     {'Depot': 5, 'A': 0, 'B': 3},
            'B':     {'Depot': 8, 'A': 3, 'B': 0},
        }
        nodes = ['Depot', 'A', 'B']
        matrix = build_distance_matrix(nodes, all_pairs)
        self.assertEqual(matrix['Depot']['A'], 5)
        self.assertEqual(matrix['A']['B'], 3)
        self.assertEqual(matrix['B']['Depot'], 8)


if __name__ == '__main__':
    unittest.main()
