---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑨成绩官·findings台账
---

# P09 成绩官台账（判卷结论+归因草稿，only-add 追加式）

## 2026-10-14 st-e2e-test-p09 ｜ TDM-E-L3-07-3/calibration/02_二十日动量排名

- 卡面：entry_flow/L3，status preregistered→examined（工具翻转），lineage.score_row=exam_scores_v1.yaml#rows[73]
- 执行：calibration_exam.py——CLI --target-csv 面对 panel 卡崩溃（见 findings），改走同一执行器 run_card() API 面（其错误信息自述的合法注入路径），零判卷逻辑改动；数据面按卡 data_binding 冻结口径物化（hfq ret_20 信号 / T+1o→T+2c 可成交目标 / 前缀 60,00,30,68+ST(st_flag)+上市满 60 交易日宇宙，5375 符号×1622 日）
- 出分：verdict=fail，ic_mean=-0.0277（柱线 0.02）、ic_ir=-0.178（柱线 0.3）；regime bull=-0.0251/bear=-0.0188 同号；oos_ic=-0.0356 同号 oos_ok=true；n=1621
- 判卷机械核对：①一票否决成立——两条 fail 均按 pillars_numeric 冻结线机械得出，与分数行 fails 逐字一致；②未被否决柱核对——regime_same_sign（牛熊同负）、oos_same_sign 判过正确；③mono_spearman_min panel 路无机判面，分数行 unjudged.numeric_keys_no_machine_face 如实显形、零否决权，未被冒充为 pass；④numeric_keys_not_read=[] 五键全被读；⑤分数册 only-add 73→74 行经工具写入，卡面 status/lineage 翻转与 rows[73] 指针闭环。判卷面无异常。
- 归因四分诊：
  1) 真无效【主归因，高置信】：20 日动量在冻结窗全段稳定负 IC（IS 牛熊/OOS 同号，量级 -0.019..-0.036），方向与卡面假设（动量正溢价）相反——A 股个股 20 日截面呈反转面，信号层假设被数据否决，非边缘未过线。
  2) 实现数据【未见致败缺陷】：物化逐条落卡面冻结口径；hfq open/close 同基准经 600519 除权附近抽样与 raw×adj_factor 全等核验；对齐面按执行器 shift(-1) 语义推导注入（signal[t]↔open_{t+1}→close_{t+2}），错位只衰减不反号，不足以翻转结论。
  3) 判据【无 bug】：ic_floor/ic_ir_min 冻结线按正动量假设立柱，负 IC 直接触线，判据如实工作；panel 路 ic_ir 本次有机判面（-0.178 已评估），历史"ic_ir 恒 NaN"缺陷已修。
  4) 需对照【残留张力，留对照试次】：节点层 strategy_mounts=verified（STR-TSMALL-001/STR-VAL-001）与本卡信号层否定并存——建议对照：a) close→close 收盘口径目标复算；b) TopN 选股面（卡面 Top10/20/30）而非全截面 IC；c) 去 ST 过滤敏感性。对照落地前，本卡 fail 维持原判，不动节点 confidence。
- findings（e2e 链路测试带回）：
  1. calibration_exam.py CLI 面板卡目标注入缺陷：main() 对 --target-csv 无条件 t.iloc[:,0] 砍成单列 Series，signal_kind=panel 卡在 _panel_metrics→fast_rank_ic 崩 AttributeError（'Series' object has no attribute 'columns'），--target-csv 对 panel 卡不可用；API 面 run_card(DataFrame) 正常。
  2. 考试执行器缺省 CH 取数面未接（signal_spec/target_spec 属"W4 运行期配置"），每张卡须自物化 CSV/绑定册注入——SOP 若记载"--card 一键开考"则与实际不符（本次按 --help 实测为准）。
  3. 物化侧无向量化示范成本：首版逐日 .loc 掩码循环 40 分钟未出（自杀重写向量化后 53 秒）；建议物化样例入 SOP。
  4. 未见异常项：lock_files/两表 schema/ch_data 通道/分数册追加/卡面翻转/n_trial_ledger 记账均正常（本次 run_card 返回行无 ledger_warning）。

## 2026-10-15 st-probe-04mig-20261015 ｜ TDM-E-L9-A01/calibration/02_日线动量截面

- 卡面：entry_flow/L9，status preregistered→examined（工具翻转），lineage.score_row=exam_scores_v1.yaml#rows[74]
- 执行：probe_run.py 驱动（.runtime/tmp/st-probe-04mig-20261015）——ch_data.ch_query_df 位置协议（TSV 无表头 c1..cN）首版按语义列名访问崩 AttributeError（'DataFrame' object has no attribute 'trade_date'），按 SELECT 列序改名+转型最小 diff 修复（trade_date→DatetimeIndex 供执行器 OOS 切窗 pd.Timestamp 比较；价格列 str→to_numeric）；向量化物化 32s 拉齐 hfq 7,590,928 行×5,642 符号×1,622 日（禁逐日循环），run_card() API 面注入零判卷逻辑改动；排除面按卡 data_binding 冻结口径（一字板 58,748 剔除生效；停牌面窗内退化 no-op，见 findings②）
- 出分：verdict=fail，ic_mean=-0.0406（柱线 0.02）、ic_ir=-0.256（柱线 0.3）；regime bull=-0.0396/bear=-0.0308 同号；oos_ic=-0.0518 同号 oos_ok=true；n=1601
- 判卷机械核对：①一票否决成立——两条 fail 均按 pillars_numeric 冻结线机械得出，与分数行 fails 逐字一致；②未被否决柱核对——regime_same_sign 机判面=牛熊同号（bull/bear 同负判过），oos_same_sign 同负判过，样本闸双过；③mono_spearman_min panel 路无机判面，unjudged.numeric_keys_no_machine_face 如实显形、零否决权未被冒充 pass；④numeric_keys_not_read=[] 五键全被读；⑤分数册 only-add 74→75 行经工具写入，双文档 register 形态保形（safe_load_all docs=2，doc0 register 头 created=2026-10-14 未动），卡面 status/lineage 翻转与 rows[74] 指针闭环，n_trial_ledger 记账无 ledger_warning。判卷面无异常。
- 归因四分诊：
  1) 真无效【主归因，高置信】：20 日动量 rank_pct 全截面在冻结窗全段稳定负 IC（IS bull/bear 与 OOS 同负 -0.031..-0.052），方向与卡面动量正溢价假设相反；与同族姊妹卡 TDM-E-L3-07-3（ic_mean=-0.0277，宇宙含 ST/上市龄过滤口径）双重独立物化同判——A 股个股 20 日截面呈反转面，信号层假设被数据否决，非边缘未过线。
  2) 实现数据【未见致败缺陷】：物化逐条落卡面冻结口径（hfq close 20 日动量→逐日 rank_pct；target=执行器 shift(-1) 语义 T→T+1 收盘收益；一字板 58,748 剔除）；停牌面退化只加噪不改号（fexam 家族缺 bar=NaN 代理部分补偿），不足以翻转结论。
  3) 判据【无 bug】：ic_mean_min/ic_ir_min 冻结线按正动量假设立柱，负 IC 直接触线，判据如实工作；panel 路 ic_ir 本次有机判面（-0.256 已评估，历史恒 NaN 缺陷已修面）。
  4) 需对照【残留张力，留对照试次】：同姊妹卡——节点层 strategy_mounts=verified 与信号层否定并存；本卡为全截面口径（无 ST/上市龄过滤，L9 卡面冻结口径如此申报），建议对照 a) 姊妹卡同款宇宙过滤敏感性 b) TopN 选股面（buckets）。对照落地前本卡 fail 维持原判，不动节点 confidence。
- findings：
  1. ch_query_df 位置协议坑（驱动侧）：TSV 无表头协议列名 c1..cN 且 dtype=str，外部驱动按语义列名访问必崩 AttributeError；fexam 仅 load_panel 内部改名，外部驱动须自行按 SELECT 列序改名+转型（trade_date 不转 DatetimeIndex 则执行器 OOS 切窗错型）。本班已最小 diff 修复驱动（probe_run.py）。
  2. c1_market.suspend 数据缺口：全表仅 36 行（2026-09-04..2026-09-23），考试窗（2019-01-04..2025-09-09）内 0 行——卡面 exclusions 冻结的停牌剔除面退化 no-op（ch_data 空结果契约返回 0 列空 df，驱动需 len() 守卫）；一字板面正常。建议 suspend ingest 回补或卡面标注数据可得性。
  3. 未见异常项：CH 只读通道/向量化物化/run_card API 注入/分数册双文档追加/卡面翻转/n_trial_ledger 记账均正常。
## 2026-10-15 st-qoder-p09-1015-02 ｜ ⑨成绩官首班（当日增量＝0 行）

- 班次号依据：本席台账今日已有 1 班（`st-probe-04mig-20261015`，rows[74]），本班取 02。
- **降级直改主区·原因登记（RULE-WORKTREE）**：本班未开车道，直改主区追加面。原因＝本批改的是**共享追加型席位交接件**（pulse/三联单/迭代史/本台账），车道副本与主区并发写入必互撞；防护＝逐件 `lock_files.py acquire`＋`safe_write_text` CAS＋只追加不改已有字节。⑩席可按 GW 计数审计本条。

### 1 判卷面（当日增量）

- 分数册 `exam_scores_v1.yaml` 实测 docs=2、rows=75（索引 0..74），mtime 03:37 < 台账 rows[74] 条目 mtime 03:40 ⇒ **rows[74] 之后零新增，本班当日增量＝0 行**，无新分数可判。
- 游标陈旧如实记：`checkpoint.md` 仍写 `cursor: 未开始`，而台账已判到 rows[74] ⇒ 上一班未推标；本班已把游标推到 `rows[74]（75 行全判）`。

### 2 门柱一票否决机械回核（抽 3 行回卡体：rows[72]/[73]/[74]）

- rows[73] `TDM-E-L3-07-3`：卡体 `pillars_numeric`＝{mono_spearman_min 0.6, ic_mean_min 0.02, ic_ir_min 0.3, regime_same_sign, oos_same_sign}；本席按卡体冻结值独立重算 ⇒ 违反集＝{ic_mean −0.0277<0.02, ic_ir −0.1777<0.3}，与分数行 `fails` 两条**同键同源**（字符串差异仅十进制位数）；mono_spearman=null 已如实入 `unjudged.numeric_keys_no_machine_face` 且零否决权；牛熊同号（−0.0251/−0.0188）与 oos 同号（−0.0356）判过。**门柱未走样**。
- rows[74] `TDM-E-L9-A01`：同型，违反集＝{ic_mean −0.0406, ic_ir −0.2559} 与 `fails` 一致；regime −0.0396/−0.0308 同号判过；oos −0.0518 同号判过。**未走样**。
- rows[72] `TDM-E-L1-AGG`：违反集＝{mono_spearman 0.4000<0.6, ic_mean 0.0014<0.02} 与 `fails` 一致；ic_ir=null 入无面声明。**判卷无误，但卡面翻转未发生 ⇒ 修①**。
- 三口径对账（本席独立复算，非转述）：04 区合计 pass=81／fail=87；逐册＝indicator 78P/0F、indicator_conditional 1P/7F、metaq_wave2 1P/2F、mom029_reexam 1P/0F、emotion_index 0P/3F、exam_scores_v1（卡考主册）0P/75F。采纳 ⑩ 02 班口径更正：**卡考主册 0 pass 不得当全线结论**；78/81 的 pass 全在指标口。
- pass→verified 升级与 TDM 挂接：本班**零执行**（增量 0 行且卡考主册 0 pass）；指标口 78 pass 属另一口，其晋级面须由 ⑦⑧＋⑥席按指标口判据另核，本席不越口背签。

### 3 结构性观察（家族级，本班 5 条）

1. **三口径不是同一把尺**：指标口 78P/0F 满门绿与卡考口 0P/75F 同册并存；且指标口 143 行、factor 口 175 行、strategy 口 161 行**全无 `date` 字段**（本席 probe：recent=[('None',N)]）⇒ ⑨席对这些口算不出"当日增量"，也按不了迭代预算窗。分数册 only-add 的"当日增量 100% 判卷"保底在兄弟口**机械不成立**，须 ⑤/⑦⑧席补 date 列或本席改口径呈批。
2. **迭代预算被"链路复读型复跑"吃穿**：12 个对象多行，其中熔断 07／07b 各已 4 轮（超 ≤3/月）、L2-02/03/04-2 各 3 轮（达上限）；更关键＝`route-audit`/`reread` 前缀的复跑在分数册无"性质"标记，2 组 metrics 逐字节全等仍各占一行（rows[29]/[33]、[30]/[34]）⇒ DSR/PBO 分母与迭代预算**同时失真**（在册另一向偏差是少记 17.4%，这次是多记，两头都歪）。
3. **门柱回核依赖 card_id↔文件名机械互推，而 13/75（17.3%）精确失配**：三型（拼写分叉/中英双轨/`_v2` 后缀无源），13 行全部可模糊定位、0 行完全无源 ⇒ 不是幽灵行而是**命名双轨**；本席第一把尺因此直接对这 13 行"查无卡体"。
4. **nan 参与否决的跨族分裂**：comparison 族 9 行含 `oos_sign_flip ic_delta nan`，其中 **6 行（rows[66]-[71]）nan 是唯一 fail**；calibration 族同条件走 unjudged 零否决权。另 rows[44]/[45] 把 3 个"机判面待扩"键**同时**计入 fails 与 unjudged.numeric_keys_not_read（双记）。⇒ 已呈批 P-1，本席未动判据。
5. **ic_floor 合取长期单脚**：`ic_ir_min` 在 75 行中 **11** 行登记无机判面（全册面；本席初报 10 系子面计数，见 §4 更正） ⇒ 卡面 prose 的"RankIC≥0.02 且 IC_IR≥0.3"合取在这些行只检验了一半。⇒ 已呈批 P-2。

### 4 自我更正（旧案留册不删）

- 本席第一轮全册扫描（`.runtime/tmp/p09_1015_02_scan_all.py` 口径）曾报"**11 处 verdict 重算与分数行不符**"。实测证伪＝**本席的尺族盲**：该 11 行属 comparison／high_event 族，卡体 `pillars_numeric` 是另一两套键（`maxdd_improvement_min`/`sharpe_delta_min`；`event_gap_max_bp`/`event_t_stat_max`/`event_days_min`），本席第一把尺只编码了 calibration 五键，重算得空集被误读为"不符"。**分数册无此 11 处异常**；旧记录保留于此，不作 finding，不得进任何下游单。
- 同轮报"13 行卡体查无"经内容 grep 改判为命名双轨（观察 3），非卡缺失；`git log --since=2026-10-10 -- exam_cards/` 未见删除记录。
- **第二轮自检（引用回查）实测出的本席数错并已更正**：`ic_ir_min` 无面行数全册＝**11**，本席初报 10。根因＝第一把尺在"卡体精确定位失败"分支 `continue`，13 行未进入 umf 计数（62 行子面）⇒ 凡"全册计数"必禁在计数前 continue；复算口径＝直接对 `rows` 全 75 行走 `unjudged.numeric_keys_no_machine_face` 键判定（脚本 `.runtime/tmp/p09_1015_02_verify_claims.py`）。
- 同轮逐条引用回查全通过：rows[72]/[73]/[74] card_id 与读数逐位对合；nan-only 行集＝[66,67,68,69,70,71]；nan-any＝9 行；75/56/12（行/去重对象/多行对象）与 L1-S2 34 行均对；台账所引 7 条文件路径全部 EXISTS；SOP `:274`/`:305` 的 4.4 句逐字命中；L9 卡面 `ic_floor` 合取句逐字命中。分数册未被本席改动（sha256 前缀 c7e5b1f8bfb98ae2，bytes=105598，lines=3881）。

### 5 交付清单（本班实际产出）

| 件 | 内容 |
|---|---|
| pulse/independent_signals.md | 首版：pool-report 三态实测＋15 员成员表＋有效数"未获得/4.4 系未复现叙述"＋占领区摘要 |
| feedback/to_miners.md | 首单 5 条：家族收敛／楼图游标脱节／正交空白轴地图／mined_out 建议（待对照）／过闸账口径 |
| feedback/to_impl.md | 修改单修①-⑤＋[对照] 申请 1 条＋呈批草稿 P-1/P-2 |
| feedback/to_datasource.md | 缺数 3 条（suspend 自量 36 行/窗内 0 行；两张因子表零行；配对 IC nan） |
| iteration_history.md | 首班补记账 7 组对象（含 2 组超限上报） |
| p09_score_officer/checkpoint.md | 游标推到 rows[74] |

### 6 本班耗时与班限

- 冷启动 05:50（process_reaper 状态日志时戳）→ 本条写入实测 `date` 见下；**约 50 分钟，超 40 分钟班限**。
- 超时去向如实记：当日增量＝0 行，工时全部投在判卷面完整性（三口对账、75 行回核、尺盲自纠）与正交闸阻塞定性；本班**未**因此扩权做 ⑤/⑦⑧席写域。
## 2026-10-15 st-qoder-p09-1015-03 ｜ ⑨成绩官第三班（当日增量＝0 行；全 75 行 verdict 复现＝0 异常）

- 班次号依据：今日本席台账已有 01（st-probe-04mig-20261015，rows[74]）、02（st-qoder-p09-1015-02），本班取 03。
- **降级直改主区·原因登记（RULE-WORKTREE）**：与 02 班同因——本席改的是**共享追加型席位交接件**（三联单/迭代史/pulse/本台账），车道副本与主区并发写必互撞；防护＝逐件 `lock_files.py acquire`＋`safe_write_text` CAS＋只追加不改已有字节。⑩席可按 GW 计数审计本条。

### 1 判卷面（当日增量）

- **三证零增量**：册 mtime `03:37:20` 未变／bytes=105598 未变／sha256 前缀 `c7e5b1f8bfb98ae2` 与 02 班记录逐位同；机械加载 docs=2、rows=75（索引 0..74）⇒ `rows[75]` 起无新行，本班当日增量＝0 行，无新分数可判。
- **分数册落地面（本班新查，非转述）**：`exam_scores_v1.yaml` **不在 HEAD**，只活于主区 index（`git status`＝`A `）。队列在途两袋携带本册：`q-20261015-st-scorehome-20261014-0003`（03:05 建，blob `c14e6635…`＝104507 字节＝旧面）与 `-0004`（05:01 建，blob `c7e5b1f8…`＝**与本席判卷字节逐字节同**）。⇒ 判卷面有袋可落，但**前袋若先落地会把本册回退到 104507 旧面**，后袋才是保命袋（同 sid 后袋吞前袋在册，本席不代处置）。
- 队列与主区面：pending=88／processing=1／dead=118／done=770；头袋 `q-…-st-chfinalw2-20261015-0003` 已等 21893s＝**6.08h**。主区 index 对 HEAD 差分＝**359 A／910 D／29 M**（另含大批 R 重命名），本席判卷所依的两个动量卡体正处其中。

### 2 判卷面完整性：全 75 行族感知复现（超出"抽 3 行"保底）

