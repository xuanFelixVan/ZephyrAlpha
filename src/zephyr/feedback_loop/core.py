# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.feedback_loop.core
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS] zephyr.trading.auto_runtime_core; zephyr.trading.lifecycle_manager; zephyr.gov_audit.feedback_bridge; zephyr.security.access_control.orphan_judge.feedback_bridge
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
FeedbackLoop core — 反馈闭环核心类。

从 src/zephyr/trading/feedback_loop.py 迁入 src/zephyr/feedback_loop/ 包内，解决包/文件同名覆盖问题。
ARCH-032 迁移创建 feedback_loop/ 包后未删除旧 feedback_loop.py 文件，
导致 Python 包优先级覆盖文件，from zephyr.feedback_loop import FeedbackLoop 失败。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: proposal_dir 参数
#   fields: 参数 proposal_dir（无注解）
#   code: core.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FeedbackLoop
#   name_en: FeedbackLoop
#   intro: 反馈闭环——登记表裁定驱动规则进化。
#   desc: 反馈闭环——登记表裁定驱动规则进化。 借鉴: - K8s Controller: 调和失败->调整->重试 - LangGraph: Human-in-the-Loop 反馈注入…；公共方法（定义序）: analyze…
#   inputs: proposal_dir
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: FeedbackLoop
#   downstream: zephyr.trading.auto_runtime_core; zephyr.trading.lifecycle_manager; zephyr.gov_…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from zephyr.shared.io.serialization import filter_dataclass_fields
from zephyr.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import now_utc

__all__ = [
    "EvolutionProposal",
    "FeedbackLoop",
]


class EvolutionProposal(BaseModel):
    model_config = BASE_CONFIG
    proposal_id: str = Field(default_factory=lambda: f"PROP-{now_utc().strftime('%Y%m%d%H%M%S')}")
    source: str = ""
    pattern: str = ""
    suggested_rule_change: str = ""
    confidence: float = 0.0
    status: str = "DRAFT"


class FeedbackLoop:
    """反馈闭环——登记表裁定驱动规则进化。

    借鉴:
      - K8s Controller: 调和失败->调整->重试
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
            proposals.append(
                EvolutionProposal(
                    source=f"NSL-{entry.get('id', '?')}",
                    pattern=f"Recurring ambiguity in {module}",
                    suggested_rule_change=f"Add deterministic rule for {module}: {context[:80]}",
                    confidence=0.6,
                    status="DRAFT",
                )
            )
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
                results.append(EvolutionProposal(**filter_dataclass_fields(EvolutionProposal, data)))
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                continue
        return results
