---
module_id: DOC_SYSTEM_MANIFEST_001
version: 5.3.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-06
owner: 首席文档架构??
standard_type: 专业量化机构文档
applicable_scope: 全系??
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 进行??
---


# System_Manifest.md - 系统清单

> 清风量化系统 v5.3.1 的完整系统状态快??
> 
> **?? 恢复说明**: 本文档于 2026-03-31 从归档文??`06_ARCHIVE/main/BLUEPRINTS/07_SYSTEM_MANIFEST.md` 恢复，作为系统主入口文档??


## ?? 文档定位

| 属??| 说明 |
|------|------|
| **职责** | 系统清单、模块映射、目录结??|
| **定位** | ??**主入口文??* - 快速了解系统的导航??|
| **阅读时间** | 15分钟 |
| **与其他文档关??* | 本文档是入口，详细技术细节见 [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md)，愿景目标见 [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md)（合并版??|


## 开发阶段说??

| 阶段 | 目标 | 文档状??| 代码状??|
|------|------|----------|----------|
| **当前：研??策略设计** | 验证策略想法，建立方法论 | 完善??| 框架+示例代码 |
| **下一步：回测验证** | 用历史数据验证策??| - | 可执行代??|
| **未来：模拟交??* | 真实环境验证 | - | 生产级代??|
| **未来：实盘交??* | 实际资金验证 | - | 交易级代??|

> **重要说明**：当前所有代码均??*示例代码/框架代码**，用于说明逻辑??*不可直接运行**??


## 1. 物理架构 (v5.3.1)

```
D:\ZephyrAlpha\
├── config/                            # 配置文件
??  ├── system.yaml
??  ├── data_sources.yaml
??  ├── factors/                      # 因子配置
??  └── risk/                         # 风险配置
├── data/                             # 数据存储 (gitignored)
├── docs/                             # 文档中心
│   ├── INDEX.md                      # 快速导航入口
│   ├── System_Manifest.md            # 本文档
│   ├── API_Contract.md              # 接口契约
│   ├── BLUEPRINT.md                  # 系统蓝图
│   ├── AI_Permissions.md            # AI权限清单
│   ├── CHANGELOG.md                  # 变更日志
│   ├── 00_OVERVIEW/                  # 系统总览
│   ├── 01_FRAMEWORK/                 # 框架定义
│   ├── 02_FACTOR_LIBRARY/            # 因子库 (Layer 2)
│   ├── 03_TRADING_TACTICS/           # 交易策略 (Layer 3, 5)
│   ├── 04_EXECUTION/                 # 执行引擎 (Layer 5, 6)
│   ├── 05_IMPLEMENTATION/            # 实施指南
│   ├── 06_ARCHIVE/                   # 归档
│   ├── 07_AI_REPORTING/              # ?? Layer 7: AI报告层
│   ├── 08_HUMAN_AI_INTERFACE/        # ?? Layer 8: 人机交互层
│   ├── 09_RESEARCH_INNOVATION/       # ?? Layer 9: 研究与创新层
│   ├── 10_GOVERNANCE_COMPLIANCE/     # ?? Layer 10: 治理与合规层
│   └── 11_STRATEGIC_DECISION/        # ?? Layer 11: 战略决策层
├── notebooks/                        # Jupyter分析 (gitignored)
├── scripts/                          # 系统脚本
??  └── audit_filesystem.py
├── src/                              # 源代??
??  ├── main.py
??  ├── core/                         # 核心基类
??  ??  ├── __init__.py
??  ??  ├── base.py                  # Result, Signal, Order, Position
??  ??  └── exceptions.py            # 异常类定??
??  ├── modules/                      # 功能模块
??  ??  ├── __init__.py
??  ??  ├── alert_manager.py
??  ??  ├── factor_calculator.py     # ??已实??
??  ??  └── risk_manager.py          # ??已实??
??  └── utils/                        # 工具函数
??      └── __init__.py
├── tests/                            # 测试代码
??  ├── __init__.py
??  ├── conftest.py
??  ├── unit/                        # 单元测试
??  ├── integration/                 # 集成测试
??  └── fixtures/                    # 测试夹具
├── .env.example                      # 环境变量模板
├── .gitignore                        # Git忽略配置
├── DOCUMENT_AUDIT_v5.3.md           # 文档审计报告
├── pyproject.toml                    # Python项目配置
├── README.md                         # 项目总入??
└── requirements.txt                  # 依赖清单
```


