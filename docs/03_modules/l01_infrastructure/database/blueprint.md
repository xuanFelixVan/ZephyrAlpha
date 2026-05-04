---
module_id: "MOD-INF-012"
title: "Database 蓝图 — SQLite 元数据 + ATM 原子事务管理器"
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
summary: "ZephyrAlpha Database 蓝图——SQLite 元数据持久化 + 原子事务管理器(ATM)：跨SQLite/文件系统的两阶段提交。task_repo.py 提供10状态任务CRUD + N:N task_files映射 + events审计日志。olap_engine.py 提供FLE时序分析。对标 SQLite 官方WAL模式 + ITIL SACM CMDB（每个CI一条记录）。"
tags: [database, db, sqlite, atm, atomic-transaction, task-repo, olap, infrastructure]
priority: P1
depends_on:
  - {target: "MOD-INF-006", at: "§3.2.1", why: "task_repo.py——TaskCard数据层真源"}
  - {target: "MOD-INF-010", at: "§2.1", why: "FLE——olap_engine时序消费方"}
  - {target: "architecture-model/layers/b_db.yaml", at: "全篇", why: "DB YAML SSoT——本蓝图真源"}
---

# Database 蓝图

> **module_id**: MOD-INF-012 | **version**: 0.1.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图的 canonical SSoT 为 [b_db.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_db.yaml)。
> 代码落位：`src/zephyr/db/`（4 个 .py 文件）。已实现。

> **对标**：SQLite WAL 模式 + ITIL SACM CMDB + 分布式事务两阶段提交模式。

---

## 1. 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-012 |
| 代码落位 | `src/zephyr/db/` |
| 核心职责 | 元数据持久化 + 跨存储的原子事务保证 |

### 核心职能

**db 是系统的"账本"**——所有需要"绝对不能丢"的数据写入这里：任务状态、审计事件、FLE 时序指标。ATM 保证"要么全写完，要么全不写"——不能出现"任务标记 COMPLETED 了但审计日志没写入"的情况。

---

## 2. 文件组成

| 文件 | 职责 |
|------|------|
| `task_repo.py` | 任务 CRUD + 10状态机 + N:N task_files + events 审计日志 |
| `atomic_transaction_manager.py` | ATM——跨 SQLite/文件系统两阶段提交 |
| `sqlite_schema.py` | SQLite 表结构定义（DDL）|
| `olap_engine.py` | OLAP 时序分析引擎——供 FLE 指标基线计算 |

---

## 3. ATM 原子事务管理器

```yaml
atm_contract: P0-DB-ATM
description: "跨 SQLite / 文件系统的两阶段提交"

phase_1_prepare:
  - 所有参与者（SQLite + 文件系统操作）进入 PREPARE 状态
  - 任何参与者 PREPARE 失败 → 全部 ROLLBACK

phase_2_commit:
  - 所有参与者 PREPARE 成功 → 依次 COMMIT
  - COMMIT 失败 → 已 COMMIT 的参与者不逆（at-least-once 语义）

timeout: 3s
fallback: WAL 模式自动回退 → 不丢数据
```

---

## 4. task_repo.py 核心接口

```python
class TaskRepo:
    def create(task: TaskCard) -> TaskCard
    def get(task_id: str) -> Optional[TaskCard]
    def update(task_id: str, updates: dict) -> TaskCard
    def transition(task_id: str, to_status: Status) -> TaskCard
    def list_by_status(status: Status) -> list[TaskCard]
    def get_history(task_id: str) -> list[Event]  # append-only audit
```

状态转换时自动写入 events 表（不可变审计日志）。

---

## 5. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Phase 0 | task_repo.py + sqlite_schema.py + ATM | ✅ implemented |
| Phase 1 | olap_engine 供 FLE 消费 | 📋 Backlog |

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 数据库——task_repo+sqlite_schema+ATM已实现，olap_engine待施工

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/db/atomic_transaction_manager.py` | ✅ 已实现 | |
| `src/zephyr/db/olap_engine.py` | ✅ 已实现 | |
| `src/zephyr/db/sqlite_schema.py` | ✅ 已实现 | |
| `src/zephyr/db/task_repo.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_task_repo.py` | ✅ 已实现 | |
| `tests/unit/test_sqlite_schema.py` | ✅ 已实现 | |
| `tests/unit/test_atomic_transaction_manager.py` | ✅ 已实现 | |
| `tests/unit/test_olap_engine.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
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
| 2026-05-03 | 0.1.0 | 初始创建——从 b_db.yaml SSoT 派生。ATM两阶段提交 + task_repo 10状态CRUD。 |
