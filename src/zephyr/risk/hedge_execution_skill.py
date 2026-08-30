# [BLUEPRINT] MOD-RK-042 | docs/03_modules/_domain_risk/hedge_execution_skill/blueprint.md
# [MODULE] zephyr.risk.hedge_execution_skill
# [DOMAIN] D_RISK
# [DEPENDENCIES] 无（协议核心纯内存；价格/基差/执行回调/双确认/时钟 全注入）
# [CONSUMERS] 运行时装配批（对冲执行技能装配：执行层回调 / 风控Agent+人工双确认注入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 标的词表闭合(股指期货/ETF映射表); hedge_ratio∈(0,1]; 敞口为正Decimal; 腿单方向=sell(对冲多头敞口); 数量取整≥1否则Fail-Closed; human_gated双确认(风控+人工)缺一不执行; 有效性=对冲前后敞口比回写; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_risk/hedge_execution_skill/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] HedgeExecutionError(占位 ZA-RK-UNREGISTERED-HEDGE-EXECUTION)——空request_id/未知标的/非法比例或敞口/价格基差缺失/数量不足一手/执行回调未注入时抛
# [TESTS] tests/risk/test_hedge_execution_skill.py
# [A_module] module_id=MOD-RK-042 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
HedgeExecutionSkill — 对冲执行技能（MOD-RK-042）。

B11-02591（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-RSK-046，A7 技能
hedge-execution）：对冲需求（敞口/比例）→ 标的映射（股指期货/ETF 词表闭合
+ 基差注入）→ 腿单生成（方向/数量计算）→ 执行层回调注入 → 对冲有效性回写
（对冲前后敞口比）+ human_gated 双确认硬约束（风控 Agent + 人工，缺一不执
行）。

查重分工（蓝图 §0）：risk_veto_engine=交易前风控否决（本件=否决之外的主动
降敞口执行技能，零交集）；exposure_manager=组合敞口调仓（本件不改正股持仓，
仅生成对冲腿单）；portfolio_optimizer=权重优化（本件=确定性词表映射+数量取
整，不做优化）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: instrument_vocab 参数
#   fields: 参数 instrument_vocab（无注解）
#   code: hedge_execution_skill.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: price_provider 参数
#   fields: 参数 price_provider（无注解）
#   code: hedge_execution_skill.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: basis_provider 参数
#   fields: 参数 basis_provider（无注解）
#   code: hedge_execution_skill.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: executor 参数
#   fields: 参数 executor（无注解）
#   code: hedge_execution_skill.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① HedgeExecutionSkill
#   name_en: HedgeExecutionSkill
#   intro: 对冲执行技能（标的映射 + 腿单生成 + 双确认执行 + 有效性回写）。
#   desc: 对冲执行技能（标的映射 + 腿单生成 + 双确认执行 + 有效性回写）。；公共方法（定义序）: plan, execute, record_of, records；源码 L196-L373
#   inputs: instrument_vocab price_provider basis_provider executor risk_confirme…
#   outputs: 返回值
#   （注：A1 之后另有 9 个公共定义未列入（含 9 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（10 定义）
#   name_en: public defs
#   intro: HedgeExecutionSkill
#   downstream: 运行时装配批（对冲执行技能装配：执行层回调 / 风控Agent+人工双确认注入）
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

import datetime
import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "HedgeEffectiveness",
    "HedgeExecutionError",
    "HedgeExecutionSkill",
    "HedgeInstrumentSpec",
    "HedgeInstrumentType",
    "HedgeLeg",
    "HedgePlan",
    "HedgeRecord",
    "HedgeRequest",
    "HedgeStatus",
]

_ZERO: Final = Decimal("0")
_ONE: Final = Decimal("1")


class HedgeExecutionError(Exception):
    """对冲执行技能输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-RK-UNREGISTERED-HEDGE-EXECUTION。
    """


class HedgeInstrumentType(str, Enum):
    """对冲工具类型（词表闭合）。"""

    STOCK_INDEX_FUTURE = "stock_index_future"
    ETF = "etf"


class HedgeStatus(str, Enum):
    """对冲计划状态机。"""

    PLANNED = "planned"
    EXECUTED = "executed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class HedgeInstrumentSpec:
    """对冲标的映射条目（股指期货/ETF 词表条目，frozen）。

    contract_multiplier 仅对股指期货有意义（ETF 取 1）。
    """

    index_code: str
    future_symbol: str
    etf_symbol: str
    contract_multiplier: Decimal