## 2. 模块映射??(实现状??

| 模块 | 路径 | 功能 | 状??|
|------|------|------|------|
| **核心基类** | | | |
| base | `src/core/base.py` | Result, Signal, Order, Position | ??已实??|
| exceptions | `src/core/exceptions.py` | 异常类定??| ??已实??|
| **功能模块** | | | |
| factor_calculator | `src/modules/factor_calculator.py` | 因子计算 (87个Alpha因子) | ??已实??|
| risk_manager | `src/modules/risk_manager.py` | 风险管理 | ??已实??|
| alert_manager | `src/modules/alert_manager.py` | 告警管理 | ??已实??|
| **规划中模??* | | | |
| data_collector | `src/modules/data_collector.py` | 数据采集 | ?? 规划??|
| data_cleaner | `src/modules/data_cleaner.py` | 数据清洗 | ?? 规划??|
| data_storage | `src/modules/data_storage.py` | 数据存储 | ?? 规划??|
| strategy_engine | `src/modules/strategy_engine.py` | 策略引擎 | ?? 规划??|
| backtest_framework | `src/modules/backtest_framework.py` | 回测框架 | ?? 规划??|
| trade_executor | `src/modules/trade_executor.py` | 交易执行 | ?? 规划??|
| monitoring_system | `src/modules/monitoring_system.py` | 监控系统 | ?? 规划??|
| config_manager | `src/modules/config_manager.py` | 配置管理 | ?? 规划??|
| task_scheduler | `src/modules/task_scheduler.py` | 任务调度 | ?? 规划??|
| logger | `src/modules/logger.py` | 日志系统 | ?? 规划??|
| performance_monitor | `src/modules/performance_monitor.py` | 性能监控 | ?? 规划??|

> **状态说??*: ??已实??= 可直接使??| ?? 规划??= 已有规格，待开??| ??待开??= 尚未规划


## 3. 接口版本管理

| 接口 | 版本 | 最后更??| 说明 |
|------|------|----------|------|
| DataHub ??FactorCalculator | 1.0 | 2026-03-28 | OHLCV + 指标 |
| FactorCalculator ??StrategyEngine | 1.0 | 2026-03-28 | 因子??+ 时间??|
| StrategyEngine ??RiskManager | 1.0 | 2026-03-28 | 信号 + 头寸 |
| RiskManager ??TradeExecutor | 1.0 | 2026-03-28 | 订单 + 风控标志 |


## 4. 依赖矩阵

### Python环境
- **Python版本**: 3.10+
- **包管??*: pip / uv

### 核心依赖
| ??| 版本 | 用??|
|----|----|------|
| pandas | 2.2.0+ | 数据处理 |
| numpy | 1.26.0+ | 数值计??|
| scipy | 1.11.0+ | 科学计算 |
| scikit-learn | 1.3.0+ | 机器学习 |
| sqlalchemy | 2.0.0+ | 数据库ORM |
| pyyaml | 6.0+ | 配置管理 |
| loguru | 0.7.0+ | 日志系统 |
| apscheduler | 3.10.0+ | 任务调度 |

### 数据源依??
| ??| 版本 | 用??|
|----|----|------|
| akshare | 1.14.0+ | 实时行情 |
| baostock | 0.0.9+ | 历史数据 |
| tushare | 1.3.0+ | 财务数据 |


## 5. AI权限矩阵

### ??可写权限（AI可修改）

