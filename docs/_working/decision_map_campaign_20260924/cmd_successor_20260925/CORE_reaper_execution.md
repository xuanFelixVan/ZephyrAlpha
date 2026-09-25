---
ttl: task_bound
---

# LANE-CORE 案卷：收割器"处决核心"定性与恢复职责取证（2026-09-25 夜）

> 车道：LANE-CORE（P0 事故定性）｜总筹：st-qmine-20260925｜执行人只取证，零改运行态。
> 全部结论按【实测】/【代码】/【推断待验】三级标注；未达标证据一律不写成结论。

## 〇、一句话结论（先给总筹可拍的那一句）

**"收割器 57 次处决 AutoRuntime Core"这个前提不成立**：`owner=auto_runtime_core`
是"登记者"字段，不是"被杀者"身份——全部 36 条 core-owner 登记记的是 `ollama.EXE serve`
子进程。但顺着这条线挖到的东西比原判更硬：**孵化收割路径按 PID 认人、不按身份认人，
Windows 会复用 PID**——此刻（22:33/22:42 两次只读复演）账本 1471 行里 1290 条
"超寿未销"记录中 **27～29 条正与存活进程撞号**，且**逐条 create_time 与登记时刻全部不符**
（=确认全是撞号而非在收真凶），撞主包括 svchost、同花顺终端、向日葵远控、postgres、
以及三条白名单常驻服务。下一轮 reaper 就会杀它们。详见 §一。

## 一、Q1 机制定性：`incubation_expired` 是什么＋是不是缺陷

### 1.1 出处【代码】
- 实现：`src/zephyr/trading/process_reaper.py:894-947` `_reap_incubated_expired()`，
  模块内注释标 "M3 孵化-收割闭环（2026-09-16）"，主流程挂载点 `process_reaper.py:1028`。
- 判据（逐条读码）：账本 `.runtime/process_incubator/ledger.jsonl` 里
  `未 exited_at 且未 reaped` + `child_pid 仍在全进程表` + `now > spawned_at + expected_lifetime_s`
  → `_kill_pid_tree(pid)`（先子后父级联）→ 落 `data/runtime/reaper_kill.log`。
- 设计意图：孵化登记制的兜底——"登记替代 cmdline 猜测"，收的是**孵化出来的子进程**
  （ollama worker / reconcile worker 之类），防止父进程崩了留下一堆巨型孤儿
  （同源背景见 `process_reaper.py:201-209` 注释：2026-09-15 提交内存耗尽事故补丁，
  9 个 llama-server ≈12GB 孤儿永生）。
- **不是"日终回收核心"**：核心从未被登记进孵化账本。账本总 1471 行、超寿未销 1290 行
  （族分布 reconcile-worker 610 / worktree-drift-watchdog 590 / write-audit-daemon 72 /
  **ollama-serve 18**）；全表 36 条 `owner=auto_runtime_core` 记录（含已标 reaped 的 18 条）
  `name` **全部**是 `ollama-serve`、`cmd` **全部**是
  `C:\Users\fanzi\AppData\Local\Programs\Ollama\ollama.EXE serve`【实测：读账本逐条打印】。
  36 条记录对 58 行击杀日志的差额（22 次）＝同一记录被反复命中（销账不落地，见缺陷 4），
  不是"核心被杀 58 次"。
  登记点=`src/zephyr/trading/auto_runtime_core.py:821-826`
  （`OllamaManager.ensure_running` 里 `get_incubator().spawn([ollama,"serve"],
  name="ollama-serve", expected_lifetime_s=86400.0, owner="auto_runtime_core")`）。
  也就是说 owner 语义="谁孵的"，日志把它打成 `reason=... owner=auto_runtime_core`，
  肉眼极易读成"核心被杀"——**本次 57 次命中的归因错误源于此日志字段歧义**。
