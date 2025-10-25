import os

def download_active_files(client, folders, download_dir):
    """
    Parcourt chaque dossier du WebDAV et télécharge les fichiers
    dont le nom commence par 'active' ou 'active_'.
    Le fichier local est renommé en remplaçant 'active' par le nom du dossier,
    tout en conservant le suffixe et l'extension.
    Exemple : about/active_sm.png → cdn/about_sm.png
    """
    for folder in folders:
        print(f"📂 Dossier : {folder}")
        try:
            files = client.list(folder)
            active_files = [
                f for f in files
                if not f.endswith("/") and f.lower().startswith("active")
            ]

            if not active_files:
                print("   ⚠️ Aucun fichier 'active' trouvé.")
                continue

            for f in active_files:
                # Nom du dossier (ex: about)
                folder_name = folder.strip("/").split("/")[-1]

                # Nom de fichier distant (ex: active_sm.png)
                base_name = os.path.basename(f)

                # Nouveau nom local : remplace "active" au début par le nom du dossier
                new_name = base_name.replace("active", folder_name, 1)
                local_path = os.path.join(download_dir, new_name)
                remote_path = f"{folder}{f}".replace("//", "/")

                print(f"   ⬇️ Téléchargement de {remote_path} → {local_path}")
                client.download_sync(remote_path=remote_path, local_path=local_path)

        except Exception as e:
            print(f"   ❌ Erreur en listant {folder} : {e}")
