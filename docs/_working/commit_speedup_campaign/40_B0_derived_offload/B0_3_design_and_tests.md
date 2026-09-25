---
ttl: task_bound
---

# B0_3 · 衍生工作下线设计 + 收敛性证明 + 红测与回滚

> 支点事实（B0_1/B0_2 已证）：`GATE-NO-COMMIT-DERIVED` 已把生成文档禁入提交面，
> 落地 worktree 里生成的衍生产物既不会提交、又被下一件 `reset --hard` 丢弃（`commit_queue_landing.py:88-90` 自认）。
> ⇒ **落地路径上的衍生再生 = 纯负收益**（付 CPU/IO 争用与锁，产出零）。这是 M2 的正当性来源，不是"偷懒异步化"。

## 1. 三分法落位

| 去向 | 对象 | 机制 | 为什么可以 |
|------|------|------|-----------|
| (a) 认领即分离 detached | `_refresh_integrity_baseline_main_repo`（`:1448-1475`，180s 超时）；post-commit regen 触发器外壳（A3） | 落地器 finally 段把"意图"写 dirty ledger，随后由 belt 守护的 idle 事件消费（`commit_belt_daemon.py:808` 已是 watchdog Observer 事件驱动） | 基线正确性改由 (c) 侧的"按 HEAD 派生"保证，不再靠"及时注册" |
| (b) 事件触发 reconciler + 去抖合并 | 30 生成器扇出（`reconcile_generators.py:605`，CPU mean 97.3s/次） | **去抖窗 N=45s 或 M=50 dirty paths 先到者**，且只在事件上判定：①一轮 drain 结束（队列 idle）②`_advance_dev` 之后 ③会话收尾 `cmd_merge` 之后 ④任何门请求 revalidate。**禁 cron/Timer/sleep-loop**（宪法运维红线第 3 条），无新事件即不跑，靠尾事件天然收敛 | 再生是幂等全量扫描（`_is_stale@:558` 的 mtime 谓词即天然 dirty 判据），合并 100 次触发与 1 次结果相同 |
| (c) 保留同步 | ①改名后 depgraph 重建义务（RENAME-DEPGRAPH-SYNC）②`GATE-RULES-INTEGRITY` 的判据面 ③`MODULE-ID-CONSISTENCY`/`GATE-BATTLE-MAP-ALIGNMENT`/`DECISION-MAP` 族（判据直接以图/册为对象）④`gate-no-commit-derived` | ①③类**改为按 git tree/HEAD blob 读**（范式=`errcode_consistency_gate.py:45/:54`），读时自证新鲜，无需再生；②类同理；④本就免疫 | "同步再生"从来不是正确性要求，**"读到的是不是本次提交的内容"才是**——把门 repoint 到 HEAD 面即可两头都赢 |

## 2. 必答的正确性问题：门读到陈生衍生件，判据会不会变？

会变，且只有 **4 类**会变（B0_2 全表逐门判过）：

1. `GATE-RULES-INTEGRITY`：`register` 用 HEAD blob、`check` 用工作树 hash（`:199-229`）。基线滞后 ⇒ 下次提交假红 TAMPERED。**这就是今天 per-item 同步 180s 刷新的唯一理由**；M1 的正解不是"异步刷新"，而是"让 check 也按 HEAD 派生"，则刷新义务消失（连异步都不需要）。
2. `MODULE-ID-CONSISTENCY`：读 `docs/03_modules/template_registry.yaml` 磁盘册 ⇒ 旧册可致放过/误拦。
3. `GATE-BATTLE-MAP-ALIGNMENT` / `MAP-ALIGNMENT` / `DECISION-MAP`：以生成图/源 YAML 为对齐目标 ⇒ 在案教训是 DECISION-MAP 的 hash-miss 静默回退曾以陈旧缓存产假阳。**本车道据此立判据：禁止"读不到/读得旧就回退默认"的第三种分支**，要么 HEAD 面自证，要么显式 revalidate 后二次读。
4. depgraph 族：读 Postgres（`apply_depgraph` 事件直写），**不受文件再生扇出影响**，但改名重建义务必须留在提交面。

