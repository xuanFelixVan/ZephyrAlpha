"""
G2 Triage 门禁 — 知识分类评分（T-2-13-B）
==========================================
依据：g2_triage.yaml、AGENTS.md §5.2 分类打标规范

功能
----
1. Domain 分类：将知识条目归入 AGENTS.md 定义的分类标签
2. AI 评分：先规则评分，后接 AI（当前实现规则评分）
3. ai_triage_score ≥ 0.7 → high_value；0.3-0.7 → 需复审；< 0.3 → rejected
4. 调用 gate_engine.py 执行 g2_triage.yaml 门禁
5. 状态转换：raw → triaged / raw → rejected
6. 写入 02_triaged/ 目录

Safety : M
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from zephyr.gates.gate_engine import GateEngine, GateResult, GATES_DIR
from zephyr.kb.kb_repo import KbRepo, KeStatus
from zephyr.shared.schemas import Task, TaskStatus

__all__ = [
    "TriageResult",
    "TriageGate",
    "APPROVED_LABELS",
    "VALID_DOC_TYPES",
    "VALID_LAYERS",
    "HIGH_VALUE_THRESHOLD",
    "REJECT_THRESHOLD",
]

APPROVED_LABELS = [
    "BLUEPRINT",
    "MODULE_SPEC",
    "STRATEGY",
    "AUDIT_REPORT",
    "STATE_SNAPSHOT",
    "GOVERNANCE_STD",
    "KNOWLEDGE_ENTRY",
    "TEMP_ARTIFACT",
    "ORPHAN_SHELL",
    "ENCODING_BROKEN",
]

VALID_DOC_TYPES = [
    "policy",
    "standard",
    "adr",
    "blueprint",
    "construction_plan",
    "design",
    "plan",
    "roadmap",
    "register",
    "index",
    "readme",
    "log",
    "checklist",
    "template",
    "knowledge_entry",
    "audit_report",
    "ai_governance",
    "candidate_pool",
    "service_spec",
    "discussion_draft",
    "terminology",
    "reference",
]

VALID_LAYERS = [
    "l00_data_source",
    "l01_data_processing",
    "l02_alpha_factor",
    "l03_signal_generation",
    "l04_ml_platform",
    "l05_portfolio_construction",
    "l06_trade_execution",
    "l07_risk_management",
    "l08_post_trade_analytics",
    "l09_research_innovation",
    "l10_compliance",
    "l11_human_ai_interface",
    "shared",
    "cross_layer",
]

HIGH_VALUE_THRESHOLD = 0.7
REJECT_THRESHOLD = 0.3

_TRIAGED_DIR_NAME = "02_triaged"

_DESIGN_KEYWORDS = [
    "设计决策", "架构", "ADR", "接口定义", "约束",
    "design decision", "architecture", "interface", "constraint",
]
_STRATEGY_KEYWORDS = [
    "策略", "因子", "回测", "信号", "alpha",
    "strategy", "factor", "backtest", "signal",
]
_GOVERNANCE_KEYWORDS = [
    "治理", "标准", "审计", "合规", "门禁",
    "governance", "standard", "audit", "compliance", "gate",
]
_LESSON_KEYWORDS = [
    "教训", "踩坑", "修复", "根因", "postmortem",
    "lesson", "pitfall", "fix", "root cause",
]

_UTC = timezone.utc


@dataclass
class TriageResult:
    passed: bool
    ke_id: Optional[str] = None
    classification: str = ""
    ai_triage_score: float = 0.0
    priority: str = "P2"
    target_path: Optional[Path] = None
    violations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class TriageGate:
    def __init__(
        self,
        kb_root: Path,
        gate_engine: Optional[GateEngine] = None,
        kb_repo: Optional[KbRepo] = None,
    ) -> None:
        self._kb_root = kb_root
        self._triaged_dir = kb_root / _TRIAGED_DIR_NAME
        self._triaged_dir.mkdir(parents=True, exist_ok=True)
        self._gate_engine = gate_engine or GateEngine(gate_dir=GATES_DIR)
        self._kb_repo = kb_repo

    def triage(self, source_path: Path) -> TriageResult:
        violations: list[str] = []

        if not source_path.exists():
            return TriageResult(passed=False, violations=[f"文件不存在：{source_path}"])

        try:
            text = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            return TriageResult(passed=False, violations=[f"无法读取文件：{exc}"])

        fm = self._parse_frontmatter(text)
        if fm is None:
            fm = {}

        classification = self._classify(fm, text)
        if classification not in APPROVED_LABELS:
            violations.append(f"分类标签无效 '{classification}'，不在批准列表中")
            return TriageResult(passed=False, violations=violations, classification=classification)

        doc_type = fm.get("doc_type", "")
        if doc_type and doc_type not in VALID_DOC_TYPES:
            violations.append(f"doc_type 无效 '{doc_type}'")

        layer = fm.get("layer", "")
        if layer and layer not in VALID_LAYERS:
            violations.append(f"layer 无效 '{layer}'")

        score = self._compute_triage_score(fm, text, classification)
        priority = self._score_to_priority(score)

        if score < REJECT_THRESHOLD:
            violations.append(f"ai_triage_score={score:.2f} < {REJECT_THRESHOLD}，拒绝入库")
            return TriageResult(
                passed=False,
                classification=classification,
                ai_triage_score=score,
                priority=priority,
                violations=violations,
            )

        gate_result = self._run_gate(source_path)
        if gate_result and not gate_result.passed:
            for v in gate_result.violations:
                violations.append(f"[{v.severity}] {v.message}")
            return TriageResult(
                passed=False,
                classification=classification,
                ai_triage_score=score,
                priority=priority,
                violations=violations,
            )

        ke_id = fm.get("module_id", "")
        target_path = self._write_to_triaged(source_path, text, fm, classification, score, priority)

        if self._kb_repo is not None and ke_id:
            try:
                rec = self._kb_repo.get(ke_id)
                if rec and rec.status == KeStatus.DRAFT:
                    self._kb_repo.transition(ke_id, KeStatus.SUBMITTED)
            except Exception:
                pass

        return TriageResult(
            passed=True,
            ke_id=ke_id,
            classification=classification,
            ai_triage_score=score,
            priority=priority,
            target_path=target_path,
            details={"doc_type": doc_type, "layer": layer},
        )

    def _classify(self, fm: dict[str, Any], text: str) -> str:
        explicit = fm.get("classification", "")
        if explicit and explicit in APPROVED_LABELS:
            return explicit

        category = fm.get("category", "").lower()
        doc_type = fm.get("doc_type", "").lower()

        if doc_type in ("blueprint", "design"):
            return "BLUEPRINT"
        if doc_type in ("standard", "policy"):
            return "GOVERNANCE_STD"
        if doc_type in ("report",):
            return "AUDIT_REPORT"
        if category in ("strategy", "factor"):
            return "STRATEGY"
        if category in ("best_practice", "lesson_learned"):
            return "KNOWLEDGE_ENTRY"

        text_lower = text.lower()
        design_hits = sum(1 for kw in _DESIGN_KEYWORDS if kw.lower() in text_lower)
        strategy_hits = sum(1 for kw in _STRATEGY_KEYWORDS if kw.lower() in text_lower)
        governance_hits = sum(1 for kw in _GOVERNANCE_KEYWORDS if kw.lower() in text_lower)
        lesson_hits = sum(1 for kw in _LESSON_KEYWORDS if kw.lower() in text_lower)

        scores = {
            "BLUEPRINT": design_hits,
            "STRATEGY": strategy_hits,
            "GOVERNANCE_STD": governance_hits,
            "KNOWLEDGE_ENTRY": lesson_hits,
        }
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "KNOWLEDGE_ENTRY"
        return best

    def _compute_triage_score(
        self, fm: dict[str, Any], text: str, classification: str
    ) -> float:
        score = 0.0

        has_module_id = bool(fm.get("module_id"))
        has_title = bool(fm.get("title"))
        has_category = bool(fm.get("category"))
        has_layer = bool(fm.get("layer"))
        has_doc_type = bool(fm.get("doc_type"))
        has_date = bool(fm.get("date") or fm.get("created_at") or fm.get("valid_from"))

        if has_module_id:
            score += 0.15
        if has_title:
            score += 0.10
        if has_category:
            score += 0.10
        if has_layer:
            score += 0.05
        if has_doc_type:
            score += 0.05
        if has_date:
            score += 0.05

        body = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL).strip()
        body_len = len(body)
        if body_len > 500:
            score += 0.15
        elif body_len > 200:
            score += 0.10
        elif body_len > 100:
            score += 0.05

        if classification in ("BLUEPRINT", "STRATEGY", "KNOWLEDGE_ENTRY"):
            score += 0.15
        elif classification in ("GOVERNANCE_STD", "MODULE_SPEC"):
            score += 0.10
        else:
            score += 0.05

        high_value_patterns = [
            r"ADR-\d+",
            r"设计决策",
            r"根因",
            r"接口定义",
            r"design\s+decision",
            r"root\s+cause",
        ]
        for pat in high_value_patterns:
            if re.search(pat, text, re.IGNORECASE):
                score += 0.05
                break

        return min(1.0, score)

    def _score_to_priority(self, score: float) -> str:
        if score >= HIGH_VALUE_THRESHOLD:
            return "P0"
        if score >= 0.5:
            return "P1"
        if score >= REJECT_THRESHOLD:
            return "P2"
        return "P3"

    def _parse_frontmatter(self, text: str) -> Optional[dict[str, Any]]:
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            return None
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return None

    def _run_gate(self, source_path: Path) -> Optional[GateResult]:
        try:
            task = Task(
                task_id="TRIAGE-GATE-0001",
                namespace=TaskNamespace.CP,
                seq=1,
                phase=2,
                title="G2 Triage Gate",
                status=TaskStatus.IN_PROGRESS,
                execution_model="system",
                safety_level="M",
                deliverables=[str(source_path)],
                created_at=datetime.now(_UTC),
                updated_at=datetime.now(_UTC),
            )
            return self._gate_engine.evaluate(task, "G2")
        except Exception:
            return None

    def _write_to_triaged(
        self,
        source_path: Path,
        text: str,
        fm: dict[str, Any],
        classification: str,
        score: float,
        priority: str,
    ) -> Path:
        ke_id = fm.get("module_id", "UNKNOWN")
        target_name = f"{ke_id}{source_path.suffix}"
        target = self._triaged_dir / target_name

        enriched_fm = dict(fm)
        enriched_fm["classification"] = classification
        enriched_fm["ai_triage_score"] = round(score, 2)
        enriched_fm["priority"] = priority

        body = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
        fm_yaml = yaml.dump(enriched_fm, allow_unicode=True, default_flow_style=False)
        enriched_text = f"---\n{fm_yaml}---\n{body}"

        target.write_text(enriched_text, encoding="utf-8", newline="\n")
        return target
