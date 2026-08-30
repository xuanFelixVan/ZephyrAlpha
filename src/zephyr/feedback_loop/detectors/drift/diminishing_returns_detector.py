# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.drift.diminishing_returns_detector
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R528: DiminishingReturnsDetector
每新增Guard边际价值计算 — 防止Guard通胀

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: diminishing_returns_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① DiminishingReturnsDetector
#   name_en: DiminishingReturnsDetector
#   intro: class DiminishingReturnsDetector 源码 L63-L128
#   desc: 公共方法（定义序）: register_guard_value, analyze_diminishing_returns；源码 L63-L128
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DiminishingReturnsDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class GuardValueRecord:
    guard_id: str
    mttr_improvement: float
    reliability_improvement: float
    false_positive_rate: float
    added_at: float


@dataclass
class DiminishingReturnsDetector:
    guard_records: list[GuardValueRecord] = field(default_factory=list)
    marginal_value_threshold: float = 0.01
    recent_window: int = 8
    inflation_warning_guard_count: int = 100

    def register_guard_value(
        self,
        guard_id: str,
        mttr_improvement: float,
        reliability_improvement: float,
        false_positive_rate: float,
        added_at: float,
    ) -> None:
        self.guard_records.append(
            GuardValueRecord(
                guard_id=guard_id,
                mttr_improvement=mttr_improvement,
                reliability_improvement=reliability_improvement,
                false_positive_rate=false_positive_rate,
                added_at=added_at,
            )
        )

    def analyze_diminishing_returns(self) -> dict:
        total_guards = len(self.guard_records)
        if total_guards < self.recent_window:
            return {
                "status": "insufficient_data",
                "total_guards": total_guards,
            }

        sorted_records = sorted(self.guard_records, key=lambda r: r.added_at)

        early_batch = sorted_records[: max(total_guards // 3, self.recent_window)]
        recent_batch = sorted_records[-self.recent_window :]

        early_avg_value = self._avg_value(early_batch)
        recent_avg_value = self._avg_value(recent_batch)

        value_ratio = recent_avg_value / max(early_avg_value, 0.001)
        is_diminishing = recent_avg_value < self.marginal_value_threshold

        inflation_risk = total_guards > self.inflation_warning_guard_count

        return {
            "total_guards": total_guards,
            "early_avg_value": round(early_avg_value, 4),
            "recent_avg_value": round(recent_avg_value, 4),
            "value_ratio": round(value_ratio, 3),
            "is_diminishing": is_diminishing or value_ratio < 0.3,
            "inflation_risk": inflation_risk,
            "recommendation": (
                "STOP_ADDING_GUARDS"
                if is_diminishing
                else "CAUTION_diminishing"
                if value_ratio < 0.5
                else "CONTINUE_monitor"
            ),
        }

    @staticmethod
    def _avg_value(records: list[GuardValueRecord]) -> float:
        if not records:
            return 0.0
        return sum(r.mttr_improvement + r.reliability_improvement for r in records) / len(records)
