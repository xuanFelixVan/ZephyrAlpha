---
ttl: task_bound
title: M5 补挖波 · 备份冷储/环境启动链/性能水位/管线路由（90_backfill_wave）
session: st-fflead-m5-backfill
---

# M5 补挖波 · 总册（90_backfill_wave）

> 立册 2026-09-25 23:4x ｜ 挖矿会话 st-fflead-m5-backfill ｜ 只读挖矿：零 git 写、零 enqueue、
> 零主区改动（除本册）。环境实证：`$env:PATH` 前插 Python312 后 `python --version` = **3.12.8**。
>
> **本册定位**：编排册 M5 行（`docs/_working/fullflow_mining/00_orchestration.md:40`）点名五类补挖
> 项。前四类姊妹波 `补挖波_20260925/`（session st-ailayer-fullflow-sc，09-25 01:4x~05:47 落盘）已
> 成册。本册**不复制姊妹波证据**，做三件事：①对四册当日活探复核（结果：备份面与水位面各发现
> **一处姊妹波未见的红**）；②补挖姊妹波完全未触碰的第 5 项「管线路由的调度属性」（F122/X7）；
> ③三地雷现状复核（1 修 / 1 仍红 / 1 转绿留历史洞）＋ FBL 语义歧义判定。

## 〇、与姊妹波的分工对账（防重复挖矿）

| 编排册点名项 | 姊妹波册（相对 `m5_scheduling/补挖波_20260925/`） | 本册动作 | 本册复核结论 |
|---|---|---|---|
| ① 备份冷储 3-2-1 | `03_backup_coldstore.md`（判"绿（备份面）"） | 当日 state json + report json + 任务码活探 | **降为红**：今日 `last_backup_status=failed` |
| ② FBL | `01_fbl_feedback_loop.md`（判=反馈回路 F84） | 全仓语义检索 + 注册表 ID 族取证 | 姊妹波判定**正确**；"预算帽类 FBL"＝**查无**（§三·2） |
| ③ 环境启动链 | `02_boot_chain.md`（判=五层启动形态 F85） | 加挖姊妹波未做的 **RULE-PATH 实际消费方/失效后果**切面 | 新增：任务侧钉绝对 exe 免疫 PATH 漂移，唯一 PATH 依赖点＝tilib bat（§三·3） |
| ④ 性能水位台账 | `04_perf_watermark.md`（判"绿，breached=[]"） | `--status` 重跑 + 任务退出码活探 | **降为红**：水位台账 22h 未刷新，reaper 任务每轮 exit 1（§三·4） |
| ⑤ 管线路由调度属性 | **无**（`00_overview.md:9` 五项清单不含路由） | **本册新挖** | 挖干可施工，附 2 待裁（§三·5） |
| 附：F82 order_daemon | `05_order_daemon_wiring.md` | 引用不重挖 | 六断点清单维持 |

**M5 车道内「待挖」缺口清点**（判据=`00_skeleton/00_全环节总册.md` 的 status 列）：M5 段带 partial
的三行 = F82（`147 行`，partial/P0）、F84（`149 行`，partial M5 补挖项）、F85（`150 行`，partial M5
补挖项）→ 姊妹波三册已各闭合；`207 行` F122 管线路由 = partial（M0 待裁 M4/M5 边界）= **编排册
M5 行点名而两波均未挖的唯一项**，本册 §三·5 补。分工册 SC 行（`00_挖矿分工册.md:27`）"接补挖项
（FBL/启动链/备份冷储/性能水位）"与 XC 行（`:31`）"F122 管线路由 M4/M5 边界待裁"互为对账锚。

## 一、环节定义与边界

**一句话**：本册＝M5 调度常驻链的"补挖波收口环节"——把编排册点名而车道未闭合的**调度属性面**
（备份链触发/水位台账真源/启动链环境依赖/管线路由的分派语义）挖到六向可复核。

- **供料方（上游）**：编排册 M5 行点名清单（`00_orchestration.md:40`）；姊妹波四册；总册 F76-F85/F122 行；
  实盘侧 = Windows 任务库（49 件）、`config/*` 路由与阈值册、`G:/F:` 盘位、备份 state/report json。
- **消费方（下游）**：总筹（三态裁决与待裁收纳）；施工班（§四 每条修法带归属）；M3 治理链（reaper
  exit-code 语义与 S6 报警疲劳同族）；M4 AI 层（管线路由选读面归属）；M1 数据链（tilib 回填链修复）。
- **不在本册边界内**：姊妹波五册已证的结构性结论（FLE tick 零调用、六断点、五层启动形态）只引用
  不重挖；提交链自身（commit_speedup 战役）按编排册 `:64` 令不重复挖。

## 二、六向台账（本补挖波 scope 整体）

