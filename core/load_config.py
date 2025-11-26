""" core/sync_active_params.py """

import os
from webdav.repo import list_folder, get_info, download_file
from processors.ods_processor import OdsProcessor


def sync_active_params_data(client, download_dir):
    """
    Recherche params/active.ods, le télécharge, le parse,
    et retourne directement les données Python (list[dict]).
    """
    print("\n🔍 Chargement des paramètres ...")

    os.makedirs(download_dir, exist_ok=True)

    folder = "params/"
    files, error = list_folder(client, folder)

    if error:
        print(f"⚠️ Impossible de lister {folder} : {error}")
        return None

    # Trouver active.ods (case insensitive)
    target = next((f for f in files if f.lower() == "active.ods"), None)

    if not target:
        print("⚠️ Aucun fichier active.ods trouvé dans params/")
        return None

    print(f"📄 Fichier trouvé : {target}")

    # Téléchargement
    remote_path = f"{folder}{target}"
    temp_path = os.path.join(download_dir, "__temp.ods")
    print("   ⬇️ Téléchargement...")
    download_file(client, remote_path, temp_path)


    # Récupération des données
    processor = OdsProcessor()
    data = processor.parse_to_python(temp_path)

    print(f"   ✅ Config chargée ({len(data)} lignes)")

    return data
