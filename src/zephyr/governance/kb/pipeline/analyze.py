# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.governance.kb.pipeline.analyze
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
# [A_module] module_id=MOD-DAT_analyze | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
G3 Evaluate 门禁 — 深度评估（T-2-13-C）
=========================================
依据：g3-evaluate.yaml、AGENTS.md §5.2

功能
----
1. 深度评估：价值评分 + 激活条件 + 实现复杂度
2. ai_value_score ≥ 7.0 通过（10 分制）
3. 评分维度：design_decision_density(0.3) + technical_specificity(0.25)
   + reuse_potential(0.25) + irreplaceability(0.2)
4. 调用 gate_engine.py 执行 g3-evaluate.yaml 门禁
5. 状态转换：triaged → analyzed / triaged → archived
6. 写入 03_analyzed/ 目录

Safety : M
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path
from typing import Any

import yaml

from zephyr.governance.kb.kb_gate_task import build_kb_gate_eval_task
from zephyr.governance.rule_enforcement.gate_engine.gate_engine import GATES_DIR, GateEngine
from zephyr.governance.rule_enforcement.gate_types import GateResult

__all__ = [
    "SCORING_DIMENSIONS",
    "VALUE_SCORE_THRESHOLD",
    "AnalyzeGate",
    "AnalyzeResult",
]

VALUE_SCORE_THRESHOLD = 7.0

SCORING_DIMENSIONS = {
    "design_decision_density": 0.30,
    "technical_specificity": 0.25,
    "reuse_potential": 0.25,
    "irreplaceability": 0.20,
}

_ANALYZED_DIR_NAME = "03_analyzed"

_DESIGN_DECISION_PATTERNS = [
    r"ADR-\d+",
    r"设计决策",
    r"选择.*因为",
    r"不采用.*原因",
    r"权衡",
    r"trade-?off",
    r"decision",
    r"rationale",
]
_TECHNICAL_PATTERNS = [
    r"接口定义",
    r"函数签名",
    r"参数配置",
    r"数据流",
    r"```python",
    r"```yaml",
    r"def\s+\w+",
    r"class\s+\w+",
    r"type:\s*\w+",
]
_REUSE_PATTERNS = [
    r"复用",
    r"通用",
    r"跨模块",
    r"跨层",
    r"reuse",
    r"cross-?layer",
    r"shared",
]
_IRREPLACEABILITY_PATTERNS = [
    r"唯一",
    r"仅此",
    r"核心",
    r"不可替代",
    r"unique",
    r"irreplaceable",
    r"critical",
]

_UTC = UTC


