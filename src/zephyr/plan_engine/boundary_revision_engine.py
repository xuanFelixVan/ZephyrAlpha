# [BLUEPRINT] MOD-PLAN-006 | 待统筹登记（92号清单 §8.3 / 44号 §3 M2 + §9.5）
# [MODULE] zephyr.plan_engine.boundary_revision_engine
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.reporting.prediction_log_writer(log_prediction/ensure_prediction_log_table); zephyr.shared.state_store(JsonStateStore 接口鸭子类型注入); 触发源类型仅 TYPE_CHECKING 引用（signal_ashare 波3/波4 输出，运行时鸭子类型读字段）
# [CONSUMERS] MOD-PLAN-001(TomorrowBoundary.apply_revision 应用经修正边界); MOD-PLAN-003(closing_session_decision 尾盘决策在修正后边界内执行); prediction_log(plan_revision 事件，44号 §12.1 M4-②)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 修正仅当日有效（次日盘前 MOD-PLAN-001 基线覆盖，不跨日累积；非当日消费拒发/标 expired）; 升档×1.2 封顶 firm 单票 8%/组合硬约束（30号 §2.2，firm 层执行）; 防抖≥15min + 升/降档当日各最多 1 次冷却; 触发源缺数据=该源跳过不炸整体; 升降档同窗同时确认→降档优先（安全方向）; 输出纯 dataclass JSON 可序列化
# [MODIFY-GUARD] blueprint.md（待统筹登记）
# [STABILITY] testing
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BoundaryRevisionError(ZA-PLAN-0006)：trade_date/eval_slot/eval_time/baseline_tier 非法 fail-closed 抛出；触发源缺数据=该源跳过（不抛）；prediction_log 写入失败 fail-open（logged=False+reasons 留痕）
# [TESTS] tests/plan_engine/test_boundary_revision_engine.py
# [A_module] module_id=MOD-PLAN-006 | layer=module | stability=testing | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
BoundaryRevisionEngine — 盘中次日预案边界修正引擎 (MOD-PLAN-006)

44号 §3 M2 落码：盘中实时输入→当晚边界档位的修正通道（T+1 场景）。
决策语义=不输出"明天涨/跌"，输出"今晚的边界该收多紧"
（41号 §3.10"边界比聪明更重要"；90号 §7 不预测裁定严格绕行，只画栏杆不算命）。

流程（44号 §3）：
    盘前 MOD-PLAN-001 生成 TomorrowBoundary 基线档位（保守/正常/进攻）
        → 盘中 M1 实时情绪流（波3/波4 触发源经 Optional 入参注入，缺数据=该源跳过）
        → 14:00/14:45 两时点评估（与 MOD-PLAN-003 尾盘窗口对齐）：
          情绪显著恶化→降档（加仓上限收紧）；情绪显著改善→升档（上限放宽）
        → MOD-PLAN-003 尾盘决策在修正后边界内执行

修正规则（44号 §9.5 设计真源，全参数 config 化）：
    - 防抖：触发信号须持续 ≥15min 才生效（防单分钟毛刺）——首次出现只登记
      first_seen，跨调用持续计时经 state_store 持久化；信号中断→计时清零。
    - 冷却：升/降档当日各最多 1 次（状态按 trade_date 命名空间隔离，次日自然重置）。
    - 降档（任一满足）：①综合情绪分<35 且 lu_net_rate_30m<0（M1 30m 字段未落地前
      以 lu_net_rate_5m 口径代理+detail 标注 rate_proxy_5m）；②distortion_flag
      且 spread>2σ；③大幅回撤数≥7；④IM 基差贴水 30min 急扩>1.5σ（机构对冲踩踏）；
      ⑤板块 5 状态=CONSENSUS_CLIMAX/DISTRIBUTION_RISK（见顶/派发风险）；
      ⑥虹吸态 z>1.5σ 且 电风扇速度计>75 分位（极端分化+无主线混沌共振）；
      ⑦BS-005 外围冲击盘中触发。
    - 升档（全部满足）：综合情绪分>65 且 ŷ_full≥1.1×20日均量 且 rs_ratio>0（进攻族领涨）。
    - 档位映射：保守=加仓上限×0.5 + 禁加仓价位上移 0.5×ATR(14)；进攻=加仓上限×1.2
      （封顶 firm 单票 8%/组合硬约束，30号 §2.2——FirmRiskAggregator SINGLE_NAME_CAP
      在 firm 层执行，本模块只出缩放系数不越层比较口径）；正常=不变。
      升/降档同一评估窗同时确认时→降档优先（安全方向，H 级语义）。
    - 修正仅当日有效：revision 带 trade_date+expired 标记，is_effective_on() 供消费方
      校验；次日盘前 MOD-PLAN-001 重新生成基线覆盖，修正不跨日累积
      （防"昨日恐慌今日过期"的滞后污染）。
    - 留痕：每次实际改档写 prediction_log（prediction_type="plan_revision"，
      时间/触发条件/原档位/新档位，供 54号对账归因与 M4-② 消费）；
      写入失败 fail-open（logged=False+reasons 留痕，不阻塞盘中评估）。

