---
ttl: task_bound
owner: st-maint3-20261011
campaign: 维护三班（令 3：T7 落地＋池面根因＋config 落账）
---

# 维护三班施工账 · st-maint3-20261011

> 接令＝总统统筹 2026-10-11 夜令 3。前任=维护二班 st-maint2-20261011（会话已死，三袋全落 HEAD
> `e9534bf202`/`c869c0a3b5`/`01513460c2`＋收口袋 `94aeb152cc`；候件随 `20_handoff_to_maint3.md` 转移）。

## 〇、工区声明：降级直改主区（显式申请制登记，根宪法 §1 RULE-WORKTREE / 并行协调政策 §10）

本班不在 `.aidrafts` 车道内施工，直改主区，原因三条（全部实测）：

1. 令 3 项 1 的**施工对象本身就是主区那枚未提交文件**——`config/resource_profile_registry.yaml`
   盘上躺着 10-10 08:21 的 103 实体新生代（存证 sha256 前 16 位 `398e0abe2c6151a9`，已双抄
   `.runtime/tmp/maint3_shift/registry_disk_103entity_20261010T0821Z.yaml`）。生成器的合并保全
   以"磁盘现档"为输入，车道里那份是 HEAD 的 102 实体旧代，**在车道重生成＝换一份新生代**，
   不是"落账"。
2. 靶件除该册外全部干净（逐件 `git status --porcelain` 实测：生成器/两枚 ps1/两枚测试/
   `apply_resource_plan.py` 皆零脏），不存在"要避开他人未落地改动"的写盘冲突面。
3. 主区 10-11 夜池面回退弹刚由前任总统筹按 HEAD 复位完毕并归档存证；此时另起车道再 merge
   回主区，正撞在册候件「池面回退方向无闸」的未闸面。

并发纪律：9 枚靶件已于 22:5x 全部 `lock_files.py acquire-batch` 到本 sid（TTL 240min）；
矿考班在飞件（`scripts/backtest/factory_grid_executor.py` 及其测试）**零触碰**；
`config/resource_profile_registry.yaml` 只经令 1/令 2 两步（生成器再生 + 排班真源写回）改写，
其余零改；宪法/热册走 `safe_write_text`/账本正门，禁裸写。

落地通道：`scripts/git_commit.py --session st-maint3-20261011 --files <清单>`（锁忙自动入队）；
主区 index 是多会话混合池（在册实测），故**只报自家文件名清单**，绝不 `git add -A`。

## 一、项 1 结论：orphaned_source 告警族＝**伪告警**，根因＝生成器 ps1 采集面瞎

### 1.1 现象

盘上新生代（`generated_at: 2026-10-10T08:21:26Z`，`total_entities: 103`）把 **34 枚**实体标成
`status: orphaned_source`＋notes_zh 追加"[生成器] 真源消失，待 Owner 裁定删除"，而 HEAD 那代
（`2026-10-02T11:24:03Z`，102 实体）里它们是 `active`。

### 1.2 真伪判据（三条独立实测）

| # | 判据 | 实测 |
|---|------|------|
| 1 | 34 枚孤儿的 `schedule_truth_source` 指向的文件在不在 | **全部存在**（`os.path.exists` 逐条真，34/34） |
| 2 | 伪孤儿的分布有没有规律 | 33 枚真源在 `scripts/tasks/register/`；唯一 1 枚例外 `ops_bdpan_tick_watch` 是**在册真孤儿**（OS 任务 2026-09-24 删除、别名撤销，见生成器 `OPS_TASK_ALIASES` 注释）；而同批新生代里从**顶层** `scripts/` 抽到的 `sch_commit_perf_report` 作为新实体 `active` 进表 |
| 3 | 生成器实际扫到几枚 ps1 实体 | `gen.parse_ps1_entities()` 实跑＝**只有 2 枚**：`{'sch_commit_perf_report', 'sch_process_reaper'}` |

