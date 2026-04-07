---
module_id: INTEGRATION_TESTING_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - 集成测试
  - 端到端测试
  - 测试环境管理
  - 测试数据管理
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
layer: Layer 5 (测试验证层)
---

# 集成测试框架蓝图

> **核心职责**: 提供完整的集成测试框架，确保模块间协作正确性
> **职责边界**: 
> - ✅ 本文档负责：集成测试、端到端测试、测试环境管理、测试数据管理
> - ❌ 本文档不负责：单元测试（由单元测试框架负责）、性能测试（由性能测试负责）

## 核心定位

负责集成测试框架的设计与构建，实现模块间集成测试、端到端测试、测试环境管理，确保系统各模块协作正确性。

## 设计目标

### 主要目标

1. **集成测试自动化**: 自动发现和执行集成测试用例
2. **测试环境管理**: 管理测试环境，确保环境一致性
3. **测试数据管理**: 管理测试数据，确保数据可重现
4. **端到端测试**: 验证完整业务流程

### 质量目标

- 集成测试覆盖率: ≥70%
- 测试环境一致性: 100%
- 测试数据可重现性: 100%
- 测试自动化率: 100%

## 开源方案选型

### 推荐方案: pytest + Docker + TestContainers

| 属性 | 详情 |
|------|------|
| **pytest** | https://github.com/pytest-dev/pytest |
| **testcontainers** | https://github.com/testcontainers/testcontainers-python |
| **Stars** | 11k+ / 1k+ |
| **License** | MIT |
| **特点** | 容器化集成测试 |

**选择理由**:
1. **容器化测试**: 使用Docker容器隔离测试环境
2. **真实环境**: 测试真实的数据库、消息队列等
3. **易于清理**: 测试后自动清理环境
4. **个人友好**: 适合个人开发者使用
5. **与pytest集成**: 无缝集成现有测试框架

### 备选方案

| 项目 | Stars | 特点 | 推荐度 |
|------|-------|------|--------|
| **pytest-docker** | 300+ | Docker集成测试 | ⭐⭐⭐⭐ |
| **docker-compose** | 32k+ | 多容器编排 | ⭐⭐⭐⭐⭐ |
| **tox** | 3k+ | 多环境测试 | ⭐⭐⭐⭐ |

## 核心功能设计

### 1. 测试环境配置

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  postgres-test:
    image: postgres:15
    environment:
      POSTGRES_DB: zephyr_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5433:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis-test:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  timescaledb-test:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: timeseries_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5434:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_test_data:
```

### 2. 集成测试工具类

```python
import pytest
import docker
import subprocess
import time
from typing import Dict, Any, Optional
from pathlib import Path
import psycopg2
import redis
import requests
from contextlib import contextmanager

class TestEnvironment:
    """测试环境管理器"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.containers = {}
        self.network = None
    
    def start_services(self, compose_file: str = "docker-compose.test.yml"):
        """启动测试服务"""
        subprocess.run(
            ["docker-compose", "-f", compose_file, "up", "-d"],
            check=True
        )
        
        time.sleep(5)
        
        self._wait_for_services()
    
    def stop_services(self, compose_file: str = "docker-compose.test.yml"):
        """停止测试服务"""
        subprocess.run(
            ["docker-compose", "-f", compose_file, "down", "-v"],
            check=True
        )
    
    def _wait_for_services(self, timeout: int = 60):
        """等待服务就绪"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5433,
                    database="zephyr_test",
                    user="test",
                    password="test"
                )
                conn.close()
                
                r = redis.Redis(host="localhost", port=6380)
                r.ping()
                r.close()
                
                return True
            except Exception:
                time.sleep(2)
        
        raise TimeoutError("Services did not become ready in time")
    
    @contextmanager
    def isolated_environment(self):
        """隔离测试环境"""
        try:
            self.start_services()
            yield self
        finally:
            self.stop_services()


class TestDatabase:
    """测试数据库管理器"""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5433,
        database: str = "zephyr_test",
        user: str = "test",
        password: str = "test"
    ):
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
        self.conn = None
    
    def connect(self):
        """连接数据库"""
        self.conn = psycopg2.connect(**self.connection_params)
        self.conn.autocommit = False
        return self.conn
    
    def disconnect(self):
        """断开连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def execute_sql(self, sql: str, params: tuple = None):
        """执行SQL"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.conn.commit()
    
    def execute_script(self, script_path: str):
        """执行SQL脚本"""
        with open(script_path, 'r') as f:
            sql = f.read()
        self.execute_sql(sql)
    
    def clean_tables(self, tables: list):
        """清理表数据"""
        for table in tables:
            self.execute_sql(f"TRUNCATE TABLE {table} CASCADE")
    
    @contextmanager
    def transaction(self):
        """事务上下文"""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise


