---
module_id: KE-1770-----trigger-table----004
status: active
title: 2.2 Skill 触发表（Trigger Table）——对接 ZephyrAlpha 全流程七阶段
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 Skill 触发表（Trigger Table）——对接 ZephyrAlpha 全流程七阶段

2.2 Skill 触发表（Trigger Table）——对接 ZephyrAlpha 全流程七阶段

> **设计原则**：触发表不仅要按关键词路由，更要对应 ZephyrAlpha 的七个施工阶段（想法→草稿→审计→蓝图→施工→验收→审计）。每个阶段有默认的 Domain Skill + Role Skill 组合。

```yaml
trigger_table:
  description: "任务类型 → Domain Skill + Role Skill 映射表"

  # ===== 按施工阶段路由 =====
  stage_routing:
    "想法/草稿":
      role: "architect"
      domain_default: "master-blueprint"  # 总蓝图
      description: "需求分析、接口设计、架构草案"

    "审计（施工前）":
      role: "governor"
      domain_default: "gate-engine"
      description: "蓝图合规性检查、门禁预评估"

    "蓝图/设计":
      role: "architect"
      domain_match: "topic"  # 根据讨论的具体话题匹配 Domain Skill
      description: "正式蓝图编写、接口契约定义"

    "施工/实现":
      role: "implementer"
      domain_match: "module"  # 根据涉及的模块匹配 Domain Skill
      description: "代码实现、测试编写、lint 修复"

    "验收/验证":
      role: "governor"
      domain_match: "module"
      description: "门禁执行、测试覆盖检查、产物质检"

    "审计（施工后）":
      role: "governor"
      domain_default: "drift-detector"
      description: "漂移检测、合规溯源、审计日志"

  # ===== 按任务类型路由 =====
  task_routing:
    - trigger: "新建数据库模型/迁移/SQL"
      domain: "database-specialist"
      role: "implementer"
      reason: "数据库有 ATM 两阶段提交 + SQLite 约束——不可用通用实现模式"

    - trigger: "新建 MCP Server/工具/协议"
      domain: "mcp-specialist"
      role: "implementer"
      reason: "MCP 使用 stdio 协议 + FastMCP 框架——接口模式特殊"

    - trigger: "修改上下文引擎/Context Pipeline"
      domain: "context-specialist"
      role: "implementer"
      reason: "Context Engine 有 build→compress→validate→inject 四阶段管线"

    - trigger: "修改反馈环/Feedback Loop"
      domain: "feedback-specialist"
      role: "implementer"
      reason: "Feedback Loop 有 predict→detect→diagnose→act→verify 五阶段闭环"

    - trigger: "修改门禁/规则/Policy"
      domain: "gate-specialist"
      role: "governor"
      reason: "门禁修改必须先审计后施工"

    - trigger: "修改 Agent 权限/RBAC"
      domain: "agent-specialist"
      role: "governor"
      reason: "权限变更需要审计闭环"

    - trigger: "新建/修改蓝图本身"
      domain: "master-blueprint"
      role: "architect"
      reason: "蓝图变更遵循蓝图架构标准"

    - trigger: "跑审计/治理/合规检查"
      domain: "drift-detector"
      role: "governor"
      reason: "治理员 Skill 负责收集 Findings → 排序 → 修复"

    - trigger: "知识库操作/KE 管理"
      domain: "knowledge-specialist"
      role: "implementer"
      reason: "Knowledge Base 有 G1-G5 门禁流水线 + 10 状态 KE 生命周期"

  # ===== 默认规则（fallback） =====
  default:
    role: "implementer"
    domain_default: null  # 无匹配时只加载 Role Skill
    description: "通用编码/文档任务——不加载 Domain Skill，节省 token"
```
