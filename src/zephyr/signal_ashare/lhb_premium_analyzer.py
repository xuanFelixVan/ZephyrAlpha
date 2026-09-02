# [BLUEPRINT] MOD-SIG-057 | 待统筹登记（blueprint 未建，真源=44号备忘录 §9.7）
# [MODULE] zephyr.signal_ashare.lhb_premium_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml; c1_market.dragon_tiger_seat（只读）; c1_market.dragon_tiger（只读）
# [CONSUMERS] （MVP 阶段无——候选消费方：M3-③ 情景方案标的不例外清单、prediction_log 落库）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] premium_factor ∈ {1.0, 0.3}; 无数据/查询异常/客户端不可用 MUST 返回 degraded=True 空结果不炸；T 日龙虎榜盘后 17:00 公布，本模块输出仅供 T+1 盘前消费（PIT）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md §9.7
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可用→degraded=True 不抛；trade_date 格式非法→ValueError（调用方契约违例，fail-closed）
# [TESTS] tests/signal_ashare/test_lhb_premium_analyzer.py
# [A_module] module_id=MOD-SIG-057 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
MOD-SIG-057 — 龙虎榜盘后溢价分析器（44号备忘录 §9.7，M3-⑤ 次日预判）

管"明天会怎样"：消费前一交易日龙虎榜（dragon_tiger_seat 608k 行 2022 起 + dragon_tiger 汇总，
62 号注册表数据已在库未消费），输出次日开盘预判三名单 + 个股级溢价系数：
  ① 高开候选 high_open_candidates——净买率>5% 且买方机构+一线游资≥2 席（yueniuzq 2026-07 口径）
  ② 低开风险 low_open_risks——机构席位净卖出占比>5%
  ③ 反核观察 fanhe_watchlist——跌停股买一为知名游资（联动 28 号反核阶段纪律）
  降权规则：独食型（单一席位买入占比>60%）/ 一日游型（registry 一日游标签 或
  近 20 交易日隔日卖出率>70%）→ 高开候选溢价系数 ×0.3。

与 MOD-SIG-056（seat_pattern_analyzer）正交：056 管"谁在买"（单票单日席位形态跟随信号，
纯函数、由上游喂数）；本模块管"次日溢价"（全市场当日榜单批量扫描，ch_client 注入式自取数）。
席位身份口径复用 seat_registry.yaml：机构=seat_type institution；一线/知名游资=registry 命中
且 seat_style ∈ {龙头连板, 首板}（对齐 MOD-SIG-056 youzi_follow_styles 白名单）；一日游=
registry seat_style="一日游"/max_holding_days≤1（静态）+ 隔日卖出率动态复核。

口径声明：「当日成交额」= 龙虎榜上榜成交额（dragon_tiger 汇总 buy_amount+sell_amount，
缺汇总行时回退席位行合计）——与 MOD-SIG-056 total_turnover / MOD-INT-EVENT-DT 净买率口径一致；
非全市场个股日成交额（该列龙虎榜表未携带）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 当日龙虎榜席位明细（dragon_tiger_seat）
#   fields: symbol/seat_name/buy_amount/sell_amount/net_amount/buy_rank/sell_rank/seat_type/reason
# - id: I2
#   name: 当日龙虎榜汇总（dragon_tiger）
#   fields: symbol/net_buy/buy_amount/sell_amount/reason
# - id: I3
#   name: 买方席位历史窗口（dragon_tiger_seat 近 45 自然日）
#   fields: trade_date/symbol/seat_name/buy_amount/sell_amount
# - id: I4
#   name: seat_registry 席位档案（机构/一线游资/一日游标签）
# 层: 特征
# - id: F1
#   name_zh: 净买率
#   formula: net_buy / (buy_amount + sell_amount)  # 严格 >5% 触发
# - id: F2
#   name_zh: 强身份买方席位数
#   formula: count(买方上榜席位 where institution or 一线游资)  # ≥2 触发
# - id: F3
#   name_zh: 单一席位买入占比
#   formula: max(buy_amount) / Σ买方 buy_amount  # >60% 独食
# - id: F4
#   name_zh: 隔日卖出率
#   formula: 近20交易日买入观测中次一交易日现卖出( sell>0 )占比  # >70% 一日游（样本<3 不定性）
# - id: F5
#   name_zh: 机构净卖出占比
#   formula: |Σ institution net_amount（<0 时）| / 成交额  # >5% 低开
# 层: 算法
# - id: A1
#   name_zh: 高开候选筛选
#   desc: F1>5% 且 F2≥2 → high_open_candidates，基准溢价系数 1.0
# - id: A2
#   name_zh: 候选降权
#   desc: F3>60%（独食）或 买方任一座位一日游（registry 静态 or F4 动态）→ 系数 ×0.3
# - id: A3
#   name_zh: 低开风险识别
#   desc: F5>5% → low_open_risks
# - id: A4
#   name_zh: 反核观察
#   desc: reason 含"跌停" 且 买一(buy_rank=1)为知名游资 → fanhe_watchlist
# 层: 输出
# - id: O1
#   name_zh: LhbPremiumResult
#   intro: date/三名单/各标的溢价系数+tags+reasons/degraded；dataclass asdict JSON 可序列化（prediction_log 预留）
# [/ALGO_FLOW]
#
# 边:
# I1,I2,I4 --> A1
# I1,I3,I4 --> A2
# I1,I4 --> A3
# I1,I2,I4 --> A4
# A1,A2,A3,A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Final

