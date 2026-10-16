---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑪整装回测席·整装成绩台账
---

# 整装成绩台账（追加式）

格式：`## <MM-DD> 整装#N` + 通过判据/下浮率/对比昨夜/问题清单。

## 2026-10-15 整装 runner 核对单（st-asmcheck-20261015，只读考古未跑回测）

- [x] runner 正门已找到：`scripts/backtest/ibt/ibt_runner.py`（MOD-BT-IBT-RUNNER，整装回测首跑正式版，源自 st-integrated-bt-20260922），`--help` 实测可用
- [x] 四窗口径在件：W_IS/W_OOS/W_HOLDOUT/W_POSTD 冻结于 IBT-PROTOCOL-V1（脚本 WINDOWS 常量）；W_HOLDOUT 须显式 `--holdout-guard`（单次烧毁确认）
- [x] 成本+护栏口径在件：冻结土规成本 T+1；`--enable-regime-throttle` 默认关（S-OWNER-002 fail-closed 硬守卫）
- [x] 下游核对：`data/strategy_intake/f06_survivors.csv` 唯一代码消费方=`scripts/backtest/f06_e4_wfa_exam.py`（MOD-BT-211 配方正考件）；其配方 38b453ca3683 E4 判**不通过**（OOS/IS=0.499<0.70），Owner 裁定②(2026-10-12)标签"禁用于实盘与候选"——f06 线当前不可入装配
- [ ] 缺口1：runner 成员池=协议 v1 冻结 15 员（脚本 MEMBERS 常量硬编码），未接装配状态册 `config/strategy_production_map.yaml`；夜跑须走 `--pool-file <yaml>`（协议 v1.1 members 覆盖，yaml 格式：`members: {sid: 文件名}` + `note:`），该桥接 yaml 尚不存在
- [ ] 缺口2：verified 晋级件自动入池机制未见（铁律"经⑨晋级自动入次夜清单"暂无代码承载，靠手工 pool-file）
- [ ] 缺口3：runner TTL=task_bound 一次性战役工具件（blueprint 自述"非永久系统"），p11 每夜 21:30 常态化触发需⑤席转正或包一层编排
- 判定：三选一之 (b)——成品战役 runner 可复用（ibt_runner），非免施工；夜用前须补 pool 桥接 yaml+晋级入池+编排壳
- 建议命令行（夜跑模板，窗口按当日选）：`python scripts/backtest/ibt/ibt_runner.py --window W_OOS --pool-file <p11装配池.yaml>`（勿动 W_HOLDOUT，烧毁窗一次性）

## 2026-10-16 整装#1（装配盘点班·按在册令未硬跑 ibt_runner）

班号 st-qoder-p11-1016-01｜冷启动三件实测：Python 3.12.8＋usercustomize 在位／lock_files cleanup＝CLEAN 无死锁／reaper source=live（scanned=18 whitelist_hits=15，keep 面第 155 行已含 ibt_runner，本班长批免登记）。禁建 worktree 遵 TRAE-079 Phase 2，本班全程主区作业、零 worktree。

### 晨报结论段（直答两问）

- **能不能赚钱：不能（在册真实成本＋护栏口径）。** 现行 14 员池（FRESH-V2-20261001）三窗两负：W_IS Sharpe **-0.308**（-12.75%）、W_OOS Sharpe **+0.457**（+17.34%，同期 000300 基准 **+31.93%** ⇒ 跑输 14.59pct）、W_HOLDOUT Sharpe **-0.938**（-8.33%）。协议 C 门（HOLDOUT Sharpe>0 ∧ DD≤30%）**不过**；证据=`docs/_working/integrated_backtest/artifacts_v2/{W_IS,W_OOS,W_HOLDOUT}/run_summary.yaml` 本班逐窗读 core 字段实测。
- **下浮率：按四种口径各自给数，且"下浮率"全仓无在册定义（判据缺失，已进转单）。**
  1. IS→OOS（Sharpe 比值，f06 先例口径 0.70 线）：0.457 / -0.308 = **-1.48 ⇒ 口径失效**（IS 为负，比值无意义，符号翻转）；
  2. OOS→HOLDOUT（同口径）：-0.938 / 0.457 = **-2.05**（衰减并翻负）；
  3. 成本下浮（同窗 OOS，零成本→土规全成本）：Sharpe 0.827→0.457 = **-44.7%**，收益 33.20%→17.34% = **-47.8%**（`W_OOS/sensitivity.yaml`）；
  4. 成本下浮（IS，`IBT-FINAL-DELIVERY` 在册）：零成本 +26.5% → 全成本 -12.1%，**成本拖累 38.6pct，毛 alpha 被吃光**。
