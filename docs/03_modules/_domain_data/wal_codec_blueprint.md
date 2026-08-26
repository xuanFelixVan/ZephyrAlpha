---
module_id: MOD-L00-006
title: WAL 段编解码蓝图
doc_type: blueprint
status: Active
layer: L2_domain
date: "2026-07-22"
version: "0.2.0"
last_updated: "2026-07-22"
ttl: permanent
depends_on:
  - "MOD-L00-004 数据源集成器（WAL 段文件格式来源，ch_writer.tsv_escape 转义真源）"
construction_progress: prototype
language: zh
description: WAL 段文件编解码层——当前 TSV 格式（已施工），Protobuf 为 P3 远期备选
build_status: production
design_maturity: design
responsibility_domain: 
---

# WAL 段编解码蓝图（MOD-L00-006）

> **状态**：P2-9 TSV codec 已施工（prototype），Protobuf 为 P3 远期备选。
> 转义逻辑委托 ch_writer.tsv_escape（裁定 #ARCH-TSV-SOT-001，单一真源）。
> wal_writer._serialize_tsv 保持直接使用 ch_writer.tsv_escape（不强制走 wal_codec，避免不必要的间接层）。

---

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L00-006`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L00-006` 的 11 个 file 节点 | design | `extract_depgraph.py --modules MOD-L00-006` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L00-006 | MOD-L00-006 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 11 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 动机

P0-1 WalWriter 使用 TSV 格式落盘 WAL 段文件。TSV 优点是与 ClickHouse INSERT 原生兼容（`FORMAT TabSeparated`），但缺点：
- 无 schema 内嵌——列变更时旧段文件解析失败
- 文本编码开销——数值列以字符串存储，空间浪费
- 无压缩——段文件体积大

借鉴 BalletHip 的 Proto 编码方案，可选升级 WAL 段格式为 Protobuf：
- 博主场景：万级 TPS IPC 序列化
- ZephyrAlpha 场景：WAL 段文件存储格式优化（低优先级，TSV 当前够用）

## §2 设计要点（占位，施工时细化）

### §2.1 格式选型

| 格式 | 空间 | 解析速度 | Schema 演进 | CH 兼容 | 优先级 |
|------|------|----------|-------------|---------|--------|
| TSV（当前） | 大 | 快 | 无 | 原生 | ✅ 当前使用 |
| Protobuf | 小 30-50% | 快 | 有 | 需转换 | P2 备选 |
| Parquet | 小 60-70% | 中 | 有 | 原生 | P3 远期 |

### §2.2 Protobuf Schema（草案）

```protobuf
syntax = "proto3";
package zephyr.wal;

message TickSegment {
  string table = 1;
  repeated TickRow rows = 2;
  int64 timestamp_ms = 3;
  string schema_version = 4;
}

message TickRow {
  string trade_date = 1;
  int64 timestamp_ms = 2;
  string symbol = 3;
  string market_type = 4;
  int64 price_scaled = 5;       // price * 10000 (Decimal → int64)
  uint64 volume = 6;
  int64 amount_scaled = 7;
  string direction = 8;
  string data_source = 9;
  int64 bid_price_scaled = 10;
  int64 ask_price_scaled = 11;
  uint64 bid_volume = 12;
  uint64 ask_volume = 13;
  string quality_flag = 14;
}
```

### §2.3 向后兼容

- 段文件头部 4 字节 magic number 区分格式：`TSV\n` vs `PB\x01`
- drain 线程根据 magic number 自动选择解码器
- 混合格式段文件可共存（渐进迁移）

## §3 依赖

- depends_on: MOD-L00-004 (data_source_integrator) — WAL 段文件由 local_replay 管理
- P0-1 WalWriter 是主要消费者
- depgraph 边: 6680249 → 6680426 (local_replay.py)

## §4 代码文件清单（已施工）

```
src/zephyr/data/wal_codec/
├── __init__.py
├── tsv_codec.py        # TSV 编解码（委托 ch_writer.tsv_escape）✅
└── codec_registry.py   # magic number → codec 路由 + Proto stub ✅
tests/zephyr/data/test_wal_codec.py  # 22 项测试 ✅
```

## §5 验收标准

- [x] TSV 格式段文件可正常编解码（向后兼容）（test_roundtrip）
- [x] 编码结果与 wal_writer._serialize_tsv 完全一致（test_roundtrip_with_ch_writer_consistency）
- [x] 混合格式段文件可自动识别并正确解码（codec_registry.get_codec）
- [ ] Protobuf 格式段文件比 TSV 节省 > 30% 空间（P3 远期）
- [ ] Schema 变更后旧段文件可降级解析（P3 远期）
