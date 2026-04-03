---
module_id: STATISTICAL_ARBITRAGE_MODULE_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席技术评审官
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 5 (中观策略层) | 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 统计套利模块技术规格书

> 清风量化系统 v5.2 - 统计套利模块详细技术设计
> **模块ID**: `STATISTICAL_ARBITRAGE_MODULE_001`
> **版本**: v1.0.0
> **状态**: ✅ 正式

---

## 1. 概述

### 1.1 设计背景与业务目标
- **业务需求**: 系统需要统计套利模块实现市场中性策略和配对交易
- **技术痛点**: 
  - 配对识别困难：需要从大量股票中识别协整关系
  - 市场中性复杂：需要同时实现行业中性和风格中性
  - 信号质量不稳定：统计套利信号容易受市场环境影响
  - 风险控制挑战：多空头寸风险难以平衡
- **预期价值**: 
  - 提供市场中性收益来源
  - 降低系统性风险暴露
  - 提升组合夏普比率
  - 实现文艺复兴风格的市场中性策略

### 1.2 技术定位与架构层归属
- **Layer定位**: Layer 6 - 组合优化层 (符合ARCHITECTURE.md定义)
- **模块类别**: 核心套利模块
- **架构角色**: Layer 6套利策略核心，负责配对交易和市场中性组合构建

### 1.3 版本信息
| 版本 | 日期 | 作者 | 变更说明 | 状态 |
|------|------|------|----------|------|
| v1.0.0 | 2026-04-02 | 首席技术评审官 | 初始版本 | Active |

---

## 2. 详细架构设计

### 2.1 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 6: 组合优化层                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     StatisticalArbitrageModule (统计套利模块主模块)    │  │
│  │  - 配对交易策略                                        │  │
│  │  - 市场中性组合                                        │  │
│  │  - 统计套利信号                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          核心组件                                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │PairSelector │ │Cointegration│ │SpreadTrader │  │  │
│  │  │配对选择器    │  │协整分析器   │  │价差交易器   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │MarketNeutrl│ │SignalGenertr│ │RiskController│  │  │
│  │  │市场中性组合 │  │信号生成器   │  │风险控制器   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          数据源层                                      │  │
│  │  - 行情数据 (价格、成交量)                            │  │
│  │  - 基本面数据 (财务指标)                              │  │
│  │  - 行业分类数据                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位详细说明
- **Layer归属**: Layer 6 - 组合优化层
- **职责范围**: 配对交易、市场中性组合构建、统计套利信号生成
- **上下层接口**: 
  - 上层依赖: Layer 5 StrategyEngine (提供策略信号)
  - 下层依赖: Layer 7 AIReportLayer (接收套利报告)

### 2.3 模块职责与边界定义
- **核心职责**: 配对交易、市场中性组合构建、统计套利信号生成
- **职责边界**: 
  - ✅ 本模块负责: 配对识别、协整检验、价差交易、市场中性组合、信号生成
  - ❌ 本模块不负责: 数据获取、交易执行、风险管理、组合优化
- **接口契约**: 提供统一的Python API接口

### 2.4 依赖关系
| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| numpy | 强依赖 | Python库 | >=1.24.0 | 数值计算 |
| pandas | 强依赖 | Python库 | >=2.0.0 | 数据处理 |
| scipy | 强依赖 | Python库 | >=1.11.0 | 统计检验 |
| statsmodels | 强依赖 | Python库 | >=0.14.0 | 协整检验 |

---

## 3. 接口定义

### 3.1 API接口规范

