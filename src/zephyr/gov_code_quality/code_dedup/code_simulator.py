# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.code_simulator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/code_quality/test_code_simulator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_code_simulator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""代码模拟器——播放录制的克隆演化序列，stress-test AST/baseline归一化."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimStep:
    iteration: int
    operation: str
    content: str
    expected_hash: str = ""
    tolerance: float = 0.0


@dataclass
class CodeSimulator:
    steps: list[SimStep] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    current_content: str = ""

    def load_sequence(self, base: str, steps: list[tuple[str, str]]) -> None:
        self.current_content = base
        for i, (op, content) in enumerate(steps):
            self.steps.append(SimStep(iteration=i, operation=op, content=content))

    def run(self) -> list[dict[str, Any]]:
        for step in self.steps:
            self.current_content = step.content
            self.history.append(
                {
                    "iteration": step.iteration,
                    "operation": step.operation,
                    "content_len": len(self.current_content),
                }
            )
        return self.history

    def get_final(self) -> str:
        return self.current_content
