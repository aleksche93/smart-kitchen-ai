import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "flavors.json"


def load_flavors():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_pairings(ingredient: str, flavors: dict):
    entry = flavors.get(ingredient)
    if not entry:
        return None

    return {
        "label_uk": entry.get("label_uk"),
        "strong": [s for s in entry.get("strong", [])],
        "good": [g for g in entry.get("good", [])],
        "affinities": entry.get("affinities", []),
        "metadata": entry.get("metadata", {})
    }