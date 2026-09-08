# [MODULE] scripts.industry_graph.migrate_unlisted_entities
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] SOP industry_chain_data_audit_sop §4.10 开放问题9 裁定执行(2026-09-08 Owner:现在就干,规则先统一防夜班幻觉)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只 UPDATE 不 DELETE; 幂等(旧格式正则不匹配 UE- 新格式,重跑零副作用); 实体登记 ON CONFLICT (name,country) 幂等; UE-id 与 CH-/ND- 同 md5 风格; 上市标定(listed+symbol)不在本脚本——须一手来源核实后另跑(防训练记忆编代码)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->抛出; 无旧格式行->打印 0 条正常退出
# [TTL] permanent
# M10豁免: manual STARTUP 一次性治理脚本
# [TESTS] 2026-09-08 实跑: 7 实体登记/23 边换码/复跑 0 条(幂等验证)
"""UNLISTED 旧格式迁移（SOP §4.10 开放问题 9 裁定执行，2026-09-08）。

存量 23 条 `UNLISTED:公司名` 边 -> 登记 ig_unlisted_entity 编码表
-> 边表 symbol 换 `UNLISTED:UE-{12hex}`（编码表主键引用）。

已上市实体的 symbol 标定（listed+listed_symbol）不在本脚本——须一手来源
（交易所公告）核实后单独执行（§4.10 上市替换三步），防训练记忆编代码。

用法::

    python scripts/industry_graph/migrate_unlisted_entities.py
"""
import hashlib
import re
import sys

sys.path.insert(0, r"d:\ZephyrAlpha\src")

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

# 旧格式检测: UNLISTED: 后不是 UE-{12hex} 即旧格式(公司名直写)
OLD_UNLISTED_RE = re.compile(r"^UNLISTED:(?!UE-[0-9a-f]{12}$).+")
# 实体国家词表(名称可判的先判,其余默认 CN;词表缺项按 CN 登记不猜)
COUNTRY_HINTS = {
    "LG新能源": "KR",
    "LG化学": "KR",
    "SK On": "KR",
}


def ue_id_for(name: str, country: str) -> str:
    h = hashlib.md5(f"{name}|{country}".encode("utf-8")).hexdigest()[:12]
    return f"UE-{h}"


def main() -> int:
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()

    # 1. 收集旧格式边(幂等锚:旧格式正则天然排除 UE- 新格式)
    cur.execute(
        "SELECT edge_id, from_symbol, to_symbol, from_name, to_name, source_doc "
        "FROM ig_company_edge "
        "WHERE from_symbol ~ '^UNLISTED:' OR to_symbol ~ '^UNLISTED:'"
    )
    rows = cur.fetchall()
    todo = [r for r in rows if OLD_UNLISTED_RE.match(r[1] or "") or OLD_UNLISTED_RE.match(r[2] or "")]
    print(f"[SCAN] UNLISTED 边 {len(rows)} 条, 其中旧格式 {len(todo)} 条")

    if not todo:
        print("[OK] 无旧格式行,幂等退出")
        conn.close()
        return 0

    # 2. 唯一实体清单
    entities: dict[str, dict] = {}
    for _eid, fsym, tsym, fname, tname, sdoc in todo:
        for sym, name in ((fsym, fname), (tsym, tname)):
            if sym and OLD_UNLISTED_RE.match(sym):
                pure = sym[len("UNLISTED:"):]
                entities.setdefault(pure, {
                    "name": pure,
                    "country": COUNTRY_HINTS.get(pure, "CN"),
                    "source_doc": sdoc,
                })

    # 3. 登记编码表(ON CONFLICT 幂等,不覆盖已有 status/listed_symbol)
    from datetime import date
    as_of = date.today().isoformat()
    for pure, ent in sorted(entities.items()):
        uid = ue_id_for(ent["name"], ent["country"])
        cur.execute(
            """
            INSERT INTO ig_unlisted_entity (ue_id, name, country, status, source_doc, as_of)
            VALUES (%s, %s, %s, 'unlisted', %s, %s)
            ON CONFLICT (name, country) DO UPDATE
            SET source_doc = EXCLUDED.source_doc, updated_at = now()
            """,
            (uid, ent["name"], ent["country"], ent["source_doc"], as_of),
        )
        print(f"  [ENTITY] {pure} ({ent['country']}) -> {uid}")

    # 4. 边表换码(只 UPDATE 不 DELETE;UNIQUE 锚 (from_symbol,to_symbol,year,source) 无撞行风险——UE 新码本不存在)
    changed = 0
    for _eid, fsym, tsym, fname, tname, _sdoc in todo:
        new_f, new_t = fsym, tsym
        if fsym and OLD_UNLISTED_RE.match(fsym):
            pure = fsym[len("UNLISTED:"):]
            new_f = f"UNLISTED:{ue_id_for(pure, COUNTRY_HINTS.get(pure, 'CN'))}"
        if tsym and OLD_UNLISTED_RE.match(tsym):
            pure = tsym[len("UNLISTED:"):]
            new_t = f"UNLISTED:{ue_id_for(pure, COUNTRY_HINTS.get(pure, 'CN'))}"
        cur.execute(
            "UPDATE ig_company_edge SET from_symbol=%s, to_symbol=%s WHERE edge_id=%s",
            (new_f, new_t, _eid),
        )
        changed += 1

    conn.commit()

    # 5. 终检:旧格式清零 + 新格式计数
    cur.execute(
        "SELECT count(*) FROM ig_company_edge WHERE from_symbol ~ '^UNLISTED:' AND from_symbol !~ '^UNLISTED:UE-[0-9a-f]{12}$'"
        " OR to_symbol ~ '^UNLISTED:' AND to_symbol !~ '^UNLISTED:UE-[0-9a-f]{12}$'"
    )
    dirty = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM ig_unlisted_entity")
    total_ent = cur.fetchone()[0]
    conn.close()

    print(f"[DONE] 实体登记 {len(entities)} 家(表内共 {total_ent}), 边换码 {changed} 条, 残留旧格式 {dirty} 条")
    return 0 if dirty == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
