---
module_id: ARCH_DEV_ENV_SETUP
version: '1.1.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P0
---

# ZephyrAlpha 开发环境设置 (Dev Environment Setup)

> **用途**：记录开发环境配置、依赖版本、测试配置和 CI/CD 本地模拟指南。
> **真源**：实际依赖定义在 `pyproject.toml`，本文件是人类可读的补充说明。
> **修改触发**：修改 `pyproject.toml` 后必须同步更新本文件的依赖版本表。

---

## 一、环境要求

| 组件 | 版本 | 安装说明 |
|------|------|---------|
| Python | **≥ 3.11**（推荐 3.12） | `pyenv install 3.12.0` |
| pip | ≥ 23.0 | `pip install --upgrade pip` |
| Poetry（可选）| ≥ 1.7 | `pip install poetry` |
| Docker | ≥ 24.0 | 用于 PostgreSQL/TimescaleDB/Redis 容器化 |
| Git | ≥ 2.40 | 版本控制 |
| pre-commit | ≥ 3.6 | `pip install pre-commit` |

---

## 二、核心依赖版本（pyproject.toml 摘要）

| 类别 | 包名 | 版本约束 | 用途 | 相关 ADR |
|------|------|---------|------|---------|
| 数据验证 | `pydantic` | `^2.7` | 数据结构定义与验证 | ADR-003 |
| 数据验证 | `pydantic-settings` | `^2.2` | 多环境配置管理 | ADR-003 |
| 日志 | `structlog` | `^24.1` | 结构化日志（JSON + 控制台）| ADR-001 |
| 重试 | `tenacity` | `^8.3` | API 重试（指数退避）| ADR-002 |
| 数据源 | `akshare` | `^1.14` | A 股 OHLCV 数据（免费）| L00 施工图 |
| 数据处理 | `pandas` | `^2.2` | DataFrame 操作 | — |
| 数据处理 | `numpy` | `^1.26` | 数值计算 | — |
| 数据库 | `duckdb` | `^0.10` | 本地分析型数据库 | ADR-005 |
| 测试 | `pytest` | `^8.1` | 测试框架 | — |
| 测试 | `pytest-cov` | `^5.0` | 代码覆盖率报告 | — |
| 测试 | `pytest-mock` | `^3.12` | Mock 支持 | — |
| 测试 | `pytest-asyncio` | `^0.23` | 异步测试支持 | — |
| 质量 | `mypy` | `^1.10` | 静态类型检查 | — |
| 质量 | `ruff` | `^0.4` | Lint + 格式化（替代 flake8+black）| — |

---

## 三、快速启动

```bash
# 1. 克隆仓库
git clone <repo-url>
cd ZephyrAlpha

# 2. 安装依赖（含开发工具）
pip install -e ".[dev]"
# 或使用 Poetry
poetry install --with dev

# 3. 安装 pre-commit hooks（必须，18 个 hooks 守护代码质量）
pre-commit install
pre-commit install --hook-type commit-msg

# 4. 验证环境
python -c "import zephyr; print('ZephyrAlpha 环境OK')"

# 5. 运行测试（覆盖率 ≥ 80%）
pytest src/tests/ -x --cov=src/zephyr --cov-fail-under=80 -v
```

---

## 四、测试配置

### 4.1 pytest 配置（`pyproject.toml` 中的 `[tool.pytest.ini_options]`）

```toml
[tool.pytest.ini_options]
testpaths = ["src/tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--cov=src/zephyr",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-fail-under=80",
    "-v",
    "--tb=short"
]
asyncio_mode = "auto"
```

### 4.2 测试目录结构

```
src/tests/
├── unit/                   # 单元测试（按 layer 组织）
│   ├── L00_data_source/    # L00 层测试
│   │   └── test_*.py
│   ├── L01_infrastructure/
│   └── ...
├── integration/            # 跨层集成测试
│   └── test_*.py
└── conftest.py             # 公共 fixture
```

### 4.3 覆盖率目标

| 层 | 目标覆盖率 | 说明 |
|----|---------|------|
| L00-M1 AKShare 适配器 | ≥ 80% | 必须覆盖重试逻辑和数据验证 |
| L00-M2 数据规范化 | ≥ 90% | 关键数据质量路径 |
| 所有业务层（L00-L07）| ≥ 80% | Phase 3 实施时强制 |

---

## 五、环境变量与 Secrets 管理

### 5.1 本地开发（`.env` 文件，已 gitignored）

```env
# 数据库配置
ZEPHYR_DB_URL=postgresql://localhost:5432/zephyr
ZEPHYR_DB_POOL_SIZE=10

# Redis 缓存
ZEPHYR_REDIS_URL=redis://localhost:6379/0

# AKShare（通常无需 key）
AKSHARE_TIMEOUT=30

# 日志级别
ZEPHYR_LOG_LEVEL=INFO

# LLM API（ADR-008 待决策，以下为占位）
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

### 5.2 CI/CD 环境变量（GitHub Secrets）

| Secret 名称 | 用途 | 必须 |
|------------|------|------|
| `DB_URL_TEST` | 测试数据库连接串 | Phase 3 实施时 |
| `REDIS_URL_TEST` | 测试 Redis 连接 | Phase 3 实施时 |

**安全规则**：
- 禁止在代码中硬编码任何 key/password
- 使用 `pydantic-settings` 从环境变量加载（已由 ADR-003 决定）
- 本地 `.env` 文件已在 `.gitignore` 中

---

## 六、Docker Compose 本地服务

```yaml
# docker-compose.dev.yml（Phase 3 实施时创建）
services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_DB: zephyr
      POSTGRES_PASSWORD: localdev_only
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**启动本地服务**：
```bash
docker compose -f docker-compose.dev.yml up -d
```

---

## 七、CI/CD 本地模拟

### 7.1 模拟 pre-commit 钩子（所有 18 个钩子）

```bash
# 运行所有 pre-commit 钩子（针对所有文件）
pre-commit run --all-files

# 只运行特定钩子
pre-commit run validate-blueprint-frontmatter --all-files
pre-commit run check-index-links --all-files
```

### 7.2 模拟 CI governance 检查（`governance-audit.yml` 的本地等价）

```bash
# Sentinel L1 扫描
python scripts/audit/sentinel_l1_governance_scan.py

# 索引健康度
python scripts/audit/scan_index_health.py

# 查看结果
cat docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_LATEST.json | python -m json.tool
```

### 7.3 模拟月度/季度审计

```bash
mkdir -p reports

# 月度
python scripts/ci_audit/monthly_audit.py --output reports/MONTHLY_AUDIT_REPORT_$(date +%Y%m).md

# 季度
python scripts/ci_audit/quarterly_audit.py --output reports/QUARTERLY_DEEP_AUDIT_REPORT_$(date +%YQ).md
```

---

## 八、mypy 静态类型配置

```toml
# pyproject.toml 中的 [tool.mypy]
[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
exclude = ["scripts/", "docs/"]
```

**运行方式**：
```bash
mypy src/zephyr/
```

---

## 九、变更历史

| 版本 | 日期 | 变更描述 |
|------|------|---------|
| 1.0.0 | 2026-04-16 | 初始创建（骨架）|
| 1.1.0 | 2026-04-16 | 补全依赖版本、pytest 配置、覆盖率目标、环境变量、CI 本地模拟指南 |
