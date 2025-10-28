""" webdav/repo.py """

def list_folder(client, folder_path):
    try:
        files = client.list(folder_path)
        active = [f for f in files if not f.endswith("/") and f.lower().startswith("active")]
        return active, None
    except Exception as e:
        return [], str(e)

def get_info(client, remote_path):
    try:
        info = client.info(remote_path)
        return {
            "etag": (info.get("etag") or "").replace('"', ""),
            "lastmod": (info.get("modified") or "").replace("+0000", "GMT").strip(),
        }
    except Exception as e:
        return {"error": str(e)}

def download_file(client, remote_path, local_path):
    client.download_sync(remote_path=remote_path, local_path=local_path)
