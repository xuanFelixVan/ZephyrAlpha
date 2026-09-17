# [BLUEPRINT] MOD-BT-039 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_c4_limit_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; numpy; pandas; scripts.backtest.translated._c4_engine
# [CONSUMERS] MODIFY-GUARD: _c4_engine 涨跌停可成交性闸（E7 引擎洞修复）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] E7 反例必须真红：601162@2024-09-25 与 000016@2025-04-10 涨停封死收盘
#   买入成交（引擎洞实证，lane E 实锤）——闸开后这两笔必须被拦（目标权重不生效）；
#   判定单位对齐原始价（kline_daily close vs stk_limit limit_up，禁 hfq 直比）；
#   跌停封死禁卖出（合成掩码单元）；闸原料缺失 fail-open 不编造可成交性；
#   gate_limits=False 必须复现旧行为（洞仍在=反例对照通道）。
# [MODIFY-GUARD] scripts/backtest/translated/_c4_engine.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/backtest/test_c4_limit_gate.py
# [TTL] permanent
"""E7 涨跌停可成交性闸守护测试——两笔真实引擎洞反例必拦 + 闸语义单元。

真实反例两笔（只读 CH，lane E e7_result.json 实锤）：
  - CAND-4440d07f973f 于 2024-09-25 买入 601162，收盘=涨停价 3.30（封死）；
  - CAND-e2e7f033d97c 于 2025-04-10 买入 000016，收盘=涨停价 4.64。
修复前：两笔照常成交（洞）；修复后：目标权重被闸拦下（绿）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_REPO = Path(__file__).resolve().parents[2]
_TRANSLATED = _REPO / "scripts" / "backtest" / "translated"
sys.path.insert(0, str(_TRANSLATED))

from _c4_engine import (  # noqa: E402
    _load_seal_masks,
    apply_fillability_gate,
    daily_net_returns,
    run_backtest,
)

REAL_CASES = [
    ("601162", "2024-09-25", 3.30),   # 924 暴动窗次日，封涨停
    ("000016", "2025-04-10", 4.64),   # 关税恐慌窗，封涨停
]


@pytest.mark.parametrize("symbol,seal_date,limit_price", REAL_CASES)
def test_seal_masks_contain_real_counterexamples(symbol: str, seal_date: str, limit_price: float) -> None:
    """封板掩码必须命中两笔真实引擎洞反例（原始价口径，只读 CH）。"""
    idx = pd.bdate_range("2024-09-20", "2025-04-15")
    up, down = _load_seal_masks(idx, pd.Index([symbol]))
    assert bool(up.loc[pd.Timestamp(seal_date), symbol]) is True, (
        f"{symbol}@{seal_date} 涨停封板未被掩码命中——闸原料/单位对齐坏了（E7 反例失明）"
    )
    # 阳性对照：掩码不是全 True（否则闸=全面禁买，无鉴别力）
    other_days = up.index[up.index != pd.Timestamp(seal_date)]
    assert bool(up.loc[other_days, symbol].any()) and not bool(up.loc[other_days, symbol].all())
    # 反例当日不处于同时封跌停的病态（涨跌停互斥的正面校验）
    assert not bool(down.loc[pd.Timestamp(seal_date), symbol])


@pytest.mark.parametrize("symbol,seal_date,limit_price", REAL_CASES)
def test_gate_blocks_real_limit_up_buy(symbol: str, seal_date: str, limit_price: float) -> None:
    """闸后两笔真实反例的买入目标权重必须不生效（变红=被拦）；gate_limits=False 复现洞。"""
    idx = pd.bdate_range("2024-09-22", "2025-04-15")
    w = pd.DataFrame(0.0, index=idx, columns=[symbol])
    w.loc[pd.Timestamp(seal_date):, symbol] = 1.0  # 封板日起全额买入目标

    gated = apply_fillability_gate(w)
    assert float(gated.loc[pd.Timestamp(seal_date), symbol]) == 0.0, (
        f"{symbol}@{seal_date} 涨停封死仍建立仓位——E7 引擎洞未修（此断言必红）"
    )

    ungated = apply_fillability_gate(w, gate_limits=False)
    assert float(ungated.loc[pd.Timestamp(seal_date), symbol]) == 1.0, "gate_limits=False 必须复现旧行为（反例对照通道）"


def test_gate_blocks_limit_down_sell_synthetic(monkeypatch: pytest.MonkeyPatch) -> None:
    """跌停封死禁卖出（合成掩码，不触 CH）：持仓被锁、目标减仓不生效。"""
    idx = pd.bdate_range("2026-01-05", periods=6)
    cols = ["600000"]

    def fake_masks(index: pd.DatetimeIndex, columns: pd.Index):
        up = pd.DataFrame(False, index=index, columns=columns)
        down = pd.DataFrame(False, index=index, columns=columns)
        down.loc[idx[2], columns[0]] = True  # 第 3 日封跌停
        return up, down

    monkeypatch.setattr(sys.modules["_c4_engine"], "_load_seal_masks", fake_masks)
    w = pd.DataFrame(0.0, index=idx, columns=cols)
    w.iloc[:2, 0] = 1.0      # 前两日建立持仓
    w.iloc[2:, 0] = 0.0      # 第 3 日起清仓目标
    gated = apply_fillability_gate(w)
    assert float(gated.iloc[1, 0]) == 1.0, "无闸事件时持仓应照常"
    assert float(gated.iloc[2, 0]) == 1.0, "跌停封死日卖出被拦后必须保持前值（禁出逃）"
    assert float(gated.iloc[3, 0]) == 0.0, "次日未封板应正常清仓（闸不锁死仓位）"


def test_gate_failopen_on_missing_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """闸原料缺失（ETF 等 stk_limit 无行）→ 不闸 fail-open，不编造可成交性。"""
    idx = pd.bdate_range("2026-01-05", periods=4)
    cols = ["510300"]

    def empty_masks(index: pd.DatetimeIndex, columns: pd.Index):
        return pd.DataFrame(False, index=index, columns=columns), pd.DataFrame(False, index=index, columns=columns)

    monkeypatch.setattr(sys.modules["_c4_engine"], "_load_seal_masks", empty_masks)
    w = pd.DataFrame(1.0, index=idx, columns=cols)
    gated = apply_fillability_gate(w)
    assert float(gated.iloc[-1, 0]) == 1.0, "无涨跌停数据标的不得被闸误伤"


def test_gate_changes_backtest_output_real() -> None:
    """端到端：真实反例窗口内，闸开/闸关的净收益路径必须可区分（洞修复有实效）。"""
    symbol, seal_date = REAL_CASES[0][0], REAL_CASES[0][1]
    from scripts.backtest.translated import _c4_engine  # noqa: PLC0415 — 复用引擎装载器取价

    px_long = _c4_engine.load_px("2024-09-20", "2025-04-15", fields=("close",))
    px = px_long.pivot(index="trade_date", columns="symbol", values="close")[[symbol]]
    idx = px.index
    w = pd.DataFrame(0.0, index=idx, columns=[symbol])
    w.loc[pd.Timestamp(seal_date):, symbol] = 1.0
    net_on = daily_net_returns(w, px, gate_limits=True)
    net_off = daily_net_returns(w, px, gate_limits=False)
    assert float(net_on.abs().sum()) >= 0.0  # 路径本身可算
    assert not np.allclose(net_on.values, net_off.values), (
        "闸开/闸关净收益逐位相同——闸无鉴别力（假绿）"
    )
    stats = run_backtest(w, px, gate_limits=True)
    assert {"days", "sharpe", "max_drawdown"} <= set(stats)
