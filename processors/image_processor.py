# processors/image_processor.py
import os
from .base import BaseProcessor


class ImageProcessor(BaseProcessor):
    """Vérifie les images (taille, poids, etc.)."""

    def process(self, src_path, download_dir, folder_id, suffix, ext):
        """
        Vérifie la taille du fichier image.
        Retourne le chemin du fichier et l’extension (inchangée).
        """
        try:
            size = os.path.getsize(src_path)
            max_size = 5 * 1024 * 1024  # 5 Mo
            if size > max_size:
                print(f"   ⚠️ Image trop lourde : {size/1024/1024:.2f} Mo (max {max_size/1024/1024:.1f} Mo)")
        except Exception as e:
            print(f"   ⚠️ Erreur lors de la vérification de l'image : {e}")

        return src_path, ext
