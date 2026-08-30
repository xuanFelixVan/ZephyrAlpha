# [BLUEPRINT] MOD-PLAN-023 | docs/03_modules/_domain_plan_engine/premarket_workflow_engine/blueprint.md
# [MODULE] zephyr.plan_engine.premarket_workflow_engine
# [DOMAIN] D_PLAN
# [DEPENDENCIES] 无（编排核心纯内存；六工序handler/时钟全注入）
# [CONSUMERS] 运行时装配批（盘前SOP六工序handler绑定 / 人工接管确认回路接线）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 六工序词表闭合并按定义序执行(数据同步→隔夜复盘→情绪扫描→预案生成→盘前检查→就绪确认); handler缺失/多键/不可调用Fail-Closed; 工序失败阻断(后续SKIPPED); 人工接管点标记后暂停等确认(批准续跑/否决阻断); handler产出须str|None; 耗时=clock注入差值逐工序统计; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_plan_engine/premarket_workflow_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PremarketWorkflowError(占位 ZA-PLAN-UNREGISTERED-PREMARKET-WORKFLOW)——handler词表非法/空trading_date/等待中并发启动/无等待点确认/产出类型非法时抛
# [TESTS] tests/plan_engine/test_premarket_workflow_engine.py
# [A_module] module_id=MOD-PLAN-023 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
PremarketWorkflowEngine — 盘前标准化工作流引擎（MOD-PLAN-023）。

B14-04681（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PLAN-017，A9 D-TRADING-15）：
盘前标准**六工序编排**——数据同步 → 隔夜复盘 → 情绪扫描 → 预案生成 →
盘前检查 → 就绪确认（工序 handler 注入，产出可流转下游工序）。

- **失败阻断**：任一工序 handler 抛异常 → 该工序 FAILED，后续工序
  SKIPPED，blocked_step 留痕；
- **人工接管点**：标记工序（默认=就绪确认）到达即暂停 WAITING_MANUAL，
  等 confirm_manual 确认——批准续跑 / 否决阻断；
- **耗时统计**：逐工序 started/finished/duration（clock 注入差值），
  报告汇总总耗时。

查重分工（蓝图 §0）：premarket_workflow（MOD-PLAN-021）=08:00-09:15 三
段式**分钟级排程 DAG**（复用 WorkDAG，重排程窗口/段序）；本件=**六工序
handler 编排**（重 handler 注入/人工接管点/耗时统计），不重造排程 DAG。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: handlers 参数
#   fields: 参数 handlers（无注解）
#   code: premarket_workflow_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: premarket_workflow_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: manual_steps 参数
#   fields: 参数 manual_steps（无注解）
#   code: premarket_workflow_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① PremarketWorkflowEngine
#   name_en: PremarketWorkflowEngine
#   intro: 盘前六工序编排引擎（handler/时钟注入，纯内存确定性）。
#   desc: 盘前六工序编排引擎（handler/时钟注入，纯内存确定性）。；公共方法（定义序）: run, confirm_manual；源码 L167-L326
#   inputs: handlers clock manual_steps
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: PremarketWorkflowEngine
#   downstream: 运行时装配批（盘前SOP六工序handler绑定 / 人工接管确认回路接线）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "PremarketWorkflowEngine",
    "PremarketWorkflowError",
    "StepRecord",
    "StepStatus",
    "WorkflowContext",
    "WorkflowReport",
    "WorkflowStepId",
]

_SKIP_DETAIL: Final = "前序失败阻断跳过"


class PremarketWorkflowError(Exception):
    """盘前工作流引擎输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-PLAN-UNREGISTERED-PREMARKET-WORKFLOW。
    """


class WorkflowStepId(str, Enum):
    """盘前六工序（定义序即执行序，词表闭合）。"""

    DATA_SYNC = "data_sync"  # 数据同步
    OVERNIGHT_REVIEW = "overnight_review"  # 隔夜复盘
    SENTIMENT_SCAN = "sentiment_scan"  # 情绪扫描
    PLAN_GENERATION = "plan_generation"  # 预案生成
    PREMARKET_CHECK = "premarket_check"  # 盘前检查
    READINESS_CONFIRM = "readiness_confirm"  # 就绪确认


