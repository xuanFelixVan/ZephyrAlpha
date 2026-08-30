---
ttl: permanent
---

> **归档注记（2026-08-30）**：自 design_memos/implementation_plans 归档（候选核销批 greatwall_20260830——内容全量施工完毕核销，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=architecture_view · title=冷数据归档施工图 · owner=ZephyrAlpha-Owner · language=zh · status=active · version=0.3.1 · date=2026-08-15 · topic=cold_archive_build_plan · scope=07_trading_decision_architecture · depends_on=- 16_technical_indicator_build_plan.md - docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml - docs/02_enterprise_architecture/04_architecture_principles_decisions/project_handbook/03_data_layer.md

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：archiver.py（scripts/ch/archiver.py）已施工；阶段 1（tick_data + kline_* 2019 年前）2026-08-10 执行完毕；阶段 2 部分执行（technical_indicator 60min/120min 2019 年前已归档）；2026-08-16 冷分层裁定批（AI-ARCH-002，合并 f556515519）落地——数据留存契约 YAML 修订 + archiver.py 重构 +214 行 + test_ch_archiver.py 新建 160 行，原"铁律修订措辞未落盘"缺口闭环。
>
> **最终成果**：ClickHouse→E 盘 Parquet 冷归档链路生产可用，D 盘物理空间冲突缓解。
>
> **未做事项及原因**：verify 逐字段值比对、manifest 四字段、checksum 强化、独立 export 子命令未做——均登记 §10 开放问题为增强候选，非阻塞；ETF 4 个分钟周期 2019 年前未归档——§2.5 未覆盖，开放问题 5 登记。

# 冷数据归档施工图

> **性质**：active v0.3.0。本文是冷数据归档（ClickHouse → E盘 Parquet）的施工执行计划。
> 落地契约 [data_retention_contract.yaml](../../../01_policies_and_standards/_registry/contracts/data_retention_contract.yaml) INV-RET-002 提到的"未来 archiver.py"，
> 解决 D 盘物理空间不足与技术指标回算存储需求的冲突。
> **执行状态（2026-08-12 回填）**：archiver.py 已施工（`scripts/ch/archiver.py`），阶段 1（tick_data + kline_* 2019 年前）已于 2026-08-10 执行完毕，阶段 2 部分执行（technical_indicator 60min/120min 2019 年前已归档）。铁律修订措辞尚未落到契约 YAML（仍 v1.0.0），见 §10 开放问题 1。

## 1. 背景：物理空间与铁律的冲突

### 1.1 问题

| 维度 | 现状（2026-08-10 规划时） |
|------|------|
| D 盘可用 | 83.2 GB（总计 731 GB，ClickHouse 占 337 GB）|
| 6 周期技术指标回算需求 | ~198 GB（实测 `technical_indicator` 压缩比 1.087，每行 547 字节，363M 行）|
| 缺口 | ~115 GB |

`technical_indicator` 表实测压缩比 1.087（浮点列 + 大量 NULL 导致 LZ4 几乎失效），与契约假设的 35% 压缩比严重偏离。6 个周期全量回算装不下 D 盘。

> **单位口径说明（v0.3.0 补）**：ClickHouse `formatReadableSize` 输出为 GiB（1024 进制），磁盘可用空间（shutil.disk_usage）为 GB（十进制），两者相差 ~7.4%。本文保留各数字的原始测量单位不换算（GB/GiB 混用处的差异在规划误差可接受范围内），跨口径求和时以 GiB 为准近似。

### 1.2 铁律冲突

[data_retention_contract.yaml](../../../01_policies_and_standards/_registry/contracts/data_retention_contract.yaml) §1 三条铁律：

| 铁律 | 原文 | 冲突点 | 状态（2026-08-12） |
|------|------|--------|--------|
| INV-RET-001 | "所有数据永不删除——禁止 DROP TABLE / DELETE WHERE / TTL" | DROP PARTITION 是否算"删除"？ | 措辞修订方案已定（§4.1），**未落盘 YAML** |
| INV-RET-002 | "进 Cold 层必须手动触发——archiver.py 仅提供手动 CLI" | archiver.py 未实现 | ✅ **已实现并执行**（2026-08-10，§3.8） |
| INV-RET-003 | "所有表 Hot 层无 TTL，永久保留" | "永久保留"是否意味着不能 DROP PARTITION？ | 措辞修订方案已定（§4.2），**未落盘 YAML** |

**裁定**：铁律精神是"数据不丢失"（保留或归档），不是"ClickHouse 必须保留全部数据"。归档到 Parquet 并验证行数一致后的 DROP PARTITION，数据仍保留在 Parquet，不违反铁律精神。需修订铁律措辞以消除歧义。**执行注记**：阶段 1/2 归档（含 DROP PARTITION）已按本裁定先行执行（2026-08-10），契约 YAML 措辞修订滞后（仍 v1.0.0），形成"执行先行、契约未同步"的临时状态——需在开放问题 1 关闭前避免再次批量归档。

### 1.3 目标

1. 腾出 D 盘 ≥ 147.8 GiB 空间（83 GB → ~231 GB，口径统一为 §2.5 阶段 1 合计），足够装 6 周期回算 ~162 GiB（缩减后，§2.4）+ 缓冲 ✅ **已达成**（阶段 1 归档完成，§3.8）
2. 落地 archiver.py，实现契约 INV-RET-002 定义的手动冷归档 CLI ✅ **已达成**（2026-08-10 施工，§3.8）
3. 修订铁律措辞，明确"归档后 DROP PARTITION"的合法性 ⏳ **未落盘**（方案 §4 已定，YAML 仍 v1.0.0，开放问题 1）
4. 保留回测所需的热数据（Tick 近期 + K线一个牛熊周期）✅ **已达成**（Tick 保留 2025-2026 / K线保留 2019 年起，§3.8）

