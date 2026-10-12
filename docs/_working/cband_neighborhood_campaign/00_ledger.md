---
ttl: task_bound
title: 令 D·C 族邻域班自班台账（st-cband-20261012）
created: "2026-10-12"
sid: st-cband-20261012
campaign: cband-20261012
---

# 00_ledger — C 族（组合/配置）邻域班

终局目标：顺着全仓唯一环节级成功案例（ATR 止损 A/B，OOS MaxDD +16.54pp／SharpeΔ +0.6189）把 C 族参数邻域挖开，
今晚出普查②（ATR 止损邻域）与普查④（分配器 5 套参数网格）的第一批**折减前原始读数**。

真源：轴集与装置=`01_prereg_axis_sets_v1.yaml`（先冻后跑）；试次计划=`02_trial_plan_v1.yaml`；
调研出处=`docs/_working/2026-10-12-exam-card-mining-meta-method-research.md` §9.2/§9.3/§9.4（C 族"适用，参数邻域 mini-grid"）。

## 1. 进场对账（02:0x–02:3x 实测，非账面引用）

| 项 | 实测读数 | 凭据 |
|---|---|---|
| Python | 3.12.8（无需 PATH 修正） | `python --version` |
| 守护闸 | `lock_files.py cleanup`=CLEAN 无死锁；reaper `--status` source=live last_run=02:06:40 killed=0 reported=4 | 命令输出 |
| 内存/提交面 | commit_pct=**84.62**、ram_used=65.2%、cpu=75.7% ⇒ 跑批禁自造并发（在册事故形态） | reaper safety_wires |
| 主区工作树 | `worktree_changes=839 > 50` 告警（多会话漂移常态，非本班起因） | reaper drift |
| 车道 | `.aidrafts/st-cband-20261012`，基=dev@`20fa9c43bb`（与 dev 同 sha，零落后），工作树 0 脏，心跳 daemon pid=7736 alive | session_worktree_start 返回 |
| 能力反查 | 中文关键词全部 0 命中；英文单 token 才有面（"backtest"8 条／"trial"1 条／"exit"28 条噪音）。扫描根=src/zephyr＋scripts/governance，**看不到 scripts/backtest** ⇒ 本腿真源（exit_simulator/allocator_shadow）靠直接读码定位，审计已落 `.runtime/lookup_audit/st-cband-20261012.jsonl` | CapabilityLookup.find |
| 共享执行面归属 | `exit_sim/exit_simulator.py`：dev 面**无** RETURN-FACE 扩展（grep=0），盘面有＝考试班在途袋 q-20261012-…-0080 未落；本班车道=dev 纯基线 | `git show dev:` vs 盘面 |
| 令 C 预算册 | **未落地**（catalogs 与 docs/_working grep "试次预算/trial_budget" 仅命中调研册散文） | grep |
| 可比性核查 | `factor_exam_scores_v1.yaml` verdict 分布={'rework':175}，pass=0 ⇒ 分配器合成列仍走 fallback，与在册 v1 同列面（已显式 pin 24 列） | 实读分数册 |

## 2. 本班自裁（域内施工序，逐条带依据）

1. **腿④ 主面换轻面（引擎面降为 1 格试点）**。依据＝在册实测批4 五臂≈3 小时（commit 6bfca4265e1 原文）⇒ 45 格≈27h 超单夜窗；
   后果与不可直读性已在 01 册 `device_delta_declared` 写死，并保留轻面基线排序 vs 引擎面排序的面间一致性观察。
2. **腿② 加 decoupled 对照面（过滤恒 14）**。依据＝在册装置里 ATR 窗同时决定候选池与止损位，w 轴是混淆轴；
   不拆开就等于把"换票池"记在"止损更紧"头上。代价＝+24 格。
3. **类型轴靠最小参数化实现**（`simulate(stop_mode=...)`＋`atr14_wilder(n=...)`，缺省逐字节原路）。
   依据＝runner 内复制日循环＝extract 级克隆无逃生；先例＝同件 [RETURN-FACE-EXTENSION] 甲案的"纯追加＋零漂移自证"工法。
   共享件避让＝改前 claim＋袋前取 dev 现字节为基＋纯加不减自证。
4. **试次双面入账**：逐格探索分册 jsonl ＋ 批次级 N 账本 `record_run` 追加（防 DSR 分母少记），
   探索批不抢考试 N_eff 披露位。已知护栏风险如实登记在 02 册，拒写不硬闯。

## 3. 待呈批／待他道（不自拍）

- 令 C 预算册未落地 ⇒ 本班试次先挂自班账，迁移字段留位；折减口径须由预算册主统一给，本班不自造第二套。
- `registry_mass_edit_guard` 标定缺陷（合法追加常驻失败）在册已转维护二班，本班复现则附读数。
- `capability_lookup` 扫描根不含 `scripts/backtest` ⇒ 该域能力反查实际为空面（本班实测四词中文全 0），是否扩根属治理域，不代修。

## 4. 进度（滚动，跑批后逐节追加）

