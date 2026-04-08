---
module_id: ARCHIVE_BP_MANIFEST_001
version: 5.0.1
status: Active
created_date: 2026-04-01
last_updated: '2026-04-07'
owner: 首席文档架构?
standard_type: 专业量化机构蓝图
applicable_scope: 全系统架构设?
compliance_level: 架构标准
parent_document: ../INDEX.md
implementation_status: 进行?
responsibility:
- 归档文档、历史版本
# System_Manifest.md - 系统清单
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 清风量化系统 v5.0 的完整系统状态快?


## 📌 文档定位

| 属?| 说明 |
|
|
---
| **职责** | 系统清单、模块映射、目录结?|
| **定位** | ?**主入口文?* - 快速了解系统的导航?|
| **阅读时间** | 15分钟 |
| **与其他文档关?* | 本文档是入口，详细技术细节见 `UNIFIED_ARCHITECTURE.md`，愿景目标见 `ULTIMATE_BLUEPRINT.md` |


## 开发阶段说?

| 阶段 | 目标 | 文档状?| 代码状?|
|------|------|----------|----------|
| **当前：研?策略设计** | 验证策略想法，建立方法论 | 完善?| 框架+示例代码 |
| **下一步：回测验证** | 用历史数据验证策?| - | 可执行代?|
| **未来：模拟交?* | 真实环境验证 | - | 生产级代?|
| **未来：实盘交?* | 实际资金验证 | - | 交易级代?|

> **重要说明**：当前所有代码均?*示例代码/框架代码**，用于说明逻辑?*不可直接运行**?


## 1. 物理架构 (v5.0)

```
D:\ZephyrAlpha\
├── docs/                              # 文档中心
?  ├── INDEX.md                       # 快速导航入?
?  ├── System_Manifest.md             # 本文?
?  ├── API_Contract.md               # 接口契约
?  ├── AI_Research_Framework.md       # AI研究框架
?  ?
?  ├── 00_OVERVIEW/                  # 系统总览
?  ?  ├── README.md
?  ?  ├── DATA_FLOW.md
?  ?  └── VERSION_HISTORY.md
?  ?
?  ├── 01_FRAMEWORK/                  # 框架定义 (Layer 0-7)
?  ?  └── README.md
?  ?
?  ├── 02_FACTOR_LIBRARY/            # 因子?(128+因子)
?  ?  ├── 00_GOVERNANCE/           # 治理框架
?  ?  ├── 00_INDEX/                 # 索引导航
?  ?  ├── 01_STANDARDS/           # 研究方法?
?  ?  ├── 02_ALPHA_FACTORS/         # Alpha因子 (87?
?  ?  ├── 03_RISK_FACTORS/          # 风险因子 (46?
?  ?  ├── 04_DATA_SOURCE/           # 数据?
?  ?  ├── 05_BACKTEST/              # 回测报告
?  ?  ├── 06_REGISTRY/       # 因子注册
?  ?  └── 07_MONITORING/            # 监控中心
?  ?
?  ├── 03_TRADING_TACTICS/           # 交易策略?(S001-S120)
?  ?  ├── 01_STRATEGY_FRAMEWORK/    # 策略框架
?  ?  ├── 03_ADVANCED_TACTICS/      # 高级战术
?  ?  ├── 04_YOUZI_STRATEGIES/      # 游资策略
?  ?  └── 05_STRATEGY_POOL/         # 策略池索?
?  ?
?  ├── 04_EXECUTION/                 # 执行引擎
?  ?  ├── 01_EVENT_ENGINE/          # 事件引擎
?  ?  ├── 02_TRADE_EXECUTOR/        # 交易执行
?  ?  ├── 03_MONITORING/            # 监控
?  ?  ├── 04_AI_COMMITTEE/          # AI委员?
?  ?  └── 05_RISK_ENGINE/           # 风险引擎
?  ?
?  ├── 05_IMPLEMENTATION/            # 实施指南
?  ?  ├── 01_QUICKSTART/            # 快速开?
?  ?  ├── 02_DEVELOPMENT/           # 开发规?
?  ?  ├── 03_DEPLOYMENT/            # 部署指南
?  ?  └── 07_OPERATIONS/            # 运维手册
?  ?
?  ├── 06_ARCHIVE/                   # 归档
?  ?  ├── main/                     # 主文档历?
?  ?  ├── factor-library/            # 因子库历?
?  ?  └── over_engineered/          # 过度工程化文?
?  ?
?  └── 07_RESEARCH/                  # AI研究
?      ├── 01_ENVIRONMENT/           # 研究环境
?      ├── 02_EXPLORATORY_ANALYSIS/  # 探索性分?
?      ├── 03_PATTERN_RECOGNITION/   # 模式识别
?      └── 04_EXPERIMENT_TRACKING/   # 实验追踪
?
├── ZephyrAlpha/                     # 代码项目
?  ├── config/                        # 配置文件
?  ?  ├── system.yaml
?  ?  ├── data_sources.yaml
?  ?  ├── factors/
?  ?  └── risk/
?  ├── src/                          # 源代?
?  ?  ├── main.py
?  ?  ├── core/                     # 核心基类
?  ?  ?  └── base.py              # Result, Signal, Order, Position
?  ?  ├── modules/                  # 功能模块
?  ?  ?  ├── alert_manager.py
?  ?  ?  ├── factor_calculator.py  # ?已实?
?  ?  ?  └── risk_manager.py       # ?已实?
?  ?  └── ai/                       # AI自主量化模块 (新增)
?  ?      ├── market_regime.py     # A01 市场状态识?
?  ?      ├── strategy_router.py   # A02 策略路由?
?  ?      ├── dynamic_risk.py      # A03 动态风?
?  ?      ├── strategy_optimizer.py # A04 策略优化?
?  ?      ├── feedback_loop.py      # A05 反馈学习闭环
?  ?      └── approval_ui.py       # A06 授权确认界面
?  ├── data/                         # 数据存储 (gitignored)
?  ├── logs/                         # 日志文件 (gitignored)
?  ├── tests/                        # 测试代码
?  ├── notebooks/                    # Jupyter分析 (gitignored)
?  ├── docs/                         # 项目级快速参?
?  ├── requirements.txt
?  ├── pyproject.toml
?  ├── .env.example
?  └── .gitignore
?
├── archive/                           # 历史文件归档 (待整?
?  └── (旧文件将逐步归档)
?
└── README.md                          # 项目总入?
```


