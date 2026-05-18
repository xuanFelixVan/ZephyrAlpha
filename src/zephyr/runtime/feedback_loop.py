# [BLUEPRINT] MOD-INF-035 | 03_modules/_cross_layer/auto-runtime-core/blueprint.md | §

# [MODULE] zephyr.runtime.feedback_loop

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
FeedbackLoop — 反馈闭环
========================
蓝图: ARC-0001 §4.3 (三阶)
借鉴: K8s Controller 调和失败重试 + Magentic-One Progress Ledger
登记表裁定→规则进化
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG


class EvolutionProposal(BaseModel):
    model_config = BASE_CONFIG
    proposal_id: str = Field(default_factory=lambda: f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    source: str = ""
    pattern: str = ""
    suggested_rule_change: str = ""
    confidence: float = 0.0
    status: str = "DRAFT"


class FeedbackLoop:
    """反馈闭环——登记表裁定驱动规则进化。

    借鉴:
      - K8s Controller: 调和失败→调整→重试
      - LangGraph: Human-in-the-Loop 反馈注入
      - Magentic-One: Progress Ledger 自我反思
    """

    def __init__(self, proposal_dir: Path) -> None:
        self._proposal_dir = Path(proposal_dir)
        self._proposal_dir.mkdir(parents=True, exist_ok=True)

    def analyze_pending(self, pending_entries: list[dict[str, Any]]) -> list[EvolutionProposal]:
        proposals: list[EvolutionProposal] = []
        for entry in pending_entries:
            module = entry.get("module", "unknown")
            context = entry.get("context", "")
            proposals.append(EvolutionProposal(
                source=f"NSL-{entry.get('id', '?')}",
                pattern=f"Recurring ambiguity in {module}",
                suggested_rule_change=f"Add deterministic rule for {module}: {context[:80]}",
                confidence=0.6,
                status="DRAFT",
            ))
        return proposals

    def generate_proposals(self, pending_entries: list[dict[str, Any]]) -> list[EvolutionProposal]:
        return self.analyze_pending(pending_entries)

    def apply_proposal(self, proposal: EvolutionProposal) -> bool:
        path = self._proposal_dir / f"{proposal.proposal_id}.yaml"
        data = proposal.model_dump(mode="json")
        path.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding="utf-8")
        return True

    def review_proposals(self) -> list[EvolutionProposal]:
        results: list[EvolutionProposal] = []
        for path in self._proposal_dir.glob("PROP-*.yaml"):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                results.append(EvolutionProposal(**data))
            except Exception:
                continue
        return results
