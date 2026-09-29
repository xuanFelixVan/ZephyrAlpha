---
created: 2026-09-24
ttl: task_bound
---

# 提交等待 10–20 分钟：全流程取证与修复方案（2026-09-24）

> 调查方式：五车道并行（队列调度／门禁链成本／提交侧锁与治理税／历史战役对账／自测底数），
> 全部数字来自本机日志与代码实测，出处逐条标注。**结论：等待不正常，且可回收。**

## 0. 一句话结论

**不是"提交本来就这么贵"，而是 09-19 打开的一道新通道把整条链的耗时抬高约 6 倍，
且这笔账在遥测里记成 0.0ms，所以三天来没人看得见。**
配套三个放大器：门禁扫的是**共享暂存区**不是你的改动、**56–63% 的提交尝试是白跑的**、
**队首按会话名字母序排队**（不是先来后到）。

## 1. 等待的真实分布（实测）

| 口径 | 数值 | 出处 |
|---|---|---|
| 队列等待（09-22~09-24，n=317） | p50 **5.5 分** / p90 **43.8 分** / p99 **183 分** / 均值 18.4 分 | `.runtime/commit_queue/done/*.json` landed_at − created_at |
| 入队→落地（车道③独立口径，n=131） | p50 **620 秒** / p90 **2625 秒** / max 13517 秒 | 同上 |
| 每日等待 p50 演化（关键） | 09-19 **0.8 分** → 09-21 **8.2 分** → 09-23 **22.1 分** → 09-24 **8.5 分**（p90 39–96 分） | 车道⑤按日重算 |
| 当前积压 | 46 件 / 637 文件，最老 **5.4 小时** | `.runtime/commit_queue/pending/` |
| 通道实际产能 | 峰值 18 件/小时（04:00–05:00），今日全天 7.9–15 笔/小时 | `git log` 分桶 + done 时间戳 |

**你说"平均十几二十分钟"= 均值 18.4 分，完全对得上；但尾部是 3 小时，不是 20 分钟。**

## 2. 一分钟的提交，钱花在哪（单文件实测）

今天 14:20 一次**只含 1 个文件**的提交，门禁链 **64 秒**（两个独立日志互证：
`commit_block_events.gate_chain_ms=64203` 与 `gate_execution_stats.total_ms=64s`）。分解：

| 门 | 单文件批 | 184 文件批 | 性质 |
|---|---|---|---|
| BLUEPRINT-HEADER | 16.7s | 15.6s | **与你改了多少无关**（全仓扫描） |
| BLUEPRINT-FORMAT | 11.8s | — | 同上 |
| GIT-CALL-BUDGET | 8.7s | 7.8s | 同上 |
| CH-BATCH-SIZE | 8.6s | 8.1s | 同上 |
| MUTABLE-CONST-WITHOUT-FINAL | 7.4s | — | 同上 |
| 前五合计 | **53.2s = 83%** | — | — |
| CREATE-GUARD | 0.3s | 80.8s | 这个才随批次涨 |

**判据自证（我的口径也红过）**：前五门在 1 文件批和 184 文件批里耗时几乎相同 ⇒ 成本与你的 diff
无关、与仓库规模有关。**代价的根不在"你提交了什么"，在"门禁看的是整个共享暂存区"**：
`_get_staged_py_files`（`_diff_helpers.py:243-263`）直接返回 `git diff --cached` 全集，
而主区暂存区当前挂着 **543 个 AM 文件**（他会话在途）。所以**你的等待随别人暂存了多少文件而涨**。

## 3. 六个根因（按可回收分钟数排序）

### R1 09-19 新通道：68 台 pre-commit 门禁在全局锁内跑，而且**不计费**（最大单项）
- 现状：`gate_precommit_run` `enabled: true / production`（`config/flags.yaml:94-99`，裁定 341 方案②，
  09-19 Owner 批准），调用点 `git_commit_gateway.py:3474` 位于 `_commit_locked` 内部 ⇒ **持全局锁执行**。
