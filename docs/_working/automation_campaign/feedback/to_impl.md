---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: 修改单/改良情报/对照申请（致实现席与制卡席）
---

# 修改单与对照申请（→⑤/⑥）

格式：日期｜类型（修改单/改良情报卡/[对照]申请）｜对象卡号｜内容摘要｜依据。

（空册待首班填写）
## 2026-10-15 ｜ st-qoder-p09-1015-02（⑨成绩官首班：修改单 5 条＋[对照] 1 条＋呈批草稿 2 条）

### 1 修改单（→⑤实现/⑦⑧考工）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep） |
|---|---|---|---|---|
| 2026-10-15 | 修改单 修① | 写分工具·卡面翻转腿 | 分数行已落而卡面 `status` 未翻：卡体仍 `status: preregistered`、`lineage` 四字段全 null，但分数册已有该卡行 | 卡体 `docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-AGG__calibration__02_四档风险轴前向收益单调.yaml` 对 `exam_scores_v1.yaml#rows[72]`（date=2026-10-13，verdict=fail）。对照：rows[73]/[74] 卡面已翻 `status: examined`＋`score_row` 回填 ⇒ 同工具两条腿行为不一致 |
| 2026-10-15 | 修改单 修② | 卡 id ↔ 卡体文件名同源 | 13/75 行（17.3%）分数行 `card_id` 与卡池文件名**精确不可互推**，门柱机械回核失效、只能模糊匹配 | 三型：①拼写分叉 `…06_m1m2_scihjorsc_longwindow`（rows[18]/[31]）↔ 文件 `…06_m1m2_scissors_longwindow.yaml`；②中英双轨 `…07_熔断五级梯度减仓对照_五态仓位锚定版`（rows[44,45,66,67]）↔ 文件 `…07_five_state_cap_anchor.yaml`，07b 同理（rows[68-71]）；③版本后缀 `…_high_event_v2`（rows[41,42,43]）↔ 盘上无 `_v2` 件，仅中文 stem。全部 13 行可按 node＋族＋序号**模糊定位，0 行完全无源**（本席实测）⇒ 非幽灵行，是命名双轨 |
| 2026-10-15 | 修改单 修③ | comparison 族机判面待扩键 | 卡面 3 个 numeric 键无机判面，被**计入 fails** 同时**又列入 unjudged.numeric_keys_not_read**（双记） | rows[44] fails[0] 原文："未支持判据键（机判面待扩）: ['maxdd_improvement_vs_no_hysteresis_min_pp', 'missed_crisis_trigger_max', 'whipsaw_roundtrip_ratio_max']"；同行 unjudged.numeric_keys_not_read 列出同三键；rows[45] 同型 |
| 2026-10-15 | 修改单 修④ | 试次记账·复读与复考不可分 | 同对象复跑 metrics **逐字节相同**而 run_id 不同，仍各占一行并各计一轮迭代预算 | rows[29]/[33] `TDM-E-L1-S3/calibration/05_limit_up_premium_derived`（run_id `mineloop-lu-*` vs `mineloop-route-audit-*`）；rows[30]/[34] `06_promotion_rate_derived` 同型。全册 75 行＝56 个 distinct card_id，12 个对象多行，其中 2 组 metrics 全等 |
| 2026-10-15 | 修改单 修⑤ | 正交闸池物化腿（本席无法自做） | `signal_orthogonality.py pool-report` 的 `--pool` 全仓无合法入参；须把 `MEMBERS` 15 员物化为 `date,sig` CSV（⑤席 d 件 `--pool-file` 桥 yaml 只解决**声明面**，不产 CSV） | 三条实测见 pulse/independent_signals.md §1；`scripts/backtest/ibt/ibt_runner.py:58-74`；`ART_ROOT` 目录不存在 |

### 2 [对照] 申请单（→⑥制卡/预注册席）

| 日期 | 类型 | 对象卡号 | 内容摘要 | 依据 |
|---|---|---|---|---|
| 2026-10-15 | [对照] | TDM-E-L3-07-3/calibration/02_二十日动量排名 ＋ TDM-E-L9-A01/calibration/02_日线动量截面 | 三组对照试次：a) 目标改 close→close 收盘口径复算；b) 选股面改 TopN（卡面 buckets quantile_decile，Top10/20/30）而非全截面 rank-IC；c) 宇宙过滤敏感性（L3 含 ST＋上市龄 vs L9 无过滤，互为对照）。**判据与阈值一律沿用卡面冻结值，本席不提修改**；对照须新卡新行 only-add，不改 rows[73]/[74] 字节 | 残留张力＝信号层两次独立物化同判负（ic_mean −0.0277／−0.0406）而节点层 `strategy_mounts=verified`（rows[73]/[74] 台账归因④）。对照回分前两卡 fail 维持，不动 TDM 节点 confidence（铁律：fail 永不升级） |

### 3 呈批草稿（判据问题，本席**不自改门柱**，等 Owner/⑩路由）

- 呈批 P-1「nan 参与否决的跨族口径分裂」：comparison 族把 `oos_sign_flip ic_delta nan（配对 IC 面样本不足）` 计入 fails；calibration 族同条件（读数不可得）走 `unjudged.numeric_keys_no_machine_face` 且**零否决权**。实测 materiality：**9 行含 nan 否决，其中 6 行（rows[66,67,68,69,70,71]）的 nan 是唯一 fail** ⇒ 这 6 次考试的 verdict 完全由"读数不可得"决定，而非任何实质门柱。问 Owner：读数不可得应判 fail（保守）还是判 unjudged（不消耗门柱）？两族须统一。本席未改任何判据字节。
- 呈批 P-2「ic_ir 门柱长期无机判面」：卡面 prose 门柱 `ic_floor: 日频横截面 RankIC 均值 >= 0.02 且 IC_IR >= 0.3` 是**合取**，但 `ic_ir_min` 在 75 行中有 **11 行**登记为无机判面（rows[72] 即其一：`ic_ir=null`），此面下 ic_floor 实际只有一半被检验。计数面声明：本席第一轮误得 10，系只扫「可精确定位卡体的 62 行」子面（13 行命名双轨被 continue 跳过）；11 为全册 75 行面，复算命令见台账 §4。问 Owner：ic_ir 无面期间，ic_floor 合取是否退化为单脚判定（现行为）还是整柱不判？禁自拟。

## 2026-10-15 ｜ st-qoder-p04-1015-01（④全网战法矿工席：改良情报卡 3 条，供楼1 盘口微结构族）

> 性质=**情报**，不是修改单：本席不提任何判据/阈值改动（挪门柱只能呈批）；凡涉及"新增对照臂/改计算基底"者，落地权在⑤，配对卡制卡权在⑥。

| 日期 | 类型 | 对象 | 内容摘要 | 依据（本班真实核实） |
|---|---|---|---|---|
| 2026-10-15 | 改良情报 1 | strategy_registry 024 号段"盘口失衡反转做 T" ＋ 本批 SIC-20261015-P04-01 | 一份**实盘实验**证据：maker 的成交概率与成交后收益呈**负相关**——挂得越容易被成交的那一侧，成交后回报越差；由此该文指出可行的做市策略常须**逆当前盘口失衡**报价，而"顺势 OBI 挂单"在其实测里多数不划算。对⑤的可执行含义=现有"极端失衡→押反弹"方向得到同向外部证据，但入场条件宜引入"成交概率/可成交性"感知（而非只看过阈），并把"顺势 OBI 挂单"作为**对照臂**提交⑥配对，而不是直接替换现方向 | arXiv API 直读条目：The Market Maker's Dilemma: Navigating the Fill Probability vs. Post-Fill Returns Trade-Off，http://arxiv.org/abs/2502.18625v2（2025-02-25，q-fin.TR，Binance BTC 永续实盘实验） |
| 2026-10-15 | 改良情报 2 | 盘口失衡族全部候选（含本批三卡与 024 号段） | 该文用 NSE（印度）BankNifty 期货**逐笔**数据做订单流结构过滤（按订单寿命/改单次数/改单时点）：对"聚合订单流"过滤相对未过滤基准只有**微小**改善；但对"**已成交的父订单**"做过滤后，OBI 与短期收益的方向关联**系统性增强**。⑤实现层含义=失衡因子的计算基底优先选"成交父订单聚合流"而非"逐笔快照事件堆叠"；同时该文以 OBI-收益关联作市场质量诊断，与本仓 PIT/回填噪声问题同型可参照 | arXiv API 直读条目：Order-Flow Filtration and Directional Association with Short-Horizon Returns，http://arxiv.org/abs/2507.22712v2（2025-07-30，q-fin.TR） |
| 2026-10-15 | 改良情报 3 | 本批 SIC-20261015-P04-01/03 的构造与⑥制卡窗参数登记 | 两条约束必须写进卡面假设，否则读数失真：①OFI-价格关系的线性斜率**与市场深度成反比**（原刊结论）⇒失衡须除以深度再进信号，裸水平值在流动性分层的全 A 池不可横向比；②预测力随聚合频率**衰减**（tick 级 R² 约 0.15 量级，聚到 1-5 分钟条降到约 0.04-0.08，社区技术站转述二手）⇒⑥冻结时须显式登记"考的是哪个频率"，禁拿分钟级读数冒充 tick 级预测力 | ①经 WebSearch 命中百度学术条目摘要（DOI 10.2139/ssrn.1712822，Cont-Kukanov-Stoikov, JFEC 12(1):47-88）＋聚宽社区同卷引文；②=https://techwhims.com/tradesys/theory/hft-lessons/ 片段转述（**非同行评议，只作风险参照，不得作为判据来源**） |
## 2026-10-15 ｜ st-qoder-p09-1015-03（⑨成绩官第三班：修改单 3 条＋修② 正解改写＋呈批 P-2 材料更正＋呈批 P-3 新条）

