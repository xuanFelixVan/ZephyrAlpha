---
module_id: DOCKER_SETUP
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: RESEARCH_DOCKER_SETUP_001
version: 1.0.1
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构?
responsibility:
  - 扩展功能、辅助模块、支撑文档
standard_type: 专业量化机构研究标准
applicable_scope: 量化研究实验
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行?
---
---


# Docker 研究环境设置
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> 容器化研究环境，确保环境一致性和隔离?

---

## 1. 设计目标

| 目标 | 说明 |
|------|------|
| 环境隔离 | 每个研究项目独立的Python环境和依?|
| 可复现?| 6个月后仍能准确复现研究结?|
| 快速启?| 新成员可?分钟内搭建好研究环境 |

---

## 2. Docker 配置

### 2.1 Dockerfile 结构

```dockerfile
FROM python:3.10-slim

WORKDIR /workspace

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git curl vim \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Jupyter
RUN pip install jupyterlab notebook

# 默认启动 JupyterLab
EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888"]
```

### 2.2 docker-compose.yml

```yaml
version: '3.8'

services:
  research:
    build: .
    volumes:
      - ../data:/workspace/data
      - ../notebooks:/workspace/notebooks
      - ../src:/workspace/src
    ports:
      - "8888:8888"
    environment:
      - PYTHONPATH=/workspace

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: quant_research
      POSTGRES_USER: quant
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  pgdata:
```

---

## 3. 研究项目模板

### 3.1 标准项目结构

```
research_project/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config/
?  └── project.yaml
├── data/
?  ├── raw/
?  ├── processed/
?  └── cache/
├── notebooks/
?  ├── 01_exploration/
?  ├── 02_factor_development/
?  └── 03_backtest/
├── src/
?  ├── factors/
?  ├── strategies/
?  └── utils/
└── reports/
    └── figures/
```

### 3.2 project.yaml 配置

```yaml
project:
  name: "因子研究_YYYYMMDD"
  version: "1.0.0"
  author: "研究员姓?
  created: "2026-03-28"

environment:
  python_version: "3.10"
  key_packages:
    - pandas>=2.0.0
    - numpy>=1.24.0
    - scikit-learn>=1.3.0

data_sources:
  - name: "akshare"
    version: "1.12.0"
  - name: "baostock"
    version: "0.8.8"

reproducibility:
  docker_image: "qingfeng/research:v1.0.0"
  conda_env: "quant_research"
```

---

## 4. 依赖管理

### 4.1 requirements.txt 规范

```txt
# 核心依赖（固定版本）
pandas==2.2.0
numpy==1.26.0
scipy==1.11.0

# 数据获取
akshare==1.12.0
baostock==0.8.8

# 因子研究
scikit-learn==1.3.0
statsmodels==0.14.0

# 可视?
matplotlib==3.7.0
seaborn==0.12.0
plotly==5.15.0

# Jupyter
jupyterlab==4.0.0
ipykernel==6.25.0
```

### 4.2 依赖版本锁定

```bash
# 导出当前环境的所有依?
pip freeze > requirements_locked.txt

# 仅导出项目直接依?
pip-compile --output-file requirements_locked.txt requirements.in
```

---

## 5. 工作流编?

### 5.1 Prefect 工作?

```python
from prefect import flow, task
from prefect.docker import DockerContainer

@task
def fetch_data(date: str):
    """数据获取任务"""
    ...

@task
def calculate_factors(data):
    """因子计算任务"""
    ...

@task
def run_backtest(factors):
    """回测任务"""
    ...

@flow
def research_pipeline(start_date: str, end_date: str):
    """完整研究流水?""
    data = fetch_data(date=start_date)
    factors = calculate_factors(data)
    results = run_backtest(factors)
    return results
```

### 5.2 Dagster 工作?

```python
from dagster import job, op

@op
def extract_data():
    """数据提取"""
    return ...

@op
def transform_data(data):
    """数据转换"""
    return ...

@job
def research_job():
    transform_data(extract_data())
```

---

## 6. 环境变量

```bash
# .env.research
RESEARCH_MODE=development
DATA_DIR=/workspace/data
REDIS_HOST=redis
POSTGRES_HOST=postgres
POSTGRES_DB=quant_research
LOG_LEVEL=INFO
```

---

## 7. 快速开?

```bash
# 1. 克隆项目
git clone <project_repo>
cd research_project

# 2. 启动环境
docker-compose up -d

# 3. 进入容器
docker-compose exec research bash

# 4. 启动 Jupyter
jupyter lab --ip=0.0.0.0

# 5. 打开浏览?
# http://localhost:8888
```

---

## 8. 相关文档

| 文档 | 说明 |
|------|------|
|  | 依赖管理详细规范 |
|  | 工作流编?|
| [../02_EXPLORATORY_ANALYSIS/statistical_tools.md](07_RESEARCH/02_EXPLORATORY_ANALYSIS/statistical_tools.md) | 统计分析工具 |

---

**版本**: 1.0 | **更新**: 2026-03-28
