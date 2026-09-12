"""
data_sources.py
----------------
One function per external data source. This is the ONLY file that should
know how to fetch/load raw data. Stage 1 ships with clearly-labeled sample
data so the rest of the app has something real to run against.

May import: utilities.py
Must NOT import: data_processing, climate_models, rag_system, app
"""

from __future__ import annotations

import random
from typing import Optional

import pandas as pd

from utilities import LOGGER, current_timestamp, is_valid_pakistan_coordinate

SAMPLE_DIR = "data/sample"


# ---------------------------------------------------------------------------
# A. Location source
# ---------------------------------------------------------------------------

def load_location_source() -> pd.DataFrame:
    """
    Load sample Pakistan location data (province, district, city, lat/lon).

    Output columns:
        province, district, city, latitude, longitude
    """
    # Stage 1: a small, hand-picked set of major cities across provinces.
    # This will later be replaced/extended with a full administrative
    # boundaries dataset (see README limitations).
    sample_locations = [
        ("Punjab", "Lahore", "Lahore", 31.5497, 74.3436),
        ("Punjab", "Rawalpindi", "Rawalpindi", 33.5651, 73.0169),
        ("Punjab", "Multan", "Multan", 30.1575, 71.5249),
        ("Sindh", "Karachi", "Karachi", 24.8607, 67.0011),
        ("Sindh", "Hyderabad", "Hyderabad", 25.3960, 68.3578),
        ("Sindh", "Sukkur", "Sukkur", 27.7052, 68.8574),
        ("Khyber Pakhtunkhwa", "Peshawar", "Peshawar", 34.0151, 71.5249),
        ("Khyber Pakhtunkhwa", "Swat", "Mingora", 34.7717, 72.3600),
        ("Balochistan", "Quetta", "Quetta", 30.1798, 66.9750),
        ("Balochistan", "Gwadar", "Gwadar", 25.1216, 62.3254),
        ("Islamabad Capital Territory", "Islamabad", "Islamabad", 33.6844, 73.0479),
        ("Gilgit-Baltistan", "Gilgit", "Gilgit", 35.9188, 74.3103),
        ("Azad Kashmir", "Muzaffarabad", "Muzaffarabad", 34.3700, 73.4711),
    ]
    df = pd.DataFrame(
        sample_locations,
        columns=["province", "district", "city", "latitude", "longitude"],
    )
    df["valid_coordinates"] = df.apply(
        lambda r: is_valid_pakistan_coordinate(r["latitude"], r["longitude"]), axis=1
    )
    df["source"] = "sample_location_dataset"
    df["is_simulated"] = True
    df["data_timestamp"] = current_timestamp()
    return df


# ---------------------------------------------------------------------------
# B. Weather source
# ---------------------------------------------------------------------------

def load_weather_source(latitude: float, longitude: float, seed: Optional[int] = None) -> pd.DataFrame:
    """
    Simulated weather data for a single point.

    Expected real-world replacement: Pakistan Meteorological Department /
    Copernicus ERA5 station or gridded data.

    Output columns:
        latitude, longitude, temperature_c, temp_max_c, temp_min_c,
        humidity_pct, wind_speed_kmh, wind_direction_deg,
        pressure_hpa, source, is_simulated, data_timestamp
    """
    rng = random.Random(seed)
    temp = round(rng.uniform(15, 42), 1)
    row = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_c": temp,
        "temp_max_c": round(temp + rng.uniform(1, 6), 1),
        "temp_min_c": round(temp - rng.uniform(1, 6), 1),
        "humidity_pct": round(rng.uniform(15, 90), 1),
        "wind_speed_kmh": round(rng.uniform(0, 40), 1),
        "wind_direction_deg": round(rng.uniform(0, 359), 0),
        "pressure_hpa": round(rng.uniform(995, 1020), 1),
        "source": "sample_weather_source",
        "is_simulated": True,
        "data_timestamp": current_timestamp(),
    }
    return pd.DataFrame([row])


# ---------------------------------------------------------------------------
# C. Rainfall source
# ---------------------------------------------------------------------------

def load_rainfall_source(latitude: float, longitude: float, seed: Optional[int] = None) -> pd.DataFrame:
    """
    Simulated rainfall data for a single point.

    Expected real-world replacement: NASA GPM IMERG / PMD rain-gauge data.

    Output columns:
        latitude, longitude, rainfall_current_mm, rainfall_24h_mm,
        rainfall_7d_mm, rainfall_30d_mm, rainfall_anomaly_pct,
        forecast_precip_mm, source, is_simulated, data_timestamp
    """
    rng = random.Random(seed)
    r24 = round(rng.uniform(0, 120), 1)
    row = {
        "latitude": latitude,
        "longitude": longitude,
        "rainfall_current_mm": round(rng.uniform(0, 20), 1),
        "rainfall_24h_mm": r24,
        "rainfall_7d_mm": round(r24 + rng.uniform(0, 200), 1),
        "rainfall_30d_mm": round(r24 + rng.uniform(0, 400), 1),
        "rainfall_anomaly_pct": round(rng.uniform(-60, 150), 1),
        "forecast_precip_mm": round(rng.uniform(0, 50), 1),
        "source": "sample_rainfall_source",
        "is_simulated": True,
        "data_timestamp": current_timestamp(),
    }
    return pd.DataFrame([row])


