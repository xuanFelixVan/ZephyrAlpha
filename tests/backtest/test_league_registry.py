# [BLUEPRINT] MOD-AUTO-L11-REGISTRY | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 测试
# [MODULE] tests.backtest.test_league_registry
# [DOMAIN] D_BACKTEST
# [INVARIANTS] 零 CH/网络触碰; 全部 IO 走 tmp_path fixture（宪法测试隔离铁律，禁写生产路径）
# [TTL] permanent
"""league_registry 测试——schema 校验/add_months/schedule_review CAS 挂单。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "backtest") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "backtest"))

import league_registry as lr  # noqa: E402


def _valid_registry() -> dict:
    return {
        "schema_version": "0.1.0",
        "title": "A/B 联赛注册表（测试）",
        "review_policy": {"window_months": 6, "judge": "scripts/backtest/promotion_combo_gate.py"},
        "groups": [
            {
                "group_id": "A",
                "status": "champion",
                "joined_date": "2026-09-21",
                "members": [],
                "archive_path": "",
                "review_window": {
                    "start": "2026-09-21",
                    "months": 6,
                    "due": "2027-03-21",
                    "review_scheduled": False,
                    "scheduled_at": None,
                    "note": "",
                },
            },
            {
                "group_id": "B",
                "status": "challenger",
                "joined_date": "2026-09-21",
                "members": ["S-TEST-001"],
                "review_window": {"start": "2026-09-21", "due": "2027-03-21"},
            },
        ],
    }


class TestValidateRegistry:
    def test_valid_registry_passes(self):
        assert lr.validate_registry(_valid_registry()) == []

    def test_missing_schema_version_flags(self):
        data = _valid_registry()
        del data["schema_version"]
        assert any("schema_version" in e for e in lr.validate_registry(data))

    def test_bad_status_flags(self):
        data = _valid_registry()
        data["groups"][0]["status"] = "winner"  # 非法状态
        assert any("status 非法" in e for e in lr.validate_registry(data))

    def test_duplicate_group_id_flags(self):
        data = _valid_registry()
        data["groups"].append(dict(data["groups"][0]))
        assert any("重复" in e for e in lr.validate_registry(data))

    def test_empty_groups_flags(self):
        data = _valid_registry()
        data["groups"] = []
        assert any("groups" in e for e in lr.validate_registry(data))

    def test_missing_review_window_flags(self):
        data = _valid_registry()
        del data["groups"][1]["review_window"]
        assert any("review_window" in e for e in lr.validate_registry(data))

    def test_members_non_list_flags(self):
        data = _valid_registry()
        data["groups"][1]["members"] = "S-TEST-001"  # 须列表
        assert any("members" in e for e in lr.validate_registry(data))


class TestGetGroup:
    def test_found_and_missing(self):
        data = _valid_registry()
        assert lr.get_group(data, "B")["status"] == "challenger"
        with pytest.raises(KeyError):
            lr.get_group(data, "Z")


class TestAddMonths:
    def test_plain_six_months(self):
        assert lr.add_months("2026-09-21", 6) == "2027-03-21"

    def test_year_rollover(self):
        assert lr.add_months("2026-11-15", 6) == "2027-05-15"

    def test_month_end_clamp(self):
        assert lr.add_months("2026-01-31", 1) == "2026-02-28"
        assert lr.add_months("2026-03-31", 1) == "2026-04-30"

    def test_leap_day_clamp(self):
        assert lr.add_months("2024-02-29", 1) == "2024-03-29"

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            lr.add_months("not-a-date", 6)


class TestScheduleReview:
    def _write_registry(self, tmp_path: Path) -> Path:
        p = tmp_path / "league_registry.yaml"
        p.write_text(yaml.safe_dump(_valid_registry(), allow_unicode=True, sort_keys=False), encoding="utf-8")
        return p

    def test_schedule_review_writes_fields(self, tmp_path):
        p = self._write_registry(tmp_path)
        updated = lr.schedule_review("A", note="满窗挂单", path=p, scheduled_at="2026-09-21T00:00:00+00:00")
        rw = updated["review_window"]
        assert rw["review_scheduled"] is True
        assert rw["scheduled_at"] == "2026-09-21T00:00:00+00:00"
        assert rw["note"] == "满窗挂单"
        # 回读核实：落盘内容与返回一致（CAS 写后核实）
        on_disk = lr.get_group(yaml.safe_load(p.read_text(encoding="utf-8")), "A")
        assert on_disk["review_window"]["review_scheduled"] is True

    def test_schedule_review_other_group_untouched(self, tmp_path):
        p = self._write_registry(tmp_path)
        lr.schedule_review("A", path=p)
        on_disk = lr.get_group(yaml.safe_load(p.read_text(encoding="utf-8")), "B")
        assert on_disk["review_window"].get("review_scheduled") in (False, None)

    def test_schedule_review_missing_group_raises(self, tmp_path):
        p = self._write_registry(tmp_path)
        with pytest.raises(KeyError):
            lr.schedule_review("Z", path=p)

    def test_load_registry_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            lr.load_registry(tmp_path / "nope.yaml")