@dataclass(frozen=True)
class HedgeRequest:
    """对冲需求 Schema（敞口/比例，frozen，金额 Decimal）。"""

    request_id: str
    index_code: str
    exposure: Decimal
    hedge_ratio: Decimal
    instrument_type: HedgeInstrumentType
    created_at: datetime.datetime


@dataclass(frozen=True)
class HedgeLeg:
    """对冲腿单（方向/数量/名义，frozen）。"""

    leg_id: str
    instrument_type: HedgeInstrumentType
    symbol: str
    direction: str  # 对冲多头敞口 → "sell"
    quantity: int
    notional: Decimal


@dataclass(frozen=True)
class HedgePlan:
    """对冲计划（腿单集合 + 基差 + 总名义，frozen）。"""

    request_id: str
    index_code: str
    exposure: Decimal
    hedge_ratio: Decimal
    basis: Decimal
    legs: tuple[HedgeLeg, ...]
    total_notional: Decimal
    planned_at: datetime.datetime


@dataclass(frozen=True)
class HedgeEffectiveness:
    """对冲有效性回写（对冲前后敞口比，frozen）。"""

    request_id: str
    exposure_before: Decimal
    exposure_after: Decimal
    effectiveness: Decimal  # 1 - |after|/before
    evaluated_at: datetime.datetime


@dataclass(frozen=True)
class HedgeRecord:
    """对冲执行记录（计划 + 状态 + 有效性，frozen）。"""

    plan: HedgePlan
    status: HedgeStatus
    reason: str
    effectiveness: HedgeEffectiveness | None


