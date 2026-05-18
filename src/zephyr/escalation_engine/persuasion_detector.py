# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.persuasion_detector

# [INVARIANTS] 心理说服检测不可禁用;Cialdini六原则必须覆盖

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Persuasion Detector — D-022-09 心理说服检测: 对抗语气+恳求+绕过指令。
"""
from __future__ import annotations

SUSPICIOUS_PATTERNS=["please","urgent","trust me","you must","override","bypass","ignore rules","just this once","don't escalate"]

class PersuasionDetector:
    def detect(self, text:str)->tuple[bool,list[str]]:
        found=[p for p in SUSPICIOUS_PATTERNS if p.lower() in text.lower()]
        return len(found)>0,found

    def score(self, text:str)->float:
        _,found=self.detect(text)
        return min(1.0,len(found)/len(SUSPICIOUS_PATTERNS))
