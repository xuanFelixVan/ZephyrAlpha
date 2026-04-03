---
module_id: UX_README_001
version: 4.0.0
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

# NozyIO可视化编辑系统

> 清风量化系统 v4.0 的四层可视化策略编辑架构

---

## 1. 系统概述

### 1.1 设计背景

传统量化策略开发存在以下痛点：
- **代码门槛高**: 需要掌握Python编程
- **调试周期长**: 修改-测试循环效率低
- **因子管理乱**: 因子库缺乏统一管理
- **协作困难**: 策略版本难以追溯

NozyIO通过四层可视化编辑系统，让用户通过拖拽、连线、配置等方式完成从因子到策略的全流程开发。

### 1.2 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    NozyIO可视化编辑系统                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  │  第一层     │   │  第二层     │   │  第三层     │   │  第四层     │
│  │  因子编辑器 │ → │  特征编辑器 │ → │  策略编辑器 │ → │  回测系统   │
│  │  (5001)    │   │  (5002)    │   │  (5003)    │   │  (5004)    │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
│        │                 │                 │                 │
│        ▼                 ▼                 ▼                 ▼
│  ┌─────────────────────────────────────────────────────────────┐
│  │                      统一数据总线                            │
│  │              (因子 → 特征 → 信号 → 回测)                    │
│  └─────────────────────────────────────────────────────────────┘
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 端口分配

| 层级 | 服务 | 端口 | 说明 |
|------|------|------|------|
| 第一层 | 因子编辑器 | 5001 | Alpha因子构建 |
| 第二层 | 特征编辑器 | 5002 | 机器学习特征生成 |
| 第三层 | 策略编辑器 | 5003 | 交易策略设计 |
| 第四层 | 回测系统 | 5004 | 历史回测验证 |

---

## 2. 第一层：因子编辑器

### 2.1 功能定位

构建Alpha因子的可视化编辑环境，支持：
- 技术指标拖拽
- 统计指标配置
- 机器学习特征引入
- 因子表达式编写

### 2.2 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  因子编辑器 - ALPHA_001                                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────────────────────────────┐  ┌─────┐ │
│  │ 模块库   │  │          画布区域                │  │属性 │ │
│  │         │  │                                  │  │面板 │ │
│  │ 📊 技术 │  │    [MA5] ──┬── [CROSS] ── [ALPHA]│  │     │ │
│  │   指标   │  │            │                     │  │参数 │ │
│  │ 📈 统计 │  │    [VOL] ──┘                     │  │     │ │
│  │   指标   │  │                                  │  │     │ │
│  │ 🤖 ML   │  │                                  │  │     │ │
│  │   特征   │  │                                  │  │     │ │
│  └─────────┘  └──────────────────────────────────┘  └─────┘ │
├─────────────────────────────────────────────────────────────┤
│  因子表达式: ALPHA_001 = CROSS(MA(close,5), MA(close,20))   │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 支持的因子类型

#### 技术指标模块

| 类别 | 因子 | 参数 | 输出类型 |
|------|------|------|----------|
| 趋势类 | MA, EMA, SMA | period | float |
| 趋势类 | MACD | fast, slow, signal | dict |
| 趋势类 | BOLL | period, std | dict |
| 均值回归 | RSI | period | float |
| 均值回归 | KDJ | period | dict |
| 波动率 | ATR | period | float |
| 波动率 | STDDEV | period | float |
| 量价 | VOLUME_RATIO | period | float |
| 量价 | AMOUNT_RATIO | period | float |

#### 统计指标模块

| 类别 | 因子 | 参数 | 输出类型 |
|------|------|------|----------|
| 描述统计 | SKEWNESS | window | float |
| 描述统计 | KURTOSIS | window | float |
| 分位数 | QUANTILE | window, q | float |
| 滚动相关 | ROLLING_CORR | window, target | float |

#### 机器学习特征模块

| 类别 | 因子 | 参数 | 输出类型 |
|------|------|------|----------|
| 降维 | PCA | n_components | array |
| 聚类 | KMEANS | n_clusters | array |
| 异常检测 | ISOLATION_FOREST | threshold | array |

### 2.4 接口定义

