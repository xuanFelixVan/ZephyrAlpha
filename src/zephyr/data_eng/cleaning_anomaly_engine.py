# [BLUEPRINT] MOD-DATA_ENG | (pending)
# [MODULE] zephyr.data_eng.cleaning_anomaly_engine
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] pandas; zephyr.data.alerter(惰性, 告警路由复用B13-04267)
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 前值填充连续缺失≤3根; 超限剔除并标quality_flag; 全部修复动作留审计; 剔除必进人工审核队列
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空帧/缺列->空检出+空修复结果不抛异常; 未知列缺失按missing_pattern处理
# [TESTS] tests/zephyr/data/test_cleaning_anomaly_engine.py
# [TTL] permanent
"""



ZephyrAlpha — D_DATA_ENG 数据清洗与异常引擎（CAND-DATENG-001 / B1-00606）。

min_build_spec（AUD-DRAFT-001-DIGEST P0）：
  - 清洗规则库：价格跳变 / 复权断点 / 重复bar / 量能异常 / 缺失模式
  - 自动修复策略：跨源仲裁 / 前值填充≤3根 / 剔除并标 quality_flag
  - 修复审计日志 + 人工审核队列
  - 多维异常告警路由复用 B13-04267（zephyr.data.alerter，惰性装配可注入）

设计要点：
  - 纯 pandas 内存计算，不触网不触库；告警经 alert_sink 依赖注入，测试零副作用
  - 修复优先序：跨源仲裁 > 前值填充 > 剔除标记（能修不剔）
  - quality_flag 取值：ok / arbitrated / filled（剔除行出列，标记入 audit 与 quality_flags）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: price_jump_pct 参数
#   fields: 参数 price_jump_pct（无注解）
#   code: cleaning_anomaly_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: price_jump_z 参数
#   fields: 参数 price_jump_z（无注解）
#   code: cleaning_anomaly_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: volume_spike_mult 参数
#   fields: 参数 volume_spike_mult（无注解）
#   code: cleaning_anomaly_engine.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: volume_z 参数
#   fields: 参数 volume_z（无注解）
#   code: cleaning_anomaly_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① default_alert_sink
#   name_en: default_alert_sink
#   intro: 惰性装配 zephyr.data.alerter 告警路由（复用 B13-04267 链路）。
#   desc: 惰性装配 zephyr.data.alerter 告警路由（复用 B13-04267 链路）。 Returns: sink(level, title, message)：leve…；源码 L157-L170
#   inputs: 无参数
#   outputs: Callable[[str, str, str], None]
# - id: A2
#   name_zh: ② CleaningAnomalyEngine
#   name_en: CleaningAnomalyEngine
#   intro: 清洗规则库 + 自动修复策略引擎。
#   desc: 清洗规则库 + 自动修复策略引擎。；公共方法（定义序）: detect, repair；源码 L173-L454
#   inputs: price_jump_pct price_jump_z volume_spike_mult volume_z alert_sink
#   outputs: 返回值
#   （注：A2 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: Callable[[str, str, str], None]
#   name_en: Callable[[str, str, str], None]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

import pandas as pd

logger = logging.getLogger(__name__)

__all__ = [
    "AnomalyFinding",
    "AnomalyRule",
    "CleaningAnomalyEngine",
    "RepairAuditRecord",
    "RepairResult",
    "RepairStrategy",
    "default_alert_sink",
]

_OHLCV = ("open", "high", "low", "close", "volume")


class AnomalyRule(str, Enum):
    """清洗规则库五类异常。"""

    PRICE_JUMP = "price_jump"
    ADJ_BREAK = "adj_break"
    DUPLICATE_BAR = "duplicate_bar"
    VOLUME_SPIKE = "volume_spike"
    MISSING_PATTERN = "missing_pattern"


class RepairStrategy(str, Enum):
    """自动修复策略。"""

    CROSS_SOURCE_ARBITRATE = "cross_source_arbitrate"
    FORWARD_FILL = "forward_fill"
    DROP_AND_FLAG = "drop_and_flag"


@dataclass(frozen=True)
class AnomalyFinding:
    """单条异常检出。"""

    rule: AnomalyRule
    symbol: str
    timestamp: str
    detail: str
    severity: str = "warn"


@dataclass(frozen=True)
class RepairAuditRecord:
    """修复审计日志单条（一行一记录）。"""

    rule: str
    symbol: str
    timestamp: str
    strategy: RepairStrategy
    detail: str


@dataclass
class RepairResult:
    """修复闭环产出：净数据 + 审计日志 + 人工审核队列 + 质量标记。"""

    data: pd.DataFrame
    audit_log: list[RepairAuditRecord] = field(default_factory=list)
    review_queue: list[AnomalyFinding] = field(default_factory=list)
    quality_flags: dict[str, str] = field(default_factory=dict)


def default_alert_sink() -> Callable[[str, str, str], None]:
    """惰性装配 zephyr.data.alerter 告警路由（复用 B13-04267 链路）。

    Returns:
        sink(level, title, message)：level 取 INFO/WARN/ERROR/CRITICAL。
    """
    from zephyr.data.alerter import Alerter

    alerter = Alerter()

    def _sink(level: str, title: str, message: str) -> None:
        alerter.notify(task_id=title, error=message, level=level, source="data_eng.cleaning")

    return _sink


class CleaningAnomalyEngine:
    """清洗规则库 + 自动修复策略引擎。"""

    MAX_FORWARD_FILL: int = 3

    def __init__(
        self,
        price_jump_pct: float = 0.20,
        price_jump_z: float = 8.0,
        volume_spike_mult: float = 20.0,
        volume_z: float = 6.0,
        alert_sink: Callable[[str, str, str], None] | None = None,
    ) -> None:
        """
        Args:
            price_jump_pct: 单根涨跌幅绝对值超此比例即判价格跳变（A股±20%涨停外即异常）
            price_jump_z: 收益率 z-score 备选阈值（std>0 时生效）
            volume_spike_mult: 量能超中位数此倍数即判量能异常
            volume_z: 量能 z-score 备选阈值
            alert_sink: 告警路由回调 (level, title, message)；None=仅记日志
        """
        self._price_jump_pct = price_jump_pct
        self._price_jump_z = price_jump_z
        self._volume_spike_mult = volume_spike_mult
        self._volume_z = volume_z
        self._alert_sink = alert_sink

    # ------------------------------------------------------------------
    # 检出
    # ------------------------------------------------------------------

    def detect(self, df: pd.DataFrame, symbol: str = "") -> list[AnomalyFinding]:
        """按清洗规则库检出五类异常。空帧/缺列返回空列表。"""
        if df is None or df.empty:
            return []
        findings: list[AnomalyFinding] = []
        findings += self._detect_price_jump(df, symbol)
        findings += self._detect_adj_break(df, symbol)
        findings += self._detect_duplicate_bar(df, symbol)
        findings += self._detect_volume_spike(df, symbol)
        findings += self._detect_missing(df, symbol)
        return findings

    def _detect_price_jump(self, df: pd.DataFrame, symbol: str) -> list[AnomalyFinding]:
        if "close" not in df.columns:
            return []
        rets = df["close"].astype(float).pct_change(fill_method=None)
        std = float(rets.std()) if len(rets) > 1 else 0.0
        mean = float(rets.mean()) if len(rets) else 0.0
        out: list[AnomalyFinding] = []
        for ts, r in rets.items():
            if pd.isna(r):
                continue
            fired = abs(r) > self._price_jump_pct
            if not fired and std > 0:
                fired = abs((r - mean) / std) > self._price_jump_z
            if fired:
                out.append(
                    AnomalyFinding(
                        rule=AnomalyRule.PRICE_JUMP,
                        symbol=symbol,
                        timestamp=str(ts),
                        detail=f"单根收益率 {r:+.2%} 超阈值 {self._price_jump_pct:.0%}",
                        severity="critical",
                    )
                )
        return out

    def _detect_adj_break(self, df: pd.DataFrame, symbol: str) -> list[AnomalyFinding]:
        if "adj_factor" not in df.columns:
            return []
        adj = df["adj_factor"].astype(float)
        out: list[AnomalyFinding] = []
        prev: float | None = None
        for ts, v in adj.items():
            if prev is not None and prev > 0 and not pd.isna(v):
                ratio = v / prev
                if ratio > 2.0 or ratio < 0.5:
                    out.append(
                        AnomalyFinding(
                            rule=AnomalyRule.ADJ_BREAK,
                            symbol=symbol,
                            timestamp=str(ts),
                            detail=f"复权因子突变 ratio={ratio:.2f}（[0.5,2.0] 外）",
                            severity="critical",
                        )
                    )
            prev = v
        return out

    def _detect_duplicate_bar(self, df: pd.DataFrame, symbol: str) -> list[AnomalyFinding]:
        dup_mask = df.index.duplicated(keep=False)
        return [
            AnomalyFinding(
                rule=AnomalyRule.DUPLICATE_BAR,
                symbol=symbol,
                timestamp=str(ts),
                detail="重复bar（同一时间戳多行）",
            )
            for ts in df.index[dup_mask]
        ]

    def _detect_volume_spike(self, df: pd.DataFrame, symbol: str) -> list[AnomalyFinding]:
        if "volume" not in df.columns:
            return []
        vol = df["volume"].astype(float)
        median = float(vol.median())
        std = float(vol.std()) if len(vol) > 1 else 0.0
        mean = float(vol.mean()) if len(vol) else 0.0
        out: list[AnomalyFinding] = []
        for ts, v in vol.items():
            if pd.isna(v):
                continue
            fired = median > 0 and v > median * self._volume_spike_mult
            if not fired and std > 0:
                fired = (v - mean) / std > self._volume_z
            if fired:
                out.append(
                    AnomalyFinding(
                        rule=AnomalyRule.VOLUME_SPIKE,
                        symbol=symbol,
                        timestamp=str(ts),
                        detail=f"量能 {v:.0f} 超中位数 {self._volume_spike_mult:.0f}x（median={median:.0f}）",
                    )
                )
        return out

    def _detect_missing(self, df: pd.DataFrame, symbol: str) -> list[AnomalyFinding]:
        cols = [c for c in _OHLCV if c in df.columns]
        if not cols:
            return []
        mask = df[cols].isna().any(axis=1)
        return [
            AnomalyFinding(
                rule=AnomalyRule.MISSING_PATTERN,
                symbol=symbol,
                timestamp=str(ts),
                detail="OHLCV 存在缺失字段",
            )
            for ts in df.index[mask]
        ]

    # ------------------------------------------------------------------
    # 修复
    # ------------------------------------------------------------------

    def repair(
        self,
        df: pd.DataFrame,
        alt_source: pd.DataFrame | None = None,
        symbol: str = "",
    ) -> RepairResult:
        """自动修复闭环：跨源仲裁 > 前值填充≤3根 > 剔除并标 quality_flag。

        Args:
            df: 待清洗 bar 帧（datetime index + OHLCV 列）
            alt_source: 备用数据源同构帧（跨源仲裁取值）
            symbol: 标的代码（审计/告警用）

        Returns:
            RepairResult（净数据 + 审计日志 + 人工审核队列 + 质量标记）
        """
        result = RepairResult(data=df.copy() if df is not None else pd.DataFrame())
        if result.data.empty:
            return result

        work = result.data
        if "quality_flag" not in work.columns:
            work["quality_flag"] = "ok"

        # 1) 重复bar：去重留首行，审计留痕
        dup_mask = work.index.duplicated(keep="first")
        for ts in work.index[dup_mask]:
            self._record(
                result,
                symbol,
                ts,
                RepairStrategy.DROP_AND_FLAG,
                "重复bar剔除（留首行）",
                rule=AnomalyRule.DUPLICATE_BAR,
            )
        work = work[~dup_mask]

        # 2) 缺失行：先跨源仲裁
        cols = [c for c in _OHLCV if c in work.columns]
        missing_rows = [ts for ts in work.index if work.loc[ts, cols].isna().any()]
        for ts in missing_rows:
            if alt_source is not None and ts in alt_source.index:
                alt_row = alt_source.loc[ts]
                fillable = [
                    c for c in cols if pd.isna(work.loc[ts, c]) and c in alt_row.index and not pd.isna(alt_row[c])
                ]
                if fillable:
                    for c in fillable:
                        work.loc[ts, c] = alt_row[c]
                    if not work.loc[ts, cols].isna().any():
                        work.loc[ts, "quality_flag"] = "arbitrated"
                        result.quality_flags[str(ts)] = "arbitrated"
                        self._record(
                            result, symbol, ts, RepairStrategy.CROSS_SOURCE_ARBITRATE, f"跨源仲裁补齐字段 {fillable}"
                        )
                        continue

        # 3) 剩余缺失：按连续 run 判定 前值填充(≤3) / 剔除(>3)
        for run in self._missing_runs(work, cols):
            if len(run) <= self.MAX_FORWARD_FILL:
                prev_pos = work.index.get_loc(run[0]) - 1
                prev_ts = work.index[prev_pos] if prev_pos >= 0 else None
                for ts in run:
                    if prev_ts is not None:
                        for c in cols:
                            if pd.isna(work.loc[ts, c]):
                                work.loc[ts, c] = work.loc[prev_ts, c]
                    work.loc[ts, "quality_flag"] = "filled"
                    result.quality_flags[str(ts)] = "filled"
                    self._record(result, symbol, ts, RepairStrategy.FORWARD_FILL, "前值填充（≤3根）")
            else:
                for ts in run:
                    result.review_queue.append(
                        AnomalyFinding(
                            rule=AnomalyRule.MISSING_PATTERN,
                            symbol=symbol,
                            timestamp=str(ts),
                            detail=f"连续缺失 {len(run)} 根超前值填充上限，剔除待人工审核",
                            severity="critical",
                        )
                    )
                    result.quality_flags[str(ts)] = "dropped"
                    self._record(
                        result, symbol, ts, RepairStrategy.DROP_AND_FLAG, f"连续缺失 {len(run)} 根>3，剔除标记"
                    )
                self._alert(
                    "ERROR",
                    f"cleaning_drop_{symbol or 'unknown'}",
                    f"标的 {symbol or 'N/A'} 连续缺失 {len(run)} 根超限剔除 {len(run)} 行（{run[0]}~{run[-1]}），已入人工审核队列",
                )
                work = work.drop(index=run)

        result.data = work
        return result

    def _missing_runs(self, work: pd.DataFrame, cols: list[str]) -> list[list]:
        """剩余缺失行按连续性分组（逐行扫描，相邻 NaN 行归同一 run）。"""
        runs: list[list] = []
        current: list = []
        for ts in work.index:
            if cols and work.loc[ts, cols].isna().any():
                current.append(ts)
            elif current:
                runs.append(current)
                current = []
        if current:
            runs.append(current)
        return runs

    def _record(
        self,
        result: RepairResult,
        symbol: str,
        ts,
        strategy: RepairStrategy,
        detail: str,
        rule: AnomalyRule = AnomalyRule.MISSING_PATTERN,
    ) -> None:
        result.audit_log.append(
            RepairAuditRecord(
                rule=rule.value,
                symbol=symbol,
                timestamp=str(ts),
                strategy=strategy,
                detail=detail,
            )
        )

    def _alert(self, level: str, title: str, message: str) -> None:
        if self._alert_sink is not None:
            try:
                self._alert_sink(level, title, message)
            except Exception:  # noqa: BLE001 — 告警失败不应中断修复主流程
                logger.exception("清洗告警路由回调失败")
        else:
            logger.warning("[%s] %s: %s", level, title, message)
