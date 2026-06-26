---
module_id: KE-1380
title: 11. 依赖关系
category: module_blueprint
ttl: permanent
---

# 11. 依赖关系

11. 依赖关系

| 依赖模块 | 类型 | 内容 | 版本要求 |
|---------|------|------|---------|
| MOD-INF-001 (capacity-assurance) | runtime | 容量预算检查 + SLO 监控 + Error Budget + Kill Switch | 2.0.0 |
| MOD-INF-003 (task-card-kms) | runtime | Finding → CRITICAL 自动创建任务卡 | 1.0.0 |
| MOD-INF-004 (vibe-coding-pipelines) | contract | 脚本系统是双管线审计侧的脚本基础设施 | 1.0.0 |
| **MOD-TASK_SYSTEM (task-system)** | **contract** | **G0-G7门禁体系 + M1-M11管线节点——脚本失败↔任务状态的核心接口** | **0.3.0** |
| PS-STD-012 (规则验证标准) | contract | V1~V4 验证分级 + 阻断/警告规则定义 | 1.1.0 |
| PS-STD-001 (元数据注册表) | contract | frontmatter schema + META-V 验证规则 | 当前版本 |
| SCRIPT-QUALITY-001 | contract | 脚本质量 8 维度 × 38 条款 | 1.0.0 |

---
