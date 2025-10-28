""" core/state_store.py """

import os, json

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def load_previous(download_dir):
    path = os.path.join(download_dir, "data_updated.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_current(download_dir, updated):
    path = os.path.join(download_dir, "data_updated.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