- 里面最贵的一台是 `gate-test`：`pytest tests/ --collect-only -q` 扫 **3720 个测试文件**
  （`.pre-commit-config.yaml:569`），触发面 `^src/zephyr/.*\.py$|^tests/.*\.py$` ⇒ **改一个 .py 就要收集全树**。
  车道②现场目击：PID 21808 为**一个 2 文件的落地件**从 15:06:40 跑到 15:13+ 未结束（≥6 分 24 秒）。
- **遥测黑洞**：该通道失败时写审计用 `_audit_commit_block_event(..., 0.0)`（`gateway.py:3478`）
  ⇒ `gate_chain_ms` 恒为 0。我自己算 24h blocked 时就看到 GATE-PRECOMMIT-RUN 出现 20/19/9 次但 **chain-min=0.0**。
  全链 638 门禁分钟/24h 里**不含这一段**。**这就是为什么三天来没人发现它贵。**
- 时间线证据：链 p50（block 口径）09-19 **47s** → 09-21 **377.8s**；同期每日死信 2 → 116 → 154。

### R2 重复执行：一次交付跑 2.4 次全链、4.0 次预检
- 直连预检（19 台）→ 锁外预跑（15 台）→ 锁内全量 102 台 → pre-commit 68 台，
  worktree 会话还加 2 段（`session_worktree.py:3656/6204`）。实测 **361 chains ÷ 152 落地 = 2.4×**，
  `603 次预检 ÷ 152 = 4.0×`。
- 更亏的是"直连失败再入队"：直连尝试 60–75 秒白做（claim+预检+≤60s 等锁），入队后**同一批门禁第三、四次全跑**。
  今天实测：`st-ailayer-final` 184 文件批在 14:28/14:37/14:46/14:53 **四次各跑约 6 分钟、四次都红**，
  主区 HEAD 从 14:29 冻到 15:00 就是它。

### R3 缓存**设计上必失效**（不是没缓存，是键错了）
- `GateResultCache._path` 键 = `gate_id × own_scope × staged_tree_sha × head_sha × flags_mtime`，
  `lookup` 还要再核 `head_sha`（`gate_cache_preflight.py:164-176`）。
  而 `compute_fingerprint` 用 `git write-tree` + `git rev-parse HEAD`（`:117-135`）
  ⇒ **任何一个会话暂存/落地一次，所有人的缓存全废**。今天 133 笔提交 ⇒ 结构性零命中。
- 实测命中：**cache_hit 仅 87 次/24h**，而 trigger_skip 6541、preflight_reused 2540。
- 并且白名单只覆盖 14 台门 ⇒ **只有 5% 的门禁时间可被缓存，95% 天生不可缓存**（`gate_cache_preflight.py:43-64`）。

### R4 失败放大：今天的尝试里 **63% 是白跑的**
- 24h：死信 233 件 vs 落地 135 件；blocked 链 129–214 次，**烧掉 296 分钟/24h 的整链时间**
  （≈今天全部门禁工时的 100%）。榜首死因：注册表三向合并失败 ×38、GATE-PRECOMMIT-RUN ×15、CREATE-GUARD ×10。
- 失败**发生在链的末尾**（全链跑完 102 台才知道红），且 **77/233 件带 `requeued_from`**（21% 是重投）。
- 214 次 blocked 里最扎眼的两例：`st-backup-cold` 为**1 个文件**连撞 **31 次** BLUEPRINT-FORMAT（31 分钟）、
  `st-ailayer-final` 6 次 ×6 分钟（34 分钟）。**门判得对（那个文件头部格式确实不合规，第 31 次改对了就落地），
  错的是"每次试错都要重付 60–380 秒全链"。**

### R5 排队规则：队首是**会话名字母序**，不是先来后到
- `heads = sorted(pending.glob("q-*.json"))`（`commit_queue.py:1193`，池版同 `landing:1921`），
  qid = `q-<日期>-<session_id>-<序号>` ⇒ 排序主键是会话名；
  `_pick_head`（`:1100-1131`）只给 machine 车道 1800 秒年龄逃生（`:1082`），**interactive 车道内部零饥饿保护**。
