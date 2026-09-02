# [BLUEPRINT] MOD-SIG-062 | 待统筹登记（blueprint 未建，真源=22号 spec §3.1⑦ 步骤① 龙头识别 + 架构审查报告 §11.5 SEC-04 行 + 92号清单 §7.7）
# [MODULE] zephyr.signal_ashare.sector_leader
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] c1_market.kline_daily（只读）; c1_market.stk_limit（只读）; c1_market.sector_constituent（只读）
# [CONSUMERS] （MVP 阶段无——观测先行不接交易；候选消费方：SEC-01 板块盘后报告器、Dashboard D-05 龙头/中军/跟风榜、远期 daban sleeve §3.1⑦ 步骤② 加权传导）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 观测先行纪律：只出四档榜单+评分，不接交易/不出买卖点（92号 §7.7 原文）；四档传导权重 1.5/1.2/0.8/0 走 config（SectorLeaderConfig），不硬编码进消费方；连板高度=stk_limit.limit_up×kline_daily.close 收盘封板连续推导（0.005 价格网格容差，对齐 MOD-SIG-060 炸板判定口径）；当日涨幅=相邻收盘推导（kline_daily.pct_change 列 2026-08-22 实证全 0 未填充，不用）；无龙头板块→leader 档空+中文注解（不强行封龙）；中位股=3-5板非龙头跟风（55188 死亡区域，×0 强制规避）；PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1⑦
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可用→degraded=True 空榜不炸；stk_limit 缺失→连板维度降级（全宇宙按 0 连板处理+notes 留痕，各板块出无龙头注解）；成分股缺失→degraded；trade_date 格式非法→ValueError（调用方契约违例，fail-closed）；个股当日无 K 线→跳过计数留痕
# [TESTS] tests/signal_ashare/test_sector_leader.py
# [A_module] module_id=MOD-SIG-062 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-062 — 板块龙头识别器（SEC-04，92号清单 §7.7；22号 spec §3.1⑦ 步骤① 落码）。

板块内个股角色四档定位（观测先行不接交易）：

| 定位 | 量化特征（22号 §3.1⑦ 原文） | 传导权重 | MVP 日频可得代理 |
|---|---|---|---|
| 龙头 leader | 涨停启动最早+封单最厚+带动后排 | ×1.5 | 板块内连板高度最高且 ≥2 板（涨停启动时间的日频代理），并列按成交额→涨幅→代码定序 |
| 中军 backbone | 市值大+趋势上涨(非连板)+成交额 Top3 | ×1.2 | 成交额板块 Top3（spec 原文口径）+ ret_20d>0 趋势向上 + 当日非连板（市值 200亿+ 无日频字段，成交额作地位代理） |
| 跟风 follower | 龙头涨停后被动拉升+封单不稳 | ×0.8 | 当日红盘（pct_change>0）且非龙头/中军/中位股 |
| 中位股 neutral | 3-5板跟风，分歧率先掉队 | ×0（禁区） | 连板数 ∈[3,5] 且非板块龙头（55188 死亡区域）；其余无特征个股同归 neutral 档 |

评分（2026 社区五维评分框架，MVP 取前三维可得数据）：
  情绪 30%（0.6×连板高度板块内分位 + 0.4×当日涨幅分位）
  + 地位 25%（成交额板块内分位）
  + 形态 20%（0.5×5 日动量分位 + 0.5×20 日动量分位）
  → 0-100 合成（按可用维度权重重归一）；筹码 15%/基本面 10% 权重入 config
  留扩展口（MVP 数据未接入，不参与归一），分位采用中秩（mid-rank）ties 约定
  （对齐 MOD-SIG-060/sector_momentum 口径）。

连板高度推导：收盘封板 = close ≥ stk_limit.limit_up×(1−0.005 网格容差)
（limit_up NULL=无涨跌幅限制 → 非涨停日）；自 trade_date 向回连续封板日数，
当日未封板 → 0（断板即归零）；窗口截断（默认 45 自然日 ≈30 交易日）按窗
长上限留痕。stk_limit 全缺 → 连板维度降级（全宇宙 0 连板，各板块无龙头注解）。

【数据实证口径（2026-08-22 直查 c1_market，可信）】
- kline_daily.pct_change 列全 0 未填充（08-10→08-21 逐日普查 countIf(<>0)=0，
  采集端 DEFAULT 0 从未赋值）→ 当日涨幅由相邻收盘推导（close_t/close_{t-1}−1，
  PIT 安全），不读该列；此数据缺口已留痕待统筹上报采集域。
