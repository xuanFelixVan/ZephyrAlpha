# [BLUEPRINT] MOD-REGIME-001 | docs/03_modules/_domain_regime/regime_detector/blueprint.md
# [MODULE] zephyr.regime.core.regime_detector
# [DOMAIN] D_REGIME
# [DEPENDENCIES] hmmlearn; numpy; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-PA-007(RegimeMetaAllocator消费RegimeProbabilities+Shrinkage); BM-BT-03-E(回测验证消费12维概率)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] RegimeProbabilities.probabilities Σ=1.0; Shrinkage≤1.0(只减不增); shrinkage_enabled=False时Shrinkage=1.0; HMM 9态3×3网格walk-forward季度重拟合; 不输出硬标签只输出12维灰度概率
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RegimeFeatureError(ZA-REGIME-0001); HMMFittingError(ZA-REGIME-0002); ShrinkageComputationError(ZA-REGIME-0003); OverlayRuleError(ZA-REGIME-0004); ProbabilityNormalizationError(ZA-REGIME-0005)
# [TESTS] tests/regime/test_regime_detector.py
# [A_module] module_id=MOD-REGIME-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RegimeDetector — 12态Regime检测器 (MOD-REGIME-001)

D_REGIME 域核心模块，整个交易决策架构的**最上游**。输出 12 维灰度概率分布 +
Shrinkage 风险节流因子，供 RegimeMetaAllocator 做 budget 分配。是 regime 链源头
（regime → Shrinkage → budget → StrategyBook）。

五子模块（discussion_002 §8.1）：
    ① HMM 9态（趋势×波动率 3×3 网格）—— hmmlearn GaussianHMM
    ② D-SIGNAL-68 覆盖层（CRISIS/RECOVERY/BREAKOUT 规则触发 + 8转换评分）
    ③ ConfidenceSignal（max(P) 4档映射 + 稀有态折扣）
    ④ RiskSignal（13参数完整计算 + 聚合公式）
    ⑤ Shrinkage（ConfidenceSignal × RiskSignal，可开关）

可验证性接口（discussion_002 §4 验证需求，接口设计不可破坏）：
    ① 输出 12 维概率分布（RegimeProbabilities，Σ=1）—— B1 校准度 / B2 CRPS
    ② Shrinkage 可开关（shrinkage_enabled）—— C1 开/关对比（**一票否决**）
    ③ 8 转换触发可记录（TransitionTriggered）—— B4 转换触发准确性
    ④ HMM hmmlearn GaussianHMM 9态 walk-forward 季度重拟合 —— A1/A2/A3 模型质量

降级策略（blueprint §7.4）：hmmlearn 不可用 / 拟合失败 → HMM 9 态均匀分布 P=1/9；
RiskSignalInputs 缺失 → RiskSignal=1.0；OverlaySignals 缺失 → 退化为纯 HMM。

依据: discussion_001 v1.3.1（12态完整 spec）/ discussion_002 v1.0.0（验证方案）
SSoT: depgraph MOD-REGIME-001
Version: 0.2.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

# 12 态编号（discussion_001 §3，D-SIGNAL-04）
REGIME_STATES: list[str] = [f"r{i}" for i in range(1, 13)]
# r1-r9: HMM 9态（趋势×波动率 3×3 网格）；r10 CRISIS / r11 RECOVERY / r12 BREAKOUT
HMM_STATES: list[str] = [f"r{i}" for i in range(1, 10)]
OVERLAY_STATES: list[str] = ["r10", "r11", "r12"]

# 8 转换（discussion_001 §4，T1-T6 趋势/震荡转换 + S1/S2 恐慌/复苏转换）
TRANSITIONS: list[str] = ["T1", "T2", "T3", "T4", "T5", "T6", "S1", "S2"]

