# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] scripts.ch.apply_exchange_columns
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.symbol_normalizer
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DDL-as-Code: exchange+symbol_canonical 列真源为本脚本+symbol_normalizer前缀映射; 三层策略(Tier-1 MATERIALIZED multiIf/Tier-2 MATERIALIZED常量/Tier-3普通列provider写); 幂等(ADD COLUMN IF NOT EXISTS); 零回填(MATERIALIZED惰性求值); market_type列不动(asset_class语义保护, INV-005)
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->打印错误+退出码2; 列校验失败->列出差异+退出码1; 全部匹配->退出码0
# [TESTS] scripts/ch/apply_exchange_columns.py --verify (smoke test: 所有证券表含exchange+symbol_canonical列+碰撞消歧验证)
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-DATA-SYMBOL-002 TRAE-082
"""ClickHouse exchange+symbol_canonical 列部署脚本（TRAE-082 1.1.0 治本 #ARCH-DATA-SYMBOL-002）。

DDL-as-Code 模式：对所有证券表 ADD COLUMN exchange + symbol_canonical，零回填。
  - Tier-1（A股前缀可推导，~45表）：exchange MATERIALIZED multiIf(前缀推导) + symbol_canonical MATERIALIZED
  - Tier-2（市场隐含，~4表）：exchange MATERIALIZED 'HK'/'US' 常量 + symbol_canonical MATERIALIZED
  - Tier-3（逐行exchange，~5表）：exchange 普通列 DEFAULT '' (provider写) + symbol_canonical MATERIALIZED

治本背景（#ARCH-DATA-SYMBOL-002，2026-07-30）：
    TRAE-082 1.0.0 原方案"复用 market_type 改值存 exchange"经实测推翻——market_type 是 asset_class
    （stock/index/sector/etf/cb/lof）非交易所码，覆写破坏正交维度。改用独立 MATERIALIZED exchange 列，
    零回填（历史 part 惰性求值，新行自动派生）。provider 写入路径零改造（get_insert_columns 排除 MATERIALIZED）。

前缀映射单一真源：symbol_normalizer.normalizer._PREFIX3/_PREFIX2/_PREFIX_TO_EXCHANGE，
    本脚本导入生成 multiIf 表达式，与 Python derive_exchange 严格对齐（DRY）。

用法::

    python scripts/ch/apply_exchange_columns.py           # 部署列 + 验证
    python scripts/ch/apply_exchange_columns.py --verify  # 仅验证（smoke test）
    python scripts/ch/apply_exchange_columns.py --dry-run # 仅打印 DDL 不执行

退出码：
    0 = 全部一致
    1 = 有不一致
    2 = ClickHouse 不可达
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.symbol_normalizer.normalizer import (  # noqa: E402
    _INDEX_PREFIX3_TO_EXCHANGE,
    _PREFIX2_TO_EXCHANGE,
    _PREFIX3_TO_EXCHANGE,
    _PREFIX_TO_EXCHANGE,
)

DB = "c1_market"

# ========== 表分层分类（基于实测 c1_market 83表 audit 2026-07-30） ==========

# Tier-1 指数表：symbol 存指数代码（非股票代码），须用指数专用 multiIf
# 关键：000001 在股票表→SZ(平安银行)，在指数表→SH(上证指数)。若误用股票规则会碰撞。
TIER1_INDEX_TABLES: set[str] = {"kline_index"}

# Tier-2：市场隐含表（exchange 由表语义决定，MATERIALIZED 常量）
#   key=表名, value=exchange 码
TIER2_TABLES: dict[str, str] = {
    "kline_hk_daily": "HK",
    "hk_kline": "HK",
    "kline_us_daily": "US",
    "us_index": "US",
}

# Tier-3：逐行 exchange 表（期货/期权，symbol 无法前缀推导，provider 按 stock_list 写入）
TIER3_TABLES: list[str] = [
    "kline_futures",
    "futures_kline_qmt",
    "futures_term_structure",
    "futures_position",
    "option_greeks",
    "option_iv_surface",
    "option_kline",
]

# Tier-1：A股前缀可推导表（其余所有 has_symbol=1 且 has_exchange=0 的表）
# 由 _resolve_tier1() 在运行时从 system.columns 动态计算（避免硬编码遗漏）
TIER1_EXCLUDE = TIER1_INDEX_TABLES | set(TIER2_TABLES) | set(TIER3_TABLES)


def _bare(symbol_expr: str = "symbol") -> str:
    """生成提取裸码的 CH 表达式（处理带后缀 + 字母前缀 symbol，治本兼容三种格式）。

    三种 symbol 格式统一提取裸码（零数据改写，TRAE-082 INV-004）：
      1. 裸码 '000001' → splitByChar 无 '.' 返回原值 → replaceRegexpAll 无匹配 → '000001'
      2. 后缀式 '588000.SH' → splitByChar 取 [1] → '588000' → replaceRegexpAll 无匹配 → '588000'
      3. 前缀式 'sh600519' → splitByChar 无 '.' 返回原值 → replaceRegexpAll 去 'sh' → '600519'

    用于 MATERIALIZED exchange 推导，确保所有格式 symbol 都能正确推导 exchange。
    注意：A股代码纯数字，sh/sz/bj/hk 前缀仅出现在 provider 旧格式（miniqmt）中，
    replaceRegexpAll 对裸码是 no-op（安全）。
    """
    return f"replaceRegexpAll(splitByChar('.', {symbol_expr})[1], '^(sh|sz|bj|hk)', '')"


def _grouped_prefix_clauses(bare: str, length: int, mapping: dict[str, str]) -> str:
    """按 exchange 分组生成前缀子句（避免硬编码单一 exchange）。

    e.g. length=3, mapping={'110':'SH','123':'SZ'} ->
      "substring(bare,1,3) IN ('110'), 'SH', substring(bare,1,3) IN ('123'), 'SZ'"
    """
    by_ex: dict[str, list[str]] = {}
    for prefix, ex in mapping.items():
        by_ex.setdefault(ex, []).append(prefix)
    clauses = []
    for ex in sorted(by_ex):
        prefixes = ", ".join(f"'{p}'" for p in sorted(by_ex[ex]))
        clauses.append(f"substring({bare},1,{length}) IN ({prefixes}), '{ex}'")
    return ", ".join(clauses)


def _build_multiif_expr() -> str:
    """从 symbol_normalizer 前缀映射生成 CH MATERIALIZED multiIf 表达式（DRY 单一真源）。

    与 normalizer.derive_exchange 严格对齐：3位→2位→1位 前缀优先级。
    用于 Tier-1 股票表（不含指数表）。
    universal：用 _bare() 提取裸码，兼容带后缀 symbol（零数据改写治本）。
    """
    bare = _bare()
    p3 = _grouped_prefix_clauses(bare, 3, _PREFIX3_TO_EXCHANGE)
    p2 = _grouped_prefix_clauses(bare, 2, _PREFIX2_TO_EXCHANGE)
    p1 = _grouped_prefix_clauses(bare, 1, _PREFIX_TO_EXCHANGE)
    return f"multiIf({p3}, {p2}, {p1}, '')"


def _build_index_multiif_expr() -> str:
    """生成指数表专用的 MATERIALIZED multiIf 表达式（kline_index 等）。

    与 normalizer.derive_exchange_index 严格对齐：3 位前缀 000/880/930/931/932→SH，399→SZ。
    关键差异：000xxx 在指数表→SH（上证指数），在股票表→SZ（平安银行）。
    universal：用 _bare() 提取裸码，兼容带后缀 symbol（如 '000510.CSI' → 裸码 '000510' → SH）。
    """
    bare = _bare()
    p3 = _grouped_prefix_clauses(bare, 3, _INDEX_PREFIX3_TO_EXCHANGE)
    return f"multiIf({p3}, '')"


# ========== DDL 生成（每层独立函数，复杂度<15） ==========

def _ddl_add_exchange_materialized(table: str, expr: str) -> str:
    """Tier-1/2：exchange MATERIALIZED + symbol_canonical MATERIALIZED。"""
    return (
        f"ALTER TABLE {DB}.{table} "
        f"ADD COLUMN IF NOT EXISTS exchange LowCardinality(String) "
        f"MATERIALIZED {expr} COMMENT '交易所码(TRAE-082 MATERIALIZED派生)'"
    )


def _ddl_add_exchange_constant(table: str, exchange: str) -> str:
    """Tier-2：exchange MATERIALIZED 常量 + symbol_canonical MATERIALIZED。"""
    return (
        f"ALTER TABLE {DB}.{table} "
        f"ADD COLUMN IF NOT EXISTS exchange LowCardinality(String) "
        f"MATERIALIZED '{exchange}' COMMENT '交易所码(市场隐含)'"
    )


def _ddl_add_exchange_regular(table: str) -> str:
    """Tier-3：exchange 普通列 DEFAULT '' (provider写) + symbol_canonical MATERIALIZED。"""
    return (
        f"ALTER TABLE {DB}.{table} "
        f"ADD COLUMN IF NOT EXISTS exchange LowCardinality(String) "
        f"DEFAULT '' COMMENT '交易所码(provider按stock_list写入)'"
    )


def _ddl_add_canonical(table: str) -> str:
    """symbol_canonical MATERIALIZED（universal：兼容裸码/后缀式/前缀式 symbol）。

    三种 symbol 格式的 canonical 生成（零数据改写，TRAE-082 INV-004）：
      1. 后缀式 '588000.SH' → position('.')>0 → 直接用 symbol = '588000.SH'
      2. 裸码 '000001' → concat('000001', '.', 'SZ') = '000001.SZ'
      3. 前缀式 'sh600519' → concat('600519', '.', 'SH') = '600519.SH'（用 _bare 去前缀）

    避免带后缀 symbol 产生 '588000.SH.SH' 垃圾值，避免前缀式产生 'sh600519.SH' 不规范值。
    """
    return (
        f"ALTER TABLE {DB}.{table} "
        f"ADD COLUMN IF NOT EXISTS symbol_canonical String "
        f"MATERIALIZED if(position(symbol,'.')>0, symbol, concat({_bare()}, '.', exchange)) "
        f"COMMENT 'canonical身份键(TRAE-082 universal)'"
    )


# ========== 运行时表发现 ==========

def _query_tables_with_symbol() -> list[str]:
    """查询 c1_market 中所有含 symbol 列的表（运行时发现，避免硬编码遗漏）。"""
    out = ch_writer.query(
        "SELECT DISTINCT table FROM system.columns "
        "WHERE database = 'c1_market' AND name = 'symbol' ORDER BY table FORMAT TabSeparated"
    )
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def _find_suffix_tables(tables: list[str]) -> set[str]:
    """检测 symbol 列含带后缀值（'.'）的表（阶段2 归一前不可部署 MATERIALIZED）。

    带后缀 symbol（如 '000001.SH' / '00001.HK'）若直接加 MATERIALIZED exchange，
    symbol_canonical 会变成 '000001.SH.SH' 垃圾值。须先归一为裸码（阶段2）。

    用 LIMIT 1 采样（廉价），仅判断是否存在带 '.' 的 symbol。
    """
    suffix_tables: set[str] = set()
    for tbl in tables:
        try:
            sample = ch_writer.query(
                f"SELECT symbol FROM c1_market.{tbl} "
                f"WHERE symbol != '' AND position(symbol, '.') > 0 LIMIT 1 "
                f"FORMAT TabSeparated"
            ).strip()
            if sample:
                suffix_tables.add(tbl)
        except Exception:  # noqa: BLE001
            # 空表或查询失败，视为无后缀（空表 MATERIALIZED 无副作用）
            pass
    return suffix_tables


def _resolve_tier1(tables: list[str]) -> list[str]:
    """Tier-1 = 含 symbol 列且不在 Tier-2/Tier-3/指数表的表（动态计算）。"""
    return [t for t in tables if t not in TIER1_EXCLUDE]


# ========== 部署 + 验证 ==========

def _exec_ddl(sql: str, dry_run: bool) -> bool:
    """执行单条 DDL（dry_run 时仅打印）。返回是否成功。"""
    if dry_run:
        print(f"  [DRY-RUN] {sql}")
        return True
    ch_writer.query(sql)
    return True


def _ddl_drop_column(table: str, column: str) -> str:
    """DROP COLUMN（用于升级旧表达式，先 DROP 再 ADD）。"""
    return f"ALTER TABLE {DB}.{table} DROP COLUMN IF EXISTS {column}"


def apply(dry_run: bool = False, upgrade: bool = False) -> dict[str, list[str]]:
    """部署 exchange+symbol_canonical 列到所有证券表（universal 表达式兼容两种 symbol 格式）。

    universal MATERIALIZED 表达式用 splitByChar 提取裸码推导 exchange，
    symbol_canonical 用 if(position>0,...) 兼容带后缀 symbol——零数据改写治本。
    带后缀 symbol 表（如 tick_data 990M 行 '588000.SH'）无需跳过，表达式自动兼容。

    Args:
        upgrade: 若 True，对已有 exchange/symbol_canonical 列的表先 DROP 再 ADD
                 （升级旧简单表达式为 universal 表达式，修复带后缀行的垃圾 canonical）

    Returns:
        {"tier1": [...], "tier1_index": [...], "tier2": [...], "tier3": [...]} 各层已处理表清单。
    """
    multiif = _build_multiif_expr()
    index_multiif = _build_index_multiif_expr()
    tables = _query_tables_with_symbol()
    tier1 = _resolve_tier1(tables)
    tier1_index = [t for t in tables if t in TIER1_INDEX_TABLES]
    result: dict[str, list[str]] = {
        "tier1": [], "tier1_index": [], "tier2": [], "tier3": [],
    }

    print(f"[apply] 发现 {len(tables)} 张含 symbol 列的表："
          f"Tier-1(股票)={len(tier1)} / Tier-1(指数)={len(tier1_index)} / "
          f"Tier-2={len(TIER2_TABLES)} / Tier-3={len(TIER3_TABLES)}"
          f"{' [UPGRADE 模式：DROP+re-ADD]' if upgrade else ''}")

    def _deploy(table: str, exchange_ddl: str) -> None:
        """部署 exchange+canonical（upgrade 模式先 DROP）。"""
        if upgrade:
            _exec_ddl(_ddl_drop_column(table, "symbol_canonical"), dry_run)
            _exec_ddl(_ddl_drop_column(table, "exchange"), dry_run)
        _exec_ddl(exchange_ddl, dry_run)
        _exec_ddl(_ddl_add_canonical(table), dry_run)

    # Tier-1 股票表：MATERIALIZED 通用前缀 multiIf
    for tbl in tier1:
        _deploy(tbl, _ddl_add_exchange_materialized(tbl, multiif))
        result["tier1"].append(tbl)

    # Tier-1 指数表：MATERIALIZED 指数专用 multiIf（000/880/930→SH, 399→SZ）
    # 关键：000001 在指数表→SH(上证指数)，与股票表→SZ(平安银行)消歧
    for tbl in tier1_index:
        _deploy(tbl, _ddl_add_exchange_materialized(tbl, index_multiif))
        result["tier1_index"].append(tbl)

    # Tier-2：MATERIALIZED 常量
    for tbl, ex in TIER2_TABLES.items():
        if tbl in tables:
            _deploy(tbl, _ddl_add_exchange_constant(tbl, ex))
            result["tier2"].append(tbl)

    # Tier-3：普通列 DEFAULT ''
    for tbl in TIER3_TABLES:
        if tbl in tables:
            _deploy(tbl, _ddl_add_exchange_regular(tbl))
            result["tier3"].append(tbl)

    return result


def verify() -> tuple[bool, list[str]]:
    """验证所有证券表含 exchange+symbol_canonical 列 + 碰撞消歧。

    universal 表达式兼容带后缀 symbol，故所有含 symbol 列的表都应已部署。

    Returns:
        (全部通过, 差异清单)
    """
    tables = _query_tables_with_symbol()
    diffs: list[str] = []
    ok_count = 0

    for tbl in tables:
        desc = ch_writer.query(f"DESCRIBE TABLE {DB}.{tbl}")
        names = {ln.split("\t")[0] for ln in desc.splitlines() if ln.strip()}
        if "exchange" not in names:
            diffs.append(f"{tbl}: 缺 exchange 列")
        elif "symbol_canonical" not in names:
            diffs.append(f"{tbl}: 缺 symbol_canonical 列")
        else:
            ok_count += 1

    # 碰撞消歧验证（TRAE-082 核心验收）
    collision_ok = _verify_collision_disambig()
    if not collision_ok:
        diffs.append("碰撞消歧失败：000001 在 kline_daily/kline_index 的 symbol_canonical 未区分")

    passed = not diffs
    print(f"[verify] {ok_count}/{len(tables)} 表含 exchange+symbol_canonical 列，"
          f"碰撞消歧={'通过' if collision_ok else '失败'}")
    return passed, diffs


def _verify_collision_disambiguation() -> bool:
    """验证 000001 跨表碰撞已消歧（kline_daily→SZ vs kline_index→SH）。"""
    daily = ch_writer.query(
        f"SELECT DISTINCT symbol_canonical FROM {DB}.kline_daily "
        f"WHERE symbol = '000001' LIMIT 1"
    ).strip()
    index = ch_writer.query(
        f"SELECT DISTINCT symbol_canonical FROM {DB}.kline_index "
        f"WHERE symbol = '000001' LIMIT 1"
    ).strip()
    if not daily or not index:
        return False
    return daily != index and "SZ" in daily and "SH" in index


# 别名（保持复杂度低，主逻辑用 _verify_collision_disambiguation）
_verify_collision_disambig = _verify_collision_disambiguation


def main() -> int:
    parser = argparse.ArgumentParser(
        description="部署 exchange+symbol_canonical MATERIALIZED 列（TRAE-082 1.1.0 universal）"
    )
    parser.add_argument("--verify", action="store_true", help="仅验证（smoke test）")
    parser.add_argument("--dry-run", action="store_true", help="仅打印 DDL 不执行")
    parser.add_argument(
        "--upgrade", action="store_true",
        help="升级模式：对已有列的表先 DROP 再 ADD（修复旧简单表达式的垃圾 canonical）",
    )
    args = parser.parse_args()

    # 健康检查
    ping = ch_writer.query("SELECT 1")
    if not ping.strip():
        print("[ERROR] ClickHouse 不可达")
        return 2

    if args.verify:
        passed, diffs = verify()
        if not passed:
            print("[FAIL] 验证失败：")
            for d in diffs:
                print(f"  - {d}")
            return 1
        print("[PASS] 全部证券表含 exchange+symbol_canonical 列，碰撞消歧通过")
        return 0

    result = apply(dry_run=args.dry_run, upgrade=args.upgrade)
    print(f"[apply] 完成：Tier-1(股票)={len(result['tier1'])} / "
          f"Tier-1(指数)={len(result['tier1_index'])} / "
          f"Tier-2={len(result['tier2'])} / Tier-3={len(result['tier3'])}")

    passed, diffs = verify()
    if not passed:
        print("[WARN] 部署后验证有差异：")
        for d in diffs:
            print(f"  - {d}")
        return 1
    print("[PASS] 部署+验证完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
