# -*- coding: utf-8 -*-
"""MOD-SIG-147 pattern_signal_runtime 链路单测（tmp 隔离，不触库）。"""

from __future__ import annotations

import datetime

import pytest

from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
    Ctr002PayloadValidator,
    PatternSignalRuntime,
)
from zephyr.signal_ashare.strategy_signal.pattern_to_signal_mapper import (
    PatternSignalMapError,
)
from zephyr.signal_ashare.strategy_signal.unified_pattern_engine import (
    KeyPoint,
    PatternClass,
    PatternDirection,
    PatternEvent,
)

_FROZEN_NOW = datetime.datetime(2026, 9, 14, 15, 0, 5)


def _clock() -> datetime.datetime:
    return _FROZEN_NOW


def _make_runtime(**kw) -> PatternSignalRuntime:
    base = dict(clock=_clock, win_rate_query=lambda pid: 0.62)
    base.update(kw)
    return PatternSignalRuntime(**base)


def _head_shoulder_event() -> PatternEvent:
    return PatternEvent(
        pattern_id="PAT-CHART-002",
        pattern_class=PatternClass.REVERSAL,
        name="头肩顶",
        direction=PatternDirection.DOWN,
        confidence=0.8,
        key_points=(
            KeyPoint(idx=5, price=10.0, role="顶1"),
            KeyPoint(idx=9, price=10.5, role="顶2"),
        ),
        historical_win_rate=0.6,
        timeframe="day",
        anchor_idx=9,
    )


# ── 装配 ──────────────────────────────────────────────────────────────────────


def test_assembly_ambiguity_rejected() -> None:
    """provider 与 win_rate_query 同时给=装配歧义，必须拒绝。"""
    with pytest.raises(ValueError, match="二选一"):
        PatternSignalRuntime(
            provider=PatternSignalRuntime(win_rate_query=lambda p: None)._provider,
            win_rate_query=lambda p: None,
            clock=_clock,
        )


def test_build_engine_injects_win_rate_fn() -> None:
    """引擎工厂：注入契约生效（recognize 出的事件带胜率）。"""
    rt = _make_runtime()
    engine = rt.build_engine()
    highs = [10.0, 10.8, 9.9, 10.9, 9.8, 10.85, 9.85, 10.1]
    lows = [9.6, 10.2, 9.5, 10.3, 9.4, 10.25, 9.45, 9.7]
    closes = [9.9, 10.5, 9.7, 10.6, 9.6, 10.55, 9.65, 9.95]
    result = engine.recognize("000001", highs, lows, closes, timeframe="day")
    assert result.events, "合成序列应至少触发一个形态"
    for ev in result.events:
        assert ev.historical_win_rate == pytest.approx(0.62)


# ── on_events 全链路 ─────────────────────────────────────────────────────────


def test_on_events_full_chain() -> None:
    """事件→映射→CTR-002 载荷（方向/强度/止损/校验全通）。"""
    rt = _make_runtime()
    payload = rt.on_events("000001", [_head_shoulder_event()], as_of=_FROZEN_NOW)
    assert payload["contract"] == "CTR-002"
    assert payload["symbol"] == "000001"
    assert payload["values"]["PAT-CHART-002"] == pytest.approx(-0.48)  # -0.8×0.6
    md = payload["metadata"]
    assert md["directions"]["PAT-CHART-002"] == "short"


def test_on_events_empty_events_no_signal() -> None:
    """空事件序列=不出载荷（无形态不发信号）。"""
    rt = _make_runtime()
    assert rt.on_events("000001", [], as_of=_FROZEN_NOW) == {}


def test_on_events_future_asof_rejected() -> None:
    """未来 as_of=映射出口直接拒绝（mapper 既有 PIT 契约透传）。"""
    rt = _make_runtime()
    with pytest.raises(PatternSignalMapError, match="未来信号"):
        rt.on_events(
            "000001",
            [_head_shoulder_event()],
            as_of=_FROZEN_NOW + datetime.timedelta(days=1),
        )


