# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.cross_env_consistency
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
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
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: cross_env_consistency.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: ConsistencyDim
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: ConsistencyDim
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class ConsistencyDim(str, Enum):
    PYTHON = "Python3.11.9"
    DEPENDENCIES = "freeze.md5 hash"
    DATA_STRUCTURE = "parquet/pickle schema"
    MODEL_OUTPUT = "float ε<1e-9"


PYTHON_VERSION: Final[str] = "3.11.9"
MODEL_FLOAT_TOLERANCE: Final[float] = 1e-9
WIN_MIN_RAM_GB: Final[int] = 16
WIN_MAX_CPU_LOAD: Final[float] = 0.75

WIN11_RISKS: Final[dict[str, str]] = {
    "permissions": "UAC escalation blocked + firewall auto",
    "paths": "反斜杠->all refs consistent WSL+",
    "crlf": "gitattributes *.bat/proj eol=crlf",
    "memory": "Win ≥16GB load avg<75%",
    "process": "single python system_module=1",
}
