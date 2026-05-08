"""Meta-Confidence — D-022-10 Agent对自身判定置信度的自评+历史校准。"""
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
