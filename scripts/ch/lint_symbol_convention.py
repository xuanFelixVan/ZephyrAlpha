# [BLUEPRINT] MOD-L04-001
# [MODULE] scripts.ch.lint_symbol_convention
# [DOMAIN] D_DATA
# [DEPENDENCIES] none (static lint, no DB)
# [CONSUMERS] pre-commit hook; 人工审查
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 校验 schemas/categories/*.py 中所有含 symbol 列的 securities 表 DDL 必含 exchange+symbol_canonical 列; 防回退（新表缺 exchange 列即阻断提交）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源文件import失败->WARN跳过; 发现违规->退出码1; 全部通过->退出码0
# [TESTS] python scripts/ch/lint_symbol_convention.py (smoke: 全量 schema 文件 lint)
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-DATA-SYMBOL-002 TRAE-082
"""Symbol 约定 lint 门禁（TRAE-082 GATE-SYMBOL-CONVENTION）。

静态 lint 校验（无 DB 连接，快速 pre-commit 适用）：
    1. 所有含 symbol 列的 securities 表 DDL 必含 exchange 列（INV-002）
    2. 所有含 symbol 列的 securities 表 DDL 必含 symbol_canonical 列（INV-003）
    3. exchange 列类型必须为 LowCardinality(String)（统一类型规范）

不校验数据层（exchange 非空率等）——那由 verify_exchange_coverage.py 负责。
不校验 DB 结构——那由 verify_schema_truth.py 负责。
本 lint 只校验 DDL-as-Code 真源文件（schemas/categories/*.py）的静态正确性。

用法::

    python scripts/ch/lint_symbol_convention.py             # 全量 lint
    python scripts/ch/lint_symbol_convention.py --ci         # CI 门禁模式
    python scripts/ch/lint_symbol_convention.py --quiet      # 只输出摘要

退出码：
    0 = 全部通过
    1 = 有违规（阻断提交）
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent.parent
_SCHEMA_DIR = _REPO_ROOT / "schemas" / "categories"


def _discover_truth_files() -> list[Path]:
    """枚举 schemas/categories/*.py 真源文件。"""
    return sorted(_SCHEMA_DIR.glob("*.py"))


def _load_ddl(path: Path) -> str | None:
    """加载真源文件的 *_DDL 字符串常量。"""
    try:
        name = f"_truth_{path.stem}"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for attr in dir(mod):
            if attr.endswith("_DDL"):
                val = getattr(mod, attr)
                if isinstance(val, str) and "CREATE TABLE" in val:
                    return val
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] 真源 {path.name} 导入失败: {e}")
    return None


def _has_column(ddl: str, col_name: str) -> bool:
    """检查 DDL 中是否包含指定列名（作为列定义，非 COMMENT/字符串内）。"""
    # 匹配列名作为列定义开头（行首缩进 + 列名 + 空白 + 类型）
    # 避免匹配 COMMENT 字符串中的文本
    pattern = rf"(?m)^\s+{re.escape(col_name)}\s+\w+"
    return bool(re.search(pattern, ddl))


def _has_symbol_column(ddl: str) -> bool:
    """检查 DDL 是否是 securities 表（含 symbol 列）。"""
    return _has_column(ddl, "symbol")


def _get_column_type(ddl: str, col_name: str) -> str | None:
    """提取列的类型（截断于 DEFAULT/MATERIALIZED/ALIAS/COMMENT 之前）。"""
    pattern = rf"(?m)^\s+{re.escape(col_name)}\s+(.+)$"
    m = re.search(pattern, ddl)
    if not m:
        return None
    rest = m.group(1).strip()
    # 截断于修饰符之前
    for keyword in ("DEFAULT", "MATERIALIZED", "ALIAS", "COMMENT"):
        idx = rest.upper().find(keyword)
        if idx > 0:
            rest = rest[:idx].strip()
    return rest


def lint() -> tuple[bool, list[str]]:
    """lint 所有 schema 文件。

    Returns:
        (全部通过, 违规清单)
    """
    violations: list[str] = []
    checked = 0

    for path in _discover_truth_files():
        ddl = _load_ddl(path)
        if not ddl:
            continue
        checked += 1

        # 只校验含 symbol 列的 securities 表
        if not _has_symbol_column(ddl):
            continue

        table_match = re.search(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+\.\w+)", ddl, re.IGNORECASE)
        table_name = table_match.group(1) if table_match else path.stem

        # 检查 exchange 列
        if not _has_column(ddl, "exchange"):
            violations.append(f"{path.name} ({table_name}): 缺 exchange 列（TRAE-082 INV-002）")
        else:
            # 检查 exchange 列类型
            ex_type = _get_column_type(ddl, "exchange")
            if ex_type and "LowCardinality(String)" not in ex_type:
                violations.append(
                    f"{path.name} ({table_name}): exchange 列类型 '{ex_type}' 应为 LowCardinality(String)"
                )

        # 检查 symbol_canonical 列
        if not _has_column(ddl, "symbol_canonical"):
            violations.append(f"{path.name} ({table_name}): 缺 symbol_canonical 列（TRAE-082 INV-003）")

    return not violations, violations


def main() -> int:
    ap = argparse.ArgumentParser(description="Symbol 约定 lint 门禁（TRAE-082 GATE-SYMBOL-CONVENTION）")
    ap.add_argument("--ci", action="store_true", help="CI 门禁模式（同默认行为，保留接口一致性）")
    ap.add_argument("--quiet", action="store_true", help="只输出摘要")
    args = ap.parse_args()

    passed, violations = lint()

    if not args.quiet or not passed:
        print(f" lint {len(_discover_truth_files())} schema 文件，发现 {len(violations)} 处违规。")

    if violations:
        print("\n=== 违规明细 ===")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("全部通过：所有 securities 表 DDL 含 exchange + symbol_canonical 列。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