## 2. 模块映射?(实现状?

| 模块 | 路径 | 功能 | 状?|
|------|------|------|------|
| **核心基类** | | | |
| base | `src/core/base.py` | Result, Signal, Order, Position | ?已实?|
| exceptions | `src/core/exceptions.py` | 异常类定?| ?已实?|
| **功能模块** | | | |
| factor_calculator | `src/modules/factor_calculator.py` | 因子计算 (87个Alpha因子) | ?已实?|
| risk_manager | `src/modules/risk_manager.py` | 风险管理 | ?已实?|
| alert_manager | `src/modules/alert_manager.py` | 告警管理 | ?已实?|
| **规划中模?* | | | |
| data_collector | `src/modules/data_collector.py` | 数据采集 | 🔄 规划?|
| data_cleaner | `src/modules/data_cleaner.py` | 数据清洗 | 🔄 规划?|
| data_storage | `src/modules/data_storage.py` | 数据存储 | 🔄 规划?|
| strategy_engine | `src/modules/strategy_engine.py` | 策略引擎 | 🔄 规划?|
| backtest_framework | `src/modules/backtest_framework.py` | 回测框架 | 🔄 规划?|
| trade_executor | `src/modules/trade_executor.py` | 交易执行 | 🔄 规划?|
| monitoring_system | `src/modules/monitoring_system.py` | 监控系统 | 🔄 规划?|
| config_manager | `src/modules/config_manager.py` | 配置管理 | 🔄 规划?|
| task_scheduler | `src/modules/task_scheduler.py` | 任务调度 | 🔄 规划?|
| logger | `src/modules/logger.py` | 日志系统 | 🔄 规划?|
| performance_monitor | `src/modules/performance_monitor.py` | 性能监控 | 🔄 规划?|

> **状态说?*: ?已实?= 可直接使?| 🔄 规划?= 已有规格，待开?| ?待开?= 尚未规划


## 3. 接口版本管理

| 接口 | 版本 | 最后更?| 说明 |
|------|------|----------|------|
| DataHub ?FactorCalculator | 1.0 | 2026-03-28 | OHLCV + 指标 |
| FactorCalculator ?StrategyEngine | 1.0 | 2026-03-28 | 因子?+ 时间?|
| StrategyEngine ?RiskManager | 1.0 | 2026-03-28 | 信号 + 头寸 |
| RiskManager ?TradeExecutor | 1.0 | 2026-03-28 | 订单 + 风控标志 |


## 4. 依赖矩阵

### Python环境
- **Python版本**: 3.10+
- **包管?*: pip / uv

