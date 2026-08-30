# [BLUEPRINT] MOD-EX-064 | docs/03_modules/_domain_execution_core/execution_param_optimizer/blueprint.md
# [MODULE] zephyr.ex_core.execution_param_optimizer
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] 无（协议核心纯内存；tca_reader/study_runner/objective_fn/clock/audit_sink 全注入；optuna 未装降级网格搜索）
# [CONSUMERS] 运行时装配批（执行参数周期优化调度 / 人工确认通道接线 / 风控硬阈值白名单声明）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 参数白名单闭合(声明校验+搜索结果校验双闸); 未人工确认提案不改变生效参数; study_runner 未注入/异常降级网格搜索; 网格按(参数名,候选声明序)确定性遍历取最小目标; TCA 读数未注入/为空 Fail-Closed; 提案状态机 PENDING→CONFIRMED|REJECTED; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_execution_core/execution_param_optimizer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ExecutionOptimizerError(占位 ZA-EX-UNREGISTERED-EXECUTION-OPTIMIZER)——空参数空间/空白名单/白名单外参数/非法候选/TCA 缺失或为空/重复 cycle_id/未知提案/非法状态迁移时抛
# [TESTS] tests/ex_core/test_execution_param_optimizer.py
# [A_module] module_id=MOD-EX-064 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



ExecutionParamOptimizer — 执行运营自优化器（MOD-EX-064）。

B1-00218（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-EX-010，C2 C-026）：执行运
营自优化——周期读 TCA 与成交质量（注入 tca_reader）+ optuna 搜索下单算法
参数与运营规则（注入 study_runner，optuna 未装/异常时降级网格搜索）+ 人工
确认后生效（确认队列硬约束：未确认提案绝不改变生效参数）+ 不自动改风控硬
阈值（参数白名单双闸拦截：声明校验 + 搜索结果校验）。

canonical 承接：CAND-EX-011（同为 C-026 执行运营自优化，B10/B1 两稿重登，
含拆单/等待参数语义）归并本件（wave08_spec.json reviews）。

查重分工（蓝图 §0）：default_tca_engine=TCA 计算真源（本件经注入 reader 消
费其周期读数，不重算 TCA）；execution_strategy_selector=策略选择规则（本
件=参数寻优与人工确认队列，零交集）；风控硬阈值由风控域自持（本件仅经白
名单拦截，绝不越权改写）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: param_space 参数
#   fields: 参数 param_space（无注解）
#   code: execution_param_optimizer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: whitelist 参数
#   fields: 参数 whitelist（无注解）
#   code: execution_param_optimizer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: tca_reader 参数
#   fields: 参数 tca_reader（无注解）
#   code: execution_param_optimizer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: study_runner 参数
#   fields: 参数 study_runner（无注解）
#   code: execution_param_optimizer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ExecutionParamOptimizer
#   name_en: ExecutionParamOptimizer
#   intro: 执行运营自优化器（TCA 周期读数 + 参数搜索 + 人工确认 + 白名单拦截）。
#   desc: 执行运营自优化器（TCA 周期读数 + 参数搜索 + 人工确认 + 白名单拦截）。；公共方法（定义序）: run_cycle, confirm, reject, active_params, proposal_stat…
#   inputs: param_space whitelist tca_reader study_runner objective_fn clock audi…
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: ExecutionParamOptimizer
#   downstream: 运行时装配批（执行参数周期优化调度 / 人工确认通道接线 / 风控硬阈值白名单声明）
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
import itertools
import logging
from dataclasses import dataclass, replace
from decimal import Decimal
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ExecutionOptimizerError",
    "ExecutionParamOptimizer",
    "OptimizationProposal",
    "ParamSpec",
    "ProposalStatus",
    "TcaSnapshot",
]


class ExecutionOptimizerError(Exception):
    """执行参数优化器输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-EX-UNREGISTERED-EXECUTION-OPTIMIZER。
    """


