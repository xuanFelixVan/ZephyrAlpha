---
module_id: KE-2824
status: active
title: permission_hooks.py — 新增文件
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# permission_hooks.py — 新增文件

permission_hooks.py — 新增文件
class PermissionHookRegistry:
    """
    权限钩子注册表——四类钩子，按顺序执行。

    钩子失败策略：
    - pre_check_hook FAIL → 操作被BLOCKED（"未能通过前置校验"）
    - post_check_hook FAIL → 触发auto_guard后验失败 → auto_rollback
    - on_blocked_hook FAIL → 仅记录日志（不能因为钩子失败而使阻断"变成放行"）
    - on_kill_switch_hook FAIL → 紧急通知Owner + 强制进入MAINTENANCE_MODE
    """

    _pre_check_hooks: list[PreCheckHook] = []
    _post_check_hooks: list[PostCheckHook] = []
    _on_blocked_hooks: list[OnBlockedHook] = []
    _on_kill_switch_hooks: list[OnKillSwitchHook] = []

    async def execute_pre_checks(
        self,
        agent: AgentIdentity,
        action: Action,
    ) -> list[HookResult]:
        """Tool调用前——运行所有注册的pre_check钩子"""

    async def execute_post_checks(
        self,
        agent: AgentIdentity,
        action: Action,
        result: ToolExecutionResult,
    ) -> list[HookResult]:
        """Tool执行后——运行所有注册的post_check钩子。
        这是 auto_guard 后验失败检测的核心注入点"""

    async def execute_on_blocked(
        self,
        agent: AgentIdentity,
        action: Action,
        block_reason: str,
        blocking_layer: str,
    ) -> list[HookResult]:
        """越权被拦截时——自定义响应（如：通知Owner、记录安全事件、触发备用路径）"""

    async def execute_on_kill_switch(
        self,
        trigger: KillSwitchTrigger,
        affected_agents: list[AgentIdentity],
    ) -> list[HookResult]:
        """全局熔断触发时——自定义响应（如：备份最新状态、通知所有下游系统、
        触发application-level的优雅降级、记录熔断前后的系统快照）"""

class HookResult(BaseModel):
    hook_id: str
    hook_name: str
    success: bool
    output: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: float
