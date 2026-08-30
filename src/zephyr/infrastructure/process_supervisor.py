# [BLUEPRINT] MOD-INF-066 | docs/03_modules/_domain_infrastructure_runtime/process_supervisor/blueprint.md | §
# [MODULE] zephyr.infrastructure.process_supervisor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.trading_core_process_spec; zephyr.infrastructure.redis_state_layer_ssot
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] P1~P5 编排真源=A9 运维架构 §1.1; 启动升序/关闭降序; P3 先于 P1、P1 先于 Redis 关闭硬约束; HC-01 P3 任何时段不自动重启不可放宽; NSSM 注册/开机自启属 Owner 窗口仅产出就绪件
# [MODIFY-GUARD] tests/infrastructure/test_process_supervisor.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ProcessSupervisorError(未登记错误码-申请中)
# [TESTS] tests/infrastructure/test_process_supervisor.py
# [A_module] module_id=MOD-INF-066 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
NSSM+5 进程架构与自研 Supervisor（MOD-INF-066）——P1~P5 启停编排与崩溃策略唯一真源。

真源：A9 运维架构 §1.1 + CAND-H1FS-002（B14-04521）。

定位：进程守护散件（MOD-INF-035 windows_service/health_monitor/lifecycle_manager、
MOD-INF-039 startup_sequencer）不变；本模块收口 NSSM 服务化定义与五进程优先级
启停编排：
  - 启动=优先级数值升序（P1→P3→P2→P4→P5），关闭=降序（P5→P4→P2→P3→P1）；
    P3 先于 P1 关闭（挂单先撤回），P1 先于 Redis 关闭（末条行情先持久化）。
  - 分级心跳 hb:{process}（TTL=超时+30s 缓冲，规则复用 MOD-INF-063）。
  - 崩溃策略：P3 任何时段不自动重启（HC-01 仅告警+人工）；P1/P2 交易时段
    告警+降级、非交易时段自动重启；P4/P5 自动重启（3 次上限终止重启循环）。
  - 日志托管声明（NSSM AppStdout/AppStderr 落盘）。