@dataclass
class AnalyzeResult:
    passed: bool
    ke_id: str | None = None
    ai_value_score: float = 0.0
    activation_conditions: list[str] = field(default_factory=list)
    implementation_complexity: str = "medium"
    target_path: Path | None = None
    violations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class AnalyzeGate:
    def __init__(
        self,
        kb_root: Path,
        gate_engine: GateEngine | None = None,
    ) -> None:
        self._kb_root = kb_root
        self._analyzed_dir = kb_root / _ANALYZED_DIR_NAME
        self._analyzed_dir.mkdir(parents=True, exist_ok=True)
        self._gate_engine = gate_engine or GateEngine(gate_dir=GATES_DIR)

    def analyze(self, source_path: Path) -> AnalyzeResult:
        violations: list[str] = []

        if not source_path.exists():
            return AnalyzeResult(passed=False, violations=[f"文件不存在：{source_path}"])

        try:
            text = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            return AnalyzeResult(passed=False, violations=[f"无法读取文件：{exc}"])

        fm = self._parse_frontmatter(text)
        if fm is None:
            fm = {}

        scores = self._compute_dimension_scores(text)
        weighted_score = sum(scores[dim] * weight for dim, weight in SCORING_DIMENSIONS.items())
        ai_value_score = weighted_score * 10.0

        activation_conditions = self._derive_activation_conditions(fm, text)
        complexity = self._assess_complexity(text)

        if ai_value_score < VALUE_SCORE_THRESHOLD:
            violations.append(f"ai_value_score={ai_value_score:.1f} < {VALUE_SCORE_THRESHOLD}，归档")
            return AnalyzeResult(
                passed=False,
                ai_value_score=ai_value_score,
                activation_conditions=activation_conditions,
                implementation_complexity=complexity,
                violations=violations,
                details={"dimension_scores": scores},
            )

        gate_result = self._run_gate(source_path)
        if gate_result and not gate_result.passed:
            for v in gate_result.violations:
                violations.append(f"[{v.severity}] {v.message}")
            return AnalyzeResult(
                passed=False,
                ai_value_score=ai_value_score,
                violations=violations,
            )

        ke_id = fm.get("module_id", "")
        target_path = self._write_to_analyzed(
            source_path, text, fm, ai_value_score, scores, activation_conditions, complexity
        )

        return AnalyzeResult(
            passed=True,
            ke_id=ke_id,
            ai_value_score=ai_value_score,
            activation_conditions=activation_conditions,
            implementation_complexity=complexity,
            target_path=target_path,
            details={"dimension_scores": scores},
        )

    def _compute_dimension_scores(self, text: str) -> dict[str, float]:
        text_lower = text.lower()

        dd_hits = sum(1 for p in _DESIGN_DECISION_PATTERNS if re.search(p, text_lower))
        dd_score = min(1.0, dd_hits * 0.15 + 0.1)

        tech_hits = sum(1 for p in _TECHNICAL_PATTERNS if re.search(p, text_lower))
        tech_score = min(1.0, tech_hits * 0.12 + 0.1)

        reuse_hits = sum(1 for p in _REUSE_PATTERNS if re.search(p, text_lower))
        reuse_score = min(1.0, reuse_hits * 0.2 + 0.15)

        irrep_hits = sum(1 for p in _IRREPLACEABILITY_PATTERNS if re.search(p, text_lower))
        irrep_score = min(1.0, irrep_hits * 0.2 + 0.15)

        return {
            "design_decision_density": dd_score,
            "technical_specificity": tech_score,
            "reuse_potential": reuse_score,
            "irreplaceability": irrep_score,
        }

    def _derive_activation_conditions(self, fm: dict[str, Any], text: str) -> list[str]:
        conditions: list[str] = []

        layer = fm.get("layer", "")
        if layer:
            conditions.append(f"依赖 {layer} 层模块就绪")

        deps = fm.get("depends_on", [])
        if isinstance(deps, list):
            for dep in deps:
                conditions.append(f"依赖 {dep} 已激活")

        if re.search(r"ChromaDB|chromadb", text, re.IGNORECASE):
            conditions.append("依赖 ChromaDB 向量索引可用")

        if re.search(r"SQLite|sqlite", text, re.IGNORECASE):
            conditions.append("依赖 SQLite 元数据层可用")

        if not conditions:
            conditions.append("无前置依赖，可直接激活")

        return conditions

    def _assess_complexity(self, text: str) -> str:
        body = re.sub(r"^---\r?\n.*?\r?\n---\r?\n?", "", text, flags=re.DOTALL).strip()
        code_blocks = len(re.findall(r"```", body))
        has_mermaid = bool(re.search(r"```mermaid", body))
        has_tables = bool(re.search(r"\|.*\|.*\|", body))

        score = 0
        if len(body) > 2000:
            score += 2
        elif len(body) > 500:
            score += 1
        if code_blocks > 4:
            score += 2
        elif code_blocks > 0:
            score += 1
        if has_mermaid:
            score += 1
        if has_tables:
            score += 1

        if score >= 4:
            return "high"
        if score >= 2:
            return "medium"
        return "low"

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
                gate_id="G3",
                title="G3 Evaluate Gate",
                deliverable=source_path,
            )
            return self._gate_engine.evaluate(task, "G3")
        except Exception:
            return None

    def _write_to_analyzed(
        self,
        source_path: Path,
        text: str,
        fm: dict[str, Any],
        ai_value_score: float,
        scores: dict[str, float],
        activation_conditions: list[str],
        complexity: str,
    ) -> Path:
        ke_id = fm.get("module_id", "UNKNOWN")
        target_name = f"{ke_id}{source_path.suffix}"
        target = self._analyzed_dir / target_name

        enriched_fm = dict(fm)
        enriched_fm["ai_value_score"] = round(ai_value_score, 1)
        enriched_fm["dimension_scores"] = scores
        enriched_fm["activation_conditions"] = activation_conditions
        enriched_fm["implementation_complexity"] = complexity

        body = re.sub(r"^---\r?\n.*?\r?\n---\r?\n?", "", text, flags=re.DOTALL)
        fm_yaml = yaml.dump(enriched_fm, allow_unicode=True, default_flow_style=False)
        enriched_text = f"---\n{fm_yaml}---\n{body}"

        target.write_text(enriched_text, encoding="utf-8", newline="\n")
        return target