- 配套（续约/重启）【实测】：账本 36 条 core 记录的 `spawned_at` 全落在
  2026-09-16 23:09 ～ 2026-09-20 03:20，即 09-25 被"处决"时它们已超寿 **5～9 天**；
  没有任何"到期前续约"把 `spawned_at` 往后推的痕迹。

### 1.2 缺陷清单（四条，全部代码级可定位）【代码】+【实测】
1. **身份盲（最硬）**：`_reap_incubated_expired` 只核 `pid in live_pids`
   （`live_pids = 全系统进程表`，`process_reaper.py:909,916`），既不比 `create_time`
   与 `spawned_at` 是否一致，也不比存活进程 cmdline 与登记 `cmd` 是否一致。
   Windows PID 会被复用 → 一条陈旧超寿记录变成**随机进程杀手**。
   实测复演（纯只读，psutil 现取现比，两次独立快照）：
   **22:33 → 29 条撞号 / 22:42 → 27 条撞号**，撞主包括 `svchost.exe`、`conhost.exe`、
   `sihost.exe`、`WeChatAppEx.exe`、`promecefpluginhost.exe`(WPS)、
   `hxperformance.exe`(同花顺终端)、`rundll32 ...AweSun`(向日葵远控)、`NVIDIA Overlay.exe`、
   `ZCode.exe`、`postgres.exe`、`git.exe`、`bash.exe`（含发起复演的 shell 本身）、
   `powershell -File scripts/start_ch_health_probe...`（白名单常驻服务）、
   `python -m zephyr.data.tick_subscriber`（白名单常驻服务）、
   `pythonw -m ...worktree_drift_watchdog`（白名单常驻服务）。
   两次快照（22:33/22:42）行数稳定在 1471；期间 22:40 曾读到一次 1290 行的快照，
   疑为整文件重写的中间态、现场不可复现——只如实挂账（见缺陷 4 附注），不作结论。
2. **白名单在这条路上是假的**：`process_reaper.py:922-923` 用 `rec["cmd"]`（陈旧登记串）
   而不是存活进程真实 cmdline 去查白名单/keep——撞号杀无辜时保护完全失效。
   实测旁注（勿误读为"所以没事"）：正因查的是登记串，`worktree-drift-watchdog` /
   `write-audit-daemon` 族记录侥幸命中白名单而不被杀；但**610 条 `reconcile-worker`
   （lifetime 1800s）登记串不含任何白名单词**，这一族才是场子上上膛的子弹——
   22:42 复演的 27 条撞号里 16 条属该族，撞主为 conhost / svchost / sihost /
   NVIDIA Overlay / ZCode / WeChatAppEx / WPS / 同花顺 hxperformance / 向日葵 AweSun
   / git / bash / postgres，且**逐条 `create_time` 与 `spawned_at` 全部 MISMATCH**
   （记录来自 09-16～09-25，存活者是当天 01:51～22:42 才起的进程）。
3. **keep 串大小写敏感**：`_is_whitelisted`（`process_reaper.py:262-270`）对
   `_DEFAULT_WHITELIST` 用 `re.IGNORECASE`，对 keep 文件条目用裸 `sub in cmdline`（区分大小写）。
   keep 文件里写着 `ollama.exe serve`，账本里是 `ollama.EXE serve` → 永不命中，
   连"本想保护 ollama"的意图都没兑现。
4. **登记端"退出对账"从未接线（弹药为何常年满仓的真因）**：
   `src/zephyr/shared/infra/process_incubator.py:368-396` 提供 `sweep()`
   （子进程已亡则打 `exited_at` 戳），但全仓 grep 生产调用方**零命中**
   （唯一命中=`tests/shared/test_process_incubator.py:256`）；
   账本实测 `marked_exited=0 / 1471`——**一条都没有**，即"孵化→退出→销账"闭环
   只接了收割端，登记端从未落地。
   收割端自己的 `reaped` 回写则是**部分生效**（实测 `marked_reaped=172`），
   但 09-25 03:52/05:32/07:17/21:18/22:32 命中的记录至今仍 `reaped:false`
   （`_mark_incubation_reaped` 为整文件读-改-写，与 append/其它整写存在竞态），
   于是同一 PID 被"处决"2～3 次（17432@03:52:01+05:32:42、28652@05:32:42+07:17:49、
   27620@03:52:02+22:32:02）。在仓弹药=1471 行中 1290 条超寿未销。
   （取证注：一次读到的中间态行数为 1290、另两次为 1471，事后 3 连读稳定在 1471
   且 md5 一致——中间态现场不可复现，只如实记"读到过不一致快照"，不升级为结论。）

