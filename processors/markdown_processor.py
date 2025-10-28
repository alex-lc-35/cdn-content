# processors/markdown_processor.py
import os
from transformers.markdown_transformer import convert_md_file_to_html
from .base import BaseProcessor


class MarkdownProcessor(BaseProcessor):
    """Convertit les fichiers Markdown en HTML."""

    def process(self, src_path, download_dir, folder_id, suffix, ext):
        """
        Convertit le fichier Markdown en HTML et retourne le chemin final + nouvelle extension.
        """
        html_temp = os.path.join(download_dir, "__temp.html")
        convert_md_file_to_html(src_path, html_temp)
        os.remove(src_path)
        return html_temp, "html"
