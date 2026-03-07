"""
Shared fixtures untuk seluruh test suite yui.

conftest.py ini otomatis diload oleh pytest dan menyediakan:
- setup_yui_env: redirect semua path yui ke tmp_path agar test tidak
  menyentuh filesystem user yang sebenarnya.
- sample_record: contoh AppRecord siap pakai.
"""

import importlib
import sys
import pytest
from helpers.models import AppRecord


@pytest.fixture(autouse=False)
def setup_yui_env(tmp_path, monkeypatch):
    """
    Redirect semua path yui ke direktori sementara.

    Fixture ini WAJIB dipakai oleh semua test yang menyentuh filesystem
    (repository, downloader, appimage). Tanpa ini, test akan menulis ke
    ~/.local/share/yui user yang sebenarnya.

    Cara pakai: tambahkan `setup_yui_env` ke parameter fungsi test,
    atau tandai modul test dengan `pytestmark = pytest.mark.usefixtures("setup_yui_env")`.
    """
    root = tmp_path / "yui"
    appimage_dir = root / "appimage"
    appimage_dir.mkdir(parents=True)

    desktop_dir = tmp_path / "applications"
    desktop_dir.mkdir()

    icon_dir = tmp_path / "icons" / "yui"
    icon_dir.mkdir(parents=True)

    monkeypatch.setenv("YUI_DATA_DIR", str(root))

    # Reload constant agar pakai env var yang baru
    import helpers.constant as con
    monkeypatch.setattr(con, "ROOT_FOLDER", str(root))
    monkeypatch.setattr(con, "APPIMAGE_PATH", str(appimage_dir))
    monkeypatch.setattr(con, "REPO_PATH", str(root / "repos.json"))
    monkeypatch.setattr(con, "DESKTOP_PATH", str(desktop_dir))
    monkeypatch.setattr(con, "ICON_PATH", str(icon_dir))

    return {
        "root": root,
        "appimage_dir": appimage_dir,
        "desktop_dir": desktop_dir,
        "icon_dir": icon_dir,
        "repo_path": root / "repos.json",
    }


@pytest.fixture
def sample_record():
    """Contoh AppRecord lengkap untuk dipakai di berbagai test."""
    return AppRecord(
        app_name="App.AppImage",
        app_path="/tmp/yui/appimage/App.AppImage",
        version="v1.0.0",
        download_url="https://github.com/owner/app/releases/download/v1.0.0/App.AppImage",
        desktop_path="/tmp/applications/app.desktop",
        icon_path="/tmp/icons/yui/app.png",
    )