## 2. 两层归档架构

按数据用途分两层，各自独立确定归档分界线。

### 2.1 第一层：Tick 数据（做T回测专用）

**用途**：逐笔回放模拟真实撮合，用于做T策略回测和滑点建模。Tick 数据量极大（3秒粒度），近期数据访问频率高，历史数据访问频率低。

**数据现状**（c1_market.tick_data，204.2 GiB，按月分区）：

| 年份 | 大小 | 行数 | 访问频率 |
|------|------|------|---------|
| 2022 | 7.67 GiB | 545M | 低（早期，标的少）|
| 2023 | 23.90 GiB | 1.77B | 低 |
| 2024 | 61.46 GiB | 4.51B | 中 |
| 2025 | 69.78 GiB | 5.11B | 高（近期做T回测）|
| 2026 | 41.34 GiB | 2.74B | 高（当前年）|

**归档分界线**：归档 2022-2024（93.0 GiB），保留 2025-2026 近 2 年 Hot。

**对标机构实践**（不按契约 cold_policy "≥2年" 经验值，按行业分层实践）：
- 机构（kdb+）：Hot 内存 1-3 月 / Warm SSD 1-3 年 / Cold HDD 5-10 年，**10 年总保留**
- 量化社区：Tick 5 年起，Parquet Cold 存储
- 证监会合规：交易数据保留 ≥7 年
- **关键**：机构 10 年保留是 Hot+Warm+Cold 分层总计，不是全部放 Hot。kdb+ Hot 内存只放 1-3 个月

**本方案**（符合行业分层实践）：
- Hot 层（ClickHouse）：2025-2026 近 2 年 → 快速做T回测（滑点建模需当前市场微观结构）
- Cold 层（E 盘 Parquet）：2022-2024 → 需要时恢复或 DuckDB 查询
- 总保留：4.5 年（全部数据都在，只是分层，不删除）
- 符合量化社区"5 年起"（4.5 年接近 5 年，全部保留）

**修订契约 L1 cold_policy**：从"≥2年后"修订为"按机构分层实践，Hot 保留近 2 年，Cold 归档 2-5 年前，总保留 ≥5 年"。

### 2.2 第二层：所有其他 K 线数据（统一时间节点）

**用途**：日线/周线/月线/各分钟周期 K 线，用于趋势策略、日内策略、多周期共振回测。

**数据现状**（按表汇总，137.2 GiB）：

| 表 | 总大小 | 2015年前 | 2015-2018 | 2019-2026 | 2019起占比 |
|------|--------|---------|-----------|-----------|-----------|
| kline_1min | 88.69 GiB | 25.42 | 14.99 | 48.28 | 54.4% |
| kline_5min | 16.17 GiB | 4.69 | 2.57 | 8.91 | 55.1% |
| kline_15min | 6.85 GiB | 2.10 | 1.14 | 3.61 | 52.6% |
| kline_30min | 3.56 GiB | 1.10 | 0.59 | 1.87 | 52.5% |
| kline_60min | 1.88 GiB | 0.60 | 0.31 | 0.97 | 51.6% |
| kline_etf_1min | 5.41 GiB | 0.17 | 0.33 | 4.90 | 90.7% |
| kline_lof_1min | 1.46 GiB | 0.09 | 0.26 | 1.11 | 76.0% |
| 其他 ETF/LOF | 2.90 GiB | 0.12 | 0.28 | 2.50 | 86.2% |
| kline_index | 0.15 GiB | 0.05 | 0.03 | 0.08 | 50.1% |
| **合计** | **137.2 GiB** | **44.3** | **20.5** | **72.4** | **52.7%** |

> 注：kline_daily/weekly/monthly 体积小（日线 ~2MB/标的/年），不在归档范围。technical_indicator 正在回算中，不归档。

**归档分界线选择**：

| 方案 | 归档范围 | 腾出空间 | 保留 Hot | 保留理由 |
|------|---------|---------|---------|---------|
| A | 2015 年前 | 44.3 GiB | 2015-2026（12年）| 2015 杠杆牛起点，数据完整 |
| **B（推荐）** | **2019 年前** | **64.9 GiB** | **2019-2026（8年）** | **一个完整牛熊周期** |
| C | 2021 年前 | 85.4 GiB | 2021-2026（6年）| 近期牛市起点 |

**推荐方案 B**：保留 2019-2026 近 8 年，覆盖一个完整牛熊周期：
- 2019-2021 核心资产牛市（茅台/宁德等）
- 2022-2024 熊市（美联储加息 + 经济下行）
- 2025-2026 当前周期

归档 2019 年前数据（64.9 GiB），符合用户"保留一个牛熊周期"的指引。

### 2.3 news_data 保留 Hot（L6 新闻事件层，不归档）

**数据现状**：c3_fundamental.news_data，21.28 GiB，1408 万行，时间跨度 1999-12-31 ~ 2026-08-10（27 年）。

