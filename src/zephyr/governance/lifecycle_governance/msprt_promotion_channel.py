# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.msprt_promotion_channel
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.pf_core.core.msprt_champion_challenger（MOD-PF-008 统计内核，仅消费不改）; zephyr.shared.foundation.errors（仅错误基类）
# [CONSUMERS] zephyr.governance.lifecycle_governance.factor_promotion_wiring（因子晋升场景）; 调用方（BM-MT-02 晋升调度，64 号 §6.4 调度基座装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 通道须预注册（SR 26-02 并行期开始前文档化纪律），未注册拒喂;状态机 PENDING→OBSERVING→PROMOTED/ELIMINATED 单向推进无回退;终局判定后内核冻结（重复投喂零副作用，裁决快照不变）;序贯早停语义=feed_batch 达终局即截断;统计判定逻辑不在本层重实现（内核唯一真源）
# [MODIFY-GUARD] 61_lifecycle_multi_ai.md §3.3 纪律 1; docs/03_modules/_domain_portfolio_core/msprt_champion_challenger/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PromotionChannelError(ZA-GV-0053);ValueError(内核参数非法由 MOD-PF-008 契约原样上抛，不包装不吞噬)
# [TESTS] tests/governance/lifecycle/test_msprt_promotion_channel.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: (champion_id, challenger_id) 通道预注册 + 内核配置（alpha/tau/historical_effects/window_size）
# I2: 逐笔 delta（challenger_pnl − champion_pnl，调用方/DeltaExtractor 契约计算）/ 批量 delta 序列
# F1: register 预注册建通道（重复/空 ID/自配对拒）
# F2: feed 单笔推进（内核 update → 决策映射状态机；终局后幂等短路）
# F3: feed_batch 批量调度入口（达终局早停；空批返回当前快照）
# O1: PromotionVerdict（state/decision/n/m_value/log_m——晋升/留观/回退三态裁决输出）
# [/ALGO_FLOW]
"""
D_GOVERNANCE — mSPRT Champion-Challenger 晋升编排层（61 号 §3.3 纪律 1 通道化）。

包装 MOD-PF-008 统计内核（``MSPRTChampionChallenger``）为可调度晋升通道：
内核管"统计判定"（e-process 累加 + Ville 边界 + 满窗最小样本门），本层管
"通道生命周期"（预注册 → 逐笔投喂 → 状态机推进 → 终局冻结），职责分离。

通道状态机（单向推进，无回退）：
  PENDING（已登记未投喂）→ OBSERVING（留观中，内核 RETAIN_CHAMPION）
  → PROMOTED（终局：PROMOTE_CHALLENGER，challenger 晋升）
  → ELIMINATED（终局：ELIMINATE_CHALLENGER，challenger 回退淘汰，champion 留任——
    memo"默认动作：证据不足时保留 Champion"）。

预注册纪律（SR 26-02）：并行验证期开始前通道须显式 register（效应量/显著性/停止规则
文档化的工程承载）；未注册配对拒喂。终局幂等：PROMOTED/ELIMINATED 后内核冻结，
重复投喂/重放返回同一裁决快照零副作用（调度器重试安全）。

载体留痕：memo 以 MLflow alias（@champion/@challenger）为晋升载体，51 号已裁定
卸载 MLflow——本层只输出裁决（PromotionVerdict），alias 切换/状态落盘由消费方
承载（已落地消费方：factor_promotion_wiring 因子灰度晋升场景）。

依据: 61_lifecycle_multi_ai §3.3 纪律 1（mSPRT 施工伪代码 + 施工要点）+ 结案报告（载体重裁定留痕）
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: alpha 参数
#   fields: 参数 alpha（无注解）
#   code: msprt_promotion_channel.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: tau 参数
#   fields: 参数 tau（无注解）
#   code: msprt_promotion_channel.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: historical_effects 参数
#   fields: 参数 historical_effects（无注解）
#   code: msprt_promotion_channel.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: window_size 参数
#   fields: 参数 window_size（无注解）
#   code: msprt_promotion_channel.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PromotionChannelManager
#   name_en: PromotionChannelManager
#   intro: mSPRT 晋升通道管理器（多通道登记 + 可调度投喂入口）。
#   desc: mSPRT 晋升通道管理器（多通道登记 + 可调度投喂入口）。 用法：调度器（64 号 §6.4 基座）对每个 champion/challenger 配对 register 一…；公共方法（定义序）: registe…
#   inputs: alpha tau historical_effects window_size
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: PromotionChannelManager
#   downstream: zephyr.governance.lifecycle_governance.factor_promotion_wiring（因子晋升场景）; 调用方（BM-…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Iterable, Sequence

from zephyr.pf_core.core.msprt_champion_challenger import (
    ChampionChallengerDecision,
    MSPRTChampionChallenger,
)
from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)


class PromotionChannelError(ZephyrBaseError):
    """晋升通道非法操作（重复注册 / 空 ID / 自配对 / 未注册投喂 / delta 非法）。"""

    error_code = "ZA-GV-0053"


class PromotionState(str, Enum):
    """通道状态机四态（单向推进）。"""

    PENDING = "PENDING"  # 已登记未投喂
    OBSERVING = "OBSERVING"  # 留观中（证据不足，默认保留 Champion）
    PROMOTED = "PROMOTED"  # 终局：challenger 晋升
    ELIMINATED = "ELIMINATED"  # 终局：challenger 回退淘汰，champion 留任

    @property
    def is_terminal(self) -> bool:
        """PROMOTED/ELIMINATED 为终局（序贯实验停止，内核冻结）。"""
        return self in (PromotionState.PROMOTED, PromotionState.ELIMINATED)


@dataclass(frozen=True)
class PromotionVerdict:
    """晋升裁决输出（通道快照；晋升/留观/回退三态 + 统计证据留痕）。

    decision: 内核三态判定（PENDING 时尚未投喂为 None）。
    n/m_value/log_m: 终局或当前 e-process 证据（审计追溯用）。
    """

    champion_id: str
    challenger_id: str
    state: PromotionState
    decision: ChampionChallengerDecision | None
    n: int
    m_value: float
    log_m: float


@dataclass
class _Channel:
    """单通道内部状态（内核实例 + 当前裁决快照）。"""

    kernel: MSPRTChampionChallenger
    verdict: PromotionVerdict


class PromotionChannelManager:
    """mSPRT 晋升通道管理器（多通道登记 + 可调度投喂入口）。

    用法：调度器（64 号 §6.4 基座）对每个 champion/challenger 配对 register 一次
    （预注册纪律），随后按交易节奏 feed 单笔或盘后 feed_batch 批量推进；
    达终局（PROMOTED/ELIMINATED）即该轮序贯实验停止，裁决交消费方执行
    （晋升/回滚载体切换），内核冻结待新挑战者重新注册。

    内核配置（alpha/tau/historical_effects/window_size）对全部通道统一生效；
    参数非法由内核 ValueError 契约在 register 时原样上抛。
    """

    def __init__(
        self,
        *,
        alpha: float = 0.05,
        tau: float | None = None,
        historical_effects: Sequence[float] | None = None,
        window_size: int = 30,
    ) -> None:
        self._kernel_kwargs = {
            "alpha": alpha,
            "tau": tau,
            "historical_effects": historical_effects,
            "window_size": window_size,
        }
        self._channels: dict[tuple[str, str], _Channel] = {}

    def register(self, champion_id: str, challenger_id: str) -> None:
        """预注册晋升通道（SR 26-02：并行期开始前文档化）；重复/空 ID/自配对拒。

        Raises:
            PromotionChannelError: 配对非法或已注册。
            ValueError: 内核参数非法（MOD-PF-008 契约原样上抛）。
        """
        if not champion_id or not champion_id.strip() or not challenger_id or not challenger_id.strip():
            raise PromotionChannelError("champion_id/challenger_id 不能为空")
        if champion_id == challenger_id:
            raise PromotionChannelError(f"自配对无意义（champion == challenger）: {champion_id!r}")
        key = (champion_id, challenger_id)
        if key in self._channels:
            raise PromotionChannelError(
                f"通道已注册（重复注册拒；新挑战者须待终局后另起配对）: {key}",
                details={"champion_id": champion_id, "challenger_id": challenger_id},
            )
        kernel = MSPRTChampionChallenger(**self._kernel_kwargs)
        self._channels[key] = _Channel(
            kernel=kernel,
            verdict=PromotionVerdict(
                champion_id=champion_id,
                challenger_id=challenger_id,
                state=PromotionState.PENDING,
                decision=None,
                n=0,
                m_value=1.0,
                log_m=0.0,
            ),
        )
        logger.info("晋升通道注册: champion=%s challenger=%s", champion_id, challenger_id)

    def pairs(self) -> tuple[tuple[str, str], ...]:
        """全部已注册配对（调度器枚举入口）。"""
        return tuple(self._channels)

    def verdict(self, champion_id: str, challenger_id: str) -> PromotionVerdict:
        """当前裁决快照（未注册 → PromotionChannelError）。"""
        return self._channel(champion_id, challenger_id).verdict

    def feed(self, champion_id: str, challenger_id: str, delta: float) -> PromotionVerdict:
        """单笔推进：内核 update → 决策映射状态机；终局后幂等短路（零副作用）。

        Raises:
            PromotionChannelError: 未注册 / delta 非有限数值。
        """
        channel = self._channel(champion_id, challenger_id)
        if channel.verdict.state.is_terminal:
            return channel.verdict  # 终局冻结：重复投喂幂等重入
        delta = float(delta)
        if math.isnan(delta) or math.isinf(delta):
            raise PromotionChannelError(f"delta 须为有限数值: {delta}")
        step = channel.kernel.update(delta)
        state = self._advance(channel.verdict.state, step.decision)
        verdict = PromotionVerdict(
            champion_id=champion_id,
            challenger_id=challenger_id,
            state=state,
            decision=step.decision,
            n=step.n,
            m_value=step.m,
            log_m=step.log_m,
        )
        channel.verdict = verdict
        if state.is_terminal:
            logger.warning(
                "晋升通道终局 %s vs %s: %s（n=%d, M=%.3f）",
                champion_id,
                challenger_id,
                state.value,
                step.n,
                step.m,
            )
        return verdict

    def feed_batch(self, champion_id: str, challenger_id: str, deltas: Iterable[float]) -> PromotionVerdict:
        """批量调度入口：逐笔投喂，达终局早停（序贯检验语义）；空批返回当前快照。"""
        self._channel(champion_id, challenger_id)  # 未注册 fail-fast
        verdict = self.verdict(champion_id, challenger_id)
        for delta in deltas:
            verdict = self.feed(champion_id, challenger_id, delta)
            if verdict.state.is_terminal:
                break
        return verdict

    # ── 内部 ──

    def _channel(self, champion_id: str, challenger_id: str) -> _Channel:
        key = (champion_id, challenger_id)
        channel = self._channels.get(key)
        if channel is None:
            raise PromotionChannelError(
                f"通道未预注册（SR 26-02 并行期开始前文档化纪律）: {key}",
                details={"champion_id": champion_id, "challenger_id": challenger_id},
            )
        return channel

    @staticmethod
    def _advance(current: PromotionState, decision: ChampionChallengerDecision) -> PromotionState:
        """内核决策 → 通道状态映射（单向推进的唯一映射点）。"""
        if decision is ChampionChallengerDecision.PROMOTE_CHALLENGER:
            return PromotionState.PROMOTED
        if decision is ChampionChallengerDecision.ELIMINATE_CHALLENGER:
            return PromotionState.ELIMINATED
        return PromotionState.OBSERVING  # RETAIN_CHAMPION：留观（current 必为 PENDING/OBSERVING）


__all__: Final = [
    "PromotionChannelError",
    "PromotionChannelManager",
    "PromotionState",
    "PromotionVerdict",
]
