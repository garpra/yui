import os
import re
import shutil
from helpers.constant import APPIMAGE_PATH
from helpers.models import ReleaseData
from helpers.utils import error_fetch_app


def get_app_name(filename: str) -> str:
    # Ambil nama file tanpa path & ekstensi
    name = os.path.splitext(os.path.basename(filename))[0]

    # Ambil bagian sebelum versi
    match = re.match(r"^(.+?)[-_.]v?\d", name)
    return match.group(1) if match else name


def move_local_app(app_url: str) -> None:
    app_base = os.path.basename(app_url)
    dest_path = os.path.join(APPIMAGE_PATH, app_base)

    # Pindahkan appimage ke path tujuan
    shutil.move(app_base, dest_path)


def fetch_local_app(app_url: str) -> ReleaseData:
    # Cek realpath dari app_url
    realpath = os.path.realpath(app_url)

    # Cek jika path benar file
    if not os.path.isfile(realpath):
        return error_fetch_app("AppImage not found in path")

    app_name = get_app_name(realpath)
    app_path = os.path.join(APPIMAGE_PATH, os.path.basename(realpath))

    return {
        "success": True,
        "app_name": app_name,
        "app_path": app_path,
        "version": "",
        "download_url": "",
        "status": "Get data success",
    }
