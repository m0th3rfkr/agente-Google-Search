# extractors/geocode.py
import requests
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def geocode_location(location_text: str):
    """
    Convierte una ubicación en texto (ej. 'Houston, TX')
    en coordenadas latitud / longitud usando Google Geocoding API
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY no está configurada")

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_text,
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    if not data.get("results"):
        raise ValueError(f"No se pudo geocodificar la ubicación: {location_text}")

    location = data["results"][0]["geometry"]["location"]
    formatted_address = data["results"][0].get("formatted_address")

    return {
        "lat": location["lat"],
        "lng": location["lng"],
        "formatted_address": formatted_address
    }

