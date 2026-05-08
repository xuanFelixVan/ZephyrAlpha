---
module_id: KE-module_blu-1_5____vs_agent_spec-000
title: 1.5 蓝图 vs Agent Spec 对比
category: module_blueprint
---

# 1.5 蓝图 vs Agent Spec 对比

1.5 蓝图 vs Agent Spec 对比

| 维度 | 蓝图（当前） | Agent Spec（目标） |
|------|------------|-------------------|
| 格式 | Markdown 文档 | SKILL.md（agentskills.io 标准） + YAML registry |
| 加载方式 | 人工指定或 MCP 搜索 | AGENTS.md 触发表 + Progressive Disclosure 三层递进 |
| 组织方式 | 1 蓝图 = 1 文档 | Domain Skill（模块领域知识） + Role Skill（角色操作模式）组合 |
| 执行验证 | 无 | Skill 执行后自动校验产出物 → 反馈环闭环 |
| 版本管理 | frontmatter version | semver + 兼容性矩阵 + 蓝图 version 联动 |
| 审计追踪 | 无 | Skill 加载/应用/漂移事件写入 Audit Trail（对接 MOD-INF-020） |
| 跨会话持久化 | 无 | Session Resume 协议：Skill 状态写入 Session Log |
| 新鲜度管理 | 无 | Freshness Score（0-100）：蓝图变更时自动降分 → 触发重审 |
| 跨 IDE 兼容 | 仅 Markdown | 同时支持 AGENTS.md（所有 IDE） + SKILL.md（原生 Skill 系统） |

---
