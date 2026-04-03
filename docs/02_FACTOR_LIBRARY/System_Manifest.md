---
module_id: DOC_SYSTEM_MANIFEST_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-02
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 进行中
---


# System_Manifest.md - 系统清单

> 清风量化系统 v5.1.0 的完整系统状态快照
> 
> **📝 恢复说明**: 本文档于 2026-03-31 从归档文件 `06_ARCHIVE/main/BLUEPRINTS/07_SYSTEM_MANIFEST.md` 恢复，作为系统主入口文档。


## 📌 文档定位

| 属性 | 说明 |
|------|------|
| **职责** | 系统清单、模块映射、目录结构 |
| **定位** | ⭐ **主入口文档** - 快速了解系统的导航页 |
| **阅读时间** | 15分钟 |
| **与其他文档关系** | 本文档是入口，详细技术细节见 [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md)，愿景目标见 [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md)（合并版） |


## 开发阶段说明

| 阶段 | 目标 | 文档状态 | 代码状态 |
|------|------|----------|----------|
| **当前：研究/策略设计** | 验证策略想法，建立方法论 | 完善中 | 框架+示例代码 |
| **下一步：回测验证** | 用历史数据验证策略 | - | 可执行代码 |
| **未来：模拟交易** | 真实环境验证 | - | 生产级代码 |
| **未来：实盘交易** | 实际资金验证 | - | 交易级代码 |

> **重要说明**：当前所有代码均为**示例代码/框架代码**，用于说明逻辑，**不可直接运行**。


## 1. 物理架构 (v5.1.0)

```
D:\ZephyrAlpha\
├── config/                            # 配置文件
│   ├── system.yaml
│   ├── data_sources.yaml
│   ├── factors/                      # 因子配置
│   └── risk/                         # 风险配置
├── data/                             # 数据存储 (gitignored)
├── docs/                             # 文档中心
│   ├── INDEX.md                      # 快速导航入口
│   ├── System_Manifest.md            # 本文件
│   ├── API_Contract.md              # 接口契约
│   ├── BLUEPRINT.md                  # 系统蓝图
│   ├── AI_Permissions.md            # AI权限清单
│   ├── CHANGELOG.md                  # 变更日志
│   ├── 00_OVERVIEW/                  # 系统总览
│   ├── 01_FRAMEWORK/                 # 框架定义
│   ├── 02_FACTOR_LIBRARY/            # 因子库
│   ├── 03_TRADING_TACTICS/           # 交易策略
│   ├── 04_EXECUTION/                 # 执行引擎
│   ├── 05_IMPLEMENTATION/            # 实施指南
│   ├── 06_ARCHIVE/                   # 归档
│   └── 07_RESEARCH/                  # AI研究
├── notebooks/                        # Jupyter分析 (gitignored)
├── scripts/                          # 系统脚本
│   └── audit_filesystem.py
├── src/                              # 源代码
│   ├── main.py
│   ├── core/                         # 核心基类
│   │   ├── __init__.py
│   │   ├── base.py                  # Result, Signal, Order, Position
│   │   └── exceptions.py            # 异常类定义
│   ├── modules/                      # 功能模块
│   │   ├── __init__.py
│   │   ├── alert_manager.py
│   │   ├── factor_calculator.py     # ✅ 已实现
│   │   └── risk_manager.py          # ✅ 已实现
│   └── utils/                        # 工具函数
│       └── __init__.py
├── tests/                            # 测试代码
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/                        # 单元测试
│   ├── integration/                 # 集成测试
│   └── fixtures/                    # 测试夹具
├── .env.example                      # 环境变量模板
├── .gitignore                        # Git忽略配置
├── DOCUMENT_AUDIT_v5.1.md           # 文档审计报告
├── pyproject.toml                    # Python项目配置
├── README.md                         # 项目总入口
└── requirements.txt                  # 依赖清单
```


## 2. 模块映射表 (实现状态)

