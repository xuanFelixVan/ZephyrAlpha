---
ttl: task_bound
completes_when: F9 队列新件死信治本已落地并复核
rule_form: data
verifiability: manual
title: F9 作业簿——提交队列 untracked 新文件落地死信缺陷治本（SerializerLease 续租+活体不抢）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: active
---

# F9 作业簿 — 提交队列 untracked 新文件落地死信缺陷治本

> 施工包：加餐缺陷包 #9（免签，来源会话 st-consrep2-20260917）｜真源：Owner 夜令 #9 §3-§8
> 会话：st-flashspeed-20260918｜lock 持有：`scripts/commit_queue.py`、`tests/governance/test_commit_queue.py`、`tests/governance/test_commit_queue_landing.py`
> 靶点：`SerializerLease`（commit_queue.py L671）+ `drain_queue` 主循环（L1075）。
> **与 F2 关系**：本包治本交付 F2「lease 续租」前置件（master ledger P-1 / S18-R3 红队复验三要件之一）；F2 余下双通道压测+热文件单通道闸另簿。

## 0. 病灶（第一性原理）

**缺陷签名**（2026-09-17 取证，`.runtime/commit_queue/dead/` 11 条死信）：含 untracked 新文件的
队列项落地时报 `error: pathspec ':(icase)<新文件相对路径>' did not match any file(s) known to git`
→ 死信。代表件 `q-20260917-st-ailayer-20260917-0013.json`，dead_reason 带 `[诊断] 自愈重试仍败`
后缀，git status 显示 `A docs/_working/ai_layer_vision/L1_perceive/DESIGN.md`（已 staged）却 pathspec
失败——**Mode B 自愈重放亦救不回**。关键特征：**只有新文件死，tracked 文件项正常落地**。

**根因（挖矿五反证后唯一自洽解释）= SerializerLease 租约竞态**：
1. `SerializerLease.__enter__`（L706）获取时写一次 `acquired_at`，**全程不续租**；无 `renew()`。
2. 旧 TTL 分支（原 L729）对「活 PID + acquired_at 超 TTL(300s)」的租约**直接 os.remove 回收**——
   不校验持有者是否仍在工作。
3. drain 处理慢项（reconciler 超时 180s 级）墙钟撑破 300s TTL → 并发自举 drain（`try_bootstrap_drain`
   每次 enqueue 都触发）判租约过期 → **抢锁成功** → 两个 drain 同跑一个 serializer worktree。
4. thief 的 `_sync_worktree`（commit_queue_landing.py L401：`reset --hard dev` + `clean -fd`）删掉
   victim 已 `_apply_snapshot` materialize、已 `_prestage_snapshot` staged、**尚未 commit** 的 untracked
   新文件（`clean -fd` 清 untracked；`reset --hard` 撤 index）。
5. victim 提交期网关 step3a（`_add_and_remove_normal_files`）`os.path.isfile`=False → `git rm --cached`
   → commit pathspec 指向已不存在的新文件 → **did not match 死信**。
6. **tracked 文件为何不死**：`reset --hard dev` 把 tracked 文件恢复到 HEAD 内容、**仍在盘**，step3a
   isfile=True → git add → pathspec 匹配。故签名=「只有新文件死」，与取证 100% 吻合。
7. **Mode B 自愈为何亦败**：自愈重放 apply+prestage 期间，thief 的 clean -fd 竞态窗口仍在（两个 drain
   持续交错），重放的新文件再次被清 → 重试仍 did not match（L925 诊断后缀即此）。

**间歇性 + 夜间多会话战役期聚集**：仅当「慢项在途 > TTL」与「并发自举 drain」同时发生才触发——
正是夜间多会话（altdata 等）+ 慢 reconciler 高峰期，与 11 条死信的时间聚集吻合。

## 1. 六向寻路台账

