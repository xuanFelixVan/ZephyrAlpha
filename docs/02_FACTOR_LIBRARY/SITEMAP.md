---
module_id: DOC_SITEMAP_001
version: 5.3.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-04
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: INDEX.md
implementation_status: 进行中
---


# 文档地图 (SITEMAP)

> 清风量化系统 v5.3 的完整文档导航地?
>
> **职责区分**:
> - [INDEX.md](../03_TRADING_TACTICS/INDEX.md) = 快速入口（5分钟导航?
> - **本文?* = 完整地图（深度参考）


## 📍 文档位置导航 (v5.3)

### 一级导?

```
docs/
├── 核心文档 (6?
?  ├── INDEX.md                   # 快速入?←──────────────?
?  ├── BLUEPRINT.md               # 蓝图总览                  ?
?  ├── API_Contract.md            # 接口契约                  ?
?  ├── AI_Permissions.md          # AI权限清单               ?
?  ├── BLUEPRINT_CHECKLIST.md     # 蓝图检查清?             ?
?  └── CHANGELOG.md               # 变更日志                   ?
?                                                           ?
├── 00_OVERVIEW/                   # 系统总览                  ?
├── 01_FRAMEWORK/                   # 框架定义 (Layer 0-11)    ?
├── 02_FACTOR_LIBRARY/            # 因子?(128+因子)         ?
├── 03_TRADING_TACTICS/           # 交易策略?                ?
├── 04_EXECUTION/                   # 执行引擎                  ?
├── 05_IMPLEMENTATION/            # 实施指南                  ?
├── 06_ARCHIVE/                    # 归档                     ?
├── 07_RESEARCH/                   # AI研究                   ?
└── 09_AUDIT/                      # 系统治理审计              ?
                                                            ?
←──────────────────────────── 快速入?/ 完整地图 ───────────?
```


## 🗺?按用途查?

### 我是新手

**快速上手路?* (30分钟):
1. 阅读 [INDEX.md](../03_TRADING_TACTICS/INDEX.md) - 快速入?(5分钟)
2. 阅读 [00_OVERVIEW/README.md](../../README.md) - 系统总览 (10分钟)
3. 阅读 [05_IMPLEMENTATION/01_QUICKSTART/README.md](../../README.md) - 快速开?(15分钟)


### 我要理解架构

