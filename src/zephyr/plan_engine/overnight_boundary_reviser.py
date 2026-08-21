# [BLUEPRINT] MOD-PLAN-004 | 待统筹登记（44号 §4 M3-①a⑦⑧ 盘前包）
# [MODULE] zephyr.plan_engine.overnight_boundary_reviser
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.data.ch_reader（默认 CH 读取通道）; zephyr.data.table_registry（表名解析）
# [CONSUMERS] 待 M3-③ scenario_planner 消费（44号 §4 盘前多情景方案）；prediction_log 落库（M4-②，后续波次接）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] fail-open 不阻塞主流程; 单通道异常=该通道降级不炸整体; calendar_event 空表静默跳过+留痕; 输出纯 dataclass JSON 可序列化
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单通道异常→该通道降级(None/缺省值)+trace 留痕; 整体不抛异常（仅 trade_date 非法抛 ValueError）
# [TESTS] tests/plan_engine/test_overnight_boundary_reviser.py
# [A_module] module_id=MOD-PLAN-004 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

OvernightBoundaryReviser — 盘前隔夜边界修正器 (MOD-PLAN-004)

44号 §4 M3 盘前综合预判的"今晨修正"计算核心。MOD-PLAN-002 当前只"加载昨夜边界"
不修正，本模块提供"用外盘隔夜+盘后资金面+事件日历修正边界档位"的增量载体。

三通道（44号 §9.6/§9.10/§9.12 为设计真源）：
    - M3-①a 外盘通道（§9.6）：us_index 最新两条收盘算隔夜涨跌幅，
      gap_adj = w1·ret_SPX + w2·ret_NDX（默认 0.2/0.3，config 化）。
      实证缺陷：表 index_code 列有空值——按"最新可得序列"取数，无法区分
      标普/纳指时退化为单序列美股代理并标 gap_adj_degraded=True。
    - M3-⑦ 盘后资金面四件套（§9.10）：margin_delta（融资净买入 20 日 z-score）/
      mf_net（全市场主力净流入强度代理）/bt_premium（大宗交易加权折溢价率）/
      etf_flow（候选缺省=0，权重重归一）。fund_score 与 gap_adj 同向→确认；
      反向且 |fund_score|>1σ→否决半档。
    - M3-⑧ 事件日历联动（§9.12）：高影响事件夜敏感度升半档（1.0% 即触发整档）；
      期权到期日 m1_threshold_scale=0.8；交割周 basis_weight_scale=0.5；
      A50 交割日（calendar_event 暂无此类，按规则自算标注）敏感度升半档
      +A50 通道权重上调 0.45。fail-open 铁律：空表/查询失败→静默跳过+留痕。

修正规则（§9.6）：
    |gap_adj| < 0.5%        → 不变档
    0.5% ≤ |gap_adj| < 1.5% → ±半档（加仓上限 ±20%）
    |gap_adj| ≥ 1.5% 或 BS-005 触发 → ±一档（保守/正常/进攻整体迁移）

不做什么：不直接改 TomorrowBoundary（消费方 M3-③ 负责应用 final_shift）/
         不做方向点预测（90号 §7 裁定，只画栏杆不算命）/不碰既有三文件。

依据: 44_premarket_intraday_decision_upgrade §4 + §9.6 + §9.10 + §9.12
SSoT: depgraph MOD-PLAN-004（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: trade_date + CH 数据（us_index/margin_trading/money_flow/block_trade/calendar_event）+ bs005_triggered
# 特征: gap_adj（外盘隔夜加权）/ fund_score（资金面四件套 z 合成）/ event_flags（事件日历联动）
# 算法: 外盘分档 → 资金面确认/否决（×1.0 / 半档）→ 事件敏感度缩放 → final_shift∈{-1,-0.5,0,+0.5,+1}
# 输出: OvernightRevision（纯 dataclass，JSON 可序列化，供 prediction_log 落库）

