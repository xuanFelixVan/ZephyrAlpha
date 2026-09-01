---
ttl: permanent
doc_type: architecture_view
title: 仓库布局与模块清单 / Repository Layout
owner: ZephyrAlpha-Owner
language: zh
---

# 02 · 仓库布局与模块清单

> 大白话项目现状。仓库布局 + 模块清单 + AUTO 计数 + 外链全量明细。

## 1. 仓库顶层结构

```
ZephyrAlpha/
├── src/zephyr/           # 核心源码（唯一 Python 包根）
├── scripts/              # 治理与工具脚本
├── config/               # 配置文件（平铺）
├── architecture_model/   # 架构模型 YAML SSoT（53 域+契约+事件）
├── docs/                 # 项目文档
├── tests/                # 测试代码（按功能域归类）
├── data/                  # 数据库与运行时数据
├── pyproject.toml         # 项目元数据与依赖
├── docker-compose.yml     # 容器编排
├── Dockerfile             # 容器构建
└── AGENTS.md              # AI 接入宪法
```

> 命名规范：全项目文件名统一 snake_case；所有域平级（无父子关系），新增域只需 INSERT 到 depgraph `domains` 表。

## 2. src/zephyr 包清单（按职能分层）

### 2.1 运行时大脑与编排层
- `trading/` — AutoRuntime Core 系统大脑（boot/reconcile/shutdown + 20+ 子组件编排）
- `orchestrator/` — Agent 编排（回滚/故障容错/生命周期/质量评估）
- `autonomy_core/` — 自治核心（技能注册/触发路由/上下文/阶段规划）

### 2.2 治理域（Governance）
- `governance/` — 治理桥接层（八件套契约 G-CT-001~008 + TaskRepository + StrategyBase）
- `gov_audit/` — 不可篡改审计追踪（加密溯源 + Agent 签名）
- `gov_drift/` — 漂移检测（39 强制检测器 + 自动调和闭环）
- `gov_enforcement/` — 规则执行（rule_bridge / ~80 commit_gates / GitCommitGateway / session_worktree）
- `gov_code_quality/` — 代码质量（去重/门禁/AST）
- `gov_rule/` — 规则宪法（constitutional_update）

### 2.3 基础设施与共享层
- `shared/` — 跨层基础（types/errors/constants/IO/event_bus/contracts/observability；`REPO_ROOT` 是被最广泛 import 的符号）
- `infrastructure/` — 基础设施（cost_tracker/event_store/sla_monitor）

### 2.4 安全域
- `security/` — LLM 防御 L0-L8 九层纵深栈（`LSGSecurityGateway` 编排，所有 LLM 调用必经）

### 2.5 集成层
- `integration/` — 外部集成边界（MCP 服务器 12 个 + LLM 桥 + 端口协议）

### 2.6 数据域
- `data/` — 数据源集成器（CLI + APScheduler 调度 + ch_writer）
- `market_data/` — 行情数据契约

### 2.7 量化交易域（端到端：信号→因子→回测→组合→执行→风控→报告）
- `factor/` — 因子框架（FactorBase 抽象 + FactorRegistry 装饰器自注册）
- `signal_fundamental/` — 信号合成管线（AlphaSignalPipeline 5 阶段）
- `signal_quality/` / `signal_ashare/` — 信号质量 / A 股信号
- `risk/` — 风险管理（止损/限仓/熔断）
- `pf_core/` / `pf_alloc/` — 组合核心 / 配置
- `position/` — 持仓
- `ex_core/` — 执行核心（订单/SOR）
- `ex_sor/` / `execution_simulation/` — 智能路由 / 执行仿真（规划态）
- `backtest/` — 回测引擎（PIT/WFA/DecisionGate 3 阶段门控）
- `reporting/` — 盘后分析报告
- `intelligence/` — 模型评估/智能
- `ml_train/` / `ml_serve/` — ML 训练 / 服务
- `simulation/` — 模拟管线
- `digital_twin/` / `cross_asset/` / `alt_data/` / `research/` — 规划态/空壳域
- `frontend/dashboard/` — Panel 仪表盘
- `feedback_loop/` — 反馈环引擎（跨层）
- `compliance/` — 合规（桩）

## 3. 模块计数

<!-- AUTO-START:module_counts -->
<!-- 数据源：module_id_registry.yaml + 文件系统扫描 | 最后同步：2026-08-17 -->

| 指标 | 值 |
|------|----|
| module_id 注册数 / Registered module_ids | 74 |
| src/zephyr 一级子包 / Top-level packages | 53 |
| scripts/governance .py 总数 / Governance scripts | 483 |
<!-- AUTO-END:module_counts -->

<!-- AUTO-START:py_file_total -->
<!-- 数据源：文件系统扫描 | 最后同步：2026-08-17 -->

| 目录 | .py 文件数（排除 __init__.py） |
|------|------|
| `src/zephyr/` | 2974 |
| `scripts/governance/` | 483 |
| `tests/` | 3235 |
| **合计 / Total** | **6692** |
<!-- AUTO-END:py_file_total -->

## 4. 外部权威源（全量明细）

| 权威源 | 内容 | 路径 |
|--------|------|------|
| 全项目树 | 每个文件逐项（en/zh） | `docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_zh.md` |
| 域架构文档 | 逐域职责/类/函数详解 | `docs/02_enterprise_architecture/02_domain_architecture_docs/` |
| 疑似异常模块 | 孤儿/重复职责/命名异常清单 | 见域文档生成器 `generate_domain_doc.py` 输出 |

> 治理基础设施（governance/gov_*）详解见 [06_governance_and_infra.md](06_governance_and_infra.md)；交易域详解见 [05_trading_domains.md](05_trading_domains.md)。
