---
module_id: IMPL_GUIDE_001
version: 1.1.0
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

# 测试规范 (TESTING_STANDARD.md)

> 本文档定义了清风量化交易系统4.0的测试标准，包括单元测试、集成测试、回测验证、策略验证等测试规范�?

---

## 1. 测试分层架构

### 1.1 测试金字�?

```markdown
         /\
        /  \
       / 🔴 \      端到端测�?(E2E)
      / 🟠   \     集成测试 (Integration)
     / 🟡     \    组件测试 (Component)
    /──────────\
   / 单元测试   \   单元测试 (Unit)
  /______________\

  比例: 70% 单元 / 20% 集成 / 10% E2E
```

### 1.2 测试分类

| 测试类型 | 简�?| 覆盖目标 | 执行频率 |
|----------|------|----------|----------|
| 单元测试 | UT | 函数、类、模�?| 每次提交 |
| 集成测试 | IT | 模块间交�?| 每日 |
| 回测验证 | BVT | 策略回测结果 | 每次发布 |
| 系统测试 | ST | 完整业务流程 | 每周 |

---

## 2. 单元测试规范

### 2.1 测试文件结构

```python
# 测试目录结构

tests/
├── unit/                    # 单元测试
�?  ├── factors/
�?  �?  ├── test_trend_factor.py
�?  �?  ├── test_mean_reversion.py
�?  �?  └── test_momentum.py
�?  ├── risk/
�?  �?  ├── test_risk_calculator.py
�?  �?  └── test_position_sizer.py
�?  └── data/
�?      ├── test_data_fetcher.py
�?      └── test_data_validator.py
�?
├── integration/            # 集成测试
�?  ├── test_factor_pipeline.py
�?  └── test_backtest_pipeline.py
�?
└── fixtures/               # 测试数据
    ├── sample_data.csv
    └── mock_api_response.json
```

### 2.2 单元测试模板

```python
# tests/unit/factors/test_trend_factor.py

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.factors.trend_factor import TrendFactor


class TestTrendFactor:
    """趋势因子单元测试"""

    @pytest.fixture
    def sample_data(self):
        """测试数据 fixture"""
        dates = pd.date_range("2026-01-01", periods=100, freq="D")
        return pd.DataFrame({
            "date": dates,
            "open": np.random.uniform(100, 110, 100),
            "high": np.random.uniform(110, 120, 100),
            "low": np.random.uniform(90, 100, 100),
            "close": np.random.uniform(100, 110, 100),
            "volume": np.random.uniform(1e6, 1e7, 100),
        })

    @pytest.fixture
    def factor(self):
        """因子实例 fixture"""
        return TrendFactor(
            short_window=5,
            long_window=20,
            min_periods=10
        )

    def test_initialization(self, factor):
        """测试因子初始�?""
        assert factor.short_window == 5
        assert factor.long_window == 20
        assert factor.min_periods == 10

    def test_calculate_with_valid_data(self, factor, sample_data):
        """测试有效数据计算"""
        result = factor.calculate(sample_data)

        assert isinstance(result, pd.Series)
        assert len(result) == len(sample_data)
        assert result.name == "trend_signal"
        assert result.notna().sum() > 0

    def test_calculate_with_insufficient_data(self, factor):
        """测试数据不足情况"""
        short_data = pd.DataFrame({
            "date": pd.date_range("2026-01-01", periods=5),
            "close": [100, 101, 102, 103, 104],
        })

        result = factor.calculate(short_data)
        assert result.isna().all()

    def test_output_range(self, factor, sample_data):
        """测试输出值范�?""
        result = factor.calculate(sample_data)
        valid_result = result.dropna()

        assert valid_result.min() >= -1.0
        assert valid_result.max() <= 1.0

    @pytest.mark.parametrize("short,long", [
        (5, 20), (10, 30), (20, 60)
    ])
    def test_different_window_combinations(self, short, long, sample_data):
        """参数化测试：不同窗口组合"""
        factor = TrendFactor(short_window=short, long_window=long)
        result = factor.calculate(sample_data)

        assert len(result) == len(sample_data)
```

---

## 3. 集成测试规范

### 3.1 回测流水线集成测�?

```python
# tests/integration/test_backtest_pipeline.py

import pytest
from datetime import datetime
from src.backtest.engine import BacktestEngine
from src.data.his_data import HistoricalDataManager
from src.risk.risk_manager import RiskManager


class TestBacktestPipeline:
    """回测流水线集成测�?""

    @pytest.fixture
    def backtest_config(self):
        return {
            "strategy_id": "S001",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "initial_cash": 1000000,
            "commission": 0.0003,
        }

    def test_full_pipeline_execution(self, backtest_config):
        """测试完整流水线执�?""
        engine = BacktestEngine(backtest_config)

        result = engine.run()

        assert result is not None
        assert "trades" in result
        assert "positions" in result
        assert "equity_curve" in result
        assert result["final_value"] > 0

    def test_data_feeding_integration(self, backtest_config):
        """测试数据供给集成"""
        engine = BacktestEngine(backtest_config)
        data_manager = HistoricalDataManager()

        data = data_manager.get_data(
            stock_code="000001",
            start_date=backtest_config["start_date"],
            end_date=backtest_config["end_date"]
        )

        assert len(data) > 0
        assert "close" in data.columns

    def test_risk_management_integration(self, backtest_config):
        """测试风险管理集成"""
        engine = BacktestEngine(backtest_config)
        risk_manager = RiskManager(max_position=0.95)

        signals = [
            {"stock_code": "000001", "direction": "buy", "volume": 1000},
            {"stock_code": "000002", "direction": "buy", "volume": 2000},
        ]

        filtered = risk_manager.filter_signals(signals)

        assert len(filtered) <= len(signals)
```

