---
module_id: GOV-DATA-002
title: 数据血缘策略
doc_type: policy
status: Draft
version: "0.2.0"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "定义 ZephyrAlpha 系统中数据从哪来到哪去必须可追溯——血缘记录要求、工具链、最小血缘粒度。"
tags: [data, governance, lineage]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter字段唯一真源——策略文件的doc_type/rule_form一致性约束"}
ai_autonomy: human_gated
---
# 数据血缘策略
> module_id: GOV-DATA-002 | version: 0.2.0 | status: draft | layer: L1
---
## 1. 目的与范围
本策略定义 ZephyrAlpha 系统中数据血缘的记录规则。适用于所有数据流转路径。
---
## 2. 规则
### DLG-001：什么数据必须有血缘

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| DLG-001 | 以下数据必须有完整的血缘记录：交易信号、持仓数据、风控指标、合规报告 | 数据不可信；禁止用于决策 |

> **关键数据判定标准**：数据需被纳入血缘追踪的条件——该数据是否直接影响 (a) 交易下单决策、(b) 账户资金安全、(c) 风控阀值计算、(d) 合规报告生成。满足任一条件即为关键数据。上表 4 类为当前已识别的关键数据，新增数据类型时 AI 按此四项标准判定是否需要血缘，不确定时上报 Owner 裁定。| 验证：`validate_architecture.py` 扫描关键数据源是否有血缘记录 |
### DLG-002：血缘记录必须包含上下游
| 编号 | 规则 | 违反后果 |
|------|------|---------|
| DLG-002 | 血缘记录必须包含：数据源（上游）、转换逻辑、数据目标（下游） | 血缘不完整 |
### DLG-003：最小血缘粒度

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 关键数据 | 血缘粒度到字段级别 | 粒度不足需补充 |
| 非关键数据 | 血缘粒度到表/文件级别 | 可接受 |

---

## 3. 验证方式

| 规则 | 验证方式 | 频率 |
|------|---------|------|
| DLG-001 | 检查关键数据是否有血缘记录 | 每季度 |
| DLG-002 | 检查血缘记录是否包含上下游 | 每季度 |
| DLG-003 | 检查血缘粒度是否达标 | 每季度 |

---

## 4. 修订记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-01 | 0.2.0 | #23 审批修复。(1) 编号前缀：ABS/COND → DLG-（DLG-001~DLG-003）。(2) DLG-001 补齐关键数据判定标准——4项条件：(a)交易下单决策 (b)账户资金安全 (c)风控阀值计算 (d)合规报告生成。新增数据类型时AI按此自主判定，不确定上报Owner裁定。(3) `depends_on: GOV-DATA-001, ai_autonomy: human_gated`。(4) `date` → 2026-05-01。 |
| 2026-04-30 | 0.1.0 | 初始版本 |
