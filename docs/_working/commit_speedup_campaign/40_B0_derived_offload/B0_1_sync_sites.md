---
ttl: task_bound
---

# B0_1 · 提交/落地可达的**同步**衍生工作点清单（file:line）

> 口径：`锁内`= 在 `_GlobalCommitLock`（`git_commit_gateway.py:495`，按 project_root 键控）持有期间执行；
> `件内`= 在落地器单项窗口（`_pool_process_item` 的 `_item_t0`@`commit_queue_landing.py:2155` → 记账@:2218）内执行；
> `钩内`= `.git/hooks/*` 同步执行（git commit 进程返回前）；`异步`= 已 detached，不在关键路径。
> 行号 = 本车道 2026-09-24 在主仓 `dev` 盘实测（S1 表的旧编号已随码位移，冲突以本文为准并注明）。

## A. 钩内同步（每次 ref 移动 / 每次 commit 都付）

| # | 位置 | 做什么衍生/治理工作 | 范围 | 实测成本 |
|---|------|--------------------|------|---------|
| A1 | `.git/hooks/reference-transaction:4-6` → `scripts/governance/git_hooks/reference_transaction_guard.sh:79`（`while read` 逐行）/ `:129,:132` 两次 `merge-base` / `:145` `git log -1 %P` / `:150` `git log -1 %B` / `:166` 读 `session_registry.json` 全册 grep | 伪造 `[GW:` 标记与分叉移动审查 | **每次 ref 事务都被调用**（含非 dev 分支） | dev 前进 1.25s(n=3)/次；非 dev 0.39s；真回退 0.44s；PATH shim 计数=**5 个 git 子进程/次** |
| A2 | `.git/hooks/post-commit:3`（`git lfs post-commit`） | LFS 探测 | 每次 commit | 未单列（<0.3s 量级，UNKNOWN） |
| A3 | `.git/hooks/post-commit:9-11` → `scripts/governance/git_hooks/post_commit_regen_yaml.py:99`（`git diff HEAD~1 HEAD` 子进程）`:115/:134`（两次 `yaml.safe_load` 全册）`:156`（TTL 判活）`:167`（写 `reconcile_stale.pid`）`:236-247`（`Popen --stale` detached） | **衍生再生的同步外壳** | 锁内+钩内（gateway 恒 `--no-verify`，post-commit 仍在 `git commit` 进程返回前跑完） | 同步段 0.1–1s（`ZEPHYR_SKIP_REGENERATE=1` 冷启动实测） |
| A4 | `.git/hooks/post-commit:16-17` → `post_commit_guard.sh:51`（`git log -1 %B`）`:70`（`rev-parse --git-common-dir`）`:114`（全册会话键 grep）`:168-171`（逐报告文件 4 次 grep）`:199/:224`（可能 `git reset --soft HEAD~1`） | 非 GW 提交回滚（会改 dev/HEAD） | 锁内+钩内 | 未单列计时；17 处 git 调用为静态上界，UNKNOWN |
| A5 | `.git/hooks/post-commit:20-21`（Qoder AI tracker：`ELECTRON_RUN_AS_NODE=1` 拉 **node 运行时**，`2>/dev/null \|\| true`） | 外部 IDE 记账 | 钩内、**全静默零留痕** | **UNKNOWN**（无任何计数器；本车道判定为残差候选之一） |
| A6 | `.git/hooks/post-checkout`（20 行）/`post-merge`（3 行） | 落地器 `_sync_worktree` 的 `reset --hard` 会触发 post-checkout | 件内 | 未测，UNKNOWN |

**关键判定**：A3 触发的再生**本体是 detached**（`reconcile_generators.py:605` 由子进程跑，`_invoke_parallel@:396`，`_MAX_WORKERS@:73`）——
即"几分钟串行衍生工作"并不在关键路径上排队，而是**与其余 3 个 worker 抢 CPU/IO**。二者的处置完全不同，故 B0_3 分两手。

## B. 锁内 / 件内同步（gateway 与落地器）

