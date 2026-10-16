---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑦考工A·游标
---

# 游标
cursor: 本班 1017-02＝**两张真分入册**（rows[111] series 路・rows[112] panel 路，均 fail），
①本班头号纠偏＝本席 §十五 曾写"entry 零自创可物化面=0"，错在自家谓词（未认 panel 面 T+1 花括号写法＋把 classify 的 B/C 当后置依据），
  06 班已推翻过同型尺错，本班当日复现并当日改尺——改后真分账＝panel∧个股目标 9 张（CLEAN 3）＋series 自足 2 张，具名见 §十六/§十七。
②两张已烧＝`TDM-E-L2-02-2/calibration/02_板块见顶预警三信号`（ic_mean 0.04207784821389372／mono 0.6242424242424242／oos 0.12516681316942546／n 996，唯一触发柱 regime 异号）
  与 `TDM-E-L3-03/ablation/02_双池代理合成`（ic_mean -0.02328400872913283／ic_ir -0.19428287778594677／n 1621，两段 regime 同为负＝方向与先验反，非弱正不过地板）。
③本班 CH 04:01 现测坐实三张断供册面陈旧（kline_sector_880 period='1d' 818,617 行／technical_indicator 385,531,229 行／auction_snapshot 300,617 行但仅 2026-06 起），
  本班零改册；改后 entry 族 §十六 的 GAP 面（25 张同点 880）即刻可扩为开考队列。
④转单三件具名＝L2-09/03（rating_change 参照系与卡面假设不符，对账 <10%）、L3-07-2/ablation/02（三变体×单臂执行器＋权重归一化未声明）、
  L2-02-1/02（4 日式"平移"无定义，承 10-13 D10 在册分叉，本席不重裁）。
⑤下一班首查四件＝(a) 本班袋是否落地（只认 `git log -- <册>` 与 blob，勿信自述）；(b) ⑦c 1017-03 的 rows[110] 未落地行与本班两行同档并存，
  谁先投谁吸（归属篡改面），落地判据一律内容级；(c) ⑤ 是否把 regimes 散文容错与 `_panel_metrics` 的 _forward_face 消费腿接上（接上即开 L9-A06/02・L3-11-1/03・L9-A17/03）；
  (d) ① 是否按本班现测改三行断供册。
last_run: 2026-10-17T04:17:49+08:00（date 实测）
last_batch: p07a-twoface-20261017（2 张出分：0 pass / 2 fail；分数册 110→113 行）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本班实耗与收班八件读数见 ledger 班次 1017-02 段，勿沿用本行时戳。

## 前班游标逐字留档（班次 1017-02 前任＝1016-03 原文，本班不涂改）

# 游标
cursor: 本班 1016-03＝**0 张入册**，但本班推翻一枚被上一班当承重用的节拍依据＝**面板装载不是瓶颈**。
①头号纠偏（四列现测，同口 `fexam.ch_data.load_panel`，窗 2021-01-04..2025-09-09）＝kline_daily_hfq.close
  16.2 秒（1622×5642）／money_flow.main_net_inflow_pct 13.6 秒／kline_daily_hfq.open 12.2 秒／
  technical_indicator.chips_winner **62.4 秒**⇒单列全市场宽面板 12–62 秒，在册"同类宽列首拉 45.7 分/两列
  ⇒单班即吃满"（前班游标与 ledger §四 两处）在现器现窗不复现；下一班**勿再把"拉数太慢"当不开考理由**，
  真约束在卡面口径与执行器形状/解析面。请 ⑩ 按新读数重估本席节拍（本席不自改班限）。
②本班锚卡开考未遂＝L9-A06/02 主力净流入截面（唯一"表在位＋窗覆盖＋合成式冻死"的 panel 卡）：占卡锁 rc=0→
  执行器 `_panel_metrics` 在**出分前**抛 DateParseError（卡面 window.regimes 里 `bull_note` 散文声明位被整串当
  时点，calibration_exam.py:255 → :87-93）⇒卡零触碰（git status 空・status 复测 preregistered）・分数册零写・
  锁已 release。修面权属 ⑤（跳过不可解析条目并记"该柱未评估"）或 ⑥（声明位移出 regimes 并署名），本席禁碰判据。
③新死族面积尺（谓词写明＝只测 dict 型 regimes 逐 value 试 `_in_spans`）＝entry preregistered 91 张里 **7 张恒不可判**
  （panel 4／series 3），具名＝.runtime/tmp/p07/shift03_regime_deadface.yaml；相对前班在册 5 枚**新增两枚**
  L3-11-1/03・L3-11-2/03（坏键 `single_state`）。⚑ 与 ⑦c 的"39/14"是两把不同尺（其尺含 str 型 regimes 全族），勿混用。
④供数复证＝c1_market.money_flow 窗内 5,509,521 行中 `pct_change!=0`＝**0**・`close!=0`＝**0**（main_net_inflow_pct
  非零 5,495,405）⇒卡面 MUST"剔当日涨幅残差化"按本表列构造即空操作；本席按卡面 target_source 自载 hfq close 面
  构造涨幅腿与 20 日动量腿（未自创口径），信号配方已备齐在复用件内，⑤/⑥ 修面后下一班可直接出分。
