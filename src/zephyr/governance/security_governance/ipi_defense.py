# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.security_governance.ipi_defense
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-RES_ipi_defense | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
import re
import time
from dataclasses import dataclass, field


@dataclass
class IPIDefenseReport:
    attack_detected: bool
    attack_type: str
    confidence: float
    blocked: bool
    evidence: list[str]
    advice: str
    timestamp: float = field(default_factory=time.time)


class IPIDefense:
    IPI_PATTERNS: dict[str, list[str]] = {
        "prompt_injection": [
            r"(?:ignore|forget|disregard)\s+(?:all\s+)?(?:previous|above|prior)\s+(?:instructions?|prompts?)",
            r"(?:you\s+are\s+now|your\s+new\s+role\s+is|act\s+as\s+a)",
            r"(?:system\s*[:：]\s*you\s+are|system\s*[:：]\s*new\s+role)",
        ],
        "budget_exfiltration": [
            r"(?:reveal|show|display|print|output)\s+(?:your\s+)?(?:budget|token\s+limit|cost\s+cap|budget_policy)",
            r"(?:read|dump|cat)\s+(?:config/budget_policy|\.zephyr_secure)",
        ],
        "command_injection": [
            r"(?:\$\{.*?\}|`.*?`|\$\(.*?\))",
            r"(?:os\.system|subprocess\.call|eval\(|exec\()",
        ],
        "role_confusion": [
            r"(?:you\s+are\s+the\s+owner|you\s+have\s+owner\s+privileges)",
            r"(?:i\s+am\s+the\s+owner|i\s+have\s+admin\s+access)",
        ],
        "cold_start_abuse": [
            r"(?:cold_start|start\s+new\s+session).*(?:allowance|repeat|loop|multiple|\d+\s*times)",
            r"(?:max\s+cold_start|cold.*(?:abuse|exploit|bypass))",
        ],
        "unlimited_delegation": [
            r"(?:delegate|child\s+agent).*(?:unlimited|infinite|recursive|depth)",
            r"(?:unlimited|infinite).*(?:delegation|chain|recursive\s+agent)",
        ],
    }

    def __init__(self, block_threshold: float = 0.75):
        self._block_threshold = block_threshold
        self._reports: list[IPIDefenseReport] = []

    def scan(self, prompt: str, context: str = "") -> IPIDefenseReport:
        evidence: list[str] = []
        max_confidence = 0.0
        detected_type = ""

        for atype, patterns in self.IPI_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    evidence.append(f"{atype}: matched {pattern[:50]}")
                    if atype == "prompt_injection":
                        max_confidence = max(max_confidence, 0.85)
                    elif atype == "budget_exfiltration":
                        max_confidence = max(max_confidence, 0.90)
                    elif atype == "command_injection":
                        max_confidence = max(max_confidence, 0.95)
                    elif atype == "role_confusion":
                        max_confidence = max(max_confidence, 0.80)
                    elif atype == "cold_start_abuse":
                        max_confidence = max(max_confidence, 0.85)
                    elif atype == "unlimited_delegation":
                        max_confidence = max(max_confidence, 0.80)
                    if not detected_type or max_confidence > 0.8:
                        detected_type = atype

        blocked = max_confidence >= self._block_threshold
        attacked = max_confidence >= 0.5

        if blocked:
            advice = f"已阻止 {detected_type} 攻击 (confidence={max_confidence:.0%})"
        elif attacked:
            advice = f"发现可疑 {detected_type} 模式，已记录但未阻止 (confidence={max_confidence:.0%})"
        else:
            advice = "未检测到 IPI 攻击"

        report = IPIDefenseReport(
            attack_detected=attacked,
            attack_type=detected_type,
            confidence=max_confidence,
            blocked=blocked,
            evidence=evidence,
            advice=advice,
        )
        self._reports.append(report)
        return report

    def recent_reports(self, n: int = 10) -> list[IPIDefenseReport]:
        return self._reports[-n:]

    def attack_count(self) -> int:
        return sum(1 for r in self._reports if r.attack_detected)

    def blocked_count(self) -> int:
        return sum(1 for r in self._reports if r.blocked)

    def clear(self) -> None:
        self._reports.clear()
