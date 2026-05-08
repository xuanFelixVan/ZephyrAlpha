"""Objective Tracker — v0.9.0 目标漂移检测器: agent目标函数稳定性+变更检测+rollback。"""
from __future__ import annotations

class ObjectiveTracker:
    def __init__(self):
        self._objectives:dict[str,list[str]]={}
        self._versions:dict[str,int]={}

    def set_objective(self, agent_id:str, objective:str):
        if agent_id not in self._objectives:
            self._objectives[agent_id]=[]
        self._objectives[agent_id].append(objective)
        self._versions[agent_id]=self._versions.get(agent_id,0)+1

    def detect_drift(self, agent_id:str)->bool:
        objs=self._objectives.get(agent_id,[])
        return len(objs)>1

    def rollback(self, agent_id:str)->str:
        objs=self._objectives.get(agent_id,[])
        if len(objs)>=2:
            objs.pop()
            self._versions[agent_id]=max(0,self._versions.get(agent_id,1)-1)
        return objs[-1] if objs else ""
