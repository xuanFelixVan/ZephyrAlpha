# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.cross_boundary_detector
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/cross/test_cross_boundary_detector.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_cross_boundary_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""跨边界克隆感知——四大边界差异化检测+独立策略+跨边界保守auto_fix规则."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Final


class Boundary(str, Enum):
    SRC_TEST_BRIDGE = "SRC_TEST_BRIDGE"
    SRC_SCRIPTS_DIVERGENCE = "SRC_SCRIPTS_DIVERGENCE"
    CROSS_LAYER_REDUNDANCY = "CROSS_LAYER_REDUNDANCY"
    VENDORED_REIMPLEMENTATION = "VENDORED_REIMPLEMENTATION"


BOUNDARY_CONFIG: Final[dict] = {
    Boundary.SRC_TEST_BRIDGE: {"threshold": 0.80, "action": "WARN", "auto_fix": False, "message": "测试可简化但非阻塞"},
    Boundary.SRC_SCRIPTS_DIVERGENCE: {
        "threshold": 0.75,
        "action": "HIGHLIGHT",
        "auto_fix": False,
        "message": "scripts vs src走向fork",
    },
    Boundary.CROSS_LAYER_REDUNDANCY: {
        "threshold": 0.80,
        "action": "CRITICAL",
        "auto_fix": True,
        "auto_fix_threshold": 0.95,
        "message": "去重最高价值目标",
    },
    Boundary.VENDORED_REIMPLEMENTATION: {
        "threshold": 0.85,
        "action": "WARN",
        "auto_fix": False,
        "message": "为什么重写三方功能",
    },
}


@dataclass
class CrossBoundaryClone:
    src_path: str
    dst_path: str
    src_func: str
    dst_func: str
    similarity: float
    boundary: Boundary
    recommendation: str = ""

    @property
    def can_auto_fix(self) -> bool:
        cfg = BOUNDARY_CONFIG[self.boundary]
        if not cfg["auto_fix"]:
            return False
        return self.similarity >= cfg.get("auto_fix_threshold", 0.95)


@dataclass
class CrossBoundaryDetector:
    findings: list[CrossBoundaryClone] = field(default_factory=list)

    def detect(
        self, src_path: str, dst_path: str, src_func: str, dst_func: str, similarity: float, boundary: Boundary
    ) -> CrossBoundaryClone:
        cfg = BOUNDARY_CONFIG[boundary]
        if similarity >= cfg["threshold"]:
            clone = CrossBoundaryClone(
                src_path=src_path,
                dst_path=dst_path,
                src_func=src_func,
                dst_func=dst_func,
                similarity=similarity,
                boundary=boundary,
                recommendation=cfg["message"],
            )
            self.findings.append(clone)
            return clone
        return CrossBoundaryClone(
            src_path=src_path,
            dst_path=dst_path,
            src_func=src_func,
            dst_func=dst_func,
            similarity=similarity,
            boundary=boundary,
            recommendation="below_threshold",
        )
