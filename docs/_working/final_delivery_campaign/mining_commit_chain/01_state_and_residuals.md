---
ttl: task_bound
title: "提交链治本深挖 R2——现状快照与五残留逐条 HEAD 复核"
session: st-finaldel-m1-20260929
---

# 01 现状快照与五残留复核（全部 HEAD/工作树+审计账本实测，2026-09-29）

> 性质：只读取证。行号以 HEAD 工作树为准；账本读数取自 `.runtime/audit/` 与 `.runtime/commit_queue/`（只读聚合）。
> 前置真源：`docs/_working/commit_speedup_campaign/99_FINAL_REPORT.md` §二五残留；`60_deep_dive/deep_dive_r1.md`。

## 一、现状快照（实测读数）

| 指标 | 实测 | 出处 |
|---|---|---|
| 门禁链 P50 | 9/26=18.5s、9/27=15.6s（Owner 呈报"15-18s"精确复现）；9/28-29 p50≈0（preflight 采信/缓存命中占比升高） | `.runtime/audit/gate_execution_stats.jsonl` 按日聚合 |
| precommit 通道 | 9/25 n=48 p50=90.1s p90=200.7s；9/26 n=30 p50=101.8s p90=183.4s；**rc!=0 占 98-100%**（9/24-29 逐日同形）；fast_subset 常占 total 的 99%（样例 44078/44312ms，rc=1 短路 Phase-B 未跑） | `.runtime/audit/precommit_channel_stats.jsonl` |
| 通道阻断（GATE-PRECOMMIT-RUN） | 按日 9/24=23、9/25=62、9/26=43、9/27=18、9/28=16、9/29=7；阻断真实工时已记账（A1 装表后 gate_chain_ms 非零：9/25 单日 4053s） | `.runtime/audit/commit_block_events.jsonl` |
| 通道阻断 hook 谱（账本全史） | **ruff-format 37、ruff 36**、gate-algo-flow-marker 28、gate-any-abuse 26、gate-naming 20、gate-no-commit-derived 16——前两名合计 46%，全是确定性秒级检查 | 同上（event=precommit_channel_blocked 的 hooks 字段聚合） |
| 队列等待 | 9/28 p50=45.0min p90=80.4min（=Owner"35-88min"）；**9/29 恶化 p50=107min p90=157min max=234min** | `.runtime/commit_queue/done/*.json` landed_at−created_at |
| 队列深度（09-29 实时） | pending 13 / processing 4 / dead 440；pending 车 lane=chief_dispatch×5+interactive×7（chief_dispatch 非 _item_lane 认识值，按 interactive 处理） | 目录实测 |
| landing 相位 | **gates 相位占 74.1%（9/28，mean 448s）→ 76.1%（9/29，mean 593s）**；residual（未归属残差）p50 已塌缩至 1.9-8.9s | `.runtime/commit_queue/worktrees/w*/.runtime/audit/landing_phase_stats.jsonl` |
| flag 三件 | immutable_tree=**true**（已翻）、gate_result_cache=enabled:true（生产）、regen_scope="any_worktree"（未翻）；工作树==HEAD 无脏 | `config/flags.yaml:48/52/99-102` + `git status` |

**关键结构性读数**：门禁链 P50 15-18s 的目标已达成（S1 生效），但单件 landing p50 仍 118→600s 且 74-76% 压在 gates 相位——差额主体=**precommit 通道（88-100s）× 首过失败重入队循环（rc!=0≈100%）+ 全局锁等待（零插桩）**。夜战排队的病根不是调度器，是"每件平均要死 1 次以上才落地"。

## 二、五残留逐条复核（HEAD 证据）

### 残留1：重试环/廉价门前置 —— 半收，主病灶已定位为 ruff 族"入队不检、落地才死"

