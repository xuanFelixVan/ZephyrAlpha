---
ttl: task_bound
title: 隔夜/日内拆分卡族 v2 施工规格（本班新矿脉①，预冻结前置件）
created: "2026-10-13"
sid: st-examunlock-20261013
family_id: EXAMUNLOCK-20261013
---

# 一、这条矿脉在本仓的确切形状（先纠口径再立卡）

Lou-Polk-Skouras 的可检验含义不是"目标面拆两半"，而是**同一群体的收益拆成隔夜段与日内段后，
两段各自对未来有相反/反转的预测力**。⇒ 本班按"**信号拆两列、目标面不动**"冻结：

- 拆的是**信号腿**：母卡若是收益形信号，则 v2 立两张姊妹卡，一张吃隔夜腿、一张吃日内腿；
- 目标面一律仍是 `next_day_index_return`（CSI300 次日收益）——现器唯一在得的腿
  （`card_binding.index_next_day_return`，`build_signal`/`run_one` 的 `tgt` 硬编此式）；
- ⇒ 本族**不依赖"目标面通道"立项**（区别于考试班价格表里 118/121 张 C 类卡）。这是本班实测出的
  与 04 号件同一把尺的差别：C 类卡的堵点是目标腿，本族的堵点只是基序列。

腿定义真源（本仓已有，非本班自拟）：
`src/zephyr/intelligence/event_score.py:282` `overnight_return_jump(open_next, close_event)`
＝隔夜腿＝`open(t+1)/close(t)-1`；日内腿＝`close(t+1)/open(t+1)-1`（同件同式的补腿，
须在卡面 `signal_derivation` 逐字写明，禁在执行器里换对齐）。模板出处＝
`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md:169`（模板 A，在册已立法形）。

# 二、母卡分母（本班现场再取，零抄台账）

尺＝遍历 `exam_cards/**`，取 `data_binding` 非空且假设/派生式命中（涨停|limit_up|连板|晋级）者：
**36 张**，其中收益形 **19 张**（含"溢价/收益/return/pct_change/涨幅"），
计数形（家数/占比/分布/高度）不属本族——**计数没有隔夜/日内可拆**，硬拆＝造伪命题。

| 状态 | 张数 | 本族处理 |
|---|---|---|
| examined（母卡已出分） | 10 | 逐张出 v2 姊妹两张；判据键**逐字沿用母卡**（先例＝矿考二班 07 卡"判据八键逐字沿用 02 卡，零自拟数值"） |
| preregistered（题面已冻未考） | 18 | 同上，但先查其底座是否已有开价腿 |
| blocked_on_data | 7 | 不在本族首批（数据闸未解，禁硬凑） |
| blocked_on_impl | 1 | 同上 |

首批建议成员（收益形且底座含 open/close，实测表引用逐张可 grep）：
`TDM-E-L1-S3/calibration/05_limit_up_premium_derived`（examined，底座 hfq+stk_limit）、
`TDM-E-L1-S3/calibration/08_limit_up_premium_high_event_v2`（examined，事件开关形）、
`TDM-E-L1-S2/calibration/09_limit_up_count_derived`（examined，派生式含收益形）、
`TDM-E-L3-03-1/calibration/02_涨停基因`、`TDM-E-L3-05/calibration/02_连板顺位`、
`TDM-E-L3-07-1/ablation/02_烂板剔除步`、`TDM-E-L3-10/calibration/02_一字板不可成交`、
`TDM-E-L4-09/comparison/02_hard_constraints_on_off`（双臂形，须等面板/双臂消费面，非首批）。

# 三、立卡前必须先落地的一件（本班为何今晚不出卡）

底座存在性（本班现读 DDL，零 CH）：
`c1_market.kline_daily_hfq` 含 `open/high/low/close/trade_date/symbol` ⇒ 两腿都可算，**本班不假设开价面缺失**；
`c1_market.stk_limit` ORDER BY `(trade_date, symbol)`，含 `pre_close/limit_up/limit_down/st_flag` ⇒ 群体掩码有面。
但两处必须写进卡面而非事后解释：
① 后复权空间内 `open/close` 同日同因子 ⇒ 日内腿无偏；隔夜腿跨日比，**必须同因子空间**（母卡 05 先例逐字：
   "全部比值在后复权空间内计算"）；
