# [BLUEPRINT] MOD-PLAN-029 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表2/§六任务2
# [MODULE] zephyr.plan_engine.next_day_forecaster
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.judgment_ledger(一行发射); zephyr.infrastructure.database_service(reader);
#   zephyr.shared.utils.time_utils(now_utc——SCHEMA-TZ 时钟真源)
# [CONSUMERS] zephyr.strategy_pipeline.pipeline_events(事件挂点 maybe_emit_next_day_forecast——
#   daily_kline SUCCESS 唤醒); judgment_next_day_forecast 台账; brier 日常闭环（P1 结算链自动覆盖本表）;
#   Phase 5 meta-回测逐层归因（数据源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定/结算分离（本件只发射判定，结算归 judgment_settler——标准 §一.2）; 触发=事件驱动
#   （daily_kline SUCCESS 唤醒，禁 cron/Timer/sleep-loop——宪法 §9.3）; 业务日真源=行情库
#   （resolve_pf_alloc_trade_date 复用，禁墙钟猜日——非交易日/数据晚到日天然抑制）; 幂等=trade_date
#   查重（judgment_next_day_forecast 按 module_id+inputs_ref LIKE 匹配，一业务日至多一判，重复唤醒
#   零副作用）; inputs_hash=当日输入指纹（sha256 截断落 inputs_ref——同输入可复算，输入变=指纹变）;
#   桶样本不足=退化全样本基线（fallback 如实标注，禁编造分布）; 概率 Laplace 平滑+和恒 1（结构性归一）;
#   历史样本窗口按 trade_date 截断于 T 日之前（PIT：未来数据禁入样本）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(业务日不可解析——钩子侧捕获出声不反噬); ValueError(日线不足/涨跌家数
#   缺失/T 日不在库——fail-closed 宁漏判不瞎判); 发射失败不抛（EmitResult.committed=False 留痕）
# [TESTS] tests/plan_engine/test_next_day_forecaster.py
# [A_module] module_id=MOD-PLAN-029 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""next_day_forecaster — 次日概率件（判定台账标准 v0.1 §六任务 2）。

T 日收盘数据入库后（daily_kline SUCCESS=自然唤醒），翻历史账找与今天同条件的
日子，统计他们次日的涨平跌频率，产出 T+1 三元概率分布+分布分位+预期波动，
经 judgment_ledger.emit_judgment 一行发射到 c1_market.judgment_next_day_forecast。
T+1 收盘后由 P1 结算链（judgment_settler，已挂同一事件）自动回填
realized_return/brier_score/log_loss/calibration_bucket——台账闭环零额外布线。

v0 判定规则（历史条件统计基线，参数全部显式声明于 RULE_PARAMS；v0 后续可整体
替换为逻辑回归/GBDT 而不动表契约）：
  1. T 日特征（kline_index 000300 日线）：
     - ret = close/prev_close - 1
     - vol_ratio = volume / 前 VOL_LOOKBACK 日均量
     - breadth = advance_count/(advance_count+decline_count)
  2. 条件桶（3×3=9 桶）：ret_bucket∈{up,flat,down}（±RET_BAND 带宽）×
     vol_bucket∈{low,mid,high}（VOL_LOW/VOL_HIGH 阈）。
  3. 历史同桶次日收益序列（全量可用历史，trade_date 截断于 T 日之前——PIT）→
     - p_up/p_flat/p_down = Laplace 平滑频率（(n_k+α)/(N+3α)——和恒 1 结构性归一）；
     - quantiles q10/q25/q50/q75/q90 = 线性插值分位（次日 ret，百分比）；
     - expected_vol_pct = 次日 ret 标准差 ×100；expected_range_pct = 次日日内
       振幅（high/low-1）均值 ×100；
     - 桶样本 < MIN_BUCKET_N → 退化全样本基线（fallback=True 如实标注）。
  4. confidence = min(n/CONF_N_FULL, CONF_CAP)；fallback 时折半（样本证据弱）。

幂等与业务日：D=resolve_pf_alloc_trade_date()（行情最新入库日，与 pf_alloc/
regime/结算链同真源）；inputs_ref 含 trade_date:<D> 幂等键——已发射过 D 则零
发射跳过（周末/节假日唤醒时 D 不变=天然抑制重复判定）。

