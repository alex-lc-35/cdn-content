import os
import json

def download_active_files_for_ids(client, config, download_dir):
    """
    Lit la config JSON, télécharge les fichiers active / active_md / active_sm
    pour chaque dossier correspondant, met à jour les champs et écrit dans un
    nouveau fichier JSON dans le même dossier que les images.
    """
    print("\n🔍 Téléchargement des fichiers 'active' pour chaque dossier :")

    updated = []
    total_downloaded = 0

    for item in config:
        folder_id = item["id"]
        folder_path = f"{folder_id.strip('/')}/"
        print(f"\n📂 Dossier : {folder_path}")

        # Copie de l'objet pour le JSON final
        new_item = item.copy()
        new_item["src"] = ""
        new_item["src_md"] = ""
        new_item["src_sm"] = ""
        new_item["load"] = False

        try:
            files = client.list(folder_path)
            if not files:
                print("   ⚠️ Dossier vide ou inaccessible.")
                updated.append(new_item)
                continue

            active_files = [
                f for f in files
                if not f.endswith("/") and f.lower().startswith("active")
            ]

            if not active_files:
                print("   ⚠️ Aucun fichier 'active' trouvé.")
                updated.append(new_item)
                continue

            for f in active_files:
                base_name = os.path.basename(f)
                ext = os.path.splitext(base_name)[1].lstrip(".").lower()

                # Nouveau nom local selon le type
                if base_name.startswith("active_sm"):
                    new_name = f"{folder_id}_sm.{ext}"
                    key = "src_sm"
                elif base_name.startswith("active_md"):
                    new_name = f"{folder_id}_md.{ext}"
                    key = "src_md"
                else:
                    new_name = f"{folder_id}.{ext}"
                    key = "src"

                local_path = os.path.join(download_dir, new_name)
                remote_path = f"{folder_path}{f}".replace("//", "/")

                print(f"   ⬇️ Téléchargement de {remote_path} → {local_path}")
                client.download_sync(remote_path=remote_path, local_path=local_path)

                new_item[key] = ext
                new_item["load"] = True
                total_downloaded += 1

        except Exception as e:
            print(f"   ❌ Erreur pour {folder_id} : {e}")

        # Ajouter la version mise à jour à la liste finale
        updated.append(new_item)

    # 💾 Écriture finale dans le dossier de téléchargement
    output_json = os.path.join(download_dir, "data_updated.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Fichier JSON mis à jour : {output_json}")
    print(f"📦 {len(updated)} dossiers traités — {total_downloaded} fichiers téléchargés.")
