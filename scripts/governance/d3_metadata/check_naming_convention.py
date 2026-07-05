# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_naming_convention.py | §
# [MODULE] scripts.governance.d3_metadata.check_naming_convention
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] .pre_commit-config.yaml GATE-11; .github/workflows/governance.yml; tests/test_gate11_naming_convention.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] N-01~N-16 rules are append-only; whitelist changes require Owner approval
# [MODIFY-GUARD] FILENAME_UPPERCASE_WHITELIST, _DATA_FILE_EXEMPT_NAMES, TECH_VERSION_TOKENS, _N16_*_FALLBACK changes require Owner approval; N-16豁免清单真源在trae_028.yaml §n16_config(代码仅fail-open回退)
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] exit 0=clean; exit 1=violations found; exit 2=usage error
# [TESTS] tests/test_gate11_naming_convention.py
# [TTL] task_bound
"""GATE-11 命名规范门禁 — 全类型命名检测。

权威依据：docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml v1.5.0 (GOV-DOC-003 命名规则真源;N-16 见 §gov_doc_003_filename_uniqueness,豁免清单真源 §n16_config)

检查项：
  N-01  文件名大写检测 + 白名单
  N-02  版本号后缀检测 + 技术栈豁免
  N-03  日期后缀检测 + LATEST 豁免
  N-04  ADR 嵌套编号检测
  N-05  ADR 缺 kebab 尾缀检测
  N-06  module_id scope 前缀检测
  N-07  module_id 与文件名编号一致性
  N-08  Python 文件名 snake_case 合规检测
  N-09  目录名空格检测
  N-10  目录名 snake_case 合规检测（禁止大写/kebab-case/驼峰/空格）
  N-11  文件名后缀与 doc_type 一致性检测
  N-12  KE 条目命名格式检测
  N-13  YAML/JSON/MD 文件名 snake_case 合规检测
  N-14  __init__.py 必须定义 __all__
  N-15  BLUEPRINT 头部路径必须存在
  N-16  文件名项目内唯一性检测（tests/ + docs/）——真源：trae_028_doc_structure_naming.yaml v1.5.0 §gov_doc_003_filename_uniqueness.n16_config(豁免清单从此动态加载,硬编码仅作fail-open回退)
        设计权衡（勿误判为 bug 扩展）：src/ 不覆盖——src/ 有模块化目录结构（包隔离）+ __all__ 注册 + RULE-TWO 孤儿检测兜底，同名冲突少；tests/docs/ 扁平堆积易撞名。扩展扫描到 src/ 会误报跨包同名（如多个 __init__.py/utils.py）。
  N-17  blueprint_id 域片段与 [DOMAIN] 一致性检测（裁定#206 B-5 派生范式）

独立模式：
  --validate-ssot  SSoT(trae_028) 与脚本双轨正则 + N-16 fallback 联动一致性校验
                    （pre-commit 自动触发，防规则改了脚本没跟上；能力反查 alias=ssot_linkage_validator）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: GATE-11 命名规范门禁 — 全类型命名检测。
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

# 双轨正则真源归位：从 validate_module_id_naming.py 复用（消除正则重复定义）
# R2 治本修订（2026-07-05）：MODULE_ID_D_PREFIX_RE 已废弃为 module_id 派生轨，
# 重定义为 SUBMODULE_ID_RE（submodule_id 专用，见 trae_028 gov_doc_009）
from d3_metadata.validate_module_id_naming import (
    MODULE_ID_LAYER_MASTER_RE as _MODULE_ID_LAYER_MASTER_RE,
    MODULE_ID_DOMAIN_DERIVED_RE as _MODULE_ID_DOMAIN_DERIVED_RE,
    MODULE_ID_SHARED_RE as _MODULE_ID_SHARED_RE,
    SUBMODULE_ID_RE as _SUBMODULE_ID_RE,
    is_valid_module_id as _is_valid_module_id,
)

# ---------------------------------------------------------------------------
# 白名单与豁免配置
# ---------------------------------------------------------------------------

# 大写文件白名单（治本：对齐 trae_028.yaml L190 + L224 根目录白名单）
# 硬约束：AGENTS.md(Trae IDE)、Dockerfile(Docker build)
# GitHub平台功能：README.md/LICENSE/CONTRIBUTING.md/SECURITY.md（大小写不敏感识别，社区约定大写）
# 已移除：PKG_INFO/SOURCES.txt（Python setuptools 构建产物，应 gitignore，不应入库）
FILENAME_UPPERCASE_WHITELIST: list[str] = [
    "AGENTS.md",
    "Dockerfile",
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
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

VALID_PREFIXES: list[str] = [
    "validate_",
    "detect_",
    "audit_",
    "check_",
    "register_",
    "sync_",
    "generate_",
    "scan_",
    "audit_session_",
]

PATH_EXEMPT_PREFIXES: list[str] = [
    "archive/",
    "_reorg_snapshots/",
    ".ruff_cache/",
    "config/",
    "data/",
    "models/",
    "logs/",
    "reports/",
    "_journals/",
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
    if name.startswith("."):
        return []
    # ID格式文件豁免（大写字母是ID一部分）
    lower_name = name.lower()
    if lower_name.startswith("task-") or lower_name.startswith("ke-") or lower_name.startswith("dm-"):
        return []
    # 安全扫描输出豁免（ISO 8601时间戳含T/Z大写）
    if lower_name.startswith("sec_leak_") and re.search(r"\d{8}T\d{6}Z", name):
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
    if lower_name.startswith("ke-"):
        return []
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

# N-03 豁免模式：任务ID文件(日期是ID一部分)、自动生成时间戳文件、ISO 8601格式
_N03_TASK_ID_RE = re.compile(r"^TASK-[A-Z]+-\d{8}\d*\.md$", re.IGNORECASE)
_N03_HEALTH_SNAPSHOT_RE = re.compile(r"^health_\d{14}\.json$")
_N03_SEC_LEAK_RE = re.compile(r"^sec_leak_\d{8}T\d{6}Z\.json$")


def _check_n03_date_suffix(filepath: str) -> list[NamingViolation]:
    """_check_n03_date_suffix implementation."""
    name = Path(filepath).name
    if "LATEST" in name.upper():
        return []
    # 豁免：任务ID文件(日期是任务ID一部分，如TASK-OPS-2026062103.md)
    if _N03_TASK_ID_RE.match(name):
        return []
    # 豁免：健康快照时间戳文件(YYYYMMDDHHMMSS格式，如health_20260623142754.json)
    if _N03_HEALTH_SNAPSHOT_RE.match(name):
        return []
    # 豁免：安全扫描输出(ISO 8601格式，如sec_leak_20260611T212859Z.json)
    if _N03_SEC_LEAK_RE.match(name):
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

_ADR_NESTED_RE = re.compile(r"^(adr|kbg)-\d+-\d+", re.IGNORECASE)


def _check_n04_adr_nested(filepath: str) -> list[NamingViolation]:
    """_check_n04_adr_nested implementation."""
    name = Path(filepath).name
    rel = filepath.replace("\\", "/").lower()
    if "adr/" not in rel and "08_knowledge/" not in rel and "knowledge/" not in rel:
        return []
    if _ADR_NESTED_RE.match(Path(filepath).stem.lower()):
        return [NamingViolation(rule="N-04", message=f"ADR/KBG 文件名含嵌套编号: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-05: ADR 缺 kebab 尾缀检测
# ---------------------------------------------------------------------------

_ADR_PLAIN_RE = re.compile(r"^(adr|kbg)-\d+$", re.IGNORECASE)


def _check_n05_adr_missing_suffix(filepath: str) -> list[NamingViolation]:
    """_check_n05_adr_missing_suffix implementation."""
    name = Path(filepath).name
    if name == "_template.md":
        return []
    rel = filepath.replace("\\", "/").lower()
    if "adr/" not in rel and "08_knowledge/" not in rel and "knowledge/" not in rel:
        return []
    stem = Path(filepath).stem.lower()
    if _ADR_PLAIN_RE.match(stem) and stem != "_template":
        return [NamingViolation(rule="N-05", message=f"ADR/KBG 文件名缺少 kebab 尾缀: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-06: module_id scope 前缀检测 + 双轨制格式校验（裁定#208 R1/R4 + R2 治本修订:
#        layer-master 轨 MOD-{LAYER_CODE}-{SEQ} 序号必填 +
#        domain-functional 派生轨 MOD-{DOMAIN_FRAGMENT}[-NNN] 序号可选）
# R2 治本修订（2026-07-05）：D-XXX-{SEQ} 已废弃为 module_id 派生轨，
#        重定义为 submodule_id 专用（见 trae_028 gov_doc_009）。
#        D- 前缀字符串触发 ERROR（不允许作为 module_id 使用）。
# ---------------------------------------------------------------------------

_MODULE_ID_SCOPE_RE = re.compile(
    r"^\s*module_id:[ \t]*[\"']?(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW|DOM|PS|SYS|KBG|REG|IDX|CFG|PHASE|TPL|IRN|TRAE|META|DM|SH)(?:[-_][A-Za-z0-9_]+)+[\"']?",
    re.MULTILINE,
)
# 裁定#208 R1/R4 + R2 治本修订: 双轨制 module_id 格式正则（真源已迁移至 validate_module_id_naming.py，
# 本文件通过顶部 import 复用 _MODULE_ID_LAYER_MASTER_RE 等常量，消除正则重复定义）
# 提取 module_id 值（兼容 YAML module_id: VALUE 和 .py 头部 module_id=VALUE 两种格式）
_MODULE_ID_VALUE_RE = re.compile(r'module_id[:=]\s*["\']?([A-Za-z][A-Za-z0-9_-]+)', re.MULTILINE)
# Relaxed regex for inline module_id: inside .py comment headers (e.g. "# [A_test] module_id: SRC-TST-0212 | ...")
_INLINE_MODULE_ID_SCOPE_RE = re.compile(
    r"module_id:\s*[\"']?(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW|DOM|PS|SYS|KBG|REG|IDX|CFG|PHASE|TPL|IRN|TRAE|META|DM|SH)(?:[-_][A-Za-z0-9_]+)+[\"']?\b"
)


def _check_n06_dual_track_format(filepath: str, content: str) -> list[NamingViolation]:
    """裁定#208 R4 + R2 治本修订: scope 前缀通过后，校验 MOD-*/SH-* module_id 值符合双轨制格式。

    layer-master 轨: MOD-{LAYER_CODE}-{SEQ}（序号必填）
    domain-functional 派生轨: MOD-{DOMAIN_FRAGMENT}[-NNN]（序号可选）
    跨域共享模块: SH-{ABBR}-{NNN}（序号必填，trae_028 L86/L466/L475）

    R2 治本修订（2026-07-05）：
    - D-XXX-NNN 已废弃为 module_id 派生轨，重定义为 submodule_id 专用
      （见 trae_028 gov_doc_009 和 validate_module_id_naming.py::is_valid_submodule_id）
    - 任何 D- 前缀的 module_id 值触发 ERROR（不允许作为 module_id 使用，
      应改用 MOD-{DOMAIN_FRAGMENT}[-NNN] 派生轨）

    非 MOD-*/SH-* 前缀（如 ADR/KBG/CFG/TRAE）跳过格式校验（由 scope 前缀检测覆盖）。
    """
    violations: list[NamingViolation] = []
    # 跳过 markdown 代码块（避免文档示例误判）
    clean = re.sub(r"```[\s\S]*?```", "", content)
    seen: set[str] = set()
    for m in _MODULE_ID_VALUE_RE.finditer(clean):
        value = m.group(1).strip().strip('"').strip("'")
        if value in seen or not value:
            continue
        seen.add(value)
        if value.startswith("MOD-"):
            if not (_MODULE_ID_LAYER_MASTER_RE.match(value) or _MODULE_ID_DOMAIN_DERIVED_RE.match(value)):
                violations.append(NamingViolation(
                    rule="N-06",
                    message=(
                        f"module_id 格式不符合双轨制(裁定#208): {value}"
                        f"（应为 MOD-{{LAYER}}-NNN layer-master 轨 或 MOD-{{DOMAIN_FRAGMENT}}[-NNN] 派生轨）"
                    ),
                    filepath=filepath,
                ))
        elif value.startswith("MOD"):
            # MOD_ 或 MODxxx — MOD 前缀后必须用连字符 - 分隔，禁止下划线 _
            violations.append(NamingViolation(
                rule="N-06",
                message=f"module_id 格式不符合双轨制(裁定#208): {value}（MOD 前缀后必须用连字符 - 分隔，禁止下划线 _）",
                filepath=filepath,
            ))
        elif value.startswith("D-"):
            # R2 治本修订（2026-07-05）：D-XXX-NNN 已废弃为 module_id 派生轨，
            # 重定义为 submodule_id 专用（见 trae_028 gov_doc_009）。
            # 任何 D- 前缀的 module_id 值触发 ERROR——应改用 MOD-{DOMAIN_FRAGMENT}[-NNN] 派生轨。
            violations.append(NamingViolation(
                rule="N-06",
                message=(
                    f"module_id D-前缀已废弃(R2治本修订,2026-07-05): {value}"
                    f"（D-XXX-NNN 重定义为 submodule_id 专用,见 trae_028 gov_doc_009;"
                    f"module_id 应改用 MOD-{{DOMAIN_FRAGMENT}}[-NNN] 派生轨）"
                ),
                filepath=filepath,
            ))
        elif value.startswith("D_"):
            violations.append(NamingViolation(
                rule="N-06",
                message=f"module_id 格式不符合双轨制(裁定#208): {value}（D 前缀后必须用连字符 - 分隔，禁止下划线 _）",
                filepath=filepath,
            ))
        elif value.startswith("SH-"):
            # 跨域共享模块: SH-{ABBR}-{NNN}（序号必填，trae_028 L86/L466/L475）
            if not _MODULE_ID_SHARED_RE.match(value):
                violations.append(NamingViolation(
                    rule="N-06",
                    message=(
                        f"module_id SH-前缀格式不符合跨域共享模块规范(trae_028 L86/L466/L475): {value}"
                        f"（应为 SH-{{ABBR}}-NNN，如 SH-DB-001）"
                    ),
                    filepath=filepath,
                ))
    return violations


def _check_n06_module_id_scope(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """_check_n06_module_id_scope implementation."""
    name = Path(filepath).name
    if name.lower().startswith("adr-"):
        return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = _read_text_bom_safe(abspath)
    except Exception:
        return []
    # Check: does ANY module_id: in the file have a valid scope prefix?
    if _MODULE_ID_SCOPE_RE.search(content) or _INLINE_MODULE_ID_SCOPE_RE.search(content):
        # 裁定#208 R4: scope 前缀通过后，校验 MOD-*/D-* module_id 双轨格式
        return _check_n06_dual_track_format(filepath, content)
    # For .py files, only check header area (not type annotations)
    if name.endswith(".py"):
        bp_match = re.search(r"^\s*#\s*\[BLUEPRINT\]\s+\S+\s+\|\s*\S+\s*\|", content, re.MULTILINE)
        if not bp_match:
            return []
        # Check if the file has module_id in its header area (first 25 lines)
        header = "\n".join(content.split("\n")[:25])
        if "module_id:" in header:
            # module_id exists but no scope prefix matched above → violation
            return [NamingViolation(rule="N-06", message=f"module_id 缺少 scope 前缀: {name}", filepath=filepath)]
        return []
    # For YAML/MD/JSON, use regex to find real module_id declarations
    # Skip code blocks (```...```), template placeholders, null values
    # Remove code blocks first for efficiency
    clean = re.sub(r"```[\s\S]*?```", "", content)
    # Find module_id declarations that are real values (not null/placeholder)
    _REAL_MID_RE = re.compile(r"^\s*module_id:[ \t]*(.+)", re.MULTILINE)
    for m in _REAL_MID_RE.finditer(clean):
        value = m.group(1).strip().strip('"').strip("'")
        if not value or value in ("null", "~", "None") or value.startswith("{") or value.startswith("<"):
            continue
        # This is a real module_id that doesn't match scope pattern
        return [NamingViolation(rule="N-06", message=f"module_id 缺少 scope 前缀: {name}", filepath=filepath)]
    return []


# ---------------------------------------------------------------------------
# N-07: module_id 与文件名编号一致性
# ---------------------------------------------------------------------------

_MODULE_ID_NUM_RE = re.compile(r"^module_id:\s*(ADR|KBG)-(\d+)", re.MULTILINE)
_FILENAME_ADR_NUM_RE = re.compile(r"^(adr|kbg)-(\d+)", re.IGNORECASE)


def _check_n07_module_id_number_mismatch(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """_check_n07_module_id_number_mismatch implementation."""
    name = Path(filepath).name
    stem = Path(filepath).stem.lower()
    if not stem.startswith(("adr-", "kbg-")):
        return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = _read_text_bom_safe(abspath)
    except Exception:
        return []
    fn_match = _FILENAME_ADR_NUM_RE.match(stem)
    mod_match = _MODULE_ID_NUM_RE.search(content)
    if not fn_match or not mod_match:
        return []
    prefix = fn_match.group(1).upper()
    fn_num = fn_match.group(2)
    mod_prefix = mod_match.group(1)
    mod_num = mod_match.group(2)
    if fn_num != mod_num:
        return [
            NamingViolation(
                rule="N-07",
                message=f"{prefix} 模块编号与文件名编号不一致: module_id={mod_prefix}-{mod_num}, 文件名={stem}",
                filepath=filepath,
            )
        ]
    return []


# ---------------------------------------------------------------------------
# N-08: Python 文件名 snake_case 合规检测
# ---------------------------------------------------------------------------

_SNAKE_CASE_PY_RE = re.compile(r"^[a-z_][a-z0-9_]*\.py$")
_PY_EXEMPT_NAMES: set[str] = {"__init__.py", "setup.py", "conftest.py", "__main__.py"}


def _check_n08_python_snake_case(filepath: str) -> list[NamingViolation]:
    """Python 源文件必须使用 snake_case 命名（PEP 8）。
    强化: __main__.py 豁免; test_ 前缀文件强制 snake_case; 禁止 CamelCase.py
    """
    name = Path(filepath).name
    if not name.endswith(".py"):
        return []
    if name in _PY_EXEMPT_NAMES:
        return []
    if not _SNAKE_CASE_PY_RE.match(name):
        reasons = []
        if re.search(r"[A-Z]", name):
            reasons.append("含大写字母(CamelCase)")
        if " " in name:
            reasons.append("含空格")
        if "-" in name:
            reasons.append("含连字符(kebab-case)")
        if not reasons:
            reasons.append("不符合 snake_case")
        return [
            NamingViolation(
                rule="N-08", message=f"Python 文件名不符合 snake_case({', '.join(reasons)}): {name}", filepath=filepath
            )
        ]
    return []


# ---------------------------------------------------------------------------
# N-09: 目录名空格检测
# ---------------------------------------------------------------------------


def _check_n09_dir_spaces(dirpath: str) -> list[NamingViolation]:
    """目录名禁止包含空格、制表符、非 ASCII 字符。
    强化: 检测空格 + 制表符 + 非 ASCII 字符
    """
    name = Path(dirpath).name
    violations: list[NamingViolation] = []
    if " " in name:
        violations.append(NamingViolation(rule="N-09", message=f"目录名含空格: {name}", filepath=dirpath))
    if "\t" in name:
        violations.append(NamingViolation(rule="N-09", message=f"目录名含制表符: {name}", filepath=dirpath))
    try:
        name.encode("ascii")
    except UnicodeEncodeError:
        violations.append(NamingViolation(rule="N-09", message=f"目录名含非 ASCII 字符: {name}", filepath=dirpath))
    return violations


# ---------------------------------------------------------------------------
# N-10: 目录名 snake_case 合规检测
# ---------------------------------------------------------------------------

_DIR_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_DIR_SINGLE_WORD_RE = re.compile(r"^[a-z][a-z0-9]*$")
_DIR_DOCS_NUM_PREFIX_RE = re.compile(r"^\d{2}_[a-z][a-z0-9_]*$")
_DIR_EXEMPT_NAMES: set[str] = {
    "__pycache__",
    ".git",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    ".tox",
    ".eggs",
    ".idea",
    ".vscode",
    ".trae",
    ".ailocks",
    ".aidrafts",
}
_DIR_MODULE_ID_RE = re.compile(r"^[A-Z]+-[A-Z]+[0-9]*-\d+(-[A-Z]+)?$|^[A-Z]+-\d+$|^[A-Z]+-[A-Z]+-\d+$")
_DIR_ROOT_KEBAB_EXEMPT: set[str] = set()
_DIR_KEBAB_PATH_PREFIXES: list[str] = [
    "src/zephyr/",
    "tests/",
    "docs/",
    "specs/",
    "frontend/",
]


def _check_n10_dir_naming(dirpath: str) -> list[NamingViolation]:
    """目录名必须为单词或 snake_case，禁止大写/kebab-case/驼峰/空格。
    命名规则真源: trae_028_doc_structure_naming.yaml gov_doc_003_naming_ssot
    强化: docs/ 下数字前缀目录豁免(01_xxx); __ 前缀目录豁免; .trae/.ailocks/.aidrafts 豁免;
          模块 ID 目录(MOD-XXX-NNN 等)豁免;
          pre_commit 目录豁免; egg-info 目录豁免; L0x_ 前缀目录豁免
    注意: 2026-06-19 移除 src/zephyr/、tests/、docs/ 下 kebab-case 豁免(统一snake_case)
          保留根级合法 kebab-case 目录豁免(历史遗留,待迁移)
    """
    name = Path(dirpath).name
    if name.startswith(".") or name in _DIR_EXEMPT_NAMES:
        return []
    if name.startswith("__") and name.endswith("__"):
        return []
    if name.startswith("_") and not name.startswith("__"):
        return []
    if _DIR_SNAKE_CASE_RE.match(name) or _DIR_SINGLE_WORD_RE.match(name):
        return []
    rel = dirpath.replace("\\", "/").lower()
    if _DIR_DOCS_NUM_PREFIX_RE.match(name) and ("docs/" in rel or rel == name):
        return []
    # Exempt module ID directories (e.g. MOD-TASK_SYSTEM, DOM-GOV-001, SYS-MASTER-001)
    if _DIR_MODULE_ID_RE.match(name):
        return []
    # Exempt root-level legitimate kebab-case directories (历史遗留,待迁移)
    if "/" not in dirpath.replace("\\", "/") and name in _DIR_ROOT_KEBAB_EXEMPT:
        return []
    # Exempt pre_commit directories (Python packaging convention)
    if name == "pre_commit":
        return []
    # Exempt egg-info directories (Python packaging convention)
    if name.endswith(".egg-info"):
        return []
    if name.endswith(".egg_info"):
        return []
    # Exempt L0x_ prefixed directories (layer naming convention)
    if re.match(r"^L\d{2}_", name):
        return []
    has_upper = bool(re.search(r"[A-Z]", name))
    has_hyphen = "-" in name
    has_space = " " in name
    reasons = []
    if has_upper:
        reasons.append("含大写字母")
    if has_hyphen:
        reasons.append("含连字符(kebab-case)")
    if has_space:
        reasons.append("含空格")
    if not reasons:
        reasons.append("不符合 snake_case 或单词格式")
    return [NamingViolation(rule="N-10", message=f"目录名不合规({', '.join(reasons)}): {name}", filepath=dirpath)]


# ---------------------------------------------------------------------------
# N-11: 文件名后缀与 doc_type 一致性检测
# ---------------------------------------------------------------------------

# 真源单一化：后缀规则是 doc_type 的属性，由 doc_type_vocabulary.yaml 唯一维护。
# 本模块直接消费词表（非同步复制），词表改即生效。禁止在此硬编码值名或后缀。
_DOC_TYPE_VOCAB_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "doc_type_vocabulary.yaml"
)


def _load_doc_type_suffixes() -> dict[str, list[str]]:
    """从 doc_type_vocabulary.yaml 加载 value→filename_suffixes 映射。"""
    data = yaml.safe_load(_DOC_TYPE_VOCAB_PATH.read_text(encoding="utf-8"))
    return {
        v["value"]: v["filename_suffixes"]
        for v in data.get("values", [])
        if "filename_suffixes" in v
    }


# 模块级加载一次（词表是项目内稳定文件，import 时读取）
_DOC_TYPE_SUFFIX_MAP: dict[str, list[str]] = _load_doc_type_suffixes()

_DOC_TYPE_RE = re.compile(r"^doc_type:\s*(\S+)", re.MULTILINE)


def _check_n11_doctype_suffix(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """01_policies_and_standards/ 下文件名后缀必须匹配 frontmatter doc_type。
    强化: 扩展 doc_type 映射表(vocabulary/blueprint/register/architecture_view/audit_report);
          YAML 文件也检查 doc_type 与后缀一致性;
          支持路径型后缀(如 _registry/vocabularies/glossary.yaml)
    """
    rel = filepath.replace("\\", "/")
    if "01_policies_and_standards/" not in rel:
        return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = _read_text_bom_safe(abspath)
    except Exception:
        return []
    dt_match = _DOC_TYPE_RE.search(content)
    if not dt_match:
        return []
    doc_type = dt_match.group(1)
    allowed_suffixes = _DOC_TYPE_SUFFIX_MAP.get(doc_type)
    if not allowed_suffixes:
        return []
    name = Path(filepath).name
    for suffix in allowed_suffixes:
        # 先检查文件名后缀
        if name.endswith(suffix):
            return []
        # 再检查相对路径后缀（支持路径型后缀如 _registry/vocabularies/glossary.yaml）
        if "/" in suffix and rel.endswith(suffix):
            return []
    return [
        NamingViolation(
            rule="N-11",
            message=f"文件名后缀与 doc_type 不匹配: doc_type={doc_type}, 文件名={name} (期望后缀: {', '.join(allowed_suffixes)})",
            filepath=filepath,
        )
    ]


# ---------------------------------------------------------------------------
# N-12: KE 条目命名格式检测
# 命名规则真源: trae_028_doc_structure_naming.yaml gov_doc_003_naming_ssot (snake_case)
# ---------------------------------------------------------------------------

_KE_PATTERN = re.compile(r"^ke-\d{1,4}-[a-z][a-z0-9_]+\.md$")
_KE_LEGACY_PATTERN = re.compile(r"^ke-\d+-[a-z0-9_-]+\.md$|^ke-[a-z0-9_-]+-\d+\.md$")
_KE_NUMERIC_TITLE_RE = re.compile(r"^ke-\d+-\d+\.md$")


def _check_n12_ke_naming(filepath: str) -> list[NamingViolation]:
    """KE 条目文件名必须符合 ke-{1-4位序号}-{snake_case_title}.md 格式。
    命名规则真源: trae_028_doc_structure_naming.yaml gov_doc_003_naming_ssot
    强化: 序号1-4位(ke-001~ke-9999); 禁止纯数字标题(ke-025-123.md); 路径范围扩展(含 08_knowledge/ 和 knowledge/)
    注意: 2026-06-19 从 kebab-case 改为 snake_case(与trae_028对齐)
    """
    rel = filepath.replace("\\", "/").lower()
    name = Path(filepath).name
    if not name.lower().startswith("ke-"):
        return []
    if "08_knowledge/" not in rel and "knowledge" not in rel:
        return []
    violations: list[NamingViolation] = []
    if _KE_NUMERIC_TITLE_RE.match(name.lower()):
        violations.append(
            NamingViolation(
                rule="N-12",
                message=f"KE 条目标题为纯数字(无语义): {name} (期望: ke-NNN-snake_case_title.md)",
                filepath=filepath,
            )
        )
        return violations
    if not _KE_PATTERN.match(name.lower()):
        violations.append(
            NamingViolation(
                rule="N-12",
                message=f"KE 条目文件名格式不合规: {name} (期望: ke-NNN-snake_case_title.md, NNN=三位数字)",
                filepath=filepath,
            )
        )
    return violations


# ---------------------------------------------------------------------------
# N-13: YAML/JSON/MD 文件名 snake_case 合规检测
# ---------------------------------------------------------------------------

_SNAKE_CASE_DATA_RE = re.compile(r"^[a-z][a-z0-9_]*\.(yaml|yml|json|md)$")
_DATA_FILE_EXEMPT_NAMES: set[str] = {
    "AGENTS.md",
    "Makefile",
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "PKG-INFO",
    "SOURCES.txt",
    ".pre_commit-config.yaml",
    "docker-compose.yml",
    "docker-compose.yaml",
    # HuggingFace model files (external convention, must not rename)
    "tokenizer_config.json",
    "special_tokens_map.json",
    "config.json",
    "sentence_bert_config.json",
    "config_sentence_transformers.json",
    "tokenizer.json",
    "vocab.txt",
    "model.safetensors",
}

# Auto-generated timestamp file pattern (e.g. secret_baseline_2026-01-15T12-00-00.json, sec_leak_20260611T212859Z.json)
_AUTO_GENERATED_TS_RE = re.compile(r"(_\d{4}-\d{2}-\d{2}[T-]|_\d{8}T\d{6}Z)")


def _check_n13_data_file_naming(filepath: str) -> list[NamingViolation]:
    """YAML/JSON/MD 数据文件名必须使用 snake_case（小写+下划线）。
    强化: 禁止大写字母/空格/连字符(除白名单); .trae/ 和 config/ 豁免;
          dot-prefix 文件豁免; 前导下划线注册/模板文件豁免
    """
    name = Path(filepath).name
    if name in _DATA_FILE_EXEMPT_NAMES:
        return []
    if not name.endswith((".yaml", ".yml", ".json", ".md")):
        return []
    if name.startswith("."):
        return []
    rel = filepath.replace("\\", "/").lower()
    for prefix in (".trae/", "config/", ".github/", "models/", "logs/"):
        if prefix in rel:
            return []
    # 知识条目 ke-* / KE-*、session_logs、kbg-* (KBG决策记录) 豁免（不区分大小写）
    lower_name = name.lower()
    if lower_name.startswith("ke-") or lower_name.startswith("session-") or lower_name.startswith("kbg-"):
        return []
    # 任务ID文件豁免（TASK-OPS-2026062103.md 等格式）
    if lower_name.startswith("task-"):
        return []
    # 决策记忆ID文件豁免（DM-100252.md 等格式）
    if lower_name.startswith("dm-"):
        return []
    # docs/ 下双数字前缀域文档豁免（01_d_infra_ops.md 等架构域文档）
    if (rel.startswith("docs/") or "/docs/" in rel) and re.match(r"^\d{2}_", name):
        return []
    stem = Path(filepath).stem
    if stem.startswith("_"):
        return []
    # Auto-generated timestamp files (e.g. secret_baseline_2026-01-15T..., score_snapshot_2026-...)
    if _AUTO_GENERATED_TS_RE.search(name):
        return []
    if _SNAKE_CASE_DATA_RE.match(name):
        return []
    reasons = []
    if re.search(r"[A-Z]", name):
        reasons.append("含大写字母")
    if " " in name:
        reasons.append("含空格")
    if "-" in name.replace(".yaml", "").replace(".yml", "").replace(".json", "").replace(".md", ""):
        reasons.append("含连字符(kebab_case)")
    if not reasons:
        reasons.append("不符合 snake_case")
    return [
        NamingViolation(
            rule="N-13",
            message=f"YAML/JSON/MD 文件名不符合 snake_case({', '.join(reasons)}): {name}",
            filepath=filepath,
        )
    ]


# ---------------------------------------------------------------------------
# N-14: __init__.py 必须定义 __all__
# ---------------------------------------------------------------------------

_ALL_RE = re.compile(r"^__all__\s*[:=]", re.MULTILINE)
_INIT_EXEMPT_DIRS: set[str] = {
    "tests",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
}


def _check_n14_init_has_all(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """Python __init__.py 必须定义 __all__（RULE-TWO 反孤儿：无 __all__ = 导入不可发现）。
    强化: tests/ 和虚拟环境豁免; 空文件(0字节)豁免
    """
    name = Path(filepath).name
    if name != "__init__.py":
        return []
    rel = filepath.replace("\\", "/").lower()
    for exempt in _INIT_EXEMPT_DIRS:
        if exempt in rel:
            return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = _read_text_bom_safe(abspath)
    except Exception:
        return []
    if not content.strip():
        return []
    if _ALL_RE.search(content):
        return []
    return [NamingViolation(rule="N-14", message=f"__init__.py 缺少 __all__ 定义: {filepath}", filepath=filepath)]


# ---------------------------------------------------------------------------
# N-15: BLUEPRINT 头部路径必须存在
# ---------------------------------------------------------------------------

_BLUEPRINT_HEADER_RE = re.compile(r"^\s*#?\s*\[BLUEPRINT\]\s+(\S+)\s*\|\s*(\S+)\s*\|", re.MULTILINE)


def _check_n15_blueprint_path_exists(
    filepath: str, abspath: Path | None = None, project_root: Path | None = None
) -> list[NamingViolation]:
    """Python 文件 [BLUEPRINT] 头部声明的蓝图路径必须存在。
    强化: 仅检查 .py 文件; 路径相对于项目根; 不存在则 P0 阻断
    """
    name = Path(filepath).name
    if not name.endswith(".py"):
        return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = _read_text_bom_safe(abspath)
    except Exception:
        return []
    match = _BLUEPRINT_HEADER_RE.search(content)
    if not match:
        return []
    blueprint_path = match.group(2).strip()
    if project_root is None:
        project_root = Path.cwd()
    full_path = project_root / blueprint_path
    if full_path.exists():
        return []
    return [
        NamingViolation(
            rule="N-15", message=f"BLUEPRINT 头部路径不存在: {blueprint_path} (声明在 {name})", filepath=filepath
        )
    ]


# ---------------------------------------------------------------------------
# N-16: 文件名项目内唯一性（tests/ + docs/）
# ---------------------------------------------------------------------------

# N-16 豁免清单真源: trae_028_doc_structure_naming.yaml §gov_doc_003_filename_uniqueness.n16_config
# 本模块直接消费 YAML 真源(非同步复制),YAML改即生效。禁止在此硬编码新豁免项。
# fail-open: YAML不存在/解析失败/n16_config字段不完整时回退到下方硬编码值,防破坏性故障。
_N16_YAML_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "rules" / "trae_028_doc_structure_naming.yaml"
)

# fail-open 回退值(与 trae_028.yaml v1.5.0 n16_config 保持一致;仅在YAML不可达时使用)
_N16_TESTS_EXEMPT_NAMES_FALLBACK: frozenset[str] = frozenset({"conftest.py", "__init__.py"})
_N16_DOCS_EXEMPT_NAMES_EXTRA_FALLBACK: frozenset[str] = frozenset({
    "index.md", "blueprint.md", "readme.md", "changelog.md", "spec.md", ".gitkeep", "_index.yaml",
})
_N16_DOCS_SKIP_DIRS_FALLBACK: set[str] = {
    "_DO_NOT_USE_old_tree", "_archive", "_backups", "session_logs",
}
# 临时沙箱目录前缀回退(目录名前缀匹配,os.walk剪枝);真源在 trae_028.yaml §n16_config.skip_dir_prefixes
_N16_SKIP_DIR_PREFIXES_FALLBACK: set[str] = {
    "_tmp_",  # 覆盖 tests/_tmp_redblue_f2/ 等并发红蓝对抗临时沙箱
}


def _load_n16_exemptions_from_yaml() -> tuple[frozenset[str], frozenset[str], set[str], set[str]]:
    """从 trae_028.yaml §gov_doc_003_filename_uniqueness.n16_config 加载豁免清单。

    返回 (tests_exempt, docs_extra_exempt, docs_skip_dirs, skip_dir_prefixes)。
    继承关系在调用方体现: _N16_DOCS_EXEMPT_NAMES = tests_exempt | docs_extra_exempt。
    fail-open: 文件缺失/解析失败/清单为空/类型不合规(非list或含非str元素) → 整体回退到硬编码值,防检测失效或污染。
    """
    try:
        data = yaml.safe_load(_N16_YAML_PATH.read_text(encoding="utf-8"))
        cfg = (
            data.get("sections", {})
            .get("gov_doc_003_filename_uniqueness", {})
            .get("n16_config", {})
        )
        tests_raw = cfg.get("exempt_names_tests", [])
        docs_raw = cfg.get("exempt_names_docs_extra", [])
        skip_raw = cfg.get("skip_dirs_docs", [])
        prefixes_raw = cfg.get("skip_dir_prefixes", [])
        # 类型严格校验: 必须是非空list且元素全为str——任一不满足视为损坏→回退
        # 防 string 标量被迭代成 char set / int 等非str 元素污染豁免集合
        for lst in (tests_raw, docs_raw, skip_raw, prefixes_raw):
            if not isinstance(lst, list) or not lst or not all(isinstance(x, str) for x in lst):
                raise ValueError("n16_config 类型/内容不合规")
        # skip_dir_prefixes 额外校验: 空串 "" 使 d.startswith("") 恒真 → 全剪枝 → N-16 静默失效(P1漏洞,红蓝R3)
        if any(x == "" for x in prefixes_raw):
            raise ValueError("n16_config.skip_dir_prefixes 含空字符串")
        return frozenset(tests_raw), frozenset(docs_raw), set(skip_raw), set(prefixes_raw)
    except Exception:
        return (
            _N16_TESTS_EXEMPT_NAMES_FALLBACK,
            _N16_DOCS_EXEMPT_NAMES_EXTRA_FALLBACK,
            _N16_DOCS_SKIP_DIRS_FALLBACK,
            _N16_SKIP_DIR_PREFIXES_FALLBACK,
        )


# 模块级加载一次(YAML是项目内稳定文件,import时读取;commit每次调用不重复解析)
(
    _N16_TESTS_EXEMPT_RAW,
    _N16_DOCS_EXEMPT_EXTRA_RAW,
    _N16_DOCS_SKIP_DIRS_RAW,
    _N16_SKIP_DIR_PREFIXES_RAW,
) = _load_n16_exemptions_from_yaml()

# tests/ 豁免：约定俗成的跨目录同名文件（基线清单，docs/ 继承此清单）
_N16_TESTS_EXEMPT_NAMES: frozenset[str] = _N16_TESTS_EXEMPT_RAW

# docs/ 豁免：继承 tests/ 基线 + docs 专属豁免（基于实际扫描校准）
#   index.md (169x) / blueprint.md (59x) / readme.md (4x) / changelog.md (2x) /
#   spec.md (2x) / .gitkeep (3x) / _index.yaml (2x)
# 注：用继承关系消除 __init__.py/conftest.py 的同步复制（RULE-ONE 真源唯一）
#     继承关系在代码侧体现: tests | docs_extra,真源值在YAML n16_config
_N16_DOCS_EXEMPT_NAMES: frozenset[str] = _N16_TESTS_EXEMPT_NAMES | _N16_DOCS_EXEMPT_EXTRA_RAW

# docs/ 跳过的目录（运行时产物、归档、备份——不纳入同名检查）
_N16_DOCS_SKIP_DIRS: set[str] = _N16_DOCS_SKIP_DIRS_RAW

# 临时沙箱目录前缀(tests/ + docs/ 通用,os.walk按目录名前缀剪枝)
# 覆盖 tests/_tmp_redblue_f2/ 等并发红蓝对抗沙箱(清理晚于commit,防撞名误阻断);真源在YAML n16_config.skip_dir_prefixes
_N16_SKIP_DIR_PREFIXES: set[str] = _N16_SKIP_DIR_PREFIXES_RAW

# src/ basename 豁免清单（P0-1 防再生门禁）
# __init__.py 是 Python 包标识，跨目录同名合法；conftest.py 是 pytest 约定；
# __main__.py 是 python -m 入口约定（多域各需自己的入口）。
# 其余同名一律违规——责任唯一，真源唯一（trae_060 §2 原则①）。
_N16_SRC_EXEMPT_NAMES: frozenset[str] = _N16_TESTS_EXEMPT_NAMES | frozenset({"__main__.py"})


def _check_basename_uniqueness(
    scan_root: Path,
    project_root: Path,
    exempt_names: set[str],
    skip_dirs: set[str] | None = None,
    skip_dir_prefixes: set[str] | None = None,
    file_filter=None,
    rule_id: str = "N-16",
    label: str = "文件名",
) -> list[NamingViolation]:
    """通用 basename 唯一性检测——扫描 scan_root 下所有文件，basename 相同视为违规。

    Args:
        scan_root: 要扫描的目录（如 tests/ 或 docs/）
        project_root: 项目根（用于计算相对路径）
        exempt_names: 豁免的 basename 集合（如 index.md / __init__.py）
        skip_dirs: 要跳过的子目录名集合(精确匹配,如 _archive / session_logs)
        skip_dir_prefixes: 要跳过的子目录名前缀集合(前缀匹配,如 _tmp_;os.walk剪枝,覆盖 tests/_tmp_redblue_f2/ 等临时沙箱)
        file_filter: 可选的文件名过滤器，返回 True 才纳入检查（如 lambda n: n.startswith("test_")）
        rule_id: 违规规则 ID
        label: 违规消息中的标签（如 "测试文件名" / "文档文件名"）
    """
    if not scan_root.is_dir():
        return []

    from collections import defaultdict

    name_to_paths: dict[str, list[str]] = defaultdict(list)
    for root, dirs, files in os.walk(scan_root):
        if skip_dirs:
            dirs[:] = [d for d in dirs if d not in skip_dirs]
        if skip_dir_prefixes:
            dirs[:] = [d for d in dirs if not any(d.startswith(p) for p in skip_dir_prefixes)]
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for f in files:
            if f in exempt_names:
                continue
            if file_filter and not file_filter(f):
                continue
            full = Path(root) / f
            rel = str(full.relative_to(project_root)).replace("\\", "/")
            name_to_paths[f].append(rel)

    violations: list[NamingViolation] = []
    for basename, paths in sorted(name_to_paths.items()):
        if len(paths) > 1:
            for p in paths:
                violations.append(
                    NamingViolation(
                        rule=rule_id,
                        message=f"{label}不唯一: {basename} (共{len(paths)}处: {', '.join(paths)})",
                        filepath=p,
                    )
                )
    return violations


def check_test_name_uniqueness(project_root: Path | None = None) -> list[NamingViolation]:
    """扫描 tests/ 下所有 test_*.py，同名文件（basename 相同）视为违规。

    豁免: conftest.py / __init__.py（这些文件在不同目录下同名是正常的）。
    修复方式: 按 test_{module}_{domain}.py 格式加入目录层级后缀。
    """
    if project_root is None:
        project_root = Path.cwd()
    return _check_basename_uniqueness(
        scan_root=project_root / "tests",
        project_root=project_root,
        exempt_names=_N16_TESTS_EXEMPT_NAMES,
        skip_dir_prefixes=_N16_SKIP_DIR_PREFIXES,
        file_filter=lambda n: n.startswith("test_"),
        label="测试文件名",
    )


def check_docs_name_uniqueness(project_root: Path | None = None) -> list[NamingViolation]:
    """扫描 docs/ 下所有文件，同名文件（basename 相同）视为违规。

    豁免: 约定俗成的跨目录同名文件（index.md / blueprint.md / readme.md /
    changelog.md / spec.md / .gitkeep / _index.yaml / __init__.py / conftest.py）。
    跳过: _archive / _backups / session_logs / _DO_NOT_USE_old_tree（运行时产物/归档）。
    """
    if project_root is None:
        project_root = Path.cwd()
    return _check_basename_uniqueness(
        scan_root=project_root / "docs",
        project_root=project_root,
        exempt_names=_N16_DOCS_EXEMPT_NAMES,
        skip_dirs=_N16_DOCS_SKIP_DIRS,
        skip_dir_prefixes=_N16_SKIP_DIR_PREFIXES,
        label="文档文件名",
    )


def check_src_name_uniqueness(project_root: Path | None = None) -> list[NamingViolation]:
    """扫描 src/zephyr/ 下所有 .py，同名文件（basename 相同）视为违规。

    P0-1 防再生门禁：阻断 AI 跨域复刻同名模块（病根1）。
    N-16 当初因"499 个 __init__.py"放弃 src/ 检测——解法是 __init__.py 已在豁免清单，
    剩余同名才是真冲突（如 wave_generator 4 份副本）。

    豁免: __init__.py（包标识）、conftest.py（pytest）、__main__.py（python -m 入口）。
    跳过: __pycache__ / ._archive 等运行时产物。
    """
    if project_root is None:
        project_root = Path.cwd()
    return _check_basename_uniqueness(
        scan_root=project_root / "src" / "zephyr",
        project_root=project_root,
        exempt_names=_N16_SRC_EXEMPT_NAMES,
        skip_dirs=_N16_DOCS_SKIP_DIRS,  # 复用 _archive 等跳过规则
        skip_dir_prefixes=_N16_SKIP_DIR_PREFIXES,
        file_filter=lambda n: n.endswith(".py"),
        label="源码文件名",
    )


def check_filename_uniqueness_all(
    project_root: Path | None = None,
    include_src: bool = False,
) -> list[NamingViolation]:
    """N-16 统一入口——检测 tests/ + docs/ 下的文件名唯一性。

    Args:
        include_src: 是否包含 src/zephyr/ 检测。默认 False（避免存量 163 影子副本
            阻断 commit）；设 True 用于诊断全量存量（如治理脚本手动调用）。
            增量检测（check_new_files_naming）默认覆盖 src/，阻断新增同名。
    """
    if project_root is None:
        project_root = Path.cwd()
    violations: list[NamingViolation] = []
    violations.extend(check_test_name_uniqueness(project_root))
    violations.extend(check_docs_name_uniqueness(project_root))
    if include_src:
        violations.extend(check_src_name_uniqueness(project_root))
    return violations


def check_new_files_naming(
    new_files: list[str],
    project_root: Path | None = None,
    scopes: tuple[str, ...] | None = ("tests", "docs", "src"),
) -> list[NamingViolation]:
    """增量 N-16 检查（真源唯一）：只检查新文件是否与已跟踪文件同名冲突。

    Args:
        new_files: 新文件路径列表（相对 project_root 或绝对路径）。
        project_root: 项目根。
        scopes: N-16 覆盖的顶级目录元组。默认 ("tests", "docs") 向后兼容；
            None 表示全库覆盖（所有目录）。
            跨包合法同名（__init__.py/conftest.py）由豁免清单处理。

    用 ``git ls-files`` 构建已跟踪文件基线（避免 os.walk 扫描未跟踪 WIP，
    防多 session 临时文件误阻断），只检测新文件是否引入冲突（不阻断历史遗留）。

    治本（向内收 v2）：N-16 检查逻辑真源唯一归本函数。GitCommitGateway 通过
    subprocess 调用 ``--check-new`` 模式，删除 gateway 内的自实现
    ``_check_naming_uniqueness`` + ``_load_n16_exempt_names``，消除真源分裂。

    Args:
        new_files: 新文件路径列表（相对 project_root 或绝对路径）。
        project_root: 项目根。

    Returns:
        NamingViolation 列表（空表示通过）。
    """
    import subprocess
    from collections import defaultdict

    if project_root is None:
        project_root = REPO_ROOT

    # scope 过滤：None=全库覆盖，tuple=只检查指定目录
    if scopes is None:
        scope_prefixes: tuple[str, ...] = ()  # 空 = 不过滤
    else:
        scope_prefixes = tuple(f"{s}/" for s in scopes)
    new_rel_files: list[str] = []
    for f in new_files:
        p = Path(f)
        if not p.is_absolute():
            p = project_root / f
        try:
            rel = p.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError:
            continue  # 不在项目内
        if not scope_prefixes or rel.startswith(scope_prefixes):
            new_rel_files.append(rel)

    if not new_rel_files:
        return []

    # 豁免清单（真源：trae_028.yaml §n16_config，模块级常量已动态加载）
    # 跨 scope 统一豁免：__init__.py/conftest.py（包标识/pytest约定）+ __main__.py（python -m入口）+ docs约定同名
    exempt = _N16_TESTS_EXEMPT_NAMES | _N16_DOCS_EXEMPT_NAMES | frozenset({"__main__.py"})

    # 用 git ls-files 构建已跟踪文件基线（只已跟踪文件，排除未跟踪 WIP）
    try:
        ls_args = ["git", "ls-files"]
        if scope_prefixes:
            ls_args.extend(list(scope_prefixes))
        result = subprocess.run(
            ls_args,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root),
        )
        tracked_files = [f for f in result.stdout.strip().splitlines() if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []  # fail-open：git 不可用时不阻断 commit

    tracked_basename_to_paths: dict[str, list[str]] = defaultdict(list)
    for rel_path in tracked_files:
        basename = os.path.basename(rel_path)
        if basename in exempt:
            continue
        # normcase 归一 basename 作 key：Windows 下 on-disk 与 git index 大小写不一致时
        # 确保同名文件正确匹配（治本·与 _is_new_file 一致性归一）
        tracked_basename_to_paths[os.path.normcase(basename)].append(rel_path.replace("\\", "/"))

    violations: list[NamingViolation] = []
    committed_basenames: dict[str, str] = {}  # basename → committed_rel_path

    for rel in new_rel_files:
        basename = os.path.basename(rel)
        if basename in exempt:
            continue

        # normcase 归一比较：防止 on-disk vs git index 大小写不一致导致修改文件
        # 被误判为新增后无法自排除自身 git-index 条目（治本·大小写一致性）
        nc_rel = os.path.normcase(rel)
        nc_basename = os.path.normcase(basename)

        # 冲突检测 1：与已跟踪文件冲突
        if nc_basename in tracked_basename_to_paths:
            existing = [p for p in tracked_basename_to_paths[nc_basename] if os.path.normcase(p) != nc_rel]
            if existing:
                violations.append(NamingViolation(
                    rule="N-16",
                    message=f"文件名不唯一: {basename} (新增: {rel}, 已有: {', '.join(existing)})",
                    filepath=rel,
                ))

        # 冲突检测 2：本次提交内部冲突
        if basename in committed_basenames:
            violations.append(NamingViolation(
                rule="N-16",
                message=f"文件名不唯一: {basename} (本次提交内冲突: {rel} vs {committed_basenames[basename]})",
                filepath=rel,
            ))
        committed_basenames[basename] = rel

    return violations


def check_new_files_full(
    new_files: list[str],
    project_root: Path | None = None,
) -> list[NamingViolation]:
    """增量全量命名硬阻断检查（治本·全库覆盖）：GitCommitGateway 内嵌，绕不过 --no-verify。

    对新增文件做 N-01~N-17 风格硬阻断 + N-16 唯一性硬阻断（全库覆盖）。
    对修改文件做历史豁免检查（只阻断本次修改新引入的违规）。

    设计（三个治本闭环）：
    1. 全库覆盖：所有目录的文件都查命名（无 scope 限制）
    2. 全维度检测：新增文件 N-01~N-17 风格 + 新增文件 N-16 唯一性 + 修改文件历史豁免
    3. 绕不过：GitCommitGateway 内嵌，--no-verify 绕过 pre-commit 但绕不过 gateway

    新增 vs 修改区分（历史豁免，只阻断新引入的违规）：
    - 新增文件（git ls-files 未跟踪）：N-16 唯一性 + check_file 全量风格检查
    - 修改文件（git ls-files 已跟踪）：历史豁免——对 HEAD 版本和工作区版本各跑
      check_file，取差集（只阻断本次修改新引入的违规，HEAD 中已有的违规不阻断）
      filename 级规则(N-01~N-05,N-08,N-11~N-13)对修改文件天然全豁免（文件名不变）；
      content 级规则(N-06,N-07,N-14,N-15,N-17)只阻断修改引入的新违规

    Args:
        new_files: 本次 commit 的文件路径列表。
        project_root: 项目根。

    Returns:
        NamingViolation 列表（空表示通过）。
    """
    if project_root is None:
        project_root = REPO_ROOT

    import subprocess  # 局部 import（与 check_new_files_naming 一致，避免模块级依赖）

    violations: list[NamingViolation] = []

    # 确定哪些是新增文件（未被 git 跟踪）vs 修改文件（已被 git 跟踪）
    # 用 git ls-files 而非 git diff --cached --diff-filter=A：gateway 在 git add
    # 之前调用此检查，staged 区为空，diff-filter=A 无法识别新增文件。
    # git ls-files 判断文件是否已跟踪：未跟踪 = 新增，已跟踪 = 修改。
    try:
        tracked_result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, check=True,
            cwd=str(project_root),
        )
        tracked_set = {os.path.normcase(f.replace("\\", "/")) for f in tracked_result.stdout.strip().splitlines() if f}
    except (subprocess.CalledProcessError, FileNotFoundError):
        tracked_set = None  # fail-open: git 不可用时不阻断

    def _is_new_file(rel_path: str) -> bool:
        """文件是否为新增（未被 git 跟踪）。fail-open: git 不可用时返回 False（不阻断）。

        大小写归一：Windows 下 on-disk 物理大小写与 git index 大小写可能不一致，
        用 os.path.normcase() 归一后比较，与 GitCommitGateway._is_git_tracked 的
        :(icase) 模式一致（治本·一致性归一，修复 N-16 对修改文件误报历史冲突）。
        """
        if tracked_set is None:
            return False
        return os.path.normcase(rel_path) not in tracked_set

    # 1. N-16 唯一性检查（仅新增文件）
    #    新文件范围：tests/+docs/（N-16 设计：src/ 包隔离不覆盖，见 §n16_config 注释）
    #    基线范围：全库（scopes=None → git ls-files 全库，含 src/ 已跟踪文件——跨域同名检测）
    #    避免跨包合法同名误报（如 ops/protocols.py vs shared/contracts/protocols.py）
    _N16_NEW_FILE_SCOPES = ("tests/", "docs/")
    added_files_for_n16: list[str] = []
    for f in new_files:
        p = Path(f)
        if not p.is_absolute():
            p = project_root / f
        try:
            rel = p.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError:
            continue
        if _is_new_file(rel) and rel.startswith(_N16_NEW_FILE_SCOPES):
            added_files_for_n16.append(f)
    if added_files_for_n16:
        violations.extend(check_new_files_naming(
            added_files_for_n16, project_root, scopes=None
        ))

    # 2. N-01~N-17 风格检查
    # - 新增文件：全量检查
    # - 修改文件：历史豁免——只阻断本次修改引入的新违规（HEAD 中已有的违规不阻断）
    #   实现：对 HEAD 版本和工作区版本各跑一次 check_file，取差集（新增违规）
    #   filename 级规则(N-01~N-05,N-08,N-11~N-13)对修改文件天然全豁免（文件名不变→HEAD 和工作区结果相同→差集为空）
    #   content 级规则(N-06,N-07,N-14,N-15,N-17)只阻断修改引入的新违规
    import tempfile
    for f in new_files:
        p = Path(f)
        if not p.is_absolute():
            p = project_root / f
        try:
            rel = p.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError:
            continue
        if _is_path_exempt(rel):
            continue
        abspath = project_root / rel
        if not (abspath.exists() and abspath.is_file()):
            continue

        if _is_new_file(rel):
            # 新增文件：全量检查
            violations.extend(check_file(rel, abspath, project_root))
        else:
            # 修改文件：历史豁免（只阻断新引入的违规）
            try:
                head_result = subprocess.run(
                    ["git", "show", f"HEAD:{rel}"],
                    capture_output=True, cwd=str(project_root),
                )
                if head_result.returncode != 0:
                    continue  # HEAD 中无此文件（新增？），跳过
                # 写 HEAD 内容到临时文件，跑 check_file 获取基线违规
                with tempfile.NamedTemporaryFile(
                    mode="wb", suffix=Path(rel).suffix, delete=False
                ) as tmp:
                    tmp.write(head_result.stdout)
                    tmp_path = Path(tmp.name)
                try:
                    head_violations = check_file(rel, tmp_path, project_root)
                finally:
                    tmp_path.unlink(missing_ok=True)
                # 工作区版本违规
                current_violations = check_file(rel, abspath, project_root)
                # 取差集：只报告 HEAD 中没有的违规（新引入的）
                head_keys = {(v.rule, v.message) for v in head_violations}
                for v in current_violations:
                    if (v.rule, v.message) not in head_keys:
                        violations.append(v)
            except Exception:
                # git show 失败或临时文件问题 → fail-open（不阻断修改）
                pass

    return violations


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
    if "session_logs/" in rel:
        return True
    if "session_logs/" in rel:
        return True
    if "docs/19_development_workspace/session_logs/" in rel:
        return True
    if "_archive/" in rel:
        return True
    if "_backups/" in rel:
        return True
    return False


# ---------------------------------------------------------------------------
# N-17: blueprint_id 域片段与 [DOMAIN] 一致性检测（裁定#206 B-5 派生范式）
# ---------------------------------------------------------------------------

# 数字序号制 module_id（层代码+纯数字序号，如 MOD-L00-001 / MOD-INF-005），不含域片段，跳过派生校验
_MODULE_ID_NUMERIC_SEQ_RE = re.compile(r"^MOD-[A-Z]{2,4}-\d+$")

_BP_HEADER_RE = re.compile(r"^\s*#\s*\[BLUEPRINT\]\s+(\S+)", re.MULTILINE)
_DOMAIN_HEADER_RE = re.compile(r"^\s*#\s*\[DOMAIN\]\s+(\S+)", re.MULTILINE)


def _check_n17_blueprint_domain_consistency(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """N-17: blueprint_id 域片段必须与 [DOMAIN] domain_id 一致（裁定#206 B-5 派生范式）。

    派生关系：blueprint_id 的域片段派生自 domain_id（去掉 D- 前缀）。
    数字序号制 module_id（MOD-L00-001 / MOD-INF-005）不含域片段，跳过校验。
    仅 .py 文件头部含 [BLUEPRINT]+[DOMAIN] 时校验。

    BOM 治本（2026-06-28）：用 utf-8-sig 自动剥离 BOM。HEAD 版本部分 .py 文件含 BOM
    （\\ufeff），导致 ^\\s*# 正则在第一行匹配失败 → bp_match=None → N-17 不触发 →
    历史豁免差集失效 → 工作区版本被误判为"新引入违规"。utf-8-sig 让 HEAD 和工作区
    版本解析一致，历史豁免差集正确计算。
    """
    name = Path(filepath).name
    if not name.endswith(".py"):
        return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = _read_text_bom_safe(abspath)
    except Exception:
        return []

    bp_match = _BP_HEADER_RE.search(content)
    dom_match = _DOMAIN_HEADER_RE.search(content)
    if not bp_match or not dom_match:
        return []

    blueprint_id = bp_match.group(1).strip()
    domain_id = dom_match.group(1).strip()

    # 提取 blueprint_id 的域片段：去掉 MOD- 前缀，去掉末尾 -{数字} 序号
    bp_domain_fragment = blueprint_id
    if bp_domain_fragment.startswith("MOD-"):
        bp_domain_fragment = bp_domain_fragment[4:]
    bp_domain_fragment = re.sub(r"-\d+$", "", bp_domain_fragment)

    # 提取 domain_id 的域片段：去掉 D- 或 D_ 前缀
    # （D_ 为域ID连字符→下划线迁移后的新格式，两种格式都需支持）
    dom_domain_fragment = domain_id
    if dom_domain_fragment.startswith(("D-", "D_")):
        dom_domain_fragment = dom_domain_fragment[2:]

    # token 化（按 _ 和 - 分割），过滤短 token（长度<3，避免短代码误匹配）
    bp_tokens = {t for t in re.split(r"[_-]", bp_domain_fragment) if len(t) >= 3}
    dom_tokens = {t for t in re.split(r"[_-]", dom_domain_fragment) if len(t) >= 3}

    # 只有当两者有共享 token 时才校验（说明 blueprint_id 包含域片段，是派生标识符）
    # 数字序号制 module_id（MOD-L00-001/MOD-INF-005/MOD-MASTER_BLUEPRINT）不包含域片段，
    # 无共享 token，自动跳过（module_id 体系问题为阶段 E 议题，裁定#206 B-4）
    if not (bp_tokens & dom_tokens):
        return []

    # 校验域片段一致性（检测改名残留，如 MOD-SIGNAL_ASHARE vs D_ASHARE_SIGNAL）
    if bp_domain_fragment != dom_domain_fragment:
        return [
            NamingViolation(
                rule="N-17",
                message=(
                    f"blueprint_id 域片段与 [DOMAIN] 不一致: blueprint_id={blueprint_id}"
                    f"(域片段={bp_domain_fragment}) vs domain_id={domain_id}"
                    f"(域片段={dom_domain_fragment})"
                ),
                filepath=filepath,
            )
        ]
    return []


# ---------------------------------------------------------------------------
# BOM 安全读取公共入口（P0-A 彻底化治本，2026-06-28）
# ---------------------------------------------------------------------------
# 根因：HEAD 版本部分 .py 文件含 BOM（\ufeff），导致锚定行首的正则
# （如 N-15 `^\s*#?\s*\[BLUEPRINT\]`、N-17 `^\s*#\s*\[BLUEPRINT\]`）匹配失败，
# HEAD 版本 violations=0，工作区版本正常触发，历史豁免差集非空 → 误阻断提交。
# utf-8-sig 自动剥离 BOM，让 HEAD 和工作区版本解析一致，差集正确计算。
# 本函数是所有 N-* 检查读取 .py 文件的唯一入口，禁止再散用 read_text(utf-8)。


def _read_text_bom_safe(abspath: Path) -> str:
    """读取文件内容，自动剥离 BOM（BOM 脆弱性统一治本入口）。

    所有 N-* 检查读取 .py 文件必须走本函数，禁止散用 abspath.read_text(utf-8)。
    见 2026-06-28 N-17 BOM 治本 + P0-A 彻底化（5 处脆弱 read_text 收拢）。
    """
    return abspath.read_text(encoding="utf-8-sig", errors="replace")


# ---------------------------------------------------------------------------
# 统一入口
# ---------------------------------------------------------------------------


def check_file(filepath: str, abspath: Path | None = None, project_root: Path | None = None) -> list[NamingViolation]:
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
    violations.extend(_check_n08_python_snake_case(filepath))
    violations.extend(_check_n11_doctype_suffix(filepath, abspath))
    violations.extend(_check_n12_ke_naming(filepath))
    violations.extend(_check_n13_data_file_naming(filepath))
    violations.extend(_check_n14_init_has_all(filepath, abspath))
    violations.extend(_check_n15_blueprint_path_exists(filepath, abspath, project_root))
    violations.extend(_check_n17_blueprint_domain_consistency(filepath, abspath))
    return violations


def check_dir(dirpath: str) -> list[NamingViolation]:
    """Check directory naming compliance."""
    if _is_path_exempt(dirpath):
        return []
    violations: list[NamingViolation] = []
    violations.extend(_check_n09_dir_spaces(dirpath))
    violations.extend(_check_n10_dir_naming(dirpath))
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


def _validate_ssot_linkage() -> tuple[bool, str]:
    """裁定#208 R4: 校验 SSoT(trae_028)与脚本双轨正则机械联动一致。

    防 SSoT 修订后 enforcement 脚本未同步（AI 编程社区 enforcement gap）。
    独立模式（--validate-ssot），不扫描文件，仅校验 SSoT 文件与脚本常量一致性。
    """
    ssot_path = (
        REPO_ROOT
        / "docs" / "01_policies_and_standards" / "rules" / "trae_028_doc_structure_naming.yaml"
    )
    if not ssot_path.exists():
        return False, f"❌ SSoT 文件不存在: {ssot_path}"
    try:
        content = ssot_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"❌ SSoT 读取失败: {e}"

    # 1. version 字段读取（用于成功消息可追溯性报告；下界校验已删除——版本号只升不降
    #    使 >= 1.3.0 永真为死代码；保留则 (1,3,0) 在被测函数+测试双处硬编码，真源缺位，
    #    违背真源唯一原则。双轨制 enforcement 由 check 2 正则定义存在性兜底；YAML condition
    #    文本侧的语义校验交由 validate_ssot.py GATE-SSOT 覆盖，避免关键词硬编码形成第二真源）
    vm = re.search(r"^version:\s*['\"]?(\d+)\.(\d+)\.(\d+)", content, re.MULTILINE)
    if not vm:
        return False, "❌ SSoT 未找到 version 字段"
    ver = (int(vm.group(1)), int(vm.group(2)), int(vm.group(3)))

    # 2. 脚本双轨正则已定义（编译期已校验，此处 sanity check 防常量被误删）
    # R2 治本修订（2026-07-05）：_MODULE_ID_D_PREFIX_RE 已废弃，
    # 替换为 _SUBMODULE_ID_RE（submodule_id 校验专用，见 trae_028 gov_doc_009）
    regexes = {
        "_MODULE_ID_LAYER_MASTER_RE": _MODULE_ID_LAYER_MASTER_RE,
        "_MODULE_ID_DOMAIN_DERIVED_RE": _MODULE_ID_DOMAIN_DERIVED_RE,
        "_MODULE_ID_SHARED_RE": _MODULE_ID_SHARED_RE,
        "_SUBMODULE_ID_RE": _SUBMODULE_ID_RE,
    }
    undefined = [name for name, rx in regexes.items() if rx is None]
    if undefined:
        return False, f"❌ 脚本双轨正则未定义: {undefined}"

    # 3. N-16 fallback 与 YAML n16_config 一致性校验（防 fallback 过时漂移）
    #    fallback 是 YAML 不可达时的安全网，其值应与 YAML 保持一致；
    #    若 YAML 加了新豁免项但 fallback 未同步，此处报漂移。
    try:
        ssot_data = yaml.safe_load(content)
        n16_cfg = (
            ssot_data.get("sections", {})
            .get("gov_doc_003_filename_uniqueness", {})
            .get("n16_config", {})
        )
        yaml_tests = frozenset(n16_cfg.get("exempt_names_tests", []))
        yaml_docs_extra = frozenset(n16_cfg.get("exempt_names_docs_extra", []))
        yaml_skip_dirs = set(n16_cfg.get("skip_dirs_docs", []))
        yaml_skip_prefixes = set(n16_cfg.get("skip_dir_prefixes", []))

        drifts: list[str] = []
        if yaml_tests != _N16_TESTS_EXEMPT_NAMES_FALLBACK:
            drifts.append(
                f"exempt_names_tests: YAML={sorted(yaml_tests)} vs fallback={sorted(_N16_TESTS_EXEMPT_NAMES_FALLBACK)}"
            )
        if yaml_docs_extra != _N16_DOCS_EXEMPT_NAMES_EXTRA_FALLBACK:
            drifts.append(
                f"exempt_names_docs_extra: YAML={sorted(yaml_docs_extra)} vs fallback={sorted(_N16_DOCS_EXEMPT_NAMES_EXTRA_FALLBACK)}"
            )
        if yaml_skip_dirs != _N16_DOCS_SKIP_DIRS_FALLBACK:
            drifts.append(
                f"skip_dirs_docs: YAML={sorted(yaml_skip_dirs)} vs fallback={sorted(_N16_DOCS_SKIP_DIRS_FALLBACK)}"
            )
        if yaml_skip_prefixes != _N16_SKIP_DIR_PREFIXES_FALLBACK:
            drifts.append(
                f"skip_dir_prefixes: YAML={sorted(yaml_skip_prefixes)} vs fallback={sorted(_N16_SKIP_DIR_PREFIXES_FALLBACK)}"
            )
        if drifts:
            return False, (
                "❌ N-16 _N16_*_FALLBACK 与 YAML n16_config 不一致（漂移风险，改 YAML 后须同步 fallback）:\n  "
                + "\n  ".join(drifts)
            )
    except Exception as e:
        return False, f"❌ N-16 fallback 一致性校验失败: {e}"

    return True, (
        f"✅ SSoT(trae_028 v{ver[0]}.{ver[1]}.{ver[2]}) 与脚本双轨正则 + N-16 fallback 一致"
    )


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="GATE-11 命名规范门禁")
    parser.add_argument("paths", nargs="*", help="要检查的文件或目录路径（可多个，pre-commit pass_filenames传入）")
    parser.add_argument("--scan", action="store_true", help="扫描整个项目目录")
    parser.add_argument("--staged", action="store_true", help="只检查git暂存区文件")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不阻断")
    parser.add_argument("--validate-ssot", action="store_true", help="校验 SSoT(trae_028)与脚本双轨正则+N-16 fallback 一致性(裁定#208 R4)")
    parser.add_argument(
        "--check-new",
        nargs="*",
        default=None,
        metavar="FILE",
        help="增量 N-16 检查：只检查指定文件是否与已跟踪文件同名冲突（GitCommitGateway subprocess 调用，"
             "git ls-files 基线，不阻断历史遗留）",
    )
    parser.add_argument(
        "--check-new-full",
        nargs="*",
        default=None,
        metavar="FILE",
        help="增量全量命名硬阻断(治本·选项B):新增文件N-01~N-17风格+所有文件N-16唯一性"
             "(覆盖tests/docs/src/scripts),硬阻断绕不过--no-verify。GitCommitGateway内嵌调用",
    )
    args = parser.parse_args()

    # 增量 N-16 检查模式（GitCommitGateway --no-verify 补偿用，真源唯一）
    if args.check_new is not None:
        project_root = REPO_ROOT
        violations = check_new_files_naming(args.check_new, project_root)
        if violations:
            for v in violations:
                print(f"[N-16] {v.message}")
            return EXIT_FINDINGS
        return EXIT_PASS

    # 增量全量命名硬阻断模式（治本·选项B：GitCommitGateway 内嵌，绕不过 --no-verify）
    if args.check_new_full is not None:
        project_root = REPO_ROOT
        violations = check_new_files_full(args.check_new_full, project_root)
        if violations:
            for v in violations:
                print(f"[{v.rule}] {v.message}")
            return EXIT_FINDINGS
        return EXIT_PASS

    # 裁定#208 R4: SSoT 机械联动校验（独立模式，不扫描文件）
    if args.validate_ssot:
        ok, msg = _validate_ssot_linkage()
        print(msg)
        return EXIT_PASS if ok else EXIT_FINDINGS

    all_violations: list[NamingViolation] = []

    if args.staged:
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
                cwd=REPO_ROOT,
            )
            staged_files = [f for f in result.stdout.strip().split("\n") if f]
        except (subprocess.CalledProcessError, FileNotFoundError):
            staged_files = []
        project_root = REPO_ROOT
        for rel_path in staged_files:
            abspath = project_root / rel_path
            if abspath.exists() and abspath.is_file():
                all_violations.extend(check_file(rel_path.replace("\\", "/"), abspath, project_root))
    elif args.scan:
        project_root = REPO_ROOT
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__" and d != "node_modules"]
            rel_root = str(root).replace(str(project_root), "").lstrip("\\/").lstrip("/")
            for d in dirs:
                dirpath = f"{rel_root}/{d}" if rel_root else d
                all_violations.extend(check_dir(dirpath))
            for f in files:
                filepath = f"{rel_root}/{f}" if rel_root else f
                abspath = Path(root) / f
                all_violations.extend(check_file(filepath, abspath, project_root))
        # N-16: 全局检测——文件名唯一性（tests/ + docs/）
        all_violations.extend(check_filename_uniqueness_all(project_root))
    else:
        # 默认模式：检查传入的文件列表（pre-commit pass_filenames），或当前目录
        targets = args.paths if args.paths else ["."]
        # N-16 全局检测不依赖传入文件列表——它是项目级唯一性检查，
        # 在默认模式也必须运行（否则 pre-commit 钩子不会发现同名文件）
        _project_root_for_n16 = REPO_ROOT
        all_violations.extend(check_filename_uniqueness_all(_project_root_for_n16))
        for target_path in targets:
            target = Path(target_path)
            if target.is_dir():
                project_root = target.resolve()
                for root, dirs, files in os.walk(target):
                    dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
                    rel_root = str(root).replace(str(target), "").lstrip("\\/").lstrip("/")
                    for f in files:
                        filepath = f"{rel_root}/{f}" if rel_root else f
                        abspath = Path(root) / f
                        all_violations.extend(check_file(filepath, abspath, project_root))
            else:
                filepath = target_path
                all_violations.extend(check_file(filepath, target))

    # N-16 是新激活规则（文件名唯一性），不受 --warn-only 影响——直接硬阻断
    # N-17 过渡期 warn-only（裁定#208 阶段 E 激活后硬阻断）
    n16_violations = [v for v in all_violations if v.rule == "N-16"]
    n17_violations = [v for v in all_violations if v.rule == "N-17"]
    other_violations = [v for v in all_violations if v.rule not in ("N-16", "N-17")]

    for v in other_violations:
        print(f"[{v.rule}] {v.message}")

    if n16_violations:
        print(f"\n[N-16 BLOCK] 文件名不唯一（硬阻断，不受 --warn-only 影响）:")
        for v in n16_violations:
            print(f"  [N-16] {v.message}")
        print(f"  共 {len(n16_violations)} 个 N-16 阻断违规")

    if n17_violations:
        if args.warn_only:
            print(f"\n[N-17 WARNING] blueprint_id 域片段不一致（过渡期 --warn-only，不阻断；裁定#208 阶段 E 激活后阻断）:")
            for v in n17_violations:
                print(f"  [N-17] {v.message}")
            print(f"  共 {len(n17_violations)} 个 N-17 warning")
        else:
            for v in n17_violations:
                print(f"[N-17] {v.message}")

    # N-16 直接硬阻断（不受 warn_only 影响）；N-17 过渡期 warn-only；其他规则受 warn_only 控制
    blocking_count = len(n16_violations) + len(other_violations) + (len(n17_violations) if not args.warn_only else 0)
    if blocking_count:
        print(f"\n总计 {blocking_count} 个阻断性命名违规")
        return EXIT_FINDINGS if (not args.warn_only or n16_violations) else EXIT_PASS
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
