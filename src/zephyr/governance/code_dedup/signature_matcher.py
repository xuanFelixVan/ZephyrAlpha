# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.signature_matcher
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/security/test_signature_matcher.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_signature_matcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Stage 0.5: 签名指纹 SHA256[:12] O(1) 精确匹配.

职责：
  - 对函数签名（param_types + return_type）计算 SHA256[:12] 指纹
  - O(1) 字典查询——匹配已有函数签名 -> 输出 COLLISION / NEAR_COLLISION
  - 路径感知阈值：shared/ 内签名碰撞 -> CRITICAL，tests/ -> LOW
  - Vibe Coding 场景性价比最高的检测维度
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass, field


@dataclass
class SignatureMatch:
    fingerprint: str
    existing: list[str] = field(default_factory=list)
    confidence: float = 0.0
    level: str = "LOW"
    method: str = "signature_collision"


class SignatureMatcher:
    """Stage 0.5 签名指纹匹配器."""

    # 路径感知级别阈值
    _PATH_LEVELS: dict[str, str] = {
        "shared": "CRITICAL",
        "core": "HIGH",
        "tests": "LOW",
    }

    def __init__(self) -> None:
        self._index: dict[str, list[str]] = {}

    # ── 公共 API ──────────────────────────────────────────────

    def build_index(self, entries: list[dict]) -> None:
        """从缓存条目构建签名索引."""
        self._index.clear()
        for entry in entries:
            fp = entry.get("signature_fingerprint", "")
            if fp:
                self._index.setdefault(fp, []).append(f"{entry.get('file', '?')}::{entry.get('name', '?')}")

    def compute_fingerprint(self, param_types: list[str], return_type: str = "") -> str:
        """计算签名指纹 = SHA256(param_types + return_type)[:12]."""
        canonical = "(" + ",".join(sorted(param_types)) + ")"
        if return_type:
            canonical += "->" + return_type
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]

    def match(self, fingerprint: str, file_path: str = "") -> SignatureMatch | None:
        """O(1) 精确匹配——返回碰撞结果."""
        candidates = self._index.get(fingerprint)
        if not candidates:
            return None

        level = self._classify_path(file_path)
        return SignatureMatch(
            fingerprint=fingerprint,
            existing=candidates,
            confidence=0.95 if level == "CRITICAL" else 0.85,
            level=level,
            method="signature_collision",
        )

    def match_bulk(self, fingerprints: list[tuple[str, str]]) -> list[SignatureMatch]:
        """批量匹配 [(fingerprint, file_path), ...]."""
        results: list[SignatureMatch] = []
        for fp, fpath in fingerprints:
            match = self.match(fp, fpath)
            if match:
                results.append(match)
        return results

    # ── AST 辅助 ──────────────────────────────────────────────

    @staticmethod
    def extract_signature(func_source: str) -> tuple[list[str], str]:
        """AST 解析函数签名——返回 (param_types, return_type)."""
        try:
            tree = ast.parse(func_source.lstrip())
        except SyntaxError:
            return [], ""

        if not tree.body:
            return [], ""
        node = tree.body[0]
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return [], ""

        param_types: list[str] = []
        for arg in node.args.args:
            anno = arg.annotation
            if anno is not None:
                param_types.append(ast.unparse(anno))
            else:
                param_types.append("Any")

        return_type = ""
        if node.returns:
            return_type = ast.unparse(node.returns)

        return param_types, return_type

    # ── 内部 ──────────────────────────────────────────────────

    @classmethod
    def _classify_path(cls, file_path: str) -> str:
        path_lower = file_path.lower().replace("\\", "/")
        for keyword, level in cls._PATH_LEVELS.items():
            if keyword in path_lower:
                return level
        return "MEDIUM"
