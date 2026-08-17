# [BLUEPRINT] MOD-BT-026 | docs/03_modules/_domain_backtest/nan_processor/blueprint.md
# [MODULE] zephyr.backtest.services.nan_processor
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-BT-007(metrics) ; MOD-BT-022(data_quality_checker)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不修改输入数据;filled+dropped+remaining=original_nan;fill_limit限制连续填充
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDataFormatError
# [TESTS] tests/backtest/test_nan_processor.py
# [A_module] module_id=MOD-BT-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


NaN Processor — 指标NaN处理器 (MOD-BT-026)

回测指标计算中NaN值的智能填充与清洗。提供6种填充策略 + 按比例清洗高NaN行/列。
纯pandas工具, 不修改原始数据。

蓝图: docs/03_modules/_domain_backtest/nan_processor/blueprint.md
SSoT: depgraph MOD-BT-026
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 含NaN指标数据 DataFrame
#   fields: 任意含NaN的回测指标表
#   code: data
# - id: I2
#   name: NaN处理配置 NaNProcessorConfig frozen
#   fields: fill_strategy=ffill + drop_all_nan_rows=True + drop_all_nan_cols=False + max_nan_ratio=0.5 + fill_limit=0
#   code: NaNProcessorConfig L83-101
# 层: 算法
# - id: A1
#   name_zh: ① 全NaN行列清洗
#   name_en: process(全空清洗段)
#   intro: 整行整列全是NaN的直接删掉
#   desc: data.copy()副本 → isna().all(axis=1)删全NaN行 → all(axis=0)删全NaN列 各自计数（L179-208）
#   inputs: I1 I2
#   outputs: 中间df+dropped计数
#   invariant: 不修改输入数据返回副本
# - id: A2
#   name_zh: ② 高NaN比例行列删除
#   name_en: process(比例清洗段)
#   intro: NaN占比超过50%的行或列按比例删掉
#   desc: isna().mean(axis=1)>max_nan_ratio删行 → 非空再mean(axis=0)超阈值删列（L210-221）
#   inputs: A1 I2
#   outputs: 中间df
# - id: A3
#   name_zh: ③ 6策略NaN填充
#   name_en: _fill
#   intro: 前向/后向/均值/中位数/线性插值/填零六种策略挑一种补洞
#   desc: ffill/bfill带limit → fillna(mean/median numeric_only) → interpolate(linear,forward) → fillna(0)（L244-263）
#   inputs: A2 I2
#   outputs: 填充后df
#   invariant: fill_limit限制连续填充长度
# - id: A4
#   name_zh: ④ 处理报告生成
#   name_en: process(报告段)
#   intro: 数清填了多少删了多少还剩多少NaN出报告
#   desc: filled_count=填充前后NaN差 → 组装NaNProcessReport → cleanup_ratio=1-after/before（L223-240, L122-127）
#   inputs: A3
#   outputs: NaNProcessReport
#   invariant: filled+dropped+remaining=original_nan
# 层: 输出
# - id: O1
#   name_zh: 清洗后DataFrame+处理报告 二元组
#   name_en: (df, NaNProcessReport)
#   intro: 返回清洗副本和处理统计，供指标计算与质量检查使用
#   invariant: 不修改输入数据
#   downstream: metrics MOD-BT-007 ; data_quality_checker MOD-BT-022
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> A3
# I2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "FillStrategy",
    "NaNProcessorConfig",
    "NaNProcessReport",
    "NaNProcessor",
    "InvalidDataFormatError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class FillStrategy(str, Enum):
    """NaN填充策略。"""

    FFILL = "ffill"        # 前向填充
    BFILL = "bfill"        # 后向填充
    MEAN = "mean"          # 均值填充
    MEDIAN = "median"      # 中位数填充
    LINEAR = "linear"      # 线性插值
    ZERO = "zero"          # 零填充


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidDataFormatError(ZephyrBaseError):
    """输入数据格式非法。"""

    error_code = "ZA-BT-0026"


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class NaNProcessorConfig:
    """NaN处理配置。"""

    fill_strategy: FillStrategy = FillStrategy.FFILL
    drop_all_nan_rows: bool = True       # 删除全NaN行
    drop_all_nan_cols: bool = False       # 删除全NaN列
    max_nan_ratio: float = 0.5            # 行/列NaN比例超此值则删除 (0=不按比例删除)
    fill_limit: int = 0                   # 连续填充上限 (0=无限制)

    def __post_init__(self) -> None:
        if not 0 <= self.max_nan_ratio <= 1:
            raise InvalidDataFormatError(
                f"max_nan_ratio must be in [0,1], got {self.max_nan_ratio}"
            )
        if self.fill_limit < 0:
            raise InvalidDataFormatError(
                f"fill_limit must be >= 0, got {self.fill_limit}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 报告
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class NaNProcessReport:
    """NaN处理报告。"""

    original_shape: tuple[int, int]
    processed_shape: tuple[int, int]
    total_nan_before: int
    total_nan_after: int
    filled_count: int
    dropped_rows: int
    dropped_cols: int
    strategy: str

    @property
    def cleanup_ratio(self) -> float:
        """NaN清除比例。"""
        if self.total_nan_before == 0:
            return 1.0
        return 1.0 - (self.total_nan_after / self.total_nan_before)


# ──────────────────────────────────────────────────────────────────────────────
# NaN处理器
# ──────────────────────────────────────────────────────────────────────────────


class NaNProcessor:
    """指标NaN处理器——智能填充+清洗。

    用法:
        proc = NaNProcessor(NaNProcessorConfig(fill_strategy=FillStrategy.LINEAR))
        cleaned, report = proc.process(df_with_nan)
        print(f"filled {report.filled_count}, dropped {report.dropped_rows} rows")

    不修改输入数据, 返回副本。

    Args:
        config: 处理配置
    """

    def __init__(self, config: NaNProcessorConfig | None = None) -> None:
        self._config = config or NaNProcessorConfig()

    @property
    def config(self) -> NaNProcessorConfig:
        return self._config

    # ── 公开 API ──

    def process(
        self, data: pd.DataFrame, config: NaNProcessorConfig | None = None
    ) -> tuple[pd.DataFrame, NaNProcessReport]:
        """处理 DataFrame 中的 NaN 值。

        Args:
            data: 含NaN的DataFrame
            config: 可选覆盖配置

        Returns:
            (处理后的DataFrame, NaNProcessReport)

        Raises:
            InvalidDataFormatError: 输入非DataFrame
        """
        cfg = config or self._config
        if not isinstance(data, pd.DataFrame):
            raise InvalidDataFormatError(
                f"data must be a pandas DataFrame, got {type(data).__name__}"
            )

        df = data.copy()
        original_shape = df.shape
        total_nan_before = int(df.isna().sum().sum())

        # 空 DataFrame
        if df.empty or total_nan_before == 0:
            return df, NaNProcessReport(
                original_shape=original_shape,
                processed_shape=df.shape,
                total_nan_before=total_nan_before,
                total_nan_after=0,
                filled_count=0,
                dropped_rows=0,
                dropped_cols=0,
                strategy=cfg.fill_strategy.value,
            )

        dropped_rows = 0
        dropped_cols = 0

        # 1. 清洗: 删除全NaN行/列
        if cfg.drop_all_nan_rows:
            mask_all_nan = df.isna().all(axis=1)
            dropped_rows += int(mask_all_nan.sum())
            df = df[~mask_all_nan]

        if cfg.drop_all_nan_cols:
            mask_all_nan_cols = df.isna().all(axis=0)
            dropped_cols += int(mask_all_nan_cols.sum())
            df = df.loc[:, ~mask_all_nan_cols]

        # 2. 清洗: 按比例删除高NaN行/列
        if cfg.max_nan_ratio > 0 and not df.empty:
            row_nan_ratio = df.isna().mean(axis=1)
            high_nan_rows = row_nan_ratio > cfg.max_nan_ratio
            dropped_rows += int(high_nan_rows.sum())
            df = df[~high_nan_rows]

            if not df.empty:
                col_nan_ratio = df.isna().mean(axis=0)
                high_nan_cols = col_nan_ratio > cfg.max_nan_ratio
                dropped_cols += int(high_nan_cols.sum())
                df = df.loc[:, ~high_nan_cols]

        # 3. 填充
        nan_before_fill = int(df.isna().sum().sum())
        df = self._fill(df, cfg)
        nan_after_fill = int(df.isna().sum().sum())
        filled_count = nan_before_fill - nan_after_fill

        total_nan_after = int(df.isna().sum().sum())

        return df, NaNProcessReport(
            original_shape=original_shape,
            processed_shape=df.shape,
            total_nan_before=total_nan_before,
            total_nan_after=total_nan_after,
            filled_count=filled_count,
            dropped_rows=dropped_rows,
            dropped_cols=dropped_cols,
            strategy=cfg.fill_strategy.value,
        )

    # ── 内部 ──

    @staticmethod
    def _fill(df: pd.DataFrame, cfg: NaNProcessorConfig) -> pd.DataFrame:
        """按策略填充NaN。"""
        strategy = cfg.fill_strategy
        limit = cfg.fill_limit if cfg.fill_limit > 0 else None

        if strategy is FillStrategy.FFILL:
            return df.ffill(limit=limit)
        if strategy is FillStrategy.BFILL:
            return df.bfill(limit=limit)
        if strategy is FillStrategy.MEAN:
            return df.fillna(df.mean(numeric_only=True))
        if strategy is FillStrategy.MEDIAN:
            return df.fillna(df.median(numeric_only=True))
        if strategy is FillStrategy.LINEAR:
            return df.interpolate(method="linear", limit=limit, limit_direction="forward")
        if strategy is FillStrategy.ZERO:
            return df.fillna(0)
        # pragma: no cover — enum 穷尽
        return df
