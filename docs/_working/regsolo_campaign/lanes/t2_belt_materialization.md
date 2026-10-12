---
ttl: task_bound
session: st-regsolo-20261010
landing_note: 本件由终清波三 st-fclean3-20261012 依统筹批复 M2 闸①代落，正文零改动，仅补 docs/_working 必需的 ttl frontmatter（原文无 frontmatter）；origin sha 见 wave3/26_件 §一
---

# T2 lane — belt 落地物化链路全图 + 守护重启 SOP + RB1 前置 + 队列空窗判据

session=st-regsolo-20261010 | 主仓绝对只读 | 调研完成 2026-10-09 深夜（运行时读数为当时实况）

## 结论（≤8 条）

1. **物化字节唯一写入点是 `_apply_snapshot`（:2311）**：袋 blob（`queue_root/<blob_ref>` :2334）→ `is_registry_mergeable` 分流（:2340）→ `_merge_registry_file`（:2211）产出合并字节 → `write_bytes` + 写后读回 sha 自验（:2348-2379）。B 的 PG render 换源只需动「theirs 字节来源」这一处入口，主落地段与池化重放段（`_replay_commit_without_gates` :3455 再调 `_apply_snapshot`）自动同享。
2. **谓词已扩面（关键事实修正）**：`is_registry_mergeable`（:364）自 2026-10-06 起 `del rel; return True`——**全路径恒真**，不再等于「catalogs 前缀+.yaml」；条目级 YAML 合并作用域改由 `_merge_registry_file` 内 `_is_catalog_yaml`（:2263-2264，前缀常量仍在 ：289）判定。B 的「注册表族」口径必须按 ：2264 的 `_is_catalog_yaml` 判，不能按 ：364 谓词判。
3. **cutover 安全结构现成**：对已入账本册取 `load_latest_snapshot`+`render` 当 theirs；`ProjectionUnavailable`（pg_source.py:48，无快照/PG 不可达/缺表全归一，:87-107 read_only 连接）→ 逐文件回退既有袋字节三向合并，零结构改动。PG 不可达但册已入账 = 环境性失败，应走 `SnapshotVerifyError`/`env_retry` 同款「退 pending 自愈 ≤3 次 → 死信带处方」（:1361-1420，池化重放支同闸 ：3377-3387），**禁**静默退回陈旧袋字节覆写（否则 A-12 通道复活）。
4. **守护是「计划任务每分钟探活 + 僵尸才补拉」形态**：Task Scheduler `ZephyrAlpha_BeltDaemon`（已验证 State=Ready）→ `scripts/installers/belt_watchdog.ps1`（心跳<600s 且 CIM 无 cmdline 命中才 spawn Python312 `-m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon D:\ZephyrAlpha`）。**守护无 --stop 子命令**（main :904 只有 --once/--status），停=杀 pid，看门狗 ≤60s 自动带新码拉起。
5. **裁定#281 纪元自检 re-exec 只在「drain 返回后的安全点」发生**（:816-813，`_gate_code_epoch` = `HEAD:src/zephyr/gov_enforcement` ∪ `HEAD:scripts/governance` 子树 tree sha ∪ `HEAD:scripts/commit_queue.py` blob sha）——**队列空窗无 drain 事件=永不自动换血**，这正是 10-09 A-12「改码没重启=白改」的机制根源（99_delivery 残留①：旧码守护手动重启才根治）。B 落地后必须主动重启，不能等纪元自检。
6. **RB1 翻 live 前置清单原文在 `docs/_working/chiefc_campaign/rb1_eval.md` §1.5**（6 条，§1.6 结论：具备前置 1-2 即可翻）；其中前置 1「守护重启窗」与 B 的重启是**同一个窗**，应同窗串行（B 落地→重启→RB1 翻），前置 6「负例红证：他会话在途脏文件零触碰」对 B 同样是硬约束（PG render 只准物化进落地事务 landed_paths，收敛臂 scope 护栏 `index_skip_out_of_scope` 已钉测试）。
7. **队列空窗可操作判据**：`python scripts/commit_queue.py status`（:3525）→ `counts.pending==0 && counts.processing==0` 且 `lease.state != "drain-active"`（`_lease_snapshot` :3402，alive=True=绝不可动）且 `head==null`；`health`（:3680）看 `oldest_pending_hours` 复核。实测当时（10-09 ~23:00）：pending=1 / processing=2 / lease 被守护自己（pid 32804）持有 → **非空窗，不可动**。
8. 现役守护实况：lock/heartbeat/lease 三文件同指 **pid 32804**（`.runtime/commit_queue/belt_daemon.lock` ts=368195 monotonic；heartbeat wall_ts 龄 ≈180s；lease acquired 龄 ≈75s=正在磨）。`dual_track.enabled` 旗**不存在**（仅 `.runtime/registry_ledger/dual_track.enabled.retired-20261003`），故 `_dualtrack_reconcile_if_armed`（:400）现役零行为；`_projection_drift_probe`（:441）处于「投影未武装=只挂双轨探针后即返回」态，`projection_run(mode="render")` 兜底自愈未激活。

