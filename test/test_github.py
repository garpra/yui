import pytest
from helpers import github


class TestIsSafeUrl:
    def test_safe_github_url(self):
        assert github.is_safe_url("https://github.com/owner/repo/releases") is True

    def test_safe_github_subdomain_url(self):
        assert github.is_safe_url("https://github.company.github.com/owner/repo") is True

    def test_unsafe_http_url(self):
        assert github.is_safe_url("http://github.com/owner/repo") is False

    def test_unsafe_different_domain(self):
        assert github.is_safe_url("https://gitlab.com/owner/repo") is False

    def test_unsafe_fake_github_domain(self):
        assert github.is_safe_url("https://github.fake.com/owner/repo") is False


class TestFindAppimageAsset:
    def test_finds_appimage_asset(self):
        assets = [
            {"name": "myapp-x86_64.AppImage"},
            {"name": "myapp-arm64.AppImage"},
        ]
        result = github.find_appimage_asset(assets)
        assert result == {"name": "myapp-x86_64.AppImage"}

    def test_returns_none_when_no_appimage(self):
        assets = [
            {"name": "myapp.tar.gz"},
            {"name": "myapp.zip"},
        ]
        result = github.find_appimage_asset(assets)
        assert result is None

    def test_skips_arm64_assets(self):
        assets = [
            {"name": "myapp-arm64.AppImage"},
            {"name": "other-arm64.AppImage"},
        ]
        result = github.find_appimage_asset(assets)
        assert result is None

    def test_returns_none_for_empty_assets(self):
        result = github.find_appimage_asset([])
        assert result is None

    def test_handles_missing_name_key(self):
        assets = [{"size": 123}]
        result = github.find_appimage_asset(assets)
        assert result is None