| # | 位置 | 做什么 | 范围 | 成本 |
|---|------|-------|------|------|
| B1 | `git_commit_gateway.py:2329 commit()` → `:2528/:2569 _gate_t0` | 102 门全链 | 锁内 | Σ逐门 med 39.8s / mean 63.7s；单件墙钟 med 81.3s |
| B2 | `:3189 _run_precommit_channel`（调用点 `:3475`，在 `_resolve_commit_result` 内）| 68 个 pre-commit hook 子进程通道（`_pre-commit-config.yaml` 内 6 个 hook 直接读衍生/基线：`gateway-post-commit-ritual`、`gate-rules-integrity`、`gate-no-commit-derived`、`gate-14-authority-registry`、`gate-22-load-path-integrity`、`gate-vocab`） | 锁内 | 单 hook 直跑实测 0.3–0.8s；68 个的冷启动税混测在 B1 内 |
| B3 | `:3718` `git commit --no-verify` → A2–A5 全链 | 见钩内 | 锁内+钩内 | 计入门禁链（`:2589 _total_ms` 之前） |
| B4 | `commit_queue_landing.py:1448-1475` `_refresh_integrity_baseline_main_repo`（`:1462 subprocess.run`，`:1468 timeout=180`，跑 `meta/validate_rules_integrity.py --register`） | **每件一次同步刷新 rules_integrity_db 基线** | 件内（收敛之后） | 尾段实测 mean 46.1s / med 6.2s / max 300.7s（含 bookkeeping） |
| B5 | `:1390 _converge_main_workspace` → `:1361 _converge_one`（`:1341 _read_blob_bytes`、`:1327 _worktree_matches` 每路径各一 git 子进程，超时 `:126`） | 主区工作树快进（衍生文件**不在**收敛清单内） | 件内 | 收敛段 med 0s（记录稀疏），max 1887s |
| B6 | `:940 _sync_worktree`、`:885 ensure_worktree`、`:1165 _apply_snapshot`、`:1208 _prestage_snapshot` | worktree 对齐+快照装填+预暂存 | 件内 | 归入 ~630s UNKNOWN 段 |
| B7 | `:1268 _advance_dev`（`update-ref` CAS） | 触发 A1 钩子 | 件内 | =A1（1.25s） |
| B8 | `:1825 _replay_commit_without_gates` / `:1860 _commit_tree_same_message` | CAS 重放（不重跑门禁，但仍触发钩链） | 件内 | 未观测 |
| B9 | `:1477 _get_gateway`（每工首次构造 gateway：读名册 + 注册 102 门 + import） | 派生清单/注册表装载 | 件内（池内按工复用） | 未拆表，UNKNOWN |

## C. 已是异步/事件触发的（本车道确认为"非关键路径"，但机制有洞）

| # | 位置 | 说明 | 洞 |
|---|------|------|----|
| C1 | `git_commit_gateway.py:1063 run_post_commit_reconcile` → `:1034/:2323 *_async`（调用点 `:2610`，在 `_total_ms` **之后**） | detached worker 跑 30+ reconciler；`ZEPHYR_RECONCILE_SYNC=1` 才同步（`:1081` worker 内直接 return 防递归） | worker 的 auto-commit 又是一件全链提交（git log 可见 `chore(reconciler): batched auto-commit`）→ 放大环 |
| C2 | `reconcile_generators.py:499 reconcile_async`（apply_*.py 写完 DB 后调用） | 非阻塞 | 同上再生锁 |
| C3 | 再生全局锁 `reconcile_generators.py:133-135`（`_LOCK_DIR = _REPO_ROOT/.runtime/locks`，`_REPO_ROOT = parents[2]`@:86，TTL 1800s，`:162 _acquire_regen_lock`/`:229 release`） | drop-not-queue（`:616-625` 抢不到即 `skipped_dup` 返回） | **锁按 `_REPO_ROOT` 键控 ⇒ 在 serializer/worker worktree 里各一把，跨工不去重**；且 drop 无持久意图记录 |
| C4 | `post_commit_regen_yaml.py:89-90`（`reconcile_stale.pid`，TTL 60s，`:156/:167`） | spawn 去重 | 丢弃**不写日志**（stderr 被 `>/dev/null 2>&1` 吞）⇒ 近 7 日 81 次合格触发只有 20 份日志 ⇒ ≈75% 静默丢弃，零证据 |
| C5 | 再生落点 = **触发所在 worktree** | 该 worktree 的衍生产物既被 `check_no_commit_derived.py:100-107`（`GATE-NO-COMMIT-DERIVED`，fail-closed 禁入 git）禁止提交，又被下一件 `_sync_worktree` 的 `reset --hard` 丢弃（`commit_queue_landing.py:88-90` 注释自认"派生文件由后续 reconcile 重生成"） | **落地路径上的衍生再生是纯负收益件** |

## D. 门禁读衍生工件（判据是否受影响 → 见 B0_2 矩阵）

已核到实读点的代表：`module_id_consistency_gate.py:51-52`（`docs/03_modules/template_registry.yaml`、`cross_module_dependency_registry.yaml`）、
`domain_fk_gate.py:79`（`functional_domain_registry.yaml`）、`industry_chain_map_gate.py:110`（`path.read_text` 磁盘 YAML）、
`errcode_consistency_gate.py:80`（`architecture_model/contracts/error_code_registry.yaml`，且 `:45/:54` 自述已从 rglob 观测面改为 `git ls-tree` 批量读=**已示范正确解**）、
`meta/validate_rules_integrity.py:199-229`（`_hash_file`=工作树 / `_hash_git_head`=HEAD blob；**register 用 HEAD、check 用工作树** ⇒ 基线滞后会假红 TAMPERED）。
反之 `blueprint_amodule_consistency_gate.py:149`、`import_integrity_gate.py:120` 走 `_read_staged_file`（读暂存 blob，**不受磁盘衍生件滞后影响**）。
先例：DECISION-MAP 门禁的 hash-miss 回退分支（"读不到就退让"）曾造成假红，是本清单的判据基线教训。
