# [BLUEPRINT] MOD-RES-001 | docs/03_modules/_domain_research/sell_news_event_study/blueprint.md
# [MODULE] zephyr.research.sell_news_event_study
# [DOMAIN] D_RESEARCH
# [DEPENDENCIES] pandas; zephyr.shared.foundation.errors(ZephyrBaseError)
# [CONSUMERS] 运行时装配批（事件清单+日K+基准指数 DataFrame 注入）；L3 消化层 priced-in 规则标定（产出为规则建议文本，不直接落库）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数零 IO（数据全注入，不直连 ClickHouse/网络）；T0=事件日当日或其后首个交易日（财报盘后披露口径）；事前涨幅窗口严格取 T0 之前（防前视）；基准按交易日精确对齐，缺口事件剔除并计数；高位/对照任一组为空 Fail-Closed；同输入必同输出
# [MODIFY-GUARD] 候选转正 CAND-RES-030（2026-08-25 新闻情感三层模型讨论批 §8，Owner 拍板 Q3 实证先行）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SellNewsStudyError(ZA-RE-0032)——配置非法/必需列缺失/事件清单为空/窗口或基准缺口致全剔除/分组任一侧为空时抛（消息不拼路径，上下文入 details）
# [TESTS] tests/research/test_sell_news_event_study.py
# [A_module] module_id=MOD-RES-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
SellNewsEventStudy — 高位利好落地事件研究（利好出尽实证，MOD-RES-001）。

CAND-RES-030 转正（2026-08-30 候选核销批桶B，P1）：26号文 §2.4 事件驱动六因子矩阵
dReport 因子的实证底座——"事前 20 日涨幅分位高 + 强利好披露落地"后的利好出尽
（sell-the-news）异常收益分布研究，产出 priced-in 判定规则建议供 L3 消化层标定阈值。

数据可得性（B16 勘探裁定 GO，docs/_working/2026-08-30-b16-feed-exploration.md）：
事件源（披露计划实际披露日/业绩快报公告日/业绩预告）与日 K、基准指数均在仓；
本模块只做统计层——事件清单、个股日 K 面板、基准日收益全部由调用方装配注入，
本模块不直连数仓（纯函数，同输入必同输出）。

口径（写清）
------------
- **T0**：事件日当日或其后首个交易日（A 股财报多盘后披露，事件反应自 T0 起算）；
- **事前涨幅**：``close[T0-1] / close[T0-1-pre_window] - 1``（严格 T0 之前，防前视）；
- **分组**：全事件横截面事前涨幅分位 >= high_quantile（默认 0.8，top 20%）为高位组，
  其余为对照组；
- **异常收益 AR**：``r_symbol - r_benchmark``（基准口径参数化，默认中证全指标签
  csi_all，仅作记录——基准序列本体注入）；
- **CAR_N**：T0 后第 1..N 个交易日 AR 累计和，N 取 horizons（默认 1/3/5/10）；
- **priced-in 判定**（逐 horizon）：高位组 CAR 均值 < 0 且高位-对照 spread < 0
  且 |t| >= significance_t（单样本 t，经验法则 2.0）且高位组 CAR<0 占比 >= 50%
  -> 利好出尽成立，输出 L3 阈值规则建议。

查重分工（防重建）
------------------
- MOD-SIG-106 sell_news_overdraft_detector（signal_ashare）：**逐事件实时**预期透支度
  检测（价格/时间/资金/情绪 4 维 -> 落地前减仓信号），是本研究的下游消费形态；
- MOD-INT-EVENT-FACTOR（intelligence/event_factor_matrix）：dReport/Jump on PEAD
  **因子值**计算件（单事件数值项），不做跨事件 CAR 分布统计；