- 实测倒挂：**1081 对里有 611 对（56%）逆序**；队首件创建于 12:55，而在册最老件创建于 09:32。
- 后果：字母序靠前的会话（`st-ailayer-*` < `st-align-*` < `st-audit-*` < `st-backup-*`）持续产件即可长期霸占队首，
  而**一个反复失败的靠前会话能把整条通道锁死几小时**（今天 14:29–15:00 即此形态）。

### R6 k=4 通道池今天**只有一路在干活**
- F2/k=4 **确实已落地**（`9ff96cc5c3`，09-24 03:50；`thresholds.yaml:281 = 4`，
  `resolve_pool_workers` `landing:1818`，`drain_queue_pool:1938`，每工独立 worktree + 独立分支 + 锁按 worktree 键控）。
- 但实测**不均衡**：按分支 reflog，w0=15 / w1=6 / **w2=53** / w3=9 次落地（w2 占 64%）；
  我自己核 ref tip：`w0 06:23 / w1 06:12 / w3 06:00`，只有 `w2 14:29`（=当前 HEAD）在推进
  ⇒ **三路工自 06:2x 起没再落地**，而 pending 有 46 件。
- 结果：产能 ≈ 名义 24 件/小时（4 工 × 单件 597 秒），**与池化前的 24/小时上限一模一样**
  ——并行度被单件耗时同比吃掉了。**（口径告警：597s 来自 `slow_item`，该账本只记 >300s 的件，是右删失样本，
  不能当全体中位数用。）**

### R7 治理税占掉四成多通道
- 按 commit message 归类，近 24h **43% 的提交是记账件**（重投 9.9%、落地损伤复原 8.6%、
  chore(integrity/reconciler) 7.3%、记账 5.3%、closeout 4.0%、token 先行批 3.3%、衍生 4.7%）。
  09-18 基线是 24.8% ⇒ **恶化**。
- 典型机制：**token 先行批必须比内容批先落地**（`commit_navigation_playbook.md:105,123`）
  ⇒ 一次交付拆成 k 件，每件各付一次 620 秒等待。今天 `st-align-dirty` 用 **37 个件提了 46 个文件**
  （中位 1.2 文件/件），`st-audit-all` 29 件/37 文件。
- **单元粒度错了**：今日 158 件共 866 文件，**每件中位数 = 1 文件**，78% 的件 ≤3 文件；
  同会话相邻 <20 分钟的"可合并对" **85 对，覆盖 154/158 件**。合批能把件数从 158 压到约 30。

## 4. 修复方案（分三档，每条带判据）

**A 档——先装表，再动刀（半天，零风险，必须最先做）**
- A1 给 pre-commit 通道**记真实工时**：`gateway.py:3478` 的 `0.0` 换成实测毫秒，并把 68 台 hook 逐台耗时
  落 `.runtime/audit/precommit_hook_stats.jsonl`。
  判据：改后 24h 内 `event=precommit_channel_*` 的 `gate_chain_ms` 非零率 = 100%，且能排出 top10 慢 hook。
  **没有这条，下面所有优化都无法验收（也无法证伪）。**
- A2 给落地件加**分段计时**（claim / sync / 快照 / 门禁 / pre-commit / commit / CAS / 收敛主区 / 基线刷新）。
  判据：车道①报的"单件 597s 里只有 110–133s 是门禁链、其余约 460s 无归属"必须归零到各段。

**B 档——治本四刀（预期把单件从 ~600s 压到 ~120s，量级 5×）**
- B1 **把 68 台 pre-commit 通道移出全局锁**（改到锁外预跑 + 锁内指纹采信，与 `gate_preflight` 同构），
  并把 `gate-test`（全树 `pytest --collect-only`）**降级为按 own-diff 导入图**或移入 manual/夜间档。
  判据：①主区 HEAD 在 6 会话并发期不再出现 >3 分钟零推进；②改 1 个 .py 的落地件不再触发全树收集
  （A1 装表后 `gate-test` 单台耗时 p90 < 5s）；③裁定 341 的**执行权不丢**——同一批红件在锁外仍判红（重放 20 件对照）。
