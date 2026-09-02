# [BLUEPRINT] MOD-PF-009 | docs/03_modules/_domain_portfolio_core/strategy_factory/blueprint.md
# [MODULE] zephyr.pf_core.core.strategy_factory
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（策略候选注册/监控接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 10阶段机 DRAFT→HYPOTHESIS→GENERATION→VALIDATION→GATE_REVIEW→PHACKING_REVIEW→HUMAN_ADJUDICATION→REGISTRATION→MONITORING→RETIREMENT；REJECTED/RETIREMENT终态；gate未过/p-hacking不达标(dsr≤0或pbo>pbo_max)→REJECTED；人工裁决approved_by非空(严禁全自动)；注册条目status恒candidate；记录frozen；非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] StrategyFactoryError
# [TESTS] tests/pf_core/test_strategy_factory.py
# [A_module] module_id=MOD-PF-009 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""Strategy Factory — C-006 策略工厂 (MOD-PF-009, CAND-PF004-002, B1-00189)

策略全生命周期工厂：10 阶段状态机 + 策略注册表 + 自动发现四通道
（GP/SR/LLM/FactorMAD）发现钩子。产出必经 C-003 三重门禁（gate_verdict 注入）
+ p-hacking 评估（dsr/pbo 注入，确定性判定）+ 人工裁决（approved_by 必填），
**严禁全自动上线**——注册条目 status 恒 candidate，本件无 auto-approve 路径。

与既有件分工（蓝图 §0 查重裁定，R2 在案）：factor_factory=因子族 9 阶段厂；
signal_factory=信号族厂；strategy_book=持仓域账本；strategy_engine=运行时执行面；
strategy_cpcv_matrix=离线打分（门禁结论真源之一）。本件=策略族工厂编排核心。

纪律：纯内存实现无 IO；门禁/p-hacking 指标由调用方注入（不跑回测、不越域取数）；
GP/SR/LLM/FactorMAD 生成器以 discovery_hook 注入（本件不内建实现）。

依据: blueprint.md（MOD-PF-009）§1 规则
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略草案
#   fields: name 非空 + DiscoveryChannel 四通道 + hypothesis
#   code: intake() 参数
# - id: I2
#   name: 门禁/p-hacking/人工证据
#   fields: gate_verdict bool; dsr/pbo 有限值; approved_by 非空
#   code: submit_gate_verdict/submit_phacking_metrics/human_adjudicate 参数
# 层: 算法
# - id: A1
#   name_zh: ① 阶段机推进（Fail-Closed）
#   name_en: _transition
#   intro: 严格顺序迁移表；REJECTED/RETIREMENT 终态拒绝再迁移
# - id: A2
#   name_zh: ② 三重门禁+p-hacking+人工三级闸门
#   name_en: submit_*/human_adjudicate
#   intro: gate False→REJECTED; dsr≤0或pbo>pbo_max→REJECTED; approved_by空→抛错
# - id: A3
#   name_zh: ③ 注册条目签发
#   name_en: register
#   intro: 仅 REGISTRATION 阶段可签发；status 恒 candidate
# 层: 输出
# - id: O1
#   name: StrategyRecord / StrategyRegistryEntry
#   fields: frozen 记录（stage/channel/history/metrics）+ candidate 注册条目
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "DiscoveryChannel",
    "StageTransition",
    "StrategyFactory",
    "StrategyFactoryError",
    "StrategyRecord",
    "StrategyRegistryEntry",
    "StrategyStage",
]


class StrategyFactoryError(ZephyrBaseError):
    """策略工厂操作非法（Fail-Closed）。

    错误码：ZA-PF-0081（2026-08-26 对账批转正）。
    """

    error_code = "ZA-PF-0081"


class DiscoveryChannel(str, Enum):
    """自动发现四通道。"""

    GP = "GP"  # 遗传规划
    SR = "SR"  # 符号回归
    LLM = "LLM"  # 大模型生成
    FACTOR_MAD = "FACTOR_MAD"  # 因子 MAD 投票挖掘（上游 factor_factory 通道）


