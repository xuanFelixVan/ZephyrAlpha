---
module_id: "MOD-INF-011"
title: "Vector Memory Service 蓝图 — ChromaDB 5 Collection 统一向量持久化"
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
summary: "ZephyrAlpha VMS 蓝图——ChromaDB 0.6 + BGE-M3 ONNX本地推理。5大Collection: decisions / code_context / lessons / knowledge / runtime_logs。Phase 3整合 kb/ 能力入 InProcessVectorMemory。当前 skeleton——代码目录存在但文件为空。对标 ChromaDB 官方最佳实践 + VectorDB设计模式。"
tags: [vector-memory, vms, chromadb, bge-m3, embedding, vector-db, collections, infrastructure]
priority: P1
depends_on:
  - {target: "MOD-MASTER-001", at: "§2.6", why: "CT-CE-VMS-001 集成契约——CE→VMS向量检索"}
  - {target: "MOD-KB-001", at: "§1.5", why: "知识库——Phase 3 VMS整合目标"}
  - {target: "MOD-INF-008", at: "§2.1", why: "CE——VMS的主要消费方"}
  - {target: "architecture-model/layers/b_vector_memory.yaml", at: "全篇", why: "VMS YAML SSoT——本蓝图真源"}
---

# Vector Memory Service 蓝图

> **module_id**: MOD-INF-011 | **version**: 0.1.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图的 canonical SSoT 为 [b_vector_memory.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_vector_memory.yaml)。
> 代码落位：`src/zephyr/vector_memory/`。当前 skeleton——目录+`__init__.py` docstring 存在，代码文件未填充。
> Phase 1 过渡期由 `src/zephyr/kb/` 承担部分能力，Phase 3 整合。

> **对标**：ChromaDB 0.6 官方最佳实践 + BGE-M3 ONNX 本地推理 + VectorDB 四层设计模式（Collection→Index→Embedding→Query）。

---

## 1. 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-011 |
| 代码落位 | `src/zephyr/vector_memory/` |
| 当前状态 | skeleton（目录存在但文件空白）|
| 过渡期能力承载 | `src/zephyr/kb/` Phase 2 |
| 整合时间线 | Phase 3 → kb/ 并入 VMS |

### 核心职能

**VMS 是全系统的统一向量记忆体**——所有系统（Orc、KB、CE、FLE）产出的需要语义检索的内容，最终都写入 VMS。相当于"全系统共用的搜索引擎索引"——不是每个系统自己建索引，而是统一用一个。

---

## 2. 五大 Collection Schema

| Collection | 写入方 | 读取方 | 存储内容 | 预估规模 |
|------|:---:|:---:|------|:---:|
| **decisions** | Orchestrator | CE、FLE | 任务决策记录（做了什么+为什么）| 1000-5000 vectors |
| **code_context** | Script System、Orc | CE | 代码上下文片段（相关文件摘要）| 500-2000 vectors |
| **lessons** | FLE、Script System | CE、KB | 经验教训（KE的向量形态）| 100-500 vectors |
| **knowledge** | KB | CE | 知识条目（KE全文向量）| 100-1000 vectors |
| **runtime_logs** | All systems | FLE、CE | 运行时日志语义摘要 | 1000-5000 vectors |

---

## 3. 技术选型

| 维度 | 选择 | 理由 |
|------|------|------|
| 向量数据库 | ChromaDB 0.6 | 本地嵌入式，Python原生，零运维 |
| 嵌入模型 | BGE-M3 ONNX | 1024维，本地推理免API费，中英文双语 |
| 推理方式 | ONNX Runtime | 免GPU，CPU可跑，延迟 <50ms/条 |
| 批量大小 | 16 | 单次embedding 16条，控制内存 |
| 距离度量 | cosine | ChromaDB 默认，语义相似标准度量 |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Phase 1 | `__init__.py` docstring + 空目录骨架 | ✅ skeleton |
| Phase 2 | ChromaDB 初始化 + BGE-M3 ONNX 加载 | 📋 Backlog |
| Phase 3 | kb/ 能力整合 → 5 Collection 完整实现 | 📋 Backlog |

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 向量记忆——仅目录+__init__.py docstring

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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
| 2026-05-03 | 0.1.0 | 初始创建——从 b_vector_memory.yaml SSoT 派生。5 Collection Schema + ChromaDB+BGE-M3技术选型。 |
