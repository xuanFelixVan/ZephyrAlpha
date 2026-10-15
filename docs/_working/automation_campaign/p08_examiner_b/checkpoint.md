---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑧考工B·游标
---
# 游标

cursor: 10-15 班次 05 已交账（**0 出分／保底未达**，承重证据见 ledger §三与§八：本族 preregistered 72 张经四台在册机器逐卡判定＝两闸全过仅 4 张且全部冻结持仓面=月频 top20，撞 `ic_exam.py:96 ic[valid<30]=nan` 的截面地板——本席自做A/B 实测悬崖精确在 **29↔30**，空 IC 序列被 `ic_stats` 交回 0.0 而非 nan，跑一张即往永久册写一条"信号零信息"的假陈述，故不开考、不挪门柱）
last_run: 17:29（`date` 实测；开班 16:57，本班耗时约 32 分，出分 0 张）
last_batch: p08-1015-05 台账追加节＋本游标（两件套；不含分数册＝旧址未退役遵 04 班 §26，不含卡件＝本班零翻态）
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
