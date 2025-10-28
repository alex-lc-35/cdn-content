""" core/naming.py """

def normalize_id(folder_id: str) -> str:
    return folder_id.strip("/")

def detect_key(base_name: str):
    base = base_name.lower()
    if base.startswith("active_sm"):
        return "_sm", "src_sm"
    elif base.startswith("active_md"):
        return "_md", "src_md"
    else:
        return "", "src"

def final_name(folder_id, suffix, etag, lastmod, ext):
    etag_clean = (etag or "").replace('"', '').replace(":", "").replace("/", "")
    if not etag_clean and lastmod:
        etag_clean = lastmod.replace(",", "").replace(" ", "_").replace(":", "-")
    if not etag_clean:
        etag_clean = "noetag"
    return f"{folder_id}{suffix}.{etag_clean}.{ext}"
