#!/usr/bin/env python3
# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md | §2.2 差集仲裁（pg_only→回放补账）+ §4 频率表 #6
# [MODULE] scripts.governance.meta_question.wo001_003.replay_audit_to_jsonl
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection, read_only=True 唯一读通道);
#                zephyr.governance.meta_question.meta_question_registry (AUDIT_WHAT_VOCAB 词表真源，越词表行拒放)；
#                .runtime/chain_piling/meta_question_audit.jsonl（补账目标，追加不改写）
# [CONSUMERS] scripts/governance/check_meta_question_audit_reconcile.py（回放后逐日/逐行差集必归零）;
#             scripts/register_metaq_audit_reconcile_task.ps1（每日排班发现差异后的人工/自动补账臂）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 默认 dry-run（--apply 才落盘，宪法 §9.7 破坏性操作三步验证的"可逆性"面：追加账只增不改）；
#              幂等=身份键多重集去重后只补缺（重跑零副作用，键口径与对账器逐字一致：
#              (object,what,who,when_utc_iso,evidence_norm)）；
#              行形状与既有回放批逐字同构（键序 who/when/what/object/diff/evidence + diff=[{before,after}]），
#              禁自创 schema（20§2.3③ 逐行哈希比对前置）；
#              when=PG created_at 的 UTC isoformat（禁 now_utc() 重取——重取即造新时点，逐日窗对不上）；
#              what 越 AUDIT_WHAT_VOCAB 的行一律拒放并计 finding；read 事件不入（20§2.2：read 仅 JSONL 侧，PG 无此行）；
#              PG 读失败=fail-closed 退出 2，零写入零半成品
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md §2 + scripts/governance/check_meta_question_audit_reconcile.py（键口径真源，改一边必改另一边）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT 0=无缺行（或 --apply 后差集归零）；EXIT 1=存在缺行（dry-run 报数不落盘）；EXIT 2=异常（PG 连接/查询失败、JSONL 不可读、词表加载失败）
# [TESTS] tests/governance/meta_question/wo001_003/test_replay_audit_to_jsonl.py（tmp_path JSONL 副本：红腿=删 1 行回放必补且只补 1 行；蓝腿=幂等重跑零追加）
# [TTL] permanent
"""replay_audit_to_jsonl — PG 审计表 → JSONL 追加账回放补账器（WO-002 收口配套，20§2.2）。

为什么需要（实测在案）：对账器全窗跑出的缺口不是历史存量，而是 **2026-09-24 的 283 条
``update``（Phase0 分诊认领）** ——那批走的是绕过写入 API 的直连 SQL，双轨里 JSONL 侧为零，
所以逐日差 pg=283/jsonl=0。20§2.2 仲裁：差集以 PG 为真源，pg_only=JSONL 缺行须回放补账。

用法::

    python scripts/governance/meta_question/wo001_003/replay_audit_to_jsonl.py            # dry-run 报缺行
    python scripts/governance/meta_question/wo001_003/replay_audit_to_jsonl.py --days 3   # 近 N 日窗
    python scripts/governance/meta_question/wo001_003/replay_audit_to_jsonl.py --apply    # 追加补缺（幂等）
    python ... --jsonl <tmp copy> --apply                                                # 红蓝自测，不碰生产账
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Final

_BOOT_ROOT = Path(__file__).resolve().parents[4]
if str(_BOOT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_BOOT_ROOT / "src"))
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓根唯一真源（原为本地重定义，SSOT-REDEFINITION 对症）

DEFAULT_JSONL: Final[Path] = REPO_ROOT / ".runtime" / "chain_piling" / "meta_question_audit.jsonl"
LINE_KEYS: Final[tuple[str, ...]] = ("who", "when", "what", "object", "diff", "evidence")
# NO-BARE-SQL（§5.160.2）：本件取数语句集中于此常量，函数体只做表名/参数插值，不嵌 SQL。
_SQL_AUDIT_ROWS: Final[str] = (
    'SELECT q_id, actor, what, "before", "after", evidence, created_at FROM {s}.meta_question_audit ORDER BY id'  # noqa: bare-sql  本行即 SQL 集中承载位本体（§5.160.2 要求的形态），非函数体内嵌
)

EXIT_DONE: Final = 0
EXIT_GAP: Final = 1
EXIT_ERROR: Final = 2


def _norm_evidence(raw: Any) -> str:
    """evidence 归一（与对账器同口径：去首尾空白）。"""
    return str(raw or "").strip()


def _identity(object_id: str, what: str, who: str, when_utc: datetime, evidence: Any) -> tuple[str, str, str, str, str]:
    return (object_id, what, who, when_utc.astimezone(timezone.utc).isoformat(), _norm_evidence(evidence))


def _load_existing_keys(path: Path) -> Counter[tuple[Any, ...]]:
    """已存 JSONL 行 → 身份键多重集（坏行跳过不中断：补账器不是对账器，判定交给对账器）。"""
    keys: Counter[tuple[Any, ...]] = Counter()
    if not path.exists():
        return keys
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
            when = datetime.fromisoformat(str(event["when"]).replace("Z", "+00:00"))
        except Exception:  # noqa: BLE001  畸形行由对账器判 malformed，这里不重复裁定
            continue
        keys[
            _identity(
                str(event.get("object") or ""),
                str(event.get("what") or ""),
                str(event.get("who") or ""),
                when,
                event.get("evidence"),
            )
        ] += 1
    return keys


def _load_pg_rows(days: int) -> tuple[list[dict[str, Any]], str | None]:
    """只读拉 PG 审计行（--days>0 走近 N 日窗，含今日）。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    sql = _SQL_AUDIT_ROWS
    params: tuple[Any, ...] = ()
    if days > 0:
        from zephyr.shared.utils.time_utils import now_utc  # RULE-SCHEMA-TZ：禁裸 datetime.now

        start: date = (now_utc() - timedelta(days=days - 1)).date()
        sql = sql.replace(" ORDER BY id", " WHERE (created_at AT TIME ZONE 'UTC')::date >= %s ORDER BY id")
        params = (start,)
    try:
        conn = get_depgraph_pg_connection(read_only=True)
    except Exception as exc:  # noqa: BLE001
        return [], f"pg_connect_failed: {exc}"
    try:
        cur = conn.cursor()
        cur.execute(sql.format(s="meta_question"), params)
        rows = []
        for q_id, actor, what, before, after, evidence, created_at in cur.fetchall():
            rows.append(
                {
                    "object": q_id,
                    "who": actor,
                    "what": what,
                    "before": before,
                    "after": after,
                    "evidence": evidence,
                    "when_utc": created_at,
                }
            )
        return rows, None
    except Exception as exc:  # noqa: BLE001
        return [], f"pg_query_failed: {exc}"
    finally:
        conn.close()


