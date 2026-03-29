# 清风量化系统5.0 阶段性开发路线图

> **文档版本**: v1.0
> **创建日期**: 2026-03-29
> **目标**: AI时代个人量化（1人+AI）
> **总时间投入**: 约5000小时（每天14小时 × 12-18个月）

---

## 一、阶段总览

| 阶段 | 名称 | 时间 | 核心目标 | 关键里程碑 |
|------|------|------|----------|------------|
| **Phase 0** | 准备阶段 | 2-4周 | 环境搭建 + QMT入门 | QMT回测成功跑通 |
| **Phase 1** | 基础架构 | 1-2月 | 数据-回测-风控基础 | iFind因子接入完成 |
| **Phase 2** | 回测完善 | 2-3月 | 专业级回测能力 | 多策略/参数优化 |
| **Phase 3** | ML集成 | 3-4月 | AI量化能力 | Qlib Alpha158上线 |
| **Phase 4** | 舆情系统 | 2-3月 | 新闻→信号流程 | 实时舆情监控 |
| **Phase 5** | AI自主量化 | 3-4月 | 人授权+AI执行 | 完整闭环运行 |
| **Phase 6** | 实盘优化 | 2-3月 | 稳定实盘运行 | 全自动化交易 |

**总时间**: 12-18个月

---

## 二、Phase 0: 准备阶段 (2-4周)

### 目标
- 搭建开发环境
- 掌握QMT Python API
- 理解iFind数据接口
- 跑通第一个回测示例

### 每日任务分配

#### 第1周: 环境搭建

| 日 | 任务 | 时长 | 产出 |
|----|------|------|------|
| Day 1 | 安装Python/conda环境 | 2h | Python 3.10+环境 |
| Day 1 | 安装PyCharm/VSCode | 1h | IDE配置完成 |
| Day 2 | 安装QMT客户端 | 2h | 国金QMT运行 |
| Day 2 | 学习QMT基本操作 | 2h | 界面熟悉 |
| Day 3 | QMT API文档阅读 | 4h | 理解Python API |
| Day 4 | 运行QMT示例策略 | 4h | 第一个策略运行 |
| Day 5 | iFind申请/安装 | 3h | iFind账号 |
| Day 5 | iFind API文档 | 3h | 接口了解 |
| Day 6-7 | 周末总结+规划 | 8h | Phase1计划 |

#### 第2周: QMT深入

| 日 | 任务 | 时长 | 产出 |
|----|------|------|------|
| Day 8 | QMT handlebar机制 | 4h | 理解回测驱动 |
| Day 9 | QMT get_market_data | 4h | 数据获取 |
| Day 10 | QMT passorder下单 | 4h | 交易函数 |
| Day 11 | QMT实盘模式 | 4h | 实盘机制理解 |
| Day 12 | 对比回测vs实盘 | 3h | 差异理解 |
| Day 13 | Backtrader入门 | 4h | 备选回测框架 |
| Day 14 | 总结QMT能力边界 | 2h | 明确限制 |

#### 第3周: iFind深入

| 日 | 任务 | 时长 | 产出 |
|----|------|------|------|
| Day 15 | iFind因子库概览 | 4h | 5700+因子分类 |
| Day 16 | iFind Python API | 4h | 数据获取 |
| Day 17 | THS_DP系列指标 | 3h | 数据产品 |
| Day 18 | THS_BD财务报表 | 3h | 财务数据 |
| Day 19 | iFind历史数据下载 | 4h | 本地数据 |
| Day 20 | SuperCommand入门 | 3h | 实时行情 |
| Day 21 | 数据对比验证 | 3h | 数据质量 |

#### 第4周: 架构设计

| 日 | 任务 | 时长 | 产出 |
|----|------|------|------|
| Day 22 | 系统架构设计 | 6h | 架构图 |
| Day 23 | 模块划分 | 4h | 模块清单 |
| Day 24 | 技术选型确认 | 3h | 技术栈文档 |
| Day 25 | 开发规范制定 | 3h | 代码规范 |
| Day 26 | 第一阶段计划 | 4h | Phase1详细计划 |
| Day 27-28 | 缓冲+调整 | 8h | 准备Phase1 |

### Phase 0 产出物

```
产出物清单:
├── QMT回测示例代码
├── iFind数据获取示例
├── 系统架构设计图
├── 模块划分文档
├── 技术选型文档
└── Phase1详细计划
```

---

## 三、Phase 1: 基础架构 (1-2个月)

