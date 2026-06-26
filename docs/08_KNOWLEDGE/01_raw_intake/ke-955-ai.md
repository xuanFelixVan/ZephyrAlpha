---
module_id: KE-877---ai-006
status: active
title: §4 对 AI 的使用指引
category: governance
ttl: permanent
---

# §4 对 AI 的使用指引

§4 对 AI 的使用指引

每个新 AI session 进入 `governance/` 后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——理解 8 个治理域的职责边界
2. **根据任务类型选择子域**：
   - 涉及架构评审/ADR → `architecture/`
   - 涉及密钥/访问/安全事件 → `security/`
   - 涉及数据质量/血缘/保留 → `data/`
   - 涉及合规/审计/监管 → `compliance/`
   - 涉及文档规范 → `document/`
   - 涉及 AI 行为 → `ai/`
   - 涉及任务管理 → `task/`
   - 涉及模块接入 → `module/`
3. **进入子域后，先读子域的 index.md**（如果有），再读具体文件

所有治理文件标记 `ai_autonomy: human_gated` —— AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

---
