# Agente Google Search – Local SEO

Este proyecto es un **agente automatizado** que analiza búsquedas locales en Google
usando **keyword** y **ubicación** como inputs, y genera un **reporte estructurado**
para análisis SEO y Google My Business.

El objetivo es replicar un análisis humano de Google Search / Maps,
pero de forma automática y consistente, para que otros agentes puedan
consumir el resultado después.

---

## 🧠 Qué hace este agente

Dado:
- una **keyword** (ej. `meat market`)
- una **ubicación** (ej. `Houston, TX`)

El agente:
1. Busca negocios relevantes en Google Maps (Places API)
2. Obtiene rating, número de reseñas y una muestra de reviews
3. Analiza las reseñas para detectar:
   - productos más mencionados
   - insights básicos
4. Genera un **reporte en JSON** con secciones fijas:
   - Optimización SEO
   - Análisis competitivo
   - Tabla comparativa
   - Insight estratégico
   - Plan de acción GMB

---

## 📦 Output

El agente genera dos archivos:

- `outputs/raw.json`  
  → datos crudos obtenidos de Google

- `outputs/report.json`  
  → reporte final estructurado (consumible por otros agentes)

---

## 🔑 Requisitos

- Python 3.9+
- Una **Google API Key** con:
  - Places API
  - Geocoding API

---

## ⚙️ Configuración

1. Crear un archivo `.env` en la raíz del proyecto:

```env
GOOGLE_API_KEY=tu_api_key_aqui
