"""
0/1 Knapsack Dynamic Programming Algorithm for Smart Courier Parcel Selection.

Given a vehicle weight capacity and a list of parcels (each with a weight and
delivery value), this module selects the subset of parcels that maximises total
delivery value without exceeding the capacity.

Algorithm: Bottom-up Dynamic Programming
  - Build a 2-D DP table of size (n+1) x (W+1) where n = number of parcels and
    W = integer capacity.
  - dp[i][w] = maximum value achievable using the first i items with capacity w.
  - Recurrence:
      dp[i][w] = dp[i-1][w]                             if weight[i] > w
               = max(dp[i-1][w], dp[i-1][w-wt[i]] + v[i])  otherwise

Complexity:
  Time  : O(n * W)
  Space : O(n * W) for full table (can be reduced to O(W), but full table is
          kept here to support backtracking and display).
"""

import time


def knapsack_01(parcels, capacity):
    """
    Solve the 0/1 Knapsack problem using bottom-up Dynamic Programming.

    Each parcel can be included at most once. The goal is to maximise total
    delivery_value subject to sum(weight) <= capacity.

    Parameters
    ----------
    parcels : list[dict]
        List of parcel dicts. Each dict must have at minimum:
          - 'weight'         : numeric (rounded to int internally)
          - 'delivery_value' : numeric
        All other keys are preserved and returned unchanged in selected/rejected.
    capacity : int
        Maximum weight the vehicle can carry. Must be a positive integer.
        Float values are rounded to int.

    Returns
    -------
    dict with keys:
        selected         : list[dict] — parcels chosen for delivery
        rejected         : list[dict] — parcels not chosen
        total_weight     : int        — sum of selected parcel weights
        remaining_capacity : int      — capacity - total_weight
        total_value      : int        — sum of selected delivery_value
        dp_table_preview : str        — human-readable DP table snippet
    """
    capacity = int(round(capacity))

    # Edge cases
    if capacity <= 0 or not parcels:
        return {
            "selected": [],
            "rejected": list(parcels),
            "total_weight": 0,
            "remaining_capacity": max(0, capacity),
            "total_value": 0,
            "dp_table_preview": "No items or zero capacity — nothing selected.",
        }

    n = len(parcels)
    weights = [int(round(float(p["weight"]))) for p in parcels]
    values = [int(round(float(p["delivery_value"]))) for p in parcels]
    W = capacity

    # Build DP table: (n+1) rows x (W+1) cols
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = weights[i - 1]
        val = values[i - 1]
        for w in range(W + 1):
            # Option 1: exclude item i
            dp[i][w] = dp[i - 1][w]
            # Option 2: include item i (if it fits)
            if wt <= w:
                include_val = dp[i - 1][w - wt] + val
                if include_val > dp[i][w]:
                    dp[i][w] = include_val

    # Backtrack to find which items were selected
    selected_indices = set()
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected_indices.add(i - 1)  # 0-based index
            w -= weights[i - 1]

    selected = [parcels[i] for i in range(n) if i in selected_indices]
    rejected = [parcels[i] for i in range(n) if i not in selected_indices]

    total_weight = sum(weights[i] for i in selected_indices)
    total_value = dp[n][W]

    preview = get_dp_table_string(parcels, capacity)

    return {
        "selected": selected,
        "rejected": rejected,
        "total_weight": total_weight,
        "remaining_capacity": W - total_weight,
        "total_value": total_value,
        "dp_table_preview": preview,
    }


def get_dp_table_string(parcels, capacity, max_display=8):
    """
    Build a human-readable string representation of the Knapsack DP table.

    For readability, only the first max_display items (rows) and the first
    max_display+1 capacity columns are shown when the table is large.

    Parameters
    ----------
    parcels : list[dict]
        Parcel list (same as passed to knapsack_01).
    capacity : int
        Knapsack capacity.
    max_display : int
        Maximum number of items/capacity values to display in each dimension.

    Returns
    -------
    str
        Formatted table string suitable for printing or logging.
    """
    capacity = int(round(capacity))
    if capacity <= 0 or not parcels:
        return "Empty DP table (no items or zero capacity)."

    n = len(parcels)
    weights = [int(round(float(p["weight"]))) for p in parcels]
    values = [int(round(float(p["delivery_value"]))) for p in parcels]
    W = capacity

    # Build table
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wt = weights[i - 1]
        val = values[i - 1]
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]
            if wt <= w:
                include_val = dp[i - 1][w - wt] + val
                if include_val > dp[i][w]:
                    dp[i][w] = include_val

    # Determine display bounds
    row_limit = min(n + 1, max_display + 1)
    col_limit = min(W + 1, max_display + 1)

    col_indices = list(range(col_limit))
    truncated_cols = col_limit < W + 1
    truncated_rows = row_limit < n + 1

    lines = []
    # Header
    header = f"{'Item':<20} " + " ".join(f"w={c:>3}" for c in col_indices)
    if truncated_cols:
        header += f"  ... (up to w={W})"
    lines.append(header)
    lines.append("-" * len(header))

    # Row 0: no items
    row0 = " ".join(f"{dp[0][c]:>6}" for c in col_indices)
    lines.append(f"{'(none)':<20} {row0}")

    for i in range(1, row_limit):
        label = parcels[i - 1].get("parcel_id", f"item{i}")
        row = " ".join(f"{dp[i][c]:>6}" for c in col_indices)
        lines.append(f"{str(label):<20} {row}")

    if truncated_rows:
        lines.append(f"  ... ({n - max_display} more items not shown)")

    lines.append(f"\nOptimal value = {dp[n][W]}  (capacity={W})")
    return "\n".join(lines)


def timed_knapsack(parcels, capacity):
    """
    Run knapsack_01 and measure wall-clock execution time.

    Parameters
    ----------
    parcels : list[dict]
        List of parcel dicts.
    capacity : int
        Vehicle weight capacity.

    Returns
    -------
    tuple[dict, float]
        (result_dict, elapsed_ms) where result_dict is the return value of
        knapsack_01 and elapsed_ms is execution time in milliseconds.
    """
    start = time.perf_counter()
    result = knapsack_01(parcels, capacity)
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000.0
    return result, elapsed_ms
