from helpers.repository import get_list_app
from pathlib import Path


def list_app(args):
    """
    Tampilkan semua aplikasi AppImage yang terinstal.

    Mengambil dan menampilkan semua aplikasi yang telah diinstal melalui Yui
    dari repositori lokal. Setiap entri ditampilkan dalam format 'owner/repo'.
    """
    # Ambil data list app
    app_list = get_list_app()

    # Cek jika app kosong
    if not app_list:
        print("No applications found")
        return

    print("Installed app:")
    # Print seluruh app
    for app_url in app_list:
        print(app_url)
