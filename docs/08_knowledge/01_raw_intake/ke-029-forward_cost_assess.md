---
module_id: KE-029--------forward-cost-assess-001
status: active
title: 6.3 未来成本评估（Forward Cost Assessment）
category: agent_instruction
ttl: permanent
doc_type: knowledge_entry
---

# 6.3 未来成本评估（Forward Cost Assessment）

6.3 未来成本评估（Forward Cost Assessment）

每个决策基于**未来实施成本**而非当前便利性。

- **决策矩阵**：

  | 未来做 = 低成本 | → 现在不做，进待办（Backlog） |
  | 未来做 = 高成本（埋雷） | → 现在做 |
  | 两者成本均可接受 | → 选对 AI 施工最友好的那个 |

- **"埋雷"判定标准**：
  - 当前选择会导致未来必须重写架构（而不仅是扩展）
  - 当前选择会产生不可逆的数据或 Schema 迁移
  - 当前选择引入的临时方案没有清晰的拆除路径和时间节点
- **专业参考**：Ward Cunningham → Technical Debt Metaphor（技术债务——借来的时间将来要还利息）/ Martin Fowler → Strangler Fig Pattern（绞杀榕模式——新系统逐步替换旧系统，而非一次性重写）
