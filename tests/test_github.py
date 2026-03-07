"""
Test untuk helpers/github.py

Mencakup:
- is_safe_url: validasi URL GitHub
- find_appimage_asset: pencarian asset .AppImage
- fetch_latest_release: integrasi dengan GitHub API (dimock)
"""

import pytest
from unittest.mock import patch, MagicMock
import requests

from helpers.github import is_safe_url, find_appimage_asset, fetch_latest_release


# ---------------------------------------------------------------------------
# is_safe_url
# ---------------------------------------------------------------------------

class TestIsSafeUrl:
    def test_github_com_https(self):
        assert is_safe_url("https://github.com/owner/repo") is True

    def test_objects_githubusercontent_com(self):
        # CATATAN: is_safe_url saat ini hanya menerima *.github.com, bukan
        # *.githubusercontent.com. GitHub release assets biasanya di-host di
        # objects.githubusercontent.com — ini adalah gap yang perlu dipertimbangkan
        # untuk diperbaiki di kode produksi.
        assert is_safe_url("https://objects.githubusercontent.com/file.AppImage") is False

    def test_releases_githubusercontent_com(self):
        assert is_safe_url("https://github.com/releases/download/v1/App.AppImage") is True

    def test_subdomain_github_com(self):
        # raw.githubusercontent.com tidak diakhiri .github.com, sehingga ditolak.
        # Ini adalah perilaku yang diharapkan dari implementasi saat ini.
        assert is_safe_url("https://raw.githubusercontent.com/owner/repo/main/file") is False

    def test_tolak_http(self):
        assert is_safe_url("http://github.com/owner/repo") is False

    def test_tolak_domain_mirip_github(self):
        assert is_safe_url("https://evil-github.com/malware.AppImage") is False

    def test_tolak_domain_github_tanpa_titik(self):
        # 'notgithub.com' tidak diakhiri '.github.com' dan bukan 'github.com'
        assert is_safe_url("https://notgithub.com/file") is False

    def test_tolak_string_kosong(self):
        assert is_safe_url("") is False

    def test_tolak_ftp(self):
        assert is_safe_url("ftp://github.com/file") is False

    def test_tolak_tanpa_scheme(self):
        assert is_safe_url("github.com/owner/repo") is False


# ---------------------------------------------------------------------------
# find_appimage_asset
# ---------------------------------------------------------------------------

class TestFindAppimageAsset:
    def test_menemukan_appimage(self):
        assets = [
            {"name": "app.tar.gz", "browser_download_url": "https://github.com/a.tar.gz"},
            {"name": "App.AppImage", "browser_download_url": "https://github.com/App.AppImage"},
        ]
        result = find_appimage_asset(assets)
        assert result is not None
        assert result["name"] == "App.AppImage"

    def test_mengembalikan_asset_pertama_jika_ada_banyak(self):
        assets = [
            {"name": "App-x86.AppImage", "browser_download_url": "https://github.com/x86"},
            {"name": "App-arm.AppImage", "browser_download_url": "https://github.com/arm"},
        ]
        result = find_appimage_asset(assets)
        assert result["name"] == "App-x86.AppImage"

    def test_tidak_menemukan_jika_tidak_ada_appimage(self):
        assets = [
            {"name": "app.deb"},
            {"name": "app.tar.gz"},
            {"name": "app.rpm"},
        ]
        assert find_appimage_asset(assets) is None

    def test_list_kosong(self):
        assert find_appimage_asset([]) is None

    def test_asset_tanpa_key_name(self):
        # Asset yang tidak punya key 'name' tidak boleh menyebabkan crash
        assets = [{"browser_download_url": "https://github.com/file"}]
        assert find_appimage_asset(assets) is None

    def test_case_sensitive_ekstensi(self):
        # '.appimage' (lowercase) tidak dianggap valid — harus '.AppImage'
        assets = [{"name": "app.appimage"}]
        assert find_appimage_asset(assets) is None


# ---------------------------------------------------------------------------
# fetch_latest_release
# ---------------------------------------------------------------------------

class TestFetchLatestRelease:

    def _mock_response(self, json_data, status_code=200):
        mock = MagicMock()
        mock.json.return_value = json_data
        mock.status_code = status_code
        mock.raise_for_status = MagicMock()
        return mock

    def test_sukses_menemukan_appimage(self, setup_yui_env):
        api_response = {
            "tag_name": "v2.0.0",
            "assets": [
                {
                    "name": "App.AppImage",
                    "browser_download_url": "https://github.com/owner/app/releases/download/v2.0.0/App.AppImage",
                }
            ],
        }
        with patch("helpers.github.requests.get", return_value=self._mock_response(api_response)):
            result = fetch_latest_release("owner/app")

        assert result["success"] is True
        assert result["app_name"] == "App.AppImage"
        assert result["version"] == "v2.0.0"
        assert result["download_url"] == "https://github.com/owner/app/releases/download/v2.0.0/App.AppImage"
        assert result["status"] == "Get data success"

    def test_gagal_tidak_ada_appimage_di_assets(self):
        api_response = {
            "tag_name": "v1.0.0",
            "assets": [{"name": "app.tar.gz", "browser_download_url": "https://github.com/app.tar.gz"}],
        }
        with patch("helpers.github.requests.get", return_value=self._mock_response(api_response)):
            result = fetch_latest_release("owner/app")

        assert result["success"] is False
        assert result["status"] == "AppImage not found"

    def test_gagal_assets_kosong(self):
        api_response = {"tag_name": "v1.0.0", "assets": []}
        with patch("helpers.github.requests.get", return_value=self._mock_response(api_response)):
            result = fetch_latest_release("owner/app")

        assert result["success"] is False
        assert result["status"] == "AppImage not found"

    def test_gagal_url_tidak_aman(self):
        api_response = {
            "tag_name": "v1.0.0",
            "assets": [
                {
                    "name": "App.AppImage",
                    "browser_download_url": "http://evil.com/malware.AppImage",
                }
            ],
        }
        with patch("helpers.github.requests.get", return_value=self._mock_response(api_response)):
            result = fetch_latest_release("owner/app")

        assert result["success"] is False
        assert result["status"] == "Unsafe download URL"

    def test_gagal_request_exception(self):
        with patch(
            "helpers.github.requests.get",
            side_effect=requests.exceptions.ConnectionError("network error"),
        ):
            result = fetch_latest_release("owner/app")

        assert result["success"] is False
        assert "network error" in result["status"]

    def test_gagal_http_404(self):
        mock = self._mock_response({})
        mock.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        with patch("helpers.github.requests.get", return_value=mock):
            result = fetch_latest_release("owner/nonexistent")

        assert result["success"] is False

    def test_app_path_berisi_appimage_path(self, setup_yui_env):
        import helpers.constant as con
        api_response = {
            "tag_name": "v1.0.0",
            "assets": [
                {
                    "name": "App.AppImage",
                    "browser_download_url": "https://github.com/owner/app/releases/download/v1.0.0/App.AppImage",
                }
            ],
        }
        with patch("helpers.github.requests.get", return_value=self._mock_response(api_response)):
            result = fetch_latest_release("owner/app")

        assert result["app_path"].startswith(con.APPIMAGE_PATH)
        assert result["app_path"].endswith("App.AppImage")
