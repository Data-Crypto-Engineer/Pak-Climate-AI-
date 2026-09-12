"""
utilities.py
------------
Shared, dependency-free helper functions used across the project.

RULE: This module must NOT import any other project module
(data_sources, data_processing, climate_models, rag_system, app).
It sits at the bottom of the dependency chain.
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """Return a configured logger. Safe to call repeatedly (no duplicate handlers)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


LOGGER = get_logger("climate_pakistan_ai")


# ---------------------------------------------------------------------------
# Risk classification constants (used later by climate_models.py + app.py)
# ---------------------------------------------------------------------------

RISK_CATEGORIES = ["LOW", "MODERATE", "HIGH", "EXTREME"]

# Example thresholds for a 0-100 risk score. Real calibration happens once
# real training data / labels are available (see Stage 3+).
RISK_THRESHOLDS = {
    "LOW": (0, 25),
    "MODERATE": (25, 50),
    "HIGH": (50, 75),
    "EXTREME": (75, 100),
}

INSUFFICIENT_DATA_MESSAGE = "Insufficient data for a reliable prediction."


def classify_risk_score(score: Optional[float]) -> str:
    """
    Map a 0-100 risk score to a RISK_CATEGORIES label.
    Returns INSUFFICIENT_DATA_MESSAGE if score is None or invalid.
    """
    if score is None or not isinstance(score, (int, float)) or math.isnan(score):
        return INSUFFICIENT_DATA_MESSAGE
    score = max(0.0, min(100.0, float(score)))
    for label, (low, high) in RISK_THRESHOLDS.items():
        if low <= score < high or (label == "EXTREME" and score == 100):
            return label
    return INSUFFICIENT_DATA_MESSAGE


# ---------------------------------------------------------------------------
# Small generic helpers
# ---------------------------------------------------------------------------

def safe_get(d: dict, key: str, default: Any = None) -> Any:
    """dict.get that also treats NaN-like values as missing."""
    if not isinstance(d, dict):
        return default
    val = d.get(key, default)
    try:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return default
    except TypeError:
        pass
    return val


def is_valid_pakistan_coordinate(lat: Optional[float], lon: Optional[float]) -> bool:
    """
    Rough bounding-box check for coordinates inside/near Pakistan.
    Not a precise polygon check -- good enough to catch obviously bad input.
    """
    if lat is None or lon is None:
        return False
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return False
    return 23.0 <= lat <= 37.5 and 60.5 <= lon <= 77.5


def current_timestamp() -> str:
    """ISO-8601 UTC timestamp string, used to label data freshness everywhere."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def make_data_quality_note(is_simulated: bool, missing_fields: Optional[list] = None) -> str:
    """
    Build a short, honest data-quality note that the UI must always show
    alongside any environmental data or prediction.
    """
    parts = []
    if is_simulated:
        parts.append("SAMPLE / SIMULATED DATA (not live observations)")
    else:
        parts.append("Live or historical data source")
    if missing_fields:
        parts.append(f"Missing fields: {', '.join(missing_fields)}")
    return " | ".join(parts)
