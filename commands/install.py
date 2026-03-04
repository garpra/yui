import os
from helpers.utils import download, get_latest_appimage_data, update_repository

# Temporary AppImage folder
APPIMAGE_PATH = os.path.join(".local", "share", "yui", "appimage")


def install_app(args):
    app_url = args.app_url

    print(f"\nSearch info AppImage for: {app_url}\n")

    # Ambil data versi terbaru dari repo
    results = get_latest_appimage_data(app_url)

    # Cek jika ambil data success
    if not results["success"]:
        print(f"Failed to get data: {results["status"]}")
        return

    app_name = results["app_name"]
    version = results["version"]
    download_url = results["download_url"]

    print(f"Found: {app_name} {version}")
    print("Downloading...")

    # Buat folder jika belum ada
    os.makedirs(APPIMAGE_PATH, exist_ok=True)

    # Buat path untuk appimage yang di download
    save_path = os.path.join(APPIMAGE_PATH, app_name)

    # Cek jika AppImage yang sesuai dengan url dan versi terbaru
    if os.path.isfile(save_path):
        print(f"\n{app_url} has been downloaded and is the latest version")
        return

    # Download AppImage sesuai dengan url dan path
    download(download_url, save_path)

    # Update repository data
    update_repository(app_url, app_name, version, download_url)

    print(f"Download {app_name} successfully")
