# [BLUEPRINT] MOD-PLAN-031 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六任务3
# [MODULE] zephyr.plan_engine.scenario_classifier
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.daily_plan(触发表达式求值器/计划装载——只 import 不改);
#   zephyr.plan_engine.intraday_l1_tracker(60min bars 拉取 SQL/代理口径/幂等键——只 import 不改);
#   zephyr.plan_engine.judgment_ledger(ULID+format_utc3); zephyr.plan_engine.judgment_settler(_reader_execute);
#   schemas.categories.judgment.judgment_plan_verification(INSERT 列清单真源); zephyr.data.ch_writer(写通道);
#   zephyr.shared.utils.time_utils(now_utc)
# [CONSUMERS] zephyr.plan_engine.close_verifier(replay_hits/scenarios_from_payload/write_verification 复用);
#   zephyr.strategy_pipeline.pipeline_events(事件挂点 maybe_classify_intraday_scenario——60min bars 入库唤醒);
#   judgment_plan_verification 台账（盘中行）; judgment_settler._settle_daily_plan（联结消费最新验证行）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定/结算分离（本件写验证事实行，结算列归 judgment_settler——标准 §一.2）; 触发=事件驱动
#   （60min bars 入库 SUCCESS 唤醒，禁 cron/Timer/sleep-loop——宪法 §9.3）; 触发状态=闭锁语义（同预案同场景
#   至多一 hit——首穿记录 trigger_ts/trigger_price，后续穿越不追加）; 幂等=确定性重放对账（bars 全量重放
#   hit 集与最新验证行一致→零写入；不一致→追加快照行——重放/重复唤醒天然抑制）; 只增不改（验证行 append-only）;
#   归类优先序=预案场景清单序（首个命中即归属——文档化，T3 同规则定格）; 盘中行 actual_scenario_id 恒空串
#   （定格归 T3——分拍职责边界）; 指数分钟源缺席=510300 ETF 60min 代理（P2a 既定口径，基差如实标注）;
#   表达式求值走 daily_plan 白名单 AST（禁 eval/exec）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(业务日不可解析——钩子侧捕获出声不反噬); ValueError(计划 payload 坏 JSON/
#   触发式非法——fail-closed 跳过该计划); 写失败不抛（disposition 留痕，重放下轮自愈）; CH 只读异常上抛点
#   全捕获（钩子永不反噬调度器，失败必须出声）
# [TESTS] tests/plan_engine/test_scenario_classifier.py
# [A_module] module_id=MOD-PLAN-031 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""scenario_classifier — 盘中场景归类器（判定台账标准 v0.1 §六任务 3 中段）。

交易时段每当一根 60min bar 落库（与 P2a 盘中 L1 跟踪件同唤醒点），用晨间预案
（daily_plan MOD-PLAN-030 产出）的可测触发条件对当日场景逐个判定：条件首穿即记
scenario_hits（trigger_ts/trigger_price），追加验证事实行到 judgment_plan_
verification。收盘定格（actual_scenario_id/plan_quality_score）归 close_verifier
（T3）——本件只写验证的**盘中部分**（盘中行 actual 恒空串）。

归类规则 v0（文档化，留待数据说话）：
  1. 逐 bar 装配特征（510300 ETF 60min 代理口径，P2a 既定）：
     - open_gap_pct = 当日首根 bar open / 前一交易日末根 bar close - 1（×100）
     - amount_ratio = 当日已收 bar 累计量 / 近 20 日同 bar 序号累计量均值
       （同序号=同一日内时钟对齐无未来函数；历史不足降级全日均量，ratio_note 标注）
     - ret_intraday_pct = 最新 bar close / 前日末根 bar close - 1（×100）
  2. 每根 bar 按预案场景**清单序**求值（优先序=清单序，文档化）：条件由假转真
     （首穿/闭锁）→ hit={scenario_id, trigger_ts(bar 收盘时刻上海时区), trigger_price
     (bar close)}；同场景后续穿越不重复记（一场景至多一 hit）。
  3. 特征缺席（表达式引用特征不可得）→ 该条件该 bar 不可满足（不触发），缺席原因
     留返回值由调用方标注——禁编造值（0 是合法测量值，缺席是另一回事）。

