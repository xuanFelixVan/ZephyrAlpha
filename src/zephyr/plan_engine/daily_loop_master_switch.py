# [BLUEPRINT] MOD-PLAN-033 | docs/_working/daily_loop_campaign/00_reuse_audit_ledger.md（缺口①真源；上层蓝图 docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md §十一）
# [MODULE] zephyr.plan_engine.daily_loop_master_switch
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.daily_warroom_pipeline(run_daily_warroom_pipeline); zephyr.plan_engine.daily_plan(emit_for_trade_date); zephyr.plan_engine.next_day_forecaster(emit_for_trade_date); zephyr.plan_engine.intraday_l1_tracker(maybe_track_intraday_state); zephyr.plan_engine.scenario_classifier(maybe_classify_intraday_scenario); zephyr.plan_engine.close_verifier(verify_for_session); zephyr.plan_engine.judgment_settler(settle_all); zephyr.strategy_pipeline.daily_decision_orchestrator(run_daily_decision); zephyr.strategy_pipeline.pipeline_events(maybe_emit_pf_alloc_daily); zephyr.pf_alloc.allocation_inputs(load_pp001_plan); zephyr.data.ch_reader(只读新鲜度); scripts/backtest/print_regime_history.py(子进程逃生口)
# [CONSUMERS] 人工/Owner 门位（手动逃生口）；zephyr.data.scheduler（dloop_post 特殊槽，交易日 16:45 自动圈）；日循环 E2E 验收（st-dloop-20260921）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 调度挂接=已获 Owner 批（2026-09-21）挂 16:45 自动圈（排程配置 dloop_post 槽 + 调度器特殊槽处理，总闸 data/runtime/daily_loop_master.disabled）；手动逃生口并存；观察/记录模式零下单（拍板体=#305 安全态，执行单不产）；幂等=全量委托底层模块既有幂等闸（prediction_log UNIQUE/台账查重/bar_key/业务日记号），编排层零自建键；逐段 fail-open（单段失败留痕不炸全链，汇总报告 ok/skipped/error 计数）；唯二 fail-closed=数据就绪门（行情缺日不出预案）与输入校验；regime 新鲜度按消费方口径（编排器 D1：滞后>1 交易日=缺）；供给方阈值已经 Owner 批对齐为 1（2026-09-21 治本，原 3 与消费方错位是 2026-09-15~09-18 断供根因，见对账总账 §4）；判定/结算分离纪律（判定器禁写结算列）由底层模块自守，本件不越权
# [MODIFY-GUARD] docs/_working/daily_loop_campaign/00_reuse_audit_ledger.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（data_date 格式/phase 非法 fail-closed）；各段异常→该段 result["status"]="error" 留痕继续下一段；数据就绪门失败→整圈 blocked 不落任何判定
# [TESTS] tests/plan_engine/test_daily_loop_master_switch.py
# [A_module] module_id=MOD-PLAN-033 | layer=module | stability=evolving | safety=L | ai_modifiable
# [TTL] permanent

