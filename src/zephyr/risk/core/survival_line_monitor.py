# [BLUEPRINT] 90_methodology_open_questions.md §16（v2.0.0 裁定）
# [MODULE] zephyr.risk.core.survival_line_monitor
# [DOMAIN] D_RISK
# [DEPENDENCIES] 无（纯判定）
# [CONSUMERS] 55 号 KPI 监控/复盘编排（接线待排期，本批仅交付模块本体）；告警通道复用 alert_rules.yaml（ALERT-KPI-001/002）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 失败指标优先于生存线突破；健康/卓越线配置占位默认不启用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法输入→ValueError
# [TESTS] tests/risk/core/test_survival_line_monitor.py
# [A_module] module_id=MOD-RK-KPI | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_RISK — 生存线监控（90 号 Phase2 项，#16 系统级成功指标修订采纳）

裁定真源：90_methodology_open_questions.md §16（v2.0.0）：
  ① 生存线（风控属性，上线即锁死）：滚动 12 个月超额>0 且 MaxDD<15% 且 Sharpe≥0.8
     （替换原"年化超额≥10%、Sharpe≥1.0"拍脑袋值；2026 实证锚点：私募量化多头
     上半年平均超额仅 3.11%，Sharpe 1.0-2.0 为专业合格线）；
     失败指标：连续 6 个月亏损 / 回撤>25%（与 4 级 Protocol Level4 一致）；
  ② 健康/卓越线暂缓定死——运行 6-12 个月（≥30 个收益观测点）后用实盘分布校准，
     本模块仅以配置占位（enabled=False）。

注意：本模块为 90 号 Phase2 交付物，MATURITY=testing；告警发射/复盘编排接线
挂起待 Owner（宪章 B-007 纪律）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

_logger = logging.getLogger(__name__)

__all__ = [
    "HealthExcellenceConfig",
    "SurvivalInput",
    "SurvivalLineConfig",
    "SurvivalLineResult",
    "SurvivalStatus",
    "evaluate_survival_line",
]


class SurvivalStatus(str, Enum):
    """生存线评估状态（严重度递增）。"""

    OK = "ok"
    SURVIVAL_BREACH = "survival_breach"  # 破生存线→降仓/关停评估
    FAILURE = "failure"                  # 触失败指标→失败处置（对齐 Level4）


@dataclass(frozen=True)
class SurvivalLineConfig:
    """生存线阈值配置（90 号 §16 裁定①默认值）。"""

    window_months: int = 12                    # 滚动窗口（月）
    excess_return_min: float = 0.0             # 超额须 >0
    max_drawdown_limit: float = 0.15           # MaxDD 须 <15%
    sharpe_min: float = 0.8                    # Sharpe 须 ≥0.8
    fail_consecutive_loss_months: int = 6      # 连续 6 个月亏损→失败
    fail_drawdown: float = 0.25                # 回撤 >25%→失败（对齐 Level4）


@dataclass(frozen=True)
class HealthExcellenceConfig:
    """健康/卓越线配置占位（90 号 §16 裁定②：实盘 6-12 月校准后启用）。"""

    enabled: bool = False


@dataclass(frozen=True)
class SurvivalInput:
    """生存线评估输入（滚动窗口口径）。"""

    excess_return_12m: float        # 滚动 12 个月超额收益
    max_drawdown: float             # 最大回撤（正数，如 0.15=15%）
    sharpe: float                   # Sharpe
    consecutive_loss_months: int    # 连续亏损月数


@dataclass(frozen=True)
class SurvivalLineResult:
    """生存线评估结果（可审计）。"""

    status: SurvivalStatus
    breaches: list[str]


def evaluate_survival_line(
    metrics: SurvivalInput,
    config: SurvivalLineConfig | None = None,
) -> SurvivalLineResult:
    """评估生存线/失败指标。

    判定顺序：失败指标优先（更严重），其次生存线。
    """
    if metrics.max_drawdown < 0:
        raise ValueError("max_drawdown 必须为非负（回撤以正数计）")
    if metrics.consecutive_loss_months < 0:
        raise ValueError("consecutive_loss_months 不能为负")
    cfg = config or SurvivalLineConfig()

    failures: list[str] = []
    if metrics.consecutive_loss_months >= cfg.fail_consecutive_loss_months:
        failures.append(
            f"连续亏损 {metrics.consecutive_loss_months} 个月 ≥ {cfg.fail_consecutive_loss_months}"
        )
    if metrics.max_drawdown > cfg.fail_drawdown:
        failures.append(f"回撤 {metrics.max_drawdown:.2%} > {cfg.fail_drawdown:.0%}（对齐 Level4）")
    if failures:
        _logger.warning("Survival line FAILURE: %s", failures)
        return SurvivalLineResult(status=SurvivalStatus.FAILURE, breaches=failures)

    breaches: list[str] = []
    if metrics.excess_return_12m <= cfg.excess_return_min:
        breaches.append(
            f"滚动 {cfg.window_months} 个月超额 {metrics.excess_return_12m:.2%} ≤ {cfg.excess_return_min:.0%}"
        )
    if metrics.max_drawdown >= cfg.max_drawdown_limit:
        breaches.append(
            f"MaxDD {metrics.max_drawdown:.2%} ≥ {cfg.max_drawdown_limit:.0%}"
        )
    if metrics.sharpe < cfg.sharpe_min:
        breaches.append(f"Sharpe {metrics.sharpe:.2f} < {cfg.sharpe_min}")

    if breaches:
        _logger.warning("Survival line breach: %s", breaches)
        return SurvivalLineResult(status=SurvivalStatus.SURVIVAL_BREACH, breaches=breaches)
    return SurvivalLineResult(status=SurvivalStatus.OK, breaches=[])