| 向 | 实证 |
|---|---|
| 上游输入 | ①备份：`D:\ZephyrAlpha` 主区 + DB dump + CH base/inc + `F:\zephyr_cold` + 仓外 4 target（`scripts/backup/backup_config.yaml`，姊妹波 `03:12-20` 六 STAGE 真源）。②水位：psutil 采样 + `config/alert_rules.yaml`（本波实读 `ALERT-SYS-001..005` 五条在位，行 21/35/53/63/73）+ `alert_threshold_registry.yaml` v1.6.0（`:35`）。③启动链：Windows SCM / 登录会话 / toolhost 进程生灭（姊妹波 `02:33`）。④路由：task_card 与 path_pattern/task_keywords（`config/blueprint_routing.yaml` 文件模式注释 `:26-32`）。 |
| 下游消费 | ①恢复场景（`restore.ps1`/`restore_drill.py`）+ INV-11 交叉核验读 `system.backup_log`。②通知板 JSONL→api_server OpsAlertFeed；晨报（MorningReport）；收割决策（reaper）。③AutoRuntime Core 子系统束。④路由消费方=`src/zephyr/integration/mcp/blueprint_search_server.py:84 ROUTING_YAML_PATH`（本波实读）+ `pipeline_roadmap.py:505-509` MOD-CONTEXT_ENGINE `config_consume`＝✅ implemented。 |
| 自动化触发 | 备份：`ZephyrAlpha-DailyBackup`（本波活探 LASTRUN=2026/9/25 6:00:01 RESULT=**267014**）+ backup_reconciler 事件触发 + 两 drill 月窗 10-01。水位：`ZephyrAlpha_ProcessReaper` PT≈5-6min（LASTRUN=2026/9/25 23:41:28 R=**1** NEXT=23:47:22）、ResourceSamplerScan（23:41:28 R=0）。启动链：Logon＋PT1M 注入群（姊妹波 `02:22`）。**管线路由：零计划任务、零 DataScheduler 槽**——实际触发沿=AutoRuntime Core 进程内 `TaskQueue.start_polling()`（`src/zephyr/trading/auto_runtime_core.py:1116` 日志串 "TaskQueue polling started (interval=300s)"）。 |
| 真源与注册表 | `data/databases/backup_state.json`（备份 verdict）＋`logs/backup_report_*.json`（STAGE 明细）；`docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml`（REG-ATH-001，本波实测 **49** 条唯一 threshold_id：`grep -oE "THD-[A-Z0-9]+-[0-9]+" \| sort -u \| wc -l`→49，键名 `threshold_id` 见 `:43/:64`）；`config/resource_profile_registry.yaml`（`total_entities: 98` 于 `:14`，`generated_at: '2026-09-24T21:21:27Z'` 于 `:10`）；`config/blueprint_routing.yaml`（module_id MOD-INF-002，`belongs_to: mod_inf_009`，ttl permanent）；`src/zephyr/infrastructure/pipeline/models.py`（运行态调度参数）。 |
| 门禁与质量尺 | INV-11 假绿闸（CH 段 ok 落账前须过 `system.backup_log` 交叉核验，姊妹波 `03:27`）；free_floor fail loud；阈值加载 fail-closed；三分互斥（拒生/收割/准入，`process_reaper.py:57` 头注）；宪法 §9.3（事件触发，路由与 order_daemon 同尺）；G6 dispatch 前蓝图已读检查（`pipeline_roadmap.py:497-502` MOD-GATE_ENGINE `pre_check`＝"dispatch()前G6检查——AI是否已读蓝图"，✅ implemented）。 |
| 当前运行状态（绿/黄/红） | **红×2 + 黄×2 + 绿×1**（详见 §三，每条附实测命令）：<br>·④水位台账＝**红**（`--status` 打印 22h 前的缓存快照，reaper 任务每轮 exit 1）<br>·①备份＝**红**（今日 `last_backup_status=failed`；`last_backup_log_verified=False` 维持）<br>·③启动链＝**黄**（姊妹波五层判黄维持；本波加证：宿主 AutoRuntime Core 今日不在进程表）<br>·⑤管线路由＝**黄**（选读路由绿；运行态分派链因宿主不活＝idle，且 4 条调度依赖 Backlog）<br>·②FBL＝**红（回路 A）/黄（回路 B）**（姊妹波 `01:34` 判定维持，本波无新增反证） |

## 三、子模块清单（五类补挖项逐条：是什么 / 入口 file:line / 状态）

### 3·1 ① 备份冷储 3-2-1 链（当日复核 → 姊妹波"绿"降级为"红"）

流水线本体与六触发通道以姊妹波 `03_backup_coldstore.md:12-31` 为已挖面，本波只记**当日新证与漂移**：

| 子件 | 入口/证据 | 本波实测 |
|---|---|---|
| 备份 verdict 真源 | `data/databases/backup_state.json` | `last_backup_status = failed`；`last_backup_time = 2026-09-25T15:06:46.0902505+08:00`；`last_backup_log_verified = False`；`last_ch_backup_status = ok`＋`last_ch_backup_verified = True`（CH 段过 INV-11，非 CH 段整体失败） |
| 本轮 STAGE 明细 | `logs/backup_report_20260925_060007.json`（**含 UTF-8 BOM，须 `encoding='utf-8-sig'` 读**，否则 json 抛错） | `mode=all` `force_mode=True` `duration_seconds=32796.4`（06:00 起跑、15:06 出报告＝9.1h）；`code_backup`：`mode=versioned failures=1 robocopy_exit=0 hardlinked=234299 copied=187513 vanished=5 prev_snapshot=G:\backup\working_vault\20260924 day_target=…`；`offrepo_backup.targets`：trae_memory ok/qmt_bridge ok/cold_archive `robocopy_exit=1 status=ok`(147.6GB)/stash_archive；`g_mirror.targets.zephyr_cold robocopy_exit=1 status=ok`；`databases.postgres/clickhouse` size_match=True |
| 任务码与"仍在跑"疑影 | `Get-ScheduledTaskInfo` | DailyBackup LASTRUN=2026/9/25 6:00:01 **RESULT=267014（=任务仍在运行码）**，而报告已于 15:06 写出 → 出报告后 8.6h 任务态未收束＝僵尸/孤儿子进程嫌疑（本波新发现） |
| 备份锁互斥 | `logs/backup_skipped_20260925_{114424,125932,131508}.json` | `reason=lock_held mode=all force=false lock_age_hours=3.21 lock_mtime=2026-09-25T10:02:41+08:00` → 长跑期间 reconciler 后触发全被吞（姊妹波"备份锁互斥"这条闸今日实际发生） |
| 三副本对账（3-2-1 实体） | 盘位活探 | 副本1 主区 `D:\ZephyrAlpha`；副本2 `G:\backup\working_vault`＝`20260921/22/23/24/25` 五日连续＋`env_cleanup_20260923`；冷库原件 `F:\zephyr_cold`＝00_manifest/10_inbox/20_raw/30_corpus/40_migration/50_archive/90_tmp 七区在盘；兜底镜像 `G:\zephyr_cold\60_mirror\zephyr_cold_main`＝**8 个子目录在盘**（PowerShell Measure-Object 实测） |
| git bundle 4 天未刷之谜（姊妹波 `03:52` 堵点 3） | `backup_report_20260925_060007.json` 的 `git_bundle` 字段 | **根因定位**：`{'status': 'skipped', 'age_days': 3.67, 'reason': 'fresh', 'latest': 'zephyralpha_full_20260921.bundle'}`＝短路判据把 3.67 天判为"新鲜"，非缺陷而是阈值语义（→ §六 待裁 R4） |
| 恢复演练 | 姊妹波 `03:28-29` | 维持：`ZEPHYR-RESTORE-DRILL`/LibraryLedgerDrill 首窗 10-01，267011＝从未跑 → **3-2-1 第三条腿"可恢复性"今日仍零实证** |