- sector_constituent 当前有效 593 板块/88,887 成分行（股票多板归属重复计数，
  per-板块分档口径下同一只股可在多个板块分组出现，属设计内）。
- 全宇宙 smoke（08-21）：5,203 股/593 板块，165 板块有龙头；08-21 为普跌日
  （sector_snapshot 广度合计涨跌比 0.43），红盘跟风稀少属数据画像非缺陷。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 个股日 K 窗（kline_daily；涨幅=相邻收盘推导，pct_change 列实证不可用）
#   fields: symbol_canonical/trade_date/close/amount/turnover
# - id: I2
#   name: 涨跌停价窗（stk_limit，连板推导腿）
#   fields: symbol_canonical/trade_date/limit_up
# - id: I3
#   name: 板块成分映射（sector_constituent，SCD-2 时点有效）
#   fields: sector_code/stock_code
# 层: 特征
# - id: F1
#   name_zh: 连板高度
#   formula: 自 trade_date 向回连续收盘封板日数（close≥limit_up×(1−0.005)）
# - id: F2
#   name_zh: 三维辨识度分位
#   formula: 情绪=0.6·midrank(连板)+0.4·midrank(pct_change); 地位=midrank(amount); 形态=0.5·midrank(ret_5d)+0.5·midrank(ret_20d)
# 层: 算法
# - id: A1
#   name_zh: 评分合成
#   desc: score=100×(0.30情绪+0.25地位+0.20形态)/可用权重和；筹码/基本面缺→不入归一
# - id: A2
#   name_zh: 四档划分
#   desc: 龙头=最高连板且≥2(并列→成交额→涨幅→代码); 中位股=3-5板非龙头优先判; 中军=额Top3∧ret20>0∧非连板; 跟风=红盘其余; 余者 neutral
# 层: 输出
# - id: O1
#   name_zh: SectorLeaderBoard
#   intro: trade_date/sectors(per 板块 leader/backbones/followers/neutrals+注解)/n_stocks/degraded/notes；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> F1
# I1,I3 --> F2
# F2 --> A1
# F1,A1 --> A2
# A1,A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "ROLE_BACKBONE",
    "ROLE_FOLLOWER",
    "ROLE_LEADER",
    "ROLE_NEUTRAL",
    "SectorLeaderBoard",
    "SectorLeaderConfig",
    "SectorRoleGroup",
    "StockRoleEntry",
    "identify_sector_leaders",
]

#: 四档角色常量（输出契约字符串）
ROLE_LEADER: Final = "leader"
ROLE_BACKBONE: Final = "backbone"
ROLE_FOLLOWER: Final = "follower"
ROLE_NEUTRAL: Final = "neutral"

# SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值
SQL_LATEST_KLINE_DATE: Final = """
SELECT max(trade_date)
FROM c1_market.kline_daily
WHERE market_type = 'A_share' AND quality_flag = 1
"""

SQL_SECTOR_CONSTITUENTS: Final = """
SELECT sector_code, stock_code
FROM c1_market.sector_constituent
WHERE valid_from <= %(trade_date)s AND (valid_to IS NULL OR valid_to > %(trade_date)s)
"""

SQL_SECTOR_CONSTITUENTS_ONE: Final = """
SELECT sector_code, stock_code
FROM c1_market.sector_constituent
WHERE valid_from <= %(trade_date)s AND (valid_to IS NULL OR valid_to > %(trade_date)s)
  AND sector_code = %(sector)s
"""

SQL_STOCK_KLINE_WINDOW: Final = """
SELECT symbol_canonical, trade_date, close, amount, turnover
FROM c1_market.kline_daily
WHERE market_type = 'A_share' AND quality_flag = 1
  AND trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""

SQL_STK_LIMIT_WINDOW: Final = """
SELECT symbol_canonical, trade_date, limit_up
FROM c1_market.stk_limit
WHERE trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""