- 本件：**跨事件统计研究**（分组 CAR 分布 -> priced-in 规则建议），纯研究态不落因子表。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: events 参数
#   fields: 参数 events，类型注解 pd.DataFrame
#   code: sell_news_event_study.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: prices 参数
#   fields: 参数 prices，类型注解 pd.DataFrame
#   code: sell_news_event_study.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: benchmark 参数
#   fields: 参数 benchmark，类型注解 pd.DataFrame
#   code: sell_news_event_study.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: config 参数
#   fields: 参数 config，类型注解 SellNewsStudyConfig | None
#   code: sell_news_event_study.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run_sell_news_study
#   name_en: run_sell_news_study
#   intro: 高位利好落地事件研究主入口（纯函数，数据全注入）。
#   desc: 高位利好落地事件研究主入口（纯函数，数据全注入）。 Parameters ---------- events : 事件清单，列 symbol / event_date / eve…；源码 L525-L590
#   inputs: events prices benchmark config
#   outputs: SellNewsStudyReport
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: SellNewsStudyReport
#   name_en: SellNewsStudyReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（事件清单+日K+基准指数 DataFrame 注入）；L3 消化层 priced-in 规则标定（产出为规则建议文本，不直接落库）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import pandas as pd

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "DEFAULT_BENCHMARK_NAME",
    "DEFAULT_HIGH_QUANTILE",
    "DEFAULT_HORIZONS",
    "DEFAULT_PRE_WINDOW",
    "DEFAULT_PRIMARY_HORIZON",
    "DEFAULT_SIGNIFICANCE_T",
    "EventCarStats",
    "PricedInVerdict",
    "SellNewsStudyConfig",
    "SellNewsStudyError",
    "SellNewsStudyReport",
    "run_sell_news_study",
]

#: 事前涨幅窗口（交易日，26号文口径 20 日）
DEFAULT_PRE_WINDOW: Final = 20
#: 高位组分位阈值（默认 top 20%）
DEFAULT_HIGH_QUANTILE: Final = 0.8
#: 落地后观察窗（交易日）
DEFAULT_HORIZONS: Final = (1, 3, 5, 10)
#: 主判定窗（priced_in 汇总口径，招商/华泰实证常用 5 日）
DEFAULT_PRIMARY_HORIZON: Final = 5
#: 显著性 t 阈值（经验法则 |t|>=2）
DEFAULT_SIGNIFICANCE_T: Final = 2.0
#: 基准口径标签（默认中证全指；基准序列本体由调用方注入，本字段仅记录口径）
DEFAULT_BENCHMARK_NAME: Final = "csi_all"

_EVENT_COLS: Final = ("symbol", "event_date", "event_type")
_PRICE_COLS: Final = ("symbol", "date", "close")
_BENCH_COLS: Final = ("date", "close")


class SellNewsStudyError(ZephyrBaseError):
    """高位利好落地事件研究输入/配置契约违反（Fail-Closed）。"""

    error_code = "ZA-RE-0032"


@dataclass(frozen=True, slots=True)
class SellNewsStudyConfig:
    """事件研究配置（frozen）。

    - pre_window: 事前涨幅窗口（交易日，默认 20）
    - high_quantile: 高位组横截面分位阈值（默认 0.8 = top 20%）
    - horizons: 落地后 CAR 观察窗（交易日，严格升序去重）
    - primary_horizon: priced-in 主判定窗（不在 horizons 内则取最大窗）
    - significance_t: 单样本 t 显著性阈值（经验法则 2.0）
    - benchmark_name: 基准口径标签（仅记录，基准序列本体注入）
    """

    pre_window: int = DEFAULT_PRE_WINDOW
    high_quantile: float = DEFAULT_HIGH_QUANTILE
    horizons: tuple[int, ...] = DEFAULT_HORIZONS
    primary_horizon: int = DEFAULT_PRIMARY_HORIZON
    significance_t: float = DEFAULT_SIGNIFICANCE_T
    benchmark_name: str = DEFAULT_BENCHMARK_NAME


@dataclass(frozen=True, slots=True)
class EventCarStats:
    """单组单窗口 CAR 分布统计（frozen）。

    negative_share = CAR<0 占比（利好出尽方向胜率）；t_stat = 均值单样本 t
    （std=0 且均值非零时为 ±inf——恒定样本的确定性偏离视作显著）。
    """

    group: str
    horizon: int
    count: int
    mean: float
    median: float
    std: float
    p25: float
    p75: float
    negative_share: float
    t_stat: float


