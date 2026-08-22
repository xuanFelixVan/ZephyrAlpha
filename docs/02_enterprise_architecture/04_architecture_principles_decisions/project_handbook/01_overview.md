---
ttl: permanent
doc_type: architecture_view
title: 项目总览与运行方式 / Project Overview
owner: ZephyrAlpha-Owner
language: zh
---

# 01 · 项目总览与运行方式

> 大白话项目现状。本文档=手工叙述（稳定）+ 自动区（统计/清单）+ 外链（深度明细）。
> 单一入口与全局导航见 [../README.md](../README.md)。

## 1. 项目定位与终极目标

ZephyrAlpha 是一个 **AI 原生（AI-native）的量化研究与交易平台**（v2.0.0），核心理念是用 AI 治理框架编排量化研究的全生命周期。项目以"接入所有模块、零孤儿率"为终极目标，由 **AutoRuntime Core（系统大脑）** 负责三层 AI 运行时编排、节律调度、健康监控与工作编排。

设计为五层同心圆：L0 引导 → L1 协调 → L2 执行 → L3 知识 → L4 编排。三层 AI 工作分配：L1 Trae（人在 IDE，免费）→ L2 Local（24/7 Ollama，零成本）→ L3 API（夜班/高价值，付费 DeepSeek/Claude）。

## 2. 整体分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoRuntime Core (系统大脑)                │
│  L0 Bootstrap → L1 Reconcile → L2 Execute → L3 Knowledge → L4 Orchestrate
└─────────────────────┬───────────────────────────────────────┘
                      │
   ┌──────────────────┼──────────────────┐
   ▼                  ▼                  ▼
┌────────┐      ┌──────────┐       ┌──────────┐
│治理域   │      │ 数据集成域│       │ 量化交易域│
│Governance│     │  Data    │       │ Backtest/ │
└────┬────┘      └────┬─────┘       └────┬─────┘
     └────────────────┼──────────────────┘
                      ▼
           ┌─────────────────────┐
           │ 共享与基础设施层      │
           │ shared / infra /     │
           │ integration / security│
           └─────────────────────┘
