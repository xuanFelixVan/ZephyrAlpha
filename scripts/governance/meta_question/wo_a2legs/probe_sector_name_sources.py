# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-P1 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0013/0063/0085)
# [MODULE] scripts.governance.meta_question.wo_a2legs.probe_sector_name_sources
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service (reader 只读探针)
# [CONSUMERS] 产物册 data/registers/metaq_sector_name/ + WO-A2LEGS 案卷
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读取证，零写；候选真源以 system.columns 实证存在性后再查，禁凭直觉猜列名。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常直接抛出（fail-visible）。
# [TESTS] 无（一次性取证脚本，同族 scripts/ch/backfill_* 先例）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-P1 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""WO-A2LEGS probe 01: sector code->name 在册真源普查。

目的：为 c1_market.kline_sector_880.sector_name 100% 空置找可机械对齐的 code->name 真源。
输出 JSON 到 stdout（供案卷引用）。
"""

from __future__ import annotations

import json
import sys

sys.path.insert(0, "src")

from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService

CONN = DatabaseService().get_clickhouse_conn(role="reader")

# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
_T_SECTOR_880 = TableRegistry().table("market_sector_kline_880")

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。库名/表名/列名为运行期入参，一律 %s 占位由调用方
# 传入，禁把值写进常量；'2025-09-09' 为固定闭卷切点判据（非运行期日期）保留字面量。
_SQL_K880_BEFORE_CUT = f"SELECT count(), uniqExact(sector_code) FROM {_T_SECTOR_880} WHERE trade_date <= '2025-09-09'"
_SQL_CODES880 = f"SELECT DISTINCT sector_code FROM {_T_SECTOR_880}"
_SQL_K880_RANGE = f"SELECT min(trade_date), max(trade_date), count(), uniqExact(sector_code) FROM {_T_SECTOR_880}"
_SQL_K880_PREFIX_HIST = (
    "SELECT substring(sector_code,1,6) AS p, count() AS n, uniqExact(sector_code) AS codes, "
    f"min(trade_date), max(trade_date) FROM {_T_SECTOR_880} "
    "GROUP BY p ORDER BY n DESC LIMIT 20"
)
_SQL_K880_NAME_FILLED = f"SELECT countIf(sector_name != '') AS name_filled, count() AS total FROM {_T_SECTOR_880}"
_SQL_COL_EXISTS = "SELECT count() FROM system.columns WHERE database='%s' AND table='%s' AND name='%s'"
_SQL_PROFILE_TOTAL = "SELECT count() FROM %s.%s FINAL"
_SQL_PROFILE_DISTINCT = "SELECT uniqExact(( %s, %s )) FROM %s.%s FINAL"
_SQL_PROFILE_NAME_NONEMPTY = "SELECT countIf(%s != '') FROM %s.%s FINAL"
_SQL_PROFILE_SAMPLE = "SELECT DISTINCT %s, %s FROM %s.%s FINAL WHERE %s != '' LIMIT 5"
_SQL_PROFILE_PREFIX_HIST = (
    "SELECT substring(%s,1,3) AS p, count() FROM %s.%s FINAL GROUP BY p ORDER BY count() DESC LIMIT 8"
)
_SQL_PROFILE_SRC = "SELECT DISTINCT %s FROM %s.%s FINAL WHERE %s != ''"


def q(sql: str):
    return [list(r) for r in CONN.execute(sql)]


def main() -> None:
    out: dict = {}
    out["k880_range"] = q(_SQL_K880_RANGE)
    out["k880_before_cut"] = q(_SQL_K880_BEFORE_CUT)
    out["k880_prefix_hist"] = q(_SQL_K880_PREFIX_HIST)
    out["k880_all_cols_nonempty"] = q(_SQL_K880_NAME_FILLED)
    # 候选真源普查：凡是同时有 code 与 name 的板块/概念维表
    cands = [
        ("c1_market", "sector_meta", "sector_code", "sector_name"),
        ("c1_market", "concept_sector", "sector_code", "sector_name"),
        ("c1_market", "sector_constituent", "sector_code", "sector_name"),
        ("c1_market", "sector_constituent_snapshot", "sector_code", "sector_name"),
        ("c1_market", "sector_state", "sector_code", "sector_name"),
        ("c1_market", "sector_snapshot", "sector_code", "sector_name"),
        ("c1_market", "concept_board", "board_code", "board_name"),
        ("c1_market", "concept_board_constituent", "board_code", "board_name"),
        ("c1_market", "industry_class", "sector_code", "sector_name"),
    ]
    cands = [
        c
        for c in cands
        if q(_SQL_COL_EXISTS % (c[0], c[1], c[2]))[0][0] > 0 and q(_SQL_COL_EXISTS % (c[0], c[1], c[3]))[0][0] > 0
    ]
    prof = {}
    for db, tb, cc, cn in cands:
        key = f"{db}.{tb}({cc}->{cn})"
        prof[key] = {
            "total": q(_SQL_PROFILE_TOTAL % (db, tb))[0][0],
            "distinct_pairs": q(_SQL_PROFILE_DISTINCT % (cc, cn, db, tb))[0][0],
            "name_nonempty": q(_SQL_PROFILE_NAME_NONEMPTY % (cn, db, tb))[0][0],
            "sample": q(_SQL_PROFILE_SAMPLE % (cc, cn, db, tb, cn)),
        }
        # 880 前缀分布
        prof[key]["prefix_hist"] = q(_SQL_PROFILE_PREFIX_HIST % (cc, db, tb))
    out["candidates"] = prof

    # 交集覆盖率：880 码去后缀后与候选源 code 去后缀后 join 命中数
    codes880 = [r[0] for r in q(_SQL_CODES880)]
    bare = sorted({c.split(".")[0] for c in codes880})
    out["k880_bare_codes"] = len(bare)
    out["k880_bare_sample"] = bare[:10]
    cover = {}
    for db, tb, cc, cn in cands:
        src = sorted({str(r[0]) for r in q(_SQL_PROFILE_SRC % (cc, db, tb, cn))})
        src_bare = {s.split(".")[0] for s in src}
        hit = [c for c in bare if c in src_bare]
        cover[f"{db}.{tb}"] = {
            "src_codes": len(src_bare),
            "hit": len(hit),
            "coverage": round(len(hit) / max(1, len(bare)), 4),
        }
    out["coverage_vs_880"] = cover
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