### 目标
- QMT数据接口封装
- iFind因子库完整接入
- 基础回测框架
- 基础风控模块
- Streamlit仪表板v1

### 里程碑

```
M1.1: QMT数据接口封装完成
M1.2: iFind 5700+因子接入完成
M1.3: SuperCommand实时行情
M1.4: 基础回测引擎
M1.5: 基础风控模块
M1.6: Streamlit仪表板v1
```

### 详细任务

#### 1.1 QMT连接器 (第1-2周)

```python
# src/data/qmt_connector.py
class QMTConnector:
    """QMT数据接口封装"""

    def get_ohlcv(self, stock_code, start_date, end_date, period='1d'):
        """获取OHLCV数据"""
        pass

    def get_financial(self, stock_code, start_date, end_date):
        """获取财务数据"""
        pass

    def get_realtime(self, stock_codes):
        """获取实时行情"""
        pass

    def subscribe(self, stock_codes, callback):
        """订阅实时行情"""
        pass
```

#### 1.2 iFind连接器 (第2-4周)

```python
# src/data/ifind_connector.py
class IFindConnector:
    """iFind数据接口封装"""

    def get_indicator(self, stock_code, indicator_name, start_date, end_date):
        """获取单个指标"""
        pass

    def get_batch_indicators(self, stock_codes, indicator_names):
        """批量获取指标"""
        pass

    def get_financial_report(self, stock_code, report_type):
        """获取财务报表"""
        pass

    def download_history(self, stock_codes, indicators, start_date, end_date):
        """下载历史数据"""
        pass
```

#### 1.3 因子层 (第4-6周)

```
因子分类:
├── 技术因子 (100+)
│   ├── 趋势类: MA, EMA, MACD, DMI, ADX...
│   ├── 均线类: SMA, WMA, KAMA...
│   ├── 波动类: ATR, NATR, STD...
│   └── 成交量类: OBV, VOL, AMO...
│
├── 财务因子 (5000+)
│   ├── 估值类: PE, PB, PS, PCF...
│   ├── 盈利类: ROE, ROA, 毛利率...
│   ├── 成长类: 营收增速, 净利润增速...
│   └── 资产类: 资产负债率, 流动比率...
│
└── 情绪因子 (100+)
    ├── 资金流: 主力净流入, 超大单...
    ├── 分析师: 评级, 目标价...
    └── 技术情绪: RSI, KDJ,威廉...
```

#### 1.4 基础回测 (第6-8周)

```python
# src/backtest/engine.py
class BacktestEngine:
    """回测引擎"""

    def run(self, strategy, start_date, end_date, initial_capital):
        """运行回测"""
        pass

    def add_position(self, stock, quantity, price):
        """持仓管理"""
        pass

    def calculate_metrics(self):
        """计算绩效指标"""
        pass
```

#### 1.5 风控模块 (第7-9周)

```python
# src/risk/risk_manager.py
class RiskManager:
    """风控管理"""

    def check_order(self, order):
        """下单前风控检查"""
        pass

    def check_position(self, position):
        """持仓风控检查"""
        pass

    def check_daily_loss(self, daily_pnl):
        """每日亏损检查"""
        pass
```

#### 1.6 Streamlit仪表板 (第8-10周)

```
仪表板页面:
├── 首页: 系统概览
├── 数据: 行情展示
├── 因子: 因子计算
├── 回测: 策略回测
├── 风控: 风控状态
└── 设置: 配置管理
```

---

## 四、Phase 2: 回测完善 (2-3个月)

### 目标
- 多周期/多标的回测
- 组合回测能力
- 参数优化框架
- 绩效归因基础
- Walk-forward分析

### 里程碑

```
M2.1: 多周期回测 (1m/5m/1d/1w)
M2.2: 多标的组合回测
M2.3: 参数优化 (Optuna)
M2.4: 绩效归因基础
M2.5: Walk-forward分析
M2.6: 回测报告可视化
```

### 详细任务

#### 2.1 高级回测引擎

```python
# 高级功能
class AdvancedBacktestEngine(BacktestEngine):
    """高级回测引擎"""

    def run_multi_period(self, strategy, periods=['1m', '5m', '1d']):
        """多周期回测"""
        pass

    def run_multi_symbol(self, strategy, symbols):
        """多标的回测"""
        pass

    def run_portfolio(self, strategies, weights):
        """组合回测"""
        pass

    def walk_forward(self, strategy, train_window, test_window):
        """Walk-forward分析"""
        pass
```

