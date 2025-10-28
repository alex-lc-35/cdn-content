""" run.py """

from core.init_loader import load_initial_json
from webdav.client import get_client
from core.sync_pipeline import sync_active_files
from core.state_store import ensure_dir
import os

def main():
    config = load_initial_json("data.json")
    client = get_client()
    download_dir = os.getenv("DOWNLOAD_DIR", "cdn")
    ensure_dir(download_dir)
    sync_active_files(client, config, download_dir)

if __name__ == "__main__":
    main()

