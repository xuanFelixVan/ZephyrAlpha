# 验证与测试框架蓝图 (Validation & Testing Framework Blueprint)

> **模块ID**: L3_VTF_001
> **版本**: v1.0
> **创建日期**: 2026-04-03
> **Layer定位**: Layer 3 - 舆情分析层
> **优先级**: P1 (高优先级)
> **预计工作量**: 60小时
> **整合模块**: L3_ABTF_001 (A/B测试框架) + L3_BVM_001 (回测验证模块)

---

## 一、模块概述

### 1.1 设计背景

**业务需求**:
- 科学验证模型和策略效果
- 验证情感信号的有效性
- 评估因子和策略的稳健性
- 支持数据驱动的决策

**技术痛点**:
- 当前缺少A/B测试框架
- 缺少情感信号回测机制
- 缺少因子有效性验证工具
- 缺少稳健性检验机制

**预期价值**:
- 模型验证效率提升80%
- 策略验证准确率>95%
- 决策科学性提升100%
- 实验复现率100%

### 1.2 模块定位

**Layer归属**: Layer 3 - 舆情分析层
**模块类别**: 支撑性模块
**架构角色**: 验证与测试组件，确保模型和策略的有效性

---

## 二、详细架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│              验证与测试框架架构                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          ABTestingFramework (A/B测试框架)                    │  │
│  │  - 实验设计                                                   │  │
│  │  - 流量分配                                                   │  │
│  │  - 结果分析                                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↓                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          BacktestingValidator (回测验证器)                    │  │
│  │  - 情感信号回测                                               │  │
│  │  - 因子有效性验证                                             │  │
│  │  - 稳健性检验                                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ↓                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          开源工具层                                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────┐ │  │
│  │  │SciPy        │  │Statsmodels  │  │Backtrader   │  │Streamlit│ │
│  │  │Statistical  │  │Statistical  │  │Backtesting  │  │Dashboard│ │
│  │  │Tests        │  │Modeling     │  │Framework    │  │        │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

#### 2.2.1 A/B测试框架 (ABTestingFramework)

**功能设计**:

