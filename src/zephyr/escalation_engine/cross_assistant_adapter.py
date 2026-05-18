# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.cross_assistant_adapter

# [INVARIANTS] 跨助手适配必须统一接口;不可泄露助手间数据

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Cross-Assistant Adapter — v0.6.0 Trae/Cursor/Windsurf/Codex/Wedata统一升级接口。
"""
from __future__ import annotations

SUPPORTED_IDES=["trae","cursor","windsurf","codex","wedata"]

class CrossAssistantAdapter:
    def __init__(self):
        self._adapters:dict[str,dict]={}

    def register_adapter(self, ide_name:str, config:dict=None)->bool:
        if ide_name not in SUPPORTED_IDES:
            return False
        self._adapters[ide_name]=config or {}
        return True

    def translate_request(self, ide_name:str, raw_request:dict)->dict:
        if ide_name not in self._adapters:
            return {"error":"Unsupported IDE"}
        return {"ide":ide_name,"operation":raw_request.get("operation",""),"normalized":True}

    def list_supported(self)->list[str]:
        return SUPPORTED_IDES
