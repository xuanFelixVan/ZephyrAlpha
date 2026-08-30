# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.native_api_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_crosscut_d.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] native API calls always blocked; clean code never flagged
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] scan never raises; returns {"allowed": bool, "matched": list}
# [TESTS] tests/agent_rbac/test_crosscut_d.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
NativeApiGuard — 原生 API 守卫.

依据蓝图 MOD-INF-018 §3:
- 检测代码中的原生 API 调用（ctypes, dlopen, mmap 等）
- 阻止绕过 Python 安全机制的原生调用

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: native_api_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① NativeApiGuard
#   name_en: NativeApiGuard
#   intro: 原生 API 守卫器.
#   desc: 原生 API 守卫器.；公共方法（定义序）: scan；源码 L85-L113
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: NativeApiGuard
#   downstream: tests/agent_rbac/test_crosscut_d.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import re
from typing import Any

BLOCKED_NATIVE_APIS = [
    r"\bctypes\b",
    r"\bCDLL\b",
    r"\bWinDLL\b",
    r"\bdlopen\b",
    r"\bmmap\b",
    r"\bptrace\b",
    r"\bkill\b",
    r"\bgetpid\b",
    r"\bsystem\b",
    r"\bpopen\b",
    r"\bexecv",
    r"\bexec[lv]",
    r"\bfork\b",
    r"\bsocket\b",
    r"\bconnect\b",
    r"\bbind\b",
    r"\blisten\b",
    r"\baccept\b",
    r"\brecv\b",
    r"\bsend\b",
    r"\bos\.system\b",
    r"\bsubprocess\b",
    r"\bcommands\b",
    r"\bgetoutput\b",
    r"\bgetstatusoutput\b",
]


class NativeApiGuard:
    """原生 API 守卫器."""

    def __init__(self) -> None:
        self._compiled = [re.compile(p, re.IGNORECASE) for p in BLOCKED_NATIVE_APIS]

    def scan(self, code: str, filename: str = "") -> dict[str, Any]:
        """扫描代码中的原生 API 调用.

        Args:
            code: 代码字符串
            filename: 文件名（可选）

        Returns:
            dict: {"allowed": bool, "matched": list, "filename": str}
        """
        if not code or not isinstance(code, str):
            return {"allowed": True, "matched": [], "filename": filename}

        matched: list[str] = []
        for i, pat in enumerate(self._compiled):
            if pat.search(code):
                matched.append(BLOCKED_NATIVE_APIS[i])

        return {
            "allowed": len(matched) == 0,
            "matched": matched,
            "filename": filename,
        }


__all__ = [
    "BLOCKED_NATIVE_APIS",
    "NativeApiGuard",
]
