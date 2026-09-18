# [BLUEPRINT] MOD-PLAN-028 | docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表1/§六任务1
# [MODULE] zephyr.plan_engine.intraday_l1_tracker
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.judgment_ledger(一行发射); zephyr.infrastructure.database_service(reader);
#   zephyr.shared.utils.time_utils(now_utc——SCHEMA-TZ 时钟真源)
# [CONSUMERS] zephyr.strategy_pipeline.pipeline_events(事件挂点 maybe_track_intraday_state——kline 60min 任务
#   SUCCESS 唤醒); judgment_intraday_market_state 台账; Phase 5 meta-回测逐层归因（数据源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定/结算分离（本件只发射判定，结算归 judgment_settler——标准 §一.2）; 触发=事件驱动
#   （60min bars 入库 task_completed 唤醒，禁 cron/Timer/sleep-loop——宪法 §9.3）; 幂等=bar_key 查重
#   （judgment_intraday_market_state 按 module_id+inputs_ref LIKE bar 键，同 bar 重放/调度器 5 分钟
#   重复唤醒零副作用）; PIT 锚 input_cutoff≤asof（数据截止时刻取特征 max ts，机械校验由发射器兜底）;
#   数据真源以库内实际为准：盘中指数代理=510300（沪深300ETF 60min，kline_60min 仅个股无指数、
#   指数分钟源=P1 登记 pending_minute_source——基差如实标注不伪造）; 进攻证据代理=market_breadth_snapshot.
#   limit_up（limit_up_pool 表空 0 行，板块归属拆解 pending——proxy 标注落 payload）; 特征缺席=降级
#   （degraded 标注+confidence 扣减，禁跳过式静默也禁编造值）; 非交易数据不判（无新 bar=零发射，
#   周末/停牌唤醒天然抑制）; 概率分布 softmax 结构性归一（和恒 1）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(业务日/行情不可解析——钩子侧捕获出声不反噬); 发射失败不抛（EmitResult.
#   committed=False 留痕，judgment_ledger 契约）; CH 只读异常上抛（数据断供必须出声）
# [TESTS] tests/plan_engine/test_intraday_l1_tracker.py
# [A_module] module_id=MOD-PLAN-028 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""intraday_l1_tracker — 盘中 L1 大盘状态跟踪件（判定台账标准 v0.1 §六任务 1）。

交易时段每当一根 60min bar 落库（kline_etf_60min_incremental / kline_60min_incremental
任务 SUCCESS=自然唤醒，宪法 §9.3 合规零新机制），对当前大盘拍一张快照：判五态
（低迷/防御/震荡/进攻/亢奋）+ 概率分布 + 尾盘方向概率，经 judgment_ledger.emit_judgment
一行发射到 c1_market.judgment_intraday_market_state。台账价值在积累——v0=规则打分
基线（参数全部显式声明于 RULE_PARAMS），后续可整体换逻辑回归/梯度提升而不动表契约。

v0 判定规则（全部参数化，RULE_PARAMS 单点声明）：
  1. 特征装配 build_features（缺失降级并标注，禁编造）：
     - volume_ratio  量比 = 当日已收 bar 累计量 / 近 20 日同 bar 序号累计量均值
       （历史不足 VOL_LOOKBACK 用全日均量折算，ratio_note 标注口径）。
     - breadth_ratio 涨跌家数比 = advancing/(advancing+declining)，源=market_breadth_snapshot
       当日最新快照；当日无快照 → 降级用 kline_index 前一交易日 advance/decline
       （degraded_breadth=True，收盘口径隔日数据如实标注）。
     - attack_sector_count 进攻拉板数 = market_breadth_snapshot.limit_up（全市场涨停计数
       代理——limit_up_pool 表空，券商/半导体板块拆解 pending proxy_note 标注；
       attack_sectors 恒 []，板块归属接电后补）。
     - gap_pct 缺口 = 当日首根 bar open / 前一交易日末根 bar close - 1（ETF 代理口径）。
     - ret_intraday 盘中涨跌 = 最新 bar close / 前一交易日末根 bar close - 1。
     - overnight_ref 隔夜参照 = A50 期货（CHA50CFD）最新行 close 对前一行 close
       （昨夜盘口径）；无数据 omit 不编造。
  2. 五态打分：bull_score = Σ w_i·x_i（各分量归一 [0,1]），五态锚点
     [低迷,防御,震荡,进攻,亢奋] 均布于 [0.05,0.95]，logits=-(anchor-bull)²/(2σ²)
     → softmax 结构性归一（和恒 1）；state_label=argmax。
  3. 尾盘方向 tail_dir_prob_down = clip(0.5 - k·(bull_score-0.5), 0.1, 0.9)
     （bull 越强尾盘下跌概率越低）；15:00 收盘 bar rest_of_day=None（无剩余时段，
     诚实留空而非给无意义概率）。
  4. expected amp_range_pct = 近 20 日日内振幅（high/low-1）均值 × [0.5,1.5] 倍带。
  5. confidence = 特征完备度（6 项特征每缺一项扣 CONF_STEP，下限 CONF_FLOOR）。

