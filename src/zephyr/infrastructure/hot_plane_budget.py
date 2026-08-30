# [BLUEPRINT] MOD-INF-065 | docs/03_modules/_domain_infrastructure_runtime/hot_plane/blueprint.md | §
# [MODULE] zephyr.infrastructure.hot_plane_budget
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.trading_core_process_spec
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Hot 平面预算唯一真源=A9 运维架构 §2.2（2/3/5ms 分解累计 2/5/10ms）; 未知阶段/负时延/缺阶段 Fail-Closed; 超限动作=circuit_alert 纯数据判定（执行归 P4）; 资源独占仅声明不执行
# [MODIFY-GUARD] tests/infrastructure/test_hot_plane_budget.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HotPlaneBudgetError(未登记错误码-申请中)
# [TESTS] tests/infrastructure/test_hot_plane_budget.py
# [A_module] module_id=MOD-INF-065 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Hot 平面（<10ms）时延预算与资源独占 SSOT（MOD-INF-065）。

真源：A9 运维架构 §2.2 + CAND-H1FS-005（B14-04542）。

定位：平面标记契约（runtime_plane_tag，MOD-INF-002）与 warm_hot_gate 已有，
本模块落地 10ms 端到端预算分解与隔离措施判定：
  - 2ms Tick→风控触发（Redis 订阅+回调，CPU 亲和核 8-11）
  - 3ms 风控规则评估（预编译规则+零 GC 路径）
  - 5ms 订单构建+下单（miniQMT 连接池复用+预构建订单模板）
  累计 2/5/10ms；任一阶段超限或总和 >10ms → circuit_alert（熔断告警声明，
  告警执行归 P4 编排）。

资源独占声明（§2.2 资源表）：核 8-11 独占绑定 P3（规格对齐 MOD-INF-064）、
P3 禁磁盘 IO（除日志）、miniQMT 连接独占、Redis 本地读路径。

注（§2.2 表注）：10ms 是 Tick 到达后的处理延迟；miniQMT Tick 间隔 3s 是
采样周期，两者不矛盾。

硬边界：核独占/禁磁盘 IO/连接独占等系统级应用属 Owner 窗口，AI 不执行。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: stage_latencies_ms 参数
#   fields: 参数 stage_latencies_ms，类型注解 dict[str, float]
#   code: hot_plane_budget.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① check_budget
#   name_en: check_budget
#   intro: 判定一次 Tick→风控→下单端到端时延是否在 10ms 预算内。
#   desc: 判定一次 Tick→风控→下单端到端时延是否在 10ms 预算内。 Args: stage_latencies_ms: {阶段名: 实测时延 ms}，必须恰好覆盖三阶段。 Ret…；源码 L176-L209
#   inputs: stage_latencies_ms
#   outputs: BudgetVerdict
# - id: A2
#   name_zh: ② render_hot_plane_declaration
#   name_en: render_hot_plane_declaration
#   intro: 产出 Hot 平面配置就绪件声明 dict（YAML 可序列化；仅声明不执行）。
#   desc: 产出 Hot 平面配置就绪件声明 dict（YAML 可序列化；仅声明不执行）。 硬边界：核独占/禁磁盘 IO/连接独占等系统级应用属 Owner 窗口。；源码 L212-L240
#   inputs: 无参数
#   outputs: dict[str, object]
#   （注：A2 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: BudgetVerdict
#   name_en: BudgetVerdict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: dict[str, object]
#   name_en: dict[str, object]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

__all__: Final = [
    "HOT_PLANE_BUDGET",
    "BudgetVerdict",
    "HotPlaneBudget",
    "HotPlaneBudgetError",
    "HotPlaneResources",
    "HotPlaneStage",
    "check_budget",
    "render_hot_plane_declaration",
]


class HotPlaneBudgetError(RuntimeError):
    """Hot 平面预算校验失败（未知阶段/负时延/缺阶段，Fail-Closed）。"""


@dataclass(frozen=True)
class HotPlaneStage:
    """Hot 平面单阶段预算（A9 §2.2 表行）。"""

    name: str  # 阶段标识（tick_to_risk/risk_eval/order_build_submit）
    budget_ms: float  # 阶段预算（ms）
    cumulative_budget_ms: float  # 累计预算（ms）
    mechanism: str  # 机制（§2.2 实现列）
    measure: str  # 保障措施（§2.2 备注列）


@dataclass(frozen=True)
class HotPlaneResources:
    """Hot 平面资源独占声明（A9 §2.2 资源表；仅声明不执行）。"""

    p3_cpu_cores_exclusive: tuple[int, ...]  # 核 8-11 独占绑定 P3
    p3_disk_io_forbidden_except_logs: bool  # P3 禁磁盘 IO（除日志）
    miniqmt_connection_exclusive: bool  # miniQMT 连接独占
    redis_local_read_path: bool  # Redis 本地读路径