## B 改造点清单（file:line | 现行为 | 改后行为）

数据流总图（袋 blob 字节 → worktree 文件 → commit → dev ref → 主区收敛）：

```
enqueue(会话工作区) ─→ bag: blobs/ + q-*.json{files[{path,action,blob_ref,blob_sha256,base_blob}], base_head}
  ↓ bootstrap_drain_with_landing(:4391，守护 _drain_once :116 与入队自举同入口，serializer.lease 单写者)
_conflict_reason(:1884)  W2 预检：mergeable 集(:1901，现=全路径)豁免 path 级快进死信(:1915 paths-mergeable)
_witness_stale_carry(:1957) ← _stale_carry_candidate_blobs(:4322)：「非注册表 modify 且袋字节==base_blob」
                             才入陈旧携带候选（:4336 is_registry_mergeable 处排除注册表族）
_apply_snapshot(:2311)   袋 blob 字节(:2336) →[mergeable :2340]→ _merge_registry_file(:2211) → write_bytes(:2349)
                             → 读回 sha 自验(:2357-2379)：期望=合并后字节(merged)或袋 blob_sha256 → SnapshotVerifyError
_prestage_snapshot(:2387)   git add/rm 进 index（gate 链 staged-diff 前置）
commit → _advance_dev CAS(:2448) / _pool_cas_replay(:3355区)：
                             CasConflict → 非mergeable重叠=死信(:3366-3374)；否则 _replay_commit_without_gates(:3422)
                             无漂移=re-parent 同树(:3451-3454)；有漂移=对新 dev 重跑 _apply_snapshot(:3455)+read-tree/
                             write-tree/commit-tree（plumbing 白名单，门禁语义靠内容判据保全）
成功 → _converge_main_workspace(:2709，fail-open；内含 RB1 index 收敛臂 _converge_index_one，现 shadow)
     → 完整性基线刷新/意图记录(:3408-3415)
```

注册表族字节判定点明细（`_merge_registry_file` :2211-2308）：
- theirs = 袋内快照整文件字节（:2219 decode）；ours = old_dev 的 blob 文本（:2220，None+基底有件=拒复活 ：2224-2228；None+基底也无=真新增直落 ：2229）；ours==theirs → noop（:2230）。
- base：`item.base_head` 可读则取 ：2234-2235；否则退袋内逐路径 `base_blob`（:2245，禁猜 `old_dev^`，F-AUDIT-QUEUE-04）；两者皆无 → fail-closed 死信（:2247-2255）。
- 快进短路（three_way_merge_registry_yaml :1093-1122）：base==ours 字节相等 → 整文件取 theirs，但 A-12 守门（:1107 `_theirs_drops_base_entries`）theirs 丢条目则拒快进转条目级合并——**这是现存唯一的「整档覆写」通道，B 删旧快照覆写路径主要就删/换这里对已入账本册的字节来源**。
- 非 catalog-YAML（config 等）整文件三方回退 ：2265-2281（仅袋改→取袋；仅 dev 改→noop；双侧改→死信）。
- catalog-YAML → 条目级 `three_way_merge_registry_yaml`（:1061，纯函数）+ `_heal_derived_totals`（:2292）+ merged==ours 时 `_noop_absorption_verdict` 自证（:2297，吞没=MergeSwallowVerifyError 死信带处方 ：1377-1398）。