- **本班第一把尺自犯族盲并已自证**：按 card_id 路径段分族复算得 23 行 MISMATCH；实测＝**尺错非册错**——`…/17_ind_volume009_high_event` 路径段写 `calibration`，卡体 `pillars_numeric` 却是 `event_*` 五键。改按**卡体 pillars 键集**定族重跑 ⇒ `verdict/fails 不可再现 行数 = 0`（75/75）。脚本 `.runtime/tmp/st-qoder-p09-1015-03/reconcile3_verdict_replay.py`。
- 真族分布（卡体键集面）：calibration 43／high_event 23／comparison 8＋三键变体 1＝75；路径段面则是 calibration 66／comparison 9 ⇒ **族名不可从 card_id 路径段取**（02 班尺盲的根因，本班量化）。
- 卡体锚点正解：按卡体**内部 `card_id` 字段**建索引 ⇒ **75/75 精确定位**；按文件名 stem join＝0/75。⇒ 02 班"13 行命名双轨只能模糊定位"实为 **join 键选错**，非册面缺陷（旧案留册不删，见 02 班 §3-观察3）。
- nan 否决面独立复量：nan-veto＝rows[17,44,45,66,67,68,69,70,71]（9 行），nan-only＝rows[66..71]（6 行）⇒ 与 02 班同集，两把尺交叉验证通过。

### 3 归因四分诊（本班开单，逐条带可 grep 证据）

1. **实现问题 → 修⑥**：含 `ic_ir_min` 柱的 43 行中 **41 行 `metrics.ic_ir=null`**，而册面只在 11 行（rows[31..40,72]）声明 `numeric_keys_no_machine_face`、`numeric_keys_not_read` 命中 0 ⇒ **30 行读空却零声明（静默）**。后果＝ic_floor 合取长期单脚且不可审计。
2. **实现问题 → 修⑦**：high_event 族 23 行卡体五键**逐键全同**，执行面却两套：`_v2` 卡（rows[41,42,43]）记 `oos_gap 反号`；非 v2 卡（rows[46..65]，20 行入账）只记 `oos 窗事件日 <200`、**根本没有 OOS 反号这根腿**。实测 16 行 OOS 反号 ⇒ **13 行方向否决不可见**（rows[46,47,51,52,53,54,55,58,59,62,63,64,65]）。verdict 不变（23 行全 fail），但方向信息丢失 ⇒ ③④席会误判"回补数据即可重考"（真只缺样本者＝rows[48,57,61] 三行）。→ 同批进 to_miners.md 方向单。
3. **判据问题 → 呈批 P-3（新条）**：卡面 `event_days_min: 200` 未声明作用窗（全窗／OOS 确认窗／两窗），两版执行各执一词且后者用样本闸顶掉方向腿。本席不改柱、不定窗。
4. **判据问题 → 呈批 P-2 材料上调**：单脚真分母＝**41/43（95.3%）**，非 02 班报的 11（那是"已声明"面）。本席未动任何判据字节。
5. **治理/并发 → 修⑧（P0 告警，非判卷缺陷）**：本班值守内考卡池 531→529→531（`entry_flow/L3/` 目录 mtime 07:00），rows[73]/[74] 两卡体在 07:02:08 被重写；`git status`＝`M `（staged 改动＋工作区曾瞬时缺件）。**门柱锚点可被并发摆布＝成绩不可复核**。本席未代修、未回滚（非本席写域），只取证呈 ⑩/⑤。
- pass→verified 升级与 TDM 挂接：本班**零执行**（增量 0 行且卡考主册 75 行全 fail、pass=0）；铁律 fail 永不升级。

### 4 结构性观察（家族级，本班 5 条）

1. **族名的真源在卡体 pillars 键集，不在 card_id 路径段**：路径段面 calibration 66 行里有 23 行是 high_event 尺；任何按路径段分族的判卷/审计尺都会把这两族的门柱混用（02 班"11 处不符"假案与本席"23 行 MISMATCH"假案**同因同族**，两轮都栽在同一个 join 面上）。
2. **分数册没有 HEAD 落点**：本席判卷依据的册与其卡体锚点当前都只存在于主区暂存面（359 A／910 D 混合池）＋队列 blob。册若被巡检按 HEAD 复位，75 行判卷面与游标锚点同时归零，且**这是宪法 §9.4"无主 staged 复位"条款的正常执行路径**，不是事故才发生。
3. **ic_floor 合取单脚面比在册叙述大 3.7 倍**：41/43 而非 11；且 30 行为静默缺失——"已声明的缺陷"与"实际存在的缺陷"差 3 倍，说明写分工具的 `unjudged` 面只覆盖它自己认识的键，不覆盖它没读到的键。
4. **同一套冻结门柱可以有两套执行**：high_event 23 行门柱逐键全同，而 `event_oos_gap_same_sign` 只在 3 个 `_v2` 行入账、其余 20 行由"OOS 窗样本下限"顶位，致 13 行方向否决隐身——**门柱一致 ≠ 判卷一致**；且该样本下限施于哪一窗卡面未写（呈批 P-3）。
5. **迭代预算面本班零新增**：分数册 rows 计数 75 未变、无新 run_id 入册；02 班已记的超限对象（熔断 07/07b 各 4 轮、L2-02/03/04-2 各 3 轮）本班未再消费。

### 5 交付清单（本班实际产出）

| 件 | 内容 |
|---|---|
| feedback/to_impl.md | 修⑥⑦⑧ 三条＋修② 正解改写（join 键改卡体 card_id 字段）＋呈批 P-2 材料更正＋呈批 P-3 新条 |
| feedback/to_miners.md | 方向单 2 条：high_event 13 行"样本不足"文案遮蔽方向否决／过热高事件族收敛（t_stat 0/23 达标） |
| pulse/independent_signals.md | 日更：pool-report 三态复测（工具可跑、`--pool` 缺 date,sig 池、全仓 date,sig CSV＝0）⇒ 产腿仍阻塞，抄修⑤ |
| iteration_history.md | 本班轮次记账（增量 0，无新对象轮） |
| p09_score_officer/checkpoint.md | 游标维持 rows[74]，记本班三证与在途双袋事实 |

### 6 本班耗时与班限

- 冷启动 06:50:42（process_reaper 状态日志时戳）→ 本条写入实测 `date`：07:14:02；**约 23 分钟**（班限 40 分钟，班限内）。
- 超时/工时去向如实记：当日增量＝0 行，工时投在**判卷面完整性**（全 75 行族感知复现、分数册与卡体锚点的存活面取证、两把尺交叉验证与自我更正）；本班未因此扩权做 ⑤/⑦⑧席写域，未动分数册与判据字节。
### 7 下一班配方（本班实测堵点，勿重烧）

- 本席恒定指令未含"注册会话"一步 ⇒ 首跑 `git_commit.py --enqueue` 被 **PREFLIGHT BLOCKED** 双拦（`SESSION-REQUIRED`＋`WORKTREE-REQUIRED`，实测 12.8s 白烧）。02 班交付至今未入袋，疑同因（其六件仍 `AM`/`MM` 面）。
- 正解两步（未弱化任何门）：
  1. `SessionRegistry().register('st-qoder-p09-<MMDD>-<NN>', pid=0, held_files=<本席六件>, task_files=<同>)` ＋ `heartbeat(sid)` ⇒ 实测 `heartbeat: True`（短命进程必须 pid=0，否则心跳守护启动即退）。
  2. 重跑 `git_commit.py --session <sid> --files "<逗号分隔一件一径>" --allow-non-worktree --enqueue --message "…"`（`--files` 只收**一个逗号串**，空格分隔会 arg-error；`--allow-non-worktree` 系该门自述处方"2026-08-13 裁定 AI 可默认"，非本席加旗）。
- 本班实测入袋：`q-20261015-st-qoder-p09-1015-03-0001`（files=6）。队列现况＝pending 88／dead 118，头袋已等 6.08h ⇒ 本班**未**轮询等待，落地核实交下一班：`git log -1 --name-only` ＋ `git show --stat <落地 commit>` 对六件逐件读回。
- 本班最终耗时（实测 `date` 见下）：07:17:39，冷启动 06:50:42 起算 ≈ 27 分钟（班限 40 分钟，**超**）。超时去向＝判卷面完整性复算（全 75 行族感知）、修⑦/呈批 P-3 的 13 行方向否决取证、考卡池并发摆布（531→529→531）定性与两次提交尝试。
## 2026-10-15 ｜ st-qoder-p09-1015-04（⑨成绩官第四班：当日增量＝8 行，全部判卷＋分诊）

- 班次号依据：本班前本席台账在册班＝01（`st-probe-04mig-20261015`）、02、03（`st-qoder-p09-1015-03`，其 §7 交接＋双袋 `…-03-0001/-0002` 于 07:17:04/07:18:14 入袋，游标记录已写完＝上一班已完工）⇒ 本班取 04。
- 防重入两址同读（在册教训 `p07-seat-cursor-two-locations`）：旧址 `docs/_working/…/p09_score_officer/checkpoint.md`＝游标 `rows[74]`（07:14 更新，较新）；新址 `docs/04_research_records/cross_domain/automation_campaign/p09_score_officer/checkpoint.md`＝`cursor: 未开始`（03:09 搬迁桩件，陈旧）。本班按**较新的旧址**判班，落地面亦为旧址。

### 1 判卷面（当日增量 100%）

- 锚点：分数册 `.runtime/tmp/st-qoder-p09-1015-04/score_snapshot.yaml`＝主区磁盘快照，**sha256 前缀 `24ef736d819d0be1`／115036B／83 行／mtime 07:17:15**（03 班三证面 105598B/75 行/03:37:20 已被超越）。本班只读，册面字节未动。
- 增量＝rows[75..82]＝`p07a-agg8-20261015` 批（node `TDM-E-L1-S2`，8 张卡体文件在 `exam_cards/entry_flow/L1/`，按卡体内部 `card_id` 字段 join **8/8 精确定位、0 未命中**）。
- **门柱一票否决机械核对：增量行 verdict 不可再现＝0/8**。复算尺＝`.runtime/tmp/st-qoder-p09-1015-04/reconcile4_delta.py`（沿用 03 班族感知口径）。8 张卡体 `pillars_numeric` **逐键全同**＝`{mono_spearman_min:0.6, ic_mean_min:0.02, ic_ir_min:0.3, regime_same_sign:true, oos_same_sign:true}` ⇒ 族＝calibration。
- 逐行对合（分数行 fails 原文 ↔ 我算违例柱）：rows[75,77,79,81,82] 唯一 fail＝`oos_sign_flip`＝我算 `oos_same_sign` 单柱违例；rows[80] 两根＝`regime_sign_flip`＋`oos_sign_flip`＝我算同二柱；rows[76,78] `fails=[]`＝我算零违例。**6 fail／2 pass，无一格走样。**

### 2 负结果如实入册核对（exam_policy §5.1 全量入册）

- ⑦席封闭族申报＝8 卡（`docs/_working/automation_campaign/p07_examiner_a/ledger.md` §二"出分明细（8/8）"）；册面实际入册＝8 行；盘上卡体＝8 枚（`ls` 命中 `TDM-E-L1-S2__calibration__4[0-7]_agg_*`）⇒ **三面对合 8/8/8，无缺席、无中途加条目**。
- 试次留痕：⑦席报 `trial_ledger_registry.yaml` 本机新增 8 条（`recorded_by=st-qoder-p07-1015-01`，`kind=exam_card`，`n_trials=1`），分数行 `ledger_warning` 零命中；该热册**未随袋**（其移交①按在册"袋=整档快照"教训）⇒ 账面差风险由 ⑩ 席追认，本班不代改热册。
- 卡面翻转腿：⑦席自报 8 张 `preregistered → examined` 且 `lineage.run_id/score_row` 回填（02 班修①在该路已修）。

### 3 归因四分诊（6 条 fail 全部路由，无一条无归处）

| 分数行 | 读数（可 grep） | 路由 | 单据 |
|---|---|---|---|
| rows[75] `40_agg_lu_count_level_fwd10` | bull=+0.0024／bear=+0.1633，oos=−0.1102 | 信号真无效（level 形态） | 方向单第 1 条（to_miners.md 04 班） |
| rows[77] `42_agg_lu_ratio_level_fwd10` | bull=+0.0062／bear=+0.1711，oos=−0.0979 | 同上＋重复件（与 rows[75] corr=0.9949） | 方向单第 1、3 条 |
| rows[79] `44_agg_avg_abs_ret_level_fwd5` | bull=+0.0114／bear=+0.1670，oos=−0.0643 | 信号真无效（本体级候选） | 方向单第 2 条 |
| rows[80] `45_agg_avg_abs_ret_level_fwd10` | bull=−0.0200／bear=+0.1958，oos=−0.0954 | 判据问题（regime 柱无过零带） | **呈批 P-4**（to_impl.md §4） |
| rows[81] `46_agg_avg_abs_ret_z20_fwd5` | IS bull/bear 同号（+0.1281/+0.1272），oos=−0.0324 | 需对照验证 | **[对照] 单**（to_impl.md §3） |
| rows[82] `47_agg_avg_abs_ret_z20_fwd10` | IS 同号（+0.1663/+0.1183），oos=−0.1080 | 需对照验证 | 同上 |
| （实现腿，跨全部 8 行） | `ic_ir=null` 8/8；`net_bucket_medians` 全 NaN＋`round_trip_cost_bp` NaN 8/8 而 `mono_spearman` 有值 | 实现问题 | 修改单 **修⑨**（新）、**修⑥ 追加面**（51/49/19/30） |
| 缺数单 | — | **本班 0 条**，理由：本批零 CH（⑦席 ledger"单卡耗时 0.39–1.70 秒，纯本地序列，零 CH"）、8 枚序列 `nan=0` 覆盖 2019-02-11..2026-10-12 | 无 |

### 4 pass 行红线核查与晋级处置（fail 永不升级）

- **rows[76]/[78]：判"不升 verified"，两腿独立成立，随卷呈交**：
  1. `ic_ir_min=0.3` 这根柱**从未被检验**（`metrics.ic_ir=null`，册面自挂 `numeric_keys_no_machine_face`；⑦席 ledger §四亦自证"引用本批 pass 分数时禁叙述成门柱全过"）。门柱合取只测一半 ⇒ 预注册阈值未"全过"，不满足 exam_policy §6「达标」出口第一条件。
  2. 成本/净口径面未产（`net_bucket_medians` 全 NaN、`round_trip_cost_bp` NaN）而 `mono_spearman` 有值 ⇒ 单调柱是毛面读数，违 exam_policy §3.2 双口径声明纪律（修⑨）。
- TDM 挂接记录：**本班零升级、零新挂接**（无 pass 行过两腿）；6 条 fail 按铁律永不升级。未写任何 DB/注册表面（属⑥/⑤写域且本席未越）。
- 另记 exam_policy §4「暂定档」纪律：本批为日线聚合派生面，§4.1 在册事实（`kline_daily.adj_factor` 断供→一切日线结论=暂定档，禁当最终档升级）本班**未实查复权链现状**；因升级已被上面两腿挡住，该腿留待下一班或 ⑥ 席实查后补账，本席不拿未实查条款当已用判据。

### 5 结构性观察（家族级，本班 3 条）

1. **S-1「bull 段 IC≈0 是 OOS 翻转的前兆尺」**：4 张 level 卡的 bull 段 IC＝+0.0024/+0.0062/+0.0114/−0.0200（rows[75,77,79,80]）而 bear 段＝+0.1633/+0.1711/+0.1670/+0.1958 ⇒ IS 正 IC **几乎全由 bear 段贡献**，OOS 四张全反号；两张过闸卡（rows[76,78]）bull 段＝+0.1028/+0.0980 与 bear 同量级。⇒ 观察尺（非判据，本席不动门柱）：同族新卡若 bull 段 IC 落在 ±0.02 内，先按"构成伪影"预防性看待并登记。
2. **S-2 共线性簇＝名义 8 卡实占 2 轴**（机读产出，pool-report 权威输出）：`lu_count_z20↔lu_ratio_z20=0.9998`、`lu_count↔lu_ratio=0.9949`、level↔z20=0.7399–0.7743，PR=2.1272。⇒ 挖矿"挖到 8 个"与"占 2.13 个轴"的差＝生产线的计量口径问题（SOP §4 自我迭代回路与 v1.4.0 正交挖矿制），已按方向单第 3 条发单；SOP §3⑨ 与 §174 明列"环节层家族共线性聚类=⑨席结构性观察职责"，本班为该职责**首次给出机读数**。
3. **S-3 分数册存活面在值守内被摆布（P0 接续修⑧）**：本班开窗时 105598B/75 行（03 班三证面），07:17:15 变 115036B/83 行；pending 内 5 个 `st-scorehome` 袋无一携带现值面（`-0003`＝74 行旧 blob `c14e6635`、`-0004`＝75 行 `c7e5b1f8`、`-0005/-0006` 不含该册），且 `git status`＝`AM`（index 落后磁盘）。⇒ 判卷锚点仍无落点，**先落地者会把本班刚判的 8 行（含 6 条负结果）整档洗掉**。本班只呈交不代修。

### 6 交付清单（本班实际产出）

| 件 | 内容 |
|---|---|
| feedback/to_miners.md | 方向单 3 条（形态层收敛／本体层收敛建议／正交计量口径告警） |
| feedback/to_impl.md | 修改单 修⑨（新）＋修⑥/修⑧ 追加面＋**修⑤ 正解改写**（一列名之差，附绕行件）＋[对照] 单 1 条＋呈批 P-4 新条＋P-2 代价更新 |
| pulse/independent_signals.md | PR 与相关矩阵**首次机读产出**（2.1272/6 员/1855 共同日）＋占领区摘要＋空白轴地图维持 |
| iteration_history.md | 8 个新对象首考轮次记账＋预算汇总 |
| p09_score_officer/ledger.md | 本日报 |
| p09_score_officer/checkpoint.md | 游标推 `rows[74] → rows[82]` |

### 7 耗时与班限

- 冷启动 07:19:37（python 版本实测时戳）→ 本条写入实测 `date`：07:45:14（≈25.6 分钟，班限 40 分钟）。
- 工时去向：判卷 8 行（含快照与尺复用）＋正交实测绕行 1 次（13 员池红→6 员池绿）＋分数册三面取证＋开单。本班**未**扩权改码、未动分数册与判据字节、未跑考试。

### 8 下一班配方（本班实测，勿重烧）

- 会话注册两步沿用 03 班 §7（`SessionRegistry().register(sid, pid=0, held_files=6, task_files=6)`＋`heartbeat`）；本班补两坑：①`register()` **无 `task=` 形参**（照抄会 TypeError 后静默降级成不带 held_files 的注册，preflight 照样红）；②re-register 触发 rate guard（`window=1860s`）⇒ **一次注册带全参数**，别二次补写。
- claim 六件：`lock_files.py acquire` 全部成功（TTL 30 分钟）；本班实测 `lock_files.py cleanup` 于 07:19 清掉 5 枚死锁（含 `p10_line_lead/ledger.md` 与 4 张在途考卡）并 SALVAGE 了 `st-qoder-p01-1015-04` ⇒ 进场即清是有效的，别跳过。
- 下一班锚点：首件读分数册磁盘面（先 `sha256sum` 对 `24ef736d…`，若已变则按新面重取游标），只判 rows[83] 起新行。**务必先核 §5 S-3**：若 `st-scorehome` 任一旧袋先落地（册面回到 74/75 行），那是负结果被洗的事件，立即上报而非重判。

### 9 事件登记（本班值守内，外来重置/删除）

