---
module_id: KE-2720
status: active
title: emergency_override.py — 新增文件
category: module_blueprint
---

# emergency_override.py — 新增文件

emergency_override.py — 新增文件
class EmergencyOverrideToken(BaseModel):
    """
    Owner签发的JIT临时越权令牌。

    安全约束：
    - 最大有效期：5分钟
    - 最大签发数：每小时3个
    - 每个token绑定一个 Agent + 一个 Session
    - 每个token绑定指定的layers_to_bypass
    - Token使用后立即失效（一次性）
    """
    token_id: str                       # UUID
    issued_to_agent_id: str             # 绑定到特定Agent
    issued_to_session_id: str           # 绑定到特定Session
    layers_to_bypass: list[str]         # 如 ["L3", "L4"]——只跳过特定层
    allowed_operations: list[str]       # 如 ["file_write"]——只允许特定操作
    issued_at: datetime
    expires_at: datetime                # issued_at + 5min
    max_uses: int = 1                   # 一次性——用完即废
    used_count: int = 0
    signature: str                      # Owner私钥签名
    revocation_url: str                 # Owner可随时吊销

class EmergencyOverrideManager:
    MAX_TOKENS_PER_HOUR: int = 3
    MAX_TOKEN_LIFETIME_MINUTES: int = 5

    async def issue_token(
        self,
        owner: OwnerIdentity,
        agent: AgentIdentity,
        layers: list[str],
        operations: list[str],
        reason: str,                     # 必须填写原因——写入审计日志
    ) -> EmergencyOverrideToken:
        """Owner签发紧急覆盖令牌"""
        # 1. 验证Owner身份——双因子确认
        # 2. 检查小时签发上限
        # 3. 签发JWT格式token（含layers和operations声明）
        # 4. 写入不可变审计日志：{who, what, when, why}
        # 5. 通知其他活跃Agent：有紧急覆盖在执行

    async def validate_and_consume(
        self,
        token: EmergencyOverrideToken,
        agent: AgentIdentity,
        action: Action,
    ) -> OverrideResult:
        """验证token并消耗它"""
        # 1. 签名验证
        # 2. 过期检查
        # 3. Agent/Session匹配检查
        # 4. allowed_operations匹配检查
        # 5. used_count++——一次性消耗
        # 6. 审计日志：{token_id, agent_id, action, layers_bypassed, result}

    async def revoke_token(self, token_id: str) -> bool:
        """Owner手动吊销——即使token未过期也立即失效"""
