# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/encoding.py | §
# [MODULE] scripts.governance._shared.encoding
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
encoding.py — UTF-8 编码安全工具

对标 AGENTS.md §6.7（审计脚本编码铁律）
     SCRIPT-QUALITY-001 D-A-01（UTF-8 stdout 强制重声明）

所有审计脚本在文件开头调用 ensure_utf8_stdout()，
替代各自重复的 if sys.stdout.encoding != 'utf-8' 代码块。
"""

from __future__ import annotations

import sys


def ensure_utf8_stdout() -> None:
    """强制 stdout/stderr 使用 UTF-8 编码。

    Windows 终端默认编码是 GBK，遇到 emoji/中文直接崩溃。
    调用此函数后，所有 print() 输出均使用 UTF-8。

    对标 AGENTS.md §6.7 标准写法：
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
    """
    if sys.stdout.encoding != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    if sys.stderr.encoding != "utf-8":
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
