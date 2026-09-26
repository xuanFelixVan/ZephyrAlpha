#!/usr/bin/env python3
# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md | §2.2 双轨载体+差集仲裁 / §4 频率表 #6
# [MODULE] scripts.governance.check_meta_question_audit_reconcile
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] src/zephyr/governance/depgraph_schema.py（get_depgraph_pg_connection，read_only=True 只读）; src/zephyr/governance/meta_question/meta_question_registry.py（AUDIT_WHAT_VOCAB 治理级词表 SSOT）; .runtime/chain_piling/meta_question_audit.jsonl（只读对账侧）
# [CONSUMERS] 20§4 频率表 #6 账本双轨机检（季度窗；PG 故障恢复后即时）; PQ-0062/PQ-0102 复考判据执行体; L6 治理层审计窗
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 全程零写（PG read_only 连接 + JSONL 只读流式解析）; 治理级词表唯一真源=zephyr.governance.meta_question.meta_question_registry.AUDIT_WHAT_VOCAB（禁另立枚举、禁 yaml.safe_load 直读词表）; read 事件按 20§2.2 仅入 JSONL 不入 PG——不参与逐日/逐行比对，仅信息性计数（PG 出现 read=设计违规 finding）; 逐行比对=身份键 (object,what,who,when_utc_iso,evidence_norm) 多重集双向差集（diff/before/after 为载荷不入身份键）; 差集仲裁以 PG 为真源——pg_only=JSONL 缺行须回放补账，jsonl_only=JSONL 独有行须报告并附原始载荷复核后处置; 逐日=UTC 日界; JSONL when 无时区=按 RULE-SCHEMA-TZ 判 malformed
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md §2/§4 + src/zephyr/governance/meta_question/meta_question_registry.py（行 schema/词表真源，改契约先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT 0=平盘（逐日相等+双向差集空+零畸形行）；EXIT 1=有差异（逐日不等/missing_in_jsonl/jsonl_only/malformed 行/what 越词表/read 入 PG，清单逐条打印）；EXIT 2=异常（PG 连接失败/参数非法，fail-closed 不出对账结论）
# [TESTS] 手动红蓝两腿：蓝腿=存量回放后全量对账 exit 0；红腿=JSONL 临时副本删 1 行/改 1 行→exit 1 且报出差异行；--days 窗口边界冒烟
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 20§4 频率表 #6 机检执行体（季度窗/PG 故障恢复后即时按需触发），按需 CLI 非驻留进程
"""check_meta_question_audit_reconcile — meta_question 审计双轨对账（PG 审计表 vs JSONL 追加账）。

设计真源：docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md
§2.2（双轨载体+差集仲裁）+ §4 频率表 #6（本脚本=机检执行体）。
JSONL 行 schema 真源：src/zephyr/governance/meta_question/meta_question_registry.py（_write_audit/_append_jsonl：
who/when/what/object/diff/evidence 六字段）。

比对口径（20§2.2）：
  1) 逐日事件数比对：UTC 日界，治理级事件双侧计数，逐日相等；
  2) 治理级事件逐行比对：身份键多重集双向差集——
     pg_only（PG 有 JSONL 无）=JSONL 缺行，以 PG 为真源须回放补账；
     jsonl_only（JSONL 有 PG 无）=JSONL 独有行，必须报告并附原始载荷复核后处置；
     双向清零方可关窗。
  read 事件量大，设计上仅入 JSONL 不入 PG（治理级事件才双写）——不参与比对，仅计数；
  PG 侧出现 read 事件即设计违规 finding。

用法：

    # 全量窗对账（默认 JSONL=.runtime/chain_piling/meta_question_audit.jsonl）
    python scripts/governance/check_meta_question_audit_reconcile.py

    # 最近 N 天窗口（UTC 日界，含今日）
    python scripts/governance/check_meta_question_audit_reconcile.py --days 7

    # 对临时副本/备轨对账（红腿自测用，不碰生产账）
    python scripts/governance/check_meta_question_audit_reconcile.py --jsonl <path>

退出码：0=平盘；1=有差异（清单逐条打印）；2=异常（fail-closed）。
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_BOOT_ROOT = Path(__file__).resolve().parents[2]
_SRC = _BOOT_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.governance.meta_question.meta_question_registry import AUDIT_WHAT_VOCAB  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓根唯一真源（原为本地重定义，SSOT-REDEFINITION 对症）

_SQL_AUDIT_COLS = "SELECT q_id, actor, what, evidence, created_at FROM {s}.meta_question_audit"

__manifest__ = """
args: []
description: 'PQ-0062/0102 审计双轨对账：PG meta_question_audit vs JSONL 追加账逐日+逐行差集（20§2.2，差集以 PG 为真源）。'
dimensions:
- D3
priority: P2
timeout_seconds: 120
warn_only: false
"""

DEFAULT_JSONL = REPO_ROOT / ".runtime" / "chain_piling" / "meta_question_audit.jsonl"
READ_WHAT = "read"
GOVERNANCE_WHAT = frozenset(AUDIT_WHAT_VOCAB) - {READ_WHAT}
_JSONL_FIELDS = ("who", "when", "what", "object", "diff", "evidence")
_LIST_REPORT_CAP = 50  # 每类差异清单最多逐条打印行数（总量照报）

EXIT_PASS = 0
EXIT_DIFF = 1
EXIT_ERROR = 2


def _norm_evidence(value: object) -> str:
    """证据指针归一化：dict/list→排序 JSON 串；None→""；其余 str()。"""
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value)


def _parse_when(raw: object) -> datetime:
    """JSONL when → aware datetime（禁 naive，RULE-SCHEMA-TZ）。"""
    text = str(raw or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        raise ValueError(f"naive datetime in jsonl when: {raw!r}")
    return parsed.astimezone(timezone.utc)


def _load_pg_events(schema: str, start_day: date | None) -> tuple[list[dict], str | None]:
    """只读拉取 PG 审计行 → 统一事件 dict；返回 (events, error)。"""
    sql = _SQL_AUDIT_COLS.format(s=schema)
    params: tuple = ()
    if start_day is not None:
        sql += " WHERE (created_at AT TIME ZONE 'UTC')::date >= %s"
        params = (start_day,)
    sql += " ORDER BY id"
    try:
        conn = get_depgraph_pg_connection(read_only=True)
    except Exception as exc:  # noqa: BLE001
        return [], f"pg_connect_failed: {exc}"
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        events = []
        for q_id, actor, what, evidence, created_at in cur.fetchall():
            when_utc = created_at.astimezone(timezone.utc)
            events.append(
                {
                    "object": q_id,
                    "what": what,
                    "who": actor,
                    "when_utc": when_utc,
                    "key": (q_id, what, actor, when_utc.isoformat(), _norm_evidence(evidence)),
                }
            )
        return events, None
    except Exception as exc:  # noqa: BLE001
        return [], f"pg_query_failed: {exc}"
    finally:
        conn.close()


def _load_jsonl_events(path: Path) -> tuple[list[dict], list[str]]:
    """只读解析 JSONL 账 → (events, malformed_reports)；畸形行计 finding 不中断。"""
    events: list[dict] = []
    malformed: list[str] = []
    if not path.exists():
        return events, [f"jsonl_file_missing: {path}"]
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                malformed.append(f"jsonl_malformed:json_decode L{lineno}: {exc.msg}")
                continue
            if not isinstance(payload, dict):
                malformed.append(f"jsonl_malformed:not_dict L{lineno}")
                continue
            missing = [f for f in _JSONL_FIELDS if f not in payload]
            if missing:
                malformed.append(f"jsonl_malformed:field_missing L{lineno}: {','.join(missing)}")
                continue
            try:
                when_utc = _parse_when(payload.get("when"))
            except ValueError as exc:
                malformed.append(f"jsonl_malformed:bad_when L{lineno}: {exc}")
                continue
            events.append(
                {
                    "object": payload.get("object"),
                    "what": payload.get("what"),
                    "who": payload.get("who"),
                    "when_utc": when_utc,
                    "key": (
                        payload.get("object"),
                        payload.get("what"),
                        payload.get("who"),
                        when_utc.isoformat(),
                        _norm_evidence(payload.get("evidence")),
                    ),
                    "raw": payload,
                }
            )
    return events, malformed


def _fmt_key(key: tuple) -> str:
    obj, what, who, when_iso, evidence = key
    return f"object={obj} what={what} who={who} when={when_iso} evidence={evidence[:60]!r}"


def _build_reconcile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="meta_question 审计双轨对账：PG meta_question_audit vs JSONL 追加账（20§2.2 差集仲裁，PG 为真源）",
        epilog="退出码：0=平盘；1=有差异；2=异常。",
    )
    parser.add_argument("--days", type=int, default=0, help="只对账最近 N 天（UTC 日界，含今日）；0 或缺省=全量窗")
    parser.add_argument(
        "--jsonl",
        default=str(DEFAULT_JSONL),
        help="JSONL 追加账路径（默认 .runtime/chain_piling/meta_question_audit.jsonl；红腿自测可指向临时副本）",
    )
    parser.add_argument("--schema", default="meta_question", help="PG schema（默认 meta_question）")
    return parser


def _resolve_start_day(args: argparse.Namespace, parser: argparse.ArgumentParser) -> date | None:
    if args.days < 0:
        parser.error("--days 必须为非负整数（0=全量窗）")
    if args.days > 0:
        return datetime.now(timezone.utc).date() - timedelta(days=args.days - 1)
    return None


def _compare_sides(pg_events: list[dict], jsonl_events: list[dict], malformed: list[str]) -> tuple[dict, list[str]]:
    """双侧分拣 + ①逐日事件数比对 + ②逐行差集（findings 次序与文案同原 main 中段）。

    :return: (报告视图 view, findings)；view 携带报告段所需的全部桶/计数。
    """
    findings: list[str] = []

    # ---- 治理级/read/越词表分拣（双侧） -------------------------------------
    pg_gov = [e for e in pg_events if e["what"] in GOVERNANCE_WHAT]
    pg_read = [e for e in pg_events if e["what"] == READ_WHAT]
    pg_unknown = [e for e in pg_events if e["what"] not in AUDIT_WHAT_VOCAB]
    for e in pg_unknown:
        findings.append(f"what_not_in_ssot_vocab(pg): object={e['object']} what={e['what']!r}")
    for e in pg_read:
        findings.append(
            f"read_in_pg(设计违规,20§2.2 read 仅入 JSONL): object={e['object']} when={e['when_utc'].isoformat()}"
        )

    jl_gov = [e for e in jsonl_events if e["what"] in GOVERNANCE_WHAT]
    jl_read = [e for e in jsonl_events if e["what"] == READ_WHAT]
    jl_unknown = [e for e in jsonl_events if e["what"] not in AUDIT_WHAT_VOCAB]
    for e in jl_unknown:
        findings.append(f"what_not_in_ssot_vocab(jsonl): object={e['object']} what={e['what']!r}")

    # ---- ①逐日事件数比对（UTC 日界，治理级） -------------------------------
    pg_daily: Counter = Counter(e["when_utc"].date() for e in pg_gov)
    jl_daily: Counter = Counter(e["when_utc"].date() for e in jl_gov)
    for day in sorted(set(pg_daily) | set(jl_daily)):
        mark = "OK" if pg_daily[day] == jl_daily[day] else "DIFF"
        if mark == "DIFF":
            findings.append(f"daily_count_mismatch: {day} pg={pg_daily[day]} jsonl={jl_daily[day]}")

    # ---- ②治理级事件逐行比对（身份键多重集双向差集，PG 为真源） ------------
    pg_keys: Counter = Counter(e["key"] for e in pg_gov)
    jl_keys: Counter = Counter(e["key"] for e in jl_gov)
    missing_in_jsonl = pg_keys - jl_keys  # pg_only：JSONL 缺行，须回放补账
    jsonl_only = jl_keys - pg_keys  # JSONL 独有行：须报告+原始载荷复核后处置
    for key, n in missing_in_jsonl.items():
        findings.append(f"missing_in_jsonl(pg_only,x{n}): {_fmt_key(key)}")
    for key, n in jsonl_only.items():
        findings.append(f"jsonl_only(须复核原始载荷,x{n}): {_fmt_key(key)}")

    findings.extend(malformed)
    view = {
        "pg_gov": pg_gov,
        "pg_read": pg_read,
        "pg_unknown": pg_unknown,
        "jl_gov": jl_gov,
        "jl_read": jl_read,
        "jl_unknown": jl_unknown,
        "pg_daily": pg_daily,
        "jl_daily": jl_daily,
        "missing_in_jsonl": missing_in_jsonl,
        "jsonl_only": jsonl_only,
        "malformed": malformed,
    }
    return view, findings


def _print_report(view: dict, findings: list[str], args: argparse.Namespace, start_day: date | None) -> int:
    """报告段（打印次序与文案同原 main；不平盘=EXIT 1，平盘=EXIT 0）。"""
    window = "ALL" if start_day is None else f"last {args.days}d (since {start_day.isoformat()} UTC)"
    pg_daily: Counter = view["pg_daily"]
    jl_daily: Counter = view["jl_daily"]
    missing_in_jsonl: Counter = view["missing_in_jsonl"]
    jsonl_only: Counter = view["jsonl_only"]
    print("=" * 76)
    print(f"check_meta_question_audit_reconcile | window={window} | schema={args.schema}")
    print(f"jsonl={args.jsonl}")
    print("=" * 76)
    print(f"PG   治理级={len(view['pg_gov'])}  read={len(view['pg_read'])}  越词表={len(view['pg_unknown'])}")
    print(
        f"JSONL 治理级={len(view['jl_gov'])}  read={len(view['jl_read'])}(信息性,不入 PG)  "
        f"越词表={len(view['jl_unknown'])}  畸形行={len(view['malformed'])}"
    )
    print("-" * 76)
    print("逐日事件数（UTC 日界，治理级）:")
    for day in sorted(set(pg_daily) | set(jl_daily)):
        print(f"  {day}: pg={pg_daily[day]} jsonl={jl_daily[day]} {'OK' if pg_daily[day] == jl_daily[day] else 'DIFF'}")
    print("-" * 76)
    print("逐行差集（治理级，身份键多重集；差集以 PG 为真源）:")
    print(f"  missing_in_jsonl(pg_only)={sum(missing_in_jsonl.values())}  jsonl_only={sum(jsonl_only.values())}")
    if findings:
        print("-" * 76)
        print(f"差异/违规 {len(findings)} 条（每类最多逐条打印 {_LIST_REPORT_CAP} 条）:")
        shown = 0
        for f in findings:
            if shown >= _LIST_REPORT_CAP:
                print(f"  …其余 {len(findings) - shown} 条略（总量照报）")
                break
            print("  " + f)
            shown += 1
        print("-" * 76)
        print(
            "不平盘（20§2.2：差集以 PG 为真源——pg_only 须回放补账，jsonl_only 须复核原始载荷后处置，双向清零方可关窗）"
        )
        return EXIT_DIFF
    print("平盘：逐日相等且双向差集为空（20§2.2 关窗判据）")
    return EXIT_PASS


def main(argv: list[str] | None = None) -> int:
    parser = _build_reconcile_parser()
    args = parser.parse_args(argv)
    start_day = _resolve_start_day(args, parser)

    pg_events, pg_error = _load_pg_events(args.schema, start_day)
    if pg_error is not None:
        print(f"FATAL: {pg_error}")
        return EXIT_ERROR

    jsonl_events, malformed = _load_jsonl_events(Path(args.jsonl))
    if start_day is not None:
        # 窗口过滤双侧同施（PG 侧 SQL 已滤；JSONL 侧按 when UTC 日界滤），窗外行不参与比对
        jsonl_events = [e for e in jsonl_events if e["when_utc"].date() >= start_day]

    view, findings = _compare_sides(pg_events, jsonl_events, malformed)
    return _print_report(view, findings, args, start_day)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001  fail-closed：未预期异常=EXIT 2
        print(f"FATAL: unhandled exception: {type(exc).__name__}: {exc}")
        sys.exit(EXIT_ERROR)