⑤分母＝entry preregistered **91**／`card_binding --mode classify`＝A2・A?7・B14・C42・D0・U26（加总 91 自证）；
  panel∧regime 可解析 29 张里 12 张标的＝CSI300 指数次日面（个股截面信号×市场级目标＝形状不配，按总包 10-15
  指令面记 blocked 勿硬啃）；sector 系待 ⑥ 补 signal 申报位（⑦c 两班在册）；事件路面本班读码判废＝
  `_event_metrics(:803-830)` 只算市场级事件开关 gap，而 L9-A05/02・L9-A13/02・L9-A17/02 冻的是个股 CAR 柱
  ⇒`judge_event(:841-843)` 对未知键 fail-closed 写"未支持判据键"，本班**不产出该行**（勿把"执行器无该柱"
  写成永久册上的 fail，与 1016-02 在册"往分数册写错陈述"同型），转 ⑤ 补柱。
⑥⚑归属与交付＝本席活文档在 HEAD 侧大面积落后：ledger 盘 1142 行 vs HEAD 583 行（本班追加前即 +497/−0）、
  checkpoint +145/−0，班次 1015-06 与 1016-02 两班正文从未进 HEAD（`git show HEAD:<ledger> | grep -c "⑦A席1016-02"`＝0）；
  上一班四袋全死系分数册双侧皆改**连带**本席两件。本班按纯追加把两件装进自家袋随行走（零删自证），
  分数册本班零新行故**不入袋**（避免再次连坐）。⑦A 1016-02 的分数行已由 ⑧B 袋携带落 HEAD（现测 HEAD 110 行含该行）。

- ⚑本班三袋（0001/0002/0003）已于 00:31–00:33 全判死，死因**不是**双侧皆改而是 GATE-PRECOMMIT-RUN 的 GIT-DANGEROUS 命中本席携带的上班未落地稿行 3 处（reset 全硬串）；本班已按 ⑩ 在册正解对自家未落地稿行加行级精确标记（3 处 ≤10・仅行内追加・门尺复跑 rc=0 零命中）并以现 HEAD 为基底重投第四袋；下班首查改一件＝先读 dead_reason 再谈落地，勿把「没落地」当成「没交付」。账见 ledger §十三。

复用件（均可原样复跑，`.runtime/tmp/p07/`）：`shift03_exam.py`（load_panel 装载＋横截面 OLS 残差＋G1-G4 前置闸＋
占卡锁＋only-add 三 sha 自证一体）／`shift03_classify.yaml`（真源普查）／`shift03_regime_deadface.yaml`（7 张具名）／
`shift03_run.json`（本班开考读数含崩点原文）／`shift03_append.py`（写册器含结构自证）。

下一班首查四件：①本班袋是否落地（只认 `git log` 与 blob 内容级，勿信自述）；②⑤ 是否已修 regimes 解析面或 ⑥
已把声明位移出 regimes——修后本班 §四具名 7 张即可开考，其中 L9-A06/02 信号配方与前置闸本班已备齐；
③⑥ 是否补两张 sector series 卡（L2-01-2/02・L2-01-3/02）的 signal 侧 PIT 申报位（⑦c 两班在册＝唯二 class A 面）；
④L3-03-2/03 温和放量遗卡与 1016-02 遗留僵卡翻回权属 ⑩，勿当可考面重复占卡。

last_run: 2026-10-16 23:3x（date 实测；收班终值见 ledger 班次 03 收班段）
last_batch: p07a-moneyflow-20261016（0 张入册；分数册本班零字节；台账 +62 行／+7,224 字节／[BLOCKER] 6 枚）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本班实耗终值与收班八件读数见台账收班段，勿沿用本行时戳。


## 前班游标逐字留档（班次 03 前任＝1016-02 原文，本班不涂改）

# 游标

cursor: 本班 1016-02＝接前任 1016-01 阵亡遗留的两张 examining 遗卡，**一张真考一张不开考**。
①L3-05/02 连板顺位＝按卡面 `signal_table: stk_limit × kline_daily`（不复权底座）重建连板高度并出分入册
  rows[108]（fail：ic_mean −0.021138／ic_ir −0.468584／oos_ic −0.023220／regime −0.02330／−0.01754／n 1620）。
  三段同号为负＝**卡面冻结式在本宇宙上方向反了**（非弱正不过地板），假设面"顺位越高次日溢价越高"被否证。
②L3-03-2/03 温和放量＝不开考转单：带界已冻（1.2-2.5／>4／<0.8）而"温和带命中二值 **与** vol_ratio 截面分位"
  的合成式有两种自洽读法（前任 dry 用的裸 vol_ratio 是第三种，不属本题）⇒ 转 ⑥ 补申报位或 ⑤ 认定；卡悬 examining，翻回权属 ⑩。

⚑⚑ 前任 dry 读数不可搬（两枚实测偏差，详见 ledger 班次 02 §三）：hfq close × 不复权 limit_up＝卡面自载量纲陷阱
（本班探针实测 2023-06-05 封板 **3,882** vs 卡面在册证据 **74**；d_close 面 74/893 逐字同值）；且其判分面未裁冻结窗
（含窗外 45 日 ⇒ n 1664 而真面 1620）。两枚 `dry01_scores_*.yaml` 请 ⑩ 标废，本席不自删他会话件。

