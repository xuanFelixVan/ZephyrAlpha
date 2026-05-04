---
module_id: "MOD-INF-016"
title: "Shared + Core 蓝图 — 跨层共享基础设施"
doc_type: blueprint
status: draft
version: "0.1.1"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
summary: "ZephyrAlpha Shared + Core 蓝图——Shared: 跨层数据契约(Instrument/Money/Timestamp) + SSoT守卫 + 观察者事件总线 + 能力定义 + 内容指纹 + DOS启动器。Core: 蓝图分解器(blueprint_decomposer) + 核心数据模型(models.py)。对标 Google Monorepo shared/ 模式 + DDD Shared Kernel。"
tags: [shared, core, cross-layer, contracts, ssot-guard, event-bus, blueprint-decomposer, infrastructure]
priority: P2
depends_on:
  - {target: "architecture-model/layers/b_shared.yaml", at: "全篇", why: "Shared YAML SSoT——本蓝图真源"}
  - {target: "architecture-model/layers/b_core.yaml", at: "全篇", why: "Core YAML SSoT——本蓝图真源"}
---

# Shared + Core 蓝图

> **module_id**: MOD-INF-016 | **version**: 0.1.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：Shared canon SSoT 为 [b_shared.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_shared.yaml)；
> Core canon SSoT 为 [b_core.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_core.yaml)。
> Shared + Core 合并为一个蓝图（两者均为跨层基础设施，且体积较小）。

> **对标**：Google Monorepo `shared/` 模式 + DDD Shared Kernel（跨限界上下文共享领域模型）。

---

## 1. 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-016 |
| 涵盖 | Shared (`src/zephyr/shared/`) + Core (`src/zephyr/core/`) |
| 核心职责 | 提供所有系统共用的数据模型、基础设施、工具函数 |

---

## 2. Shared 模块（2 子模块, 10 文件）

### 2.1 shared-contracts（跨层数据契约）

| 文件 | 职责 |
|------|------|
| `instrument.py` | 金融 Instrument 模型（symbol/name/asset_type）|
| `money.py` | 货币金额模型 + 汇兑 |
| `timestamp.py` | 时间戳模型（ISO 8601 含时区）|
| `runtime_plane_tag.py` | 运行时平面标签（cold/warm/hot）|

### 2.2 shared-infra（共享基础设施）

| 文件 | 职责 |
|------|------|
| `schemas.py` | **Task 28字段 Pydantic V2 模型**——TaskCard 基座 |
| `ssot_guard.py` | SSoT 守卫——防止多个文件定义同一概念 |
| `observer.py` | 观察者事件总线——系统间松耦合消息通知 |
| `capability.py` | 能力定义——系统能力注册与发现 |
| `content_fingerprint.py` | 内容指纹——文件内容哈希去重 |
| `dos_launcher.py` | DOS 启动器——Windows 兼容性工具 |

---

## 3. Core 模块（1 子模块, 2 文件）

| 文件 | 职责 |
|------|------|
| `blueprint_decomposer.py` | 蓝图分解器——蓝图.md → 多个 TaskCard |
| `models.py` | 核心数据模型（v0.2.0 TaskCard，待升级到 v0.3.0 对齐 schemas.py Task）|

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Phase 0 | 全部 12 文件已实现 | ✅ implemented |
| Phase 1 | models.py 升级到 v0.3.0（继承 schemas.py Task 28字段）| 📋 Backlog |

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 共享+核心——全部12文件已实现

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/shared/API_INDEX.py` | ✅ 已实现 | |
| `src/zephyr/shared/capability.py` | ✅ 已实现 | |
| `src/zephyr/shared/content_fingerprint.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/instrument.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/money.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/runtime_plane_tag.py` | ✅ 已实现 | |
| `src/zephyr/shared/contracts/timestamp.py` | ✅ 已实现 | |
| `src/zephyr/shared/dos_launcher.py` | ✅ 已实现 | |
| `src/zephyr/shared/frontmatter_utils.py` | ✅ 已实现 | |
| `src/zephyr/shared/observer.py` | ✅ 已实现 | |
| `src/zephyr/shared/paths.py` | ✅ 已实现 | |
| `src/zephyr/shared/schemas.py` | ✅ 已实现 | |
| `src/zephyr/shared/ssot_guard.py` | ✅ 已实现 | |
| `src/zephyr/shared/time_utils.py` | ✅ 已实现 | |
| `src/zephyr/shared/token_utils.py` | ✅ 已实现 | |
| `src/zephyr/core/blueprint_decomposer.py` | ✅ 已实现 | |
| `src/zephyr/core/models.py` | ✅ 已实现 | |

### 5.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_schemas.py` | ✅ 已实现 | |
| `tests/unit/test_ssot_guard.py` | ✅ 已实现 | |
| `tests/unit/test_capability.py` | ✅ 已实现 | |
| `tests/unit/test_money.py` | ✅ 已实现 | |
| `tests/unit/test_instrument.py` | ✅ 已实现 | |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-03 | 0.1.0 | 初始创建——合并 Shared YAML + Core YAML。2 系统 12 文件清单。 |
