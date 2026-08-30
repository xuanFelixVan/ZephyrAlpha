# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §3.1
# [MODULE] zephyr.factor.core.ctr001_consumer.converter
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.shared.contracts.market_data
# [CONSUMERS] zephyr.factor.factor_base
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——仅使用timestamp做截面对齐，禁止使用ingested_at(可能引入未来函数)
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空列表->返回空DataFrame; None输入->返回空DataFrame
# [TESTS] tests/factor/test_ctr001_consumer.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CTR-001 NormalizedMarketData 消费者——数据适配层。

将 D_DATA 产出的 CTR-001 NormalizedMarketData（frozen dataclass, Decimal 字段）
转为 D_FACTOR 因子计算所需的 pd.DataFrame（float 字段, MultiIndex）。

职责边界：
- Decimal→float 集中转换（pandas 向量化需要 float）
- 质量过滤（可选：is_suspended / quality_score）
- 不做任何因子计算——纯数据适配

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: records 参数
#   fields: 参数 records，类型注解 Sequence[NormalizedMarketData] | None
#   code: converter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: df 参数
#   fields: 参数 df，类型注解 pd.DataFrame
#   code: converter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: min_score 参数
#   fields: 参数 min_score，类型注解 float
#   code: converter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① to_dataframe
#   name_en: to_dataframe
#   intro: 将 CTR-001 NormalizedMarketData 列表转为因子计算用 DataFrame。
#   desc: 将 CTR-001 NormalizedMarketData 列表转为因子计算用 DataFrame。 Args: records: NormalizedMarketData 列…；源码 L101-L116
#   inputs: records
#   outputs: pd.DataFrame
# - id: A2
#   name_zh: ② filter_quality
#   name_en: filter_quality
#   intro: 过滤低质量数据：剔除 is_suspended=True 和 quality_score < min_score。
#   desc: 过滤低质量数据：剔除 is_suspended=True 和 quality_score < min_score。 Args: df: to_dataframe 的输出 min_…；源码 L119-L132
#   inputs: df min_score
#   outputs: pd.DataFrame
# 层: 输出
# - id: O1
#   name_zh: pd.DataFrame
#   name_en: pd.DataFrame
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.factor.factor_base
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

import pandas as pd

from zephyr.shared.contracts.market_data import NormalizedMarketData

# 转换为 float 的数值列（CTR-001 中为 Decimal）
_NUMERIC_FIELDS = ("open", "high", "low", "close", "volume", "amount", "adj_factor")
# 保留的元数据列（float / bool）
_META_FIELDS = ("quality_score", "is_suspended")


def _record_to_dict(rec: NormalizedMarketData) -> dict:
    """单条 NormalizedMarketData → dict（Decimal→float）。"""
    row: dict = {}
    for f in _NUMERIC_FIELDS:
        val = getattr(rec, f, None)
        row[f] = float(val) if isinstance(val, Decimal) else val
    for f in _META_FIELDS:
        row[f] = getattr(rec, f, None)
    row["symbol"] = rec.symbol
    row["timestamp"] = rec.timestamp
    return row


def to_dataframe(records: Sequence[NormalizedMarketData] | None) -> pd.DataFrame:
    """将 CTR-001 NormalizedMarketData 列表转为因子计算用 DataFrame。

    Args:
        records: NormalizedMarketData 列表（来自 D_DATA）

    Returns:
        MultiIndex=(symbol, timestamp)，列=open/high/low/close/volume/amount/
        adj_factor/quality_score/is_suspended。空输入返回空 DataFrame。
    """
    if not records:
        return pd.DataFrame()
    rows = [_record_to_dict(r) for r in records]
    df = pd.DataFrame(rows)
    df = df.set_index(["symbol", "timestamp"])
    return df.sort_index()


def filter_quality(df: pd.DataFrame, min_score: float = 0.7) -> pd.DataFrame:
    """过滤低质量数据：剔除 is_suspended=True 和 quality_score < min_score。

    Args:
        df: to_dataframe 的输出
        min_score: 最低质量分阈值（默认 0.7，对齐 CTR-001 契约说明）

    Returns:
        过滤后的 DataFrame（仅保留高质量行）
    """
    if df.empty or "is_suspended" not in df.columns:
        return df
    mask = ~df["is_suspended"] & (df["quality_score"] >= min_score)
    return df[mask]
