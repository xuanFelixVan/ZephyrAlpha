# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.symbol_index
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/data_layer/test_symbol_index.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_symbol_index | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""符号索引 — 全局函数/类/import映射表."""

import ast
from pathlib import Path


class SymbolIndex:
    """全局符号索引."""

    def __init__(self) -> None:
        self._functions: dict[str, list[str]] = {}
        self._classes: dict[str, list[str]] = {}
        self._imports: dict[str, list[str]] = {}

    def index_file(self, file_path: str | Path) -> None:
        """索引单个文件."""
        path = Path(file_path)
        if path.suffix != ".py":
            return
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, OSError):
            return

        rel_path = str(path)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._functions.setdefault(node.name, []).append(rel_path)
            elif isinstance(node, ast.ClassDef):
                self._classes.setdefault(node.name, []).append(rel_path)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self._imports.setdefault(alias.name, []).append(rel_path)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._imports.setdefault(node.module, []).append(rel_path)

    def lookup_function(self, name: str) -> list[str]:
        return self._functions.get(name, [])

    def lookup_class(self, name: str) -> list[str]:
        return self._classes.get(name, [])

    def lookup_import(self, name: str) -> list[str]:
        return self._imports.get(name, [])

    def stats(self) -> dict:
        return {
            "functions": len(self._functions),
            "classes": len(self._classes),
            "imports": len(self._imports),
        }