- B2 **修缓存键，让缓存能用**：把"全仓扫描型"门的键改成 `(gate_id, 被扫内容哈希)`（不含 HEAD/暂存树），
  own-diff 型门用 `(gate_id, own_scope, own blob 哈希)`；`CONTENT_SCAN_CACHE_WHITELIST` 从 14 台扩到实测 top15 耗时门。
  判据：`cache_hit` 从 87 次/24h 升到 >1500 次/24h；单文件链 64s → **<15s**；
  **红证**：故意改一个被缓存门要读的注册表文件，缓存必须立刻判失（不许假绿）。
- B3 **门禁改 own-scope 的落地面**：CREATE-GUARD / BLUEPRINT-HEADER / BLUEPRINT-FORMAT /
  CH-BATCH-SIZE / GIT-CALL-BUDGET / MUTABLE-CONST 六台（合计约 186 分钟/24h）按 `_split_own_foreign` 收窄；
  CREATE-GUARD 内部把"每类一次 `git grep`"（`create_guard.py:515`）改成**一次 `git grep -f` 全量类名**。
  判据：**重放最近 100 笔提交，逐笔判定与当时 100% 一致**（这条判据 09-18 就写了、至今没执行，是 F3 的欠账）。
- B4 **排队键改 `(created_at, qid)` + 两车道都加年龄逃生**（`commit_queue.py:1193/1100-1131`，并去掉 `[:64]` 截断）。
  判据：倒挂率从 56% 降到 <5%；任何件等待 p99 < 30 分钟。
- B5 **试错成本止血**：廉价且高命中失败的门（BLUEPRINT-FORMAT/HEADER、CREATE-GUARD token 面）
  提到链首并按代价排序，红件应在 **3 秒内**判死而不是 218 秒；blocked 后再投同批文件走**去抖+退避**。
  判据：blocked 平均 `gate_chain_ms` 从 218s 降到 <30s；24h 白烧分钟从 296 降到 <60。

**C 档——结构性减量（要 Owner 拍，因为动的是流程不是代码）**
- C1 **合批/去抖**：同会话 <N 分钟内的多件自动合并（已有 `supersedes`/`depends_on` 元数据可复用），
  并把"token 先行批"改为**同件内 `depends_on` 排序**而非两次独立排队。
  判据：件数/日从 158 → <60，文件/件中位数从 1 → >5。
- C2 **治理税并入主批**：F1 的 fold 虽已落地（`fe47296db5`）但**保留判据被违背**——09-24 仍有 9 笔
  `chore(integrity): post-flush re-register`。判据：该类记账件连续 3 日 = 0，否则 fold 视为未生效。
- C3 **池不均衡排雷**：查 w0/w1/w3 为何 06:2x 后不接单（路径锁 600s？波级 `LandingEnvironmentError` 全体中止
  且无重试计数 `landing:2102-2114`？）。判据：四工落地量占比各 >15%，或明确"当前工作负载下并行度上限=X"并公示。

## 5. 与 09-17 那次提速战役的对账（避免重复提案）

**已落地、不要再提**：F1 fold（部分）、F2/k=4 池（09-24 03:50 已上线）、F3 六台 diff 化（P50 已 <10s）、
F4 生成器并发（57.4s→28s）、F5 DC 预检、claim TTL/孤魂回收、watchdog 状态机、门禁缓存/preflight flag 转正，
**S18-R1~R4 四签已全签**（`ruling_registry.yaml` 318–321 + 总签 333）⇒ **提速不再卡 Owner 签字**。
"24 件/小时 = 串行上限"这个旧结论**已被裁定 334 修订**，现在实测运行在 7.9–15 件/小时，**上限根本不是主矛盾**。

