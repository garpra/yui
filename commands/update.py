from helpers.downloader import download
from helpers.appimage import (
    extract_data_appimage,
    make_executable,
    remove_appimage,
    remove_desktop_entry,
)
from helpers.github import fetch_latest_release
from helpers.repository import (
    update_repository,
    get_list_app,
    read_repository,
)
import helpers.models as types


def update_app(args):
    """
    Perbarui semua aplikasi AppImage yang terinstal ke versi terbaru.

    Memeriksa versi terbaru aplikasi dari GitHub,
    dan mengunduh pembaruan jika tersedia. Untuk setiap aplikasi yang diperbarui,
    AppImage dan desktop entry lama dihapus, dan versi baru akan diunduh,
    dijadikan executable, dan didaftarkan ke repositori.

    Aplikasi yang gagal diunduh akan dilewati dengan pesan error.
    Aplikasi yang sudah versi terbaru akan dilewati.
    """
    # Ambil list data dari repo
    list_app = get_list_app()
    # Cek jika list data kosong
    if not list_app:
        print("\nNo application is installed")
        return

    # Ambil semua data dari repo
    data_repo = read_repository()

    for app_url in list_app["github_app"]:
        # Ambil versi app dari repo
        repo_version = data_repo[app_url]["version"]

        # Ambil metadata app terbaru
        new_data = fetch_latest_release(app_url)

        # Cek jika data new kosong/error
        if not new_data["success"]:
            print(f"Failed to get data for {app_url}, skipping...")
            continue

        url_type = data_repo[app_url]["url_type"]
        new_version = new_data["version"]
        new_download_url = new_data["download_url"]
        new_app_path = new_data["app_path"]

        # Cek jika versi app sudah terbaru
        if repo_version == new_version:
            print(f"{app_url} is latest version")
        else:
            # Update app ke versi terbaru
            print(f"Updating {app_url} {new_version}:")
            try:
                download(new_download_url, new_app_path)
            # Kalau gagal skip app tersebut
            except RuntimeError as err:
                print(f"\nDownload failed for {app_url}: {err}, skipping...")
                continue

            # Hapus appimage lama
            remove_appimage(data_repo[app_url]["app_path"])

            # Hapus desktop entry lama
            remove_desktop_entry(data_repo[app_url]["desktop_path"])

            # Atur agar appimage menjadi executable
            make_executable(new_app_path)

            # Ambil data desktop dan icon dari appimage
            app_data_path = extract_data_appimage(new_app_path)
            desktop_path = app_data_path["desktop_path"]
            icon_path = app_data_path["icon_path"]

            record = types.AppRecord(
                url_type=url_type,
                app_path=new_app_path,
                version=new_version,
                download_url=new_download_url,
                desktop_path=desktop_path,
                icon_path=icon_path,
            )
            # Update repository data
            update_repository(app_url, record)

    print("\nUpdate all application finished")
