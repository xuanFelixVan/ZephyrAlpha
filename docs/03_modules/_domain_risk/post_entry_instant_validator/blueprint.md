---
module_id: MOD-RK-40
title: "Post-Entry Instant Validator 买入后即时验证与快速纠错蓝图 — T+5/15/30min 三档验证"
doc_type: blueprint
status: Active
version: "0.1.2"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P1
blueprint_level: module
design_maturity: production
build_status: production
responsibility_domain: 
---

# MOD-RK-40 Post-Entry Instant Validator — 买入后即时验证与快速纠错 蓝图

> **module_id**: MOD-RK-40 | **域**: D_RISK | **层**: L04 风控层增量
> **优先级**: P1 | **来源**: CAND-RSK-044（B14-04546，A9 §2.2后 36.1/36.2，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-RK-40

## 0. 查重裁定与 canonical 声明（RULE-EIGHT 探查结论）

候选 spec：买入后 T+5min（跌破买价>1% 且放量→观察标记）/ T+15min（跌破分时均线
反弹无力→减仓 50%）/ T+30min（反向>2ATR→全部止损）；与 stop_loss/ATR 止损联动；
动作写审计链（对标 Gao et al. 2018 JF 日内动量 + A 股交易台纪律）。

场内既有件逐一探查：

- MOD-TRADING-008 strategy_abnormal_exit_orchestrator：**异常退出五步编排**
  （冻结→撤单→平仓→核对→置态，CRASH/TIMEOUT/RISK_TRIGGERED 触发）——执行编排面，
  非"买入后动量验证"判定核心；
- stop_loss（MOD-L04-001）/ ashare_stop_loss_engine（MOD-RK-09）/ atr_stop_engine
  （MOD-RK-35）：常规止损体系（价格/ATR 止损单点）——无 T+5/15/30min 三档
  时间窗验证规则；
- MOD-SELL-012 sell_execution_quality_tracker：卖出执行质量复盘（滑点分级）——
  事后度量非盘中纠错。

**裁定：独立缺口成立，按补充层施工。canonical 声明：本模块为"买入后即时验证与
快速纠错"唯一真源；W-P1-22 同名候选 CAND-SELL-002（B10-01475，D_SELL_DECISION，
spec 全等：5min 观察/15min 减 50%/30min 清 2ATR）应归并本件（本波先建）。**

## 1. 定位

L4 风控层增量判定核心：买入成交后按 T+5/15/30min 三档时点校验持仓动量，
逐档产出 PASS/WATCH/REDUCE_HALF/EXIT_ALL 纠错动作信号。纯函数无 IO；动作仅产
信号——减仓/清仓执行委托既有止损执行族（stop_loss/atr_stop_engine/卖出编排），
动作留痕经 audit_sink 委托 D_GOV_AUDIT（"动作写审计链"）。

## 2. 输入 / 输出

- 输入：symbol + entry_price + checkpoint（MIN_5/MIN_15/MIN_30）+ current_price；
  档位必填：MIN_5→volume_ratio（当日量/均量）；MIN_15→vwap（分时均线）+ session_low
  （时段最低价）+ atr14；MIN_30→atr14。
- 输出：PostEntryVerdict（symbol/checkpoint/action/reason/metrics，frozen）。
- 审计：非 PASS 动作经 audit_sink 回调留痕。

## 3. 核心规则

1. MIN_5：drawdown=(entry−current)/entry > 1%（可配）且 volume_ratio ≥ 1.5（可配）
   → WATCH（观察标记）；否则 PASS。
2. MIN_15：current < vwap 且反弹无力（current − session_low < 0.5×ATR，可配）
   → REDUCE_HALF（减仓 50%）；否则 PASS。
3. MIN_30：entry − current > 2×ATR（反向幅度，可配）→ EXIT_ALL（全部止损）；
   否则 PASS。
4. 逐档独立判定、纯函数天然幂等；上一档动作不改变后续档位评估口径（调用方按
   时点逐档调用）。
5. Fail-Closed：价格/atr/vwap 非正非有限、volume_ratio<0、session_low 越界、
   档位必填缺失、未知档位、阈值配置非法 → InvalidPostEntryInputError。
6. verdict frozen 不可变；reason 如实记录命中规则与指标快照。

## 4. 依赖前置与联动

- 分时行情（vwap/量价/时段低点，调用方注入，三维解耦不越域取数）
- 联动（装配面，非 import）：REDUCE_HALF/EXIT_ALL 信号 → stop_loss（MOD-L04-001）/
  atr_stop_engine（MOD-RK-35）/ sell_signal_collector（MOD-SELL-001）执行族；
  audit_sink → D_GOV_AUDIT writer
- 分工边：MOD-TRADING-008（异常退出编排，执行面）

## 5. 验收标准

- 单测全绿：三档规则命中/未命中边界（1% 严格大于、2ATR 严格大于、vwap 严格小于）、
  档位必填缺失拒绝、配置非法拒绝、audit_sink 仅非 PASS 触发、verdict frozen；
  tests/risk 域零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-40`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-40` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-40` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-40 | MOD-RK-40 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
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
| — | — | 本模块尚无已实现代码 |

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


