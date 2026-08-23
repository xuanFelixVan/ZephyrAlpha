# [BLUEPRINT] MOD-NLP-PIPELINE | 13_regime_phase3_engineering_plan.md | §Phase 7
# [TTL] permanent
"""test_ml_run_sentiment_batch.py — 离线批量推理+日级聚合脚本单元测试（Phase 7）。

覆盖（FakeChat 零外部依赖，不触达 Ollama/ClickHouse）：
  1. load_news_jsonl / publish_date_of —— 输入解析与日键提取
  2. run_batch —— 端到端预测写入/断点续作跳过/单条失败降级不阻断
  3. aggregate_from_predictions —— resume 安全的全量聚合（含历史部分）
  4. write_daily —— 日级产物落盘字段（negative_count/vote_score）
  5. main 守卫 —— jsonl 源缺 --input  exit 1
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "run_sentiment_batch",
    _ROOT / "scripts" / "ml" / "run_sentiment_batch.py",
)
rsb = importlib.util.module_from_spec(_spec)
sys.modules["run_sentiment_batch"] = rsb  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(rsb)


def _news(news_id: str, source: str = "eastmoney", day: str = "2026-08-19", title: str = "t") -> dict:
    return {
        "news_id": news_id,
        "title": title,
        "content": "",
        "source": source,
        "publish_time": f"{day} 10:30:00",
    }


def _write_jsonl(path: pathlib.Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


class _FakeChat:
    """按 news 标题决定响应的 fake 后端（零外部依赖）。"""

    def ask(self, prompt: str, *, system: str = "", temperature: float | None = None) -> str:
        if "bad" in prompt:
            return '{"sentiment": "negative", "score": 0.9}'
        if "boom" in prompt:
            raise RuntimeError("backend down")
        return '{"sentiment": "positive", "score": 0.8}'


# ============ 1. 输入解析 ============


class TestInputParsing:
    def test_load_news_jsonl_skips_bad_lines(self, tmp_path):
        p = tmp_path / "in.jsonl"
        p.write_text(
            json.dumps(_news("n1")) + "\n" + "{not json}\n" + json.dumps(_news("n2")) + "\n",
            encoding="utf-8",
        )
        items = rsb.load_news_jsonl(p)
        assert [i["news_id"] for i in items] == ["n1", "n2"]

    def test_publish_date_extraction(self):
        assert rsb.publish_date_of(_news("n1", day="2026-08-18")) == "2026-08-18"
        assert rsb.publish_date_of({"publish_date": "2026-01-01"}) == "2026-01-01"
        assert rsb.publish_date_of({}) == ""


# ============ 2. run_batch ============


class TestRunBatch:
    def test_writes_predictions_and_returns_results(self, tmp_path):
        news = [_news("n1"), _news("n2", source="cls")]
        pred = tmp_path / "predictions.jsonl"
        results = rsb.run_batch(news, chat=_FakeChat(), pred_path=pred)
        assert len(results) == 2
        rows = [json.loads(x) for x in pred.read_text(encoding="utf-8").splitlines()]
        assert rows[0]["news_id"] == "n1"
        assert rows[0]["polarity"] == pytest.approx(0.8)
        assert rows[1]["source"] == "cls"

    def test_resume_skips_done(self, tmp_path):
        pred = tmp_path / "predictions.jsonl"
        _write_jsonl(pred, [{"news_id": "n1", "polarity": 0.8}])
        news = [_news("n1"), _news("n2")]
        results = rsb.run_batch(news, chat=_FakeChat(), pred_path=pred, resume=True)
        assert len(results) == 1  # n1 已预测跳过
        rows = pred.read_text(encoding="utf-8").splitlines()
        assert len(rows) == 2  # 追加而非覆盖

    def test_single_failure_degrades_not_blocks(self, tmp_path):
        news = [_news("n1", title="boom"), _news("n2")]
        pred = tmp_path / "predictions.jsonl"
        results = rsb.run_batch(news, chat=_FakeChat(), pred_path=pred)
        assert len(results) == 2
        assert results[0].sentiment == "neutral"  # 推理失败降级
        assert results[0].error != ""
        assert results[1].sentiment == "positive"


# ============ 3. aggregate_from_predictions ============


class TestAggregateFromPredictions:
    def test_aggregates_full_file(self, tmp_path):
        pred = tmp_path / "predictions.jsonl"
        _write_jsonl(
            pred,
            [
                {"news_id": "n1", "source": "eastmoney", "publish_date": "2026-08-18", "polarity": -0.8},
                {"news_id": "n2", "source": "cls", "publish_date": "2026-08-18", "polarity": -0.6},
                {"news_id": "n3", "source": "rss", "publish_date": "2026-08-19", "polarity": 0.7},
            ],
        )
        daily = rsb.aggregate_from_predictions(pred)
        assert [d.day for d in daily] == ["2026-08-18", "2026-08-19"]
        assert daily[0].negative_count == 2
        assert daily[0].vote_strength == "strong"  # 两源同向
        assert daily[1].vote_strength == "weak"  # 单源孤证

    def test_missing_file_returns_empty(self, tmp_path):
        assert rsb.aggregate_from_predictions(tmp_path / "nope.jsonl") == []


# ============ 4. write_daily ============


class TestWriteDaily:
    def test_daily_fields_written(self, tmp_path):
        pred = tmp_path / "predictions.jsonl"
        _write_jsonl(
            pred,
            [
                {"news_id": "n1", "source": "eastmoney", "publish_date": "2026-08-18", "polarity": -0.8},
                {"news_id": "n2", "source": "cls", "publish_date": "2026-08-18", "polarity": -0.6},
            ],
        )
        daily = rsb.aggregate_from_predictions(pred)
        out = tmp_path / "daily_sentiment.jsonl"
        rsb.write_daily(daily, out)
        rows = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
        assert rows[0]["negative_count"] == 2
        assert rows[0]["vote_score"] < 0
        assert rows[0]["vote_strength"] == "strong"


# ============ 5. benchmark 产物（验收检查项 2 生产者）============


class TestWriteBenchmark:
    def test_writes_items_and_elapsed(self, tmp_path):
        bench = tmp_path / "sub" / "benchmark.json"
        rsb.write_benchmark(1000, 240.5, bench)
        obj = json.loads(bench.read_text(encoding="utf-8"))
        assert obj["items"] == 1000
        assert obj["elapsed_s"] == pytest.approx(240.5)

    def test_zero_items(self, tmp_path):
        bench = tmp_path / "benchmark.json"
        rsb.write_benchmark(0, 0.0, bench)
        obj = json.loads(bench.read_text(encoding="utf-8"))
        assert obj == {"items": 0, "elapsed_s": 0.0}


# ============ 6. main 守卫 ============


class TestMainGuards:
    def test_jsonl_source_missing_input_exits_1(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            rsb.sys,
            "argv",
            ["run_sentiment_batch.py", "--source", "jsonl", "--input", str(tmp_path / "nope.jsonl")],
        )
        with pytest.raises(SystemExit) as exc:
            rsb.main()
        assert exc.value.code == 1
