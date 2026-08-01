# [BLUEPRINT] MOD-BT-022 | docs/03_modules/_domain_backtest/data_quality_checker/blueprint.md
# [MODULE] zephyr.backtest.services.data_quality_checker
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-BT-017(scheduler,回测前质量门禁) ; MOD-BT-021(param_analyzer)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯pandas只读不修改输入;passed=无ERROR级问题;空DataFrame返回passed=True;支持单标的与MultiIndex
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDataFormatError
# [TESTS] tests/backtest/test_data_quality_checker.py
# [A_module] module_id=MOD-BT-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Data Quality Checker — 回测数据质量检查器 (MOD-BT-022)

回测前/后对 OHLCV 数据执行质量检查, 输出结构化质量报告。
覆盖三大维度: 缺失检测(NaN/交易日gaps) + 异常检测(价格/成交量/OHLC逻辑) + 一致性检查(前复权连续性)。

属A类基础设施(纯pandas检查+阈值判定+报告生成, 逻辑明确), 阈值为C类可调参数。
纯工具模块, 不依赖外部数据库, 数据由调用方传入。

依据: D:\\临时工作区\\依赖图\\32-D-BACKTEST-回测引擎域.md §1 BT-22
       docs/03_modules/_domain_backtest/blueprint.md §5.1 L697 (P1-13 数据质量检查)
SSoT: depgraph MOD-BT-022
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "Severity",
    "DataQualityConfig",
    "QualityIssue",
    "DataQualityReport",
    "DataQualityChecker",
    "InvalidDataFormatError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class Severity(str, Enum):
    """问题严重度。"""

    ERROR = "ERROR"  # 必须修复 → report.passed = False
    WARN = "WARN"    # 建议检查
    INFO = "INFO"    # 提示信息


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidDataFormatError(ZephyrBaseError):
    """输入数据格式非法(如非DataFrame / 缺少必需列)。"""

    error_code = "ZA-BT-0022"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DataQualityConfig:
    """数据质量检查配置 (设计真源 §3)。"""

    price_anomaly_threshold: float = 0.20       # 单日涨跌幅阈值 (默认20%)
    volume_spike_multiplier: float = 10.0        # 异常放量倍数 (相对均值)
    max_gap_days: int = 10                       # 交易日间隔阈值 (超此值报gaps)
    adj_discontinuity_threshold: float = 0.30    # 前复权跳变阈值 (默认30%)
    required_columns: tuple[str, ...] = (
        "open", "high", "low", "close", "volume",
    )

    def __post_init__(self) -> None:
        if not 0 < self.price_anomaly_threshold <= 1:
            raise InvalidDataFormatError(
                f"price_anomaly_threshold must be in (0,1], got {self.price_anomaly_threshold}"
            )
        if self.volume_spike_multiplier <= 0:
            raise InvalidDataFormatError(
                f"volume_spike_multiplier must be > 0, got {self.volume_spike_multiplier}"
            )
        if self.max_gap_days <= 0:
            raise InvalidDataFormatError(
                f"max_gap_days must be > 0, got {self.max_gap_days}"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class QualityIssue:
    """单条数据质量问题。"""

    rule: str
    severity: Severity
    symbol: str
    message: str
    date: Any | None = None       # 时间戳 (可能为 None)
    value: float | None = None    # 实际值
    threshold: float | None = None  # 阈值


@dataclass
class DataQualityReport:
    """数据质量检查报告。"""

    passed: bool
    issues: list[QualityIssue] = field(default_factory=list)
    total_bars: int = 0
    symbols_checked: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity is Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity is Severity.WARN)

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity is Severity.INFO)

    def issues_by_severity(self, severity: Severity) -> list[QualityIssue]:
        """按严重度过滤问题。"""
        return [i for i in self.issues if i.severity is severity]

    def issues_by_rule(self, rule: str) -> list[QualityIssue]:
        """按规则名过滤问题。"""
        return [i for i in self.issues if i.rule == rule]


