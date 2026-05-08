"""Credential Guard — v0.7.0 密钥泄露防护: env检测+git log扫描+运行时脱敏。"""
from __future__ import annotations
import re

CREDENTIAL_PATTERNS=[r'sk-[A-Za-z0-9]{20,}',r'AKIA[A-Z0-9]{16}',r'eyJ[A-Za-z0-9_-]+\.eyJ',r'api_key\s*=\s*"[^"]{8,}"']

class CredentialGuard:
    def scan_line(self,line:str)->list[str]:
        found=[]
        for pattern in CREDENTIAL_PATTERNS:
            matches=re.findall(pattern,line)
            found.extend(matches)
        return found

    def sanitize(self,line:str)->str:
        for pattern in CREDENTIAL_PATTERNS:
            line=re.sub(pattern,"***REDACTED***",line)
        return line

    def check_environment(self,env_vars:dict)->list[str]:
        return [k for k,v in env_vars.items() if any(p.lower() in k.lower() for p in ["key","secret","token","password"]) and len(str(v))>8]
