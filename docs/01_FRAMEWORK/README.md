# 框架定义 (Framework)

> **版本**: v2.0
> **更新日期**: 2026-03-30
> **Layer**: Layer 0 (基础)
> **职责**: 系统架构、市场状态识别、人机协作流程、技术栈选择

---

## 一、文档概览

| 文档 | 职责 | 说明 |
|------|------|------|
| **ARCHITECTURE.md** | Layer 0-8统一架构 | 分层架构、模块映射、技术选型 |
| **MARKET_REGIME.md** | 市场状态识别 | 大盘择时、状态分类、策略映射 |
| **HUMAN_AI_FLOW.md** | 人机协作流程 | 授权机制、AI角色定义、决策流程 |
| **TECH_STACK.md** | 技术栈选择 | 数据源/回测/可视化/AI/存储选型 |

---

## 二、核心概念

### 2.1 Layer 0-8 架构

```
Layer 0: 数据源层 (QMT/iFind/SuperCommand)
Layer 1: 数据预处理层 (清洗/标准化/验证)
Layer 2: Alpha因子层 (5700+因子)
Layer 3: 舆情分析层 (新闻/情感/事件) 🆕
Layer 4: 机器学习层 (Qlib Alpha158/LSTM) 🆕
Layer 5: 策略执行层 (信号生成/QMT交易)
Layer 6: 组合优化层 (均值方差/Barra)
Layer 7: AI报告层 (日报/月报/归因) 🆕
Layer 8: 人机交互层 (授权/监控/辩论) 🆕
```

### 2.2 核心设计原则

| 原则 | 说明 |
|------|------|
| **大盘择时优先** | 所有策略的第一步，判断市场状态 |
| **人授权AI执行** | 人做决策，AI执行 |
| **可回测优先** | 稳定策略才实盘 |
| **AI辅助不替代** | AI提供建议，人最终决策 |

---

## 三、快速导航

### 3.1 按任务导航

| 任务 | 文档 |
|------|------|
| 理解系统架构 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| 了解大盘择时 | [MARKET_REGIME.md](./MARKET_REGIME.md) |
| 理解人机协作 | [HUMAN_AI_FLOW.md](./HUMAN_AI_FLOW.md) |
| 查看技术选型 | [TECH_STACK.md](./TECH_STACK.md) |

### 3.2 按Layer导航

| Layer | 文档 |
|-------|------|
| Layer 0 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 1 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 2 | [因子库文档](../02_FACTOR_LIBRARY/README.md) |
| Layer 3 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 4 | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Layer 5 | [执行文档](../04_EXECUTION/README.md) |
| Layer 6 | [组合优化文档](../04_EXECUTION/README.md) |
| Layer 7 | [绩效文档](../05_BACKTEST/README.md) |
| Layer 8 | [HUMAN_AI_FLOW.md](./HUMAN_AI_FLOW.md) |

---

## 四、与其他模块的关系

```
01_FRAMEWORK (本目录)
├── ARCHITECTURE.md     ←→ 02_FACTOR_LIBRARY (因子层)
├── MARKET_REGIME.md    ←→ 03_TRADING_TACTICS (策略)
├── HUMAN_AI_FLOW.md   ←→ 04_EXECUTION (执行)
└── TECH_STACK.md      ←→ 05_IMPLEMENTATION (部署)

层级关系:
├── Layer 0-2: 数据和因子 → 02_FACTOR_LIBRARY
├── Layer 3-4: AI能力 → 07_RESEARCH
├── Layer 5-6: 交易执行 → 04_EXECUTION
└── Layer 7-8: 人机交互 → 08_USER_EXPERIENCE
```

---

## 五、更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-03-30 | 方案C重组，新增4个独立文档 |
| v1.0 | 2026-03-29 | 初始版本 |

---

**状态**: ✅ 活跃
