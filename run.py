""" run.py """

from webdav.client import get_client
from core.sync_pipeline import sync_active_files
from core.state_store import ensure_dir
from core.load_config import sync_active_params_data
import os

def main():
    client = get_client()
    download_dir = os.getenv("DOWNLOAD_DIR", "cdn")
    config = sync_active_params_data(client, download_dir)
    ensure_dir(download_dir)
    sync_active_files(client, config, download_dir)

if __name__ == "__main__":
    main()

