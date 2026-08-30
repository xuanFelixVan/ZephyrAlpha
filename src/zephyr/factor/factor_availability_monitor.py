# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.factor_availability_monitor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] pandas; zephyr.factor.factor_base(FactorRegistry); zephyr.shared.contracts.factor_signal(CTR-002); zephyr.shared.alerts.alert_manager(惰性,告警路由); zephyr.signal_quality.degradation_monitor_base(D_SIGQC降级语义)
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 覆盖率=1-缺失率; 三级阈值80%/50%/20%分级(边界入高档); coverage<50%→is_degraded; coverage<20%→阻断信号合成; 降级状态写FactorSignal.extra供下游降权
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空注册表->coverage=0.0+BLOCKED不抛异常; 告警回调失败仅log不阻断计算
# [TESTS] tests/factor/test_factor_availability_monitor.py
# [TTL] permanent
"""



ZephyrAlpha — D_FACTOR 因子可用性监控器（CAND-FAC-006 canonical / B13-04305，合并 B2-05116 定义）。

合并定义裁定（AUD-DRAFT-001-DIGEST P0 合并对）：
  本模块为 D-SIGNAL-77 因子可用性监控器唯一 canonical 实现——
  CAND-FAC-006（B13-04305）与 CAND-FAC-007（B2-05116）为同一模块的合并定义对，
  CAND-FAC-007 信息更全（含覆盖率=1-缺失率合并定义、ONLINE 占比口径、<20% 阻断），
  两份 min_build_spec 已全部并入本实现，CAND-FAC-007 不再单独施工。

min_build_spec（合并版）：
  - 覆盖率 + 缺失比例逐日计算（覆盖率 = 1 - 缺失率；注册因子 ONLINE 状态占比）
  - 三级阈值 80%/50%/20% 分级告警（复用数据告警路由，注入式 alert_sink）
  - is_degraded 降级标记（coverage < 50%）
  - 低于 20% 阻断信号合成（block_signal_synthesis）
  - 降级状态写 FactorSignal 元数据（CTR-002 extra 字段）供下游降权

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: registry 参数
#   fields: 参数 registry（无注解）
#   code: factor_availability_monitor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: factor_availability_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① default_alert_sink
#   name_en: default_alert_sink
#   intro: 惰性装配 shared.alerts.alert_manager 告警路由（数据告警路由复用）。
#   desc: 惰性装配 shared.alerts.alert_manager 告警路由（数据告警路由复用）。 Returns: sink(severity, title, message)：…；源码 L123-L146
#   inputs: 无参数
#   outputs: Callable[[str, str, str], None]
# - id: A2
#   name_zh: ② FactorAvailabilityMonitor
#   name_en: FactorAvailabilityMonitor
#   intro: 因子覆盖率 + 缺失比例监控，三级阈值门控。
#   desc: 因子覆盖率 + 缺失比例监控，三级阈值门控。；公共方法（定义序）: compute_daily, signal_weight, annotate_signal；源码 L149-L286
#   inputs: registry alert_sink
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
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
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, ClassVar, Mapping

import pandas as pd

from zephyr.factor.factor_base import FactorRegistry
from zephyr.shared.contracts.factor_signal import FactorSignal

logger = logging.getLogger(__name__)

__all__ = [
    "AvailabilityLevel",
    "FactorAvailabilityMonitor",
    "FactorAvailabilityReport",
    "default_alert_sink",
]


class AvailabilityLevel(str, Enum):
    """可用性三级阈值分级（+放行）。"""

    OK = "ok"
    WARN = "warn"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class FactorAvailabilityReport:
    """因子可用性逐日报告。"""

    as_of: str
    registered_total: int
    online_count: int
    coverage: float
    missing_ratio: float
    level: AvailabilityLevel
    is_degraded: bool
    block_signal_synthesis: bool
    per_factor_missing: dict[str, float] = field(default_factory=dict)
    alerts: list[str] = field(default_factory=list)


def default_alert_sink() -> Callable[[str, str, str], None]:
    """惰性装配 shared.alerts.alert_manager 告警路由（数据告警路由复用）。

    Returns:
        sink(severity, title, message)：severity 取 info/warning/critical。
    """
    from zephyr.shared.alerts.alert_manager import AlertManager, AlertSeverity

    manager = AlertManager()
    _sev_map = {
        "info": AlertSeverity.INFO,
        "warning": AlertSeverity.WARNING,
        "critical": AlertSeverity.CRITICAL,
    }

    def _sink(severity: str, title: str, message: str) -> None:
        manager.raise_alert(
            title=title,
            severity=_sev_map.get(severity, AlertSeverity.WARNING),
            source="factor.availability_monitor",
            message=message,
        )

    return _sink


class FactorAvailabilityMonitor:
    """因子覆盖率 + 缺失比例监控，三级阈值门控。"""

    THRESHOLD_WARN: float = 0.80
    THRESHOLD_DEGRADED: float = 0.50
    THRESHOLD_BLOCK: float = 0.20

    _LEVEL_WEIGHT: ClassVar[dict] = {
        AvailabilityLevel.OK: 1.0,
        AvailabilityLevel.WARN: 0.5,
        AvailabilityLevel.DEGRADED: 0.25,
        AvailabilityLevel.BLOCKED: 0.0,
    }

    def __init__(
        self,
        registry=None,
        alert_sink: Callable[[str, str, str], None] | None = None,
    ) -> None:
        """
        Args:
            registry: FactorRegistry 协议对象（list_all() -> metas with factor_id）；
                None 时用全局 FactorRegistry 单例
            alert_sink: 缺失告警路由回调 (severity, title, message)；None=仅记日志
        """
        self._registry = registry if registry is not None else FactorRegistry
        self._alert_sink = alert_sink

    # ------------------------------------------------------------------
    # 逐日覆盖率计算
    # ------------------------------------------------------------------

    def compute_daily(
        self,
        factor_values: Mapping[str, pd.Series | None],
        as_of: str,
    ) -> FactorAvailabilityReport:
        """覆盖率 + 缺失比例逐日计算，三级阈值裁定 + 缺失告警。

        Args:
            factor_values: {factor_id: 因子值 Series 或 None（当日无产出）}
            as_of: 评估日期（YYYY-MM-DD）

        Returns:
            FactorAvailabilityReport（含 is_degraded / block_signal_synthesis）
        """
        metas = self._registry.list_all()
        total = len(metas)
        per_factor_missing: dict[str, float] = {}
        online = 0
        for meta in metas:
            fid = meta.factor_id
            series = factor_values.get(fid)
            if series is None or len(series) == 0:
                per_factor_missing[fid] = 1.0
                continue
            ratio = float(series.isna().mean())
            per_factor_missing[fid] = ratio
            if ratio < 1.0:
                online += 1

        coverage = online / total if total > 0 else 0.0
        level = self._classify(coverage)
        is_degraded = coverage < self.THRESHOLD_DEGRADED
        block = coverage < self.THRESHOLD_BLOCK

        alerts: list[str] = []
        fully_missing = [fid for fid, r in per_factor_missing.items() if r >= 1.0]
        if fully_missing:
            alerts.append(f"因子完全缺失 {len(fully_missing)} 个: {','.join(sorted(fully_missing))}")
        if level != AvailabilityLevel.OK:
            alerts.append(
                f"因子覆盖率 {coverage:.0%} 触发 {level.value} 级（阈值 "
                f"{self.THRESHOLD_WARN:.0%}/{self.THRESHOLD_DEGRADED:.0%}/{self.THRESHOLD_BLOCK:.0%}）"
            )
        for msg in alerts:
            severity = "critical" if level in (AvailabilityLevel.DEGRADED, AvailabilityLevel.BLOCKED) else "warning"
            self._emit(severity, f"factor_availability_{as_of}", msg)

        return FactorAvailabilityReport(
            as_of=as_of,
            registered_total=total,
            online_count=online,
            coverage=coverage,
            missing_ratio=1.0 - coverage,
            level=level,
            is_degraded=is_degraded,
            block_signal_synthesis=block,
            per_factor_missing=per_factor_missing,
            alerts=alerts,
        )

    def _classify(self, coverage: float) -> AvailabilityLevel:
        """三级阈值分级（边界入高档：0.8→OK / 0.5→WARN / 0.2→DEGRADED）。"""
        if coverage >= self.THRESHOLD_WARN:
            return AvailabilityLevel.OK
        if coverage >= self.THRESHOLD_DEGRADED:
            return AvailabilityLevel.WARN
        if coverage >= self.THRESHOLD_BLOCK:
            return AvailabilityLevel.DEGRADED
        return AvailabilityLevel.BLOCKED

    # ------------------------------------------------------------------
    # 下游降权接线（CTR-002 FactorSignal 元数据）
    # ------------------------------------------------------------------

    def signal_weight(self, report: FactorAvailabilityReport) -> float:
        """可用性对应的下游信号权重：OK=1.0 / WARN=0.5 / DEGRADED=0.25 / BLOCKED=0.0。"""
        return self._LEVEL_WEIGHT[report.level]

    def annotate_signal(self, signal: FactorSignal, report: FactorAvailabilityReport) -> FactorSignal:
        """降级状态写 FactorSignal 元数据供下游降权（CTR-002 extra 字段）。

        - extra.is_degraded / availability_level / coverage：下游可读降权依据
        - confidence 按 signal_weight 折算（D_SIGQC 降级语义对齐：不阻断仅降权，
          BLOCKED 由 block_signal_synthesis 在合成入口拦截）
        """
        weight = self.signal_weight(report)
        extra = {
            **signal.extra,
            "is_degraded": report.is_degraded,
            "availability_level": report.level.value,
            "coverage": report.coverage,
        }
        return dataclasses.replace(signal, extra=extra, confidence=signal.confidence * weight)

    # ------------------------------------------------------------------
    # 告警路由
    # ------------------------------------------------------------------

    def _emit(self, severity: str, title: str, message: str) -> None:
        if self._alert_sink is not None:
            try:
                self._alert_sink(severity, title, message)
            except Exception:  # noqa: BLE001 — 告警失败不应中断监控计算
                logger.exception("可用性告警路由回调失败")
        else:
            logger.warning("[%s] %s: %s", severity, title, message)