### 1.3 判：缺陷 or 有意？
**缺陷**（不是有意的日终回收）。三条支撑：①被杀对象的登记身份与击杀对象不一致
（身份盲是设计漏洞，不是策略）；②盘前 03:52/05:32/07:17 的"处决"不需要用日终解释——
**它们根本不是核心**，而是陈旧账本条目撞上当时存活的（多为无关）进程；
③同族 `reconcile_runner`（lifetime 1800s）也在按同样方式反复命中，说明是路径级缺陷，
不是针对核心的策略。【推断待验】09-25 那 6 次击落的**实际**对象是什么进程，
现有日志无法归因——`_log_kill`（`process_reaper.py:445-450`）只写 PID+reason，
不写被杀进程真实 name/cmdline/create_time，这是取证面的硬缺口（处置方案里要补）。

## 二、Q2 谁该把核心带回来：watchdog 现状与禁用痕迹

- 计划任务实测（`schtasks /query /tn ZephyrAlpha_TradingWatchdog /v /fo LIST`）：
  动作=`powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File
  "D:\ZephyrAlpha\scripts\start_trading.ps1"`；触发器=登陆时 + 一次性(2026-08-22 17:47:56)
  每 5 分钟重复；登录状态=只使用交互方式；**模式=已禁用**；
  **上次运行时间=1999/11/30 0:00:00、上次结果=267011(0x41303=从未运行)**。
- `scripts/start_trading.ps1`（187 行，读全文）确实是合格的重启者：
  while-true 重启 `python -m zephyr.trading`、单实例锁 `tmp/trading.lock`、
  15s 心跳 `tmp/trading.heartbeat`（>5min 视为僵尸守卫并接管）、
  守卫退出 finally 杀子、uptime<10s 判启动失败退避 30s。
- **禁用是设计，不是事故**【代码/文档，非猜测】：
  `register_guard_tasks.ps1:33-36` 与 `:113-131`、`start_trading.ps1` 头部注释
  同写 INT-03（2026-08-22，92 号 §5.4 **D3 裁定**）："当日无常驻交易生产进程，
  启用=生产行为变更 → 注册即禁用，启用属 Owner 窗口"；
  并且 `register_guard_tasks.ps1` 对已存在的该任务**只跳过不改**（保留 Owner 后续选择）。
- 从未真跑过的旁证【实测】：`tmp/trading_guard.log`、`tmp/trading.lock`、
  `tmp/trading.heartbeat` **三个文件均不存在**。
- 结论：**重启职责无主（在当前运行形态下）**。机制上"该由 TradingWatchdog 负责"，
  但它按 D3 裁定停在禁用态、且历史上从未运行过一秒；D3 的前提（"无常驻交易进程"）
  与"核心应当常驻"的现行期待已经分叉——是否成立取决于 §四（盘后该不该在跑）。
  本车道不代裁启用（启用共享态计划任务=高风险，须 Owner 门位）。

## 三、Q3 跳日与 6 次处决的因果：不成立（且前提被证伪）

- 【实测·决定性】`zephyr.data.trading_calendar.is_trading_day` 走
  `exchange_calendars` 的 **XSHG** 日历（`src/zephyr/data/trading_calendar.py`）：
  2026-09-23 True / 2026-09-24 True / **2026-09-25 False** / 2026-09-26 False /
  2026-09-28 True（09-25 恰周五、次日双休日，日历判为非交易日）。