"""

from __future__ import annotations

import datetime
import logging
import math
import statistics
from dataclasses import asdict, dataclass
from typing import Any, Callable, Final

log = logging.getLogger(__name__)

# ── 常量（44号 §9.6/§9.10/§9.12 参数默认值，全部可经 OvernightRevisionConfig 覆盖）──

GAP_WEIGHT_SPX: Final = 0.2  # 标普500 通道权重（§9.6 w1）
GAP_WEIGHT_NDX: Final = 0.3  # 纳指 通道权重（§9.6 w2）
GAP_THRESHOLD_HALF: Final = 0.005  # 半档触发阈值 0.5%
GAP_THRESHOLD_FULL: Final = 0.015  # 整档触发阈值 1.5%
EVENT_FULL_THRESHOLD: Final = 0.010  # 高影响事件夜整档触发阈值降至 1.0%（§9.12 敏感度升半档）

FUND_WEIGHT_MARGIN: Final = 0.4  # 融资净买入 z 权重（§9.10，华泰三资金之首）
FUND_WEIGHT_MF_NET: Final = 0.3  # 主力净流入 z 权重
FUND_WEIGHT_BT_PREMIUM: Final = 0.2  # 大宗折溢价 z 权重
FUND_WEIGHT_ETF: Final = 0.1  # ETF 净申购 z 权重（候选，缺省=0 时权重重归一）
FUND_VETO_SIGMA: Final = 1.0  # 资金面否决阈值 |fund_score| > 1σ（§9.10）
VETO_HALF_STEP: Final = 0.5  # 否决半档=幅度减 0.5 档（保持 final_shift 落在五档集合内）

ZSCORE_WINDOW: Final = 20  # 20 日 z-score 窗口（§9.10/项目因子归一惯例）
MIN_HISTORY_FOR_Z: Final = 5  # 不足 5 个历史点该分量降级（防小样本 z 失真）

M1_THRESHOLD_SCALE_OPTION_EXPIRY: Final = 0.8  # 期权到期日 M1 信号阈值缩放（§9.12/§9.9）
BASIS_WEIGHT_SCALE_DELIVERY_WEEK: Final = 0.5  # 交割周基差信号降权（§9.12/§9.8）
A50_DELIVERY_CHANNEL_WEIGHT: Final = 0.45  # A50 交割日 A50 通道权重上调（§9.12）

# 高影响事件类型（事件夜外盘波动放大约 1.5-2×，§9.12）
HIGH_IMPACT_EVENT_TYPES: Final = frozenset({"fomc_meeting", "us_cpi_release", "major_meeting"})

# us_index 表 index_code 取值（tickflow_provider：SPX/DJI/IXIC，ETF 替代真实指数）
_US_INDEX_SPX_CODES: Final = frozenset({"SPX", "SPY", "SPY.US"})
_US_INDEX_NDX_CODES: Final = frozenset({"IXIC", "NDX", "QQQ", "QQQ.US"})

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，与 ch_reader 同约定）
_SQL_US_INDEX = (
    "SELECT trade_date, index_code, close FROM {table} FINAL "
    "WHERE trade_date <= toDate('{trade_date}') ORDER BY trade_date DESC LIMIT 400"
)
_SQL_MARGIN = (
    "SELECT trade_date, sum(toFloat64(margin_buy) - toFloat64(margin_repay)) AS net_buy "
    "FROM {table} FINAL WHERE trade_date < toDate('{trade_date}') "
    "GROUP BY trade_date ORDER BY trade_date DESC LIMIT {limit}"
)
_SQL_MONEY_FLOW = (
    "SELECT trade_date, avg(toFloat64(main_net_inflow_pct)) AS avg_pct "
    "FROM {table} FINAL WHERE trade_date < toDate('{trade_date}') "
    "GROUP BY trade_date ORDER BY trade_date DESC LIMIT {limit}"
)
# 大宗折溢价：JOIN 用 USING 无别名写法（ch_reader.inject_final 注入 FINAL 后语法仍合法，
# 与 akshare_provider #198 同约定）；close 缺失（LEFT JOIN 未命中）经 sumIf 剔除
_SQL_BLOCK_PREMIUM = (
    "SELECT trade_date, "
    "sumIf((toFloat64(price) - toFloat64(close)) / toFloat64(close) * toFloat64(amount), toFloat64(close) > 0) "
    "/ sumIf(toFloat64(amount), toFloat64(close) > 0) AS premium "
    "FROM {bt_table} LEFT JOIN {kline_table} USING (symbol, trade_date) "
    "WHERE trade_date < toDate('{trade_date}') AND toFloat64(amount) > 0 "
    "GROUP BY trade_date ORDER BY trade_date DESC LIMIT {limit}"
)
_SQL_CALENDAR = (
    "SELECT event_date, event_type FROM {table} FINAL "
    "WHERE event_date BETWEEN toDate('{win_start}') AND toDate('{win_end}')"
)


def _parse_tsv(tsv: str, ncols: int) -> list[list[str]]:
    """把 ch_reader.query 返回的 TSV 字符串解析成行列表（ncols 不足跳过该行）。"""
    if not tsv or not tsv.strip():
        return []
    rows: list[list[str]] = []
    for line in tsv.strip().split("\n"):
        vals = line.rstrip("\r").split("\t")
        if len(vals) >= ncols:
            rows.append(vals)
    return rows


def _safe_float(v: Any) -> float | None:
    """安全转 float；失败/NaN/Inf 返回 None（区别于 0.0，供降级判定）。"""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _zscore(latest: float, history: list[float]) -> float | None:
    """20 日 z-score：z = (latest - mean(hist)) / pstdev(hist)。

    历史点不足 MIN_HISTORY_FOR_Z 或标准差为 0 → 返回 None（该分量降级）。
    """
    if len(history) < MIN_HISTORY_FOR_Z:
        return None
    std = statistics.pstdev(history)
    if std <= 0:
        return None
    return (latest - statistics.fmean(history)) / std


def _a50_delivery_day(year: int, month: int) -> datetime.date:
    """富时 A50 期货交割日：每月倒数第 2 个工作日（SGX 口径 Mon-Fri，§9.12 自算规则）。

    calendar_event 表暂无 a50_futures_delivery 类（P0-4② 挂账），本函数按规则自算标注。
    """
    if month == 12:
        d = datetime.date(year, 12, 31)
    else:
        d = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    count = 0
    while True:
        if d.weekday() < 5:
            count += 1
            if count == 2:
                return d
        d -= datetime.timedelta(days=1)


def _next_business_day(d: datetime.date) -> datetime.date:
    """下一个工作日（Mon-Fri 口径，与 A50 自算规则一致）。"""
    nxt = d + datetime.timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += datetime.timedelta(days=1)
    return nxt


# ── 配置契约（44号 §9 全部参数 config 化，默认值取设计真源口径）──


@dataclass(frozen=True)
class OvernightRevisionConfig:
    """盘前隔夜修正配置（全参数可调，默认值=44号设计真源口径）。"""

    gap_weight_spx: float = GAP_WEIGHT_SPX
    gap_weight_ndx: float = GAP_WEIGHT_NDX
    gap_threshold_half: float = GAP_THRESHOLD_HALF
    gap_threshold_full: float = GAP_THRESHOLD_FULL
    event_full_threshold: float = EVENT_FULL_THRESHOLD
    fund_weight_margin: float = FUND_WEIGHT_MARGIN
    fund_weight_mf_net: float = FUND_WEIGHT_MF_NET
    fund_weight_bt_premium: float = FUND_WEIGHT_BT_PREMIUM
    fund_weight_etf: float = FUND_WEIGHT_ETF
    fund_veto_sigma: float = FUND_VETO_SIGMA
    zscore_window: int = ZSCORE_WINDOW
    high_impact_window_days: int = 1  # 高影响事件夜窗口：事件日∈[今日-N, 今日]
    enable_a50_channel: bool = False  # A50 夜盘通道预留接口（§9.6 w3，数据源未接入默认关闭）
    enable_china_concept_channel: bool = False  # 中概通道预留接口（§9.6 w4，默认关闭）
    etf_flow_z: float | None = None  # ETF 净申购 z 外部注入位（候选；None=缺省 0 且权重重归一）


DEFAULT_CONFIG: Final = OvernightRevisionConfig()


# ── 输出契约（供 M3-③ scenario_planner 消费 + prediction_log 落库）──


@dataclass(frozen=True)
class OvernightRevision:
    """盘前隔夜边界修正结果（MOD-PLAN-004 产出，JSON 可序列化）。

    final_shift 档位修正：-1/-0.5/0/+0.5/+1（保守/正常/进攻整体迁移的档位增量，
    由消费方 M3-③ 应用到基线边界档位；本模块不直接改 TomorrowBoundary）。
    """

    date: str  # 交易日（ISO）
    gap_adj: float | None  # 外盘隔夜加权修正系数（None=外盘通道无数据）
    gap_adj_degraded: bool  # us_index 符号空值缺陷退化为单序列代理
    fund_score: float | None  # 资金面四件套合成（None=四件全无数据）
    fund_detail: dict[str, Any]  # 各分量原值/z 值/启用与降级留痕
    event_flags: dict[str, Any]  # 事件日历命中标记（含 A50 自算标注）
    sensitivity_scale: float  # 敏感度缩放（1.0=正常 / 0.5=事件夜升半档，语义标记）
    final_shift: float  # 最终档位修正 {-1, -0.5, 0, +0.5, +1}
    m1_threshold_scale: float  # M1 信号阈值缩放（期权到期日=0.8，否则 1.0）
    basis_weight_scale: float  # 基差信号权重缩放（交割周=0.5，否则 1.0）
    a50_channel_weight: float | None  # A50 通道当日权重（交割日=0.45；通道默认关闭=None）
    reasons: list[str]  # 决策理由链（留痕）
    trace: dict[str, Any]  # 通道状态留痕（ok/degraded/skipped/error + 数据日期）

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（prediction_log 落库契约）。"""
        return asdict(self)