| 路径 | 说明 |
|------|------|
| `docs/02_FACTOR_LIBRARY/02_ALPHA_FACTORS/` | Alpha因子定义 |
| `docs/02_FACTOR_LIBRARY/05_BACKTEST/` | 回测报告 |
| `docs/03_TRADING_TACTICS/` | 策略文档 |
| `src/modules/` | 模块实现代码 |
| `tests/` | 测试代码 |
| `notebooks/` | Jupyter分析 |
| `docs/CHANGELOG.md` | 变更日志 |

### ?? 只读权限（AI仅可读取??

| 路径 | 说明 |
|------|------|
| `docs/00_OVERVIEW/` | 系统总览 |
| `docs/01_FRAMEWORK/` | 核心框架 |
| `docs/02_FACTOR_LIBRARY/00_INDEX/` | 因子索引 |
| `docs/02_FACTOR_LIBRARY/01_STANDARDS/` | 研究方法??|
| `docs/04_EXECUTION/` | 执行引擎规格 |
| `config/` | 配置文件 |
| `src/core/` | 核心基础??|
| `System_Manifest.md` | 系统清单 |
| `API_Contract.md` | 接口契约 |
| `AI_Permissions.md` | 权限清单 |

### ??禁止权限（AI严禁修改??

| 路径 | 说明 |
|------|------|
| `.env` | API密钥 |
| `secrets/` | 私钥存放 |
| `.gitignore` | Git配置 |
| `pyproject.toml` | 项目配置 |


## 6. 配置文件关联

```
config/
├── system.yaml ──────────────??main.py
├── data_sources.yaml ────────??data_collector
├── factors/
??  └── selected_factors.yaml ─??factor_calculator
└── risk/
    └── rules.yaml ──────────??risk_manager
```


## 7. 数据存储规格

| 存储??| 格式 | 位置 | 说明 |
|--------|------|------|------|
| 原始数据 | Parquet | `data/raw/{type}/{year}/` | 原始采集数据 |
| 处理后数??| Parquet + SQLite | `data/processed/` | 清洗后数??|
| 因子数据 | Parquet | `data/factors/{factor_id}/` | 按因子存??|
| 信号数据 | SQLite | `data/signals/` | 策略信号 |
| 订单数据 | SQLite | `data/orders/` | 交易订单 |
| 回测结果 | Parquet | `data/backtest_results/` | 回测绩效 |


## 8. 版本管理规则

### 主版本升级（v5.0 ??v6.0??
- 架构改变（Layer 0-11重组??
- 核心模块替换
- 数据格式不兼??

### 次版本升级（v5.0 ??v5.3??
- 新增模块
- 新增因子??
- 新增策略

### 补丁版本升级（v5.0 ??v5.0.1??
- Bug修复
- 文档更新
- 性能优化


## 9. 启动检查清??

AI启动前必读顺序：
1. ??读取本文件（System_Manifest.md??
2. ??读取 `docs/INDEX.md` - 快速导??
3. ??读取 `API_Contract.md`
4. ??读取 `AI_Permissions.md`
5. ??读取相关模块??`README.md`


## 10. 核心文档索引

