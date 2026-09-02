# [BLUEPRINT] MOD-NLP-PIPELINE | 13_regime_phase3_engineering_plan.md | §Phase 7
# [TTL] permanent
"""test_ml_run_research_rating_batch.py — 研报评级批量脚本单元测试（CAND-NLP-006）。

覆盖（零外部依赖，不触达 ClickHouse）：
  1. extract_rows —— 字段齐备/单行失败跳过
  2. aggregate_daily —— 评级分布/变动计数/均分/目标价统计/无值 None 处理
  3. load_done_ids —— 断点续作去重
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "run_research_rating_batch",
    _ROOT / "scripts" / "ml" / "run_research_rating_batch.py",
)
rrb = importlib.util.module_from_spec(_spec)
sys.modules["run_research_rating_batch"] = rrb
_spec.loader.exec_module(rrb)


def _rep(news_id: str, title: str, summary: str, day: str = "2026-08-20 10:00:00") -> dict:
    return {
        "news_id": news_id,
        "publish_time": day,
        "title": title,
        "summary": summary,
        "source": "akshare_research_report",
    }


class TestExtractRows:
    def test_fields_complete(self):
        rows = rrb.extract_rows(
            [
                _rep("n1", "首次覆盖：品牌基因驱动成长", "机构:招银国际 | 评级:增持 | 行业:工程机械"),
            ]
        )
        (r,) = rows
        assert r["news_id"] == "n1"
        assert r["publish_date"] == "2026-08-20"
        assert r["org"] == "招银国际"
        assert r["rating"] == "增持"
        assert r["score"] == 0.6
        assert r["revision"] == "initiation"

    def test_bad_row_skipped(self, monkeypatch):
        """analyze_report 抛异常的行被跳过（None 等退化输入由模块自身容错不属此类）。"""
        orig = rrb.analyze_report

        def _boom(title, summary):
            if title == "炸":
                raise ValueError("boom")
            return orig(title, summary)

        monkeypatch.setattr(rrb, "analyze_report", _boom)
        rows = rrb.extract_rows(
            [
                _rep("n1", "正常标题", "机构:A | 评级:买入"),
                _rep("n2", "炸", "机构:B | 评级:增持"),
            ]
        )
        assert [r["news_id"] for r in rows] == ["n1"]

    def test_degenerate_row_yields_degenerate_output(self):
        """None 字段不抛异常（模块容错契约），产出退化值。"""
        rows = rrb.extract_rows(
            [
                {"news_id": "n3", "publish_time": None, "title": "x", "summary": "", "source": "s"},
            ]
        )
        (r,) = rows
        assert r["publish_date"] == "None"
        assert r["score"] is None and r["revision"] == "none"


class TestAggregateDaily:
    def test_metrics(self):
        rows = [
            {
                "publish_date": "2026-08-20",
                "rating": "买入",
                "score": 1.0,
                "revision": "initiation",
                "target_price": 58.0,
            },
            {
                "publish_date": "2026-08-20",
                "rating": "增持",
                "score": 0.6,
                "revision": "maintain",
                "target_price": None,
            },
            {
                "publish_date": "2026-08-20",
                "rating": "中性",
                "score": 0.0,
                "revision": "downgrade",
                "target_price": 40.0,
            },
            {"publish_date": "2026-08-21", "rating": "", "score": None, "revision": "none", "target_price": None},
        ]
        daily = rrb.aggregate_daily(rows)
        assert [d["day"] for d in daily] == ["2026-08-20", "2026-08-21"]
        d0, d1 = daily
        assert d0["n_reports"] == 3
        assert abs(d0["mean_score"] - (1.0 + 0.6 + 0.0) / 3) < 1e-9
        assert d0["rating_dist"] == {"买入": 1, "增持": 1, "中性": 1}
        assert d0["n_initiation"] == 1 and d0["n_downgrade"] == 1 and d0["n_maintain"] == 1
        assert d0["n_with_target_price"] == 2
        assert abs(d0["mean_target_price"] - 49.0) < 1e-9
        assert d1["mean_score"] is None and d1["mean_target_price"] is None


class TestLoadDoneIds:
    def test_roundtrip(self, tmp_path):
        p = tmp_path / "r.jsonl"
        p.write_text(json.dumps({"news_id": "a"}) + "\n{bad}\n" + json.dumps({"news_id": "b"}) + "\n", encoding="utf-8")
        assert rrb.load_done_ids(p) == {"a", "b"}
        assert rrb.load_done_ids(tmp_path / "nope.jsonl") == set()
