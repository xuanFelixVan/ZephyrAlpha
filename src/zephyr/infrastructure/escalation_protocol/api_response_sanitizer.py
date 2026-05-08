"""API Response Sanitizer — v0.9.0 API响应清洗器: 外部API返回内容清洗+injection检测。"""
from __future__ import annotations

class APIResponseSanitizer:
    def sanitize(self,response_text:str)->str:
        dangerous=["<script","javascript:","onerror=","onclick="]
        result=response_text
        for d in dangerous:
            result=result.replace(d,"[SANITIZED]")
        return result

    def is_suspicious(self,response_text:str)->bool:
        return any(p in response_text.lower() for p in ["<script","eval(","__import__("])