### 3·2 ② FBL：语义判定 + "预算帽类"查无取证

- **项目内 FBL 唯一实义＝反馈回路（Feedback Loop）**，与姊妹波判定一致。注册表侧证（本波实读）：
  `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml:6025 CAND-FBL-001`、
  `:7723 CAND-FBL-002`（头注 `:30` 释义＝"FLE 自卫门禁激活专项"）、`:13707 CAND-FBL-003`、`:13736 CAND-FBL-004`；
  `architecture_issue_registry.yaml:20532` 出现 `MOD-FBL-001`、`:20804` `MOD-FBL-002~004`；
  `docs/registry_of_registries.yaml:473` 记 "e27cf22c FAC/**FBL** 去重删 11 条"。总册 `00_全环节总册.md:149`
  F84 行原文＝"反馈循环 FBL …… `src/zephyr/feedback_loop/`"。
- **"feature/business 预算帽类 FBL"＝查无**。检索面与关键词（全为 `-r` 全仓，含 `src/ config/ scripts/
  docs/01_policies_and_standards/rules/ docs/01_policies_and_standards/_registry/ registry_of_registries.yaml`）：
  `feature budget`／`feature_budget`／`business budget`／`business_budget`／`budget cap`／`budget_cap`／
  `预算帽`／`fbl_limit`／`\bFBL\b`。**命中 0 个以 FBL 命名的预算帽件**。查到的"预算帽形"件均另有其名，列此供总筹判"是否被误称为 FBL"：
  `src/zephyr/governance/ops_governance/self_budget_tracker.py:30 budget_cap: int`（AI 自身日报预算）·
  `config/search_space_prereg.yaml:53 budget_caps:`（回测搜索空间预注册帽，`config/schedule_gate_policy.yaml:97` 注其 gpu 箱同值）·
  `scripts/backtest/factory_grid_executor.py:862 caps = cfg.get("budget_caps")`·
  `src/zephyr/pf_core/rl_portfolio_execution.py:155 risk_budget_cap`·
  `src/zephyr/pf_alloc/allocation_orchestrator.py:490 "STRATEGY_BUDGET_CAP"`。
- **反馈回路本体状态**：姊妹波 `01_fbl_feedback_loop.md:34` 判"红（回路 A：FLE tick 零生产调用）/黄（回路 B：4 月仅 1 提案）"，
  本波反查 `auto_runtime_core.py` 与进程表未见任何 FLE 触发沿新增件；宿主 AutoRuntime Core 今日不活（见 3·3），
  回路 A 的"零触发"今日依旧无法被活探推翻 → **判定维持，不升不降**。

### 3·3 ③ 环境启动链 · RULE-ENV PATH 修正的实际消费方与失效后果（姊妹波未挖的切面）

**四类消费方分层（本波实测，姊妹波 `02_boot_chain.md` 只挖了五层启动形态，未挖环境依赖向）**：

| 消费方类 | 实证 | 对 PATH 修正的依赖 |
|---|---|---|
| A. 计划任务注册脚本（25+ 件） | `grep -rln "Python312" scripts/*.ps1` → 25 个 `register_*/run_*` 命中。样例：`scripts/register_post_settlement_task.ps1:34` `$pythonExe = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"`；`scripts/register_process_reaper_task.ps1:51-53`（`$env:LOCALAPPDATA` 主路 + `C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe` 硬编码兜底）；`scripts/run_sim_bridge_execute_daily.ps1:49-51`（同双路形态） | **免疫**：任务 action 里烤的是**绝对 exe 路径**，不走 PATH 解析 → RULE-ENV 失手不会打挂计划任务 |
| B. 仓内 .bat 包装（唯一 PATH 依赖件） | `scripts/data/backfill_night.bat:3` `set PATH=C:\Users\fanzi\AppData\Local\Programs\Python\Python312;...\Scripts;%PATH%` | **强依赖且写死用户名**：目录缺失即回落 `%PATH%` 头一位（可能是 3.10）；且 `C:\Users\fanzi` 硬编码=换机/换用户即哑 |
| C. AI 会话/工具宿主 shell | 本波实测：全新 Git Bash（**未** export 前）`python --version` = **3.12.8**；PowerShell `(Get-Command python).Source` = `C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe` | 机器级默认已是 312；RULE-ENV 的 hazard 源＝IDE/工具宿主注入 3.10（AGENTS §0.1 声明），非 OS 默认 → 本会话未复现注入 |
| D. 常驻守卫（启动链宿主本身） | 本波活探：23:4x 见 `pythonw.exe src\zephyr\trading\process_reaper.py`（PID 36404，**one-shot 在跑态**，23:47 复跑即 0 行＝非常驻，判据勿误读）；三守卫心跳新鲜 `tmp/scheduler.heartbeat`＝`2026-09-25T23:42:19+08:00\|34596\|35244`、`tick_subscriber`＝`23:42:20`、`ch_health_probe`＝`23:42:19`；**`python -m zephyr.trading`（AutoRuntime Core）进程两次活探皆零** | AutoRuntime Core 未起＝F85 的 L4 主入口今日缺席，连带 F122 分派链 idle（见 3·5） |