### 1 修改单（→⑤实现/⑦⑧考工，抄⑩）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修改单 修⑥ | 写分工具·`unjudged` 申报腿 | 读数取空必须落"未读/无面"声明，禁静默。含 `ic_ir_min` 柱的 43 行中 41 行 `metrics.ic_ir=null`，册面只声明 11 行 `numeric_keys_no_machine_face`、`numeric_keys_not_read` 命中 0 ⇒ **30 行静默读空** | 复跑 `python .runtime/tmp/st-qoder-p09-1015-03/reconcile3_verdict_replay.py`；静默行集＝rows[0..30]（除 17）。同型另一面：rows[44] 三键**同时**在 fails 与 not_read（02 班修③），本条是"该声明的没声明"，修③是"声明了两遍"，同属申报腿 |
| 2026-10-15 | 修改单 修⑦ | high_event 执行器·`event_oos_gap_same_sign` 腿在非 v2 路缺位 | 卡体五键（`event_days_min 200/event_gap_max_bp 0/event_t_stat_max -2/event_oos_gap_same_sign/event_regime_gap_same_sign`）**23 行全同**，但账面只有 3 行（`_v2` 卡 rows[41,42,43]）记 `oos_gap 反号`；非 v2 路不记该腿，改记 `oos 窗事件日 <200`。实测 16 行 OOS 反号 ⇒ **13 行方向否决不可见** | 复跑口径＝`fails[i].startswith('oos_gap 反号')` 对 23 行只命中 3；`is_gap_bp×oos.gap_bp≤0` 命中 16＝rows[41,42,43,46,47,51,52,53,54,55,58,59,62,63,64,65]；未入账 13＝rows[46,47,51,52,53,54,55,58,59,62,63,64,65]。样本行：rows[46] is=−3.22bp／oos=+11.37bp（反号）却只记"事件日 105<200"；对照 rows[41] oos_n=104 同条件却记反号。`regime_gap 反号` 腿两路都在（11 行入账），故缺的是 OOS 这一根。**判据阈值本席一字未动**，请修的是腿的有无与顺序 |
| 2026-10-15 | 修改单 修⑧（P0 告警） | 考卡池/分数册的并发存活面 | ①分数册 `exam_scores_v1.yaml` **不在 HEAD**，只活于主区 index（`A `）＋队列 blob；②本班值守内考卡池 531→529→531，rows[73]/[74] 两卡体 07:02:08 被重写（`M ` 态）。⇒ 判卷锚点无落点、可被并发摆布 | `git cat-file -e HEAD:docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 返非零；`git status --porcelain` 对两卡体＝`M `；在途双袋 `-0003`（blob c14e6635＝104507 旧面）／`-0004`（blob c7e5b1f8＝现值）。本席未回滚未代修，只呈交 |

### 2 修② 正解改写（02 班 2026-10-15 修② 的接续，非推翻其现象）

- 现象仍在：02 班报分数行 `card_id` 与卡池**文件名** 13/75 精确不可互推（拼写分叉／中英双轨／`_v2` 后缀）。本班另测一维：按"文件名 stem 直接等于 card_id"的 join **0/75 全不命中**——即两侧从来不同名，13 只是 02 班模糊尺下的子集。
- 但正解不是改名：**卡体内部 `card_id` 字段是全的**——本班按该字段建索引 ⇒ **75/75 精确定位**（531 份卡体、531 个 distinct card_id，unresolved=0）。⇒ ⑤席回核/门禁工具应把 join 键从"文件名 stem"改为"卡体 card_id 字段"，一行改动即消除判卷面失明，且不动任何册面字节。依据脚本＝`.runtime/tmp/st-qoder-p09-1015-03/reconcile3_verdict_replay.py`。

### 3 呈批材料更正（判据问题，本席仍不自改门柱）

- **P-2 材料量级上调**：02 班报"ic_ir_min 在 75 行中 11 行无机判面"。本班按两种分母分别实测：①**册自述面**（`no_machine_face` 含 ic_ir）＝11 行（rows[31..40,72]），与前班同值；②**读数面**（卡体含 `ic_ir_min` 的 43 行中 `metrics.ic_ir` 为 null）＝**41 行**。⇒ 门柱合取"RankIC≥0.02 且 IC_IR≥0.3"实际只测一半的面＝41/43（95.3%），且其中 30 行册面零声明。问 Owner 的题面不变（无面期间合取退化单脚还是整柱不判），但**代价数值以 41 为准**；旧 11 不作删除，留案卷。
- **呈批 P-3（本班新增，判据口径，本席不裁）**：卡面 `event_days_min: 200` **未声明作用窗口**。两版执行各执一词——`_v2` 路只量全窗（rows[41,42,43]：全窗 n_event 295/…≥200 判过，OOS 窗 104/81/79 天不触限），非 v2 路把下限施于 OOS 确认窗并**以此顶掉 `event_oos_gap_same_sign` 腿**（rows[46..65] 20 行入账"事件日<200"）。问：①该下限作用在全窗、OOS 窗还是两窗；②样本不足与方向反号同触时，是否两条都记（现行为只记前者）。裁定前本席维持分数册原判、不改一字。
## 2026-10-15 ｜ st-qoder-p09-1015-04（⑨成绩官第四班：修改单 2 条＋修⑤ 正解改写＋修⑥/修⑧ 追加面＋[对照] 1 条＋呈批 P-4 新条）

> 本班增量＝8 行（rows[75..82]，`p07a-agg8-20261015` 批，node `TDM-E-L1-S2`）。判卷尺沿用 03 班在册脚本口径（族按卡体 `pillars_numeric` 键集定、卡体按内部 `card_id` 字段 join，8/8 定位 0 未命中）。复算＝`python .runtime/tmp/st-qoder-p09-1015-04/reconcile4_delta.py` ⇒ **增量行 verdict 不可再现＝0/8**（8 张卡体 `pillars_numeric` 全同＝`mono_spearman_min 0.6 / ic_mean_min 0.02 / ic_ir_min 0.3 / regime_same_sign / oos_same_sign`）。以下各单一律**不动判据阈值、不挪门柱、不碰分数册字节**。

### 1 修改单（→⑤实现/⑦⑧考工，抄⑩）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修改单 修⑨ | 写分工具·series 路净/成本面未产，而毛面读数挂进"门柱" | 8/8 行 `net_bucket_medians` 全 NaN、`round_trip_cost_bp=NaN`，**同时** `mono_spearman` 有值（0.721–0.927）⇒ `mono_spearman_min≥0.6` 这根柱是在**毛收益面**上过的；pass 行（rows[76]/[78]）账面读起来像"门柱全过"，实际成本口径从未被检验。全册同型 **32 行** net 面全 NaN（不止本批） | 快照 `.runtime/tmp/st-qoder-p09-1015-04/score_snapshot.yaml`（sha `24ef736d819d0be1`）rows[75..82] `metrics` 面；复量命令＝`python -c "import yaml,math;rows=list(yaml.safe_load_all(open('.runtime/tmp/st-qoder-p09-1015-04/score_snapshot.yaml',encoding='utf-8')))[1]['rows'];print(sum(1 for r in rows if all(isinstance(x,float) and math.isnan(x) for x in (r['metrics'].get('net_bucket_medians') or [1]))and r['metrics'].get('net_bucket_medians')))"` → 32。请修＝series 路补净桶与 `round_trip_cost_bp`，或在柱名/`unjudged` 显式标"毛口径"。**exam_policy §3.2 双口径声明纪律是本条依据，本席未新增判据** |
| 2026-10-15 | 修改单 修⑥（追加面，非推翻） | 写分工具·`ic_ir_min` 柱无机判面（03 班在册） | 面级数值随本批**由 43/41 升至 51/49**：卡体含 `ic_ir_min` 柱的分数行＝**51 行**（原 43＋本批 8），其中 `metrics.ic_ir` 读数空＝**49 行**（原 41＋8），册面已申报（`no_machine_face` 或 `not_read` 任一命中）＝**19 行**（原 11＋本批 8），**静默读空仍＝30 行**（rows[0..30] 除 17，未随本批变化）。⇒ 本批 8 行申报腿**做对了**（8/8 如实挂 `ic_ir_min`），欠的是①前 30 行历史静默面 ②柱本身没面 | 复量＝同上手 `pillars_numeric` 含 `ic_ir_min` 计数（脚本 `.runtime/tmp/st-qoder-p09-1015-04/`，0命中 0 行未定位卡体）。同族在册旧账：02 班呈批 P-2、03 班修⑥（未修）。**本席不代修、不自改合取口径** |
| 2026-10-15 | 修改单 修⑧（追加面，P0 升级） | 分数册存活面：现值 83 行面**在 HEAD/在途袋/册面申报之外** | 本班值守内实测三态：①`git cat-file -e HEAD:…exam_scores_v1.yaml` 仍非零（不在 HEAD）；②磁盘现值 **115036B／83 行／sha `24ef736d819d0be1`（mtime 07:17:15）**；③index 面＝105598B／75 行／sha `c7e5b1f8bfb98ae2`；④pending 的 `q-20261015-st-scorehome-20261014-0003` 带该册 blob `c14e6635de949bab`（104507B＝74 行旧面）、`-0004` 带 `c7e5b1f8bfb98ae2`（75 行面）、`-0005/-0006` **不含**该册 ⇒ **没有任何一袋带现值 83 行面**。若 `-0003` 或 `-0004` 先落地，本班刚判的 8 行（含 6 条负结果）会被整档快照洗掉＝exam_policy §5.1 全量入册被回退 | 复量＝`python -c` 遍历 `.runtime/commit_queue/pending/q-20261015-st-scorehome-*.json` 对 `exam_scores_v1.yaml` 打 `blob_sha256` 前缀（本班正文读数）＋`git status --porcelain`＝`AM`。**本席未回滚、未代修、未 requeue 他人袋**（属⑩线长席串行/属主班写域），只呈交判据 |

### 2 修⑤ 正解改写（02 班修⑤ 的接续，非推翻其现象；本席无法自做的部分已缩小到一列名之差）

- 现象仍在：`signal_orthogonality.py pool-report` 直读生产序列面被拒——报错原文（本班正文原样跑）：`[SIGNAL-ORTHOGONALITY] ERROR: 信号 CSV 须含 date,sig 两列: docs\04_research_records\mining\ledgers\nightmine_20261010\series\avg_abs_ret.csv 实有 ['trade_date', 'value']`。
- **但阻塞对象比 02 班所报更窄**：02 班报"全仓 0 个 date,sig CSV／15 员池物化腿缺位"。本班实测＝池物化腿**本来就存在**（`nightmine_20261010/series/` 有 13 枚单列序列），差的只是**列名契约**（工具吃 `date,sig`，采集面产 `trade_date,value`）。本班未改工具、未改采集面，只在仓外临时面 `.runtime/tmp/st-qoder-p09-1015-04/pool_datesig/`（13 枚）与 `pool6/`（6 枚 agg8 本体×变换）做改名适配 ⇒ **工具权威输出即得**：`n_members=6 n_common_dates=1855 effective_n_signals(PR)=2.1272`，`pool6_report.json` 在册。
- 正解（属"改喂给闸的输入指向"，禁弱化闸）：①闸侧读取处加列名映射 `trade_date→date`、`value→sig`（一行，禁动 `|corr|≤0.3` 判据）；或②采集面落库时双写列名。**两者都不涉及判据**。
- 附带第二个症状（供⑤席定位，本席不自修）：整池 13 员跑 `pool-report` 报 `[SIGNAL-ORTHOGONALITY] ERROR: 池内共同日期不足: 0 < 3`，而 6 员子池共同日＝1855 ⇒ 池谓词按**全体交集**取日，任一成员覆盖面不齐即整池拒算且**不指认是哪个成员**。建议闸侧把该分母改逐对交集、或报错打印打成 0 的候选成员名（属观测面，非判据）。复跑：`python scripts/backtest/fexam/signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool_datesig`（13 员，红）／`--pool …/pool6`（6 员，绿）。

### 3 [对照] 申请单（→⑥制卡席，本班 1 条）

| 日期 | 标记 | 对象 | 对照要什么（只改一个变量） | 依据（可 grep） |
|---|---|---|---|---|
| 2026-10-15 | [对照] | `TDM-E-L1-S2/calibration/46_agg_avg_abs_ret_z20_fwd5`、`47_agg_avg_abs_ret_z20_fwd10`（rows[81]/[82]） | 制**对照卡**（禁改现卡冻结口径）：同信号本体、同 z20 变换、同前向窗、同桶边界，**只把 OOS 窗切成 IS 内同号段／反号段两段**分别复量 `oos_ic` 符号。目的＝分离两种死因：(a) 族本身时段失稳（外推无效）vs (b) OOS 窗 regime 构成造成的符号翻转。前者→方向单第 2 条成立、走死矿候选；后者→须先修窗构成再谈判死 | rows[81] IS `bull=+0.1281/bear=+0.1272`（同号）却 `oos_ic=-0.0324`；rows[82] `+0.1663/+0.1183` 却 `-0.1080`；对照面同批 rows[76]/[78] IS 也同号而 OOS 同号（`+0.0997/+0.1016`）⇒ 同框架下两根信号 z20 面一过一反号，**差别不在变换**。⑦席 ledger 同判："是否构成族级结论须由 ⑨ 成绩官按复制账判"——本班复制账＝0 异常，判族级前先要这张对照卡 |

### 4 呈批草稿（判据口径，本席一律不自改）

- **呈批 P-4（本班新增）**：`regime_same_sign` 柱**无最小幅度/过零带**。实测 materiality＝同一信号本体只差前向窗，bull 段读数从 rows[79] `+0.0114` 变到 rows[80] `-0.0200`（约 0.03 量级位移）即**跨零变号并多背一根 `regime_sign_flip`**；而 `ic_mean_min=0.02` 说明 0.02 量级读数在本册本就是"贴着门柱"的噪声级。问 Owner：①regime 同号柱是否须配过零带（如 `|IC|<ε` 视为不判，判据改动=挪门柱）；②ε 由谁定、是否与 `ic_mean_min` 挂钩。**裁定前本班维持分数册原判**（rows[80] fail 不动），只登记可见性。
- **P-2 代价数值更新（02 班在册题面不变，旧数不作删除，留案卷）**：02 班报"75 行中 11 行无机判面"、03 班上调为"43 行含柱／41 行读数空／30 行静默"；本班按 83 行全册面复量＝**含柱 51／读数空 49／已申报 19／静默 30**。⇒ 门柱合取"RankIC≥0.02 且 IC_IR≥0.3"**实际只测一半**的比例＝49/51（96.1%）。题面仍是那两问（无面期间合取退化单脚还是整柱不判），代价数值以 49/51 为准。

## 2026-10-15 ｜ st-qoder-p04-1015-02（④全网战法矿工席：改良情报 5 条，楼1 价差族＋楼4 残差动量／状态门控反转）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 实现自检义务（**判据级，不是风格建议**） | ⑤实现 SIC-20261015-P04-04 的 CS 估计量 | 高低价价差估计量的 γ 项分母是 √(3−2√2)=0.41421（等价 α=K(√β−√γ)，K=1/(√2−1)），**不是**把整式同除 (3−2√2)。写错的表征是"全零且无告警"：因 γ≥β/2>0.1716β，错式在数学上恒负⇒clip 后恒 0。⇒ 请⑤把"合成序列复原已知价差"做成该件的**必过单测**（本席已给可复现数值），否则该族会以下一班的"0 命中"形态静默死掉 | 本席实测：错版在真实 10 票 α>0 占比=0.000，在合成 s_true=150bps 上也=0.000（尺无判别力正证）；改版在合成（日波动 1.2%、48 步/日、2000 日、W=21）上 s_true=0/30/60/150bps ⇒ meanS=5.2/20.7/44.2/127.1bps、α>0 占比=0.306/0.729/0.961/1.000（单调）；式子归属来源=https://github.com/mariasfondrini/etf-liquidity-lab src/spreads.py docstring（MIT，本席直读，未复制码） |
| 2026-10-15 | 刻度选择约束（**⑥冻结须落字**） | 同上卡｜信号刻度 | 本库日线面上该估计量**水平值不可用**：零价差合成底噪 5.2bps，本库 10 票同口径均值仅 7.9bps（中位数 0.0bps、P90 25.0bps）⇒ 均值只比"完全没有价差"高 2.7bps。卡面可用面只两种：横截面 rank(S) 或横截面 rank(α>0 占比)。禁把 bps 裸值写进阈值（如"价差>30bps 则…"），那是在给噪声定门柱 | 本席 W=21 实跑（不复权 c1_market.kline_daily，2025-06-01..2026-09-30，n=3060）；同题外部证据=同仓 README"日线 CS 无法分辨现代 ETF 价差水平，SPY 读数 24.8bps 而真实报价价差<1bp"；另有同行评议反方证据（CS 价差"1963 年前后两段均缺乏预测收益的能力"，本席转述引证，未直连原刊） |
| 2026-10-15 | 顺序约束（不平滑即虚高 8 倍） | 同上卡｜矩的平滑顺序 | β 与 γ 必须**先做窗均值再解 α**；逐日算 S 再平均的写法，本席实测在真价差 0bps 的合成上给出 meanS=41.6bps（α>0 占比 0.557）＝噪声冒充价差，比平滑版底噪（5.2bps）高 8 倍。A 股另有两类退化日必须先剔：high=low（实测 2026-09 全月 228/116,749=0.20%）与停牌日 | 本席合成对照两态实测；退化日普查为 CH 只读实跑（负对照 high<low=0 行、high<=0/low<=0=0 行，同表正对照 amount>0=116,641 行） |
| 2026-10-15 | 口径自由度登记 | ⑥制卡 SIC-20261015-P04-05（残差动量） | 该族至少五处"择一即换对象"的自由度：①因子集（CAPM/FF3/FF5/行业/PCA）②截距 α_i 是否计入信号（主刊**排除**，理由=控制设定偏误）③回归窗长与"跳过最近几期"④分母是残差波动还是含 1/11 系数的变体（不改排序单调性）⑤是否加卖方"窗内日波动最高子期残差×−1"改进。⇒ 请⑥逐条冻结并在卡面写明每条取自哪个口径；**改进臂可作对照，禁作主臂**（非同行评议，且该卖方自报 2024Q3-2025Q2 大幅持续超额回撤） | 主刊条目（Blitz-Huij-Martens, JEF 18(3):506-521, 2011，本席经期刊界条目页核实摘要）；α_i 与公式缺失之质疑=https://blog.csdn.net/weixin_39624332/article/details/112527941（非同行评议）；因子集并存两口径=https://juejin.cn/post/7591360623469871114（factors.directory 同列 residual-momentum-capm 与 residual-momentum-ff3）；改进版与年化数字=https://cj.sina.com.cn/articles/view/5953466437/162dab0450670a7tl0（卖方研究转载，本席未取研报原文） |
| 2026-10-15 | 防伪标签（**禁偷顶**） | ⑤⑥ SIC-20261015-P04-06（状态门控反转） | 原文三腿=个股漂移状态门 × 短期反转 × 价值。本库价值腿实测不可达（daily_valuation 仅 47 交易日、末日 10-14 只有 1553 行而 10-13 有 5574 行、is_st 全表 sum=0）⇒ 本班交付为**半构造**（门×反转）。请⑤⑥不得用 circ_mv／turnover_rate／流动性列偷顶"价值"：那样⑨席空白轴地图会把"估值"记成已出分＝账面造假。另：0 收益日在"正收益日占比"里的归属（含或不含）会变阈值读数，须⑥登记规则 | 卡面实测段；换手真源单列在供数缺陷（kline_daily/hfq 的 turnover 恒 0，stock_daily_basic.turnover_rate 同窗 116,588/116,588 全正）；空白轴地图依据=docs/_working/automation_campaign/feedback/to_miners.md 2026-10-15 ⑨席 02 班第 3 行 |
## 2026-10-15 ｜ st-qoder-p09-1015-05（⑨成绩官第五班：修⑧ 追加面＝**更正兼扩面**，本班零新开单号）

| 日期 | 单据 | 对象 | 内容（判卷面事实） | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修⑧ 追加面（05 班，更正 04 班一处扫面＋扩面至馆级，P0 维持） | 分数册永久区存活面与跨席读面一致性 | ①**更正**：04 班"pending 的 5 个 st-scorehome 袋无一携带现值 83 行面"按 `st-scorehome` 字面成立，但按**全 pending 面（102 袋）**不成立——`q-20261015-st-qoder-p07-1015-01-0001`（`created 2026-10-15T07:30:18+08:00`，action=modify）的 blob sha256=`24ef736d819d0be1…`＝**与磁盘现值逐位同**，现值面在途有袋。②**扩面**：未落地面积远大于"一册"——`git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/` 返回 **0 件**，`git ls-files` 同目录 **30 件**（含 11 册他类成绩册与 8 份 .md twin），30 件全 `AM`（index≠磁盘：`exam_scores_v1.yaml` +9438B；其余 29 件 +164~179B 一致偏移，形制＝同批生成器头注）。③同路径三面并存（磁盘 83／index 75／`-0003` 74），**落地顺序决定终面**；判卷锚点在 HEAD 无任何落点＝CAS 重放/整树回退类事故的天然靶面。④**跨席读面已分叉**：⑩席 `pulse/queue_depths.md:24`（07:52）记 `exam_scores_v1.yaml docs=2/rows=75`＝index 面，本席同刻磁盘面＝83 行；两席皆如实实测却得两个行数，差值恰为本席 04 班新判的 8 行 ⇒ 建议在生产线圈一条"报行数须声明读面（index／磁盘／HEAD）"的口径注（属判据外的观测面纪律，非门柱改动） | 复跑：`git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/ \| wc -l`＝0；`git ls-files docs/04_research_records/backtest/scores/ \| wc -l`＝30；`git status --porcelain docs/04_research_records/backtest/scores/`＝30 行 `AM`；袋面＝`python` 遍历 `.runtime/commit_queue/pending/*.json` 取 `path==…exam_scores_v1.yaml` 的 `blob_ref` 再对 `.runtime/commit_queue/blobs/<sha256>` 做 `safe_load_all` 数行（本班读数：p07 袋 115036B/83 行、`-0004` 105598B/75 行、`-0003` 104507B/单文档/74 行）。**本席未回滚、未代修、未 requeue 他人袋、未动分数册与判据字节**（属⑩串行裁定与属主班写域），只呈交判据 |

## 2026-10-15 ｜ st-qoder-p04-1015-03（④全网战法矿工席第三班：改良情报 6 条，全部资金面/流动性/筹码轴）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 归一分母择一（**口径级**） | ⑤实现 SIC-20261015-P04-07（大单净流入强度） | 净流入腿**禁直接除以成交额**做跨市值比较，主构造应除以流通市值；成交额版只作对照臂 | 外部实证（百度知道"主力资金选股"条目，WebSearch 本班命中）自陈 lmf_per_cap_5/lmf_per_cap_20（大单净额占流通市值比）在 IC、t 检验、五层分层三面上均优于占成交额版本，且因子在沪深300 上失效的原因是"大国企市值大但流通市值低"。本库分母可用面本班实测=stock_daily_basic.circ_mv 于 2026-10-14 为 5563/5563 行 >0，中位 493741.644 |
| 2026-10-15 | 用法约束（**禁全域线性排序**） | ⑤⑥ 卡07 | 该族应实现为**分档过滤**而非 zscore 全域打分；短窗显著、长窗等同随机 | 同作者系列两篇独立回测（xueqiu 386081946／386898071，本班 WebSearch 命中）：大单净流入额版 5/10/20/60/120/250 日 Spearman p=0.090/0.090/0.090/0.108/0.489/0.405 全不显著、分组呈倒U（中段6-7稳、两端对称陷阱）；占比版仅 5 日 p=0.043 通过，250 日 p=0.987 |
| 2026-10-15 | 共线预警（**排闸优先级，非证据**） | ⑥⑨ 卡07 与 SIC-20261015-P04-08 必须同池先测 | 社区自报"主力净流入比率 vs 换手率"相关性 0.68，若两卡同池极可能超在册门柱 0.3；本席**未**复现该数（禁当已证） | 来源=CSDN 163556400（非同行评议，本班 WebSearch 命中）；在册门柱=研究生产线 SOP v1.4.0 正交准入 0.3（⑨席不动） |
| 2026-10-15 | 双臂分考义务 | ⑥预注册 卡07 | 须同时挂"顺势臂"（净流入强度高→押涨）与"反转臂"（前一日大额净流入→押回调），两臂读数禁合并报数 | 反转臂线索=同文自报"昨日主力净流入 Top10% 的票今日平均跑输 0.3%"；顺势臂线索=占比版 5 日正相关显著。二者符号相反，属⑥择一以外的**并列候选**，本席不裁 |
| 2026-10-15 | PIT 与剔样义务（**判据级，写错即造假**） | ⑤实现 SIC-20261015-P04-09（股东户数环比） | 事件时点一律取 announce_date（禁 end_date）；必剔上市不满一年次新；必剔期间发生增发/解禁/转债转股的机械变更样本 | 本班实测 dateDiff('day', end_date, announce_date) 中位=25、P95=113，且 countIf(announce_date<end_date)=3904/515280=0.76% 逻辑异常行；外部页面（yyqyx.com/s/000017.SZ）独立报"公告平均比报告期末晚 27 天"并自陈其 17.9 万份公告实证用公告日、次新 617 样本平均超额达 +81 个百分点会**把结论做反**——两路互证 |
| 2026-10-15 | 标度写死前的互证义务 | ⑤实现 SIC-20261015-P04-08（换手率双臂） | turnover_rate 本班判为**百分数口径**（中位 1.7877、P90 6.3214），但实现仍须用 float_share 与 kline_daily.volume 反算一日样本互证后才写死标度；换手腿**必须**绑 stock_daily_basic，禁绑 kline_daily.turnover | 本表读数非零率 144389/144389（2026-09 起）；对照在册死列：kline_daily turnover>0=0/144576、kline_daily_hfq 0/144590，而正对照同表 amount>0=144438/144452（本班复证仍未修） |

## 2026-10-15 ｜ st-qoder-p09-1015-06（⑨成绩官第六班：当日增量＝0 行 ⇒ 本班产出＝**在册四单的复测追加重烧**，零新开单号）

> 本班读面声明（遵 05 班 S-2 口径注建议）：以下全部行号与读数取自**磁盘面** `exam_scores_v1.yaml`（sha256 `24ef736d819d0be1aa943fcd1eaf7aa311eb50d775827455011c33f916c55758`／115036B／`safe_load_all` doc1.rows=83，mtime 07:17:15，与 04/05 班逐位同）。族口径＝**卡体 `pillars_numeric` 键集**（03 班在册口径，非路径段）。尺件＝`.runtime/tmp/st-qoder-p09-1015-06/census6_materiality.py`（只读，正文可原样复跑）。

| 日期 | 单据 | 对象 | 内容（判卷面事实，非新问题） | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修④ 追加面（**面级数值更正 2→5**，旧数留案卷不删） | 试次记账·复读与复考不可分 | 02 班在册"全册 75 行＝56 个 distinct card_id，12 个对象多行，其中 **2 组** metrics 全等"。本班在 83 行面直测：**83 行＝64 个 distinct card_id／多行对象 12 个（数不变）／metrics 全等组＝5 组**。新增三组恰是三个"3 轮达上限"对象：`(rows[26],rows[36])`=L2-02/02_接棒撤离榜、`(rows[27],rows[37])`=L2-03/02_调整周期进度、`(rows[28],rows[38])`=L2-04-2/02_虹吸态成交集中度 ⇒ **迭代预算被字节完全相同的复跑各消费掉一轮**，SOP §4"同 holdout 迭代 ≤3 轮/月"的上限在其中两轮里买到的是零新信息。本条只报计量面，判据（全等复跑是否该计入轮次）属 呈批面与 ⑩ 席 | `python .runtime/tmp/st-qoder-p09-1015-06/census6_materiality.py` 的 [1]/[B] 段逻辑：`sha256(json.dumps(metrics,sort_keys=True,default=str))` 按 `(card_id,key)` 分组取 len>1；轮次直方图 `{1:52, 2:7, 3:3, 4:2}` |
| 2026-10-15 | 修⑥ 追加面（**复量逐位同＝未修**） | 写分工具·`ic_ir_min` 柱申报腿 | 本班按 04 班同谓词独立复量得 **含柱 51／有读数 2／读空 49／已申报 19／静默 30**，与 04 班在册面（51/49/19/30）**逐位同** ⇒ 修⑥ 自 07:17 以来未落地，非口径之争。⚠ 并更正本席自己第一轮的错口径：首轮尺打印"申报无机判面的行=21"，谓词是"该行 `no_machine_face` 非空"（含他柱申报），会把 51−19=32 误算成静默面；正确谓词须**按柱名**判 `ic_ir_min ∈ (no_machine_face ∪ not_read)`，且静默集要再减掉有读数的 rows[73]/[74] 两行。声明于此供下一班勿复犯 | 尺 [A] 段；`ic_ir` 有读数行实测＝`[73, 74]`（唯一两行，与在册"panel 路才有 ICIR 面"一致）；未定位卡体行＝0（`card_id→卡体` join 83/83 全命中） |
| 2026-10-15 | 修⑦ 追加面（族级材料度，**不改在册 13 行不可见结论**） | high_event 执行器 | 在册结论维持（23 行同五柱、非 v2 路不记 `oos_gap 反号`）。本班新出的是**这族离门柱有多远**：门柱为负向命题 `event_t_stat_max: -2.0`，23 行 `t_stat` 读数区间 `-0.985 … +1.977`，**距柱最近 1.015 个 t、中位 2.479、最远 3.977** ⇒ 该族无一行属"边缘未过"，全部是方向/功效双双未成立。另记 1 行**反向近显著**：rows[50] `TDM-E-L1-S2/calibration/21_ind_vol008_high_event` t=**+1.977**（命题要求 ≤−2.0，实测正向达常规显著阈） | 尺 [2] 段全读数清单；复跑＝`python .runtime/tmp/st-qoder-p09-1015-06/census6_materiality.py` |
| 2026-10-15 | 修⑧ 追加面（**谓词更正＋复测：旧面两袋仍在途，风险未解除**） | 分数册永久区存活面 | ①本席第一轮用 `path.endswith('exam_scores_v1.yaml')` 扫 pending 得"13 条命中"＝**误计**：命中的是他册同后缀件（`alt_factor_／factor_／indicator_conditional_／indicator_／strategy_exam_scores_v1.yaml`，各袋 5 条）。按**精确路径** `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 复扫＝**3 袋**，与 05 班"共 3 袋"结论一致（本条为印证非推翻）。②本班实测三袋 blob：`q-20261015-st-qoder-p07-1015-01-0001`＝`24ef736d…`（磁盘现值 83 行面）、`q-20261015-st-scorehome-20261014-0003`＝`c14e6635…`（74 行旧面）、`-0004`＝`c7e5b1f8…`（75 行面）⇒ **两个旧面袋仍在 pending**，任一日志序上后落地即洗掉 04 班刚判的 8 行（含 6 条负结果）。③馆级面复测同 05 班：`git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**、index＝**30 件**、该册 `git status`＝`AM`。④**新增面（队列积压与本席自身交付）**：pending 总数 **103 袋**、`head` 为 `q-20261015-st-chfinalw2-20261015-0005`（`waiting_s=28019`，drain-active、lease 由 PID 40328 持有）；**本席 02/03/04/05 四班的 6 只袋全部仍在 pending 未落地**（`-02-0001`(7件)/`-03-0001`/`-03-0002`/`-04-0001`/`-04-0002`/`-05-0001`）⇒ ⑨席判卷台账与全部信箱件的 git 落点＝零，磁盘面可见纯靠主区工作树。本席未 requeue、未代修、未动他人袋 | 复跑＝`python scripts/commit_queue.py status`（`head.waiting_s`／`lease`）＋遍历 `.runtime/commit_queue/pending/*.json` 按 `it['path']==TARGET` 精确匹配打 `blob_sha256`；袋清单＝`ls .runtime/commit_queue/pending/ \| grep p09` |
| 2026-10-15 | 呈批 **P-1 追加面**（二次实测成立，题面不变、旧卷不删） | nan 参与否决的跨族口径分裂 | 02 班在册："9 行含 nan 否决，其中 6 行（rows[66..71]）nan 是唯一 fail"。本班在 83 行面独立复量＝**同值**：`fails` 只含单一 token 的行中 `oos_sign_flip` 12 行＝comparison 6（rows[66,67,68,69,70,71]，逐行 fails 原文均为 `oos_sign_flip ic_delta nan（配对 IC 面样本不足）`，且 `numeric_keys_not_read=[]`、`numeric_keys_no_machine_face={}` **零申报**）＋calibration 6（rows[8,75,77,79,81,82]，这 6 行的 nan 不存在、是真反号）。⇒ 同册内"读数不可得"在 calibration 族走 `unjudged`（零否决权，rows[76]/[78] 的 `ic_ir_min` 即此形态）、在 comparison 族直接进 `fails`（有一票否决权）；rows[44]/[45] 更把同三键**既记 fails 又列 not_read**（02 班修③）。问 Owner 的仍是 02 班那两问，本班只补一句：**这 6 次考试的 verdict 完全由"读数不可得"决定，不能用作"该战法无效"的证据**。本席未改任何判据字节、未动分数册 | 逐行原文取证＝`python -c` 打印 rows[66..71] 的 `fails`/`unjudged`（本班正文原样跑，读数见台账 §2）；尺 [5] 段 |
| 2026-10-15 | **[对照] 追加面**（04 班单扩面，非另起一单） | 只栽 OOS 一根柱的对象 | 04 班 [对照] 单只覆盖 `46/47_agg_avg_abs_ret_z20_fwd5/fwd10`（rows[81]/[82]）。本班机读全册"单一死因"面＝**12 行**，其中属"IS 全柱过、只 OOS 反号"且从未开过对照的 calibration 行还有 **rows[8] `TDM-E-L9-A04/calibration/02_估值ERP分位日增量`（is=+0.0467／oos=−0.0048，bull 0.0457／bear 0.0945 同号过）、rows[75] `40_agg_lu_count_level_fwd10`（is=+0.0961／oos=−0.1102，bull 0.0024／bear 0.1633）、rows[77] `42_agg_lu_ratio_level_fwd10`（is=+0.1023／oos=−0.0979，bull 0.0062／bear 0.1711）、rows[79] `44_agg_avg_abs_ret_level_fwd5`（is=+0.0828／oos=−0.0643，bull 0.0114／bear 0.1670）** ⇒ 请 ⑥ 席按 04 班同一变量单换法（只切 OOS 窗为 IS 内同号段／反号段）把这 4 行并入同一张对照卡的批次；comparison 那 6 行**不走对照**（死因是 nan 非反号，归 P-1 与修⑩面） | 尺 [5] 段行集 `[8, 66, 67, 68, 69, 70, 71, 75, 77, 79, 81, 82]`；rows[8] 卡体五柱与读数回核见台账 §2 轮二 |

### 本班净零声明与另记事实

- 本班**零新开单号**：以上五条全部是对在册单（修④/修⑥/修⑦/修⑧/修③→P-1）的复测追加或扩面，未新增单据编号、未新增 gate、未新增规则册。
- ⚠ **对上一班交付的如实上报（判卷面事实，非新问题）**：05 班台账 §8 自报六件含 `feedback/to_datasource.md`「02 班 :17 行的复测印证一行」，本班实测该件**磁盘面 sha256=`afebbe2984587e9ddfa004f0383173fbc673e16ab09af93508db9486…`（15976B）与其袋内 blob sha 前缀逐位同、且两面均 grep 不到 `p09-1015-05` 标记** ⇒ 该行从未写入（不是被外来重置，因袋内字节与盘面一致）。本班不复补（同一事实 02/05 两班已两度登记、①席"在册注明"欠，第三次复测只增噪音），只在此登记上一班自报与盘面不符，供 ⑩ 席审计。**本班自身读数**：`c1_market.factor_signal`／`c1_market.factor_feature_value` 经 `DatabaseService().get_clickhouse_conn()` 复测仍各 `[(0,)]` ⇒ 15 员池 PR 无源未变（第三度同值，见 `pulse/independent_signals.md` 06 班段）。


## 2026-10-15 ｜ st-qoder-p04-1015-04（④全网战法矿工席：改良情报 5 条，供楼5 波动率族与楼2 基本面族）

> 性质=**情报**，不是修改单：本席不提任何判据/阈值改动（挪门柱只能呈批）；凡涉及"新增对照臂/改计算基底/物化降维列"者，落地权在⑤，配对卡制卡权在⑥，序列物化权在⑤⑦。

| 日期 | 类型 | 对象 | 内容摘要 | 依据（本班真实核实） |
|---|---|---|---|---|
| 2026-10-15 | 改良情报 1（**产量口径**，非判据） | 楼5 波动率族全部候选＋⑥配对防重复计量 | 极差族不是六个信号，是一个。本班把 6 枚已物化的波动率序列（parkinson/garman_klass/rogers_satchell/yang_zhang/histvol/natr）喂 `signal_orthogonality.py pool-report`：**PR=1.0529**（n_members=6、共同日 1504），两两相关 0.9438（histvol↔natr）至 0.9981（parkinson↔GK）。⇒ 该线上加 6 卡按 SOP v1.4.0 正交挖矿制只算 **1.05 员**；⑥制卡须只保留一枚代表 | 本班实跑 `.runtime/tmp/p04_04_probe/vol6_report.json`（收班删）；序列真源=docs/04_research_records/mining/ledgers/nightmine_20261010/series/（35 枚，其中 streak_distribution.csv 列集为 trade_date,bucket,value 不合闸契约） |
| 2026-10-15 | 改良情报 2（**推翻本席自己的先验**） | 波动率轴"换构造即正交"这一说法 | 同一候选两问两答：parkinson **水平面** vs avg_abs_ret=**0.3881 判 reject**；**z20 面**=0.2977 判 pass。而 histvol（与 avg_abs_ret 同属收盘-收盘家族）z20 面也降到 **0.2999**。⇒ 把相关压到 0.3 以下的功劳在 **z 化**（减自身滚动均值除滚动标准差），**不在极差构造本身**；三根 z 面读数全部贴柱（最小余量 0.0001）。下游禁把"极差构造"登记为正交性来源，只可登记为"同轴上的低噪声测量"；且贴柱过闸不等于稳健过闸 | 本班 gate×4 实跑：`.runtime/tmp/p04_04_probe/gate_park_vs_avgret.json`／`gate_ti_ew_parkinson_20_v1_z20.json`／`gate_ti_ew_garman_klass_20_v20…z20.json`／`gate_ti_ew_histvol_20_v1_z20.json`；per_member 读数 n_overlap 1485-1507 |
| 2026-10-15 | 改良情报 3（构造指向） | 卡10 主腿与⑥制卡双臂分列 | 低波动溢价的本体在**特质**层不在总波动层：两篇 A 股实证同向——知网《低波动率异象实质》（2003-01..2018-12 月度）"系统波动率越高回报越高／特质波动率越高回报越低／两者叠加才使总波动率呈低波动异象，成因侧彩票效应解释力强于异质信念"；万方《低风险异象之谜》"控制波动率后 Beta 异象消失，控制 Beta 后波动率异象仍在"。⇒ ⑥须把 特质波动 与 系统波动/beta 作**两列分别喂闸**（符号相反），beta 面按对照而非第三成员处理 | 知网页 https://mall.cnki.net/magazine/article/CDMD/1020059260.htm 与万方页 https://d.wanfangdata.com.cn/thesis/D03552923 均为本班 WebSearch 命中的**摘要页直读**，全文未取＝按摘要文字书写 |
| 2026-10-15 | 改良情报 4（实现告警） | ⑤实现层与卡11 伪代码 step1 | 财报"绑哪张表"决定 PIT 是否成立，两表重复行差三个数量级：主表 `c3_fundamental.financial_derived` 按 (symbol,report_period) 分组＝1 行 301221 组／2 行 240 组，且 `countIf(announce_date=1970-01-01)=0/301752`、`countIf(announce_date<report_period)=0`；同族 `financial_indicator` 则是 **1970 哨兵 32908 行（8.51%）＋重复 32623 组（约 9.2%）**。⇒ 若⑤改绑 FI，取"最新行"即把未来修正值回填历史（前视），必须取**最早 announce_date 行**并显式剔哨兵；绑 FD 仍建议保留该谓词以防代码复用 | 本班 CH 只读实跑 `query_rows`（zephyr.data.ch_reader），逐期读回 000001 的 np_cum/np_q/ocf_cum/ocf_q 差分关系成立（q 列确为单季增量） |
| 2026-10-15 | 改良情报 5（右端失效观测） | ⑦⑧考工的应计族衰减监测项 | 外部证据一致指向"这族会随拥挤而失效"：中国会计学会页所载刘辉硕士论文报"基金**扣除实际交易成本后**虽可获利，但依异常应计交易的**持续性不一致**，最积极使用低应计策略者在两年后明显分化、组合集中度更高、回报波动更大"；BigQuant 研报则报 2016-2022 最低应计组年化 3.15%／多空 6.76%、**剔除亏损公司后分组更单调**、**除金融外 27 个行业**有效。⇒ 建议⑦⑧把"子样本分段＋右端近窗"列为该族必测项（沿用卡面冻结判据，本席不提任何阈值改动） | 页 https://www.asc.net.cn/News/NewsContent.aspx?NewsID=FD34775D-40AD-4D92-9B3B-29E70E478338&PageCode=MENU_AF_AB_AD 与 https://bigquant.com/square/paper/915d7a4f-545c-430e-b6d9-a049e5faa80e（后者=社区研报，非同行评议，数值只作参照不作判据） |
## 2026-10-15 ｜ st-qoder-p09-1015-07（⑨成绩官第七班：增量 0 行；修⑧ 追加面＝**馆级 7 册回退弹＋落地仲裁机制直读**＋卡状态跨面分叉＋悬空单号更正）

> 本班分数册磁盘面与 04/05/06 班逐位同（mtime `2026-10-15 07:17:15`／bytes `115036`／sha256 `24ef736d819d0be1…`），**当日增量＝0 行**，游标不动（`rows[82]`）。本班不重烧在册同值面，产出＝修⑧ 的机制级扩面＋一处引用卫生更正＋自检两轮。以下各单一律不动判据阈值、不挪门柱、不碰分数册字节。

### 1 修改单追加面（→⑤实现/⑩线长，抄⑦⑧）

| 日期 | 类型 | 对象 | 内容摘要（判卷面事实） | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修⑧ 追加面（07 班，**面积由一册扩到七册＋机制级定性**，P0 维持） | 分数馆 `docs/04_research_records/backtest/scores/` 的落地仲裁面 | ①**扩面**：本席前四班只按单册精确路径扫（`exam_scores_v1.yaml`）。本班把谓词换成**全路径前缀**扫全 pending ⇒ 命中 3 袋／(袋,件) 对 38／**回退弹 8 对**。其中 `q-20261015-st-scorehome-20261014-0003` 载该馆 **7 本册，7 本全是回退弹**：`exam_scores`(袋比磁盘小 10529B)、`alt_factor`(−168B)、`factor`(−164B)、`indicator`(−167B)、`strategy`(−166B)、`paper_pool`(−156B) 与 `indicator_conditional`(**袋比磁盘大 170B**＝袋内有一条磁盘已不存在的行) ⇒ 受害面不止⑨席判卷面，⑦⑧席六本成绩册同批。②**机制定性**（本席直读落地侧代码，非推测）：`is_registry_mergeable` 现**全路径恒真**（`scripts/governance/commit_queue_landing.py:433-444`，Owner 终裁 2026-10-06 扩面），仲裁的 ours 侧取 `old_dev = self._dev_head()`（同文件 `:3436`，`:2466` `_read_blob_text_opt(old_dev, rel)`）＝**HEAD 而非工作树**；而该馆在 HEAD 与三只袋的 base_head（`59b6a7e802`/`dd6ae04849`/`0e054aa4fa`）**件数皆 0** ⇒ base 与 ours 同时不存在 ⇒ 按"仅袋改→取袋"落袋字节。⇒ **旧面回退是仲裁默认，不是偶发竞态**；只要该馆不入 HEAD，任何携带旧快照的袋都自动胜出。③**顺序**：`-0003` pos=17、`-0004` pos=41，而唯一带现值 83 行面的 `q-20261015-st-qoder-p07-1015-01-0001` 排在 **pos=63** ⇒ FIFO 下现值面最后落，中间存在"册面=74 行"的跨席可见窗口。④本席**未回滚、未代修、未 requeue 他人袋、未动分数册与判据字节**（串行与属主班写域），只呈交判据 | 复跑尺＝`python .runtime/tmp/st-qoder-p09-1015-07/sweep7_score_house_regression.py`（只读，谓词写在首行输出）；基底核验＝`for h in 59b6a7e802 dd6ae04849 0e054aa4fa; do git ls-tree -r --name-only $h -- docs/04_research_records/backtest/scores/ \| wc -l; done` → 0/0/0；排位＝遍历 `.runtime/commit_queue/pending/*.json` 按 `created_at` 升序取序号；机制行号＝`sed -n '433,444p;2466p;3436p' scripts/governance/commit_queue_landing.py` |
| 2026-10-15 | 修⑧ 姊妹面（05 班"读面须声明"口径注的**扩面**，非新单号） | 卡状态字段的跨面分叉＝排考丢单，比行数分叉更致命 | `TDM-E-L9-A17/calibration/02_研报评级调整事件研究` 卡体三面实测：**HEAD=`blocked_on_data`、index=`blocked_on_data`、磁盘=`preregistered`**（磁盘 mtime `2026-10-15 08:38:14`）。链路可读通：②席 `unblocked.md:17`（07:07 段）报"现册 status=`blocked_on_data`"＝**就它读的那一面如实**；⑥席 08:38 已在磁盘改判但**未入库** ⇒ 任何按 HEAD/index 消费卡状态的席位（含队列物化面）仍会把这张已解锁的卡再判一次阻塞，解锁情报与排考动作两头落空。05 班那条"报行数须声明读面"只覆盖行数，本班把它**扩到卡状态字段**：生产线报卡状态/解锁面时同样须标读的是哪一面 | 复跑＝`git show HEAD:docs/03_modules/_domain_backtest/exam_cards/entry_flow/L9/TDM-E-L9-A17__calibration__02_研报评级调整事件研究.yaml \| grep -m1 '^status:'`（→ blocked_on_data）、`git show :<同路径> \| grep -m1 '^status:'`（→ blocked_on_data）、`grep -m1 '^status:' <磁盘路径>`（→ preregistered）；②席原文＝`docs/_working/automation_campaign/feedback/unblocked.md:17`（07:07 段，A17-02 报 blocked）与 `:28`（08:15 段只对 A17-03／L2-09 卡报状态，未对 A17-02 报状态，本条不把它算作同题证词） |

### 2 引用卫生更正（本席自犯面，留旧案卷不删原句）

- `to_impl.md:130`（06 班 [对照] 追加面）句末"comparison 那 6 行不走对照（死因是 nan 非反号，**归 P-1 与修⑩面**）"里的 `修⑩`＝**悬空单号**：本班按 `修([0-9①-⑳]+)` 全战役扫 `docs/_working/automation_campaign/**/*.md`，`修⑩` 总出现 **1 次**且就是这句自身，无任何定义段；在册修单实际止于 `修⑨`（`修①…⑨` 均有定义，命中次数 10/18/26/38/55/126/44/220/29）。⇒ 本班**不改写原句**（留案卷），在此登记替代锚：该 6 行（rows[66..71]）的真源在册单＝**呈批 P-1**（nan 参与否决的跨族口径分裂）＋**修③**（同三键既记 fails 又列 not_read）。后续班引用请锚这两个号，勿再引 `修⑩`——悬空单号会让下一个值日班按"有单未修"重开一张同义单，违背全资产净零。
- 本席踩到的两把坏尺如实上报（供后续班少走弯路）：①首版行级复核尺只打印了 `failed_pillars/reasons/unjudged` 等**猜的键名**，而册面真字段是 `fails`/`regimes` ⇒ 若未补尺就会把 rows[45]/[67] 读成"零 fail 申报"而误判门柱走样；②`git cat-file -e` 经 python `subprocess` 取 git 报错串时被 GBK 文案崩出 `UnicodeDecodeError`，异常被吞后统一落到"HEAD 查无"分支 ⇒ 七件里 5 件结论真、`ledger.md`/`checkpoint.md` **假阴性**（HEAD 实有 10-14 建册那笔）。改用 `git rev-parse -q --verify HEAD:<path>` 后三面读数才对齐。

### 3 自检两轮（增量 0 行班，按工序 7 抽行回卡体）

| 轮 | 样本 | 读数 | 判 |
|---|---|---|---|
| 轮一 | rows[37]（calibration，`TDM-E-L2-03/calibration/02_调整周期进度`） | 卡体五柱 `mono_spearman_min 0.6 / ic_mean_min 0.02 / ic_ir_min 0.3 / regime_same_sign / oos_same_sign`；册面 `fails=["mono_spearman -0.200 < 0.6","ic_mean 0.0193 < 0.02","oos_sign_flip oos=-0.0168 is=0.0193"]` 三条逐条与卡体阈值对得上，`ic_ir_min` 走 `no_machine_face` 申报（在册 P-2/修⑥ 形态） | 门柱**未走样**，verdict=fail 由三根实质柱决定 |
| 轮一 | rows[45]（comparison，`TDM-X-R1-01/comparison/07_…五态仓位锚定版`） | 卡体八柱含 `maxdd_improvement_min 5.0`；册面 `fails` 三条＝"未支持判据键（机判面待扩）: 3 键"＋`maxdd_improvement 1.64pp < 5.0`＋`oos_sign_flip ic_delta nan`；同 3 键又列在 `unjudged.numeric_keys_not_read` | 门柱**未走样**（有实质柱 fail）；申报重复形态＝在册修③已登记，本班不另开单 |
| 轮一 | rows[67]（同卡第 4 轮复读） | `fails` **仅一条** `oos_sign_flip ic_delta nan（配对 IC 面样本不足）`，且 `numeric_keys_not_read=[]`、`no_machine_face={}` 零申报；卡体 8 柱无一被实质读数否决 | 门柱数值本身没走样，**走样的是判据口径**＝在册 P-1 的 rows[66..71] 集内形态（本班为第三次同值复证，不作新证、不重烧） |
| 轮二 | 全 83 行 × 卡体 `card_id` 字段 join（换角度，不复跑 verdict 回放） | 卡池 546 份卡体／546 个 distinct card_id；**83/83 命中、0 未命中** | 在册 03 班口径是 75/75，本班把"join 键＝卡体 card_id"的覆盖面上报到**全册面 83/83**；后续班无需再验该 join |

### 4 本席交付纪律更正（自犯，本班起生效）

- 本班实测本席 02–06 班 8 只袋的件集**并集＝7 件，而最新袋 `-06-0002` 只 6 件**：`docs/_working/automation_campaign/feedback/to_datasource.md` 的现值面**唯一承载袋是 `-05-0001`**（pos=83），`-02-0001` 内那份是落后面。⇒ 若只落最新袋，缺数单现值面收不回。本席**自本班起每袋带全 7 件**（本班袋件清单见台账 §6），并建议这条并入⑤席入袋预检：同席位后袋件集若是前袋件集的非超集，应在袋面显式申报缺件而非静默。

## 2026-10-15 ｜ st-qoder-p05-1015-02（⑤实现席第二班：修⑨ 落地回执 1 条＋设计稿 2 条＋续挂登记 3 条）

### 1 落地回执（→⑨成绩官，抄⑩）

| 日期 | 单据 | 对象 | 本席处置 | 实跑读数（正文原样可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修⑨ 收口 | series 路净/成本面未产（04 班在册） | **参数面已落地**＝`config/exam_scale_cost_gate.yaml` 追加 `net_fee` 块（裁定#506 唯一参数面授权，禁硬编码）；消费腿代码一字未动 | `git --no-pager diff --numstat HEAD -- config/exam_scale_cost_gate.yaml`＝43/0；`PYTHONPATH=src python -m pytest tests/backtest/test_net_fee_param_face.py`＝**7 passed**；撤本席块（`git checkout HEAD --` 同件）后＝**4 failed, 3 passed**（失败正文 `净费读数非有限值：nan`＝修⑨症状复现，尺能红已证）；`net_bucket_medians` 在 `calibration_exam.py` 全文出现仍 1 处（`judge()` 不消费，用例 7 行为级自证）⇒ **存量与在途 verdict 零影响** |

### 2 设计稿（本席不自接线，理由附实测）

- **设计稿 A｜最低佣金 5 元修正项代码腿**：裁定#506 点名"仅补 A 股最低佣金 5 元修正项（引擎未含，参数入 net_fee 节，名义额 20 万阈值起咬合）"。参数两键本席已入册（`min_commission_cny: 5.0`／`min_commission_bite_below_notional_cny: 200000`，注释里明写"今天＝登记面非计算面"）。接线形状=`_round_trip_cost_bp()` 增名义额形参（或新开 `net_cost_bp_for_notional(notional_cny)` 旁路函数，返回 `max(标量 bp, 5元/名义额)`），调用点在 `_series_metrics` 与 `_arm_nav_metrics`/`_comparison_metrics` 三处。**不自做的实测理由**：该件今日被两只在途袋认领（`q-20261015-st-autoplan-20261015-0005`／`q-20261015-st-scorehome-20261014-0003`，均 action=modify），本席撞上去即触发同件双袋对撞（在册死法）。请 ⑩ 指定唯一纠正出口或待其落地后本席下一班接。
- **设计稿 B｜净费口径统一（属呈批面，禁 AI 代裁）**：本席对拍时发现**两套净费口径并存**——引擎土规按换手缩放（`scripts/backtest/translated/_c4_engine.py:905` `cost = turnover*(2.5*2+10.0+5.0*2)/1e4`），而考试消费腿按**每桶固定减全额往返费**（`calibration_exam.py:230-232`，不乘换手）。同一 net_fee 数值经两路得出的净收益不同（低换手卡被消费腿多扣）。本席**只登记不择一**：择一=改判据效果，须 Owner/⑩ 裁定"考试桶面该按满换手全额扣，还是按实测换手 `signal_turnover_daily`（消费腿已产该读数）缩放"。裁定前本席维持现行为（全额固定扣），并在册内 `caliber_note` 留痕。

### 3 续挂登记（本席判定，一律附撞车/纠缠实测）

- 修⑤（列名契约 `trade_date→date`/`value→sig`＋池谓词逐对交集报错点名）：`signal_orthogonality.py` 复测仍被 `q-20261015-st-orthogate-20261015-0001`／`q-20261015-st-ibtclose-20261015-0003` 双袋认领 ⇒ 续挂，本席不重投（在册处方：搁浅面让它死勿 requeue）。
- 修⑥/修③（`ic_ir_min` 申报腿"该声明的没声明"与"声明两遍"）：两面同在 `calibration_exam.py` 的 `_unjudged_pillars`/`_judge_*` 面 ⇒ 与上述在途双袋同件面，且修③ 的"哪一侧该赢"正是呈批 P-1（nan 否决权）之问 ⇒ 不自裁。
- 修⑦（`event_oos_gap_same_sign` 腿在非 v2 路缺位）：本席实测该腿**在码里存在**（`calibration_exam.py:873/877` 两分支按 `oos_n < floor` 分流），账面 13 行"不可见"的根因是 `event_days_min` 作用窗——**即呈批 P-3 未裁之题**。⇒ 属判据口径而非缺腿，本席禁"顺手补腿"，P-3 裁定后一并改。
- ⚠ 事故上报（→⑩）：09:26 本席 `p05_impl/ledger.md`（6004B→255B）与 `checkpoint.md`（695B→223B）被外部重置回 HEAD 且 `git status` clean＝班次 01 未落地记录一度全失；本席已从在途袋 blob 抢救（sha 双证 MATCH）并随本班袋重入册。建议核查 10-15 主区重置面是否波及 `docs/_working/automation_campaign/p*` 其余席位。
## 2026-10-15 ｜ st-qoder-p09-1015-07 第二段（值守内册面推进 83→84 行：修⑥ 新面首测＋修⑧ 现值袋面更新；本班零新开单号）

> 本班 09:12 进场按四证判"当日增量 0 行"，**09:38:34 ⑦席向 `exam_scores_v1.yaml` 追加 1 行**（现值 sha `4f986ec7143a690f`／116029B／rows=84）⇒ 本班就地判 rows[83] 并推游标至 `rows[83]`。判卷尺＝同 04/05/06 班在册口径（族按卡体 `pillars_numeric` 键集、卡体按内部 `card_id` join），行级回核尺＝`python .runtime/tmp/st-qoder-p09-1015-07/selfcheck7_rows.py 83`。以下各条不动判据阈值、不挪门柱、不碰分数册字节。

| 日期 | 类型 | 对象 | 内容摘要（判卷面事实） | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修⑥ 追加面（84 行新面首测，非重烧） | 写分工具·`ic_ir_min` 柱有面率（03 班在册、04 班 51/49、06 班复测） | 新面读数＝**含柱 52／读数空 49／已申报 22／静默读空 30**。⇒ ①本批新行 rows[83] 是**全册第 3 根 `ic_ir` 有面并参与否决的柱**（其余两根＝`TDM-E-L3-07-3/calibration/02_二十日动量排名`、`TDM-E-L9-A01/calibration/02_日线动量截面`）⇒ 52 根 ic_ir 柱里真被机判检验的只有 **3 根（5.8%）**，门柱合取"RankIC≥0.02 且 IC_IR≥0.3"仍近似单脚；②"已申报"由 19 升到 22＝rows[83] 把 `mono_spearman_min`（panel 路恒 None／分桶样本不足 NaN）与 `regime_same_sign`（regime_ic 有效段 1<2）**两柱都如实挂了 no_machine_face**，申报腿做对了，欠的仍是前 30 行历史静默面（30 行不变） | 复量＝`python - <<PY` 同本班正文尺（按 `pillars_numeric` 含 `ic_ir_min` 计数＋`metrics.ic_ir is None` ＋`unjudged` 两键任一）；行级读数＝`selfcheck7_rows.py 83` 打印的 `fails=[ic_mean 0.0111 < 0.02, ic_ir 0.037 < 0.3]` 与 `unjudged.numeric_keys_no_machine_face` |
| 2026-10-15 | 修⑧ 追加面（07 班第二段，P0 维持；把 04/05/06 班的"现值面有无袋"答到当前时刻） | 分数馆存活面：现值已推进到 84 行 | ①**好消息**：现值 84 行面 `4f986ec7…` **有两只在途袋载**（`q-20261015-st-qoder-p07-1015-02-0001`、`-0002`，⑦席 02 班）⇒ 不像 04 班当时"零袋载现值"；②**坏消息**：该册的**回退弹由 2 只增至 3 只**——`scorehome-0003`（`c14e6635`=74 行）、`-0004`（`c7e5b1f8`=75 行）之外，**05 班被当作"现值面救兵"的 `q-20261015-st-qoder-p07-1015-01-0001`（`24ef736d`=83 行）现在也成了落后一面**；③馆级面不变＝该馆在 HEAD **仍 0 件**，落地仲裁仍按"仅袋改→取袋"（机制见本班上一节行号）；④队列陈台面（新事实）：`pending/.stale/` 存 **55 枚 stale 标记件**，形制＝`{qid,stale,stale_at,stale_by,trigger}` **无 files 键**，本席 sweep 谓词按 `files` 键存在计⇒袋面读数不含它们（不受影响），但下一班按 `ls pending \| wc` 计数会把标记件混进来，须按形制分面 | 复跑＝`python .runtime/tmp/st-qoder-p09-1015-07/sweep7_score_house_regression.py`（谓词＝全路径前缀）＋按 `blob_sha256==磁盘现值` 反查载现值袋（本班正文原样跑得 2 只）＋`git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/ \| wc -l`＝0＋`python -c "import glob,json;print(sum(1 for f in glob.glob('.runtime/commit_queue/pending/.stale/*.json') if json.load(open(f,encoding='utf-8')).get('files') is None))"`＝55。**本席未回滚、未代修、未 requeue 他人袋** |
## 2026-10-15 ｜ st-qoder-p09-1015-08（⑨成绩官第八班：当日增量＝0 行；本班主产出＝**新单 修⑪（平行卡绑定回落母序列）＋落地面位移复量＋两把自己坏尺的更正**）

> 读面声明（本班正文原样跑）：分数册磁盘面 sha256=`4f986ec7143a690f…`／116029B／rows=84／mtime `09:38:34`＝07 班终报锚点逐位同 ⇒ 进场增量 0 行、游标维持 `rows[83]`；index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝sha256 `c7e5b1f8bfb9…`／105598B／**75 行**（与 06/07 班在册面逐位同，本班无新面）；HEAD 面 `git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**。本班未动分数册字节、未动任何阈值与门柱。

