# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.draft.draft_assistant
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Draft Assistant — 想法 -> MTH-012 蓝图骨架生成。

依据：
    蓝图 MOD-TASK_SYSTEM §13.3 路线图 #26 + v0.6.0
    任务卡 TASK-INF-0132 (Part 3/4)

功能：
    - 输入想法 -> MTH-012 格式蓝图骨架
    - 目标/边界/约束预填
    - Owner 填充 + 涌现式血肉补全

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 想法输入 DraftInput 数据类
#   fields: idea_text 想法原文、author 作者（默认AI_AGENT）、suggested_module/suggested_layer 可选建议
#   code: DraftInput L53-L58
# - id: I2
#   name: 草稿输出目录 output_dir 路径
#   fields: JSON 草稿落盘目录，默认 data/drafts
#   code: output_dir L62-L63
# 层: 算法
# - id: A1
#   name_zh: ① 模块与层推断
#   name_en: _infer_module/_infer_layer
#   intro: 用关键词表扫想法文本猜所属 MOD 模块，层优先取建议值
#   desc: suggested_module 非空直接用；否则 idea_text 转小写后按 rollback/task/blueprint/pipeline/decompose/lifecycle/gate 关键词表匹配 MOD-INF-021/MOD-TASK_SYSTEM/MOD-INF-005，全不命中回退 MOD-INF-TBD；layer 同理取建议或默认 infrastructure_runtime_integration
#   inputs: I1
#   outputs: module_id + layer 字符串
# - id: A2
#   name_zh: ② 目标边界约束预填
#   name_en: _extract_targets/_extract_boundaries/_extract_constraints
#   intro: 从想法里抽目标句子，边界与约束用内置模板预填
#   desc: targets：按 句号/分号/换行 切句，含 实现/建设/构建/develop/implement/build 关键词的句子截100字入选，至多5条，兜底取原文前100字；boundaries/constraints 返回固定四条模板（RULE-ZERO锁、原子写、单任务≤5文件、Python3.10+ 等）
#   inputs: I1
#   outputs: targets/boundaries/constraints 三列表
# - id: A3
#   name_zh: ③ 草稿组装与落盘
#   name_en: generate_draft/_save_draft
#   intro: 汇总推断结果成 BlueprintDraft，并以 JSON 写进草稿目录
#   desc: draft_id=DRAFT-yyyymmdd-HHMMSS UTC时间戳；idea_summary 截200字；组装 BlueprintDraft 后 _save_draft 建目录、写 {draft_id}.json（ensure_ascii=False indent=2）
#   inputs: I1 I2
#   outputs: BlueprintDraft + DRAFT-*.json 文件
# - id: A4
#   name_zh: ④ MTH-012骨架渲染
#   name_en: render_blueprint_skeleton
#   intro: 把草稿渲染成带 frontmatter 和固定章节的蓝图 Markdown 骨架
#   desc: 拼接 --- frontmatter（module_id/layer/version 0.1.0-draft/draft_id/generated_at）+ Idea Summary/Targets/Boundaries/Constraints 列表段 + 四条固定 TODO 勾选框，返回整段文本
#   inputs: I1
#   outputs: 蓝图骨架 Markdown 字符串
# 层: 输出
# - id: O1
#   name_zh: 蓝图草稿对象
#   name_en: BlueprintDraft
#   intro: generate_draft 返回的草稿数据类，含模块/层/目标/边界/约束，template_version 固定 MTH-012
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 草稿JSON与骨架Markdown
#   name_en: DRAFT-*.json/render_blueprint_skeleton
#   intro: 落盘的草稿 JSON 文件（data/drafts/）与待 Owner 补全血肉的可渲染蓝图骨架文本
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I1 --> A2
# A1 --> A3
# A2 --> A3
# I2 --> A3
# A3 --> A4
# A3 --> O1
# A3 --> O2
# A4 --> O2
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

    @property
    def output_dir(self):
        """只读：output_dir（Stage 4 公共化）。"""
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        """写入：output_dir（Stage 4 公共化）。"""
        self._output_dir = value

    def extract_targets(self, text) -> list[str]:
        """公共接口：extract_targets（Stage 4 公共化）。"""
        return self._extract_targets(text)

    def extract_constraints(self, text) -> list[str]:
        """公共接口：extract_constraints（Stage 4 公共化）。"""
        return self._extract_constraints(text)

    def extract_boundaries(self, text) -> list[str]:
        """公共接口：extract_boundaries（Stage 4 公共化）。"""
        return self._extract_boundaries(text)

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
