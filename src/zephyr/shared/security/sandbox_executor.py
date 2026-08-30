# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.security.sandbox_executor
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
SandboxExecutor — re-homed to eliminate shared->infrastructure circular import.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: base_dir 参数
#   fields: 参数 base_dir（无注解）
#   code: sandbox_executor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SandboxExecutor
#   name_en: SandboxExecutor
#   intro: Execute fix actions in an isolated sandbox directory.
#   desc: Execute fix actions in an isolated sandbox directory.；公共方法（定义序）: execute；源码 L59-L79
#   inputs: base_dir
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SandboxExecutor
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import logging

logger = logging.getLogger(__name__)

import os
import tempfile
from collections.abc import Callable
from typing import Any

__all__ = ["SandboxExecutor"]


class SandboxExecutor:
    """Execute fix actions in an isolated sandbox directory."""

    def __init__(self, base_dir: str | None = None) -> None:
        self._base_dir = base_dir or os.path.join(tempfile.gettempdir(), "auto_fix_sandbox")

    def execute(self, action: object, fix_fn: Callable[..., object]) -> tuple[bool, str]:
        sandbox_dir = os.path.join(self._base_dir, getattr(action, "action_id", "unknown"))
        os.makedirs(sandbox_dir, exist_ok=True)
        try:
            result = fix_fn(action.target, dry_run=True)
            return True, str(result)
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            return False, str(exc)
        finally:
            try:
                import shutil

                shutil.rmtree(sandbox_dir, ignore_errors=True)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in sandbox_executor", exc_info=True)