- 一句话给 Owner：毛 alpha 存在（零成本 OOS Sharpe 0.827），但成本与执行容量把它砍到不能赚钱；且本夜**没有任何可入池的 verified 件**，装配线在"卡→件"这一环是断的（见转单环节类①）。

### 装配盘点（工序 1，本夜唯一进产件＝盘点）

- 分数册实测：`docs/04_research_records/backtest/scores/2026/exam_scores_v1.yaml` rows=106 ＝ **pass 2／fail 102／blocked 2**（yaml 解析后 Counter 实测，非 grep 估）。
- 两条 pass 件＝`TDM-E-L1-S2/calibration/41_agg_lu_count_z20_fwd10`、`.../43_agg_lu_ratio_z20_fwd10`（run_id p07a-agg8-20261015-*，date 2026-10-15，ic_mean 0.1037/0.1022，oos_ic 0.0997/0.1016，mono_spearman 0.733/0.745）。
- 卡面内容级复核（存在性≠内容判据）：两卡的考试卡本体 `docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__4{1,3}_*.yaml` 实测 `status: examined`、`signal_kind: series`、`family: calibration`，target=`mkt_fwd10_panel_ew_return`，窗＝IS 2019-02-11..2026-04-02／OOS 2026-04-03..2026-10-12（**与 IBT 协议窗不同构**）；卡内 status_reason 自陈三处缺口在册。⇒ 二者是**因子校准 IC 卡**，非可执行策略件。
- pool 契约实测：`scripts/backtest/ibt/ibt_runner.py:58` MEMBERS 形如 `sid -> c4_*.py`，装载腿 :165-176 按 `scripts/backtest/translated/<fname>` 逐件 import 并调 `mod.build(start,end)`；`translated/` 现有 89 个 c4_*.py，对 `agg_lu` 全库 grep（py/yaml/csv/md）命中 **0 个实现件**。
- **交集判定＝可入池 verified 件 0 个**。已按三对照自证（跑在 .runtime/tmp，事后已删）：① 空 members 池→`_apply_pool_override` 如期 SystemExit「池清单缺 members——拒绝空池」；② 两件按卡名拼池→override 装载通过但两文件 `exists()=False`（build 腿必炸）；③ 冻结池取 FACT-4f749668→文件在（正对照）。
- 装配状态册面：`config/strategy_production_map.yaml` store_refs 17 处全为**产物位置**（E3=`scripts/backtest/translated/`、E4=`c1_backtest.strategy_screen + data/backtest_artifacts/runs/`），无成员级清单；build_status 分布 built 325／partial 12／pending 4，E8 装配节点 sleeve 落库自述 partial（:396-403）。

### 前置三件核对（工序 2）

