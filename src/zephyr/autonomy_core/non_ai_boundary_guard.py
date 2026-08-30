# [BLUEPRINT] MOD-AU-012 | docs/03_modules/_domain_autonomy_core/non_ai_boundary_guard/blueprint.md
# [MODULE] zephyr.autonomy_core.non_ai_boundary_guard
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（决策流接入 / 风控执行闸阻断执行体 / D_GOV_AUDIT 决策溯源落账）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] meter/admit 判定纯函数无IO; 决策记录与阈值非法 Fail-Closed; 非AI决策恒 ALLOW; AI占比严格大于 max_ai_share 且样本达标才 BLOCK_NEW_AI; 阻断仅产 block_trigger 信号（执行委托风控/执行闸，本模块不直接阻断下单）; 回调/sink 异常不阻断判定; 计量快照与阻断信号双审计记录
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/non_ai_boundary_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidDecisionRecordError; InvalidBoundaryConfigError
# [TESTS] tests/autonomy/test_non_ai_boundary_guard.py
# [A_module] module_id=MOD-AU-012 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""



NonAIBoundaryGuard — Non-AI 边界守卫 (MOD-AU-012)

B10-02362 / D-AUTONOMY-33（AUD-DRAFT-001-DIGEST P1 波 W-P1-12，§30.5.2）：
AI/非AI**决策权重占比计量器** + 超限（默认 >30%）阻断信号——guardrails 思路的
门禁化实现，守护非AI（人工/确定性规则）决策权重不被 AI 决策稀释越界。

查重分工（W-P1-12 探查结论，均不复制）：
- a2a_check_gateway（MOD-INF-025）：跨 Agent 通信三段检查（身份/能力/边界）；
- per_agent_gate（MOD-AU-006）：单 Agent 规则集（动作黑白名单/限额/时段）；
- autonomy_boundary_gate（MOD-AU-001）：写操作三区（ai_modifiable/human_gated/
  immutable_core）运行时拦截；
- autonomy_level_registry（MOD-AU-005）：Agent 四级自治级别裁定；
- ai_agent_monitor（MOD-RK-14）：Agent 行为异常风险分（涌现/轨迹/指纹）；
- autonomy_guard（MOD-INF-039）：Owner 缺位分级自治降级（本守卫计量结论可挂
  其动作面，装配批接线）。
本模块唯一缺口 = 决策流的 **AI/非AI 权重占比计量与超限阻断信号**。
决策溯源落账委托 D_GOV_AUDIT（audit_sink 回调，不 import 不复制）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: thresholds 参数
#   fields: 参数 thresholds（无注解）
#   code: non_ai_boundary_guard.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: block_trigger 参数
#   fields: 参数 block_trigger（无注解）
#   code: non_ai_boundary_guard.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: non_ai_boundary_guard.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① NonAIBoundaryGuard
#   name_en: NonAIBoundaryGuard
#   intro: AI/非AI 决策权重边界守卫（判定纯函数 + 信号回调委托）。
#   desc: AI/非AI 决策权重边界守卫（判定纯函数 + 信号回调委托）。 Args: thresholds: 边界阈值（None 用默认：>30% 硬顶 / 窗口 200 / 最小样本…；公共方法（定义序）: threshol…
#   inputs: thresholds block_trigger audit_sink
#   outputs: 返回值
#   （注：A1 之后另有 8 个公共定义未列入（含 8 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: NonAIBoundaryGuard
#   downstream: 运行时装配批（决策流接入 / 风控执行闸阻断执行体 / D_GOV_AUDIT 决策溯源落账）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "BoundaryAction",
    "BoundarySnapshot",
    "BoundaryThresholds",
    "BoundaryVerdict",
    "DecisionOrigin",
    "DecisionRecord",
    "InvalidBoundaryConfigError",
    "InvalidDecisionRecordError",
    "NonAIBoundaryGuard",
]

#: D-AUTONOMY-33 §30.5.2：AI 决策权重占比硬顶（严格大于即阻断新 AI 决策）
_DEFAULT_MAX_AI_SHARE: Final[float] = 0.30
_DEFAULT_WINDOW_SIZE: Final[int] = 200
_DEFAULT_MIN_SAMPLES: Final[int] = 20


class InvalidDecisionRecordError(ZephyrBaseError):
    """决策记录非法（Fail-Closed：脏输入不参与计量/判定）。"""


