# ui_app.py
import json
import os
import time
import requests
import streamlit as st

from extractors.geocode import geocode_location
from extractors.places_search import search_places
from extractors.place_details import get_place_details
from composer.report_builder import build_report

st.set_page_config(page_title="Agente Google Search UI", layout="wide")

# ------------------------
# SESSION STATE
# ------------------------
if "raw" not in st.session_state:
    st.session_state.raw = None
if "report" not in st.session_state:
    st.session_state.report = None
if "elapsed" not in st.session_state:
    st.session_state.elapsed = None

# ------------------------
# AUTOCOMPLETE FUNCTION
# ------------------------
def location_suggestions(text: str):
    if not text or len(text) < 2:
        return []

    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return []

    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": text,
        "types": "(cities)",
        "key": key
    }

    r = requests.get(url, params=params, timeout=20).json()
    predictions = r.get("predictions") or []
    return [p.get("description") for p in predictions]

# ------------------------
# UI
# ------------------------
st.title("Agente Google Search – UI")
st.caption("Keyword + ubicación → análisis automático SEO")

with st.sidebar:
    st.header("Parámetros")

    keyword = st.text_input("Keyword", value="meat market")

    location_text = st.text_input("Ubicación", value="Houston, TX", key="loc_input")

    suggestions = location_suggestions(location_text)
    if suggestions:
        selected = st.selectbox("Sugerencias", suggestions)
        if selected != location_text:
            st.session_state.loc_input = selected
            location_text = selected

    radius_m = st.number_input("Radio (metros)", min_value=1000, max_value=100000, value=30000, step=1000)
    top_n = st.number_input("Top N negocios", min_value=1, max_value=20, value=6)

    st.divider()
    api_ok = bool(os.getenv("GOOGLE_API_KEY"))
    st.write("API Key:", "✅ Detectada" if api_ok else "❌ No detectada")

run = st.button("🚀 Correr agente", use_container_width=True)

# ------------------------
# RUN AGENT
# ------------------------
if run:
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("No hay GOOGLE_API_KEY configurada.")
        st.stop()

    start_time = time.time()
    progress = st.progress(0)

    # Geocode
    progress.progress(15)
    geo = geocode_location(location_text)
    lat = geo["lat"]
    lng = geo["lng"]
    formatted_location = geo.get("formatted_address") or location_text

    # Search places
    progress.progress(35)
    places = search_places(keyword, lat, lng, radius_m=int(radius_m))
    places = [p for p in places if p.get("place_id")][: int(top_n)]

    # Details
    progress.progress(60)
    places_details = []
    for p in places:
        try:
            details = get_place_details(p["place_id"])
            places_details.append(details)
        except Exception:
            continue

    # Build report
    progress.progress(85)
    raw = {
        "keyword": keyword,
        "location_text": location_text,
        "formatted_location": formatted_location,
        "center": {"lat": lat, "lng": lng},
        "radius_m": int(radius_m),
        "top_n": int(top_n),
        "places": places_details
    }

    report = build_report(keyword, location_text, formatted_location, places_details)

    st.session_state.raw = raw
    st.session_state.report = report
    st.session_state.elapsed = time.time() - start_time

    progress.progress(100)

# ------------------------
# SHOW RESULTS
# ------------------------
if st.session_state.raw and st.session_state.report:
    st.success(f"Tiempo total: {st.session_state.elapsed:.2f} segundos")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Raw JSON")
        st.json(st.session_state.raw)
        st.download_button(
            "⬇ Descargar raw.json",
            json.dumps(st.session_state.raw, indent=2, ensure_ascii=False),
            "raw.json"
        )

    with col2:
        st.subheader("Reporte Final")
        st.json(st.session_state.report)
        st.download_button(
            "⬇ Descargar report.json",
            json.dumps(st.session_state.report, indent=2, ensure_ascii=False),
            "report.json"
        )
else:
    st.info("Corre el agente para ver resultados.")
