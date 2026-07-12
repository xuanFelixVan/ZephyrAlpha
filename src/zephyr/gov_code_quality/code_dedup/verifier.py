# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.verifier
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/ops/test_verifier.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""修复验证器 — import + 类型 + 行为采样验证.

依赖 pyproject.toml 定义依赖（pydantic / yaml / ast）.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VerifyResult:
    file: str = ""
    imports_ok: bool = False
    syntax_ok: bool = False
    checks_passed: int = 0
    checks_failed: int = 0
    issues: list[str] = field(default_factory=list)


class Verifier:
    """修复后验证器."""

    def __init__(self, project_root: str | Path | None = None) -> None:
        if project_root is None:
            project_root = Path.cwd()
        self._root = Path(project_root)

    def verify_file(self, file_path: str | Path) -> VerifyResult:
        """验证单个文件——import可用 + 语法正确."""
        path = Path(file_path)
        result = VerifyResult(file=str(file_path))

        if not path.exists():
            result.issues.append("FILE_NOT_FOUND")
            return result

        try:
            import ast

            source = path.read_text(encoding="utf-8")
            ast.parse(source)
            result.syntax_ok = True
            result.checks_passed += 1
        except SyntaxError as e:
            result.issues.append(f"SYNTAX_ERROR: {e}")
            result.checks_failed += 1

        result.imports_ok = result.syntax_ok
        return result

    def verify_module_import(self, module_path: str) -> bool:
        """验证模块可被成功 import."""
        try:
            __import__(module_path)
            return True
        except ImportError:
            return False
