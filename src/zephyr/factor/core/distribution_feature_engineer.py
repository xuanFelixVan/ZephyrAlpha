# [BLUEPRINT] MOD-L02-026 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §1
# [MODULE] zephyr.factor.core.distribution_feature_engineer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas; numpy
# [CONSUMERS] zephyr.signal_ashare.conditional_density_predictor（特征输入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT 铁律——默认 shift=1，t 行特征只用 ≤t−1 数据；滚动统计仅用 trailing 窗口（无 center）；输入 df 不被修改（返回副本）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 指定列不存在 → ValueError；空 df → 空副本（仅索引）
# [TESTS] tests/factor/test_distribution_feature_engineer.py
# [A_module] module_id=MOD-L02-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 因子/收益 DataFrame + DistributionFeatureConfig（lags/windows/quantiles/interactions/shift）
# A1: 滞后项——{col}_lag{k}（k ∈ lags）
# A2: 滚动分布统计——trailing 窗口 mean/std/skew/kurt(Fisher)/分位数（{col}_roll*{w}）
# A3: 交互项——{a}_x_{b} 列对乘积；全特征统一 shift（PIT 对齐）
# O1: 增强 DataFrame（原列 + 派生特征列，副本返回）
# [/ALGO_FLOW]
"""
分布特征工程器（MOD-L02-026，D_FACTOR core）。

给因子加料——滞后项、交互项、滚动统计量（均值/标准差/偏度/峰度/分位数），
专门喂给密度预测模型（BM-SEL-13 conditional_density_predictor 的条件分布特征）。
与 factor/core/dist_feature_eng（分布式**计算**引擎，ProcessPool 并行调度）边界：
本模块是分布**特征**构造函数（纯 pandas 变换），不做并行调度。

PIT 铁律（INV-004 对齐）：默认 shift=1——t 行特征只使用 ≤t−1 的数据（t 日决策
消费 t−1 特征，无未来函数）；滚动统计全部 trailing 窗口，不用 center=True。
签名方法（signature features）登记远期——路径签名张量需 esig 依赖，当前滚动
统计量已覆盖密度预测所需分布信息，不引入。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: df 参数
#   fields: 参数 df，类型注解 pd.DataFrame
#   code: distribution_feature_engineer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: columns 参数
#   fields: 参数 columns，类型注解 tuple[str, ...]
#   code: distribution_feature_engineer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: lags 参数
#   fields: 参数 lags，类型注解 tuple[int, ...]
#   code: distribution_feature_engineer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: windows 参数
#   fields: 参数 windows，类型注解 tuple[int, ...]
#   code: distribution_feature_engineer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① add_lag_features
#   name_en: add_lag_features
#   intro: 滞后项：{col}_lag{k}（沿索引下移 k 行，头部 NaN）。
#   desc: 滞后项：{col}_lag{k}（沿索引下移 k 行，头部 NaN）。；源码 L149-L162
#   inputs: df columns lags
#   outputs: pd.DataFrame
# - id: A2
#   name_zh: ② add_rolling_distribution_features
#   name_en: add_rolling_distribution_features
#   intro: 滚动分布统计：trailing 窗口 mean/std/skew/kurt(Fisher)/分位数。
#   desc: 滚动分布统计：trailing 窗口 mean/std/skew/kurt(Fisher)/分位数。 列命名：{col}_rollmean{w} / _rollstd{w} /…；源码 L165-L193
#   inputs: df columns windows quantiles min_periods
#   outputs: pd.DataFrame
# - id: A3
#   name_zh: ③ add_interaction_features
#   name_en: add_interaction_features
#   intro: 交互项：{a}_x_{b} 列对乘积。
#   desc: 交互项：{a}_x_{b} 列对乘积。；源码 L196-L206
#   inputs: df pairs
#   outputs: pd.DataFrame
# - id: A4
#   name_zh: ④ build_distribution_features
#   name_en: build_distribution_features
#   intro: 全量构建：滞后 + 滚动分布统计 + 交互 → 派生列统一 PIT 右移。
#   desc: 全量构建：滞后 + 滚动分布统计 + 交互 → 派生列统一 PIT 右移。 shift>0 时全部**派生**特征列右移 shift 行（原样列不动）——t 行派生特征 只含 ≤…；源码 L209-L229
#   inputs: df config
#   outputs: pd.DataFrame
#   （注：A4 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: pd.DataFrame
#   name_en: pd.DataFrame
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.signal_ashare.conditional_density_predictor（特征输入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable

import pandas as pd

__all__: Final = [
    "DistributionFeatureConfig",
    "add_interaction_features",
    "add_lag_features",
    "add_rolling_distribution_features",
    "build_distribution_features",
]


@dataclass(frozen=True)
class DistributionFeatureConfig:
    """分布特征配置（参数 >4 统一收口，防散装参数）。

    Attributes:
        columns: 目标列（滞后+滚动统计的作用列）
        lags: 滞后阶数
        windows: 滚动窗口
        quantiles: 滚动分位数网格（0-1）
        interactions: 交互列对 ((a, b), ...)
        shift: PIT 右移期数（默认 1；0=不右移，仅当调用方保证 t 行只用 t 之前数据）
        min_periods: 滚动窗口最小样本数（None=与窗口等长，最严口径）
    """

    columns: tuple[str, ...] = ("return",)
    lags: tuple[int, ...] = (1, 2, 3, 5)
    windows: tuple[int, ...] = (5, 10, 20)
    quantiles: tuple[float, ...] = (0.05, 0.50, 0.95)
    interactions: tuple[tuple[str, str], ...] = ()
    shift: int = 1
    min_periods: int | None = None


def _require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"列不存在: {missing}（现有: {list(df.columns)}）")


def add_lag_features(
    df: pd.DataFrame,
    columns: tuple[str, ...],
    lags: tuple[int, ...],
) -> pd.DataFrame:
    """滞后项：{col}_lag{k}（沿索引下移 k 行，头部 NaN）。"""
    _require_columns(df, columns)
    out = df.copy()
    for col in columns:
        for k in lags:
            if k < 1:
                raise ValueError(f"滞后阶数必须 ≥1: {k}")
            out[f"{col}_lag{k}"] = df[col].shift(k)
    return out


def add_rolling_distribution_features(
    df: pd.DataFrame,
    columns: tuple[str, ...],
    windows: tuple[int, ...],
    quantiles: tuple[float, ...],
    min_periods: int | None = None,
) -> pd.DataFrame:
    """滚动分布统计：trailing 窗口 mean/std/skew/kurt(Fisher)/分位数。

    列命名：{col}_rollmean{w} / _rollstd{w} / _rollskew{w} / _rollkurt{w} /
    _rollq{pct}{w}（pct=分位×100 整数，如 q05/q50/q95）。头部不足窗口为 NaN。
    """
    _require_columns(df, columns)
    out = df.copy()
    for col in columns:
        for w in windows:
            if w < 2:
                raise ValueError(f"滚动窗口必须 ≥2: {w}")
            mp = w if min_periods is None else min_periods
            roll = df[col].rolling(window=w, min_periods=mp)
            out[f"{col}_rollmean{w}"] = roll.mean()
            out[f"{col}_rollstd{w}"] = roll.std()
            out[f"{col}_rollskew{w}"] = roll.skew()
            out[f"{col}_rollkurt{w}"] = roll.kurt()  # Fisher 超额峰度
            for q in quantiles:
                if not 0.0 < q < 1.0:
                    raise ValueError(f"分位数必须 ∈ (0,1): {q}")
                out[f"{col}_rollq{int(round(q * 100)):02d}{w}"] = roll.quantile(q)
    return out


def add_interaction_features(
    df: pd.DataFrame,
    pairs: tuple[tuple[str, str], ...],
) -> pd.DataFrame:
    """交互项：{a}_x_{b} 列对乘积。"""
    for a, b in pairs:
        _require_columns(df, (a, b))
    out = df.copy()
    for a, b in pairs:
        out[f"{a}_x_{b}"] = df[a] * df[b]
    return out


def build_distribution_features(
    df: pd.DataFrame,
    config: DistributionFeatureConfig | None = None,
) -> pd.DataFrame:
    """全量构建：滞后 + 滚动分布统计 + 交互 → 派生列统一 PIT 右移。

    shift>0 时全部**派生**特征列右移 shift 行（原样列不动）——t 行派生特征
    只含 ≤t−shift 数据（默认 shift=1，PIT 对齐 t−1）。空 df 返回空副本。
    """
    cfg = config or DistributionFeatureConfig()
    if cfg.shift < 0:
        raise ValueError(f"shift 必须 ≥0: {cfg.shift}")
    if df.empty:
        return df.copy()
    out = add_lag_features(df, cfg.columns, cfg.lags)
    out = add_rolling_distribution_features(out, cfg.columns, cfg.windows, cfg.quantiles, cfg.min_periods)
    out = add_interaction_features(out, cfg.interactions)
    if cfg.shift > 0:
        derived = [c for c in out.columns if c not in df.columns]
        out[derived] = out[derived].shift(cfg.shift)
    return out
