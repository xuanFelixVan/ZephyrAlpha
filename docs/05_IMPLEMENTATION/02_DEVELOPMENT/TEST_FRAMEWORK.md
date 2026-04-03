---
module_id: IMPL_DOC_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构实施标准
applicable_scope: 系统实施与部�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---


# 单元测试框架蓝图

> 清风量化系统 v5.0 - 单元测试框架
> **索引**: `TEST.UNIT.001`
> **开发时�?*: 15h
> **核心定位**: 确保代码质量，所有模块可独立测试


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **AAA模式** | Arrange-Act-Assert，测试结构清�?|
| **单一职责** | 每个测试只验证一个行�?|
| **独立�?* | 测试间无依赖，可并行执行 |
| **可重�?* | 测试结果稳定，不依赖外部状�?|
| **快速执�?* | 单元测试<1s，集成测�?10s |


## 2. 测试目录结构

### 2.1 目录组织

```
tests/
├── unit/
�?  ├── __init__.py
�?  ├── conftest.py              # 共享fixtures
�?  �?
�?  ├── core/                    # core模块测试
�?  �?  ├── test_base.py
�?  �?  └── test_exceptions.py
�?  �?
�?  ├── modules/                 # modules模块测试
�?  �?  ├── test_datahub.py
�?  �?  ├── test_factor_calculator.py
�?  �?  ├── test_risk_manager.py
�?  �?  ├── test_alert_manager.py
�?  �?  └── test_strategy_engine.py
�?  �?
�?  ├── strategies/              # 策略测试
�?  �?  ├── test_s001_trend_follow.py
�?  �?  └── test_s002_macd.py
�?  �?
�?  └── utils/                  # 工具测试
�?      ├── test_data_utils.py
�?      └── test_math_utils.py
�?
├── integration/                 # 集成测试
�?  ├── test_data_pipeline.py
�?  ├── test_backtest_pipeline.py
�?  └── test_full_workflow.py
�?
├── fixtures/                   # 测试数据
�?  ├── sample_ohlcv.csv
�?  ├── sample_factors.csv
�?  └── mock_api_response.json
�?
└── pytest.ini                  # pytest配置
```


## 3. 核心实现

### 3.1 共享Fixture

```python
# tests/unit/conftest.py

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

@pytest.fixture(scope="session")
def project_root():
    """项目根目�?""
    return Path(__file__).parent.parent.parent

@pytest.fixture(scope="session")
def sample_ohlcv():
    """标准OHLCV测试数据"""
    dates = pd.date_range("2026-01-01", periods=100, freq="D")
    np.random.seed(42)
    return pd.DataFrame({
        'date': dates,
        'symbol': '000001.SZ',
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 105 + np.random.randn(100).cumsum(),
        'low': 95 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'volume': np.random.uniform(1e6, 1e7, 100)
    })

@pytest.fixture(scope="function")
def sample_factor_data():
    """因子计算测试数据"""
    dates = pd.date_range("2026-01-01", periods=60, freq="D")
    return pd.DataFrame({
        'date': dates,
        'symbol': '000001.SZ',
        'close': 100 + np.random.randn(60).cumsum(),
        'volume': np.random.uniform(1e6, 1e7, 60)
    })

@pytest.fixture(scope="function")
def mock_config():
    """模拟配置"""
    return {
        'data': {
            'cache_dir': '/tmp/test_cache',
            'storage_type': 'memory'
        },
        'risk': {
            'max_position': 0.95,
            'max_drawdown': 0.20
        },
        'factor': {
            'momentum_window': 20,
            'mean_reversion_window': 10
        }
    }

@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    """临时目录"""
    return tmp_path / "test_data"
```

### 3.2 模块测试模板

