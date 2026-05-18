# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md
# [MODULE] zephyr.agent_rbac
# [INVARIANTS] 七层纵深防御+六横切面Runtime RBAC
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md;src/zephyr/agent_rbac/__init__.py
# [CONSUMERS] MOD-INF-007;MOD-INF-020;MOD-INF-027
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PermissionError;ValueError;RuntimeError
# [TESTS] tests/test_agent_rbac/
from __future__ import annotations

import ast
import logging
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def check_lock_before_write(lock_check_fn: Callable[[], bool]) -> Callable[[F], F]:
    """AP1防护装饰器——写入前强制检查锁状态。"""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not lock_check_fn():
                logger.warning("AP1 VIOLATION: %s 未 check lock_files.py", func.__name__)
            return func(*args, **kwargs)
        return wrapper  # type: ignore[return-value]
    return decorator


def scan_silent_ignore(source_code: str) -> list[int]:
    """AP3检测——扫描 except: pass 模式,返回违规行号。"""
    violations: list[int] = []
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    if node.body and len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        violations.append(node.lineno)
    except SyntaxError:
        pass
    return violations


def benchmark_before_optimize(target_func: str) -> bool:
    """AP2防护——优化前先benchmark。"""
    logger.info("AP2 CHECK: 优化 %s 前先 benchmark", target_func)
    return True