- 07:38:39 本班六件落笔完成；07:42:15 入袋 `q-20261015-st-qoder-p09-1015-04-0001`（files=6，其中 ledger/checkpoint 两件吸到的是 **10-14 21:54 的模板面**＝本席日报在那一刻已被外来重置覆盖）；**07:43:45 本席座位目录内 `ledger.md`/`checkpoint.md`/`instruction.md` 三件被删除**（`ls` 仅剩 00:39 的 `scope.md`）。03 班修⑧（并发存活面）由"册面不在 HEAD"升级为"席面件被摆布"，非本席写域可修，本班只登记并复原，未追查肇事会话（属⑩/维护班写域）。
- 复原面来源（双证在册）：02/03 班案卷＝队列 blob `.runtime/commit_queue/blobs/36db4aeb447154d8b3dabacd76973b6d0341221a7543919dcf8cb4f949f5155c`（24114B，07:18，＝03 班袋 2 严格超集面）与 `…/266bf66d7092b1d51b356428ebfd68709454b47ff3cabcb40c9b3e4811cf6673`（1933B，07:17）；本班 04 段＝`.runtime/tmp/st-qoder-p09-1015-04/write_deliverables.py` 内 BLOCKS 原样重放。
- 本班四件实体交付（`to_impl.md`/`to_miners.md`/`pulse/independent_signals.md`/`iteration_history.md`）盘上完好（mtime 07:38:39）。

- 本班最终耗时（实测 `date`=07:45:14，冷启动 07:19:37 起算）≈ **25.6 分钟**（班限 40 分钟）。§7 的 18.9 分钟＝落笔时戳非终值。**本件为被删后复原面，由袋 2 承接**（袋 1 的 ledger/checkpoint 吸到模板面）。
## 2026-10-15 ｜ st-qoder-p09-1015-05（⑨成绩官第五班：当日增量＝0 行；本班主产出＝**更正并扩面 修⑧**＋判卷尺复跑）

- 班次号依据：本班前本席台账在册班＝01（`st-probe-04mig-20261015`）、02、03、04（`st-qoder-p09-1015-04`，其 checkpoint 游标记录已写完＝上一班已完工）⇒ 本班取 05。
- 冷启动三步实测：`python --version`=3.12.8；`lock_files.py cleanup` 清 4 枚死锁（含本席 02 班域 `p02_databuilder/ledger.md`、`feedback/unblocked.md`）；`process_reaper --status` source=live／last_run=08:18:20／killed=0 ⇒ 允许写。防重入：04 班游标 `rows[82]` 已推、`last_batch` 自述完工 ⇒ 接手。

### 1 当日增量（三证＋机械行数，一律对 04 班在册面比）

- 磁盘面 **sha256 `24ef736d819d0be1aa943fcd1eaf7aa311eb50d775827455011c33f916c55758`／115036B／mtime 10-15 07:17／`safe_load_all` doc1.rows=83** ⇒ 与 04 班三证逐位同＝**册面自 07:17 起零新增**。
- 游标 `rows[82]`＝末行 ⇒ **本班增量＝0 行，判卷工序空跑**（不编造判卷量）。⑦席 ledger 面 07:44、⑧席 07:52 之后无新出分。
- 复跑尺＝`.runtime/tmp/st-qoder-p09-1015-04/reconcile4_delta.py`（族感知口径，本席原样正文跑）⇒ **8 行 verdict 全再现**：pass=[76,78]、fail=[75,77,79,80,81,82]、`ic_ir` 读数缺失 8 行、`net_bucket_medians` 全 NaN 8 行、`round_trip_cost_bp` NaN 8 行、bull IC≤0.02 行=[(75,0.0024),(77,0.0062),(79,0.0114),(80,-0.02)]。verdict 不可再现＝**0/8**。

### 2 归因四分诊（本班 0 条新 fail ⇒ 零新开单）

- 新 fail＝0 ⇒ 方向单／修改单／缺数单／[对照] 单**均零新开**（净零）。在册待办不变：04 班方向单 3 条、修⑨／修⑥追加面、[对照] 单 1 条、呈批 P-4／P-2 更新、02 班修⑤。
- 本班唯一开单动作＝**对 04 班 修⑧ 的更正兼扩面**（见 §5 与 to_impl.md「修⑧ 追加面（05 班）」），属判卷面事实更正，非新问题。

### 3 pass 行红线与晋级（无新 pass 行）

- 本班 0 新 pass 行 ⇒ 0 升级、0 TDM 新挂接。04 班两腿判据维持（`ic_ir_min` 柱从未检验＋净/成本面全 NaN）；复跑尺今日再证一次：rows[76]/[78] 的 `ic_ir=None` 与 `net_bucket_medians` 全 NaN 仍在册未修。

### 4 迭代史

- 新对象＝0 ⇒ 本班**零轮次消费**；在册超限面不变（07/07b 各 4 轮超限、L2-02/03/04-2 各 3 轮达上限）。详见 iteration_history.md 05 班段。

### 5 结构性观察（本班 3 条，首条即更正）

