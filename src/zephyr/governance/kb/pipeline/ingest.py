# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.data.knowledge_management.kb.pipeline.ingest
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
# [TTL] task_bound

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
8. 状态转换：draft → DRAFT(KeStatus) / draft → rejected
9. 写入 01_raw_intake/ 目录

Safety : M（治理层代码，门禁失败阻断入库）
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path
from typing import Any

import yaml

from zephyr.governance.kb.kb_gate_task import build_kb_gate_eval_task
from zephyr.governance.kb.kb_repo import KbRepo
from zephyr.governance.rule_enforcement.gate_engine import GATES_DIR, GateEngine
from zephyr.governance.rule_enforcement.gate_types import GateResult

__all__ = [
    "ALLOWED_EXTENSIONS",
    "BLACKLIST_PATTERNS",
    "MIN_CONTENT_CHARS",
    "REQUIRED_FRONTMATTER_FIELDS",
    "IngestGate",
    "IngestResult",
]

REQUIRED_FRONTMATTER_FIELDS = ["module_id", "title", "category", "ttl"]
ALLOWED_EXTENSIONS = {".md", ".yaml", ".yml"}
MIN_CONTENT_CHARS = 100

BLACKLIST_PATTERNS = [
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
        kb_repo: KbRepo | None = None,
    ) -> None:
        self._kb_root = kb_root
        self._raw_intake_dir = kb_root / _RAW_INTAKE_DIR_NAME
        self._raw_intake_dir.mkdir(parents=True, exist_ok=True)
        self._gate_engine = gate_engine or GateEngine(gate_dir=GATES_DIR)
        self._kb_repo = kb_repo

    def ingest(self, source_path: Path, content: str | None = None) -> Self:
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

        if self._kb_repo is not None and ke_id:
            try:
                self._kb_repo.create(
                    ke_id=ke_id,
                    title=title,
                    category=category,
                    source_file=str(source_path),
                    content=text,
                )
            except Exception:
                pass

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
        if not title or self._kb_repo is None:
            return None
        records = self._kb_repo.list_by_status()
        for rec in records:
            if rec.title == title:
                return f"Title 去重失败：'{title}' 已存在于 {rec.ke_id}"
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
            return None

    def _write_to_raw_intake(self, source_path: Path, text: str, fm: dict[str, Any]) -> Path:
        ke_id = fm.get("module_id", "UNKNOWN")
        target_name = f"{ke_id}{source_path.suffix}"
        target = self._raw_intake_dir / target_name
        target.write_text(text, encoding="utf-8", newline="\n")
        return target