其余在进程门（BLUEPRINT-* / IMPORT-* / CH-* / GIT-CALL-BUDGET / REGISTRY-MASS-DELETION / CONSUMERS-ACCURACY / CREATE-GUARD …）走 `_read_staged_file`/own-diff 面，**再生下线零判据影响**。
未知面如实登记：121 个观测到执行的门 vs 180 条登记，差集未静态证明不读衍生件（B0_2 `unknowns`）。

## 3. 幂等 + 收敛性证明计划

**不变式（要证的两条）**
- **L-1 无丢**：每一次"输入变新于产物"的事实，最终都产生一次覆盖该输入的再生执行。
- **L-2 无环**：再生自身不再触发生成（沿用 `post_commit_regen_yaml.py:134-153/:180-197` 的产物阻断，加机检）。

**记账件（新增 1 个 ledger + 1 个 state，均走 `safe_write_text` CAS）**
- `.runtime/derived_dirty/ledger.jsonl`：`{ts, trigger(qid|commit|merge), input_paths[], head_sha, generator[], reason}` —— **先写意图，再决定要不要 spawn**（现状是先决定、丢弃时零留痕：近 7 日 81 合格触发 vs 20 份日志 ⇒ ≈75% 静默丢，C4）。
- `.runtime/derived_dirty/state.yaml`：按生成器 `{dirty_since, dirty_count, last_attempt_ts, last_success_head, last_success_mtime_ge_input, consecutive_failures}`。
- 清除条件（唯一）：生成器 rc=0 **且** 重跑 `_is_stale(entry)==False`（用生成器自身谓词做后置校验，不另造判据）。
- 事件触发点（全部现成事件，零新增定时器）：drain idle、`_advance_dev` 后、`cmd_merge` 后、belt 守护 watchdog poke、以及**任何第 2 节 4 类门的 revalidate 请求**。

**卡死检测（这是今天最缺的一块，现网零证据）**
| 信号 | 阈值 | 动作 |
|------|------|------|
| `dirty_since` 账龄且 `dirty_count` 未降 | > 1800s | 写 `bottleneck_ledger.jsonl kind=derived_stale`（沿用 `_ledger_*` 通路），复用 `bottleneck_backlog_alert_state.json` 的去抖 |
| `consecutive_failures` | ≥ 3 | `kind=derived_stuck` + 任务板打标（`_notify_task_board_dead_letter` 同通道） |
| `last_success_head` 落后 HEAD ≥ 5 次移动 | 5 | 升 high tier，Owner 门位（`risk_tier_registry.yaml`） |
| 再生锁持有者 PID 死亡或锁龄 > TTL 1800s | 既有 | 保留现抢占逻辑（`:194-210`），但抢占必须**同时**落一条 `stolen_after_ttl` 记录 |

**证明义务（施工时逐条交证据，不接受"我看了一次是好的"）**
- P-1：构造 8 连击 YAML 输入变更（burst），断言 ledger 8 条全在、最终每生成器 `last_success_*` 覆盖最大输入 mtime（证 L-1）。
- P-2：在 spawn 前 kill 掉持有者，断言下一次任意事件即恢复（证不依赖 TTL 走运）。
- P-3：`ZEPHYR_SKIP_REGENERATE=1` 全窗跑，断言 dirty 意图仍完整入册（逃生通道不得变成丢件通道）。
- P-4：产物→输入闭环用例（policies.yaml 型），断言 0 次自触发（证 L-2）。

## 4. 前三手 · 红测（现码必红、改后必绿）与回滚

### M1 integrity 基线改「按 HEAD 派生」（删 per-item 180s 同步子进程）
- **红 R1a**：落地一件触碰 `docs/01_policies_and_standards/rules/*.yaml` 后，立即在**基线未刷新**的窗口跑 `validate_rules_integrity.py`（check 态），断言 exit 0。现码红：check 走工作树 hash，基线由上一件的 `--register` 注册，刷新滞后即假红（B0_1:B4 尾段实测 mean 46.1s、max 300.7s 就是这个同步代价）。
- **红 R1b**：monkeypatch 记录 `commit_queue_landing._refresh_integrity_baseline_main_repo` 的调用，断言该子进程**不在** `_pool_process_item` 关键路径内（现码红：`:1462` 直调，`:1468 timeout=180`）。
- **绿条件**：check 以 `_hash_git_head` 为准；工作树面降级为 warn-only 观测。
- **预期收益**：40–46s/件（尾段 max 301s 归零）。
- **回滚**：flag `git_operations.integrity_baseline_mode: head|snapshot`，出厂态=`snapshot`（现行为），翻转须 Owner 门位（flag 出厂翻转是 high tier）；回滚=改一个 YAML 值，不动码。

