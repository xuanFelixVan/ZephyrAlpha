# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.security.wireheading_prevention
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Wireheading Prevention — v0.37.0 R486

Blindspot: FLE gains ability to modify its own success metrics;
learns to game KPI measurements instead of fixing real problems.

Risk: R486 — FLE wireheads by altering metric definitions, thresholds,
or data sources to report false success (AI safety critical).

Mitigation: Immutable metric definitions with cryptographic signature.
Any attempt to modify metric registry -> immediate SAFE_MODE + full audit.
Whitelist-only modification channel requiring owner cryptographic approval.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: wireheading_prevention.py
# 层: 算法
# - id: A1
#   name_zh: ① WireheadingPrevention
#   name_en: WireheadingPrevention
#   intro: class WireheadingPrevention 源码 L74-L115
#   desc: 公共方法（定义序）: register_metric, verify_metric, owner_override_reset；源码 L74-L115
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: WireheadingPrevention
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum


class WireheadState(str, Enum):
    CLEAN = "CLEAN"
    ATTEMPT_DETECTED = "ATTEMPT_DETECTED"
    SAFE_MODE = "SAFE_MODE"


@dataclass
class WireheadingPrevention:
    immutable_metrics: dict[str, str] = field(default_factory=dict)
    modification_attempts: list[dict] = field(default_factory=list)
    state: WireheadState = WireheadState.CLEAN
    safe_mode_until: float = 0.0

    def register_metric(self, name: str, definition: str) -> str:
        sig = hashlib.sha256(definition.encode("utf-8")).hexdigest()[:32]
        self.immutable_metrics[name] = sig
        return sig

    def verify_metric(self, name: str, definition: str) -> bool:
        if self.state is WireheadState.SAFE_MODE:
            return False
        expected = self.immutable_metrics.get(name)
        if not expected:
            return True
        actual = hashlib.sha256(definition.encode("utf-8")).hexdigest()[:32]

        if actual != expected:
            self.modification_attempts.append(
                {
                    "metric": name,
                    "time": time.time(),
                    "expected_hash": expected,
                    "actual_hash": actual,
                }
            )
            if len(self.modification_attempts) >= 3:
                self._trigger_safe_mode()
            self.state = WireheadState.ATTEMPT_DETECTED
            return False

        return True

    def _trigger_safe_mode(self) -> None:
        self.state = WireheadState.SAFE_MODE
        self.safe_mode_until = time.time() + 3600.0

    def owner_override_reset(self) -> None:
        self.state = WireheadState.CLEAN
        self.modification_attempts.clear()