---

## 4. 回测验证规范

### 4.1 回测结果验证清单

```python
# tests/validation/test_backtest_validation.py

class BacktestValidator:
    """回测结果验证�?""

    @staticmethod
    def validate_result(result: dict) -> ValidationReport:
        """验证回测结果的完整性和合理�?""

        checks = []

        # 1. 数据完整性检�?
        checks.append(ValidationCheck(
            name="数据完整�?,
            passed=result.get("trades") is not None,
            message="交易记录存在"
        ))

        # 2. 收益率合理性检�?
        total_return = result.get("total_return", 0)
        checks.append(ValidationCheck(
            name="收益率合理�?,
            passed=-10.0 <= total_return <= 100.0,
            message=f"总收益率 {total_return:.2%} 在合理范�?
        ))

        # 3. 最大回撤检�?
        max_drawdown = result.get("max_drawdown", 0)
        checks.append(ValidationCheck(
            name="最大回撤检�?,
            passed=max_drawdown <= 0.5,  # 不超�?0%
            message=f"最大回�?{max_drawdown:.2%} 可接�?
        ))

        # 4. 胜率检�?
        win_rate = result.get("win_rate", 0)
        checks.append(ValidationCheck(
            name="胜率检�?,
            passed=0.1 <= win_rate <= 0.9,  # 10%-90%之间
            message=f"胜率 {win_rate:.2%} 合理"
        ))

        return ValidationReport(checks=checks)
```

### 4.2 回测参数验证

```markdown
## 回测参数验证标准

| 参数 | 合理范围 | 异常检�?|
|------|----------|----------|
| 初始资金 | 10,000 - 100,000,000 | < 最低门槛或 > 异常�?|
| 收益�?| -100% ~ +1000% | > 1000% 标记可疑 |
| 最大回�?| 0% ~ 100% | > 50% 警告 |
| 夏普比率 | -10 ~ +10 | 绝对�?> 10 异常 |
| 交易次数 | > 0 | = 0 表示无交�?|
| 胜率 | 0% ~ 100% | < 5% �?> 95% 可疑 |
```

---

## 5. 策略验证规范

### 5.1 策略正确性验�?

```python
# tests/validation/test_strategy_validation.py

class StrategyValidator:
    """策略验证�?""

    def validate_signal_generation(self, strategy, historical_data):
        """验证信号生成逻辑"""

        signals = strategy.generate_signals(historical_data)

        for signal in signals:
            assert signal.direction in ["buy", "sell", "hold"]
            assert 0.0 <= signal.strength <= 1.0
            assert signal.stock_code is not None
            assert signal.timestamp is not None

    def validate_no_future_lookahead(self, strategy, historical_data):
        """验证无未来函�?""

        for i in range(len(historical_data)):
            train_data = historical_data[:i+1]
            signal = strategy.generate_signals(train_data)

            assert signal.generated_at <= historical_data.index[i]

    def validate_position_limits(self, strategy, signals, max_position=0.95):
        """验证仓位限制"""

        for signal in signals:
            if signal.direction == "buy":
                assert signal.volume * signal.price <= max_position
```

### 5.2 策略绩效基准

```markdown
## 策略绩效评估基准

| 指标 | 合格 | 良好 | 优秀 |
|------|------|------|------|
| 年化收益�?| > 0% | > 10% | > 20% |
| 夏普比率 | > 0.5 | > 1.0 | > 1.5 |
| 最大回�?| < 30% | < 20% | < 10% |
| 胜率 | > 40% | > 50% | > 55% |
| 盈亏�?| > 1.0 | > 1.5 | > 2.0 |
| 日均交易次数 | < 50 | < 20 | < 10 |
```

---

## 6. 测试数据规范

### 6.1 测试数据管理

```python
# tests/conftest.py

import pytest
import pandas as pd
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def sample_ohlcv(test_data_dir):
    """标准OHLCV测试数据"""
    csv_path = test_data_dir / "sample_ohlcv.csv"
    return pd.read_csv(csv_path, parse_dates=["date"])

@pytest.fixture
def mock_api_response(test_data_dir):
    """Mock API响应"""
    import json
    with open(test_data_dir / "mock_api_response.json") as f:
        return json.load(f)
```

---

## 7. 测试执行规范

### 7.1 测试命令

