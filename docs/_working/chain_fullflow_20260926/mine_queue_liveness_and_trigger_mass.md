---
ttl: task_bound
---

# 案卷 M4 — 提交队列活性 / 饿死 / 触发面臃肿 家族（只挖矿，不施工）

> 取数时刻（UTC）：2026-09-25T18:23Z–18:4xZ 窗口（`date -u` 实测三点：叙述 ts ≤ 文件 mtime ≤ 收尾 `date`）。本地=UTC+8。统计脚本与中间产物在 `.runtime/tmp/mine_dossiers_20260926/`。全程只读：未 drain、未 requeue、未动主区 index、未提交。本卷所有计数=实测读数+取数命令，勿当常数引用。

## 0. 母节点与分母

- 母节点 = 端到端提交链吞吐（袋→队首→落地→HEAD），Owner 关心"提交链速度=开发速度"。
- 实测分母（快照窗口内）：
  - `pending/`=9、`processing/`=1、`done/`=804（受 done TTL 截断）、`dead` 系（dead + 各 dead_archive）合计 = 2397。
  - `main_workspace_sync.jsonl` = 1805 行（skipped_dirty 1802 / error 3 / 其余 0）。
  - `gate_registry.yaml`：字段 `total_gates: 181`，机读解析 gates 数 = 181（字段与解析一致）；dev 树文件数 = 17746（`git ls-tree -r dev --name-only | wc -l`）。
  - 门禁计时账本：6 个 stats 根（主区 + w0..w3 + serializer worktree）合计链式记录 5006 行、被计时门 128 个。
- 复现：`python .runtime/tmp/mine_dossiers_20260926/m1_queue_stats.py`；`wc -l / grep -c` 见 §2；`python .runtime/tmp/mine_dossiers_20260926/m3_gate_trigger.py`。

## 1. 矿脉一：排队键与公平性

### 1.1 排队键现状（dev 与在盘双验）——底数修正

- **两版 `_pick_head` 均已是 B4 版**：车道内按 `created_at` FCFS、`qid` 仅破平；machine 车道等待超 `_MACHINE_LANE_STARVATION_SEC` 提前放行；B5 退避（attempts≥3 排序键加 900s/次惩罚→未来时刻让位；attempts≥5 拾取即死信）。
  - 复现：`grep -n "_pick_head" -A 25 scripts/commit_queue.py`（在盘 ~L1422）；`git show dev:scripts/commit_queue.py > .runtime/tmp/mine_dossiers_20260926/commit_queue_dev.py && grep -n "_pick_head" -A 25 .runtime/tmp/mine_dossiers_20260926/commit_queue_dev.py`（dev ~L1504）。
  - dev 版 docstring 自述（当数据读）：旧形状"heads 按 qid 字典序预排⇒主键实为会话名字母序；实测 24h 内 1081 对先后 56% 倒挂、最老件等 5.9h、09-24 14:29–15:21 HEAD 零推进 52min"⇒**任务书母节点描述的"合规独占队首饿死"是 B4 修复前形状，修复已落地 dev**。
- `created_at` 秒粒度**证实**（804 件 done 时间戳带小数者 = 0，`_now_iso()` 秒级），同秒退化 qid 字母序**存在但面小**：804 件仅 21 件与他件共享 exact second（distinct 792/804≈2.6%），且同秒件多为同一会话连号袋（qid 序号尾递增⇒字母序=到达序，良性）。**次生候选**：reconciler 派生 machine 批同秒入队时的会话间并列。
  - 复现：`.runtime/tmp/mine_dossiers_20260926/` 内 tie 统计（`items_sharing_exact_second: 21`）。

### 1.2 饿死/等待分布（重取数，done 804 件 `landed_at−created_at`）

| 指标 | 实测 | 备注 |
|---|---|---|
| p50 | 263 s ≈ 4.4 min | |
| p90 | 4,358 s ≈ 1.2 h | |
| p95 | 8,448 s ≈ 2.3 h | |
| p99 | 32,776 s ≈ 9.1 h | |
| max | 44,149 s ≈ 12.3 h | `q-20260924-st-t0-matrix-20260924-0031` |
| >1h | 88/804 ≈ 10.9% | |
| >6h | 17/804 ≈ 2.1% | |
| >24h | 0 | |

