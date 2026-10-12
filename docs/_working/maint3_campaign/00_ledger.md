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

## 七、统筹批复执行账（双令齐发 2026-10-12 01:0x）

### 7.1 批令一·重跑注册（已完成，时间敏感项，09:35 前必办）

**动手前预检（不做就把好任务改成必然炸的坏任务）**：三枚注册器的 `$RepoRoot` 全是硬编码
`"D:\ZephyrAlpha"`（非 `PSScriptRoot` 上溯）⇒ **不携带**拆簇遗留病（cc056bf 修过同簇 `register_sector_eqw_task.ps1`
"少一层"那类）；且三枚各自 `Test-Path` 把关引用目标——实测三目标全在场：
`scripts/run_sim_bridge_execute_daily.ps1`、`scripts/governance/decision_chain_sentinel.py`、
`scripts/governance/generators/generate_resource_week_view.py`。三枚 ps1 `isascii()` 全 True（根宪法 §9.7）。

**注册前基线快照**（进程外 `Get-ScheduledTask` 实测，证明确实是"在册未生效"）：

| 任务 | 注册前 NextRun | 注册前 StartBoundary |
|---|---|---|
| `ZephyrAlpha_SimBridgeExecute` | 10-12 **09:35** | `09:35` + `13:05` 两腿 |
| `ZephyrAlpha_DecisionChainSentinel` | 10-12 **09:40** | `09:40` |
| `ZephyrAlpha_ResourceViewPublish` | 10-12 **05:50** | `05:50` |

**执行**：逐枚 `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/<枚>.ps1`
（首试因 bash 把 `\\$f` 吞成字面量而**根本没执行**——零半态，改正斜杠后三枚全 `Updated existing task in place`）。

**注册后复验**（进程外读回，含 Action 未被牵连）：

| 任务 | 复验 State | 复验 NextRun | Action/Arguments |
|---|---|---|---|
| `ZephyrAlpha_SimBridgeExecute` | Ready | **10-12 09:45** | `powershell.exe … -File "D:\ZephyrAlpha\scripts\run_sim_bridge_execute_daily.ps1"`；两腿 StartBoundary=`09:45`＋`13:05`（13:05 未被牵连） |
| `ZephyrAlpha_DecisionChainSentinel` | Ready | **10-12 09:50** | `pythonw.exe "…decision_chain_sentinel.py"`（脚本自检同读数） |
| `ZephyrAlpha_ResourceViewPublish` | Ready | **10-12 06:10** | `pythonw.exe "…generate_resource_week_view.py" --publish-alerts` |

**在册铁律复跑**：`generate_resource_profile_registry.py --check` ⇒ **"注册表无漂移（104 实体）"**；
把 T7 原方案再喂一次单口 ⇒ 两枚均 **`noop: true`／verdict=pass**（＝真源已在目标值，工具自证幂等，不是"我以为改了"）。

**回退命令（成对留档，本班未执行）**：

```bash
# 1) 真源与表回退（逐字节还原到本次写回前）
python scripts/governance/apply_resource_plan.py --rollback \
  .runtime/sessions/st-maint3-20261011/archive/plan_20261011T151409Z   # T7 两腿
python scripts/governance/apply_resource_plan.py --rollback \
  .runtime/sessions/st-maint3-20261011/archive/plan_20261011T162521Z   # 05:50 带
# 2) OS 侧回退：重跑三枚注册器即可（注册器读的是 ps1 里的时刻，回退真源后重跑就回到 09:35/09:40/05:50）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_sim_bridge_execute_task.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_decision_chain_sentinel_task.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/tasks/register/register_resource_view_publish_task.ps1
# 3) 复验（三条读数应回到旧时刻）
powershell -NoProfile -Command "foreach ($n in 'ZephyrAlpha_SimBridgeExecute','ZephyrAlpha_DecisionChainSentinel','ZephyrAlpha_ResourceViewPublish') { (Get-ScheduledTask -TaskName $n | Get-ScheduledTaskInfo).NextRunTime }"
```

### 7.2 批令三·热册待登记面（量测并登记，本班不代落）

`capability_canonical_file_registry.yaml` 工作区面 vs HEAD 实测（**键集合差尺，不肉眼**）：

| 量 | 读数 |
|---|---|
| 行差 | **+1190 / −0**（统筹给的 +1135 是更早一刻，此后又被别班 render 追加） |
| `creation_tokens` 条目 | HEAD=14513 → 盘面=14751＝**净增 238 条** |
| 净减（＝他人面被抹） | **0**（PG-wins render 未吞任何条目；顶层键集合差亦 0） |
| 净增归属（`created_by` 分布） | `st-deadcure3b-chief-20261011` **140**／`st-mineloop-20261010` 39／`st-maint2-20261011` 16／`st-gpuwo-20261011` 13／`st-fclean3-20261012` 10／`st-maint3-20261011`（本班）**5**／其余 15 枚零散 |

本班立场与理由：这 238 条**不是本班的账**——一袋=整档快照，随袋提交即把五个会话的登记挂到本班 `[GW:]` 名下
＝归属篡改（Owner 10-10 已明令禁出"重打投影袋"，在册另两次实证连坐）。本班只做到两件：
①本班自建的 5 枚新件 token **已进 PG 真源**（三口径尺：盘面 5／index 0／HEAD 0，CREATE-GUARD 走 PG 第三源放行，
本班两袋均因此能落地）；②把待落地面**量化到条目级**交统筹，供册主车道出一只**聚合袋**（归属写清"投影重放、
非本会话登记"）或由各属主自投。

## 八、批令二施工账·池面回退方向闸三层（全部带红证）

### 8.1 三层落点与实测

| 层 | 落点（本班实改） | 判据 | 出口 |
|---|---|---|---|
| **L1 写者层** | `commit_queue_landing.py` `_converge_one`（主区工作树**唯一字节写口**，三个上游全汇于 `_converge_main_workspace` 单点调用） | 写入/删除前调 `cq._snapshot_head_regressions(root, [(rel,data)], base_ref=<主区 HEAD>, item_base_head=<本件基底>)`——**尺体零克隆**；命中返 `skipped_head_regression` | 单件剥除（外层逐件 fail-open，**不连坐整袋**）＋`main_workspace_sync.jsonl` 记 `pool_regression_blocked/acked`，含 `head_only_lines`/`base_compared`/`sid`/`sid_missing` |
| **L2 池面快照层** | `worktree_drift_watchdog.py` `scan_once`（在册 60s 全量＋10s 热件；已实测 20:40:05 目击 531 drifted 却全程无声） | 仅当 `wh≠hb` 时读字节做行集差（控住量级）；`regression_strict`＝`head_only≥1 且 work_only==0`；`regression_near`＝`head_only≥20 且比值≤0.05` | `summary["pool_regressions"]` 无条件普查（新键恒在）；逐件方向读数**并进既有"未登记写者"那条已去重报文**（`alerted` 签名 dedupe 生效），另加**每轮一条**批量汇总（含未署名件数）；快照沿用在册 `known_quarantine` 面 |
| **L3 提交层（入队正门）** | `enqueue_preflight.py` 新增 `pool_regression_preclean`，挂在 `run_enqueue_preflight` 的 ruff 之后 | 同一把三方尺，`base_ref="dev"`、`item_base_head=<提交者本地 HEAD>` ⇒ 主区提交恒不命中（HEAD==dev），只拦**车道基底落后 dev 的整档重放** | 处方→上游 `QueueReject`（在册"被拦件连 pending 都不进"通道）；处方首条正路＝`git checkout dev -- <件>` 重基（**改喂闸的输入指向**，非弱化判据）；env `ZEPHYR_ENQUEUE_POOL_REGRESSION=0` 一键回退；设施故障 degraded 放行**但必记日志** |

阈值不拍脑袋：本班对 `.runtime/tmp/pool_rollbackbomb_20261011/code_drift/` 里 **28 件受害旧字节**逐件重算
`HEAD vs 盘` 行集差＝严格子集 5 件（含 `head_only=6/9` 的小件，故严格臂不设最小值）；近子集比
0.012/0.019/0.037/0.04/0.045…0.167 拖尾（故近臂取 ≤0.05 且 `head_only≥20`，且只升级不阻断）。

### 8.2 红证与回归（每层先证明能红，防幽灵闸）

| 面 | 修后 | HEAD 基线（受控换文件跑完即按 sha 复原，已核一致） |
|---|---|---|
| L1 新测 5 支（拦下／ack 越过仍量／合法快进不假红／删除臂含反证臂／出口普查与署名） | 5 passed | **5 failed** |
| L2 新测 3 支（读数三态／探针降级显影 unknown／scan_once 普查＋告警带署名） | 3 passed | **3 failed** |
| L3 新测 4 支（落后车道重放必拦／主区不假红／ack 与 env 两开关／无 git 环境 fail-open 不炸） | 4 passed | **4 failed** |
| 全族 | `test_enqueue_preflight`＋`test_worktree_drift_watchdog` **94 passed**；`test_commit_queue_landing` 68 passed | 该族 HEAD 基线即 **27 failed／63 passed**（同一批 27 支逐支同名，病因＝"注册表项基底不可知（拒绝猜基底）"族）⇒ 本班**零新增红**，68＝63＋本班 5 支 |
| ruff | `check` 全绿、`format` 六支 left unchanged（两支 `# noqa` 写法警告系存量） | — |

### 8.3 L3 为何先落入队正门而不新造 commit-gate

