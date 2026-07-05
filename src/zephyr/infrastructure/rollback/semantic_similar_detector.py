# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.semantic_similar_detector
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_semantic_similar_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SemanticSimilarDetector — 语义变形攻击检测。

依据: 蓝图 MOD-INF-021 §7 Phase 6.3 + §6.12 B58 + D-021-13 + exit code 12

检测 AI 通过 AST 改写绕过回滚门禁的 "morphing" 攻击:
    回滚前代码 vs 回滚后代码的 AST 语义相似度。
    >70% 相似度 → 语义变形 (malicious rewrite) → exit code 12 → L2 Skill Kill。
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MorphingReport:
    file_path: str
    old_source: str
    new_source: str
    ast_similarity: float
    call_chain_similarity: float
    sensitive_api_match_count: int
    is_morphing: bool
    exit_code: int
    details: list[str] = field(default_factory=list)


SENSITIVE_APIS = {
    "eval",
    "exec",
    "compile",
    "os.system",
    "os.popen",
    "subprocess.call",
    "subprocess.Popen",
    "os.remove",
    "os.unlink",
    "shutil.rmtree",
    "open",
    "__import__",
    "importlib.import_module",
    "pickle.loads",
    "pickle.dumps",
}


class SemanticSimilarDetector:
    SIMILARITY_THRESHOLD: float = 0.70
    EXIT_CODE_MORPHING: int = 12

    def __init__(self) -> None:
        pass

    def compare(self, old_source: str, new_source: str, file_path: str = "") -> MorphingReport:
        old_ast = self._parse_safe(old_source)
        new_ast = self._parse_safe(new_source)

        ast_sim = self._ast_structure_similarity(old_ast, new_ast)
        call_sim = self._call_chain_similarity(old_source, new_source)
        sensitive_matches = self._count_sensitive_api_matches(new_source)

        is_morphing = ast_sim > self.SIMILARITY_THRESHOLD and old_source.strip() != new_source.strip()

        details: list[str] = []
        details.append(f"AST structural similarity: {ast_sim:.2%}")
        details.append(f"Call chain similarity: {call_sim:.2%}")
        details.append(f"Sensitive API matches in new code: {sensitive_matches}")

        if is_morphing:
            details.append(f"MORPHING DETECTED: >{self.SIMILARITY_THRESHOLD:.0%} similarity but different text")

        return MorphingReport(
            file_path=file_path,
            old_source=old_source,
            new_source=new_source,
            ast_similarity=ast_sim,
            call_chain_similarity=call_sim,
            sensitive_api_match_count=sensitive_matches,
            is_morphing=is_morphing,
            exit_code=self.EXIT_CODE_MORPHING if is_morphing else 0,
            details=details,
        )

    def compare_files(self, old_path: Path, new_path: Path) -> MorphingReport:
        old_src = old_path.read_text(encoding="utf-8") if old_path.exists() else ""
        new_src = new_path.read_text(encoding="utf-8") if new_path.exists() else ""
        return self.compare(old_src, new_src, file_path=str(new_path))

    def _parse_safe(self, source: str) -> ast.AST | None:
        try:
            return ast.parse(source)
        except SyntaxError:
            return None

    def _ast_structure_similarity(self, old_tree: ast.AST | None, new_tree: ast.AST | None) -> float:
        if old_tree is None and new_tree is None:
            return 1.0
        if old_tree is None or new_tree is None:
            return 0.0

        old_features = self._extract_features(old_tree)
        new_features = self._extract_features(new_tree)

        if not old_features and not new_features:
            return 1.0

        common = len(old_features & new_features)
        total = len(old_features | new_features)
        return common / total if total > 0 else 1.0

    def _extract_features(self, tree: ast.AST) -> set[str]:
        features: set[str] = set()
        for node in ast.walk(tree):
            features.add(type(node).__name__)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                features.add(f"func:{node.name}")
            elif isinstance(node, ast.ClassDef):
                features.add(f"class:{node.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    features.add(f"import:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    features.add(f"importfrom:{node.module}.{alias.name}" if node.module else f"import:{alias.name}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    features.add(f"call:{node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    features.add(f"call_attr:{ast.unparse(node.func)}")
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        features.add(f"assign:{target.id}")
        return features

    def _call_chain_similarity(self, old_source: str, new_source: str) -> float:
        old_tree = self._parse_safe(old_source)
        new_tree = self._parse_safe(new_source)
        if old_tree is None and new_tree is None:
            return 1.0
        if old_tree is None or new_tree is None:
            return 0.0

        old_calls = self._collect_calls(old_tree)
        new_calls = self._collect_calls(new_tree)

        if not old_calls and not new_calls:
            return 1.0

        common = len(old_calls & new_calls)
        total = len(old_calls | new_calls)
        return common / total if total > 0 else 1.0

    def _collect_calls(self, tree: ast.AST) -> set[str]:
        calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                calls.add(ast.unparse(node.func))
        return calls

    def _count_sensitive_api_matches(self, source: str) -> int:
        count = 0
        tree = self._parse_safe(source)
        if tree is None:
            return 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_str = ast.unparse(node.func)
                for api in SENSITIVE_APIS:
                    if api in call_str:
                        count += 1
                        break
        return count

    def is_morphing_attack(self, old_source: str, new_source: str) -> tuple[bool, float]:
        report = self.compare(old_source, new_source)
        return report.is_morphing, report.ast_similarity
