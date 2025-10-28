import os
import json
import shutil
from markdonw_transformer import convert_md_file_to_html


def download_active_files_for_ids(client, config, download_dir):
    """
    Télécharge les fichiers active / active_md / active_sm pour chaque dossier.
    Évite les téléchargements inutiles grâce à la comparaison etag / lastmod.
    Renomme les fichiers selon leur etag (ou date de modification si manquant).
    """
    print("\n🔍 Téléchargement des fichiers 'active' pour chaque dossier :")

    updated = []
    total_downloaded = 0
    total_errors = 0

    # 🔹 Charger le JSON précédent s'il existe
    output_json = os.path.join(download_dir, "data_updated.json")
    if os.path.exists(output_json):
        with open(output_json, "r", encoding="utf-8") as f:
            previous_data = json.load(f)
    else:
        previous_data = []

    # 🔸 Boucle principale
    for item in config:
        folder_id = item["id"].strip("/")
        folder_path = f"{folder_id}/"
        print(f"\n📂 Dossier : {folder_path}")

        # 🔍 Récupérer la version précédente du même dossier (si elle existe)
        previous_item = next((i for i in previous_data if i["id"].strip("/") == folder_id), None)
        previous_meta = (previous_item.get("meta") or {}) if previous_item else {}

        # 🆕 Créer le nouvel item (en gardant les anciens meta s’il y en a)
        new_item = (previous_item.copy() if previous_item else item.copy())
        new_item.update({
            "src": "",
            "src_md": "",
            "src_sm": "",
            "load": False,
            "filetype": "",
            "error": None,
            "meta": previous_meta.copy(),
        })

        try:
            files = client.list(folder_path)
            if not files:
                msg = "Dossier vide ou inaccessible."
                print(f"   ⚠️ {msg}")
                new_item["error"] = msg
                total_errors += 1
                updated.append(new_item)
                continue

            active_files = [f for f in files if not f.endswith("/") and f.lower().startswith("active")]
            if not active_files:
                msg = "Aucun fichier 'active' trouvé."
                print(f"   ⚠️ {msg}")
                new_item["error"] = msg
                updated.append(new_item)
                continue

            # 🔁 Boucle sur chaque fichier "active"
            for f in active_files:
                base_name = os.path.basename(f)
                ext = os.path.splitext(base_name)[1].lstrip(".").lower()
                remote_path = f"{folder_path}{f}".replace("//", "/")

                # 🧠 Déterminer le suffixe et la clé JSON
                if base_name.startswith("active_sm"):
                    suffix = "_sm"
                    key = "src_sm"
                elif base_name.startswith("active_md"):
                    suffix = "_md"
                    key = "src_md"
                else:
                    suffix = ""
                    key = "src"

                # 🔎 Métadonnées distantes
                info = client.info(remote_path)
                etag = (info.get("etag") or "").replace('"', "")
                lastmod = (info.get("modified") or "").replace("+0000", "GMT").strip()

                prev_info = previous_meta.get(key, {})
                prev_etag = prev_info.get("etag")
                prev_lastmod = prev_info.get("lastmod")

                print(f"DEBUG {base_name}: prev={prev_etag!r}, new={etag!r}")

                # 🔍 Vérification inchangé
                if prev_etag and prev_etag == etag:
                    print(f"   ⏩ {base_name} inchangé (etag identique)")
                    continue
                if not etag and prev_lastmod and prev_lastmod == lastmod:
                    print(f"   ⏩ {base_name} inchangé (lastmod identique)")
                    continue

                # 🆕 Téléchargement nécessaire
                print(f"   ⬇️ Téléchargement de {base_name}")
                temp_path = os.path.join(download_dir, f"__temp.{ext}")
                client.download_sync(remote_path=remote_path, local_path=temp_path)

                # 🪄 Conversion Markdown → HTML
                if ext == "md":
                    html_temp = os.path.join(download_dir, "__temp.html")
                    convert_md_file_to_html(temp_path, html_temp)
                    os.remove(temp_path)
                    ext = "html"
                    temp_path = html_temp

                # 🏁 Nom final basé sur l’etag ou la date
                etag_clean = etag.replace(":", "").replace("/", "")
                if not etag_clean and lastmod:
                    etag_clean = lastmod.replace(",", "").replace(" ", "_").replace(":", "-")
                if not etag_clean:
                    etag_clean = "noetag"

                final_name = f"{folder_id}{suffix}.{etag_clean}.{ext}"
                final_path = os.path.join(download_dir, final_name)
                shutil.move(temp_path, final_path)

                # 📦 Mise à jour de l’item
                new_item[key] = final_name
                new_item["filetype"] = ext
                new_item["load"] = True
                new_item["meta"][key] = {"etag": etag, "lastmod": lastmod}
                total_downloaded += 1

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Erreur pour {folder_id} : {error_msg}")
            new_item["error"] = error_msg
            total_errors += 1

        updated.append(new_item)

    # 💾 Écriture du JSON final
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Fichier JSON mis à jour : {output_json}")
    print(f"📦 {len(updated)} dossiers traités — {total_downloaded} fichiers téléchargés — {total_errors} erreurs.")