- 长尾簇：top-10 最劣中 8 件为 `st-metaq-20260923-00xx` 连号袋、等待 9.1–9.2h——**同会话整批同等待遇**，形状="批次被反复退回/门禁拦+落地服务时间被 §3 贵门吃掉"，**非字母序独占**。
- 当前 pending 最老 = 0.42h（无跨日饿死袋）。任务书"09-24 入队到 09-26 未落地"案例：当前 pending/processing 无同名在等件；死信侧 09-22/09-23 陈旧袋留在 dead/（终态留档）⇒该案例的真实归宿=死信往返或已落地后被 TTL 抹痕，不作单点引用。
- 复现：`python .runtime/tmp/mine_dossiers_20260926/m1_queue_stats.py`（`wait_pct` / `top10_worst` / `pending` 段）。

### 1.3 本矿脉盲区（如实记录）

- `done/` 有 TTL（`_DONE_TTL_DAYS_DEFAULT`），>24h 等待件落地即到期蒸除 ⇒ 上表是**存活窗内下界**；全历史分布需常设"落地流水账"（见 §9 C2）。
- 等待分解（排队时长 vs 服务时长）当前账本无法逐件拆分；`pool_wave.log` 显示工间大量 `exit=claim_none`（空转轮询），belt 心跳正常（`belt_daemon.heartbeat` wall_ts 18:29:49Z、mtime、`date` 18:30:16Z 三点对齐）。

## 2. 矿脉二：skipped_dirty 下游影响

### 2.1 语义（代码机判）

- 唯一读者/写者 = `scripts/governance/commit_queue_landing.py`（`grep -rln "main_workspace_sync" --include="*.py" src scripts` 仅命中此一件）。
- 语义（L1747-1761）：袋已落地 dev 后，落地器逐文件把**主工作区**快进到 new_sha；若盘上内容 ≠ old_sha（他会话 WIP 持脏）或未跟踪同名文件 ⇒ `skipped_dirty` 跳过（零丢失铁律：宁不收敛不覆写他人 WIP）。收敛异常 fail-open（仅 warning+留痕）。
- 实测：1805 行 / skipped_dirty 1802 / error 3（error 只涉 2 个 qid）；涉及 **431 个 qid、939 个 distinct 路径**。热点集中：`capability_canonical_file_registry.yaml` 112 次、`module_translation_registry.yaml` 41 次、`rule_catalog_registry.yaml` 16 次、`rules_integrity_db.json` 16 次。
  - 复现：`wc -l .runtime/commit_queue/main_workspace_sync.jsonl; grep -c skipped_dirty 同名文件` + path 计数脚本（`.runtime/tmp/mine_dossiers_20260926/` 内 sync 分析段）。

### 2.2 失效不变量与相关性实测

- 被破不变量 = "主工作区随 HEAD 逐文件收敛"（真源注释标 66 号 §9.7 受控放松，2026-08-23）。后果链（机判）：
  1. 主区热册长期陈旧 ⇒ 后续袋以陈旧盘为基底，再落地时"注册表三向合并失败"死信簇同热点文件：dead_reason 含三向合并失败 137 件，其冲突文件 top2 = canonical registry 60 次、translation registry 42 次——**与 skipped_dirty 热点 top2 完全同峰**（同根=主区热册被多会话长期持脏）。
  2. 观测盲区：sync 日志无第二消费方 ⇒"主区漂移"不进任何告警账（worktree_drift_watchdog 另有账，未与 qid 关联）。
  3. 门禁再校验面：读盘型门对陈旧盘判读的风险（先例账本在案"读盘不读册"类缺陷）——本卷只登记嫌疑，逐门证明属施工面。