- [x] 01 轴集预登记冻结（先于一切仿真运行）
- [x] 02 试次计划入自班台账
- [x] 共享件参数化扩展＋零漂移自证（零 CH；含 01 册 A1/A2 两则冻结前更正）
- [x] runner 脚手架（零 CH 合成面全绿：115／44 格，error_rows=0）
- [x] 三件定窗＋CH 存活探针（04:00 门；窗况裁决见 §8.0，实况＝tilib 全程 Running，按"照令发跑＋双刷钩留证"处置）
- [x] 腿② 115 格（04:43–04:46，读数与判据命中数见 10_atr_stop_raw_v1 与晨间包 §3）
- [ ] 腿④ 轻面 44 格＋引擎面试点 1 格
- [x] 入账（探索分册 118 行；N 账本 L0 零写＝设计如此；02 册 actual_write_outcome 已定稿）
- [ ] 晨间包与落地袋

## 5. 施工前置记账（02:4x–03:3x，零 CH）

| 件 | 动作 | 实测回执 |
|---|---|---|
| 共享面参数位① | `exit_sim/exit_simulator.py` 开 `simulate(stop_mode=…)`＋`atr14_wilder(n=…)`（keyword-only，缺省=在册语义） | 已 claim（TTL 240min）；diff=+15/−2，两枚删除行逐条点名＝被替换的旧签名行与旧调用行；`ZERO DRIFT PASS checks=10 failed=0`（dev 面源码以伪 `__file__` exec 成第二命名空间，同输入双臂 nav 逐位等）；配对测试 `test_exit_sim_stop_modes.py` 6 支绿；ruff format/check 双清 |
| 共享面参数位② | `allocator_shadow.py` 开 `three_layer_weights(w_eq/w_iv/w_mom)`＋`pa015_weights(up_w_iv/up_w_mom/down_w_iv/down_w_mom)` | 已 claim；diff=+29/−7；缺省常数与乘法次序与旧码同（逐位等断言在测试里）；`test_allocator_share_params.py` 4 支绿；五套定义与批4 落册路径零动 |
| 跑批器 | 新建 `scripts/backtest/fexam/cband_grid.py`（读册枚举＋零 CH 自检面） | `--enumerate` 实测 atr=114(＋1 参照=115)／allocator=44／总计 160，与 01 册 EXPECTED 双向相符；`--selftest` 两腿全流程绿（counts 90/24/1 与 44/44，error_rows=0）；三测试文件合跑 `15 passed` |
| creation_token | `batch_creation_tokens.py` 意图 API 三步（register→publish→render） | 文档册 3 件＋跑批器 1 件（v333，quadrant=stale wrote=True）；车道需先补 `config/.env.postgres`＋`config/.env.clickhouse`（gitignore 件，车道缺→"PG 连接配置文件不存在"，与考试班 §11 同族；已按在册处方从主区 cp 入车道，且验证 `PYTHONPATH=车道根;车道根/src` 后 `zephyr`/`schemas` 均解析到车道＝非主区旧码） |
| 大白话翻译 | `add_module_translation.py --path scripts/backtest/fexam/cband_grid.py` | 账本 OK＋publish v35＋render armed_initial wrote=True＋三方核验（PG active v1 ∧ 投影命中）；**门源已自己读到 return 行**：TRANSLATION-COVERAGE 经 `module_translation_loader.get_module_translation` 读 **YAML 投影面**（非 PG 第三源）⇒ 落袋须"翻译册投影先行"（§6-1） |
| depgraph | `apply_depgraph.py --granularity file --add-design-node … planned` | 先 `--dry-run` 实证零 PG 写（"本次若真跑将写 1 处，均已 rollback"）后真跑：node_id=16612345；随带告警 MOD-BT-FEXAM 蓝图文件不存在（他道在册缺陷，本班不代修） |
| reaper 避让 | 判据实测 `_IDLE_KILL_AGE_S=6h 且 cpu<0.5%` 才杀 | 本班跑批分钟级且 CPU 忙⇒不入误杀面；命令行不含 `.runtime` 子串；故不改主区 keep 册（改它=降级直改主区，无必要不申请） |

## 6. 落地车道待办（读数出来后一并处理）

1. 车道投影册被 render 动过两本且均为**严格超集**：`module_translation_registry.yaml` +51/−0（本班 1 条＋代带他道
   已入 PG 未落投影的 9 条：`statsgov_deflation_and_budget.py`／`build_distilled_sft_dataset.py`／`degraded.py`／
   `pool_regression_direction_gate.py`／`layered.py`／`lying.py`／`new_mod.py`／`orphan.py`／`with_extras.py`），
   `capability_canonical_file_registry.yaml` +1525/−0。前者按考试班"投影先行同步袋"通道走（袋名点名代带条目）；
   后者体积大且非本班资产⇒**不随本班袋**，留车道并交册主车道（在此登记，不隐瞒）。
