---
module_id: MOD-RK-37
title: "统一绩效归因与策略退化检测蓝图 — IC 衰减 60 日均线退化判定 + 拥挤度联动自动降权"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P0
blueprint_level: module
design_maturity: production
build_status: stable
responsibility_domain: 
---

# MOD-RK-37 Performance Attribution & Degradation Guard — 统一绩效归因与策略退化检测 蓝图

> **module_id**: MOD-RK-37 | **域**: D_RISK | **层**: L02/L04 风控层
> **优先级**: P0 | **来源**: CAND-RSK-040（B4-06959，模块42，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-RK-37

## 1. 定位

绩效监控不只看盈亏：统一绩效归因（Brinson 配置/选择/交互 + 因子/风险归因）+
策略退化检测闭环。归因与 IC 衰减计算分散三处（MOD-L07-001/MOD-PF-007/
MOD-L02-004）已各自可用，缺的是**策略退化判定与自动降权闭环**——本模块补上：
IC 60 日均线衰减 >50% → 退化判定；拥挤度联动（MOD-RK-13 口径分数）→ 追加降权；
产出 weight_multiplier 指令（0.0=权重归零写回信号权重，0.5=减半，1.0=保持），
写回执行归调用方（模块48 动态信号权重联动编排）。

复用优先：退化判定核心规则委托 MOD-PF-007 detect_degradation（IC 衰减 >50% →
权重归 0 建议唯一真源）；Brinson 归因委托 MOD-PF-007 brinson_attribute（统一入口
薄封装，不重造 Brinson/因子/风险归因）。

## 2. 输入 / 输出

- 输入：strategy_id；ic_series（日 IC 序列，PIT 已实现口径，≥window 个）；
  crowding_score（可选，MOD-RK-13 拥挤度分数 0~1）；segments（Brinson 归因用）。
- 输出：StrategyDegradationVerdict（ic_ma60_reference/current、ic_decay_pct、
  degraded、crowding_penalty、weight_multiplier、action KEEP/HALVE/ZERO、reasons）；
  BrinsonResult（委托产出）。

## 3. 核心规则

1. IC 60 日均线：reference=序列首个 window 均值，current=末个 window 均值
   （window 默认 60，C 类参数）。
2. 退化判定：ic_decay_pct=(reference−current)/reference > 50% → degraded
   （委托 MOD-PF-007 detect_degradation，reference≤0 语义同其约定→退化）。
3. 拥挤度联动：crowding_score > crowding_warn（默认 0.6，RK-13 阈值口径）→
   追加 0.5 降权（HALVE）；degraded 优先 → weight_multiplier=0.0（ZERO）。
4. action：ZERO（degraded）> HALVE（拥挤超阈）> KEEP；reasons 全量记录。
5. 统一归因入口：brinson_attribute 委托 MOD-PF-007（本模块不重算归因）。
6. Fail-Closed：IC 序列不足 window/非有限值/crowding_score 越界 [0,1] → 拒绝。

## 4. 依赖前置

- MOD-PF-007 performance_attribution_engine（退化判定/Brinson 委托真源）
- MOD-RK-13 crowding_monitor（拥挤度分数口径）
- MOD-L02-004 ic_decay（IC 衰减曲线口径参考，PIT 铁律）

## 5. 验收标准

- 单测全绿（MA60 计算/退化边界 50%/reference≤0/拥挤联动 HALVE/degraded 优先
  ZERO/统一入口委托/留痕 reasons/非法输入拒绝）；tests/risk 域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-37`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-37` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-37` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-37 | MOD-RK-37 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/risk/core/performance_attribution_degradation.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_performance_attribution_degradation.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