class StrategyStage(str, Enum):
    """策略 10 阶段生命周期（+ REJECTED 终态）。"""

    DRAFT = "DRAFT"
    HYPOTHESIS = "HYPOTHESIS"
    GENERATION = "GENERATION"
    VALIDATION = "VALIDATION"
    GATE_REVIEW = "GATE_REVIEW"
    PHACKING_REVIEW = "PHACKING_REVIEW"
    HUMAN_ADJUDICATION = "HUMAN_ADJUDICATION"
    REGISTRATION = "REGISTRATION"
    MONITORING = "MONITORING"
    RETIREMENT = "RETIREMENT"
    REJECTED = "REJECTED"


# 顺序主链；GATE_REVIEW→PHACKING_REVIEW 须经 submit_gate_verdict，
# PHACKING_REVIEW→HUMAN_ADJUDICATION 须经 submit_phacking_metrics，
# HUMAN_ADJUDICATION→REGISTRATION 须经 human_adjudicate（见 _GATED_STAGES）。
_CHAIN: Final[tuple[StrategyStage, ...]] = (
    StrategyStage.DRAFT,
    StrategyStage.HYPOTHESIS,
    StrategyStage.GENERATION,
    StrategyStage.VALIDATION,
    StrategyStage.GATE_REVIEW,
    StrategyStage.PHACKING_REVIEW,
    StrategyStage.HUMAN_ADJUDICATION,
    StrategyStage.REGISTRATION,
    StrategyStage.MONITORING,
    StrategyStage.RETIREMENT,
)
_GATED_STAGES: Final[frozenset[StrategyStage]] = frozenset(
    {StrategyStage.GATE_REVIEW, StrategyStage.PHACKING_REVIEW, StrategyStage.HUMAN_ADJUDICATION}
)
_TERMINAL: Final[frozenset[StrategyStage]] = frozenset({StrategyStage.REJECTED, StrategyStage.RETIREMENT})


@dataclass(frozen=True)
class StageTransition:
    """一次阶段迁移留痕（frozen）。"""

    from_stage: StrategyStage | None
    to_stage: StrategyStage
    note: str
    occurred_at: datetime


