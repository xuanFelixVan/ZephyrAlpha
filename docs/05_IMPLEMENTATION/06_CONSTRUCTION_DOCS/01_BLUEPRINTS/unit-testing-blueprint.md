---

module_id: UNIT_TESTING_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: 2026-04-07

owner: 首席文档架构师

responsibility:

  - 单元测试

  - 测试框架

  - 测试覆盖率

  - 测试自动化

standard_type: 专业量化机构蓝图

compliance_level: 专业标准

layer: layer_05

---



# 单元测试框架蓝图



> **核心职责**: 提供完整的单元测试框架，确保代码质量和功能正确性

> **职责边界**: 

> - ✅ 本文档负责：单元测试、测试框架、测试覆盖率、测试自动化

> - ❌ 本文档不负责：集成测试（由集成测试框架负责）、性能测试（由性能测试负责）



## 核心定位



负责单元测试框架的设计与构建，实现自动化单元测试、测试覆盖率统计、测试报告生成，确保代码质量和功能正确性。



## 接口与契约（蓝图终稿）



本模块遵循系统接口契约，详见：API_Contract.md



### 关键接口

- **测试运行接口**: `pytest` - 测试框架运行命令

- **覆盖率统计接口**: `pytest-cov` - 代码覆盖率统计

- **测试数据生成接口**: `TestDataGenerator` - 测试数据生成器

- **断言工具接口**: `TestAssertions` - 测试断言工具集



## 验收标准（可检查）



- 能够对至少 1 个模块运行测试套件并生成覆盖率报告，覆盖率 ≥ 80%，测试结果可追溯（测试用例数、通过率、失败原因）。



## 已知限制



- 测试覆盖率指标不能完全代表代码质量；实施阶段需在契约真源中固化覆盖率阈值、关键路径测试要求与豁免规则。



## 设计目标



### 主要目标



1. **测试自动化**: 自动发现和执行测试用例

2. **测试覆盖率**: 统计代码覆盖率，确保测试充分性

3. **测试报告**: 生成详细的测试报告

4. **持续集成**: 与CI/CD流程集成



### 质量目标



- 测试覆盖率: ≥80%

- 测试通过率: 100%

- 测试执行时间: <5分钟

- 测试自动化率: 100%



## 开源方案选型



### 推荐方案: pytest



| 属性 | 详情 |

|------|------|

| **GitHub** | https://github.com/pytest-dev/pytest |

| **Stars** | 11k+ |

| **License** | MIT |

| **特点** | Python最流行的测试框架 |



**选择理由**:

1. **简单易用**: 简洁的语法，易于上手

2. **功能强大**: 丰富的插件生态

3. **参数化测试**: 支持参数化测试用例

4. **夹具机制**: 强大的fixture系统

5. **个人友好**: 适合个人开发者使用



### 备选方案



| 项目 | Stars | 特点 | 推荐度 |

|------|-------|------|--------|

| **unittest** | 内置 | Python标准库 | ⭐⭐⭐⭐ |

| **nose2** | 800+ | unittest扩展 | ⭐⭐⭐ |

| **Robot Framework** | 9k+ | 关键字驱动测试 | ⭐⭐⭐⭐ |



## 核心功能设计



### 1. pytest配置文件



```ini

# pytest.ini

[pytest]

testpaths = tests

python_files = test_*.py

python_classes = Test*

python_functions = test_*

addopts = 

    -v

    --strict-markers

    --tb=short

    --cov=src

    --cov-report=html

    --cov-report=term-missing

    --cov-fail-under=80

markers =

    unit: Unit tests

    integration: Integration tests

    slow: Slow running tests

    smoke: Smoke tests

```



### 2. 测试工具类