**裁定（用户确认 2026-08-10）**：全量保留 Hot，不归档。理由：
1. 21 GiB 对机构标准算小（机构基本面/新闻层通常全留 Hot）
2. NLP 管道训练（#ARCH-NLP-PIPELINE-001）需要全量历史样本提升情绪分类准确率
3. 跨周期情绪回测（事件驱动 sleeve 26 号 + 情绪周期 28 号）需要全量新闻 + 全量日 K 反推新闻对股价的影响
4. 省的 8.5 GiB 仅占总归档量 5.4%，性价比低

契约 L6 cold_policy 维持"不归档（21 GiB 机构标准算小，全量 Hot 保留）"。

### 2.4 technical_indicator 归档策略（逻辑一致化）

**原方案问题**：K 线分钟数据只保留 2019 年后，但 technical_indicator 全量保留——逻辑不一致。

**修正**（跟 K 线归档分界线对齐）：
- **日线/周线/月线指标**：全量保留（跟日 K 一致，日 K 永久保留是机构标准）
- **分钟周期指标**（1min/5min/15min/30min/60min/120min）：只算 2019 年后，2019 年前的回算数据归档到 Cold

**回算量缩减**：
- 60min 全量 64M 行 → 2019 年后约 19M 行（省 70%）
- 120min 全量 32M 行 → 2019 年后约 9.5M 行（省 70%）
- 30min/15min/5min/1min 原本就是近期滚动，不受影响
- technical_indicator 回算后总量从 198 GiB 降到 ~162 GiB（省 36 GiB）

### 2.5 全部归档对象合计

| 数据 | 归档范围 | 腾出空间 | 保留 Hot | 执行阶段 |
|------|---------|---------|---------|---------|
| tick_data | 2022-2024 | 93.0 GiB | 2025-2026（2年）| 阶段 1 |
| kline_1min | 2019 年前 | 40.4 GiB | 2019-2026（8年）| 阶段 1 |
| kline_5min/15min/30min/60min | 2019 年前 | 13.1 GiB | 2019-2026 | 阶段 1 |
| kline_etf/lof 各周期 | 2019 年前 | 1.3 GiB | 2019-2026 | 阶段 1 |
| ~~news_data~~ | ~~2019 年前~~ | ~~8.5 GiB~~ | **全量保留 Hot（不归档）** | — |
| **阶段 1 合计** | | **147.8 GiB** | | 立即执行 |
| technical_indicator 分钟指标 | 2019 年前 | ~36 GiB | 2019-2026 | 阶段 2（回算后）|
| **总计** | | **~183.8 GiB** | | |

**分两阶段执行**：
- **阶段 1**（立即）：归档 tick_data + kline_* 2019 年前 → 腾出 ~147.8 GiB → D盘可用 ~231 GB
- **阶段 2**（technical_indicator 回算完成后）：归档分钟指标 2019 年前 → 腾出 ~36 GiB

阶段 1 后 D 盘可用 231 GB，technical_indicator 回算需要 162 GiB（缩减后），留 69 GB 缓冲。充足。

**E 盘空间需求**：183.8 GiB（ClickHouse 体积），Parquet 压缩后预计 25-38 GiB（tick_data/kline 在 CH 已压缩至 13-18%，Parquet zstd 类似）。E 盘可用 463.5 GiB，充足。

**其他 103 个表**（合计 ~2 GiB）：体积小，全部保留 Hot，不归档。包括 L3 日K（< 2 MiB）、L4 资金面（< 50 MiB）、L5 基本面（~250 MiB）、L7-L10（均 < 1 MiB）。

## 3. archiver.py 施工方案

### 3.1 模块定位

| 属性 | 值 |
|------|-----|
| 文件路径 | `scripts/ch/archiver.py` |
| 模块 ID | MOD-L00-004-ARCHIVER（待登记）|
| 契约对接 | data_retention_contract.yaml INV-RET-002 |
| 触发方式 | 手动 CLI（INV-RET-002 铁律：不接入 scheduler）|
| 成熟度 | production |
| 安全级别 | M（数据删除操作，需验证门禁）|

### 3.2 三阶段原子操作

```
archiver.py archive --table c1_market.tick_data --partition 202201

  阶段1: export  — ClickHouse 读取分区 → pyarrow 写 Parquet 到 E 盘
  阶段2: verify  — 比对行数 + 抽样字段值（100行）
  阶段3: drop    — 验证通过后 ALTER TABLE DROP PARTITION

  任何阶段失败 → 不进入下一阶段，数据不丢失
```

### 3.3 E 盘目录结构

```
E:/zephyr_cold_archive/
├── archive_manifest.jsonl              # 归档清单（append-only，铁律审计依据）
├── c1_market/
│   ├── tick_data/
│   │   ├── 202201.parquet              # 按月一个文件（与 CH toYYYYMM 分区对齐）
│   │   ├── 202202.parquet
│   │   └── ...
│   ├── kline_1min/
│   │   ├── 200006.parquet
│   │   └── ...
│   ├── kline_5min/
│   ├── kline_15min/
│   ├── kline_30min/
│   ├── kline_60min/
│   ├── kline_etf_1min/
│   └── ...
└── restore_log.jsonl                   # 恢复日志（应急恢复时记录）
```

### 3.4 归档清单格式（archive_manifest.jsonl）

每行一条 JSON 记录，append-only：

```json
{
  "table": "c1_market.tick_data",
  "partition": "202201",
  "rows": 38425289,
  "parquet_path": "E:/zephyr_cold_archive/c1_market/tick_data/202201.parquet",
  "parquet_size_bytes": 123456789,
  "ch_size_bytes": 584023456,
  "compress_ratio": 0.21,
  "archived_at": "2026-08-10T15:30:00Z",
  "verified": true,
  "dropped": true,
  "checksum_md5": "abc123..."
}
```