| 向 | 探查 | 结论 |
|----|------|------|
| ①上游 | 谁触发抢锁 | `try_bootstrap_drain`（每次 `enqueue_item` 后自举）+ 显式 `commit_queue.py drain`；多会话并发入队 → 多个 drain 争 `SerializerLease` |
| ②下游 | 抢锁后毁什么 | thief `_sync_worktree` 的 `reset --hard`+`clean -fd` 作用于**共享** serializer worktree（`.runtime/commit_queue/worktree/`，单一 git linked worktree）→ 删 victim 未提交新文件 |
| ③算法机制 | 租约生命周期 | O_EXCL 原子创建；TTL=300s；僵尸 PID 检测（`is_pid_alive`）；超时 5s 放弃。**缺环=无续租、TTL 回收不校验活体工作状态** |
| ④后端 | DB 读写 | 不涉及 DB；纯文件锁（`serializer.lease` JSON：pid+acquired_at）+ git worktree 状态 |
| ⑤前端 | 无 | 纯后端队列落地链路 |
| ⑥数据字段 | 租约字段 | `pid`（活体判定真源）、`acquired_at`（TTL 判定基准，**原全程不刷新=病根**）；修复新增 `renewed_at`（续租留痕，审计可观测） |

## 2. 治本设计（三处改动，均在 commit_queue.py，零碰门禁/网关 pathspec 语义）

**核心洞察**：TTL 的本意是「持有者**崩溃**后自动回收」，不是「持有者**慢**时被抢」。崩溃已由
僵尸 PID 检测（`is_pid_alive`）零窗口即时回收兜底；TTL-only 回收只需保留给「无 PID 可校验」的
损坏/旧格式租约。活体持有者即便显示超期（慢项在途）也**绝不可抢**——抢=毁 worktree=杀死新文件。
再用 `renew()` 心跳令工作中 drain 的 `acquired_at` 始终新鲜，TTL 对活体永不触发（双保险）。

**改动 1 — `__enter__` TTL 分支改活体感知**（L729-753）：
- 超 TTL 且 `holder_pid is None`（损坏/旧格式）→ 保留 TTL 回收语义（os.remove + continue）。
- 超 TTL 且持有 PID **仍存活**（死亡持有者已被上面 dead-PID 分支即时回收）→ 判「慢项在途」，
  **不抢**，落 warning 后 fall-through 到 `expired = monotonic() >= deadline` 等待逻辑，至 timeout
  抛 `LeaseUnavailable`（自举语义：拿不到等下次，项安全留 pending 零丢失）。

**改动 2 — 新增 `SerializerLease.renew()` 心跳**（L775-824）：
- 把 `acquired_at` 原子刷新为当前时间（tmp + `os.replace`，防半写损坏），附 `renewed_at` 留痕。
- **防易主误覆盖**：覆盖前校验租约 `pid` 仍是本进程；已易主 → 返回 False 并置 `_acquired=False`
  （绝不 clobber 新持有者，且令 `__exit__` 不误删他人租约）。
- **fail-open**：读/写 OSError 不抛进排空主循环（返回 False，调用方继续）——续租失败不致命，
  改动 1 的活体感知分支已兜底防抢。

**改动 3 — `drain_queue` 主循环逐项续租**（L1075、L1080-1090）：
- `with SerializerLease(...) as lease:` 绑定句柄。
- `while` 循环体首行 `lease.renew()`——每处理一项刷新租约，令「活着且在干活」的持有者永不被 TTL 误抢。

**为何治本非对症**（Owner 红线「加大超时/加重试/日志降级=对症只准记账」）：
- 未加大 TTL、未加重试、未降级日志——改的是**锁的正确性语义**（活体不可抢 + 心跳保鲜），
  消灭「双 drain 并发毁 worktree」这一根因，而非掩盖其症状。