class HedgeExecutionSkill:
    """对冲执行技能（标的映射 + 腿单生成 + 双确认执行 + 有效性回写）。"""

    def __init__(
        self,
        *,
        instrument_vocab: Mapping[str, HedgeInstrumentSpec],
        price_provider: Callable[[str], Decimal] | None = None,
        basis_provider: Callable[[str], Decimal] | None = None,
        executor: Callable[[HedgeLeg], bool] | None = None,
        risk_confirmer: Callable[[HedgePlan], bool] | None = None,
        human_confirmer: Callable[[HedgePlan], bool] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not instrument_vocab:
            raise HedgeExecutionError("instrument_vocab 为空（标的词表未声明）")
        for index_code, spec in instrument_vocab.items():
            if not index_code:
                raise HedgeExecutionError("index_code 为空")
            if not isinstance(spec, HedgeInstrumentSpec):
                raise HedgeExecutionError(f"非法标的条目: {spec!r}")
            if spec.index_code != index_code:
                raise HedgeExecutionError(f"词表键/条目不一致: {index_code!r} vs {spec.index_code!r}")
            if spec.contract_multiplier <= _ZERO:
                raise HedgeExecutionError(f"合约乘数非正: {index_code!r}")
        self._vocab: dict[str, HedgeInstrumentSpec] = dict(instrument_vocab)
        self._price = price_provider
        self._basis = basis_provider
        self._executor = executor
        self._risk_confirmer = risk_confirmer
        self._human_confirmer = human_confirmer
        self._clock = clock or datetime.datetime.now
        self._records: dict[str, HedgeRecord] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _spec_of(self, index_code: str) -> HedgeInstrumentSpec:
        spec = self._vocab.get(index_code)
        if spec is None:
            raise HedgeExecutionError(f"未知对冲标的: {index_code!r}（不在词表中）")
        return spec

    def _price_of(self, symbol: str) -> Decimal:
        if self._price is None:
            raise HedgeExecutionError("price_provider 未注入（腿单数量计算缺价格）")
        price = self._price(symbol)
        if price is None or price <= _ZERO:
            raise HedgeExecutionError(f"价格缺失/非正: {symbol!r}")
        return price

    def _basis_of(self, index_code: str) -> Decimal:
        if self._basis is None:
            return _ZERO
        basis = self._basis(index_code)
        if basis is None:
            raise HedgeExecutionError(f"基差缺失: {index_code!r}")
        return basis

    # ── 对冲需求 → 腿单生成 ──────────────────────────────────────────────

    def plan(self, request: HedgeRequest) -> HedgePlan:
        """对冲需求 → 标的映射 → 腿单生成（数量=名义/(价格×乘数) 取整）。"""
        if not isinstance(request, HedgeRequest):
            raise HedgeExecutionError(f"非法对冲需求: {request!r}")
        if not request.request_id:
            raise HedgeExecutionError("request_id 为空")
        if not isinstance(request.instrument_type, HedgeInstrumentType):
            raise HedgeExecutionError(f"非法工具类型: {request.instrument_type!r}")
        if request.exposure <= _ZERO:
            raise HedgeExecutionError(f"敞口非正: {request.exposure!r}")
        if not (_ZERO < request.hedge_ratio <= _ONE):
            raise HedgeExecutionError(f"对冲比例越界(0,1]: {request.hedge_ratio!r}")
        spec = self._spec_of(request.index_code)
        basis = self._basis_of(request.index_code)

        if request.instrument_type is HedgeInstrumentType.STOCK_INDEX_FUTURE:
            symbol = spec.future_symbol
            multiplier = spec.contract_multiplier
        else:
            symbol = spec.etf_symbol
            multiplier = _ONE
        price = self._price_of(symbol)
        target_notional = request.exposure * request.hedge_ratio
        per_contract = price * multiplier
        quantity = int(target_notional / per_contract)
        if quantity < 1:
            raise HedgeExecutionError(f"对冲名义不足一手: 目标名义 {target_notional} < 单手名义 {per_contract}")
        notional = per_contract * quantity
        leg = HedgeLeg(
            leg_id=f"{request.request_id}-L1",
            instrument_type=request.instrument_type,
            symbol=symbol,
            direction="sell",
            quantity=quantity,
            notional=notional,
        )
        return HedgePlan(
            request_id=request.request_id,
            index_code=request.index_code,
            exposure=request.exposure,
            hedge_ratio=request.hedge_ratio,
            basis=basis,
            legs=(leg,),
            total_notional=notional,
            planned_at=self._clock(),
        )

    # ── 双确认执行 + 有效性回写 ──────────────────────────────────────────

    def execute(self, request: HedgeRequest) -> HedgeRecord:
        """执行：human_gated 双确认（风控+人工缺一不执行）→ 回调 → 有效性回写。"""
        plan = self.plan(request)
        if plan.request_id in self._records:
            raise HedgeExecutionError(f"request_id 重复: {plan.request_id!r}")

        blockers: list[str] = []
        if self._risk_confirmer is None:
            blockers.append("风控确认未注入")
        elif not bool(self._risk_confirmer(plan)):
            blockers.append("风控确认拒绝")
        if self._human_confirmer is None:
            blockers.append("人工确认未注入")
        elif not bool(self._human_confirmer(plan)):
            blockers.append("人工确认拒绝")
        if blockers:
            reason = "双确认硬约束拦截: " + "; ".join(blockers)
            _log.warning("对冲执行拦截: %s (%s)", plan.request_id, reason)
            record = HedgeRecord(plan=plan, status=HedgeStatus.BLOCKED, reason=reason, effectiveness=None)
            self._records[plan.request_id] = record
            return record

        if self._executor is None:
            raise HedgeExecutionError("executor 未注入（双确认已过，禁止旁路执行）")
        for leg in plan.legs:
            try:
                ok = bool(self._executor(leg))
            except Exception:  # noqa: BLE001 — 执行回调异常按失败处理不抛
                _log.exception("executor 执行异常: %s", leg.leg_id)
                ok = False
            if not ok:
                reason = f"执行回调失败: {leg.leg_id}"
                record = HedgeRecord(plan=plan, status=HedgeStatus.BLOCKED, reason=reason, effectiveness=None)
                self._records[plan.request_id] = record
                return record

        # 有效性回写：对冲后敞口 = 对冲前敞口 - 有效对冲名义（基差扣减）
        effective_notional = plan.total_notional - abs(plan.basis) * plan.legs[0].quantity
        if effective_notional < _ZERO:
            effective_notional = _ZERO
        exposure_after = plan.exposure - effective_notional
        effectiveness = HedgeEffectiveness(
            request_id=plan.request_id,
            exposure_before=plan.exposure,
            exposure_after=exposure_after,
            effectiveness=_ONE - (abs(exposure_after) / plan.exposure),
            evaluated_at=self._clock(),
        )
        record = HedgeRecord(
            plan=plan,
            status=HedgeStatus.EXECUTED,
            reason="",
            effectiveness=effectiveness,
        )
        self._records[plan.request_id] = record
        return record

    # ── 查询 ─────────────────────────────────────────────────────────────

    def record_of(self, request_id: str) -> HedgeRecord:
        """单请求执行记录（未知 → Fail-Closed）。"""
        record = self._records.get(request_id)
        if record is None:
            raise HedgeExecutionError(f"未知 request: {request_id!r}")
        return record

    def records(self) -> tuple[HedgeRecord, ...]:
        """全部执行记录（按 request_id 确定性排序）。"""
        return tuple(self._records[k] for k in sorted(self._records))
