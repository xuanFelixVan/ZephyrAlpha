---
module_id: SRC_TREE_README_001
version: 1.0.0
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 文档维护者
responsibility:
  - 源码树入口导航（与根 README、架构服务目录生成物互补）
standard_type: 技术说明
applicable_scope: src/
---

# 源码目录 `src/` 导航

运行入口：**`python -m src.main`**（见仓库根 [README.md](../README.md)）。

| 路径 | 说明 |
|------|------|
| [`main.py`](main.py) | CLI / 应用入口 |
| [`api/main.py`](api/main.py) | HTTP 服务装配；路由见 [`api/routes/`](api/routes/)（`health`、`backtest`、`strategies`、`monitoring` 等） |
| [`core/`](core/) | 核心实体、校验、异常与基类 |
| [`engines/`](engines/) | 回测适配器、引擎工厂等 |
| [`modules/`](modules/) | 业务模块（如 `ai_factor_miner`、`economic_regime_engine`、`statistical_arbitrage`、合规与报表类等） |
| [`data/`](data/) | 数据层占位/初始化 |
| [`utils/`](utils/) | 文档治理检查、链接校验、元数据工具等 |

**自动生成、可检索的组件/端点表**：[`docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md`](../docs/09_AUDIT/STATE/ARCHITECTURE_SERVICE_CATALOG_20260410.md)（复跑 `python scripts/governance/generate_architecture_service_catalog.py`）。
