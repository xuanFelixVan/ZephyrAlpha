---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-E-L1
flow: entry_flow
node_count: 9
session: mine-fullchain-tdm-20261015
---

# S_TDM-E-L1 大盘总闸/市场状态判定（9 节点）

## 1. 定义

一句话：全链唯一开闸裁定者——先证明环境允许交易再谈买什么（PT-01"大盘死了别买"），双轨判定宏观 7 态×微观情绪六段，输出预算带+六段状态+策略路由三件套一次 broadcast 全图。

展开：本体不自算宏观——消费 RegimeSnapshot 的 7 态概率分布（4 态 HMM r1-r4 + CRISIS/RECOVERY/BREAKOUT overlay，真源 10_regime_detector_spec.md + regime_detector.py）当谨慎度系数；微观情绪六段（capitulation/accumulation/ignition/expansion/euphoria/distribution）由 AGG 锚定状态机合成。R-055a 数值侧 fail-closed：缺供数落地板值 0.30 并带 risk_signal_source 溯源，禁把降级读作"确无风险"。九节点=总闸本体+七传感器（S0 宏观/S0-1 新闻情绪/S1 指数/S2 涨停跟随/S3 连板溢价/S4 合成 VIX/S5 日级水温）+AGG 市场状态判定。骨架总纲写本环节 10 节点，地图实读 9（漂移记录于 §4）。

## 2. 六向台账

### 2.1 输入面（有证）
- 七传感器 feed 边：S1/S2/S3/S4→AGG（edges 块前 4 条，payload=data，frequency=daily）；S1→S3 feedback 边（lag=T-1）。
- 外部入边：TDM-F-C3→TDM-E-L1-AGG、TDM-F-C3-05→TDM-E-L1-AGG（传感器可靠度反馈）；TDM-E-L0-04→TDM-E-L1-AGG；TDM-E-L1-S5→TDM-E-L0-04。
- 数据供数：L9 源线 45 节点为挂点面（TDM-E-L9-AGG=src/zephyr/data/l9_readiness_aggregator.py）；宏观序列翻译=config/macro_indicator_series_map.yaml（16 条实读于骨架批）。

### 2.2 输出面（有证）
- 出边 25 条（全图最多之一）：L1→L2；AGG→L0/L2-05-1/F-C1/F-C1-01/P-P1/P2-01/P3-01/X-S1/X-S1-04/L9-V2——"一次判定 broadcast 全图"在边上兑现。
- 状态矩阵 6 格挂 TDM-E-L1（capitulation/accumulation/ignition/expansion/euphoria/distribution，state_matrix.cells 24 格之一）；ignition/euphoria/distribution 三格 mounted_reason=pending-owner-adoption+2026-09-30 C5 禁用标记（PP-001 无防御 sleeve，填格=Owner 资金分配门位）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-E-L1（line 457-528）+S0..S5/AGG（line 529/566/602/636/695/732/771/803）。
- 宏观态真源：docs/01_policies_and_standards/sop/ 10_regime_detector_spec.md（D-SIGNAL-04）+src/zephyr/regime/core/regime_detector.py（地图 line 97-99 注记）。
- goal 块 family=F15 系；casebooks 挂 12 处（CASEBOOK-001#outage/alert/task_reconcile 等）；全图仅 2 个 verified 节点之一=TDM-E-L1（confidence=verified）。

### 2.4 代码模块（有证，9/9 ref 实存）
- 总闸/AGG：src/zephyr/regime/core/regime_detector.py（MOD-REGIME-001）、anchored_state_machine.py（MOD-REGIME-001）。
- 传感器：index_sensor.py（MOD-REGIME-016）、synthetic_vix.py（MOD-REGIME-002，SVX-1-P0 治理在案）、signal_ashare/limit_up/limit_up_followthrough.py（MOD-SIG-078）、lhb_premium_analyzer.py（MOD-SIG-057）、alt_data/policy_expectation_analyzer.py（MOD-ALT-010）、intelligence/news_sentiment_analyzer.py（MOD-INT-AISA）、signal_ashare/core/daily_condition_sensor.py（MOD-SIG-135）。

### 2.5 门禁约束（有证）
- 四门同 L0（MAP-ALIGNMENT/TDM-MOUNT-COVERAGE/ALGO-NOTE-SYNC/ALGO-FLOW-LINK，双册实证：in_process_gate_registry.yaml total_gates: 107、gate_registry.yaml total_gates: 191）。
- S2/S3/S4/S0-1/AGG 五节点 algo_note 显式记"2026-09-15 ALGO_FLOW 块出仓至 docs/03_modules/_domain_*/algo_flow/*.yaml"——ALGO-FLOW-LINK 门管 external 锚存在性。

### 2.6 自动化触发（有证）
- S1/S3/S4/S0/AGG=盘前 premarket；S2/S5=盘中 intraday（S5 9:35 首算，唯一盘中可变 L1 输入）；S0-1=continuous。
- dloop 链：daily_loop_master_switch 内 regime 新鲜度体检（消费方口径滞后>1 交易日=缺）+盘中 L1（intraday_l1_tracker，MOD-PLAN-028）；供给方阈值已 Owner 批对齐为 1（2026-09-21，治本 2026-09-15~18 断供根因）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 七传感器+反馈边+L9 挂点面全在册 |
| 输出面 | pass | 出边 25 条+状态矩阵 6 格+broadcast 三件套 |
| SSOT | pass | spec 真源+macro 翻译册+ROOR+casebooks 12 处 |
| 代码模块 | pass | 9/9 ref 实存；唯一 verified 节点在本环节 |
| 门禁约束 | pass | 四门+ALGO_FLOW 出仓锚五处 |
| 自动化触发 | pass | premarket/intraday/continuous 分档+dloop 双挂点 |

**总评：pass（6/6）**。

## 4. 缺口与建议

1. 状态矩阵 TDM-E-L1 的 ignition/euphoria/distribution 三格 pending-owner-adoption+C5 禁用（PP-001 无防御型 sleeve）——防御档新设属 Owner 资金分配门位，已在格内如实标记，建议列入 Owner 议题清单。
2. S0 宏观传感器"政策（监管动态人工录入）"为半人工通道——全自动面缺口，建议挂 intelligence 事件采集自动化批次。
3. 骨架总纲写 L1=10 节点、地图实读 9（S0-S5+S0-1+AGG+本体）；骨架计数漂移建议随下批骨架修订对齐（同漂移还见于 L2/L3/L4/C2，见各册）。
