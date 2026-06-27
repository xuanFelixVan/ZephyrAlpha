# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_frontmatter_metadata.py | §gate-15
# [MODULE] governance.d3_metadata.check_frontmatter_metadata
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance._shared.frontmatter; _shared.constants
# [CONSUMERS] pre-commit GATE-15; GitCommitGateway._check_frontmatter_ttl; manual validation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 从 ttl_vocabulary.yaml + doc_type_vocabulary.yaml 动态加载合法值；ttl 始终 hard block；doc_type 默认 warn-only，--strict-doctype 或 ZEPHYR_DOCTYPE_STRICT=1 升级 hard block；只校验有 frontmatter 的 .md；--all-files 强制全量扫描（忽略传入的文件参数）；--ci 参数接受但当前等同于默认（全量校验）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无 hard-block 违规）；EXIT_FINDINGS=1（ttl 缺失/非法 或 strict-doctype 下 doc_type 缺失/非法）；EXIT_ERROR=2（脚本异常）
# [TESTS] tests/unit/governance/test_check_frontmatter_metadata.py
# [TTL] task_bound
"""GATE-15: Frontmatter metadata validation（ttl + doc_type 字段校验）

校验 .md 文档 frontmatter 的词表字段：
  1. ttl——必填 + 合法值（从 ttl_vocabulary.yaml 动态加载），始终 hard block
  2. doc_type——必填 + 合法值（从 doc_type_vocabulary.yaml 动态加载），
     默认 warn-only（93 文件仍缺 doc_type，Stage 2.3 完成后升级 strict）

字段校验配置见 _FIELD_RULES——新增词表字段校验只需加一行配置，不改加载/校验逻辑。
通用词表加载器 _load_vocab_values() 吸收归档脚本 validate_frontmatter_values.py 模式。

capability registry: 本文件是 frontmatter metadata validation 的 canonical 真源
（见 capability_canonical_file_registry.yaml capability_id=frontmatter_metadata_validation）。
归档脚本 validate_frontmatter_values.py 是 legacy 副本，不复活——如需扩展字段校验，扩展本文件。

两种模式:
  全量（无参数或 --all-files）: 扫描 docs/ 下所有 .md
  增量（有文件参数且无 --all-files，pre-commit pass_filenames=true 时用）: 只校验传入的 .md

Usage::

    # 全量扫描（无参数即全量）
    python scripts/governance/d3_metadata/check_frontmatter_metadata.py

    # 全量扫描（显式 --all-files，即使传入文件参数也忽略）
    python scripts/governance/d3_metadata/check_frontmatter_metadata.py --all-files

    # 增量校验（pre-commit 传入文件）
    python scripts/governance/d3_metadata/check_frontmatter_metadata.py --ci docs/foo.md docs/bar.md

    # strict doc_type（hard block on missing/invalid doc_type）
    python scripts/governance/d3_metadata/check_frontmatter_metadata.py --strict-doctype
    # 或 env: ZEPHYR_DOCTYPE_STRICT=1
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ── 路径设置 ──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.frontmatter import (  # noqa: E402
    parse_byaml_anchor,
    parse_frontmatter,
    parse_json_meta,
    parse_py_header,
)

_VOCAB_DIR = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"
)

# 字段校验配置——GATE-15 校验哪些字段的唯一声明
# 吸收归档脚本 validate_frontmatter_values.py 的 VOCAB_FIELD_MAP 模式
# 新增字段校验只需在此添加一行，不改 _load_vocab_values / _check_file 逻辑
_FIELD_RULES: dict[str, dict] = {
    "ttl": {
        "vocab_file": "ttl_vocabulary.yaml",
        "required": True,        # 缺失 → 始终 hard block
        "always_strict": True,   # 非法值 → 始终 hard block（不可降级）
    },
    "doc_type": {
        "vocab_file": "doc_type_vocabulary.yaml",
        "required": True,         # 缺失 → issue（warn-only 或 strict）
        "always_strict": False,  # 默认 warn-only；--strict-doctype/env 升级 hard block
        "deprecated_key": "deprecated_values",  # 词表有废弃值节
    },
}


def _load_vocab_values(vocab_file: str) -> set[str]:
    """通用词表值加载（吸收归档脚本 validate_frontmatter_values.py:73-90 模式）。

    单一加载函数服务 _FIELD_RULES 中所有字段，避免每字段写一个 _load_xxx_values()。
    """
    import yaml

    path = _VOCAB_DIR / vocab_file
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    values: set[str] = set()
    for entry in data.get("values", []):
        if isinstance(entry, dict):
            val = entry.get("value") or entry.get("id")
            if val:
                values.add(str(val))
        elif isinstance(entry, str):
            values.add(entry)
    return values


def _load_deprecated_values(
    vocab_file: str, deprecated_key: str
) -> dict[str, str | None]:
    """加载废弃值及迁移目标（单值→目标，多值/N/A→None 需人工判定）。"""
    import yaml

    path = _VOCAB_DIR / vocab_file
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    result: dict[str, str | None] = {}
    for v in data.get(deprecated_key, []):
        val = v.get("value", "")
        mt = v.get("migrated_to", [])
        if isinstance(mt, str) and mt and not mt.startswith("N/A"):
            result[val] = mt
        elif isinstance(mt, list) and len(mt) == 1 and mt[0] and not mt[0].startswith("N/A"):
            result[val] = mt[0]
        else:
            result[val] = None  # 多值/N/A → 需人工判定
    return result


def _check_file(
    fpath: Path,
    field_rules: dict[str, dict],
    vocab_cache: dict[str, set[str]],
    deprecated_cache: dict[str, dict[str, str | None]],
    strict_doctype: bool,
) -> list[str]:
    """校验单个文件的 frontmatter 字段。

    ttl：始终 hard block（缺失/非法 → issues 列表 → EXIT_FINDINGS）
    doc_type：默认 warn-only（缺失/非法 → print WARN，不计入 issues → EXIT_PASS）；
              --strict-doctype 或 ZEPHYR_DOCTYPE_STRICT=1 → hard block

    Returns:
        issues 列表（空列表 = 无 hard-block 违规）。
    """
    issues: list[str] = []
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [f"cannot read file"]

    # 格式路由（向内收——一个校验函数，多格式解析）
    # .md→parse_frontmatter / .py+.sh+.ps1+.mmd→parse_py_header / .yaml→parse_byaml_anchor / .json→parse_json_meta
    suffix = fpath.suffix.lower()
    if suffix == ".md":
        metadata, _ = parse_frontmatter(text)
    elif suffix in (".py", ".sh", ".ps1", ".mmd"):
        metadata = parse_py_header(text)
    elif suffix == ".yaml":
        metadata = parse_byaml_anchor(text)
    elif suffix == ".json":
        metadata = parse_json_meta(text)
    else:
        return issues  # 不校验的扩展名

    # 无头部的文件跳过（不强制要求头部，仅校验有头部文件的字段）
    if not metadata:
        return issues

    for field, rule in field_rules.items():
        # doc_type 只对 .md 校验（其他格式无 doc_type 字段）
        if field == "doc_type" and suffix != ".md":
            continue
        val = metadata.get(field)
        is_strict = rule["always_strict"] or (field == "doc_type" and strict_doctype)
        valid_values = vocab_cache[field]
        deprecated = deprecated_cache.get(field, {})

        if not val:
            if rule["required"]:
                issue = f"missing required field '{field}'"
                if is_strict:
                    issues.append(issue)
                else:
                    print(f"  WARN (doctype): {fpath.name} {issue}")
        elif val not in valid_values:
            if val in deprecated:
                target = deprecated[val]
                issue = f"deprecated {field}='{val}'" + (
                    f", migrate to: {target}" if target else ", needs manual review"
                )
            else:
                issue = f"invalid {field}='{val}' (valid: {sorted(valid_values)[:5]}...)"
            if is_strict:
                issues.append(issue)
            else:
                print(f"  WARN (doctype): {fpath.name} {issue}")
    return issues


def main() -> int:
    raw_args = sys.argv[1:]
    all_files = "--all-files" in raw_args
    strict_doctype = (
        "--strict-doctype" in raw_args
        or os.environ.get("ZEPHYR_DOCTYPE_STRICT", "0") == "1"
    )

    # 加载所有字段的词表缓存（一次性加载，_check_file 复用）
    vocab_cache: dict[str, set[str]] = {}
    deprecated_cache: dict[str, dict[str, str | None]] = {}
    for field, rule in _FIELD_RULES.items():
        vocab_cache[field] = _load_vocab_values(rule["vocab_file"])
        if "deprecated_key" in rule:
            deprecated_cache[field] = _load_deprecated_values(
                rule["vocab_file"], rule["deprecated_key"]
            )

    # 过滤掉 -- 开头的参数（如 --ci, --all-files, --strict-doctype），只保留文件路径
    args = [a for a in raw_args if not a.startswith("-")]

    if args and not all_files:
        # 增量模式：只校验传入的文件（.md/.py/.sh/.ps1/.mmd/.yaml/.json）
        valid_suffixes = (".md", ".py", ".sh", ".ps1", ".mmd", ".yaml", ".json")
        files = [Path(a).resolve() for a in args if a.endswith(valid_suffixes)]
    else:
        # 全量模式：扫描 docs/ + src/ + scripts/ + tests/ 下所有支持格式
        valid_suffixes = {".md", ".py", ".sh", ".ps1", ".mmd", ".yaml", ".json"}
        exempt_parts = {"__pycache__", ".git", ".ailocks", "_backups", "_archive",
                        ".aidrafts", ".runtime", "data", "models", ".mypy_cache",
                        ".pytest_cache", ".ruff_cache"}
        files = []
        for scan_root_name in ("docs", "src", "scripts", "tests"):
            scan_dir = REPO_ROOT / scan_root_name
            if not scan_dir.exists():
                continue
            for fp in scan_dir.rglob("*"):
                if (fp.is_file() and fp.suffix.lower() in valid_suffixes
                        and not any(p in exempt_parts for p in fp.relative_to(REPO_ROOT).parts)):
                    files.append(fp)

    if not files:
        print("OK: no files to check")
        return EXIT_PASS

    errors = 0
    checked = 0
    for fpath in files:
        if not fpath.exists():
            continue
        checked += 1
        issues = _check_file(
            fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype
        )
        if issues:
            try:
                rel = fpath.relative_to(REPO_ROOT)
            except ValueError:
                rel = fpath
            for issue in issues:
                print(f"  FAIL: {rel} {issue}")
            errors += 1

    if errors:
        print(
            f"\nFAIL: {errors} file(s) with hard-block issues in {checked} files checked"
        )
        return EXIT_FINDINGS

    print(f"OK: Frontmatter validation passed ({checked} files checked)")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