class InvalidBoundaryConfigError(ZephyrBaseError):
    """边界守卫阈值配置非法。"""


class DecisionOrigin(str, Enum):
    """决策来源。"""

    AI = "ai"
    NON_AI = "non_ai"


class BoundaryVerdict(str, Enum):
    """边界判定。"""

    ALLOW = "allow"  # 占比未越界 / 样本不足观察期 / 非AI决策
    BLOCK_NEW_AI = "block_new_ai"  # AI 权重占比超限，阻断新 AI 决策（信号）


@dataclass(frozen=True)
class DecisionRecord:
    """单条决策记录（装配层注入；weight 为该决策的权重份额，正数）。"""

    decision_id: str
    origin: DecisionOrigin
    weight: float


@dataclass(frozen=True)
class BoundaryThresholds:
    """边界阈值（frozen；非法即 InvalidBoundaryConfigError）。"""

    max_ai_share: float = _DEFAULT_MAX_AI_SHARE
    window_size: int = _DEFAULT_WINDOW_SIZE
    min_samples: int = _DEFAULT_MIN_SAMPLES

    def __post_init__(self) -> None:
        if not (0.0 < float(self.max_ai_share) < 1.0):
            raise InvalidBoundaryConfigError(
                "max_ai_share 必须落在 (0,1)",
                details={"max_ai_share": self.max_ai_share},
            )
        if int(self.window_size) < 1:
            raise InvalidBoundaryConfigError("window_size 必须 >= 1", details={"window_size": self.window_size})
        if int(self.min_samples) < 1 or int(self.min_samples) > int(self.window_size):
            raise InvalidBoundaryConfigError(
                "min_samples 必须落在 [1, window_size]",
                details={"min_samples": self.min_samples, "window_size": self.window_size},
            )


@dataclass(frozen=True)
class BoundarySnapshot:
    """一次计量快照（frozen；reason 结构化留痕供审计归因）。"""

    samples: int
    total_weight: float
    ai_weight: float
    ai_share: float
    verdict: BoundaryVerdict
    reason: str


@dataclass(frozen=True)
class BoundaryAction:
    """admit 判定结果（frozen；含快照/信号达成标记/审计记录）。"""

    verdict: BoundaryVerdict
    snapshot: BoundarySnapshot
    block_signaled: bool
    audit_records: tuple[dict[str, Any], ...]


def _validate_record(record: DecisionRecord) -> DecisionOrigin:
    """决策记录 Fail-Closed 校验，返回归一化 origin。"""
    if not isinstance(record.decision_id, str) or not record.decision_id.strip():
        raise InvalidDecisionRecordError("decision_id 不能为空", details={"decision_id": record.decision_id})
    try:
        origin = record.origin if isinstance(record.origin, DecisionOrigin) else DecisionOrigin(str(record.origin))
    except (ValueError, TypeError) as exc:
        raise InvalidDecisionRecordError("origin 非法（仅 ai/non_ai）", details={"origin": str(record.origin)}) from exc
    weight = float(record.weight)
    if not math.isfinite(weight) or weight <= 0.0:
        raise InvalidDecisionRecordError("weight 必须为正且有限", details={"weight": str(record.weight)})
    return origin


