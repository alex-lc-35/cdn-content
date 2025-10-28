# processors/base.py

class BaseProcessor:
    """Classe de base pour tous les processeurs."""

    def process(self, src_path, download_dir, folder_id, suffix, ext):
        raise NotImplementedError("Chaque processeur doit implémenter 'process'.")