1. **pool 桥接 yaml＝不存在**（`p11_assembler/*.yaml` 实测 NONE）。本班**未手工建**——成员源按本席指令＝分数册 verdict=pass，该源产出 0 个可装载成员，手搭空池 runner 直接拒（负对照已证），手搭旧 14 员池＝把 10-15 产物当本班成绩（dispatch 在册令原文「硬跑＝假成绩」）。桥接件的**格式契约已由三对照钉死**：`{schema_version:'1.1', members:{sid: c4_fname}, note: <str>}`，消费位=`ibt_runner.py:500-515`。
2. **verified 自动入池＝无承载件**。`scripts/backtest/factory_intake_pipeline.py` 实测只做到 E1 进货→E2 预审（:207 取 hypothesis_precheck VERDICT_PASS、:360 读 precheck_passed），**不写 pool yaml、不消费 exam_scores**。全仓 grep `pool_override` 消费位只有 ibt_runner 本体。
3. **21:30 编排壳＝未注册**。`config/trading_day_cycle_map.yaml` grep `21:30|整装|p11|ibt` 命中 **0**；src/zephyr/trading 侧唯一"整装"命中是 `decision_map.py:264-296` 的 PortfolioPlan 数据类（与研究整装无关）。⇒ 依本席指令工序 2 分支：本班只做判读准备＋记 finding，不强行进产。

### 通过判据读数（对既有产物核对，非本班新跑）

- 证据代次声明：`artifacts_v2/` 三窗产物＝14 员 FRESH-V2 池（meta.members 逐窗 14、variants_run=['IBT-A']、throttle_enabled=False、dampen=None）；而 `IBT-RUN-REPORT/IBT-FINAL-DELIVERY` 的在册四门判定属 **v1 15 员池**（其 §2 逐轮数字 0.336/0.408/13935 与 v2 的 0.457/0.1734/13134 不同代）。**v2 池迄今无人出过准入判定**，本席按协议 §8 逐门核对：
  - A 链路完备＝**过**（组合层 variants＋个股层 members 14 条＋benchmark 齐，产物实测）；
  - B 红蓝正确性＝**未闭合**（`W_OOS/redblue_round1.yaml` 实测 `new_red: 1`：shift_injection_material ok=false「注入后 Sharpe 0.457→0.469 (Δ=+0.012)」＝位移注入未被 fill 审计抓出；v2 面只有 round1，无 round2+；在册"连续两轮 0（round3+round4）"属 v1 池不可移用）；
  - C 绩效底线＝**不过**（v2 HOLDOUT Sharpe -0.938<0；DD 14.10%≤30% 单项过）；
  - D 池污染披露＝随附（meta 含 data/regime 披露块）。
  - ⇒ 准入判定＝**差什么**（三条：C 门绩效＋B 门位移注入未闭合＋v2 池无准入判定在册面）。
- 护栏面：overfitting_flag=True 三窗全带（引擎自报）；W_HOLDOUT 本班零触碰（未跑未改，只读已入库产物）。E7 换手上限门（`config/exam_scale_cost_gate.yaml` turnover_gate.cap_annual_x=8.0，本班零改动）在 v2 产物上**不可判**——`W_OOS/run_summary.yaml` variants['IBT-A'] 实测只有 core/extras/wall_sec 三键、无 turnover 键，而现行 `ibt_runner.py:621` 会在 portfolio 非 None 时写该键 ⇒ 产物早于该代码代（或 portfolio 分支未走），两种解释本席无产物可分辨，列为待复跑判读。在册 v1 读数是 33-39x/年 ≫ 8.0x。

### 对比昨夜

**无昨夜基线**——本席 checkpoint 游标本班进场实测 `cursor: 未开始／last_run: —`，ledger 仅有 10-15 考古班一条（未跑回测），⑫席 1016-01 已就"游标自立席起恒未开始"登记 [BLOCKER]（`p12_maintenance/ledger.md:102`）。本班＝该席第一条真实收班记录，下夜起才有同尺差分面。

### 转单（问题清单三类分流全文，经⑩汇总，本席不自写共写面）

