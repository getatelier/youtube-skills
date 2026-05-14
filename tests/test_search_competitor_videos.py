"""Tests for search_competitor_videos.py."""

from unittest.mock import MagicMock

from search_competitor_videos import flag_outliers, search_videos


class TestSearchVideos:
    def test_basic_search(self) -> None:
        service = MagicMock()
        service.search.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": {"videoId": "vid1"},
                    "snippet": {
                        "title": "Video 1",
                        "channelTitle": "Channel A",
                        "channelId": "UCA",
                        "publishedAt": "2024-01-01",
                        "description": "Desc 1",
                        "thumbnails": {"high": {"url": "http://thumb1"}},
                    },
                },
                {
                    "id": {"videoId": "vid2"},
                    "snippet": {
                        "title": "Video 2",
                        "channelTitle": "Channel B",
                        "channelId": "UCB",
                        "publishedAt": "2024-01-02",
                        "description": "Desc 2",
                        "thumbnails": {"high": {"url": "http://thumb2"}},
                    },
                },
            ]
        }
        service.videos.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "vid1",
                    "statistics": {"viewCount": "1000", "likeCount": "100", "commentCount": "10"},
                    "contentDetails": {"duration": "PT10M"},
                },
                {
                    "id": "vid2",
                    "statistics": {"viewCount": "5000", "likeCount": "500", "commentCount": "50"},
                    "contentDetails": {"duration": "PT5M"},
                },
            ]
        }

        results = search_videos(service, "test query")
        assert len(results) == 2
        assert results[0]["video_id"] == "vid1"
        assert results[0]["views"] == 1000
        assert results[1]["views"] == 5000
        assert "engagement_rate_pct" in results[0]

    def test_channel_filter(self) -> None:
        service = MagicMock()
        service.search.return_value.list.return_value.execute.return_value = {"items": []}
        service.videos.return_value.list.return_value.execute.return_value = {"items": []}

        search_videos(service, "query", channel_id="UC123")
        service.search.return_value.list.assert_called_once()
        call_kwargs = service.search.return_value.list.call_args.kwargs
        assert call_kwargs["channelId"] == "UC123"

    def test_empty_results(self) -> None:
        service = MagicMock()
        service.search.return_value.list.return_value.execute.return_value = {"items": []}
        results = search_videos(service, "unlikely query xyz")
        assert results == []


class TestFlagOutliers:
    def test_flags_outliers(self) -> None:
        videos = [
            {"video_id": "v1", "channel_id": "UCA", "views": 100},
            {"video_id": "v2", "channel_id": "UCA", "views": 110},
            {"video_id": "v3", "channel_id": "UCA", "views": 120},
            {"video_id": "v4", "channel_id": "UCA", "views": 1000},
        ]
        flagged = flag_outliers(videos, multiplier=3.0)
        outlier = next(v for v in flagged if v["video_id"] == "v4")
        assert outlier["is_outlier"] is True
        assert outlier["vs_channel_avg"] >= 3.0

    def test_no_outliers_small_channel(self) -> None:
        videos = [
            {"video_id": "v1", "channel_id": "UCA", "views": 100},
            {"video_id": "v2", "channel_id": "UCA", "views": 200},
        ]
        flagged = flag_outliers(videos)
        # Less than 3 videos per channel, no outlier analysis
        assert all("is_outlier" not in v for v in flagged)

    def test_empty_list(self) -> None:
        assert flag_outliers([]) == []

    def test_single_video(self) -> None:
        videos = [{"video_id": "v1", "channel_id": "UCA", "views": 100}]
        flagged = flag_outliers(videos)
        assert flagged == videos