@dataclass(frozen=True, slots=True)
class PricedInVerdict:
    """单窗口 priced-in 判定（frozen）。

    priced_in=True 即"利好出尽成立"：高位组 CAR 显著为负且弱于对照组。
    rule_hint 为给 L3 消化层的规则建议文本（建议态，不直接生效）。
    """

    horizon: int
    high_mean_car: float
    control_mean_car: float
    spread: float
    high_negative_share: float
    t_stat: float
    significant: bool
    priced_in: bool
    rule_hint: str


@dataclass(frozen=True, slots=True)
class SellNewsStudyReport:
    """事件研究总报告（frozen）。

    stats 覆盖 (high, control) x horizons 全组合；primary_verdict 为主判定窗结论；
    priced_in / suggestion 为主判定窗汇总（供 L3 消化层规则标定）。
    """

    n_events_input: int
    n_events_used: int
    n_events_dropped: int
    event_type_counts: dict[str, int]
    pre_window: int
    high_quantile: float
    pre_return_threshold: float
    benchmark_name: str
    stats: tuple[EventCarStats, ...]
    verdicts: tuple[PricedInVerdict, ...]
    primary_verdict: PricedInVerdict
    priced_in: bool
    suggestion: str


@dataclass(frozen=True, slots=True)
class _EventSample:
    """单事件提取结果（内部）：事前涨幅 + 各窗口 CAR。"""

    symbol: str
    event_type: str
    pre_ret: float
    cars: dict[int, float]


def _validate_config(cfg: SellNewsStudyConfig) -> None:
    """配置契约校验（Fail-Closed，上下文入 details）。"""
    if cfg.pre_window < 1:
        raise SellNewsStudyError("配置非法：pre_window 必须 >= 1", details={"pre_window": cfg.pre_window})
    if not 0.0 < cfg.high_quantile < 1.0:
        raise SellNewsStudyError(
            "配置非法：high_quantile 必须落在 (0, 1) 开区间",
            details={"high_quantile": cfg.high_quantile},
        )
    if not cfg.horizons:
        raise SellNewsStudyError("配置非法：horizons 为空", details={})
    _validate_horizons(cfg.horizons)
    if cfg.significance_t <= 0.0:
        raise SellNewsStudyError(
            "配置非法：significance_t 必须 > 0",
            details={"significance_t": cfg.significance_t},
        )


def _validate_horizons(horizons: tuple[int, ...]) -> None:
    """观察窗契约：全正整数且严格升序去重。"""
    if any(h < 1 for h in horizons):
        raise SellNewsStudyError("配置非法：horizons 含非正窗口", details={"horizons": horizons})
    if tuple(sorted(set(horizons))) != tuple(horizons):
        raise SellNewsStudyError(
            "配置非法：horizons 必须严格升序且无重复",
            details={"horizons": horizons},
        )


def _validate_frames(
    events: pd.DataFrame,
    prices: pd.DataFrame,
    benchmark: pd.DataFrame,
) -> None:
    """输入 DataFrame 必需列与非空校验（Fail-Closed）。"""
    required = (
        (events, _EVENT_COLS, "events"),
        (prices, _PRICE_COLS, "prices"),
        (benchmark, _BENCH_COLS, "benchmark"),
    )
    for df, cols, label in required:
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise SellNewsStudyError(
                "输入数据缺少必需列",
                details={"frame": label, "missing": missing},
            )
    if len(events) == 0:
        raise SellNewsStudyError("事件清单为空，无研究样本", details={"frame": "events"})


def _benchmark_returns(benchmark: pd.DataFrame) -> dict[pd.Timestamp, float]:
    """基准日收益字典：date -> close/close_prev - 1（首日为起点无收益）。"""
    bench = benchmark.sort_values("date", kind="mergesort")
    dates = pd.to_datetime(bench["date"])
    closes = bench["close"].to_numpy(dtype=float)
    rets: dict[pd.Timestamp, float] = {}
    prev = 0.0
    started = False
    for d, c in zip(dates, closes, strict=True):
        if started and prev > 0.0:
            rets[pd.Timestamp(d)] = float(c) / prev - 1.0
        prev = float(c)
        started = True
    return rets


