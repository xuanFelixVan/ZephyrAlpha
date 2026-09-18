# [BLUEPRINT] MOD-PLAN-032 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六任务3
# [MODULE] zephyr.plan_engine.close_verifier
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.daily_plan(daily_features_of/load_plan_for_session/NO_SCENARIO——只 import 不改);
#   zephyr.plan_engine.scenario_classifier(replay_hits/scenarios_from_payload/write_verification/earliest_actual——
#   只 import 不改); zephyr.plan_engine.judgment_settler(_reader_execute); zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] zephyr.strategy_pipeline.pipeline_events(事件挂点 maybe_verify_plan_close——daily_kline SUCCESS 唤醒);
#   judgment_plan_verification 台账（EOD 定格行）; judgment_settler._settle_daily_plan（联结最新验证行回填
#   judgment_daily_plan 结算列——P1 链自动闭环）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定/结算分离（本件写验证事实行，结算列归 judgment_settler——标准 §一.2）; 触发=事件驱动
#   （daily_kline SUCCESS 唤醒，禁 cron/Timer/sleep-loop——宪法 §9.3）; 宽限期契约=P1 惯例（治理次日验证，
#   当日宽限；隔日无验证由结算器 unresolvable(verification_missing) 如实留痕——本件只写有证据的事实，
#   无证据不写行）；幂等=EOD 定格行查重（verified_by 前缀 close_verifier 已存在→零写入）; 只增不改
#   （验证行 append-only，EOD 行=最新行覆盖语义——结算器取最新）; actual 归类规则文档化：盘中 hits 非空=
#   最早 trigger_ts 优先（同刻清单序）；hits 空=日线 EOD 特征兜底归类；仍不中=no_scenario 哨兵（预案未覆盖
#   如实留痕，结算侧 actual_scenario_unknown=覆盖缺口可见，禁硬凑全覆盖）; plan_quality_score=path_prior 对
#   实际场景的似然取值（∈[0,1]，no_scenario/未知=0.0——口径文档化留待数据说话）; plan_followed v0 恒 0
#   （编排器执行链未接电，预留接口不伪造）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(业务日不可解析——钩子侧捕获出声不反噬); ValueError(计划 payload 坏/日线
#   缺席——fail-closed 不写行留结算器宽限链); 写失败不抛（disposition 留痕，下轮唤醒自愈）
# [TESTS] tests/plan_engine/test_close_verifier.py
# [A_module] module_id=MOD-PLAN-032 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""close_verifier — 收盘验证器（判定台账标准 v0.1 §六任务 3 下半，作战室"验证昨日计划"收口件）。

T+1（治理时段）收盘数据入库后（daily_kline SUCCESS=自然唤醒，与结算器同拍但**先于
结算器执行**——验证行必须先落库，结算器才能联结最新验证行回填 judgment_daily_plan
结算列；钩子序由 pipeline_events wire 顺序保证），对治理日=前一日(G)的预案完成
plan_verification 定格：

  1. 重放盘中 hits（scenario_classifier.replay_hits，510300 ETF 60min bars 确定性
     重放——与 T2 盘中行同口径同函数，幂等对账不冲突）。
  2. actual_scenario 定格（归类规则文档化）：
     - hits 非空 → 最早 trigger_ts 的场景（同刻按预案清单序——"路径首次兑现"口径）；
     - hits 空 → 日线 EOD 特征兜底归类（daily_features_of 指数日线口径，逐场景清单序
       求值——盘中分钟源缺席时的最低证据归类，verified_by 标 :eod_daily_proxy）；
     - 仍不中 → actual='no_scenario' 哨兵（预案未覆盖当日路径，如实记账——结算侧
       按 verification 链 unresolvable(actual_scenario_unknown) 呈现覆盖缺口，数据说话）。
  3. plan_quality_score = 预案 path_prior 对 actual 的似然取值（∈[0,1]；actual 不在
     分支集=0.0）——"触发预测命中率"的分布口径；argmax 命中等价于取值=max(prior)。
  4. plan_followed = 0（v0 预留：编排器执行链接电后由执行记账回填 deviations/判定，
     本件不伪造执行结论）；deviations = '[]'（对接 execution_deviation_attributor 挂点）。

EOD 行（verified_by='close_verifier:v0[:mode]'）追加后即该计划**最新**验证行——
结算器 _load_verifications 最新行覆盖语义下，盘中快照行自动被定格行覆盖（只增不改
约束下的收敛通道）。60min bars 缺席（分钟源断供）→ 降级日线 EOD 兜底；日线也缺席
→ 不写行（结算器宽限链如实 unresolvable）。

不做什么：不写结算列（无通道）；不改 P2a/P1 件（只 import）；不做执行对比判定
（plan_followed 预留）；不跑 unresolvable（结算器职责——本件只写有证据的事实）。

依据: docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六
      + 2026-09-16-blueprint-addendum-warroom-three-tasks.md 任务 3
