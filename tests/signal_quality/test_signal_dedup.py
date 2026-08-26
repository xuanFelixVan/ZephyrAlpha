# [BLUEPRINT] MOD-SIGQC-003 | docs/03_modules/_domain_signal_quality/signal_dedup/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIGQC-003 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_quality.test_signal_dedup
# [TESTS] src/zephyr/signal_quality/signal_dedup.py
"""MOD-SIGQC-003 单元测试：signal_dedup 信号去重器。

蓝图验收（B11-02594/CAND-SIGQC-002，A7 技能 signal-dedup）：
指纹四元组（标的/方向/逻辑标签/参数桶）+ 相似度>0.9 合并（保留最高置信度）+
时间窗去重（默认当日）+ 去重决策落审计回调供串谋检测复查。
审计 sink 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_quality.signal_dedup",
    reason="signal_dedup not importable",
)

from zephyr.signal_quality.signal_dedup import (  # noqa: E402
    DedupAction,
    DedupSignal,
    SignalDedup,
    SignalDedupError,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 26, 10, 30, 0)


def _signal(
    signal_id: str = "sig-1",
    *,
    symbol: str = "600519.SH",
    direction: str = "long",
    logic_tag: str = "value_reversal",
    param_bucket: str = "lookback20",
    confidence: float = 0.8,
    emitted_at: datetime.datetime = _T0,
) -> DedupSignal:
    return DedupSignal(
        signal_id=signal_id,
        symbol=symbol,
        direction=direction,
        logic_tag=logic_tag,
        param_bucket=param_bucket,
        confidence=confidence,
        emitted_at=emitted_at,
    )


def _dedup(audit: list | None = None, **kwargs) -> SignalDedup:
    return SignalDedup(
        clock=lambda: _T0,
        audit_sink=(lambda d: audit.append(d)) if audit is not None else None,
        **kwargs,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 指纹与保留/合并（正常路径）
# ──────────────────────────────────────────────────────────────────────────────


class TestFingerprint:
    def test_fingerprint_tuple(self) -> None:
        sig = _signal()
        assert SignalDedup.fingerprint_of(sig) == (
            "600519.SH",
            "long",
            "value_reversal",
            "lookback20",
        )

    def test_new_signal_kept(self) -> None:
        d = _dedup()
        decision = d.ingest(_signal("sig-1"))
        assert decision.action is DedupAction.KEPT_NEW
        assert decision.representative_id == "sig-1"
        assert decision.matched_signal_id is None
        assert [s.signal_id for s in d.kept_signals()] == ["sig-1"]
        assert not d.is_merged("sig-1")

    def test_distinct_fingerprints_coexist(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1", symbol="600519.SH"))
        d.ingest(_signal("sig-2", symbol="000001.SZ"))
        assert {s.signal_id for s in d.kept_signals()} == {"sig-1", "sig-2"}


class TestMerge:
    def test_same_fingerprint_merges_existing_kept(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1", confidence=0.9))
        decision = d.ingest(_signal("sig-2", confidence=0.7, emitted_at=_T1))
        assert decision.action is DedupAction.MERGED_EXISTING_KEPT
        assert decision.representative_id == "sig-1"
        assert decision.matched_signal_id == "sig-1"
        assert decision.similarity == 1.0
        assert d.is_merged("sig-2")
        assert [s.signal_id for s in d.kept_signals()] == ["sig-1"]

    def test_higher_confidence_new_replaces_representative(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1", confidence=0.7))
        decision = d.ingest(_signal("sig-2", confidence=0.95, emitted_at=_T1))
        assert decision.action is DedupAction.MERGED_NEW_KEPT
        assert decision.representative_id == "sig-2"
        assert d.is_merged("sig-1")
        kept = d.kept_signals()
        assert [s.signal_id for s in kept] == ["sig-2"]
        assert kept[0].confidence == 0.95  # 合并留最高置信度

    def test_equal_confidence_first_arrival_wins(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1", confidence=0.8))
        decision = d.ingest(_signal("sig-2", confidence=0.8, emitted_at=_T1))
        assert decision.action is DedupAction.MERGED_EXISTING_KEPT
        assert decision.representative_id == "sig-1"

    def test_three_of_four_match_below_default_threshold(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1"))
        # 仅 param_bucket 不同 → 相似度 0.75，不超默认 0.9
        decision = d.ingest(_signal("sig-2", param_bucket="lookback60", emitted_at=_T1))
        assert decision.action is DedupAction.KEPT_NEW
        assert len(d.kept_signals()) == 2

    def test_threshold_strictly_greater(self) -> None:
        # 阈值 0.75 时 3/4 匹配（=0.75）不合并——判定为严格大于
        d = _dedup(similarity_threshold=0.75)
        d.ingest(_signal("sig-1"))
        decision = d.ingest(_signal("sig-2", param_bucket="lookback60", emitted_at=_T1))
        assert decision.action is DedupAction.KEPT_NEW

    def test_custom_threshold_merges_partial_match(self) -> None:
        d = _dedup(similarity_threshold=0.7)
        d.ingest(_signal("sig-1", confidence=0.9))
        decision = d.ingest(_signal("sig-2", param_bucket="lookback60", confidence=0.6, emitted_at=_T1))
        assert decision.action is DedupAction.MERGED_EXISTING_KEPT
        assert decision.similarity == 0.75


class TestTimeWindow:
    def test_outside_window_not_merged(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1", emitted_at=_T0))
        far = _signal("sig-2", emitted_at=_T0 + datetime.timedelta(days=2))
        decision = d.ingest(far)
        assert decision.action is DedupAction.KEPT_NEW
        assert len(d.kept_signals()) == 2

    def test_window_boundary_merges(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1", confidence=0.9, emitted_at=_T0))
        edge = _signal("sig-2", confidence=0.6, emitted_at=_T0 + datetime.timedelta(days=1))
        decision = d.ingest(edge)  # |差| == 窗长，仍在窗内
        assert decision.action is DedupAction.MERGED_EXISTING_KEPT

    def test_custom_window(self) -> None:
        d = _dedup(window=datetime.timedelta(hours=1))
        d.ingest(_signal("sig-1", emitted_at=_T0))
        decision = d.ingest(_signal("sig-2", emitted_at=_T0 + datetime.timedelta(hours=2)))
        assert decision.action is DedupAction.KEPT_NEW


# ──────────────────────────────────────────────────────────────────────────────
# 审计与确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestAudit:
    def test_every_decision_audited(self) -> None:
        audit: list = []
        d = _dedup(audit)
        d.ingest(_signal("sig-1", confidence=0.9))
        d.ingest(_signal("sig-2", confidence=0.6, emitted_at=_T1))
        d.ingest(_signal("sig-3", symbol="000001.SZ", emitted_at=_T1))
        assert [x.action for x in audit] == [
            DedupAction.KEPT_NEW,
            DedupAction.MERGED_EXISTING_KEPT,
            DedupAction.KEPT_NEW,
        ]
        assert audit[1].fingerprint == ("600519.SH", "long", "value_reversal", "lookback20")

    def test_audit_sink_failure_not_blocking(self) -> None:
        def _bad_sink(_decision) -> None:
            raise RuntimeError("审计通道故障")

        d = SignalDedup(clock=lambda: _T0, audit_sink=_bad_sink)
        decision = d.ingest(_signal("sig-1"))  # 审计失败不阻断
        assert decision.action is DedupAction.KEPT_NEW
        assert len(d.decisions()) == 1

    def test_decisions_sorted_deterministic(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-b", symbol="000001.SZ", emitted_at=_T1))
        d.ingest(_signal("sig-a", emitted_at=_T0))
        ids = [x.signal_id for x in d.decisions()]
        assert ids == ["sig-a", "sig-b"]  # 按 (decided_at, signal_id) 排序

    def test_kept_signals_sorted_by_emission(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-late", symbol="000001.SZ", emitted_at=_T1))
        d.ingest(_signal("sig-early", emitted_at=_T0))
        ids = [s.signal_id for s in d.kept_signals()]
        assert ids == ["sig-early", "sig-late"]

    def test_deterministic_replay(self) -> None:
        seq = [
            _signal("sig-1", confidence=0.9),
            _signal("sig-2", confidence=0.6, emitted_at=_T1),
            _signal("sig-3", symbol="000001.SZ", emitted_at=_T1),
            _signal("sig-4", confidence=0.99, emitted_at=_T1),
        ]
        d1, d2 = _dedup(), _dedup()
        r1 = [d1.ingest(s) for s in seq]
        r2 = [d2.ingest(s) for s in seq]
        assert [(x.action, x.representative_id) for x in r1] == [
            (x.action, x.representative_id) for x in r2
        ]
        assert [s.signal_id for s in d1.kept_signals()] == [
            s.signal_id for s in d2.kept_signals()
        ]


# ──────────────────────────────────────────────────────────────────────────────
# Fail-Closed 分支
# ──────────────────────────────────────────────────────────────────────────────


class TestFailClosed:
    def test_empty_signal_id_raises(self) -> None:
        with pytest.raises(SignalDedupError):
            _dedup().ingest(_signal(""))

    def test_duplicate_signal_id_raises(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1", symbol="000001.SZ"))
        with pytest.raises(SignalDedupError):
            d.ingest(_signal("sig-1", symbol="600519.SH"))

    def test_merged_signal_id_reuse_raises(self) -> None:
        d = _dedup()
        d.ingest(_signal("sig-1", confidence=0.9))
        d.ingest(_signal("sig-2", confidence=0.6))  # 并入 sig-1
        with pytest.raises(SignalDedupError):
            d.ingest(_signal("sig-2", symbol="000001.SZ"))

    def test_empty_fingerprint_fields_raise(self) -> None:
        with pytest.raises(SignalDedupError):
            _dedup().ingest(_signal("sig-1", symbol=""))
        with pytest.raises(SignalDedupError):
            _dedup().ingest(_signal("sig-1", direction=""))
        with pytest.raises(SignalDedupError):
            _dedup().ingest(_signal("sig-1", logic_tag=""))

    def test_confidence_out_of_range_raises(self) -> None:
        with pytest.raises(SignalDedupError):
            _dedup().ingest(_signal("sig-1", confidence=-0.1))
        with pytest.raises(SignalDedupError):
            _dedup().ingest(_signal("sig-1", confidence=1.1))

    def test_invalid_threshold_constructor_raises(self) -> None:
        with pytest.raises(SignalDedupError):
            _dedup(similarity_threshold=0.0)
        with pytest.raises(SignalDedupError):
            _dedup(similarity_threshold=1.01)

    def test_invalid_window_constructor_raises(self) -> None:
        with pytest.raises(SignalDedupError):
            _dedup(window=datetime.timedelta(0))
        with pytest.raises(SignalDedupError):
            _dedup(window=datetime.timedelta(days=-1))
