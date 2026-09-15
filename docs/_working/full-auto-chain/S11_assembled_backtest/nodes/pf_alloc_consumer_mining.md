---
ttl: task_bound
title: T1-α 节点挖矿：pf_alloc 实盘消费端（MOD-PA-007 组合资金分配）
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 节点挖矿 7：pf_alloc 实盘消费端（MOD-PA-007 RegimeMetaAllocator 组合资金分配）

> 挖矿依据：decision_kernel_mining §5 / tdm_sleeve_allocation_mining §5 共同列出的待挖
> 子节点——"PP-001 静态权重→实盘动态预算之间的 MOD-PA-003/PA-007 从未与回测侧对表"。
> 疑点=组合层资金分配结果在回测侧有消费、实盘侧可能无消费端或链路断开。
> 方法：全仓 grep 定位模块与全部消费方 + 实盘/模拟盘链路全文精读 + ClickHouse 只读实证
> （2026-09-15，ch_reader 只读查询，零写库）。产出=数据，采纳裁定归主力会话施工班。

## 1. 头号发现 PFA-1（P0）：MOD-PA-007 实盘消费端不存在——整条 A 模型分配链是"无生产调用方的纯库"

**模块定位**：MOD-PA-007 = `src/zephyr/pf_alloc/core/regime_meta_allocator.py`（879 行全读）。
分配公式 allocation=normalize(Base×PerfScore)、floor 5%/cap 40%、global_shrinkage 总暴露缩放、
冷启动中性/比例——数学本体合格（见正面清单）。问题全在消费端：

**调用方全量核查（grep 全仓 + 逐文件精读）**：

| 链上模块 | blueprint 声明的消费关系 | 实际生产调用方 | 证据锚点 |
|---------|------------------------|--------------|---------|
| MOD-PA-007 RegimeMetaAllocator | [CONSUMERS] MOD-POS-020/022（regime_meta_allocator.py:5） | **零**。唯一调用=tests（test_regime_meta_allocator.py、test_e2e_redblue_night001.py:367-399）+ 自身 sensitivity grid | `allocate(` 全仓仅 tests 命中 |
| MOD-POS-020 StrategyBook | 消费 BudgetAllocation（build_target_portfolio budget 参） | **零**。仅 tests + cold_start_progression（包内互引） | strategy_book.py:371 `_current_budget=1.0 # Phase 1 等权占位，Phase 2 来自 RegimeMetaAllocator`——Phase 2 从未到来 |
| MOD-POS-022 BudgetChangeHandler | 收 BudgetChanged 事件 | **零**。sync_from_allocator（budget_change_handler.py:640）docstring 自述"生产编排层每个分配周期拿到 BudgetAllocation 后调用本方法一次即可"——该编排层不存在 | memo 33 自证：33_budget_change_handler.md:22（2026-08-19 复核注记）"handle_budget_change 全 src 无生产调用方"；:153 "当前是无生产调用方的纯库模块，接线随 G15→G14 集成时完成（待决策）" |
| MOD-POS-021 FirmRiskAggregator | 产 FirmTargetPortfolio 交 MOD-POS-001（firm_risk_aggregator.py:5） | **零**。仅 tests + single_name_cap_caliber 的常量 import | — |
| MOD-PA-006 BatchedPositionBuilder | [CONSUMERS] 40_execution_broker（batched_position_builder.py:5） | **零**。仅 tests/compliance/test_runtime_wiring.py:44,268（合规接线红队测试） | "不读市场态(只消费budget数字)"（:8）——消费的 budget 数字本身无生产来源 |

**核心结论**：分配结果（BudgetAllocation）从模块产出到实盘下单引擎（ex_core TradingSession）
之间的每一环都存在且各自带测试，但**没有任何一环被生产编排调用**。这不是"链路断在一处"，
而是"链路从未装配"——memo 33 已诚实登记（"设计内延期非烂尾"），但下游治理登记却把它
当作既有能力引用（见 PFA-4）。

## 2. PFA-2（P0）：实盘/模拟盘的真实资金分配=100 万平钱包——与 MOD-PA-007 零交集（CH 实证）

**实盘链路的真实形态**（57 号文 GAP-2 过渡形态，S09 已挖排班面、本挖矿补分配面）：

