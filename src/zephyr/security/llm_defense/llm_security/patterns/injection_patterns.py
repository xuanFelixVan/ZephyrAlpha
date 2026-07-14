# [BLUEPRINT] MOD-LLM_SECURITY
# [MODULE] zephyr.security.llm_defense.llm_security.patterns.injection_patterns
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.llm_security.test_injection_patterns
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from typing import Final

import os
import re
from typing import Any


class InjectionPattern:
    """Legacy injection pattern descriptor."""

    def __init__(self, pattern_type: str = "", regex: str = "", severity: str = "medium"):
        self.pattern_type = pattern_type
        self.regex = regex
        self.severity = severity

    def match(self, text: str) -> bool:
        try:
            return re.search(self.regex, text, re.IGNORECASE) is not None
        except re.error:
            return False


# --- Pattern definitions (regex, category) ---

_DIRECT_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+(all\s+)?previous\s+instructions?", "direct_injection"),
    (r"disregard\s+(the\s+)?above", "direct_injection"),
    (r"you\s+are\s+now\s+(an?\s+)?(unrestricted|unfiltered|dan)\b", "direct_injection"),
    (r"what\s+is\s+your\s+system\s+prompt", "direct_injection"),
    (r"reveal\s+your\s+(system\s+)?prompt", "direct_injection"),
    (r"do\s+what\s+i\s+say", "direct_injection"),
]

_NESTED_PATTERNS: list[tuple[str, str]] = [
    (r"\{\{[^}]*\}\}", "nested_structure"),
    (r"\(\([^)]*\)\)", "nested_structure"),
    (r"<<<[^>]*>>>", "nested_structure"),
]

_INDIRECT_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+(all\s+)?previous\s+instructions?", "rag_poisoning"),
    (r"disregard\s+(the\s+)?above", "rag_poisoning"),
]

_JAILBREAK_PATTERNS: list[tuple[str, str]] = [
    (r"\bdan\s+mode\b", "dan_mode"),
    (r"enable\s+dan\b", "dan_mode"),
    (r"jailbreak", "dan_mode"),
]

_ENCODING_OBFUSCATION_PATTERNS: list[tuple[str, str]] = [
    (r"\\x[0-9a-fA-F]{2}", "encoding_obfuscation"),
    (r"\\u[0-9a-fA-F]{4}", "encoding_obfuscation"),
]

_TOKEN_SMUGGLING_PATTERNS: list[tuple[str, str]] = [
    (r"\bs\s+y\s+s\s+t\s+e\s+m\b", "token_smuggling"),
    (r"\bp\s+r\s+o\s+m\s+p\s+t\b", "token_smuggling"),
]

_EMOTIONAL_PATTERNS: list[tuple[str, str]] = [
    (r"someone\s+will\s+die", "emotional_manipulation"),
    (r"if\s+you\s+don'?t\s+answer", "emotional_manipulation"),
    (r"please\s+,\s+i\s+(beg|implore)", "emotional_manipulation"),
]

_SHELL_PATTERNS: list[tuple[str, str]] = [
    (r"rm\s+-rf", "destructive_command"),
    (r"curl\s+[^|]+\|\s*(sh|bash)", "remote_execution"),
    (r"wget\s+[^|]+\|\s*(sh|bash)", "remote_execution"),
    (r"subprocess\.(Popen|run|call)", "subprocess_invocation"),
    (r"eval\s*\(", "eval_exec"),
    (r"exec\s*\(", "eval_exec"),
    (r"os\.system\s*\(", "os_system"),
]

_SQL_PATTERNS: list[tuple[str, str]] = [
    (r"'\s*OR\s+1=1", "sql_injection"),
    (r"'\s*OR\s+'1'='1", "sql_injection"),
    (r"DROP\s+TABLE", "sql_drop"),
    (r"UNION\s+SELECT", "sql_union"),
    (r"INSERT\s+INTO", "sql_insert"),
    (r"DELETE\s+FROM", "sql_delete"),
    (r"--\s*$", "sql_comment"),
]

_PATH_TRAVERSAL_PATTERNS: list[tuple[str, str]] = [
    (r"\.\./", "path_traversal"),
    (r"\.\.\\", "path_traversal"),
    (r"file:///", "file_uri"),
    (r"/etc/passwd", "sensitive_file"),
    (r"/etc/shadow", "sensitive_file"),
]

_SEMANTIC_PATTERNS: list[tuple[str, str]] = [
    (r"extract\s+(the\s+)?training\s+data", "training_data_extraction"),
    (r"extract\s+(the\s+)?model\s+(weights|architecture)", "model_theft"),
    (r"file\s+write\s+tool\s+to\s+create\s+a\s+backdoor", "tool_abuse"),
    (r"backdoor\s+script", "tool_abuse"),
    (r"create\s+a\s+backdoor", "tool_abuse"),
]

# Zero-width characters: U+200B–U+200F, U+FEFF
_ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\ufeff]")

# Threshold for context overflow (characters)
_CONTEXT_OVERFLOW_THRESHOLD = 10000


def _compile(patterns: list[tuple[str, str]]) -> list[tuple[Any, str]]:
    """Compile a list of (regex, category) into (compiled, category)."""
    return [(re.compile(p, re.IGNORECASE), cat) for p, cat in patterns]


# --- Precompiled pattern exports (non-empty) ---