#### 3.1.1 主接口类
```python
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
import logging


class SignalType(Enum):
    """信号类型枚举"""
    LONG_SPREAD = "long_spread"      # 做多价差
    SHORT_SPREAD = "short_spread"    # 做空价差
    CLOSE_POSITION = "close_position" # 平仓
    HOLD = "hold"                    # 持有


@dataclass
class CointegratedPair:
    """协整股票对"""
    stock_a: str                    # 股票A代码
    stock_b: str                    # 股票B代码
    hedge_ratio: float              # 对冲比例
    correlation: float              # 相关系数
    adf_statistic: float            # ADF统计量
    p_value: float                  # P值
    half_life: float                # 半衰期（天）
    timestamp: datetime             # 时间戳


@dataclass
class PairTradingSignal:
    """配对交易信号"""
    pair: CointegratedPair          # 协整股票对
    signal_type: SignalType         # 信号类型
    z_score: float                  # Z-score值
    spread: float                   # 当前价差
    mean_spread: float              # 价差均值
    std_spread: float               # 价差标准差
    position_ratio: float           # 仓位比例
    timestamp: datetime             # 时间戳


@dataclass
class PortfolioAllocation:
    """组合配置"""
    long_positions: Dict[str, float]   # 多头头寸
    short_positions: Dict[str, float]  # 空头头寸
    net_exposure: float                 # 净敞口
    gross_exposure: float               # 总敞口
    industry_exposure: Dict[str, float] # 行业暴露
    style_exposure: Dict[str, float]    # 风格暴露
    timestamp: datetime                 # 时间戳


class StatisticalArbitrageModule:
    """统计套利模块"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化统计套利模块
        
        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        self.pair_selector = PairSelector(self.config.get('pair_selection', {}))
        self.cointegration_analyzer = CointegrationAnalyzer(
            self.config.get('cointegration', {})
        )
        self.spread_trader = SpreadTrader(self.config.get('spread_trading', {}))
        self.market_neutral_portfolio = MarketNeutralPortfolio(
            self.config.get('market_neutral', {})
        )
        self.signal_generator = StatisticalArbitrageSignalGenerator(self.config)
        
    def find_cointegrated_pairs(
        self, 
        price_data: pd.DataFrame,
        stock_pool: Optional[List[str]] = None
    ) -> List[CointegratedPair]:
        """
        寻找协整股票对
        
        Args:
            price_data: 价格数据
            stock_pool: 股票池（可选）
            
        Returns:
            List[CointegratedPair]: 协整股票对列表
        """
        self.logger.info("开始寻找协整股票对")
        
        if stock_pool is None:
            stock_pool = price_data.columns.tolist()
        
        candidate_pairs = self.pair_selector.select_pairs(price_data, stock_pool)
        
        cointegrated_pairs = []
        for pair in candidate_pairs:
            result = self.cointegration_analyzer.test_cointegration(
                price_data[pair[0]], 
                price_data[pair[1]]
            )
            
            if result['is_cointegrated']:
                cointegrated_pair = CointegratedPair(
                    stock_a=pair[0],
                    stock_b=pair[1],
                    hedge_ratio=result['hedge_ratio'],
                    correlation=result['correlation'],
                    adf_statistic=result['adf_statistic'],
                    p_value=result['p_value'],
                    half_life=result['half_life'],
                    timestamp=datetime.now()
                )
                cointegrated_pairs.append(cointegrated_pair)
        
        self.logger.info(f"找到 {len(cointegrated_pairs)} 对协整股票对")
        
        return cointegrated_pairs
    
    def generate_pair_trading_signals(
        self,
        price_data: pd.DataFrame,
        pairs: List[CointegratedPair]
    ) -> List[PairTradingSignal]:
        """
        生成配对交易信号
        
        Args:
            price_data: 价格数据
            pairs: 协整股票对列表
            
        Returns:
            List[PairTradingSignal]: 配对交易信号列表
        """
        self.logger.info("开始生成配对交易信号")
        
        signals = []
        for pair in pairs:
            signal = self.spread_trader.generate_signal(
                price_data[pair.stock_a],
                price_data[pair.stock_b],
                pair.hedge_ratio
            )
            
            if signal['signal_type'] != SignalType.HOLD:
                trading_signal = PairTradingSignal(
                    pair=pair,
                    signal_type=signal['signal_type'],
                    z_score=signal['z_score'],
                    spread=signal['spread'],
                    mean_spread=signal['mean_spread'],
                    std_spread=signal['std_spread'],
                    position_ratio=signal['position_ratio'],
                    timestamp=datetime.now()
                )
                signals.append(trading_signal)
        
        self.logger.info(f"生成 {len(signals)} 个配对交易信号")
        
        return signals
    
    def construct_market_neutral_portfolio(
        self,
        signals: List[PairTradingSignal],
        constraints: Optional[Dict[str, Any]] = None
    ) -> PortfolioAllocation:
        """
        构建市场中性组合
        
        Args:
            signals: 配对交易信号列表
            constraints: 约束条件
            
        Returns:
            PortfolioAllocation: 组合配置
        """
        self.logger.info("开始构建市场中性组合")
        
        allocation = self.market_neutral_portfolio.construct(signals, constraints)
        
        self.logger.info(f"市场中性组合构建完成，净敞口={allocation.net_exposure:.2f}")
        
        return allocation
```

