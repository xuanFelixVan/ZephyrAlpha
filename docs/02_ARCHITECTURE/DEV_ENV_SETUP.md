---
module_id: ARCH_DEV_ENV_SETUP
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P0
---

# ZephyrAlpha 开发环境设置 (Dev Environment Setup)

> **用途**：记录开发环境配置、依赖版本、Docker 配置。修改 pyproject.toml 后必须同步更新本文件。
> **真源**：实际依赖定义在 `pyproject.toml`，本文件是人类可读的补充说明。

---

## 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | ≥ 3.11 | 必须 |
| 包管理 | Poetry 或 pip | 推荐 Poetry |
| Docker | ≥ 24.0 | 用于容器化部署 |
| Git | ≥ 2.40 | 版本控制 |
| pre-commit | ≥ 3.0 | hooks 运行 |

---

## 核心依赖（pyproject.toml 摘要）

| 包 | 版本约束 | 用途 |
|----|---------|------|
| `pydantic` | ≥ 2.0 | 数据验证 |
| `pydantic-settings` | ≥ 2.0 | 配置管理 |
| `structlog` | - | 结构化日志 |
| `tenacity` | - | API 重试 |
| `akshare` | - | A 股数据 |
| `pandas` | - | 数据处理 |
| `numpy` | - | 数值计算 |
| `duckdb` | - | 本地数据库 |

---

## 快速启动

```bash
# 1. 克隆仓库
git clone <repo-url>
cd ZephyrAlpha

# 2. 安装依赖
pip install -e ".[dev]"  # 或 poetry install

# 3. 安装 pre-commit hooks
pre-commit install

# 4. 验证环境
python -c "import zephyr; print('OK')"
pytest src/tests/ -x --cov=src/zephyr --cov-fail-under=80
```

---

## Docker 配置

> 详细 Docker Compose 配置见 `docker-compose.yml`

---

## 变更历史

| 版本 | 日期 | 变更描述 | 变更人 |
|------|------|---------|--------|
| 1.0.0 | 2026-04-16 | 初始创建（骨架，待填充实际版本）| AI |