Owner 批准的是"三层"这个覆盖面而非某个 gate_id。新造 in-process commit-gate 必须**同批**改 7 处：
门本体＋`in_process_gate_registry.yaml` 条目**及其 `total_gates` 标量 106→107**＋`commit_gates/__init__.py`
ORPHAN-MODULE 静态 import＋`generate_gate_registry.py` 重生成（`own_scope` 靠门文件 import
`_split_own_foreign`/`_build_own_scope` 才被探测为 True）＋creation_token（须 `map_mounts` 真在册挂点或
`no_mount_reason`）＋`add_module_translation` 大白话简介＋自家测试。其中**标量漏改＝全册 107 台门集体装载失败**
（在册事故形态）、`map_mounts` 编造即硬拦。凌晨拿全册门装载去赌一次性大批登记性价比为负，故第三层
接进已确立的入队快败通道（同尺、可回退、零新资产），并把 commit-gate 形态完整装机清单（含 priority
安全空段 161-199，实测零占用；勿碰 830＝reconciler 专用）留予下一班一次做完。
**差口如实报**：绕过队列的直连 commit 不走 L3（L1/L2 仍在写者与池面两维兜，落地侧权威链不缺席）。

### 8.4 案卷订正（另起一节留旧案，不改历史判据）

`30_pool_rollback_rootcause_casefile.md` §⑥ 有一条被本班实测否掉：**"同尺须装在 B5 `git add` 之前"**——
`_auto_stage_candidates`（worktree_drift_watchdog.py:153）用 `git ls-files --others --exclude-standard --
docs/_working`，作用面＝**untracked 且仅此前缀**；untracked 在 HEAD 无字节，"盘是 HEAD 真子集"这条谓词
在它身上结构上不成立。B5 的真实风险是另一回事：它把未挂名写者造出的未跟踪件**固化进共享 index**
（本班案卷自己曾被 `AM` 化即活证），需要的是"只自动暂存有主 claim 的件／写入带 sid"，不是方向尺。
订正已随案卷 §⑨ 落盘（旧 §⑥ 原文不动）。


### 8.5 自查更正（同类缺陷当场修，不留到下班）

首版 L2 我另起了一条"逐件 critical_warn"循环——**绕过了既有 `alerted` 签名 dedupe**，
后果＝同一个未修好的回退件每 60s 再刷一条告警、且与既有"未登记写者"报文重复计数。
更正＝方向读数**并进那条已去重的报文**，本层只另加"每轮一条"批量汇总（含未署名件数）；
测试同步改为断言"逐件报文含方向＋汇总含未署名 1 件"。复跑：watchdog 单跑 51 passed
（合跑那次 `test_self_heal_on_resolve` 报 WinError 5 os.replace 拒绝访问＝Windows 瞬时锁，
单跑与复跑均绿，非逻辑失败）。

### 8.6 交付态

6 码件＝3 源（写者层净增 101/−5、入队层 86/−0、哨兵层 ~107/−0）＋3 自家测试（纯追加
160/63/72 行）；治理文档 2 件（本账＋案卷 §⑨）。零新 gate_id、零新 .py 资产、零注册表标量改动、
零判据阈值放宽、零他人面随袋（逐支 `git diff --numstat` 核：删除数只发生在本班重构的 5 行）。
待办如实留册：commit-gate 形态的 L3 完整版（7 处同批，含两册 total_gates 与 priority 161-199 空段）
＝下一班的活，装机清单已在 §8.3 落定。

## 九、批令二 L3 完整版装机账（Owner 问答点头"本班接着把门装完"，2026-10-12 02-04 时窗）

### 9.1 终态＝共台而非新建件（结构性发现，不是选择偏好）

`src/zephyr/gov_enforcement/commit_gates/` 与 `tests/gov/governance/commit_gates/` 的平铺件数
**实测均已达 T_soft=120 硬上限**（`folder_capacity_hard_limit_gate._count_flat_files`＝120/120；
我的第 121 件一落地就 FOLDER-CAPACITY-HARD-LIMIT 硬阻断）。两件事同批量出来：

- 该 tests 深目录 HEAD 在册只有 66 件，盘上 121 件＝**55 件是未落地工作件**，其中
  `git status` 可见 10 件已 staged 的新测试件（test_ttl_gate / test_translation_coverage_gate /
  test_unsafe_dict_spread_gate …全属他道）；容量被在途件吃掉，本班无权也无法腾。
- 结论口径：**本仓现在放不进"新门＋新测试"这对最小件**。这不是本班绕行理由——共台
  （工厂并入 `registry_mass_deletion_gate.py`，双工厂先例＝本仓 8 个多工厂门模块）就是
  在册治本路；测试件落 `tests/gov/governance/`（实测 103 件，有余量）。
  腾容量＝退役/搬迁他道资产＝Owner 门位，本班不代裁，只如实标价。

### 9.2 装载七处（全绿自证）

| 面 | 落位 | 自证 |
|----|------|------|
| 判据本体 | `registry_mass_deletion_gate.py` 追加 ~130 行（`_pool_line_set`/`_pool_direction_pair`/`classify_pool_regression_direction`/`_pool_modified_staged_files`/`make_pool_regression_direction_gate`） | ruff format+check 2 件全绿；[DEPENDENCIES]/[INVARIANTS]/[MODIFY-GUARD] 三门自述同步改 |
| 自家测试 | `tests/gov/governance/test_pool_regression_direction_gate.py`（13 条，FakeGateway 直供字节不碰真仓） | 13 passed；宿主原 13 条复跑仍 13 passed |
| in_process 册 | 本门条目 module_path 改指宿主＋register_line 注记 | 单行改动（逐行索引比对 len 相等／差 1 行），total_gates 107==条目数 |
| gate_registry 册 | HEAD 基重放＋只注入本条目，190→191 | 键集合差：净增={本门}，净减=∅，STRATEGY-CARD 仍在 |
| 装载实测 | `auto_register_gates` | 99 门在册、POOL-REGRESSION-DIRECTION 可装载、priority 零撞号（161 独属本门） |
| creation_token | 不需要（零新建 src 件） | 先登记后撤账，见 9.3 |
| 大白话简介 | 不需要（同上） | 同上 |

### 9.3 本班自登记两条账的撤账（retired，非物理删）

装机中途我先按"新建件"形态登了 creation_token 与 module_translation 两条 PG 条目；改道共台后
这两个路径永不落地，遂 `api.retire` 撤账（authority_ref=本班批令二通道，reason 写明改道原因）。
**这是我自己 30 分钟内造的账，不是他人资产**。当前 PG 状态：两条 status=retired。

### 9.4 CREATE-GUARD 双源分歧（在册缺陷，呈统筹定位，本班不代修）

实测两台判据读的不是同一源：`_pg_confirmed_token_files` 只确认"该 file 在 PG 有 token"（第三源，
2026-10-10 maint1 加）；而 `_check_map_mounts` 走 `_collect_token_entries(registry_data)`＝**只读投影 YAML**。
后果：一个真源已在 PG 登记、但投影尚未重打的新建 `src/zephyr/**.py`，若投影里恰好没有该条目则
MAP-MOUNTS 静默跳过（`entry is None: continue`），若投影里有该条目却无 map_mounts/no_mount_reason
则**硬阻断**——同一门的两臂对"何谓在册"口径不一致。本班按窄口径同时登了 `no_mount_reason`，故不受影响；
缺陷如实留册。

### 9.5 挂图申报面实测（no_mount_reason 的承重证据）

`_load_node_map_index(.)` 实测 6 张图，**nodes 面零 gate 类节点**（含 'gate' 子串的节点＝0）。
所以本模块属"非节点图资产"，走 no_mount_reason 逃生＋审计是事实而非取巧；扩图/立格＝Owner 终审，本班不自加挂点。

### 9.6 热册生成器与投影的三处对撞（全部只测量，不改他人面）

1. **生成器会静默剪掉在册义务**：`generate_gate_registry.py` 重打时丢掉 `STRATEGY-CARD-LIFECYCLE-MAP`
   条目（其实现件不在 HEAD/盘/index），而该门在 `deadcure_campaign/07_residual_bags_index.yaml:235`
   是**登记在案的待补真缺口**；同一条事实的另一路证据＝auto_registrar 打印
   `MAP-ALIGNMENT files_trigger 死触发（HEAD 树零命中）: .../strategy_card_lifecycle_map_gate.py`。
   本班处置＝HEAD 基重放保住该条目，不替生成器背书。
2. **翻译册被 6+1 条幽灵行劫持**：`registry_ledger.registry_entry`（REG-MODULE-TRANSLATION-001/entries）
   现存 active 行 7 条指向盘上与 HEAD 都不存在的文件——`src/zephyr/{degraded,layered,lying,new_mod,orphan,with_extras}.py`
   （created_by 全＝`add_module_translation` 缺省归因名，即测试经真 CLI 写进生产账本，违根宪法 §9.6 测试隔离）
   ＋`scripts/ml/build_distilled_sft_dataset.py`（created_by=st-gpuwo-20261011，待该道自证是否未落地件）。
   任何一次合法 render 都会把这 7 条重打进被跟踪投影（实测盘上投影 vs HEAD＝+7 条/49 行）。
   本班处置＝只注入本行、其余还原 HEAD，**未替他道退役**（治理资产净删＝墓碑制＋属主车道，非本班面）。
