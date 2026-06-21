---
module_id: KE-1715----------000
status: active
title: 2.14 Permission Guard 七层+三横切面 运行时检查（核心 API）
category: module_blueprint
---

# 2.14 Permission Guard 七层+三横切面 运行时检查（核心 API）

2.14 Permission Guard 七层+三横切面 运行时检查（核心 API）

```python
class PermissionGuard:
    """七层纵深防御 + 三横切面 运行时权限执行器"""

    async def check(
        self,
        agent: AgentIdentity,
        action: Action,
        task_context: Optional[TaskContext] = None,
    ) -> PermissionResult:
        """
        完整权限判定——横切面A→L0→L5→横切面A
        
        横切面A pre_hooks → L0 ColdStartLock → L0 EmergencyOverride → L0→L5七层检查 → 横切面A post_hooks

        输入：Agent 身份 + 请求的动作 + 任务上下文
        输出：ALLOW / AUTO_GUARD / BLOCKED + 决策链
        延迟目标：< 1.2ms（含横切面）
        """

    async def dry_run(
        self,
        agent: AgentIdentity,
        action: Action,
        task_context: TaskContext,
    ) -> DryRunResult:
        """模拟模式：预览权限判定而不实际执行"""

    async def impact_analysis(
        self,
        proposed_change: RoleChange,
    ) -> ImpactReport:
        """权限影响分析——这个变更会影响多少 Agent/操作"""

    async def kill_switch(
        self,
        agent: AgentIdentity,
        trigger: KillSwitchTrigger,
    ) -> KillSwitchResult:
        """触发熔断——阻断单 Agent 或全局"""

    def engine_status(self) -> EngineHealth:
        """Engine 健康检查 + 降级状态 + 冷启动锁状态 + 缓存通道健康"""

    # ─── v0.4.0 新增方法 ───
    async def emergency_override(
        self,
        token: EmergencyOverrideToken,
        agent: AgentIdentity,
        action: Action,
    ) -> OverrideResult:
        """紧急覆盖——验证JIT越权令牌并临时绕过指定层"""

    async def invalidate_cache(
        self,
        reason: InvalidationReason,
    ) -> InvalidationReport:
        """缓存失效——权限变更或紧急收紧时推送失效"""

    async def get_health_dashboard(self) -> HealthDashboard:
        """获取Owner健康仪表盘——5个关键数字"""

class PermissionResult(BaseModel):
    decision: PermissionDecision
    reason: str
    layered_decisions: dict[str, LayerResult]  # 横切面A+L0→L5+横切面A 每层判定
    guard_checks: Optional[list[str]]  # auto_guard 时列出后验检查项
    audit_entry: AuditEntry
    latency_us: float
    # ─── v0.4.0 新增字段 ───
    cold_start_elapsed_ms: Optional[float] = None    # 冷启动锁耗时
    emergency_override_applied: bool = False          # 是否应用了紧急覆盖
    hooks_executed: int = 0                            # 执行的钩子数

class LayerResult(BaseModel):
    layer: str  # "L0".."L6"
    decision: PermissionDecision
    reason: str
    latency_us: float

class PermissionDecision(str, Enum):
    ALLOW = "allow"
    AUTO_GUARD = "auto_guard"
    BLOCKED = "blocked"
    SKIPPED = "skipped"  # 当前层不适用

class Action(BaseModel):
    tool_id: str = Field(..., description="Tool 标识符")
    tool_name: str = Field(..., description="Tool 名称")
    tool_type: str = Field(..., description="Tool 类型——read/write/delete/execute/network")
    parameters: dict[str, Any] = Field(..., description="Tool 参数")
    target_paths: list[str] = Field(default_factory=list, description="操作目标路径")
    session_id: str = Field(..., description="会话 ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # ─── v0.4.0 新增字段 ───
    emergency_token: Optional[str] = Field(None, description="紧急覆盖令牌（Owner签发JIT，<5分钟有效）")
    source_i
