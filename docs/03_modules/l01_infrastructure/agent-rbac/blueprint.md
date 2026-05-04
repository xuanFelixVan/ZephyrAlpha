---
module_id: "MOD-INF-018"
title: "Agent 身份与权限系统蓝图 — RBAC Runtime + 权限执行器"
doc_type: blueprint
status: draft
version: "0.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: not_started
summary: "ZephyrAlpha Agent 身份与权限系统蓝图——将静态权限注册表(GOV-AI-001)升级为运行时强制执行器。三层权限(always_allow 95% / auto_guard 4% / blocked 1%) + 先干后验模式 + GOV-AI-001 自动派生 rbac_roles.yaml。支持多 IDE 并发（TRAE/Cursor/RooCode）。对标 Claude Code 宽默认窄限制 + K8s RBAC 自动派生 + Terraform auto-apply 先干后验。"
tags: [agent-rbac, rbac, permission-guard, identity, access-control, governance, infrastructure]
priority: P0
depends_on:
  - {target: "MOD-INF-007", at: "§2", why: "Gate Engine——权限检查是门禁的一种特化"}
  - {target: "MOD-INF-020", at: "§3", why: "审计追踪链——权限判定结果写入审计日志"}
  - {target: "MOD-INF-021", at: "§2", why: "Rollback——auto_guard 后验失败时自动回滚"}
  - {target: "GOV-AI-001", at: "全篇", why: "AI自治权限注册表——本蓝图的声明式权限真源，自动派生为 rbac_roles.yaml"}
---

# Agent 身份与权限系统蓝图 — RBAC Runtime

> **module_id**: MOD-INF-018 | **version**: 0.2.0 | **status**: draft | **layer**: cross_layer

> **对标**：Claude Code 宽默认窄限制（90% always allow）+ K8s RBAC 自动派生（Go 类型 → OpenAPI Schema）+ Terraform auto-apply 先干后验 + Cursor 自动编辑模式。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-018 |
| 代码落位 | `src/zephyr/agent_rbac/` |
| 运行时平面 | Warm memory（任务执行前加载权限配置） |
| 核心职责 | 判定"这个 Agent 能不能做这件事"——运行时权限强制执行 |

### 1.2 核心职能（一句话）

**Agent RBAC 是系统的门卫**——信任默认，边界拦截，先干后验，自动回滚。当前权限注册表是静态文档（AI 可以不查），本模块将其升级为运行时强制执行器——规则不执行 = 规则不存在。

### 1.3 运行场景约束（决策输入）

| 约束 | 影响 |
|------|------|
| 100% AI 开发，多 IDE 并发（TRAE / Cursor / RooCode） | 权限系统必须跨 IDE 统一，不能依赖单一 IDE 的审批机制 |
| 同时开启 10+ 对话 | 阻塞式审批 = 10 个对话全卡死——绝对不可接受 |
| 1 人 + AI，99% AI 维护 | 人工审批是最稀缺资源——必须最小化，能自动绝不人工 |
| 决策围绕原则/目标驱动 | 权限判定应该是规则驱动的自动决策，不是人工审批 |

### 1.4 当前痛点

| # | 痛点 | 后果 |
|---|------|------|
| 1 | 权限注册表(GOV-AI-001)是静态 .md 文档 | AI 可以不查注册表直接操作——规则形同虚设 |
| 2 | 没有 Agent 身份概念 | 无法区分"谁做了什么"——审计链断裂 |
| 3 | 没有 auto_guard 中间态 | AI 要么全自主、要么全阻断，缺少"先干后验"的信任梯度 |
| 4 | 权限检查不在执行路径上 | 权限是"建议"而非"强制"——绕过零成本 |
| 5 | 多 IDE 各自为政 | TRAE/Cursor/RooCode 各有自己的权限模型——无法统一管控 |

### 1.5 责任范围

| 管什么 | 不管什么（→ 去哪） |
|------|------|
| Agent 身份注册与识别 | Agent 的具体执行逻辑 → Orchestrator (MOD-INF-006) |
| 权限声明式配置（GOV-AI-001 → rbac_roles.yaml 自动派生） | 权限判定的触发时机 → Gate Engine (MOD-INF-007) |
| 运行时 Permission Guard | 权限审计日志的存储 → Audit Trail (MOD-INF-020) |
| auto_guard 后验失败 → auto-rollback | 回滚的具体执行 → Rollback System (MOD-INF-021) |

---

## 2. 核心架构

### 2.1 三层权限模型（决策 D-018-01：95/4/1 分布）

> **决策 D-018-01**：采用三层权限模型，分布为 always_allow 95% / auto_guard 4% / blocked 1%。取消 needs_approval 层——要么 auto_guard（先干后验），要么 blocked（绝对不让干）。人工审批是最稀缺资源，不应消耗在权限判定上。
>
> **决策依据**：1人+AI场景，10+并发对话，物理上不可能实时审批。对标 Claude Code 90% always allow + Cursor 自动编辑 + Terraform auto-apply。

