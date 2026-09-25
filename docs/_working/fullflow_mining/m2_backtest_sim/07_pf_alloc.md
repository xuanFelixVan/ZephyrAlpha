---
ttl: task_bound
volume: 07_pf_alloc
session: st-commitspeed-tbl-20260924
---

# 07 · pf_alloc 组合分配链（五模块装配体+分配器族）

## 一、环节定义与边界
组合层资金分配：把 regime PIT 概率+策略绩效证据转成 sleeve 权重并持久化，事件驱动再权（SIM_DAILY 事件节拍，非 cron）。上游=simulation 域账本+regime_snapshot_history；下游=模拟盘钱包/决策地图 PP-001 配比。真源=docs/_working/full-auto-chain/S11_assembled_backtest/nodes/pf_alloc_consumer_mining.md（PFA-1..4 四缺口）。

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | regime_snapshot_history PIT 概率（allocation_orchestrator.py:48 PFA-3 喂进分配器）；base_weights/PerformanceScore 由 allocation_inputs 供件（PFA-4 前两缺）；wallet_capital 由装配体产出（PFA-2：账本 flat 100 万与"组合分配"叙事脱钩的解法） |
| 下游消费 | allocation_persistence 落库（DDL=scripts/ch/apply_pf_alloc_ddl.py）；strategy_pipeline/pipeline_events.py 消费 allocation_orchestrator（SIM_DAILY 事件=再权节拍，防抖在 BudgetChangeHandler）；03 册模拟盘链联动 |
| 自动化触发 | 事件驱动（无月度 cron 自注：allocation_orchestrator.py:50-51"每个 SIM_DAILY 事件即再权节拍"——符合宪法 §9.3 事件触发红线）；另有 CLI |
| 真源与注册表 | MOD-PA-007 五模块链；allocation_config.py 参数面；真源节点册 pf_alloc_consumer_mining.md |
| 门禁与质量尺 | tests/pf_alloc/ 20 件（实测计数：test_allocation_chain/test_crisis_gate/test_maxdd_limit_allocator/test_multi_strategy_capital_allocator/test_anchored_cap/test_batched_position_builder/test_correlation_persistence/test_forward_stop_loss 等） |
| 当前运行状态 | **黄**：装配体+13 分配器+持久化全在码，测试面 20 件在；但"生产实证运行记录"（月度再权落库行数）本车道未查 DB（只读挖矿不碰库），留 M5/施工班复核。IBT 侧 105 格权重矩阵空（06 册堵点3）旁证分配链尚未喂整装回测 |

## 三、子模块清单（6 子环节）

| # | 子环节 | 入口 file:line | 状态 |
|---|---|---|---|
| 7.1 | 装配体（PFA-1"链从未被组装"的解） | src/zephyr/pf_alloc/allocation_orchestrator.py:43-59（四 PFA 缺口逐一自注） | 绿 |
| 7.2 | 供件层（base_weights/PerformanceScore 无生产者的补件） | allocation_inputs.py（grep 实锚 allocation_orchestrator 同族） | 绿 |
| 7.3 | 分配器族 13 件（risk_budget/regime_bma_weighting/regime_meta_allocator/vol_target/maxdd_limit/multi_strategy_capital_allocator/strategy_screener_3d/strategy_correlation_gate/signal_synthesis_combiner/tail_hedge_signal/forward_stop_loss/sector_distribution_comparator/synergy_dedup） | src/zephyr/pf_alloc/core/（ls 实测 13 文件） | 绿 |
| 7.4 | 危机门（crisis_gate，分配面熔断语义） | src/zephyr/pf_alloc/crisis_gate.py；test_crisis_gate.py | 绿 |
| 7.5 | 持久化+DDL | allocation_persistence.py；scripts/ch/apply_pf_alloc_ddl.py | 绿 |
| 7.6 | 事件接线（SIM_DAILY 再权节拍） | src/zephyr/strategy_pipeline/pipeline_events.py（grep 消费 allocation_orchestrator 实锚）；batched_position_builder+strategy_lifecycle_event 支撑 | 绿（结构）；运行实证黄（同台账向6） |

## 四、堵点与病灶
1. **生产运行实证缺**：装配体 09-16 车道 D 建成后，落库行数/再权次数无本车道可查证据（不碰 DB 红线下如实标黄）。修法：一条只读 SQL 数 allocation 落表行数+最近 SIM_DAILY 事件时间戳。XS，复核命令给出。
2. **与 auto_mount PP-001 的双头配比风险**：auto_mount 第③步"新 sleeve 0.05 起步/老 sleeve 等比缩水"（02 册 2.3）与 pf_alloc 证据×风险预算提案是两条配比路径，only-add 语义门+--rebalance 只出 diff 不落图（SLE-1 Owner 门位）是当前护栏；但两边都动 sleeve 权重，长期需裁定唯一配比真源。**待裁**（入 pending_rulings）。
3. batched_position_builder/simulation 域接口的映射在 pipeline_events——若 SIM_DAILY 事件改名/迁移，装配体静默失联（事件契约无对账测试）。修法：事件 schema 版本断言。S。

## 五、提速与合并机会
- 7.3 十三分配器中 sector_distribution_comparator/synergy_dedup/tail_hedge_signal 三件在 tests/pf_alloc 外未见独立测试（20 件实测清单未含）——若生产未用可按内收判据 w5_1"零触发零消费→退役"评审（归总筹，不代判）。
- 与 06 册 6.7 审计的"③组合构建"是同一缺口的两侧（IBT 侧要 7 态×15 员矩阵，pf_alloc 侧有分配器族）——合流施工=一次施工双闭环。

## 六、自审闸三态
**挖干可施工**（6 子环节 file:line 实证；运行态黄有明确补证命令）。堵点 2 待裁，1/3 可施工。

## 七、复核命令
```bash
sed -n '43,59p' src/zephyr/pf_alloc/allocation_orchestrator.py
ls src/zephyr/pf_alloc/core/ | wc -l    # 13
ls tests/pf_alloc | wc -l               # 20
grep -rn "allocation_orchestrator" src/zephyr/strategy_pipeline/pipeline_events.py | head -3
# 运行实证（施工班补）：数 allocation 落表行数（经 DatabaseService 只读）
```
