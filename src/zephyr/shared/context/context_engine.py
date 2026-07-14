# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.context.context_engine
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.__init__
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
# [A_module] module_id=MOD-INF_context_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Context Engine — AI 上下文组装与 Token 预算管理。

依据：
    蓝图 MOD-TASK_SYSTEM §2.2.1 + v0.3.0
    任务卡 TASK-INF-0006 + TASK-INF-0105

功能：
    - context_assembly: 根据 task_id 组装最小上下文
    - token_budget_tracker: 限制 context 不超过 max_tokens
    - pipeline M1-M11 集成验证
    - 支持 context_assembly_manifest 路径索引
"""

from __future__ import annotations

from typing import Final
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_MAX_TOKENS: Final[int] = 20000


@dataclass
class ContextSlice:
    file_path: str
    content: str
    token_estimate: int
    reason: str


@dataclass
class ContextAssembly:
    task_id: str
    slices: list[ContextSlice]
    total_tokens: int
    max_tokens: int
    budget_remaining: int
    truncated: bool = False


@dataclass
class TokenBudget:
    max_tokens: int
    used_tokens: int
    reserve_tokens: int
    over_budget: bool = False


class ContextEngine:
    CHARS_PER_TOKEN = 4

    def __init__(self, project_root: Path | None = None, max_tokens: int = DEFAULT_MAX_TOKENS) -> None:
        self._project_root = project_root or Path.cwd()
        self._max_tokens = max_tokens
        self._budget = TokenBudget(
            max_tokens=max_tokens,
            used_tokens=0,
            reserve_tokens=int(max_tokens * 0.1),
        )

    def assemble_context(
        self,
        task_id: str,
        manifest: list[dict[str, str]],
        truncate: bool = True,
    ) -> ContextAssembly:
        slices: list[ContextSlice] = []
        total_tokens = 0
        available = self._budget.max_tokens - self._budget.reserve_tokens

        # 5.106.5 修复: x.get("reason", "") 仅在 key 缺失时返回 default,
        # key 存在但值为 None 时 None 与 str 比较抛 TypeError。改为 `or ""` 兼容 None。
        sorted_manifest = sorted(manifest, key=lambda x: x.get("reason") or "")

        for entry in sorted_manifest:
            file_path = entry.get("file_path", "")
            reason = entry.get("reason", "")

            if not file_path:
                continue

            full_path = self._project_root / file_path
            content = ""
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8")

            token_estimate = len(content) // self.CHARS_PER_TOKEN

            if truncate and total_tokens + token_estimate > available:
                remaining = available - total_tokens
                if remaining > 100:
                    content = content[: remaining * self.CHARS_PER_TOKEN]
                    token_estimate = remaining
                else:
                    break

            total_tokens += token_estimate

            slices.append(
                ContextSlice(
                    file_path=file_path,
                    content=content,
                    token_estimate=token_estimate,
                    reason=reason,
                )
            )

        return ContextAssembly(
            task_id=task_id,
            slices=slices,
            total_tokens=total_tokens,
            max_tokens=self._budget.max_tokens,
            budget_remaining=self._budget.max_tokens - total_tokens,
            truncated=total_tokens > available,
        )

    def check_token_budget(self, content: str) -> TokenBudget:
        token_estimate = len(content) // self.CHARS_PER_TOKEN
        used = self._budget.used_tokens + token_estimate
        over = used > self._budget.max_tokens - self._budget.reserve_tokens

        return TokenBudget(
            max_tokens=self._budget.max_tokens,
            used_tokens=used,
            reserve_tokens=self._budget.reserve_tokens,
            over_budget=over,
        )

    def validate_pipeline_modules(self, module_names: list[str]) -> dict[str, bool]:
        pipeline_map = {
            "M1": "context_assembly",
            "M2": "task_parsing",
            "M3": "validation",
            "M4": "generation",
            "M5": "unit_testing",
            "M6": "integration_testing",
            "M7": "audit_and_coverage",
            "M8": "rollback_preparation",
            "M9": "governance_compliance",
            "M10": "artifact_collection",
            "M11": "journal_checkpoint",
        }

        return {name: name in pipeline_map for name in module_names}

    def estimate_task_tokens(self, task_card: dict[str, Any]) -> int:
        estimated = 0
        manifest = task_card.get("context_assembly_manifest", [])
        for entry in manifest:
            file_path = entry.get("file_path", "")
            full_path = self._project_root / file_path
            if full_path.exists():
                estimated += full_path.stat().st_size // self.CHARS_PER_TOKEN
        return estimated
