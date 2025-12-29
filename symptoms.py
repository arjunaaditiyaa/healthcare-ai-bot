from sqlmodel import Session, select
from models import DiseaseSymptom
from db import engine


def get_symptoms(disease: str):
    with Session(engine) as s:
        existing = s.exec(
            select(DiseaseSymptom).where(DiseaseSymptom.disease == disease.lower())
        ).first()

        if existing:
            return existing.symptoms

    base = {
        "polio": "Fever, fatigue, headache, vomiting, neck stiffness, limb weakness",
        "measles": "High fever, cough, runny nose, red eyes, rash",
        "covid-19": "Fever, cough, fatigue, loss of taste or smell"
    }

    symptoms = base.get(disease.lower())
    if not symptoms:
        return None

    obj = DiseaseSymptom(
        disease=disease.lower(),
        symptoms=symptoms,
        source="WHO/CDC"
    )

    with Session(engine) as s:
        s.add(obj)
        s.commit()

    return symptoms