3. **正名册 +1290 行＝批令三移交面的量化**：一次 render 把 PG 里未落地 token 全量物化（按 created_by 分布
   st-deadcure3b-chief 153／st-mineloop 39／st-gpuwo 17／st-maint2 16／st-fclean3 14／**本班 6**／其余…）。
   本班已把该册还原 HEAD 字节并留证 `.runtime/tmp/maint3_shift/capability_canonical_render_20261012.yaml`。
   **重打投影袋＝禁出**（Owner 10-10 已明令）；正解＝各属主车道自投或册主车道出一只归属写清的聚合袋。

### 9.7 一处"只读复核命令"实为写盘（自纠）

跑 `tests/gov/governance/test_derived_books_parity.py` 复核派生册一致性时，conftest 的 #ARCH-084 tracked
写入守护抓到**该测试自己写了生产册** `capability_canonical_file_registry.yaml`。该文件另有 7 条红：
逐条对过口径＝均属在册三版未定真源家族（`total_command_closeout/wave2/lane_bagging_plan.md` §四-11
"同题多版未定真源前禁各自成袋"＋deadcure P0 tests 洞），与本班两册标量无关——本班标量的判别面是
`test_gate_auto_registrar/test_files_trigger_wiring/test_files_trigger_validation`＝61 passed。
本班未修该测试（非本班件、且它一跑就写生产册），只登记。

### 9.8 一处对外件的回撤（如实标价证据等级）

为共台我曾把 13 条测试追加进 `tests/gov/governance/commit_gates/test_registry_mass_deletion_gate.py`，
随后发现该件 **不在 HEAD**（?? 未跟踪，疑为他道在途/残件），已全部逆向撤回到追加前形态：
逐条反向替换＋行数复原（202 行）＋该件原 13 条复跑 passed。
证据等级＝**构造级**（该件无 git 基线可作字节比对），不是"与 HEAD 零差"实测级。

### 9.9 交队列态

`q-20261012-st-maint3-20261011-0007`（4 件：宿主门＋自家测试＋两本门册）为本班第 7 袋。
前 6 袋（写者层/入队层/哨兵层＋三自家测试）仍在队；留守盯到落地，逐袋按 dead_reason 处置。

### 9.10 生产热册被测试写盘的第二处实证（本班一夜三次还原）

`tests/gov/governance/test_commit_queue_landing.py` 合跑时，#ARCH-084 tracked 写入守护在会话
teardown 抓到 **3 支存量测试写了生产册 `capability_canonical_file_registry.yaml`**：
`TestMainWorkspaceConvergence::test_delete_action_already_missing_is_noop_without_audit`／
`TestRegistryMergeLandingIntegration::test_three_writer_scenario_zero_loss`／
`::test_ours_retirement_honored_via_real_path_check`。
三支均**在 HEAD 在册**（git show HEAD 该行号实测 597/689/1647/1674/1786），非本班追加类；
症状与 §9.6-②/§9.7 同源（测试经真 CLI 或缺省 PROJECT_ROOT 写生产账本/投影）。
本班本班面上做的事只有还原：`capability_canonical_file_registry.yaml` 一夜三次被写脏
（render 一次＋两次测试跑），三次都还原为 HEAD 字节并留证
`.runtime/tmp/maint3_shift/capability_canonical_render_20261012.yaml`。
**本班起的后续验证一律带 `PYTHONNOUSERSITE=1` 且不再在主区合跑这两支文件**（改单跑自有测试）。
守护代码口径也如实登记：`tests/conftest.py:508` 只在 `ZEPHYR_TEST_GUARD_STRICT=1` 时硬失败，
缺省 warn——所以"抓到"不等于"拦下"。

### 9.11 同路径多修订袋的回退风险＝落地侧已有同伴闸（实测在册判据，非推测）

本班 8 袋里 `00_ledger.md` 有 4 版、watchdog 与其测试有 2 版（袋序＝入队序，落地序不按 FIFO：
实测 belt 按 lane 取件，head 那袋 00:31 入 processing 而 03:07 才真跑）。
判据真源＝`scripts/governance/commit_queue_landing.py:2016` `_witness_stale_carry`：
陈旧携带按 **stale-path 级剥除**（"部分命中=剥除危险携带路径后其余照常落地，全部命中=拒落整袋"），
另配 `_noop_overwrite_paths`（git blob 同值才短接）。
⇒ 后到的陈旧袋不会把已落地新版拍回旧字节，**本班台账不存在自造回退弹**。
这条同时是项 4 案卷的补强读数：落地侧早有方向保护的同伴闸，缺口在**直连提交/主区工作树同步**那一路
（L1 写者层补的正是那一路，L3 门补的是完全绕过队列的直连形态）。

### 9.12 队列实时态与本班袋的落地 ETA（实测标价，非承诺）

`commit_queue.py health`（03:08）＝pending 51／processing 1／done 747／dead 1456，
oldest_pending 2.6h。dev 实测落地节拍＝近 40 笔跨 512 分钟＝**12.8 分钟/袋**（0.078 笔/分）。
本班 0007 前还有 47 袋 ⇒ 线性外推 **ETA≈10 小时**（不含死信重试与整点高峰）。
本班是"留守盯到落地"，但按此节拍把班挂在空轮询上不划算；处置＝
①八袋入队后逐件 `blob_sha256 vs 盘面` 全量核过（16 件 MATCH，6 件"不匹配"全部是**同路径旧修订快照**，
 已由 §9.11 判据证明无害）；②盘面 11 件方向闸覆盖面字节已存档
  `.runtime/tmp/maint3_shift/faces_snapshot_20261012/`＋`MANIFEST.json`（落地前后双向可比，防回退弹偷吃）；
③接班复核口令（逐条可贴）＝

```
git show dev:src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py | grep -c "make_pool_regression_direction_gate"   # 应 1
git show dev:docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml | grep -c "POOL-REGRESSION-DIRECTION"      # 应 1
git show dev:docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | grep -c "total_gates: 191"                          # 应 1
git show dev:scripts/governance/commit_queue_landing.py | grep -c "skipped_head_regression"                                             # 应 >=2
git show dev:src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py | grep -c "regression_strict"                            # 应 >=2
python scripts/commit_queue.py status --session st-maint3-20261011   # 八袋 state 全应为 done；出现 dead 读 dead_reason 对症 requeue
```

## 十、通宵令执行账与晨间裁定包（st-maint3-20261011，2026-10-12 01:15 令 → 04:1x 自收）

北极星对齐：本班今夜四病根里"池面回退有闸"＝三层＋提交层已齐（§八/§九）；"队列完整性有探针"＝本节 §9.14/§9.16；
"时钟"＝§〇 预签3 实测（NextRunTime 三枚全为新时刻）；"注册表"＝§9.6+§十.3-4 撤账与治法。

### 10.1 预签3 复核（T7 运行态）＝满足，不回退

实测：`schtasks //query //tn <三枚> //xml` 取 StartBoundary＝
`ZephyrAlpha_SimBridgeExecute` 09:45 与 13:05 两腿／`ZephyrAlpha_DecisionChainSentinel` 09:50／
`ZephyrAlpha_ResourceViewPublish` 06:10；NextRunTime 三枚均为新时刻（09:35/09:40 旧冲突时刻已消失）。
资源册 `--check` 零写复核＝"注册表无漂移（104 实体）"，册字节前后同 sha256（202b5abe…，证 --check 确为只读）；
`test_resource_schedule_mem_ceiling_invariant.py` 11 passed。⇒ 依预签3"两条件皆满足＝完成入册"，不执行回退命令。
`--check` 同时报 14 条健康码（sched_task_missing×6＝册上有而系统无任务／sched_task_disabled×1／
sched_task_orphan×9 减 3 条在册豁免／GAP×5 申报受闸而源码无闸调用），全部存量、非本班引入；
其中 **sched_task_orphan 含 `ZephyrAlpha_BeltDaemon`（Running）**＝提交传送带自身不在资源画像与冲突闸内，
如实登记为待裁观察项（§十.6-C7）。

### 10.2 队列完整性簇＝两把尺（本班清位第一项）

尺一 LANDED_ID_FOREIGN 只读探针 `commit_queue.audit_landed_id_integrity`：袋内 blob（自算 git blob id，
**与内容 sha256/PG 口径不互换**）逐件比 ①记录 landed_id 里该路径 blob ②dev 现面该路径 blob。
分档：all_match／partial_match(+partial_with_absent_in_dev)／**foreign_zero_match_not_in_dev**（假落地实锤，点名）／
stale_superseded（零命中但 dev 有面＝被后继覆写，不冤枉）／unverifiable（账本族册 PG-wins、blob 已 purge）／
noop 哨兵／stub／空值／item_unreadable。health 输出键 `landed_id_integrity` **恒在**（缺省 OFF 时打
skipped 而不玩"键消失"）；死信告警旁路以 `landed_probe=False` 不烧 git 预算；预算截断显影 truncated。
测试 9 臂全绿（全 tmp 隔离；其中 stale_superseded 臂首版我构造错场景——把"后继改同文件"当成覆写档案，
实际 blob 仍相等判成 all_match，改为"记录号里无此件＋dev 另有该件"后绿，教训＝构造档要按判据集合而不是直觉）。
尺二＝入袋口续租：`_renew_claims_inflight` 放进 `enqueue_item`（四通道合流：交互正门/CLI 直投/requeue/网关改道），
ttl 沿用同一旋钮 ZEPHYR_ENQUEUE_CLAIM_TTL_S 缺省 7200s，fail-open；读 `lock_files.renew_claim` 实现确认
"只动本持有者名下已存在条目、无条目即 continue"⇒ 不造锁、测试不污染真 .ailocks。测试 8 臂全绿。
回归：`test_commit_queue_base_head + resilience` 合跑 446 支＝1 红，
`test_h2_from_bag_requeue_keeps_original_base` 撞快照重放闸（commit_queue.py:3235 要求 --allow-snapshot-replay），
与本班两把尺无因果（该 raise 在 requeue 判据支），按授权矩阵"他基座复跑定性存量红→照册登记不代修"处理。

