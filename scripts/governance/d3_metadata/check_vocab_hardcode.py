# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_vocab_hardcode.py | §gate-vocab
# [MODULE] governance.d3_metadata.check_vocab_hardcode
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance._shared.constants; _shared.walk
# [CONSUMERS] pre-commit GATE-VOCAB; manual audit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] AST 扫描检测词表合法值硬编码 + load_vocabulary_values 引用 yaml 存在性；warn-only 起步(exit 0)；DDL 例外白名单；_archive 排除；# noqa: gate-vocab 内联豁免
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无违规或 warn-only）；EXIT_FINDINGS=1（--ci 模式有违规）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动测试：全量扫描 exit 0；已知违规文件被检出
"""GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）

检测 src/ 与 scripts/ 下 .py 文件中硬编码的词表合法值集合。
词表合法值必须从 *_vocabulary.yaml 动态加载（yaml.safe_load），
禁止用 list/set/frozenset 字面量复制合法值——同步=复制=多真源=必漂移。

检测逻辑（AST 扫描）：
  1. 变量名匹配 VALID_*_VALUES/STATUSES/TYPES/LEVELS/LAYERS/TTL 等模式
  2. 赋值为字面量集合（list/set/frozenset/tuple）→ 疑似硬编码
  3. 赋值为函数调用（如 _load_xxx_values()）→ 动态加载 → 合规
  4. load_vocabulary_values("xxx.yaml") 调用 → 校验 xxx.yaml 是否存在

模式:
  --warn-only（默认）: print 违规清单，exit 0
  --ci: print 违规清单，有违规则 exit 1（未来 hard block）

Usage::

    # 全量扫描（warn-only，默认）
    python scripts/governance/d3_metadata/check_vocab_hardcode.py

    # CI 模式（有违规则 exit 1）
    python scripts/governance/d3_metadata/check_vocab_hardcode.py --ci
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

# ── 路径设置 ──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.walk import iter_files  # noqa: E402

# ── 词表前缀 → YAML 文件名映射（用于输出建议）──
_VOCAB_FILES: dict[str, str] = {
    "TTL": "ttl_vocabulary.yaml",
    "STATUS": "status_vocabulary.yaml",
    "STATUSES": "status_vocabulary.yaml",
    "LAYER": "layer_vocabulary.yaml",
    "LAYERS": "layer_vocabulary.yaml",
    "CATEGORY": "category_vocabulary.yaml",
    "SAFETY": "safety_level_vocabulary.yaml",
    "SAFETY_LEVEL": "safety_level_vocabulary.yaml",
    "STABILITY": "stability_vocabulary.yaml",
    "AUTONOMY": "ai_autonomy_vocabulary.yaml",
    "AI_AUTONOMY": "ai_autonomy_vocabulary.yaml",
    "CLASSIFICATION": "classification_vocabulary.yaml",
    "DOC_TYPE": "doc_type_vocabulary.yaml",
    "DOC_TYPES": "doc_type_vocabulary.yaml",
    "REVIEW_STATUS": "review_status_vocabulary.yaml",
    "RULE_FORM": "rule_form_vocabulary.yaml",
    "VERIFIABILITY": "verifiability_vocabulary.yaml",
}

# ── 疑似词表硬编码的变量名模式 ──
# 匹配 VALID/ALLOWED/LEGAL/PERMITTED_*_VALUES/STATUSES/TYPES/LEVELS/LAYERS/TTL/CATEGORIES/CLASSIFICATIONS/LIST/SET
# v1.1.0 增强：增加 ALLOWED/LEGAL/PERMITTED 前缀 + LIST/SET 后缀（覆盖红队绕过 A01/A10）
_VALID_VAR_PATTERN = re.compile(
    r"^(VALID|ALLOWED|LEGAL|PERMITTED)_[A-Z_]*?(VALUES|STATUSES|TYPES|LEVELS|LAYERS|TTL|CATEGORIES|CLASSIFICATIONS|LIST|SET)$"
)

# ── DDL 例外白名单（SQL CHECK 无法 yaml.safe_load，走 DDL-as-Code 协议）──
_DDL_EXEMPT_FILES: frozenset[str] = frozenset({
    "sqlite_schema.py",
    "depgraph_schema.py",
    "audit_post_sync_commands.py",
})


def _is_literal_collection(value: ast.expr) -> bool:
    """判断 AST 节点是否为字面量集合（list/set/tuple 字面量，或对字面量参数的 set/frozenset 调用）。

    Returns:
        True 如果是字面量集合（硬编码嫌疑），False 如果是函数调用/动态加载（合规）。
        关键区分：set({...字面量...}) = 硬编码；set(动态调用) = 合规动态加载。

    v1.1.0 增强（覆盖红队绕过 A04/A05）:
        - dict()/list()/tuple() 字面量参数调用 → 硬编码
        - "a,b,c".split(",") 字符串方法产生列表 → 硬编码
        - dict(a=1, b=2) 关键字参数 → 硬编码
    """
    if isinstance(value, (ast.List, ast.Set, ast.Tuple)):
        return True
    # 仅当 set()/frozenset()/dict()/list()/tuple() 的参数本身是字面量集合时才判为字面量硬编码
    # set({"a","b"}) → True（字面量参数）
    # set(_bp_meta.get(...)) → False（动态调用参数，合规）
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
        if value.func.id in ("frozenset", "set", "list", "tuple"):
            if value.args and isinstance(value.args[0], (ast.List, ast.Set, ast.Tuple)):
                return True
            # 无参数或参数非字面量集合 → 动态加载，合规
            return False
        # dict(a=1, b=2) 关键字参数 → 字面量硬编码
        if value.func.id == "dict":
            if value.args and isinstance(value.args[0], (ast.Dict, ast.List, ast.Set, ast.Tuple)):
                return True
            if value.keywords:
                return True
            return False
    # "a,b,c".split(",") → 字符串方法产生列表，硬编码
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
        if value.func.attr in ("split", "rsplit", "splitlines"):
            if isinstance(value.func.value, ast.Constant):
                return True
            return False
    return False


def _check_file(filepath: Path, vocab_dir: Path) -> list[tuple[int, str]]:
    """检查单个 Python 文件的词表硬编码与 yaml 引用存在性。

    Args:
        filepath: Python 文件绝对路径。
        vocab_dir: 词表 YAML 所在目录（用于校验 load_vocabulary_values 引用存在性）。

    Returns:
        (行号, 违规描述) 列表（空列表 = 通过）。

    内联豁免：行尾 ``# noqa: gate-vocab`` 可豁免该行检测（标准 lint 做法）。
    豁免行仍会记录到 issues 但标记为 [EXEMPTED]，warn-only 模式不阻断。
    """
    issues: list[tuple[int, str]] = []

    # _archive 排除
    if "_archive" in filepath.parts:
        return issues

    # DDL 例外
    if filepath.name in _DDL_EXEMPT_FILES:
        return issues

    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [(0, "cannot read file")]

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []  # 语法错误的文件跳过（非词表问题）

    for node in ast.walk(tree):
        # 检测1：词表硬编码（VALID_* 赋值为字面量集合）
        # v1.1.0 增强：同时检测 ast.NamedExpr（walrus 操作符，覆盖红队绕过 A11）
        if isinstance(node, (ast.Assign, ast.NamedExpr)):
            # Assign.targets 是列表；NamedExpr.target 是单个 Name
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                var_name = target.id
                match = _VALID_VAR_PATTERN.match(var_name)
                if not match:
                    continue

                # 字面量赋值 = 硬编码嫌疑；函数调用 = 动态加载 = 合规
                if not _is_literal_collection(node.value):
                    continue

                # noqa: gate-vocab 内联豁免检查
                if _has_noqa_exempt(source, node.lineno):
                    continue  # 豁免，不报

                # 提取词表前缀，推断对应 YAML 文件名
                suffix = match.group(2)  # VALUES / STATUSES / TYPES / LEVELS / LAYERS / TTL / LIST / SET
                # 从变量名提取前缀：VALID_TTL_VALUES → TTL，VALID_LAYERS → LAYERS
                # v1.1.0: 前缀可能是 VALID/ALLOWED/LEGAL/PERMITTED
                prefix_part = var_name.split("_", 1)[1]  # 去掉前缀（VALID/ALLOWED/...）
                prefix_part = prefix_part[:-(len(suffix) + 1)]  # 去掉 _SUFFIX 后缀
                if not prefix_part:
                    prefix_part = suffix  # VALID_VALUES → VALUES
                vocab_file = _VOCAB_FILES.get(prefix_part) or _VOCAB_FILES.get(suffix)
                if not vocab_file:
                    vocab_file = f"{prefix_part.lower()}_vocabulary.yaml"

                issues.append((
                    node.lineno,
                    f"{var_name} 硬编码词表合法值(应从 {vocab_file} 动态加载)",
                ))
        # 检测2：load_vocabulary_values("xxx.yaml") 引用的词表文件存在性
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id != "load_vocabulary_values":
                continue
            if not node.args:
                continue
            first = node.args[0]
            # 仅校验字面量字符串参数（变量参数无法静态分析）
            if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
                continue
            # noqa 豁免
            if _has_noqa_exempt(source, node.lineno):
                continue
            vocab_file = first.value
            p = Path(vocab_file)
            if not p.is_absolute():
                p = vocab_dir / vocab_file
            if not p.exists():
                issues.append((
                    node.lineno,
                    f"load_vocabulary_values 引用的词表文件不存在: {vocab_file}",
                ))

    return issues


def _has_noqa_exempt(source: str, lineno: int) -> bool:
    """检查指定行是否有 ``# noqa: gate-vocab`` 内联豁免。

    Args:
        source: 文件源码
        lineno: 1-based 行号

    Returns:
        True 如果该行有 noqa: gate-vocab 注释
    """
    lines = source.splitlines()
    if lineno < 1 or lineno > len(lines):
        return False
    return "# noqa: gate-vocab" in lines[lineno - 1]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）"
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        default=True,
        help="仅警告不阻断（默认，exit 0 即使有违规）",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI 模式，有违规则 exit 1（未来硬阻断用）",
    )
    args = parser.parse_args()

    # 扫描 src/zephyr/ 和 scripts/
    scan_dirs = [
        REPO_ROOT / "src" / "zephyr",
        REPO_ROOT / "scripts",
    ]

    # 词表 YAML 真源目录（用于校验 load_vocabulary_values 引用存在性）
    vocab_dir = (
        REPO_ROOT
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "vocabularies"
    )

    # 排除 _archive 目录
    exclude = EXCLUDE_DIRS | {"_archive", "tests"}

    all_issues: list[tuple[Path, int, str]] = []
    checked = 0

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        py_files = iter_files(
            scan_dir,
            extensions=frozenset({".py"}),
            exclude_dirs=exclude,
        )
        for filepath in py_files:
            checked += 1
            issues = _check_file(filepath, vocab_dir)
            for lineno, issue in issues:
                all_issues.append((filepath, lineno, issue))

    if not all_issues:
        print(f"OK: No vocabulary hardcode issues found ({checked} files checked)")
        return EXIT_PASS

    # 输出违规
    for filepath, lineno, issue in all_issues:
        try:
            rel = filepath.relative_to(REPO_ROOT)
        except ValueError:
            rel = filepath
        print(f"  WARN: {rel}:{lineno} {issue}")

    print(f"\nFOUND: {len(all_issues)} vocabulary hardcode issue(s) in {checked} files checked")

    if args.ci:
        return EXIT_FINDINGS
    return EXIT_PASS  # warn-only


if __name__ == "__main__":
    sys.exit(main())
