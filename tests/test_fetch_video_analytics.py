"""Tests for fetch_video_analytics.py."""

from unittest.mock import MagicMock, patch

from fetch_video_analytics import (
    fetch_daily_metrics,
    fetch_traffic_sources,
    fetch_video_metrics,
    get_channel_id,
)


class TestFetchVideoMetrics:
    def test_success(self) -> None:
        service = MagicMock()
        service.reports.return_value.query.return_value.execute.return_value = {
            "columnHeaders": [
                {"name": "video"},
                {"name": "views"},
            ],
            "rows": [
                ["vid1", "100"],
                ["vid2", "200"],
            ],
        }
        result = fetch_video_metrics(
            service, "UC123", ["vid1", "vid2"], "2024-01-01", "2024-01-31", ["views"]
        )
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["video"] == "vid1"
        assert result[0]["views"] == "100"

    def test_api_error(self) -> None:
        service = MagicMock()
        service.reports.return_value.query.return_value.execute.side_effect = Exception("API Error")
        result = fetch_video_metrics(
            service, "UC123", ["vid1"], "2024-01-01", "2024-01-31", ["views"]
        )
        assert isinstance(result, dict)
        assert "error" in result


class TestFetchTrafficSources:
    def test_success(self) -> None:
        service = MagicMock()
        service.reports.return_value.query.return_value.execute.return_value = {
            "columnHeaders": [
                {"name": "insightTrafficSourceType"},
                {"name": "views"},
            ],
            "rows": [
                ["YT_SEARCH", "50"],
                ["SUGGESTED", "30"],
            ],
        }
        result = fetch_traffic_sources(service, "UC123", ["vid1"], "2024-01-01", "2024-01-31")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["insightTrafficSourceType"] == "YT_SEARCH"

    def test_api_error(self) -> None:
        service = MagicMock()
        service.reports.return_value.query.return_value.execute.side_effect = Exception("API Error")
        result = fetch_traffic_sources(service, "UC123", ["vid1"], "2024-01-01", "2024-01-31")
        assert isinstance(result, dict)
        assert "error" in result


class TestFetchDailyMetrics:
    def test_success(self) -> None:
        service = MagicMock()
        service.reports.return_value.query.return_value.execute.return_value = {
            "columnHeaders": [
                {"name": "day"},
                {"name": "views"},
            ],
            "rows": [
                ["2024-01-01", "10"],
                ["2024-01-02", "20"],
            ],
        }
        result = fetch_daily_metrics(service, "UC123", ["vid1"], "2024-01-01", "2024-01-31")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["day"] == "2024-01-01"

    def test_api_error(self) -> None:
        service = MagicMock()
        service.reports.return_value.query.return_value.execute.side_effect = Exception("API Error")
        result = fetch_daily_metrics(service, "UC123", ["vid1"], "2024-01-01", "2024-01-31")
        assert isinstance(result, dict)
        assert "error" in result


class TestGetChannelId:
    def test_success(self) -> None:
        mock_creds = MagicMock()
        with patch("googleapiclient.discovery.build") as mock_build:
            mock_service = MagicMock()
            mock_service.channels.return_value.list.return_value.execute.return_value = {
                "items": [{"id": "UC123"}]
            }
            mock_build.return_value = mock_service
            result = get_channel_id(mock_creds)
            assert result == "UC123"
            mock_build.assert_called_once_with("youtube", "v3", credentials=mock_creds)

    def test_no_items(self) -> None:
        mock_creds = MagicMock()
        with patch("googleapiclient.discovery.build") as mock_build:
            mock_service = MagicMock()
            mock_service.channels.return_value.list.return_value.execute.return_value = {
                "items": []
            }
            mock_build.return_value = mock_service
            assert get_channel_id(mock_creds) is None

    def test_exception(self) -> None:
        mock_creds = MagicMock()
        with patch("googleapiclient.discovery.build") as mock_build:
            mock_build.side_effect = Exception("Auth failed")
            assert get_channel_id(mock_creds) is None