**失效后果（可量化，非推测）**：`grep -rn "datetime.UTC\|from datetime import UTC" src/zephyr/ --include=*.py | wc -l` = **466**。
`datetime.UTC` 是 3.11+ 才有的别名 → 3.10 解释器 import 期即 `AttributeError`，覆盖面 466 处，等于"任何一条以 3.10 起的
python 命令行/任务/会话，凡触到这些模块即首行崩"。与 AGENTS §0.1 的"TRAE 注入 3.10 会崩 `datetime.UTC`"口径互证。
失效后果分级：类 B 最脆（PATH 依赖+硬编码+日志目录可清区三重叠加，今日实证见 3·6 地雷 2）；类 A 只在"重注册时
脚本自身被 3.10 跑"才中招（PowerShell 起 python 跑注册脚本→脚本内再 pin 绝对路径，故实为脚本宿主 shell 的版本问题）。

### 3·4 ④ 性能水位台账（当日复核 → 发现"绿"是缓存读数）

| 层 | 真源/入口 | 本波实测 |
|---|---|---|
| 层1 进程收割 | `src/zephyr/trading/process_reaper.py:161 _DANGEROUS_MEM_GB = 10.0`；判定权三分 `:57` | 与姊妹波一致，未见改动 |
| 层2 系统水位闸 | `src/zephyr/infrastructure/capacity_assurance/host_resource_governor.py:224 check_system_watermark()`；规则 `config/alert_rules.yaml` 的 `ALERT-SYS-001..005`（本波实读行 21/35/53/63/73） | 规则在位 5 条 |
| 层3 阈值 SSoT | `alert_threshold_registry.yaml` v1.6.0（`:35`），`unique_key: [threshold_id]`（`:43`） | **49 条唯一**（命令见 §二"真源"向）→ 姊妹波 `04:26` 的 49 与总册 F81"38"之间，**49 为实测真值** |
| 画像注册表 | `config/resource_profile_registry.yaml:14 total_entities: 98`、`:10 generated_at '2026-09-24T21:21:27Z'` | 98 确认（姊妹波一致，总册 F80"96"为漂移）；**但 generated_at 距今≈26h**，RegenCheck 号称 PT1H → 画像再生是否真跑须看 §四 D3 |
| **台账读数新鲜度（本波新发现）** | `python -m zephyr.trading.process_reaper --status` | 23:4x 执行，输出 `last_run=2026-09-25 01:47:24`，`watermark` 五项数值与姊妹波 01:47 基线**逐位相同**（ram_used_pct 69.8 / commit_pct 77.59 / cpu 61.8 / degraded False / `breached=[]`），`scanned=23 whitelist_hits=17 killed=0 reported=19`，`drift={'stash_count':0,'worktree_changes':1031}` |
| 任务侧对照 | `Get-ScheduledTask -TaskName "*Reap*"` | `ZephyrAlpha_ProcessReaper Ready LAST=2026/9/25 23:41:28 **R=1** NEXT=23:47:22` → 每 5-6min fire 但 exit 1，state 自 01:47 起**未刷新≈22h** |

**结论**：`--status` 打印的是**持久化快照**而非活探（姊妹波把该读数当"当日绿"引用，方法学漏判）。
健康判据应回到 05 册 row 3 的"last_run 距今 <12min"——本波实测＝**22h，红**。

### 3·5 ⑤ 管线路由的调度属性（F122/X7，本波新挖；M0 裁 M4/M5 互引的落点）

**两物同名"路由"，必须先拆**（代码级边界声明就是 M0"互引"裁定的真源落点）：
`src/zephyr/infrastructure/pipeline/ct_pipe_routing.py:23-24` 原文＝"与 `config/blueprint_routing.yaml`
的边界：本模块输出 **Mx 入口决策**（CT-PIPE-ORC-001）；**blueprint_routing 仅为关键词/路径→蓝图文档索引**
（MOD-INF-009，供选读与 `blueprint_search`）"。

**(a) 选读路由侧（归 M4 AI 层，调度侧只消费其优先级语义）**