# ------------------------------------------------------------------
# 配置与输出容器（frozen dataclass，asdict JSON 可序列化）
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SectorLeaderConfig:
    """龙头识别配置——四档传导权重与阈值（22号 §3.1⑦ 定稿值+2026 社区五维权重）。

    筹码（w_chip）/基本面（w_fundamental）为扩展口：权重入 config 但 MVP 数据
    未接入，不参与归一（备换手/财务数据腿接入后启用，启用即改默认值并补测试）。
    """

    # ── 四档传导权重（22号 §3.1⑦ 定稿：龙头×1.5/中军×1.2/跟风×0.8/中位股×0） ──
    weight_leader: float = 1.5
    weight_backbone: float = 1.2
    weight_follower: float = 0.8
    weight_neutral: float = 0.0
    # ── 五维评分权重（2026 社区框架：情绪30/地位25/形态20/筹码15/基本面10） ──
    w_emotion: float = 0.30
    w_status: float = 0.25
    w_form: float = 0.20
    w_chip: float = 0.15  # 扩展口 MVP 未启用
    w_fundamental: float = 0.10  # 扩展口 MVP 未启用
    emotion_consec_share: float = 0.6  # 情绪维内：连板高度 0.6 + 当日涨幅 0.4
    form_ret5_share: float = 0.5  # 形态维内：5 日动量 0.5 + 20 日动量 0.5
    # ── 四档划分阈值 ──
    leader_min_consec: int = 2  # 龙头最低连板高度（首板辨识度不足不封龙，待实盘标定）
    neutral_consec_min: int = 3  # 中位股连板区间下限（3-5 板跟风=死亡区域）
    neutral_consec_max: int = 5  # 中位股连板区间上限
    backbone_amount_top: int = 3  # 中军成交额板块内 Top N（spec 原文 Top3）
    backbone_min_trend: float = 0.0  # 中军 20 日动量下限（ret_20d 严格大于）
    backbone_max_consec: int = 0  # 中军当日连板状态上限（spec "非连板"严格口径；首板中军归跟风，待标定）
    follower_min_pct: float = 0.0  # 跟风当日涨幅下限（pct_change 严格大于，%）
    # ── 数据窗与容差 ──
    lookback_calendar_days: int = 45  # 查询自然日窗（覆盖 20 日动量+连板推导，长连板截断留痕）
    limit_price_tol: float = 0.005  # 收盘封板价格网格容差（0.01 取整半格，对齐 MOD-SIG-060）
    max_neutral_list: int = 50  # 单板块 neutral 档清单上限（防爆板，超出仅计数）


@dataclass(frozen=True, slots=True)
class StockRoleEntry:
    """个股角色条目（四档清单行，评分+理由链可追溯）。"""

    symbol: str
    sector_code: str
    role: str  # leader/backbone/follower/neutral
    weight: float  # 传导权重（config 四档值透传）
    score: float  # 五维合成评分 0-100（按可用维度归一）
    consec_limit: int  # 连板高度（0=当日未封板）
    amount: float  # 当日成交额（元）
    pct_change: float | None  # 当日涨跌幅（%，相邻收盘推导）；窗口首日无昨收 → None
    ret_5d: float | None  # 5 交易日动量（小数）；样本不足 → None
    ret_20d: float | None  # 20 交易日动量（小数）；样本不足 → None
    reasons: list[str] = field(default_factory=list)  # 分档理由链（中文可审计）


@dataclass(frozen=True, slots=True)
class SectorRoleGroup:
    """单板块四档分组（无龙头板块 leader=None+annotation 注解）。"""

    sector_code: str
    leader: StockRoleEntry | None  # 龙头（None=无龙头板块）
    backbones: list[StockRoleEntry] = field(default_factory=list)  # 中军（≤backbone_amount_top）
    followers: list[StockRoleEntry] = field(default_factory=list)  # 跟风
    neutrals: list[StockRoleEntry] = field(default_factory=list)  # 中位股/无特征（≤max_neutral_list）
    n_neutral_total: int = 0  # neutral 档全量计数（清单截断时 >len(neutrals)）
    annotation: str | None = None  # 板块注解（无龙头原因等）


@dataclass(frozen=True, slots=True)
class SectorLeaderBoard:
    """龙头识别输出契约（T 日盘后计算，观测层消费；不接交易）。"""

    trade_date: str  # 数据日 YYYY-MM-DD
    sectors: list[SectorRoleGroup] = field(default_factory=list)
    n_sectors: int = 0
    n_stocks: int = 0  # 参与分档的个股数（当日有 K 线的成分股）
    degraded: bool = False  # 主数据不可用/查询异常 → True（结果不可用于决策）
    notes: list[str] = field(default_factory=list)  # 降级原因等留痕


