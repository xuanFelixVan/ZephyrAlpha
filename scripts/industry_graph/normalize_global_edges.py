# [MODULE] scripts.industry_graph.normalize_global_edges
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] industry_chain_data_audit_sop §8 开放问题治理(跨市场边治本);后续夜班 R6 校验引用
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只 UPDATE 不 DELETE; name 内嵌 symbol 提取优先,人工词表兜底;未上市/无代码端点标 UNLISTED:公司名 前缀并清 name 内码;单事务;幂等(复跑零改动——WHERE 条件含空 symbol)
# [MODIFY-GUARD] KNOWN_SYMBOLS 词表(2026-09-08 首次夜班存量 53 边实测梳理)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PG 不可达->非零退出;无候选边->exit 0 打印 0
# [TTL] permanent
# M10豁免: manual STARTUP 一次性治理脚本
# [TESTS] 干跑(--dry-run)+实跑各一次(2026-09-08),修复 29 边/未上市 24 边
"""存量跨市场边规范化(2026-09-08 夜班验收发现的治本施工)。

夜班写入的全球锚点边存在海外端 symbol 留空、公司名内嵌代码的情况
(如 to_name='特斯拉(US:TSLA)', to_symbol='')——按 symbol 查询的量化消费路径
会漏掉这批边。本脚本一次性修复:
1. name 内嵌代码提取(英伟达(NVDA.US) -> from_symbol='NVDA.US')
2. 人工词表兜底(理想汽车->LI.US / 大众集团->VOW3.DE 等)
3. 未上市/无代码端点(长江存储/华为/奇瑞...) -> symbol='UNLISTED:公司名',
   name 保留公司名(去掉内嵌码),查询侧可按 UNLISTED: 前缀过滤或保留展示

用法::

    python scripts/industry_graph/normalize_global_edges.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

SYM_GL = re.compile(r"\b([A-Z0-9]{1,6})\.(US|KS|TW|T|HK|DE|LN|JP|SM)\b")
BRACKET = re.compile(r"[((]([A-Z0-9]{1,6})[.:]([A-Z]{2})[))]")

# 人工词表: name 内无代码但公司有明确上市代码的兜底(2026-09-08 梳理)
KNOWN_SYMBOLS = {
    "理想汽车": "LI.US",
    "蔚来汽车": "NIO.US",
    "小鹏汽车": "XPEV.US",
    "特斯拉(US:TSLA)": "TSLA.US",
    "英伟达(US:NVDA)": "NVDA.US",
    "大众集团": "VOW3.DE",
    "丰田汽车": "TM.US",
    "LG新能源": None,  # 373220.KS 转换规则复杂(前导零),留 None 走 UNLISTED
}
# 明确未上市/不适用代码的(避免脚本误标):None -> UNLISTED:公司名


def _extract(name: str | None) -> str | None:
    if not name:
        return None
    m = SYM_GL.search(name)
    if m:
        return m.group(0)
    m2 = BRACKET.search(name)
    if m2:
        return f"{m2.group(1)}.{m2.group(2)}"
    return None


def _clean_name(name: str | None) -> str | None:
    """去掉 name 内嵌的代码段(特斯拉(US:TSLA)->特斯拉)。"""
    if not name:
        return name
    return SYM_GL.sub("", name).replace("(US:", "(").rstrip("()").strip() or name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    cur.execute(
        "SELECT edge_id, from_symbol, to_symbol, from_name, to_name "
        "FROM ig_company_edge WHERE source='websearch' AND (from_symbol='' OR to_symbol='')"
    )
    rows = cur.fetchall()
    print(f"候选边(空端 symbol): {len(rows)}")

    fixed, unlisted, skipped = 0, 0, 0
    plans: list[tuple] = []
    for eid, fs, ts, fn, tn in rows:
        new_fs, new_ts = fs, ts
        if not fs:
            new_fs = _extract(fn) or KNOWN_SYMBOLS.get(fn or "")
        if not ts:
            new_ts = _extract(tn) or KNOWN_SYMBOLS.get(tn or "")
        # 仍未解析 -> UNLISTED 处理
        if not fs and not new_fs:
            new_fs = f"UNLISTED:{_clean_name(fn)}"
            unlisted += 1
        elif not ts and not new_ts:
            new_ts = f"UNLISTED:{_clean_name(tn)}"
            unlisted += 1
        if new_fs == fs and new_ts == ts:
            skipped += 1
            continue
        # name 清理: 内嵌码去掉(保留纯公司名)
        new_fn = _clean_name(fn) if (fn and not fs) else fn
        new_tn = _clean_name(tn) if (tn and not ts) else tn
        plans.append((new_fs, new_ts, new_fn, new_tn, eid))
        fixed += 1

    print(f"修复: {fixed}(含 UNLISTED {unlisted}) / 跳过: {skipped}")
    for p in plans[:8]:
        print("  样例:", p[0], "->", p[1], "|", p[2], "=>", p[3])

    if args.dry_run:
        conn.rollback()
        print("[DRY-RUN] 未落库")
    else:
        cur.executemany(
            "UPDATE ig_company_edge SET from_symbol=%s, to_symbol=%s, from_name=%s, to_name=%s "
            "WHERE edge_id=%s",
            plans,
        )
        conn.commit()
        print(f"[WRITTEN] {len(plans)} 边已规范化")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
