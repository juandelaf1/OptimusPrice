import sys, re, json, time
sys.path.insert(0, r"C:\Users\JUAN\Desktop\Proyectos\Optimus_Price_Final")
from raspal import Fetcher, AutoThrottle, Extractor
from raspal.models import LLMConfig
import requests

GROQ_API_KEY = ""  # Set via environment variable
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def groq_extract(text, schema):
    prompt = f"""Extract hotel pricing information from the following HTML text.
Return ONLY a JSON object with these fields: {json.dumps(schema)}

Text (first 3000 chars):
{text[:3000]}

Return ONLY valid JSON. No explanation."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 500,
    }
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

f = Fetcher(throttle=AutoThrottle(min_delay=2, max_delay=5))
ext = Extractor()

url = "https://www.booking.com/searchresults.html?ss=Madrid&checkin=2026-07-01&checkout=2026-07-02&group_adults=2&no_rooms=1"
print("Fetching booking.com...")
r = f.fetch(url, engine="stealth", timeout=15000)
print(f"HTML: {len(r.html) if r.html else 0} bytes")

if r.html:
    text = ext.extract_text(r.html)
    print(f"Extracted text: {len(text) if text else 0} chars")
    if text:
        print(f"Preview: {text[:300]}")
        print("\n--- Groq extraction ---")
        result = groq_extract(text, {
            "hotels": [{"name": "", "price": 0, "currency": "", "rating": 0}]
        })
        print(json.dumps(result, indent=2))