@dataclass(frozen=True)
class StrategyRecord:
    """策略记录（frozen）。"""

    strategy_id: str
    name: str
    channel: DiscoveryChannel
    stage: StrategyStage
    hypothesis: str = ""
    gate_detail: str = ""
    dsr: float | None = None
    pbo: float | None = None
    approved_by: str = ""
    history: tuple[StageTransition, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StrategyRegistryEntry:
    """策略注册条目（frozen；status 恒 candidate——严禁全自动上线）。"""

    strategy_id: str
    name: str
    channel: DiscoveryChannel
    approved_by: str
    status: str
    registered_at: datetime


def _require_text(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StrategyFactoryError(f"{name} 不能为空字符串")
    return value


def _require_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise StrategyFactoryError(f"{name} 必须为有限值: {value}")
    return v


class StrategyFactory:
    """策略工厂（10 阶段状态机 + 三级闸门 + 注册表）。

    Args:
        pbo_max: p-hacking 过拟合概率上限（默认 0.5，超出→REJECTED）
        clock: 时间源（测试注入）
    """

    def __init__(self, pbo_max: float = 0.5, clock: Callable[[], datetime] | None = None) -> None:
        pbo_max = _require_finite("pbo_max", pbo_max)
        if not 0.0 < pbo_max < 1.0:
            raise StrategyFactoryError(f"pbo_max 必须 ∈(0,1): {pbo_max}")
        self._pbo_max = pbo_max
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._records: dict[str, StrategyRecord] = {}
        self._seq = 0
        self._hooks: dict[DiscoveryChannel, Callable[[str], StrategyRecord]] = {}

    # ── 发现与登记 ──

    def intake(self, name: str, channel: DiscoveryChannel, hypothesis: str = "") -> StrategyRecord:
        """登记策略草案（DRAFT）。channel 必须为四通道之一。"""
        name = _require_text("name", name)
        if not isinstance(channel, DiscoveryChannel):
            raise StrategyFactoryError(f"channel 必须为 DiscoveryChannel: {channel!r}")
        self._seq += 1
        sid = f"SF-{self._seq:06d}"
        rec = StrategyRecord(
            strategy_id=sid,
            name=name,
            channel=channel,
            stage=StrategyStage.DRAFT,
            hypothesis=hypothesis,
            history=(StageTransition(None, StrategyStage.DRAFT, "intake", self._clock()),),
        )
        self._records[sid] = rec
        return rec

    def register_discovery_hook(self, channel: DiscoveryChannel, hook: Callable[[str], StrategyRecord]) -> None:
        """注册通道发现钩子（GP/SR/LLM/FactorMAD 生成器注入位）。"""
        if not isinstance(channel, DiscoveryChannel):
            raise StrategyFactoryError(f"channel 必须为 DiscoveryChannel: {channel!r}")
        if not callable(hook):
            raise StrategyFactoryError("hook 必须可调用")
        self._hooks[channel] = hook

    def discover(self, channel: DiscoveryChannel, name: str) -> StrategyRecord:
        """经通道钩子发现候选（钩子只产 DRAFT）。"""
        name = _require_text("name", name)
        hook = self._hooks.get(channel)
        if hook is None:
            raise StrategyFactoryError(f"通道 {channel.value} 未注册发现钩子")
        rec = hook(name)
        if not isinstance(rec, StrategyRecord) or rec.stage is not StrategyStage.DRAFT:
            raise StrategyFactoryError("发现钩子必须返回 DRAFT 阶段 StrategyRecord")
        return rec

    # ── 阶段推进 ──

    def advance(self, strategy_id: str, to_stage: StrategyStage, note: str = "") -> StrategyRecord:
        """顺序推进阶段（闸门阶段的跨越须经对应 submit_* 方法）。"""
        rec = self.get(strategy_id)
        if not isinstance(to_stage, StrategyStage):
            raise StrategyFactoryError(f"to_stage 必须为 StrategyStage: {to_stage!r}")
        if rec.stage in _TERMINAL:
            raise StrategyFactoryError(f"终态不可再迁移: {rec.stage.value}")
        if to_stage in (StrategyStage.REJECTED, StrategyStage.DRAFT):
            raise StrategyFactoryError(f"advance 不可直达 {to_stage.value}")
        if to_stage is StrategyStage.RETIREMENT:
            return self._move(rec, StrategyStage.RETIREMENT, note or "retire")
        try:
            cur_idx = _CHAIN.index(rec.stage)
            to_idx = _CHAIN.index(to_stage)
        except ValueError:
            raise StrategyFactoryError(f"未知阶段: {to_stage!r}") from None
        if to_idx != cur_idx + 1:
            raise StrategyFactoryError(f"非法阶段迁移: {rec.stage.value}→{to_stage.value}（仅顺序单步）")
        if rec.stage in _GATED_STAGES:
            raise StrategyFactoryError(f"{rec.stage.value} 为闸门阶段，须经对应 submit_*/human_adjudicate 推进")
        return self._move(rec, to_stage, note)

    def submit_gate_verdict(self, strategy_id: str, passed: bool, detail: str = "") -> StrategyRecord:
        """C-003 三重门禁结论（GATE_REVIEW→PHACKING_REVIEW / REJECTED）。"""
        rec = self.get(strategy_id)
        self._require_stage(rec, StrategyStage.GATE_REVIEW)
        rec = replace(rec, gate_detail=detail)
        self._records[rec.strategy_id] = rec
        if not passed:
            return self._move(rec, StrategyStage.REJECTED, f"三重门禁未过: {detail}")
        return self._move(rec, StrategyStage.PHACKING_REVIEW, f"三重门禁通过: {detail}")

    def submit_phacking_metrics(self, strategy_id: str, dsr: float, pbo: float) -> StrategyRecord:
        """p-hacking 评估（dsr>0 且 pbo≤pbo_max → HUMAN_ADJUDICATION，否则 REJECTED）。"""
        rec = self.get(strategy_id)
        self._require_stage(rec, StrategyStage.PHACKING_REVIEW)
        dsr = _require_finite("dsr", dsr)
        pbo = _require_finite("pbo", pbo)
        rec = replace(rec, dsr=dsr, pbo=pbo)
        self._records[rec.strategy_id] = rec
        if dsr <= 0 or pbo > self._pbo_max:
            return self._move(rec, StrategyStage.REJECTED, f"p-hacking 不达标: dsr={dsr:.4f}, pbo={pbo:.4f}")
        return self._move(rec, StrategyStage.HUMAN_ADJUDICATION, f"p-hacking 通过: dsr={dsr:.4f}, pbo={pbo:.4f}")

    def human_adjudicate(self, strategy_id: str, approved: bool, approved_by: str, note: str = "") -> StrategyRecord:
        """人工裁决（approved_by 必填——严禁全自动上线）。"""
        rec = self.get(strategy_id)
        self._require_stage(rec, StrategyStage.HUMAN_ADJUDICATION)
        approved_by = _require_text("approved_by（人工裁决，严禁全自动）", approved_by)
        rec = replace(rec, approved_by=approved_by)
        self._records[rec.strategy_id] = rec
        if not approved:
            return self._move(rec, StrategyStage.REJECTED, f"人工否决({approved_by}): {note}")
        return self._move(rec, StrategyStage.REGISTRATION, f"人工批准({approved_by}): {note}")

    def register(self, strategy_id: str) -> StrategyRegistryEntry:
        """签发注册条目（仅 REGISTRATION 阶段；status 恒 candidate）。"""
        rec = self.get(strategy_id)
        self._require_stage(rec, StrategyStage.REGISTRATION)
        return StrategyRegistryEntry(
            strategy_id=rec.strategy_id,
            name=rec.name,
            channel=rec.channel,
            approved_by=rec.approved_by,
            status="candidate",
            registered_at=self._clock(),
        )

    def retire(self, strategy_id: str, reason: str) -> StrategyRecord:
        """退役（RETIREMENT 终态）。"""
        reason = _require_text("reason", reason)
        rec = self.get(strategy_id)
        if rec.stage in _TERMINAL:
            raise StrategyFactoryError(f"终态不可再迁移: {rec.stage.value}")
        return self._move(rec, StrategyStage.RETIREMENT, reason)

    # ── 查询 ──

    def get(self, strategy_id: str) -> StrategyRecord:
        strategy_id = _require_text("strategy_id", strategy_id)
        try:
            return self._records[strategy_id]
        except KeyError:
            raise StrategyFactoryError(f"未知策略: {strategy_id}") from None

    def list_strategies(self, stage: StrategyStage | None = None) -> list[StrategyRecord]:
        recs = list(self._records.values())
        if stage is not None:
            recs = [r for r in recs if r.stage is stage]
        return recs

    # ── 内部 ──

    @staticmethod
    def _require_stage(rec: StrategyRecord, stage: StrategyStage) -> None:
        if rec.stage is not stage:
            raise StrategyFactoryError(f"当前阶段 {rec.stage.value} 不支持该操作（要求 {stage.value}）")

    def _move(self, rec: StrategyRecord, to: StrategyStage, note: str) -> StrategyRecord:
        rec = replace(
            rec,
            stage=to,
            history=rec.history + (StageTransition(rec.stage, to, note, self._clock()),),
        )
        self._records[rec.strategy_id] = rec
        return rec