| 模块 | 路径 | 功能 | 状态 |
|------|------|------|------|
| **核心基类** | | | |
| base | `src/core/base.py` | Result, Signal, Order, Position | ✅ 已实现 |
| exceptions | `src/core/exceptions.py` | 异常类定义 | ✅ 已实现 |
| **功能模块** | | | |
| factor_calculator | `src/modules/factor_calculator.py` | 因子计算 (87个Alpha因子) | ✅ 已实现 |
| risk_manager | `src/modules/risk_manager.py` | 风险管理 | ✅ 已实现 |
| alert_manager | `src/modules/alert_manager.py` | 告警管理 | ✅ 已实现 |
| **规划中模块** | | | |
| data_collector | `src/modules/data_collector.py` | 数据采集 | 🔄 规划中 |
| data_cleaner | `src/modules/data_cleaner.py` | 数据清洗 | 🔄 规划中 |
| data_storage | `src/modules/data_storage.py` | 数据存储 | 🔄 规划中 |
| strategy_engine | `src/modules/strategy_engine.py` | 策略引擎 | 🔄 规划中 |
| backtest_framework | `src/modules/backtest_framework.py` | 回测框架 | 🔄 规划中 |
| trade_executor | `src/modules/trade_executor.py` | 交易执行 | 🔄 规划中 |
| monitoring_system | `src/modules/monitoring_system.py` | 监控系统 | 🔄 规划中 |
| config_manager | `src/modules/config_manager.py` | 配置管理 | 🔄 规划中 |
| task_scheduler | `src/modules/task_scheduler.py` | 任务调度 | 🔄 规划中 |
| logger | `src/modules/logger.py` | 日志系统 | 🔄 规划中 |
| performance_monitor | `src/modules/performance_monitor.py` | 性能监控 | 🔄 规划中 |

> **状态说明**: ✅ 已实现 = 可直接使用 | 🔄 规划中 = 已有规格，待开发 | ❌ 待开发 = 尚未规划


## 3. 接口版本管理

| 接口 | 版本 | 最后更新 | 说明 |
|------|------|----------|------|
| DataHub → FactorCalculator | 1.0 | 2026-03-28 | OHLCV + 指标 |
| FactorCalculator → StrategyEngine | 1.0 | 2026-03-28 | 因子值 + 时间戳 |
| StrategyEngine → RiskManager | 1.0 | 2026-03-28 | 信号 + 头寸 |
| RiskManager → TradeExecutor | 1.0 | 2026-03-28 | 订单 + 风控标志 |


## 4. 依赖矩阵

### Python环境
- **Python版本**: 3.10+
- **包管理**: pip / uv

### 核心依赖
| 库 | 版本 | 用途 |
|----|----|------|
| pandas | 2.2.0+ | 数据处理 |
| numpy | 1.26.0+ | 数值计算 |
| scipy | 1.11.0+ | 科学计算 |
| scikit-learn | 1.3.0+ | 机器学习 |
| sqlalchemy | 2.0.0+ | 数据库ORM |
| pyyaml | 6.0+ | 配置管理 |
| loguru | 0.7.0+ | 日志系统 |
| apscheduler | 3.10.0+ | 任务调度 |

### 数据源依赖
| 库 | 版本 | 用途 |
|----|----|------|
| akshare | 1.14.0+ | 实时行情 |
| baostock | 0.0.9+ | 历史数据 |
| tushare | 1.3.0+ | 财务数据 |


## 5. AI权限矩阵

### ✅ 可写权限（AI可修改）

| 路径 | 说明 |
|------|------|
| `docs/02_FACTOR_LIBRARY/02_ALPHA_FACTORS/` | Alpha因子定义 |
| `docs/02_FACTOR_LIBRARY/05_BACKTEST/` | 回测报告 |
| `docs/03_TRADING_TACTICS/` | 策略文档 |
| `src/modules/` | 模块实现代码 |
| `tests/` | 测试代码 |
| `notebooks/` | Jupyter分析 |
| `docs/CHANGELOG.md` | 变更日志 |

### 🔒 只读权限（AI仅可读取）

