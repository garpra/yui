import os

from helpers.downloader import download
from helpers.appimage import extract_data_appimage, make_executable
from helpers.github import fetch_latest_release
from helpers.repository import update_repository
import helpers.models as types


def install_app(args):
    """
    Instal aplikasi AppImage dari repositori GitHub.

    Mengambil versi terbaru dari repositori GitHub yang ditentukan, mengunduh
    asset AppImage, menjadikan appimage executable, mengekstrak data desktop dan ikon,
    serta mendaftarkan aplikasi di repositori lokal. Jika AppImage sudah di download
    dan versi terbaru, operasi akan dilewati.
    """
    app_url = args.app_url

    print(f"Search info AppImage for: {app_url}\n")

    # Ambil data versi terbaru dari repo
    results = fetch_latest_release(app_url)

    # Cek jika ambil data success
    if not results["success"]:
        print(f"Failed to get data: {results['status']}\n")
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
    desktop_path = app_data_path["desktop_path"]
    icon_path = app_data_path["icon_path"]

    record = types.AppRecord(
        app_name=app_name,
        app_path=app_path,
        version=version,
        download_url=download_url,
        desktop_path=desktop_path,
        icon_path=icon_path,
    )

    # Update repository data
    update_repository(app_url, record)

    print(f"\nDownload {app_name} successfully")
