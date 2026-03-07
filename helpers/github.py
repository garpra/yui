import requests
import os
from urllib.parse import urlparse
import helpers.constant as con
import helpers.models as types


def is_safe_url(url: str) -> bool:
    """
    Periksa apakah URL adalah URL unduhan GitHub yang valid.

    Memvalidasi bahwa URL menggunakan HTTPS dan mengarah ke domain github.com
    atau subdomain dari github.com.
    """
    parsed = urlparse(url)
    # Cek jika url benar-benar dari github
    return parsed.scheme == "https" and (
        parsed.netloc == "github.com" or parsed.netloc.endswith(".github.com")
    )


def find_appimage_asset(assets: list) -> dict | None:
    """
    Temukan asset AppImage dari daftar asset dari API GitHub.

    Mencari melalui daftar asset yang diberikan dan mengembalikan asset pertama
    yang memiliki nama file dengan akhiran '.AppImage'.
    """
    for asset in assets:
        # Cek jika name dari app berekstensi .appimage
        if asset.get("name", "").endswith(".AppImage"):
            return asset
    return None


def fetch_latest_release(app_url: str) -> types.ReleaseData:
    """
    Ambil informasi versi terbaru dari repositori GitHub.

    Mengquery API GitHub pada versi terbaru dari aplikasi yang ditentukan,
    menemukan asset dari AppImage, dan mengembalikan informasi
    tag versi, URL download, dan path file lokal.
    """

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

    # Ambil data asset appimage
    assets_app = find_appimage_asset(data.get("assets", []))
    # Cek jika appimage ada
    if assets_app:
        # Cek jika key browser_download_url aman
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
