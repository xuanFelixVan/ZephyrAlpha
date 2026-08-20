# [A_module] module_id=SH-GOV-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md
# [TTL] permanent
"""公共包别名（R5 公共化）— 从 _shared 重新导出所有公共符号。

测试通过 ``from scripts.governance.shared.frontmatter import parse_frontmatter`` 导入，
本包提供公共路径，实际实现在 ``_shared/``。

注意：``_shared`` 内部使用 ``from _shared.xxx import ...`` 绝对导入，
因此需要将 ``scripts/governance`` 加入 sys.path 以确保内部导入正常工作。
"""

import pathlib
import sys

# _shared 内部使用 `from _shared.constants import ...` 绝对导入，
# 需要将 scripts/governance 父目录加入 sys.path
_shared_parent = str(pathlib.Path(__file__).resolve().parent.parent)
if _shared_parent not in sys.path:
    sys.path.insert(0, _shared_parent)

from scripts.governance._shared import *  # noqa: F401,F403,E402
from scripts.governance._shared import (  # noqa: F401,E402
    base,
    constants,
    encoding,
    file_utils,
    frontmatter,
    libcst_docstring_adder,
    registry_entry_count,
    thresholds,
    walk,
    yaml_utils,
)

__all__: list[str] = ["frontmatter"]
