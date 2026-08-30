# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.burn_rate_alerter
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Burn Rate Alerter — v0.14.0 R200

Blindspot: SLO burn rate not tracked; error budget exhausted silently.
Risk: R200 — 36-hour burn at 10x exhausts 30-day budget; no alert until SLO already breached.

Mitigation: Multi-window burn rate alerts per Google SRE workbook methodology.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: burn_rate_alerter.py
# 层: 算法
# - id: A1
#   name_zh: ① BurnRateAlerter
#   name_en: BurnRateAlerter
#   intro: class BurnRateAlerter 源码 L70-L96
#   desc: 公共方法（定义序）: record, alerts；源码 L70-L96
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: BurnRateAlerter
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BurnWindow:
    name: str
    window_seconds: float
    target_burn_rate: float
    current_burn_rate: float = 0.0
    error_count: int = 0
    total_count: int = 0


@dataclass
class BurnRateAlerter:
    slo_pct: float = 99.9
    windows: list[BurnWindow] = field(
        default_factory=lambda: [
            BurnWindow(name="1h", window_seconds=3600, target_burn_rate=14.4),
            BurnWindow(name="6h", window_seconds=21600, target_burn_rate=6.0),
            BurnWindow(name="3d", window_seconds=259200, target_burn_rate=1.0),
        ]
    )

    def record(self, success: bool) -> None:
        for w in self.windows:
            w.total_count += 1
            if not success:
                w.error_count += 1
            if w.total_count > 0:
                error_budget_pct = (100.0 - self.slo_pct) / 100.0
                w.current_burn_rate = (
                    (w.error_count / w.total_count) / error_budget_pct if error_budget_pct > 0 else 0.0
                )

    def alerts(self) -> list[str]:
        return [
            f"{w.name} burn rate {w.current_burn_rate:.1f}x > {w.target_burn_rate}x"
            for w in self.windows
            if w.current_burn_rate > w.target_burn_rate
        ]