_STEP_ORDER: Final = tuple(WorkflowStepId)


class StepStatus(str, Enum):
    """工序执行状态。"""

    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING_MANUAL = "waiting_manual"


@dataclass(frozen=True)
class WorkflowContext:
    """工序 handler 入参（交易日 + 前序工序产出，frozen）。"""

    trading_date: str
    step_outputs: Mapping[WorkflowStepId, str]


@dataclass(frozen=True)
class StepRecord:
    """单工序执行记录（frozen）。"""

    step_id: WorkflowStepId
    status: StepStatus
    detail: str
    started_at: datetime.datetime | None
    finished_at: datetime.datetime | None
    duration_seconds: Decimal | None


@dataclass(frozen=True)
class WorkflowReport:
    """工作流报告（frozen，六工序全量记录按工序序）。"""

    trading_date: str
    steps: tuple[StepRecord, ...]
    ready: bool
    waiting_step: WorkflowStepId | None
    blocked_step: WorkflowStepId | None
    total_duration_seconds: Decimal
    started_at: datetime.datetime | None
    finished_at: datetime.datetime | None


def _duration(started: datetime.datetime, finished: datetime.datetime) -> Decimal:
    return Decimal(str((finished - started).total_seconds()))


class PremarketWorkflowEngine:
    """盘前六工序编排引擎（handler/时钟注入，纯内存确定性）。"""

    def __init__(
        self,
        *,
        handlers: Mapping[WorkflowStepId, Callable[[WorkflowContext], str | None]],
        clock: Callable[[], datetime.datetime] | None = None,
        manual_steps: Iterable[WorkflowStepId] | None = None,
    ) -> None:
        if not handlers:
            raise PremarketWorkflowError("handlers 为空（六工序 handler 须注入）")
        expected = set(WorkflowStepId)
        keys = set(handlers)
        missing = expected - keys
        extra = keys - expected
        if missing:
            raise PremarketWorkflowError(f"缺少工序 handler: {[s.value for s in _STEP_ORDER if s in missing]}")
        if extra:
            raise PremarketWorkflowError(f"未知工序 handler 键: {sorted(str(k) for k in extra)}")
        for step_id, handler in handlers.items():
            if not callable(handler):
                raise PremarketWorkflowError(f"工序 handler 不可调用: {step_id!r}")
        manual = set(manual_steps) if manual_steps is not None else {WorkflowStepId.READINESS_CONFIRM}
        for step in manual:
            if not isinstance(step, WorkflowStepId):
                raise PremarketWorkflowError(f"人工接管点未知工序: {step!r}")
        self._handlers = dict(handlers)
        self._clock = clock or datetime.datetime.now
        self._manual_steps = frozenset(manual)
        self._reset()

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _reset(self) -> None:
        self._records: dict[WorkflowStepId, StepRecord] = {}
        self._outputs: dict[WorkflowStepId, str] = {}
        self._waiting_step: WorkflowStepId | None = None
        self._blocked_step: WorkflowStepId | None = None
        self._trading_date: str | None = None
        self._started_at: datetime.datetime | None = None
        self._finished_at: datetime.datetime | None = None
        self._active = False

    def _skip_rest(self, from_index: int) -> None:
        for rest in _STEP_ORDER[from_index:]:
            self._records[rest] = StepRecord(rest, StepStatus.SKIPPED, _SKIP_DETAIL, None, None, None)

    def _execute_from(self, start_index: int) -> None:
        for idx in range(start_index, len(_STEP_ORDER)):
            step = _STEP_ORDER[idx]
            if step in self._manual_steps:
                now = self._clock()
                self._records[step] = StepRecord(step, StepStatus.WAITING_MANUAL, "人工接管点等待确认", now, None, None)
                self._waiting_step = step
                _log.info("盘前工作流人工接管点: %s 等待确认", step.value)
                return
            started = self._clock()
            ctx = WorkflowContext(trading_date=self._trading_date or "", step_outputs=dict(self._outputs))
            try:
                out = self._handlers[step](ctx)
            except Exception as exc:  # noqa: BLE001 — 工序失败阻断（蓝图 §1）
                _log.exception("盘前工序失败: %s", step.value)
                finished = self._clock()
                self._records[step] = StepRecord(
                    step,
                    StepStatus.FAILED,
                    f"{type(exc).__name__}: {exc}",
                    started,
                    finished,
                    _duration(started, finished),
                )
                self._blocked_step = step
                self._skip_rest(idx + 1)
                self._finished_at = finished
                return
            if out is not None and not isinstance(out, str):
                raise PremarketWorkflowError(f"工序产出须为 str|None: {step.value} 返回 {type(out).__name__}")
            finished = self._clock()
            detail = out or ""
            self._records[step] = StepRecord(
                step, StepStatus.DONE, detail, started, finished, _duration(started, finished)
            )
            self._outputs[step] = detail
        self._finished_at = self._clock()

    def _report(self) -> WorkflowReport:
        steps = tuple(
            self._records.get(s, StepRecord(s, StepStatus.PENDING, "", None, None, None)) for s in _STEP_ORDER
        )
        ready = (
            self._active
            and self._waiting_step is None
            and self._blocked_step is None
            and all(r.status is StepStatus.DONE for r in steps)
        )
        total = sum((r.duration_seconds for r in steps if r.duration_seconds is not None), Decimal("0"))
        return WorkflowReport(
            trading_date=self._trading_date or "",
            steps=steps,
            ready=ready,
            waiting_step=self._waiting_step,
            blocked_step=self._blocked_step,
            total_duration_seconds=total,
            started_at=self._started_at,
            finished_at=self._finished_at,
        )

    # ── 编排 ─────────────────────────────────────────────────────────────

    def run(self, trading_date: str) -> WorkflowReport:
        """启动盘前六工序（人工接管点暂停；失败阻断后续跳过）。"""
        if not isinstance(trading_date, str) or not trading_date:
            raise PremarketWorkflowError("trading_date 为空")
        if self._active and self._waiting_step is not None:
            raise PremarketWorkflowError(f"上一轮在人工接管点 {self._waiting_step.value} 等待确认，禁止并发启动")
        self._reset()
        self._active = True
        self._trading_date = trading_date
        self._started_at = self._clock()
        _log.info("盘前工作流启动: %s", trading_date)
        self._execute_from(0)
        return self._report()

    def confirm_manual(self, approved: bool) -> WorkflowReport:
        """人工接管点确认：批准→续跑后续工序；否决→阻断。"""
        if self._waiting_step is None:
            raise PremarketWorkflowError("无等待确认的人工接管点")
        if not isinstance(approved, bool):
            raise PremarketWorkflowError(f"approved 须为 bool: {approved!r}")
        step = self._waiting_step
        self._waiting_step = None
        rec = self._records[step]
        finished = self._clock()
        idx = _STEP_ORDER.index(step)
        if approved:
            self._records[step] = StepRecord(
                step,
                StepStatus.DONE,
                "人工确认通过",
                rec.started_at,
                finished,
                _duration(rec.started_at, finished) if rec.started_at is not None else None,
            )
            self._outputs[step] = "人工确认通过"
            self._execute_from(idx + 1)
        else:
            self._records[step] = StepRecord(
                step,
                StepStatus.FAILED,
                "人工接管否决",
                rec.started_at,
                finished,
                _duration(rec.started_at, finished) if rec.started_at is not None else None,
            )
            self._blocked_step = step
            self._skip_rest(idx + 1)
            self._finished_at = finished
            _log.warning("盘前工作流人工否决: %s", step.value)
        return self._report()