判据 3 同时被**在册测试**独立证实（本班未新增任何判据即已红）：
`tests/meta/scripts/test_generate_resource_profile_registry.py::test_parse_ps1_entities_covers_all_task_names`
现红，报 `assert 'sch_factory_lane_c' in {'sch_commit_perf_report', 'sch_process_reaper'}`。

### 1.3 根因

`generate_resource_profile_registry.py:266` `PS1_GLOB = "register_*.ps1"` ＋
`:1080` `(REPO_ROOT / "scripts").glob(PS1_GLOB)` 是**单目录非递归** glob。
`a4b503a1630`（2026-10-02 20:11，scripts 拆簇第一波）把 `register_*×32` 搬进
`scripts/tasks/register/`，commit 正文自称"生成器 glob 双目录五处"，但：

- `git log --since=2026-10-01 -- .../generate_resource_profile_registry.py` = **空**（该生成器自 10-01
  起零改动）；`git log -S PS1_GLOB` 只有初立那笔 `aa253167d92`。
- 那笔拆簇对**本册**做的事是文本级改写 `schedule_truth_source` 字符串（diff 可见 32 行 `+ ... scripts/tasks/register/...`），
  即"册看着对、再生必崩"——采集面从未跟上搬家，路径字符串却被单独改对了。

⇒ 结论：**告警族为伪**，"待 Owner 裁定删除"是生成器自己瞎造成的假陈述。若按盘上新生代直接落账
（正门落账字面执行），就是把 33 枚在册活班次的"真源消失"写进 tier0 总册并推进 Owner 待删队列——
属编造账面，不落。

### 1.4 派生缺陷（同一病灶的下游，一并治）

| 编号 | 缺陷 | 凭据 |
|------|------|------|
| D2 | **孤儿标不可逆**：`merge_preserve:1914` 按 `_HUMAN_FIELDS`（含 `status`）用磁盘值覆盖派生值，真源回来后磁盘上的 `orphaned_source` 会被当作"人复核值"永久保全 ⇒ 一次坏再生永久毒化整册，无自愈路径 | 读码 `:1887-1916`；`pool_vocabulary` 幽灵池为此已开唯一例外（`:1921`），status 无对应例外 |
| D3 | **孤儿注记不幂等**：`:1938` 每次再生无条件 `notes_zh += "；[生成器] 真源消失..."`，同一实体被追加 5–6 次 | HEAD `ops_bdpan_tick_watch` 该串出现 5 次、盘上 6 次（diff 实测）；同件 C-11 标注早已有"哨兵幂等剥离"先例（`:1728-1730`） |

### 1.5 修法（本班裁：三项同批，medium 域 AI 代裁）

D1 采集面双目录（`PS1_REL_DIRS = ("scripts", "scripts/tasks/register")`，缺目录=跳过并告警，不静默）；
D2 真源回来即销孤儿标（**只撤本生成器自己打的标**，人写的 notes_zh 正文逐字节不动）；
D3 注记先剥后贴（哨兵幂等，全仓同族写法对齐）。
守卫：在册 `test_parse_ps1_entities_covers_all_task_names` 由红转绿即 D1 的正证；
新增 D2/D3 结构测（红证＝打在未修判据上必红）。

## 二、项 2 T7 落地＋项 3 测试重钉（总统统筹裁定，medium 域 AI 代裁，adjudicator=st-maint3-20261011）

### 2.1 落地前置：单口的两处自身缺陷（不修就落不了）