| file:line | 现行为 | 改后行为（B） |
|---|---|---|
| commit_queue_landing.py :2333-2346（`_apply_snapshot` theirs 取用点） | theirs 恒=袋 blob 字节 | rel 命中 `_is_catalog_yaml` 且该册已入 PG 账本（registry_id 经 ROOR/`p0_physical_paths` 可解析，baseline.py :102/:113）→ theirs=「`pg_source.load_latest_snapshot(rid, rel)` + `renderer.render(snap)`」确定性投影字节；袋 blob 保留为审计/回退底 |
| commit_queue_landing.py :2211 `_merge_registry_file`（签名处） | theirs 由调用方传入袋字节 | 增 PG render 源：入参或内部解析；`ProjectionUnavailable`（未入账本册/无快照）→ 原样用袋字节走既有合并（cutover 安全）；PG 宕机但册已入账 → 抛 env 类错误 |
| commit_queue_landing.py :1093-1122 快进分支 | 快进取 theirs（袋字节） | 已入账本册：快进目标=PG render 字节（旧快照整档覆写路径在此消亡）；判不了/未入账本册保持现行为 |
| commit_queue_landing.py :1361-1420（SnapshotVerifyError/env_retry 闸） | 物化自验失败退 pending ≤3 次→死信带处方 | PG 不可达（已入账册）对齐同闸：新 `ProjectionEnvError(LandingEnvironmentError)` 或复用 SnapshotVerifyError 形态，retried_key 建议独立（如 `pg_render_retry`）；死信处方写「PG/账本不可达，恢复后自动重放」 |
| commit_queue_landing.py :3455（`_replay_commit_without_gates`） | 重放时重跑 `_apply_snapshot` | 零改动自动继承 PG render 源；验证池化 worker 同模块同行为 |
| commit_queue_landing.py :364 `is_registry_mergeable` / :2264 `_is_catalog_yaml` | 谓词恒真；catalog 作用域在 :2264 | B 的作用域判据一律挂 ：2264 口径；勿改 :364 谓词（六处调用点+测试注入依赖签名） |
| 保留路径（不动的） | — | 未入账本册全链（袋字节 theirs+三向合并）、非 catalog 件整文件三方、`three_way_merge_registry_yaml` 本体、noop 吸收自证、`_heal_derived_totals` |

## 守护重启+装载验证 SOP

1. **拉起链**：Task Scheduler `ZephyrAlpha_BeltDaemon`（AtLogOn+PT1M）→ `scripts/installers/belt_watchdog.ps1` 两段探活（心跳 wall_ts<600s 且 pid 活 → 活；否则 CIM 查 python*.exe cmdline 含 `commit_belt_daemon`）→ 双死才 `Start-Process Python312\python.exe -m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon D:\ZephyrAlpha`（cwd=仓根）。旧注册脚本 `scripts/_archive/ops/register_belt_daemon_task.ps1`（pythonw 形态）已归档。
2. **单例锁**：`_acquire_singleton`（:89）`.runtime/commit_queue/belt_daemon.lock`＝{pid, ts(monotonic)}，TTL 600s+`pp.is_pid_alive` 僵尸检测；释放 ：109。活锁存在时新启动 exit 2（:824-826）。
3. **重启步骤（空窗内）**：
   a. 前置：RULE-GUARDIAN——长批先登记 `data/runtime/process_reaper_keep.txt`（加一行 `commit_belt_daemon`）；
   b. 读 pid：`cat .runtime/commit_queue/belt_daemon.heartbeat`（或 lock）；
   c. `taskkill /PID <pid> /F`（守护无 stop 子命令；看门狗 ≤60s 自动拉起新进程，新进程启动即 `git rev-parse HEAD:…` 种子纪元+新码惰性 import 于首轮 drain）；
   d. 如需延迟到 B 已落地后再拉：置 `ZEPHYR_BELT_DAEMON_NO_REEXEC=1`（:686 运维逃生）只禁自动 re-exec，不影响 watchdog 补拉。
4. **验证新码已装载（探针方案）**：
   - B 在 `scripts/governance/commit_queue_landing.py` 加模块级常量，如 `BELT_MATERIALIZATION_EPOCH = "b-pg-render-cutover-20261010"`；
   - 重启后：①lock/heartbeat pid ≠ 旧 pid；②`powershell (Get-Process -Id <新pid>).StartTime` > B 的 commit 时刻；③heartbeat_age_s < 60（`--status` 直接给出 ：934）；④探针读数：`python -c "import sys; sys.path.insert(0,r'D:\ZephyrAlpha'); from scripts.governance import commit_queue_landing as m; print(m.BELT_MATERIALIZATION_EPOCH)"`——④证盘上新码、①②③+惰性 import（`_drain_once` :124 每进程首 drain 才 import，之后 sys.modules 常驻直至 execv/重启）合证守护内存里是新码；
   - 机制佐证：守护日志出现「纪元变更…安全点原地 re-exec（裁定#281）」（:786）=旧进程自我换血成功（但空窗无 drain 时不会出现，勿等它）。