硬边界（Owner 窗口）：NSSM 注册、开机自启、计划任务、核亲和、禁 swap 等
系统级动作 AI 一律不执行——本模块只产出配置就绪件（服务定义声明 +
安装脚本草稿文本 + 编排判定代码）；实际 spawn 通道归 MOD-INF-016
ProcessLifecycleGateway（本 MVP 不发起进程）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: process_id 参数
#   fields: 参数 process_id，类型注解 str
#   code: process_supervisor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: is_trading_hours 参数
#   fields: 参数 is_trading_hours（无注解）
#   code: process_supervisor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: consecutive_failures 参数
#   fields: 参数 consecutive_failures（无注解）
#   code: process_supervisor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_process_spec
#   name_en: get_process_spec
#   intro: 按进程 ID 取注册表条目；未知 ID Fail-Closed。
#   desc: 按进程 ID 取注册表条目；未知 ID Fail-Closed。；源码 L283-L288
#   inputs: process_id
#   outputs: SupervisorProcessSpec
# - id: A2
#   name_zh: ② compute_start_order
#   name_en: compute_start_order
#   intro: 启动序列：优先级数值升序（高优先级先启动）→ P1→P3→P2→P4→P5。
#   desc: 启动序列：优先级数值升序（高优先级先启动）→ P1→P3→P2→P4→P5。；源码 L291-L293
#   inputs: 无参数
#   outputs: list[str]
# - id: A3
#   name_zh: ③ compute_shutdown_order
#   name_en: compute_shutdown_order
#   intro: 关闭序列：优先级降序 → P5→P4→P2→P3→P1（P3 先于 P1，挂单先撤回）。
#   desc: 关闭序列：优先级降序 → P5→P4→P2→P3→P1（P3 先于 P1，挂单先撤回）。；源码 L296-L298
#   inputs: 无参数
#   outputs: list[str]
# - id: A4
#   name_zh: ④ shutdown_sequence_with_redis
#   name_en: shutdown_sequence_with_redis
#   intro: 含 Redis 的完整关闭序列：P1 先于 Redis（末条行情先持久化）。
#   desc: 含 Redis 的完整关闭序列：P1 先于 Redis（末条行情先持久化）。；源码 L301-L303
#   inputs: 无参数
#   outputs: list[str]
# - id: A5
#   name_zh: ⑤ heartbeat_key
#   name_en: heartbeat_key
#   intro: 进程心跳键：hb:{process_name}（A9 §1.1.3）。
#   desc: 进程心跳键：hb:{process_name}（A9 §1.1.3）。；源码 L306-L308
#   inputs: process_id
#   outputs: str
# - id: A6
#   name_zh: ⑥ heartbeat_ttl_seconds
#   name_en: heartbeat_ttl_seconds
#   intro: 心跳 TTL = 超时阈值 + 30s 缓冲（规则复用 MOD-INF-063 hb dynamic_ttl，不重造）。
#   desc: 心跳 TTL = 超时阈值 + 30s 缓冲（规则复用 MOD-INF-063 hb dynamic_ttl，不重造）。；源码 L311-L315
#   inputs: process_id
#   outputs: int
# - id: A7
#   name_zh: ⑦ decide_crash_action
#   name_en: decide_crash_action
#   intro: 崩溃重启判定（A9 §1.1.3 + §3.1；纯数据判定，执行归 P4 与 Owner 窗口）。
#   desc: 崩溃重启判定（A9 §1.1.3 + §3.1；纯数据判定，执行归 P4 与 Owner 窗口）。 - P3（critical_no_restart）：HC-01 任何时段不自动…；源码 L318-L351
#   inputs: process_id is_trading_hours consecutive_failures
#   outputs: CrashAction
# - id: A8
#   name_zh: ⑧ check_supervisor_consistency
#   name_en: check_supervisor_consistency
#   intro: 注册表一致性自检：五进程/优先级唯一/心跳不倒挂/核号无重叠/启停序列硬约束。
#   desc: 注册表一致性自检：五进程/优先级唯一/心跳不倒挂/核号无重叠/启停序列硬约束。；源码 L354-L375
#   inputs: 无参数
#   outputs: dict[str, object]
# - id: A9
#   name_zh: ⑨ render_nssm_service_definitions
#   name_en: render_nssm_service_definitions
#   intro: 产出五进程 NSSM 服务定义声明（按启动序列；仅就绪件不执行注册）。
#   desc: 产出五进程 NSSM 服务定义声明（按启动序列；仅就绪件不执行注册）。 硬边界：nssm install/set 注册与开机自启属 Owner 窗口（applied_by_ai=…；源码 L378-L410
#   inputs: 无参数
#   outputs: list[dict[str, object]]
# - id: A10
#   name_zh: ⑩ render_nssm_install_script
#   name_en: render_nssm_install_script
#   intro: 产出 NSSM 安装脚本草稿（PowerShell 文本；DRAFT 仅就绪件，AI 不执行注册）。
#   desc: 产出 NSSM 安装脚本草稿（PowerShell 文本；DRAFT 仅就绪件，AI 不执行注册）。；源码 L413-L436
#   inputs: 无参数
#   outputs: str
#   （注：A10 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: SupervisorProcessSpec
#   name_en: SupervisorProcessSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> A10
# A10 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from zephyr.infrastructure.redis_state_layer_ssot import get_namespace
from zephyr.trading.trading_core_process_spec import TRADING_CORE_SPEC

__all__: Final = [
    "FIVE_PROCESS_REGISTRY",
    "MAX_RESTART_ATTEMPTS",
    "CrashAction",
    "ProcessSupervisorError",
    "SupervisorProcessSpec",
    "check_supervisor_consistency",
    "compute_shutdown_order",
    "compute_start_order",
    "decide_crash_action",
    "get_process_spec",
    "heartbeat_key",
    "heartbeat_ttl_seconds",
    "render_nssm_install_script",
    "render_nssm_service_definitions",
    "shutdown_sequence_with_redis",
]


class ProcessSupervisorError(RuntimeError):
    """Supervisor 校验失败（未知进程/注册表畸形/HC-01 放宽，Fail-Closed）。"""


