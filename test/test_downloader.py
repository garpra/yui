import pytest
import sys
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from helpers import downloader


class TestPrintProgress:
    def test_with_unknown_total_size(self, capsys):
        downloader.print_progress(2048, 0)
        captured = capsys.readouterr()
        assert "Downloading..." in captured.out
        assert "2.0 KB" in captured.out

    def test_progress_zero_percent(self, capsys):
        downloader.print_progress(0, 1024)
        captured = capsys.readouterr()
        assert "0.0%" in captured.out

    def test_progress_fifty_percent(self, capsys):
        downloader.print_progress(512, 1024)
        captured = capsys.readouterr()
        assert "50.0%" in captured.out

    def test_progress_full(self, capsys):
        downloader.print_progress(1024, 1024)
        captured = capsys.readouterr()
        assert "100.0%" in captured.out

    def test_progress_bar_filled(self, capsys):
        downloader.print_progress(512, 1024)
        captured = capsys.readouterr()
        assert "█" in captured.out
        assert "░" in captured.out


class TestDownload:
    @patch("helpers.downloader.os.makedirs")
    @patch("helpers.downloader.requests.get")
    @patch("helpers.downloader.open", new_callable=mock_open)
    def test_download_success(self, mock_file, mock_get, mock_makedirs):
        mock_response = MagicMock()
        mock_response.headers = {"content-length": "1024"}
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        downloader.download("https://example.com/file.AppImage", "/tmp/test.AppImage")

        mock_get.assert_called_once()
        mock_file.assert_called_once_with("/tmp/test.AppImage", "wb")

    @patch("helpers.downloader.os.makedirs")
    @patch("helpers.downloader.requests.get")
    def test_download_network_error(self, mock_get, mock_makedirs):
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError("Failed")

        with pytest.raises(RuntimeError, match="Download failed"):
            downloader.download("https://example.com/file.AppImage", "/tmp/test.AppImage")