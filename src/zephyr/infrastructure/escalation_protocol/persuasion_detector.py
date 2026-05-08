"""Persuasion Detector — D-022-09 心理说服检测: 对抗语气+恳求+绕过指令。"""
from __future__ import annotations

SUSPICIOUS_PATTERNS=["please","urgent","trust me","you must","override","bypass","ignore rules","just this once","don't escalate"]

class PersuasionDetector:
    def detect(self, text:str)->tuple[bool,list[str]]:
        found=[p for p in SUSPICIOUS_PATTERNS if p.lower() in text.lower()]
        return len(found)>0,found

    def score(self, text:str)->float:
        _,found=self.detect(text)
        return min(1.0,len(found)/len(SUSPICIOUS_PATTERNS))