- **环节类→转⑤（施工席）**：
  ①「卡→件」无桥＝装配线结构性断点。分数册 verdict=pass 记的是 calibration IC 卡（signal_kind=series），pool 契约要 `c4_*.py` 可执行件；中间既无翻译件生成承载，也无"卡→成员"登记面。请⑤给一条正门：卡 pass 后产出/登记对应 translated 实现件（含 build(start,end) 契约），否则 ⑪席永远 0 件可整。证据：`exam_scores_v1.yaml` pass 行＋两卡 `status: examined`／`signal_kind: series`＋`translated/` 对 agg_lu 零命中＋`ibt_runner.py:165-176` 装载腿。
  ②E7 换手上限门在整装面空转：v2 产物无 turnover 键（见上）。请⑤把 ibt_runner 主跑成本档与 turnover 读数一并落 run_summary（含 slippage_bps 归属），使 cap_annual_x=8.0 可判。
- **数据类→转①（数据源席）**：本班无数据缺口诉求（W_OOS 三窗产物齐、CH 腿本班未触发）。写"无"。
- **结构类→呈批（经⑩）**：
  ①**下浮率无在册定义**——SOP 只要求"晨报直答"（`research_production_line_policy.md:157,162`），全仓 grep「下浮」在判据/参数面零命中，唯一先例是 f06 案的 OOS/IS≥0.70 比值（本席 10-15 台账:16 引用过）。请 Owner 或⑩定一线值与分子分母口径（收益 or Sharpe、IS→OOS or 含 HOLDOUT），否则本席只能四口径并报，不可比。
  ②**W_HOLDOUT 保密窗产物已在库**：`artifacts_v2/W_HOLDOUT/`（run_summary/nav/trades 三件，git 跟踪，入库提交=e74f0e1354 2026-10-03）实测 HOLDOUT 段已被跑出并落库，与"单次烧毁权只在 Owner 显式授权"相抵。本席零处置（不删不跑），请 Owner 定：作废该窗读数 or 追认；今后 HOLDOUT 复跑的门位归谁。
  ③**21:30 排班线机器面无注册**（trading_day_cycle_map 零命中）＝该席夜窗无人接。⑩第 13 条已判"非指令面缺口而是排班/开机面缺口，属 Owner 排班面"（`daily_dispatch.md:503`）。本席复证：config 与 src 两侧 grep 均无承载件。请 Owner 排班或明确改盘点频次。
  ④池身份与判定代次混用风险：在册四门判定属 v1 15 员池，v2 14 员池无判定面；若下夜⑪硬跑 v2 池，判读须自带代次声明，禁引 v1"两轮 0"。属⑩汇总纪律项。

### 自检两轮

- 轮一（口径）：所有数字来自 `artifacts_v2/*/run_summary.yaml`、`sensitivity.yaml`、`redblue_round1.yaml` 与 `exam_scores_v1.yaml` 的 yaml 解析读数（非转述），路径与键名逐条在册；比值计算 4 条已重算（-0.938/0.457=-2.053、0.457/-0.308=-1.484、0.457/0.827-1=-44.7%、0.1734/0.3320-1=-47.8%）。
- 轮二（负对照与越界）：三对照池自证含 1 枚正对照（文件在）＋1 枚负对照（空池被拒），非"零命中即判无"；本班零写判据册（cap_annual_x/8.0 与冻结窗未动）、零写他席面、零建 worktree、零触碰 W_HOLDOUT 产物；.runtime/tmp 三枚探针 yaml 当场删除。

## [BLOCKER] 登记（追加式，禁删改旧行）

