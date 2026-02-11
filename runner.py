# runner.py
import json
import os

from extractors.geocode import geocode_location
from extractors.places_search import search_places
from extractors.place_details import get_place_details
from composer.report_builder import build_report


def main():
    # 1) Inputs (por ahora aquí mismo)
    keyword = "meat market"
    location_text = "Houston, TX"
    radius_m = 30000
    top_n = 6

    # 2) Geocode
    geo = geocode_location(location_text)
    lat = geo["lat"]
    lng = geo["lng"]
    formatted_location = geo.get("formatted_address") or location_text

    # 3) Search places
    places = search_places(keyword, lat, lng, radius_m=radius_m)
    places = [p for p in places if p.get("place_id")][:top_n]

    # 4) Details (rating, reviews sample, etc.)
    places_details = []
    for p in places:
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

    # 5) Raw output
    raw = {
        "keyword": keyword,
        "location_text": location_text,
        "formatted_location": formatted_location,
        "center": {"lat": lat, "lng": lng},
        "radius_m": radius_m,
        "top_n": top_n,
        "places": places_details
    }

    # 6) Report output (template estable)
    report = build_report(keyword, location_text, formatted_location, places_details)

    # 7) Save outputs
    os.makedirs("outputs", exist_ok=True)

    with open("outputs/raw.json", "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

    with open("outputs/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("✅ Listo. Archivos generados:")
    print("- outputs/raw.json")
    print("- outputs/report.json")


if __name__ == "__main__":
    main()
