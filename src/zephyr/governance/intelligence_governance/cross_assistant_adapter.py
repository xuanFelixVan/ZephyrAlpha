# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.cross_assistant_adapter
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 跨助手适配必须统一接口;不可泄露助手间数据
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_cross_assistant_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Cross-Assistant Adapter — v0.6.0 Trae/Cursor/Windsurf/Codex/Wedata统一升级接口。
"""

from __future__ import annotations

from typing import Final
SUPPORTED_IDES: Final[list] = ["trae", "cursor", "windsurf", "codex", "wedata"]


class CrossAssistantAdapter:
    def __init__(self):
        self._adapters: dict[str, dict] = {}

    def register_adapter(self, ide_name: str, config: dict = None) -> bool:
        if ide_name not in SUPPORTED_IDES:
            return False
        self._adapters[ide_name] = config or {}
        return True

    def translate_request(self, ide_name: str, raw_request: dict) -> dict:
        if ide_name not in self._adapters:
            return {"error": "Unsupported IDE"}
        return {"ide": ide_name, "operation": raw_request.get("operation", ""), "normalized": True}

    def list_supported(self) -> list[str]:
        return SUPPORTED_IDES