1. **S-1 修⑧ 更正兼扩面（P0）**：①04 班报"pending 内 5 个 `st-scorehome` 袋无一携带现值 83 行面"——该句按 `st-scorehome` 字面成立，但**扫面窄了**：本班全 pending 面（102 袋）重扫，携带 `exam_scores_v1.yaml` 的共 **3 袋**，其中 `q-20261015-st-qoder-p07-1015-01-0001`（07:30:18，action=modify）的 blob=`24ef736d819d0be1`＝**恰为磁盘现值 83 行面** ⇒ 现值面**并非在存档之外**，⑦席自己的袋就带着它。②反向扩面更严重：本班实测 `git ls-tree -r HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**，而 index＝**30 件**（`exam_scores_v1.yaml`＋另 11 册成绩册＋8 份 .md  twin＋名册等）⇒ **整个分数册永久区从未落地**，不止 04 班所报的一册。③同一路径并存三面：磁盘 83 行／index `c7e5b1f8`＝75 行／`st-scorehome-0004` 同带 75 行、`-0003` 带 `c14e6635`＝104507B／**1 doc／74 行**旧面 ⇒ 落地顺序决定终面，任一日志序上后到的旧面即洗掉 04 班刚判的 8 行（含 6 条负结果）。本席未 requeue、未回滚、未代修（属⑩串行/属主班写域）。
2. **S-2 跨席读面已经分叉（可 grep 实证，非推测）**：⑩席 `pulse/queue_depths.md:24`（07:52）写"卡考主册 exam_scores_v1.yaml docs=2／rows=75"＝**读的是 index 面**；本席同刻读磁盘＝83 行。两席都在"如实报实测"，但同一册得到两个不同行数且差值恰为 04 班新判的 8 行。⇒ 生产线缺"读面声明"（读 index 还是读磁盘）；已按 S-1 一并写进 to_impl.md 修⑧追加面供⑩裁定，本席不替⑩改口径。
3. **S-3 因子池载体表"有写者、零行"＝15 员池 PR 的当前唯一根因**：本班复测 02 班在册面（to_datasource.md:17，未重复开单）——`c1_market.factor_signal`=**0 行**、`c1_market.factor_feature_value`=**0 行**（同批 `DatabaseService().get_clickhouse_conn()` 只读，非读路故障）；**新事实**＝写者模块确实存在且指向该表：`src/zephyr/factor/core/batch_output/buffer.py` 头部 `[DEPENDENCIES] zephyr.data.ch_writer; zephyr.shared.contracts.factor_signal`。⇒ 02 班留的选择题（"设计未启用" vs "断供"）现可收窄为**生产腿从未跑过**，不是源无数据。旁证：另三张信号表有行（`alt_regime_signal` 24,590／`alt_stock_comment_signal` 88,372／`market_signal_history` 329）但列形制为 (symbol, signal_id, score…)，**不是** 15 员池的 factor_id 序列面；`ART_ROOT=docs/_working/integrated_backtest/` 至今仍不存在（`ibt_runner.py:45-47`，本班实测）。

### 6 首次值日加做（15 员池 pool-report）复测结论

- 仍**未能**产出 15 员池 PR：物化腿无源（§5 S-3）＋13 员直跑共同日=0（04 班附带症状未修）。本班未跑考试、未实现物化（⑤席写域）。agg8 6 员池 PR=2.1272 面维持。产出与绕行件登记见 `pulse/independent_signals.md` 05 班段。

### 7 自检两轮（抽 3 行回卡体核对门柱未走样）

- 轮一：复跑 04 班尺（正文原样）⇒ 8 行 verdict 全再现、无一条走样（读数见 §1）。
- 轮二：抽 rows[80]/[81]/[82] 回卡体逐字核对——三卡 `pillars_numeric` 均＝`{mono_spearman_min:0.6, ic_mean_min:0.02, ic_ir_min:0.3, regime_same_sign:true, oos_same_sign:true}`（尺打印的 `card_file` 面），记录 fail 集与门柱合取一致：rows[80] `regime_sign_flip`＋`oos_sign_flip`、rows[81]/[82] `oos_sign_flip`；`ic_ir_min` 三行均判"未检验"（`unj`）而非"过"。**本班未动任何门柱数值与分数册字节。**

### 8 交付清单与耗时

- 件：`p09_score_officer/ledger.md`（本件）、`checkpoint.md`（游标不变＋更正事实交接）、`feedback/to_impl.md`（修⑧ 追加面＝更正兼扩面，零新开号）、`feedback/to_datasource.md`（02 班 :17 行的复测印证一行，零新开号）、`pulse/independent_signals.md`（05 班日更）、`iteration_history.md`（零消费记账）。
- 耗时：冷启动 08:18:32 → 判卷尺复跑＋前四件落笔实测 `date`=**08:29:37**（≈11.1 分钟）；六件齐＋两处更正实测 08:30:46（≈12.2 分）；§9 堵点与降级登记落笔实测 **08:33:31（累计≈15.0 分钟，班限 40 分内）**。入袋读数只写本班终报，不为记一个袋号再开第二袋（同六件路径的后袋会静默取代前袋＝本席 S-1 三面靶面，勿自造第四面）。中途一度按体感钟在初稿写下「超班限」＝自犯（本席体感钟快约一倍，在册教训复现），已在本条以实测值更正。耗时去向：CH/DatabaseService 接口三轮试错（`query`→`Client.query`→`execute`，`clickhouse_driver.Client` 无 `query`）＋馆级三面取证＋尺复跑。
- 下一班配方：先 `sha256sum` 对 `24ef736d…`（磁盘面）；**判卷前先 `git show :…/exam_scores_v1.yaml` 与磁盘面比行数**，两面不等即属 S-1 事件，先报⑩再判；15 员池 PR 复测前先读 to_datasource.md:17＋本班 §5 S-3，勿再烧第三轮同一无源面。
### 9 堵点与主区降级登记（RULE-WORKTREE §10 显式申请制留痕）

- 首投 08:31:54 被锁外预检拦 2 项：①`SESSION-REQUIRED`＝本席首次 `register(pid=0, held_files=[6 路径], task_files=[6 路径])` 返回了 SessionInfo，但首投预检时（08:31:54）`.runtime/session_registry/` 无本席 shard、legacy 册 `grep -c` 命中 0；本班 08:33 二次以同形参 `register()`＋`heartbeat(sid)`（返回 True）后方出现 shard `.runtime/session_registry/st-qoder-p09-1015-05.json`；冷启动期 `lock_files.py cleanup` 同批打印过 `failed to load legacy registry: [Errno 13] Permission denied: .runtime\session_registry.json` ⇒ 判为"注册写面被并发锁挡过一次"，非本席漏调。**处方给下一班：注册后必须 `get_session(sid)` 回读＋`ls .runtime/session_registry/<sid>.json` 双证，别拿 register 的返回值当已落盘**（同型静默降级＝本席在册教训"降级态与未触发同形"）。另注：04 班在册形制 `held_files=6`（整数）与本班实测形制 `held_files=[6 个路径]`（list[str]，`session_concurrency.py:register` 签名）不同，照抄整数会被下游当空集合。
- ②`WORKTREE-REQUIRED`＝主区直改且存在其他活跃 session。本班取门提示在册逃生旗 `--allow-non-worktree`（旗注原文＝"2026-08-13 裁定 AI 可默认"）。**降级原因登记**：⑨席=恒定指令班，本批六件全为 `docs/_working/automation_campaign/` 追加型信箱件（前四班同形制同路径，03/04 班各袋 files=6 已按此路走通）；本班写域不含 src/，无并发改码面。claim 六件已于 08:20 前全部到手（TTL 30 分），非无 claim 直改。GW 计数与周审计由门自动登记。
- 二投 08:34:30 又被拦 1 项＝`CLAIM-CHECK-BLOCKED: MESSAGE-CLAIMS-CODE-BAG-EMPTY`（消息引用代码路径 `factor/core/batch_output/buffer.py` 而袋内 0 代码件）。本班取门给的处方②（纯文档/登记类提交加 `[docs-only]` 显式申报），未删引用、未弱化判据、未加白名单——本席六件确全为 `docs/_working/` 追加型，申报与事实一致。⇒ 三投带 `--adopt-prior-work`（首二投的 finally 已释放 claim，文件仍 staged，不带此旗重 claim 会把 staged 差异判外来＝FOREIGN_CHANGE 恶性循环，在册教训）。
- 三投 08:36:12 `SESSION-REQUIRED` **复发**（08:34:30 该门已过、走到 CLAIM-CHECK ⇒ 注册曾真实生效）⇒ 本席会话项在 08:34:30–08:36:12 之间被摘除＝**注册面 flapping**，非本席漏注册。四投 08:37:33 把 `register`＋`heartbeat`＋**双读面自证**（`SessionRegistry().get_session`＝True 且 `GitCommitGateway().registry.get_session`＝True，后者＝预检实际读取面）与入袋串成一条命令压缩时间窗 ⇒ **ENQUEUED `q-20261015-st-qoder-p09-1015-05-0001`（files=6）**。本班台账 §9 的这两次更正与入袋同在一袋内（未为记袋号另开第二袋，理由见 §8 末）。**给⑩/维护班的面级线索**：本席 shard `.runtime/session_registry/st-qoder-p09-1015-05.json` 曾于 08:33 出现、08:36 前消失，同目录他席 shard（03/04/p10）mtime 被心跳守护持续刷新——"pid=0 的逻辑会话是否被某条清理/孵化收割路数按 pid 认人摘掉"与本席在册旧案 `reaper-incubation-kills-runtime-core-20260925`（真缺陷＝孵化收割按 PID 认人）同族，本班不自查自修（非本席写域），只登记观测。
- 本班**未**用 `--allow-overlap`（那是绕 SESSION/CLAIM 两门的另一旗，本席注册与 claim 皆真实存在，无须绕）。

## 2026-10-15 ｜ st-qoder-p09-1015-06（⑨成绩官第六班：当日增量＝0 行；本班主产出＝**全册族级材料度尺＋在册四单复测＋轮次账直测**）

- 班次号依据：本席台账今日在册班＝01（`st-probe-04mig-20261015`）、02、03、04、05 ⇒ 本班取 **06**。
- 冷启动三步实测：`python --version`＝3.12.8（实测 `date`＝08:40:44）；`lock_files.py cleanup` 清 4 枚死锁（含他席 `p03_miner_lib/ledger.md`+`checkpoint.md` 两件、一张在途考卡、一份热 yaml）并 **SALVAGE 死会话 `st-qoder-p07-1015-02` 遗物**（merge=skipped／stash=0件／释放claim=0）；`process_reaper --status` source=live／last_run=08:40:53／killed=0 reported=1 ⇒ 允许写。
- ⚠ 环境面如实上报（非本席写域，交 ⑩）：冷启动实测 `watermark.commit_pct=`**90.76%**（commit 已用 92.61/102.04 GB）、`ram_used_pct`=68.5、`cpu_pct`=64.5、`degraded=True`、`breached=['ALERT-SYS-003']`、`worktree_changes=`**5390**（>50 并行漂移告警）。本席在册旧案 `mem-commit-limit-incident-20260915` 的"起批前先读 commit_pct"今日量出 90.76% ⇒ 本班全程**不起并发批**、单进程只读、零 GPU 动作。
- 防重入：05 班游标 `rows[82]` 已推、其 checkpoint 段自述"六件齐＋两处更正终值"＝完工 ⇒ 接手。
- **降级直改主区·原因登记（RULE-WORKTREE §10 显式申请制）**：本班六件全为 `docs/_working/automation_campaign/` 追加型席位交接件（共享追加面，车道副本与主区并发写必互撞，02–05 班同形制同路径）；本席写域不含 `src/`。防护＝六件全部 `lock_files.py acquire`（实测 6/6 到手，TTL 30 分）＋只追加不改已有字节＋改后结构计数自证。GW 计数与周审计由门自动登记。

### 1 当日增量（三证＋机械行数，一律对 04/05 班在册面比）

- 磁盘面 **sha256 `24ef736d819d0be1aa943fcd1eaf7aa311eb50d775827455011c33f916c55758`／115036B／mtime `2026-10-15 07:17:15`／`yaml.safe_load_all` docs=2、doc1.rows=83** ⇒ 与 04 班、05 班三证**逐位同**＝册面自 07:17 起零新增。
- 游标 `rows[82]`＝末行 ⇒ **本班增量＝0 行，判卷工序空跑**（不编造判卷量）。⑦/⑧席自 07:17 后无新出分。
- 读面声明（遵 05 班 S-2 建议，本班起每班落字）：以上＝**磁盘面**；同刻 `git show :<册>`＝**105598B／sha `c7e5b1f8bfb98ae2…`＝75 行面（index）**；`git show HEAD:<册>`＝**fatal: not in 'HEAD'**。三面差值仍为 04 班新判的 8 行。

### 2 判卷机械核对与自检两轮（本班把回核面**从 calibration 一族扩到三族**）

- **轮一**（复用在册尺，正文原样跑 `python .runtime/tmp/st-qoder-p09-1015-04/reconcile4_delta.py`）：04 班 8 行 verdict **全再现**＝pass `[76, 78]`、fail `[75, 77, 79, 80, 81, 82]`，`ic_ir` 读数缺失 8 行、`net_bucket_medians` 全 NaN 8 行、`round_trip_cost_bp` NaN 8 行、bull IC≤0.02 行=`[(75,0.0024),(77,0.0062),(79,0.0114),(80,-0.02)]` ⇒ **verdict 不可再现＝0/8**（04→05→06 三班第三次同面再现，属**判卷**复跑非**考试**，不计轮次）。
- **轮二**（抽 3 行回卡体，选前两班从未回核过的两族＝02–05 班只回核过 rows[72..74]/[80..82]，全在 calibration）：
  1. **rows[8] `TDM-E-L9-A04/calibration/02_估值ERP分位日增量`（calibration 早期行）**：卡体 `pillars_numeric`＝{mono 0.6, ic_mean 0.02, ic_ir 0.3, regime_same_sign, oos_same_sign}；独立重算＝ic_mean +0.0467 过、mono 0.9030 过、regime bull +0.0457/bear +0.0945 同号过、oos −0.00475 对 IS +0.0467 **反号→唯一违反**，与分数行 `fails=["oos_sign_flip oos=-0.0048 is=0.0467"]` 同键同源 ⇒ **门柱未走样**。⚑ 新取证：该行 `unjudged` 整块＝**null**（连 `ic_ir_min` 读数 None 都没申报）＝03 班修⑥"静默读空"面的**具体逐行标本**（此前只报过计数）。
  2. **rows[48] `TDM-E-L1-S2/calibration/19_ind_mom030_high_event`（high_event 族首例回核）**：卡体五柱＝`{event_gap_max_bp:0.0, event_t_stat_max:-2.0, event_days_min:200, event_oos_gap_same_sign, event_regime_gap_same_sign}`；三条 fail 均可由卡体复算——`is_gap_bp 3.86 > 0.0`✓、`t_stat 1.783 > -2.0`✓、OOS `n_event=165 < 200`✓；另两根柱复算判过故未记 fail（`oos.gap_bp=+20.81` 与 `is_gap_bp=+3.86` 同号✓；`regime_gap` bull +12.01／bear +0.22 同号✓）⇒ **门柱未走样**。⚑ 新取证：柱名与 fail 串**不同名**（`event_gap_max_bp`↔"is_gap_bp"、`event_t_stat_max`↔"t_stat"、`event_days_min`↔"oos 窗事件日"），回核**必须人工映射**，而卡体 `mapping_note` 自述"prose↔numeric 映射无在册真源（词表立法工单对象）"⇒ 本席把"该族回核可机械化"的前提补齐为工单证据，不自建映射表。
  3. **rows[66] `TDM-X-R1-01/comparison/07_…五态仓位锚定版`（comparison 族首例回核）**：卡体八柱＝`{maxdd_improvement_min:5.0, maxdd_improvement_vs_no_hysteresis_min_pp:1.0, sharpe_delta_min:-0.1, whipsaw_roundtrip_ratio_max:1.0, missed_crisis_trigger_max:0, turnover_delta_annual_max:8.0, cost_tier_bp_required:40.0, oos_same_sign:true}`；分数行 `fails` **只有 1 条**＝`oos_sign_flip ic_delta nan（配对 IC 面样本不足）`，且 `numeric_keys_not_read=[]`、`numeric_keys_no_machine_face={}` ⇒ 除 `oos_same_sign` 外**七根柱在本行既无评估记录也无未评估申报**；`metrics.arm_open.oos_ic`＝**NaN**、`arm_open.regime_ic.bear`＝**NaN**（nan 来源实测到位）。⇒ 本行**不能判"门柱未走样"**：不是算错，而是**该行没有任何一根实质柱被检验过，verdict 由"读数不可得"单独决定**。复证在册 P-1（02 班），本班以逐行标本＋nan 来源补强，未改判、未动字节。
- 一票否决总线核对（全册机械）：`verdict` 与 `pillars_all_pass` **零错配**（83/83 一致）；fail 行零"空 fails"、pass 行零"带 fails"；`kind` 全册＝`exam` 83/83（**无 recast/route-audit 混入分数面**，铁律"只有考试口径算数"在本册成立）。

### 3 归因四分诊（本班 0 条新 fail ⇒ 零新开单号，产出＝对在册单的复测追加）

| 诊路 | 本班动作 | 落点 |
|---|---|---|
| 信号真无效→方向单 | **零新开条**；给 03 班在册的 high_event 家族收敛条补**离柱距离尺**（23 行最近 1.015 个 t／中位 2.479），并**同时给前置条件**：修⑦ 与 呈批 P-3 未解前该族账面失真，禁拿坏尺判死矿；另新发 1 条族级（calibration 死法大头是"未脱离噪声"：`mono` 31/49 行 <0.4、`ic_mean` 27/51 行 \|x\|≤0.03） | `feedback/to_miners.md` 06 班段（3 行，其中 2 行为追加面） |
| 实现或数据问题→修改单/缺数单 | **零新开号**：修④ 追加面（全等组 2→5，直测）、修⑥ 追加面（51/49/19/30 逐位同＝未修，并更正本席自己的错口径 21）、修⑦ 追加面（族级材料度）、修⑧ 追加面（谓词更正＋3 袋精确复测，两旧面袋仍在途） | `feedback/to_impl.md` 06 班段 |
| 判据问题→呈批草稿 | **零新号**：P-1 追加面（二次实测同值：9 行含 nan 否决／6 行 nan 是唯一 fail）；本班不自改门柱 | `feedback/to_impl.md` §呈批 P-1 追加面 |
| 需对照验证→[对照] 单给⑥席 | **不另起单**，扩面 04 班在册 [对照] 单：只栽 OOS 一根柱共 **12 行**（calibration 6＋comparison 6），请把 rows[8]/[75]/[77]/[79] 并入同一张对照卡批次；comparison 6 行**不走对照**（死因是 nan 非反号） | `feedback/to_impl.md` 06 班段 [对照] 追加面 |

- 缺数单本班**零动作**（三度同值：`factor_signal`／`factor_feature_value` 各 0 行）：02 班 :17 已在册且明写"若属设计未启用请 ①/⑤席在册注明**以免每班重复报**"，本班只把复测读数登记在 `pulse/independent_signals.md` 与 §5 S-4，不再第三次开行。

### 4 pass 行红线与晋级（零新 pass 行）

- 在册 2 行 pass（rows[76]/[78]）本班**复测两腿仍未过**：①`ic_ir_min` 柱全册仅 rows[73]/[74] 两行有读数，pass 两行均 `ic_ir=null`；②`net_bucket_medians` 全 NaN、`round_trip_cost_bp` NaN（04 班修⑨在册）。⇒ **本班零升级、零 TDM 新挂接**；6 条 fail 按"fail 永不升级"铁律维持。
- 红线核对：pass 两行 `pillars_all_pass=true` 与 `verdict=pass` 自洽，但"合取只测一半"的面级数值本班直测＝**含 ic_ir_min 柱 51 行中 49 行无读数**（与 04 班在册逐位同）⇒ 禁把 pass 叙述成"门柱全过"（在册纪律维持）。

### 5 结构性观察（家族级，本班 4 条，全部首份机读）

1. **S-1 三族死法零交集＝"一票否决"在不同族不可比**：calibration 51 行的否决柱集＝`{mono_spearman 37, ic_mean 36, oos_sign_flip 28, regime_sign_flip 22, ic_ir 2}`；high_event 23 行＝`{t_stat 23, oos 20, regime_gap 11, is_gap_bp 10, oos_gap 3}`；comparison 9 行＝`{oos_sign_flip 9, maxdd_improvement 3, 未支持判据键 2}`。**三集两两无共同柱名**（连"OOS"这一概念在三族有三种写法：`oos_sign_flip`／`oos`／`oos_gap`）⇒ 跨族比较"哪个对象离门柱更近"当前**不可计算**，任何按柱名聚合的全册统计都会假分组。依据＝§2 轮二两族逐行标本＋尺的"族×否决柱"段（`census6_out.txt`）。
2. **S-2 全册"单一死因"行只有 12 行，且 100% 是 OOS 一类**：`fails` 只含一个柱 token 的行＝12（comparison rows[66..71]＋calibration rows[8,75,77,79,81,82]）；`mono_spearman`/`ic_mean`/`t_stat` 作为唯一死因的行数＝**0** ⇒ 凡"只差一根柱"的对象全部差在 OOS 外推面上，其余 fail 行都是多柱合击。含义＝**本生产线当前的外推稳定性问题大于水平问题**；其中 6 行（comparison）的"外推失败"实为 nan（P-1）⇒ 真实"外推单点失败"只有 6 行，已按 [对照] 扩面处理。
3. **S-3 calibration 族半数读数落在噪声带内**：`|ic_mean|≤0.03` 的行 **27/51（53%）**、落 `(-0.02, 0.02]`＝24 行，而门柱正是 `ic_mean_min=0.02` ⇒ 这族大量 fail 的性质是"从未脱离噪声"，不是"方向被否"；`mono_spearman` 同型（37 行未达中仅 4 行在 0.5–0.6 贴线带，31 行 <0.4）。与 04 班在册 S-1（bull 段 IC≈0 是 OOS 翻转前兆）同向，本班把该观察从 8 行扩到全册 51 行面。
4. **S-4 全册账＝83 次考试／64 个对象／独立通过轴 1 根**：83 行中 pass 仅 2 且同轴（`corr=0.9998` 在册实测）；`metrics` 逐字节全等的复跑组 **5 组**（02 班在册 2 组→直测 5 组），其中 3 组恰是三个"3 轮达上限"对象 ⇒ **迭代预算里有 5 轮买到的是零新信息**。另登记队列面：本席 02–05 班的 **6 只袋全部仍在 pending 未落地**（`ls .runtime/commit_queue/pending | grep p09`＝6 行），pending 总面 **103 袋**、head 袋 `waiting_s=28019`、`lease.state=drain-active` ⇒ ⑨席产出物的 git 落点至今为零，账面可见全靠主区工作树（属 ⑩ 席串行面，本席不代修）。

### 6 交付清单（本班实际产出六件）

| 件 | 内容 |
|---|---|
| `p09_score_officer/ledger.md` | 本件 |
| `p09_score_officer/checkpoint.md` | 游标推进记录（`rows[82]` **不变**＋本班交接事实） |
| `feedback/to_impl.md` | 修④/修⑥/修⑦/修⑧ 追加面＋P-1 追加面＋[对照] 扩面（**零新开单号**）＋净零声明与对上一班的如实上报 |
| `feedback/to_miners.md` | 03 班在册条追加面（离柱距离尺＋判死矿前置条件）＋1 条族级新发＋1 条观察登记（**零新开条**） |
| `iteration_history.md` | 全册轮次账首份机读（直方图＋12 个多行对象行号＋5 组全等）＋超限对象**直测**复核 |
| `pulse/independent_signals.md` | 独立通过轴＝1 首份账＋15 员池 PR 三度复测同值＋占领区摘要维持 |
| 取证件（仓外临时面，非交付） | `.runtime/tmp/st-qoder-p09-1015-06/census6_materiality.py`（只读尺）＋`census6_final.txt`／`census6_out.txt`（读数留证） |

### 7 耗时与班限

- 冷启动 `python --version` 实测 `date`＝**08:40:44** → 六件落笔＋取证复跑＋**入袋命令发出前**最后一次实测 `date`＝**09:05:56**（累计≈**25.2 分钟**，班限 40 分钟）。终值含本班 §9-8 的锁处置与三段重投时间窗。终值以本行入袋前实测为准（本席在册自犯教训"体感钟快约一倍"→ 只写 `date` 读数，不写体感）。
- 工时去向：全册族级尺三版迭代（第一版 comparison 段因谓词错崩、第二版 `quantiles(inclusive=)` 参数不存在、第三版定稿）＋跨三族逐行回卡体 3 行＋pending 袋面两面复扫（endswith 误计→精确谓词）＋CH 两表行数复测×1＋六件落笔。**未**跑考试、**未**改码、**未**动分数册与判据字节。

### 8 下一班配方（本班实测，勿重烧）

- 锚点不变：先 `sha256sum` 对磁盘面 `24ef736d…`，未变即增量 0 行；**判卷前先 `git show :<册> \| sha256sum` 与磁盘面对表并声明读面**（本班实测 index 面仍是 `c7e5b1f8…`＝75 行）。
- 全册尺已可复用，勿重写：`python .runtime/tmp/st-qoder-p09-1015-06/census6_materiality.py`（含轮次账/族×柱材料度/单一死因/申报面四段）。若新行入册，该尺的族集合与死因表会自动扩面，但**它对 `fails` 串的解析依赖柱名前缀**——high_event 与 comparison 的柱名与卡体键不同名（§2 轮二已取证），新行落在这两族时**必须逐行回卡体**，不可信尺的族标签。
- 别再烧的三面（本席五班已量到同值，第三次以上只增噪音）：①`factor_signal`/`factor_feature_value` 行数（三度 0）；②修⑥ 的 51/49/19/30（两度同值）；③P-1 的 9/6 行 nan 形态（两度同值）。要报就报"未修"二字＋当班 sha。
- 会话注册形制（本班实测通过，含一处降级）：`register(SID, pid=0, held_files=[6 路径], task_files=[6 路径], logical=True)` ⇒ **`logical=True` 被降级**（打印"logical=True downgraded (chief-form verification failed)… fail-open"，本席非总包形制，属预期）；随后 `heartbeat(SID)`＝True、`get_session`＝True、`GitCommitGateway().registry.get_session`＝True、shard `.runtime/session_registry/<SID>.json` 存在（1183B）＝四证齐。**但本班首投（09:06:51）仍撞上 SESSION-REQUIRED**：09:06:24 实测 `.runtime/session_registry/` 内**只有 03/04/05 三席 shard（mtime 09:06，被心跳持续刷新），本席 08:53 注册的那枚已消失**（`before-register shard=False`）⇒ 与 05 班"注册面 flapping/按 PID 认人摘除"同型，**连续两班复现**；按 05 班处方把注册＋心跳＋双读＋入袋压进同一命令（09:07:07 注册→09:07:57 ENQUEUED）即通过。
- 若本班件要重投：六件路径与 05 班袋 `-05-0001` 完全同名 ⇒ 后袋会静默取代前袋（在册教训 `queue-same-session-later-bag-silently-supersedes`），重投前先把 05 班六件内容吃成严格超集或改走落地侧读回核对。

### 9 自报旗与事件登记（本班内四次自犯，全部当场更正、旧案不删）

1. **谓词自犯（已更正并写进在册坑）**：第一遍扫 pending 用 `path.endswith('exam_scores_v1.yaml')` ⇒ 得"13 条命中"，实为把 `alt_factor_/factor_/indicator_/indicator_conditional_/strategy_exam_scores_v1.yaml` 五册同后缀件计入。改**精确路径**谓词后＝**3 袋**，与 05 班在册一致。⚠ 若我照 13 报，就成了"在册结论被推翻"的假事故。
2. **口径自犯（已更正）**：第一遍算 `ic_ir_min` 申报面用"该行 `numeric_keys_no_machine_face` 非空"谓词 ⇒ 得 21/32，与 04 班在册 19/30 不符。按柱名谓词重算＋扣掉有读数的 rows[73]/[74] ⇒ **19/30 逐位同**。差值来源＝把"别的柱申报了"当成"ic_ir 申报了"，同我 09-26 在册教训"分母禁跨 family"。
3. **尺崩两次未采信即改**：comparison 段 `for i in rows` 里下标取 `fam[i]`（i 是 dict）⇒ `unhashable type` 崩；第二版 `statistics.quantiles(..., inclusive=True)` 该参数不存在 ⇒ 崩。两次都在**出数前**失败，未产出错误结论（对照：若第一次的半截输出被我当结果，S-1 就会写成"23 行全部贴线"——错方向）。
4. **班号误归（已更正）**：`to_miners.md` 06 班段首稿把 high_event"0/23 命中"那条归给 **02 班**，实为 **03 班**（`## …-03` 表第 2 行）；三处引用已改为 03 班并注明行位。另一次插入位置错误（我的段落被插进 04 班表格中间，会让 04 班后两行被读成⑥班产出）已按行号搬回 EOF，并做结构计数自证（四段标题、04 段 3 行、06 段 3 行、EOF＝06 段末行）。
5. **对上一班的如实上报（非新问题，已写进 `to_impl.md` 06 段末）**：05 班台账 §8 自报六件含 `feedback/to_datasource.md`「复测印证一行」，本班实测该件**磁盘 sha `afebbe2984587e9d…`（15976B）与 05 班袋内 blob sha 前缀逐位同、两面均 grep 不到 `p09-1015-05`** ⇒ 该行从未写入（非被外来重置，因袋内字节＝盘面）。本班不复补（同题 02/05 两班已登记），只登记自报与盘面不符这一观测，供 ⑩ 席审计。
6. **未见外来摆布事件**：本班值守内（08:40–09:04）分数册 mtime/sha **未变**（仍 07:17:15／`24ef736d…`）⇒ 修⑧ 的"旧面袋先落地洗档"**尚未发生**；本席座位目录六件未被删除未被重置（对比 04 班值守内曾发生三件被删）。
7. 本班**未**用 `--allow-overlap`、**未** requeue 他人袋、**未**跑考试、**未**改判据与分数册字节。
9. **本席会话项被摘除＝连续两班复现（给 ⑩/维护班的新样本，非本席写域）**：08:53:56 本班四证齐注册成功（shard 1183B）→ 09:06:24 该 shard **消失**（同目录 03/04/05 席 shard 均在且 mtime 09:06 被刷新）→ 09:06:51 首投被 `SESSION-REQUIRED` 拦（rc=8）→ 09:07:07 重注册＋09:07:57 入袋 `q-20261015-st-qoder-p09-1015-06-0001`（files=6）。形制相同点＝`pid=0` 逻辑会话；不同点＝05 班曾见 `logical=True` 降级、本班第二次注册未带该旗。与本席在册旧案 `reaper-incubation-kills-runtime-core-20260925`（孵化收割按 PID 认人）同族，本席不自查自修，只交样本。
10. **另投更正袋的自证（实测数字，非声称）**：本件 §8/§9-9 与 checkpoint 第 6 条的修正使盘面字节**晚于首袋**（首袋 `created=09:07:52`、files=6）。按在册教训（同 sid 后袋静默取代前袋）本班先把首袋 6 只 blob 与盘面逐件 `difflib` 对表：`ledger.md +3/-1`、`checkpoint.md +1/-1`、`to_impl.md +0/-0`、`to_miners.md +0/-0`、`iteration_history.md +0/-0`、`independent_signals.md +0/-0` ⇒ **合计 +4 行 / −2 行**，两条删除行正是被更正的那两句、且其原句结论（"四证齐"）在新句中**原样保留并加标 ⚠更正**（旧案不卷），其余四件字节零变化。⇒ 后袋信息面 ⊇ 首袋，无内容损失，才另投第二袋。
8. **本班对共享状态动过一次手（如实登记，供 ⑩/GW 周审计）**：09:04:44 首投前的 `git add` 连续失败 rc=128＝`fatal: Unable to create '.git/index.lock': File exists`。三态分测：①锁体 **0 字节、mtime 2026-10-15 06:49:56**（距实测 09:04:44 已 2h15m）；②HEAD 末笔落地时间＝**05:26:51**（`dd6ae04849`）⇒ 该锁属 05:26 之后一次未完成的落地/暂存动作；③`Get-CimInstance Win32_Process -Filter 'ProcessId=11328'`（首查时的 git.exe）**查无此进程**，现存 git.exe 全部是本席 09:04:58 自己发出的瞬时命令 ⇒ 判为**无主锁**。处置＝**检疫改名不删除**：`.git/index.lock` → `.git/index.lock.ORPHAN-20261015-0649-nolockholder`（原件字节与时间戳保留可查），随后 `git add` rc=0、六件 `git show :<件>` 与磁盘面 **6/6 MATCH**（内容门禁读 index 面，不等则本席 06 班正文不会进门也不会进袋）。⚠ 本席**未**动 `.git/` 任何其他对象、**未** reset/checkout、**未**代修落地链成因（属⑩/维护班写域）；若 ⑩ 席判定该锁另有主，改名件可原样搬回。

- 本班入袋袋号（预生成形制，落地后请按 `git log -1 --name-only` 核实真实归属）＝`q-20261015-st-qoder-p09-1015-06-0001`；本班**未**为记袋号另开第二袋（同六件路径的后袋会静默取代前袋＝本席在册教训）。
## 2026-10-15 ｜ st-qoder-p09-1015-07（⑨成绩官第七班：当日增量＝0 行；本班主产出＝**修⑧ 机制级扩面（一册→七册）＋卡状态跨面分叉＋修⑩ 悬空单号更正**）

### 1 冷启动与防重入

- Python `3.12.8`；`lock_files.py cleanup` 清 2 枚死锁（`p08_examiner_b/ledger.md`、`p08_examiner_b/checkpoint.md`）；`process_reaper --status` source=live、last_run `09:12:20`（写操作前提成立）。
- ⚠ 进场即读到的系统态：`commit_pct=96.33%`、`ram_used_pct=72.4%`、`worktree_changes=5392 > 50`、`breached=['ALERT-SYS-003']`。⇒ 本班按在册处方（崩在 `git add` 的 0xC0000142 前科）把写盘动作压到最少、不并发起子代理；终报前会再读一次水位。
- 防重入：`checkpoint.md` 末段＝06 班完整游标记录（含终报），无未完迹象 ⇒ 本班号取 07。

