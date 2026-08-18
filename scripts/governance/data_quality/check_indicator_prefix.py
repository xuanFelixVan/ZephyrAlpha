# [BLUEPRINT] MOD-GOV_DQ | scripts/governance/data_quality/check_indicator_prefix.py | §
# [MODULE] scripts.governance.data_quality.check_indicator_prefix
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.data.ch_reader
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 前缀映射真源=INDICATOR_PREFIX_MAP；akshare 中文名无前缀属预期（非违规）；只读查询不修改数据
# [MODIFY-GUARD] 修改前缀映射时同步更新本文件 docstring + INDICATOR_PREFIX_MAP 注释
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ch_reader.query 失败返回空字符串->打印错误并 exit 2
# [TESTS]
# [TTL] permanent
# [A_module] module_id=MOD-GOV_DQ | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
"""macro_data indicator_name 前缀合规检测工具。

检测 c1_market.macro_data 表中 indicator_name 是否符合各数据源的前缀命名约定。

前缀命名约定（INDICATOR_PREFIX_MAP）：
    data_source  | expected_prefix | 说明
    ------------ | --------------- | ----
    fred         | FRED_           | FRED 经济数据，全大写前缀
    eia          | EIA_            | EIA 能源数据，全大写前缀
    worldbank    | WB_             | World Bank 缩写（非 WORLDBANK_，WB 是国际标准缩写）
    akshare      | None            | akshare 指标名为中文原生格式（如"全国-同比增长"），无前缀属预期

设计理由（第一性原理）：
    1. 前缀目的是让 indicator_name 自文档化（从名称可推断数据源）
    2. data_source 字段已提供可靠的数据源追溯能力，前缀是辅助可读性
    3. worldbank 用 WB_ 缩写比 WORLDBANK_ 更符合国际惯例且更简洁
    4. akshare 指标名为中文金融术语（CPI/PMI/货币供应量），加 AKSHARE_ 前缀会破坏可读性
    5. 强制统一前缀（如 AKSHARE_全国-同比增长）会降低可读性且不符合中文金融数据惯例

用法：
    python scripts/governance/data_quality/check_indicator_prefix.py           # 检测模式（默认）
    python scripts/governance/data_quality/check_indicator_prefix.py --fix     # 生成修复 SQL（不执行）
    python scripts/governance/data_quality/check_indicator_prefix.py --ci      # CI 模式（违规即 exit 1）

退出码：
    0 = 全部合规
    1 = 发现违规（CI 模式）
    2 = 查询失败
"""
from __future__ import annotations

__manifest__ = """
args: []
description: macro_data indicator_name 前缀合规检测工具。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.data import ch_reader  # noqa: E402

# =============================================================================
# 前缀映射真源（SSoT）
# 修改此映射时 MUST 同步更新 docstring 中的表格
# =============================================================================
INDICATOR_PREFIX_MAP: dict[str, str | None] = {
    "fred": "FRED_",
    "eia": "EIA_",
    "worldbank": "WB_",  # World Bank 标准缩写，非 WORLDBANK_
    "akshare": None,     # 中文名原生格式，无前缀属预期
}


def check_prefixes() -> list[dict[str, object]]:
    """查询 ClickHouse 并检测前缀合规性。

    返回违规列表，每项包含 data_source/indicator_name/expected_prefix/actual。
    """
    result = ch_reader.query(
        "SELECT data_source, indicator_name, count() as cnt "
        "FROM c1_market.macro_data "
        "GROUP BY data_source, indicator_name "
        "ORDER BY data_source, indicator_name"
    )
    if not result or not result.strip():
        print("ERROR: 查询返回空结果", file=sys.stderr)
        return []

    violations: list[dict[str, object]] = []
    for line in result.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        data_source = parts[0].strip()
        indicator_name = parts[1].strip()
        # cnt = parts[2].strip()  # 保留用于报告

        expected_prefix = INDICATOR_PREFIX_MAP.get(data_source, None)

        # 数据源不在映射中 → 跳过（未知数据源，不检测）
        if data_source not in INDICATOR_PREFIX_MAP:
            continue

        # expected_prefix = None → 该数据源无前缀要求（如 akshare 中文名）
        if expected_prefix is None:
            continue

        # 检查前缀
        if not indicator_name.startswith(expected_prefix):
            violations.append({
                "data_source": data_source,
                "indicator_name": indicator_name,
                "expected_prefix": expected_prefix,
                "actual": indicator_name[:30],
            })

    return violations


def generate_fix_sql(violations: list[dict[str, object]]) -> str:
    """生成 ALTER TABLE UPDATE 修复 SQL（仅生成不执行）。

    对于 worldbank 违规（WB_ 前缀缺失），生成添加前缀的 SQL。
    对于其他数据源违规，生成建议注释。
    """
    if not violations:
        return "-- 无违规，无需修复\n"

    lines = ["-- 前缀修复 SQL（请人工审核后执行）", "-- " + "=" * 60]

    # 按数据源分组
    by_source: dict[str, list[dict[str, object]]] = {}
    for v in violations:
        src = str(v["data_source"])
        by_source.setdefault(src, []).append(v)

    for src, viols in sorted(by_source.items()):
        prefix = INDICATOR_PREFIX_MAP.get(src)
        if prefix is None:
            lines.append(f"\n-- {src}: 无前缀要求，{len(viols)} 个指标名无需修复")
            continue

        lines.append(f"\n-- {src}: 期望前缀 '{prefix}'，{len(viols)} 个违规")
        names = sorted({str(v["indicator_name"]) for v in viols})
        for name in names:
            new_name = f"{prefix}{name}"
            lines.append(
                f"ALTER TABLE c1_market.macro_data UPDATE "
                f"indicator_name = '{new_name}' "
                f"WHERE data_source = '{src}' AND indicator_name = '{name}';"
            )

    return "\n".join(lines)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="macro_data indicator_name 前缀合规检测"
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="生成修复 SQL（不执行）",
    )
    parser.add_argument(
        "--ci", action="store_true",
        help="CI 模式（违规即 exit 1）",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("macro_data indicator_name 前缀合规检测")
    print("=" * 60)
    print(f"\n前缀映射（INDICATOR_PREFIX_MAP）：")
    for src, prefix in INDICATOR_PREFIX_MAP.items():
        desc = f"'{prefix}'" if prefix else "无前缀要求（中文名原生格式）"
        print(f"  {src:12s} → {desc}")

    violations = check_prefixes()
    if violations is None:
        return 2

    print(f"\n检测结果：{len(violations)} 个违规")

    if violations:
        print("\n违规明细：")
        print(f"{'data_source':12s} {'indicator_name':40s} {'expected':12s} {'actual':30s}")
        print("-" * 94)
        for v in violations:
            print(
                f"{v['data_source']:12s} {v['indicator_name']:40s} "
                f"{v['expected_prefix']:12s} {v['actual']:30s}"
            )

        if args.fix:
            print("\n" + "=" * 60)
            print("修复 SQL（请人工审核后执行）")
            print("=" * 60)
            print(generate_fix_sql(violations))

        if args.ci:
            print("\nCI 模式：发现违规，exit 1")
            return 1
    else:
        print("\n✅ 全部合规")

    return 0


if __name__ == "__main__":
    sys.exit(main())