```python
class FactorEditor:
    """因子编辑器接口"""

    def get_available_modules(self) -> List[Module]:
        """获取可用的因子模块"""

    def create_factor(self, config: FactorConfig) -> FactorResult:
        """创建新因子"""
        # config包含：模块类型、参数、连接关系

    def validate_factor(self, factor_id: str) -> ValidationResult:
        """验证因子合法性"""

    def save_factor(self, factor_id: str, workspace_id: str) -> bool:
        """保存因子到工作区"""

    def load_factor(self, factor_id: str) -> FactorConfig:
        """加载因子配置"""

    def calculate_factor(self, factor_id: str, data: DataFrame) -> Series:
        """计算因子值"""

class FactorConfig:
    factor_id: str
    name: str
    modules: List[ModuleConnection]  # 模块连接关系
    params: Dict[str, Any]
    output_type: str  # float, dict, array
```

---

## 3. 第二层：特征编辑器

### 3.1 功能定位

将多个因子组合成机器学习特征集：
- 特征选择
- 特征降维
- 特征归一化
- 特征库管理

### 3.2 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  特征编辑器 - FEATURE_SET_001                                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────────────────────────────┐  ┌─────┐ │
│  │ 因子库   │  │          画布区域                 │  │属性 │ │
│  │         │  │                                  │  │面板 │ │
│  │ 🌟 已选 │  │  [ALPHA_001] ──┬── [CONCAT] ──   │  │     │ │
│  │   因子   │  │               │       │         │  │特征 │ │
│  │         │  │ [ALPHA_002] ──┴── [SCALE] ──    │  │选择 │ │
│  │ 📥 待选 │  │               │       │         │  │     │ │
│  │   因子   │  │ [RISK_001] ──┴────── [PCA] ──── │  │降维 │ │
│  │         │  │                                  │  │     │ │
│  └─────────┘  └──────────────────────────────────┘  └─────┘ │
├─────────────────────────────────────────────────────────────┤
│  输出特征: 20维 → PCA(5维) → 归一化                         │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 支持的特征处理

| 处理类型 | 模块 | 参数 | 说明 |
|----------|------|------|------|
| 组合 | Concat | axis | 按列拼接多个因子 |
| 选择 | FeatureSelect | method, k | 基于方法的特征选择 |
| 降维 | PCA | n_components | 主成分分析 |
| 归一化 | StandardScaler | - | Z-score标准化 |
| 归一化 | MinMaxScaler | - | 0-1标准化 |
| 缺失值 | FillNa | method | 填充缺失值 |

### 3.4 接口定义

```python
class FeatureEditor:
    """特征编辑器接口"""

    def add_factor(self, feature_set_id: str, factor_id: str) -> bool:
        """添加因子到特征集"""

    def remove_factor(self, feature_set_id: str, factor_id: str) -> bool:
        """从特征集移除因子"""

    def configure_processing(self, config: ProcessingConfig) -> bool:
        """配置特征处理流程"""

    def calculate_ic(self, feature_set_id: str, target: Series) -> Dict:
        """计算特征IC值"""

    def optimize_feature_set(self, target: Series, method: str) -> List[str]:
        """优化特征集"""

class FeatureSetConfig:
    feature_set_id: str
    factors: List[str]
    processing_steps: List[ProcessingStep]
    target: str
```

---

## 4. 第三层：策略编辑器

### 4.1 功能定位

基于特征集生成交易信号：
- 条件判断逻辑
- 信号生成规则
- 风控规则嵌入
- 策略参数优化

### 4.2 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  策略编辑器 - STRATEGY_001                                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌──────────────────────────────────┐  ┌─────┐ │
│  │ 信号模块 │  │          画布区域                 │  │属性 │ │
│  │         │  │                                  │  │面板 │ │
│  │ 🔀 条件 │  │  [SIGNAL] ──┬── [POSITION] ──     │  │     │ │
│  │ 🔄 逻辑 │  │             │           │        │  │信号 │ │
│  │ ⚖️ 风控 │  │  [FOLLOWUP]─┴────────────┘        │  │逻辑 │ │
│  │ 📊 仓位 │  │                                  │  │     │ │
│  │         │  │                                  │  │风控 │ │
│  └─────────┘  └──────────────────────────────────┘  └─────┘ │
├─────────────────────────────────────────────────────────────┤
│  策略逻辑: SIGNAL > 0.5 → POSITION(0.3) → RISK_CHECK        │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 支持的策略模块

