---
module_id: KE-2761-----------d-000
status: active
title: intent_binder.py — 新增文件（横切面D核心组件）
category: module_blueprint
ttl: permanent
---

# intent_binder.py — 新增文件（横切面D核心组件）

intent_binder.py — 新增文件（横切面D核心组件）
class IntentBindingContext(BaseModel):
    """意图绑定上下文——每次任务启动时创建，贯穿整个操作链"""
    task_id: str                      # 来自Task System的任务ID
    original_intent: str              # Owner最初的自然语言指令（不可变）
    intent_signature: str             # HMAC(task_id + original_intent + issued_at)
    allowed_tool_categories: list[str]  # 如 ["file_read", "file_write", "shell_test"]
    disallowed_tool_categories: list[str]  # 如 ["network_external", "file_delete_system"]
    permission_envelope_ttl: int = 3600  # 权限信封有效期（秒），超时需重签发
    created_at: datetime
    drift_tolerance: float = 0.3      # 意图漂移容忍度（0-1，越低越严格）

class IntentBoundPermissionGuard:
    """
    IBAC 权限执行器——横切面D核心。

    工作原理：
    1. 任务启动 → 绑定原始意图 + 创建临时权限信封
    2. 每个Tool调用 → 验证当前操作是否仍在意图信封内
    3. 操作链进行中 → 持续检测意图漂移
    4. 意图信封过期 → 需Owner重新确认或自动降级
    """

    async def bind_intent(
        self,
        agent: AgentIdentity,
        task: TaskContext,
        owner_instruction: str,         # Owner原始指令（不可变基线）
    ) -> IntentBindingContext:
        """任务启动时——绑定意图，创建临时权限信封"""
        intent_hash = self._compute_intent_hash(task.task_id, owner_instruction)
        envelope = IntentBindingContext(
            task_id=task.task_id,
            original_intent=owner_instruction,
            intent_signature=intent_hash,
            allowed_tool_categories=self._derive_allowed_tools(task, agent),
        )
        # 写入不可变审计日志：{when, who, task, intent, envelope}
        return envelope

    async def check_within_intent(
        self,
        binding: IntentBindingContext,
        agent: AgentIdentity,
        action: Action,
        operation_chain: list[Action],  # 当前操作链的历史（最近10步）
    ) -> IntentCheckResult:
        """
        每一步检查：当前操作是否仍在意图信封内？

        检查维度：
        1. tool_category 是否在 allowed 中（硬边界）
        2. 意图漂移度（soft边界——语义相似度检测）
        3. 操作链累积漂移（多步操作累积的意图偏离）
        """
        # 硬边界检查
        if action.tool_type not in binding.allowed_tool_categories:
            return IntentCheckResult.VIOLATION

        # 软边界——意图漂移
        drift_score = await self._compute_drift(
            binding.original_intent,
            operation_chain,
            action,
        )
        if drift_score > binding.drift_tolerance:
            return IntentCheckResult.DRIFT_DETECTED
        elif drift_score > binding.drift_tolerance * 0.7:
            return IntentCheckResult.DRIFT_WARNING

        return IntentCheckResult.WITHIN_INTENT

class IntentCheckResult(str, Enum):
    WITHIN_INTENT = "within_intent"         # 在意图信封内——放行
    DRIFT_WARNING = "drift_warning"         # 漂移警告——降级为auto_guard
    DRIFT_DETECTED = "drift_detected"       # 漂移检测——blocked + P0告警
    VIOLATION = "violation"                 # 硬违反——blocked + 无例外
```

---
