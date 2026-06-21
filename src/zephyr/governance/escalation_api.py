# [A_module] module_id=MOD-RES_escalation_api | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [MODULE] zephyr.governance.escalation_api

# [INVARIANTS] 模块接口签名不可变

# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.infrastructure.escalation

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Escalation API — v0.6.0 Service Account API: 外部系统安全触发升级，不绕过引擎。
"""

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