class ProposalStatus(str, Enum):
    """优化提案状态机（人工确认队列）。"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ParamSpec:
    """单个可调参数的离散搜索空间（候选声明序即网格遍历序，frozen）。"""

    name: str
    candidates: tuple


@dataclass(frozen=True)
class TcaSnapshot:
    """TCA/成交质量周期读数（tca_reader 返回载体，frozen）。"""

    snapshot_id: str
    algo: str
    slippage_bps: Decimal
    fill_rate: Decimal
    observed_at: datetime.datetime


@dataclass(frozen=True)
class OptimizationProposal:
    """优化提案（人工确认队列条目，frozen）。"""

    proposal_id: str
    params: dict
    objective_value: Decimal
    source: str  # "optuna"（study_runner 注入）| "grid"（降级网格）
    created_at: datetime.datetime
    status: ProposalStatus


class ExecutionParamOptimizer:
    """执行运营自优化器（TCA 周期读数 + 参数搜索 + 人工确认 + 白名单拦截）。"""

    def __init__(
        self,
        *,
        param_space: Mapping[str, ParamSpec],
        whitelist: frozenset[str] | set[str],
        tca_reader: Callable[[], list[TcaSnapshot]] | None = None,
        study_runner: Callable[
            [Mapping[str, ParamSpec], Callable[[Mapping[str, object]], Decimal]],
            Mapping[str, object],
        ]
        | None = None,
        objective_fn: Callable[[Mapping[str, object], tuple[TcaSnapshot, ...]], Decimal] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[dict], None] | None = None,
    ) -> None:
        if not param_space:
            raise ExecutionOptimizerError("param_space 为空（无可调参数声明）")
        if not whitelist:
            raise ExecutionOptimizerError("whitelist 为空（无可优化参数白名单）")
        self._space: dict[str, ParamSpec] = {}
        for name in sorted(param_space):
            spec = param_space[name]
            if not isinstance(spec, ParamSpec) or spec.name != name:
                raise ExecutionOptimizerError(f"参数声明不符: {name!r}")
            if name not in whitelist:
                raise ExecutionOptimizerError(f"参数 {name!r} 不在白名单（风控硬阈值等非白名单参数禁止自动优化）")
            if not spec.candidates:
                raise ExecutionOptimizerError(f"参数 {name!r} 候选为空")
            self._space[name] = spec
        self._whitelist = frozenset(whitelist)
        self._tca_reader = tca_reader
        self._study_runner = study_runner
        self._objective_fn = objective_fn
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        # 生效参数初值=各参数首候选（确定性默认）；仅人工确认后才会改变
        self._defaults: dict[str, object] = {name: spec.candidates[0] for name, spec in self._space.items()}
        self._active: dict[str, object] = dict(self._defaults)
        self._proposals: dict[str, OptimizationProposal] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _audit(self, event: dict) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(event)
            except Exception:  # noqa: BLE001 — 审计回调不阻断主链
                _log.exception("audit_sink 回调失败")

    def _objective(self, params: Mapping[str, object], snapshots: tuple[TcaSnapshot, ...]) -> Decimal:
        if self._objective_fn is not None:
            value = self._objective_fn(params, snapshots)
            if not isinstance(value, Decimal):
                raise ExecutionOptimizerError(f"objective_fn 返回非 Decimal: {type(value)!r}")
            return value
        # 默认目标：平均滑点（bps，越小越好），与参数无关 → 网格取首候选组合（确定性）
        total = sum((s.slippage_bps for s in snapshots), Decimal("0"))
        return total / Decimal(len(snapshots))

    def _validate_found(self, found: Mapping[str, object]) -> None:
        """搜索结果白名单/候选校验（第二道闸：拦截风控硬阈值等越权参数）。"""
        for key, value in found.items():
            if key not in self._whitelist:
                raise ExecutionOptimizerError(f"搜索结果含白名单外参数 {key!r}（风控硬阈值拦截，禁止自动优化）")
            spec = self._space.get(key)
            if spec is None:
                raise ExecutionOptimizerError(f"搜索结果含未声明参数 {key!r}")
            if value not in spec.candidates:
                raise ExecutionOptimizerError(f"参数 {key!r} 取值 {value!r} 不在候选空间")

    def _grid_search(self, objective: Callable[[Mapping[str, object]], Decimal]) -> tuple[dict, Decimal]:
        """降级网格搜索：按 (参数名, 候选声明序) 确定性遍历，取最小目标。"""
        names = sorted(self._space)
        best_params: dict | None = None
        best_value: Decimal | None = None
        for combo in itertools.product(*(self._space[n].candidates for n in names)):
            params = dict(zip(names, combo, strict=True))
            value = objective(params)
            if best_value is None or value < best_value:
                best_value = value
                best_params = params
        assert best_params is not None and best_value is not None  # 候选非空已校验
        return best_params, best_value

    # ── 周期优化 ──────────────────────────────────────────────────────────

    def run_cycle(self, cycle_id: str) -> OptimizationProposal:
        """周期优化：读 TCA → 搜索（optuna 注入/降级网格）→ 提案入人工确认队列。"""
        if not cycle_id:
            raise ExecutionOptimizerError("cycle_id 为空")
        proposal_id = f"PROP-{cycle_id}"
        if proposal_id in self._proposals:
            raise ExecutionOptimizerError(f"cycle_id 重复: {cycle_id!r}")
        if self._tca_reader is None:
            raise ExecutionOptimizerError("tca_reader 未注入（周期读 TCA 为硬依赖，Fail-Closed）")
        snapshots = tuple(self._tca_reader())
        if not snapshots:
            raise ExecutionOptimizerError("TCA 读数为空（无法计算目标函数）")

        def objective(params: Mapping[str, object]) -> Decimal:
            return self._objective(params, snapshots)

        source = "grid"
        params: dict | None = None
        best_value: Decimal | None = None
        if self._study_runner is not None:
            try:
                found = self._study_runner(dict(self._space), objective)
                self._validate_found(found)
            except ExecutionOptimizerError:
                raise  # 白名单拦截属硬约束，不降级
            except Exception:  # noqa: BLE001 — optuna 异常降级网格搜索（蓝图 §0）
                _log.warning("study_runner 异常，降级网格搜索: cycle=%s", cycle_id, exc_info=True)
            else:
                params = dict(self._defaults)
                params.update(found)
                best_value = objective(params)
                source = "optuna"
        if params is None:
            params, best_value = self._grid_search(objective)

        proposal = OptimizationProposal(
            proposal_id=proposal_id,
            params=params,
            objective_value=best_value,
            source=source,
            created_at=self._clock(),
            status=ProposalStatus.PENDING,
        )
        self._proposals[proposal_id] = proposal
        _log.info(
            "优化提案入人工确认队列: %s source=%s objective=%s",
            proposal_id,
            source,
            best_value,
        )
        return proposal

    # ── 人工确认队列（硬约束：未确认不生效） ───────────────────────────────

    def _pending_of(self, proposal_id: str, operator: str) -> OptimizationProposal:
        if not operator:
            raise ExecutionOptimizerError("操作人为空")
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            raise ExecutionOptimizerError(f"未知提案: {proposal_id!r}")
        if proposal.status is not ProposalStatus.PENDING:
            raise ExecutionOptimizerError(
                f"非法状态迁移: 提案 {proposal_id!r} 当前 {proposal.status.value}，须 PENDING"
            )
        return proposal

    def confirm(self, proposal_id: str, confirmed_by: str) -> None:
        """人工确认：仅 PENDING 可确认；确认后提案参数才生效（硬约束）。"""
        proposal = self._pending_of(proposal_id, confirmed_by)
        self._proposals[proposal_id] = replace(proposal, status=ProposalStatus.CONFIRMED)
        self._active = dict(proposal.params)
        _log.info("提案已人工确认生效: %s (operator=%s)", proposal_id, confirmed_by)
        self._audit(
            {
                "event": "proposal_confirmed",
                "proposal_id": proposal_id,
                "operator": confirmed_by,
                "at": self._clock(),
            }
        )

    def reject(self, proposal_id: str, rejected_by: str) -> None:
        """人工驳回：仅 PENDING 可驳回；生效参数保持不变。"""
        proposal = self._pending_of(proposal_id, rejected_by)
        self._proposals[proposal_id] = replace(proposal, status=ProposalStatus.REJECTED)
        _log.info("提案已人工驳回: %s (operator=%s)", proposal_id, rejected_by)
        self._audit(
            {
                "event": "proposal_rejected",
                "proposal_id": proposal_id,
                "operator": rejected_by,
                "at": self._clock(),
            }
        )

    # ── 查询 ─────────────────────────────────────────────────────────────

    def active_params(self) -> dict:
        """当前生效参数（未经人工确认前恒为默认首候选）。"""
        return dict(self._active)

    def proposal_status(self, proposal_id: str) -> ProposalStatus:
        """单提案状态查询（未知 → Fail-Closed）。"""
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            raise ExecutionOptimizerError(f"未知提案: {proposal_id!r}")
        return proposal.status

    def pending_proposals(self) -> list[OptimizationProposal]:
        """待确认提案（按 (created_at, proposal_id) 确定性排序）。"""
        out = [p for p in self._proposals.values() if p.status is ProposalStatus.PENDING]
        out.sort(key=lambda p: (p.created_at, p.proposal_id))
        return out