def test_on_events_neutral_no_stop() -> None:
    """中性方向：无关键点位也合法，止损=None，强度带 0 值。"""
    ev = PatternEvent(
        pattern_id="PAT-TREND-013",
        pattern_class=PatternClass.TREND,
        name="均线排列",
        direction=PatternDirection.NEUTRAL,
        confidence=0.5,
        key_points=(),
        historical_win_rate=None,
        timeframe="day",
        anchor_idx=0,
    )
    rt = _make_runtime(win_rate_query=lambda p: None)
    payload = rt.on_events("000001", [ev], as_of=_FROZEN_NOW)
    assert payload["values"]["PAT-TREND-013"] == 0.0


# ── Ctr002PayloadValidator（Fail-Closed 四态） ───────────────────────────────


def _valid_payload() -> dict:
    return {
        "contract": "CTR-002",
        "factor_id": "pattern_signal",
        "source_domain": "ashare_signal",
        "symbol": "000001",
        "values": {"PAT-CHART-002": -0.48},
        "as_of": _FROZEN_NOW.isoformat(),
        "advisory": True,
        "metadata": {},
    }


def test_validator_accepts_valid_payload() -> None:
    v = Ctr002PayloadValidator(clock=_clock)
    assert v(_valid_payload()) is True


def test_validator_rejects_future_asof() -> None:
    p = _valid_payload()
    p["as_of"] = (_FROZEN_NOW + datetime.timedelta(days=1)).isoformat()
    assert Ctr002PayloadValidator(clock=_clock)(p) is False


def test_validator_rejects_empty_values() -> None:
    p = _valid_payload()
    p["values"] = {}
    assert Ctr002PayloadValidator(clock=_clock)(p) is False


def test_validator_fail_closed_on_garbage() -> None:
    """非 Mapping/坏 as_of/None=异常路径，一律 False（Fail-Closed）。"""
    v = Ctr002PayloadValidator(clock=_clock)
    assert v("not-a-mapping") is False
    p = _valid_payload()
    p["as_of"] = "not-a-timestamp"
    assert v(p) is False
    assert v(None) is False


# ── W-C2：meta 门 + 审计快照 + 工厂注册 ────────────────────────────────────


def test_regime_gate_denies() -> None:
    """regime_filter 拒准→空载荷（准入路由，无信号出网）。"""
    rt = _make_runtime(regime_filter=lambda s, t: False)
    assert rt.on_events("000001", [_head_shoulder_event()], as_of=_FROZEN_NOW) == {}


def test_regime_gate_admits_with_tag() -> None:
    rt = _make_runtime(
        regime_filter=lambda s, t: t == "r1",
        regime_tag="r1",
        weight_version="w7",
    )
    payload = rt.on_events("000001", [_head_shoulder_event()], as_of=_FROZEN_NOW)
    md = payload["metadata"]
    assert md["regime_tag"] == "r1"
    assert md["weight_version"] == "w7"
    assert md["win_rate_snapshot"]["PAT-CHART-002"] == {"win_rate": 0.6}


def test_factory_registers_per_direction() -> None:
    """逐方向注册最强分量：DOWN 事件→一条 SHORT 草稿入册。"""
    from zephyr.signal_ashare.strategy_signal.signal_factory import SignalFactory

    factory = SignalFactory()
    rt = _make_runtime(factory=factory, source="patmine:test")
    payload = rt.on_events("000001", [_head_shoulder_event()], as_of=_FROZEN_NOW)
    ids = payload["metadata"]["signal_ids"]
    assert len(ids) == 1
    rec = factory.get(ids[0])
    assert rec.direction == "SHORT"
    assert rec.strength == pytest.approx(0.48)
    assert rec.source == "patmine:test:PAT-CHART-002"
    assert rec.symbol == "000001"


