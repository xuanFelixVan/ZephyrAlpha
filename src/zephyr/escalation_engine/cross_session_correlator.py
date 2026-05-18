# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.cross_session_correlator

# [INVARIANTS] 跨会话关联必须执行;异常必须触发告警

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Cross-Session Correlator — v0.9.0 跨会话Coreset关联器: 多session行为模式+异常跨session模式检测。
"""
from __future__ import annotations
import math

class CrossSessionCorrelator:
    def __init__(self):
        self._sessions:dict[str,dict]={}

    def register_session(self, session_id:str, metrics:dict):
        self._sessions[session_id]=metrics

    def detect_anomalous_session(self, metrics:dict, std_dev_threshold:float=2.0)->bool:
        if len(self._sessions)<3:return False
        means={k:sum(s[k] for s in self._sessions.values())/len(self._sessions) for k in metrics}
        for k,v in metrics.items():
            mean=means.get(k,0)
            if mean>0 and abs(v-mean)/mean>std_dev_threshold:
                return True
        return False
