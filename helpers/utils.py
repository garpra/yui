import json
import requests
import sys
import os
import stat
import subprocess
import glob
import shutil

ROOT_FOLDER = os.path.join(os.path.expanduser("~"), ".local", "share", "yui")
APPIMAGE_PATH = os.path.join(ROOT_FOLDER, "appimage")
REPO_PATH = os.path.join(ROOT_FOLDER, "repos.json")


def remove_appimage(app_path: str):
    if os.path.exists(app_path):
        os.remove(app_path)
    else:
        print("File already deleted")


def make_executable(app_path: str):
    # Ambil status appimage
    current_mode = os.stat(app_path).st_mode

    # Cek jika appimage ada
    if os.path.exists(app_path):
        # Ubah appimage ke executable
        os.chmod(app_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return True
    else:
        return False


def remove_desktop_entry(desktop_path: str):
    if os.path.exists(desktop_path):
        os.remove(desktop_path)
    else:
        print("Desktop Entry already deleted")


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
            "app_path": None,
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
            download_path = os.path.join(APPIMAGE_PATH, name)
            return {
                "success": True,
                "app_name": name,
                "app_path": download_path,
                "version": version,
                "download_url": download_url,
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


# Membuat fungsi untuk progress bar proses download
def print_progress(downloaded: int, total: int):
    # Jika total ukuran tidak diketahui
    if total == 0:
        # Tampilkan jumlah data yang sudah diunduh dalam KB
        print(f"\rDownloading... {downloaded / 1024:.1f} KB", end="")
        return

    # Hitung persentase progress (0 - 100)
    percent = downloaded / total * 100

    # Tentukan jumlah blok progress bar, Setiap blok mewakili 5%
    filled = int(percent / 5)

    # Buat string progress bar
    bar = "█" * filled + "░" * (20 - filled)

    # Konversi byte ke kilobyte untuk tampilan yang lebih dibaca
    downloaded_kb = downloaded / 1024
    total_kb = total / 1024

    # Tulis output ke terminal tanpa pindah baris
    sys.stdout.write(
        f"\rDownloading [{bar}] {percent:.1f}% ({downloaded_kb:.1f}/{total_kb:.1f} KB)"
    )

    # Memastikan output langsung muncul
    sys.stdout.flush()


def download(url: str, app_path: str):
    try:
        # Ambil data dari url
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Download Error: {err}")
        return

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    # Buat folder jika belum ada
    os.makedirs(APPIMAGE_PATH, exist_ok=True)

    # Download dan simpan content dari response dengan progress
    with open(app_path, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
            downloaded += len(chunk)
            print_progress(downloaded, total_size)

    print()


def read_repository():
    # Cek apakah file ada sebelum membuka file
    if not os.path.exists(REPO_PATH):
        return {}

    # Baca file
    with open(REPO_PATH, "r") as file:
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
    with open(REPO_PATH, "w") as file:
        json.dump(data, file, indent=2)


def remove_repository(app_url: str):
    # Ambil data repo
    data = read_repository()

    # Hapus data repo sesuai dengan 'app_url'
    data.pop(app_url, "")

    # Update data repo
    with open(REPO_PATH, "w") as file:
        json.dump(data, file, indent=2)


def get_list_app():
    # Baca data repo
    data = read_repository()
    repo_list = []

    # Ambil key name appnya saja
    for app_url in data:
        repo_list.append(app_url)

    return repo_list


def extract_data_appimage(app_path: str):
    app_data = []

    # Jalankan command mount untuk appimage
    proc = subprocess.Popen(
        [app_path, "--appimage-mount"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Ambil path mount dari command yang sudah dijalankan
    mount_app = proc.stdout.readline().decode().strip()

    # Ambil file path .desktop dan .png di mount path
    desktop_file = glob.glob(os.path.join(mount_app, "*.desktop"))
    icon_app = glob.glob(os.path.join(mount_app, "*.png"))

    # Buat path tujuan untuk desktop entry dan icon
    desktop_path = os.path.join(
        os.path.expanduser("~"), ".local", "share", "applications"
    )
    icon_path = os.path.join(os.path.expanduser("~"), ".local", "share", "icons", "yui")

    # Buat folder jika tidak ada
    os.makedirs(desktop_path, exist_ok=True)
    os.makedirs(icon_path, exist_ok=True)

    # Cek apakah menemukan desktop entry
    if desktop_file:
        desktop_name = os.path.basename(desktop_file[0])
        dest_desktop = os.path.join(desktop_path, desktop_name)
        # Copy file dari mount app ke tujuan
        shutil.copy2(desktop_file[0], desktop_path)
        app_data.append(dest_desktop)

    # Cek apakah menemukan icon
    if icon_app:
        icon_name = os.path.basename(icon_app[0])
        dest_icon = os.path.join(icon_path, icon_name)
        # Copy file dari mount app ke tujuan
        shutil.copy2(icon_app[0], icon_path)
        app_data.append(dest_icon)

    # Matikan command
    proc.terminate()
    return app_data
