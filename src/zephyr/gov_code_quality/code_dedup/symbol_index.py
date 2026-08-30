# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.symbol_index
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/data_layer/test_symbol_index.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
符号索引 — 全局函数/类/import映射表.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: symbol_index.py
# 层: 算法
# - id: A1
#   name_zh: ① SymbolIndex
#   name_en: SymbolIndex
#   intro: 全局符号索引.
#   desc: 全局符号索引.；公共方法（定义序）: classes, functions, imports, index_file, lookup_function, lookup_class, lookup_import, sta…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SymbolIndex
#   downstream: tests/governance/data_layer/test_symbol_index.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import ast
from pathlib import Path


class SymbolIndex:
    """全局符号索引."""

    def __init__(self) -> None:
        self._functions: dict[str, list[str]] = {}
        self._classes: dict[str, list[str]] = {}
        self._imports: dict[str, list[str]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def classes(self) -> dict[str, list[str]]:
        """只读：classes（Stage 4 公共化）。"""
        return self._classes

    @classes.setter
    def classes(self, value):
        """写入：classes（Stage 4 公共化）。"""
        self._classes = value

    @property
    def functions(self) -> dict[str, list[str]]:
        """只读：functions（Stage 4 公共化）。"""
        return self._functions

    @functions.setter
    def functions(self, value):
        """写入：functions（Stage 4 公共化）。"""
        self._functions = value

    @property
    def imports(self) -> dict[str, list[str]]:
        """只读：imports（Stage 4 公共化）。"""
        return self._imports

    @imports.setter
    def imports(self, value):
        """写入：imports（Stage 4 公共化）。"""
        self._imports = value

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