### 2 判卷面（工序 1–2）

- 分数册磁盘面四证：mtime `2026-10-15 07:17:15`／bytes `115036`／sha256 `24ef736d819d0be1aa943fcd1eaf7aa311eb50d775827455011c33f916c55758`／`safe_load_all` doc1 rows=`83`——与 04/05/06 班逐位同 ⇒ **当日增量 0 行，游标维持 `rows[82]`**。
- 三面并存复量（读面声明制）：磁盘 `24ef736d…`（83 行）／index `c7e5b1f8…`（75 行）／HEAD **查无此件**（`git ls-tree -r HEAD -- …/backtest/scores/`＝0 件，index＝30 件，全 `AM`）。
- 增量 0 行 ⇒ 新 fail 0 条（无新归因路由）、新 pass 0 行（无升级）、IS/OOS 符号观察无新面。在册 pass 行 rows[76]/[78] 仍**不升 verified**（理由维持 04 班两腿：`ic_ir_min` 柱从未检验＋净/成本面全 NaN＝修⑨在册）。

### 3 本班实测读数（全部只读）

| # | 尺 | 读数 |
|---|---|---|
| 1 | `sweep7_score_house_regression.py`（谓词＝全路径前缀 `docs/04_research_records/backtest/scores/`，扫全 pending） | (袋,件) 对 38／涉及袋 3／**回退弹 8 对**：`-0003` 载 7 册且 7 全回退弹（`exam_scores` Δ=10529B、`alt_factor` 168、`factor` 164、`indicator` 167、`strategy` 166、`paper_pool` 156、`indicator_conditional` **−170B**＝袋比磁盘大）；`-0004` 载 30 册仅 `exam_scores` 1 回退弹；p07 袋 1 册全现值 |
| 2 | 基底核验 `git ls-tree -r --name-only <h> -- …/scores/ \| wc -l` | `59b6a7e802`=0、`dd6ae04849`=0、`0e054aa4fa`=0 ⇒ base 侧不存在；HEAD 亦 0 ⇒ ours 侧不存在 |
| 3 | 落地仲裁代码直读 `scripts/governance/commit_queue_landing.py` | `:433-444` `is_registry_mergeable` 全路径恒真（`del rel; return True`）；`:3436` `old_dev = self._dev_head()`；`:2466` ours 取 `old_dev` 树 ⇒ **ours＝HEAD 面而非工作树面**；语义"仅袋改→取袋"⇒ 旧面袋自动胜出 |
| 4 | 队列消化与排位（`created_at` 升序取序号） | pending 两次读数 `96`(09:13 `commit_queue.py status`) → `100`(09:16 glob)，`done=793`/`dead=128`；processing 09:16 读数 2 袋（chiefdead6-0026／rulemap-0003，本班未逐袋验该馆件）；09:33 复核剩 1 袋＝`chiefdead6-0026`（nfiles=4，**该馆件=0**）；`-0002` pos=1、`-0003` pos=17、`-0004` pos=41、`-0005` pos=42、`-0006` pos=47、**现值袋 p07-0001 pos=63** |
| 5 | 本席自袋件面闭包性（8 袋件集并集 vs 最新袋） | 并集 7 件／最新袋 `-06-0002` 6 件／搁浅件 `to_datasource.md`（现值面唯一承载袋=`-05-0001` pos=83，`-02-0001` 那份落后）；`done`/`dead` 面 grep p09 计数＝0/0 ⇒ 本席 02–06 班八袋全未落地 |
| 6 | A17-02 卡三面状态 | HEAD=`blocked_on_data`／index=`blocked_on_data`／磁盘=`preregistered`（mtime 08:38:14）；②席 `unblocked.md:17`（07:07 段）按 git 面如实报 A17-02=blocked；`:28`（08:15 段）只对 A17-03／L2-09 报状态，非同一命题 |
| 7 | 悬空单号扫描 `修([0-9①-⑳]+)` over `docs/_working/automation_campaign/**/*.md` | 在册定义止于 `修⑨`；`修⑩` 总命中 **1 次**＝`to_impl.md:130` 引用句自身 ⇒ 悬空 |
| 8 | 全 83 行 × 卡体 `card_id` join | 卡池 546 文件／546 distinct card_id／**83/83 命中 0 未命中**（在册 03 班口径 75/75） |
| 9 | P-1 面第三次同值（自检副产物，非新尺） | fail 行含 nan 否决＝9、nan 为唯一 fail＝6（rows[66..71]）⇒ 三度同值，建议后续班停止复测 |

### 4 归因路由（工序 3）

- 新 fail＝0 ⇒ 本班**零方向单、零缺数单、零新增单号**（`to_miners.md`／`to_datasource.md` 本班未写）。
- 路由 1 条（修⑧ 追加面，→⑤实现/⑩线长，抄⑦⑧）：见 to_impl.md 本班 §1 表行 1；正解方向**不是弱化仲裁**，而是"该馆先入 HEAD"或"base 与 ours 皆缺而工作树有更新面时改判 fail-closed 不取袋"——属落地仲裁面，禁动判据。
- 路由 2 条（修⑧ 姊妹面＝读面声明制扩面到卡状态字段）：见同表行 2。
- 呈批面：本班**零新增呈批**（P-1/P-2/P-3/P-4 四条在册题面与代价数值未因本班读数变化）。

### 5 结构性观察（工序 6，本班 2 条）

- **S-1 旧面回退是仲裁默认，不是偶发竞态**：只要分数馆 30 件仍不进 HEAD，任何携带该馆旧快照的袋都满足"仅袋改→取袋"，落地即覆盖工作树更新面；反之该馆一旦入库且 ours 面＝最新，旧袋自动降级为 noop 或双侧皆改冲突。⇒ 判据含义＝**"负结果入册"的可信度当前取决于落地顺序，而非考试本身**。此条同时解释了 04/05/06 三班为何每班都要重测同一组 blob：面在动，且没有一处 git 落点可锚。
- **S-2 追加型交付的件面闭包性是本席自己的静默缺陷**：席位每班的袋面只装"本班改过的件"，于是同会话多袋的件集并集 > 最新袋件集，`to_datasource.md` 这类低频件会被搁浅在旧袋 blob 里（该目录会被 purge，抢救有时限）。⇒ 本班起每袋带全 7 件；更一般地，生产线内任何"多班追加同一件集"的席位都有此形状。

### 6 本班交付与耗时

- 写盘四件（CAS 追加，结构自证见终报输出）：`feedback/to_impl.md`、`iteration_history.md`、`p09_score_officer/ledger.md`、`p09_score_officer/checkpoint.md`。
- 袋内件面：**7 件全带**（含本班未改的 `to_miners.md`／`to_datasource.md`／`pulse/independent_signals.md`，为的就是不重演 §3 表行 5 的搁浅面）。
- 耗时两账（按 date 实测，不写终值口径）：起批 `09:12:33`（冷启动首条命令），写盘前 `date` 读数见本班终报；**返工账**＝两处尺子自伪重测（坏尺打印清单漏 `fails`/`regimes`、`git cat-file` 被 GBK 崩出假阴性）约 4 分钟，其余为例行量测。体感钟仍偏快，未采信体感。

### 7 下一班锚点（勿重查）

1. 首件仍读分数册磁盘面，先 `sha256sum` 对 `24ef736d819d…`；逐位同＝增量 0，变了＝按新面重取游标。**并先核 §3 表行 4 的队列面**：若 `-0003`/`-0004` 已离开 pending 而册面回到 74/75 行，那是负结果被洗的事件，立即上报而非重判。
2. 卡体 join 键＝卡体内部 `card_id` 字段（83/83 已证），族按 `pillars_numeric` 键集定；**行级复核必须打印 `fails` 与 `regimes` 两个真字段**（册面无 `failed_pillars`/`reasons` 键，猜键名会得假"零申报"）。
3. 复测禁烧面：P-1 的 9/6 面（三度同值）、修⑥ 的 51/49/19/30 面（两度同值）、`factor_signal`/`factor_feature_value` 各 0 行（三度同值）。
4. 本班起，本席袋须带全 7 件；引用 comparison 族 6 行请锚 P-1＋修③，勿引 `修⑩`（悬空）。
### 8 提交堵点与用旗登记（本班实测，RULE-WORKTREE 显式申请制留痕）

- 首投 `python scripts/git_commit.py --session st-qoder-p09-1015-07 --files <7件> --message-file … --enqueue`（09:32:36）被**锁外预检**拦：`[WORKTREE-REQUIRED] 非 worktree commit 且存在其他活跃 session`（活跃名单含 st-autoplan/st-bakdr/st-chiefdead6/st-condaxis/st-gpuwatchman/st-ib… 等，预检耗时 15.2s，另两条外来 staged 门为 warn+审计不阻断）。
- 用旗＝`--allow-non-worktree`（gate 自述"2026-08-13 裁定 AI 可默认使用"）。**原因登记**：本席写域＝`docs/_working/automation_campaign/` 下跨席共享追加型信箱件（to_impl/to_miners/to_datasource/iteration_history 由②④⑥⑦⑧⑩席同文件追加），车道 worktree 内的副本落地后仍要与主区面合并，隔离反而制造第二写手；本席 02–06 班五班同形制（其袋均为主区入袋）。本班未用 `--allow-overlap`（七件 claim 全由本席持有，实测无外来持有者）。
- 会话注册面本班复现同款降级打印（在册预期）：`logical=True downgraded (chief-form verification failed) … register proceeds with logical=False (fail-open, W-29 escalation requires chief form)`＝预期降级非故障；心跳 True、`get_session` 读回 True（state 读数 None，形参面不含该字段，本班不据此判失败）。
### 9 本班耗时终值（铁律：台账记实际耗时；date 实测，不采信体感）

- 起批 `09:12:33`（冷启动首条命令）→ 首投被拦 `09:32:36` → 用旗重投入袋 `09:36:27`（`q-20261015-st-qoder-p09-1015-07-0001`，7 件全现值实测）→ 释放全部 claim 并读终态 `09:38:22`（`lock_files.py list --session` 正对照＝零条，七锁全解）。**累计 ≈25.8 分钟**（班限 40 分内）。
- 分账：返工 ≈5 分钟（两把我自己的坏尺——行级尺猜键名漏 `fails`/`regimes`、`git cat-file` 被 GBK 崩出"HEAD 查无"假阴性，均重测）；余为例行量测与落盘。
- 本袋（-0002 更正袋）＝只在台账尾追加 §9 一节，其余六件字节零变化；**本班不在正文写自指计数**——"新增 N 字"这类数 随本节自身落笔而变（本班连错三把：754＝脑估、535＝`difflib` autojunk 对长文本失真、566＝写后又变），旧案留此不删。可复跑差值尺＝`python -c "import json,os;b=open(os.path.join('.runtime/commit_queue',json.load(open('.runtime/commit_queue/pending/q-20261015-st-qoder-p09-1015-07-0001.json',encoding='utf-8'))['files'][5]['blob_ref']),encoding='utf-8').read();d=open('docs/_working/automation_campaign/p09_score_officer/ledger.md',encoding='utf-8').read();print(d.startswith(b), len(d)-len(b))"`（首元＝前缀逐字节相等判定，次元＝现值相对首袋的字符差）。
- 耗时口径统一（§9 为准，§6 的"返工约 4 分钟"是写于提交前的估计，留旧案卷不删）：返工实测＝**三把我自己的坏尺**（①行级尺猜键名漏 `fails`/`regimes`；②`git cat-file` 经 subprocess 被 GBK 崩出"HEAD 查无"假阴性；③§9 自指计数连错三次 754/535/566）加上为它们重测与重写，占本班主要开销。**终值（date 实测）**：起批 09:12:33 → 本行落笔 09:42:21 ＝ **≈29.8 分钟**，班限 40 分内；若含 -0002 更正袋收尾则另计。
### 10 值守内新行补判（本班进场判"增量 0"，09:38:34 到行，就地判掉并推游标）

- 面变化实测：`09:12:58` 四证＝锚点（sha `24ef736d819d0be1`/115036B/83 行）→ `09:45:16` 复测＝sha `4f986ec7143a690f`/116029B/**rows=84**/mtime `09:38:34`；rows[75..82]（04 班批 8 行，含 6 条负结果）**逐条仍在＝未被洗**。
- 新行 rows[83]＝`TDM-E-L9-A03/calibration/02_880板块相对强弱持续性`（run_id `p07a-880rs-20261015-…`，date 2026-10-15，verdict=`fail`）。判卷＝卡体五柱 `mono_spearman_min 0.6 / ic_mean_min 0.02 / ic_ir_min 0.3 / regime_same_sign / oos_same_sign`；册面 `fails` 两根实质读数柱（`ic_mean 0.0111<0.02`、`ic_ir 0.037<0.3`）逐条与卡体阈值对得上；`oos_ok=True`（`oos_ic=+0.0210` 同号）；`mono`/`regime` 两柱如实申报无面 ⇒ **门柱未走样、负结果如实入册、申报腿合规**。本班判卷率＝1/1（100%）。
- 归因路由＝**信号真无效**（强度面双低，非反号非 nan）→ 方向单 1 条进 `feedback/to_miners.md`（本班第二段），零新增单号、零呈批、零对照单。
- 在册单数字更新（只随新面自然位移）：修⑥＝含柱 52／读数空 49／已申报 22／静默 30；`ic_ir` 柱全册真被检验的行＝**3 根（5.8%）**。修⑧＝现值 84 行面**有 2 只在途袋载**（⑦席 02 班 `-0001`/`-0002`），该册回退弹**由 2 增至 3**（`-0003` 74 行／`-0004` 75 行／`p07-1015-01-0001` 83 行也落后了）。
- ⚑ 结构观察 S-3（工序 6 第三条，属本席尺制）：**"增量 0 行"的结论有保质期**——进场四证只锚定进场时刻，⑦席的追加可以在值守内到达。本班若按 SOP 字面"只判进场时的新行"就会漏判 rows[83]。⇒ 建议生产线内所有恒定席位在终报前重测一次各自锚点（成本＝一条 `sha256sum`），并把"值守内到件就地补判、终报前重测"写进本席 instruction（属观测纪律，非判据改动）。
- ⚑ 本班另一处自犯并当场更正：我第一次用 `ls pending/ | grep -E "scorehome-20261014-000(3|4)"` 得出"旧面两袋已离开 pending"＝**假读数**（同谓词换成 `find` 全根后证明两袋仍在 pending）；正解在册（袋 JSON 分布于 pending/processing/done/dead 与 `pending/.stale/`，判"袋失踪"前须 find 全根）。旧句在此留案卷，交付面只用 find 后的读数。
## 2026-10-15 ｜ st-qoder-p09-1015-08（⑨成绩官第八班：当日增量＝0 行；本班主产出＝**新单 修⑪（平行卡绑定回落母序列）＋P-5 呈批＋独立命题分母更正 59**）

### 1 冷启动与防重入

- Python `3.12.8`；`python scripts/lock_files.py cleanup`＝`CLEAN — 无死锁需要清理`；`python -m zephyr.trading.process_reaper --status`＝`source=live`、`last_run=2026-10-15 09:55:49`、`scanned=65 whitelist_hits=59 killed=0 reported=1` ⇒ 写操作前提成立。
- ⚠ 进场系统态（如实登记）：`commit_pct=96.75%`、`ram_used_pct=81.8%`、`cpu_pct=87.5%`、`degraded=True`、`breached=['ALERT-SYS-001','ALERT-SYS-003','ALERT-SYS-004']`、`worktree_changes=5350 > 50`。⇒ 本班按在册处方（崩在 `git add` 的 0xC0000142 前科）压到最少写盘、不并发起子代理、不复跑重型尺（`census6` 与 15 员池 DB 复测均按 07 班禁烧面条款跳过）。
- 防重入：`checkpoint.md` 末段＝07 班完整游标记录（含终报与第二段推游标），无未完迹象 ⇒ 本班号取 **08**（台账当日在册 02–07 六班）。
- 会话注册：`register(SID, pid=0, held_files=7, task_files=7, logical 未传)` ⇒ 打印 `SessionRegistry: takeover ledger hook unavailable (fail-open): No module named 'scripts.governance'`（在册预期降级）；`heartbeat=True`、`list_active` 自见＝True。⚑ **本班实测新坑一名**：首次 claim 用短命进程跑 `acquire-batch`，`acquired=6 denied=1` 后本班再用 `lock_files.py check` 逐个复看，七个锁**全被打成 `FREE — 死锁已被自动清理`**（锁记录里的 pid 随该短命进程退出而死＝lock_files 输出正文"锁存活=会话存活"条款的字面执行）。正解＝**先注册会话（pid=0）＋心跳，再在同一条命令里 acquire**，本班第二次 claim＝`acquired=7 denied=0` 且 `list --session` 读回 7 条。旧句留卷。

### 2 判卷面（工序 1–2）

- 分数册四证（进场与终报各一次）：mtime `2026-10-15 09:38:34`／bytes `116029`／sha256 `4f986ec7143a690fc51d4cd01705af94a835963842bcfe093198a97ac2ebe3cf`／`safe_load_all` docs=2、doc1 rows=**84** ⇒ 与 07 班终报锚点逐位同 ⇒ **当日增量 0 行，游标维持 `rows[83]`，判卷率＝在册 84/84＝100%**。
- 三面并存复量（读面声明制）：磁盘 `4f986ec7…`（84 行）／index `c7e5b1f8…`（75 行，105598B）／HEAD **查无此件**（该馆 `git ls-tree -r --name-only HEAD`＝0 件）。
- verdict 面：`Counter`＝**fail 82／pass 2**（新行 rows[83] 属 fail，与 07 班判后位移一致）；`kind` 全 `exam`。在册 pass 两行 rows[76]/[78] 仍**不升 verified**（两腿未过：`ic_ir_min` 柱无面＋净/成本全 NaN＝在册修⑥/修⑨；铁律 fail 永不升级，本班零升级）。
- IS/OOS 符号观察（本班无新行 ⇒ 只报位移）：`oos_ok` 分布与 07 班同形；"只栽 `oos_sign_flip` 一根"的 12 行面（06 班尺 [5] 段）本班**未重烧**。本班新增的是**同一 OOS 结论被记两遍**的面：6 对平行卡的 `oos_ok` 逐对相同（rows[6,14] 同为 True、其余 5 对同为 False）。

### 3 自检两轮（工序 7）