class TestRedis:
    """测试Redis管理器"""
    
    def __init__(self, host: str = "localhost", port: int = 6380):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
    
    def flush_all(self):
        """清空所有数据"""
        self.client.flushall()
    
    def set_test_data(self, key: str, value: str, ttl: int = None):
        """设置测试数据"""
        if ttl:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)
    
    def get_test_data(self, key: str) -> Optional[str]:
        """获取测试数据"""
        return self.client.get(key)
    
    def close(self):
        """关闭连接"""
        self.client.close()


class TestAPI:
    """测试API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: dict = None):
        """GET请求"""
        response = self.session.get(
            f"{self.base_url}{endpoint}",
            params=params
        )
        return response
    
    def post(self, endpoint: str, data: dict = None, json: dict = None):
        """POST请求"""
        response = self.session.post(
            f"{self.base_url}{endpoint}",
            data=data,
            json=json
        )
        return response
    
    def put(self, endpoint: str, data: dict = None, json: dict = None):
        """PUT请求"""
        response = self.session.put(
            f"{self.base_url}{endpoint}",
            data=data,
            json=json
        )
        return response
    
    def delete(self, endpoint: str):
        """DELETE请求"""
        response = self.session.delete(f"{self.base_url}{endpoint}")
        return response
    
    def wait_for_service(self, timeout: int = 30):
        """等待服务就绪"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.get("/health")
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        
        raise TimeoutError("API service did not become ready in time")


class IntegrationTestFixture:
    """集成测试夹具"""
    
    @pytest.fixture(scope="session")
    def test_environment(self):
        """测试环境夹具"""
        env = TestEnvironment()
        
        with env.isolated_environment():
            yield env
    
    @pytest.fixture(scope="function")
    def test_database(self, test_environment):
        """测试数据库夹具"""
        db = TestDatabase()
        db.connect()
        
        try:
            yield db
        finally:
            db.disconnect()
    
    @pytest.fixture(scope="function")
    def test_redis(self, test_environment):
        """测试Redis夹具"""
        redis_client = TestRedis()
        
        try:
            yield redis_client
        finally:
            redis_client.flush_all()
            redis_client.close()
    
    @pytest.fixture(scope="function")
    def test_api(self, test_environment):
        """测试API夹具"""
        api = TestAPI()
        api.wait_for_service()
        
        yield api
```

### 3. 集成测试用例示例

```python
# tests/integration/test_factor_pipeline.py
import pytest
import pandas as pd
from tests.fixtures.integration import IntegrationTestFixture
from src.factors.factor_engine import FactorEngine
from src.data.data_loader import DataLoader