# Shrinkage 4 档映射（design_memo_001 §2.2 / discussion_001 §5.1）
# (max(P) 下界, base_confidence) —— 从高到低匹配，取首个 max(P) >= 下界
_CONFIDENCE_BANDS: tuple[tuple[float, float], ...] = (
    (0.95, 1.0),   # >95% → 满部署
    (0.80, 0.85),  # 80-95% → 轻度收缩
    (0.60, 0.6),   # 60-80% → 中度收缩
    (0.0, 0.3),    # <60% → 强收缩
)
# 稀有态折扣（design_memo_001 §2.2）：(频率下界, discount)
_RARITY_BANDS: tuple[tuple[float, float], ...] = (
    (0.05, 1.0),   # 常见态 >5%
    (0.01, 0.85),  # 中等态 1-5%
    (0.0, 0.7),    # 稀有态 <1%
)

# 8 转换阶段配置（discussion_001 §4.1 总览表 + §4.6/§4.10.8/§4.11.8/§4.12.8 标准汇总）
# 每个 stage 的条件：total_gte（总分下界）/ keys_gte（关键维度下界，任一缺失即不满足）
# p_overlay：该阶段触发的特殊态概率覆盖（覆盖 HMM）；shrinkage：该阶段的 Shrinkage 锚定值
# stage 判定优先级：strong_confirm > confirm > trigger > fail（取首个满足）
# 维度 key 命名对齐 spec：调用方在 score_breakdown 中提供同名 key
TRANSITION_CONFIG: dict[str, dict[str, Any]] = {
    "T1": {  # Neutral-Medium → BREAKOUT → Bull-Medium（§4.6 三阶段评分）
        "overlay_target": "r12",
        "stages": {
            "confirm":       {"keys_gte": {"bqs": 60, "rcs": 60}, "p_overlay": {}, "shrinkage": 1.0},
            "trigger":       {"keys_gte": {"bqs": 60}, "p_overlay": {"r12": 0.80}, "shrinkage": 0.85},
            "fail":          {"keys_gte": {"frs": 60}, "p_overlay": {}, "shrinkage": 0.6},
        },
    },
    "T2": {  # Bear-Low → RECOVERY（§4.7 冰点反核）
        "overlay_target": "r11",
        "stages": {
            "confirm":  {"total_gte": 180, "p_overlay": {"r11": 0.65}, "shrinkage": 0.6},
            "trigger":  {"total_gte": 120, "p_overlay": {"r11": 0.35}, "shrinkage": 0.6},
            "fail":     {"keys_gte": {"continue_decline": 1}, "p_overlay": {}, "shrinkage": 0.3},
        },
    },
    "T3": {  # RECOVERY → BREAKOUT → Bull-Medium（§4.10.8 主升确立）
        "overlay_target": "r12",
        "stages": {
            "strong_confirm": {"total_gte": 200, "p_overlay": {}, "shrinkage": 1.0},
            "confirm":        {"keys_gte": {"volume_price": 60, "ma_trend": 50, "money_effect": 50},
                               "p_overlay": {}, "shrinkage": 0.85},
            "trigger":        {"keys_gte": {"sentiment": 60, "mainline": 60, "leader": 60},
                               "p_overlay": {"r12": 0.55}, "shrinkage": 0.7},
            "fail":           {"keys_gte": {"one_day_mainline": 1}, "p_overlay": {"r11": 0.60}, "shrinkage": 0.6},
        },
    },
    "T4": {  # Bull-Medium → Bull-High（§4.8 疯狂期赶顶）
        "overlay_target": None,
        "stages": {
            "confirm":  {"total_gte": 180, "p_overlay": {}, "shrinkage": 0.85},
            "trigger":  {"total_gte": 120, "p_overlay": {}, "shrinkage": 0.85},
            "fail":     {"keys_gte": {"shrink_flat": 1}, "p_overlay": {}, "shrinkage": 0.85},
        },
    },
    "T5": {  # Bull-High → Bear-Medium（§4.11.8 逃顶退潮）
        "overlay_target": None,
        "stages": {
            "confirm":  {"total_gte": 180, "p_overlay": {}, "shrinkage": 0.6},
            "trigger":  {"keys_gte": {"leader_break": 60}, "p_overlay": {}, "shrinkage": 0.6},
            "fail":     {"keys_gte": {"rebound_wrap": 1}, "p_overlay": {}, "shrinkage": 0.85},
        },
    },
    "T6": {  # Bear-Medium → Bear-Low（§4.7 退潮冰点）
        "overlay_target": None,
        "stages": {
            "confirm":  {"total_gte": 180, "p_overlay": {}, "shrinkage": 0.3},
            "trigger":  {"total_gte": 120, "p_overlay": {}, "shrinkage": 0.3},
            "fail":     {"keys_gte": {"sudden_volume": 1}, "p_overlay": {"r11": 0.40}, "shrinkage": 0.6},
        },
    },
    "S1": {  # Any → CRISIS（§4.9 VIX Panic + 相关性 + 流动性）
        "overlay_target": "r10",
        "stages": {
            "confirm":  {"keys_gte": {"vix_panic": 60, "correlation": 60, "liquidity": 60},
                         "p_overlay": {"r10": 0.80}, "shrinkage": 0.3},
            "trigger":  {"keys_gte": {"vix_panic": 60, "correlation": 60},
                         "p_overlay": {"r10": 0.60}, "shrinkage": 0.3},
            "fail":     {"keys_gte": {"flash_recover": 1}, "p_overlay": {}, "shrinkage": 0.6},
        },
    },
    "S2": {  # CRISIS → RECOVERY（§4.12.8 八维度见底）
        "overlay_target": "r11",
        "stages": {
            "strong_confirm": {"total_gte": 250, "keys_gte": {"spring": 1, "three_yang": 1},
                               "p_overlay": {"r11": 0.80}, "shrinkage": 0.7},
            "confirm":        {"keys_gte": {"wyckoff": 60, "policy": 40, "valuation": 40, "fund": 50},
                               "p_overlay": {"r11": 0.65}, "shrinkage": 0.6},
            "trigger":        {"keys_gte": {"capitulation": 60, "vix": 40, "bad_news_flat": 40},
                               "p_overlay": {"r11": 0.40}, "shrinkage": 0.4},
            "fail":           {"keys_gte": {"break_sc_low": 1, "vix_new_high": 1, "fund_outflow": 1},
                               "p_overlay": {"r10": 0.60}, "shrinkage": 0.3},
        },
    },
}
# 阶段判定顺序（从高到低）
_STAGE_ORDER: tuple[str, ...] = ("strong_confirm", "confirm", "trigger", "fail")


