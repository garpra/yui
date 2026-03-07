"""
Test untuk helpers/appimage.py

Mencakup:
- remove_appimage: hapus file AppImage
- remove_desktop_entry: hapus file .desktop
- make_executable: set permission executable
- fix_desktop_entry: perbaiki Exec= dan Icon= di .desktop
- extract_data_appimage: mount + ekstrak (subprocess dimock)
"""

import os
import stat
import pytest
from unittest.mock import patch, MagicMock

from helpers.appimage import (
    remove_appimage,
    remove_desktop_entry,
    make_executable,
    fix_desktop_entry,
    extract_data_appimage,
)

pytestmark = pytest.mark.usefixtures("setup_yui_env")


# ---------------------------------------------------------------------------
# remove_appimage
# ---------------------------------------------------------------------------

class TestRemoveAppimage:
    def test_hapus_file_yang_ada(self, tmp_path):
        f = tmp_path / "App.AppImage"
        f.write_text("dummy")
        remove_appimage(str(f))
        assert not f.exists()

    def test_tidak_error_jika_file_tidak_ada(self, capsys):
        remove_appimage("/tmp/tidak-ada.AppImage")
        captured = capsys.readouterr()
        assert "already deleted" in captured.out


# ---------------------------------------------------------------------------
# remove_desktop_entry
# ---------------------------------------------------------------------------

class TestRemoveDesktopEntry:
    def test_hapus_file_yang_ada(self, tmp_path):
        f = tmp_path / "app.desktop"
        f.write_text("[Desktop Entry]\nName=App\n")
        remove_desktop_entry(str(f))
        assert not f.exists()

    def test_tidak_error_jika_file_tidak_ada(self, capsys):
        remove_desktop_entry("/tmp/tidak-ada.desktop")
        captured = capsys.readouterr()
        assert "already deleted" in captured.out


# ---------------------------------------------------------------------------
# make_executable
# ---------------------------------------------------------------------------

class TestMakeExecutable:
    def test_set_permission_executable(self, tmp_path):
        f = tmp_path / "App.AppImage"
        f.write_bytes(b"ELF")
        # Pastikan awalnya tidak executable
        os.chmod(str(f), 0o644)

        make_executable(str(f))

        mode = os.stat(str(f)).st_mode
        assert mode & stat.S_IXUSR  # owner executable
        assert mode & stat.S_IXGRP  # group executable
        assert mode & stat.S_IXOTH  # other executable

    def test_raise_jika_file_tidak_ada(self):
        with pytest.raises(FileNotFoundError, match="AppImage not found"):
            make_executable("/tmp/tidak-ada.AppImage")

    def test_permission_lain_tidak_terganggu(self, tmp_path):
        f = tmp_path / "App.AppImage"
        f.write_bytes(b"ELF")
        os.chmod(str(f), 0o644)  # rw-r--r--

        make_executable(str(f))

        mode = os.stat(str(f)).st_mode
        # Read permission harus tetap ada
        assert mode & stat.S_IRUSR
        assert mode & stat.S_IRGRP


# ---------------------------------------------------------------------------
# fix_desktop_entry
# ---------------------------------------------------------------------------

