---
module_id: KE-documentat-4_3_pit-001
title: 4.3 PIT 查询的实现路径（架构原则，非具体技术）
category: documentation
---

# 4.3 PIT 查询的实现路径（架构原则，非具体技术）

4.3 PIT 查询的实现路径（架构原则，非具体技术）

1. **bitemporal 表** —— OLTP 主数据用 valid_time + transaction_time 双时间戳建模
2. **append-only event log** —— 事件实体（Tick/Fill/Signal）天然 PIT，永不修改
3. **PIT-safe view layer** —— 因子计算前必须经过统一的 `pit_view(entity, asof=T)` 函数封装（具体实现归 09_data_platform）
4. **CI fitness function** —— `test_no_lookahead_bias.py` 在 PR 阶段扫描所有因子代码，禁止任何 `df.loc[df.date <= today]` 之外的时间过滤模式

> **DA 视图只定义"原则与契约"**，具体 SQL/代码归 03-AA L00/L02、09_data_platform、scripts/fitness_functions/。

---
