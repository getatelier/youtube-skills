"""Tests for fetch_transcript parser functions."""

from fetch_transcript import parse_srt, parse_video_id, parse_vtt, segments_to_text


class TestParseVideoId:
    def test_direct_id(self) -> None:
        assert parse_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_youtube_url(self) -> None:
        assert parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self) -> None:
        assert parse_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_shorts_url(self) -> None:
        assert parse_video_id("https://youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


class TestParseVtt:
    def test_basic_vtt(self) -> None:
        content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Hello world

00:00:05.000 --> 00:00:08.000
This is a test
"""
        segments = parse_vtt(content)
        assert len(segments) == 2
        assert segments[0]["text"] == "Hello world"
        assert segments[0]["start"] == "00:00:01.000"

    def test_vtt_with_tags(self) -> None:
        content = """WEBVTT

00:00:01.000 --> 00:00:05.000
<c>Hello</c> world
"""
        segments = parse_vtt(content)
        assert segments[0]["text"] == "Hello world"

    def test_dedupes_consecutive_identical(self) -> None:
        content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Same text

00:00:05.000 --> 00:00:08.000
Same text
"""
        segments = parse_vtt(content)
        assert len(segments) == 1


class TestParseSrt:
    def test_basic_srt(self) -> None:
        content = """1
00:00:01,000 --> 00:00:05,000
Hello world

2
00:00:05,000 --> 00:00:08,000
This is a test
"""
        segments = parse_srt(content)
        assert len(segments) == 2
        assert segments[0]["text"] == "Hello world"

    def test_srt_with_tags(self) -> None:
        content = """1
00:00:01,000 --> 00:00:05,000
<b>Hello</b> world
"""
        segments = parse_srt(content)
        assert segments[0]["text"] == "Hello world"


class TestSegmentsToText:
    def test_joins_text(self) -> None:
        segments = [
            {"start": "00:00:01", "text": "Hello"},
            {"start": "00:00:05", "text": "world"},
        ]
        assert segments_to_text(segments) == "Hello world"