- 已收：D3 Phase-A 快败子集在岗（`gateway:3491-3508`，首败短路全通道）；簇1 CREATE-GUARD 塌缩（p50 4.1→0.7s）；B5 attempts 退避在岗（`commit_queue.py:203-204` 阈值3退避/5死信）。
- 未收（本次定谳）：**enqueue 预检不跑 ruff/ruff-format**（入队预检=in-process gate 面 `scripts/commit_queue.py:893` commit_preflight，pre-commit 通道钩子只在落地侧跑）⇒ ruff 族违规必然烧完一整轮 landing（gates 相位 mean 448-593s）才第一次见红，requeue 后再烧一轮。decisions_log 19:5x 行已有"教训入册"（人工跑两连），但**未机械化**——首过率 9% 的直接来源。阻断谱前六名全部是秒级确定性检查（见快照表），不存在"必须到落地侧才能判"的判据。
- 处方：Rx-1（02 卷）。

### 残留2：hook 成本与件数脱钩 —— 通道面 own-scope 已收，剩余=全仓自扫描 hook 的固定地板

- 已收：通道 own-scope 临时索引在岗（`gateway:3367-3372` GIT_INDEX_FILE=read-tree HEAD+仅本提交文件；pass_filenames 型由 --files own 限定）——"扫他会话 staged 连坐"在通道层已不存在。L2 层 S1 不可变树在岗（见残留4）。
- 未收：**单次 pre-commit 调用的固定地板 ≈ 30-45s**（T10 实测单 hook 冷启动 0.49s×69≈34s；样例 Phase-A 34 台跑 44s）。现形态绿路径要跑**两次调用**：Phase-A（57 台 − 20 慢尾 − 3 SKIP=34 台）+ Phase-B 全量 57 台 ⇒ 绿路径 91 台次/件。慢尾 20 台（`gateway:388-411`）全是全仓自扫描（gate-test=pytest 全树收集、gate-17 孤儿扫描、gate-zr/errcode 等），与件数无关。
- 处方：Rx-3/Rx-4（02 卷）。

### 残留3：precommit 超时 ×N —— 数值已变，仍在锁内（本问核心，见 §三 Q1 详证）

- `1200s×3` 已不存在：HEAD 为 `_PRECOMMIT_RUN_TIMEOUT_S=900`（`gateway:383`，自 aca8c71fad5 引入即 900）；Phase-A 超时 300s（`gateway:3545`）；变异重跑 attempts=2（`gateway:3296`，仅变异时）；infra_error=warn+放行不重试（`gateway:3443-3455`）。理论最坏=300+900+900=2100s/次调用。
- **仍在全局锁内**：调用链 `gateway:2592 with _GlobalCommitLock` → `:2638 _commit_locked` → `:3171 _resolve_commit_result` → `:3667 _run_precommit_channel`（step5.5）。TRAE-079 铁律1 注释（`:2543`）明示 [gate→stage→commit] 整体在临界区。
- **锁键控拓扑（精细）**：`strip_session_worktree` 只剥 `.aidrafts`/`.worktrees`（`src/zephyr/shared/io/paths.py:100-114`）⇒ ①主区直连（git_commit.py 直连/worktree 会话 merge/记账件）共享**主仓唯一锁**，通道 88-100s 全部计入锁持有时间；②k=4 队列工的 worktree 在 `.runtime/commit_queue/worktrees/w*`，**不**被剥 ⇒ 各工持**私有锁**，门禁段真并行——工内串行但互不堵主区。故"68 hooks 在全局锁内"今 Reads：主区路径=是；队列路径=在工私锁内（等价于占用工人 88-100s/件）。

### 残留4：S1 生效 —— 已完成（flag 已翻，验收链在案）

