# ui_app.py
import json
import os
import time
import streamlit as st

from extractors.geocode import geocode_location
from extractors.places_search import search_places
from extractors.place_details import get_place_details
from composer.report_builder import build_report

st.set_page_config(page_title="Agente Google Search UI", layout="wide")

st.title("Agente Google Search – UI")
st.caption("Mete keyword + ubicación, corre el agente, ve tiempos y outputs (raw/report).")

with st.sidebar:
    st.header("Parámetros")
    keyword = st.text_input("Keyword", value="meat market")
    location_text = st.text_input("Ubicación", value="Houston, TX")
    radius_m = st.number_input("Radio (metros)", min_value=1000, max_value=100000, value=30000, step=1000)
    top_n = st.number_input("Top N negocios", min_value=1, max_value=20, value=6, step=1)

    st.divider()
    st.write("API Key (status)")
    api_ok = bool(os.getenv("GOOGLE_API_KEY"))
    st.write("✅ Detectada" if api_ok else "❌ No detectada (export GOOGLE_API_KEY=...)")

run = st.button("🚀 Correr agente", type="primary", use_container_width=True)

if run:
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("No hay GOOGLE_API_KEY en el entorno. Exporta la variable y vuelve a correr.")
        st.stop()

    t0 = time.time()
    progress = st.progress(0, text="Iniciando...")

    # 1) Geocode
    progress.progress(10, text="Geocoding ubicación...")
    geo = geocode_location(location_text)
    lat = geo["lat"]
    lng = geo["lng"]
    formatted_location = geo.get("formatted_address") or location_text

    # 2) Search places
    progress.progress(30, text="Buscando negocios (Places Text Search)...")
    places = search_places(keyword, lat, lng, radius_m=int(radius_m))
    places = [p for p in places if p.get("place_id")][: int(top_n)]

    # 3) Details
    progress.progress(55, text="Sacando detalles + reseñas (Place Details)...")
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
        progress.progress(55 + int(35 * (i / max(1, len(places)))), text=f"Detalles: {i}/{len(places)}")

    # 4) Build outputs
    progress.progress(93, text="Construyendo reporte...")
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

    elapsed = time.time() - t0
    progress.progress(100, text="Listo ✅")

    st.success(f"Listo. Tiempo total: {elapsed:.2f} segundos")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Raw (datos crudos)")
        st.json(raw)
        st.download_button(
            "⬇️ Descargar raw.json",
            data=json.dumps(raw, ensure_ascii=False, indent=2),
            file_name="raw.json",
            mime="application/json"
        )

    with col2:
        st.subheader("Report (reporte final)")
        st.json(report)
        st.download_button(
            "⬇️ Descargar report.json",
            data=json.dumps(report, ensure_ascii=False, indent=2),
            file_name="report.json",
            mime="application/json"
        )
