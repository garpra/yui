import os
import json
from filelock import FileLock, Timeout
import helpers.constant as con


def read_repository():
    # Cek apakah file ada sebelum membuka file
    if not os.path.exists(con.REPO_PATH):
        return {}

    # Baca file
    with open(con.REPO_PATH, "r") as file:
        return json.load(file)


def update_repository(
    repo: str,
    app_name: str,
    app_path: str,
    version: str,
    download_url: str,
    desktop_path: str,
    icon_path: str,
):
    # Buat file lock
    try:
        with FileLock(con.REPO_PATH + ".lock", timeout=5):
            # Baca data repo
            data = read_repository()

            # Buat dict untuk data repo
            data[repo] = {
                "app_name": app_name,
                "app_path": app_path,
                "version": version,
                "download_url": download_url,
                "desktop_path": desktop_path,
                "icon_path": icon_path,
            }

            # Simpan data ke repo
            with open(con.REPO_PATH, "w") as file:
                json.dump(data, file, indent=2)
    except Timeout:
        print("Unable to access repos.json. Please try again later.")


def remove_repository(app_url: str):
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
        print("")


def get_list_app():
    return list(read_repository().keys())
