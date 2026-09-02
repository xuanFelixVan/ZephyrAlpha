# [BLUEPRINT] MOD-SIG-060 | 待统筹登记（blueprint 未建，真源=44号备忘录 §9.13 + §9.2 通道 c；92号清单 §7.4+§7.10 合并施工，架构审查报告 §11.5 SEC-03 同一工件裁定）
# [MODULE] zephyr.signal_ashare.sector_divergence
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] config/sector_attribute_labels.yaml（板块族标签真源）; docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml（一线游资席位身份）; c1_market.kline_sector_880（只读）; c1_market.sector_constituent（只读）; c1_market.money_flow（只读）; c1_market.kline_daily（只读）; c1_market.stk_limit（只读）; c1_market.dragon_tiger_seat（只读）
# [CONSUMERS] （MVP 阶段无——候选消费方：M2 边界修正降档触发（44号 §9.5）、MOD-SIG-025 情绪注解、SEC-01 板块盘后报告器、M3-⑨ LLM 板块族输入、prediction_log 落库）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 不预测纪律：只出状态+风险清单+历史条件频率，不出方向/点位（个股分歧≠必然下跌，44号原文）；velocity_percentile ∈ [0,1]；top3_overlap ∈ [0,1]；各维度独立降级互不累及；PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md §9.13
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可用→对应维度降级 notes 留痕不抛；主数据（kline_sector_880）缺失/异常→degraded=True；trade_date 格式非法→ValueError（调用方契约违例，fail-closed）；板块族标签 yaml 缺失/解析失败→rs 维度降级不抛
# [TESTS] tests/signal_ashare/test_sector_divergence.py
# [A_module] module_id=MOD-SIG-060 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""
MOD-SIG-060 — 板块分歧度与轮动速度计 + SEC-03 概率标定器（44号备忘录 §9.13，M1-⑩；
合并施工 M1-②c 板块属性标签雷达 §9.2 通道 c；92号清单 §7.4+§7.10，
架构审查报告 §11.5 SEC-03 同一工件防双真源裁定）。

四件套：
  a) 消费接入——import 既有 22 号模块（不重复造）：sector_rotation_state 5 状态分类
     （classify_rotation_state/top_n_hhi/watch_score）+ sector_siphon 虹吸态
     （detect_siphon_state/SectorFlowSnapshot，z>1.5σ）。映射：CONSENSUS_CLIMAX/
     DISTRIBUTION_RISK → top_risk_flag（见顶风险标记，M2 降档触发输出）；
     虹吸态且电风扇>75 分位 → siphon_chaos_flag（极端分化+无主线混沌共振）。
  b) 电风扇速度计（国泰海通 2026-08 口径）：rotation_velocity = mean(|rank_t(板块涨幅)
     − rank_{t-5}(板块涨幅)|)，>75 分位_250d → 电风扇行情；top3_overlap =
     |今日 Top3 ∩ 昨日 Top3|/3 <20% → 一日游生态；lead_streak<2 且 velocity>75 分位
     → no_mainline_flag（无主线混沌注解）。
  c) 个股分歧度（24号口径通用化）：divergence = 0.4·z(换手突增倍数) + 0.3·上影占比
     + 0.2·炸板标记 + 0.1·龙虎榜买卖对打；>80 分位 → 个股级例外清单（禁新开仓注解）。
     映射纪律：个股分歧≠必然下跌（见顶/上涨中继/下跌中继三态都可能），只出风险清单
     不出方向。
  d) SEC-03 概率标定器：5 状态 × 后续 3/5 日涨跌历史条件频率（滚动 250 交易日窗）——
     输出"当前状态=X；该状态历史后续 3 日下跌>2% 频率=Y%（样本 N=Z）"；可审计可复算，
     不做伪精确点概率；单状态样本 <30 → sufficient=False 标注。

合并施工 M1-②c（§7.10）：config/sector_attribute_labels.yaml 为板块族标签真源
（防御族=银行/保险/公用/煤炭，进攻族=科技/券商），本模块 loader 消费；
rs_ratio = mean_ret(进攻族) − mean_ret(防御族)，rs_z<−1 且指数红 → 避险抱团注解
（情绪差）；rs_z>+1 且上涨家数占比改善 → 真情绪好注解。

【数据实证口径（2026-08-22 直查 c1_market，可信）】
- kline_sector_880（period='1d'）：469 板块 24,981 行至 08-20；880001-880009 为市场
  统计指数（880001=总市值，本模块作市场收益代理），880201-880232 地区板块（锚定实证），
  8805xx-8809xx 概念/风格板块；sector_name 列在库中为空串；无成分纯净 880xxx 行业板。
  板块全集口径 = 全部 880xxx 剔除 880001-880009（初拟，待实盘标定）。
- 纯行业板块为 881xxx 族（sector_constituent SCD-2 锚定：银行 881386 n=15 / 保险 881395
  n=5 / 券商 881394 n=50 / 煤炭 881002 n=25 / 电力公用 881459 n=103 / 半导体 881319
  n=182 / 通信设备 881338 n=90），但 881xxx 无板块 K 线 → 族收益经成分股等权聚合
  （kline_daily.pct_change）计算，yaml evidence 字段逐条留痕。
- 炸板判定：limit_up_down 采集仅 涨停/跌停 两类（无炸板池）→ 炸板 = 盘中触及涨停价
  （high ≥ stk_limit.limit_up，0.005 价格网格容差）且收盘未封（close < limit_up）。
- 龙虎榜对打：买卖两侧均有一线游资席位（seat_registry：youzi 且 seat_style ∈
  {龙头连板, 首板}，对齐 MOD-SIG-056/057 白名单）且 |净买入| < 上榜成交额 1%
  （成交额=席位行 buy+sell 合计，对齐 MOD-INT-EVENT-DT 口径）。
- 板块 K 线历史仅 ~52 交易日（2026-06 起采）：速度计 250 分位窗/标定器 250 窗在
  数据积累期常态降级（min_periods 守卫 + insufficient 标注），属设计内行为。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 板块日 K 历史窗（kline_sector_880，period=1d）
