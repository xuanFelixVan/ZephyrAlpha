---
ttl: permanent
doc_type: index
title: ZephyrAlpha 项目文档库 / Project Documentation Hub
owner: ZephyrAlpha-Owner
language: zh
---

# ZephyrAlpha 项目文档库

> 单一入口 · 大白话总览。读完这一篇，即可对 ZephyrAlpha 全貌建立认知。
> 本文件夹是项目架构文档的**唯一汇集点**：项目现状手册（描述"是什么"）+ 架构原则（规范"该怎么"）+ 全景图能力（深度参考）。
> 描述性事实的深度明细外链到 `docs/02_enterprise_architecture/{00,01,02,05,06}/` 的权威 auto-gen 输出，不在本文件夹重复（SSoT 铁律）。

---

## 这是什么项目

ZephyrAlpha 是一个 **AI 原生（AI-native）的量化研究与交易平台**，核心理念是用 AI 治理框架编排量化研究的全生命周期。项目以"接入所有模块、零孤儿率"为终极目标，由 **AutoRuntime Core（系统大脑）** 负责三层 AI 运行时编排、节律调度、健康监控与工作编排。

**一句话**：一个让 AI 自动干量化研究全流程（数据→因子→信号→回测→组合→执行→风控→报告）、且每个 AI 动作都可审计、可回滚、可治理的平台。

### 核心特征

- **AI 治理优先**：所有 AI 行为必须审计、所有组件必须注册 CapabilityCard、所有 LLM 调用必经安全网关（LSG）。
- **SSoT（单一真源）铁律**：规则数据真源为 YAML 文件，架构数据真源为 PostgreSQL depgraph DB，禁止多真源同步。
- **三层 AI 工作分配**：L1 Trae（人在环，免费）→ L2 Local（24/7 本地推理，零成本）→ L3 API（夜班/高价值，付费）。
- **PIT（Point-in-Time）铁律**：回测引擎零前瞻偏差，三平面一致性 + Embargo 期。
- **depgraph 依赖图**：依赖关系唯一真源，AI 查询 depgraph = 零幻觉空间。

---

## 大局架构

ZephyrAlpha 采用 **五层同心圆** 架构（灵感来自 Magentic-One + K8s Controller Manager + Google A2A）：

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoRuntime Core (系统大脑)                │
│  L0 Bootstrap → L1 Reconcile → L2 Execute → L3 Knowledge → L4 Orchestrate
│  - 三层 AI 运行时编排 (L1 Trae / L2 Local / L3 API)           │
│  - MAPE-K reconcile 循环 (孤儿率/健康/任务学习/A2A同步)        │
└─────────────────────┬───────────────────────────────────────┘
                      │
   ┌──────────────────┼──────────────────┐
   ▼                  ▼                  ▼
┌────────┐      ┌──────────┐       ┌──────────┐
│治理域   │      │ 数据集成域│       │ 量化交易域│
│Governance│     │  Data    │       │ Backtest/ │
│ audit/  │      │ scheduler│       │ Factor/   │
│ drift/  │      │ provider │       │ Risk/     │
│ enforce │      │ ch_writer│       │ Exec/     │
└────┬────┘      └────┬─────┘       └────┬─────┘
     └────────────────┼──────────────────┘
                      ▼
           ┌─────────────────────┐
           │ 共享与基础设施层      │
           │ shared / infra /     │
           │ integration / security│
           └─────────────────────┘
