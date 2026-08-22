# [BLUEPRINT] MOD-SIG-059 | 待统筹登记（blueprint 未建，真源=44号备忘录 §9.9）
# [MODULE] zephyr.signal_ashare.option_sentiment
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] c1_market.option_iv_surface（只读）; c1_market.option_kline（只读）; c1_market.option_greeks（只读）; c1_market.calendar_event（只读）
# [CONSUMERS] （MVP 阶段无——候选消费方：MOD-SIG-025 情绪注解维度⑨，经输入契约注入，权重≤0.10；M1 阈值缩放因子消费方）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] m1_threshold_scale ∈ {1.0, 0.8}; pcr_basis ∈ {"volume", "open_interest"}（当前实证恒为 "volume"）; 无数据/查询异常/客户端不可用 MUST 返回 degraded=True 空结果不炸；各字段独立降级互不累及；iv_surface.delta 全 0 实证不可用，禁止以该列选约
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md §9.9
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可用→degraded=True 不抛；trade_date 格式非法→ValueError（调用方契约违例，fail-closed）
# [TESTS] tests/signal_ashare/test_option_sentiment.py
# [A_module] module_id=MOD-SIG-059 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
MOD-SIG-059 — 期权情绪三件套（44号备忘录 §9.9，M1-⑨，华泰 2026-03 机构范式）

A 股单边做多市场衍生品"少而精"只取 PCR+IV 两指标最有效，加 Skew 尾部偏度作机构行为
佐证，三件套合成"情绪注解维度⑨"（候选消费方 MOD-SIG-025 综合分，权重 ≤0.10 纪律，
本模块只出分数与注解文本，权重由下游控制）。主标的=300ETF 期权（510300.SH，华泰口径），
50ETF/500ETF/科创同算法可经 config.underlying 扩展。

【数据实证口径（2026-08-22 直查 c1_market，可信）】
- option_iv_surface 27,881 行（2026-01-29 起）：iv/strike/expiry/option_type(call/put/''
  空串脏行)/delta/gamma/theta/vega；510300.SH 3,667 行 127 交易日；**delta 列全 0
  （DEFAULT 未回填，选约不可用）**；data_source 08-14 切换（miniqmt 每日 4 到期月 →
  akshare_sina 每日仅最近月）→ 本模块统一限定"最近月（当日 min expiry）"跨源一致口径。
- option_kline 3,027 行（2026-07-30 起）：OHLC+volume+amount，**无 open_interest 列**；
  symbol 体系与 iv_surface 不同（100xxxxx），经 iv_surface DISTINCT symbol 映射
  (underlying, option_type)，成交量加权覆盖率实证 100%。
- option_greeks 2,187 行（2026-08-03 起，510300/510050）：delta 有效（25Δ 选约唯一
  可用源），**option_type 空串 → 由 delta 符号推断（>0=call，<0=put）**；无 IV 列，
  经 (trade_date, symbol) JOIN iv_surface 取 IV（命中率实证 25/25）。
- **无任何表含 open_interest 持仓列 → F1 PCR 实证降级为成交量口径
  （pcr_basis="volume" 留痕）**；后续若 OI 列回填，同函数自动切持仓口径。
- calendar_event 含 index_option_expiry（每月第 4 个周三口径登记在库）。

【三件套算法（44号 §9.9 逐条）】
- F1 成交量 PCR = Σ认沽 volume / Σ认购 volume（当日全合约，经映射过滤主标的）。
  历史分位 <20% = 过度乐观反向风险；>80% = 恐慌过度（底部区）。分位窗 = option_kline
  覆盖期（实证 ~16 交易日），pcr_min_periods=20 守卫，不足 → pcr_percentile=None 降级。
- F2 IV Rank = 当前平值 IV 在可用窗 IV 序列中的分位（标准 250 日窗不足，实证 127
  交易日；min_periods=60 守卫，不足 degraded）。平值选约：iv_surface.delta 不可用 →
  最近月合约中 strike 距当日 strike 中位数最近者（atm_basis="strike_median" 口径
  留痕），call/put 各一取均值。IV 单日跳升 >+3σ → iv_jump_flag（机构避险急增）。