inputs_hash=sha256("D|close|volume|advance|decline|bucket|n_history")[:16]——
当日输入指纹，同输入必同指纹（可复算审计），输入变=指纹变（修订可追溯）。

不做什么：不写结算列（无通道）；不做个股（subject 仅 index:000300.SH——Phase 1
结算映射首批）；不做场景预案（归作战室任务 3）。

依据: docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表2/§六
SSoT: depgraph node 14570139（MOD-PLAN-029）
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import math
from datetime import datetime
from typing import Any, Final, Sequence

from zephyr.plan_engine.judgment_ledger import (
    EmitResult,
    JudgmentDraft,
    emit_judgment,
)
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "MODULE_ID",
    "MODEL_VERSION",
    "RULE_PARAMS",
    "SUBJECT",
    "NextDayForecaster",
    "build_day_features",
    "bucket_of",
    "cond_prob_from_history",
    "emit_for_trade_date",
    "inputs_hash_of",
    "maybe_emit_next_day_forecast",
    "percentile",
]

MODULE_ID: Final = "MOD-PLAN-029"
MODEL_VERSION: Final = "v0-hist"
SUBJECT: Final = "index:000300.SH"

# ── v0 规则参数（单点声明；调参=改这里+跑测试）──
RULE_PARAMS: Final[dict[str, float]] = {
    "ret_band": 0.003,     # T 日涨跌桶带宽（±0.3% 之外才算方向日）
    "vol_low": 0.8,        # 量能桶下阈（缩量）
    "vol_high": 1.2,       # 量能桶上阈（放量）
    "vol_lookback": 20,    # 量比窗口（交易日）
    "laplace_alpha": 5.0,  # Laplace 平滑伪计数（防小样本 0/1 极端概率）
    "min_bucket_n": 20,    # 桶最小样本（不足退化全样本基线）
    "conf_n_full": 60.0,   # 置信饱和样本量（n≥60 → conf=cap）
    "conf_cap": 0.9,       # 置信上限（v0 不给满置信）
}

_INDEX_TABLE: Final = "c1_market.kline_index"
_SYMBOL: Final = "000300"

# 日线拉取（全量一次——2005→今约 5000 行，台账行数量级小）
_KLINE_SQL: Final = (
    "SELECT trade_date, open, high, low, close, volume, advance_count, decline_count "
    "FROM {table} WHERE symbol = '{symbol}' AND quality_flag = 1 "
    "ORDER BY trade_date"
)
# 幂等查重：同 module_id + 同业务日（inputs_ref 结构化指纹 LIKE 匹配）。
# 模式不带前导 '|'——trade_date 是 inputs_ref 首键（首键前无分隔符，'%|key|%' 永远
# miss=幂等失效三连发事故修复 2026-09-17）；尾 '|' 防日期前缀误配（15 不吃 15X）。
_ALREADY_EMITTED_SQL: Final = (
    "SELECT count() FROM c1_market.judgment_next_day_forecast "
    "WHERE module_id = '{module_id}' AND inputs_ref LIKE '%trade_date:{day}|%'"
)


# ── 只读通道（模块级函数=测试注入点；实现单点收口于共享结算器库件——本件只 import
#    不复制（CLONE-GUARD AGG-40410b77 治本），生产走 DatabaseService reader，§9.1）──

from zephyr.plan_engine.judgment_settler import _reader_execute  # noqa: PLC2701


# ── 纯函数（判定核心，数据注入可单测）──


def percentile(sorted_vals: Sequence[float], q: float) -> float:
    """线性插值分位数（sorted_vals 升序；q∈[0,1]；空序列=ValueError fail-closed）。"""
    if not sorted_vals:
        raise ValueError("percentile 空序列（禁编造分位）")
    if not 0.0 <= q <= 1.0:
        raise ValueError(f"分位 q 须在 [0,1]: {q!r}")
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return float(sorted_vals[lo]) * (1.0 - frac) + float(sorted_vals[hi]) * frac


