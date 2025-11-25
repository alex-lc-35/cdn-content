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

        # ------------------------------------------------------
        # 🛑 1) IGNORER LES ENTRÉES INACTIVES (active != 1)
        # ------------------------------------------------------
        if str(item.get("active", 1)) != "1":
            print("   ⏭️ Dossier inactif, ignoré.")
            inactive_item = item.copy()
            inactive_item.update({
                "load": False,
                "error": None,
                "meta": item.get("meta", {}),
            })
            updated.append(inactive_item)
            continue

        # Récupération des anciennes métadonnées
        prev_item = next((i for i in previous_data if i["id"].strip("/") == folder_id), None)
        prev_meta = (prev_item.get("meta") or {}) if prev_item else {}
        new_item = (prev_item.copy() if prev_item else item.copy())
        new_item.update({"error": None, "meta": prev_meta.copy(), "load": False})

        # ------------------------------------------------------
        # Listing WebDAV du dossier
        # ------------------------------------------------------
        active_files, error = list_folder(client, folder_path)
        if error:
            print(f"   ⚠️ {error}")
            new_item["error"] = error
            total_errors += 1
            updated.append(new_item)
            continue

        # ------------------------------------------------------
        # Traitement fichier par fichier
        # ------------------------------------------------------
        for f in active_files:
            base_name = os.path.basename(f)
            ext = os.path.splitext(base_name)[1].lstrip(".").lower()
            suffix, key = detect_key(base_name)
            remote_path = f"{folder_path}{f}".replace("//", "/")

            info = get_info(client, remote_path)
            etag, lastmod = info.get("etag"), info.get("lastmod")
            prev_info = prev_meta.get(key, {})

            # ------------------------------------------------------
            # Comparaison pour éviter les téléchargements inutiles
            # ------------------------------------------------------
            if prev_info.get("etag") == etag or (not etag and prev_info.get("lastmod") == lastmod):
                print(f"   ⏩ {base_name} inchangé")
                continue

            # ------------------------------------------------------
            # ⚠️ PURGE INTELLIGENTE AVANT TÉLÉCHARGEMENT
            # ------------------------------------------------------

            # Si suffix existe → purge par folder_id_suffix_
            # Exemple : header_sm.png → purge header_sm_*
            if suffix:
                root = f"{folder_id}{suffix}."

            # Si suffix n'existe pas → purge par folder_id_
            # Exemple : header.png → purge header_*
            else:
                root = f"{folder_id}."

            print(f"   ⬇️ sufix {root}")

            for file in os.listdir(download_dir):
                if file.startswith(root):
                    try:
                        os.remove(os.path.join(download_dir, file))
                        print(f"   🗑️ Ancien fichier supprimé : {file}")
                    except Exception as e:
                        print(f"   ⚠️ Erreur suppression {file} : {e}")


            # ------------------------------------------------------
            # Téléchargement du fichier WebDAV
            # ------------------------------------------------------
            print(f"   ⬇️ Téléchargement de {base_name}")
            temp_path = os.path.join(download_dir, f"__temp.{ext}")
            download_file(client, remote_path, temp_path)

            # ------------------------------------------------------
            # Traitement via le bon processor
            # ------------------------------------------------------
            processor = get_processor_for(ext)
            if not processor:
                msg = f"Extension '{ext}' non gérée."
                print(f"   ⚠️ {msg}")
                new_item["error"] = msg
                total_errors += 1
                continue

            temp_path, ext = processor.process(temp_path, download_dir, folder_id, suffix, ext)

            # ------------------------------------------------------
            # Déplacement dans un nom final propre
            # ------------------------------------------------------
            final = final_name(folder_id, suffix, etag, lastmod, ext)
            shutil.move(temp_path, os.path.join(download_dir, final))

            # ------------------------------------------------------
            # Mise à jour de l'état interne
            # ------------------------------------------------------
            new_item[key] = final
            new_item["filetype"] = ext
            new_item["meta"][key] = {"etag": etag, "lastmod": lastmod}
            new_item["load"] = True
            total_downloaded += 1

        updated.append(new_item)

    # ------------------------------------------------------
    # Sauvegarde de l'état global
    # ------------------------------------------------------
    save_current(download_dir, updated)

    print(f"\n✅ Synchronisation terminée : {total_downloaded} fichiers téléchargés, {total_errors} erreurs.")
