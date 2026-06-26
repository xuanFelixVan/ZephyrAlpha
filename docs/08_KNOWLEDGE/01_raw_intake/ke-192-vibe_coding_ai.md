---
module_id: KE-172--------006
status: active
title: 2.1B Vibe Coding 2.0 AI 基础设施技术选型（17 项聚焦视图）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.1B Vibe Coding 2.0 AI 基础设施技术选型（17 项聚焦视图）

2.1B Vibe Coding 2.0 AI 基础设施技术选型（17 项聚焦视图）

> 新增于 v2.1.0（2026-04-24）。源自 `vibe-coding-audit-merged.md` Qwen 17 项技术选型共识，是 AI 基础设施的**强约束选型**。

**权威真源**：[`architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml`](architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml)（17 项 AI 基础设施选型） + [`architecture_model/technology/technology_landscape.yaml`](architecture_model/technology/technology_landscape.yaml)（43 项全技术栈雷达）

**两者关系**：

| 维度 | `vibe_coding_infrastructure_tech_stack.yaml`（AI 基础设施聚焦）| `technology_landscape.yaml`（全技术栈雷达）|
|------|----------------------------------------------------|---------------------------------------------------------|
| 覆盖范围 | 6 大核心服务的 17 项 AI 基础设施选型 | 全技术栈 43 项（含业务层数据库、调度器等）|
| 分类方式 | 按服务分组 + 升级阈值看板 + ADR 对应 | ThoughtWorks Radar 四象限（adopt/trial/assess/hold）|
| 约束强度 | **强约束**（experimental 必须使用首选方案）| 推荐性（部分项目仍 pending）|
| 消费方 | KBG-0015 ~ KBG-0020 + 6 份接口规范 | 整体架构规划 + CI 审计 |
| 关系 | 前者是后者的**聚焦子集**（特别关注 AI 基础设施部分）| — |

**17 项核心选型按服务分组**：

| 服务 | 项数 | 代表选型 |
|------|:----:|---------|
| Context Engine | 3 | NetworkX 3.2 / Qwen2.5-3B ONNX / 规则基降级 |
| Vector Memory | 3 | ChromaDB 0.6 / BGE-M3 ONNX / 递归字符分块 |
| Agent Orchestrator | 5 | SQLite + asyncio.Queue / 状态机 Enum / filelock |
| Agent Sandbox | 1 | Windows ACL + 只读挂载 |
| Feedback Loop | 2 | SQLite 时间序列 / EMA 异常检测 |
| LLM Security Gateway | 3 | Pydantic v2 / 正则 Pattern 库 / git-secrets |

**升级阈值看板**：新 landscape 的 `upgrade_watchboard` 段定义了 8 项关键升级触发条件（如 ChromaDB > 500MB、并发任务 > 20、红队绕过率 > 5%），由 Feedback Loop Engine 自动上报。

**对应 ADR**：

- KBG-0015 Context Engine 架构
- KBG-0016 Vector Memory 技术栈
- KBG-0017 Agent Orchestrator 任务队列与状态机
- KBG-0018 Agent Sandbox 实现选择
- KBG-0019 Feedback Loop Engine 时序存储与异常检测
- KBG-0020 LLM Security Gateway 设计
