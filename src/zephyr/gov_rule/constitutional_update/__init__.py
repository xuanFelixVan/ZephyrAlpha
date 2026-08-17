# [A_module] module_id=MOD-GOV-constitutional_update | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RULE_DOMAIN | docs/03_modules/_domain_governance/rule/blueprint.md
# [MODULE] zephyr.gov_rule.constitutional_update
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: constitutional_update 实现模块
#   fields: ConstitutionalAutoUpdate / Learning / ProposedUpdate 三个公开类
#   code: zephyr.gov_rule.constitutional_update.constitutional_update L3
# 层: 算法
# - id: A1
#   name_zh: ① 导入再导出
#   name_en: __init__ re-export
#   intro: 把实现文件里的三个类提到包级命名空间，外面 import 更短
#   desc: from ...constitutional_update import 三类，__all__ 登记三类加模块名，无其他逻辑
#   inputs: I1
#   outputs: 包级导出列表
# 层: 输出
# - id: O1
#   name_zh: constitutional_update 包命名空间
#   name_en: package __all__
#   intro: 对外暴露 ConstitutionalAutoUpdate/Learning/ProposedUpdate 三个入口
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.gov_rule.constitutional_update.constitutional_update import (
    ConstitutionalAutoUpdate,
    Learning,
    ProposedUpdate,
)

__all__ = ["ConstitutionalAutoUpdate", "Learning", "ProposedUpdate", "constitutional_update"]
