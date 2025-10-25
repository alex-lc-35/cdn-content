from webdav_client import get_client
from init import load_initial_json
from webdave import download_active_files_for_ids
import os

# Chargement du JSON
config = load_initial_json("data.json")

# Création du client
client = get_client()

# Préparer le dossier local
download_dir = os.getenv("DOWNLOAD_DIR", "cdn")
os.makedirs(download_dir, exist_ok=True)

# Extraire les IDs
ids = [item["id"] for item in config]

# Télécharger les fichiers actifs
download_active_files_for_ids(client, ids, download_dir)
