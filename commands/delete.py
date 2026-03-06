from helpers.repository import read_repository, remove_repository
from helpers.appimage import remove_appimage, remove_desktop_entry


def delete_app(args):
    # Ambil data input
    app_url = args.app_url
    # Ambil data repo
    data = read_repository()

    # Cek jika app tidak ada
    if app_url not in data:
        print("Application is not installed and cannot be removed")
        return

    app_path = data[app_url]["app_path"]
    desktop_path = data[app_url]["desktop_path"]

    print(f"Found {app_url}\n\nDeleting app...")

    # Hapus data app dari repo
    remove_repository(app_url)
    # Hapus appimage dari app
    remove_appimage(app_path)
    # Hapus desktop entry
    remove_desktop_entry(desktop_path)