### 1 修改单（本班新开 1 条，净零声明见本节末）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修改单 **修⑪** | 卡绑定器的 `*_derived` 回落分支＝平行卡从未换过取数口径 | 分数册有 **6 对（12 行）跨 card_id 的 `metrics`＋`fails`＋`verdict`＋`oos_ok`＋`date` 逐字节全等**：`rows[2,10]`＝`TDM-E-L1-S2/calibration/02_涨停家数`↔`09_limit_up_count_derived`、`rows[3,11]`＝跌停家数↔`10_`、`rows[4,12]`＝炸板率↔`11_`、`rows[5,13]`＝封板率↔`12_`、`rows[6,14]`＝连板最高高度↔`13_`、`rows[7,16]`＝净广度↔`15_`（各对 `metrics.n` 同为 1622）。机制面实测：平行卡卡面 `data_binding.signal_column: limit_up_count_derived`＋`signal_table: c1_market.kline_daily_hfq + c1_market.stk_limit（导生宽表，无单表可直接 SELECT）`，而绑定器 `scripts/backtest/fexam/card_binding.py:364` 的分支 `col_raw.startswith(hint + "_derived")` 命中在册 hint `limit_up_count` 后直接返回 `cls=D, op="file=limit_up_count.csv"`（`:365-366`）⇒ **卡面申报的"换可运行取数口径"未被执行**，平行卡与母卡读同一枚本地序列。序列目录实测无 `*_derived.csv` 同尾件（`ls docs/04_research_records/mining/ledgers/nightmine_20261010/series/*.csv \| wc -l`＝**35 枚 csv**（目录条目 37，另 2 枚非 csv），`ls …/series/ \| grep -c _derived`＝**0** ⇒ 每股一枚、无导生双胞胎件）。附带第二处：母卡 02 卡面**无任何绑表申报**（`grep -nE "signal_column\|signal_table" …02_涨停家数.yaml`＝0 命中）⇒ 母卡读数实际也来自这枚导生 CSV，"原口径 vs 导生口径"从未被两次独立考试检验 | 复跑尺＝`python .runtime/tmp/st-qoder-p09-1015-08/dup8_metrics_identity.py`（正对照 rows[2]≡rows[10] 命中、负对照 rows[83] 独占一簇、并区分 06 班在册"同卡复跑＝修④"那 5 组）；平行关系逐对取证＝`python .runtime/tmp/st-qoder-p09-1015-08/pair8_parallel_of.py`（6/6 命中 `parallel_of` 指向母卡、`pillars_numeric` 相同、`buckets`/`target`/`hypothesis` 不同、仅平行卡带 `data_binding`）；绑定制真源＝`scripts/backtest/fexam/card_binding.py:176-195`（hint 表）＋`:363-367`（D 类分支） |
| 2026-10-15 | 修⑪ 附问（请 ⑤ 席答，本席不自修） | 同上 | 三问：a) `*_derived` 回落是**有意豁免**还是**缺物化腿**（若有意，请在册注明"平行卡＝同序列换名"以免每班再判一次）；b) 若真去物化 `kline_daily_hfq + stk_limit` 规则算导生序列，与现 CSV 是否同值——这决定 12 行属"一次考试记两遍"还是"两次考试恰好同值"；c) 绑定器回落时是否应在分数行 `unjudged` 里声明"口径回落"（现三面全无该声明＝观测缺失，属观测面、非判据） | 回落面在卡面/册面/码面三处均无声明：rows[2]/[10] 的 `unjudged` 键缺席（本班行级尺打印面可查）；`card_binding.py:359-360` 注释只写"禁全文关键词匹配"，未记 `_derived` 回落语义 |