### 10.3 终清波三移交 4 条悬挂 token＝已撤账（先自核再动手）

撤账前自核（不采信只读车道转述）：PG 四条 active v1、created_by=st-fclean3-20261012、
四路径 `git cat-file -e HEAD:` 全 ABSENT 且盘上不存在；`grep -rl` 在 done/＋dead/＋pending/＋processing/ **零引用**；
wave3 族 token 全表 18 条中后继 `lane_*.md` 7 条**全部不动**——它们正在 st-fclean3-20261012 的
pending 袋 0001/0002/0004 内待落（＝合法 token 先行，撤了会让人家落地撞 CREATE-GUARD）。
`api.retire` 四条全 OK，authority_ref 照本班令原文＝"通宵令§五·维护三班清位清单（原文：终清波三移交的
4 条悬挂 token retire）"，未编造任何裁定号；随后 publish_snapshot v409（entry_count 15583）。

### 10.4 热册治理两刀＝本班自裁（Owner 通宵令原文授权"你班裁"）

刀一＝投影生成器测试面禁写生产册（`_write_rendered` 入口，精确同根判定＋nodeid 归因＋独立计数＋
ZEPHYR_TEST_NO_PROD_PROJECTION=0 一键回退）。**自纠一处**：首版用"目标在真仓根之下"判，把
`basetemp=.runtime/tmp/pytest_<pid>`（conftest.py:95 在册 PID-unique 设计）的合法沙盘测试一屏打死 2 支，
A/B 关旗复跑立即 9 passed 才定位到判据过宽，改精确同根后宿主 9 支复绿。
刀二＝写者署名：landing 主工作区收敛按**袋属主 sid**挂 env 作用域（出界必复原，含抛错臂；sid 空一律不动）＋
belt 投影自愈探针写口署 `belt_daemon:projection_probe`。选"只包这一处"而非全局设 ZEPHYR_SESSION_ID，
理由＝该 env 还被 validate_worktree_required／apply_depgraph／git_guard／lock_files 消费，全局设置会改它们判定输入。
测试 3＋4 臂全绿，零新建 src/scripts 件（工厂/守卫全部并入既有模块，容量原因见 §9.1）。

### 10.5 一处口径自我更正（重要，防后人误读 §9.10）

§9.10 曾把热册被写归因给"三支 HEAD 在册测试＋一支派生册测试"。**该归因不成立**，证据与结论：
①开关对照——同三支测试在守卫 ON／OFF 两次跑，结果都是"2 failed／1 error"且册都变了字节，
说明写者不在这些测试里；②per-test sha 归因两次给出**不同的肇事名单**（一次三支、一次两支），
外部写者节拍约 50s，短时窗内 sha 变化会被记到"当时在跑的那支"名下；③真写者特征＝safe_write 审计里
`session=''` ＋**每次 pid 都不同**⇒ 不是常驻 daemon 单进程，而是每个落地事件派生的短命进程在做渲染
（belt 投影探针 cooldown=300s，量级也对不上"每 50s"）。
⇒ 结论下调为"存在未署名外部渲染写者，per-test 归因不可信"；本班因此补了刀二（署名）让审计面自己能答。
证据等级＝**实测**（对照实验＋审计读数），不是推断。

### 10.6 等裁清单（Owner 醒后一次转统筹；每条给建议默认）

- **C1 torch 归属二选一**。实测：单环境（系统 Python312，`__editable__` 挂 src），torch=2.13.0+cu126、
  CUDA 可用、RTX 3090；`requirements.txt:5-10` 写着"2026-07-21 裁定 #ARCH-TORCH-CPU-ONLY…已替换为 CPU 版
  (2.13.0+cpu)"，而 `pyproject.toml:115` 写着"torch 须单独装 CUDA 版（cu126 wheel）"，实装跟后者；
  torch 不入任何 dependencies 声明面（靠 sentence-transformers 传递决定版本），ml-train extras 只列 peft/trl/…；
  消费面实测 3 支（ex_sor rl_trainer 顶层 import、kronos_adapter 惰性、sentiment_sft_trainer QLoRA），
  另有无主件 cuda-toolkit 12.9.2／cupy-cuda12x／nvidia-*-cu12（Required-by 全空）。
  A＝收编：torch 入 ml-train extras 钉 `torch==2.13.0+cu126`＋撤改 #ARCH-TORCH-CPU-ONLY 注记为"训练轨 CUDA 例外"；
  B＝判外来：卸 CUDA 轮改 CPU 轮（代价＝Kronos 考尺与 QLoRA 训练轨即瘫）。
  **建议默认＝A**（B 的前提"无消费者"已被 3 支在册消费者证伪；07-21 裁定那句"项目代码 0 个 import torch"已过时）。
  不可自裁理由＝动裁定口径＋依赖声明面镜像同改。装机来源（08-08 谁装的）＝查无 provenance。
- **C2 提交网关 landed_id 判据**。根因照只读车道地图：`git_commit_gateway.py:4976-4981` 取提交后
  `rev-parse HEAD`，不解析本笔 sha、不断言 HEAD 位移；`landing:2668` 的 `update-ref new old` 在 new==old 时
  是 no-op 且 rc=0 ⇒ CAS 不报错；`:1913-1921` 的"已落盘"判定只跑 is-ancestor 零 blob 复核。
  本班只出了**观测尺**（§10.2）未动提交语义。**建议默认＝授权按"提交后校验本笔 sha 且 old!=new 才记 landed_id，
  否则记 landed_id_unverified"改造**，属判据改动故等裁。
- **C3 翻译册幽灵行 6＋1 条**（`src/zephyr/{degraded,layered,lying,new_mod,orphan,with_extras}.py` 六条
  created_by=`add_module_translation` 缺省名＝测试经真 CLI 写进生产账本；`scripts/ml/build_distilled_sft_dataset.py`
  一条属 st-gpuwo-20261011 待自证）。**建议默认＝六条本班上墓碑（一条命令）、gpuwo 那条转属主自证**；
  治本＝那条测试改走 tmp 账本/投影根（PROJECTION_ROOT 注入点在册）。等裁理由＝治理资产净删走墓碑制。
- **C4 投影物化与"禁出重打投影袋"的结构性冲突**：PG 领先 HEAD 面约 +500 行未落地 token（实测 publish
  entry_count 15583 vs 投影 15048 行），每次渲染都把他人未落地条目刷进被跟踪册并留在主区，而本班被明令
  禁出重打投影袋 ⇒ 池面在该册上**不可能保持干净**（本班一夜还原 3 次，最后一次起已放弃拉锯，改为刀二署名）。
  **建议默认＝由册主车道择窗出一只归属写清"投影重放、非本会话登记"的聚合袋，其余车道禁带该册**。
- **C5 派生册一致性测试家族**：`test_derived_books_parity.py` 7 红＋`test_gate21_selfcheck_fix_channel_is_scalar_only`
  写生产册，在册三版未定真源家族（`total_command_closeout/wave2/lane_bagging_plan.md` §四-11）。
  **建议默认＝指定唯一真源版后一次性并版**，本班未代修。
- **C6 FOLDER-CAPACITY 饱和**：commit_gates 两深目录实测满 120（该 tests 目录 121 件里仅 66 件在库）。
  **建议默认＝排一次"门族分目录"专波（含 depgraph 同步），在此之前新门一律走双工厂共台**；本班已按共台落地并留标尺。
- **C7 BeltDaemon 不在资源画像**（sched_task_orphan，状态 Running）：传送带自身不受冲突闸/资源预算管辖。
  **建议默认＝收编为受控实体并给窗**（涉排班册新实体＝Owner 门位）。
- **C8 weekend_calibration 周一/周二差一天**＝本班 §四 R11 已登记候裁（低优先，今夜未动）。
- **C9 快照重放闸 vs h2 测试期望**：`test_h2_from_bag_requeue_keeps_original_base` 期望 --from-bag 保基底，
  现闸要求显式 `--allow-snapshot-replay`。**建议默认＝改测试期望（闸是治本面，测试是旧语义）**，属判据面故等裁。

### 10.7 本班袋与接班复核口令

本班 12 袋全在队（0001-0012），无一 dead；实测队列 12.8 分钟/袋、pending 51、本班 0012 前约 47-52 袋
⇒ 线性 ETA ≈ 10 小时（0007 起为门与册，0011/0012 为今夜新尺）。同路径多修订袋不会互回退（§9.11 判据真源）。
方向闸覆盖面的 11 件字节已存档 `.runtime/tmp/maint3_shift/faces_snapshot_20261012/`＋MANIFEST.json（落地前后双向可比）。