- 【实测·同夜同路证据】`.runtime/logs/paper_session.log:179`：
  `2026-09-25 09:25:09 SKIP:  (is_trading_day=False)`
  ——盘前发车器当日自己就按"非交易日"SKIP 了；上一交易日
  （`:146` 起 `2026-09-24 09:25:03` 启动、`:178` `15:05:14 exit_code=0` 正常收场）。
- 于是 L09 三条观测可在"非交易日"单一前提下全部解释，无需收割器参与：
  `kline_index` 尾日停在 09-24（休市无新柱）、`last_audit.json` 当日零记号
  （审计链被日历闸住）、`decision_daily` 缺 09-25 目标行却有 09-28 行
  （09-28 是节后首个交易日，写"下一交易日目标"符合语义）。
- **判：09-25 跳日 与 6 次 `incubation_expired` 命中 之间因果不成立**。
  同时提请总筹回批 L09：其"09-25 是交易日"的前提与 SSOT 日历冲突，
  需按日历口径重定性（本车道不碰 L09/LANE-DAY 领地，不改哨兵尺子、不碰 decision_daily 写侧）。
- 需要保留的反面口径：哨兵尺子用 `max()` 致 lag=0 的"跳日哑火"缺陷**独立存在**
  （即便当天真是休市，"期望交易日未产出"这条硬闸该不该立，仍归 LANE-DAY 判）。
  本车道只登记该引用，不实现、不评价其实现。

### 3.1 结构证据：核心根本不在决策链上【代码·零引用实测】
- `grep -n "daily_loop\|pipeline_events\|strategy_pipeline\|warroom"
  src/zephyr/trading/auto_runtime_core.py` → **0 命中**：AutoRuntime Core 与
  16 钩子日循环/事件链**无任何耦合**，它不是这条链的生产者也不是消费者。
- 链的真触发源＝`src/zephyr/data/scheduler.py:373-404`（DataScheduler 调
  `plan_engine.daily_loop_master_switch.run_daily_loop`）——而 `ZephyrAlpha_DataScheduler`
  此刻状态=**正在运行**（schtasks 实测，下次 22:42:42），未被收割器打停。
- 当日链上痕迹【实测】：`.runtime/strategy_pipeline/pending_events.jsonl` 6 条待处理，
  其中一条正是 09-25 10:57:18 由 `data/scheduler.py:714 wire_data_scheduler` 发出的
  `PIPE-20260925-105718-d72441 sim_observe_daily {due: daily_kline,
  task_id: kline_daily_incremental}`；`last_receipt.json` 把它记为
  `skipped: why=poison_held`（`pipeline_events.py:336-345`：attempts≥MAX_ATTEMPTS 才打毒丸，
  毒丸不堵队但当日不再产）；文件 mtime 09-25 12:20。
  → 09-25 链上**有活动、有留档**，不是"整日无人唤醒"的静默断链；
  其"未产出"与核心存亡无结构通路。
- 记号面【实测】：`.runtime/strategy_pipeline/daily_decision_marker.json` 只到
  `daily_decision:2026-09-24`（无 09-25，与 §三 日历判定自洽）；
  `last_audit.json` mtime=09-25 08:43，末批为 `pf_alloc_daily:2026-09-24`→09-25T00:42:31、
  `regime_snapshot_daily:2026-09-24`→09-24T08:40 等（同样停在 09-24 业务日）。

### 3.2 对本夜在流通结论的更正请求（提请总筹回批）
- 本夜记忆/案卷中流传的口径"**收割器以 incubation_expired(24h) 处决交易核心 57 次**"
  与 §一 1.1 的账本逐条实证冲突：58 行 `owner=auto_runtime_core` 命中的登记对象
  全部是 `name=ollama-serve`（`cmd=...\ollama.EXE serve`），**不是** `python -m zephyr.trading`。
  本车道不否认"收割器有 P0 级缺陷"（§一 1.2 的四条比原定性更危险），
  但受害者身份必须改判为"任意撞号进程"。此更正建议由总筹出面回批，本车道不改他人案卷。

