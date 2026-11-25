"""
core/parcel_manager.py
Manages loading, validation, and querying of parcel data.
"""

import csv
from datetime import datetime


class ParcelManager:
    """Handles parcel data: loading from CSV, validation, and queries."""

    REQUIRED_FIELDS = [
        "parcel_id", "parcel_name", "weight", "priority_score",
        "delivery_deadline", "destination_node", "delivery_value"
    ]

    def __init__(self):
        self._parcels = []

    @property
    def parcels(self):
        return self._parcels

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_from_csv(self, filepath: str) -> int:
        """
        Load parcels from a CSV file.

        Returns the number of parcels loaded.
        Raises ValueError with a descriptive message on bad data.
        """
        self.clear()
        seen_ids = set()

        try:
            with open(filepath, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)

                # Verify required columns exist
                if reader.fieldnames is None:
                    raise ValueError(f"CSV file '{filepath}' is empty or has no header.")

                missing_cols = set(self.REQUIRED_FIELDS) - set(reader.fieldnames)
                if missing_cols:
                    raise ValueError(
                        f"CSV is missing required columns: {', '.join(sorted(missing_cols))}"
                    )

                for lineno, row in enumerate(reader, start=2):
                    # Strip whitespace
                    row = {k: (v.strip() if v else v) for k, v in row.items()}

                    # --- parcel_id uniqueness ---
                    pid = row.get("parcel_id", "")
                    if not pid:
                        raise ValueError(f"Row {lineno}: parcel_id is empty.")
                    if pid in seen_ids:
                        raise ValueError(
                            f"Row {lineno}: Duplicate parcel_id '{pid}'."
                        )
                    seen_ids.add(pid)

                    # Validate and coerce the full row
                    parcel = self._coerce_row(row, lineno)
                    self.validate_parcel(parcel)
                    self._parcels.append(parcel)

        except FileNotFoundError:
            raise ValueError(f"Parcel CSV file not found: '{filepath}'")
        except csv.Error as exc:
            raise ValueError(f"CSV parse error in '{filepath}': {exc}") from exc

        return len(self._parcels)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all_parcels(self) -> list:
        """Return a copy of the full parcel list."""
        return list(self._parcels)

    def get_parcels_for_destination(self, node: str) -> list:
        """Return all parcels destined for *node*."""
        return [p for p in self._parcels if p["destination_node"] == node]

    def get_summary(self) -> dict:
        """
        Return a summary dict:
            total_count, destinations, weight_range, value_range
        """
        if not self._parcels:
            return {
                "total_count": 0,
                "destinations": [],
                "weight_range": (0, 0),
                "value_range": (0, 0),
            }

        weights = [p["weight"] for p in self._parcels]
        values  = [p["delivery_value"] for p in self._parcels]
        destinations = sorted({p["destination_node"] for p in self._parcels})

        return {
            "total_count":   len(self._parcels),
            "destinations":  destinations,
            "weight_range":  (min(weights), max(weights)),
            "value_range":   (min(values),  max(values)),
        }

    def clear(self):
        """Reset the parcel list."""
        self._parcels = []

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_parcel(self, parcel_dict: dict):
        """
        Validate a single parcel dict (all fields already coerced to their
        proper types).  Raises ValueError with a field-specific message.
        """
        # weight
        try:
            w = float(parcel_dict.get("weight", 0))
        except (TypeError, ValueError):
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': weight must be numeric."
            )
        if w <= 0:
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': weight must be > 0 (got {w})."
            )

        # priority_score
        try:
            ps = float(parcel_dict.get("priority_score", 0))
        except (TypeError, ValueError):
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': priority_score must be numeric."
            )
        if not (1 <= ps <= 10):
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': priority_score must be 1-10 (got {ps})."
            )

        # delivery_deadline
        deadline = parcel_dict.get("delivery_deadline", "")
        if not deadline:
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': delivery_deadline is empty."
            )
        try:
            datetime.strptime(str(deadline), "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': delivery_deadline must be YYYY-MM-DD (got '{deadline}')."
            )

        # delivery_value
        try:
            dv = float(parcel_dict.get("delivery_value", 0))
        except (TypeError, ValueError):
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': delivery_value must be numeric."
            )
        if dv <= 0:
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': delivery_value must be > 0 (got {dv})."
            )

        # destination_node
        dest = parcel_dict.get("destination_node", "")
        if not dest:
            raise ValueError(
                f"Parcel '{parcel_dict.get('parcel_id')}': destination_node must not be empty."
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _coerce_row(row: dict, lineno: int) -> dict:
        """
        Convert raw CSV string values to appropriate Python types.
        Returns a new dict ready for validate_parcel().
        """
        try:
            weight = float(row["weight"])
        except (ValueError, KeyError):
            raise ValueError(
                f"Row {lineno}: 'weight' is not a valid number (got '{row.get('weight')}')."
            )

        try:
            priority_score = float(row["priority_score"])
        except (ValueError, KeyError):
            raise ValueError(
                f"Row {lineno}: 'priority_score' is not a valid number (got '{row.get('priority_score')}')."
            )

        try:
            delivery_value = float(row["delivery_value"])
        except (ValueError, KeyError):
            raise ValueError(
                f"Row {lineno}: 'delivery_value' is not a valid number (got '{row.get('delivery_value')}')."
            )

        return {
            "parcel_id":          row.get("parcel_id", "").strip(),
            "parcel_name":        row.get("parcel_name", "").strip(),
            "weight":             weight,
            "priority_score":     priority_score,
            "delivery_deadline":  row.get("delivery_deadline", "").strip(),
            "destination_node":   row.get("destination_node", "").strip(),
            "delivery_value":     delivery_value,
        }
