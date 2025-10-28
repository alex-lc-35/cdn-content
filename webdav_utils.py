""" webdav_utils.py """
import os
import json
import shutil
from markdonw_transformer import convert_md_file_to_html


# ============================================================
# 🔹 Utilitaires de base
# ============================================================

def load_previous_data(download_dir):
    """Charge le JSON précédent s'il existe."""
    path = os.path.join(download_dir, "data_updated.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_previous_item(folder_id, previous_data):
    """Récupère l'ancien item correspondant à un dossier donné."""
    return next((i for i in previous_data if i["id"].strip("/") == folder_id), None)


def get_active_files(client, folder_path):
    """Retourne la liste des fichiers 'active' dans un dossier WebDAV."""
    files = client.list(folder_path)
    if not files:
        return [], "Dossier vide ou inaccessible."
    active = [f for f in files if not f.endswith("/") and f.lower().startswith("active")]
    if not active:
        return [], "Aucun fichier 'active' trouvé."
    return active, None


def download_and_process_file(client, remote_path, download_dir, ext):
    """Télécharge un fichier, convertit s'il est Markdown, et retourne son chemin final."""
    temp_path = os.path.join(download_dir, f"__temp.{ext}")
    client.download_sync(remote_path=remote_path, local_path=temp_path)

    if ext == "md":
        html_temp = os.path.join(download_dir, "__temp.html")
        convert_md_file_to_html(temp_path, html_temp)
        os.remove(temp_path)
        ext = "html"
        temp_path = html_temp

    return temp_path, ext


def build_final_name(folder_id, suffix, etag, lastmod, ext):
    """Construit un nom de fichier final basé sur etag ou lastmod."""
    etag_clean = (etag or "").replace('"', '').replace(":", "").replace("/", "")
    if not etag_clean and lastmod:
        etag_clean = lastmod.replace(",", "").replace(" ", "_").replace(":", "-")
    if not etag_clean:
        etag_clean = "noetag"
    return f"{folder_id}{suffix}.{etag_clean}.{ext}"


def update_item_with_file(new_item, key, final_name, etag, lastmod, ext):
    """Met à jour les métadonnées d'un item avec un fichier téléchargé."""
    new_item[key] = final_name
    new_item["filetype"] = ext
    new_item["load"] = True
    new_item.setdefault("meta", {})[key] = {"etag": etag, "lastmod": lastmod}


# ============================================================
# 🔸 Fonction principale
# ============================================================

def download_active_files_for_ids(client, config, download_dir):
    print("\n🔍 Téléchargement des fichiers 'active' pour chaque dossier :")

    updated = []
    total_downloaded = 0
    total_errors = 0
    previous_data = load_previous_data(download_dir)

    for item in config:
        folder_id = item["id"].strip("/")
        folder_path = f"{folder_id}/"
        print(f"\n📂 Dossier : {folder_path}")

        previous_item = get_previous_item(folder_id, previous_data)
        previous_meta = (previous_item.get("meta") or {}) if previous_item else {}

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
            active_files, error = get_active_files(client, folder_path)
            if error:
                print(f"   ⚠️ {error}")
                new_item["error"] = error
                total_errors += 1
                updated.append(new_item)
                continue

            for f in active_files:
                base_name = os.path.basename(f)
                ext = os.path.splitext(base_name)[1].lstrip(".").lower()
                remote_path = f"{folder_path}{f}".replace("//", "/")

                # 🔹 Déterminer le suffixe
                if base_name.startswith("active_sm"):
                    suffix, key = "_sm", "src_sm"
                elif base_name.startswith("active_md"):
                    suffix, key = "_md", "src_md"
                else:
                    suffix, key = "", "src"

                # 🔹 Métadonnées distantes
                info = client.info(remote_path)
                etag = (info.get("etag") or "").replace('"', "")
                lastmod = (info.get("modified") or "").replace("+0000", "GMT").strip()

                prev_info = previous_meta.get(key, {})
                prev_etag = prev_info.get("etag")
                prev_lastmod = prev_info.get("lastmod")

                print(f"DEBUG {base_name}: prev={prev_etag!r}, new={etag!r}")

                # 🔸 Vérification inchangé
                if prev_etag and prev_etag == etag:
                    print(f"   ⏩ {base_name} inchangé (etag identique)")
                    continue
                if not etag and prev_lastmod and prev_lastmod == lastmod:
                    print(f"   ⏩ {base_name} inchangé (lastmod identique)")
                    continue

                # 🔹 Téléchargement nécessaire
                print(f"   ⬇️ Téléchargement de {base_name}")
                temp_path, ext = download_and_process_file(client, remote_path, download_dir, ext)

                # 🔹 Nom final
                final_name = build_final_name(folder_id, suffix, etag, lastmod, ext)
                final_path = os.path.join(download_dir, final_name)
                shutil.move(temp_path, final_path)

                # 🔹 Mise à jour de l'item
                update_item_with_file(new_item, key, final_name, etag, lastmod, ext)
                total_downloaded += 1

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Erreur pour {folder_id} : {error_msg}")
            new_item["error"] = error_msg
            total_errors += 1

        updated.append(new_item)

    # 💾 Sauvegarde finale
    output_json = os.path.join(download_dir, "data_updated.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Fichier JSON mis à jour : {output_json}")
    print(f"📦 {len(updated)} dossiers traités — {total_downloaded} fichiers téléchargés — {total_errors} erreurs.")