```bash
# 运行所有测�?
pytest tests/

# 运行单元测试
pytest tests/unit/ -v

# 运行带覆盖率的测�?
pytest tests/ --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/unit/factors/test_trend_factor.py -v

# 运行标记的测�?
pytest tests/ -m "not slow"  # 跳过慢速测�?
pytest tests/ -m "integration"  # 只运行集成测�?

# 生成测试报告
pytest tests/ --html=report.html --self-contained-html
```

### 7.2 测试标记

```python
import pytest

# 标记定义
pytest.mark.unit = "单元测试"
pytest.mark.integration = "集成测试"
pytest.mark.slow = "慢速测�?>10s)"
pytest.mark.backtest = "回测相关"
pytest.mark.weekly = "每周执行"
```

---

## 8. CI/CD 测试集成

### 8.1 GitHub Actions 配置

```yaml
# .github/workflows/test.yml

name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=src

  integration-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Run integration tests
        run: pytest tests/integration/ -v

  backtest-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backtest validation
        run: pytest tests/ -m backtest -v
```

---

## 9. 测试覆盖目标

### 9.1 覆盖率要�?

```markdown
## 模块覆盖率目�?

| 模块 | 最低覆盖率 | 目标覆盖�?|
|------|------------|------------|
| core/ | 90% | 95% |
| factors/ | 80% | 90% |
| risk/ | 85% | 90% |
| backtest/ | 75% | 85% |
| data/ | 70% | 80% |
| trade/ | 70% | 80% |

## 覆盖率检查命�?

pytest tests/ --cov=src --cov-fail-under=70
```

---

## 附录: 相关文档

| 文档 | 说明 |
|------|------|
| `CODE_QUALITY.md` | 代码质量标准 |
| `ERROR_HANDLING.md` | 错误处理规范 |
| `CONFIG_STANDARD.md` | 配置文件标准 |

---

## 10. 系统验证标准

### 10.1 目录结构一致性验�?

```python
# tests/validation/test_directory_structure.py

import pytest
from pathlib import Path

class DirectoryStructureValidator:
    """目录结构一致性验证器"""

    EXPECTED_DIRS = [
        "src/core",
        "src/modules",
        "src/utils",
        "config",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        "docs",
        "data/cache",
        "logs",
    ]

    EXPECTED_FILES = [
        "src/__init__.py",
        "src/main.py",
        "config/system.yaml",
        "requirements.txt",
        ".gitignore",
    ]

    @staticmethod
    def validate_structure(root_path: Path) -> ValidationReport:
        """验证目录结构是否符合规范"""
        checks = []

        for dir_path in DirectoryStructureValidator.EXPECTED_DIRS:
            full_path = root_path / dir_path
            checks.append(ValidationCheck(
                name=f"目录存在: {dir_path}",
                passed=full_path.exists() and full_path.is_dir(),
                message=f"{dir_path} {'�?存在' if full_path.exists() else '�?缺失'}"
            ))

        for file_path in DirectoryStructureValidator.EXPECTED_FILES:
            full_path = root_path / file_path
            checks.append(ValidationCheck(
                name=f"文件存在: {file_path}",
                passed=full_path.exists() and full_path.is_file(),
                message=f"{file_path} {'�?存在' if full_path.exists() else '�?缺失'}"
            ))

        return ValidationReport(checks=checks)
```

### 10.2 功能验证清单

```markdown
## 功能验证检查清�?

### P0 - 必须通过

- [ ] **系统启动测试**: `python src/main.py --mode dev` 无报错退�?
- [ ] **配置加载测试**: 所�?`config/*.yaml` 可正常解�?
- [ ] **数据目录测试**: `data/` �?`logs/` 目录可写
- [ ] **依赖完整性测�?*: `pip install -r requirements.txt` 成功
- [ ] **单元测试**: `pytest tests/unit/ -v` 覆盖�?> 70%

### P1 - 核心功能

- [ ] **回测流水线测�?*: 完整回测可执行并产出结果
- [ ] **因子计算测试**: 因子计算模块返回有效输出
- [ ] **风控模块测试**: 风控规则正确触发
- [ ] **日志系统测试**: 日志正常写入 `logs/`

### P2 - 集成功能

- [ ] **目录结构一致�?*: 验证 docs/ 目录结构完整
- [ ] **文档链接检�?*: 文档内交叉引用有�?
- [ ] **API接口测试**: 核心模块接口可调�?
```

### 10.3 验证执行标准

```bash
# 完整验证命令
python src/main.py --mode dev  # 启动验证
pytest tests/ -v --cov=src     # 单元测试
pytest tests/integration/ -v   # 集成测试

# 目录结构验证
python -c "
from pathlib import Path
import sys

root = Path('.')
expected = ['src/core', 'src/modules', 'config', 'tests/unit']
missing = [d for d in expected if not (root / d).exists()]
if missing:
    print(f'缺失目录: {missing}')
    sys.exit(1)
print('目录结构验证通过')
"
```

---

**版本**: v1.1
**最后更�?*: 2026-03-28
**更新内容**: 新增�?0章系统验证标�?
