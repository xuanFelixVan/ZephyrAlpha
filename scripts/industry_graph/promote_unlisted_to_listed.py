# [MODULE] scripts.industry_graph.promote_unlisted_to_listed
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] SOP industry_chain_data_audit_sop §4.10 上市替换流程步骤2(通用工具,任何实体上市均可复用)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只 UPDATE 不 DELETE; 幂等(已无 UNLISTED:UE-xxx 引用则零副作用); 只处理编码表 status='listed' 且 listed_symbol 非空的实体(标定须先走 ingest unlisted_entity 通道+一手来源); 前置=编码表已标定,本脚本不做标定(防训练记忆编代码)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->抛出; 无待替换行->打印 0 条正常退出
# [TTL] permanent
# M10豁免: manual STARTUP 治理脚本
# [TESTS] 2026-09-08 首跑: 长鑫存储 UE-f4b20d6e5983->688825.SH 2 条边换码(上交所上市公告书一手来源)
"""UNLISTED 实体上市替换（SOP §4.10 上市替换流程步骤 2）。

前置：编码表已标 status='listed' 且 listed_symbol 已回填（走 ingest
unlisted_entity 通道，source_doc 须一手来源——交易所上市公告书）。

本脚本扫全库 ig_company_edge：UNLISTED:UE-{12hex} 引用中实体已 listed 的
→ symbol 换成 listed_symbol（全库存量边一键换真码，幂等）。

用法::

    python scripts/industry_graph/promote_unlisted_to_listed.py
"""
import sys

sys.path.insert(0, r"d:\ZephyrAlpha\src")

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection


def main() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()

    # 1. 取已标定实体(ue_id -> listed_symbol)
    cur.execute("SELECT ue_id, name, listed_symbol FROM ig_unlisted_entity WHERE status='listed' AND listed_symbol IS NOT NULL")
    listed = cur.fetchall()
    if not listed:
        print("[OK] 编码表无已标定实体,无替换需求")
        conn.close()
        return 0

    # 2. 扫边表换码(逐实体,只 UPDATE)
    total_changed = 0
    for ue_id, name, real_sym in listed:
        cur.execute(
            "SELECT count(*) FROM ig_company_edge WHERE from_symbol=%s OR to_symbol=%s",
            (f"UNLISTED:{ue_id}", f"UNLISTED:{ue_id}"),
        )
        pending = cur.fetchone()[0]
        if pending == 0:
            continue
        cur.execute("UPDATE ig_company_edge SET from_symbol=%s WHERE from_symbol=%s", (real_sym, f"UNLISTED:{ue_id}"))
        cur.execute("UPDATE ig_company_edge SET to_symbol=%s WHERE to_symbol=%s", (real_sym, f"UNLISTED:{ue_id}"))
        print(f"  [PROMOTE] {name} ({ue_id}) -> {real_sym}: {pending} 条边换码")
        total_changed += pending

    conn.commit()

    # 3. 终检:已 listed 实体的 UE 码在边表残留必须为 0
    residual = 0
    for ue_id, name, _sym in listed:
        cur.execute(
            "SELECT count(*) FROM ig_company_edge WHERE from_symbol=%s OR to_symbol=%s",
            (f"UNLISTED:{ue_id}", f"UNLISTED:{ue_id}"),
        )
        residual += cur.fetchone()[0]
    conn.close()

    print(f"[DONE] 换码 {total_changed} 条,已标定实体 UE 码残留 {residual} 条")
    return 0 if residual == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