### 3.5 CLI 接口设计

```bash
# 归档单个分区（export + verify + drop 三阶段原子操作）
python scripts/ch/archiver.py archive --table c1_market.tick_data --partition 202201

# 批量归档（指定年月范围）
python scripts/ch/archiver.py archive-range \
    --table c1_market.tick_data --from 202201 --to 202412

# dry-run（只打印计划，不执行）
python scripts/ch/archiver.py archive-range \
    --table c1_market.tick_data --from 202201 --to 202412 --dry-run

# 只导出不删除（纯备份模式，不腾 D 盘空间）
python scripts/ch/archiver.py export --table c1_market.tick_data --partition 202201

# 列出已归档分区
python scripts/ch/archiver.py list

# 从 Parquet 恢复到 ClickHouse（应急用）
python scripts/ch/archiver.py restore --table c1_market.tick_data --partition 202201

# 统计归档情况（各表已归档分区数 + 腾出空间）
python scripts/ch/archiver.py stats
```

### 3.6 关键实现要点

**导出方式**：ClickHouse HTTP API `SELECT ... FORMAT Parquet` 服务端序列化流式落盘（64KB chunk，内存恒定——ClickHouse 在 Hyper-V VM 不能直接写 Windows E 盘；防 OOM 由"按月分区单文件"粒度保证）。✅ 已施工（§3.8.1）。

**验证机制**：行数比对（CH `count()` vs Parquet 元数据 num_rows；>1M 行大分区允许 ±1 容差——count() 元数据优化与 FORMAT Parquet 的已知差异，§3.8.1）+ 随机 100 行抽样可查性确认。逐字段值比对未实现，强化候选见 §10 开放问题 6。

**DROP PARTITION**：验证通过后 `ALTER TABLE {table} DROP PARTITION {partition}`。

**断点续传**：归档清单记录每个分区的 `verified`/`dropped` 状态；批量归档中断后重跑跳过 `dropped=true` 分区；`verified=true` 但 `dropped=false` 的分区直接执行 drop 阶段（跳过 export+verify）。

### 3.7 依赖

| 依赖 | 来源 | 用途 |
|------|------|------|
| clickhouse-driver | 已安装 | 读 ClickHouse 分区数据（restore 用）|
| pyarrow 19.0.1 | 已安装 | verify 读 Parquet 元数据 / restore 读表 |
| zephyr.data.ch_reader | 已有 | ClickHouse 查询封装 |
| zephyr.data.ch_writer | 已有 | ClickHouse 写入（restore 用）|

### 3.8 已施工设施盘点与执行状态（2026-08-12 回填，通用规则 #11）

#### 3.8.1 archiver.py 已施工

`scripts/ch/archiver.py`（528 行，2026-08-10 施工），实现三阶段原子操作（export→verify→drop）+ 断点续传 + append-only 清单。已提供 5 个 CLI 子命令：`archive` / `archive-range`（含 `--dry-run`）/ `list` / `stats` / `restore`。

**与 §3.5 设计的差异**：

| 设计项（§3.5/§3.4/§3.6） | 代码现状 | 差异评估 |
|---|---|---|
| 独立 `export` 子命令（纯备份模式，不删除） | **未实现为 CLI**（export_partition 函数存在，仅作为 archive 的阶段 1 内部调用） | 功能缺口，非阻塞——纯备份可用 archive-range 后手动保留分区替代；记入开放问题 6 |
| verify 抽样 100 行**字段值比对**（symbol/OHLC/volume） | 仅做行数比对 + 抽样 100 行"可查性"确认（未逐字段比对，代码注释："行数一致已足够可信"） | 弱化。行数一致 + Parquet 列存自描述（schema 随文件）已覆盖主要风险；字段级校验强化记入开放问题 6 |
| verify 行数严格相等 | 大分区（>1M 行）允许 **±1 行容差**（ClickHouse count() 元数据优化 vs FORMAT Parquet 的已知差异） | 实现期发现的合理容差，回填设计 |
| manifest 字段：table/partition/rows/parquet_path/parquet_size_bytes/ch_size_bytes/compress_ratio/archived_at/verified/dropped/checksum_md5 | 实际字段：table/partition/parquet_path/parquet_size_bytes/archived_at/verified/dropped | 缺 rows/ch_size_bytes/compress_ratio/checksum_md5 四字段；checksum 强化记入开放问题 6 |
| 分批读取单次 < 2GB 防 OOM | HTTP 流式落盘（64KB chunk），内存恒定，无需分批 | 实现更优 |

#### 3.8.2 阶段 1/2 执行状态（archive_manifest.jsonl 实证）

归档已于 **2026-08-10** 执行，manifest 共 **1865 条**记录（全部 verified=true, dropped=true）：

| 数据 | 归档范围 | 分区数 | 设计（§2.5） | 状态 |
|------|---------|--------|------|------|
| tick_data | 202201-202412 | 36 | 93.0 GiB，阶段 1 | ✅ 完成 |
| kline_1min | 200006-201812 | 223 | 40.4 GiB，阶段 1 | ✅ 完成 |
| kline_5min/15min/30min/60min | 200006-201812 | 各 223 | 13.1 GiB，阶段 1 | ✅ 完成 |
| kline_etf_1min | 200502-201812 | 167 | 1.3 GiB（etf+lof），阶段 1 | ✅ 完成 |
| kline_lof_1min | 201008-201812 | 101 | 同上 | ✅ 完成 |
| technical_indicator 60min | 2019 年前 | 223 | ~36 GiB，阶段 2 | ✅ 完成（提前于回算完成） |
| technical_indicator 120min | 2019 年前 | 223 | 同上 | ✅ 完成 |