```python

import pytest

import pandas as pd

import numpy as np

from typing import Any, Dict, List, Callable

from pathlib import Path

import tempfile

import shutil



class TestDataGenerator:

    """测试数据生成器"""

    

    @staticmethod

    def generate_ohlcv_data(

        rows: int = 100,

        start_date: str = "2023-01-01"

    ) -> pd.DataFrame:

        """生成OHLCV测试数据"""

        dates = pd.date_range(start=start_date, periods=rows, freq='D')

        

        np.random.seed(42)

        base_price = 100.0

        prices = base_price + np.random.randn(rows).cumsum()

        

        data = pd.DataFrame({

            'date': dates,

            'open': prices + np.random.randn(rows) * 0.5,

            'high': prices + np.abs(np.random.randn(rows) * 1.0),

            'low': prices - np.abs(np.random.randn(rows) * 1.0),

            'close': prices + np.random.randn(rows) * 0.5,

            'volume': np.random.randint(1000000, 10000000, rows)

        })

        

        return data

    

    @staticmethod

    def generate_factor_data(

        rows: int = 100,

        cols: int = 10

    ) -> pd.DataFrame:

        """生成因子测试数据"""

        np.random.seed(42)

        

        data = pd.DataFrame(

            np.random.randn(rows, cols),

            columns=[f'factor_{i}' for i in range(cols)]

        )

        

        return data

    

    @staticmethod

    def generate_portfolio_data(

        assets: int = 10,

        periods: int = 100

    ) -> pd.DataFrame:

        """生成组合测试数据"""

        np.random.seed(42)

        

        dates = pd.date_range(start='2023-01-01', periods=periods, freq='D')

        asset_names = [f'asset_{i}' for i in range(assets)]

        

        returns = pd.DataFrame(

            np.random.randn(periods, assets) * 0.02,

            index=dates,

            columns=asset_names

        )

        

        return returns





class TestFixture:

    """测试夹具基类"""

    

    @pytest.fixture

    def temp_dir(self):

        """临时目录夹具"""

        temp_path = Path(tempfile.mkdtemp())

        yield temp_path

        shutil.rmtree(temp_path)

    

    @pytest.fixture

    def sample_ohlcv_data(self):

        """样本OHLCV数据夹具"""

        return TestDataGenerator.generate_ohlcv_data()

    

    @pytest.fixture

    def sample_factor_data(self):

        """样本因子数据夹具"""

        return TestDataGenerator.generate_factor_data()

    

    @pytest.fixture

    def sample_portfolio_data(self):

        """样本组合数据夹具"""

        return TestDataGenerator.generate_portfolio_data()





class TestAssertions:

    """测试断言工具"""

    

    @staticmethod

    def assert_dataframe_equal(

        df1: pd.DataFrame,

        df2: pd.DataFrame,

        check_dtype: bool = True,

        check_index: bool = True,

        check_columns: bool = True,

        rtol: float = 1e-5

    ):

        """断言DataFrame相等"""

        if check_columns:

            assert list(df1.columns) == list(df2.columns), \

                f"Columns mismatch: {list(df1.columns)} vs {list(df2.columns)}"

        

        if check_index:

            assert df1.index.equals(df2.index), \

                f"Index mismatch: {df1.index} vs {df2.index}"

        

        if check_dtype:

            assert df1.dtypes.equals(df2.dtypes), \

                f"Dtypes mismatch: {df1.dtypes} vs {df2.dtypes}"

        

        np.testing.assert_allclose(

            df1.values,

            df2.values,

            rtol=rtol,

            err_msg="Values mismatch"

        )

    

    @staticmethod

    def assert_series_equal(

        s1: pd.Series,

        s2: pd.Series,

        check_dtype: bool = True,

        check_index: bool = True,

        rtol: float = 1e-5

    ):

        """断言Series相等"""

        if check_index:

            assert s1.index.equals(s2.index), \

                f"Index mismatch: {s1.index} vs {s2.index}"

        

        if check_dtype:

            assert s1.dtype == s2.dtype, \

                f"Dtype mismatch: {s1.dtype} vs {s2.dtype}"

        

        np.testing.assert_allclose(

            s1.values,

            s2.values,

            rtol=rtol,

            err_msg="Values mismatch"

        )

    

    @staticmethod

    def assert_not_empty(obj: Any):

        """断言对象非空"""

        if isinstance(obj, pd.DataFrame):

            assert not obj.empty, "DataFrame is empty"

        elif isinstance(obj, pd.Series):

            assert not obj.empty, "Series is empty"

        elif isinstance(obj, (list, dict)):

            assert len(obj) > 0, f"{type(obj).__name__} is empty"

        else:

            assert obj is not None, "Object is None"

    

    @staticmethod

    def assert_valid_returns(returns: pd.Series):

        """断言收益率有效"""

        assert not returns.isnull().any(), "Returns contain NaN values"

        assert not np.isinf(returns).any(), "Returns contain infinite values"

        assert isinstance(returns.index, pd.DatetimeIndex), \

            "Returns index must be DatetimeIndex"

    

    @staticmethod

    def assert_valid_weights(weights: pd.Series):

        """断言权重有效"""

        assert not weights.isnull().any(), "Weights contain NaN values"

        assert not np.isinf(weights).any(), "Weights contain infinite values"

        assert abs(weights.sum() - 1.0) < 1e-6, \

            f"Weights must sum to 1.0, got {weights.sum()}"





class TestPerformance:

    """测试性能工具"""

    

    @staticmethod

    def measure_time(func: Callable, *args, **kwargs) -> Dict[str, Any]:

        """测量函数执行时间"""

        import time

        

        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()

        

        return {

            "result": result,

            "execution_time": end_time - start_time

        }

    

    @staticmethod

    def assert_performance(

        func: Callable,

        max_time: float,

        *args,

        **kwargs

    ):

        """断言函数性能"""

        measurement = TestPerformance.measure_time(func, *args, **kwargs)

        

        assert measurement["execution_time"] <= max_time, \

            f"Function took {measurement['execution_time']:.2f}s, " \

            f"expected <= {max_time:.2f}s"

        

        return measurement["result"]





class TestMock:

    """测试Mock工具"""

    

    @staticmethod

    def mock_database_connection():

        """Mock数据库连接"""

        from unittest.mock import MagicMock, patch

        

        mock_conn = MagicMock()

        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor

        

        return mock_conn, mock_cursor

    

    @staticmethod

    def mock_api_response(data: Dict[str, Any], status_code: int = 200):

        """Mock API响应"""

        from unittest.mock import MagicMock

        

        mock_response = MagicMock()

        mock_response.status_code = status_code

        mock_response.json.return_value = data

        

        return mock_response

    

    @staticmethod

    def mock_file_read(content: str):

        """Mock文件读取"""

        from unittest.mock import mock_open, patch

        

        return patch('builtins.open', mock_open(read_data=content))

```