- [BLOCKER] 2026-10-16|⑪1016-01|流程问题|分数册 pass 件与整装池成员不同物（calibration IC 卡 vs c4 可执行件），装配交集实测 0 个可入池成员，本席 0 件可整|docs/03_modules/_domain_backtest/exam_cards/entry_flow/L1/TDM-E-L1-S2__calibration__41_agg_lu_count_z20_fwd10.yaml status=examined＋scripts/backtest/ibt/ibt_runner.py:165-176 装载腿＋translated/ 对 agg_lu 零命中|要⑤席给"卡 pass→登记/生成 translated 实现件"一条正门承载件（严重度 高）
- [BLOCKER] 2026-10-16|⑪1016-01|工具缺陷|E7 换手上限门在整装产物面空转——v2 run_summary 无 turnover 键而现行 ibt_runner.py:621 应写该键，且主跑成本档（slippage_bps）未落产物，0.457 无法对齐 0/5bp 任一档|docs/_working/integrated_backtest/artifacts_v2/W_OOS/run_summary.yaml variants.IBT-A 键集实测{core,extras,wall_sec}＋config/exam_scale_cost_gate.yaml turnover_gate.cap_annual_x=8.0|要⑤席复跑时在 run_summary 落 turnover 与主跑成本档归属（禁改判据值）|高
- [BLOCKER] 2026-10-16|⑪1016-01|判据缺失|「下浮率」全仓无在册定义（SOP 只要求晨报直答），本席只能四口径并报，跨班不可比|grep「下浮」判据/参数面零命中，仅 docs/01_policies_and_standards/sop/automation_sop/research_production_line_policy.md:157,162 提要求；先例比值 0.70 见 docs/04_research_records/…f06 案与本席 ledger:16|要 Owner 或⑩定一线值与分子分母口径（收益/Sharpe、IS→OOS/含 HOLDOUT）|中
- [BLOCKER] 2026-10-16|⑪1016-01|需Owner|W_HOLDOUT 保密窗产物已在库并被跑出（Sharpe -0.938），与"单次烧毁权只在 Owner 显式授权"相抵；本席零处置（未删未跑）|git ls-files docs/_working/integrated_backtest/artifacts_v2/W_HOLDOUT/ 三件＋入库提交 e74f0e1354（2026-10-03）＋同窗 run_summary.yaml core.sharpe_ratio=-0.938|要 Owner 裁：作废该窗读数／追认／今后 HOLDOUT 复跑门位归属|高
- [BLOCKER] 2026-10-16|⑪1016-01|流程问题|21:30 夜窗机器编排面无注册（排班线未建），本席自立席起九班零发车；dispatch 在册令＝pool yaml 未交付前不硬跑，本班遵令只盘点|config/trading_day_cycle_map.yaml grep「21:30|整装|p11|ibt」零命中＋docs/_working/automation_campaign/dispatch/daily_dispatch.md:57,142,503|要⑩汇总呈 Owner 排班面（非指令面缺口），或明确改本席频次|中
- [BLOCKER] 2026-10-16|⑪1016-01|工具缺陷|heartbeat_daemon CLI 不校验 session id 形态，`python -m ...heartbeat_daemon --help` 把「--help」当 sid 往 .runtime/sessions/--help/heartbeat.jsonl 追加 started/exited 两行（本席本班触发的 --help 探测复现，末行 status=exited reason="session not in registry"）|.runtime/sessions/--help/heartbeat.jsonl 末两行 ts=2026-10-16T13:39:27Z/13:39:28Z＋src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py:810-819 argv 直取 sid|要⑫席给 _run_cli 加 sid 形态校验并清该 stray 目录；本席未删该目录（非本席所建，10-14 15:12 已存在）|低
- [BLOCKER] 2026-10-16|⑪1016-01|数据问题|无（本班未触发 CH 腿，三窗产物齐；无缺数诉求）|—|—|—
- [BLOCKER] 2026-10-16|⑪1016-01|工具缺陷|禁建 worktree 令（TRAE-079 Phase 2，Owner 2026-10-16）与提交正门互斥：本席零调用任何建道入口，但 `git_commit.py --enqueue` 在入队路径上无条件调 `session_worktree_start(session_id, allow_workspace_drift=True)`，实测 21:52:01 为本 sid 自动开出整份检出车道（.aidrafts/st-qoder-p11-1016-01，files=22555/dirs=3222 按 is_file 谓词分层实测），并起第二个心跳 daemon（pid 38408，与本席手工 39696 并存；.runtime/locks/heartbeat_*.pid 只记 38408＝手工那路无 pid 面可查，收班须按 PID 双杀）|scripts/git_commit.py:1028-1036（兜底意图=会话存活保障，副作用=建道）＋.git/worktrees/st-qoder-p11-1016-01 mtime 21:52:02＋heartbeat.jsonl 末两行 pid 38408/39696 同 sid alive|要⑤席把存活保障与建道解耦（只 re-register＋拉 daemon，禁 add worktree），禁弱闸/禁白名单/禁新豁免（在册先例＝改喂给闸的输入指向）；本席未删该车道（袋 pending 中，删道恐连坐落地）|高

