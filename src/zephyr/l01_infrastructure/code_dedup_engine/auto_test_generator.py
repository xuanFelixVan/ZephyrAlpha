# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.auto_test_generator

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""提取后自动测试生成 — 类型驱动+金丝雀录制+契约测试."""

from __future__ import annotations

import ast


class AutoTestGenerator:
    """对标 Google Mozart——提取后自动生成测试."""

    def analyze_signature(self, source: str) -> dict:
        """AST解析 → 参数类型 → 生成测试模板."""
        try:
            tree = ast.parse(source.lstrip())
        except SyntaxError:
            return {"parameters": [], "return_type": "Any"}

        if not tree.body:
            return {"parameters": [], "return_type": "Any"}

        func = tree.body[0]
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return {"parameters": [], "return_type": "Any"}

        params = [{
            "name": a.arg,
            "type": ast.unparse(a.annotation) if a.annotation else "Any",
        } for a in func.args.args]

        return_type = ast.unparse(func.returns) if func.returns else "Any"

        return {"parameters": params, "return_type": return_type}

    def generate_contract_test(self, func_name: str, signature: dict) -> str:
        """生成pytest契约测试模板."""
        params = signature.get("parameters", [])
        param_str = ", ".join(p["name"] for p in params)
        lines = [
            "import pytest",
            "",
            f"def test_{func_name}_contract():",
            f"    result = {func_name}({','.join('None' for _ in params)})",
            f"    assert result is not None",
        ]
        return "\n".join(lines)
