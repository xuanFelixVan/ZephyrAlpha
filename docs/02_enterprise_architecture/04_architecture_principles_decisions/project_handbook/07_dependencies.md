---
ttl: permanent
doc_type: architecture_view
title: 依赖关系 / Dependencies
owner: ZephyrAlpha-Owner
language: zh
---

# 07 · 依赖关系

> 大白话项目现状。层级依赖方向 + 关键链路 + AUTO 边统计 + 外链契约目录。
> 依赖关系真源 = PostgreSQL depgraph DB（非 YAML），AI 查询 depgraph = 零幻觉空间。

## 1. 层级依赖方向

```
shared (paths, errors, types, constants, event_bus)   ← 最底层，无外部依赖
    ↑
infrastructure (cost_tracker, event_store, sla_monitor)
    ↑
data / integration / security / governance / backtest / factor / risk
    ↑
trading (AutoRuntimeCore)   ← 顶层，组合所有子组件
```

> `shared.io.paths.REPO_ROOT` / `DB_PATH` 是被最广泛 import 的符号。`shared` 禁止 import `integration.*`（向下依赖原则）。

## 2. 量化交易域依赖流

```
market_data (NormalizedMarketData CTR-001)
    → factor (FactorBase → FactorSignal CTR-002)
        → signal_fundamental (AlphaSignalPipeline 合成)
            → risk (RiskLimits CTR-003 约束)
                → pf_core (StrategyBase 目标权重)
                    → ex_core (ExecutionEngine → Fill CTR-005)
                        → backtest (镜像实盘路径 + DecisionGate 门控)
```

## 3. 治理域依赖流

```
governance/ (桥接层, G-CT-001~008 契约)
    ├─ gov_audit (审计追踪, 漂移/脚本发现的汇聚点)
    ├─ gov_drift (漂移检测 → 发现回流 gov_audit)
    ├─ gov_enforcement (规则执行, ~80 commit_gates + GitCommitGateway + session_worktree)
    ├─ gov_rule / gov_code_quality (迁移子域)
    └─ scripts/governance/ (12 维审计扫描, 消费治理事实)
```

## 4. 依赖边统计（AUTO）

<!-- AUTO-START:edge_stats -->
<!-- 数据源：depgraph (PostgreSQL) | 最后同步：2026-08-17 -->

| dep_type | 边数 / Edges |
|----------|------|
| `import_depends` | 5463 |
| `test_depends` | 4139 |
| `import` | 2756 |
| `config_depends` | 497 |
| `data` | 49 |
| `runtime` | 40 |
| `contract` | 6 |
| `event` | 3 |
| **合计 / Total** | **12953** |

**跨域边 / Cross-domain edges：3385** 条（两端节点 domain_id 不同的依赖边）。
<!-- AUTO-END:edge_stats -->

> 节点/域总数见 [01_overview.md](01_overview.md) 的 `dependency_stats` AUTO 块。

## 5. 外部依赖（pyproject.toml）

外部依赖表见 [01_overview.md](01_overview.md) 的 `external_deps` AUTO 块（由生成器从 `pyproject.toml [project.dependencies]` 同步）。

技术栈：Python 3.12+ / Pydantic v2 / asyncio / PostgreSQL+ClickHouse+DuckDB+ChromaDB+SQLite / APScheduler / SQLAlchemy 2.x / OpenAI SDK（经 LSG）/ sentence-transformers（BGE-M3）/ Panel+HoloViz+plotly_resampler / structlog / ruff / mypy / pytest。

## 6. 外部权威源（全量依赖明细）

| 权威源 | 内容 | 路径 |
|--------|------|------|
| 契约目录 | 全接口契约（CTR-001~005、G-CT-001~008 等） | `docs/02_enterprise_architecture/01_global_architecture_diagram/contract_catalog.md` |
| 跨域矩阵 | 域间依赖矩阵 | `docs/02_enterprise_architecture/01_global_architecture_diagram/cross_domain_matrix.md` |
| 集成拓扑 | 外部集成点 | `docs/02_enterprise_architecture/01_global_architecture_diagram/integration_topology.md` |
| 全景对齐 | 全景孤儿/漂移检测 | `docs/02_enterprise_architecture/generated/panorama_alignment_report.md` |

> 依赖全景能力定位（双态/SSoT/生成器）见 [../panorama/dependency_path_panorama.md](../panorama/dependency_path_panorama.md)。
