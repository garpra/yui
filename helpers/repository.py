import os
import json
from filelock import FileLock, Timeout
import helpers.constant as con
import helpers.models as types


def read_repository() -> dict:
    """
    Ambil dan kembalikan isi dari repositori aplikasi lokal.

    Membaca file JSON repositori dari aplikasi AppImage yang terinstal.
    Jika file repositori tidak ada, dictionary kosong akan dikembalikan.
    """
    # Cek apakah file ada sebelum membuka file
    if not os.path.exists(con.REPO_PATH):
        return {}

    # Baca file
    with open(con.REPO_PATH, "r") as file:
        return json.load(file)


def update_repository(repo: str, record: types.AppRecord) -> None:
    """
    Tambahkan atau perbarui data aplikasi pada repositori lokal.

    Menggunakan file locking untuk memastikan akses bersamaan yang aman. Membaca
    data repositori yang ada, memperbarui atau menambahkan data aplikasi,
    dan menulis data baru ke file repositori.
    """
    # Buat file lock
    try:
        with FileLock(con.REPO_PATH + ".lock", timeout=5):
            # Baca data repo
            data = read_repository()

            # Buat dict untuk data repo
            data[repo] = {
                "app_name": record.app_name,
                "app_path": record.app_path,
                "version": record.version,
                "download_url": record.download_url,
                "desktop_path": record.desktop_path,
                "icon_path": record.icon_path,
            }

            # Simpan data ke repo
            with open(con.REPO_PATH, "w") as file:
                json.dump(data, file, indent=2)
    except Timeout:
        print("Unable to access repos.json. Please try again later")


def remove_repository(app_url: str) -> None:
    """
    Hapus data aplikasi dari repositori lokal.

    Menggunakan file locking untuk memastikan akses bersamaan yang aman. Membaca
    data repositori yang ada, menghapus entri untuk aplikasi yang ditentukan, dan
    menulis data yang telah diperbarui ke repositori lokal.
    """
    try:
        with FileLock(con.REPO_PATH + ".lock", timeout=5):
            # Ambil data repo
            data = read_repository()

            # Hapus data repo sesuai dengan 'app_url'
            data.pop(app_url, None)

            # Update data repo
            with open(con.REPO_PATH, "w") as file:
                json.dump(data, file, indent=2)
    except Timeout:
        print("Unable to access repos.json. Please try again later")


def get_list_app() -> list[str]:
    """
    Ambil daftar semua aplikasi yang terinstal di repositori lokal.
    """
    return list(read_repository().keys())
