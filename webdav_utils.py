import os
import json
import hashlib
import shutil
from markdonw_transformer import convert_md_file_to_html


def download_active_files_for_ids(client, config, download_dir):
    """
    Télécharge les fichiers active / active_md / active_sm pour chaque dossier,
    les renomme avec un hash, les convertit si Markdown, et écrit le résultat dans un JSON.
    """
    print("\n🔍 Téléchargement des fichiers 'active' pour chaque dossier :")

    updated = []
    total_downloaded = 0
    total_errors = 0

    for item in config:
        folder_id = item["id"]
        folder_path = f"{folder_id.strip('/')}/"
        print(f"\n📂 Dossier : {folder_path}")

        new_item = item.copy()
        new_item["src"] = ""
        new_item["src_md"] = ""
        new_item["src_sm"] = ""
        new_item["load"] = False
        new_item["filetype"] = ""
        new_item["error"] = None

        try:
            files = client.list(folder_path)
            if not files:
                msg = "Dossier vide ou inaccessible."
                print(f"   ⚠️ {msg}")
                new_item["error"] = msg
                total_errors += 1
                updated.append(new_item)
                continue

            active_files = [
                f for f in files
                if not f.endswith("/") and f.lower().startswith("active")
            ]

            if not active_files:
                msg = "Aucun fichier 'active' trouvé."
                print(f"   ⚠️ {msg}")
                new_item["error"] = msg
                updated.append(new_item)
                continue

            for f in active_files:
                base_name = os.path.basename(f)
                ext = os.path.splitext(base_name)[1].lstrip(".").lower()
                remote_path = f"{folder_path}{f}".replace("//", "/")

                # 1. Téléchargement temporaire
                temp_path = os.path.join(download_dir, f"__temp.{ext}")
                print(f"   ⬇️ Téléchargement de {remote_path} → {temp_path}")
                client.download_sync(remote_path=remote_path, local_path=temp_path)

                # 2. Définir le suffixe et clé JSON
                if base_name.startswith("active_sm"):
                    suffix = "_sm"
                    key = "src_sm"
                elif base_name.startswith("active_md"):
                    suffix = "_md"
                    key = "src_md"
                else:
                    suffix = ""
                    key = "src"

                # 3. Si Markdown → conversion en HTML
                if ext == "md":
                    html_temp = os.path.join(download_dir, "__temp.html")
                    convert_md_file_to_html(temp_path, html_temp)
                    os.remove(temp_path)

                    ext = "html"
                    temp_path = html_temp  # on continue avec le HTML

                # 4. Calcul du hash
                hash_suffix = hash_file(temp_path)

                # 5. Nom final avec hash
                final_name = f"{folder_id}{suffix}.{hash_suffix}.{ext}"
                final_path = os.path.join(download_dir, final_name)

                # 6. Déplacement vers le nom définitif
                shutil.move(temp_path, final_path)

                # 7. Enregistrement dans le JSON
                new_item[key] = final_name
                new_item["filetype"] = ext
                new_item["load"] = True
                total_downloaded += 1

        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Erreur pour {folder_id} : {error_msg}")
            new_item["error"] = error_msg
            total_errors += 1

        updated.append(new_item)

    # 💾 Écriture finale
    output_json = os.path.join(download_dir, "data_updated.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Fichier JSON mis à jour : {output_json}")
    print(f"📦 {len(updated)} dossiers traités — {total_downloaded} fichiers téléchargés — {total_errors} erreurs.")


def hash_file(filepath):
    """
    Retourne les 6 premiers caractères d’un hash SHA1 du fichier.
    """
    h = hashlib.sha1()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:6]
