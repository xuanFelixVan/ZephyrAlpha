"""Escalation API — v0.6.0 Service Account API: 外部系统安全触发升级，不绕过引擎。"""
from __future__ import annotations
from typing import Any

class EscalationAPI:
    def __init__(self):
        self._api_keys:dict[str,str]={}

    def register_service(self, service_name:str, api_key:str):
        self._api_keys[service_name]=api_key

    def validate_request(self, service_name:str, api_key:str, operation:str)->tuple[bool,str]:
        expected=self._api_keys.get(service_name)
        if expected is None:
            return False,"Unknown service"
        if expected!=api_key:
            return False,"Invalid API key"
        return True,"OK"

    def trigger_escalation(self,service_name:str,api_key:str,operation:str,context:dict=None)->dict:
        ok,reason=self.validate_request(service_name,api_key,operation)
        if not ok:
            return {"status":"rejected","reason":reason}
        return {"status":"escalated","operation":operation,"service":service_name,"context":context or {}}