@dataclass(frozen=True)
class RegimeProbabilities:
    """12 维灰度概率分布（CTR-SIG-012）。

    满足 discussion_002 验证需求 ①：输出 12 维概率分布（非硬标签），供 B1 校准度 / B2 CRPS。
    probabilities 必须 Σ=1.0（INVARIANTS）。
    """

    probabilities: dict[str, float]          # {r1..r12: P(ri)}，Σ=1.0
    hmm_probabilities: dict[str, float]      # {r1..r9: P_hmm(ri)}（归因用）
    overlay_probabilities: dict[str, float]  # {r10..r12: P_overlay(ri)}（归因用）
    dominant_regime: str                     # max(P) 对应的态
    dominant_frequency: float                # dominant_regime 历史频率（稀有态判断用）
    confidence: float                        # max(P) 值
    timestamp: datetime
    schema_version: str = "1.0"


@dataclass(frozen=True)
class ShrinkageResult:
    """Shrinkage 风险节流因子（CTR-SIG-014）。

    满足 discussion_002 验证需求 ②：shrinkage_enabled 可开关。
    - True  → value = ConfidenceSignal × RiskSignal
    - False → value = 1.0（C1 开/关对比基准）
    value ≤ 1.0（只减不增，INVARIANTS）。
    """

    value: float                  # Shrinkage 最终值，≤1.0
    confidence_signal: float      # max(P) → 4 档映射 + 稀有态折扣
    risk_signal: float            # 13 参数聚合
    shrinkage_enabled: bool       # 验证开关（C1 一票否决）
    timestamp: datetime
    schema_version: str = "1.0"


