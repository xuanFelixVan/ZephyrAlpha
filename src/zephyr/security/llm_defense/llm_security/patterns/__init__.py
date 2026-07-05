# [A_module] module_id=MOD-SEC_patterns | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

__all__ = [
    "PRECOMPILED_ENCODING",
    "InjectionPattern",
    "injection_patterns",
    "scan_direct",
    "scan_encoding_escape",
    "scan_indirect",
    "scan_jailbreak",
    "scan_path_traversal",
    "scan_secrets",
    "scan_semantic_attacks",
    "scan_shell",
    "scan_sql",
    "secrets",
]

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
