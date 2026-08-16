---
module_id: MOD-INF-044
title: Grafana 双数据源仪表盘蓝图
doc_type: blueprint
status: Active
layer: L1_platform
date: "2026-07-22"
version: "0.2.0"
last_updated: "2026-07-22"
ttl: permanent
depends_on:
  - "MOD-INF-016 共享核心（MetricsRegistry 指标来源）"
construction_progress: prototype
language: zh
description: Grafana 双数据源仪表盘——Prometheus（实时 metrics）+ ClickHouse（历史行情/回测），统一可视化 + 告警
build_status: stable
design_maturity: production
responsibility_domain: 
---

# Grafana 双数据源仪表盘蓝图（MOD-INF-044）

> **状态**：P2-10 已施工（prototype），depgraph 节点已登记。
> 施工内容：datasource_config / dashboard_templates / alert_rules 三模块 + 3 个 Dashboard JSON + ClickHouse datasource YAML。
> docker-compose.yml 已添加 grafana-clickhouse-datasource 插件。

---

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-044`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-INF-044` 的 5 个 file 节点 | production | `extract_depgraph.py --modules MOD-INF-044` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-INF-044 | MOD-INF-044 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 5 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 动机

P1-5 完成后，ZephyrAlpha 暴露 `/metrics` 端点（Prometheus 兼容）。但仅有指标数据不够——需要可视化层。

借鉴 BalletHip 的双数据源 Grafana 方案：
- Prometheus 数据源：实时 metrics（tick 速率、队列水位、WAL 积压、CH 写入延迟）
- ClickHouse 数据源：历史行情数据、回测结果、因子 IC/IR

双数据源的优势：同一 Dashboard 可同时展示"系统健康"和"业务数据"，DevOps 和量化研究员共享视图。

## §2 设计要点（占位，施工时细化）

### §2.1 数据源配置

| 数据源 | 类型 | URL | 用途 |
|--------|------|-----|------|
| Prometheus | prometheus | `http://localhost:9090` | 实时 metrics（P1-5 产出） |
| ClickHouse | clickhouse | `http://<VM-IP>:8123` | 历史行情 / 回测结果 |

### §2.2 Dashboard 规划

| Dashboard | 数据源 | 面板 |
|-----------|--------|------|
| 数据采集健康 | Prometheus | tick 接收/写入/丢弃速率、队列水位、WAL 段文件数、WAL 目录大小 |
| ClickHouse 写入健康 | Prometheus | 写入成功率（by outcome）、写入延迟 p50/p99、冷却状态 |
| Drain 健康 | Prometheus | drain 成功/失败速率、积压文件数、WAL 容量水位 |
| 行情数据概览 | ClickHouse | 今日 tick 总量、按 symbol 分布、价格走势 |
| 回测结果 | ClickHouse | 策略收益曲线、回撤、因子 IC/IR |

### §2.3 告警规则

| 告警 | 条件 | 级别 |
|------|------|------|
| tick 丢弃速率高 | `rate(zephyr_tick_dropped_total[5m]) > 10` | Warning |
| 队列水位高 | `zephyr_tick_queue_size > 80000` | Warning |
| WAL 容量告警 | `zephyr_wal_dir_bytes > 1.4GB` | Warning |
| WAL 容量危急 | `zephyr_wal_dir_bytes > 1.8GB` | Critical |
| CH 写入失败 | `rate(zephyr_ch_write_total{outcome!="committed"}[5m]) > 0` | Warning |
| drain 持续失败 | `rate(zephyr_drain_failed_total[5m]) > 0` | Warning |

### §2.4 docker-compose 集成

现有 `docker-compose.yml` 已定义 prometheus + grafana + node-exporter 服务。本模块负责：
- 配置 Grafana 数据源（provisioning/datasources/）
- 导入 Dashboard JSON 模板（provisioning/dashboards/）
- 配置告警通知渠道

## §3 依赖

- depends_on: MOD-INF-016 (shared_core) — MetricsRegistry 是 Prometheus 数据源的基础
- P1-5 metrics_server 提供 /metrics 端点
- depgraph 边: 6680250 → 6682516 (metrics.py)

## §4 代码文件清单（已施工）

```
src/zephyr/shared/observability/dashboard/
├── __init__.py
├── datasource_config.py      # Grafana 数据源配置生成 ✅
├── dashboard_templates.py    # Dashboard JSON 模板 ✅
├── alert_rules.py            # 告警规则定义 ✅
config/infra/grafana/
├── datasources/
│   ├── prometheus.yml        # 已有 ✅
│   └── clickhouse.yml        # 新增 ✅
└── dashboards/
    ├── provider.yml          # 已有 ✅
    ├── data_collection_health.json  # 新增 ✅
    ├── ch_write_health.json         # 新增 ✅
    └── drain_health.json            # 新增 ✅
tests/zephyr/shared/observability/test_dashboard.py  # 14 项测试 ✅
```

## §5 验收标准

- [x] Grafana 可同时查询 Prometheus 和 ClickHouse 两个数据源（clickhouse.yml + docker-compose 插件）
- [x] 3 个 Dashboard 可正常展示（数据采集/CH写入/Drain健康）
- [x] 6 条告警规则可触发并通知（ALERT_RULES）
- [x] docker-compose up 后 Grafana 自动加载数据源和 Dashboard（provisioning + GF_INSTALL_PLUGINS）
- [ ] 行情数据概览 / 回测结果 Dashboard（需 ClickHouse 查询层，P3 迭代）