def build_day_features(rows: Sequence[tuple]) -> dict[str, float]:
    """T 日（rows 末行）特征装配。

    Args:
        rows: kline_index 日线 [(trade_date, open, high, low, close, volume,
            advance_count, decline_count)]，按 trade_date 升序，至少 VOL_LOOKBACK+1 行。

    Returns:
        {trade_date, ret, vol_ratio, breadth, close, volume, advance, decline,
        degraded_breadth}。breadth 不可得（涨跌家数 0——kline_index 该列 2026-07 后
        断供的实际缺口）=键缺席+degraded_breadth=True 降级标注，不 raise（breadth
        不参与条件桶，桶统计仍完备；缺席如实进 evidence 由 confidence 反映）。

    Raises:
        ValueError: 行数不足/均量非正（fail-closed——桶统计不可得时禁打分）。
    """
    lookback = int(RULE_PARAMS["vol_lookback"])
    if len(rows) < lookback + 1:
        raise ValueError(f"日线历史不足（须 ≥{lookback + 1} 行，实得 {len(rows)}）")
    t = rows[-1]
    prev = rows[-2]
    prev_close = float(prev[4])
    close = float(t[4])
    if prev_close <= 0:
        raise ValueError("前收非正（数据异常，禁打分）")
    ret = close / prev_close - 1.0
    vol_hist = [float(r[5]) for r in rows[-(lookback + 1):-1]]
    vol_mean = sum(vol_hist) / len(vol_hist)
    if vol_mean <= 0:
        raise ValueError("历史均量非正（数据异常，禁打分）")
    vol_ratio = float(t[5]) / vol_mean
    adv = float(t[6] or 0)
    dec = float(t[7] or 0)
    feat = {
        "trade_date": str(t[0]),
        "ret": ret,
        "vol_ratio": vol_ratio,
        "close": close,
        "volume": float(t[5]),
        "advance": adv,
        "decline": dec,
        "degraded_breadth": True,
    }
    if adv + dec > 0:
        feat["breadth"] = adv / (adv + dec)
        feat["degraded_breadth"] = False
    return feat


def bucket_of(feat: dict[str, float], params: dict[str, float] = RULE_PARAMS) -> tuple[str, str]:
    """T 日条件桶（ret_bucket, vol_bucket）——3×3 判定坐标。"""
    band = float(params["ret_band"])
    if feat["ret"] > band:
        rb = "up"
    elif feat["ret"] < -band:
        rb = "down"
    else:
        rb = "flat"
    vr = feat["vol_ratio"]
    vb = "low" if vr < float(params["vol_low"]) else ("high" if vr > float(params["vol_high"]) else "mid")
    return rb, vb


