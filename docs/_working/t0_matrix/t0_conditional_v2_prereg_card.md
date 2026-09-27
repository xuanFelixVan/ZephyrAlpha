---
ttl: task_bound
rule_form: data
verifiability: manual
title: 条件化做T 预注册假设卡 V2（全窗日内往返材料+六段情绪门可用后的双门考试，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: "2026-09-24"
status: frozen（本卡于任何全窗考试取数之前写死；实验启动后任何字段不得改动，改动即作废重开）
family_id: T0-CONDITIONAL-V2
parent_family: T0-CONDITIONAL（docs/_working/t0_revival/t0_conditional_prereg_card.md，保持 frozen 不动）
session: st-t0-matrix-20260924
ruling_basis: 裁定#399 二（做T 复活唯一口=新预注册假设卡+考试制）
---

# T0-CONDITIONAL-V2：全窗日内往返材料上，市场/情绪双状态门是否使做T 成本经济学转为可行

## 0. 为什么是"另立一卡"而不是"重跑 v1"（先读，防口径漂移）

三条实测事实，每一条都使 v1 的原样重跑**不能**产生新结论：

1. **v1 考件自带自我作废条款**：`scripts/audit/t0_conditional_e4_exam.py:147-148` 明文
   `if emotion_ok: raise SystemExit("FAIL: 情绪门历史已可用，但本脚本尚未实现双门取数——按卡纪律作废重开，禁单门硬出")`。
   本班把情绪门接成可评（见 §2.2）后，v1 考件按纪律必须作废重开，**不得打补丁**。
2. **v1 考窗样本不随时间增长**：v1 §4 材料窗="D 后 4 交易日"。2026-09-24 实测重跑=**逐位复现**
   09-22 基线（24 对 / 0 净正 / 0≥30bp / 毛 −9.2bp / 毛 p50 −5.13bp），配对日仍只有
   2026-09-14、09-15 两日，全材料最新成交日=2026-09-15（沙盘流水未再产出新日）。
   ⇒ 卡面"样本积累后原样重跑"的前提（流水在积累）不成立，样本恒为 24。
3. **v1 的 24 对不是日内往返**（本班实测，材料机械定性）：`data/backtest_artifacts/bt-*.json`
   共 60 件 / 130,998 笔，其中**仅 6 件的 timestamp 带日内粒度**（共 3,900 笔，跨 2026-02-27→2026-09-01）；
   其余 54 件（127,098 笔）timestamp 只有日期。v1 考窗两日（09-14/09-15）落在 `bt-fw-*`
   日线走查件内 ⇒ 其"同日买卖配对"是**同一日线 bar 的聚合产物**，不构成做T 往返。

结论：扩样本必须换材料定义，而换材料定义按 v1 §4"改卡=作废重开"⇒ 只能另立本卡。
**v1 卡与其首考产物一并保持原样入库，作为基线证据**（红蓝复现锚点）。

## 1. 假设（H1，逐字继承 v1 §1，禁改）

**存在可测的市场/情绪状态子集，使该状态下"同 symbol×day 买卖配对"的做T 成本经济学由不可行转为可行：状态命中日配对的净价差（CST-T0-001 口径）均值为正，且状态命中日配对的毛边际显著高于非命中日配对。**

零假设 H0：同 v1。诚实条款（承 v1 §1）：本卡结论仍是**成本经济学级**，不是"找到赚钱策略"；
全部结果全量披露（含 RED），禁事后挑样。

## 2. 状态选择门（先于测量，frozen）

### 2.1 宏观门（逐字继承 v1 §2.1，零改动）

- 数据源：`c1_backtest.regime_state_anchored`（vol_pct=000300 hv20 滚动 250 日分位；dominant=HMM 七态标签）。
- PIT：配对日 T 的状态取 **T-1 交易日**读数，asof 向后 7 自然日容差，弃日计数披露。
- 允许条件（OR）：`vol_pct(T-1) > 0.700` **或** `dominant(T-1) ∈ {r3, r12}`。
- 禁做：L/M 桶且 dominant ∉ {r3, r12}。

### 2.2 情绪门（本班接线；词表与允许集逐字继承 v1 §2.2）

- 词表：TDM 六段（capitulation/accumulation/ignition/expansion/euphoria/distribution）。
- 允许集：`∈ {ignition, expansion, euphoria}`；禁做：`∈ {capitulation, accumulation, distribution}`。
- **数据源真源（本卡的接线义务，v1 §2.2 已明文授权"前瞻接线义务"）**：
  `docs/_working/t0_matrix/six_phase_history_v1.csv`（由 `scripts/audit/t0_six_phase_materialize.py` 物化）。
