# [BLUEPRINT] MOD-INF-071 | docs/03_modules/_domain_infrastructure_runtime/warm_plane/blueprint.md | §
# [MODULE] zephyr.infrastructure.warm_plane_budget
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.redis_state_layer_ssot
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Warm 平面预算唯一真源=A9 运维架构 §2.3（200/300/500ms 分解累计 200/500/1000ms）; 11 态路由表唯一真源=§2.3.2（7 行权重Σ=1）; 未知阶段/负时延/缺阶段/未知状态码 Fail-Closed; 超 1s 信号=过期→P3 用缓存信号（纯数据判定）; 系统级隔离仅声明不执行
# [MODIFY-GUARD] tests/infrastructure/test_warm_plane_budget.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] WarmPlaneBudgetError+WarmPlaneRoutingError(未登记错误码-申请中)
# [TESTS] tests/infrastructure/test_warm_plane_budget.py
# [A_module] module_id=MOD-INF-071 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Warm 平面（10ms~1s）时延预算与 11 态路由表 SSOT（MOD-INF-071）。

真源：A9 运维架构 §2.3 + CAND-H1FS-007（B14-04547）。

定位：与 Hot 档 MOD-INF-065 同族衔接的 Warm 档补件——平面标记契约
（runtime_plane_tag，MOD-INF-002）与 warm_hot_gate 已有，本模块落地
Warm 1s 端到端预算分解与 11 种市场状态路由表：
  - 200ms 增量因子计算（NumPy/Pandas 向量化 + GPU 批量加速）
  - 300ms 信号生成+聚合（多策略并行 + 进程内线程池）
  - 500ms 策略路由+仓位裁决（市场状态驱动路由 + Redis 缓存市场状态）
  累计 200/500/1000ms；任一阶段超限或总和 >1s → stale_signal_use_cache
  （超 1s 信号视为过期信号，P3 使用缓存信号替代——04-D-SIGNAL §8.1 硬约束，
  判定为纯数据，执行归 P3/P4）。

路由表（§2.3.2，7 行 11 态）：①②趋势向上 / ③高波动 / ④⑤震荡 /
⑥压缩突破 / ⑦⑧⑨趋势向下 / ⑩事件驱动 / ⑪板块轮动——每行路由策略 +
信号权重（Σ=1.0 Fail-Closed 校验）+ 仓位上限（区间或按事件调整 None）。

单向通道（§2.4.2 规则2）：Warm→Hot 仅经 Redis signal:* Pub/Sub +
market:state 传递，P3 订阅消费；Cold→Hot 禁止直连。

硬边界：核绑定/资源隔离/进程调度等系统级应用属 Owner 窗口，AI 不执行。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: measured_ms 参数
#   fields: 参数 measured_ms，类型注解 dict[str, float]
#   code: warm_plane_budget.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: state_code 参数
#   fields: 参数 state_code，类型注解 str
#   code: warm_plane_budget.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① check_budget
#   name_en: check_budget
#   intro: Warm 平面预算判定（A9 §2.3.1；纯数据判定，过期信号替换执行归 P3/P4）。
#   desc: Warm 平面预算判定（A9 §2.3.1；纯数据判定，过期信号替换执行归 P3/P4）。 任一阶段超限或总和 >1000ms → within_budget=False， 动作…；源码 L278-L308
#   inputs: measured_ms
#   outputs: BudgetVerdict
# - id: A2
#   name_zh: ② get_routing
#   name_en: get_routing
#   intro: 按市场状态码（①~⑪）取路由行；未知状态码 Fail-Closed。
#   desc: 按市场状态码（①~⑪）取路由行；未知状态码 Fail-Closed。；源码 L311-L316
#   inputs: state_code
#   outputs: MarketStateRouting
# - id: A3
#   name_zh: ③ render_warm_plane_declaration
#   name_en: render_warm_plane_declaration
#   intro: 产出 Warm 平面配置就绪件声明 dict（**仅声明不执行**——Owner 窗口）。
#   desc: 产出 Warm 平面配置就绪件声明 dict（**仅声明不执行**——Owner 窗口）。；源码 L319-L352
#   inputs: 无参数
#   outputs: dict
#   （注：A3 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: BudgetVerdict
#   name_en: BudgetVerdict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: MarketStateRouting
#   name_en: MarketStateRouting
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

__all__: Final = [
    "MARKET_STATE_ROUTING",
    "WARM_PLANE_BUDGET",
    "BudgetVerdict",
    "MarketStateRouting",
    "WarmPlaneBudget",
    "WarmPlaneBudgetError",
    "WarmPlaneRoutingError",
    "WarmPlaneStage",
    "check_budget",
    "get_routing",
    "render_warm_plane_declaration",
]


class WarmPlaneBudgetError(RuntimeError):
    """Warm 平面预算校验失败（未知阶段/负时延/缺阶段，Fail-Closed）。"""


class WarmPlaneRoutingError(RuntimeError):
    """Warm 平面路由表畸形或未知市场状态码（Fail-Closed）。"""


