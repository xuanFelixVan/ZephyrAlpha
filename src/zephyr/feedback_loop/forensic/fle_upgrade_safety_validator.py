# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.forensic.fle_upgrade_safety_validator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
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
R529: FLEUpgradeSafetyValidator
FLE自身代码升级兼容性校验 — 持久化状态/阈值/规则 vs 新版本

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: fle_upgrade_safety_validator.py
# 层: 算法
# - id: A1
#   name_zh: ① FLEUpgradeSafetyValidator
#   name_en: FLEUpgradeSafetyValidator
#   intro: class FLEUpgradeSafetyValidator 源码 L65-L131
#   desc: 公共方法（定义序）: register_current_state_schema, validate_upgrade, record_successful_upgrade；源码 L65-L131
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: FLEUpgradeSafetyValidator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import hashlib
import json
from dataclasses import dataclass, field


@dataclass
class UpgradeSafetyResult:
    version_from: str
    version_to: str
    compatible: bool
    breaking_changes: list[str]
    state_compatibility: dict[str, bool]


@dataclass
class FLEUpgradeSafetyValidator:
    current_version: str = "0.41.0"
    state_schema_hash: str = ""
    known_compatible_versions: set[str] = field(default_factory=set)
    upgrade_log: list[UpgradeSafetyResult] = field(default_factory=list)

    def register_current_state_schema(self, schema: dict) -> str:
        h = hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()[:16]
        self.state_schema_hash = h
        self.known_compatible_versions.add(self.current_version)
        return h

    def validate_upgrade(
        self,
        target_version: str,
        target_schema_hash: str,
        persisted_state_keys: list[str],
    ) -> dict:
        breaking_changes = []

        if target_schema_hash != self.state_schema_hash:
            breaking_changes.append(f"schema_hash_mismatch: {self.state_schema_hash[:8]} vs {target_schema_hash[:8]}")

        state_compatibility = {}
        for key in persisted_state_keys:
            state_compatibility[key] = key in self._get_expected_persisted_keys()

        missing_keys = [k for k, v in state_compatibility.items() if not v]
        if missing_keys:
            breaking_changes.append(f"missing_state_keys: {missing_keys}")

        compatible = len(breaking_changes) == 0

        result = UpgradeSafetyResult(
            version_from=self.current_version,
            version_to=target_version,
            compatible=compatible,
            breaking_changes=breaking_changes,
            state_compatibility=state_compatibility,
        )
        self.upgrade_log.append(result)
        if len(self.upgrade_log) > 20:
            self.upgrade_log = self.upgrade_log[-20:]

        return {
            "can_upgrade": compatible,
            "version_from": self.current_version,
            "version_to": target_version,
            "breaking_changes": breaking_changes,
            "state_keys_verified": len(state_compatibility),
            "recommendation": ("SAFE_TO_UPGRADE" if compatible else "BLOCKED_breaking_changes"),
        }

    def _get_expected_persisted_keys(self) -> set[str]:
        return {
            "thresholds",
            "rules",
            "baselines",
            "config_hashes",
            "guard_states",
            "cycle_count",
            "self_model",
        }

    def record_successful_upgrade(self, new_version: str) -> None:
        self.current_version = new_version
        self.known_compatible_versions.add(new_version)
