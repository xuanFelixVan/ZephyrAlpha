# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
"""manual 日历事件 CSV 校验测试（17号 §6.3）。

测试内容（tmp_path 构造 CSV，不落库）：
- 合法 CSV（含 BOM/注释行/空行/缺省 data_source 补 manual/列序乱序）
- 列头缺失/未知列/无列头
- event_date 非法格式/超范围；event_type 非白名单（internal 派生类拒绝）
- description 空/超长；列数不齐；同键重复；data_source 显式非 manual
- 文件不存在

设计文档：17_special_trading_days_data_assets.md §6.3；schema 真源 config/manual_calendar_events_schema.yaml
"""

from __future__ import annotations

from zephyr.data.manual_calendar_events import validate_manual_events_csv

_VALID_HEADER = "event_date,event_type,description\n"
_VALID_ROW = "2026-01-28,fomc_meeting,FOMC 2026 第1次议息会议\n"


def _write(tmp_path, content: str | bytes, name: str = "events.csv"):
    p = tmp_path / name
    if isinstance(content, bytes):
        p.write_bytes(content)
    else:
        p.write_text(content, encoding="utf-8")
    return p


class TestValidCsv:
    def test_minimal_valid(self, tmp_path):
        rows, errors = validate_manual_events_csv(_write(tmp_path, _VALID_HEADER + _VALID_ROW))
        assert errors == []
        assert len(rows) == 1
        assert rows[0]["event_date"] == "2026-01-28"
        assert rows[0]["event_type"] == "fomc_meeting"
        assert rows[0]["data_source"] == "manual"  # 缺省补 manual

    def test_bom_tolerated(self, tmp_path):
        content = ("﻿" + _VALID_HEADER + _VALID_ROW).encode("utf-8")
        rows, errors = validate_manual_events_csv(_write(tmp_path, content))
        assert errors == [] and len(rows) == 1

    def test_comments_and_empty_lines_skipped(self, tmp_path):
        content = (
            "# FOMC 2026 台账（手工录入）\n"
            "\n"
            + _VALID_HEADER
            + "# 第1次\n"
            + _VALID_ROW
            + "\n"
            + "2026-03-18,fomc_meeting,FOMC 2026 第2次议息会议\n"
        )
        rows, errors = validate_manual_events_csv(_write(tmp_path, content))
        assert errors == [] and len(rows) == 2

    def test_column_order_irrelevant(self, tmp_path):
        content = "description,event_type,event_date\nFOMC 2026 第1次议息,fomc_meeting,2026-01-28\n"
        rows, errors = validate_manual_events_csv(_write(tmp_path, content))
        assert errors == []
        assert rows[0]["event_type"] == "fomc_meeting"
        assert rows[0]["event_date"] == "2026-01-28"

    def test_explicit_data_source_manual_accepted(self, tmp_path):
        content = "event_date,event_type,description,data_source\n" + _VALID_ROW.replace(
            "\n", ",manual\n"
        )
        rows, errors = validate_manual_events_csv(_write(tmp_path, content))
        assert errors == [] and rows[0]["data_source"] == "manual"

    def test_all_three_event_types(self, tmp_path):
        content = _VALID_HEADER + (
            "2026-01-28,fomc_meeting,FOMC 议息\n"
            "2026-03-05,major_meeting,全国两会\n"
            "2008-09-19,stamp_duty_change,印花税改单边征收\n"
        )
        rows, errors = validate_manual_events_csv(_write(tmp_path, content))
        assert errors == [] and len(rows) == 3


class TestHeaderErrors:
    def test_missing_required_column(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, "event_date,event_type\n2026-01-28,fomc_meeting\n")
        )
        assert rows == []
        assert any("缺少必需列" in e and "description" in e for e in errors)

    def test_unknown_column(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, "event_date,event_type,description,extra_col\n" + _VALID_ROW.replace("\n", ",x\n"))
        )
        assert any("未知列" in e for e in errors)

    def test_no_header(self, tmp_path):
        rows, errors = validate_manual_events_csv(_write(tmp_path, "# 只有注释\n\n"))
        assert rows == []
        assert any("无有效列头" in e for e in errors)


class TestRowErrors:
    def test_bad_date_format(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, _VALID_HEADER + "2026/01/28,fomc_meeting,FOMC\n")
        )
        assert rows == []
        assert any("YYYY-MM-DD" in e for e in errors)

    def test_invalid_calendar_date(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, _VALID_HEADER + "2026-02-30,fomc_meeting,FOMC\n")
        )
        assert rows == []
        assert any("event_date" in e for e in errors)

    def test_date_out_of_range(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, _VALID_HEADER + "1980-01-01,fomc_meeting,过早\n2200-01-01,fomc_meeting,过晚\n")
        )
        assert rows == []
        assert sum("超出范围" in e for e in errors) == 2

    def test_internal_event_type_rejected(self, tmp_path):
        """internal 派生九类（如 month_end）禁止走 CSV（防与派生通道双写冲突）。"""
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, _VALID_HEADER + "2026-01-30,month_end,月末\n")
        )
        assert rows == []
        assert any("event_type 非法" in e for e in errors)

    def test_empty_description(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, _VALID_HEADER + "2026-01-28,fomc_meeting,\n")
        )
        assert rows == []
        assert any("description 为空" in e for e in errors)

    def test_overlong_description(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, _VALID_HEADER + f"2026-01-28,fomc_meeting,{'长' * 201}\n")
        )
        assert rows == []
        assert any("超长" in e for e in errors)

    def test_column_count_mismatch(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, _VALID_HEADER + "2026-01-28,fomc_meeting\n")
        )
        assert rows == []
        assert any("列数" in e for e in errors)

    def test_duplicate_key(self, tmp_path):
        rows, errors = validate_manual_events_csv(
            _write(tmp_path, _VALID_HEADER + _VALID_ROW + _VALID_ROW)
        )
        assert len(rows) == 1
        assert any("同键重复" in e for e in errors)

    def test_explicit_non_manual_data_source_rejected(self, tmp_path):
        content = "event_date,event_type,description,data_source\n2026-01-28,fomc_meeting,FOMC,akshare\n"
        rows, errors = validate_manual_events_csv(_write(tmp_path, content))
        assert rows == []
        assert any("data_source" in e for e in errors)

    def test_error_aggregation_continues(self, tmp_path):
        """单行错误不影响后续合法行；错误带行号。"""
        content = _VALID_HEADER + "bad-date,fomc_meeting,坏行\n" + _VALID_ROW
        rows, errors = validate_manual_events_csv(_write(tmp_path, content))
        assert len(rows) == 1
        assert any("行 2" in e for e in errors)


class TestFileErrors:
    def test_file_not_found(self, tmp_path):
        rows, errors = validate_manual_events_csv(tmp_path / "nonexistent.csv")
        assert rows == []
        assert any("文件不存在" in e for e in errors)

    def test_header_only_no_data_rows(self, tmp_path):
        rows, errors = validate_manual_events_csv(_write(tmp_path, _VALID_HEADER))
        assert rows == [] and errors == []