### 3. 测试用例示例



```python

# tests/test_factor_engine.py

import pytest

import pandas as pd

import numpy as np

from src.factors.factor_engine import FactorEngine

from tests.fixtures import TestFixture, TestAssertions, TestDataGenerator



class TestFactorEngine(TestFixture):

    """因子引擎测试"""

    

    @pytest.mark.unit

    def test_factor_calculation(self, sample_ohlcv_data):

        """测试因子计算"""

        engine = FactorEngine()

        

        factor = engine.calculate_momentum(

            data=sample_ohlcv_data,

            window=20

        )

        

        TestAssertions.assert_not_empty(factor)

        assert isinstance(factor, pd.Series)

        assert len(factor) == len(sample_ohlcv_data)

    

    @pytest.mark.unit

    def test_factor_normalization(self, sample_factor_data):

        """测试因子标准化"""

        engine = FactorEngine()

        

        normalized = engine.normalize_factors(sample_factor_data)

        

        TestAssertions.assert_dataframe_equal(

            normalized.shape,

            sample_factor_data.shape

        )

        

        assert normalized.mean().abs().max() < 1e-6

        assert (normalized.std() - 1.0).abs().max() < 1e-6

    

    @pytest.mark.unit

    @pytest.mark.parametrize("window", [5, 10, 20, 60])

    def test_momentum_factor_windows(self, sample_ohlcv_data, window):

        """测试不同窗口的动量因子"""

        engine = FactorEngine()

        

        factor = engine.calculate_momentum(

            data=sample_ohlcv_data,

            window=window

        )

        

        assert len(factor) == len(sample_ohlcv_data)

        assert not factor.isnull().all()

    

    @pytest.mark.unit

    def test_factor_neutralization(self, sample_factor_data):

        """测试因子中性化"""

        engine = FactorEngine()

        

        industry_dummy = pd.get_dummies(

            np.random.randint(0, 5, len(sample_factor_data))

        )

        

        neutralized = engine.neutralize_factors(

            factors=sample_factor_data,

            industry_dummy=industry_dummy

        )

        

        TestAssertions.assert_dataframe_equal(

            neutralized.shape,

            sample_factor_data.shape

        )

    

    @pytest.mark.slow

    def test_large_dataset_performance(self):

        """测试大数据集性能"""

        large_data = TestDataGenerator.generate_ohlcv_data(rows=10000)

        engine = FactorEngine()

        

        result = TestPerformance.assert_performance(

            engine.calculate_momentum,

            max_time=1.0,

            data=large_data,

            window=20

        )

        

        assert len(result) == 10000

```



### 4. GitHub Actions集成



