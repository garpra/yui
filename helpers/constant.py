import os

ROOT_FOLDER = os.environ.get(
    "YUI_DATA_DIR", os.path.join(os.path.expanduser("~"), ".local", "share", "yui")
)
APPIMAGE_PATH = os.path.join(ROOT_FOLDER, "appimage")
REPO_PATH = os.path.join(ROOT_FOLDER, "repos.json")
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
ICON_PATH = os.path.join(os.path.expanduser("~"), ".local", "share", "icons")