# ──────────────────────────────────────────────────────────────────────────────
# 数据质量检查器
# ──────────────────────────────────────────────────────────────────────────────


class DataQualityChecker:
    """回测数据质量检查器——缺失检测+异常检测+一致性检查。

    用法:
        checker = DataQualityChecker()
        report = checker.check(ohlcv_df)
        if not report.passed:
            # 存在 ERROR 级问题, 需修复后才能回测
            for issue in report.issues_by_severity(Severity.ERROR):
                print(issue)

    支持两种输入格式:
        1. 单标的: DataFrame indexed by date, columns=[open,high,low,close,volume]
        2. 多标的: MultiIndex [symbol, date], same columns

    纯 pandas 只读操作, 不修改输入数据。

    Args:
        config: 检查配置 (阈值)
    """

    def __init__(self, config: DataQualityConfig | None = None) -> None:
        self._config = config or DataQualityConfig()

    @property
    def config(self) -> DataQualityConfig:
        return self._config

    # ── 公开 API ──

    def check(self, data: pd.DataFrame) -> DataQualityReport:
        """检查 OHLCV 数据质量。

        Args:
            data: OHLCV DataFrame (单标的 date-indexed 或多标的 MultiIndex [symbol, date])

        Returns:
            DataQualityReport (passed=无ERROR级问题)

        Raises:
            InvalidDataFormatError: 输入非 DataFrame / 缺少必需列
        """
        self._validate(data)

        # 空 DataFrame → 通过 (不报错)
        if data.empty:
            return DataQualityReport(passed=True, issues=[], total_bars=0, symbols_checked=0)

        groups = self._split_by_symbol(data)

        issues: list[QualityIssue] = []
        total_bars = 0
        for symbol, df in groups:
            total_bars += len(df)
            issues.extend(self._check_missing(symbol, df))
            issues.extend(self._check_anomaly(symbol, df))
            issues.extend(self._check_consistency(symbol, df))

        passed = not any(i.severity is Severity.ERROR for i in issues)
        return DataQualityReport(
            passed=passed,
            issues=issues,
            total_bars=total_bars,
            symbols_checked=len(groups),
        )

    # ── 内部: 校验与分组 ──

    def _validate(self, data: pd.DataFrame) -> None:
        if not isinstance(data, pd.DataFrame):
            raise InvalidDataFormatError(
                f"data must be a pandas DataFrame, got {type(data).__name__}"
            )
        missing = set(self._config.required_columns) - set(data.columns)
        if missing:
            raise InvalidDataFormatError(
                f"missing required columns: {sorted(missing)}; "
                f"got columns={list(data.columns)}"
            )

    @staticmethod
    def _split_by_symbol(data: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
        """将 DataFrame 拆分为 [(symbol, sub_df)] 列表。

        单标的 (date index) → [("_default", data)]
        多标的 (MultiIndex [symbol, date]) → groupby(level=0)
        """
        if isinstance(data.index, pd.MultiIndex):
            return [
                (str(symbol), group.droplevel(0))
                for symbol, group in data.groupby(level=0, sort=False)
            ]
        return [("_default", data)]

    # ── 内部: 缺失检测 ──

    def _check_missing(self, symbol: str, df: pd.DataFrame) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        cfg = self._config

        # NaN 字段检测
        for col in cfg.required_columns:
            nan_mask = df[col].isna()
            if nan_mask.any():
                sev = Severity.ERROR if col in ("close", "volume") else Severity.WARN
                for idx in df.index[nan_mask]:
                    issues.append(QualityIssue(
                        rule="nan_value", severity=sev, symbol=symbol,
                        date=idx, message=f"{col} is NaN",
                    ))

        # 交易日 gaps 检测 (相邻日期间隔 > max_gap_days)
        if isinstance(df.index, pd.DatetimeIndex) and len(df) > 1:
            gaps = df.index.to_series().diff().dt.days
            big_gaps = gaps[gaps > cfg.max_gap_days]
            for idx, gap_days in big_gaps.items():
                if pd.notna(gap_days):
                    issues.append(QualityIssue(
                        rule="trading_day_gap", severity=Severity.WARN,
                        symbol=symbol, date=idx, value=float(gap_days),
                        threshold=float(cfg.max_gap_days),
                        message=f"gap of {int(gap_days)} days exceeds max {cfg.max_gap_days}",
                    ))

        return issues

    # ── 内部: 异常检测 ──

    def _check_anomaly(self, symbol: str, df: pd.DataFrame) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        cfg = self._config

        # 负值检测
        for col in cfg.required_columns:
            neg_mask = df[col] < 0
            for idx in df.index[neg_mask]:
                issues.append(QualityIssue(
                    rule="negative_value", severity=Severity.ERROR,
                    symbol=symbol, date=idx, value=float(df.loc[idx, col]),
                    threshold=0.0, message=f"{col} is negative",
                ))

        # 单日涨跌幅异常 (fill_method=None 避免填充 NaN 掩盖缺失)
        pct = df["close"].pct_change(fill_method=None).abs()
        anomalous = pct > cfg.price_anomaly_threshold
        for idx in df.index[anomalous]:
            issues.append(QualityIssue(
                rule="price_anomaly", severity=Severity.WARN,
                symbol=symbol, date=idx, value=float(pct.loc[idx]),
                threshold=cfg.price_anomaly_threshold,
                message=f"price change {pct.loc[idx]:.2%} exceeds {cfg.price_anomaly_threshold:.0%}",
            ))

        # 零成交量
        zero_vol = df["volume"] == 0
        for idx in df.index[zero_vol]:
            issues.append(QualityIssue(
                rule="zero_volume", severity=Severity.WARN,
                symbol=symbol, date=idx, message="volume is 0",
            ))

        # 异常放量 (用 median 避免单个异常值拉高基线导致漏检)
        vol_median = df["volume"].median()
        if vol_median and vol_median > 0:
            spike_threshold = vol_median * cfg.volume_spike_multiplier
            spike_mask = df["volume"] > spike_threshold
            for idx in df.index[spike_mask]:
                issues.append(QualityIssue(
                    rule="volume_spike", severity=Severity.WARN,
                    symbol=symbol, date=idx, value=float(df.loc[idx, "volume"]),
                    threshold=spike_threshold,
                    message="volume spike exceeds mean x multiplier",
                ))

        # OHLC 逻辑违背
        ohlc_checks = [
            ("high_lt_low", df["high"] < df["low"], "high < low"),
            ("high_lt_open", df["high"] < df["open"], "high < open"),
            ("high_lt_close", df["high"] < df["close"], "high < close"),
            ("low_gt_open", df["low"] > df["open"], "low > open"),
            ("low_gt_close", df["low"] > df["close"], "low > close"),
        ]
        for rule, mask, msg in ohlc_checks:
            for idx in df.index[mask]:
                issues.append(QualityIssue(
                    rule=rule, severity=Severity.ERROR,
                    symbol=symbol, date=idx, message=msg,
                ))

        return issues

    # ── 内部: 一致性检查 ──

    def _check_consistency(self, symbol: str, df: pd.DataFrame) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        cfg = self._config

        # 前复权连续性: close 跳变 > 阈值 (可能是复权问题)
        if len(df) > 1:
            pct = df["close"].pct_change(fill_method=None).abs()
            big_jump = pct > cfg.adj_discontinuity_threshold
            for idx in df.index[big_jump]:
                issues.append(QualityIssue(
                    rule="adj_continuity", severity=Severity.WARN,
                    symbol=symbol, date=idx, value=float(pct.loc[idx]),
                    threshold=cfg.adj_discontinuity_threshold,
                    message="possible adjustment discontinuity",
                ))

        return issues
