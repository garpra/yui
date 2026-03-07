"""
Test untuk commands/ (install, update, delete, list)

Semua external dependencies (fetch_latest_release, download, dll.)
dimock sehingga test ini cepat dan tidak perlu network atau filesystem nyata.
"""

import pytest
from unittest.mock import patch, MagicMock, call
import argparse

from commands.install import install_app
from commands.update import update_app
from commands.delete import delete_app
from commands.list import list_app
from helpers.models import AppRecord

pytestmark = pytest.mark.usefixtures("setup_yui_env")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_args(**kwargs):
    """Buat argparse.Namespace dari keyword arguments."""
    return argparse.Namespace(**kwargs)


def make_release(version="v1.0.0", app_name="App.AppImage", app_path="/tmp/App.AppImage"):
    return {
        "success": True,
        "app_name": app_name,
        "app_path": app_path,
        "version": version,
        "download_url": "https://github.com/owner/app/releases/download/v1.0.0/App.AppImage",
        "status": "Get data success",
    }


def make_failed_release(status="AppImage not found"):
    return {
        "success": False,
        "app_name": None,
        "app_path": None,
        "version": None,
        "download_url": None,
        "status": status,
    }


def make_app_path_data(desktop="", icon=""):
    return {"desktop_path": desktop, "icon_path": icon}


# ---------------------------------------------------------------------------
# install_app
# ---------------------------------------------------------------------------

class TestInstallApp:
    BASE_PATCHES = {
        "fetch": "commands.install.fetch_latest_release",
        "download": "commands.install.download",
        "make_exec": "commands.install.make_executable",
        "extract": "commands.install.extract_data_appimage",
        "update_repo": "commands.install.update_repository",
        "exists": "commands.install.os.path.exists",
    }

    def test_install_sukses(self, setup_yui_env):
        app_path = str(setup_yui_env["appimage_dir"] / "App.AppImage")
        release = make_release(app_path=app_path)

        with patch(self.BASE_PATCHES["fetch"], return_value=release), \
             patch(self.BASE_PATCHES["exists"], return_value=False), \
             patch(self.BASE_PATCHES["download"]) as mock_dl, \
             patch(self.BASE_PATCHES["make_exec"]) as mock_exec, \
             patch(self.BASE_PATCHES["extract"], return_value=make_app_path_data("/d/app.desktop", "/i/app.png")), \
             patch(self.BASE_PATCHES["update_repo"]) as mock_update:

            install_app(make_args(app_url="owner/app"))

            mock_dl.assert_called_once()
            mock_exec.assert_called_once_with(app_path)
            mock_update.assert_called_once()

    def test_skip_jika_sudah_terinstall(self, setup_yui_env, capsys):
        app_path = str(setup_yui_env["appimage_dir"] / "App.AppImage")
        release = make_release(app_path=app_path)

        with patch(self.BASE_PATCHES["fetch"], return_value=release), \
             patch(self.BASE_PATCHES["exists"], return_value=True), \
             patch(self.BASE_PATCHES["download"]) as mock_dl:

            install_app(make_args(app_url="owner/app"))
            mock_dl.assert_not_called()

        captured = capsys.readouterr()
        assert "latest version" in captured.out

    def test_gagal_jika_fetch_gagal(self, capsys):
        with patch(self.BASE_PATCHES["fetch"], return_value=make_failed_release()):
            install_app(make_args(app_url="owner/app"))

        captured = capsys.readouterr()
        assert "Failed to get data" in captured.out

    def test_update_repository_dipanggil_dengan_record_yang_benar(self, setup_yui_env):
        app_path = str(setup_yui_env["appimage_dir"] / "App.AppImage")
        release = make_release(app_path=app_path)
        desktop = "/d/app.desktop"
        icon = "/i/app.png"

        captured_record = {}

        def fake_update(repo, record):
            captured_record["repo"] = repo
            captured_record["record"] = record

        with patch(self.BASE_PATCHES["fetch"], return_value=release), \
             patch(self.BASE_PATCHES["exists"], return_value=False), \
             patch(self.BASE_PATCHES["download"]), \
             patch(self.BASE_PATCHES["make_exec"]), \
             patch(self.BASE_PATCHES["extract"], return_value=make_app_path_data(desktop, icon)), \
             patch(self.BASE_PATCHES["update_repo"], side_effect=fake_update):

            install_app(make_args(app_url="owner/app"))

        assert captured_record["repo"] == "owner/app"
        assert isinstance(captured_record["record"], AppRecord)
        assert captured_record["record"].desktop_path == desktop
        assert captured_record["record"].icon_path == icon
        assert captured_record["record"].version == "v1.0.0"