- F3 Skew = IV(25Δ沽) - IV(25Δ购)，归一化 = skew / ATM_IV。25Δ 选约走 greeks.delta
  （|delta∓0.25| 最近者）JOIN iv_surface 取 IV。归一 skew > 历史 90% 分位 = 极端左偏
  （机构尾部保护急增）；greeks 实证仅 ~14 交易日，skew_min_periods=10 守卫，不足 →
  skew_extreme=None 降级。**PCR 低分位（散户乐观）× Skew 极端（机构买保护）背离组合
  = 多空分歧最大警示 divergence_warning**（2026-08-14 科创 ETF 实证形态，44号原文）。
- 期权到期日（calendar_event index_option_expiry 当日）：平值 Gamma 飙升做市商对冲
  放大波动 → m1_threshold_scale=0.8（M1 各加速度/异动信号阈值缩放，防伽马挤压假
  情绪，2026-08-21 实证）；calendar_event 查询失败 → fail-open scale=1.0 留痕。

【合成】composite_score ∈ [-1,1]：正=温和/恐慌过度反向机会，负=过度乐观反向风险/
高波恐慌/尾部保护警示；取可用子分均值，缺项不累及（独立降级）。annotation 为中文
注解文本链（维度⑨直接可消费）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: IV 表面历史窗（option_iv_surface 主标的，iv>0 且 option_type∈{call,put}）
#   fields: trade_date/symbol/strike/expiry/iv/option_type
# - id: I2
#   name: 期权日 K 成交量（option_kline 全窗）
#   fields: trade_date/symbol/volume
# - id: I3
#   name: 合约映射（iv_surface DISTINCT symbol→underlying/option_type）
#   fields: symbol/underlying/option_type
# - id: I4
#   name: Greeks 历史窗（option_greeks 主标的，delta≠0）
#   fields: trade_date/symbol/expiry/delta
# - id: I5
#   name: 期权到期日历（calendar_event index_option_expiry）
#   fields: event_date/event_type
# 层: 特征
# - id: F1
#   name_zh: 成交量 PCR
#   formula: Σvolume(put) / Σvolume(call)  # 当日主标的全合约；call=0 → None 降级
# - id: F2
#   name_zh: 平值 IV 与 IV Rank
#   formula: atm_iv=最近月 strike≈中位数 合约 IV 均值(call/put)；iv_rank=分位(序列≤当前)  # min_periods=60
# - id: F3
#   name_zh: 归一化尾部偏度
#   formula: skew=IV(25Δput)-IV(25Δcall)；skew_norm=skew/atm_iv  # greeks.delta 选约，min_periods=10
# 层: 算法
# - id: A1
#   name_zh: PCR 分位判读
#   desc: pcr_percentile<20%→过度乐观反向风险(-1)；>80%→恐慌过度底部区(+1)；窗不足→None
# - id: A2
#   name_zh: IV Rank 与跳升判读
#   desc: iv_rank>80%→高波恐慌(-1)；<20%→低波温和(+0.5)；ΔIV>+3σ→iv_jump_flag 避险急增
# - id: A3
#   name_zh: Skew 极端与背离警示
#   desc: skew_norm>90%分位→skew_extreme(-1)；pcr_percentile<20%×skew_extreme→divergence_warning
# - id: A4
#   name_zh: 到期日阈值缩放
#   desc: 当日∈index_option_expiry→m1_threshold_scale=0.8，否则 1.0（fail-open 留痕）
# - id: A5
#   name_zh: 维度⑨合成
#   desc: composite_score=可用子分均值∈[-1,1]（权重≤0.10 下游控制）+annotation 文本链
# 层: 输出
# - id: O1
#   name_zh: OptionSentimentResult
#   intro: date/pcr/pcr_basis/pcr_percentile/iv_rank/iv_jump_flag/skew_norm/skew_extreme/divergence_warning/composite_score/annotation/m1_threshold_scale/degraded/notes；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I2,I3 --> F1
# I1 --> F2
# I1,I4 --> F3
# F1 --> A1
# F2 --> A2
# F3 --> A3
# I5 --> A4
# A1,A2,A3 --> A5
# A4,A5 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "OptionSentimentConfig",
    "OptionSentimentResult",
    "compute_option_sentiment",
]

# SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值
SQL_IV_SURFACE_WINDOW: Final = """
SELECT trade_date, symbol, strike, expiry, iv, option_type
FROM c1_market.option_iv_surface
WHERE underlying = %(underlying)s
  AND trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
  AND option_type IN ('call', 'put') AND iv > 0
"""

