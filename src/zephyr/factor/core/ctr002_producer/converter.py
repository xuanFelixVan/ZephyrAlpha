# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §3.1
# [MODULE] zephyr.factor.core.ctr002_producer.converter
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.contracts.factor_signal
# [CONSUMERS] zephyr.signal_fundamental.pipeline
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——as_of_date必须对齐因子计算的数据截面日期
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空Series->返回空列表; None输入->返回空列表
# [TESTS] tests/factor/test_ctr002_producer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CTR-002 FactorSignal 生产者——信号适配层。

将 D_FACTOR 因子计算结果 pd.Series 转为 CTR-002 FactorSignal（frozen dataclass），
供 D_SIGNAL / D_RISK / D_PORTFOLIO_CORE 消费。

职责边界：
- 截面 z-score 标准化 → normalized_value
- 百分位排名 → rank_pct (0-1)
- NaN 处理 → is_valid=False
- 幂等键生成 → idempotency_key
- 不做任何因子计算——纯信号适配

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: values 参数
#   fields: 参数 values，类型注解 pd.Series | None
#   code: converter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: factor_id 参数
#   fields: 参数 factor_id，类型注解 str
#   code: converter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: as_of_date 参数
#   fields: 参数 as_of_date，类型注解 datetime
#   code: converter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: factor_version 参数
#   fields: 参数 factor_version，类型注解 str
#   code: converter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① to_signals
#   name_en: to_signals
#   intro: 将因子计算结果 pd.Series 转为 CTR-002 FactorSignal 列表。
#   desc: 将因子计算结果 pd.Series 转为 CTR-002 FactorSignal 列表。 Args: values: 因子截面得分，index 为 symbol，values…；源码 L130-L168
#   inputs: values factor_id as_of_date factor_version idempotency_key_prefix
#   outputs: list[FactorSignal]
# 层: 输出
# - id: O1
#   name_zh: list[FactorSignal]
#   name_en: list[FactorSignal]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_fundamental.pipeline
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from zephyr.shared.contracts.factor_signal import FactorSignal

# z-score 分母零保护阈值
_EPS = 1e-10


def _compute_zscore(values: pd.Series) -> pd.Series:
    """截面 z-score 标准化（仅在非NaN值上计算）。"""
    valid = values.dropna()
    if len(valid) < 2:
        return pd.Series(0.0, index=valid.index)
    std = valid.std(ddof=0)
    if std < _EPS:
        return pd.Series(0.0, index=valid.index)
    return (valid - valid.mean()) / std


def _compute_rank_pct(values: pd.Series) -> pd.Series:
    """百分位排名 (0-1)，仅在非NaN值上计算。"""
    return values.dropna().rank(pct=True)


def _build_signal(
    symbol: str,
    raw_val: float,
    as_of_date: datetime,
    factor_id: str,
    factor_version: str,
    confidence: float,
    normalized: float | None,
    rank_pct: float | None,
    key_prefix: str,
) -> FactorSignal:
    """构建单条 FactorSignal（私有辅助函数）。"""
    is_valid = pd.notna(raw_val)
    date_str = as_of_date.strftime("%Y%m%d")
    norm = float(normalized) if normalized is not None and pd.notna(normalized) else None
    rnk = float(rank_pct) if rank_pct is not None and pd.notna(rank_pct) else None
    return FactorSignal(
        as_of_date=as_of_date,
        factor_id=factor_id,
        idempotency_key=f"{key_prefix}{factor_id}:{symbol}:{date_str}",
        raw_value=float(raw_val) if is_valid else 0.0,
        symbol=str(symbol),
        confidence=confidence,
        normalized_value=norm,
        rank_pct=rnk,
        is_valid=is_valid,
        factor_version=factor_version,
    )


def to_signals(
    values: pd.Series | None,
    factor_id: str,
    as_of_date: datetime,
    factor_version: str = "1.0",
    idempotency_key_prefix: str = "",
) -> list[FactorSignal]:
    """将因子计算结果 pd.Series 转为 CTR-002 FactorSignal 列表。

    Args:
        values: 因子截面得分，index 为 symbol，values 为因子值
        factor_id: 因子ID（须在 FactorRegistry 中已注册）
        as_of_date: 截面日期（对齐因子计算的数据日期）
        factor_version: 因子版本号
        idempotency_key_prefix: 幂等键前缀（可选）

    Returns:
        FactorSignal 列表，每个 symbol 一条。空输入返回空列表。
    """
    if values is None or values.empty:
        return []
    valid_count = values.notna().sum()
    confidence = float(valid_count) / float(len(values)) if len(values) > 0 else 0.0
    normalized = _compute_zscore(values)
    rank_pct = _compute_rank_pct(values)
    return [
        _build_signal(
            symbol=sym,
            raw_val=val,
            as_of_date=as_of_date,
            factor_id=factor_id,
            factor_version=factor_version,
            confidence=confidence,
            normalized=normalized.get(sym),
            rank_pct=rank_pct.get(sym),
            key_prefix=idempotency_key_prefix,
        )
        for sym, val in values.items()
    ]