```yaml
permission_levels:
  always_allow:
    description: "默认允许——95%的操作走这条路"
    distribution: "95%"
    philosophy: "信任默认——AI 直接干，不拦截"
    examples:
      - "读写 src/ 代码"
      - "创建/修改/删除非 permanent 文件"
      - "运行审计脚本、测试、lint"
      - "修改 YAML 配置文件"
      - "创建任务卡、修改任务状态"
      - "读取蓝图文档"
      - "创建新模块目录"
    enforcement: "自动放行 + 审计日志记录"

  auto_guard:
    description: "先干后验——AI 先执行，自动护栏后验，失败自动回滚"
    distribution: "4%"
    philosophy: "信任但验证——让 AI 先干，用自动化护栏兜底"
    examples:
      - "修改架构 YAML（CI 门禁后验 schema 合规）"
      - "修改蓝图接口契约 §3（AST 级对比后验）"
      - "修改 .pre-commit-config.yaml（CI 后验语法正确）"
      - "批量修改 5+ 文件（drift detector 后验一致性）"
    enforcement: "AI 正常执行 → pre-commit/CI 自动检查 → 失败则 auto-rollback (MOD-INF-021) → 审计日志记录"
    fallback: "后验失败 → 自动回滚 → 审计告警 → Owner 异步审阅"

  blocked:
    description: "绝对禁止——只有不可逆操作"
    distribution: "1%"
    philosophy: "边界拦截——这些操作连 AI 都不该想"
    examples:
      - "删除 ttl:permanent 文件"
      - "修改 AGENTS.md 核心原则"
      - "绕过门禁直接修改任务状态"
      - "执行 shell=True 的子进程"
      - "修改 immutable_core 标记的文件"
      - "删除审计日志"
    enforcement: "硬阻断 + 审计告警 + 没有例外"
```

### 2.2 先干后验模式（决策 D-018-02）

> **决策 D-018-02**：审批流采用"先干后验 + 自动护栏"模式，而非"事前审批"模式。AI 直接执行 → 自动护栏检查 → 失败自动回滚 → 审计日志记录 → Owner 异步审阅。
>
> **决策依据**：10+ 并发对话不可能等 Owner 实时审批。对标 Terraform auto-apply + Cursor 自动编辑 + K8s controller reconciliation。

```yaml
execution_flow:
  step_1_execute:
    who: "AI"
    what: "直接执行操作（always_allow 或 auto_guard）"
    note: "不等待任何人类确认"

  step_2_auto_guard:
    who: "自动护栏（pre-commit / CI / drift detector）"
    what: "自动检查操作结果是否合规"
    trigger: "git commit / git push / 定期轮询"

  step_3_auto_rollback:
    who: "Rollback System (MOD-INF-021)"
    what: "后验失败 → 自动回滚到上一个 checkpoint"
    trigger: "auto_guard 检查失败"

  step_4_audit:
    who: "Audit Trail (MOD-INF-020)"
    what: "所有操作（成功/失败/回滚）写入不可变审计日志"
    trigger: "每个操作"

  step_5_async_review:
    who: "Owner（异步）"
    what: "有空时翻审计日志，发现异常再处理"
    trigger: "Owner 主动查看 / 异常告警通知"
    note: "这是唯一需要人类参与的步骤——且是异步的"
```

### 2.3 GOV-AI-001 自动派生（决策 D-018-03）

> **决策 D-018-03**：rbac_roles.yaml 从 GOV-AI-001 自动派生，而非人工维护两份文档。Owner 只维护 GOV-AI-001（人类可读的权限声明），rbac_roles.yaml 由脚本自动生成（机器可执行的权限配置）。
>
> **决策依据**：消除手动复制 = 消除漂移可能。对标 K8s CRD 从 Go 类型自动派生 OpenAPI Schema。

```yaml
derivation_flow:
  source: "GOV-AI-001（ai-autonomy-authority-registry.md）"
  derivation_script: "scripts/governance/d3_metadata/derive_rbac_roles.py"
  target: "src/zephyr/agent_rbac/rbac_roles.yaml"
  ci_check: "CI 门禁校验 rbac_roles.yaml 与 GOV-AI-001 一致性"

  principle: "人类写声明 → 机器生成配置 → CI 校验一致性"
  benefit: "单点维护 + 零漂移 + 自动同步"
```

### 2.4 Agent 身份模型（多 IDE 支持）

```python
class AgentIdentity(BaseModel):
    agent_id: str = Field(..., description="唯一标识——格式 AGT-{NAMESPACE}-{SEQ}")
    agent_type: AgentType = Field(..., description="Agent 类型")
    ide_source: IDESource = Field(..., description="来源 IDE——区分 TRAE/Cursor/RooCode")
    capabilities: list[str] = Field(default_factory=list, description="能力列表")
    role_bindings: list[RoleBinding] = Field(default_factory=list, description="角色绑定")
    session_id: str = Field(..., description="当前会话 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
```

