# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.canary_manager
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_canary_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""金丝雀工厂——生成已知oracle 文件 用于引擎检出+回归测试."""

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CanaryFile:
    path: str
    content_hash: str
    relation_group: str
    expected_clones: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class CanaryManager:
    canaries: dict[str, CanaryFile] = field(default_factory=dict)
    results: list[dict[str, Any]] = field(default_factory=list)

    A_IDENTICAL = """def hello():
    return "hello world"
"""
    B_IDENTICAL = """def hello():
    return "hello world"
"""
    C_WRAPPED = """def greeter():
    def hello():
        return "hello world"
    return hello()
"""
    D_NEAR_MISS = """def hello():
    return "hello world!"  # one char diff
"""
    E_TEMPLATE = """def <NAME>():
    return "<VALUE>"
"""

    def register_canary(
        self, name: str, path: str, content: str, relation_group: str, expected_clones: list[str]
    ) -> CanaryFile:
        cf = CanaryFile(
            path=path,
            content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
            relation_group=relation_group,
            expected_clones=expected_clones,
            tags=["canary", relation_group],
        )
        self.canaries[name] = cf
        return cf

    def setup_standard_canaries(self) -> None:
        self.register_canary(
            "identical1", "tests/canary/a.py", self.A_IDENTICAL, "identical", ["identical2", "identical3"]
        )
        self.register_canary(
            "identical2", "tests/canary/b.py", self.B_IDENTICAL, "identical", ["identical1", "identical3"]
        )
        self.register_canary(
            "identical3", "tests/canary/b2.py", self.B_IDENTICAL, "identical", ["identical1", "identical2"]
        )
        self.register_canary("near_miss", "tests/canary/near.py", self.D_NEAR_MISS, "near_miss", [])

    def record_result(self, canary_name: str, detected: int, expected: int, passed: bool) -> None:
        self.results.append({"canary": canary_name, "detected": detected, "expected": expected, "passed": passed})

    def score(self) -> dict[str, Any]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        return {
            "total_canaries": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / max(total, 1),
        }
