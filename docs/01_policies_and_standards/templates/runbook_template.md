---
ai_autonomy: human_gated
classification: confidential
completeness: unknown
created_by: human_plus_agent
date: ''
depends_on: []
doc_type: template
language: zh
layer: cross_layer
module_id: OPS-008
owner: ZephyrAlpha-Owner
rule_form: procedural
scope: global
stability: evolving
status: Draft
summary: Runbook 创建模板——过程式操作规则，定义具体操作的步骤化流程，新建 runbook 类文档时使用此模板
tags: []
template_for: operational_rule
title: Runbook Template
ttl: permanent
verifiability: manual
version: 0.1.0
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
Runbook 模板 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/d3_metadata/check_template_compliance.py <文档路径> --template runbook
-->
<!--
REQUIRED_SECTIONS:
  overview: "概述"
  s1: "1. 目的与范围"
  s2: "2. 前置条件"
  s3: "3. 执行频率与耗时"
  s4: "4. 操作步骤"
  s5: "5. 验证清单"
  s6: "6. 回滚方案"
  s7: "7. AI 自治权限标注"
  s8: "8. TTL 与生命周期"
  s9: "9. 变更记录"
END_REQUIRED_SECTIONS
-->

# {标题}

> module_id: {填写} | version: 0.1.0 | status: draft | layer: {填写}

---

## 概述

> ⚠️ **必填**。AI 阅读本文档的第一段——3~5 句话建立心理模型。
> 写清楚：这个 runbook 执行什么操作、谁来执行、什么时候执行、为什么存在。

{本 Runbook 定义 {操作名称} 的标准化执行流程——从前置条件检查到验证完成的完整步骤链。执行频率：{按需/每日/每周}，预计耗时 {N} 分钟。执行对象：AI Agent / 人类运维。核心目标：{一句话描述操作要达成的结果}。}

---

## 1. 目的与范围

### 1.1 目的

<!-- 填写：这个 runbook 执行什么操作？ -->

### 1.2 责任范围（本文档管什么）

<!-- 填写：正向声明——本文档涵盖哪些操作 -->

- {覆盖的操作1}
- {覆盖的操作2}

### 1.3 责任边界（本文档不管什么）

<!-- 填写：负向声明——明确排除什么操作、以哪个文件为准 -->

- {排除的操作 → 以哪个 runbook 为准}

---

## 2. 前置条件

| 条件 | 检查方式 |
|------|---------|
| {如：数据库连接正常} | {如：`ping db-host`} |
| {如：配置文件已就绪} | {如：检查 `config.yaml` 存在} |

---

## 3. 执行频率与耗时

| 字段 | 值 |
|------|-----|
| 执行频率 | {如：每日 / 每周 / 按需} |
| 预计耗时 | {如：5 分钟} |
| 可并发执行 | {是 / 否} |
| 维护窗口 | {如：每日凌晨 2:00-3:00 GMT+8} |

---

## 4. 操作步骤

<!-- 每个步骤按需复制此结构。变量 <XXX> 在步骤执行前替换为实际值。 -->

### 4.1 {步骤名称}

| 字段 | 内容 |
|------|------|
| 操作 | {具体操作命令或操作} |
| 验证 | {如何验证操作成功} |
| 预期输出 | {预期输出} |
| 失败处理 | {失败时的回退操作} |

## 5. 验证清单

| # | 检查项 | 通过条件 |
|---|--------|---------|
| 1 | {检查项} | {通过条件} |
| 2 | {检查项} | {通过条件} |

## 6. 回滚方案

<!-- 填写：如果操作出问题，怎么回滚？ -->

## 7. AI 自治权限标注

<!-- 填写：AI 对本 runbook 的操作权限。合法值见 PS-STD-001 §10.3：
  - immutable_core：不可变核心，AI 禁止修改
  - human_gated：AI 需 Owner 批准才能修改
  - ai_editable：AI 可自主修改
-->

| 规则区域 | AI 自治权限 | 说明 |
|---------|:---:|------|
| 操作步骤 | human_gated | 操作步骤变更需 Owner 确认 |
| 前置条件检查 | ai_editable | AI 可自主补充检查项 |
| 回滚方案 | human_gated | 回滚操作不可逆，需谨慎 |

## 8. TTL 与生命周期

<!-- 填写：本文档的保留期限和过期处理方式。 -->

| 字段 | 值 |
|------|-----|
| TTL | permanent |
| 审查周期 | 每 90 天或每次执行后 |
| 过期处理 | 如被新 runbook 取代，按废弃流程标记 deprecated |
| 最后审查日期 | {YYYY-MM-DD} |

## 9. 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| {YYYY-MM-DD} | 0.1.0 | 初始版本 |
