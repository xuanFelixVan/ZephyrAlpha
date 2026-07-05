# [BLUEPRINT]
# [MODULE] zephyr.security.access_control.orphan_judge.duplicate_detector
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_duplicate_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import ast
import hashlib
import logging
import time
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_DEFAULT_THRESHOLD = 0.85
_DEFAULT_SCOPE = "src/zephyr/"


class DuplicateResult(BaseModel):
    has_duplicates: bool
    top_matches: list[tuple[str, float]] = Field(default_factory=list)
    search_duration_ms: float = 0.0


class DuplicateDetector:
    """L2 功能重复检测器——基于 AST 哈希的 Jaccard 相似度检测模块间功能重叠。

    检测策略：
      1. 解析每个 .py 文件的 AST，提取函数/类名+参数签名
      2. 生成标准化 AST 哈希（函数名+参数+返回类型）
      3. 对目标文件与范围内所有文件计算 Jaccard 相似度
      4. 相似度 >= threshold 的归入 top_matches
    降级原则：AST 解析失败 → 假设不重复，返回空结果
    """

    def __init__(self, similarity_threshold: float = _DEFAULT_THRESHOLD) -> None:
        self._threshold = similarity_threshold

    def detect(self, target_path: str, scope: str = _DEFAULT_SCOPE) -> DuplicateResult:
        start = time.monotonic()
        target_hash = self._compute_ast_hash(target_path)
        if not target_hash:
            elapsed_ms = (time.monotonic() - start) * 1000
            return DuplicateResult(has_duplicates=False, search_duration_ms=elapsed_ms)

        candidates = self._scan_scope(scope)
        matches: list[tuple[str, float]] = []

        for candidate_path in candidates:
            if Path(candidate_path).resolve() == Path(target_path).resolve():
                continue
            candidate_hash = self._compute_ast_hash(candidate_path)
            if not candidate_hash:
                continue
            similarity = self._compute_similarity(target_hash, candidate_hash)
            if similarity >= self._threshold:
                matches.append((candidate_path, round(similarity, 4)))

        matches.sort(key=lambda m: m[1], reverse=True)
        elapsed_ms = (time.monotonic() - start) * 1000

        return DuplicateResult(
            has_duplicates=len(matches) > 0,
            top_matches=matches,
            search_duration_ms=round(elapsed_ms, 2),
        )

    def _compute_ast_hash(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists() or path.suffix != ".py":
            return ""
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (SyntaxError, UnicodeDecodeError, OSError):
            logger.warning("AST parse failed, degrading to empty hash: %s", path)
            return ""

        signatures: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sig = self._function_signature(node)
                signatures.append(sig)
            elif isinstance(node, ast.ClassDef):
                sig = self._class_signature(node)
                signatures.append(sig)

        if not signatures:
            return ""

        canonical = "\n".join(sorted(signatures))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _compute_similarity(self, hash_a: str, hash_b: str) -> float:
        if not hash_a or not hash_b:
            return 0.0
        if hash_a == hash_b:
            return 1.0
        set_a = set(hash_a)
        set_b = set(hash_b)
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        if union == 0:
            return 0.0
        return intersection / union

    def _scan_scope(self, scope: str) -> list[str]:
        scope_path = Path(scope)
        if not scope_path.is_dir():
            scope_path = Path.cwd() / scope
        if not scope_path.is_dir():
            logger.warning("Scope directory not found: %s", scope)
            return []

        results: list[str] = []
        for py_file in scope_path.rglob("*.py"):
            if any(p in py_file.parts for p in ("__pycache__", ".mypy_cache", "_snapshots", ".aidrafts")):
                continue
            results.append(str(py_file))
        return results

    def batch_detect(self, targets: list[str]) -> list[DuplicateResult]:
        return [self.detect(target) for target in targets]

    @staticmethod
    def _function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        arg_names = [a.arg for a in node.args.args if a.arg != "self"]
        return_type = "Any"
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except Exception:
                return_type = "Any"
        return f"def {node.name}({', '.join(arg_names)}) -> {return_type}"

    @staticmethod
    def _class_signature(node: ast.ClassDef) -> str:
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                bases.append("Any")
        method_names = sorted(n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        return f"class {node.name}({', '.join(bases)}): [{', '.join(method_names)}]"