| 类别 | 模块 | 参数 | 说明 |
|------|------|------|------|
| 信号生成 | Compare | operator, threshold | 条件比较 |
| 信号生成 | Cross | fast, slow | 穿越信号 |
| 信号生成 | Range | upper, lower | 区间信号 |
| 逻辑运算 | And, Or, Not | - | 逻辑组合 |
| 仓位管理 | FixedPosition | size | 固定仓位 |
| 仓位管理 | DynamicPosition | method | 动态仓位 |
| 风控规则 | MaxPosition | limit | 最大仓位限制 |
| 风控规则 | MaxLoss | limit | 最大亏损限制 |

### 4.4 接口定义

```python
class StrategyEditor:
    """策略编辑器接口"""

    def create_signal_module(self, config: SignalConfig) -> str:
        """创建信号模块"""

    def connect_modules(self, from_id: str, to_id: str, port: str) -> bool:
        """连接模块"""

    def set_parameters(self, module_id: str, params: Dict) -> bool:
        """设置模块参数"""

    def generate_signal(self, strategy_id: str, features: DataFrame) -> Series:
        """生成交易信号"""

    def backtest_strategy(self, strategy_id: str) -> BacktestResult:
        """回测策略"""

    def optimize_parameters(self, strategy_id: str, method: str) -> Dict:
        """优化策略参数"""

class StrategyConfig:
    strategy_id: str
    modules: List[StrategyModule]
    connections: List[Connection]
    risk_rules: List[RiskRule]
```

---

## 5. 第四层：回测系统

### 5.1 功能定位

完整回测和可视化报告：
- 高性能回测引擎
- 多参数配置
- 可视化绩效报告
- 风险分析

### 5.2 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  回测系统 - BACKTEST_001                                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    绩效图表区                         │   │
│  │   📈 收益曲线   📊 回撤图   📉 月度收益   📋 统计   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌──────────────────┐  ┌────────────────────────────────┐   │
│  │   回测配置        │  │         回测结果               │   │
│  │   • 时间范围      │  │   总收益率: 25.6%             │   │
│  │   • 初始资金      │  │   夏普比率: 1.85              │   │
│  │   • 手续费        │  │   最大回撤: 8.3%              │   │
│  │   • 滑点          │  │   胜率: 62.5%                 │   │
│  └──────────────────┘  └────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 回测指标

| 类别 | 指标 | 说明 |
|------|------|------|
| 收益 | 总收益率 | 策略总收益 |
| 收益 | 年化收益率 | 年化收益 |
| 风险 | 夏普比率 | 风险调整收益 |
| 风险 | 最大回撤 | 最大回撤幅度 |
| 风险 | 波动率 | 收益波动率 |
| 交易 | 胜率 | 盈利交易占比 |
| 交易 | 盈亏比 | 平均盈利/亏损 |
| 交易 | 交易次数 | 总交易次数 |

### 5.4 接口定义

```python
class BacktestEngine:
    """回测引擎接口"""

    def configure(self, config: BacktestConfig) -> bool:
        """配置回测参数"""

    def run(self, strategy_id: str, data: DataFrame) -> BacktestResult:
        """运行回测"""

    def get_equity_curve(self) -> Series:
        """获取权益曲线"""

    def get_positions(self) -> DataFrame:
        """获取持仓记录"""

    def get_trades(self) -> DataFrame:
        """获取交易记录"""

    def get_performance_report(self) -> PerformanceReport:
        """获取绩效报告"""

    def generate_chart(self, chart_type: str) -> bytes:
        """生成图表"""

class BacktestConfig:
    start_date: str
    end_date: str
    initial_capital: float
    commission: float  # 手续费率
    slippage: float    # 滑点
    benchmark: str      # 基准

class BacktestResult:
    equity_curve: Series
    positions: DataFrame
    trades: DataFrame
    performance: PerformanceMetrics
```

---

## 6. 统一数据总线

### 6.1 数据流转

```
因子编辑器 → 因子数据 ─┐
                      ├→ 特征编辑器 → 特征数据 ─┐
市场数据 ─────────────┘                        │
                                              ├→ 策略编辑器 → 信号数据 ─┐
                                              │                        │
历史数据 ──────────────────────────────────────┘                        │
                                                                      ├→ 回测系统 → 报告
                                              │
信号数据 ──────────────────────────────────────┘
```

