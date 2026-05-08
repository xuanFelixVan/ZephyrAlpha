"""Witness Isolation — v0.8.0 Witness隔离: N版本decision验证+投票机制+majority判定。"""
from __future__ import annotations

class WitnessIsolator:
    def __init__(self):
        self._witnesses:dict[str,str]={}

    def register_witness(self, witness_id:str, decision:str):
        self._witnesses[witness_id]=decision

    def majority_decision(self)->str:
        if not self._witnesses:return "no_decision"
        from collections import Counter
        counts=Counter(self._witnesses.values())
        total=len(self._witnesses)
        for decision,count in counts.most_common(1):
            if count>total/2:
                return decision
        return "no_consensus"

    def disagree_count(self)->int:
        from collections import Counter
        counts=Counter(self._witnesses.values())
        return len(self._witnesses)-max(counts.values())
