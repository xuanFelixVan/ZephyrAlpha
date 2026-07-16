# ZephyrAlpha Code Wiki

> 版本: 2.0.0 | 生成日期: 2026-07-13
> 本文档为 ZephyrAlpha 项目的结构化代码百科，涵盖整体架构、模块职责、关键类与函数、依赖关系及运行方式。

---

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 整体架构](#2-整体架构)
- [3. 目录结构](#3-目录结构)
- [4. 核心模块职责](#4-核心模块职责)
  - [4.1 AutoRuntime Core（系统大脑）](#41-autoruntime-core系统大脑)
  - [4.2 治理域（Governance）](#42-治理域governance)
  - [4.3 数据集成域（Data）](#43-数据集成域data)
  - [4.4 量化交易域](#44-量化交易域)
  - [4.5 共享与基础设施层](#45-共享与基础设施层)
  - [4.6 集成与安全层](#46-集成与安全层)
- [5. 关键类与函数说明](#5-关键类与函数说明)
- [6. 依赖关系](#6-依赖关系)
- [7. 项目运行方式](#7-项目运行方式)
- [8. 技术栈与配置](#8-技术栈与配置)

---

## 1. 项目概述

ZephyrAlpha 是一个 **AI 原生（AI-native）的量化研究与交易平台**（v2.0.0），核心理念是用 AI 治理框架编排量化研究的全生命周期。项目以"接入所有模块、零孤儿率"为终极目标，由 **AutoRuntime Core（系统大脑）** 负责三层 AI 运行时编排、节律调度、健康监控与工作编排。

**核心特征：**

- **AI 治理优先**：所有 AI 行为必须审计、所有组件必须注册 CapabilityCard、所有 LLM 调用必经安全网关。
- **SSoT（单一真源）铁律**：规则数据真源为 YAML 文件，架构数据真源为 PostgreSQL DB，禁止多真源同步。
- **三层 AI 工作分配**：L1 Trae（人在环，免费）→ L2 Local（24/7 本地推理，零成本）→ L3 API（夜班/高价值，付费）。
- **PIT（Point-In-Time）铁律**：回测引擎零前瞻偏差，三平面一致性 + Embargo 期。
- **depgraph 依赖图**：依赖关系唯一真源，AI 查询 depgraph = 零幻觉空间。

---

## 2. 整体架构

ZephyrAlpha 采用 **五层同心圆** 架构，灵感来自 Microsoft Magentic-One + Kubernetes Controller Manager + Google A2A。

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
│Governance│     │  Data    │       │ Backtest/│
│         │      │          │       │ Factor/  │
│ audit/  │      │ scheduler│       │ Risk/    │
│ drift/  │      │ provider │       │ Exec/    │
│ kb/     │      │ ch_writer│       │ Portfolio│
│ rule/   │      │          │       │          │
└────┬────┘      └────┬─────┘       └────┬─────┘
     │                │                  │
     └────────────────┼──────────────────┘
                      ▼
           ┌─────────────────────┐
           │ 共享与基础设施层      │
           │ shared / infra /     │
           │ integration / security│
           └─────────────────────┘
```

### 架构分层（LPC 双轨制）

项目域按 `layer_id` 属性分为 4 个层级（真源：`depgraph_schema.py` DB trigger）：

| 层级 | 含义 | 代表域 |
|------|------|--------|
| `L0_infrastructure` | 基础设施层 | D_INFRA_RUNTIME / D_INFRA_RECOVERY |
| `L1_foundation` | 基础层 | D_SHARED / D_GOVERNANCE |
| `L2_domain` | 领域层 | D_BACKTEST / D_FACTOR / D_RISK / D_DATA |
| `L3_application` | 应用层 | D_TRADING / D_ORCHESTRATOR |

### 三态状态机（depgraph 节点生命周期）

| 值 | 含义 | 代码状态 | 写入方式 |
|------|------|---------|---------|
| `design` | 设计态 | 蓝图阶段，代码未写 | `apply_depgraph.py --add-design-node` |
| `prototype` | 原型态 | 代码已写，验证中 | 生成器自动产出 |
| `production` | 运营态 | 已上线稳定运行 | 生成器自动产出 |

状态升级单调推进：`design → prototype → production`（禁止倒退）。

---

## 3. 目录结构

```
ZephyrAlpha/
├── src/zephyr/                  # 核心源码（唯一 Python 包根）
│   ├── trading/                 # AutoRuntime Core（系统大脑）
│   ├── governance/              # 核心治理桥接层（8件套契约）
│   ├── gov_audit/               # 治理审计（审计追踪/法证审计）
│   ├── gov_drift/               # 漂移检测（概念/配置/回归漂移）
│   ├── gov_kb/                  # 知识库治理（5门禁管线）
│   ├── gov_enforcement/         # 规则执行（门禁/CBAC/合规）
│   ├── gov_code_quality/        # 代码质量（去重/门禁/AST）
│   ├── data/                    # 数据源集成器（CLI+调度）
│   ├── backtest/                # 回测引擎（PIT/WFA/决策门控）
│   ├── factor/                  # 因子框架（抽象+注册表+示例）
│   ├── signal_fundamental/      # 信号合成管线
│   ├── signal_quality/          # 信号质量评估
│   ├── risk/                    # 风险管理（止损/限仓/熔断）
│   ├── ex_core/                 # 执行核心（订单/SOR）
│   ├── pf_core/                 # 组合核心（策略基类/注册表）
│   ├── market_data/             # 行情数据契约
│   ├── shared/                  # 共享层（types/errors/io/event_bus）
│   ├── infrastructure/          # 基础设施（cost/event_store/sla）
│   ├── integration/             # 集成层（MCP/LLM桥/端口协议）
│   ├── security/                # 安全层（LLM防御 L0-L8）
│   ├── autonomy_core/           # 自治核心（技能/触发路由）
│   ├── frontend/dashboard/      # Panel 仪表盘
│   └── orchestrator/            # Agent 编排
├── scripts/                     # 治理与工具脚本
│   ├── governance/              # 12 维度审计扫描器（317 脚本）
│   ├── mcp/                     # MCP 服务器集群管理
│   └── arch_guard/              # 架构守卫
├── config/                      # 配置文件（平铺）
├── docs/                        # 项目文档
├── tests/                       # 测试代码（按功能域归类）
├── architecture_model/          # 架构模型 YAML SSoT（53域+契约+事件）
├── pyproject.toml               # 项目元数据与依赖
├── docker-compose.yml           # 容器编排
├── Dockerfile                   # 容器构建
└── AGENTS.md                    # AI 接入宪法
```

> **命名规范**：全项目文件名统一 snake_case；所有域平级（无父子关系），新增域只需 INSERT 到 domains 表。

---

## 4. 核心模块职责

### 4.1 AutoRuntime Core（系统大脑）

**位置**：[src/zephyr/trading/](file:///d:/ZephyrAlpha/src/zephyr/trading/) | **蓝图**：MOD-INF-035 | **层级**：infrastructure

AutoRuntime Core 是项目的"系统大脑"，负责三层 AI 运行时编排、节律调度、健康监控、审计日志与工作编排。其设计为五层同心圆：L0 引导 → L1 协调 → L2 执行 → L3 知识 → L4 编排。

#### 核心类

| 类 | 文件 | 职责 |
|----|------|------|
| `AutoRuntimeCore` | [auto_runtime_core.py](file:///d:/ZephyrAlpha/src/zephyr/trading/auto_runtime_core.py) | 三层运行时运营中心，组合 20+ 子组件 |
| `Conductor` | [conductor.py](file:///d:/ZephyrAlpha/src/zephyr/trading/conductor.py) | 全自动指挥官，任务认领+冲突检测+并行分组 |
| `AutoPilot` | [autopilot.py](file:///d:/ZephyrAlpha/src/zephyr/trading/autopilot.py) | 自动驾驶，扫描+原子认领待处理任务 |
| `WorkOrchestrator` | [work_orchestrator.py](file:///d:/ZephyrAlpha/src/zephyr/trading/work_orchestrator.py) | 工作编排子系统，决定 what/when/which model/order |
| `CapabilityRegistry` | [capability_registry.py](file:///d:/ZephyrAlpha/src/zephyr/trading/capability_registry.py) | 能力注册表，解决"AI 不知道功能存在"问题 |
| `LifecycleManager` | [lifecycle_manager.py](file:///d:/ZephyrAlpha/src/zephyr/trading/lifecycle_manager.py) | 子组件生命周期管理（boot/shutdown 序列） |

#### 启动流程

```
python -m zephyr.trading
  → main() 构建 RuntimeConfig + AutoRuntimeCore
  → core.boot()
      → LifecycleManager.boot_sequence() 启动 20+ 子组件
      → _start_local_models() (可选 L2 本地模型)
      → _bootstrap_rbac() (Agent RBAC)
      → register_boot_hooks() (注册 15+ 事件钩子)
      → _start_task_queue() (任务队列+PipelineOrchestrator)
      → _run_boot_triple_alignment() (启动三对齐)
      → _init_escalation_protocol() (升级协议)
  → poll loop: core.reconcile() (MAPE-K 循环)
  → SIGINT/SIGTERM → core.shutdown()
```

`register_boot_hooks()`（[boot_hooks.py](file:///d:/ZephyrAlpha/src/zephyr/trading/boot_hooks.py)）幂等注册以下钩子：

- **任务系统钩子**：`auto_unblock_dependents`(p50)、`auto_retry_on_failure`(p60)、`triple_alignment_on_verified`(p70)、`cleanup_task_processes`(p45)、`orc_vms_archive`(p48)、`kb_vms_sync`(p47)、`rbk_gate_freeze`(p55)
- **事件驱动钩子**：`escalation_check_event`、`timeout_check_event`、`budget_delta_event`、`session_startup_init_budget`、`session_shutdown_budget_close`、`triple_align_event`
- **守护子系统**：IdeHealthDaemon、RollbackBootIntegration(WAL)、SLAMonitor、Notifier、HealthAggregator、RedBlueTriggerConsumer、MCP 集群（10 服务器 DAG 拓扑启动）

#### 三层 AI 工作分配

| 层 | 名称 | 用途 | 成本 | 模型 |
|----|------|------|------|------|
| L1 | Trae | 人在 IDE 交互 | 免费 | Trae IDE |
| L2 | Local | 24/7 自动化 | 零成本 | Ollama（BGE-M3 + qwen3:8b） |
| L3 | API | 夜班/高价值/不确定 | 付费 | DeepSeek V4 Pro / Claude |

`WorkOrchestrator.resolve_layer()` 决定任务运行层级；`acquire_slot()`/`release_slot()` 执行每层并行度控制。

---

### 4.2 治理域（Governance）

治理域采用"桥接层 + 引擎包"的分层结构：`governance/` 定义跨模块契约，`gov_*` 引擎包实现具体能力。

#### 4.2.1 核心治理桥接层

**位置**：[src/zephyr/governance/](file:///d:/ZephyrAlpha/src/zephyr/governance/) | **蓝图**：DOM-GOV-001

定义"Agent 治理八件套"（agent_rbac / agent_spec / audit_trail / rollback / escalation / drift_detector / budget_enforcer / a2a）及 8 个集成契约（G-CT-001~008）。

| 模块 | 文件 | 职责 |
|------|------|------|
| `CapabilityLookup` | [capability_lookup.py](file:///d:/ZephyrAlpha/src/zephyr/governance/capability_lookup.py) | 能力→真源文件反查引擎（消费者 76+） |
| `DepgraphSchema` | [depgraph_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) | depgraph PostgreSQL DDL + 版本迁移（11 表，v6~v16） |
| `IntegrityGuard` | [integrity.py](file:///d:/ZephyrAlpha/src/zephyr/governance/integrity.py) | 审计组件健康检查守卫（Safety H） |
| `MerkleAggregator` | [integrity.py](file:///d:/ZephyrAlpha/src/zephyr/governance/integrity.py) | Merkle 小时聚合（消费者 71+） |

#### 4.2.2 治理审计（gov_audit）

**位置**：[src/zephyr/gov_audit/](file:///d:/ZephyrAlpha/src/zephyr/gov_audit/) | **蓝图**：MOD-INF-020 | **域**：D_GOV_AUDIT

不可篡改审计追踪，带加密溯源与 Agent 签名。62 文件物理平铺但逻辑聚类（ARCH-042：10 前缀簇）。

| 类 | 文件 | 职责 |
|----|------|------|
| `AuditIndexer` | [indexer.py](file:///d:/ZephyrAlpha/src/zephyr/gov_audit/indexer.py) | 增量非破坏性索引构建（按维度/严重度/类型） |
| `AuditReportWriter` | [writer.py](file:///d:/ZephyrAlpha/src/zephyr/gov_audit/writer.py) | 原子报告写入（temp+fsync+replace，防崩溃损坏） |
| `AuditQueryEngine` | [query.py](file:///d:/ZephyrAlpha/src/zephyr/gov_audit/query.py) | 只读查询引擎（失败返回空，不抛异常） |
| `AuditType`/`Severity`/`Priority` | [models.py](file:///d:/ZephyrAlpha/src/zephyr/gov_audit/models.py) | Pydantic 数据模型与枚举（不可变分类） |

#### 4.2.3 漂移检测（gov_drift）

**位置**：[src/zephyr/gov_drift/](file:///d:/ZephyrAlpha/src/zephyr/gov_drift/) | **蓝图**：MOD-INF-023 | **域**：D_GOV_DRIFT

Git 原生运行时漂移检测，39 个强制检测器（全部必须执行）+ 自动调和闭环。

| 类 | 文件 | 职责 |
|----|------|------|
| `DriftDetector` | [drift_detector.py](file:///d:/ZephyrAlpha/src/zephyr/gov_drift/drift_detector.py) | 兼容别名，同步漂移检测（欧氏距离+事件发射） |
| `DriftEngine` | [drift_engine.py](file:///d:/ZephyrAlpha/src/zephyr/gov_drift/drift_engine.py) | 编排核心：检测器发现→调度→聚合→反馈（Safety H） |
| `Reconciler` | [reconciler.py](file:///d:/ZephyrAlpha/src/zephyr/gov_drift/reconciler.py) | 自动调和：快照→修复→验证→回滚闭环 |
| `DriftStateMachine` | [state_machine.py](file:///d:/ZephyrAlpha/src/zephyr/gov_drift/state_machine.py) | 漂移事件状态机 |

#### 4.2.4 知识库治理（gov_kb）

**位置**：[src/zephyr/gov_kb/](file:///d:/ZephyrAlpha/src/zephyr/gov_kb/) | **蓝图**：MOD-KB-001 | **域**：D_GOV_KB

5 门禁（G1~G5）知识管线 + 冷启动 Bootstrap。

| 类 | 文件 | 职责 |
|----|------|------|
| `IngestGate` | [ingest.py](file:///d:/ZephyrAlpha/src/zephyr/gov_kb/ingest.py) | G1 入库门禁（格式/frontmatter/去重/注入防护） |
| `KnowledgeEngine` | [knowledge_engine.py](file:///d:/ZephyrAlpha/src/zephyr/gov_kb/knowledge_engine.py) | 知识条目存储+倒排索引搜索 |
| `Bootstrap` | [bootstrap.py](file:///d:/ZephyrAlpha/src/zephyr/gov_kb/bootstrap.py) | 冷启动引擎（扫描文档→分段→脱敏→G1~G5 注入） |

#### 4.2.5 治理脚本系统

**位置**：[scripts/governance/](file:///d:/ZephyrAlpha/scripts/governance/) | **蓝图**：MOD-INF-005

12 维度审计扫描器套件（317 脚本），入口 `run_all.py`，~60 秒全量扫描。

| 维度 | 职责 | 脚本数 |
|------|------|--------|
| D1 结构 | 目录结构验证 | 22 |
| D2 链接 | 断链检测 | 3 |
| D3 元数据 | frontmatter 校验 | 23 |
| D4 路径 | 路径守卫 | 4 |
| D5 架构 | 架构合规（最大） | 72 |
| D6 安全 | 安全扫描 | 13 |
| D7 代码质量 | 去重/AST | 21 |
| D8 文档同步 | 文档一致性 | 4 |
| D9 知识 | 知识库 | 2 |
| D11 合规 | 合规检查 | 12 |
| D12 AI 幻觉 | 幻觉检测 | 4 |

退出码：0=通过 / 1=警告 / 2=阻断 / 3=崩溃。

---

### 4.3 数据集成域（Data）

**位置**：[src/zephyr/data/](file:///d:/ZephyrAlpha/src/zephyr/data/) | **蓝图**：MOD-L00-004 | **CLI**：`integrator`

统一管理多数据源（iFind / miniQMT / AKShare）的自动下载、调度与 ClickHouse 持久化。

| 类 | 文件 | 职责 |
|----|------|------|
| `DataSourceBase` | [provider_base.py](file:///d:/ZephyrAlpha/src/zephyr/data/provider_base.py) | Provider 抽象基类（connect/health_check/fetch/disconnect） |
| `IntegratorScheduler` | [scheduler.py](file:///d:/ZephyrAlpha/src/zephyr/data/scheduler.py) | APScheduler 编排器（5 cron 时段 + DAG 依赖 + 断点续传） |
| `ClickHouseWriter` | [ch_writer.py](file:///d:/ZephyrAlpha/src/zephyr/data/ch_writer.py) | ClickHouse 写入（TCP:9000 查询 + HTTP:8123 写入 + 本地落盘回退） |
| `Alerter` | [alerter.py](file:///d:/ZephyrAlpha/src/zephyr/data/alerter.py) | 失败告警 |
| `ProgressStore` | [progress_store.py](file:///d:/ZephyrAlpha/src/zephyr/data/progress_store.py) | 断点续传存储 |

**数据流**：`CLI → get_integrator() → IntegratorScheduler → DataSourceBase providers → ch_writer.write_result() → ClickHouse`

**配置**：[config/tasks.yaml](file:///d:/ZephyrAlpha/src/zephyr/data/config/tasks.yaml) 定义 10 个任务（3 个 provider × 2 调度时段），每个任务声明 `task_id/table/source/schedule/incremental/dependencies/capability`。

---

### 4.4 量化交易域

量化交易域遵循端到端数据流：

```
D_MKT_DATA (NormalizedMarketData, CTR-001)
    │
    ▼
D_FACTOR (FactorBase.compute → FactorSignal, CTR-002)
    │  [FactorRegistry 自动发现; AlphaSignalPipeline 驱动 5 阶段]
    ▼
D_SIGNAL (AlphaSignalPipeline: 合成 → 验证 → 分配; D_SIGQC 监控降级)
    │
    ▼
D_RISK (RiskLimitsCalculator → RiskLimits CTR-003; RiskValidator 预交易; 止损/熔断)
    │
    ▼
D_PORTFOLIO_CORE (StrategyBase.generate_target_weights, 受 RiskLimits 约束)
    │  [StrategyRegistry 自动发现; 产出目标权重]
    ▼
D_EX_CORE (ExecutionEngine.execute_order → OrderManager → Broker; 产出 Fill CTR-005)
    │
    ▼
D_BACKTEST (镜像实盘路径 via MatchingEngine+Portfolio+metrics, DecisionGate 门控 IS→WFA→OOS)
```

#### 4.4.1 回测引擎（backtest）

**位置**：[src/zephyr/backtest/](file:///d:/ZephyrAlpha/src/zephyr/backtest/) | **蓝图**：MOD-BT-001 | **域**：D_BACKTEST

| 类 | 文件 | 职责 |
|----|------|------|
| `BacktestEngineBase` | [core/engine_base.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/engine_base.py) | 回测引擎抽象基类（OCP 扩展点） |
| `MatchingEngine` | [core/matching_engine.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/matching_engine.py) | 撮合引擎（委托纯函数 MatchingLogic，保证回测=实盘；A 股 T+1/涨跌停/停牌/100 股） |
| `DecisionGate` | [core/decision_gate.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/decision_gate.py) | 3 阶段门控 IS→WFA→OOS（不可跳过；IS Sharpe>0.5 准入；OOS Sharpe≥70% IS） |
| `PITManager` | [core/pit_manager.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/pit_manager.py) | PIT 铁律（AS-OF JOIN + Embargo 期，零前瞻） |
| `WalkForward` | [core/walk_forward.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/walk_forward.py) | Walk-Forward 分析（滚动/锚定/扩展 + White's Reality Check） |
| `Portfolio` | [core/portfolio.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/portfolio.py) | 组合（T+1 锁 + NAV 曲线） |
| `calculate_metrics()` | [core/metrics.py](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/metrics.py) | 指标计算（中国 10 年国债 2.5% 无风险；样本<60 不算 Sharpe；DSR 修正） |

#### 4.4.2 因子框架（factor）

**位置**：[src/zephyr/factor/](file:///d:/ZephyrAlpha/src/zephyr/factor/) | **蓝图**：MOD-L02-001 | **域**：D_FACTOR

| 类 | 文件 | 职责 |
|----|------|------|
| `FactorBase` | [factor_base.py](file:///d:/ZephyrAlpha/src/zephyr/factor/factor_base.py) | 因子抽象基类（OCP 扩展点；`compute(data)->Series`） |
| `FactorMeta` | [factor_base.py](file:///d:/ZephyrAlpha/src/zephyr/factor/factor_base.py) | 因子元数据（factor_id/name/domain/version/dependencies） |
| `FactorRegistry` | [factor_base.py](file:///d:/ZephyrAlpha/src/zephyr/factor/factor_base.py) | 因子注册表单例（装饰器自注册） |
| `ValueFactor` | [value_factor.py](file:///d:/ZephyrAlpha/src/zephyr/factor/value_factor.py) | 示例价值因子（PE 倒数） |
| `Momentum20d` | [momentum_factor.py](file:///d:/ZephyrAlpha/src/zephyr/factor/momentum_factor.py) | 示例动量因子（20 日收益率） |

#### 4.4.3 信号管线（signal_fundamental）

**位置**：[src/zephyr/signal_fundamental/pipeline.py](file:///d:/ZephyrAlpha/src/zephyr/signal_fundamental/pipeline.py) | **域**：D_SIGLEGACY

`AlphaSignalPipeline` 驱动 5 阶段：`FACTOR_DISCOVERY → FACTOR_COMPUTE → SIGNAL_SYNTHESIS → SIGNAL_VALIDATION → CAPITAL_ALLOCATION`。内置安全防护（因子名黑名单、置信度上限、builtins 完整性快照）。

#### 4.4.4 风险管理（risk）

**位置**：[src/zephyr/risk/](file:///d:/ZephyrAlpha/src/zephyr/risk/) | **蓝图**：MOD-L04-001 | **域**：D_RISK

| 类 | 文件 | 职责 |
|----|------|------|
| `RiskManagerBase` | [risk_manager.py](file:///d:/ZephyrAlpha/src/zephyr/risk/risk_manager.py) | 顶级风险编排（预+后+熔断） |
| `RiskLimitsCalculator` | [risk_limits.py](file:///d:/ZephyrAlpha/src/zephyr/risk/risk_limits.py) | 限仓计算（L1 硬限/L2 软限/L3 熔断） |
| `RiskValidator` | [risk_validator.py](file:///d:/ZephyrAlpha/src/zephyr/risk/risk_validator.py) | 预交易+组合验证（HALT 抛异常，WARNING 仅日志） |
| `evaluate_stop_loss()` | [stop_loss.py](file:///d:/ZephyrAlpha/src/zephyr/risk/stop_loss.py) | 止损评估（fixed_pct/trailing/time_based/volatility） |

不变量：熔断延迟 <1ms（INV-001）、日亏硬限（INV-004）、所有调用携带 idempotency_key（INV-007）。

#### 4.4.5 执行核心（ex_core）

**位置**：[src/zephyr/ex_core/](file:///d:/ZephyrAlpha/src/zephyr/ex_core/) | **蓝图**：MOD-L06-001 | **域**：D_EX_CORE

| 类 | 文件 | 职责 |
|----|------|------|
| `ExecutionEngine` | [execution_engine.py](file:///d:/ZephyrAlpha/src/zephyr/ex_core/execution_engine.py) | 算法执行+SOR 编排（TWAP/VWAP/冰山） |
| `OrderManager` | [order_manager.py](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py) | 订单状态机生命周期（PENDING→SUBMITTED→FILLED） |
| `BrokerInterface` | [broker_interface.py](file:///d:/ZephyrAlpha/src/zephyr/trading/trading_contracts/broker_interface.py) | Broker 接口（OCP-003 扩展点，canonical 路径 ARCH-GOV-SHIM-001） |

#### 4.4.6 组合核心（pf_core）

**位置**：[src/zephyr/pf_core/](file:///d:/ZephyrAlpha/src/zephyr/pf_core/) | **蓝图**：MOD-L05-001 | **域**：D_PORTFOLIO_CORE

| 类 | 文件 | 职责 |
|----|------|------|
| `StrategyBase` | [governance/strategies/strategy_base.py](file:///d:/ZephyrAlpha/src/zephyr/governance/strategies/strategy_base.py) | 策略抽象基类（`generate_target_weights`，OCP-002 扩展点） |
| `StrategyRegistry` | [governance/strategies/strategy_base.py](file:///d:/ZephyrAlpha/src/zephyr/governance/strategies/strategy_base.py) | 策略注册表单例（装饰器自注册） |

---

### 4.5 共享与基础设施层

#### 4.5.1 共享层（shared）

**位置**：[src/zephyr/shared/](file:///d:/ZephyrAlpha/src/zephyr/shared/) | **蓝图**：MOD-SHR_shared

跨层基础能力：types / errors / constants / IO / event_bus / contracts / observability。

| 类/函数 | 文件 | 职责 |
|---------|------|------|
| `EventBus` / `DomainEvent` | [event_bus.py](file:///d:/ZephyrAlpha/src/zephyr/shared/event_bus.py) | 异步事件总线+背压控制（CAP-006=500 队列深度） |
| `ZephyrBaseError` + 11 子类 | [foundation/errors.py](file:///d:/ZephyrAlpha/src/zephyr/shared/foundation/errors.py) | 统一异常树根（ZA-XX-NNNN 错误码） |
| `REPO_ROOT` / `find_repo_root()` | [io/paths.py](file:///d:/ZephyrAlpha/src/zephyr/shared/io/paths.py) | 仓库根常量 SSoT（基于 .git marker 向上搜索） |
| `load_vocabulary_values()` | [io/yaml_utils.py](file:///d:/ZephyrAlpha/src/zephyr/shared/io/yaml_utils.py) | 词表合法值加载器（strict=True fail-fast） |
| `Task` / `TaskCard` / `DecompositionResult` | [foundation/models.py](file:///d:/ZephyrAlpha/src/zephyr/shared/foundation/models.py) | 任务系统核心数据模型（Pydantic v2） |
| NewType 别名 | [foundation/types.py](file:///d:/ZephyrAlpha/src/zephyr/shared/foundation/types.py) | TaskId/ModuleId/FilePath 等零开销语义标识 |

> **向下依赖原则**：`shared` 禁止 import `integration.*`。

#### 4.5.2 基础设施层（infrastructure）

**位置**：[src/zephyr/infrastructure/](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/) | **蓝图**：MOD-INFRA_RUNTIME

| 类 | 文件 | 职责 |
|----|------|------|
| `CostTracker` | [cost_tracker.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/cost_tracker.py) | AI Agent 执行成本追踪（token/API 调用/费用，日预算告警） |
| `EventStore` | [event_store.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/event_store.py) | 不可篡改审计日志（SQLite WAL + SHA256 checksum） |
| `SLAMonitor` | [sla/sla_monitor.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/sla/sla_monitor.py) | RTO/RPO 自动记录（事件驱动：pipeline_failed→rollback_completed） |

所有持久化通过 `shared.io.sqlite_factory` + `paths.DB_PATH`（governance.db）。

---

### 4.6 集成与安全层

#### 4.6.1 集成层（integration）

**位置**：[src/zephyr/integration/](file:///d:/ZephyrAlpha/src/zephyr/integration/) | **蓝图**：MOD-INT_integration

外部集成边界：MCP 服务器、LLM 桥、端口协议。

| 类/函数 | 文件 | 职责 |
|---------|------|------|
| `BaseMCPServer` | [mcp/_base_server.py](file:///d:/ZephyrAlpha/src/zephyr/integration/mcp/_base_server.py) | 自建 JSON-RPC 2.0 over stdio MCP 基类（MCP/0.3 spec） |
| `BlueprintSearchProtocol` 等 | [ports.py](file:///d:/ZephyrAlpha/src/zephyr/integration/ports.py) | `@runtime_checkable Protocol` 接口（解耦 pipeline→mcp 依赖链） |
| `LLMBridge` | [llm_bridge.py](file:///d:/ZephyrAlpha/src/zephyr/integration/llm_bridge.py) | LLM 修复文本生成（不可用时降级为模板） |

**MCP 服务器集群**（[config/mcp.json](file:///d:/ZephyrAlpha/config/mcp.json)）：10 个服务器（task_manager / knowledge_base / gate_engine / session_handoff / intent_router / sentinel_server / blueprint_search / sandbox / governance / vector_memory / red_blue_validator），网关提供 Auth/ACL + RateLimit + Route + Audit + Degrade。

#### 4.6.2 安全层（security）

**位置**：[src/zephyr/security/](file:///d:/ZephyrAlpha/src/zephyr/security/) | **蓝图**：MOD-SEC_security

LLM 防御 L0-L8 九层纵深防御栈。

| 类 | 文件 | 职责 |
|----|------|------|
| `LLMSecurityProtocol` | [llm_defense/llm_security/protocol.py](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/protocol.py) | 防御层抽象基类（fail-closed：层不可用→BLOCK） |
| `LSGSecurityGateway` | [llm_defense/llm_security/gateway.py](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/gateway.py) | LSG 安全网关编排器（所有 LLM 调用必经） |
| `InputSanitizer` | [llm_defense/llm_security/input_sanitizer.py](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/input_sanitizer.py) | 输入消毒（路径穿越/命令注入/上下文注入） |
| `AuditLogger` | [llm_defense/llm_security/behavior_audit_logger.py](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/behavior_audit_logger.py) | 行为审计日志（带轮转） |

**防御层**：L0 供应链 / L1 输入 / L2 提示保护 / L2a 进程沙箱 / L3 输出 / L4 Agent / L5 资源保护 / L6 数据流+可观测性 / L8 合规+多 Agent。

> **RULE-LSG-001 铁律**：所有 LLM 调用必须经过 `LSGSecurityGateway`，禁止裸调任何 LLM API。运行时拦截器（[sitecustomize.py](file:///d:/ZephyrAlpha/sitecustomize.py)）在解释器启动时自动安装，monkey-patch openai/anthropic/litellm/langchain。

---

## 5. 关键类与函数说明

### 5.1 AutoRuntimeCore（系统大脑）

```python
# src/zephyr/trading/auto_runtime_core.py
class AutoRuntimeCore:
    def __init__(self, config: RuntimeConfig | None = None, ...): ...
    def boot(self) -> BootReport          # 启动所有子组件 + 注册钩子
    def shutdown(self) -> ShutdownReport   # 优雅关闭（try/finally 保证 _booted=False）
    def reconcile(self) -> ReconciliationReport  # MAPE-K 循环（孤儿率/健康/任务学习/A2A同步）
    def dispatch_task(self, task: WorkItem) -> str
    def submit_work(self, work: WorkItem) -> str
    def submit_dag(self, dag_id, params) -> str
```

### 5.2 WorkOrchestrator（工作编排）

```python
# src/zephyr/trading/work_orchestrator.py
class WorkOrchestrator:
    def __init__(self, capability_registry, dag_dir=None, max_parallel_l1=1, max_parallel_l2=3, max_parallel_l3=2): ...
    def register_dag(self, dag: WorkDAG) -> None
    def submit(self, work: WorkItem) -> str
    def submit_dag(self, dag_id, params=None) -> str
    def schedule_next(self) -> list[WorkItem]
    def resolve_layer(self, work: WorkItem) -> str   # 决定 L1/L2/L3
    def acquire_slot(self, layer: str) -> bool        # 获取并行槽位
    def release_slot(self, layer: str) -> None
```

### 5.3 Conductor（全自动指挥官）

```python
# src/zephyr/trading/conductor.py
class Conductor:
    def __init__(self, session_id: str, db_path=None, max_parallel: int = 3): ...
    def plan_cycle(self, max_tasks: int = 10) -> list[list[TaskCard]]
        # recover_stale_claims → AutoPilot.run_cycle → _detect_file_conflicts
        # → _group_by_conflict（贪心着色，保证同组无文件冲突）
    def mark_completed(self, task_id, note=None) -> None
    def mark_failed(self, task_id, note) -> None
    def is_done(self) -> bool
```

### 5.4 CapabilityRegistry（能力注册表）

```python
# src/zephyr/trading/capability_registry.py
class CapabilityRegistry:
    def register(self, card: CapabilityCard) -> None   # 注册能力卡
    def discover(self, query: str) -> list[CapabilityCard]  # 子串搜索
    def find_by_tags(self, tags: list[str]) -> list[CapabilityCard]
    def health_check_all(self) -> dict[str, bool]
```

### 5.5 FactorBase（因子抽象）

```python
# src/zephyr/factor/factor_base.py
class FactorBase(ABC):
    meta: ClassVar[FactorMeta]  # 必须定义
    @abstractmethod
    def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series  # 返回横截面评分
    def validate(self, data: pd.DataFrame) -> bool  # 默认非空检查

class FactorRegistry:  # 单例
    @classmethod
    def register(cls, factor_cls): ...  # 装饰器自注册
    @classmethod
    def get(cls, factor_id) -> type[FactorBase] | None
    @classmethod
    def list_all(cls) -> list[str]
```

### 5.6 MatchingEngine（回测撮合）

```python
# src/zephyr/backtest/core/matching_engine.py
class MatchingEngine:
    def generate_fills(self, target_weights, prices, portfolio, date, prev_close=None) -> list[BacktestFill]
    def generate_fills_with_order_book(self, target_weights, order_books, portfolio, date, prev_close=None) -> list[BacktestFill]
    def generate_fills_with_tick(self, target_weights, ticks, portfolio, date) -> list[BacktestFill]
    # 委托纯函数 MatchingLogic，保证回测=实盘一致性
```

### 5.7 IntegratorScheduler（数据调度）

```python
# src/zephyr/data/scheduler.py
class IntegratorScheduler:
    # APScheduler BackgroundScheduler 编排器
    # 5 cron 时段 + DAG 依赖 + 断点续传 + 失败告警
    def subscribe(self, event, handler): ...  # 热配置重载
```

### 5.8 LSGSecurityGateway（LLM 安全网关）

```python
# src/zephyr/security/llm_defense/llm_security/gateway.py
class LSGSecurityGateway:
    async def scan_input(self, user_text, metadata=None) -> ScanResult   # 输入安检
    async def scan_output(self, llm_response) -> ScanResult              # 输出安检
    async def full_scan(self, user_text, llm_response) -> ScanResult     # 全量流水线
    # 返回 SecurityDecision.ALLOW/DENY；ALLOW 时自动颁发运行时令牌
```

---

## 6. 依赖关系

### 6.1 层级依赖方向

```
shared (paths, errors, types, constants, event_bus)   ← 最底层，无外部依赖
    ↑
infrastructure (cost_tracker, event_store, sla_monitor)
    ↑
data / integration / security / governance / backtest / factor / risk
    ↑
trading (AutoRuntimeCore)   ← 顶层，组合所有子组件
```

> `shared.io.paths.REPO_ROOT` / `DB_PATH` 是被最广泛 import 的符号。`shared` 禁止 import `integration.*`（向下依赖原则）。

### 6.2 量化交易域依赖流

```
market_data (NormalizedMarketData CTR-001)
    → factor (FactorBase → FactorSignal CTR-002)
        → signal_fundamental (AlphaSignalPipeline 合成)
            → risk (RiskLimits CTR-003 约束)
                → pf_core (StrategyBase 目标权重)
                    → ex_core (ExecutionEngine → Fill CTR-005)
                        → backtest (镜像实盘路径 + DecisionGate 门控)
```

### 6.3 治理域依赖流

```
governance/ (桥接层, G-CT-001~008 契约)
    ├─ gov_audit (审计追踪, 漂移/脚本发现的汇聚点)
    ├─ gov_drift (漂移检测 → 发现回流 gov_audit)
    ├─ gov_kb (知识管线, 依赖 gov_enforcement.gate_engine)
    ├─ gov_enforcement (规则执行, 共享门禁基础设施)
    ├─ gov_rule / gov_code_quality (迁移子域)
    └─ scripts/governance/ (12 维审计扫描, 消费治理事实)
```

### 6.4 关键依赖（depgraph）

依赖关系真源为 **PostgreSQL depgraph DB**（非 YAML）。查询方式：

- **架构数据**（depgraph.nodes/edges）：用 `apply_depgraph.py` 直接写 DB
- **规则数据**（trae_*.yaml）：改 YAML → `sync_yaml_to_depgraph.py` 单向同步到 DB

```bash
# 刷新运营态
python scripts/governance/d5_architecture/generate_project_depgraph.py
# 登记设计态
python scripts/governance/d5_architecture/apply_depgraph.py --add-design-node PATH BLUEPRINT_ID DOMAIN_ID
```

### 6.5 外部依赖（pyproject.toml）

| 依赖 | 用途 |
|------|------|
| `pydantic>=2.0` | 数据验证 |
| `pandas>=2.0` | 数据处理 |
| `psycopg2-binary` | PostgreSQL（depgraph） |
| `duckdb>=0.10` | DuckDB（Warm 层） |
| `chromadb>=0.4.24` | 向量数据库（KB） |
| `apscheduler>=3.10` | 任务调度 |
| `sqlalchemy>=2.0` | ORM（JobStore） |
| `openai>=1.0` | LLM API |
| `sentence-transformers>=3.0` | 嵌入模型 |
| `panel`/`holoviews`/`datashader` | v3.0 可视化（仪表盘） |
| `mcp>=1.0` | MCP SDK |
| `structlog>=24.1` | 结构化日志 |

---

## 7. 项目运行方式

### 7.1 安装

```bash
cd D:\ZephyrAlpha
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
# 可选：pip install -r requirements-demo.txt（Akshare 演示）
# 或：pip install -e ".[demo]"
```

### 7.2 CLI 命令

安装后提供两个控制台命令（[pyproject.toml](file:///d:/ZephyrAlpha/pyproject.toml) `[project.scripts]`）：

| 命令 | 模块 | 用途 |
|------|------|------|
| `zephyr` | `zephyr.trading.__main__:main` | AutoRuntime Core 主入口 |
| `integrator` | `zephyr.data.cli:main` | 数据源集成器 CLI |

#### `zephyr` 命令

```bash
zephyr [--once] [--no-demo] [--no-dream] [--interval N]
# --once: 运行一次 reconcile 后退出
# --no-demo: 跳过演示任务
# --no-dream: 跳过 dream cycle
# --interval: reconcile 间隔秒数（默认 5.0）
```

#### `integrator` 命令（8 子命令）

```bash
integrator status [task_id]              # 今日所有任务 / 单任务详情
integrator list [--source <src>]         # 列出任务
integrator run <task_id>                 # 手动触发单个任务
integrator rerun-failed                  # 重跑今日失败任务
integrator pause <source>                # 熔断数据源
integrator resume <source>               # 恢复数据源
integrator start                         # 启动常驻调度进程
integrator speed-test [--source] [--capability]  # 数据源测速
```

#### 其他模块入口

```bash
python -m zephyr.gov_drift               # 漂移检测 CLI（scan/self-test/budget/list/status）
python -m zephyr.autonomy_core           # 技能注册表 CLI（list/status/help）
python -m zephyr.data.scheduler          # 数据调度守护进程
python -m zephyr.security.adversarial_validation  # 红蓝对抗验证器
python -m zephyr.infrastructure.auto_fix_engine   # 自动修复引擎
```

### 7.3 Docker 部署（全栈）

```bash
docker-compose up
```

启动 4 个服务（[docker-compose.yml](file:///d:/ZephyrAlpha/docker-compose.yml)）：

| 服务 | 端口 | 说明 |
|------|------|------|
| `zephyr-core` | 8000 | CMD `python -m zephyr.trading`；2 CPU/2GB |
| `prometheus` | 9090 | 监控（30 天 TSDB） |
| `grafana` | 3000 | 仪表盘（admin/zephyr_admin） |
| `node-exporter` | 9100 | 主机指标 |

Dockerfile 基于 `python:3.12-slim`，健康检查 `python -c "import zephyr"`，暴露 8000 端口。

### 7.4 数据调度器（Windows）

```powershell
# 手动启动（自动重启循环）
powershell -File scripts\start_scheduler.ps1

# 注册为 Windows 计划任务（AtStartup，SYSTEM 权限）
# 需管理员 PowerShell 运行 scripts\register_scheduler_task.ps1
# 管理：schtasks /run|/end|/query /tn ZephyrAlpha_DataScheduler
```

### 7.5 MCP 服务器集群

```bash
python scripts\mcp\launcher.py           # 启动 10 个 MCP 服务器（DAG 拓扑序）
python scripts\mcp\launcher.py --dry-run # 仅打印启动计划
python scripts\mcp\status_all.py         # 查看运行状态
python scripts\mcp\stop_all.py           # 停止所有 MCP 服务器
```

> MCP 集群也会在 AutoRuntime Core 启动时由 `boot_hooks.py` 在守护线程中自动启动。

### 7.6 仪表盘（Panel）

```bash
# 方法 1（推荐）：
panel serve src/zephyr/frontend/dashboard/app_panel.py --show --port 5006
# 方法 2：
python src/zephyr/frontend/dashboard/app_panel.py
# 浏览器访问：http://localhost:5006
```

10 个 Tab（5 治理 + 5 交易/回测）。

### 7.7 端到端演示

```bash
python scripts/demos/demo_e2e_pipeline.py   # 依赖网络与 Akshare
```

### 7.8 环境变量

复制 [.env.example](file:///d:/ZephyrAlpha/.env.example) → `.env` 并填入：

| 类别 | 变量 |
|------|------|
| AI API | `DEEPSEEK_API_KEY` / `GLM_API_KEY` / `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `KIMI_API_KEY` |
| 数据源 | `IFIND_USERNAME` / `IFIND_PASSWORD` / `TIINGO_API_KEY` / `FINNHUB_API_KEY` 等 |
| 数据库 | `ZEPHYR_DB_PATH`（默认 `.runtime/db/zephyr.db`）；PostgreSQL 真源 `config/.env.postgres` |
| 运行时 | `ZEPHYR_ENV`（dev/staging/production/test）/ `ZEPHYR_LOG_LEVEL` / `ZEPHYR_PROJECT_ROOT` |
| 审计 | `ZEPHYR_AUDIT_HMAC_SECRET`（**生产必填**） |
| 告警 | `ZEPHYR_FEISHU_WEBHOOK` / `ZEPHYR_SMTP_*` |
| MCP | `ZEPHYR_MCP_LOG_LEVEL` / `ZEPHYR_MCP_TIMEOUT` / `ZEPHYR_MCP_RATE_LIMIT_QPS` |

### 7.9 测试

```bash
pytest                           # 全量测试
pytest -m "not slow"             # 跳过慢测试
pytest -m "not e2e"              # 跳过端到端
pytest tests/backtest/           # 单目录
pytest --cov=zephyr --cov-report=term-missing   # 覆盖率（阈值 70%）
```

测试按功能域归类（84 子目录），不混入测试类型维度。

---

## 8. 技术栈与配置

### 8.1 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.12+（`requires-python = ">=3.12"`） |
| 验证 | Pydantic v2 |
| 异步 | asyncio |
| 数据库 | PostgreSQL（depgraph 真源）/ ClickHouse（Hot 层）/ DuckDB（Warm 层）/ ChromaDB（向量）/ SQLite（审计） |
| 调度 | APScheduler 3.x |
| ORM | SQLAlchemy 2.x |
| LLM | OpenAI SDK（经 LSG 安全网关） |
| 嵌入 | sentence-transformers（BGE-M3） |
| 可视化 | Panel + HoloViz + plotly_resampler（v3.0 #ARCH-047） |
| 日志 | structlog |
| Lint | ruff（target py312, line-length 120） |
| 类型 | mypy（disallow_any_generics + warn_any_explicit） |
| 测试 | pytest + pytest-asyncio + pytest-cov |
| 容器 | Docker / docker-compose |

### 8.2 关键配置文件

| 文件 | 用途 |
|------|------|
| [config/mcp.json](file:///d:/ZephyrAlpha/config/mcp.json) | MCP 服务器注册表（10 服务器 + 网关策略） |
| [config/trigger_router.yaml](file:///d:/ZephyrAlpha/config/trigger_router.yaml) | 事件驱动路由表（6 触发器 + handler + 安全等级） |
| [config/sla_targets.yaml](file:///d:/ZephyrAlpha/config/sla_targets.yaml) | SLA 目标（RTO/RPO） |
| [config/risk_params.yaml](file:///d:/ZephyrAlpha/config/risk_params.yaml) | 风险参数 |
| [config/capacity_slo.yaml](file:///d:/ZephyrAlpha/config/capacity_slo.yaml) | 容量 SLO |
| [src/zephyr/data/config/tasks.yaml](file:///d:/ZephyrAlpha/src/zephyr/data/config/tasks.yaml) | 数据任务清单（10 任务） |
| [architecture_model/index.yaml](file:///d:/ZephyrAlpha/architecture_model/index.yaml) | 架构模型 SSoT（53 域） |

### 8.3 Hot/Warm/Cold 三层存储架构

| 层 | 职责 | 存储 | 场景 |
|----|------|------|------|
| Hot | 高频实时数据 | ClickHouse MergeTree + 常驻内存 | tick_data / index_quote |
| Warm | 中频历史数据 | DuckDB + Parquet | daily_kline 等 |
| Cold | 长期归档（7 年合规） | E 盘 Parquet（架构预留） | 合规归档 |

### 8.4 治理铁律速查

| 铁律 | 要点 |
|------|------|
| SSoT 真源分类 | 规则数据→YAML（sync 到 DB）；架构数据→PostgreSQL DB（apply_*.py 直接写） |
| 依赖关系先行 | 施工前 MUST 先 `apply_depgraph.py --add-design-node` 登记依赖 |
| 任务系统 SSoT | 查询任务状态 MUST 通过 TaskRepository，禁止直接读 tasks/*.md |
| LLM 安全 | 所有 LLM 调用必经 LSGSecurityGateway，禁止裸调 |
| PIT 铁律 | 回测零前瞻偏差 + 三平面一致性 + Embargo 期 |
| 容量治理 | 单域 production_nodes ≤150（ARCH-CAP-002） |
| Git 提交 | 所有 commit 通过 session_worktree 流程或 GitCommitGateway |

---

> **文档说明**：本文档基于 2026-07-13 的代码库快照生成。真源以代码与 `AGENTS.md` 为准，架构数据以 depgraph DB 为准。