SSoT: depgraph node 14585412（MOD-PLAN-032）
Version: 0.1.0
"""

from __future__ import annotations

import json
from typing import Any, Final, Sequence

from zephyr.plan_engine.daily_plan import (
    NO_SCENARIO,
    RULE_PARAMS,
    daily_features_of,
    eval_trigger_measurable,
    load_plan_for_session,
    parse_trigger,
)
from zephyr.plan_engine.judgment_ledger import VERIFICATION_TABLE
from zephyr.plan_engine.judgment_settler import _reader_execute  # noqa: PLC2701 —— 注入点单点收口
from zephyr.plan_engine.scenario_classifier import (  # noqa: PLC2701 —— 私有复用通道（只 import 不改）
    earliest_actual,
    replay_hits,
    scenarios_from_payload,
    write_verification,
)

__all__: Final = [
    "MODULE_ID",
    "VERIFIED_BY_EOD",
    "classify_actual",
    "maybe_verify_plan_close",
    "prev_business_day",
    "quality_score_of",
]

MODULE_ID: Final = "MOD-PLAN-032"
VERIFIED_BY_EOD: Final = "close_verifier:v0"  # EOD 定格行写方前缀（幂等查重键）

_KLINE_SQL: Final = (
    "SELECT trade_date, open, high, low, close, volume "
    "FROM c1_market.kline_index WHERE symbol = '000300' AND quality_flag = 1 "
    "ORDER BY trade_date"
)
_PREV_DAY_SQL: Final = (
    "SELECT max(trade_date) FROM c1_market.kline_index "
    "WHERE symbol = '000300' AND quality_flag = 1 AND trade_date < '{day}'"
)
_SQL_EOD_VERIFIED = (
    "SELECT count() "
    "FROM {table} "
    "WHERE plan_judgment_id = '{jid}' AND verified_by LIKE 'close_verifier%'"
)
# 60min bars 拉取（降级判定用——缺席走日线兜底，不经手 tracker 私有 SQL：此处只判有无）
_HAS_BARS_SQL: Final = (
    "SELECT count() FROM c1_market.kline_etf_60min "
    "WHERE symbol = '510300' AND trade_date = '{day}'"
)


def prev_business_day(day: str, *, reader=None) -> str | None:
    """行情库口径的前一交易日（治理日 G 真源——禁墙钟猜日）。None=不可解析。"""
    rd = reader or _reader_execute
    rows = rd(_PREV_DAY_SQL.format(day=day))
    if not rows or rows[0][0] is None:
        return None
    return str(rows[0][0])


def classify_actual(
    scenarios: list[dict[str, Any]],
    hits: Sequence[dict[str, Any]],
    eod_features: dict[str, float] | None,
) -> tuple[str, str]:
    """actual_scenario 定格（归类规则文档化——见模块头 §2）。

    Args:
        scenarios: 预案分支清单（清单序=优先序）。
        hits: 盘中重放命中集（可空）。
        eod_features: 日线 EOD 特征（None=不可得——兜底归类不可用）。

    Returns:
        (actual_scenario_id, mode)：mode∈{intraday_hits, eod_daily_proxy, no_scenario}。
    """
    if hits:
        return earliest_actual(list(hits), scenarios), "intraday_hits"
    if eod_features:
        for sc in scenarios:
            ast = parse_trigger(str(sc["trigger"]))
            ok, _miss = eval_trigger_measurable(ast, eod_features)
            if ok:
                return str(sc["scenario_id"]), "eod_daily_proxy"
    return NO_SCENARIO, "no_scenario"


def quality_score_of(
    scenarios: list[dict[str, Any]],
    actual: str,
) -> float:
    """plan_quality_score（口径文档化）：path_prior 对 actual 的似然取值 ∈[0,1]。

    actual 不在分支集（含 no_scenario 哨兵）= 0.0（预案未覆盖实际路径——如实给 0
    而非编造中性分）；分布口径下 argmax 命中等价于取值=max(prior)。
    """
    for sc in scenarios:
        if str(sc.get("scenario_id")) == actual:
            try:
                v = float(sc.get("path_prior") or 0.0)
            except (TypeError, ValueError):
                return 0.0
            return max(0.0, min(1.0, v))
    return 0.0


def _eod_features_for(day: str, rows: Sequence[tuple], *,
                      params: dict[str, float] = RULE_PARAMS) -> dict[str, float] | None:
    """G+1=day 的日线 EOD 特征（daily_features_of 复用——指数日线口径）。"""
    day_rows = [r for r in rows if str(r[0]) <= day]
    if not day_rows or str(day_rows[-1][0]) != day or len(day_rows) < 2:
        return None
    lookback = int(params["vol_lookback"])
    vol_hist = [float(r[5]) for r in day_rows[-(lookback + 1):-1]]
    return daily_features_of(day_rows[-2], day_rows[-1], vol_hist, params)


def verify_for_session(
    day: str,
    *,
    reader=None,
    synthetic: bool = False,
) -> dict[str, Any]:
    """单治理时段验证定格（组合入口：G=prev(day)→计划→重放→归类→追加 EOD 行）。

    Raises:
        ValueError: 前一交易日不可解析/日线缺席（fail-closed——不写行留宽限链）。
    """
    rd = reader or _reader_execute
    g_day = prev_business_day(day, reader=rd)
    if g_day is None:
        raise ValueError(f"前一交易日不可解析（day={day}，行情库断供?）")
    plan = load_plan_for_session(g_day, reader=rd)
    if plan is None:
        return {"action": "no_plan", "session": day, "plan_date": g_day}
    rows = rd(_KLINE_SQL)
    eod_feats = _eod_features_for(day, rows)
    if eod_feats is None:
        raise ValueError(f"T+1 日线不在库（day={day}，禁猜日验证）")
    scenarios = scenarios_from_payload(plan["payload"])

    # 已定格→幂等零写入（EOD 行查重）
    cnt = rd(_SQL_EOD_VERIFIED.format(table=VERIFICATION_TABLE, jid=plan["judgment_id"]))
    if cnt and int(cnt[0][0]) > 0:
        return {"action": "already_verified", "session": day, "plan_date": g_day,
                "judgment_id": plan["judgment_id"]}

    # 盘中重放（60min bars 有则用；缺席降级日线兜底）
    hits: list[dict[str, Any]] = []
    mode_hint = ""
    from zephyr.plan_engine.scenario_classifier import _load_bars  # noqa: PLC0415 —— 私有复用通道

    bars = _load_bars(day, reader=rd)
    if bars is not None:
        hits, missing_note = replay_hits(bars[0], bars[1], scenarios)
        mode_hint = ":bars_replay" + (f":missing:{missing_note}" if missing_note else "")
    else:
        mode_hint = ":eod_daily_proxy(no_60min_bars)"

    actual, mode = classify_actual(scenarios, hits, eod_feats)
    score = quality_score_of(scenarios, actual)
    committed, disposition = write_verification(
        plan_judgment_id=plan["judgment_id"],
        scenario_hits=json.dumps(list(hits), ensure_ascii=False),
        actual_scenario_id=actual,
        plan_followed=False,  # v0 预留编排器接口（执行链未接电恒 0——不伪造）
        deviations="[]",
        plan_quality_score=score,
        verified_by=f"{VERIFIED_BY_EOD}{mode_hint}|mode:{mode}",
        synthetic=synthetic,
    )
    if not committed:
        return {"action": "write_not_committed", "disposition": disposition,
                "session": day, "plan_date": g_day}
    return {
        "action": "verified",
        "session": day,
        "plan_date": g_day,
        "judgment_id": plan["judgment_id"],
        "actual_scenario_id": actual,
        "mode": mode,
        "plan_quality_score": score,
        "n_hits": len(hits),
    }


def maybe_verify_plan_close(task_id: Any = None, success: bool = True,
                            **_kwargs) -> dict[str, Any]:
    """收盘验证的**唯一自动产出者**：daily_kline SUCCESS=自然唤醒（T+1 收盘数据齐）。

    宪法 §9.3 合规（零新机制，P2a 钩子同款骨架）：不建 cron/Timer/sleep 循环。
    业务日 D=resolve_pf_alloc_trade_date()（禁墙钟猜日），G=行情库前一交易日。
    EOD 行幂等查重——重复唤醒零副作用。永不抛：失败 WARN 出声不反噬唤醒链。
    钩子序契约：必须先于 maybe_settle_judgment_ledger 执行（验证行先落库，
    结算器才能联结——否则当日宽限被误判 unresolvable，见 wire 注释）。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in ("daily_kline", "kline_daily", "kline_index")):
        return {"action": "skipped_wake_point"}
    day = ""
    try:
        from zephyr.strategy_pipeline.pipeline_events import resolve_pf_alloc_trade_date

        day = resolve_pf_alloc_trade_date()  # 共用业务日真源（禁墙钟猜日）
        return verify_for_session(day)
    except ValueError as exc:
        # 必需数据缺席=fail-closed 不写行（结算器宽限链如实处置）——下个唤醒点自愈
        return {"action": "data_insufficient", "session": day, "reason": str(exc)[:200]}
    except Exception as exc:  # noqa: BLE001——钩子永不反噬调度器，失败必须出声
        return {"action": "error", "session": day,
                "error": f"{type(exc).__name__}: {exc}"[:200]}


if __name__ == "__main__":  # pragma: no cover — 手工补跑逃生口（非自动链路）
    print(maybe_verify_plan_close(task_id="manual_cli", success=True))


class CloseVerifier:
    """验证 facade（scaffold 契约）：模块级组合入口的对象化包装（无独立状态）。"""

    module_id: str = MODULE_ID

    def verify_once(self) -> dict[str, Any]:
        """跑一次唤醒点等价的收盘验证（手工补跑/冒烟入口）。"""
        return maybe_verify_plan_close(task_id="manual_facade", success=True)
