# [BLUEPRINT] MOD-INF-088 | docs/03_modules/_domain_infrastructure_operations/loki_log_pipeline/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-088 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_ops.test_loki_log_pipeline
# [TESTS] src/zephyr/infra_ops/loki_log_pipeline.py
"""MOD-INF-088 单元测试：loki_log_pipeline Loki 日志聚合管道。

蓝图验收（B8-10662/CAND-INFRAOPS-006，A8集成架构）：
JSON 结构化日志（Agent决策/自治边界/风控否决/异常事件）构建 + 推送管道
（loki_push_client 注入不真发 HTTP，失败重试计数+DLQ）+ LogQL 查询构建
器 + 热30天/冷 Parquet 导出策略裁决（注入时钟）+ 脱敏钩子注入。
client/clock/sanitizer 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infra_ops.loki_log_pipeline",
    reason="loki_log_pipeline not importable",
)

from zephyr.infra_ops.loki_log_pipeline import (  # noqa: E402
    LogCategory,
    LokiLogPipeline,
    LokiPipelineError,
    RetentionTier,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _pipe(client=None, sanitizer=None, max_retries: int = 3) -> LokiLogPipeline:
    return LokiLogPipeline(
        loki_push_client=client if client is not None else (lambda e: True),
        clock=lambda: _T0,
        sanitizer=sanitizer,
        max_retries=max_retries,
        hot_retention_days=30,
    )


def _entry(pipe: LokiLogPipeline | None = None) -> dict:
    p = pipe or _pipe()
    return p.build_entry(
        LogCategory.AGENT_DECISION,
        {"agent": "risk_manager", "env": "prod"},
        {"action": "veto", "score": 0.9},
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验
# ──────────────────────────────────────────────────────────────────────────────


class TestConstruct:
    def test_negative_retries_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            LokiLogPipeline(clock=lambda: _T0, max_retries=-1)

    def test_nonpositive_hot_days_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            LokiLogPipeline(clock=lambda: _T0, hot_retention_days=0)


# ──────────────────────────────────────────────────────────────────────────────
# 结构化日志构建
# ──────────────────────────────────────────────────────────────────────────────


class TestBuildEntry:
    def test_ok_structure(self) -> None:
        entry = _entry()
        assert entry["category"] == "agent_decision"
        assert entry["labels"] == {"agent": "risk_manager", "env": "prod"}
        assert entry["ts"] == _T0.isoformat()
        assert entry["payload"] == {"action": "veto", "score": 0.9}

    def test_all_categories(self) -> None:
        p = _pipe()
        for cat, value in [
            (LogCategory.AGENT_DECISION, "agent_decision"),
            (LogCategory.AUTONOMY_BOUNDARY, "autonomy_boundary"),
            (LogCategory.RISK_VETO, "risk_veto"),
            (LogCategory.ANOMALY_EVENT, "anomaly_event"),
        ]:
            assert p.build_entry(cat, {}, {})["category"] == value

    def test_invalid_category_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().build_entry("agent_decision", {}, {})  # str 非 LogCategory

    def test_empty_label_key_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().build_entry(LogCategory.RISK_VETO, {"": "x"}, {})

    def test_non_str_label_value_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().build_entry(LogCategory.RISK_VETO, {"k": 1}, {})

    def test_none_payload_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().build_entry(LogCategory.RISK_VETO, {}, None)

    def test_sanitizer_applied(self) -> None:
        def _mask(payload: dict) -> dict:
            return {k: ("***" if k == "secret" else v) for k, v in payload.items()}

        entry = _pipe(sanitizer=_mask).build_entry(
            LogCategory.ANOMALY_EVENT, {}, {"secret": "token-1", "ok": 1}
        )
        assert entry["payload"] == {"secret": "***", "ok": 1}

    def test_explicit_ts(self) -> None:
        ts = datetime.datetime(2026, 1, 1, 0, 0, 0)
        entry = _pipe().build_entry(LogCategory.RISK_VETO, {}, {}, ts=ts)
        assert entry["ts"] == ts.isoformat()


# ──────────────────────────────────────────────────────────────────────────────
# 推送管道（重试 + DLQ）
# ──────────────────────────────────────────────────────────────────────────────


class TestPush:
    def test_client_missing_fail_closed(self) -> None:
        p = LokiLogPipeline(clock=lambda: _T0)
        with pytest.raises(LokiPipelineError):
            p.push(_entry())

    def test_push_ok(self) -> None:
        sent: list = []
        p = _pipe(client=lambda e: sent.append(e) or True)
        assert p.push(_entry(p)) is True
        assert len(sent) == 1
        assert p.retry_count == 0
        assert p.dlq == []

    def test_malformed_entry_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().push({"labels": {}})

    def test_retry_then_success(self) -> None:
        state = {"n": 0}

        def _flaky(e: dict) -> bool:
            state["n"] += 1
            return state["n"] >= 3  # 前两次失败第三次成功

        p = _pipe(client=_flaky)
        assert p.push(_entry(p)) is True
        assert p.retry_count == 2
        assert p.dlq == []

    def test_exhaust_to_dlq(self) -> None:
        p = _pipe(client=lambda e: False, max_retries=2)
        entry = _entry(p)
        assert p.push(entry) is False
        assert p.retry_count == 2
        assert p.dlq == [entry]

    def test_client_exception_retried(self) -> None:
        def _boom(e: dict) -> bool:
            raise RuntimeError("conn")

        p = _pipe(client=_boom, max_retries=1)
        assert p.push(_entry(p)) is False
        assert p.retry_count == 1
        assert len(p.dlq) == 1


# ──────────────────────────────────────────────────────────────────────────────
# LogQL 查询构建器
# ──────────────────────────────────────────────────────────────────────────────


class TestLogQL:
    def test_selector_sorted(self) -> None:
        q = _pipe().build_logql({"env": "prod", "app": "zephyr"})
        assert q == '{app="zephyr", env="prod"}'

    def test_filters_appended(self) -> None:
        q = _pipe().build_logql({"app": "zephyr"}, filters=["veto", "risk"])
        assert q == '{app="zephyr"} |= "veto" |= "risk"'

    def test_empty_selector_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().build_logql({})

    def test_invalid_selector_value_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().build_logql({"app": ""})

    def test_empty_filter_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().build_logql({"app": "zephyr"}, filters=[""])


# ──────────────────────────────────────────────────────────────────────────────
# 保留策略裁决（热30天/冷 Parquet 导出）
# ──────────────────────────────────────────────────────────────────────────────


class TestRetention:
    def test_hot_and_cold(self) -> None:
        p = _pipe()
        assert p.retention_decision(_T0 - datetime.timedelta(days=29)) is RetentionTier.HOT
        assert p.retention_decision(_T0 - datetime.timedelta(days=31)) is RetentionTier.COLD_EXPORT

    def test_boundary_30d_hot(self) -> None:
        p = _pipe()
        assert p.retention_decision(_T0 - datetime.timedelta(days=30)) is RetentionTier.HOT

    def test_entries_for_export(self) -> None:
        p = _pipe()
        old = p.build_entry(
            LogCategory.AGENT_DECISION, {}, {}, ts=_T0 - datetime.timedelta(days=45)
        )
        new = _entry(p)
        assert p.entries_for_export([old, new]) == [old]

    def test_bad_ts_raises(self) -> None:
        with pytest.raises(LokiPipelineError):
            _pipe().entries_for_export([{"ts": 123}])