def _symbol_panels(prices: pd.DataFrame) -> dict[str, tuple[pd.DatetimeIndex, tuple[float, ...]]]:
    """个股日 K 面板：symbol -> (交易日期升序索引, 收盘价序列)（确定性排序）。"""
    panels: dict[str, tuple[pd.DatetimeIndex, tuple[float, ...]]] = {}
    for symbol, grp in prices.groupby("symbol", sort=True):
        g = grp.sort_values("date", kind="mergesort")
        idx = pd.DatetimeIndex(pd.to_datetime(g["date"]))
        closes = tuple(float(c) for c in g["close"].to_numpy(dtype=float))
        panels[str(symbol)] = (idx, closes)
    return panels


def _forward_ars(
    closes: tuple[float, ...],
    dates: pd.DatetimeIndex,
    t0: int,
    max_horizon: int,
    bmk_ret: dict[pd.Timestamp, float],
) -> list[float] | None:
    """T0 后第 1..max_horizon 日异常收益序列；基准缺口返回 None（事件剔除）。"""
    ars: list[float] = []
    for k in range(1, max_horizon + 1):
        r_sym = closes[t0 + k] / closes[t0 + k - 1] - 1.0
        r_bmk = bmk_ret.get(pd.Timestamp(dates[t0 + k]))
        if r_bmk is None:
            return None
        ars.append(r_sym - r_bmk)
    return ars


def _cars_from_ars(ars: list[float], horizons: tuple[int, ...]) -> dict[int, float]:
    """AR 序列累计为各窗口 CAR（horizons 严格升序已由配置校验保证）。"""
    cars: dict[int, float] = {}
    acc = 0.0
    for i, ar in enumerate(ars, start=1):
        acc += ar
        if i in horizons:
            cars[i] = acc
    return cars


def _event_sample(
    symbol: str,
    event_date: object,
    event_type: str,
    panel: tuple[pd.DatetimeIndex, tuple[float, ...]],
    cfg: SellNewsStudyConfig,
    bmk_ret: dict[pd.Timestamp, float],
) -> _EventSample | None:
    """单事件样本提取；窗口不足/基准缺口返回 None（由调用方计数剔除）。

    T0 = 事件日当日或其后首个交易日（盘后披露口径）；事前涨幅严格取 T0 之前
    ``close[T0-1] / close[T0-1-pre_window] - 1``（防前视）。
    """
    dates, closes = panel
    t0 = int(dates.searchsorted(pd.Timestamp(event_date)))
    max_horizon = cfg.horizons[-1]
    if t0 >= len(dates) or t0 < cfg.pre_window + 1 or t0 + max_horizon >= len(closes):
        return None
    pre_ret = closes[t0 - 1] / closes[t0 - 1 - cfg.pre_window] - 1.0
    ars = _forward_ars(closes, dates, t0, max_horizon, bmk_ret)
    if ars is None:
        return None
    return _EventSample(
        symbol=symbol,
        event_type=event_type,
        pre_ret=pre_ret,
        cars=_cars_from_ars(ars, cfg.horizons),
    )


def _collect_samples(
    events: pd.DataFrame,
    panels: dict[str, tuple[pd.DatetimeIndex, tuple[float, ...]]],
    bmk_ret: dict[pd.Timestamp, float],
    cfg: SellNewsStudyConfig,
) -> tuple[list[_EventSample], int]:
    """逐事件提取样本；缺面板/窗口不足/基准缺口剔除并计数（不抛错）。"""
    samples: list[_EventSample] = []
    dropped = 0
    for row in events.itertuples(index=False):
        symbol = str(row.symbol)
        panel = panels.get(symbol)
        sample = (
            None if panel is None else _event_sample(symbol, row.event_date, str(row.event_type), panel, cfg, bmk_ret)
        )
        if sample is None:
            dropped += 1
            continue
        samples.append(sample)
    return samples, dropped


