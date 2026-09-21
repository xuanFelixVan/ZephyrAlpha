---
oid: C01
title: 日度资金分配编排（allocation_orchestrator.run_daily_allocation + batched_position_builder.schedule_buy_orders）
status: 已审
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline: 2fa92002c3
date: 2026-09-18
ttl: task_bound
---

# 深度审查报告：C01 日度资金分配编排（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 入口：`src/zephyr/pf_alloc/allocation_orchestrator.py:686`（run_daily_allocation）、`:1265`（handle_pf_alloc_daily_event）、`src/zephyr/pf_alloc/batched_position_builder.py:240`（schedule_buy_orders）。
- 范围：五模块链装配（screen_panel→RegimeMetaAllocator→BudgetChangeHandler→StrategyBook→AdjudicationCenter→BatchedPositionBuilder→三表落库）+ MOD-PA-006 分批建仓全件。
- 排除项：allocation_inputs/allocation_persistence 内部实现（按上游/下游黑盒审，其缺陷归 C 系其他对象/后续轮次）；BudgetChangeHandler 详审以 C01 消费口径为限。
- 生产接线现状：事件链经 `pipeline_events.run_pf_alloc_daily`（pipeline_events.py:449）subprocess 调 CLI 正门；钱包额度真消费方=`scripts/backtest/sim_paper_ledger.py:249`（读 alloc 快照 allocated_capital）。CLI 路径 alpha_provider=None。
- 测试覆盖：tests/pf_alloc/test_allocation_chain.py（27 用例）+ test_batched_position_builder.py（65 用例）=92 passed（5.25s）。注：任务指定 `-p no:cacheprovider` 与 pyproject `[tool.pytest.ini_options] cache_dir` 冲突报 INTERNALERROR，去 flag 后通过——属环境/配置摩擦，非代码缺陷。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | AGGRESSIVE 模式单批 weight_fraction=first_pct∈[0.70,1.0)，无第 2 承接批，违反头注不变量"批次比例和=1.0"（batched_position_builder.py:8 vs :477-480） | batched_position_builder.py:178,479 | **P1** | `build_plan("x",0.08,0.80,"daban").batches` → 单批 fraction≈0.75≠1.0 |
| A | 测试断言强度：test_build_plan_aggressive 只断言 `len(batches)==1`，不断言比例（tests/pf_alloc/test_batched_position_builder.py:453-457）；"批次和=1.0"断言只覆盖 SCALED（:465,699-707） | 同左 | P2 | 阅读该测试函数体 |
| A | sum_effective 在策略构建失败置 0 **之前**计算（:854 vs budgets[sid]=0 于 :892），TOTAL_POSITION_CAP 缩放分母含失败策略（保守方向漂移） | allocation_orchestrator.py:854,873,892,422 | P2 | 构造一策略 build 抛错场景，比对 facts.sum_effective 与实际 Σbudgets |
| A | `symbol_aggregate` 空 dict 在 :855 先行注入 _LayerFacts、Pass A（:876-897）按引用回填——依赖 dataclass 可变+dict 别名，脆但当前正确 | allocation_orchestrator.py:855,859,896 | P3 | 代码阅读（引用语义确认） |
| A | 数学四问：三账闭合 deployed+cash+unallocated=total 推演成立；wallet_weights=abs/budget 换算与 clip 口径自洽；空输入/全灭 fail-closed（screen_panel:647）；NaN 由 _clip01 拦截 | allocation_orchestrator.py:934,980,1089-1121,400-403 | 已查无 | test_cash_three_accounts_reconcile_to_total |
| A | A股口径：T+1 冻结=注入缝 available_cash_provider（:694,1113）；尾盘窗口对齐上交所 2026 规则（builder:100-106）；**100 股整手未在任何一层承载**（计划层只出权重；执行层缺位，义务无人认领） | batched_position_builder.py 全文（无整手逻辑） | P2 | grep 整手/100 股逻辑于 ex_core/sim 链 |
| A.3 | 测试假阳性排查：allocation_chain 27 用例含 fail-closed/不变量/现金闭合断言，强度合格；未覆盖 AGGRESSIVE 比例、sum_effective 失败漂移、Tier3 存量状态路径 | tests/pf_alloc/test_allocation_chain.py:176-503 | P2（缺口） | 对照本表 P1/P2 用例清单 |
| B | 上游：load_regime_input NaN→isfinite 兜底（allocation_inputs.py:419）；alloc_budget_daily 未建表 fail-closed 带指错（:818-826）；防抖/升级 payload 口径 instruction_tiers=[1,2] 与 `"1" in tiers` 判定兼容（budget_change_handler.py:763,855 vs orchestrator:574） | 同左 | 已查无 | 跑 test_allocation_chain 全绿 |
| B | 上游隐式契约：strategy_book target_weight 口径——头注称"相对 strategy_budget 占比"（strategy_book.py:36,124,140），实现为绝对占比（Σ≤budget，:399-400），orchestrator 按绝对口径消费正确——**文档漂移** | strategy_book.py:36 vs :399 | P3 | 阅读两处并跑 build_target_portfolio 实测 Σ |
| C | 下游：**Tier3 强裁生产零触发**——check_convergence/on_firm_violation 全仓无生产调用方（仅同名无关件），_strategy_layer TIER3_TRIM_PENDING 分支生产不可达 | grep 全仓；allocation_orchestrator.py:463-470 永不命中 | **P1** | `grep -rn "check_convergence\|on_firm_violation" src/ scripts/` 排除 handler 本体与 test |
| C | Tier3 存量状态被"预算相等"误清：new==old 走 rule1 上调分支→_retarget_in_convergence `new>=old_target` 含相等→Tier3 转 CONVERGED 无指令（budget_change_handler.py:407-410,891-909）→本轮 freeze/retain 全空→带 Tier3 伤开新仓 | budget_change_handler.py:900-909 | **P1** | handler.sync 两轮同预算，首轮造 Tier3（on_firm_violation），二轮观察 instructions=[] 且 tier=CONVERGED |
| C | schedule_buy_orders/rank_buy_orders/compute_anchor_price/check_batch2_release/gate_batch_order 零生产调用方；BM-BUY-08"不得绕过"纪律闸无生产执行点（orchestrator 只产计划不调用闸） | grep 全仓零命中 | P2 | 同上 grep 法 |
| D | 兄弟口径：单票 cap=min(5%,5%)（orchestrator:488+single_name_cap_caliber）为组合绝对占比；C04 default_single_position_cap=0.05 为策略 NAV 占比——同名"5%"不同基（checklist#4 双承载味，登记不判错） | single_name_cap_caliber.py:37-42; position_sizing_engine.py:188 | P3 | 两处常量对照 |
| D | is_crisis facts 字段装载后四层判定无一人读（:397,866 装载，层函数零引用）——危机在裁决层死载 | allocation_orchestrator.py:397,503-524 | P3 | grep is_crisis 于层函数 |
| E | 静默失败：单策略 build 异常→budget=0+warning+note 留痕（:889-894）合格；订阅者异常隔离（handler:726-732）合格；ChangeLogCollector 永不退订——生产路径 handler 每 run 新建无泄漏，注入复用 handler 的测试场景会累积订阅者 | allocation_orchestrator.py:813-815 | P3 | 注入同一 handler 跑两轮看 collector 行数 |
| E | 重复触发：run_id 随机后缀，重跑=追加行（MergeTree 只增），marker 闸在 pipeline_events.run_pf_alloc_daily 承担当日幂等——幂等责任在调用方且已实现 | pipeline_events.py:478-487 | 已查无 | _date_marker_done 逻辑阅读 |
| E | 时序：防抖日切依赖 current_date 字符串比较（handler:429）；乱序事件（日期回拨）会重置累计——当前单线程事件链可接受 | budget_change_handler.py:429-433 | P3 | 造乱序日期单测 |