## 四、Q4 盘后核心零实例：按现行排班=**正常**，不是断供

- 【实测·计划任务全表】交易相关腿各有独立任务，**没有任何任务以 `python -m zephyr.trading` 为动作**：
  `ZephyrAlpha_PaperSession`（每天 09:25，09-25 09:25:02 实跑 结果 0）、
  `ZephyrAlpha_SimBridgeExecute`（09:35）、`ZephyrAlpha_PostSettlement`（每周 15:30，
  09-25 15:30:00 实跑 结果 0，下次 09-28 15:30）、`ZephyrAlpha_QMTWatchdog`（08:45/12:55）、
  `ZephyrAlpha_DecisionChainSentinel`（下次 09-26 09:40）、`ZephyrAlpha_OllamaServe`
  （仅登陆时触发、无重复）、`ZephyrAlpha_DataScheduler`/`TickSubscriber`/`CHHealthProbe` 正在运行。
  `ZephyrAlpha_TradingWatchdog` 已禁用、下次运行 N/A。
- 【代码】`src/zephyr/trading/__main__.py` 头部元数据即自证：`[STARTUP] manual`
  + M02/M10 noqa 豁免注释"CLI 触发启动，手动启动后自动运行 reconcile 循环"——
  核心在设计上就是**手动发车的常驻 reconcile 循环**，不在任何排班上。
- 【文档·同役前班已在案】`13_trading_chain_audit.md` 待办第 5 条：TradingWatchdog
  "这是裁定不是故障，但意味着**交易主进程守护当前是空位**，paper 会话靠
  ZephyrAlpha_PaperSession（09:25 拉起）+keepalive"；M4 行同判"常驻交易进程本无（D3），
  M4 语义随架构收窄"。本车道复核后**沿用该定性**：零实例=已知空位，不是 09-25 新事故。
- 盘后旁证【实测】：`tmp/live_strategy_biz.heartbeat` mtime=09-24 15:05（执行腿按交易日收点停），
  `tmp/` 下无 `trading.lock`/`trading.heartbeat`（守卫从未发车）。
- **给总筹的可操作性回答**：今晚**不需要**为"交易链恢复"去拉起核心——盘后结算腿已在 15:30 实跑并
  正常退出（exit_code=0），明日（09-26 亦休市）09-28 开盘前腿路由计划任务覆盖。
  真正因本次收割**受创的是 LLM 腿**：此刻 `ollama.exe`/`llama-server.exe` 进程数 **0**
  （psutil 实测），而 `ZephyrAlpha_OllamaServe` 只有"登陆时"触发器、无每 5 分钟重入
  ——被收割后**无人重启**，下次自愈要等登录。这一条是"重启职责无主"的实例，且落在核心侧。
- 关于任务书点名的两处尺子：`config/schedule_gate_policy.yaml` 读全文后判定**与本问无关**
  （它是 L5 AI 层排产成熟度/配额尺子，不含交易时段语义）；17 号文 §四 是 TRD-A* 的**验收判据**
  （量尺非排班），其中 TRD-A02"trigger 实跑日=设计日"恰好是本次要用的口径，
  实测结论=PaperSession/PostSettlement 两条 trigger 的实跑日与设计日一致（含按日历跳过）。

## 五、Q5 处置方案（只出方案，本车道零执行）

> 前置事实（决定所有案的次序）：账本在仓弹药=1290 条"超寿未销"记录，
> 其中 27～29 条**此刻正与存活进程撞号**；不先消这个，任何"重启/续约"都是在给随机杀手换靶子。

### 方案 A（推荐主案：治本改收割器身份判定）【代码级可定位】
改法（四处，全在 `src/zephyr/trading/process_reaper.py`，不动判定矩阵主干）：
1. A1 撞号闸：`_reap_incubated_expired` 命中后、动手前加身份一致性核——
   存活进程 `create_time` 与 `spawned_at` 差 >容差(建议 60s) **或** 存活 cmdline
   与登记 `cmd` 归一化（去引号/大小写/路径分隔符）不等 → 判 `identity_mismatch`，
   只 report 不 kill，并把该记录标 exited（消弹药）。
