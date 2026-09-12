"""
data_processing.py
-------------------
Load -> validate -> clean -> standardize -> align -> derive features.

Stage 1 scope: enough to combine the point-based sample sources for a
single selected location and hand a clean, flat dict of environmental
readings to the rest of the app. Full validation/cleaning/derived-feature
logic (cumulative rainfall calcs, anomaly detection, etc.) is expanded in
Stage 2.

May import: data_sources.py, utilities.py
Must NOT import: climate_models, rag_system, app
"""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from data_sources import POINT_SOURCE_REGISTRY
from utilities import (
    LOGGER,
    current_timestamp,
    is_valid_pakistan_coordinate,
    make_data_quality_note,
    safe_get,
)

REQUIRED_LOCATION_COLUMNS = ["province", "district", "city", "latitude", "longitude"]


def validate_location_row(location: Dict[str, Any]) -> list:
    """Return a list of problems found with a location record (empty = OK)."""
    problems = []
    for col in REQUIRED_LOCATION_COLUMNS:
        if col not in location or location[col] in (None, ""):
            problems.append(f"missing '{col}'")
    lat, lon = location.get("latitude"), location.get("longitude")
    if not is_valid_pakistan_coordinate(lat, lon):
        problems.append("coordinates outside expected Pakistan bounding box")
    return problems


def build_environmental_snapshot(location: Dict[str, Any], seed: int = None) -> Dict[str, Any]:
    """
    Run every registered point source for a location and merge the results
    into one flat dictionary, tracking any sources that failed and any
    fields that ended up missing.

    Parameters
    ----------
    location : dict with at least 'latitude' and 'longitude'
    seed : optional int, forwarded to sample sources for reproducibility

    Returns
    -------
    dict with keys:
        location, readings (flat dict of all fields), missing_sources,
        is_simulated, data_timestamp, data_quality_note
    """
    problems = validate_location_row(location)
    if problems:
        LOGGER.warning("Location validation issues: %s", problems)

    lat, lon = location.get("latitude"), location.get("longitude")
    readings: Dict[str, Any] = {}
    missing_sources = []

    for name, source_fn in POINT_SOURCE_REGISTRY.items():
        try:
            df = source_fn(latitude=lat, longitude=lon, seed=seed)
            if df is None or df.empty:
                missing_sources.append(name)
                continue
            row = df.iloc[0].to_dict()
            # Namespacing avoids column collisions across sources while
            # staying flat and easy for beginners to read.
            for key, val in row.items():
                if key in ("latitude", "longitude", "source", "is_simulated", "data_timestamp"):
                    continue
                readings[key] = val
        except Exception as exc:  # noqa: BLE001 - one bad source must not crash the app
            LOGGER.error("Source '%s' failed: %s", name, exc)
            missing_sources.append(name)

    quality_note = make_data_quality_note(is_simulated=True, missing_fields=missing_sources)

    return {
        "location": location,
        "readings": readings,
        "missing_sources": missing_sources,
        "is_simulated": True,
        "data_timestamp": current_timestamp(),
        "data_quality_note": quality_note,
        "validation_problems": problems,
    }


def snapshot_to_dataframe(snapshot: Dict[str, Any]) -> pd.DataFrame:
    """Flatten a snapshot dict into a single-row DataFrame for display in the UI."""
    flat = {}
    flat.update({f"location.{k}": v for k, v in snapshot["location"].items()})
    flat.update(snapshot["readings"])
    flat["data_timestamp"] = snapshot["data_timestamp"]
    flat["is_simulated"] = snapshot["is_simulated"]
    return pd.DataFrame([flat])