### M2 落地 worktree 内不触发再生，改主区单点事件触发 + 去抖
- **红 R2a**：在 serializer/worker worktree 形态下 commit 一个生成器 YAML 输入源，断言 (i) 无 `Popen --stale` 于该 worktree 产生（现码红：`post_commit_regen_yaml.py:236` 以所在 worktree 的 `_REPO_ROOT` 起子进程），(ii) dirty ledger 有且仅有 1 条（现码红：今天**根本没有 ledger**，丢弃零留痕）。
- **红 R2b**（去抖不丢）：45s 窗内连投 5 件，断言 spawn=1 而 ledger=5，且尾触发仍覆盖第 5 件输入。
- **红 R2c**（跨工不串）：4 工并行各触发 1 次，断言主区只跑 1 次扇出（现码红：`reconcile_generators.py:86 _REPO_ROOT=parents[2]` ⇒ 锁落在各自 worktree 的 `.runtime/locks`，C3 的"全局锁"其实是每 worktree 一把）。
- **预期收益**：关键路径只省 A3 的 0.1–1s；**真实收益是争用面**：消掉 4×97.3 CPU-s/触发的同窗爆发与 `domain_doc`(78.7s) 串行鲸鱼，按 4 工实测并发系数曾 1.000 的历史教训，此项**必须先有 A2 分段计时器再认账**，本文不背书秒数。
- **回滚**：flag `git_operations.regen_scope: main_only|any_worktree`，出厂态=`any_worktree`；regen 本体有既成逃生口 `ZEPHYR_SKIP_REGENERATE=1`（但按 P-3 要求，它只允许抑制执行、不允许抑制记账）。

### M3 钩链瘦身（reference-transaction 并进程 + Qoder tracker 出锁）
- **红 R3a**：直跑 `.git/hooks/reference-transaction prepared`（dev 前进合成 stdin），断言其 git 子进程数 ≤1 且墙钟 ≤0.5s。现码红：**5 个子进程 / 1.25s**（PATH shim 计数法，探针已留在 `.runtime/tmp/cs-tbl/b0_probe/t2_rt.py`）。
- **红 R3b（治理不得放松）**：伪造 `[GW: not_a_real_sid]` 的 dev 前进移动，断言仍 exit 1 且落审计；真回退仍放行。合并 5 个 git 调用为 1 次 `git log --format=%H%x1f%P%x1f%B` 后此条必须仍绿。
- **红 R3c**：post-commit 全链每 commit 的**未计时黑盒**必须可观测——断言存在 `post_commit_hook_ms` 一类分段记录。现码红（零留痕，`|| true` 全吞，A5）。
- **预期收益**：2–4s/件（每件 ≥2 次 ref 移动）+ 把 A5 从 UNKNOWN 变可知。
- **回滚**：钩子是被 `.git/hooks/*` 软装配的文件 ⇒ 回滚=还原旧文件（源在 `scripts/governance/git_hooks/`，安装动作显式）；`reference-transaction` 与 `post-commit` 各自独立，互不牵连。

## 5. 与其他车道的接口（勿重复施工）

- **A2 分段计时器未落地 ⇒ 本车道 630s/件 残差不可归因**（README 表末行）。M2 的收益证明完全依赖 A2 的 phase 计时，二者是**串行依赖**，不是并行选项。
- D 系（门禁地板 81.2+0.96×文件）与 B0 无交叠：B0 只碰 ST-16/18/20，不碰 ST-07 的门内实现；`CREATE-GUARD`/`BLUEPRINT-HEADER` 两慢门留给 D 系。
- 派工面铁律：**不得为省秒而削弱任何门的判据**（R3b 是为此立的防回归哨）；衍生件"禁入 git"的既有不变式（`GATE-NO-COMMIT-DERIVED`）在本设计下更强而非更弱。
