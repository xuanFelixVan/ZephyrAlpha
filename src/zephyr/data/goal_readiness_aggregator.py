# [BLUEPRINT] MOD-DATA-GOALAGG | docs/_working/infoaxis/00_ledger.md §3-Q6 | 对标 MOD-DATA-L9AGG 全部纪律
# [MODULE] zephyr.data.goal_readiness_aggregator
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer（写通道，测试可注入）; zephyr.data.ch_reader;
#   zephyr.data.l9_readiness_aggregator（业务日真源 _resolve_day 复用，禁第二套）; time_utils.now_utc
#   （禁 datetime.now——RULE-SCHEMA-TZ）; config/trading_decision_map.yaml（goal 块/edges 真源）;
#   docs/03_modules/_domain_backtest/exam_cards/**（考卡计数）; exam_scores_v1.yaml（验证读数）
# [CONSUMERS] TDM-E-L9-AGG 目标就绪度读数（Q6 实件）; 完工判据读数面（151 核心非红）;
#   Q7 开班令 gate（读汇总态）; strategy_pipeline（task_completed 唤醒挂接，二期）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯读取聚合层（TDM/考卡/分数册只读，禁在汇聚点写上游——l9 同款边界）;
#   fail-open：探测失败≠读数为零，禁静默绿（error 行出声）; suspended 不计红（30 源线+4 币圈
#   +V2，goal.status 判定真源=TDM goal 块非本模块硬编码）; 分母口径=151（186−30−4−1AGG，
#   Q2 批准，与 tdm_goal_blocks._family_for 同判据复现）; 事件触发禁 cron/Timer/sleep（宪法 §9.3，
#   exam/l9_readiness 系 SUCCESS 唤醒，同日 60min 节流 DB 侧时钟比较）; DateTime64(3)+显式时区、
#   ingest_ts DB 侧生成写侧零墙钟（RULE-SCHEMA-TZ）; 表名经 schema 模块派生禁硬编码
# [MODIFY-GUARD] 分档口径（缺一=黄/缺≥2=红）变更须同步 00_ledger.md §3-Q6 与 schemas/categories/goal_readiness_daily.py 文档串（三面口径锁）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 钩子永不反噬调度器（全捕获转 error 出声）; 源不可达转 error 行留因; 业务日不可解析=data_insufficient
# [TESTS] tests/data/test_goal_readiness_aggregator.py
# [A_module] module_id=MOD-DATA-GOALAGG | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-data-goalagg-goal-readiness-aggregator-20261013
"""TDM 目标就绪度聚合器——Q6 实件（裁定#516；对标 l9_readiness_aggregator 全部纪律）。

真源：docs/_working/infoaxis/00_goal_structure_research_2026_10_13.md §5（目标责任制读数：
绿=有目标＋有考卡＋有消费方＋有读数；黄=缺一；红=有目标零验证）＋ infoaxis/00_ledger.md §3。

定位：151 核心 TDM 节点的目标就绪度读数生产者。事件触发（exam/l9_readiness 系任务完成
唤醒）→ 纯读取三源（①TDM goal 块×四字段 ②考卡计数 node_id 直挂 ③消费方=TDM 边 from 节点
∪ mounts 非空 ④验证读数=confidence verified ∪ exam_scores_v1 在册）→ 逐节点单行读数
（绿/黄/红/挂起＋四布尔）→ 写 c1_market.goal_readiness_daily（ReplacingMergeTree latest-wins
同日刷新幂等）→ 汇总行 AGG-GOAL（core 分母 151＋red 计数，suspended 不计红）。

分档 v1 自裁（严口径，放宽须过 MODIFY-GUARD 三面锁）：
  green=四要素齐；yellow=恰缺一（明示缺件）；red=缺≥2（"有目标零验证"字面态=三件全缺的
  子集，v1 并入缺≥2）；suspended=goal.status∈{suspended,suspended_reference} 不计红；
  error=源探测失败出声。

用法：
  python -m zephyr.data.goal_readiness_aggregator                # 唤醒过滤+节流+读数+写 CH
  python -m zephyr.data.goal_readiness_aggregator --dry-run      # 只拼装打 stdout，零写
  python -m zephyr.data.goal_readiness_aggregator --force        # 绕过 60min 节流强制刷新

# [ALGO_FLOW]
# 层: TDM/考卡/分数册 → 逐节点行 → AGG 汇总 → TSV 落 CH
# - 输入: config/trading_decision_map.yaml goal 块＋exam_cards 计数＋exam_scores 验证读数（全只读注入可测）
# - 判级: _grade(goal, has_card, has_consumer, has_reading) → green/yellow/red；suspended 不计红
# - 汇总: AGG-GOAL 行（分母=151 核心口径，red 计数）
# - 落表: goal_readiness_daily（writer 注入可测；事件唤醒面在 pipeline_events 订阅）
# [/ALGO_FLOW]
"""

