"""Cross-Assistant Adapter — v0.6.0 Trae/Cursor/Windsurf/Codex/Wedata统一升级接口。"""
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
