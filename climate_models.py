"""
climate_models.py
------------------
Flood, heatwave, and drought risk models.

Stage 1 scope: function signatures + a transparent placeholder risk-index
calculation, clearly labeled as a prototype (NOT a validated probability).
Real trained models (Random Forest / Gradient Boosting / XGBoost) are
added starting Stage 3.

May import: data_processing.py (processed data), utilities.py
Must NOT import: rag_system, app
"""

from __future__ import annotations

from typing import Any, Dict

from utilities import LOGGER, classify_risk_score, INSUFFICIENT_DATA_MESSAGE

MODEL_VERSION = "0.1.0-prototype"
PREDICTION_HORIZON_HOURS = 24


def _prototype_index(readings: Dict[str, Any], weighted_fields: Dict[str, tuple]) -> float | None:
    """
    Very simple, transparent weighted-average prototype index over 0-100.
    weighted_fields: {field_name: (weight, min_expected, max_expected)}
    Returns None if none of the needed fields are present (insufficient data).
    """
    total_weight = 0.0
    weighted_sum = 0.0
    for field, (weight, lo, hi) in weighted_fields.items():
        val = readings.get(field)
        if val is None:
            continue
        try:
            val = float(val)
        except (TypeError, ValueError):
            continue
        norm = max(0.0, min(1.0, (val - lo) / (hi - lo))) if hi != lo else 0.0
        weighted_sum += norm * weight
        total_weight += weight
    if total_weight == 0:
        return None
    return round((weighted_sum / total_weight) * 100, 1)


def predict_flood_risk(processed_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: a snapshot dict from data_processing.build_environmental_snapshot()
    Output: {hazard, risk_score, risk_category, is_probability, contributing_factors,
             model_version, prediction_horizon_hours, status}
    """
    readings = processed_snapshot.get("readings", {})
    weights = {
        "rainfall_24h_mm": (0.3, 0, 150),
        "rainfall_7d_mm": (0.2, 0, 400),
        "river_level_change_m": (0.25, -1.0, 1.5),
        "forecast_precip_mm": (0.15, 0, 50),
        "slope_deg": (0.1, 25, 0),  # inverted: lower slope -> higher flood risk
    }
    score = _prototype_index(readings, weights)
    return _build_result("flood", score, readings, weights)


def predict_heatwave_risk(processed_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    readings = processed_snapshot.get("readings", {})
    weights = {
        "temp_max_c": (0.4, 30, 48),
        "humidity_pct": (0.2, 15, 90),
        "land_surface_temp_c": (0.3, 25, 48),
        "urban_density_pct": (0.1, 5, 95),
    }
    score = _prototype_index(readings, weights)
    return _build_result("heatwave", score, readings, weights)


def predict_drought_risk(processed_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    readings = processed_snapshot.get("readings", {})
    weights = {
        "rainfall_anomaly_pct": (0.35, 150, -60),  # inverted: negative anomaly -> higher drought risk
        "soil_moisture_pct": (0.35, 45, 5),  # inverted: lower moisture -> higher risk
        "ndvi": (0.3, 0.8, 0.05),  # inverted: lower vegetation -> higher risk
    }
    score = _prototype_index(readings, weights)
    return _build_result("drought", score, readings, weights)


def _build_result(hazard: str, score: float | None, readings: Dict[str, Any], weights: Dict[str, tuple]) -> Dict[str, Any]:
    if score is None:
        LOGGER.warning("%s risk: %s", hazard, INSUFFICIENT_DATA_MESSAGE)
        return {
            "hazard": hazard,
            "risk_score": None,
            "risk_category": INSUFFICIENT_DATA_MESSAGE,
            "is_probability": False,
            "contributing_factors": [],
            "model_version": MODEL_VERSION,
            "prediction_horizon_hours": PREDICTION_HORIZON_HOURS,
            "status": "insufficient_data",
        }
    used_fields = [f for f in weights if readings.get(f) is not None]
    return {
        "hazard": hazard,
        "risk_score": score,  # a prototype index, NOT a calibrated probability
        "risk_category": classify_risk_score(score),
        "is_probability": False,
        "contributing_factors": used_fields,
        "model_version": MODEL_VERSION,
        "prediction_horizon_hours": PREDICTION_HORIZON_HOURS,
        "status": "prototype_index",
    }
