---
module_id: FRAMEWORK_ARCH_001
version: 5.1.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构文档
applicable_scope: 全系统
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 统一架构 (UNIFIED_ARCHITECTURE)

> **版本**: v5.1
> **创建日期**: 2026-03-30
> **Layer**: Layer 0-8
> **职责**: Layer 0-8技术架构定义
> **父文档**: [README.md](./README.md)

---

> **🔔 重要更新说明 (2026-04-02)**
> 
> 本文档描述的是**Layer 0-8技术流水线架构**，适用于系统技术实现层面。
> 
> **专业机构级架构已发布**，建议优先阅读以下文档：
> - **架构设计**：[PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md](./PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md) - 三级时间框架融合架构（桥水+文艺复兴模式）
> - **实施指导**：[PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md](./PROFESSIONAL_IMPLEMENTATION_BLUEPRINT.md) - 6个月实施路线图、开源集成策略
> 
> **架构选择建议**：
> - **技术实现**：继续使用本文档（Layer 0-8架构）
> - **业务决策**：使用专业多时间框架架构
> - **项目实施**：使用专业实施蓝图

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

**设计理由**: 
- **市场有效性**: 传统量化因子趋于同质化，舆情数据提供另类Alpha
- **事件驱动**: 重大新闻和事件对股价有短期显著影响
- **情感指标**: 市场情绪是重要的反指指标，可用于风险控制
- **数据可得性**: iFind/AkShare提供实时新闻接口，技术成熟

| 模块 | 功能 | 技术方案 |
|------|------|----------|
| NewsCrawler | 财联社/同花顺爬虫 | AkShare + iFind API |
| SentimentAnalyzer | 情感分析 | GLM-4.7-Flash |
| EventDetector | 事件分类/抽取 | Qwen3-4B |
| NewsStockMatcher | 新闻-股票匹配 | GLM-4.7-Flash |

### Layer 4: 机器学习层 🆕

**设计理由**:
- **因子挖掘**: 传统因子库有限，机器学习可发现非线性、高维Alpha
- **预测增强**: 时序模型(LSTM/Transformer)提供短期价格预测信号
- **特征工程**: 自动化特征工程减少人工干预，提高策略迭代速度
- **Qlib生态**: 复用Qlib成熟的AI量化框架，降低开发成本

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

**设计理由**:
- **AI安全**: 金融交易风险高，需要人类最终授权关键决策
- **可解释性**: 复杂的AI决策需要可视化解释，增强信任
- **实时监控**: 量化系统7×24运行，需要实时监控和告警
- **辩论机制**: 多头/空头辩论提供多角度分析，减少AI盲点
- **迭代反馈**: 人机交互提供反馈循环，持续优化AI性能

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
## 4. 跨层级数据流

### 4.1 核心数据流图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Layer 0-8 数据流总览                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 0: 数据源层                                                          │
│      │                                                                      │
│      ▼ 原始数据 (OHLCV、财务、新闻)                                          │
│  Layer 1: 数据预处理层                                                      │
│      │                                                                      │
│      ▼ 清洗后数据 (标准化、对齐、验证)                                        │
│  Layer 2: Alpha因子层                                                       │
│      │                                                                      │
│      ▼ 因子值 (5700+个因子)                                                  │
│  Layer 3: 舆情分析层 ←─────┐                                                │
│      │                    │                                                 │
│      ▼ 舆情信号           │ 新闻/情感数据                                     │
│  Layer 4: 机器学习层      │                                                 │
│      │                    │                                                 │
│      ▼ 预测信号/AI因子     │                                                 │
│  Layer 5: 策略执行层 ──────┘                                                 │
│      │                    ▲                                                 │
│      ▼ 交易信号           │ 风险检查结果                                      │
│  Layer 6: 组合优化层 ←─────┤                                                 │
│      │                    │ 持仓/风险约束                                     │
│      ▼ 优化后组合          │                                                 │
│  Layer 7: AI报告层        │                                                 │
│      │                    │ 绩效数据                                          │
│      ▼ 分析报告           │                                                 │
│  Layer 8: 人机交互层 ←─────┘                                                 │
│      │                    ▲                                                 │
│      ▼ 可视化/告警/授权    │ 人指令/反馈                                       │
│     人(决策者) ───────────┘                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 关键数据接口

