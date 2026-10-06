---
ttl: task_bound
rule_form: data
verifiability: manual
title: 条件化做T 预注册假设卡（状态选择性做T，市场/情绪状态门+成本假设+E4考试判据，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-22
status: frozen（本卡于任何考试取数之前写死；实验启动后任何字段不得改动，改动即作废重开）
family_id: T0-CONDITIONAL
session: st-t0-revival-20260922
parent_context: 裁定#399 二（做T复活改裁授权）+ 裁定#331/#386（旧形态终止/禁复试图救口径）+ etft0_prereg_card.md（方法论母本，docs/_working/archive/2026-09/bizmine_night/）+ docs/_working/daily_loop_campaign/02_state_vocabulary_unification.md（丁线状态/情绪词表）+ scripts/audit/cost_trio_exam.py（成本判据复用真源）
---

# T0-CONDITIONAL：市场/情绪状态选择性做T 是否存在正净期望状态子集（预注册考试卡）

## 0. 裁定链定位（先读，防口径漂移）

- #331（原 #304 撞号勘误）终止的是**旧形态=无条件全状态做T**；#386 封死的是 **S-OWNER-001 策略级复试图救**。
- #399 二明确授权：做T 非死刑，方向=**按市场/情绪状态选择性做T（不同状态不同考试）**，复活唯一口=新预注册假设卡+考试制。本卡就是那个正门。
- 本卡是**考试族卡**（真实成交流水成本侧+状态门分层），不是策略上线卡；任何 verdict 都不构成实盘放行（实盘准入门=B-007 pilot 档 Owner 门位）。

## 1. 假设（H1，唯一，写死）

**存在可测的市场/情绪状态子集，使该状态下"同 symbol×day 买卖配对"的做T 成本经济学由不可行转为可行：状态命中日配对的净价差（CST-T0-001 口径）均值为正，且状态命中日配对的毛边际显著高于非命中日配对。**

零假设 H0：状态命中子集与非命中子集的净价差无可区分改善，或任何子集净期望均不为正。

诚实条款（承 ETFT0 母本）：本卡结论是**成本经济学级**（状态条件下的成本门可行性），不是"找到赚钱策略"；"绿区≠净边际正"同样适用于状态命中子集。全部结果全量披露（含 RED），禁事后挑样。

## 2. 状态选择门（先于测量，frozen；消费丁线词表）

状态词表真源：官方词表立法件（docs/_working/vocab_legislation/01_official_state_vocabulary.md）+ src/zephyr/shared/vocab/market_state.py（SH-VOCAB-001 常量本体）。

### 2.1 宏观门（历史可复现，frozen）

- 数据源：`c1_backtest.regime_state_anchored`（vol_pct=000300 hv20 滚动 250 日分位连续灰度；dominant=HMM 七态标签）。
- PIT 规则：配对日 T 的状态取 **T-1 交易日** 读数（承 T 车道/ETFT0 双保险口径），asof 向后 7 自然日容差，弃日计数披露。
- 做T 允许条件（OR）：`vol_pct(T-1) > 0.700`（H 桶，承 frozen 边界 q33=0.328/q67=0.700 的 H 段）**或** `dominant(T-1) ∈ {r3, r12}`（牛市趋势/突破态，HMM 七态官方语义）。
- 禁做：L/M 桶且 dominant ∉ {r3, r12}（低中波非趋势态——510300 判定不外推的镜像面：低波=做T 最不利）。

### 2.2 情绪门（丁线情绪周期六段，frozen）

- 词表：情绪周期轴官方=TDM 六段（capitulation 投降/accumulation 蓄势/ignition 点火/expansion 主升/euphoria 亢奋/distribution 退潮）。
- 做T 允许：`∈ {ignition, expansion, euphoria}`（情绪上行三段）；
- 禁做：`∈ {capitulation, accumulation, distribution}`（冰点/蓄势/退潮——退潮期做T=接飞刀，方向陷阱登记面已立法）。
- 数据源与 PIT：**前瞻接线义务**——sentiment_panel 自 2026-09-01 起积累（PIT T 收盘算 T+1 用）；历史回溯窗若无六段历史标签，则考试对该窗降级为**单宏观门**并显式标记 `emotion_gate=unevaluable`（fail-closed 披露，禁用当期标签回填历史——前视偏差禁令）。