```
git show dev:scripts/commit_queue.py | grep -c "def audit_landed_id_integrity"      # 应 1
git show dev:scripts/commit_queue.py | grep -c "_renew_claims_inflight(session_id"  # 应 1
git show dev:src/zephyr/governance/registry_projection/projection_generator.py | grep -c "TEST-PROJECTION-WRITE-BLOCKED"   # 应 1
git show dev:scripts/governance/commit_queue_landing.py | grep -c "_converge_main_workspace_impl"                          # 应 2（包裹＋本体）
git show dev:src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py | grep -c "_PROJECTION_WRITE_ACTOR"              # 应 2
git show dev:src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py | grep -c "make_pool_regression_direction_gate"  # 应 1
python scripts/commit_queue.py status --session st-maint3-20261011                  # 12 袋应全 done；dead 读 dead_reason 对症 requeue
PYTHONPATH=src python -c "import sys;sys.path.insert(0,'scripts');import commit_queue as cq;print(cq.queue_health()['landed_id_integrity']['verdict_counts'])"
```

## 十一、断电善后与 Owner 裁定③执行账（2026-10-12 15:3x-20:3x，本机两次断电之后）

### 11.1 断电后果实测（不猜，逐面对账出来的）

队列在本班离席期间继续排空，本班 14 袋终态＝**done 3（0001 台账初版／0010 GPU 知会／0011 热册两刀）
＋ dead 11**，死因三族，逐族取全文死因后对症：

| 族 | 袋 | 死因（门/ landing 原话摘要） | 处置 |
|----|----|------------------------------|------|
| 裸 subprocess | 0003、0005、0012 | BARE-SUBPROCESS：`enqueue_preflight.py:195`、`commit_queue.py:4115/4134` 三处裸 `subprocess.run` 违 trae_067 铁律2 | 全改在册统一入口 `process_pool.run_subprocess_hidden`，**未走 `# noqa: bare-subprocess` 逃生**；顺手清掉因改法而失效的函数内 `import subprocess`（不留死语句）。重投＝0016/0017 |
| 可变常量缺 Final | 0007 | MUTABLE-CONST-WITHOUT-FINAL：`registry_mass_deletion_gate.py:75` 的 `__all__`（我把宿主 `__all__` 扩成双工厂时该行进 own-diff） | 改 `__all__: Final = [...]` 正形＋补 `from typing import Final`（本文件有 `from __future__ import annotations` 也躲不掉：`__all__` 是运行时求值的真实赋值，不是注解位——此交界面如实登记）。重投＝0015 |
| 台账三方真冲突 | 0002、0004、0006、0008、0009、0013、0014 | landing：非注册表族件"双侧皆改"→整文件三方冲突死信 | 见 11.2 机制账 |

### 11.2 台账七连死的机制（终清波三收班袋替我钉到机制层，本班实测复核）

`5be65ce20b`（fclean3 收班袋）原话：袋的 `base_head` 是**车道分支旧 HEAD**而非 dev 现头 ⇒ base 面内
根本没有该件 ⇒ "dev 侧与我侧都算改动" ⇒ **即使把内容做成 dev 的严格超集也救不了**。据此给在册两条
纪律加前置条件：**"新建件先入队后落码"与"同会话后袋＝严格超集"两条仅在 base_head 与 dev 同源时成立**。

本班实测同一机制在主区的第三种触发路径：0001 落地后，dev 的 `00_ledger.md` 变了，而 0002 之后各袋的
`base_blob` 仍是落地前那版 ⇒ 七袋全被判"双侧皆改"。对策（本机已验证成立）：主区 `git rev-parse HEAD`
与 `dev` 实测**同源**（13439e6679f1 == 13439e6679f1），此时重新入袋的 `base_head/base_blob` 即 dev 现值，
且 dev 面台账字节是磁盘版的**严格前缀**（`disk.startswith(dev)=True`，269→648 行纯追加）⇒ 单一侧改动，
三方合并可过。新袋＝0019（本节所在袋）。

### 11.3 断电把本班会话判死：按在册配方复活，未加旗绕行

死机后第一次入队被 `[SESSION-REQUIRED] session 未注册` 拦（`st-maint3-20261011` 注册条目随重启消失）。
按在册配方处置：`SessionRegistry().register(sid, pid=0)` → `_spawn_heartbeat_daemon`（实测 pid 28668，
心跳 30s 一跳，`heartbeat.jsonl` status=alive）→ `register_heartbeat_keepalive(ttl=7200)`，
再以门自己的尺核命中面：`.runtime/takeover_ledger.jsonl` 全 183 条里**本会话零条目**（不必自解，
他班条目不碰）。全程未用 `allow_overlap` 之类旗子洗掉判据。

### 11.4 落地后复跑探针：假落地面比夜间读数更大（尺已在 dev，读数可复算）

`audit_landed_id_integrity` 现从落地面跑（40 袋窗口／195 次 git 比对／truncated 如实显影）：
all_match 30、partial_match 4、**foreign_zero_match_not_in_dev 5**、noop 哨兵 1，共用落地号组 0。
点名：`gpux2-0019/0020`、`minedig-0002/0005/0007`；partial 且袋字节在 dev 无面：
`gpuwo-0009/0012/0022`、`minedig-0003`。逐件二次核（本机实测，别只信分档名）：
- `minedig-0002`：20 件全部 `记录的 landed_id 里的 blob == dev 现 blob != 袋 blob` ⇒ 记的号是真的、
  **落的内容不是这袋的**（同路径被别版覆盖）。这档不是"号指错人"，是"done 而本袋内容未进库"。
- `gpux2-0019`：袋/记录号/dev 三方 blob 互不相同（该道后续又纯追加过一版）⇒ 属"陈旧袋被后继覆写"，
  与我 `stale_superseded` 档语义相邻但当前分档判 foreign（因袋字节确实不在 dev）——
  **尺的边界如实记：本探针按"袋字节是否在库"判，不按"内容是否被后继演进"判**；要区分演进需另加
  按行集包含关系的第二判据（未做，避免今夜动尺的判据面）。

### 11.5 Owner 裁定③（torch 收编）执行五款，四件同批已入队 0018

①钉版 `torch==2.13.0+cu126` 进 pyproject `[project.dependencies]` ＋ requirements 镜像同串＋
内嵌 `--extra-index-url https://download.pytorch.org/whl/cu126`；②清除 requirements:5-10 的 CPU-only
矛盾句（旧正文留在被取代条目 adjudication 内，声明面不留假指令）；③登记正门＝
`#ARCH-TORCH-CPU-ONLY` → superseded＋`superseded_by` 指回新条目 `#ARCH-TORCH-CUDA-PIN`
（adjudicator=st-maint3-20261011，内容=裁定③原文转录＋本机取证；**账本与 YAML 两侧同批改**，
实测改前 818/818 全等、改中一度差 1 条、补登后 819/819 双向零差；identity roundtrip＋entrykey parity
2 passed；字段合法性校验器只报存量 final_adjudication 漂移 19 条）；④三支消费点 import 冒烟全通；
⑤ENV-001 `disposition` 写"已收编钉版"并按该件自带 `generation_command` 现算复测＝
`2.13.0+cu126 12.6 True`（常数不搬进债账，遵本件 net_zero 口径）。
同步闸 `_check_pair` 复跑 findings=3 条与 HEAD 基线逐条同名（asia 幻影/gplearn+ta_lib/demo websockets），
**零新增噪声**；我一度把长注放进 deps 块内，被解析器读出一个假 `torch` 依赖名（块内任何双引号片段都会被
当依赖名，HEAD 里 `asia` 那条噪声正是同坑）——已把长注移到块外并留短注说明此坑。

### 11.6 今晚新登记的两条在册缺陷（入晨间包，本班未代修）

1. **`api.update` 对 REG-ARCH-ISSUE-001 旧行连"原样 payload"都拒**：`INVALID_ARGUMENT
   {payload identity mismatch with entry_key}`。根因＝身份键 `entry_composite_key` 取 payload
   **首个标量字段**现算，而 PG `jsonb` 不保键序（旧行在 PG 里首键是 `title`，在册 entry_key 却是
   `issue_id=…`）。对策＝身份字段置首重投（本班已据此成功，旧行 v2 status=superseded）。
   根治建议＝账本 catalog 为各册显式声明 `identity_fields`，禁按字典序碰运气；属 REG 账本层判据，等裁。
2. **REG-ARCH-ISSUE-001 在 ROOR 标 `maintenance: manual`，实为 PG 真源册**（账本 1633 行／active 818→819，
   且在 P0 七册齐平名单内）：标与机制不合，会诱导车道只改 YAML 而破齐平（本班 0018 差点踩中，
   靠复跑齐平测试才发现）。与 C4（投影滞后）同族。

另：`.runtime/sessions/st-dexp-20261009.json` 分片损坏致读侧静默 skip（他班早列），本机死机后复测**仍在**，
状态无变化——留队列完整性簇待办，不属本班今夜可自裁面。

## 十二、统筹四令执行账（2026-10-12 21:5x → 00:0x，含 Card A 止血与接管大扫除）

### 12.1 Card A「清理器正在吃裁定保护面」＝前提成立，止血落在删除集输入面

【实测面积】尺＝`ops_guard_delete.jsonl` 全段流扫（含轮转段 .1/.2/.3），按 `timestamp` 取窗：

- 24h 窗内 `is_protected_zone=TRUE` 且理由含"声明制直通"的删除 **1510 条**，声明方 **全部**＝
  `GATE-RUNTIME-CLEANUP`，落点 **全部**＝`.runtime/quarantine`；
- 近 7d 窗同型 **1575 条**（该闸 7d 直通总量 272,379 条的保护区子集）；
- 盘面存量：`.runtime/quarantine` 9,006 件（其中 >7d＝2,743 件＝下一轮起即删）、
  `.runtime/takeover` 507 件（>7d 233，＝接管销账证据面）、`.runtime/orphan_quarantine` **现存 0 件**、
  `.runtime/workspace_alerts` 7 件（>7d 4，含根宪法点名的 `stash_notice.json`）。