#   fields: sector_code/trade_date/close/amount
# - id: I2
#   name: 板块成分股映射（sector_constituent，SCD-2 时点有效）
#   fields: sector_code/stock_code
# - id: I3
#   name: 个股主力资金流（money_flow，虹吸净流入腿）
#   fields: trade_date/symbol_canonical/main_net_inflow
# - id: I4
#   name: 个股日 K（kline_daily，换手/上影/族收益/广度）
#   fields: symbol_canonical/trade_date/high/low/close/turnover/pct_change
# - id: I5
#   name: 涨跌停价（stk_limit，炸板判定）
#   fields: symbol_canonical/limit_up
# - id: I6
#   name: 龙虎榜席位（dragon_tiger_seat，对打识别）
#   fields: symbol_canonical/seat_name/buy_amount/sell_amount/net_amount/buy_rank/sell_rank
# - id: I7
#   name: 板块族标签（sector_attribute_labels.yaml）+ 席位身份（seat_registry.yaml）
# 层: 特征
# - id: F1
#   name_zh: 轮动状态输入四件
#   formula: up_ratio=上涨板块占比; hhi_top5=头部5成交额份额平方和; lead_streak=同一板块连续领涨天数; disp=领涨放量滞涨(额>5日均×1.2 且 涨幅<前日×0.5)
# - id: F2
#   name_zh: 电风扇速度计
#   formula: rotation_velocity=mean(|rank_t−rank_{t-5}|); percentile_250d; top3_overlap=|Top3_t∩Top3_{t-1}|/3
# - id: F3
#   name_zh: 虹吸三信号历史序列
#   formula: hhi/inflow_conc/outflow_ratio 逐日（detect_siphon_state 复用，历史序列本模块构）
# - id: F4
#   name_zh: 个股分歧四件
#   formula: 换手突增=当日换手/20日均(>2.5 注解); 上影占比=(high−close)/(high−low)(>0.5 注解); 炸板=触板未封; 对打=双侧一线游资且|净|<1%额
# - id: F5
#   name_zh: 族相对强度
#   formula: rs_ratio=mean(pct_change 进攻族成分)−mean(pct_change 防御族成分); rs_z=z(rs_ratio,20d)
# 层: 算法
# - id: A1
#   name_zh: 5 状态分类与映射
#   desc: classify_rotation_state(F1) → CONSENSUS_CLIMAX/DISTRIBUTION_RISK→top_risk_flag
# - id: A2
#   name_zh: 速度计判读
#   desc: percentile>0.75→fan_market; overlap<0.20→one_day_ecology; streak<2 且 percentile>0.75→no_mainline
# - id: A3
#   name_zh: 虹吸态与共振
#   desc: detect_siphon_state z>1.5σ; 虹吸 且 fan_market→siphon_chaos_flag
# - id: A4
#   name_zh: 个股分歧合成与例外清单
#   desc: divergence=0.4z+0.3影+0.2炸+0.1打; 截面 >80 分位→stock_watchlist（只清单不方向）
# - id: A5
#   name_zh: SEC-03 条件频率标定
#   desc: 状态序列重放×880001 后续 3/5 日收益; 分组频率; N<30→sufficient=False
# - id: A6
#   name_zh: 族相对强度注解
#   desc: rs_z<−1 且指数红→避险抱团; rs_z>+1 且 adv 改善→真情绪好
# 层: 输出
# - id: O1
#   name_zh: SectorDivergenceResult
#   intro: date/rotation_state/top_risk_flag/siphon_z/rotation_velocity/velocity_percentile/top3_overlap/lead_streak/no_mainline_flag/siphon_chaos_flag/state_conditional_stats/stock_watchlist/rs_ratio/rs_z/annotations/degraded；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I1 --> F1
# I1 --> F2
# I1,I2,I3 --> F3
# I4,I5,I6,I7 --> F4
# I2,I4,I7 --> F5
# F1 --> A1
# F2 --> A2
# F3 --> A3
# F2 --> A3
# F4 --> A4
# F1,I1 --> A5
# F5,I1,I4 --> A6
# A1,A2,A3,A4,A5,A6 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.signal_ashare.sector_rotation_state import (
    RotationState,
    classify_rotation_state,
    top_n_hhi,
    watch_score,
)
from zephyr.signal_ashare.sector_siphon import (
    SectorFlowSnapshot,
    detect_siphon_state,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "SectorAttributeLabels",
    "SectorDivergenceConfig",
    "SectorDivergenceResult",
    "StateConditionalStat",
    "StockDivergenceWatch",
    "compute_sector_divergence",
    "load_sector_attribute_labels",
]

_LABELS_PATH: Final = Path(__file__).resolve().parents[3] / "config" / "sector_attribute_labels.yaml"
_SEAT_REGISTRY_PATH: Final = (
    Path(__file__).resolve().parents[3] / "docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml"
)

#: 市场统计指数代码（剔除出板块全集；880001 作市场收益代理）
_MARKET_INDEX_CODES: Final = frozenset(f"88000{i}.SH" for i in range(1, 10))

# SQL 集中化（§5.160.2）：模块级 SQL_* 常量，参数化查询禁 f-string 插值
SQL_LATEST_SECTOR_DATE: Final = """
SELECT max(trade_date)
FROM c1_market.kline_sector_880
WHERE period = '1d'
"""

SQL_SECTOR_KLINE_WINDOW: Final = """
SELECT sector_code, trade_date, close, amount
FROM c1_market.kline_sector_880
WHERE period = '1d' AND trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""

SQL_SECTOR_CONSTITUENTS: Final = """
SELECT sector_code, stock_code
FROM c1_market.sector_constituent
WHERE valid_from <= %(trade_date)s AND (valid_to IS NULL OR valid_to > %(trade_date)s)
"""

SQL_MONEY_FLOW_WINDOW: Final = """
SELECT trade_date, symbol_canonical, main_net_inflow
FROM c1_market.money_flow
WHERE trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""

SQL_STOCK_KLINE_WINDOW: Final = """
SELECT symbol_canonical, trade_date, high, low, close, turnover, pct_change
FROM c1_market.kline_daily
WHERE market_type = 'A_share' AND quality_flag = 1
  AND trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
"""

SQL_STK_LIMIT_TODAY: Final = """
SELECT symbol_canonical, limit_up
FROM c1_market.stk_limit
WHERE trade_date = %(trade_date)s
"""

SQL_LHB_TODAY: Final = """
SELECT symbol_canonical, seat_name, buy_amount, sell_amount, net_amount, buy_rank, sell_rank
FROM c1_market.dragon_tiger_seat
WHERE trade_date = %(trade_date)s
"""

SQL_BREADTH_WINDOW: Final = """
SELECT trade_date, countIf(pct_change > 0), count()
FROM c1_market.kline_daily
WHERE market_type = 'A_share' AND quality_flag = 1
  AND trade_date <= %(trade_date)s AND trade_date >= %(start_date)s
GROUP BY trade_date
"""


@dataclass(frozen=True, slots=True)
class SectorDivergenceConfig:
    """阈值配置——默认值取自 44号备忘录 §9.13/§9.2 + 2026-08-22 数据实证。"""

    labels_path: str = str(_LABELS_PATH)  # 板块族标签 yaml 真源
    seat_registry_path: str = str(_SEAT_REGISTRY_PATH)  # 席位身份 registry
    sector_lookback_calendar_days: int = 400  # 板块 K 线查询自然日窗（覆盖 250 交易日标定窗）
    stock_lookback_calendar_days: int = 45  # 个股 K 线查询自然日窗（覆盖 20 日均换手+1 日）
    siphon_lookback_calendar_days: int = 120  # 虹吸历史序列查询自然日窗（z-score 滚动参照）
    market_index_code: str = "880001.SH"  # 市场收益代理（总市值指数）
    velocity_lag_days: int = 5  # 速度计排名对照 lag（周度=5 交易日，国泰海通口径）
    velocity_percentile_window: int = 250  # 分位参照窗（交易日）
    velocity_min_periods: int = 60  # 速度计分位最小样本（不足 → None 降级）
    fan_market_percentile: float = 0.75  # 电风扇行情触发分位（>75 分位）
    top3_overlap_threshold: float = 0.20  # 一日游生态阈值（Top3 次日重合率 <20%）
    lead_streak_no_mainline: int = 2  # 无主线判定：连续领涨 <2 日
    fast_rotation_window: int = 90  # 快轮动标志 P90 参照窗（交易日）
    fast_rotation_min_periods: int = 10  # P90 最小样本（不足 → fast_rotation=False）
    siphon_z_threshold: float = 1.5  # 虹吸态 z 阈值（22 号 spec §3.1⑤）
    siphon_n_top: int = 5  # 虹吸头部 N 板块
    turnover_mean_days: int = 20  # 换手突增分母窗（20 日均换手）
    turnover_surge_flag: float = 2.5  # 换手突增注解阈值（>2.5）
    upper_shadow_flag: float = 0.5  # 上影占比注解阈值（>0.5）
    lhb_fight_net_ratio: float = 0.01  # 龙虎榜对打：|净买入| < 上榜成交额 1%
    watchlist_percentile: float = 0.80  # 个股分歧例外清单分位（>80 分位）
    watchlist_min_universe: int = 30  # 截面分位最小可评分宇宙（不足 → 不出清单）
    calib_forward_days: tuple[int, ...] = (3, 5)  # 标定器后续涨跌观察窗（交易日）
    calib_down_threshold: float = -0.02  # 下跌事件阈值（跌 >2%）
    calib_min_samples: int = 30  # 单状态条件频率最小样本（不足 → sufficient=False）
    limit_price_tol: float = 0.005  # 炸板触板价格网格容差（0.01 取整半格）