5. **现役进程查法**：pid=`belt_daemon.lock`/`belt_daemon.heartbeat`（两者应一致）；活性=heartbeat wall_ts 龄（`--status` 的 `heartbeat_age_s`）；在磨=lease `{pid,acquired_at,renewed_at}`（`serializer.lease`，TTL 300s；`status` 输出 `lease.state`：drain-active/stale）。

## RB1 前置清单对照表（原文=`docs/_working/chiefc_campaign/rb1_eval.md` §1.5/§1.6；99_delivery 残留⑩「RB1 翻 live 待守护重启窗+shadow 账复核（前置已全备）」）

| # | RB1 原文前置 | B 件需一并满足的条目 |
|---|---|---|
| 1 | 守护重启窗：落地器改动须 belt 守护重启才生效 | **与 B 同窗**：B 落地→杀 pid→watchdog 拉新→探针验证→（同窗）RB1 才准翻 live。顺序不可倒：先翻 live 后重启=旧码跑新开关 |
| 2 | shadow 观察复核：2026-09-29 起 `main_workspace_sync.jsonl` 的 `index_shadow_clear`/`index_skip_staged_wip` 全量样本 | B 的物化改造会改变落地字节源，复核窗口应覆盖 B 落地后的新增样本，确认 PG render 字节与 shadow 口径无交互意外 |
| 3 | （优选非硬前置）主区活跃会话低峰窗首轮实做 | B 同样受益：与队列空窗判据合并执行 |
| 4 | 回滚预案：`data/runtime/main_index_convergence.off` 一票关停 | B 应对称设 off 旗（如 `data/runtime/registry_pg_render.off`），关停=全量回退袋字节三向合并旧行为 |
| 5 | 观察指标：周比 `index_cleared`/`index_skip_*` 计数；A-0 复发应为零 | B 对应指标：死信里 `ProjectionUnavailable`/pg_render_retry 计数、A-12 型「陈旧快照抹活条目」死因应归零 |
| 6 | **负例红证（硬前置）**：他会话在途脏文件（工作树 WIP+staged、路径不在 landed_paths）零触碰，`test_foreign_inflight_dirty_file_zero_touch` 已钉 | **B 硬约束**：PG render 字节只准写落地事务 worktree 的 landed_paths；主区只准经 `_converge_main_workspace` 收敛臂（scope 护栏）；禁任何「PG→主区盘面直写」旁路（A-12 复发监视 a13_recurrence_watch.md ：54-57 点名的盘面投影污染面） |

## 队列空窗判据

- 命令：`python scripts/commit_queue.py status`（queue_status :3525：counts/lease/head/daemon 四件套）、`python scripts/commit_queue.py health`（:3680：四态计数+oldest_pending_hours+blobs，只读不排空）。
- **空窗判据（全部满足才动手）**：
  1. `counts.pending == 0` 且 `counts.processing == 0`（done/dead 不计）；
  2. `lease.present == false` 或 `lease.state == "stale"`（`_lease_snapshot` :3402；`alive==True` 一票否决=有活体在磨，绝不可抢/杀）；
  3. `head == null`（无队首）；
  4. `daemon.online == true` 且 heartbeat_age_s < 60（确认看门狗-守护链活着，重启后可自动回来）。
- 附注：processing 项崩溃残留靠 lease TTL 300s+僵尸 PID 回收；杀守护若恰逢 drain-active，processing 项会退回 pending（不丢，但产生一次重放噪音）——所以判据 2 是硬门。
- 实测基线（2026-10-09 ~23:00）：pending=1 / processing=2 / done=652 / dead=1410，lease={pid:32804, acquired 75s 前}=drain-active → **非空窗**。dead=1410 与 deadcure-2 工单（rb1_eval.md §二，触发条件已满足）并行存在，B 不碰 dead/。

## 证据

