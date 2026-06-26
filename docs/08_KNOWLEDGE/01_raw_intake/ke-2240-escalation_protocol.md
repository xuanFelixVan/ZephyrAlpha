---
module_id: KE-2147--------004
status: active
title: 3.7 Escalation Protocol 集成（对接 MOD-INF-022）
category: module_blueprint
ttl: permanent
---

# 3.7 Escalation Protocol 集成（对接 MOD-INF-022）

3.7 Escalation Protocol 集成（对接 MOD-INF-022）

```yaml
skill_escalation:
  description: "Skill 执行遇到需要人类决策的情况时走升级/委托路径"
  escalation_triggers:
    - "Skill 指令自身有歧义——AI 不知道该怎么做 → 升级到 Owner 决策"
    - "Skill 修改涉及 breaking change（蓝图 §3 接口契约变更）→ 升级到 Owner 批准"
    - "Skill 执行后门禁连续 3 次 FAIL → 升级到 Owner 分析根因"
  escalation_paths:
    - "轻量决策（如修一个小 lint 错误的方式选择）→ 标记为 flag，不阻塞继续执行"
    - "中度决策（如选择哪种数据库迁移策略）→ 暂停执行，等待 Owner 回复"
    - "重大决策（如架构变更）→ 生成决策文档，暂停，等待 Owner 签字"
```
