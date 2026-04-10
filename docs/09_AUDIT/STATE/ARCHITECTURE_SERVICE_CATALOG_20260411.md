---
standard_type: audit_state
applicable_scope: 架构服务目录（生成物）
generated_date: '20260411'
generated_by: scripts/governance/generate_architecture_service_catalog.py
---

# 架构服务目录与 C4 摘要（自动生成）

> **机器真源**：[`ARCHITECTURE_SERVICE_CATALOG_20260411.json`](./ARCHITECTURE_SERVICE_CATALOG_20260411.json)
> **复跑**：仓库根 `python scripts/governance/generate_architecture_service_catalog.py`
> **叙事与裁决**仍以 [`docs/01_FRAMEWORK/ARCHITECTURE.md`](../../01_FRAMEWORK/ARCHITECTURE.md)、[`docs/System_Manifest.md`](../../System_Manifest.md) 等为真源；本文仅**从代码/元数据推导**的索引视图。

## 1. 项目元数据（pyproject）

| 键 | 值 |
|---|---|
| name | `quant-system-v5` |
| version | `5.1.0` |
| requires-python | `>=3.10` |
| license | `MIT` |

## 2. C4 — Context（上下文）

量化交易与策略研究系统；用户含研究员/运营/自动化客户端；对外契约见 API_Contract 与 OpenAPI。

- **对外契约**： [`docs/03_TRADING_TACTICS/API_Contract.md`](../../03_TRADING_TACTICS/API_Contract.md)（存在：**是**）

## 3. C4 — Containers（容器）

### python_application

- **technology**：Python >=3.10
- **path**：src/
- **entry_cli**：python -m src.main
- **role**：领域逻辑、引擎、模块

### http_api

- **technology**：FastAPI (optional extra `api`)
- **path**：src/api/
- **entry**：src/api/main.py
- **role**：REST/OpenAPI 服务

## 4. C4 — Components（组件 / HTTP 端点摘录）

### `backtest` ← `src/api/routes/backtest.py`

- **url_prefix**：`/api/backtest`
- **endpoints**：
  - `POST` `/api/backtest/run`
  - `GET` `/api/backtest/results/{backtest_id}`
  - `GET` `/api/backtest/results/{backtest_id}/trades`
  - `GET` `/api/backtest/results/{backtest_id}/equity`

### `health` ← `src/api/routes/health.py`

- **url_prefix**：`(none)`
- **endpoints**：
  - `GET` `/health`
  - `GET` `/health/ready`
  - `GET` `/health/live`

### `monitoring` ← `src/api/routes/monitoring.py`

- **url_prefix**：`/api/monitoring`
- **endpoints**：
  - `GET` `/api/monitoring/system`
  - `GET` `/api/monitoring/trading`
  - `GET` `/api/monitoring/risk`
  - `GET` `/api/monitoring/alerts`
  - `GET` `/api/monitoring/dashboard`

### `strategies` ← `src/api/routes/strategies.py`

- **url_prefix**：`/api/strategies`
- **endpoints**：
  - `GET` `/api/strategies/`
  - `GET` `/api/strategies/{strategy_id}`
  - `POST` `/api/strategies/`
  - `PUT` `/api/strategies/{strategy_id}`
  - `DELETE` `/api/strategies/{strategy_id}`

## 5. `src/` 目录组件平面表（按文件夹 Python 文件数）

| 路径前缀 | .py 文件数 |
|---|---:|
| `src/api` | 2 |
| `src/api/routes` | 5 |
| `src/core` | 5 |
| `src/data` | 1 |
| `src/engines` | 4 |
| `src/modules` | 16 |
| `src/modules/ai_factor_miner` | 7 |
| `src/modules/ai_factor_miner/examples` | 1 |
| `src/modules/economic_regime_engine` | 4 |
| `src/modules/economic_regime_engine/examples` | 1 |
| `src/modules/economic_regime_engine/tests` | 1 |
| `src/modules/examples` | 1 |
| `src/modules/statistical_arbitrage` | 2 |
| `src/modules/statistical_arbitrage/examples` | 1 |
| `src/utils` | 6 |

## 6. 根目录相对专业机构常见缺口（自检表）

| 项 | 说明 |
|---|---|
| **LICENSE** | 根目录许可证文件（与 pyproject 声明一致，便于 GitHub/GitLab 识别）；**状态**：已存在 |
| **CONTRIBUTING.md** | 贡献流程、PR、代码风格入口；**状态**：已存在 |
| **SECURITY.md（根目录）** | 漏洞上报渠道（GitHub Security 推荐）；细则可在 docs 展开；**状态**：已存在 |
| **Dockerfile / compose** | 可复现运行与 CI 镜像；**状态**：当前仓库未检出 |
| **CODEOWNERS** | 按路径自动评审人；**状态**：当前仓库未检出 |
| **.python-version / 工具链钉扎** | 与 pyproject requires-python 对齐的可选文件；**状态**：可选 |

> 说明：表中「已补」以**本仓库目标态**为准；若某文件尚未提交，以 `git ls-files` 根目录为准更新本生成物。
