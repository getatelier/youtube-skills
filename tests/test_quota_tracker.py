"""Tests for quota_tracker utility."""

import json
from pathlib import Path

from utils.quota_tracker import (
    DAILY_QUOTA,
    _pacific_date,
    _quota_file,
    check_quota,
    consume_quota,
    get_remaining,
    reset_quota,
)


class TestPacificDate:
    def test_returns_string(self) -> None:
        result = _pacific_date()
        assert isinstance(result, str)
        assert len(result) == 10  # YYYY-MM-DD


class TestQuotaFile:
    def test_returns_path(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        path = _quota_file()
        assert isinstance(path, Path)
        assert path.name.startswith("youtube_quota_")


class TestCheckQuota:
    def test_basic_status(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        reset_quota()
        result = check_quota()
        assert result["consumed"] == 0
        assert result["remaining"] == DAILY_QUOTA
        # can_execute only present when operation is specified
        assert "can_execute" not in result

    def test_operation_cost(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        reset_quota()
        result = check_quota("search.list")
        assert result["operation_cost"] == 100
        assert result["can_execute"] is True

    def test_quota_exceeded(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        reset_quota()
        # Artificially consume almost all quota
        data = {"date": _pacific_date(), "consumed": DAILY_QUOTA - 10, "operations": {}}
        quota_file = _quota_file()
        quota_file.parent.mkdir(parents=True, exist_ok=True)
        with open(quota_file, "w") as f:
            json.dump(data, f)
        result = check_quota("search.list")
        assert result["can_execute"] is False
        assert "error" in result

    def test_warning_threshold(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        reset_quota()
        data = {
            "date": _pacific_date(),
            "consumed": int(DAILY_QUOTA * 0.85),
            "operations": {},
        }
        quota_file = _quota_file()
        quota_file.parent.mkdir(parents=True, exist_ok=True)
        with open(quota_file, "w") as f:
            json.dump(data, f)
        result = check_quota()
        assert "warning" in result


class TestConsumeQuota:
    def test_consumes_correct_amount(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        reset_quota()
        result = consume_quota("videos.list", 5)
        assert result["units_consumed"] == 5
        assert result["remaining"] == DAILY_QUOTA - 5

    def test_unknown_operation(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        reset_quota()
        result = consume_quota("unknown.operation")
        assert "warning" in result

    def test_exceeds_quota(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        reset_quota()
        data = {
            "date": _pacific_date(),
            "consumed": DAILY_QUOTA - 5,
            "operations": {},
        }
        quota_file = _quota_file()
        quota_file.parent.mkdir(parents=True, exist_ok=True)
        with open(quota_file, "w") as f:
            json.dump(data, f)
        result = consume_quota("search.list")
        assert "error" in result


class TestGetRemaining:
    def test_returns_int(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        reset_quota()
        assert get_remaining() == DAILY_QUOTA


class TestResetQuota:
    def test_resets_to_zero(self, monkeypatch, tmp_path) -> None:
        fake_tmp = tmp_path / ".tmp"
        monkeypatch.setattr("utils.quota_tracker.TMP_DIR", fake_tmp)
        consume_quota("videos.list", 10)
        result = reset_quota()
        assert result["remaining"] == DAILY_QUOTA