| # | 缺陷 | 实测凭据 | 处置 |
|---|------|---------|------|
| D1-b | `apply_resource_plan.py:1232` 自持一份 `(root/"scripts").glob("register_*.ps1")` **克隆采集面**，沙箱只收到顶层 2 枚 ps1 ⇒ 沙箱再生对着缺真源的表跑闸 | 修前 dry-run 定位不到 `sch_sim_bridge_execute`；修后 `--map` 全表命中 | 改调生成器新单口 `ps1_paths_for(root)`，并保留 `tmp` 副本根可注入（自检零生产写不破） |
| D4 | 单口**读得出多腿窗却写不回去**：同任务两枚 `-Daily -At`（sim_bridge 09:35+13:05，表内 `35 9 * * *|5 13 * * *`）一律拒"须人工拆方案"；`new_window_cron` 带 `\|` 又判段数非法 ⇒ 令 3 指定的"只挪其中一腿"无任何合法通道 | `REFUSE[build_patches]: ZephyrAlpha_SimBridgeExecute: 命中 2 条触发器构造行且无法唯一判定目标` | **加前置不拆闸**：仅 `new_times` 全量清单＋腿数与清单等长（不等长＝静默砍班/加班，双向拒）＋逐腿只换 `-At` 时刻字面量（引号在 group 内侧，再拼一层会写毒行——本班首版当场被"改后重抽为空"抓住）＋配对按**现时刻升序对齐新时刻升序**（不按行序，防腿序不同步挪错腿）＋改后仍走生成器重抽复验 |

守卫：`tests/meta/scripts/test_apply_resource_plan.py` 新增 3 支（单腿挪动+腿序翻转+双引号毒行反证／不等长与同刻拒／单点改写仍拒）。红证：HEAD 版 `patch_ps1_trigger` 对同一方案直接拒（上面那条 REFUSE 报文即基线实况）。

### 2.2 落地读数（全部进程外可核）

- 方案件=`20_t7_plan.yaml`，通道=`apply_resource_plan.py --apply --session st-maint3-20261011`，`verdict=pass`，
  `report_sha256=9b4a1ba6ea57d5f4`，旧值全量存档=`.runtime/sessions/st-maint3-20261011/archive/plan_20261011T151409Z/`
  （`orig/` 含两枚 ps1＋注册表＋周历视图四件旧像）。
- 真源：`register_sim_bridge_execute_task.ps1:47` `09:35→09:45`（`:48` 的 `13:05` 腿未动）、
  `register_decision_chain_sentinel_task.ps1:69` `09:40→09:50`；两文件 `git diff --numstat`=5/5 与 7/7，
  行数守恒（60/90 不变）。
- 表：`window_expr` 见新值，`generated_at: 2026-10-11T15:14:11Z`，`total_entities: 103`，
  `mem_ceiling_gb: 10.0` 未动（表头第 16 行仍 `lines[15]`）。
- 闸门逐臂对账（同一把尺打存档旧代 vs 落后面，实测）：
  `sched_mem_ceiling` block **3→1**（消解 09:35/10.5GB 与 09:40/11.0GB 两条；余 1 条=10-13 05:50 既存非本令对象）、
  `overlap`=0→0、`e0_trading`=0→0、`sched_pool_concurrency(C-8)`=1→1（10-12 15:10 既存）。
- ps1 内 5＋6 处时刻陈述（含 OS 可见 `-Description` 串）随批对齐——写回工具按"未命中字节零改动"硬线
  只改触发行，留下同文件注释说谎＝本班制造的矛盾，故当班修；`isascii()` 断言随测钉住（根宪法 §9.7）。

### 2.3 项 3：`test_resource_schedule_mem_ceiling_invariant.py` 重钉（5 failed → 11 passed）

进场 5 红的**真因不是排班变化**，而是 §一 的伪孤儿态：`status=orphaned_source` 的实体被排除出
`_budget_rows` 求和，于是 09:35 读成 9.0（应 10.5）、09:40 读不成红、`sch_ollama_serve` 干脆不进预算表
（`:366` 那条"常驻体占窗档账"实为"实体整个消失"）。D1＋落账修复后 3 红自愈，剩 3 支按新现场重钉：