### 核心依赖
| ?| 版本 | 用?|
|----|----|------|
| pandas | 2.2.0+ | 数据处理 |
| numpy | 1.26.0+ | 数值计?|
| scipy | 1.11.0+ | 科学计算 |
| scikit-learn | 1.3.0+ | 机器学习 |
| sqlalchemy | 2.0.0+ | 数据库ORM |
| pyyaml | 6.0+ | 配置管理 |
| loguru | 0.7.0+ | 日志系统 |
| apscheduler | 3.10.0+ | 任务调度 |

### 数据源依?
| ?| 版本 | 用?|
|----|----|------|
| akshare | 1.14.0+ | 实时行情 |
| baostock | 0.0.9+ | 历史数据 |
| tushare | 1.3.0+ | 财务数据 |


## 5. AI权限矩阵

### ?可写权限（AI可修改）

| 路径 | 说明 |
|------|------|
| `docs/02_FACTOR_LIBRARY/02_ALPHA_FACTORS/` | Alpha因子定义 |
| `docs/02_FACTOR_LIBRARY/05_BACKTEST/` | 回测报告 |
| `docs/03_TRADING_TACTICS/` | 策略文档 |
| `ZephyrAlpha/src/modules/` | 模块实现代码 |
| `ZephyrAlpha/tests/` | 测试代码 |
| `ZephyrAlpha/notebooks/` | Jupyter分析 |
| `docs/CHANGELOG.md` | 变更日志 |

### 🔒 只读权限（AI仅可读取?

| 路径 | 说明 |
|------|------|
| `docs/00_OVERVIEW/` | 系统总览 |
| `docs/01_FRAMEWORK/` | 核心框架 |
| `docs/02_FACTOR_LIBRARY/00_INDEX/` | 因子索引 |
| `docs/02_FACTOR_LIBRARY/01_STANDARDS/` | 研究方法?|
| `docs/04_EXECUTION/` | 执行引擎规格 |
| `ZephyrAlpha/config/` | 配置文件 |
| `ZephyrAlpha/src/core/` | 核心基础?|
| `System_Manifest.md` | 系统清单 |
| `API_Contract.md` | 接口契约 |
| `AI_Permissions.md` | 权限清单 |

### ?禁止权限（AI严禁修改?

| 路径 | 说明 |
|------|------|
| `.env` | API密钥 |
| `secrets/` | 私钥存放 |
| `ZephyrAlpha/.gitignore` | Git配置 |
| `ZephyrAlpha/pyproject.toml` | 项目配置 |


## 6. 配置文件关联

```
config/
├── system.yaml ──────────────?main.py
├── data_sources.yaml ────────?data_collector
├── factors/
?  └── selected_factors.yaml ─?factor_calculator
└── risk/
    └── rules.yaml ──────────?risk_manager
```


## 7. 数据存储规格

| 存储?| 格式 | 位置 | 说明 |
|--------|------|------|------|
| 原始数据 | Parquet | `data/raw/{type}/{year}/` | 原始采集数据 |
| 处理后数?| Parquet + SQLite | `data/processed/` | 清洗后数?|
| 因子数据 | Parquet | `data/factors/{factor_id}/` | 按因子存?|
| 信号数据 | SQLite | `data/signals/` | 策略信号 |
| 订单数据 | SQLite | `data/orders/` | 交易订单 |
| 回测结果 | Parquet | `data/backtest_results/` | 回测绩效 |


## 8. 版本管理规则

### 主版本升级（v5.0 ?v6.0?
- 架构改变（Layer 0-7重组?
- 核心模块替换
- 数据格式不兼?

### 次版本升级（v5.0 ?v5.1?
- 新增模块
- 新增因子?
- 新增策略

### 补丁版本升级（v5.0 ?v5.0.1?
- Bug修复
- 文档更新
- 性能优化


## 9. 启动检查清?

AI启动前必读顺序：
1. ?读取本文件（System_Manifest.md?
2. ?读取 `docs/INDEX.md` - 快速导?
3. ?读取 `API_Contract.md`
4. ?读取 `AI_Permissions.md`
5. ?读取相关模块?`README.md`


## 10. 核心文档索引

| 文档 | 说明 | 优先?|
|------|------|--------|
| `INDEX.md` | 快速导航入?| ?必读 |
| System_Manifest.md | 系统清单 | ?必读 |
| `API_Contract.md` | 接口契约 | ?必读 |
|  | AI研究框架 | ?必读 |
| `Strategy_Spec_S001.md` | 策略模板 | 建议 |
| AI_Permissions.md | AI权限 | 必读 |


**版本**: v5.0.0 | **更新**: 2026-03-29 | **状?*: ?活跃
