---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑦考工A·游标
---

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