| 支 | 处置 | 依据 |
|---|---|---|
| `test_production_registry_currently_carries_the_old_values` | 改写为 `…_now_carries_the_staggered_values`（表带新值＋带内 block=0＋**把两腿拍回旧值必须立刻重新报 2 红**的反空跑桩） | 该桩本体原文即"本测试须随属主落地同步改写"，本班即属主 |
| `test_same_pool_caliber_is_already_green_in_the_band` | `default 7.0→6.0`（realtime 4.0 未动） | 来历=错峰本身：旧 09:40 default 峰含 `sector_pre_open`(09:15+30min)＋两腿=7.0；两腿挪到 09:45/09:50 时 pre_open 已结束，default 峰落回纯基线 6.0（逐刻活跃集实测见案） |
| `test_registry_yaml_bytes_untouched_by_this_shift` | 改写为 `test_t7_landed_bytes_pinned_in_table_and_truth_sources`（三面钉＋"13:05 腿未被牵连"＋ps1 纯 ASCII） | 原桩=维护二班"本班零改动"守卫，T7 授权写回后前提被有意取代 |

同族回归面：`test_generate_resource_profile_registry.py` 40 passed、`test_apply_resource_plan.py` 34 passed、
`test_resource_schedule_regen_check.py` 37 passed、五文件合跑 155 passed；
`test_resource_scheduler.py` 单跑 24 passed（合跑那次 ERROR 是 `#ARCH-084` 把**并发写者**在 23:26:04 写生产热册
记到当时在跑的测名下——单跑该测前后 mtime/sha 逐字节同＝非本班测所写，此条同时是项 4 案卷"会话零动作也有写者"的活体复现）。

### 2.4 同批追认的三支陈旧钉值（全部先证明 HEAD 基线本就红，非本班改出）

| 支 | 旧钉值→新 | HEAD 基线红证 |
|---|---|---|
| `test_generate_…::test_parse_ps1_entities_covers_all_task_names` | `len==26→35` | 报 `'sch_factory_lane_c' in {'sch_commit_perf_report','sch_process_reaper'}`（§一 D1） |
| `test_generate_…::test_parse_schedule_slots_…` | `len==26→32` | `assert 32 == 26`；判据不是跟现值：`schedule.yaml['schedules']` 键数=32、parse=32、与 HEAD 册内 `data_slot_*` **集合差=0** |
| `test_apply_resource_plan.py` 两支 f06 路径 | `scripts/register_f06_grid_task.ps1`→`scripts/tasks/register/…` | 沙箱拷回 HEAD 那份"只收顶层"的面实测：`未知 task_id 'sch_f06_grid'` rc=2（连 `files_touched` 都拿不到） |
| `test_resource_schedule_regen_check.py` 两支 | ps1 路径搬家追认；豁免集改为"点名集合 ∩ OS 实测仍在" | HEAD 基线复跑实测 2 failed（临时换回 HEAD 字节跑完即按 sha 复原本班码）；`C4Exam_OneShot0915`/`FactoryLaneC_OneShot0915` 实测已不在本机任务表 |

## 三、项 4 池面回退根因（案卷=`30_pool_rollback_rootcause_casefile.md`，203 行 8 节，29【实测】/6【推断】/5【查无】）

结论提要（总包独立复核过引用可 grep 性：`scripts/commit_queue.py:2967` 定义＋`:3191` 唯一调用点、
`:2984` "实测 26 件里误报 17 件" 原话、`scripts/governance/commit_queue_landing.py:2527`/`:2743-2746`
写盘点、§② 六个 `file:line` 锚点全部文件存在且行号在界内）：

1. **头号嫌疑的字面版被证伪**：事件窗（20:36:01→21:57:12）队列零活动（`pool_wave.log` 非 `claim_none` 行=0、
   pending/processing/dead 新基=空、dev reflog 81 分钟无推进、`main_workspace_sync.jsonl` 窗内 0 条）。
   ⇒ 不是"队列落地后的主区池面同步"这一条直路。