- `scripts/governance/commit_queue_landing.py`：:289 前缀常量；:364 `is_registry_mergeable`（恒真扩面 2026-10-06）；:1061 `three_way_merge_registry_yaml`；:1093-1122 快进+A-12 守门；:1356-1398 CasConflict/SnapshotVerifyError/MergeSwallowVerifyError；:1401-1429 `_RETRY_META_MAX=3`+`_bump_item_retry`（env_retry/snapshot_retry 单一真源）；:1884-1929 `_conflict_reason` W2 预检（:1901 mergeable 集、:1915 豁免）；:1957 `_witness_stale_carry`；:2197-2256 基底取证（base_head→base_blob，禁猜 `^`）；:2211-2308 `_merge_registry_file`（:2229 真新增、:2230 noop、:2263-2281 非 catalog 整文件三方）；:2311-2381 `_apply_snapshot`（:2334 blob 读取、:2340 分流、:2348-2379 写后读回）；:2387-2445 `_prestage_snapshot`；:2448 `_advance_dev` CAS；:2709 `_converge_main_workspace`；:3355-3420 `_pool_cas_replay`（:3366 非mergeable 死信、:3377-3387 env 错误透传）；:3422-3461 `_replay_commit_without_gates`（:3451 无漂移 re-parent、:3455 重跑 `_apply_snapshot`）；:3497 `resolve_pool_workers`；:4322-4347 `_stale_carry_candidate_blobs`（:4336 mergeable_pred 排除注册表族）；:4391 `bootstrap_drain_with_landing`。
- `src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py`：:5-8 头注（watchdog 事件驱动+单例+心跳）；:57-82 常量（lock/heartbeat/水位线）；:85-113 单例锁；:116-131 `_drain_once`（:124 惰性 import landing）；:338-389 离线缺口检查；:396-438 `_dualtrack_reconcile_if_armed`（:412 旗=`.runtime/registry_ledger/dual_track.enabled`）；:441-470 `_projection_drift_probe`（:453 未武装返回）；:685-688 纪元子树常量+`ZEPHYR_BELT_DAEMON_NO_REEXEC`；:691-761 纪元采集（gov_enforcement 子树∪scripts/governance 子树∪scripts/commit_queue.py blob）；:764-776 lease 活体判定；:779-813 re-exec 安全点契约；:816-901 `run_daemon` 主循环（:875 30s 心跳窗、:892 drain 后纪元自检）；:904-940 CLI（仅 --once/--status，无 stop；:934 heartbeat_age_s）。
- `scripts/installers/belt_watchdog.ps1`（两段探活+spawn 命令全文）；`scripts/_archive/ops/register_belt_daemon_task.ps1`（任务 ZephyrAlpha_BeltDaemon=AtLogOn+PT1M、pythonw 形态已归档）；实测 `Get-ScheduledTask ZephyrAlpha_BeltDaemon` → State=Ready。
- `src/zephyr/governance/registry_projection/pg_source.py`：:48 `ProjectionUnavailable`、:87-107 `load_latest_snapshot`（read_only depgraph 连接，registry_snapshot 最新版，row=None→无快照异常）；`renderer.py` :140 `render(snapshot)`（确定性投影文本）。
- `src/zephyr/governance/registry_ledger/baseline.py`：:102-110 `P0_REGISTRY_IDS` 七册；:113-146 `p0_physical_paths`（ROOR∪YAML 头反查）。
- `scripts/commit_queue.py`：:173 `_LEASE_FILE`；:3402-3441 `_lease_snapshot`（state=drain-active/stale）；:3525-3565 `queue_status`；:3680-3737 `queue_health`；:4555/:4609 status/health 子命令。
- RB1：`docs/_working/chiefc_campaign/rb1_eval.md` §1.5 前置 6 条+§1.6 建议；`docs/_working/chiefc_campaign/99_delivery.md` :98 残留⑩；`docs/_working/chiefc_campaign/a13_recurrence_watch.md`（A-12 复发=盘面投影面、守护旧码病灶）。
- 运行时实况：`.runtime/commit_queue/{belt_daemon.lock,belt_daemon.heartbeat,serializer.lease}`（pid 32804；heartbeat 龄≈180s；lease drain-active）；`.runtime/commit_queue/` 四态计数 pending=1/processing=2/done=652/dead=1410；`.runtime/registry_ledger/` 仅 `dual_track.enabled.retired-20261003`（旗已退役未重建）。
