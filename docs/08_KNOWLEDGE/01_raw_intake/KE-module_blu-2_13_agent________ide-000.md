---
module_id: KE-module_blu-2_13_agent________ide-000
title: 2.13 Agent 身份模型（多 IDE 支持 + 成熟度 + 委托链）
category: module_blueprint
---

# 2.13 Agent 身份模型（多 IDE 支持 + 成熟度 + 委托链）

2.13 Agent 身份模型（多 IDE 支持 + 成熟度 + 委托链）

> **v0.4.0 扩展**：AgentIdentity 增加 parent_agent_id/delegation_depth 委托链字段 + SessionToken 签名校验。

```python
class AgentMaturityLevel(str, Enum):
    INTERN = "intern"         # L1: 新手——always_allow只读，写auto_guard，删blocked
    JUNIOR = "junior"         # L2: 初级——always_allow读写，删auto_guard
    SENIOR = "senior"         # L3: 高级——always_allow读写删，仅高危操作auto_guard
    PRINCIPAL = "principal"   # L4: 首席——近似Owner但不可改L0

class AgentIdentity(BaseModel):
    agent_id: str = Field(..., description="唯一标识——格式 AGT-{NAMESPACE}-{SEQ}")
    agent_type: AgentType = Field(..., description="Agent 类型")
    ide_source: IDESource = Field(..., description="来源 IDE——区分 TRAE/Cursor/RooCode")
    capabilities: list[str] = Field(default_factory=list, description="能力列表")
    role_bindings: list[RoleBinding] = Field(default_factory=list, description="角色绑定")
    maturity_level: AgentMaturityLevel = Field(default=AgentMaturityLevel.INTERN,
                                                description="Agent 信任成熟度")
    session_id: str = Field(..., description="当前会话 ID")
    session_token: Optional["SessionToken"] = Field(None, description="v0.4.0: Session签名Token——防跨Session身份伪造")
    parent_agent_id: Optional[str] = Field(None, description="v0.4.0: 父Agent ID——委托链起点")
    delegation_depth: int = Field(0, ge=0, le=3, description="v0.4.0: 委托深度——每层+1，上限3")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tasks_completed: int = Field(default=0, description="已完成任务数——来自不可变审计日志(MOD-INF-020)")
    safety_incidents: int = Field(default=0, description="安全事故次数")
    auto_guard_pass_rate: float = Field(default=1.0, description="auto_guard 后验通过率")

class AgentType(str, Enum):
    ARCHITECT = "architect"
    IMPLEMENTER = "implementer"
    REVIEWER = "reviewer"
    GOVERNOR = "governor"
    RESEARCHER = "researcher"
    OPERATOR = "operator"

class IDESource(str, Enum):
    TRAE = "trae"
    CURSOR = "cursor"
    ROOCODE = "roocode"
    CLI = "cli"

class RoleBinding(BaseModel):
    role: str = Field(..., description="角色名——引用 rbac_roles.yaml")
    scope: str = Field(..., description="作用域——layer/module/global")
    granted_by: str = Field(..., description="授权者——owner/system")
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None, description="临时授权过期时间")
```

---