**架构学习路线** (2小时):
1. 阅读 [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 系统蓝图 (30分钟)
2. 阅读 [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) - Layer 0-11统一架构 (30分钟)
3. 阅读 [01_FRAMEWORK/README.md](../../README.md) - 框架文档索引 (20分钟)
4. 阅读 [AI_Permissions.md](../01_FRAMEWORK/AI_PERMISSIONS.md) - AI权限清单 (20分钟)


### 我要开发策?

**策略开发路?* (4小时):
1. 阅读 [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 系统蓝图 (30分钟)
2. 阅读 [Strategy_Spec_S001.md](../03_TRADING_TACTICS/Strategy_Spec_S001.md) - 策略模板 (30分钟)
3. 阅读 [03_TRADING_TACTICS/INDEX.md](../03_TRADING_TACTICS/INDEX.md) - 策略索引 (20分钟)
4. 阅读 [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](02_ALPHA_FACTORS_INDEX.md) - 因子?(30分钟)
5. 阅读  - 开发规?(1小时)
6. 实践编写策略代码 (1.5小时)


### 我要部署系统

**部署路线** (3小时):
1. 阅读 [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 系统蓝图 (30分钟)
2. 阅读 [05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md](../05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md) - 部署方案 (30分钟)
3. 执行部署脚本 (2小时)


### 我理解安?

**安全学习路线** (1.5小时):
1. 阅读 [AI_Permissions.md](../01_FRAMEWORK/AI_PERMISSIONS.md) - AI权限清单 (20分钟)
2. 阅读 [05_IMPLEMENTATION/02_DEVELOPMENT/SECURITY.md](../05_IMPLEMENTATION/02_DEVELOPMENT/SECURITY.md) - 安全规范 (25分钟)
3. 阅读 [05_IMPLEMENTATION/02_DEVELOPMENT/AUTH.md](../05_IMPLEMENTATION/02_DEVELOPMENT/AUTH.md) - 认证授权 (20分钟)


### 我遇到问?

**故障排查路线** (30分钟):
1. 查看 [FAQ.md](./FAQ.md) - 常见问题 (10分钟)
2. 查看 [05_IMPLEMENTATION/04_OPERATIONS/README.md](../../README.md) - 运维手册 (10分钟)
3. 查看 [CHANGELOG.md](../06_ARCHIVE/CHANGELOG.md) - 版本变更 (5分钟)
4. 查看系统日志 (5分钟)

### 我要审计系统

**审计工作路线** (1-2小时):
1. 访问 [09_AUDIT/INDEX_AUDIT.md](../09_AUDIT/INDEX_AUDIT.md) - 审计门户首页 (5分钟)
2. 选择审计模式: 个人模式(5分钟)或AI模式(30分钟)
3. 按审计标准执? [09_AUDIT/STANDARDS/AUDIT_STANDARDS.md](../09_AUDIT/STANDARDS/AUDIT_STANDARDS.md) - 审计标准 (15分钟)
4. 遵循工作流程: [09_AUDIT/PROCEDURES/PERSONAL_AUDIT_WORKFLOW.md](../09_AUDIT/PROCEDURES/PERSONAL_AUDIT_WORKFLOW.md) - 个人审计流程 (10分钟)
5. 生成审计报告 (30-60分钟)


## 📂 按目录查?(v5.3)

### 00_OVERVIEW/ - 系统总览

| 文件 | 说明 | 阅读时间 |
|------|------|----------|
| README.md | 系统简?| 10分钟 |
|  | 数据流与模块依赖 | 15分钟 |
| CHANGELOG.md | 版本历史（已合并?| 5分钟 |


### 01_FRAMEWORK/ - 框架定义

| 文件 | 说明 | 阅读时间 |
|------|------|----------|
| README.md | 框架文档索引 | 10分钟 |
| ARCHITECTURE.md | Layer 0-11统一架构 | 30分钟 |
| MARKET_REGIME.md | 市场状态识?| 20分钟 |
| HUMAN_AI_FLOW.md | 人机协作流程 | 15分钟 |
| TECH_STACK.md | 技术栈选择 | 15分钟 |


### 02_FACTOR_LIBRARY/ - 因子?

| 目录 | 说明 |
|------|------|
| 00_GOVERNANCE/ | 因子治理框架 |
| 00_INDEX/ | 因子分类导航 |
| 01_STANDARDS/ | 因子研究方法?|
| 02_ALPHA_FACTORS_INDEX.md | Alpha因子索引 |
| 03_RISK_FACTORS/ | 风险因子 |
| 04_DATA_SOURCE/ | 数据源说?|
| 05_BACKTEST/ | 回测报告 |
| 06_REGISTRY/ | 因子注册 |
| 07_FACTOR_MONITORING/ | 监控中心 |
| 10_MANUAL/ | 因子库手?|


### 03_TRADING_TACTICS/ - 策略?

| 文件/目录 | 说明 |
|------|------|
| INDEX.md | 策略导航 |
| README.md | 策略文档索引 |
| Strategy_Spec_S001.md | 策略模板 |
| 01_STRATEGY_FRAMEWORK/ | 策略框架 |
| 03_ADVANCED_TACTICS/ | 高级战术 |
| 04_YOUZI_STRATEGIES/ | 游资策略 |
| 05_STRATEGY_POOL/ | 策略池索?|
| 06_POSITION_MANAGEMENT/ | 仓位管理 |
| 07_ORDER_GENERATION/ | 订单生成 |
| 09_RISK_RULES/ | 风险规则 |


### 04_EXECUTION/ - 执行引擎

| 目录 | 说明 |
|------|------|
| 01_EVENT_ENGINE/ | 事件驱动引擎 |
| 01_ORDER_EXECUTION/ | 订单执行 |
| 02_TRADE_EXECUTOR/ | 交易执行 |
| 03_MONITORING/ | 实时监控 |
| 04_AI_COMMITTEE/ | AI委员?|
| 05_RISK_ENGINE/ | 风险引擎 |
| 06_SIMULATION/ | 仿真测试 |


### 05_IMPLEMENTATION/ - 实施指南

| 目录 | 说明 |
|------|------|
| 01_QUICKSTART/ | 快速开?|
| 02_DEVELOPMENT/ | 开发规?|
| 03_DEPLOYMENT/ | 部署指南 |
| 04_INFRASTRUCTURE/ | 基础设施 |
| 04_OPERATIONS/ | 运维手册 |
| 99_ARCHIVE/ | 归档 |


### 06_ARCHIVE/ - 归档

| 目录/文件 | 说明 |
|------|------|
| README.md | 归档说明（v5.3精简版） |
| main/BLUEPRINTS/ | 蓝图历史归档?个） |
| main/v4_development/ | v4.0开发文档（精简?个） |
| factor-library/ | 因子库历?|
| tactics_manual.md | v1.0战术手册 |
| technical_documentation.md | v1.0技术文?|


### 07_RESEARCH/ - AI研究

| 目录 | 说明 |
|------|------|
| 01_ENVIRONMENT/ | 研究环境 |
| 02_EXPLORATORY_ANALYSIS/ | 探索性分?|
| 03_PATTERN_RECOGNITION/ | 模式识别 |
| 04_EXPERIMENT_TRACKING/ | 实验追踪 |

### 09_AUDIT/ - 系统治理审计

| 目录/文件 | 说明 |
|------|------|
| README.md | 审计体系总览 |
| INDEX_AUDIT.md | 审计门户首页 |
| STANDARDS/ | 审计标准 |
| PROCEDURES/ | 审计程序 |


## 🔍 按关键词查找

### 架构相关

- [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 系统蓝图
- [01_FRAMEWORK/ARCHITECTURE.md](../01_FRAMEWORK/ARCHITECTURE.md) - Layer 0-11架构
- [01_FRAMEWORK/MARKET_REGIME.md](../01_FRAMEWORK/MARKET_REGIME.md) - 市场状态识?

### 模块相关

- [API_Contract.md](../03_TRADING_TACTICS/API_Contract.md) - 接口契约
- [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 模块蓝图
- [AI_Permissions.md](../01_FRAMEWORK/AI_PERMISSIONS.md) - AI权限

### 策略相关

- [Strategy_Spec_S001.md](../03_TRADING_TACTICS/Strategy_Spec_S001.md) - 策略模板
- [03_TRADING_TACTICS/INDEX.md](../03_TRADING_TACTICS/INDEX.md) - 策略索引
- [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](02_ALPHA_FACTORS_INDEX.md) - 因子?

### 因子相关

- [02_FACTOR_LIBRARY/02_ALPHA_FACTORS_INDEX.md](02_ALPHA_FACTORS_INDEX.md) - Alpha因子
-  - 风险因子
-  - 因子方法?
- [02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_MANAGEMENT_STANDARD.md](01_STANDARDS/FACTOR_MANAGEMENT_STANDARD.md) - 因子管理标准
- [02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_SCREENING_STRATEGY.md](01_STANDARDS/FACTOR_SCREENING_STRATEGY.md) - 因子筛选策?

### 部署相关

- [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - 系统蓝图
- [05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md](../05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md) - 部署方案

### 开发相?

-  - 开发规?
- [CHANGELOG.md](../06_ARCHIVE/CHANGELOG.md) - 变更日志

### AI研究相关

- [BLUEPRINT.md](04_DATA_SOURCE/02_SCHEDULER/BLUEPRINT.md) - AI研究框架（见附录?
- [EXPERIMENT_TRACKING.md](../07_RESEARCH/EXPERIMENT_TRACKING.md) - 实验追踪
- [KNOWLEDGE_MANAGEMENT.md](./KNOWLEDGE_MANAGEMENT.md) - 知识管理

### 运维相关

-  - 运维手册
- [FAQ.md](./FAQ.md) - 常见问题

### 审计相关

- [09_AUDIT/INDEX_AUDIT.md](../09_AUDIT/INDEX_AUDIT.md) - 审计门户首页
- [09_AUDIT/STANDARDS/AUDIT_STANDARDS.md](../09_AUDIT/STANDARDS/AUDIT_STANDARDS.md) - 审计标准
- [09_AUDIT/PROCEDURES/AI_AUDIT_GUIDELINES.md](../09_AUDIT/PROCEDURES/AI_AUDIT_GUIDELINES.md) - AI审计指南
- [09_AUDIT/PROCEDURES/PERSONAL_AUDIT_WORKFLOW.md](../09_AUDIT/PROCEDURES/PERSONAL_AUDIT_WORKFLOW.md) - 个人审计流程


## 📊 文档统计 (v5.3)

| 类型 | 数量 | 说明 |
|------|------|------|
| 核心文档 | 6?| 必读 |
| 索引文件 | 2?| 导航 |
| 一级目?| 8?| 分类 |
| **精简?* | **~80+文档** | 较v5.0减少?0?|


## 🎯 推荐阅读顺序

### ??(2小时)

1. INDEX.md (5分钟)
2. 00_OVERVIEW/README.md (10分钟)
3. BLUEPRINT.md (30分钟)
4. 01_FRAMEWORK/ARCHITECTURE.md (30分钟)
5. 05_IMPLEMENTATION/01_QUICKSTART/README.md (15分钟)

### ??(2小时)

1. AI_Permissions.md (20分钟)
2. API_Contract.md (15分钟)
3. Strategy_Spec_S001.md (30分钟)
4. 03_TRADING_TACTICS/INDEX.md (20分钟)
5. FAQ.md (15分钟)

### ??(2小时)

1. 02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_MANAGEMENT_STANDARD.md (30分钟)
2. 02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_SCREENING_STRATEGY.md (30分钟)
3. 05_IMPLEMENTATION/03_DEPLOYMENT/DEPLOYMENT_PLAN.md (30分钟)
4. CHANGELOG.md (15分钟)


## 🔗 文档关系?

```
INDEX.md (快速入?
    ?
    ├→ 00_OVERVIEW/ (系统总览)
    ?
    ├→ 01_FRAMEWORK/ (框架定义)
    ?  └→ ARCHITECTURE.md (Layer 0-11)
    ?
    ├→ BLUEPRINT.md (系统蓝图)
    ?
    ├→ 02_FACTOR_LIBRARY/ (因子?
    ?  ├→ 01_STANDARDS/ (方法?
    ?  ?  ├→ FACTOR_MANAGEMENT_STANDARD.md (因子管理标准)
    ?  ?  └→ FACTOR_SCREENING_STRATEGY.md (筛选策?
    ?  └→ 02_ALPHA_FACTORS_INDEX.md (因子索引)
    ?
    ├→ 03_TRADING_TACTICS/ (交易策略)
    ?  └→ Strategy_Spec_S001.md (策略模板)
    ?
    ├→ 04_EXECUTION/ (执行引擎)
    ?
    ├→ 05_IMPLEMENTATION/ (实施指南)
    ?  ├→ 01_QUICKSTART/
    ?  ├→ 02_DEVELOPMENT/
    ?  ├→ 03_DEPLOYMENT/
    ?  └→ 04_OPERATIONS/
    ?
    ├→ 06_ARCHIVE/ (归档)
    ?  └→ main/BLUEPRINTS/ (历史蓝图)
    ?
    ├→ 07_RESEARCH/ (AI研究)
    ?
    └→ 09_AUDIT/ (系统治理审计)
```


## 📱 移动端访?

所有文档均支持Markdown格式，可在以下平台查?
- GitHub (在线查看)
- GitLab (在线查看)
- 本地编辑?(VS Code、Sublime?
- Markdown阅读?(Typora、Obsidian?


**最后更?*: 2026-03-31
**维护?*: 清风量化系统
**版本**: v5.3

