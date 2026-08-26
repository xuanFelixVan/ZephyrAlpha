# [BLUEPRINT] MOD-L00-004 | data_source_integrator_blueprint.md | §4
# [TTL] permanent
"""test_ch_backfill_research_report_2025.py — 2025 研报补采器单元测试（CAND-DAT-023）。

覆盖（Fake 零外部依赖，不触达 akshare/ClickHouse）：
  1. fetch_2025_rows —— 年份过滤/11 元组含 category/空标题跳过/摘要字段拼装
  2. 断点续作 —— load_done_symbols 读写往返
  3. flush —— FetchResult 列顺序含 category、空批不写
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pandas as pd
import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "backfill_research_report_2025",
    _ROOT / "scripts" / "ch" / "backfill_research_report_2025.py",
)
bf = importlib.util.module_from_spec(_spec)
sys.modules["backfill_research_report_2025"] = bf
_spec.loader.exec_module(bf)


def _df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


_R = {
    "报告名称": "公司点评：业绩超预期，维持买入",
    "日期": "2025-06-15",
    "机构": "某某证券",
    "东财评级": "买入",
    "行业": "电子",
    "报告PDF链接": "http://example.com/x.pdf",
}


class TestFetch2025Rows:
    def test_filters_year_and_builds_category_rows(self):
        df = _df([
            _R,
            {**_R, "日期": "2024-12-31"},
            {**_R, "日期": "2026-01-01"},
            {**_R, "报告名称": ""},
        ])
        rows = bf.fetch_2025_rows("600519", df)
        assert len(rows) == 1
        row = rows[0]
        assert len(row) == 11
        assert row[-1] == "research_report"
        assert row[2] == _R["报告名称"]  # title 列
        assert "机构:某某证券" in row[4] and "评级:买入" in row[4] and "行业:电子" in row[4]
        assert row[5] == "akshare_research_report"  # source 列

    def test_empty_and_all_out_of_range(self):
        assert bf.fetch_2025_rows("600519", _df([{**_R, "日期": "2026-03-01"}])) == []
        assert bf.fetch_2025_rows("600519", _df([])) == []

    def test_existing_ids_prefilter(self):
        """库内已有 news_id 预检集命中即跳过（写侧防多版本冗余）。"""
        rows = bf.fetch_2025_rows("600519", _df([_R]))
        assert len(rows) == 1
        nid = rows[0][0]
        assert bf.fetch_2025_rows("600519", _df([_R]), {nid}) == []


class TestResume:
    def test_progress_roundtrip(self, tmp_path, monkeypatch):
        pf = tmp_path / "done.txt"
        monkeypatch.setattr(bf, "PROGRESS_FILE", pf)
        assert bf.load_done_symbols() == set()
        pf.write_text("600519\n000001\n", encoding="utf-8")
        assert bf.load_done_symbols() == {"600519", "000001"}


class TestFlush:
    def test_writes_fetch_result_with_category_column(self, monkeypatch):
        captured = {}

        def _fake_write(result, *a, **kw):
            captured["result"] = result
            return True

        monkeypatch.setattr(bf.ch_writer, "write_result", _fake_write)
        row = bf.build_news_row("2025-06-15", "t", "", "s", "akshare_research_report", "akshare") + ("research_report",)
        bf.flush([row])
        res = captured["result"]
        assert res.table == "c3_fundamental.news_data"
        assert res.columns[-1] == "category"
        assert res.rows[0][-1] == "research_report"
        assert len(res.rows[0]) == len(res.columns)

    def test_empty_batch_no_write(self, monkeypatch):
        called = []
        monkeypatch.setattr(bf.ch_writer, "write_result", lambda *a, **kw: called.append(1))
        bf.flush([])
        assert called == []

    def test_write_failure_raises(self, monkeypatch):
        monkeypatch.setattr(bf.ch_writer, "write_result", lambda *a, **kw: False)
        with pytest.raises(RuntimeError):
            bf.flush([("x",) * 11])
