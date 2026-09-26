# [BLUEPRINT] MOD-METAQ-REEXAM-DSRHYTHM | docs/_working/meta_question_answers/gaps/PQ-0172_workbook.md §六向台账 + PQ-0196_workbook.md §六向台账
# [MODULE] scripts.governance.meta_question.reexam.dsrhythm.writeback_dsrhythm
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pyyaml; zephyr.governance.depgraph_schema (PG 读写，仅限 meta_question schema)
# [CONSUMERS] meta_question.meta_question_exam_result / meta_question.meta_question_audit（纯追加）
# [STARTUP] manual（python scripts/governance/meta_question/reexam/dsrhythm/writeback_dsrhythm.py [--dry-run]）
# [MATURITY] testing
# [INVARIANTS] 只写 meta_question schema；零 UPDATE/零 DELETE，历史行不可触碰；
#              裁决写 conclusion JSONB 的 outcome 键，列 outcome 恒为生命周期 'answered'；
#              conclusion 必含 11 规范键（outcome/conclusion/evidence/fail_type/confidence/data_window/
#              exam_ref/pit_assertion/three_check/notes/threshold），附加键只增不换；
#              confidence/data_window 列为 jsonb → 必传 json.dumps(default=str)；
#              案卷非法裁决（非 pass/fail/insufficient）→ 跳过并打印，不猜；
#              任一步异常 → conn.rollback() 非零退出；回写后三态和 != 283 → 回滚
# [MODIFY-GUARD] docs/_working/meta_question_answers/casefiles/REEXAM-DSRHYTHM.yaml
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 案卷缺失/判据缺键→raise；PG 写失败→rollback 非零退出；
#                  三态自证不通过→rollback 并报告（禁硬回写）
# [TESTS] --dry-run 全形状自检（11 键齐 + jsonb 列可序列化），真写后跑 _SQL_TRISTATE 自证
# [A_module] module_id=MOD-METAQ-REEXAM-DSRHYTHM | layer=script | stability=volatile | safety=M | ai_autonomy=human_gated
# [TTL] task_bound
"""DS 节奏族复考结论回写 PG（PQ-0172 / PQ-0196，纯追加，照总包范式）。

形状契约：meta_question.meta_question_exam_result 列 outcome = 生命周期（写 'answered'），
裁决在 conclusion JSONB 的 outcome 键（pass/fail/insufficient）——全仓三态读的是 JSONB 那个。

用法：
    python scripts/governance/meta_question/reexam/dsrhythm/writeback_dsrhythm.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

S = "meta_question"
ACTOR = "st-metaq-gc-20260924"
CASEFILE = Path("D:/ZephyrAlpha/docs/_working/meta_question_answers/casefiles/REEXAM-DSRHYTHM.yaml")
REQUIRED_KEYS = (
    "outcome",
    "conclusion",
    "evidence",
    "fail_type",
    "confidence",
    "data_window",
    "exam_ref",
    "pit_assertion",
    "three_check",
    "notes",
    "threshold",
)

# NO-BARE-SQL：本脚本 SQL 集中于此。
_SQL_APPEND = (
    f"insert into {S}.meta_question_exam_result "
    "(q_id, exam_ref, conclusion, confidence, data_window, pit_assertion, outcome, recorded_by) "
    "values (%s, %s, %s, %s, %s, %s, %s, %s)"
)
_SQL_PRIOR = (
    f"select conclusion, confidence, data_window from {S}.meta_question_exam_result "
    f"where q_id = %s and conclusion->>'outcome' is not null "
    f"order by created_at desc limit 1"
)
_SQL_TRISTATE = (
    f"select conclusion->>'outcome', count(*) from ("
    f"  select distinct on (q_id) conclusion from {S}.meta_question_exam_result"
    f"  order by q_id, created_at desc) t group by 1 order by 2 desc"
)
_SQL_AUDIT_APPEND = (
    f"insert into {S}.meta_question_audit (q_id, actor, what, before, after, evidence) values (%s, %s, %s, %s, %s, %s)"
)


def _conclusion(qid: str, ex: dict, doc: dict, verdict: str) -> dict:
    """Assemble the canonical 11-key conclusion JSONB (extra keys appended only)."""
    ref = ex["exam_plan_ref"]
    items = doc["reconciliation"][qid]["items"]
    head = "; ".join(f"{it.get('item_no')}.{str(it.get('item'))[:60]}" for it in items)
    concl = {
        "outcome": verdict,
        "conclusion": (
            f"复考（两面真算对账）：判据「{ref['criterion']}」阈值「{ref['threshold']}」"
            f"→ 不一致项={len(items)} ≠ 0 → {verdict}。逐项：{head}"
        ),
        "evidence": [
            {
                "probe": doc["reexam_engine"]["dir"] + "exam_dsrhythm.py",
                "machine_output": doc["writeback"]["machine_output"],
                "query": str(ex.get("impl", ""))[:700],
                "result": ex.get("metrics", {}),
                "registered_side_head": doc["registered_side"].get(qid, {}),
                "reconciliation_items": items,
                "payload_md5": doc["reexam_engine"]["determinism"]["payload_md5"],
            }
        ],
        "fail_type": ex.get("fail_type"),
        "confidence": ex.get("confidence"),
        "data_window": ex.get("pit", {}),
        "exam_ref": f"{ACTOR}/reexam/dsrhythm/{qid}",
        "pit_assertion": str(ex.get("pit_assertion", "")),
        "three_check": ex.get("three_check", {}),
        "notes": str(ex.get("notes", "")),
        "threshold": ref.get("threshold"),
        # ── 附加键（不替换规范键）──
        "reexam_engine": doc["reexam_engine"]["dir"],
        "threshold_check": ex.get("threshold_check", {}),
        "n_inconsistency_items": len(items),
        "inconsistency_items": items,
        "method": ref.get("method"),
        "casefile": str(CASEFILE),
        "supersedes": f"fail(原判 不一致项=1, st-metaq-20260923/probe/periph_a_{qid})",
        "precondition_landing": {
            "small_fix_batch_0cd098e56b_in_head": doc["precondition_landing"]["small_fix_batch"]["in_head"],
            "wo010_ds_book_annotation_in_head": doc["precondition_landing"]["wo010_ds_book_annotation"][
                "landed_in_head"
            ],
            "head_sha": doc["precondition_landing"]["head_sha_at_exam"],
        },
    }
    missing = [k for k in REQUIRED_KEYS if k not in concl]
    if missing:
        raise RuntimeError(f"{qid} conclusion 缺规范键 {missing}")
    return concl


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    doc = yaml.safe_load(CASEFILE.read_text(encoding="utf-8"))
    exams = doc["exams"]

    # 恒取 writer 角色：--dry-run 走同一条写路径但结尾显式 rollback（零落地），
    # 这样形状自检与真写完全同构（避免 reader 角色下 INSERT 假失败）
    conn = get_depgraph_pg_connection(read_only=False)
    cur = conn.cursor()
    written: list[tuple[str, str | None, str]] = []
    try:
        for qid, ex in sorted(exams.items()):
            verdict = ex.get("outcome")
            if verdict not in ("pass", "fail", "insufficient"):
                print(f"  [SKIP] {qid}: 非法裁决 {verdict!r}")
                continue
            cur.execute(_SQL_PRIOR, (qid,))
            row = cur.fetchone()
            prior = (json.loads(row[0]) if isinstance(row[0], str) else (row[0] or {})) if row else {}
            concl = _conclusion(qid, ex, doc, verdict)
            cur.execute(
                _SQL_APPEND,
                (
                    qid,
                    concl["exam_ref"],
                    json.dumps(concl, ensure_ascii=False, default=str),
                    json.dumps(
                        {
                            "basis": "登记面 HEAD 逐字回读 + CH FINAL 全窗实测 + 45 份健康日志覆盖度",
                            "score": concl["confidence"],
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                    json.dumps(concl["data_window"], ensure_ascii=False, default=str),
                    concl["pit_assertion"],
                    "answered",
                    ACTOR,
                ),
            )
            cur.execute(
                _SQL_AUDIT_APPEND,
                (
                    qid,
                    ACTOR,
                    "update",
                    json.dumps(
                        {
                            "outcome": prior.get("outcome"),
                            "n_inconsistency_items": (prior or {}).get("n_inconsistency_items"),
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                    json.dumps(
                        {
                            "outcome": verdict,
                            "fail_type": concl["fail_type"],
                            "n_inconsistency_items": concl["n_inconsistency_items"],
                        },
                        ensure_ascii=False,
                        default=str,
                    ),
                    f"reexam dsrhythm engine={doc['reexam_engine']['dir']} "
                    f"payload_md5={doc['reexam_engine']['determinism']['payload_md5']}",
                ),
            )
            written.append((qid, prior.get("outcome"), verdict))
        cur.execute(_SQL_TRISTATE)
        dist = {str(r[0]): r[1] for r in cur.fetchall()}
        total = sum(dist.values())
        print("post-write tri-state:", dist, "sum:", total)
        if total != 283:
            raise RuntimeError(f"三态和={total} != 283，回滚")
        if args.dry_run:
            conn.rollback()
            print("[DRY-RUN] 已回滚，零落地")
            return 0
        conn.commit()
    except Exception as exc:  # noqa: BLE001
        conn.rollback()
        print(f"[ABORT-ROLLED-BACK] {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        cur.close()
        conn.close()

    for q, old, new in written:
        print(f"  {q}: {old} -> {new}")
    c2 = get_depgraph_pg_connection()
    k = c2.cursor()
    k.execute(_SQL_TRISTATE)
    dist2 = {str(r[0]): r[1] for r in k.fetchall()}
    k.close()
    c2.close()
    print("committed; re-read tri-state:", dist2, "sum:", sum(dist2.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
