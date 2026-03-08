import os
import stat
import subprocess
import time
import glob
import shutil
import helpers.constant as con
import helpers.models as types

ICON_DIRS = [
    "/usr/share/icons",
    os.path.expanduser("~/.local/share/icons"),
    "/usr/share/pixmaps",
]


def remove_appimage(app_path: str) -> None:
    """
    Hapus file AppImage dari sistem file.
    """
    # Cek jika app path ada
    if os.path.exists(app_path):
        os.remove(app_path)
    else:
        print("File already deleted")


def find_icon(name: str) -> list[str]:
    """
    Cari file icon berdasarkan nama (tanpa ekstensi) di direktori icon sistem.

    Menelusuri ICON_DIRS secara rekursif dan mengembalikan semua path
    yang cocok dengan nama dan berekstensi .png, .svg, atau .xpm.
    """
    results = []
    for d in ICON_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in files:
                stem, ext = os.path.splitext(f)
                if ext in (".png", ".svg", ".xpm") and stem == name:
                    results.append(os.path.join(root, f))
    return results


def get_icon_name(filepath: str) -> str | None:
    """
    Ambil nilai Icon= dari file .desktop.

    Membaca file .desktop dan mengembalikan nama icon yang tertera
    di baris Icon= dalam section [Desktop Entry]. Mengembalikan None
    jika tidak ditemukan atau file tidak bisa dibaca.
    """
    try:
        with open(filepath) as f:
            for line in f:
                if line.startswith("Icon="):
                    return line.split("=", 1)[1].strip()
    except OSError:
        return None
    return None


def fix_desktop_entry(desktop_path: str, app_path: str, icon_path: str) -> None:
    """
    Perbaiki Exec dan Icon di .desktop entry agar menunjuk ke path yang benar.

    Hanya mengganti Exec= pertama di dalam section [Desktop Entry].
    Icon= diganti di seluruh file karena biasanya hanya muncul sekali.
    """
    with open(desktop_path, "r") as f:
        lines = f.readlines()

    in_desktop_entry = False
    exec_fixed = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("["):
            in_desktop_entry = stripped == "[Desktop Entry]"
        if in_desktop_entry and stripped.startswith("Exec=") and not exec_fixed:
            lines[i] = f"Exec={app_path} %U\n"
            exec_fixed = True
        if get_icon_name(line):
            if in_desktop_entry and stripped.startswith("Icon="):
                lines[i] = f"Icon={icon_path}\n"

    with open(desktop_path, "w") as f:
        f.writelines(lines)


def remove_desktop_entry(desktop_path: str) -> None:
    """
    Hapus file desktop entry dari sistem file.

    File desktop entry (.desktop) digunakan oleh lingkungan desktop Linux untuk
    menampilkan aplikasi di menu aplikasi dan launcher.
    """
    # Cek jika desktop entry path ada
    if os.path.exists(desktop_path):
        os.remove(desktop_path)
    else:
        print("Desktop Entry already deleted")


def make_executable(app_path: str) -> None:
    """
    Atur izin executable pada file AppImage.

    Ini diperlukan agar file AppImage dapat dijalankan pada sistem Linux.
    """
    # Cek jika appimage ada
    if not os.path.exists(app_path):
        raise FileNotFoundError(f"AppImage not found: {app_path}")

    # Ambil status appimage
    current_mode = os.stat(app_path).st_mode

    # Ubah appimage ke executable
    os.chmod(app_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def extract_data_appimage(app_path: str) -> types.AppPathData:
    """
    Ekstrak data desktop dan ikon dari file AppImage dengan cara mounting.

    Mount file AppImage menggunakan flag bawaan --appimage-mount, kemudian
    mencari file .desktop dan .png di dalam sistem file yang di-mount. File-file
    ini disalin ke direktori sistem yang sesuai (~/.local/share/applications
    dan ~/.local/share/icons/yui) sehingga aplikasi muncul di menu desktop.

    Mount akan dibersihkan secara otomatis setelah ekstraksi.
    """
    app_data: types.AppPathData = {"desktop_path": "", "icon_path": ""}

    # Validasi app_path
    real_path = os.path.realpath(app_path)
    if not real_path.startswith(os.path.realpath(con.APPIMAGE_PATH)):
        raise ValueError(f"Suspicious app path: {app_path}")

    # Jalankan command mount untuk appimage
    proc = subprocess.Popen(
        [app_path, "--appimage-mount"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Ambil path mount dari command yang sudah dijalankan
    mount_app = proc.stdout.readline().decode().strip()

    # Tunggu mount selesai
    for _ in range(10):
        # Jika mount ada keluar dari looping
        if os.path.isdir(mount_app):
            break
        time.sleep(0.3)
    else:
        # Jika mount path tidak ditemukan dalam 10 detik
        # Hentikan command
        proc.terminate()
        raise RuntimeError(f"Mount path not available: {mount_app}")

    try:
        # Ambil file path .desktop dan .png di mount path
        desktop_file = glob.glob(os.path.join(mount_app, "*.desktop"))
        icon_app = glob.glob(os.path.join(mount_app, "*.png"))

        # Buat folder jika tidak ada
        os.makedirs(con.DESKTOP_PATH, exist_ok=True)
        os.makedirs(con.ICON_PATH, exist_ok=True)

        # Cek apakah menemukan desktop entry
        if desktop_file:
            desktop_name = os.path.basename(desktop_file[0])
            dest_desktop = os.path.join(con.DESKTOP_PATH, desktop_name)
            # Copy file dari mount app ke tujuan
            shutil.copy2(desktop_file[0], con.DESKTOP_PATH)
            app_data["desktop_path"] = dest_desktop

        # Tentukan icon yang akan dipakai:
        # Cek apakah icon dengan nama yang sama sudah ada di sistem
        # Jika tidak ada, ekstrak icon dari AppImage
        icon_path_to_use = ""

        if desktop_file:
            # Baca nama icon dari .desktop yang masih di dalam mount
            icon_name = get_icon_name(desktop_file[0])
            if icon_name:
                system_icons = find_icon(icon_name)
                if system_icons:
                    # Icon sudah tersedia di sistem, tidak perlu salin
                    icon_path_to_use = system_icons[0]

        if not icon_path_to_use and icon_app:
            # Icon tidak ditemukan di sistem, salin dari AppImage
            icon_filename = os.path.basename(icon_app[0])
            dest_icon = os.path.join(con.ICON_PATH, icon_filename)
            shutil.copy2(icon_app[0], con.ICON_PATH)
            app_data["icon_path"] = dest_icon
            icon_path_to_use = dest_icon

        # Fix Exec dan Icon di desktop entry
        if app_data["desktop_path"]:
            fix_desktop_entry(app_data["desktop_path"], app_path, icon_path_to_use)

    finally:
        # Matikan command
        proc.terminate()
        proc.wait()

    return app_data
