---
module_id: KE-2755
status: active
title: identity.py 中新增
category: module_blueprint
---

# identity.py 中新增

identity.py 中新增
class SessionToken(BaseModel):
    """Session 签名Token——防跨Session身份伪造"""
    session_id: str
    agent_id: str
    ide_source: str              # TRAE / Cursor / RooCode
    issued_at: datetime
    expires_at: datetime
    signature: str               # HMAC-SHA256(agent_id + session_id + issued_at, secret_key)
    parent_agent_id: Optional[str] = None   # 委托链——谁创建/委托了这个Agent
    delegation_depth: int = 0               # 委托深度——每层+1，上限3

class AgentIdentityVerifier:
    """Agent身份验证器——横向越权防护"""
    
    SECRET_KEY: str = "from-secure-key-store"
    MAX_DELEGATION_DEPTH: int = 3
    
    async def verify_session_token(self, token: SessionToken) -> bool:
        """验证Session Token的签名有效性"""
    
    async def detect_identity_mismatch(
        self,
        claimed_agent: AgentIdentity,
        session_token: SessionToken,
    ) -> MismatchReport:
        """
        检测身份不匹配：
        - 同一 session 中出现不同 maturity_level 的声明
        - 跨 session 操作中 agent_id 不一致
        - 委托链深度超过 MAX_DELEGATION_DEPTH
        """
    
    async def prevent_cross_session_forgery(
        self,
        current_session: SessionContext,
        operation_target: Action,
    ) -> ForgeryCheckResult:
        """
        跨Session身份伪造防护：
        - Session 2不能声明Session 1的Agent Identity
        - Maturity Level不能跨Session无痕提升
        """
```

```yaml
