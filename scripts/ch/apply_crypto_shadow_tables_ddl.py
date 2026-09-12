# [MODULE] scripts.ch.apply_crypto_shadow_tables_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; schemas.categories.crypto_kline_daily
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] DDL-as-Code: crypto_kline_daily/crypto_shadow_gate DDL 真源为 schemas/categories/crypto_kline_daily.py; 全部幂等(CREATE IF NOT EXISTS); 影子表只记账不进决策链路; apply() 通过 ch_writer.query 执行; verify() 查 system.tables 验证引擎
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->打印错误+退出码2; 引擎不匹配->列出差异+退出码1; 全部匹配->退出码0
# [TESTS] none
# noqa: m11-perm-manual-legitimate  M11豁免: 手动 DDL 部署脚本（A 类一次性运维，按需手动执行；DDL 语义真源=schemas/categories/crypto_kline_daily.py 才是 permanent）
# [TTL] task_bound
"""ClickHouse crypto 影子 MVP 两表 DDL 部署 + 引擎验证脚本。

DDL-as-Code 模式（同款 apply_market_tables_ddl.py）：
    - crypto_kline_daily DDL 真源 = schemas/categories/crypto_kline_daily.py
    - crypto_shadow_gate  DDL 真源 = schemas/categories/crypto_kline_daily.py

背景：Owner 2026-09-11 免费影子模式裁定——C-L1 影子判定只记账不进决策；
两表落 c1_market 库（ClickHouse Hyper-V VM，与 A 股行情同库不同表，复用既有备份/监控通道）。

用法::

    python scripts/ch/apply_crypto_shadow_tables_ddl.py           # 建表 + 验证
    python scripts/ch/apply_crypto_shadow_tables_ddl.py --verify  # 仅验证

退出码：
    0 = 全部一致
    1 = 有不一致
    2 = ClickHouse 不可达
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
# 仓根入 path（schemas/categories/*.py DDL-as-Code 真源导入前提，同 apply_market_tables_ddl.py）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from zephyr.data import ch_reader, ch_writer
from schemas.categories.crypto_kline_daily import (
    CRYPTO_KLINE_DAILY_DDL,
    CRYPTO_SHADOW_GATE_DDL,
)

_TABLES = {
    "c1_market.crypto_kline_daily": CRYPTO_KLINE_DAILY_DDL,
    "c1_market.crypto_shadow_gate": CRYPTO_SHADOW_GATE_DDL,
}


def apply() -> int:
    """建表（幂等 CREATE IF NOT EXISTS）+ 建库前置容错。"""
    if not ch_writer.ensure_database("c1_market"):
        print("错误: c1_market 库不存在且无权限创建（治本路径=管理员预建，见 ch_writer.ensure_database docstring）")
        return 2
    rc = 0
    for table, ddl in _TABLES.items():
        print(f"应用 DDL: {table}")
        try:
            ch_writer.query(ddl)
        except Exception as e:  # noqa: BLE001 — 与 apply_market_tables_ddl.py 同款兜底
            print(f"错误: {table} 建表失败: {e}")
            rc = 2
    return rc


def verify() -> int:
    """查询 system.tables 验证两表存在且引擎为 ReplacingMergeTree。"""
    rc = 0
    for table in _TABLES:
        db, tbl = table.split(".", 1)
        out = ch_reader.query(
            f"SELECT engine FROM system.tables WHERE database = '{db}' AND name = '{tbl}'"
        ).strip()
        if not out:
            print(f"不一致: {table} 不存在")
            rc = 1
        elif "ReplacingMergeTree" not in out:
            print(f"不一致: {table} 引擎={out}（预期 ReplacingMergeTree）")
            rc = 1
        else:
            print(f"一致: {table} 引擎={out}")
    return rc


def main() -> int:
    rc = apply()
    if rc != 0:
        print("ClickHouse 不可达或建表失败，跳过验证")
        return rc
    return verify()


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(verify())
    sys.exit(main())