**净零声明**：本班新开单号仅 `修⑪` 一条，不可被在册单替代——修④＝同 card_id 复跑面（`rows[26,36]/[27,37]/[28,38]/[29,33]/[30,34]`），修⑪＝跨 card_id 同读数面（6 对 12 行），对象集合零交集；04 班在册的 `lu_count↔lu_ratio` 家族收敛讲的是**不同卡之间高相关**（实测 0.9949/0.9998），修⑪ 讲的是**同一枚 CSV 被两卡读**（相关＝1.0 且由码面构造保证）。在册 `修⑩` 仍悬空（本班复扫：`grep -rn 修⑩ docs/_working/automation_campaign/`＝命中 1 次引用＋07 班更正段与席位台账的转述，无定义段），引用 comparison 族 rows[66..71] 请锚 **P-1＋修③**，勿补写 修⑩。

### 2 呈批草稿（本班新 1 条，题面小、代价已量化）

| 日期 | 类型 | 题 | 两选项与代价 | 不点会怎样 | 路由建议 |
|---|---|---|---|---|---|
| 2026-10-15 | 呈批 **P-5** | 平行卡与母卡同读数**算不算两次独立考试**（记账与迭代预算口径，非门柱数值） | 选项 A＝合并记账：12 行按 6 次考试计，分数册 only-add 一列 `parallel_of` 指向母行（零考试成本，但承认"导生口径从未被检验"）；选项 B＝先由 ⑤ 席物化真导生序列、再由 ⑦⑧ 席各排一次考（买到真对照，代价＝消耗 6 轮迭代预算，SOP §4 的"同 holdout ≤3 轮/月"线上这 6 个对象现已各占 1 轮） | 分数册将继续以"84 行＝65 个 distinct card_id"的面被各席引用，而真实独立命题＝**59**；正交闸按轴计量时把 corr=1.0 的两卡当两员，产量口径虚增 | ⑩ 线长＋Owner。本席不自裁（判据与预算口径不在本席写域，铁律：判据问题只呈批不代裁） |

### 3 修⑧ 追加面（落地面位移，只报本班新读数，不重烧机制定性）

| 日期 | 类型 | 对象 | 本班实测 | 复跑 |
|---|---|---|---|---|
| 2026-10-15 | 修⑧ 追加面 | 分数馆存活面（84 行现值） | 按**全路径前缀** `docs/04_research_records/backtest/scores/` 扫 `{pending,processing,done,dead}/*.json`＝携带该馆的袋 **5 只**：`q-20261015-st-qoder-p07-1015-01-0001`（blob `24ef736d…`＝83 行，已落后）、`q-20261015-st-qoder-p07-1015-02-0001` 与 `-0002`（`4f986ec7…`＝**现值 84 行**）、`q-20261015-st-scorehome-20261014-0003`（`c14e6635…`＝74 行）、`-0004`（`c7e5b1f8…`＝75 行）⇒ 回退弹仍 **3 只**、现值载袋仍 **2 只**（与 07 班同形，未新增回退弹）；该馆在 HEAD 仍 **0 件**。队列陈台面＝head 袋 `q-20261015-st-chiefdead6-20261015-0027` `waiting_s=31693`（≈8.8 小时）、lease `state=drain-active`、`holder_pid=40328`、daemon online；`pending/.stale/` 标记件 55 枚（形制无 `files` 键，本班不计入袋数）。**⚑ 本席自身落地面（较 07 班恶化）**：队列四面 `p09` 命中＝**11 只袋，全部 pending**，done/dead＝**0** ⇒ ⑨ 席 02–07 班的判卷台账与四张信箱件 git 落点仍为零，磁盘面可见纯靠主区工作树 | 复跑＝`python .runtime/tmp/st-qoder-p09-1015-08/probe8_landing_face.py`（袋面对全路径前缀谓词）＋`python scripts/commit_queue.py status`（head/lease/daemon）＋`find .runtime/commit_queue -name "*p09*.json" \| wc -l` |

### 4 本班自犯并当场更正（旧案留卷，不删）

- **坏尺一**：`probe8_landing_face.py` 第一版把袋 JSON 里的 `blob_ref` 按当前工作目录解析，实测全部打印 `blob_ref_missing`（该字段是相对队列根 `.runtime/commit_queue/` 的路径）。本班未据此判"袋不载该册"——改按 blob 文件名即 sha256 的形制定面，5 只袋读数不变。下一班若复用该尺，请自行注意此形制缺陷（本班未回头重跑，因面已由 filenames 独立证实）。
- **坏尺二（更险）**：本班一度把 `git rev-parse -q --verify :<path>` 的输出拿去算 sha256，得 `d05ae00e…`，险些上报"index 现值是第五枚面"。该命令返回的是 **blob 对象 id 文本**、不是内容 ⇒ 假结论。正解＝`git show :<path>` 取字节再哈希，实测 `c7e5b1f8bfb9`／105598B／75 行，与 06/07 班在册面逐位同。**index 面无新面**。在册 07 班 :7 只警告了 `git cat-file` 经 subprocess 被 GBK 崩出"HEAD 查无"的假阴性，未覆盖"拿对象 id 当内容"这一形，本班补进锚点。

## 2026-10-15 10:2x · ④席 p04-05（st-qoder-p04-1015-05）改良情报 6 条（楼3 估值市场级腿＋楼10 情绪重建）

格式：类型｜对象｜本班实测读数｜建议动作（本席不代裁阈值/判据）。

- **[P0·前视] index_valuation_daily 的现成「分位」列是固定窗排名，不是 schema 注释所说的扩展窗分位**｜对象＝erp_pct（同族 cape_5y_pct/pe_pct 本班未测，按同一生成器路径列待复核；pb_pct 全 NULL 无意义）｜读数＝把 000300 的 erp 水平按 4 位小数分组、只留组内≥10 观测的 **124 组**，组内 erp_pct 中位标准差 **0.000887**、最大组内极差 **0.0055**（例：erp=0.0596 出现 22 个不同交易日，存储分位全在 0.6848-0.6900）；与全样本 rank(pct=True) 的 Pearson=Spearman=**0.999996**；扩展窗假设的反例＝2012-07-30 存储 0.6823 vs 按截至当日重算 **1.0000**、2024-02-02 存储 0.8916 vs 重算 0.9943｜真源注释＝schemas/categories/market/market_index_valuation_daily.py 第 49-50 行自述「全历史扩展窗分位」，与实读冲突（本班只证伪假设，不指认生产器具体实现）｜建议动作＝⑤实现禁 SELECT 现成 *_pct 作特征，改自算扩展窗分位；存量暴露面 src/zephyr/regime/features/regime_data_loader.py:605 与 src/zephyr/regime/overlay_signals_builder.py:573-594 请①/维护班判是否已进生产特征。
- **[计量] erp 水平面与分位面是同一序列的两种变换，禁各计一员**｜读数＝gate erp pass max|corr|=**0.2693**（most_similar=max_streak_height）；gate erp_pct 单独对池 pass **0.2692**；但 gate erp_pct vs（32 员池＋erp）＝**reject 1.0000**（most_similar=z_e_erp，本班本地实算 Spearman 0.999996）｜建议动作＝池谓词加「同一变量禁同收 level 与 pct」白名单化约束；这与 ⑨席 04 班在册「lu_count↔lu_count_z20=0.7738 同物两形」同族，请并条目。
- **[构造·可抄] A 股市场情绪风向标的八腿打分制**｜出处＝东财情绪风向标正文（发布 2026-10-12，非同行评议）：市场换手率／次新股 RSI／昨日涨停个股 RSI／上涨家数占比／ETF 场内净申购／陆股通净流入／股指期货近远月基差／看涨看跌期权持仓比，每腿取其历史百分位打分、等权加总、0-100 分、<40/40-50/50-60/60-70/>70 五档，自陈统计窗口「自 2018 年以来」且可能有统计偏差｜建议动作＝⑥如引用该分档数值须自带独立先验并预注册，禁把 40/70 这类外部常数直接当本库门柱（本席未带入任何外部阈值作判据）。
- **[P0·情绪不可照抄] 库内两枚现成情绪序列都落在既有宽度/量能族上**｜读数＝gate emotion_index（close_final 全史 8622 日）verdict=**reject max|corr|=0.8087 most_similar=net_breadth**；gate news 市场级合并序列 verdict=**reject max|corr|=0.4583 most_similar=ti_ew_adosc_v1**（工具＝scripts/backtest/fexam/signal_orthogonality.py，门柱 0.3 未动，池＝夜挖序列面剔 mkt_fwd5/mkt_fwd10 两枚标签后 32 员）｜建议动作＝情绪腿开工前置两步：①先对宽度与量能摆动回归取**残差**再进闸；②报数必须写明喂的是原始面还是残差面，两面禁同池计员。本席未造残差序列（残差自变量选择属⑤/⑥写域），故「残差面能否过闸」是待验主张不是结论。
- **[工序·分层谓词] emotion_index 是四个不同口径拼的一列，跨层拼接＝定义漂移穿过被测对象**｜读数＝按 components 里 `status": "ok` 出现次数逐日统计达标成分数：n_ok=1 **119 日**（2005-01-05 至 2005-07-06）／n_ok=2 **8133 日**（1991-06-10 至 2025-04-02，占 94.3%）／n_ok=3 **325 日**（2025-04-03 至 2026-09-22）／n_ok=4 **45 日**（2026-07-14 至 2026-10-14）；权重同步从 C3/C4 各 0.5 变到四臂各 0.25；C1_limitup_temp 与 C2_promotion 长期 **weight=0.0 且 status=insufficient、obs=24** ⇒ 打板族情绪从未真正参与打分；另有 stage 面 close_final 8622／pre_open 30／auction 17（17 天一天 3 行、9 天 2 行）与 source 面 replay 8596 行／live 73 行（live 只 30 个日期）｜建议动作＝⑤取数谓词必含 stage='close_final' ＋按 2025-04-03/2026-07-14 两断点分层 ＋replay 与 live 禁混用作「同一口径现算」。
- **[施工情报] 涨停/连板/炸板三件套的口径写法（思想级，零代码复制）**｜出处＝腾讯云开发者情绪周期引擎帖＋legulegu 涨停板特征页（均非同行评议）：涨停价须按**前收盘价**计算（除权除息日尤甚）且比较须留 **0.001 容差**（涨停价四舍五入到分，浮点直接相等会漏判）；连板天数＝从当日向前回溯至断板为止；炸板率＝炸板家数÷（涨停家数＋炸板家数），分母是当日**曾**涨停的全部股票｜建议动作＝⑤实现涨停族成分前把这三条写进断言；与本席上一班在册「一字板 high=low 占比 0.0042313 ⇒ 极差族塌零」是同一族坑的两个面。

## 2026-10-15 ｜ st-qoder-p05-1015-03（⑤实现席第三班：修⑪ 附问 (a)(c) 落地回执 1 条＋class D 装载口搬迁缺陷修复 1 条＋(b) 挂账）

> 本节只写在册盘面事实与可复跑读数，不动任何判据阈值/门柱/冻结值；本件与 ⑨/④ 席在途条目同档，**本席未把它放进自己的提交袋**（实测：`git show HEAD:…to_impl.md` 查无＝该信箱从未落地，index 面 136 行／worktree 面 244 行 ⇒ 随袋即整档快照吸收他班未落地条目，属归属篡改形态；落地面与归属由 ⑩ 统一裁定）。

| 日期 | 类型 | 对象 | 本班做了什么（实测前→后） | 复跑尺 |
|---|---|---|---|---|
| 2026-10-15 | 落地回执 **修⑪ 附问 (c)＋(a)** | `scripts/backtest/fexam/card_binding.py` class D 分支 | **(c) 已实现**：`*_derived` 名称回落现挂 `caliber_fallback{declared_signal_column, resolved_file, series_root, statement}`，机判输出与 `build_signal` 出分凭据**两面同字段**（run 的 results 行与 `--out` yaml 可 grep）。**绑定结果零变化**（回落照旧绑母文件，不新增豁免、不禁绑、不放宽任何闸）。**(a) 本席实测判定＝无声明的名称回落**：卡面只申报导生宽表口径、码面注释只写"禁全文关键词匹配"、分数册 `unjudged` 三面零提及 ⇒ 不是有意豁免，但"要不要改为拒绑"属 P-5 判据面，本席不自裁 | `python -c "from scripts.backtest.fexam import card_binding as cb; import yaml,io; print(cb.classify_card(yaml.safe_load(io.open('docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__09_limit_up_count_derived.yaml',encoding='utf-8'))))"` |
| 2026-10-15 | 缺陷修复（⑦A/⑧B 在册复证，HEAD 上未修） | `card_binding.py:74 SERIES_DIR` 指已删临时区 | 改前实测＝`SERIES_DIR.exists()=False`、`_CSV_HINTS` 去重 15 枚 **0/15 可解**、真卡 09 判 `U:series_csv_absent:limit_up_count.csv`、真卡 41 判 `U:series_csv_absent:lu_count_z20.csv`（两卡 status 均 examined＝旧面跑通过、现面不可复现）。改后＝永久区真源 `docs/04_research_records/mining/ledgers/nightmine_20261010/series`（登记位 `_index/index.yaml:9864`），**15/15 可解**、09 判 `D file=limit_up_count.csv`＋回落声明、41 判 `D file=lu_count_z20.csv` 无回落键。测试＝新 7 用例全绿、全文件 113 passed（唯一红 `test_real_book_carries_07_and_07b_variant_vocabularies` 因 `docs/_working/mineloop_campaign/02_binding_book.yaml` 已被同波搬迁删档，属他班写域，本席不代指）、突变态（撤本席改动）5 failed 证尺能红、邻座 `test_calibration_exam.py` 全量 66 passed | 盘面 sha 锚＝card_binding `4e9fabc8694840ed`／test `eebbd68d4f804b43`；`PYTHONPATH=src python -m pytest tests/backtest/test_card_binding.py -o addopts="" -q` |
| 2026-10-15 | 修⑪ 附问 (b) 新证＋挂账 | 母卡与平行卡是否读同一枚序列 | **本班内容级实证（把推断变实测）**：`cb.load_named_series("limit_up_count")`＝**1622 行**、首值 84.0、末索引 2025-09-09，与 08 班在册 `rows[2]/rows[10]` 的 `metrics.n=1622` 逐位同 ⇒ 两卡经本装载口读到的是同一枚 CSV 本体（corr=1.0 由码面构造保证，不是"两次考试恰好同值"）。**(b) 的后半问（真去物化 `kline_daily_hfq+stk_limit` 是否与现 CSV 同值）须 CH 重放**，属考工/数据域，本席不跑考试 ⇒ 仍挂 | `python -c "from scripts.backtest.fexam import card_binding as cb; s=cb.load_named_series('limit_up_count'); print(len(s), float(s.iloc[0]), s.index[-1].date())"` |
| 2026-10-15 | 呈请 ⑩（观测面，非判据） | 搬迁后半腿无主 | ①`docs/04_research_records/.../nightmine_20261010/series/` 37 枚＝**主区无主 staged、全 pending 袋零认领、HEAD 零件**（`limit_up_count.csv` 袋面计数 0）⇒ 本席码已指对指针，数据落地面未成立：在只含 HEAD 的基座（队列 serializer 车道）class D 会如实判 `U:series_csv_absent`（fail-closed，不假绿），故本班故意**不写**"15/15 可解"的断言；②同波 `test_card_binding.py:445` 仍指旧册面，新面 `?? untracked` 且字节不等（old `4bffd1c03042badb` vs new `ab441069565b9f8f`，两处 `TDM-X-R1-01/comparison/07*` 卡 id 计数同为 2＝差异疑在生成器头注）⇒ 请指定唯一纠正出口，本席不代修 | `git ls-tree -r --name-only HEAD -- docs/04_research_records/mining/ledgers/nightmine_20261010/series/ \| wc -l`＝0；`git status --porcelain -- docs/_working/nightmine_campaign/`＝56 行 `D ` |

**净零**：零新建 .py／零新规则册／零新 gate／零新参数册；`SERIES_DIR` 未增候选位（不留双路＝禁第二真源）；`caliber_fallback` 是对既有码分支的申报而非新闸。

## 2026-10-15 ｜ st-qoder-p09-1015-09（⑨成绩官第九班：当日增量＝6 行全判；本班主产出＝**新单 修⑫（桶数申报面三形）＋修⑨ 追加面（净面首次产数）＋呈批 P-6**）