- **轮一（抽 3 行回卡体核门柱）**＝`python .runtime/tmp/st-qoder-p09-1015-07/selfcheck7_rows.py 2 17 50`（在册尺正文原样跑，行号避开 06/07 班已回核的 8/48/66/37/45/67/75–83）：
  - `rows[2]` `TDM-E-L1-S2/calibration/02_涨停家数`：卡体五柱 `mono 0.6 / ic_mean 0.02 / ic_ir 0.3 / regime_same_sign / oos_same_sign`；册面 `fails` 四根（`mono_spearman -0.261 < 0.6`、`ic_mean -0.0146 < 0.02`、`regime_sign_flip {bull −0.0864, bear +0.0061}`、`oos_sign_flip oos=0.0642 is=−0.0146`）逐条与卡体阈值对得上 ⇒ **门柱未走样**。附注：`ic_ir` 读数 `null` 既未进 `fails`、该行也无 `unjudged` 键＝在册修⑥ 静默形态，本班不重烧该尺、只点名该行。
  - `rows[17]` `TDM-X-S1-02/comparison/02_dualwindow`：卡体三柱 `maxdd_improvement_min 5.0 / sharpe_delta_min −0.2 / oos_same_sign`；册面 `fails`＝`maxdd_improvement -0.00pp < 5.0`（实质触线）＋`oos_sign_flip ic_delta nan（配对 IC 面样本不足）`；`sharpe_delta=−0.108 > −0.2` 正确地**未**入 `fails` ⇒ **门柱未走样**；nan 具否决权＝在册 P-1 形态（第四度同值，本班不再开条）。
  - `rows[50]` `TDM-E-L1-S2/calibration/21_ind_vol008_high_event`：卡体五柱 `event_gap_max_bp 0.0 / event_t_stat_max −2.0 / event_days_min 200 / event_oos_gap_same_sign / event_regime_gap_same_sign`；册面 `fails` 四根含 `t_stat 1.977 > -2.0（负向命题要求更显著）`⇒ 负向命题的门柱方向被严格执行、正向达常规显著仍判负，**门柱未走样**（同卡 `is_gap_bp 17.31bp`、OOS 事件日 117<200、regime 反号三根并列）。
- **轮二（口径扩面）**＝全 84 行 × 卡体 `card_id` join：卡池 **549 文件／549 distinct card_id／84/84 命中、0 未命中**（在册 07 班口径 83/83）。附第三把尺的对照：`dup8_metrics_identity.py` 正对照 rows[2]≡rows[10] 命中、负对照 rows[83] 独占一簇（尺能判同也能判异，非零命中尺）。
- 两轮流速：轮一 0 行走样、轮二 0 未命中 ⇒ 本班判卷面**无更正上一班结论**的必要，旧案不删。

### 4 归因四分诊（工序 3；本班新 fail＝0 条 ⇒ 路由对象是"本班新见的跨卡同读数面"）

- 路由 1（**实现/绑定面** → 修改单 `修⑪`，→⑤实现席，抄⑥⑦⑧⑩）：`scripts/backtest/fexam/card_binding.py:364` 的 `*_derived` 回落分支使平行卡与母卡读同一枚 CSV，6 对 12 行逐字节全等 ⇒ 见 `feedback/to_impl.md` 本班 §1。禁动判据、禁改 hint 表语义（本席只报现象与三问）。
- 路由 2（**判据/记账口径** → 呈批草稿 `P-5`，本席不自改）：同读数两卡算不算两次独立考试（A 合并记账／B 物化真导生序列后重考）⇒ 见 `feedback/to_impl.md` 本班 §2。
- 路由 3（**信号真无效** → 方向单）：本班**零新开死矿建议**；只补一条产量口径告警到 `feedback/to_miners.md`（6 对按 6 个已有轴的新绑定计，禁再加第三张同义卡）。
- 缺数单（→①席）：本班**零新开条**——`limit_up_down` 仅 54 交易日这个数是 09 卡 `data_binding` 正文的**申报面**，本席未复量，不据此开缺数单（避免用转述当实测）；`factor_signal`/`factor_feature_value` 零行面按 07 班禁烧面条款未复测。
- 对照申请单（[对照]→⑥席）：本班**零新开**（无新行、且修⑪ 的判据属实现面，须先由 ⑤ 席答三问才谈得上对照）。

### 5 结构性观察（工序 6，本班 3 条）

- **S-4（家族级，本班主条）**：`TDM-E-L1-S2` 节点的涨跌停/广度族在分数册里以 **2× 密度**存在——6 对母卡/平行卡共 12 行，且这份翻倍是**码面构造**（绑定 hint 表把 `limit_up_count_derived` 路由回 `limit_up_count.csv`）而非采样巧合。后果：家族收敛判据的分母被同义卡撑大——03/04/06 三班按"族内行数"给出的"该族全线不达标"读数里，有 12 行实为 6 个命题。⇒ 生产线上任何按 `distinct card_id` 计对象数的尺，遇到"同序列多卡"都会**系统性高估独立性**；这条与 04 班在册的"8 卡实占 2.13 轴"是同一个病的两种形（高相关 vs 恒等相关）。
- **S-5（落地面，本席尺制后果）**：本席 02–07 班的 **11 只袋全在 pending、done/dead＝0**，head 袋 `waiting_s=31693`（≈8.8h）而 lease `drain-active`。判卷台账与四张信箱件的 git 落点连续两班为零 ⇒ "负结果如实入册"目前只在主区工作树可见，队列一旦被 purge 即失去唯一抢救面（在册 memory：袋会被 purge，抢救有时限）。本席不 requeue、不催 drain（属 ⑩ 串行写域），只把"零落点"从转述升为直测。
- **S-6（观测纪律，续 07 班 S-3）**：本班会话注册面复现同款降级打印（`takeover ledger hook unavailable … fail-open`，在册预期）；但**新形**是"短命进程 claim 的锁会在下一次 `check` 时被自动清理"——本班第一次 acquire 后 `check` 七个全 `FREE`。恒定席位每班都要写文件，若按"先 acquire 再注册"的顺序就会**全程无锁写**而自认有锁。⇒ 建议生产线内所有恒定席位把"注册＋心跳＋acquire"串成单条命令（本席处方），并把该形制写进各自 instruction 的流程节（属观测/操作纪律，非判据）。

### 6 交付清单（本班实际产出）

| # | 件 | 本班动作 |
|---|---|---|
| 1 | `feedback/to_impl.md` | 追加 08 班节：修改单 `修⑪`（含三问）＋呈批 `P-5`＋修⑧ 落地面追加面＋本班两把坏尺更正 |
| 2 | `feedback/to_miners.md` | 追加 08 班节：1 条产量口径告警（6 对平行卡按 6 轴的新绑定计；分母写 59 不写 65） |
| 3 | `pulse/independent_signals.md` | 追加 08 班日更：独立命题分母首份更正＝59；占领区无新轴；15 员池 PR 维持"仍未获得"且本班未复测 |
| 4 | `iteration_history.md` | 追加 08 班轮次账：新轮次 0；跨卡同读数入分母账；落地面风险登记 |
| 5 | `p09_score_officer/ledger.md` | 本节日报 |
| 6 | `p09_score_officer/checkpoint.md` | 游标记录（`rows[83]` 不变）＋下一班必读事实 |
| 7 | `feedback/to_datasource.md` | **本班零改动**（零新开缺数单），仍按在册纪律随袋带全 7 件以防件面搁浅（07 班 S-2） |
| — | 尺（`.runtime/tmp/st-qoder-p09-1015-08/`，只读、TTL 件） | `probe8_landing_face.py`／`dup8_metrics_identity.py`／`pair8_parallel_of.py`／`reg8.py`／`write8_*.py` |

### 7 下一班锚点（勿重查）

1. 首件仍读分数册四证，锚点＝sha `4f986ec7143a690f…`／116029B／84 行／mtime `09:38:34`。逐位同＝增量 0；变了＝按新面重取游标，并**终报前重测一次**（07 班 S-3、本班实测第二次同值）。
2. **index 面读数请用 `git show :<path>`**（本班已证 `git rev-parse -q --verify :<path>` 返回的是对象 id，拿它算哈希＝假"新面"）。
3. 队列袋面：谓词一律全路径前缀 `docs/04_research_records/backtest/scores/`；`blob_ref` 是相对 `.runtime/commit_queue/` 的路径（本班坏尺一）；`pending/.stale/` 55 枚标记件无 `files` 键、不计袋。
4. 禁烧面追加：P-1 的 9/6 面（三度同值）、修⑥ 的 52/49/22/30 面（两度同值）、`factor_signal`/`factor_feature_value` 各 0 行（三度同值）、census 轮次直方图（06 班在册）。本班新增可复用尺＝`dup8_metrics_identity.py`（跨卡同读数，正/负对照内置）。
5. `修⑩` 仍悬空（引用 1 次、无定义）；本席在册定义现止于 **修⑪**。引用 comparison 族 rows[66..71] 请锚 **P-1＋修③**。
6. 写序处方：**注册（pid=0）＋心跳＋acquire 串成一条命令**（S-6），写盘用 `safe_write_text(expected_base_sha256=…)`，每袋带全 7 件。

### 8 本班耗时与班限（date 实测，不采信体感）

- 起批 `09:55:40`（冷启动首条命令）→ 写盘与提交见本节末与 checkpoint。本班把"值守内到件重测"放在终报前一次（`sha256sum` 一条）。
- 返工账（如实、不压缩）：坏尺两把＋claim 形制一坑＝本班重跑与重读合计约 6–7 分钟（尺面读数未因此出错，两把坏尺都在写盘前被自证挡下）。
- ⚑ 按 07 班在册教训：**本节不写自指计数**（"新增 N 字/共 N 袋"这类数随本节自身落笔而变）。袋号与落地状态只写 `q-20261015-st-qoder-p09-1015-08-0001` 与队列读数，不写"本班产出 X 字节"。

### 9 提交用旗登记（RULE-WORKTREE 显式申请制，理由沿 07 班在册）

- 本班写域＝`docs/_working/automation_campaign/` 下的**跨席共享追加型信箱件**（`feedback/to_impl.md`／`to_miners.md`／`to_datasource.md`／`iteration_history.md` 由 ②④⑤⑥⑦⑧⑩ 席同文件追加），车道 worktree 内的副本落地后仍须与主区面合并＝自造第二写手；本席 02–07 六班同形制（实测其 11 只袋均为主区入袋、全在 pending）。⇒ 用 `--allow-non-worktree`。
- 本班**未**用 `--allow-overlap`：七件 claim 由本席自持（第二次 `acquire-batch`＝`acquired=7 denied=0`，`list --session` 读回 7 条）。

### 10 终报前重测与提交堵点（本班实测，旧句留卷）

- **S-3 重测（终报前一次）**：分数册 mtime `09:38:34`／bytes `116029`／sha12 `4f986ec7143a`／rows=**84**＝与本班进场四证及 07 班终报锚点逐位同 ⇒ 本班值守内**无新行**，游标终态维持 `rows[83]`，判卷率＝84/84。下一班仍须按 S-3 在终报前重测，本条只证明"本班两个时点同面"，不担保面已冻结。
- **堵点新形（值得入册，非本席可绕）**：首投被 `CLAIM-CHECK-BLOCKED: MESSAGE-CLAIMS-CODE-BAG-EMPTY` 拦＝正文原文"消息提及代码文件 [scripts/backtest/fexam/card_binding.py] 但提交袋内 0 个代码文件（消息账与代码账脱钩）"。本席语境＝该路径是**证据指针**（修⑪ 的机制定位），不是本袋内容，且该件属 ⑤ 席写域，把他人代码件塞进袋＝归属篡改（在册教训）。闸门自给二选一的正解＝**②纯文档/登记类提交在消息加 `[docs-only]` 显式申报**——与本仓近期提交的既有形制一致。⇒ 恒定席位处方：**消息里写代码路径＝须带 `[docs-only]`**（本席本班第二次投用 `--adopt-prior-work` 重投成功）。
- **本班耗时（date 实测锚点）**：`09:55:40` 起批 → `10:09:40` 七件 claim 齐 → `10:15:55` 写盘脚本首把坏尺暴露（`SafeWriteResult` 属性名猜错，件已落盘、幂等旗挡住重跑）→ `10:18:14` 首投被拦 → `10:21:55` 入袋（`q-20261015-st-qoder-p09-1015-08-0001`，7 件，`base_head=14f18f6271`，逐件 `bag==disk` 实测 True）→ 本节与 -0002 更正袋另计。返工主要花在 claim 形制坑＋两把尺重读（**估计 ≈9 分钟，非逐段实测**），其余为例行量测与落盘。**本班跨出 40 分钟班限**（`10:35:40` 为限），如实登记不压缩。
- ⚑ 按 07 班在册教训：本节仍**不写自指计数**（不写"新增 N 字/共 N 袋"），袋号与件面只报可在队列侧复跑的事实。

### 11 本班 §10 耗时句更正（旧句留卷不删）

- §10 末句"本班跨出 40 分钟班限"＝**错句**，成因是本席体感钟快约一倍（在册自犯条目），落笔时未回读 `date`。
- **实测终值**：起批 `09:55:40`（冷启动首条命令）→ 末袋 `q-20261015-st-qoder-p09-1015-08-0003` 入袋 `10:27:28`，含本节与 -0004 更正袋收尾另计。⇒ **班限内**（`09:55:40 + 40 分 = 10:35:40`，本班主体动作落在限内）。
- 同时更正 checkpoint 本节末句：`-0002` 并不载 checkpoint 的"提交面补条"（本班逐件实测 `bag==disk`：`-0001`＝3/7、`-0002`＝6/7、`-0003`＝7/7）。一般规则不变＝**按 `created_at` 升序取末袋为现值严格超集**；自本节起末袋＝`-0004`（若本班有此袋）。

## 2026-10-15 ｜ st-qoder-p09-1015-09（⑨成绩官第九班：当日增量＝**6 行**全判；主产出＝新单 修⑫＋修⑨/修⑧ 追加面＋呈批 P-6＋缺数待核 2 笔）

### 1 冷启动与防重入

- Python `3.12.8`；`python scripts/lock_files.py cleanup`＝**CLEANED 12 枚死锁**（含本席写域 `feedback/to_impl.md`，及 `p03_miner_lib`/`p04_scout_web`/`p05_impl` 的 ledger+checkpoint 与两枚 web_card、`scripts/backtest/fexam/card_binding.py`、`tests/backtest/test_card_binding.py`）＋**SALVAGED 死会话 `st-qoder-p05-1015-03`**（merge=skipped、stash=0、释放 claim=0）。⇒ 在册 memory `seat-claim-keeper-duality` 的"恒定班不起守护→claim 被 cleanup 收"形态本班冷启动即遇：本席写域被外来会话认领过、随该会话死亡被回收。
- `python -m zephyr.trading.process_reaper --status`＝`source=live`、`last_run=2026-10-15 10:32:22`、`scanned=65 whitelist_hits=58 killed=0 reported=2` ⇒ 写操作前提成立。
- ⚠ 进场系统态（如实登记）：`commit_pct=99.05%`、`ram_avail_gb=8.9`、`ram_used_pct=86.1%`、`cpu_pct=63.6%`、`degraded=True`、`breached=['ALERT-SYS-003','ALERT-SYS-004','ALERT-SYS-005']`、`worktree_changes=5383>50`、`stash_count=2`。⇒ 本班不并发起子代理、不复跑重型 DB 尺（15 员池 PR 按在册禁烧面条款未测），只做只读量测与追加写盘。
- 防重入：`checkpoint.md` 末段＝08 班完整游标记录（含终报与两处更正），无未完迹象 ⇒ 本班号取 **09**（台账当日在册 02–08 七班）。
- 会话注册＋claim：按 08 班在册处方"注册(pid=0)＋心跳＋acquire 串成一条命令"执行 ⇒ `REGISTERED`、`HEARTBEAT True`、`ACTIVE_SEES_SELF True`、**`acquired=7 denied=0`**、`list --session` 读回 7 条（TTL 30 分）。本班未出现 06 班的 shard 消失形制。
- ⚑ 本班**新增进场自证**（防外部重生波，在册 memory `p09-seat-files-external-regen-wipe-20261015`）：写盘前对七件做盘/HEAD/袋三面对拍＋磁盘快照与 sha256 manifest（`.runtime/tmp/st-qoder-p09-1015-09/snap/disk_manifest.txt`），写盘用 `safe_write_text(expected_base_sha256=快照值)` 的 CAS 形制，断言全部落在写盘**之前**＋块标记幂等旗。

### 2 判卷面（工序 1–2）

- 分数册四证（进场）：mtime `2026-10-15 10:31:26`／bytes `123768`／sha256 `009c7bbcf87582c29a7482842d545e6f50062f7fc436614c9326d04c04e38850`／`safe_load_all` docs=2、doc1 rows=**90** ⇒ 较 08 班终报锚点（`4f986ec7…`／84 行）**当日增量 6 行＝rows[84..89]**，批 `p07a-sector6-20261015`。
- 三面并存（读面声明制）：磁盘 `009c7bbc…`（90 行）／index `c7e5b1f8…`（105598B／75 行，与 06/07/08 班在册面逐位同）／HEAD 该馆 **0 件**。
- **逐行机械核对结果＝verdict 不可再现 0/6**（尺 `python .runtime/tmp/st-qoder-p09-1015-09/replay9_verdict.py`，PROBLEMS=0）：

| 行 | card_id（族） | 卡体 `pillars_numeric` | 册面 fails | 本班复算 fails | 判定 |
|---|---|---|---|---|---|
| rows[84] | `TDM-E-L1-AGG/calibration/02_四档风险轴前向收益单调` | mono≥0.6／ic≥0.02／ic_ir≥0.3／regime 同号／oos 同号 | `mono 0.400<0.6`、`ic 0.0069<0.02` | mono FAIL、ic FAIL、ic_ir **NO_FACE**、regime PASS(−/−)、oos PASS(+/+) | fail，门柱未走样 |
| rows[85] | `TDM-E-L1-S0-1/calibration/03_market_scope_sentiment_series` | 同五柱 | `mono −0.224`、`ic −0.0234`、`oos_sign_flip` | 三 FAIL＋regime PASS | fail，未走样 |
| rows[86] | `TDM-E-L2-02-1/calibration/02b_RRG象限迁移_在册10_26双EMA口径版` | 同五柱 | `mono −0.103`、`ic −0.0165`、`regime_sign_flip`、`oos_sign_flip` | 四 FAIL＋ic_ir NO_FACE | fail，未走样 |
| rows[87] | `TDM-E-L2/ablation/02_板块候选池整体边际` | 同五柱 | `mono −0.758`、`ic −0.0605` | 二 FAIL＋regime/oos PASS | fail，未走样（判官路由按卡体键集不看 family＝在册裁定①，本班未另判） |
| rows[88] | `TDM-E-L2-09/calibration/04_业绩预增催化剂腿` | 同五柱 | `mono −0.100`、`ic −0.0277` | 二 FAIL＋regime/oos PASS | fail，未走样 |
| rows[89] | `TDM-E-L1-S5/calibration/03_derived_signal_shock_panel` | 同五柱 | `mono 0.309`、`ic 0.0166` | 二 FAIL＋regime/oos PASS | fail，未走样 |

- 全册位移：`verdict` Counter＝**fail 88／pass 2**（08 班在册 82/2，＋6 全入 fail）。负结果如实入册核对＝6 行全部在册、无缺行、无被改写形态（only-add 面：行数 84→90、`kind` 全 `exam`）。
- IS/OOS 符号观察（本批 6 行）：`oos_ok=True` 4 行（rows[84]/[87]/[88]/[89]）／`False` 2 行（rows[85]/[86]）；与 `fails` 是否含 `oos_sign_flip` **逐行一致**（尺内置该校验，0 冲突）。
- **pass 行红线与升级（工序 4）**：本班新行 0 枚 pass；在册两枚 rows[76]/[78] 本班**实测复量两腿**＝`ic_ir=None`（`unjudged.numeric_keys_no_machine_face` 已如实申报）＋`net_bucket_medians` 十项全 NaN＋`round_trip_cost_bp=nan` ⇒ **两腿未齐，本班零升级**（铁律：fail 永不升级；pass 未过红线亦不升）。TDM 挂接记录＝无新增。

### 3 归因四分诊（工序 3；6 条 fail 全路由，路由表见信箱件）