# ---------------------------------------------------------------------------
# update_app
# ---------------------------------------------------------------------------

class TestUpdateApp:
    BASE_PATCHES = {
        "get_list": "commands.update.get_list_app",
        "read_repo": "commands.update.read_repository",
        "fetch": "commands.update.fetch_latest_release",
        "download": "commands.update.download",
        "make_exec": "commands.update.make_executable",
        "extract": "commands.update.extract_data_appimage",
        "update_repo": "commands.update.update_repository",
        "remove_app": "commands.update.remove_appimage",
        "remove_desktop": "commands.update.remove_desktop_entry",
    }

    def _repo_data(self, version="v1.0.0"):
        return {
            "owner/app": {
                "app_name": "App.AppImage",
                "app_path": "/old/App.AppImage",
                "version": version,
                "download_url": "https://github.com/...",
                "desktop_path": "/old/app.desktop",
                "icon_path": "/old/app.png",
            }
        }

    def test_tidak_ada_app_terinstall(self, capsys):
        with patch(self.BASE_PATCHES["get_list"], return_value=[]):
            update_app(make_args())

        assert "No application is installed" in capsys.readouterr().out

    def test_skip_jika_sudah_versi_terbaru(self, capsys):
        with patch(self.BASE_PATCHES["get_list"], return_value=["owner/app"]), \
             patch(self.BASE_PATCHES["read_repo"], return_value=self._repo_data("v1.0.0")), \
             patch(self.BASE_PATCHES["fetch"], return_value=make_release(version="v1.0.0")), \
             patch(self.BASE_PATCHES["download"]) as mock_dl:

            update_app(make_args())
            mock_dl.assert_not_called()

        assert "latest version" in capsys.readouterr().out

    def test_update_jika_ada_versi_baru(self, setup_yui_env):
        new_app_path = str(setup_yui_env["appimage_dir"] / "App-v2.AppImage")
        new_release = make_release(version="v2.0.0", app_path=new_app_path)

        with patch(self.BASE_PATCHES["get_list"], return_value=["owner/app"]), \
             patch(self.BASE_PATCHES["read_repo"], return_value=self._repo_data("v1.0.0")), \
             patch(self.BASE_PATCHES["fetch"], return_value=new_release), \
             patch(self.BASE_PATCHES["download"]) as mock_dl, \
             patch(self.BASE_PATCHES["remove_app"]) as mock_rm_app, \
             patch(self.BASE_PATCHES["remove_desktop"]) as mock_rm_desk, \
             patch(self.BASE_PATCHES["make_exec"]), \
             patch(self.BASE_PATCHES["extract"], return_value=make_app_path_data("/d/app.desktop", "/i/app.png")), \
             patch(self.BASE_PATCHES["update_repo"]) as mock_update:

            update_app(make_args())

            mock_dl.assert_called_once()
            mock_rm_app.assert_called_once_with("/old/App.AppImage")
            mock_rm_desk.assert_called_once_with("/old/app.desktop")
            mock_update.assert_called_once()

    def test_download_dulu_sebelum_hapus_yang_lama(self, setup_yui_env):
        """Pastikan urutan: download → hapus lama (bukan sebaliknya)."""
        call_order = []
        new_release = make_release(version="v2.0.0", app_path="/new/App.AppImage")

        def fake_download(*a, **kw): call_order.append("download")
        def fake_remove_app(*a, **kw): call_order.append("remove_app")
        def fake_remove_desk(*a, **kw): call_order.append("remove_desktop")

        with patch(self.BASE_PATCHES["get_list"], return_value=["owner/app"]), \
             patch(self.BASE_PATCHES["read_repo"], return_value=self._repo_data("v1.0.0")), \
             patch(self.BASE_PATCHES["fetch"], return_value=new_release), \
             patch(self.BASE_PATCHES["download"], side_effect=fake_download), \
             patch(self.BASE_PATCHES["remove_app"], side_effect=fake_remove_app), \
             patch(self.BASE_PATCHES["remove_desktop"], side_effect=fake_remove_desk), \
             patch(self.BASE_PATCHES["make_exec"]), \
             patch(self.BASE_PATCHES["extract"], return_value=make_app_path_data()), \
             patch(self.BASE_PATCHES["update_repo"]):

            update_app(make_args())

        assert call_order.index("download") < call_order.index("remove_app")
        assert call_order.index("download") < call_order.index("remove_desktop")

    def test_skip_app_jika_download_gagal(self, setup_yui_env, capsys):
        new_release = make_release(version="v2.0.0")

        with patch(self.BASE_PATCHES["get_list"], return_value=["owner/app"]), \
             patch(self.BASE_PATCHES["read_repo"], return_value=self._repo_data("v1.0.0")), \
             patch(self.BASE_PATCHES["fetch"], return_value=new_release), \
             patch(self.BASE_PATCHES["download"], side_effect=RuntimeError("timeout")), \
             patch(self.BASE_PATCHES["remove_app"]) as mock_rm, \
             patch(self.BASE_PATCHES["update_repo"]) as mock_update:

            update_app(make_args())

            # App lama tidak boleh dihapus jika download gagal
            mock_rm.assert_not_called()
            mock_update.assert_not_called()

        assert "skipping" in capsys.readouterr().out

    def test_lanjut_ke_app_berikutnya_jika_fetch_gagal(self, capsys):
        repo_data = {
            "owner/app-a": {"app_name": "A.AppImage", "app_path": "/a", "version": "v1", "download_url": "", "desktop_path": "", "icon_path": ""},
            "owner/app-b": {"app_name": "B.AppImage", "app_path": "/b", "version": "v1", "download_url": "", "desktop_path": "", "icon_path": ""},
        }

        def fake_fetch(app_url):
            if app_url == "owner/app-a":
                return make_failed_release()
            return make_release(version="v1.0.0")  # sama, tidak perlu update

        with patch(self.BASE_PATCHES["get_list"], return_value=["owner/app-a", "owner/app-b"]), \
             patch(self.BASE_PATCHES["read_repo"], return_value=repo_data), \
             patch(self.BASE_PATCHES["fetch"], side_effect=fake_fetch):

            # Tidak boleh raise exception — harus selesai
            update_app(make_args())

        captured = capsys.readouterr().out
        assert "skipping" in captured