def cond_prob_from_history(
    rows: Sequence[tuple],
    feat: dict[str, float],
    params: dict[str, float] = RULE_PARAMS,
) -> dict[str, Any]:
    """历史条件统计 → 次日判定主体（概率/分位/波动，不含 evidence 包装）。

    以 trade_date 早于 T 日的全部历史为样本（PIT：未来数据禁入）：找同桶日，
    取其次日 ret/振幅序列做 Laplace 频率+分位统计。桶样本不足 → 全样本基线
    （fallback=True 如实标注）。

    Returns:
        {p_up, p_flat, p_down, quantiles{q10..q90}, expected_vol_pct,
         expected_range_pct, n, fallback, ret_bucket, vol_bucket}

    Raises:
        ValueError: 历史统计样本为空（禁编造分布，fail-closed）。
    """
    rb, vb = bucket_of(feat, params)
    band = float(params["ret_band"])
    lookback = int(RULE_PARAMS["vol_lookback"])
    next_rets: dict[str, list[float]] = {}  # "rb:vb" → 次日 ret 列表
    next_ranges: dict[str, list[float]] = {}
    all_rets: list[float] = []
    all_ranges: list[float] = []
    for i in range(lookback, len(rows) - 1):  # 末行=T 日本体；统计只用其之前
        cur = rows[i]
        nxt = rows[i + 1]
        if str(cur[0]) >= feat["trade_date"]:
            break  # PIT 截断：只用 T 日之前的历史
        prev_c = float(rows[i - 1][4])
        if prev_c <= 0 or float(cur[4]) <= 0 or float(cur[5]) <= 0:
            continue
        c_ret = float(cur[4]) / prev_c - 1.0
        vol_mean_i = sum(float(r[5]) for r in rows[i - lookback:i]) / lookback
        if vol_mean_i <= 0:
            continue
        c_vr = float(cur[5]) / vol_mean_i
        h_rb, h_vb = bucket_of({"ret": c_ret, "vol_ratio": c_vr}, params)
        n_ret = float(nxt[4]) / float(cur[4]) - 1.0  # 次日收益（对当日收盘）
        n_range = (float(nxt[2]) / float(nxt[3]) - 1.0) if float(nxt[3]) > 0 else 0.0
        key = f"{h_rb}:{h_vb}"
        next_rets.setdefault(key, []).append(n_ret)
        next_ranges.setdefault(key, []).append(n_range)
        all_rets.append(n_ret)
        all_ranges.append(n_range)
    if not all_rets:
        raise ValueError("历史统计样本为空（禁编造分布）")
    same = next_rets.get(f"{rb}:{vb}", [])
    fallback = len(same) < int(params["min_bucket_n"])
    use_rets = same if not fallback else all_rets
    use_ranges = same if not fallback else all_ranges
    n = len(use_rets)

    alpha = float(params["laplace_alpha"])
    counts = [
        sum(1 for r in use_rets if r > band),
        sum(1 for r in use_rets if -band <= r <= band),
        sum(1 for r in use_rets if r < -band),
    ]
    denom = n + 3.0 * alpha
    p_up, p_flat, p_down = ((c + alpha) / denom for c in counts)

    s = sorted(use_rets)
    quantiles = {
        "q10": round(percentile(s, 0.10) * 100.0, 3),
        "q25": round(percentile(s, 0.25) * 100.0, 3),
        "q50": round(percentile(s, 0.50) * 100.0, 3),
        "q75": round(percentile(s, 0.75) * 100.0, 3),
        "q90": round(percentile(s, 0.90) * 100.0, 3),
    }
    mean = sum(use_rets) / n
    var = sum((r - mean) ** 2 for r in use_rets) / n
    expected_vol_pct = round(math.sqrt(var) * 100.0, 3)
    expected_range_pct = round(sum(use_ranges) / len(use_ranges) * 100.0, 3) if use_ranges else 0.0
    return {
        "p_up": round(p_up, 6),
        "p_flat": round(p_flat, 6),
        "p_down": round(p_down, 6),
        "quantiles": quantiles,
        "expected_vol_pct": expected_vol_pct,
        "expected_range_pct": expected_range_pct,
        "n": n,
        "fallback": fallback,
        "ret_bucket": rb,
        "vol_bucket": vb,
    }