### 2.3 门语义（frozen）

- 双门可用时：宏观门 AND 情绪门 均允许才做T。
- 情绪门不可用时：单宏观门判定，verdict 措辞必须携带 `emotion_gate=unevaluable` 限定。

## 3. 成本假设（frozen，复用 cost_trio 判据）

- 成本口径唯一真源=CST-T0-001：rt 31.2bp 固定口径（佣金双边 6+印花 5+过户双边 0.2+滑点 2×10）；min5 抬升单列披露（承分包1 对账）。
- 开仓前置：毛价差 ≥30bp（min_expected_edge_rate=0.003）。
- 可测规则链（状态命中日配对集合上）：
  1. `edge_precondition_hit_rate = edge_ge_30bp / n_gate_pairs`，须 **≥0.30** 才进入净期望判定（前置命中率门槛，写死）；
  2. `net_mean = 净价差 mean > 0`（CST-T0-001 固定口径）；
  3. 对照组：非命中日配对同口径四数全量披露（状态区分度的证据面，非独立判定门）。

## 4. 样本区间（frozen）

- 考试材料=真实成交流水：`data/backtest_artifacts/bt-*.json` trade_log，D=2026-09-09 定稿锚点（D 前全锁/D 后可考，P6 真源）；配对=分包1 cost_trio 同一规则（symbol×day 双边配对，全侧 VWAP 近似）。
- 窗口：材料窗即考窗（当前=D 后 4 交易日）；前瞻滚动积累，样本积累后**原样重跑**，禁改卡重跑（改卡=作废重开）。
- 状态变量历史覆盖：regime_state_anchored 2017-07-11→今（2236 行，实测）；sentiment_panel 2026-09-01→今（25 行，实测）。

## 5. 判据与土规（frozen，REG-VALM-001 同源）

| 土规 | 阈值 | 违反时 |
|---|---|---|
| 配对数 | n_gate_pairs ≥30 | `INSUFFICIENT_SAMPLES`（禁硬出方向性结论） |
| 状态门命中 | n_gate_pairs ≥1 | =0 则 `STATE_GATE_NEVER_TRIGGERED`（门规则与材料窗不相容，如实披露） |
| 前置命中率 | ≥0.30 | 未达=门内毛边际不存在，`FAIL`（不开仓前置都不成立，无需再看净期望） |
| 净期望 | net_mean > 0 | 未达=`FAIL`（fail-closed，禁"接近为正"措辞） |

verdict 枚举（写死）：`PASS-待考`（三土规全过+双门可用）/ `PASS-单门`（过但 emotion_gate=unevaluable，须双门复考）/ `FAIL` / `INSUFFICIENT_SAMPLES` / `STATE_GATE_NEVER_TRIGGERED`。**fail-closed：任何数据缺失/门不可评/样本不足都落到后两态，禁硬出。**

## 6. E4 考试执行（frozen）

- 脚本：`scripts/audit/t0_conditional_e4_exam.py`（判据件住 scripts/；产物=docs/_working/t0_revival/t0_conditional_e4_result.yaml + t0_conditional_e4_verdict.md）。
- 顺序纪律：本卡 frozen 先于脚本取数（mtime 链可核）；禁裸跑回测、禁卡外判据。
- 零状态变更：不动任何 verdict/can_deploy/台账行；查库只读（DatabaseService reader）；产物只写 docs/_working/t0_revival/。

## 7. 与既裁口径的边界（防撞车披露）

- 本卡与 #386 S-OWNER-001（300ETF 波段+底仓T）考试窗不重叠：S-OWNER-001 是策略级 E4 OOS 不及格件，禁复试图救；本卡是**状态条件化的成本经济学考试族**，材料=D 后真实流水配对，不重建 S-OWNER-001 任何参数。
- 与 ETFT0 三宇宙（振幅勘测族）的关系：ETFT0 回答"哪些标的振幅经济学可行"（标的维），本卡回答"哪些状态下出手"（状态维）；两轴正交，结论互不替代。
- 策略实现（若未来 PASS）：须另立实现级预注册卡（因子族+执行语义），本卡 verdict 不构成实现授权。