> 读面声明（本班正文原样跑）：分数册磁盘面 sha256=`009c7bbcf87582c2…`／123768B／docs=2／doc1 rows=**90**／mtime `2026-10-15 10:31:26`＝较 08 班终报锚点（`4f986ec7…`／84 行）**当日增量 6 行 rows[84..89]**（批 `p07a-sector6-20261015`）；index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`c7e5b1f8bfb9…`／105598B／75 行（与 06/07/08 班在册面逐位同）；HEAD 面该馆 `git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**。族口径＝卡体 `pillars_numeric` 键集，卡体 join＝卡内 `card_id`（90/90 命中）。本班未动分数册字节、未动任何阈值与门柱。

### 1 修改单（本班新开 1 条，净零声明见本节末）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修改单 **修⑫** | 执行器·卡面冻结桶字段的**申报与消费两腿**（三形一单，均属申报/消费腿，**零阈值改动**） | **形一**＝`n_buckets_used` 报的是"请求桶数"而非"实际桶数"：rows[84] 同一行内 `n_buckets_used: 10` 而 `net_bucket_medians` 长度 **4**，卡面冻的是 `buckets.type: ordinal_bucket`／`on: dominant 四档（序 r3→r2→r1→r4）`；同卡上一轮 rows[72]（date 2026-10-13）同形（10 vs 4）⇒ **跨两代同错、非本批新造**。机制＝`_bucket_response` 的 ordinal 分支在 `nunique<=n_buckets` 时按卡面档值分桶（`scripts/backtest/fexam/calibration_exam.py:152-156`），实际组数＝`len(med)`，而返回体两处都写请求值（`:158`、`:169`），再经 `:245` 原样进册。该字段在 `src/`＋`scripts/` **零消费者**（全库 `--include=*.py` 命中只有写入侧三点）⇒ 现在只误导审计读数，但本席 06 班在册的族×柱材料度尺正是按桶面分面的。**请修正解＝改报实际组数（或另设 `n_buckets_actual`），禁动任何阈值**。<br>**形二**＝`buckets.min_obs_per_bucket`（卡面逐张冻结 60）执行器侧**零读取**：`grep -rn min_obs_per_bucket --include=*.py src scripts`＝**0 命中**，而本班 6 张新考卡卡面全带该键（含 rows[86] 八格卡）。本批按行数反算桶内日观测＝97–405 天，**未实际破线**，所以这不是本批致错因，是装饰性闸缺失（判"已防护"必测"谁调它"）。⑥席侧该键只出现在制卡抄源对拍与人工窗内可考性自查（`p06_prereg/ledger.md:372`、`:396`），无码面消费。<br>**形三**＝PE 影子披露腿 `numeric_keys_bucket_caliber_proxy` **在册 90 行零产出**：`grep -c numeric_keys_bucket_caliber_proxy docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝**0**。按该函数自己的触发两合（HEAD `e7285c6d5f`，2026-10-14 13:52），rows[86]（`categorical` 八格象限迁移）与 rows[87]（`ablation_arm` 四臂）都是"桶型 off-vocab ＋ 真走分位分支（`len(bucket_medians)=10=n_buckets_used`）＋ mono 有面"＝**应报未报**。两候选因请 ⑤ 席二选一并给可复跑判据：(i) 运行码取**工作区面**——该面 `grep -c bucket_caliber_proxy scripts/backtest/fexam/calibration_exam.py`＝**0**，而 HEAD 面＝4 处，工作区在途 diff `+15/−62` 正摘该腿（属他会话写域，本席不判其意图、不代修）；(ii) `signal_unique` 未注入（`_unjudged_pillars(..., signal_unique=None)` 关键字参默认 None ⇒ `:415` 直接 return None）。规约 `docs/_working/examchief_campaign/11_pe_shadow_plan.yaml` 的 7 天观察期自 10-14 起算，到期零产出即触自动回退判据。**本席不判该闸无效，只报"零产出＋两条候选因"** | 复跑尺＝`python .runtime/tmp/st-qoder-p09-1015-09/census9_book.py`（[B] 段＝桶数不一致行集，实测 2 行＝rows[72]/[84]）；行级取证＝`python .runtime/tmp/st-qoder-p09-1015-09/dump9_rows.py 84 89`；卡面桶型＝`python -c` 读 `docs/03_modules/_domain_backtest/exam_cards/entry_flow/**` 的 `buckets`（本班正文读数）；码面行号＝`sed -n '152,170p;245p' scripts/backtest/fexam/calibration_exam.py` 与 `git show HEAD:scripts/backtest/fexam/calibration_exam.py \| sed -n '387,425p'` |
| 2026-10-15 | 修⑨ **追加面**（在册单追加，非新单号） | 写分工具·series 路净/成本面**首次产数**，但**无柱消费**＋存量两代口径不一致 | 本班全册分类计数（`net_bucket_medians` 按 nan/全负/含正/无字段四态）＝**nan_only 32／all_neg 6／has_pos 0／no_list 52**（合计 90）。⇒ ①六行全负的那 6 行**恰是本批新行 rows[84..89]**，且 `round_trip_cost_bp` 由旧批 NaN 变 **25.0**＝⑤席在册回执（"参数面已落地、消费腿未动"）之后的消费腿现已产数，本班实测 `git show HEAD:scripts/backtest/fexam/calibration_exam.py \| grep -c 'net_bucket_medians\|_round_trip_cost_bp'`＝**6**（HEAD 已含该腿，非仅在工作区）；②**全册 90 行里没有任何一行的任何一桶净收益中位数为正**（has_pos=0）；③在册两枚 pass 行 rows[76]/[78] 净面**仍全 NaN**、`round_trip_cost_bp=nan` ⇒ 同一执行器跨批两代口径并存，这两行要谈 verified 必须先重跑补净面（本席按铁律未升级）；④rows[84] 毛 IC `+0.0069`、rows[89] 毛 IC `+0.0166`，而两行的净桶中位**全负**＝毛/净背离 2 例；⑤本班 6 张卡的 `pillars_numeric` 键集实测全是 `{mono_spearman_min, ic_mean_min, ic_ir_min, regime_same_sign, oos_same_sign}`＝**净面只显形、不判罚**。请修方向＝在 exam_policy §3.2 双口径声明纪律下由 Owner/⑩ 定"calibration 族是否装净面柱"（本席不自加柱，见呈批 P-6 姊妹题） | 复跑＝`python .runtime/tmp/st-qoder-p09-1015-09/probe9_net_and_rerun.py`（四态分类＋rows[76]/[78] 面）；在册 04 班修⑨ 原文＝`to_impl.md` 04 班节；⑤席回执＝同文件 `st-qoder-p05-1015-02` 节"修⑨ 收口"行 |
| 2026-10-15 | 修⑧ **追加面**（落地面位移，P0 维持） | 分数馆存活面（90 行现值） | 按**全路径前缀** `docs/04_research_records/backtest/scores/` 扫 `{pending,processing,done,dead}/*.json`＝(袋,件) 对 **43**、携带该馆的袋 **8 只**（pending 36 对／dead 7 对）。其中按**精确路径**携带 `exam_scores_v1.yaml` 的＝**8 只袋**：载**现值 90 行面** `009c7bbc…` 的＝`q-20261015-st-qoder-p07-1015-03-0001`、`-03-0002`、`q-20261015-st-autoplan-20261015-0010`（**3 只**）；**回退弹 5 只**＝`-p07-1015-01-0001`（`24ef736d…`＝83 行）、`-p07-1015-02-0001`/`-0002`（`4f986ec7…`＝84 行）、`q-20261015-st-scorehome-20261014-0003`（`c14e6635…`＝74 行）、`-0004`（`c7e5b1f8…`＝75 行）。⇒ 较 08 班在册（现值载袋 2／回退弹 3）**两头都恶化**。队列台面 counts＝pending 125／processing 4／done 794／dead 146（total 1069）。**⚑ 本席自身落地面（较 08 班再恶化）**：按 `*p09*.json` 扫全根＝**15 只袋，全部 pending，done/dead＝0** ⇒ ⑨ 席 02–08 班的判卷台账与信箱件 git 落点连续第三班为零，磁盘可见纯靠主区工作树。本席**未回滚、未代修、未 requeue 他人袋**（属 ⑩ 串行写域与属主班），只呈交事实 | 复跑＝本班正文尺（`glob` 四态目录＋`blob_sha256` 前缀 16 位对表）＋`python scripts/commit_queue.py status` |

**净零声明**：本班新开单号仅 `修⑫` 一条，且不可被在册单替代——修⑥＝`ic_ir_min` 柱"该声明的没声明"（申报腿），修⑨＝净/成本面未产（产数腿），修⑪＝跨 card_id 同读数（绑定回落），三者对象均非"桶字段申报值≠实际值／卡面冻结闸零消费／影子腿零产出"这三形；`修⑫` 的三形同属"卡面冻结字段与执行器机判面的申报-消费一致性"一病，故**并为一条、不拆三号**。在册 `修⑩` 仍悬空（07 班在册：引用 1 次、无定义），本席未补写。呈批在册定义现止于 P-5，本班新 **P-6**（见 §2）。

### 2 呈批草稿（本班新 1 条；判据问题，本席一律不自改）

| 日期 | 类型 | 题 | 两选项与代价 | 不点会怎样 | 路由建议 |
|---|---|---|---|---|---|
| 2026-10-15 | 呈批 **P-6** | **有符号门柱把"反向稳定"与"零信息"洗成同一个 fail**（记账/观测面问题，**不动任何阈值、不改任何 verdict**） | rows[87] `TDM-E-L2/ablation/02_板块候选池整体边际` 实测 `mono_spearman −0.758`（镜像阈 −0.6 已过线）、`ic_mean −0.0605`、`oos_ic −0.0740` 与 IS **同号**、bear/rebound 两段 **同号**＝5 根柱里 2 根因"方向与卡面假设相反"而败、3 根（ic_ir 无面／regime／oos）**过**，verdict=fail。而 rows[86] `mono −0.103` 属"信息量近零"，两行在册同形（都写作 `mono_spearman … < 0.6`）。选项 A＝分数行加一列纯观测标签（如 `mirror_shape`，判据＝`mono<=−0.6 且 regime/oos 同号`，由写分工具机械导出，不进 fails、存量行不回填），代价＝写分工具加一腿＋需 ⑤ 席排期；选项 B＝不加列，由本席每班日报点"镜像簇"名单（本班实测全册该簇＝**1 行／88 fail＝1.1%**），代价＝跨席不可机读、每班多一次量测、且随批漂移 | ③④席无法按标签检索"信息存在但方向与假设相反"的对象，只能靠本席每班人工点名；更险的一面＝**事后翻方向重挖**＝数据挖掘，现无任何在册通道把它与" preregistered 反向新卡"区分开。本席不自裁（铁律：判据问题只呈批不代裁；翻方向属 ⑥ 席看数前冻结的注册动作） | Owner＋⑩ 线长。若裁"另立反向卡"，请 ⑥ 席按 `TDM-E-L2/ablation/02` 的反号命题 preregistered 新卡（看数前冻结窗与柱），本席不在分数册侧做任何方向改写 |

### 3 [对照] 申请单（→⑥制卡席）

- 本班**零新开**：6 行里 4 行死因是"IS 方向/强度双不足"（rows[85]/[86]/[88] 与 rows[84]），1 行是"毛过净不过"（rows[89]，属修⑨ 面），1 行是"反向稳定"（rows[87]，属 P-6 题面）——四者都不是"只栽 OOS 一根柱"的形态，故不满足在册 [对照] 单的前置（04/06 班口径：只切 OOS 窗单变量）。⚠ 在册未销的 [对照] 扩面（06 班点名的 rows[8]/[75]/[77]/[79]）本席**不重复派**，仍等 ⑥ 席并批。

### 4 本班未做与理由（防下一班重烧）

- 未复跑 `census6_materiality.py`（06 班在册轮次直方图 `{1:52,2:7,3:3,4:2}` 属禁烧面；本班只在 90 行面另测新直方图，见迭代史节，不复用旧尺）。
- 未复测 `factor_signal`/`factor_feature_value` 零行面（三度同值在册）与 15 员池 PR（正解口径已在册，见 pulse 件）。
- 未查 ⑤ 席在途工作区改动意图（非本席写域），只登记"工作区面该腿 0 命中／HEAD 面 4 处命中"两态事实。


## 2026-10-15 ｜ st-qoder-p09-1015-10（⑨成绩官第十班：当日增量＝4 行全判；主产出＝**对照族"OOS 从未判过"路级根因＋新单 修⑬＋修⑧ 追加面＋呈批 P-7＋[对照] 1 条**）

> **读面声明（本班正文原样跑）**：判卷锚点＝快照 `.runtime/tmp/st-qoder-p09-1015-10/score_snapshot.yaml`（磁盘面 sha256 `d8a6fd8d52f749cecf73c8f02e931d936df020702bfc548bfb97778476cbf949`／129267B／docs=2／doc1 rows=**93**／mtime `2026-10-15 15:13:49`，较 09 班终报锚点 `009c7bbcf87582c2…`／123768B／90 行＝增量 3 行 rows[90..92]）。**本班写作期间册又长**：现值 `b0c9a370fcfc5b080c0b4171…`／130320B／rows=**94**／mtime `15:41:28`（第二快照 `score_snapshot_1542.yaml`）⇒ 本班追加判 rows[93]，**实判 4 行**。index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`009c7bbcf87582c2…`／rows=**90**（09 班磁盘终面已被吸收入 index）；HEAD 面该馆 `git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**。本班未动分数册任何字节、未动任何阈值与门柱。

### 1 修改单（本班新开 1 条，净零声明见本节末）

| 日期 | 单号 | 对象 | 实测与请修方向 | 复跑凭据 |
|---|---|---|---|---|
| 2026-10-15 | **修⑬**（新） | 写分工具·**双臂配对面的 NaN 因果与披露未分账**（三形并一条，同属一病；记账/观测面，**不动任何阈值、不改任何 verdict**） | **形一（文案断言了码面未确定的因）**＝`scripts/backtest/fexam/calibration_exam.py:226` `oos_ic = _spearman(...) if len(m) >= 60 else float("nan")` 与 `:97-98` `if s.std()==0 or t.std()==0: return nan` **两因同值**（样本不足／信号恒常数），加上 `:222-224` `oos = card.get("oos_window_ref") or []` + `if len(oos)==2` 是**第三因**（卡面根本没申报窗）；三条路产出的都是同一个 NaN，而 fails 串固定写「oos_sign_flip ic_delta nan（**配对 IC 面样本不足**）」。**实测铁证**＝rows[17] 卡 `TDM-X-S1-02/comparison/02_dualwindow` 卡体 `oos_window_ref=null` 且 `window.oos=null`（本班卡体直读，非推断）⇒ 该行 fail 串的"样本不足"与实际因不符。 **形二（记败却不披露）**＝`:364` `if "oos_same_sign" in p and m.get("oos_ic") != m.get("oos_ic")` 只在 metrics 有 `oos_ic` 键时成立；双臂路的配对 metrics 面**没有** `oos_ic` 键（只有 `ic_delta_oos`，见 `:568-578`），`None != None` 为假 ⇒ `numeric_keys_no_machine_face` 在双臂路**永不登记**。实测 7 行（rows[66]/[67]/[68]/[69]/[70]/[71]/[92]）`no_machine_face={}` 且唯一 fail 就是 oos 无面，违该函数自己 docstring `:350`「禁静默跳」与 `:324` 裁定③注「缺注入即显式记败…禁静默跳」。 **形三（同行两面互斥＋潜在假绿）**＝甲案附加规则①（卡 07 `exam_scope_note_ruling_jia`）要求凭据带 `not_judged_pillars`，而 rows[92] 载的是 `arm_pillars_owned_by_other_run`（`:637` 产出）**同时** `numeric_keys_not_read=[]` ⇒ 一行内"无未读键"与"两柱本跑不判"并存，读卡人无法机械判定本跑实际判了几根柱（本班尺实数＝**6 根**，含甲案两跑分配里未点名的 `cost_tier_bp_required`，执行器 `:619-621` 无条件评它）。另 `:973` `oos_ok = (m.get("oos_ic") == m.get("oos_ic")) and not any("oos" in f ...)` 在双臂路是**键缺席即判真**（`None == None` 恒 True），现值只靠 fail 串里含 "oos" 才碰巧为假 ⇒ 本班实测 10/10 行 oos_ok=false（**尚无活体假绿，属潜在**）。请修＝①双臂路 `no_machine_face` 腿改键在 `ic_delta_oos` 上并分账三因（把 OOS 段 `len(m)`／两侧 `std()` 随册披露）；②凭据字段名与甲案对齐（`not_judged_pillars`），并使 `numeric_keys_not_read` 与本跑实际柱集一致；③`oos_ok` 的 NaN 判据改显式 `isinstance` 谓词，禁靠键缺席 | 复跑＝`python .runtime/tmp/st-qoder-p09-1015-10/replay10_dualarm.py 0 92`（PROBLEMS 0＝10 行 verdict 与 fail 集全再现）；卡体窗申报＝同尺对 rows[90]/[91] 打印的 `card oos_window_ref` 行；`_spearman` 常数面探针＝本班实测 `constant vs varying -> nan`、`varying vs varying -> 1.0`（纯数值零数据） |

### 2 修⑧ 追加面（在册单追加，非新号；落地面新态，不重烧机制定性）

| 日期 | 对象 | 本班实测 | 与 09 班在册的关系 |
|---|---|---|---|
| 2026-10-15 | **产分侧代码件未入库**＝blocked 行的真实成因 receipts | `git status --porcelain scripts/backtest/fexam/comparison_exam.py scripts/backtest/fexam/exit_sim/exit_simulator.py scripts/backtest/fexam/card_binding.py` 实读＝**`??` comparison_exam.py**（对照/消融族驱动器**整件未跟踪**，即产 rows[90..92] 的那件工具不在 git）；**` M` exit_simulator.py**（磁盘面 `:70-74` 已把 `SCORES_YAML` 指向 `docs/04_research_records/backtest/scores/2026/indicator_exam_scores_v1.yaml` 并注「旧 docs/_working/fexam/ 整目录已删；2026-10-15 OD-1 冒烟实测旧路径 FileNotFoundError 堵双臂底座」，而 `git show HEAD:` 面 **`SCORES_YAML` 零命中**、旧 `_working/fexam` 形态 4 处命中）；**`MM` card_binding.py**（他会话在途，本席未碰） | 修⑧ 在册定性＝**分数册三面分叉**（本席未重烧）；本条对象＝**代码面同型分叉**（磁盘已修／HEAD 落后／驱动器压根未跟踪），是"任一从 HEAD 起跑的车道会再撞一次 FileNotFoundError"的另一半。禁按条数估，两册两条各归各的落地动作 |
| 2026-10-15 | 旧路径件的**真所在**（本班第一轮误读已更正，旧案留卷） | 主树两面＝旧路径 `docs/_working/fexam/indicator_exam_scores_v1.yaml` **MISSING**（`docs/_working/fexam/` 整目录不存在）、新路径同名片段 **EXISTS**（262360B／mtime `2026-10-15 03:09:08`）。⚠ 本班第一次把 `ls`+`find`+`git ls-files` 用 `&&` 串成一条，**首段 `ls` 失败即短路，后两段从未执行**，零输出被本席误读成"`find` 假阴性"；改为分面直读后实测＝`find docs -name "*_exam_scores_v1.yaml"` **5 枚全命中**，且 `find . -name "*indicator_exam_scores*"` 在 **`.aidrafts/<各班会话>/docs/_working/fexam/indicator_exam_scores_v1.yaml` 多枚命中** ⇒ 旧路径的件**只活在 `.aidrafts` 车道草稿树**（主树那份随 10-14 搬迁删除）。请修方向＝①车道草稿树里的旧册是第二真源风险（从 `.aidrafts` 面起跑的跑法能读到与主树不同代的册），请 ⑤/⑩ 席判是否清账；②**取证纪律**＝存在性判定禁把多面命令用 `&&` 串，零输出≠测得零命中 | 三面读数各附谓词：主树 MISSING／新路径 EXISTS（`ls`+`stat` 直读）／`.aidrafts` 命中清单＝`find . -path ./.git -prune -o -name "*indicator_exam_scores*" -print`（后台跑完的原始输出，本班已回读） |

### 3 呈批草稿（本班新 1 条；判据口径问题，本席一律不自改）

| 日期 | 单号 | 题面 | 实测与选项代价 | 本席立场 |
|---|---|---|---|---|
| 2026-10-15 | 呈批 **P-7** | **「无机器面」该记 fail 还是记 blocked/未判——同册两形并存，且两形后果不同**（记账口径，**不动阈值、不改 verdict**） | 同册实测两形并存＝①**校准路**把无面登记进 `unjudged.numeric_keys_no_machine_face` 且**不进 fails**（rows[89] 的 `ic_ir_min`、rows[93] 的 `mono_spearman_min`，本席尺复现其 verdict 均不含该柱）；②**双臂路**把无面直接记成 fail 且**不登记**（rows[66]/[67]/[68]/[69]/[70]/[71]/[92] 共 7 行，唯一败根就是 `ic_delta_oos` NaN）。后果差＝`fail` 按铁律**永不升级 verified**、进"信号无效"分母；`blocked` 按卡注「双腿装载不出=如实记 blocked（禁编造指标）；卡面不翻 examined；试次零消费不记账」可重投且不翻卡。选项 A＝双臂路无面改记 blocked 并入 unjudged（代价＝分数册新增形态，⑦⑧写分工具与 ⑩汇总分母要跟，且 10 行历史行须留旧案不回填）；选项 B＝保留 fail 但强制登记 `no_machine_face`（代价＝"考不了"仍占 fail 分母，本席每班须人工点名，同 P-6 的人工替代面成本）；选项 C＝先只修文案（把"配对 IC 面样本不足"改成分因描述，属修⑬ 形一），口径待 OOS 面真出数后再裁（代价＝分母仍失真一期） | 本席不自裁：A/B/C 都不在写域。本席按现口径判卷并如实点名 7 行，**禁 ③④ 席据此读成信号无效**（见 `to_miners.md` 本班节首条路由更正） |

### 4 [对照] 申请单（→⑥制卡席，标 [对照]）

| 日期 | 对象 | 对照设计（单变量） | 正/负对照与判据 |
|---|---|---|---|
| 2026-10-15 | **[对照]** 卡 `TDM-X-R1-01/comparison/07_熔断五级梯度减仓对照_五态仓位锚定版` 的 OOS 配面无读数 | 同卡、同冻结窗（`oos_window_ref=[2025-10-09, 2026-09-30]`，卡面逐字未动）、同臂档，**唯一改动＝随册披露探针**：OOS 段 `len(m)`、`sig`/`tgt` 两侧 `std()`、级别序列在 OOS 段是否整段驻留 `0.0`（该近似在册＝卡面 `approximations_disclosed` 的「L4-不可解除」原文「一旦进 KILL 即整窗驻留 0.0」）。**禁动任何阈值与窗** | 三因分账判据（本班尺实数）：`len(m)<60` ⇒ 样本因；`len(m)>=60 且某侧 std()=0` ⇒ 恒常数因（`_spearman` `:97-98` 实测返回 nan）；两者皆非而仍 NaN ⇒ 对齐/类型因。**旁证形制**＝rows[92] 的 `regime_ic` 呈 bull 有值／**bear=NaN**／crisis 有值／OOS=NaN 四角形，与"KILL 于熊段首现后整段驻留"同向，但本席**未证为真**（`base_downgrades=1`、`signal_turnover_daily=0.1598` 两面互斥未解，属待验），故只作探针指向。**负对照**＝对 `TDM-X-S1-02/comparison/02_dualwindow`（卡面 `oos_window_ref=null`）同跑一次，若披露面能显式区分"卡面未申报窗"即修⑬ 形一得证 |

**净零声明**：本班新开单号仅 `修⑬` 一条＋呈批 `P-7` 一条，均不可并进在册单——`修⑥`＝`ic_ir_min` 柱申报腿、`修⑨`＝净/成本产数腿、`修⑪`＝跨 card_id 绑定回落、`修⑫`＝桶字段申报-消费三形，四者对象均非"配对面 NaN 三因未分账／双臂无面披露腿键错／`oos_ok` 靠键缺席判真"；`修⑧` 的新态按**追加面**记（同真源＝三面分叉，代码面与册面各一条，不另三号）；`P-6` 是"有符号柱把反向稳定与零信息洗成同一 fail"，`P-7` 是"无面与读数不过洗成同一 fail"，两题面同族不同对象，禁并号。在册 `修⑩` 仍悬空（引用 1 次、无定义），本席未补写。

### 5 本班未做与理由（防下一班重烧）

- 未复测 15 员池 PR 与 `factor_signal`/`factor_feature_value`（05/06 班在册三度同值＝各 0 行，07/08/09 班在册禁烧面条款沿用）。
- 未重跑 rows[76]/[78] 两腿读数（09 班在册禁烧面：`ic_ir` 无面＋净面全 NaN＋`rt=nan`；本班册面 sha 虽变，但 only-add 语义下两行字节不动，本班未逐字节复量该行）。
- 未复量 rows[73]/[74]/[83] 三行的 ic_ir 判定细节以外的面（本班只直测：全册 94 行 `ic_ir` 有实数＝**4 行**＝rows[73]/[74]/[83]/[93]，且**4/4 全记 ic_ir FAIL、0 次过线**；该"有面即败、无第二态"形制属结构性观察，见台账 §2）。
- 未碰 `card_binding.py`（`MM` 他会话在途）与任何 ⑤ 席写域；未 requeue、未代修落地面。

## 2026-10-15 16:1x ｜ ④席 p04-06（st-qoder-p04-1015-06）改良情报 6 条

1. **[情报·可直接用]** 波动率期限结构的业界主口径是**比率**不是差值，且有可回查的数值带：VX1/spot 正常升水带 1.04–1.08、上穿 1.00 即 backwardation、>1.10 为深贴水（三独立命中：thetrading.tools／eco3min／TradingView 脚本页）。对本库的直接含义＝**同一张表上「水平已占、斜率未占」是可复现分割**：本班实测 vollvl_20（波动水平）对池 reject max|corr|=0.6465（撞 ti_ew_garman_klass_20_v1），slope_5_60（同列构造的比值形）pass 0.2771 ⇒ ⑥ 制卡时这对读数是「该轴增量存在」的最省成本证据。
2. **[情报·未造腿]** TradingView 命中给了一条时序条件：深贴水（backwardation）之后**须等比率自身回落（diff 变号）才翻转状态**，原文『ONLY after the ratio begins to roll over——don't sell into a rising backwardation spike』。本班**未造该事件腿**，登记给 ⑤ 席做门控状态机时引用；水平值臂与事件腿禁合并报数。
3. **[修·贴柱族第三证]** 本班 slope_5_60 余量 **0.0229**（在册先例：卡12 erp 余量 0.0307、cape_5y_pct 超柱 0.0016）。三条同族读数都落在「市场级 vs 市场级」面上 ⇒ 0.3 门柱在该面的分辨率已接近噪声量级。**本席不动门柱**，只登记第三次同型；建议 ⑥ 对该面改用「换窗/换面复核一次」作前置，而非只看一次 pass。
4. **[修·实现面缺陷候选]** 本库 `c1_market.dragon_tiger_seat.seat_type` 值域是**英文** broker／institution／connect，与交易所披露文案的「机构专用」不一致。本班首版按中文谓词做 sumIf 得到**全 0 伪读数**（不是「当日无机构席位」，是谓词永不命中），重跑才更正。凡按席位身份筛/拆分的实现，接线前必须先 `GROUP BY seat_type` 读值域——本席把该坑写进卡15 pseudocode 首行注释。
5. **[情报·替代供数面]** 北向腿的日频替代面：`c1_market.northbound_hold_snapshot` 实测只有 **8 个不同日期跨 21 个月**（max=2026-06-30，且无 symbol 列、只有 ts_code），而 `dragon_tiger_seat` 的 connect 臂有 21023 行**日频**记录 ⇒ 若 ① 席要补「北向资金」轴，龙虎榜陆股通席位是现成原料。本席只登记原料存在性，**不判两口径可否互换**（覆盖宇宙与频率都不同）。
6. **[通道实测·诚实面]** arXiv export API 可用（正对照 cat:q-fin.PM=3 条、负对照乱词=0＋原文 No matches found，故「龙虎榜/dragon tiger 主题 0 命中」为真稀疏非故障）；**Semantic Scholar graph API 两次均 HTTP=429**（原文『Too Many Requests. Please apply for a key』）⇒ 本班学术锚只到「题目＋合著者＋刊名」面（取自学者主页论文列表），**年份卷期未核**，⑥ 制卡冻结前须回查原刊，禁把本班引用当已核文献。

## 2026-10-15 16:5x ｜ st-qoder-p09-1015-11（⑨成绩官第十一班：当日增量＝**2 行**全判；主产出＝新单 **修⑭**＋**修⑮**＋呈批 **P-8**＋〔对照〕1 条＋**修⑧ 追加面（回退弹出局·现值无载体袋）**）

> **读面声明**（本班正文原样跑）：分数册磁盘面 sha256=d77773545f5b4cc7…／132248B／docs=2／rows=**96**／mtime `2026-10-15 16:28:53`；本班 16:11:36 进场锚点＝`8903ef9e9c731fdc…`／131320B／rows=95 ⇒ **本班为在册第二次"一班之内册面两代"**（首现＝10 班 93→94），增量按终面取 rows[94]＋rows[95] 两行。index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`009c7bbcf87582c2…`／123768B／rows=**90**（＝09 班磁盘终面已入 index）；HEAD 面 `git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**。旧行零改动实测＝与 10 班快照 `score_snapshot_1542.yaml` 逐行 JSON 对表，rows[0..93] **byte changes=[]**，唯一变化是追加 rows[94]、rows[95]。族口径＝卡体 `pillars_numeric` 键集，卡体 join＝卡内 `card_id`（**96/96 命中**，卡池 550 件）。本班未动分数册字节、未动任何阈值与门柱。
> 判卷尺＝`python .runtime/tmp/st-qoder-p09-1015-10/replay10_calib.py 94 94` 与 `… 95 95` ⇒ 两行 verdict **全再现**，PROBLEMS 0／0；双臂路自检＝`replay10_dualarm.py 90 93` PROBLEMS **0**。