@dataclass(frozen=True, slots=True)
class SectorAttributeLabels:
    """板块族标签（config/sector_attribute_labels.yaml 加载结果）。"""

    defensive_boards: tuple[str, ...]  # 防御族板块代码（银行/保险/公用/煤炭）
    offensive_boards: tuple[str, ...]  # 进攻族板块代码（科技/券商）
    board_names: dict[str, str]  # 板块代码 → 中文名（注解文本用）
    rs_sigma_window: int = 20  # rs_ratio ±1σ 判读窗（交易日）
    rs_min_periods: int = 10  # σ 序列最小样本


@dataclass(frozen=True, slots=True)
class StateConditionalStat:
    """SEC-03 单状态条件频率（可审计可复算，非伪精确点概率）。"""

    state: str  # RotationState 值
    n_samples: int  # 该状态历史样本数（至少有 1 个前向观测的交易日数）
    freq_down_3d: float | None  # 后续 3 交易日跌 >2% 频率；无 3 日前向观测 → None
    freq_down_5d: float | None  # 后续 5 交易日跌 >2% 频率；无 5 日前向观测 → None
    sufficient: bool  # n_samples >= calib_min_samples


@dataclass(frozen=True, slots=True)
class StockDivergenceWatch:
    """个股分歧例外清单条目（只出风险清单不出方向，44号映射纪律）。"""

    symbol: str
    score: float  # 合成分歧度
    percentile: float  # 当日截面分位 ∈ [0,1]
    turnover_surge: float | None  # 换手突增倍数（当日换手/20 日均）
    upper_shadow: float  # 上影占比 ∈ [0,1]
    limit_broken: bool  # 炸板标记（触板未封）
    lhb_fight: bool  # 龙虎榜买卖对打标记
    reasons: list[str] = field(default_factory=list)  # 触发理由链（可追溯）


@dataclass(frozen=True, slots=True)
class SectorDivergenceResult:
    """板块分歧度输出契约（T 日盘后计算，M2 降档/注解层消费）。"""

    date: str  # 数据日 YYYY-MM-DD
    rotation_state: str | None = None  # 5 状态（RotationState 值）；板块 K 线不足 → None
    watch_score: float | None = None  # 22 号 watch_score 透传（板块强度综合层调节项）
    top_risk_flag: bool = False  # CONSENSUS_CLIMAX/DISTRIBUTION_RISK → 见顶风险标记（M2 降档触发）
    siphon_z: float | None = None  # 虹吸态 z 分；money_flow/成分缺失 → None（降级）
    siphon_flag: bool = False  # z > 1.5σ 虹吸态
    rotation_velocity: float | None = None  # 电风扇速度计原值（周度排名变化均值）
    velocity_percentile: float | None = None  # 速度计 250 交易日分位；样本不足 → None
    fan_market_flag: bool = False  # 电风扇行情（分位 >0.75）
    top3_overlap: float | None = None  # Top3 次日重合率 ∈ [0,1]
    one_day_ecology: bool = False  # 一日游生态（重合率 <20%）
    lead_streak: int | None = None  # 同一板块连续领涨天数
    no_mainline_flag: bool = False  # 无主线混沌（streak<2 且 速度计 >75 分位）
    siphon_chaos_flag: bool = False  # 极端分化+无主线混沌共振（虹吸 且 电风扇）
    rs_ratio: float | None = None  # 进攻族−防御族 当日等权收益差
    rs_z: float | None = None  # rs_ratio 相对 20 日窗 z 分；样本不足 → None
    state_conditional_stats: list[StateConditionalStat] = field(default_factory=list)
    current_state_summary: str | None = None  # "当前状态=X；后续3日下跌>2%频率=Y%（样本N=Z）"
    stock_watchlist: list[StockDivergenceWatch] = field(default_factory=list)
    annotations: list[str] = field(default_factory=list)  # 中文注解文本链（消费方直读）
    degraded: bool = False  # 主数据不可用/查询异常时 True，结果不可用于决策
    notes: list[str] = field(default_factory=list)  # 降级原因等留痕


# ------------------------------------------------------------------
# 板块族标签 loader（M1-②c 真源消费）
# ------------------------------------------------------------------


