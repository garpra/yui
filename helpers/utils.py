import requests


def get_latest_appimage_data(app_url: str):

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
            "version": None,
            "download_url": None,
            "status": str(err),
        }

    data = response.json()
    # Ambil versi app terbaru
    version = data.get("tag_name", "")

    # Cari file yang berekstensi .AppImage di daftar asset
    for asset in data.get("assets", ""):
        name = asset.get("name", "")
        if name.endswith(".AppImage"):
            download_url = asset.get("browser_download_url", "")
            return {
                "success": True,
                "app_name": name,
                "version": version,
                "download_url": download_url,
                "status": "Get data success",
            }

    return {
        "success": False,
        "app_name": None,
        "version": None,
        "download_url": None,
        "status": "AppImage not found",
    }