写行契约（judgment_plan_verification，只增不改）：
  - scenario_hits = 累积 hit JSON 数组（快照语义：每行=截至该 bar 的全量命中集）
  - actual_scenario_id = ''（定格归 T3）；plan_followed = 0（v0 预留编排器接口，
    执行链未接电前恒 0——如实不伪造）；deviations = '[]'（对接执行不一致记账
    execution_deviation_attributor 的挂点，v0 预留）；plan_quality_score = NULL（T3 口径）
  - verified_by = 'scenario_engine:intraday:<bar_key>'（写方+血缘双用途留痕）
  - 幂等：bars 确定性全量重放的 hit 集 == 最新验证行的 hit 集 → 零写入跳过

不做什么：不写结算列（无通道）；不做收盘定格（close_verifier）；不改编译 P2a
件（tracker/forecaster/ledger/settler 只 import）。

依据: docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表3/§六
      + 2026-09-16-blueprint-addendum-warroom-three-tasks.md 任务 3
SSoT: depgraph node 14585411（MOD-PLAN-031）
Version: 0.1.0
"""

from __future__ import annotations

import json
from datetime import timedelta
from typing import Any, Final, Sequence

from zephyr.data import ch_writer
from zephyr.plan_engine.daily_plan import (
    NO_SCENARIO,
    eval_trigger_measurable,
    load_plan_for_session,
    parse_trigger,
)
from zephyr.plan_engine.intraday_l1_tracker import (  # noqa: PLC2701 —— 私有常量复用（只 import 不改，
    # bars 拉取/代理口径/幂等键单一真源，禁另拼第二份——CLONE-GUARD 通道）
    _BARS_SQL,
    _ETF_PROXY_SYMBOL,
    _ETF_TABLE,
    _SHANGHAI,
    format_bar_key,
)
from zephyr.plan_engine.judgment_ledger import VERIFICATION_TABLE, format_utc3, new_judgment_id
from zephyr.plan_engine.judgment_settler import _reader_execute  # noqa: PLC2701 —— 注入点单点收口
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "MODULE_ID",
    "VERIFIED_BY_PREFIX",
    "latest_verification",
    "maybe_classify_intraday_scenario",
    "prev_session_close",
    "replay_hits",
    "scenarios_from_payload",
    "session_feature_at",
    "write_verification",
]

MODULE_ID: Final = "MOD-PLAN-031"
VERIFIED_BY_PREFIX: Final = "scenario_engine"  # 盘中验证行写方前缀（T3 用 close_verifier 前缀）

_VERIFICATION_TABLE: Final = VERIFICATION_TABLE  # 表名经 TableRegistry 真源派生（#ARCH-CH-024；2026-09-18 判定链注册迁移 st-ff-judgment-20260918），单点=judgment_ledger
from schemas.categories.judgment.judgment_plan_verification import (  # noqa: E402  # noqa: import-integrity  仓根 sys.path 由 judgment_ledger 运行时注入，静态 find_spec 不可解析（目标件在 HEAD）
    INSERT_COLUMNS as _VER_INSERT_COLS,
)

_LOOKUP_DAYS: Final = 45          # bars 回看窗口（与 P2a tracker 同口径）
_VOL_LOOKBACK_DAYS: Final = 20    # 量比历史窗口（交易日）


# ── 计划/验证行装载（消费方侧）──


def scenarios_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """预案 payload → 场景清单（结构 fail-closed：非 dict/无 scenarios/坏元素=ValueError）。"""
    if not isinstance(payload, dict):
        raise ValueError(f"预案 payload 非 dict: {type(payload).__name__}")
    scs = payload.get("scenarios")
    if not isinstance(scs, list) or not scs:
        raise ValueError("预案 payload 无 scenarios（禁归类空计划）")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for sc in scs:
        if not isinstance(sc, dict):
            raise ValueError(f"场景元素非 dict: {sc!r}")
        sid = str(sc.get("scenario_id") or "")
        trig = str(sc.get("trigger") or "")
        if not sid or not trig:
            raise ValueError(f"场景缺 scenario_id/trigger: {sc!r}")
        if sid in seen:
            raise ValueError(f"scenario_id 重复: {sid!r}")
        parse_trigger(trig)  # 文法+词表 fail-closed（坏触发式=ValueError 跳过该计划）
        seen.add(sid)
        out.append(sc)
    return out


def _last_verification_sql(jid: str) -> str:
    # noqa: bare-sql  最新验证行查询（参数受控：jid 来自本仓台账 ULID，集中拼接点）
    return (
        "SELECT scenario_hits, actual_scenario_id, verified_by, verified_at "
        f"FROM {_VERIFICATION_TABLE} WHERE plan_judgment_id = '{jid}' "
        "ORDER BY verified_at DESC, verification_id DESC LIMIT 1"
    )


def latest_verification(plan_judgment_id: str, *, reader=None) -> dict[str, Any] | None:
    """计划的最新验证行（结算器 _load_verifications 同取法——最新行覆盖语义一致）。"""
    rd = reader or _reader_execute
    rows = rd(_last_verification_sql(plan_judgment_id))
    if not rows:
        return None
    return {
        "scenario_hits": str(rows[0][0] or "[]"),
        "actual_scenario_id": str(rows[0][1] or ""),
        "verified_by": str(rows[0][2] or ""),
        "verified_at": rows[0][3],
    }


# ── 验证行写入（T2/T3 共用通道——append-only）──


def write_verification(
    *,
    plan_judgment_id: str,
    scenario_hits: str,
    actual_scenario_id: str = "",
    plan_followed: bool = False,
    deviations: str = "[]",
    plan_quality_score: float | None = None,
    verified_by: str,
    synthetic: bool = False,
    verified_at: Any = None,
) -> tuple[bool, str]:
    """追加一行验证事实（write_tsv_outcome；不抛——返回 (committed, disposition)）。

    Raises:
        ValueError: plan_judgment_id 为空（fail-closed——无联结键禁写行）。
    """
    if not plan_judgment_id:
        raise ValueError("plan_judgment_id 为空（无联结键禁写验证行）")
    va = verified_at or now_utc()
    if va.tzinfo is None:
        raise ValueError("verified_at 须带时区（RULE-SCHEMA-TZ）")
    row = "\t".join(
        ch_writer.tsv_escape(v)
        for v in (
            new_judgment_id(),
            plan_judgment_id,
            scenario_hits or "[]",
            actual_scenario_id or "",
            1 if plan_followed else 0,
            deviations or "[]",
            plan_quality_score,  # None→\N（Nullable 列——tsv_escape 契约）
            format_utc3(va),
            verified_by,
            1 if synthetic else 0,
        )
    )
    outcome = ch_writer.write_tsv_outcome(
        _VERIFICATION_TABLE, _VER_INSERT_COLS, (row + "\n").encode("utf-8")
    )
    committed = outcome.disposition == ch_writer.WriteDisposition.CH_COMMITTED
    return committed, str(outcome.disposition.value)


# ── 盘中特征/重放（纯函数：数据注入可单测）──


def prev_session_close(bars_hist: Sequence[tuple]) -> float | None:
    """前一交易日末根 bar close（缺口/盘中涨跌的基准锚；None=历史缺席）。"""
    if not bars_hist:
        return None
    last_day = str(bars_hist[-1][0])
    prev_last_close: float | None = None
    for row in bars_hist:
        if str(row[0]) == last_day:
            prev_last_close = float(row[3])  # 后写覆盖=当日最晚 bar
    return prev_last_close if prev_last_close and prev_last_close > 0 else None


def session_feature_at(
    bars_today: Sequence[tuple],
    bars_hist: Sequence[tuple],
    j: int,
    params: dict[str, float] | None = None,
) -> tuple[dict[str, float], str]:
    """截至第 j 根 bar（0 基）收盘的特征向量（ETF 代理口径）。

    Returns:
        ({open_gap_pct, amount_ratio, ret_intraday_pct}, ratio_note)。

    Raises:
        ValueError: 历史基准缺席（前日末根 close 不可得——调用方跳过该判定点）。
    """
    lookback = _VOL_LOOKBACK_DAYS if params is None else int(params.get("vol_lookback", _VOL_LOOKBACK_DAYS))
    prev_close = prev_session_close(bars_hist)
    if prev_close is None:
        raise ValueError("前日末根 bar close 不可得（历史缺席，禁判定）")
    first_open = float(bars_today[0][2])
    cur_close = float(bars_today[j][3])
    cum_vol = sum(float(r[6]) for r in bars_today[: j + 1])
    n = j + 1
    by_day: dict[str, list[tuple]] = {}
    for row in bars_hist:
        by_day.setdefault(str(row[0]), []).append(row)
    recent = sorted(by_day)[-(lookback):]
    same_idx = [
        sum(float(r[6]) for r in by_day[d][:n]) for d in recent if len(by_day[d]) >= n
    ]
    note = "same_index"
    if same_idx and cum_vol > 0 and sum(same_idx) > 0:
        base = sum(same_idx) / len(same_idx)
    else:
        full = [sum(float(r[6]) for r in by_day[d]) for d in recent]
        full = [v for v in full if v > 0]
        if not full or cum_vol <= 0:
            raise ValueError("量比基不可得（历史无有效量）")
        base = sum(full) / len(full)
        note = "full_day_fallback"
    return {
        "open_gap_pct": (first_open / prev_close - 1.0) * 100.0,
        "amount_ratio": cum_vol / base,
        "ret_intraday_pct": (cur_close / prev_close - 1.0) * 100.0,
    }, note


def _bar_trigger_ts(trade_time: Any) -> str:
    """bar 收盘时刻 → trigger_ts 字面量（上海时区 'YYYY-MM-DD HH:MM:00.000'）。"""
    import datetime as _dt

    if isinstance(trade_time, str):
        trade_time = _dt.datetime.fromisoformat(trade_time)
    if trade_time.tzinfo is None:
        trade_time = trade_time.replace(tzinfo=_SHANGHAI)
    sh = trade_time.astimezone(_SHANGHAI)
    return f"{sh.year:04d}-{sh.month:02d}-{sh.day:02d} {sh.hour:02d}:{sh.minute:02d}:00.000"


def replay_hits(
    bars_today: Sequence[tuple],
    bars_hist: Sequence[tuple],
    scenarios: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str | None]:
    """确定性重放：逐 bar 逐场景求值，条件首穿记 hit（同场景闭锁至多一 hit）。

    Returns:
        (hits [{scenario_id, trigger_ts, trigger_price}], missing_note)——hits 按
        触发时刻升序（同刻按清单序）；missing_note=首次特征缺席原因（或 None）。

    Raises:
        ValueError: bars 历史/当日结构不可判（调用方跳过）。
    """
    asts = [parse_trigger(str(sc["trigger"])) for sc in scenarios]
    hits: list[dict[str, Any]] = []
    latched: set[str] = set()
    missing_note: str | None = None
    for j in range(len(bars_today)):
        try:
            feats, _note = session_feature_at(bars_today, bars_hist, j)
        except ValueError as exc:
            if missing_note is None:
                missing_note = f"feature_unavailable:{exc}"
            break  # 特征链断了（历史缺席）——已有 hits 仍有效，后续 bar 不可判
        for sc, ast in zip(scenarios, asts):
            sid = str(sc["scenario_id"])
            if sid in latched:
                continue
            ok, miss = eval_trigger_measurable(ast, feats)
            if miss and missing_note is None:
                missing_note = miss
            if ok:
                latched.add(sid)
                hits.append({
                    "scenario_id": sid,
                    "trigger_ts": _bar_trigger_ts(bars_today[j][1]),
                    "trigger_price": float(bars_today[j][3]),
                })
    hits.sort(key=lambda h: (h["trigger_ts"], next(
        i for i, sc in enumerate(scenarios) if str(sc["scenario_id"]) == h["scenario_id"])))
    return hits, missing_note


def eval_or_missing(ast: tuple, features: dict[str, float]) -> tuple[bool, str | None]:
    """求值便壳（兼容别名——语义同 daily_plan.eval_trigger_measurable）。"""
    return eval_trigger_measurable(ast, features)


def earliest_actual(hits: Sequence[dict[str, Any]], scenarios: list[dict[str, Any]]) -> str:
    """命中集 → 实际场景：最早 trigger_ts 优先；同刻按清单序（归类规则文档化）。"""
    if not hits:
        return NO_SCENARIO
    order = {str(sc["scenario_id"]): i for i, sc in enumerate(scenarios)}
    return str(min(hits, key=lambda h: (h["trigger_ts"], order.get(h["scenario_id"], 10**9)))["scenario_id"])


# ── 组合入口（钩子薄壳）──


def _load_bars(day: str, *, reader=None) -> tuple[list[tuple], list[tuple]] | None:
    rd = reader or _reader_execute
    since = (day_dt(day) - timedelta(days=_LOOKUP_DAYS)).strftime("%Y-%m-%d")
    bars = rd(_BARS_SQL.format(table=_ETF_TABLE, symbol=_ETF_PROXY_SYMBOL, since=f"'{since}'"))
    if not bars:
        return None
    today = [r for r in bars if str(r[0]) == day]
    hist = [r for r in bars if str(r[0]) < day]
    if not today or not hist:
        return None
    return today, hist


def day_dt(day: str):
    """'YYYY-MM-DD' → date（钩子内部日期运算）。"""
    import datetime as _dt

    return _dt.datetime.strptime(day, "%Y-%m-%d").date()


def maybe_classify_intraday_scenario(task_id: Any = None, success: bool = True,
                                     **_kwargs) -> dict[str, Any]:
    """盘中场景归类的**唯一自动产出者**：60min bars 入库任务 SUCCESS=自然唤醒。

    宪法 §9.3 合规（零新机制，P2a maybe_track_intraday_state 同款骨架）：不建
    cron/Timer/sleep 循环，节拍由调度器给；确定性重放对账使重复唤醒/事件重放
    零副作用。当日业务日真源=墙钟上海日仅用于**选 bars**（无 bar 即零写入——
    非交易日天然抑制）；预案联结真源=行情库前一交易日（禁墙钟猜治理日）。
    永不抛：失败 WARN 出声不反噬唤醒链。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in ("kline_60min", "kline_etf_60min")):
        return {"action": "skipped_wake_point"}
    try:
        day = now_utc().astimezone(_SHANGHAI).strftime("%Y-%m-%d")
        prev_day = _reader_execute(
            "SELECT max(trade_date) FROM c1_market.kline_index "
            f"WHERE symbol = '000300' AND quality_flag = 1 AND trade_date < '{day}'"
        )[0][0]
        g_day = str(prev_day)
        plan = load_plan_for_session(g_day, reader=_reader_execute)  # reader 注入点（测试可换）
        if plan is None:
            return {"action": "no_plan", "session": day, "plan_date": g_day}
        scenarios = scenarios_from_payload(plan["payload"])
        bars = _load_bars(day)
        if bars is None:
            return {"action": "no_bars", "session": day}
        bars_today, bars_hist = bars
        hits, missing_note = replay_hits(bars_today, bars_hist, scenarios)
        last = latest_verification(plan["judgment_id"])
        if last is not None:
            if str(last.get("verified_by") or "").startswith("close_verifier"):
                # EOD 定格行已存在（收盘验证已完成）——盘中行冻结防晚到 bar 以 actual=''
                # 覆盖定格行（最新行覆盖语义下的自保闸）
                return {"action": "frozen_by_eod", "session": day, "n_hits": len(hits)}
            if _norm_hits(last["scenario_hits"]) == _norm_hits(json.dumps(hits)):
                return {"action": "no_change", "session": day, "bar_key": format_bar_key(bars_today[-1][1]),
                        "n_hits": len(hits)}
        committed, disposition = write_verification(
            plan_judgment_id=plan["judgment_id"],
            scenario_hits=json.dumps(hits, ensure_ascii=False),
            actual_scenario_id="",  # 定格归 close_verifier（分拍职责边界）
            verified_by=f"{VERIFIED_BY_PREFIX}:intraday:{format_bar_key(bars_today[-1][1])}",
        )
        if not committed:
            return {"action": "write_not_committed", "disposition": disposition,
                    "session": day, "n_hits": len(hits)}
        return {"action": "appended", "session": day, "n_hits": len(hits),
                "missing_note": missing_note,
                "bar_key": format_bar_key(bars_today[-1][1])}
    except ValueError as exc:
        return {"action": "skipped_invalid_plan", "reason": str(exc)[:200]}
    except Exception as exc:  # noqa: BLE001——钩子永不反噬调度器，失败必须出声
        return {"action": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}


