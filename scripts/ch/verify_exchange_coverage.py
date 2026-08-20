# [BLUEPRINT] MOD-L04-001
# [MODULE] scripts.ch.verify_exchange_coverage
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; scripts.ch.apply_exchange_columns
# [CONSUMERS] 人工审查; CI门禁
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 检查所有证券表 exchange+symbol_canonical 列的数据覆盖率; Tier-1/2 MATERIALIZED 表 exchange 非空率应~100%; Tier-3 regular 表 exchange 可空(provider迁移期); symbol_canonical 非空率应与 exchange 非空率一致
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 覆盖率不足->退出码1(可--ci降级为WARN); 全部通过->退出码0
# [TESTS] python scripts/ch/verify_exchange_coverage.py (smoke: 全量覆盖率报告)
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-DATA-SYMBOL-002 TRAE-082
"""exchange+symbol_canonical 数据覆盖率校验器（TRAE-082 1.1.0 阶段2 配套）。

与 apply_exchange_columns.py --verify 互补：
    - apply_exchange_columns.py --verify：检查列是否存在 + 碰撞消歧（结构层）
    - verify_exchange_coverage.py：检查 exchange/symbol_canonical 非空率（数据层）

覆盖率预期（按 Tier 分层）：
    - Tier-1（MATERIALIZED multiIf 前缀推导）：exchange 非空率应 ~100%
      若 <100% 说明有 symbol 不匹配前缀规则（如 'T' 前缀测试数据 / 未知格式）
    - Tier-2（MATERIALIZED 常量）：exchange 非空率应 100%（常量派生）
    - Tier-3（regular 列 provider 写）：exchange 可空（provider 迁移期，阶段3 后应 ~100%）
    - symbol_canonical：非空率应与 exchange 非空率一致（MATERIALIZED 派生）

用法::

    python scripts/ch/verify_exchange_coverage.py             # 全量校验，打印报告
    python scripts/ch/verify_exchange_coverage.py --table NAME # 只校验指定表
    python scripts/ch/verify_exchange_coverage.py --ci         # CI 门禁模式
    python scripts/ch/verify_exchange_coverage.py --output PATH # 写 markdown 报告

退出码：
    0 = 全部通过（Tier-1/2 覆盖率达标）
    1 = 有不达标（Tier-1/2 覆盖率 < 阈值）
    2 = ClickHouse 不可达（--ci 模式降级为 0 + WARN）
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.ch.apply_exchange_columns import (  # noqa: E402
    DB,
    TIER1_INDEX_TABLES,
    TIER2_TABLES,
    TIER3_TABLES,
)
from zephyr.data import ch_writer  # noqa: E402

# 覆盖率阈值：Tier-1/2 MATERIALIZED 表 exchange 非空率低于此值则告警
TIER12_COVERAGE_THRESHOLD = 0.95  # 95%（允许少量异常 symbol）


def _query_tables_with_symbol() -> list[str]:
    """查询 c1_market 中所有含 symbol 列的表。"""
    out = ch_writer.query(
        "SELECT DISTINCT table FROM system.columns "
        "WHERE database = 'c1_market' AND name = 'symbol' ORDER BY table FORMAT TabSeparated"
    )
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def _classify_table(table: str) -> str:
    """返回表的 Tier 分类：tier1 / tier1_index / tier2 / tier3。"""
    if table in TIER1_INDEX_TABLES:
        return "tier1_index"
    if table in TIER2_TABLES:
        return "tier2"
    if table in TIER3_TABLES:
        return "tier3"
    return "tier1"


def _query_coverage(table: str) -> dict | None:
    """查询单表 exchange/symbol_canonical 覆盖率。

    大表（>100K 行）使用 100K 样本估算覆盖率，避免 14.5B 行全表扫描。
    小表（≤100K 行）做精确 countIf。

    Returns:
        {total, exchange_nonempty, exchange_empty, exchange_coverage,
         canonical_nonempty, canonical_coverage, empty_symbols_sample, sampled} 或 None
    """
    try:
        # 从 system.tables 获取总行数（O(1)，不扫描数据）
        total_row = ch_writer.query(
            f"SELECT total_rows FROM system.tables WHERE database='{DB}' AND name='{table}' FORMAT TabSeparated"
        ).strip()
        total = int(total_row) if total_row else 0

        if total == 0:
            return {
                "total": 0,
                "exchange_coverage": 1.0,
                "canonical_coverage": 1.0,
                "exchange_nonempty": 0,
                "exchange_empty": 0,
                "canonical_nonempty": 0,
                "empty_symbols_sample": [],
                "sampled": False,
            }

        # 大表采样（100K 样本），小表精确统计
        sample_size = 100_000
        if total > sample_size:
            result = ch_writer.query(
                f"""
                SELECT
                    count() AS sample_total,
                    countIf(exchange != '') AS ex_nonempty,
                    countIf(symbol_canonical != '') AS canon_nonempty
                FROM (SELECT exchange, symbol_canonical FROM {DB}.{table} LIMIT {sample_size})
                FORMAT TabSeparated
                """
            ).strip()
            sampled = True
        else:
            result = ch_writer.query(
                f"""
                SELECT
                    count() AS sample_total,
                    countIf(exchange != '') AS ex_nonempty,
                    countIf(symbol_canonical != '') AS canon_nonempty
                FROM {DB}.{table}
                FORMAT TabSeparated
                """
            ).strip()
            sampled = False

        if not result:
            return {
                "total": total,
                "exchange_coverage": 1.0,
                "canonical_coverage": 1.0,
                "exchange_nonempty": 0,
                "exchange_empty": 0,
                "canonical_nonempty": 0,
                "empty_symbols_sample": [],
                "sampled": sampled,
            }

        parts = result.split("\t")
        sample_total = int(parts[0])
        ex_nonempty = int(parts[1])
        canon_nonempty = int(parts[2])
        ex_empty = sample_total - ex_nonempty
        ex_cov = ex_nonempty / sample_total if sample_total > 0 else 1.0
        canon_cov = canon_nonempty / sample_total if sample_total > 0 else 1.0

        # 采样空 exchange 的 symbol（用于诊断，大表用子查询 LIMIT 避免全表扫描）
        empty_sample: list[str] = []
        if ex_empty > 0:
            if total > sample_size:
                diag = ch_writer.query(
                    f"SELECT DISTINCT symbol FROM "
                    f"(SELECT symbol, exchange FROM {DB}.{table} LIMIT {sample_size}) "
                    f"WHERE exchange = '' LIMIT 5 FORMAT TabSeparated"
                ).strip()
            else:
                diag = ch_writer.query(
                    f"SELECT DISTINCT symbol FROM {DB}.{table} WHERE exchange = '' LIMIT 5 FORMAT TabSeparated"
                ).strip()
            empty_sample = [s for s in diag.splitlines() if s.strip()]

        return {
            "total": total,
            "exchange_nonempty": ex_nonempty,
            "exchange_empty": ex_empty,
            "exchange_coverage": ex_cov,
            "canonical_nonempty": canon_nonempty,
            "canonical_coverage": canon_cov,
            "empty_symbols_sample": empty_sample,
            "sampled": sampled,
        }
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] 查询 {table} 覆盖率失败: {e}")
        return None


def _check_column_types(table: str) -> dict | None:
    """检查 exchange/symbol_canonical 列的 default_kind 是否符合 Tier 预期。

    Returns:
        {exchange_kind, canonical_kind, exchange_type, canonical_type} 或 None
    """
    try:
        rows = ch_writer.query(
            f"SELECT name, type, default_kind FROM system.columns "
            f"WHERE database='{DB}' AND table='{table}' "
            f"AND name IN ('exchange','symbol_canonical') "
            f"ORDER BY position FORMAT TabSeparated"
        ).strip()
        result = {}
        for line in rows.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t")
            name, typ, kind = parts[0], parts[1], parts[2] if len(parts) > 2 else ""
            if name == "exchange":
                result["exchange_type"] = typ
                result["exchange_kind"] = kind
            elif name == "symbol_canonical":
                result["canonical_type"] = typ
                result["canonical_kind"] = kind
        return result if result else None
    except Exception:  # noqa: BLE001
        return None


def verify(table_filter: str | None = None) -> tuple[bool, list[dict]]:
    """校验所有证券表 exchange 覆盖率。

    Returns:
        (全部通过, 逐表结果列表)
    """
    tables = _query_tables_with_symbol()
    if table_filter:
        tables = [t for t in tables if t == table_filter]

    results: list[dict] = []
    failures: list[str] = []

    for tbl in tables:
        tier = _classify_table(tbl)
        cols = _check_column_types(tbl)
        cov = _query_coverage(tbl)

        if cov is None:
            failures.append(f"{tbl}: 覆盖率查询失败")
            results.append({"table": tbl, "tier": tier, "status": "ERROR"})
            continue

        if cols is None:
            failures.append(f"{tbl}: 列定义查询失败")
            results.append({"table": tbl, "tier": tier, "status": "ERROR", "coverage": cov})
            continue

        entry = {
            "table": tbl,
            "tier": tier,
            "total": cov["total"],
            "exchange_coverage": cov["exchange_coverage"],
            "canonical_coverage": cov["canonical_coverage"],
            "exchange_kind": cols.get("exchange_kind", "?"),
            "canonical_kind": cols.get("canonical_kind", "?"),
            "empty_symbols": cov["empty_symbols_sample"],
            "sampled": cov.get("sampled", False),
            "status": "OK",
        }

        # Tier-1/2: exchange 应为 MATERIALIZED，覆盖率应 ≥ 阈值
        if tier in ("tier1", "tier1_index", "tier2"):
            if cols.get("exchange_kind") != "MATERIALIZED":
                entry["status"] = "FAIL"
                failures.append(
                    f"{tbl} (tier={tier}): exchange default_kind={cols.get('exchange_kind')} 应为 MATERIALIZED"
                )
            elif cov["total"] > 0 and cov["exchange_coverage"] < TIER12_COVERAGE_THRESHOLD:
                entry["status"] = "WARN"
                failures.append(
                    f"{tbl} (tier={tier}): exchange 覆盖率 "
                    f"{cov['exchange_coverage']:.1%} < {TIER12_COVERAGE_THRESHOLD:.0%} "
                    f"({cov['exchange_empty']}/{cov['total']} 行空 exchange)"
                )

        # Tier-3: exchange 应为 DEFAULT（regular），覆盖率可低（provider 迁移期）
        elif tier == "tier3":
            if cols.get("exchange_kind") == "MATERIALIZED":
                entry["status"] = "FAIL"
                failures.append(f"{tbl} (tier3): exchange default_kind=MATERIALIZED 应为 DEFAULT（regular列）")

        # symbol_canonical 应始终为 MATERIALIZED
        if cols.get("canonical_kind") != "MATERIALIZED":
            entry["status"] = "FAIL"
            failures.append(f"{tbl}: symbol_canonical default_kind={cols.get('canonical_kind')} 应为 MATERIALIZED")

        results.append(entry)

    passed = not failures
    return passed, results


def _print_report(results: list[dict], failures: list[str]) -> None:
    """打印覆盖率报告。"""
    # 按 tier 分组
    by_tier: dict[str, list[dict]] = {}
    for r in results:
        by_tier.setdefault(r["tier"], []).append(r)

    tier_order = ["tier1", "tier1_index", "tier2", "tier3"]
    tier_labels = {
        "tier1": "Tier-1 (A股 MATERIALIZED)",
        "tier1_index": "Tier-1 (指数 MATERIALIZED)",
        "tier2": "Tier-2 (市场隐含 MATERIALIZED)",
        "tier3": "Tier-3 (期货/期权 regular)",
    }

    print("=" * 80)
    print("exchange + symbol_canonical 覆盖率报告")
    print("=" * 80)

    for tier in tier_order:
        if tier not in by_tier:
            continue
        print(f"\n--- {tier_labels.get(tier, tier)} ({len(by_tier[tier])} 表) ---")
        print(
            f"{'表名':30s} {'行数':>12s} {'exch覆盖':>8s} {'canon覆盖':>8s} "
            f"{'ex_kind':>13s} {'can_kind':>13s} {'采样':>4s} {'状态':>5s}"
        )
        for r in sorted(by_tier[tier], key=lambda x: x["table"]):
            total = r.get("total", 0)
            ex_cov = r.get("exchange_coverage", 0)
            canon_cov = r.get("canonical_coverage", 0)
            ex_kind = r.get("exchange_kind", "?")
            can_kind = r.get("canonical_kind", "?")
            status = r.get("status", "?")
            sampled = "Y" if r.get("sampled") else "N"
            print(
                f"{r['table']:30s} {total:>12d} {ex_cov:>7.1%} {canon_cov:>7.1%} "
                f"{ex_kind:>13s} {can_kind:>13s} {sampled:>4s} {status:>5s}"
            )

            # 打印空 exchange 样本（诊断用）
            empty = r.get("empty_symbols", [])
            if empty and status in ("WARN", "FAIL"):
                print(f"  ↳ 空 exchange symbol 样本: {', '.join(empty[:5])}")

    print(f"\n{'=' * 80}")
    if failures:
        print(f"不达标项 ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
    else:
        print("全部通过：Tier-1/2 exchange 覆盖率达标，列类型符合 Tier 预期。")


def _write_markdown(path: Path, results: list[dict], failures: list[str]) -> None:
    """写 markdown 报告。"""
    import datetime as _dt

    lines = [
        "---",
        "ttl: task_bound",
        "---",
        "# Exchange Coverage Report",
        "",
        f"- 生成时间: {_dt.datetime.now(_dt.timezone.utc).isoformat()}",
        f"- 校验表数: {len(results)}",
        f"- 不达标项: {len(failures)}",
        f"- 退出码: {'1 (有不达标)' if failures else '0 (通过)'}",
        "",
        "## 逐表结果",
        "",
        "| 表名 | Tier | 行数 | exchange覆盖率 | canonical覆盖率 | exchange_kind | canonical_kind | 状态 |",
        "|------|------|------|---------------|----------------|--------------|---------------|------|",
    ]
    for r in sorted(results, key=lambda x: (x["tier"], x["table"])):
        lines.append(
            f"| {r['table']} | {r['tier']} | {r.get('total', 0)} | "
            f"{r.get('exchange_coverage', 0):.1%} | "
            f"{r.get('canonical_coverage', 0):.1%} | "
            f"{r.get('exchange_kind', '?')} | {r.get('canonical_kind', '?')} | "
            f"{r.get('status', '?')} |"
        )
    if failures:
        lines.extend(["", "## 不达标项", ""])
        for f in failures:
            lines.append(f"- {f}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="exchange+symbol_canonical 覆盖率校验")
    ap.add_argument("--table", help="只校验指定表名")
    ap.add_argument("--ci", action="store_true", help="CI 门禁模式：CH 不可达不阻断（exit 0 + WARN）")
    ap.add_argument("--output", help="把 markdown 报告写到指定路径")
    args = ap.parse_args()

    # 健康检查
    try:
        ping = ch_writer.query("SELECT 1")
        if not ping.strip():
            raise RuntimeError("SELECT 1 返回空")
    except Exception as e:  # noqa: BLE001
        if args.ci:
            print(f"[WARN] GATE-EXCHANGE-COVERAGE 跳过：ClickHouse 连接失败（{e}）")
            return 0
        print(f"[ERROR] ClickHouse 连接失败: {e}")
        return 2

    passed, results = verify(table_filter=args.table)
    failures = [r for r in results if r.get("status") in ("FAIL", "WARN", "ERROR")]
    fail_msgs: list[str] = []
    for r in results:
        if r.get("status") == "ERROR":
            fail_msgs.append(f"{r['table']}: 查询失败")
        elif r.get("status") == "FAIL":
            fail_msgs.append(f"{r['table']}: 列类型不符 Tier 预期")
        elif r.get("status") == "WARN":
            fail_msgs.append(f"{r['table']}: exchange 覆盖率 {r.get('exchange_coverage', 0):.1%} 低于阈值")

    _print_report(results, fail_msgs)

    if args.output:
        _write_markdown(Path(args.output), results, fail_msgs)
        print(f"\n报告已写入: {args.output}")

    return 1 if fail_msgs else 0


if __name__ == "__main__":
    sys.exit(main())
