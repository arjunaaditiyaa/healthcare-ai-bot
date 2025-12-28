import requests

def find_hospitals(city):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"hospitals in {city}",
        "format": "json",
        "limit": 3
    }
    r = requests.get(
        url,
        headers={"User-Agent": "HealthcareBot/1.0"},
        timeout=10,params= params
    )

    try:
        return r.json()
    except Exception:
        return []