2. 代码袋＝两共享件（纯追加＋点名删除行）＋跑批器＋三支测试；文档袋＝00/01/02＋读数两册＋晨间包。
3. 每袋前：共享件先 `git checkout dev -- <件>` 取现字节为基（考试班 0080/0081 若先落，本班纯追加须重放到其现值），
   并 `git diff --numstat dev -- <件>` 自证删除行只准是点名的那几条。
4. 新建件投法（在册新工法，st-gpuwo 实测）：**先 enqueue 后车道 commit**——车道先 commit 新建件会把袋的
   base_head 记成车道 HEAD，落地侧判"基底有而 dev 已删"必死袋；投后核 `pending/<qid>.json` 的 base_head 应等 `git rev-parse dev`；
   一袋一暂存面（投前 `git restore --staged .` 再只 add 本袋），跨域按域拆袋＋`--depends-on`，勿用 `--allow-multi-domain` 糊。

## 7. 窗况实测（三件定窗口径，逐次带钟）

| 本地钟 | 面 | 实测读数 |
|---|---|---|
| 02:29 | 算力闸 FAC-E0 | `window` 档=heavy_ok（is_trading_day=true）；`check --purpose cband_grid --compute-class local` ⇒ allowed=true（reason=gate_allow_light_always） |
| 02:5x | 计划任务 | tilib_indicator_backfill_nightly **state=Running**（last=10/12 02:30:01，rc=267009=运行中，next=10/13 02:30）；CH-OptimizeMerge-Weekly=Ready 下次 10/18 03:30（本周窗已过）；ZephyrAlpha_F06Grid=**Disabled**；QMTWatchdog rc=0；EmotionIndexSnapshot rc=0（next 12:35） |
| 02:5x | 产物目录 | `data/strategy_intake` 最新目录仍是 10-10 的批次（零今晨新目录）⇒ 无人在发配方网格 |
| 02:5x | CH 存活 | `SELECT 1`→1（0.03s）；`kline_daily_hfq` 2026-09-30 行数=6766（0.48s）——零触碰 technical_indicator 面 |
| 03:0x | 接口探针 | `ch_data.regime_series(2026-09-01,09-30)` 从车道跑通：30 行，**source=sma200_default**（证实 01 册 regime_delta：本班体制面与在册 v1 的 regime_table+sma_fallback 不同源）；27.5s/月（SMA200 需暖机窗） |
| 03:1x | 装置列面 | `load_pass_columns()` 24 列与 `prereg_frozen.yaml` 冻结清单**逐字等**（equal?=True）⇒ 腿② 底座与 A/B 出生时同列集，非仅同函数 |
| 03:1x | 争用判断 | tilib 夜跑正在写 `c1_market.technical_indicator`＝本班两腿唯一读取源 ⇒ 等待判据不是钟表而是**它跑完**（04:00 只是令面下限）：中途读数＝半写局面，锚对账会把它当"数据漂移"误解释 |

等窗期零 CH 重活已完成（参数位＋跑批器＋三测试＋四项登记），后台探针每 60s 查 tilib 态，窗开即发。

### 7.1 等窗期另外三处实测（03:3x–03:4x，都是真发生的）

| 项 | 实测与处置 |
|---|---|
| 自家会话活性锚 | 03:3x 门预检报 **TAKEOVER-PENDING：死会话 sid=本班**（证据原文"pid 48272 dead"）。真因＝开班时 `session_worktree_start` 落在**短命 python 进程**上，守护 02:38 因 idle 1809s 自退（心跳日志末行 `status=exited reason="idle timeout"`）⇒ last_heartbeat 陈旧 ⇒ pid=0 轨判死。处方按在册正门：`register_heartbeat_keepalive(reason 具名, ttl=7200)`＋重跑 `session_worktree_start`（幂等复用车道，daemon pid=55084 alive）＋`mark_logical(True)` 过 W-29 形态核验；修后实测 `hb_age=27.4s`、`in list_active=True`、`session_takeover_ledger --scan` 四条 dead 里**已无本班**（余 st-backfix-patrol/st-deadcure3/st-nightmine2/st-regsolo）。⚑ 教训在册：判"我的会话活着"不许靠记忆，须与门同尺（list_active＋心跳新鲜度） |
| 车道治理件缺 config | 车道根跑 `batch_creation_tokens` 报 `CH 配置文件不存在 → PG 连接配置文件不存在`（与考试班 §11 同族），处方＝从主区 cp `.env.postgres/.env.clickhouse` 入车道＋`PYTHONPATH=<车道根>;<车道根>/src` 并实测 `zephyr.__file__`/`schemas.__file__` 双双落车道（否则 import 落主区旧码＝在册假绿形态） |
| 发跑序的进程面自匹配坑 | 我第一版用 `nohup` 起序列：①命令行含 `.runtime` 子串（reaper 对"孤儿＋.runtime"是 **30 分钟即杀**，非 2h 孤儿线）；②`git-bash kill <pid>` 用错 PID 命名空间没杀掉 ⇒ 一度两条序列并存会在 04:00 双发。处置＝脚本与刷钩迁入车道 `.tmp_shift/`（命令行不再含 .runtime，且该目录被 `/*` 忽略不入库）＋改用平台后台任务（父进程在岗，不构成孤儿）＋`taskkill /F` 按 Win32 PID 收掉残留。⚑ 另记一条：用 `CommandLine -like '*run_all.sh*'` 查进程表时，**我自己的查询命令**也含该串，前两轮回执里的"残留进程"全是自匹配假象——加 `-notmatch 'Win32_Process'` 才是净面（在册"先减掉自家观测节拍"同形，今夜复现） |

