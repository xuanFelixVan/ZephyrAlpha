---
module_id: KE-843
status: active
title: §2 本目录的责任（governance/task/）
category: governance
---

# §2 本目录的责任（governance/task/）

§2 本目录的责任（governance/task/）

`governance/task/` 是 ZephyrAlpha 的**任务治理中心**。这里管的是"任务卡怎么写、怎么被治理、怎么关闭"相关的规则。

**正向责任**（本目录管的事）：
1. 任务卡的正文结构规范（如何写"读→做→产→检"四步）
2. 任务生命周期的治理规则（谁有权取消/改优先级、P0 通胀保护、升级治理）
3. 任务关闭的验证标准和残留清扫

**负向责任**（本目录不管的事，去对应位置找）：
- 任务卡字段的权威定义 → `meta/metadata_registry.yaml` §7
- 状态机实现、门禁检查逻辑、超时检测代码 → `03_modules/infra_ops/task-system/blueprint.md` §5.2-§5.5
- Session 交接协议 → `governance/ai/handoff-protocol.md`

---
