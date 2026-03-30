# 统一架构 (UNIFIED_ARCHITECTURE)

> **版本**: v2.0
> **创建日期**: 2026-03-30
> **Layer**: Layer 0-8
> **职责**: Layer 0-8技术架构定义
> **父文档**: [README.md](./README.md)

---

## 1. 双重架构关系

本系统采用**双层架构**设计：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    终极蓝图架构 (Layer 0-8 + AI增强)                        │
│                                                                             │
│  Layer 8: 人机交互层 ──────→ 新增: 授权/监控/报告                          │
│  Layer 7: AI报告层 ────────→ 原Layer 7绩效层增强                           │
│  Layer 6: 组合优化层 ──────→ 原Layer 4组合层增强                           │
│  Layer 5: 策略执行层 ──────→ 原Layer 5执行层                               │
│  Layer 4: 机器学习层 ──────→ 新增: ML Pipeline                             │
│  Layer 3: 舆情分析层 ──────→ 新增: 新闻/情感/事件                          │
│  Layer 2: Alpha因子层 ─────→ 原Layer 2 Alpha层                             │
│  Layer 1: 数据预处理层 ────→ 原Layer 1前置层                               │
│  Layer 0: 数据源层 ────────→ 原Layer 0数据层                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 架构对应关系表

| 原7层架构 | 终极蓝图架构 | 变化说明 |
|-----------|-------------|----------|
| Layer 0: 数据层 | Layer 0: 数据源层 | 名称优化 + iFind/SuperCommand |
| Layer 1: 前置层 | Layer 1: 数据预处理层 | 名称优化 |
| Layer 2: Alpha层 | Layer 2: Alpha因子层 | 名称优化 + 5700+因子 |
| Layer 3: 风险层 | (融入各层) | 重构为风险模型 |
| Layer 4: 组合层 | Layer 6: 组合优化层 | 升级 + Barra+CVXPY |
| Layer 5: 执行层 | Layer 5: 策略执行层 | QMT API |
| Layer 6: 风控层 | (融入各层) | 重构为风控贯穿 |
| Layer 7: 绩效层 | Layer 7: AI报告层 | 升级为AI自动报告 |
| **无** | Layer 3: 舆情分析层 | 🆕 新增核心差异化 |
| **无** | Layer 4: 机器学习层 | 🆕 新增AI能力 |
| **无** | Layer 8: 人机交互层 | 🆕 新增授权/监控 |

---

## 2. 完整分层架构 (Layer 0-8)

```
Layer 0: 数据源层 (Data Sources)
    ↓
Layer 1: 数据预处理层 (Preprocessing)
    ↓
Layer 2: Alpha因子层 (Alpha Factors)
    ↓
Layer 3: 舆情分析层 (Sentiment & Events) 🆕
    ↓
Layer 4: 机器学习层 (Machine Learning) 🆕
    ↓
Layer 5: 策略执行层 (Strategy Execution)
    ↓
Layer 6: 组合优化层 (Portfolio Optimization)
    ↓
Layer 7: AI报告层 (AI Reporting)
    ↓
Layer 8: 人机交互层 (Human-AI Interface)
```

---

## 3. 详细分层架构

### Layer 0: 数据源层

| 模块 | 功能 | 数据源 |
|------|------|--------|
| QMT数据接口 | 行情/财务/交易 | QMT客户端 |
| iFind连接器 | 5700+因子/舆情 | iFind终端 |
| SuperCommand | 实时行情/选股 | 同花顺 |
| Baostock | 免费财务验证 | Baostock |

### Layer 1: 数据预处理层

| 模块 | 功能 |
|------|------|
| DataCleaner | 缺失值/异常值/复权 |
| DataNormalizer | 标准化/对齐 |
| DataValidator | 质量校验 |

### Layer 2: Alpha因子层

| 类别 | 数量 | 示例 |
|------|------|------|
| iFind因子 | 5700+ | 估值/财务/情绪 |
| 技术因子 | 100+ | MA/MACD/RSI |
| Qlib Alpha158 | 158 | AI验证因子 |

### Layer 3: 舆情分析层 🆕

| 模块 | 功能 | 技术方案 |
|------|------|----------|
| NewsCrawler | 财联社/同花顺爬虫 | AkShare + iFind API |
| SentimentAnalyzer | 情感分析 | GLM-4.7-Flash |
| EventDetector | 事件分类/抽取 | Qwen3-4B |
| NewsStockMatcher | 新闻-股票匹配 | GLM-4.7-Flash |

### Layer 4: 机器学习层 🆕

| 模块 | 功能 |
|------|------|
| FeatureEngineering | 自动特征工程 |
| LSTMModel | 股价预测 |
| TransformerModel | 时间序列 |
| QlibAlpha158 | AI因子库 |

### Layer 5: 策略执行层

| 模块 | 功能 |
|------|------|
| StrategyEngine | 策略运行 |
| SignalGenerator | 信号生成 |
| PositionManager | 仓位管理 |
| QMTExecutor | QMT交易执行 |
| TradeAuditor | AI下单前审核 |

### Layer 6: 组合优化层

| 模块 | 功能 |
|------|------|
| PortfolioOptimizer | 均值方差/风险平价 |
| BarraRiskModel | Barra风格因子 |
| ConstraintsSolver | 约束求解 |

### Layer 7: AI报告层

| 模块 | 功能 |
|------|------|
| PerformanceAnalyzer | 绩效归因 |
| DailyReporter | AI日报生成 |
| MonthlyReporter | AI月报生成 |
| MarketAnalyzer | 市场分析 |

### Layer 8: 人机交互层

| 模块 | 功能 |
|------|------|
| StreamlitDashboard | 可视化仪表板 |
| ApprovalUI | 授权确认界面 |
| GrafanaMonitor | 监控大屏 |
| WeChatAlert | 告警推送 |
| BullishDebater | 多头辩论 |
| BearishDebater | 空头辩论 |
| AIArbitrator | AI仲裁 |

---

## 4. 相关文档

| 文档 | 说明 |
|------|------|
| [MARKET_REGIME.md](./MARKET_REGIME.md) | 市场状态识别 |
| [HUMAN_AI_FLOW.md](./HUMAN_AI_FLOW.md) | 人机协作流程 |
| [TECH_STACK.md](./TECH_STACK.md) | 技术栈选择 |
| [README.md](./README.md) | 框架总览 |

---

**版本**: v2.0 | **更新**: 2026-03-30 | **状态**: ✅ 活跃
