# [BLUEPRINT] MOD-MKT-004 | docs/03_modules/_domain_mkt_data/failover/blueprint.md
# [MODULE] zephyr.market_data.failover
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_registry; zephyr.market_data.vendor_base; zephyr.shared.foundation.errors
# [CONSUMERS] D_EX_SOR
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] FailoverEvent/FailoverConfig frozen; FailoverPolicy/FailoverReason Enum; _active_vendor_id/_history加Lock; 切换原子(先确认目标可用); 同vendor不切自身
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FailoverError(ZA-MKT-0004)
# [TESTS] tests/market_data/failover/test_failover_manager.py
# [A_module] module_id=MOD-MKT-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_MKT_DATA — Failover (故障切换)

多数据源主备切换管理。主数据源健康检查失败时自动切换到备用数据源,
主源恢复后可选自动切回。基于 VendorRegistry 的多 vendor 注册。

属 A 类基础设施(高可用机制), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-004
蓝图: docs/03_modules/_domain_mkt_data/failover/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: FailoverConfig 切换配置
#   fields: priority_list/policy(PRIORITY/ROUND_ROBIN)/auto_failback/history_max（frozen 不可变）
#   code: manager.py FailoverConfig L68
# - id: I2
#   name: VendorRegistry 已注册数据源池
#   fields: 各 vendor 实例及其 health_check() 可用性
#   code: manager.py L39 引用 MOD-MKT-001
# 层: 算法
# - id: A1
#   name_zh: ① 健康巡检与自动切换决策
#   name_en: FailoverManager.check_and_failover
#   intro: 定期检查活跃源健康，挂了切备、主源恢复切回
#   desc: active=None 初选(INITIAL)；active 注销或 health_check 失败→切备(HEALTH_CHECK_FAILED)；auto_failback 且主源恢复→切回(AUTO_FAILBACK)；active 健康则无操作
#   inputs: I1 I2
#   outputs: FailoverEvent 或 None
# - id: A2
#   name_zh: ② 备用源选择
#   name_en: _find_next_available
#   intro: 按优先级或轮询策略挑出下一个可用数据源
#   desc: PRIORITY 按 priority_list 顺序找首个健康 vendor；ROUND_ROBIN 从 _rr_index 轮询找首个健康并推进索引；均排除当前 active
#   inputs: I1 I2
#   outputs: 目标 vendor_id 或 None
# - id: A3
#   name_zh: ③ 原子切换
#   name_en: _switch_to
#   intro: 先确认目标可用再切换活跃源，保证切换原子性
#   desc: 目标须已注册且健康否则返回 None；同 vendor 幂等不切；切后目标 set_status(ACTIVE)；失败源在 _do_failover 中置 ERROR
#   inputs: A2
#   outputs: 新活跃 vendor_id
#   invariant: 先确认目标可用再切；同 vendor 不切自身
# - id: A4
#   name_zh: ④ 事件记录与回调通知
#   name_en: _record_event
#   intro: 把每次切换记成事件存历史并通知回调
#   desc: FailoverEvent 含 from/to/reason/UTC 时间戳；deque(maxlen=history_max) 存历史；锁外通知回调且异常隔离；无可用源记 ALL_FAILED
#   inputs: A3
#   outputs: FailoverEvent
# 层: 输出
# - id: O1
#   name_zh: 切换事件与当前活跃源
#   name_en: FailoverEvent/get_active
#   intro: 主备切换结果与当前可用数据源，供执行层取数
#   invariant: active 指向健康 vendor 或 None（ALL_FAILED）
#   downstream: D_EX_SOR（#[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from zephyr.market_data.failover.manager import (
    FailoverConfig,
    FailoverError,
    FailoverEvent,
    FailoverManager,
    FailoverPolicy,
    FailoverReason,
)

__all__ = [
    "FailoverConfig",
    "FailoverError",
    "FailoverEvent",
    "FailoverManager",
    "FailoverPolicy",
    "FailoverReason",
]