| 路径 | 说明 |
|------|------|
| `docs/00_OVERVIEW/` | 系统总览 |
| `docs/01_FRAMEWORK/` | 核心框架 |
| `docs/02_FACTOR_LIBRARY/00_INDEX/` | 因子索引 |
| `docs/02_FACTOR_LIBRARY/01_METHODOLOGY/` | 研究方法论 |
| `docs/04_EXECUTION/` | 执行引擎规格 |
| `config/` | 配置文件 |
| `src/core/` | 核心基础类 |
| `System_Manifest.md` | 系统清单 |
| `API_Contract.md` | 接口契约 |
| `AI_Permissions.md` | 权限清单 |

### ❌ 禁止权限（AI严禁修改）

| 路径 | 说明 |
|------|------|
| `.env` | API密钥 |
| `secrets/` | 私钥存放 |
| `.gitignore` | Git配置 |
| `pyproject.toml` | 项目配置 |


## 6. 配置文件关联

```
config/
├── system.yaml ──────────────▶ main.py
├── data_sources.yaml ────────▶ data_collector
├── factors/
│   └── selected_factors.yaml ─▶ factor_calculator
└── risk/
    └── rules.yaml ──────────▶ risk_manager
```


## 7. 数据存储规格

| 存储层 | 格式 | 位置 | 说明 |
|--------|------|------|------|
| 原始数据 | Parquet | `data/raw/{type}/{year}/` | 原始采集数据 |
| 处理后数据 | Parquet + SQLite | `data/processed/` | 清洗后数据 |
| 因子数据 | Parquet | `data/factors/{factor_id}/` | 按因子存储 |
| 信号数据 | SQLite | `data/signals/` | 策略信号 |
| 订单数据 | SQLite | `data/orders/` | 交易订单 |
| 回测结果 | Parquet | `data/backtest_results/` | 回测绩效 |


## 8. 版本管理规则

### 主版本升级（v5.0 → v6.0）
- 架构改变（Layer 0-7重组）
- 核心模块替换
- 数据格式不兼容

### 次版本升级（v5.0 → v5.1）
- 新增模块
- 新增因子库
- 新增策略

### 补丁版本升级（v5.0 → v5.0.1）
- Bug修复
- 文档更新
- 性能优化


## 9. 启动检查清单

AI启动前必读顺序：
1. ✅ 读取本文件（System_Manifest.md）
2. ✅ 读取 `docs/INDEX.md` - 快速导航
3. ✅ 读取 `API_Contract.md`
4. ✅ 读取 `AI_Permissions.md`
5. ✅ 读取相关模块的 `README.md`