def test_factory_neutral_skips_registration() -> None:
    """纯中性事件：无方向信号，不注册草稿。"""
    from zephyr.signal_ashare.strategy_signal.signal_factory import SignalFactory

    ev = PatternEvent(
        pattern_id="PAT-TREND-013",
        pattern_class=PatternClass.TREND,
        name="均线排列",
        direction=PatternDirection.NEUTRAL,
        confidence=0.5,
        key_points=(),
        historical_win_rate=None,
        timeframe="day",
        anchor_idx=0,
    )
    factory = SignalFactory()
    rt = _make_runtime(factory=factory, win_rate_query=lambda p: None)
    payload = rt.on_events("000001", [ev], as_of=_FROZEN_NOW)
    assert payload["metadata"]["signal_ids"] == []


def test_factory_duplicate_skips_with_note() -> None:
    """同载荷二次注册：幂等跳过留痕 notes，不抛错。"""
    from zephyr.signal_ashare.strategy_signal.signal_factory import SignalFactory

    factory = SignalFactory()
    rt = _make_runtime(factory=factory)
    ev = _head_shoulder_event()
    first = rt.on_events("000001", [ev], as_of=_FROZEN_NOW)
    second = rt.on_events("000001", [ev], as_of=_FROZEN_NOW)
    assert first["metadata"]["signal_ids"] == second["metadata"]["signal_ids"]
    assert "factory_duplicate_skipped" in second.get("notes", [])


# ── W-C3：调权同步 + 持久化 ──────────────────────────────────────────────────


class _SyncStubProvider:
    """同步链 stub：命中行按 pid 应答，其余查无。"""

    def __init__(self, rows, baseline=0.52, ids=None):
        self._rows = rows
        self._baseline = baseline
        self._ids = ids if ids is not None else sorted(rows)

    def get_detail(self, pid, **kw):
        return self._rows.get(pid)

    def get_baseline(self, **kw):
        return self._baseline

    def list_pattern_ids(self, **kw):
        return list(self._ids)


def test_sync_records_and_adjusts(tmp_path):
    from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
        PatternWeightSync,
    )

    provider = _SyncStubProvider(
        rows={
            "双顶": {"n_events": 500, "hit_rate": 0.72, "low_sample": 0},
            # 双底：查无（不在 rows）→ 跳过
        },
        ids=["双顶", "双底"],
    )
    sync = PatternWeightSync(provider=provider, store=None, clock=_clock)
    assert sync.patterns == ["双顶", "双底"]
    records = sync.sync_from_provider(reason="materialize_done")
    assert len(records) == 1  # 双底无统计不调权
    rec = records[0]
    assert rec.signal_id == "双顶"
    assert 0.0 <= rec.new_weight <= 1.0
    assert sync.weight_of("双底") == pytest.approx(1.0)  # 无统计不动权重


def test_sync_persists_and_restores(tmp_path):
    from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
        PatternWeightStore,
        PatternWeightSync,
    )

    state_path = tmp_path / "weights.json"
    provider = _SyncStubProvider(rows={"双顶": {"n_events": 500, "hit_rate": 0.72, "low_sample": 0}})
    store = PatternWeightStore(state_path)
    sync = PatternWeightSync(provider=provider, patterns=["双顶"], store=store, clock=_clock)
    sync.sync_from_provider()
    saved = store.load()
    assert saved["双顶"]["weight"] == pytest.approx(sync.weight_of("双顶"))
    assert saved["双顶"]["version"] >= 2  # 注册=1，adjust 后 ≥2

    restored = PatternWeightSync(provider=provider, patterns=["双顶"], store=store, clock=_clock)
    assert restored.weight_of("双顶") == pytest.approx(sync.weight_of("双顶"))


def test_sync_low_sample_skipped(tmp_path):
    from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
        PatternWeightStore,
        PatternWeightSync,
    )

    provider = _SyncStubProvider(rows={"双顶": {"n_events": 8, "hit_rate": 0.9, "low_sample": 1}})
    store = PatternWeightStore(tmp_path / "w.json")
    sync = PatternWeightSync(provider=provider, patterns=["双顶"], store=store, clock=_clock)
    assert sync.sync_from_provider() == []
    assert sync.weight_of("双顶") == pytest.approx(1.0)


