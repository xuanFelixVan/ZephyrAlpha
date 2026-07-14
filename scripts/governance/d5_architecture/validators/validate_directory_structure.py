# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_directory_structure.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_directory_structure
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""Module docstring — see module-level docstring for details."""

from __future__ import annotations

#!/usr/bin/env python3
"""
validate_directory_structure.py — LPC 双轨目录结构合规性扫描器
==============================================================
依据：GOV-DOC-002 §三（src/zephyr/ 双轨结构）+ §二（docs/ 目录结构）
GOV-DOC-002 §5.1.2 防幻觉路径映射表的自动化执行器。


检查项
------
1. src/zephyr/ 下的所有一级子目录是否在 LPC 双轨受控列表中
2. src/zephyr/ 下的所有一级 .py 文件（孤儿文件）报告
3. docs/ 下的所有一级子目录是否在受控列表中

问题背景（根因）
--------------
项目曾出现 7 处违规：script_system/、config/、core/、dashboard/、
hooks/、rules/、schemas.py 等目录/文件不在规范定义的受控列表中，
原因是施工时未参考 GOV-DOC-002 的目录定义。本扫描器作为门禁，
防止此类问题再次发生。

Usage:
    python scripts/governance/d5_architecture/validate_directory_structure.py
    python scripts/governance/d5_architecture/validate_directory_structure.py --warn-only

