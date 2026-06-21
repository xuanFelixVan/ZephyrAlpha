---
ai_autonomy: human_gated
classification: confidential
completeness: unknown
created_by: human_plus_agent
date: ''
depends_on: []
doc_type: template
evolution_policy: ''
language: zh
layer: cross_layer
module_id: GOV-031
owner: ZephyrAlpha-Owner
rule_form: declarative
scope: global
stability: evolving
status: Draft
summary: 协议文档创建模板——定义交互流程和消息时序，新建 protocol 类文档时使用此模板
tags: []
template_for: protocol
title: Protocol Template
ttl: permanent
verifiability: manual
version: 0.1.0
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
协议文档模板 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/d3_metadata/check_template_compliance.py <文档路径> --template protocol
-->
<!--
REQUIRED_SECTIONS:
  overview: "概述"
  s1: "1. 协议类型与适用范围"
  s2: "2. 参与方"
  s3: "3. 前置条件"
  s4: "4. 交互流程"
  s5: "5. 成功条件"
  s6: "6. 失败处理"
  s7: "7. 版本兼容"
  s8: "8. AI 自治权限标注"
  s9: "9. TTL 与生命周期"
  s10: "10. 变更记录"
END_REQUIRED_SECTIONS
-->

# {协议名称}

> module_id: {填写} | version: 0.1.0 | status: draft | layer: cross_layer | protocol_type: {handoff / interaction / emergency}

---

## 概述

> ⚠️ **必填**。AI 阅读本文档的第一段——3~5 句话建立心理模型。
> 写清楚：这个协议是什么、参与方是谁、适用什么场景、为什么存在。

{本协议文档定义 {协议名称} 的交互流程——参与方 {角色A} 与 {角色B} 之间的消息时序和职责划分。适用场景：{场景描述}。协议类型：{handoff — AI session 间交接 / interaction — 多模块协作 / emergency — 事故应急}。核心目标：{一句话描述协议要达成的结果}。}

---

## 1. 协议类型与适用范围

| 字段 | 值 |
|------|-----|
| 协议类型 | {handoff — AI session 间交接 / interaction — 多模块协作 / emergency — 事故应急} |
| 适用范围 | {描述什么场景下适用此协议} |
| 不适用的场景 | {明确排除的场景} |

---

## 2. 参与方

| 角色 | 负责方 | 职责 |
|------|--------|------|
| {角色A} | {负责方} | {职责描述} |

---

## 3. 前置条件

- {条件1}
- {条件2}

---

## 4. 交互流程

| 步骤 | 发起方 | 接收方 | 操作 | 预期结果 |
|:----:|--------|--------|------|---------|
| 1 | {角色A} | {角色B} | {操作} | {预期结果} |

---

## 5. 成功条件

- {条件1}

---

## 6. 失败处理

| 失败场景 | 回退操作 | 通知对象 |
|---------|---------|---------|
| {场景} | {回退} | {通知谁} |

---

## 7. 版本兼容

| 协议版本 | 兼容版本 | 不兼容版本 | 迁移说明 |
|:-------:|----------|----------|---------|
| 0.1.0 | —（初始版本） | — | — |

---

## 8. AI 自治权限标注

<!-- 填写：AI 对本协议的操作权限。协议类文档通常是 human_gated——涉及多方交互的规则变更需 Owner 审批。 -->

| 操作 | AI 自治权限 | 说明 |
|------|:---:|------|
| 新增交互步骤 | human_gated | 交互流程变更涉及多方协调 |
| 修改失败处理 | human_gated | 失败处理的变更需谨慎 |
| 更新版本兼容表 | ai_editable | AI 可自主更新版本兼容信息 |
| 补充参与方信息 | ai_editable | AI 可自主补充参与方详情 |

## 9. TTL 与生命周期

<!-- 填写：协议通常是 permanent（长期维护），但 handoff 协议可能随 Phase 变化调整。 -->

| 字段 | 值 |
|------|-----|
| TTL | permanent |
| 审查周期 | 每 90 天或版本变更时 |
| 过期处理 | 如被新版本协议取代，按废弃流程标记 deprecated |
| 最后审查日期 | {YYYY-MM-DD} |

## 10. 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| {YYYY-MM-DD} | 0.1.0 | 初始版本 |
