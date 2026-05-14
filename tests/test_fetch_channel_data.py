"""Tests for fetch_channel_data.py."""

import json
from unittest.mock import MagicMock, patch

import pytest
from fetch_channel_data import (
    fetch_channel_info,
    fetch_recent_videos,
    parse_channel_input,
    resolve_channel_id,
)


class TestParseChannelInput:
    def test_direct_channel_id(self) -> None:
        # Channel IDs are exactly 24 characters (UC + 22 chars)
        result = parse_channel_input("UCxxxxxxxxxxxxxxxxxxxxxx")
        assert result == {"type": "id", "value": "UCxxxxxxxxxxxxxxxxxxxxxx"}

    def test_handle(self) -> None:
        result = parse_channel_input("@testhandle")
        assert result == {"type": "handle", "value": "@testhandle"}

    def test_url_channel_id(self) -> None:
        result = parse_channel_input("https://youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxxxx")
        assert result["type"] == "id"

    def test_url_handle(self) -> None:
        result = parse_channel_input("https://youtube.com/@testhandle")
        assert result == {"type": "handle", "value": "@testhandle"}

    def test_custom_url(self) -> None:
        result = parse_channel_input("https://youtube.com/c/customname")
        assert result == {"type": "custom_url", "value": "customname"}

    def test_username_url(self) -> None:
        result = parse_channel_input("https://youtube.com/user/username")
        assert result == {"type": "username", "value": "username"}

    def test_bare_handle(self) -> None:
        result = parse_channel_input("testhandle")
        assert result == {"type": "handle", "value": "@testhandle"}

    def test_unknown_url(self) -> None:
        result = parse_channel_input("https://unknown.com/xyz")
        assert result["type"] == "unknown"


class TestResolveChannelId:
    def test_direct_id(self) -> None:
        service = MagicMock()
        parsed = {"type": "id", "value": "UC123"}
        assert resolve_channel_id(service, parsed) == "UC123"
        service.channels.assert_not_called()

    def test_handle(self) -> None:
        service = MagicMock()
        service.channels.return_value.list.return_value.execute.return_value = {
            "items": [{"id": "UC456"}]
        }
        parsed = {"type": "handle", "value": "@test"}
        assert resolve_channel_id(service, parsed) == "UC456"
        service.channels.return_value.list.assert_called_once_with(part="id", forHandle="test")

    def test_handle_not_found(self) -> None:
        service = MagicMock()
        service.channels.return_value.list.return_value.execute.return_value = {"items": []}
        parsed = {"type": "handle", "value": "@unknown"}
        assert resolve_channel_id(service, parsed) is None

    def test_custom_url(self) -> None:
        service = MagicMock()
        service.search.return_value.list.return_value.execute.return_value = {
            "items": [{"id": {"channelId": "UC789"}}]
        }
        parsed = {"type": "custom_url", "value": "custom"}
        assert resolve_channel_id(service, parsed) == "UC789"


class TestFetchChannelInfo:
    def test_success(self) -> None:
        service = MagicMock()
        service.channels.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "UC123",
                    "snippet": {
                        "title": "Test Channel",
                        "description": "A test channel",
                        "customUrl": "@test",
                        "publishedAt": "2020-01-01",
                        "country": "US",
                    },
                    "statistics": {
                        "subscriberCount": "1000",
                        "viewCount": "50000",
                        "videoCount": "50",
                    },
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
                    "brandingSettings": {"channel": {"keywords": "test, channel"}},
                }
            ]
        }
        info = fetch_channel_info(service, "UC123")
        assert info is not None
        assert info["title"] == "Test Channel"
        assert info["subscriber_count"] == 1000
        assert info["uploads_playlist"] == "UU123"

    def test_not_found(self) -> None:
        service = MagicMock()
        service.channels.return_value.list.return_value.execute.return_value = {"items": []}
        assert fetch_channel_info(service, "UCmissing") is None


class TestFetchRecentVideos:
    def test_success(self) -> None:
        service = MagicMock()
        # First call: playlist items
        service.playlistItems.return_value.list.return_value.execute.return_value = {
            "items": [
                {"contentDetails": {"videoId": "vid1"}},
                {"contentDetails": {"videoId": "vid2"}},
            ]
        }
        # Second call: video details
        service.videos.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "vid1",
                    "snippet": {"title": "Video 1", "publishedAt": "2024-01-01"},
                    "statistics": {"viewCount": "100", "likeCount": "10", "commentCount": "5"},
                    "contentDetails": {"duration": "PT10M"},
                },
                {
                    "id": "vid2",
                    "snippet": {"title": "Video 2", "publishedAt": "2024-01-02"},
                    "statistics": {"viewCount": "200", "likeCount": "20", "commentCount": "10"},
                    "contentDetails": {"duration": "PT5M"},
                },
            ]
        }
        videos = fetch_recent_videos(service, "UU123", max_results=2)
        assert len(videos) == 2
        assert videos[0]["video_id"] == "vid1"
        assert videos[0]["views"] == 100

    def test_empty_playlist(self) -> None:
        service = MagicMock()
        service.playlistItems.return_value.list.return_value.execute.return_value = {"items": []}
        videos = fetch_recent_videos(service, "UUempty")
        assert videos == []


class TestMain:
    @patch("fetch_channel_data.get_data_api_service")
    @patch("fetch_channel_data.check_quota")
    @patch("fetch_channel_data.consume_quota")
    def test_main_success(
        self, mock_consume, mock_check, _mock_get_service, monkeypatch, tmp_path, capsys
    ) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("fetch_channel_data.TMP_DIR", fake_tmp)

        mock_check.return_value = {"can_execute": True}
        mock_consume.return_value = {"remaining": 9999}

        service = MagicMock()
        service.channels.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "UC123",
                    "snippet": {
                        "title": "Test",
                        "description": "Desc",
                        "customUrl": "@test",
                        "publishedAt": "2020-01-01",
                    },
                    "statistics": {
                        "subscriberCount": "100",
                        "viewCount": "1000",
                        "videoCount": "10",
                    },
                    "contentDetails": {"relatedPlaylists": {"uploads": "UU123"}},
                    "brandingSettings": {"channel": {"keywords": ""}},
                }
            ]
        }
        service.playlistItems.return_value.list.return_value.execute.return_value = {"items": []}
        _mock_get_service.return_value = (service, None)

        import sys

        from fetch_channel_data import main

        old_argv = sys.argv
        try:
            sys.argv = ["fetch_channel_data.py", "UC123"]
            main()
        finally:
            sys.argv = old_argv

        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["channel"]["title"] == "Test"
        assert result["videos"] == []

    @patch("fetch_channel_data.get_data_api_service")
    @patch("fetch_channel_data.check_quota")
    def test_main_quota_exceeded(self, mock_check, _mock_get_service, capsys) -> None:
        mock_check.return_value = {"can_execute": False, "error": "Quota exceeded"}

        import sys

        from fetch_channel_data import main

        old_argv = sys.argv
        try:
            sys.argv = ["fetch_channel_data.py", "UC123"]
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
        finally:
            sys.argv = old_argv

        captured = capsys.readouterr()
        result = json.loads(captured.err)
        assert "error" in result