MAX_RESTART_ATTEMPTS: Final[int] = 3  # 重启循环熔断上限（A9 §3.1：3 次上限终止重启循环）

# 崩溃策略分档
_RESTART_CLASS_CRITICAL_NO_RESTART: Final[str] = "critical_no_restart"  # P3：HC-01 任何时段不自动重启
_RESTART_CLASS_CORE_DEGRADE: Final[str] = "core_degrade"  # P1/P2：交易时段告警+降级，非交易时段重启
_RESTART_CLASS_NON_CORE: Final[str] = "non_core"  # P4/P5：自动重启（3 次上限）


@dataclass(frozen=True)
class SupervisorProcessSpec:
    """五进程注册表条目（A9 §1.1 进程矩阵行）。"""

    process_id: str  # P1~P5
    process_name: str  # market_data/signal_engine/trading_core/ai_autonomy/ml_pipeline
    priority: int  # 数值越小优先级越高
    cpu_cores: tuple[int, ...]
    memory_budget_gb: int
    heartbeat_interval_s: int
    heartbeat_timeout_s: int
    restart_class: str  # critical_no_restart/core_degrade/non_core
    duties: str  # 职责摘要
    service_module: str  # python -m 入口（NSSM AppParameters 声明）


@dataclass(frozen=True)
class CrashAction:
    """崩溃判定结果（纯数据；告警/降级/重启执行归 P4 与 Owner 窗口）。"""

    action: str  # "auto_restart" | "alert_and_degrade" | "alert_only"
    reason: str


_P3 = TRADING_CORE_SPEC  # MOD-INF-064：P3 规格派生唯一真源，不重复声明

FIVE_PROCESS_REGISTRY: Final[tuple[SupervisorProcessSpec, ...]] = (
    SupervisorProcessSpec(
        process_id="P1",
        process_name="market_data",
        priority=10,
        cpu_cores=(0, 1, 2, 3),
        memory_budget_gb=8,
        heartbeat_interval_s=3,
        heartbeat_timeout_s=15,
        restart_class=_RESTART_CLASS_CORE_DEGRADE,
        duties="iFind行情拉取/miniQMT Tick订阅/数据清洗分发/QPS限流",
        service_module="zephyr.data.tick_subscriber",
    ),
    SupervisorProcessSpec(
        process_id="P2",
        process_name="signal_engine",
        priority=20,
        cpu_cores=(4, 5, 6, 7),
        memory_budget_gb=16,
        heartbeat_interval_s=5,
        heartbeat_timeout_s=30,
        restart_class=_RESTART_CLASS_CORE_DEGRADE,
        duties="因子计算/信号生成/策略路由/市场状态判定",
        service_module="zephyr.runtime.signal_engine_main",
    ),
    SupervisorProcessSpec(
        process_id=_P3.process_id,
        process_name=_P3.process_name,
        priority=_P3.priority,
        cpu_cores=_P3.cpu_cores,
        memory_budget_gb=_P3.memory_budget_gb,
        heartbeat_interval_s=_P3.heartbeat_interval_s,
        heartbeat_timeout_s=_P3.heartbeat_timeout_s,
        restart_class=_RESTART_CLASS_CRITICAL_NO_RESTART,
        duties="/".join(_P3.duties),
        service_module="zephyr.trading",
    ),
    SupervisorProcessSpec(
        process_id="P4",
        process_name="ai_autonomy",
        priority=30,
        cpu_cores=(12, 13, 14, 15),
        memory_budget_gb=12,
        heartbeat_interval_s=10,
        heartbeat_timeout_s=60,
        restart_class=_RESTART_CLASS_NON_CORE,
        duties="自监控/自诊断/自修复/告警收敛/降级决策",
        service_module="zephyr.autonomy_core",
    ),
    SupervisorProcessSpec(
        process_id="P5",
        process_name="ml_pipeline",
        priority=40,
        cpu_cores=(16, 17, 18, 19),
        memory_budget_gb=20,
        heartbeat_interval_s=30,
        heartbeat_timeout_s=120,
        restart_class=_RESTART_CLASS_NON_CORE,
        duties="模型推理调度/离线训练/GPU显存管理/模型版本管理",
        service_module="zephyr.ml_train",
    ),
)

