# [BLUEPRINT] MOD-SIG-033 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.youzi_relay_emotion_engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] zephyr.signal_ashare.dual_engine_fusion_decision_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 6因子评分满分100; 情绪周期4+1阶段不可跳跃(冰点→反核→主升→疯狂→退潮); 降级路径必须有日志
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/signal_ashare/test_youzi_relay_emotion_engine.py
# [A_module] module_id=MOD-SIG-033 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ashare_signal
# category: signal_analyzer
# status: active
# created: "2026-08-02"
# ---

r"""


D-SIGNAL-33 A股游资接力情绪引擎

游资接力情绪6因子0-100分评分(连板高度25分+封单质量20分+涨停时间15分
+开板次数15分+竞价强度10分+助攻梯队10分) + 情绪周期4+1阶段定位
(冰点/反核/主升/疯狂/退潮) + 各阶段策略映射。

理论依据：行为金融学 / 情绪周期 / 市场微观结构。

设计文档默认值可配置——所有阈值通过 YouziEmotionConfig 调整，
默认值取自 D:\临时工作区\依赖图-D-SIGNAL-信号域.md §D-SIGNAL-33。

依赖方向：D_DATA(行情数据) -> D-SIGNAL-33 -> D-SIGNAL-35(双引擎融合决策)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 连板与封单 行情数据
#   fields: consecutive_limit_ups 连板数 + seal_amount 封单金额 + float_market_cap 流通市值
#   code: YouziEmotionInput L146-152
# - id: I2
#   name: 封板时间与开板 数据
#   fields: seal_time 封板时间 + open_board_count 盘中开板次数
#   code: YouziEmotionInput L154-157
# - id: I3
#   name: 竞价与板块 数据
#   fields: auction_rise_pct 竞价涨幅 + auction_volume_ratio 竞价量比 + sector_limit_up_count 同板块涨停家数
#   code: YouziEmotionInput L160-164
# - id: I4
#   name: 市场环境 数据
#   fields: market_limit_up_count 全市场涨停家数 + market_breadth_ratio 涨跌家数比
#   code: YouziEmotionInput L167-168
# 层: 特征
# - id: F1
#   name_zh: 连板高度评分
#   name_en: score_consecutive_height
#   intro: 连板越多游资接力情绪越强，满分25
#   formula: score=min(1+(连板数-1)×5, 25)，无连板=0
#   code: youzi_relay_emotion_engine.py L277-291
#   registry: factor_registry: 有FCT条目 FCT-SENT-002（分量：连板高度——情绪三件套之一，节点为分量计算步骤，§4.16.4 分量引用）
#   is_break: false
# - id: F2
#   name_zh: 封单质量评分
#   name_en: score_seal_quality
#   intro: 封流比衡量封板强度，满分20
#   formula: 封流比=封单金额/流通市值 → ≥10%→20分，≥5%→15分，≥2%→10分，否则 封流比/2%×10
#   code: youzi_relay_emotion_engine.py L297-318
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F3
#   name_zh: 涨停时间评分
#   name_en: score_seal_time
#   intro: 越早封板情绪越强，满分15
#   formula: ≤9:25→15分(一字板)，≤10:00→12，≤11:00→8，≤13:30→5，≤14:30→3，之后→1
#   code: youzi_relay_emotion_engine.py L324-352
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F4
#   name_zh: 开板次数评分
#   name_en: score_open_board
#   intro: 开板越少封板越稳，满分15
#   formula: 0次→15分，1次→8分，2次→3分，≥3次→0分
#   code: youzi_relay_emotion_engine.py L358-374
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F5
#   name_zh: 竞价强度评分
#   name_en: score_auction_strength
#   intro: 竞价高开加量比放大说明抢筹，满分10
#   formula: 涨幅分(≥5%→7,≥3%→5,≥1%→3,否则按比例) + 量比分(≥2→3,否则 量比/2×3)，min(和,10)
#   code: youzi_relay_emotion_engine.py L380-402
#   registry: factor_registry: 无FCT条目
#   is_break: true
# - id: F6
#   name_zh: 助攻梯队评分
#   name_en: score_assist_echelon
#   intro: 同板块涨停家数越多梯队越完整，满分10
#   formula: ≥5家→10分，≥3家→7分，≥1家→4分，否则0分
#   code: youzi_relay_emotion_engine.py L408-424
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 6因子评分求和
#   name_en: YouziRelayEmotionEngine.analyze（评分段）
#   intro: 6个因子得分加总封顶100，得综合情绪评分
#   desc: total=min(Σ6因子score, 100)，逐因子记 audit_trail（L227-254）
#   inputs: F1 F2 F3 F4 F5 F6
#   outputs: total_score 综合情绪评分 0-100
#   invariant: 6因子评分满分100
# - id: A2
#   name_zh: ② 情绪周期4+1阶段定位
#   name_en: determine_emotion_phase
#   intro: 按评分分段定情绪阶段，再用市场广度/断板检测退潮
#   desc: ≤20冰点/≤40反核/≤65主升/≤85疯狂；>85且广度<0.4 或 ≥4连板且≥3次开板→退潮；全市涨停≤5家且分≤40→冰点；置信度=距阶段中心越近越高 max(100-distance×30,50)（L430-479）
#   inputs: A1 I1 I2 I4
#   outputs: emotion_phase + phase_confidence
#   invariant: 4+1阶段顺序不可跳跃（冰点→反核→主升→疯狂→退潮）
# - id: A3
#   name_zh: ③ 阶段策略映射
#   name_en: map_strategy
#   intro: 每个情绪阶段对应一条操作建议
#   desc: 冰点→空仓/埋伏，反核→小仓试错，主升→核心仓做龙头，疯狂→只做龙头，退潮→空仓等冰点，未知→中性观望（L485-495）
#   inputs: A2
#   outputs: strategy_action 策略建议
# - id: A4
#   name_zh: ④ 输入校验与降级路径
#   name_en: _validate_input / _degraded_result
#   intro: 输入出现负值就返回全零降级结果并记日志
#   desc: 连板/开板/市值/封单金额任一<0 → is_degraded=True 的降级结果 + warning 日志（L501-524）
#   inputs: I1 I2
#   outputs: 降级 YouziEmotionResult
#   invariant: 降级路径必须有日志
# 层: 输出
# - id: O1
#   name_zh: 游资接力情绪分析结果
#   name_en: YouziEmotionResult
#   intro: 综合评分+6因子明细+情绪阶段+置信度+策略建议+审计轨迹
#   invariant: total_score ∈ 0-100
#   downstream: zephyr.signal_ashare.dual_engine_fusion_decision_engine（D-SIGNAL-35 双引擎融合决策，# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> F1
# I1 -.->|断点| F2
# I2 -.->|断点| F3
# I2 -.->|断点| F4
# I3 -.->|断点| F5
# I3 -.->|断点| F6
# F1 --> A1
# F2 --> A1
# F3 --> A1
# F4 --> A1
# F5 --> A1
# F6 --> A1
# I1 --> A2
# I2 --> A2
# I4 --> A2
# A1 --> A2
# A2 --> A3
# I1 --> A4
# I2 --> A4
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# 枚举
# ============================================================================


class EmotionPhase(str, Enum):
    """情绪周期4+1阶段（顺序：冰点→反核→主升→疯狂→退潮→冰点…循环）。"""

    FREEZING = "冰点"  # 连板断层，市场冰点
    REVERSAL = "反核"  # 首板密集，情绪反核
    MAIN_RISE = "主升"  # 龙头加速，情绪主升
    MANIA = "疯狂"  # 高位接力，情绪疯狂
    RETREAT = "退潮"  # 断板潮，情绪退潮
    UNKNOWN = "未知"


class StrategyAction(str, Enum):
    """各情绪阶段策略映射。"""

    WAIT = "空仓/埋伏"  # 冰点期
    SMALL_TRIAL = "小仓试错"  # 反核期
    CORE_POSITION = "核心仓做龙头"  # 主升期
    LEADER_ONLY = "只做龙头"  # 疯狂期
    CLEAR_WAIT = "空仓等冰点"  # 退潮期
    NEUTRAL = "中性观望"  # 未知


# ============================================================================
# 配置（设计文档默认值，可配置）
# ============================================================================


@dataclass(frozen=True)
class YouziEmotionConfig:
    """游资接力情绪引擎可配置阈值——默认值取自设计文档 §D-SIGNAL-33。"""

    # ── 因子1: 连板高度 (满分25) ──
    # 连板高度越高，游资接力情绪越强
    consecutive_height_base: int = 1  # 1连板基础分
    consecutive_height_step: int = 5  # 每增加1板加分
    consecutive_height_max_score: float = 25.0

    # ── 因子2: 封单质量 (满分20) ──
    # 封流比 = 封单金额 / 流通市值
    seal_ratio_excellent: float = 0.10  # >=10% → 满分
    seal_ratio_good: float = 0.05  # >=5% → 15分
    seal_ratio_fair: float = 0.02  # >=2% → 10分
    seal_ratio_max_score: float = 20.0

    # ── 因子3: 涨停时间 (满分15) ──
    # 越早涨停越好
    # 9:25前(一字板) → 15分; 9:25-10:00 → 12分; 10:00-11:00 → 8分;
    # 11:00-13:30 → 5分; 13:30-14:30 → 3分; 14:30后 → 1分
    seal_time_max_score: float = 15.0

    # ── 因子4: 开板次数 (满分15) ──
    # 开板次数越少越好（0次=15分, 1次=8分, 2次=3分, >=3次=0分）
    open_board_0_score: float = 15.0
    open_board_1_score: float = 8.0
    open_board_2_score: float = 3.0
    open_board_3plus_score: float = 0.0

    # ── 因子5: 竞价强度 (满分10) ──
    # 竞价涨幅 + 竞价量比
    auction_rise_excellent: float = 5.0  # >=5% → 满分
    auction_rise_good: float = 3.0  # >=3% → 7分
    auction_rise_fair: float = 1.0  # >=1% → 4分
    auction_volume_ratio_good: float = 2.0  # 竞价量比>=2 → 加分
    auction_max_score: float = 10.0

    # ── 因子6: 助攻梯队 (满分10) ──
    # 同板块涨停家数（助攻梯队越完整越好）
    assist_count_excellent: int = 5  # >=5家 → 满分
    assist_count_good: int = 3  # >=3家 → 7分
    assist_count_fair: int = 1  # >=1家 → 4分
    assist_max_score: float = 10.0

    # ── 情绪周期阶段阈值 ──
    # 基于综合情绪评分划分阶段
    phase_freezing_max: float = 20.0  # <=20 → 冰点
    phase_reversal_max: float = 40.0  # 20-40 → 反核
    phase_main_rise_max: float = 65.0  # 40-65 → 主升
    phase_mania_max: float = 85.0  # 65-85 → 疯狂
    # >85 → 退潮（过高反而危险，疯狂后必退潮）


# ============================================================================
# 输入 / 输出
# ============================================================================


@dataclass
class YouziEmotionInput:
    """游资接力情绪引擎输入数据。"""

    # ── 连板高度因子 ──
    consecutive_limit_ups: int = 0  # 连板数（1=首板, 2=二板, ...）

    # ── 封单质量因子 ──
    seal_amount: float = 0.0  # 封单金额(元)
    float_market_cap: float = 0.0  # 流通市值(元)

    # ── 涨停时间因子 ──
    seal_time: datetime | None = None  # 封板时间

    # ── 开板次数因子 ──
    open_board_count: int = 0  # 盘中开板次数

    # ── 竞价强度因子 ──
    auction_rise_pct: float = 0.0  # 竞价涨幅(%)
    auction_volume_ratio: float = 1.0  # 竞价量比

    # ── 助攻梯队因子 ──
    sector_limit_up_count: int = 0  # 同板块涨停家数

    # ── 市场环境 ──
    market_limit_up_count: int = 0  # 全市场涨停家数
    market_breadth_ratio: float = 0.5  # 涨跌家数比(0-1)


@dataclass
class FactorScore:
    """单因子评分结果。"""

    name: str
    score: float
    max_score: float
    detail: str


@dataclass
class YouziEmotionResult:
    """游资接力情绪引擎分析结果。"""

    total_score: float  # 综合情绪评分(0-100)
    factor_scores: list[FactorScore]  # 6因子明细
    emotion_phase: str  # 情绪周期阶段
    phase_confidence: float  # 阶段置信度
    strategy_action: str  # 策略映射
    is_degraded: bool = False
    audit_trail: list[dict[str, Any]] = field(default_factory=list)


# ============================================================================
# 分析器
# ============================================================================


class YouziRelayEmotionEngine:
    """
    A股游资接力情绪引擎（D-SIGNAL-33）。

    6因子评分 + 情绪周期4+1阶段定位 + 策略映射：
      1. 连板高度(25分) — 游资接力核心指标
      2. 封单质量(20分) — 封流比衡量封板强度
      3. 涨停时间(15分) — 越早封板情绪越强
      4. 开板次数(15分) — 开板越少越强
      5. 竞价强度(10分) — 竞价高开+量比
      6. 助攻梯队(10分) — 板块涨停家数
    """

    def __init__(self, config: YouziEmotionConfig | None = None) -> None:
        self._config = config or YouziEmotionConfig()

    # ------------------------------------------------------------------
    # 公开入口
    # ------------------------------------------------------------------

    def analyze(self, input_data: YouziEmotionInput) -> YouziEmotionResult:
        """执行6因子评分 + 情绪周期定位，返回综合结果。"""
        if not self._validate_input(input_data):
            logger.warning("YouziRelayEmotionEngine: 输入数据不合法，返回降级结果")
            return self._degraded_result("输入数据校验失败")

        audit_trail: list[dict[str, Any]] = []

        # ── 6因子评分 ──
        factors: list[FactorScore] = []

        f1 = self.score_consecutive_height(input_data.consecutive_limit_ups)
        factors.append(f1)
        audit_trail.append({"factor": "连板高度", "score": f1.score, "detail": f1.detail})

        f2 = self.score_seal_quality(input_data.seal_amount, input_data.float_market_cap)
        factors.append(f2)
        audit_trail.append({"factor": "封单质量", "score": f2.score, "detail": f2.detail})

        f3 = self.score_seal_time(input_data.seal_time)
        factors.append(f3)
        audit_trail.append({"factor": "涨停时间", "score": f3.score, "detail": f3.detail})

        f4 = self.score_open_board(input_data.open_board_count)
        factors.append(f4)
        audit_trail.append({"factor": "开板次数", "score": f4.score, "detail": f4.detail})

        f5 = self.score_auction_strength(input_data.auction_rise_pct, input_data.auction_volume_ratio)
        factors.append(f5)
        audit_trail.append({"factor": "竞价强度", "score": f5.score, "detail": f5.detail})

        f6 = self.score_assist_echelon(input_data.sector_limit_up_count)
        factors.append(f6)
        audit_trail.append({"factor": "助攻梯队", "score": f6.score, "detail": f6.detail})

        total = min(sum(f.score for f in factors), 100.0)

        # ── 情绪周期定位 ──
        phase, phase_conf = self.determine_emotion_phase(total, input_data)
        audit_trail.append({"factor": "情绪周期", "phase": phase, "confidence": phase_conf})

        # ── 策略映射 ──
        action = self.map_strategy(phase)
        audit_trail.append({"factor": "策略映射", "action": action})

        return YouziEmotionResult(
            total_score=total,
            factor_scores=factors,
            emotion_phase=phase,
            phase_confidence=phase_conf,
            strategy_action=action,
            audit_trail=audit_trail,
        )

    # ------------------------------------------------------------------
    # 因子1: 连板高度 (满分25)
    # ------------------------------------------------------------------

    def score_consecutive_height(self, consecutive_limit_ups: int) -> FactorScore:
        """连板高度评分——连板越高，游资接力情绪越强。"""
        cfg = self._config
        if consecutive_limit_ups <= 0:
            return FactorScore("连板高度", 0.0, cfg.consecutive_height_max_score, "无连板")

        # 基础分 + 每板加分，封顶 max_score
        raw = cfg.consecutive_height_base + (consecutive_limit_ups - 1) * cfg.consecutive_height_step
        score = min(float(raw), cfg.consecutive_height_max_score)
        return FactorScore(
            "连板高度",
            score,
            cfg.consecutive_height_max_score,
            f"{consecutive_limit_ups}连板 → {score}分",
        )

    # ------------------------------------------------------------------
    # 因子2: 封单质量 (满分20)
    # ------------------------------------------------------------------

    def score_seal_quality(self, seal_amount: float, float_market_cap: float) -> FactorScore:
        """封单质量评分——封流比衡量封板强度。"""
        cfg = self._config
        if float_market_cap <= 0:
            return FactorScore("封单质量", 0.0, cfg.seal_ratio_max_score, "流通市值为0")

        seal_ratio = seal_amount / float_market_cap

        if seal_ratio >= cfg.seal_ratio_excellent:
            score = cfg.seal_ratio_max_score
            detail = f"封流比{seal_ratio:.1%} >= {cfg.seal_ratio_excellent:.0%} → 满分"
        elif seal_ratio >= cfg.seal_ratio_good:
            score = 15.0
            detail = f"封流比{seal_ratio:.1%} >= {cfg.seal_ratio_good:.0%} → 15分"
        elif seal_ratio >= cfg.seal_ratio_fair:
            score = 10.0
            detail = f"封流比{seal_ratio:.1%} >= {cfg.seal_ratio_fair:.0%} → 10分"
        else:
            score = max(seal_ratio / cfg.seal_ratio_fair * 10.0, 0.0)
            detail = f"封流比{seal_ratio:.1%} < {cfg.seal_ratio_fair:.0%} → {score:.1f}分"

        return FactorScore("封单质量", score, cfg.seal_ratio_max_score, detail)

    # ------------------------------------------------------------------
    # 因子3: 涨停时间 (满分15)
    # ------------------------------------------------------------------

    def score_seal_time(self, seal_time: datetime | None) -> FactorScore:
        """涨停时间评分——越早封板情绪越强。"""
        cfg = self._config
        if seal_time is None:
            return FactorScore("涨停时间", 0.0, cfg.seal_time_max_score, "无封板时间")

        t = seal_time.time()

        # 分段评分
        if t <= time(9, 25):
            score = cfg.seal_time_max_score  # 一字板
            label = "9:25前(一字板)"
        elif t <= time(10, 0):
            score = 12.0
            label = "9:25-10:00"
        elif t <= time(11, 0):
            score = 8.0
            label = "10:00-11:00"
        elif t <= time(13, 30):
            score = 5.0
            label = "11:00-13:30"
        elif t <= time(14, 30):
            score = 3.0
            label = "13:30-14:30"
        else:
            score = 1.0
            label = "14:30后"

        return FactorScore("涨停时间", score, cfg.seal_time_max_score, f"{label} → {score}分")

    # ------------------------------------------------------------------
    # 因子4: 开板次数 (满分15)
    # ------------------------------------------------------------------

    def score_open_board(self, open_board_count: int) -> FactorScore:
        """开板次数评分——开板越少越强。"""
        cfg = self._config
        if open_board_count <= 0:
            score = cfg.open_board_0_score
            detail = "0次开板 → 满分"
        elif open_board_count == 1:
            score = cfg.open_board_1_score
            detail = "1次开板 → 8分"
        elif open_board_count == 2:
            score = cfg.open_board_2_score
            detail = "2次开板 → 3分"
        else:
            score = cfg.open_board_3plus_score
            detail = f"{open_board_count}次开板 → 0分"

        return FactorScore("开板次数", score, cfg.open_board_0_score, detail)

    # ------------------------------------------------------------------
    # 因子5: 竞价强度 (满分10)
    # ------------------------------------------------------------------

    def score_auction_strength(self, auction_rise_pct: float, auction_volume_ratio: float) -> FactorScore:
        """竞价强度评分——竞价涨幅 + 量比。"""
        cfg = self._config

        # 涨幅分(0-7分)
        if auction_rise_pct >= cfg.auction_rise_excellent:
            rise_score = 7.0
        elif auction_rise_pct >= cfg.auction_rise_good:
            rise_score = 5.0
        elif auction_rise_pct >= cfg.auction_rise_fair:
            rise_score = 3.0
        else:
            rise_score = max(auction_rise_pct / cfg.auction_rise_fair * 3.0, 0.0)

        # 量比分(0-3分)
        if auction_volume_ratio >= cfg.auction_volume_ratio_good:
            vol_score = 3.0
        else:
            vol_score = max(auction_volume_ratio / cfg.auction_volume_ratio_good * 3.0, 0.0)

        total = min(rise_score + vol_score, cfg.auction_max_score)
        detail = f"竞价涨{auction_rise_pct:.1f}% 量比{auction_volume_ratio:.1f} → {total:.1f}分"
        return FactorScore("竞价强度", total, cfg.auction_max_score, detail)

    # ------------------------------------------------------------------
    # 因子6: 助攻梯队 (满分10)
    # ------------------------------------------------------------------

    def score_assist_echelon(self, sector_limit_up_count: int) -> FactorScore:
        """助攻梯队评分——同板块涨停家数。"""
        cfg = self._config
        if sector_limit_up_count >= cfg.assist_count_excellent:
            score = cfg.assist_max_score
            detail = f"板块{sector_limit_up_count}家涨停 → 满分"
        elif sector_limit_up_count >= cfg.assist_count_good:
            score = 7.0
            detail = f"板块{sector_limit_up_count}家涨停 → 7分"
        elif sector_limit_up_count >= cfg.assist_count_fair:
            score = 4.0
            detail = f"板块{sector_limit_up_count}家涨停 → 4分"
        else:
            score = 0.0
            detail = f"板块{sector_limit_up_count}家涨停 → 0分"

        return FactorScore("助攻梯队", score, cfg.assist_max_score, detail)

    # ------------------------------------------------------------------
    # 情绪周期4+1阶段定位
    # ------------------------------------------------------------------

    def determine_emotion_phase(self, total_score: float, input_data: YouziEmotionInput) -> tuple[str, float]:
        """
        根据综合评分 + 市场环境定位情绪周期阶段。

        4+1阶段：冰点/反核/主升/疯狂/退潮
        退潮是"+1"——疯狂后必然退潮，通过市场广度下降检测。
        """
        cfg = self._config

        # 基础阶段由评分决定
        if total_score <= cfg.phase_freezing_max:
            base_phase = EmotionPhase.FREEZING
        elif total_score <= cfg.phase_reversal_max:
            base_phase = EmotionPhase.REVERSAL
        elif total_score <= cfg.phase_main_rise_max:
            base_phase = EmotionPhase.MAIN_RISE
        elif total_score <= cfg.phase_mania_max:
            base_phase = EmotionPhase.MANIA
        else:
            base_phase = EmotionPhase.MANIA  # 超高可能已疯狂

        # ── 退潮检测(+1阶段) ──
        # 疯狂/高分但市场广度下降 → 退潮信号
        if total_score > cfg.phase_mania_max and input_data.market_breadth_ratio < 0.4:
            base_phase = EmotionPhase.RETREAT

        # 高连板但开板频繁 → 退潮信号
        if input_data.consecutive_limit_ups >= 4 and input_data.open_board_count >= 3:
            base_phase = EmotionPhase.RETREAT

        # 冰点检测：全市场涨停家数极少
        if input_data.market_limit_up_count > 0 and input_data.market_limit_up_count <= 5:
            if total_score <= cfg.phase_reversal_max:
                base_phase = EmotionPhase.FREEZING

        # 置信度：评分越接近阶段边界中心，置信度越高
        phase_ranges = {
            EmotionPhase.FREEZING: (0, cfg.phase_freezing_max),
            EmotionPhase.REVERSAL: (cfg.phase_freezing_max, cfg.phase_reversal_max),
            EmotionPhase.MAIN_RISE: (cfg.phase_reversal_max, cfg.phase_main_rise_max),
            EmotionPhase.MANIA: (cfg.phase_main_rise_max, cfg.phase_mania_max),
            EmotionPhase.RETREAT: (cfg.phase_mania_max, 100.0),
        }
        lo, hi = phase_ranges.get(base_phase, (0, 100))
        mid = (lo + hi) / 2
        # 距中心越近置信度越高
        distance = abs(total_score - mid) / max((hi - lo) / 2, 1.0)
        confidence = max(100.0 - distance * 30.0, 50.0)

        return base_phase.value, confidence

    # ------------------------------------------------------------------
    # 策略映射
    # ------------------------------------------------------------------

    def map_strategy(self, phase: str) -> str:
        """各情绪阶段策略映射。"""
        mapping = {
            EmotionPhase.FREEZING.value: StrategyAction.WAIT.value,
            EmotionPhase.REVERSAL.value: StrategyAction.SMALL_TRIAL.value,
            EmotionPhase.MAIN_RISE.value: StrategyAction.CORE_POSITION.value,
            EmotionPhase.MANIA.value: StrategyAction.LEADER_ONLY.value,
            EmotionPhase.RETREAT.value: StrategyAction.CLEAR_WAIT.value,
            EmotionPhase.UNKNOWN.value: StrategyAction.NEUTRAL.value,
        }
        return mapping.get(phase, StrategyAction.NEUTRAL.value)

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _validate_input(self, input_data: YouziEmotionInput) -> bool:
        """校验输入数据基本合法性。"""
        if input_data.consecutive_limit_ups < 0:
            return False
        if input_data.open_board_count < 0:
            return False
        if input_data.float_market_cap < 0:
            return False
        if input_data.seal_amount < 0:
            return False
        return True

    def _degraded_result(self, reason: str) -> YouziEmotionResult:
        """降级结果。"""
        logger.warning("YouziRelayEmotionEngine 降级: %s", reason)
        return YouziEmotionResult(
            total_score=0.0,
            factor_scores=[],
            emotion_phase=EmotionPhase.UNKNOWN.value,
            phase_confidence=0.0,
            strategy_action=StrategyAction.NEUTRAL.value,
            is_degraded=True,
            audit_trail=[{"degraded": True, "reason": reason}],
        )
