# [A_module] module_id=MOD-SEC_patterns | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

__all__ = [
    "InjectionPattern",
    "PRECOMPILED_ENCODING",
    "scan_direct",
    "scan_encoding_escape",
    "scan_indirect",
    "scan_jailbreak",
    "scan_path_traversal",
    "scan_semantic_attacks",
    "scan_shell",
    "scan_sql",
    "scan_secrets",
    "injection_patterns",
    "secrets",
]

from typing import Any, Dict, List, Optional

class PatternMatch:
    def __init__(self, pattern_type, value, confidence=1.0):
        self.pattern_type = pattern_type
        self.value = value
        self.confidence = confidence

class PatternRegistry:
    def __init__(self):
        self._patterns = []

    def register(self, pattern):
        self._patterns.append(pattern)

    def match(self, text):
        return []