## 10. 核心文档索引

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [INDEX.md](../03_TRADING_TACTICS/INDEX.md) | 快速导航入口（5分钟） | ⭐ 必读 |
| [SITEMAP.md](SITEMAP.md) | 完整文档地图（深度参考） | ⭐ 导航 |
| [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | 系统蓝图（合并版） | ⭐ 必读 |
| [System_Manifest.md](System_Manifest.md) | 系统清单 | ⭐ 必读 |
| [API_Contract.md](../03_TRADING_TACTICS/API_Contract.md) | 接口契约 | ⭐ 必读 |
| [AI_Permissions.md](../08_AI_GOVERNANCE/AI_Permissions.md) | AI权限清单 | ⭐ 必读 |
| [Strategy_Spec_S001.md](../03_TRADING_TACTICS/Strategy_Spec_S001.md) | 策略模板 | 建议 |

> **说明**: INDEX.md为快速入口（5分钟），SITEMAP.md为完整地图（深度参考），两者职责互补。


## 11. 模块蓝图索引

| 蓝图文档 | 路径 | 模块ID | 版本 | 状态 | 职责概要 |
|----------|------|--------|------|------|----------|
| [Layer 11架构蓝图](../module_designs/layer_11/LAYER_11_ARCHITECTURE.md) | `docs/module_designs/layer_11/LAYER_11_ARCHITECTURE.md` | LAYER_11_ARCH_001 | 1.0 | Active | 文字驱动层整体架构、技术选型、实施方案、成本评估 |
| [文字驱动核心模块](../module_designs/layer_11/L11_TEXT_DRIVER.md) | `docs/module_designs/layer_11/L11_TEXT_DRIVER.md` | L11_TEXT_DRIVER_001 | 1.0 | Active | 自然语言理解、意图识别、参数提取、工具调度 |
| [量化交易Agent模块](../module_designs/layer_11/L11_QUANT_AGENT.md) | `docs/module_designs/layer_11/L11_QUANT_AGENT.md` | L11_QUANT_AGENT_001 | 1.0 | Active | Agent框架、模型管理、工具集成、记忆管理、安全机制 |
| [Layer 11工具封装蓝图](../module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_ENCAPSULATION_BLUEPRINT.md` | LAYER_11_TOOL_ENCAP_001 | 1.0 | Active | 工具封装架构、单一AI层设计、纯执行层分离、性能优化 |
| [Layer 11工具接口规范](../module_designs/layer_11/LAYER_11_TOOL_INTERFACE_SPECIFICATION.md) | `docs/module_designs/layer_11/LAYER_11_TOOL_INTERFACE_SPECIFICATION.md` | LAYER_11_TOOL_SPEC_001 | 1.0 | Active | 所有模块工具接口详细定义、操作规范、参数定义、返回值规范 |
| [因子库蓝图](FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md) | `docs/02_FACTOR_LIBRARY/FACTOR_BACKTEST_INTEGRATION_BLUEPRINT.md` | FACTOR_BACKTEST_001 | 1.0 | Active | 因子计算、存储、IC分析、Backtrader回测集成 |
| [模拟交易蓝图](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) | `docs/04_EXECUTION/06_SIMULATION/BLUEPRINT.md` | SIMULATION_001 | 1.0 | Active | 模拟撮合引擎、模拟账户管理、交易执行 |
| [策略引擎蓝图](../03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_BLUEPRINT.md) | `docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/STRATEGY_ENGINE_BLUEPRINT.md` | STRAT_ENGINE_001 | 1.0 | Active | 策略引擎开发、开源模块集成 |
| [专业多时间框架架构](../01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) | `docs/01_FRAMEWORK/PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md` | FRAMEWORK_PROF_ARCH_001 | 1.0 | Active | 三级时间框架融合架构、桥水+文艺复兴模式融合 |
| [专业实施蓝图](../01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) | `docs/01_FRAMEWORK/PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md` | FRAMEWORK_IMPL_BLUEPRINT_001 | 1.0 | Active | 6个月实施路线图、开源集成策略、风险管理 |
| [直播金融分析蓝图](../04_EXECUTION/07_LIVE_STREAM/LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md) | `docs/04_EXECUTION/07_LIVE_STREAM/LIVE_STREAM_FINANCIAL_ANALYSIS_BLUEPRINT.md` | LIVE_STREAM_FINANCIAL_ANALYSIS_001 | 1.0 | Active | 多主播直播监控、MP3录制、AI内容分析、观点聚合、因子生成 |
| [AI工作记录与优化模块蓝图](../10_AI_WORKFLOW/AI_WORKFLOW_LOGGER_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/AI_WORKFLOW_LOGGER_BLUEPRINT.md` | AI_WORKFLOW_LOGGER_001 | 1.0 | Active | AI会话记录、决策记录、效果评估、优化迭代、知识库构建 |
| [AI工作汇报与交付模块蓝图](../10_AI_WORKFLOW/AI_WORK_REPORTER_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/AI_WORK_REPORTER_BLUEPRINT.md` | AI_WORK_REPORTER_001 | 1.0 | Active | 每日工作总结、进度通知、决策汇报、交互交付、可视化展示 |
| [复盘模块蓝图](../10_AI_WORKFLOW/POST_TRADE_REVIEW_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/POST_TRADE_REVIEW_BLUEPRINT.md` | POST_TRADE_REVIEW_001 | 1.0 | Active | 回测复盘、实盘复盘、因子复盘、策略复盘、风险复盘 |
| [全流程数据保存机制蓝图](../10_AI_WORKFLOW/FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md` | FULL_PROCESS_DATA_PERSISTENCE_001 | 1.0 | Active | 实验追踪、数据血缘、版本控制、数据治理 |
| [开源项目集成方案蓝图](../10_AI_WORKFLOW/OPEN_SOURCE_INTEGRATION_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/OPEN_SOURCE_INTEGRATION_BLUEPRINT.md` | OPEN_SOURCE_INTEGRATION_001 | 1.0 | Active | MLflow集成、Qlib集成、架构参考、工具集成 |
| [合规监控模块蓝图](../10_AI_WORKFLOW/COMPLIANCE_MONITORING_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/COMPLIANCE_MONITORING_BLUEPRINT.md` | COMPLIANCE_MONITORING_001 | 1.0 | Active | 交易合规检查、风控合规检查、监管报告生成、审计追踪、违规预警 |
| [实盘监控模块蓝图](../10_AI_WORKFLOW/LIVE_TRADING_MONITOR_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/LIVE_TRADING_MONITOR_BLUEPRINT.md` | LIVE_TRADING_MONITOR_001 | 1.0 | Active | 实时交易监控、持仓风险监控、异常交易预警、性能指标监控、多渠道告警 |
| [性能分析模块蓝图](../10_AI_WORKFLOW/PERFORMANCE_ANALYSIS_BLUEPRINT.md) | `docs/10_AI_WORKFLOW/PERFORMANCE_ANALYSIS_BLUEPRINT.md` | PERFORMANCE_ANALYSIS_001 | 1.0 | Active | 性能指标采集、性能瓶颈识别、性能报告生成、优化建议生成、性能趋势分析 |

> **索引状态**: 新增Layer 11文字驱动层蓝图（3个文档）和AI工作流模块蓝图（8个文档），已集成到系统文档体系中。包含完整的技术选型、实施方案和成本评估。

## 12. 次要文档索引

| 文档 | 路径 | 模块ID | 版本 | 状态 | 说明 |
|------|------|--------|------|------|------|
| [IC分析方法论](01_METHODOLOGY/ic_analysis.md) | `docs/02_FACTOR_LIBRARY/01_METHODOLOGY/ic_analysis.md` | METHODOLOGY_001 | 1.0 | Active | IC分析标准 |
| [因子预处理方法](01_METHODOLOGY/factor_preprocessing.md) | `docs/02_FACTOR_LIBRARY/01_METHODOLOGY/factor_preprocessing.md` | METHODOLOGY_002 | 1.0 | Active | 因子预处理标准 |
| [因子治理框架](../../README.md) | `docs/02_FACTOR_LIBRARY/00_GOVERNANCE/README.md` | GOVERNANCE_001 | 1.0 | Active | 因子库治理框架 |
| [路径标准](../05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md) | `docs/05_IMPLEMENTATION/02_DEVELOPMENT/PATH_STANDARD.md` | DEV_STD_001 | 1.0 | Stable | 路径引用标准 |
| [文档编号标准](../05_IMPLEMENTATION/02_DEVELOPMENT/DOCUMENT_NUMBERING_STANDARD.md) | `docs/05_IMPLEMENTATION/02_DEVELOPMENT/DOCUMENT_NUMBERING_STANDARD.md` | DEV_STD_005 | 1.0 | Stable | 文档编号体系标准 |
| [A股规则引擎设计](../design/a_stock_rules/T.08.AR001.a_stock_rule_engine_design.md) | `docs/design/a_stock_rules/T.08.AR001.a_stock_rule_engine_design.md` | DESIGN_001 | 1.0 | Active | A股规则引擎设计 |
| [交易成本模型算法](../design/trading_costs/T.05.TE001.trading_cost_model_algorithm_document.md) | `docs/design/trading_costs/T.05.TE001.trading_cost_model_algorithm_document.md` | DESIGN_002 | 1.0 | Active | 交易成本模型算法 |
| [多引擎数据一致性设计方案](../design/data_consistency/多引擎数据一致性设计方案.md) | `docs/design/data_consistency/多引擎数据一致性设计方案.md` | DESIGN_003 | 1.0 | Active | 多引擎数据一致性设计方案 |
| [Saga模式实现流程图](../design/data_consistency/Saga模式实现流程图.md) | `docs/design/data_consistency/Saga模式实现流程图.md` | DESIGN_004 | 1.0 | Active | Saga模式实现流程图 |
| [补偿事务设计文档](../design/data_consistency/补偿事务设计文档.md) | `docs/design/data_consistency/补偿事务设计文档.md` | DESIGN_005 | 1.0 | Active | 补偿事务设计文档 |
| [Web管理界面架构设计文档](../design/web_interface/T.06.UI001.web_management_interface_architecture_design.md) | `docs/design/web_interface/T.06.UI001.web_management_interface_architecture_design.md` | DESIGN_006 | 1.0 | Active | Web管理界面架构设计 |
| [前端组件结构图](../design/web_interface/前端组件结构图.md) | `docs/design/web_interface/前端组件结构图.md` | DESIGN_007 | 1.0 | Active | 前端组件结构图 |
| [API接口规范文档](../design/web_interface/API接口规范文档.md) | `docs/design/web_interface/API接口规范文档.md` | DESIGN_008 | 1.0 | Active | API接口规范文档 |
| [交易成本测试用例设计](../design/trading_costs/交易成本测试用例设计.md) | `docs/design/trading_costs/交易成本测试用例设计.md` | DESIGN_009 | 1.0 | Active | 交易成本测试用例设计 |
| [技术方案设计汇总报告](../design/技术方案设计汇总报告.md) | `docs/design/技术方案设计汇总报告.md` | DESIGN_SUMMARY_001 | 1.0 | Active | 技术方案设计汇总报告 |
| [专业审计指南](../09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md) | `docs/09_AUDIT/TEMPLATES/PROFESSIONAL_DOCUMENT_GOVERNANCE_AUDIT_GUIDE.md` | AUDIT_GUIDE_001 | 1.0 | Active | 专业审计指南 |
| [审计质量标准](../09_AUDIT/STANDARDS/AUDIT_STANDARDS.md) | `docs/09_AUDIT/STANDARDS/AUDIT_STANDARDS.md` | AUDIT_STD_001 | 1.0 | Stable | 审计质量标准v1.0 |
| [质量监控蓝图](../09_AUDIT/QUALITY_MONITORING_BLUEPRINT.md) | `docs/09_AUDIT/QUALITY_MONITORING_BLUEPRINT.md` | MONITORING_001 | 1.0 | Active | 质量监控体系蓝图 |
| [技术方案评审会议议程](../design/技术方案评审会议议程.md) | `docs/design/技术方案评审会议议程.md` | REVIEW_AGENDA_001 | 1.0 | Active | 技术方案评审会议议程 |
| [评审材料分发清单](../design/评审材料分发清单.md) | `docs/design/评审材料分发清单.md` | DISTRIBUTION_001 | 1.0 | Active | 评审材料分发指南 |
| [个人技术决策确认清单](../design/个人技术决策确认清单.md) | `docs/design/个人技术决策确认清单.md` | PERSONAL_DECISION_001 | 1.0 | Active | 个人项目决策流程 |
| [专业量化机构开发完整流程](../design/专业量化机构开发完整流程.md) | `docs/design/专业量化机构开发完整流程.md` | DEV_PROCESS_001 | 1.0 | Active | 专业量化机构开发流程指南 |
| [数据库设计文档](../design/database/P0-01_Database_Design_Document.md) | `docs/design/database/P0-01_Database_Design_Document.md` | DB_DESIGN_001 | 1.0 | Active | 专业量化机构数据库设计标准 |
| [数据库设计评审报告](../design/database/P0-01_Database_Design_Review_Report.md) | `docs/design/database/P0-01_Database_Design_Review_Report.md` | DB_REVIEW_001 | 1.0 | Active | 专业量化机构数据库设计评审 |


**版本**: v5.1.0 | **更新**: 2026-04-02 | **状态**: ✅ 活跃