2. **形态版被加强**：窗内唯一命中主区池面的在册写者=hygiene_reconciler→`git_batcher.git_restore_batch`
   （20:45:33，作用域仅 2 个 `data/**/latest.json`，还原目标=HEAD，解释不了退旧字节）；
   替代嫌疑=**per-path 陈旧车道面被物化进主区池并顺带 staged**（受害 3 件正是 20:36:01 那袋 payload、
   第二击 4 件正是 22:25:45 那袋 payload）＋不留 reflog 的 `checkout <old> -- paths`/`restore --source` 旁路。
3. **字节形态=逐件拍到"该件自己的旧版本"**，非整树：DISK 与 INDEX 双面 sha 逐位相同（排除两基线分裂）；
   四件盘旧字节分别等于 09-16／10-03／10-10T09:53／10-10T21:26 **四笔不同**提交；
   决定性反例 `test_session_concurrency.py` 盘旧 sha `3fd5c015` 既非 HEAD 也非该袋 `base_head`。
   行集量化 `only_in_head`=33/375/11/42、`only_in_disk`=2/33/**0**/3。
4. **指针面清白**：六笔受害提交全是 HEAD/dev 祖先，全天 dev 单调前进，无 reset/stash。
5. **gate 提案 `GATE-POOL-REGRESSION-DIRECTION`**（提案非裁定，待 Owner/统筹）：三层——
   写者层（`:2527`/`:2743-2746` 写入前方向判据，不依赖 git 故旁路同尺覆盖）＋池面快照层
   （`worktree_drift_watchdog` 已有 60s 心跳且 20:40:05 实测目击 531 drifted，缺的只是方向分量；
   同尺必须装在 B5 `git add` **之前**）＋提交前 own-scope 层；判据必须**三方**口径
   （两方尺在册已自证 26 件误报 17 件＝闸废）；门位=**AI 可放**，仅"规则册例外白名单"与
   "硬阻断主区历史写"两格归 Owner。可复用零件缺口三条：仅 requeue 侧接线、不读池面 work/index 字节、
   `base_ref` 缺省硬编码 `"dev"` 在车道内会拿错基底。

## 四、项 5 知会＋残余与待裁（呈批面）

项 5 已办＝`40_notice_gpu_requeue_2026-10-11.md`（SCHED-NOTICE-20261011-T7）。GPU 袋
`q-20261011-st-gpux-20261011-0010` 的 `dead_reason` 原文两条阻断（09:35/10.5GB、09:40/11.0GB）
与本班消解的两条逐字对上；本班**不代投**（属主道/Owner 面）。

待裁与移交（本班不擅动）：

