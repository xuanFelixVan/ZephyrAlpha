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
"""

数据源冗余与热切换模块（MOD-L00-005）。

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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 主源 tick 心跳 + CH 连通性状态
#   fields: 主源 tick 到达时间戳 + ClickHouse 健康探针结果（心跳检测输入）
#   code: heartbeat_monitor.HeartbeatMonitor（docstring 组件清单 L22-25）
# 层: 算法
# - id: A1
#   name_zh: ① 心跳检测
#   name_en: HeartbeatMonitor/SourceState
#   intro: 盯主源 tick 到达和 CH 连通性，主源中断超 10 秒标记不可用
#   desc: 包公共面再导出 heartbeat_monitor 的 HeartbeatMonitor/SourceState（L32）；契约=主源中断>10s 触发切换，心跳检测失败只标记不可用+log（[INVARIANTS]/[ERROR_CONTRACT]）
#   inputs: I1
#   outputs: 主源/CH 可用性状态 SourceState
#   invariant: 主源中断>10s切换备源
# - id: A2
#   name_zh: ② 主备源热切换
#   name_en: SourceSwitcher/SourceProvider
#   intro: 按心跳状态把数据面在主源备源间切来切去，备源走抽象接口不绑实现
#   desc: 包公共面再导出 source_switcher 的 SourceSwitcher/SourceProvider（L33）；主→备→主 切换，切换失败保持当前源+log（[ERROR_CONTRACT]）
#   inputs: A1
#   outputs: 当前生效数据源
# - id: A3
#   name_zh: ③ CH 不可达降级 SQLite
#   name_en: SQLiteFallback
#   intro: ClickHouse 不可达超 30 秒就把数据先写本地 SQLite 兜底
#   desc: 包公共面再导出 sqlite_fallback 的 SQLiteFallback（L34）；仅写最近 N 小时数据防止 SQLite 无限增长（docstring L29）
#   inputs: A1
#   outputs: 本地 SQLite 兜底数据
#   invariant: CH不可达>30s降级SQLite
# - id: A4
#   name_zh: ④ CH 恢复自动回灌
#   name_en: RecoveryManager
#   intro: CH 恢复后把 SQLite 里攒的数据按 batch 灌回 ClickHouse
#   desc: 包公共面再导出 recovery 的 RecoveryManager（L35）；按 batch 推进、失败指数退避，回灌失败保留 SQLite 数据+log（docstring L30/[ERROR_CONTRACT]）
#   inputs: A3
#   outputs: SQLite→CH 回灌完成
#   invariant: CH恢复后自动回灌
# 层: 输出
# - id: O1
#   name_zh: 数据源冗余公共 API 面（6 符号）
#   name_en: __all__（HeartbeatMonitor/SourceSwitcher/SQLiteFallback/RecoveryManager 等）
#   intro: 主备热切换 + CH 降级回灌四组件的统一 import 面，全程 metrics 暴露
#   invariant: 全程 metrics 暴露
#   downstream: zephyr.data.tick_subscriber MOD-L00-001（可选接入，[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# A3 --> A4
# A2 --> O1
# A4 --> O1
"""

from zephyr.data.redundant_source.heartbeat_monitor import HeartbeatMonitor, SourceState
from zephyr.data.redundant_source.recovery import RecoveryManager
from zephyr.data.redundant_source.source_switcher import SourceProvider, SourceSwitcher
from zephyr.data.redundant_source.sqlite_fallback import SQLiteFallback

__all__ = [
    "HeartbeatMonitor",
    "SourceState",
    "SourceSwitcher",
    "SourceProvider",
    "SQLiteFallback",
    "RecoveryManager",
]
