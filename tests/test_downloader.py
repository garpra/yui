"""
Test untuk helpers/downloader.py

Mencakup:
- print_progress: output progress bar
- download: unduh file dengan streaming (requests dimock)
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call
import requests

from helpers.downloader import print_progress, download

pytestmark = pytest.mark.usefixtures("setup_yui_env")


# ---------------------------------------------------------------------------
# print_progress
# ---------------------------------------------------------------------------

class TestPrintProgress:
    def test_total_tidak_diketahui_tampilkan_kb(self, capsys):
        print_progress(2048, 0)
        captured = capsys.readouterr()
        assert "2.0 KB" in captured.out

    def test_tampilkan_persentase(self, capsys):
        print_progress(50 * 1024, 100 * 1024)
        # flush menggunakan stdout.write, bukan print — cek via capsys
        # stdout.write tidak selalu ter-capture capsys; gunakan mock langsung
        with patch("helpers.downloader.sys.stdout") as mock_stdout:
            print_progress(50 * 1024, 100 * 1024)
            written = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
            assert "50.0%" in written

    def test_bar_penuh_saat_100_persen(self):
        with patch("helpers.downloader.sys.stdout") as mock_stdout:
            print_progress(100 * 1024, 100 * 1024)
            written = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
            assert "█" * 20 in written

    def test_bar_kosong_saat_0_persen(self):
        with patch("helpers.downloader.sys.stdout") as mock_stdout:
            print_progress(0, 100 * 1024)
            written = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
            assert "░" * 20 in written

    def test_flush_selalu_dipanggil(self):
        with patch("helpers.downloader.sys.stdout") as mock_stdout:
            print_progress(50 * 1024, 100 * 1024)
            mock_stdout.flush.assert_called()


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------

class TestDownload:
    def _make_mock_response(self, content: bytes, content_length: int | None = None):
        mock = MagicMock()
        mock.headers = {"content-length": str(content_length or len(content))}
        mock.raise_for_status = MagicMock()
        # iter_content menghasilkan chunks
        mock.iter_content.return_value = [content[i:i+65536] for i in range(0, len(content), 65536)]
        return mock

    def test_download_file_tersimpan(self, setup_yui_env):
        content = b"fake appimage binary content"
        mock_response = self._make_mock_response(content)
        app_path = str(setup_yui_env["appimage_dir"] / "App.AppImage")

        with patch("helpers.downloader.requests.get", return_value=mock_response):
            download("https://github.com/owner/app/App.AppImage", app_path)

        assert os.path.exists(app_path)
        assert open(app_path, "rb").read() == content

    def test_raise_runtime_error_jika_request_gagal(self, setup_yui_env):
        app_path = str(setup_yui_env["appimage_dir"] / "App.AppImage")

        with patch(
            "helpers.downloader.requests.get",
            side_effect=requests.exceptions.ConnectionError("timeout"),
        ):
            with pytest.raises(RuntimeError, match="Download failed"):
                download("https://github.com/owner/app/App.AppImage", app_path)

    def test_hapus_file_parsial_jika_gagal_saat_menulis(self, setup_yui_env):
        content = b"x" * 200_000
        mock_response = self._make_mock_response(content)
        app_path = str(setup_yui_env["appimage_dir"] / "App.AppImage")

        original_write = open

        def fail_on_write(*args, **kwargs):
            f = original_write(*args, **kwargs)
            if "wb" in args:
                raise OSError("disk full")
            return f

        with patch("helpers.downloader.requests.get", return_value=mock_response):
            with patch("builtins.open", side_effect=OSError("disk full")):
                with pytest.raises(OSError):
                    download("https://github.com/owner/app/App.AppImage", app_path)

        # File parsial tidak boleh tersisa
        assert not os.path.exists(app_path)

    def test_download_tanpa_content_length(self, setup_yui_env):
        content = b"small content"
        mock_response = self._make_mock_response(content)
        mock_response.headers = {}  # tidak ada content-length
        app_path = str(setup_yui_env["appimage_dir"] / "App.AppImage")

        with patch("helpers.downloader.requests.get", return_value=mock_response):
            download("https://github.com/owner/app/App.AppImage", app_path)

        assert os.path.exists(app_path)

    def test_buat_folder_jika_belum_ada(self, setup_yui_env, monkeypatch):
        import helpers.constant as con
        new_appimage_dir = setup_yui_env["root"] / "appimage" / "subdir"
        monkeypatch.setattr(con, "APPIMAGE_PATH", str(new_appimage_dir))

        content = b"content"
        mock_response = self._make_mock_response(content)
        app_path = str(new_appimage_dir / "App.AppImage")

        with patch("helpers.downloader.requests.get", return_value=mock_response):
            download("https://github.com/owner/app/App.AppImage", app_path)

        assert new_appimage_dir.exists()
        assert os.path.exists(app_path)

    def test_raise_jika_http_error(self, setup_yui_env):
        mock = MagicMock()
        mock.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
        app_path = str(setup_yui_env["appimage_dir"] / "App.AppImage")

        with patch("helpers.downloader.requests.get", return_value=mock):
            with pytest.raises(RuntimeError, match="Download failed"):
                download("https://github.com/owner/app/App.AppImage", app_path)
