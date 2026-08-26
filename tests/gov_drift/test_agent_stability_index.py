# [BLUEPRINT] MOD-GOV-055 | docs/03_modules/_domain_gov_drift/agent_stability_index/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-GOV-055 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.gov_drift.test_agent_stability_index
# [TESTS] src/zephyr/gov_drift/agent_stability_index.py
"""MOD-GOV-055 单元测试：agent_stability_index Agent 稳定度指数检查器。

蓝图验收（B11-03056/CAND-GOVDRIFT-003）：语义一致性（注入 embedder 余弦）+
工具序列 Levenshtein 稳定性 + 推理路径编辑距离 + 多 Agent 一致率四分量 ASI +
滚动窗评估 + ASI<阈值连续 N 窗告警 + gov_drift 事件回调 + Fail-Closed 分支 +
确定性。embedder/事件/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.gov_drift.agent_stability_index",
    reason="agent_stability_index not importable",
)

from zephyr.gov_drift.agent_stability_index import (  # noqa: E402
    AgentStabilityError,
    AgentStabilityIndex,
    DriftEvent,
    InteractionRecord,
)

_T0 = datetime.datetime(2026, 8, 26, 15, 0, 0)

#: 确定性内存 embedder 词表（正交/同向向量人工构造）
_VECS = {
    "多": (1.0, 0.0),
    "空": (0.0, 1.0),
}


def _embedder(text: str) -> tuple[float, ...]:
    return _VECS.get(text, (1.0, 0.0))


def _index(
    events: list | None = None,
    window_size: int = 3,
    threshold: float = 0.75,
    alert_consecutive: int = 3,
    weights: dict | None = None,
    embedder=_embedder,
) -> AgentStabilityIndex:
    return AgentStabilityIndex(
        embedder=embedder,
        clock=lambda: _T0,
        event_sink=(lambda e: events.append(e)) if events is not None else None,
        window_size=window_size,
        asi_threshold=threshold,
        alert_consecutive=alert_consecutive,
        weights=weights,
    )


def _rec(
    agent: str = "signal_analyst",
    text: str = "多",
    tools: tuple[str, ...] = ("scan", "rank"),
    path: tuple[str, ...] = ("observe", "infer"),
    agreed: bool | None = True,
) -> InteractionRecord:
    return InteractionRecord(
        agent_id=agent,
        response_text=text,
        tool_sequence=tools,
        reasoning_path=path,
        agreed=agreed,
        ts=_T0,
    )


def _fill(idx: AgentStabilityIndex, n: int, **kwargs):
    return [idx.record_interaction(_rec(**kwargs)) for _ in range(n)]


# ──────────────────────────────────────────────────────────────────────────────
# 构造参数（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestConstructor:
    def test_embedder_required(self) -> None:
        with pytest.raises(AgentStabilityError):
            AgentStabilityIndex(embedder=None, clock=lambda: _T0)

    def test_invalid_params_rejected(self) -> None:
        with pytest.raises(AgentStabilityError):
            _index(window_size=1)
        with pytest.raises(AgentStabilityError):
            _index(threshold=0.0)
        with pytest.raises(AgentStabilityError):
            _index(threshold=1.5)
        with pytest.raises(AgentStabilityError):
            _index(alert_consecutive=0)
        with pytest.raises(AgentStabilityError):
            _index(weights={"ghost": 0.5})
        with pytest.raises(AgentStabilityError):
            _index(weights={"semantic": 0.0})


# ──────────────────────────────────────────────────────────────────────────────
# 交互接入与窗评估
# ──────────────────────────────────────────────────────────────────────────────


class TestRecordAndWindow:
    def test_window_not_full_returns_none(self) -> None:
        idx = _index()
        assert idx.record_interaction(_rec()) is None
        assert idx.record_interaction(_rec()) is None
        assert idx.buffered("signal_analyst") == 2

    def test_full_window_stable_asi_one(self) -> None:
        idx = _index()
        report = _fill(idx, 3)[-1]
        assert report is not None
        assert report.asi == pytest.approx(1.0)
        assert report.semantic_score == pytest.approx(1.0)
        assert report.tool_score == pytest.approx(1.0)
        assert report.path_score == pytest.approx(1.0)
        assert report.agreement_rate == pytest.approx(1.0)
        assert report.consecutive_low == 0
        assert report.alerted is False

    def test_rolling_window_slides(self) -> None:
        idx = _index(window_size=3)
        _fill(idx, 5)
        assert idx.buffered("signal_analyst") == 3  # deque 定长
        assert len(idx.reports("signal_analyst")) == 3  # 第3/4/5条各评估一次

    def test_semantic_drift_lowers_asi(self) -> None:
        idx = _index()
        reports = [
            idx.record_interaction(_rec(text="多" if i % 2 == 0 else "空"))  # 余弦 0
            for i in range(3)
        ]
        report = reports[-1]
        assert report.semantic_score == pytest.approx(0.0)
        # 0.4*0 + 0.2*1 + 0.2*1 + 0.2*1 = 0.6
        assert report.asi == pytest.approx(0.6)

    def test_sequence_drift_lowers_scores(self) -> None:
        idx = _index()
        idx.record_interaction(_rec())
        idx.record_interaction(_rec())
        report = idx.record_interaction(_rec(tools=("fetch", "dump"), path=("guess", "assert", "pray")))
        assert report.tool_score < 1.0
        assert report.path_score < 1.0
        assert report.asi < 1.0

    def test_agreement_none_excluded_with_renormalize(self) -> None:
        idx = _index()
        report = _fill(idx, 3, agreed=None)[-1]
        assert report.agreement_rate is None
        assert report.asi == pytest.approx(1.0)  # 权重归一化后稳定样本仍满分

    def test_agreement_false_lowers_asi(self) -> None:
        idx = _index()
        report = _fill(idx, 3, agreed=False)[-1]
        assert report.agreement_rate == pytest.approx(0.0)
        assert report.asi == pytest.approx(0.8)  # 0.4+0.2+0.2+0.2*0

    def test_custom_weights_applied(self) -> None:
        idx = _index(weights={"semantic": 0.7, "tool": 0.1, "path": 0.1, "agreement": 0.1})
        reports = [idx.record_interaction(_rec(text="多" if i % 2 == 0 else "空")) for i in range(3)]
        # 0.7*0 + 0.1*1*3 = 0.3
        assert reports[-1].asi == pytest.approx(0.3)


# ──────────────────────────────────────────────────────────────────────────────
# record 校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestRecordValidation:
    def test_invalid_scalar_fields(self) -> None:
        idx = _index()
        with pytest.raises(AgentStabilityError):
            idx.record_interaction(_rec(agent=""))
        with pytest.raises(AgentStabilityError):
            idx.record_interaction(_rec(agreed="yes"))
        with pytest.raises(AgentStabilityError):
            idx.record_interaction("not-a-record")

    def test_sequence_fields_must_be_str_tuple(self) -> None:
        idx = _index()
        with pytest.raises(AgentStabilityError):
            idx.record_interaction(_rec(tools=["scan"]))
        with pytest.raises(AgentStabilityError):
            idx.record_interaction(_rec(path=("ok", 1)))


# ──────────────────────────────────────────────────────────────────────────────
# embedder 异常（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestEmbedderFailClosed:
    def test_zero_or_empty_vector_raises(self) -> None:
        with pytest.raises(AgentStabilityError):
            _fill(_index(embedder=lambda t: (0.0, 0.0)), 3)
        with pytest.raises(AgentStabilityError):
            _fill(_index(embedder=lambda t: ()), 3)

    def test_dim_mismatch_raises(self) -> None:
        def bad_embedder(text: str) -> tuple[float, ...]:
            return (1.0, 0.0) if text == "多" else (1.0, 0.0, 0.0)

        idx = _index(embedder=bad_embedder)
        idx.record_interaction(_rec(text="多"))
        idx.record_interaction(_rec(text="空"))
        with pytest.raises(AgentStabilityError):
            idx.record_interaction(_rec(text="多"))

    def test_embedder_exception_wrapped(self) -> None:
        def boom(text: str) -> tuple[float, ...]:
            raise RuntimeError("model down")

        with pytest.raises(AgentStabilityError):
            _fill(_index(embedder=boom), 3)


# ──────────────────────────────────────────────────────────────────────────────
# 连续低窗告警 + gov_drift 事件
# ──────────────────────────────────────────────────────────────────────────────


class TestAlerting:
    def test_alert_after_three_consecutive_low_windows(self) -> None:
        events: list[DriftEvent] = []
        idx = _index(events)
        for i in range(5):  # 第3/4/5条 → 3次低窗评估
            idx.record_interaction(_rec(text="多" if i % 2 == 0 else "空"))
        assert len(events) == 1
        assert events[0].agent_id == "signal_analyst"
        assert events[0].consecutive_low == 3
        assert events[0].asi == pytest.approx(0.6)
        assert "连续" in events[0].reason
        assert idx.reports("signal_analyst")[-1].alerted is True

    def test_no_alert_before_streak_reached(self) -> None:
        events: list[DriftEvent] = []
        idx = _index(events)
        for i in range(4):  # 仅 2 次低窗评估
            idx.record_interaction(_rec(text="多" if i % 2 == 0 else "空"))
        assert events == []
        assert idx.consecutive_low("signal_analyst") == 2

    def test_streak_reset_by_good_window(self) -> None:
        events: list[DriftEvent] = []
        idx = _index(events)
        for i in range(4):  # 工具/路径交替 → 2 次低窗（asi=0.6）
            alt = i % 2 == 0
            idx.record_interaction(_rec(
                tools=("x", "y") if alt else ("scan", "rank"),
                path=("u", "v") if alt else ("observe", "infer"),
            ))
        _fill(idx, 1)  # 稳定交互滑入 → 混合窗分量 0.5 → asi=0.8 好窗重置
        assert idx.consecutive_low("signal_analyst") == 0
        assert events == []

    def test_alert_once_per_streak(self) -> None:
        events: list[DriftEvent] = []
        idx = _index(events)
        for i in range(7):  # 5 次连续低窗，仅第 3 次触发告警
            idx.record_interaction(_rec(text="多" if i % 2 == 0 else "空"))
        assert len(events) == 1
        assert idx.events == tuple(events)  # 事件同时落内存留痕
        assert idx.consecutive_low("signal_analyst") == 5

    def test_event_sink_exception_not_blocking(self) -> None:
        idx = AgentStabilityIndex(
            embedder=_embedder,
            clock=lambda: _T0,
            event_sink=lambda e: (_ for _ in ()).throw(RuntimeError("sink down")),
            window_size=3,
            alert_consecutive=3,
        )
        for i in range(5):
            idx.record_interaction(_rec(text="多" if i % 2 == 0 else "空"))
        assert len(idx.events) == 1  # 告警异常不阻断评估，事件仍留痕


# ──────────────────────────────────────────────────────────────────────────────
# 强制评估与查询
# ──────────────────────────────────────────────────────────────────────────────


class TestEvaluateAndQuery:
    def test_evaluate_partial_window(self) -> None:
        idx = _index(window_size=50)
        _fill(idx, 2)
        report = idx.evaluate("signal_analyst")
        assert report.window_size == 2
        assert report.asi == pytest.approx(1.0)

    def test_evaluate_fail_closed(self) -> None:
        idx = _index()
        with pytest.raises(AgentStabilityError):
            idx.evaluate("ghost")  # 未知 agent
        idx.record_interaction(_rec())
        with pytest.raises(AgentStabilityError):
            idx.evaluate("signal_analyst")  # 样本不足

    def test_empty_agent_id_query_raises(self) -> None:
        idx = _index()
        with pytest.raises(AgentStabilityError):
            idx.reports("")
        with pytest.raises(AgentStabilityError):
            idx.buffered("")
        with pytest.raises(AgentStabilityError):
            idx.consecutive_low("")

    def test_reports_isolated_per_agent(self) -> None:
        idx = _index()
        _fill(idx, 3)
        _fill(idx, 3, agent="t0_trader")
        assert len(idx.reports("signal_analyst")) == 1
        assert len(idx.reports("t0_trader")) == 1
        assert idx.buffered("ghost") == 0


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        def run() -> list[float]:
            idx = _index(window_size=3)
            out = []
            for i in range(5):
                report = idx.record_interaction(_rec(text="多" if i % 2 == 0 else "空", agreed=i % 2 == 0))
                if report is not None:
                    out.append(report.asi)
            return out

        assert run() == run()
