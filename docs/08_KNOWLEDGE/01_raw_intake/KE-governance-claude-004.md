---
module_id: KE-governance-claude-004
title: 三、Claude 特种救援触发条件
category: governance
---

# 三、Claude 特种救援触发条件

三、Claude 特种救援触发条件

Claude 在以下任一条件满足时被触发——**不是每个任务都用 Claude**：

| 触发条件 | 判定标准 | 示例 |
|---------|---------|------|
| **DeepSeek 执行失败** | `execute_pipeline()` 返回 `MODULE_TIMEOUT` 或 `ARTIFACT_FORMAT_ERROR` 连续 3 次 | DeepSeek 反复改不对一个核心算法 |
| **GLM 审查连续驳回** | G7 门禁不通过 ≥ 2 次——GLM 审查发现 DeepSeek 产出有结构性缺陷 | DeepSeek 生成的代码存在架构级错误 |
| **Owner 标记为"关键"** | 任务卡 `priority = "P0"` 且 title 含 "核心" / "关键" / "架构" / "安全" | "实现数据库迁移脚本——涉及不可逆 Schema 变更" |
| **安全敏感任务** | `tags_fn` 含 "security" 或 `tags_mo` 含安全相关模块 | "实现用户认证中间件" |
| **新领域探索** | `tags_st = "experimental"` ——全新领域，DeepSeek 可能缺乏相关知识 | "集成第三方支付 SDK——项目首次使用" |

---