**仍未做（欠账，本报告已并入 B/C 档）**：F3 判据②的"重放 100 笔逐笔一致"**从未执行**；
P-4 YAML 解析缓存（无 lru_cache，CREATE-GUARD 反复解析 1.67MB 注册表）；
own_scope 五台补登记；blobs GC；R-05 watchdog 告警量判据未达（1731–3053 行/日 vs <1000 目标）。
**另有两批 Held 件待处置**：`.runtime/commit_queue/hold_stress_phaseB_20260923/`（31 件，放行条件"池激活+吞吐验证后重跑"——
条件今天已成立）与 `hold_st_gov2/`（2 件）。

## 6. 本轮未能证实（诚实清单）

1. 单件 597s 中约 460s 的**归属未定**（无分段计时，A2 才能定）；`slow_item` 是 >300s 右删失样本。
2. 68 台 hook 的**逐台耗时全无可信来源**（A1 之前只能靠现场目击 ≥6.4 分钟这一个下界）。
3. w0/w1/w3 停摆的**原因未证**（ref tip + reflog 只证明"没干活"，不证明"为什么"）。
4. 直连与池工是否抢同一把锁：代码证据（`paths.py:113` 不匹配 `.runtime/commit_queue/worktrees/w*`）说**不抢**，
   但那是安全性判断，未做实弹验证。
5. 治理税 43% 是 message 正则分类，**±5 个百分点**。
6. 我自己一处口径先错后改：初稿说"前五门占 92%"，重算为 **83%**（53.2/64 秒）；
   另有一版按 UTC 日过滤却按本地时分桶，导致 00–07 时"零门禁链"假象，已重做。

## 7. 我建议的动手顺序

A1+A2（装表，半天）→ B2（修缓存键，收益/风险比最高）→ B1（移出锁 + 杀 gate-test 全树收集，最大单项）
→ B5（试错止血）→ B4（排队键）→ B3（own-scope 落地面，需重放 100 笔判据）→ C1/C3（合批与池排雷）。
**B1+B2 合起来就是你要的"提交一个文件不再等十几分钟"的那一刀；A1 是让它可被证明的前提。**

## 8. 施工进展（15:30– 复命；A 档已开工，与 R6 机理车道并行）

**worktree**：`.worktrees/st-commitspeed-tbl-20260924`（分支 `ai/st-commitspeed-tbl-20260924/task-commit-chain-instrumentation`）
冷启动序列已过：reaper 计划任务 Ready、capability_lookup 反查留审计（`bottleneck`/`gate_execution` 零命中
⇒ 确认没有现成分段表可复用，不是另造第二真源）、热文件 claim 冲突检查=提交链五件**当前零 claim**。

**A1 已施工**（`git_commit_gateway.py`，纯插入）：
① `step5.5` 调用点算真实耗时并传进 `_audit_commit_block_event`——替换原先恒写的 `0.0`；
② 新增 `_append_precommit_channel_stat`，每次通道执行落一行 `precommit_channel_stats.jsonl`
（字段 total_ms / fast_subset_ms / rc / skipped / infra_error）；快段与全段之差≈慢尾成本，
**不逐 hook 调用**（该形态已被在册实测否决："会把套件时长乘 N 倍"，50-commit 挂死教训）。
③ 独立成册而不进 `commit_block_events` 的原因：后者是阈值化设计（只记异常），全量写会破坏其约定。

**A2 已施工**（`commit_queue_landing.py`，`git diff --numstat` = **92 插入 / 0 删除**）：
① `_timed_phase` 装饰器按**方法定义位**挂八台叶子（worktree/sync/conflict/snapshot/prestage/cas/converge/baseline），
零控制流改动、不拆函数名（拆名即丢 COMPLEXITY-GUARD 存量豁免，q-…-0002 死信实证）；
② `_emit_landing_phase_stat` 在 `_pool_process_item` 既有 `finally` 里发射 ⇒ **成功/死信/环境失败三条出口都有账**
（失败件恰恰最该有账），并显式记 `residual_ms`＝残差，即下一轮装表的靶子；
③ 账本按**本工 worktree** 落盘＝池各工天然分账，且新增 `worker` 归因字段
（w0/w1/w2/w3/single）——**k=4 池此前所有账本都不按工归因，这正是"三路工熄火 9 小时"看不见的直接原因**。