② `stk_limit` 的在册深史限制（在案：表面自 2015/1990 起但 2019 年前仅约 237 只票且 100% rule_computed）
   ⇒ 本族任何 IS 窗早于 2019-01-03 的部分**不能称作全市场**，卡面须按在册"涨停回放诚实上限=2019-01-03 起"写窗。

现仓缺的那一件：本族每张卡的 `data_binding` 需要一条**逐日截面隔夜腿/日内腿均值**基序列。实测
`SERIES_DIR` 7 枚 CSV 全部是计数/比率形（无价格腿），`technical_indicator` 族物化件今晚才补上
（本班 `ti_daily_mean_materialize.py`，且该件因翻译册滞后暂未入库，见本班台账"落地链受阻"节）。
两腿要从 `kline_daily_hfq` 的 open/close × `stk_limit` 的涨停群体联合派生
＝**第二个物化面**，不是把本班现件加一列就能出（现件列白名单只认 technical_indicator）。

⇒ 本班今晚**不写卡件**，理由写在纪律里而不是赶数：卡面一旦冻结，判据数值就永不许改（G4-5），
而"隔夜腿/日内腿各用哪一列、群体掩码按哪一版 stk_limit、暖机段怎么切"三件此刻只有规格没有实跑面；
在没跑通的底座上先冻数值＝把猜测洗成门柱。本班按在册先例走"先立规格→底座跑通→再逐张冻卡"，
并已在 §四 把逐张冻卡所需的全部字段位预置好（接手人只填实测底座名，不增判据）。

# 四、逐张冻卡的字段模板（接手人照此填，禁新增判据键）

```yaml
card_id: <母卡 card_id>/calibration/<nn>_premium_<overnight|intraday>_leg_v2
family: calibration              # 与母卡同族；比较形（两腿对照）才用 comparison 且须双臂通道
signal_kind: series
origin: overnight_intraday_split_v2_20261013
parallel_of: <母卡 card_id>      # 血统位，禁空
mother_card_relation: 逐字沿用母卡 window/buckets/pillars/pillars_numeric 四节，仅信号腿改为
  隔夜= open(t+1)/close(t)-1 或 日内= close(t+1)/open(t+1)-1（event_score.overnight_return_jump 同式）
window / buckets / pillars / pillars_numeric: <逐字继承母卡，禁改一个字节>
target: {primary: next_day_index_return（CSI300 000300 次日收益，执行器 shift(-1) 原生口径）}
status: blocked_on_impl          # 底座未物化即如实标，跑通后转 preregistered（与 20 张反向卡同轨）
data_binding:
  signal_table: c1_market.kline_daily_hfq ＋ c1_market.stk_limit（群体掩码，逐字承母卡）
  derived_series: <第二物化件产出文件名，含 v1 版号>
  signal_derivation: <母卡原文＋本班只替换"腿"的定义一句，其余不动>
  impl_gap: 开考前验证①两腿逐日可复算②腿均值截面票数逐日如实入 meta（禁筛阈）
one_round_limit: <逐字继承母卡>
discipline: 冻结后开考；事后挪门柱=作废（G4-5）；试次全入 n_trial_ledger
preregistered_by: <接手 sid>
```

# 五、按族计试次（令卡要求的族级前置，本班实测＝未立法）

`trial_ledger_registry.yaml` 无族级/预算字段；全仓 grep「按族计试次/family_budget」只命中提案句
（`docs/_working/2026-10-12-exam-card-mining-meta-method-research.md:199`），无裁定、无机判面。
⇒ 本班不自造族计数口径（造＝第二真源）。呈批项：族级试次登记落哪本册、由哪个门执法；
在立法前本族每张卡仍按单卡入 `n_trial_ledger`（在册现行口径）。
