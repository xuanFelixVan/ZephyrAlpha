---
module_id: KE-module_blu-2_1___________d-022-01-004
title: 2.1 三级升级策略（决策 D-022-01）
category: module_blueprint
---

# 2.1 三级升级策略（决策 D-022-01）

2.1 三级升级策略（决策 D-022-01）

> **决策 D-022-01**：升级级别与 MOD-INF-018 权限级别对齐——自主(always_allow) → auto_guard → blocked。取消 needs_approval 人工审批层。升级由规则引擎自动判定，不依赖人类。**升级双向可逆**——条件改善后自动降级恢复自主。
>
> **决策依据**：与 MOD-INF-018 三层权限 95/4/1 分布一致。人工审批是最稀缺资源，升级判定应该是规则驱动的自动决策。同时，升级不应是单向死胡同——对标 Terraform drift 的 P0→P1→P2 可升降级。

```yaml
escalation_levels:
  level_1_autonomous:
    permission: "always_allow"
    description: "AI 自主决策——95%的操作"
    rule: "操作在 Agent 能力矩阵内 + 不涉及 blocked 资源 + Token预算充足"
    action: "直接执行"

  level_2_auto_guard:
    permission: "auto_guard"
    description: "先干后验——4%的操作"
    rule: "操作涉及架构 YAML / 批量修改 / 接口契约变更 / 中低置信度"
    action: "AI 先执行 → 自动护栏后验 → 成功→降级回autonomous / 失败→回滚→重试→3次失败→升级blocked"
    deescalate_condition: "3次连续后验通过 → 降级回 autonomous"

  level_3_blocked:
    permission: "blocked"
    description: "绝对禁止——1%的操作"
    rule: "操作不可逆 / 涉及安全敏感内容 / 熔断器 OPEN"
    action: "硬阻断 + 审计告警 + 通知 Owner（分级：CRITICAL）"
    deescalate_condition: "熔断器 CLOSED + Owner手动确认解除"
```
