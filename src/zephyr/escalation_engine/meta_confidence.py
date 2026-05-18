# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.meta_confidence

# [INVARIANTS] 元置信度评估不可跳过;自评偏差必须校准

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Meta-Confidence — D-022-10 Agent对自身判定置信度的自评+历史校准。
"""
from __future__ import annotations

class MetaConfidence:
    def __init__(self):
        self._history:list[tuple[float,float,bool]]=[]

    def self_assess(self, confidence:float, evidence_count:int, domain_familiarity:float)->float:
        ev_score=min(1.0,evidence_count/5.0)
        return confidence*0.5+ev_score*0.3+domain_familiarity*0.2

    def calibrate(self, predicted:float, actual_correct:bool):
        self._history.append((predicted,0.0,actual_correct))

    def calibration_error(self)->float:
        if not self._history:return 0.0
        return sum(abs(p-(1.0 if c else 0.0)) for p,_,c in self._history)/len(self._history)
