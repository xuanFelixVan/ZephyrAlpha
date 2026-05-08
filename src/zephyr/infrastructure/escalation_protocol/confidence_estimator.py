"""Confidence Estimator — D-022-05 置信度评估器: certainty×evidence×risk三维评估。"""
from __future__ import annotations

class ConfidenceLevel:
    HIGH="high"
    MEDIUM="medium"
    LOW="low"

class ConfidenceEstimator:
    def evaluate(self, certainty:float, evidence:float, risk:float)->str:
        score=certainty*0.4+evidence*0.35+(1.0-risk)*0.25
        if score>=0.7:return ConfidenceLevel.HIGH
        if score>=0.4:return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def should_auto_execute(self, certainty:float, evidence:float, risk:float)->bool:
        return self.evaluate(certainty,evidence,risk)==ConfidenceLevel.HIGH and risk<0.3
