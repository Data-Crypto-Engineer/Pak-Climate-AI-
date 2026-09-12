"""
rag_system.py
--------------
Climate knowledge retrieval (FAISS + Sentence Transformers) and Gemini
explanation layer.

Stage 1 scope: a safe placeholder so app.py has a stable interface to call
against. No FAISS index, no embeddings, no Gemini call yet -- those are
built in Stage 5 (RAG) and wired to Gemini per the LLM-integration rules
(Gemini never invents data, never overrides the numerical model, and the
app must keep working if Gemini is unavailable).

May import: utilities.py, and later climate_models' processed results
Must NOT import: app.py
"""

from __future__ import annotations

from typing import Any, Dict, List

from utilities import LOGGER

FALLBACK_EXPLANATION = (
    "The AI explanation layer is not yet available in this build "
    "(RAG + Gemini are added in a later stage). Showing verified "
    "numerical model results only."
)


def retrieve_relevant_passages(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Stage 1 placeholder: returns an empty list until the FAISS index exists.
    Later: embed `query`, search FAISS, return passages with metadata
    (title, source, date, location, hazard_type, section).
    """
    LOGGER.info("RAG retrieval requested but not yet implemented (query=%r)", query)
    return []


def generate_explanation(
    hazard: str,
    risk_result: Dict[str, Any],
    location: Dict[str, Any],
    user_question: str | None = None,
) -> Dict[str, Any]:
    """
    Stage 1 placeholder for the Gemini explanation call.

    Returns a dict shaped the way the real implementation will:
        {explanation, recommendations, sources, limitations, llm_status}
    so app.py doesn't need to change when Gemini is wired in later.
    """
    return {
        "explanation": FALLBACK_EXPLANATION,
        "recommendations": [
            "Follow official NDMA / PDMA guidance for your area.",
            "This prototype does not yet generate AI-tailored recommendations.",
        ],
        "sources": [],
        "limitations": [
            "Explanation layer (Gemini + RAG) not yet implemented.",
            f"Risk category shown is a prototype index for '{hazard}', not a calibrated probability.",
        ],
        "llm_status": "not_implemented",
    }
