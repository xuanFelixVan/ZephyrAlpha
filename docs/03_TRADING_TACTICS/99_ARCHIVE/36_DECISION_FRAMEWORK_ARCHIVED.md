---
module_id: 36_DECISION_FRAMEWORK_ARCHIVED
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 36环节决策框架归档文档
---

﻿---
module_id: 36_DECISION_FRAMEWORK_ARCHIVED_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 交易策略、战术执行
  - 交易执行
  - 回测系统
---

---
module_id: TACTICS_ARCH_DECISION_FRAMEWORK_001
version: 0.1.1
status: Archived
created_date: 2026-04-01
last_updated: 2026-04-04
owner: 首席文档架构?standard_type: 专业量化机构文档
responsibility:
  - 因子计算
  - 交易执行
  - 回测系统
applicable_scope: 全系?compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 已归?archive_reason: 36个环节过于复杂，单人无法维护
archive_date: 2026-03-28---



# 36环节决策框架（归档）
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> **状?*: ?已归?> **原因**: 36个环节过于复杂，单人无法维护
> **索引**: `ARC_001`


## 原设计概?
原计划将量化研究/开?验证/部署流程拆分?6个环节，每个环节独立文档案

## 归档原因

| 问题 | 说明 |
|------|------|
| 维护成本 | 36个文档需要持续更新，单人不现?|
| 复杂?| 过度拆分导致关联性丢?|
| 实际价?| 文档数量≠系统质?|


## 替代方案

采用**精简版决策框?*（见下方），覆盖核心决策点：

### 精简版决策流?
```
研究决策 ?因子决策 ?策略决策 ?风控决策 ?执行决策
    ?          ?          ?          ?          ?  验证1      验证2       验证3       验证4       验证5
    ?          ?          ?          ?          ?  ?        ?         ?         ?         ?
   ?         ?          ?          ?          ?  是→下一    是→下一     是→下一     是→下一     是→实盘
  否→优化    否→优化     否→优化     否→优化     否→暂停
```

### 核心决策?(5?

| 决策?| 验证内容 | 通过标准 |
|--------|----------|----------|
| 研究决策 | 因子IC_IR | >0.3 |
| 因子决策 | IC衰减 | <30% |
| 策略决策 | 回测夏普 | >1.5 |
| 风控决策 | 最大回?| <15% |
| 执行决策 | 模拟交易 | 3个月稳定 |


## 归档位置

本文档已归档案`03_TRADING_TACTICS/99_ARCHIVE/` 目录?

**维护?*: 清风量化系统
**状?*: 已归?**归档时间**: 2026-03-28
