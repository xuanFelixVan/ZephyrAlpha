# [BLUEPRINT] MOD-L04-001
# [MODULE] scripts.ch.apply_cross_asset_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service; zephyr.data.ch_reader; schemas.categories.market.market_cftc_positioning; schemas.categories.market.market_gold_etf_holdings
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] DDL-as-Code: D5 跨资产两表 DDL 真源为 schemas/categories/market/market_cftc_positioning.py 与 market_gold_etf_holdings.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动 DDL 部署脚本（A 类一次性运维，幂等按需手动执行）
"""D5 跨资产两表 DDL 部署 + 验证（CFTC 持仓 + SPDR 黄金 ETF 持仓，2026-09-18）。

DDL 真源（DDL-as-Code）：
    schemas/categories/market/market_cftc_positioning.py
    schemas/categories/market/market_gold_etf_holdings.py

为什么不走 apply_market_tables_ddl.py：该文件为全流通战役 residG 车道独占（COORDINATION_LEDGER
§2 所有权地图），且已知被 legacy reconciliation_differences 坏 DDL 毒化（首败致 TCP 失效 →
HTTP 伪通道 500 → verify 失真，晨报遗留 7）。照 apply_irm_extraction_ddl.py /
apply_pdf_forecast_extracted_ddl.py 先例独立成件，走 DatabaseService admin 通道
（writer 无 CREATE 权限，#ARCH-CH-027）。

用法::

    python scripts/ch/apply_cross_asset_ddl.py           # 建表 + 验证
    python scripts/ch/apply_cross_asset_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.market.market_cftc_positioning import (  # noqa: E402
    CFTC_POSITIONING_DDL,
    TABLE_NAME as CFTC_TABLE,
)
from schemas.categories.market.market_gold_etf_holdings import (  # noqa: E402
    GOLD_ETF_HOLDINGS_DDL,
    TABLE_NAME as GOLD_TABLE,
)
from zephyr.data import ch_reader  # noqa: E402

_ALL: list[tuple[str, str]] = [
    ("c1_market." + CFTC_TABLE, CFTC_POSITIONING_DDL),
    ("c1_market." + GOLD_TABLE, GOLD_ETF_HOLDINGS_DDL),
]

# NO-BARE-SQL 合规：SQL 提为模块级常量，plain 赋值不加 Final
# （门判据 _extract_sql_constant_lines 只识别 ast.Assign，加注解反而不被豁免）。
# system.tables 是 CH 系统视图、非业务表，不入 TableRegistry（TABLE-NAME-REGISTRY 只管已注册品类表）。
SQL_ENGINE_PROBE = (
    "SELECT engine FROM system.tables WHERE database = '{db}' AND name = '{tbl}'"
)


def apply() -> int:
    """DDL 用 admin 账号执行（writer 无 CREATE 权限，#ARCH-CH-027）。"""
    try:
        from zephyr.infrastructure.database_service import get_db_service

        c = get_db_service().get_clickhouse_conn(role="admin")
        for fq, ddl in _ALL:
            c.execute(ddl)
            print(f"OK: {fq} DDL executed (IF NOT EXISTS, 幂等)")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: DDL 执行失败: {exc}")
        return 2
    return verify()


def verify() -> int:
    """验证两表存在且引擎正确。"""
    bad = 0
    for fq, _ddl in _ALL:
        db, tbl = fq.split(".", 1)
        out = ch_reader.query(SQL_ENGINE_PROBE.format(db=db, tbl=tbl))
        if not out:
            print(f"VERIFY FAIL: {fq} 不存在")
            bad += 1
            continue
        engine = out.strip().split("\t")[0]
        ok = "MergeTree" in engine
        print(f"VERIFY {'OK' if ok else 'FAIL'}: {fq} engine={engine}")
        if not ok:
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else apply())