- **映射零自定**：六段↔状态轴对应全部沿用 HEAD 内法定件
  `scripts/backtest/auto_mount.py`（`R2SIX` 宏观腿 + `phase_overlay` 亢奋/退潮微观腿 +
  `resolve_six_phase` 合成，`PHASE_PREEMPT` 优先），该件有漂移守卫测试
  `test_r2six_drift_guard_vs_framework_composer` 钉住。本卡**不新增任何阈值**。
- PIT 规则：与宏观门同构（配对日 T 用 **T-1** 的相位标签）。
- **不路由日的处理（写死，禁含糊）**：`routed=0`（宏观态 r1/r2 无六段对应且当日无微观相位）
  ⇒ 该日情绪门 **unevaluable_day**，按 §2.3 降级为单宏观门评估并**单独计数披露**；
  禁当作"禁做段"计入对照（那会把"不知道"偷换成"不做"，方向性偏置）。
- 覆盖硬限制（如实登记，不外推）：宏观腿真源 `regime_snapshot_history` 首日=**2019-04-01**，
  早于此六段不可判。实测物化 1,816 日中 1,054 日路由到六段；闭卷窗 [2019-01-04, 2025-09-09]
  内 1,566 日中 886 日路由、**359 日属允许集**。
- **禁顶替条款（继承 v1）**：`c1_market.sentiment_panel` 经注册表定性=**币圈宏观情绪面板**
  （`market_sentiment_panel`，data_source=crypto_sentiment_panel，实测仅 29 行 2 metric），
  不是 A 股情绪真源；`c1_market.emotion_index` 是连续 0-1 温度计（注册表 hard_constraint 明文
  "禁 fear_greed 异轴顶替（t0 判例）"）。二者**均不得**顶替六段标签。v1 首考探针误读前者，
  本班改指六段物化件，非换轴。

### 2.3 门语义（frozen）

- **主考（primary）**：两门当日均"可评且均允许"才入门集 ⇒ 报 `n_gate_pairs`。
- **副考（secondary）**：情绪门 unevaluable_day 的配对按单宏观门入另一集，**单独报数不并入主考**。
- 对照集：宏观门判"禁做"的配对（同口径四数全量披露，=状态区分度证据面）。

## 3. 成本假设（逐字继承 v1 §3 / CST-T0-001，零改动）

- 成本口径唯一真源=CST-T0-001：rt **31.2bp**（佣金双边 6 + 印花 5 + 过户双边 0.2 + 滑点 2×10）；
  min5 抬升单列披露。
- 开仓前置：毛价差 ≥**30bp**。
- 判据链：`edge_precondition_hit_rate ≥ 0.30` → `net_mean > 0`；对照组全量披露。
- 配对规则唯一真源=`scripts/audit/cost_trio_exam.py:build_pairs()`（同 (symbol,trade_date) 双边、
  min(Σ买量,Σ卖量) 配对量、全侧 VWAP、gross_bp=(卖VWAP/买VWAP−1)×1e4、净=毛−31.2）。
  **V2 执行件必须 import 该函数，禁重写**（RULE-CLONEGUARD + 判据单一真源）。

## 4. 样本区间（本卡唯一实质变更点，frozen 先于取数）

### 4.1 材料合格性过滤（机械判据，与任何结果统计无关）

- 入样：`bt-*.json` 的 trade_log 记录 `str(timestamp)` 长度 > 10（**含时分=日内粒度**）。
- 剔除：timestamp 仅日期（长度=10）者=日线 bar 件，同日买卖属同一 bar 聚合，
  **不构成做T 往返** ⇒ 整件剔除，且剔除件数/笔数/文件清单须在产物中如实登记。
- 该过滤只读材料的**记录格式**，不读价格/收益/配对结果 ⇒ 无挑样自由度。
- 符号归一：剔除前后均按原 `symbol` 字段配对（6 位码，无交易所后缀），禁在本卡内改代码格式。

### 4.2 考窗（继承既有 frozen 切分，非本卡新定）

- 考试段起点=**2026-06-01**，真源=`docs/_working/archive/2026-09/bizmine_night/t0_regime/t0_regime_prereg_card.md`
  §3（frozen：IS 期 2017-07-11→2026-05-31 定 vol_pct 分桶边界；考试段 2026-06-01→2026-09-18）。
  ⇒ 起点早于本卡 created（2026-09-24）且由第三方 frozen 卡给定，本班无从此窗拟合阈值的空间。
- 考试段终点=材料末日（禁写死，动态取）。
- 闭卷纪律（承全仓统一口径）：任何阈值/权重选择禁使用 **>2025-09-09** 的数据；
  本卡全部阈值继承自 frozen v1 卡与 CST-T0-001，故对本卡而言 2025-09-09 之后材料与
  "判据选择"无关，仅参与判读——产物须带 `closed_book_ok` 列如实标记。

