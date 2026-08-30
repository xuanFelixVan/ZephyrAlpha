# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.adaptive_threshold
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler (P3-1 接入 count_threshold 模式)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 概率型阈值范围 [0.1, 0.99]；次数型阈值 = max(ewma * factor, static_floor)，static_floor 防止阈值过低掩盖问题；mode 一经设置不可变更（同一 gate_id 模式一致）；history deque maxlen=100 防止内存膨胀
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] observe/observe_count 不抛异常——outcome 非法时返回当前阈值不变（fail-safe）；ewma 空历史返回当前阈值
# [TESTS] tests/governance/rule_enforcement/test_adaptive_threshold.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
自适应阈值——双模式：概率型（PASS/FAIL outcome 调节）+ 次数型（EWMA 基线 × factor）。

P3-0 扩展（#ARCH-PREVENTABILITY-LAYER-001 Phase 3，2026-07-20）:
原仅支持 probability_threshold 模式（0.1-0.99），与 abuse_monitor 的"次数阈值"
模型不匹配。本次扩展新增 count_threshold 模式：基于 7d 滚动基线 EWMA 计算
阈值 = max(ewma * factor, static_floor)，受 static_floor 下限约束防止阈值
过低掩盖问题。两种模式并存，同一 gate_id 模式一经设置不可变更。

设计权衡:
1. **双模式并存而非替换**: 概率型服务于 gate fail/pass 反馈调节，次数型服务于
   abuse monitor 的"24h/7d 计数告警"。两者语义不同，强行合并会引入歧义。
2. **static_floor 强制下限**: 防止 EWMA 基线降到很低后阈值跟随降低，掩盖真实
   恶化。对标 ruling_100pct_ai_governance_hardening.md §5.3 风险"自适应阈值
   掩盖真实恶化 → 缓解：保留静态下限"。
3. **factor 默认 1.5**: 给基线 ×1.5 作为告警阈值，留 50% 余量给正常波动。
   可配置，abuse monitor 5 维可各自设定 factor。
4. **mode 不可变更**: 同一 gate_id 第一次 observe 时确定 mode，后续调用必须
   使用同 mode 的方法，否则 fail-safe 返回当前阈值不变。防止运行中切换模式
   导致 history 混淆（概率值与计数值混在同一 deque）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: window 参数
#   fields: 参数 window（无注解）
#   code: adaptive_threshold.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: smoothing 参数
#   fields: 参数 smoothing（无注解）
#   code: adaptive_threshold.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AdaptiveThreshold
#   name_en: AdaptiveThreshold
#   intro: 双模式自适应阈值管理器。
#   desc: 双模式自适应阈值管理器。 Usage（概率型，向后兼容）:: at = AdaptiveThreshold() at.observe("gate-A", 0.8, "PASS")…；公共方法（定义序）: smoothi…
#   inputs: window smoothing
#   outputs: 返回值
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: main() 源码 L320-L321
#   desc: 源码 L320-L321
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: AdaptiveThreshold, main
#   downstream: zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler (P3-1 接入 count_…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

import logging
from collections import deque
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ThresholdMode(Enum):
    """阈值模式枚举。

    PROBABILITY: 概率型，observe(value, outcome=PASS/FAIL) 调节，范围 [0.1, 0.99]
    COUNT: 次数型，observe_count(daily_count) 计 EWMA 基线，阈值 = max(ewma * factor, static_floor)
    """

    PROBABILITY = "probability"
    COUNT = "count"


@dataclass
class ThresholdState:
    """单 gate_id 的阈值状态。

    history: deque[float]，存储历史观察值（概率型存 PASS/FAIL 0/1，次数型存每日次数）。
        maxlen=100 防止内存膨胀（次数型 7d 滚动 = 7 个值，远小于 100）。
    mode: ThresholdMode，模式一经设置不可变更（由 AdaptiveThreshold 强制）。
    static_floor: 次数型下限，默认 0.0；abuse monitor 设为对应静态阈值（如 warn_only=20）。
    factor: 次数型阈值倍数，默认 1.5（基线 × 1.5 = 告警阈值）。
    """

    gate_id: str
    current_threshold: float
    history: deque = None  # type: ignore[assignment]
    mode: ThresholdMode = ThresholdMode.PROBABILITY
    static_floor: float = 0.0
    factor: float = 1.5

    def __post_init__(self) -> None:
        if self.history is None:
            self.history = deque(maxlen=100)