幂等与判定点：bar_key="YYYY-MM-DDTHH:MM"（bar 收盘时刻，上海时区）；同 key 已有
台账行（module_id+inputs_ref LIKE 匹配）→ 零发射跳过——调度器每 5 分钟唤醒一次
而 60min bar 每小时才一根，重放/重复唤醒天然抑制。判定时刻 asof=now(UTC)，
input_cutoff=max(bar 收盘, breadth 快照 ts, A50 ingest)（UTC，≤asof 恒成立）。

不做什么：不写结算列（无通道）；不做分钟级判定（指数分钟源 pending，不伪造）；
不做场景/预案（daily_plan 归作战室任务 3 场景引擎）。

依据: docs/_working/trading_vision/2026-09-16-judgment-ledger-standard.md §三表1/§六
SSoT: depgraph node 14570138（MOD-PLAN-028）
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Final, Sequence
from zoneinfo import ZoneInfo

from zephyr.plan_engine.judgment_ledger import (
    JUDGMENT_TABLES,
    EmitResult,
    JudgmentDraft,
    emit_judgment,
)
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "Judgment5State",
    "MODULE_ID",
    "MODEL_VERSION",
    "RULE_PARAMS",
    "SUBJECT",
    "build_features",
    "decide_five_state",
    "format_bar_key",
    "latest_unemitted_bar",
    "maybe_track_intraday_state",
    "score_features",
]

MODULE_ID: Final = "MOD-PLAN-028"
MODEL_VERSION: Final = "v0-rule"
SUBJECT: Final = "index:000300.SH"

# ── 数据源口径（库内实际，代理关系如实标注）──
_ETF_PROXY_SYMBOL: Final = "510300"  # 沪深300ETF 60min=指数盘中代理（kline_60min 仅个股）
_ETF_TABLE: Final = "c1_market.kline_etf_60min"
_BREADTH_TABLE: Final = "c1_market.market_breadth_snapshot"
_INDEX_TABLE: Final = "c1_market.kline_index"  # 昨日涨跌家数降级源 + 业务日参考
_A50_TABLE: Final = "c1_market.a50_futures_daily"
_SHANGHAI: Final = ZoneInfo("Asia/Shanghai")

# ── v0 规则参数（单点声明，文档=本模块 docstring §v0；调参=改这里+跑测试）──
RULE_PARAMS: Final[dict[str, float]] = {
    "w_volume": 0.25,        # 量比权重（放量=多头进攻证据之一）
    "w_breadth": 0.35,       # 涨跌家数比权重（市场宽度=最主要证据）
    "w_attack": 0.15,        # 拉板数权重（赚钱效应）
    "w_ret": 0.25,           # 盘中涨跌权重
    "ret_norm_span": 0.02,   # 盘中涨跌归一跨度（±2% 映射到 [0,1]，超出截断）
    "attack_cap": 100.0,     # 拉板数归一上限（家）
    "state_sigma": 0.12,     # 五态锚点 softmax 温度（越小分布越尖）
    "tail_k": 0.6,           # 尾盘方向斜率
    "tail_clip": 0.9,        # 尾盘方向截断（0.1~0.9——v0 不给极端自信）
    "vol_lookback": 20,      # 量比历史窗口（交易日）
    "amp_band_low": 0.5,     # 预期振幅带下倍数
    "amp_band_high": 1.5,    # 预期振幅带上倍数
    "conf_step": 0.15,       # 每缺一项特征的置信扣减
    "conf_floor": 0.4,       # 置信下限
}