# ---------------------------------------------------------------------------
# D. River / water source
# ---------------------------------------------------------------------------

def load_river_source(latitude: float, longitude: float, seed: Optional[int] = None) -> pd.DataFrame:
    """
    Simulated river/water-level data for a single point.

    Expected real-world replacement: WAPDA / Flood Forecasting Division
    river-gauge data.

    Output columns:
        latitude, longitude, river_level_m, river_flow_cumecs,
        river_level_change_m, source, is_simulated, data_timestamp
    """
    rng = random.Random(seed)
    row = {
        "latitude": latitude,
        "longitude": longitude,
        "river_level_m": round(rng.uniform(1, 12), 2),
        "river_flow_cumecs": round(rng.uniform(50, 5000), 1),
        "river_level_change_m": round(rng.uniform(-1.0, 1.5), 2),
        "source": "sample_river_source",
        "is_simulated": True,
        "data_timestamp": current_timestamp(),
    }
    return pd.DataFrame([row])


# ---------------------------------------------------------------------------
# E. Satellite / geospatial source
# ---------------------------------------------------------------------------

def load_satellite_source(latitude: float, longitude: float, seed: Optional[int] = None) -> pd.DataFrame:
    """
    Simulated satellite-derived indicators for a single point.

    Expected real-world replacement: Copernicus Sentinel / NASA
    Earth-observation products.

    Output columns:
        latitude, longitude, ndvi, land_surface_temp_c, soil_moisture_pct,
        source, is_simulated, data_timestamp
    """
    rng = random.Random(seed)
    row = {
        "latitude": latitude,
        "longitude": longitude,
        "ndvi": round(rng.uniform(0.05, 0.8), 2),
        "land_surface_temp_c": round(rng.uniform(18, 48), 1),
        "soil_moisture_pct": round(rng.uniform(5, 45), 1),
        "source": "sample_satellite_source",
        "is_simulated": True,
        "data_timestamp": current_timestamp(),
    }
    return pd.DataFrame([row])


# ---------------------------------------------------------------------------
# F. Elevation / terrain source
# ---------------------------------------------------------------------------

def load_elevation_source(latitude: float, longitude: float, seed: Optional[int] = None) -> pd.DataFrame:
    """
    Simulated elevation/terrain data for a single point.

    Expected real-world replacement: SRTM / open elevation datasets.

    Output columns:
        latitude, longitude, elevation_m, slope_deg, urban_density_pct,
        source, is_simulated, data_timestamp
    """
    rng = random.Random(seed)
    row = {
        "latitude": latitude,
        "longitude": longitude,
        "elevation_m": round(rng.uniform(0, 2500), 1),
        "slope_deg": round(rng.uniform(0, 25), 1),
        "urban_density_pct": round(rng.uniform(5, 95), 1),
        "source": "sample_elevation_source",
        "is_simulated": True,
        "data_timestamp": current_timestamp(),
    }
    return pd.DataFrame([row])


# ---------------------------------------------------------------------------
# G. Historical hazards source
# ---------------------------------------------------------------------------

def load_historical_hazards_source() -> pd.DataFrame:
    """
    Sample historical hazard events for Pakistan (illustrative, not exhaustive).

    Expected real-world replacement: NDMA / PDMA disaster records.

    Output columns:
        hazard_type, province, district, event_date, severity, source,
        is_simulated
    """
    events = [
        ("flood", "Sindh", "Sukkur", "2022-08-15", "severe"),
        ("flood", "Punjab", "Multan", "2022-08-20", "moderate"),
        ("heatwave", "Sindh", "Karachi", "2015-06-20", "severe"),
        ("drought", "Balochistan", "Quetta", "2018-03-01", "moderate"),
        ("flood", "Khyber Pakhtunkhwa", "Swat", "2010-07-29", "severe"),
    ]
    df = pd.DataFrame(events, columns=["hazard_type", "province", "district", "event_date", "severity"])
    df["source"] = "sample_historical_hazards"
    df["is_simulated"] = True
    return df


# ---------------------------------------------------------------------------
# Source registry
# ---------------------------------------------------------------------------
# Register any new point-based source function here. Adding a source should
# only require: (1) writing the function above, (2) adding one line below.

POINT_SOURCE_REGISTRY = {
    "weather": load_weather_source,
    "rainfall": load_rainfall_source,
    "river": load_river_source,
    "satellite": load_satellite_source,
    "elevation": load_elevation_source,
}

LOGGER.info("data_sources.py loaded: %d point sources registered", len(POINT_SOURCE_REGISTRY))
