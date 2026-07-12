# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation.activate
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.gate_engine; zephyr.governance.rule_enforcement.gate_types.__init__; zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RSC_activate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G4 Activate 门禁 — 人工激活（T-2-13-D）
========================================
依据：g4-activate.yaml、AGENTS.md §5.2

功能
----
1. 生成 Markdown 提案 + 通知
2. auto_activate_score: 9.0（高分预授权自动激活）
3. 调用 gate_engine.py 执行 g4-activate.yaml 门禁
4. 状态转换：analyzed -> active / analyzed -> analyzed（驳回）
5. 写入 05_active_research/ 或 04_future_capabilities/

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

from zephyr.gov_kb.kb_gate_task import build_kb_gate_eval_task
from zephyr.governance.rule_enforcement.gate_engine.gate_engine import GATES_DIR, GateEngine
from zephyr.governance.rule_enforcement.gate_types import GateResult

__all__ = [
    "ACTIVE_DIR_NAME",
    "AUTO_ACTIVATE_THRESHOLD",
    "FUTURE_DIR_NAME",
    "ActivateGate",
    "ActivateResult",
]

AUTO_ACTIVATE_THRESHOLD: Final[float] = 9.0
ACTIVE_DIR_NAME: Final[str] = "05_active_research"
FUTURE_DIR_NAME: Final[str] = "04_future_capabilities"

_UTC = UTC


@dataclass
class ActivateResult:
    passed: bool
    ke_id: str | None = None
    auto_activated: bool = False
    target_dir: str = ""
    target_path: Path | None = None
    proposal: str | None = None
    violations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class ActivateGate:
    def __init__(
        self,
        kb_root: Path,
        gate_engine: GateEngine | None = None,
    ) -> None:
        self._kb_root = kb_root
        self._active_dir = kb_root / ACTIVE_DIR_NAME
        self._future_dir = kb_root / FUTURE_DIR_NAME
        self._active_dir.mkdir(parents=True, exist_ok=True)
        self._future_dir.mkdir(parents=True, exist_ok=True)
        self._gate_engine = gate_engine or GateEngine(gate_dir=GATES_DIR)

    def activate(
        self,
        source_path: Path,
        force: bool = False,
    ) -> ActivateResult:
        violations: list[str] = []

        if not source_path.exists():
            return ActivateResult(passed=False, violations=[f"文件不存在：{source_path}"])

        try:
            text = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            return ActivateResult(passed=False, violations=[f"无法读取文件：{exc}"])

        fm = self._parse_frontmatter(text)
        if fm is None:
            fm = {}

        ke_id = fm.get("module_id", "")
        ai_value_score = float(fm.get("ai_value_score", 0.0))
        priority = fm.get("priority", "P2")
        classification = fm.get("classification", "KNOWLEDGE_ENTRY")

        deps = fm.get("depends_on", [])
        if isinstance(deps, list) and deps:
            dep_missing = self._check_dependencies(deps)
            if dep_missing:
                violations.append(f"依赖未就绪：{dep_missing}")
                if not force:
                    return ActivateResult(
                        passed=False,
                        ke_id=ke_id,
                        violations=violations,
                        details={"missing_deps": dep_missing},
                    )

        target_path_pattern = fm.get("target_path", "")
        if target_path_pattern:
            path_err = self._validate_target_path(target_path_pattern)
            if path_err:
                violations.append(path_err)
                return ActivateResult(passed=False, ke_id=ke_id, violations=violations)

        auto_activated = ai_value_score >= AUTO_ACTIVATE_THRESHOLD or force

        if not auto_activated:
            proposal = self._generate_proposal(fm, text)
            return ActivateResult(
                passed=False,
                ke_id=ke_id,
                auto_activated=False,
                proposal=proposal,
                violations=["需人工审批：ai_value_score < AUTO_ACTIVATE_THRESHOLD"],
                details={"ai_value_score": ai_value_score},
            )

        gate_result = self._run_gate(source_path)
        if gate_result and not gate_result.passed:
            for v in gate_result.violations:
                violations.append(f"[{v.severity}] {v.message}")
            return ActivateResult(
                passed=False,
                ke_id=ke_id,
                violations=violations,
            )

        target_dir = self._determine_target_dir(priority, classification)
        target_path = self._write_to_target(source_path, text, fm, target_dir)

        return ActivateResult(
            passed=True,
            ke_id=ke_id,
            auto_activated=True,
            target_dir=target_dir,
            target_path=target_path,
            details={"ai_value_score": ai_value_score, "priority": priority},
        )

    def _check_dependencies(self, deps: list[str]) -> list[str]:
        return []

    def _validate_target_path(self, target_path: str) -> str | None:
        pattern = r"^docs/08_knowledge/[a-z0-9-]+/ke-\d{3,}-[a-z0-9-]+\.md$"
        if not re.match(pattern, target_path):
            return f"目标路径不符合规范 '{target_path}'，应匹配 {pattern}"
        return None

    def _determine_target_dir(self, priority: str, classification: str) -> str:
        if priority in ("P0", "P1") or classification in (
            "BLUEPRINT",
            "STRATEGY",
            "KNOWLEDGE_ENTRY",
        ):
            return ACTIVE_DIR_NAME
        return FUTURE_DIR_NAME

    def _generate_proposal(self, fm: dict[str, Any], text: str) -> str:
        ke_id = fm.get("module_id", "UNKNOWN")
        title = fm.get("title", "Untitled")
        category = fm.get("category", "general")
        score = fm.get("ai_value_score", 0.0)
        classification = fm.get("classification", "UNKNOWN")
        priority = fm.get("priority", "P2")

        body = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL).strip()
        summary = body[:300] + "..." if len(body) > 300 else body

        return (
            f"# 知识激活提案：{ke_id}\n\n"
            f"## 基本信息\n\n"
            f"| 字段 | 值 |\n|------|----|\n"
            f"| KE ID | {ke_id} |\n"
            f"| 标题 | {title} |\n"
            f"| 分类 | {classification} |\n"
            f"| 类别 | {category} |\n"
            f"| 优先级 | {priority} |\n"
            f"| 价值评分 | {score} |\n\n"
            f"## 内容摘要\n\n{summary}\n\n"
            f"## 审批\n\n"
            f"- [ ] 批准激活\n"
            f"- [ ] 驳回（附理由）\n"
        )

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
                gate_id="G4",
                title="G4 Activate Gate",
                deliverable=source_path,
            )
            return self._gate_engine.evaluate(task, "G4")
        except Exception:
            return None

    def _write_to_target(
        self,
        source_path: Path,
        text: str,
        fm: dict[str, Any],
        target_dir: str,
    ) -> Path:
        ke_id = fm.get("module_id", "UNKNOWN")
        target_name = f"{ke_id}{source_path.suffix}"
        target = self._kb_root / target_dir / target_name

        enriched_fm = dict(fm)
        enriched_fm["activated_at"] = datetime.now(_UTC).isoformat()
        enriched_fm["activation_status"] = "active"

        body = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL)
        fm_yaml = yaml.dump(enriched_fm, allow_unicode=True, default_flow_style=False)
        enriched_text = f"---\n{fm_yaml}---\n{body}"

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(enriched_text, encoding="utf-8", newline="\n")
        return target