# 五态锚点（bull_score 语义轴上的均布位置：低迷≈0.05 → 亢奋≈0.95）
_STATE_ANCHORS: Final[tuple[str, ...]] = ("低迷", "防御", "震荡", "进攻", "亢奋")
_ANCHOR_LO: Final = 0.05
_ANCHOR_HI: Final = 0.95

# 收盘 bar 判定点标记（上海时区 bar_key 后缀=该时刻者视为全天终判，rest_of_day=None）
_SESSION_LAST_BAR: Final = "15:00"


# ── 只读通道（模块级函数=测试注入点；实现单点收口于共享结算器库件——本件只 import
#    不复制（CLONE-GUARD AGG-40410b77 治本），生产走 DatabaseService reader，§9.1）──

from zephyr.plan_engine.judgment_settler import _reader_execute  # noqa: PLC2701


# SQL 集中为模块常量（禁裸 SQL 散落；参数受控拼接——symbol 白名单字面量）
_BARS_SQL: Final = (
    "SELECT trade_date, trade_time, open, close, high, low, volume "
    "FROM {table} WHERE symbol = '{symbol}' AND trade_date >= {since} "
    "ORDER BY trade_date, trade_time"
)
_BREADTH_TODAY_SQL: Final = (
    "SELECT ts, advancing, declining, limit_up, limit_down FROM {table} "
    "WHERE trade_date = '{day}' ORDER BY ts DESC LIMIT 1"
)
_INDEX_PREV_SQL: Final = (
    "SELECT trade_date, advance_count, decline_count, close FROM {table} "
    "WHERE symbol = '000300' AND quality_flag = 1 AND trade_date < '{day}' "
    "ORDER BY trade_date DESC LIMIT 1"
)
_A50_LAST2_SQL: Final = (
    "SELECT trade_date, close FROM {table} WHERE symbol = 'CHA50CFD' "
    "ORDER BY trade_date DESC LIMIT 2"
)
# 幂等查重：同 module_id + 同 bar_key（inputs_ref 结构化指纹 LIKE 匹配）。
# 模式不带前导 '|'——bar_key 是 inputs_ref 首键（首键前无分隔符，'%|key|%' 永远
# miss=幂等失效三连发事故修复 2026-09-17，同 next_day_forecaster）；尾 '|' 防前缀误配。
_SQL_ALREADY_EMITTED = (
    "SELECT count() "
    "FROM {table} "
    "WHERE module_id = '{module_id}' AND inputs_ref LIKE '%bar_key:{bar_key}|%'"
)


