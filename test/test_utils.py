import pytest
from helpers import utils
from helpers.models import ReleaseData


class TestErrorFetchApp:
    def test_returns_failure_with_message(self):
        result = utils.error_fetch_app("Connection timeout")
        assert result["success"] is False
        assert result["status"] == "Connection timeout"
        assert result["app_name"] == ""
        assert result["app_path"] == ""
        assert result["version"] == ""
        assert result["download_url"] == ""

    def test_returns_correct_type(self):
        result = utils.error_fetch_app("Test error")
        assert isinstance(result, dict)
        assert "success" in result
        assert "status" in result