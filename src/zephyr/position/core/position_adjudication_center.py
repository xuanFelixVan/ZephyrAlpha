# [BLUEPRINT] MOD-POS-024 | docs/03_modules/_domain_position/position_adjudication_center/blueprint.md
# [MODULE] zephyr.position.core.position_adjudication_center
# [DOMAIN] D_POSITION
# [DEPENDENCIES]
# [CONSUMERS] 运行时装配批（四层 callable 接 MOD-POS-001/010/013/018；下单链令牌校验接线）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只编排不重造(四层判定全委托注入callable); 四层顺序固定(组合→策略→标的→动态); 任一层拒绝/异常→终审拒绝final_weight=0(Fail-Closed不外抛); 四层全过→final_weight=min(最保守收敛); adjudication_id=sha256(规范化请求)前16hex同请求幂等不重复签发; 令牌缺失/不符=旁路阻断; 请求字段非法Fail-Closed
# [MODIFY-GUARD] tests/position/test_position_adjudication_center.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PositionAdjudicationError(未登记错误码-申请中)
# [TESTS] tests/position/test_position_adjudication_center.py
# [A_module] module_id=MOD-POS-024 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: AdjudicationRequest(request_id/strategy_id/symbol/action/intended_weight/context)
# I2: 四层callable(组合/策略/标的/动态,装配批接MOD-POS-013/020族/001+010/018)
# A1: 请求校验+规范化指纹(sha256前16hex=adjudication_id)
# A2: 四层依序裁决(任一层拒绝/异常→终审拒绝汇聚violations)
# A3: 最保守收敛(全过→final_weight=min(adjusted_weight))+幂等注册
# O1: AdjudicatedPositionPlan / verify_bypass(令牌缺失或不符=True)
# [/ALGO_FLOW]
"""
C-047 仓位管理唯一裁决中心（MOD-POS-024）。

真源：construction_backlog_dig.tsv B1-00194（跨域元文档 §功能域模块·D-PORTFOLIO，
裁定=做 P1）+ CAND-POS-002。TSV 现状注记："四层构件(sizing/limit/risk_budget/
intraday)已存在但无唯一权威裁决入口，核心交易链需要"——本模块=该**编排层
唯一入口**（查重铁律⑤裁定：编排缺口，非真源重叠）。

裁决规则（确定性，Fail-Closed，"只编排不重造"与 MOD-BT-001
strategy_validation_pipeline 同族）：
  ① 四层裁决：依序调 组合层→策略层→标的层→动态层（注入 callable，装配批
     接 MOD-POS-013 风险预算/MOD-POS-020 族策略账本/MOD-POS-001 精裁+
     MOD-POS-010 否决/MOD-POS-018 盘中约束）；任一层 allowed=False → 终审
     拒绝（final_weight=0，汇聚 violations）；层异常 → 该层拒绝处理
     （Fail-Closed，不外抛）。
  ② 最保守收敛：四层全过 → final_weight=min(各层 adjusted_weight)。
  ③ 唯一性令牌：adjudication_id=sha256(规范化请求)前16hex；同请求幂等
     （重复 adjudicate 返回首份裁决，不重发令牌）。
  ④ 旁路阻断：verify_bypass(request, token)——令牌缺失/请求未曾裁决/令牌
     与首发不符 = True（旁路下单嫌疑，下单链只认首发令牌，装配批接线）。

不做什么：不重造四层判定逻辑（委托注入）、不直接下单（只出
AdjudicatedPositionPlan+令牌）、不做预算分配（归 MOD-PA-007 effective_budget
链——那是分配层，本件是交易时裁决层）。

SSoT: docs/03_modules/_domain_position/position_adjudication_center/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: portfolio_layer 参数
#   fields: 参数 portfolio_layer（无注解）
#   code: position_adjudication_center.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: strategy_layer 参数
#   fields: 参数 strategy_layer（无注解）
#   code: position_adjudication_center.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: symbol_layer 参数
#   fields: 参数 symbol_layer（无注解）
#   code: position_adjudication_center.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: dynamic_layer 参数
#   fields: 参数 dynamic_layer（无注解）
#   code: position_adjudication_center.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AdjudicationRequest
#   name_en: AdjudicationRequest
#   intro: 裁决请求（不可变）。
#   desc: 裁决请求（不可变）。 Attributes: request_id: 请求标识（审计留痕） strategy_id: 策略标识 symbol: 标的代码 action: 交易意图…；公共方法（定义序）: fingerp…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② PositionAdjudicationCenter
#   name_en: PositionAdjudicationCenter
#   intro: 仓位管理唯一裁决中心（四层编排 + 唯一令牌 + 旁路阻断）。
#   desc: 仓位管理唯一裁决中心（四层编排 + 唯一令牌 + 旁路阻断）。 四层 callable 注入（装配批接既有件）；本中心只编排不判定。；公共方法（定义序）: adjudicate, verify_bypass；源码 L2…
#   inputs: portfolio_layer strategy_layer symbol_layer dynamic_layer
#   outputs: 返回值
#   （注：A2 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: AdjudicationRequest, PositionAdjudicationCenter
#   downstream: 运行时装配批（四层 callable 接 MOD-POS-001/010/013/018；下单链令牌校验接线）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final

__all__: Final = [
    "AdjudicatedPositionPlan",
    "AdjudicationRequest",
    "IntendedAction",
    "LayerVerdict",
    "PositionAdjudicationCenter",
    "PositionAdjudicationError",
]

_log = logging.getLogger(__name__)


class PositionAdjudicationError(Exception):
    """仓位裁决中心错误（请求非法）。"""

    error_code = "ZA-POS-0026"  # 2026-08-25 主代理正式登记（P1 R4W19）

    def __init__(self, *args: object, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


class IntendedAction(str, Enum):
    """交易意图（四层裁决语义对齐 MOD-POS-010 OPEN/ADD 族）。"""

    OPEN = "OPEN"
    ADD = "ADD"
    REDUCE = "REDUCE"
    EXIT = "EXIT"


@dataclass(frozen=True)
class AdjudicationRequest:
    """裁决请求（不可变）。

    Attributes:
        request_id: 请求标识（审计留痕）
        strategy_id: 策略标识
        symbol: 标的代码
        action: 交易意图
        intended_weight: 意图目标权重 ∈[0,1]
        context: 裁决上下文（组合暴露/策略预算/盘中投影等，键值由层解释）
    """

    request_id: str
    strategy_id: str
    symbol: str
    action: IntendedAction
    intended_weight: float
    context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_id:
            raise PositionAdjudicationError("request_id不能为空")
        if not self.strategy_id:
            raise PositionAdjudicationError("strategy_id不能为空")
        if not self.symbol:
            raise PositionAdjudicationError("symbol不能为空")
        if not isinstance(self.action, IntendedAction):
            raise PositionAdjudicationError(f"action必须∈IntendedAction, got {self.action!r}")
        if not 0.0 <= self.intended_weight <= 1.0:
            raise PositionAdjudicationError(f"intended_weight必须∈[0,1], got {self.intended_weight}")
        if not isinstance(self.context, Mapping):
            raise PositionAdjudicationError("context必须是Mapping")

    def fingerprint(self) -> str:
        """规范化指纹（sha256 前 16 hex = adjudication_id 候选）。"""
        try:
            canonical = json.dumps(
                {
                    "strategy_id": self.strategy_id,
                    "symbol": self.symbol,
                    "action": self.action.value,
                    "intended_weight": self.intended_weight,
                    "context": dict(self.context),
                },
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            )
        except (TypeError, ValueError) as exc:
            raise PositionAdjudicationError(f"context不可规范化序列化: {exc}") from exc
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class LayerVerdict:
    """单层裁决（不可变）。

    Attributes:
        layer: 层名（portfolio/strategy/symbol/dynamic）
        allowed: 本层是否放行
        adjusted_weight: 本层调整后的权重上限 ∈[0,1]
        violations: 违规项（拒绝时非空）
        reason: 裁决理由（审计留痕）
    """

    layer: str
    allowed: bool
    adjusted_weight: float
    violations: tuple[str, ...] = ()
    reason: str = ""

    def __post_init__(self) -> None:
        if self.layer not in ("portfolio", "strategy", "symbol", "dynamic"):
            raise PositionAdjudicationError(f"layer非法: {self.layer}")
        if not 0.0 <= self.adjusted_weight <= 1.0:
            raise PositionAdjudicationError(f"adjusted_weight必须∈[0,1], got {self.adjusted_weight}")


@dataclass(frozen=True)
class AdjudicatedPositionPlan:
    """唯一权威目标仓位裁决（不可变）。

    Attributes:
        adjudication_id: 唯一性令牌（sha256 前 16 hex，下单链凭证）
        request: 原请求
        allowed: 终审是否放行
        final_weight: 终审目标权重（拒绝=0；放行=min(四层) 最保守收敛）
        layer_verdicts: 四层裁决（按 组合→策略→标的→动态 顺序）
        reason: 终审理由
    """

    adjudication_id: str
    request: AdjudicationRequest
    allowed: bool
    final_weight: float
    layer_verdicts: tuple[LayerVerdict, ...]
    reason: str


_LAYER_ORDER: Final = ("portfolio", "strategy", "symbol", "dynamic")


class PositionAdjudicationCenter:
    """仓位管理唯一裁决中心（四层编排 + 唯一令牌 + 旁路阻断）。

    四层 callable 注入（装配批接既有件）；本中心只编排不判定。
    """

    def __init__(
        self,
        portfolio_layer: Callable[[AdjudicationRequest], LayerVerdict],
        strategy_layer: Callable[[AdjudicationRequest], LayerVerdict],
        symbol_layer: Callable[[AdjudicationRequest], LayerVerdict],
        dynamic_layer: Callable[[AdjudicationRequest], LayerVerdict],
    ) -> None:
        layers = {
            "portfolio": portfolio_layer,
            "strategy": strategy_layer,
            "symbol": symbol_layer,
            "dynamic": dynamic_layer,
        }
        for name, fn in layers.items():
            if not callable(fn):
                raise PositionAdjudicationError(f"{name}_layer必须可调用")
        self._layers = layers
        self._issued: dict[str, AdjudicatedPositionPlan] = {}

    def _call_layer(self, name: str, request: AdjudicationRequest) -> LayerVerdict:
        """调用单层：异常收敛为该层拒绝（Fail-Closed，不外抛）。"""
        try:
            verdict = self._layers[name](request)
        except Exception as exc:  # noqa: BLE001 — 层异常=该层拒绝，Fail-Closed
            _log.warning("裁决层%s异常(按拒绝处理): %s", name, exc, exc_info=True)
            return LayerVerdict(
                layer=name,
                allowed=False,
                adjusted_weight=0.0,
                violations=(f"LAYER_ERROR:{type(exc).__name__}",),
                reason=f"层异常Fail-Closed: {exc}",
            )
        if not isinstance(verdict, LayerVerdict):
            return LayerVerdict(
                layer=name,
                allowed=False,
                adjusted_weight=0.0,
                violations=("LAYER_CONTRACT_VIOLATION",),
                reason="层返回非LayerVerdict（契约违反，Fail-Closed）",
            )
        return verdict

    def adjudicate(self, request: AdjudicationRequest) -> AdjudicatedPositionPlan:
        """四层裁决唯一入口（幂等：同请求返回首份裁决，不重发令牌）。"""
        if not isinstance(request, AdjudicationRequest):
            raise PositionAdjudicationError("request必须是AdjudicationRequest")
        adjudication_id = request.fingerprint()
        if adjudication_id in self._issued:
            return self._issued[adjudication_id]

        verdicts: list[LayerVerdict] = []
        for name in _LAYER_ORDER:
            verdicts.append(self._call_layer(name, request))
        vt = tuple(verdicts)

        denied = [v for v in vt if not v.allowed]
        if denied:
            plan = AdjudicatedPositionPlan(
                adjudication_id=adjudication_id,
                request=request,
                allowed=False,
                final_weight=0.0,
                layer_verdicts=vt,
                reason="终审拒绝：" + ";".join(f"{v.layer}({','.join(v.violations) or v.reason})" for v in denied),
            )
        else:
            final_weight = min(v.adjusted_weight for v in vt)
            plan = AdjudicatedPositionPlan(
                adjudication_id=adjudication_id,
                request=request,
                allowed=True,
                final_weight=final_weight,
                layer_verdicts=vt,
                reason=f"四层全过，最保守收敛final_weight={final_weight:.6f}",
            )
        self._issued[adjudication_id] = plan
        return plan

    def verify_bypass(self, request: AdjudicationRequest, token: str | None) -> bool:
        """旁路下单检测：令牌缺失/请求未曾裁决/令牌与首发不符 = True（阻断）。"""
        if not isinstance(request, AdjudicationRequest):
            raise PositionAdjudicationError("request必须是AdjudicationRequest")
        if not token:
            return True
        issued = self._issued.get(request.fingerprint())
        if issued is None:
            return True
        return issued.adjudication_id != token
