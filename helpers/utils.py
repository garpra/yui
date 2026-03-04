import json
import requests
import sys
import os

# Temporary Repo folder
ROOT_FOLDER = os.path.join(".local", "share", "yui")


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


def download(url: str, location: str):
    try:
        # Ambil data dari url
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Download Error: {err}")
        return

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    # Download dan simpan content dari response dengan progress
    with open(location, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
            downloaded += len(chunk)
            print_progress(downloaded, total_size)

    print()


REPO_PATH = os.path.join(ROOT_FOLDER, "repos.json")


def read_repository():
    # Cek apakah file ada sebelum membuka file
    if not os.path.exists(REPO_PATH):
        return {}

    # Baca file
    with open(REPO_PATH, "r") as file:
        return json.load(file)


def update_repository(repo: str, app_name: str, version: str, download_url: str):
    # Baca data repo
    data = read_repository()

    # Buat dict untuk data repo
    data[repo] = {
        "app_name": app_name,
        "version": version,
        "download_url": download_url,
    }

    # Simpan data ke repo
    with open(REPO_PATH, "w") as file:
        json.dump(data, file, indent=2)
