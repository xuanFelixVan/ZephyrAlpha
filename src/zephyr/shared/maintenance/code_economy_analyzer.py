# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.maintenance.code_economy_analyzer
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement.gate_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: code_economy_analyzer.py
# 层: 算法
# - id: A1
#   name_zh: ① CodeEconomyAnalyzer
#   name_en: CodeEconomyAnalyzer
#   intro: class CodeEconomyAnalyzer 源码 L62-L79
#   desc: 公共方法（定义序）: register_module, register_import, analyze；源码 L62-L79
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CodeEconomyAnalyzer
#   downstream: zephyr.gov_enforcement.rule_enforcement.gate_engine
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EconomyReport:
    total_lines: int
    active_lines: int
    dead_lines: int
    reuse_ratio: float
    redundancy_ratio: float


class CodeEconomyAnalyzer:
    def __init__(self):
        self._modules: dict[str, int] = {}
        self._imports: dict[str, int] = {}

    def register_module(self, name: str, lines: int) -> None:
        self._modules[name] = lines

    def register_import(self, module_name: str) -> None:
        self._imports[module_name] = self._imports.get(module_name, 0) + 1

    def analyze(self) -> EconomyReport:
        total = sum(self._modules.values())
        active = sum(v for k, v in self._modules.items() if self._imports.get(k, 0) > 0)
        dead = total - active
        reuse = sum(v for v in self._imports.values() if v > 1) / max(len(self._imports), 1)
        redundancy = dead / total if total > 0 else 0.0
        return EconomyReport(total, active, dead, reuse, redundancy)
