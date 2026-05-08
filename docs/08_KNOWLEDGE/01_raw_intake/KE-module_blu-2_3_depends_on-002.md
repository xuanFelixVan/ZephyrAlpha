---
module_id: KE-module_blu-2_3_depends_on-002
title: 2.3 depends_on 声明
category: module_blueprint
---

# 2.3 depends_on 声明

2.3 depends_on 声明

本蓝图（MOD-KB-001）作为知识库模块的蓝图，**直接依赖**以下模块/标准的设计契约：

| 依赖目标 | 引用位置 | 为什么依赖 | 耦合程度 |
|---------|---------|-----------|:---:|
| MOD-INF-006 | §3.2 + §4.2 | TaskCard 模型 + task_id 格式（`{NAMESPACE}-{SEQ}`）——KB 自己的施工任务用 TaskCard 追踪 | 强 |
| MOD-INF-006 | §5.1 | `context_assembler` 的 KE 知识注入接口——上下文引擎通过此接口拉取 KB 知识 | 强 |
| MOD-INF-006 | §4.2 | 10 状态任务状态机——KB 施工任务状态管理引用此状态机 | 中 |
| MOD-INF-005 | §6.3 + §6.6 | 脚本系统 MEDIUM Finding → KB 入库（C4→G1）——Finding→KE 数据格式转换 | 强 |
| MOD-INF-005 | §3.6 | 脚本系统标签体系（`[Quick]`/`[Security]` 等）——KB 的 tags 字段对齐脚本系统标签 | 中 |
| PS-STD-001 | §3 | doc_type 受控词表——知识条目的 doc_type 注册 | 中 |
| PS-STD-004 | §5 | domain 枚举——知识 domain 分类与冲突仲裁 | 弱 |
| ADR-0016 | 全文 | ChromaDB + BGE-M3 向量存储技术选型 | 中 |
| ADR-0031 | 全文 | ChromaDB 向量检索方案细节 | 中 |

> **耦合说明**：KB 系统是一个"基础设施模块"——它**服务**于任务系统（追踪施工）、上下文引擎（注入知识）、审计系统（记录决策）。
> KB 出问题会**连锁影响**这三个上游消费者。因此 depends_on 强耦合 = KB 变更时必须通知对方。
> 大白话：知识库不是孤岛——任务系统靠它追踪进度，上下文引擎靠它喂资料给 AI，审计系统靠它留证据。改了知识库的结构，这三个兄弟都得知道。

---