@dataclass(frozen=True)
class WarmPlaneStage:
    """Warm 平面单阶段预算（A9 §2.3.1 表行）。"""

    name: str  # 阶段标识（incremental_factor_compute/signal_gen_aggregate/strategy_route_position）
    budget_ms: float  # 阶段预算（ms）
    cumulative_budget_ms: float  # 累计预算（ms）
    mechanism: str  # 机制（§2.3.1 实现列）
    measure: str  # 优化手段（§2.3.1 备注列）


@dataclass(frozen=True)
class WarmPlaneBudget:
    """Warm 平面端到端预算（A9 §2.3.1 唯一真源，frozen 不可变）。"""

    stages: tuple[WarmPlaneStage, ...]
    total_budget_ms: float = 1000.0


@dataclass(frozen=True)
class BudgetVerdict:
    """预算判定结果（纯数据；过期信号替换执行归 P3/P4 编排）。"""

    within_budget: bool
    overrun_stages: tuple[str, ...]
    action: str  # "none" | "stale_signal_use_cache"
    reason: str


@dataclass(frozen=True)
class MarketStateRouting:
    """市场状态路由行（A9 §2.3.2 表行，frozen 不可变）。

    position_cap_range: (下限, 上限) 仓位上限区间；单值=两端相同；
    None=按事件调整（⑩事件驱动行，仓位由事件面裁决不预设）。
    """

    state_codes: tuple[str, ...]  # 覆盖的市场状态码（①~⑪ 子集）
    state_label: str  # 状态名（趋势向上/高波动/...）
    route_strategy: str  # 路由策略标识
    signal_weights: dict[str, float]  # 信号权重（Σ=1.0 校验）
    position_cap_range: tuple[float, float] | None


WARM_PLANE_BUDGET: Final[WarmPlaneBudget] = WarmPlaneBudget(
    stages=(
        WarmPlaneStage(
            name="incremental_factor_compute",
            budget_ms=200.0,
            cumulative_budget_ms=200.0,
            mechanism="NumPy/Pandas向量化",
            measure="GPU加速因子批量计算",
        ),
        WarmPlaneStage(
            name="signal_gen_aggregate",
            budget_ms=300.0,
            cumulative_budget_ms=500.0,
            mechanism="多策略并行",
            measure="进程内线程池",
        ),
        WarmPlaneStage(
            name="strategy_route_position",
            budget_ms=500.0,
            cumulative_budget_ms=1000.0,
            mechanism="市场状态驱动路由",
            measure="Redis缓存市场状态",
        ),
    )
)

MARKET_STATE_ROUTING: Final[tuple[MarketStateRouting, ...]] = (
    MarketStateRouting(
        state_codes=("①", "②"),
        state_label="趋势向上",
        route_strategy="momentum_first",
        signal_weights={"momentum": 0.6, "value": 0.2, "defense": 0.2},
        position_cap_range=(0.80, 0.80),
    ),
    MarketStateRouting(
        state_codes=("③",),
        state_label="高波动",
        route_strategy="t0_activate",
        signal_weights={"momentum": 0.3, "t0": 0.4, "defense": 0.3},
        position_cap_range=(0.60, 0.60),
    ),
    MarketStateRouting(
        state_codes=("④", "⑤"),
        state_label="震荡",
        route_strategy="mean_reversion_first",
        signal_weights={"mean_reversion": 0.5, "value": 0.3, "defense": 0.2},
        position_cap_range=(0.50, 0.50),
    ),
    MarketStateRouting(
        state_codes=("⑥",),
        state_label="压缩突破",
        route_strategy="breakout_standby",
        signal_weights={"momentum": 0.4, "mean_reversion": 0.3, "breakout": 0.3},
        position_cap_range=(0.40, 0.70),  # 突破确认后 40%→70%
    ),
    MarketStateRouting(
        state_codes=("⑦", "⑧", "⑨"),
        state_label="趋势向下",
        route_strategy="defense_dominant",
        signal_weights={"defense": 0.6, "value": 0.3, "momentum": 0.1},
        position_cap_range=(0.10, 0.30),  # 随趋势恶化 30%→10%
    ),
    MarketStateRouting(
        state_codes=("⑩",),
        state_label="事件驱动",
        route_strategy="event_activate",
        signal_weights={"event": 0.5, "momentum": 0.3, "defense": 0.2},
        position_cap_range=None,  # 按事件调整（§2.3.2 表注）
    ),
    MarketStateRouting(
        state_codes=("⑪",),
        state_label="板块轮动",
        route_strategy="rotation_activate",
        signal_weights={"rotation": 0.5, "momentum": 0.3, "value": 0.2},
        position_cap_range=(0.70, 0.70),
    ),
)

_STAGE_BY_NAME: Final[dict[str, WarmPlaneStage]] = {stage.name: stage for stage in WARM_PLANE_BUDGET.stages}

_ROUTING_BY_CODE: Final[dict[str, MarketStateRouting]] = {
    code: row for row in MARKET_STATE_ROUTING for code in row.state_codes
}

