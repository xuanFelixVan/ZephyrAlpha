# [A_module] module_id=MOD-SEC_injection_patterns | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
class InjectionPattern:
    def __init__(self, pattern_type="", regex="", severity="medium"):
        self.pattern_type = pattern_type
        self.regex = regex
        self.severity = severity

    def match(self, text):
        return False


PRECOMPILED_ENCODING = {"utf8": True, "ascii": True, "latin1": True}


def scan_direct(text, patterns=None):
    return []


def scan_encoding_escape(text):
    return []


def scan_indirect(text, context=None):
    return []


def scan_jailbreak(text):
    return []


def scan_path_traversal(text):
    return []


def scan_semantic_attacks(text):
    return []


def scan_shell(text):
    return []


def scan_sql(text):
    return []


# Precompiled pattern constants for each scan category
PRECOMPILED_DIRECT: list = []
PRECOMPILED_JAILBREAK: list = []
PRECOMPILED_NESTED: list = []
PRECOMPILED_SEMANTIC: list = []
PRECOMPILED_SHELL: list = []
PRECOMPILED_SQL: list = []
PRECOMPILED_PATH: list = []


def check_file_type(content: str) -> str:
    """Detect the content type for injection scanning."""
    if not content:
        return "empty"
    if any(tag in content for tag in ("<", ">", "script", "html")):
        return "html"
    if any(kw in content for kw in ("SELECT", "INSERT", "DROP", "UNION", "--")):
        return "sql"
    if any(kw in content for kw in ("import os", "subprocess", "eval(", "exec(")):
        return "code"
    return "text"