SQL_SYMBOL_MAP: Final = """
SELECT symbol, underlying, option_type
FROM c1_market.option_iv_surface
WHERE option_type IN ('call', 'put')
GROUP BY symbol, underlying, option_type
"""

SQL_OPTION_VOLUME_WINDOW: Final = """
SELECT trade_date, symbol, volume
FROM c1_market.option_kline
WHERE trade_date <= %(trade_date)s AND trade_date >= %(start_date)s AND volume > 0
"""

SQL_GREEKS_WINDOW: Final = """
SELECT trade_date, symbol, expiry, delta
FROM c1_market.option_greeks
WHERE underlying = %(underlying)s
  AND trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
  AND delta != 0
"""

SQL_EXPIRY_EVENT: Final = """
SELECT count()
FROM c1_market.calendar_event
WHERE event_date = %(trade_date)s AND event_type = 'index_option_expiry'
"""

SQL_LATEST_IV_DATE: Final = """
SELECT max(trade_date)
FROM c1_market.option_iv_surface
WHERE underlying = %(underlying)s AND option_type IN ('call', 'put') AND iv > 0
"""

_PCT_EPS: Final = 1e-12


@dataclass(frozen=True, slots=True)
class OptionSentimentConfig:
    """阈值配置——默认值取自 44号备忘录 §9.9（华泰 2026-03 口径）+ 2026-08-22 数据实证。"""

    underlying: str = "510300.SH"  # 主标的 300ETF 期权（扩展 50ETF=510050.SH/500ETF=510500.SH/科创=588000.SH 同算法）
    lookback_calendar_days: int = 400  # 历史查询自然日窗（覆盖标准 250 交易日 IV Rank 口径）
    iv_rank_min_periods: int = 60  # IV Rank 可用窗最小样本（不足 → iv_rank=None degraded）
    pcr_min_periods: int = 20  # PCR 历史分位最小样本（option_kline 实证仅 ~16 交易日，常态降级）
    skew_min_periods: int = 10  # Skew 归一分位最小样本（option_greeks 实证仅 ~14 交易日）
    pcr_low_percentile: float = 0.20  # PCR 分位 <20% 过度乐观反向风险
    pcr_high_percentile: float = 0.80  # PCR 分位 >80% 恐慌过度（底部区）
    iv_low_percentile: float = 0.20  # IV Rank <20% 低波温和
    iv_high_percentile: float = 0.80  # IV Rank >80% 高波恐慌
    iv_jump_sigma: float = 3.0  # IV 单日跳升 >+3σ 机构避险急增
    skew_extreme_percentile: float = 0.90  # 归一 skew >90% 分位 极端左偏
    delta_25_target: float = 0.25  # 25Δ 选约目标（|delta∓0.25| 最近者）
    expiry_threshold_scale: float = 0.8  # 期权到期日 M1 信号阈值缩放
    max_weight: float = 0.10  # 维度⑨ 下游权重纪律上限（声明性，权重在消费方）


@dataclass(frozen=True, slots=True)
class OptionSentimentResult:
    """期权情绪三件套输出契约（T 日数据计算，情绪注解维度⑨候选输入）。"""

    date: str  # 数据日 YYYY-MM-DD
    pcr: float | None = None  # F1 PCR 原值（口径见 pcr_basis）；无数据/除零 → None
    pcr_basis: str = "volume"  # 实证恒为成交量口径（无 OI 列）；OI 回填后自动切 "open_interest"
    pcr_percentile: float | None = None  # PCR 历史分位 ∈[0,1]；样本不足 → None（降级）
    iv_rank: float | None = None  # F2 IV Rank 分位 ∈[0,1]；可用窗 <60 日 → None（降级）
    iv_jump_flag: bool = False  # IV 单日跳升 >+3σ（机构避险急增）
    skew_norm: float | None = None  # F3 归一化尾部偏度 skew/ATM_IV；选约失败 → None
    skew_extreme: bool | None = None  # 归一 skew >90% 分位极端左偏；样本不足 → None（降级）
    divergence_warning: bool = False  # PCR 低分位×Skew 极端背离 = 多空分歧最大警示
    composite_score: float | None = None  # 维度⑨ 三件套合成 ∈[-1,1]；全部件不可用 → None
    annotation: list[str] = field(default_factory=list)  # 中文注解文本链（维度⑨ 直接消费）
    m1_threshold_scale: float = 1.0  # 期权到期日 0.8，否则 1.0（fail-open）
    degraded: bool = False  # 主数据不可用/查询异常时 True，结果不可用于决策
    notes: list[str] = field(default_factory=list)  # 降级原因等留痕


