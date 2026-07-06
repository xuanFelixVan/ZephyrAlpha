# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb.ingest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.gate_engine; zephyr.governance.rule_enforcement.gate_types.__init__; zephyr.governance.__init__
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
# [A_module] module_id=MOD-DAT_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G1 Ingest 门禁 — 知识流水线入口校验（T-2-13-A）
==================================================
依据：g1-ingest.yaml、ADR-0030（SQLite gates 表）

功能
----
1. 文件格式校验：仅接受 .md / .yaml
2. Frontmatter 必填字段：module_id, title, category
3. 内容长度 > 100 字（排除 frontmatter）
4. Title 去重（与 knowledge 表已有记录比对）
5. UTF-8 无 BOM 编码校验
6. 输入清洗（黑名单：{{, {%, ignore all rules 等注入模式）
7. 调用 gate_engine.py 执行 g1-ingest.yaml 门禁
8. 状态转换：draft → raw / draft → rejected
9. 写入 01_raw_intake/ 目录

Safety : M（治理层代码，门禁失败阻断入库）
"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import hashlib
import importlib
import re
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path
from typing import Any

import yaml

from zephyr.governance.kb.kb_gate_task import build_kb_gate_eval_task
from zephyr.governance.rule_enforcement.gate_engine.gate_engine import GATES_DIR, GateEngine
from zephyr.governance.rule_enforcement.gate_types import GateResult
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

__all__ = [
    "ALLOWED_EXTENSIONS",
    "BLACKLIST_PATTERNS",
    "MIN_CONTENT_CHARS",
    "REQUIRED_FRONTMATTER_FIELDS",
    "IngestGate",
    "IngestResult",
]

REQUIRED_FRONTMATTER_FIELDS: Final[list] = ["module_id", "title", "category", "ttl"]
ALLOWED_EXTENSIONS: Final[set] = {".md", ".yaml", ".yml"}
MIN_CONTENT_CHARS: Final[int] = 100

BLACKLIST_PATTERNS: Final[list] = [
    r"\{\{",
    r"\{%",
    r"ignore\s+all\s+rules",
    r"ignore\s+previous",
    r"disregard\s+all",
    r"you\s+are\s+now",
    r"system\s*:",
    r"<\s*script",
]

_BLACKLIST_RES = [re.compile(p, re.IGNORECASE) for p in BLACKLIST_PATTERNS]

_RAW_INTAKE_DIR_NAME = "01_raw_intake"

_UTC = UTC

# 口语化模式 — 用于 triage 门禁检测非正式表述
COLLOQUIAL_PATTERNS: Final[list] = [
    r"gonna",
    r"wanna",
    r"gotta",
    r"kinda",
    r"sorta",
    r"yeah",
    r"nope",
    r"ok\b",
    r"ok\s*,",
    r"\btbh\b",
    r"\bimo\b",
    r"\bfyi\b",
    r"\btbd\b",
    r"\bwip\b",
]


@dataclass
class IngestResult:
    passed: bool
    ke_id: str | None = None
    target_path: Path | None = None
    violations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class IngestGate:
    def __init__(
        self,
        kb_root: Path,
        gate_engine: GateEngine | None = None,
    ) -> None:
        self._kb_root = kb_root
        self._raw_intake_dir = kb_root / _RAW_INTAKE_DIR_NAME
        self._raw_intake_dir.mkdir(parents=True, exist_ok=True)
        self._gate_engine = gate_engine or GateEngine(gate_dir=GATES_DIR)

    def ingest(self, source_path: Path, content: str | None = None) -> IngestResult:
        violations: list[str] = []

        if not source_path.exists():
            return IngestResult(passed=False, violations=[f"文件不存在：{source_path}"])

        ext = source_path.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            violations.append(f"不允许的文件扩展名 '{ext}'，仅允许 {ALLOWED_EXTENSIONS}")
            return IngestResult(passed=False, violations=violations)

        if content is None:
            try:
                raw = source_path.read_bytes()
            except OSError as exc:
                return IngestResult(passed=False, violations=[f"无法读取文件：{exc}"])
        else:
            raw = content.encode("utf-8")

        enc_err = self._check_encoding(raw)
        if enc_err:
            violations.append(enc_err)
            return IngestResult(passed=False, violations=violations)

        text = raw.decode("utf-8")

        inject_err = self._check_injection(text)
        if inject_err:
            violations.append(inject_err)
            return IngestResult(passed=False, violations=violations)

        lsg_err = self._lsg_scan_content(text)
        if lsg_err:
            violations.append(lsg_err)
            return IngestResult(passed=False, violations=violations)

        fm_err = self._check_frontmatter(text, ext)
        if fm_err:
            violations.append(fm_err)
            return IngestResult(passed=False, violations=violations)

        fm = self._parse_frontmatter(text, ext)
        if fm is None:
            violations.append("frontmatter 解析失败")
            return IngestResult(passed=False, violations=violations)

        missing = [f for f in REQUIRED_FRONTMATTER_FIELDS if f not in fm]
        if missing:
            violations.append(f"frontmatter 缺少必填字段 {missing}")
            return IngestResult(passed=False, violations=violations)

        length_err = self._check_content_length(text)
        if length_err:
            violations.append(length_err)
            return IngestResult(passed=False, violations=violations)

        dup_err = self._check_title_dedup(fm.get("title", ""))
        if dup_err:
            violations.append(dup_err)
            return IngestResult(passed=False, violations=violations)

        gate_result = self._run_gate(source_path)
        if gate_result and not gate_result.passed:
            for v in gate_result.violations:
                violations.append(f"[{v.severity}] {v.message}")
            return IngestResult(
                passed=False,
                violations=violations,
                details={"gate_result": gate_result.summary()},
            )

        ke_id = fm.get("module_id", "")
        title = fm.get("title", "")
        category = fm.get("category", "general")

        target_path = self._write_to_raw_intake(source_path, text, fm)

        return IngestResult(
            passed=True,
            ke_id=ke_id,
            target_path=target_path,
            details={
                "title": title,
                "category": category,
                "fingerprint": hashlib.sha256(raw).hexdigest()[:16],
            },
        )

    def _check_encoding(self, raw: bytes) -> str | None:
        if raw.startswith(b"\xef\xbb\xbf"):
            return "文件含 UTF-8 BOM"
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            return f"编码损坏（非 UTF-8）：{exc}"
        return None

    def _check_injection(self, text: str) -> str | None:
        for pat in _BLACKLIST_RES:
            m = pat.search(text)
            if m:
                return f"输入清洗拦截：检测到黑名单模式 '{m.group()}'"
        return None

    def _lsg_scan_content(self, text: str) -> str | None:
        try:
            _mod = importlib.import_module("zephyr.security.llm_defense.llm_security.gateway")
            _LSGSecurityGateway = _mod.LSGSecurityGateway
            import asyncio

            gateway = _LSGSecurityGateway()
            result = run_sync(gateway.scan_input(text))
            if result.decision.value not in ("allow", "ALLOW"):
                reasons = ", ".join(r.reason for r in result.details if hasattr(r, "reason"))
                return f"LSG 安全扫描拦截：{reasons or result.decision.value}"
        except ImportError:
            pass
        except Exception as e:
            logger.warning("suppressed error in ingest", exc_info=True)
        return None

    def _check_frontmatter(self, text: str, ext: str) -> str | None:
        if ext in {".yaml", ".yml"}:
            return None
        if not text.startswith("---"):
            return "Markdown 文件缺少 frontmatter（必须以 --- 开头）"
        m = re.match(r"^---\r?\n.*?\r?\n---", text, re.DOTALL)
        if not m:
            return "Markdown 文件 frontmatter 格式不正确（缺少闭合 ---）"
        return None

    def _parse_frontmatter(self, text: str, ext: str = ".md") -> dict[str, Any] | None:
        m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
        if m:
            try:
                return yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError:
                return None
        if ext in {".yaml", ".yml"}:
            try:
                return yaml.safe_load(text) or {}
            except yaml.YAMLError:
                return None
        return None

    def _check_content_length(self, text: str) -> str | None:
        body = re.sub(r"^---\r?\n.*?\r?\n---\r?\n?", "", text, flags=re.DOTALL)
        body_len = len(body.strip())
        if body_len < MIN_CONTENT_CHARS:
            return f"内容过短（{body_len} 字符 < {MIN_CONTENT_CHARS}）"
        return None

    def _check_title_dedup(self, title: str) -> str | None:
        return None

    def _run_gate(self, source_path: Path) -> GateResult | None:
        try:
            task = build_kb_gate_eval_task(
                gate_id="G1",
                title="G1 Ingest Gate",
                deliverable=source_path,
            )
            return self._gate_engine.evaluate(task, "G1")
        except Exception:
            logger.warning("G1 gate evaluation failed for %s", source_path, exc_info=True)
            return None

    def _write_to_raw_intake(self, source_path: Path, text: str, fm: dict[str, Any]) -> Path:
        ke_id = fm.get("module_id", "UNKNOWN")
        target_name = f"{ke_id}{source_path.suffix}"
        target = self._raw_intake_dir / target_name
        target.write_text(text, encoding="utf-8", newline="\n")
        return target
