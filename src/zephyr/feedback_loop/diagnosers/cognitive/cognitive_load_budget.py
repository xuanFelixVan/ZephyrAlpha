# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive.cognitive_load_budget
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
Cognitive Load Budget — v0.16.0 R223

Blindspot: Owner decision fatigue unmodeled; notification rate constant regardless of owner state.
Risk: R223 — 1-person operator overwhelmed; critical alerts missed from context switching.

Mitigation: Owner cognitive load budget tracking with adaptive notification pacing.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: cognitive_load_budget.py
# 层: 算法
# - id: A1
#   name_zh: ① CognitiveLoadBudget
#   name_en: CognitiveLoadBudget
#   intro: class CognitiveLoadBudget 源码 L69-L92
#   desc: 公共方法（定义序）: request, defer；源码 L69-L92
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CognitiveLoadBudget
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class DecisionRecord:
    decision_id: str
    severity: int
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False


@dataclass
class CognitiveLoadBudget:
    max_decisions_per_hour: int = 12
    max_decisions_per_day: int = 50
    fatigue_weight_severity_high: float = 3.0
    decisions_hourly: list[float] = field(default_factory=list)
    decisions_daily: list[float] = field(default_factory=list)
    fatigue_score: float = 0.0

    def request(self, decision_id: str, severity: int) -> bool:
        now = time.time()
        self.decisions_hourly = [t for t in self.decisions_hourly if now - t < 3600]
        self.decisions_daily = [t for t in self.decisions_daily if now - t < 86400]
        weighted_hourly = sum(severity / 10.0 * self.fatigue_weight_severity_high for t in self.decisions_hourly)
        if weighted_hourly > self.max_decisions_per_hour:
            return False
        if len(self.decisions_daily) >= self.max_decisions_per_day:
            return False
        self.decisions_hourly.append(now)
        self.decisions_daily.append(now)
        self.fatigue_score = len(self.decisions_hourly) / self.max_decisions_per_hour
        return True

    def defer(self, decision_id: str, delay_seconds: float) -> None:
        pass