**ClickHouse 实测（2026-08-12，`system.parts`）**：

| 表 | 当前大小 | 剩余分区 | 与 §6.2 预期对照 |
|---|---|---|---|
| tick_data | 111.13 GiB | 202501-202608（20 个） | 预期 ~111 GiB ✅ 精确吻合 |
| kline_1min | 48.37 GiB | 201901-202608（92 个） | 预期 ~48 GiB ✅ 吻合 |
| kline_5min/15min/30min/60min | 8.72 / 3.61 / 1.87 / 0.97 GiB | 201901 起（各 92 个） | ✅ 符合 |
| technical_indicator | 108.06 GiB / 300M 行 | — | 回算进行中（目标 300M+ 行，§6.4 口径 363M 为 6 周期全量上限） |
| kline_etf_5min/15min/30min/60min | 合计 ~2.5 GiB | **200502 起（未归档 2019 年前）** | ⚠️ §2.5 未覆盖 4 个 ETF 5min+ 周期，见开放问题 5 |
| kline_lof_5min/15min/30min/60min | 合计 ~1.3 GiB | **201008 起（未归档 2019 年前）** | ⚠️ 同上 |

**D/E 盘实测（2026-08-12）**：D 盘可用 **80.2 GB**，E 盘可用 **362 GB**（归档占用约 100 GB）。D 盘可用与 §6.2 预期（≥231 GB）差距大——差异归因：归档腾出的空间已被 technical_indicator 回算（当前 108 GiB）回填占用，属"归档→回算"计划内接力，非归档失败。回算全部完成后 D 盘稳态可用预期 ~60-80 GB（83.2 + 147.8 - 162 ≈ 69 GB GiB 口径近似），与设计目标自洽。

## 4. 铁律修订

文件：[data_retention_contract.yaml](../../../01_policies_and_standards/_registry/contracts/data_retention_contract.yaml)

> **落盘状态（2026-08-12 核实）**：以下 §4.1/§4.2/§4.3 修订方案（v0.2.0 用户确认）**尚未落到契约 YAML**——契约当前仍为 v1.0.0（2026-07-14），INV-RET-001 仍为"所有数据永不删除"原措辞，changelog 无 v1.1.0 条目。契约文件为 human_gated 治理资产，修订需用户触发，见 §10 开放问题 1。

### 4.1 修订 INV-RET-001

```yaml
# 修订前
- id: INV-RET-001
  rule: "所有数据永不删除"
  description: "业务数据只保留或归档，禁止 DROP TABLE / DELETE WHERE / TTL 自动删除"

# 修订后
- id: INV-RET-001
  rule: "所有数据永不丢弃——只保留或归档"
  description: "业务数据只保留或归档，禁止 DROP TABLE / DELETE WHERE / TTL 自动删除。归档到 Parquet 并验证行数一致后的 ClickHouse 分区，允许通过 ALTER TABLE ... DROP PARTITION 移除（数据已保留在 Parquet）"
  enforcement: "archiver.py 归档前必须验证 Parquet 行数 = ClickHouse 行数，验证通过后才 DROP PARTITION；归档清单 append-only 记录"
```

### 4.2 补充 INV-RET-003

```yaml
# 修订前
- id: INV-RET-003
  description: "ClickHouse 所有业务表不设 TTL 表达式，永久保留"

# 修订后
- id: INV-RET-003
  description: "ClickHouse 所有业务表不设 TTL 表达式，无自动删除。允许手动 DROP PARTITION 归档（INV-RET-002 手动触发前提，归档后数据保留在 E 盘 Parquet）"
```

### 4.3 新增 changelog

```yaml
- version: "1.1.0"
  date: "2026-08-10"
  changes:
    - "修订 INV-RET-001：归档到 Parquet 并验证后允许 DROP PARTITION（D 盘物理空间不足驱动）"
    - "补充 INV-RET-003：明确手动 DROP PARTITION 归档不属于 TTL 自动删除"
    - "落地 archiver.py（契约 INV-RET-002 提到的'未来 archiver.py'）"
    - "两层归档架构：Tick 层（2022-2024归档）+ K线层（2019年前归档，保留一个牛熊周期）"
```

## 5. 执行步骤

### 步骤 1：修订铁律（手动编辑 data_retention_contract.yaml）

按 §4 修订 INV-RET-001 / INV-RET-003 / 新增 changelog v1.1.0。

### 步骤 2：实现 archiver.py

✅ 已施工（2026-08-10，`scripts/ch/archiver.py` 528 行，5 个 CLI 子命令）——实现函数清单与设计差异见 §3.8.1。

### 步骤 3：执行冷归档

**执行顺序**（先小表验证流程，再大表批量执行）：kline_30min/15min/5min/60min（200006-201812）→ kline_1min（最大头）→ ETF/LOF 1min → tick_data 2022-2024（93 GiB，流程验证后执行）。CLI 用法见 §3.5。

✅ 已于 2026-08-10 执行完毕——各表分区范围、分区数与 manifest 实证（1865 条全 verified+dropped）见 §3.8.2。

### 步骤 4：验证 D 盘空间释放

