"""
Sorting Algorithms for Smart Courier Parcel Management System.

Implements Merge Sort and Python's built-in sort for ordering parcels
by delivery deadline, priority score, and delivery value.

Complexity:
  - Merge Sort: O(n log n) time, O(n) auxiliary space
  - Built-in Sort (Timsort): O(n log n) time, O(n) auxiliary space
"""

import time


def default_sort_key(parcel):
    """
    Return the default comparison tuple for a parcel.

    Sorts by:
      1. delivery_deadline ascending (earlier deadlines first, string YYYY-MM-DD compares correctly)
      2. priority_score descending (higher priority first)
      3. delivery_value descending (higher value first)

    Parameters
    ----------
    parcel : dict
        A parcel dict with keys: parcel_id, parcel_name, weight, priority_score,
        delivery_deadline (YYYY-MM-DD string), destination_node, delivery_value.

    Returns
    -------
    tuple
        (delivery_deadline_str, -priority_score, -delivery_value)
    """
    return (
        str(parcel["delivery_deadline"]),
        -float(parcel["priority_score"]),
        -float(parcel["delivery_value"]),
    )


def merge_sort(parcels, key_func=None):
    """
    Sort a list of parcel dicts using the Merge Sort algorithm.

    Merge Sort is a stable, divide-and-conquer algorithm:
      1. Recursively split the list into halves until each sub-list has ≤ 1 element.
      2. Merge adjacent sorted sub-lists by comparing key values.

    Time Complexity  : O(n log n) — always (best, average, worst)
    Space Complexity : O(n)       — auxiliary space for merge step

    Parameters
    ----------
    parcels : list[dict]
        List of parcel dicts to sort. Each dict must contain the keys expected
        by key_func (or the default key).
    key_func : callable or None
        A function that takes a parcel dict and returns a comparable value/tuple.
        If None, uses default_sort_key (deadline asc, priority desc, value desc).

    Returns
    -------
    list[dict]
        A new list of parcel dicts sorted according to key_func.
    """
    if key_func is None:
        key_func = default_sort_key

    # Base case: 0 or 1 elements is already sorted
    if len(parcels) <= 1:
        return list(parcels)

    mid = len(parcels) // 2
    left = merge_sort(parcels[:mid], key_func)
    right = merge_sort(parcels[mid:], key_func)
    return _merge(left, right, key_func)


def _merge(left, right, key_func):
    """
    Merge two sorted lists into one sorted list.

    Parameters
    ----------
    left : list[dict]
        Left sorted sub-list.
    right : list[dict]
        Right sorted sub-list.
    key_func : callable
        Comparison key function.

    Returns
    -------
    list[dict]
        Merged, sorted list.
    """
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key_func(left[i]) <= key_func(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    # Append any remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def builtin_sort(parcels, key_func=None):
    """
    Sort a list of parcel dicts using Python's built-in sorted() (Timsort).

    Timsort is a hybrid stable sort derived from Merge Sort and Insertion Sort.
    It is highly optimised for real-world data and runs in-place relative to
    Python's list objects.

    Time Complexity  : O(n log n) — worst case
    Space Complexity : O(n)

    Parameters
    ----------
    parcels : list[dict]
        List of parcel dicts to sort.
    key_func : callable or None
        A function that takes a parcel dict and returns a comparable value/tuple.
        If None, uses default_sort_key.

    Returns
    -------
    list[dict]
        A new sorted list of parcel dicts.
    """
    if key_func is None:
        key_func = default_sort_key
    return sorted(parcels, key=key_func)


def timed_sort(parcels, sort_func, key_func=None):
    """
    Execute a sorting function and measure its wall-clock execution time.

    Parameters
    ----------
    parcels : list[dict]
        List of parcel dicts to sort.
    sort_func : callable
        A sorting function with signature sort_func(parcels, key_func=None).
        Typically merge_sort or builtin_sort.
    key_func : callable or None
        Key function passed through to sort_func. If None, sort_func uses its
        own default.

    Returns
    -------
    tuple[list[dict], float]
        (sorted_list, elapsed_ms) where elapsed_ms is the time taken in
        milliseconds as a float, measured with time.perf_counter() for
        high resolution.
    """
    start = time.perf_counter()
    sorted_list = sort_func(parcels, key_func)
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000.0
    return sorted_list, elapsed_ms
