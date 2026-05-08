"""Integrity Verifier — v0.8.0 代码完整性验证器: hash校验+diff detection+rollback。"""
from __future__ import annotations
import hashlib

class IntegrityVerifier:
    def __init__(self):
        self._hashes:dict[str,str]={}

    def register_hash(self,filepath:str,content:str):
        self._hashes[filepath]=hashlib.sha256(content.encode()).hexdigest()

    def verify(self,filepath:str,content:str)->bool:
        expected=self._hashes.get(filepath)
        if expected is None:return True
        current=hashlib.sha256(content.encode()).hexdigest()
        return current==expected

    def diff_files(self,filepath:str,old_content:str,new_content:str)->list[str]:
        old_lines=old_content.splitlines()
        new_lines=new_content.splitlines()
        diffs=[f"+{l}" for l in new_lines if l not in old_lines]+[f"-{l}" for l in old_lines if l not in new_lines]
        return diffs[:50]