| # | 项 | 实测凭据 | 门位 |
|---|---|---|---|
| R1 | **OS 任务未重注册⇒错峰在运行态尚未生效**：ps1 与表已是 09:45/09:50，但 `ZephyrAlpha_SimBridgeExecute`/`DecisionChainSentinel` 的在册触发仍是旧时刻，须重跑两枚注册器（`Register/Set-ScheduledTask -Force`）才对操作系统生效 | 两任务实测 `Ready`（`query_schtasks`），Action/Trigger 未重放 | 改活任务=在册"禁改活任务"纪律面，请统筹/Owner 定点（可回退：再跑一次注册器即回旧时刻，ps1 已含新时刻） |
| R2 | 4 枚**纸面排班**：注册表 active 但 OS 查无（`AIL1Scan`/`BudgetReport`/`ModelExam`/`ModelIntelScan`）；另 `F06Grid` 在册 active 而 OS 实测 `Disabled` | `--check` 健康码 5 条，逐条 `query_schtasks` 复核为真 | 注册/启用=改活任务，Owner 或属主车道 |
| R3 | 7 枚 OS 任务注册表不认识（含 `ZephyrAlpha_SectorEqwIntraday`：真源 `register_sector_eqw_task.ps1:16` 用 `$taskName='…'` 变量赋值＋`:24` `-TaskName $taskName`，生成器 `_RE_TASKNAME` 只认字面量；dash 命名族需 `OPS_TASK_ALIASES` 收编） | 实测 `SectorEqwIntraday`=Ready 而 claims 表无它 | 归资源排班车道（收编=改画像人口，非本班靶面） |
| R4 | 图13 生成册仍写 `交易日 09:35 与 13:05 两拍`（`generate_trading_day_cycle_map.py:450/:462`，锚点正是本班改的 `ps1:47`）；validator 实测 0 错 0 警＝它不核散文时刻，故不会自拦也不会自愈 | 校验器复跑 nodes=52 errors=0 | 移交图13/fig13 车道（禁本班代修他道生成器 spec） |
| R5 | 既存 2 条 block（10-13 05:50 内存天花板／10-12 15:10 同池跨组 2.5GB）——05:50 那条已由 §五 追加错峰清零；C-8 的 15:10 一条仍在，非本令对象 | §2.2 逐臂对账＋§五复测 | C-8 条归各自域 |
| R6 | 热册 `capability_canonical_file_registry.yaml` 工作区面 380 行未落地（PG render 投影，含他班登记）；本班 token 已入 PG（三口径尺：盘面 4／index 0／HEAD 0），CREATE-GUARD 走 PG 第三源正证放行 | 抽 3 条他班 token 在 render 后仍全部在场 | 归册主车道 render 袋，**本班绝不随袋提交他人未落地条目**（袋=整档快照＝归属篡改） |
| R7 | 主区 663 枚脏件（466 枚 `docs/03_modules/**/blueprint.md` 等机生面）归属非本班；本班提交清单严格白名单 14 件 | `git status --porcelain` 分类计数 | 各属主道 |
| R8 | `Welch 收编`＝维护二班【指针】项，本班在 `00_ledger.md` 与 dev 面 grep 均 0 命中，无出处不立项（在册纪律：禁为达标编造判据） | 二班交接包 §三同记 | 请统筹给原句 |
| R9 | ENV-001（torch 在册要求 `+cpu` vs 实测 `+cu126`）仍待处理——降级=花钱/环境类且撞 GPU 车道同机窗 | 二班 `18_env_debt_ledger.yaml` | Owner |

本班申报：零 CH、零 GPU、零生产数据写、零判据阈值/口径改动、零新 gate、零新裁定号（T7 沿用统筹裁定原文）、
零杀停进程；矿考班在飞件（`factory_grid_executor.py` 及其测试）零触碰；`config/resource_profile_registry.yaml`
仅经 §一（再生落账）＋§二（单口写回）两步改写，其余零改；热册经账本正门（`batch_creation_tokens` 意图 API），
未裸写。

## 五、Owner 批准追加：05:50 带最小错峰（超令 3 原文范围，经问答通道点头后执行）

**为什么必须追加**：本班袋 23:4x 走正门被 **RESOURCE-SCHEDULE 全量拦下**，拦点是一条**HEAD 既存**的
10-13 05:50 内存天花板冲突。门本体硬线实测：`resource_schedule_gate.py:795`（"预算类判据仍全量"）、
`:501`/`:24`（"内存预算永不豁免"）⇒ 无豁免旗、无 own-scope 通道；不清这条带，**任何**碰这张册的袋
（包括 T7 本身）都进不了 `dev`。把三选项呈 Owner（追加错峰清带／袋挂着等属主车道清／改门口径），
Owner 选**追加最小错峰**。

**带构成实测（六档=10.5GB > 10.0）**：`weekend_calibration` 4.0（`00 3 * * 2` 起 180min）+
`news_slow` 2.0（`17,47 * * * *` 常驻带）+ `pf_alloc_rebalance_check` 2.0（`45 5 * * 1-5`+30）+
`catchup_guard` 1.0（`30 5 * * *`+30）+ `sampler_writeback` 0.5（`40 5 * * *`+15）+
`view_publish` 1.0（`50 5 * * *`+15）。取向=**只挪最轻的一档、位移最小**：
`sch_resource_view_publish` 05:50→06:10（15min 轻档，挪后该刻和=5.0；05:50 刻=9.5）。
六档 `peak_mem_gb` 申报值一个都没改（改申报=改口径不是改排班，§2 已论）。