# create-guard-not-dup: 本模块只做 TDM 目标就绪度绿黄红读数的只读聚合（TDM/考卡/分数册三源拼装），非回测引擎、执行、风控或情绪分析任一在册能力的第二实现
# noqa: m11-perm-manual-legitimate  M11豁免: 产线触发＝事件订阅非本文件（zephyr.strategy_pipeline.pipeline_events.wire_data_scheduler 的 scheduler.subscribe("task_completed", _on_task_completed) 内调本模块 maybe_emit_*，与 L9/GOAL-AGG 先例同款）；本文件内 `__main__`+argparse 仅为人工复现/调试入口，非 cron/daemon/常驻

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from typing import Any, Final

import yaml

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = ["aggregate", "maybe_emit_goal_readiness", "run_aggregate"]

MODULE_ID: Final = "MOD-DATA-GOALAGG"

_TDM_YAML: Final = REPO_ROOT / "config" / "trading_decision_map.yaml"
_EXAM_CARD_GLOB: Final = "docs/03_modules/_domain_backtest/exam_cards/**/*.yaml"
_EXAM_SCORES: Final = REPO_ROOT / "docs" / "03_modules" / "_domain_backtest" / "exam_scores_v1.yaml"

#: 唤醒点：考试系/就绪度系任务 SUCCESS＝验证面或结构面刚变（宪法 §9.3 事件触发禁轮询）。
_WAKE_TASK_KEYS: Final = ("exam", "examcard", "l9_readiness", "tdm", "goal")

#: 同业务日最小刷新间隔（分钟）：DB 侧 ingest_ts 比较（l9 同款节流语义）。
_THROTTLE_MINUTES: Final = 60

#: 分母口径（Q2 批准 151）：186−30 源线−4 币圈−1 AGG——与 tdm_goal_blocks 同判据。
_SUSPENDED_STATUSES: Final = frozenset({"suspended", "suspended_reference"})
_AGG_SUMMARY_NODE: Final = "AGG-GOAL"
#: 分母口径三判据（与 tdm_goal_blocks 同判据复现——真源在那，tests 双面交叉核）。
import re as _re  # noqa: E402 — 模块级常量局部导入

_RE_SRC_LINE: Final = _re.compile(r"^TDM-E-L9-(A\d{2}|B\d{2}|C\d{2})$")
_RE_CRYPTO: Final = _re.compile(r"^TDM-C-L\d$")

SQL_THROTTLE = (
    "SELECT count() FROM {table} WHERE trade_date='{day}' AND ingest_ts > now64(3) - INTERVAL {minutes} MINUTE"
)
SQL_INSERT_READINGS = "INSERT INTO {table} ({cols}) FORMAT TSV"


# ── 源读取（模块级缺省，调用时解析＝测试注入点）─────────────────────────
def _default_reader(sql: str) -> str:
    from zephyr.data.ch_reader import query_tsv

    return query_tsv(sql)


def _default_writer(table: str, cols: str, tsv: str) -> bool:
    from zephyr.data.ch_writer import write_tsv

    return bool(write_tsv(table, cols, tsv.encode("utf-8")))


def _load_tdm() -> dict[str, Any]:
    return yaml.safe_load(_TDM_YAML.read_text(encoding="utf-8"))


def _card_counts() -> dict[str, int]:
    import glob as _glob

    counts: dict[str, int] = {}
    for p in _glob.glob(str(REPO_ROOT / _EXAM_CARD_GLOB), recursive=True):
        try:
            with open(p, encoding="utf-8") as fh:
                c = yaml.safe_load(fh)
        except Exception:  # noqa: BLE001 — 坏卡不炸聚合器
            continue
        nid = c.get("node_id") if isinstance(c, dict) else None
        if nid:
            counts[str(nid)] = counts.get(str(nid), 0) + 1
    return counts