def load_sector_attribute_labels(path: str | Path | None = None) -> SectorAttributeLabels:
    """加载板块族标签 yaml → SectorAttributeLabels。

    Args:
        path: yaml 路径；None 用默认 config/sector_attribute_labels.yaml。

    Returns:
        SectorAttributeLabels（防御/进攻族板块代码元组 + 板块中文名表 + rs 参数）。

    Raises:
        FileNotFoundError: yaml 不存在（调用方契约违例；主入口捕获后 rs 维度降级）。
        ValueError: yaml 结构非法（families.defensive/offensive 缺失）。
    """
    p = Path(path) if path is not None else _LABELS_PATH
    if not p.is_file():
        raise FileNotFoundError(f"板块族标签 yaml 不存在: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    families = data.get("families") or {}
    defensive = families.get("defensive") or {}
    offensive = families.get("offensive") or {}
    if not defensive.get("boards") or not offensive.get("boards"):
        raise ValueError(f"板块族标签 yaml 结构非法（families.defensive/offensive.boards 缺失）: {p}")

    def _codes(section: dict) -> tuple[str, ...]:
        return tuple(str(b.get("code")) for b in section.get("boards") or [] if b.get("code"))

    names: dict[str, str] = {}
    for section in (defensive, offensive):
        for b in section.get("boards") or []:
            code = b.get("code")
            if code:
                names[str(code)] = str(b.get("name") or code)
    params = data.get("params") or {}
    return SectorAttributeLabels(
        defensive_boards=_codes(defensive),
        offensive_boards=_codes(offensive),
        board_names=names,
        rs_sigma_window=int(params.get("rs_sigma_window") or 20),
        rs_min_periods=int(params.get("rs_min_periods") or 10),
    )


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


def _default_client():
    """延迟加载默认 CH 客户端（不可用时返回 None，由主入口转 degraded）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，板块分歧度分析降级", exc_info=True)
        return None


def _as_date(v: Any) -> date:
    """CH 日期行值归一（date 原样返回，str 按 YYYY-MM-DD 解析）。"""
    return v if isinstance(v, date) else _normalize_date(v)


def _midrank_percentile(sorted_values: list[float], current: float) -> float:
    """中秩分位 = (count(< x) + count(≤ x)) / (2n)——并列值取平均秩（对齐 sector_momentum
    percentile_ranks 的 ties 约定）；用于截面清单分位，防止大量并列低分被 >80 分位误纳。"""
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


def _mean_std(values: list[float]) -> tuple[float, float]:
    """样本均值/标准差（n<2 → (mean, 0.0)，调用方按 0 守卫）。"""
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    if n < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in values) / (n - 1)
    return mean, math.sqrt(var)


def _zscore(value: float, history: list[float]) -> float:
    """value 相对 history 的 z-score（n<2 或 σ=0 → 0.0，降级不触发不误报）。"""
    mean, std = _mean_std(history)
    if std == 0.0:
        return 0.0
    return (value - mean) / std


def _daily_close_amount(
    sector_rows: list[tuple],
) -> tuple[dict[str, list[tuple[date, float, float]]], list[date]]:
    """板块 K 线行 → {板块: [(日期, 收盘, 成交额)] 升序} + 全日期升序（板块全集剔除市场指数）。"""
    by_sector: dict[str, list[tuple[date, float, float]]] = {}
    dates: set[date] = set()
    for row in sector_rows:
        code = str(row[0])
        if code in _MARKET_INDEX_CODES:
            continue
        d = _as_date(row[1])
        by_sector.setdefault(code, []).append((d, float(row[2] or 0.0), float(row[3] or 0.0)))
        dates.add(d)
    for series in by_sector.values():
        series.sort(key=lambda x: x[0])
    return by_sector, sorted(dates)


def _daily_returns(series: list[tuple[date, float, float]]) -> dict[date, float]:
    """(日期, 收盘, 成交额) 序列 → {日期: 日收益}（相邻收盘比，基准 ≤0 跳过）。"""
    out: dict[date, float] = {}
    for i in range(1, len(series)):
        prev_close = series[i - 1][1]
        if prev_close > 0:
            out[series[i][0]] = series[i][1] / prev_close - 1.0
    return out


def _amount_maps(
    by_sector: dict[str, list[tuple[date, float, float]]],
) -> dict[str, dict[date, float]]:
    """板块 → {日期: 成交额} 预计算（hhi/放量滞涨/虹吸取数共用，免逐日线性扫描）。"""
    return {code: {d: a for d, _, a in series} for code, series in by_sector.items()}


def _leader_series(
    by_sector: dict[str, list[tuple[date, float, float]]],
    all_dates: list[date],
) -> tuple[dict[date, str], dict[date, dict[str, float]]]:
    """逐日领涨板块（当日收益最高者）+ 逐日 {板块: 收益} 截面。"""
    rets_by_sector = {code: _daily_returns(series) for code, series in by_sector.items()}
    cross: dict[date, dict[str, float]] = {}
    for code, rets in rets_by_sector.items():
        for d, r in rets.items():
            cross.setdefault(d, {})[code] = r
    leaders: dict[date, str] = {}
    for d in all_dates:
        day = cross.get(d)
        if day:
            leaders[d] = max(day.items(), key=lambda kv: kv[1])[0]
    return leaders, cross


def _lead_streaks(leaders: dict[date, str], all_dates: list[date]) -> dict[date, int]:
    """逐日连续领涨天数（同一板块截至当日连续领涨日数；当日无领涨 → 不出键）。"""
    streaks: dict[date, int] = {}
    prev_leader: str | None = None
    streak = 0
    for d in all_dates:
        leader = leaders.get(d)
        if leader is None:
            prev_leader = None
            streak = 0
            continue
        streak = streak + 1 if leader == prev_leader else 1
        prev_leader = leader
        streaks[d] = streak
    return streaks


def _disp_signal(
    d: date,
    leader: str,
    by_sector: dict[str, list[tuple[date, float, float]]],
    amounts: dict[str, dict[date, float]],
    cross: dict[date, dict[str, float]],
) -> int:
    """领涨板块放量滞涨：成交额 > 5 日均额 ×1.2 且 当日涨幅 < 前日涨幅 ×0.5（22 号 §3.1⑨ 口径）。"""
    series = by_sector.get(leader)
    amt_map = amounts.get(leader)
    if not series or not amt_map:
        return 0
    idx = next((i for i, (dd, _, _) in enumerate(series) if dd == d), None)
    if idx is None or idx == 0:
        return 0
    prev_days = [series[i][0] for i in range(max(0, idx - 5), idx)]
    prev5 = [amt_map[dd] for dd in prev_days if amt_map.get(dd, 0.0) > 0]
    if len(prev5) < 2:
        return 0
    amount_today = amt_map.get(d, 0.0)
    ret_today = cross.get(d, {}).get(leader)
    ret_prev = cross.get(series[idx - 1][0], {}).get(leader)
    if ret_today is None or ret_prev is None:
        return 0
    mean_amt = sum(prev5) / len(prev5)
    return 1 if amount_today > mean_amt * 1.2 and ret_today < ret_prev * 0.5 else 0


def _rotation_speeds(
    amounts: dict[str, dict[date, float]],
    all_dates: list[date],
) -> dict[date, float]:
    """逐日轮动速度 = 0.5 × Σ|今日成交额占比 − 昨日占比|（22 号 §3.1⑨ fast_rotation 口径）。"""
    speeds: dict[date, float] = {}
    prev_shares: dict[str, float] | None = None
    for d in all_dates:
        today = {c: amap[d] for c, amap in amounts.items() if d in amap}
        total = sum(today.values())
        shares = {c: a / total for c, a in today.items()} if total > 0 else {}
        if prev_shares is not None and shares:
            codes = set(shares) | set(prev_shares)
            speeds[d] = 0.5 * sum(abs(shares.get(c, 0.0) - prev_shares.get(c, 0.0)) for c in codes)
        prev_shares = shares
    return speeds


def _build_rotation_states(
    by_sector: dict[str, list[tuple[date, float, float]]],
    all_dates: list[date],
    cfg: SectorDivergenceConfig,
) -> dict[date, RotationState]:
    """逐日重放 5 状态分类（22 号 classify_rotation_state 消费，供当日状态+标定器共用）。"""
    amounts = _amount_maps(by_sector)
    leaders, cross = _leader_series(by_sector, all_dates)
    streaks = _lead_streaks(leaders, all_dates)
    speeds = _rotation_speeds(amounts, all_dates)
    sorted_dates = [d for d in all_dates if d in cross]
    states: dict[date, RotationState] = {}
    for i, d in enumerate(sorted_dates):
        day = cross[d]
        up_ratio = sum(1 for r in day.values() if r > 0) / len(day)
        day_amounts = [amounts[c][d] for c in day if c in amounts and d in amounts[c]]
        hhi = top_n_hhi(day_amounts, n=cfg.siphon_n_top)
        disp = _disp_signal(d, leaders[d], by_sector, amounts, cross)
        # 快轮动标志：速度 > 前 N 日 P90
        hist = [speeds[dd] for dd in sorted_dates[max(0, i - cfg.fast_rotation_window) : i] if dd in speeds]
        fast = False
        if d in speeds and len(hist) >= cfg.fast_rotation_min_periods:
            p90 = sorted(hist)[min(len(hist) - 1, math.ceil(0.9 * len(hist)) - 1)]
            fast = speeds[d] > p90
        states[d] = classify_rotation_state(
            up_ratio=up_ratio,
            hhi_top5=hhi,
            lead_streak=streaks.get(d, 1),
            disp_signal=disp,
            fast_rotation=fast,
        )
    return states


def _compute_velocity(
    cross: dict[date, dict[str, float]],
    sorted_dates: list[date],
    cfg: SectorDivergenceConfig,
) -> tuple[dict[date, float], float | None, float | None, list[str]]:
    """电风扇速度计：逐日 mean(|rank_t − rank_{t-lag}|) + 当日分位（250 交易日窗）。

    Returns:
        (velocity 序列, 当日 velocity, 当日分位, notes)；样本不足 → 分位 None 降级。
    """
    notes: list[str] = []

    def _ranks(day: dict[str, float]) -> dict[str, int]:
        ordered = sorted(day.items(), key=lambda kv: kv[1])
        return {code: rank for rank, (code, _) in enumerate(ordered)}

    velocities: dict[date, float] = {}
    for i in range(cfg.velocity_lag_days, len(sorted_dates)):
        d = sorted_dates[i]
        d0 = sorted_dates[i - cfg.velocity_lag_days]
        today, prev = cross.get(d, {}), cross.get(d0, {})
        common = set(today) & set(prev)
        if len(common) < 2:
            continue
        rt, rp = _ranks(today), _ranks(prev)
        velocities[d] = sum(abs(rt[c] - rp[c]) for c in common) / len(common)

    today = sorted_dates[-1] if sorted_dates else None
    v_today = velocities.get(today) if today else None
    if today is None or v_today is None:
        return velocities, None, None, notes
    window = [v for dd, v in velocities.items() if dd <= today][-cfg.velocity_percentile_window :]
    if len(window) < cfg.velocity_min_periods:
        notes.append(f"速度计分位窗 {len(window)} 日 < {cfg.velocity_min_periods} 日守卫，velocity_percentile 降级")
        return velocities, v_today, None, notes
    if len(set(window)) == 1:
        notes.append("速度计分位窗内零变异（序列恒定），分位无意义降级")
        return velocities, v_today, None, notes
    return velocities, v_today, _midrank_percentile(sorted(window), v_today), notes


def _top3_overlap(
    cross: dict[date, dict[str, float]],
    sorted_dates: list[date],
) -> float | None:
    """Top3 次日重合率 = |今日 Top3 ∩ 昨日 Top3| / 3（昨日缺 → None 降级）。"""
    if len(sorted_dates) < 2:
        return None
    today, prev = sorted_dates[-1], sorted_dates[-2]
    t, p = cross.get(today), cross.get(prev)
    if not t or not p:
        return None
    top3_t = {c for c, _ in sorted(t.items(), key=lambda kv: kv[1], reverse=True)[:3]}
    top3_p = {c for c, _ in sorted(p.items(), key=lambda kv: kv[1], reverse=True)[:3]}
    return len(top3_t & top3_p) / 3.0


# ------------------------------------------------------------------
# 虹吸态消费（sector_siphon 复用，历史序列本模块构）
# ------------------------------------------------------------------


def _compute_siphon(
    by_sector: dict[str, list[tuple[date, float, float]]],
    constituents: dict[str, list[str]],
    mf_rows: list[tuple],
    current_date: date,
    cfg: SectorDivergenceConfig,
) -> tuple[float | None, bool, list[str]]:
    """虹吸态识别——money_flow×sector_constituent 聚合板块净流入，detect_siphon_state 复用。

    Returns:
        (siphon_z, is_siphon, notes)；数据缺口 → (None, False, 降级说明)。
    """
    notes: list[str] = []
    if not mf_rows:
        return None, False, ["money_flow 窗内无数据，虹吸态降级"]
    if not constituents:
        return None, False, ["sector_constituent 当日无有效成分，虹吸态降级"]

    # 个股净流入 → (板块, 日) 聚合（板块全集 = 有 K 线的 880 板块）
    flow_by_symbol_day: dict[tuple[date, str], float] = {}
    for row in mf_rows:
        flow_by_symbol_day[(_as_date(row[0]), str(row[1]))] = float(row[2] or 0.0)
    sector_codes = [c for c in by_sector if c in constituents]
    if not sector_codes:
        return None, False, ["板块 K 线与成分映射无交集，虹吸态降级"]
    amounts = _amount_maps(by_sector)

    dates = sorted({d for d, _ in flow_by_symbol_day if d <= current_date})

    def _day_snapshot(dd: date) -> list[SectorFlowSnapshot]:
        snaps: list[SectorFlowSnapshot] = []
        for code in sector_codes:
            amt = amounts[code].get(dd, 0.0)
            net = sum(flow_by_symbol_day.get((dd, s), 0.0) for s in constituents[code])
            snaps.append(SectorFlowSnapshot(name=code, turnover=amt, net_inflow=net))
        return snaps

    def _signals(snaps: list[SectorFlowSnapshot]) -> tuple[float, float, float]:
        total_amt = sum(s.turnover for s in snaps)
        top = sorted(snaps, key=lambda s: s.turnover, reverse=True)[: cfg.siphon_n_top]
        hhi = sum((s.turnover / total_amt) ** 2 for s in top) if total_amt > 0 else 0.0
        total_abs = sum(abs(s.net_inflow) for s in snaps)
        conc = sum(s.net_inflow for s in top) / total_abs if total_abs > 0 else 0.0
        top_ids = {id(s) for s in top}
        rest = [s for s in snaps if id(s) not in top_ids]
        outflow = sum(1 for s in rest if s.net_inflow < 0) / len(rest) if rest else 0.0
        return hhi, conc, outflow

    today_snaps = _day_snapshot(current_date)
    if not any(s.turnover > 0 for s in today_snaps):
        return None, False, [f"{current_date.isoformat()} 板块成交额全 0，虹吸态降级"]

    hhi_hist: list[float] = []
    conc_hist: list[float] = []
    out_hist: list[float] = []
    for d in dates:
        if d >= current_date:
            continue
        hhi, conc, outflow = _signals(_day_snapshot(d))
        hhi_hist.append(hhi)
        conc_hist.append(conc)
        out_hist.append(outflow)
    if len(hhi_hist) < 2:
        notes.append(f"虹吸历史序列 {len(hhi_hist)} 日 < 2，z-score 降级不触发（rolling_zscore 守卫）")

    result = detect_siphon_state(
        today_snaps,
        hhi_hist,
        conc_hist,
        out_hist,
        n_top=cfg.siphon_n_top,
        threshold=cfg.siphon_z_threshold,
    )
    return result.siphon_score, result.is_siphon, notes


# ------------------------------------------------------------------
# 个股分歧度（24 号口径通用化）
# ------------------------------------------------------------------


def _load_top_youzi_seats(path: str) -> set[str]:
    """seat_registry → 一线游资席位名/别名小写集合（youzi 且 风格∈{龙头连板,首板}，对齐 056/057）。

    registry 缺失/解析失败 → 空集合（对打维度静默降级，主入口 notes 留痕）。
    """
    p = Path(path)
    if not p.is_file():
        logger.warning("seat_registry 不存在，龙虎榜对打识别降级为空集合: %s", path)
        return set()
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        logger.warning("seat_registry 解析失败，对打识别降级为空集合: %s", e)
        return set()
    out: set[str] = set()
    for seat in data.get("seats") or []:
        if str(seat.get("seat_type") or "") != "youzi":
            continue
        if str(seat.get("seat_style") or "") not in ("龙头连板", "首板"):
            continue
        name = str(seat.get("seat_name") or "").strip().lower()
        if name:
            out.add(name)
        for alias in seat.get("aliases") or []:
            a = str(alias).strip().lower()
            if a:
                out.add(a)
    return out


def _lhb_fight_map(
    lhb_rows: list[tuple],
    top_youzi: set[str],
    cfg: SectorDivergenceConfig,
) -> dict[str, bool]:
    """龙虎榜买卖对打：买卖两侧均有一线游资 且 |净买入| < 上榜成交额 1%（方向不明）。"""
    by_symbol: dict[str, list[tuple]] = {}
    for row in lhb_rows:
        by_symbol.setdefault(str(row[0]), []).append(row)
    out: dict[str, bool] = {}
    for sym, rows in by_symbol.items():
        buyers = [r for r in rows if r[5] is not None]
        sellers = [r for r in rows if r[6] is not None]
        has_top_buyer = any(str(r[1]).strip().lower() in top_youzi for r in buyers)
        has_top_seller = any(str(r[1]).strip().lower() in top_youzi for r in sellers)
        turnover = sum(float(r[2] or 0.0) + float(r[3] or 0.0) for r in rows)
        net = sum(float(r[4] or 0.0) for r in rows)
        out[sym] = has_top_buyer and has_top_seller and turnover > 0 and abs(net) < cfg.lhb_fight_net_ratio * turnover
    return out


def _compute_stock_divergence(
    stock_rows: list[tuple],
    limit_rows: list[tuple],
    lhb_rows: list[tuple],
    top_youzi: set[str],
    current_date: date,
    cfg: SectorDivergenceConfig,
) -> tuple[list[StockDivergenceWatch], list[str]]:
    """个股分歧度四件合成 + 截面 >80 分位例外清单（只出清单不出方向）。

    divergence = 0.4·z(换手突增倍数, 当日截面) + 0.3·上影占比 + 0.2·炸板 + 0.1·对打。
    """
    notes: list[str] = []
    if not stock_rows:
        return [], ["kline_daily 窗内无数据，个股分歧度降级"]

    # 按个股分组（时间升序）
    by_symbol: dict[str, list[tuple[date, float, float, float, float, float]]] = {}
    for row in stock_rows:
        sym = str(row[0])
        by_symbol.setdefault(sym, []).append(
            (
                _as_date(row[1]),
                float(row[2] or 0.0),
                float(row[3] or 0.0),
                float(row[4] or 0.0),
                float(row[5] or 0.0),
                float(row[6] or 0.0),
            )
        )
    for series in by_symbol.values():
        series.sort(key=lambda x: x[0])

    limit_up_today: dict[str, float] = {
        str(r[0]): float(r[1]) for r in limit_rows if r[1] is not None and float(r[1]) > 0
    }
    fight = _lhb_fight_map(lhb_rows, top_youzi, cfg)

    # 当日可评分宇宙：换手突增倍数 + 上影占比
    entries: dict[str, tuple[float | None, float, bool, bool]] = {}
    for sym, series in by_symbol.items():
        if series[-1][0] != current_date:
            continue
        d, high, low, close, turnover, _pct = series[-1]
        # 上影占比（high==low → 0；脏数据 high<low → 0）
        shadow = (high - close) / (high - low) if high > low else 0.0
        shadow = max(0.0, min(1.0, shadow))
        # 换手突增 = 当日换手 / 前 20 交易日均换手（分母 ≤0 → None 降级该项）
        prior = [t for dd, _, _, _, t, _ in series[:-1] if dd < current_date][-cfg.turnover_mean_days :]
        surge: float | None = None
        if prior:
            mean_t = sum(prior) / len(prior)
            if mean_t > 0:
                surge = turnover / mean_t
        lu = limit_up_today.get(sym)
        broken = bool(lu is not None and high >= lu - cfg.limit_price_tol and close < lu - cfg.limit_price_tol)
        entries[sym] = (surge, shadow, broken, fight.get(sym, False))

    if len(entries) < cfg.watchlist_min_universe:
        return [], [f"个股可评分宇宙 {len(entries)} < {cfg.watchlist_min_universe} 守卫，分歧度清单降级"]

    # 换手突增截面 z-score（缺项按 0 计入合成但不出注解）
    surges = [v[0] for v in entries.values() if v[0] is not None]
    smean, sstd = _mean_std(surges)

    def _z(surge: float | None) -> float:
        if surge is None or sstd == 0.0:
            return 0.0
        return (surge - smean) / sstd

    scores: dict[str, float] = {}
    parts: dict[str, tuple[float | None, float, bool, bool]] = {}
    for sym, (surge, shadow, broken, fought) in entries.items():
        score = 0.4 * _z(surge) + 0.3 * shadow + 0.2 * (1.0 if broken else 0.0) + 0.1 * (1.0 if fought else 0.0)
        scores[sym] = score
        parts[sym] = (surge, shadow, broken, fought)

    sorted_scores = sorted(scores.values())
    watchlist: list[StockDivergenceWatch] = []
    for sym, score in scores.items():
        pct = _midrank_percentile(sorted_scores, score)
        if pct <= cfg.watchlist_percentile:
            continue
        surge, shadow, broken, fought = parts[sym]
        reasons: list[str] = []
        if surge is not None and surge > cfg.turnover_surge_flag:
            reasons.append(f"换手突增{surge:.1f}×(>{cfg.turnover_surge_flag})")
        if shadow > cfg.upper_shadow_flag:
            reasons.append(f"上影占比{shadow:.2f}(>{cfg.upper_shadow_flag})")
        if broken:
            reasons.append("炸板（触板未封）")
        if fought:
            reasons.append("龙虎榜买卖对打（双侧一线游资且净额<1%）")
        if not reasons:
            reasons.append(f"截面分位{pct:.0%}>{cfg.watchlist_percentile:.0%}（多因子合成）")
        watchlist.append(
            StockDivergenceWatch(
                symbol=sym,
                score=score,
                percentile=pct,
                turnover_surge=surge,
                upper_shadow=shadow,
                limit_broken=broken,
                lhb_fight=fought,
                reasons=reasons,
            )
        )
    watchlist.sort(key=lambda w: w.score, reverse=True)
    return watchlist, notes


# ------------------------------------------------------------------
# M1-②c 族相对强度雷达（44号 §9.2 通道 c）
# ------------------------------------------------------------------


def _compute_rs_radar(
    labels: SectorAttributeLabels,
    constituents: dict[str, list[str]],
    stock_rows: list[tuple],
    market_ret_today: float | None,
    adv_ratio_today: float | None,
    adv_ratio_prev: float | None,
    current_date: date,
) -> tuple[float | None, float | None, list[str], list[str]]:
    """防御/进攻族相对强度：rs_ratio = mean_ret(进攻族) − mean_ret(防御族)。

    rs_z < −1 且指数红 → 避险抱团注解（情绪差）；rs_z > +1 且 adv 改善 → 真情绪好注解。
    族收益 = 成分股当日 pct_change 等权均值（881xxx 无板块 K 线实证裁定，成分 SCD-2 时点过滤）。

    Returns:
        (rs_ratio, rs_z, annotations, notes)；族成分/个股数据缺口 → 对应 None 降级。
    """
    annotations: list[str] = []
    notes: list[str] = []

    defensive_stocks = sorted({s for b in labels.defensive_boards for s in constituents.get(b, [])})
    offensive_stocks = sorted({s for b in labels.offensive_boards for s in constituents.get(b, [])})
    if not defensive_stocks or not offensive_stocks:
        return None, None, annotations, ["族标签板块无当前有效成分（sector_constituent 缺口），rs 雷达降级"]

    defensive_set = set(defensive_stocks)
    offensive_set = set(offensive_stocks)
    ret_by_day_symbol: dict[date, dict[str, float]] = {}
    for row in stock_rows:
        d = _as_date(row[1])
        ret_by_day_symbol.setdefault(d, {})[str(row[0])] = float(row[6] or 0.0) * 0.01

    rs_series: list[tuple[date, float]] = []
    for d in sorted(ret_by_day_symbol):
        if d > current_date:
            continue
        day = ret_by_day_symbol[d]
        off = [day[s] for s in offensive_stocks if s in day]
        dfn = [day[s] for s in defensive_stocks if s in day]
        if off and dfn:
            rs_series.append((d, sum(off) / len(off) - sum(dfn) / len(dfn)))

    rs_today = next((v for d, v in rs_series if d == current_date), None)
    if rs_today is None:
        return None, None, annotations, [f"{current_date.isoformat()} 族成分当日收益缺失，rs 雷达降级"]

    window = [v for d, v in rs_series if d < current_date][-labels.rs_sigma_window :]
    rs_z: float | None = None
    if len(window) < labels.rs_min_periods:
        notes.append(f"rs σ 窗 {len(window)} 日 < {labels.rs_min_periods} 日守卫，rs_z 降级")
    else:
        rs_z = _zscore(rs_today, window)

    if rs_z is not None:
        if rs_z < -1.0 and market_ret_today is not None and market_ret_today > 0:
            annotations.append(
                f"避险抱团：进攻族−防御族 rs_z={rs_z:.2f}<−1σ 而指数红（{market_ret_today:+.2%}）——指数失真嫌疑，情绪差"
            )
        elif (
            rs_z > 1.0
            and adv_ratio_today is not None
            and adv_ratio_prev is not None
            and adv_ratio_today > adv_ratio_prev
        ):
            annotations.append(
                f"真情绪好：进攻族领涨 rs_z={rs_z:.2f}>+1σ 且上涨家数占比改善（{adv_ratio_prev:.0%}→{adv_ratio_today:.0%}）"
            )
    return rs_today, rs_z, annotations, notes


# ------------------------------------------------------------------
# SEC-03 概率标定器（5 状态 × 后续 3/5 日条件频率）
# ------------------------------------------------------------------


def _calibrate_states(
    states: dict[date, RotationState],
    market_series: list[tuple[date, float]],
    cfg: SectorDivergenceConfig,
) -> list[StateConditionalStat]:
    """5 状态 × 后续 3/5 日涨跌历史条件频率（滚动窗内重放，可审计可复算）。

    频率 = 该状态样本中 后续 N 交易日收益 < −2% 的占比；样本 <calib_min_samples
    → sufficient=False（不隐藏频率，标注供消费方决断，禁伪精确点概率）。
    """
    market = [(d, c) for d, c in market_series if c > 0]
    if len(market) < 2:
        return []
    dates = [d for d, _ in market]
    closes = [c for _, c in market]
    pos = {d: i for i, d in enumerate(dates)}

    buckets: dict[RotationState, dict[int, list[float]]] = {}
    for d, state in states.items():
        i = pos.get(d)
        if i is None:
            continue
        for horizon in cfg.calib_forward_days:
            j = i + horizon
            if j < len(dates):
                buckets.setdefault(state, {}).setdefault(horizon, []).append(closes[j] / closes[i] - 1.0)

    out: list[StateConditionalStat] = []
    for state in RotationState:
        fwd = buckets.get(state, {})
        r3 = fwd.get(3, [])
        r5 = fwd.get(5, [])
        n = max(len(r3), len(r5))
        if n == 0:
            continue
        freq3 = sum(1 for r in r3 if r < cfg.calib_down_threshold) / len(r3) if r3 else None
        freq5 = sum(1 for r in r5 if r < cfg.calib_down_threshold) / len(r5) if r5 else None
        out.append(
            StateConditionalStat(
                state=state.value,
                n_samples=n,
                freq_down_3d=freq3,
                freq_down_5d=freq5,
                sufficient=n >= cfg.calib_min_samples,
            )
        )
    return out


def _current_state_summary(
    state: RotationState,
    stats: list[StateConditionalStat],
) -> str:
    """当前状态条件频率中文摘要（44号示例口径，可审计）。"""
    stat = next((s for s in stats if s.state == state.value), None)
    if stat is None:
        return f"当前状态={state.value}；滚动窗内无该状态历史前向观测样本"
    freq = f"{stat.freq_down_3d:.0%}" if stat.freq_down_3d is not None else "无 3 日观测"
    suffix = "" if stat.sufficient else "（样本不足 insufficient）"
    return f"当前状态={state.value}；该状态历史后续 3 日下跌>2% 频率={freq}（样本 N={stat.n_samples}）{suffix}"


def _degraded_result(date_str: str, note: str) -> SectorDivergenceResult:
    logger.warning("板块分歧度分析降级: %s", note)
    return SectorDivergenceResult(date=date_str, degraded=True, notes=[note])


# ------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------


def compute_sector_divergence(
    trade_date: str | date | datetime | None = None,
    ch_client: Any | None = None,
    config: SectorDivergenceConfig | None = None,
) -> SectorDivergenceResult:
    """主入口：板块分歧度与轮动速度计 + SEC-03 概率标定 + M1-②c 族相对强度雷达。

    Args:
        trade_date: 数据日；None 时取 kline_sector_880 最新数据日（PIT 数据日口径）。
        ch_client: clickhouse-driver 鸭子类型（execute(sql, params) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client，不可得→degraded。
        config: 阈值配置（None 用默认 44号 §9.13/§9.2 + 实证口径）。

    Returns:
        SectorDivergenceResult；主数据（kline_sector_880）缺失/查询异常 → degraded=True
        空结果不炸；虹吸/个股分歧/rs 雷达/标定器各维度独立降级互不累及（notes 留痕）。
    """
    cfg = config or SectorDivergenceConfig()

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        d = _normalize_date(trade_date) if trade_date is not None else date.today()
        return _degraded_result(d.isoformat(), "ch_client 未注入且默认客户端不可用")

    if trade_date is None:
        try:
            latest = client.execute(SQL_LATEST_SECTOR_DATE, {})
        except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
            return _degraded_result("unknown", f"最新板块数据日查询异常: {e!r}")
        if not latest or latest[0][0] is None:
            return _degraded_result("unknown", "kline_sector_880 无任何日 K 数据")
        d = _as_date(latest[0][0])
    else:
        d = _normalize_date(trade_date)
    date_str = d.isoformat()

    # 主数据：板块日 K 历史窗（5 状态/速度计/标定器/市场收益代理共用）
    sector_start = d - timedelta(days=cfg.sector_lookback_calendar_days)
    try:
        sector_rows = client.execute(SQL_SECTOR_KLINE_WINDOW, {"trade_date": d, "start_date": sector_start})
    except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
        return _degraded_result(date_str, f"kline_sector_880 查询异常: {e!r}")
    if not sector_rows:
        return _degraded_result(date_str, f"{date_str} 板块 K 线窗内无数据（非交易日或未采集）")

    notes: list[str] = []
    annotations: list[str] = []
    by_sector, all_dates = _daily_close_amount(sector_rows)
    if d not in all_dates:
        return _degraded_result(date_str, f"{date_str} 当日无板块 K 线（非交易日或未采集）")
    sorted_dates = [dd for dd in all_dates if dd <= d]
    leaders, cross = _leader_series(by_sector, sorted_dates)
    streaks = _lead_streaks(leaders, sorted_dates)

    # ── a) 5 状态消费接入 ──
    states = _build_rotation_states(by_sector, sorted_dates, cfg)
    today_state = states.get(d)
    top_risk = today_state in (RotationState.CONSENSUS_CLIMAX, RotationState.DISTRIBUTION_RISK)
    if today_state is not None and top_risk:
        annotations.append(f"板块 5 状态={today_state.value}：见顶/派发风险标记（M2 降档触发输出）")
    lead_streak = streaks.get(d)

    # ── b) 电风扇速度计 ──
    velocity, v_today, v_pct, v_notes = _compute_velocity(cross, sorted_dates, cfg)
    notes.extend(v_notes)
    fan_market = v_pct is not None and v_pct > cfg.fan_market_percentile
    if fan_market:
        annotations.append(f"电风扇行情：轮动速度 {v_today:.1f} 分位 {v_pct:.0%}>75%（快速轮动无主线）")
    overlap = _top3_overlap(cross, sorted_dates)
    one_day = overlap is not None and overlap < cfg.top3_overlap_threshold
    if one_day:
        annotations.append(f"一日游生态：Top3 次日重合率 {overlap:.0%}<20%")
    no_mainline = lead_streak is not None and lead_streak < cfg.lead_streak_no_mainline and fan_market
    if no_mainline:
        annotations.append("无主线混沌：连续领涨<2 日且轮动速度>75 分位（混沌/下跌中继注解）")

    # ── c-d) 成分映射（虹吸聚合 + rs 雷达共用，一次查询） ──
    constituents: dict[str, list[str]] = {}
    try:
        for row in client.execute(SQL_SECTOR_CONSTITUENTS, {"trade_date": d}):
            constituents.setdefault(str(row[0]), []).append(str(row[1]))
    except Exception as e:  # noqa: BLE001 — 成分缺失虹吸/rs 独立降级
        notes.append(f"sector_constituent 查询异常，虹吸/rs 维度降级: {e!r}")

    # ── c) 虹吸态消费（独立降级） ──
    siphon_z: float | None = None
    siphon_flag = False
    try:
        mf_start = d - timedelta(days=cfg.siphon_lookback_calendar_days)
        mf_rows = client.execute(SQL_MONEY_FLOW_WINDOW, {"trade_date": d, "start_date": mf_start})
        siphon_z, siphon_flag, siphon_notes = _compute_siphon(by_sector, constituents, mf_rows, d, cfg)
        notes.extend(siphon_notes)
        if siphon_flag:
            annotations.append(f"虹吸态：z={siphon_z:.2f}>1.5σ（极端分化）")
    except Exception as e:  # noqa: BLE001 — 虹吸部件异常独立降级
        notes.append(f"money_flow 查询异常，虹吸态降级: {e!r}")
    siphon_chaos = siphon_flag and fan_market
    if siphon_chaos:
        annotations.append("极端分化+无主线混沌共振（虹吸 z>1.5σ 且 电风扇>75 分位，M2 降档评估）")

    # ── 市场收益代理（880001）与涨跌广度 ──
    market_rows = [(_as_date(r[1]), float(r[2] or 0.0)) for r in sector_rows if str(r[0]) == cfg.market_index_code]
    market_series = sorted(set(market_rows), key=lambda x: x[0])
    market_ret_today: float | None = None
    if len(market_series) >= 2 and market_series[-1][0] == d and market_series[-2][1] > 0:
        market_ret_today = market_series[-1][1] / market_series[-2][1] - 1.0

    adv_today: float | None = None
    adv_prev: float | None = None
    try:
        breadth_rows = client.execute(SQL_BREADTH_WINDOW, {"trade_date": d, "start_date": d - timedelta(days=10)})
        breadth = {_as_date(r[0]): (int(r[1]) / int(r[2]) if int(r[2]) > 0 else None) for r in breadth_rows}
        bdays = sorted(b for b in breadth if b <= d)
        if bdays:
            adv_today = breadth[bdays[-1]] if bdays[-1] == d else None
            if len(bdays) >= 2:
                adv_prev = breadth[bdays[-2]] if bdays[-1] == d else None
    except Exception as e:  # noqa: BLE001 — 广度缺失仅抑制"真情绪好"注解
        notes.append(f"涨跌广度查询异常（fail-closed 抑制真情绪好注解）: {e!r}")

    # ── e) 个股分歧度（独立降级） ──
    watchlist: list[StockDivergenceWatch] = []
    stock_start = d - timedelta(days=cfg.stock_lookback_calendar_days)
    stock_rows: list[tuple] = []
    try:
        stock_rows = client.execute(SQL_STOCK_KLINE_WINDOW, {"trade_date": d, "start_date": stock_start})
    except Exception as e:  # noqa: BLE001 — 个股 K 线缺失，个股分歧/rs 独立降级
        notes.append(f"kline_daily 查询异常，个股分歧/rs 维度降级: {e!r}")
        stock_rows = []
    if stock_rows:
        limit_rows: list[tuple] = []
        lhb_rows: list[tuple] = []
        try:
            limit_rows = client.execute(SQL_STK_LIMIT_TODAY, {"trade_date": d})
        except Exception as e:  # noqa: BLE001 — 炸板腿缺失按无炸板处理（fail-open 留痕）
            notes.append(f"stk_limit 查询异常，炸板标记按 0 处理: {e!r}")
        top_youzi: set[str] = set()
        try:
            lhb_rows = client.execute(SQL_LHB_TODAY, {"trade_date": d})
            top_youzi = _load_top_youzi_seats(cfg.seat_registry_path)
            if not top_youzi:
                notes.append("seat_registry 一线游资集合为空，对打识别降级")
        except Exception as e:  # noqa: BLE001 — 龙虎榜腿缺失按无对打处理
            notes.append(f"dragon_tiger_seat 查询异常，对打标记按 0 处理: {e!r}")
        watchlist, w_notes = _compute_stock_divergence(stock_rows, limit_rows, lhb_rows, top_youzi, d, cfg)
        notes.extend(w_notes)
        if watchlist:
            annotations.append(f"个股分歧例外清单 {len(watchlist)} 只（截面>80 分位，禁新开仓注解；只出清单不出方向）")

    # ── f) M1-②c 族相对强度雷达（独立降级） ──
    rs_ratio: float | None = None
    rs_z: float | None = None
    try:
        labels = load_sector_attribute_labels(cfg.labels_path)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
        notes.append(f"板块族标签加载失败，rs 雷达降级: {e!r}")
    else:
        if stock_rows:
            rs_ratio, rs_z, rs_ann, rs_notes = _compute_rs_radar(
                labels, constituents, stock_rows, market_ret_today, adv_today, adv_prev, d
            )
            annotations.extend(rs_ann)
            notes.extend(rs_notes)
        else:
            notes.append("个股 K 线缺失，rs 雷达随个股维度一并降级")

    # ── g) SEC-03 概率标定器 ──
    stats = _calibrate_states(states, market_series, cfg)
    if not stats:
        notes.append("标定器滚动窗内无可复算样本（板块 K 线历史积累期）")
    summary = _current_state_summary(today_state, stats) if today_state is not None else None

    return SectorDivergenceResult(
        date=date_str,
        rotation_state=today_state.value if today_state is not None else None,
        watch_score=watch_score(today_state) if today_state is not None else None,
        top_risk_flag=top_risk,
        siphon_z=siphon_z,
        siphon_flag=siphon_flag,
        rotation_velocity=v_today,
        velocity_percentile=v_pct,
        fan_market_flag=fan_market,
        top3_overlap=overlap,
        one_day_ecology=one_day,
        lead_streak=lead_streak,
        no_mainline_flag=no_mainline,
        siphon_chaos_flag=siphon_chaos,
        rs_ratio=rs_ratio,
        rs_z=rs_z,
        state_conditional_stats=stats,
        current_state_summary=summary,
        stock_watchlist=watchlist,
        annotations=annotations,
        degraded=False,
        notes=notes,
    )
