---
module_id: KE-679
status: active
title: 1. 目的与范围
category: governance
---

# 1. 目的与范围

1. 目的与范围

本策略定义 ZephyrAlpha 系统中任何模块**进入系统前**必须通过的准入条件。覆盖三类操作：

- **新增模块**：`architecture-model/` 下所有新模块
- **模块变更**：active 模块的接口修改、依赖变更、status 变化、优先级调整——变更视同重新注入，必须重走准入。涉及 active 模块的变更还须先通过 GOV-ARCH-002（架构变更门控）
- **迁移模块**：从候选池注入正式目录的模块

第三方模块（外部引入）除本章四级筛选外，还须通过 §10 的专项安全检查。

本策略**不适用于**：纯文档类文件（doc_type: template/register）、临时草稿（status: draft 且未申请注入）。