领面普查修正：entry prereg 91 张里"本席缓存面可直接物化"真数 **=0**（v1 谓词报的 3 张系卡面空绑定段假阳性）。
下一张可考须 fresh 拉 technical_indicator 宽列（在册同类首拉 45.7 分/两列，单班即吃满）或 sector 系（⑦c 在册：卡面
signal 写响应式非 t 日 PIT 式，待 ⑥；另受代码轴 2021-08 前不可回测约束）。

下一班首查四件：①本袋是否落地（只认 git log 与 blob 内容级）；②⑦c-1016-02 的 rows[106..107] 是否已落 HEAD
（本班入袋携其 2 行在途字节，零删自证 numstat 102/0）；③⑥ 是否补 L3-03-2/03 合成式与 L9-A15/02 币种宇宙申报位；
④L3-03-2/03 需 ⑩ 翻回 preregistered 后才能再领，勿当可考面重复占卡。
复用件：`.runtime/tmp/p07/shift02_exam.py`（缓存装载＋G1-G4 闸＋占卡锁＋only-add 自证一体）／`shift02_census.py`（v2 谓词）。
last_run: 2026-10-16 22:3x（date 实测 22:32:54 与 numstat 读数同框配对）
last_batch: p07a-lianban-20261016（1 张入册：0 pass / 1 fail；分数册 108→109 行）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本班实耗终值见 ledger 班次 02 收班段。

## 前班游标逐字留档（班次 06 原文，本班不涂改）

# 游标

cursor: 本班（06 双跑合账）续做完成＝**四族形状分布账**已交 ⑩ 晨报用，尺 v4 过正对照 **8/8 SHAPE_OK**。
一句话结论：**entry 95 张 prereg 里形状对得上的有 39 张，真"形状对不上"只有 10 张；三班沿用的"形状/绑定"混账里有 45 张
属自动绑定层边界（classify 只认指数目标＋panel_deferred 逐表面工序），不是"考工不能考"。**
class×形状：A 2 全 OK／A? 7＝OK 5＋双臂 2／B 14＝崩 8＋双臂 4＋净值 2／C 46＝净值 20＋未决 13＋OK 13／U 26＝OK 19＋崩 2＋其他 3。
10 张崩面已具名（ledger 班次 06 本席实例段 §八），按总包指令面记 **blocked** 等执行器形状预检上线，判据零改动。
净 15 张（OK∧只欠自家逐表面工序）＝下一班可即考试面；⚑ 该 15 是**形状面**上限，逐张还要过信号供数（内含 L9-A01/03 分钟面卡供数）
与卡面口径两关；本尺两处禁用面已标注（supply_gap 谓词失效命中 0、形状账不量信号物化）。

【P0 环境】D 盘写满：`df -h`＝732G/732G・Avail 11M・100%；`shutil.disk_usage` 复测 free_GB 0.012；
`.runtime/audit/feature_flags.jsonl` 已实报 `[Errno 28] No space left on device`。项目库/git/队列 blobs/分数册全在 D 面 ⇒ 落地链暴露 ENOSPC。
本席不代删（物理不可逆删除属 Owner 保留面），只呈报。C 17.26G／F 1477.8G／G 2357.5G 为对照面。

【P 级归属·未结】rows[96..103] run_id 全＝本席 sid 而本席零 run_card 实跑；同 sid 第二跑者 8 张出分＋台账交叉追加
（本班台账被两边同时 append：本席 §三~§七 与对方 §九 交叉追加）。请 ⑩ 定 sid 策；本席袋为严格超集（逐件 blob 判定）。

尺迭代留痕：v2 混串（primary＋target_source）→ v3 拆串但多日谓词过宽（正对照 2/8 否证）→ v4 定序修正 8/8。
自证件＝.runtime/tmp/p07/shift06_classify2.yaml・shift06_shape_census4.py＋.json・shift06_panel_shape_probe.py＋.json・shift06_disk_and_census4.py。
last_run: 2026-10-15 20:3x（date 实测）
last_batch: p07a-shapeface-20261015（本席 0 张入册＋形状账交⑩；同 sid 第二跑者 8 张在册）
notes: 下一班先读 §八 三张表（class×形状／他闸／崩面具名 10）与净 15 张清单，再决定开考；勿再沿用 commit_pct<80% 假闸。


## 前班游标逐字留档（班次 06 本席实例原文，本班不涂改）

cursor: entry 族本席实例 **0 张入册**，但本班产出第三尺错＝**判据与执行器对 panel 目标形状的要求正好相反**：
绑定册 `card_binding.py:330-338` 把"目标＝全市场指数次日面"当 panel 卡**合格**条件（命中即入 B=`panel_deferred`，:355-362＝考工自家工序），
而执行器 `calibration_exam.py:961` 按 `signal_kind` 选判分面、`:249-268` panel 路只做逐日截面秩 IC（`:250` 无条件 shift(-1)，
源码切片实测 `_forward_face` 只在 series 路＝in_series true／in_panel false）⇒ 市场级一个数喂不进 189 列截面，
负对照崩在 `:261` `TypeError`（装载崩非判据红）；正对照换同形宽表即正常出分并正确判 fail（ic −0.00032／icir −0.0045）。
B 族 16 张逐张等值分桶＝**12 形状对不上／2 形状对得上（L3-07-3/03・L9-A01/04，恰为同 sid 那班实测跑通的两张＝尺被自然实验证实）／2 派生重放面（L4-03・L4-11，另闸）**。
⚑ 本席 18:0x 口头初报"14 形状"，等值复算拆为 12＋2；退回集合仍＝16 除该 2 张外 14 张，子因两类不得混出题。

