# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §4.1
# [MODULE] zephyr.governance.semantic_audit.reference_extractor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.semantic_audit.models
# [CONSUMERS] trigger_engine; alignment_engine; safety_boundary
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 提取 9 个维度的引用；AST 解析覆盖 import/call/inherit/BLUEPRINT 头部
# [MODIFY-GUARD] 新增维度必须同步 models.ExtractedReferences 字段
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SyntaxError/OSError 时返回空 ExtractedReferences + 日志警告
# [TESTS] tests/semantic-auditor/test_reference_extractor.py
# [A_module] module_id=MOD-GOV_reference_extractor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — 引用提取器 Stage 1

AST 解析文件，提取 9 个维度的引用信息。
"""

from __future__ import annotations

import ast
import logging
import re
from pathlib import Path

from zephyr.governance.semantic_audit.models import ExtractedReferences

logger = logging.getLogger(__name__)

_BLUEPRINT_HEADER_RE = re.compile(r"^#\s*\[(?P<key>[A-Z_]+)\]\s*(?P<value>.*)", re.MULTILINE)
_INTERNAL_RULE_RE = re.compile(r"\b[A-Z]{2,5}-\d{3,4}\b")
_MODULE_ID_RE = re.compile(r"\b(MOD|DOC|TPL|REG|GOV|PS|MTH|IRN|TASK|KBG|CP|KE|STD|BLP)-\w+-\d+\b")
_SECTION_REF_RE = re.compile(r"§\d+\.\d+(?:\.\d+)?")
_SCRIPT_REF_RE = re.compile(r"`\.\./scripts/([^`]+)`|scripts/([\w/]+\.py)")
_BLUEPRINT_LINK_RE = re.compile(r"\(file://[^)]+\.md[^)]*\)|\[[^]]*\]\([^)]*blueprint[^)]*\.md[^)]*\)")
_NUMERIC_CLAIM_RE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(个|条|项|files?|scripts?|modules?|gates?|registr(?:y|ies)|lines?)\b"
)
_DEPENDS_ON_RE = re.compile(r"depends_on\s*[=:]\s*\[([^\]]+)\]")


def _parse_path(path_str: str) -> list[str]:
    return [s.strip(" '\"") for s in path_str.split(",") if s.strip(" '\"")]


def _to_path_str(p: str | Path) -> str:
    return str(p).replace("\\", "/")


class ReferenceExtractor:
    def extract(self, file_path: str | Path) -> ExtractedReferences:
        file_path = Path(file_path)
        refs = ExtractedReferences()

        if not file_path.exists():
            logger.warning("File not found: %s", file_path)
            return refs

        content = self._read_file(file_path)
        if content is None:
            return refs

        ext = file_path.suffix.lower()
        rel = _to_path_str(file_path)

        if ext == ".py":
            refs.file_paths = self._extract_py_paths(content)
            refs.depends_on_targets = self._extract_depends_on(content)
            self._extract_blueprint_headers(content, refs)
        elif ext in (".md", ".yaml", ".yml"):
            pass

        refs.file_paths.append(rel)

        blueprint_hits = _BLUEPRINT_LINK_RE.findall(content)
        refs.blueprint_links = [str(h) for h in blueprint_hits]

        refs.internal_rule_ids = _INTERNAL_RULE_RE.findall(content)
        refs.module_id_refs = _MODULE_ID_RE.findall(content)
        refs.section_refs = _SECTION_REF_RE.findall(content)

        for name in _SCRIPT_REF_RE.findall(content):
            script = name[0] or name[1]
            if script:
                refs.script_refs.append(script)

        refs.numeric_claims = [{"value": m.group(1), "unit": m.group(2)} for m in _NUMERIC_CLAIM_RE.finditer(content)]

        return refs

    def extract_batch(self, file_paths: list[str]) -> dict[str, ExtractedReferences]:
        results = {}
        for fp in file_paths:
            results[_to_path_str(fp)] = self.extract(fp)
        return results

    def _read_file(self, file_path: Path) -> str | None:
        try:
            return file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            logger.warning("Cannot read %s: %s", file_path, exc)
            return None

    def _extract_py_paths(self, content: str) -> list[str]:
        paths: list[str] = []
        try:
            tree = ast.parse(content)
        except SyntaxError as exc:
            logger.warning("AST parse failed: %s", exc)
            return paths

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    paths.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    paths.append(node.module)
        return paths

    def _extract_depends_on(self, content: str) -> list[dict]:
        results = []
        for m in _DEPENDS_ON_RE.finditer(content):
            raw = m.group(1)
            targets = _parse_path(raw)
            for t in targets:
                results.append({"target": t, "raw_line": m.group(0)})
        return results

    def _extract_blueprint_headers(self, content: str, refs: ExtractedReferences) -> None:
        meta: dict = {}
        for m in _BLUEPRINT_HEADER_RE.finditer(content):
            meta[m.group("key")] = m.group("value").strip()

        if meta:
            refs.frontmatter_metadata = meta
            if "CONSUMERS" in meta:
                for c in _parse_path(meta["CONSUMERS"]):
                    refs.depends_on_targets.append({"target": c, "source": "BLUEPRINT-CONSUMERS"})
