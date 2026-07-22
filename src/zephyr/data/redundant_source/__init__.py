# [BLUEPRINT] MOD-L00-005 | docs/03_modules/_domain_data/redundant_source_blueprint.md
# [MODULE] zephyr.data.redundant_source
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.local_replay; zephyr.shared.observability.metrics
# [CONSUMERS] zephyr.data.tick_subscriber(可选接入)
# [STARTUP] lazy
# [MATURITY] production
# [INVARIANTS] 主源中断>10s切换备源; CH不可达>30s降级SQLite; CH恢复后自动回灌; 全程metrics暴露
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 心跳检测失败->标记不可用+log; 切换失败->保持当前源+log; 回灌失败->保留SQLite数据+log
# [TESTS] tests/zephyr/data/test_redundant_source.py
# [A_module] module_id=MOD-L00-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据源冗余与热切换模块（MOD-L00-005）。

P2-8：主备数据源热切换 + CH 冗余降级。

组件：
- heartbeat_monitor: 心跳检测（主源 tick + CH 连通性）
- source_switcher: 数据源切换控制器（主→备→主）
- sqlite_fallback: CH 不可达时降级写本地 SQLite
- recovery: CH 恢复后 SQLite→CH 回灌

设计要点：
- 备源用抽象接口 SourceProvider，不绑定具体实现
- CH 降级到 SQLite 仅写最近 N 小时数据（防止 SQLite 无限增长）
- 回灌按 batch 推进，失败指数退避
"""
from zephyr.data.redundant_source.heartbeat_monitor import HeartbeatMonitor, SourceState
from zephyr.data.redundant_source.source_switcher import SourceSwitcher, SourceProvider
from zephyr.data.redundant_source.sqlite_fallback import SQLiteFallback
from zephyr.data.redundant_source.recovery import RecoveryManager

__all__ = [
    "HeartbeatMonitor",
    "SourceState",
    "SourceSwitcher",
    "SourceProvider",
    "SQLiteFallback",
    "RecoveryManager",
]