2. A2 白名单改查活体：`process_reaper.py:922-927` 的 `_is_whitelisted` 入参由 `rec["cmd"]`
   改为存活进程真实 cmdline（`all_procs[pid]["cmdline"]`）；`_is_whitelisted` 内
   keep 子串匹配改 `casefold()`（现有 `ollama.exe serve` vs `ollama.EXE serve` 失配实证）。
3. A3 取证面补齐：`_log_kill`（`:445-450`）增写被杀进程真实 `name`/`cmdline`/`create_time`
   ——否则下一次仍然无法归因"到底杀了谁"。
4. A4 销账可信：`_mark_incubation_reaped` 写后进程外回读核实；不符即计数告警
   （现状=击杀记录与账本 `reaped:false` 长期背离，同一 PID 被杀 2～3 次）。

影响面：reaper 一条路径 + 双端契约测试 `tests/trading/test_process_reaper_incubation.py`
（该测试钉住 ledger 路径常量与收割语义，必须同批改，否则契约假绿）。
不会放开孤儿洪水：`_reap_derived_orphans`（`:201-209/:760`）按真实 cmdline 匹配
`llama-server.exe`/`ollama.exe serve` 的那条防线本方案不动。
可逆性：纯代码，revert 即回。**门位：低**（不碰计划任务/不碰资金/不改阈值语义，
只是把"身份盲"堵上）；但属"放宽杀"，建议同批登记 A3+A4 的可观测计数，防反向失守。

### 方案 B（补充案：核心/ollama 侧语义纠错与自续约）
- B1（一行、零风险、优先）：`auto_runtime_core.py:821-826` 的
  `expected_lifetime_s=86400.0` 对 `ollama-serve` 是**语义错配**——把"一次性 worker 日终回收"
  的默认寿命套在永久服务上；且该服务已由 `ZephyrAlpha_OllamaServe` 任务管辖（双头管理）。
  改法=孵化登记不再给 ollama 超寿（或干脆不走孵化登记），并给
  `_DEFAULT_WHITELIST` 补 `ollama\.exe[\" ]+serve` 与 `zephyr\.trading` 两条
  （核心目前**在收割器面前零保护**，见 §四）。
- B2（真"自续约"）：`process_incubator` 增 `renew(record_id)` API，孵化方周期后推
  `spawned_at`；reaper 判 `now > last_renew + lifetime`。
  风险：续约要写同一张 jsonl（整文件 CAS），本役已见"标记写不进去"的蒸发迹象，
  加写频率=加蒸发概率 → **B2 排在 A1/A4 之后**，且必须复用 15 号文 EV 族的治本写法。
门位：低（代码+白名单册）。B1 与 A 案可同批，也可作为 A 落地前的最小止血码。

### 方案 C（恢复 TradingWatchdog）——**必须 Owner 门位，且顺序在 A 之后**
- 改法：`Enable-ScheduledTask ZephyrAlpha_TradingWatchdog` + `schtasks /run /tn ...`
  （`start_trading.ps1` 头注亲自指定用 schtasks 发车，禁从 IDE 终端 Start-Process，会随终端死）。
- 为什么不能先做：守卫是 while-true + 每 5 分钟重入的复活器；收割器的身份盲未修前启用，
  就是"拉起→（随机时刻）被收割→5 分钟内再拉起"的**起停抖动往复**，
  并把 29 个撞号靶子里的每一个都反复喂一遍。
- 启用同窗必须一并办（守卫脚本自己留的作业）：把 `tmp/trading.heartbeat` 接入
  `deadman_switch.ps1` 第 4 通道，否则一启用就 MISSING 假告警（头注明写）。
