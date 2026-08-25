---
module_id: MOD-L00-005
title: 数据源冗余与热切换蓝图
doc_type: blueprint
status: Active
layer: L2_domain
date: "2026-07-22"
version: "0.2.0"
last_updated: "2026-07-22"
ttl: permanent
depends_on:
  - "MOD-L00-004 数据源集成器（CH 写入层复用）"
construction_progress: prototype
language: zh
description: 主备数据源热切换——主 QMT 推送中断时自动切换备源（通达信本地接口），CH 不可达时降级写本地 SQLite，保证数据不中断
build_status: testing
design_maturity: design
responsibility_domain: 
---

# 数据源冗余与热切换蓝图（MOD-L00-005）

> **状态**：P2-8 已施工（prototype），depgraph 节点已登记。
> 施工内容：heartbeat_monitor / source_switcher / sqlite_fallback / recovery 四模块。
> 集成点：tick_subscriber.__init__ 接受 heartbeat 参数，_on_tick 中调用 record_tick()。

---

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L00-005`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L00-005` 的 15 个 file 节点 | design | `extract_depgraph.py --modules MOD-L00-005` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L00-005 | MOD-L00-005 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | testing | testing | ✅ |
| file_count | 15 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 动机

A 股数据源（QMT/miniQMT）是单点。QMT 客户端崩溃、券商服务器抖动、网络中断 = 数据中断。

借鉴 BalletHip 主备线路热切换思想（Caddy + Cloudflare Tunnel），适配为"主备数据源热切换"：
- 博主场景：polymarket 网络线路冗余（主备 Tunnel）
- ZephyrAlpha 场景：数据源 API 冗余（主 QMT + 备通达信）+ CH 冗余（主 VM + 备本地 SQLite）

## §2 设计要点（占位，施工时细化）

### §2.1 主备数据源

| 层 | 主源 | 备源 | 切换触发 |
|----|------|------|----------|
| tick 推送 | miniQMT subscribe_quote | 通达信本地接口 / 其他券商 API | 主源 tick 推送中断 > 10 秒 |
| K线下载 | miniQMT get_market_data | 通达信本地接口 | 下载失败重试 3 次 |

### §2.2 CH 冗余降级

| 层 | 主 | 备 | 切换触发 |
|----|-----|-----|----------|
| ClickHouse | Hyper-V VM (TCP 9000 / HTTP 8123) | 本地 SQLite（WAL 段文件） | VM 不可达 > 30 秒 |

> P0-1 WalWriter 已保证数据不丢（主动 WAL 落盘）。本模块在此基础上增加 CH 降级到 SQLite 的能力，使查询层在 CH 不可达时仍可读取最近数据。

### §2.3 心跳检测

- tick_subscriber 每 N 秒检测主源 tick 推送是否中断
- CH 心跳：每 10 秒 ping CH `SELECT 1`，连续 3 次失败标记 CH 不可达

### §2.4 切换策略

```
主源中断 > 10s → 切换备源 → log + metrics 告警
主源恢复 → 等 30s 稳定期 → 切回主源（避免抖动）
CH 不可达 > 30s → 降级写本地 SQLite → CH 恢复后回灌
```

## §3 依赖

- depends_on: MOD-L00-004 (data_source_integrator) — 复用 ch_writer 的二级降级链
- P0-1 WalWriter 提供数据不丢保证
- depgraph 边: 6680248 → 6680427 (ch_writer.py)

## §4 代码文件清单（已施工）

```
src/zephyr/data/redundant_source/
├── __init__.py
├── heartbeat_monitor.py    # 心跳检测（主源 + CH）✅
├── source_switcher.py      # 数据源切换控制器 ✅
├── sqlite_fallback.py      # CH 降级到本地 SQLite ✅
└── recovery.py             # CH 恢复后 SQLite→CH 回灌 ✅
tests/zephyr/data/test_redundant_source.py  # 16 项测试 ✅
```

## §5 验收标准

- [x] 主源中断 10 秒内切换到备源，数据不丢（test_switch_to_backup_on_primary_dead）
- [x] CH 不可达 30 秒内降级到 SQLite，查询层可读（test_ch_dead_after_failures）
- [x] CH 恢复后自动回灌 SQLite 数据到 CH（test_recovery_triggers_when_ch_up_and_data_pending）
- [x] 切换/降级/恢复全程有 metrics 指标暴露（zephyr_ch_heartbeat / zephyr_primary_heartbeat / zephyr_source_active）
- [x] tick_subscriber 集成 HeartbeatMonitor（_on_tick 调用 record_tick）