import yaml

logger = logging.getLogger(__name__)

__all__: Final = [
    "LhbPremiumConfig",
    "LhbPremiumResult",
    "LhbSymbolPremium",
    "compute_lhb_premium",
]

_SEAT_REGISTRY_PATH: Final = (
    Path(__file__).resolve().parents[3] / "docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml"
)

# SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值
SQL_LHB_SEAT_ROWS: Final = """
SELECT symbol, seat_name, buy_amount, sell_amount, net_amount, buy_rank, sell_rank, seat_type, reason
FROM c1_market.dragon_tiger_seat
WHERE trade_date = %(trade_date)s
"""

SQL_LHB_SUMMARY_ROWS: Final = """
SELECT symbol, net_buy, buy_amount, sell_amount, reason
FROM c1_market.dragon_tiger
WHERE trade_date = %(trade_date)s
"""

SQL_LHB_SEAT_HISTORY: Final = """
SELECT trade_date, symbol, seat_name, buy_amount, sell_amount
FROM c1_market.dragon_tiger_seat
WHERE trade_date < %(trade_date)s AND trade_date >= %(start_date)s AND seat_name IN %(seat_names)s
"""


@dataclass(frozen=True, slots=True)
class LhbPremiumConfig:
    """阈值配置——默认值取自 44号备忘录 §9.7（yueniuzq 2026-07 口径）。"""

    registry_path: str = str(_SEAT_REGISTRY_PATH)
    net_buy_ratio_threshold: float = 0.05  # 净买率严格 >5% 触发高开候选
    min_strong_buyer_seats: int = 2  # 机构+一线游资 ≥2 席
    single_seat_dominance: float = 0.60  # 单一席位买入占比 >60% 独食
    one_day_sell_rate_threshold: float = 0.70  # 隔日卖出率 >70% 一日游（动态口径）
    one_day_lookback_trade_days: int = 20  # 一日游动态复核窗口（交易日）
    history_window_calendar_days: int = 45  # 历史查询自然日窗口（覆盖 20 交易日）
    one_day_min_samples: int = 3  # 动态隔日卖出率最小观测样本（噪声护栏）
    premium_downgrade_factor: float = 0.3  # 降权系数
    top_youzi_styles: tuple[str, ...] = ("龙头连板", "首板")  # 一线/知名游资风格白名单
    limit_down_keywords: tuple[str, ...] = ("跌停",)  # 跌停判定关键词（reason 字段）


@dataclass(frozen=True, slots=True)
class LhbSymbolPremium:
    """单标的溢价明细（仅信号标的有条目）。"""

    symbol: str
    premium_factor: float  # 1.0 基准 / 0.3 降权
    tags: list[str] = field(
        default_factory=list
    )  # high_open_candidate/downgraded_dushi/downgraded_yiriyou/low_open_risk/fanhe_watch
    reasons: list[str] = field(default_factory=list)  # 判定理由链（可追溯）


@dataclass(frozen=True, slots=True)
class LhbPremiumResult:
    """龙虎榜盘后溢价输出契约（T 日盘后计算，T+1 盘前消费）。"""

    date: str  # 龙虎榜数据日 YYYY-MM-DD
    high_open_candidates: list[str] = field(default_factory=list)  # 次日高开概率升（标的不例外清单）
    low_open_risks: list[str] = field(default_factory=list)  # 低开风险提示
    fanhe_watchlist: list[str] = field(default_factory=list)  # 次日反核观察名单
    premiums: dict[str, LhbSymbolPremium] = field(default_factory=dict)  # 各信号标的溢价系数与理由
    degraded: bool = False  # 无数据/查询异常时 True，结果不可用于决策
    notes: list[str] = field(default_factory=list)  # 降级原因等备注


