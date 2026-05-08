"""Account Isolator — v0.10.0 多账户升级隔离器。"""
from __future__ import annotations

class AccountIsolator:
    def __init__(self):
        self._bindings:dict[str,str]={}

    def bind(self, account_id:str, escalation_policy:str):
        self._bindings[account_id]=escalation_policy

    def get_policy(self, account_id:str)->str:
        return self._bindings.get(account_id,"default_blocked")

    def isolate_account(self, account_id:str)->bool:
        return account_id in self._bindings
