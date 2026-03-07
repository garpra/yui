"""
Test untuk helpers/repository.py

Mencakup:
- read_repository: baca repos.json
- update_repository: tulis data app baru / update
- remove_repository: hapus data app
- get_list_app: ambil list app terinstall
"""

import json
import pytest
from helpers.repository import (
    read_repository,
    update_repository,
    remove_repository,
    get_list_app,
)
from helpers.models import AppRecord

pytestmark = pytest.mark.usefixtures("setup_yui_env")


def make_record(version="v1.0.0") -> AppRecord:
    return AppRecord(
        app_name="App.AppImage",
        app_path="/tmp/appimage/App.AppImage",
        version=version,
        download_url="https://github.com/owner/app/releases/download/v1.0.0/App.AppImage",
        desktop_path="/tmp/applications/app.desktop",
        icon_path="/tmp/icons/yui/app.png",
    )


# ---------------------------------------------------------------------------
# read_repository
# ---------------------------------------------------------------------------

class TestReadRepository:
    def test_kembalikan_dict_kosong_jika_file_tidak_ada(self):
        result = read_repository()
        assert result == {}

    def test_baca_file_yang_ada(self, setup_yui_env):
        repo_path = setup_yui_env["repo_path"]
        data = {"owner/app": {"app_name": "App.AppImage", "version": "v1.0.0"}}
        repo_path.write_text(json.dumps(data))

        result = read_repository()
        assert result == data

    def test_baca_file_kosong_valid_json(self, setup_yui_env):
        setup_yui_env["repo_path"].write_text("{}")
        assert read_repository() == {}


# ---------------------------------------------------------------------------
# update_repository
# ---------------------------------------------------------------------------

class TestUpdateRepository:
    def test_simpan_record_baru(self, setup_yui_env):
        record = make_record()
        update_repository("owner/app", record)

        data = json.loads(setup_yui_env["repo_path"].read_text())
        assert "owner/app" in data
        assert data["owner/app"]["version"] == "v1.0.0"
        assert data["owner/app"]["app_name"] == "App.AppImage"

    def test_update_record_yang_sudah_ada(self, setup_yui_env):
        update_repository("owner/app", make_record("v1.0.0"))
        update_repository("owner/app", make_record("v2.0.0"))

        data = json.loads(setup_yui_env["repo_path"].read_text())
        assert data["owner/app"]["version"] == "v2.0.0"

    def test_simpan_multiple_record(self, setup_yui_env):
        record_a = make_record()
        record_b = AppRecord(
            app_name="OtherApp.AppImage",
            app_path="/tmp/appimage/OtherApp.AppImage",
            version="v3.0.0",
            download_url="https://github.com/owner/other/releases/download/v3.0.0/OtherApp.AppImage",
            desktop_path="/tmp/applications/otherapp.desktop",
            icon_path="/tmp/icons/yui/otherapp.png",
        )
        update_repository("owner/app", record_a)
        update_repository("owner/other", record_b)

        data = json.loads(setup_yui_env["repo_path"].read_text())
        assert "owner/app" in data
        assert "owner/other" in data

    def test_semua_field_tersimpan(self, setup_yui_env):
        record = make_record()
        update_repository("owner/app", record)

        data = json.loads(setup_yui_env["repo_path"].read_text())
        saved = data["owner/app"]
        assert saved["app_name"] == record.app_name
        assert saved["app_path"] == record.app_path
        assert saved["version"] == record.version
        assert saved["download_url"] == record.download_url
        assert saved["desktop_path"] == record.desktop_path
        assert saved["icon_path"] == record.icon_path


# ---------------------------------------------------------------------------
# remove_repository
# ---------------------------------------------------------------------------

class TestRemoveRepository:
    def test_hapus_app_yang_ada(self, setup_yui_env):
        update_repository("owner/app", make_record())
        remove_repository("owner/app")

        data = json.loads(setup_yui_env["repo_path"].read_text())
        assert "owner/app" not in data

    def test_hapus_app_yang_tidak_ada_tidak_error(self):
        # Tidak boleh raise exception
        remove_repository("owner/tidak-ada")

    def test_hapus_hanya_app_yang_ditentukan(self, setup_yui_env):
        update_repository("owner/app-a", make_record())
        update_repository("owner/app-b", make_record())
        remove_repository("owner/app-a")

        data = json.loads(setup_yui_env["repo_path"].read_text())
        assert "owner/app-a" not in data
        assert "owner/app-b" in data


# ---------------------------------------------------------------------------
# get_list_app
# ---------------------------------------------------------------------------

class TestGetListApp:
    def test_kosong_jika_belum_ada_app(self):
        assert get_list_app() == []

    def test_mengembalikan_list_app_url(self, setup_yui_env):
        update_repository("owner/app-a", make_record())
        update_repository("owner/app-b", make_record())

        result = get_list_app()
        assert "owner/app-a" in result
        assert "owner/app-b" in result
        assert len(result) == 2

    def test_mengembalikan_list_string(self, setup_yui_env):
        update_repository("owner/app", make_record())
        result = get_list_app()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_setelah_hapus_tidak_muncul_lagi(self, setup_yui_env):
        update_repository("owner/app", make_record())
        remove_repository("owner/app")
        assert get_list_app() == []