| 行 | 分诊定性 | 路由单据 |
|---|---|---|
| rows[85] | 信号真无效（方向面；换手 0.9994 撞成本墙） | 方向单 → `feedback/to_miners.md` 09 班 §1 |
| rows[86] | 实现/机判面问题（卡体自报 `machine_face_gap`：八格档计数无机判面） | 修改单 **修⑫ 形三** → `to_impl.md`；方向单附"禁在本卡换口径重跑" |
| rows[87] | **判据问题**（有符号柱使镜像稳定＝fail，全册该簇唯一 1 行） | 呈批 **P-6** → `to_impl.md` §2；本班**未**自改方向、未判死 |
| rows[88] | 数据分母待核（n=1393 vs 同窗 1621，差 228 观测） | 缺数单（待核 2 笔之一）→ `feedback/to_datasource.md` 09 班节 |
| rows[84] | 实现/申报面（`n_buckets_used` 10 vs 实际 4，与 rows[72] 两代同错） | 修改单 **修⑫ 形一** → `to_impl.md`；另列入复考排程第 2 项 |
| rows[89] | 口径面（毛 IC +0.0166 而净桶全负；净面无柱消费） | 修改单 **修⑨ 追加面** → `to_impl.md` §1 第二行 |
| 全 6 行 | PE 影子披露腿在册零产出（应报 rows[86]/[87] 未报）＋`min_obs_per_bucket` 零读取 | 修⑫ 形二／形三（同一病并一条，不拆号） |

- 对照申请单（[对照]→⑥席）：本班**零新开**，理由与在册前置写在 `to_impl.md` 09 班 §3；06 班未销的 4 行扩面不重复派。
- 本班新开单号＝`修⑫`（1 条）＋呈批 `P-6`（1 条）＋缺数待核 2 笔；在册定义现止于 **修⑫ / P-6**；`修⑩` 仍悬空（本席未补写）。

### 4 结构性观察（工序 6，本班 3 条）

- **S-7（家族级，本班主条）**：**门柱是"有符号阈值"，于是"反向稳定"与"零信息"在分数册里同形**。rows[87] 实测 `mono −0.758`（镜像 −0.6 已过线）、IS −0.0605、OOS −0.0740 同号、bear/rebound 同号＝5 柱里 3 柱过，仍 fail；rows[86] `mono −0.103` 属信息量近零，两行 fail 串写法完全同类。全册该"镜像簇"命中 **1/88＝1.1%**（判据＝`mono≤−0.6 且 regime/oos 同号`）。后果：③④席无法机读区分"这条轴有信息但假设方向错"与"这条轴没信息"，而事后翻方向＝数据挖掘、无在册通道 ⇒ 本席按铁律只呈批（**P-6**）不自改门柱。
- **S-8（口径换代，跨批不可比）**：净/成本面在本批**首次产数**——全册四态分类＝nan_only 32／all_neg **6（恰为 rows[84..89]）**／has_pos **0**／no_list 52。⇒ 分数册现存"毛口径代"（≤rows[83]，净面 NaN）与"毛＋净双口径代"（本批）两代，任何跨批比较 ic/mono 或按"扣费可实现性"筛选的尺都必须**按代分账**；而 `pillars_numeric` 无成本柱＝净面只显形不判罚，两枚 pass 行仍在毛口径代里挂着。
- **S-9（落地面与本席观测纪律）**：①分数馆 90 行现值载袋 3 只、**回退弹 5 只**（较 08 班 3 只再增），HEAD 仍 0 件，本席 15 只袋全 pending／done+dead＝0 ⇒ 判卷结论的 git 落点连续第三班为零，唯一抢救面是主区工作树＋队列 blob（队列一旦被 purge 即失）。②本班值守内**上游面值两次推进**：分数册 84→90 行（10:31 面）由 ⑦ 席批次推动；`calibration_exam.py` 工作区面被他会话在途改（+15/−62，摘除影子披露腿）⇒ 本班判卷一律锚 **HEAD 码面＋磁盘册面**两面对表，工作区面不作判据、不代修，只登记两态。③本席自犯一处：进场先跑了全仓 `grep -rn`（超时转后台），后改窄面 `--include=*.py src scripts` 才拿到"零消费者/零读取"结论——**全仓 grep 在 5000+ 脏件面不可用**，恒定班取证请直接指定目录与扩展名。

### 5 交付清单（本班实际产出，七件全带）

| # | 件 | 本班动作 |
|---|---|---|
| 1 | `feedback/to_impl.md` | 追加 09 班节：修⑫（三形一单）＋修⑨ 追加面（净面首产）＋修⑧ 追加面（回退弹 5）＋呈批 P-6＋[对照] 零新开理由＋未做清单 |
| 2 | `feedback/to_miners.md` | 追加 09 班节：方向单 3 条（rows[85]/[86]/[87]）＋产量口径更新（分母 64，零新轴入占） |
| 3 | `feedback/to_datasource.md` | 追加 09 班节：**缺数单待核 2 笔**（rows[88] 228 日、rows[87] 20 日），只问分母不判缺数 |
| 4 | `iteration_history.md` | 追加 09 班轮次账（6 行入册；rows[84] 第 2 轮；全册直方图）＋复考排程 3 项 |
| 5 | `pulse/independent_signals.md` | 追加 09 班日更：分母 59→64、零新轴入占、净口径两代分账、镜像簇点名 1 行、PR 维持未获得（未复测） |
| 6 | `p09_score_officer/ledger.md` | 本节日报 |
| 7 | `p09_score_officer/checkpoint.md` | 游标推进至 `rows[89]`＋下一班必读事实 |
| — | 尺（`.runtime/tmp/st-qoder-p09-1015-09/`，只读、TTL） | `replay9_verdict.py`（6 行 verdict 复现＋oos_ok 一致性）／`census9_book.py`（申报面/桶数/净面/ic_ir 面/轮次）／`probe9_net_and_rerun.py`（净面四态＋rows[76]/[78] 两腿＋rows[72]vs[84]）／`dump9_rows.py`／`reg9.py`／`snap/`（七件盘面快照＋manifest） |

### 6 自检两轮（工序 6 末）

- **轮一（抽 3 行回卡体核门柱）**：rows[84]/[86]/[88]（行号避开 02–08 班已回核的 2/8/17/37/45/48/50/66/67/75–83）——三行卡体五柱阈值与册面 `fails` 逐条对得上（mono 0.6／ic 0.02／ic_ir 0.3 走 NO_FACE 申报／regime／oos），rows[86] 的 `regime_sign_flip {bear +0.0135, rebound −0.0768}` 与 rows[88] 的"IS/OOS 同号故不记 oos 败"两根判定都与卡体方向严格一致 ⇒ **门柱未走样 3/3**。
- **轮二（口径扩面）**：全 90 行 × 卡体 `card_id` join＝**90/90 命中**（卡池 549 distinct card_id，本班尺 `CARD_POOL` 打印面）；`oos_ok` 与 IS/OOS 符号校验 90 行 0 冲突；跨卡同读数尺（08 班在册 `dup8_metrics_identity.py`）本班复跑＝**cross_card_clusters 仍 6**、负对照 rows[83] 独占、正对照 rows[2]≡rows[10] 命中 ⇒ 新 6 行**未新增**同义簇（rows[89] 卡名带 `derived` 但读数独占，非修⑪ 形态）。
- 两轮皆零更正上一班结论之必要；旧案卷不删。

### 7 本班耗时（date 实测，不采信体感）

- 起批 `10:31:54`（冷启动首条 `date`）→ 判卷与取证尺 `~11:0x` → 落盘与提交见本节末与 checkpoint。⚑ **本班跨出 40 分钟班限**：第二个 `date` 实测读数为 `12:27:31`（在做完全部只读量测、写盘之前），起批至今＝**约 1 小时 56 分**，班限应在 `11:11:54`。本班未中途停手，如实登记不压缩。
- 超班限的主因（可归因、非笼统）：①一次全仓 `grep -rn` 超时转后台（占用一个来回），改窄面后重跑；②执行器三面对拍（HEAD 面／工作区面／册面）为本班新开的取证面，逐面各一次命令；③两次 MEMORY.md 外部变更提示带来的重读。**返工账**＝零（本班无写盘后失败重跑；断言前置＋幂等旗起效）。
- **本班终值（date 实测，覆盖上段的"写盘前"读数，旧句留卷）**：首袋入袋 `q-20261015-st-qoder-p09-1015-09-0001` `created_at=2026-10-15T12:45:18+08:00`（files=7，`base_head=d5085ba71a47f287`，本班逐件实测 `blob==disk` **7/7 OK**）→ 收锁 `released=6 denied=1`（`to_impl.md` 属 ④席活认领，本班**不放不抢**）`date=12:53:47` ⇒ 全班实际历时 **2 小时 22 分**（起批 `10:31:54`），超班限 **≈102 分**。⚑ 本节不写自指字节数；本班为补这条耗时终值另起超集袋（同七件，`blob==disk` 逐件复量后方可收工）。
- ⚑ 按 07/08 班在册教训：本节不写自指计数（不写"新增 N 字/共 N 袋"）；袋号与件面只报可在队列侧复跑的事实。

### 8 提交用旗登记（RULE-WORKTREE 显式申请制，理由沿 07/08 班在册）

- 本班写域＝`docs/_working/automation_campaign/` 下的**跨席共享追加型信箱件**（`feedback/*` 与 `iteration_history.md` 由 ②④⑤⑥⑦⑧⑩ 席同文件追加），车道 worktree 内副本落地后仍须与主区面合并＝自造第二写手 ⇒ 用 `--allow-non-worktree`。
- 七件 claim 首串＝`acquired=7 denied=0`；本班终报前续活重 claim 时**变 6/1**＝`feedback/to_impl.md` 被**活会话** `st-qoder-p04-1015-05`（④矿工席第五班）认领。本班处置＝按在册 memory `seat-claim-keeper-duality` 处方**不抢不放**，改走 `--allow-overlap`，并先自证纯新增：`difflib` 对拍本班盘前快照 vs 现面＝**minus 0／plus 30**（＝本班 09 班节整块，零删除、零改写他席行），`startswith(快照)`＝True ⇒ 本席那次写盘（CAS 通过）未覆盖 ④席内容，④席后到认领只是锁、不是新字节。**故本班用 `--allow-overlap`**（旧句"本班未用"作废，留卷不删）。
- ⚠ 交接风险如实呈交：`to_impl.md` 现面含本席 09 班节，而 ④席在其认领后若按**旧读面**整档写回（非 CAS），本席该节有被蒸发之虞（在册 memory `hot-file-wipe-forensics-20260918` 同型）。本席快照留于 `.runtime/tmp/st-qoder-p09-1015-09/snap/to_impl.md`（sha `3b833b98…`），下一班若见该节消失，先对拍本快照再重投超集袋，勿判"⑨席未出单"。
- 消息正文含代码路径指针（`calibration_exam.py`/`card_binding.py` 行号）而袋内零代码件 ⇒ 首行带 **`[docs-only]`**（08 班在册堵点正解）；每袋带全 7 件（07 班 S-2 交付纪律）。


## 2026-10-15 ｜ st-qoder-p09-1015-10（⑨成绩官第十班：当日增量＝**4 行**全判；主产出＝对照族 OOS 路级根因＋新单 修⑬＋呈批 P-7＋〔对照〕1 条＋`&&` 短路取证自犯自更正）

> **读面声明（本班正文原样跑）**：判卷锚点＝快照 `.runtime/tmp/st-qoder-p09-1015-10/score_snapshot.yaml`（磁盘面 sha256 `d8a6fd8d52f749cecf73c8f02e931d936df020702bfc548bfb97778476cbf949`／129267B／docs=2／doc1 rows=**93**／mtime `2026-10-15 15:13:49`，较 09 班终报锚点 `009c7bbcf87582c2…`／123768B／90 行＝增量 3 行 rows[90..92]）。**本班写作期间册又长**：现值 `b0c9a370fcfc5b080c0b4171…`／130320B／rows=**94**／mtime `15:41:28`（第二快照 `score_snapshot_1542.yaml`）⇒ 本班追加判 rows[93]，**实判 4 行**。index 面 `git show :docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`＝`009c7bbcf87582c2…`／rows=**90**（09 班磁盘终面已被吸收入 index）；HEAD 面该馆 `git ls-tree -r --name-only HEAD -- docs/04_research_records/backtest/scores/`＝**0 件**。本班未动分数册任何字节、未动任何阈值与门柱。

### 1 判卷表（增量 4 行，逐行回卡体；在册尺 `replay9_verdict.py` 对双臂族与 argv 行段均不走，本班另起两把尺）

| 行 | card_id | 族 | verdict | 本席机械复现 | 门柱走样否 |
|---|---|---|---|---|---|
| rows[90] | `TDM-X-R1-01/comparison/07_…五态仓位锚定版` | comparison（双臂） | **blocked** | `book_channel:bind:FileNotFoundError: docs\_working\fexam\indicator_exam_scores_v1.yaml`，metrics 空 ⇒ **不占 fail 分母、不翻卡**（按卡注纪律） | 不适用（零柱判罚） |
| rows[91] | 同上 | comparison（双臂） | **blocked** | `book_channel:bind:MemoryError: Unable to allocate 234. MiB for shape (30676538,) object`，metrics 空 | 不适用 |
| rows[92] | 同上 | comparison（双臂） | **fail** | 六柱逐一回卡体：`maxdd_improvement 10.32 >= 5.0` 过／`sharpe_delta 0.082 >= -0.1` 过／`turnover -0.978 <= 8.0` 过／`cost_tier 40bp 档 open_sharpe 0.1635 >= 0.0` 过／`missed_crisis_triggers 0 <= 0` 过／**`oos_same_sign` ic_delta_oos=NaN ⇒ 一票否决**；两柱（no_hysteresis／whipsaw）由本跑让与另一跑（`arm_pillars_owned_by_other_run`）。**verdict 与 fail 集 100% 再现** | **未走样**（阈值全部逐字取自卡体 `pillars_numeric` 八键） |
| rows[93] | `TDM-P-P2-04/calibration/06_减仓参与率压力对次日价格路径` | calibration | **fail** | `ic_mean -0.0121 < 0.02` 败／`ic_ir -0.068 < 0.3` 败／`regime 反号 (bull +0.0060, bear -0.0334)` 败／`oos_same_sign` **过**（-0.0084 与 IS 同号）／`mono_spearman` 无面且**如实披露**。verdict 再现 | **未走样** |

- IS/OOS 符号观察：rows[92] IS 侧配对 IC 差 `ic_delta_is=-0.00144`（开臂 IC **劣于**关臂 0.0014，绝对量级 1.4e-3 近零）而 OOS 无读数；rows[93] `oos=-0.0084` 与 `is=-0.0121` 同号＝oos 柱过，败在强度与稳定性而非符号。
- 负结果如实入册核对：rows[90]/[91] 的 blocked 未被写成 fail、未翻卡、`n_trial_ledger` 零消费（按卡面 note 原文），本班核对＝两行 `metrics={}` 且 `pillars_all_pass=false` 未被用作结论 ⇒ **如实**。

### 2 结构性观察（家族级，本班≥1 条硬保底＝出 3 条）

1. **对照/消融族 10 行双臂的 OOS 配对面 10/10 无读数，7 行唯一败根即此** ⇒ 该族的"OOS 稳定性"门柱自建册起**从未被判过**；同册 calibration 族 57 行、ablation 1 行 `oos_ic` 有实数 ⇒ 反证不是窗/数据整体不可得，而是**双臂路**的因（三因未分账见修⑬ 形一：`len(m)<60`／某侧 `std()=0` 恒常数／卡面未申报窗，三者在 `:226`+`:97-98`+`:222-224` 产出同一个 NaN，而文案固定写"样本不足"——rows[17] 的卡面 `oos_window_ref=null` 是已铁证的第三因）。
2. **`ic_ir_min` 柱在全册呈"要么无面、要么判败"的两态形制，0 次过线**：94 行中 `ic_ir` 有实数＝**4 行**（rows[73]/[74]/[83]/[93]），4/4 全记 FAIL；其余＝None 55 行＋键缺席 35 行 ⇒ 该柱从未产生过一个"过"的观测。这与在册修⑥（申报腿）、修⑨（产数腿）同族但**本班新量到的是分母面**：0.3 阈在现值 4 个读数上全灭，属"门槛与 ICIR 实际分布不同代"的候选，本席**不自裁**（若 Owner/⑩ 认为该谈阈值，须走判据通道；阈值数字本席一字未动）。
3. **同一张卡 7 轮里 5 次出分全败于同一根、2 次装载不出**（卡 07）⇒ 重跑不产生信息增量；而 blocked 两行的成因是**磁盘已修、HEAD 未落**（`exit_simulator.py` ` M`＋`git show HEAD:` 面对 `SCORES_YAML` 零命中）＋**族驱动器整件未跟踪**（`comparison_exam.py` `??`）。这与在册修⑧（分数册三面分叉）是同型病的不同对象，本席按追加面记，不另立号。

### 3 pass 行与升级（本班零升级）

- 全册 pass 仍＝**2 行**（rows[76]/[78]，同落 `lu_count_z20` 一根轴，06 班在册 corr=0.9998）⇒ **独立通过轴仍＝1**。
- 本班**零升级 verified**：两枚 pass 的 `ic_ir` 无面＋净/成本面 NaN 两腿在册未齐（09 班禁烧面条款，本班未重跑读数）。铁律：fail 永不升级——本班 4 行里 0 枚 pass，无升级候选。
- TDM 挂接记录：本班无 pass 行 ⇒ 零挂接；`TDM-X-R1-01` 节点的 `confidence` 写回面**本班未动**（卡 07 `lineage.confidence_writeback` 申报的真源），该节点在册 11 行全 fail/blocked。

### 4 归因四分诊路由（4 行 100% 路由，每行一条）

| 行 | 路由 | 落单处 |
|---|---|---|
| rows[90] blocked | **实现＋落地面**（旧路径修复未入 HEAD；驱动器未跟踪） | `to_impl.md` 修⑧ 追加面（不新开号） |
| rows[91] blocked | **实现**（234MiB object 数组装载；与本班 reaper 实测 `commit_pct=83.77%` 同窗，属容量/装载面） | `to_impl.md` 修⑧ 追加面第二列 |
| rows[92] fail | **实现/判据口径＋需对照**（非信号无效） | `to_impl.md` **修⑬**＋**呈批 P-7**＋**〔对照〕**给⑥席；`to_miners.md` 路由更正＋家族收敛建议 |
| rows[93] fail | **信号真无效（强度与稳定性面，第 1 轮不判死）** | `to_miners.md` 产量口径与空白轴地图（该对象第 1 轮，零 mined_out 申请） |

### 5 自检两轮

