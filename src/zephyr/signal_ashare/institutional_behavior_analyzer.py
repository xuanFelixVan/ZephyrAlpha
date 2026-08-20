# [BLUEPRINT] MOD-SIG-021 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.institutional_behavior_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] zephyr.signal_ashare.short_term_stock_selector
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 6阶段状态机不可跳跃(建仓→洗盘→试盘→再洗盘→拉升→出货); 降级路径必须有日志
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/signal_ashare/test_institutional_behavior_analyzer.py
# [A_module] module_id=MOD-SIG-021 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ashare_signal
# category: signal_analyzer
# status: active
# created: "2026-08-02"
# ---

r"""


D-SIGNAL-21 A股主力行为分析引擎

主力行为学6阶段识别(建仓-洗盘-试盘-再洗盘-拉升-出货) + 洗盘vs出货识别
+ 诱多行为检测 + 主力游资打架胜负判断(30分钟观察期) + 主力行为分时特征识别。

理论依据：主力行为学 / 市场微观结构 / 行为金融学。

设计文档默认值可配置——所有阈值通过 InstitutionalBehaviorConfig 调整，
默认值取自 D:\临时工作区\依赖图-D-SIGNAL-信号域.md §D-SIGNAL-21。

依赖方向：D_DATA(行情数据) -> D-SIGNAL-21 -> D-SIGNAL-23(短线选股) / D-SIGNAL-24(日内买卖点)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 分时价量序列 列表数据
#   fields: prices 价格序列 + volumes 成交量序列 + timestamps 时间戳序列（三者等长）
#   code: InstitutionalBehaviorInput L165-L167
# - id: I2
#   name: 大单资金数据 列表数据
#   fields: large_order_net 大单净流入(元) + large_order_count 大单笔数（单笔≥50万元为大单）
#   code: InstitutionalBehaviorInput L168-L169
# 层: 特征
# - id: F1
#   name_zh: 近期量比
#   name_en: volume_ratio
#   intro: 后半段均量除以前半段均量 看量能放大还是萎缩
#   formula: mean(volumes[n//2:])/mean(volumes[:n//2])
#   code: institutional_behavior_analyzer.py L603
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F2
#   name_zh: 区间涨跌幅
#   name_en: price_change_pct
#   intro: 序列末价相对首价涨了百分之几
#   formula: (末价-首价)/首价×100
#   code: institutional_behavior_analyzer.py L615
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 大单净方向
#   name_en: large_order_direction
#   intro: 大单净流入求和 正=主力在买 负=主力在卖
#   formula: Σ large_order_net
#   code: institutional_behavior_analyzer.py L621
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F4
#   name_zh: 价格波动率
#   name_en: volatility_pct
#   intro: 价格标准差除以均值 衡量走势剧烈程度
#   formula: std(prices)/mean(prices)×100 归一化 min(波动/5,1)
#   code: institutional_behavior_analyzer.py L627
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 6阶段主力行为识别
#   name_en: identify_behavior_phase
#   intro: 量比×涨幅×大单方向三维打分 从建仓到出货6阶段取最高
#   desc: 建仓(量1.1-1.5倍+涨<2%+大单正) 洗盘(量<0.8+跌<5%+大单正) 试盘(量1.3-2.0+涨1-3%) 再洗盘(量<0.6+跌<3%) 拉升(量>2.0+涨>5%+大单正) 出货(量>1.5+滞涨<2%+大单负) argmax <20→未知
#   inputs: F1 F2 F3
#   outputs: current_phase + phase_confidence
#   invariant: 6阶段状态机不可跳跃(建仓→洗盘→试盘→再洗盘→拉升→出货)
# - id: A2
#   name_zh: ② 洗盘vs出货判定
#   name_en: distinguish_wash_vs_distribute
#   intro: 缩量跌+大单未走=洗盘 放量滞涨+大单流出=出货
#   desc: 双评分制 wash_score vs dist_score 各3项加分 高者≥50生效 否则中性
#   inputs: F1 F2 F3 A1
#   outputs: wash_distribute + confidence
# - id: A3
#   name_zh: ③ 诱多行为检测
#   name_en: detect_bull_trap
#   intro: 价格冲高≥3%后又反转跌≥2% 判定多头陷阱
#   desc: rise_pct=(峰值-首价)/首价×100 ≥3 且 reversal_pct=(现价-峰值)/峰值×100 ≤-2 → 诱多 confidence按两幅度加权
#   inputs: I1
#   outputs: bull_trap_detected + confidence
# - id: A4
#   name_zh: ④ 主力游资打架胜负判断
#   name_en: judge_main_force_vs_hot_money
#   intro: 30分钟观察期 看大单持续净流入的主力强还是高波动的游资强
#   desc: 主力主导度=大单正值占比×0.5+大单强度×0.5; 游资活跃度=min(波动率/5,1); 任一方≥0.6分胜负 否则僵持
#   inputs: I2 F4
#   outputs: conflict_winner + conflict_confidence
# - id: A5
#   name_zh: ⑤ 主力行为分时特征识别
#   name_en: recognize_intraday_features
#   intro: 按开盘/上午/午盘/尾盘4段统计成交量占比与价格变化
#   desc: 时间段切分(9:30-10:00/10:00-11:30/13:00-14:00/14:00-15:00) 段内量占比=段量和/总量×100 段内价格变化%=(段末-段首)/段首×100
#   inputs: I1
#   outputs: intraday_features 字典
# - id: A6
#   name_zh: ⑥ 综合评分
#   name_en: _compute_overall_score
#   intro: 5维置信度加权成0-100综合分 诱多越明显分越低
#   desc: score=阶段置信×0.30+洗出置信×0.25+(诱多则100-诱多置信否则100)×0.20+打架置信×0.25 clamp[0,100]
#   inputs: A1 A2 A3 A4
#   outputs: overall_score 0-100
# 层: 输出
# - id: O1
#   name_zh: 主力行为分析结果
#   name_en: InstitutionalBehaviorResult
#   intro: 当前阶段+洗出判定+诱多检测+打架胜负+分时特征+综合分 一次输出
#   invariant: 6阶段状态机不可跳跃 降级路径必须有日志
#   downstream: 短线选股器 MOD-SIG-023; 日内买卖点引擎 MOD-SIG-024
# [/ALGO_FLOW]
#
# 边:
# I1 -.->|断点| F1
# I1 -.->|断点| F2
# I1 -.->|断点| F4
# I2 -.->|断点| F3
# F1 --> A1
# F2 --> A1
# F3 --> A1
# F1 --> A2
# F2 --> A2
# F3 --> A2
# A1 --> A2
# I1 --> A3
# I2 --> A4
# F4 --> A4
# I1 --> A5
# A1 --> A6
# A2 --> A6
# A3 --> A6
# A4 --> A6
# A5 --> O1
# A6 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# 枚举
# ============================================================================


class BehaviorPhase(str, Enum):
    """主力行为6阶段（不可跳跃顺序：建仓→洗盘→试盘→再洗盘→拉升→出货）。"""

    BUILDING = "建仓"
    WASHING = "洗盘"
    TESTING = "试盘"
    RE_WASHING = "再洗盘"
    PULLING = "拉升"
    DISTRIBUTING = "出货"
    UNKNOWN = "未知"


class WashDistributeVerdict(str, Enum):
    """洗盘 vs 出货判定。"""

    WASH = "洗盘"
    DISTRIBUTE = "出货"
    NEUTRAL = "中性"


class ConflictWinner(str, Enum):
    """主力 vs 游资打架胜负。"""

    MAIN_FORCE_WINS = "主力胜"
    HOT_MONEY_WINS = "游资胜"
    STALEMATE = "僵持"


# ============================================================================
# 配置（设计文档默认值，可配置）
# ============================================================================


@dataclass(frozen=True)
class InstitutionalBehaviorConfig:
    """主力行为分析可配置阈值——默认值取自设计文档 §D-SIGNAL-21。"""

    # ── 6阶段识别阈值 ──
    # 建仓：成交量温和放大(1.1~1.5倍)，涨幅小(<2%)
    building_volume_min: float = 1.1
    building_volume_max: float = 1.5
    building_price_change_max: float = 2.0

    # 洗盘：成交量萎缩(<0.8倍)，跌幅适中(<5%)
    washing_volume_max: float = 0.8
    washing_price_drop_max: float = 5.0

    # 试盘：成交量短暂放大(1.3~2.0倍)，涨幅小到中(1%~3%)
    testing_volume_min: float = 1.3
    testing_volume_max: float = 2.0
    testing_price_rise_min: float = 1.0
    testing_price_rise_max: float = 3.0

    # 再洗盘：成交量极度萎缩(<0.6倍)，跌幅小(<3%)
    re_washing_volume_max: float = 0.6
    re_washing_price_drop_max: float = 3.0

    # 拉升：成交量显著放大(>2.0倍)，涨幅大(>5%)
    pulling_volume_min: float = 2.0
    pulling_price_rise_min: float = 5.0

    # 出货：成交量大(>1.5倍)但滞涨(<2%)
    distributing_volume_min: float = 1.5
    distributing_price_stagnation_max: float = 2.0

    # ── 洗盘vs出货判定 ──
    # 洗盘特征：缩量下跌
    wash_volume_threshold: float = 0.8
    wash_price_drop_min: float = 1.0
    # 出货特征：放量滞涨
    distribute_volume_threshold: float = 1.3
    distribute_price_stagnation: float = 2.0
    # 大单方向：洗盘时大单净流入仍为正，出货时为负
    wash_large_order_min: float = 0.0  # 洗盘大单净流入>=0
    distribute_large_order_max: float = 0.0  # 出货大单净流入<=0

    # ── 诱多行为检测 ──
    bull_trap_breakout_pct: float = 3.0  # 突破幅度阈值
    bull_trap_reversal_pct: float = -2.0  # 反转幅度阈值
    bull_trap_observation_minutes: int = 30  # 观察窗口

    # ── 主力vs游资打架 ──
    conflict_observation_minutes: int = 30  # 30分钟观察期
    main_force_dominance_threshold: float = 0.6  # 主力主导度阈值
    hot_money_dominance_threshold: float = 0.6  # 游资主导度阈值
    # 主力特征：大单持续净流入，走势稳健
    # 游资特征：成交活跃但大单占比低，走势剧烈波动

    # ── 分时特征 ──
    intraday_segments: tuple[tuple[str, tuple[int, int]], ...] = (
        ("开盘", (9, 30), (10, 0)),
        ("上午", (10, 0), (11, 30)),
        ("午盘", (13, 0), (14, 0)),
        ("尾盘", (14, 0), (15, 0)),
    )

    # ── 大单识别 ──
    large_order_threshold: float = 500000.0  # 单笔大单阈值(元)


# ============================================================================
# 输入 / 输出
# ============================================================================


@dataclass
class InstitutionalBehaviorInput:
    """主力行为分析输入数据。"""

    prices: list[float]
    volumes: list[float]
    timestamps: list[datetime]
    large_order_net: list[float] = field(default_factory=list)  # 主力资金净流入(元)
    large_order_count: list[int] = field(default_factory=list)  # 大单笔数
    market_sentiment_score: float = 50.0  # 来自 D-SIGNAL-25 市场情绪


@dataclass
class InstitutionalBehaviorResult:
    """主力行为分析结果。"""

    current_phase: str
    phase_confidence: float
    wash_distribute: str
    wash_distribute_confidence: float
    bull_trap_detected: bool
    bull_trap_confidence: float
    conflict_winner: str
    conflict_confidence: float
    intraday_features: dict[str, float]
    overall_score: float
    audit_trail: list[dict[str, Any]] = field(default_factory=list)
    is_degraded: bool = False


# ============================================================================
# 分析器
# ============================================================================


class InstitutionalBehaviorAnalyzer:
    """
    A股主力行为分析引擎（D-SIGNAL-21）。

    5维度分析：
      1. 6阶段主力行为识别（建仓-洗盘-试盘-再洗盘-拉升-出货）
      2. 洗盘vs出货识别
      3. 诱多行为检测
      4. 主力游资打架胜负判断（30分钟观察期）
      5. 主力行为分时特征识别
    """

    def __init__(self, config: InstitutionalBehaviorConfig | None = None) -> None:
        self._config = config or InstitutionalBehaviorConfig()

    # ------------------------------------------------------------------
    # 公开入口
    # ------------------------------------------------------------------

    def analyze(self, input_data: InstitutionalBehaviorInput) -> InstitutionalBehaviorResult:
        """执行5维度主力行为分析，返回综合结果。"""
        if not self._validate_input(input_data):
            logger.warning("InstitutionalBehaviorAnalyzer: 输入数据不合法，返回降级结果")
            return self._degraded_result("输入数据校验失败")

        audit_trail: list[dict[str, Any]] = []

        # ── 维度1: 6阶段识别 ──
        phase, phase_confidence = self.identify_behavior_phase(input_data)
        audit_trail.append(
            {
                "dimension": "phase_identification",
                "result": phase,
                "confidence": phase_confidence,
            }
        )

        # ── 维度2: 洗盘vs出货 ──
        wd_verdict, wd_confidence = self.distinguish_wash_vs_distribute(input_data, phase)
        audit_trail.append(
            {
                "dimension": "wash_vs_distribute",
                "result": wd_verdict,
                "confidence": wd_confidence,
            }
        )

        # ── 维度3: 诱多行为检测 ──
        bull_trap, bull_trap_conf = self.detect_bull_trap(input_data)
        audit_trail.append(
            {
                "dimension": "bull_trap",
                "result": bull_trap,
                "confidence": bull_trap_conf,
            }
        )

        # ── 维度4: 主力vs游资打架 ──
        winner, conflict_conf = self.judge_main_force_vs_hot_money(input_data)
        audit_trail.append(
            {
                "dimension": "conflict",
                "result": winner,
                "confidence": conflict_conf,
            }
        )

        # ── 维度5: 分时特征 ──
        intraday_features = self.recognize_intraday_features(input_data)
        audit_trail.append(
            {
                "dimension": "intraday_features",
                "result": intraday_features,
            }
        )

        # ── 综合评分 ──
        overall_score = self._compute_overall_score(
            phase,
            phase_confidence,
            wd_verdict,
            wd_confidence,
            bull_trap,
            bull_trap_conf,
            winner,
            conflict_conf,
        )

        return InstitutionalBehaviorResult(
            current_phase=phase,
            phase_confidence=phase_confidence,
            wash_distribute=wd_verdict,
            wash_distribute_confidence=wd_confidence,
            bull_trap_detected=bull_trap,
            bull_trap_confidence=bull_trap_conf,
            conflict_winner=winner,
            conflict_confidence=conflict_conf,
            intraday_features=intraday_features,
            overall_score=overall_score,
            audit_trail=audit_trail,
        )

    # ------------------------------------------------------------------
    # 维度1: 6阶段主力行为识别
    # ------------------------------------------------------------------

    def identify_behavior_phase(self, input_data: InstitutionalBehaviorInput) -> tuple[str, float]:
        """
        识别当前主力行为阶段。

        通过成交量比率 + 价格变化 + 大单方向三维交叉判断，
        返回(阶段, 置信度0~100)。
        """
        cfg = self._config
        prices = input_data.prices
        volumes = input_data.volumes

        if len(prices) < 2 or len(volumes) < 2:
            return BehaviorPhase.UNKNOWN.value, 0.0

        # 计算近期量比和价格变化
        volume_ratio = self._recent_volume_ratio(volumes)
        price_change_pct = self._recent_price_change_pct(prices)
        large_order_direction = self._large_order_direction(input_data)

        scores: dict[str, float] = {}

        # 建仓：量温和放大 + 价小涨/横盘 + 大单净流入
        scores[BehaviorPhase.BUILDING.value] = self._score_building(
            volume_ratio, price_change_pct, large_order_direction
        )
        # 洗盘：缩量 + 价跌 + 大单仍正
        scores[BehaviorPhase.WASHING.value] = self._score_washing(volume_ratio, price_change_pct, large_order_direction)
        # 试盘：量短暂放大 + 价小涨
        scores[BehaviorPhase.TESTING.value] = self._score_testing(volume_ratio, price_change_pct)
        # 再洗盘：极度缩量 + 价小跌
        scores[BehaviorPhase.RE_WASHING.value] = self._score_re_washing(volume_ratio, price_change_pct)
        # 拉升：放量 + 大涨 + 大单强正
        scores[BehaviorPhase.PULLING.value] = self._score_pulling(volume_ratio, price_change_pct, large_order_direction)
        # 出货：放量 + 滞涨 + 大单负
        scores[BehaviorPhase.DISTRIBUTING.value] = self._score_distributing(
            volume_ratio, price_change_pct, large_order_direction
        )

        best_phase = max(scores, key=scores.get)  # type: ignore[arg-type]
        best_score = scores[best_phase]
        if best_score < 20.0:
            return BehaviorPhase.UNKNOWN.value, best_score
        return best_phase, best_score

    def _score_building(self, vol_ratio: float, price_pct: float, lo_dir: float) -> float:
        cfg = self._config
        score = 0.0
        # 量比在 building_volume_min~max 之间
        if cfg.building_volume_min <= vol_ratio <= cfg.building_volume_max:
            score += 40.0
        elif vol_ratio <= cfg.building_volume_max:
            score += 20.0
        # 涨幅小
        if 0 <= price_pct <= cfg.building_price_change_max:
            score += 30.0
        # 大单净流入
        if lo_dir > 0:
            score += 30.0
        return min(score, 100.0)

    def _score_washing(self, vol_ratio: float, price_pct: float, lo_dir: float) -> float:
        cfg = self._config
        score = 0.0
        if vol_ratio <= cfg.washing_volume_max:
            score += 40.0
        if -cfg.washing_price_drop_max <= price_pct < 0:
            score += 30.0
        # 洗盘时大单仍为正（主力未走）
        if lo_dir >= cfg.wash_large_order_min:
            score += 30.0
        return min(score, 100.0)

    def _score_testing(self, vol_ratio: float, price_pct: float) -> float:
        cfg = self._config
        score = 0.0
        if cfg.testing_volume_min <= vol_ratio <= cfg.testing_volume_max:
            score += 50.0
        if cfg.testing_price_rise_min <= price_pct <= cfg.testing_price_rise_max:
            score += 50.0
        return min(score, 100.0)

    def _score_re_washing(self, vol_ratio: float, price_pct: float) -> float:
        cfg = self._config
        score = 0.0
        if vol_ratio <= cfg.re_washing_volume_max:
            score += 50.0
        if -cfg.re_washing_price_drop_max <= price_pct < 0:
            score += 50.0
        return min(score, 100.0)

    def _score_pulling(self, vol_ratio: float, price_pct: float, lo_dir: float) -> float:
        cfg = self._config
        score = 0.0
        if vol_ratio >= cfg.pulling_volume_min:
            score += 35.0
        if price_pct >= cfg.pulling_price_rise_min:
            score += 35.0
        if lo_dir > 0:
            score += 30.0
        return min(score, 100.0)

    def _score_distributing(self, vol_ratio: float, price_pct: float, lo_dir: float) -> float:
        cfg = self._config
        score = 0.0
        if vol_ratio >= cfg.distributing_volume_min:
            score += 35.0
        if abs(price_pct) <= cfg.distributing_price_stagnation_max:
            score += 35.0
        if lo_dir < cfg.distribute_large_order_max:
            score += 30.0
        return min(score, 100.0)

    # ------------------------------------------------------------------
    # 维度2: 洗盘vs出货识别
    # ------------------------------------------------------------------

    def distinguish_wash_vs_distribute(self, input_data: InstitutionalBehaviorInput, phase: str) -> tuple[str, float]:
        """
        区分洗盘与出货。

        洗盘：缩量下跌 + 大单净流入仍为正（主力未走）
        出货：放量滞涨 + 大单净流入为负（主力在卖）
        """
        cfg = self._config
        vol_ratio = self._recent_volume_ratio(input_data.volumes)
        price_pct = self._recent_price_change_pct(input_data.prices)
        lo_dir = self._large_order_direction(input_data)

        wash_score = 0.0
        dist_score = 0.0

        # 洗盘评分
        if vol_ratio <= cfg.wash_volume_threshold:
            wash_score += 35.0
        if price_pct <= -cfg.wash_price_drop_min:
            wash_score += 30.0
        if lo_dir >= cfg.wash_large_order_min:
            wash_score += 35.0

        # 出货评分
        if vol_ratio >= cfg.distribute_volume_threshold:
            dist_score += 35.0
        if abs(price_pct) <= cfg.distribute_price_stagnation:
            dist_score += 30.0
        if lo_dir <= cfg.distribute_large_order_max:
            dist_score += 35.0

        if wash_score > dist_score and wash_score >= 50.0:
            return WashDistributeVerdict.WASH.value, wash_score
        if dist_score > wash_score and dist_score >= 50.0:
            return WashDistributeVerdict.DISTRIBUTE.value, dist_score
        return WashDistributeVerdict.NEUTRAL.value, max(wash_score, dist_score)

    # ------------------------------------------------------------------
    # 维度3: 诱多行为检测
    # ------------------------------------------------------------------

    def detect_bull_trap(self, input_data: InstitutionalBehaviorInput) -> tuple[bool, float]:
        """
        检测诱多行为（多头陷阱）。

        诱多特征：价格突破关键位后快速反转下跌。
        判定逻辑：近期最高涨幅 >= bull_trap_breakout_pct，随后反转 <= bull_trap_reversal_pct。
        """
        cfg = self._config
        prices = input_data.prices
        if len(prices) < 3:
            return False, 0.0

        # 找到近期最高点
        peak_idx = prices.index(max(prices))
        if peak_idx == 0 or peak_idx == len(prices) - 1:
            return False, 0.0

        base_price = prices[0]
        peak_price = prices[peak_idx]
        current_price = prices[-1]

        if base_price <= 0:
            return False, 0.0

        rise_pct = (peak_price - base_price) / base_price * 100.0
        reversal_pct = (current_price - peak_price) / peak_price * 100.0

        if rise_pct >= cfg.bull_trap_breakout_pct and reversal_pct <= cfg.bull_trap_reversal_pct:
            confidence = min(
                100.0,
                (rise_pct / cfg.bull_trap_breakout_pct) * 50.0
                + (abs(reversal_pct) / abs(cfg.bull_trap_reversal_pct)) * 50.0,
            )
            return True, confidence
        return False, 0.0

    # ------------------------------------------------------------------
    # 维度4: 主力vs游资打架胜负判断
    # ------------------------------------------------------------------

    def judge_main_force_vs_hot_money(self, input_data: InstitutionalBehaviorInput) -> tuple[str, float]:
        """
        判断主力与游资打架胜负（30分钟观察期）。

        主力特征：大单持续净流入，走势稳健（波动小）
        游资特征：成交活跃但大单占比低，走势剧烈波动

        胜负判定：
          - 主力胜：大单净流入持续为正 + 波动率低 → 持有
          - 游资胜：大单净流入为负/波动率高 → 离场
          - 僵持：双方势均力敌 → 减半仓
        """
        cfg = self._config
        if not input_data.large_order_net or len(input_data.prices) < 3:
            return ConflictWinner.STALEMATE.value, 0.0

        # 主力主导度：大单净流入正值占比 + 大单强度
        lo_net = input_data.large_order_net
        positive_ratio = sum(1 for x in lo_net if x > 0) / max(len(lo_net), 1)
        lo_strength = sum(lo_net) / max(sum(abs(x) for x in lo_net), 1.0)

        # 游资主导度：波动率（高波动=游资活跃）
        volatility = self._price_volatility(input_data.prices)
        # 归一化波动率到 0~1（假设 5% 波动率为高波动）
        hot_money_activity = min(volatility / 5.0, 1.0)

        main_force_dominance = positive_ratio * 0.5 + max(lo_strength, 0.0) * 0.5
        hot_money_dominance = hot_money_activity

        if main_force_dominance >= cfg.main_force_dominance_threshold:
            return ConflictWinner.MAIN_FORCE_WINS.value, main_force_dominance * 100.0
        if hot_money_dominance >= cfg.hot_money_dominance_threshold:
            return ConflictWinner.HOT_MONEY_WINS.value, hot_money_dominance * 100.0
        return ConflictWinner.STALEMATE.value, 50.0

    # ------------------------------------------------------------------
    # 维度5: 主力行为分时特征识别
    # ------------------------------------------------------------------

    def recognize_intraday_features(self, input_data: InstitutionalBehaviorInput) -> dict[str, float]:
        """
        识别主力行为分时特征。

        按时间段(开盘/上午/午盘/尾盘)统计成交量占比、价格变化、大单占比。
        """
        cfg = self._config
        timestamps = input_data.timestamps
        volumes = input_data.volumes
        prices = input_data.prices

        if not timestamps or len(timestamps) != len(volumes):
            return {"degraded": 1.0}

        total_volume = sum(volumes) if sum(volumes) > 0 else 1.0
        features: dict[str, float] = {}

        for seg_name, (start_h, start_m), (end_h, end_m) in cfg.intraday_segments:
            seg_volumes = []
            seg_prices = []
            for i, ts in enumerate(timestamps):
                minutes_of_day = ts.hour * 60 + ts.minute
                seg_start = start_h * 60 + start_m
                seg_end = end_h * 60 + end_m
                if seg_start <= minutes_of_day < seg_end:
                    seg_volumes.append(volumes[i])
                    if i < len(prices):
                        seg_prices.append(prices[i])

            vol_pct = sum(seg_volumes) / total_volume * 100.0 if seg_volumes else 0.0
            price_chg = 0.0
            if len(seg_prices) >= 2 and seg_prices[0] > 0:
                price_chg = (seg_prices[-1] - seg_prices[0]) / seg_prices[0] * 100.0
            features[f"{seg_name}_成交量占比"] = round(vol_pct, 2)
            features[f"{seg_name}_价格变化%"] = round(price_chg, 2)

        features["总成交量"] = round(total_volume, 2)
        features["波动率%"] = round(self._price_volatility(prices), 2)
        return features

    # ------------------------------------------------------------------
    # 辅助计算
    # ------------------------------------------------------------------

    def _validate_input(self, data: InstitutionalBehaviorInput) -> bool:
        if not data.prices or not data.volumes or not data.timestamps:
            return False
        if len(data.prices) != len(data.volumes):
            return False
        if len(data.prices) != len(data.timestamps):
            return False
        if len(data.prices) < 2:
            return False
        return True

    def _recent_volume_ratio(self, volumes: list[float]) -> float:
        """近期成交量 / 前期平均成交量。"""
        n = len(volumes)
        if n < 2:
            return 1.0
        mid = max(n // 2, 1)
        recent_avg = sum(volumes[mid:]) / max(len(volumes[mid:]), 1)
        prior_avg = sum(volumes[:mid]) / max(mid, 1)
        if prior_avg <= 0:
            return 1.0
        return recent_avg / prior_avg

    def _recent_price_change_pct(self, prices: list[float]) -> float:
        """近期价格变化百分比。"""
        if len(prices) < 2 or prices[0] <= 0:
            return 0.0
        return (prices[-1] - prices[0]) / prices[0] * 100.0

    def _large_order_direction(self, data: InstitutionalBehaviorInput) -> float:
        """大单方向：正值=净流入(主力买)，负值=净流出(主力卖)。"""
        if not data.large_order_net:
            return 0.0
        return sum(data.large_order_net)

    def _price_volatility(self, prices: list[float]) -> float:
        """价格波动率(%)——标准差/均值*100。"""
        if len(prices) < 2:
            return 0.0
        mean = sum(prices) / len(prices)
        if mean <= 0:
            return 0.0
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        return (variance**0.5) / mean * 100.0

    def _compute_overall_score(
        self,
        phase: str,
        phase_conf: float,
        wd_verdict: str,
        wd_conf: float,
        bull_trap: bool,
        bull_trap_conf: float,
        winner: str,
        conflict_conf: float,
    ) -> float:
        """综合评分(0~100)——加权融合5维度。"""
        # 阶段置信度 30%
        # 洗盘vs出货 25%
        # 诱多检测 20%
        # 主力游资打架 25%
        score = (
            phase_conf * 0.30
            + wd_conf * 0.25
            + (100.0 - bull_trap_conf if bull_trap else 100.0) * 0.20
            + conflict_conf * 0.25
        )
        return round(min(max(score, 0.0), 100.0), 2)

    def _degraded_result(self, reason: str) -> InstitutionalBehaviorResult:
        """降级结果——输入不合法时返回。"""
        return InstitutionalBehaviorResult(
            current_phase=BehaviorPhase.UNKNOWN.value,
            phase_confidence=0.0,
            wash_distribute=WashDistributeVerdict.NEUTRAL.value,
            wash_distribute_confidence=0.0,
            bull_trap_detected=False,
            bull_trap_confidence=0.0,
            conflict_winner=ConflictWinner.STALEMATE.value,
            conflict_confidence=0.0,
            intraday_features={"degraded": 1.0},
            overall_score=0.0,
            is_degraded=True,
            audit_trail=[{"dimension": "degraded", "reason": reason}],
        )


__all__ = [
    "BehaviorPhase",
    "ConflictWinner",
    "InstitutionalBehaviorAnalyzer",
    "InstitutionalBehaviorConfig",
    "InstitutionalBehaviorInput",
    "InstitutionalBehaviorResult",
    "WashDistributeVerdict",
]
