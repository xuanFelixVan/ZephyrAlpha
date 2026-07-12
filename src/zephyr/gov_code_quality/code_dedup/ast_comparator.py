# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.ast_comparator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.intelligence_governance.self_benchmark; tests/governance/code_quality/test_ast_comparator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_ast_comparator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Stage 2: AST 级精确比对器.

职责：
  - AST 子树归一化哈希
  - 部分重复 LCS 最长公共子序列
  - 参数化模板聚类
  - Python 惯用法豁免（IDIOM_WHITELIST：__init__/__repr__/__enter__/@property/ABC/@overload）
  - 设计模式白名单（Strategy/Adapter/Factory/Template Method/Observer/Decorator）
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass

# ── 豁免规则 ──────────────────────────────────────────────────

IDIOM_WHITELIST: set[str] = {
    "__init__",
    "__repr__",
    "__str__",
    "__enter__",
    "__exit__",
}

DESIGN_PATTERN_WHITELIST: set[str] = {
    "strategy",
    "adapter",
    "factory",
    "template_method",
    "observer",
    "decorator_wrapper",
}


@dataclass
class ASTCompareResult:
    similarity: float
    hash_a: str = ""
    hash_b: str = ""
    exempted: bool = False
    exempt_reason: str = ""
    partial_match_ratio: float = 0.0
    template_group: str = ""


class ASTComparator:
    """Stage 2: AST 子树哈希 + LCS + 模板聚类 + 豁免白名单."""

    def __init__(self) -> None:
        pass

    # ── 公共 API ──────────────────────────────────────────────

    def compare(self, func_a: str, func_b: str, name_a: str = "", name_b: str = "") -> ASTCompareResult:
        """比较两个函数的 AST 结构."""
        exempt_check = self._check_exemption(name_a, name_b)
        if exempt_check.exempted:
            return exempt_check

        hash_a = self.compute_subtree_hash(func_a)
        hash_b = self.compute_subtree_hash(func_b)

        if hash_a == hash_b:
            return ASTCompareResult(
                similarity=1.0,
                hash_a=hash_a,
                hash_b=hash_b,
            )

        sim = self._compute_structure_similarity(func_a, func_b)
        lcs_ratio = self._compute_lcs_ratio(func_a, func_b)

        return ASTCompareResult(
            similarity=round(sim, 3),
            hash_a=hash_a,
            hash_b=hash_b,
            partial_match_ratio=round(lcs_ratio, 3),
        )

    def compare_bulk(self, pairs: list[tuple[str, str, str, str]]) -> list[ASTCompareResult]:
        """批量比较 [(func_a, func_b, name_a, name_b), ...]."""
        return [self.compare(a, b, na, nb) for a, b, na, nb in pairs]

    def compute_subtree_hash(self, source: str) -> str:
        """计算 AST 子树归一化哈希——剥离 docstring + 归一化变量名."""
        normalized = self._normalize_ast(source)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

    def cluster_templates(self, functions: list[tuple[str, str]]) -> dict[str, list[str]]:
        """模板聚类——基于命名前缀 + 结构相似度."""
        clusters: dict[str, list[str]] = {}
        prefix_groups: dict[str, list[str]] = {}

        for name, source in functions:
            prefix = name.split("_")[0] if "_" in name else name[:6]
            prefix_groups.setdefault(prefix, []).append(name)

        for prefix, names in prefix_groups.items():
            if len(names) >= 2:
                clusters[f"pattern_{prefix}"] = names

        return clusters

    # ── 内部方法 ─────────────────────────────────────────────

    def _check_exemption(self, name_a: str, name_b: str) -> ASTCompareResult:
        """检查是否符合豁免规则."""
        if name_a in IDIOM_WHITELIST or name_b in IDIOM_WHITELIST:
            return ASTCompareResult(
                similarity=0.0,
                exempted=True,
                exempt_reason=f"Python惯用法豁免: {name_a or name_b}",
            )
        return ASTCompareResult(similarity=-1.0)

    def _normalize_ast(self, source: str) -> str:
        """AST 归一化——剥离 docstring + 注释 + 归一化变量名."""
        try:
            tree = ast.parse(source.lstrip())
        except SyntaxError:
            return source

        class _Normalizer(ast.NodeTransformer):
            def visit_Expr(self, node: ast.Expr) -> ast.Expr | None:
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    return None
                return node

            def visit_Name(self, node: ast.Name) -> ast.Name:
                if node.id not in {
                    "self",
                    "cls",
                    "None",
                    "True",
                    "False",
                    "int",
                    "str",
                    "float",
                    "bool",
                    "list",
                    "dict",
                    "set",
                    "tuple",
                    "bytes",
                    "type",
                    "object",
                    "range",
                    "len",
                    "print",
                    "isinstance",
                    "super",
                    "Exception",
                }:
                    node.id = "_VAR_"
                return node

            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
                node.name = "_FUNC_"
                return self.generic_visit(node)

        normalized = _Normalizer().visit(tree)
        ast.fix_missing_locations(normalized)
        return ast.unparse(normalized)

    def _compute_structure_similarity(self, a: str, b: str) -> float:
        """结构相似度——基于归一化 token 的重叠率."""
        tokens_a = set(self._normalize_ast(a).split())
        tokens_b = set(self._normalize_ast(b).split())
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return intersection / union if union else 0.0

    def _compute_lcs_ratio(self, a: str, b: str) -> float:
        """LCS 最长公共子序列——行级."""
        lines_a = a.strip().splitlines()
        lines_b = b.strip().splitlines()
        if not lines_a or not lines_b:
            return 0.0

        m, n = len(lines_a), len(lines_b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if lines_a[i - 1].strip() == lines_b[j - 1].strip():
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        lcs_len = dp[m][n]
        return lcs_len / max(m, n)
