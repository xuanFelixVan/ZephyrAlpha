# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_frontmatter_metadata.py | §gate-15
# [MODULE] governance.d3_metadata.check_frontmatter_metadata
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance._shared.frontmatter; _shared.constants
# [CONSUMERS] pre-commit GATE-15; manual validation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 从 ttl_vocabulary.yaml 动态加载合法 ttl 值；只校验有 frontmatter 的 .md；--ci 参数接受但当前等同于默认（全量校验）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无违规）；EXIT_FINDINGS=1（有 ttl 缺失/非法）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动测试：全量模式 EXIT=0；增量模式传入有/无 ttl 文件
"""GATE-15: Frontmatter metadata validation（ttl 字段校验）

校验 .md 文档 frontmatter 的 ttl 字段：
  1. ttl 字段存在（有 frontmatter 的文档必填）
  2. ttl 值合法（从 ttl_vocabulary.yaml 动态加载）

两种模式:
  全量（无参数）: 扫描 docs/ 下所有 .md
  增量（有文件参数，pre-commit pass_filenames=true 时用）: 只校验传入的 .md

Usage::

    # 全量扫描
    python scripts/governance/d3_metadata/check_frontmatter_metadata.py

    # 增量校验（pre-commit 传入文件）
    python scripts/governance/d3_metadata/check_frontmatter_metadata.py --ci docs/foo.md docs/bar.md

    # --ci 参数接受但等同于默认模式（当前不区分 ci/非 ci）
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── 路径设置 ──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402
from _shared.frontmatter import parse_frontmatter  # noqa: E402

_PROJ = Path(__file__).resolve().parents[3]
_TTL_VOCAB_PATH = (
    _PROJ
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "vocabularies"
    / "ttl_vocabulary.yaml"
)


def _load_ttl_values() -> set[str]:
    """从 ttl_vocabulary.yaml 加载合法 ttl 值集合。"""
    import yaml

    data = yaml.safe_load(_TTL_VOCAB_PATH.read_text(encoding="utf-8"))
    return {v["value"] for v in data.get("values", [])}


def _check_file(fpath: Path, valid_ttl: set[str]) -> list[str]:
    """校验单个文件的 ttl 字段。

    Returns:
        issues 列表（空列表 = 通过）。
    """
    issues: list[str] = []
    try:
        text = fpath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [f"cannot read file"]

    metadata, _ = parse_frontmatter(text)

    # 无 frontmatter 的文档跳过（不校验 ttl）
    if not metadata:
        return issues

    ttl = metadata.get("ttl")
    if not ttl:
        issues.append("missing required field 'ttl' (see ttl_vocabulary.yaml decision_tree)")
    elif ttl not in valid_ttl:
        issues.append(
            f"invalid ttl='{ttl}' (valid values: {sorted(valid_ttl)})"
        )

    return issues


def main() -> int:
    valid_ttl = _load_ttl_values()

    # 过滤掉 -- 开头的参数（如 --ci），只保留文件路径
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if args:
        # 增量模式：只校验传入的 .md 文件
        files = [Path(a).resolve() for a in args if a.endswith(".md")]
    else:
        # 全量模式：扫描 docs/ 下所有 .md
        docs_dir = _PROJ / "docs"
        files = list(docs_dir.rglob("*.md"))

    if not files:
        print("OK: no .md files to check")
        return EXIT_PASS

    errors = 0
    checked = 0
    for fpath in files:
        if not fpath.exists():
            continue
        checked += 1
        issues = _check_file(fpath, valid_ttl)
        if issues:
            try:
                rel = fpath.relative_to(_PROJ)
            except ValueError:
                rel = fpath
            for issue in issues:
                print(f"  WARN: {rel} {issue}")
            errors += 1

    if errors:
        print(f"\nFAIL: {errors} frontmatter ttl issue(s) in {checked} files checked")
        return EXIT_FINDINGS

    print(f"OK: Frontmatter ttl validation passed ({checked} files checked)")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