| 属性 | 实证（`config/blueprint_routing.yaml`，828 行） |
|---|---|
| priority | `:32` 文件模式注释"priority: 1-100 —— 并发匹配时取最高优先级（参考 COBIT APO03）"；实读条目 priority 分布 30~100（`:80`=100、`:108`=90、`:146/:162`=30、`:805`=78 等 30+ 处） |
| scope | `:31` "pre_change（修改前加载）/ post_change（修改后加载）/ always"＝**变更时序属性**，与调度"何时触发"同构，是路由表里唯一的时间语义 |
| safety | `:30` L/M/H 路由安全等级 |
| fallback | `:813-817` `enabled: true` / `strategy: "keyword_count_then_priority"` / `min_keyword_hits: 1` |
| agent_hints | `:824-828` `enabled: false` `activated_in: "Phase_3"`（**设计态未启**） |
| 消费方 | `integration/mcp/blueprint_search_server.py:84 ROUTING_YAML_PATH`、`:156`（增量刷新索引子命令）、`:13` 错误契约 `ZA-BPS-0001`（missing/unreadable→fail-soft）；`pipeline_roadmap.py:505-509` MOD-CONTEXT_ENGINE `config_consume` "blueprint_routing.yaml->触发路由匹配" ✅ implemented；`:604` 注 "5.12.4 修复：相对路径（原 `D:\ZephyrAlpha\...` 硬编码）" |
| **调度属性实测** | **零计划任务、零 DataScheduler 槽、零 cron**——纯同步查表（Agent 决定读哪份蓝图时查）。即：M5 侧无调度件可挖，只有"优先级/时序 scope 可否被排产消费"的设计问题（→ 待裁 R1） |

**(b) 运行态编排侧（归 M5 调度，本波找到的唯一真实挂点）**

| 调度属性 | 真源 file:line | 状态 |
|---|---|---|
| 触发沿 | `src/zephyr/trading/auto_runtime_core.py:1096-1116`：`_BootSubsystemRegistrar` 内 `core._task_queue = TaskQueue()`（`:1096`）→ `_dispatch_handler` 里 `po = PipelineOrchestrator()`（`:1103`）+ `po.dispatch(task)`（`:1107`）→ `set_dispatch_handler`（`:1114`）+ `start_polling()`（`:1115`）；`:1116` 日志 "TaskQueue polling started (interval=300s)" | **进程内 300s 轮询**，非计划任务；`:1110` 注 "5.12.1 修复：原 except: pass 静默吞任务派发失败（任务黑洞）"（`:1111` 现改 `logger.exception`）。今日宿主不活＝整链 idle（3·3 类 D） |
| 并发/互斥 | `infrastructure/pipeline/pipeline_lock.py`（`PipelineLock`/`LockResult`，orchestrator `:135` 引、`:380/:390` 注、`:64-74` helper `_setup_lock_and_skills`＋finally 条件 release） | 件在 |
| 优先级截断/抢占 | `infrastructure/pipeline/preemption_manager.py:69 priority_cutoff: str = "P2"`（orchestrator `:417` 同值实参）；`models.py:381-384` `preempted_task_id/preempted_by_task_id/preempted_priority/preempted_at` | 件在 |
| 重试/退避 | `models.py:337 retry_count: int = 0`、`:350 wait_before_retry_s: int = 300`、`:479 RETRY="retry"`、`:502 retry_max: Field(default=0, ge=0, le=3)`、`:522/:638/:662 retry_max=1` | 件在（上限 3，语义内） |
| 周期采样 | `models.py:401 periodic_profile_interval_s: float = 3600.0`；orchestrator `:17` M10 豁免注（`while+sleep` 是 benchmark 周期触发，非 reconciler 时间触发；四要素 `_periodic_stop_flag`+`stop_periodic_profile()`+`shutdown()` join） | 件在且合规 §9.3 |
| 失败隔离族 | `infrastructure/pipeline/` 实测在册：`circuit_breaker_manager` / `dead_letter_queue.py:77 retry_count=max_retries` / `backpressure_manager`+`backpressure_types` / `cost_tracker` / `model_router` / `routing_plugins` / `pipeline_agent_bridge` / `pipeline_roadmap` | 件在 |
| **未闭环调度依赖**（本波逐条读 `pipeline_roadmap.py:495-560` Dependency 表） | `:511-516` MOD-FEEDBACK_LOOP "FLE反馈->调复杂度估计->重新路由"＝📋 **Backlog**；`:517-522` MOD-INF-003 "Orc.create_task->Pipe.dispatch->Orc.assign_session"＝📋 **Backlog**；`:539-544` SH-DB-001 DeferredQueue "dispatch LOCKED->DeferredQueue.enqueue->auto-retry"＝📋 **Backlog**；`:545-550` MOD-INF-001 Capacity Assurance "Kill Switch前置检查+Token Budget扣减+Graceful Degradation"＝📋 **Backlog**（✅ 项：MOD-GATE_ENGINE `pre_check`、MOD-CONTEXT_ENGINE `config_consume`、MOD-INF-016、MOD-LLM_SECURITY） | **四缺**：反馈重路由 / 编排-分派闭环 / 锁等待转延迟队列 / 容量准入与预算扣减 |

**本波对"路由归属调度侧要挖什么"的答**：要挖的不是路由表本身（那是 M4 选读物），而是
**(i) 分派触发沿的宿主活性**（AutoRuntime Core 300s 轮询，今日缺位）与 **(ii) 上表四条 Backlog
调度依赖**——它们才是"调度属性"的实缺面。

### 3·6 三个已知地雷现状复核（主波 `04_silent_failure_modes.md` S1/S2/S3）