- 相关性证伪一条：**qid 级"skipped_dirty→后续死亡"相关 = 0**（137 个 merge-fail qid 中 0 个出现在 skipped_dirty 日志）⇒ skipped 的袋本身多已落地成功，伤害落在**后继袋**的合并面上。窗口截断（日志起点 2026-08-24）注意。
- 复现：`.runtime/tmp/mine_dossiers_20260926/` 内 dead×sync 交叉脚本（输出 `merge-fail qids also present in skipped_dirty log: 0/134`）。

## 3. 矿脉三：门禁触发面与成本

### 3.1 触发面覆盖（机判 gate_registry × dev 文件树 × 最近 150 袋）

- 覆盖 8791 文件的门共 **7 个**（底数"8791"证实为特定 glob 簇，非全门）：ASYNCIO-RUN-IN-CONTEXT / GATE-DOMAIN-FK / FILE-COPY / FUNCTION-DUP / BLOOD-FLESH / UNSAFE-DICT-SPREAD / COMPLEXITY-GUARD。对**真实袋**的触发率仅 0.32（袋多为 docs 件）⇒"覆盖大"≠"每袋必触发"。
- **每袋必触发集 = 1 门**：`R5-DIGIT-SUFFIX`（files_trigger 覆盖 13,725/17,746 ≈ 77% 仓文件，近 150 袋触发率 **0.94**，own_scope=False）。
- `always_run` 仅 1（GATE-COMMIT-GW）；files_trigger 为空的门 104 个——其中 in-process 内容扫描门（CREATE-GUARD/CAPABILITY-OVERLAP/REGISTRY-MASS-DELETION）**不走 files_trigger 也每链执行**（见 3.2），registry 的触发面对它们无描述力=**登记口径缺陷**。
- own_scope 已标记 33/181。
- 复现：`python .runtime/tmp/mine_dossiers_20260926/m3_gate_trigger.py`（输出 top15、≥90% 集、empty-trigger 计数）。

### 3.2 实际耗时 × 触发率（5+1 stats 根 union，UTC；slow_item 右删失教训已避开——改用逐门 ms 明细）

Top（score = total_s × bag_rate；CREATE-GUARD rate=0 因无触发面登记，按 0.01 地板计，仍见 raw total）：

| 门 | execs | mean | max | total(链累计) | bag触发率 | files覆盖 | own_scope |
|---|---|---|---|---|---|---|---|
| CREATE-GUARD | 4488 | 23.4 s | **1558.3 s** | **105,154 s** | 未登记 | — | False |
| CAPABILITY-OVERLAP | 4436 | 7.5 s | 89.6 s | 33,426 s | 未登记 | — | True |
| REGISTRY-MASS-DELETION | 4546 | 5.7 s | 323.7 s | 25,974 s | 未登记 | — | True |
| RECONCILER-HEALTH | 3795 | 6.2 s | 277.5 s | 23,716 s | 0.233 | 2398 | False |
| REFERENCE-INTEGRITY | 998 | 5.5 s | 110.2 s | 5518 s(×0.66 率高) | 0.66 | 8031 | False |
| GATE-DOMAIN-FK | 4017 | 1.5 s | 106.2 s | 5973 s | 0.32 | 8791 | False |
| COMPLEXITY-GUARD | 1251 | 4.3 s | 206.0 s | 5389 s | 0.32 | 8791 | True |

- **Top-5 贵门（耗时×触发面综合）**：CREATE-GUARD、CAPABILITY-OVERLAP、REGISTRY-MASS-DELETION、RECONCILER-HEALTH、REFERENCE-INTEGRITY。
- 处方二分（宪法 §3 第 1/3 条）：
  - **该改 own-scope 差分**：CREATE-GUARD / CAPABILITY-OVERLAP / REGISTRY-MASS-DELETION（无触发面登记、每链全量、max 均 ≥89s——差分后 docs-only 袋成本近零）；REFERENCE-INTEGRITY / RECONCILER-HEALTH 同理（触发率×全量扫描）。
  - **该缩触发面**：R5-DIGIT-SUFFIX（0.94 必触发+77% 仓覆盖——若其判据只涉命名，应转 own-diff 命名检查而非 glob 扩面）。
  - 8791 簇 7 门触发率仅 0.32，**不是**主要成本源，缩面对它们收益小。
