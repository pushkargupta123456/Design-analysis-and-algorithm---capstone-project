import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from algorithms.knapsack import knapsack_01, timed_knapsack


def make_parcel(pid, weight, value, priority=5, deadline='2024-01-01', dest='A'):
    return {
        'parcel_id': pid,
        'parcel_name': f'Parcel-{pid}',
        'weight': weight,
        'priority_score': priority,
        'delivery_deadline': deadline,
        'destination_node': dest,
        'delivery_value': value,
    }


class TestKnapsack01(unittest.TestCase):

    def test_normal_selection(self):
        """5 parcels, capacity 20 — optimal selection verified."""
        parcels = [
            make_parcel(1, 5, 100),
            make_parcel(2, 8, 200),
            make_parcel(3, 3, 60),
            make_parcel(4, 10, 250),
            make_parcel(5, 7, 180),
        ]
        result = knapsack_01(parcels, 20)
        self.assertIn('selected', result)
        self.assertIn('total_value', result)
        self.assertIn('total_weight', result)
        self.assertLessEqual(result['total_weight'], 20)
        # Optimal value for this instance: items 2+4+3 = w:21 > 20; best is 1+2+5=w:20, v:480
        # or 2+4=w:18 v:450; 1+4+3=w:18 v:410; 1+5+3=w:15 v:340; 2+5+3=w:18 v:440
        # Items 3+4+5: weight 3+10+7 = 20, value 60+250+180 = 490 is optimal
        self.assertEqual(result['total_value'], 490)

    def test_capacity_fully_used(self):
        """Input designed to exactly fill capacity."""
        parcels = [
            make_parcel(1, 5, 50),
            make_parcel(2, 5, 50),
        ]
        result = knapsack_01(parcels, 10)
        self.assertEqual(result['total_weight'], 10)
        self.assertEqual(len(result['selected']), 2)

    def test_no_eligible_parcels(self):
        """All parcels heavier than capacity → selected is empty."""
        parcels = [make_parcel(i, 15, 100) for i in range(3)]
        result = knapsack_01(parcels, 10)
        self.assertEqual(result['selected'], [])
        self.assertEqual(result['total_weight'], 0)

    def test_single_parcel_fits(self):
        parcel = [make_parcel(1, 5, 100)]
        result = knapsack_01(parcel, 10)
        self.assertEqual(len(result['selected']), 1)
        self.assertEqual(result['total_weight'], 5)
        self.assertEqual(result['total_value'], 100)

    def test_single_parcel_too_heavy(self):
        parcel = [make_parcel(1, 15, 100)]
        result = knapsack_01(parcel, 10)
        self.assertEqual(result['selected'], [])
        self.assertEqual(result['total_weight'], 0)

    def test_empty_parcels(self):
        result = knapsack_01([], 50)
        self.assertEqual(result['selected'], [])
        self.assertEqual(result['total_weight'], 0)
        self.assertEqual(result['total_value'], 0)

    def test_zero_capacity(self):
        parcels = [make_parcel(i, 5, 100) for i in range(3)]
        result = knapsack_01(parcels, 0)
        self.assertEqual(result['selected'], [])
        self.assertEqual(result['total_weight'], 0)

    def test_total_weight_within_capacity(self):
        """total_weight must never exceed capacity for any input."""
        import random
        random.seed(7)
        parcels = [make_parcel(i, random.randint(1, 20), random.randint(10, 300))
                   for i in range(30)]
        for capacity in [10, 50, 100, 200]:
            result = knapsack_01(parcels, capacity)
            self.assertLessEqual(result['total_weight'], capacity,
                                 f"total_weight exceeded capacity {capacity}")

    def test_timed_knapsack(self):
        parcels = [make_parcel(i, 3, 100) for i in range(5)]
        result, elapsed = timed_knapsack(parcels, 10)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(elapsed, float)
        self.assertGreaterEqual(elapsed, 0.0)


if __name__ == '__main__':
    unittest.main()
