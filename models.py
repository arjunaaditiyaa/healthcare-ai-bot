from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int
    country: str

class VaccineInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    disease: str
    vaccine_name: str
    age_group: str
    schedule: str
    doses: int
    source: str


class DiseaseSymptom(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    disease: str
    symptoms: str
    source: str

class DiseaseOutbreak(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    disease: str
    country: str
    year: int
    summary: str
    source_url: str