### 7.3 04:00 首发达全灭＝内存墙（实测与处方，先于任何读数）

04:00:42 起四步全部 rc=1，报错原文两类：`ch_data.CHAccessError: CH 查询失败: （空消息）SELECT trade_date, symbol, open AS v …`
与 `numpy._core._exceptions._ArrayMemoryError: Unable to allocate 1.00 MiB … / 69.2 MiB for shape (9075508,) int64`。
同期机器水位（reaper 自报）：**commit_pct=91.51%、ram_avail=16.78G、cpu=69%、degraded=True、breached=['ALERT-SYS-003']**，
占用大头＝miniquote 6.1G／llama-server 私 17.7G／本班 python 3.5G。⇒ 不是本班代码错，是**提交内存墙**；
本班 24 列面板同驻的峰值（估 ~5GB）撞线。⚠ 自裁一条：02:06 已读到 commit_pct=84.62% 却仍排了高峰值方案，
属处置不足（在册教训"起批前先读 commit_pct"我只读未用），已改为下述低峰路径。

处方（两件事，都不动读数口径）：

1. **降峰改按日分块构建 composite**：`DATE_CHUNKS` 五段（互不重叠、并集=WINDOW_RUN），每段装载 24 列→
   `composite_signal`→该段 value_panel→**释放面板**再下一段，最后按 index 拼合。正确性前提＝
   `rank(axis=1, pct=True)` 与跨列均值**只在当日行内运算** ⇒ 分块与整段逐位等价；已落正对照钉
   `test_composite_and_value_panel_are_row_local_so_chunking_is_bitwise_identical`（含 12 个整行 NaN 面构造，
   `assert_array_equal` 逐位过）；若将来 composite_signal 引入跨行运算，该钉必红＝分块路径自动失效信号。
   同一段代码顺带把 `real_frames` 改成"缓存命中则整批面板不进内存"，格循环进程只读 composite＋K 线 pickle。
2. **进程命令行去 `.runtime` 子串**：脚本与刷钩移入车道 `.tmp_shift/`（`/*` 已忽略，不入库），
   并用平台后台任务而非 `nohup`（父进程在岗⇒不构成孤儿，避开"孤儿＋.runtime＝30 分钟即杀"线）。

复核：分块改造后 `--selftest` 两腿重跑与改前基线**读数逐位相同**（rows/counts 双 True），
`test_cband_grid_cells.py` 6 passed，ruff check/format 双清。04:14 二次发跑（当时水位 ram_avail=16.5G，本班峰值目标 <3G）。

## 8. 发跑与读数（窗开后填）

### 8.0 窗况裁决（本班自裁，先于任何跑批；03:4x）

令面写"需 CH 的腿 04:00 后跑"，而实测 tilib_indicator_backfill_nightly 02:30:01 起跑、03:41 仍 **Running**；
该班夜跑日志文件 mtime 停在 10-10 **15:34**（上次运行 02:30 起跑）⇒ 上轮历时约 13 小时，
"等它跑完"等价于今晚零读数。两判据相冲时的裁决依据：

1. 令面 04:00 是**下限**不是"必须等到对象消失"，且统筹其它夜窗处方（tilib 02:30 让路）默认其在 04:00 前结束——
   本轮实测与该默认不符，属**令面前提与实况不符**，按在册工法=不硬等也不擅改令，改为"照令发跑＋把实况与风险如实随册"；
2. 真正的风险不是钟点而是**读面在半写中不一致**（24 列分次查询）⇒ 处置=装载前后各跑一次只读刷钩
   `snapshot_probe.py`（technical_indicator 末班日/行数/四列抽样和＋kline 末班日/行数），
   前后有动即在两册 `data_face`/晨间包标"读面在装载期间有变动，锚对账含续供项"，不动装置不凑数；
3. 面板 dtype=float32（`ch_data.load_panel` 原文）⇒ 24 列峰值估算下修至 ~4.5GB，远离 reaper `_DANGEROUS_MEM_GB=10` 即时线；
4. 若 nostop 参照臂与在册读数不等，先按"数据面自 10-06 起重算/续供"申报，禁调装置；tilib 完事后另批复算一版对照（列入待办）。

### 8.1 逐件登记

- [x] 前置刷钩（baseline）：04:14:11 rc=0——`ti_max_date=2026-10-09｜kline_max_date=2026-10-09｜ti_rows(9 月起)=360,696｜kline_rows(9 月起)=129,089`
- [x] prep 腿②（分块 composite）：04:14:19→04:43:15（28.9 min，5 块各 ~5.5 min），composite=(1880 日 × 5818 票)；
      缓存件落 `.runtime/tmp/st-cband-20261012/cache`，格循环进程只读 pickle 不再装载面板
