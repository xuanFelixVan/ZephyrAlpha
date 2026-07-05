# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/mcp-servers/blueprint.md
# [MODULE] zephyr.infrastructure.prompt_provider
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [A_module] module_id=MOD-INF_prompt_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MCP Prompt 模板提供者（MOD-INF-013 Phase 6 — 关闭 B3）。

为 BaseMCPServer 提供 prompts/list + prompts/get 原语支持。
注册至少 5 个模板。
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

__all__ = ["PromptDefinition", "PromptProvider"]


@dataclass
class PromptDefinition:
    name: str
    description: str
    arguments: list[dict[str, Any]] | None = None
    handler: Callable[..., str] | None = None


class PromptProvider:
    """MCP Prompt 模板注册与渲染统一接口。"""

    def __init__(self) -> None:
        self._prompts: dict[str, PromptDefinition] = {}
        self._register_default_prompts()

    def _register_default_prompts(self) -> None:
        self.register(
            name="code_review",
            description="代码审查模板——按 SOLID + blueprint compliance 维度检查",
            arguments=[
                {"name": "language", "description": "编程语言", "required": True},
                {"name": "context", "description": "审查上下文/模块名", "required": False},
            ],
            handler=self._code_review_template,
        )
        self.register(
            name="task_card_create",
            description="任务卡创建模板——从蓝图章节自动生成施工任务卡",
            arguments=[
                {"name": "blueprint_id", "description": "蓝图模块ID", "required": True},
                {"name": "section", "description": "目标章节", "required": True},
            ],
            handler=self._task_card_create_template,
        )
        self.register(
            name="blueprint_decompose",
            description="蓝图分解模板——将蓝图按小节拆解为独立任务卡映射",
            arguments=[
                {"name": "blueprint_id", "description": "蓝图模块ID", "required": True},
            ],
            handler=self._blueprint_decompose_template,
        )
        self.register(
            name="test_generation",
            description="测试生成模板——从 tool contract 自动生成 pytest case",
            arguments=[
                {"name": "tool_name", "description": "目标 tool 名称", "required": True},
            ],
            handler=self._test_generation_template,
        )
        self.register(
            name="architecture_review",
            description="架构评审模板——DDD 限界上下文 + KBG 兼容性检查",
            arguments=[
                {"name": "module_id", "description": "模块ID", "required": True},
            ],
            handler=self._architecture_review_template,
        )

    def register(
        self,
        name: str,
        description: str,
        *,
        arguments: list[dict[str, Any]] | None = None,
        handler: Callable[..., str] | None = None,
    ) -> None:
        self._prompts[name] = PromptDefinition(
            name=name,
            description=description,
            arguments=arguments,
            handler=handler,
        )

    def list_prompts(self) -> list[dict[str, Any]]:
        return [
            {
                "name": p.name,
                "description": p.description,
                "arguments": p.arguments or [],
            }
            for p in self._prompts.values()
        ]

    def get(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any] | None:
        p = self._prompts.get(name)
        if p is None:
            return None
        text = ""
        if p.handler:
            text = p.handler(**{k: str(v) for k, v in (arguments or {}).items()})
        return {
            "description": p.description,
            "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
        }

    def _code_review_template(self, language: str, context: str = "") -> str:
        return (
            f"You are a {language} code reviewer. "
            f"Review the following code for SOLID violations, blueprint compliance, "
            f"and OWASP Top 10 vulnerabilities.{context and ' Context: ' + context}"
        )

    def _task_card_create_template(self, blueprint_id: str, section: str) -> str:
        return (
            f"Generate a TASK-{blueprint_id}-NNNN task card from blueprint "
            f"section {section}. Include: task_id, priority, estimated_effort, "
            f"dependencies, acceptance_criteria, and construction steps."
        )

    def _blueprint_decompose_template(self, blueprint_id: str) -> str:
        return (
            f"Decompose blueprint {blueprint_id} into individual task cards. "
            f"Each task card should map to one blueprint section. "
            f"Output a YAML mapping of sections → task cards."
        )

    def _test_generation_template(self, tool_name: str) -> str:
        return (
            f"Generate comprehensive pytest test cases for MCP tool '{tool_name}'. "
            f"Include: happy path, edge cases, error handling, and contract compliance checks."
        )

    def _architecture_review_template(self, module_id: str) -> str:
        return (
            f"Review the architecture of module {module_id}. "
            f"Check: DDD bounded context boundaries, KBG recording completeness, "
            f"cross-layer dependency compliance, and architectural fitness function scores."
        )
