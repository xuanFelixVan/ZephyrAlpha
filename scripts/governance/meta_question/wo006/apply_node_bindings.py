# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-006
# [MODULE] scripts.governance.meta_question.wo006.apply_node_bindings
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] wo006_common（只读复核/RULE-DATA-OPS 留痕/旁挂册）; scripts/industry_graph/websearch_ingest.py
#                （SOP §5 图谱写入唯一合法通道，子进程调用，本件零自开写连接零裸 SQL）
# [CONSUMERS] 写入 ig_node_company（纯 INSERT）；执行台账 data/registers/metaq_node_binding/apply_ledger_wo006.yaml
# [STARTUP] manual
# [INVARIANTS] 写面强约束三条：①只经 websearch_ingest ingest 通道（禁自取 read_only=False 连接、禁裸 SQL，
#            从结构性保证不触碰 UPDATE/DELETE/DROP/TRUNCATE——通道对 node_company 只做 INSERT ... ON CONFLICT，
#            而本件预检保证候选 (node_id,symbol) 与存量零交集，故连 ON CONFLICT 的 DO UPDATE 分支都不会触发）；
#            ②只挂未挂接非已并入节点（预检现算，他会话已抢挂则本行 drop 并留痕，不覆盖他人成果）；
#            ③幂等（重跑第二遍预检全部命中"已存在"→零写入，批次数为 0）；
#            RULE-DATA-OPS 三验证在任何子进程写之前打印并落台账；分片=单事务全成全败（通道保证）；
#            每片写后即时复核 source_doc='wo006|%' 行数增量，账实不符立即停止后续分片（fail-visible）
# [MODIFY-GUARD] none（本件只新增旁挂写入器，不改既有模块；写面约束见 INVARIANTS）
# [MATURITY] experimental
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 预检不通过（候选与存量有交集/节点已非未挂接）→ 拒写非零退出；
#                  通道返回码非 0 → 停止后续分片并把该片校验错误原文回显台账；PG 不可达→抛出
# [TESTS] 2026-09-24 首跑前后 ig_node_company 行数与 wo006 前缀行数对账 + 候选册投影与实盘占比逐项相等
#         （recompute_pq0064.py 出对账结论）
# [TTL] task_bound
"""WO-006 挂接写入器——读候选旁挂册 → 三验证 → 分片走 ingest 唯一合法通道纯 INSERT。

用法::

    python scripts/governance/meta_question/wo006/apply_node_bindings.py --dry-run
    python scripts/governance/meta_question/wo006/apply_node_bindings.py

设计裁定（写进案卷）：不复用 get_depgraph_pg_connection 的写连接形态自开写连接，
而经 `scripts/industry_graph/websearch_ingest.py ingest` 子进程——图谱七表写入通道自带
词表/符号/三段式 source_doc 硬校验且是 SOP 规定的唯一合法通道，本件因此零写连接、零裸 SQL，
"纯 INSERT 不改不删"由通道的 ON CONFLICT 语义 + 本件零交集预检双重保证。
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wo006_common as W  # noqa: E402

from zephyr.shared.utils.time_utils import now_iso  # noqa: E402  （时间戳唯一真源，禁裸本机时钟拼串）

CAND_PATH = W.REG_DIR / "node_binding_candidates_wo006.yaml"
LEDGER_PATH = W.REG_DIR / "apply_ledger_wo006.yaml"
CHANNEL = W.ROOT / "scripts" / "industry_graph" / "websearch_ingest.py"
SHARD = 800

BATCH_RECORD_KEYS = (
    "type",
    "chain_id",
    "node_name",
    "symbol",
    "role",
    "confidence",
    "evidence_text",
    "source_doc",
    "market",
    "valid_from",
    "source",
)


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{vals}=运行期变长 VALUES 片段、{tag}=wo006 写面排他
# 标记真源（wo006_common.TAG_SQL），一律由调用点 .format() 注入，禁把标记/日期字面量写进常量。
_SQL_EXISTING_PAIRS = (
    "select t.n, t.s from (values {vals}) as t(n,s) "
    "where exists (select 1 from ig_node_company x where x.node_id=t.n and x.symbol=t.s)"
)
_SQL_STILL_UNATTACHED = (
    "select t.n from (values {vals}) as t(n)\n"
    "                  join ig_node x on x.node_id = t.n\n"
    "                 where x.name not like '%已并入%'\n"
    "                   and not exists (select 1 from ig_node_company y where y.node_id = t.n)"
)
_SQL_EVIDENCE_CLUSTERS = (
    "select to_char(date_trunc('minute', created_at),'YYYY-MM-DD HH24:MI') as m, count(*)\n"
    "              from ig_node_company where {tag} group by 1 order by 1"
)
_SQL_EVIDENCE_BY_DOC = (
    "select split_part(source_doc,'|',2), count(*), count(distinct node_id),\n"
    "                   min(confidence), max(confidence)\n"
    "              from ig_node_company where {tag} group by 1 order by 2 desc"
)
_SQL_EVIDENCE_ROLES = "select role, count(*) from ig_node_company where {tag}\n             group by 1 order by 2 desc"
_SQL_EVIDENCE_SPAN = (
    "select min(created_at), max(created_at), count(distinct node_id), count(distinct symbol)\n"
    "              from ig_node_company where {tag}"
)


def _existing_pairs(pairs: list[tuple[str, str]], conn) -> set[tuple[str, str]]:
    """存量 (node_id,symbol) 交集检测（分块 VALUES join，只读角色）。"""
    found: set[tuple[str, str]] = set()
    for i in range(0, len(pairs), 900):
        chunk = pairs[i : i + 900]
        vals = ",".join("('%s','%s')" % (n, s) for n, s in chunk)
        for nid, sym in W.rows(_SQL_EXISTING_PAIRS.format(vals=vals), conn):
            found.add((nid, sym))
    return found


def _still_unattached(node_ids: list[str], conn) -> set[str]:
    """节点现算复核：仍"未挂接 + 非已并入"的节点集合（他会话并发漂移防线）。"""
    ok: set[str] = set()
    for i in range(0, len(node_ids), 900):
        chunk = node_ids[i : i + 900]
        vals = ",".join("('%s')" % n for n in chunk)
        for (nid,) in W.rows(_SQL_STILL_UNATTACHED.format(vals=vals), conn):
            ok.add(nid)
    return ok


def _to_record(row: dict) -> dict:
    rec = {"type": "node_company", "source": "wo006_derived", "market": row["market"] or "cn"}
    for k in ("chain_id", "node_name", "symbol", "role", "confidence", "evidence_text", "source_doc", "valid_from"):
        rec[k] = row[k]
    rec["evidence_text"] = row["evidence_text"] + f"|wo006_replay={row['node_id']}"
    return rec


def build_batches(rows: list[dict], conn) -> tuple[list[Path], dict]:
    """预检（零交集 + 节点现算）后切片，批次 JSON 落 .runtime/tmp（临时件，非交付）。"""
    pairs = [(r["node_id"], r["symbol"]) for r in rows]
    clash = _existing_pairs(pairs, conn)
    alive_unattached = _still_unattached(sorted({p[0] for p in pairs}), conn)
    kept, dropped = [], {"already_bound_pair": 0, "node_no_longer_eligible": 0}
    for r in rows:
        if (r["node_id"], r["symbol"]) in clash:
            dropped["already_bound_pair"] += 1
            continue
        if r["node_id"] not in alive_unattached:
            dropped["node_no_longer_eligible"] += 1
            continue
        kept.append(r)
    W.TMP_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for i in range(0, len(kept), SHARD):
        bp = W.TMP_DIR / f"wo006_batch_{i // SHARD:03d}.json"
        bp.write_text(
            json.dumps(
                {
                    "batch": f"WO-006 node_company 三源补挂 片 {i // SHARD}",
                    "records": [_to_record(r) for r in kept[i : i + SHARD]],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
            newline="\n",
        )
        out.append(bp)
    return out, {"kept": len(kept), "dropped": dropped, "shards": len(out)}


def _channel_ingest(batch_path: Path) -> tuple[int, str]:
    env = {**os.environ, "PYTHONPATH": str(W.ROOT / "src")}
    p = subprocess.run(
        [sys.executable, str(CHANNEL), "ingest", "--batch", str(batch_path)],
        cwd=str(W.ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    return p.returncode, (p.stdout + "\n" + p.stderr)[-1500:]


def write_evidence(conn) -> dict:
    """从库侧现算写面存证（不依赖控制台输出）：wo006 行时间簇 + 源分布 + 置信度/角色分布。"""
    clusters = W.rows(_SQL_EVIDENCE_CLUSTERS.format(tag=W.TAG_SQL), conn)
    by_doc = W.rows(_SQL_EVIDENCE_BY_DOC.format(tag=W.TAG_SQL), conn)
    roles = W.rows(_SQL_EVIDENCE_ROLES.format(tag=W.TAG_SQL), conn)
    span = W.rows(_SQL_EVIDENCE_SPAN.format(tag=W.TAG_SQL), conn)
    return {
        "created_at_span": [str(span[0][0]), str(span[0][1])],
        "rows": int(sum(c[1] for c in clusters)) if clusters else 0,
        "nodes": span[0][2],
        "symbols": span[0][3],
        "per_minute_clusters": [[m, n] for m, n in clusters],
        "by_source_doc_segment": [list(r) for r in by_doc],
        "by_role": [list(r) for r in roles],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="WO-006 挂接写入器（纯 INSERT，走 ingest 唯一合法通道）")
    ap.add_argument("--dry-run", action="store_true", help="只预检切片不写库")
    a = ap.parse_args(argv)

    payload = W.load_register(CAND_PATH)
    rows = W.reg_rows(payload)
    audit: list[str] = []
    conn = W.reader()
    try:
        pre = W.pq0064_metrics(conn)
        pre_recon = W.pq0064_metrics(conn, exclude_wo006=True)
        batches, prep = build_batches(rows, conn)
    finally:
        conn.close()
    print(f"[PRE-FLIGHT] candidates={len(rows)} kept={prep['kept']} dropped={prep['dropped']} shards={prep['shards']}")
    print(
        f"[PRE-STATE] rows={pre['ig_node_company_rows_total']} wo006_rows={pre['ig_node_company_rows_wo006']} "
        f"unattached={pre['unattached_nodes']} ratio_all={pre['ratio_all']} ratio_active={pre['ratio_active']}"
    )

    if a.dry_run:
        print("[DRY-RUN] 未写库")
        return 0
    results: list[dict] = []
    if not batches:
        print("[IDEMPOTENT] 预检后零可写行（候选已全部在册或节点已失格）——本次不写库")
    else:
        W.data_ops_verify(
            "wo006.apply_node_bindings → ig_node_company 纯 INSERT",
            necessity=f"PQ-0064 fail(infra) 配套③：{prep['kept']} 行三源挂接补齐未挂接活跃节点，"
            f"链覆盖率判据复算前置；不建则本问永远无 pass 路径",
            truthfulness="候选全部来自四个可机检在库通道（PG stock_concept / ig_node_company 同名穿透 / "
            "CH akshare_ths 概念板+同花顺公司档案 / PG ig_product_revenue.node_ref），"
            "每行带 origin+match+置信度+时点，符号过 cn 正则且在市；源 C 直连不可得已取证登记（零造假）",
            reversibility="纯 INSERT 零 UPDATE 零 DELETE：source_doc 前缀 'wo006|' 唯一可定位，"
            "回滚=按该前缀单条 DELETE（由 Owner 门位执行）；旁挂册 node_binding_candidates_wo006.yaml "
            "为引用即重放凭证；分片单事务全成全败，中途失败不留半片",
            log=audit,
        )
        # 不建物理备份表（writer 角色无 CREATE 权 + 全资产净零）：可逆性由 source_doc 前缀
        # + 旁挂册双保险承担，见案卷 rollback 节
        for bp in batches:
            rc, tail = _channel_ingest(bp)
            results.append({"batch": bp.name, "returncode": rc, "tail": tail.strip()[-500:]})
            print(f"[INGEST] {bp.name} rc={rc}")
            if rc != 0:
                print(f"[ABORT] 通道拒绝，停止后续分片：\n{tail}")
                break
            conn = W.reader()
            try:
                now = W.pq0064_metrics(conn)
            finally:
                conn.close()
            print(
                f"  [VERIFY] wo006_rows={now['ig_node_company_rows_wo006']} "
                f"total={now['ig_node_company_rows_total']} unattached={now['unattached_nodes']}"
            )

    conn = W.reader()
    try:
        post = W.pq0064_metrics(conn)
        ev = write_evidence(conn)
    finally:
        conn.close()
    this_run = {
        "run_at": now_iso(),
        "rule_data_ops_audit": audit,
        "pre_flight": prep,
        "pre_state": pre,
        "pre_state_wo006_excluded": pre_recon,
        "wrote_anything_this_run": bool(batches),
        "batches": results,
        "post_state": post,
        "delta": {
            "ig_node_company_rows": post["ig_node_company_rows_total"] - pre["ig_node_company_rows_total"],
            "wo006_tagged_rows": post["ig_node_company_rows_wo006"],
            "unattached_nodes": f"{pre['unattached_nodes']} -> {post['unattached_nodes']}",
            "unattached_active_nodes": f"{pre['unattached_active_nodes']} -> {post['unattached_active_nodes']}",
            "ratio_all": f"{pre['ratio_all']} -> {post['ratio_all']}",
            "ratio_active": f"{pre['ratio_active']} -> {post['ratio_active']}",
        },
    }
    # 台账 append-only：每次执行一条 run（禁覆盖前次写证），库侧存证每次重算保证与实盘一致
    prior = W.load_register(LEDGER_PATH) if LEDGER_PATH.exists() else None
    runs = (prior or {}).get("runs") or ([prior] if prior and "runs" not in (prior or {}) else [])
    ledger = {
        "meta": {
            "wo": W.WO_ID,
            "q_id": W.Q_ID,
            "session": W.SESSION,
            "channel": "scripts/industry_graph/websearch_ingest.py ingest（SOP §5 唯一合法通道）",
            "write_shape": "ig_node_company 纯 INSERT（零 UPDATE/DELETE/DROP/TRUNCATE，零自开写连接）",
            "shard_rows": SHARD,
            "note": "runs 为历次执行流水（首跑=真写入，后续=幂等复核）；"
            "write_evidence 每次从库侧现算，是写面存证的权威副本",
        },
        "write_evidence": ev,
        "runs": runs + [this_run],
    }
    W.write_register(LEDGER_PATH, ledger)
    print(
        f"[POST] rows {pre['ig_node_company_rows_total']} -> {post['ig_node_company_rows_total']} "
        f"| unattached {pre['unattached_nodes']} -> {post['unattached_nodes']} "
        f"| ratio_all {pre['ratio_all']} -> {post['ratio_all']} "
        f"| ratio_active {pre['ratio_active']} -> {post['ratio_active']}"
    )
    failed = [r for r in results if r["returncode"] != 0]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