def _to_utc(dt: datetime) -> datetime:
    """clickhouse 返回的带时区/naive datetime → UTC aware（naive 视为上海时区）。"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_SHANGHAI)
    return dt.astimezone(timezone.utc)


# ── 特征装配（纯函数：数据以行元组注入，可单测）──


@dataclass(frozen=True)
class Judgment5State:
    """一次盘中五态判定的完整产出（payload 组装前形态）。"""

    state_label: str
    state_probs: dict[str, float]
    bull_score: float
    tail_dir_prob_down: float | None  # None=收盘 bar（无剩余时段）
    confidence: float
    amp_range_pct: list[float]
    evidence: dict[str, Any] = field(default_factory=dict)
    cutoff_utc: datetime | None = None  # input_cutoff（特征最大数据时刻）


def _norm_ratio(x: float) -> float:
    """量比归一 [0,1]：x/(1+x)（x=1 平量→0.5，x→∞ 有界饱和 1，单调）。"""
    x = max(x, 0.0)
    return x / (1.0 + x)


def _norm_ret(ret: float, span: float) -> float:
    """涨跌归一 [0,1]：0→0.5，±span→0/1，超出截断。"""
    return max(0.0, min(1.0, 0.5 + ret / (2.0 * span)))


def _last_bar_close_per_day(bars: Sequence[tuple]) -> dict[str, datetime]:
    """每日末根 bar 的收盘时刻（gap/ret 的基准锚）。输入按 (trade_date, trade_time) 有序。"""
    out: dict[str, datetime] = {}
    for row in bars:
        out[str(row[0])] = row[1]  # 后写覆盖=当日最晚 trade_time
    return out


def build_features(
    bars_today: Sequence[tuple],
    bars_hist: Sequence[tuple],
    breadth: dict[str, Any] | None,
    index_prev: tuple | None,
    a50_closes: Sequence[float],
    params: dict[str, float] = RULE_PARAMS,
) -> tuple[dict[str, Any], list[str]]:
    """装配判定特征。

    Args:
        bars_today: 当日 60min bars [(trade_date, trade_time, open, close, high, low, volume)]，
            按 (trade_date, trade_time) 有序（SQL ORDER BY 保证）。
        bars_hist: 近 N 日 bars（同结构，不含当日，同样有序）。
        breadth: 当日 breadth 快照 {ts, advancing, declining, limit_up, limit_down}
            或 None（降级 index_prev 收盘口径）。
        index_prev: kline_index 前一交易日 (trade_date, advance_count, decline_count, close)
            或 None。
        a50_closes: A50 收盘序列（最近在前，≥2 个才有隔夜参照）。
        params: RULE_PARAMS（可注入测试口径）。

    Returns:
        (features dict, missing 特征名清单)。缺失降级：值缺席=键缺席（禁编造 0 值——
        0 是合法测量值，缺席是另一回事，混用会污染打分）。
    """
    f: dict[str, Any] = {}
    missing: list[str] = []
    lookback = int(params["vol_lookback"])

    if not bars_today:
        return f, ["bars_today"]  # 无 bar 不判定（调用方直接跳过）

    # 基准锚：前一交易日末根 bar close
    prev_closes = _last_bar_close_per_day(bars_hist)
    if not prev_closes:
        return dict(f), ["bars_hist"]
    prev_last_ts = max(prev_closes.values())
    prev_last_close = None
    for row in reversed(bars_hist):
        if row[1] == prev_last_ts:
            prev_last_close = float(row[3])
            break
    if prev_last_close is None or prev_last_close <= 0:
        return dict(f), ["bars_hist"]

    # gap_pct / ret_intraday（ETF 代理口径）
    first_open = float(bars_today[0][2])
    last_close = float(bars_today[-1][3])
    f["gap_pct"] = first_open / prev_last_close - 1.0
    f["ret_intraday"] = last_close / prev_last_close - 1.0

    # volume_ratio：当日已收 bar 累计 / 近 lookback 日同 bar 序号累计均值
    # （同序号=该日第 n_today 根 bar 收盘时的累计量——同一日内时钟对齐，无未来函数）
    n_today = len(bars_today)
    vol_today = sum(float(r[6]) for r in bars_today)
    by_day: dict[str, list[tuple]] = {}
    for row in bars_hist:
        by_day.setdefault(str(row[0]), []).append(row)
    recent_days = sorted(by_day)[-lookback:]
    day_vols = {d: sum(float(r[6]) for r in by_day[d]) for d in recent_days}
    same_idx_sums = [
        sum(float(r[6]) for r in by_day[d][:n_today])
        for d in recent_days if len(by_day[d]) >= n_today
    ]
    if same_idx_sums and vol_today > 0 and sum(same_idx_sums) > 0:
        f["volume_ratio"] = vol_today / (sum(same_idx_sums) / len(same_idx_sums))
        f["ratio_note"] = "same_index"
    elif vol_today > 0 and day_vols:
        full_day = [v for v in day_vols.values() if v > 0]
        if full_day:
            f["volume_ratio"] = vol_today / (sum(full_day) / len(full_day))
            f["ratio_note"] = "full_day_fallback"
    if "volume_ratio" not in f:
        missing.append("volume_ratio")

    # breadth_ratio / attack：当日盘中快照优先，降级昨日收盘口径
    if breadth is not None:
        adv = float(breadth.get("advancing") or 0)
        dec = float(breadth.get("declining") or 0)
        if adv + dec > 0:
            f["breadth_ratio"] = adv / (adv + dec)
        f["attack_sector_count"] = float(breadth.get("limit_up") or 0)
        f["breadth_source"] = "market_breadth_snapshot"
        f["breadth_ts"] = str(breadth.get("ts") or "")
    else:
        if index_prev is not None:
            adv_p = float(index_prev[1] or 0)
            dec_p = float(index_prev[2] or 0)
            if adv_p + dec_p > 0:
                f["breadth_ratio"] = adv_p / (adv_p + dec_p)
                f["breadth_source"] = "kline_index_prev_day"
                f["degraded_breadth"] = True
            else:
                missing.append("breadth_ratio")
        else:
            missing.append("breadth_ratio")
        missing.append("attack_sector_count")

    # overnight_ref：A50 昨夜收盘变动（最近在前）
    if len(a50_closes) >= 2 and a50_closes[1]:
        f["overnight_ref"] = {"a50_ret": a50_closes[0] / a50_closes[1] - 1.0}

    # 近 N 日日内振幅均值（amp_range_pct 基）
    amps = [
        float(r[4]) / float(r[5]) - 1.0
        for r in bars_hist if float(r[5]) > 0
    ]
    f["amp_base_pct"] = (sum(amps) / len(amps) * 100.0) if amps else None
    if f["amp_base_pct"] is None:
        missing.append("amp_range_pct")

    return f, missing


def score_features(
    features: dict[str, Any],
    params: dict[str, float] = RULE_PARAMS,
) -> Judgment5State:
    """五态打分（纯函数）：bull_score → 锚点 softmax → 五态分布 + 尾盘方向。

    特征缺席=权重归一重分配（降级打分——kline_index 涨跌家数 2026-07 后断供等
    上游缺口的既定处置；缺失项进 evidence 由 confidence 扣减反映，不拒绝判定）。

    Raises:
        ValueError: 盘中涨跌缺席（无价格证据，无法判定——唯一硬性必需特征）。
    """
    if "ret_intraday" not in features:
        raise ValueError("必需特征缺席，拒绝打分（无价格证据禁判定）: ret_intraday")
    span = float(params["ret_norm_span"])
    parts: list[tuple[float, float]] = []  # (weight, normalized)
    if "volume_ratio" in features:
        parts.append((float(params["w_volume"]), _norm_ratio(float(features["volume_ratio"]))))
    if "breadth_ratio" in features:
        parts.append((float(params["w_breadth"]), max(0.0, min(1.0, float(features["breadth_ratio"])))))
    if "attack_sector_count" in features:
        parts.append((float(params["w_attack"]),
                      max(0.0, min(1.0, float(features["attack_sector_count"]) / float(params["attack_cap"])))))
    parts.append((float(params["w_ret"]), _norm_ret(float(features["ret_intraday"]), span)))
    w_sum = sum(w for w, _ in parts)
    bull = sum(w * x for w, x in parts) / w_sum if w_sum > 0 else 0.5

    # 锚点 softmax（结构性归一：Σprobs=1 恒成立）
    sigma = float(params["state_sigma"])
    anchors = [_ANCHOR_LO + i * (_ANCHOR_HI - _ANCHOR_LO) / 4.0 for i in range(5)]
    logits = [-((a - bull) ** 2) / (2.0 * sigma * sigma) for a in anchors]
    m = max(logits)
    exps = [math.exp(l - m) for l in logits]
    z = sum(exps)
    probs = {s: e / z for s, e in zip(_STATE_ANCHORS, exps)}
    label = max(probs, key=lambda k: probs[k])  # type: ignore[arg-type]
    # round(6) 后归一修补（余差并入 argmax——保证落库分布和=1，过发射器 1e-6 容差）
    rounded = {s: round(probs[s], 6) for s in _STATE_ANCHORS}
    remainder = round(1.0 - sum(rounded.values()), 9)
    rounded[label] = round(rounded[label] + remainder, 6)

    # 尾盘方向（None=收盘 bar——由调用方按 bar_key 决定，此处恒给值）
    k_t = float(params["tail_k"])
    clip = float(params["tail_clip"])
    tail = max(1.0 - clip, min(clip, 0.5 - k_t * (bull - 0.5)))

    # 置信=特征完备度（5 项可打分特征：volume/breadth/attack/ret/overnight）
    n_have = sum(1 for k in ("volume_ratio", "breadth_ratio", "attack_sector_count",
                             "ret_intraday", "overnight_ref") if k in features)
    conf = max(float(params["conf_floor"]), min(1.0, n_have * float(params["conf_step"]) + 0.25))

    lo = float(params["amp_band_low"])
    hi = float(params["amp_band_high"])
    base = float(features.get("amp_base_pct") or 0.0)
    amp = [round(base * lo, 3), round(base * hi, 3)]

    return Judgment5State(
        state_label=label,
        state_probs=rounded,
        bull_score=round(bull, 6),
        tail_dir_prob_down=round(tail, 6),
        confidence=round(conf, 4),
        amp_range_pct=amp,
        evidence={
            "volume_ratio": features.get("volume_ratio"),
            "breadth_ratio": features.get("breadth_ratio"),
            "attack_sector_count": features.get("attack_sector_count"),
            "attack_sectors": [],  # 板块拆解 pending（limit_up_pool 空——proxy 标注）
            "gap_pct": features.get("gap_pct"),
            "ret_intraday": features.get("ret_intraday"),
            "overnight_ref": features.get("overnight_ref"),
            "breadth_source": features.get("breadth_source"),
            "degraded_breadth": features.get("degraded_breadth", False),
            "proxy_notes": {
                "index_intraday": "pending_minute_source(etf_510300_proxy)",
                "attack_sectors": "pending_sector_pool(limit_up_pool_empty)",
            },
        },
    )


def format_bar_key(trade_time: datetime) -> str:
    """bar 收盘时刻 → 幂等键（上海时区 ISO 分钟精度）。"""
    if trade_time.tzinfo is None:
        trade_time = trade_time.replace(tzinfo=_SHANGHAI)
    sh = trade_time.astimezone(_SHANGHAI)
    return f"{sh.year:04d}-{sh.month:02d}-{sh.day:02d}T{sh.hour:02d}:{sh.minute:02d}"


def decide_five_state(
    bars_today: Sequence[tuple],
    bars_hist: Sequence[tuple],
    breadth: dict[str, Any] | None,
    index_prev: tuple | None,
    a50_closes: Sequence[float],
    is_closing_bar: bool,
    params: dict[str, float] = RULE_PARAMS,
) -> tuple[dict[str, Any], float]:
    """判定组装（装配+打分+payload/inputs_ref 拼装）。

    Returns:
        (payload dict, confidence float)——inputs_ref 由调用方按 bar 组装；
        closing bar 的 rest_of_day=None（诚实留空）。

    Raises:
        ValueError: 必需特征缺席/无 bar（调用方跳过该判定点）。
    """
    features, missing = build_features(bars_today, bars_hist, breadth, index_prev,
                                       a50_closes, params)
    if not features or "ret_intraday" not in features:
        raise ValueError(f"特征装配不完整，拒绝判定（missing={missing}）")
    j = score_features(features, params)
    rest_of_day: dict[str, Any] | None = None
    if not is_closing_bar:
        rest_of_day = {
            "tail_dir_prob_down": j.tail_dir_prob_down,
            "amp_range_pct": j.amp_range_pct,
        }
    payload = {
        "state_label": j.state_label,
        "state_probs": j.state_probs,
        "evidence": {**j.evidence, "bull_score": j.bull_score, "missing_features": missing},
        "rest_of_day": rest_of_day,
    }
    return payload, _confidence_of(payload)


# ── 发射组合（读库→查重→发射；挂点薄壳=maybe_track_intraday_state）──


def latest_unemitted_bar(
    *, reader=None, today: str | None = None,
) -> tuple[str, list[tuple], list[tuple]] | None:
    """找出当日最新一根**未发射过**的 bar（幂等闸）。

    Returns:
        (bar_key, bars_today, bars_hist) 或 None（无新 bar/收盘 bar 已发射/当日无数据）。
        收盘 bar（15:00）也判定（全天终判，rest_of_day=None）——已发射同样跳过。
    """
    rd = reader or _reader_execute
    day = today or now_utc().astimezone(_SHANGHAI).strftime("%Y-%m-%d")
    since = (datetime.strptime(day, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d")
    bars = rd(_BARS_SQL.format(table=_ETF_TABLE, symbol=_ETF_PROXY_SYMBOL, since=f"'{since}'"))
    if not bars:
        return None
    by_day: dict[str, list[tuple]] = {}
    for row in bars:
        by_day.setdefault(str(row[0]), []).append(row)
    today_bars = by_day.get(day)
    if not today_bars:
        return None
    # 当日最新 bar（未发射的第一优先：从最新往旧找首个未发射的）
    for bar in reversed(today_bars):
        bar_key = format_bar_key(bar[1])
        rows = rd(_SQL_ALREADY_EMITTED.format(table=JUDGMENT_TABLES["intraday_market_state"],
                                      module_id=MODULE_ID, bar_key=bar_key))
        if rows and int(rows[0][0]) > 0:
            continue  # 该 bar 已发射
        hist: list[tuple] = [
            r for r in bars if str(r[0]) < day
        ]
        return bar_key, today_bars, hist
    return None


def _load_breadth(day: str, *, reader=None) -> dict[str, Any] | None:
    rd = reader or _reader_execute
    rows = rd(_BREADTH_TODAY_SQL.format(table=_BREADTH_TABLE, day=day))
    if not rows:
        return None
    return {"ts": rows[0][0], "advancing": rows[0][1], "declining": rows[0][2],
            "limit_up": rows[0][3], "limit_down": rows[0][4]}


def _load_index_prev(day: str, *, reader=None) -> tuple | None:
    rd = reader or _reader_execute
    rows = rd(_INDEX_PREV_SQL.format(table=_INDEX_TABLE, day=day))
    return rows[0] if rows else None


def _load_a50(*, reader=None) -> list[float]:
    rd = reader or _reader_execute
    return [float(r[1]) for r in rd(_A50_LAST2_SQL.format(table=_A50_TABLE))]


def emit_for_bar(
    bar_key: str,
    bars_today: Sequence[tuple],
    bars_hist: Sequence[tuple],
    *,
    reader=None,
    synthetic: bool = False,
    asof_ts: datetime | None = None,
) -> EmitResult:
    """单 bar 判定发射（组合入口：装配证据→判定→emit_judgment 一行发射）。

    inputs_ref=结构化指纹：bar_key（幂等键）+ bar 数据 hash + 证据源时刻 + 缺席清单；
    confidence=五态 argmax 概率 × 特征完备度折减（decide_five_state 组装）。
    """
    rd = reader or _reader_execute
    day = bar_key[:10]
    breadth = _load_breadth(day, reader=rd)
    index_prev = _load_index_prev(day, reader=rd)
    a50 = _load_a50(reader=rd)
    bar_last_close_utc = _to_utc(bars_today[-1][1])
    cutoff = bar_last_close_utc
    if breadth is not None and isinstance(breadth.get("ts"), datetime):
        cutoff = max(cutoff, _to_utc(breadth["ts"]))
    is_closing = bar_key.endswith(_SESSION_LAST_BAR)
    payload, confidence = decide_five_state(
        bars_today, bars_hist, breadth, index_prev, a50,
        is_closing_bar=is_closing,
    )
    fp_raw = "|".join(f"{r[0]}:{r[1]}:{r[3]}:{r[6]}" for r in bars_today)
    fp = hashlib.sha256(fp_raw.encode("utf-8")).hexdigest()[:16]
    missing = payload.get("evidence", {}).get("missing_features") or []
    inputs_ref = (
        f"bar_key:{bar_key}|bar_hash:{fp}"
        f"|proxy:etf_510300|breadth_ts:{breadth.get('ts', '') if breadth else ''}"
        f"|missing:{','.join(missing) if missing else 'none'}|"
    )
    a_ts = asof_ts or now_utc()
    if a_ts.tzinfo is None:
        raise ValueError("asof_ts 须带时区（RULE-SCHEMA-TZ）")
    if cutoff > a_ts:
        cutoff = a_ts  # PIT 机械兜底（bar 时间戳漂移防御；正常路径恒 ≤）
    return emit_judgment(
        "intraday_market_state",
        JudgmentDraft(
            module_id=MODULE_ID,
            model_version=MODEL_VERSION,
            subject=SUBJECT,
            payload=payload,
            confidence=confidence,
            horizon="intraday_rest",
            inputs_ref=inputs_ref,
            run_id=f"intraday-track:{bar_key}",
        ),
        asof_ts=a_ts,
        input_cutoff_ts=cutoff,
        synthetic=synthetic,
    )


def _confidence_of(payload: dict[str, Any]) -> float:
    """置信=五态 argmax 概率与完备度的合成（evidence.missing_features 驱动扣减）。"""
    base = float(payload["state_probs"].get(payload["state_label"], 0.0))
    n_missing = len(payload.get("evidence", {}).get("missing_features") or [])
    return round(max(0.2, base * (1.0 - 0.1 * n_missing)), 4)


def maybe_track_intraday_state(task_id: Any = None, success: bool = True,
                               **_kwargs) -> dict[str, Any]:
    """盘中 L1 跟踪的**唯一自动产出者**：60min bars 入库任务 SUCCESS=自然唤醒。

    宪法 §9.3 合规（零新机制，maybe_settle_judgment_ledger 同款骨架）：不建
    cron/Timer/sleep 循环，节拍由调度器 task_completed 唤醒给（intraday_minute
    时段每 5 分钟唤醒，60min bar 每小时一根——bar_key 查重闸使重复唤醒零副作用）。
    永不抛：发射/读库失败 WARN 出声不反噬唤醒链；周末/停牌=无新 bar 零发射
    （非交易日触发抑制是数据驱动的结构性质，非日历硬编码）。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in ("kline_60min", "kline_etf_60min")):
        return {"action": "skipped_wake_point"}
    try:
        found = latest_unemitted_bar()
        if found is None:
            return {"action": "no_new_bar"}
        bar_key, bars_today, bars_hist = found
        result = emit_for_bar(bar_key, bars_today, bars_hist)
        if not result.committed:
            return {"action": "emit_not_committed", "disposition": result.disposition,
                    "bar_key": bar_key, "judgment_id": result.judgment_id}
        return {"action": "emitted", "bar_key": bar_key,
                "judgment_id": result.judgment_id}
    except Exception as exc:  # noqa: BLE001——钩子永不反噬调度器，失败必须出声
        return {"action": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}


if __name__ == "__main__":  # pragma: no cover — 手工补跑逃生口（非自动链路）
    print(maybe_track_intraday_state(task_id="manual_cli", success=True))


class IntradayL1Tracker:
    """发射 facade（scaffold 契约）：模块级组合入口的对象化包装（无独立状态）。"""

    module_id: str = MODULE_ID
    model_version: str = MODEL_VERSION
    subject: str = SUBJECT

    def track_once(self) -> dict[str, Any]:
        """跑一次唤醒点等价的盘中跟踪（手工补跑/冒烟入口）。"""
        return maybe_track_intraday_state(task_id="manual_facade", success=True)

    def decide(self, *args: Any, **kwargs: Any) -> tuple[dict[str, Any], float]:
        """判定组装直通（decide_five_state 纯函数——测试与人工核查用）。"""
        return decide_five_state(*args, **kwargs)