- ⚠ 归因保留（反驳者一问）：CREATE-GUARD max 1558s 可能是 CPU 争抢放大而非判据慢（池 4 工+20 核并发），mean 23.4s 也含负载污染——施工前先单工低峰对照重放（A/B 口径见外部引文 [6] 不适用，用本项目对照法）。
- 计时账本自身盲区（引用前必带）：只记 ms≥1.0、链记录无 qid/session 关联键（普查卷自报口径）。
- 复现：union 脚本（本卷运行版）聚合 `.runtime/audit/gate_execution_stats.jsonl` + `worktrees/w{0..3}/.runtime/audit/…`，字段 `ms{gate:ms}`。

## 4. 矿脉四：活性与心跳

### 4.1 "90 秒过期"真实作用域（机判纠偏）

- 判活双轨（`src/zephyr/security/access_control/session_concurrency.py` [INVARIANTS] 段 + L152 `_HEARTBEAT_TIMEOUT_SECONDS=90`）：**pid>0 = PID 存活+TTL 3600s 双判据**；**仅 pid=0 逻辑会话**走 90s 心跳新鲜度。⇒ 底数"会话注册 90 秒过期"覆盖面被夸大：带活进程的会话不受 90s 影响。
- 后果方向**不是"门拒投"而是"保护失效"**：`held_overlap_gate.py` L108-116——持有人会话判死 ⇒ `continue`（锁视为 stale，**不阻断**）。即 daemon 一停 90s 后，HELD-OVERLAP 防连坐保护静默下线；同时 claim 自动释放（heartbeat_daemon 注释：idle 1800s 自动退出→90s 后条目过期→held_files 释放，防僵尸 daemon 永久保活）。
- 提交侧自身：`git_commit.py` SessionRegistry 懒注册（claim_file 懒注册+幂等），无"先注册否则拒投"的门；`--release-only` 双处释放（SessionRegistry + .ailocks）。
- ⇒ 判"已防护"两问实测：谁调用？`session_worktree.py` create 时 `spawn_python_hidden(…heartbeat_daemon…)`（L245-249，在盘与主区两版俱在）。能否改变行为？能——90s 新鲜度被 held_overlap_gate 真实消费。**但** spawn 失败"不阻断创建"（L260）且**计划任务无任何心跳兜底**（`schtasks /query //fo csv` 49 个 Zephyr* 任务，grep -iE "heartbeat|keeper|liveness" = 0 命中）⇒半防护：daemon 死了无人再拉。
- 观测噪声：手工旁路在实跑（09-24 LEDGER 进程表自述 `st-metaq-gc-20260924 的 session_keeper/heartbeat/p3_route`；仓内 src/scripts **无** session_keeper.py 登记件=各会话自带临时件）⇒心跳时间戳存在"手工续 vs daemon 续"双源，跨会话审计区分不了。主区另有 `record_session_start_commit.py`（在册）。
- belt 守护心跳三点对照：`belt_daemon.heartbeat` 内容 ts=18:29:49Z ≤ mtime=18:29:49Z ≤ `date -u`=18:30:16Z ✅（belt≠session 心跳，两码事，防混读）。

## 5. 外部对照引文库（URL+发布方+年份+过闸状态）