## 3 SOTA 对照

| 对象算法 | 结论 | 来源 |
|---|---|---|
| 分批建仓置信度驱动批次 | 对等已有（分批/尾盘执行为卖方实务常见形态，无单一学术真源；2 批+2/3 放行属保守设计） | 轴 F 检索受限（429），按家族对照记录 |
| Regime 驱动缩放/危机响应 | 对等已有：市场对 regime 切换反应迟滞导致持续超险是已知问题，支持事件驱动每日常规再权+快冻结设计 | Man Group "Volatility is Back: Better to Target Returns or Target Risk?"（man.com）；ECB FSR 2020（ecb.europa.eu） |
| Half-Kelly 上游口径 | 对等已有（详见 rpt_c04） | 见 rpt_c04 §3 |
| 尾盘执行窗口对齐上交所 2026 规则 | 已查无英文对照必要（本地交易所规则题）；14:57-15:00 不可撤单语义在 CHECK_AND_AMEND/CLOSING_AUCTION_ONLY 分界正确体现 | batched_position_builder.py:246-267 |

## 4 缺陷清单（按严重级）

1. **[P1] AGGRESSIVE 单批欠部署 0-30% 目标权重**。现状：单批 weight_fraction=first_pct∈[0.70,1.0)（batched_position_builder.py:479），无第二承接批，1-first_pct 份额静默消失；头注不变量"批次比例和=1.0"（:8）自相矛盾。影响与爆炸半径：高置信入场（≥阈值）按 70-100% 部署，执行层落地后=系统性少买（决策偏移，非反向亏损）；当前执行层缺位故未兑现。建议修法：AGGRESSIVE 分支 weight_fraction=1.0（"实质 1 批"语义）或补 batch2 承接余量，并补比例断言测试。验证法：`python -c "from zephyr.pf_alloc.batched_position_builder import BatchedPositionBuilder; p=BatchedPositionBuilder().build_plan('x',0.08,0.80,'daban'); print(p.batches[0].weight_fraction)"` → 0.75。
2. **[P1] Tier3 强裁生产不可达**。现状：check_convergence/on_firm_violation 无任何生产调用方（grep 全仓）。影响：三级升级实为两级，强裁兜底失效；_strategy_layer TIER3_TRIM_PENDING（orchestrator:463-470）成死分支。建议修法：在事件链日结位（run_sim_ledger_daily 或 pf_alloc_daily 执行体）接 check_convergence(exposure) 与 firm 违例直触。验证法：grep 命令见 §2 C 行。
3. **[P1] Tier3 存量状态被预算相等误清**。现状：budget_change_handler.py:900 `new_budget >= old_target` 把"相等"当"上调"，Tier3→CONVERGED 停强裁且零指令；随后 orchestrator 本轮 freeze/retain 全空，策略可带强裁伤开新仓。建议修法：相等走"维持强裁/重发 trim"分支（仅严格大于才停）。验证法：两轮同预算复现（§2 C 行）。
4. **[P2] sum_effective 失败策略漂移**（保守方向）+ **[P2] BM-BUY-08 闸与执行调度五函数零消费** + **[P2] 生产 CLI 路径 alpha_provider=None 致四层裁决/分批计划生产不可达**（诚实降级但需知情：当前生产分配=纯钱包额度+空仓计划）+ **[P2] 100 股整手无人认领**。修法与验证见 §2 对应行。
5. **[P3] 文档漂移组**：strategy_book 权重口径头注 vs 实现；is_crisis 死载；cash_drag_capital 命名实为全钱包闲置合计；BUILDER_STRATEGY_TYPE 未知类型静默归 multifactor（:1145）。

## 5 挂起疑问

1. Tier2 期间"新开仓"语义：收敛中策略 sizing 预算=分配目标（非 handler 批准的渐进值），Tier2 只冻结 Tier1 当日——是否符合 MOD-POS-022 原意，建议 Owner 裁定留痕。
2. AGGRESSIVE 欠部署是否曾按"首仓即全部"意图评审过（blueprint.md 未读，缺材料）。
3. 基线漂移：crisis_gate.py 为未跟踪在途件，其 L2 接线将改 orchestrator——本报告 :813/:866 行号锚点在接线落地后需重验。

## 6 完备性自评

六轴全查。长尾：①allocation_inputs/allocation_persistence 未逐行（黑盒入轴 B）；②blueprint.md 文档未取（挂起 2）；③数据画像（alloc 三表真实 NaN 率/缺失率）未取——CH 只读查询超范围，记长尾；④运行时证据包（近 N 天 error 日志）未取（无权限窗口），以 92 测试绿+实测复现替代。