```python
# tests/unit/modules/test_factor_calculator.py

import pytest
from src.modules.factor_calculator import FactorCalculator

class TestFactorCalculator:
    """因子计算器单元测�?

    索引: TEST.UNIT.001-MOD-001
    """

    @pytest.fixture
    def calculator(self, mock_config):
        """因子计算器实�?""
        return FactorCalculator(mock_config)

    def test_initialization(self, calculator):
        """测试初始�?""
        assert calculator is not None
        assert calculator.config is not None

    def test_calculate_momentum(self, calculator, sample_factor_data):
        """测试动量因子计算"""
        result = calculator.calculate_momentum(
            sample_factor_data,
            window=20
        )

        assert result is not None
        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_factor_data)
        assert not result.isna().all()

    def test_calculate_momentum_insufficient_data(self, calculator):
        """测试数据不足情况"""
        short_data = pd.DataFrame({
            'date': pd.date_range("2026-01-01", periods=5),
            'close': [100, 101, 102, 103, 104],
            'volume': [1e6] * 5
        })

        result = calculator.calculate_momentum(short_data, window=20)
        assert result.isna().all()

    @pytest.mark.parametrize("window,expected_min_periods", [
        (5, 5),
        (10, 10),
        (20, 20)
    ])
    def test_momentum_different_windows(self, calculator, sample_factor_data, window, expected_min_periods):
        """参数化测试：不同窗口"""
        result = calculator.calculate_momentum(sample_factor_data, window=window)
        valid_count = result.notna().sum()
        assert valid_count >= expected_min_periods

    def test_output_range(self, calculator, sample_factor_data):
        """测试输出值范�?""
        result = calculator.calculate_momentum(sample_factor_data, window=20)
        valid_result = result.dropna()

        if len(valid_result) > 0:
            assert valid_result.min() >= -1.0
            assert valid_result.max() <= 1.0

    def test_no_future_lookahead(self, calculator, sample_factor_data):
        """测试无未来函�?""
        for i in range(5, len(sample_factor_data)):
            train_data = sample_factor_data.iloc[:i]
            result = calculator.calculate_momentum(train_data, window=3)

            assert result.iloc[-1] is not None or pd.isna(result.iloc[-1])
```

### 3.3 风险管理器测�?

```python
# tests/unit/modules/test_risk_manager.py

import pytest
from src.modules.risk_manager import RiskManager, Order, Position

class TestRiskManager:
    """风险管理器单元测�?

    索引: TEST.UNIT.001-MOD-002
    """

    @pytest.fixture
    def risk_manager(self, mock_config):
        """风险管理器实�?""
        return RiskManager(mock_config)

    @pytest.fixture
    def sample_positions(self):
        """样本持仓"""
        return [
            Position(symbol='000001.SZ', quantity=1000, avg_price=10.0),
            Position(symbol='000002.SZ', quantity=2000, avg_price=15.0)
        ]

    def test_initialization(self, risk_manager):
        """测试初始�?""
        assert risk_manager is not None
        assert risk_manager.max_position == 0.95

    def test_check_order_within_limits(self, risk_manager, sample_positions):
        """测试订单在限制内"""
        order = Order(
            symbol='000003.SZ',
            action='buy',
            quantity=500,
            price=20.0
        )

        result = risk_manager.check_order(order, sample_positions)
        assert result.approved is True
        assert len(result.violations) == 0

    def test_check_order_exceeds_position_limit(self, risk_manager, sample_positions):
        """测试超过仓位限制"""
        order = Order(
            symbol='000001.SZ',
            action='buy',
            quantity=100000,  # 数量过大
            price=10.0
        )

        result = risk_manager.check_order(order, sample_positions)
        assert result.approved is False
        assert any('position' in v.lower() for v in result.violations)

    def test_calculate_var(self, risk_manager, sample_positions):
        """测试VaR计算"""
        var = risk_manager.calculate_var(sample_positions, confidence=0.95)
        assert var >= 0
        assert isinstance(var, float)

    def test_calculate_portfolio_risk(self, risk_manager, sample_positions):
        """测试组合风险计算"""
        risk_metrics = risk_manager.calculate_portfolio_risk(sample_positions)

        assert 'var_95' in risk_metrics
        assert 'cvar_95' in risk_metrics
        assert 'max_drawdown' in risk_metrics
```


## 4. 测试覆盖目标

### 4.1 覆盖要求

