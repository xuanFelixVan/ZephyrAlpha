# [BLUEPRINT] MOD-SIM-028 | docs/03_modules/_domain_simulation/overfitting_protection_gate/blueprint.md
# [MODULE] zephyr.simulation.overfitting_protection_gate
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] 无（纯内存/DI；四层检查器/时钟全注入；DSR/PBO 数值语义经注入检查器旁挂 deflated_sharpe_calculator/overfitting_guard）
# [CONSUMERS] 运行时装配批（因子/策略/信号/ML 四层检查器绑定 / 上线前统一裁决装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层词表闭合(factor|strategy|signal|ml); 检查项按 check_id 确定性排序执行; 任一层失败即拦截(BLOCKED); 任一层无注册检查项 Fail-Closed 拒绝裁决; 检查器异常按失败处理不旁路; 报告 frozen; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_simulation/overfitting_protection_gate/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] OverfittingGateError(占位 ZA-SIM-UNREGISTERED-OVERFITTING-GATE)——非法层/空check_id/重复注册/检查器不可调用/空subject_id/层缺检查项时抛
# [TESTS] tests/simulation/test_overfitting_protection_gate.py
# [A_module] module_id=MOD-SIM-028 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
OverfittingProtectionGate — 过拟合系统性防护门禁（MOD-SIM-028）。

B1-00261（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-SIM-009，C2 C-033）：
**四层防护统一门禁**——因子层（IC 衰减 + 多重检验校正）/ 策略层
（deflated SR + PBO）/ 信号层（walkforward 折叠一致性）/ ML 层（OOS 退化
+ 对抗注入）**四层检查项注册表** + **统一裁决**（任一层失败即拦截上线）
+ **防护报告**。

查重分工（蓝图 §0）：deflated_sharpe_calculator=DSR 数值计算、
overfitting_guard=预注册/WFE 方法论栈（本件不重算指标，各层算法经注入
检查器消费其语义）；本件=检查项注册/编排/统一裁决/报告协议面，检查器
全注入，缺层 Fail-Closed 不放行。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: overfitting_protection_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① OverfittingProtectionGate
#   name_en: OverfittingProtectionGate
#   intro: 四层过拟合防护统一门禁（注册表 + 编排 + 裁决 + 报告）。
#   desc: 四层过拟合防护统一门禁（注册表 + 编排 + 裁决 + 报告）。；公共方法（定义序）: register_check, checks_of, evaluate；源码 L161-L270
#   inputs: clock
#   outputs: 返回值
#   （注：A1 之后另有 8 个公共定义未列入（含 8 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（9 定义）
#   name_en: public defs
#   intro: OverfittingProtectionGate
#   downstream: 运行时装配批（因子/策略/信号/ML 四层检查器绑定 / 上线前统一裁决装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "CheckOutcome",
    "CheckResult",
    "CheckStatus",
    "GateDecision",
    "LayerVerdict",
    "OverfittingGateError",
    "OverfittingProtectionGate",
    "ProtectionLayer",
    "ProtectionReport",
]


class OverfittingGateError(Exception):
    """过拟合防护门禁输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIM-UNREGISTERED-OVERFITTING-GATE。
    """


class ProtectionLayer(str, Enum):
    """防护层（词表闭合）。"""

    FACTOR = "factor"  # 因子层：IC 衰减 + 多重检验校正
    STRATEGY = "strategy"  # 策略层：deflated SR + PBO
    SIGNAL = "signal"  # 信号层：walkforward 折叠一致性
    ML = "ml"  # ML 层：OOS 退化 + 对抗


class CheckStatus(str, Enum):
    """单检查项结论。"""

    PASSED = "passed"
    FAILED = "failed"


class GateDecision(str, Enum):
    """统一裁决（任一层失败即拦截上线）。"""

    APPROVED = "approved"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CheckOutcome:
    """检查器返回载荷（frozen）：passed + 指标 + 说明。"""

    passed: bool
    metrics: Mapping = field(default_factory=dict)
    detail: str = ""


@dataclass(frozen=True)
class CheckResult:
    """单检查项执行结果（frozen）。"""

    check_id: str
    layer: ProtectionLayer
    status: CheckStatus
    metrics: Mapping
    detail: str


@dataclass(frozen=True)
class LayerVerdict:
    """单层裁决（frozen；results 按 check_id 确定性排序）。"""

    layer: ProtectionLayer
    passed: bool
    results: tuple[CheckResult, ...]