| 文档 | 说明 | 优先??|
|------|------|--------|
| [INDEX.md](../03_TRADING_TACTICS/INDEX.md) | 快速导航入口（5分钟??| ??必读 |
| [SITEMAP.md](SITEMAP.md) | 完整文档地图（深度参考） | ??导航 |
| [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | 系统蓝图（合并版??| ??必读 |
| [System_Manifest.md](System_Manifest.md) | 系统清单 | ??必读 |
| [API_Contract.md](../03_TRADING_TACTICS/API_Contract.md) | 接口契约 | ??必读 |
| [AI_Permissions.md](../08_AI_GOVERNANCE/AI_Permissions.md) | AI权限清单 | ??必读 |
| [Strategy_Spec_S001.md](../03_TRADING_TACTICS/Strategy_Spec_S001.md) | 策略模板 | 建议 |

> **说明**: INDEX.md为快速入口（5分钟），SITEMAP.md为完整地图（深度参考），两者职责互补??


## 11. 模块蓝图索引

| 蓝图文档 | 路径 | 模块ID | 版本 | 状??| 职责概要 |
|----------|------|--------|------|------|----------|
| [Layer 11架构蓝图](../module_designs/layer_11/LAYER_11_ARCHITECTURE.md) | `docs/module_designs/layer_11/LAYER_11_ARCHITECTURE.md` | LAYER_11_ARCH_001 | 1.0 | Active | 文字驱动层整体架构、技术选型、实施方案、成本评??|
| [文字驱动核心模块](../module_designs/layer_11/L11_TEXT_DRIVER.md) | `docs/module_designs/layer_11/L11_TEXT_DRIVER.md` | L11_TEXT_DRIVER_001 | 1.0 | Active | 自然语言理解、意图识别、参数提取、工具调??|
| [量化交易Agent模块](../module_designs/layer_11/L11_QUANT_AGENT.md) | `docs/module_designs/layer_11/L11_QUANT_AGENT.md` | L11_QUANT_AGENT_001 | 1.0 | Active | Agent框架、模型管理、工具集成、记忆管理、安全机??|
| [Layer 11工具封装蓝图](../module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md` | LAYER_11_TOOL_ENCAP_001 | 1.0 | Active | 工具封装架构、单一AI层设计、纯执行层分离、性能优化 |
| [Layer 11工具接口规范](../module_designs/layer_11/LAYER_11_TOOL_INTERFACE_SPECIFICATION.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_INTERFACE_SPECIFICATION.md` | LAYER_11_TOOL_SPEC_001 | 1.0 | Active | 所有模块工具接口详细定义、操作规范、参数定义、返回值规??|
| [因子库蓝图](FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md) | `docs/02_FACTOR_LIBRARY/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md` | FACTOR_BACKTEST_001 | 1.0 | Active | 因子计算、存储、IC分析、Backtrader回测集成 |
| [模拟交易蓝图](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | `docs/04_EXECUTION/06_SIMULATION/BLUEPRINT.md` | SIMULATION_001 | 1.0 | Active | 模拟撮合引擎、模拟账户管理、交易执??|
| [策略引擎蓝图](../03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_BLUEPRINT.md) | `docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_BLUEPRINT.md` | STRAT_ENGINE_001 | 1.0 | Active | 策略引擎开发、开源模块集??|
| [专业多时间框架架构](../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) | `docs/01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md` | FRAMEWORK_PROF_ARCH_001 | 1.0 | Active | 三级时间框架融合架构、桥??文艺复兴模式融合 |
| [专业实施蓝图](../01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) | `docs/01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md` | FRAMEWORK_IMPL_BLUEPRINT_001 | 1.0 | Active | 6个月实施路线图、开源集成策略、风险管??|
| [直播金融分析蓝图](../04_EXECUTION/07_LIVE_STREAM/LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md) | `docs/04_EXECUTION/07_LIVE_STREAM/LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md` | LIVE_STREAM_FINANCIAL_ANALYSIS_001 | 1.0 | Active | 多主播直播监控、MP3录制、AI内容分析、观点聚合、因子生??|
| [AI工作记录与优化模块蓝图](../10_AI_WORKFLOW/AI_WORKFLOW_LOGGER_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/AI_WORKFLOW_LOGGER_BLUEPRINT.md` | AI_WORKFLOW_LOGGER_001 | 1.0 | Active | AI会话记录、决策记录、效果评估、优化迭代、知识库构建 |
| [AI工作汇报与交付模块蓝图](../10_AI_WORKFLOW/AI_WORK_REPORTER_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/AI_WORK_REPORTER_BLUEPRINT.md` | AI_WORK_REPORTER_001 | 1.0 | Active | 每日工作总结、进度通知、决策汇报、交互交付、可视化展示 |
| [复盘模块蓝图](../10_AI_WORKFLOW/POST_TRADE_REVIEW_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/POST_TRADE_REVIEW_BLUEPRINT.md` | POST_TRADE_REVIEW_001 | 1.0 | Active | 回测复盘、实盘复盘、因子复盘、策略复盘、风险复??|
| [全流程数据保存机制蓝图](../10_AI_WORKFLOW/FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md` | FULL_PROCESS_DATA_PERSISTENCE_001 | 1.0 | Active | 实验追踪、数据血缘、版本控制、数据治??|
| [开源项目集成方案蓝图](../10_AI_WORKFLOW/OPEN_SOURCE_INTEGRATION_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/OPEN_SOURCE_INTEGRATION_BLUEPRINT.md` | OPEN_SOURCE_INTEGRATION_001 | 1.0 | Active | MLflow集成、Qlib集成、架构参考、工具集??|
| [合规监控模块蓝图](../10_AI_WORKFLOW/COMPLIANCE_MONITORING_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/COMPLIANCE_MONITORING_BLUEPRINT.md` | COMPLIANCE_MONITORING_001 | 1.0 | Active | 交易合规检查、风控合规检查、监管报告生成、审计追踪、违规预??|
| [实盘监控模块蓝图](../10_AI_WORKFLOW/LIVE_TRADING_MONITOR_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/LIVE_TRADING_MONITOR_BLUEPRINT.md` | LIVE_TRADING_MONITOR_001 | 1.0 | Active | 实时交易监控、持仓风险监控、异常交易预警、性能指标监控、多渠道告警 |
| [性能分析模块蓝图](../10_AI_WORKFLOW/PERFORMANCE_ANALYSIS_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/PERFORMANCE_ANALYSIS_BLUEPRINT.md` | PERFORMANCE_ANALYSIS_001 | 1.0 | Active | 性能指标采集、性能瓶颈识别、性能报告生成、优化建议生成、性能趋势分析 |
| **Layer 6: 组合优化层蓝??* | | | | | |
| [Barra风险模型蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BARRA_RISK_MODEL_BLUEPRINT.md) | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/BARRA_RISK_MODEL_BLUEPRINT.md` | BARRA_RISK_001 | 1.0 | Active | P0级核心模块、多因子风险模型、风险分解、因子暴露控??|
| [约束求解器蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/CONSTRAINT_SOLVER_BLUEPRINT.md) | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/CONSTRAINT_SOLVER_BLUEPRINT.md` | CONSTRAINT_SOLVER_001 | 1.0 | Active | P0级核心模块、凸优化求解、约束验证、冲突解??|
| [风险归因系统蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md) | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RISK_ATTRIBUTION_SYSTEM_BLUEPRINT.md` | RISK_ATTRIBUTION_001 | 1.0 | Active | P1级模块、因子风险归因、行业风险归因、资产风险归??|
| [多资产类别配置蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MULTI_ASSET_ALLOCATION_BLUEPRINT.md) | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MULTI_ASSET_ALLOCATION_BLUEPRINT.md` | MULTI_ASSET_001 | 1.0 | Active | P1级模块、跨资产风险平价、全天候策略、动态配??|
| [组合再平衡策略蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_REBALANCING_BLUEPRINT.md) |

| [动态相关性建模蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DYNAMIC_CORRELATION_MODELING_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DYNAMIC_CORRELATION_MODELING_BLUEPRINT.md | DYNAMIC_CORR_001 | 1.0 | Active | P0级核心模块、DCC-GARCH动态相关性、桥水核心能力 |
| [动态杠杆管理蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DYNAMIC_LEVERAGE_MANAGEMENT_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/DYNAMIC_LEVERAGE_MANAGEMENT_BLUEPRINT.md | LEVERAGE_001 | 1.0 | Active | P1级模块、波动率目标策略、动态杠杆调节 |
| [统计套利模块蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STATISTICAL_ARBITRAGE_MODULE_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STATISTICAL_ARBITRAGE_MODULE_BLUEPRINT.md | STATISTICAL_ARBITRAGE_001 | 1.0 | Active | P1级模块、配对交易、协整分析 |
| [交易成本优化蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TRADING_COST_OPTIMIZATION_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TRADING_COST_OPTIMIZATION_BLUEPRINT.md | TRADING_COST_001 | 1.0 | Active | P1级模块、Almgren-Chriss模型、最优执行 |
| [简化风险预算系统蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SIMPLIFIED_RISK_BUDGET_SYSTEM_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SIMPLIFIED_RISK_BUDGET_SYSTEM_BLUEPRINT.md | RISK_BUDGET_001 | 1.0 | Active | P1级模块、三层风险预算体系 |
| [简化时间框架协同蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SIMPLIFIED_TIMEFRAME_COORDINATION_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SIMPLIFIED_TIMEFRAME_COORDINATION_BLUEPRINT.md | TIMEFRAME_COORD_001 | 1.0 | Active | P1级模块、三级时间框架协同 |
| [压力测试系统蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRESS_TESTING_SYSTEM_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/STRESS_TESTING_SYSTEM_BLUEPRINT.md | STRESS_TEST_001 | 1.0 | Active | P2级模块、历史情景回放、蒙特卡洛模拟 |
| [强化学习再平衡系统蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RL_REBALANCING_SYSTEM_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/RL_REBALANCING_SYSTEM_BLUEPRINT.md | RL_REBALANCING_001 | 1.0 | Active | P2级模块、PPO/SAC强化学习 |
| [多策略分层系统蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md | STRATEGY_HIERARCHY_001 | 1.0 | Active | P2级模块、策略分层权重分配 |
| [组合保险策略蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md | CPPI_BLUEPRINT_001 | 1.0 | Active | 可选模块、CPPI/OBPI组合保险 |
| [尾部风险对冲蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TAIL_RISK_HEDGING_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/TAIL_RISK_HEDGING_BLUEPRINT.md | TAIL_RISK_BLUEPRINT_001 | 1.0 | Active | 可选模块、期权对冲、尾部风险保护 |
| [融资优化蓝图](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/FINANCING_OPTIMIZATION_BLUEPRINT.md) | docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/FINANCING_OPTIMIZATION_BLUEPRINT.md | FINANCING_BLUEPRINT_001 | 1.0 | Active | 可选模块、融资成本优化、杠杆效率提升 | `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/PORTFOLIO_REBALANCING_BLUEPRINT.md` | REBALANCING_001 | 1.0 | Active | P2级模块、强化学习调仓、多时间框架协同、动态再平衡 |
| **Layer 9: 研究与创新层** | | | | | |
| [研究与创新层蓝图](../09_RESEARCH_INNOVATION/BLUEPRINT.md) | `docs/09_RESEARCH_INNOVATION/BLUEPRINT.md` | RESEARCH_INNOVATION_001 | 1.0 | Active | AI虚拟研究实验室、创新孵化器、学术跟踪、知识管理 |
| [缺失模块补充设计](../09_RESEARCH_INNOVATION/MISSING_MODULES_SUPPLEMENT.md) | `docs/09_RESEARCH_INNOVATION/MISSING_MODULES_SUPPLEMENT.md` | LAYER9_SUPPLEMENT_001 | 1.0 | Active | 特征存储、模型注册表、研究仪表板 |
| [完整缺失模块补充方案v2.0](../09_RESEARCH_INNOVATION/COMPLETE_SUPPLEMENT_v2.md) | `docs/09_RESEARCH_INNOVATION/COMPLETE_SUPPLEMENT_v2.md` | LAYER9_COMPLETE_002 | 2.0 | Active | 数据版本控制、超参数优化、模型解释性、A/B测试、审计日志、成本管理 |

> **索引状??*: 新增Layer 11文字驱动层蓝图（3个文档）、AI工作流模块蓝图（8个文档）和Layer 6组合优化层蓝图（5个文档），已集成到系统文档体系中。包含完整的技术选型、实施方案和成本评估??

## 12. 次要文档索引

| 文档 | 路径 | 模块ID | 版本 | 状??| 说明 |
|------|------|--------|------|------|------|
| **技术规格书** | | | | | |
| [Barra风险模型技术规格书](../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/BARRA_RISK_MODEL_TECHNICAL_SPECIFICATION.md) | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/BARRA_RISK_MODEL_TECHNICAL_SPECIFICATION.md` | BARRA_RISK_SPEC_001 | 1.0 | Active | Barra风险模型详细技术设计、接口定义、数据结构、测试方??|
| [约束求解器技术规格书](../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/CONSTRAINT_SOLVER_TECHNICAL_SPECIFICATION.md) | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/CONSTRAINT_SOLVER_TECHNICAL_SPECIFICATION.md` | CONSTRAINT_SOLVER_SPEC_001 | 1.0 | Active | 约束求解器详细技术设计、凸优化算法、约束验证、测试方??|
| [风险归因系统技术规格书](../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/RISK_ATTRIBUTION_SYSTEM_TECHNICAL_SPECIFICATION.md) | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/RISK_ATTRIBUTION_SYSTEM_TECHNICAL_SPECIFICATION.md` | RISK_ATTRIBUTION_SPEC_001 | 1.0 | Active | 风险归因系统详细技术设计、多维度归因、测试方??|
| [多资产类别配置技术规格书](../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/MULTI_ASSET_ALLOCATION_TECHNICAL_SPECIFICATION.md) | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/MULTI_ASSET_ALLOCATION_TECHNICAL_SPECIFICATION.md` | MULTI_ASSET_SPEC_001 | 1.0 | Active | 多资产配置详细技术设计、风险平价、全天候策??|
| [组合再平衡策略技术规格书](../05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/PORTFOLIO_REBALANCING_TECHNICAL_SPECIFICATION.md) | `docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/PORTFOLIO_REBALANCING_TECHNICAL_SPECIFICATION.md` | REBALANCING_SPEC_001 | 1.0 | Active | 组合再平衡详细技术设计、强化学习调仓、多时间框架协同 |
| **方法论文??* | | | | | |
| [IC分析方法论](01_STANDARDS/ic_analysis.md) | `docs/02_FACTOR_LIBRARY/01_STANDARDS/ic_analysis.md` | METHODOLOGY_001 | 1.0 | Active | IC分析标准 |
| [因子预处理方法](01_STANDARDS/factor_preprocessing.md) | `docs/02_FACTOR_LIBRARY/01_STANDARDS/factor_preprocessing.md` | METHODOLOGY_002 | 1.0 | Active | 因子预处理标??|
| [因子治理框架](../../README.md) | `docs/02_FACTOR_LIBRARY/00_GOVERNANCE/README.md` | GOVERNANCE_001 | 1.0 | Active | 因子库治理框??|
| [路径标准](../05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md) | `docs/05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md` | DEV_STD_001 | 1.0 | Stable | 路径引用标准 |
| [文档编号标准](../05_IMPLEMENTATION/02_DEVELOPMENT/DOCUMENT_NUMBERING_STANDARD.md) | `docs/05_IMPLEMENTATION/02_DEVELOPMENT/DOCUMENT_NUMBERING_STANDARD.md` | DEV_STD_005 | 1.0 | Stable | 文档编号体系标准 |
| [A股规则引擎设计](../design/a_stock_rules/T.08.AR001.a_stock_rule_engine_design.md) | `docs/design/a_stock_rules/T.08.AR001.a_stock_rule_engine_design.md` | DESIGN_001 | 1.0 | Active | A股规则引擎设??|
| [交易成本模型算法](../design/trading_costs/T.05.TE001.trading_cost_model_algorithm_document.md) | `docs/design/trading_costs/T.05.TE001.trading_cost_model_algorithm_document.md` | DESIGN_002 | 1.0 | Active | 交易成本模型算法 |
| [多引擎数据一致性设计方案](../design/data_consistency/多引擎数据一致性设计方??md) | `docs/design/data_consistency/多引擎数据一致性设计方??md` | DESIGN_003 | 1.0 | Active | 多引擎数据一致性设计方??|
| [Saga模式实现流程图](../design/data_consistency/Saga模式实现流程??md) | `docs/design/data_consistency/Saga模式实现流程??md` | DESIGN_004 | 1.0 | Active | Saga模式实现流程??|
| [补偿事务设计文档](../design/data_consistency/补偿事务设计文档.md) | `docs/design/data_consistency/补偿事务设计文档.md` | DESIGN_005 | 1.0 | Active | 补偿事务设计文档 |
| [Web管理界面架构设计文档](../design/web_interface/T.06.UI001.web_management_interface_architecture_design.md) | `docs/design/web_interface/T.06.UI001.web_management_interface_architecture_design.md` | DESIGN_006 | 1.0 | Active | Web管理界面架构设计 |
| [前端组件结构图](../design/web_interface/前端组件结构??md) | `docs/design/web_interface/前端组件结构??md` | DESIGN_007 | 1.0 | Active | 前端组件结构??|
| [API接口规范文档](../design/web_interface/API接口规范文档.md) | `docs/design/web_interface/API接口规范文档.md` | DESIGN_008 | 1.0 | Active | API接口规范文档 |
| [交易成本测试用例设计](../design/trading_costs/交易成本测试用例设计.md) | `docs/design/trading_costs/交易成本测试用例设计.md` | DESIGN_009 | 1.0 | Active | 交易成本测试用例设计 |
| [技术方案设计汇总报告](../design/技术方案设计汇总报??md) | `docs/design/技术方案设计汇总报??md` | DESIGN_SUMMARY_001 | 1.0 | Active | 技术方案设计汇总报??|
| [专业审计指南](../09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md) | `docs/09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md` | AUDIT_GUIDE_001 | 1.0 | Active | 专业审计指南 |
| [审计质量标准](../09_AUDIT/STANDARDS/AUDIT_STANDARDS.md) | `docs/09_AUDIT/STANDARDS/AUDIT_STANDARDS.md` | AUDIT_STD_001 | 1.0 | Stable | 审计质量标准v1.0 |
| [质量监控蓝图](../09_AUDIT/QUALITY_MONITORING_BLUEPRINT.md) | `docs/09_AUDIT/QUALITY_MONITORING_BLUEPRINT.md` | MONITORING_001 | 1.0 | Active | 质量监控体系蓝图 |
| [技术方案评审会议议程](../design/技术方案评审会议议??md) | `docs/design/技术方案评审会议议??md` | REVIEW_AGENDA_001 | 1.0 | Active | 技术方案评审会议议??|
| [评审材料分发清单](../design/评审材料分发清单.md) | `docs/design/评审材料分发清单.md` | DISTRIBUTION_001 | 1.0 | Active | 评审材料分发指南 |
| [个人技术决策确认清单](../design/个人技术决策确认清??md) | `docs/design/个人技术决策确认清??md` | PERSONAL_DECISION_001 | 1.0 | Active | 个人项目决策流程 |
| [专业量化机构开发完整流程](../design/专业量化机构开发完整流??md) | `docs/design/专业量化机构开发完整流??md` | DEV_PROCESS_001 | 1.0 | Active | 专业量化机构开发流程指??|
| [数据库设计文档](../design/database/P0-01_Database_Design_Document.md) | `docs/design/database/P0-01_Database_Design_Document.md` | DB_DESIGN_001 | 1.0 | Active | 专业量化机构数据库设计标??|
| [数据库设计评审报告](../design/database/P0-01_Database_Design_Review_Report.md) | `docs/design/database/P0-01_Database_Design_Review_Report.md` | DB_REVIEW_001 | 1.0 | Active | 专业量化机构数据库设计评??|


**版本**: v5.3.1 | **更新**: 2026-04-06 | **状??*: ??活跃