#### 3.1.2 配对选择器类
```python
class PairSelector:
    """配对选择器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化配对选择器
        
        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        self.min_correlation = config.get('min_correlation', 0.7)
        self.max_pairs = config.get('max_pairs', 50)
        
    def select_pairs(
        self, 
        price_data: pd.DataFrame,
        stock_pool: List[str]
    ) -> List[Tuple[str, str]]:
        """
        选择候选股票对
        
        Args:
            price_data: 价格数据
            stock_pool: 股票池
            
        Returns:
            List[Tuple[str, str]]: 候选股票对列表
        """
        self.logger.info(f"开始选择候选股票对，股票池大小={len(stock_pool)}")
        
        returns = price_data[stock_pool].pct_change().dropna()
        
        correlation_matrix = returns.corr()
        
        candidate_pairs = []
        for i in range(len(stock_pool)):
            for j in range(i + 1, len(stock_pool)):
                stock_a = stock_pool[i]
                stock_b = stock_pool[j]
                
                correlation = correlation_matrix.loc[stock_a, stock_b]
                
                if correlation >= self.min_correlation:
                    candidate_pairs.append((stock_a, stock_b))
        
        candidate_pairs = candidate_pairs[:self.max_pairs]
        
        self.logger.info(f"找到 {len(candidate_pairs)} 对候选股票对")
        
        return candidate_pairs
```

#### 3.1.3 协整分析器类
```python
from statsmodels.tsa.stattools import coint, adfuller
from scipy import stats


class CointegrationAnalyzer:
    """协整分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化协整分析器
        
        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        self.adf_critical_value = config.get('adf_critical_value', 0.05)
        self.min_half_life = config.get('min_half_life', 5)
        self.max_half_life = config.get('max_half_life', 60)
        
    def test_cointegration(
        self, 
        series_a: pd.Series,
        series_b: pd.Series
    ) -> Dict[str, Any]:
        """
        协整检验
        
        Args:
            series_a: 价格序列A
            series_b: 价格序列B
            
        Returns:
            Dict[str, Any]: 协整检验结果
        """
        coint_t, p_value, crit_value = coint(series_a, series_b)
        
        X = np.column_stack([np.ones(len(series_b)), series_b.values])
        hedge_ratio = np.linalg.lstsq(X, series_a.values, rcond=None)[0][1]
        
        spread = series_a - hedge_ratio * series_b
        
        adf_result = adfuller(spread, maxlag=1)
        adf_statistic = adf_result[0]
        adf_p_value = adf_result[1]
        
        half_life = self._calculate_half_life(spread)
        
        is_cointegrated = (
            p_value < self.adf_critical_value and
            self.min_half_life <= half_life <= self.max_half_life
        )
        
        correlation = series_a.corr(series_b)
        
        return {
            'is_cointegrated': is_cointegrated,
            'hedge_ratio': hedge_ratio,
            'correlation': correlation,
            'adf_statistic': adf_statistic,
            'p_value': p_value,
            'half_life': half_life,
            'spread': spread
        }
    
    def _calculate_half_life(self, spread: pd.Series) -> float:
        """
        计算半衰期
        
        Args:
            spread: 价差序列
            
        Returns:
            float: 半衰期（天）
        """
        spread_lag = spread.shift(1).dropna()
        spread_ret = spread.diff().dropna()
        
        spread_lag = spread_lag.iloc[:len(spread_ret)]
        spread_ret = spread_ret.iloc[:len(spread_lag)]
        
        X = np.column_stack([np.ones(len(spread_lag)), spread_lag.values])
        params = np.linalg.lstsq(X, spread_ret.values, rcond=None)[0]
        
        lambda_param = params[1]
        
        if lambda_param >= 0:
            return float('inf')
        
        half_life = -np.log(2) / lambda_param
        
        return half_life
```