【P 级归属事故】rows[96..103] run_id 全＝本席 sid `st-qoder-p07-1015-06`，而本席零 run_card 实跑（只读普查＋合成面对照，
真卡 sha 起=止 705dd9d43d42f619）。同 sid 第二跑者 18:10 起手、19:37:04 交游标、8 张出分，与本席**同号同命名空间**
＝`lock_files` 按 sid 记持有者⇒两跑者之间零互斥。请 ⑩ 定策（sid 加跑者位／自动器取号读在册游标），本席不认领、不改判、不随袋。

【两把前任尺被推翻·本席独立复算】① `commit_pct<80%` 算力窗三班沿用而**无在册源**：真源闸
`scripts/backtest/compute_window_gate.py window` @20:01:32 实测 `{"is_trading_day":true,"window":"heavy_ok"}`＝放行；
`check --compute-class mixed` 需 `--purpose`（实测 usage 报错）⇒ 第二跑者叙述的 `gate_allow_off_hours` 本席未复算，待下一班带 --purpose 复测。
② GPU＝**加速不扩面**：`smoke_gpu.py --tier small` 实测放行（free 21497MiB・5 用例 worst|dIC|=2.220e-16・HEAD `f8e3c2b717`），
但 `calibration_exam.py` 对 GPU 零引用（grep），内核只接 `ic_exam.py`（IC_DEVICE=auto＋看门人）⇒ 不据预检开考。

分母两时点（活分母勿照抄）：17:3x prereg **103**／examined 68／blocked_impl 28／blocked_data 69／empty 133（总 401）
⇒ 19:53:58 复测 prereg **95**／examined 76／blocked_impl 29／blocked_data 69／empty 133（总 402；差额＝19:14:09 新增 1 张自宣
blocked_on_impl 的 L9-A02/calibration/13，非本席）。分数册 19:53:58 实测 **104 行**／pass 2／bytes-sha16 21ce93c0a55c450e，
工作树面属他班在途＝本席零字节未碰。

下一班领面序（按 ROI）：
①**形状预检上线后即接 12 张**（总包 20:0x 指令面：上线前此类 TypeError＝已知形状不匹配，记 blocked 勿硬啃）：
   名单与具名子因见 ledger 班次 06 本席实例段 §三之二；判据零改动，退回出题属 ⑥。
②**等⑥补 `_forward_face` 三件齐**＝6 张多日标的（班次 05 M1 清单）；③**等①改 research_report 断供行**＝3 张；
   ④**等⑤修散文 regime**＝5 张；⑤**C 族 51＋A 族 9＋U 族 26 全量形状账**＝本席同班续做，产出后另起一节落 ledger。
⑥**勿再入的面**＝dual_arm 7 张（班次 04 逐张判死）・class D 本地序列面（已烧尽）・骨架 empty 133 张（须③④席先出具名子题）。

last_run: 2026-10-15 20:0x（date 实测见 ledger 本席实例段）
last_batch: p07a-shapeface-20261015（本席 0 张入册；同 sid 第二跑者 8 张已另行在册；分数册本席零字节）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本席带守护交班；sid 撞名条款见上【P 级】段，待 ⑩ 定性后本席才再取号。

## 前班游标逐字留档（班次 06 同 sid 第二跑者原文，本席不涂改）

