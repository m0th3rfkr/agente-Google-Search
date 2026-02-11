# analyzers/reviews_analyzer.py
import re
from collections import Counter

FOOD_TERMS = [
    "fajitas","fajita","chorizo","tacos","al pastor","pastor","tamales",
    "barbacoa","menudo","carnitas","ribeye","wagyu","tomahawk","picaña",
    "bbq","sausage","brisket","seafood","shrimp","camarón",
    "tuétano","bone marrow"
]

def analyze_reviews(reviews: list):
    """
    Analiza una lista de reviews de Google Places y extrae:
    - productos más mencionados
    - testimonio destacado
    - reseña negativa reciente (si existe)
    """

    texts = []
    for r in reviews or []:
        text = (r.get("text") or "").strip()
        if text:
            texts.append(text.lower())

    blob = " ".join(texts)

    # Productos más mencionados
    counts = Counter()
    for term in FOOD_TERMS:
        hits = len(re.findall(rf"\b{re.escape(term.lower())}\b", blob))
        if hits:
            counts[term] += hits

    top_products = [
        {"product": k, "mentions": v}
        for k, v in counts.most_common(5)
    ]

    # Testimonio destacado (el más largo)
    featured_testimonial = ""
    best_len = -1
    for r in reviews or []:
        t = r.get("text") or ""
        if len(t) > best_len:
            best_len = len(t)
            featured_testimonial = t

    # Reseña negativa reciente
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