"""

daily_loop_master_switch — 日循环手动总扳手（缺口①，对账总账 §5）

一个入口串起整圈排班链路（对账定案=复用 9 棒既有产出者，禁平行实现）：

    数据就绪门(fail-closed) → regime 新鲜度体检(消费方口径,缺则逃生口补印)
    → warroom scenario_plan 族(MOD-PLAN-018, 唯一未挂事件链的棒)
    → 晨间预案(MOD-PLAN-030) → 次日概率(MOD-PLAN-029) → pf_alloc 分配(记号幂等)
    → 盘中 L1(MOD-PLAN-028) → 盘中归类(MOD-PLAN-031)
    → 收盘验证(MOD-PLAN-032, 序契约先于结算) → 三表结算(MOD-PLAN-027)
    → 日度拍板(MOD-BT-214, #305 安全态, force=显式重拍逃生口)

用法（手动逃生口与 16:45 自动圈并存——原 MANUAL-ONLY 不挂调度器约束已经 Owner 批准
于 2026-09-21 解除，挂排程配置 dloop_post 特殊槽，总闸
data/runtime/daily_loop_master.disabled；门禁合规保持=不设 argparse，编程式入口，先例
=daily_decision_orchestrator 手工补跑逃生口）：
    python -c "from zephyr.plan_engine.daily_loop_master_switch import run_daily_loop as r; \
print(r(None))"    # 无参=自动解析最新业务日（dloop_post 调度圈同款形态）
    python -c "from zephyr.plan_engine.daily_loop_master_switch import run_daily_loop as r; \
print(r('2026-09-21'))"
    python -c "from zephyr.plan_engine.daily_loop_master_switch import run_daily_loop as r; \
print(r('2026-09-21', phase='intraday'))"
    python -c "from zephyr.plan_engine.daily_loop_master_switch import run_daily_loop as r; \
print(r('2026-09-18', force_decision=True))"

零下单声明：全链只写判定台账/验证/决策快照（观察/记录面），不触执行单源；
拍板体写 decision_daily 快照行但 GRADUATED_PACKAGES 恒空（裁定#305）→ 结构性无实盘行为。
# [ALGO_FLOW] external: docs/03_modules/_domain_plan/algo_flow/daily_loop_master_switch.yaml
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from datetime import time as dtime
from pathlib import Path
from typing import Any, Final
from zoneinfo import ZoneInfo

from zephyr.data.table_registry import get_registry
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final[list[str]] = [
    "run_daily_loop",
    "PHASE_STAGES",
]

_VALID_PHASES: Final[tuple[str, ...]] = ("premarket", "intraday", "postmarket", "full")
_WAKE_60MIN: Final = "kline_etf_60min"  # 盘中族人工触发等价唤醒词（maybe_* 契约）
_WAKE_DAILY: Final = "daily_kline"
_REGIME_REPRINT_TIMEOUT_S: Final = 1800
_DATE_LEN: Final = 10
_SHANGHAI: Final = ZoneInfo("Asia/Shanghai")
_AUCTION_WINDOW: Final[tuple[dtime, dtime]] = (dtime(10, 0), dtime(10, 30))  # 10:00 判定时点闸
_SCENARIO_MODULE: Final = "plan_engine.scenario_planner"  # W0 归因统计对象


# ── 只读帮手（新鲜度/日历/配比快照）──────────────────────────────────────────


def _ch_query(sql: str) -> str:
    from zephyr.data.ch_reader import query

    return query(sql)


_SQL_MAX_REGIME: Final = "SELECT max(trade_date) FROM c1_backtest.regime_snapshot_history FORMAT TSV"  # noqa: bare-sql  只读新鲜度单值查询常量，无注入面
_DB_MARKET: Final = "c1_market"
_TBL_KLINE_INDEX: Final = "kline_index"  # 业务日真源（与 judgment_settler/pf_alloc 同源）
_SQL_MAX_KLINE: Final = "SELECT max(trade_date) FROM {db}.{src} FINAL FORMAT TSV"  # noqa: bare-sql  只读数据就绪门单值查询常量，无注入面
_TBL_CALENDAR: Final = get_registry().table("market_trade_calendar")
_PREV_BD_SQL: Final = (
    f"SELECT max(cal_date) FROM {_TBL_CALENDAR} FINAL "  # noqa: bare-sql  只读日历查询常量，表名走真源注册表，参数化无注入面
    "WHERE is_open=1 AND cal_date < '{d}' FORMAT TSV"
)


def _max_regime_trade_date() -> str | None:
    return _ch_query(_SQL_MAX_REGIME).strip() or None


def _max_kline_trade_date() -> str | None:
    return _ch_query(_SQL_MAX_KLINE.format(db=_DB_MARKET, src=_TBL_KLINE_INDEX)).strip() or None


def _prev_business_day(data_date: str) -> str | None:
    out = _ch_query(_PREV_BD_SQL.format(d=data_date)).strip()
    return out or None


def _pp001_snapshot() -> dict[str, Any]:
    """只读 PP-001 配比快照（配比产出证据，禁写 config）。"""
    from zephyr.pf_alloc.allocation_inputs import load_pp001_plan

    tdm = Path(REPO_ROOT) / "config" / "trading_decision_map.yaml"
    weights, caps, plan_id = load_pp001_plan(tdm)
    return {
        "plan_id": plan_id,
        "sleeve_count": len(weights),
        "weight_sum": round(sum(weights.values()), 6),
        "aggregator_caps": caps,
    }


# ── regime 新鲜度（消费方口径）──────────────────────────────────────────────


def ensure_regime_fresh(data_date: str) -> dict[str, Any]:
    """编排器 D1 消费方口径体检：快照滞后 >1 交易日=缺 → 官方逃生口补印缺口窗。

    供给方 fw_backtest._REGIME_STALE_DAYS=3 与消费方 1 日阈值错位（对账总账 §4），
    本件按消费方口径把关；补印走 print_regime_history.py（不受供给方幂等闸约束）。
    """
    prev_bd = _prev_business_day(data_date)
    if prev_bd is None:
        return {"status": "skipped", "reason": "calendar_no_prev_business_day"}
    max_d = _max_regime_trade_date()
    if max_d is not None and max_d >= prev_bd:
        return {"status": "ok", "action": "fresh", "max_trade_date": max_d, "required_min": prev_bd}
    start = max_d or prev_bd
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    proc = run_subprocess_hidden(
        [sys.executable, "scripts/backtest/print_regime_history.py", "--start", start, "--end", data_date],
        timeout=_REGIME_REPRINT_TIMEOUT_S,
        cwd=str(REPO_ROOT),
        encoding="utf-8",
    )
    after = _max_regime_trade_date()
    ok = proc.returncode == 0 and after is not None and after >= prev_bd
    return {
        "status": "ok" if ok else "error",
        "action": "reprinted" if ok else "reprint_failed",
        "before": max_d,
        "after": after,
        "required_min": prev_bd,
        "rc": proc.returncode,
        "stderr_tail": (proc.stderr or "")[-300:],
    }


# ── 各段（薄委托，禁平行实现）───────────────────────────────────────────────


def _stage_data_readiness(data_date: str) -> dict[str, Any]:
    max_d = _max_kline_trade_date()
    if max_d is None or max_d < data_date:
        return {"status": "error", "reason": "kline_index_missing_date", "max_trade_date": max_d, "required": data_date}
    return {"status": "ok", "max_trade_date": max_d}


def _stage_warroom(data_date: str, phase: str) -> dict[str, Any]:
    from zephyr.plan_engine.daily_warroom_pipeline import run_daily_warroom_pipeline

    wp = {"full": "both"}.get(phase, phase if phase != "full" else "both")
    res = run_daily_warroom_pipeline(data_date, phase=wp)
    return {
        "status": "ok",
        "premarket_status": getattr(res, "premarket_status", None),
        "postmarket_status": getattr(res, "postmarket_status", None),
    }


def _stage_daily_plan(data_date: str) -> dict[str, Any]:
    from zephyr.plan_engine.daily_plan import maybe_emit_daily_plan

    # 钩子内建 plan_date 查重幂等（emit_for_trade_date 直调=修订行追加，绕过查重——
    # E2E 首圈实证：同 inputs_hash 追加新 judgment_id）。段序契约要求唤醒词过滤通过。
    out = maybe_emit_daily_plan(task_id=_WAKE_DAILY, success=True)
    return {
        "status": "ok",
        "detail": str(out)[:300],
        "note": "日解析=resolve_pf_alloc_trade_date（最新入库日）；"
        f"与 --data-date={data_date} 不一致时以最新入库日为准",
    }


def _stage_next_day(data_date: str) -> dict[str, Any]:
    from zephyr.plan_engine.next_day_forecaster import maybe_emit_next_day_forecast

    out = maybe_emit_next_day_forecast(task_id=_WAKE_DAILY, success=True)
    return {"status": "ok", "detail": str(out)[:300], "note": "钩子内建 trade_date 查重幂等"}


def _stage_pf_alloc(data_date: str) -> dict[str, Any]:
    from zephyr.strategy_pipeline.pipeline_events import maybe_emit_pf_alloc_daily

    out = maybe_emit_pf_alloc_daily(task_id=_WAKE_DAILY, success=True)
    return {"status": "ok" if out.get("rc", 0) == 0 else "error", "detail": str(out)[:300]}


def _stage_intraday_l1(data_date: str) -> dict[str, Any]:
    from zephyr.plan_engine.intraday_l1_tracker import maybe_track_intraday_state

    out = maybe_track_intraday_state(task_id=_WAKE_60MIN, success=True)
    return {"status": "ok", "detail": str(out)[:300]}


def _stage_classify(data_date: str) -> dict[str, Any]:
    from zephyr.plan_engine.scenario_classifier import maybe_classify_intraday_scenario

    out = maybe_classify_intraday_scenario(task_id=_WAKE_60MIN, success=True)
    return {"status": "ok", "detail": str(out)[:300]}


def _stage_close_verify(data_date: str) -> dict[str, Any]:
    from zephyr.plan_engine.close_verifier import verify_for_session

    out = verify_for_session(data_date)
    return {"status": "ok", "detail": str(out)[:400]}


def _stage_settle(data_date: str) -> dict[str, Any]:
    from zephyr.plan_engine.judgment_settler import settle_all

    reports = settle_all(asof_day=data_date)
    return {"status": "ok", "brief": " | ".join(r.brief() for r in reports.values())[:400]}


def _stage_decision(data_date: str, *, force: bool) -> dict[str, Any]:
    from zephyr.strategy_pipeline.daily_decision_orchestrator import run_daily_decision

    out = run_daily_decision(data_date, force=force)
    return {"status": "ok", "action": out.get("action"), "brief": str(out.get("brief", ""))[:300]}


# ── Owner 扩面令（2026-09-21）A 类新段：未进编排器件的打通席位 ────────────────


def _stage_llm_premarket(data_date: str) -> dict[str, Any]:
    """盘前 LLM 分析（MOD-PLAN-007）：工序定义了无执行者——本段=执行者席位。

    llm_client 契约=prompt→str|Mapping；注入经 LLMRuntimeGateway（LSG 必经，
    BLOCK/DENY 不发起调用）。网关构造失败→本段 error 留痕（fail-open 不炸圈）。
    """
    from zephyr.integration.llm_runtime_gateway import LLMRuntimeGateway
    from zephyr.plan_engine.llm_premarket_analysis import run_llm_analysis

    gateway = LLMRuntimeGateway()

    def _client(prompt: str) -> dict[str, Any]:
        r = gateway.infer("premarket_analysis", prompt)
        return {
            "text": r.text,
            "model": r.model_version,
            "tokens_in": r.tokens_in,
            "tokens_out": r.tokens_out,
            "cost_yuan": r.cost_yuan,
        }

    res = run_llm_analysis(data_date, llm_client=_client)
    return {"status": "ok", "llm_status": getattr(res, "status", None), "detail": str(res)[:300]}


def _stage_sentiment_loop(data_date: str) -> dict[str, Any]:
    """盘中情绪环单拍（MOD-DATA-063）：单拍就绪没节拍——本段=节拍席位。

    previous_board 跨拍态 v1=None（新开板对照缺，SEC-02 降级留痕由模块自守）；
    落库=prediction_log sentiment_score（append-only 观测行）。
    """
    from zephyr.data.intraday_sentiment_loop import run_once

    res = run_once()
    sent = res.sentiment
    return {
        "status": "ok",
        "trade_date": res.trade_date,
        "prediction_log_id": res.prediction_log_id,
        "sentiment": getattr(sent, "label", None) or str(getattr(sent, "score", "")),
        "degraded": res.degraded,
        "notes": list(res.notes)[:3],
    }


def _stage_auction_hit(data_date: str) -> dict[str, Any]:
    """竞价命中 10:00 判定（MOD-PLAN-015）：本地 10:00-10:30 窗闸（PIT 卫生）。

    窗外=skipped（竞价三细节注入位 None→degraded 语义内建）；幂等=prediction_log
    内容 hash 保首条（同日重跑零重行）。
    """
    from datetime import datetime as _dt

    from zephyr.plan_engine.auction_hit_recorder import record_auction_hit

    now_local = _dt.now(_SHANGHAI).timetz().replace(tzinfo=None)
    if not (_AUCTION_WINDOW[0] <= now_local < _AUCTION_WINDOW[1]):
        return {
            "status": "skipped",
            "reason": "outside_auction_window",
            "window": "10:00-10:30 Asia/Shanghai",
            "now": str(now_local),
        }
    out = record_auction_hit(data_date)
    return {"status": "ok", "hit": getattr(out, "hit", None), "detail": str(out)[:300]}


def _stage_similar_day(data_date: str) -> dict[str, Any]:
    """相似日命中率评估（MOD-PLAN-016 挂靠件）：只读 prediction_log，零写库。"""
    from zephyr.plan_engine.similar_day_evaluator import evaluate_similar_day_hit_rate

    rep = evaluate_similar_day_hit_rate(eval_date=data_date)
    return {"status": "ok", "detail": str(rep)[:300]}


def _stage_attribution(data_date: str) -> dict[str, Any]:
    """W0 三维归因统计（MOD-PLAN-009）：纯统计只读，scenario_plan 族 W0 窗口。"""
    from datetime import date as _date

    from zephyr.plan_engine.scenario_attribution_stats import compute_scenario_attribution

    y, m, d = data_date.split("-")
    rep = compute_scenario_attribution(_SCENARIO_MODULE, window_days=20, as_of=_date(int(y), int(m), int(d)))
    return {"status": "ok", "detail": str(rep)[:300]}


# ── 段序注册（postmarket 内 verify 恒先于 settle——钩子序契约）───────────────

PHASE_STAGES: Final[dict[str, list[str]]] = {
    "premarket": ["data_readiness", "regime_freshness", "warroom", "daily_plan", "llm_premarket"],
    "intraday": ["intraday_l1", "classify", "sentiment_loop", "auction_hit"],
    "postmarket": [
        "close_verify",
        "warroom",
        "next_day",
        "pf_alloc",
        "settle",
        "similar_day",
        "attribution",
        "decision",
    ],
    "full": [
        "data_readiness",
        "regime_freshness",
        "warroom",
        "daily_plan",
        "llm_premarket",
        "next_day",
        "pf_alloc",
        "intraday_l1",
        "classify",
        "sentiment_loop",
        "auction_hit",
        "close_verify",
        "settle",
        "similar_day",
        "attribution",
        "decision",
    ],
}


def run_daily_loop(
    data_date: str | None = None, *, phase: str = "full", force_decision: bool = False, dry_run: bool = False
) -> dict[str, Any]:
    """跑一圈日循环（或指定段）。返回 JSON 可序列化报告，编排层零自建幂等键。

    data_date=None → 行情最新入库日（resolve_pf_alloc_trade_date 同源口径，禁墙钟猜日）。
    """
    if data_date is None:
        from zephyr.strategy_pipeline.pipeline_events import resolve_pf_alloc_trade_date

        data_date = resolve_pf_alloc_trade_date()
    if len(data_date) != _DATE_LEN or data_date.count("-") != 2:
        raise ValueError(f"data_date 非法（期望 YYYY-MM-DD）: {data_date}")
    if phase not in _VALID_PHASES:
        raise ValueError(f"phase 非法（期望 {_VALID_PHASES}）: {phase}")

    report: dict[str, Any] = {
        "data_date": data_date,
        "phase": phase,
        "mode": "observe_record_only_zero_orders",
        "pp001_snapshot": _pp001_snapshot(),
        "stages": {},
    }
    if dry_run:
        report["dry_run"] = True
        report["planned_stages"] = PHASE_STAGES[phase]
        report.pop("stages", None)  # dry-run 无执行面
        return report

    counts = {"ok": 0, "skipped": 0, "error": 0}
    # 查表法派发（NO-HIGH-COMPLEXITY 合规：禁 if/elif 长链）
    dispatch: dict[str, Callable[[str], dict[str, Any]]] = {
        "data_readiness": _stage_data_readiness,
        "regime_freshness": ensure_regime_fresh,
        "warroom": lambda dd: _stage_warroom(dd, phase),
        "daily_plan": _stage_daily_plan,
        "next_day": _stage_next_day,
        "pf_alloc": _stage_pf_alloc,
        "intraday_l1": _stage_intraday_l1,
        "classify": _stage_classify,
        "close_verify": _stage_close_verify,
        "settle": _stage_settle,
        "llm_premarket": _stage_llm_premarket,
        "sentiment_loop": _stage_sentiment_loop,
        "auction_hit": _stage_auction_hit,
        "similar_day": _stage_similar_day,
        "attribution": _stage_attribution,
        "decision": lambda dd: _stage_decision(dd, force=force_decision),
    }
    for name in PHASE_STAGES[phase]:
        fn = dispatch.get(name)
        if fn is None:  # pragma: no cover — PHASE_STAGES 与派发表失同步时显式炸出
            res: dict[str, Any] = {"status": "error", "error": f"未知段: {name}"}
        else:
            try:
                res = fn(data_date)
            except Exception as exc:  # noqa: BLE001 — 逐段 fail-open 留痕继续
                res = {"status": "error", "error": f"{type(exc).__name__}: {exc}"[:300]}
        if name == "data_readiness" and res.get("status") == "error":
            report["blocked"] = "数据就绪门失败（fail-closed：行情缺日不出预案）"
            report["stages"][name] = res
            counts["error"] += 1
            break
        report["stages"][name] = res
        counts[str(res.get("status", "error")) if str(res.get("status")) in counts else "error"] += 1
    report["summary"] = counts
    return report


if __name__ == "__main__":  # pragma: no cover — 手工补跑逃生口（非自动链路，编排器同款）
    print(json.dumps(run_daily_loop(None), ensure_ascii=False, indent=1, default=str))