### 4.3 状态变量覆盖（实测登记）

- 宏观门 `regime_state_anchored`：2017-07-11→今，2,238 行/2,238 唯一日。
- 情绪门六段物化件：2019-04-01→2026-09-21（1,816 日，1,054 路由）。
- 二者均覆盖考窗 2026-06-01→今，故本卡 §2.3 主考（双门）具备可评条件；
  `emotion_gate` 状态位须按日如实取 `allow / deny / unevaluable_day` 三态。

## 5. 判据与土规（逐字继承 v1 §5，禁改）

| 土规 | 阈值 | 违反时 |
|---|---|---|
| 配对数 | n_gate_pairs ≥30 | `INSUFFICIENT_SAMPLES`（禁硬出方向性结论） |
| 状态门命中 | n_gate_pairs ≥1 | =0 则 `STATE_GATE_NEVER_TRIGGERED`（如实披露） |
| 前置命中率 | ≥0.30 | 未达=`FAIL`（开仓前置都不成立） |
| 净期望 | net_mean > 0 | 未达=`FAIL`（fail-closed，禁"接近为正"措辞） |

verdict 枚举：`PASS-待考`（三土规全过+双门可用）/ `PASS-单门`（过但含 unevaluable_day，须双门复考）/
`FAIL` / `INSUFFICIENT_SAMPLES` / `STATE_GATE_NEVER_TRIGGERED`。
**判档表述遵裁定#325（禁"全绿"）。fail-closed：任何数据缺失/门不可评/样本不足都落到后两态，禁硬出。**

## 6. 执行件与顺序纪律（frozen）

- 执行件：`scripts/audit/t0_conditional_e4_v2_exam.py`（判据件住 scripts/，同 v1 目录契约）。
- 产物：`docs/_working/t0_matrix/t0_conditional_e4_v2_result.yaml` + `t0_conditional_e4_v2_verdict.md`
  + `t0_conditional_e4_v2_pairs.csv`（机读=.yaml+.csv，docs/_working 禁 .json/.py）。
- 顺序纪律：**本卡 frozen 先于执行件取数**（mtime 链可核）；禁裸跑回测、禁卡外判据。
- 零状态变更：不动任何 verdict/can_deploy/台账行；查库只读（DatabaseService/ChReader）；
  产物只写 docs/_working/t0_matrix/。
- v1 件与其产物保持原样不改不删（基线证据）。

## 7. 与前卡/前裁的边界（防撞车披露）

- 与 v1（T0-CONDITIONAL）：本卡**只重定义材料窗**（§4），假设/门规则/成本判据/土规逐字继承；
  v1 verdict 不被本卡改写，两卡并列留档。
- 与 #331（旧形态无条件做T 终止）/#386（S-OWNER-001 策略级复试图救封死）：本卡仍是**考试族卡**，
  任何 verdict 不构成实盘放行（实盘准入门=B-007 pilot 档 Owner 门位）；不重建 S-OWNER-001 任何参数。
- 与 ETFT0 三宇宙（标的维）正交：本卡答"哪些状态下出手"（状态维）。
- 若未来 PASS：须另立实现级预注册卡（因子族+执行语义），本卡 verdict 不构成实现授权。

## 8. 已知灰区（写卡时即披露，不等结果再补）

1. **判据先于材料但晚于部分数据存在时刻**：v1 卡 frozen 于 2026-09-22，而本卡材料（日内件）
   覆盖 2026-02-27→2026-09-01。缓解=本卡阈值无一由材料拟合（成本常数来自 CST-T0-001 注册表、
   vol 分桶边界来自 2026-05-31 止的 IS、考窗起点来自第三方 frozen 卡），如实登记不辩称干净。
2. **材料为回测流水非真单**：bt-*.json 是模拟成交（含 commission 字段），v1 §4 措辞"真实成交流水"
   在本卡口径下=回测器产出的成交记录；滑点已按 CST-T0-001 固定 2×10bp 计，与模拟成交价内滑点
   是否重复计入未独立复核 ⇒ 该口径若偏保守/偏乐观，两向均可能，判读时须带此保留。
3. **六段中 ignition 极稀**（实测全史仅 2 日路由到 ignition）⇒ "情绪上行三段"的允许集
   实际由 expansion（388）+euphoria（40）主导，本卡不据此放宽允许集（改=动判据）。
4. **`regime_snapshot_history` 品类未注册**（auto_mount.py:107 注释自记"品类未注册，注册 diff 见
   车道 B 报告"）⇒ 六段物化件的宏观腿表名在 auto_mount 内为硬编码常量，本班不代修该欠账，
   登记移交。
