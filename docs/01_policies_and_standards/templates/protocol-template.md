---
module_id: ""
title: ""
doc_type: protocol
status: draft
version: "0.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: ""
ttl: permanent
summary: ""
tags: []
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on: []
ai_autonomy: human_gated
evolution_policy: ""
---

# {协议名称}

> module_id: {填写} | version: 0.1.0 | status: draft | layer: cross_layer | protocol_type: {handoff / interaction / emergency}

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
