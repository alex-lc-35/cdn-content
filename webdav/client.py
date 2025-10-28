""" webdav/client.py """

import os
from dotenv import load_dotenv
from webdav3.client import Client

def get_client():
    load_dotenv()
    options = {
        "webdav_hostname": os.getenv("WEBDAV_HOSTNAME"),
        "webdav_login": os.getenv("WEBDAV_LOGIN"),
        "webdav_password": os.getenv("WEBDAV_PASSWORD"),
    }
    return Client(options)