def _score_nodes() -> set[str]:
    try:
        d = yaml.safe_load(_EXAM_SCORES.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — 分数册不可读＝读数源 fail-open 出声于调用方
        raise
    return {str(r.get("node_id")) for r in (d or {}).get("rows", []) if r.get("node_id")}


def _edge_sources(edges: list[dict[str, Any]]) -> set[str]:
    """TDM 边 from 集合＝"有人消费我" 的结构面证据（边键 from/to 兼容 source/target）。"""
    out: set[str] = set()
    for e in edges:
        f = e.get("from") or e.get("source")
        if f:
            out.add(str(f))
    return out


def _is_core(node_id: str) -> bool:
    """分母口径机械复现（真源=scripts/governance/tdm_goal_blocks.py 同判据；tests 交叉核一致）。"""
    return not (_RE_SRC_LINE.match(node_id) or _RE_CRYPTO.match(node_id) or node_id == "TDM-E-L9-AGG")


def _grade(
    goal: dict[str, Any] | None, *, has_card: bool, has_consumer: bool, has_reading: bool
) -> tuple[str, int, int, int, int, str]:
    """→ (status, has_goal, has_card, has_consumer, has_reading, detail)。"""
    if not isinstance(goal, dict):
        return "red", 0, int(has_card), int(has_consumer), int(has_reading), "缺 goal 块（核心节点零目标=红）"
    gs = str(goal.get("status", ""))
    if gs in _SUSPENDED_STATUSES:
        basis = goal.get("suspension_basis", "")
        return "suspended", 1, int(has_card), int(has_consumer), int(has_reading), f"挂起有据不计红：{basis or gs}"
    has_goal = all(goal.get(f) for f in ("goal_statement", "output_contract", "exam_ref", "campaign_ref"))
    missing = [
        name
        for name, ok in (
            ("goal", has_goal),
            ("card", has_card),
            ("consumer", has_consumer),
            ("reading", has_reading),
        )
        if not ok
    ]
    n = len(missing)
    if n == 0:
        return "green", 1, 1, 1, 1, "四要素齐"
    if n == 1:
        return (
            "yellow",
            int(has_goal),
            int(has_card),
            int(has_consumer),
            int(has_reading),
            f"恰缺一：{missing[0]}（补一即绿）",
        )
    return (
        "red",
        int(has_goal),
        int(has_card),
        int(has_consumer),
        int(has_reading),
        f"缺{n}件：{'/'.join(missing)}（有目标零验证面）",
    )


def aggregate(
    day: str,
    *,
    tdm: dict[str, Any] | None = None,
    cards: dict[str, int] | None = None,
    scores: set[str] | None = None,
    produced_at: str | None = None,
) -> list[dict[str, Any]]:
    """纯读取拼装：TDM×考卡×消费边×读数 → 逐节点行列表（全注入可测，零采集）。

    Args:
        day: 业务日（调用方已按共用真源校验）。
        tdm: TDM yaml 解析结果；None=模块级 _load_tdm（调用时解析）。
        cards: node_id→考卡数；None=_card_counts()。
        scores: 有验证读数的 node_id 集；None=_score_nodes()∪confidence==verified。
        produced_at: 产出时刻串（缺省=now_utc 转上海时区）。
    """
    from zoneinfo import ZoneInfo  # noqa: DTZ901 — produced_at 由 now_utc 真源生成（RULE-SCHEMA-TZ）

    tdm = tdm if tdm is not None else _load_tdm()
    cards = cards if cards is not None else _card_counts()
    produced = produced_at or now_utc().astimezone(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    nodes = tdm.get("nodes", [])
    edge_from = _edge_sources(tdm.get("edges", []))
    if scores is None:
        scores = {n["node_id"] for n in nodes if n.get("confidence") == "verified"} | _score_nodes()
    rows: list[dict[str, Any]] = []
    red_cnt = 0
    core_cnt = 0
    for n in nodes:
        nid = str(n.get("node_id", ""))
        goal = n.get("goal")
        mounts = (n.get("module_mounts") or []) or (n.get("strategy_mounts") or [])
        has_consumer = bool(mounts) or (nid in edge_from)
        status, hg, hc, hcon, hr, detail = _grade(
            goal, has_card=cards.get(nid, 0) > 0, has_consumer=has_consumer, has_reading=nid in scores
        )
        fam = (goal or {}).get("family", "") if isinstance(goal, dict) else ""
        rows.append(
            {
                "trade_date": day,
                "node_id": nid,
                "family": fam,
                "status": status,
                "has_goal": hg,
                "has_card": hc,
                "has_consumer": hcon,
                "has_reading": hr,
                "detail": detail,
                "produced_at": produced,
            }
        )
        if _is_core(nid):
            core_cnt += 1
            if status == "red":
                red_cnt += 1
    rows.append(
        {
            "trade_date": day,
            "node_id": _AGG_SUMMARY_NODE,
            "family": "AGG",
            "status": "red" if red_cnt else ("yellow" if any(r["status"] == "yellow" for r in rows) else "green"),
            "has_goal": -1,
            "has_card": -1,
            "has_consumer": -1,
            "has_reading": -1,
            "detail": f"分母={core_cnt}（口径 151）red={red_cnt}；suspended 不计红；黄={sum(1 for r in rows if r['status'] == 'yellow')}",
            "produced_at": produced,
        }
    )
    return rows


def _rows_to_tsv(rows: list[dict[str, Any]], columns: tuple[str, ...]) -> str:
    out = []
    for r in rows:
        out.append("\t".join(str(r.get(c, "")) for c in columns))
    return "\n".join(out)


def _throttled(table: str, day: str, reader: Callable[[str], str]) -> bool:
    try:
        raw = (reader(SQL_THROTTLE.format(minutes=_THROTTLE_MINUTES, table=table, day=day)) or "").strip()
        return raw.isdigit() and int(raw) > 0
    except Exception as exc:  # noqa: BLE001 — 节流探测失败不节流直走
        log.warning("节流探测失败（不节流直走）: %s", exc)
        return False


def run_aggregate(
    day: str | None = None,
    *,
    force: bool = False,
    dry_run: bool = False,
    reader: Callable[[str], str] | None = None,
    writer: Callable[[str, str, str], bool] | None = None,
) -> dict[str, Any]:
    """拼装→（节流闸）→写 CH；返回动作摘要（l9 run_aggregate 同款契约）。"""
    from schemas.categories import goal_readiness_daily as schema

    reader = reader or _default_reader
    writer = writer or _default_writer
    out: dict[str, Any] = {"module": MODULE_ID, "action": "error"}
    try:
        from zephyr.data.l9_readiness_aggregator import _resolve_day

        biz_day = _resolve_day(day)
    except Exception as exc:  # noqa: BLE001 — 业务日不可解析=不发读数但必须出声
        out["error"] = f"业务日不可解析（禁墙钟猜日）: {type(exc).__name__}: {exc}"[:200]
        return out
    out["trade_date"] = biz_day
    if not force and not dry_run and _throttled(schema.TABLE_NAME, biz_day, reader):
        out["action"] = "throttled"
        return out
    try:
        rows = aggregate(biz_day)
    except Exception as exc:  # noqa: BLE001 — 拼装失败出声（fail-open 绝不静默零读数）
        out["error"] = f"拼装失败 {type(exc).__name__}: {exc}"[:300]
        return out
    columns = tuple(schema.INSERT_COLUMNS)
    out["rows"] = len(rows)
    summary = rows[-1]
    out["summary"] = {"status": summary["status"], "detail": summary["detail"]}
    if dry_run:
        out["action"] = "dry_run"
        out["tsv"] = _rows_to_tsv(rows, columns)
        return out
    if not writer(schema.TABLE_NAME, "(" + ",".join(columns) + ")", _rows_to_tsv(rows, columns)):
        out["error"] = "CH 写入未确认（write_tsv=False）——读数未落地，禁记成功"
        return out
    out["action"] = "emitted"
    return out


def maybe_emit_goal_readiness(task_id: object = None, success: bool = True, **_kwargs) -> dict[str, Any]:
    """调度器 task_completed 唤醒钩子（唯一自动产出者；宪法 §9.3 事件触发禁轮询）。

    契约同 l9 maybe_emit：非唤醒点/失败→零副作用；节流窗内→skipped_throttled；
    任何异常→error 出声绝不反噬唤醒链。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in _WAKE_TASK_KEYS):
        return {"action": "skipped_wake_point"}
    try:
        res = run_aggregate()
        action = res.get("action", "error")
        if action == "error":
            log.warning("[GOAL-AGG] 目标就绪度读数未落地: %s", res.get("error", ""))
            return {"action": "error", "reason": res.get("error", "")}
        if action == "throttled":
            return {"action": "skipped_throttled"}
        log.info("[GOAL-AGG] 目标就绪度读数已产出: %s", {k: v for k, v in res.items() if k != "tsv"})
        return {"action": "emitted", **{k: v for k, v in res.items() if k not in ("tsv", "rows")}}
    except Exception as exc:  # noqa: BLE001 — 钩子永不反噬调度器，失败必须出声
        log.warning("[GOAL-AGG] 唤醒钩子异常（不影响后续链）: %s", exc, exc_info=True)
        return {"action": "error", "reason": str(exc)[:200]}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="只拼装打 stdout，零写")
    p.add_argument("--force", action="store_true", help="绕过 60min 节流强制刷新")
    p.add_argument("--day", default=None, help="业务日 YYYY-MM-DD（缺省=共用真源解析）")
    args = p.parse_args(argv)
    res = run_aggregate(day=args.day, force=args.force, dry_run=args.dry_run)
    import json

    print(json.dumps({k: v for k, v in res.items() if k != "tsv"}, ensure_ascii=False, default=str))
    if args.dry_run and res.get("tsv"):
        print(res["tsv"])
    return 0 if res.get("action") not in ("error",) else 1


if __name__ == "__main__":
    raise SystemExit(main())