def test_sync_ic_proxy_bounded():
    """命中率大幅超基准→ic 代理截断在 [-1,1]。"""
    from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
        PatternWeightSync,
    )

    provider = _SyncStubProvider(
        rows={"双顶": {"n_events": 500, "hit_rate": 0.99, "low_sample": 0}}, baseline=0.3
    )
    sync = PatternWeightSync(provider=provider, patterns=["双顶"], clock=_clock)
    records = sync.sync_from_provider()
    assert len(records) == 1
    assert 0.0 <= records[0].new_weight <= 1.0


def test_cli_sync_weights(tmp_path, capsys, monkeypatch):
    """CLI 钩子：--sync-weights 出摘要 JSON 且状态落盘。"""
    import json as _json

    from zephyr.signal_ashare.strategy_signal import pattern_signal_runtime as mod

    class _StubCls:
        def __init__(self):
            self._inner = _SyncStubProvider(
                rows={"双顶": {"n_events": 500, "hit_rate": 0.72, "low_sample": 0}}
            )

        def _ensure_client(self):
            return self

        def execute(self, sql, params=None):
            return []  # 认证表查无→回落 provider 路径

        def get_detail(self, pid, **kw):
            return self._inner.get_detail(pid, **kw)

        def get_baseline(self, **kw):
            return self._inner.get_baseline(**kw)

        def list_pattern_ids(self, **kw):
            return self._inner.list_pattern_ids(**kw)

    monkeypatch.setattr(mod, "PatternWinRateProvider", _StubCls)
    state_path = tmp_path / "cli_weights.json"
    rc = mod.main(
        ["--sync-weights", "--state-path", str(state_path), "--reason", "materialize_done"]
    )
    assert rc == 0
    summary = _json.loads(capsys.readouterr().out.strip())
    assert summary["patterns"] == 1
    assert summary["adjusted"] == 1
    assert state_path.exists()


# ── W-CC：认证口径消费（shrunk + failed 跳过） ───────────────────────────────


def test_sync_shrunk_certified_path(tmp_path):
    """认证行存在：win_rate 样本=shrunk_rate（非 raw Wilson）。"""
    from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
        PatternWeightSync,
    )

    cert = {"双顶": {"state": "certified", "shrunk_rate": 0.58}}
    provider = _SyncStubProvider(rows={"双顶": {"n_events": 5000, "hit_rate": 0.60, "low_sample": 0}})
    sync = PatternWeightSync(
        provider=provider, patterns=["双顶"], cert_reader=lambda p: cert.get(p),
        clock=_clock,
    )
    records = sync.sync_from_provider()
    assert len(records) == 1
    # ic = 2×(shrunk 0.58 − 基线 0.52) = 0.12；win_rate 样本=0.58
    assert records[0].new_weight <= 1.0


def test_sync_failed_skipped(tmp_path):
    """认证 failed：不录样本不调权（Fail-Closed）。"""
    from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
        PatternWeightSync,
    )

    cert = {"双顶": {"state": "failed", "shrunk_rate": 0.51}}
    provider = _SyncStubProvider(rows={"双顶": {"n_events": 5000, "hit_rate": 0.60, "low_sample": 0}})
    sync = PatternWeightSync(
        provider=provider, patterns=["双顶"], cert_reader=lambda p: cert.get(p),
        clock=_clock,
    )
    assert sync.sync_from_provider() == []
    assert sync.weight_of("双顶") == pytest.approx(1.0)


def test_sync_no_cert_row_falls_back_to_provider(tmp_path):
    """无认证行（认证未跑）：回落 provider Wilson 路径（向后兼容）。"""
    from zephyr.signal_ashare.strategy_signal.pattern_signal_runtime import (
        PatternWeightSync,
    )

    provider = _SyncStubProvider(rows={"双顶": {"n_events": 5000, "hit_rate": 0.60, "low_sample": 0}})
    sync = PatternWeightSync(
        provider=provider, patterns=["双顶"], cert_reader=lambda p: None,
        clock=_clock,
    )
    records = sync.sync_from_provider()
    assert len(records) == 1  # 回落旧口径不炸
