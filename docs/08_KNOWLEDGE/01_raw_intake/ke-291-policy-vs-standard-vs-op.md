---
module_id: KE-269
status: active
title: 3.2.2 policy vs standard vs operational_rule 判据
category: documentation
---

# 3.2.2 policy vs standard vs operational_rule 判据

3.2.2 policy vs standard vs operational_rule 判据

> **问一个问题就能区分**：这个文件是在"定规矩"还是在"教操作"？

| 文件在做什么 | doc_type | 归属 | 例子 |
|------------|----------|------|------|
| 定义"什么是对的/错的"——必须、禁止、不得 | `policy` | `governance/` | "所有 API 密钥必须存储在环境变量中" |
| 定义"推荐怎么做"——应该、建议、最佳实践 | `standard` | `governance/` | "建议使用 Pydantic v2 做数据验证" |
| 定义"按步骤执行"——步骤 1→2→3 | `operational_rule` | `operational/` | "Step 1: 检查 .env → Step 2: 验证密钥格式" |

**3 个测试**：

| 测试 | policy | standard | operational_rule |
|------|--------|----------|-----------------|
| 删掉步骤描述，规则还成立吗？ | ✅ 成立 | ✅ 成立 | ❌ 不成立（没有步骤就没法执行） |
| 违反了会怎样？ | 🔴 严重（红线） | 🟡 不推荐（但不是红线） | 🔴 操作出错（按步骤才能避免） |
| 换一个人/AI 执行，结果一样吗？ | ✅ 一样（规则不变） | ⚠️ 可能不同（推荐做法有弹性） | ✅ 一样（步骤固定） |