@dataclass(frozen=True, slots=True)
class _IvRow:
    """option_iv_surface 行解析（iv/strike 已 float 化）。"""

    trade_date: date
    symbol: str
    strike: float
    expiry: date
    iv: float
    option_type: str  # call/put（SQL 已过滤空串）


def _normalize_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式抛 ValueError）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _default_client():
    """延迟加载默认 CH 客户端（不可用时返回 None，由主入口转 degraded）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，期权情绪分析降级", exc_info=True)
        return None


def _parse_iv_row(row: tuple) -> _IvRow:
    return _IvRow(
        trade_date=row[0] if isinstance(row[0], date) else _normalize_date(row[0]),
        symbol=str(row[1]),
        strike=float(row[2]),
        expiry=row[3] if isinstance(row[3], date) else _normalize_date(row[3]),
        iv=float(row[4]),
        option_type=str(row[5]),
    )


def _percentile_rank(sorted_values: list[float], current: float) -> float:
    """当前值在序列中的分位 = count(≤ current) / n（含当前，序列已排序）。"""
    n = len(sorted_values)
    if n == 0:
        return 0.0
    lo, hi = 0, n
    while lo < hi:  # bisect_right 手写（避免 import，语义直观）
        mid = (lo + hi) // 2
        if sorted_values[mid] <= current:
            lo = mid + 1
        else:
            hi = mid
    return lo / n


def _daily_atm_iv(iv_rows: list[_IvRow]) -> dict[date, float]:
    """逐日平值 IV：最近月（当日 min expiry）合约中 strike 距当日 strike 中位数最近者。

    iv_surface.delta 全 0 实证不可用（头注口径），平值近似 = 行权价中位数（ETF 期权
    挂牌行权价围绕标的价格对称，中位 strike 即近平值），call/put 各取一合约 IV 均值。
    """
    by_day: dict[date, list[_IvRow]] = {}
    for r in iv_rows:
        by_day.setdefault(r.trade_date, []).append(r)
    out: dict[date, float] = {}
    for d, rows in by_day.items():
        near_expiry = min(r.expiry for r in rows)
        month_rows = [r for r in rows if r.expiry == near_expiry]
        strikes = sorted({r.strike for r in month_rows})
        if not strikes:
            continue
        mid = strikes[len(strikes) // 2] if len(strikes) % 2 == 1 else (strikes[len(strikes) // 2 - 1] + strikes[len(strikes) // 2]) / 2
        atm_ivs: list[float] = []
        for otype in ("call", "put"):
            legs = [r for r in month_rows if r.option_type == otype]
            if legs:
                atm_ivs.append(min(legs, key=lambda r: abs(r.strike - mid)).iv)
        if atm_ivs:
            out[d] = sum(atm_ivs) / len(atm_ivs)
    return out


def _compute_iv_rank(
    atm_series: dict[date, float],
    current_date: date,
    cfg: OptionSentimentConfig,
) -> tuple[float | None, bool, str | None]:
    """IV Rank 分位 + 单日跳升 >+3σ 标记；样本 <iv_rank_min_periods → (None, False, 降级说明)。"""
    series = sorted((d, v) for d, v in atm_series.items() if d <= current_date)
    if current_date not in atm_series:
        return None, False, f"{current_date.isoformat()} 无平值 IV（非交易日或无近月合约）"
    if len(series) < cfg.iv_rank_min_periods:
        return None, False, f"IV Rank 可用窗 {len(series)} 日 < {cfg.iv_rank_min_periods} 日守卫，降级"
    values = [v for _, v in series]
    current = values[-1]
    rank = _percentile_rank(sorted(values), current)

    jump = False
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))]
    if len(deltas) >= 2:
        mean = sum(deltas) / len(deltas)
        var = sum((x - mean) ** 2 for x in deltas) / (len(deltas) - 1)
        sd = math.sqrt(var)
        if sd > _PCT_EPS and deltas[-1] > cfg.iv_jump_sigma * sd:
            jump = True
    return rank, jump, None


def _compute_pcr(
    volume_rows: list[tuple],
    symbol_map: dict[str, tuple[str, str]],
    current_date: date,
    cfg: OptionSentimentConfig,
) -> tuple[float | None, float | None, list[str]]:
    """成交量 PCR + 历史分位；call 成交量为 0/样本不足 → 对应字段 None 降级。"""
    notes: list[str] = []
    by_day: dict[date, dict[str, float]] = {}
    for row in volume_rows:
        d = row[0] if isinstance(row[0], date) else _normalize_date(row[0])
        mapped = symbol_map.get(str(row[1]))
        if mapped is None or mapped[0] != cfg.underlying:
            continue
        vol = float(row[2])
        if vol <= 0:
            continue
        bucket = by_day.setdefault(d, {"call": 0.0, "put": 0.0})
        bucket[mapped[1]] += vol

    today = by_day.get(current_date)
    if today is None:
        return None, None, [f"{current_date.isoformat()} 主标的无期权成交量（option_kline 未覆盖或非交易日）"]
    if today["call"] <= 0:
        return None, None, ["当日认购成交量为 0，PCR 除零降级"]
    pcr = today["put"] / today["call"]

    history = sorted(
        (d, b["put"] / b["call"]) for d, b in by_day.items() if d <= current_date and b["call"] > 0
    )
    if len(history) < cfg.pcr_min_periods:
        notes.append(f"PCR 分位窗 {len(history)} 日 < {cfg.pcr_min_periods} 日守卫，pcr_percentile 降级")
        return pcr, None, notes
    percentile = _percentile_rank(sorted(v for _, v in history), pcr)
    return pcr, percentile, notes


def _compute_skew(
    greeks_rows: list[tuple],
    iv_rows: list[_IvRow],
    atm_series: dict[date, float],
    current_date: date,
    cfg: OptionSentimentConfig,
) -> tuple[float | None, bool | None, list[str]]:
    """归一化 Skew + 极端左偏判定；25Δ 选约走 greeks.delta（iv_surface.delta 实证不可用）。"""
    notes: list[str] = []
    iv_by_key: dict[tuple[date, str], _IvRow] = {(r.trade_date, r.symbol): r for r in iv_rows}

    def _daily_skew_norm(d: date, day_greeks: list[tuple]) -> float | None:
        atm = atm_series.get(d)
        if atm is None or atm <= _PCT_EPS:
            return None
        near_expiry = min(g[2] if isinstance(g[2], date) else _normalize_date(g[2]) for g in day_greeks)

        def _pick(target: float, want_call: bool) -> _IvRow | None:
            best: tuple[float, _IvRow] | None = None
            for g in day_greeks:
                expiry = g[2] if isinstance(g[2], date) else _normalize_date(g[2])
                if expiry != near_expiry:
                    continue
                delta = float(g[3])
                if want_call and delta <= 0:  # greeks.option_type 空串实证 → delta 符号推断
                    continue
                if not want_call and delta >= 0:
                    continue
                iv_row = iv_by_key.get((d, str(g[1])))
                if iv_row is None:
                    continue
                dist = abs(abs(delta) - target)
                if best is None or dist < best[0]:
                    best = (dist, iv_row)
            return best[1] if best else None

        put25 = _pick(cfg.delta_25_target, want_call=False)
        call25 = _pick(cfg.delta_25_target, want_call=True)
        if put25 is None or call25 is None:
            return None
        return (put25.iv - call25.iv) / atm

    by_day: dict[date, list[tuple]] = {}
    for g in greeks_rows:
        d = g[0] if isinstance(g[0], date) else _normalize_date(g[0])
        if d <= current_date:
            by_day.setdefault(d, []).append(g)

    if current_date not in by_day:
        return None, None, [f"{current_date.isoformat()} 无 greeks 数据（08-03 前未覆盖），Skew 降级"]
    skew_norm = _daily_skew_norm(current_date, by_day[current_date])
    if skew_norm is None:
        return None, None, ["当日 25Δ 选约失败（greeks×iv_surface 映射缺口或平值 IV 缺失），Skew 降级"]

    history = sorted(
        (d, v) for d, day_rows in by_day.items() if (v := _daily_skew_norm(d, day_rows)) is not None
    )
    if len(history) < cfg.skew_min_periods:
        notes.append(f"Skew 分位窗 {len(history)} 日 < {cfg.skew_min_periods} 日守卫，skew_extreme 降级")
        return skew_norm, None, notes
    hist_values = sorted(v for _, v in history)
    threshold = hist_values[min(len(hist_values) - 1, math.ceil(cfg.skew_extreme_percentile * len(hist_values)) - 1)]
    # 严格超过历史 90% 分位值（平盘序列不误判极端）；右偏/零值不算尾部保护
    extreme = skew_norm > 0 and skew_norm > threshold
    return skew_norm, extreme, notes


def _compose_score(
    pcr_percentile: float | None,
    iv_rank: float | None,
    iv_jump_flag: bool,
    skew_extreme: bool | None,
    cfg: OptionSentimentConfig,
) -> tuple[float | None, list[str]]:
    """维度⑨ 合成：子分 ∈[-1,1] 取可用均值；正=温和/恐慌反向机会，负=风险警示。"""
    subs: list[float] = []
    notes: list[str] = []
    if pcr_percentile is not None:
        if pcr_percentile < cfg.pcr_low_percentile:
            subs.append(-1.0)
            notes.append(f"PCR 分位 {pcr_percentile:.0%}<20%：过度乐观，反向风险")
        elif pcr_percentile > cfg.pcr_high_percentile:
            subs.append(1.0)
            notes.append(f"PCR 分位 {pcr_percentile:.0%}>80%：恐慌过度，底部区")
        else:
            subs.append(0.0)
            notes.append(f"PCR 分位 {pcr_percentile:.0%}：中性区")
    if iv_rank is not None:
        if iv_rank > cfg.iv_high_percentile:
            subs.append(-1.0)
            notes.append(f"IV Rank {iv_rank:.0%}>80%：高波恐慌")
        elif iv_rank < cfg.iv_low_percentile:
            subs.append(0.5)
            notes.append(f"IV Rank {iv_rank:.0%}<20%：低波温和")
        else:
            subs.append(0.0)
            notes.append(f"IV Rank {iv_rank:.0%}：中性区")
    if iv_jump_flag:
        subs.append(-0.5)
        notes.append("IV 单日跳升>+3σ：机构避险急增")
    if skew_extreme is True:
        subs.append(-1.0)
        notes.append("归一 Skew>90% 分位：机构尾部保护急增（极端左偏）")
    elif skew_extreme is False:
        subs.append(0.0)
    if not subs:
        return None, notes
    score = sum(subs) / len(subs)
    return max(-1.0, min(1.0, score)), notes


def _degraded_result(date_str: str, note: str, m1_threshold_scale: float = 1.0) -> OptionSentimentResult:
    logger.warning("期权情绪分析降级: %s", note)
    return OptionSentimentResult(date=date_str, m1_threshold_scale=m1_threshold_scale, degraded=True, notes=[note])


def compute_option_sentiment(
    trade_date: str | date | datetime | None = None,
    ch_client: Any | None = None,
    config: OptionSentimentConfig | None = None,
) -> OptionSentimentResult:
    """主入口：期权情绪三件套（PCR+IV Rank+Skew）→ 情绪注解维度⑨。

    Args:
        trade_date: 数据日；None 时取主标的 iv_surface 最新数据日（PIT 数据日口径）。
        ch_client: clickhouse-driver 鸭子类型（execute(sql, params) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client，不可得→degraded。
        config: 阈值配置（None 用默认 44号 §9.9 + 实证口径）。

    Returns:
        OptionSentimentResult；主数据（iv_surface）缺失/查询异常 → degraded=True 空结果
        不炸；PCR/Skew/到期日各部件独立降级互不累及（notes 留痕）。
    """
    cfg = config or OptionSentimentConfig()

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        d = _normalize_date(trade_date) if trade_date is not None else date.today()
        return _degraded_result(d.isoformat(), "ch_client 未注入且默认客户端不可用")

    if trade_date is None:
        try:
            latest = client.execute(SQL_LATEST_IV_DATE, {"underlying": cfg.underlying})
        except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
            return _degraded_result("unknown", f"最新数据日查询异常: {e!r}")
        if not latest or latest[0][0] is None:
            return _degraded_result("unknown", f"主标的 {cfg.underlying} iv_surface 无任何数据")
        d = latest[0][0] if isinstance(latest[0][0], date) else _normalize_date(latest[0][0])
    else:
        d = _normalize_date(trade_date)
    date_str = d.isoformat()
    start = d - timedelta(days=cfg.lookback_calendar_days)
    params = {"underlying": cfg.underlying, "trade_date": d, "start_date": start}

    # 到期日阈值缩放（fail-open：calendar_event 异常 → 1.0 留痕，44号 §9.12 兜底纪律）
    m1_scale = 1.0
    scale_notes: list[str] = []
    try:
        cnt = client.execute(SQL_EXPIRY_EVENT, {"trade_date": d})
        if cnt and int(cnt[0][0]) > 0:
            m1_scale = cfg.expiry_threshold_scale
            scale_notes.append(f"期权到期日（index_option_expiry）当日 → M1 信号阈值 ×{cfg.expiry_threshold_scale}（防伽马挤压假情绪）")
    except Exception as e:  # noqa: BLE001 — 事件日历缺失静默跳过，fail-open 留痕
        scale_notes.append(f"calendar_event 查询异常（fail-open scale=1.0）: {e!r}")

    # 主数据：IV 表面历史窗（iv_rank/ATM/Skew 共用）
    try:
        iv_rows = [_parse_iv_row(r) for r in client.execute(SQL_IV_SURFACE_WINDOW, params)]
    except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
        return _degraded_result(date_str, f"option_iv_surface 查询异常: {e!r}", m1_scale)
    if not iv_rows:
        return _degraded_result(date_str, f"主标的 {cfg.underlying} iv_surface 窗内无有效 IV 数据", m1_scale)

    notes: list[str] = list(scale_notes)
    atm_series = _daily_atm_iv(iv_rows)
    iv_rank, iv_jump, iv_note = _compute_iv_rank(atm_series, d, cfg)
    if iv_note:
        notes.append(iv_note)

    # F1 成交量 PCR（独立降级：option_kline 缺失不累及 IV/Skew）
    pcr: float | None = None
    pcr_pct: float | None = None
    pcr_basis = "volume"
    try:
        volume_rows = client.execute(SQL_OPTION_VOLUME_WINDOW, params)
        map_rows = client.execute(SQL_SYMBOL_MAP, {})
        symbol_map = {str(r[0]): (str(r[1]), str(r[2])) for r in map_rows}
        pcr, pcr_pct, pcr_notes = _compute_pcr(volume_rows, symbol_map, d, cfg)
        notes.extend(pcr_notes)
    except Exception as e:  # noqa: BLE001 — PCR 部件异常独立降级
        notes.append(f"option_kline/映射查询异常，PCR 降级: {e!r}")

    # F3 Skew（独立降级：greeks 缺失不累及 PCR/IV）
    skew_norm: float | None = None
    skew_extreme: bool | None = None
    try:
        greeks_rows = client.execute(SQL_GREEKS_WINDOW, params)
        skew_norm, skew_extreme, skew_notes = _compute_skew(greeks_rows, iv_rows, atm_series, d, cfg)
        notes.extend(skew_notes)
    except Exception as e:  # noqa: BLE001 — Skew 部件异常独立降级
        notes.append(f"option_greeks 查询异常，Skew 降级: {e!r}")

    # 背离警示：PCR 低分位（散户乐观）× Skew 极端（机构买保护）= 多空分歧最大（44号原文形态）
    divergence = (
        pcr_pct is not None
        and pcr_pct < cfg.pcr_low_percentile
        and skew_extreme is True
    )
    if divergence:
        notes.append("PCR 低分位×Skew 极端背离：多空分歧最大警示（散户乐观 vs 机构尾部保护）")

    score, annotations = _compose_score(pcr_pct, iv_rank, iv_jump, skew_extreme, cfg)

    return OptionSentimentResult(
        date=date_str,
        pcr=pcr,
        pcr_basis=pcr_basis,
        pcr_percentile=pcr_pct,
        iv_rank=iv_rank,
        iv_jump_flag=iv_jump,
        skew_norm=skew_norm,
        skew_extreme=skew_extreme,
        divergence_warning=divergence,
        composite_score=score,
        annotation=annotations,
        m1_threshold_scale=m1_scale,
        degraded=False,
        notes=notes,
    )