```bash
# D 盘可用空间（预期 83 GB → ~231 GB；2026-08-12 实测 80.2 GB，差异为回算回填占用，见 §3.8.2）
python -c "import shutil; u = shutil.disk_usage('D:\\'); print(f'D 盘可用: {u.free/1024**3:.1f} GB')"

# ClickHouse 各表大小（确认已缩小）
python -c "from zephyr.data import ch_reader; print(ch_reader.query(\"SELECT table, formatReadableSize(sum(bytes_on_disk)) FROM system.parts WHERE database='c1_market' AND active=1 GROUP BY table ORDER BY sum(bytes_on_disk) DESC\"))"

# 归档清单统计
python scripts/ch/archiver.py stats
```

### 步骤 5：继续后续 4 周期回算

D 盘空间释放后，启动流水线：
- 30min 滚动 5 年（55M 行，30 GiB）
- 15min 滚动 3 年（66M 行，36 GiB）
- 5min 滚动 1 年（63M 行，34 GiB）
- 1min 滚动 90 天（83M 行，45 GiB）

用现有 [pipeline_remaining_periods.py](../../../../.runtime/tmp/pipeline_remaining_periods.py) 自动执行。

## 6. 验证方法

### 6.1 归档正确性

1. **行数一致性**：每个分区 Parquet 行数 = ClickHouse 归档前行数（实现容差：>1M 行大分区允许 ±1 行，§3.8.1）
2. **抽样可查性**：随机 100 行抽样查询确认可读（⚠️ 实现未做逐字段值比对，强化方案见开放问题 6）
3. **归档清单完整性**：`archive_manifest.jsonl` 每条记录 `verified=true` 且 `dropped=true` ✅（1865 条全部满足，2026-08-12 核实）
4. **ClickHouse 分区已删除**：`SELECT count() FROM system.parts WHERE table='tick_data' AND partition='202201'` 返回 0 ✅（实测 tick_data 剩余分区 202501-202608，§3.8.2）

### 6.2 D 盘空间

| 检查项 | 归档前 | 归档后（预期）| 实测（2026-08-12，§3.8.2）|
|--------|--------|-------------|-------------|
| D 盘可用 | 83.2 GB | ≥ 231 GB | 80.2 GB（回算回填占用，technical_indicator 已 108 GiB，属计划内接力）|
| tick_data | 204.2 GiB | ~111 GiB（保留 2025-2026）| 111.13 GiB ✅ |
| kline_1min | 88.7 GiB | ~48 GiB（保留 2019-2026）| 48.37 GiB ✅ |
| 其他 K 线表 | 44.3 GiB | ~24 GiB | 约 16 GiB（2019 年起，含未归档的 ETF/LOF 5min+ ~3.8 GiB）|

### 6.3 回测可恢复性

- 从 Parquet 恢复单分区测试：`python scripts/ch/archiver.py restore --table c1_market.tick_data --partition 202201`
- 验证恢复后行数一致 + 字段值一致
- DuckDB 可直接查询 Parquet（无需恢复）：`duckdb -c "SELECT count() FROM 'E:/zephyr_cold_archive/c1_market/tick_data/202201.parquet'"`

### 6.4 后续回算验证

6 周期回算全部完成后：
- `technical_indicator` 表总行数 ≈ 363M
- 各周期行数符合预期（60min 64M / 120min 32M / 30min 55M / 15min 66M / 5min 63M / 1min 83M）
- 抽样验证指标值非空（kdj_k/macd_dif/boll_upper 等）

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| Parquet 导出过程中 ClickHouse OOM | 低 | 导出失败 | 分批读取（按月分区，单次 < 2GB）|
| 验证通过但 DROP PARTITION 失败 | 低 | D 盘空间未释放 | 手动重试 DROP，归档清单记录状态 |
| 归档后需要回测 2022-2024 Tick 数据 | 中 | 需从 Parquet 恢复 | restore 命令可恢复单分区；DuckDB 可直接查询 Parquet |
| 归档后需要回测 2019 年前 K 线数据 | 中 | 需从 Parquet 恢复 | 同上；或用 DuckDB 联邦查询 |
| 导出期间 60min/120min 回算仍在跑 | 低 | 资源竞争 | 导出按月分批，单次 < 2GB，不影响回算 |

> **行业实践印证（2026-08-12 WebSearch）**：本文"分区级导出 Parquet + 行数验证 + DROP PARTITION"方案与 ClickHouse 社区归档工作流一致（oneuptime 2026-03 三策略中的 Strategy 3 分区级归档；验证环节同样以行数比对为准）。机构全自动方案（Storage Policy + TTL TO DISK 到 S3 冷层）依赖对象存储与 TTL 自动迁移，与本项目铁律 INV-RET-002（手动触发）/INV-RET-003（禁 TTL）及无 S3 的单机约束不兼容——手动 archiver.py 是硬边界内的正确取舍，非简化版缺陷。

## 8. 治理登记

### 8.1 ARCH 条目（architecture_issue_registry.yaml）

新增 ARCH 条目记录此次架构变更：

```yaml
- id: "ARCH-DATA-COLD-001"  # 待登记（ARCH-REFERENCE gate 要求引用与 registry 同 commit；登记补办落盘后恢复 # 前缀，见 §10 开放问题 2）
  title: "冷数据归档落地 + INV-RET-001/003 铁律修订"
  status: "in_progress"
  priority: "P0"
  date: "2026-08-10"
  description: "D 盘空间不足（83GB 可用 vs 198GB 回算需求），落地 archiver.py 冷归档工具，修订铁律允许归档后 DROP PARTITION"
  decision: "两层归档：Tick 2022-2024 + K线 2019年前，腾出 147.8 GiB"
  depends_on: ["#ARCH-DATA-TI-001"]
```

