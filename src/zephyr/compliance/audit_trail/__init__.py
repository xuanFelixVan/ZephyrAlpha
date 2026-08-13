# [A_module] module_id=MOD-CMP-audit_trail | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


Re-export wrapper: audit-trail has migrated to zephyr.gov_audit

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: gov_audit 子模块符号 1个
#   fields: bridges
#   code: zephyr.gov_audit
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.compliance.audit_trail.__init__
#   intro: Re-export wrapper: audit-trail has migrated to zephyr.gov_au
#   desc: MOD-CMP-audit_trail 包入口，包级聚合再导出并声明 __all__（1项）
#   inputs: I1
#   outputs: zephyr.compliance.audit_trail 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（1项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.compliance.audit_trail 包公共 API
#   name_en: __all__ 1项
#   intro: Re-export wrapper: audit-trail has migrated to zephyr.gov_au——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

# 5.93.6 修复：import * → 显式导入
from zephyr.gov_audit import bridges

__all__ = ["bridges"]