### 1 修改单（本班新开 2 条，净零声明见本节末）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 修改单 **修⑭** | 执行器·**panel 路的 `mono_spearman` 生产腿硬编缺失**（申报/消费腿，**零阈值改动**） | `scripts/backtest/fexam/calibration_exam.py:268` `_panel_metrics` 返回体里 `"mono_spearman": None` 是**字面常量**，而 panel 路 `:272` 同时返回 `"bucket_medians": None`＝分桶响应面从未计算。后果＝凡 `signal_kind: panel` 的卡，其 `pillars_numeric.mono_spearman_min` **永不可判**。册面实测（96 行）＝panel 路且冻该柱的行 **6 行＝rows[73]/[74]/[83]/[93]/[94]/[95]**，`metrics.mono_spearman` 6/6 为 None，6/6 verdict=fail。⚠ 本班的两行新件恰都落在此簇：rows[94] 卡体 `hypothesis` 原文"**假设其对次日收益单调负（越冲高越弱）**"、`pillars.response_monotonicity` 原文"\|Spearman rho\| >= 0.6"＝**该卡命题本体就是单调性，而唯一能判它的柱子在 panel 路恒不出数**；rows[95] 同形。申报腿本身是做对的（6/6 都如实挂进 `unjudged.numeric_keys_no_machine_face`，措辞"panel 路恒 None／分桶样本不足 NaN"），欠的是**生产腿**。请修＝panel 路补分桶响应（或显式在卡模板面禁止 panel 卡冻 mono 柱，属 ⑥ 席制卡面）；**禁为凑数用其它统计量替该柱出数**。本席不判该柱无效，只报"6/6 恒无面且 6/6 落在这批新 fail 上" | 行级＝`python .runtime/tmp/st-qoder-p09-1015-11/census11_final.py`（panel 簇清单＋join 96/96）；码面＝`sed -n '249,273p' scripts/backtest/fexam/calibration_exam.py`；卡面命题＝`grep -n "单调负" docs/03_modules/_domain_backtest/exam_cards/position_flow/P2/TDM-P-P2-04__calibration__07_*.yaml` |
| 2026-10-15 | 修改单 **修⑮** | 执行器·**`ic_mean` 是"全窗（含 OOS）"量，却被 `oos_same_sign` 当 IS 参照，且 fails 串把它标成 `is=`**（口径/披露腿，**零阈值改动、零 verdict 改写**） | **机制**＝两条路都把整段序列直接汇总、从不按卡面 `window.in_sample` 切片：series 路 `calibration_exam.py:214-215` `aligned=pd.concat(...).dropna()` → `ic_ts=_spearman(aligned…)`，`:235` 原样作 `"ic_mean"` 进册；panel 路 `:251-252` `ic=fast_rank_ic(...)`→`st=ic_stats(ic)`，`:264` 取 `st["ic_mean"]`。而 `oos_ic` 是在**同一枚全窗对象**上切出 OOS 段（`:225-226`／`:261-262`），`oos_same_sign` 柱比的就是"OOS 段 vs 含 OOS 段的全窗" ⇒ 该柱**不是样本外检验**。fails 串更把参照量写成 `is=`（`:226`／`:626` 输出形如 `oos_sign_flip oos=… is=…`），字面宣称 in-sample。**实测铁证（本席直读 CH，正对照 `SELECT 1`→`[(1,)]`）**＝`c1_market.kline_daily_hfq` 的 `count(DISTINCT trade_date)`：IS `2019-01-04..2023-12-31`=**1212**、OOS `2024-01-01..2026-09-30`=**666**、并集=**1878**；而 rows[94]/[93]（同卡族、同冻结窗）册面 `metrics.n`=**1859** ⇒ 覆盖的是全窗而非 IS，OOS 段占该参照量的 **666/1859≈35.8%**。**材料度（96 行面）**＝冻 `oos_same_sign` 柱 **73 行**；两侧皆实数（该柱真咬合）**61 行**；fails 串含 oos **40 行**；该柱走 `no_machine_face` 披露 **0 行**。⚠ 占比逐卡不同（rows[76]/[78] 卡面 OOS＝`2026-04-03..2026-10-12`＝在册 126 日扣留面，占 n=1846 约 6.8%）⇒ 同一根柱在不同卡上"独立性"强度差 5 倍，账面看不出。请修＝`ic_mean` 按卡面 `window.in_sample` 切片（全窗读数可另设键保留，禁删旧披露）；fails 串的 `is=` 与实际窗一致后才可用该标签。**本席不自修、不改任何 verdict，且如实声明：本班两行 fail 的定性不受此单影响**（两行各有 `ic_mean`/`ic_ir` 两根**实数**败柱独立成立） | 复跑＝`python .runtime/tmp/st-qoder-p09-1015-11/probe11_oos_materiality.py`＋`probe11b_oos_passface.py`；CH 计数＝`DatabaseService().get_clickhouse_conn()` 三条 BETWEEN 查询（本班正文读数）；卡面窗＝`grep -n "in_sample\|oos_window_ref" docs/03_modules/_domain_backtest/exam_cards/position_flow/P2/TDM-P-P2-04__calibration__07_*.yaml` |
| 2026-10-15 | **〔对照〕**（给 ⑥ 席） | 卡 `TDM-P-P2-04/calibration/07_冲高反弹幅度对次日收益与减半阈值落点`（＋姊妹卡 06）的 **IS 段单变量对照** | 同卡、同冻结窗（卡面 `window` 与 `oos_window_ref` 逐字不动）、同绑定、同桶面，**唯一改动＝读数只取 `in_sample` 段（1212 交易日面）重算 `ic_mean`/`ic_ir`**，并随册披露两侧（IS-only 与全窗）。**禁动任何阈值与窗**。判别用途＝若 IS-only 读数与全窗同号且同侧过柱 ⇒ rows[94] 的 fail 定性不依赖 修⑮；若异号或一侧过柱 ⇒ 修⑮ 有活体后果，须先于任何复考落地。本席按铁律不跑考试 | 指向＝修⑮ 正文的机制行号与 CH 三值；对照基线读数＝册面 rows[94] `ic_mean −0.0271`／`ic_ir −0.1357`／`oos_ic −0.0250`／`n 1859` |
| 2026-10-15 | 呈批 **P-8** | **单卡内"散文柱声明反向计分"与"机器柱带符号正下限"互斥 ⇒ 该卡在其自身假设成立时必败**（判据口径，**本席不动阈值、不改 verdict**） | rows[94] 卡体三处原文同读＝①`hypothesis`"本卡只考①：…**假设其对次日收益单调负（越冲高越弱）**"；②`pillars.response_monotonicity`"\|Spearman rho\| >= 0.6；符号约定=冲高越强次日越弱，**反向同号同样计分**但须在结论里写明\"限额方向被证伪\"（G4-5）"；③`pillars_numeric`=`{mono_spearman_min: 0.6, ic_mean_min: 0.02, ic_ir_min: 0.3, regime_same_sign: true, oos_same_sign: true}`（**全是带符号正下限/绝对值正下限**）。⇒ 三态合起来＝**只有当该卡假设被证伪（IC 为正）时 pass 面才可达；假设成立（IC 为负，实测 IS/OOS/牛熊三处同号负）必记 fail**；且散文要求的"须在结论里写明证伪"在分数行**无任何承载字段**（册面只有 `fails` 串与 `unjudged` 两键，本班实测）。材料度（精确谓词、非关键词粗筛）＝全卡池 550 件里明文含"反向同号／同样计分／符号约定"三词的卡＝**恰 1 件**（就是本卡，`grep -rl` 逐词三查一致）；另：全册"三处同号负向"形态＝**10 行／7 张卡**（rows[29]/[30]/[33]/[34]/[73]/[74]/[87]/[88]/[94]/[95]，谓词＝`ic_mean<0 且 oos_ic<0 且 regime_ic 有效段全负`），其中仅 1 张卡散文授权反向计分，其余 6 张未声明 ⇒ **同一形态在不同卡上被读成"证伪方向"还是"信号无效"没有在册分账**。选项 A＝按卡面声明方向取绝对值评 `ic_mean_min`/`mono_spearman_min`（**＝改判据，须 Owner 签**，代价＝历史 96 行不可比、须新行 only-add 留旧案）；选项 B＝由写分工具加一列纯观测标签（如 `direction_confirmed`／`falsified_direction`，不进 fails，代价＝与 **P-6 选项 A** 同族、需 ⑤ 席排期，请合并排期勿开两次工）；选项 C＝由 ⑥ 席按反号命题 preregistered 新卡（代价＝该限额 RLM-POSITION-011 的"方向已证"结论仍无处落，且同对象两卡并存的试次记账要一并裁）。**本席不自裁**：A/B/C 均不在写域；按现口径判卷，rows[94] 维持 fail 一字未动 | 卡体逐字＝`python -c` 读 `pillars`/`pillars_numeric`/`hypothesis`（本班正文）；三词精确 grep＝本班正文（各 1 命中、同一路径）；簇计数尺＝`python .runtime/tmp/st-qoder-p09-1015-11/probe11_polarity.py` |
| 2026-10-15 | **修⑧ 追加面**（在册单追加，**非新单号**） | 落地链·分数馆**回退弹出局，但风险换成"现值无载体袋"**＋**本席袋四态换代** | ①**回退弹出局**＝携带分数馆旧面的 `st-scorehome-20261014-0001..0007` 现**全部在 dead**（死因三分族：`-0001` 门 `REGISTRY-MASS-DELETION` 拦、`-0002` 门 `TAKEOVER-PENDING` 拦、`-0003/-0004/-0005/-0006/-0007` `ghost_session` 属主 `st-scorehome-20261014` 已死被存活闸拒（裁定#459））；全 pending 面现仅 **1 袋**＝`q-20261015-st-qoder-p07-1015-04-0003`（1 件，**不载** `docs/04_research_records/backtest/scores/`）⇒ 07/08/09/10 班在册的"任一旧袋先落地即洗掉新行"威胁**由死信终结，而非由落地解决**。②**新态势**＝分数册现值（磁盘 rows=96）**无任何在途载体袋**，HEAD 该馆 **0 件**，index 落后磁盘 **6 行／8480B** ⇒ 唯一存活处＝主区工作树，属第六态而非已交付。③**本席四态换代**＝`*p09*` 袋现 **17 dead ＋ 1 done**（`q-20261015-st-qoder-p09-1015-09-0002`，7 件，本席今日**首次真落地**）⇒ 09 班在册"15 只全 pending、done/dead=0"与 10 班同题句均已被 drain 覆盖。死因二族＝`ghost_session`（属主会话判死→自动重投被存活闸拒）×**9**（02 班 1／03 班 2／06 班 2／07 班 3／10 班 1）＋`landing 异常: RuntimeError: [landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）: docs/_working/automation_…`×**8**（08 班 0001–0004、09 班 0001 等）。⚠ 后者与本席七件热件的 `MM` 态同源：本班实测七件全部 **HEAD 有件、磁盘比 HEAD 大 3036–14662B**（`git cat-file -s HEAD:<件>` vs `os.path.getsize`），即袋=磁盘快照必然含**他席未落地条目**＝双侧皆改的结构性成因。**本班未 requeue、未代修**（requeue 前须读 dead_reason 修因，而"活袋投出即随收班而死"的循环要 ⑩/统筹定方：建议＝本岗交付改"当班活会话＋收班前 drain"或改由 ⑦⑧ 写分席同袋带出，不属本席自裁面） | 死袋枚举＝`ls .runtime/commit_queue/dead/*p09*.json \| wc -l`＝17、`ls .runtime/commit_queue/done/*p09*.json`＝1；逐袋 `dead_reason` 聚合尺＝本班正文内联脚本；pending 单件面＝`.runtime/commit_queue/pending/`（1 枚）；七件 `MM` 与 Δ 字节＝本班正文读数；在册旧面＝`to_impl.md` 07/08/09/10 班"修⑧"各节 |

**净零声明**：本班新开单号＝`修⑭`＋`修⑮` 两条＋呈批 `P-8` 一条，均不可并入在册单——`修⑥`＝`ic_ir_min` 柱**申报腿**（本班两行的 `ic_ir` 都有实数并参与否决，非该单对象）；`修⑫` 形二＝`buckets.min_obs_per_bucket` **零读取**（装饰性闸），形三＝PE 影子披露腿零产出，均非"panel 路 mono 生产腿硬编 None"（修⑭）或"`ic_mean` 窗切片与 `is=` 标签名实不符"（修⑮）；`修⑬` 形二讲的是**双臂路** `no_machine_face` 键错，本班两行走**校准路**且披露腿正确，故不并；`修⑨`＝净/成本产数腿，`修⑪`＝跨 card_id 绑定回落。两新单同属"执行器机判面与卡面冻结语义不同源"一病但**对象不同柱、修法不同腿**，分列不并；呈批面 `P-6`＝全册缺"反向稳定"观测标签（记账），`P-8`＝**单卡内散文与机器柱极性互斥＋散文柱无落点**（判据可达性），题面同族不同对象，**禁并号**。在册单号现止于 `修⑮`／`P-8`；`修⑩` 仍悬空（引用 1 次、无定义，本席未补写）。

### 2 本班零新开缺数单（口径声明）

rows[94]/[95] 两行的 `ic_mean`/`ic_ir`/`oos_ic`/`regime_ic`/`n` 五面皆实数，无"因缺源而考不了"形态；在册缺②（`c1_market.suspend` 考试窗内零行）与 `factor_signal`/`factor_feature_value` 各 0 行均属三度同值**禁烧面**，本班未重烧、未重复开单。


## 2026-10-15 ｜ st-qoder-p09-1015-13（⑨成绩官第十三班：当日增量＝**0 行**；主产出＝**事件族 OOS 确认柱可达性**＋新单 **修⑯**＋呈批 **P-9**＋**修⑫ 追加面**＋本班假红自纠）

> **读面声明**（本班正文原样跑，终报前重测）：分数册磁盘面 sha256=d77773545f5b4cc7c8c64686a8aab8e2c672a540740e843da953f4e3186d0c9c／132248B／docs=2／rows=96／mtime `2026-10-15 16:28:53`＝与 12 班终报锚点逐位同 ⇒ **增量 0 行**；index＝`009c7bbcf87582c2…`／90 行；HEAD 该馆 0 件。本班未动分数册字节、未动任何阈值与门柱；尺＝`.runtime/tmp/st-qoder-p09-1015-13/measure13*.py`（全只读）。

### 1 修改单与呈批（本班新开 2 条，净零声明见本节末）

| 日期 | 类型 | 对象 | 内容摘要 | 依据（可 grep／可复跑） |
|---|---|---|---|---|
| 2026-10-15 | 呈批 **P-9** | 判据可达性·**事件族"OOS 同号确认"柱＝floor(200 事件日) 套在 410 交易日 OOS 窗上，实测 0/23 行可达**（**本席不动阈值、不改 verdict、不代拍**） | 码面＝`scripts/backtest/fexam/calibration_exam.py:843`（`floor = max(200, 卡面 event_days_min)`，卡面往松不采）＋`:872-875`（OOS 窗套**同一下限**）＋`:877-881`（反号判定仅在 `oos_n >= floor` 分支执行）⇒ 两分支互斥，窗下限未过时符号检验**永不运行**；该规则由 commit `ed5e59c2890`（2026-10-11 04:42:19）引入，其 message 自陈"本轮单向收紧一处……只增 fail 不增 pass"。册面直测＝事件族 23 行（rows[41..43]/[46..65]）卡面 `event_days_min` 分账 `{200: 23}`；`metrics.windows` 唯一形（23/23）＝IS `2019-01-04..2023-12-31`／OOS `2024-01-01..2025-09-09`；OOS 面总日数 `n_event+n_none`=**410**；`oos.n_event` **79–165**（密度 19.3%–40.2%，过线需 **48.8%**）；IS 侧 `n_event` **239–363**、`≥200` 命中 **23/23**。⇒ 同一条 200 下限套 IS 窗（1212 日）要 16.5% 密度、套 OOS 窗（410 日）要 48.8%，**两套难度**；12 班在册"事件族 23 行 0 pass"的原因层＝可达性、非信号弱。<br>**选项与代价（本席不自裁）**：A＝floor 随窗长缩放（**＝改判据，须 Owner 签**；代价＝历史 96 行不可比，须新行 only-add 留旧案）；B＝不动门槛，由 ⑥ 席对确有把握的事件轴 prereg **更长 OOS 窗或更密事件定义**（代价＝同对象多卡并存，试次记账撞在册 **P-5** 题面，请合并排期勿开两次工）；C＝维持现状并把事件族按"结构不可达 pass"记账（代价＝④ 席生成端在该族继续投变体＝零产出挖矿，需据本条改调度）。**本席按现口径判卷，23 行 verdict 一字未动** | 尺＝`python .runtime/tmp/st-qoder-p09-1015-13/measure13d.py`（符号×触发 cross-tab＋窗下限命中分账）；读数存件＝`probe13_event.txt`／`probe13_windows.txt`；码面行号＝`sed -n '843p;872,881p' scripts/backtest/fexam/calibration_exam.py`；规则史＝`git log --format='%h %ad' -S'确认窗同样受族内下限约束' -- scripts/backtest/fexam/calibration_exam.py`（恰 1 命中）；卡面 `window`／`event_days_min`＝`python -c` 读 `docs/03_modules/_domain_backtest/exam_cards/**`（本班正文） |
| 2026-10-15 | 修改单 **修⑯** | 分数行·**"读到的窗面＋判据版本"两枚披露锚缺失**（**纯披露腿，零阈值改动、零 verdict 改写**） | **形一**＝同一族内两代败根并存而册面不可分：rows[41]/[42]/[43]（date `2026-10-11`，卡 `*_high_event_v2`）fails 引 `oos_gap 反号 …`，但三行 `oos.n_event`=104/81/79 **<200**，按现行码面 `:873`／`:877` 互斥分支该 fail **不可能由现行码面产出**；`git log -S'oos_gap 反号'` 与 `-S'确认窗同样受族内下限约束'` **各恰 1 命中且同一条 commit** ⇒ 两串同源于 `ed5e59c2890`，故三行必出自该 commit **生效前的运行码面**（在册"HEAD 已修而运行面读磁盘旧码"案的同族新形）。同族后 20 行的 OOS 侧败根＝窗下限。⇒ 现册面**无任何字段**能区分这两代（只有 `fails` 串与 `unjudged` 两键）。**形二**＝`metrics.windows` 披露面分族＝事件族 **23/23 有**、校准族 **0/61 有**（双臂族同样无面）⇒ 校准族究竟读了哪段 OOS 窗**册面无痕**，跨族／跨卡比较 OOS 只能逐张回卡体，审计不可机械复验。**请修正解（不改判据）**＝写分时把执行器**实际读到的** IS／OOS 窗（含边界日与总日数）＋该次运行所用判据码面锚（commit 或文件 sha256 前缀）两枚**纯观测字段**写入行内，禁进 `fails`、禁参与否决；本班不代改码（属 ⑤ 席写域） | 尺＝`python .runtime/tmp/st-qoder-p09-1015-13/measure13d.py`（`windows` 分族披露面）＋`measure13c.py`（三行字面取证含 `oos.n_event`）；码面互斥分支＝`sed -n '872,881p' scripts/backtest/fexam/calibration_exam.py`；两串同源＝`git log -S` 各恰 1 命中（本班正文）；册面键集＝96 行 `metrics` 键频次分账（`measure13.py` 前置探针正文） |
| 2026-10-15 | **修⑫ 追加面**（在册单追加，**非新单号**） | 执行器·桶面在**同卡复跑间翻动**且**拉动门柱读数**（修⑫ 形一的复跑侧证据，**零阈值改动**） | 尺＝`python .runtime/tmp/st-qoder-p09-1015-13/measure13b.py`／`measure13c.py`。14 张多行卡（38 行，`run_id` 14/14 多值＝全真复跑）四类分账＝读数全同 7／桶数口径变 3／窗变 2／多变体双档剔除 2 ⇒ **"窗同＋桶同＋读数变"＝0**（复跑可再现性本身未被证伪）。但 3 张 L2 卡（`TDM-E-L2-02/03/04-2/calibration/02_*`）在 **`n` 恒同**（1254／1195／1254）下 `n_buckets_used` null→5 且**门柱读数** `mono_spearman` 随之变（`0.0303→−0.10`／`−0.1152→−0.20`／`−0.2242→−0.60`），另 5 张卡复跑后 `n_buckets_used` **10→null**（净/成本披露退化而头柱一字未变）⇒ 修⑫ 形一原写"该字段零消费者、只误导审计"，本班证据显示**桶数口径变会带动 `mono_spearman` 这根在册门柱的读数**，故按追加面入本单（对象＝同一枚桶字段的消费腿，不另立号）；修法方向仍＝改报实际组数或另设 `n_buckets_actual`，**禁动任何阈值** | 逐卡读数＝`measure13c.py` 输出第 2 段（本班存件 `measure13c.out`）；正对照 rows[2]≡rows[10] metrics 逐字相同＝True、负对照 rows[83] 同卡行数＝1（同尺内置）；在册修⑫ 定义＝本文件 09 班节 |

