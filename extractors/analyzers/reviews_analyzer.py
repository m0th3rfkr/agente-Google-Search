# analyzers/reviews_analyzer.py
import re
from collections import Counter

FOOD_TERMS = [
    "fajitas","fajita","chorizo","tacos","al pastor","pastor","tamales","barbacoa","menudo","carnitas",
    "ribeye","wagyu","tomahawk","picaña","bbq","sausage","brisket","seafood","shrimp","camarón",
    "tuétano","bone marrow"
]

def analyze_reviews(reviews: list):
    """
    Recibe una lista de reviews (como las devuelve Google Places)
    y devuelve:
    - top_products: lista de productos más mencionados
    - featured_testimonial: texto de testimonio destacado (el más largo)
    - urgent_negative: primera reseña negativa reciente (heurística simple)
    """
    texts = []
    for r in reviews or []:
        t = (r.get("text") or "").strip()
        if t:
            texts.append(t.lower())

    blob = " ".join(texts)

    # Top products
    counts = Counter()
    for term in FOOD_TERMS:
        hits = len(re.findall(rf"\b{re.escape(term.lower())}\b", blob))
        if hits:
            counts[term] += hits

    top_products = [{"product": k, "mentions": v} for k, v in counts.most_common(5)]

    # Featured testimonial (más largo)
    featured_testimonial = ""
    if reviews:
        best = None
        best_len = -1
        for r in reviews:
            txt = r.get("text") or ""
            if len(txt) > best_len:
                best_len = len(txt)
                best = r
        if best:
            featured_testimonial = best.get("text") or ""

    # Urgent negative (rating <=2 y reciente por texto tipo "day/día/week/semana")
    urgent_negative = None
    for r in reviews or []:
        rating = r.get("rating") or 0
        if rating <= 2:
            time_desc = (r.get("relative_time_description") or "").lower()
            if any(x in time_desc for x in ["day", "día", "días", "dias", "week", "semana"]):
                urgent_negative = r
                break

    return {
        "top_products": top_products,
        "featured_testimonial": featured_testimonial,
        "urgent_negative": urgent_negative
    }