【谁的声明／什么口径】（统筹问的第②件）＝`ReconcilerSpec.file_ops=frozenset({"read","delete"})`
一次性声明覆盖整棵 `.runtime/` 遍历；`guard_remove` 在 reconciler 上下文内走
"声明即授权直通"（`is_protected_zone` 只**标记**不**判**），与 `guard_rmtree` 的
"保护区递归＝双保险硬拦"**不对称**。⇒ 单文件通道缺第二次判定，声明的粒度（整树）远大于
保护面粒度，保护面因而不存在。这就是第五次同族（M1"无声吃掉要留痕"）的机制口径。

【本班改法】按 Owner 在册正解"改喂给闸的输入，不弱化闸"：

1. `make_runtime_cleanup_reconciler` 遍历内加保护区排除面，真源取 `ops_guard.PROTECTED_PREFIXES`
   （不在清理腿另立第二份清单——多真源必漂移，`RULE-SSOT`）＋`protected_skipped` 独立出口
   （每出口独立计数，防"降级态与未触发同形"假绿）；
2. `PROTECTED_PREFIXES` 只**收紧**扩列三支取证面：`.runtime/takeover`／`.runtime/orphan_quarantine`／
   `.runtime/workspace_alerts`；
3. 留痕（统筹问的第③件）：保护区删除逐条带 `content_sha256`（M1 原话的 sha 项）。
   非保护区**不写该键**——7d 直通 27 万条全带 sha 会复刻 3.7GB/42h 洪峰（#ARCH-258 在册）。

【红绿双向自证】合成树探针（stale 8 天线）：四支取证面过期件全部存活＋`protected_skipped=4`；
同前缀长相目录 `quarantine_lookalike` 与 `handoffs` 照常删（＝修口径未变成停清理）；
审计段 `.jsonl`/`.jsonl.1`/`.jsonl.23` 全存活、同目录非审计件照删。
在册他班红队规格 `TestProtectedZoneExemption`（st-fclean4-20261012 在途字节）跑本班代码 **45 passed**。

【本班自纠一条】`.runtime/gate_audit` 一度被本班加进 PROTECTED_PREFIXES，量出副作用后撤回：
一旦入保护区，审计轮转自己的 `oldest.unlink()` 会被 in-process judge 拦，`rotate_if_oversized`
的 fail-soft 把"轮转失败"吞成 False ⇒ 当前段永不收缩，正好复刻 #ARCH-258 洪峰。
真实止血点＝清理腿的后缀豁免认轮转旧段（`*.jsonl.N` 原不匹配 `.jsonl` 后缀，实测 >7d 39 件正被删，
与在册"旧段移位保留不物理删除"直接冲突），改 `_is_audit_segment`。

【死信两枚对症】0023 死于链内 ruff 以"本提交文件整档"为作用域咬到 `ops_guard.py:223` 存量裸 except
（非本班新增），按在册 fail-soft 注记惯例补一行 `# noqa: BLE001` 带理由、语义零改动后重投＝0026；
入队口 ruff 预清把两条存量 `# noqa: m03/m10` 自定义标记当违规，本班**不改那两行**（M03/M10 门在消费
该标记，改写＝给他班门拆腿），改走在册 `--skip-preflight` 留痕旗、以锁内真门判词为准。

### 12.2 Card B 接管幽灵大扫除：183→173 open，真挡袋 11→2

尺＝门自己的函数（`load_open_entries`＋`entry_match_surface`，带正对照），判活＝
`SessionRegistry().list_active_readonly()`＋`last_heartbeat age≤90s`（在册配方，不用心跳文件 mtime 自证）。

- 183 条 open 里**只有 11 条**的命中面含仓内可提交路径，其余 172 条命中面全在
  `.aidrafts/`、`.worktrees/`、序列化器工作树副本内 ⇒ 不挡任何袋（"184 条全在拦袋"是量的错觉，
  真实拦袋面＝11 条，本班已按此排序处置）；
- 三证核账（目录在否／`.git/worktrees` 管理面在否／`session/<sid>` 分支在否，逐条实测）后
  **代销 10 条**：nightmine、nightmine-b、tests-chief、govfix-g6、regsolo、dexp、final4、vm12w、
  ffllead、deadcure3b（末条为"活班自挡型"：dirty=0 逐件 blob 对拍差 0 件、分支 tip＝dev 尖、零在途袋）；
  每条 note 逐句对处方表态，证据尺读数落 `.runtime/tmp/maint3_takeover_11_verify.json`；
- **拒销 2 条**转属主：`st-examrun-20261012`（dirty 5 件中 4 件与 dev 有差＝真未落地成果）、
  `st-gpux3-20261012`（两条车道 34＋27 件全差分，且心跳 23.6s 新鲜＝活班）。这两条按在册纪律
  只能该 sid 自销，本班不代。本班 `st-maint3-20261011` 自己的条目已先自销（§十一 之后）。
- 根因收口（统筹问的③，本班只报不改判据）：崩溃静默期 `--scan` 批量判死立 open 条目，
  而门**不看活性是否已恢复**；今日自挡死袋 14 枚全部是这一形态。提案两条见 §十二.5 菜单 C11。

### 12.3 Card C 夜间合并令三条读数（其中两条前提被实测证伪）

- ①「序列化守护已死、零进程、processing 压 4 件」→ **证伪**：
  `commit_belt_daemon` 进程在（`pythonw`/`python` 命令行实测），`belt_daemon.heartbeat` age=11.0s，
  `serializer.lease` state=drain-active、holder_pid 30476 存活；4 件 in-flight 中 3 件随后落地
  （dev 尖由 8606f242 → 0a9f7eef，含考试班 21:47 一笔）。本班未重启 drain——重启会造双传送带。
- ② 接管大扫除 → 见 §十二.2。
- ③「M14 补全：`registry_mass_deletion_gate` 只 import Final、`__all__: Final` 仍缺」→ **半证伪**：
  盘面与本班在途袋 blob 两面皆已是 `__all__: Final`（blob 内 grep 实测）；命中的是
  **dev 现值第 73 行仍是旧裸 `__all__`**（dev 面 grep 实测）——即"门链仍拦"拦的是尚未落地的袋
  （0021 死于容量型超时，内容已由 0025 重投）。任何班此刻改那本宿主模块都会被门咬，
  解法不是补注解而是让 0025 落地；本班已把此读数发统筹。

### 12.4 Card D 第四击回退弹：本班三层的在岗状态与署名缺口（喂波四取证车道）

- **L1 在 dev**：`commit_queue_landing.py` 自 10-12 16:12（6e88398e2a）起含
  `_pool_direction_regressions`／`skipped_head_regression`（`git show dev:` grep＝4 命中）。
- **L1 没写留痕**：`main_workspace_sync.jsonl` 全窗口动作分布
  `skipped_dirty 3,665｜index_shadow_clear 3,072｜index_skip_staged_wip 210｜skipped_missing 47｜error 477`，
  **`skipped_head_regression` ＝ 0 条**。⇒ 收敛臂对这 32＋24 件是"判脏拒写"，不是"写旧字节的人"。
  本班三层不背这一击，但也**不能据此定凶**——只能说写者不在落地收敛臂里。
- **哨兵层在岗**：`worktree_drift_watchdog --daemon` 进程在；`.runtime/quarantine/drift_*` 当日按小时
  ＝08×3／09×4／11×1／15×1／18×10／19×8／**21×6**／22×6，strike-4 窗口 21:41/21:44×4/21:51 六次存证在盘，
  其中 `drift_20261012T134143`（UTC 命名＝本地 21:41）内含 `data/strategy_intake/constructed_manifest.csv`
  ＝第四击打的那一族。
- **署名缺口如实**：哨兵存证只带**路径＋字节**，不带写者 pid/sid；`main_workspace_sync.jsonl` 字段全集
  ＝`ts/qid/path/action/old/new`，**无 pid、无 session_id**。⇒ "这次 stomper 的 pid/sid"没抓到。
  文件级写者身份目前只有走 `safe_write_text` 的热册面留痕（本班刀二已把 landing 子进程补上署名），
  而第四击的 24 件是**盘面旧字节回退**（非 safe_write 面）⇒ 天然无署名。收口方案在菜单 C12。
- 另案同族（本班当班新发现，非 Card D 原问）：**六个死车道的 `.aidrafts` 目录在 21:07→22:50 之间从盘上消失**
  （nightmine／nightmine-b／govfix-g6／regsolo／dexp／final4，逐条 `exists()` 复核；`.git/worktrees` 管理面
  同批消失；`session/<sid>` 分支同批不存在）。机制＝`_sweep_stale_worktrees` 启动清扫（判据三条：
  目录 age>30min＋sid 不在活性注册表＋分支 tip 是 HEAD 祖先或被取代），
  **判据不含"脏面是否为空"**——dirty 件在清扫中无判据、无 blob 备份、无遥测事件
  （`worktree_ops_log.jsonl` 事件种类全集＝pass/sync_reset/fail_closed/sync_rebase/workspace_head_diff/
  base_freshness_check，**零删除类事件**；`.aidrafts` 又在 `ops_guard.ALLOWED_PREFIXES` 内＝直通删除只计数不落盘）。
  nightmine 那条本班 21:07 还读到 5 条 token 仅在车道面、dev 与 PG 账本两面皆无——现已无处可取。
  这是"有主取证面被静默继承前先静默蒸发"的新形状，喂波四车道，并列菜单 C13。