- 与裁定#280（落地可靠性语义重做）**对齐**：未把 pathspec 错误塞进 `_TRANSIENT_GIT_MARKERS`
  改判「瞬态环境失败」（Owner §4 明令禁止——那会让坏项无限重试卡队）；死信分类语义零改动。
- 未碰网关 pathspec 语义、未放宽任何门禁（Owner §7 明令）；未动 `_apply_snapshot`/`_prestage_snapshot`
  （挖矿已证二者对新文件写入+git add 均正确，非病根）。

## 3. 安全性 / 等价证明（红蓝自审 + 零回归实证）

| 场景 | 修复前 | 修复后 | 等价/改善 |
|------|--------|--------|-----------|
| 持有者崩溃（PID 死） | 僵尸分支即时回收 | 同（僵尸分支零改动） | ✓ 不变 |
| 损坏/旧格式租约（无 PID）超 TTL | TTL 回收 | TTL 回收（holder_pid is None 分支） | ✓ 不变 |
| 活体持有者超 TTL（慢项在途） | **被抢 → 毁 worktree → 新文件死信** | 不抢，等待至 timeout 放弃，项留 pending | ✓ 治本 |
| 活体持有者新鲜租约 | 不抢（未超 TTL） | 不抢 + renew 保鲜 | ✓ 双保险 |
| 工作中 drain 逐项续租 | 无续租，慢批必超 TTL | 每项 renew，acquired_at 恒新鲜 | ✓ 治本 |
| 续租时租约已易主 | N/A（无续租） | renew 返回 False 不 clobber，__exit__ 不误删 | ✓ 新防护 |
| tracked 文件项落地 | 正常（reset 后仍在盘） | 正常（零改动） | ✓ 不变 |
| untracked 新文件项落地 | **竞态期必死** | 竞态根因消除 → 正常落地字节级一致 | ✓ 治本 |

**零回归实证**（逐文件跑，Owner §6 测试纪律）：
- `tests/governance/test_commit_queue.py` → **83 passed**（基线 80 + 净增 3：活体不抢回归 1、无 PID 回收 1、renew 保鲜/防易主 2，删旧「活体超期被抢」误语义钉 1）。
- `tests/governance/test_commit_queue_landing.py` → **37 passed**（基线 35 + 新增 2：acceptance ① 字节级一致 1、能红证明 pathspec 死信签名 1）。
- `tests/governance/test_commit_queue_integration.py`（真 gateway 全门禁链 29 例）→ 见 §6 施工日志。
- `SerializerLease` 类引用全仓扫描：仅 commit_queue.py + 两测试文件（ops_guard.py 仅注释提及）→ 改动半径封闭，无其他测试依赖旧 TTL-steal 语义。

## 4. 判据映射（Owner #9 §5 验收三件）

| 判据 | 验法 | 结果 |
|------|------|------|
| ① 单测：入队含 untracked 新文件快照 → 落地成功 + blob 字节级一致 | `TestUntrackedNewFileLanding::test_untracked_new_file_lands_byte_identical_via_pathspec`（**pathspec 保真桩**，非 whole-index 桩——后者对缺陷结构性失明恒 GREEN） | ✓ PASS（done=1/dead=0，`show dev:docs/brand_new.txt`==content，commit 恰 1 次零自愈） |
| ② 零回归：landing 30 + queue 80 | 逐文件跑：landing **37 passed** / queue **83 passed**（均超基线，净增全为本包新钉） | ✓ PASS |
| ③ 实弹：enqueue→drain 含新文件，`git log -1 --name-only` 归属正确 | 见 §6 施工日志实弹记录 | ✓ 见日志 |
| **能红证明**（Owner 铁律「判通过的脚本须先证明能红」） | `test_new_file_wiped_before_commit_reproduces_pathspec_deadletter`：monkeypatch `_prestage_snapshot` 持续清新文件 → 复现 `did not match`+`pathspec`+`[诊断]` 死信签名（commit 调 2 次=首试+Mode B 重试） | ✓ 桩对缺陷可见（GREEN↔RED 双向） |