class TestFixDesktopEntry:
    def test_ganti_exec_dan_icon(self, tmp_path):
        desktop = tmp_path / "app.desktop"
        desktop.write_text(
            "[Desktop Entry]\nName=App\nExec=AppRun\nIcon=app\nType=Application\n"
        )
        fix_desktop_entry(str(desktop), "/path/App.AppImage", "/path/app.png")
        content = desktop.read_text()

        assert "Exec=/path/App.AppImage %U\n" in content
        assert "Icon=/path/app.png\n" in content
        assert "Exec=AppRun" not in content
        assert "Icon=app\n" not in content

    def test_hanya_ganti_exec_pertama_di_desktop_entry(self, tmp_path):
        desktop = tmp_path / "app.desktop"
        desktop.write_text(
            "[Desktop Entry]\n"
            "Exec=AppRun\n"
            "\n"
            "[Desktop Action NewWindow]\n"
            "Exec=AppRun --new-window\n"
        )
        fix_desktop_entry(str(desktop), "/App.AppImage", "/icon.png")
        content = desktop.read_text()

        assert "Exec=/App.AppImage %U\n" in content
        # Exec di action section TIDAK boleh diganti
        assert "Exec=AppRun --new-window\n" in content

    def test_hanya_ganti_icon_di_desktop_entry(self, tmp_path):
        desktop = tmp_path / "app.desktop"
        desktop.write_text(
            "[Desktop Entry]\n"
            "Exec=AppRun\n"
            "Icon=app\n"
            "\n"
            "[Desktop Action NewWindow]\n"
            "Exec=AppRun --new\n"
            "Icon=app-action\n"
        )
        fix_desktop_entry(str(desktop), "/App.AppImage", "/icon.png")
        content = desktop.read_text()

        assert "Icon=/icon.png\n" in content
        # Icon di action section TIDAK boleh diganti
        assert "Icon=app-action\n" in content

    def test_exec_diperbaiki_meski_tanpa_icon(self, tmp_path):
        desktop = tmp_path / "app.desktop"
        desktop.write_text("[Desktop Entry]\nName=App\nExec=AppRun\n")
        fix_desktop_entry(str(desktop), "/App.AppImage", "")

        content = desktop.read_text()
        assert "Exec=/App.AppImage %U\n" in content

    def test_icon_kosong_ditulis_jika_ada_baris_icon(self, tmp_path):
        desktop = tmp_path / "app.desktop"
        desktop.write_text("[Desktop Entry]\nExec=AppRun\nIcon=app\n")
        fix_desktop_entry(str(desktop), "/App.AppImage", "")

        content = desktop.read_text()
        assert "Icon=\n" in content

    def test_tidak_ada_exec_di_file_tidak_crash(self, tmp_path):
        desktop = tmp_path / "app.desktop"
        desktop.write_text("[Desktop Entry]\nName=App\nType=Application\n")
        # Tidak boleh raise exception
        fix_desktop_entry(str(desktop), "/App.AppImage", "/icon.png")

    def test_baris_lain_tidak_berubah(self, tmp_path):
        desktop = tmp_path / "app.desktop"
        desktop.write_text(
            "[Desktop Entry]\nName=My App\nExec=AppRun\nIcon=app\nType=Application\nCategories=Utility;\n"
        )
        fix_desktop_entry(str(desktop), "/App.AppImage", "/icon.png")
        content = desktop.read_text()

        assert "Name=My App\n" in content
        assert "Type=Application\n" in content
        assert "Categories=Utility;\n" in content

    def test_format_exec_menyertakan_percent_u(self, tmp_path):
        desktop = tmp_path / "app.desktop"
        desktop.write_text("[Desktop Entry]\nExec=AppRun\n")
        fix_desktop_entry(str(desktop), "/path/to/App.AppImage", "/icon.png")

        assert "Exec=/path/to/App.AppImage %U\n" in desktop.read_text()


# ---------------------------------------------------------------------------
# extract_data_appimage (subprocess dimock)
# ---------------------------------------------------------------------------

