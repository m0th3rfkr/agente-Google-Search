# extractors/places_search.py
import requests
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def search_places(keyword: str, lat: float, lng: float, radius_m: int = 30000):
    """
    Busca lugares en Google Places (Text Search) usando:
    - keyword (ej. 'meat market')
    - centro (lat, lng)
    - radio en metros
    Devuelve una lista de resultados con place_id y nombre.
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY no está configurada")

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": keyword,
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    results = data.get("results") or []

    places = []
    for r in results:
        places.append({
            "place_id": r.get("place_id"),
            "name": r.get("name"),
            "formatted_address": r.get("formatted_address")
        })

    return places
