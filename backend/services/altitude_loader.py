import json
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "puno_altitudes.json"

def get_altitude(city: str) -> int:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(city)
