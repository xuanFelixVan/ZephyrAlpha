# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_silent_failure
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Silent Failure Detector
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

静默失败检测引擎
================
检测 Skill 运行时产生的"无错误但产出劣质"的静默失败:
  1. OutputTruncation: 输出被截断但无报错
  2. PartialSuccess: 5 项检查中 3 项过但 2 项默默失败
  3. AssumptionViolation: Skill 的前提条件实际不满足但未告警
  4. DeterministicNonIdempotency: 同一输入两次执行结果不一致
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any


class SilentFailureDetector:
    """静默失败检测器"""

    ANOMALY_TRUNCATION = "output_truncation"
    ANOMALY_PARTIAL_SUCCESS = "partial_success"
    ANOMALY_ASSUMPTION = "assumption_violation"
    ANOMALY_NON_IDEMPOTENT = "non_idempotent"

    _TRUNCATION_INDICATORS = [
        r"\.\.\.$",
        r"\.\.\.\s*$",
        r"truncated",
        r"\[.*truncated.*\]",
        r"output exceeded",
        r"(?:some|部分)\s+(?:content|characters)\s+(?:truncated|removed|skipped)",
    ]

    _PARTIAL_SUCCESS_INDICATORS = [
        r"partially\s+(?:completed|successful|done)",
        r"部分完成",
        r"(?:some|部分)\s+(?:checks?\s+)?(?:failed|失败)",
        r"\d+/\d+\s+(?:passed|通过)",
    ]

    _ASSUMPTION_INDICATORS = [
        r"(?:assumed|assuming|assumes?)\s+(?:that\s+)?",
        r"(?:expected|expecting)\s+(?:that\s+)?.*(?:but|然而|却)",
        r"前提.*(?:不满足|未满足|缺失)",
    ]

    def __init__(self):
        self._execution_history: dict[str, list[dict[str, Any]]] = {}
        self._anomalies: list[dict[str, Any]] = []

    def _check_truncation(self, output: str) -> tuple[bool, dict[str, Any]]:
        for pattern in self._TRUNCATION_INDICATORS:
            found = re.findall(pattern, output[-500:], re.IGNORECASE)
            if found:
                return True, {
                    "type": self.ANOMALY_TRUNCATION,
                    "pattern_matched": pattern,
                    "found_instances": found[:3],
                    "output_tail": output[-200:],
                }

        lines = output.split("\n")
        if len(lines) > 2 and lines[-1].strip() == "" and lines[-2].strip().endswith("..."):
            return True, {
                "type": self.ANOMALY_TRUNCATION,
                "pattern_matched": "lines_end_with_ellipsis",
                "last_line": lines[-1][:100],
            }

        return False, {}

    def _check_partial_success(self, output: str) -> tuple[bool, dict[str, Any]]:
        for pattern in self._PARTIAL_SUCCESS_INDICATORS:
            if re.search(pattern, output, re.IGNORECASE):
                ratio_match = re.search(r"(\d+)/(\d+)", output)
                if ratio_match:
                    passed = int(ratio_match.group(1))
                    total = int(ratio_match.group(2))
                    if passed < total:
                        return True, {
                            "type": self.ANOMALY_PARTIAL_SUCCESS,
                            "passed": passed,
                            "total": total,
                            "failure_ratio": (total - passed) / total,
                        }

                return True, {
                    "type": self.ANOMALY_PARTIAL_SUCCESS,
                    "pattern": pattern,
                }

        return False, {}

    def _check_assumptions(self, output: str) -> tuple[bool, dict[str, Any]]:
        violations: list[str] = []
        for pattern in self._ASSUMPTION_INDICATORS:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                violations.extend(matches[:3])

        if violations:
            return True, {
                "type": self.ANOMALY_ASSUMPTION,
                "violations": violations,
            }

        return False, {}

    def _check_idempotency(
        self,
        skill_id: str,
        operation: str,
        output: str,
    ) -> tuple[bool, dict[str, Any]]:
        op_hash = hashlib.md5((operation + output[:200]).encode()).hexdigest()[:12]
        key = f"{skill_id}:{op_hash}"

        if key in self._execution_history:
            prev = self._execution_history[key][-1]
            if prev["output_hash"] != hashlib.md5(output.encode()).hexdigest()[:12]:
                return True, {
                    "type": self.ANOMALY_NON_IDEMPOTENT,
                    "key": key,
                    "previous_output_hash": prev["output_hash"],
                    "current_output_hash": hashlib.md5(output.encode()).hexdigest()[:12],
                }

        self._execution_history.setdefault(key, []).append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "output_hash": hashlib.md5(output.encode()).hexdigest()[:12],
            }
        )

        return False, {}

    def scan(
        self,
        skill_id: str,
        output: str,
        operation: str = "",
    ) -> dict[str, Any]:
        anomalies: list[dict[str, Any]] = []
        checks_run = 0

        truncated, trunc_detail = self._check_truncation(output)
        checks_run += 1
        if truncated:
            anomalies.append(
                {
                    "type": self.ANOMALY_TRUNCATION,
                    **trunc_detail,
                }
            )

        partial, partial_detail = self._check_partial_success(output)
        checks_run += 1
        if partial:
            anomalies.append(
                {
                    "type": self.ANOMALY_PARTIAL_SUCCESS,
                    **partial_detail,
                }
            )

        assumptions, assum_detail = self._check_assumptions(output)
        checks_run += 1
        if assumptions:
            anomalies.append(
                {
                    "type": self.ANOMALY_ASSUMPTION,
                    **assum_detail,
                }
            )

        non_idem, idem_detail = self._check_idempotency(skill_id, operation, output)
        checks_run += 1
        if non_idem:
            anomalies.append(
                {
                    "type": self.ANOMALY_NON_IDEMPOTENT,
                    **idem_detail,
                }
            )

        detected = len(anomalies) > 0

        if detected:
            for a in anomalies:
                a.setdefault("timestamp", datetime.now(UTC).isoformat())
                a.setdefault("skill_id", skill_id)
            self._anomalies.extend(anomalies)

        return {
            "skill_id": skill_id,
            "operation": operation,
            "silent_failure_detected": detected,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "checks_run": checks_run,
            "output_length": len(output),
        }

    def get_session_anomalies(self, skill_id: str | None = None) -> list[dict[str, Any]]:
        if skill_id:
            return [a for a in self._anomalies if a.get("skill_id") == skill_id]
        return list(self._anomalies)
