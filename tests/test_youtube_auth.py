"""Tests for youtube_auth utility."""

import json

from utils.youtube_auth import check_auth, get_api_key


class TestGetApiKey:
    def test_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("YOUTUBE_API_KEY", "test-key-123")
        assert get_api_key() == "test-key-123"

    def test_from_config_file(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        fake_claude_dir = tmp_path / ".claude"
        fake_claude_dir.mkdir()
        config_path = fake_claude_dir / "youtube-credentials.json"
        with open(config_path, "w") as f:
            json.dump({"api_key": "file-key-456"}, f)
        monkeypatch.setattr("utils.youtube_auth.Path.home", lambda: tmp_path)
        assert get_api_key() == "file-key-456"

    def test_missing(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        monkeypatch.setattr("utils.youtube_auth.Path.home", lambda: tmp_path)
        assert get_api_key() is None


class TestCheckAuth:
    def test_api_key_ok(self, monkeypatch) -> None:
        monkeypatch.setenv("YOUTUBE_API_KEY", "ABCD1234EFGH5678")
        result = check_auth("api_key")
        assert result["status"] == "ok"
        assert "ABCD" in result["key"]

    def test_api_key_missing(self, monkeypatch) -> None:
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        result = check_auth("api_key")
        assert result["status"] == "missing"

    def test_oauth_missing(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setattr("utils.youtube_auth.Path.home", lambda: tmp_path)
        result = check_auth("oauth")
        assert result["status"] == "missing"

    def test_unknown_auth_type(self) -> None:
        result = check_auth("unknown")
        assert result["status"] == "error"