@dataclass(frozen=True)
class TransitionTriggered:
    """8 转换触发记录（E-SIG-01）。

    满足 discussion_002 验证需求 ③：8 转换触发可记录，供 B4 转换触发准确性。
    """

    transition_type: str          # T1-T6 / S1 / S2
    timestamp: datetime
    score_breakdown: dict[str, float]  # 各维度评分明细（如 S2 八维度）
    triggered: bool               # 是否达到触发阈值
    confirmed: bool               # 是否达到确认阈值
    stage: str                    # strong_confirm/confirm/trigger/fail/none
    total_score: float            # 总分（score_breakdown 求和）
    schema_version: str = "1.0"


@dataclass(frozen=True)
class RegimeSnapshot:
    """Regime 快照（E-SIG-02，归因用）。"""

    probabilities: RegimeProbabilities
    shrinkage: ShrinkageResult
    transitions: list[TransitionTriggered] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


# ── 错误契约（blueprint §5）──────────────────────────────────────────


class RegimeFeatureError(ZephyrBaseError):
    """ZA-REGIME-0001: RegimeFeatures 格式非法/缺失必需字段。"""


class HMMFittingError(ZephyrBaseError):
    """ZA-REGIME-0002: HMM 拟合失败（特征缺失/NaN/不收敛/hmmlearn 不可用）。"""


class ShrinkageComputationError(ZephyrBaseError):
    """ZA-REGIME-0003: ConfidenceSignal/RiskSignal 计算异常。"""


class OverlayRuleError(ZephyrBaseError):
    """ZA-REGIME-0004: 覆盖层规则计算异常（评分维度缺失/阈值非法）。"""


class ProbabilityNormalizationError(ZephyrBaseError):
    """ZA-REGIME-0005: 12 维归一化失败（Σ≠1 / 含 NaN）。"""


