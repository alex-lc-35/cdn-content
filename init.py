""" init.py """
import json

def load_initial_json(json_path):
    """Charge simplement le fichier JSON initial et retourne la liste."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✅ JSON chargé ({len(data)} éléments)")
    return data
