# [A_test] module_id: MOD-SIG-090 | layer=test | stability=volatile | safety=H | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-090 | docs/03_modules/_domain_signal/t0_trading_pipeline/blueprint.md
# [MODULE] tests.signal_ashare.test_t0_trading_pipeline
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] permanent

"""C-012 做T日内套利管线（MOD-SIG-090，B1-00191）施工验证测试。

覆盖：
- 硬约束：底仓自平衡（任意路径买量=卖量）、手数对齐、轮次上限、最小价差、配置校验；
- 信号→决策→执行→复盘全链路：V 型行情完成一轮、价差落账；
- 失败回滚：平衡腿失败→反向回滚；回滚再失败→升级留痕；
- 延迟预算：累计延迟超预算→不再开新轮，平衡腿仍闭合；
- 尾盘强制平衡：未闭合轮 EOD 强制闭合；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据+ executor 测试替身，无 DB 无券商。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.signal_ashare.t0_point_analyzer import (
    MinuteBar,
    T0AnalyzerConfig,
    T0Context,
)
from zephyr.signal_ashare.t0_trading_pipeline import (
    T0DayReport,
    T0Fill,
    T0OrderIntent,
    T0PipelineConfig,
    T0TradingPipeline,
)


def _ts(day_minute: int) -> str:
    base = 9 * 60 + 30 + day_minute
    return f"2026-08-25 {base // 60:02d}:{base % 60:02d}"


def _bars(closes: list[float], volume: float = 10000.0) -> list[MinuteBar]:
    bars = []
    for i, c in enumerate(closes):
        bars.append(MinuteBar(ts=_ts(i), open=c, high=c * 1.001, low=c * 0.999, close=c, volume=volume))
    return bars


def _v_closes() -> list[float]:
    up = [10.0 * (1.003**i) for i in range(30)]
    down = [up[-1] * (0.997**i) for i in range(1, 31)]
    return up + down


def _flat_closes() -> list[float]:
    return [10.0] * 40


def _analyzer_cfg() -> T0AnalyzerConfig:
    return T0AnalyzerConfig(lookback_bars=5, dev_sell_pct=0.5, dev_buy_pct=-0.5)


def _strict_analyzer_cfg() -> T0AnalyzerConfig:
    return T0AnalyzerConfig(
        lookback_bars=5,
        dev_sell_pct=50.0,
        dev_buy_pct=-50.0,
        pullback_min_excursion_pct=50.0,
        enable_deviation_buy=False,
        enable_divergence_buy=False,
    )


def _ctx() -> T0Context:
    return T0Context(symbol="600000.SH", prev_close=10.0)


class _Executor:
    """executor 测试替身：记录意图与成交，按脚本成交。"""

    def __init__(self, latency_ms: float = 10.0, fail_on: set[int] | None = None) -> None:
        self.intents: list[T0OrderIntent] = []
        self._filled: list[bool] = []
        self.latency_ms = latency_ms
        self.fail_on = fail_on or set()

    def __call__(self, intent: T0OrderIntent) -> T0Fill:
        idx = len(self.intents)
        self.intents.append(intent)
        if idx in self.fail_on:
            self._filled.append(False)
            return T0Fill(filled=False, price=intent.price, latency_ms=self.latency_ms, note="拒绝")
        self._filled.append(True)
        return T0Fill(filled=True, price=intent.price, latency_ms=self.latency_ms)

    def net_volume(self) -> int:
        """已成交腿的净量（未成交意图不计）。"""
        return sum((i.volume if i.side == "BUY" else -i.volume) for i, f in zip(self.intents, self._filled) if f)


def _cfg(**kw) -> T0PipelineConfig:
    base = {
        "base_position": 1000,
        "lot_size": 100,
        "min_spread_pct": 0.1,
        "max_rounds": 1,
        "trade_volume": 300,
        "latency_budget_ms": 500.0,
        "signal_confidence_min": 0.0,
    }
    base.update(kw)
    return T0PipelineConfig(**base)


class TestConfigValidation:
    @pytest.mark.parametrize(
        "kw",
        [
            {"trade_volume": 1200},  # 单腿>底仓
            {"trade_volume": 150},  # 手数未对齐
            {"max_rounds": 0},
            {"min_spread_pct": 0.0},
            {"latency_budget_ms": 0.0},
            {"base_position": 0},
        ],
    )
    def test_invalid_config_fail_closed(self, kw: dict) -> None:
        good = {
            "base_position": 1000,
            "lot_size": 100,
            "min_spread_pct": 0.1,
            "max_rounds": 1,
            "trade_volume": 300,
            "latency_budget_ms": 500.0,
        }
        good.update(kw)
        with pytest.raises(ValueError):
            T0PipelineConfig(**good)

    def test_executor_required(self) -> None:
        with pytest.raises(ValueError):
            T0TradingPipeline(_cfg(), None)  # type: ignore[arg-type]


class TestHappyPath:
    def test_one_round_completed_and_balanced(self) -> None:
        ex = _Executor()
        pipe = T0TradingPipeline(_cfg(), ex)
        rep = pipe.run_day(_bars(_v_closes()), _ctx(), _analyzer_cfg())
        assert isinstance(rep, T0DayReport)
        assert rep.completed_rounds == 1
        assert ex.net_volume() == 0  # 底仓自平衡
        r = rep.rounds[0]
        assert r.status == "completed"
        assert r.volume == 300
        assert r.spread_pct > 0
        assert rep.realized_spread_pct > 0

    def test_max_rounds_respected(self) -> None:
        ex = _Executor()
        pipe = T0TradingPipeline(_cfg(max_rounds=1), ex)
        # 双 V 也只开一轮
        closes = _v_closes() + _v_closes()
        rep = pipe.run_day(_bars(closes), _ctx(), _analyzer_cfg())
        assert rep.completed_rounds <= 1


class TestFailureRollback:
    def test_close_leg_failure_rolls_back(self) -> None:
        ex = _Executor(fail_on={1})  # 第二腿（平衡腿）失败
        pipe = T0TradingPipeline(_cfg(), ex)
        rep = pipe.run_day(_bars(_v_closes()), _ctx(), _analyzer_cfg())
        assert rep.completed_rounds == 0
        assert ex.net_volume() == 0  # 回滚恢复平衡
        assert any(r.rolled_back for r in rep.rounds)

    def test_rollback_failure_escalates(self) -> None:
        ex = _Executor(fail_on={1, 2})  # 平衡腿+回滚腿都失败
        pipe = T0TradingPipeline(_cfg(), ex)
        rep = pipe.run_day(_bars(_v_closes()), _ctx(), _analyzer_cfg())
        assert rep.escalation is True
        assert any("回滚失败" in n for n in rep.notes)


class TestLatencyBudget:
    def test_budget_exhaustion_aborts_new_rounds(self) -> None:
        ex = _Executor(latency_ms=600.0)  # 单腿即超 500 预算
        pipe = T0TradingPipeline(_cfg(latency_budget_ms=500.0), ex)
        rep = pipe.run_day(_bars(_v_closes()), _ctx(), _analyzer_cfg())
        assert rep.aborted is True
        assert ex.net_volume() == 0  # 平衡不变量仍成立
        assert any("预算" in n for n in rep.notes)


class TestEodForcedBalance:
    def test_open_round_force_closed_at_eod(self) -> None:
        ex = _Executor()
        pipe = T0TradingPipeline(_cfg(), ex)
        closes = [10.0 * (1.003**i) for i in range(60)]  # 只涨不跌
        rep = pipe.run_day(_bars(closes), _ctx(), _analyzer_cfg())
        assert ex.net_volume() == 0
        statuses = {r.status for r in rep.rounds}
        assert statuses <= {"completed", "forced_closed"}
        assert any("尾盘" in n for n in rep.notes) or statuses == {"completed"}


class TestNoSignal:
    def test_flat_day_no_round(self) -> None:
        ex = _Executor()
        pipe = T0TradingPipeline(_cfg(), ex)
        rep = pipe.run_day(_bars(_flat_closes()), _ctx(), _strict_analyzer_cfg())
        assert rep.completed_rounds == 0
        assert ex.intents == []


class TestContract:
    def test_frozen_and_json(self) -> None:
        ex = _Executor()
        pipe = T0TradingPipeline(_cfg(), ex)
        rep = pipe.run_day(_bars(_v_closes()), _ctx(), _analyzer_cfg())
        with pytest.raises(dataclasses.FrozenInstanceError):
            rep.completed_rounds = 99  # type: ignore[misc]
        json.dumps(rep.to_dict(), ensure_ascii=False)

    def test_empty_bars_rejected(self) -> None:
        pipe = T0TradingPipeline(_cfg(), _Executor())
        with pytest.raises(ValueError):
            pipe.run_day([], _ctx(), _analyzer_cfg())
