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
# AUTOCOMPLETE
# ------------------------
def location_suggestions(text: str):
    if not text or len(text) < 2:
        return []
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return []
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {"input": text, "types": "(cities)", "key": key}
    r = requests.get(url, params=params, timeout=20).json()
    preds = r.get("predictions") or []
    return [p.get("description") for p in preds if p.get("description")]

# ------------------------
# UI
# ------------------------
st.title("Agente Google Search – UI")
st.caption("Keyword + ubicación → análisis automático SEO (con sugerencias de ubicación)")

with st.sidebar:
    st.header("Parámetros")

    keyword = st.text_input("Keyword", value="meat market")
    typed_location = st.text_input("Ubicación (escribe)", value="Houston, TX")

    sugs = location_suggestions(typed_location)
    chosen_location = None
    if sugs:
        chosen_location = st.selectbox("Sugerencias (elige una)", ["(usar lo escrito)"] + sugs, index=0)

    # ubicación final que se usará al correr
    if chosen_location and chosen_location != "(usar lo escrito)":
        location_text = chosen_location
    else:
        location_text = typed_location

    radius_m = st.number_input("Radio (metros)", min_value=1000, max_value=100000, value=30000, step=1000)
    top_n = st.number_input("Top N negocios", min_value=1, max_value=20, value=6, step=1)

    st.divider()
    api_ok = bool(os.getenv("GOOGLE_API_KEY"))
    st.write("API Key:", "✅ Detectada" if api_ok else "❌ No detectada (export GOOGLE_API_KEY=...)")

run = st.button("🚀 Correr agente", type="primary", use_container_width=True)

# ------------------------
# RUN AGENT
# ------------------------
if run:
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("No hay GOOGLE_API_KEY configurada en el entorno.")
        st.stop()

    t0 = time.time()
    progress = st.progress(0, text="Iniciando...")

    progress.progress(15, text="Geocoding ubicación...")
    geo = geocode_location(location_text)
    lat = geo["lat"]
    lng = geo["lng"]
    formatted_location = geo.get("formatted_address") or location_text

    progress.progress(35, text="Buscando negocios (Places Text Search)...")
    places = search_places(keyword, lat, lng, radius_m=int(radius_m))
    places = [p for p in places if p.get("place_id")][: int(top_n)]

    progress.progress(60, text="Sacando detalles + reseñas (Place Details)...")
    places_details = []
    for i, p in enumerate(places, start=1):
        try:
            details = get_place_details(p["place_id"])
            places_details.append(details)
        except Exception as e:
            places_details.append({
                "place_id": p.get("place_id"),
                "name": p.get("name"),
                "rating": None,
                "reviews_count": None,
                "address": p.get("formatted_address"),
                "maps_url": None,
                "reviews": [],
                "error": str(e)
            })
        progress.progress(60 + int(25 * (i / max(1, len(places)))), text=f"Detalles: {i}/{len(places)}")

    progress.progress(90, text="Construyendo reporte...")
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
    st.session_state.elapsed = time.time() - t0

    progress.progress(100, text="Listo ✅")

# ------------------------
# SHOW RESULTS (no se borran al descargar)
# ------------------------
if st.session_state.raw and st.session_state.report:
    st.success(f"Tiempo total: {st.session_state.elapsed:.2f} segundos")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Raw JSON")
        st.json(st.session_state.raw)
        st.download_button(
            "⬇ Descargar raw.json",
            data=json.dumps(st.session_state.raw, ensure_ascii=False, indent=2),
            file_name="raw.json",
            mime="application/json",
            key="dl_raw"
        )

    with col2:
        st.subheader("Reporte Final")
        st.json(st.session_state.report)
        st.download_button(
            "⬇ Descargar report.json",
            data=json.dumps(st.session_state.report, ensure_ascii=False, indent=2),
            file_name="report.json",
            mime="application/json",
            key="dl_report"
        )
else:
    st.info("Corre el agente para ver resultados aquí.")
