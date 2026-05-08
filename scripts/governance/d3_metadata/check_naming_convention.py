"""GATE-11 命名规范门禁 — 全类型命名检测。

权威依据：docs/01_policies_and_standards/governance/document/file-naming-standard.md v2.0.1 §五

检查项：
  N-01  文件名大写检测 + 白名单
  N-02  版本号后缀检测 + 技术栈豁免
  N-03  日期后缀检测 + LATEST 豁免
  N-04  ADR 嵌套编号检测
  N-05  ADR 缺 kebab 尾缀检测
  N-06  module_id scope 前缀检测
  N-07  module_id 与文件名编号一致性
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402

# ---------------------------------------------------------------------------
# 白名单与豁免配置
# ---------------------------------------------------------------------------

FILENAME_UPPERCASE_WHITELIST: list[str] = [
    "README.md",
    "AGENTS.md",
    "INDEX.md",
    "LATEST.md",
    "TODO.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    "MAKEFILE",
    "Dockerfile",
]

TECH_VERSION_TOKENS: list[str] = [
    "pydantic-v2",
    "python-v3",
    "claude-3",
    "deepseek-v3",
    "deepseek-v4",
    "gpt-4",
    "gpt-5",
    "glm-4",
    "qwen-2",
    "pytest-8",
    "react-18",
    "vue-3",
    "node-v20",
    "node-v18",
    "django-5",
    "fastapi-0",
    "postgres-16",
    "redis-7",
    "k8s-1",
    "terraform-1",
    "ubuntu-22",
    "ubuntu-24",
]

VALID_PREFIXES: list[str] = ["validate_", "detect_", "audit_", "check_", "register_", "sync_", "generate_", "scan_", "audit_session_"]

PATH_EXEMPT_PREFIXES: list[str] = [
    "archive/",
    "_reorg_snapshots/",
    ".ruff_cache/",
]

SESSION_LOG_PATTERN = re.compile(r"^session-\d{8}-\d{3}")


@dataclass
class NamingViolation:
    rule: str
    message: str
    filepath: str


# ---------------------------------------------------------------------------
# N-01: 文件名大写检测
# ---------------------------------------------------------------------------

_UPPERCASE_RE = re.compile(r"[A-Z]")


def _check_n01_uppercase(filepath: str) -> list[NamingViolation]:
    """_check_n01_uppercase implementation."""
    name = Path(filepath).name
    if name in FILENAME_UPPERCASE_WHITELIST:
        return []
    if _UPPERCASE_RE.search(name):
        return [NamingViolation(rule="N-01", message=f"文件名含连续大写字母: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-02: 版本号后缀检测
# ---------------------------------------------------------------------------

_VERSION_SUFFIX_RE = re.compile(r"(?:-v\d+|-round\d+|-iteration\d+|-version\d+)", re.IGNORECASE)


def _check_n02_version_suffix(filepath: str) -> list[NamingViolation]:
    """_check_n02_version_suffix implementation."""
    name = Path(filepath).name
    lower_name = name.lower()
    for token in TECH_VERSION_TOKENS:
        if token.lower() in lower_name:
            return []
    if _VERSION_SUFFIX_RE.search(name):
        return [NamingViolation(rule="N-02", message=f"文件名含版本号后缀: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-03: 日期后缀检测
# ---------------------------------------------------------------------------

_DATE_SUFFIX_RE = re.compile(r"[-_]\d{8}(?![-_]LATEST)")


def _check_n03_date_suffix(filepath: str) -> list[NamingViolation]:
    """_check_n03_date_suffix implementation."""
    name = Path(filepath).name
    if "LATEST" in name.upper():
        return []
    stem = Path(filepath).stem
    if re.search(r"\d{4}-\d{2}-\d{2}", stem):
        return []
    if _DATE_SUFFIX_RE.search(name):
        return [NamingViolation(rule="N-03", message=f"文件名含日期后缀（非 ISO 格式）: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-04: ADR 嵌套编号检测
# ---------------------------------------------------------------------------

_ADR_NESTED_RE = re.compile(r"^adr-\d+-\d+", re.IGNORECASE)


def _check_n04_adr_nested(filepath: str) -> list[NamingViolation]:
    """_check_n04_adr_nested implementation."""
    name = Path(filepath).name
    rel = filepath.replace("\\", "/").lower()
    if "adr/" not in rel:
        return []
    if _ADR_NESTED_RE.match(Path(filepath).stem.lower()):
        return [NamingViolation(rule="N-04", message=f"ADR 文件名含嵌套编号: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-05: ADR 缺 kebab 尾缀检测
# ---------------------------------------------------------------------------

_ADR_PLAIN_RE = re.compile(r"^adr-\d+$", re.IGNORECASE)


def _check_n05_adr_missing_suffix(filepath: str) -> list[NamingViolation]:
    """_check_n05_adr_missing_suffix implementation."""
    name = Path(filepath).name
    if name == "_template.md":
        return []
    rel = filepath.replace("\\", "/").lower()
    if "adr/" not in rel:
        return []
    stem = Path(filepath).stem.lower()
    if _ADR_PLAIN_RE.match(stem) and stem != "_template":
        return [NamingViolation(rule="N-05", message=f"ADR 文件名缺少 kebab 尾缀: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-06: module_id scope 前缀检测
# ---------------------------------------------------------------------------

_MODULE_ID_SCOPE_RE = re.compile(r"^module_id:\s*(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW)-\d+", re.MULTILINE)


def _check_n06_module_id_scope(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """_check_n06_module_id_scope implementation."""
    name = Path(filepath).name
    if name.lower().startswith("adr-"):
        return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = abspath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    if _MODULE_ID_SCOPE_RE.search(content):
        return []
    if "module_id:" in content:
        return [NamingViolation(rule="N-06", message=f"module_id 缺少 scope 前缀: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-07: module_id 与文件名编号一致性
# ---------------------------------------------------------------------------

_MODULE_ID_NUM_RE = re.compile(r"^module_id:\s*ADR-(\d+)", re.MULTILINE)
_FILENAME_ADR_NUM_RE = re.compile(r"^adr-(\d+)", re.IGNORECASE)


def _check_n07_module_id_number_mismatch(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """_check_n07_module_id_number_mismatch implementation."""
    name = Path(filepath).name
    stem = Path(filepath).stem.lower()
    if not stem.startswith("adr-"):
        return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = abspath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    fn_match = _FILENAME_ADR_NUM_RE.match(stem)
    mod_match = _MODULE_ID_NUM_RE.search(content)
    if not fn_match or not mod_match:
        return []
    fn_num = fn_match.group(1)
    mod_num = mod_match.group(1)
    if fn_num != mod_num:
        return [NamingViolation(
            rule="N-07",
            message=f"ADR 模块编号与文件名编号不一致: module_id=ADR-{mod_num}, 文件名={stem}",
            filepath=filepath,
        )]
    return []


# ---------------------------------------------------------------------------
# 路径豁免判断
# ---------------------------------------------------------------------------

def _is_path_exempt(filepath: str) -> bool:
    """_is_path_exempt implementation."""
    normalized = filepath.replace("\\", "/").lower()
    for prefix in PATH_EXEMPT_PREFIXES:
        if normalized.startswith(prefix.lower()):
            return True
    name = Path(filepath).name.lower()
    if SESSION_LOG_PATTERN.match(name):
        return True
    rel = filepath.replace("\\", "/").lower()
    if "session-logs/" in rel:
        return True
    if "docs/19_development_workspace/session-logs/" in rel:
        return True
    return False


# ---------------------------------------------------------------------------
# 统一入口
# ---------------------------------------------------------------------------

def check_file(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """Check compliance and report findings."""
    if _is_path_exempt(filepath):
        return []
    violations: list[NamingViolation] = []
    violations.extend(_check_n01_uppercase(filepath))
    violations.extend(_check_n02_version_suffix(filepath))
    violations.extend(_check_n03_date_suffix(filepath))
    violations.extend(_check_n04_adr_nested(filepath))
    violations.extend(_check_n05_adr_missing_suffix(filepath))
    violations.extend(_check_n06_module_id_scope(filepath, abspath))
    violations.extend(_check_n07_module_id_number_mismatch(filepath, abspath))
    return violations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def check_naming(file_path: str) -> tuple[bool, str]:
    """Check compliance and report findings."""
    name = Path(file_path).stem
    for prefix in VALID_PREFIXES:
        if name.startswith(prefix):
            return True, f"✅ {name} 符合前缀 {prefix}"
    return False, f"❌ {name} 不符合任何标准前缀 {VALID_PREFIXES}"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    if len(sys.argv) < 2:
        violations = check_file(sys.argv[1]) if len(sys.argv) > 1 else []
        for v in violations:
            print(f"[{v.rule}] {v.message}")
        return EXIT_FINDINGS if violations else EXIT_PASS
    ok, msg = check_naming(sys.argv[1])
    print(msg)
    return EXIT_PASS if ok else EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
