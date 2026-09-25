# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-W1 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0013/0063)
# [MODULE] scripts.governance.meta_question.wo_a2legs.write_sector_name_map_to_ch
# [DOMAIN] D_DATA
# [DEPENDENCIES] data/registers/metaq_sector_name/sector_code_name_registry.yaml (真源册);
#                 zephyr.data.ch_writer (strict 写通道); zephyr.infrastructure.database_service (reader 复核);
#                 zephyr.shared.utils.time_utils (RULE-SCHEMA-TZ)
# [CONSUMERS] c1_market.sector_code_name_map（新维表）+ c1_market.v_kline_sector_880_named（兼容视图）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 写面三验证留痕（必要性=kline_sector_880.sector_name 443,380/443,380 空置且 CH 内无 880 名源；
#              真实性=名字取自同供应商主数据 cfg 并经 132/132 在册常量交叉验证；
#              可逆性=只新增对象（新表+新视图），零触碰既有表，回滚=DROP 新对象即可，既有行零改写）；
#              禁 UPDATE/DELETE/DROP 既有表、禁覆写既有行（写面铁律：改既有列一律"新表+视图兼容层"）；
#              幂等=map_version 为输入指纹，重跑同版本先探测再插，版本已足量则 skip；
#              列清单无 MATERIALIZED/ALIAS；ingest_ts 由 time_utils 显式赋 UTC。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 册缺失/DLL 失败→异常上抛非零退出；写后复核不过→SystemExit(6) fail-visible。
# [TESTS] 无（数据施工脚本，验收以 CH 探针复核为准）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-W1 | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""把 880 code→name 真源册派生落 CH 新维表 + 建兼容视图（不触碰 kline_sector_880 本体）。

用法：
    python scripts/governance/meta_question/wo_a2legs/write_sector_name_map_to_ch.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_ROOT / "src"))

import yaml  # noqa: E402

from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

REG = _ROOT / "data" / "registers" / "metaq_sector_name" / "sector_code_name_registry.yaml"
TBL = "c1_market.sector_code_name_map"
VIEW = "c1_market.v_kline_sector_880_named"
# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
# 注：本件写面=TBL/VIEW 两个新对象；母表 kline_sector_880 只读作视图 FROM 源，不改其行。
_T_SECTOR_880 = TableRegistry().table("market_sector_kline_880")

DDL = f"""
CREATE TABLE IF NOT EXISTS {TBL} (
    sector_code        String               COMMENT '880xxx.SH 全码（与 kline_sector_880.sector_code 同口径）',
    code_bare          String               COMMENT '880xxx 裸码',
    sector_name        String               COMMENT '板块中文名；未配码=空串（禁拍名）',
    code_family        LowCardinality(String) COMMENT '码族注记（mkt_index/region/industry_l1/industry_l2/concept_or_style）',
    coverage_status    LowCardinality(String) COMMENT 'named|unresolved',
    name_source        LowCardinality(String) COMMENT '真源文件（tdxzs3.cfg/tdxzs.cfg），unresolved 为空',
    tdx_type           String               COMMENT 'TDX 主数据 type 字段原值',
    tdx_level          String               COMMENT 'TDX 主数据 level 字段原值',
    map_version        String               COMMENT '映射册内容指纹（幂等键）',
    register_id        String               COMMENT '真源册标识',
    source_sha256      String               COMMENT '来源文件指纹',
    note               String               COMMENT '未配/例外留痕',
    ingest_ts          DateTime64(3, 'UTC') COMMENT '入库时间戳'
) ENGINE = ReplacingMergeTree(ingest_ts)
ORDER BY (map_version, sector_code)
COMMENT 'metaq_sector_name 派生维表：880 板块码→中文名（WO-A2LEGS，真源=data/registers/metaq_sector_name/）'
"""