不做什么：不做方向点预测（90号 §7）/ 不直接改 TomorrowBoundary（消费方经
         TomorrowBoundary.apply_revision 应用）/ 不执行下单 / 不读库取数
         （触发源全部经入参注入，本模块纯计算）。

依据: 44_premarket_intraday_decision_upgrade §3 + §9.5；30号 §2.2 firm 硬约束
SSoT: depgraph MOD-PLAN-006（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: trade_date + eval_slot(14:00/14:45) + 触发源（MarketSentimentResult/DistortionDetectionResult/FuturesBasisSnapshot/SectorDivergenceResult/VolumeForecastResult/rs_ratio/bs005_triggered，全 Optional）
# 特征: 七降档触发源 + 升档三条件（阈值全 config 化）
# 算法: 触发采集（缺数据跳过）→ 防抖（持续≥15min，state_store 跨调用计时）→ 冷却（升/降当日各 1 次）→ 档位映射（保守×0.5+禁加仓上移0.5ATR / 进攻×1.2 封顶 firm 硬约束）→ plan_revision 留痕
# 输出: BoundaryRevision（frozen dataclass，JSON 可序列化，仅当日有效）

"""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
)

if TYPE_CHECKING:  # 触发源类型仅注解用（运行时鸭子类型读字段，缺数据=该源跳过）
    from zephyr.shared.state_store import JsonStateStore
    from zephyr.signal_ashare.futures_basis_monitor import FuturesBasisSnapshot
    from zephyr.signal_ashare.market_sentiment_analyzer import (
        DistortionDetectionResult,
        MarketSentimentResult,
        VolumeForecastResult,
    )
    from zephyr.signal_ashare.sector_divergence import SectorDivergenceResult

log = logging.getLogger(__name__)

__all__: Final = [
    "BoundaryRevision",
    "BoundaryRevisionConfig",
    "BoundaryRevisionEngine",
    "BoundaryRevisionError",
    "InMemoryJsonStateStore",
    "evaluate_boundary_revision",
]

# ── 常量（44号 §9.5 参数默认值，全部可经 BoundaryRevisionConfig 覆盖）──

EVAL_SLOTS: Final = ("14:00", "14:45")  # 评估时点（与 MOD-PLAN-003 尾盘窗口对齐）
DEBOUNCE_MINUTES: Final = 15  # 防抖：触发信号须持续 ≥15min 才生效（防单分钟毛刺）
COOLDOWN_PER_DIRECTION: Final = 1  # 冷却：升/降档当日各最多 1 次

SENTIMENT_DOWNGRADE_THRESHOLD: Final = 35.0  # 降档：综合情绪分 <35（且 lu_net_rate<0）
SENTIMENT_UPGRADE_THRESHOLD: Final = 65.0  # 升档：综合情绪分 >65
DISTORTION_SPREAD_SIGMA: Final = 2.0  # 降档：distortion_flag 且 spread >2σ
DRAWDOWN_COUNT_THRESHOLD: Final = 7  # 降档：大幅回撤数 ≥7
IM_BASIS_SIGMA: Final = 1.5  # 降档：IM 基差贴水 30min 急扩 >1.5σ
SIPHON_Z_THRESHOLD: Final = 1.5  # 降档：虹吸态 z >1.5σ
VELOCITY_PERCENTILE_THRESHOLD: Final = 0.75  # 降档：电风扇速度计 >75 分位（共振腿）
VOLUME_CONFIRM_RATIO: Final = 1.1  # 升档：ŷ_full ≥1.1×20 日均量

TIER_CONSERVATIVE: Final = "CONSERVATIVE"  # 保守
TIER_NORMAL: Final = "NORMAL"  # 正常
TIER_AGGRESSIVE: Final = "AGGRESSIVE"  # 进攻
TIERS: Final = frozenset({TIER_CONSERVATIVE, TIER_NORMAL, TIER_AGGRESSIVE})

CONSERVATIVE_CAP_SCALE: Final = 0.5  # 保守=加仓上限×0.5
AGGRESSIVE_CAP_SCALE: Final = 1.2  # 进攻=加仓上限×1.2
CONSERVATIVE_NO_ADD_SHIFT_ATR: Final = -0.5  # 保守=禁加仓价位下移 0.5×ATR(14)——2026-08-22 统筹裁定：44号 §9.5"上移"与 §3"下移"张力按语义裁定=下移（no_add_price=接近即禁加仓的防追高线，保守=更严=线更低；negative=下移）
ATR_WINDOW: Final = 14  # ATR 窗口（位移倍数的名义口径，ATR 值由消费方计算注入）

# firm 单票硬上限 8%（30号 §2.2/§2.4；SSoT=position/core/firm_risk_aggregator.py SINGLE_NAME_CAP）
# ——升档 ×1.2 后的封顶由 firm 层执行，本模块只出缩放系数（口径不同不越层比较）
FIRM_SINGLE_NAME_CAP: Final = 0.08

# 触发源键（留痕/防抖计时/测试断言的稳定标识）
TRIGGER_SENTIMENT_BREADTH: Final = "sentiment_breadth"  # ①情绪分<35 且 lu_net_rate<0
TRIGGER_DISTORTION_SPREAD: Final = "distortion_spread"  # ②护盘失真且 spread>2σ
TRIGGER_DRAWDOWN_COUNT: Final = "drawdown_count"  # ③大幅回撤数≥7
TRIGGER_IM_BASIS_DISCOUNT: Final = "im_basis_discount"  # ④IM 贴水 30min 急扩>1.5σ
TRIGGER_SECTOR_TOP_RISK: Final = "sector_top_risk"  # ⑤板块 5 状态见顶/派发
TRIGGER_SIPHON_CHAOS: Final = "siphon_chaos"  # ⑥虹吸×电风扇共振
TRIGGER_BS005_SHOCK: Final = "bs005_shock"  # ⑦BS-005 外围冲击盘中触发
TRIGGER_UPGRADE: Final = "upgrade_conditions"  # 升档三条件（全部满足）

DOWNGRADE_TRIGGERS: Final = (
    TRIGGER_SENTIMENT_BREADTH,
    TRIGGER_DISTORTION_SPREAD,
    TRIGGER_DRAWDOWN_COUNT,
    TRIGGER_IM_BASIS_DISCOUNT,
    TRIGGER_SECTOR_TOP_RISK,
    TRIGGER_SIPHON_CHAOS,
    TRIGGER_BS005_SHOCK,
)

TOP_RISK_STATES: Final = frozenset({"CONSENSUS_CLIMAX", "DISTRIBUTION_RISK"})  # 板块见顶/派发态
IM_PRODUCT_KEY: Final = "IM"  # 中证1000 期指（对中小盘/题材情绪最敏感，44号 §9.8）

STATE_NAMESPACE_PREFIX: Final = "boundary_revision"  # state_store 命名空间前缀（按日隔离）
PREDICTION_TYPE_PLAN_REVISION: Final = "plan_revision"  # 留痕事件类型（44号 §9.5）
MODULE_LOG_NAME: Final = "plan_engine.boundary_revision_engine"  # prediction_log.module 口径


class BoundaryRevisionError(ValueError):
    """边界修正错误（ZA-PLAN-0006）——输入非法/跨日消费等契约违例 fail-closed。

    继承 ValueError 保持向后兼容（调用方/测试按 ValueError 捕获仍生效）。
    """

    error_code = "ZA-PLAN-0006"


# ── 状态存取（冷却/防抖持久化；JsonStateStore 同接口鸭子类型）──


class InMemoryJsonStateStore:
    """内存态状态存取（JsonStateStore 同接口，测试/单进程缺省后端）。

    save/load 均经 JSON 往返深拷贝——与文件后端同口径校验可序列化性，
    且避免消费方原地改坏存档。无跨进程持久化：生产必须注入 JsonStateStore
    （防抖/冷却状态才能跨评估进程存活）。
    """

    def __init__(self) -> None:
        self._data: dict[str, dict] = {}

    def save(self, namespace: str, payload: dict) -> None:
        self._data[namespace] = json.loads(json.dumps(payload, ensure_ascii=False, default=str))

    def load(self, namespace: str) -> dict | None:
        rec = self._data.get(namespace)
        return json.loads(json.dumps(rec, ensure_ascii=False)) if rec is not None else None

    def delete(self, namespace: str) -> bool:
        return self._data.pop(namespace, None) is not None


# ── 配置契约（44号 §9.5 全参数 config 化，默认值=设计真源口径）──


@dataclass(frozen=True)
class BoundaryRevisionConfig:
    """盘中边界修正配置（全参数可调，默认值=44号 §9.5 设计真源口径）。"""

    eval_slots: tuple[str, ...] = EVAL_SLOTS  # 评估时点（尾盘窗口对齐）
    debounce_minutes: int = DEBOUNCE_MINUTES  # 防抖持续分钟数
    cooldown_per_direction: int = COOLDOWN_PER_DIRECTION  # 升/降档当日各最多次数
    sentiment_downgrade_threshold: float = SENTIMENT_DOWNGRADE_THRESHOLD
    sentiment_upgrade_threshold: float = SENTIMENT_UPGRADE_THRESHOLD
    distortion_spread_sigma: float = DISTORTION_SPREAD_SIGMA
    drawdown_count_threshold: int = DRAWDOWN_COUNT_THRESHOLD
    im_basis_sigma: float = IM_BASIS_SIGMA
    siphon_z_threshold: float = SIPHON_Z_THRESHOLD
    velocity_percentile_threshold: float = VELOCITY_PERCENTILE_THRESHOLD
    volume_confirm_ratio: float = VOLUME_CONFIRM_RATIO
    conservative_cap_scale: float = CONSERVATIVE_CAP_SCALE
    aggressive_cap_scale: float = AGGRESSIVE_CAP_SCALE
    conservative_no_add_shift_atr: float = CONSERVATIVE_NO_ADD_SHIFT_ATR


DEFAULT_CONFIG: Final = BoundaryRevisionConfig()


# ── 输出契约（MOD-PLAN-006 产出，JSON 可序列化，供消费方+prediction_log 落库）──


@dataclass(frozen=True)
class BoundaryRevision:
    """盘中边界修正结果（MOD-PLAN-006 输出契约，frozen dataclass JSON 可序列化）。

    仅当日有效（44号 §3 修正有效期）：is_effective_on() 供消费方校验，
    非当日消费拒发/标 expired（with_expired）；次日基线由 MOD-PLAN-001 覆盖，
    修正不跨日累积。
    """

    trade_date: str  # 交易日（ISO，修正有效期锚）
    eval_slot: str  # 评估时点标签（14:00/14:45）
    eval_time: str  # 实际评估时钟 HH:MM（防抖计时口径，缺省=eval_slot）
    original_tier: str  # 原档位（当日前次修正后滚动档位；首日=baseline_tier）
    revised_tier: str  # 新档位（未改档时=original_tier）
    revision_applied: bool  # 本次评估是否实际改档
    direction: str  # DOWNGRADE / UPGRADE / NONE
    triggers: list[str]  # 防抖确认触发的触发源键（含被冷却拒发的；未确认不入列）
    pending_triggers: list[str]  # 已出现但防抖未满（持续<15min）的触发源键
    debounce_proof: dict[str, dict[str, Any]]  # 触发源→{first_seen, elapsed_min, confirmed}
    cooldown: dict[str, int]  # {downgrades_used, upgrades_used, max_per_direction}
    position_cap_scale: float  # 加仓上限缩放（保守 0.5 / 正常 1.0 / 进攻 1.2）
    no_add_price_shift: float  # 禁加仓价位位移（ATR(14) 倍数，负=下移；保守 -0.5，2026-08-22 裁定）
    reasons: list[str]  # 决策理由链（留痕）
    trace: dict[str, Any]  # 触发源明细/跳过原因留痕
    expired: bool = False  # 过期标记（跨日消费方拒发）
    logged: bool = False  # plan_revision 事件是否已落 prediction_log

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（prediction_log 落库契约）。"""
        return asdict(self)

    def is_effective_on(self, trade_date: str) -> bool:
        """修正在给定交易日是否有效（仅当日有效：同日且未过期）。"""
        return (not self.expired) and self.trade_date == trade_date

    def with_expired(self) -> BoundaryRevision:
        """返回 expired=True 的副本（frozen，不改原实例）。"""
        return replace(self, expired=True)


