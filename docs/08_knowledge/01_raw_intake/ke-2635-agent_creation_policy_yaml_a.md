---
module_id: KE-2540---a-003
status: active
title: agent_creation_policy.yaml — Agent 复制/派生规则
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# agent_creation_policy.yaml — Agent 复制/派生规则

agent_creation_policy.yaml — Agent 复制/派生规则
agent_creation_policy:
  # ─── 谁能创建 Agent ───
  who_can_create:
    - role: "human_owner"
      description: "Owner本人——无限制。可创建任意类型、任意maturity的Agent"
    - role: "principal_agent"          # L4_PRINCIPAL——已充分信任
      description: "Principal Agent——可在其IDE内创建子Agent。子Agent自动L1_INTERN起"
      max_children_per_hour: 2
      max_total_children: 5
    - role: "senior_agent"             # L3_SENIOR——有限委派
      description: "Senior Agent——仅在当前session内可创建临时子Agent（session结束=终止）"
      max_children_per_session: 1
      child_lifetime: "session"        # Session结束自动终止

  # ─── 创建者不可创建的类型 ───
  restrictions:
    - "Agent不能创建 maturity_level >= 自己的Agent"      # 防止越级复制
    - "Agent不能修改子Agent的maturity_level"              # 成熟度不可转让
    - "Agent不能创建跨IDE的Agent"                         # IDE隔离

  # ─── 权限遗传（Permission Inheritance with Attenuation）───
  inheritance:
    algorithm: "创建者权限集 × 衰减系数"
    attenuation:
      L4_PRINCIPAL_parent: 0.7          # Principal创建的Agent获得70%权限
      L3_SENIOR_parent: 0.5             # Senior创建的Agent获得50%权限

    never_inherited_permissions:        # 这些权限绝对不传递
      - "modify_immutable_core"         # 不可变核心修改权
      - "delete_audit_logs"             # 审计日志删除权
      - "disable_kill_switch"           # 熔断器禁用权
      - "create_further_agents"         # 孙子Agent创建权——只传一代
      - "modify_rbac_config"            # RBAC配置修改权
      - "issue_emergency_token"         # 紧急覆盖令牌签发权——仅Owner

  # ─── Agent 生命周期 ───
  lifecycle:
    spawn: "创建者发起 spawn_agent → Gate Engine检查creation_policy → Agent RBAC验证角色→创建子Agent"
    termination:
      owner_terminated: "Owner手动终止"
      session_expired: "Session结束 → 临时子Agent自动终止"
      kill_switch: "熔断触发 → 相关Agent终止"
      idle_timeout: "Agent 30分钟无操作 → L1_INTERN自动休眠"

    audit: "每个创建/复制/终止事件 → 不可变审计日志"
```

---
