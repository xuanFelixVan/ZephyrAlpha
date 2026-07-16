# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/file_utils.py | §
# [MODULE] scripts.governance._shared.file_utils
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
# [TTL] permanent
"""
_shared/file_utils.py — 原子写入共享工具（ARCH-036 P1-1）

对标 SCRIPT-QUALITY-001 D-D-05（禁止跨脚本复制粘贴逻辑）
所有原子写入逻辑集中在此，脚本通过 import 引用。

本文件 re-export src/zephyr/shared/io/file_utils.py 的真源函数
（atomic_write / AtomicWriteError），让 scripts/ 下消费者通过
``from _shared.file_utils import atomic_write`` 获取真源，
无需每个脚本自己 bootstrap sys.path（向内收：扩展已有，不创造新文件）。

graceful 变体 atomic_write_safe() 供防御性调用方使用——
写入失败时返回 False 而非 raise（对标本地实现的 PermissionError swallow 模式）。
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path

# ── 一次性 bootstrap：加 src/ 到 sys.path，re-export 真源函数 ──
# 约束：N 值对本文件固定（scripts/governance/_shared/ → repo root = parents[3]），仅此一次
from _shared.constants import REPO_ROOT
_REPO_ROOT = REPO_ROOT
_SRC = str(_REPO_ROOT / "src")
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

# re-export 真源函数（SSoT：src/zephyr/shared/io/file_utils.py）
from zephyr.shared.io.file_utils import AtomicWriteError, atomic_write  # noqa: E402,F401


def atomic_write_safe(
    filepath: Path | str,
    content: str,
    *,
    encoding: str = "utf-8",
) -> bool:
    """graceful 变体：写入失败时返回 False 而非 raise。

    供防御性调用方使用（如状态持久化脚本对可选文件做容错写入）。
    与 atomic_write 的契约差异：失败返回 False（非 raise AtomicWriteError）；
    成功返回 True。

    对标本地实现的 ``except PermissionError: os.remove(tmp)`` 静默吞异常模式，
    消除 40+ 处重复的 tmp_path+os.replace+PermissionError 样板代码。
    """
    try:
        atomic_write(filepath, content, encoding=encoding)
        return True
    except (AtomicWriteError, OSError):
        return False
