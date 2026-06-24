---
module_id: KE-2757
status: active
title: immutable_core.py 新增
category: module_blueprint
---

# immutable_core.py 新增

immutable_core.py 新增
class ColdStartLock:
    """
    冷启动锁——系统启动时全局拒绝所有Agent操作，直到权限配置加载校验通过。

    生命周期：
    1. 系统启动 → startup_lock = BLOCKED_ALL（所有Agent操作被拒绝）
    2. rbac_roles.yaml 加载 → hash校验通过 → startup_lock = RELEASED（正常检查链路）
    3. 30秒内未加载成功 → startup_lock = MAINTENANCE_MODE（仅Owner可操作）
    """

    _state: str = "BLOCKED_ALL"           # BLOCKED_ALL | RELEASED | MAINTENANCE_MODE
    _loaded_at: Optional[datetime] = None
    _release_conditions_met: bool = False
    MAX_LOAD_TIME_SECONDS: int = 30

    async def check(self) -> StartupLockResult:
        if self._state == "BLOCKED_ALL":
            elapsed = (datetime.utcnow() - self._started_at).total_seconds()
            if elapsed > self.MAX_LOAD_TIME_SECONDS:
                self._state = "MAINTENANCE_MODE"
                return StartupLockResult.MAINTENANCE_MODE
            return StartupLockResult.BLOCKED
        elif self._state == "MAINTENANCE_MODE":
            # 仅Owner（human）操作可通过
            return StartupLockResult.MAINTENANCE_MODE
        elif self._state == "RELEASED":
            return StartupLockResult.ALLOWED

    async def release_after_validation(self) -> bool:
        """校验通过后释放锁"""
        # 1. rbac_roles.yaml hash校验
        # 2. L0 protected_paths 所有路径存在性验证
        # 3. Gate Engine (MOD-INF-007) 就绪确认
        # 全部通过 → _state = RELEASED

    def status_indicator(self) -> str:
        return f"Agent RBAC Cold Start: awaiting permission config load ({self.elapsed}s)"
```

---
