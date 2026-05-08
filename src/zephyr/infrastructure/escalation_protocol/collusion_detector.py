"""Collusion Detector — v0.8.0 共谋检测器: agent-pair行为关联+时序聚类+异常协同检测。"""
from __future__ import annotations
import time

class CollusionDetector:
    def __init__(self):
        self._cooccurrence:dict[str,dict[str,int]]={}

    def record_interaction(self, agent_a:str, agent_b:str):
        self._cooccurrence.setdefault(agent_a,{}).setdefault(agent_b,0)
        self._cooccurrence[agent_a][agent_b]+=1

    def detect_suspicious_pair(self, threshold:int=10)->list[tuple[str,str]]:
        suspicious=[]
        for a,partners in self._cooccurrence.items():
            for b,count in partners.items():
                if count>threshold:
                    suspicious.append((a,b))
        return suspicious
