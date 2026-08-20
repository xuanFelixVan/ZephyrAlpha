# [A_module] module_id=MOD-INF-system_telemetry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | §0
# [MODULE] zephyr.infrastructure.system_telemetry
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] fail-closed on write; test_mode=True silences all outbound; shutdown() reverses init order
# [MODIFY-GUARD] facade.py; auto_bootstrap.py; health/; alerts/; profiles/; schema/
# [CONSUMERS] zephyr.__init__; zephyr.security.access_control; zephyr.security.budget_enforcement
# [ERROR_CONTRACT] ValueError; OSError; RuntimeError
# [TESTS] tests/infrastructure/test_telemetry_facade.py; tests/infrastructure/test_auto_telemetry_bootstrap.py
# [TTL] permanent
"""

system-telemetry — 系统遥测模块（MOD-INF-015 v2.1.0）.

9 子系统: metrics | logs | traces | ai_behavior | health | profiles | alerts | schema | archive

完全自动化接入:
    from zephyr.infrastructure.system_telemetry import Telemetry
    telemetry = Telemetry("my_module", test_mode=False)
    # 后台自动: flush(60s) / alert(30s) / health(10s) / archive(300s)

模块零代码注册:
    from zephyr.infrastructure.system_telemetry.auto_bootstrap import register_module
    t = register_module("MOD-INF-XXX")

Watchdog 独立进程:
    python -m zephyr.infrastructure.system_telemetry.watchdog --id wd-1 --interval 10

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 调用方模块标识与运行模式 参数
#   fields: 模块名 module_name + test_mode 开关（True 静默全部外发）
#   code: Telemetry("my_module", test_mode=False) L19 / register_module("MOD-INF-XXX") L24
# - id: I2
#   name: Watchdog 命令行 参数
#   fields: --id 实例标识 + --interval 心跳间隔秒
#   code: python -m ...watchdog --id wd-1 --interval 10 L27
# 层: 算法
# - id: A1
#   name_zh: ① 9子系统公共API聚合导出
#   name_en: __init__ 聚合导出
#   intro: 把遥测9个子系统的类与函数集中到一个包入口对外提供
#   desc: 从 metrics/logs/traces/ai_behavior/health/profiles/alerts/schema/archive 9 子系统 import 并汇总 __all__（L30-132）
#   inputs: I2
#   outputs: 统一公共符号面（Telemetry/HealthSubsystem/AlertSubsystem/Watchdog 等）
# - id: A2
#   name_zh: ② 零代码注册与全局门面入口
#   name_en: auto_bootstrap.register_module / facade.Telemetry
#   intro: 模块注册即拿遥测实例，后台自动跑flush/alert/health/archive四个循环
#   desc: register_module 注册模块返回 Telemetry；后台自动 flush(60s)/alert(30s)/health(10s)/archive(300s)（L17-27）
#   inputs: I1
#   outputs: Telemetry 实例（test_mode=True 时全部外发静默）
#   invariant: fail-closed on write; shutdown() 按初始化逆序关闭
# 层: 输出
# - id: O1
#   name_zh: 系统遥测公共API面
#   name_en: Telemetry + 9子系统符号集
#   intro: 对外暴露 Telemetry 门面与各子系统类，供全库模块接入遥测
#   downstream: zephyr.__init__ / zephyr.security.access_control / zephyr.security.budget_enforcement（# [CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A2
# I2 --> A1
# A1 --> A2
# A1 --> O1
# A2 --> O1
"""

from zephyr.infrastructure.system_telemetry.ai_behavior import (
    AIBehaviorEvent,
    ErrorContext,
    emit_ai_behavior_event,
    validate_error_context,
)
from zephyr.infrastructure.system_telemetry.alerts import AlertLevel, AlertSubsystem
from zephyr.infrastructure.system_telemetry.archive import next_archive_batch_id
from zephyr.infrastructure.system_telemetry.auto_bootstrap import (
    get_global_telemetry,
    get_registered_modules,
    register_module,
)
from zephyr.infrastructure.system_telemetry.contract_metrics import (
    CT_TEL_SLA,
    ContractMetricsCollector,
    DriftAlert,
    SlaRecord,
    get_contract_metrics,
    get_ct_tel_stats,
    measure_ct_tel_sla,
)
from zephyr.infrastructure.system_telemetry.facade import Telemetry
from zephyr.infrastructure.system_telemetry.health import HealthSubsystem
from zephyr.infrastructure.system_telemetry.health_probes import (
    HealthProbeManager,
    HealthzProbe,
    LivenessProbe,
    ProbeStatus,
    ReadinessProbe,
)
from zephyr.infrastructure.system_telemetry.logs import flush as logs_flush
from zephyr.infrastructure.system_telemetry.metrics_bridge import MetricsBridge
from zephyr.infrastructure.system_telemetry.profiles import ProfileSubsystem
from zephyr.infrastructure.system_telemetry.schema import SchemaSubsystem
from zephyr.infrastructure.system_telemetry.traces import (
    Span,
    SpanEvent,
    TraceContext,
    TraceSampler,
    get_trace_tree,
    list_active_spans,
    noop_span,
)
from zephyr.infrastructure.system_telemetry.watchdog import Watchdog, WatchdogHeartbeat

__all__ = [
    "CT_TEL_SLA",
    "AIBehaviorEvent",
    "AlertLevel",
    "AlertSubsystem",
    "ContractMetricsCollector",
    "DriftAlert",
    "ErrorContext",
    "HealthProbeManager",
    "HealthSubsystem",
    "HealthzProbe",
    "LivenessProbe",
    "ProbeStatus",
    "ProfileSubsystem",
    "ReadinessProbe",
    "SchemaSubsystem",
    "SlaRecord",
    "Span",
    "SpanEvent",
    "Telemetry",
    "TraceContext",
    "TraceSampler",
    "Watchdog",
    "WatchdogHeartbeat",
    "_budget_telemetry_bridge",
    "_trace_bridge",
    "ai_behavior",
    "alerts",
    "archive",
    "auto_bootstrap",
    "contract_metrics",
    "emit_ai_behavior_event",
    "facade",
    "get_contract_metrics",
    "get_ct_tel_stats",
    "get_global_telemetry",
    "get_registered_modules",
    "get_trace_tree",
    "health",
    "health_aggregator",
    "health_probes",
    "list_active_spans",
    "logs",
    "logs_flush",
    "measure_ct_tel_sla",
    "metrics_bridge",
    "next_archive_batch_id",
    "noop_span",
    "profiles",
    "register_module",
    "schema",
    "traces",
    "validate_error_context",
    "watchdog",
    "otel_instrumentation",
]

__all__.append("MetricsBridge")