- 盘中会话：`scripts/start_paper_session.py` → `zephyr/ex_core/trading_session.py` rebalance()
  （trading_session.py:342）——`strategy.generate_target_weights → _apply_position_cap（:356，
  唯一"分配约束"=单标的权重上限）→ _compute_order_deltas（:357）→ _calc_target_qty（:509，
  total_asset×weight/price）`。**链上无 budget 层/无 Shrinkage/无 floor5% cap40%/无
  PerformanceScore/无冷启动比例**；且当前实机不跑（S09 实证：计划任务缺席+Disabled+mock
  信号彩排口径，start_paper_session.py:307-309）。
- 模拟盘账本：`scripts/backtest/sim_paper_ledger.py`——**一策略一钱包固定 100 万**（:9
  INVARIANTS"初始 100 万=Owner 批准"、:49），内置引擎恐慌日**全仓 all-in**（:102-107
  `shares = cash / px_now`），其余策略只写开户行"策略引擎未接线"（:216-218）。

**ClickHouse 只读实证（2026-09-15）**：

| 表 | 实测内容 | 分配语义 |
|----|---------|---------|
| c1_backtest.sim_pocket_daily | 56 行 / 54 交易日（2026-07-01~09-15）/ **4 策略 × 各 1,000,000 平钱包**（STR-VREV-025、STR-MULTIFACTOR-001、STR-AUTO-001、STR-E-TIMING-001）；signal 枚举=open/cash/entry/holding/exit | **无任何 budget/allocation 列**；资金=等额平钱包，无跨策略分配 |
| c1_backtest.sim_trade_log | **仅 5 行**：1 笔 replay_demo 交易 + 3 笔" C1 自动开户" | 无调仓/调预算事件 |
| c1_backtest 全库 8 表 | hypothesis_precheck / node_verdict / regime_snapshot_history / regime_state_anchored / sim_platform_journal / sim_pocket_daily / sim_trade_log / strategy_screen | **全 CH（c0/c1_backtest/c1_market/c3_fundamental 四库）无任何 alloc/budget/shrinkage 表**——分配结果从未落库 |
| MOD-PA-007 blueprint 全景节 | "数据流图 (dataflow) \|（无节点）\| N/A"（blueprint.md:377） | 模块声明侧自证：分配产物无数据集登记 |

**与姊妹发现同构**：tdm_sleeve_allocation_mining 的"死成员假组合"是回测侧 44.1% 权重被
静默再归一；实盘侧同类静默降级=**"一策略一钱包平权"**——floor5%/cap40%/Shrinkage/绩效
后验这套防饿死防集中机制在实盘侧整体不存在，且因链路未装配而**无人知道它该生效**。
方向上实盘侧更"安全"（平钱包无集中风险），但回测证据（整装组合的权重结构）外推实盘时
**分配假设完全失效**。

## 3. PFA-3（P1）：regime/风控信号在实盘分配里零消费——修正姊妹节点 F2 的"实盘侧"描述

- regime_detector.py:5 声明 [CONSUMERS] MOD-PA-007；RegimeDetector 生产调用方实测仅
  print_regime_history.py:135（回测供给链 manual CLI）+ 验证脚本 + shrinkage_provider.py:314
  （回测）。**实盘运行时没有任何组件消费 regime 概率/Shrinkage**。
- **修正**：regime_supply_chain_mining F2 表述"实盘运行时链消费方式=灰度概率×Shrinkage：
  RegimeMetaAllocator（MOD-PA-007）消费 RegimeProbabilities 做 budget 分配"——该"实盘链"
  是**纸面链**（模块存在、调用方不存在，PFA-1 实证）。F2 推出的"回测外推实盘系统性偏乐观"
  结论方向仍成立，但机制比 F2 描述的更弱：不是"实盘会被 Shrinkage 压缩而回测不会"，而是
  **"实盘连被压缩的分配器都没有"**。RSC-2（Shrinkage 进回测）的裁定前提应更新：回测加
  Shrinkage 是向纸面口径对齐，先要裁定"目标口径到底是满仓还是 Shrinkage 节流"（Owner 决策位）。

## 4. PFA-4（P1）：TDM 把 MOD-PA-007 登记为"月度调权引擎"——三件能力实物均缺，治理登记失真