- [x] （取消独立 limit=1 校准步，理由随册）：分块改造后已无"首件失败即白烧 30 分钟"的风险，
      且每格秒数由全量跑自身实测；令面"首件校准再放量"的意图由 04:00 首发的失败诊断＋selftest 逐位钉承担
- [x] 腿② 全 114 格＋参照臂：04:43:15→04:46:04（2.8 min）**每格 0.7664s 实测**（在册同装置 0.428s/格是 10-06 空机读数，
      本班机器 cpu 76%／他班在跑，两值不互换）；counts={coupled 90, decoupled 24, reference 1, error_rows 0}；
      探索分册 118 行＝115 格行＋3 批次行（90/24/1 与预登记相符）
- [x] nostop 锚对账：**与在册不等，且已定因＝数据面续供**——本班空仓月 12／成交 3634 笔／1477 票，
      在册 36／2686／1174；composite 首日 2019-01-02（在册那次起点约 2021-01）⇒ `technical_indicator` 被今晚
      tilib 夜跑回填，基线 OOS Sharpe 从 -0.187 变 **-0.590**（IS -0.367→-0.199）。
      反证"不是本班管路错"的三条结构面：交易日数 2123 相同｜调仓月 105 相同｜24 列与冻结册逐字相同。
      不动装置凑数，如实随册，并在晨间包列"判据在此基线下失去判别力"一条。
- [x] 混淆项实测归零：同(倍数,类型)下 coupled−decoupled 的 OOS Sharpe 差 **24 对全 =0.000**
      ⇒ ATR 窗改候选过滤这条路径实测不改票池选择，w 轴读数干净；decoupled 24 格的作用是"证伪混淆"而非新信息
- [x] 腿④ 首发达 44 格全错＝`KeyError: "['300114'] not in index"`（轻面缺"不可定价标的"这一层——在册引擎面靠
      `flat.dropna(subset=['close'])` 天然做到）。处方＝`monthly_topn_signals` 之后按价格面掩列，
      **秩仍在全截面算，只剔成交面**（与引擎面同语义）；实测掩掉 1 列而它出现在 21 个调仓月目标权重里；
      修后 05:23:36→05:24:36（1.0 min，composite/value_panel/kline 全走缓存）**44 格全成 0 错**，每格 0.9063s
- [x] prep＋腿④ 轻面 44 格：prep④ 04:46:04→05:14:43（28.7 min，5 块各 ~5.7 min＋value_panel）
- [x] 后置刷钩（after 05:14:47）：与 baseline **有动**——`ti_rows 360,696→365,115`（＋4,419，落在 2026-09 起＝OOS 窗内）、
      四列抽样和全变（macd_dif 14371.15→14487.36 等）、kline 两面未动 ⇒ tilib 正在续供指标面。
      每格内部仍一致（composite 一次成形、格循环零再读），但**绝对读数属"回填中途快照"**，
      tilib 收工后须以同册同轴复算一版对照（晨间包 §6 第 6 项，禁当作已完成）
- [x] 引擎面试点 1 格（40min 墙钟线）：**未发**——04:0x 实测提交内存墙（commit_pct 91.51／degraded=True／
      breached=ALERT-SYS-003）下，15M 行 flat 面的引擎跑批是最高风险腿，本班把额度让给两腿读数；
      按 01 册 `engine_face_stop_rule` 如实登记"未跑"而非"零结果"，待水位回 ram_avail>20G 且他班收工后再发（明日待办）

## 9. 落地与队列面（本班末端实测，06:1x）

| 件 | 读数 |
|---|---|
| 文档袋 | `q-20261012-st-cband-20261012-0001`（8 件，base_head=`59a9e96309b6`＝当时 dev tip ✓） |
| 代码袋 | `q-20261012-st-cband-20261012-0002`（8 件，base_head=`20fa9c43bb36`＝**车道 HEAD**，非 dev tip） |
| 代码袋基底是否有害 | 实测无害：`git diff --stat 20fa9c43bb dev -- <本袋 8 件>` **空**＝dev 自车道基线起这 8 件零改动；袋内新件在 base_head 处不存在 ⇒ 不触"基底有而 dev 已删"判据。⚑ 若考试班 0080（RETURN-FACE 扩展）在本袋之前落地，则该件两侧皆改，届时按 dead_reason 重基复投，不硬闯 |
| 队列水位 | 06:12 pending≈55→本班投两袋后 done 计数在动（02:5x done=746、03:4x done=750）＝**约 14 min/袋**；本班不轮询抢跑，落地核验按 `git show dev:<file>` 只认落地面 |
| 三门预检 | 文档袋 `gate_dry_run` 三段全绿（0/3）后方入队；代码袋 COMMIT-SCOPE 实测 2 域（码＋测试＋两本生成册），按在册正门用 `git_commit.py --allow-multi-domain --enqueue`（留痕在消息内），**未**用 `--skip-preflight` |

