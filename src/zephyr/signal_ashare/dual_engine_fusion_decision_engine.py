# [BLUEPRINT] MOD-SIG-035 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_ashare.dual_engine_fusion_decision_engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.youzi_relay_emotion_engine; zephyr.signal_ashare.quant_short_term_strength_engine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 双引擎权重和为1.0; 情绪周期自适应权重不可跳过; 降级路径必须有日志
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/signal_ashare/test_dual_engine_fusion_decision_engine.py
# [A_module] module_id=MOD-SIG-035 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ashare_signal
# category: signal_analyzer
# status: active
# created: "2026-08-02"
# ---

r"""


D-SIGNAL-35 A股双引擎融合决策输出器

游资引擎(D-SIGNAL-33) + 量化引擎(D-SIGNAL-34)信号融合：
  - 基准权重: 60%游资 + 40%量化
  - 情绪周期自适应权重: 冰点→量化70% / 主升→游资70% / 退潮→量化60% / 疯狂→游资80%
  - 6类决策输出: 主升龙头/二进三/跟风/复苏/伪强/地天反包
  - PDF分布信号提取: 方向/置信度/尾部风险/相对价值

理论依据：集成学习 / 贝叶斯融合 / 决策理论。

设计文档默认值可配置——所有权重通过 FusionDecisionConfig 调整，
默认值取自 D:\临时工作区\依赖图-D-SIGNAL-信号域.md §D-SIGNAL-35。

依赖方向：D-SIGNAL-33(游资情绪) + D-SIGNAL-34(量化强度) -> D-SIGNAL-35 -> 下游执行层

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 游资情绪引擎输出 YouziEmotionResult数据类
#   fields: total_score 游资情绪总分 + emotion_phase 情绪周期(冰点/反核/主升/疯狂/退潮)
#   code: FusionDecisionInput.youzi_result L145 来自D-SIGNAL-33
# - id: I2
#   name: 量化强度引擎输出 QuantStrengthResult数据类
#   fields: total_score 量化短线强度总分
#   code: FusionDecisionInput.quant_result L146 来自D-SIGNAL-34
# - id: I3
#   name: 个股上下文 标量参数组
#   fields: 连板数 + 是否主线龙头 + 个股涨幅% + 大盘涨幅% + 风险评分0-100
#   code: FusionDecisionInput L148-L152
# 层: 特征
# - id: F1
#   name_zh: 超额收益
#   name_en: excess
#   intro: 个股涨幅比大盘涨幅多出来多少 衡量相对价值
#   formula: 个股涨幅% - 大盘涨幅% ≥5%→相对价值好 ≥0→中 <0→差
#   code: dual_engine_fusion_decision_engine.py L376
#   registry: factor_registry: 无FCT条目
#   is_break: true
# 层: 算法
# - id: A1
#   name_zh: ① 情绪周期自适应权重
#   name_en: determine_adaptive_weights
#   intro: 按情绪周期查表定双引擎权重 冰点信量化 主升信游资
#   desc: 冰点(0.3/0.7) 反核(0.5/0.5) 主升(0.7/0.3) 疯狂(0.8/0.2) 退潮(0.4/0.6) 未知默认基准(0.6/0.4)
#   inputs: I1
#   outputs: 游资权重 + 量化权重
#   invariant: 双引擎权重和为1.0
# - id: A2
#   name_zh: ② 加权融合评分
#   name_en: analyze Step2 fused score
#   intro: 两个引擎分数按自适应权重加权合成一个融合分
#   desc: fused = min(100, w_游资×游资分 + w_量化×量化分)
#   inputs: I1 I2 A1
#   outputs: fused_score 0-100
# - id: A3
#   name_zh: ③ 6类决策分类
#   name_en: classify_decision
#   intro: 按优先级把股票归入主升龙头/二进三/复苏/伪强/跟风/地天反包/中性
#   desc: 地天反包(1板+涨≥9.5%+风险≥60)→主升龙头(融合≥80+双引擎≥70+主线)→二进三(融合≥65+连板≥2)→复苏(量化≥70+游资40-65)→伪强(游资≥60+量化<50)→跟风(融合50-65)→中性
#   inputs: I1 I2 I3 A2
#   outputs: 6+1类决策标签
# - id: A4
#   name_zh: ④ PDF分布信号提取
#   name_en: extract_pdf_signal
#   intro: 从融合分提取方向/置信度/尾部风险/相对价值4维信号
#   desc: 方向 融合≥65做多 ≤35做空; 置信度=|融合-50|×2; 尾部风险 风险评分≥60高 ≥40或疯狂/退潮期 中; 相对价值按超额收益分档
#   inputs: I1 I3 A2 F1
#   outputs: PDFSignal 4维信号
# 层: 输出
# - id: O1
#   name_zh: 双引擎融合决策结果
#   name_en: FusionDecisionResult
#   intro: 融合分+实际权重+6类决策+PDF信号+情绪周期 一次输出
#   invariant: 双引擎权重和为1.0 情绪周期自适应权重不可跳过 降级路径必须有日志
#   downstream: 无下游/内部使用（设计文档指向下游执行层）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A2
# I1 --> A3
# I2 --> A3
# I3 --> A3
# A2 --> A3
# I3 -.->|断点| F1
# F1 --> A4
# I1 --> A4
# I3 --> A4
# A2 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from zephyr.signal_ashare.quant_short_term_strength_engine import (
    QuantStrengthResult,
    StockCategory,
)
from zephyr.signal_ashare.youzi_relay_emotion_engine import (
    EmotionPhase,
    YouziEmotionResult,
)

logger = logging.getLogger(__name__)


# ============================================================================
# 枚举
# ============================================================================


class FusionDecision(str, Enum):
    """6类决策输出。"""

    MAIN_LEADER = "主升龙头"  # 双引擎强+主线
    SECOND_TO_THIRD = "二进三"  # 游资高+量化中高
    FOLLOWER = "跟风"  # 双引擎中
    RECOVERY = "复苏"  # 量化高+游资中
    FAKE_STRONG = "伪强"  # 游资高+量化低
    INVERSE_BOARD = "地天反包"  # 极端反转
    NEUTRAL = "中性"  # 无法决策


class SignalDirection(str, Enum):
    """PDF信号方向。"""

    LONG = "做多"
    SHORT = "做空"
    NEUTRAL = "观望"


# ============================================================================
# 配置（设计文档默认值，可配置）
# ============================================================================


@dataclass(frozen=True)
class FusionDecisionConfig:
    """双引擎融合决策可配置参数——默认值取自设计文档 §D-SIGNAL-35。"""

    # ── 基准权重 ──
    base_youzi_weight: float = 0.60  # 游资引擎基准权重
    base_quant_weight: float = 0.40  # 量化引擎基准权重

    # ── 情绪周期自适应权重 (youzi_weight, quant_weight) ──
    # 冰点期：量化主导(游资情绪冰点，量化更可靠)
    phase_weights_freezing: tuple[float, float] = (0.30, 0.70)
    # 反核期：均衡(情绪开始反转，双引擎各有优势)
    phase_weights_reversal: tuple[float, float] = (0.50, 0.50)
    # 主升期：游资主导(游资接力是主升核心驱动力)
    phase_weights_main_rise: tuple[float, float] = (0.70, 0.30)
    # 疯狂期：游资极主导(情绪疯狂，游资信号最强)
    phase_weights_mania: tuple[float, float] = (0.80, 0.20)
    # 退潮期：量化主导(游资退潮信号不可靠，量化控制风险)
    phase_weights_retreat: tuple[float, float] = (0.40, 0.60)

    # ── 6类决策阈值 ──
    # 主升龙头: 融合分>=80 + 游资>=70 + 量化>=70 + 主线
    main_leader_fused_min: float = 80.0
    main_leader_youzi_min: float = 70.0
    main_leader_quant_min: float = 70.0
    # 二进三: 融合分>=65 + 连板>=2
    second_to_third_fused_min: float = 65.0
    second_to_third_consecutive_min: int = 2
    # 复苏: 量化>=70 + 游资40-65
    recovery_quant_min: float = 70.0
    # 伪强: 游资>=60 + 量化<50
    fake_strong_youzi_min: float = 60.0
    fake_strong_quant_max: float = 50.0
    # 跟风: 融合分50-65
    follower_fused_min: float = 50.0
    follower_fused_max: float = 65.0

    # ── PDF信号阈值 ──
    long_threshold: float = 65.0  # 融合分>=65 → 做多
    short_threshold: float = 35.0  # 融合分<=35 → 做空
    confidence_high: float = 75.0  # 高置信度阈值
    tail_risk_threshold: float = 60.0  # 尾部风险阈值
    relative_value_good: float = 5.0  # 相对价值好阈值(超额收益%)


# ============================================================================
# 输入 / 输出
# ============================================================================


@dataclass
class FusionDecisionInput:
    """双引擎融合决策输入——消费两个引擎的输出。"""

    youzi_result: YouziEmotionResult  # D-SIGNAL-33 游资情绪输出
    quant_result: QuantStrengthResult  # D-SIGNAL-34 量化强度输出
    # 额外上下文
    consecutive_limit_ups: int = 0  # 连板数
    is_main_line: bool = False  # 是否主线龙头
    stock_change_pct: float = 0.0  # 个股涨幅(%)
    market_change_pct: float = 0.0  # 大盘涨幅(%)
    risk_score: float = 50.0  # 风险评分(0-100)


@dataclass
class PDFSignal:
    """PDF分布信号提取结果。"""

    direction: str  # 方向: 做多/做空/观望
    confidence: float  # 置信度(0-100)
    tail_risk: str  # 尾部风险: 高/中/低
    relative_value: str  # 相对价值: 好/中/差
    detail: str


@dataclass
class FusionDecisionResult:
    """双引擎融合决策输出。"""

    fused_score: float  # 融合评分(0-100)
    youzi_weight: float  # 实际游资权重
    quant_weight: float  # 实际量化权重
    decision: str  # 6类决策
    pdf_signal: PDFSignal  # PDF信号
    emotion_phase: str  # 情绪周期(来自游资引擎)
    is_degraded: bool = False
    audit_trail: list[dict[str, Any]] = field(default_factory=list)


# ============================================================================
# 分析器
# ============================================================================


class DualEngineFusionDecisionEngine:
    """
    A股双引擎融合决策输出器（D-SIGNAL-35）。

    融合流程：
      1. 获取游资引擎 + 量化引擎输出
      2. 根据情绪周期确定自适应权重
      3. 计算融合评分 = youzi_weight * youzi_score + quant_weight * quant_score
      4. 6类决策输出分类
      5. PDF分布信号提取(方向/置信度/尾部风险/相对价值)
    """

    def __init__(self, config: FusionDecisionConfig | None = None) -> None:
        self._config = config or FusionDecisionConfig()

    # ------------------------------------------------------------------
    # 公开入口
    # ------------------------------------------------------------------

    def analyze(self, input_data: FusionDecisionInput) -> FusionDecisionResult:
        """执行双引擎融合决策，返回综合结果。"""
        if not self._validate_input(input_data):
            logger.warning("DualEngineFusionDecisionEngine: 输入数据不合法，返回降级结果")
            return self._degraded_result("输入数据校验失败")

        # 降级传播契约：上游引擎结果已降级时，融合结果必须降级且不产出决策
        # （降级输入融合出的分数与真实弱信号不可区分，会掩盖上游数据质量问题）
        degraded_upstreams = [
            name
            for name, res in (("youzi", input_data.youzi_result), ("quant", input_data.quant_result))
            if res.is_degraded
        ]
        if degraded_upstreams:
            reason = f"上游引擎结果降级: {','.join(degraded_upstreams)}"
            logger.warning("DualEngineFusionDecisionEngine: %s，返回降级结果", reason)
            return self._degraded_result(reason)

        audit_trail: list[dict[str, Any]] = []

        youzi_score = input_data.youzi_result.total_score
        quant_score = input_data.quant_result.total_score
        emotion_phase = input_data.youzi_result.emotion_phase

        audit_trail.append({"step": "引擎输入", "youzi_score": youzi_score, "quant_score": quant_score})

        # ── Step1: 情绪周期自适应权重 ──
        youzi_w, quant_w = self.determine_adaptive_weights(emotion_phase)
        audit_trail.append(
            {
                "step": "自适应权重",
                "emotion_phase": emotion_phase,
                "youzi_weight": youzi_w,
                "quant_weight": quant_w,
            }
        )

        # ── Step2: 融合评分 ──
        fused = youzi_w * youzi_score + quant_w * quant_score
        fused = min(fused, 100.0)
        audit_trail.append({"step": "融合评分", "fused_score": fused})

        # ── Step3: 6类决策输出 ──
        decision = self.classify_decision(fused, youzi_score, quant_score, input_data)
        audit_trail.append({"step": "决策分类", "decision": decision})

        # ── Step4: PDF信号提取 ──
        pdf = self.extract_pdf_signal(fused, input_data)
        audit_trail.append({"step": "PDF信号", "direction": pdf.direction, "confidence": pdf.confidence})

        return FusionDecisionResult(
            fused_score=fused,
            youzi_weight=youzi_w,
            quant_weight=quant_w,
            decision=decision,
            pdf_signal=pdf,
            emotion_phase=emotion_phase,
            audit_trail=audit_trail,
        )

    # ------------------------------------------------------------------
    # Step1: 情绪周期自适应权重
    # ------------------------------------------------------------------

    def determine_adaptive_weights(self, emotion_phase: str) -> tuple[float, float]:
        """
        根据情绪周期确定自适应权重 (youzi_weight, quant_weight)。

        权重和为1.0——不同阶段双引擎的可信度不同：
          - 冰点/退潮: 量化更可靠(游资情绪不可靠)
          - 主升/疯狂: 游资更可靠(游资接力是核心驱动力)
          - 反核: 均衡
        """
        cfg = self._config
        weights_map = {
            EmotionPhase.FREEZING.value: cfg.phase_weights_freezing,
            EmotionPhase.REVERSAL.value: cfg.phase_weights_reversal,
            EmotionPhase.MAIN_RISE.value: cfg.phase_weights_main_rise,
            EmotionPhase.MANIA.value: cfg.phase_weights_mania,
            EmotionPhase.RETREAT.value: cfg.phase_weights_retreat,
        }
        # 默认使用基准权重
        return weights_map.get(emotion_phase, (cfg.base_youzi_weight, cfg.base_quant_weight))

    # ------------------------------------------------------------------
    # Step3: 6类决策输出分类
    # ------------------------------------------------------------------

    def classify_decision(
        self,
        fused_score: float,
        youzi_score: float,
        quant_score: float,
        input_data: FusionDecisionInput,
    ) -> str:
        """
        6类决策分类——结合融合评分 + 各引擎评分 + 连板 + 主线。

        优先级：
        1. 主升龙头: 融合>=80 + 游资>=70 + 量化>=70 + 主线
        2. 二进三: 融合>=65 + 连板>=2
        3. 复苏: 量化>=70 + 游资40-65
        4. 伪强: 游资>=60 + 量化<50
        5. 跟风: 融合50-65
        6. 地天反包: 极端反转形态
        """
        cfg = self._config

        # 地天反包：极端反转(连板=1 + 涨停 + 高风险)
        if input_data.consecutive_limit_ups == 1 and input_data.stock_change_pct >= 9.5 and input_data.risk_score >= 60:
            return FusionDecision.INVERSE_BOARD.value

        # 1. 主升龙头
        if (
            fused_score >= cfg.main_leader_fused_min
            and youzi_score >= cfg.main_leader_youzi_min
            and quant_score >= cfg.main_leader_quant_min
            and input_data.is_main_line
        ):
            return FusionDecision.MAIN_LEADER.value

        # 2. 二进三
        if (
            fused_score >= cfg.second_to_third_fused_min
            and input_data.consecutive_limit_ups >= cfg.second_to_third_consecutive_min
        ):
            return FusionDecision.SECOND_TO_THIRD.value

        # 3. 复苏
        if quant_score >= cfg.recovery_quant_min and 40.0 <= youzi_score < 65.0:
            return FusionDecision.RECOVERY.value

        # 4. 伪强
        if youzi_score >= cfg.fake_strong_youzi_min and quant_score < cfg.fake_strong_quant_max:
            return FusionDecision.FAKE_STRONG.value

        # 5. 跟风
        if cfg.follower_fused_min <= fused_score <= cfg.follower_fused_max:
            return FusionDecision.FOLLOWER.value

        return FusionDecision.NEUTRAL.value

    # ------------------------------------------------------------------
    # Step4: PDF分布信号提取
    # ------------------------------------------------------------------

    def extract_pdf_signal(self, fused_score: float, input_data: FusionDecisionInput) -> PDFSignal:
        """
        PDF分布信号提取——从融合评分提取4维信号。

        1. 方向: 做多/做空/观望
        2. 置信度: 基于融合评分距阈值的距离
        3. 尾部风险: 基于风险评分和情绪周期
        4. 相对价值: 个股 vs 大盘超额收益
        """
        cfg = self._config

        # ── 方向 ──
        if fused_score >= cfg.long_threshold:
            direction = SignalDirection.LONG.value
        elif fused_score <= cfg.short_threshold:
            direction = SignalDirection.SHORT.value
        else:
            direction = SignalDirection.NEUTRAL.value

        # ── 置信度 ──
        # 距50越远置信度越高
        confidence = abs(fused_score - 50.0) * 2.0
        confidence = min(confidence, 100.0)

        # ── 尾部风险 ──
        # 高风险评分 + 疯狂/退潮期 → 高尾部风险
        phase = input_data.youzi_result.emotion_phase
        if input_data.risk_score >= cfg.tail_risk_threshold:
            tail_risk = "高"
        elif input_data.risk_score >= 40.0 or phase in (
            EmotionPhase.MANIA.value,
            EmotionPhase.RETREAT.value,
        ):
            tail_risk = "中"
        else:
            tail_risk = "低"

        # ── 相对价值 ──
        excess = input_data.stock_change_pct - input_data.market_change_pct
        if excess >= cfg.relative_value_good:
            relative_value = "好"
        elif excess >= 0.0:
            relative_value = "中"
        else:
            relative_value = "差"

        detail = (
            f"方向={direction} 置信度={confidence:.0f}% "
            f"尾部风险={tail_risk} 相对价值={relative_value}(超额{excess:.1f}%)"
        )

        return PDFSignal(
            direction=direction,
            confidence=confidence,
            tail_risk=tail_risk,
            relative_value=relative_value,
            detail=detail,
        )

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _validate_input(self, input_data: FusionDecisionInput) -> bool:
        """校验输入数据基本合法性。"""
        if input_data.youzi_result is None:
            return False
        if input_data.quant_result is None:
            return False
        if input_data.consecutive_limit_ups < 0:
            return False
        if input_data.risk_score < 0 or input_data.risk_score > 100:
            return False
        return True

    def _degraded_result(self, reason: str) -> FusionDecisionResult:
        """降级结果。"""
        logger.warning("DualEngineFusionDecisionEngine 降级: %s", reason)
        return FusionDecisionResult(
            fused_score=0.0,
            youzi_weight=0.0,
            quant_weight=0.0,
            decision=FusionDecision.NEUTRAL.value,
            pdf_signal=PDFSignal(
                direction=SignalDirection.NEUTRAL.value,
                confidence=0.0,
                tail_risk="高",
                relative_value="差",
                detail=f"降级: {reason}",
            ),
            emotion_phase=EmotionPhase.UNKNOWN.value,
            is_degraded=True,
            audit_trail=[{"degraded": True, "reason": reason}],
        )
