# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.governance.escalation.triage
# [DOMAIN] D_GOV_OPS_RESILIENCE
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
# [A_module] module_id=MOD-DAT_triage | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G2 Triage 门禁 — 知识分类评分（T-2-13-B）
==========================================
依据：g2-triage.yaml 分类打标规范

功能
----
1. Domain 分类：将知识条目归入 AGENTS.md 定义的分类标签
2. AI 评分：先规则评分，后接 AI（当前实现规则评分）
3. ai_triage_score ≥ 0.7 -> high_value；0.3-0.7 -> 需复审；< 0.3 -> rejected
4. 调用 gate_engine.py 执行 g2-triage.yaml 门禁
5. 状态转换：raw -> triaged / raw -> rejected
6. 写入 02_triaged/ 目录

Safety : M
"""

from __future__ import annotations

from typing import Final
import re
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path
from typing import Any

import yaml

from zephyr.governance.kb.ingest import COLLOQUIAL_PATTERNS
from zephyr.governance.kb.kb_gate_task import build_kb_gate_eval_task
from zephyr.governance.rule_enforcement.gate_engine.gate_engine import GATES_DIR, GateEngine
from zephyr.governance.rule_enforcement.gate_types import GateResult
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # 词表合法值加载 SSoT（D-D-05：禁止复制 _load_xxx()）

__all__ = [
    "APPROVED_LABELS",
    "HIGH_VALUE_THRESHOLD",
    "REJECT_THRESHOLD",
    "VALID_DOC_TYPES",
    "VALID_LAYERS",
    "TriageGate",
    "TriageResult",
]

APPROVED_LABELS: Final[list] = [
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

# 真源单一化：doc_type/layer 合法值由各自 vocabulary.yaml 唯一维护。
# 治本（P2-1，2026-06-30）：消除私有 _load_doc_type_values()/_load_layer_values()，
# 收敛到共享 SSoT load_vocabulary_values()（D-D-05 禁止跨脚本复制粘贴逻辑）。
# 词表改即生效，本模块不复制值名。返回 set[str]（消费者均用 in/set() 消费，类型安全）。
VALID_DOC_TYPES: Final[set[str]] = load_vocabulary_values("doc_type_vocabulary.yaml")
VALID_LAYERS: Final[set[str]] = load_vocabulary_values("layer_vocabulary.yaml")

HIGH_VALUE_THRESHOLD: Final[float] = 0.7
REJECT_THRESHOLD: Final[float] = 0.3

_TRIAGED_DIR_NAME = "02_triaged"

_DESIGN_KEYWORDS = [
    "设计决策",
    "架构",
    "接口定义",
    "约束",
    "design decision",
    "architecture",
    "interface",
    "constraint",
]
_STRATEGY_KEYWORDS = [
    "策略",
    "因子",
    "回测",
    "信号",
    "alpha",
    "strategy",
    "factor",
    "backtest",
    "signal",
]
_GOVERNANCE_KEYWORDS = [
    "治理",
    "标准",
    "审计",
    "合规",
    "门禁",
    "governance",
    "standard",
    "audit",
    "compliance",
    "gate",
]
_LESSON_KEYWORDS = [
    "教训",
    "踩坑",
    "修复",
    "根因",
    "postmortem",
    "lesson",
    "pitfall",
    "fix",
    "root cause",
]

_COLLOQUIAL_RES = [re.compile(p) for p in COLLOQUIAL_PATTERNS]

_UTC = UTC


@dataclass
class TriageResult:
    passed: bool
    ke_id: str | None = None
    classification: str = ""
    ai_triage_score: float = 0.0
    priority: str = "P2"
    target_path: Path | None = None
    violations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class TriageGate:
    def __init__(
        self,
        kb_root: Path,
        gate_engine: GateEngine | None = None,
    ) -> None:
        self._kb_root = kb_root
        self._triaged_dir = kb_root / _TRIAGED_DIR_NAME
        self._triaged_dir.mkdir(parents=True, exist_ok=True)
        self._gate_engine = gate_engine or GateEngine(gate_dir=GATES_DIR)

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

        # RENAME_REVIEW: 以下分支按值名分组——若词表改名（如 blueprint->xxx），
        # 需复核此分组映射。无法用词表属性（如 rule_form）替代，因为是业务分类逻辑。
        if doc_type == "blueprint":
            return "BLUEPRINT"
        if doc_type in ("policy",):
            return "GOVERNANCE_STD"
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

    def _compute_triage_score(self, fm: dict[str, Any], text: str, classification: str) -> float:
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

        colloquial_hits = sum(1 for cp in _COLLOQUIAL_RES if cp.search(text))
        if colloquial_hits > 0:
            score -= min(0.3, colloquial_hits * 0.1)

        return min(1.0, max(0.0, score))

    def _score_to_priority(self, score: float) -> str:
        if score >= HIGH_VALUE_THRESHOLD:
            return "P0"
        if score >= 0.5:
            return "P1"
        if score >= REJECT_THRESHOLD:
            return "P2"
        return "P3"

    def _parse_frontmatter(self, text: str) -> dict[str, Any] | None:
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            return None
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return None

    def _run_gate(self, source_path: Path) -> GateResult | None:
        try:
            task = build_kb_gate_eval_task(
                gate_id="G2",
                title="G2 Triage Gate",
                deliverable=source_path,
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