**红证（自写盘点脚本也要能红，逐条实测）**：
- A1 两条新测试在 HEAD 旧字节上 **2 failed**（"装表册未生成"／源码里仍含 `0.0` 写法），新码上 2 passed；
- A2 两条新测试在旧字节上 **2 failed**（ImportError `_emit_landing_phase_stat`／"ensure_worktree 未挂分段计时"），新码上 2 passed；
- 两次变异均按**字节**还原并核 sha256 相等（不用 `git checkout --`，防行尾翻转造假差异）；
- 模块归因自证：`cql.__file__` 与 `gw.__file__` 均指向本 worktree（否则会静默测到主仓代码＝典型假绿源）。

**关键运维发现（免掉了 Owner 的重启门位）**：belt 守护带裁定 281 ① 的
"纪元自检 → 安全点原地 re-exec"（`commit_belt_daemon.py:662/760`），其纪元覆盖
`_PRIMARY_SUBTREE=src/zephyr/gov_enforcement` **与** `_CRITERIA_SUBTREE=scripts/governance` 两棵子树
——**A1/A2 分别正落在这两棵里** ⇒ 合入 dev 后守护会在下一轮 drain 结束的安全点**自行换血生效，
不需要手工 kill 守护**（serializer lease 被持时等下一个安全点）。原报告 §7 里"需重启才生效"的担忧撤销。

**待办（本车道）**：① 七套回归 241 项跑完判绿（进行中）；② 走正门入队落地（本仓队列现况拥堵，
预计排队；纯存量件改动不涉及 CREATE-GUARD/翻译登记）；③ 落地后 24h 读表出
"分段耗时 TOP + 残差占比 + 各工利用率"三张账，作为 B1/B2 的立项依据；
④ R6 机理由并行车道给出证/伪结论后，与本补丁合并成一份"装表→定位→动刀"闭环。

## 9. 车道 A 复命（R6 机理）——**其中一条推翻了我先前的因果假设**

| 假设 | 判定 | 证据 |
|---|---|---|
| H1 池是否真被调用 | **PROVEN 是** | `serializer.lease` 的 `renewed_at` 以**精确 60.0s** 步进续租，只有 `_pool_heartbeat_loop` 产生该节律（单传送带是逐件续租）；`thresholds.yaml:281=4` 自 `9ff96cc5c3` 未变 |
| H2 毒药队首（失败件零推进） | **结构成立，但今天不是它** | 两条回退路径都复用同名文件 ⇒ 字母序与队首位置不变、无尝试计数无退避；但 `三向合并` 家族走的是 dead 分支，dead **会给 processed 计数 +1**，归不了零波次 |
| H3 工间不对称（worktree 锁/脏/prunable） | **DISPROVEN** | 四工全部在册、无 locked、无 stale ref lock、无 index.lock；`make_worker_landing`/`range(k)` 对称，无闭包捕获缺陷 |
| H4 记录是否按工归因 | **PROVEN 完全没有** | 账本 kind 只有 dead_letter/alert/slow_item/landing_staleness/registry_drift，**无 env_abort、无 pool_* 任何一种**；`slow_item` 行字段仅 `{ts,kind,qid,session_id,seconds}`。**决定性：belt 守护只 getLogger、不装任何 handler ⇒ 它所有 `logger.error` 走 lastResort→stderr→丢弃**（这就是"三路工熄火"盘上零证据的直接原因） |
| H5 "CPU 悖论"（守护 0.6 CPU 分却落地了三笔） | **DISPROVEN，且推翻我的结论** | 链在子进程侧：`run_gate_chain.py -m pytest --collect-only` 与 **w2 的 `reconcile_generators.py --stale` 串行扇出**（`generate_path_tree`→`generate_domain_doc --all`→`generate_decision_diagram`→`generate_governance_map`）。**这条扇出才是 597–2800s/件的主体，≈ 我先前所称"6 分钟门禁链"的 10 倍** |