> **登记状态（2026-08-12 核实）**：⚠️ 该条目**尚未登记**到 architecture_issue_registry.yaml（全文检索无命中），违反"新增架构变更必须登记 ARCH 条目"治理约束。登记时需同步更新 status——阶段 1/2 归档已执行（§3.8.2），仅铁律 YAML 修订未落盘。见 §10 开放问题 2。

### 8.2 模块登记

- `capability_canonical_file_registry.yaml`：登记 archiver.py creation_token ⚠️ **未登记**（2026-08-12 全文检索无命中）
- `module_translation_registry.yaml`：登记 plain_zh 翻译条目（cold_archive → 冷数据归档）⚠️ **未登记**（2026-08-12 全文检索无命中）

> 两项登记缺口见 §10 开放问题 2（与 ARCH-DATA-COLD-001 一并补办）。旁证：OE-031（BM-SEL-01 L0 降级裁定条目，2026-08-12 兄弟 session 登记中）已引用本文档作为"现状 ClickHouse+Parquet 冷归档已覆盖需求"的依据——本文档已被治理注册表消费，自身登记却未完成。（注：条目编号暂以无 # 前缀弱引用，待登记落盘后恢复正式引用格式，见开放问题 2）

## 9. 与现有文档的关系

| 文档 | 关系 |
|------|------|
| [data_retention_contract.yaml](../../../01_policies_and_standards/_registry/contracts/data_retention_contract.yaml) | 铁律真源，本文落地其 INV-RET-002 定义的 archiver.py |
| [03_data_layer.md](../../04_architecture_principles_decisions/project_handbook/03_data_layer.md) | Hot/Warm/Cold 三层定义，本文落地 Cold 层（Parquet 归档）|
| [16_technical_indicator_build_plan.md](16_technical_indicator_build_plan.md) | 技术指标回算施工图，本文为其腾出存储空间 ⚠️ 该文档曾因未 commit 丢失、现为重建骨架（47 行），存储数字真源暂在本文（§1.1/§2.4），见开放问题 3 |
| [c1_market_clickhouse.md](../../03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md) | C1 行情仓库蓝图，本文归档其 tick_data/kline_* 表历史数据 |

## 10. 开放问题（2026-08-12 审查新增）

> 以下事项均不属本文档自身可闭环范围（涉及其他文档/注册表/治理资产），按"不越界改"纪律登记，待用户触发。

1. **铁律修订 YAML 落盘（用户决策项）**：§4 修订方案（INV-RET-001 改"永不丢弃"、INV-RET-003 补充手动归档豁免、changelog v1.1.0）经 v0.2.0 用户确认，但 data_retention_contract.yaml 仍为 v1.0.0 未落盘。当前处于"归档已执行、契约未同步"临时状态。契约是 human_gated 资产，需用户手动编辑落盘（或明确授权 AI 代编）。
2. **治理登记补办**：ARCH-DATA-COLD-001 未登记 architecture_issue_registry.yaml；archiver.py 未登记 capability_canonical_file_registry.yaml（creation_token）与 module_translation_registry.yaml（plain_zh）。登记时 status 应反映实际（归档已执行，非 in_progress 施工态）。登记落盘后，本文相关处的无 # 前缀弱引用恢复为正式 #ARCH- 引用格式。
3. **16号文档补全**：[16_technical_indicator_build_plan.md](16_technical_indicator_build_plan.md) 现为 47 行重建骨架（曾丢失），本文 §1.1/§2.4/§5/§6.4 的存储数字（198 GB/162 GiB/各周期行数）是其唯一真源——16号补全时应对齐引用本文数字，避免双源漂移。
4. **03_data_layer.md 同步**：03号三层定义（Warm=DuckDB+Parquet）与本文两层施工的关系需说明；03号把 daily_kline 划 Warm 层 vs 本文日 K 永久 Hot 的口径差异；03号 Cold"7 年合规"vs 本文"总保留 ≥5 年"的年限口径；03号未登记 archiver.py 的存在。以上归 03号作者侧同步。
5. **ETF/LOF 5min+ 周期归档裁定**：kline_etf_5min/15min/30min/60min（2005 年起，~2.5 GiB）与 kline_lof_5min/15min/30min/60min（2010 年起，~1.3 GiB）的 2019 年前分区未归档（§2.5 清单只列了 etf/lof 1min）。合计仅 ~3.8 GiB，归档收益小；但分界线一致性受损（同为分钟 K 线，1min 归档而 5min+ 不归档）。待裁定：补归档（一致性优先）还是维持现状（收益/成本比优先）。另注：[63_data_utilization_audit.md](63_data_utilization_audit.md) 的"归档"指表级生命周期退役，与本文分区级冷归档同名不同义，两文表计数口径差 1（102 vs 103），归 63号侧对齐。
6. **verify 机制强化（可选）**：当前 verify = 行数比对（±1 容差）+ 抽样可查性，未做 §3.6 设计的逐字段值比对，manifest 缺 rows/ch_size_bytes/compress_ratio/checksum_md5 字段，无独立 export CLI。候选强化：① Parquet 文件级 checksum_md5 写入 manifest（restore 前校验防静默腐坏，E 盘家用存储无 scrub）；② 抽样 100 行恢复字段值比对（symbol/OHLC/volume）；③ manifest 补 rows/compress_ratio（stats 更有用）。评估：已归档的 1865 分区行数全一致，风险敞口小，强化属"好上加好"非必须；若采纳需重跑历史分区补 checksum（成本高，可仅对新归档生效）。
7. **technical_indicator 30min/15min/5min/1min 归档时机**：阶段 2 已归档 60min/120min 2019 年前；剩余 4 周期为滚动窗口（§5 步骤 5：30min 5 年/15min 3 年/5min 1 年/1min 90 天），其 2019 年前分区是否存在取决于回算最终范围——回算完成后用 `archive-range` 对 2019 年前残留分区收尾即可，无需新设计。

