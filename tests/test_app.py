"""
Test untuk app.py

Mencakup:
- repo_type: validasi format input owner/repo
- main: routing argparse ke subcommand yang benar
"""

import argparse
import pytest
from unittest.mock import patch, MagicMock

from app import repo_type, main


# ---------------------------------------------------------------------------
# repo_type
# ---------------------------------------------------------------------------

class TestRepoType:
    def test_format_valid(self):
        assert repo_type("owner/repo") == "owner/repo"

    def test_format_valid_dengan_titik(self):
        assert repo_type("my.org/my-repo") == "my.org/my-repo"

    def test_format_valid_dengan_underscore(self):
        assert repo_type("owner_name/repo_name") == "owner_name/repo_name"

    def test_format_valid_dengan_angka(self):
        assert repo_type("owner123/repo456") == "owner123/repo456"

    def test_format_valid_kombinasi_karakter(self):
        assert repo_type("My.Owner-1/My_Repo.2") == "My.Owner-1/My_Repo.2"

    def test_format_tidak_valid_tanpa_slash(self):
        with pytest.raises(argparse.ArgumentTypeError):
            repo_type("ownerrepo")

    def test_format_tidak_valid_dua_slash(self):
        with pytest.raises(argparse.ArgumentTypeError):
            repo_type("owner/repo/extra")

    def test_format_tidak_valid_string_kosong(self):
        with pytest.raises(argparse.ArgumentTypeError):
            repo_type("")

    def test_format_tidak_valid_spasi(self):
        with pytest.raises(argparse.ArgumentTypeError):
            repo_type("owner name/repo")

    def test_format_tidak_valid_karakter_khusus(self):
        with pytest.raises(argparse.ArgumentTypeError):
            repo_type("owner@/repo!")

    def test_pesan_error_menyebut_input(self):
        try:
            repo_type("invalid input")
        except argparse.ArgumentTypeError as e:
            assert "invalid input" in str(e)


# ---------------------------------------------------------------------------
# main — routing subcommand
# ---------------------------------------------------------------------------

class TestMain:
    def test_install_memanggil_install_app(self):
        with patch("app.install_app") as mock_install:
            with patch("sys.argv", ["yui", "install", "owner/app"]):
                main()
            mock_install.assert_called_once()

    def test_list_memanggil_list_app(self):
        with patch("app.list_app") as mock_list:
            with patch("sys.argv", ["yui", "list"]):
                main()
            mock_list.assert_called_once()

    def test_update_memanggil_update_app(self):
        with patch("app.update_app") as mock_update:
            with patch("sys.argv", ["yui", "update"]):
                main()
            mock_update.assert_called_once()

    def test_delete_memanggil_delete_app(self):
        with patch("app.delete_app") as mock_delete:
            with patch("sys.argv", ["yui", "delete", "owner/app"]):
                main()
            mock_delete.assert_called_once()

    def test_tanpa_subcommand_tampilkan_help(self, capsys):
        with patch("sys.argv", ["yui"]):
            main()
        # argparse print_help menulis ke stdout
        captured = capsys.readouterr()
        assert "yui" in captured.out

    def test_install_meneruskan_args_dengan_app_url(self):
        captured_args = {}

        def fake_install(args):
            captured_args["app_url"] = args.app_url

        with patch("app.install_app", side_effect=fake_install):
            with patch("sys.argv", ["yui", "install", "owner/myapp"]):
                main()

        assert captured_args["app_url"] == "owner/myapp"

    def test_delete_meneruskan_args_dengan_app_url(self):
        captured_args = {}

        def fake_delete(args):
            captured_args["app_url"] = args.app_url

        with patch("app.delete_app", side_effect=fake_delete):
            with patch("sys.argv", ["yui", "delete", "owner/myapp"]):
                main()

        assert captured_args["app_url"] == "owner/myapp"

    def test_install_validasi_format_app_url(self):
        with patch("sys.argv", ["yui", "install", "invalid-format"]):
            with pytest.raises(SystemExit):
                main()