#### 3.1.4 价差交易器类
```python
class SpreadTrader:
    """价差交易器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化价差交易器
        
        Args:
            config: 配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        self.entry_zscore = config.get('entry_zscore', 2.0)
        self.exit_zscore = config.get('exit_zscore', 0.5)
        self.stop_loss = config.get('stop_loss', 0.05)
        
    def generate_signal(
        self,
        price_a: pd.Series,
        price_b: pd.Series,
        hedge_ratio: float
    ) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            price_a: 价格序列A
            price_b: 价格序列B
            hedge_ratio: 对冲比例
            
        Returns:
            Dict[str, Any]: 交易信号
        """
        spread = price_a - hedge_ratio * price_b
        
        mean_spread = spread.mean()
        std_spread = spread.std()
        
        current_spread = spread.iloc[-1]
        z_score = (current_spread - mean_spread) / std_spread
        
        signal_type = SignalType.HOLD
        position_ratio = 0.0
        
        if z_score > self.entry_zscore:
            signal_type = SignalType.SHORT_SPREAD
            position_ratio = min(z_score / self.entry_zscore, 2.0)
        elif z_score < -self.entry_zscore:
            signal_type = SignalType.LONG_SPREAD
            position_ratio = min(abs(z_score) / self.entry_zscore, 2.0)
        elif abs(z_score) < self.exit_zscore:
            signal_type = SignalType.CLOSE_POSITION
            position_ratio = 0.0
        
        return {
            'signal_type': signal_type,
            'z_score': z_score,
            'spread': current_spread,
            'mean_spread': mean_spread,
            'std_spread': std_spread,
            'position_ratio': position_ratio
        }
```

### 3.2 数据格式与协议定义

#### 3.2.1 输入数据格式
```json
{
  "price_data": {
    "stock_a": [100.0, 101.5, 102.3, ...],
    "stock_b": [50.0, 50.8, 51.2, ...],
    ...
  },
  "timestamp": "2026-04-02T10:00:00Z"
}
```

#### 3.2.2 输出数据格式
```json
{
  "pair_trading_signal": {
    "pair": {
      "stock_a": "600000.SH",
      "stock_b": "601166.SH",
      "hedge_ratio": 1.25,
      "correlation": 0.85,
      "half_life": 15.5
    },
    "signal_type": "long_spread",
    "z_score": -2.3,
    "position_ratio": 1.15,
    "timestamp": "2026-04-02T10:05:00Z"
  }
}
```

### 3.3 性能指标与SLA要求
| 指标 | 目标值 | 测量方法 | 备注 |
|------|--------|----------|------|
| **配对识别准确率** | ≥60% | 历史回测 | 协整关系稳定性 |
| **信号胜率** | ≥55% | 历史回测 | 盈利信号占比 |
| **组合夏普比率** | ≥1.5 | 历史回测 | 年化夏普比率 |
| **最大回撤** | ≤10% | 历史回测 | 最大回撤控制 |
| **响应时间** | ≤30秒 | P95延迟 | 信号生成延迟 |

---

## 4. 数据模型与存储

### 4.1 数据库表结构设计
```sql
-- 协整股票对历史表
CREATE TABLE IF NOT EXISTS cointegrated_pairs_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_a VARCHAR(20) NOT NULL,
    stock_b VARCHAR(20) NOT NULL,
    hedge_ratio REAL NOT NULL,
    correlation REAL NOT NULL,
    adf_statistic REAL NOT NULL,
    p_value REAL NOT NULL,
    half_life REAL NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_stocks (stock_a, stock_b)
);

-- 配对交易信号历史表
CREATE TABLE IF NOT EXISTS pair_trading_signals_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_a VARCHAR(20) NOT NULL,
    stock_b VARCHAR(20) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,
    z_score REAL NOT NULL,
    spread REAL NOT NULL,
    position_ratio REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp)
);
```

### 4.2 数据流与ETL流程
```
行情数据 → 配对选择 → 协整检验 → 价差交易 → 信号生成 → 组合构建 → 风险控制
```

---

## 5. 算法实现说明

### 5.1 核心算法原理

