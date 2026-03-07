import sys
import requests
import os
import helpers.constant as con


# Membuat fungsi untuk progress bar proses download
def print_progress(downloaded: int, total: int) -> None:
    """
    Tampilkan progress bar unduhan di terminal.

    Mencetak progress bar visual dengan informasi persentase dan ukuran unduhan.
    """
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


def download(url: str, app_path: str) -> None:
    """
    Unduh file dari URL ke path yang ditentukan.

    Mengunduh file dalam potongan dan menampilkannya dalam progress bar. Jika unduhan
    gagal, file yang telah diunduh sebagian akan dihapus secara otomatis.
    """
    try:
        # Ambil data dari url
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise RuntimeError(f"Download failed: {err}") from err

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    # Buat folder jika belum ada
    os.makedirs(con.APPIMAGE_PATH, exist_ok=True)

    try:
        # Download dan simpan content dari response dengan progress
        with open(app_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=65536):
                file.write(chunk)
                downloaded += len(chunk)
                print_progress(downloaded, total_size)
    except Exception:
        # Jika gagal download hapus appimage
        os.remove(app_path)
        raise

    print()
