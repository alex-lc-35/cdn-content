# processors/markdown_processor.py
import os
import markdown
from .base import BaseProcessor


class MarkdownProcessor(BaseProcessor):
    """Convertit les fichiers Markdown en HTML."""

    def process(self, src_path, download_dir, folder_id, suffix, ext):
        """
        Convertit le fichier Markdown en HTML et retourne le chemin final + nouvelle extension.
        """
        try:
            # Lire le fichier Markdown
            with open(src_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Conversion → HTML
            html_content = markdown.markdown(md_content)

            # Écriture du résultat dans un fichier temporaire
            html_temp = os.path.join(download_dir, "__temp.html")
            with open(html_temp, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Nettoyage du fichier source temporaire
            os.remove(src_path)
            

            return html_temp, "html"

        except Exception as e:
            print(f"   ❌ Erreur lors de la conversion Markdown : {e}")
            return src_path, ext  # fallback : on retourne le fichier brut