@dataclass(frozen=True)
class ProtectionReport:
    """防护报告（frozen；blocked_by 确定性排序）。"""

    subject_id: str
    decision: GateDecision
    layer_verdicts: tuple[LayerVerdict, ...]
    blocked_by: tuple[str, ...]
    generated_at: datetime.datetime


#: 统一裁决层执行顺序（确定性）
_LAYER_ORDER: Final[tuple[ProtectionLayer, ...]] = (
    ProtectionLayer.FACTOR,
    ProtectionLayer.STRATEGY,
    ProtectionLayer.SIGNAL,
    ProtectionLayer.ML,
)


class OverfittingProtectionGate:
    """四层过拟合防护统一门禁（注册表 + 编排 + 裁决 + 报告）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._checks: dict[ProtectionLayer, dict[str, Callable[[Mapping], CheckOutcome]]] = {
            layer: {} for layer in _LAYER_ORDER
        }

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_layer(layer: ProtectionLayer) -> ProtectionLayer:
        if not isinstance(layer, ProtectionLayer):
            raise OverfittingGateError(f"非法防护层: {layer!r}（词表闭合 factor|strategy|signal|ml）")
        return layer

    # ── 检查项注册表 ──────────────────────────────────────────────────────

    def register_check(
        self,
        layer: ProtectionLayer,
        check_id: str,
        checker: Callable[[Mapping], CheckOutcome],
    ) -> None:
        """登记检查项：层词表闭合；check_id 非空且层内唯一；检查器可调用。"""
        self._validate_layer(layer)
        if not check_id:
            raise OverfittingGateError("check_id 为空")
        if not callable(checker):
            raise OverfittingGateError(f"检查器不可调用: {check_id!r}")
        bucket = self._checks[layer]
        if check_id in bucket:
            raise OverfittingGateError(f"check_id 重复注册: {layer.value}/{check_id!r}")
        bucket[check_id] = checker
        _log.debug("防护检查项登记: %s/%s", layer.value, check_id)

    def checks_of(self, layer: ProtectionLayer) -> tuple[str, ...]:
        """单层已注册 check_id 视图（按 check_id 确定性排序）。"""
        self._validate_layer(layer)
        return tuple(sorted(self._checks[layer]))

    # ── 统一裁决 ──────────────────────────────────────────────────────────

    def evaluate(self, subject_id: str, payload: Mapping | None = None) -> ProtectionReport:
        """统一裁决：四层全评估，任一层任一检查项失败即 BLOCKED 拦截上线。

        Fail-Closed：任一层无注册检查项 → 拒绝裁决（防护不完整不放行）；
        检查器异常 → 该检查项按失败处理（不旁路）。
        """
        if not subject_id:
            raise OverfittingGateError("subject_id 为空")
        ctx: Mapping = payload if payload is not None else {}
        for layer in _LAYER_ORDER:
            if not self._checks[layer]:
                raise OverfittingGateError(f"防护层 {layer.value!r} 无注册检查项（防护不完整，Fail-Closed 拒绝裁决）")

        verdicts: list[LayerVerdict] = []
        blocked: list[str] = []
        for layer in _LAYER_ORDER:
            results: list[CheckResult] = []
            for check_id in sorted(self._checks[layer]):
                checker = self._checks[layer][check_id]
                try:
                    outcome = checker(ctx)
                    passed = bool(outcome.passed)
                    metrics = dict(outcome.metrics)
                    detail = outcome.detail
                except Exception as exc:  # noqa: BLE001 — 检查器异常按失败处理不旁路
                    _log.exception("防护检查器异常: %s/%s", layer.value, check_id)
                    passed, metrics, detail = False, {}, f"检查器异常: {exc!r}"
                status = CheckStatus.PASSED if passed else CheckStatus.FAILED
                if not passed:
                    blocked.append(check_id)
                results.append(
                    CheckResult(
                        check_id=check_id,
                        layer=layer,
                        status=status,
                        metrics=metrics,
                        detail=detail,
                    )
                )
            verdicts.append(
                LayerVerdict(
                    layer=layer,
                    passed=all(r.status is CheckStatus.PASSED for r in results),
                    results=tuple(results),
                )
            )

        decision = GateDecision.APPROVED if not blocked else GateDecision.BLOCKED
        report = ProtectionReport(
            subject_id=subject_id,
            decision=decision,
            layer_verdicts=tuple(verdicts),
            blocked_by=tuple(sorted(blocked)),
            generated_at=self._clock(),
        )
        _log.info(
            "过拟合防护裁决: subject=%s decision=%s blocked_by=%s",
            subject_id,
            decision.value,
            report.blocked_by,
        )
        return report