**落地凭据**：方案件=`21_clear0550_plan.yaml`（含批准来历与撤销通道）；
`apply_resource_plan.py --apply` → `verdict=pass`、`新增 block=0 基线既存 block=1 本方案消解=1`、
`report_sha256=cc3814a36d2debb5`、旧值存档=`plan_20261011T162521Z/`；
真源 `register_resource_view_publish_task.ps1:74` `+1/-1`；
独立复测（闸自己的三臂，三个评估瞬间）：**block=0**（10-11 23:30／10-12 00:00／10-12 12:00），
反证臂（把 view_publish 拍回 05:50）当场重新报 1 红 ⇒ 尺有牙；
全家测试 131 passed（六文件合跑）。

**同批追认两支**（都因这次追加或并发落地产生，非判据松动）：
①`test_resource_schedule_regen_check.py:185` 的 `view_publish` 窗档钉值 05:50→06:10——该桩本意是
"时间值来自真源且被物化"，不是钉死历史时刻，旧代字节在存档目录可逐字节复原；
②`test_generate_…::test_parse_ps1_entities_covers_all_task_names` 计数 35→36——
GPU 工单施工班 `a2c46fddca`（00:1x）落了 `scripts/tasks/register/register_sft_train_window_task.ps1`，
本班 00:25 的再生已正确含它（active/default/0.5GB/300min/`0 10 * * 0`）。

**顺带挖出三条，本班不动、只登记**：

| 编号 | 内容 | 实测凭据 |
|------|------|---------|
| R10 | **外来 staged 删除挂在共享 index**：`register_sft_train_window_task.ps1` 盘上存在且 HEAD 有（`a2c46fddca` 所加），而 `git ls-files -s` 对该路径**空**＝index 里是一条 staged 删除。任何"整 index"提交会把它删掉。非本班所为，本班提交清单不含该件 | `git status --porcelain` 该行=`D `；`git cat-file -e HEAD:<路径>`=YES；盘=YES |
| R11 | **`weekend_calibration` 名实不符**：`schedule.yaml:144` cron `"00 3 * * 1"`＋同槽注释/description 都自称"周一03:00"，但 APScheduler 口径 `1`=**周二**（`0`=周一），生成器如实归一成 `00 3 * * 2`⇒ 2026-09-23 `st-emomine-20260923` 那笔"周日改周一"的 S1 根因修复实际落在了周二，比意图晚一天 | 直读 `schedule.yaml:143-150` 与册内 `window_expr` |
| R12 | **单口的 `pre_existing` 账有一次报 0**：05:50 候选件 23:5x dry-run 报"基线既存 block=0 消解=0"，而同一 registry 我用闸本体函数在三个 `now` 下都测到该 block；00:2x 再跑同一件报"既存=1 消解=1"。⇒ 该计数**随评估瞬间变**（`pin_eval_now` 按 UTC 日取整＋`weekend_calibration` 的 dow 在 UTC/本地跨日错位，见 R11），"新增=0"结论不可只凭工具自报，须像本班这样独立复测。工具设计意图（确定性三条）本身在册且未改 | 两次 dry-run 报文对照＋§五独立复测 |

## 六、结工单（本班交付终态）

**落地**：`dbc86560e3`（16 件；`git show --name-only` 与本班清单**集合差=0**，零他人面被扫入）。
验收判据逐条在 **HEAD 面**复跑（非盘面自证）：

