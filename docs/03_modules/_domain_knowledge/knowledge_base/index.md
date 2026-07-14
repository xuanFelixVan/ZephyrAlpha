---
doc_type: index
status: active
title: "knowledge_base — 目录索引"
module_id: MOD-KB-001
blueprint_id: MOD-KB-001
version: "0.12.1"
created: "2026-05-06"
updated: "2026-06-22"
ttl: permanent
---

# knowledge_base

> 本文件由 `generate_missing_index_md.py` 自动生成（后经手动校正）
> 生成日期：2026-06-22

## 模块概览

| 维度 | 详情 |
|------|------|
| 蓝图路径 | [blueprint.md](./blueprint.md) |
| 代码路径 | `src/zephyr/gov_kb/` |
| KE存放路径 | `docs/08_knowledge/` |
| 施工进度 | completed（G1-G5 五门禁已实现） |
| MCP Server | `src/zephyr/integration/mcp/knowledge_base_server.py` |
| KE Schema | `src/zephyr/shared/schemas.py`（KeEntry） |
| 核心入口 | `src/zephyr/gov_kb/kb_repo.py` |

## G1-G5 五门禁流水线（已实现）

| 门禁 | 代码文件 | 说明 |
|:---:|------|------|
| G1 摄取 | `src/zephyr/gov_kb/ingest.py` | 摄取门禁 |
| G2 分拣 | `src/zephyr/gov_kb/triage.py` | 分拣门禁 |
| G3 分析 | `src/zephyr/gov_kb/analyze.py` | 分析门禁 |
| G4 激活 | `src/zephyr/gov_kb/activate.py` | 激活门禁 |
| G5 提取 | `src/zephyr/gov_kb/extract.py` | 提取门禁 |

## 容量升级 Phase 规划（§0.7）

| Phase | 优先级 | 状态 | 说明 |
|-------|:---:|:---:|------|
| Phase C0 | P0 | 📋 | ID 体系扩容 + 并发基础设施 |
| Phase C1 | P0 | 📋 | 脚本执行引擎 + 增量扫描 |
| Phase C2 | P1 | 📋 | 事件总线 + 速率限制 |
| Phase C3 | P2 | 📋 | 知识隔离 + 分片 + 预算重算 |

## 目录内容

| 文件/目录 | 类型 | 说明 |
|-----------|------|------|
| `blueprint.md` | 蓝图 | 知识库系统完整蓝图 v0.12.1 |
| `changes/` | 目录 | 变更记录 |

## 导航

- [上级目录](../index.md)