- `config/flags.yaml:52 immutable_tree: true`（工作树==HEAD）；翻转 commit=`ed935c29afd`（2026-09-27 00:10 +0800，"Owner 09-26 已批准"，回滚=同词反向 replace）。
- 接线：`gateway:219-235` 直读 YAML（每次调用即生效、无需重启）；`:3076` 门禁链跑 CommitTreeView 替身；15 台故意读全索引门经 `SHARED_INDEX_WITHOUT_OWN_SCOPE` 分道回本体（`commit_gates/_tree_view.py:115-133`）。
- 验收：`90_verification/s1_acceptance_20260929.md`——30 笔×100 台×2 口径=6000 verdict，**100/100 台 verdict/hits/detail 三零漂移**；selfcheck100（100 笔/1522 文件/byte_mismatch=0/worktree_reads=0）；读面收益 7.1x。效果：门禁链 P50 64s→15.6-18.5s（<25s 目标达成）。
- 详见 03 卷裁定。

### 残留5：未解释 123s/笔 —— 装表后已重新定案：残差塌缩，大头在 gates 相位内部的三个未分解段

- deep_dive_r1 的"residual 344s mean/未解释 123s"是在 A2 八相位装表**初版**口径下量的。当前账本：**residual p50 已塌缩至 1.9-8.9s**（9/26-29 逐日），残差之谜形式上已解。
- 但 time 去了哪也清楚了：**gates 相位占 74-76%**（mean 448-593s/件）。gates 相位=一次 `gateway.commit()` 全程（`commit_queue_landing.py:2811 _record_phase(self,"gates",...)`），内部含三段**互不分解**的成分：①全局锁等待（零插桩，见 §三 Q2）；②L2 门禁链（P50 15-18s，有账）；③precommit 通道（P50 88-100s，有独立账）＋ git add/commit。②+③ 合计 ~110s，对 mean 448-593s 的差额=锁等待+首过失败在 gates 相位内的重复消耗+同窗并发互等。
- 处方：Rx-2（锁等待插桩，gates 相位三分）为 R2 定案前置。

## 三、深挖五问结论速览（处方细节在 02 卷）

| 问 | 结论 | 处方 |
|---|---|---|
| Q1 | 通道仍在主仓全局锁内（直连路径）；900s+300s(快段)+×2 变异重跑；廉价优先仅以 Phase-A SKIP 反选形态存在（配置序未动，gate-test 居 32/57）；Phase-A 首败短路=部分 fail-fast，Phase-B 仍跑满全链才报红；通道面 own-scope 已收 | Rx-1/3/4/6 |
| Q2 | 锁等待零插桩（唯一落账是 GatewayError 异常文本）；gateway 缺省 60s 仍在（`:243`）但两个消费方都改写（落地侧 300s `commit_queue_landing.py:137`、CLI LOCK_TIMEOUT→自动入队 `git_commit.py:1305-1323`），"盲重试空转"已消，锁等待时长本身仍无账 | Rx-2 |
| Q3 | FCFS 已在岗（`commit_queue.py:1656-1701`，(created_at,qid)+车道优先+machine 1800s 防饿）；**无优先级字段**（item 键=qid/session_id/created_at/branch/base_head/message/files/meta，实测 12 份 pending 全无 priority）；无夜窗错峰/合批机制（仅同会话 C1 去抖 20min `:664`） | Rx-5 |
| Q4 | immutable_tree=true 已翻（验收链满分）；gate_result_cache=ON+新键已live（T7 无独立 flag）；regen_scope=any_worktree 未翻 | 03 卷 |
| Q5 | 统一册 HEAD 183 条：own_scope true=29/false=124/null=2/missing=28（27 条 deprecated 锚点居 missing）；S1 后"扫全暂存区"的实害面收敛为 **15 台 SHARED_INDEX_WITHOUT_OWN_SCOPE（设计如此）**+20 台慢尾全仓自扫描 hook；ERRCODE（GATE-ERRCODE-CONSISTENCY）own_scope=false、居 15 台名单、precommit 侧居慢尾清单（Phase-A 跳过、Phase-B 每次全跑 pytest 全仓对账） | Rx-7 + T14 14 条终裁仍悬（Owner 门位） |
