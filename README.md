# Climate Pakistan AI (Prototype — Stage 1: Foundation)

An AI-assisted climate-risk and early-warning **prototype** for Pakistan
covering flood, heatwave, and drought hazards.

> ⚠️ **This is a demonstration prototype, not an official government
> early-warning system.** All environmental data in this build stage is
> simulated sample data, clearly labeled as such throughout the app.

## What's implemented in Stage 1

- Six-file architecture (`utilities.py`, `data_sources.py`,
  `data_processing.py`, `climate_models.py`, `rag_system.py`, `app.py`)
  with a strict one-way dependency chain (see comments at the top of each
  file).
- A sample Pakistan location dataset (13 cities across all
  provinces/territories) and a basic Folium map.
- One function per environmental data source (`data_sources.py`), all
  currently returning clearly-labeled **simulated** data:
  weather, rainfall, river/water, satellite, elevation, historical hazards.
- A data-processing pipeline that runs every registered source for a
  selected location, merges the results, and reports which sources failed
  or returned nothing.
- Flood / heatwave / drought risk functions in `climate_models.py`. These
  currently compute a transparent **prototype weighted index (0–100)** —
  explicitly *not* a trained, validated model and *not* a calibrated
  probability. Real ML models (Random Forest / Gradient Boosting / XGBoost)
  are added in Stage 3+.
- A placeholder explanation layer (`rag_system.py`) with the exact
  interface the real FAISS + Gemini implementation will use later, so
  `app.py` won't need to change when that's wired in (Stage 5).
- A Streamlit UI with Overview, Map + Hazard Analysis, and Data/Model
  Information sections.

## Not yet implemented (planned in later stages)

- Real data sources (Pakistan Meteorological Department, NASA GPM IMERG,
  Copernicus ERA5/Sentinel, WAPDA river gauges, NDMA/PDMA hazard records).
  Several of these require registration or manual download — this will be
  documented here once integrated.
- Trained ML models with evaluation metrics (Stage 3, 6).
- FAISS vector index + Sentence Transformers embeddings over real climate
  documents (Stage 5).
- Gemini-powered explanations and preventive recommendations (Stage 5),
  read from `st.secrets["GEMINI_API_KEY"]` — **never** hardcoded, and the
  numerical dashboard will keep working if Gemini is unavailable.
- Full data validation/cleaning pipeline, cumulative rainfall and anomaly
  calculations, risk-zone map layers, and early-warning alert cards.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Running in Google Colab (with a tunnel for local testing)

```bash
!pip install -r requirements.txt -q
!streamlit run app.py &>/content/logs.txt &
# then expose the local Streamlit port (e.g. 8501) with your tunnel tool
# of choice (Cloudflare Tunnel, localtunnel, etc.)
```

## Configuring the Gemini API key (for later stages)

When the Gemini explanation layer is wired in, add this to
`.streamlit/secrets.toml` (never commit this file):

```toml
GEMINI_API_KEY = "YOUR_SECRET_KEY"
```

End users of the deployed app are never asked to enter an API key.

## Project structure

```text
climate_pakistan_ai/
├── app.py                # Streamlit UI (imports everything else)
├── data_sources.py       # One function per data source + registry
├── data_processing.py    # Load -> validate -> clean -> derive features
├── climate_models.py     # Flood / heatwave / drought risk functions
├── rag_system.py         # FAISS + Gemini explanation layer (placeholder)
├── utilities.py          # Shared helpers (no project imports)
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── sample/
│   ├── raw/
│   └── processed/
└── models/
```

## Test checklist (Stage 1)

- [ ] `pip install -r requirements.txt` succeeds
- [ ] `streamlit run app.py` starts without errors
- [ ] Overview page loads and shows the simulated-data warning
- [ ] Map page shows all sample cities as markers
- [ ] Selecting a different city updates the highlighted marker
- [ ] Hazard Analysis tabs show a risk index + category for flood, heatwave,
      and drought for the selected city
- [ ] Data quality note and any "missing sources" warning are visible
- [ ] About/Data page clearly states the current build stage and limitations