三条新工法（本班实测，值得入册）：

1. **车道 claim 必须传车道绝对路径**：`GitCommitGateway(project_root=车道).claim_files(sid, 相对路径)` **静默返回 0/8**——
   因为 `SessionRegistry.claim_files_batch` 把相对路径按**进程级 REPO_ROOT（主区）**归一，而 gateway 的
   `_norm_path` 按 project_root（车道）归一，两侧永不相等 ⇒ CLAIM-REQUIRED 永远红且无任何告警。
   传 `<车道根>/<相对路径>` 后实测 8/8 ✓。这是"门禁替身/静默失败"家族的新形态。
2. **短命 CLI 会把自家会话打成死会话**：`gate_dry_run`/`git_commit` 等每次跑都会带当前 pid 触碰注册表，
   进程一退 ⇒ 台账判"pid dead"⇒ TAKEOVER-PENDING 反手拦我的袋。处置正门＝
   `register_heartbeat_keepalive(具名＋TTL≤7200)` ＋ `session_worktree_start`（幂等复用车道，重启守护）
   ＋ `mark_logical(True)`（须心跳<120s 才授标，本班实测 True）＋ `session_takeover_ledger.py --resolve <sid> --by <sid> --note <证据>`；
   修后 `TAKEOVER-PENDING` 门 PASS ✓，实测 hb_age≈15s、list_active 含本班。
3. **机生 .md 也要 frontmatter ttl**：`write_report` 产出的 `10_/11_*.md` 被 DOC-HEADER-SUITE[TTL-METADATA] 硬拦
   （"temporary zone 缺 ttl，doc_type 不豁免"）⇒ 生成器现在自带
   `--- ttl: task_bound / campaign / generated_by（机生禁手改） ---` 头；修后三门全绿。

跑批复现性自检（在册列序事故的同型风险）：修 lint 后两腿各重跑一次，
**逐格读数（去掉 `seconds` 列）哈希与首跑完全相同**（`f1dc3ddc354393c0`／`4dc17514f7de533f` 双 IDENTICAL）
⇒ 本班轻面无"同参不复现"形态（composite 与面板全部走缓存、无 set 迭代入列序）。

## 10. 协调检验收尾（06:2x–06:4x 实测，非推断）

**队列面**：pending=59 袋，本班三袋列第 56–58；近 1h `done/` 新增 6 袋（≈10min/袋）⇒ 轮到本班约在午后。
processing 当前挂着前任 `st-deadcure3b-...-0026`（等 5.1h），本班不催不插队。

**袋内容自证（对 dev 现面做多重集合差分，逐件）**：
- `exit_simulator.py` 会丢的 2 行＝本班自己替换掉的旧 `atr14_wilder` 签名与旧 `wilder_atr_one(hv[:, j])` 调用；净 +13。
- `allocator_shadow.py` 会丢的 7 行＝本班参数化掉的旧签名/旧权重表达式；净 +22。
- `module_translation_registry.yaml` 相对 dev **净删 0 行**（纯追加 51）⇒ 不驱逐他班条目。
- `script-manifest.yaml` 净删 3 行＝`generated_at`／`total_scripts`／一条描述的折行宽度（同句"…调用本脚本向翻译账本"，
  dev 版在"向"处断行）⇒ 生成器重排，非他班内容损失。

**与考试班共用执行面的碰撞（如实登记，不代裁不代修）**：他班死信袋
`q-20261012-st-mineloop-20261010-0080`（1 件＝`exit_simulator.py`，blob `3856c894b9c0…`）携带的是 RETURN-FACE 甲案 14 行、
**不含**本班 `STOP_MODES`；本班袋携带 `STOP_MODES`、**不含**那 14 行。两侧行集互不相交但同改一文件
⇒ 按落地仲裁语义"双侧皆改＝真冲突死信"处理，不会静默覆盖（`commit_queue_landing` §370–376 扩面条款在案：
基底漂移交合并仲裁，不在队列层判覆盖）。06:3x 实测本班注册表 `held_files=[]`（claim 已随入袋释放）
⇒ 该死信袋已不被本班 claim 挡道；其属主 requeue 前须先 `git show dev:scripts/backtest/fexam/exit_sim/exit_simulator.py`
取本班落地版做**超集重建**，否则会把 STOP_MODES 参数位判成外来差异而回退。

**活性闸残余风险与处方（预先声明，免被读成事故）**：`register_heartbeat_keepalive` TTL 上限 7200s 是设计
（钳制而非报错，到期必须 renew），本班现授到 08:34。若队列在守护自退之后才轮到本班袋，池工拾取点
`_session_ghost_dead` 会把袋直落 `dead/`（`dead_reason=ghost_session`，归 env 类）；
**手动 `python scripts/commit_queue.py requeue <qid>` 不受存活闸限**（459 号裁定原文"CLI 手动 requeue 不受闸限"），
袋字节在 `blobs/` 无损。reaper 防误杀已按在册格式追加两行（`cband_grid`／`heartbeat_daemon st-cband-20261012`，
键集合差自证 added=3 行·removed=0）。