**并发度实测＝恰好 1.000**（不是我推测的"1/4 路"，是彻底的 1）：
四件 `created_at` 与实测起始时刻对表——0006 起于 14:30:09、0007 起于 **14:40:06＝0006 的结束**、
0008 起于 **14:57:07＝0007 的结束**、0009 约 15:30 —— **背靠背零重叠**；且这三件路径集**互不相交**
⇒ **路径锁不是串行化者**（50 件 pending 中仅 12 件有任何路径相撞）。
熄火时刻：04:00–05:59 四工全活（11–14 件/时）→ 06:00–06:23 w3/w1/w0 依次退出认领循环
→ 06:22 起只有 w2 再进过 `landing()`。idle 工**不持有工件**（`processing/` 恒为 1 件），
w0/w1/w3 的 `.env.postgres` mtime 停在 06:2x、`.git/worktrees/w{0,1,3}/index` 停在 06:0x–06:2x，
w1/w3 工作区**至今脏**（3/12 件）＝`reset --hard` 再没跑过。
**"为什么这三路停止认领"仍判 UNPROVABLE-BY-DISK**（三个候选：8 轮认领全撞空 /
`os.rename` 抛未捕获的 `FileExistsError` 杀死工线程 / 粘滞 `env_aborted` 冻住 `_reserve_slot`），
三条互斥处方需 A3 出口日志来判。

**车道 A 顺手挖到的第二个虫（我认为优先级高于原 B1）**
1. **`stats_lock` 是 stop-the-world**：锁内跑 `_mark_cascade_stale`（**glob + 重写每一个 pending JSON**）
   与 `_notify_task_board_dead_letter` ⇒ 50 件积压时，**每落地一件都要重写 50 个文件且四工全停**。
   这条与"并发度实测 1.000"直接相容，**很可能就是串行化的真身**（路径锁已被排除）。
2. **`os.environ[ZEPHYR_COMMIT_GATEWAY]` 是进程全局**：`:1501-1502` 置、`:1567-1569` 还原，
   线程 A 的 `finally` 会在线程 B 的子进程运行中途把它摘掉 ⇒ **FORGED-GW-MARKER / POST-COMMIT-GUARD 暴露面**，
   且这个 bug **是 k=4 池化之后才可达的**（单通道时代无并发线程）。属安全性缺陷，优先级应按高缺陷走。
3. 游离的 post-commit 再生子进程（父死子活）持有句柄 + worktree 内 `.runtime/locks/regenerate_global.lock`
   ⇒ 该 worktree 下一次 `_sync_worktree` 的 `clean -fd`/`reset --hard` 失败 ⇒ `LandingEnvironmentError`
   ⇒ 粘滞 `env_aborted`。**这是"为什么恰好是那三个 worktree 死了"的最佳候选。**
4. `_PATH_LOCKS` 模块级字典从不清理 ⇒ 10 小时守护无界增长；`_recover_orphans` 只捕 `OSError`，
   同名 qid 文件已在 pending 时孤儿会永久卡在 processing。

**因此修正 §7 的动手顺序**（原判据不变，只改优先级）：
A3 出口日志（已随本批施工，见 §10）→ **D1 `stats_lock` 出锁化**（把 `_mark_cascade_stale`/死信通知移出临界区）
→ **D2 修 `ZEPHYR_COMMIT_GATEWAY` 线程泄漏**（改参数透传或 thread-local）→ B2 缓存键 →
B1 通道出锁 + 杀 `gate-test` 全树收集 → **B0 把衍生再生扇出移出落地窗口**（H5 新证据：这才是每件大头的 10 倍）
→ B5 → B4 → B3 → C1/C3。
**车道 A 给的复现/验收判据（照抄进修池批）**：≥8 件路径两两不相交的 pending 下，每 8s 采样
`processing/` 连续 5 分钟，要求**最大并发 ≥2** 且 30 分钟内 **≥2 条 `serializer/commit-queue-w*` 分支**新增 reflog；
反证形态＝任一件实测起始与上一件实测结束同秒即回归。
