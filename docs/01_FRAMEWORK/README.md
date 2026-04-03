---
module_id: FRAMEWORK_README_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构文档
applicable_scope: 全系�?
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---

# 框架定义 (Framework)

> **版本**: v5.1
> **更新日期**: 2026-03-30
> **技术架�?*: Layer 0-8技术流水线
> **业务架构**: 三级时间框架融合架构
> **职责**: 系统架构、市场状态识别、人机协作流程、技术栈选择

---

## 一、文档概�?

| 文档 | 职责 | 说明 |
|------|------|------|
| **ARCHITECTURE.md** | Layer 0-8统一架构 | 分层架构、模块映射、技术选型 |
| **MARKET_REGIME.md** | 市场状态识�?| 大盘择时、状态分类、策略映�?|
| **HUMAN_AI_FLOW.md** | 人机协作流程 | 授权机制、AI角色定义、决策流�?|
| **TECH_STACK.md** | 技术栈选择 | 数据�?回测/可视�?AI/存储选型 |
| **PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md** | 专业多时间框架架�?| 三级时间框架融合架构（桥�?文艺复兴模式�?|
| **PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md** | 专业实施蓝图 | 10个月实施路线图、AI评审团机制�?个关键审核节�?|
| **DATA_LAYER_IMPLEMENTATION_BLUEPRINT.md** | 数据源层专业实施蓝图 | P0/P1/P2三级模块设计�?个月实施计划、专业机构对�?|
| **PERSONAL_DEVELOPMENT_BLUEPRINT.md** | 个人开发友好实施方�?| 6个适合个人开发的模块�?周实施计划、低成本轻量级方�?|
| **CRITICAL_MODULES_IMPLEMENTATION_BLUEPRINT.md** | 关键模块实施蓝图 | P0实时风控+P1全球市场+P2扩展模块�?-6周实施、覆盖度提升�?5% |
| **AI_STRATEGY_AUTOMATION_BLUEPRINT.md** | AI策略自动化集成蓝�?| 15个AI开源项目、五阶段实施、AI评审团、QMT集成 |
| **NATURAL_LANGUAGE_INTERFACE_BLUEPRINT.md** | Layer 11文字驱动层架�?| 自然语言交互层、Open WebUI + LangChain + VNPY、零代码操作 |

---

## 二、核心概�?

### 2.1 Layer 0-8 架构

```
Layer 0: 数据源层 (QMT/iFind/SuperCommand)
Layer 1: 数据预处理层 (清洗/标准�?验证)
Layer 2: Alpha因子�?(5700+因子)
Layer 3: 舆情分析�?(新闻/情感/事件) 🆕
Layer 4: 机器学习�?(Qlib Alpha158/LSTM) 🆕
Layer 5: 策略执行�?(信号生成/QMT交易)
Layer 6: 组合优化�?(均值方�?Barra)
Layer 7: AI报告�?(日报/月报/归因) 🆕
Layer 8: 人机交互�?(授权/监控/辩论) 🆕
Layer 11: 文字驱动�?(自然语言交互/零代码操�? 🆕
```

**注意**: Layer 11是文字驱动层，位于Layer 0-8之上，提供自然语言交互界面，实现零代码操作整个系统。详细设计参�?[NATURAL_LANGUAGE_INTERFACE_BLUEPRINT.md](./NATURAL_LANGUAGE_INTERFACE_BLUEPRINT.md)

### 2.2 核心设计原则

| 原则 | 说明 |
|------|------|
| **大盘择时优先** | 所有策略的第一步，判断市场状�?|
| **人授权AI执行** | 人做决策，AI执行 |
| **可回测优�?* | 稳定策略才实�?|
| **AI辅助不替�?* | AI提供建议，人最终决�?|

---

## 三、快速导�?

### 3.1 按任务导�?

| 任务 | 文档 |
|------|------|
| 理解系统架构 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| 了解大盘择时 | [MARKET_REGIME.md](./MARKET_REGIME.md) |
| 理解人机协作 | [HUMAN_AI_FLOW.md](./HUMAN_AI_FLOW.md) |
| 查看技术选型 | [TECH_STACK.md](./TECH_STACK.md) |
| 零代码操作系�?| [NATURAL_LANGUAGE_INTERFACE_BLUEPRINT.md](./NATURAL_LANGUAGE_INTERFACE_BLUEPRINT.md) |

### 3.2 按Layer导航

| Layer | 文档 |
|-------|------|
| Layer 0 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 1 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 2 | [因子库文档](../02_FACTOR_LIBRARY/README.md) |
| Layer 3 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 4 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 5 | [执行文档](../04_EXECUTION/README.md) |
| Layer 6 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 7 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 8 | [HUMAN_AI_FLOW.md](./HUMAN_AI_FLOW.md) |
| Layer 11 | [NATURAL_LANGUAGE_INTERFACE_BLUEPRINT.md](./NATURAL_LANGUAGE_INTERFACE_BLUEPRINT.md) |

---

## 四、与其他模块的关�?

```
01_FRAMEWORK (本目�?
├── ARCHITECTURE.md     ←→ 02_FACTOR_LIBRARY (因子�?
├── MARKET_REGIME.md    ←→ 03_TRADING_TACTICS (策略)
├── HUMAN_AI_FLOW.md   ←→ 04_EXECUTION (执行)
└── TECH_STACK.md      ←→ 05_IMPLEMENTATION (部署)

层级关系:
├── Layer 0-2: 数据和因�?�?02_FACTOR_LIBRARY
├── Layer 3-4: AI能力 �?07_RESEARCH
├── Layer 5-6: 交易执行 �?04_EXECUTION
└── Layer 7-8: 人机交互 �?08_USER_EXPERIENCE
```

---

## 五、更新记�?

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-03-30 | 方案C重组，新�?个独立文�?|
| v1.0 | 2026-03-29 | 初始版本 |

---

**状�?*: �?活跃
