# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.data_governance.data_lifecycle
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
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
#   code: data_lifecycle.py
# 层: 算法
# - id: A1
#   name_zh: ① forget_pii
#   name_en: forget_pii
#   intro: forget_pii() 源码 L65-L66
#   desc: 源码 L65-L66
#   inputs: 无参数
#   outputs: dict[str, str]
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: dict[str, str]
#   name_en: dict[str, str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from enum import Enum
from typing import Final


class DataStage(str, Enum):
    CREATE = "Create"
    STORE = "Store"
    USE = "Use"
    ARCHIVE = "Archive"
    PURGE = "Purge"


ARCHIVE_AFTER_YEARS: Final[int] = 7
PURGE_AFTER_YEARS: Final[int] = 15
GDPR_PII_FIELDS: Final[list[str]] = ["user", "payment", "email"]


def forget_pii() -> dict[str, str]:
    return {"action": "permanent_delete", "cert": "provided"}
