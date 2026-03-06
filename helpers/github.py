import requests
import os
from urllib.parse import urlparse
import helpers.constant as con


def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.netloc.endswith("github.com")


def find_appimage_assets(assets: list) -> dict | None:
    for asset in assets:
        if asset.get("name", "").endswith(".AppImage"):
            return asset
    return None


def fetch_latest_release(app_url: str):

    url = f"https://api.github.com/repos/{app_url}/releases/latest"

    try:
        # Get data api dari url
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        # Jika gagal mendapatkan data dari GET
        return {
            "success": False,
            "app_name": None,
            "app_path": None,
            "version": None,
            "download_url": None,
            "status": str(err),
        }

    data = response.json()
    # Ambil versi app terbaru
    version = data.get("tag_name", "")

    assets_app = find_appimage_assets(data)
    if assets_app:
        if not is_safe_url(assets_app.get("browser_download_url", "")):
            return {
                "success": False,
                "app_name": None,
                "app_path": None,
                "version": None,
                "download_url": None,
                "status": "Unsafe download URL",
            }

        download_path = os.path.join(con.APPIMAGE_PATH, assets_app.get("name", ""))
        return {
            "success": True,
            "app_name": assets_app.get("name", ""),
            "app_path": download_path,
            "version": version,
            "download_url": assets_app.get("browser_download_url", ""),
            "status": "Get data success",
        }

    return {
        "success": False,
        "app_name": None,
        "app_path": None,
        "version": None,
        "download_url": None,
        "status": "AppImage not found",
    }
