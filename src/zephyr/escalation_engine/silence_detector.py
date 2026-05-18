# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.silence_detector

# [INVARIANTS] 静默窗口检测不可禁用;预期事件模型必须维护

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Silence Detector — v0.8.0 静默窗口检测器: agent无响应超时+heartbeat缺失检测。
"""
from __future__ import annotations
import time

class SilenceDetector:
    def __init__(self):
        self._last_activity:dict[str,float]={}
        self._timeout_s=1800

    def record_activity(self, agent_id:str):
        self._last_activity[agent_id]=time.time()

    def detect_silence(self)->list[str]:
        now=time.time()
        return [aid for aid,last in self._last_activity.items() if now-last>self._timeout_s]

    def is_silent(self, agent_id:str)->bool:
        last=self._last_activity.get(agent_id,0)
        return time.time()-last>self._timeout_s
