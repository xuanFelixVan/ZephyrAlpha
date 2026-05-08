# MOD-MASTER-001 跨系统集成契约注册中心

> **模块类型**：Master Blueprint（跨系统集成 SSoT）
> **蓝图文件**：[blueprint.md](../blueprint.md)
> **状态**：v0.1.0 — 施工中
> **优先级**：P0

## 模块定位

本模块是 ZephyrAlpha 12 个基础设施系统之间集成关系的 canonical SSoT（单一真源）。

- **不做代码实现**——仅定义 54 条 CT-* 集成契约
- 模块蓝图定义"内部怎么干"，本蓝图定义"之间怎么连"
- 违反本蓝图定义的任何集成行为均构成架构违规（AP1）

## 目录结构

```
_master-blueprint/
├── index.md                       ← 本文件
├── changes/
│   └── MOD-MASTER-001/
│       ├── README.md              ← 变更目录说明
│       ├── TASK-MST-0001.md       ← 真源优先级宪章
│       ├── TASK-MST-0002.md       ← AI Agent 冷启动分派表
│       ├── TASK-MST-0003.md       ← 模块骨架搭建
│       ├── ...
│       └── TASK-MST-0033.md       ← 全版本管理
```

## 核心导航

| 入口 | 路径 | 说明 |
|------|------|------|
| 蓝图正文 | `D:\ZephyrAlpha\docs\03_modules\_master-blueprint\blueprint.md` | 54 条 CT-* 契约定义 |
| 代码落地 | `D:\ZephyrAlpha\src\zephyr\orchestrator\contract_registry.py` | 契约注册表 |
| 代码落地 | `D:\ZephyrAlpha\src\zephyr\gates\truth_source_validator.py` | 真源优先级裁决器 |
| 代码落地 | `D:\ZephyrAlpha\src\zephyr\context_engine\dispatch_table.py` | AI 分派表 |

## 12 个集成系统

| # | 系统 | 模块蓝图 | 关键 CT-* |
|---|------|:---:|------|
| 1 | Agent Orchestrator | MOD-INF-006 | CT-ORC-SCRIPT, CT-ORC-CE, CT-ORC-VMS, CT-ORC-GATE, CT-ORC-DB |
| 2 | Script System | MOD-INF-005 | CT-ORC-SCRIPT, CT-SCRIPT-KB, CT-SCRIPT-GATE |
| 3 | Knowledge Base | MOD-KB-001 | CT-SCRIPT-KB, CT-KB-VMS |
| 4 | Gate Engine | MOD-INF-007 | CT-ORC-GATE, CT-SCRIPT-GATE |
| 5 | Context Engine | MOD-INF-008 | CT-ORC-CE, CT-CE-VMS, CT-CE-LSG |
| 6 | Task Pipeline | MOD-INF-009 | CT-PIPE-ORC |
| 7 | Feedback Loop Engine | MOD-INF-010 | CT-FLE-ORC, CT-FLE-DB, CT-TELE-FLE |
| 8 | Vector Memory Service | MOD-INF-011 | CT-ORC-VMS, CT-CE-VMS, CT-KB-VMS |
| 9 | Database | MOD-INF-012 | CT-FLE-DB, CT-ORC-DB |
| 10 | MCP Servers | MOD-INF-013 | — |
| 11 | LLM Security Gateway | MOD-INF-014 | CT-CE-LSG |
| 12 | System Telemetry | MOD-INF-015 | CT-TELE-FLE |