@dataclass(frozen=True, slots=True)
class _SeatRow:
    """dragon_tiger_seat 行解析结果（金额已 float 化）。"""

    symbol: str
    seat_name: str
    buy: float
    sell: float
    net: float
    buy_rank: int | None
    sell_rank: int | None
    provider_type: str
    reason: str


@dataclass(frozen=True, slots=True)
class _SeatIdentity:
    """席位身份（registry 命中优先，未命中回退 provider 粗分类）。"""

    seat_type: str
    matched_registry: bool
    is_top_youzi: bool  # 一线/知名游资：registry 命中 youzi 且风格在白名单
    is_one_day_youzi: bool  # registry 静态一日游标签


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
        logger.warning("ch_writer 默认客户端不可用，龙虎榜溢价分析降级", exc_info=True)
        return None


def _load_registry(path: str) -> dict[str, dict]:
    """加载 seat_registry.yaml → {seat_name 或 alias 小写: 席位档案}（对齐 MOD-SIG-056 口径）。"""
    p = Path(path)
    if not p.is_file():
        logger.warning("seat_registry 不存在，降级为空档案: %s", path)
        return {}
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        logger.warning("seat_registry 解析失败，降级为空档案: %s", e)
        return {}
    table: dict[str, dict] = {}
    for seat in data.get("seats") or []:
        name = str(seat.get("seat_name") or "").strip()
        if not name:
            continue
        table[name.lower()] = seat
        for alias in seat.get("aliases") or []:
            a = str(alias).strip().lower()
            if a:
                table.setdefault(a, seat)
    return table


def _resolve_identity(
    seat_name: str, provider_type: str, registry: dict[str, dict], cfg: LhbPremiumConfig
) -> _SeatIdentity:
    """席位身份识别：registry 精确名/别名 → provider 粗分类回退。"""
    hit = registry.get(seat_name.strip().lower())
    if hit is None:
        return _SeatIdentity(
            seat_type=provider_type or "unknown",
            matched_registry=False,
            is_top_youzi=False,
            is_one_day_youzi=False,
        )
    seat_type = str(hit.get("seat_type") or "unknown")
    style = str(hit.get("seat_style") or "")
    try:
        max_hold = int(hit.get("max_holding_days") or 0)
    except (TypeError, ValueError):
        max_hold = 0
    return _SeatIdentity(
        seat_type=seat_type,
        matched_registry=True,
        is_top_youzi=seat_type == "youzi" and style in cfg.top_youzi_styles,
        is_one_day_youzi=style == "一日游" or 0 < max_hold <= 1,
    )


def _parse_seat_row(row: tuple) -> _SeatRow:
    return _SeatRow(
        symbol=str(row[0]),
        seat_name=str(row[1]),
        buy=float(row[2] or 0.0),
        sell=float(row[3] or 0.0),
        net=float(row[4] or 0.0),
        buy_rank=int(row[5]) if row[5] is not None else None,
        sell_rank=int(row[6]) if row[6] is not None else None,
        provider_type=str(row[7] or ""),
        reason=str(row[8] or ""),
    )


def _compute_nextday_sell_rates(
    history_rows: list[tuple],
    current_date: date,
    cfg: LhbPremiumConfig,
) -> dict[str, float]:
    """逐席位隔日卖出率：近 N 交易日买入观测中，次一交易日同票现卖出（sell>0）占比。

    日历取历史窗口全部出现日期 ∪ {当日} 近似交易日序列；次日无同席位同票行=不可观测，
    不计入分母（披露仅 Top5，卖出不可见属常态）。观测样本 < min_samples 不定性（不出键）。
    """
    by_seat: dict[str, list[tuple]] = {}
    calendar: set[date] = {current_date}
    for row in history_rows:
        td = row[0] if isinstance(row[0], date) else _normalize_date(row[0])
        by_seat.setdefault(str(row[2]), []).append((td, str(row[1]), float(row[3] or 0.0), float(row[4] or 0.0)))
        calendar.add(td)
    cal_sorted = sorted(calendar)
    next_day = {cal_sorted[i]: cal_sorted[i + 1] for i in range(len(cal_sorted) - 1)}

    rates: dict[str, float] = {}
    for seat, rows in by_seat.items():
        seat_dates = sorted({r[0] for r in rows}, reverse=True)[: cfg.one_day_lookback_trade_days]
        cutoff = min(seat_dates)
        window = [r for r in rows if r[0] >= cutoff]
        index = {(sym, td): (buy, sell) for td, sym, buy, sell in window}
        observed = sells = 0
        for td, sym, buy, _sell in window:
            if buy <= 0:
                continue
            nd = next_day.get(td)
            if nd is None:
                continue
            nxt = index.get((sym, nd))
            if nxt is None:
                continue
            observed += 1
            if nxt[1] > 0:
                sells += 1
        if observed >= cfg.one_day_min_samples:
            rates[seat] = sells / observed
    return rates


