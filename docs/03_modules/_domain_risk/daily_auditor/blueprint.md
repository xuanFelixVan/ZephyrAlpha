---
module_id: MOD-RK-20
title: "日终审计器蓝图 — PnL对账 + 归因偏差 + 合规报告 + 日终检查清单"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: production
---

# MOD-RK-20 Post-Trade Daily Auditor — 日终审计器 蓝图

> **module_id**: MOD-RK-20 | **域**: D_RISK | **层**: L3 Post-Trade 盘后审计
> **优先级**: P1 | **成熟度**: production | **对标能力**: C-004●, C-026◐
> **SSoT**: depgraph MOD-RK-20 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-20, §2 依赖(RK-03→RK-20, RK-06→RK-20, RK-16→RK-20)

## 1. 定位

日终审计器——D-RISK 三层防线第三层 (L3 Post-Trade 盘后审计) 的核心模块。每个交易日收盘后执行:
- 日终 PnL 对账 (预期 vs 实际, 检测资金缺口)
- 归因偏差检测 (预测风险归因 vs 实际 PnL 归因, 复用 RK-16)
- 合规报告生成 (限额消耗/突破检查, 复用 RK-06)
- 日终检查清单 (位置/PnL/限额/Kill Switch/数据完整性)
- 问题追溯修正 (问题登记 + 根因 + 修正动作)
- CTR-P1-011 RiskMetricsReport 产出 (供 D-REPORTING)

属 A 类基础设施 (对账 + 报告装配, 逻辑确定), 输入为各域盘后快照, 不参与热路径。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 前后持仓快照 + 成交记录 + 限额消耗 (RK-06) + 风险分解 (RK-16) | — |
| 输出 | DailyAuditReport + RiskMetricsReport | CTR-P1-011 → D-REPORTING |
| 依赖 | RK-03 Portfolio Risk Monitor (持仓快照) ; RK-06 Risk Limit Manager (限额) ; RK-16 Risk Decomposition (归因) | — |

## 3. 核心规则 (设计真源 §1.2 RK-20, §2)

### 3.1 日终 PnL 对账 (资产负债表恒等式, gross)

- 市值: MV_prev = Σ qty_prev × close_prev ; MV_now = Σ qty_now × close
- 交易现金流: trade_cash = Σ fill.qty × fill.price (买入 cash out, 卖出 cash in)
- 预期 PnL: expected = (MV_now − MV_prev) − trade_cash
- 已实现 PnL (gross, 不含成本): realized = Σ fill.realized_pnl
- 未实现 PnL (当日, prev_close→close): unrealized = Σ_i qty_i × (close_i − prev_close_i)
  - prev_close 来源: 前日快照 close ; 新持仓 (无前日快照) 取 avg_entry (入场→收盘 = 日内移动)
- 账面总 PnL: total_pnl = realized + unrealized
- 对账缺口: gap = expected − total_pnl ; gap_pct = gap / |nav| (nav=0 时为 0)
- 状态: |gap_pct| ≤ tolerance → MATCH ; 否则 MISMATCH
- 交易成本: total_cost = Σ fill.cost (报告用, 不参与 gap)
- 一致性: 持仓守恒 + 已实现盈亏与成交一致时 gap=0; 缺失成交/已实现错误 → gap≠0

### 3.2 归因偏差检测 (复用 RK-16)

- 预测因子贡献占比: predicted_factor_pct = factor_variance / total_variance (来自 RK-16)
- 实际因子 PnL 占比: actual_factor_pct = factor_pnl / (|factor_pnl| + |residual_pnl|) (分母为 0 时偏差=0)
- 偏差: bias = predicted_factor_pct − actual_factor_pct
- 判定: |bias| > bias_threshold → BIASED ; 否则 ALIGNED

### 3.3 合规报告

- 逐项限额检查: consumed > value → BREACHED ; consumed > value×warn_ratio → WARNING ; 否则 OK
- 整体: 任一 BREACHED → FAIL ; 否则 PASS

### 3.4 日终检查清单

5 项必查:
1. 持仓对账 (前后持仓数量核对)
2. PnL 对账 (缺口在容差内)
3. 限额合规 (无 BREACHED)
4. Kill Switch 状态 (终态为 CLOSED 或明确 OPEN 原因)
5. 数据完整性 (行情/成交数据无缺失)

### 3.5 问题追溯修正

每个问题登记: issue_id / category / severity / description / root_cause / correction / status

## 4. 关键不变量 (INVARIANTS)

- PnL 守恒: total_pnl = realized + unrealized
- 对账缺口: gap = expected − total_pnl (符号一致)
- 归因占比和: |factor_pnl|+|residual_pnl| 为实际占比分母 (允许异号, 取绝对值)
- 检查清单状态: 任一 FAIL → 整体 FAIL ; 全 PASS → PASS ; 仅 WARNING → PASS_WITH_WARNINGS
- 报告幂等: 同一交易日 + portfolio_id 重复审计产生等价报告

## 5. 错误契约

- `InvalidAuditInputError` (ZA-RK-0020): 持仓快照 symbol 不一致 / 数量为 NaN / 容差非正 / 限额消耗非法

## 6. 测试

- `tests/risk/test_daily_auditor.py`
- 覆盖: PnL 对账 (MATCH/MISMATCH/缺口计算) / 归因偏差 (ALIGNED/BIASED/零分母) / 合规报告 (OK/WARNING/BREACHED/整体) / 检查清单 (5项/整体状态) / 问题追溯 / RiskMetricsReport 装配 / 输入校验 / 幂等性

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费: RK-03 (持仓快照) / RK-06 (限额消耗) / RK-16 (风险分解, DecompositionResult)
- 产出: CTR-P1-011 RiskMetricsReport → D-REPORTING

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-20`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-20` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-20` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-20 | MOD-RK-20 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


