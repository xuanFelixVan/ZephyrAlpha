---
module_id: KE-1911----------------ai------d-0-003
status: active
title: 2.5 规则不可变性 —— 升级规则对AI只读（决策 D-022-04）
category: module_blueprint
ttl: permanent
---

# 2.5 规则不可变性 —— 升级规则对AI只读（决策 D-022-04）

2.5 规则不可变性 —— 升级规则对AI只读（决策 D-022-04）

> **决策 D-022-04**：升级规则文件（escalation_rules.yaml）和权限配置（rbac_roles.yaml）在运行时加载后对 AI 只读。任何 AI 尝试修改这些规则的行为触发 blocked 硬阻断。规则变更只能由 Owner（人类）通过专用通道执行。
>
> **决策依据**：Cross-Agent Privilege Escalation 研究发现多Agent可互相篡改配置绕过安全护栏。GitHub 已禁止 Copilot 修改 .github/agents 目录。对标 MARIA OS 的修正责任门框架——不同修正类型需不同门级别。

```yaml
rule_immutability:
  # === 保护范围 ===
  protected_files:
    - "escalation_rules.yaml"
    - "rbac_roles.yaml"
    - "system_prompts/*.md"
    - "skill_pack_definitions/*.yaml"
    protection_level: "blocked"  # AI 写操作 = 直接 blocked

  # === 完整性校验 ===
  integrity:
    on_load: "SHA-256 hash 校验"
    periodic: "每5分钟 re-hash 对比"
    mismatch_action: "立即阻止所有AI操作 + 通知Owner + 记录安全事件"

  # === 变更通道 ===
  change_process:
    who: "仅 Owner（人类）"
    how: "通过专用脚本 apply_rule_change.py（需Owner手动执行）"
    audit: "每次变更写入规则变更审计日志（独立于通用审计）"
    rollback: "变更脚本自动备份旧版本，支持一键回滚"

  # === Agent 配置隔离 ===
  cross_agent_isolation:
    rule: "不同 Skill Pack / IDE 的配置目录物理隔离"
    implementation: "每个 Agent 实例加载配置后锁定自身配置句柄为只读"
    violation_detection: "文件系统监控——任何Agent写入其他Agent配置目录 → blocked + 安全告警"
```

---