# ── 盘中边界修正引擎 ──


def _validate_trade_date(v: str | datetime.date) -> str:
    """交易日归一（date/ISO 字符串→ISO）；非法抛 BoundaryRevisionError（fail-closed）。"""
    if isinstance(v, datetime.date):
        return v.isoformat()
    try:
        return datetime.date.fromisoformat(str(v)).isoformat()
    except ValueError as exc:
        raise BoundaryRevisionError(f"trade_date 非法（须 YYYY-MM-DD）: {v!r}") from exc


def _parse_hhmm(s: str) -> int:
    """HH:MM → 自午夜分钟数；非法抛 BoundaryRevisionError（fail-closed）。"""
    try:
        t = datetime.datetime.strptime(str(s), "%H:%M")
    except ValueError as exc:
        raise BoundaryRevisionError(f"eval_time/eval_slot 非法（须 HH:MM）: {s!r}") from exc
    return t.hour * 60 + t.minute


def _min_to_hhmm(m: int) -> str:
    """自午夜分钟数 → HH:MM 字符串（防抖留痕可读口径）。"""
    return f"{m // 60:02d}:{m % 60:02d}"


class BoundaryRevisionEngine:
    """盘中边界修正引擎（MOD-PLAN-006）。

    state_store 注入 JsonStateStore（生产持久化）或 InMemoryJsonStateStore
    （测试）；None=每次构造新建内存态（无跨调用状态，防抖/冷却仅当次有效）。
    触发源全部 Optional 入参注入（波3/波4 输出），缺数据=该触发源跳过。
    """

    def __init__(
        self,
        state_store: JsonStateStore | InMemoryJsonStateStore | None = None,
        config: BoundaryRevisionConfig | None = None,
        log_db_path: str | Path | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._store = state_store if state_store is not None else InMemoryJsonStateStore()
        self._log_db_path = log_db_path

    # ── 状态（冷却/防抖；按 trade_date 命名空间隔离，次日自然重置）──────────

    @staticmethod
    def _namespace(trade_date: str) -> str:
        return f"{STATE_NAMESPACE_PREFIX}_{trade_date}"

    def _load_state(self, trade_date: str) -> dict[str, Any]:
        rec = self._store.load(self._namespace(trade_date))
        if rec is None:
            return {
                "trade_date": trade_date,
                "current_tier": None,  # None=未修正（取调用方注入 baseline_tier）
                "downgrades_used": 0,
                "upgrades_used": 0,
                "debounce_first_seen": {},  # 触发源键 → 首次出现（自午夜分钟数）
            }
        return rec

    def _save_state(self, trade_date: str, state: dict[str, Any]) -> None:
        self._store.save(self._namespace(trade_date), state)

    # ── 触发采集（44号 §9.5 七降档+升档三条件；缺数据=该源跳过）──────────────

    def _collect_triggers(
        self,
        sentiment: MarketSentimentResult | None,
        distortion: DistortionDetectionResult | None,
        futures_basis: FuturesBasisSnapshot | None,
        sector_divergence: SectorDivergenceResult | None,
        volume_forecast: VolumeForecastResult | None,
        rs_ratio: float | None,
        bs005_triggered: bool,
    ) -> tuple[list[str], dict[str, Any], list[str], list[str]]:
        """采集当前激活触发源。返回 (active_keys, details, reasons, skipped)。"""
        cfg = self._config
        active: list[str] = []
        details: dict[str, Any] = {}
        reasons: list[str] = []
        skipped: list[str] = []

        # ① 综合情绪分<35 且 lu_net_rate_30m<0（30m 字段未落地前以 5m 口径代理）
        key = TRIGGER_SENTIMENT_BREADTH
        if sentiment is None:
            skipped.append(f"{key}:sentiment 未注入")
        else:
            score = getattr(sentiment, "overall_score", None)
            accel = getattr(sentiment, "breadth_acceleration", None)
            rate = getattr(accel, "lu_net_rate_30m", None) if accel is not None else None
            proxy = False
            if rate is None and accel is not None:
                rate = getattr(accel, "lu_net_rate_5m", None)
                proxy = rate is not None  # 30m 未落地→5m 口径代理（detail 标注）
            if score is None or rate is None:
                skipped.append(f"{key}:overall_score/lu_net_rate 缺失")
            else:
                details[key] = {"overall_score": score, "lu_net_rate": rate, "rate_proxy_5m": proxy}
                if score < cfg.sentiment_downgrade_threshold and rate < 0:
                    active.append(key)
                    reasons.append(
                        f"综合情绪分 {score:.1f}<{cfg.sentiment_downgrade_threshold:.0f} 且 "
                        f"lu_net_rate={rate:.2f}<0{'（5m 口径代理 30m）' if proxy else ''} → 降档触发 {key}"
                    )

        # ② distortion_flag（护盘失真）且 spread>2σ（显式入参优先，缺省回退 sentiment.distortion）
        key = TRIGGER_DISTORTION_SPREAD
        dist = distortion if distortion is not None else getattr(sentiment, "distortion", None)
        if dist is None:
            skipped.append(f"{key}:distortion 未注入")
        else:
            flag = bool(getattr(dist, "distortion_flag", False))
            z = getattr(dist, "spread_zscore", None)
            details[key] = {"distortion_flag": flag, "spread_zscore": z}
            if flag and z is not None and z > cfg.distortion_spread_sigma:
                active.append(key)
                reasons.append(
                    f"护盘失真 distortion_flag=True 且 spread_z={z:.2f}>{cfg.distortion_spread_sigma:.1f}σ → 降档触发 {key}"
                )

        # ③ 大幅回撤数≥7（开盘啦口径：追涨资金亏钱效应，44号 §9.4/§9.5）
        key = TRIGGER_DRAWDOWN_COUNT
        dd = getattr(sentiment, "drawdown_risk", None) if sentiment is not None else None
        if dd is None:
            skipped.append(f"{key}:drawdown_risk 未注入")
        else:
            count = getattr(dd, "drawdown_count", None)
            details[key] = {
                "drawdown_count": count,
                "max_drawdown_pct": getattr(dd, "max_drawdown_pct", None),
            }
            if count is not None and count >= cfg.drawdown_count_threshold:
                active.append(key)
                reasons.append(f"大幅回撤数 {count}≥{cfg.drawdown_count_threshold} → 降档触发 {key}")
            elif count is None:
                skipped.append(f"{key}:drawdown_count 缺失")

        # ④ IM 基差贴水 30min 急扩>1.5σ（机构对冲踩踏，44号 §9.8）
        key = TRIGGER_IM_BASIS_DISCOUNT
        if futures_basis is None or bool(getattr(futures_basis, "degraded", False)):
            skipped.append(f"{key}:futures_basis 未注入/降级")
        else:
            sym = (getattr(futures_basis, "per_symbol", None) or {}).get(IM_PRODUCT_KEY)
            vel = getattr(sym, "basis_vel_30m", None) if sym is not None else None
            sigma = getattr(sym, "sigma_20d", None) if sym is not None else None
            if vel is None or sigma is None:
                skipped.append(f"{key}:IM 腿 basis_vel_30m/sigma_20d 缺失")
            else:
                details[key] = {"basis_vel_30m": vel, "sigma_20d": sigma}
                if sigma > 0 and vel < -cfg.im_basis_sigma * sigma:
                    active.append(key)
                    reasons.append(
                        f"IM 基差贴水 30min 急扩 vel={vel:.5f}<-{cfg.im_basis_sigma:.1f}σ({sigma:.5f}) → 降档触发 {key}"
                    )

        # ⑤ 板块 5 状态=CONSENSUS_CLIMAX/DISTRIBUTION_RISK（见顶/派发风险，44号 §9.13）
        key = TRIGGER_SECTOR_TOP_RISK
        sd = sector_divergence
        if sd is None or bool(getattr(sd, "degraded", False)):
            skipped.append(f"{key}:sector_divergence 未注入/降级")
        else:
            state5 = getattr(sd, "rotation_state", None)
            top_flag = bool(getattr(sd, "top_risk_flag", False))
            details[key] = {"rotation_state": state5, "top_risk_flag": top_flag}
            if state5 in TOP_RISK_STATES or top_flag:
                active.append(key)
                reasons.append(f"板块 5 状态={state5}（见顶/派发风险）→ 降档触发 {key}")

        # ⑥ 虹吸态 z>1.5σ 且 电风扇速度计>75 分位（极端分化+无主线混沌共振）
        key = TRIGGER_SIPHON_CHAOS
        if sd is None or bool(getattr(sd, "degraded", False)):
            skipped.append(f"{key}:sector_divergence 未注入/降级")
        else:
            z = getattr(sd, "siphon_z", None)
            vp = getattr(sd, "velocity_percentile", None)
            if z is None or vp is None:
                skipped.append(f"{key}:siphon_z/velocity_percentile 缺失")
            else:
                details[key] = {"siphon_z": z, "velocity_percentile": vp}
                if z > cfg.siphon_z_threshold and vp > cfg.velocity_percentile_threshold:
                    active.append(key)
                    reasons.append(
                        f"虹吸态 z={z:.2f}>{cfg.siphon_z_threshold:.1f}σ 且 速度计分位 {vp:.2f}>"
                        f"{cfg.velocity_percentile_threshold:.2f}（共振）→ 降档触发 {key}"
                    )

        # ⑦ BS-005 外围冲击盘中触发（36号 §3 上游注入）
        key = TRIGGER_BS005_SHOCK
        if bs005_triggered:
            active.append(key)
            details[key] = {"bs005_triggered": True}
            reasons.append(f"BS-005 外围冲击盘中触发 → 降档触发 {key}")
        else:
            details[key] = {"bs005_triggered": False}

        # 升档（全部满足）：综合情绪分>65 且 ŷ_full≥1.1×20日均量 且 rs_ratio>0（进攻族领涨）
        key = TRIGGER_UPGRADE
        score = getattr(sentiment, "overall_score", None) if sentiment is not None else None
        vol_ratio = getattr(volume_forecast, "volume_ratio", None) if volume_forecast is not None else None
        rs = rs_ratio if rs_ratio is not None else getattr(sd, "rs_ratio", None)
        legs = {
            "sentiment_score": score,
            "volume_ratio": vol_ratio,
            "rs_ratio": rs,
        }
        details[key] = legs
        missing = [k for k, v in legs.items() if v is None]
        if missing:
            skipped.append(f"{key}:升档腿缺失 {missing}")
        elif (
            score > cfg.sentiment_upgrade_threshold
            and vol_ratio >= cfg.volume_confirm_ratio
            and rs > 0
        ):
            active.append(key)
            reasons.append(
                f"综合情绪分 {score:.1f}>{cfg.sentiment_upgrade_threshold:.0f} 且 ŷ_full/20日均量="
                f"{vol_ratio:.2f}≥{cfg.volume_confirm_ratio:.1f} 且 rs_ratio={rs:.3f}>0（进攻族领涨）→ 升档触发 {key}"
            )

        return active, details, reasons, skipped

    # ── 档位映射（44号 §9.5）──────────────────────────────────────────────

    def _cap_scale(self, tier: str) -> float:
        cfg = self._config
        if tier == TIER_CONSERVATIVE:
            return cfg.conservative_cap_scale
        if tier == TIER_AGGRESSIVE:
            return cfg.aggressive_cap_scale
        return 1.0

    def _no_add_shift(self, tier: str) -> float:
        return self._config.conservative_no_add_shift_atr if tier == TIER_CONSERVATIVE else 0.0

    # ── 留痕（plan_revision 事件 → prediction_log；写入失败 fail-open）───────

    def _emit_revision_log(self, rev: BoundaryRevision) -> bool:
        try:
            ensure_prediction_log_table(self._log_db_path)
            log_prediction(
                trade_date=rev.trade_date,
                module=MODULE_LOG_NAME,
                prediction_type=PREDICTION_TYPE_PLAN_REVISION,
                payload=rev.to_dict(),
                asof_ts=f"{rev.trade_date}T{rev.eval_time}:00+08:00",
                db_path=self._log_db_path,
            )
            return True
        except Exception as exc:  # noqa: BLE001 — fail-open：留痕失败不阻塞盘中评估
            log.warning("plan_revision 留痕写入失败（fail-open）: %s", exc)
            return False

    # ── 主评估 ────────────────────────────────────────────────────────────

    def evaluate(
        self,
        trade_date: str | datetime.date,
        eval_slot: str,
        *,
        eval_time: str | None = None,
        baseline_tier: str = TIER_NORMAL,
        sentiment: MarketSentimentResult | None = None,
        distortion: DistortionDetectionResult | None = None,
        futures_basis: FuturesBasisSnapshot | None = None,
        sector_divergence: SectorDivergenceResult | None = None,
        volume_forecast: VolumeForecastResult | None = None,
        rs_ratio: float | None = None,
        bs005_triggered: bool = False,
    ) -> BoundaryRevision:
        """盘中边界修正评估（14:00/14:45 两时点；防抖+冷却+档位映射+留痕）。

        Args:
            trade_date: 交易日（ISO 字符串或 date；修正仅当日有效的锚）。
            eval_slot: 评估时点标签（config.eval_slots，默认 14:00/14:45）。
            eval_time: 实际评估时钟 HH:MM（防抖计时口径；None=取 eval_slot）。
            baseline_tier: 当日基线档位（MOD-PLAN-001/盘前产出注入；首评估前生效）。
            sentiment: 市场情绪结果（MOD-SIG-025 波3 输出，含 M1 增量维度）。
            distortion: 护盘/风格失真检测（显式注入优先，缺省回退 sentiment.distortion）。
            futures_basis: 期指基差快照（波4；degraded=跳过该源）。
            sector_divergence: 板块分歧度结果（波4；degraded=跳过⑤⑥源）。
            volume_forecast: 量能盘中预测（ŷ_full/20 日均量腿）。
            rs_ratio: 进攻族-防御族相对强度（缺省回退 sector_divergence.rs_ratio）。
            bs005_triggered: BS-005 外围冲击盘中触发（上游注入）。

        Returns:
            BoundaryRevision：仅当日有效；revision_applied=True 时档位已改并留痕。

        Raises:
            BoundaryRevisionError: trade_date/eval_slot/eval_time/baseline_tier 非法。
        """
        iso = _validate_trade_date(trade_date)
        cfg = self._config
        if eval_slot not in cfg.eval_slots:
            raise BoundaryRevisionError(f"eval_slot 非法（须 ∈ {cfg.eval_slots}）: {eval_slot!r}")
        if baseline_tier not in TIERS:
            raise BoundaryRevisionError(f"baseline_tier 非法（须 ∈ {sorted(TIERS)}）: {baseline_tier!r}")
        slot_time = eval_time if eval_time is not None else eval_slot
        now_min = _parse_hhmm(slot_time)

        state = self._load_state(iso)
        original_tier = state.get("current_tier") or baseline_tier

        active, details, reasons, skipped = self._collect_triggers(
            sentiment, distortion, futures_basis, sector_divergence, volume_forecast, rs_ratio, bs005_triggered
        )

        # ── 防抖：触发须持续 ≥debounce_minutes（跨调用计时，信号中断清零）──
        first_seen: dict[str, int] = state["debounce_first_seen"]
        for t in active:
            first_seen.setdefault(t, now_min)
        for t in list(first_seen):
            if t not in active:
                del first_seen[t]
                reasons.append(f"触发源 {t} 信号中断 → 防抖计时清零")
        confirmed: list[str] = []
        pending: list[str] = []
        proof: dict[str, dict[str, Any]] = {}
        for t in active:
            elapsed = now_min - first_seen[t]
            ok = elapsed >= cfg.debounce_minutes
            proof[t] = {"first_seen": _min_to_hhmm(first_seen[t]), "elapsed_min": elapsed, "confirmed": ok}
            if ok:
                confirmed.append(t)
                reasons.append(f"触发源 {t} 持续 {elapsed}min≥{cfg.debounce_minutes}min → 防抖通过")
            else:
                pending.append(t)
                reasons.append(
                    f"触发源 {t} 首现 {proof[t]['first_seen']}，持续 {elapsed}min<{cfg.debounce_minutes}min → 防抖未生效"
                )

        # ── 冷却+改档判定（升/降档当日各最多 1 次；同窗同时确认→降档优先）──
        down_confirmed = [t for t in confirmed if t != TRIGGER_UPGRADE]
        up_confirmed = TRIGGER_UPGRADE in confirmed
        down_used = int(state.get("downgrades_used", 0))
        up_used = int(state.get("upgrades_used", 0))
        cooldown = {
            "downgrades_used": down_used,
            "upgrades_used": up_used,
            "max_per_direction": cfg.cooldown_per_direction,
        }

        revised_tier = original_tier
        direction = "NONE"
        drivers: list[str] = []
        applied = False
        if down_confirmed:
            drivers = down_confirmed
            if down_used < cfg.cooldown_per_direction and original_tier != TIER_CONSERVATIVE:
                revised_tier = TIER_CONSERVATIVE
                direction = "DOWNGRADE"
                applied = True
            elif down_used >= cfg.cooldown_per_direction:
                reasons.append(f"当日降档已用 {down_used} 次（冷却上限 {cfg.cooldown_per_direction}）→ 拒发")
        elif up_confirmed:
            drivers = [TRIGGER_UPGRADE]
            if up_used < cfg.cooldown_per_direction and original_tier != TIER_AGGRESSIVE:
                revised_tier = TIER_AGGRESSIVE
                direction = "UPGRADE"
                applied = True
            elif up_used >= cfg.cooldown_per_direction:
                reasons.append(f"当日升档已用 {up_used} 次（冷却上限 {cfg.cooldown_per_direction}）→ 拒发")

        if applied:
            state["current_tier"] = revised_tier
            if direction == "DOWNGRADE":
                state["downgrades_used"] = down_used + 1
                cooldown["downgrades_used"] = down_used + 1
                reasons.append(
                    f"降档生效：{original_tier}→{revised_tier}（加仓上限×{cfg.conservative_cap_scale}，"
                    f"禁加仓价位上移 {cfg.conservative_no_add_shift_atr}×ATR({ATR_WINDOW})）"
                )
            else:
                state["upgrades_used"] = up_used + 1
                cooldown["upgrades_used"] = up_used + 1
                reasons.append(
                    f"升档生效：{original_tier}→{revised_tier}（加仓上限×{cfg.aggressive_cap_scale}，"
                    f"封顶 firm 单票 {FIRM_SINGLE_NAME_CAP:.0%} 硬约束由 firm 层执行，30号 §2.2）"
                )
        elif not confirmed:
            reasons.append("无防抖确认触发源 → 不修正")

        # 防抖/冷却状态每次评估必落（防抖计时跨调用累积的前提）
        self._save_state(iso, state)

        rev = BoundaryRevision(
            trade_date=iso,
            eval_slot=eval_slot,
            eval_time=slot_time,
            original_tier=original_tier,
            revised_tier=revised_tier,
            revision_applied=applied,
            direction=direction,
            triggers=drivers,
            pending_triggers=pending,
            debounce_proof=proof,
            cooldown=cooldown,
            position_cap_scale=self._cap_scale(revised_tier),
            no_add_price_shift=self._no_add_shift(revised_tier),
            reasons=reasons,
            trace={"trigger_details": details, "skipped_sources": skipped},
        )
        if applied:
            logged = self._emit_revision_log(rev)
            if not logged:
                rev = replace(
                    rev,
                    logged=False,
                    reasons=[*rev.reasons, "plan_revision 留痕写入失败（fail-open，详见日志）"],
                )
            else:
                rev = replace(rev, logged=True)
        return rev


# ── 主入口 ──


def evaluate_boundary_revision(
    trade_date: str | datetime.date,
    eval_slot: str,
    sentiment: MarketSentimentResult | None = None,
    distortion: DistortionDetectionResult | None = None,
    futures_basis: FuturesBasisSnapshot | None = None,
    sector_divergence: SectorDivergenceResult | None = None,
    volume_forecast: VolumeForecastResult | None = None,
    rs_ratio: float | None = None,
    bs005_triggered: bool = False,
    state_store: JsonStateStore | InMemoryJsonStateStore | None = None,
    config: BoundaryRevisionConfig | None = None,
    *,
    eval_time: str | None = None,
    baseline_tier: str = TIER_NORMAL,
    log_db_path: str | Path | None = None,
) -> BoundaryRevision:
    """盘中边界修正主入口（MOD-PLAN-006，44号 §3 M2 + §9.5）。

    Args:
        trade_date: 交易日（ISO 字符串或 date；修正仅当日有效，次日基线覆盖）。
        eval_slot: 评估时点标签（14:00/14:45，与 MOD-PLAN-003 尾盘窗口对齐）。
        sentiment/distortion/futures_basis/sector_divergence/volume_forecast:
            波3/波4 触发源输出（全 Optional；缺数据=该触发源跳过）。
        rs_ratio: 进攻族-防御族相对强度（None=回退 sector_divergence.rs_ratio）。
        bs005_triggered: BS-005 外围冲击盘中触发（上游注入）。
        state_store: 冷却/防抖状态后端（JsonStateStore 生产持久化 /
            InMemoryJsonStateStore 测试共享；None=当次性内存态，跨调用不累积）。
        config: 参数配置（None=44号 §9.5 设计真源默认值）。
        eval_time: 实际评估时钟 HH:MM（防抖计时口径；None=取 eval_slot）。
        baseline_tier: 当日基线档位（MOD-PLAN-001/盘前产出注入，默认 NORMAL）。
        log_db_path: prediction_log 库路径（None=DB_PATH SSoT；测试注入临时库）。

    Returns:
        BoundaryRevision：纯 frozen dataclass，JSON 可序列化，仅当日有效。
    """
    return BoundaryRevisionEngine(state_store=state_store, config=config, log_db_path=log_db_path).evaluate(
        trade_date,
        eval_slot,
        eval_time=eval_time,
        baseline_tier=baseline_tier,
        sentiment=sentiment,
        distortion=distortion,
        futures_basis=futures_basis,
        sector_divergence=sector_divergence,
        volume_forecast=volume_forecast,
        rs_ratio=rs_ratio,
        bs005_triggered=bs005_triggered,
    )