输出
----
- exit 0: 全部合规
- exit 1: 发现违规（--warn-only 下仅打印警告，exit 0）
"""

__manifest__ = {
    "args": ["--warn-only", "--jsonl"],
    "description": "LPC双轨目录结构合规性扫描 [src/zephyr/ + docs/ 一级目录白名单校验]",
    "dimensions": ["D5"],
    "priority": "P0",
    "timeout_seconds": 30,
    "warn_only": False,
}


import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml as _yaml
except ImportError:  # pragma: no cover
    _yaml = None

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import REPO_ROOT
from _shared.thresholds import get

SRC_ZEPHYR = REPO_ROOT / "src" / "zephyr"
DOCS = REPO_ROOT / "docs"

C_TRACK_DIRS: set[str] = {  # noqa: gate-vocab  层目录名，非 domain 值
    "data",
    "infrastructure_runtime_integration",
    "factor",
    "signal",
    "risk",
    "pf_core",
    "ex_core",
    "frontend",
    "research",
    "compliance",
    "ml_train",
    "integration",
}

B_TRACK_DIRS: set[str] = {
    "llm-security",
    "vector-memory",
    "context-engine",
    "orchestrator",
    "feedback-loop",
    "gates",
    "pipeline",
    "core",
    "db",
    "kb",
    "mcp",
    "shared",
    "hooks",
    "agent-rbac",
    "agent-spec",
    "audit-trail",
    "rollback",
    "escalation",
    "drift-detector",
    "budget-enforcer",
    "a2a",
    "telemetry",
    "capacity-assurance",
    "code_dedup_engine",
    "script_system",
}
ALLOWED_SRC_ZEPHYR_DIRS: set[str] = C_TRACK_DIRS | B_TRACK_DIRS

ALLOWED_DOCS_DIRS: set[str] = {
    "01_policies_and_standards",
    "02_enterprise_architecture",
    "03_modules",
    "08_knowledge",
    "_working",
    "99_archive",
}

DOCS_ROOT_ALLOWED_FILES: set[str] = {
    "migration-declaration.md",
    "index.md",
}

SRC_ZEPHYR_ALLOWED_FILES: set[str] = {
    "__init__.py",
}

# gov_doc_003_directory_semantics R5: 数字后缀禁止（_\d+ 结尾）
_DIGIT_SUFFIX_RE = re.compile(r"_\d+$")

# gov_doc_003_directory_semantics R1 grandfathered 白名单 fail-open 回退
# 真源: trae_028 gov_doc_003_directory_semantics.grandfathered.abbreviation_dirs
_GRANDFATHERED_ABBREVIATION_FALLBACK: set[str] = {"api", "mcp", "io", "a2a", "sla", "db", "kb"}

_TRAE_028_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "rules" / "trae_028_doc_structure_naming.yaml"
)


def _load_grandfathered_abbreviations() -> set[str]:
    """从 trae_028 gov_doc_003_directory_semantics.grandfathered.abbreviation_dirs 动态加载。

    fail-open: YAML 缺失/解析失败/字段不完整时返回硬编码回退值。
    """
    if _yaml is None:
        return _GRANDFATHERED_ABBREVIATION_FALLBACK
    try:
        data = _yaml.safe_load(_TRAE_028_PATH.read_text(encoding="utf-8"))
        sections = data.get("sections", {})
        sem = sections.get("gov_doc_003_directory_semantics", {})
        grandfathered = sem.get("grandfathered", {})
        abbrev_dirs = grandfathered.get("abbreviation_dirs", [])
        if abbrev_dirs:
            return set(abbrev_dirs)
        return _GRANDFATHERED_ABBREVIATION_FALLBACK
    except Exception:
        return _GRANDFATHERED_ABBREVIATION_FALLBACK


def _scan_directory(path: Path, allowed_dirs: set[str], allowed_files: set[str], label: str) -> list[str]:
    """_scan_directory implementation."""
    violations: list[str] = []
    if not path.exists():
        violations.append(f"\u274c {label}: 路径不存在: {path}")
        return violations

    for item in sorted(path.iterdir()):
        name = item.name
        if name.startswith("_"):
            continue
        if item.is_dir():
            if name not in allowed_dirs:
                violations.append(f"\u274c [{label}] 未授权的目录: {name}/ \u2192 GOV-DOC-002 §三/§二 未定义此目录")
        elif item.is_file():
            if name.endswith(".pyc") or name == "__pycache__":
                continue
            if name not in allowed_files:
                violations.append(
                    f"\u26a0\ufe0f [{label}] 孤儿文件: {name} \u2192 一级 .py 文件应归入 shared/ 或对应模块目录"
                )
    return violations


def _scan_layer_internals() -> list[str]:
    """_scan_layer_internals implementation."""
    violations: list[str] = []
    for layer_name in ALLOWED_SRC_ZEPHYR_DIRS:
        layer_dir = SRC_ZEPHYR / layer_name
        if not layer_dir.exists() or not layer_dir.is_dir():
            continue
        py_files = [
            f
            for f in layer_dir.iterdir()
            if f.is_file() and f.suffix == ".py" and f.name != "__init__.py" and not f.name.startswith("_")
        ]
        if len(py_files) >= get("directory_scalability.src_py_error", 120):
            violations.append(
                f"\u26a0\ufe0f [{layer_name}] {len(py_files)} 个平铺 .py 文件 -- 应采用 <module>/ 子目录隔离 (GOV-DOC-018 文件夹平铺容量阈值协议，warn=60/error=120)"
            )
    docs_modules = DOCS / "03_modules"
    if docs_modules.exists():
        for layer_name in ALLOWED_SRC_ZEPHYR_DIRS:
            layer_dir = docs_modules / layer_name
            if not layer_dir.exists() or not layer_dir.is_dir():
                continue
            if (layer_dir / "blueprint.md").exists():
                violations.append(
                    f"\u274c [docs/{layer_name}] blueprint.md 直接平铺 -- 必须在 <module>/ 子目录下 (GOV-DOC-002 §三 C轨层内规范)"
                )
    return violations


def _scan_directory_naming_semantics() -> list[str]:
    """检测子目录命名语义违规（gov_doc_003_directory_semantics）。

    R1: 缩写必除——2字符及以下缩写（grandfathered 白名单外）警告
    R5: 数字后缀禁止——_\\d+ 结尾（本脚本 warning-only，硬阻断在 GitCommitGateway R5-DIGIT-SUFFIX gate）
    """
    violations: list[str] = []
    grandfathered = _load_grandfathered_abbreviations()
    for dirpath in SRC_ZEPHYR.rglob("*"):
        if not dirpath.is_dir():
            continue
        name = dirpath.name
        if name.startswith("_") or name == "__pycache__":
            continue
        rel = dirpath.relative_to(SRC_ZEPHYR)
        # R5: 数字后缀检测（本脚本 warning-only，硬阻断在 GitCommitGateway R5-DIGIT-SUFFIX gate）
        if _DIGIT_SUFFIX_RE.search(name):
            violations.append(
                f"\u274c [命名语义] 数字后缀目录: {rel} \u2192 gov_doc_003_directory_semantics R5 禁止 _NN 数字后缀（暗示多真源）"
            )
        # R1: 缩写检测（2字符及以下，非 grandfathered）
        elif len(name) <= 2 and name not in grandfathered:
            violations.append(
                f"\u26a0\ufe0f [命名语义] 缩写目录: {rel} \u2192 gov_doc_003_directory_semantics R1 禁止2字符及以下缩写（AI无法推断语义）"
            )
    return violations


def main() -> int:
    """入口函数。"""
    parser = argparse.ArgumentParser(description="LPC 双轨目录结构合规扫描（GOV-DOC-002）")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--jsonl", action="store_true")
    args = parser.parse_args()

    warn_only = args.warn_only

    all_violations: list[str] = []

    src_violations = _scan_directory(SRC_ZEPHYR, ALLOWED_SRC_ZEPHYR_DIRS, SRC_ZEPHYR_ALLOWED_FILES, "src/zephyr")
    all_violations.extend(src_violations)

    docs_violations = _scan_directory(DOCS, ALLOWED_DOCS_DIRS, DOCS_ROOT_ALLOWED_FILES, "docs")
    all_violations.extend(docs_violations)

    layer_violations = _scan_layer_internals()
    all_violations.extend(layer_violations)

    # gov_doc_003_directory_semantics 命名语义检测（仅警告，不影响 exit code）
    # 历史违规目录渐进收敛，不批量改名（避免过度工程）
    naming_violations = _scan_directory_naming_semantics()
    for v in naming_violations:
        print(f"  {v}", file=sys.stderr)

    if not all_violations:
        print("\u2705 目录结构合规: src/zephyr/ 和 docs/ 下无违规目录/文件", file=sys.stderr)
        code = 0
        if args.jsonl:
            print(
                json.dumps(
                    {"severity": "INFO", "check_id": "DIR-STRUCTURE", "violations": 0},
                    ensure_ascii=False,
                )
            )
        return code

    print(f"\u274c 发现 {len(all_violations)} 处目录结构违规:\n", file=sys.stderr)
    for v in all_violations:
        print(f"  {v}", file=sys.stderr)

    if warn_only:
        print("\n\u26a0\ufe0f  --warn-only 模式: 仅报告，不阻断", file=sys.stderr)
        code = 0
    else:
        print(
            "\n\u274c 阻断: 请将违规目录/文件迁移到正确位置。参考 GOV-DOC-002 §三/§二 + §四 决策树。",
            file=sys.stderr,
        )
        code = 1

    if args.jsonl:
        print(
            json.dumps(
                {
                    "severity": "HIGH" if all_violations else "INFO",
                    "check_id": "DIR-STRUCTURE",
                    "violations": len(all_violations),
                },
                ensure_ascii=False,
            )
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
