"""Hooks Integrity Guard — v0.11.0 Hooks自编辑防护器。"""
from __future__ import annotations

class HooksIntegrityGuard:
    def __init__(self):
        self._hooks_hashes:dict[str,str]={}

    def register(self, hook_path:str, hash_value:str):
        self._hooks_hashes[hook_path]=hash_value

    def verify(self, hook_path:str, current_hash:str)->bool:
        expected=self._hooks_hashes.get(hook_path)
        return expected is None or expected==current_hash
