---
module_id: MOD-SIG-155
title: "A01 日线/分钟行情源线判据转化器蓝图 — 动量五档×量价确认×方向判据"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
layer: L05_signal
layer_name: signal
functional_domain: ashare_signal
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-10-05"
last_updated: "2026-10-05"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-155 Kline Momentum Criterion — A01 日线/分钟行情源线判据转化器 蓝图

> **module_id**: MOD-SIG-155 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L9-A01（源线·日线/分钟行情，module_ref 挂载=总裁终裁批，本班不落图）
> **出身**：施工单 st-fg-srcline1-20261005（红源线首批 6 条判据转化器，红源线施工母单批准）；能力反查零命中（新增能力面，2026-10-05 留审计）。

## 1. 判据语义（地图节点 decision_question 逐条对码）

节点问句：**价量趋势与动量能否预测N日收益？** 本件把 OHLCV K 线序列（DS-002 口径）转为三段判据：

1. **N 日动量档位**（momentum_tier）：`ret_N = close[-1]/close[-1-N] − 1`，五档（STRONG_UP/UP/NEUTRAL/DOWN/STRONG_DOWN），阈值 ±0.05/±0.15 初拟待实盘标定；
2. **价量确认**（volume_mode）：量能放大（近半窗量均/前半窗量均 ≥1.2）确认当前方向，缩量（≤0.8）判背离，平稳判中性；
3. **方向判据**（direction_lean）：确认态沿动量方向给 long/short，背离态降级 flat（不编方向），NEUTRAL 档恒 flat。

## 2. 关键口径（proposed，待实盘标定）

- **回看窗口** N=20 日（A01 节点 algo_note：U3 频率=daily）。
- **量比** = 近半窗量均 / 前半窗量均（半窗=window//2）；前半窗量均 ≤0 → 比值取中性 1.0 并记 notes。
- **复权口径**：由调用方注入已复权收盘（复权因子禁进 PIT 窗，本件不感知复权，K 线落定不修订）。
- ** DS 真源注记**：DS-002（market_data.ohlc_bar）注册表标 deprecated，在产真源=CH 日线表（kline 族）；读入形态（symbol/trade_date/close/volume）不变，判据不受迁移影响。

## 3. 查重分工（三重反查留痕 2026-10-05）

CapabilityLookup「源线 判据/动量判据」等六向零命中；clone_guard 写前预查 6 文件 0 findings；sector/ 族 `sector_momentum`（MOD-SIG-026 系）是**板块级**动量打分（q3/q5/q20 横截面排名），本件是**源线级**判据转化（单标的 OHLCV → decision_question 判据），正交不并。

## 4. INVARIANTS（代码头部同文）

纯函数核零 IO（K 线序列调用方注入，升序）；五档单值输出；输入非法 fail-closed（KlineMomentumInputError）；记录级缺陷跳过记 notes 不整体 fail；同输入必同输出（零墙钟零随机）；复权口径调用方保证。

## 5. 接口

- `build_kline_momentum_criterion(symbol, closes, volumes, *, window=20) -> KlineMomentumCriterion`：主入口（序列形态）。
- `build_from_bars(symbol, bars, *, window=20)`：DS 读入形态入口（bar 字典序列，乱序重排+缺陷 bar 跳过记 notes）。
- 输出 `KlineMomentumCriterion.to_dict()`：全基本类型，json.dumps 直序列化。
- 测试：`tests/signal_ashare/source_line/test_kline_momentum_criterion.py`（22 测，tmp_path 无生产路径写入）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-155`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-155` 的 3 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-155` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-155 | MOD-SIG-155 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | N/A | — |
| file_count | 3 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/source_line/__init__.py` | ⚠️ 骨架 | |
| `src/zephyr/signal_ashare/source_line/kline_momentum_criterion.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/signal_ashare/source_line/test_kline_momentum_criterion.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