_WEIGHT_SUM_TOLERANCE: Final[float] = 1e-9


def _validate_routing_table() -> None:
    """路由表自检（导入即跑，畸形即 Fail-Closed）：权重Σ=1/仓位区间合法/11 态唯一。"""
    seen: set[str] = set()
    for row in MARKET_STATE_ROUTING:
        total = sum(row.signal_weights.values())
        if abs(total - 1.0) > _WEIGHT_SUM_TOLERANCE:
            raise WarmPlaneRoutingError(f"路由行 {row.state_label} 信号权重 Σ={total} ≠ 1.0（§2.3.2 真源畸形）")
        if any(w < 0.0 for w in row.signal_weights.values()):
            raise WarmPlaneRoutingError(f"路由行 {row.state_label} 存在负权重")
        if row.position_cap_range is not None:
            lo, hi = row.position_cap_range
            if not (0.0 <= lo <= hi <= 1.0):
                raise WarmPlaneRoutingError(f"路由行 {row.state_label} 仓位上限区间越界: {row.position_cap_range}")
        for code in row.state_codes:
            if code in seen:
                raise WarmPlaneRoutingError(f"市场状态码 {code} 重复映射（11 态须唯一）")
            seen.add(code)
    if len(seen) != 11:
        raise WarmPlaneRoutingError(f"市场状态码覆盖数 {len(seen)} ≠ 11（§2.3.2 真源畸形）")


_validate_routing_table()


def check_budget(measured_ms: dict[str, float]) -> BudgetVerdict:
    """Warm 平面预算判定（A9 §2.3.1；纯数据判定，过期信号替换执行归 P3/P4）。

    任一阶段超限或总和 >1000ms → within_budget=False，
    动作=stale_signal_use_cache（超 1s 信号视为过期，P3 使用缓存信号替代）。
    """
    unknown = set(measured_ms) - set(_STAGE_BY_NAME)
    if unknown:
        raise WarmPlaneBudgetError(f"未知 Warm 平面阶段: {sorted(unknown)}")
    missing = set(_STAGE_BY_NAME) - set(measured_ms)
    if missing:
        raise WarmPlaneBudgetError(f"缺阶段时延: {sorted(missing)}（缺项属畸形输入）")
    if any(v < 0 for v in measured_ms.values()):
        raise WarmPlaneBudgetError(f"负时延属畸形输入: {measured_ms}")

    overrun = tuple(name for name, stage in _STAGE_BY_NAME.items() if measured_ms[name] > stage.budget_ms)
    total = sum(measured_ms.values())
    within = not overrun and total <= WARM_PLANE_BUDGET.total_budget_ms
    if within:
        return BudgetVerdict(within_budget=True, overrun_stages=(), action="none", reason="全程在 1s 预算内")
    reasons: list[str] = []
    if overrun:
        reasons.append(f"阶段超限: {list(overrun)}")
    if total > WARM_PLANE_BUDGET.total_budget_ms:
        reasons.append(f"端到端 {total:.1f}ms > {WARM_PLANE_BUDGET.total_budget_ms:.0f}ms")
    return BudgetVerdict(
        within_budget=False,
        overrun_stages=overrun,
        action="stale_signal_use_cache",
        reason="; ".join(reasons) + " → 信号视为过期，P3 使用缓存信号替代",
    )


def get_routing(state_code: str) -> MarketStateRouting:
    """按市场状态码（①~⑪）取路由行；未知状态码 Fail-Closed。"""
    row = _ROUTING_BY_CODE.get(state_code)
    if row is None:
        raise WarmPlaneRoutingError(f"未知市场状态码: {state_code!r}（11 态真源=A9 §2.3.2）")
    return row


def render_warm_plane_declaration() -> dict:
    """产出 Warm 平面配置就绪件声明 dict（**仅声明不执行**——Owner 窗口）。"""
    return {
        "plane": "warm",
        "latency_band": "10ms~1s",
        "stages": [
            {
                "name": stage.name,
                "budget_ms": stage.budget_ms,
                "cumulative_budget_ms": stage.cumulative_budget_ms,
                "mechanism": stage.mechanism,
                "measure": stage.measure,
            }
            for stage in WARM_PLANE_BUDGET.stages
        ],
        "total_budget_ms": WARM_PLANE_BUDGET.total_budget_ms,
        "stale_signal_action": "stale_signal_use_cache",
        "routing_table": [
            {
                "state_codes": list(row.state_codes),
                "state_label": row.state_label,
                "route_strategy": row.route_strategy,
                "signal_weights": dict(row.signal_weights),
                "position_cap_range": (list(row.position_cap_range) if row.position_cap_range is not None else None),
            }
            for row in MARKET_STATE_ROUTING
        ],
        "egress": {
            "signal_pubsub": "signal:*",
            "market_state": "market:state:current",
            "direction": "warm_to_hot_one_way",  # §2.4.2 规则2：P3 订阅消费
        },
        "execution_boundary": "declaration_only_owner_window",
    }