#### 5.1.1 配对选择算法
```
算法名称: 基于相关性的配对选择
输入: 价格数据、股票池
输出: 候选股票对列表

步骤:
1. 计算股票收益率相关系数矩阵
2. 筛选相关性 > 0.7 的股票对
3. 按相关性排序
4. 返回前N对股票

时间复杂度: O(n²), n=股票数量
空间复杂度: O(n²)
```

#### 5.1.2 协整检验算法
```
算法名称: Engle-Granger两步法协整检验
输入: 两只股票的价格序列
输出: 协整检验结果

步骤:
1. 对价格序列进行线性回归
2. 对残差序列进行ADF检验
3. 计算半衰期
4. 判断是否协整

时间复杂度: O(T), T=时间序列长度
空间复杂度: O(T)
```

#### 5.1.3 价差交易算法
```
算法名称: 基于Z-score的价差交易
输入: 价差序列
输出: 交易信号

步骤:
1. 计算价差
2. 计算Z-score
3. 根据阈值生成信号
4. 计算仓位比例

时间复杂度: O(T)
空间复杂度: O(T)
```

---

## 6. 实施技术栈

### 6.1 语言与框架
| 技术选型 | 版本要求 | 用途 | 选择理由 |
|----------|----------|------|----------|
| Python | >=3.8 | 主要开发语言 | 量化系统标准语言 |
| scipy | >=1.11.0 | 统计检验 | 协整检验工具 |
| statsmodels | >=0.14.0 | 时间序列分析 | ADF检验工具 |
| pandas | >=2.0.0 | 数据处理 | 标准工具 |

### 6.2 第三方依赖
```yaml
requirements:
  - numpy>=1.24.0
  - pandas>=2.0.0
  - scipy>=1.11.0
  - statsmodels>=0.14.0
```

---

## 7. 测试策略

### 7.1 单元测试
| 测试项 | 测试内容 | 覆盖率目标 |
|--------|----------|------------|
| 配对选择 | 相关性计算正确性 | 100% |
| 协整检验 | 协整检验正确性 | 100% |
| 价差交易 | 信号生成正确性 | 100% |
| 组合构建 | 中性化正确性 | 100% |

### 7.2 集成测试
| 测试项 | 测试内容 | 验收标准 |
|--------|----------|----------|
| 配对识别 | 端到端配对识别 | 准确率≥60% |
| 信号生成 | 端到端信号生成 | 胜率≥55% |
| 组合构建 | 端到端组合构建 | 夏普比率≥1.5 |

---

## 8. 风险与约束

### 8.1 技术风险
| 风险项 | 风险等级 | 影响范围 | 缓解措施 |
|--------|----------|----------|----------|
| 协整关系失效 | P1 | 配对交易 | 动态监控、止损机制 |
| 市场冲击成本 | P2 | 交易执行 | 交易量限制、分批建仓 |
| 模型过拟合 | P2 | 信号质量 | 样本外测试、交叉验证 |
| 流动性风险 | P1 | 交易执行 | 流动性筛选、仓位限制 |

### 8.2 实施约束
- **数据依赖**: 需要高质量的价格数据
- **技能要求**: 需要统计学和量化交易知识
- **计算资源**: 协整检验需要一定计算资源

---

## 9. 验收标准

### 9.1 功能验收标准
- ✅ 能够识别协整股票对
- ✅ 能够生成配对交易信号
- ✅ 能够构建市场中性组合
- ✅ 能够生成统计套利信号

### 9.2 性能验收标准
- ✅ 配对识别准确率 ≥ 60%
- ✅ 信号胜率 ≥ 55%
- ✅ 组合夏普比率 ≥ 1.5
- ✅ 最大回撤 ≤ 10%

### 9.3 质量验收标准
- ✅ 代码覆盖率 ≥ 80%
- ✅ 文档完整性 ≥ 95%
- ✅ 架构合规性 100%

---

## 10. 实施路线图

### 10.1 Week 3: 配对交易策略开发
- Day 1-2: 配对选择算法实现
- Day 3-4: 协整检验算法实现
- Day 5-7: 价差交易策略实现

### 10.2 Week 4: 市场中性组合与信号生成
- Day 1-3: 市场中性组合构建
- Day 4-5: 统计套利信号生成
- Day 6-7: 集成测试与文档

---

**文档版本**: v1.0.0 | **创建日期**: 2026-04-02 | **维护者**: 首席技术评审官
