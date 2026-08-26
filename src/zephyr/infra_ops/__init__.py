# [BLUEPRINT] MOD-INF_OPS | docs/03_modules/_domain_infrastructure_operations/index.md
# [MODULE] zephyr.infra_ops
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] 无（包门面，守卫式导入四个模块主类）
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 子模块导入失败不阻断包导入（守卫式 import，目标类落地即自愈）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 无（门面不抛错；子模块错误契约见各自 ERROR_CONTRACT）
# [TESTS] tests/infra_ops/
# [A_module] module_id=MOD-INF_OPS | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""zephyr.infra_ops — 基础设施运维域包门面（MOD-INF_OPS）。

WAL 检查点监控 / 存储成本核算 / 运行时依赖拓扑 / Loki 日志管道四件
主类的守卫式导出入口（参照 data_eng 可逆模式：目标类落地即自愈）。
"""

from __future__ import annotations

from typing import Final

try:
    from zephyr.infra_ops.wal_checkpoint_monitor import WalCheckpointMonitor
except ImportError:
    WalCheckpointMonitor = None  # type: ignore[assignment]

try:
    from zephyr.infra_ops.storage_cost_calculator import StorageCostCalculator
except ImportError:
    StorageCostCalculator = None  # type: ignore[assignment]

try:
    from zephyr.infra_ops.runtime_topology_visualizer import RuntimeTopologyVisualizer
except ImportError:
    RuntimeTopologyVisualizer = None  # type: ignore[assignment]

try:
    from zephyr.infra_ops.loki_log_pipeline import LokiLogPipeline
except ImportError:
    LokiLogPipeline = None  # type: ignore[assignment]

__all__: Final = []

__all__.append("WalCheckpointMonitor")

__all__.append("StorageCostCalculator")

__all__.append("RuntimeTopologyVisualizer")

__all__.append("LokiLogPipeline")