def _vocab() -> frozenset[str] | None:
    try:
        from zephyr.governance.meta_question.meta_question_registry import AUDIT_WHAT_VOCAB

        return frozenset(AUDIT_WHAT_VOCAB)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] 审计词表不可加载（fail-closed 不补账）：{exc}", file=sys.stderr)
        return None


def build_missing_lines(
    rows: list[dict[str, Any]], existing: Counter, vocab: frozenset[str]
) -> tuple[list[str], list[str]]:
    """PG 行 − 已存键多重集 → 待补 JSONL 行（保持 PG 序）；返回 (行文本, findings)。

    多重集口径=同键 N 条 PG 行需 N 条已存 JSONL 行才算平（与对账器双向差集同判据），
    逐行按 PG 序消费"已存配额"，超出配额者即缺行。
    """
    findings: list[str] = []
    lines: list[str] = []
    matched: Counter = Counter()
    for row in rows:
        key = _identity(row["object"], row["what"], row["who"], row["when_utc"], row["evidence"])
        if matched[key] < existing[key]:
            matched[key] += 1
            continue
        if row["what"] not in vocab:
            findings.append(f"off_vocab_what: {row['what']} ({row['object']}) 拒放")
            continue
        lines.append(json.dumps(_line(row), ensure_ascii=False))
    return lines, findings


def _line(row: dict[str, Any]) -> dict[str, Any]:
    """JSONL 行（与既有回放批同构：键序 who/when/what/object/diff/evidence）。"""
    return {
        "who": row["who"],
        "when": row["when_utc"].astimezone(timezone.utc).isoformat(),
        "what": row["what"],
        "object": row["object"],
        "diff": [{"before": row["before"], "after": row["after"]}],
        "evidence": _norm_evidence(row["evidence"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, default=0, help="只回拉近 N 个 UTC 日（0=全窗）")
    parser.add_argument("--jsonl", default=str(DEFAULT_JSONL), help="补账目标（默认生产追加账）")
    parser.add_argument("--apply", action="store_true", help="落盘追加（缺省 dry-run）")
    args = parser.parse_args(argv)

    path = Path(args.jsonl)
    vocab = _vocab()
    if vocab is None:
        return EXIT_ERROR
    rows, error = _load_pg_rows(args.days)
    if error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return EXIT_ERROR
    lines, findings = build_missing_lines(rows, _load_existing_keys(path), vocab)
    by_day = Counter(line.split('"when": "')[1][:10] for line in lines)

    print(f"PG 审计行={len(rows)}  待补 JSONL 行={len(lines)}  目标={path}")
    for day, count in sorted(by_day.items()):
        print(f"  {day}: 缺 {count} 行")
    for finding in findings:
        print(f"  [FINDING] {finding}")
    if not lines:
        print("无缺行（双轨平盘，回放幂等零写）")
        return EXIT_DONE
    if not args.apply:
        print("[DRY-RUN] 未落盘（--apply 才追加；20§2.2 差集以 PG 为真源）")
        return EXIT_GAP
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(line + "\n")
    print(
        f"[APPLIED] 追加 {len(lines)} 行（只增不改）；复核=python scripts/governance/"
        f"check_meta_question_audit_reconcile.py 应 exit 0"
    )
    return EXIT_DONE


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
