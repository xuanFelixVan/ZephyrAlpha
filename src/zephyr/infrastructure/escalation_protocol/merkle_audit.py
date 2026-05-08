"""Merkle Audit — v0.8.0 密码学审计追踪: escalation event Merkle树+不可篡改proof。"""
from __future__ import annotations
import hashlib,json

class MerkleTree:
    def __init__(self):
        self._leaves:list[bytes]=[]

    def add_event(self, event:dict)->None:
        self._leaves.append(hashlib.sha256(json.dumps(event,sort_keys=True).encode()).digest())

    def root_hash(self)->str:
        nodes=[h for h in self._leaves]
        while len(nodes)>1:
            if len(nodes)%2==1:nodes.append(nodes[-1])
            new_nodes=[hashlib.sha256(nodes[i]+nodes[i+1]).digest() for i in range(0,len(nodes),2)]
            nodes=new_nodes
        return nodes[0].hex() if nodes else "empty"

class MerkleAudit:
    def __init__(self):
        self._tree=MerkleTree()

    def record(self, escalation_event:dict)->str:
        self._tree.add_event(escalation_event)
        return self._tree.root_hash()

    def get_root(self)->str:
        return self._tree.root_hash()
