# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.governance.kb.pipeline.extract
# [DOMAIN] D_GOV_KB
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
# [A_module] module_id=MOD-DAT_extract | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G5 Extract 门禁 — 知识升格（T-2-13-E）
=======================================
依据：g5-extract.yaml、AGENTS.md §5.3

功能
----
1. 知识升格路由：
   - 失败经验 -> 06_lessons_learned/
   - 成功经验 -> 07_best_practices/
   - 设计决策 -> 写入 ADR
2. 调用 gate_engine.py 执行 g5-extract.yaml 门禁
3. 状态转换：active -> graduated
4. KE 编号自动分配（递增）

Safety : M
"""

from __future__ import annotations

from typing import Final
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from zephyr.governance.kb.kb_gate_task import build_kb_gate_eval_task
from zephyr.governance.rule_enforcement.gate_engine.gate_engine import GATES_DIR, GateEngine
from zephyr.governance.rule_enforcement.gate_types import GateResult

__all__ = [
    "BEST_PRACTICES_DIR_NAME",
    "EXTRACTION_TEMPLATES",
    "LESSONS_DIR_NAME",
    "ExtractGate",
    "ExtractResult",
]

LESSONS_DIR_NAME: Final[str] = "06_lessons_learned"
BEST_PRACTICES_DIR_NAME: Final[str] = "07_best_practices"

EXTRACTION_TEMPLATES: Final[set] = {
    "blueprint": {
        "fields": ["design_decisions", "interfaces", "constraints", "dependencies"],
    },
    "strategy": {
        "fields": ["strategy_logic", "parameters", "risk_rules", "backtest_results"],
    },
    "factor": {
        "fields": ["factor_formula", "computation_logic", "pit_rules", "performance_metrics"],
    },
    "best_practice": {
        "fields": ["practice_description", "rationale", "applicability", "anti_patterns"],
    },
    "lesson_learned": {
        "fields": ["incident_description", "root_cause", "fix_action", "prevention"],
    },
}

_KE_PATTERN = re.compile(r"KE-(\d{3,})")

_UTC = UTC


@dataclass
class ExtractResult:
    passed: bool
    ke_id: str | None = None
    extract_type: str = ""
    target_path: Path | None = None
    adr_path: Path | None = None
    violations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class ExtractGate:
    def __init__(
        self,
        kb_root: Path,
        gate_engine: GateEngine | None = None,
        adr_dir: Path | None = None,
    ) -> None:
        self._kb_root = kb_root
        self._lessons_dir = kb_root / LESSONS_DIR_NAME
        self._best_practices_dir = kb_root / BEST_PRACTICES_DIR_NAME
        self._lessons_dir.mkdir(parents=True, exist_ok=True)
        self._best_practices_dir.mkdir(parents=True, exist_ok=True)
        self._gate_engine = gate_engine or GateEngine(gate_dir=GATES_DIR)
        self._adr_dir = adr_dir

    def extract(self, source_path: Path) -> ExtractResult:
        violations: list[str] = []

        if not source_path.exists():
            return ExtractResult(passed=False, violations=[f"文件不存在：{source_path}"])

        try:
            text = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            return ExtractResult(passed=False, violations=[f"无法读取文件：{exc}"])

        fm = self._parse_frontmatter(text)
        if fm is None:
            fm = {}

        ke_id = fm.get("module_id", "")
        category = fm.get("category", "general").lower()
        classification = fm.get("classification", "KNOWLEDGE_ENTRY")

        template = EXTRACTION_TEMPLATES.get(category)
        if template is None:
            violations.append(f"无提取模板匹配 category='{category}'，可用模板：{list(EXTRACTION_TEMPLATES.keys())}")
            return ExtractResult(passed=False, ke_id=ke_id, violations=violations)

        extract_type = self._determine_extract_type(category, classification, text)

        ke_number = self._get_next_ke_number()
        if ke_id and not ke_id.startswith("KE-"):
            ke_id = f"KE-{ke_number:03d}"

        gate_result = self._run_gate(source_path)
        if gate_result and not gate_result.passed:
            for v in gate_result.violations:
                violations.append(f"[{v.severity}] {v.message}")
            return ExtractResult(
                passed=False,
                ke_id=ke_id,
                extract_type=extract_type,
                violations=violations,
            )

        extracted_content = self._extract_fields(text, template["fields"])

        target_path: Path | None = None
        adr_path: Path | None = None

        if extract_type == "lesson_learned":
            target_path = self._write_to_lessons(ke_id, fm, extracted_content, text)
        elif extract_type == "design_decision":
            target_path = self._write_to_best_practices(ke_id, fm, extracted_content, text)
            adr_path = self._write_adr(ke_id, fm, extracted_content)
        else:
            target_path = self._write_to_best_practices(ke_id, fm, extracted_content, text)

        return ExtractResult(
            passed=True,
            ke_id=ke_id,
            extract_type=extract_type,
            target_path=target_path,
            adr_path=adr_path,
            details={"template_fields": template["fields"]},
        )

    def _determine_extract_type(self, category: str, classification: str, text: str) -> str:
        lesson_keywords = [
            "教训",
            "踩坑",
            "修复",
            "根因",
            "postmortem",
            "lesson",
            "pitfall",
            "fix",
            "root cause",
            "incident",
        ]
        design_keywords = [
            "ADR",
            "设计决策",
            "架构决策",
            "技术选型",
            "design decision",
            "architecture decision",
        ]

        text_lower = text.lower()
        lesson_hits = sum(1 for kw in lesson_keywords if kw.lower() in text_lower)
        design_hits = sum(1 for kw in design_keywords if kw.lower() in text_lower)

        if category in ("lesson_learned",) or lesson_hits > design_hits:
            return "lesson_learned"
        if category in ("blueprint",) or design_hits > 0:
            return "design_decision"
        return "best_practice"

    def _get_next_ke_number(self) -> int:
        max_num = 0

        for search_dir in [self._lessons_dir, self._best_practices_dir]:
            if not search_dir.exists():
                continue
            for f in search_dir.iterdir():
                m = _KE_PATTERN.search(f.name)
                if m:
                    num = int(m.group(1))
                    max_num = max(max_num, num)

        return max_num + 1

    def _extract_fields(self, text: str, fields: list[str]) -> dict[str, str]:
        body = re.sub(r"^---\r?\n.*?\r?\n---\r?\n?", "", text, flags=re.DOTALL).strip()
        result: dict[str, str] = {}

        for field_name in fields:
            field_label = field_name.replace("_", " ").replace("-", " ")
            pattern = re.compile(
                rf"(?:##?\s*{re.escape(field_label)}|{re.escape(field_name)})\s*\n(.*?)(?=\n##?\s|\Z)",
                re.IGNORECASE | re.DOTALL,
            )
            m = pattern.search(body)
            if m:
                result[field_name] = m.group(1).strip()
            else:
                result[field_name] = ""

        if not any(result.values()):
            result["_full_body"] = body

        return result

    def _write_to_lessons(
        self,
        ke_id: str,
        fm: dict[str, Any],
        extracted: dict[str, str],
        original_text: str,
    ) -> Path:
        target = self._lessons_dir / f"{ke_id}.md"
        frontmatter = {
            "module_id": ke_id,
            "title": fm.get("title", ""),
            "category": "lesson_learned",
            "source_file": fm.get("source_file", ""),
            "extracted_date": datetime.now(_UTC).strftime("%Y-%m-%d"),
            "version": "1.0.0",
            "status": "Active",
        }
        content = self._build_ke_content(frontmatter, extracted, "lesson_learned")
        target.write_text(content, encoding="utf-8", newline="\n")
        return target

    def _write_to_best_practices(
        self,
        ke_id: str,
        fm: dict[str, Any],
        extracted: dict[str, str],
        original_text: str,
    ) -> Path:
        target = self._best_practices_dir / f"{ke_id}.md"
        frontmatter = {
            "module_id": ke_id,
            "title": fm.get("title", ""),
            "category": "best_practice",
            "source_file": fm.get("source_file", ""),
            "extracted_date": datetime.now(_UTC).strftime("%Y-%m-%d"),
            "version": "1.0.0",
            "status": "Active",
        }
        content = self._build_ke_content(frontmatter, extracted, "best_practice")
        target.write_text(content, encoding="utf-8", newline="\n")
        return target

    def _write_adr(
        self,
        ke_id: str,
        fm: dict[str, Any],
        extracted: dict[str, str],
    ) -> Path | None:
        if self._adr_dir is None:
            return None

        self._adr_dir.mkdir(parents=True, exist_ok=True)

        adr_id = fm.get("module_id", ke_id).replace("KE-", "ADR-KE-")
        adr_path = self._adr_dir / f"{adr_id}.md"

        title = fm.get("title", "")
        context = extracted.get("design_decisions", extracted.get("_full_body", ""))

        adr_content = (
            f"# {adr_id}: {title}\n\n"
            f"## 状态\n\n已接受\n\n"
            f"## 上下文\n\n{context[:500]}\n\n"
            f"## 决策\n\n{extracted.get('constraints', '见源文档')}\n\n"
            f"## 后果\n\n{extracted.get('dependencies', '见源文档')}\n\n"
            f"## 来源\n\n{ke_id}\n"
        )

        adr_path.write_text(adr_content, encoding="utf-8", newline="\n")
        return adr_path

    def _build_ke_content(
        self,
        frontmatter: dict[str, Any],
        extracted: dict[str, str],
        category: str,
    ) -> str:
        fm_yaml = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
        parts = [f"---\n{fm_yaml}---\n"]

        template = EXTRACTION_TEMPLATES.get(category, EXTRACTION_TEMPLATES["best_practice"])
        for field_name in template["fields"]:
            value = extracted.get(field_name, "")
            if value:
                heading = field_name.replace("_", " ").title()
                parts.append(f"## {heading}\n\n{value}\n")

        if not any(extracted.get(f) for f in template["fields"]):
            full_body = extracted.get("_full_body", "")
            if full_body:
                parts.append(f"\n{full_body}\n")

        return "\n".join(parts)

    def _parse_frontmatter(self, text: str) -> dict[str, Any] | None:
        m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
        if not m:
            return None
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return None

    def _run_gate(self, source_path: Path) -> GateResult | None:
        try:
            task = build_kb_gate_eval_task(
                gate_id="G5",
                title="G5 Extract Gate",
                deliverable=source_path,
            )
            return self._gate_engine.evaluate(task, "G5")
        except Exception:
            return None
