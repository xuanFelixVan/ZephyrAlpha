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
"""D_FACTOR core backpressure 子包——进程内在途并发限流器。

提供 BackpressureLimiter（基于 threading.Semaphore），三态状态机：
- NORMAL：正常受理
- THROTTLED：高水位触发（仍受理但告警）
- PAUSED：外部强制暂停（拒绝新请求）

与 infrastructure/pipeline/backpressure_manager.py 的边界：
- 本模块是进程内并发闸门（Semaphore 语义）
- BackpressureManager 是跨域 PAUSE/THROTTLE/RESUME 信号路由
- 两者正交，不冲突
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
