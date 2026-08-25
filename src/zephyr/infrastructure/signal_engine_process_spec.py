# [BLUEPRINT] MOD-INF-070 | docs/03_modules/_domain_infrastructure_runtime/signal_engine_process/blueprint.md | §
# [MODULE] zephyr.infrastructure.signal_engine_process_spec
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.redis_state_layer_ssot; zephyr.infrastructure.process_supervisor
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] P2 进程规格唯一真源=A9 运维架构 §1.1.1/§1.1.3; 畸形规格 Fail-Closed; core_degrade 语义不可放宽（交易时段告警+P3缓存信号）; 心跳 TTL 规则复用 MOD-INF-063 不重造; 系统级设置仅声明不执行
# [MODIFY-GUARD] tests/infrastructure/test_signal_engine_process_spec.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SignalEngineSpecError(未登记错误码-申请中)
# [TESTS] tests/infrastructure/test_signal_engine_process_spec.py
# [A_module] module_id=MOD-INF-070 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""P2 信号引擎进程规格 SSOT（MOD-INF-070）——signal_engine 独立进程参数唯一真源。

真源：A9 运维架构 §1.1.1 进程矩阵（P2 行）+ §1.1.3 健康检查（P2 行）+
CAND-H1FS-006（B14-04523）。

职责边界：与 P3 规格 MOD-INF-064 同族的 P2 补件——MOD-INF-066
process_supervisor 的 FIVE_PROCESS_REGISTRY 已含 P2 注册行（启停编排面），
本模块收口 P2 进程规格深件声明，两真源双向对账防漂移：
  - 四职责：因子计算 / 信号生成 / 策略路由 / 市场状态判定
  - 核 4-7 亲和（SetProcessAffinityMask 属 Owner 窗口）
  - 内存 16GB 峰值上限
  - 分级心跳 hb:signal_engine 5s/30s（TTL=超时+30s 缓冲，规则复用 MOD-INF-063）
  - 崩溃策略 core_degrade：交易时段告警 + P3 使用缓存信号降级（不可放宽）；
    非交易时段自动重启（3 次上限，上限真源归 MOD-INF-066）
  - 产出通道（§1.2.1/§2.4.2 规则2）：signal:* Pub/Sub（TTL 60s）+
    market:state:current 单向传 Hot，P3 订阅消费

硬边界：核亲和/内存硬限/进程 spawn 等系统级动作属 Owner 窗口与
MOD-INF-016 ProcessLifecycleGateway，本模块只产出配置声明，AI 不执行。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from zephyr.infrastructure.redis_state_layer_ssot import get_namespace

__all__: Final = [
    "SIGNAL_ENGINE_SPEC",
    "SignalEngineProcessSpec",
    "SignalEngineSpecError",
    "check_supervisor_alignment",
    "heartbeat_key",
    "heartbeat_ttl_seconds",
    "render_process_spec_declaration",
]


class SignalEngineSpecError(RuntimeError):
    """P2 进程规格畸形或 core_degrade 语义放宽尝试（Fail-Closed）。"""


#: P2 恒为 core_degrade（A9 §1.1.3 P2 行）；critical_no_restart 属 P3（HC-01）、
#: non_core 属 P4/P5，出现在 P2 规格即畸形。
_P2_RESTART_CLASS: Final[str] = "core_degrade"


@dataclass(frozen=True)
class SignalEngineProcessSpec:
    """P2 signal_engine 进程规格（A9 §1.1.1/§1.1.3 唯一真源，frozen 不可变）。

    core_degrade 约束：restart_class="core_degrade" 时 trading_hours_degrade
    必须为 "alert_and_p3_cached_signal"——交易时段不自动重启，告警 + P3 使用
    缓存信号降级（§1.1.3 P2 行不健康动作，不可放宽）。
    """

    process_id: str = "P2"
    process_name: str = "signal_engine"
    priority: int = 20  # 数值越小优先级越高（A9 §1.1）
    duties: tuple[str, ...] = ("因子计算", "信号生成", "策略路由", "市场状态判定")
    cpu_cores: tuple[int, ...] = (4, 5, 6, 7)
    memory_budget_gb: int = 16
    heartbeat_interval_s: int = 5
    heartbeat_timeout_s: int = 30
    restart_class: str = "core_degrade"
    trading_hours_degrade: str = "alert_and_p3_cached_signal"
    max_restart_attempts: int = 3  # 非交易时段自动重启上限（真源归 MOD-INF-066 §3.1）
    signal_key_pattern: str = "signal:{strategy_id}:{date}"  # §1.2.1 signal 命名空间
    signal_ttl_seconds: int = 60  # §1.2 signal=60s
    market_state_key: str = "market:state:current"  # §1.2.1 market_state 命名空间

    def __post_init__(self) -> None:
        if not self.duties:
            raise SignalEngineSpecError("P2 职责列表为空（四职责缺项属畸形规格）")
        if self.heartbeat_interval_s >= self.heartbeat_timeout_s:
            raise SignalEngineSpecError(
                f"心跳间隔 {self.heartbeat_interval_s}s 必须小于超时 {self.heartbeat_timeout_s}s"
            )
        if len(set(self.cpu_cores)) != len(self.cpu_cores):
            raise SignalEngineSpecError(f"CPU 核号重复: {self.cpu_cores}")
        if any(core < 0 for core in self.cpu_cores):
            raise SignalEngineSpecError(f"CPU 核号越界: {self.cpu_cores}")
        if self.memory_budget_gb <= 0:
            raise SignalEngineSpecError(f"内存预算非正: {self.memory_budget_gb}GB")
        if self.restart_class != _P2_RESTART_CLASS:
            raise SignalEngineSpecError(
                f"P2 恒 core_degrade（收到 {self.restart_class!r}；"
                "critical_no_restart 属 P3 HC-01、non_core 属 P4/P5）"
            )
        if self.trading_hours_degrade != "alert_and_p3_cached_signal":
            raise SignalEngineSpecError(
                "core_degrade 不可放宽：交易时段降级语义必须 alert_and_p3_cached_signal"
                f"（收到 {self.trading_hours_degrade!r}）"
            )
        if self.max_restart_attempts <= 0:
            raise SignalEngineSpecError(f"重启上限非正: {self.max_restart_attempts}")
        if self.signal_ttl_seconds <= 0:
            raise SignalEngineSpecError(f"信号 TTL 非正: {self.signal_ttl_seconds}s")


