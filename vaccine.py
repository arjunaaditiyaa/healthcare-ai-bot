import requests
from sqlmodel import Session, select
from models import VaccineInfo
from db import engine

WHO_VACCINE_URL = "https://www.who.int/teams/immunization-vaccines-and-biologicals"

def get_vaccine_schedule(disease: str):
    with Session(engine) as s:
        existing = s.exec(
            select(VaccineInfo).where(VaccineInfo.disease == disease.lower())
        ).first()

        if existing:
            return existing

    # 🔒 SAFE STATIC FALLBACK (ONLY VERIFIED)
    known = {
        "polio": {
            "vaccine": "OPV / IPV",
            "age": "0–5 years",
            "schedule": "At birth, 6, 10, 14 weeks",
            "doses": 4
        },
        "measles": {
            "vaccine": "MMR",
            "age": "9 months – 15 months",
            "schedule": "2 doses",
            "doses": 2
        }
    }

    data = known.get(disease.lower())
    if not data:
        return None

    info = VaccineInfo(
        disease=disease.lower(),
        vaccine_name=data["vaccine"],
        age_group=data["age"],
        schedule=data["schedule"],
        doses=data["doses"],
        source="WHO"
    )

    with Session(engine) as s:
        s.add(info)
        s.commit()
        s.refresh(info)

    return info
