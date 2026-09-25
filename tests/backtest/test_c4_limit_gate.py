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
    ("601162", "2024-09-25", 3.30),  # 924 暴动窗次日，封涨停
    ("000016", "2025-04-10", 4.64),  # 关税恐慌窗，封涨停
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
    w.loc[pd.Timestamp(seal_date) :, symbol] = 1.0  # 封板日起全额买入目标

    gated = apply_fillability_gate(w)
    assert float(gated.loc[pd.Timestamp(seal_date), symbol]) == 0.0, (
        f"{symbol}@{seal_date} 涨停封死仍建立仓位——E7 引擎洞未修（此断言必红）"
    )

    ungated = apply_fillability_gate(w, gate_limits=False)
    assert float(ungated.loc[pd.Timestamp(seal_date), symbol]) == 1.0, (
        "gate_limits=False 必须复现旧行为（反例对照通道）"
    )


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
    w.iloc[:2, 0] = 1.0  # 前两日建立持仓
    w.iloc[2:, 0] = 0.0  # 第 3 日起清仓目标
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
    w.loc[pd.Timestamp(seal_date) :, symbol] = 1.0
    net_on = daily_net_returns(w, px, gate_limits=True)
    net_off = daily_net_returns(w, px, gate_limits=False)
    assert float(net_on.abs().sum()) >= 0.0  # 路径本身可算
    assert not np.allclose(net_on.values, net_off.values), "闸开/闸关净收益逐位相同——闸无鉴别力（假绿）"
    stats = run_backtest(w, px, gate_limits=True)
    assert {"days", "sharpe", "max_drawdown"} <= set(stats)


# ── st-ddup-20260925 去重改造③：掩码 pivot 向量化+批级 LRU 缓存 守护 ──────────────
class TestSealMaskVectorizedAndCache:
    """向量化构建与原逐行参考实现逐位等价；缓存命中免 CH 往返且逐位一致；LRU 有界。"""

    @staticmethod
    def _rowwise_reference(index, columns, raw_rows, lim_rows):
        """原逐行实现复刻（对拍锚，摘自改造前 _c4_engine._load_seal_masks）。"""
        empty = pd.DataFrame(False, index=index, columns=columns)
        raw = {(str(d)[:10], str(s)[:6]): float(c) for d, s, c in raw_rows}
        sealed_up = empty.copy()
        sealed_down = empty.copy()
        idx_map = {d.strftime("%Y-%m-%d"): i for i, d in enumerate(index)}
        col_map = {str(c)[:6]: j for j, c in enumerate(columns)}
        for d, s, up, dn in lim_rows:
            i, j = idx_map.get(str(d)[:10]), col_map.get(str(s)[:6])
            if i is None or j is None:
                continue
            c_raw = raw.get((str(d)[:10], str(s)[:6]))
            if c_raw is None:
                continue
            if up is not None and c_raw >= float(up) * (1 - 1e-4):
                sealed_up.iat[i, j] = True
            if dn is not None and c_raw <= float(dn) * (1 + 1e-4):
                sealed_down.iat[i, j] = True
        return sealed_up, sealed_down

    def test_vectorized_matches_rowwise_synthetic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import _c4_engine as eng

        idx = pd.bdate_range("2024-01-02", periods=5)
        cols = pd.Index(["600001", "600002", "600003"])
        raw_rows = [
            # (date, symbol, close)：含索引外日期 / 列外标的 / 5 日全价
            (idx[0].date(), "600001", 10.0),
            (idx[2].date(), "600001", 10.0),
            (idx[0].date(), "600002", 20.0),
            (idx[3].date(), "600002", 20.0),
            (idx[1].date(), "600003", 30.0),
            (idx[1].date(), "699999", 99.0),  # 列外
        ]
        lim_rows = [
            # 精确边界：close == up*(1-1e-4) → 须封（>= 语义）
            (idx[0].date(), "600001", 10.0 / (1 - 1e-4), 9.0),
            # up NULL（无涨停限制）→ 只判跌停方向
            (idx[2].date(), "600001", None, 5.0),
            # 缺 raw close → skip
            (idx[1].date(), "600002", 20.0, 18.0),
            # 跌停封死边界：close == dn*(1+1e-4) → 封
            (idx[3].date(), "600002", 20.0, 20.0 / (1 + 1e-4)),
            # 索引外日期 → skip
            (idx[0].date() - pd.Timedelta(days=3), "600003", 30.0, 27.0),
            # 重复键 → last-wins（与 dict 推导/wide drop_duplicates 同口径）
            (idx[1].date(), "600003", 10.0, 9.0),
            (idx[1].date(), "600003", 31.0, 29.0),
        ]
        monkeypatch.setattr(eng, "_q", lambda sql: raw_rows if "close) FROM" in sql else lim_rows)
        eng._SEAL_MASK_CACHE.clear()
        up_new, dn_new = eng._load_seal_masks(idx, cols)
        up_ref, dn_ref = self._rowwise_reference(idx, cols, raw_rows, lim_rows)
        assert up_new.equals(up_ref), f"sealed_up 漂移:\n{(up_new != up_ref).sum()} 处"
        assert dn_new.equals(dn_ref), f"sealed_down 漂移:\n{(dn_new != dn_ref).sum()} 处"
        # 参考实现确有封板发生（防两路同错全 False 假绿）
        assert int(up_new.to_numpy().sum()) >= 1 and int(dn_new.to_numpy().sum()) >= 1

    def test_cache_hit_skips_ch_and_identical(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import _c4_engine as eng

        idx = pd.bdate_range("2024-01-02", periods=3)
        cols = pd.Index(["600001"])
        rows = [(idx[0].date(), "600001", 10.0)], [(idx[0].date(), "600001", 10.0, 9.0)]
        calls = {"n": 0}

        def fake_q(sql):
            calls["n"] += 1
            return rows[0] if "close) FROM" in sql else rows[1]

        monkeypatch.setattr(eng, "_q", fake_q)
        eng._SEAL_MASK_CACHE.clear()
        up1, dn1 = eng._load_seal_masks(idx, cols)
        n_after_first = calls["n"]
        up2, dn2 = eng._load_seal_masks(idx, cols)
        assert calls["n"] == n_after_first, "缓存命中仍发 CH 查询"
        assert up1.equals(up2) and dn1.equals(dn2)

    def test_lru_capacity_bounded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import _c4_engine as eng

        rows_common = (
            [(pd.Timestamp("2024-01-02").date(), "600001", 10.0)],
            [(pd.Timestamp("2024-01-02").date(), "600001", 10.0, 9.0)],
        )
        monkeypatch.setattr(eng, "_q", lambda sql: rows_common[0] if "close) FROM" in sql else rows_common[1])
        monkeypatch.setattr(eng, "_SEAL_MASK_CACHE_MAX", 2)
        eng._SEAL_MASK_CACHE.clear()
        for extra in ("600001", "600002", "600003"):
            eng._load_seal_masks(pd.bdate_range("2024-01-02", periods=3), pd.Index([extra]))
        assert len(eng._SEAL_MASK_CACHE) <= 2