@dataclass(frozen=True)
class HotPlaneBudget:
    """Hot 平面端到端预算声明（总量 10ms 不可放宽）。"""

    total_budget_ms: float
    stages: tuple[HotPlaneStage, ...]
    resources: HotPlaneResources


@dataclass(frozen=True)
class BudgetVerdict:
    """预算判定结果（纯数据；circuit_alert 执行归 P4 编排）。"""

    within_budget: bool
    total_ms: float
    breached_stages: tuple[str, ...]
    action: str  # "none" | "circuit_alert"


HOT_PLANE_BUDGET: Final[HotPlaneBudget] = HotPlaneBudget(
    total_budget_ms=10.0,
    stages=(
        HotPlaneStage(
            name="tick_to_risk",
            budget_ms=2.0,
            cumulative_budget_ms=2.0,
            mechanism="Redis订阅+回调",
            measure="CPU亲和绑定核8-11",
        ),
        HotPlaneStage(
            name="risk_eval",
            budget_ms=3.0,
            cumulative_budget_ms=5.0,
            mechanism="纯Python规则引擎",
            measure="预编译规则+零GC路径",
        ),
        HotPlaneStage(
            name="order_build_submit",
            budget_ms=5.0,
            cumulative_budget_ms=10.0,
            mechanism="miniQMT API调用",
            measure="连接池复用+预构建订单模板",
        ),
    ),
    resources=HotPlaneResources(
        p3_cpu_cores_exclusive=(8, 9, 10, 11),
        p3_disk_io_forbidden_except_logs=True,
        miniqmt_connection_exclusive=True,
        redis_local_read_path=True,
    ),
)

_STAGE_BY_NAME: Final[dict[str, HotPlaneStage]] = {stage.name: stage for stage in HOT_PLANE_BUDGET.stages}


def check_budget(stage_latencies_ms: dict[str, float]) -> BudgetVerdict:
    """判定一次 Tick→风控→下单端到端时延是否在 10ms 预算内。

    Args:
        stage_latencies_ms: {阶段名: 实测时延 ms}，必须恰好覆盖三阶段。

    Returns:
        BudgetVerdict：within_budget/total_ms/breached_stages/action
        （action="circuit_alert" 为纯数据声明，熔断告警执行归 P4）。

    Raises:
        HotPlaneBudgetError: 未知阶段/缺阶段/负时延（Fail-Closed）。
    """
    unknown = set(stage_latencies_ms) - set(_STAGE_BY_NAME)
    if unknown:
        raise HotPlaneBudgetError(f"未知 Hot 平面阶段: {sorted(unknown)}")
    missing = set(_STAGE_BY_NAME) - set(stage_latencies_ms)
    if missing:
        raise HotPlaneBudgetError(f"Hot 平面阶段缺项: {sorted(missing)}")
    for name, value in stage_latencies_ms.items():
        if value < 0:
            raise HotPlaneBudgetError(f"阶段 {name} 时延为负: {value}")

    breached = tuple(
        stage.name for stage in HOT_PLANE_BUDGET.stages if stage_latencies_ms[stage.name] > stage.budget_ms
    )
    total_ms = sum(stage_latencies_ms[stage.name] for stage in HOT_PLANE_BUDGET.stages)
    within = not breached and total_ms <= HOT_PLANE_BUDGET.total_budget_ms
    return BudgetVerdict(
        within_budget=within,
        total_ms=total_ms,
        breached_stages=breached,
        action="none" if within else "circuit_alert",
    )


def render_hot_plane_declaration() -> dict[str, object]:
    """产出 Hot 平面配置就绪件声明 dict（YAML 可序列化；仅声明不执行）。

    硬边界：核独占/禁磁盘 IO/连接独占等系统级应用属 Owner 窗口。
    """
    budget = HOT_PLANE_BUDGET
    return {
        "plane": "HOT",
        "total_budget_ms": budget.total_budget_ms,
        "stages": [
            {
                "name": stage.name,
                "budget_ms": stage.budget_ms,
                "cumulative_budget_ms": stage.cumulative_budget_ms,
                "mechanism": stage.mechanism,
                "measure": stage.measure,
            }
            for stage in budget.stages
        ],
        "resources": {
            "p3_cpu_cores_exclusive": list(budget.resources.p3_cpu_cores_exclusive),
            "p3_disk_io_forbidden_except_logs": budget.resources.p3_disk_io_forbidden_except_logs,
            "miniqmt_connection_exclusive": budget.resources.miniqmt_connection_exclusive,
            "redis_local_read_path": budget.resources.redis_local_read_path,
        },
        "breach_action": "circuit_alert",
        "applied_by_ai": False,
        "apply_boundary": "核独占/禁磁盘 IO/连接独占等系统级设置属 Owner 窗口执行，本声明仅供审阅应用",
    }