### 12.5 通宵令晨间包增补（C10–C13，接 §十 的 C1–C9）

- **C10 清理腿判据语义等裁（本班只做到"输入面排除"为止）**：`guard_remove` 在 reconciler 上下文内
  "声明即授权直通"这一条，与 `guard_rmtree` 的保护区递归双保险不对称，是 M3/M5 保护面被吃 1510 件/24h 的
  机制根。本班**未改**该不对称——改它会让 `DeleteBlockedError` 逃逸出各 reconciler 的 `except OSError`
  （在册 P0① 提交遮蔽事故同型），须先枚举全部调用方异常面。**建议默认＝把单文件通道对齐递归双保险
  （保护区内即使已声明也硬拦＋逐条 sha 留痕），前置＝随袋带一张 reconciler 调用方异常处理清单**。
  不改的代价＝保护面今后仍依赖每条清理腿各自记得排除，忘一条即静默吃一次。
- **C11 接管门的活性复核（今日 14 枚自挡死袋的根）**：`--scan` 崩溃静默期批量判死立 open 条目，
  而 `TAKEOVER-PENDING` 门不看活性是否已恢复；现网 open 173 条中 171 条属主不在活性注册表（真死），
  自挡形态只能靠属主按配方自销（今日已三例验证、本班又销 10 条）。
  **建议默认＝门在连坐前先做一次同源判活（`list_active_readonly`＋心跳末拍），活班命中自有条目时
  降级为 warn＋留痕**；替代方案＝scan 判死前强制双源（心跳末拍＋进程表）。两条都动判据面，等裁。
- **C12 盘面回退的写者署名缺口**：`main_workspace_sync.jsonl` 与 drift 存证皆无 pid/session_id，
  非 `safe_write_text` 面的整档回退**结构上无法归因**（第四击即此）。
  **建议默认＝给 landing 收敛臂与工作树写入臂各加一行带 pid＋sid＋前后内容 sha 的遥测**
  （纯可观测性，不碰判据分支；本班 ⑫款可自裁，但因涉 `safe_write`/landing 两面的字段契约，仍列此呈批）。
- **C13 车道清扫对脏面无判据（新形状，喂波四）**：`_sweep_stale_worktrees` 三条判据不含"脏面为空"，
  且 `.aidrafts` 同时在 ops_guard 白名单与遥测豁免里 ⇒ 未落地字节可在无人批准下静默消失
  （本班 21:07 到 22:50 实测六条车道目录同批蒸发，其中 nightmine 有 5 条 token 仅存在于该面）。
  **建议默认＝清扫前对 dirty_files 做 blob 存证（refs/quarantine 或 blobs），并在
  `worktree_ops_log.jsonl` 增设 `sweep_remove`/`sweep_backup` 两类事件**；
  等裁理由＝给系统态加写面＋涉清扫判据。

### 12.6 本班在途袋终态（判据只认 dev 面读回，不信 done 目录）

| 袋 | 内容 | 结果 |
|----|------|------|
| 0023 | Card A 止血两件 | 死（链内 ruff 咬存量一行）→ 已重投 0026 |
| 0024 | watchdog CloneGuard 合流＋preflight 单口＋两测试 | 在途 |
| 0025 | 方向闸宿主模块＋专属测试＋两册登记 | 在途 |
| 0026 | Card A 止血两件（补存量注记后） | 在途 |
| 0022 | C4 聚合 render 袋（CAPCAN 投影重放，+2139 行／删 0／token 净增 424） | 死（TAKEOVER-PENDING 命中 nightmine）→ nightmine 条目已由本班 §十二.2 三证代销，**待复投** |

已落地件的内容级复验（`git show dev:` 侧读回）：0017 探针与 claim 续租、0018 torch 四面
（`torch==2.13.0+cu126`／`#ARCH-TORCH-CUDA-PIN`／ENV-001 disposition）、0019 台账 §十一＋知会 §五–§七
全部在 dev 面命中；三支测试件（投影写拦截／landed_id 探针／claim 续租）在 dev 面存在。

### 12.7 超时簇定量（统筹"60s 提交上限还成不成立"一问的实测答案）

【死信口径】尺＝`.runtime/commit_queue/dead/q-20261012-*.json` 全量正则取 `timed out after ([\d.]+) seconds`
＋`Command '[...]'` 首两段动词，今日共 **14 枚**：

| 档位 | 命令 | 枚数 | 会话分布 |
|------|------|------|----------|
| 60.0s（write 档） | `git commit --no-verify -F … --pathspec-from-file=…` | 12 | gpuwo 6／backfix3 2／本班 2／cband 1／deadcure3b 1／minedig 1 |
| 15.0s（read 档） | `git ls-files --error-unmatch -- …` | 2 | 其中 1 枚＝本班 0021（门禁 DOC-HEADER-SUITE 自身异常 fail-closed 打死袋） |

按小时：00 时 3／20 时 3／**21 时 8**。涉 7 个会话（统筹给的签名计数 364→366 是复发型累计，
本表是当日盘上枚数，两口径并存不互否）。

【档位真源定位】`git_commit_gateway.py:1159` 分级注释＝read 15s／write 60s／其他 30s；
`thresholds.yaml` 的 `git_operations` 段只 SSoT 化了四类**快照**超时
（classify／gate_chain／commit_queue_landing 120s／evaporation），commit 与 ls-files 两档仍在代码内。
⇒ 调参面目前不是单口，这条本身就是要报的口径缺口。

【空载实测对照（本机 22:5x）】`psutil` 读数＝CPU 30.4%、mem 69.7% used（avail 11.8G）。同刻三处计时：

- 主区：`git status --porcelain` 0.23s（668 行）／`git diff --cached --numstat` 0.13s／`git ls-files` 0.03s（20,872 条）；
- 池工 w2、w3 同面：0.02–0.19s。

⇒ 上限本身有**两个数量级余量**，问题形态是"并发窗内的尾延迟"，不是"60s 结构性过小"。
21 时 8 枚集中在 4–6 件并发 processing 的窗内（池 k＝6，thresholds 在册）。

【预签条件判定（可自裁面，本班据此不动）】`thresholds.yaml` 注记 Owner 09-26 批 k=6 时写
"CPU 69% 水位观察，异动回 4"。实测当前 CPU 30.4% ⇒ **时间件不成立，本班未翻 k**；
但"异动"半件证据在边缘（21 时 8 枚集中、当时 4–6 件并发、本机两次断电＋96.5% 内存水位重启），
故把 k 的处置一并进菜单而不是自决。

【提案三条（改超时＝队列判据面，带数据呈批）】

- 甲＝自适应档：按 index 条目数×并发工数缩放 read/write 上限并设上下界；改动大、判别力强，单独呈批。
- 乙＝先搬不改值：把 commit/write 与 ls-files/read 两档搬进 `thresholds.yaml` 的 `git_operations` 段
  （SSoT 化，数值原样 60/15），零判据改动，是后续任何调参的前置。
- 丙＝k 回 4 观察一夜（在册回退位，可即时复原，非新判据）。
- **建议默认＝乙＋丙并行**（二者都不动判据数值），甲另批。

## 十三、四裁执行账与两处自我更正（统筹裁定 2026-10-12 23:5x → 10-13 00:4x）

### 13.1 四裁＋超时乙丙的落地面

| 裁 | 改了什么 | 袋 | 落地面读数 |
|----|----------|----|------------|
| C10 | `guard_remove` 单文件通道补保护区双保险（已声明也硬拦）＋异常带 `zone_protected` 来源标记＋框架文案分叉 | 0031 | 45 passed；BLOCKED 审计行含 `content_sha256`；白名单面照删（非保护区不写 sha 键） |
| C11 | `TAKEOVER-PENDING` 连坐前同源判活（只放开"提交人＝条目属主且判活"一格）＋逐次留痕 | 0031 | 25 passed（新 6 臂：alive/degraded 放行留痕／dead 照拦／他班照拦／verdict 不可达照拦／无 sid 照拦） |
| C12 | 主区收敛臂"真正改写盘面"那一支补署名：pid＋袋 sid＋pre/post 内容 sha＋字节数（32MB 上限，读失败写标记串不改主链） | 0031 | 待 0031 落地后在 sync 面读回 |
| C13 | lane-archive 擦除动作进统一遥测流（begin 带栈／done 带 patch 路径＋verdict＋ahead＋pid），`_log_worktree_delete` 只增 `extra` 不改五键语义 | 0032 | 探针实测两条 `op=worktree_delete` 落流，done 条带 patch_path |
| 超时乙 | 15/60/30 三档搬进 thresholds.yaml `git_operations`，消费方 `git_commit_gateway._resolve_git_timeout` 走同一 `get()` 单口（照 `commit_queue_landing.py:129` 先例），坏值/缺键/异常退原常量 | 0032 | 实测 `READ 15 WRITE 60 DEFAULT 30`；`classify git commit→60`、`git ls-files→15`；注入桩证键非装饰 |
| 超时丙 | `commit_queue_landing_pool_workers` 6→4（在册回退位，非新判据） | 0032 | 全册键集合差＝新增 3 键／删除 0 键／值变更仅 6→4 一处 |