```python
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ExperimentConfig:
    """实验配置"""
    experiment_id: str              # 实验ID
    experiment_name: str            # 实验名称
    hypothesis: str                 # 假设描述
    control_group: str              # 对照组名称
    treatment_group: str            # 实验组名称
    sample_size: int                # 样本量
    significance_level: float       # 显著性水平 (默认0.05)
    power: float                    # 统计功效 (默认0.8)
    start_time: datetime            # 开始时间
    end_time: datetime              # 结束时间


@dataclass
class ExperimentResult:
    """实验结果"""
    experiment_id: str              # 实验ID
    control_metrics: Dict[str, float]  # 对照组指标
    treatment_metrics: Dict[str, float]  # 实验组指标
    lift: float                     # 提升度
    p_value: float                  # P值
    confidence_interval: Tuple[float, float]  # 置信区间
    is_significant: bool            # 是否显著
    conclusion: str                 # 结论


class ABTestingFramework:
    """A/B测试框架
    
    负责实验设计、流量分配和结果分析
    """
    
    def __init__(self, config: Dict[str, Any]):
        """初始化A/B测试框架
        
        Args:
            config: 配置参数
        """
        self.config = config
        self.experiments = {}
    
    def design_experiment(
        self,
        experiment_name: str,
        hypothesis: str,
        control_group: str,
        treatment_group: str,
        expected_lift: float = 0.05,
        baseline_metric: float = 0.5,
        significance_level: float = 0.05,
        power: float = 0.8
    ) -> ExperimentConfig:
        """设计实验
        
        Args:
            experiment_name: 实验名称
            hypothesis: 假设描述
            control_group: 对照组名称
            treatment_group: 实验组名称
            expected_lift: 预期提升度
            baseline_metric: 基线指标
            significance_level: 显著性水平
            power: 统计功效
            
        Returns:
            实验配置对象
        """
        pass
    
    def calculate_sample_size(
        self,
        baseline_metric: float,
        expected_lift: float,
        significance_level: float = 0.05,
        power: float = 0.8
    ) -> int:
        """计算样本量
        
        Args:
            baseline_metric: 基线指标
            expected_lift: 预期提升度
            significance_level: 显著性水平
            power: 统计功效
            
        Returns:
            所需样本量
        """
        pass
    
    def assign_traffic(
        self,
        user_id: str,
        experiment_id: str,
        traffic_split: Tuple[float, float] = (0.5, 0.5)
    ) -> str:
        """分配流量
        
        Args:
            user_id: 用户ID
            experiment_id: 实验ID
            traffic_split: 流量分配比例
            
        Returns:
            分配的组别
        """
        pass
    
    def collect_data(
        self,
        experiment_id: str,
        group: str,
        metrics: Dict[str, float]
    ) -> None:
        """收集实验数据
        
        Args:
            experiment_id: 实验ID
            group: 组别
            metrics: 指标数据
        """
        pass
    
    def analyze_experiment(
        self,
        experiment_id: str,
        metric_name: str = "accuracy"
    ) -> ExperimentResult:
        """分析实验结果
        
        Args:
            experiment_id: 实验ID
            metric_name: 指标名称
            
        Returns:
            实验结果对象
        """
        pass
    
    def statistical_test(
        self,
        control_data: np.ndarray,
        treatment_data: np.ndarray,
        test_type: str = "t-test"
    ) -> Tuple[float, float]:
        """统计检验
        
        Args:
            control_data: 对照组数据
            treatment_data: 实验组数据
            test_type: 检验类型 (t-test, mann-whitney, chi-square)
            
        Returns:
            (统计量, P值)
        """
        pass
    
    def generate_experiment_report(
        self,
        experiment_id: str,
        output_path: str = None
    ) -> str:
        """生成实验报告
        
        Args:
            experiment_id: 实验ID
            output_path: 输出路径
            
        Returns:
            报告路径
        """
        pass
```

**统计检验方法**:

