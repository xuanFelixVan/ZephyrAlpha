# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.correlation.external_validation_checkpoint
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
R524: ExternalValidationCheckpoint
Godel边界人工升级触发条件 — 连续失败/共识低于阈值/未知状态空间

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: external_validation_checkpoint.py
# 层: 算法
# - id: A1
#   name_zh: ① ExternalValidationCheckpoint
#   name_en: ExternalValidationCheckpoint
#   intro: class ExternalValidationCheckpoint 源码 L62-L140
#   desc: 公共方法（定义序）: hash_in_known_variants, record_self_mod_failure, record_self_mod_success, check_guard_consensus, c…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ExternalValidationCheckpoint
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field
from enum import Enum


class EscalationReason(str, Enum):
    CONSECUTIVE_SELF_MOD_FAILURES = "consecutive_self_mod_failures"
    LOW_GUARD_CONSENSUS = "low_guard_consensus"
    UNKNOWN_STATE_SPACE = "unknown_state_space"
    CRITICAL_METRIC_DEVIATION = "critical_metric_deviation"


@dataclass
class ExternalValidationCheckpoint:
    consecutive_self_mod_failures: int = 0

    def hash_in_known_variants(self, h) -> bool:
        """公共接口：hash_in_known_variants（Stage 4 公共化）。"""
        return self._hash_in_known_variants(h)

    max_consecutive_failures: int = 3
    guard_consensus_threshold: float = 0.6
    known_state_space_hash: str = ""
    escalation_log: list[dict] = field(default_factory=list)
    owner_alerted: bool = False

    def record_self_mod_failure(self) -> str | None:
        self.consecutive_self_mod_failures += 1
        if self.consecutive_self_mod_failures >= self.max_consecutive_failures:
            return self._escalate(
                EscalationReason.CONSECUTIVE_SELF_MOD_FAILURES,
                {
                    "consecutive_failures": self.consecutive_self_mod_failures,
                },
            )
        return None

    def record_self_mod_success(self) -> None:
        self.consecutive_self_mod_failures = 0

    def check_guard_consensus(self, agree_count: int, total_count: int) -> str | None:
        if total_count == 0:
            return None
        ratio = agree_count / total_count
        if ratio < self.guard_consensus_threshold:
            return self._escalate(
                EscalationReason.LOW_GUARD_CONSENSUS,
                {
                    "agree_count": agree_count,
                    "total_count": total_count,
                    "consensus_ratio": round(ratio, 3),
                },
            )
        return None

    def check_state_space(self, current_state_hash: str) -> str | None:
        if self.known_state_space_hash and current_state_hash != self.known_state_space_hash:
            if not self._hash_in_known_variants(current_state_hash):
                return self._escalate(
                    EscalationReason.UNKNOWN_STATE_SPACE,
                    {
                        "current_hash": current_state_hash[:16],
                        "known_hash": self.known_state_space_hash[:16],
                    },
                )
        return None

    def register_known_state(self, state_hash: str) -> None:
        self.known_state_space_hash = state_hash
        self._known_variants: set[str] = getattr(self, "_known_variants", set())
        self._known_variants.add(state_hash)

    def _hash_in_known_variants(self, h: str) -> bool:
        variants = getattr(self, "_known_variants", set())
        return h in variants

    def _escalate(self, reason: EscalationReason, details: dict) -> str:
        entry = {
            "reason": reason.value,
            "details": details,
            "requires_human_intervention": True,
        }
        self.escalation_log.append(entry)
        self.owner_alerted = True
        return reason.value

    def get_pending_escalations(self) -> list[dict]:
        return [e for e in self.escalation_log if e.get("acknowledged") is not True]

    def acknowledge(self, escalation_index: int) -> None:
        if 0 <= escalation_index < len(self.escalation_log):
            self.escalation_log[escalation_index]["acknowledged"] = True
