# core/config.py
import os
from dotenv import load_dotenv

# Charger le fichier .env une seule fois
load_dotenv()

# Récupération des variables d'environnement avec valeurs par défaut
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "cdn")
WEBDAV_HOSTNAME = os.getenv("WEBDAV_HOSTNAME")
WEBDAV_LOGIN = os.getenv("WEBDAV_LOGIN")
WEBDAV_PASSWORD = os.getenv("WEBDAV_PASSWORD")

def show_config_summary():
    """Affiche un résumé utile pour le debug."""
    print("\n⚙️  Configuration chargée :")
    print(f"   📁 Dossier de sortie : {DOWNLOAD_DIR}")
    print(f"   🌐 WebDAV Hostname : {WEBDAV_HOSTNAME}")
