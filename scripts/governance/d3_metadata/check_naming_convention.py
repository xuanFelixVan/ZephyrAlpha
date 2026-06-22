# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_naming_convention.py | §
# [MODULE] scripts.governance.d3_metadata.check_naming_convention
# [INVARIANTS] N-01~N-15 rules are append-only; whitelist changes require Owner approval
# [MODIFY-GUARD] FILENAME_UPPERCASE_WHITELIST, _DATA_FILE_EXEMPT_NAMES, TECH_VERSION_TOKENS changes require Owner approval
# [CONSUMERS] .pre_commit-config.yaml GATE-11; .github/workflows/governance.yml; tests/unit/test_gate11_naming_convention.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] exit 0=clean; exit 1=violations found; exit 2=usage error
# [TESTS] tests/unit/test_gate11_naming_convention.py
"""GATE-11 命名规范门禁 — 全类型命名检测。

权威依据：docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml v2.5.0 §五

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
  N-16  测试文件名项目内唯一性检测
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS

# ---------------------------------------------------------------------------
# 白名单与豁免配置
# ---------------------------------------------------------------------------

FILENAME_UPPERCASE_WHITELIST: list[str] = [
    "AGENTS.md",
    "MAKEFILE",
    "Dockerfile",
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "ARCHITECTURE_LOCK.yaml",
    "SCOPE.yaml",
    "LICENSE",
    "AGENT.md",
    "SKILL.md",
    "PKG_INFO",
    "SOURCES.txt",
    "SHARED-QUICKREF.yml",
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
# N-06: module_id scope 前缀检测
# ---------------------------------------------------------------------------

_MODULE_ID_SCOPE_RE = re.compile(
    r"^\s*module_id:\s*(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW|DOM|PS|SYS|KBG|REG|IDX|CFG|PHASE|TPL|IRN)(?:-[A-Z]+[0-9]*)*-\d+",
    re.MULTILINE,
)
# Relaxed regex for inline module_id: inside .py comment headers (e.g. "# [A_test] module_id: SRC-TST-0212 | ...")
_INLINE_MODULE_ID_SCOPE_RE = re.compile(
    r"module_id:\s*(ADR|CP|KE|STD|DW|SRC|OPS|MOD|PSP|GOV|ARCH|VIEW|DOM|PS|SYS|KBG|REG|IDX|CFG|PHASE|TPL|IRN)(?:-[A-Z]+[0-9]*)*-\d+\b"
)


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
    # Check: does ANY module_id: in the file have a valid scope prefix?
    if _MODULE_ID_SCOPE_RE.search(content) or _INLINE_MODULE_ID_SCOPE_RE.search(content):
        return []
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
    _REAL_MID_RE = re.compile(r"^\s*module_id:\s*(.+)", re.MULTILINE)
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
        content = abspath.read_text(encoding="utf-8", errors="replace")
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
_DIR_ROOT_KEBAB_EXEMPT: set[str] = {
    "architecture-model",
    "session-logs",
    "test_dir",
    "target-architecture",
    "cross-cutting",
}
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
    # Exempt module ID directories (e.g. MOD-INF-006, DOM-GOV-001, SYS-MASTER-001)
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

_DOC_TYPE_SUFFIX_MAP: dict[str, list[str]] = {
    "policy": ["-policy.md", "-policy.yaml", "-policy.yml", "-rules.yaml", "-rules.yml"],
    "standard": ["-standard.md", "-standard.yaml", "-standard.yml"],
    "protocol": ["-protocol.md"],
    "operational_rule": ["-runbook.md", "-playbook.md", "-procedure.md", "-checklist.md"],
    "register": ["-registry.md", "-register.md", "-registry.yaml", "-registry.yml", "-register.yaml", "-register.yml"],
    "index": ["index.md"],
    "template": ["-template.md"],
    "terminology": [
        "-_registry/vocabularies/glossary.yaml",
        "-terminology.md",
        "-mapping.md",
        "_registry/vocabularies/glossary.yaml",
        "_registry/vocabularies/terminology_mapping.yaml",
    ],
    "blueprint": ["blueprint.md"],
    "catalog": ["-catalog.md", "-catalog.yaml", "-catalog.yml", "-ranking.md"],
    "guide": ["-guide.md"],
    "reference": ["-reference.md", "-ref.md"],
    "log": ["-log.md"],
    "report": ["-report.md"],
}

_DOC_TYPE_RE = re.compile(r"^doc_type:\s*(\S+)", re.MULTILINE)


def _check_n11_doctype_suffix(filepath: str, abspath: Path | None = None) -> list[NamingViolation]:
    """01_policies_and_standards/ 下文件名后缀必须匹配 frontmatter doc_type。
    强化: 扩展 doc_type 映射表(terminology/blueprint/catalog/guide/reference/log/report);
          YAML 文件也检查 doc_type 与后缀一致性
    """
    rel = filepath.replace("\\", "/")
    if "01_policies_and_standards/" not in rel:
        return []
    if abspath is None or not abspath.exists():
        return []
    try:
        content = abspath.read_text(encoding="utf-8", errors="replace")
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
        if name.endswith(suffix):
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
    "ARCHITECTURE_LOCK.yaml",
    "SCOPE.yaml",
    "LICENSE",
    "AGENT.md",
    "SKILL.md",
    "PKG-INFO",
    "SOURCES.txt",
    "SHARED-QUICKREF.yml",
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
    # 知识条目 ke-* 和 session-logs 豁免
    if name.startswith("ke-") or name.startswith("session-"):
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
        content = abspath.read_text(encoding="utf-8", errors="replace")
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
        content = abspath.read_text(encoding="utf-8", errors="replace")
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
# N-16: 测试文件名项目内唯一性
# ---------------------------------------------------------------------------

_N16_EXEMPT_NAMES: set[str] = {"conftest.py", "__init__.py"}


def check_test_name_uniqueness(project_root: Path | None = None) -> list[NamingViolation]:
    """扫描 tests/ 下所有 test_*.py，同名文件（basename 相同）视为违规。

    豁免: conftest.py / __init__.py（这些文件在不同目录下同名是正常的）。
    修复方式: 按 test_{module}_{domain}.py 格式加入目录层级后缀。
    """
    if project_root is None:
        project_root = Path.cwd()
    tests_dir = project_root / "tests"
    if not tests_dir.is_dir():
        return []

    from collections import defaultdict

    name_to_paths: dict[str, list[str]] = defaultdict(list)
    for py_file in tests_dir.rglob("*.py"):
        basename = py_file.name
        if basename in _N16_EXEMPT_NAMES:
            continue
        if not basename.startswith("test_"):
            continue
        rel = str(py_file.relative_to(project_root)).replace("\\", "/")
        name_to_paths[basename].append(rel)

    violations: list[NamingViolation] = []
    for basename, paths in sorted(name_to_paths.items()):
        if len(paths) > 1:
            for p in paths:
                violations.append(
                    NamingViolation(
                        rule="N-16",
                        message=f"测试文件名不唯一: {basename} (共{len(paths)}处: {', '.join(paths)})",
                        filepath=p,
                    )
                )
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
    if "session-logs/" in rel:
        return True
    if "docs/19_development_workspace/session-logs/" in rel:
        return True
    return False


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


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="GATE-11 命名规范门禁")
    parser.add_argument("path", nargs="?", default=".", help="要检查的文件或目录路径")
    parser.add_argument("--scan", action="store_true", help="扫描整个项目目录")
    parser.add_argument("--staged", action="store_true", help="只检查git暂存区文件")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不阻断")
    args = parser.parse_args()

    all_violations: list[NamingViolation] = []

    if args.staged:
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
                cwd=Path(__file__).resolve().parents[3],
            )
            staged_files = [f for f in result.stdout.strip().split("\n") if f]
        except (subprocess.CalledProcessError, FileNotFoundError):
            staged_files = []
        project_root = Path(__file__).resolve().parents[3]
        for rel_path in staged_files:
            abspath = project_root / rel_path
            if abspath.exists() and abspath.is_file():
                all_violations.extend(check_file(rel_path.replace("\\", "/"), abspath, project_root))
    elif args.scan:
        project_root = Path(args.path).resolve()
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
        # N-16: 全局检测——测试文件名唯一性
        all_violations.extend(check_test_name_uniqueness(project_root))
    else:
        target = Path(args.path)
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
            filepath = args.path
            all_violations.extend(check_file(filepath, target))

    for v in all_violations:
        print(f"[{v.rule}] {v.message}")

    if all_violations:
        print(f"\n总计 {len(all_violations)} 个命名违规")
        return EXIT_FINDINGS if not args.warn_only else EXIT_PASS
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