| 地雷 | 原判（主波 04 册） | **本波现状复核** |
|---|---|---|
| 地雷1 PostSettlement 注册脚本被 `bc76efe3bf` 覆盖回退 | S1：HEAD 是坏形态（`python.exe -u ... >> log 2>&1`），重注册即复断 | **已修，非回退态**。`git log --oneline -3 -- scripts/register_post_settlement_task.ps1` 顶部＝`a0446129e3 [st-commitspeed-tbl-20260924][批·M5S1-调度地雷修复] PostSettlement 注册脚本回退逆转：纯回植 8f0e5feba9 修复块`（其下即 `bc76efe3bf`、`8f0e5feba9`）。工作区实读 `:43-48`＝`$conhost = Join-Path $env:SystemRoot "System32\conhost.exe"` + `--headless -- cmd.exe /c … >> log 2>&1`（好形态）。live 任务 `ZephyrAlpha_PostSettlement` LASTRUN=2026/9/25 15:30:00 **RESULT=0** → 脚本↔任务双绿无漂移。**残余风险**＝病灶 5 类（注册脚本↔live 漂移）无机制防复发，归 M3/提交链 |
| 地雷2 tilib 夜回填住 `.runtime/tmp` 夜夜 exit 1 | S2：重定向目标目录不存在，探针脚本住可清区 | **仍红，未修**。任务 LASTRUN=2026/9/25 2:30:01 **RESULT=1** NEXT=2026/9/26 2:30；`ls .runtime/tmp/tilib-probe` → "No such file or directory"；`scripts/data/backfill_night.bat` 全文四行仍是 `set PATH=C:\Users\fanzi\...Python312;%PATH%` + `python scripts\data\backfill_technical_indicator_dwm.py > .runtime\tmp\tilib-probe\backfill_night.log 2>&1` + `python .runtime\tmp\tilib-probe\night_probe.py > ...`（第 1 行重定向失败、第 2 行脚本缺位）；任务 action 实测 `EXEC=[D:\ZephyrAlpha\scripts\data\backfill_night.bat] ARGS=[]`。**注意**：编排册 `:46`/`:52` 记施工袋"0041(S2 tilib ps1)"已落地，而 live 任务 action 仍指旧 `.bat`＝修复若存在也未接到任务（→ §四 D5） |
| 地雷3 SimBridgeExecute 09-24 静默断链嫌疑 | S3：09-24 13:05 无日志 + 非标准码 4294770688 | **今日转绿，历史洞维持**。任务 LASTRUN=2026/9/25 13:05:01 **RESULT=0**；`.runtime/logs/sim_bridge_execute.log` 尾部四行＝`2026-09-23 13:05:07 bridge-execute … exit_code=0` → `2026-09-25 09:35:10 SKIP: non-trading day (is_trading_day=False)` → `2026-09-25 13:05:08 SKIP: non-trading day`。包装层活着并按日闸 SKIP 留痕。**但日志从 09-23 直接跳到 09-25，09-24 两班仍零行**——`zephyr.data.trading_calendar.is_trading_day` 实测 09-22 Tue→True / 09-23 Wed→True / 09-24 Thu→True / 09-25 Fri→**False**，即 09-24 确为交易日而该日无任何包装层日志＝**静默断链嫌疑不因今日 exit 0 而洗清**，取证需求（Windows 事件日志 Task Scheduler 操作通道）维持，归 M7 S3 线索 |

## 四、堵点与病灶（现象/根因/修法草案/预估工作量/是否本车道可修）