```yaml

# .github/workflows/test.yml

name: Unit Tests



on:

  push:

    branches: [ main, develop ]

  pull_request:

    branches: [ main ]



jobs:

  test:

    runs-on: ubuntu-latest

    strategy:

      matrix:

        python-version: [3.9, 3.10, 3.11]

    

    steps:

    - uses: actions/checkout@v4

    

    - name: Set up Python ${{ matrix.python-version }}

      uses: actions/setup-python@v4

      with:

        python-version: ${{ matrix.python-version }}

    

    - name: Cache dependencies

      uses: actions/cache@v3

      with:

        path: ~/.cache/pip

        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

        restore-keys: |

          ${{ runner.os }}-pip-

    

    - name: Install dependencies

      run: |

        python -m pip install --upgrade pip

        pip install -r requirements.txt

        pip install pytest pytest-cov pytest-xdist

    

    - name: Run unit tests

      run: pytest tests/unit -v --cov=src --cov-report=xml --cov-report=html -n auto

    

    - name: Upload coverage to Codecov

      uses: codecov/codecov-action@v3

      with:

        file: ./coverage.xml

        flags: unittests

        name: codecov-umbrella

        fail_ci_if_error: true

    

    - name: Archive test results

      uses: actions/upload-artifact@v3

      with:

        name: test-results

        path: |

          coverage.xml

          htmlcov/

```



## 部署架构



### 本地测试环境



```bash

# 安装测试依赖

pip install pytest pytest-cov pytest-xdist pytest-asyncio



# 运行所有测试

pytest tests/



# 运行单元测试

pytest tests/unit -v



# 运行特定测试文件

pytest tests/test_factor_engine.py -v



# 运行带标记的测试

pytest -m unit tests/

pytest -m "not slow" tests/



# 生成覆盖率报告

pytest --cov=src --cov-report=html tests/



# 并行测试

pytest -n auto tests/

```



### CI/CD集成



```yaml

# GitHub Actions自动测试

# 每次提交自动运行测试

# PR必须通过测试才能合并

# 自动生成覆盖率报告

```



## 实施计划



### 阶段1: 基础配置 (Day 1)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| 安装pytest | 0.5h | 开发者 | pytest安装 |

| 创建pytest.ini | 0.5h | 开发者 | 配置文件 |

| 创建测试目录结构 | 1h | 开发者 | 目录结构 |

| 编写测试工具类 | 2h | 开发者 | 工具类 |



### 阶段2: 测试用例编写 (Day 2)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| 因子引擎测试 | 2h | 开发者 | 测试用例 |

| 策略引擎测试 | 2h | 开发者 | 测试用例 |

| 数据处理测试 | 2h | 开发者 | 测试用例 |



### 阶段3: CI/CD集成 (Day 2)



| 任务 | 工时 | 负责人 | 交付物 |

|------|------|--------|--------|

| GitHub Actions配置 | 1h | 开发者 | 工作流文件 |

| Codecov集成 | 0.5h | 开发者 | Codecov配置 |

| 测试报告配置 | 0.5h | 开发者 | 报告配置 |



## 性能指标



| 指标 | 目标值 | 测量方法 |

|------|--------|---------|

| **测试覆盖率** | ≥80% | pytest-cov统计 |

| **测试通过率** | 100% | 测试结果 |

| **测试执行时间** | <5分钟 | pytest耗时 |

| **测试自动化率** | 100% | CI/CD集成 |



## 成本估算



| 项目 | 开源方案成本 | 商业方案成本 |

|------|-------------|-------------|

| **软件许可** | $0 | $0 |

| **pytest** | 免费 | 免费 |

| **Codecov** | 免费（公开仓库） | $0-$50/月 |

| **总成本** | **$0** | **$0-$50/月** |



## 最佳实践



### 1. 测试命名规范



```python

# 测试文件命名

test_factor_engine.py



# 测试类命名

class TestFactorEngine:



# 测试方法命名

def test_factor_calculation(self):

def test_factor_normalization(self):

def test_invalid_input_raises_error(self):

```



### 2. 测试组织结构



```

tests/

├── unit/              # 单元测试

│   ├── test_factors/

│   ├── test_strategy/

│   └── test_data/

├── integration/       # 集成测试

├── fixtures/          # 测试夹具

├── conftest.py        # pytest配置

└── __init__.py

```



### 3. 参数化测试



```python

@pytest.mark.parametrize("input,expected", [

    (1, 2),

    (2, 4),

    (3, 6),

])

def test_double(input, expected):

    assert double(input) == expected

```



---



**文档版本**: v1.0.0

**创建日期**: 2026-04-07

**最后更新**: 2026-04-07

**状态**: Active