# ------------------------------------------------------------------
# 内部辅助（纯函数）
# ------------------------------------------------------------------


def _normalize_date(trade_date: str | date | datetime) -> date:
    """归一化交易日（str 须 YYYY-MM-DD，非法格式抛 ValueError）。"""
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _as_date(v: Any) -> date:
    """CH 日期行值归一（date 原样返回，str 按 YYYY-MM-DD 解析）。"""
    return v if isinstance(v, date) else _normalize_date(v)


def _default_client() -> Any | None:
    """延迟加载默认 CH 客户端（不可用时返回 None，由主入口转 degraded）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，龙头识别降级", exc_info=True)
        return None


def _midrank(sorted_values: list[float], current: float) -> float:
    """中秩分位 = (count(<x) + count(≤x)) / (2n)——并列取平均秩（对齐 MOD-SIG-060 口径）。"""
    n = len(sorted_values)
    if n == 0:
        return 0.0
    lo, hi = 0, n
    while lo < hi:  # bisect_left
        mid = (lo + hi) // 2
        if sorted_values[mid] < current:
            lo = mid + 1
        else:
            hi = mid
    left = lo
    lo, hi = left, n
    while lo < hi:  # bisect_right（从左边界起）
        mid = (lo + hi) // 2
        if sorted_values[mid] <= current:
            lo = mid + 1
        else:
            hi = mid
    return (left + lo) / (2.0 * n)


@dataclass(frozen=True, slots=True)
class _StockMetrics:
    """个股窗口度量（内部中间态）。"""

    symbol: str
    consec_limit: int
    amount: float
    pct_change: float | None  # 当日涨幅（%，相邻收盘推导）；窗口首日无昨收 → None
    turnover: float
    ret_5d: float | None
    ret_20d: float | None


def _consec_limit_height(
    series: list[tuple[date, float]],
    limit_map: dict[date, float | None],
    trade_date: date,
    tol: float,
) -> int:
    """连板高度：自 trade_date 向回连续收盘封板日数。

    封板判定 = close ≥ limit_up×(1−tol)；limit_up 缺失/NULL（无涨跌幅限制）
    → 非涨停日（断板）；当日未封板 → 0。series 须 (日期, 收盘) 升序且 ≤trade_date。
    """
    height = 0
    for d, close in reversed(series):
        if d > trade_date:
            continue
        limit_up = limit_map.get(d)
        if limit_up is None or close < limit_up * (1 - tol):
            break
        height += 1
    return height


def _build_metrics(
    kline_rows: list[tuple],
    limit_rows: list[tuple],
    universe: set[str],
    trade_date: date,
    cfg: SectorLeaderConfig,
) -> tuple[dict[str, _StockMetrics], int]:
    """kline+stk_limit 行 → {symbol: 度量}（仅宇宙内且当日有 K 线者）+ 跳过计数。

    当日涨幅由相邻收盘推导（pct_change 列 2026-08-22 实证全 0 未填充，不用）；
    同 symbol 同日重复行按 date 去重（末行有效）——连板计数对重复日敏感（防双计数）。
    """
    by_symbol: dict[str, dict[date, tuple[float, float, float]]] = {}
    for row in kline_rows:
        sym = str(row[0])
        if sym not in universe:
            continue
        by_symbol.setdefault(sym, {})[_as_date(row[1])] = (
            float(row[2] or 0.0),  # close
            float(row[3] or 0.0),  # amount
            float(row[4] or 0.0),  # turnover
        )
    limits: dict[str, dict[date, float | None]] = {}
    for row in limit_rows:
        sym = str(row[0])
        if sym not in universe:
            continue
        limits.setdefault(sym, {})[_as_date(row[1])] = float(row[2]) if row[2] is not None else None

    metrics: dict[str, _StockMetrics] = {}
    n_skipped = 0
    for sym, day_map in by_symbol.items():
        days = sorted(d for d in day_map if d <= trade_date)
        if not days or days[-1] != trade_date:
            n_skipped += 1  # 当日无 K 线（停牌/未采集）→ 不参与当日分档
            continue
        closes = [(dd, day_map[dd][0]) for dd in days]
        consec = _consec_limit_height(closes, limits.get(sym, {}), trade_date, cfg.limit_price_tol)
        today_close = day_map[days[-1]][0]
        pct_change: float | None = None
        if len(days) >= 2 and day_map[days[-2]][0] > 0:
            pct_change = round((today_close / day_map[days[-2]][0] - 1.0) * 100.0, 4)
        ret_5d = today_close / day_map[days[-6]][0] - 1.0 if len(days) >= 6 and day_map[days[-6]][0] > 0 else None
        ret_20d = today_close / day_map[days[-21]][0] - 1.0 if len(days) >= 21 and day_map[days[-21]][0] > 0 else None
        metrics[sym] = _StockMetrics(
            symbol=sym,
            consec_limit=consec,
            amount=day_map[days[-1]][1],
            pct_change=pct_change,
            turnover=day_map[days[-1]][2],
            ret_5d=round(ret_5d, 6) if ret_5d is not None else None,
            ret_20d=round(ret_20d, 6) if ret_20d is not None else None,
        )
    return metrics, n_skipped


def _score_universe(metrics: dict[str, _StockMetrics], cfg: SectorLeaderConfig) -> dict[str, float]:
    """板块内三维分位合成 0-100 评分（中秩 ties；缺维度按可用权重重归一）。"""
    symbols = sorted(metrics)
    if not symbols:
        return {}
    consecs = sorted(float(metrics[s].consec_limit) for s in symbols)
    pcts = sorted(m.pct_change for s in symbols if (m := metrics[s]).pct_change is not None)
    amounts = sorted(metrics[s].amount for s in symbols)
    ret5s = sorted(m.ret_5d for s in symbols if (m := metrics[s]).ret_5d is not None)
    ret20s = sorted(m.ret_20d for s in symbols if (m := metrics[s]).ret_20d is not None)

    scores: dict[str, float] = {}
    for sym in symbols:
        m = metrics[sym]
        consec_rank = _midrank(consecs, float(m.consec_limit))
        # 情绪维：连板高度主+当日涨幅辅；涨幅不可得（窗口首日）→ 仅用连板分位
        if m.pct_change is not None and pcts:
            emotion = cfg.emotion_consec_share * consec_rank + (1.0 - cfg.emotion_consec_share) * _midrank(
                pcts, m.pct_change
            )
        else:
            emotion = consec_rank
        status = _midrank(amounts, m.amount)
        parts: list[tuple[float, float]] = [  # (权重, 维度分位)
            (cfg.w_emotion, emotion),
            (cfg.w_status, status),
        ]
        form_parts: list[tuple[float, float]] = []
        if m.ret_5d is not None and ret5s:
            form_parts.append((cfg.form_ret5_share, _midrank(ret5s, m.ret_5d)))
        if m.ret_20d is not None and ret20s:
            form_parts.append((1.0 - cfg.form_ret5_share, _midrank(ret20s, m.ret_20d)))
        if form_parts:
            w_sum = sum(w for w, _ in form_parts)
            form = sum(w * v for w, v in form_parts) / w_sum if w_sum > 0 else 0.0
            parts.append((cfg.w_form, form))
        # 筹码/基本面扩展口：MVP 数据未接入，不参与归一（config 权重留痕）
        w_total = sum(w for w, _ in parts)
        scores[sym] = round(100.0 * sum(w * v for w, v in parts) / w_total, 2) if w_total > 0 else 0.0
    return scores


def _assign_sector_roles(
    sector_code: str,
    members: list[_StockMetrics],
    scores: dict[str, float],
    cfg: SectorLeaderConfig,
) -> SectorRoleGroup:
    """单板块四档划分（定序确定性：连板→成交额→涨幅→代码升序）。"""
    ordered = sorted(
        members,
        key=lambda m: (
            -m.consec_limit,
            -m.amount,
            -(m.pct_change if m.pct_change is not None else float("-inf")),
            m.symbol,
        ),
    )

    def _entry(m: _StockMetrics, role: str, weight: float, reasons: list[str]) -> StockRoleEntry:
        return StockRoleEntry(
            symbol=m.symbol,
            sector_code=sector_code,
            role=role,
            weight=weight,
            score=scores.get(m.symbol, 0.0),
            consec_limit=m.consec_limit,
            amount=m.amount,
            pct_change=m.pct_change,
            ret_5d=m.ret_5d,
            ret_20d=m.ret_20d,
            reasons=reasons,
        )

    # 龙头：最高连板且 ≥leader_min_consec（并列按定序链取首）
    leader_entry: StockRoleEntry | None = None
    annotation: str | None = None
    if ordered and ordered[0].consec_limit >= cfg.leader_min_consec:
        top = ordered[0]
        leader_entry = _entry(
            top,
            ROLE_LEADER,
            cfg.weight_leader,
            [f"板块内最高连板 {top.consec_limit} 板（≥{cfg.leader_min_consec} 辨识度门槛）"],
        )
    else:
        max_consec = ordered[0].consec_limit if ordered else 0
        annotation = f"无龙头板块：最高连板 {max_consec} 板 <{cfg.leader_min_consec} 辨识度门槛，不强行封龙"

    backbones: list[StockRoleEntry] = []
    followers: list[StockRoleEntry] = []
    neutrals: list[StockRoleEntry] = []
    n_neutral_total = 0
    amount_rank = {m.symbol: i + 1 for i, m in enumerate(sorted(members, key=lambda x: (-x.amount, x.symbol)))}

    for m in ordered:
        if leader_entry is not None and m.symbol == leader_entry.symbol:
            continue
        if cfg.neutral_consec_min <= m.consec_limit <= cfg.neutral_consec_max:
            n_neutral_total += 1
            if len(neutrals) < cfg.max_neutral_list:
                neutrals.append(
                    _entry(
                        m,
                        ROLE_NEUTRAL,
                        cfg.weight_neutral,
                        [
                            f"中位股禁区：{m.consec_limit} 板非龙头跟风"
                            f"（∈[{cfg.neutral_consec_min},{cfg.neutral_consec_max}] 死亡区域，×0 规避）"
                        ],
                    )
                )
            continue
        if (
            amount_rank[m.symbol] <= cfg.backbone_amount_top
            and m.ret_20d is not None
            and m.ret_20d > cfg.backbone_min_trend
            and m.consec_limit <= cfg.backbone_max_consec
        ):
            backbones.append(
                _entry(
                    m,
                    ROLE_BACKBONE,
                    cfg.weight_backbone,
                    [
                        f"中军：成交额板块 Top{cfg.backbone_amount_top}"
                        f"（第 {amount_rank[m.symbol]}）+ 20 日动量 {m.ret_20d:+.1%} 趋势向上 + 非连板"
                    ],
                )
            )
            continue
        if m.pct_change is not None and m.pct_change > cfg.follower_min_pct:
            followers.append(
                _entry(
                    m,
                    ROLE_FOLLOWER,
                    cfg.weight_follower,
                    [f"跟风：当日红盘 {m.pct_change:+.2f}% 被动拉升（非龙头/中军/中位股）"],
                )
            )
            continue
        n_neutral_total += 1
        if len(neutrals) < cfg.max_neutral_list:
            neutrals.append(_entry(m, ROLE_NEUTRAL, cfg.weight_neutral, ["无龙头/中军/跟风特征（×0）"]))

    return SectorRoleGroup(
        sector_code=sector_code,
        leader=leader_entry,
        backbones=backbones,
        followers=followers,
        neutrals=neutrals,
        n_neutral_total=n_neutral_total,
        annotation=annotation,
    )


def _degraded_board(trade_date: str, reason: str) -> SectorLeaderBoard:
    """降级空榜（主数据不可用/查询异常，notes 留痕不炸）。"""
    return SectorLeaderBoard(trade_date=trade_date, degraded=True, notes=[reason])


# ------------------------------------------------------------------
# 主接口
# ------------------------------------------------------------------


def identify_sector_leaders(
    trade_date: str | date | datetime | None = None,
    sector: str | None = None,
    ch_client: Any | None = None,
    config: SectorLeaderConfig | None = None,
) -> SectorLeaderBoard:
    """主入口：板块内个股角色四档识别（22号 §3.1⑦ 步骤①，观测先行不接交易）。

    Args:
        trade_date: 数据日；None 时取 kline_daily 最新数据日（PIT 数据日口径）。
        sector: 单板块代码（如 "881319.SH"）；None 时全板块扫描。
        ch_client: clickhouse-driver 鸭子类型（execute(sql, params) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client，不可得 → degraded。
        config: 阈值与四档权重配置（None 用默认 22号 §3.1⑦ 定稿值）。

    Returns:
        SectorLeaderBoard；主数据（成分股/kline_daily）缺失或查询异常 → degraded=True
        空榜不炸；stk_limit 缺失 → 连板维度独立降级（全宇宙 0 连板+无龙头注解）。
    """
    cfg = config or SectorLeaderConfig()

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        d = _normalize_date(trade_date) if trade_date is not None else date.today()
        return _degraded_board(d.isoformat(), "ch_client 未注入且默认客户端不可用")

    if trade_date is None:
        try:
            latest = client.execute(SQL_LATEST_KLINE_DATE, {})
        except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
            return _degraded_board("unknown", f"最新 K 线数据日查询异常: {e!r}")
        if not latest or latest[0][0] is None:
            return _degraded_board("unknown", "kline_daily 无任何日 K 数据")
        d = _as_date(latest[0][0])
    else:
        d = _normalize_date(trade_date)
    date_str = d.isoformat()

    # ── 成分映射（SCD-2 时点过滤；单板块/全宇宙两路 SQL 常量） ──
    # 按 (sector,stock) 去重：client.execute 无 FINAL 注入，ReplacingMergeTree
    # 预合并重复行会导致同股在同板块分档清单出现两次（2026-08-22 实盘 smoke 抓出）。
    constituents: dict[str, list[str]] = {}
    try:
        if sector is not None:
            rows = client.execute(SQL_SECTOR_CONSTITUENTS_ONE, {"trade_date": d, "sector": sector})
        else:
            rows = client.execute(SQL_SECTOR_CONSTITUENTS, {"trade_date": d})
        cons_sets: dict[str, set[str]] = {}
        for row in rows:
            cons_sets.setdefault(str(row[0]), set()).add(str(row[1]))
        constituents = {code: sorted(syms) for code, syms in cons_sets.items()}
    except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
        return _degraded_board(date_str, f"sector_constituent 查询异常: {e!r}")
    if not constituents:
        target = f"板块 {sector}" if sector is not None else "全宇宙"
        return _degraded_board(date_str, f"{date_str} {target} 无有效成分股（SCD-2 时点过滤后为空）")

    universe = {sym for members in constituents.values() for sym in members}

    # ── 个股日 K 窗（主数据） ──
    start = d - timedelta(days=cfg.lookback_calendar_days)
    try:
        kline_rows = client.execute(SQL_STOCK_KLINE_WINDOW, {"trade_date": d, "start_date": start})
    except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
        return _degraded_board(date_str, f"kline_daily 查询异常: {e!r}")
    if not kline_rows:
        return _degraded_board(date_str, f"{date_str} 个股 K 线窗内无数据（非交易日或未采集）")

    # ── stk_limit 连板推导腿（独立降级：缺失 → 全宇宙 0 连板） ──
    notes: list[str] = []
    try:
        limit_rows = client.execute(SQL_STK_LIMIT_WINDOW, {"trade_date": d, "start_date": start})
        if not limit_rows:
            notes.append("stk_limit 窗内无数据，连板维度降级（全宇宙按 0 连板处理）")
    except Exception as e:  # noqa: BLE001 — 连板腿缺失独立降级不累及主榜
        notes.append(f"stk_limit 查询异常，连板维度降级（全宇宙按 0 连板处理）: {e!r}")
        limit_rows = []

    metrics, n_skipped = _build_metrics(kline_rows, limit_rows, universe, d, cfg)
    if n_skipped:
        notes.append(f"{n_skipped} 只成分股当日无 K 线（停牌/未采集），不参与分档")
    if not metrics:
        return _degraded_board(date_str, f"{date_str} 宇宙内个股当日均无 K 线")

    # ── per 板块评分与四档划分（分位宇宙=本板块当日可评分成员） ──
    sectors: list[SectorRoleGroup] = []
    for code in sorted(constituents):
        members = [metrics[sym] for sym in constituents[code] if sym in metrics]
        if not members:
            sectors.append(
                SectorRoleGroup(
                    sector_code=code,
                    leader=None,
                    annotation="板块成员当日均无 K 线（停牌/未采集）",
                )
            )
            continue
        scores = _score_universe({m.symbol: m for m in members}, cfg)
        sectors.append(_assign_sector_roles(code, members, scores, cfg))

    return SectorLeaderBoard(
        trade_date=date_str,
        sectors=sectors,
        n_sectors=len(sectors),
        n_stocks=len(metrics),
        degraded=False,
        notes=notes,
    )
