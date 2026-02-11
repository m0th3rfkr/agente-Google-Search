# extractors/place_details.py
import requests
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_place_details(place_id: str):
    """
    Obtiene detalles de un lugar usando Google Places Details API.
    Devuelve rating, total de reseñas y una muestra de reviews.
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY no está configurada")

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,types,formatted_address,url,reviews",
        "reviews_sort": "newest",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    result = data.get("result")
    if not result:
        raise ValueError(f"No se pudieron obtener detalles para place_id: {place_id}")

    return {
        "place_id": place_id,
        "name": result.get("name"),
        "rating": result.get("rating"),
        "reviews_count": result.get("user_ratings_total"),
        "address": result.get("formatted_address"),
        "maps_url": result.get("url"),
        "reviews": result.get("reviews", [])
    }