SIGNAL_ENGINE_SPEC: Final[SignalEngineProcessSpec] = SignalEngineProcessSpec()


def heartbeat_key() -> str:
    """P2 心跳键：hb:signal_engine（A9 §1.1.3）。"""
    return f"hb:{SIGNAL_ENGINE_SPEC.process_name}"


def heartbeat_ttl_seconds() -> int:
    """心跳 TTL = 超时阈值 + 30s 缓冲（规则复用 MOD-INF-063 dynamic_ttl，不重造）。"""
    hb_spec = get_namespace("hb")
    assert hb_spec.dynamic_ttl is not None  # MOD-INF-063 一致性自检保证
    return hb_spec.dynamic_ttl(SIGNAL_ENGINE_SPEC.heartbeat_timeout_s)


def check_supervisor_alignment() -> SignalEngineProcessSpec:
    """与 MOD-INF-066 FIVE_PROCESS_REGISTRY P2 注册行双向对账（漂移即 Fail-Closed）。

    两真源分工：supervisor 管 P1~P5 启停编排面，本模块管 P2 规格深件面；
    共有字段（优先级/核/内存/心跳/职责）必须一致，防两真源各自漂移。
    """
    from zephyr.infrastructure.process_supervisor import get_process_spec

    spec = SIGNAL_ENGINE_SPEC
    row = get_process_spec(spec.process_id)
    mismatches: list[str] = []
    if row.process_name != spec.process_name:
        mismatches.append(f"process_name: {row.process_name!r} != {spec.process_name!r}")
    if row.priority != spec.priority:
        mismatches.append(f"priority: {row.priority} != {spec.priority}")
    if row.cpu_cores != spec.cpu_cores:
        mismatches.append(f"cpu_cores: {row.cpu_cores} != {spec.cpu_cores}")
    if row.memory_budget_gb != spec.memory_budget_gb:
        mismatches.append(f"memory_budget_gb: {row.memory_budget_gb} != {spec.memory_budget_gb}")
    if row.heartbeat_interval_s != spec.heartbeat_interval_s:
        mismatches.append(
            f"heartbeat_interval_s: {row.heartbeat_interval_s} != {spec.heartbeat_interval_s}"
        )
    if row.heartbeat_timeout_s != spec.heartbeat_timeout_s:
        mismatches.append(
            f"heartbeat_timeout_s: {row.heartbeat_timeout_s} != {spec.heartbeat_timeout_s}"
        )
    if row.duties != "/".join(spec.duties):
        mismatches.append(f"duties: {row.duties!r} != {'/'.join(spec.duties)!r}")
    if row.restart_class != spec.restart_class:
        mismatches.append(f"restart_class: {row.restart_class!r} != {spec.restart_class!r}")
    if mismatches:
        raise SignalEngineSpecError(
            "P2 规格与 MOD-INF-066 注册行漂移（两真源对账失败）: " + "; ".join(mismatches)
        )
    return spec


def render_process_spec_declaration(
    spec: SignalEngineProcessSpec = SIGNAL_ENGINE_SPEC,
) -> dict:
    """产出 P2 进程配置就绪件声明 dict（**仅声明不执行**——Owner 窗口）。"""
    return {
        "process_id": spec.process_id,
        "process_name": spec.process_name,
        "priority": spec.priority,
        "duties": list(spec.duties),
        "cpu_cores": list(spec.cpu_cores),
        "memory_budget_gb": spec.memory_budget_gb,
        "heartbeat": {
            "key": f"hb:{spec.process_name}",
            "interval_s": spec.heartbeat_interval_s,
            "timeout_s": spec.heartbeat_timeout_s,
            "probe": "信号产出计数器",
        },
        "restart": {
            "restart_class": spec.restart_class,
            "trading_hours_degrade": spec.trading_hours_degrade,
            "max_restart_attempts": spec.max_restart_attempts,
        },
        "output_channels": {
            "signal_pubsub": "signal:*",
            "signal_key_pattern": spec.signal_key_pattern,
            "signal_ttl_seconds": spec.signal_ttl_seconds,
            "market_state": spec.market_state_key,
            "direction": "warm_to_hot_one_way",  # §2.4.2 规则2：P3 订阅消费
        },
        "execution_boundary": "declaration_only_owner_window",
    }
