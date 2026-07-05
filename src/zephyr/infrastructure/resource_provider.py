# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §[MODULE] zephyr.infrastructure.resource_provider
# [MODULE] zephyr.infrastructure.resource_provider
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.paths
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
# [A_module] module_id=MOD-INF_resource_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MCP Resource 提供者（MOD-INF-013 Phase 6 — 关闭 B2/B41）。

为 BaseMCPServer 提供 resources/list + resources/read 原语支持。
注册至少 3 类资源：蓝图/任务卡/测试报告。
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT

__all__ = ["ResourceDefinition", "ResourceProvider"]


@dataclass
class ResourceDefinition:
    uri: str
    name: str
    mime_type: str
    description: str = ""
    handler: Callable[[], str] | None = None


class ResourceProvider:
    """MCP Resource 注册与读取统一接口。

    BaseMCPServer 通过 resource_provider 属性挂载。
    """

    def __init__(self) -> None:
        self._resources: dict[str, ResourceDefinition] = {}
        self._register_default_resources()

    def _register_default_resources(self) -> None:
        self.register(
            uri="blueprint://MOD-INF-013",
            name="MCP Blueprint",
            mime_type="text/markdown",
            description="MOD-INF-013 MCP Servers blueprint",
            handler=self._blueprint_handler,
        )
        self.register(
            uri="blueprint://MOD-TASK_SYSTEM",
            name="TaskCard Blueprint",
            mime_type="text/markdown",
            description="MOD-TASK_SYSTEM TaskCard schema blueprint",
        )
        self.register(
            uri="blueprint://MOD-KB-001",
            name="KB Blueprint",
            mime_type="text/markdown",
            description="MOD-KB-001 Knowledge Base blueprint",
        )
        self.register(
            uri="task://INDEX",
            name="Task Index",
            mime_type="application/json",
            description="List of all registered TaskCards",
        )
        self.register(
            uri="report://INDEX",
            name="Test Report Index",
            mime_type="application/json",
            description="Aggregated test report summary",
        )

    def register(
        self,
        uri: str,
        name: str,
        mime_type: str,
        *,
        description: str = "",
        handler: Callable[[], str] | None = None,
    ) -> None:
        self._resources[uri] = ResourceDefinition(
            uri=uri,
            name=name,
            mime_type=mime_type,
            description=description,
            handler=handler,
        )

    def list_resources(self) -> list[dict[str, Any]]:
        return [
            {
                "uri": r.uri,
                "name": r.name,
                "mimeType": r.mime_type,
                "description": r.description,
            }
            for r in self._resources.values()
        ]

    def read(self, uri: str) -> dict[str, Any] | None:
        r = self._resources.get(uri)
        if r is None:
            return None
        contents: list[dict[str, Any]] = [{"uri": uri, "mimeType": r.mime_type}]
        if r.handler:
            contents[0]["text"] = r.handler()
        return {"contents": contents}

    def _blueprint_handler(self) -> str:
        path = REPO_ROOT / "docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return "# Blueprint not found"