_REGISTRY_BY_ID: Final[dict[str, SupervisorProcessSpec]] = {spec.process_id: spec for spec in FIVE_PROCESS_REGISTRY}


def get_process_spec(process_id: str) -> SupervisorProcessSpec:
    """按进程 ID 取注册表条目；未知 ID Fail-Closed。"""
    spec = _REGISTRY_BY_ID.get(process_id)
    if spec is None:
        raise ProcessSupervisorError(f"未知进程 ID: {process_id!r}（五进程真源=A9 §1.1）")
    return spec


def compute_start_order() -> list[str]:
    """启动序列：优先级数值升序（高优先级先启动）→ P1→P3→P2→P4→P5。"""
    return [spec.process_id for spec in sorted(FIVE_PROCESS_REGISTRY, key=lambda s: s.priority)]


def compute_shutdown_order() -> list[str]:
    """关闭序列：优先级降序 → P5→P4→P2→P3→P1（P3 先于 P1，挂单先撤回）。"""
    return [spec.process_id for spec in sorted(FIVE_PROCESS_REGISTRY, key=lambda s: s.priority, reverse=True)]


def shutdown_sequence_with_redis() -> list[str]:
    """含 Redis 的完整关闭序列：P1 先于 Redis（末条行情先持久化）。"""
    return [*compute_shutdown_order(), "redis"]


def heartbeat_key(process_id: str) -> str:
    """进程心跳键：hb:{process_name}（A9 §1.1.3）。"""
    return f"hb:{get_process_spec(process_id).process_name}"


def heartbeat_ttl_seconds(process_id: str) -> int:
    """心跳 TTL = 超时阈值 + 30s 缓冲（规则复用 MOD-INF-063 hb dynamic_ttl，不重造）。"""
    hb_spec = get_namespace("hb")
    assert hb_spec.dynamic_ttl is not None  # MOD-INF-063 一致性自检保证
    return hb_spec.dynamic_ttl(get_process_spec(process_id).heartbeat_timeout_s)


def decide_crash_action(
    process_id: str,
    *,
    is_trading_hours: bool,
    consecutive_failures: int = 0,
) -> CrashAction:
    """崩溃重启判定（A9 §1.1.3 + §3.1；纯数据判定，执行归 P4 与 Owner 窗口）。

    - P3（critical_no_restart）：HC-01 任何时段不自动重启 → alert_only + 人工介入。
    - P1/P2（core_degrade）：交易时段 alert_and_degrade（P1 降级 miniQMT 纯 Tick /
      P2 由 P3 用缓存信号）；非交易时段 auto_restart（3 次上限）。
    - P4/P5（non_core）：auto_restart（3 次上限终止重启循环后 alert_only）。
    """
    spec = get_process_spec(process_id)
    if spec.restart_class == _RESTART_CLASS_CRITICAL_NO_RESTART:
        return CrashAction(
            action="alert_only",
            reason="HC-01：P3 交易核心任何时段不自动重启，立即告警+人工介入",
        )
    if consecutive_failures >= MAX_RESTART_ATTEMPTS:
        return CrashAction(
            action="alert_only",
            reason=f"连续失败 {consecutive_failures} 次达 {MAX_RESTART_ATTEMPTS} 次上限，终止重启循环仅告警",
        )
    if spec.restart_class == _RESTART_CLASS_CORE_DEGRADE and is_trading_hours:
        degrade = {
            "P1": "降级为 miniQMT 纯 Tick",
            "P2": "P3 使用缓存信号",
        }.get(spec.process_id, "降级")
        return CrashAction(
            action="alert_and_degrade",
            reason=f"交易时段核心进程崩溃：告警+{degrade}",
        )
    return CrashAction(action="auto_restart", reason="非交易时段/非核心进程：自动重启")