class NonAIBoundaryGuard:
    """AI/非AI 决策权重边界守卫（判定纯函数 + 信号回调委托）。

    Args:
        thresholds: 边界阈值（None 用默认：>30% 硬顶 / 窗口 200 / 最小样本 20）。
        block_trigger: 阻断信号回调 ``(snapshot, record) -> None``（执行体委托
            风控/执行闸；异常不阻断判定，block_signaled 如实记 False）。
        audit_sink: 审计记录回调 ``(record_dict) -> None``（决策溯源委托
            D_GOV_AUDIT；异常不阻断判定）。
    """

    def __init__(
        self,
        thresholds: BoundaryThresholds | None = None,
        block_trigger: Callable[[BoundarySnapshot, DecisionRecord], None] | None = None,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._thresholds = thresholds if thresholds is not None else BoundaryThresholds()
        if not isinstance(self._thresholds, BoundaryThresholds):
            raise InvalidBoundaryConfigError(
                "thresholds 必须为 BoundaryThresholds",
                details={"type": type(self._thresholds).__name__},
            )
        self._block_trigger = block_trigger
        self._audit_sink = audit_sink

    @property
    def thresholds(self) -> BoundaryThresholds:
        return self._thresholds

    def meter(self, decisions: Iterable[DecisionRecord]) -> BoundarySnapshot:
        """计量窗口内 AI 权重占比（纯函数：同输入必同输出，无 IO）。

        窗口取尾部 ``window_size`` 条；样本 < min_samples 进入观察期恒 ALLOW；
        AI 占比严格大于 max_ai_share → BLOCK_NEW_AI。
        """
        records = list(decisions)[-self._thresholds.window_size :]
        ai_weight = 0.0
        total_weight = 0.0
        for rec in records:
            origin = _validate_record(rec)
            weight = float(rec.weight)
            total_weight += weight
            if origin is DecisionOrigin.AI:
                ai_weight += weight
        samples = len(records)
        ai_share = (ai_weight / total_weight) if total_weight > 0.0 else 0.0
        if samples < self._thresholds.min_samples:
            return BoundarySnapshot(
                samples=samples,
                total_weight=total_weight,
                ai_weight=ai_weight,
                ai_share=ai_share,
                verdict=BoundaryVerdict.ALLOW,
                reason=f"样本不足观察期（{samples}<{self._thresholds.min_samples}），不阻断",
            )
        if ai_share > self._thresholds.max_ai_share:
            return BoundarySnapshot(
                samples=samples,
                total_weight=total_weight,
                ai_weight=ai_weight,
                ai_share=ai_share,
                verdict=BoundaryVerdict.BLOCK_NEW_AI,
                reason=(
                    f"AI决策权重占比 {ai_share:.3f} 超过硬顶 {self._thresholds.max_ai_share:.2f}"
                    "（D-AUTONOMY-33 §30.5.2），阻断新AI决策"
                ),
            )
        return BoundarySnapshot(
            samples=samples,
            total_weight=total_weight,
            ai_weight=ai_weight,
            ai_share=ai_share,
            verdict=BoundaryVerdict.ALLOW,
            reason=f"AI决策权重占比 {ai_share:.3f} 未越界（≤{self._thresholds.max_ai_share:.2f}）",
        )

    def admit(self, record: DecisionRecord, window: Iterable[DecisionRecord]) -> BoundaryAction:
        """单条新决策准入判定：计量窗口 → 非AI恒 ALLOW / AI 超限 BLOCK_NEW_AI。

        阻断仅产 block_trigger 信号（不直接阻断下单，执行委托装配层风控闸）；
        计量快照与阻断信号双审计记录。
        """
        origin = _validate_record(record)
        snapshot = self.meter(window)
        verdict = (
            BoundaryVerdict.BLOCK_NEW_AI
            if origin is DecisionOrigin.AI and snapshot.verdict is BoundaryVerdict.BLOCK_NEW_AI
            else BoundaryVerdict.ALLOW
        )
        block_signaled = False
        if verdict is BoundaryVerdict.BLOCK_NEW_AI and self._block_trigger is not None:
            try:
                self._block_trigger(snapshot, record)
                block_signaled = True
            except Exception:  # noqa: BLE001 - 回调异常不阻断判定（留痕降级）
                _logger.warning("block_trigger 回调异常（不阻断判定）", exc_info=True)
        audit_records: list[dict[str, Any]] = [
            {
                "kind": "meter_snapshot",
                "decision_id": record.decision_id,
                "origin": origin.value,
                "samples": snapshot.samples,
                "ai_share": snapshot.ai_share,
                "verdict": verdict.value,
                "reason": snapshot.reason,
            }
        ]
        if verdict is BoundaryVerdict.BLOCK_NEW_AI:
            audit_records.append(
                {
                    "kind": "block_signal",
                    "decision_id": record.decision_id,
                    "ai_share": snapshot.ai_share,
                    "max_ai_share": self._thresholds.max_ai_share,
                    "signaled": block_signaled,
                }
            )
        if self._audit_sink is not None:
            for audit in audit_records:
                try:
                    self._audit_sink(audit)
                except Exception:  # noqa: BLE001 - sink 异常不阻断判定
                    _logger.warning("audit_sink 回调异常（不阻断判定）", exc_info=True)
        return BoundaryAction(
            verdict=verdict,
            snapshot=snapshot,
            block_signaled=block_signaled,
            audit_records=tuple(audit_records),
        )
