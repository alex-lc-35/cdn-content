from webdav3.client import Client
from dotenv import load_dotenv
import os

load_dotenv()

options = {
    "webdav_hostname": os.getenv("WEBDAV_HOSTNAME"),
    "webdav_login": os.getenv("WEBDAV_LOGIN"),
    "webdav_password": os.getenv("WEBDAV_PASSWORD"),
}

client = Client(options)

download_dir = os.getenv("DOWNLOAD_DIR", "cdn")
os.makedirs(download_dir, exist_ok=True)

try:
    print("📡 Connexion à Framaspace…")
    files = client.list()  # racine
    print("✅ Connexion réussie !")

    for f in files:
        if not f.endswith("/"):
            local_path = os.path.join(download_dir, os.path.basename(f))
            print(f"⬇️ Téléchargement de {f} → {local_path}")
            client.download_sync(remote_path=f, local_path=local_path)

    print(f"✅ Tous les fichiers ont été téléchargés dans '{download_dir}'")

except Exception as e:
    print(f"❌ Erreur : {e}")
