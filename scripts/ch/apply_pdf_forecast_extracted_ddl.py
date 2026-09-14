# [BLUEPRINT] MOD-L04-001
# [MODULE] scripts.ch.apply_pdf_forecast_extracted_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service; schemas.categories.fundamental.pdf_forecast_extracted
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] DDL-as-Code: pdf_forecast_extracted DDL 真源为 schemas/categories/fundamental/pdf_forecast_extracted.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动 DDL 部署脚本（A 类一次性运维，幂等按需手动执行）
"""pdf_forecast_extracted 建表 DDL 部署 + 验证（C4 历史修复，2026-09-14）。

DDL 真源：schemas/categories/fundamental/pdf_forecast_extracted.py（DDL-as-Code）。
方案真源：docs/_working/2026-09-14-c4-history-repair-plan.md。

用法::

    python scripts/ch/apply_pdf_forecast_extracted_ddl.py           # 建表 + 验证
    python scripts/ch/apply_pdf_forecast_extracted_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.fundamental.pdf_forecast_extracted import (  # noqa: E402
    PDF_FORECAST_EXTRACTED_DDL,
    TABLE_NAME,
)
from zephyr.data import ch_reader  # noqa: E402


def apply() -> int:
    """DDL 用 admin 账号执行（writer 无 CREATE 权限，#ARCH-CH-027）。"""
    try:
        from zephyr.infrastructure.database_service import get_db_service

        c = get_db_service().get_clickhouse_conn(role="admin")
        c.execute(PDF_FORECAST_EXTRACTED_DDL)
        print(f"OK: {TABLE_NAME} DDL executed (IF NOT EXISTS, 幂等)")
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: DDL 执行失败: {exc}")
        return 2
    return verify()


def verify() -> int:
    """验证表存在且引擎正确。"""
    out = ch_reader.query(
        "SELECT engine FROM system.tables WHERE database = 'c3_fundamental' AND name = '" + TABLE_NAME + "'"
    )
    if not out:
        print(f"VERIFY FAIL: c3_fundamental.{TABLE_NAME} 不存在")
        return 1
    engine = out.strip().split("\t")[0]
    ok = "MergeTree" in engine
    print(f"VERIFY {'OK' if ok else 'FAIL'}: c3_fundamental.{TABLE_NAME} engine={engine}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else apply())
