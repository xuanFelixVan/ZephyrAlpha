# [BLUEPRINT] MOD-L04-001
# [MODULE] scripts.ch.apply_irm_extraction_ddl
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service; schemas.categories.fundamental.irm_interactive_qa; schemas.categories.fundamental.irm_interactive_extraction; schemas.categories.fundamental.ir_activity_record; schemas.categories.fundamental.ir_activity_extraction
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] DDL-as-Code: D7 文本抽取四表 DDL 真源为 schemas/categories/fundamental/irm_*.py 与 ir_*.py
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 表不存在->建表; 引擎不匹配->退出码1
# [TESTS] 本脚本 --verify 即验证
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 手动 DDL 部署脚本（A 类一次性运维，幂等按需手动执行）
"""D7 文本抽取四表 DDL 部署 + 验证（C6 互动易 + C9 调研纪要，2026-09-18）。

DDL 真源（DDL-as-Code）：
    schemas/categories/fundamental/irm_interactive_qa.py
    schemas/categories/fundamental/irm_interactive_extraction.py
    schemas/categories/fundamental/ir_activity_record.py
    schemas/categories/fundamental/ir_activity_extraction.py

c3_fundamental 域表不走 apply_market_tables_ddl（其 verify 只查 c1_market），
照 pdf_forecast_extracted 先例独立成件（scripts/ch/apply_pdf_forecast_extracted_ddl.py）。

用法::

    python scripts/ch/apply_irm_extraction_ddl.py           # 建表 + 验证
    python scripts/ch/apply_irm_extraction_ddl.py --verify  # 仅验证
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from schemas.categories.fundamental.irm_interactive_qa import (  # noqa: E402
    IRM_INTERACTIVE_QA_DDL,
    TABLE_NAME as QA_TABLE,
)
from schemas.categories.fundamental.irm_interactive_extraction import (  # noqa: E402
    IRM_INTERACTIVE_EXTRACTION_DDL,
    TABLE_NAME as QA_EXT_TABLE,
)
from schemas.categories.fundamental.ir_activity_record import (  # noqa: E402
    IR_ACTIVITY_RECORD_DDL,
    TABLE_NAME as IR_TABLE,
)
from schemas.categories.fundamental.ir_activity_extraction import (  # noqa: E402
    IR_ACTIVITY_EXTRACTION_DDL,
    TABLE_NAME as IR_EXT_TABLE,
)
from zephyr.data import ch_reader  # noqa: E402

_ALL: list[tuple[str, str]] = [
    ("c3_fundamental." + QA_TABLE, IRM_INTERACTIVE_QA_DDL),
    ("c3_fundamental." + QA_EXT_TABLE, IRM_INTERACTIVE_EXTRACTION_DDL),
    ("c3_fundamental." + IR_TABLE, IR_ACTIVITY_RECORD_DDL),
    ("c3_fundamental." + IR_EXT_TABLE, IR_ACTIVITY_EXTRACTION_DDL),
]


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
    """验证四表存在且引擎正确。"""
    bad = 0
    for fq, _ddl in _ALL:
        db, tbl = fq.split(".", 1)
        out = ch_reader.query(
            "SELECT engine FROM system.tables WHERE database = '" + db + "' AND name = '" + tbl + "'"
        )
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
