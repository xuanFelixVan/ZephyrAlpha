---
module_id: KE-258------registry-004
title: 3.2 登记表层（Registry）
category: documentation
---

# 3.2 登记表层（Registry）

3.2 登记表层（Registry）

| 属性 | 值 |
|------|-----|
| 存储位置 | `_registry/catalogs/_index.yaml`（PS-REG-001）+ 各领域规则文件 |
| 内容 | 所有 COND 条目（后果可逆的）+ REC 条目 + CODE 条目 |
| 判定标准 | 违反后后果可逆（可通过后续操作完全消除） |
| 修改门槛 | 领域规则负责人批准 |
| AI 权限 | `human_gated`——AI 可提议修改，需 Owner 批准 |
| 编号体系 | COND-XX / REC-XX / CODE-XX / {域代码}-XX |
| 加载策略 | **领域触发（Domain-Triggered）**——按任务类型加载。对应 CR-005（P1）：新任务时 2 轮内预加载相关文档。CR-011（P2）：只加载相关架构层的上下文 |
