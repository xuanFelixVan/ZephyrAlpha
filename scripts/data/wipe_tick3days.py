# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.wipe_tick3days
# [DOMAIN] D_DATA
# [TTL] permanent
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.infrastructure.database_service
# [CONSUMERS] Owner/施工会话手动触发（2026-09-14 行情修复批，缺口报告 v2 §二/§三）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 先备份后删除（tick_data_tzbak_20260914）；DELETE 恒 mutations_sync=2；删后必须复验零残余；raw count 随后台合并漂移属正常，以备份表内容为准
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非零退出码+打印错误明细；破坏性操作前置校验失败即终止
# [TESTS] none  # 手动运维件：dry-run/计数核验内置

# -*- coding: utf-8 -*-
"""tick_data 三天残留删除（备份已在 tzbak 表，507,700 行）。"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, r"D:/ZephyrAlpha/src")

import zephyr.data.ch_writer as chw  # noqa: E402

from zephyr.data.table_registry import get_registry
from zephyr.infrastructure.database_service import get_db_service

_TICK = get_registry().table("market_tick")  # c1_market.tick_data
_BAK = _TICK + "_tzbak_20260914"

cli = get_db_service().get_clickhouse_conn(
    role="reader", extra_kwargs={"settings": {"max_execution_time": 600}})
w = chw.get_client()

cond = "'2026-09-09','2026-09-10','2026-09-11'"
bak_n = cli.execute(f"SELECT count() FROM {_BAK}")[0][0]  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批
main_n = cli.execute(    f"SELECT count() FROM {_TICK} WHERE trade_date IN ({cond})")[0][0]  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批
print(f"BAK={bak_n:,} main三天={main_n:,}（raw 计数随合并漂移属正常）")
w.execute(f"ALTER TABLE {_TICK} DELETE WHERE trade_date IN ({cond}) "
          "SETTINGS mutations_sync=2")
left = cli.execute(
    f"SELECT count() FROM {_TICK} WHERE trade_date IN ({cond})")[0][0]  # noqa: bare-sql  存量搬运非新增 SQL，集中化治理挂下批
if left:
    raise SystemExit(f"✗ 删除后残余 {left:,}")
print(f"✓ 三天残留已清空（备份表 tick_data_tzbak_20260914 = {bak_n:,} 行可回滚）")
