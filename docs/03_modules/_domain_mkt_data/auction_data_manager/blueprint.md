---
module_id: MOD-MKT-007
title: "A股集合竞价数据管理器蓝图 — 竞价时段快照采集校验落账与回放供数"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L01_foundation
layer_name: market_data
functional_domain: mkt_data
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-MKT-007 Auction Data Manager — A股集合竞价数据管理器 蓝图

> **module_id**: MOD-MKT-007 | **域**: D_MKT_DATA | **层**: L1 基础平台
> **优先级**: P1 | **成熟度**: design→testing | **对标能力**: D-DATA-32 A-Share Auction Data Manager
> **SSoT**: depgraph MOD-MKT-007 | **代码**: `src/zephyr/market_data/auction_data_manager.py`
> **设计真源**: D-DATA-32 §30.3.1（B10-02234，canonical）+ A3数据架构 §17.1（B13-04251，REVIEW 归并）

## 0. 边界与撞名裁定

- **双 D-DATA-32 撞名裁定**：B10-02234（§30.3.1，竞价时段采集任务+CH 落地+命中率回放）
  与 B13-04251（§17.1，miniQMT 竞价快照 9:15-9:25 逐 3 秒+14:57-15:00+落 CH/Parquet+
  竞价量价/虚拟撮合价量字段校验）为同一建设项（同号同名同域）。本模块为唯一 canonical
  （CAND-MKTDATA-003 晋升），B13-04251（CAND-MKTDATA-004）REVIEW 归并——其 miniQMT/
  逐 3 秒/尾盘竞价/字段校验四面全部并入本模块 spec。
- **数据管理 vs 信号分析分工**：MOD-SIG-089 auction_microstructure_analyzer=信号分析面
  （特征/行为分类/方向，快照由上游注入）；本模块=数据管理面（采集编排/校验规范化/
  落账委托/回放供数），为其上游供数。MOD-PLAN-015 auction_hit_recorder=盘中命中判定
  持久化；本模块"命中率回放"=回放供数面，不做命中判定。
- **不重复存量**：miniqmt_provider._fetch_auction_snapshot/_fetch_auction_book=原始
  采集函数（已建，本模块 fetcher 注入挂接点）；schemas/categories/market_auction(.book)
  =DDL 真源（本模块 quality_flag 口径对齐）；scenario_planner=auction_book 消费（不碰）。

## 1. 定位

竞价数据管理器——竞价时段判定（开盘 09:15-09:25 逐 3 秒 + 收盘 14:57-15:00）、
采集编排（fetcher 注入源无关）、字段校验 Fail-Closed、规范化落账（sink 委托
CH/Parquet）、回放供数（loader 注入，PIT 过滤+排序去重）。纯内存管理面，零 IO。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 原始 tick（fetcher 注入 Iterable[Mapping]） | symbol/ts/indicative_price/indicative_volume 必填 |
| 输入 | 库存行（loader 注入，Mapping 或 AuctionSnapshotRecord） | 回放路径 session 按 ts 推导 |
| 输出 | AuctionSnapshotRecord（规范化快照，quality_flag 对齐 CH 列口径） | 字段名对齐 MOD-SIG-089 AuctionSnapshot |
| 输出 | CollectReport / ReplayReport（状态+拒收留痕+notes） | frozen |

## 3. 核心设计

### 3.1 竞价时段判定

| 要素 | 口径 |
|------|------|
| 开盘集合竞价 | 09:15:00 ≤ t ≤ 09:25:00（含端点），快照节奏逐 3 秒（OPEN_SNAPSHOT_CADENCE_SEC=3） |
| 收盘集合竞价 | 14:57:00 ≤ t ≤ 15:00:00（含端点） |
| session_of(ts) | 命中返回 AuctionSession，窗口外 None |

### 3.2 字段校验（Fail-Closed，构造即校验）

- 必填键：symbol/ts/indicative_price/indicative_volume（缺失即拒）。
- 取值域：indicative_price>0；indicative_volume/auction_amount/buy1/placed/canceled ≥ 0；
  canceled ≤ placed（两者皆存在时）；quality_flag ∈ (0,1)。
- PIT：ts.date() == trade_date（跨日/未来拒收）。
- session 匹配：session_of(ts) == 声明时段（采集路径）；回放路径按 ts 推导。
- 类型 coercion：datetime 或 ISO 字符串 ts；int/float/数值字符串数值；bool 一律拒收。

### 3.3 采集编排 collect_session

fetcher(trade_date, session) → 逐条 validate_tick → (symbol,ts) 去重保首条 →
sink(records) 一次性落账。状态机：ok / empty（零抓取不调 sink）/ all_rejected
（全拒不调 sink）/ fetch_error / sink_error（异常留痕不抛，调度不炸）。

### 3.4 回放供数 replay

loader(trade_date, symbols) → 轻校验（Mapping 重走 validate_tick 推导 session；
Record 直通仍核 PIT）→ session/symbols 过滤 → (symbol,ts) 去重保首条 →
按 (symbol,ts) 排序输出（同标的 ts 严格递增，MOD-SIG-089 消费前置条件）。
loader 异常 → notes 留痕不抛。

## 4. 关键不变量 (INVARIANTS)

- 记录构造即 Fail-Closed（价>0/量≥0/撤单≤申报/PIT/session 匹配）。
- (symbol,ts) 批内去重保首条（采集与回放同口径）。
- fetcher/sink/loader 异常不炸调度（status/notes 留痕）。
- 不直连行情源/DB——三面全注入，模块零 IO。

## 5. 错误契约

- `AuctionDataManagerError`（占位 ZA-MKT-UNREGISTERED-auction-manager）：用法 Fail-Closed。
- `InvalidAuctionTickError`（占位 ZA-MKT-UNREGISTERED-auction-tick）：逐条校验失败。

## 6. 依赖

- `zephyr.shared.foundation.errors`（ZephyrBaseError）。
- 设计面依赖（depgraph design 边）：miniqmt_provider（采集通道挂接）、
  schemas/categories/market_auction（落表口径）、auction_microstructure_analyzer
  （供数分工）、auction_hit_recorder（回放供数分工）。

## 7. 测试

`tests/market_data/test_auction_data_manager.py`（51 例）：时段边界/记录校验/
tick 规范化/采集编排（去重/拒收/异常不炸/空批与全拒不调 sink）/回放（排序/去重/
过滤/PIT/异常不炸）/用法 Fail-Closed/frozen。

## 8. 遗留

- 运行时接线：fetcher 接 miniqmt_provider 竞价采集函数（可包 xtdata 逐 3 秒轮询），
  sink 接 ch_writer（auction_snapshot 表 INSERT_COLUMNS 口径）/Parquet 写入，
  loader 接 ch_reader 读库存——留运行时装配批；tasks.yaml 挂 scheduler 同批。
- 错误码正式登记（占位→ZA-MKT 区段，见 P1W16 fragment manual_registrations）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MKT-007`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MKT-007` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-MKT-007` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MKT-007 | MOD-MKT-007 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/market_data/auction_data_manager.py` | ✅ 已实现 | |

### 9.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/market_data/test_auction_data_manager.py` | ✅ 已实现 | |

### 9.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §9（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