### 2.5 Permission Guard 运行时检查

```python
class PermissionGuard:
    async def check(self, agent: AgentIdentity, action: Action) -> PermissionResult:
        """
        运行时权限检查——每个写操作前必须调用

        输入：agent 身份 + 请求的动作
        输出：ALLOW / AUTO_GUARD / BLOCKED
        核心逻辑：查找 agent.role_bindings → 匹配 rbac_roles.yaml → 返回判定
        """

class PermissionResult(BaseModel):
    decision: PermissionDecision
    reason: str
    guard_checks: Optional[list[str]]  # auto_guard 时列出后验检查项
    audit_entry: AuditEntry

class PermissionDecision(str, Enum):
    ALLOW = "allow"
    AUTO_GUARD = "auto_guard"
    BLOCKED = "blocked"
```

---

## 3. 文件组成

| 文件 | 职责 |
|------|------|
| `identity.py` | Agent 身份注册与识别——AgentIdentity 模型 + 注册表（含 IDESource） |
| `permission_guard.py` | 运行时权限检查——ALLOW / AUTO_GUARD / BLOCKED 三路判定 |
| `rbac_roles.yaml` | 角色定义——从 GOV-AI-001 自动派生，CI 校验一致性 |
| `audit_emitter.py` | 权限审计事件发射器——对接 Audit Trail (MOD-INF-020) |
| `derive_rbac_roles.py` | 自动派生脚本——GOV-AI-001 → rbac_roles.yaml |

---

## 4. 与现有系统的集成

| 集成目标 | 集成方式 | 集成点 |
|---------|---------|--------|
| Gate Engine (MOD-INF-007) | 权限检查作为 G0 门禁的前置检查 | `gate_engine.py` → `permission_guard.check()` |
| Task System (MOD-INF-006) | 任务创建时绑定 Agent 身份 | `task_repo.create()` → `identity.register()` |
| Audit Trail (MOD-INF-020) | 每次权限判定写入审计日志 | `permission_guard.check()` → `audit_emitter.emit()` |
| Rollback System (MOD-INF-021) | auto_guard 后验失败时自动回滚 | CI 失败 → `rollback_executor.restore()` |
| MCP Servers (MOD-INF-013) | MCP Tool 调用前权限检查 | `tool_call` → `permission_guard.check()` |
| GOV-AI-001 | 自动派生 rbac_roles.yaml | `derive_rbac_roles.py` → GOV-AI-001 → rbac_roles.yaml |

---

## 5. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | GOV-AI-001 → rbac_roles.yaml 派生脚本 + AgentIdentity 模型 + PermissionGuard 骨架 | 📋 Backlog |
| experimental | 完整三层权限执行 + auto_guard 后验链路 + Gate Engine 集成 | 📋 Backlog |
| beta | 多 IDE 统一身份 + MCP 权限检查 + 权限漂移检测 + 审计仪表盘 | 📋 Backlog |

---

## 6. 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | auto_guard 后验失败率高——频繁自动回滚影响效率 | 中 | 中 | 统计后验失败率，持续优化 auto_guard 规则；失败率 > 20% 的操作降级为 blocked |
| R2 | 权限配置漂移——rbac_roles.yaml 与 GOV-AI-001 不一致 | 低 | 高 | CI 门禁校验一致性 + derive_rbac_roles.py 自动派生 |
| R3 | 性能开销——每个操作前权限检查增加延迟 | 低 | 中 | 权限结果缓存（TTL=5min）+ always_allow 跳过详细检查 |
| R4 | 多 IDE 身份冲突——同一文件被不同 IDE 的 Agent 同时修改 | 中 | 高 | 文件锁 + 乐观并发控制 + drift detector 实时检测 |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-018-01 | 三层权限 95/4/1 分布，取消 needs_approval | 2026-05-05 | 1人+AI场景，10+并发对话，人工审批不可行 |
| D-018-02 | 先干后验 + 自动护栏，非事前审批 | 2026-05-05 | 多 IDE 并发不可能等实时审批；对标 Terraform auto-apply |
| D-018-03 | GOV-AI-001 自动派生 rbac_roles.yaml | 2026-05-05 | 消除手动复制=消除漂移；对标 K8s CRD 自动派生 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.2.0 | 三项决策写入：D-018-01 三层95/4/1分布 + D-018-02 先干后验 + D-018-03 自动派生；新增 IDESource 多 IDE 支持；取消 needs_approval 层；新增 Rollback System 依赖 |
| 2026-05-05 | 0.1.0 | 初始创建——Agent 身份模型 + 三层权限 + Permission Guard + 审批流 |