class AdaptiveThreshold:
    """双模式自适应阈值管理器。

    Usage（概率型，向后兼容）::
        at = AdaptiveThreshold()
        at.observe("gate-A", 0.8, "PASS")  # 概率值 + outcome

    Usage（次数型，P3-0 新增）::
        at = AdaptiveThreshold()
        at.set_count_config("warn_only_24h", static_floor=20.0, factor=1.5)
        at.observe_count("warn_only_24h", 45)  # 今日 45 次
        threshold = at.get_threshold("warn_only_24h")  # max(ewma * 1.5, 20.0)
    """

    DEFAULT_WINDOW = 50
    DEFAULT_SMOOTHING = 0.2
    # 次数型默认配置（可被 set_count_config 覆盖）
    DEFAULT_COUNT_FACTOR = 1.5
    DEFAULT_COUNT_FLOOR = 0.0

    def __init__(self, window: int = DEFAULT_WINDOW, smoothing: float = DEFAULT_SMOOTHING) -> None:
        self._window = window
        self._smoothing = smoothing
        self._states: dict[str, ThresholdState] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def smoothing(self):
        """只读：smoothing（Stage 4 公共化）。"""
        return self._smoothing

    @smoothing.setter
    def smoothing(self, value):
        """写入：smoothing（Stage 4 公共化）。"""
        self._smoothing = value

    @property
    def states(self) -> dict[str, ThresholdState]:
        """只读：states（Stage 4 公共化）。"""
        return self._states

    @states.setter
    def states(self, value):
        """写入：states（Stage 4 公共化）。"""
        self._states = value

    @property
    def window(self):
        """只读：window（Stage 4 公共化）。"""
        return self._window

    @window.setter
    def window(self, value):
        """写入：window（Stage 4 公共化）。"""
        self._window = value

    def get_state(
        self,
        gate_id: str,
        initial: float = 0.8,
        mode: ThresholdMode = ThresholdMode.PROBABILITY,
    ) -> ThresholdState:
        """获取或创建 gate_id 的状态。

        首次创建时确定 mode，后续调用若 mode 与已存 mode 不一致则返回已存状态
        （fail-safe，不抛异常）。这是"mode 不可变更"约束的实现点。
        """
        if gate_id not in self._states:
            self._states[gate_id] = ThresholdState(
                gate_id=gate_id,
                current_threshold=initial,
                mode=mode,
            )
        return self._states[gate_id]

    def set_count_config(self, gate_id: str, static_floor: float, factor: float) -> None:
        """配置次数型阈值参数（必须在 observe_count 前调用）。

        若 gate_id 已存在且 mode != COUNT，fail-safe 忽略配置（mode 不可变更）。
        若 gate_id 不存在，创建 COUNT 模式状态。
        """
        if gate_id in self._states:
            state = self._states[gate_id]
            if state.mode != ThresholdMode.COUNT:
                logger.warning(
                    "set_count_config ignored for %s: mode=%s (expected COUNT, mode 不可变更)",
                    gate_id,
                    state.mode,
                )
                return
        else:
            self._states[gate_id] = ThresholdState(
                gate_id=gate_id,
                current_threshold=static_floor,  # 初始为 static_floor
                mode=ThresholdMode.COUNT,
                static_floor=static_floor,
                factor=factor,
            )
            return
        # 已存在 COUNT 模式，更新配置
        state.static_floor = static_floor
        state.factor = factor
        # 重算 current_threshold（用现有 history）
        ewma_val = self.ewma(gate_id)
        state.current_threshold = max(ewma_val * factor, static_floor)

    def observe(self, gate_id: str, value: float, outcome: str) -> float:
        """概率型观察（向后兼容原 API）。

        若 gate_id 已是 COUNT 模式，fail-safe 返回当前阈值不变（mode 不可变更）。
        """
        state = self.get_state(gate_id)
        if state.mode == ThresholdMode.COUNT:
            logger.warning(
                "observe (probability) ignored for %s: mode=COUNT (use observe_count instead)",
                gate_id,
            )
            return state.current_threshold
        state.history.append(value)

        if outcome == "PASS":
            direction = -self._smoothing
        elif outcome == "FAIL":
            direction = self._smoothing
        else:
            return state.current_threshold

        state.current_threshold = max(
            0.1, min(0.99, state.current_threshold + direction * (1.0 - state.current_threshold))
        )
        logger.debug("threshold %s adjusted: %.4f (outcome=%s)", gate_id, state.current_threshold, outcome)
        return state.current_threshold

    def observe_count(self, gate_id: str, daily_count: float) -> float:
        """次数型观察：记录今日次数，更新 EWMA 基线，重算阈值。

        阈值 = max(ewma(history) * factor, static_floor)
        - ewma 给近期数据更高权重，适应趋势变化
        - static_floor 防止阈值降到很低后掩盖真实恶化

        若 gate_id 已是 PROBABILITY 模式，fail-safe 返回当前阈值不变。
        """
        # 确保 state 存在（首次调用时创建 COUNT 模式，用 DEFAULT 配置）
        if gate_id not in self._states:
            self._states[gate_id] = ThresholdState(
                gate_id=gate_id,
                current_threshold=self.DEFAULT_COUNT_FLOOR,
                mode=ThresholdMode.COUNT,
                static_floor=self.DEFAULT_COUNT_FLOOR,
                factor=self.DEFAULT_COUNT_FACTOR,
            )
        state = self._states[gate_id]
        if state.mode != ThresholdMode.COUNT:
            logger.warning(
                "observe_count ignored for %s: mode=%s (use observe instead)",
                gate_id,
                state.mode,
            )
            return state.current_threshold
        state.history.append(daily_count)

        ewma_val = self.ewma(gate_id)
        state.current_threshold = max(ewma_val * state.factor, state.static_floor)
        logger.debug(
            "count threshold %s adjusted: %.2f (ewma=%.2f, factor=%.2f, floor=%.2f, count=%.0f)",
            gate_id,
            state.current_threshold,
            ewma_val,
            state.factor,
            state.static_floor,
            daily_count,
        )
        return state.current_threshold

    def get_threshold(self, gate_id: str) -> float:
        """获取当前阈值（两种模式通用）。"""
        state = self.get_state(gate_id)
        return state.current_threshold

    def ewma(self, gate_id: str) -> float:
        """计算 EWMA 加权移动平均。

        空历史返回当前阈值（fail-safe，避免除零）。
        alpha = 2 / (min(len, window) + 1)，window 默认 50。
        """
        state = self.get_state(gate_id)
        if not state.history:
            return state.current_threshold
        alpha = 2.0 / (min(len(state.history), self._window) + 1)
        ewma_val = state.history[0]
        for v in list(state.history)[1:]:
            ewma_val = alpha * v + (1 - alpha) * ewma_val
        return ewma_val


__all__ = ["AdaptiveThreshold", "ThresholdState", "ThresholdMode"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