### 补强与更正（本班后半段另 found 在册下浮尺，旧案卷保留不改）

- **更正**：上方转单结构类①与 [BLOCKER] 判据缺失条说"下浮率全仓无在册定义"——该断言只对**⑪席/整装协议面**成立（`IBT-PROTOCOL-V1.md` §8 四门无衰减项，grep 命中仅 SOP 散文），对**E4 在库监控面不成立**：在册尺=`c1_backtest.strategy_screen.oos_years_decay`，判据=`strategy_decay_certifier.py:38-40`（DSR≥0.5 ∧ decay<0.5→certified；decay≥0.5→failed）与 `strategy_lifecycle_advisor.py:36`／`strategy_screen_query.py:150` DECAY_SUSPECT=0.5 三处同源。旧行不删，按此更正读。
- **v2 池在册下浮尺实测（本班新增唯一硬数据，14/14 有值零 NULL）**：`oos_years_decay` 中位 **0.0000**／均值 **0.0543**／**≥0.5 存疑数 0**／最劣 **0.3033**（CAND-9ce75aa27ce5），正衰减仅 4 员（0.0779/0.0991/0.2795/0.3033），其余 10 员为 0.0；`argMax(deflated_sharpe, screened_at)` 全员 ≤0.0065 ⇒ 按 certified 判据 **0/14 可 certified**。查询走 `zephyr.data.ch_reader.query`（IN 清单先过 `[A-Za-z0-9_-]{4,40}` 白名单正则断言 len 相等，禁裸拼；正对照=14 员全回行、缺席集空）。
- **读法（直给 Owner）**：这套池的问题**不在下浮，在上浮之前就是负的**——六员 FACT 族 `is_sharpe` 实测 -0.218~-1.038（`-0.492/-0.218/-1.038/-0.623/+0.138/-0.527`），叠加成本后 OOS 唯一正读数（+0.457）也跑输基准 14.59pct。所以"能不能赚钱=不能"的成因链＝①成员绝对水平低＋②成本容量（IS 成本拖累 38.6pct 在册）＋③DSR≈0（多重检验校正后无显著性），而非 IS→OOS 衰减。
- **新触发的判据矛盾（已另起 [BLOCKER]）**：写腿 `scripts/backtest/c4_batch_screen.py:379-385` 对 decay 做 `min(1.0, max(0.0, ...))` 裁断⇒**负衰减（OOS 优于 IS）恒被压成 0.0**，而 `config/comparison_policy.yaml:43 oos_is_decay_negative: true` 注释明写"OOS 优于 IS（oos_years_decay<0）即触发"——经本腿入库的行该分支恒不成立。本席未逐腿查证其余三条 INSERT 供数腿（intake_load_screen_c2.py:46／sim_deviation_report.py:258 透传），故只判"本腿供数面恒空转"，不判"政策分支全局死"。
- 通道三态实测（防"查空"伪装"查无"）：`SELECT 1`→`'1
'` 通道活；`count_strict` 于本表抛 `ClickHouseQueryError(engine_probe: 空返回（未知引擎）)`，而 `system.tables WHERE name='strategy_screen'` 等值定位＝**c1_backtest.strategy_screen，engine=MergeTree**（非 ReplacingMergeTree）⇒ 严格读死在引擎探测腿，不是表缺；本表读数一律走等值定位＋非严格 query，在册 [[ch-query-fails-soft-trap]] 复证。

### 收班八件（本班逐件实测）