| # | 引文 | 关键结论 | ≥2 来源组 | 过闸 |
|---|---|---|---|---|
| 1 | [Managing a merge queue — GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)（GitHub, 文档随版本更新，2025-2026 在档） | 合并队列按加入序成组落地；失败件阻塞其后组直至 removed ⇒ 毒药队首=显式设计风险 | 组A 之1 | 过（结论性对照，不引细节参数） |
| 2 | [How Bors and Google's TAP inspired modern merge queues — Graphite](https://graphite.com/blog/bors-google-tap-merge-queue)（Graphite, 2024） | 现代合并队列谱系=Bors：默认 FIFO 按到达序，priority 仅作有限例外 | 组A 之2 ⇒ **结论①"FCFS 为默认公平、优先级是例外"双源齐** | 过 |
| 3 | [The Origin Story of Merge Queues — Mergify](https://mergify.com/blog/the-origin-story-of-merge-queues)（Mergify, 2025） | Bors 优先级 p 数值化、队列保持到达序主干 | 组A 之3 / 组C 之1 | 过 |
| 4 | [Starvation (computer science) — Wikipedia](https://en.wikipedia.org/wiki/Starvation_(computer_science))（Wikimedia, 2025 修订） | 反饿死标准解=priority aging（等待时间折算进优先级） | 组C 之2 ⇒ **结论③"anti-starvation 用 aging"双源齐** | 过 |
| 5 | [Partition Multi-Tenant Backoff and Retry Budgets Fairly — OneUptime](https://oneuptime.com/blog/post/2026-08-14-multi-tenant-retry-budgets/view)（OneUptime, 2026） | 重试退避预算须按租户分区，防单一复发者霸占共享队列 | 组B 之1 ⇒ **结论②"毒药件退避/让位"与 GitHub 组语义双源齐** | 过 |
| 6 | [mrqueue — gastown (Steve Yegge) pkg.go.dev](https://pkg.go.dev/github.com/steveyegge/gastown/internal/mrqueue)（2025-2026） | AI 代理多会话 MR 队列先例存在（生态同型问题） | 单源，降级为"存在性参考" | 挂（不入关键结论） |
| — | Jenkins/Argo CD/数据库工作队列专项 | 本轮未采到合格 URL+年份双源（Argo sync-wave 属依赖排序非公平策略，硬凑即噪音） | — | **已查无，列长尾 L4** |

**适配性判断**（本项目 vs 上述）：袋=整档快照（非单 PR diff）、写者=多 AI 会话（非人审门）、单写者 serializer 串行落地 ⇒ 与 Bors"审批即入队"形似神异：Bors 的失败=回退重审（袋 dead 后人工 requeue 即同构），Bors 的 p 优先级在本项目**无对应物**——本项目已有的等价物是 lane 二分 + machine 饿死保护 + B5 退避，**缺**的是 aging（等待时长进排序键）与逐秒以下全序（见 §9 C1/C4）。

## 6. 六向寻路台账

| 向 | 内动作 | 外动作 | 发现/已查无 |
|---|---|---|---|
| ① 代码 | dev vs 在盘 `_pick_head` 双读；landing 收敛函数读 | — | B4/B5 已落地；skipped_dirty 语义机判 |
| ② 盘上队列数据 | m1 脚本算分布/pending/dead 三分类 | — | p50=263s…max=12.3h；dead 2397 十三类 reason |
| ③ 审计账本 | sync jsonl×dead 交叉；6 stats 根 union | — | qid 级相关=0；CREATE-GUARD 105k s |
| ④ 注册表 | gate_registry 181 门解析×dev 树×袋样本 | — | 8791 簇=7 门；R5 唯一 ≥90% |
| ⑤ 进程/计划任务 | schtasks 49 项普查；belt 心跳三点 | — | 无心跳计划任务；belt 活 |
| ⑥ 外部对照 | — | 5 组 WebSearch/引文入库 | 结论①②③双源齐；Jenkins/Argo 已查无 |

## 7. 挖矿日志表

| 轮 | 矿脉 | signal/noise+归因 | 产出 | 复现命令 |
|---|---|---|---|---|
| 1 | 一 | signal：B4/B5 dev+在盘双证 ⇒ 母节点底数是修复前旧形状 | §1.1 | `git show dev:scripts/commit_queue.py`+grep |
| 1 | 一 | signal：秒粒度证实、同秒碰撞 21/804 多同会话（良性偏） | §1.1 | m1 脚本 tie 段 |
| 2 | 一 | signal：等待分布 p50=263s/max=12.3h/>24h=0；长尾=metaq 连号簇 | §1.2 | `python .runtime/tmp/mine_dossiers_20260926/m1_queue_stats.py` |
| 2 | 二 | signal：1802/1805 skipped_dirty；431 qid/939 路径；热点=canonical registry | §2.1 | wc/grep + sync 脚本 |
| 3 | 一 | noise 修正："09-24 袋未落地"当前快照无在等同名件 ⇒ 改判死信往返/TTL 抹痕 | §1.3 | m1 pending/dead 段 |
| 4 | 三 | signal：8791=7 门 glob 簇、袋触发率仅 0.32；R5-DIGIT-SUFFIX 0.94 唯一必触发 | §3.1 | `python …/m3_gate_trigger.py` |
| 5 | 三 | signal：CREATE-GUARD 累计 105,154s、max 1558s ⇒ 触发面登记缺失的真成本主 | §3.2 | stats union 脚本（本卷 §3.2 复现行） |
| 5 | 三 | noise 警示：max 含 CPU 争抢右删失，勿直读为"门判据 26min" | 反驳者一问 | 低峰重放（施工期） |
| 6 | 二 | signal：merge-fail 137 件冲突文件与 skipped 热点同峰（canonical 60/112） | §2.2 | dead×sync 交叉脚本 |
| 6 | 二 | signal：qid 级 skipped→死亡相关=0/134 ⇒ 伤害滞后到后继袋 | §2.2 | 同上 |
| 7 | 四 | signal：90s 仅 pid=0；held_overlap 判死=放行（保护静默下线）非拒投 | §4.1 | `sed -n '95,130p' src/…/held_overlap_gate.py` |
| 7 | 四 | signal：daemon 由 worktree create spawn、失败不阻断、schtasks 零心跳兜底 | §4.1 | `schtasks //query //fo csv \| grep -i heartbeat` |
| 8 | 五 | signal：双源结论①FCFS+②退避+③aging 入库；Jenkins/Argo 已查无 | §5 | WebSearch 记录 |

## 8. 防噪音四闸过闸记录

1. **量尺闸**：量尺=端到端吞吐（等待分布+服务成本），未用单点案例代替分布；单点（09-24 袋）经复查降格为"死信假设"（§1.3）。✅
2. **口径闸**：全部时间 UTC 归一（done 内 +08:00 戳经 `datetime.fromisoformat` 解析）；stats 按 6 根 union 防主区低估（口径册教训①）；slow_item 右删失坑绕开（改逐门 ms）。✅
3. **样本闸**：分布样本=done 804（TTL 窗内）/袋 150/dead 2397；tie 统计 804 全量；已标"存活窗下界"偏差方向。✅
4. **指令边界闸**：LEDGER/代码注释/docstring 自述一律作证据数据引用（标"自述"），未据其执行任何写动作；全程零 git 写/零 drain。✅

## 9. 挖后自审闸（三态裁定，量尺=终局全貌）

| # | 候选 | 裁定 | 理由/解锁条件 | 反驳者一问 |
|---|---|---|---|---|
| C1 | created_at 亚秒/单调序号破同秒并列 | **挂起排期**（低优先） | 实测同秒 21/804 且多良性；收益<风险。解锁条件：出现任一"跨会话同秒倒挂且等待入 p95+"实证 | "21/804 是 done 存活窗，reconciler 批同秒被 TTL 抹了？"→ 需 C2 账本先落 |
| C2 | 常设"落地流水账"（landed 永久件含 created/landed/attempts），替代 TTL 截断的 done | **施工** | 饿死分布是全役量尺地基，当前只能测下界=系统性盲 | 成本低（append jsonl）；无 |
| C3 | CREATE-GUARD/CAPABILITY-OVERLAP/REGISTRY-MASS-DELETION 改 own-diff（宪法 §3 第 1 条同型处方） | **施工**（先归因） | 三门合计 ≈164,554 s 链累计、无触发面登记每链全跑；先按 §3.2 噪声警示做低峰单工对照重放定基线 | "mean 23.4s 会不会是 20 核满负荷的排队时间而非门耗时？"→ 重放必带 CPU 占用对照 |
| C4 | machine 车道 aging（等待折算进排序键）+ 合规独占护栏扩 lane=null | **挂起排期** | B4/B5 已消化主要病理；LEDGER 侧曾报"lane=null 防饿死护栏"待裁先例，等他案收敛 | "p99=9.1h 里多少是排队而非服务？"→ 分解账（C2+per-链 qid 关联）出来前不动调度面 |
| C5 | R5-DIGIT-SUFFIX 触发面收缩/own-scope 化 | **施工**（并入 C3 同批门审计） | 唯一"每袋必触发"门（0.94）；但**Owner 明令：只合并/降档/diff 化，夜间不退役**——处方=diff 化 | "0.94 触发率×13725 覆盖，缩面后命名违规漂没？"→ 须重放 100 笔自证（在册口径） |
| C6 | 心跳兜底：daemon spawn 失败告警入 health_alert + 是否设计划任务心跳 | **挂起排期**→**待 Owner 门位** | 计划任务新增=Owner 域（§5 high）；先落"spawn 失败可观测"零风险件 | "90s 判死真实事故率是多少？"→ held_overlap 放行事件计数账缺失，解锁条件=该账落地 |
| C7 | skipped_dirty 漂移消费方（sync 日志→drift watchdog/告警接线），热册脏滞留时长报表 | **挂起排期** | 相关=0/134 证否了"直接致死"假设；但同根热点=真结构性债；接线前需先定"谁有权清主区滞留脏"（owner 责任制已在宪法 §3 第 4 条） | "把 939 路径全接告警=噪音轰炸？"→ 只接 registry 族热点白名单 |
| C8 | 排队键改 qid 全局字典序 / 插队 / --no-verify 类 | **方案封矿** | B4 已裁定 created_at FCFS 为真源秩序；插队/绕门类直接封（任务书铁律+宪法 §2）；封矿理由=同真源不可二主 | — |
| C9 | 恒绿无配对测试的贵门判"疑似判据失效"清单（stats `failed` 字段×execs 比） | **挂起排期**（排期解锁=白天审计窗） | 本轮未算恒绿率（预算）；Owner 明令禁夜退役，只出"疑似"清单 | 无 |

三态计数：施工 3（C2/C3/C5）｜挂起排期 5（C1/C4/C6/C7/C9）｜方案封矿 1（C8）。禁以"现状规模小"封矿——本卷无一条以此为由。

## 10. 长尾矿脉清单

- L1：`dead_reason` 十三类中 "NOTHING_TO_COMMIT 但快照未真应用"（62 件）——快照应用链自证缺失，独立母节点。
- L2：门禁链账本无 qid/session 关联键 ⇒"每次红/每分成本归到袋"不可得（口径册⑪），补关联键是 C2 的伴生件。
- L3：pool 工 `exit=claim_none` 空转轮询频率与 belt 拾取间隔的占空比损失未量化（端到端吞吐的另一半）。
- L4：Jenkins/Argo CD/DB 工作队列公平性策略**已查无**（本轮未采到合格双源引文），留待白班补。
- L5：`record_session_start_commit.py` 与 heartbeat_daemon/session_keeper 三套"活性"机制的职责重叠面（内收判据候选簇）。
- L6：`main_workspace_sync.jsonl` 起点 2026-08-24（受控放松日），其前的收敛失败史无账。
- L7：`.runtime/commit_queue/worktree/` 与 `worktrees/w{0..3}` 两套目录并存（serializer 根 vs 池工根），stats/lease 归属易混读。

## 11. 待 Owner 门位登记项（只登记，不自裁）

1. C6 心跳计划任务兜底（新计划任务=正式通道）。
2. C3/C5 门禁 diff 化施工批（改动门禁行为，Owner 已给"只合并/降档/diff 化"总方针，批次落地仍需门位确认）。
3. C9 若白天审计窗查出"恒绿无配对测试"门集：处置走合并/降档，不在夜间执行。
4. dead 系 2397 件归档净删（注册表/留痕净删=high）。