#### 2.2 参数优化

```python
# src/backtest/optimizer.py
class ParameterOptimizer:
    """参数优化器"""

    def grid_search(self, strategy, param_grid):
        """网格搜索"""
        pass

    def random_search(self, strategy, param_dist):
        """随机搜索"""
        pass

    def bayesian_optimization(self, strategy, param_space):
        """贝叶斯优化 (Optuna)"""
        pass

    def genetic_algorithm(self, strategy):
        """遗传算法 (DEAP)"""
        pass
```

#### 2.3 绩效归因

```python
# src/portfolio/attribution.py
class PerformanceAttribution:
    """绩效归因"""

    def calculate_returns(self):
        """收益分解"""
        pass

    def factor_attribution(self):
        """因子归因"""
        pass

    def brinson_attribution(self):
        """Brinson归因"""
        pass

    def risk_attribution(self):
        """风险归因"""
        pass
```

---

## 五、Phase 3: 机器学习集成 (3-4个月)

### 目标
- Qlib Alpha158集成
- LSTM/Transformer预测模型
- 自动化特征工程
- 模型训练流水线
- 模型服务部署

### 这是核心差异化模块

```
┌─────────────────────────────────────────────────────────────────┐
│                     ML层 - 核心差异化                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Qlib Alpha158: 158个AI验证因子                                 │
│  ├── 收益类: return_5d, return_10d, return_20d...              │
│  ├── 波动类: std_5d, std_10d, bolling...                        │
│  ├── 资金类: volume_0, amount_0...                               │
│  └── 市场类: beta, mkt_cap, res_vol...                          │
│                                                                 │
│  预测模型:                                                       │
│  ├── LSTM: 股价/收益预测                                         │
│  ├── Transformer: 时间序列预测                                   │
│  └── 集成: 多模型融合                                           │
│                                                                 │
│  特征工程:                                                       │
│  ├── 自动特征: featuretools                                     │
│  ├── 特征选择: SHAP, 互信息                                      │
│  └── 特征监控: 特征有效性跟踪                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 里程碑

```
M3.1: Qlib环境搭建
M3.2: Alpha158因子计算
M3.3: LSTM预测模型
M3.4: Transformer预测
M3.5: 自动化特征工程
M3.6: 模型训练流水线
M3.7: 模型服务部署
```

### Qlib集成详细设计

```python
# src/ml/qlib集成.py
import qlib
from qlib.data import D
from qlib.data.dataset import DatasetH
from qlib.data.dataset.handler import Alpha158

class QlibAlpha158:
    """Qlib Alpha158因子集成"""

    def __init__(self):
        qlib.init(provider_uri=self.provider_uri)

    def get_alpha158(self, instruments, start_date, end_date):
        """获取Alpha158因子"""
        # Alpha158格式: [I_open, I_high, I_low, I_close, I_vwap, I_volume,
        #                 I_turnover, I_returns, I_label, vwap_adv, ...
        #                 pe_op, pb, ps, pc, capital_flow, ...
        #                 .., beta, mkt_cap, ..]
        pass

    def calculate_custom_alpha(self, instruments, factors):
        """计算自定义因子"""
        pass

    def backtest_alpha(self, alpha):
        """因子回测"""
        pass