def _quantile(sorted_vals: list[float], q: float) -> float:
    """线性插值分位数（输入必须已升序排序；确定性）。"""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    rank = q * (n - 1)
    lo = int(math.floor(rank))
    hi = int(math.ceil(rank))
    frac = rank - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def _sample_std(vals: list[float], mean: float) -> float:
    """样本标准差（ddof=1；n<2 返回 0.0）。"""
    n = len(vals)
    if n < 2:
        return 0.0
    return math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))


def _t_stat(mean: float, std: float, n: int) -> float:
    """单样本 t 统计量；std=0 时恒定样本的非零均值视作确定性偏离（±inf）。"""
    if n < 2 or std <= 0.0:
        if mean == 0.0:
            return 0.0
        return math.copysign(math.inf, mean)
    return mean / (std / math.sqrt(n))


def _car_stats(group: str, horizon: int, cars: list[float]) -> EventCarStats:
    """单组单窗口 CAR 分布统计（均值/中位/胜率/分位/t）。"""
    ordered = sorted(cars)
    n = len(cars)
    mean = sum(cars) / n
    std = _sample_std(cars, mean)
    return EventCarStats(
        group=group,
        horizon=horizon,
        count=n,
        mean=mean,
        median=_quantile(ordered, 0.5),
        std=std,
        p25=_quantile(ordered, 0.25),
        p75=_quantile(ordered, 0.75),
        negative_share=sum(1 for c in cars if c < 0.0) / n,
        t_stat=_t_stat(mean, std, n),
    )


def _group_stats(
    high: list[_EventSample],
    control: list[_EventSample],
    cfg: SellNewsStudyConfig,
) -> tuple[EventCarStats, ...]:
    """(high, control) x horizons 全组合分布统计。"""
    out: list[EventCarStats] = []
    for horizon in cfg.horizons:
        for group_name, group in (("high", high), ("control", control)):
            out.append(_car_stats(group_name, horizon, [s.cars[horizon] for s in group]))
    return tuple(out)


def _stats_lookup(stats: tuple[EventCarStats, ...]) -> dict[tuple[str, int], EventCarStats]:
    """(group, horizon) -> EventCarStats 索引。"""
    return {(s.group, s.horizon): s for s in stats}


def _build_verdict(
    horizon: int, high: EventCarStats, control: EventCarStats, cfg: SellNewsStudyConfig
) -> PricedInVerdict:
    """单窗口 priced-in 判定：显著为负 + 弱于对照 + 负收益过半 -> 利好出尽成立。"""
    spread = high.mean - control.mean
    significant = abs(high.t_stat) >= cfg.significance_t
    priced_in = bool(high.mean < 0.0 and spread < 0.0 and significant and high.negative_share >= 0.5)
    if priced_in:
        rule_hint = (
            f"高位组落地后 {horizon} 日 CAR 均值 {high.mean:.2%} 显著为负"
            f"（对照组 {control.mean:.2%}，t={high.t_stat:.2f}）"
            "——建议 L3 消化层对高位强利好按 priced-in 处理"
        )
    else:
        rule_hint = (
            f"高位组落地后 {horizon} 日 CAR 均值 {high.mean:.2%} 未满足利好出尽判定"
            "（需显著为负且弱于对照且负收益占比过半）——本窗口不建议启用 priced-in 规则"
        )
    return PricedInVerdict(
        horizon=horizon,
        high_mean_car=high.mean,
        control_mean_car=control.mean,
        spread=spread,
        high_negative_share=high.negative_share,
        t_stat=high.t_stat,
        significant=significant,
        priced_in=priced_in,
        rule_hint=rule_hint,
    )


def _primary_verdict(verdicts: tuple[PricedInVerdict, ...], primary_horizon: int) -> PricedInVerdict:
    """主判定窗结论；primary_horizon 不在 horizons 内时取最大窗。"""
    for v in verdicts:
        if v.horizon == primary_horizon:
            return v
    return verdicts[-1]


