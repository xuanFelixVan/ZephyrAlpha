# [A_test] module_id: MOD-SIG-064 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-064 | 待统筹登记 | 21号 memo §3.4
# [MODULE] tests.signal_ashare.test_strength_ic_data_assembler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""StrengthICDataAssembler（MOD-SIG-064）施工验证测试。

覆盖：
- 60 日窗口切片（与 calibrator 对齐）；
- 前瞻收益推导（预计算优先 / close/next_close 推导）；
- NaN 同步剔除；
- 契约适配：输出可直接传入 compute_rolling_ic_weights；
- 输入校验 fail-closed。
纯内存夹具，不触库。
"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.strength_ic_data_assembler import (
    DailyStrengthRecord,
    assemble_from_records,
    assemble_ic_window,
)
from zephyr.signal_ashare.strength_ic_weight_calibrator import (
    STRENGTH_DIMENSIONS,
    compute_rolling_ic_weights,
)


def _mk_records(n: int, start_day: int = 1) -> list[DailyStrengthRecord]:
    """合成 n 日记录（线性收益，便于验证窗口切片）。"""
    records = []
    for i in range(n):
        day = start_day + i
        records.append(
            DailyStrengthRecord(
                trade_date=f"2026-08-{day:02d}",
                scores={dim: float(i) + j * 0.1 for j, dim in enumerate(STRENGTH_DIMENSIONS)},
                close=100.0 + i,
                next_close=101.0 + i,
            )
        )
    return records


def test_assemble_ic_window_slices_last_60():
    """窗口切片：输入 100 日 → 输出末 60 日。"""
    n = 100
    dim_series = {dim: list(range(n)) for dim in STRENGTH_DIMENSIONS}
    returns = [0.001 * i for i in range(n)]
    out_dim, out_ret = assemble_ic_window(dim_series, returns, window=60)
    assert len(out_ret) == 60
    assert out_ret[0] == pytest.approx(0.040)  # 第 40 个元素起（100-60）
    for dim in STRENGTH_DIMENSIONS:
        assert len(out_dim[dim]) == 60
        assert out_dim[dim][0] == 40


def test_assemble_ic_window_short_input():
    """输入 < 窗口 → 全量返回。"""
    dim_series = {dim: [1.0, 2.0] for dim in STRENGTH_DIMENSIONS}
    returns = [0.01, 0.02]
    out_dim, out_ret = assemble_ic_window(dim_series, returns, window=60)
    assert len(out_ret) == 2


def test_assemble_ic_window_length_mismatch_fail_closed():
    """维度序列长度不一致 → ValueError。"""
    dim_series = {dim: [1.0, 2.0] for dim in STRENGTH_DIMENSIONS}
    dim_series["price_momentum"] = [1.0]  # 长度不一致
    with pytest.raises(ValueError):
        assemble_ic_window(dim_series, [0.01, 0.02])


def test_assemble_from_records_forward_return_derivation():
    """前瞻收益推导：close/next_close → (next/close - 1)。"""
    records = _mk_records(10)
    dim_series, returns = assemble_from_records(records, window=60)
    assert len(returns) == 10
    # 第 0 日收益 = 101/100 - 1 = 1%
    assert returns[0] == pytest.approx(0.01)


def test_assemble_from_records_precomputed_return_priority():
    """预计算 forward_return 优先于 close/next_close。"""
    rec = DailyStrengthRecord(
        trade_date="2026-08-01",
        scores={dim: 1.0 for dim in STRENGTH_DIMENSIONS},
        close=100.0,
        next_close=200.0,  # 若用此值 = 100% 收益
        forward_return=0.005,  # 预计算 = 0.5% 收益
    )
    _, returns = assemble_from_records([rec], window=60)
    assert returns[0] == pytest.approx(0.005)


def test_assemble_from_records_nan_sync_drop():
    """任一维度 NaN 的索引从所有维度同步剔除。"""
    records = _mk_records(10)
    # 第 3 日 price_momentum 置 NaN
    records[3] = DailyStrengthRecord(
        trade_date=records[3].trade_date,
        scores={**records[3].scores, "price_momentum": float("nan")},
        close=records[3].close,
        next_close=records[3].next_close,
    )
    dim_series, returns = assemble_from_records(records, window=60)
    assert len(returns) == 9  # 剔除 1 日
    assert len(dim_series["price_momentum"]) == 9


def test_assemble_from_records_unsorted_input_sorted():
    """乱序输入自动按 trade_date 升序重排。"""
    records = _mk_records(10)
    records.reverse()
    dim_series, returns = assemble_from_records(records, window=60)
    assert returns[0] == pytest.approx(0.01)  # 首日收益仍在前


def test_assemble_from_records_missing_dim_empty_series():
    """记录缺某维度 → 该维空序列（calibrator 回退经验权重）；NaN 索引整条剔除。"""
    records = [
        DailyStrengthRecord(
            trade_date="2026-08-01",
            scores={"price_momentum": 1.0},  # 缺其余 5 维
            close=100.0,
            next_close=101.0,
        )
    ]
    dim_series, returns = assemble_from_records(records, window=60)
    # 缺 5 维 → NaN 同步剔除后该日整条剔除 → 全空
    assert len(dim_series["price_momentum"]) == 0
    assert len(dim_series["industry_strength"]) == 0
    assert len(returns) == 0


def test_contract_compatibility_with_calibrator():
    """装配输出可直接传入 compute_rolling_ic_weights（契约适配验证）。"""
    records = _mk_records(70)
    dim_series, returns = assemble_from_records(records, window=60)
    weights = compute_rolling_ic_weights(dim_series, returns, window=60)
    assert abs(sum(weights.values()) - 1.0) < 1e-9  # 权重归一


def test_empty_records():
    """空记录 → 空序列。"""
    dim_series, returns = assemble_from_records([], window=60)
    assert all(len(v) == 0 for v in dim_series.values())
    assert len(returns) == 0


def test_invalid_trade_date_fail_closed():
    """trade_date 非法 → ValueError。"""
    rec = DailyStrengthRecord(
        trade_date="",
        scores={dim: 1.0 for dim in STRENGTH_DIMENSIONS},
        close=100.0,
        next_close=101.0,
    )
    with pytest.raises(ValueError):
        assemble_from_records([rec])
