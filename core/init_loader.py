# core/init_loader.py
import json
import os


def load_initial_json(json_path: str):
    """
    Charge le fichier JSON initial (config de base du projet).
    Retourne une liste d'items (ex: sections ou dossiers à synchroniser).

    Exemples d'entrée attendue :
    [
      { "id": "header", "title": "Header Section" },
      { "id": "footer", "title": "Footer Section" }
    ]
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ Le fichier '{json_path}' est introuvable.")

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Erreur de parsing JSON : {e}")

    if not isinstance(data, list):
        raise ValueError("❌ Le fichier JSON initial doit contenir une liste d'éléments (ex: [{...}, {...}]).")

    print(f"✅ JSON initial chargé ({len(data)} éléments) depuis '{json_path}'")
    return data