def check_supervisor_consistency() -> dict[str, object]:
    """注册表一致性自检：五进程/优先级唯一/心跳不倒挂/核号无重叠/启停序列硬约束。"""
    issues: list[str] = []
    ids = [spec.process_id for spec in FIVE_PROCESS_REGISTRY]
    if len(ids) != 5 or len(set(ids)) != 5:
        issues.append(f"进程注册表应为 5 进程且唯一: {ids}")
    priorities = [spec.priority for spec in FIVE_PROCESS_REGISTRY]
    if len(set(priorities)) != len(priorities):
        issues.append("优先级重复")
    all_cores = [core for spec in FIVE_PROCESS_REGISTRY for core in spec.cpu_cores]
    if len(set(all_cores)) != len(all_cores):
        issues.append("CPU 核号重叠")
    for spec in FIVE_PROCESS_REGISTRY:
        if spec.heartbeat_interval_s >= spec.heartbeat_timeout_s:
            issues.append(f"{spec.process_id} 心跳间隔 >= 超时")
    start = compute_start_order()
    shutdown = compute_shutdown_order()
    if start != ["P1", "P3", "P2", "P4", "P5"]:
        issues.append(f"启动序列漂移: {start}")
    if shutdown.index("P3") >= shutdown.index("P1"):
        issues.append("硬约束破坏：P3 必须先于 P1 关闭")
    return {"ok": not issues, "issues": issues}


def render_nssm_service_definitions() -> list[dict[str, object]]:
    """产出五进程 NSSM 服务定义声明（按启动序列；仅就绪件不执行注册）。

    硬边界：nssm install/set 注册与开机自启属 Owner 窗口（applied_by_ai=False）。
    """
    defs: list[dict[str, object]] = []
    for pid in compute_start_order():
        spec = get_process_spec(pid)
        service_name = f"ZephyrAlpha-{pid}"
        defs.append(
            {
                "service_name": service_name,
                "display_name": f"ZephyrAlpha {pid} {spec.process_name} (pri={spec.priority})",
                "app_parameters": f"-m {spec.service_module}",
                "start_mode": "auto",  # 开机自启声明（实际注册属 Owner 窗口）
                "priority": spec.priority,
                "cpu_cores": list(spec.cpu_cores),
                "memory_budget_gb": spec.memory_budget_gb,
                "heartbeat": {
                    "key": heartbeat_key(pid),
                    "interval_s": spec.heartbeat_interval_s,
                    "timeout_s": spec.heartbeat_timeout_s,
                    "ttl_seconds": heartbeat_ttl_seconds(pid),
                },
                "log_hosting": {
                    "app_stdout": f"logs/{spec.process_name}.out.log",
                    "app_stderr": f"logs/{spec.process_name}.err.log",
                },
                "applied_by_ai": False,
                "apply_boundary": "NSSM 注册/开机自启/核亲和等系统级设置属 Owner 窗口执行，本声明仅供审阅应用",
            }
        )
    return defs


def render_nssm_install_script() -> str:
    """产出 NSSM 安装脚本草稿（PowerShell 文本；DRAFT 仅就绪件，AI 不执行注册）。"""
    lines = [
        "# ============================================================",
        "# DRAFT — ZephyrAlpha 五进程 NSSM 安装脚本草稿（MOD-INF-066 生成）",
        "# 真源: A9 运维架构 §1.1 | 仅供 Owner 窗口审阅执行，AI 不执行服务注册",
        "# 启动序列: P1->P3->P2->P4->P5（优先级数值升序）",
        "# ============================================================",
        "$ErrorActionPreference = 'Stop'",
        "",
    ]
    for d in render_nssm_service_definitions():
        name = d["service_name"]
        lines.append(f"nssm install {name} python")
        lines.append(f'nssm set {name} AppParameters "{d["app_parameters"]}"')
        lines.append(f'nssm set {name} DisplayName "{d["display_name"]}"')
        lines.append(f"nssm set {name} Start SERVICE_AUTO_START")
        log = d["log_hosting"]
        assert isinstance(log, dict)
        lines.append(f'nssm set {name} AppStdout "{log["app_stdout"]}"')
        lines.append(f'nssm set {name} AppStderr "{log["app_stderr"]}"')
        lines.append("")
    lines.append("# 关闭序列（应急，优先级降序）: P5->P4->P2->P3->P1（P3 先于 P1，P1 先于 Redis）")
    return "\n".join(lines)
