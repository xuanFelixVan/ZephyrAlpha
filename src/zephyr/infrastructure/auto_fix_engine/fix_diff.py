# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.fix_diff
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;fix_report.py;compliance_auditor.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] diff MUST展示before/after;MUST可逆
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DiffError
# [TESTS] tests/auto-fix-engine/test_fix_diff.py
# [A_module] module_id=MOD-INF-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: fix_diff.py
# 层: 算法
# - id: A1
#   name_zh: ① FixDiff
#   name_en: FixDiff
#   intro: class FixDiff 源码 L57-L115
#   desc: 公共方法（定义序）: compute, compute_text, reverse；源码 L57-L115
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: FixDiff
#   downstream: engine.py;fix_report.py;compliance_auditor.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import difflib
import hashlib
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import FixAction


class FixDiff:
    @staticmethod
    def compute(action: FixAction) -> dict[str, Any]:
        if not action.before and not action.after:
            return {"has_changes": False, "unified_diff": "", "stats": {}}
        before_lines = action.before.splitlines(keepends=True)
        after_lines = action.after.splitlines(keepends=True)
        diff = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"{action.target} (before)",
            tofile=f"{action.target} (after)",
            lineterm="",
        )
        diff_text = "\n".join(diff)
        added = sum(1 for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in diff_text.splitlines() if l.startswith("-") and not l.startswith("---"))
        return {
            "has_changes": action.before != action.after,
            "unified_diff": diff_text,
            "stats": {
                "added": added,
                "removed": removed,
                "changed": min(added, removed),
                "before_hash": hashlib.sha256(action.before.encode()).hexdigest()[:16],
                "after_hash": hashlib.sha256(action.after.encode()).hexdigest()[:16],
            },
        }

    @staticmethod
    def compute_text(before: str, after: str, label: str = "file") -> dict[str, Any]:
        before_lines = before.splitlines(keepends=True)
        after_lines = after.splitlines(keepends=True)
        diff = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile=f"{label} (before)",
            tofile=f"{label} (after)",
            lineterm="",
        )
        diff_text = "\n".join(diff)
        return {
            "has_changes": before != after,
            "unified_diff": diff_text,
            "stats": {
                "added": sum(1 for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++")),
                "removed": sum(1 for l in diff_text.splitlines() if l.startswith("-") and not l.startswith("---")),
            },
        }

    @staticmethod
    def reverse(action: FixAction) -> FixAction:
        reversed_action = action.model_copy(
            update={
                "before": action.after,
                "after": action.before,
            }
        )
        return reversed_action
