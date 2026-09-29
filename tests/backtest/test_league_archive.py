# [BLUEPRINT] MOD-AUTO-L11-ARCHIVE | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 测试
# [MODULE] tests.backtest.test_league_archive
# [DOMAIN] D_BACKTEST
# [INVARIANTS] 零 CH/网络触碰（CH 经 sys.modules 假件注入）; 全部 IO 走 tmp_path fixture（禁写生产路径）
# [TTL] permanent
"""league_archive + league_monthly_snapshot 纯函数测试——manifest 组装/TSV 解析/快照表。"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "backtest") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "backtest"))

import league_archive as la  # noqa: E402
import league_monthly_snapshot as lms  # noqa: E402

_GROUP = {"group_id": "A", "status": "champion", "joined_date": "2026-09-21"}


class TestBuildManifest:
    def test_all_fingerprint_fields_present(self):
        m = la.build_manifest(
            _GROUP,
            "abc123",
            ["f1", "f2"],
            {"trade_date": "2026-09-18"},
            {"path": "data/backtest_artifacts/fw-auto/latest.json", "exists": True},
            {"review_policy": {}},
            created_at="20260921T000000+0000",
        )
        assert m["group_id"] == "A"
        assert m["fingerprint_code_git_hash"] == "abc123"
        assert m["fingerprint_factors"] == ["f1", "f2"]
        assert m["fingerprint_data_cutoff"]["trade_date"] == "2026-09-18"
        assert "fw_artifact_pointer" in m and "module_deps" in m
        # 复原边界必须如实载入 manifest
        assert "数据本体不可复原" in m["restore_semantics"]
        assert "trade_date" in m["restore_semantics"]

    def test_factors_list_copied_not_referenced(self):
        src = ["f1"]
        m = la.build_manifest(_GROUP, "abc123", src, {}, {}, {}, created_at="X")
        src.append("f2")
        assert m["fingerprint_factors"] == ["f1"]


class TestArchiveDirName:
    def test_format(self):
        assert la.archive_dir_name("A", "20260921") == "A-20260921"
        assert la.archive_dir_name("G", "20260921") == "G-20260921"


class TestParseScalarTsv:
    def test_headerless_tsv_primary_form(self):
        # ch_reader.query 实测返回无表头 TSV（2026-09-21 实测钉值）
        assert la.parse_scalar_tsv("2026-09-18\n") == "2026-09-18"

    def test_header_form_tolerated(self):
        assert la.parse_scalar_tsv("max(trade_date)\n2026-09-18\n") == "2026-09-18"

    def test_empty_and_header_only(self):
        assert la.parse_scalar_tsv("") is None
        assert la.parse_scalar_tsv("max(trade_date)\n") is None

    def test_blank_value_is_none(self):
        assert la.parse_scalar_tsv("d\n\t\n") is None


class TestFactorListFromFwPlan:
    def test_weights_keys_sorted(self):
        fw = {"plan": {"weights": {"STR-B": 0.5, "STR-A": 0.5}}}
        assert la.factor_list_from_fw_plan(fw) == ["STR-A", "STR-B"]

    def test_missing_plan_gives_empty(self):
        assert la.factor_list_from_fw_plan({}) == []


class TestLoadFwPointer:
    def test_missing_file_reports_exists_false(self, tmp_path):
        p = la.load_fw_pointer(tmp_path / "latest.json")
        assert p["exists"] is False and "缺失" in p.get("note", "")

    def test_broken_json_degrades(self, tmp_path):
        f = tmp_path / "latest.json"
        f.write_text("{bad json", encoding="utf-8")
        p = la.load_fw_pointer(f)
        assert p["exists"] is True and "不可解析" in p.get("note", "")

    def test_pointer_extracts_fingerprint_fields(self, tmp_path):
        f = tmp_path / "latest.json"
        f.write_text(
            '{"trigger": "auto_mount", "plan": {"plan_id": "fw-tdm-current", '
            '"fingerprint": "fe90e572"}, "window": {"start": "2025-09-16", "end": "2026-09-16"}}',
            encoding="utf-8",
        )
        p = la.load_fw_pointer(f)
        assert p["exists"] is True
        assert p["plan_id"] == "fw-tdm-current"
        assert p["fingerprint"] == "fe90e572"
        assert p["window"]["end"] == "2026-09-16"


class TestWriteArchive:
    def _manifest(self) -> dict:
        return la.build_manifest(_GROUP, "abc123", [], {}, {}, {}, created_at="20260921T000000+0000")

    def test_writes_manifest_yaml(self, tmp_path):
        out = la.write_archive(self._manifest(), tmp_path)
        assert out.name == "manifest.yaml" and out.parent.name == "A-20260921"
        loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert loaded["group_id"] == "A"

    def test_second_write_same_date_raises(self, tmp_path):
        la.write_archive(self._manifest(), tmp_path)
        with pytest.raises(FileExistsError):
            la.write_archive(self._manifest(), tmp_path)


class TestCurrentGitHash:
    def test_returns_hex_hash_in_repo(self):
        h = la.current_git_hash(REPO_ROOT)
        assert len(h) == 40 and all(c in "0123456789abcdef" for c in h)


class TestQueryDataCutoffDegrade:
    def test_ch_down_degrades_to_none(self, monkeypatch):
        import league_archive as la_mod

        def _boom(sql):
            raise RuntimeError("CH down")

        fake = types.ModuleType("zephyr.data.ch_reader")
        fake.query = _boom
        monkeypatch.setitem(sys.modules, "zephyr.data.ch_reader", fake)
        out = la_mod.query_data_cutoff()
        assert out["trade_date"] is None and "CH 不可达" in out["note"]


# ---------- league_monthly_snapshot 纯函数 ----------


class TestParsePocketTsv:
    def test_round_trip_headerless(self):
        # ch_reader.query 实测无表头 TSV（主形态）
        tsv = "2026-09-01\t1000000.0\n2026-09-02\t1010000.5\n"
        rows = lms.parse_pocket_tsv(tsv)
        assert rows == [
            {"trade_date": "2026-09-01", "equity": 1000000.0},
            {"trade_date": "2026-09-02", "equity": 1010000.5},
        ]

    def test_header_line_tolerated(self):
        tsv = "trade_date\tequity\n2026-09-01\t100.0\n"
        assert lms.parse_pocket_tsv(tsv) == [{"trade_date": "2026-09-01", "equity": 100.0}]

    def test_empty_and_garbage_rows(self):
        assert lms.parse_pocket_tsv("") == []
        assert lms.parse_pocket_tsv("trade_date\tequity\n") == []
        assert lms.parse_pocket_tsv("trade_date\tequity\n2026-09-01\tnot-a-number\n") == []


class TestMemberSummary:
    def test_empty_rows(self):
        s = lms.member_summary([])
        assert s["days"] == 0 and s["monthly_return"] is None

    def test_positive_month(self):
        rows = [
            {"trade_date": "2026-09-01", "equity": 100.0},
            {"trade_date": "2026-09-15", "equity": 90.0},
            {"trade_date": "2026-09-30", "equity": 110.0},
        ]
        s = lms.member_summary(rows)
        assert s["days"] == 3
        assert s["monthly_return"] == pytest.approx(0.10)
        assert s["max_drawdown"] == pytest.approx(0.10)  # 100→90 回撤 10%

    def test_zero_start_equity_no_crash(self):
        rows = [{"trade_date": "2026-09-01", "equity": 0.0}, {"trade_date": "2026-09-02", "equity": 10.0}]
        assert lms.member_summary(rows)["monthly_return"] is None


class TestRenderSnapshot:
    def test_contains_disclaimer_and_table(self):
        groups = [{"group_id": "A", "name_zh": "A 组", "status": "champion", "members": ["S-1", "S-2"]}]
        data = {
            "A": {
                "S-1": {
                    "days": 20,
                    "start_equity": 100.0,
                    "end_equity": 110.0,
                    "monthly_return": 0.1,
                    "max_drawdown": 0.05,
                },
                "S-2": None,
            }
        }  # S-2=CH 断供缺口
        text = lms.render_snapshot(data, groups, "2026-09")
        assert "# A/B 联赛月度快照 2026-09" in text
        assert "只留档不判胜负" in text
        assert "CH 缺口" in text
        assert "10.0000%" in text

    def test_group_without_members_noted(self):
        groups = [{"group_id": "B", "name_zh": "B 组", "status": "challenger", "members": []}]
        text = lms.render_snapshot({}, groups, "2026-09")
        assert "暂无成员入组" in text


class TestSnapshotPath:
    def test_month_formatting(self, tmp_path):
        p = lms.snapshot_path("2026-09", tmp_path)
        assert p.name == "snapshot-202609.md"


class TestFetchMemberRowsInjection:
    def test_uses_injected_ch_reader(self, monkeypatch):
        captured = {}

        def fake_query(sql, *a, **k):
            captured["sql"] = sql
            return "2026-09-01\t100.0\n"  # 无表头（ch_reader 实测形态）

        fake = types.ModuleType("zephyr.data.ch_reader")
        fake.query = fake_query
        monkeypatch.setitem(sys.modules, "zephyr.data.ch_reader", fake)
        rows = lms.fetch_member_rows("S-1", "2026-09")
        assert rows and rows[0]["equity"] == 100.0
        assert "strategy_id = 'S-1'" in captured["sql"]

    def test_quote_injection_neutralized(self, monkeypatch):
        captured = {}

        def fake_query(sql, *a, **k):
            captured["sql"] = sql
            return ""

        fake = types.ModuleType("zephyr.data.ch_reader")
        fake.query = fake_query
        monkeypatch.setitem(sys.modules, "zephyr.data.ch_reader", fake)
        lms.fetch_member_rows("S'); DROP--", "2026-09")
        # 净化后：裸引号/反斜杠被剥除，恶意片段不再以原样进入 SQL
        assert "S'); DROP--" not in captured["sql"]
        assert "S); DROP--" in captured["sql"]
        assert "\\" not in captured["sql"]
