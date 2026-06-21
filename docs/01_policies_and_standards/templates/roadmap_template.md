---
module_id: GOV-034
title: <季度或主题> 路线图
doc_type: template
status: Draft
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: YYYY-MM-DD
horizon_start: YYYY-MM-DD
horizon_end: YYYY-MM-DD
summary: 一段话说清本路线图覆盖的时间范围、主题焦点与核心里程碑。
completeness: "unknown"

template_for: roadmap

date: '2026-04-22'
ttl: permanent
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
路线图模板 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/d3_metadata/check_template_compliance.py <文档路径> --template roadmap
-->
<!--
REQUIRED_SECTIONS:
  overview: "概述"
  s1: "1. 覆盖范围"
  s2: "2. 里程碑地图"
  s3: "3. 每个里程碑的出口标准"
  s4: "4. 风险与假设"
  s5: "5. Review 节奏"
  s6: "6. 修订记录"
END_REQUIRED_SECTIONS
-->

# <标题> 路线图

## 概述

> ⚠️ **必填**。AI 阅读本文档的第一段——3~5 句话建立心理模型。
> 写清楚：这个路线图覆盖什么时间范围、主题焦点、核心里程碑、谁在看。

{本路线图覆盖 {YYYY-MM-DD ~ YYYY-MM-DD}，主题焦点为 {主题}。核心里程碑：M1 {里程碑名称} → M2 {里程碑名称} → M3 {里程碑名称}。读者：自己 / 协作 AI / 外部利益相关者。核心目标：{一句话描述路线图要达成的结果}。}

---

## 1. 覆盖范围

- **时间基线**：YYYY-MM-DD ~ YYYY-MM-DD
- **主题焦点**：...
- **读者**：自己 / 协作 AI / 外部利益相关者

## 2. 里程碑地图

```
M1: <里程碑 1 名称>    [YYYY-MM]  ←── 当前
    │
    ▼
M2: <里程碑 2 名称>    [YYYY-MM]
    │
    ▼
M3: <里程碑 3 名称>    [YYYY-MM]
```

## 3. 每个里程碑的出口标准

### M1：<名称>

**目标时间**：YYYY-MM

**出口标准**（满足即 done）：

- [ ] 条件 1
- [ ] 条件 2

**主要动作**（详见 taskbook）：

- 动作 X
- 动作 Y

### M2：<名称>

...

## 4. 风险与假设

- 风险 1：...
- 假设 1：...

## 5. Review 节奏

- 月度 review：只看里程碑是否按时
- 季度 review：调整里程碑顺序或增删

## 6. 修订记录

| 日期 | 说明 |
|------|------|
| YYYY-MM-DD | 初版 |