- trading_decision_map.yaml:3889-3926（TDM-F-C3-03 sleeve权重调权）：module_ref=
  regime_meta_allocator.py / MOD-PA-007，`activation: postmarket`、`ai_autonomy: auto`，
  algo_note 写明月度调权公式+防过拟合三纪律。实物缺口：
  1. **base_weights 无来源**：allocator 的 base_weights 是构造参数（:310），全仓无任何代码
     从 TDM/PP-001/fw-tdm-current 加载先验权重传入；
  2. **月度调权无调度体**：activation=postmarket 无事件接线（schedule.yaml 21 槽全数据层，
     S09 已实证）；
  3. **PerformanceScore 无生产者**：StrategyBook.get_performance_snapshot（strategy_book.py:567
     "供 RegimeMetaAllocator 后验分配（Phase 2）"）同样零调用方。
- **登记矛盾**：strategy_production_map.yaml:328-335（E8 组装与资金分配）诚实标注
  `build_status: partial`+"TDM 组合流对接未闭环"；而 candidate_module_registry.yaml:17753
  的审计注记写"仓位上限+策略激活**已由 MOD-REGIME-001→MOD-PA-007→StrategyBook production
  链覆盖**"（以此否决 B1-00153 候选项）——同一事实两图两口径，registry 把未接线链当
  "已覆盖"证据，属治理登记失真（宪法 §4.3 文档矛盾=事故同类）。

## 5. PFA-5（P2）：三处口径漂移——"同一 allocator 两边参数同源"无从谈起

| # | 漂移 | 证据锚点 |
|---|------|---------|
| 1 | STR-VREV-025 注册表 position_sizing="波动率目标化 K=target_vol/σ，EWMA 平滑，区间截断"（strategy_registry.yaml:139）；sim 引擎实际=恐慌日**全仓 all-in**（sim_paper_ledger.py:102-107）；code_path 的 lane_e_quantile_baseline.py 亦无 vol-target 实现——**注册表声明两侧都无实现** | strategy_registry.yaml:139 vs sim_paper_ledger.py:102-107 |
| 2 | 成本口径：sim 冻结土规 买 2.5bp+5bp/卖 2.5bp+10bp+5bp（sim_paper_ledger.py:52）vs 整装回测 佣金万 0.854+印花税万 5（vectorized_engine.py:104/matching_logic.py:67-77）——两套成本常量无同源真源 | 同左 |
| 3 | 执行口径：sim=当日收盘判定收盘执行（sim_paper_ledger.py:9 INVARIANTS）vs 整装回测 execution_lag_days=1 次日开盘（vectorized_engine.py:199-206）——两条"回测→实盘"名义链自身先分叉，将来谁代表实盘口径无裁定 | 同左 |

## 6. PFA-6（P2）：pf_alloc+position 库边界死成员清单（防后续审计再误判）

- pf_alloc/core 14 件生产消费实况：forward_stop_loss（panic_rebound_depth.py:149，sim 内置
  引擎同族）、strategy_correlation_gate（performance_attribution_engine.py:168→仅
  risk/core/performance_attribution_degradation 消费→后者仅 tests）、regime_meta_allocator
  （tests）、synergy_dedup（tests）——**其余 10 件**（vol_target/maxdd_limit/risk_budget
  (pf_alloc)/screener_3d/signal_synthesis/regime_bma/tail_hedge/sector_comparator/
  multi_strategy_capital/batched_position_builder）**零生产消费**。
- MOD-PA-003 multi_strategy_capital_allocator：blueprint §7.4 判"可能降级/重构"但称其
  "有活跃生产依赖"（regime_meta_allocator blueprint.md:303）——grep 实测同样零生产调用方，
  "活跃生产依赖"陈述过期。
- attribution_meta_iteration.py:300 推荐语指向"30 号 RegimeMetaAllocator budget 上调评审
  入口"——推荐链终点是不存在的入口。
- cold_start_progression（30 号 §6.7）与 allocator cold_start_ratios 接口双向就绪、零调用方。

## 7. 六向挖矿日志表