cursor: entry 族本班 **8 张入册**（分数册 rows[96..103，写册时点实测 104 行／139,777B／sha12 21ce93c0a55c；0 pass / 8 fail）
＋三枚纠偏把前任"现器可考面=0"推翻＝①`card_binding.classify_card` 的 B 义＝`panel_deferred(去重/撮合口径须逐表面核)`
（card_binding.py:355-362）＝**考工自家工序**不是他席堵点；②C 的第一道触发词表只认**指数**次日目标（card_binding.py:330-338），
对 `signal_kind=panel` 的卡而言"个股次日收益宽表"本是正解 ⇒ 103 张 prereg 里 panel＋个股次日目标卡实测 24 张（21 被错归 C／3 归 B），
本班烧尽其中 8 张；③前任开 panel 面的前提 `commit_pct<80%` 无在册来源，在册真闸实测
`compute_window_gate.py window`→`heavy_ok`、`check --compute-class mixed`→`{"allowed":true,"reason_code":"gate_allow_off_hours"}`，
GPU `gpu_watchman status`→free 21.29GB/util 29%（SOP §3-D 研究态 24h 不停，白天禁算只在 §3-E 实盘态表）。
分母两时点（活分母勿照抄）：18:10 首测 prereg 103／examined 68／blocked_impl 28／blocked_data 69／empty 133（总 401）
⇒ 19:37 复测 prereg 95／examined 76／blocked_impl 29／blocked_data 69／empty 133（总 402；差额＝19:14:09 盘面新增 1 张
自宣 blocked_on_impl 的 `L9-A02/calibration/13_crossday_minutep*`，非本席）。本班净变化＝−8 全对账。

下一班领面序（按 ROI）：
①**复用底座，勿重复装载**（CH 装载占本班上节工时约 25 分）：`.runtime/tmp/p07/shift06_{close,open,hfq_high,hfq_volume,
d_close,d_high,d_low,d_open,d_amount,limitup,ma5,ma10,ma20,ma60,mask}.parquet` ＋宇宙元数据装载件
`shift06_panel_materialize.load_first_quote/load_calendar/load_st_pairs`；通道等价性已逐格证
（argMax-in-CH vs `ch_data.load_panel`：102,049 格 max_abs_diff=0.0、NaN 模式全等，负对照另月亦等）。
②**转⑥三张口径未钉**（任一钉死即回收 ≥1 张，本席不代拍）：`L3-03/ablation/02_双池代理合成`＝第二项"当日涨幅截面分位"未钉
源（kd.pct_change 还是 hfq close/close_{t-1}，本卡 evidence 已自证两表量纲不可混用却未对涨幅表态）／
`L3-03-2/calibration/02_均线多排`＝"计数与 (close/ma_20−1) 的截面**复合分位**"无合成式／
`L3-12-3/calibration/02_获利盘占比`＝"chips_winner 取值域 0-1 或 0-100 **需首跑时以分布实证并写死换算**"＝看数后定，与 `frozen_note: 看数前冻结` 互斥。
③**新领面候选（本班未烧，逐张先核表可得性）**：`L3-12-3/calibration/03_股东户数集中度`（c3_fundamental.shareholder_count，
卡面谓词读起来闭合：ln(holder_count_t/prev)＋announce_date 严格 ≤T＋未公告不填充）／`L3-05/calibration/02_连板顺位`（kd×stk_limit 已缓存，
但"连板高度**档**＋异常强势**档**"分档未钉）／technical_indicator 余 2 张（含 L3-07-2/ablation/02 IC加权＝双臂面需 comparison 通道）。
④**事故面转 ⑩/运行班**＝分数册 `docs/04_research_records/` 全馆 HEAD 侧 0 件（`git ls-tree -r HEAD` 实数 0），index 现为他班
97 行快照（`AM`），本班 7 行只在盘面。本班值守内已被他会话整树落地洗过一次（19:00:53-19:04:32：册与 scores/2026 目录三面查无、
四张卡面复位回 preregistered、后 3 行被吞），恢复靠自有 pre-shift 备份＋同码同参补投（sha 链与首投**逐位同**）。
四枚副本留存证区可原样复跑：`shift06_register_{preshift,at97,at100,final}.bin`。**落地面未成之前每班开班先核册 sha，勿信上一班游标。** 本班袋①（两件活文档）于 19:5x 判 dead，dead_reason 首段＝落地器对 21,108 文件 `git reset --hard refs/heads/dev` rc=128（3%→9% 处断），盘面三件逐件复量与袋 blob 逐位同＝交付未受损；交付终态以袋③为准，史文见台账 §八。 `[GATE-SELFDOC:GIT-DANGEROUS]`
⑤**用芯面凭证缺口转 ⑤**：`IC_DEVICE=auto` 现测 `_resolve_device()='gpu'`（ic_exam.py:213），但 `device_ledger` 只在 `run_exam`
返回体内（ic_exam.py:447），`run_card→_panel_metrics→fast_rank_ic` 路径不落任何持久芯账 ⇒ 本班 8 行既不断言 GPU 读数也不断言回退。
⑥**勿再入的面（更新在册清单）**：dual_arm 7 张（班次 04 逐张判死凭据在册）／tick 重放族（L4-03・L4-11・L9-A02 全族，
19:00:53 后已由他会话置 blocked_on_data/blocked_on_impl）／散文 regime 面（本班复测 L9-A15/02・/03 两枚 `DateParseError`，
`_span_pairs` 命中日期 <2 即退回整串单点）／6 张多日 `_forward_face` 面仍等⑥／骨架 empty 133 张须③④席先产具名子题。
⑦**转⑨（在册 panel 行不可复现）**：rows[95] 与 rows[73] 用"卡面口径＋现库"15 枚候选组合全不中（最小差 3.34e-4，n 皆 1621＝
窗对而截面成分不对），库面时移已排除（窗内 max(ingest_ts)=2026-09-24，今日新灌 1,457 行全在窗外）；
同 node 三卡宇宙不同物（L9-A01/02 无 universe_rule 而 /04・/05 有）⇒ 判卷须分面；本班 rows[96]≡rows[97] 逐位同值＝
两卡申报面同形（同 ret_20＋同 t+1 close→close＋同 universe 原文），非复跑伪影，请合并叙述。

⑧**pop 回退风险**：`stash@{0}` 未 drop ⇒ 主区一 pop 分数册按回 97 行（⑨席15 ledger:970 在册），下一班开班须 `git stash list`＋核 `refs/recover/p09-scorehouse-20261015`；本班台账 §八 一处假锚（席名写错）已另起更正。
last_run: 2026-10-15 19:37:04（date 实测）
last_batch: p07a-panel8-20261015（8 张入册＝rows[96..103]，0 pass / 8 fail；分数册 96→104 行；本班净增 7,529B，cum_prefix 对开班 96 行备份=True）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本席 60 分钟班 vs 前班入队续租锁＝结构性自锁仍在（班次 03 堵点①⑦未解）；
本班达 ≥8 张保底，"节拍降档/并席"呈批面（班次 05 §七）本班不撤但补一条事实：可考面非 0，降档判据须先按本班 §二 三枚纠偏重估。

## 前班游标逐字留档（班次 05 原文，本班不涂改）
# 游标

cursor: entry 族本班 **0 张入册**。三把尺同框互证"现器可考面=0"（执行器路由真源 `pillars_route`／本班轻重底座尺
（首版正则漏裸名 `kline_daily_hfq`⇒16 张 panel 误判轻底座，逐张人读后**当场自纠**）／真源普查件
`card_binding.py --mode classify`＝A2・A?7・B16・C52・D0・U26 加总 103），并以判官直调做**正/负对照**证明
"0 是面结论非管道失明"（正＝L1-S2/40 出 fail 且读数逐柱受门柱约束，负＝信号取反柱集换人；卡面 sha 起=止）。
本班不重抄前任结论，交付＝量化纠偏＋新面锚点（见下①②③）。
分母（16:41 与 16:5x 两时点实测，**读数同值而成员已变＝禁当同面**）：preregistered 103／empty 133／
blocked_on_data 69／blocked_on_impl 27／examined 68；值守内改名者点名＝L9-A17/02（⑥席 p06-1015-09，16:09:43）
blocked_on_data→preregistered・L9-A01/02（run_id st-autoplan-verify-20261015，16:28:53，非本席）→examined；
分数册主册 95→**96 行**（他席在写，git 面 AM，本班零碰；TDM-E 面 82 行／pass 2 行）。
下一班领面序（按 ROI）：
①**等⑥（新面 6 张，前任移交清单未覆盖）**＝多日前向标的缺 `_forward_face` 三件齐申报位（须
`target_forward_face: precomputed`＋`target_horizon_days` 2..252＋`target.primary` 内 `mkt_fwd{h}` 同值，缺一即拒）：
L9-A08/02・L9-A11/02・L9-A12/02・L9-A13/02・L9-A17/02・L9-A17/03。全库申报者仅 8 张＝班次 01 的 class D（现全 examined）。
改记号＝动冻结目标面命名＝呈批面，本席不代拍；另一路＝⑤给 sector/panel 面接 h 日聚合。
②**等①（本班 CH 实测翻案）**＝断供册 `c3_fundamental.research_report` 行文字仍写"rating_change 维持空列・status=open・
last_updated 09-21"，本班实测＝294,066 行中非空 **267,835（91.08%）**・取值 维持/上调/下调/首次 四类齐・
publish_date 非空面 2017-01-02..2026-10-14；负对照空串谓词命中 26,231，`hot_value` 列查询报 404（与册
verification_20260921"该列已不存在"吻合）。**册为真源故本班照旧不开考挂它的三张**（A17/02・A17/03・L2-09/03），
①席复测改行后下一班才接。
③**等⑤**＝散文 regime 串装载崩（本班实测 entry prereg 内 5 张：L9-A06/02・L9-A11/02・L9-A15/02・L9-A15/03・L9-V3/ablation/02，
键名 bull_note/unavailable；`_span_pairs` 不足两日期即退回整串单点⇒`pd.Timestamp` 抛）；
`card_binding --mode classify` 传相对 `--cards-dir` 崩 relative_to（**正解传绝对路径**，本班实测可用）；
另承接前任在册：双臂 panel 权重矩阵面 4 张＋双臂各自 target 面 2 张。
④**算力窗班**＝本班三次 date 配对实测 commit_pct **89.13／94.98／89.52**（门槛 <80%，全程未成就）⇒ 个股 hfq panel
面 15 张不开；底座读数复用前任 shift04_hfqprobe.json（7,590,928 行／5,642 票／重复单元 0），同签名事实勿重跑。
⑤**断供尺纠偏（转⑩与各班）**＝前任"表名级"命中 61 张而按在册 status 词表（open|no_source）真断供仅 38 张
⇒ **23 张被 accepted/completed/mitigated/monitoring 多挡**；本班一张未据此开考（这 23 张逐张另有 classify B/C/U 闸），
只纠谓词：断供＝表绑定 ∩ status∈{open,no_source} ∩ 卡窗 ∩ 该卡所需列。U 面两数勿混用：classify 谓词（缺
data_binding 或缺 signal_table）＝26 张，本班窄谓词（整段 data_binding 缺失）＝12 张。
⑥**勿再入的面**＝dual_arm 7 张（班次 04 逐张判死凭据在册）・class D 本地序列面（D=0 已烧尽）・
骨架 empty 面（133 张，须③④席先产具名子题）。
本班自证件（`.runtime/tmp/p07/`，均可原样复跑）：shift05_census.py＋.json（路由尺）・shift05_classify.yaml
（真源普查，绝对路径才通）・shift05_findings.py＋.yaml（M1 六张清单／M2 两把断供尺 61 vs 38／M3 与 A 面交集）；
正/负对照＝内联判官直调（读数在台账 §三，零写盘）。
本班事故如实上报：pid=0 注册的会话于 16:58:02 被外来回收，心跳末行自证 `status:"exited"・reason:"session not in registry"`
＝在册"pid=0 短命注册被收"形态复证；本班按在册处方同串重注册＋独立后台重启守护（pid 47564）后续做，未放他人 claim。
last_run: 2026-10-15 17:13:12（date 实测）
last_batch: p07a-census-20261015（0 张入册；分数册本班零行未搬，主册现 96 行／pass 2 行／TDM-E 面 82 行）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本席 60 分钟班 vs 前班入队续租锁＝结构性自锁仍在；
连续三班（03/04/05）四闸下 0 出分且真源尺给出现器可考面=0 ⇒ 请 ⑩/总筹按在册停手考虑节拍降档或并席（本席不代裁）。

## 前班游标逐字留档（班次 04 原文，本班不涂改）

cursor: entry 族本班 **0 张入册**——四闸（判据面／装载面／卡面口径／算力窗）下 0 张可考；本席唯一未探面 dual_arm（7 张）已**逐张实测判死**（4 张 `_series_metrics` 拒权重矩阵 ValueError／2 张双臂共用 target 与卡面"各臂池收益"不同构／1 张卡面门槛 conc>=0.30 在自述分母下考窗 997 日 0 次成就），故下一班**勿再入 dual_arm 面试投**。
分母（本班 15:2x 与 16:3x 两时点实测，活分母勿照抄）：preregistered 103／g_pass 85（series 48／panel 37）／有 data_binding 的 series **39**（48 减 9 张无绑定位＝U 面不入写域）／dual_arm 7／blocked_on_impl 27（上班读数 23，本班值守外被上游推进 4 张）／examined 68。
上游回收状态实测：entry_flow 全树 10:31 后仅 **1 张**卡被改（L9-A01/08，12:49 转入 blocked_on_impl）⇒ 上班堵点②七张**卡面一字未动**，"等⑥"面未回收。
下一班领面序（按 ROI）：①**等⑥**——本班台账堵点③给出 6 类新增精确锚点（L2-01-3 缺 series 折标量句／L2-01-2 前向归属未钉／五张 ablation 查表值与主臂无数／L2-02-1 03·03b 三臂与 confirm_k 的 k 无数／L9-A10 "或"字二选一／L2-02-2 RSI 阈值与第三信号无源），任一闭合即回收 ≥10 张；
②**等⑤**——双臂支路加 panel 权重矩阵面（4 张）＋双臂各自 target 面（2 张）＋`_in_spans` 不可解析段跳过（1 张 L9-A15/03；实测 calibration_exam.py 今日零提交）；
③**算力窗班**（commit_pct<80%；本班两次实测 83.5%／92.73% 且 degraded True 未成就）开个股 hfq panel 面 15 张，先核 target_source 自相矛盾件是否已被⑥更正（本班实测＝未更正），底座行数与列集读数复用前任 shift04_hfqprobe.json（7,590,928 行／5,642 票／重复单元 0）；
④断供面勿再当可考分母：本班对册 82 条逐条扫，命中共表＝macro_data(open)／research_report(open)／kline_sector_intraday(discontinued)／sector_constituent(2026-07-22 起)／edb_data(accepted)／alt_shipping_index／alt_typhoon_track／technical_indicator(duplicate)；
⑤U 面（无 data_binding 段）9 张不在考工写域，勿计入可考分母。
本班自证件：尺与普查 .runtime/tmp/p07/shift04x_census.py＋shift04x_census.json（宽筛读数 6/48，附"命中数≠可考性"自纠）；开考与对拍 shift04x_run.py＋证据 shift_1015_04x_evidence.yaml；接手三证核查 shift04x_open_report.json；交班组件 shift04x_promote.py。
本班事故与复原（如实在册）：run_card 实跑把 L2-04/02 翻 examined 并向**暂存面**追加 1 行（95→96）；本班判"未触发不入册"⇒ 主册字节全程未碰（sha 起=止 8903ef9e9c731fdcc…），卡面以 HEAD blob 原字节复原（disk sha==HEAD sha==896548cbc734d04d…，git status 该路径空）；副作用 trial_ledger_registry.yaml +126 行（含本班 1 条）**不随袋提交**。
在册事故复证：前任班次 04 注册 pid=0 后守护 13:27 idle 1800s 自退（心跳末行自证 exited）⇒ 本班会话同风险；本班处方＝守护以独立后台进程起（`python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <sid> <repo> 30 ""`，PYTHONPATH=仓根）而非 `_spawn_heartbeat_daemon`（后者在本机实测 `No module named scripts.ops_guard` 静默失败）。
last_run: 2026-10-15 16:09（date 实测）
last_batch: p07a-dualarm-20261015（0 张入册；分数册行数不变，主册现 95 行、pass 2 行）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本席 60 分钟班 vs 前班入队续租锁＝结构性自锁仍在（班次 03 堵点①⑦未解），本班带守护交班。

## 前班游标逐字留档（班次 03 原文，本班不涂改）

# 游标

cursor: entry 族 series 面在本班四道闸下烧至 6 张出分＋九类卡面口径未闭合（逐张锚点见台账堵点②，均已转⑥/⑤，本席不代拍）。
分母（本席 09:5x 实测，活分母勿照抄）：preregistered 109／判据面通过 91（series 54／panel 37）／缺 oos_window_ref 0；机判词表外键**按路由取词表后=11 张（全在 series 面）**，双臂 7 张在 _UNION_PILLAR_KEYS 下全 clean（勿拿 5 键尺一把量，本班首跑就栽在这）。
本班烧 6 张后同串复测：preregistered 103／判据面通过 85。
本班烧掉的 6 张＝L1-AGG/02·L1-S0-1/03·L1-S5/03·L2-02-1/02b·L2/ablation-02·L2-09/04（全 fail，无 pass）。
下一班领面序（按 ROI）：①**算力窗班**（commit_pct<80%）开个股 hfq panel 面 15 张（目标面 stock_fwd_ret_t1o_to_t2c 共用一次物化，先核卡面 target_source 自相矛盾件是否已被⑥更正）；
②等⑤修 `_in_spans` 装载崩（本席台账堵点①）后回收 L9-A15/03；③等⑥补 series 收口句后回收 L2-02-1/02·L2-02-2/02·L2-04-1/02·L2-05-1/02·L1-AGG/03·L2-09/03；
④U 面（无 data_binding 段）不在考工写域，勿再计入可考分母。
本班自证件：只读普查 .runtime/tmp/p07/face_census_1015_03.py（改正后 91/109 与上班两时点读数交叉一致）、开考 .runtime/tmp/p07/shift03_run.py＋shift03_extra.py、
搬账 .runtime/tmp/p07/shift03_promote.py、证据 shift_1015_03_evidence.yaml／_extra_evidence.yaml／promote_1015_03_report.yaml、日频导生落盘面 shock_daily_1015_03.parquet。
在册事故复证：本班 pid=0 会话值守内被外来回收（11 件 claim 同批被收走），正解=同串重注册＋重 claim＋重投（台账堵点③）。
last_run: 2026-10-15 10-15 10:31（date 实测）
last_batch: p07a-sector6-20261015（6 张出分：0 pass / 6 fail；分数册 84→90 行）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本席 60 分钟班 vs 前班入队续租锁＝结构性自锁仍在（上班堵点①⑦未解），本班带守护交班。

## 前班游标逐字留档（班次 02 原文，本班不涂改）

# 游标

cursor: entry 族 class D 面已烧尽（班次 01 八张 07:23）；班次 02 用 run_card API＋CH 实读打开 panel 面 1 张
（TDM-E-L9-A03/calibration/02_880板块相对强弱持续性，fail：ic_mean 0.0111／ic_ir 0.0374／oos_ic +0.0210／n 976 日）。
普查读数（活分母 109，分母在动勿照抄）：判据面通过 91（双臂 7＋机判词表外键 11 之外）；卡塞在装载面——
target_face_not_index_next_day 51（其中判据面通过 41）／no_data_binding_section 12／panel 待装配 12／
multi_table 复合配方 16／signal_column 非单标识符 3／绑定册缺项 4／needs_replay_engine 1／
class A 名义可绑实为 anyLast 砍面板（假分红线，不开）2；23 桶合计=109。
下一班先跑只读普查领新面（.runtime/tmp/p07 下 census／gate_census／unlock_ledger／panel_face_review 四件 1015_02.py 可复跑），
并先核三件在飞袋：q-20261015-st-qoder-p07-1015-01-0001/0002 ＋ 本班袋（本班袋=上班袋严格超集，倒序时上班袋最多判 noop，见 ledger 堵点⑤）。
最高 ROI 单点（转绑定层属主）：_REGISTERED_TABLES 只 5 张表，c1_market.kline_daily_hfq 未入配方册 ⇒ 本族 12 张 B 卡有 9 张卡在此。
last_run: 2026-10-15 09:38（date 实测）
last_batch: p07a-880rs-20261015（1 张出分：0 pass / 1 fail；分数册 83→84 行）
notes: 游标由本岗每批推进；监督员(⑩)可代修。本席 60 分钟班 vs 前班入队续租 90 分钟锁＝结构性自锁，待 ⑩ 定策（ledger 堵点①⑦）。

## 前班游标逐字留档（班次 01 原文，本班不涂改）

cursor: entry_flow class D 八张（L1/TDM-E-L1-S2__calibration__40..47）已出分并翻 examined；本族剩余可考面=class A 2 张＋A? 7 张（需绑定册），class B 15 张（panel）与 C 49 张（重放引擎）按在册判据后置，U 40 张无 data_binding 段不考 ⇒ 下一班开考前先跑只读普查领新面，勿照抄本游标
last_run: 2026-10-15 07:23（date 实测）
last_batch: p07a-agg8-20261015（8 张出分：2 pass / 6 fail；分数册 75→83 行）
notes: 游标由本岗每批推进；监督员(⑩)可代修。


## 下一班指令（总包裁定 2026-10-15）
- 收班后执行"形状尺"C 族 51 张+A 族 9 张+U 族 26 张全量切查（方法=06 班 ledger 的正负对照），产出四族形状分布账→报⑩晨报。
- B 族 14 卡 ill-formed 已按具名子题规则退回重新出题；执行器形状预检施工中，上线前遇 TypeError :261 崩溃=已知形状不匹配，记 blocked 勿硬啃。

【交班终态】本班袋 0006 已 dead（死因＝reset --hard unable to write file＝D 盘满）；同 sid 六袋全 dead（三族磁盘死／两族门禁死）；分数册 104 行 git cat-file 证 **从未落 HEAD**（工作树 AM＝他席在途），交付存证 .runtime/sessions/st-qoder-p07-1015-06/staging/p07a06_{ledger.md,checkpoint.md}（sha16 a50691d50ead57a4 / f0c0a9fb3922b836）；claim 不放，等 ⑩ 定磁盘策后重投。

<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 120781 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。
