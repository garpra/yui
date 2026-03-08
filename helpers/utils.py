# Repo cek format repo app
from helpers.models import ReleaseData


def error_fetch_app(msg: str) -> ReleaseData:
    return {
        "success": False,
        "url_type": "",
        "app_name": "",
        "app_path": "",
        "version": "",
        "download_url": "",
        "status": msg,
    }