| 向 | 内部发现 | 外部发现（URL+发布方+年份） | 判定 |
|----|---------|---------------------------|------|
| ①上游 | PP-001 sleeve 权重→MOD-PA-007 base_weights 无读取路径（§4 缺口 1）；PerformanceScore 生产者不存在 | 多策略组合 meta 层分配应有先验权重+后验绩效双输入（30 号设计即此，Morwane/multi-strategy-alpha-book 实证 regime 做 risk-throttle，github.com，2025 前后） | signal |
| ②下游 | 分配结果→下单引擎闭环整体未装配（PFA-1）；实盘真实分配=平钱包（PFA-2） | paper→live 过渡期必须保证回测/实盘同一分配语义（Concretum 生产十课，concretumgroup.com，访问 2026-09） | signal |
| ③机制 | 两边口径同源性无从谈起（PFA-5）；registry 把未接线链当已覆盖（PFA-4） | — | signal |
| ④后端 | 全 CH 无分配落库表+blueprint dataflow 无节点（PFA-2）；接线就绪适配器已预留（sync_from_allocator L640/on_budget_allocation L594） | — | signal |
| ⑤前端 | pano-engine.js 仅展示模块全景，无分配结果透出面——登记不施工 | — | 已查无 |
| ⑥数据字段 | sim_pocket_daily 缺 budget/allocation_source 溯源列（接线后可对账）；regime_snapshot_history 已有 shrinkage 列可作分配输入真源 | — | signal |

**计数：signal 5 / noise 0 / 受阻 0 / 已查无 1（⑤前端）。**

## 8. 正面清单

- **MOD-PA-007 模块本体是合格库件**：water-filling 投影+Σ=1 硬不变量兜底（:660-670，
  AI-NIGHT-001 #206 修复实证）、冷启动中性强制+越界校验（:392-397）、CRISIS floor 当前
  参数域不可达性的双测试锚定（:190-192，不夸大生效范围）。
- **依赖倒置纪律好**：budget_change_handler 不 import pf_alloc（duck-typing，:654 注释）；
  regime 概率纯数据入参（regime_meta_allocator.py:4）——接线时无 import 环风险。
- **接线就绪件已预留**：sync_from_allocator/on_budget_allocation 适配器+persist_path 跨日
  快照（fail-closed ZA-POS-0044）——装配成本=一个编排调用，非重写。
- **断点登记诚实**：memo 33 复核注记明示"无生产调用方的纯库模块"；sim 账本引擎未接线时
  不伪造信号/收益（sim_paper_ledger.py:13 注记）；strategy_production_map E8 诚实标 partial
  ——三处留痕使本挖矿可完整复原真相，无静默腐烂。

## 9. 修复优先级裁定建议

| 项 | 级别 | 动作 |
|----|------|------|
| PFA-1 | P0 | Owner 决策位：G15→G14 编排件立项（谁在哪个事件里调 allocate+sync_from_adapter+Budget 落库）或显式裁定 A 模型分配链延期并改登记；**同步修正 candidate_module_registry.yaml:17753 的"production 链覆盖"表述**（治理登记失真，防后续立项被错误否决） |
| PFA-2 | P0 | sim 钱包先加 budget/allocation_source 溯源列（低成本，CH 表结构变更走数据通道）；"sim 侧要不要消费分配层"与 PFA-1 合并裁定，不单独施工 |
| PFA-3 | P1 | RSC-2（Shrinkage 进回测）施工前先裁定目标口径（满仓 vs Shrinkage 节流）——本发现为其裁定输入 |
| PFA-4 | P1 | TDM-F-C3-03 补交付状态标注（algo_note 加"编排未接线"或引入 build_status 字段），消除与 strategy_production_map partial 的矛盾 |
| PFA-5 | P2 | 三口径同源化登记：成本常量单一真源（与 T1A-4 同件）、sim/整装执行口径裁定、STR-VREV-025 position_sizing 声明与实现对表（改声明或补实现） |
| PFA-6 | P2 | pf_alloc 死成员清单落模块翻译/capability card（标注"库件，无生产消费方"）；blueprint MOD-PA-003 "活跃生产依赖"过期陈述勘正 |

## 10. 封矿判定

- **本节点主体封批**：消费端全量核查完成（MOD-PA-007 及其下游四模块调用方逐一 grep+精读，
  全部带 file:line）；实盘/模拟盘真实分配形态经 CH 只读实证（平钱包+零分配表）；与回测侧
  口径漂移三处 concrete 到锚点。
- **未枯竭部分**：G15→G14 编排件设计位（事件源选型：DataScheduler 唤醒 vs pipeline_events
  新 kind，S09 已有先例可复用）——属施工设计非挖矿，转施工班。
- 一句话结论：**MOD-PA-007 是一台造好了但从没接过电的分配机——回测侧的组合资金语义是
  "满仓再归一"，实盘侧是"一策略一百万平钱包"，两边之间隔着一整条未装配的 A 模型链；
  最大的风险不是链断（断点都留了痕），而是 registry/TDM 把这条纸面链当既有能力引用，
  让后续立项误以为"资金分配已被覆盖"。**
