# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.config_scanner

# [INVARIANTS] AI配置注入扫描不可禁用;恶意配置必须检测

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Config Scanner — v0.9.0 AI配置文件注入扫描器: 检测AI修改的配置+注入攻击。
"""
from __future__ import annotations

class ConfigScanner:
    def __init__(self):
        self._baseline:dict[str,str]={}

    def set_baseline(self, filepath:str, content_hash:str):
        self._baseline[filepath]=content_hash

    def detect_modification(self, filepath:str, current_hash:str)->bool:
        baseline=self._baseline.get(filepath)
        return baseline is not None and baseline!=current_hash

    def check_injection(self, content:str)->list[str]:
        suspicious=[]
        if "{{" in content and "}}" in content:suspicious.append("template_injection")
        if "eval(" in content:suspicious.append("code_injection")
        return suspicious