# ---------------------------------------------------------------------------
# delete_app
# ---------------------------------------------------------------------------

class TestDeleteApp:
    BASE_PATCHES = {
        "read_repo": "commands.delete.read_repository",
        "remove_repo": "commands.delete.remove_repository",
        "remove_app": "commands.delete.remove_appimage",
        "remove_desktop": "commands.delete.remove_desktop_entry",
    }

    def _repo_data(self):
        return {
            "owner/app": {
                "app_path": "/path/App.AppImage",
                "desktop_path": "/path/app.desktop",
            }
        }

    def test_hapus_app_yang_ada(self):
        with patch(self.BASE_PATCHES["read_repo"], return_value=self._repo_data()), \
             patch(self.BASE_PATCHES["remove_repo"]) as mock_repo, \
             patch(self.BASE_PATCHES["remove_app"]) as mock_app, \
             patch(self.BASE_PATCHES["remove_desktop"]) as mock_desk:

            delete_app(make_args(app_url="owner/app"))

            mock_repo.assert_called_once_with("owner/app")
            mock_app.assert_called_once_with("/path/App.AppImage")
            mock_desk.assert_called_once_with("/path/app.desktop")

    def test_pesan_error_jika_app_tidak_terinstall(self, capsys):
        with patch(self.BASE_PATCHES["read_repo"], return_value={}):
            delete_app(make_args(app_url="owner/tidak-ada"))

        assert "not installed" in capsys.readouterr().out

    def test_tidak_hapus_jika_app_tidak_ditemukan(self):
        with patch(self.BASE_PATCHES["read_repo"], return_value={}), \
             patch(self.BASE_PATCHES["remove_repo"]) as mock_repo, \
             patch(self.BASE_PATCHES["remove_app"]) as mock_app:

            delete_app(make_args(app_url="owner/tidak-ada"))

            mock_repo.assert_not_called()
            mock_app.assert_not_called()


# ---------------------------------------------------------------------------
# list_app
# ---------------------------------------------------------------------------

class TestListApp:
    def test_tampilkan_app_terinstall(self, capsys):
        with patch("commands.list.get_list_app", return_value=["owner/app-a", "owner/app-b"]):
            list_app(make_args())

        output = capsys.readouterr().out
        assert "owner/app-a" in output
        assert "owner/app-b" in output

    def test_pesan_kosong_jika_tidak_ada_app(self, capsys):
        with patch("commands.list.get_list_app", return_value=[]):
            list_app(make_args())

        assert "No applications found" in capsys.readouterr().out

    def test_tampilkan_header(self, capsys):
        with patch("commands.list.get_list_app", return_value=["owner/app"]):
            list_app(make_args())

        assert "Installed app" in capsys.readouterr().out