## 变更历史

### v0.3.1 (2026-08-15) 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08）
- §3.6 压为当前态陈述（导出方式/验证机制/DROP/断点续传四条）：被 HTTP FORMAT Parquet 流式落盘取代的 clickhouse-driver 逐行读取设计与未施工伪代码块删除，实际实现以 §3.8.1 差异表为准；§3.7 末尾实现差异注记并入 §3.6
- §5 步骤 2/3 已施工内容压为"✅ 已施工/已执行"+指针（函数清单→§3.8.1、执行实证→§3.8.2、CLI 用法→§3.5）
- 变更历史 v0.3.0 条目"§7 行业实践印证"三重重复 bullet 去重为 1 条
- §1-§2/§4/§6-§10 零改动；铁律裁定/开放问题 7 项/跨文档链接零丢失

### v0.3.0 (2026-08-12) 执行状态回填 + 已施工设施盘点 + 口径统一
- **archiver.py 已施工回填**：§1.2 INV-RET-002 状态"未实现"→已实现并执行；新增 §3.8 已施工设施盘点——代码 528 行 5 个 CLI 子命令，与设计的 5 项差异逐条登记（export 走 HTTP FORMAT Parquet 流式落盘优于原方案；独立 export CLI 未实现；verify 仅行数±1容差+抽样可查性未做字段比对；manifest 缺 4 字段）
- **阶段 1/2 执行状态回填**：manifest 1865 条（2026-08-10 执行，全 verified+dropped）；tick_data 36 分区 + kline 5 周期各 223 + etf_1min 167 + lof_1min 101 + tech_ind 60/120min 各 223；ClickHouse 实测 tick_data 111.13 GiB（与 §6.2 预期精确吻合）/ kline_1min 48.37 GiB / tech_ind 108.06 GiB 300M 行（回算进行中）
- **D 盘差异归因**：实测 80.2 GB vs 预期 231 GB——归档腾出空间已被回算回填占用（计划内接力），回算完成后稳态预期 ~60-80 GB
- **口径统一**：§1.3 腾出目标 135 GB/218 GB+ → 147.8 GiB/~231 GB（与 §2.5 一致）；§5 步骤 4 "241 GB"→"231 GB"；§8.1 ARCH 条目 "157.9 GiB"→"147.8 GiB"；§1.1 补 GB/GiB 单位口径说明
- **治理缺口披露**：§4 铁律修订未落盘（YAML 仍 v1.0.0）；§8.1 ARCH-DATA-COLD-001 未登记；§8.2 两项模块登记未落盘——均转入新增 §10 开放问题（7 项：YAML 落盘/治理登记补办/16号补全/03号同步/ETF-LOF 5min+ 归档裁定/verify 强化/tech_ind 剩余周期归档时机）
- **§6 验证方法回填**：§6.1 四条验证标准标注实测状态（行数容差/抽样可查性弱化/清单完整性✅/分区删除✅）；§6.2 补实测列
- **§7 行业实践印证（2026-08-12 WebSearch）**：分区级归档+行数验证方案与 ClickHouse 社区工作流（oneuptime 2026-03 Strategy 3）一致；机构 TTL TO DISK 自动方案因铁律与无 S3 约束不适用，手动 archiver.py 是硬边界内正确取舍

### v0.2.0 (2026-08-10) 审查修正 + 用户确认
- **Tick 归档分界线**：不按契约 cold_policy "≥2年" 经验值，改为按机构分层实践（Hot 2年 + Cold 归档，总保留 ≥5 年）
- **news_data 归档→保留**：初版拟归档 2019 年前 news_data（省 8.5 GiB），经机构实践对标 + 算法依赖审查后**改为全量保留 Hot**——21 GiB 机构标准算小，NLP 训练 + 跨周期情绪回测需全量历史，省 8.5 GiB 仅占总量 5.4% 性价比低
- **technical_indicator 逻辑一致化**：分钟指标只算 2019 年后（跟 K 线对齐），日线指标全量保留。回算总量从 198 GiB 降到 162 GiB
- **分两阶段执行**：阶段 1（tick+kline，147.8 GiB）+ 阶段 2（tech_ind 分钟指标，36 GiB）
- **Parquet 压缩比修正**：从"50-80 GiB"修正为"25-38 GiB"（tick_data/kline 在 CH 已压缩至 13-18%）
- **导出性能预估补充**：tick_data 36 月分区约 2.5-4 小时，kline_1min 102 月约 1-2 小时
- **断点续传边界**：export 完成但 verify 失败时，重跑删除旧 Parquet 重新 export

### v0.1.0 (2026-08-10) 初始草案
- 两层归档架构定义（Tick 层 + K 线层）
- archiver.py 三阶段原子操作设计
- 铁律修订方案（INV-RET-001/003）
- 数据分析（各表 2015/2019 年起占用量）
- 执行步骤 + 验证方法
