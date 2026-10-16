---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑧考工B·游标
---
# 游标

cursor: 10-16 班次 02 已交账（**出分 1 张＝连续三班 0 出分止**：改正尺真跑 `TDM-X-S1-04/calibration/02`＝panel 宽宇宙 4567 名/日、verdict=fail、rows[109]、注入面与卡面 target_source 逐字对拍；本班头号＝同卡两读法实测差 23 倍而永久册无读法申报位＋judge() 遇越表键早退使真破柱不进 fails；本族剩余 71 张六桶机械分账 A17/B7/C15/D6/E5/Z21，A+C+D=38 张在 ⑤/⑥ 补腿前任何考工班零出分＝本岗天花板 1 张/班；D 桶与 /03 两案本席自纠改判并留旧案；comparison/02 差两格非一格；同 sid 孤儿半班 15 件被抓（未造二次试次双证）本席未删呈 ⑩；本席 [BLOCKER] 追加 8 条）
last_run: 22:3x（`date` 实测 2026-10-16 23:02:12；本班＝班次 02，出分 1 张；开班 22:30:17 现测，终值以本行与收班 date 差由 ⑩ 复核，本席不写自估）
last_batch: p08-1016-02 首袋＝台账新节（§一–§七＋[BLOCKER] 8 行）＋本游标＋分数册新址 1 行＋卡 1 枚翻 examined（四件含成绩面；消息内 .py 路径系逐字引用在册读数与本班 tmp 尺面，非本席代码改动＝[docs-only]）
notes: |
  游标由本岗每批推进；监督员(⑩)可代修。
  **下一班开考规格（班次 04 实跑核对，覆盖班次 03 的 ①-⑦）**：
  ① 注入面不变：target=`close/close.shift(1)-1`（禁注 close 本体、禁 `pct_change()` 默认 pad）；工具 `_panel_metrics:251` 配对 signal[t]×target[t+1]。
  ② **正门已开**：卡 06/07 的 ⑥-07 ttl=90m 活锁于 15:34 前自然解除（`lock_files.py list` 零命中）；本席已把两张出分入册并翻 examined ⇒ **本族可考面从 6 张缩到 4 张**。
  ③ **余下 4 张（P1-02/02、P1-02/04、P1-04/04、P3-04/04）本席判"不可开"，勿尝试**：卡面冻结持仓池=多因子 top20（20 只/日），撞 `ic_exam.py:96 ic[valid<30]=nan` 地板；本席同帧双对照（seed=7）实测 20 列面 ⇒ `_panel_metrics` 回 `ic_mean=0.0000`（空序列被读成 0）+ judge `fails=['ic_mean 0.0000 < 0.02', ...]`＝把"截面不足"写成"信号无信息"的假红。开一张即造一条假成绩。
  ④ **且其因子集真源已断**：`scripts/backtest/fexam/exit_sim/prereg_frozen.yaml:23` 的 signal_source 指 `docs/_working/fexam/indicator_exam_scores_v1.yaml`——盘面查无＋`git ls-files docs/_working/fexam/` 零命中 ⇒ top20 列集当前不可复验。转 ⑥ 冻列集／⑤ 修指针（与 ⑤-1015-03 修的 SERIES_DIR 同族）。
  ⑤ **双臂 29 张的册面闸已解**（`card_binding.py:1927` 现值 `safe_load_all`，本班实测双文档 2 doc 无 ComposerError）；仍缺 NAV 接线（signal_b），属 ⑤/⑪ 产出面，本席不物化。
  ⑥ 分数册面值现测口径（禁引本游标当事实）：`python -c "import hashlib,pathlib;p=pathlib.Path('docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml');b=p.read_bytes();print(len(b),hashlib.sha256(b).hexdigest()[:16])"`；本班 16:0x 读数 131,320B/95 行（本席 +2）。promote 前置仍＝当场重拷＋difflib minus=0 硬闸＋`safe_write_text` CAS（本席两次 promote 均 written=True/equals_staging=True）。
  ⑦ **驱动已可复用**：`.runtime/tmp/st-qoder-p08-1015-04/shift04_land.py <runner> <卡面相对路径>` ＝ open_session＋心跳＋卡锁/册锁须本席＋当场重拷＋minus=0 硬闸＋CAS promote。runner 形态见 `shift04_run06.py`/`shift04_run07.py`（hs300 PIT 下推，向量化无逐日循环）。**必带 `sys.path.insert(0, ROOT)`**，否则 `_spawn_heartbeat_daemon` 报 `No module named 'scripts.ops_guard'` 而静默无守护（本席首版踩过）。
  ⑧ 卡面归属：卡 06/07 盘面含 ⑥-07 的 `oos_window_ref` 补键（`git show HEAD:<卡>` grep 命中 0＝未落地），本席袋=整档快照必然带出，已在 commit message 署名 ⑥-07；下一班若见该键已在 HEAD＝前置已由他席落地，勿再声明。
  ⑨ 门误报一条（给 ⑤/⑩）：`scripts/lock_files.py:585-597` 命名门仅在 `not tracked` 时跑；本席 15:5x acquire 卡 06 首报 `NAMING VIOLATION [N-01][N-13]`、立即重试即 ACQUIRED，同进程直调 `_is_git_tracked()` 实测 True ⇒ git 探针瞬时失败会把存量卡降级成"未跟踪新件"并报错误导。
  防重入两址并存期须两址同读（旧址 docs/_working、新址 docs/04_research_records/cross_domain；新址现值仍＝10-14 搬迁空壳 `cursor: 未开始`，本班 15:59 实测）。
  本班水位（现测命令＋时刻，非终值）：15:31 `commit_pct=88.79`、15:59 `88.7`、degraded=False、breached=ALERT-SYS-001；ALERT-SYS-003 未触发＝本席仍未拉全 A 与水位无关（见 ③④）。
  ⑩ **本班最重要一条（给 ⑩/⑥/成绩面，16:4x 补写：首版脚本因 ledger 追加 minus=1 提前退出，此行当时未落）**：N-16 文件名唯一性把新址分数册挡在 HEAD 外——旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 仍在 HEAD（盘面已删＋`git status --porcelain` 读数 `D `＝已暂存删除无人落），本席首袋与 ⑦A-01 首袋死于**逐字同一条 N-16**（`GATE-PRECOMMIT-RUN ... hook=['gate-naming']`）。本席 2 行真分＝盘面在册、HEAD 无册（`git cat-file -e HEAD:<新址>` 实测 fatal rc=128）。scorehome 七袋全死但 dead_reason 点名 ruling_registry/capability 册与 ghost_session，**是否即旧址删除腿＝本席未证**，派活前先判该格归属。
  ⑪ 下一班口径（与 ⑩ 配套）：旧址若已退役＝把 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 加回袋直接 requeue（盘面册已含本席 2 行，**勿重跑 run_card 造二次试次**）；旧址未退役则勿投含册袋。盘面册面值在值守内会继续被他席推进（本席实测 15:34=93 行→16:0x=95（本席+2）→16:4x=96（上游+1）），promote 前置仍是"当场重拷＋difflib minus=0＋CAS"。
  ⑫ 交班带锁与游标袋面（本席有意偏离 §2.9"收班即 release"，理由留此给下一班与 ⑩）：本班第二袋 `q-20261015-st-qoder-p08-1015-04-0002`（files=4）在 16:5x 实测仍 state=processing ⇒ 本席四件 claim 未 release（放了会让他会话在袋落地前改同件、落地侧判"双侧皆改"）。**注意本袋内 cursor blob＝4,479B 的旧游标（无 ⑩/⑪ 两行），盘面现值 5,714B 含之** ⇒ 下一班写游标时必须从盘面整档带袋（含 ⑩/⑪⑫），勿只写自己新增行而把这两行洗掉；本袋落地后即可 release（`python scripts/git_commit.py --release-only`）。
  ⑬ 本班收班实测分母（下一班自己复跑为准，本行只记本班时刻）：preregistered **72**（本班开班 74，-2＝本席把 06/07 翻 examined）；route 分布 dual_arm 29／series 43／event 0；series 43＝39 越表＋4 张柱全在词表且 `oos_window_ref` 齐（＝本席 §③ 那四张，仍判不可开）。尺＝`pillars_route()` 本体＋按路由取词表（本班复测确认 event 路由零命中⇒5 键尺在本族不误判）。复跑命令：`python .runtime/tmp/st-qoder-p08-1015-04/census.py`（只读零写）。
  ⑭ **本班最重要一条（给 ⑥/统筹批准面，17:29 实测）**：本族唯一"卡面全冻结、只差一格已批准臂册格"的卡＝
     `docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__02_熔断五级梯度减仓对照.yaml`。
     机械预检凭据（用 arm_protocol_binding 自家 verify_arm_quote/pending_numeric_params，零写）：ARM_OPS 引句命中
     `arm_identity`＋`arm_level_cap_multiply`；待冻数值参数＝**无**；越表柱＝**无**；r 位身份词 `基线臂日净值`/`日收益序列`
     两词均命中 `data_binding.signal_column`。批准到手下一班直接跑，**不必重判可行性**。
     另两张 feasible_now 各缺一件：`X-R1-01/ablation/03` 缺 ⑥ 给三处臂参数冻数（趋势门/降风险/预算＝"无相邻数值"）；
     `X-R1/shadow/02` 缺 ⑤ 给三根越表柱机器面（false_trigger_rate_max/forgone_gain_max_pp/loss_avoided_min_pp）＋r 位身份声明。
  ⑮ **上班两条结论被本班实测改判（勿再当事实引用）**：(a)"top20 因子集真源已断⇒列集不可复验"过强——
     `exit_sim/prereg_frozen.yaml` 的 `device.columns_cap24` 实为 24 列且逐列带 provenance，断的只是 `signal_source`
     推导指针（正解＝⑤ 指永久区真源，与 SERIES_DIR 同族，不是 ⑥ 重冻列集）；(b)"29 张 dual_arm 全缺 NAV 接线"过宽——
     feasible_now∩preregistered=3，且三张卡面自述 `blocked_on_impl: drawdown_state_machine 零引用` 已过期
     （实测 `card_binding.py:1455/:1509/:1573` 与 `sim_daily_runner.py:1364/:1403` 均在引用）。
  ⑯ **落地面新判据（给 ⑩ 派活用，本席仍不代落他人 staged 件）**：旧址 HEAD 册 73 行 == 新址盘面前 73 行**逐位同序且内容零漂移**
     （only_old=0，本班脚本断言 True）⇒ 上一班 §三 处方 1 缺的"超集性前置"已补齐，可派；旧址末笔落地＝`eb02e513f6`（10-13 23:35）
     ⇒ 全线成绩自搬家起零落地，盘面滞留 23 行＝⑦A 15／本席 2／exit 他席 3／来源名带 test/probe/plan 3（性质呈 ⑨/⑩）。
     新量代价：全库 551 张卡里 72 张用 `#rows[N]` **位置指针**，N 值域 0..95，旧址只 73 行 ⇒ **20/72＝27.8% 在 HEAD 悬空**。
     两址在 `lock_files.py list` 均无持有者＝无主 staged 残留，而根宪法 §9.4 给无主件的处方是"按 HEAD 复位并留存证"，
     与"落地删除腿"方向相反 ⇒ 该格归属仍请 ⑩ 先判，本席不自作。
  ⑰ 工具坑（给下一班省一轮）：`card_binding.py`/`arm_protocol_binding.py` 的 `--cards-dir` **必须绝对路径**，
     相对路径在 `Path.relative_to()` 崩；读 `lock_files.py list` 须 `stdout=PIPE`＋`.decode('utf-8')`（Windows `text=True` 按 GBK 吞）。
     在册尺口径：`card_binding --mode classify` 的 class A/D=0 是"绑定层不覆盖"，**不等于**考工跑不了（04 班两张真分就是自物化跑的）。
  ⑱ **双臂底座通道现状（本班实测，纠正上班游标 ⑮(a)＝处方已成就）**：`scripts/backtest/fexam/exit_sim/exit_simulator.py:72` 的
     `SCORES_YAML` 现指永久区 `docs/04_research_records/backtest/scores/2026/indicator_exam_scores_v1.yaml`（该件 exists=True，
     results 143 行/pass 78 行）；本班 `load_pass_columns()` 返回 **24 列且与 prereg_frozen.device.columns_cap24 逐列逐序相等**
     ＝内容中性（脚本 `.runtime/tmp/st-qoder-p08-1015-06/ab_dualarm.py`，零 CH 零写）。`prereg_frozen.yaml:23` 的 `signal_source`
     散文行仍写旧 `_working` 路径但**非消费面**，勿再当堵点呈报。新缺陷转 ⑤：同件 `:77-78` 的 `OUT_YAML`/`OUT_MD` 仍指
     `docs/_working/fexam/`（实测父目录 exists=False）＝10-14 搬迁波漏改的第二根指针；本席只读实测未触写者。
     断链册对拍：`broken_records.json` 对该条给 `batch=D_同名模糊命中／note=需人工确认`，而本岗指令只授 B/C 两批改指权⇒本席未自创路径未改件。
  ⑲ **下一班开考判据＝两尺合闸（本席自纠在册）**：本班三闸尺（柱全在本 route 词表＋oos 齐＋臂册格）单独用给出 3 张"只差⑥格"，
     叠 `arm_protocol_binding.triage_card` 三态尺后：`X-R1-01/comparison/02`＝`state=feasible_now`（arm_count=3/numeric_frozen=True/pending=[]/越表=[]）真只差格；
     `X-S1-01/comparison/02`＝`needs_matching_engine`（凭据：panel 横截面回放缺件，执行核 comparison 分支对两臂恒走日频标量面）；
     `X-S1-03/comparison/02_dualwindow`＝`has_arm_face=False`（卡面无臂协议声明，属 ⑥ 非 ⑤）。⇒ 上班游标 ⑭ 的"唯一"经复量成立。
  ⑳ **给 ⑤ 的补柱面边际收益（只算柱闸，不担保其余闸与格；本族 preregistered 72）**：现状柱全过闸 7/72；累加 `maxdd_delta_max`→7、
     `sharpe_vs_baseline_min`→8、`turnover_cost_gate`→11、`tracking_diff_max`→**19**、`turnover_or_cost_gate`→23、top8 仍 23（饱和）。
     无机器柱 distinct=107 根／卡次 179／只差一根柱的卡 13 张。词面分裂转 ⑥ 并名：`turnover_cost_gate`(11 卡) vs `turnover_or_cost_gate`(10 卡)。
     谓词双对照已留卷（正：`ic_mean_min` py 命中 1、`whipsaw_roundtrip_ratio_max` 2；负：`maxdd_delta_max` py=0 而卡面命中 15 件）。
  ㉑ **断供闸本族两口径**：册现值 `known_data_gaps.yaml` gaps=84 条／distinct 表 66／按在册词表 `open|no_source` 断供表 34；本族 72 张的
     lineage/data_binding 表名级命中 9 张 vs status 词表命中 **1** 张（`TDM-X-R1-03/calibration/02_宽基ETF天量与护盘滞后结构`）＝按表名级避让会白挡 8 张
     （与 ⑦ 班 repo 级 61vs38 同一纠偏形态，本族数字另立）。
  ㉒ 工具坑（给下一班省一轮）：`card_binding.load_binding_book(02_binding_book.yaml)` **裸调即在 `card_binding.py:1933` 抛**
     `arms_variant_required:[…07…, …07b…]`（这两格带 arms_variants，须显式 `--arms-variant`，禁默认第一档）；册面卡级集合=18 格，
     其中双臂格仅 07/07b 两格 `status=approved` 而两卡现均 `examined`⇒本族 preregistered 双臂卡在册格命中=0。另：`comparison_exam --dry-run`
     不传 `--binding-book` 时零写且 `book_entry` 恒 False（分诊面够用，别把它当成“册无此卡”的反证）。
  ㉓ 尺纠偏（给 ⑩/⑨）：04/05 班普查件 `.runtime/tmp/st-qoder-p08-1015-0{4,5}/census.py` 拿单一 `_CALIBRATION_JUDGED_KEYS` 量全部 72 张，
     对 `family∈{comparison,ablation}` 属**族盲**（真源按 route 分词表＝`comparison_exam.py:86`）；"两闸全过仅 4 张"只对 series 校准面成立，
     非本族可考面全貌。本班复量构成＝OD1 44／calibration 14／shadow 14（加总 72）。44 张 OD1 首次经自家执行器 `run_card_comparison(dry=True)`
     逐卡分诊凭据＝`.runtime/tmp/st-qoder-p08-1015-06/triage_od1.json`（binding_class 全 C 除 dualwindow=U；oos 齐 43/44）。
  ㉔ 落地面本班现测（禁当终值引用）：`git status --porcelain` 对两址册读 `RM docs/03_modules/_domain_backtest/exam_scores_v1.yaml -> docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml`
     ＝旧址已出 index 而改名腿未落 HEAD（`git cat-file -e HEAD:<新址>` rc=128）⇒ N-16 仍挡含册袋；本班仍只投两件文本、不动他人 staged 面。
  ㉕ **本班追加节要点（第二袋在册，给下一班三条硬事实）**：(a) 截面地板判据加强＝与信号质量无关——`_panel_metrics` 的 `n` 由
  ㉖ **本班头号＝改正尺（下一班必用，禁再按单尺判可考面）**：柱越表**不是**不开考理由——新址分数册 HEAD 现测 106 行中 75 行 `unjudged` 非空仍照常出 verdict（fail 71/pass 2/blocked 2，尺面 .runtime/tmp/st-qoder-p08-1016-01/unjudged_precedent.py）＝「越表柱由分数行 unjudged 显形」是在册实践。本族真硬闸只有一条＝截面地板 30 列（`ic_exam.py:96 ic[valid < 30] = np.nan`，本班同进程双控 20/24 列→n=0、30/120 列→n=299，且不足者被写成 ic_mean=0.0 非 nan）＋构造是否 t 日 PIT 可算（不可算＝瞎跑，禁）。同坑本线已点名三次（⑦A 06／⑧B 05／⑦c 01），本班＝第四次，见 ledger §二。
  ㉗ **真跑面起点（按 ㉖ 改正尺复量，非终值）**：series 路由 preregistered 43 张中越表 ≤2 柱者 **16** 张，其中卡面未写 top20 池者 **11** 张；尺＝`.runtime/tmp/st-qoder-p08-1016-01/pick_series.py`（只读）。⚠该 11 张的谓词「文本不含 top20」**过宽**：`TDM-P-P1-04__calibration__04` 不含该词却 entry 承 prereg_frozen 月频调仓＝仍是 20 只/日池，逐张须读 `signal_derivation` 定宇宙（承在册 endswith 过宽假扩同族）。
  ㉘ **三态尺命令原文（可复用，只读出 json 零写业务面）**：`python scripts/backtest/fexam/arm_protocol_binding.py --cards-dir D:/ZephyrAlpha/docs/03_modules/_domain_backtest/exam_cards --out .runtime/tmp/<本班sid>/apb_triage.json` ⇒ 本族 20 条臂协议凭据（无臂协议声明的卡不入该面，**禁当成「册无此卡」的反证**）；preregistered∩feasible_now=3（X-R1-01/comparison/02、X-R1-01/ablation/03、X-R1/shadow/02），各缺件逐张见 ledger §四。`triage_card()` 收 **dict 非 Path**（本席首遍传 Path 得 AttributeError，系自犯非工具缺陷，不立案）。
  ㉙ **绑定册现状与一只暗闸（给下一班省两轮）**：`docs/04_research_records/mining/ledgers/mineloop_campaign/02_binding_book.yaml` entries=18（approved 17），本族命中仅 comparison/07 与 /07b 两格且两卡均已 examined ⇒ `comparison/02` 零条目＝待 ⑥ 补格，本席**勿改用 07 的臂**（禁凭记忆补臂）。取册须 `safe_load_all` 后挑含 `entries` 的 doc；且任一带 arms_variants 的格会让**全册**装载在缺 `--arms-variant` 时抛 `arms_variant_required`（card_binding.py:1933）——分诊任何单卡都要带 `--arms-variant off`。
  ㉚ **落地面本班现测（禁当终值引用）**：分数册新址 `docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` 已进 HEAD（`git cat-file -e HEAD:` rc=0，上班 §㉔ 的 rc=128/N-16 堵点由他席 `e1033fb48d` 解除），HEAD rows=106；旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 仍在 HEAD 且停更 rows=73（末笔 eb02e513f6）；四元组对账 only_old=0 且旧址序列==新址前 73（prefix=True）⇒ 旧址＝新址严格前缀，退役判据齐（交 ⑩，本席不自删）。本族 5 枚 `#rows[N]` 对新址全解悬，含本席 04 班亲笔 #rows[93]/[94]（run_id p08b-1015-04-card06/07，verdict 均 fail）。下一班**可投含册袋**，但 promote 前置仍是当场重拷＋difflib minus=0＋CAS。
  ㉛ **停发两面读数（2026-10-16 17:51:06 现测，下一班先复量再谈 enable）**：`git merge-base --is-ancestor 23e28b2cb7 HEAD` rc=0（六件代码腿已落）而 ruling_registry HEAD 5025 行内按该三枚新裁编号谓词命中 **0**、盘面 5119 行命中 **3**＝注册表腿未落＝运行面与治理面脱钩；本席仍按原卡执行（不自判停发解除、零席 enable）。队列四态 pending 1/processing 1/done 889/dead 436（done 面非单调，判落地只认 git log 与 blob）。
  ㉜ **本班自犯两枚当场改正（旧读数不涂）**：(a) 双臂底座列集对拍首版把 `columns_cap24` 按 `symbol` 键取（真键=`column`，load_pass_columns() 返元组）⇒ 打出 cols_equal_cap24=False 假漂移；改正后 ordered/set/provenance 三项全 True（24/24 逐列逐序全等，复证上班 ⑱）。(b) 防重入首遍只读游标，已补 `lock_files.py list` 面（全表 1 行、p08 命中 0、上班 §⑫ 在途袋现 done）两尺并读。
  ㉝ **本班收班与下班首查**：本班＝纯文档袋（ledger 新节＋本游标），出分 0 张＝连续三班 0 出分（10-15 05/06＋本班），根因全在他席缺件（ledger §七 高 4 条/中 5 条）。下班首查四件＝①§五 三张 feasible_now 卡的 ⑥/⑤ 缺件是否已清（现值 comparison/02 零条目）；②§㉗ 16 张越表≤2 卡是否已按 ㉖ 改正尺真跑出分（**别再用「越表＝不开考」**）；③旧址分数册退役案是否已由 ⑩ 签；④断链三件是否已补 add（尺 `git ls-files docs/04_research_records/governance/working_ref_sweep_20261015/` 现值 0）。
  ㉞ **本班＝改正尺（上班 ㉖）首次真跑出分 1 张**：`TDM-X-S1-04/calibration/02`（panel 宽宇宙全 A，日均名数 4567/最小 230）run_id=`p08b-1016-02-x-s1-04-02`、verdict=fail、ic_mean=-0.000734、ic_ir=-0.009901、oos_ic=-0.004189、n=1665、bull=-0.003088/bear=+0.004126 异号；册 `rows[109]`，卡翻 examined。注入面 target=`close/close.shift(1)-1` 与卡面 `target_source` 声明的 `ch_data.forward_returns(close,1)`（ch_data.py:194 实读）逐字对拍。物化尺面 `.runtime/tmp/st-qoder-p08-1016-02/card_x_s1_04_02.py`（装载承 ⑦A p07 三面板 parquet 缓存，零新拉数，4.6 秒）。
  ㉟ **判读约束（下班与下游读者必知，本席 [BLOCKER] 高/中各一行）**：`calibration_exam.py:736-748` 的 `judge()` 遇越表键**立即 return**，真破门柱（本卡 ic_floor 与牛熊异号双双破）**不进 fails 只进 metrics**⇒ 按 fails 归因越表卡＝错结论。上班 ㉖ 的「越表柱进 unjudged 显形」须补此半句。
  ㊱ **取号前必扫 tmp（本席自犯证伪其可跳过性）**：本班 22:30 取 `st-qoder-p08-1016-02`，直到 22:54 才发现该 sid 下已有 **21:37–22:02 孤儿半班 15 件**（open_session/probe_faces/census_true/run_x_s1_04_02/run_x_s1_04_03/bucket_gap/pit_rerun+log）。本次未造二次试次＝双证（其 json 首字段 `dry:true`＋册内该卡按 card_id 全表扫仅 rows[109] 一行）。下班首件先 `ls .runtime/tmp/st-qoder-p08-<MMDD>-<NN>` 再定号（在册律 dispatch-engine-outage-session-failed-20261016 复证）。
  ㊲ **同卡两读法实测差 23 倍＝永久册缺读法申报位**：孤儿 `build_K` 与本席 `build_signal` 三处分叉（20 日均 volume 含否当日／K 清零锚系于突破日 vs 上次失败日／活跃突破期可否被新突破覆盖）⇒ 其 dry ic_mean=-0.016878(n=1662) vs 本席 -0.000734(n=1665)。两读皆属卡面文字许可、皆判 fail。**下班禁把任一读法当唯一正解**，须待 ⑥ 补机读参数位。
  ㊳ **本族剩余 71 张六桶机械分账（尺 `.runtime/tmp/{SID}/block_census.py`＋json，只读）**：首命中 A17（宇宙=top20/24 撞 30 列地板）／B7（kline_1min/5min）／C15（组合 NAV 双臂装置未接线）／D6（primary 5/10/20 日而 panel 无多日腿）／E5（primary 是概率/中位差/误判率＝形状不配）／Z21（待逐张）。正对照＝谓词 `30\s*只票` 全卡库命中 3 文件（尺非零）。**A+C+D＝38 张在 ⑤/⑥ 补腿前任何考工班零出分**（本岗天花板实测 1 张/班）。
  ㊴ **D 桶改判（留旧案，下班勿再当结构死案）**：旧案＝panel 路无多日腿＝不可考；新案＝腿可经注入面预补偿达成（孤儿 `excess(5).shift(1)` 配方＝⑦c 在册 t1o_t2c 同族），但真缺两腿＝①`_forward_face` 只被 `_series_metrics`(:212) 消费而 `_panel_metrics`(:251-252) 硬编码 shift(-1) 且**无视申报**（⑤）；②全库申报 `target_forward_face` 仅 8 张且全在 entry_flow 已 examined（⑥）。两腿齐前禁考工自拟起算锚。
  ㊵ **comparison/02 上班「只差一格」实测＝差两格**：该卡 `grep level_to_cap_map` 命中 **0**，五级→仓位映射只在 `arm_protocol` 散文行原文（L1 100%/L2 100% 禁新开/L3 梯度 80/60/40%/L4 0%，:50）⇒ ⑥ 先补卡面机读位（承 07 在册形态）再走 verify_arm_quote 建格。绑定册现测 entries=18/approved=17、本卡零条目；07/07b 磁盘仍 examined、07c=blocked_on_impl（三态尺 6 张 feasible_now 里 preregistered 仅 3 张：02 pending=∅／ablation03 pending=三处臂参数／shadow02 缺三根机器柱）。
  ㊶ **本席对 /03 的初判被孤儿实测证伪并当场改判**：旧案「dragon_tiger reason 仅 2026-08-07 起⇒46 日⇒不可开考」（承 ④席在册实测）；新案＝`seat_rows=620913`／`days_ge30=1146`／日均宽度 61 名⇒装置可承重，真堵＝卡面极性未钉（V1 signed ic=-0.00706 vs V2 abs-flipped ic=-0.02969，差 4.2 倍）。⇒ 转 ⑥ 钉极性；下班勿再用「跨度不足」挡这张卡。
  ㊷ **落地面本班现测（禁当终值引用）**：分数册新址盘 110 行（本班 109→110，sha16 a9532fceb0899c94）；旧址 `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 仍在 HEAD（cat-file rc=0）而新址亦在 HEAD⇒旧址退役案仍未签（本席不自删）；`git ls-files docs/04_research_records/governance/working_ref_sweep_20261015/`＝**0**（上班 §㉝④ 续期未动）；本班谓词对旧址 HEAD 读 `^  - card_id:` 得 0 行＝本席谓词不覆盖旧址行形态（非「旧址无行」），⑩ 换尺。
  ㊸ **下班首查四件（2026-10-16 23:02:12 现测为基线）**：①⑥ 是否已给 comparison/02 补机读映射位＋建格（现值零条目）；②⑤ 是否已把 `_forward_face` 接进 `_panel_metrics`（现值 :252 硬编码）；③同 sid 孤儿 15 件的归属与清理权（本席未删）；④旧址册退役案与 working_ref_sweep 入库（现值 0）。本班收班八件逐项见 ledger §七；实耗以游标 last_run 现测差计，禁写自估终值。
     `ic_exam.py:96 ic[valid < 30] = np.nan` 掩码直接决定，本班同进程读数 20/29 列 `n=0`、30/120 列 `n=419`，且 `ic_stats(空序列)` 回
     `{'ic_mean': 0.0, 'icir': 0.0, 'n_obs': 0}`（0.0 非 nan）⇒ 任何 20 列面只能产出 0 读数，"跑一张即写一条假陈述"不依赖信号好坏；本席另把自造 `A_perfect_signal_*` 探针命名证伪（iid 噪声 shift(-1) 本身无自相关，见 ledger §九）。
     (b) 本族 `#rows[N]` 指针分账＝151 个卡件中 5 张用位置指针，HEAD 旧址册 rows=73 ⇒ 悬空 3 张，其中 **本席 04 班亲笔 2 枚**
     （`P-P2-04/calibration/06`=#rows[93]、`/07`=#rows[94]，袋 19f2852467），第三枚 `X-R1-01/comparison/07`=#rows[92] 属他席；
     定性＝N-16 册未落地的下游症状，非卡面写错，本席不自改。(c) 下一班若要复用本班尺：`census2.py`（按 route 词表交叉）／
     `triage_od1.py`（44 张 OD1 逐卡 dry 凭据→triage_od1.json）／`ab_dualarm.py`（指针＋列集内容中性对拍）／`summary.py`（边际收益与断供两口径）。

<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 116227 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。
