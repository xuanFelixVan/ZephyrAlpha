---
module_id: KE-DOCUMENTAT-J5-L00-ACL-OQ-001
status: active
title: 附记：J5 L00 ACL 显式化（非正式 OQ，补充落盘）
category: documentation
ttl: permanent
---

# 附记：J5 L00 ACL 显式化（非正式 OQ，补充落盘）

附记：J5 L00 ACL 显式化（非正式 OQ，补充落盘）

**背景**：J5 是后续 H8（ACL 设计深化）阶段的前置基础，本 Stage 在 §4.1 L00 中明确标注 `connectors/` 子模块为 **Anti-Corruption Layer (ACL)**。

**ACL 选型依据**（vs Adapter / Facade）：
- **Adapter** 只做接口适配（方法签名转换），无法处理语义差异（如 tushare 用整数表示价格分、AKShare 不同时区约定）
- **Facade** 是简化复杂系统调用的门面，目标是"隐藏复杂度"而非"隔离外部领域概念"
- **ACL（Anti-Corruption Layer）** 是 DDD 战略设计模式，核心价值是将外部领域概念"翻译"为内部领域语言，防止 Vendor 命名约定和数据模型渗透到核心业务层——这正是 `connectors/` 的职责

**落盘位置**：`application_architecture.md` §4.1 L00 `connectors/` 子模块说明（约 250 字）；H8 阶段将在此基础上深化 Vendor Registry + 多 Vendor 故障转移设计。
