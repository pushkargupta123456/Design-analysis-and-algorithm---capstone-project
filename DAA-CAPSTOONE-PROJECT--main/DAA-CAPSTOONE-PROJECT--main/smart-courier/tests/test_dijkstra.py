import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import unittest
from algorithms.dijkstra import dijkstra, reconstruct_path, shortest_path_info, all_pairs_shortest_paths


class TestDijkstra(unittest.TestCase):

    def _simple_graph(self):
        return {
            'Depot': [('A', 5), ('B', 8)],
            'A':     [('B', 3)],
            'B':     [],
        }

    def test_simple_graph(self):
        """Depot→B direct=8, via A=5+3=8; both paths cost 8."""
        graph = self._simple_graph()
        distances, predecessors = dijkstra(graph, 'Depot')
        self.assertEqual(distances['Depot'], 0)
        self.assertEqual(distances['A'], 5)
        self.assertEqual(distances['B'], 8)

    def test_multiple_paths(self):
        """5-node graph — verify shortest paths are correct."""
        graph = {
            'S': [('A', 2), ('B', 10)],
            'A': [('C', 3), ('B', 4)],
            'B': [('D', 1)],
            'C': [('D', 5)],
            'D': [],
        }
        distances, predecessors = dijkstra(graph, 'S')
        # S→A=2, S→A→B=6, S→A→C=5, S→A→B→D=7, S→A→C→D=10
        self.assertEqual(distances['A'], 2)
        self.assertEqual(distances['B'], 6)
        self.assertEqual(distances['C'], 5)
        self.assertEqual(distances['D'], 7)

    def test_same_source_dest(self):
        graph = {'X': [('Y', 3)], 'Y': []}
        distances, predecessors = dijkstra(graph, 'X')
        self.assertEqual(distances['X'], 0)
        path = reconstruct_path(predecessors, 'X', 'X')
        self.assertEqual(path, ['X'])

    def test_unreachable(self):
        graph = {
            'A': [('B', 5)],
            'B': [],
            'C': [],  # disconnected
        }
        distances, predecessors = dijkstra(graph, 'A')
        self.assertEqual(distances.get('C', math.inf), math.inf)
        info = shortest_path_info(graph, 'A', 'C')
        self.assertFalse(info['reachable'])
        self.assertEqual(info['distance'], math.inf)

    def test_negative_edge_raises(self):
        graph = {
            'A': [('B', -1)],
            'B': [],
        }
        with self.assertRaises(ValueError):
            dijkstra(graph, 'A')

    def test_all_pairs(self):
        graph = {
            'P': [('Q', 2), ('R', 4)],
            'Q': [('R', 1)],
            'R': [],
        }
        all_pairs = all_pairs_shortest_paths(graph)
        self.assertIn('P', all_pairs)
        self.assertIn('Q', all_pairs)
        self.assertIn('R', all_pairs)
        # P→Q=2, P→R via Q = 3, Q→R=1
        self.assertEqual(all_pairs['P']['Q'], 2)
        self.assertEqual(all_pairs['P']['R'], 3)
        self.assertEqual(all_pairs['Q']['R'], 1)

    def test_reconstruct_path(self):
        graph = {
            'Depot': [('A', 5), ('B', 8)],
            'A':     [('B', 3)],
            'B':     [],
        }
        distances, predecessors = dijkstra(graph, 'Depot')
        # Path Depot→B should be Depot→A→B (cost 8)
        path = reconstruct_path(predecessors, 'Depot', 'B')
        self.assertEqual(path[0], 'Depot')
        self.assertEqual(path[-1], 'B')
        self.assertIn('A', path)
        self.assertEqual(len(path), 3)

    def test_shortest_path_info_reachable(self):
        graph = self._simple_graph()
        info = shortest_path_info(graph, 'Depot', 'A')
        self.assertTrue(info['reachable'])
        self.assertEqual(info['distance'], 5)
        self.assertEqual(info['path'][0], 'Depot')
        self.assertEqual(info['path'][-1], 'A')


if __name__ == '__main__':
    unittest.main()
