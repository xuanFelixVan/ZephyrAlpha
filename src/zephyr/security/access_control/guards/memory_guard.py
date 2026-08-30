# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.memory_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_crosscut_d.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] privileged ops always blocked; size > MAX always blocked
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_access never raises; returns {"allowed": bool}
# [TESTS] tests/agent_rbac/test_crosscut_d.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
MemoryGuard — 内存访问守卫.

依据蓝图 MOD-INF-018 §3:
- 限制 agent 的内存访问大小
- 阻止特权内存操作（mprotect, mmap, mlock 等）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_size 参数
#   fields: 参数 max_size（无注解）
#   code: memory_guard.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MemoryGuard
#   name_en: MemoryGuard
#   intro: 内存访问守卫器.
#   desc: 内存访问守卫器.；公共方法（定义序）: check_access；源码 L87-L122
#   inputs: max_size
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: MemoryGuard
#   downstream: tests/agent_rbac/test_crosscut_d.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from typing import Any

MAX_MEMORY_ACCESS = 1_000_000  # 1MB

PRIVILEGED_MEMORY_OPS = {
    "mprotect",
    "mmap",
    "mlock",
    "munlock",
    "mremap",
    "msync",
    "mincore",
    "madvise",
    "brk",
    "sbrk",
    "virtual_alloc",
    "virtual_protect",
    "virtual_free",
    "write_process_memory",
    "read_process_memory",
}


class MemoryAccessLog:
    """内存访问日志."""

    def __init__(self, agent_id: str, operation: str, size: int, allowed: bool) -> None:
        self.agent_id = agent_id
        self.operation = operation
        self.size = size
        self.allowed = allowed


class MemoryGuard:
    """内存访问守卫器."""

    def __init__(self, max_size: int = MAX_MEMORY_ACCESS) -> None:
        self._max_size = max_size
        self._logs: list[MemoryAccessLog] = []

    def check_access(self, agent_id: str, operation: str, size: int) -> dict[str, Any]:
        """检查内存访问权限.

        Args:
            agent_id: agent 标识
            operation: 内存操作名称
            size: 访问大小（字节）

        Returns:
            dict: {"allowed": bool, "reason": str}
        """
        if operation in PRIVILEGED_MEMORY_OPS:
            result = {
                "allowed": False,
                "reason": f"privileged memory operation blocked: {operation}",
            }
        elif size > self._max_size:
            result = {
                "allowed": False,
                "reason": f"size {size} exceeds max {self._max_size}",
            }
        else:
            result = {
                "allowed": True,
                "reason": "within limits",
            }

        self._logs.append(MemoryAccessLog(agent_id, operation, size, result["allowed"]))
        return result


__all__ = [
    "MAX_MEMORY_ACCESS",
    "MemoryAccessLog",
    "MemoryGuard",
]