1. **release 全部 claim**＝本班 2 件（ledger.md/checkpoint.md）走 `git_commit.py --release-only` 出口，读数见班末回报。
2. **注销心跳**＝本 sid 实测**两个** daemon 并存需双杀：pid 39696（21:40:43 本席手工起，pid 面无记录）＋pid 38408（21:52:05 正门 `git_commit.py:1028-1036` 兜底起，`.runtime/locks/heartbeat_st-qoder-p11-1016-01.pid` 只记这一个）；按 PID 精确杀，禁 /IM 全杀（在册 [[never-kill-processes-by-image-name]]）。
3. **实际耗时**＝21:30:33 进场（reaper 首行时戳）→21:58:47 写本段，**≈28 分**（含等袋 6 分，袋仍 pending 未阻收班，快照入袋即安全）。
4. **[BLOCKER] 行**＝本班累计 10 行（含数据问题类写"无"一行），`grep -c "\[BLOCKER\]"` 命中面见班末复量。
5. **自清收口**＝`.runtime/tmp/` 本班临时件全部删除（池探针目录 p11_1016_01 两件＋message 文件），主区无本班散落件；四件套已入队 q-20261016-st-qoder-p11-1016-01-0001。
6. **GPU 还牌**＝本班**未 acquire 看门人**（零算力腿），status 免核。
7. **后台子任务清点**＝本班 **零子代理** spawn；唯一后台进程=本席心跳（归第 2 件），零孤儿。
8. **零 worktree 确认**＝**未达**：本席零调用建道入口，但正门 `--enqueue` 于 21:52:01 自动为 sid 开出 `.aidrafts/st-qoder-p11-1016-01`（files=22555/dirs=3222，is_file 谓词分层实测；.git/worktrees 元数据 mtime 21:52:02）⇒ 第 8 件本班如实记"被正门代建"，处置见上方 [BLOCKER] 工具缺陷条，本席不删（袋 pending 中，删道连坐落地风险）。历史遗留面另报⑩：`git worktree list` 现 51 条（43 条在 `.aidrafts/`），本席禁自行清理，交清理专班。
- [BLOCKER] 2026-10-16|⑪1016-01|判据缺失|更正当班自纠——本席前一条"下浮率全仓无在册定义"只对⑪席/整装协议面成立，E4 侧其实有在册尺 oos_years_decay（三处同源：strategy_decay_certifier.py:38-40／strategy_lifecycle_advisor.py:36／strategy_screen_query.py:150 判存疑线 0.5），而 IBT 协议 §8 四门与 SOP:157,162 均未把该尺接进本席晨报口径|config/comparison_policy.yaml:43＋scripts/backtest/c4_batch_screen.py:379-385 写腿＋实测 v2 池 14 员 decay 中位 0.0/均值 0.0543/≥0.5 零员/最劣 0.3033，DSR 全员≤0.0065⇒0/14 certified|要⑩或 Owner 定一句：⑪席晨报下浮率是否直接引"池内成员 oos_years_decay 中位＋≥0.5 计数"为该席在册口径（旧行保留不删，按此更正读）|中
- [BLOCKER] 2026-10-16|⑪1016-01|工具缺陷|下浮尺写腿把负衰减裁成 0.0，政策面等不到的分支恒不成立——`min(1.0, max(0.0, ...))` 使 OOS 优于 IS 的负值不可见，而在册政策明写 decay<0 即触发；本席实测 10/14 成员落 0.0 与真零衰减面不可分（非 NULL，NULL 仅出现在 is_sharpe 映射缺失时）|scripts/backtest/c4_batch_screen.py:384-385 裁断式＋config/comparison_policy.yaml:43 期望值域＋本席 argMax 读数（14/14 有值零 NULL）|要⑤席定性并给处方（去裁断或加负值列/符号位，属改判据数值面须走裁定，本席禁改）；本席只判"经本腿入库面恒空转"，未查另两条透传腿不判全局死|中