def _degraded_result(date_str: str, note: str) -> LhbPremiumResult:
    logger.warning("龙虎榜溢价分析降级: %s", note)
    return LhbPremiumResult(date=date_str, degraded=True, notes=[note])


def compute_lhb_premium(
    trade_date: str | date | datetime,
    ch_client: Any | None = None,
    config: LhbPremiumConfig | None = None,
) -> LhbPremiumResult:
    """主入口：T 日龙虎榜 → T+1 日开盘预判（高开候选/低开风险/反核观察+溢价系数）。

    Args:
        trade_date: 龙虎榜数据日（T 日；盘后 17:00 后计算，T+1 盘前消费）。
        ch_client: clickhouse-driver 鸭子类型（execute(sql, params) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client，不可得→degraded。
        config: 阈值配置（None 用默认 44号 §9.7 口径）。

    Returns:
        LhbPremiumResult；无数据/查询异常 → degraded=True 空结果不炸（对齐 MOD-SIG-056 范式）。
    """
    cfg = config or LhbPremiumConfig()
    d = _normalize_date(trade_date)
    date_str = d.isoformat()

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        return _degraded_result(date_str, "ch_client 未注入且默认客户端不可用")

    try:
        seat_rows = [_parse_seat_row(r) for r in client.execute(SQL_LHB_SEAT_ROWS, {"trade_date": d})]
        summary_rows = client.execute(SQL_LHB_SUMMARY_ROWS, {"trade_date": d})
    except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
        return _degraded_result(date_str, f"龙虎榜查询异常: {e!r}")

    if not seat_rows and not summary_rows:
        return _degraded_result(date_str, f"{date_str} 无龙虎榜数据（非交易日或未披露）")

    registry = _load_registry(cfg.registry_path)

    summary_by_symbol: dict[str, tuple[float, float, float, str]] = {}
    for row in summary_rows:
        summary_by_symbol[str(row[0])] = (
            float(row[1] or 0.0),
            float(row[2] or 0.0),
            float(row[3] or 0.0),
            str(row[4] or ""),
        )
    seats_by_symbol: dict[str, list[_SeatRow]] = {}
    for r in seat_rows:
        seats_by_symbol.setdefault(r.symbol, []).append(r)

    symbols = sorted(set(seats_by_symbol) | set(summary_by_symbol))
    identities: dict[str, _SeatIdentity] = {
        r.seat_name: _resolve_identity(r.seat_name, r.provider_type, registry, cfg) for r in seat_rows
    }

    high_open: list[str] = []
    low_open: list[str] = []
    fanhe: list[str] = []
    workspace: dict[str, dict[str, Any]] = {}  # sym → {tags/reasons/factor} 可变工作区（末段一次性冻结）
    candidate_buyers: dict[str, list[_SeatRow]] = {}  # 待降权复核的候选买方席位

    for sym in symbols:
        seats = seats_by_symbol.get(sym, [])
        summary = summary_by_symbol.get(sym)
        if summary is not None:
            net_buy, sum_buy, sum_sell, sum_reason = summary
            turnover = sum_buy + sum_sell
        else:
            net_buy = sum(r.net for r in seats)
            turnover = sum(r.buy + r.sell for r in seats)
            sum_reason = ""
        if turnover <= 0:
            continue
        ratio = net_buy / turnover
        buyers = [r for r in seats if r.buy_rank is not None]
        strong = [
            r
            for r in buyers
            if identities[r.seat_name].seat_type == "institution" or identities[r.seat_name].is_top_youzi
        ]

        tags: list[str] = []
        reasons: list[str] = []
        factor = 1.0

        # 规则① 高开候选：净买率>5% 且 机构+一线游资 ≥2 席
        if ratio > cfg.net_buy_ratio_threshold and len(strong) >= cfg.min_strong_buyer_seats:
            tags.append("high_open_candidate")
            reasons.append(f"净买率{ratio:.1%}>5%且机构/一线游资{len(strong)}席≥2 → 次日高开概率升")
            high_open.append(sym)
            candidate_buyers[sym] = buyers

        # 规则③ 低开风险：机构席位净卖出>5%
        inst_net = sum(r.net for r in seats if identities[r.seat_name].seat_type == "institution")
        if inst_net < 0 and abs(inst_net) / turnover > cfg.net_buy_ratio_threshold:
            tags.append("low_open_risk")
            reasons.append(f"机构席位净卖出占比{abs(inst_net) / turnover:.1%}>5% → 低开风险提示")
            low_open.append(sym)

        # 规则④ 反核观察：跌停股买一为知名游资
        reason_text = sum_reason + " " + " ".join(r.reason for r in seats)
        if any(kw in reason_text for kw in cfg.limit_down_keywords):
            top_buyer = next((r for r in seats if r.buy_rank == 1), None)
            if top_buyer is not None and identities[top_buyer.seat_name].is_top_youzi:
                tags.append("fanhe_watch")
                reasons.append(f"跌停股买一为知名游资({top_buyer.seat_name}) → 次日反核观察")
                fanhe.append(sym)

        if tags:
            workspace[sym] = {"tags": tags, "reasons": reasons, "factor": factor}

    # 规则② 候选降权：独食 / 一日游（静态 registry 标签 + 动态隔日卖出率复核）
    if candidate_buyers:
        dynamic_seats = sorted(
            {
                r.seat_name
                for buyers in candidate_buyers.values()
                for r in buyers
                if not identities[r.seat_name].is_one_day_youzi
            }
        )
        sell_rates: dict[str, float] = {}
        if dynamic_seats:
            try:
                history_rows = client.execute(
                    SQL_LHB_SEAT_HISTORY,
                    {
                        "trade_date": d,
                        "start_date": d - timedelta(days=cfg.history_window_calendar_days),
                        "seat_names": tuple(dynamic_seats),
                    },
                )
                sell_rates = _compute_nextday_sell_rates(history_rows, d, cfg)
            except Exception as e:  # noqa: BLE001 — 历史复核失败不阻塞主结果，仅留痕
                logger.warning("一日游动态复核查询失败，跳过动态口径: %r", e)

        for sym, buyers in candidate_buyers.items():
            entry = workspace[sym]
            tags = entry["tags"]
            reasons = entry["reasons"]
            total_buy = sum(r.buy for r in buyers if r.buy > 0)
            if total_buy > 0:
                top_seat = max(buyers, key=lambda r: r.buy)
                share = top_seat.buy / total_buy
                if share > cfg.single_seat_dominance:
                    tags.append("downgraded_dushi")
                    reasons.append(
                        f"独食降权：单一席位({top_seat.seat_name})买入占比{share:.1%}>60% → 溢价系数×{cfg.premium_downgrade_factor}"
                    )
            for r in buyers:
                ident = identities[r.seat_name]
                rate = sell_rates.get(r.seat_name)
                if ident.is_one_day_youzi:
                    tags.append("downgraded_yiriyou")
                    reasons.append(
                        f"一日游降权：{r.seat_name} 注册表一日游标签 → 溢价系数×{cfg.premium_downgrade_factor}"
                    )
                    break
                if rate is not None and rate > cfg.one_day_sell_rate_threshold:
                    tags.append("downgraded_yiriyou")
                    reasons.append(
                        f"一日游降权：{r.seat_name} 近{cfg.one_day_lookback_trade_days}日隔日卖出率{rate:.1%}>70% → 溢价系数×{cfg.premium_downgrade_factor}"
                    )
                    break
            if "downgraded_dushi" in tags or "downgraded_yiriyou" in tags:
                entry["factor"] = cfg.premium_downgrade_factor

    premiums = {
        sym: LhbSymbolPremium(symbol=sym, premium_factor=ws["factor"], tags=ws["tags"], reasons=ws["reasons"])
        for sym, ws in workspace.items()
    }

    return LhbPremiumResult(
        date=date_str,
        high_open_candidates=sorted(high_open),
        low_open_risks=sorted(low_open),
        fanhe_watchlist=sorted(fanhe),
        premiums=premiums,
        degraded=False,
    )
