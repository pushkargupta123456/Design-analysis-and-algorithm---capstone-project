import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import random
from algorithms.sorting import merge_sort, builtin_sort, timed_sort, default_sort_key


def make_parcel(pid, deadline, priority, value, weight=5, dest='A'):
    return {
        'parcel_id': pid,
        'parcel_name': f'Parcel-{pid}',
        'weight': weight,
        'priority_score': priority,
        'delivery_deadline': deadline,
        'destination_node': dest,
        'delivery_value': value,
    }


class TestMergeSort(unittest.TestCase):

    def test_empty_list(self):
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(builtin_sort([]), [])

    def test_single_parcel(self):
        p = make_parcel(1, '2024-01-10', 5, 100)
        self.assertEqual(merge_sort([p]), [p])
        self.assertEqual(builtin_sort([p]), [p])

    def test_sort_by_deadline(self):
        p1 = make_parcel(1, '2024-03-01', 5, 100)
        p2 = make_parcel(2, '2024-01-01', 5, 100)
        p3 = make_parcel(3, '2024-02-01', 5, 100)
        for sort_fn in (merge_sort, builtin_sort):
            result = sort_fn([p1, p2, p3])
            deadlines = [r['delivery_deadline'] for r in result]
            self.assertEqual(deadlines, sorted(deadlines))

    def test_sort_equal_deadline_priority(self):
        # Equal deadlines → higher priority_score first (lower tuple value = -priority)
        p1 = make_parcel(1, '2024-01-01', 3, 100)
        p2 = make_parcel(2, '2024-01-01', 9, 100)
        p3 = make_parcel(3, '2024-01-01', 6, 100)
        for sort_fn in (merge_sort, builtin_sort):
            result = sort_fn([p1, p2, p3])
            priorities = [r['priority_score'] for r in result]
            self.assertEqual(priorities, sorted(priorities, reverse=True),
                             f"{sort_fn.__name__} did not sort by priority descending")

    def test_sort_equal_deadline_equal_priority(self):
        # Equal deadline, equal priority → higher value first
        p1 = make_parcel(1, '2024-01-01', 5, 50)
        p2 = make_parcel(2, '2024-01-01', 5, 300)
        p3 = make_parcel(3, '2024-01-01', 5, 150)
        for sort_fn in (merge_sort, builtin_sort):
            result = sort_fn([p1, p2, p3])
            values = [r['delivery_value'] for r in result]
            self.assertEqual(values, sorted(values, reverse=True),
                             f"{sort_fn.__name__} did not sort by value descending")

    def test_sort_stability(self):
        """Large list: sorted result must have non-decreasing sort keys."""
        random.seed(42)
        deadlines = ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01']
        parcels = [
            make_parcel(i,
                        random.choice(deadlines),
                        random.randint(1, 10),
                        random.randint(50, 500))
            for i in range(50)
        ]
        for sort_fn in (merge_sort, builtin_sort):
            result = sort_fn(parcels[:])
            keys = [default_sort_key(r) for r in result]
            for i in range(len(keys) - 1):
                self.assertLessEqual(keys[i], keys[i + 1],
                                     f"{sort_fn.__name__}: not sorted at index {i}")

    def test_timed_sort(self):
        parcels = [make_parcel(i, '2024-01-01', 5, 100) for i in range(10)]
        result, elapsed = timed_sort(parcels, merge_sort)
        self.assertIsInstance(result, list)
        self.assertIsInstance(elapsed, float)
        self.assertGreaterEqual(elapsed, 0.0)

    def test_merge_matches_builtin(self):
        random.seed(99)
        deadlines = ['2024-01-10', '2024-02-20', '2024-03-15']
        parcels = [
            make_parcel(i,
                        random.choice(deadlines),
                        random.randint(1, 10),
                        random.randint(50, 500))
            for i in range(20)
        ]
        merge_result = merge_sort(parcels[:])
        builtin_result = builtin_sort(parcels[:])
        merge_ids = [p['parcel_id'] for p in merge_result]
        builtin_ids = [p['parcel_id'] for p in builtin_result]
        self.assertEqual(merge_ids, builtin_ids,
                         "merge_sort and builtin_sort produced different orders")


if __name__ == '__main__':
    unittest.main()