def _suggest(primary: PricedInVerdict, cfg: SellNewsStudyConfig, threshold: float) -> str:
    """L3 消化层规则建议文本（建议态，不直接生效）。"""
    if primary.priced_in:
        return (
            f"利好出尽成立：事前 {cfg.pre_window} 日涨幅横截面分位 >= {cfg.high_quantile:.0%}"
            f"（本次样本门槛涨幅 {threshold:.2%}）的强利好事件，落地后 {primary.horizon} 日"
            f" CAR 均值 {primary.high_mean_car:.2%}（对照组 {primary.control_mean_car:.2%}，"
            f"负收益占比 {primary.high_negative_share:.0%}）"
            "——建议 L3 消化层 priced-in 阈值取该分位口径，高位落地后转入回避/减仓评审"
        )
    return (
        f"证据不足：高位组 {primary.horizon} 日 CAR 未显著弱于对照"
        f"（高位 {primary.high_mean_car:.2%} vs 对照 {primary.control_mean_car:.2%}）"
        "——不建议启用 priced-in 阈值规则，待扩样后复评"
    )


def _event_type_counts(samples: list[_EventSample]) -> dict[str, int]:
    """事件类型计数（确定性升序键序）。"""
    counts: dict[str, int] = {}
    for s in samples:
        counts[s.event_type] = counts.get(s.event_type, 0) + 1
    return dict(sorted(counts.items()))


def run_sell_news_study(
    events: pd.DataFrame,
    prices: pd.DataFrame,
    benchmark: pd.DataFrame,
    config: SellNewsStudyConfig | None = None,
) -> SellNewsStudyReport:
    """高位利好落地事件研究主入口（纯函数，数据全注入）。

    Parameters
    ----------
    events : 事件清单，列 symbol / event_date / event_type。
    prices : 个股日 K 面板，列 symbol / date / close（每 symbol 日期唯一升序）。
    benchmark : 基准日行情，列 date / close（默认口径中证全指，标签记录于报告）。
    config : 研究配置；None 用默认（事前 20 日 / top 20% / 窗 1,3,5,10）。

    Returns
    -------
    SellNewsStudyReport —— 分组 CAR 分布统计 + 逐窗 priced-in 判定 + 规则建议。

    Raises
    ------
    SellNewsStudyError(ZA-RE-0032) —— 配置非法 / 必需列缺失 / 事件清单为空 /
    窗口或基准缺口致样本全剔除 / 高位或对照组为空（Fail-Closed）。
    """
    cfg = config if config is not None else SellNewsStudyConfig()
    _validate_config(cfg)
    _validate_frames(events, prices, benchmark)
    bmk_ret = _benchmark_returns(benchmark)
    panels = _symbol_panels(prices)
    samples, dropped = _collect_samples(events, panels, bmk_ret, cfg)
    if not samples:
        raise SellNewsStudyError(
            "全部事件因窗口不足或基准缺口被剔除，无有效样本",
            details={"n_events_input": len(events), "n_dropped": dropped},
        )
    threshold = _quantile(sorted(s.pre_ret for s in samples), cfg.high_quantile)
    high = [s for s in samples if s.pre_ret >= threshold]
    control = [s for s in samples if s.pre_ret < threshold]
    if not high or not control:
        raise SellNewsStudyError(
            "分位分组失败：高位组或对照组为空（事前涨幅区分度不足）",
            details={
                "threshold": threshold,
                "n_high": len(high),
                "n_control": len(control),
            },
        )
    stats = _group_stats(high, control, cfg)
    lookup = _stats_lookup(stats)
    verdicts = tuple(_build_verdict(h, lookup[("high", h)], lookup[("control", h)], cfg) for h in cfg.horizons)
    primary = _primary_verdict(verdicts, cfg.primary_horizon)
    return SellNewsStudyReport(
        n_events_input=len(events),
        n_events_used=len(samples),
        n_events_dropped=dropped,
        event_type_counts=_event_type_counts(samples),
        pre_window=cfg.pre_window,
        high_quantile=cfg.high_quantile,
        pre_return_threshold=threshold,
        benchmark_name=cfg.benchmark_name,
        stats=stats,
        verdicts=verdicts,
        primary_verdict=primary,
        priced_in=primary.priced_in,
        suggestion=_suggest(primary, cfg, threshold),
    )