class RegimeDetector:
    """12 态 Regime 检测器（MOD-REGIME-001）。

    使用方式：
        detector = RegimeDetector(hmm_params={"n_states": 9}, shrinkage_enabled=True)
        detector.fit(train_features)              # walk-forward 季度重拟合
        probs, shrinkage = detector.detect(features, overlay_signals, risk_inputs)

    降级：hmmlearn 不可用 → fit 标记 degraded，detect 返回 HMM 均匀分布（§7.4）。
    """

    def __init__(
        self,
        hmm_params: dict[str, Any] | None = None,
        shrinkage_enabled: bool = True,
        state_frequencies: dict[str, float] | None = None,
    ) -> None:
        """初始化 Regime 检测器。

        Args:
            hmm_params: HMM 超参（n_states=9, covariance_type, n_iter 等）。
            shrinkage_enabled: Shrinkage 开关（验证用，默认 True）。
                discussion_002 C1 开/关对比一票否决——False 时 Shrinkage=1.0。
            state_frequencies: 各态历史频率（稀有态判断用），未提供时按 spec §3 占比估计。
        """
        self.hmm_params = hmm_params or {"n_states": 9, "covariance_type": "full", "n_iter": 100}
        self.shrinkage_enabled = shrinkage_enabled
        self._hmm_model: Any = None  # hmmlearn GaussianHMM，fit() 后赋值
        self._hmm_degraded: bool = False  # hmmlearn 不可用 / 拟合失败标记
        # 各态历史频率（稀有态判断用），默认按 discussion_001 §3.1 占比估计
        self._state_frequencies: dict[str, float] = dict(state_frequencies or {
            "r1": 0.15, "r2": 0.15, "r3": 0.05, "r4": 0.15, "r5": 0.15,
            "r6": 0.05, "r7": 0.10, "r8": 0.10, "r9": 0.05,
            "r10": 0.02, "r11": 0.02, "r12": 0.01,
        })
        self._last_transitions: list[TransitionTriggered] = []  # 最近一次 detect 的转换事件

    # ── 公共接口 ──────────────────────────────────────────────────────

    def detect(
        self,
        regime_features: dict[str, Any],
        overlay_signals: dict[str, Any],
        risk_signal_inputs: dict[str, Any],
    ) -> tuple[RegimeProbabilities, ShrinkageResult]:
        """主入口：输出 12 维灰度概率 + Shrinkage。

        满足 discussion_002 验证需求 ①②：12 维概率分布 + Shrinkage 可开关。
        供 RegimeMetaAllocator (MOD-PA-007) 消费。

        Args:
            regime_features: HMM 特征（波动率分位/趋势斜率/相关性矩阵/涨跌家数/量能异动）。
            overlay_signals: 覆盖层信号，结构 {"transitions": {T_id: {dim: score}}}。
            risk_signal_inputs: RiskSignal 13 参数输入，结构 {"params": {#id: coef}, "opportunity": {...}}。

        Returns:
            (RegimeProbabilities, ShrinkageResult)
        """
        # 子模块①：HMM 9态
        hmm_probs = self._run_hmm(regime_features)
        # 子模块②：覆盖层 3 特殊态 + 8 转换评分
        overlay_probs = self._run_overlay(overlay_signals)
        # 12 维合并归一化
        probs = self._merge_probabilities(hmm_probs, overlay_probs)
        # 子模块③④⑤：Shrinkage 链
        confidence = self._compute_confidence_signal(probs)
        risk = self._compute_risk_signal(risk_signal_inputs)
        shrinkage = self._compute_shrinkage(confidence, risk)
        return probs, shrinkage

    def fit(self, train_features: dict[str, Any]) -> None:
        """HMM 拟合（walk-forward 季度重拟合）。

        满足 discussion_002 验证需求 ④：hmmlearn GaussianHMM 9 态 walk-forward。

        Args:
            train_features: {"X": np.ndarray (T, F), "lengths": list[int]} 序列特征。
                X 为观测矩阵（T 个时间步 × F 个特征），lengths 为多序列长度（可选）。

        Raises:
            HMMFittingError: 特征缺失/含 NaN/不收敛。
        """
        try:
            from hmmlearn.hmm import GaussianHMM  # lazy import，hmmlearn 不可用时降级
        except Exception as exc:  # pragma: no cover
            self._hmm_degraded = True
            self._hmm_model = None
            raise HMMFittingError(
                "hmmlearn 不可用，HMM 降级为均匀分布（blueprint §7.4）"
            ) from exc

        X = train_features.get("X")
        if X is None:
            raise HMMFittingError("train_features 缺少 'X' 观测矩阵")
        try:
            import numpy as np
            if not isinstance(X, np.ndarray):
                X = np.asarray(X, dtype=float)
            if X.ndim != 2:
                raise HMMFittingError(f"X 维度应为 2D (T, F)，实际 {X.ndim}D")
            if not np.isfinite(X).all():
                raise HMMFittingError("X 含 NaN/Inf，无法拟合")
        except HMMFittingError:
            raise
        except Exception as exc:
            raise HMMFittingError(f"X 校验失败: {exc}") from exc

        n_states = int(self.hmm_params.get("n_states", 9))
        model = GaussianHMM(
            n_components=n_states,
            covariance_type=self.hmm_params.get("covariance_type", "full"),
            n_iter=self.hmm_params.get("n_iter", 100),
            random_state=self.hmm_params.get("random_state", 42),
        )
        lengths = train_features.get("lengths")
        try:
            model.fit(X, lengths=lengths) if lengths is not None else model.fit(X)
        except Exception as exc:
            self._hmm_degraded = True
            self._hmm_model = None
            raise HMMFittingError(f"GaussianHMM.fit 不收敛: {exc}") from exc
        self._hmm_model = model
        self._hmm_degraded = False

    def record_transition(
        self, transition_type: str, score_breakdown: dict[str, float]
    ) -> TransitionTriggered:
        """记录 8 转换触发事件（动态评分制聚合）。

        满足 discussion_002 验证需求 ③：8 转换触发可记录，供 B4 转换触发准确性。

        Args:
            transition_type: T1-T6 / S1 / S2（不在 TRANSITIONS 中抛 ValueError）。
            score_breakdown: 各维度分值明细（如 S2 的 {capitulation, wyckoff, vix, ...}）。

        Returns:
            TransitionTriggered：含 stage（strong_confirm/confirm/trigger/fail/none）+ 总分。
        """
        if transition_type not in TRANSITIONS:
            raise ValueError(f"未知转换类型 {transition_type}，合法值 {TRANSITIONS}")
        if not isinstance(score_breakdown, dict):
            raise OverlayRuleError(f"{transition_type} score_breakdown 必须为 dict")

        total = float(sum(v for v in score_breakdown.values() if isinstance(v, (int, float))))
        cfg = TRANSITION_CONFIG.get(transition_type, {})
        stages = cfg.get("stages", {})
        stage = "none"
        for cand in _STAGE_ORDER:
            cond = stages.get(cand)
            if cond and self._eval_stage(score_breakdown, total, cond):
                stage = cand
                break
        return TransitionTriggered(
            transition_type=transition_type,
            timestamp=datetime.now(),
            score_breakdown=dict(score_breakdown),
            triggered=stage in ("trigger", "confirm", "strong_confirm"),
            confirmed=stage in ("confirm", "strong_confirm"),
            stage=stage,
            total_score=total,
        )

    # ── 子模块 ① HMM 9态 ─────────────────────────────────────────────

    def _run_hmm(self, regime_features: dict[str, Any]) -> dict[str, float]:
        """子模块①：HMM 9态推断，输出 P_hmm(r1)..P_hmm(r9)，Σ=1.0。

        降级：_hmm_model is None（未 fit / hmmlearn 不可用）→ 均匀分布 1/9（§7.4）。
        """
        if self._hmm_model is None or self._hmm_degraded:
            return {s: 1.0 / 9.0 for s in HMM_STATES}

        X = regime_features.get("X")
        if X is None:
            # 缺特征时降级（不抛错，保证 detect 可用）
            return {s: 1.0 / 9.0 for s in HMM_STATES}
        try:
            import numpy as np
            if not isinstance(X, np.ndarray):
                X = np.asarray(X, dtype=float)
            if X.ndim == 1:
                X = X.reshape(1, -1)
            # predict_proba 返回 (T, n_states)，取最后一步（因果 Viterbi 防前视）
            probs = self._hmm_model.predict_proba(X)
            last = probs[-1]
            if len(last) != 9:
                # 状态数不匹配，降级
                return {s: 1.0 / 9.0 for s in HMM_STATES}
            return {HMM_STATES[i]: float(last[i]) for i in range(9)}
        except Exception:
            # 推断异常降级为均匀分布，保证 detect 鲁棒
            return {s: 1.0 / 9.0 for s in HMM_STATES}

    # ── 子模块 ② D-SIGNAL-68 覆盖层 ──────────────────────────────────

    def _run_overlay(self, overlay_signals: dict[str, Any]) -> dict[str, float]:
        """子模块②：3 特殊态（CRISIS/RECOVERY/BREAKOUT）规则触发 + 8 转换评分。

        输出 P_overlay(r10..r12)，并内部调用 record_transition() 记录 8 转换。
        无转换触发时返回全 0（退化为纯 HMM）。

        overlay_signals 结构：{"transitions": {T_id: {dim: score}, ...}}
        """
        transitions_in: dict[str, dict[str, float]] = (
            overlay_signals.get("transitions") if isinstance(overlay_signals, dict) else None
        ) or {}
        recorded: list[TransitionTriggered] = []
        # 每个特殊态取所有相关转换里最高的 p_overlay（后发覆盖先发）
        overlay_best: dict[str, float] = {"r10": 0.0, "r11": 0.0, "r12": 0.0}
        for tid, breakdown in transitions_in.items():
            if tid not in TRANSITIONS or not isinstance(breakdown, dict):
                continue
            try:
                trig = self.record_transition(tid, breakdown)
            except (ValueError, OverlayRuleError):
                continue
            recorded.append(trig)
            if trig.stage == "none":
                continue
            stage_cfg = TRANSITION_CONFIG[tid]["stages"][trig.stage]
            for state, p in stage_cfg.get("p_overlay", {}).items():
                if state in overlay_best and p > overlay_best[state]:
                    overlay_best[state] = float(p)
        self._last_transitions = recorded
        return overlay_best

    # ── 子模块 ③④⑤ Shrinkage 链 ─────────────────────────────────────

    def _merge_probabilities(
        self, hmm_probs: dict[str, float], overlay_probs: dict[str, float]
    ) -> RegimeProbabilities:
        """12 维合并归一化（blueprint §3.3）：覆盖层概率压缩 HMM 概率质量。

            overlay_mass = Σ P_overlay(r10..r12)
            hmm_scale = 1 − overlay_mass
            P(r1..r9) = P_hmm(r_i) × hmm_scale
            P(r10..r12) = P_overlay(r_i)
            normalize → Σ=1.0
        """
        overlay_mass = sum(overlay_probs.get(s, 0.0) for s in OVERLAY_STATES)
        if overlay_mass > 1.0:
            # 覆盖层总概率超 1（多转换同时触发），等比压缩回 1.0
            overlay_mass = 1.0
            scale = 1.0 / sum(overlay_probs.get(s, 0.0) for s in OVERLAY_STATES)
            overlay_probs = {s: overlay_probs.get(s, 0.0) * scale for s in OVERLAY_STATES}
        hmm_scale = 1.0 - overlay_mass

        merged: dict[str, float] = {}
        for s in HMM_STATES:
            merged[s] = hmm_probs.get(s, 0.0) * hmm_scale
        for s in OVERLAY_STATES:
            merged[s] = overlay_probs.get(s, 0.0)

        merged = self._normalize(merged)
        dominant = max(merged, key=lambda k: merged[k])
        confidence = merged[dominant]
        freq = self._state_frequencies.get(dominant, 0.0)
        return RegimeProbabilities(
            probabilities=merged,
            hmm_probabilities=dict(hmm_probs),
            overlay_probabilities=dict(overlay_probs),
            dominant_regime=dominant,
            dominant_frequency=freq,
            confidence=confidence,
            timestamp=datetime.now(),
        )

    def _compute_confidence_signal(self, probs: RegimeProbabilities) -> float:
        """子模块③：max(P) → 4 档映射 + 稀有态折扣（design_memo_001 §2.2）。

        ConfidenceSignal = base_confidence(max(P)) × rarity_discount(dominant_frequency)
        最低 0.3 × 0.7 = 0.21。
        """
        max_p = probs.confidence
        base = 0.3
        for bound, coef in _CONFIDENCE_BANDS:
            if max_p >= bound:
                base = coef
                break
        rarity = 0.7
        for bound, coef in _RARITY_BANDS:
            if probs.dominant_frequency >= bound:
                rarity = coef
                break
        return base * rarity

    def _compute_risk_signal(self, risk_inputs: dict[str, Any]) -> float:
        """子模块④：13 参数聚合（discussion_001 §5.3.3）。

        RiskSignal = clamp[0.30, RiskBase × 共振惩罚 + 机会恢复, 1.00]
          RiskBase = min(11 个风险参数系数 #1-10/#12)
          共振惩罚 = 1 − 0.05 × max(0, 异常参数数 − 1)，下限 ×0.80
          机会恢复 = #11 鬼故事抵消 + #13 利空不跌抵消，上限 +0.25

        risk_inputs 结构：
            {"params": {1: 0.85, 2: 1.0, ..., 12: 0.6},  # #1-10/#12 系数
             "opportunity": {"news_ghost": 0.10, "bad_news_flat": 0.15}}  # #11/#13 抵消值
        缺失时降级为 RiskSignal=1.0（§7.4）。
        """
        if not isinstance(risk_inputs, dict) or not risk_inputs:
            return 1.0
        params: dict[int, float] = risk_inputs.get("params") or {}
        if not params:
            return 1.0
        # RiskBase：11 个风险参数（#1-10, #12）取最严
        risk_param_ids = [i for i in list(range(1, 11)) + [12]]
        coefs = [float(params[i]) for i in risk_param_ids if i in params and params[i] is not None]
        if not coefs:
            return 1.0
        risk_base = min(coefs)
        # 共振惩罚：异常参数数（系数<1.0）每多一个再扣 5%，下限 ×0.80
        anomaly_count = sum(1 for c in coefs if c < 1.0)
        resonance = max(0.80, 1.0 - 0.05 * max(0, anomaly_count - 1))
        # 机会恢复：#11 鬼故事 + #13 利空不跌，上限 +0.25
        opp = risk_inputs.get("opportunity") or {}
        recovery = 0.0
        if isinstance(opp, dict):
            recovery = float(opp.get("news_ghost", 0.0)) + float(opp.get("bad_news_flat", 0.0))
        recovery = min(recovery, 0.25)
        risk = risk_base * resonance + recovery
        return max(0.30, min(1.00, risk))

    def _compute_shrinkage(
        self, confidence: float, risk: float
    ) -> ShrinkageResult:
        """子模块⑤：Shrinkage = ConfidenceSignal × RiskSignal（可开关）。

        - shrinkage_enabled=True  → value = confidence × risk
        - shrinkage_enabled=False → value = 1.0（C1 验证基准）
        value ≤ 1.0（只减不增，INVARIANTS）。
        """
        if not self.shrinkage_enabled:
            return ShrinkageResult(
                value=1.0, confidence_signal=confidence, risk_signal=risk,
                shrinkage_enabled=False, timestamp=datetime.now(),
            )
        value = confidence * risk
        if value > 1.0:  # 理论上不会（两者均 ≤1.0），防浮点误差
            value = 1.0
        return ShrinkageResult(
            value=value, confidence_signal=confidence, risk_signal=risk,
            shrinkage_enabled=True, timestamp=datetime.now(),
        )

    # ── 辅助 ─────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(probs: dict[str, float]) -> dict[str, float]:
        """归一化到 Σ=1.0（防浮点误差）。全零时回退均匀分布。"""
        total = sum(probs.values())
        if not (total == total) or total <= 0:  # NaN 或全零
            n = len(probs)
            return {k: 1.0 / n for k in probs} if n else {}
        return {k: v / total for k, v in probs.items()}

    @staticmethod
    def _eval_stage(
        breakdown: dict[str, float], total: float, cond: dict[str, Any]
    ) -> bool:
        """阶段条件判定：total_gte 与 keys_gte 同时满足（缺 key 视为不满足）。"""
        if total < float(cond.get("total_gte", 0)):
            return False
        for key, threshold in (cond.get("keys_gte") or {}).items():
            if float(breakdown.get(key, 0.0)) < float(threshold):
                return False
        return True
