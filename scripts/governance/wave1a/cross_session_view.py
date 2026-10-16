# [BLUEPRINT] MOD-TASK_SYSTEM | docs/_archive/_working_cleared/total_command_closeout/10_wave_plan.md#波1A-1A.6
# [MODULE] scripts.governance.wave1a.cross_session_view
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] 标准库 sqlite3/argparse/json; zephyr.shared.io.paths（仅推导 DB 默认路径）
# [CONSUMERS] docs/_archive/_working_cleared/total_command_closeout/wave1a/delivery_cards_report.md; 各后继会话交接
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
#   （原值 permanent——CLI 审计工具按需人工触发，PERM-TRIGGER 手动模式铁律归 task_bound）
# [STARTUP] manual
# [MATURITY] candidate
# [SAFETY] L
# [AI_AUTONOMY] supervised
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [STABILITY] evolving
# [ERROR_CONTRACT] 外部依赖失败必抛并点名，禁把异常吞成空值/空表（假绿源）
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
"""cross_session_view.py — 交接视图（1A.6）：一条命令出跨会话状态视图。

三个视图：按 session_id 汇总 / 按 blocked_by 出阻塞链 / 按 verification_status 分布。
状态真源=governance.db tasks 表；散文（案卷）只承载为什么，不承载状态。
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict

from zephyr.shared.io.paths import DB_PATH


def _rows(db: str, session: str | None, wave: str | None) -> list[sqlite3.Row]:
    """_rows implementation."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    q = (
        "SELECT task_id, title, status, session_id, blocked_by, depends_on, "
        "verification_status, construction_status, approval_required, requires_rb_check "
        "FROM tasks WHERE is_deleted=0"
    )
    args: list = []
    if session:
        q += " AND session_id=?"
        args.append(session)
    if wave:
        q += " AND source_section LIKE ?"
        args.append(f"%波{wave}%")
    if not session and not wave:
        q += " AND status IN ('PENDING','READY','IN_PROGRESS','BLOCKED','WAITING','RETRY')"
    q += " ORDER BY session_id, task_id"
    rows = con.execute(q, args).fetchall()
    con.close()
    return list(rows)


def _parse(v) -> list[str]:
    """_parse implementation."""
    try:
        out = json.loads(v) if v else []
        return [str(x) for x in out] if isinstance(out, list) else [str(out)]
    except (json.JSONDecodeError, TypeError):
        return [v] if v else []


def build_view(db: str, session: str | None, wave: str | None) -> dict:
    """build_view implementation."""
    rows = _rows(db, session, wave)
    by_session: dict[str, dict] = defaultdict(lambda: defaultdict(int))
    blocked_chain = []
    by_verification: dict[str, dict] = defaultdict(lambda: defaultdict(int))
    for r in rows:
        sid = r["session_id"] or "(no-session)"
        by_session[sid][r["status"]] += 1
        by_session[sid]["_total"] += 1
        by_verification[r["verification_status"] or "(null)"][r["status"]] += 1
        if r["status"] == "BLOCKED":
            blocked_chain.append(dict(task_id=r["task_id"], blocked_by=_parse(r["blocked_by"]), title=r["title"][:40]))
    return dict(
        db=db,
        filter=dict(session=session, wave=wave, active_only=not (session or wave)),
        total=len(rows),
        view_by_session={k: dict(v) for k, v in by_session.items()},
        view_blocked_by=blocked_chain,
        view_by_verification={k: dict(v) for k, v in by_verification.items()},
    )


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="跨会话状态视图（只读）")
    ap.add_argument("--db", default=None)
    ap.add_argument("--session", default=None)
    ap.add_argument("--wave", default=None, help="1A/1B/2 —— 按 source_section 过滤波次")
    args = ap.parse_args()
    print(json.dumps(build_view(args.db or str(DB_PATH), args.session, args.wave), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