class TestFactorPipeline(IntegrationTestFixture):
    """因子管道集成测试"""
    
    @pytest.mark.integration
    def test_factor_calculation_with_database(
        self,
        test_database,
        test_redis
    ):
        """测试因子计算与数据库集成"""
        test_database.execute_script("tests/sql/setup_test_data.sql")
        
        data_loader = DataLoader(
            db_connection=test_database.conn,
            redis_client=test_redis.client
        )
        
        ohlcv_data = data_loader.load_ohlcv_data(
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        
        assert not ohlcv_data.empty
        assert len(ohlcv_data) > 0
        
        factor_engine = FactorEngine()
        factors = factor_engine.calculate_all_factors(ohlcv_data)
        
        assert not factors.empty
        assert len(factors.columns) > 0
        
        data_loader.save_factors(factors)
        
        loaded_factors = data_loader.load_factors(
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        
        pd.testing.assert_frame_equal(factors, loaded_factors)
    
    @pytest.mark.integration
    def test_factor_cache_with_redis(
        self,
        test_database,
        test_redis
    ):
        """测试因子缓存与Redis集成"""
        test_database.execute_script("tests/sql/setup_test_data.sql")
        
        data_loader = DataLoader(
            db_connection=test_database.conn,
            redis_client=test_redis.client
        )
        
        ohlcv_data = data_loader.load_ohlcv_data(
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        
        factor_engine = FactorEngine()
        factors = factor_engine.calculate_all_factors(ohlcv_data)
        
        cache_key = "factors:2023-01-01:2023-12-31"
        cached_data = test_redis.get_test_data(cache_key)
        
        assert cached_data is not None
    
    @pytest.mark.integration
    def test_end_to_end_factor_workflow(
        self,
        test_database,
        test_redis,
        test_api
    ):
        """测试端到端因子工作流"""
        test_database.execute_script("tests/sql/setup_test_data.sql")
        
        response = test_api.post(
            "/api/v1/factors/calculate",
            json={
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "factors": ["momentum", "volatility", "value"]
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "task_id" in result
        
        import time
        for _ in range(10):
            status_response = test_api.get(
                f"/api/v1/tasks/{result['task_id']}"
            )
            
            if status_response.json()["status"] == "completed":
                break
            
            time.sleep(2)
        
        assert status_response.json()["status"] == "completed"
        
        factors_response = test_api.get(
            "/api/v1/factors",
            params={
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
        )
        
        assert factors_response.status_code == 200
        factors_data = factors_response.json()
        
        assert len(factors_data["factors"]) > 0
```

### 4. pytest配置

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
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

### 5. GitHub Actions集成

```yaml
# .github/workflows/integration-test.yml
name: Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  integration-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov testcontainers
    
    - name: Start test services
      run: docker-compose -f docker-compose.test.yml up -d
    
    - name: Wait for services
      run: sleep 10
    
    - name: Run integration tests
      run: pytest tests/integration -v --cov=src --cov-report=xml
    
    - name: Stop test services
      run: docker-compose -f docker-compose.test.yml down -v
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: integration
```

## 部署架构

### 本地测试环境

```bash
# 启动测试服务
docker-compose -f docker-compose.test.yml up -d

# 运行集成测试
pytest tests/integration -v

# 运行特定测试
pytest tests/integration/test_factor_pipeline.py -v

# 清理测试环境
docker-compose -f docker-compose.test.yml down -v
```

### CI/CD集成

```yaml
# GitHub Actions自动集成测试
# 每次提交自动运行集成测试
# PR必须通过测试才能合并
```

## 实施计划

### 阶段1: 环境配置 (Day 1)

| 任务 | 工时 | 负责人 | 交付物 |
|------|------|--------|--------|
| Docker配置 | 2h | 开发者 | docker-compose.test.yml |
| 测试工具类 | 3h | 开发者 | 工具类代码 |
| 测试夹具 | 2h | 开发者 | 夹具代码 |

### 阶段2: 测试用例编写 (Day 2)

| 任务 | 工时 | 负责人 | 交付物 |
|------|------|--------|--------|
| 数据库集成测试 | 3h | 开发者 | 测试用例 |
| API集成测试 | 3h | 开发者 | 测试用例 |

### 阶段3: CI/CD集成 (Day 3)

| 任务 | 工时 | 负责人 | 交付物 |
|------|------|--------|--------|
| GitHub Actions配置 | 2h | 开发者 | 工作流文件 |
| 测试报告配置 | 1h | 开发者 | 报告配置 |
| 文档编写 | 1h | 开发者 | 使用文档 |

## 性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| **集成测试覆盖率** | ≥70% | pytest-cov统计 |
| **测试执行时间** | <10分钟 | pytest耗时 |
| **环境启动时间** | <30秒 | Docker启动时间 |
| **测试自动化率** | 100% | CI/CD集成 |

## 成本估算

| 项目 | 开源方案成本 | 商业方案成本 |
|------|-------------|-------------|
| **软件许可** | $0 | $0 |
| **Docker** | 免费 | 免费 |
| **testcontainers** | 免费 | 免费 |
| **总成本** | **$0** | **$0** |

## 最佳实践

### 1. 测试隔离

```python
# 每个测试用例使用独立的数据
@pytest.fixture(autouse=True)
def setup_test_data(test_database):
    test_database.clean_tables(["factors", "ohlcv_data"])
    test_database.execute_script("tests/sql/setup_test_data.sql")
    yield
    test_database.clean_tables(["factors", "ohlcv_data"])
```

### 2. 测试数据管理

```python
# 使用工厂模式创建测试数据
class TestDataFactory:
    @staticmethod
    def create_ohlcv_data(rows: int = 100):
        return pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=rows),
            'open': np.random.randn(rows) * 100,
            'close': np.random.randn(rows) * 100,
            'volume': np.random.randint(1000000, 10000000, rows)
        })
```

### 3. 测试标记

```python
@pytest.mark.integration
def test_database_integration():
    pass

@pytest.mark.e2e
def test_end_to_end_workflow():
    pass

@pytest.mark.slow
def test_large_dataset():
    pass
```

---

**文档版本**: v1.0.0
**创建日期**: 2026-04-07
**最后更新**: 2026-04-07
**状态**: Active
