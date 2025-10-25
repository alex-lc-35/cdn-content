from webdav3.client import Client
from dotenv import load_dotenv
import os
import shutil

from webdav_utils import download_active_files  # ← fonction externe

load_dotenv()

options = {
    "webdav_hostname": os.getenv("WEBDAV_HOSTNAME"),
    "webdav_login": os.getenv("WEBDAV_LOGIN"),
    "webdav_password": os.getenv("WEBDAV_PASSWORD"),
}

client = Client(options)
download_dir = os.getenv("DOWNLOAD_DIR", "cdn")

# 🧹 Nettoyage du dossier local
if os.path.exists(download_dir):
    print(f"🧹 Suppression du contenu de '{download_dir}'…")
    shutil.rmtree(download_dir)
os.makedirs(download_dir, exist_ok=True)

print("📡 Connexion à Framaspace…")
items = client.list()
print("✅ Connexion réussie !")

# Ignorer le dossier courant (souvent premier élément)
folders = [item for item in items[1:] if item.endswith("/")]

if not folders:
    print("⚠️ Aucun dossier trouvé.")
else:
    print(f"📁 {len(folders)} dossier(s) trouvé(s) :")
    for d in folders:
        print(f" - {d}")

    print("\n🔍 Recherche et téléchargement des fichiers 'active'...\n")
    download_active_files(client, folders, download_dir)

    print(f"\n✅ Téléchargements terminés dans '{download_dir}'.")
