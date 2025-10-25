import os

def download_active_files_for_ids(client, ids, download_dir):
    """
    Pour chaque id, cherche un dossier correspondant sur le WebDAV.
    Télécharge les fichiers commençant par active / active_sm / active_md.
    Renomme les fichiers localement en remplaçant 'active' par le nom du dossier.
    Retourne une liste d'informations sur les fichiers téléchargés.
    """
    print("\n🔍 Téléchargement des fichiers 'active' pour chaque dossier :")

    results = []

    for folder_id in ids:
        folder_path = f"{folder_id.strip('/')}/"
        print(f"\n📂 Dossier : {folder_path}")

        try:
            files = client.list(folder_path)
            if not files:
                print("   ⚠️ Dossier vide ou inaccessible.")
                continue

            # Filtrer les fichiers "active", "active_sm", "active_md"
            active_files = [
                f for f in files
                if not f.endswith("/") and (
                    f.lower().startswith("active")
                )
            ]

            if not active_files:
                print("   ⚠️ Aucun fichier 'active' trouvé.")
                continue

            for f in active_files:
                base_name = os.path.basename(f)
                ext = os.path.splitext(base_name)[1].lower()

                # Nouveau nom local selon le pattern trouvé
                if base_name.startswith("active_sm"):
                    new_name = f"{folder_id}_sm{ext}"
                elif base_name.startswith("active_md"):
                    new_name = f"{folder_id}_md{ext}"
                else:
                    new_name = f"{folder_id}{ext}"

                local_path = os.path.join(download_dir, new_name)
                remote_path = f"{folder_path}{f}".replace("//", "/")

                print(f"   ⬇️ Téléchargement de {remote_path} → {local_path}")
                client.download_sync(remote_path=remote_path, local_path=local_path)

                results.append({
                    "id": folder_id,
                    "filename": new_name,
                    "extension": ext.lstrip(".")
                })

        except Exception as e:
            print(f"   ❌ Erreur pour {folder_id} : {e}")

    # Résumé
    if results:
        print("\n📊 Récapitulatif :")
        for r in results:
            print(f" - {r['id']:<10} → {r['filename']:<25} ({r['extension']})")
    else:
        print("\n⚠️ Aucun fichier téléchargé.")

    return results