| 数据流方向 | 数据类型 | 格式 | 频率 | 质量要求 |
|------------|----------|------|------|----------|
| **Layer 0 → Layer 1** | 原始市场数据 | OHLCV + 财务 + 新闻 | 实时/日频 | 完整性 > 95% |
| **Layer 1 → Layer 2** | 清洗后数据 | 标准化DataFrame | 日频 | 无缺失值 |
| **Layer 2 → Layer 5** | 因子矩阵 | 因子值矩阵 | 日频 | IC > 0.05 |
| **Layer 3 → Layer 5** | 舆情信号 | 情感评分 + 事件标签 | 实时 | 准确率 > 80% |
| **Layer 4 → Layer 2/5** | AI预测信号 | 预测概率 + 置信度 | 日频 | 回测Sharpe > 1.0 |
| **Layer 5 → Layer 6** | 策略信号 | 买卖信号 + 目标仓位 | 日频 | 通过风控检查 |
| **Layer 6 → Layer 5** | 优化后组合 | 权重向量 + 约束条件 | 日频 | 满足所有约束 |
| **Layer 5 → Layer 7** | 交易执行结果 | 订单 + 成交记录 | 实时 | 完整可审计 |
| **Layer 7 → Layer 8** | 绩效报告 | 归因分析 + 可视化 | 日/周/月 | 可解释性强 |
| **Layer 8 → 各层** | 人工指令 | 授权/否决/参数调整 | 按需 | 明确无歧义 |

### 4.3 数据流控制机制

1. **数据质量门控**
   - Layer 1: 数据完整性检查 (缺失率 < 5%)
   - Layer 2: 因子有效性检查 (IC显著 > 0)
   - Layer 5: 信号质量检查 (回测验证通过)
   - Layer 6: 组合可行性检查 (满足所有约束)

2. **异常处理流程**
   - 数据缺失: 自动填充或降级使用
   - 接口超时: 重试机制 + 备选数据源
   - 质量不达标: 告警 + 人工干预
   - 风控拒绝: 停止执行 + 记录原因

3. **数据版本管理**
   - 原始数据: 时间戳 + 数据源标识
   - 处理数据: 处理流水线版本号
   - 因子数据: 因子定义版本 + 计算参数
   - 信号数据: 策略版本 + 市场状态

---
## 5. 相关文档

| 文档 | 说明 |
|------|------|
| [MARKET_REGIME.md](./MARKET_REGIME.md) | 市场状态识别 |
| [HUMAN_AI_FLOW.md](./HUMAN_AI_FLOW.md) | 人机协作流程 |
| [TECH_STACK.md](./TECH_STACK.md) | 技术栈选择 |
| [README.md](./README.md) | 框架总览 |
| **[AI_EXPLAINABILITY_TOOLKIT_BLUEPRINT.md](./AI_EXPLAINABILITY_TOOLKIT_BLUEPRINT.md)** | **🆕 P0级: AI可解释性工具蓝图** |
| **[RAG_KNOWLEDGE_SYSTEM_BLUEPRINT.md](./RAG_KNOWLEDGE_SYSTEM_BLUEPRINT.md)** | **🆕 P0级: RAG知识系统蓝图** |
| **[ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md](./ADAPTIVE_MODEL_SYSTEM_BLUEPRINT.md)** | **🆕 P0级: 统一自适应模型蓝图** |
| **[IMPLEMENTATION_ACCELERATION_BLUEPRINT.md](./IMPLEMENTATION_ACCELERATION_BLUEPRINT.md)** | **🆕 P0级: 实施加速方案蓝图** |

---

**版本**: v2.2 | **更新**: 2026-04-03 | **状态**: ✅ 活跃
