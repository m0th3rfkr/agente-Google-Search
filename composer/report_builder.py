# composer/report_builder.py
import urllib.parse
from analyzers.reviews_analyzer import analyze_reviews

def build_report(keyword: str, location_text: str, formatted_location: str, places_details: list):
    """
    Construye el reporte con secciones fijas (template estable),
    usando keyword + ubicación y la lista de lugares con detalles.
    """

    google_search_url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(f"{keyword} {location_text}")

    # Si no hay lugares, regresamos reporte mínimo
    if not places_details:
        return {
            "seo_optimization": {
                "query": f"{keyword} | {formatted_location}",
                "google_search_url": google_search_url,
                "current_position": None,
                "target_top": 10,
                "objective_6_months": "Top 10",
                "potential_clients_per_month": 0,
                "projected_annual_revenue": ""
            },
            "competitive_reviews": {
                "reviews_analyzed_total": 0,
                "premium_quality_comparison": [],
                "client_top_products": [],
                "featured_testimonial": {"text": "", "source_place": ""}
            },
            "places_detail": [],
            "comparison_table": [],
            "strategic_insight": {
                "headline": "Ultra Premium vs Premium Prime: oportunidad real",
                "what_they_value": ["Calidad Prime","Frescura garantizada","Servicio personalizado","Precios justos"],
                "what_they_dont_mention": ["Wagyu","Tomahawk","Picaña"]
            },
            "gmb_plan": {
                "actions": [],
                "vip_opportunity": {"reviewer":"","profile":"","situation":"","strategy":"","why_it_matters":""},
                "urgent_recovery": {"reviewer":"","problem":"","plan":"","related_complaints":[]},
                "goal": "Convertir review negativo en positivo"
            }
        }

    # Treat first result as CLIENTE por ahora (simple y estable)
    client = places_details[0]
    client_reviews = client.get("reviews", [])
    client_a = analyze_reviews(client_reviews)

    # total reviews analizadas (muestra)
    total_reviews_used = sum(len(p.get("reviews", [])) for p in places_details)

    # comparativa simple "calidad premium"
    comp = []
    for p in places_details:
        rating = p.get("rating") or 0
        total = p.get("reviews_count") or 0
        score = int(round(rating * 10 + min(20, (total ** 0.5))))
        comp.append({"name": p.get("name",""), "score": score})
    comp.sort(key=lambda x: x["score"], reverse=True)

    # acciones GMB base (estáticas por ahora)
    actions = [
        {"priority":"alta","title":"Subir MÁS fotografías","description":"Curaduría completa: preparación, staff, productos, instalaciones.","deliverable":"30+ fotos por ubicación"},
        {"priority":"alta","title":"Campaña de Keywords","description":"Optimizar señales y términos objetivo en el perfil.","deliverable":"Keywords + ejecución"},
        {"priority":"media","title":"Información Completa y Actualizada","description":"Auditoría de horarios, descripción, servicios.","deliverable":"Checklist 100%"},
        {"priority":"media","title":"Plan de Respuesta a Reviews","description":"Responder todas las reseñas en <24h.","deliverable":"Protocolo + templates"}
    ]

    urgent = client_a.get("urgent_negative")

    report = {
        "seo_optimization": {
            "query": f"{keyword} | {formatted_location}",
            "google_search_url": google_search_url,
            "current_position": 1,  # en este MVP: cliente = #1 de la lista
            "target_top": 10,
            "objective_6_months": "Top 10",
            "potential_clients_per_month": 0,
            "projected_annual_revenue": ""
        },
        "competitive_reviews": {
            "reviews_analyzed_total": total_reviews_used,
            "premium_quality_comparison": comp[:6],
            "client_top_products": client_a.get("top_products", []),
            "featured_testimonial": {
                "text": client_a.get("featured_testimonial",""),
                "source_place": client.get("name","")
            }
        },
        "places_detail": [],
        "comparison_table": [],
        "strategic_insight": {
            "headline": "Ultra Premium vs Premium Prime: oportunidad real",
            "what_they_value": ["Calidad Prime","Frescura garantizada","Servicio personalizado","Precios justos"],
            "what_they_dont_mention": ["Wagyu","Tomahawk","Picaña"]
        },
        "gmb_plan": {
            "actions": actions,
            "vip_opportunity": {"reviewer":"","profile":"","situation":"","strategy":"","why_it_matters":""},
            "urgent_recovery": {
                "reviewer": (urgent.get("author_name") if urgent else ""),
                "problem": (urgent.get("text") if urgent else ""),
                "plan": "Contacto personal + compensación + seguimiento para intentar edición/actualización de reseña",
                "related_complaints": []
            },
            "goal": "Convertir review negativo en positivo"
        }
    }

    # llenar places_detail + comparison_table
    for i, p in enumerate(places_details):
        a = analyze_reviews(p.get("reviews", []))
        role = "CLIENTE" if i == 0 else "Competencia"

        report["places_detail"].append({
            "name": p.get("name",""),
            "role": role,
            "rating": p.get("rating"),
            "reviews_count": p.get("reviews_count"),
            "strengths": [],
            "weaknesses": [],
            "top_products": a.get("top_products", [])
        })

        report["comparison_table"].append({
            "name": p.get("name",""),
            "role": role,
            "stars": [x["product"] for x in a.get("top_products", [])[:4]],
            "summary": "",
            "best_comment": a.get("featured_testimonial",""),
            "worst_finding": ""
        })

    return report
