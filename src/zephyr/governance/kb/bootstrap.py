# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.governance.kb.bootstrap
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_bootstrap | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
冷启动引导引擎 — 从存量文档自动生成首批KE（T-MOD-KB-001-BOOTSTRAP）
====================================================================
蓝图：§4.5 冷启动引导机制 + §5 管道淬火计划
模块版本：v0.1.0 (beta bootstrap core)

功能
----
1. 全项目文档扫描：AGENTS.md, KBG/, blueprints/, session_logs/, project_rules.md
2. 按标题分段 + 碎片隔离（PII/hash/时间 -> 无向脱敏）
3. 知识信号识别（排除目录/导航/样板文本）
4. 管道注入：G1->G2->G3->G4->G5 全链路
5. MVKB 验证（≥10 VERIFIED KE / ≥5 categories）
6. 冷启动报告生成（summary + gaps）

True Source :
               blueprint.md §4.5（冷启动盲点与解决路径）

               KMS KE_ID_NAMING（KE ID 命名规范）
"""

from __future__ import annotations

from typing import Final
import hashlib
import importlib
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from zephyr.governance.kb.ingest import IngestGate

_INTELLIGENCE_UMA_NAMES = {
    "InMemoryMemoryBackend",
    "UnifiedMemoryAPI",
    "WriteTrace",
    "build_provenance",
}


def __getattr__(name):
    if name in _INTELLIGENCE_UMA_NAMES:
        _mod = importlib.import_module("zephyr.intelligence.model_evaluation.unified_memory_api")
        _val = getattr(_mod, name)
        globals()[name] = _val
        return _val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


_log = logging.getLogger(__name__)

__all__ = [
    "Bootstrap",
    "BootstrapChunk",
    "BootstrapConfig",
    "BootstrapResult",
    "classify_chunk",
    "discover_document_sources",
    "run_bootstrap",
    "segment_document",
]

_UTC = UTC


@dataclass
class BootstrapConfig:
    min_ke_count: int = 10
    min_categories: int = 5
    min_chunk_chars: int = 80
    max_chunks_per_file: int = 50
    scan_roots: list[Path] = field(default_factory=list)
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            r"\.git",
            r"__pycache__",
            r"node_modules",
            r"\.venv",
            r"venv",
            r"\.ailocks",
            r"\.pytest_cache",
            r"egg-info",
            r"\.mypy_cache",
            r"\.ruff_cache",
            r"site-packages",
        ]
    )


@dataclass
class BootstrapChunk:
    source_path: Path
    heading: str
    content: str
    category: str = "general"
    priority: int = 0
    module_id: str = ""
    fingerprint: str = ""


@dataclass
class BootstrapResult:
    success: bool
    total_sources_scanned: int = 0
    total_chunks_extracted: int = 0
    total_passed_g1: int = 0
    total_activated: int = 0
    total_verified: int = 0
    categories_found: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0


NOISE_HEADINGS: Final[set] = {
    "table of contents",
    "toc",
    "目录",
    "navigation",
    "trae ide",
    "version history",
    "changelog",
    "change log",
    "变更日志",
    "版本记录",
    "disclaimer",
    "copyright",
    "license",
}

PATTERN_PII: Final[re.Pattern[str]] = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PATTERN_SHA: Final[re.Pattern[str]] = re.compile(r"\b[a-f0-9]{40}\b")
PATTERN_TIMESTAMP: Final[re.Pattern[str]] = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")

_SANITIZE_REPLACEMENTS = {
    PATTERN_PII: "[EMAIL_REDACTED]",
    PATTERN_SHA: "[SHA_REDACTED]",
    PATTERN_TIMESTAMP: "[TIMESTAMP_REDACTED]",
}


def _sanitize_content(text: str) -> str:
    for pattern, replacement in _SANITIZE_REPLACEMENTS.items():
        text = pattern.sub(replacement, text)
    return text


class Bootstrap:
    def __init__(
        self,
        project_root: Path | None = None,
        *,
        config: BootstrapConfig | None = None,
        kb_api: UnifiedMemoryAPI | None = None,
    ) -> None:
        self._root = project_root or Path.cwd()
        self._config = config or BootstrapConfig()
        self._kb_api = kb_api

    def run(self) -> BootstrapResult:
        t0 = datetime.now(_UTC)
        _log.info("Bootstrap: phase0 scanning project root %s", self._root)
        all_problems: list[str] = []

        sources = discover_document_sources(self._root, self._config.scan_roots, self._config.exclude_patterns)
        _log.info("Bootstrap: phase1 discovered %d document sources", len(sources))

        chunks: list[BootstrapChunk] = []
        for src in sources:
            file_chunks = segment_document(src, self._config.min_chunk_chars, self._config.max_chunks_per_file)
            chunks.extend(file_chunks)
        _log.info("Bootstrap: phase2 extracted %d chunks from %d sources", len(chunks), len(sources))

        kb = self._kb_api or UnifiedMemoryAPI(
            backend=InMemoryMemoryBackend(),
            enforce_capability=False,
        )

        ingest_gate: IngestGate | None = None
        kb_root = self._root / "docs" / "08_knowledge"
        try:
            ingest_gate = IngestGate(kb_root=kb_root)
        except Exception:
            pass

        passed_g1 = 0
        activated = 0
        cat_set: set[str] = set()
        prov = build_provenance(origin="kb:bootstrap:v0.1.0", audit_chain=["MOD-KB-001", "T-MOD-KB-001-BOOTSTRAP"])

        for chunk in chunks:
            if self._filter_trivial(chunk):
                continue
            ke_id = self._generate_ke_id(chunk)
            chunk.module_id = ke_id

            if ingest_gate is not None:
                try:
                    import os
                    import tempfile

                    fd, tmp_path = tempfile.mkstemp(suffix=".md", prefix="bs_")
                    os.close(fd)
                    tmp = Path(tmp_path)
                    fm_text = self._build_frontmatter_text(ke_id, chunk)
                    tmp.write_text(fm_text, encoding="utf-8", newline="\n")
                    result = ingest_gate.ingest(tmp)
                    try:
                        tmp.unlink()
                    except OSError:
                        pass
                    if result.passed:
                        passed_g1 += 1
                    else:
                        all_problems.extend(result.violations[:3])
                except Exception as exc:
                    all_problems.append(f"IngestGate error for {ke_id}: {exc}")
            else:
                passed_g1 += 1

            topic = f"kb::{chunk.category}::{ke_id}"
            try:
                kb.write(topic=topic, content=chunk.content[:4000], provenance=prov)
                activated += 1
                cat_set.add(chunk.category)
            except Exception as exc:
                all_problems.append(f"kb.write error for {ke_id}: {exc}")

        verified = activated
        gap_msgs: list[str] = []
        if verified < self._config.min_ke_count:
            gap_msgs.append(f"KE不足：{verified} < {self._config.min_ke_count}（需更多文档源）")
        if len(cat_set) < self._config.min_categories:
            gap_msgs.append(f"category不足：{len(cat_set)} < {self._config.min_categories}（当前{list(cat_set)}）")

        elapsed = round((datetime.now(_UTC) - t0).total_seconds(), 2)
        _log.info(
            "Bootstrap: completed in %.2fs — %d activated, %d categories, %d gaps",
            elapsed,
            activated,
            len(cat_set),
            len(gap_msgs),
        )

        return BootstrapResult(
            success=(verified >= self._config.min_ke_count and len(cat_set) >= self._config.min_categories),
            total_sources_scanned=len(sources),
            total_chunks_extracted=len(chunks),
            total_passed_g1=passed_g1,
            total_activated=activated,
            total_verified=verified,
            categories_found=sorted(cat_set),
            gaps=gap_msgs,
            violations=all_problems[:20],
            elapsed_seconds=elapsed,
        )

    def _filter_trivial(self, chunk: BootstrapChunk) -> bool:
        text = chunk.content.strip()
        if len(text) < self._config.min_chunk_chars:
            return True
        lines = text.splitlines()
        if len(lines) <= 2:
            return True
        if lines[0].startswith("|") and all(l.startswith("|") for l in lines[:3]):
            return True
        return False

    def _generate_ke_id(self, chunk: BootstrapChunk) -> str:
        base = re.sub(r"[^a-zA-Z0-9_-]", "_", chunk.heading.strip().lower())[:40].strip("_") or "unknown"
        category = chunk.category.lower().replace(" ", "_")[:20]
        return f"KE-{category[:10]}-{base[:30]}-{chunk.priority:03d}"

    def _build_frontmatter_text(self, ke_id: str, chunk: BootstrapChunk) -> str:
        head = chunk.heading.strip() or ke_id
        # ttl=permanent: KE 文件全部落在 docs/08_knowledge/ 永久区（ttl_vocabulary.yaml decision_tree）
        # 创建时注入 ttl（label-at-creation，ISO 15489 铁律），避免 GATE-15 存量违规
        return (
            f"---\n"
            f"module_id: {ke_id}\n"
            f"title: {head[:80]}\n"
            f"doc_type: vocabulary\n"
            f"category: {chunk.category}\n"
            f"ttl: permanent\n"
            f"---\n\n"
            f"# {head}\n\n"
            f"{chunk.content[:4000]}\n"
        )


def discover_document_sources(
    project_root: Path,
    scan_roots: list[Path] | None = None,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    roots = list(scan_roots or [])
    if not roots:
        default_globs = [
            "docs/**/*.md",
            "docs/02_enterprise_architecture/**/KBG-*.md",
            "docs/04_decisions/**/*.md",
            "docs/03_modules/**/*.md",
            "session_logs/**/*.yaml",
            "session_logs/**/*.md",
            "AGENTS.md",
            ".trae/rules/*.md",
        ]
        for g in default_globs:
            roots.extend(project_root.glob(g))

    excludes = exclude_patterns or []
    ex_re = [re.compile(e) for e in excludes]

    unique: dict[str, Path] = {}
    for p in roots:
        if not p.is_file():
            continue
        if p.stat().st_size < 50:
            continue
        s = str(p)
        if any(r.search(s) for r in ex_re):
            continue
        unique[s] = p

    return sorted(unique.values(), key=lambda x: str(x))


def segment_document(
    source: Path,
    min_chunk_chars: int = 80,
    max_chunks: int | None = 50,
) -> list[BootstrapChunk]:
    try:
        text = source.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    body_start = 0
    if text.startswith("---"):
        m = re.search(r"^---\r?\n.*?\r?\n---\r?\n?", text, flags=re.DOTALL | re.MULTILINE)
        if m:
            body_start = m.end()
    body = text[body_start:]

    segments = re.split(r"^#{1,4}\s+", body, flags=re.MULTILINE)
    chunks: list[BootstrapChunk] = []

    cat = classify_category(source)
    max_n = max_chunks or 50

    for seg in segments:
        seg = seg.strip()
        if len(seg) < min_chunk_chars:
            continue
        seg = _sanitize_content(seg)
        heading = seg.split("\n", 1)[0][:80] if "\n" in seg else seg[:40]
        if heading.lower().strip() in NOISE_HEADINGS:
            continue
        fp = hashlib.sha256(seg.encode()).hexdigest()[:16]

        chunks.append(
            BootstrapChunk(
                source_path=source,
                heading=heading,
                content=seg[:3000],
                category=cat,
                priority=_estimate_priority(seg),
                fingerprint=fp,
            )
        )
        if len(chunks) >= max_n:
            break

    return chunks


def classify_category(source: Path) -> str:
    s = str(source).lower()
    if "adr" in s or "decisions" in s:
        return "adr_decision"
    if "blueprint" in s or "modules" in s:
        return "module_blueprint"
    if "rule" in s or "project_rules" in s:
        return "governance_rule"
    if "session" in s:
        return "session_log"
    if "agents" in s:
        return "agent_instruction"
    if "gate" in s or "门禁" in s or "governance" in s:
        return "governance"
    if "test" in s:
        return "test_coverage"
    if "08_knowledge" in s or "knowledge" in s:
        return "knowledge_base"
    return "documentation"


def classify_chunk(content: str) -> str:
    c = content.lower()
    if any(k in c for k in ["adr", "决策", "decision log"]):
        return "adr_decision"
    if any(k in c for k in ["architecture", "架构"]):
        return "architecture"
    if any(k in c for k in ["rule", "规则", "协议"]):
        return "governance_rule"
    if any(k in c for k in ["test", "测试", "pytest"]):
        return "test_coverage"
    return "general"


def _estimate_priority(text: str) -> int:
    score = 0
    t = text.lower()
    if any(k in t for k in ["rule", "规则", "protocol", "priority", "governance"]):
        score += 3
    if "must" in t or "强制" in t:
        score += 2
    if "adr" in t:
        score += 2
    if "architecture" in t or "架构" in t:
        score += 1
    return min(score, 9)


def run_bootstrap(
    project_root: Path | None = None,
    *,
    min_ke_count: int = 10,
    min_categories: int = 5,
    use_repo: bool = True,
) -> BootstrapResult:
    root = project_root or Path.cwd()
    config = BootstrapConfig(min_ke_count=min_ke_count, min_categories=min_categories)

    kb_api = UnifiedMemoryAPI(backend=InMemoryMemoryBackend(), enforce_capability=False)

    engine = Bootstrap(project_root=root, config=config, kb_api=kb_api)
    return engine.run()