1. **t检验** (Student's t-test):
   - 独立样本t检验
   - 配对样本t检验
   - Welch's t-test

2. **非参数检验**:
   - Mann-Whitney U检验
   - Wilcoxon符号秩检验
   - Kruskal-Wallis检验

3. **卡方检验**:
   - 卡方独立性检验
   - 卡方拟合优度检验

---

#### 2.2.2 回测验证器 (BacktestingValidator)

**功能设计**:

```python
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BacktestConfig:
    """回测配置"""
    backtest_id: str                # 回测ID
    start_date: datetime            # 开始日期
    end_date: datetime              # 结束日期
    initial_capital: float          # 初始资金
    commission: float               # 手续费率
    slippage: float                 # 滑点
    benchmark: str                  # 基准指数


@dataclass
class BacktestResult:
    """回测结果"""
    backtest_id: str                # 回测ID
    total_return: float             # 总收益率
    annual_return: float            # 年化收益率
    sharpe_ratio: float             # 夏普比率
    max_drawdown: float             # 最大回撤
    win_rate: float                 # 胜率
    profit_loss_ratio: float        # 盈亏比
    ic: float                       # 信息系数
    ir: float                       # 信息比率
    trades: List[Dict[str, Any]]    # 交易记录


class BacktestingValidator:
    """回测验证器
    
    负责情感信号回测、因子有效性验证和稳健性检验
    """
    
    def __init__(self, config: Dict[str, Any]):
        """初始化回测验证器
        
        Args:
            config: 配置参数
        """
        self.config = config
    
    def backtest_sentiment_signals(
        self,
        sentiment_data: pd.DataFrame,
        price_data: pd.DataFrame,
        strategy_params: Dict[str, Any]
    ) -> BacktestResult:
        """回测情感信号
        
        Args:
            sentiment_data: 情感数据
            price_data: 价格数据
            strategy_params: 策略参数
            
        Returns:
            回测结果对象
        """
        pass
    
    def validate_factor_effectiveness(
        self,
        factor_data: pd.DataFrame,
        return_data: pd.DataFrame,
        factor_name: str
    ) -> Dict[str, Any]:
        """验证因子有效性
        
        Args:
            factor_data: 因子数据
            return_data: 收益数据
            factor_name: 因子名称
            
        Returns:
            因子有效性验证结果
        """
        pass
    
    def calculate_ic(
        self,
        factor_values: np.ndarray,
        returns: np.ndarray,
        method: str = "spearman"
    ) -> float:
        """计算信息系数 (IC)
        
        Args:
            factor_values: 因子值
            returns: 收益率
            method: 相关性方法 (pearson, spearman)
            
        Returns:
            IC值
        """
        pass
    
    def calculate_ir(
        self,
        ic_series: np.ndarray
    ) -> float:
        """计算信息比率 (IR)
        
        Args:
            ic_series: IC序列
            
        Returns:
            IR值
        """
        pass
    
    def analyze_factor_decay(
        self,
        factor_data: pd.DataFrame,
        return_data: pd.DataFrame,
        max_lag: int = 20
    ) -> pd.DataFrame:
        """分析因子衰减
        
        Args:
            factor_data: 因子数据
            return_data: 收益数据
            max_lag: 最大滞后期
            
        Returns:
            因子衰减分析结果
        """
        pass
    
    def robustness_test(
        self,
        backtest_func: callable,
        params_range: Dict[str, List[Any]],
        n_simulations: int = 100
    ) -> Dict[str, Any]:
        """稳健性检验
        
        Args:
            backtest_func: 回测函数
            params_range: 参数范围
            n_simulations: 模拟次数
            
        Returns:
            稳健性检验结果
        """
        pass
    
    def parameter_sensitivity_analysis(
        self,
        base_params: Dict[str, Any],
        param_name: str,
        param_range: List[Any]
    ) -> pd.DataFrame:
        """参数敏感性分析
        
        Args:
            base_params: 基础参数
            param_name: 参数名称
            param_range: 参数范围
            
        Returns:
            敏感性分析结果
        """
        pass
    
    def out_of_sample_test(
        self,
        data: pd.DataFrame,
        train_ratio: float = 0.7
    ) -> Dict[str, Any]:
        """样本外测试
        
        Args:
            data: 数据
            train_ratio: 训练集比例
            
        Returns:
            样本外测试结果
        """
        pass
    
    def monte_carlo_simulation(
        self,
        strategy_func: callable,
        data: pd.DataFrame,
        n_simulations: int = 1000
    ) -> Dict[str, Any]:
        """蒙特卡洛模拟
        
        Args:
            strategy_func: 策略函数
            data: 数据
            n_simulations: 模拟次数
            
        Returns:
            蒙特卡洛模拟结果
        """
        pass
    
    def stress_test(
        self,
        data: pd.DataFrame,
        stress_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """压力测试
        
        Args:
            data: 数据
            stress_scenarios: 压力场景列表
            
        Returns:
            压力测试结果
        """
        pass
    
    def generate_backtest_report(
        self,
        backtest_id: str,
        output_path: str = None
    ) -> str:
        """生成回测报告
        
        Args:
            backtest_id: 回测ID
            output_path: 输出路径
            
        Returns:
            报告路径
        """
        pass
```

---

### 2.3 开源工具集成

#### Backtrader集成

**安装和配置**:

```bash
# 安装Backtrader
pip install backtrader
```

**回测引擎示例**:

```python
import backtrader as bt


class SentimentStrategy(bt.Strategy):
    """情感分析策略"""
    
    params = (
        ('sentiment_threshold', 0.5),
        ('holding_period', 5),
    )
    
    def __init__(self):
        self.sentiment = self.datas[0].sentiment
        self.order = None
        self.buy_price = None
        self.buy_comm = None
    
    def next(self):
        if self.order:
            return
        
        if not self.position:
            if self.sentiment[0] > self.params.sentiment_threshold:
                self.order = self.buy()
        else:
            if self.sentiment[0] < -self.params.sentiment_threshold:
                self.order = self.sell()


def run_backtest(
    data_feed,
    strategy_class,
    initial_capital: float = 100000.0
):
    """运行回测"""
    cerebro = bt.Cerebro()
    
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategy_class)
    cerebro.broker.setcash(initial_capital)
    cerebro.broker.setcommission(commission=0.001)
    
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    
    results = cerebro.run()
    
    return results[0]
```

---

#### SciPy统计检验集成

**统计检验示例**:

```python
from scipy import stats
import numpy as np


def perform_ttest(
    control: np.ndarray,
    treatment: np.ndarray,
    equal_var: bool = False
) -> Tuple[float, float]:
    """执行t检验
    
    Args:
        control: 对照组数据
        treatment: 实验组数据
        equal_var: 方差是否相等
        
    Returns:
        (统计量, P值)
    """
    statistic, p_value = stats.ttest_ind(
        control,
        treatment,
        equal_var=equal_var
    )
    return statistic, p_value


def perform_mannwhitney_u(
    control: np.ndarray,
    treatment: np.ndarray
) -> Tuple[float, float]:
    """执行Mann-Whitney U检验
    
    Args:
        control: 对照组数据
        treatment: 实验组数据
        
    Returns:
        (统计量, P值)
    """
    statistic, p_value = stats.mannwhitneyu(
        control,
        treatment,
        alternative='two-sided'
    )
    return statistic, p_value


def calculate_effect_size(
    control: np.ndarray,
    treatment: np.ndarray
) -> float:
    """计算效应量 (Cohen's d)
    
    Args:
        control: 对照组数据
        treatment: 实验组数据
        
    Returns:
        效应量
    """
    n1, n2 = len(control), len(treatment)
    var1, var2 = control.var(ddof=1), treatment.var(ddof=1)
    
    pooled_std = np.sqrt(
        ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
    )
    
    d = (treatment.mean() - control.mean()) / pooled_std
    return d
```

---

## 三、接口定义

### 3.1 RESTful API接口

#### A/B测试API

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


class ExperimentDesignRequest(BaseModel):
    """实验设计请求"""
    experiment_name: str
    hypothesis: str
    control_group: str
    treatment_group: str
    expected_lift: float = 0.05
    baseline_metric: float = 0.5


@app.post("/api/v1/experiment/design")
async def design_experiment(request: ExperimentDesignRequest):
    """设计实验"""
    pass


@app.post("/api/v1/experiment/start/{experiment_id}")
async def start_experiment(experiment_id: str):
    """启动实验"""
    pass


@app.post("/api/v1/experiment/stop/{experiment_id}")
async def stop_experiment(experiment_id: str):
    """停止实验"""
    pass


@app.get("/api/v1/experiment/result/{experiment_id}")
async def get_experiment_result(experiment_id: str):
    """获取实验结果"""
    pass
```

#### 回测验证API

```python
class BacktestRequest(BaseModel):
    """回测请求"""
    sentiment_data_path: str
    price_data_path: str
    strategy_params: Dict[str, Any]
    start_date: str
    end_date: str


@app.post("/api/v1/backtest/run")
async def run_backtest(request: BacktestRequest):
    """运行回测"""
    pass


@app.get("/api/v1/backtest/result/{backtest_id}")
async def get_backtest_result(backtest_id: str):
    """获取回测结果"""
    pass


@app.post("/api/v1/factor/validate")
async def validate_factor(
    factor_data_path: str,
    return_data_path: str,
    factor_name: str
):
    """验证因子有效性"""
    pass


@app.post("/api/v1/robustness/test")
async def run_robustness_test(
    backtest_id: str,
    test_type: str
):
    """运行稳健性检验"""
    pass
```

---

## 四、数据模型

### 4.1 实验记录表

```sql
CREATE TABLE experiments (
    experiment_id TEXT PRIMARY KEY,
    experiment_name TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    control_group TEXT NOT NULL,
    treatment_group TEXT NOT NULL,
    sample_size INTEGER NOT NULL,
    significance_level REAL NOT NULL,
    power REAL NOT NULL,
    status TEXT NOT NULL,  -- running, completed, stopped
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

### 4.2 实验数据表

```sql
CREATE TABLE experiment_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    group_name TEXT NOT NULL,
    metrics TEXT NOT NULL,  -- JSON格式
    collected_at TIMESTAMP NOT NULL,
    INDEX idx_experiment_id (experiment_id),
    INDEX idx_collected_at (collected_at)
);
```

### 4.3 回测记录表

```sql
CREATE TABLE backtest_records (
    backtest_id TEXT PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital REAL NOT NULL,
    total_return REAL NOT NULL,
    annual_return REAL NOT NULL,
    sharpe_ratio REAL NOT NULL,
    max_drawdown REAL NOT NULL,
    win_rate REAL NOT NULL,
    ic REAL,
    ir REAL,
    status TEXT NOT NULL,  -- running, completed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

---

## 五、实施计划

### 5.1 第1-2周: A/B测试框架开发

**任务清单**:
- [ ] 开发实验设计模块
- [ ] 开发流量分配模块
- [ ] 开发统计检验模块
- [ ] 开发结果分析模块
- [ ] 开发实验报告生成模块
- [ ] 测试和验证

**交付物**:
- ABTestingFramework代码
- 测试报告

---

### 5.2 第3-4周: 回测验证器开发

**任务清单**:
- [ ] 开发情感信号回测模块
- [ ] 开发因子有效性验证模块
- [ ] 开发稳健性检验模块
- [ ] 集成Backtrader
- [ ] 开发回测报告生成模块
- [ ] 测试和验证

**交付物**:
- BacktestingValidator代码
- 测试报告

---

### 5.3 第5周: 集成和测试

**任务清单**:
- [ ] 开发RESTful API
- [ ] 开发Streamlit仪表板
- [ ] 集成到现有系统
- [ ] 开发单元测试
- [ ] 开发集成测试
- [ ] 性能测试和优化

**交付物**:
- 集成后的系统
- Streamlit仪表板
- 测试报告

---

## 六、测试策略

### 6.1 单元测试

**测试范围**:
- 实验设计功能测试
- 统计检验功能测试
- 回测功能测试
- 因子验证功能测试

**测试工具**:
- pytest
- unittest.mock

---

### 6.2 集成测试

**测试范围**:
- 端到端A/B测试流程
- 端到端回测流程
- 因子验证流程

**测试数据**:
- 使用历史情感数据
- 使用历史价格数据

---

## 七、风险管理

### 7.1 技术风险

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| 统计方法误用 | 中 | 高 | 参考统计学最佳实践，咨询专家 |
| 回测过拟合 | 中 | 高 | 使用样本外测试，稳健性检验 |
| 性能问题 | 低 | 中 | 使用并行计算，优化算法 |

---

## 八、验收标准

### 8.1 功能验收

- [ ] 实验设计功能正常
- [ ] 统计检验功能正常
- [ ] 回测功能正常
- [ ] 因子验证功能正常
- [ ] 稳健性检验功能正常

### 8.2 性能验收

- [ ] 统计检验速度 < 1秒
- [ ] 回测速度 < 30秒/1年数据
- [ ] 因子验证速度 < 5秒

### 8.3 质量验收

- [ ] 代码覆盖率 > 80%
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过

---

## 九、相关文档

| 文档 | 说明 |
|------|------|
| [Layer 3改进实施计划](./LAYER3_IMPROVEMENT_IMPLEMENTATION_PLAN.md) | 总体实施计划 |
| [蓝图欠缺分析报告](./LAYER3_BLUEPRINT_GAP_ANALYSIS.md) | 欠缺模块分析 |

---

**版本**: v1.0 | **更新**: 2026-04-03 | **状态**: ✅ 活跃