**净零声明**：本班新开单号＝`修⑯` 一条＋呈批 `P-9` 一条，均不可并入在册单——`修⑫`＝桶字段**申报值≠实际值／卡面冻结闸零读取／影子披露腿零产出**三形，本班只按其"消费腿"口径**追加复跑证据**（未另立号）；`修⑬`＝双臂路配对面 NaN 三因未分账＋`no_machine_face` 键错，对象是**双臂族**且不含"窗面／判据版本锚"；`修⑮`＝`ic_mean` 窗切片与 `is=` 标签名实不符（口径腿），非"行内无窗面披露"；`修⑥`＝`ic_ir_min` 柱申报腿；`修⑧`＝落地面分叉。`修⑯` 的对象＝**行级两枚观测锚（实读窗面＋判据码面版本）缺失**，与上述各条**不同腿**，故单列；呈批面 `P-5`＝同读数两卡算不算两次独立考试（试次记账），`P-6`＝缺"反向稳定"观测标签，`P-8`＝单卡内散文柱与机器柱极性互斥，`P-9`＝**门槛×窗长的可达性**（判据物理可达面），四者题面同族而对象各异，**禁并号**。在册 `修⑩` 仍悬空（引用 1 次、无定义），本席未补写。在册单号现止于 `修⑯`／`P-9`。

### 2 本班零新开方向单／缺数单／对照单（口径声明）

- 增量 0 行 ⇒ 无新 fail 可四分诊；S-1 属**判据可达性**（P-9）与**披露腿**（修⑯），不在 ③④ 席或 ① 席写域，本班**不据此判事件族 mined_out**（判死须 ④ 席＋连续负读数，沿 07/12 班口径）。15 员池两表各 0 行、rows[76]/[78] 两腿、`ic_ir` 有实数 6 行、双臂 10 行 OOS 无面＝**在册禁烧面，本班全部未重烧**（双臂面为册面直读复现，非重跑考试）。


## 2026-10-15 ｜ st-qoder-p04-1015-07（④全网战法矿工席第七班：改良情报 6 条，全部带实跑读数）

| 日期 | 类型 | 对象 | 依据（本班可 grep 证据） | 建议动作（本席不出裁定） |
|---|---|---|---|---|
| 2026-10-15 | **负结果（公式版本未定，禁据此开卡）** | Corwin–Schultz 高低价隐含价差（本席 02 班旧卡 SIC-20261015-P04-04 `cs_spread` 同族公式） | 尺=`.runtime/tmp/p04_07_probe/build3.py`（绕注入器＋显式 FINAL，可原样复跑）：按业界流通写法 `β=½[(ln H/L)²_t+(ln H/L)²_{t−1}]`、`γ=(ln(maxH/minL))²`、`α=(√(2β)−√β−√γ)/(3−2√2)`、`α<0 截 0`、`S=2(e^α−1)/(1+e^α)` 在 `c1_market.kline_daily FINAL`（2021-01-05..2026-10-15，HAVING n≥500，**1398 个交易日**）逐日截面均值 ⇒ `spread mean=min=max=**0.0**`＝**全段被截零**。两独立命中（blog.csdn 152387417 与 tandfonline 2024）给的是同一承载形，故不是单源抄错；旁证＝CNKI《基于日高低价的有效价差新矩估计》（系统科学与工程 2019(6)）明文『五个新矩估计在理想与非理想条件下均优于 Corwin and Schultz 的估计器』⇒ 该族确有已知退化面。**本席未能与 JF 原文对表 β 取均值还是和／截零规则，故不给修法** | ⑤/⑥：`cs_spread` 那张 02 班旧卡**禁按现公式物化**（会得到恒零序列＝"查无"伪装成"查空"）；若仍要这条腿，请先取 JF 原文式(5)–(7) 逐字对表，或直接改用 CNKI 那篇的新矩估计／Roll 修正版（Goyenko et al. 2009，本席 frds 面已核到定义域陷阱） |
| 2026-10-15 | **原料可及性实测（解禁一条在册"未做卡"的堵点已解）** | `c3_fundamental.share_unlock` 长史解禁轴＋日内冲击成本腿 | 本班探针实测：share_unlock＝30,304 行／2010-01-04..**2027-10-13**／5,533 票／countIf(ratio>0)=29,839／countIf(amount>0)=30,133／engine=ReplacingMergeTree；未来解禁 countIf(unlock_date>today)=**1,442**（与 06 班在册逐字同）；DESCRIBE 9 列**不含**①席 12 班点名的"解禁后 20 日涨跌幅"后视列 ⇒ 该 PIT 雷在**本库物化面不存在**，只剩 as-of 截断义务。日内腿另有 `c1_market.kline_5min`＝**296,690,486 行／2021-09-01 09:35..2026-10-15 15:00／8,710 票**，12 列（trade_time,symbol,OHLC,volume,amount,data_source,ingest_ts,exchange,symbol_canonical） | ③/⑤：06 班游标⑨b「解禁须先解 as-of 截断口径」的堵点**已可由本库面自证**（本席已出卡17）；Kyle λ（frds 口径 S=Σsign(v)·√\|v\| 的 5 分钟回归）原料史长已够 5 年，本班**未物化**（算力窗），请 ⑤ 排期；kline_5min 无 mid 列 ⇒ 日内口径须先定 (H+L)/2 还是买一卖一 |
| 2026-10-15 | **工具口结构缺陷（采集面通用坑，非本席个案）** | `zephyr.data.ch_reader.query_rows` 的 `inject_final_strict` | 任何带 `WITH ... AS` 的只读 SQL 都会崩：注入器对 FROM/CTE 后每个 token 调 `get_table_engine_strict`，别名 `b/s/e/sp/x/i` 探不到引擎 ⇒ `ClickHouseQueryError: engine_probe: 空返回（未知引擎）`，且 GATE-P0-ENGINE-PROBE 同步打警『空返回与"表不存在"不可分』。本班两枚候选首次因此中断（build2.py 崩在 [B]，[C] 未跑） | ⑩/工具班：建议 query_rows 支持 CTE 名单跳过（或 `--allow-cte` 旗／只对白名单 schema 限定名探引擎）。**本席未改工具**，处方是绕道 `ch_writer.query_strict` 自加 FINAL，已写进两卡伪代码；该绕道要求调用方自己记得 FINAL，属易错面 |
| 2026-10-15 | **在册判定再复证＋新计数** | `system.tables` 的 LIKE/ILIKE 假空 | 首查 `WHERE name ILIKE '%unlock%'` ⇒ `[]`（零命中）；同进程枚举 `database NOT IN ('system','INFORMATION_SCHEMA','information_schema')` 得 253 张后在 Python 侧过滤 ⇒ 命中 `c3_fundamental.share_unlock` 与 `c3_fundamental.restricted_shares` 两枚。⇒ 假空形态在本库**可稳定复现**，非一次性 | ⑩/文档班：把"跨库定位只认等值／禁 LIKE 于 system.tables"升为采集 SOP 硬条目（本席已在卡面 caliber_pitfall 写死） |
| 2026-10-15 | **下游归一器兼容性缺陷（本班普查量出）** | `data/strategy_intake/web_cards/` 卡面 schema | 盘面 17 枚逐件 `safe_load`＋键名普查：第五必备字段（数据源映射）**两代键名并存**＝`data_binding` **4 枚**（06 班卡14/15＋本班卡16/17）与 `data_source_mapping` **12 枚**（01–05 班），旧代另带 `gates/seven_gates_precheck/verification` 三段、新代把闸写进 `data_binding.*_gate_zh`。并集谓词下真缺面=0（本班首版按单键判"10 枚缺第五字段"＝尺族盲假红，已自纠并留旧案） | ⑤/C1：归一与索引生成器须**双键兼容**，否则只认 `data_binding` 会静默漏 12 枚（漏采形态＝看起来无源）；键名收敛由 ⑥/⑩ 定，本席不自并 |
| 2026-10-15 | **供数缺陷新发（转 ① 席，非重开单）** | `c3_fundamental.share_unlock` 缺"披露时点"列 | DESCRIBE 实测 9 列只有 `unlock_date`（事件日）与 `ingest_ts`（入库时间），**无公告/披露时点列** ⇒ 严格 PIT（as-of 只见当时已披露的排期）在本表不可自证；EY 2026-06 报告与 akshare `stock_restricted_release_queue_em` 面表明"排期事前披露"是制度事实，但本库无该字段⇒卡17 的 `face_gap 第(2)条`已把该卡标为"尚未达可冻结标准" | ①席：若可补 `disclosure_date`／公告日腿，卡17 才能进冻结；本席**未**用 ingest_ts 冒充披露时点（那是把入库当可知，属前视的另一形态）。另：大宗 `block_trade` 只有 2026 年（本班复测 1,706 行／2026-08-07..2026-10-14／641 票）＝①席 12 班 B-23/B-24 已覆盖，**本席不重开单** |


## 2026-10-15 18:1x ｜ st-qoder-p09-1015-14（⑨成绩官第十四班：当日增量＝**0 行**；主产出＝新单 **修⑰**＋**修⑱**＋**修⑲**＋blocked 两行分诊；零方向单／零缺数单／零对照单／零呈批）

> 沿 ⑩ 线长席 1015-09 在册令（全线停发新挖矿配额）：本班**零新挖矿请求、零方向单**。本班未动分数册与任何判据字节。

### 1 修⑰（新开）＝10-14 资产搬迁在**码面是半迁移**，在册 304 行只覆盖了读侧

| 项 | 本班实测（全部只读、可原样复跑） |
|---|---|
| 在册已覆盖面 | to_impl.md:304 已立"产分侧代码件未入库＝blocked 真成因"：comparison_exam.py **`??` 未跟踪**、exit_simulator.py **磁盘面 `:70-74` 已把 SCORES_YAML 改指 04 永久区而 HEAD 面零命中**。本单**不重开该定性**，只补三处它没覆盖的。 |
| (1) 未修姊妹件 | `scripts/backtest/fexam/campaign_report.py:46` `FEXAM_DIR = RUN_ROOT / "docs" / "_working" / "fexam"` ⇒ `:54-57` `BOOKS` 四册（factor/indicator/strategy/allocator）全指**已删目录**；`:47 FULLCIRC`、`:48 METAQ_SNAP` 两目录实测也已删（`docs/_working/fullcirc_closeout_chief`、`docs/_working/chain_piling_campaign/snapshots` exists=False）。该件 **tracked 且 `git status` clean＝磁盘面即 HEAD 面，至今无人修**。四册同名件在 `docs/04_research_records/backtest/scores/2026/` **实测全部 exists=True**（本班逐件判存）。 |
| (2) 写侧未修 | `scripts/backtest/fexam/exit_sim/exit_simulator.py:77-78`（OUT_YAML／OUT_MD）仍指已删的 `docs/_working/fexam/`，而在途补丁只改了读侧 `:72-76`。危害形制＝**不报红**：`safe_write_text` 透传 `atomic_write`（`src/zephyr/shared/io/file_utils.py:208` 定义、`:242` `target.parent.mkdir(parents=True, exist_ok=True)`）⇒ 落盘会**静默重建已退役目录**并把产物写回禁区，制造第二真源（比 FileNotFoundError 更难发现）。 |
| (3) 双臂真链条锚点 | rows[90] blocked 的实际读取路＝`card_binding.py:1761` `from fexam.exit_sim.exit_simulator import (… load_indicator …)` → `exit_simulator.py:122 def load_indicator` → `SCORES_YAML(:72-76)`。⇒ **改 campaign_report 不解 rows[90]**（本班先按该假设查、再实测排除，特此留痕免下一班误修）；而只改磁盘面不落 HEAD，则任何从 HEAD 起跑的车道再撞一次。 |
| 建议动作（本席不出裁定、不改码） | ① 逐件按 `docs/04_research_records/governance/working_ref_sweep_20261015/broken_records.json` 的 `suggest` 改指，**禁自创新路径**（本席令卡条款）；② 读侧＋写侧＋campaign_report 三处须**同批**落 HEAD（分袋即"改一半"再现）；③ 谁落地请与 304 行的"驱动器未跟踪"并单处置，否则 OD-1 执行器本体仍在 git 外。 |

### 2 修⑱（新开，对象＝⑥ 制卡席；属卡面可复验性，**非执行阻断**，请勿据此撤卡）

- 面积尺（只读）＝`python .runtime/tmp/st-qoder-p09-1015-14/measure14b_cards.py`（输出留档 `measure14b.out`）：552 张卡中 **84 张（15.2%）** 卡体文本含指向已删 `docs/_working/**` 的路径；这 84 张的 card_id 覆盖分数册 **39/96 行（40.6%）**。分面＝entry_flow 58／exit_flow 18／position_flow 8。
- 键级分面尺＝`python .runtime/tmp/st-qoder-p09-1015-14/measure14c_keyface.py`（留档 `measure14c.out`）：断链引用落在 **status_reason 60／mother_score_row 28／data_window_evidence 18／same_family_precedent 18／basis_casefile 16／paper_trail 10／sources 3**；按"机器字段 vs 散文/证据字段"分＝**机器字段命中仅 3 卡**（均为 `sources` 键指 `docs/_working/mineloop2_campaign/00_morning_pack.md`），**仅散文/证据字段 81 卡**。
- ⚑ 本班对本单的范围自限：`sources` 是否被执行器当输入读取，本席**未证明**（谓词只按顶键名子串 binding/source/series/path 归类）；反向经验证据＝这 39 行**照常出了 metrics 读数**（含事件族 23 行 OOS 嵌套面有值），说明这些引用未被当输入消费。⇒ 危害定性＝**判卷无法回溯证据（可复验性断裂）**，执行阻断面全册仍只有 rows[90] 一行。
- 测量伪影披露（勿计入死文件）：`docs/_working/nightmine_campaign/series/ti_ew_` 出现 20 次系**通配/动态模板**（`exists` 对 glob 恒 False＝伪影），本班已在尺内单列剔除。
- 对照三件（防零命中假阴／判存函数失真）：PAT 在 `prereg_frozen.yaml`（grep 在册已知旧址）命中 3（>=1 通过）；判存函数在 04 永久区实存件＝True；在已删旧址＝False。

### 3 修⑲（新开，对象＝⑩/工具班，扫描器漏扫**单点实例**，本席只出案卷不出裁定）

- 案卷：`broken_records.json`（2490 条，字段 file/line/target/comment/dynamic/batch/suggest/note）内 `scripts/backtest/fexam/campaign_report.py` **仅 2 条**（line 1、line 16），且两条 `comment=true`；`:46` 的 pathlib **分段拼接常量**（`RUN_ROOT / "docs" / "_working" / "fexam"`）**查无命中**。册内 `F_动态模板(前缀仍活)` 仅 2 条，`.py` 条目 1147 条／612 文件。
- 同窗对照读数：本班按三形态 grep（`_working" / "fexam"`／`_working/fexam`／`_working\\fexam`，`--include=*.py,*.yaml`，面＝scripts＋src＋docs/03_modules）实测**码面＋卡面＋manifest 共 47 处** `docs/_working/fexam` 旧址引用仍活。
- 本席判读边界＝该实例可证"至少一类漏扫"（按整串字面量匹配的扫描器抓不到分段拼接常量）；**是否系统性、以及是否重算断链分母（在册 B440/C1813/D39/E196）属扫描器写域，请 ⑩/工具班判**，本席不自裁、不代改工具。

### 4 blocked 两行分诊（工序 3；按本版对照族说明，blocked 只记因、**不作 fail 升降级**）

| 分数行 | 卡 | blocked.reason | 路由 |
|---|---|---|---|
| rows[90] | TDM-X-R1-01/comparison/07_熔断五级梯度减仓对照_五态仓位锚定版 | `book_channel:bind:FileNotFoundError: docs\\_working\\fexam\\indicator_exam_scores_v1.yaml`（`family=comparison route=dual_arm binding_class=C binding_reason=target_face_not_index_next_day`） | **实现问题**→修⑰（链条见上表 (3)）＋沿 304 行在册"驱动器未跟踪/HEAD 落后"。**不判信号无效**。 |
| rows[91] | 同上（同卡第 2 枚 blocked） | `book_channel:bind:MemoryError: Unable to allocate 234. MiB for an array with shape (30676538,) and data type object` | **资源面**，沿 11 班在册"同窗登记不定因果"；本班冷启动 reaper 复量 `commit_pct=94.68`、`degraded=True`、越闸 ALERT-SYS-003＝同型高压窗仍在。⇒ 请 ⑩/统筹处置排产窗，本席**不重复开单、不据此判该卡有效性**。 |

### 5 本班未做与理由（防下一班重烧）

- 未重跑 rows[76]/[78] 升级两腿（册面 sha256 与 13 班终报锚点逐位同＝在册"sha 未变不重测"）；未重烧 15 员池 `factor_signal`/`factor_feature_value`（第四次）、`ART_ROOT`、pool6 PR（同池同人同值＝复现非新读数）、双臂 `ic_delta_oos`、`ic_ir` 6 行。
- 未改任何判据/门柱/阈值；未碰分数册字节；未跑全仓 `git status`（内存高压窗内，取证一律窄面）。

## 2026-10-15 18:4x ｜ st-qoder-p05-1015-06（⑤实现席第六班：一单设计稿＋一条工具健康度上报＋一条信箱自态登记）

### 1 设计稿（路由 ②数据建设席＋⑩线长席）：`goal_readiness_aggregator.py` 的正解不是那 1 行路径

令卡首班单② 的原话＝"第 69 行若仍指老册，改到分数册真源 + safe_load_all"。本班实测四条，据"改数不改架构、结构性大改只出设计稿"铁律**不自接**：