# ── 盘前隔夜边界修正器 ──


class OvernightBoundaryReviser:
    """盘前隔夜边界修正器（MOD-PLAN-004）。

    数据经 ch_client 注入（测试 mock/离线）；未注入时走项目默认 CH 通道
    （zephyr.data.ch_reader.query）。任何单通道异常=该通道降级不炸整体。
    """

    def __init__(
        self,
        ch_client: Callable[[str], str] | None = None,
        config: OvernightRevisionConfig | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._ch = ch_client  # None → 查询时走 ch_reader.query（惰性解析，离线可导入）

    # ── 基础设施 ──────────────────────────────────────────────────────────

    @staticmethod
    def _table(category_id: str, fallback: str) -> str:
        """按 category_id 解析全限定表名；注册表不可用降级 fallback（fail-open）。"""
        try:
            from zephyr.data.table_registry import get_registry

            return get_registry().table(category_id)
        except Exception as exc:  # noqa: BLE001 — fail-open：表名解析失败不阻塞主流程
            log.warning("表名解析失败 %s，降级 %s: %s", category_id, fallback, exc)
            return fallback

    def _query(self, sql: str, channel: str, trace: dict[str, Any]) -> str:
        """执行 CH 查询（自动注入 FINAL）；异常→通道降级空串+留痕。"""
        try:
            if self._ch is not None:
                return self._ch(sql)
            from zephyr.data import ch_reader

            return ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open：单通道异常不炸整体
            log.warning("通道 %s 查询异常，降级跳过: %s", channel, exc)
            trace["channels"][channel] = f"error:{exc}"
            return ""

    # ── M3-①a 外盘通道（§9.6）────────────────────────────────────────────

    def _compute_gap_adj(self, trade_date: str, trace: dict[str, Any]) -> tuple[float | None, bool, list[str]]:
        """外盘隔夜加权修正系数（us_index 最新两条收盘，符号空值退化单序列代理）。"""
        reasons: list[str] = []
        table = self._table("market_us_index", "c1_market.us_index")
        tsv = self._query(_SQL_US_INDEX.format(table=table, trade_date=trade_date), "us_index", trace)
        rows = _parse_tsv(tsv, 3)
        if not rows:
            trace["channels"].setdefault("us_index", "skipped:no_data")
            reasons.append("外盘通道无数据，跳过（fail-open）")
            return None, False, reasons

        # 按 index_code 分组取各序列最新两条收盘（最新可得序列口径）
        series: dict[str, list[tuple[str, float]]] = {}
        for d, code, close_s in rows:
            close = _safe_float(close_s)
            code = (code or "").strip()
            if close is None or close <= 0 or not code:
                continue  # 实证缺陷：symbol/index_code 空值行剔除
            series.setdefault(code, []).append((d, close))
        for code in series:
            series[code] = sorted(series[code], key=lambda x: x[0], reverse=True)[:2]

        def _ret(closes: list[tuple[str, float]]) -> float | None:
            if len(closes) < 2 or closes[1][1] <= 0:
                return None
            return (closes[0][1] - closes[1][1]) / closes[1][1]

        def _first_ret(codes: frozenset[str]) -> float | None:
            for c in series:
                if c in codes:
                    r = _ret(series[c])
                    if r is not None:
                        return r
            return None

        ret_spx = _first_ret(_US_INDEX_SPX_CODES)
        ret_ndx = _first_ret(_US_INDEX_NDX_CODES)

        cfg = self._config
        if ret_spx is not None and ret_ndx is not None:
            gap = cfg.gap_weight_spx * ret_spx + cfg.gap_weight_ndx * ret_ndx
            trace["channels"]["us_index"] = "ok"
            reasons.append(f"外盘双序列：ret_SPX={ret_spx:+.4f} ret_NDX={ret_ndx:+.4f} → gap_adj={gap:+.4f}")
            return gap, False, reasons

        # 退化：无法区分标普/纳指（符号空值缺陷/序列缺失）→ 单序列美股代理
        proxy = next((r for c in sorted(series) for r in [_ret(series[c])] if r is not None), None)
        if proxy is None:
            trace["channels"]["us_index"] = "skipped:insufficient_closes"
            reasons.append("外盘序列收盘不足两条，跳过（fail-open）")
            return None, False, reasons
        trace["channels"]["us_index"] = "degraded:single_series_proxy"
        reasons.append(f"符号无法区分标普/纳指，退化单序列代理 ret={proxy:+.4f}（degraded=True）")
        return proxy, True, reasons

    # ── M3-⑦ 盘后资金面四件套（§9.10）────────────────────────────────────

    def _compute_fund_score(self, trade_date: str, trace: dict[str, Any]) -> tuple[float | None, dict[str, Any]]:
        """资金面四件套合成 fund_score（缺数据分量剔除+权重重归一，etf_flow 候选缺省=0）。"""
        cfg = self._config
        detail: dict[str, Any] = {"components_used": [], "components_skipped": {}}
        z_parts: dict[str, tuple[float, float]] = {}  # name → (weight, z)

        # ── margin_delta：融资净买入(T-1) 的 20 日 z-score ──
        table = self._table("market_margin_trading", "c1_market.margin_trading")
        tsv = self._query(
            _SQL_MARGIN.format(table=table, trade_date=trade_date, limit=cfg.zscore_window + 1),
            "margin_trading",
            trace,
        )
        rows = _parse_tsv(tsv, 2)
        nets = [v for _, s in rows if (v := _safe_float(s)) is not None]
        if nets:
            detail["margin_delta"] = nets[0]
            z = _zscore(nets[0], nets[1:])
            if z is not None:
                z_parts["margin"] = (cfg.fund_weight_margin, z)
                detail["z_margin_delta"] = z
                detail["components_used"].append("margin_delta")
                trace["channels"].setdefault("margin_trading", "ok")
            else:
                detail["components_skipped"]["margin_delta"] = "history<min_or_zero_std"
                trace["channels"].setdefault("margin_trading", "degraded:insufficient_history")
        else:
            detail["components_skipped"]["margin_delta"] = "no_data"
            trace["channels"].setdefault("margin_trading", "skipped:no_data")

        # ── mf_net：全市场主力净流入(T-1)/成交额 代理（avg(main_net_inflow_pct)）──
        table = self._table("market_money_flow", "c1_market.money_flow")
        tsv = self._query(
            _SQL_MONEY_FLOW.format(table=table, trade_date=trade_date, limit=cfg.zscore_window + 1),
            "money_flow",
            trace,
        )
        rows = _parse_tsv(tsv, 2)
        pcts = [v for _, s in rows if (v := _safe_float(s)) is not None]
        if pcts:
            detail["mf_net"] = pcts[0]
            z = _zscore(pcts[0], pcts[1:])
            if z is not None:
                z_parts["mf_net"] = (cfg.fund_weight_mf_net, z)
                detail["z_mf_net"] = z
                detail["components_used"].append("mf_net")
                trace["channels"].setdefault("money_flow", "ok")
            else:
                detail["components_skipped"]["mf_net"] = "history<min_or_zero_std"
                trace["channels"].setdefault("money_flow", "degraded:insufficient_history")
        else:
            detail["components_skipped"]["mf_net"] = "no_data"
            trace["channels"].setdefault("money_flow", "skipped:no_data")

        # ── bt_premium：大宗交易加权折溢价率(T-1) 的 20 日 z-score ──
        # （block_trade ⋈ kline_daily 收盘价，(成交价-收盘)/收盘 按成交额加权）
        bt_premium, z_bt = self._compute_bt_premium(trade_date, trace)
        if bt_premium is not None and z_bt is not None:
            detail["bt_premium"] = bt_premium
            detail["z_bt_premium"] = z_bt
            z_parts["bt_premium"] = (cfg.fund_weight_bt_premium, z_bt)
            detail["components_used"].append("bt_premium")
        else:
            detail["components_skipped"]["bt_premium"] = (
                "no_data_or_no_close" if bt_premium is None else "history<min_or_zero_std"
            )

        # ── etf_flow：候选缺省=0（权重重归一）；外部注入时启用 ──
        if cfg.etf_flow_z is not None:
            z_parts["etf_flow"] = (cfg.fund_weight_etf, cfg.etf_flow_z)
            detail["z_etf_flow"] = cfg.etf_flow_z
            detail["components_used"].append("etf_flow")
        else:
            detail["etf_flow"] = 0.0
            detail["components_skipped"]["etf_flow"] = "candidate_default_zero"

        if not z_parts:
            return None, detail
        w_sum = sum(w for w, _ in z_parts.values())
        fund_score = sum(w * z for w, z in z_parts.values()) / w_sum
        detail["weight_renormalized"] = w_sum
        return fund_score, detail

    def _compute_bt_premium(self, trade_date: str, trace: dict[str, Any]) -> tuple[float | None, float | None]:
        """大宗交易加权折溢价率(T-1) 及其 20 日 z-score。

        单查询 JOIN kline_daily 收盘价（USING 无别名写法），返回 (premium, z)；
        无数据/收盘腿缺失→(None, None)；历史不足→(premium, None)（该分量降级）。
        """
        bt_table = self._table("market_block_trade", "c1_market.block_trade")
        kline_table = self._table("market_kline_daily", "c1_market.kline_daily")
        tsv = self._query(
            _SQL_BLOCK_PREMIUM.format(
                bt_table=bt_table,
                kline_table=kline_table,
                trade_date=trade_date,
                limit=self._config.zscore_window + 1,
            ),
            "block_trade",
            trace,
        )
        rows = _parse_tsv(tsv, 2)
        premiums = [v for _, s in rows if (v := _safe_float(s)) is not None]
        if not premiums:
            trace["channels"].setdefault("block_trade", "skipped:no_data_or_no_close")
            return None, None
        z = _zscore(premiums[0], premiums[1:])
        if z is None:
            trace["channels"]["block_trade"] = "degraded:insufficient_history"
        else:
            trace["channels"]["block_trade"] = "ok"
        return premiums[0], z

    # ── M3-⑧ 事件日历联动（§9.12，fail-open 铁律）────────────────────────

    def _compute_event_flags(self, trade_date: datetime.date, trace: dict[str, Any]) -> dict[str, Any]:
        """事件日历联动：高影响事件夜/期权到期/交割周/A50 交割（自算标注）。

        fail-open 铁律：calendar_event 空表/查询失败→本层静默跳过+留痕，不阻塞主流程。
        A50 交割日 calendar_event 暂无此类——按规则自算标注（每月倒数第 2 个工作日）。
        """
        flags: dict[str, Any] = {
            "high_impact_event_night": False,
            "high_impact_events": [],
            "index_option_expiry_today": False,
            "futures_delivery_week": False,
            "a50_futures_delivery_today": False,
            "a50_futures_delivery_eve": False,
            "calendar_status": "ok",
        }
        iso = trade_date.isoformat()
        # 窗口：前 7 天覆盖"当周"交割日（周一事件 vs 周五今日）+前后窗口高影响事件
        win_start = (trade_date - datetime.timedelta(days=7)).isoformat()
        win_end = (trade_date + datetime.timedelta(days=2)).isoformat()
        table = self._table("market_calendar_event", "c1_market.calendar_event")
        tsv = self._query(
            _SQL_CALENDAR.format(table=table, win_start=win_start, win_end=win_end),
            "calendar_event",
            trace,
        )
        rows = _parse_tsv(tsv, 2)
        if not rows:
            flags["calendar_status"] = "empty_or_failed"
            trace["channels"].setdefault("calendar_event", "skipped:empty_fail_open")
        else:
            trace["channels"]["calendar_event"] = "ok"
            hi_lo = (trade_date - datetime.timedelta(days=self._config.high_impact_window_days)).isoformat()
            for ev_date, ev_type in rows:
                ev_type = (ev_type or "").strip()
                if ev_type in HIGH_IMPACT_EVENT_TYPES and hi_lo <= ev_date <= iso:
                    flags["high_impact_event_night"] = True
                    flags["high_impact_events"].append(f"{ev_date}:{ev_type}")
                if ev_type == "index_option_expiry" and ev_date == iso:
                    flags["index_option_expiry_today"] = True
                if ev_type == "futures_delivery":
                    # 当周判定：事件日与今日落在同一 Mon-Sun 自然周
                    try:
                        ev_d = datetime.date.fromisoformat(ev_date)
                        if ev_d.isoweekday() <= 7 and (ev_d - datetime.timedelta(days=ev_d.isoweekday() - 1)) == (
                            trade_date - datetime.timedelta(days=trade_date.isoweekday() - 1)
                        ):
                            flags["futures_delivery_week"] = True
                    except ValueError:
                        continue

        # A50 交割日自算标注（§9.12：每月倒数第 2 个工作日；交割日及其前夜敏感度升半档）
        a50_day = _a50_delivery_day(trade_date.year, trade_date.month)
        flags["a50_delivery_rule_date"] = a50_day.isoformat()
        if trade_date == a50_day:
            flags["a50_futures_delivery_today"] = True
        elif _next_business_day(trade_date) == a50_day:
            flags["a50_futures_delivery_eve"] = True
        return flags

    # ── 主合成 ────────────────────────────────────────────────────────────

    def compute(
        self,
        trade_date: str | datetime.date,
        bs005_triggered: bool = False,
    ) -> OvernightRevision:
        """计算盘前隔夜边界修正（三通道合成，任何单通道异常降级不炸整体）。

        Args:
            trade_date: 交易日（ISO 字符串或 date）。
            bs005_triggered: BS-005 外围冲击硬触发（上游 36号 §3 检测注入）→±一档。

        Returns:
            OvernightRevision：final_shift∈{-1,-0.5,0,+0.5,+1} + 全程留痕。
        """
        if isinstance(trade_date, str):
            d = datetime.date.fromisoformat(trade_date)  # 非法日期抛 ValueError（ERROR_CONTRACT）
        else:
            d = trade_date
        iso = d.isoformat()
        cfg = self._config
        trace: dict[str, Any] = {"channels": {}}
        reasons: list[str] = []

        # 通道 1：外盘（§9.6）
        gap_adj, gap_degraded, gap_reasons = self._compute_gap_adj(iso, trace)
        reasons.extend(gap_reasons)

        # 通道 2：资金面四件套（§9.10）
        fund_score, fund_detail = self._compute_fund_score(iso, trace)
        if fund_score is None:
            reasons.append("资金面四件全无数据，跳过确认/否决（fail-open）")
        else:
            reasons.append(f"fund_score={fund_score:+.4f}（分量 {fund_detail['components_used']}）")

        # 通道 3：事件日历（§9.12，fail-open）
        event_flags = self._compute_event_flags(d, trace)

        # 敏感度：高影响事件夜 或 A50 交割日/前夜 → 升半档（整档阈值 1.5%→1.0%）
        sensitivity_up = (
            event_flags["high_impact_event_night"]
            or event_flags["a50_futures_delivery_today"]
            or event_flags["a50_futures_delivery_eve"]
        )
        sensitivity_scale = 0.5 if sensitivity_up else 1.0
        full_threshold = cfg.event_full_threshold if sensitivity_up else cfg.gap_threshold_full
        if sensitivity_up:
            reasons.append(
                f"事件敏感度升半档（{'+'.join(event_flags['high_impact_events']) or 'a50_delivery'}），整档阈值降至 {full_threshold:.1%}"
            )

        # 外盘分档（§9.6 修正规则）
        if gap_adj is None:
            base_shift = 0.0
        elif bs005_triggered:
            # BS-005 硬触发→±一档；方向随 gap 符号，gap≈0 取保守迁移（外围冲击=风险事件）
            base_shift = 1.0 if gap_adj > 0 else -1.0
            reasons.append(f"BS-005 外围冲击触发 → {'+1' if base_shift > 0 else '-1'} 档（硬触发）")
        elif abs(gap_adj) >= full_threshold:
            base_shift = 1.0 if gap_adj > 0 else -1.0
            reasons.append(f"|gap_adj|={abs(gap_adj):.2%} ≥ {full_threshold:.1%} → {'+1' if base_shift > 0 else '-1'} 档")
        elif abs(gap_adj) >= cfg.gap_threshold_half:
            base_shift = 0.5 if gap_adj > 0 else -0.5
            reasons.append(f"{cfg.gap_threshold_half:.1%} ≤ |gap_adj|={abs(gap_adj):.2%} < {full_threshold:.1%} → {'+0.5' if base_shift > 0 else '-0.5'} 档（加仓上限±20%）")
        else:
            base_shift = 0.0
            reasons.append(f"|gap_adj|={abs(gap_adj):.2%} < {cfg.gap_threshold_half:.1%} → 不变档")

        # 资金面确认/否决（§9.10）：同向×1.0；反向且 |fund_score|>1σ→否决半档
        final_shift = base_shift
        if fund_score is not None and base_shift != 0.0:
            if fund_score * base_shift >= 0:
                reasons.append(f"fund_score={fund_score:+.2f} 与外盘修正同向 → 确认（×1.0）")
            elif abs(fund_score) > cfg.fund_veto_sigma:
                final_shift = base_shift - VETO_HALF_STEP * (1 if base_shift > 0 else -1)
                reasons.append(
                    f"fund_score={fund_score:+.2f} 与外盘修正反向且 |fund_score|>{cfg.fund_veto_sigma}σ → 否决半档（{base_shift:+.1f}→{final_shift:+.1f}）"
                )
            else:
                reasons.append(f"fund_score={fund_score:+.2f} 反向但 |fund_score|≤{cfg.fund_veto_sigma}σ → 不否决")

        # 事件联动缩放输出（§9.12）
        m1_threshold_scale = M1_THRESHOLD_SCALE_OPTION_EXPIRY if event_flags["index_option_expiry_today"] else 1.0
        basis_weight_scale = BASIS_WEIGHT_SCALE_DELIVERY_WEEK if event_flags["futures_delivery_week"] else 1.0
        a50_weight = A50_DELIVERY_CHANNEL_WEIGHT if event_flags["a50_futures_delivery_today"] else None
        if event_flags["index_option_expiry_today"]:
            reasons.append(f"期权到期日 → m1_threshold_scale={m1_threshold_scale}（防伽马挤压假情绪）")
        if event_flags["futures_delivery_week"]:
            reasons.append(f"股指期货交割周 → basis_weight_scale={basis_weight_scale}（贴水收敛失真降权）")
        if a50_weight is not None:
            reasons.append(f"A50 交割日（规则自算 {event_flags['a50_delivery_rule_date']}）→ a50_channel_weight={a50_weight}")

        return OvernightRevision(
            date=iso,
            gap_adj=gap_adj,
            gap_adj_degraded=gap_degraded,
            fund_score=fund_score,
            fund_detail=fund_detail,
            event_flags=event_flags,
            sensitivity_scale=sensitivity_scale,
            final_shift=final_shift,
            m1_threshold_scale=m1_threshold_scale,
            basis_weight_scale=basis_weight_scale,
            a50_channel_weight=a50_weight,
            reasons=reasons,
            trace=trace,
        )


# ── 主入口 ──


def compute_overnight_revision(
    trade_date: str | datetime.date,
    ch_client: Callable[[str], str] | None = None,
    config: OvernightRevisionConfig | None = None,
    bs005_triggered: bool = False,
) -> OvernightRevision:
    """盘前隔夜边界修正主入口（MOD-PLAN-004）。

    Args:
        trade_date: 交易日（ISO 字符串或 date）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）；
            None 时走项目默认 CH 通道（zephyr.data.ch_reader.query）。
        config: 修正参数配置（None=44号设计真源默认值）。
        bs005_triggered: BS-005 外围冲击硬触发（上游注入）。

    Returns:
        OvernightRevision：纯 dataclass，JSON 可序列化（供 prediction_log 落库）。
    """
    return OvernightBoundaryReviser(ch_client=ch_client, config=config).compute(
        trade_date, bs005_triggered=bs005_triggered
    )