## 5. 挖后自审闸（三态）

**裁定 = 施工**。理由：
- ①设计闭环：根因（租约竞态）经五反证排除（_sweep 撤暂存/step3a isfile 竞态/`:(icase)` 怪癖/外来残留/gate 链改 index 均经复现证伪），唯一自洽解释=活体 TTL 抢锁；治本三改直击根因。
- ②不碰任何门禁语义/判据/通道数/POST-COMMIT-GUARD/RULING-REFERENCE/risk_tier 门位（Owner 禁项全守）。
- ③与裁定#280 对齐，未塞 `_TRANSIENT_GIT_MARKERS`，未改网关 pathspec，未放宽门禁。
- ④非对症（未加大超时/重试/降级日志）——改锁正确性语义，消灭根因。
- ⑤可机验：单测能红能绿 + 零回归 + 实弹归属。
- **过度工程三问**：是否消灭人工参与？是（死信不再需人工 requeue 新文件项）。是否引入第二真源？否（复用既有 `is_pid_alive` 僵尸检测 + 租约 JSON，仅补 renew 字段）。现状规模小是否封矿理由？否（按夜间 50-100 车道并发终局判——并发越高租约竞态越频发，本修复是通道扩容的前置地基）。

## 6. 施工日志

- [x] 挖矿：读透 `SerializerLease`（L671-824）+ `drain_queue`（L1036-1182）+ landing `_sync_worktree`/`_apply_snapshot`/`_prestage_snapshot`/`__call__`（含 Mode B 自愈 L895-932）+ 网关 step3a/pathspec/commit 全链。
- [x] 五反证复现（_sweep/step3a isfile/`:(icase)`/外来残留/gate 链改 index 逐一证伪）→ 锁定租约竞态为唯一自洽根因。
- [x] 取证核实：`q-20260917-st-ailayer-20260917-0013.json` dead_reason `[诊断]` 后缀显示新文件已 staged 却 pathspec 失败（smoking gun）。
- [x] 改动 1：`__enter__` TTL 分支活体感知（holder_pid is None 才回收；活体不抢，等待至 timeout）。
- [x] 改动 2：新增 `renew()` 心跳（原子刷新 acquired_at + pid 防易主 + fail-open）。
- [x] 改动 3：`drain_queue` `as lease` 绑定 + 循环首行 `lease.renew()`。
- [x] `ast.parse` 语法核验 OK；Python 3.12.8。
- [x] 测试：queue 83 passed / landing 37 passed（逐文件跑）；新增 5 钉（活体不抢、无 PID 回收、renew 保鲜、renew 防易主、新文件字节级一致 + 能红死信签名）。
- [x] pathspec 保真桩 `_PathspecStubGateway`（生产同款 `--pathspec-from-file` + `:(icase)rel` + step3a add/rm）——补 whole-index 桩对缺陷失明的盲区。
- [ ] integration 29 例真门禁链回归（后台运行中，结果回填）。
- [ ] 实弹：enqueue→drain 含新文件 → `git log -1 --name-only` 归属核实（结果回填）。
- [ ] 提交（`git_commit.py --session st-flashspeed-20260918 --files <清单> --allow-multi-domain --wait` 直连，**含新文件批次缺陷修复前勿走队列**=Owner §6）。
- [ ] architecture_issue_registry.yaml 登记（取号前 `git show dev:<file>` 重算 max+1，status=resolved 指向修复 commit）。

### 验收结论（待提交后封矿）

| 判据 | 结果 |
|------|------|
| ① 新文件落地字节级一致 | ✓ pathspec 保真桩单测 PASS |
| ② 零回归 | ✓ queue 83 / landing 37（integration 回填） |
| ③ 实弹归属正确 | ⬜ 回填 |
| 能红证明 | ✓ 持续清新文件复现 pathspec 死信签名 |
