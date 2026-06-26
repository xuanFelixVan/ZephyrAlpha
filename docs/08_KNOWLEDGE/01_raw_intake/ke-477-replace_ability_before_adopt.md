---
module_id: KE-428
status: active
title: 原则 5：Replace-ability Before Adoption / 先保替换性，再引入
category: documentation
ttl: permanent
---

# 原则 5：Replace-ability Before Adoption / 先保替换性，再引入

原则 5：Replace-ability Before Adoption / 先保替换性，再引入

> 引入任何开源项目前，必须证明：如果该项目死亡（archive/abandon），系统在 2 周内可切换到替代方案。

**评估清单**（每次引入 OSS 时必须填写）：
1. **替代方案**：是否已有 1+ 个备选 OSS 项目？（是/否，列出备选名称）
2. **抽象层完整性**：当前 adapter 是否封装了所有 OSS 特定调用？（是/否）
3. **迁移成本**：替换 OSS 需要修改多少个文件？（目标 ≤ 3 个 adapter 文件）
4. **数据迁移**：替换是否需要数据格式迁移？（是/否，若是需提供迁移脚本）

**不满足 2 周替换承诺的 OSS → 禁止引入**。此原则确保 OSS 是"借力"而非"绑死"。

---