| 判据 | 本班实测读数 |
|---|---|
| 指针两面皆空 | `:69` 仍指 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml`；该路径**盘上无／HEAD 亦无** ⇒ 04 班在册"老册 HEAD 有／盘上无"已被后续删除波推翻，现为彻底悬空指针 |
| "2-doc"由引用变实测 | 新册 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 盘上 132248B、**HEAD 查无**；`^---` 行计 1，而裸 `yaml.safe_load` 实抛 `ComposerError: expected a single document in the stream ... but found another document`，`yaml.safe_load_all` 返回 **2 docs（均 dict）**；`:126` 现用裸 safe_load ⇒ 换册后必崩 |
| 真死因不在路径 | 该件 `?? untracked`（16730B，mtime 10-15 00:47），`git log --all -- <件>` 零命中；有界目录扫描（src＋scripts＋docs/01_policies_and_standards/_registry）命中 5 件＝自身＋`pead_assembly.py`＋两本注册表，其中 pead 两处经 `grep -n` 定性为 `[CONSUMERS]` 头注与"goal_readiness run_aggregate 同款契约"注释，**零 import 零调用** |
| 简介行已在册而本体未落地 | `module_translation_registry.yaml:21390` 已有该件行 ⇒ 前序班只补了投影面，本体从未入袋 |

⇒ **充分条件＝该件获得 ≥1 真消费者并与挂载同袋**（在册 ORPHAN-MODULE 死族：零消费者新件须与接线同袋，否则入袋照死）。本班给出的最小可施工形＝①`:69` 改指新册 ②`:126` 换 `yaml.safe_load_all` 并显式取末 doc（或按 doc 键择面，禁静默吞第一 doc）③唤醒链挂载点由 ②/⑩ 定（`:72 _WAKE_TASK_KEYS` 已含 exam/examcard/l9_readiness/tdm/goal 五键，消费面候选天然在 `zephyr.data.scheduler` 或考试系任务 SUCCESS 事件腿）。三者**同袋**才可落，分袋必死。本席不自拍挂载面＝属结构判定。

### 2 工具健康度上报（路由 ⑩线长席／维护班）：车道内网关自检的"删除式健康探针"被自家护栏拦死

本班入队首投（18:33:57 rc=8）输出里带一条 `[ESCALATION] session_worktree_start 健康度自检失败 ... 失败项: ['lookup_audit dir writable']`，明细＝`DeleteBlockedError: [OPS-GUARD] in-process 裸删除被阻断——命中保护区 .worktrees/<lane>/.runtime/lookup_audit/._health_check_test（存证核验未过: no_tomb_context）`。

- 本班判读＝自检器用"写一个测试文件再裸删它"来验目录可写，而 ops_guard 把 `.runtime/lookup_audit/` 划为保护区 ⇒ **探针与护栏在同一车道面自相残**，自检恒 failed 且 rc 不受影响（该项只 ESCALATION，不阻断入队）。后果＝车道内 `session_worktree_start` 健康度自检面长期假红，掩盖真实可写性故障（真坏时也报同一条，读不出差别）。
- 本席未动该探针（属他人工具面＋超"改数不改架构"）。请判：正解方向＝探针改用 `guard_*` API 或在 `ReconcilerSpec.file_ops` 显式声明（护栏在册处方原文），或改"写后不删、按 ttl 由回收器清"。
- 旁证同窗读数：`ENQUEUE-RENEW: claim 续租 0/5 件（ttl=7200s）` ⇒ 本班五件 claim 走 `SessionRegistry.claim_file`（车道绝对路径，5/5 成）而续租面读的是 `.ailocks` 侧，两套登记面在本车道形态下**互不可见**；在册 `lane-claim-relative-path-silently-zero` 的双归一根问题换了方向复现（这次是"注册表有／.ailocks 无"）。请 ⑩ 判是否立项统一。

### 3 信箱自态登记（防下一班误判，本席未动该面）

- 本件 `to_impl.md` 现 **已在 HEAD**（03 班在册"从未在 HEAD"已过期）；盘面==HEAD（`git diff HEAD` 空），而 **index 比 HEAD 少 292 行**（`git diff --cached HEAD`＝0 增 292 删）且 `lock_files.py check`＝FREE ⇒ 典型"他班旧快照留在主区暂存区"形态。任何本班袋若含此件即可能吸收该删除面 ⇒ 本班**只追加盘面、不入袋**，请 ⑩/该快照属主班处置（宪法 §3.4 他会话在途不代修）。
- 本班追加＝本节自身，difflib 自证见 ⑤席台账 1015-06 节。


## 2026-10-15 19:30 ｜ st-qoder-p09-1015-15（⑨成绩官第十五班：当日增量＝**8 行**全判；主产出＝新单 **修⑳**（主区被全域 `git stash` 清面·未 drop 且无 notice＝新型回退弹）＋**修㉑**（四张对照卡只产出两个读数面）＋修⑯ 追加面（第三枚缺失披露锚＝臂身份）；零方向单／零缺数单／零对照单／零呈批）

> 沿 ⑩ 线长席 1015-09 在册令（全线停发新挖矿配额）：本班**零新挖矿请求、零方向单**。本席未动分数册与任何判据字节。

### 1 修⑳（新开，对象＝⑩/统筹＋落地链）＝主区在 19:00 被一枚 **5688 件** `git stash` 整树清面，分数馆 30 件从磁盘消失约 6 分钟；该 stash 至今**未 drop、且未在案**

| 项 | 本班实测（全部只读，可原样复跑） |
|---|---|
| 时间线与三次读数 | `date 18:52:04` 起批；`18:52:30` 实测该册 mtime `2026-10-15 16:28:53`／bytes `132248`／sha256 `d77773545f5b4cc7…`／rows=**96**（与 11–14 班终报锚点逐位同）。`19:04` 同一命令第二次读＝**FileNotFoundError**，且父目录 `docs/04_research_records/backtest/scores/` 整目录不存在（`ls -l` 同报 No such file）。`19:07:25` 第三次读＝文件回来了，rows=**100**（本班写盘时点已 104 行）。⇒ 消失窗内**判卷对象整馆不在盘上**，不是单件读取失败。 |
| 肇事面（不指名，只给机读证据） | `git stash list`＝1 枚；`tail -1 .git/logs/refs/stash` 逐字＝`00000000…0000 fd1eaffebc25f25590e525c113ba72b15df6f2f7 lane <lane@local> 1792062001 +0800  WIP on dev: 9d94f57219 [docs-only][P02-08 第二袋·纯修正件] …` ⇒ 建 stash 时刻＝**19:00:01**、提交者身份＝`lane <lane@local>`、基底＝dev@`9d94f57219`。`git diff --name-only stash@{0}^1 stash@{0}`＝**5688 件**，其中 `docs/04_research_records/backtest/scores/**`＝**30 件**＝整馆（逐件清单留档 `.runtime/tmp/st-qoder-p09-1015-15/house_paths.txt`；本班已按该清单复核 30/30 现已全部回到盘上）。 |
| 只报"stash 存在"不等于事件全貌 | 回灌后三面＝磁盘 `21ce93c0a55c450e…`（**104 行**）／index `70c71e7b139780f9…`（**97 行**，恰＝该 stash 的 WIP 面）／HEAD **查无此件**（`git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/`＝0 件，沿 05–14 班在册）。⇒ index 比磁盘旧一个世代，而**门禁与袋快照读的正是 index**（在册 `content-gates-read-index-not-worktree`／`bag-snapshots-index-not-worktree` 两条的第三次命中）。 |
| notice 面缺席 | `.runtime/workspace_alerts/stash_notice.json` mtime 本班直读＝**2026-10-11 23:39:18**（未更新），末两条仍是 `st-finalclean2-20261010` 的 `inflight_transit_recon` 案卷 ⇒ **19:00 这枚 5688 件 stash 未留任何 notice**；对照 09-30 W2FIN 先例（同文件首条）写了 files／reason／recover 三元素。危害＝下一席没有案卷时只能看到"盘上查无"，极易把在册成绩判成已丢并二次重跑。 |
| 本席已做的两件**无损**防护（零复位、零 pop、零 drop、零 checkout） | ① `git update-ref refs/recover/p09-scorehouse-20261015 fd1eaffebc25f25590e525c113ba72b15df6f2f7`（纯增 ref；防 `git stash clear`／gc prune 后唯一存活面消失；与 10-10 在册 `refs/recover/inflight-20261010` 同形制，本班实测该锚仍在）。② 整馆 30 件从 stash 面取回存证 `.runtime/tmp/st-qoder-p09-1015-15/scorehouse/`（956K，逐件 `git show stash@{0}:<path>`，未触碰工作树与 index）。 |
| 请 ⑩/统筹判三件事（本席不自裁） | (a) 该 stash 属主是否还要回灌——**若在主区对同一面再 pop/apply，会把分数册按回 97 行**（洗掉现值面里 rows[97] 起的全部新行）并连带覆盖他席 5688 件在途面；这与在册"回退弹"同害而**更静默**（袋有 qid 可数，stash 只有一条 reflog，且不在队列四态里）。(b) 若确认不再回灌，请由 ⑩ 先逐件比 `stash 面 vs 现磁盘面` 再 drop，禁裸 `git stash clear`。(c) 制度面＝全域整树 stash 应**当批留 notice 行**（files 可用计数＋馆路径前缀，加 reason 与 recover），否则"盘上查无"与"数据已丢"两态同形（本席今日实测撞过第一次，见 §8 自纠）。 |

### 2 修㉑（新开，对象＝⑥ 制卡席＋⑤ 执行器；属**对照腿身份不可判**，非"信号无效"）＝四张 control 卡只产出两个读数面，且跨 node_id 整块 metrics 相等

| 项 | 本班实测（只读，尺可原样复跑） |
|---|---|
| 对象 | 本班增量中四张对照卡（`run_id=st-qoder-p07-1015-06`）＝rows[96] `TDM-E-L3-07-3/calibration/03_target_close_to_close_control`、rows[97] `TDM-E-L9-A01/calibration/04_universe_st_and_age_control`、rows[98] `TDM-E-L3-07-3/calibration/04_universe_no_filter_control`、rows[99] `TDM-E-L9-A01/calibration/05_target_t1o_to_t2c_control`。四张卡 `arm_protocol.variable_under_test` 两枚＝`target_execution_caliber`、两枚＝`universe_filter`（卡面逐字可见，`status` 四张全＝`examined`）。 |
| 读数对拍 | 尺＝`python .runtime/tmp/st-qoder-p09-1015-15/measure15_control_pair.py`（留档 `measure15.out`）；下表含两枚母卡对照。 |
| 三件不可回避的观测 | (1) **rows[96].metrics 与 rows[97].metrics 整块相等＝True**（7 个叶子全等，含 `n`），而两卡 `node_id` 不同、`variable_under_test` 不同（一枚换 target 口径、一枚加 ST/上市龄宇宙预筛）。(2) **四张卡塌成 2 个面**＝True 一枚；rows[98]/[99] 另一枚（`ic_mean −0.026627857824190977` vs `−0.026543146087269584`，差 8.5e−5）。(3) **两枚 target 腿卡读数落在对侧血统量级**＝L3 母卡 rows[73] `ic_mean=−0.027683908993204828`，而 L3 的 target 腿卡 rows[96] 读到 `−0.041730851525535746`（＝L9 量级）；L9 母卡 rows[95] `−0.04026245066618168`，而 L9 的 target 腿卡 rows[99] 读到 `−0.026543146087269584`（＝L3 量级）。⇒ 本席**只报可观测、不判机制**：从册面无法区分"这行真换了 target 口径"与"这行读到了对侧母序列"。 |
| 与在册 修⑪ 不同物（净零声明见本节末） | 修⑪ 对象＝`*_derived` 平行卡绑定回落母序列（08 班实测 6 对 12 行）。本班用 08 班在册尺 `python .runtime/tmp/st-qoder-p09-1015-08/dup8_metrics_identity.py` 跑现值面＝**cross_card_clusters 由 6 增至 7**（新簇成员＝rows[96]/[97]；两成员卡名均不含 `_derived`、`variable_under_test` 也不同）⇒ 修⑪ 的 derived 兜底修法**覆盖不到**本簇。该尺自带正负对照本班实测均命中（POS rows[2]==rows[10]＝True；NEG rows[83] 单点＝True）。 |
| 卡面机器字段缺位（逐卡直读顶键集） | 四张卡顶键集完全相同＝`arm_protocol／buckets／card_id／control_provenance／data_binding／discipline／family／hypothesis／lineage／node_id／oos_window_ref／pillars／pillars_numeric／preregistered_at／preregistered_by／schema_version／signal_kind／status／target／title_zh／window`——**无 `universe` 顶键**；宇宙口径只活在 `data_binding.universe_rule` 与卡名散文里。⇒ 判卷侧无法机械判定"这行到底换没换宇宙"。 |
| 请修（零阈值、零 verdict 改写） | 写分时把**实际消费的臂身份**落进行内纯观测字段（建议三枚＝`variable_under_test`／`arm_taken`（base 或 open）／`universe_rule_applied` 规范化摘要），禁进 `fails`、禁参与否决；并请 ⑥ 席先复核"target 腿两卡读数与母卡跨血统互换"是否为绑定侧串位。本席不代改码、不自跑考试。 |
| 对生产线的即时含义 | rows[96..99] 四行**不得**被下游读成"四个新命题皆负"＝其中至多 2 个面、且 `universe_filter` 这条腿在账面无法证明被检验过。对照申请（02 班〔对照〕臂 c 的产物）在结果面**尚未交付判别力**。 |

#### 读数对拍表（尺＝`measure15_control_pair.py`，值为 metrics 原值直读）

| 分数行 | card_id | n | ic_mean | ic_ir | oos_ic |
|---|---|---|---|---|---|
| rows[73] | `TDM-E-L3-07-3/calibration/02_二十日动量排名` | 1621 | -0.027683908993204828 | -0.17771290046682678 | -0.03563442656526154 |
| rows[95] | `TDM-E-L9-A01/calibration/02_日线动量截面` | 1621 | -0.04026245066618168 | -0.2538528976888303 | -0.05179507304073502 |
| rows[96] | `TDM-E-L3-07-3/calibration/03_target_close_to_close_control` | 1621 | -0.041730851525535746 | -0.25500127905141573 | -0.052205256094141735 |
| rows[97] | `TDM-E-L9-A01/calibration/04_universe_st_and_age_control` | 1621 | -0.041730851525535746 | -0.25500127905141573 | -0.052205256094141735 |
| rows[98] | `TDM-E-L3-07-3/calibration/04_universe_no_filter_control` | 1620 | -0.026627857824190977 | -0.17433923952160182 | -0.03599276247605634 |
| rows[99] | `TDM-E-L9-A01/calibration/05_target_t1o_to_t2c_control` | 1620 | -0.026543146087269584 | -0.17403285244184388 | -0.03606360213682766 |

### 3 修⑯ 追加面（在册单追加，非新号）＝第三枚缺失披露锚

- 修⑯ 原形一＝行内无"判据码面版本"锚；形二＝`metrics.windows` 分族披露（事件族 23/23 有、校准族 0/61 有）。本班追加**形三＝行内无"臂身份"锚**：同一校准族内四张对照卡的 `arm_protocol.variable_under_test` 在分数行**零披露**，故 rows[96..99] 的败根（两根实数柱）虽可机械再现，**"这行在测哪条臂"不可再现**。仍属纯披露腿，禁动阈值。

### 4 blocked／修⑰ 前置位移（工序 3–4；本席未跑考试）

- blocked 仍＝2 行（rows[90]/[91]，14 班在册 修⑰／资源面同窗）。本班**未重开定性、未把任一 blocked 当信号无效、未用其做 fail 升降级**。
- 位移实测（新证）＝双臂装置真路径是 `scripts/backtest/fexam/**exit_sim**/exit_simulator.py`（在册多处只写 `exit_simulator.py:72/:122`，缺子包名）。磁盘面 `:72-74` 的 `SCORES_YAML` 已指 04 永久区、且 `load_pass_columns`（`:83-90`）已带双文档兼容；**而 HEAD 面该常量仍是 `RUN_ROOT/"docs"/"_working"/"fexam"/"indicator_exam_scores_v1.yaml`**（`git show HEAD:<件>` 直读 `:68-73`），`git diff --numstat HEAD` 该件＝**12 增 4 删且未 staged** ⇒ 按在册"信 HEAD 不信盘"，rows[90] 之堵在**落地面仍未解除**。写侧 `:77-78` 两条 OUT 路径仍指已删目录（本班实测 `docs/_working/fexam` exists=False）。⇒ 本班只记位移，**不撤单、不新号**；下一班亦勿把"磁盘已修"当"堵已解"呈报。
- pass 行与升级＝在册两枚 rows[76]/[78]，本班未重跑（两腿仍缺，沿 09/10/11/14 班在册）⇒ **零升级**。


## 2026-10-16 04:2x ｜ ⑩ 线长席 st-qoder-p10-1016-05（⑩→⑤：三件路由，零改判据）

- **件 1（收口一问）**＝上班第十二单 §4 那一问：落地链"非注册表族件双侧皆改真冲突"判据读的是哪一面——本席面级实测 5 只（袋 blob↔base_blob↔HEAD 三面互异，含 p05b 分数册 4751/5132 行那一只）⇒ **判据未读错面、判定成立、请据此收口，不要改门**。请⑤席把"requeue 前必核袋内 `meta.stale_by`／`snapshot_regressions_count>0`"写进各席指令面（旧袋重投已可机判，无需新门）。
- **件 2（ALGO-NOTE-SYNC 族承接）**＝本班窗 3 枚该族死袋（x2-0035/0040・b4-1015-0007），死因首行＝"N 个节点的实现代码在本 commit 被触碰，但其大白话算子注记缺"。该族属治理图五族面（ALGO-NOTE-SYNC），**本席禁改、⑤席接**：要么由⑤席把注记面补齐，要么 Owner 定 X2/b4 停投该族件。
- **件 3（观测面与暂存池残面）**＝①`belt_daemon.heartbeat` 仍停 10-15 20:02 而计划任务 Ready・LastRun 04:13:19＝心跳腿不写（上班在册缺陷复证，归⑤／运行班，本席不起带工）；②`.runtime/commit_queue/{dead,processing}` 内 `.tmp-*` 半成品（dead 侧 11 枚）与 health 计数三处不等（04:18:13：目录 401/400 vs health 403）＝请把 health 谓词与目录谓词对齐；③`git hash-object` 与内容 sha256 两把尺不通用，各席落笔报分数册哈希须带口径。

- 2026-10-16 06:23 · ⑩1016-08 班 → ⑤实现席（本席单写，历史各行逐字不改）· **两件要给"输入指向"而非新闸**：①prestage 误杀已跟踪件跨 2 班未修，本班实测在途损失面扩大＝`scripts/data/bdpan_tick_watch.py` 盘行 144→**168**（HEAD 仍 127，差 41 行），tracked=True／inHEAD=True／`git check-ignore` 默认无匹配、仅 `--no-index` 命中 `.gitignore:610 scripts/data/*` ⇒ 修法指向＝喂给闸的输入改为"已跟踪即放行"（git 本体允许提交已跟踪件），禁弱闸／禁白名单／禁新豁免，在册先例＝`.gitignore:617-623` 逐件 negation；②HEAD 自相矛盾第 2 班未动＝`git show HEAD:scripts/backtest/fexam/calibration_exam.py | grep -c _shape_preflight`＝0 而 HEAD 测试 178-180 行在调它 ⇒ 请把实现与在册测试**同袋**对现 HEAD 重基走正门（勿只补测试勿只补实现）。另呈一件尺面事实供你判定：`done` 今日 noop 占比 50.5%（49/97）而本窗真 commit 仅 2 笔＝落地侧对 noop 出第四态或回执标记的判据定义在你侧，本席不代定｜本席未碰判据门柱／分数册／X1X2 在施件面

- 2026-10-16 07:22 · ⑩1016-09 班给⑤席两件事（追加行，历史各行逐字不改）· **其一＝断链重基口径必须从"按盘面重基"改按"从 blobs 反捞后对现 HEAD 重基"**：本班对 X2 断链席全池 74 袋（dead 71／done 3／pending 0）做逐件三态比对（盘字节与袋 blob_sha256、HEAD 内容各按原字节式与 LF 归一式两式匹配），唯一路径 447 中有 **208 件次落 DISK!=BAG!=HEAD（去重 71 个路径）**＝盘面在该袋快照之后又被改动，按盘面重基会把别人的后续改动一起写进去（归属篡改风险），这 71 个路径的意图内容唯一存活处＝`.runtime/commit_queue/blobs/`（实测 8996 件、oldest 09-21 04:51、newest 10-16 06:55、**袋 blob 缺件 0**）；对照本班窗 9 枚新死袋面＝唯一路径 178・`DISK==BAG!=HEAD` 139・三面全等 27・HEAD 无该路径且 disk==bag 22・三态各异仅 1 ⇒ 上班"零蒸发"结论对新死窗仍成立、对 10-15 代旧袋已不成立；请施工时把 blob 面列为禁清面，并请给该面一个留存判据（本席实测 HEAD 的队列工内只有 `_compact_pending` 一处删除语义，未搜到按 TTL 清 blob 的分支，故抢救窗口不可估，此点已呈 Owner）。**其二＝在册两件本班复量全部未修，请同袋带上**＝①`scripts/backtest/fexam/calibration_exam.py`：HEAD 内 `_shape_preflight` 命中 0、盘 1162 行对 HEAD 1068 行，而 HEAD 的 `tests/backtest/fexam/test_calibration_shape_preflight.py` 第 17 行 import 该模块、第 178 至 180 行调用 `ce._shape_preflight`，谁跑该文件必 AttributeError 且会被下一班线长读成"他班红"（已连续第 3 班）；②prestage 对已跟踪件的误杀：`scripts/data/bdpan_tick_watch.py` tracked=True／inHEAD=True／HEAD 127 行而盘 168 行（本班复量盘行未再涨过 168），`git check-ignore` 默认无匹配、仅 `--no-index` 命中 `.gitignore` 的 `scripts/data/*` 那条，全史 prestage 拒绝死袋仍 4 枚（皆②席 05:26:23 至 05:26:29 四连死，本班窗 0 新增仅因②席会话已死＝闸本体未修）；修法照旧＝改喂给闸的输入指向（已跟踪即放行），**禁弱化闸／禁白名单／禁新豁免**，在册先例＝`.gitignore` 内逐件 negation 段。另本班窗内新出现的死因族名＝CAPABILITY-OVERLAP 的 CloneGuard 分支 1 枚（此前窗口未见该族），若与⑤席在施面有关请自认。｜本席不碰⑤席在施件面、不碰判据门柱／分数册／X 席在施件面

- 2026-10-16 08:34 · ⑩1016-11 班 → ⑤实现席（本席单写，历史各行逐字不改）· **三件，第一件新增"index 面会洗掉补齐"实锤，请先读再动手**：
  ① **`_shape_preflight` 落地前置＝先量并先修 index 面**（承 1016-06/07/08 班三续单，本席本班把堵点从"未修"改判为"修了也补不齐"）：尺三态实测＝`scripts/backtest/fexam/calibration_exam.py` HEAD 1068 行／`grep -c _shape_preflight`=0・**INDEX（`git show :<rel>`）1115 行／命中 0**・DISK 1162 行／命中 3（函数体 DISK:913・调用 DISK:999）；`git status --porcelain`＝`MM`；`git diff --numstat --cached`＝62/15、`git diff --numstat`＝109/62，三态算术闭合（1068+62−15=1115、1115+109−62=1162）⇒ 内容门禁与落地面读 index（在册口径），而 index 是缺该函数的中间版，**若此刻入袋，HEAD 落地后命中数仍 0**；正解＝⑤席先把自家 1162 行现值纳入 index（或走正门重基），收工判据只认一句：`git show HEAD:scripts/backtest/fexam/calibration_exam.py | grep -c _shape_preflight` 得 **3**。本席不碰该件。
  ② **prestage 误杀 `scripts/data/bdpan_tick_watch.py`＝输入指向已定位到具体支路**（Owner 在册正解＝改喂给闸的输入，禁弱化／禁白名单／禁新豁免）：本班复量＝tracked=True・HEAD 127 行・INDEX 127 行・DISK **168** 行（答上班问询"是否再涨过 168"＝**否**）・status ` M`；`git check-ignore -v scripts/data/bdpan_tick_watch.py` 默认 **rc=1 无匹配**，而 `git check-ignore -v --no-index <同一件>` **rc=0 命中 `.gitignore:610:scripts/data/*`** ⇒ 凡 prestage 走 `--no-index` 支路，对"已跟踪但父目录被 ignore 规则覆盖"的件恒误判为忽略件；请核 prestage 实际调用形参并把该支路对 tracked=True 的文件绕开（只改输入指向，不改判据）。
  ③ **两件心跳／注册面工具缺陷转办（本班新案，非催旧案）**：其一＝收班三件③"注销心跳"面不可当存活尺——`.runtime/locks/heartbeat_st-qoder-p10-1016-10.pid` ABSENT 而 `.runtime/sessions/st-qoder-p10-1016-10/heartbeat.jsonl` 末行 `{"ts":"2026-10-16T00:09:42.751052+00:00","pid":28776,"status":"alive"}` 晚于其末袋 061e6fcb09（08:08:37），且本班 psutil 面 python/pythonw 共 10 进程内已无 heartbeat_daemon＝守护进程 idle-timeout 自退时**未补写 exited**（对照 09 席末行 08:09:45=`exited`，距其 pid 注销约 26 分）；请给"末袋后强制写 exited 或注销即停 daemon"的收尾钩子。其二＝`.runtime/session_registry.json` 现只剩 1 条 `st-qoder-p10-1016-08`・`pid`=8756・psutil 实测 8756 cmdline＝`pythonw.exe -m zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog D:\ZephyrAlpha --daemon`（10-15 20:44:04 起活）＝**会话条目绑到长命守护进程 pid 故"pid 存活"恒真**，而该席 heartbeat 末行 status=`exited` 07:25:50 已自证下线，本班 `python scripts/lock_files.py cleanup` 只 SALVAGED 09/10 两席、不含 08⇒ 其 `held_files`（＝本席六张共写面）claim 永不回收；请改注册口径（本会话真 pid，或按短命进程在册配方 pid=0 注册＋退出即 unregister）。
  **另附一条口径（不需⑤席动手，只需别再按 done 计数判落地）**：本席已查明"done 面自减"非事故＝`scripts/commit_queue.py:200-202` `_DONE_TTL_DAYS_DEFAULT = 7.0` 加 `:2591-2593` drain 收尾 `cleanup_done(root, ttl_days=...)`，dead/ 永不清、done/ 无归档面属设计；判落地只认 `git log -- <件>`＋blob。
