---
module_id: MOD-INF-017
title: "代码去重引擎 — 目录索引"
doc_type: index
status: draft
version: "0.1.0"
layer: L01
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
created_by: AI
date: "2026-05-03"
ttl: permanent
summary: "code-dedup-engine/ 模块目录索引。语义级代码重复检测引擎——消除 Vibe Coding AI 上下文失忆导致的重复代码。"
depends_on:
  - target: 03_modules/l01_infrastructure/index.md
    at: module-list
    why: "本模块在 L01 基础设施层中登记"
---

# code-dedup-engine — 代码去重引擎

## 责任声明（Single Responsibility）

本模块负责：**语义级代码重复检测——检测词法不同但语义相同的函数/常量定义，消除 Vibe Coding AI 的上下文失忆导致的重复造轮子**。

## 文件清单

| 文件 | 说明 |
|------|------|
| blueprint.md | 代码去重引擎蓝图（MOD-INF-017 v0.1.0） |
| index.md | 本文件 |

## 当前状态

`draft` — 蓝图已编写，施工待 Phase 2。

## 排除规则

- ❌ 不负责代码格式化/风格检查 → `01_policies_and_standards/`
- ❌ 不负责测试覆盖率 → CI 管线

## 父级目录

- 父级：[L01 基础设施层](../index.md)