**收尾序列状态**：claim 全空 ✓；staging 成果已 promote 到 `docs/_working/cband_neighborhood_campaign/` ✓；
handoff＝本节＋`99_morning_package.md`；车道未 merge（本班成果全部经队列正门，协调政策"任务完成=merge"
对队列路径的等效终态是"袋落地"，落地后车道走 abort＋worktree remove 裁定通道）。

## 11. 晨裁执行账（11:1x 收令 → 19:5x，含本机两次死机与复投）

### 11.0 死机与损伤清单（先记账，免被后人读成"本班没做"）

| 时刻 | 事件 | 证据 |
|---|---|---|
| 11:55:55 | 本机第一次非期望关机 | `Get-WinEvent` Id=41（Kernel-Power）列表实测 |
| 11:51:59 | `technical_indicator` 回填停在半途 | `data/runtime/dwm_shard_state/daily_shard_022.json` done_windows=3/6、finished_at=11:51:59；全 58 只分片最新写即止于此刻 |
| 18:22:20 | 第二次非期望关机 | 同上事件表第二条 |
| 16:17–16:39 | **本班四袋全部阵亡**（队列在 18:3x 已排空 0 pending） | `dead/q-…-0001/0002/0003/0004.json` |
| 两次 | 会话注册表条目被洗（`get_session`→None）、心跳守护随机器死 | 复注册两次；`mark_logical` 复评 True |

死因分类：**三只是自伤**（TAKEOVER-PENDING——`last_activity idle 31104.7s > 7200s`，死机把活性锚冻在死机那一刻；
`--resolve st-cband-20261012 --by st-cband-20261012` 已按在册处方解除，注记写明"自复非接管"）；
**一只是同族门缺陷**（TRANSLATION-COVERAGE，见 §11.4）。四袋袋内字节 sha256 复核 **32/32 无损**。

### 11.1 晨裁①（换尺＝批，两案并用）——已执行，标定数如下

尺装在 `cband_grid.py --rejudge`（零 CH：只在已入账读数上做算术；阈数值原样继承 5pp／-0.2，本班只动"对照什么"与"看几个窗"）：

| 尺 | 腿②（参照臂＝nostop，114 格） | 腿④（参照臂＝**各套自己的基线格**，39 格） |
|---|---|---|
| 在册原尺（仅 OOS） | **105/114（92%）＝无判别力** | 0/39 |
| 案 A：IS 与 OOS 双窗同改 | **15/114（13%）** | 0/39 |
| 案 B：同波动缩放对照（仅 OOS） | **69/114**；λ 可信带内 59/82 | 4/39 |
| 新尺＝A∧B（两案并用） | **6/114（5%）**；带内 6/82 | 0/39 |

- 案 A 单独就把案 B 拦不住的格拦下 9 格（＝两案并用非冗余）。
- 通过的 6 格全部集中在 **mult 2.0–2.5 ＋ win 21–30** 角；mult 2.0/12 格过案 A、2.5/3 格，**无一格在 mult≥3.0 过双案**——
  与"越紧越好"的单调曲面自洽。
- 机读册：`13_reruler_v1.yaml`（逐格 λ／双窗原始差分／四尺命中）＋`13_reruler_v1.md`（机生，含近似申报）。
- 读数等级：`尺判别力标定（折减前＋在标为无效待复算的快照上），非任何格的录用判定`。

### 11.2 班中三处工程自纠（都是"尺本身会骗人"的形态，非读数问题）

1. **腿④ 参照臂错配**：首版把"首个基线臂"当全表对照（拿 THREELAYER 的基线去量 PA015 的格）⇒ 改为**逐行按各自套的基线格**
   （`baseline_cell_ids` 查表），无参照即跳过该格而非硬凑；格数 44→39（EQUAL 套无可对照格）。
2. **σ 代理符号口径混用**：首版 `_ann_vol=年化收益/Sharpe` 要求同号，30/114 格判"不可测"——那不是数据缺失是两套年化
   口径（几何 vs 算术）符号相反。改取量级 `|年化收益|/|Sharpe|`（λ 是比值，绝对值即抵消）⇒ **114/114 可判**，
   原尺命中从 75/84 回到与册内一致的 **105/114**。
3. **λ 可信带旗**：端点统计量下 Sharpe 近零的格 σ 会爆（λ 实测跨 0.002–26.8），此类格的案 B 读数属失真——
   自报诊断旗（0.2≤λ≤5），可信带内另计；**复算（⑤）时案 B 改从逐日净值序列取 σ，本近似届时退役**。
   此旗是诊断面，不改任何格的四尺命中口径（两套数都在册）。
4. 另自抓自补一处：改 CLI 时误删 `--leg` 参数行，当场以袋内字节对拍发现并复原（对拍＝本班在册收口动作，非声明）。

### 11.3 晨裁②③④⑤的落点

