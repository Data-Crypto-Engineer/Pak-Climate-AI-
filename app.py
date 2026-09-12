"""
app.py
------
Climate Pakistan AI - Streamlit entry point.

Stage 1 scope:
    - Basic multi-section interface (Overview, Map, Hazard Analysis, About).
    - Location selector backed by sample Pakistan location data.
    - Basic Folium map of Pakistan with selectable city markers.
    - Clearly labeled SIMULATED environmental data pulled through the
      full data_sources -> data_processing pipeline.
    - Flood / heatwave / drought prototype risk index displayed per
      hazard, with an explicit "prototype, not a validated probability"
      disclaimer.
    - Safe fallback explanation text (real Gemini + RAG wiring: Stage 5).

This file may import every other project module. No other module may
import this file.
"""

from __future__ import annotations

import streamlit as st
from streamlit_folium import st_folium
import folium

from data_sources import load_location_source
from data_processing import build_environmental_snapshot, snapshot_to_dataframe
from climate_models import predict_flood_risk, predict_heatwave_risk, predict_drought_risk
from rag_system import generate_explanation
from utilities import LOGGER, RISK_CATEGORIES

st.set_page_config(page_title="Climate Pakistan AI", layout="wide")

RISK_COLORS = {
    "LOW": "green",
    "MODERATE": "orange",
    "HIGH": "red",
    "EXTREME": "darkred",
}


@st.cache_data(show_spinner=False)
def get_locations():
    return load_location_source()


def render_overview():
    st.title("🌍 Climate Pakistan AI")
    st.markdown(
        "An AI-assisted climate-risk and early-warning **prototype** for Pakistan, "
        "covering flood, heatwave, and drought hazards."
    )
    st.warning(
        "This is a demonstration prototype, **not an official government "
        "early-warning system**. All environmental data shown in this build "
        "stage is simulated sample data, clearly labeled as such."
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Hazards covered", "Flood, Heatwave, Drought")
    col2.metric("Locations available", str(len(get_locations())))
    col3.metric("Data mode", "Sample / Simulated")


def render_map_and_selection():
    st.header("🗺️ Climate Risk Map")
    locations = get_locations()

    city_names = locations["city"].tolist()
    default_index = city_names.index("Islamabad") if "Islamabad" in city_names else 0
    selected_city = st.selectbox("Select a location", city_names, index=default_index)

    loc_row = locations[locations["city"] == selected_city].iloc[0].to_dict()

    m = folium.Map(location=[30.3753, 69.3451], zoom_start=5, tiles="CartoDB positron")
    for _, row in locations.iterrows():
        is_selected = row["city"] == selected_city
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=9 if is_selected else 5,
            color="blue" if is_selected else "gray",
            fill=True,
            fill_opacity=0.8,
            popup=f"{row['city']}, {row['province']}",
        ).add_to(m)

    st_folium(m, width=None, height=450)

    st.caption(
        "Markers show sample Pakistan locations. Risk-zone shading and "
        "hazard-layer toggles are added in a later development stage."
    )
    return loc_row


def render_hazard_analysis(loc_row: dict):
    st.header("📊 Hazard Analysis")
    st.caption(f"Location: {loc_row['city']}, {loc_row['district']}, {loc_row['province']}")

    snapshot = build_environmental_snapshot(loc_row, seed=hash(loc_row["city"]) % (2**31))

    st.info(snapshot["data_quality_note"])
    if snapshot["missing_sources"]:
        st.warning(f"Sources that failed or returned no data: {', '.join(snapshot['missing_sources'])}")

    with st.expander("Raw environmental snapshot"):
        st.dataframe(snapshot_to_dataframe(snapshot), use_container_width=True)

    tabs = st.tabs(["🌊 Flood", "🔥 Heatwave", "🏜️ Drought"])
    predictors = [
        ("flood", predict_flood_risk),
        ("heatwave", predict_heatwave_risk),
        ("drought", predict_drought_risk),
    ]

    for tab, (hazard, predict_fn) in zip(tabs, predictors):
        with tab:
            result = predict_fn(snapshot)
            render_risk_card(hazard, result, loc_row, snapshot)


def render_risk_card(hazard: str, result: dict, loc_row: dict, snapshot: dict):
    category = result["risk_category"]
    color = RISK_COLORS.get(category, "gray")

    c1, c2 = st.columns([1, 2])
    with c1:
        if result["risk_score"] is not None:
            st.markdown(f"### Risk index: **{result['risk_score']} / 100**")
            st.markdown(f"### Category: :{color}[{category}]")
        else:
            st.markdown(f"### {category}")
        st.caption(
            "This is a prototype risk **index**, not a calibrated real-world "
            "probability. It will be replaced by a trained model with "
            "evaluation metrics in a later stage."
        )
        st.caption(f"Model version: {result['model_version']} | Horizon: {result['prediction_horizon_hours']}h")

    with c2:
        if result["contributing_factors"]:
            st.markdown("**Contributing factors used:**")
            for f in result["contributing_factors"]:
                val = snapshot["readings"].get(f)
                st.markdown(f"- `{f}` = {val}")
        else:
            st.markdown("_No contributing factors available for this hazard yet._")

    explanation = generate_explanation(hazard, result, loc_row)
    with st.expander("AI explanation (fallback mode)"):
        st.write(explanation["explanation"])
        st.markdown("**Preventive guidance (placeholder):**")
        for rec in explanation["recommendations"]:
            st.markdown(f"- {rec}")
        st.markdown("**Limitations:**")
        for lim in explanation["limitations"]:
            st.caption(f"⚠️ {lim}")


def render_about():
    st.header("ℹ️ Data & Model Information")
    st.markdown(
        """
        **Current build stage:** Stage 1 — Foundation

        - All environmental readings are **simulated sample data**, generated
          locally for demonstration only.
        - Flood, heatwave, and drought risk values are a transparent
          **prototype weighted index (0–100)**, not a trained, validated
          model and not a calibrated probability.
        - The RAG (FAISS) knowledge base and Gemini explanation layer are
          not yet connected — see `rag_system.py` for the planned interface.
        - Real data sources (PMD, NASA GPM IMERG, Copernicus ERA5/Sentinel,
          WAPDA river data, NDMA/PDMA hazard records) require registration
          or manual download and are integrated in later stages.
        """
    )
    st.caption(f"Risk categories used: {', '.join(RISK_CATEGORIES)}")


def main():
    page = st.sidebar.radio(
        "Sections",
        ["Overview", "Climate Risk Map & Hazard Analysis", "Data & Model Information"],
    )

    if page == "Overview":
        render_overview()
    elif page == "Climate Risk Map & Hazard Analysis":
        loc_row = render_map_and_selection()
        render_hazard_analysis(loc_row)
    else:
        render_about()


if __name__ == "__main__":
    main()