```

层级依赖方向（向下依赖原则）：`shared`（最底层）← `infrastructure` ← `data/integration/security/governance/backtest/factor/risk` ← `trading`（顶层，组合所有子组件）。`shared` 禁止 import `integration.*`。

## 3. 目录结构

*自动化同步（目录树）+ 手工维护（注释）| 数据源：文件系统扫描 src/zephyr/、scripts/governance/*

<!-- AUTO-START:directory_tree -->
<!-- 自动生成：由 generate_code_wiki_stats.py 扫描 src/zephyr/ 一级目录 + scripts/governance/ 维度目录填充，请勿手工编辑 -->
<!-- AUTO-END:directory_tree -->

> 完整全项目树（en/zh，含每个文件）见权威源 `docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_zh.md`（由 `generate_path_tree.py` 产出）。

## 4. 项目运行方式

### 4.1 安装

```bash
cd D:\ZephyrAlpha
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
# 可选：pip install -e ".[demo]"（Akshare 演示）
```

### 4.2 CLI 命令

安装后提供两个控制台命令（`pyproject.toml` `[project.scripts]`）：

| 命令 | 模块 | 用途 |
|------|------|------|
| `zephyr` | `zephyr.trading.__main__:main` | AutoRuntime Core 主入口 |
| `integrator` | `zephyr.data.cli:main` | 数据源集成器 CLI |

`zephyr [--once] [--no-demo] [--no-dream] [--interval N]`：
- `--once`：运行一次 reconcile 后退出
- `--interval`：reconcile 间隔秒数（默认 5.0）

`integrator` 8 子命令：`status [task_id]` / `list [--source]` / `run <task_id>` / `rerun-failed` / `pause <source>` / `resume <source>` / `start` / `speed-test`。

其他模块入口：`python -m zephyr.gov_drift`（漂移检测）、`python -m zephyr.autonomy_core`（技能注册表）、`python -m zephyr.data.scheduler`（数据调度守护）、`python -m zephyr.infrastructure.auto_fix_engine`（自动修复）。

### 4.3 Docker 全栈

```bash
docker-compose up   # zephyr-core:8000 / prometheus:9090 / grafana:3000 / node-exporter:9100
```

### 4.4 数据调度器（Windows）

```powershell
powershell -File scripts\start_scheduler.ps1          # 手动启动（自动重启循环）
# 注册为 Windows 计划任务（AtStartup，SYSTEM）：管理员运行 scripts\register_scheduler_task.ps1
# 管理：schtasks /run|/end|/query /tn ZephyrAlpha_DataScheduler
```

### 4.5 MCP 服务器集群

```bash
python scripts\mcp\launcher.py            # 启动 12 个 MCP 服务器（DAG 拓扑序）
python scripts\mcp\launcher.py --dry-run  # 仅打印启动计划
```

> MCP 集群也会在 AutoRuntime Core 启动时由 `boot_hooks.py` 在守护线程自动启动。

### 4.6 仪表盘（Panel）

```bash
panel serve src/zephyr/frontend/dashboard/app_panel.py --show --port 5006
# 浏览器访问：http://localhost:5006
```

10 个 Tab（5 治理 + 5 交易/回测）。

### 4.7 测试

```bash
pytest                           # 全量
pytest -m "not slow"             # 跳过慢测试
pytest --cov=zephyr --cov-report=term-missing   # 覆盖率（阈值 70%）
```

## 5. 依赖统计

<!-- AUTO-START:dependency_stats -->
<!-- 数据源：depgraph (PostgreSQL) | 最后同步：2026-08-17 -->

| 指标 | 值 |
|------|----|
| 域总数 / Total domains | 73 |
| 节点总数 / Total nodes | 6869 |
| 依赖边总数 / Total edges | 14474 |
| 孤儿节点数 / Orphan nodes | 0 |

| build_status | 节点数 |
|--------------|--------|
| `deprecated` | 94 |
| `generated` | 4619 |
| `planned` | 85 |
| `stable` | 2071 |
<!-- AUTO-END:dependency_stats -->

<!-- AUTO-START:external_deps -->
| 依赖 | 用途 |
|------|------|
| `pydantic>=2.0.0,<3.0.0` | 数据验证 / Data validation |
| `pyyaml>=6.0,<7.0` | YAML 配置解析 / YAML config parsing |
| `pandas>=2.0.0,<3.0.0` | 数据处理 / Data processing |
| `psutil>=5.9.0,<7.0` | 系统监控 / System monitoring |
| `chromadb>=0.4.24,<1.0.0` | 向量数据库（知识库）/ Vector DB (KB) |
| `mcp>=1.0.0,<2.0.0` | MCP 协议 / MCP protocol |
| `openai>=1.0.0,<2.0.0` | LLM 客户端 / LLM client |
| `sentence-transformers>=3.0.0,<4.0.0` | 句向量模型 / Sentence embeddings |
| `structlog>=24.1.0,<25.0.0` | 结构化日志 / Structured logging |
| `pyarrow>=15.0.0,<26.0.0` | Parquet I/O / Parquet I/O |
| `psycopg2-binary>=2.9.0,<3.0.0` | PostgreSQL 驱动 / PostgreSQL driver |
| `clickhouse-driver>=0.2.6,<1.0.0` | — / — |
| `redis>=5.0.0,<6.0.0` | — / — |
| `plotly>=6.0.0,<7.0.0` | 可视化 / Visualization |
| `streamlit>=1.50.0,<2.0.0` | 早期仪表盘 / Legacy dashboard |
| `panel>=1.5.0,<2.0.0` | 仪表盘 / Dashboard |
| `holoviews>=1.19.0,<2.0.0` | 可视化层 / Viz layer |
| `datashader>=0.16.0,<1.0.0` | 大数据渲染 / Large data rendering |
| `hvplot>=0.10.0,<1.0.0` | Pandas 绘图 / Pandas plotting |
| `plotly_resampler>=0.9.0,<1.0.0` | 时序降采样 / Timeseries downsampling |
| `python-dotenv>=1.0.0,<2.0.0` | 环境变量 / Env vars |
| `tzdata>=2024.1` | — / — |
| `apscheduler>=3.10.0,<4.0.0` | 任务调度 / Task scheduling |
| `sqlalchemy>=2.0.0,<3.0.0` | ORM/JobStore / ORM/JobStore |
| `exchange_calendars>=4.13,<5.0` | 交易日历 / Trading calendars |
<!-- AUTO-END:external_deps -->

> 依赖关系详解与关键链路图见 [07_dependencies.md](07_dependencies.md)。