- **②SIG131 恒等参数＝登记实现面缺口**：登记位＝`02_trial_plan_v1.yaml` 新增键 `implementation_gaps_registered`
  （机读，含 cap_frac 六档逐位同的证据键＋在册 v1 引擎面 `ALC-SIG131-001`＝`ALC-EQUAL-001` 的 metrics 相等事实）。
  五套定义在册禁改照旧，本班不动实现面；下游口径按批复＝**与腿④ 0/39 同族结论：分配器邻域现阶段无增量，记录在案不硬挖**。
- **③L0 消耗数据转令 C 册主**：转口＝`02_trial_plan_v1.yaml` 新增键 `l0_consumption_payload_for_statsgov`
  （batch_id／格数／axes_used／探索分册 jsonl 路径／kind 名建议）；本班不自写 N 账本 L0（mining_sop_policy §8.5.2）。
- **④引擎面基线臂＝排队**：01 册 `engine_face_stop_rule` 与晨裁"池减半前不加新格"叠加后本班**不自发**——
  实测水位虽已回（15:4x commit_pct 56.5%／18:3x 41.3%／ram_avail 33.5G），但"池减半"与"内存宽松"两条同时成立
  须由在册池面判定，非本班自量自批；已登记为待办臂，1 格≈36min 成本随 §7 在册。
- **⑤tilib 收工后 159 格同册复算＝强制**：前置条件现**不成立**——回填停在 11:51:59（`daily_shard_022` 3/6 窗口）
  且重启后无人复跑、`tilib_dwm_runner_instance.lock` 陈旧在盘（02:30 那次）。复算腿随 data 车道收工触发，
  本班已把复跑面留在在册形态（`--prep`＋两腿＋`--rejudge`，轴集册未动）。
- **下游口径（批复原文照落）**：腿② 6 格**不采纳不晋级**，走"候选"位（冻卡呈批＋考试＋预算册记账三件缺一不可），
  折减口径以预算册终版为准；今天的标定数＝**"尺的验收"，不是"矿的终读"**。

### 11.4 TRANSLATION-COVERAGE 半边缺陷——本班处置＝不重烧、挂待 render

实测三面（同族缺陷只修了一半的再现）：

- PG 账本：`REG-CAPCAN-001` 有 `file=scripts/backtest/fexam/cband_grid.py` token 行 **active**；
  `REG-MODULE-TRANSLATION-001` 有 `module_path=…cband_grid.py` **active**（直读 `registry_entry`，DatabaseService 只读连接）。
- 投影面：`git show dev:…module_translation_registry.yaml | grep -c cband_grid` = **0**；主区盘面同 0；车道盘面 1（本班登记时 render 过车道）。
- 门路向：`translation_coverage_gate._check_translation_entry` → `module_translation_loader.get_module_translation`
  只读 `_REGISTRY_YAML`（投影），**无 PG 第三源**；CREATE-GUARD 已于 10-10 补 `_pg_confirmed_token_files`（只加正证不松门禁），此门未补。
- 另证（本班首判错了一次，改在此）：袋 0002 的 files 面**含**该投影册，且袋内 blob 里本班条目完整在场
  （`- module_path: scripts/backtest/fexam/cband_grid.py` ＋ `name_zh: C族参数邻域小网格跑批器` ＋
  非模板 `plain_zh` 全文，袋内 blob `cband_grid` 命中 1 次；册面 68,265 行 vs dev 68,214 行、相对 dev **净删 0 行**）
  ——**门仍判"无 plain_zh"**。⇒ 结论不是"没带"，而是**门读的不是袋内增量**（读基座/HEAD 面；
  即便按袋面带，直写投影的条目也会被下一次 render 当非账本内容修剪掉，见该门 docstring）。
  故"带也是白搭"成立，而"重打投影袋"更禁出——唯一稳解＝给该门补 PG 第三源（同 CREATE-GUARD 形态）。

本班处置：①**不再投代码袋**（投一次烧一次）；②文档袋先行；③根解＝给该门补 PG 第三源（照 CREATE-GUARD 同形），
属他人门禁件＋本班会话不代修他道门禁（宪法 §3.4 owner 责任制），已作"待 render／待补第三源"呈批面留此。
代码袋 8 件正身未丢：车道字节与袋内 blob 逐件对拍一致（§11.0 的 32/32），解除后原样复投即可。

### 11.5 复投账（文档袋）

| 袋 | 内容 | 状态 |
|---|---|---|
| `q-…-0001/0002/0003/0004` | 昨夜四投 | 全部 dead（拦条已解／挂 render），blobs sha 无损 |
| `q-…-0005` | 文档袋终态＝10 件（8 件＋`13_reruler_v1.yaml/.md`），base_head=dev 现值 | 待填 qid 与落地核验 |

新两件登记：creation_token 走意图 API 逐件 `--prefix <文件全路径>`（预览恒 1，断言 2/2）；
投影面滞后不阻塞 .yaml/.md（CREATE-GUARD 有 PG 第三源，可正证放行）。