C10 前置的调用方异常面清单（AST 全仓）＝18 个 `guard_*` 调用点：14 处只捕 `OSError/PermissionError`、
3 处无 try、1 处 `except Exception` 兜住；逃逸面由 `reconciliation_registry:980-998` 框架层收为
critical_warn（不炸 post-commit 主链，在册 #ARCH-PRE-EXISTING-DEBT-001 形态）——这就是"带清单才改"的清单。

存量红登记不代修：`tests/gov/governance/test_commit_queue_landing.py` 27 failed/72 passed，
对 dev 现值基座复跑同为 27/72 且尾部 node id 同名（含 `TestIndexConvergenceRB1` 三支、
`TestF2ExitBurst`、`TestRegistryThreeWayMergePure` 等）⇒ 非本袋引入。**如实标注**：node-id 全集对照
只做了本班侧（`.runtime/tmp/maint3_night/red_mine.txt` 27 行），dev 侧只留了计数与尾部 6 条同名，
落地后应由任一班补一次两侧全集差集。

### 13.2 ⚠ 本班两处案卷错，另起一节留旧案（不改写 §十二 原文）

**更正一（§十二.4 末尾"另案同族"段）**：我写了"清扫判据不含脏面、dirty 件无 blob 备份、
`worktree_ops_log.jsonl` 零删除类事件、nightmine 五条 token 现已无处可取"。四句里三句错：

1. **有存证，且 fail-closed**：`_generate_retire_patch_evidence`（CAND-WORKTREE-001 Z1）在退役前把
   全量 `git diff HEAD` patch 写到 `.runtime/quarantine/<sid>-retire-<ts>.patch`（不在被删的车道里）。
   nightmine 那条**此刻就在盘上，3,217,124 字节、三分类 substantive=259**。
2. **遥测不是零删除事件**：`_log_worktree_delete` 写的键是 `op/phase/session_id/source/path`，
   我第一把尺只按 `event`/`stage` 分组，把 10,822 行读成"?"，因此把在册 171 条 `phase=done` 的
   删除事件整个看漏＝**假红尺**（在册教训同源：0 命中上报前必须配正对照——这次正对照没做，
   是下一班该盯的我自己的洞）。
3. **真凶不是 `_sweep_stale_worktrees` 而是 `lane-archive`**：六条车道存证头写
   `source=lane-archive`，`.runtime/gate_audit/worktree_abort.jsonl` 里 10-12 22:20-22:21 有
   `RETIRE_EVIDENCE`＋`needs_rescue` 逐条记录，**带 pid（7792/19688…）、分支、ahead、patch 路径**。
   也就是说：动作是有主、有审计、有存证的归档，不是我写的"静默蒸发"。
4. **四条 token 可取回**：`adjudication_routing_policy`／`t2-handover-claim-grid0926`／
   `t2-subspace-json-grid0926`／`t2-subspace-meta-grid0926` 在 `.runtime/quarantine/drift_*/…`
   的 CAPCAN 副本里命中 8/7/7 个文件；`chiefc-99-delivery-20261009` 也在 nightmine patch 内。
   取回属主车道的事（归属纪律），本班只报坐标不动手。

真实剩余缺口收窄成两条，且都已在本次两袋里堵上：**遥测流缺 lane-archive 的擦除事件**（C13 已补）、
**存证面 `.runtime/quarantine` 曾被 TTL 腿按 7 天线吃**（Card A 已堵；被吃掉的过去件已不可回，
实测 7d 内 1575 条，其中就包括别班早年的 `*-retire-*.patch`）。

**更正二（§十二.2 已写，这里补一句给统筹的复盘）**：令上"184 条 open 正在批量拦袋"的量不是拦袋量——
真含仓内可提交路径的只有 11 条，其余 172 条命中面全在 `.aidrafts/.worktrees/序列化器副本`里。
按总量排处置序会把一整夜花在不必销的条目上。

### 13.3 今夜新增四件的案卷落点（三路案卷班只读出，未改任何跟踪文件）

| 件 | 一句话读数 | 案卷路径 |
|----|------------|----------|
| ① 三方真冲突合并器 | raise 在 `commit_queue_landing.py:2446`（`_merge_registry_file` 内）；**非族件分支只有两次整文件相等判定**（:2432 noop／:2444 取袋／否则死信）——无行集、无超集、无并集语义，"严格超集也死"在源码上成立；base 取工作区自己的 HEAD(:4492)，⚑`requeue` 不带旗会在 :3312 继承旧袋陈旧 base_head；不弱化门即可校正（`--base-head $(git rev-parse dev)`）；在册三方尺 `_snapshot_head_regressions` 已存在但合并分支不调它，且是 set 语义＝无前缀判定；"同件只投一袋"是纪律不是机械门 | `.runtime/tmp/maint3_night/merger_3way_dossier.md`（处方件主文＝考试班台账 §25.11） |
| ② CH 7.14GiB | 真源**不是 settings/profile 也不是传参**：`max_memory_usage=0`（查询级不限量），7.14GiB＝服务器级 `max_server_memory_usage` 的实时派生值（0.9×cgroup/RAM，会漂：10 分钟内 7,761,811,089→7,771,823,280；Hyper-V 动态内存，启动日志自述 Available RAM 7.75GiB）。面板分母实测 daily 20,027,656 行／2019-01-02 起＝7.78 年非 8 年／格数 8.93M（名义满格 11.41M）／同键多版本 2.59× ⇒ **结论＝条件够**：逐列路线峰值 0.86GiB＝上限 0.12；24 列同查一条 SQL 理论 5.5GiB＝0.77；同族实测锚（204 列×100 只×1 年一条 SQL）3 日内 2,092 异常 vs 39 成功、峰值 7.33GiB>上限；最挤分钟 9 条重查询合计 24.9GiB＝3.4× ⇒ **24 列一次同查在本 VM 是异常路线，逐列才是安全路线**。`NO_ELEMENTS_IN_CONFIG`＝Code 139 一条（14:35:27Z）原文 `Volume default must contain at least one disk`，语义是"卷 default 解析到 0 个 disk＝配置段元素个数为 0"，不是"某设置为空值"；当前态 1 卷 1 盘不空；具体空的配置段需 VM 文件系统读面，本班未测 | `.runtime/tmp/maint3_night/ch_capacity_dossier.md`（原始读数 probe3–10_raw.json 同目录） |
| ③ schemas 遮蔽断裂 | 遮蔽本体＝pip 包 `safety_schemas` 在 site-packages 落的**命名空间包 `schemas`**（无 `__init__.py`，`import schemas` 假成功、`__file__=None`）；炸点在 `registry_ledger_ddl` 模块级 `from schemas.categories…` → ModuleNotFoundError。五面实测：PYTHONPATH=仓根通（正对照，mock 全链 register→publish→render 走通）；PYTHONPATH=src、w2 车道裸 python、以及**正规脚本直调形态**（`python <路径>`，sys.path[0]=脚本目录，不带 cwd）三面全断 ⇒ 统筹原说法需修正：不是"只在 PYTHONPATH=仓根放行"，是**正门脚本形态必断**。最险影响面＝`factory_intake_pipeline.py:311` 子进程不查 rc 全静默；`register_asset` rc≠0 但归因误指 PG。旧叙述"落投影 YAML 被覆盖"未复现——直写轨已随 #502 删除，现形态是 raise 被吞＝**根本没登记** | `.runtime/tmp/maint3_night/schemas_shadow_dossier.md`（修法候选 5 条各附代价，未选未批） |
| ④ 午夜指纹 | **陷阱成立**，判据式＝`src/zephyr/data/catchup_guard.py:154` 用 `last_success.date()`（UTC，源 `progress_store.py now_utc()`）对 `:194` `date.today()`（本地）与 `:193-197` 本地交易日历，在 `:160/:162/:164` 同式比较，消费方 `scheduler.py:337-339` ⇒ 真改补跑行为。两笔后果：凌晨跑成功⇒`daily` 桶**误判已跑过**（当日少跑）／`always_on` 桶**误判没跑过**（重复补跑），只覆盖本地 00:00-07:59 记账窗。不成立的四支已逐一排除（belt 水位／backup 8h／计划任务三色／heartbeat UTC↔UTC）；`safe_write.jsonl` 的 ts 确为 UTC 但**仓内零读者**。修法四条各附代价，首条＝`d` 改 `astimezone(上海).date()` 一行 | `.runtime/tmp/maint3_night/midnight_fingerprint_dossier.md`（跨 00:00 分桶实证本班未做，取样止于 23:5x） |

### 13.4 本班残余（交下一班或统筹定序）

1. ②③④① 四件的**修法选择全部未批**（案卷只出候选＋代价）；其中③是 P1 正门断裂，
   最小止血＝在 `registry_ledger_ddl` 起点自装仓根 sys.path（在册先例 `reconcile_worker` 的
   `#ARCH-264`-同款裁定），但选哪条应统筹定，因它牵动 pip 依赖面（卸 `safety_schemas` 一条会碰依赖库）。
2. C12 的 sync 面读回复验（0031 落地后 `tail .runtime/commit_queue/main_workspace_sync.jsonl`
   看是否出现带 pid/sid/pre_sha/post_sha 的 `wt_fast_forwarded` 行）。
3. ④ 午夜窗的**跨 00:00 分桶实证**（本班未做，取样止于 23:5x）。
4. 落地链 27 枚存量红的 node-id 全集对照（§13.1 如实标注只做了本班侧）。
5. 超时丙的"一夜数据"读数明早该回收：k=4 下再数一次超时死信枚数，与 §十二.7 的 14 枚对比，
   再决定甲（自适应）是否值得批。
