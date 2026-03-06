import os
from helpers.utils import extract_icon_appimage

ROOT_FOLDER = os.path.join(os.path.expanduser("~"), ".local", "share", "yui")
APPIMAGE_PATH = os.path.join(ROOT_FOLDER, "appimage")

app_path = os.path.join(APPIMAGE_PATH, "Heroic-2.20.1-linux-x86_64.AppImage")

extract_icon_appimage(app_path)
