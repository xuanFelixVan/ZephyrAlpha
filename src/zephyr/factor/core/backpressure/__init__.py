# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-CORE-BP
# [MODULE] zephyr.factor.core.backpressure
# [DOMAIN] D_FACTOR
# [DEPENDENCIES]
# [CONSUMERS] zephyr.factor.core.dag_manager; zephyr.factor.core.dist_feature_eng
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三态状态机（NORMAL/THROTTLED/PAUSED）单调转换
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] acquire 在 PAUSED 或超时返回 False（不抛）；release 不抛
# [TESTS] tests/factor/test_backpressure.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_FACTOR core backpressure 子包——进程内在途并发限流器。

提供 BackpressureLimiter（基于 threading.Semaphore），三态状态机：
- NORMAL：正常受理
- THROTTLED：高水位触发（仍受理但告警）
- PAUSED：外部强制暂停（拒绝新请求）

与 infrastructure/pipeline/backpressure_manager.py 的边界：
- 本模块是进程内并发闸门（Semaphore 语义）
- BackpressureManager 是跨域 PAUSE/THROTTLE/RESUME 信号路由
- 两者正交，不冲突

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: limiter 子模块公开符号 类/枚举/数据类
#   fields: BackpressureConfig 配置 / BackpressureLimiter 限流器 / BackpressureState 三态枚举 / BackpressureStats 统计快照
#   code: backpressure/limiter.py L37-188；__init__.py L31-36 from-import
# 层: 算法
# - id: A1
#   name_zh: ① 包门面聚合再导出
#   name_en: __init__ re-export facade
#   intro: 把 limiter 子模块的 4 个公开符号汇集到包入口，调用方只认 backpressure 包名
#   desc: from .limiter import 4 符号（L31-36）→ __all__ 显式声明（L38-43）；docstring 厘清与 infrastructure BackpressureManager 的正交边界（进程内并发闸门 vs 跨域信号路由）
#   inputs: I1
#   outputs: 4 个再导出符号（__all__）
#   invariant: __all__ 与导入符号一一对应
# 层: 输出
# - id: O1
#   name_zh: 背压限流器公共 API 面
#   name_en: BackpressureLimiter 等 4 符号
#   intro: 对外提供进程内在途并发限流器（threading.Semaphore，三态状态机 NORMAL/THROTTLED/PAUSED）
#   invariant: 三态单调转换；acquire 在 PAUSED 或超时返回 False 不抛
#   downstream: zephyr.factor.core.dag_manager / zephyr.factor.core.dist_feature_eng（MOD-L02-001 [CONSUMERS]，实际经 limiter 子模块直连）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.factor.core.backpressure.limiter import (
    BackpressureConfig,
    BackpressureLimiter,
    BackpressureState,
    BackpressureStats,
)

__all__ = [
    "BackpressureConfig",
    "BackpressureLimiter",
    "BackpressureState",
    "BackpressureStats",
]
