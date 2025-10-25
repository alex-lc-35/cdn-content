from webdav3.client import Client
from dotenv import load_dotenv
import os

# Charger les variables du .env
load_dotenv()

options = {
    "webdav_hostname": os.getenv("WEBDAV_HOSTNAME"),
    "webdav_login": os.getenv("WEBDAV_LOGIN"),
    "webdav_password": os.getenv("WEBDAV_PASSWORD"),
}

client = Client(options)

try:
    print("📡 Connexion à Framaspace…")
    files = client.list()  # racine
    print("✅ Connexion réussie !")
    print("📂 Contenu du dossier racine :")
    for f in files:
        print(" -", f)
except Exception as e:
    print(f"❌ Erreur : {e}")