class TestExtractDataAppimage:
    def _make_fake_appimage(self, appimage_dir) -> str:
        """Buat file AppImage palsu di direktori yang valid."""
        f = appimage_dir / "App.AppImage"
        f.write_bytes(b"ELF")
        os.chmod(str(f), 0o755)
        return str(f)

    def _mock_proc(self, mount_path: str):
        """Buat mock subprocess.Popen yang mensimulasikan --appimage-mount."""
        proc = MagicMock()
        proc.stdout.readline.return_value = (mount_path + "\n").encode()
        proc.terminate = MagicMock()
        proc.wait = MagicMock()
        return proc

    def test_ekstrak_desktop_dan_icon(self, setup_yui_env, tmp_path):
        app_path = self._make_fake_appimage(setup_yui_env["appimage_dir"])

        # Buat direktori mount palsu dengan .desktop dan .png
        mount_dir = tmp_path / "mount"
        mount_dir.mkdir()
        (mount_dir / "app.desktop").write_text(
            "[Desktop Entry]\nName=App\nExec=AppRun\nIcon=app\n"
        )
        (mount_dir / "app.png").write_bytes(b"PNG")

        mock_proc = self._mock_proc(str(mount_dir))

        with patch("helpers.appimage.subprocess.Popen", return_value=mock_proc):
            result = extract_data_appimage(app_path)

        assert result["desktop_path"] != ""
        assert result["icon_path"] != ""
        assert result["desktop_path"].endswith("app.desktop")
        assert result["icon_path"].endswith("app.png")

    def test_exec_diperbaiki_setelah_ekstrak(self, setup_yui_env, tmp_path):
        app_path = self._make_fake_appimage(setup_yui_env["appimage_dir"])

        mount_dir = tmp_path / "mount"
        mount_dir.mkdir()
        (mount_dir / "app.desktop").write_text(
            "[Desktop Entry]\nExec=AppRun\nIcon=app\n"
        )
        (mount_dir / "app.png").write_bytes(b"PNG")

        mock_proc = self._mock_proc(str(mount_dir))

        with patch("helpers.appimage.subprocess.Popen", return_value=mock_proc):
            result = extract_data_appimage(app_path)

        content = open(result["desktop_path"]).read()
        assert f"Exec={app_path} %U" in content

    def test_tanpa_desktop_dan_icon(self, setup_yui_env, tmp_path):
        app_path = self._make_fake_appimage(setup_yui_env["appimage_dir"])

        mount_dir = tmp_path / "mount"
        mount_dir.mkdir()
        # Mount kosong, tidak ada .desktop atau .png

        mock_proc = self._mock_proc(str(mount_dir))

        with patch("helpers.appimage.subprocess.Popen", return_value=mock_proc):
            result = extract_data_appimage(app_path)

        assert result["desktop_path"] == ""
        assert result["icon_path"] == ""

    def test_proc_selalu_diterminasi_meski_exception(self, setup_yui_env, tmp_path):
        app_path = self._make_fake_appimage(setup_yui_env["appimage_dir"])

        mount_dir = tmp_path / "mount"
        mount_dir.mkdir()
        (mount_dir / "app.desktop").write_text("[Desktop Entry]\nExec=AppRun\n")

        mock_proc = self._mock_proc(str(mount_dir))

        # Paksa shutil.copy2 raise exception untuk test finally block
        with patch("helpers.appimage.subprocess.Popen", return_value=mock_proc):
            with patch("helpers.appimage.shutil.copy2", side_effect=OSError("disk full")):
                with pytest.raises(OSError):
                    extract_data_appimage(app_path)

        # proc.terminate() harus tetap dipanggil meski ada exception
        mock_proc.terminate.assert_called()
        mock_proc.wait.assert_called()

    def test_raise_jika_path_di_luar_appimage_dir(self, tmp_path):
        malicious_path = str(tmp_path / "../../etc/passwd")
        with pytest.raises(ValueError, match="Suspicious app path"):
            extract_data_appimage(malicious_path)

    def test_raise_jika_mount_tidak_tersedia(self, setup_yui_env, tmp_path):
        app_path = self._make_fake_appimage(setup_yui_env["appimage_dir"])

        mount_dir = tmp_path / "nonexistent_mount"
        # Mount dir sengaja tidak dibuat

        mock_proc = self._mock_proc(str(mount_dir))

        with patch("helpers.appimage.subprocess.Popen", return_value=mock_proc):
            with patch("helpers.appimage.time.sleep"):  # percepat test
                with pytest.raises(RuntimeError, match="Mount path not available"):
                    extract_data_appimage(app_path)

        mock_proc.terminate.assert_called()