def inputs_hash_of(feat: dict[str, float], stats: dict[str, Any]) -> str:
    """当日输入指纹（sha256 截断 16 hex）：同输入必同指纹，输入变=指纹变。"""
    raw = "|".join([
        feat["trade_date"], f"{feat['close']:.4f}", f"{feat['volume']:.0f}",
        f"{feat['advance']:.0f}", f"{feat['decline']:.0f}",
        stats["ret_bucket"], stats["vol_bucket"], str(stats["n"]),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def emit_for_trade_date(
    day: str,
    *,
    reader=None,
    synthetic: bool = False,
    asof_ts: datetime | None = None,
) -> EmitResult:
    """T 日次日判定发射（组合入口：读库→特征→条件统计→emit_judgment）。

    Raises:
        ValueError: T 日不在库/历史不足/特征缺失（fail-closed，调用方出声处理）。
    """
    rd = reader or _reader_execute
    rows = rd(_KLINE_SQL.format(table=_INDEX_TABLE, symbol=_SYMBOL))
    day_rows = [r for r in rows if str(r[0]) <= day]
    if not day_rows or str(day_rows[-1][0]) != day:
        raise ValueError(f"T 日 {day} 日线不在库（禁猜日发射）")
    feat = build_day_features(day_rows)
    stats = cond_prob_from_history(day_rows, feat)
    h = inputs_hash_of(feat, stats)
    payload = {
        "p_up": stats["p_up"],
        "p_flat": stats["p_flat"],
        "p_down": stats["p_down"],
        "quantiles": stats["quantiles"],
        "expected_vol_pct": stats["expected_vol_pct"],
        "expected_range_pct": stats["expected_range_pct"],
        "evidence": {
            "ret_bucket": stats["ret_bucket"],
            "vol_bucket": stats["vol_bucket"],
            "n_bucket": stats["n"],
            "fallback": stats["fallback"],
            "vol_ratio": round(feat["vol_ratio"], 4),
            "breadth": round(feat["breadth"], 4) if "breadth" in feat else None,
            "degraded_breadth": feat.get("degraded_breadth", False),
        },
    }
    inputs_ref = (
        f"trade_date:{day}|inputs_hash:{h}|bucket:{stats['ret_bucket']}:{stats['vol_bucket']}"
        f"|n:{stats['n']}|fallback:{int(stats['fallback'])}|"
    )
    n_eff = stats["n"]
    conf = min(n_eff / float(RULE_PARAMS["conf_n_full"]), float(RULE_PARAMS["conf_cap"]))
    if stats["fallback"]:
        conf *= 0.5  # 全样本基线=证据弱，置信折半（v0 口径，文档化）
    a_ts = asof_ts or now_utc()
    if a_ts.tzinfo is None:
        raise ValueError("asof_ts 须带时区（RULE-SCHEMA-TZ）")
    return emit_judgment(
        "next_day_forecast",
        JudgmentDraft(
            module_id=MODULE_ID,
            model_version=MODEL_VERSION,
            subject=SUBJECT,
            payload=payload,
            confidence=round(conf, 4),
            horizon=None,  # 表默认 next_day
            inputs_ref=inputs_ref,
            run_id=f"next-day:{day}",
        ),
        asof_ts=a_ts,
        input_cutoff_ts=a_ts,  # 日线收盘口径数据齐后才触发（事件真源保证）
        synthetic=synthetic,
    )


def maybe_emit_next_day_forecast(task_id: Any = None, success: bool = True,
                                 **_kwargs) -> dict[str, Any]:
    """次日概率的**唯一自动产出者**：daily_kline SUCCESS=自然唤醒（T 日数据齐）。

    宪法 §9.3 合规（零新机制，maybe_settle_judgment_ledger 同款骨架）：不建
    cron/Timer/sleep 循环。业务日 D=行情最新入库日（resolve_pf_alloc_trade_date，
    禁墙钟猜日）——非交易日/行情停更唤醒时 D 不变且已发射→零副作用跳过（非交易
    日触发抑制是数据驱动的结构性质，非日历硬编码）。发射失败 WARN 出声不反噬唤醒链。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in ("daily_kline", "kline_daily", "kline_index")):
        return {"action": "skipped_wake_point"}
    day = ""
    try:
        from zephyr.strategy_pipeline.pipeline_events import resolve_pf_alloc_trade_date

        day = resolve_pf_alloc_trade_date()  # 共用业务日真源（禁墙钟猜日）
        rows = _reader_execute(_ALREADY_EMITTED_SQL.format(module_id=MODULE_ID, day=day))
        if rows and int(rows[0][0]) > 0:
            return {"action": "already_emitted", "trade_date": day}
        result = emit_for_trade_date(day)
        if not result.committed:
            return {"action": "emit_not_committed", "disposition": result.disposition,
                    "trade_date": day, "judgment_id": result.judgment_id}
        return {"action": "emitted", "trade_date": day, "judgment_id": result.judgment_id}
    except ValueError as exc:
        # 必需数据缺席=fail-closed 漏判（出声留痕，不编造）——T 日线未齐时下个唤醒点自愈
        return {"action": "data_insufficient", "trade_date": day, "reason": str(exc)[:200]}
    except Exception as exc:  # noqa: BLE001——钩子永不反噬调度器，失败必须出声
        return {"action": "error", "trade_date": day,
                "error": f"{type(exc).__name__}: {exc}"[:200]}


class NextDayForecaster:
    """发射 facade（scaffold 契约）：模块级组合入口的对象化包装（无独立状态）。"""

    module_id: str = MODULE_ID
    model_version: str = MODEL_VERSION
    subject: str = SUBJECT

    def emit_once(self) -> dict[str, Any]:
        """跑一次唤醒点等价的次日判定（手工补跑/冒烟入口）。"""
        return maybe_emit_next_day_forecast(task_id="manual_facade", success=True)

    def forecast(self, rows: Sequence[tuple]) -> dict[str, Any]:
        """判定主体直通（条件统计纯函数——测试与人工核查用）。"""
        feat = build_day_features(rows)
        return cond_prob_from_history(rows, feat)
