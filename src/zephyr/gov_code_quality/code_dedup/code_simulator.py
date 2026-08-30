# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.code_simulator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/code_quality/test_code_simulator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
代码模拟器——播放录制的克隆演化序列，stress-test AST/baseline归一化.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: code_simulator.py
# 层: 算法
# - id: A1
#   name_zh: ① CodeSimulator
#   name_en: CodeSimulator
#   intro: class CodeSimulator 源码 L63-L86
#   desc: 公共方法（定义序）: load_sequence, run, get_final；源码 L63-L86
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CodeSimulator
#   downstream: tests/governance/code_quality/test_code_simulator.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
