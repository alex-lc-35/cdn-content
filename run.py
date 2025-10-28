""" run.py """
from webdav_client import get_client
from init import load_initial_json
from webdav_utils import download_active_files_for_ids
import os

# Chargement du JSON original
json_path = "data.json"
config = load_initial_json(json_path)

# Création du client WebDAV
client = get_client()

# Préparer le dossier local
download_dir = os.getenv("DOWNLOAD_DIR", "cdn")
os.makedirs(download_dir, exist_ok=True)

# Lancer le processus complet
download_active_files_for_ids(client, config, download_dir)
