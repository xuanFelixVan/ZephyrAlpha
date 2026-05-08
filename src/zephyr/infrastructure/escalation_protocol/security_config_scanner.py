"""Security Config Scanner — v0.13.0 缺失安全配置扫描器。"""
from __future__ import annotations

REQUIRED_CONFIGS={"limits.yaml":"resource_limits","cors.yaml":"cors_whitelist","secrets.yaml":"api_keys"}

class SecurityConfigScanner:
    def scan(self, existing_files:list[str])->dict:
        missing={}
        for req_file,desc in REQUIRED_CONFIGS.items():
            if not any(req_file in f for f in existing_files):
                missing[req_file]=desc
        return {"missing_count":len(missing),"missing":missing,"complete":len(missing)==0}
