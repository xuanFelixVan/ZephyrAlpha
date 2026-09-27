# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md | §1
# [MODULE] zephyr.library.ledger_fingerprint
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.librarian (PgConnection 协议，注入连接零自建); zephyr.library.ledger_schema (lib_events DDL 真源)
# [CONSUMERS] zephyr.library.ledger_cache
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 账本级世代指纹的**唯一**实现（S1 案 B：max(event_id)，lib_events PK btree O(1)，实测 3.45ms）；SQL=共享常量 SQL_LEDGER_FINGERPRINT，世代缓存/磁盘快照一律 import，禁分头写 SQL（S1 §⑤ 施工条件·单写者公理）；本探测恒**现读真源**——它是缓存层的裁判而非客户（S4 §⑤ 不可缓存位第二条）；指纹推进前提=馆员 INVARIANT「event 与 state 同事务（写必留痕）」；数据订正一律走 act()/register_batch，禁绕过馆员直改 lib_assets（S1 §4.2 F1"订正必补事件"条款落点）
# [MODIFY-GUARD] gate_id 不适用；变更走 08 §6 增枝制
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 异常原样上抛（本件不吞异常，降级口径由调用方决定）；lib_events 空表 → 指纹 0
# [TESTS] tests/library/test_ledger_cache.py
# [A_module] module_id=MOD-LIB-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ledger_fingerprint.py — 账本级世代指纹（世代水位）唯一读出件（MOD-LIB-001 常量层）。

世代指纹回答"总账现在属于哪一代"：`lib_events.event_id` 是全账本单调追加序列，
任何入账/变更都同事务插一行事件，故 `max(event_id)` 即账本水位——零 DDL、零新写者、
零旁路写洞（S1 簿 §4.2 案 B，§4.4 实测优于 max(built_at) 的 15.9ms 全表扫）。

Usage::

    from zephyr.library.ledger_fingerprint import read_ledger_fingerprint

    conn = get_depgraph_pg_connection()           # 连接由调用方借还（本件零自建连接）
    try:
        version = read_ledger_fingerprint(conn)   # 现读，永不缓存
    finally:
        release_depgraph_pg_connection(conn)

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/ledger_fingerprint.yaml
"""

from __future__ import annotations

from typing import Final

from zephyr.library.librarian import PgConnection

#: 账本级世代指纹 SQL（共享常量真源：S2 世代缓存与 S3 磁盘快照同 import，禁各自拼装）
#: 多行常量形态与 ledger_schema._SQL_LOOKUP 同族（NO-BARE-SQL 行级判定按行匹配）
SQL_LEDGER_FINGERPRINT: Final[str] = """
SELECT max(event_id)
FROM lib_events
"""


def read_ledger_fingerprint(conn: PgConnection) -> int:
    """现读账本世代水位（世代指纹）——缓存失效判定的唯一原料。

    Args:
        conn: depgraph PG 连接（结构满足 :class:`~zephyr.library.librarian.PgConnection`；
            池化借还由调用方负责，本件不建连不关连）。

    Returns:
        ``lib_events`` 当前最大 event_id；事件表为空时返回 0。

    Raises:
        Exception: DB 异常原样上抛（含只读角色权限缺失/连接断开）——水位读不到
            就必须让调用方显式选边（服务旧代要打标，或干脆报错），禁在本件吞成 0。
    """
    with conn.cursor() as cur:
        cur.execute(SQL_LEDGER_FINGERPRINT)
        row = cur.fetchone()
    value = row[0] if row else None
    return int(value) if value is not None else 0