VIEW_DDL = f"""
CREATE OR REPLACE VIEW {VIEW} AS
SELECT k.* EXCEPT (sector_name),
       if(m.sector_name != '', m.sector_name, k.sector_name) AS sector_name
FROM {_T_SECTOR_880} AS k
LEFT JOIN (
    SELECT sector_code, argMax(sector_name, ingest_ts) AS sector_name
    FROM {TBL} WHERE coverage_status = 'named' GROUP BY sector_code
) AS m ON k.sector_code = m.sector_code
"""

# 列清单无 MATERIALIZED/ALIAS（Code 44 规避）
INSERT_COLS = [
    "sector_code",
    "code_bare",
    "sector_name",
    "code_family",
    "coverage_status",
    "name_source",
    "tdx_type",
    "tdx_level",
    "map_version",
    "register_id",
    "source_sha256",
    "note",
    "ingest_ts",
]

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{TBL}/{VIEW}/INSERT_COLS 由模块常量注入；
# version（真源册指纹）为运行期入参，用 %s 占位由调用方传入，禁把值写进常量。
_SQL_HAVE_VERSION = f"SELECT count() FROM {TBL} WHERE map_version = '%s'"
_SQL_INSERT_VALUES = f"INSERT INTO {TBL} ({', '.join(INSERT_COLS)}) VALUES"
_SQL_CHK = f"SELECT count(), uniqExact(sector_code), countIf(coverage_status='named') FROM {TBL} FINAL"
_SQL_VIEW_NAMED = f"SELECT count() FROM {VIEW} WHERE period='1d' AND sector_name != ''"
_SQL_VIEW_TOTAL = f"SELECT count() FROM {VIEW} WHERE period='1d'"
_SQL_BASE_BLANKNAME = f"SELECT countIf(sector_name='') FROM {_T_SECTOR_880}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    reg = yaml.safe_load(REG.read_text(encoding="utf-8"))
    meta = reg["meta"]
    version = meta["map_version"]
    src_sha = json.dumps(meta["authoritative_source"]["file_sha256_and_mtime"], ensure_ascii=False)
    ing = now_utc()
    rows = [
        [
            r["sector_code"],
            r["code_bare"],
            r["sector_name"],
            r["code_family"],
            r["coverage_status"],
            r["name_source"],
            r["tdx_type"],
            r["tdx_level"],
            version,
            meta["register_id"],
            src_sha,
            r["note"],
            ing,
        ]
        for r in sorted(reg["rows"], key=lambda x: x["sector_code"])
    ]

    client = ch_writer.get_client()
    if args.dry_run:
        print(
            json.dumps(
                {"dry_run": True, "table": TBL, "view": VIEW, "rows": len(rows), "map_version": version},
                ensure_ascii=False,
            )
        )
        return

    client.execute(DDL)
    have = client.execute(_SQL_HAVE_VERSION % version)[0][0]
    if have < len(rows):
        client.execute(_SQL_INSERT_VALUES, rows, types_check=True)
    client.execute(VIEW_DDL)

    reader = DatabaseService().get_clickhouse_conn(role="reader")
    chk = reader.execute(_SQL_CHK)[0]
    named = reader.execute(_SQL_VIEW_NAMED)[0][0]
    total = reader.execute(_SQL_VIEW_TOTAL)[0][0]
    ok = chk[0] >= len(rows) and named > 0 and total > 0
    print(
        json.dumps(
            {
                "map_rows_total": chk[0],
                "map_codes": chk[1],
                "map_named": chk[2],
                "view_rows_1d": total,
                "view_rows_1d_named": named,
                "view_named_ratio": round(named / max(1, total), 4),
                "base_table_untouched": reader.execute(_SQL_BASE_BLANKNAME)[0][0],
                "verify": "PASS" if ok else "FAIL",
            },
            ensure_ascii=False,
            indent=1,
        )
    )
    if not ok:
        raise SystemExit(6)


if __name__ == "__main__":
    main()