def _norm_hits(hits_json: str) -> list[tuple[str, str, float]]:
    """hit 集规范化（对账键）：[(scenario_id, trigger_ts, round(price,6))] 升序。"""
    try:
        arr = json.loads(hits_json or "[]")
    except (ValueError, TypeError):
        return [("<<bad_json>>", "", 0.0)]
    out = []
    for h in arr if isinstance(arr, list) else []:
        if isinstance(h, dict):
            out.append((str(h.get("scenario_id")), str(h.get("trigger_ts")),
                        round(float(h.get("trigger_price") or 0.0), 6)))
    return sorted(out)


if __name__ == "__main__":  # pragma: no cover — 手工补跑逃生口（非自动链路）
    print(maybe_classify_intraday_scenario(task_id="manual_cli", success=True))


class ScenarioClassifier:
    """归类 facade（scaffold 契约）：模块级组合入口的对象化包装（无独立状态）。"""

    module_id: str = MODULE_ID

    def classify_once(self) -> dict[str, Any]:
        """跑一次唤醒点等价的盘中归类（手工补跑/冒烟入口）。"""
        return maybe_classify_intraday_scenario(task_id="manual_facade", success=True)

    def replay(self, bars_today: Sequence[tuple], bars_hist: Sequence[tuple],
               scenarios: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str | None]:
        """重放直通（replay_hits 纯函数——测试与人工核查用）。"""
        return replay_hits(bars_today, bars_hist, scenarios)