PRECOMPILED_DIRECT: Final[list] = _compile(_DIRECT_PATTERNS + _NESTED_PATTERNS)
PRECOMPILED_JAILBREAK: Final[list] = _compile(
    _JAILBREAK_PATTERNS
    + _ENCODING_OBFUSCATION_PATTERNS
    + _TOKEN_SMUGGLING_PATTERNS
    + _EMOTIONAL_PATTERNS
)
PRECOMPILED_SHELL: Final[list] = _compile(_SHELL_PATTERNS)
PRECOMPILED_SQL: Final[list] = _compile(_SQL_PATTERNS)
PRECOMPILED_SEMANTIC: Final[list] = _compile(_SEMANTIC_PATTERNS)
PRECOMPILED_PATH: Final[list] = _compile(_PATH_TRAVERSAL_PATTERNS)
PRECOMPILED_ENCODING: Final[list] = [
    ("zero_width", _ZERO_WIDTH_RE),
    ("hex_escape", re.compile(r"\\x[0-9a-fA-F]{2}")),
    ("unicode_escape", re.compile(r"\\u[0-9a-fA-F]{4}")),
]


def scan_direct(text: str, patterns: list | None = None) -> list[dict[str, Any]]:
    """Scan for direct prompt-injection and nested-structure patterns."""
    if not text:
        return []
    compiled = patterns if patterns is not None else PRECOMPILED_DIRECT
    hits: list[dict[str, Any]] = []
    for regex, cat in compiled:
        m = regex.search(text)
        if m:
            hits.append({"category": cat, "match": m.group(), "position": m.start()})
    return hits


def scan_indirect(text: str, context: object = None) -> list[dict[str, Any]]:
    """Scan for indirect injection (RAG poisoning) + context overflow."""
    if not text:
        return []
    hits: list[dict[str, Any]] = []
    for regex, cat in _compile(_INDIRECT_PATTERNS):
        m = regex.search(text)
        if m:
            hits.append({"channel": "rag_poisoning", "category": cat, "match": m.group()})
    if len(text) > _CONTEXT_OVERFLOW_THRESHOLD:
        hits.append({"channel": "context_overflow", "length": len(text)})
    return hits


def scan_jailbreak(text: str) -> list[dict[str, Any]]:
    """Scan for jailbreak, encoding-obfuscation, token-smuggling, emotional."""
    if not text:
        return []
    hits: list[dict[str, Any]] = []
    for regex, cat in PRECOMPILED_JAILBREAK:
        m = regex.search(text)
        if m:
            hits.append({"category": cat, "match": m.group(), "position": m.start()})
    return hits


def scan_shell(text: str) -> list[dict[str, Any]]:
    """Scan for shell-injection and dangerous-subprocess patterns."""
    if not text:
        return []
    hits: list[dict[str, Any]] = []
    for regex, cat in PRECOMPILED_SHELL:
        m = regex.search(text)
        if m:
            hits.append({"category": cat, "match": m.group()})
    return hits


def scan_sql(text: str) -> list[dict[str, Any]]:
    """Scan for SQL-injection patterns."""
    if not text:
        return []
    hits: list[dict[str, Any]] = []
    for regex, cat in PRECOMPILED_SQL:
        m = regex.search(text)
        if m:
            hits.append({"category": cat, "match": m.group()})
    return hits


def scan_path_traversal(text: str) -> list[dict[str, Any]]:
    """Scan for path-traversal and sensitive-file-access patterns."""
    if not text:
        return []
    hits: list[dict[str, Any]] = []
    for regex, cat in PRECOMPILED_PATH:
        m = regex.search(text)
        if m:
            hits.append({"category": cat, "match": m.group()})
    return hits


def scan_encoding_escape(text: str) -> list[dict[str, Any]]:
    """Scan for encoding-escape attacks (zero-width, hex, unicode)."""
    if not text:
        return []
    hits: list[dict[str, Any]] = []
    for technique, regex in PRECOMPILED_ENCODING:
        found = regex.findall(text)
        if found:
            hits.append({"technique": technique, "count": len(found)})
    return hits


def scan_semantic_attacks(text: str) -> list[dict[str, Any]]:
    """Scan for semantic attacks (training-data extraction, model theft, tool abuse)."""
    if not text:
        return []
    hits: list[dict[str, Any]] = []
    for regex, cat in PRECOMPILED_SEMANTIC:
        m = regex.search(text)
        if m:
            hits.append({"category": cat, "match": m.group()})
    return hits


# File-type -> applicable scan patterns mapping
_FILE_TYPE_PATTERNS: dict[str, list] = {
    ".py": None,  # sentinel: returns PRECOMPILED_SHELL
    ".js": None,
    ".ts": None,
    ".sh": None,
    ".sql": None,  # returns PRECOMPILED_SQL
    ".html": None,  # returns PRECOMPILED_DIRECT
    ".htm": None,
}


def check_file_type(filename: str) -> list:
    """Return applicable scan patterns based on file extension.

    Code/script files return shell patterns, SQL files return SQL patterns,
    HTML files return direct-injection patterns, unknown types return [].
    """
    if not filename:
        return []
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".py", ".js", ".ts", ".sh"):
        return PRECOMPILED_SHELL
    if ext == ".sql":
        return PRECOMPILED_SQL
    if ext in (".html", ".htm"):
        return PRECOMPILED_DIRECT
    return []
