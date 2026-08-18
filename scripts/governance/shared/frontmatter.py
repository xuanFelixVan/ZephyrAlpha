# [A_module] module_id=SH-GOV-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md
# [TTL] permanent
"""公共模块别名（R5 公共化）— 从 _shared.frontmatter 重新导出。

测试通过 ``from scripts.governance.shared.frontmatter import parse_frontmatter`` 导入，
本模块提供公共路径，实际实现在 ``_shared/frontmatter.py``。
"""

__manifest__ = """
args: []
description: 公共模块别名（R5 公共化）— 从 _shared.frontmatter 重新导出。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

from scripts.governance._shared.frontmatter import *  # noqa: F401,F403