| # | 现象（本波实测） | 根因 | 修法草案 | 预估工作量 | 本车道可修？ |
|---|---|---|---|---|---|
| D1 | 备份 verdict `failed`（09-25 15:06），同轮 `code_backup.failures=1` 而 `robocopy_exit=0`、`hardlinked=234299`/`copied=187513` 看着健康 | 失败位来自 STAGE 内**非退出码**判据（vanished=5 或子 target），而 verdict 只落一个布尔——细粒度丢失，读 state json 不知"哪一段失败" | `backup.ps1` 把 failures 明细结构化落 state json（stage/子件/原因），verdict 分级（ok/partial/failed） | 中（0.5 日，纯脚本+json，不触生产库） | 否（备份属 M1/D 组施工面；本车道只出判据） |
| D2 | DailyBackup `RESULT=267014`（任务仍在运行）距报告写出已 8.6h；期间 3 次 reconciler 触发全 `lock_held`（lock_age 3.21h） | 9.1h 长跑（cold_archive 147GB）无看门狗；出报告后任务树未收束＝孤儿进程/结果码不回写 | ①STAGE 3c 大 target 增 `--max-run-hours` 与进度心跳；②锁带 TTL+mtime 越限告警（现仅互斥不告警）；③重跑前用 `Get-ScheduledTaskInfo` 判僵尸再决定 Force | 中 | 部分（心跳/锁 TTL 是调度件，归本车道；robocopy 面归备份班） |
| D3 | 水位台账 22h 未刷新：`--status` 打 01:47 缓存；任务每轮 **exit 1** | reaper 任务本体失败（非水位命中），失败即不写 state → 台账"看上去绿、实为陈旧"；姊妹波与 05 册 row 3 都被该读数误导 | 先取 exit 1 真因（任务 action 直跑一次带日志），再：①`--status` 输出加 `state_age_min` 并在 >2 倍周期时打 stale 标记；②05 册 row 3 判据改为"last_run 距今 <12min **且** LastTaskResult=0" | 小（判据 0.2 日；根因待取证） | 是（判据+stale 标记是本车道；exit 1 根因若在读文件逻辑则共修） |
| D4 | 画像 `resource_profile_registry.yaml` `generated_at` 09-24T21:21Z（≈26h 前），与"RegenCheck PT1H 再生"不符 | 再生链只在 exit 3（检出漂移）时跑 `--auto-regen`；无漂移即不刷时间戳 → 无法区分"没漂移"与"没跑" | RegenCheck 落一行 `last_check_ok_at`（与 regen 时间戳分离），晨报消费该字段 | 小 | 是 |
| D5 | tilib 夜回填仍 exit 1（见 3·6 地雷 2），而编排册记 0041(S2) 已落地 | 任务 action 仍直指 `scripts/data/backfill_night.bat`（旧形态），修复件未接到任务注册面 | ①`.bat` 两行日志目录改 `logs/`（仓内）＋`night_probe.py` 正名入 `scripts/data/`；②重注册 tilib 任务 action 指向修好后件；③按宪法 §9.4 加一条 lint：注册脚本/bat 禁引用 `.runtime/tmp`（防第五类横断病复发） | 小-中 | 部分（重注册属 M1/数据链；**§9.4 lint 建议转 M3**） |
| D6 | 管线路由四条调度依赖全 Backlog（FLE 重路由 / Orc↔Pipe 闭环 / DeferredQueue 自动重试 / 容量准入+预算扣减）＋分派宿主 AutoRuntime Core 今日不活 | 编排链"件齐线缺"：锁/抢占/重试/死信/DLQ 组件皆在，**但把它们串成常驻自动链的沿未施工**；宿主缺席即整链 idle | ①分派链活性纳入 05 册健康总表新增一行（判据＝`-m zephyr.trading` 进程存在 **或** TaskQueue 心跳新鲜，缺＝黄）；②DeferredQueue（SH-DB-001）与 Capacity Assurance（MOD-INF-001）两条 Backlog 立跨车道工单族，与姊妹波 `00_overview.md:27` "事件沿接线工单族"合并 | 大（跨 M2/M4/M5，估 3-5 日） | 部分（活性判据行本车道可修；Backlog 依赖属 AI 层/容量域） |
| D7 | 备份报告 JSON 带 UTF-8 BOM，标准 `json.loads` 直接抛 `Unexpected UTF-8 BOM` | PowerShell `Out-File -Encoding utf8` 产 BOM（主波 05 册头注已知病，扩展到 logs/*.json） | 读侧统一 `encoding='utf-8-sig'`；写侧改 `utf8NoBOM`（PS7）或 `[IO.File]::WriteAllText` | 小 | 是（复核命令已在 §七 用规避式） |

## 五、提速与合并机会（Owner 令"能合并的合并"）

1. **两波合一（本册即收口册）**：姊妹波 `00_overview.md:12-22` 的五册三态与本册 §〇 对账表可合并为
   M5 车道唯一入口册（编排册 M5 行只指 `90_backfill_wave.md`，五册留作分册证据），省总筹逐册读。
2. **同真源可派生 → 必并（w5_1 判据）**：05 册 row 3/row 18/row 20 的"探活"与本册 D3/D5/① 的活探是同一
   判据的三次手写。建议 `05_master_health_table.md` 的"实测基线"列由生成器从 `schtasks`+`--status` 派生
   （宪法 §9.5：静态清单必生成器产出），人只维护判据列。
3. **F122 归属互引的机械落点已存在**：`ct_pipe_routing.py:23-24` 已把边界写进代码注释。建议 ROOR/blueprint
   侧引这段为裁定注脚，**不必新开注册表条目**（净零铁律 §四.1）。
4. **exit-code 语义债一族合并**：D3（reaper exit 1）、D4（RegenCheck exit 3 与崩溃同码）、S6 报警疲劳是同一族
   "检出 vs 崩溃"分码欠账 → 单开一张 M3 工单族，别按件重复修。
5. **事件沿接线工单族扩面**：姊妹波 `00_overview.md:27` 提议把 FLE tick 沿（F84）与 order_daemon 胜者沿（F82）
   立族；本波 D6 再加两条同族——AutoRuntime TaskQueue 分派沿（F122）与备份 reconciler 锁沿。四同族一单，
   裁决点唯一（§9.3"探活任务"形态边界）。
6. **F81/F80 计数漂移回填**（姊妹波 `00_overview.md:26` 已登，本波再确认）：实测 49 / 98，总册 `:146/:145`
   仍写 38 / 96 → 属总筹侧回填义务，非新增证据；按宪法 §四.3 建议改为字段引用，杜绝第四次漂移。

## 六、自审闸三态

**册级三态＝挖干可施工**（五类补挖项均有当日实证；姊妹波四册的结构性结论未推翻，仅 2 处运行态由"绿"改"红"并给新判据）。
作业三态：F122 管线路由调度属性＝**挖干可施工**（其 (b) 运行态部分）＋**待裁**（归属细则与 Backlog 立单）；
①③④＝挖干可施工（附 D1-D7 小单）；②＝FBL 语义已闭合（预算帽类查无）。

**待裁案（5 条，均不自裁，交总筹/Owner）**：

| # | 问题 | 已试路径 | 选项 | 建议 |
|---|---|---|---|---|
| R1 | F122 管线路由归属细则：M0 已裁"M4/M5 互引"（`00_orchestration.md:35`），但互引的**判据**未定 | 实读 `ct_pipe_routing.py:23-24` 边界声明 + `blueprint_routing.yaml` 全属性 + orchestrator 挂点 | a 按本册 §3·5 二分：选读面（priority/scope/fallback）归 M4、分派面（触发/锁/抢占/重试/容量）归 M5，交叉轴＝`pipeline_roadmap.py` Dependency 表；b 整环节归 M5，M4 只作消费方登记；c 维持"互引"不落判据 | **a**（代码里已有同判据注释，零新增真源，合净零铁律） |
| R2 | 备份 verdict=failed + 9.1h 长跑 + 267014 僵尸疑影：是否授权施工班**重跑 `-Mode all -Force` 并加锁 TTL/看门狗** | 只读取 report/state/lock json；未触任何备份件 | a 授权备份班当夜重跑+看门狗；b 待 10-01 演练窗一并验；c 先只加观测位不重跑 | **c→a 序**（先 0.2 日观测位，再择非交易日窗重跑；备份流转涉生产数据面，Owner 门位候选） |
| R3 | reaper 任务每轮 exit 1 致水位台账 22h 失明：修 reaper 本体 or 先改台账判据（05 册 row 3） | 已定位"读缓存当活探"方法学漏洞；exit 1 真因未取证 | a 先改判据（<12min 且 LastTaskResult=0）立即可防误判；b 先取证 exit 1 根因再一并改；c 并入 S6 分码族一次做 | **a 立即 + c 跟进**（判据改是本车道小单，根因取证不阻塞） |
| R4 | `git_bundle` 把 3.67 天判 `reason='fresh'` 跳过（姊妹波 03 册堵点 3 的根因）：3-2-1 灾备是否接受 3.67 天 RPO | 读到 report 字段级证据，未改 config | a 阈值收紧（如 1 天）；b 维持并在册内写明"git 灾备 RPO≈4 天"为已接受风险；c 与 STAGE 3 working_vault 的 14 天 retention 联动判据 | **b 明示 + c 评估**（阈值改动落在 `backup_config.yaml` 属生产配置面，不自裁） |
| R5 | tilib 修复未接任务（编排册记 0041 落地、live action 仍旧 `.bat`）：是否认定"施工未完成/落地漂移"并回报 Owner | 三重证据（任务 action / `.bat` 全文 / 目录缺失）齐 | a 本车道登记为落地漂移并派重注册单；b 判为内容未落地需施工班返工；c 留晨报 | **a + c**（重注册=幂等 Set-ScheduledTask 惯例，非净删非资金，可派；但"落地漂移"结论要总筹向 Owner 交代） |

（另：姊妹波两册各附 1 内嵌待裁——FLE 触发沿形态（`01:39` 堵点 1 a/b）、order_daemon 拉起形态
（`05:43-46` W-B3 a/b）——本波无新增反证，**不重复列案**，由总筹与 R1/R3 的"事件沿"族合并裁。）

## 七、复核命令（Git Bash 可直接跑，约 8 分钟；全部只读）

```bash
# 0) 环境（RULE-ENV）
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version   # 期望 3.12.8

# 1) 水位台账新鲜度（D3 红证：看 last_run 是否今天且 <12min）
python -m zephyr.trading.process_reaper --status | tail -3
powershell -NoProfile -Command 'Get-ScheduledTask -TaskName "*Reap*" | %{ $i=$_|Get-ScheduledTaskInfo; "{0} LAST={1} R={2}" -f $_.TaskName,$i.LastRunTime,$i.LastTaskResult }'
grep -cE "ALERT-SYS-00[1-5]" config/alert_rules.yaml        # 期望 5
grep -oE "THD-[A-Z0-9]+-[0-9]+" docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml | sort -u | wc -l   # 期望 49
grep -nE "total_entities|generated_at" config/resource_profile_registry.yaml | head -2   # 期望 98 / 2026-09-24T21:21:27Z

# 2) 备份链 verdict（BOM 规避读法 = utf-8-sig）
python - <<'PY'
import json,pathlib
d=json.loads(pathlib.Path('data/databases/backup_state.json').read_text(encoding='utf-8'))
print({k:d[k] for k in d if 'last_backup' in k or 'last_ch_backup_status' in k})
r=json.loads(pathlib.Path('logs/backup_report_20260925_060007.json').read_text(encoding='utf-8-sig'))
print('duration_s',r['duration_seconds'],'| git_bundle',r['git_bundle'],'| code_backup.failures',r['code_backup']['failures'])
PY
ls G:/backup/working_vault | tail -3 ; ls G:/zephyr_cold/60_mirror/zephyr_cold_main | head -3   # 副本2/3 在盘
powershell -NoProfile -Command '(Get-ScheduledTask -TaskName "ZephyrAlpha-DailyBackup"|Get-ScheduledTaskInfo).LastTaskResult'   # 期望 267014（=僵尸/未收束）

# 3) 三地雷
git log --oneline -3 -- scripts/register_post_settlement_task.ps1   # 顶部须为 a0446129e3（回退逆转）
grep -n "conhost\|cmdExe" scripts/register_post_settlement_task.ps1 | head -4      # 好形态
cat scripts/data/backfill_night.bat                                                 # 仍指 .runtime\tmp\tilib-probe
ls ".runtime/tmp/tilib-probe" 2>&1                                                  # No such file（红证）
tail -4 .runtime/logs/sim_bridge_execute.log                                        # 09-23 exit0 → 09-25 SKIP
python -c "import datetime;from zephyr.data.trading_calendar import is_trading_day as f;print([(str(d),d.strftime('%a'),f(d)) for d in [datetime.date(2026,9,24),datetime.date(2026,9,25)]])"

# 4) 管线路由调度属性（§3·5）
sed -n '26,32p;813,817p;824,828p' config/blueprint_routing.yaml                     # priority/scope/fallback/agent_hints
grep -n "blueprint_routing" src/zephyr/infrastructure/pipeline/ct_pipe_routing.py | head -4    # M4/M5 边界声明 :23-24
sed -n '495,560p' src/zephyr/infrastructure/pipeline/pipeline_roadmap.py | grep -n "Backlog" # 四条 Backlog
sed -n '1096,1118p' src/zephyr/trading/auto_runtime_core.py                         # TaskQueue 300s 轮询=唯一触发沿
powershell -NoProfile -Command 'Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "zephyr.trading" -and $_.Name -match "python" } | %{ $_.CommandLine }'   # 本波两次实测：23:4x 见 1 行 pythonw process_reaper.py（PID 36404），23:47 复跑=0 行（reaper 是 one-shot 非常驻）；**关键判据＝行集里永无 `-m zephyr.trading`/auto_runtime_core ⇒ AutoRuntime Core 缺位=D6**
```
