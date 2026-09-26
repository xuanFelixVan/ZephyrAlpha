# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §1.1(断言段 pit_assertion) + 工单 WO-B3
# [MODULE] scripts.governance.meta_question.wo_b3_macro.macro_vintage
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.data.macro_vintage（唯一真源，scripts 侧不可直接 import 先例同 tests：本地 sys.path 引导）
# [CONSUMERS] apply_macro_vintage_ddl.py / register_macro_history_inventory.py / audit_macro_vintage.py（同目录 import macro_vintage as mv）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 本文件是 zephyr.data.macro_vintage 的兼容重导出 shim（单一血统治本：
#   全量副本曾与真源 95% AST 同构被 FILE-COPY 门拦，且 PIT 参数化视图在真源侧已按
#   实测 Code 90 证据改为 DROP 清理——任何行为语义只在真源改，此处禁止新增逻辑。
#   新增导出名=在真源实现后在此显式列出，禁 import *（防隐式漂移）。）
# [MODIFY-GUARD] none（新建文件；入库侧改造以 patch 交付，不直改 src/）
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 真源 import 失败即 ImportError 向上抛（fail-closed，不降级副本）。
# [TESTS] python -m pytest tests/governance/meta_question tests/data/test_macro_vintage_mirror.py -q
# [A_module] module_id=MOD-CHAINPILE-METAQ | layer=script | stability=new | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""macro_vintage — 工单侧兼容重导出 shim（真源=src/zephyr/data/macro_vintage.py）。

WO-B3 三件工单脚本（apply/register/audit）历史上以同目录兄弟模块形态 import 本名；
真源收敛进 src/zephyr/data 后，本文件只做显式名字重导出，保持既有 import 行为零改动。
发布时戳三态/版次推导/PIT 取数等全部语义不变，见真源 docstring。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from zephyr.data.macro_vintage import (  # noqa: E402
    _BASIS_BACKFILL,
    _BASIS_OBSERVED,
    _BASIS_OFFICIAL,
    ALL_COLUMNS,
    DDL_STATEMENTS,
    PIT_LATEST_SQL,
    TABLE_VINTAGE,
    build_backfill_rows,
    insert_sql,
    inventory_sql,
    resolve_vintages,
    write_vintage_rows,
)

__all__ = [
    "ALL_COLUMNS",
    "DDL_STATEMENTS",
    "PIT_LATEST_SQL",
    "TABLE_VINTAGE",
    "_BASIS_BACKFILL",
    "_BASIS_OBSERVED",
    "_BASIS_OFFICIAL",
    "build_backfill_rows",
    "insert_sql",
    "inventory_sql",
    "resolve_vintages",
    "write_vintage_rows",
]