| 模块 | 最低覆盖率 | 目标覆盖�?|
|------|------------|------------|
| core/ | 90% | 95% |
| modules/ | 80% | 90% |
| strategies/ | 75% | 85% |
| utils/ | 85% | 90% |
| **整体** | **70%** | **80%** |

### 4.2 关键测试场景

```
必须覆盖的测试场�?

core/
├── Result类所有方�?
├── Signal类验�?
├── Order类验�?
└── Position类验�?

modules/
├── DataHub: 数据获取、缓存、错误处�?
├── FactorCalculator: 所有因子、边界条件、NaN处理
├── RiskManager: 风控规则、VaR计算、仓位检�?
├── AlertManager: 告警触发、通知发�?
└── StrategyEngine: 信号生成、订单处�?

utils/
├── 数据转换函数
├── 数学计算函数
└── 时间处理函数
```


## 5. pytest配置

### 5.1 pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes

markers =
    slow: marks tests as slow (>10s)
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    smoke: marks tests as smoke tests

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning

[coverage:run]
source = src
omit =
    */tests/*
    */conftest.py
    */__init__.py

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
```


## 6. 执行命令

### 6.1 测试执行

```bash
# 运行所有单元测�?
pytest tests/unit/ -v

# 运行带覆盖率的测�?
pytest tests/unit/ --cov=src --cov-report=html --cov-report=term

# 运行特定模块测试
pytest tests/unit/modules/test_factor_calculator.py -v

# 运行标记的测�?
pytest tests/unit/ -m "not slow" -v

# 生成HTML报告
pytest tests/unit/ --html=report.html --self-contained-html
```

### 6.2 CI集成

```yaml
# .github/workflows/test.yml

name: Unit Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-html

      - name: Run tests with coverage
        run: |
          pytest tests/unit/ --cov=src --cov-report=xml --cov-fail-under=70

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```


## 7. 测试数据管理

### 7.1 Fixture工厂

```python
# tests/unit/fixtures/factories.py

class DataFactory:
    """测试数据工厂"""

    @staticmethod
    def create_ohlcv(
        symbol: str = "000001.SZ",
        days: int = 100,
        start_price: float = 100.0
    ) -> pd.DataFrame:
        """创建OHLCV测试数据"""
        dates = pd.date_range("2026-01-01", periods=days, freq="D")
        np.random.seed(hash(symbol) % 2**32)

        return pd.DataFrame({
            'date': dates,
            'symbol': symbol,
            'open': start_price + np.random.randn(days).cumsum(),
            'high': start_price + 5 + np.random.randn(days).cumsum(),
            'low': start_price - 5 + np.random.randn(days).cumsum(),
            'close': start_price + np.random.randn(days).cumsum(),
            'volume': np.random.uniform(1e6, 1e7, days)
        })

    @staticmethod
    def create_factor_data(
        symbols: List[str],
        dates: int = 60
    ) -> pd.DataFrame:
        """创建多股票因子测试数�?""
        dfs = []
        for symbol in symbols:
            df = DataFactory.create_ohlcv(symbol, dates)
            df['momentum_20'] = df['close'].pct_change(20)
            df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
            dfs.append(df)
        return pd.concat(dfs, ignore_index=True)
```


## 8. 开发任务分�?15h)

| 任务 | 时间 | 交付�?|
|------|------|--------|
| 测试目录结构 | 0.5h | tests/目录 |
| conftest.py fixtures | 1.5h | 共享fixtures |
| core模块测试 | 2h | test_base.py, test_exceptions.py |
| DataHub测试 | 2h | test_datahub.py |
| FactorCalculator测试 | 2.5h | test_factor_calculator.py |
| RiskManager测试 | 2h | test_risk_manager.py |
| AlertManager测试 | 1h | test_alert_manager.py |
| 策略测试 | 1.5h | test_strategies.py |
| pytest配置 | 0.5h | pytest.ini |
| CI集成 | 1h | github/workflows |
| 覆盖率报�?| 0.5h | 报告配置 |


**维护�?*: 清风量化系统
**索引**: `TEST.UNIT.001`
**最后更�?*: 2026-03-29
