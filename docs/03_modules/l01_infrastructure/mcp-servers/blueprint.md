---
module_id: "MOD-INF-013"
title: "MCP Servers 蓝图 — stdio 协议向外部 IDE/Agent 暴露系统能力"
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
construction_progress: phase_1_complete
summary: "ZephyrAlpha MCP Servers 蓝图——6个 MCP 服务端通过 stdio 协议暴露内部系统能力：task_manager(已实现decompose_blueprint) / knowledge_base / gate_engine / doc_guard / sentinel。tool_contracts.yaml 定义工具契约。对标 MCP (Model Context Protocol) 2024-11-05 规范。"
tags: [mcp, mcp-servers, stdio, tool-contracts, model-context-protocol, external-api, infrastructure]
priority: P1
depends_on:
  - {target: "MOD-INF-006", at: "§3.2.1", why: "task_manager MCP——decompose_blueprint接口"}
  - {target: "MOD-KB-001", at: "§4", why: "knowledge_base MCP——KE查询接口"}
  - {target: "MOD-INF-007", at: "§3.2", why: "gate_engine MCP——Gate判定接口"}
  - {target: "architecture-model/layers/b_mcp.yaml", at: "全篇", why: "MCP YAML SSoT——本蓝图真源"}
---

# MCP Servers 蓝图

> **module_id**: MOD-INF-013 | **version**: 0.1.0 | **status**: draft | **layer**: cross_layer

> 真源声明：本蓝图的 canonical SSoT 为 [b_mcp.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_mcp.yaml)。
> 代码落位：`src/zephyr/mcp/`（8 个文件，其中 task_manager 已实现 decompose_blueprint，blueprint_search 已实现 find_relevant_blueprint）。

> **对标**：MCP (Model Context Protocol) 2024-11-05 规范 + Anthropic Tool Use 模式。

---

## 1. 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-013 |
| 代码落位 | `src/zephyr/mcp/` |
| 核心职责 | 向外部 IDE/Agent 暴露内部系统能力的统一接口 |

### 核心职能

**MCP 是系统的"对外服务窗口"**——外部 Agent（Trae IDE、Claude Code、Cursor）通过 stdio 连接 MCP 服务端 → 获得任务管理/知识查询/门禁决策等能力。里面 12 个系统各干各的，外部只需要连 MCP 这一个入口。

---

## 2. 六个 MCP 服务端

| 服务端 | 文件 | 实现状态 | 暴露能力 |
|------|------|:---:|------|
| **task_manager** | `task_manager_server.py` | ✅ 已实现 decompose_blueprint | 蓝图→任务卡拆解 |
| **knowledge_base** | `knowledge_base_server.py` | stub | KE 查询/创建 |
| **gate_engine** | `gate_engine_server.py` | stub | Gate 判定/熔断状态 |
| **doc_guard** | `doc_guard_server.py` | stub | 文档安全校验 |
| **sentinel** | `sentinel_server.py` | stub | 系统哨兵监控 |
| **_base_server** | `_base_server.py` | ✅ | 公共基类 |

---

## 3. 协议与契约

- **通信协议**：MCP stdio（标准输入/输出流）
- **契约定义**：`tool_contracts.yaml`
- **工具调用模式**：request→response，同步阻塞模型
- **认证**：当前无——本地 stdio 进程内通信，无需网络层认证

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Phase 0 | task_manager decompose_blueprint + _base_server | ✅ implemented |
| Phase 1 | knowledge_base / gate_engine MCP 实现 | 📋 Backlog |

---

## 5. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> MCP服务器——task_manager decompose_blueprint已实现

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/mcp/_base_server.py` | ✅ 已实现 | |
| `src/zephyr/mcp/doc_guard_server.py` | ✅ 已实现 | |
| `src/zephyr/mcp/gate_engine_server.py` | ✅ 已实现 | |
| `src/zephyr/mcp/knowledge_base_server.py` | ✅ 已实现 | |
| `src/zephyr/mcp/sentinel_server.py` | ✅ 已实现 | |
| `src/zephyr/mcp/task_manager_server.py` | ✅ 已实现 | |
| `src/zephyr/mcp/blueprint_search_server.py` | ✅ 已实现 | P0-2 MCP 蓝图检索 tool —— Phase 1e T-V2-010 |
| `src/zephyr/mcp/tool_contracts.yaml` | ✅ 已实现 | |

### 5.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_mcp_servers.py` | ✅ 已实现 | |
| `tests/integration/test_mcp_e2e.py` | ✅ 已实现 | |

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
| 2026-05-03 | 0.1.0 | 初始创建——从 b_mcp.yaml SSoT 派生。6 MCP服务器 + stdio协议 + tool_contracts。 |
| 2026-05-03 | 0.1.1 | P1升级——追加 §6核心调用流程、§7集成依赖、§11施工指引（对标金标准13节）。 |
| 2026-05-04 | 0.1.2 | P0-2 MCP 蓝图检索 tool 落地——新增 `src/zephyr/mcp/blueprint_search_server.py`（BlueprintSearchServer + `find_relevant_blueprint` tool）。AI agent 通过 MCP 查询当前任务该读哪份蓝图。关联文件：`config/blueprint_routing.yaml`（关键字路由表）。关联蓝图：MOD-INF-009 §8（触发路由表）。关联决策：R90。 |
