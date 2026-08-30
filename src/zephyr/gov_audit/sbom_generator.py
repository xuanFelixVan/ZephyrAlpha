# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.sbom_generator
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.__init__ (LicenseType)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] LicenseType 枚举值稳定（MIT/APACHE2/BSD/PSF/UNKNOWN）
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-020 | layer=module | stability=stable | safety=L | ai_autonomy=immutable_core
# [TTL] permanent

"""
LicenseType 枚举——许可证类型定义（P3 价值审判退役残留）。

原 SBOM 生成器（DepInfo/SBOMReport/generate_sbom）经价值审判退役：
- 0 消费者（governance/__init__.py 仅重导出 LicenseType）
- 代码价值低：SBOMReport 是静态数据容器无生成逻辑，generate_sbom 仅做简单阈值判断
- 独有性低：许可证校验逻辑可由 ALLOWED_LICENSES 集合直接完成
- 集成可行性低：无实际 SBOM 扫描器接入，depth/cvss/cve_ids 字段无数据源

保留 LicenseType 枚举（governance/__init__.py:132 重导出，250 行 __all__ 声明）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: sbom_generator.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: LicenseType
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: LicenseType
#   downstream: zephyr.governance.__init__ (LicenseType)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum


class LicenseType(str, Enum):
    MIT = "MIT"
    APACHE2 = "Apache-2.0"
    BSD = "BSD"
    PSF = "PSF"
    UNKNOWN = "UNKNOWN"


ALLOWED_LICENSES: set[LicenseType] = {
    LicenseType.MIT,
    LicenseType.APACHE2,
    LicenseType.BSD,
    LicenseType.PSF,
}
