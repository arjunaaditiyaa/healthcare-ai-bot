import requests
from sqlmodel import Session, select
from models import DiseaseOutbreak
from db import engine
from datetime import datetime

KNOWN_COUNTRIES = [
    "India", "China", "United States", "USA", "Brazil",
    "Egypt", "Nigeria", "Kenya", "Pakistan", "Bangladesh",
    "Indonesia", "Philippines", "South Africa", "Uganda",
    "Nepal", "Sri Lanka", "Japan", "Thailand", "Vietnam"
]


def extract_country(text: str) -> str:
    for c in KNOWN_COUNTRIES:
        if c.lower() in text.lower():
            return c
    return "Unknown"

def fetch_outbreaks():
    url = "https://www.who.int/api/news/diseaseoutbreaknews"
    current_year = datetime.now().year

    try:
        r = requests.get(
            url,
            headers={"User-Agent": "HealthcareBot/1.0"},
            timeout=10
        )

        if r.status_code != 200:
            return []

        data = r.json().get("value", [])

    except Exception as e:
        print("WHO API error:", e)
        return []

    outbreaks = []

    with Session(engine) as s:
        for d in data:
            title = d.get("Title", "")
            overview = d.get("Overview", "")

            year_str = d.get("PublicationDate", "0000")[:4]
            if not year_str.isdigit():
                continue

            year = int(year_str)

            # 🔴 FILTER: ONLY RECENT (≤ 1 YEAR)
            if current_year - year > 1:
                continue

            disease = title.split("–")[0].strip() or "Unknown"
            country = extract_country(title + " " + overview)
            summary = overview

            exists = s.exec(
                select(DiseaseOutbreak).where(
                    DiseaseOutbreak.disease == disease,
                    DiseaseOutbreak.year == year,
                    DiseaseOutbreak.country == country
                )
            ).first()

            if exists:
                o = exists
            else:
                o = DiseaseOutbreak(
                    disease=disease,
                    country=country,
                    year=year,
                    summary=summary,
                    source_url=d.get("ItemDefaultUrl", "https://www.who.int")
                )
                s.add(o)
                s.commit()
                s.refresh(o)

            outbreaks.append({
                "disease": o.disease,
                "year": o.year,
                "country": o.country,
                "summary": o.summary
            })

    return outbreaks

