""" core/sync_pipeline.py """

import os, shutil
from core.state_store import load_previous, save_current
from core.naming import normalize_id, detect_key, final_name
from webdav.repo import list_folder, get_info, download_file
from processors import get_processor_for

def sync_active_files(client, config, download_dir):
    print("\n🔍 Synchronisation des fichiers actifs...")
    previous_data = load_previous(download_dir)
    updated = []
    total_downloaded, total_errors = 0, 0

    for item in config:
        folder_id = normalize_id(item["id"])
        folder_path = f"{folder_id}/"
        print(f"\n📂 Dossier : {folder_path}")

        prev_item = next((i for i in previous_data if i["id"].strip("/") == folder_id), None)
        prev_meta = (prev_item.get("meta") or {}) if prev_item else {}
        new_item = (prev_item.copy() if prev_item else item.copy())
        new_item.update({"error": None, "meta": prev_meta.copy(), "load": False})

        active_files, error = list_folder(client, folder_path)
        if error:
            print(f"   ⚠️ {error}")
            new_item["error"] = error
            total_errors += 1
            updated.append(new_item)
            continue

        for f in active_files:
            base_name = os.path.basename(f)
            ext = os.path.splitext(base_name)[1].lstrip(".").lower()
            suffix, key = detect_key(base_name)
            remote_path = f"{folder_path}{f}".replace("//", "/")

            info = get_info(client, remote_path)
            etag, lastmod = info.get("etag"), info.get("lastmod")
            prev_info = prev_meta.get(key, {})

            # Comparaison
            if prev_info.get("etag") == etag or (not etag and prev_info.get("lastmod") == lastmod):
                print(f"   ⏩ {base_name} inchangé")
                continue

            # Téléchargement
            print(f"   ⬇️ Téléchargement de {base_name}")
            temp_path = os.path.join(download_dir, f"__temp.{ext}")
            download_file(client, remote_path, temp_path)

            # Traitement
            processor = get_processor_for(ext)
            if not processor:
                msg = f"Extension '{ext}' non gérée."
                print(f"   ⚠️ {msg}")
                new_item["error"] = msg
                total_errors += 1
                continue

            temp_path, ext = processor.process(temp_path, download_dir, folder_id, suffix, ext)

            # Nom final et déplacement
            final = final_name(folder_id, suffix, etag, lastmod, ext)
            shutil.move(temp_path, os.path.join(download_dir, final))

            # Mise à jour
            new_item[key] = final
            new_item["meta"][key] = {"etag": etag, "lastmod": lastmod}
            new_item["load"] = True
            total_downloaded += 1

        updated.append(new_item)

    save_current(download_dir, updated)
    print(f"\n✅ Synchronisation terminée : {total_downloaded} fichiers téléchargés, {total_errors} erreurs.")
