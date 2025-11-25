# processors/ods_processor.py
import os
import json
import re
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from .base import BaseProcessor


class OdsProcessor(BaseProcessor):
    """Lit un fichier ODS et convertit la première feuille en liste d’objets JSON typés."""

    def process(self, src_path, download_dir, folder_id, suffix, ext):
        """
        Analyse un fichier ODS, affiche un aperçu console,
        et exporte les données en JSON avec détection automatique des types.
        """
        try:
            print(f"   📊 Lecture du fichier ODS : {os.path.basename(src_path)}")

            # Charger le document ODS
            doc = load(src_path)
            sheet = doc.getElementsByType(Table)[0]  # une seule feuille
            sheet_name = sheet.getAttribute("name") or "Sheet1"

            # Extraction des lignes et cellules
            rows = []
            for row in sheet.getElementsByType(TableRow):
                cells = []
                for cell in row.getElementsByType(TableCell):
                    text_parts = []
                    for p in cell.childNodes:
                        if hasattr(p, "data"):
                            text_parts.append(p.data)
                        elif hasattr(p, "childNodes"):
                            for c in p.childNodes:
                                if hasattr(c, "data"):
                                    text_parts.append(c.data)
                    value = "".join(text_parts).strip()
                    cells.append(value)
                if any(cells):  # ignorer les lignes complètement vides
                    rows.append(cells)

            if len(rows) < 2:
                print("   ⚠️ Pas assez de lignes pour créer un tableau d’objets.")
                return src_path, ext

            # Première ligne = clés → suppression des colonnes vides
            headers = [h.strip().lower() for h in rows[0] if h.strip() != ""]
            data = []

            # Construction des objets
            for row in rows[1:]:
                obj = {}
                for i, key in enumerate(headers):
                    if i >= len(row):
                        continue
                    value = row[i].strip()
                    obj[key] = self._auto_cast(value)
                data.append(obj)

            # Aperçu console
            print(f"   🗂 Feuille : {sheet_name}")
            for line in data[:5]:
                print("   →", line)
            if len(data) > 5:
                print(f"   ... ({len(data)} lignes au total)")

            # Écriture JSON
            json_path = os.path.join(download_dir, "__temp.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"   ✅ Export JSON terminé : {os.path.basename(json_path)}\n")
            return json_path, "json"

        except Exception as e:
            print(f"   ⚠️ Erreur lors du traitement du fichier ODS : {e}")
            return src_path, ext

    # ============================================================
    # 🧩 Méthode interne : conversion automatique des types
    # ============================================================

    def _auto_cast(self, value: str):
        """Détecte automatiquement le type d’une valeur texte."""
        if value == "":
            return None

        lower = value.lower()

        # Booléens
        if lower in ["true", "vrai", "yes", "oui"]:
            return True
        if lower in ["false", "faux", "no", "non"]:
            return False

        # Entiers
        if re.fullmatch(r"[-+]?\d+", value):
            try:
                return int(value)
            except ValueError:
                pass

        # Flottants (point ou virgule)
        if re.fullmatch(r"[-+]?\d*[\.,]\d+", value):
            try:
                return float(value.replace(",", "."))
            except ValueError:
                pass

        # Par défaut : texte
        return value

    def parse_to_python(self, src_path):
        """
        Analyse un fichier ODS et retourne directement
        une liste d'objets Python (list[dict]).
        """
        try:
            print(f"   📊 Lecture du fichier ODS : {os.path.basename(src_path)}")

            doc = load(src_path)
            sheet = doc.getElementsByType(Table)[0]

            rows = []
            for row in sheet.getElementsByType(TableRow):
                cells = []
                for cell in row.getElementsByType(TableCell):
                    text_parts = []
                    for p in cell.childNodes:
                        if hasattr(p, "data"):
                            text_parts.append(p.data)
                        elif hasattr(p, "childNodes"):
                            for c in p.childNodes:
                                if hasattr(c, "data"):
                                    text_parts.append(c.data)
                    value = "".join(text_parts).strip()
                    cells.append(value)
                if any(cells):
                    rows.append(cells)

            if len(rows) < 2:
                print("   ⚠️ Pas assez de lignes pour créer un tableau d’objets.")
                return []

            headers = [h.strip().lower() for h in rows[0] if h.strip() != ""]
            data = []

            for row in rows[1:]:
                obj = {}
                header_index = 0
                for value in row:
                    if header_index >= len(headers):
                        break
                    key = headers[header_index]
                    obj[key] = self._auto_cast(value.strip())
                    header_index += 1
                data.append(obj)

            return data

        except Exception as e:
            print(f"   ⚠️ Erreur lors du parse ODS : {e}")
            return []
