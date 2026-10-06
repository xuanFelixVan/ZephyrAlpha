---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e9_attribution —— E9 实盘归因（SPM 9 节点）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 实盘绩效归因（Brinson/因子/风险/影子组合）并回灌假说先验，闭合 E9→E2 环。
- 计数: 9 = 1 stage(partial) + 8 mech（built 7 / pending 1）。

## 1. 族内节点全清单

| node_id | 名称 | 状态 | module_ref | 行 |
|---|---|---|---|---|
| FAC-E9 | 实盘归因（stage） | partial | MOD-PF-007 | SPM:L419 |
| FAC-E9-M-001 | 绩效归因引擎（Brinson三因子+因子/风险归因） | built | MOD-PF-007 | SPM:L4764 |
| FAC-E9-M-002 | 风险归因复用件 | built | MOD-RK-16 | SPM:L4795 |
| FAC-E9-M-003 | 模拟盘归因报告（residual 战役） | **pending** | MOD-BT-215 | SPM:L4808 |
| FAC-E9-M-004 | 决策标注数据集 | built | MOD-ML-014 | SPM:L4819 |
| FAC-E9-M-005 | 盈亏计算器（E9 归因原料手） | built | MOD-TRADING-002 | SPM:L4831 |
| FAC-E9-M-006 | 策略迭代升级器（归因→回灌执行件） | built | dir:_domain_factor/strategy_iteration_upgrader | SPM:L4844 |
| FAC-E9-M-007 | 影子组合对照引擎（Perold 四分解） | built | code:src/zephyr/pf_core/core/shadow_portfolio.py | SPM:L4855 |
| FAC-E9-M-008 | 条件胞归因 | built | code:scripts/backtest/condition_attribution.py | SPM:L4866 |

## 2. 接线现状与缺口判定

- 已接线：归因主体四件（Brinson 引擎/风险复用/影子组合 Perold/条件胞）+ 原料手（盈亏计算）+ 回灌执行件（M-006，feedback E9→E2 的机械落地）全 built。
- 缺口：M-003 模拟盘归因报告 pending（MOD-BT-215，residual 战役）——与 chief B1 ENV-16"sim 腿仅钩子"同判：sim 半腿只挂了钩子未出报告。
- 可考性：E9 的回测半腿=考卷 manifest/成本归因（H9 §1.8 F-C3-01 判 B：cost_attribution 在册考卷未开）；实盘半腿依赖 E7→E8 的真实持仓流。**两端都在半开状态**是本层结构性事实。

## 3. 修复建议（一句话）

M-003 模拟盘归因报告补齐以闭合"sim 考试→归因→回灌"半环；实盘半环等 GAP-1 翻转后自启。

## 4. 交叉验证

- TDM C 族：TDM-F-C3-01 多维归因引擎（TDM:L4356，performance_attribution_engine）=E9-M-001 同域件——H9 判 B（框架 cost_attribution 在册考卷未接）；H9 S5 建议（归因 manifest 增列）是两层的共同最小接线。
- feedback_loops[0] E9→E2"实盘归因回灌假说先验（RD-Agent 式闭环）"（SPM feedback 区）——与 M-006 互证，闭环骨架在、sim 归因报告未出。
- chief B1 ENV-16（复盘回测与归因 TDM C3+FACTORY E9，15 节点=C3 6+E9 9）计数口径与本册一致。