```

域按 `layer_id` 分四层（真源：depgraph DB `domains` 表）：

| 层级 | 含义 | 代表域 |
|------|------|--------|
| `L0_infrastructure` | 基础设施 | D_INFRA_RUNTIME / D_INFRA_RECOVERY |
| `L1_foundation` | 基础 | D_SHARED / D_GOVERNANCE |
| `L2_domain` | 领域 | D_BACKTEST / D_FACTOR / D_RISK / D_DATA |
| `L3_application` | 应用 | D_TRADING / D_ORCHESTRATOR |

depgraph 节点两态生命周期：`design`（设计态，蓝图阶段代码未写）→ `production`（运营态，代码已写），状态单调推进禁止倒退。

---

## 项目快照（自动生成）

<!-- AUTO-START:project_snapshot -->
<!-- 数据源：depgraph (PostgreSQL) | 最后同步：2026-08-17 -->

| 指标 | 值 |
|------|----|
| 功能域 / Domains | 73 |
| 代码节点 / Nodes | 6869 |
| 依赖边 / Edges | 14474 |
| 孤儿节点 / Orphans | 0 |
| 运营态占比 / Production ratio | 97.4%（stable+generated） |
<!-- AUTO-END:project_snapshot -->

> 完整统计见 [project_handbook/07_dependencies.md](project_handbook/07_dependencies.md)。

---

## 怎么跑起来

```bash
cd D:\ZephyrAlpha
python -m venv .venv; .\.venv\Scripts\activate
pip install -r requirements.txt
```

| 命令 | 用途 |
|------|------|
| `zephyr [--once] [--interval N]` | AutoRuntime Core 主入口（系统大脑） |
| `integrator status\|run\|start` | 数据源集成器 CLI（8 子命令） |
| `panel serve src/zephyr/frontend/dashboard/app_panel.py --port 5006` | 仪表盘（http://localhost:5006） |
| `docker-compose up` | 全栈容器（core/prometheus/grafana/node-exporter） |

> 详细运行方式见 [project_handbook/01_overview.md](project_handbook/01_overview.md)。

---

## 哪里找什么（导航）

本文件夹分三部分：

| 部分 | 路径 | 回答什么 |
|------|------|---------|
| **项目现状手册** | [project_handbook/](project_handbook/) | 项目**是什么**：仓库布局、数据层、数据源、交易域、治理基础设施、依赖关系（大白话 + AUTO 统计 + 外链权威源） |
| **全景图能力** | [panorama/](panorama/) | depgraph 双态模型、SSoT 分层、生成器角色——AI 干活前必查的依赖与路径全景 |
| **自动化说明** | [_automation/](_automation/) | 哪些文档自动生成、AUTO 标记块清单、触发方式、维护规则 |

> **原则文档层已取消（2026-07-30）**：原 `principles/` 下 10 份原则文档已全部删除——可执行约束由 `architecture_model/cross_cutting/invariants.yaml`（20 条不变量 + fitness function）+ `trae_*.yaml` 规则 + commit gates 强制执行，原则文档是已执行不变量的人类可读副本 + TOGAF/STRIDE 通用教学，无人读、AI 不消费、且与 depgraph 实际状态脱节（如 security_principles.md 称 LSG/Agent Sandbox 为"T1+ deferred 待建"，实证 depgraph 显示早 production）。设计大纲留 git 历史。

### 外部权威源（深度明细，不在本文件夹重复）

| 权威源 | 路径 | 内容 |
|--------|------|------|
| 全局架构图 | `docs/02_enterprise_architecture/01_global_architecture_diagram/` | 全项目树（en/zh）、资产目录、契约目录、跨域矩阵、集成拓扑、能力热图 |
| 域架构文档 | `docs/02_enterprise_architecture/02_domain_architecture_docs/` | 逐域文档（生成器 `generate_domain_doc.py` 产出） |
| 数据流架构 | `docs/02_enterprise_architecture/05_dataflow_architecture/` | 数据清单、数据采集流、数据流图 |
| 决策架构 | `docs/02_enterprise_architecture/06_decision_architecture/` | 决策轨迹图（模型/数据/人类接管/紧急 + L2a/L3） |
| 治理报告 | `docs/02_enterprise_architecture/03_governance_reports/` | 容量报告、约束违反、设计 vs 运营态、能力热图 |
| 全景注册表 | `docs/02_enterprise_architecture/00_overview_entry/` | 导航索引、全景注册表 |
| 全景对齐报告 | `docs/02_enterprise_architecture/generated/panorama_alignment_report.md` | depgraph/dataflow/decision/blueprint 五图对齐检测 |

---

## 治理铁律速查

| 铁律 | 要点 |
|------|------|
| SSoT 真源分类 | 规则数据→YAML（sync 到 DB）；架构数据→PostgreSQL DB（apply_*.py 直接写） |
| 依赖关系先行 | 施工前 MUST 先 `apply_depgraph.py --add-design-node` 登记依赖 |
| 任务系统 SSoT | 查询任务状态 MUST 通过 TaskRepository，禁止直接读 tasks/*.md |
| LLM 安全 | 所有 LLM 调用必经 LSGSecurityGateway，禁止裸调 |
| PIT 铁律 | 回测零前瞻偏差 + 三平面一致性 + Embargo 期 |
| Git 提交 | 所有 commit 通过 GitCommitGateway（`scripts/git_commit.py`）；裸 git commit 被硬阻断 |
| 能力反查 | 写 src/zephyr 业务代码前 MUST 调用能力反查（MCP 或 Python API） |
| 数据操作 | 破坏性 DB 操作前 MUST 三步验证（必要性+真实性+可逆性） |

> 完整铁律与裁定见 [AGENTS.md](../../../AGENTS.md)。

---

## 文档维护机制

本文件夹采用**半自动维护**（详见 [_automation/README.md](_automation/README.md)）：

- **手工区**（叙述/解读）：人工维护，稳定不常变
- **自动区**（统计/清单）：由 `generate_code_wiki_stats.py` 用 `<!-- AUTO-START/END -->` 标记块全自动刷新，触发方式 `event_driven`（depgraph 刷新钩子）
- **外链区**：深度明细外链到 `docs/02/{00,01,02,05,06}/` 权威 auto-gen 源，不复制

真源以代码与 `AGENTS.md` 为准，架构数据以 depgraph DB 为准。
