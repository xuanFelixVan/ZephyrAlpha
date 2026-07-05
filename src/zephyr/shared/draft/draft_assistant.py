# [BLUEPRINT] SRC-093 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.draft.draft_assistant
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_draft_assistant | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Draft Assistant — 想法 → MTH-012 蓝图骨架生成。

依据：
    蓝图 MOD-TASK_SYSTEM §13.3 路线图 #26 + v0.6.0
    任务卡 TASK-INF-0132 (Part 3/4)

功能：
    - 输入想法 → MTH-012 格式蓝图骨架
    - 目标/边界/约束预填
    - Owner 填充 + 涌现式血肉补全
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class BlueprintDraft:
    draft_id: str
    idea_summary: str
    module_id: str
    layer: str
    targets: list[str]
    boundaries: list[str]
    constraints: list[str]
    generated_at: str
    template_version: str = "MTH-012"


@dataclass
class DraftInput:
    idea_text: str
    author: str = "AI_AGENT"
    suggested_module: str = ""
    suggested_layer: str = "infrastructure_runtime_integration"


class DraftAssistant:
    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or Path("data/drafts")

    def generate_draft(self, input_data: DraftInput) -> BlueprintDraft:
        module_id = self._infer_module(input_data)
        layer = self._infer_layer(input_data)
        targets = self._extract_targets(input_data.idea_text)
        boundaries = self._extract_boundaries(input_data.idea_text)
        constraints = self._extract_constraints(input_data.idea_text)

        draft = BlueprintDraft(
            draft_id=f"DRAFT-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            idea_summary=input_data.idea_text[:200],
            module_id=module_id,
            layer=layer,
            targets=targets,
            boundaries=boundaries,
            constraints=constraints,
            generated_at=datetime.now(UTC).isoformat(),
        )

        self._save_draft(draft)

        return draft

    def render_blueprint_skeleton(self, draft: BlueprintDraft) -> str:
        lines = [
            "---",
            f'module_id: "{draft.module_id}"',
            f'layer: "{draft.layer}"',
            'version: "0.1.0-draft"',
            f'draft_id: "{draft.draft_id}"',
            f'generated_at: "{draft.generated_at}"',
            "---",
            "",
            f"# {draft.module_id} — Blueprint Draft",
            "",
            "## Idea Summary",
            f"{draft.idea_summary}",
            "",
            "## Targets",
        ]
        for t in draft.targets:
            lines.append(f"- {t}")
        lines.append("")
        lines.append("## Boundaries")
        for b in draft.boundaries:
            lines.append(f"- {b}")
        lines.append("")
        lines.append("## Constraints")
        for c in draft.constraints:
            lines.append(f"- {c}")
        lines.append("")
        lines.append("## TODO")
        lines.append("- [ ] Owner review and fill details")
        lines.append("- [ ] Define data models")
        lines.append("- [ ] Define acceptance criteria")
        lines.append("- [ ] Create task cards")

        return "\n".join(lines)

    def _infer_module(self, input_data: DraftInput) -> str:
        if input_data.suggested_module:
            return input_data.suggested_module

        keywords = {
            "rollback": "MOD-INF-021",
            "task": "MOD-TASK_SYSTEM",
            "task-system": "MOD-TASK_SYSTEM",
            "blueprint": "MOD-TASK_SYSTEM",
            "pipeline": "MOD-INF-005",
            "decompose": "MOD-TASK_SYSTEM",
            "lifecycle": "MOD-TASK_SYSTEM",
            "gate": "MOD-TASK_SYSTEM",
        }

        text_lower = input_data.idea_text.lower()
        for keyword, module in keywords.items():
            if keyword in text_lower:
                return module

        return "MOD-INF-TBD"

    def _infer_layer(self, input_data: DraftInput) -> str:
        if input_data.suggested_layer:
            return input_data.suggested_layer
        return "infrastructure_runtime_integration"

    def _extract_targets(self, text: str) -> list[str]:
        targets: list[str] = []
        sentences = re.split(r"[.。;；\n]+", text)
        for sent in sentences:
            sent = sent.strip()
            if sent and any(kw in sent.lower() for kw in ["实现", "建设", "构建", "develop", "implement", "build"]):
                targets.append(sent[:100])
        if not targets:
            targets.append(text[:100])
        return targets[:5]

    def _extract_boundaries(self, text: str) -> list[str]:
        return [
            "Only create files, never delete",
            "Follow RULE-ZERO lock protocol",
            "All writes use atomic temp-file + os.replace()",
            "Maximum files per task: 5",
        ]

    def _extract_constraints(self, text: str) -> list[str]:
        return [
            "Python 3.10+",
            "UTF-8 encoding required",
            "Dataclass-based data models",
            "No external dependencies without blueprint approval",
        ]

    def _save_draft(self, draft: BlueprintDraft) -> None:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        draft_path = self._output_dir / f"{draft.draft_id}.json"
        draft_path.write_text(
            json.dumps(
                {
                    "draft_id": draft.draft_id,
                    "idea_summary": draft.idea_summary,
                    "module_id": draft.module_id,
                    "layer": draft.layer,
                    "targets": draft.targets,
                    "boundaries": draft.boundaries,
                    "constraints": draft.constraints,
                    "generated_at": draft.generated_at,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