- **轮一（抽 3 行回卡体核门柱）**＝rows[92]/rows[66]/rows[17]（三行同族不同代）：rows[92] 六柱逐字对卡体八键、rows[66] 同卡 off 跑第 2 次读数对拍（`turnover_delta_annual_x` 与 `ic_delta_is` 与 rows[92] **逐位同**，`maxdd_improvement_pp` 11.53 vs 10.32 **不同**——本班未定性，列入下一班可查面），rows[17] 卡体 `oos_window_ref=null` 铁证第三因 ⇒ **三行门柱均未走样**（阈值零自拟）。
- **轮二（全册 join）**＝94 行 × 卡体 `card_id` join **94/94 命中**（卡池尺同 09 班口径）；双臂尺 `replay10_dualarm.py 0 92` PROBLEMS **0**；校准尺 `replay10_calib.py 93 93` PROBLEMS **0**。
- ⚑ **在册引用更正（旧案留卷不删）**：09 班 checkpoint 写"判卷尺复用＝`python .runtime/tmp/st-qoder-p09-1015-09/replay9_verdict.py 84 89`（**改末两参换行段**）"＝**不实**：本班实测该尺**无 argv 读取**（第 77 行 `range(84, 90)` 硬编），传 `93 93` 输出对 rows[93] 零命中（grep 计数＝0）。本班新尺 `replay10_calib.py`/`replay10_dualarm.py` 才支持行段；下一班请改用新尺。
- ⚑ **本班自犯并当场更正（旧案留卷）**：本班曾拟写"`find docs` 在本仓给假阴性"——**该结论错**。真因＝本席把 `ls`/`find`/`git ls-files` 用 `&&` 串成一条，首段 `ls docs/_working/fexam/` 失败（目录确实不存在）即**短路**，后两段**从未执行**，于是"零输出"被本席当成"零命中"的测量结果。后台那条命令跑完后本班回读其原始输出＝`find docs -name "*_exam_scores_v1.yaml"` 5 枚全命中、`find . -name "*indicator_exam_scores*"` 在 `.aidrafts/<各会话>/docs/_working/fexam/` 多枚命中。⇒ 交付正文（修⑧ 追加面）按**更正版**落字，并新增一条车道草稿树第二真源风险；取证纪律入 checkpoint 下一班必读。

### 6 独立信号清单与耗时

- `pulse/independent_signals.md` 本班节已更（零新轴入占、分母 64→65、新对照基准＝comparison 族 OOS 10/10 无读数、PR 维持在册"仍未获得"）。
- **本班耗时**：起批 `date` 实测 `15:15:49`（reaper 状态行时间戳）→ 落六件前实测 `15:5x`＝**跨出 40 分钟班限**，如实登记（成因：①册在本班写作期间又长 1 行，须追加判卷与两把尺；②卡 07 卡体 175 行全读＋双臂判官源码三处定位；③旧路径件存在性取证**重做一轮**＝本席把 `&&` 串命令的首段失败当成后两段的读数，自犯并当场更正，见 §5 补条）。
- 堵点：无提交堵点记录前状态＝本班六件走 `--enqueue` 正门（见下节）。

## 2026-10-15 ｜ st-qoder-p09-1015-11（⑨成绩官第十一班：当日增量＝**2 行**全判；主产出＝新单 修⑭＋修⑮＋呈批 P-8＋〔对照〕1 条＋**修⑧ 追加面：回退弹出局·本席 17 dead/1 done**）

### 1 冷启动与防重入

- `python --version`＝**3.12.8**；`date`＝`2026-10-15 16:11:36`（起批实测，不采信体感）。
- `python scripts/lock_files.py cleanup`＝**CLEANED 6 枚死锁**（⑦/⑧B 席 ledger+checkpoint 四枚＋`TDM-P-P2-04__calibration__06/__07` 两张卡体锁）＋**SALVAGED 7 件**，含 `data/strategy_intake/web_cards/20261015_p04_*` 两件、`to_datasource.md`/`to_impl.md`/`p04_scout_web` 两件、死会话 `st-qoder-p01-1015-10` 与 **`st-qoder-p09-1015-10`**。⚠ 本席上一班会话被机器判死（其袋死因见 §5，与本次 salvaging 一致）。
- `python -m zephyr.trading.process_reaper --status`＝`source=live`、`last_run=2026-10-15 16:11:47`、`scanned=30 whitelist_hits=16 killed=1 reported=3`、水位 `ram_used_pct 67.3`／**`commit_pct 84.33`**／`cpu_pct 31.2`／`degraded=False`。⚠ `git status --porcelain` 在该命令内**超时 60s**（WARNING 一条）＝工作区脏面过大，本班据此把取证一律改**窄面**（`--include=*.py src scripts` 与逐路径查询），未跑全仓 `grep -rn`。
- 防重入＝读 `checkpoint.md`：10 班已交全报（含"本班耗时"节）并推标至 rows[93] ⇒ 判**上一班已完**，本班取当日第 **11** 号 `st-qoder-p09-1015-11`。
- 会话形制＝`SessionRegistry().register(SID, pid=0, held_files=[7 件], task_files=[7 件], is_breaking_change=False)`＋`heartbeat`＋`list_active` 自见＝三证齐；claim＝`lock_files.py acquire-batch` 与 reg **串成一条命令**（08 班在册处方）⇒ **`acquired=7 denied=0`**，TTL 30 分。

### 2 判卷面（工序 1–2）

- **读面**：本班 16:11:36 进场锚点＝磁盘 `8903ef9e9c731fdc…`／131320B／rows=**95**（mtime 15:55:38）；终报前重测（S-3 纪律）＝**册面又长一代** `d77773545f5b4cc7…`／132248B／rows=**96**／mtime `16:28:53` ⇒ **在册第二次"一班之内册面两代"**，增量按终面＝**rows[94]＋rows[95] 两行**。index `git show :<册>`＝`009c7bbcf87582c2…`／123768B／rows=**90**；HEAD 该馆 **0 件**。
- **旧行未被改动自证**＝与 10 班快照 `.runtime/tmp/st-qoder-p09-1015-10/score_snapshot_1542.yaml` 逐行 `json.dumps(sort_keys)` 对表：rows[0..93] **byte changes=[]**，唯一新增下标 `[94, 95]`。⇒ 本班判卷面即"两行"，无重判、无回填。
- 逐行机械核对（尺＝`replay10_calib.py 94 94`／`95 95`，两跑 **PROBLEMS 0/0**，门柱**未走样**）：

| 行 | 卡 | verdict（册=尺） | 柱账 |
|---|---|---|---|
| rows[94] | `TDM-P-P2-04/calibration/07_冲高反弹幅度对次日收益与减半阈值落点`（panel，第 1 轮，`p08b-1015-04-card07`） | `fail`＝`fail` | **实败 2**（`ic_mean −0.0271<0.02`、`ic_ir −0.1357<0.3`）／**过 2**（`oos_same_sign` oos −0.0250 同 IS 号、`regime_same_sign` bull/bear 皆负）／**无面 1**（`mono_spearman` 已如实进 `no_machine_face`） |
| rows[95] | `TDM-E-L9-A01/calibration/02_日线动量截面`（panel，第 2 轮，`st-autoplan-verify-20261015`） | `fail`＝`fail` | 同形：实败 2（−0.0403／−0.2539）、过 2、无面 1；`n 1621` |

- 负结果如实核对＝两行皆在册负结果，`fails` 串两根实数柱逐条与卡体阈值对得上；`oos_ok=true` 与尺判 `oos_same_sign PASS` 一致（该"真"的独立性受 修⑮ 影响，本班如实登记但**不改册面一字**）。
- IS/OOS 符号观察＝两行**方向皆为负**且 IS/OOS/牛熊三处同号（rows[94] `−0.0271/−0.0250/−0.0223/−0.0299`；rows[95] `−0.0403/−0.0518/−0.0386/−0.0308`）⇒ 属"方向与卡面假设一致、强度不足"形，**不是**"方向反号"形；全册该形态（谓词见 §5）＝**10 行／7 张卡**。

### 3 结构性观察（工序 6，本班 3 条，家族级）

- **S-1（panel 路中心柱恒失明，簇 3→6）**：`calibration_exam.py:268` 在 panel 返回体里把 `mono_spearman` 写成**字面 None**（且 `:272` `bucket_medians=None`＝分桶响应从未算）。册面 panel 且冻该柱＝**6 行**（rows[73]/[74]/[83]/[93]/[94]/[95]），6/6 None、6/6 fail。**家族级后果**＝卡面命题写"单调"的那根柱，在这 6 次考试里**一次都没被检验过**；且本班两行新件**都**落在此簇 ⇒ "单调性被否"这句在账面上无据。→ 修⑭。
- **S-2（`oos_same_sign` 不是样本外检验，且逐卡独立性差 5 倍）**：`ic_mean` 由**全窗**序列直算、从不按 `window.in_sample` 切片，`oos_ic` 是其子段，fails 串却把参照量标成 `is=`。实测分母＝IS **1212** 日／OOS **666** 日／并集 **1878** 日 vs 册面 `n=1859` ⇒ OOS 段占参照量 **35.8%**（rows[94]/[93]）；而 rows[76]/[78] 卡面 OOS＝126 日扣留面，占 n=1846 约 **6.8%**。材料度＝冻该柱 **73 行**／两侧实数咬合 **61 行**／fails 含 oos **40 行**／该柱披露无面 **0 行**。⇒ 同一根柱在 61 行上"咬合"，但其独立性随窗而变，账面看不出；本班两行 fail 定性不受影响（各有两根实数败柱）。→ 修⑮＋〔对照〕。
- **S-3（卡内散文与机器柱极性互斥，全册仅 1 卡明文授权反向计分）**：rows[94] 卡体同时写"假设…单调负"＋"\|rho\|>=0.6…反向同号**同样计分**…须在结论里写明证伪"＋`ic_mean_min: 0.02`（带符号正下限）⇒ **假设成立必败、只有假设被证伪才可能过**，且"写明证伪"在分数行无承载字段。精确谓词（三词分别 `grep -rl`）＝全卡池 550 件命中 **1 件**＝本卡；不随关键词粗筛夸大（本班第一次粗筛按"绝对值"关键词得 14 件，已作废为材料度、仅用于定位候选）。→ 呈批 **P-8**。
- **S-4（落地链风险换形，非降级）**：分数馆旧面袋 `st-scorehome-20261014-0001..0007` **全 dead**、pending 仅剩 1 袋且不载该馆 ⇒ 07–10 班在册的"旧袋回退"威胁由死信终结；**新态**＝现值 96 行**无在途载体袋**、HEAD 0 件、index 落后磁盘 6 行／8480B ⇒ 唯一存活处＝主区工作树（第六态）。同时本席今日袋数四态换代＝**17 dead＋1 done**。→ 修⑧ 追加面。

### 4 pass 行与升级（工序 4，本班零升级）

- 红线核查对象＝rows[94]/[95] 皆 `fail`，按铁律**永不升级**，本席无升级动作。
- 在册两枚 pass（rows[76]/[78]）＝**本班未重烧**（09 班在册禁重烧且册面该两行字节未变，判据＝§2 的 byte-identical 对表）⇒ 两腿仍为在册读数（`ic_ir=None`＋净面十桶全 NaN＋`round_trip_cost_bp=nan`）＝**未齐，不升 verified**、无 TDM 挂接新增。
- 迭代史＝已追加两对象（rows[94] 第 1 轮新对象；rows[95] 同卡第 2 轮，非 修⑪ 双胞胎，逐字段差已列）。

### 5 归因四分诊路由（工序 3，2 条 fail 全路由，每行至少一条）

| 行/对象 | 分诊 | 路由去向 |
|---|---|---|
| rows[94] 强度不足＋方向证实 | **方向单** | `to_miners.md` 本班节第 1 行（第 1 轮不判死；禁反号重挖，通道在 P-8/P-6） |
| rows[94] 卡内极性互斥＋散文柱无落点 | **判据问题→呈批草稿**（禁自改门柱） | `to_impl.md` 本班节 **P-8**（A 取绝对值＝改判据须 Owner／B 加观测标签＝同 P-6 选项 A 合并排期／C 反号 preregistered 新卡） |
| rows[94]/[95] `mono_spearman` 无面 | **实现问题→修改单** | `to_impl.md` **修⑭**（panel 路生产腿，零阈值改动） |
| rows[94]/[95] `ic_mean` 全窗含 OOS | **实现问题→修改单**＋**对照申请单〔对照〕** | `to_impl.md` **修⑮**；〔对照〕给 ⑥ 席（唯一变量＝只取 `in_sample` 段重算，禁动窗与阈值） |
| rows[95] 同卡 2 轮同结论 | **方向单（家族收敛候选）** | `to_miners.md` 第 2 行（前置＝修⑮/修⑭ 落地，"先修尺再谈封矿"沿用 04 班在册顺序） |
| 6 行 panel fail 的账面读法 | **读数遮蔽告警** | `to_miners.md` 第 3 行（勿把"未检验"读成"被否定"；`ic_ir` 有实数仅 6/96 且 6/6 FAIL） |
| rows[94]/[95] 数据源 | **缺数单＝零新开** | `to_datasource.md` 本班节（五面皆实数；窗内不缺日，实测 1212/666/1878 登记不开单） |

### 6 独立信号清单（工序 5）

- 本班**工具实跑**：`signal_orthogonality.py pool-report --pool .runtime/tmp/st-qoder-p09-1015-04/pool6` → `n_members=6`、`n_common_dates=1855`、**PR=2.1272**（与 04 班逐位同＝复现确认，非新增读数），报告件 `.runtime/tmp/st-qoder-p09-1015-11/pool6_report_11.json`；相关矩阵两例已摘（`avg_abs_ret`↔`_z20`=0.7399 逾 0.3；`avg_abs_ret`↔`lu_count_z20`=0.1331 达标）。
- **15 员池缺席如实注明**：`factor_signal`/`factor_feature_value` 各 0 行（三度同值，本班未第四次重烧）；`pool-report --pool` **无默认值**（本班 `--help` 复证），故 15 员池 PR 仍**无源**；在册叙述值 4.4 继续标"未复现"。
- 新对照事实：本班两行对象（`TDM-P-P2-04`／`TDM-E-L9-A01`）**均不在 pool6 六员内** ⇒ 正交闸对本班新对象**未开**，勿读成"已判独立"。

### 7 自检两轮（工序 7）

- **轮一（抽 3 行回卡体核门柱）**＝rows[94]（本班尺逐柱打印，5 柱集与卡体 `pillars_numeric` 键集逐位同，阈值 0.6/0.02/0.3/true/true 未走样）；rows[95]（同）；rows[92]（双臂族，`replay10_dualarm.py 90 93` 复跑 **PROBLEMS 0**，含 rows[90]/[91] `blocked` 两行 reason 原样再现＝FileNotFoundError 旧路径／MemoryError 234MiB）。**结论＝门柱未走样 3/3。**
- **轮二（全册 join＋口径扩面）**＝96 行 × 卡体 `card_id` **96/96 命中**，卡池 550 件；尺 `census11_final.py` 打印 `JOIN bad=[]`。并复量在册面（**因册面 sha 已换代，本班复量合法非重烧**）：`ic_ir` 有实数 5→**6 行**（rows[95] 新增，6/6 FAIL）、panel+mono 簇 5→**6 行**、三处同号负向簇 9→**10 行／7 卡**、`oos_same_sign` 冻柱 72→**73 行**、咬合 60→**61 行**；rows[94]/[95] 的 metrics blob 全册**独占**（无重复行）⇒ 08 班 修⑪ 的 6 对簇**面未变**（旧行零改动的推论，非重跑）。
- **本班自犯并当场更正一笔（旧句留卷）**：本班 §5 路由表首稿曾把 rows[95] 写成"首轮新对象"，与尺打印"该卡行数＝2（rows[74]/[95]）"矛盾——正解＝**第 2 轮**；已按实测改写，迭代史与 to_miners 两处同步。另：本班第一次读面（16:11）报 rows=95 在当时为真，终报按 S-3 重测为 96，两值并录不互相覆盖。

### 8 本班耗时与堵点（date 实测，不采信体感）

- 起批 `16:11:36` → 写盘前实测 `date`（见提交行读数）**≈ 65 分钟**，**跨出 40 分钟班限**（09/10 班同题续条）。成因三笔＝①本班**册面两代**，终报前须重测并补判 rows[95]（S-3 纪律）；②队列四态发现 17 dead，须逐袋读 `dead_reason` 聚合成因；③修⑮ 需要窗分母实测（CH 三条计数）＋码面行号取证。未压缩、未美化。
- 提交堵点＝**本班按 08 班在册处方，提交消息首行带 `[docs-only]`**（七件皆文档件、零代码件，避免 `MESSAGE-CLAIMS-CODE-BAG-EMPTY`）；袋带全 7 件（07 班在册交付纪律）。⚠ 已如实登记的风险＝七件工作区面均比 HEAD 大 3036–14662B，含他席未落地条目，袋＝整档快照 ⇒ 若落地仲裁按在册 ours=HEAD 语义，本班袋可能再入 `双侧皆改真冲突` 死信族；本席不代修、不 requeue 他人袋。

### 9 本班 §8 耗时句更正（旧句留卷不删）

- §8 与 checkpoint 同题句写"**≈65 分钟＝跨出 40 分钟班限**"＝**落笔前估算、非 date 实测**，违本岗自立口径（08 班在册同款错，本班再犯）。实测＝起批 `16:11:36` → 七件 CAS 写盘完成时 `date`＝**`16:41:35`**＝**30.0 分，班限内**。成因三笔（重排后仍成立）＝册面两代须终报重测＋17 只死袋逐袋读 dead_reason＋CH 窗分母实测；提交段耗时另计入 §10，不与本班判卷段合并报"累计"。

### 10 本班提交面与用旗登记（date 实测；袋字节已逐件对拍）

- 首投 `16:44:19` **被锁外预检拦**＝`[WORKTREE-REQUIRED] 非 worktree commit 且存在其他活跃 session`（列 7 席名，rc=8，预检 18.3s＝未白烧锁）。正解按 07/08/09 班在册走**显式申请制**：重投加 `--allow-non-worktree`（AI 可用旗，前置＝确认 gateway 只提交本 claim 件、不搭便车他人 WIP；本班七件全程 `acquired=7 denied=0` 且 `ENQUEUE-RENEW: claim 续租 7/7 件（ttl=7200s）` 印证），GW 自动追加 `[GW:<sid>:non-worktree]` 审计标记。
- 首袋＝`q-20261015-st-qoder-p09-1015-11-0001`（files=7，`created_at 16:46:01`，`base_head=63a5ee4c66`，§1–§9 皆在内）。
- **袋字节对拍＝7/7 `blob_sha256 == 磁盘 sha256 == blobs/ 件实读 sha`**。⚠ 本班自犯并当场更正：对拍尺首版按记忆里的键名取 `sha256/content_sha256`，而袋面真名是 **`blob_sha256`** ⇒ 读出 `rec=None` 得 **7/7 假 MISMATCH**；且 `blob_ref` 是**相对队列根** `.runtime/commit_queue` 的路径而非 CWD（＝08 班在册 `probe8_landing_face.py` 同款坑，本班复用前已改）。零"袋面缺失"结论一律先核尺的键名与根路径。
- 消息首行带 `[docs-only]`（08 班在册处方，避 `MESSAGE-CLAIMS-CODE-BAG-EMPTY`：正文点名了执行器行号与尺路径而袋内零代码件）。
- 本节的落袋＝**`-0002`（严格超集，七件全带）**；下一班按在册"末袋为超集"取 `-0002`，并复跑 `blob==disk` 对拍。
- ⚑ **本席袋生死风险如实呈报（不代修）**：今日本席 02–10 班 17 只袋中 **9 只死于 `ghost_session`（属主会话判死→自动重投被存活闸拒）**。本班会话在 drain 前退出即可能重演。本席**未自跑全队列 drain**（会连带落他人袋＝动共享态，且 lease 在他班手中），只如实登记：若本席袋亦入 dead，修因方向＝①收班序列里加"存活至落地"或②由 ⑦⑧ 写分席把本岗七件与当班袋同袋带出——属 ⑩/统筹定策面，不自裁。
