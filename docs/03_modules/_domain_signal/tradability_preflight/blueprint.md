---
module_id: MOD-SIG-151
title: "可交易性预检蓝图 — 候选池当日可买性五查聚合"
doc_type: blueprint
status: Active
version: "0.1.1"
design_maturity: production
ttl: permanent
layer: L05_signal
layer_name: signal
functional_domain: signal
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-09-16"
last_updated: "2026-09-16"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-SIG-151 Tradability Preflight — 可交易性预检三查专件 蓝图

> **module_id**: MOD-SIG-151 | **域**: D_ASHARE_SIGNAL | **消费节点**: TDM-E-L3-10
> **出身**：晨审 st-tdm-review-20260911 §7.1 L3-10"部分采纳"缺口（价格笼子/权限/资金一手三查无专件）；Owner 2026-09-16 裁定"四个欠账直接开工，全部接通"。

## 1. 职责（节点 TDM-E-L3-10 逐条对码）

| 节点语义 | 本模块落法 |
|---|---|
| 停牌 | InstrumentSnapshot.suspended（instrument_master 口径注入）→ SUSPENDED |
| 一字涨停（买不进） | prev_close×板块比例算涨停价（主板10/ST5/创业科创20/北交所30），开=高=低≥涨停 → LIMIT_UP_UNBUYABLE；意图价触板同判 |
| 价格笼子（±2%） | 复用 ex_core.check_price_cage；**夹边语义非拒单**（ex_core 实装=超限自动夹边），CLAMPED 给 cage_suggested_price 建议价不阻断——节点"会被拒"按实装口径修正，真拒单在下单层 L4-12（有实时盘口） |
| 板块权限 | classify_board→权限词表 {STAR,CHINEXT,BSE}；账户注入则强校验，未注入降级 detail（下单层复检） |
| 资金一手 | min_order_unit（主板100/科创200）×意图价=一手成本；可用资金不足 → LOT_CASH |

**fail-closed**：prev_close/min_order_unit 缺失 → DATA_MISSING 判不可交易（不猜）；symbol 非法 → ValueError。

## 2. 边界

- 纯函数零 DB/CH：行情快照与账户上下文全部注入；不直连 instrument_master 存储。
- 集合竞价/市价单豁免笼子校验由调用方判断（ex_core 原口径保留）。
- 不做卖出向预检（T+1 可卖归 position/t1_sellable，X-S2-02 已挂）。

## 3. 接口

```python
from zephyr.signal_ashare.tradability_preflight import preflight_tradability
verdict = preflight_tradability(InstrumentSnapshot(...), AccountContext(...), intended_price=..., intended_qty=...)
# TradabilityVerdict(symbol, tradable, blocked, cage_suggested_price, details)
```

## 4. 验收

- tests/signal_ashare/test_tradability_preflight.py：五查命中×5 + fail-closed×3 + 笼子建议价 + ST/科创板块矩阵 + 红蓝（空 symbol 契约/边界 10.99<11.00/零 prev_close）
- 地图：TDM-E-L3-10 module_ref 回填本模块（同 commit）

## 5. 已实现代码路径

| 文件 | 状态 |
|---|---|
| src/zephyr/signal_ashare/tradability_preflight.py | ✅ 本模块 |
| tests/signal_ashare/test_tradability_preflight.py | ✅ 配套测试 |

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（AGENTS.md 同名条款）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/tradability_preflight.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/signal_ashare/test_tradability_preflight.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本节 → 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-151`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-151` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-151` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-151 | MOD-SIG-151 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