### 6.2 数据格式

```python
# 因子数据格式
FactorData = DataFrame {
    'symbol': str,
    'date': datetime,
    'factor_id': str,
    'value': float
}

# 特征数据格式
FeatureData = DataFrame {
    'symbol': str,
    'date': datetime,
    'feature_set_id': str,
    'features': np.array  # 多维特征
}

# 信号数据格式
SignalData = DataFrame {
    'symbol': str,
    'date': datetime,
    'signal': float,  # -1 to 1
    'confidence': float,
    'action': str  # 'buy', 'sell', 'hold'
}

# 回测结果格式
BacktestResult = {
    'equity_curve': Series,
    'positions': DataFrame,
    'trades': DataFrame,
    'metrics': PerformanceMetrics,
    'charts': Dict[str, bytes]
}
```

---

## 7. API端点

### 7.1 因子编辑器 (端口 5001)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/factors` | GET | 获取因子列表 |
| `/api/v1/factors` | POST | 创建新因子 |
| `/api/v1/factors/{id}` | GET | 获取因子详情 |
| `/api/v1/factors/{id}` | PUT | 更新因子 |
| `/api/v1/factors/{id}` | DELETE | 删除因子 |
| `/api/v1/factors/{id}/calculate` | POST | 计算因子值 |
| `/api/v1/factors/{id}/validate` | POST | 验证因子 |

### 7.2 特征编辑器 (端口 5002)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/features` | GET | 获取特征集列表 |
| `/api/v1/features` | POST | 创建特征集 |
| `/api/v1/features/{id}` | GET | 获取特征集详情 |
| `/api/v1/features/{id}` | PUT | 更新特征集 |
| `/api/v1/features/{id}/calculate` | POST | 计算特征 |
| `/api/v1/features/{id}/ic` | POST | 计算IC值 |

### 7.3 策略编辑器 (端口 5003)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/strategies` | GET | 获取策略列表 |
| `/api/v1/strategies` | POST | 创建新策略 |
| `/api/v1/strategies/{id}` | GET | 获取策略详情 |
| `/api/v1/strategies/{id}` | PUT | 更新策略 |
| `/api/v1/strategies/{id}/signal` | POST | 生成信号 |
| `/api/v1/strategies/{id}/backtest` | POST | 回测策略 |

### 7.4 回测系统 (端口 5004)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/backtest` | POST | 运行回测 |
| `/api/v1/backtest/{id}` | GET | 获取回测结果 |
| `/api/v1/backtest/{id}/equity` | GET | 获取权益曲线 |
| `/api/v1/backtest/{id}/trades` | GET | 获取交易记录 |
| `/api/v1/backtest/{id}/report` | GET | 获取绩效报告 |
| `/api/v1/backtest/{id}/chart/{type}` | GET | 获取图表 |

---

## 8. 索引设计

### 8.1 文档索引

| 文档路径 | 说明 |
|----------|------|
| docs/08_USER_EXPERIENCE/04_NOZYIO/README.md | 本文档 |
| docs/08_USER_EXPERIENCE/04_NOZYIO/因子编辑器.md | 第一层详细设计 |
| docs/08_USER_EXPERIENCE/04_NOZYIO/特征编辑器.md | 第二层详细设计 |
| docs/08_USER_EXPERIENCE/04_NOZYIO/策略编辑器.md | 第三层详细设计 |
| docs/08_USER_EXPERIENCE/04_NOZYIO/回测系统.md | 第四层详细设计 |
| docs/08_USER_EXPERIENCE/04_NOZYIO/API.md | API文档 |

### 8.2 模块索引

| 模块ID | 模块名称 | Layer归属 | 说明 |
|--------|----------|-----------|------|
| NE1 | FactorEditor | UI Layer 1 | 因子编辑器 |
| NE2 | FeatureEditor | UI Layer 2 | 特征编辑器 |
| NE3 | StrategyEditor | UI Layer 3 | 策略编辑器 |
| NE4 | BacktestViewer | UI Layer 4 | 回测系统 |

---

**最后更新**: 2026-03-28
**版本**: v4.0
**维护者**: 清风量化系统