```

---

## 六、Phase 4: 舆情分析系统 (2-3个月)

### 目标
- 新闻爬虫完整
- 情感分析上线
- 新闻-股票匹配
- 信号生成
- 实时监控

### 舆情系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     舆情分析系统                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  数据源:                                                        │
│  ├── 财联社快讯 (实时)                                          │
│  ├── 同花顺资讯 (实时)                                          │
│  ├── 东方财富 (补充)                                            │
│  └── 公司公告 (PDF解析)                                          │
│                                                                 │
│  AI分析:                                                        │
│  ├── DeepSeek API (主)                                         │
│  ├── Qwen3 (降级)                                              │
│  └── 规则引擎 (兜底)                                            │
│                                                                 │
│  分析维度:                                                       │
│  ├── 事件分类: 利好/利空/中性                                    │
│  ├── 实体识别: 股票/行业/概念                                    │
│  ├── 影响评估: 范围/强度/置信度                                  │
│  └── 事件类型: 政策/业绩/并购/业绩...                            │
│                                                                 │
│  信号输出:                                                       │
│  ├── 舆情因子: 情绪得分                                         │
│  ├── 事件信号: 事件驱动交易                                      │
│  └── 预警通知: WeChat/邮件                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 里程碑

```
M4.1: 财联社爬虫
M4.2: 同花顺爬虫
M4.3: DeepSeek情感分析
M4.4: 新闻-股票匹配
M4.5: 事件信号生成
M4.6: 舆情监控仪表板
M4.7: WeChat告警推送
```

---

## 七、Phase 5: AI自主量化 (3-4个月)

### 目标
- LangChain研究Agent
- 策略推荐系统
- 人授权界面
- AI执行闭环
- AI报告生成

### 人机协作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI自主量化闭环                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. AI研究 (Research Agent)                                     │
│     ├── 市场分析                                                │
│     ├── 因子挖掘                                                │
│     ├── 策略生成                                                │
│     └── 报告撰写                                                │
│                                                                 │
│  2. AI推荐 (Strategy Recommender)                               │
│     ├── 市场状态识别                                            │
│     ├── 策略选择                                                │
│     └── 仓位推荐                                                │
│                                                                 │
│  3. 人授权 (Human Approval)                                     │
│     ├── 信号展示                                                │
│     ├── 风险提示                                                │
│     └── 确认/拒绝                                               │
│                                                                 │
│  4. AI执行 (AI Execution)                                       │
│     ├── 订单执行                                                │
│     ├── 状态追踪                                                │
│     └── 异常处理                                                │
│                                                                 │
│  5. 反馈闭环 (Feedback Loop)                                     │
│     ├── 绩效记录                                                │
│     ├── 结果分析                                                │
│     └── 策略优化                                                │
│                                                                 │
│  6. AI报告 (AI Reporting)                                       │
│     ├── 日报生成                                                │
│     ├── 周报生成                                                │
│     └── 月报生成                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 里程碑

```
M5.1: LangChain研究Agent
M5.2: 策略推荐系统
M5.3: 授权确认UI
M5.4: AI执行引擎
M5.5: 反馈学习闭环
M5.6: AI日报生成
M5.7: AI周报/月报
M5.8: 异常自动处理
```

---

## 八、Phase 6: 实盘优化 (2-3个月)

### 目标
- 实盘无缝切换
- 全面监控告警
- Grafana大屏
- 应急预案

### 里程碑

```
M6.1: 实盘对接优化
M6.2: 订单智能路由
M6.3: 滑点分析
M6.4: Grafana监控大屏
M6.5: 全面监控告警
M6.6: 应急预案
M6.7: 操作文档完善
M6.8: 知识库建设
```

---

## 九、任务优先级矩阵

### 紧急/重要矩阵

```
                    重要
           ┌────────────┬────────────┐
           │   Phase1   │   Phase5   │
    紧急    │  基础架构  │  AI自主量化 │
           ├────────────┼────────────┤
           │   Phase0   │   Phase3   │
    不紧急  │   准备     │  ML集成    │
           └────────────┴────────────┘
                    不重要
```

### 依赖关系

```
Phase0 (4周)
    ↓
Phase1 (1-2月) ───────────────────────────────────┐
    ↓                   ↓                        │
Phase2 (2-3月)    Phase4 (2-3月)                  │
    ↓                   ↓                        │
Phase3 (3-4月) ───────────────────────────────────┤
    ↓                                                │
Phase5 (3-4月) ───────────────────────────────────┘
    ↓
Phase6 (2-3月)
```

---

## 十、风险与备选

### 主要风险

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| QMT API限制 | 中 | 高 | 预留手动干预 |
| iFind数据断供 | 低 | 高 | Baostock备用 |
| 模型过拟合 | 高 | 高 | 严格样本外测试 |
| 市场风格切换 | 中 | 中 | 多策略覆盖 |

### 备选方案

```
数据源备选:
iFind → Baostock + AkShare + Efinance

回测备选:
QMT回测 → Backtrader研究 → 自研

ML备选:
Qlib → 自建因子库

情感分析备选:
DeepSeek → Qwen3本地 → 规则引擎
```

---

## 十一、进度追踪模板

### 每周检查点

```markdown
## Week X 检查

### 完成情况
- [ ] 任务1
- [ ] 任务2

### 里程碑
- [ ] M1.1: ...

### 遇到的问题
- 问题1: 解决方案

### 下周计划
- [ ] 任务1
- [ ] 任务2
```

---

**文档状态**: 规划完成
**下一步**: Phase 0准备阶段立即启动
