import os
from webdav3.client import Client
from dotenv import load_dotenv

def get_client():
    """Initialise et retourne un client WebDAV configuré à partir du .env"""
    load_dotenv()

    options = {
        "webdav_hostname": os.getenv("WEBDAV_HOSTNAME"),
        "webdav_login": os.getenv("WEBDAV_LOGIN"),
        "webdav_password": os.getenv("WEBDAV_PASSWORD"),
    }

    client = Client(options)
    return client
