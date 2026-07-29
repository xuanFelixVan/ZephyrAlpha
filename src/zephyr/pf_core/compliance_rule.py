# [A_module] module_id=SH-PRT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [TTL] permanent
"""公共模块别名（R5 公共化）— 从 canonical 路径重新导出 ComplianceRule。

ARCH-GOV-SHIM-001 阶段3：pf_core 的 compliance_rule shim 已删除，直接指向 canonical 路径。
但 ``from zephyr.pf_core.compliance_rule import ComplianceRule`` 需要真实模块文件
（PEP 562 ``__getattr__`` 不支持子模块导入语义），故创建此公共别名。
"""
from zephyr.shared.contracts.compliance_rule import *  # noqa: F401,F403
from zephyr.shared.contracts.compliance_rule import ComplianceRule  # noqa: F401
