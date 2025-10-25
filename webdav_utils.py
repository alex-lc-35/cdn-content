import os

def download_active_files(client, folders, download_dir):
    """
    Parcourt chaque dossier du WebDAV, télécharge les fichiers
    dont le nom commence par 'active' ou 'active_'.
    Les fichiers sont renommés en remplaçant 'active' par le nom du dossier.
    Retourne une liste d'infos sur les fichiers téléchargés.
    """
    results = []

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
                folder_name = folder.strip("/").split("/")[-1]
                base_name = os.path.basename(f)
                new_name = base_name.replace("active", folder_name, 1)
                local_path = os.path.join(download_dir, new_name)
                remote_path = f"{folder}{f}".replace("//", "/")

                ext = os.path.splitext(base_name)[1].lower()

                print(f"   ⬇️ Téléchargement de {remote_path} → {local_path}")
                client.download_sync(remote_path=remote_path, local_path=local_path)

                # Ajouter une entrée dans le tableau
                results.append({
                    "folder": folder_name,
                    "filename": new_name,
                    "extension": ext
                })

        except Exception as e:
            print(f"   ❌ Erreur en listant {folder} : {e}")

    # Afficher un résumé à la fin
    if results:
        print("\n📊 Récapitulatif des fichiers téléchargés :")
        for r in results:
            print(f" - {r['folder']:<15} → {r['filename']:<25} ({r['extension']})")
    else:
        print("\n⚠️ Aucun fichier téléchargé.")

    return results
