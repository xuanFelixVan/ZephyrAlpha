---
module_id: MOD-L00-006
title: WAL 段编解码蓝图
doc_type: blueprint
status: Draft
layer: L2_domain
date: "2026-07-22"
version: "0.1.0"
last_updated: "2026-07-22"
ttl: permanent
depends_on:
  - "MOD-L00-004 数据源集成器（WAL 段文件格式来源）"
construction_progress: not_started
language: zh
description: WAL 段文件编解码层——当前 TSV 格式，可选升级为 Protobuf（更紧凑、schema 演进友好），支持向后兼容
build_status: planned
design_maturity: design
responsibility_domain: 
---

# WAL 段编解码蓝图（MOD-L00-006）

> **状态**：P2 阶段规划，depgraph 设计态已登记（node_id=6680249, status=planned）。
> 预计施工时机：P0+P1 完成后评估，仅在 TSV 性能不满足时启动。

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

## §4 代码文件清单（目标态，未施工）

```
src/zephyr/data/wal_codec/
├── __init__.py
├── tsv_codec.py        # TSV 编解码（当前格式，从 local_replay 提取）
├── proto_codec.py      # Protobuf 编解码（可选）
├── schema.py           # Schema 注册表 + 版本管理
└── codec_registry.py   # magic number → codec 路由
```

## §5 验收标准（施工时定义）

- [ ] TSV 格式段文件可正常编解码（向后兼容）
- [ ] Protobuf 格式段文件比 TSV 节省 > 30% 空间
- [ ] 混合格式段文件可自动识别并正确解码
- [ ] Schema 变更后旧段文件可降级解析（缺失列填默认值）