- 净零/裁定冲突要请 Owner 判：D3（2026-08-22，92 号 §5.4）前提"当日无常驻交易生产进程"
  与"核心该常驻"的现行期待已经分叉；启用=生产行为变更，**AI 不可自决**。
  本车道未启用、未改任何计划任务态。

### 方案 E（止血案，A 落地前唯一能立刻消弹药的动作——需总筹拍，属改运行态）
一次性清账：把 ledger 内 1290 条"超寿未销"中 `pid 已死` 或 `身份不符` 的批量标
`exited_at`（等价于把在场弹药清仓），改前把 `ledger.jsonl` 原样备份到 `G:/backup` 或
`.runtime/tmp/`。可逆（还原备份即回）。影响面：只影响 reaper 下一轮的候选集，
不动任何在跑进程；**禁在 T1/做T全量/重考首考批的运行窗口里做**（它们自身的孵化登记在册）。

### 方案 D（引用登记，不实现）
"期望交易日未产出"硬闸 = LANE-DAY 领地，本车道只登记引用、不碰其文件。
本车道供其一条口径：**硬闸输入必须取 SSOT 日历**
（`zephyr.data.trading_calendar.is_trading_day`→exchange_calendars XSHG，
09-25 判 False，且 PaperSession/PostSettlement 两腿均已按此自洽跳过）；
按"自然日"造闸会在每个节假日假告警。

### 推荐次序（呈总筹拍，非本车道决定）
**E（今晚止血）→ A1+A2+A3（治本码，同批带契约测试）→ B1（ollama 语义纠错+白名单补两条）
→ A4（销账可信）→（Owner 门位）C（启用 watchdog + deadman 第 4 通道，二件原子）**。
LLM 腿的即时恢复（ollama serve 现零实例）不在上述任何案里，需单独拍：
要么下次登录自愈，要么人工发车——本车道未动。

## 六、遗留不可判项（如实挂账，不凑故事）

1. 09-25 那 6 次击落的**实际**进程身份：日志字段不足（`_log_kill` 不记活体 name/cmdline），
   账本又被蒸发式重写，**不可判**；能判的是"它们不是以'核心'身份被登记的"。
2. 09-25 10:37 `runtime_dir_orphan`、11:47 `orphan_aged`、20:27 `orphan_aged` 三次击杀
   的对象是否含交易链进程：同样无法从日志归因（A3 修完才可判）。
3. `_mark_incubation_reaped` 不落地的根因二选一未验：
   整文件重写竞态（孵化方 append 覆盖）vs 账本 CAS 拒写降级
   （`process_incubator.py:393-395/411-413` 明示拒写即放弃）。两者都指向同一条治本要求（A4）。
4. reaper `--status` 显示 `last_run=2026-09-25 01:47:24`，但 kill log 有 21:18/22:32 命中
   ——status 文件与实际轮次不同步，属观测面缺口，未深查（不越车道权限）。

1. `data/runtime/reaper_kill.log`（`grep -c owner=auto_runtime_core` = 58 行：
   总筹 22:30 测得的 57 次 + 22:32:02 新命中一行；09-25 当天 6+2 次，含 03:39:28 [FAILED]）
2. `.runtime/process_incubator/ledger.jsonl`（1471 行；1290 条超寿未销；core 36 条全为 ollama-serve）
3. `src/zephyr/trading/process_reaper.py:894-947 / 909 / 916-927 / 262-270 / 445-450 / 184-209`
4. `src/zephyr/trading/auto_runtime_core.py:821-826`（登记点，owner 语义出处）
5. `schtasks /query /tn ZephyrAlpha_TradingWatchdog /v /fo LIST`（已禁用/从未运行）
6. `scripts/start_trading.ps1` 头部 D3 注释 + `scripts/register_guard_tasks.ps1:33-36,113-131`
7. `src/zephyr/data/trading_calendar.py`（XSHG 日历）+ `.runtime/logs/paper_session.log:179`
8. 撞号复演探针：`python -c` 以 psutil 现取进程表比对全部超寿未销记录（29 撞号，见 §一 1.2）
