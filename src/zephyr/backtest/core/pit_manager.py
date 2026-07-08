# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.pit_manager
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.core.data_handler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] PIT三公理;Embargo期;AS OF JOIN;pit_consistency_test
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PITError
# [TESTS]
# [TTL] permanent
# [A_module] module_id=MOD-BT-001-pit_manager | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
"""PIT(Point-In-Time)铁律管理器模块

职责:
  - 落实PIT三公理: 时点标记 / 版本对齐 / 泄漏防护
  - 提供 AS OF JOIN 接口, 模拟 Feature Store 语义
  - Embargo期隔离标签泄漏(默认5个交易日)
  - pit_consistency_test 训练平面与回测平面因子一致性校验
  - check_survivorship_bias 幸存者偏差检测

约束:
  - 纯 pandas/numpy 操作, 不依赖外部数据库连接, 数据由调用方传入
  - 所有查询仅返回 query_time 之前(含)可用的数据
  - 禁止使用后续修正数据(版本对齐)

SSoT: docs/03_modules/_domain_backtest/blueprint.md §5.1 PIT铁律
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

__all__ = [
    "PITConfig",
    "PITManager",
    "PITError",
]

# Embargo默认隔离交易日数
DEFAULT_EMBARGO_DAYS = 5
# 一致性校验默认偏差告警阈值(1%)
DEFAULT_CONSISTENCY_THRESHOLD = 0.01
# 相对偏差分母保护下限, 防止除零
_EPSILON = 1e-12


class PITError(Exception):
    """PIT铁律违反或数据一致性错误"""

    error_code = "ZA-BT-0004"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


@dataclass(frozen=True)
class PITConfig:
    """PIT管理器配置(frozen, 实例化后不可变, 保证纯值语义)

    Attributes:
        embargo_days: 标签泄露隔离期(交易日, 默认5)
        consistency_threshold: 因子一致性偏差告警阈值(默认0.01=1%)
    """

    embargo_days: int = DEFAULT_EMBARGO_DAYS
    consistency_threshold: float = DEFAULT_CONSISTENCY_THRESHOLD


def _to_serializable(idx_val: Any) -> Any:
    """将索引值转换为可序列化对象(Timestamp->ISO字符串, 元组递归处理)"""
    if isinstance(idx_val, tuple):
        return [_to_serializable(v) for v in idx_val]
    if isinstance(idx_val, (pd.Timestamp, datetime)):
        return idx_val.isoformat()
    return idx_val


class PITManager:
    """PIT(Point-In-Time)铁律管理器

    落实蓝图 §5.1 PIT三公理:
      1. 时点标记 - 数据点须区分 event_time(生效时间) 与 available_at(可用时间)
      2. 版本对齐 - 同一查询时点返回该时点已知的最新版本, 禁用后续修正数据
      3. 泄漏防护 - 查询时点 T 不得返回 event_time > T 的数据

    纯 pandas/numpy 实现, 数据由调用方传入, 不连接外部数据库。

    Usage:
        mgr = PITManager(PITConfig(embargo_days=5))
        visible = mgr.as_of_join(df, query_time=pd.Timestamp("2024-06-01"))
        safe = mgr.apply_embargo(label_df, current_time=pd.Timestamp("2024-06-01"))
    """

    def __init__(self, config: PITConfig | None = None) -> None:
        """初始化PIT管理器

        Args:
            config: PIT配置; None时使用默认配置(embargo=5, threshold=0.01)
        """
        self.config = config if config is not None else PITConfig()

    # ------------------------------------------------------------------
    # AS OF JOIN
    # ------------------------------------------------------------------
    def as_of_join(
        self,
        data: pd.DataFrame,
        query_time: datetime,
        event_time_col: str = "date",
        available_time_col: str | None = None,
    ) -> pd.DataFrame:
        """AS OF JOIN: 返回 query_time 之前(含)可用的数据, 按 event_time 升序

        模拟 Feature Store 的 AS OF JOIN 语义, 落实PIT三公理:
          - 泄漏防护: 仅保留 available_time <= query_time 的行
          - 时点标记: available_time_col 缺省时视同 event_time
          - 版本对齐: 同一(event_time, 标的)存在多版本时,
            取 available_time 最大且 <= query_time 的版本

        Args:
            data: 原始数据, 须包含 event_time_col 列
            query_time: 查询时点(含), 仅返回此时点已知的数据
            event_time_col: 事件生效时间列名, 默认 "date"
            available_time_col: 数据可用时间列名; None 时与 event_time 相同

        Returns:
            pd.DataFrame: query_time 可见的数据子集, 按 event_time 升序

        Raises:
            PITError: data 为空或缺少必要时间列
        """
        if data is None or len(data) == 0:
            raise PITError("data不能为空")
        if event_time_col not in data.columns:
            raise PITError(f"缺少事件时间列: {event_time_col}")

        avc = available_time_col if available_time_col is not None else event_time_col
        if avc not in data.columns:
            raise PITError(f"缺少可用时间列: {avc}")

        qts = pd.Timestamp(query_time)
        # 兼容字符串日期: 转为 datetime 后比较
        av_times = pd.to_datetime(data[avc])
        ev_times = pd.to_datetime(data[event_time_col])

        # 泄漏防护: available_time <= query_time 且 event_time <= query_time
        mask = (av_times <= qts) & (ev_times <= qts)
        visible = data.loc[mask].copy()

        # 版本对齐: 同一(event_time, 标的)多版本时取最新可用版本
        # 仅在显式提供 available_time_col(表明数据带版本)时执行去重
        if available_time_col is not None and available_time_col != event_time_col:
            group_cols = [event_time_col] + [
                c for c in ("symbol", "ticker", "code", "instrument")
                if c in visible.columns
            ]
            # 按 available_time 升序后, 每组保留最后一行(即最大可用时间版本)
            visible = visible.sort_values(avc)
            visible = visible.drop_duplicates(subset=group_cols, keep="last")

        # 按 event_time 升序输出
        visible = visible.sort_values(event_time_col).reset_index(drop=True)
        return visible

    # ------------------------------------------------------------------
    # Embargo
    # ------------------------------------------------------------------
    def apply_embargo(
        self,
        data: pd.DataFrame,
        current_time: datetime,
        event_time_col: str = "date",
    ) -> pd.DataFrame:
        """应用 Embargo 期隔离标签泄漏

        蓝图 §5.1: 时点 T 的标签(如 forward_return)只能使用 T+embargo 之前
        可用的数据。等价地, 在当前决策时点 current_time 使用标签时, 标签锚定
        时点 E 须满足 E + embargo <= current_time(标签的前瞻窗口与隔离期均已
        落入过去), 即仅保留 event_time <= current_time - embargo 的行。

        实现: 排除 event_time 落在隔离窗口 (current_time - embargo, current_time]
        内的样本, 避免标签前瞻窗口与当前决策时点重叠造成泄漏。

        注: embargo 按工作日(BDay)偏移近似"交易日"; 精确交易日历需调用方提供。

        Args:
            data: 含标签的数据, 须包含 event_time_col 列
            current_time: 当前回测决策时点
            event_time_col: 事件时间列名, 默认 "date"

        Returns:
            pd.DataFrame: 通过 embargo 过滤的数据子集, 按 event_time 升序

        Raises:
            PITError: data 为空或缺少 event_time_col 列
        """
        if data is None or len(data) == 0:
            raise PITError("data不能为空")
        if event_time_col not in data.columns:
            raise PITError(f"缺少事件时间列: {event_time_col}")

        # 隔离期截止时点: current_time 向前推 embargo 个工作日
        cutoff = pd.Timestamp(current_time) - pd.tseries.offsets.BDay(
            self.config.embargo_days
        )
        ev_times = pd.to_datetime(data[event_time_col])
        mask = ev_times <= cutoff
        safe = data.loc[mask].copy()
        safe = safe.sort_values(event_time_col).reset_index(drop=True)
        return safe

    # ------------------------------------------------------------------
    # 一致性校验
    # ------------------------------------------------------------------
    def pit_consistency_test(
        self,
        train_data: pd.DataFrame,
        backtest_data: pd.DataFrame,
        factor_col: str,
    ) -> dict:
        """训练平面与回测平面因子一致性校验

        比较同一因子在训练平面与回测平面的取值, 检测因 PIT 处理差异(如使用
        未来修正数据)导致的因子值偏差。偏差超过 consistency_threshold 即告警。

        对齐方式: 在两平面共同索引上对齐 factor_col, 计算相对偏差
            deviation = |train - backtest| / (|train| + epsilon)

        Args:
            train_data: 训练平面数据, 须含 factor_col
            backtest_data: 回测平面数据, 须含 factor_col
            factor_col: 因子列名

        Returns:
            dict: {
                "consistent": bool,        # max_deviation <= threshold
                "max_deviation": float,    # 最大相对偏差
                "violations": list[dict],  # 偏差超阈值的记录列表
            }
            其中 violations 每项形如:
                {"index": ..., "train_value": float, "backtest_value": float,
                 "deviation": float}

        Raises:
            PITError: 数据为空或缺少 factor_col 列
        """
        if train_data is None or len(train_data) == 0:
            raise PITError("train_data不能为空")
        if backtest_data is None or len(backtest_data) == 0:
            raise PITError("backtest_data不能为空")
        if factor_col not in train_data.columns:
            raise PITError(f"train_data缺少因子列: {factor_col}")
        if factor_col not in backtest_data.columns:
            raise PITError(f"backtest_data缺少因子列: {factor_col}")

        # 在共同索引上对齐因子序列
        s_train = train_data[factor_col]
        s_bt = backtest_data[factor_col]
        a, b = s_train.align(s_bt, join="inner")

        # 剔除任一平面缺失的样本
        valid = ~(a.isna() | b.isna())
        a = a[valid]
        b = b[valid]

        if len(a) == 0:
            # 无共同样本, 视为一致(无偏差可比较)
            return {"consistent": True, "max_deviation": 0.0, "violations": []}

        # 转为 numpy 数组计算相对偏差
        a_arr = np.asarray(a, dtype=np.float64)
        b_arr = np.asarray(b, dtype=np.float64)
        denom = np.abs(a_arr) + _EPSILON
        dev_arr = np.abs(a_arr - b_arr) / denom

        max_deviation = float(np.nanmax(dev_arr))
        threshold = self.config.consistency_threshold

        # 收集超阈值违规项
        violations: list[dict] = []
        over_mask = dev_arr > threshold
        if over_mask.any():
            over_idx = np.flatnonzero(over_mask)
            for i in over_idx:
                idx_val = a.index[i]
                violations.append({
                    "index": _to_serializable(idx_val),
                    "train_value": float(a_arr[i]),
                    "backtest_value": float(b_arr[i]),
                    "deviation": float(dev_arr[i]),
                })

        consistent = max_deviation <= threshold
        return {
            "consistent": consistent,
            "max_deviation": max_deviation,
            "violations": violations,
        }

    # ------------------------------------------------------------------
    # 幸存者偏差检测
    # ------------------------------------------------------------------
    def check_survivorship_bias(
        self,
        backtest_symbols: list[str],
        all_symbols: list[str],
        delisted_symbols: list[str],
    ) -> dict:
        """幸存者偏差检测

        检查回测标的集合是否遗漏已退市标的(仅保留存续标的会造成幸存者偏差,
        系统性高估策略收益)。

        Args:
            backtest_symbols: 回测中实际包含的标的代码列表
            all_symbols: 历史上曾上市的全部标的代码列表(保留用于扩展覆盖率统计)
            delisted_symbols: 已退市标的代码列表

        Returns:
            dict: {
                "has_delisted": bool,       # 回测中是否包含已退市标的
                "delisted_count": int,      # 回测中包含的已退市标的数量
                "missing_delisted": list,   # 已退市但未纳入回测的标的(偏差来源)
                "coverage_ratio": float,   # 回测标的占历史全部标的比例(越低->偏差风险越高)
            }
        """
        bt_set = set(backtest_symbols or [])
        dl_set = set(delisted_symbols or [])
        all_set = set(all_symbols or [])

        # 覆盖率: 回测标的占历史全部标的的比例(越低->幸存者偏差风险越高)
        if all_set:
            coverage_ratio = len(bt_set & all_set) / len(all_set)
        else:
            coverage_ratio = 0.0

        in_backtest = bt_set & dl_set
        missing_delisted = dl_set - bt_set
        return {
            "has_delisted": len(in_backtest) > 0,
            "delisted_count": len(in_backtest),
            "missing_delisted": sorted(missing_delisted),
            "coverage_ratio": float(coverage_ratio),
        }
