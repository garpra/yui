import os

from helpers.downloader import download
from helpers.appimage import extract_data_appimage, make_executable
from helpers.github import fetch_latest_release
from helpers.repository import update_repository


def install_app(args):
    app_url = args.app_url

    print(f"Search info AppImage for: {app_url}\n")

    # Ambil data versi terbaru dari repo
    results = fetch_latest_release(app_url)

    # Cek jika ambil data success
    if not results or not results["success"]:
        print(
            f"Failed to get data: {results['status'] if results else 'unknown error'}\n"
        )
        return

    app_name = results["app_name"]
    app_path = results["app_path"]
    version = results["version"]
    download_url = results["download_url"]

    print(f"Found: {app_name} {version}\n")

    # Cek jika appimage sudah ada dan versi terbaru
    if os.path.exists(app_path):
        print(f"{app_url} has been downloaded and is the latest version")
        return

    # Download AppImage sesuai dengan url dan path
    download(download_url, app_path)

    # Atur agar appimage menjadi executable
    make_executable(app_path)

    # Ambil data desktop dan icon dari appimage
    app_data_path = extract_data_appimage(app_path)
    desktop_path = app_data_path.get("desktop_path", "")
    icon_path = app_data_path.get("icon_path", "")

    # Update repository data
    update_repository(
        app_url, app_name, app_path, version, download_url, desktop_path, icon_path
    )

    print(f"\nDownload {app_name} successfully")