| 判据 | 实测 |
|---|---|
| HEAD 册内见错峰后 window_expr | `45 9 * * *\|5 13 * * *`=1、`50 9 * * *`=1、`10 6 * * *`=1 |
| HEAD 册内见落账后 generated_at | `2026-10-11T16:25…`（UTC）=1；`total_entities: 104`=1 |
| 伪孤儿族已销 | `orphaned_source: sch_`=**0**；真孤儿 `ops_bdpan_tick_watch`=1（保留，删除属 Owner 门位） |
| 上限未动 | `mem_ceiling_gb: 10.0`=1（表头/生成器常量/reaper 三面同钉） |
| HEAD 面真源时刻 | 两枚 ps1：`-At "09:45"`＋`-At "13:05"`（未被牵连腿）＋`-At "09:50"` |
| `test_resource_schedule_mem_ceiling_invariant.py` | **11 passed**（进场 5 failed） |
| 根因报告入册 | `30_pool_rollback_rootcause_casefile.md` 在 `dbc86560e3` 内，含 gate 提案 |

**三次拦点三次对症（无一靠拆旗）**：① RESOURCE-SCHEDULE 全量拦既存 05:50 → Owner 批准追加清带（§五）；
② TAKEOVER-PENDING 把**本班自己**判成死会话（`pid=37924 dead`＋idle 仅 122s，未达 7200s 阈值——
起因是注册由首个短命工具进程带上了自己的实 pid，并非真死）→ 按在册处方处置：`list_active`（与守卫**同源**判据）
确证活体 → `pid=0` 复注册 → `session_worktree._spawn_heartbeat_daemon` 起守护（心跳末态 `started`；
本班先前手拼 `python -m` 那条**根本没起来**＝目录里连 heartbeat.jsonl 都没有，属"降级态看起来像没触发"）→
`register_heartbeat_keepalive` 3600s → `session_takeover_ledger.py --resolve` 属主自解（open 余量 0）→
复投带 `--adopt-prior-work` 通过。**防再犯配方**：长班起袋前先把 sid 注册成 `pid=0`，别让首个工具进程留实 pid。
③ 其余"外来 staged 未检查"皆 warn+审计不阻断（点名 104-106 枚无主外来件，含 `module_translation_registry.yaml`
与 `register_sft_train_window_task.ps1` 的 staged 删除＝§四 R10 在册）。

**项 5 交付**：知会件 `40_notice_gpu_requeue_2026-10-11.md` 已随 `dbc86560e3` 入库；本班**未代投** GPU 袋。

**待 Owner/统筹回话三件（本班不擅动）**：R1（OS 计划任务重注册＝改活任务；09:45/09:50/06:10 三处**运行态尚未生效**，
可回退命令在 §二/§五）、R10（外来 staged 删除的归属处置）、R11（`weekend_calibration` 名实差一天）。

**R13（终检时抓到的活体复现，补记）**：四文件合跑时
`test_resource_schedule_regen_check.py::test_main_view_freshness_only_for_production_registry`
报 teardown ERROR，`#ARCH-084` 把"生产热册 `capability_canonical_file_registry.yaml` 被写"
记到 `test_generate_…::test_full_registry_build_and_drift_check` 名下。**先查再判"是不是我改的"，
结论＝非本班**，三证：①同一组合第一轮 122 passed 零 ERROR（不可复现＝非代码性质）；②该支单跑 passed；
③写审计尾部三条命中该册：**00:50:18 pid=50640、00:51:00 pid=42252、00:51:43 pid=16932
——三个不同 pid、`session` 全为空串，85 秒内连写三次**，而本班那一轮只有一个 pytest 进程。
⇒ 这正是项 4 案卷 §⑥ 点名的缺陷面（写者 `session_id=""`，`os.environ.get("ZEPHYR_SESSION_ID","")`
未置位）＋§③"会话零动作时也有在册写手改写共享面"的**第二次独立复现**（前一次＝23:26:04 那次，
当时用"单跑该测 mtime/sha 前后逐字节同"排除）。含义：**方向闸若不带"写者必须填 sid"这一条，
这类写入永远归不到人**（根宪法 §3.4 owner 责任制落空）——案卷 §⑥ 已把该要求写进提案，本班不放宽判据。
本班交付面不受影响：16 件在 `dbc86560e3`、结工单段在 `40a48dbbe0`，四文件合跑读数 122 passed。

