# [MODULE] tests.nlp.test_sentiment_pipeline
# [DOMAIN] D_DATA
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/nlp/test_sentiment_pipeline.py -q
"""test_sentiment_pipeline.py — sentiment_pipeline 离线批量端到端接线件单元测试。

覆盖（FakeChat 零外部依赖，不触达 Ollama/ClickHouse/网络）：
  1. run_offline_pipeline —— 端到端（推理→聚合→sink）/outcome 指标/日键提取
  2. 空输入 → 空 outcome 且 sink 不调用
  3. 单条推理失败降级 neutral 不阻断（n_degraded 计数）
  4. chat=None → NLPInferenceError（契约违反传播）
  5. daily_sink 注入——mock sink 收到聚合产物
  6. write_daily_jsonl —— JSONL 落盘字段齐备（negative_count/vote_score）
"""

from __future__ import annotations

import json

import pytest

from zephyr.nlp.nlp_inference import NLPInferenceError
from zephyr.nlp.sentiment_pipeline import (
    publish_date_of,
    run_offline_pipeline,
    write_daily_jsonl,
)


def _news(news_id: str, source: str = "eastmoney", day: str = "2026-08-19", title: str = "t") -> dict:
    return {
        "news_id": news_id,
        "title": title,
        "content": "",
        "source": source,
        "publish_time": f"{day} 10:30:00",
    }


class _FakeChat:
    """按标题关键词决定响应的 fake 后端（零外部依赖）。"""

    def ask(self, prompt: str, *, system: str = "", temperature: float | None = None) -> str:
        if "bad" in prompt:
            return '{"sentiment": "negative", "score": 0.9}'
        if "boom" in prompt:
            raise RuntimeError("backend down")
        return '{"sentiment": "positive", "score": 0.8}'


# ============ 1. 端到端 ============


class TestRunOfflinePipeline:
    def test_e2e_infer_aggregate_sink(self):
        news = [
            _news("n1", source="eastmoney", title="bad 利空"),
            _news("n2", source="cls", title="bad 又利空"),
            _news("n3", source="rss", day="2026-08-20", title="good 利好"),
        ]
        captured: list = []
        outcome = run_offline_pipeline(news, chat=_FakeChat(), daily_sink=captured.append)
        assert outcome.n_input == 3
        assert outcome.n_inferred == 3
        assert outcome.n_degraded == 0
        assert outcome.n_daily == 2
        assert outcome.elapsed_s >= 0.0
        # sink 收到聚合产物
        assert len(captured) == 1
        daily = captured[0]
        assert [d.day for d in daily] == ["2026-08-19", "2026-08-20"]
        assert daily[0].negative_count == 2
        assert daily[0].vote_strength == "strong"  # 两源同向负
        assert daily[1].vote_strength == "weak"  # 单源孤证
        # outcome.daily 与 sink 产物一致
        assert [d.day for d in outcome.daily] == ["2026-08-19", "2026-08-20"]

    def test_empty_input_empty_outcome_sink_not_called(self):
        captured: list = []
        outcome = run_offline_pipeline([], chat=_FakeChat(), daily_sink=captured.append)
        assert outcome.n_input == 0
        assert outcome.n_inferred == 0
        assert outcome.n_daily == 0
        assert outcome.daily == ()
        assert captured == []

    def test_single_failure_degrades_not_blocks(self):
        news = [_news("n1", title="boom"), _news("n2")]
        outcome = run_offline_pipeline(news, chat=_FakeChat())
        assert outcome.n_inferred == 2
        assert outcome.n_degraded == 1
        assert outcome.n_daily == 1

    def test_chat_none_raises_contract_error(self):
        with pytest.raises(NLPInferenceError):
            run_offline_pipeline([_news("n1")], chat=None)

    def test_no_sink_still_aggregates(self):
        news = [_news("n1"), _news("n2", source="cls")]
        outcome = run_offline_pipeline(news, chat=_FakeChat(), daily_sink=None)
        assert outcome.n_daily == 1
        assert outcome.daily[0].n_news == 2


# ============ 2. 日键提取 ============


class TestPublishDateOf:
    def test_publish_time_string(self):
        assert publish_date_of(_news("n1", day="2026-08-18")) == "2026-08-18"

    def test_publish_date_fallback(self):
        assert publish_date_of({"publish_date": "2026-01-01"}) == "2026-01-01"

    def test_missing_returns_empty(self):
        assert publish_date_of({}) == ""


# ============ 3. write_daily_jsonl ============


class TestWriteDailyJsonl:
    def test_fields_roundtrip(self, tmp_path):
        news = [
            _news("n1", source="eastmoney", title="bad x"),
            _news("n2", source="cls", title="bad y"),
        ]
        outcome = run_offline_pipeline(news, chat=_FakeChat())
        out = tmp_path / "daily_sentiment.jsonl"
        write_daily_jsonl(outcome.daily, out)
        rows = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines()]
        assert len(rows) == 1
        assert rows[0]["negative_count"] == 2
        assert rows[0]["vote_score"] < 0
        assert rows[0]["vote_strength"] == "strong"
        # 验收脚本检查项 3 必需字段
        assert {"negative_count", "vote_score", "vote_strength"} <= set(rows[0])

    def test_empty_daily_writes_empty_file(self, tmp_path):
        out = tmp_path / "sub" / "daily.jsonl"
        write_daily_jsonl([], out)
        assert out.exists()
        assert out.read_text(encoding="utf-8") == ""
