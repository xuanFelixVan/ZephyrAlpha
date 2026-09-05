---
module_id: MOD-RK-34
title: "系统性风险分级预警与尾部风险管理蓝图 — 绿黄橙红黑 5 级状态机"
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
priority: P0
blueprint_level: module
design_maturity: production
build_status: production
responsibility_domain: 
---

# MOD-RK-34 Systemic Risk Alert State Machine — 系统性风险分级预警 5 级状态机 蓝图

> **module_id**: MOD-RK-34 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **来源**: CAND-RSK-037（B10-01476，模块37，AUD-DRAFT-001 裁定=做）
> **SSoT**: depgraph MOD-RK-34

## 1. 定位

VaR/CVaR 分级预警（Basel III 逆周期缓冲思想）落码：把组合 VaR95/CVaR、单日亏损、
连续两日亏损统一映射为绿/黄/橙/红/黑 5 级状态机，每级联动减仓/禁开/清仓与
kill switch 触发标记。与既有件分工：

- MOD-RK-10 ashare_systemic_risk_detector：市场侧 5 信号→3 级警报（信号计数制）；
- 本模块：组合侧 VaR/CVaR+亏损阈值→5 级（阈值分级制），补齐"绿黄橙红黑+连续亏损
  触发"缺口；纯计算输出指令，执行归调用方（减仓/禁开/清仓与 MOD-INF-016
  trading_kill_switch 的接线在编排层）。

## 2. 输入 / 输出

- 输入：var95_pct（VaR95 占 NAV 比例，正=损失）、cvar_pct（CVaR/ES 同口径）、
  daily_pnl_pct（当日盈亏比例）、prev_day_pnl_pct（前一日）、liquidity_crisis 标记；
  阈值配置（C 类参数，默认值见 §3）。
- 输出：SystemicRiskAssessment（level + 触发理由列表）+ RiskDirective
  （new_position_scale/reduce_pct/close_only/trigger_kill_switch/liquidate_all）。

## 3. 核心规则（默认阈值，候选登记真源）

| 级 | 触发（任一） | 指令 |
|---|---|---|
| 绿 GREEN | 其余皆不命中 | 正常（scale=1.0） |
| 黄 YELLOW | VaR95∈[2%,4%) 或 连续 2 日亏均 ≤−1% | 新开仓减半（scale=0.5） |
| 橙 ORANGE | VaR95∈[4%,6%) 或 单日亏 ≤−2% | 禁新开仓 + 减仓 30% |
| 红 RED | VaR95≥6% 或 单日亏 ≤−4% | 全线减仓 50% + 只平不开 |
| 黑 BLACK | CVaR≥10% 或 流动性危机 | 全部清仓 + kill switch 触发标记 |

- 取命中最严级（BLACK>RED>ORANGE>YELLOW>GREEN）；触发理由全量记录（不短路）。
- 状态机保留前态与迁移历史（只追加），迁移去抖由调用方按评估频率控制。
- Fail-Closed：输入非有限值/阈值配置畸形（级别边界非单调）→ 拒绝。

## 4. 依赖前置

- MOD-RK-05 var_calculator（VaR95/CVaR 输入来源，调用方计算注入）
- MOD-RK-011 drawdown_tracker（单日/连续亏损口径参考）
- MOD-INF-016 trading_kill_switch（BLACK 级触发标记的消费方，编排层接线）

## 5. 验收标准

- 单测全绿（5 级阈值边界/取最严/指令映射/理由全量/迁移历史/非法输入拒绝）；
  tests/risk 域集成零回归。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-34`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-34` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-34` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-34 | MOD-RK-34 | ✅ |
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

### 6.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/core/test_systemic_risk_alert_state_machine.py` | ✅ 已实现 | |

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


