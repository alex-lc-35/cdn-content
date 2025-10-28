# processors/default_processor.py
from .base import BaseProcessor


class DefaultProcessor(BaseProcessor):
    """Traitement neutre : aucun changement sur le fichier."""

    def process(self, src_path, download_dir, folder_id, suffix, ext):
        """
        Ne fait rien de particulier, retourne simplement le même chemin et extension.
        """
        return src_path, ext
