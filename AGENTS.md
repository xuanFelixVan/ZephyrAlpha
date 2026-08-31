# ZephyrAlpha — AI Agent 接入宪法

> **硬规则入口**: [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)（IDE 自动注入，全读完再开工）
> **施工指导**: [`.trae/rules/onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)（详细规则/冷启动序列/方法论索引）
> **内部 Agent 系统**: [`data/capability_cards/`](file:///d:/ZephyrAlpha/data/capability_cards/)（22 个 skill_*.yaml，L0/L1/L2/L3 渐进披露，非 IDE AI 使用）
> **新 AI 必读三件套**（2026-08-31 新增）：①[全项目对齐清单](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/sop/alignment_checklist.md)（六图+40+注册表+代码文档三层对齐规则）②[施工流程 SOP](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/sop/construction_workflow_sop.md)（端到端 15 步施工闭环）③前端手册（如涉及前端，待建）——**不知道要对齐什么=施工必有漏项**

## RULE-ENV：第零件事（环境对齐，2026-07-22 治本，#ARCH-ENV-PATH-001）

> **AI session 启动第一命令（在任何 `python` 调用之前，含 RULE-GUARDIAN / RULE-WORKTREE / RULE-DEPGRAPH）**：
> ```powershell
> $env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
> ```
> **验证**：`python --version` 输出 `Python 3.12.x`。用 `$env:LOCALAPPDATA` 推导路径（符合 D-G-01a，不硬编码绝对路径）。
>
> **根因**：TRAE IDE 启动 shell 时临时注入内置 Python 3.10.11（`ModularData\...\vm\tools\python\`）到 PATH 最前，覆盖 User PATH 中已优先的 Python 3.12.8。后果：`datetime.UTC`（3.11+ 新增）缺失 → GitCommitGateway 崩溃；`psycopg2` 未装 → 依赖 `_shared` 的 gate 崩溃；`ruff` 未装 → lint/format gate 崩溃。**Python 3.12.8 已装且依赖齐全**（psycopg2-binary 2.9.12 / ruff 0.15.10 / PyYAML 6.0.3 / pre-commit 4.5.1），纯 PATH 优先级问题。
>
> **已排除方案（穷举验证）**：①`default_language_version`（pre-commit 对 `language: system` 无效）②`.python-version`（无 pyenv/pyenv-win 无效）③`py -3.12`（py launcher 未安装）④修改持久 User PATH（TRAE 运行时注入覆盖，User PATH 已把 3.12 放最前但仍被覆盖）⑤PowerShell `$PROFILE`（TRAE shell 用 `-NoProfile` 启动，`use-ds-pro` 函数不可用验证）⑥`pyenv`（未安装）。
>
> **君子协定**：无门禁强制（TRAE 不可 hook shell 启动），依赖 AI 自觉（对标 RULE-WORKTREE FP-ISO.4C 模式）。**必须先执行此命令再启动 session_worktree**——`zephyr` 包内部使用 `datetime.UTC` 等 3.11+ 特性，3.10 下 `session_worktree_start` 会崩溃。版本契约：[`pyproject.toml`](file:///d:/ZephyrAlpha/pyproject.toml) L14 `requires-python = ">=3.12"`，ruff `target-version = "py312"`。

## RULE-GUARDIAN：第一件事

> **进入本项目的第一个命令（任何平台：Cursor/RooCode/Claude Code/Trae/VS Code）**：
> ```
> python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status
> ```
> never_run=true（或 last_run 超 24h 未更新）→ `powershell -ExecutionPolicy Bypass -File scripts\register_process_reaper_task.ps1`
> 有 last_run → 继续
>
> 进程清理由 OS 托管（2026-08-28 裁定，替代旧 ide_health_daemon 常驻守护模式）：Task Scheduler `ZephyrAlpha_ProcessReaper` 每 10 分钟触发 [`process_reaper.py`](file:///d:/ZephyrAlpha/src/zephyr/trading/process_reaper.py) one-shot 清理（孤儿/超龄/危险项目 python 进程 + Trae 幽灵窗口 + drift 指标 stash>5 自动清理），白名单保护永久服务，个案保留走 `data/runtime/process_reaper_keep.txt`（每行一个 cmdline 子串）。后台任务会话结束后由 reaper 兜底回收，AI 无需手动清理，但长批任务 MUST 先登记 keep 文件防误杀。
> **ProcessReaper 计划任务不存在 = 禁止任何写操作。**

## RULE-WORKTREE：第二件事（正式规则，2026-07-02 转正）

> **AI 对话启动后 MUST 调**（创建独立 worktree，消除 stash 冲突）：
> ```
> python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_start, generate_session_id; sid = generate_session_id(); r = session_worktree_start(sid); print(r)"
> ```
> 记住返回的 `session_id`。**一个任务=1次start+多次Edit/Write+1次commit+1次merge**。后续编辑用 Edit/Write 正常操作（写项目根即可，`session_worktree_commit` 会自动同步到 worktree）。
>
> **IDE 脏缓冲区陷阱（#68/#71/#75 事故族，#ARCH-WORKTREE-WRITE-INTEGRITY-001 治本）**：Trae IDE 文档层脏缓冲区可致 Edit/Write **不落盘**且 Read 回显旧缓冲区（mtime 回拨可识别）——关键文件改后 MUST 进程外核实（`Select-String`/`git diff`），疑似回拨用 PowerShell `[System.IO.File]::WriteAllText` 直写。防御机制已落地：tracked 文件漂移有常驻看门狗自动快照存证+告警（[`worktree_drift_watchdog.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py)，post-commit reconciler 自动拉起）；写注册表/AGENTS.md/tracker 等热文件 MUST 用 `safe_write_text`（[`file_utils.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/io/file_utils.py)，base-hash CAS+回读校验，陈旧缓冲区直接拒写落审计）。
>
> **提交时 MUST 调**（不用裸 `git commit`）：
> ```
> python -c "from zephyr.gov_enforcement.rule_bridge.session_worktree import session_worktree_commit; r = session_worktree_commit('<session_id>', ['<file1>', '<file2>'], '<message>'); print(r)"
> ```
> **任务完成**：调 `session_worktree_merge(session_id)` merge 回主分支（pre-merge 自动清理冗余未提交改动，通常无需手动处理脏工作区）。**放弃**：调 `session_worktree_abort(session_id, files=['<file1>', '<file2>'])`——`files` 参数传入 AI 修改/创建的文件列表，abort 时自动清理主工作区残留（tracked→`git checkout --`恢复，untracked→物理删除）。**merge失败**（自动清理后仍失败=AI commit 后又编辑了同一文件导致内容不一致）：先 `git checkout -- <冲突文件>` 还原主工作区→重试 `session_worktree_merge`→仍失败才 `session_worktree_abort` + 改用 GitCommitGateway。
>
> **为什么**：多 AI 对话共享工作目录导致 stash 堆积（4 个 stash 卡住对话），worktree 独立 git index 从根本消除冲突。
> **君子协定（正式）**：无门禁强制（Trae IDE 不可 hook），依赖 AI 自觉。6 连续 PASS 已转正式（Round2-4 + Extreme A/B/C，覆盖 4 种代码路径）。**HELD-OVERLAP 已加硬（2026-07-02）**：`session_worktree_commit` 内置 auto-claim + 硬阻断（对标 GitCommitGateway 的 HELD-OVERLAP gate）——commit 前对每个文件调 `registry.claim_file()`（原子 check-and-claim，防 TOCTOU 竞态），被其他活跃 session 持有则 `HELD_OVERLAP_VIOLATION` 阻断（回滚已 claim 文件）；claim 是 session 级，merge/abort 时 `unregister` 自动释放。逃生通道：`allow_overlap=True` 参数放行（对标 `--allow-overlap`）。**逃生通道（永久保留）**：HELD-OVERLAP 加硬消除了"两 session 编辑同一文件"的搭便车根因，但无法解决 git 固有 merge conflict（`allow_overlap=True` 强行覆盖时）+ AI commit 后又编辑同一文件导致内容漂移——此时 `session_worktree_abort` + 改用 GitCommitGateway（stash 隔离）作为兜底。详见 [FP-ISO.4C](#fp-iso4c)。
>
> **COMMIT-SCOPE gate（13a5e1d512 混合提交治本，priority=48）**：检测一个 commit 的文件是否跨越多个功能域（D_XXX）——跨≥2 域硬阻断（`COMMIT_SCOPE_VIOLATION`，exit 9），要求拆分为每个域一个 commit（对标「一个任务=1次commit」原则的语义层执行）。域判定三级 fallback：`.py` 文件读 `# [DOMAIN]` 头部 → `functional_domain_registry.yaml` 的 ssot_path 最长前缀匹配 → UNKNOWN（不参与跨域判定）。逃生通道：`--allow-multi-domain`（合理场景：跨域重构/域注册表变更/gate 基础设施本身）。三 gate 正交防御：HELD-OVERLAP(50) 注册表层 + FOREIGN-CHANGE(45) 内容层 + COMMIT-SCOPE(48) 语义层。详见 [`commit_scope_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/commit_scope_gate.py)。FOREIGN-CHANGE gate 另有 P1 post-claim 修改审计（warn-only，记录 claim 后到 commit 前的文件变化到 `.runtime/gate_audit/post_claim_modifications.jsonl`）。
>
> **软门禁升级（#ARCH-GIT-SELF-HARM-GUARD L3.1，2026-08-04）**：RULE-WORKTREE 从纯君子协定升级为渐进式软门禁——主工作区 commit 不再"无门禁强制"。双层防护：① **Layer 1** = in-process gate `WORKTREE-REQUIRED`（[`validate_worktree_required.py`](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/validate_worktree_required.py) priority=44，GitCommitGateway `check_all()` 路径）；② **Layer 2** = pre-commit hook `gate-worktree-required`（裸 `git commit` 路径；`--no-verify` 可绕过但 Layer 1 补齐覆盖缺口）。行为：主工作区 commit → warn + 按 session 计数（`.runtime/gate_audit/worktree_skip.jsonl`），单 session 累计 ≥5 次升级阻断；worktree 内 commit / reconciler auto-commit / merge 提交放行。详见 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `#ARCH-GIT-SELF-HARM-GUARD`。
>
> **自伤防护（#ARCH-GIT-SELF-HARM-GUARD L1+L2，2026-08-04）**：背景——100% AI 开发下并发 session 频繁 `git reset --hard` 覆盖未提交 AI 编辑（reflog 19 次 reset）。治本——[`git_guard.py`](file:///d:/ZephyrAlpha/scripts/git_guard.py) 在危险命令执行前检测"自伤"（覆盖自身未提交修改）：① **L1 止血** `git reset --hard`：有 tracked 未提交修改且未授权 → fail-closed 阻断（`--soft`/`--mixed` 不覆盖工作区不触发）；② **L2 治本** `git checkout --` / `git restore`：文件级自伤检测，目标文件有未提交修改时阻断。**逃生通道**：`ZEPHYR_FORCE_STASH=1` 环境变量授权放行 + 记审计（`.runtime/gate_audit/git_guard_self_harm.jsonl`），复用已有 env 不引入新真源。**绕过监控**：[`git_guard_bypass_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/git_guard_bypass_reconciler.py)（post-commit priority=810，warn-only）对比 git reflog 的 reset 记录与审计日志，检测绕过 alias 直连 git 的场景。
>
> **豁免条款（reconciler 实弹验证专用，2026-07-02 裁定）**：验证 GitCommitGateway post-commit reconciler 链路时，允许走 `scripts/git_commit.py --reconciler-verify`（不经过 session_worktree）。**豁免理由**：reconciler 操作主分支数据（depgraph DB / 主仓库 index auto-commit），无法在 worktree 独立 index 内运行；且验证为单 session 诊断场景，与君子协定“防多 session 并发冲突”的核心目的正交。**三重前置条件**（缺一不可）：(1) 主工作区 clean（`git status --short` 空）(2) 无其他活跃 session（或 `--allow-concurrent` 逃生）(3) `claim_files` 全部成功（`--allow-overlap` 自动禁用）。搭便车风险由 claim_files 文件级锁 + `_GlobalCommitLock` 串行锁 + 干净环境三重防护覆盖。**仅限验证场景**，常规开发提交仍 MUST 走 session_worktree。
>
> **相关策略文档**（2026-07-08 架构师审查追加）：
> - [分支策略](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/branch_strategy_policy.md)（单一主分支模型：dev 主分支 + master FF 镜像 + session/* 命名约定 + 3 个月废弃规则）
> - [工作区治理规则](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/workspace_governance_policy.md)（auto-sync 产物还原优先 + .gitignore 维护规则 + bdpan 数据评估）
> - [并行 session 协调策略](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md)（held_files 协议 + handoff 交接 + 冲突升级）
>
> **stash 自动清理（#ARCH-WORKTREE-002 Phase 4，2026-07-19）**：`session_worktree` 在 pre_merge/abort/auto-recover 多处 stash 临时修改。post-commit reconciler `GATE-STASH-LIFECYCLE`（[`make_stash_lifecycle_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) priority=801）事件驱动清理 > 24h 的 session_worktree 临时 stash（按 msg 前缀 `session_worktree_pre_merge`/`session_worktree_abort` 识别，按索引降序 drop 避免 renumbering），不影响用户手动 stash。AI 无需手动 `git stash drop`。
>
> **stash 操作 AI 可见性通告（#ARCH-RECONCILE-WORKER-HEARTBEAT-001 R3，2026-08-01 治本）**：`session_worktree` 的 pre-merge/abort 路径用 `git stash push` 保存 AI 编辑（文件还原到 HEAD），AI 看到"编辑没了"但不知被 stash 保存了——误判为"被覆盖/丢失"。治本：[`_write_stash_notice`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 在每次 stash push 后写入 `.runtime/workspace_alerts/stash_notice.json`（含 stash 文件列表 + 恢复命令 `git stash pop` + AI 通告"编辑已被 stash 保存，非丢失"）。AI 发现编辑"消失"时，MUST 先检查 `.runtime/workspace_alerts/stash_notice.json` 确认是否被 stash 保存，而非误判为丢失。
>
> **heartbeat 保活机制（#ARCH-HEARTBEAT-001 Phase 1，2026-07-20 治本）**：`session_worktree_start` 用 `pid=0`（逻辑 session）注册，跨多个 `python -c` 进程存活靠 TTL。旧方案仅 TTL=3600s，AI 崩溃后 held_files 阻塞 1 小时。治本：`session_worktree_start` 自动 spawn detached heartbeat daemon（[`heartbeat_daemon.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py)），daemon 每 30s 调 `registry.heartbeat(session_id)` 刷新 `last_heartbeat` + 追加 `heartbeat.jsonl` 审计记录。`_is_session_alive` 用 90s 新鲜度判据（3×30s，容忍 2 次漏跳），daemon 死亡→90s 后 session 判死→held_files 自动释放。`session_worktree_merge`/`abort` 时 `_kill_heartbeat_daemon` 终止 daemon + `cleanup_heartbeat_file` 清理审计文件。阻塞窗口从 1h 缩短到 90s，消除 `HELD_OVERLAP_VIOLATION` 误阻断根因（之前 allow_overlap 62× 超阈）。AI 无需手动管理 heartbeat 生命周期。
>
> **heartbeat 活性反转治本（#ARCH-HEARTBEAT-002，2026-07-23 治本）**：#ARCH-HEARTBEAT-001 的 daemon 退出判据仅"session 不在 registry"，但 daemon 自己是 `last_heartbeat` 唯一刷新源——chat 异常关闭（未走 merge/abort）时 daemon 持续刷新心跳，session 永远"存活"，held_files 永久阻塞（活性反转：活性锚点=daemon 自己的输出，自证存活闭环；实测 sess-39820/sess-53456 僵尸 daemon）。治本：引入 `last_activity` 独立活性锚点（`SessionInfo` 字段），只由真实治理操作刷新（`register`/`claim_file`/`register_dependency`），heartbeat **不**刷新。daemon 主循环新增 idle 检查：idle 超 `_ACTIVITY_IDLE_TIMEOUT_SECONDS=1800s`（30min）自动退出→90s 后 registry 过期→held_files 释放。缺失 `last_activity` 时回退 `start_time`（绝不回退 `last_heartbeat`）。AI 无需手动管理——daemon 自愈，30 分钟无治理操作自动退出。
>
> **reconcile worker 心跳保活 + 孤儿主动清扫（#ARCH-RECONCILE-WORKER-HEARTBEAT-001，2026-08-01 治本）**：async reconcile_worker 死亡后 status file 永驻 `running`（僵尸判定惰性——仅 `read_status_file` 被 query 时触发且不改文件，`launch_reconcile_async` 不遍历已有 running 文件），无人 query 即永不标 stale（实测 commit 8af8f5b worker_pid=21524 死亡后 running 持续 398132s ≈ 4.6 天）。治本（三处对齐）：①**心跳信号** [`write_heartbeat`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconcile_runner.py)——每个 reconciler 执行前刷新 status file 的 `last_heartbeat_at` + `current_reconciler`，注入路径 `reconcile_worker._run_worker` → `_run_post_commit_reconcile_sync_worker(heartbeat=_hb)` → `reconcile_for(heartbeat=...)` → 回调；②**主动孤儿扫描** [`sweep_stale_workers`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconcile_runner.py)——在 `launch_reconcile_async` 入口遍历 `reconcile_status_*.json`，对 running 超阈值 + pid 已死的 worker 改写为 `stale`（`orphaned_worker_dead`），live worker（pid 存活）不改写（避免误杀慢 reconciler）；③**僵尸判定对齐**——`read_status_file` 优先看心跳（无心跳回退 `started_at`），超阈值时探测 pid 存活，与 `sweep_stale_workers` 判定逻辑一致。进程探活复用 [`process_pool.is_pid_alive`](file:///d:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py)（真源唯一），`reconcile_runner._is_pid_alive` 为其别名。AI 查询 worker status 时看 `last_heartbeat_at`（新鲜=live）+ `current_reconciler`（当前执行哪个 reconciler），无需手动清扫。

## RULE-DEPGRAPH / 五图对齐：第三件事（防幻觉/防漂移治本规则，2026-07-02；五图对齐提升 2026-07-22）

> **施工前 MUST 登记**：任何模块施工前（写第1行业务代码前），MUST先通过 `apply_depgraph.py` 将该模块的依赖关系（模块间/契约/事件/外部域）登记到 depgraph 设计态（`status=planned`）。禁止"先施工后补登记"或"施工中临时编造依赖"。施工完成并通过验证后做状态转正——**场景分流（2026-08-14 勘正，SOP Step 8 同口径）**：worktree 隔离施工会话内只登记不流转（design 态受重建 DELETE 豁免保护；merge 回 dev 后由 #ARCH-70 同身份 UPDATE 通道随第一次重建自动转 production，merge 执行人负责实证核验+闭环遗留）；主工作区直接施工用 `--transition-design-maturity <NODE_ID> production`（注意 build_status 六态（B-007 P0 2026-08-26 +production）与 design_maturity 两字段正交——build_status 的 production 仅 stable 节点可转（testing→stable→production 两步法），稳定度走 planned→generated→testing→stable 链）。
>
> **写入设计态前 MUST 检查运营态**：`apply_depgraph.py --add-design-node` 写入 `build_status=planned` 时，内置门闸自动检查 depgraph 运营态（production节点）是否就绪。运营态为空→阻断，提示先手动运行 `generate_project_depgraph.py` 刷新；运营态就绪→允许写入设计态。设计态必须基于最新运营态，否则在过期快照上设计=幻觉温床。逃生通道：`--skip-refresh`（仅限故障时使用，正常流程禁止）。
>
> **为什么**：depgraph 是依赖关系唯一真源。AI 从 depgraph 查询依赖=零幻觉空间；AI 绕过 depgraph 自行推断依赖=幻觉/漂移根源。**当前强制状态（三层防御，2026-07-21 第三期落地）**：①未登记依赖在拓扑验证（`check_blueprint_code_alignment.py`）时定级为 **LOW**（CODE_NOT_IN_DEPGRAPH，暂态容忍，由 post-merge reconciler 兜底同步）；②**HIGH drift（ORPHAN_MODULE_ID/MODULE_ID_DRIFT）已 pre-merge 硬阻断**——`session_worktree_merge` 经 `_pre_merge_gate_check` → `_run_pre_merge_topo_check`（#ARCH-DEP-001 第二期，2026-07-17 落地）subprocess 调 MAIN 副本 `check_blueprint_code_alignment.py --json --scan-root <worktree>`（MAIN 副本有 DB 配置，`--scan-root` 仅重定向代码扫描），过滤到 session 变更文件（仅阻断 session 自身引入的 HIGH），HIGH drift 阻断 merge（checker 缺失 fail-closed 阻断；DB 不可用/超时/JSON 解析失败 fail-open 放行）；③**commit-time 轻量预检已落地（#ARCH-DEP-001 第三期，2026-07-21）**——`NEW-FILE-DEPGRAPH-ENFORCEMENT` gate（priority=58，post-HELDOVERLAP(50) pre-CREATE-GUARD(60)）检测 staged 新增 .py 文件（src/zephyr/ 或 scripts/ 下，tests/ 豁免）在 depgraph nodes 表完全无记录（generated/planned/stable/deprecated 任一状态均放行）时硬阻断 commit。bootstrap 豁免：现有 3811 个 generated 节点不受影响（gate 只检测本次 commit 新增文件）。DB 不可达时 fail-open（对标 rename_depgraph_sync_gate）。AI 仍应在施工前通过 `apply_depgraph.py --add-design-node` + `--add-edge` 登记设计态；或施工完毕运行 `python scripts/governance/generate_project_depgraph.py` 让扫描器自动登记运营态。L1 铁律从"君子协定"升级为"君子协定 + pre-merge 拓扑硬阻断 + commit-time 轻量预检"三层防御。
>
> **流程**：
> 1. `generate_project_depgraph.py` 刷新运营态（门闸自动执行）
> 2. `apply_depgraph.py --add-design-node PATH BLUEPRINT_ID DOMAIN_ID planned` 登记设计态
> 3. 拓扑验证（无循环/无缺失/无孤儿）
> 4. 施工（代码引用 depgraph 契约名）
> 5. 验证依赖一致性
> 6. `apply_depgraph.py --transition-design-maturity NODE_ID production` 转正（2026-08-14 勘正：旧写法 `--transition-build-status ... production` 必失败——build_status 五态无 production；worktree 施工禁止会话内流转，merge 后自动转换，见 SOP Step 8 分流）
>
> **五图对齐（ARCH-053/056，2026-07-22 提升为入职必读）**：五图 = 前四图以 `module_id` 为对齐 key（depgraph/dataflowgraph/decisiongraph/blueprint.md）+ 第五图 battle_map 以 `step_id` 为对齐 key + 双向锚点（BM-INV-002/007）——
>
> | 图 | 真源 | 设计态机制 | 工具 |
> |----|------|-----------|------|
> | depgraph | PostgreSQL | `design_maturity='design'` 节点 | `apply_depgraph.py --add-design-node` |
> | dataflowgraph | PostgreSQL（3 表） | design 行 + 触发器保护 | `apply_dataflowgraph.py` |
> | decisiongraph | PostgreSQL（3 表） | design 行 + 触发器保护 | `apply_decisiongraph.py` |
> | blueprint.md | MD frontmatter | `sync_panorama_module.py` 从 depgraph 单向派生 4 字段 | `sync_panorama_module.py` |
>
> **入口只有一个——depgraph 设计态**：写入 depgraph 设计态后，[`sync_panorama_module.py`](file:///d:/ZephyrAlpha/scripts/governance/sync_panorama_module.py) 自动派生其余三图（dataflow_jobs/decision_layers 占位 + blueprint.md frontmatter 4 字段），[`align_panoramas.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/align_panoramas.py) 自动检测四类对齐问题（孤儿/状态漂移/域不一致/设计态孤立）。所以"在全景设计并对齐"实操上 = 上面流程的步骤 2 后跑 sync 派生、施工前跑 align 验证干净。AI 不需要也不允许手编派生三图。
>
> **对齐验证（施工前 MUST）**：`python scripts/governance/d5_architecture/generators/align_all.py` —— 五图两轴问题须干净（或已知可接受）。**门禁**：`GATE-PANORAMA-ALIGNMENT`（priority=830）`domain_mismatches>0` **硬阻断**，orphans/state_drifts warn-only（君子协定，post-merge reconciler 兜底）；修复入口 `python scripts/governance/sync_panorama_module.py --all`。
>
> 规则真源：[`trae_080_panorama_alignment.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_080_panorama_alignment.yaml)；执行细节见 §11.0.2 ARCH-053/056。
>
> **作战地图对齐（step_id 轴，2026-08-02）**：与五图对齐（module_id 轴）正交——[`align_battle_map.py`](file:///d:/ZephyrAlpha/scripts/governance/align_battle_map.py) 检测 battle_map 三表（steps/anchors/edges）七类问题：孤儿环节(BM-INV-001)/幽灵锚点(BM-INV-002)/缺失叙事(BM-INV-003)/悬空边/域漂移(BM-INV-004)/父子嵌套一致性(BM-INV-006，V0.4.0 parent_step_id+depth，防悬空父引用/跨阶段嵌套/成环/depth超限)/孤儿模块(BM-INV-007，V0.7.0 业务域depgraph模块无任何锚点指向=造出来没用上)。**V1.1.0 三档分类（2026-08-06 #ARCH-BM-001 治本）**：①扫描范围改用 [`§domain_classification`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml)（38 业务域+19 工具域显式分类，替代原"flow_stage allowed 域并集"逻辑——并集把工具域误判为业务域导致 106 基础设施模块误报孤儿）；②新增 [`§acknowledged_orphans`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml)（8 模块+28 环节已确认合理孤儿登记，带 review_frequency 到期复审+promotion_criteria 移出条件）——孤儿分三档：**违规**（不在名单，须修复）/ **已确认合理**（在名单，定期复审）/ **待实现**（名单中 build_status=planned，promote 后移出）。AI 看到 violations=0 + acknowledged≠0 时**不应尝试给 acknowledged 项挂锚点**（会触发域漂移→违反铁律5→振荡）。BM-INV-005(派生缓存直写)为未落地规划——depgraph.nodes 无 battle_map_step_ids 列、无 sync、align 不检测，当前通过 anchors 反查(target_graph=depgraph+target_id=blueprint_id)。域漂移规则真源：[`battle_map_domain_policy.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml)（flow_stage→允许 domain 列表，TRAE-062 规则数据真源=YAML）。君子协定 warn-only，不硬阻断。**改 battle_map 三表前已由 backup_pg_architecture() 自动 PG 备份**（trae_054 v1.6.0 STEP0，apply_battle_map 写入后事件触发，非 git commit；覆盖全景 19 张 DB 真源表）。spec：[`battle_map_positioning.md`](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md) §7 SSoT 铁律/§8.4 不变量。
>
> **文件重命名 MUST 先重建 depgraph**（AI-14 审计 S1，2026-07-17）：`git mv old.py new.py` 后、commit 前，MUST 运行 `python scripts/governance/generate_project_depgraph.py --force` 重建 depgraph。RENAME-DEPGRAPH-SYNC commit gate（priority=39）会检测 staged .py 重命名的新路径是否已在 depgraph nodes 表登记，未登记则硬阻断。历史债务扫描：`python scripts/governance/d8_doc_sync/audit_rename_completeness.py --check-file-renames`。
>
> **分层契约诊断辅助 .importlinter**（AI-01 P4 治本，2026-08-01）：分层契约主守护 = 上文 depgraph 拓扑验证（`check_blueprint_code_alignment.py`，HIGH drift 已 pre-merge 硬阻断）。[`.importlinter`](file:///d:/ZephyrAlpha/.importlinter) 是**诊断辅助工具**（warn-only，未接 pre-commit），用于本地 `lint-imports` 诊断 shared 层是否误 import 业务层。**不登记 GATE-IMPORT-LAYER 硬阻断**——避免与 depgraph 拓扑验证职责重叠（双真源漂移风险：两套检测逻辑对"shared 能 import 谁"判定不一致时 AI 无所适从）。运行：`lint-imports`（需安装 import-linter，非核心依赖）。
>
> ### 文档引用铁律（2026-08-04，独立于设计态准入门槛）
>
> 蓝图/文档引用 depgraph 时**只写稳定标识**（`module_id`/`blueprint_id`/`path`），**禁止写易变物理ID**（`node_id`/`edge_id`）。背景：8 个 blueprint.md 曾硬编码 `node_id`，DB 节点重建后成死引用。属命名/引用规范。
>
> **二元判定**：文档出现 `node_id=数字` / `edge_id=数字` → 硬阻断。**双层防御**（检测逻辑 SSoT = [`check_doc_node_id_hardcode.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_doc_node_id_hardcode.py)）：① pre-commit hook **GATE-DOC-NODE-ID**（`gate-doc-node-id`，检测范围 `docs/**/*.md`）；② in-process gate **BLUEPRINT-NODE-ID-HARDCODE**（[`blueprint_node_id_hardcode_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/blueprint_node_id_hardcode_gate.py)，priority=57，subprocess 调 `check_doc_node_id_hardcode.py --ci --files` 检测 staged blueprint.md）——GitCommitGateway 用 `--no-verify` 绕过 pre-commit hook，in-process gate 在 `check_all()` 阶段执行补齐覆盖缺口（#ARCH-DOC-NODE-ID-RULE-001 P1 补齐，2026-08-04；P3 三源→单源治本 2026-08-04：原内联正则与 `validate_blueprint_provenance.py` 形成三源已漂移，治本改为 subprocess 调用专门检测器，GATE-12 回归纯 provenance 校验）。需要物理 ID 时**查 depgraph DB 获取**，不在文档里固化。
>
> ### 模块获取方式元数据（acquisition fields，2026-08-05）
>
> **每个模块登记"怎么搞到手"**：`nodes_metadata` 表两列记录模块的获取方式与来源，供 AI 开发时查询，避免重复造轮子（已有开源替代时直接复用、已借鉴时对齐命名、废弃者不复用）。
>
> | 字段 | 列 | 取值 / 含义 |
> |------|-----|------------|
> | acquisition_method | `nodes_metadata.acquisition_method` | `self_build`（自建）/ `opensource`（开源替代）/ `borrow`（借鉴）/ `deprecate`（弃用） |
> | acquisition_source | `nodes_metadata.acquisition_source` | 开源链接 / 借鉴组件名 / 空（self_build 时通常空） |
>
> **枚举真源（单真源）**：`acquisition_method` 合法值唯一真源 = DDL CHECK 约束（[`depgraph_schema._DDL_NODES_METADATA`](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) + [`02_create_pg_schema.sql`](file:///d:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql)）。注释 / help 文本 / 生成器字典均为派生展示，禁止作真源；非法值 INSERT 被 DB 拒绝。
>
> **设置方式**：`apply_depgraph.py --update-module-metadata PATH acquisition_method=opensource acquisition_source=<url>`（[apply_depgraph.py](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py)）UPSERT 到 `nodes_metadata`（`path` 为稳定 PK，PATH 后跟 `KEY=VALUE` 列表）。
>
> **查询方式**：[`DepgraphReader.get_status_and_gate_map(target_ids)`](file:///d:/ZephyrAlpha/src/zephyr/governance/persistence/depgraph_reader.py) 批量返回 `{build_status, gate_reason, acquisition_method, acquisition_source}`，按 `blueprint_id` 聚合 acquisition（优先取非空值，`ORDER BY n.path` 确保确定性）。
>
> **可视化**：battle_map 生成器按 `acquisition_method` 渲染 emoji 标记（[`generate_battle_map_diagram.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py)），一眼区分自建/开源/借鉴/弃用模块。
>
> **迁移**：现有库加列用 [`add_acquisition_fields.py`](file:///d:/ZephyrAlpha/scripts/governance/migrations/add_acquisition_fields.py)（幂等 `ALTER TABLE ADD COLUMN IF NOT EXISTS`，superuser DDL 权限）。

## RULE-REGISTRY：第四件事（ARCH-053 AI 可发现性，2026-07-06）

> **查项目所有 registry**：MUST 先读 [`registry_of_registries.yaml`](file:///d:/ZephyrAlpha/docs/registry_of_registries.yaml)（ROOR，title="全项目唯一真源总纲"，注册表发现的唯一真源；精确数量以该文件 `summary.total_registries` 字段为准，**勿在文档/AI 记忆中写死**）或调用 `discover_all_registries()` 函数（`zephyr.infrastructure.asset_inventory.registry_adapter`，读 ROOR 返回全部 registry）。
>
> **为什么**：项目有 50+ 个 registry（精确数量以 ROOR `summary.total_registries` 为准；基础设施/门禁/规则/脚本/测试/接口契约/聚合节点/数据库/code_inline/directory 等全格式），硬编码路径只能覆盖 ~7 个。AI 启动时通过 ROOR 发现全部 registry，避免"不知道某表存在"导致重复造轮子或绕过治理。
>
> **真源分类（#ARCH-REGISTRY-DISCOVERY-SSOT-001 治本，2026-07-30）**——两个索引性质不同，**勿混用**：
> - **ROOR**（`docs/registry_of_registries.yaml`，人工 human_gated，`REG-*` 编号）= 注册表发现真源，覆盖全格式（yaml/markdown/postgresql/directory/code_inline）。被 `RegistryManager.discover_registry_files()`/`load_all()` 资产盘点主管线消费。
> - **master_index**（`docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml`，自动生成，`CFG-*/PS-REG-*/GOV-*` = catalogs 文件自身 module_id）= **catalogs/ 目录的派生漂移缓存**（GATE-REGISTRY-SYNC reconciler 维护），**不是** registry-of-registries，不可作为发现真源。
>
> **关键 registry 速查**：
> - 基础设施（数据库/缓存/队列）：[`infrastructure_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml)
> - API 接口契约：[`interface_contract_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/interface_contract_registry.yaml)（ARCH-053 新增）
> - 跨模块依赖：[`cross_module_dependency_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml)
> - 能力→真源文件反查：[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)
> - 告警阈值：[`alert_threshold_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml)（REG-ATH-001，监控/告警/复盘链路阈值 SSoT，35 条/11 类；改阈值先改表，tests/governance/test_alert_threshold_consistency.py 强制注册表↔代码对齐）
> - 冷数据分层（冷库/归档/物理去重）：[`infrastructure_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml) INFRA-STORE-002（E:/zephyr_cold_archive Parquet 冷库，DuckDB 直读）+ 真源契约 [`data_retention_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml)（INV-RET-001~005+§2A 派生治理；ST/小体量研究数据永不归档）；工具 scripts/ch/archiver.py（归档唯一通道，--period 支持元组分区键）+ scripts/ch/optimize_merge.py（ReplacingMergeTree 物理去重，计划任务每周日 03:30）
>
> **业务资产 registry 速查**（#ARCH-BREG-001，18 表体系，施工总案=design_memos/62_business_registry_construction.md；✅=P0 完成，🔄=P1 Step1-3 落盘待审计）：
> - ✅ 股票池：[`universe_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml)（6 条，回测 MUST 指定 universe_id）
> - ✅ 基准：[`benchmark_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/benchmark_registry.yaml)（8 条，回测 MUST 指定 benchmark_id）
> - ✅ 交易成本模型：[`cost_model_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cost_model_registry.yaml)（5 条，回测 MUST 扣成本）
> - ✅ 因子库：[`factor_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml)（140 条/7 类，Step1-8 全量闭环）
> - ✅ 策略库：[`strategy_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml)（146 条/5 类，Step1-8 全量闭环）
> - ✅ 风控限额：[`risk_limit_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml)（111 条/9 类，K4 补登 var/es/kill_switch 20 条后闭环）
> - ✅ 技术指标：[`technical_indicator_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml)（41 条/6 大类，含 Ichimoku，9 周期覆盖）
> - ✅ 执行算法：[`execution_algo_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/execution_algo_registry.yaml)（7 条：TWAP/VWAP/ICEBERG/POV/IS/ALT+EXA-TWAP-002 智能执行参数）
> - ✅ 数据资产：[`data_asset_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml)（206 条=15 源+105 数据集+86 作业，含龙虎榜/财务/公司行动/宏观全谱系）
> - ✅ 图形形态：[`chart_pattern_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml)（256 条/8 大类，十五轮 SOTA 调研收敛关闭）
> - ✅ 字段字典：[`field_dictionary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/field_dictionary.yaml)（259 条/16 域，factor.inputs FK 全量可解析）
> - ✅ 实验：[`experiment_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml)（5 条可溯源实验记录）
> - ✅ 龙虎榜席位：[`seat_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml)（16 席位，管"谁在买"，与图形形态表正交；消费模块=CAND-SEAT-001）
> - ✅ 周期分析：[`regime_cycle_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/regime_cycle_registry.yaml)（13 条 Gann/统计周期，管"时间窗口"，与 regime/emotion_cycle 正交；消费模块=CAND-CYCLE-001）
> - ✅ ML 模型：[`model_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/model_registry.yaml)（8 条，模型产物版本/晋升/衰减，与 experiment 过程表正交）
> - ✅ 事件日历：[`event_calendar_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/event_calendar_registry.yaml)（14 事件类型全量 PIT 规则，event_driven 策略前提）
> - ✅ 宏观指标：[`macro_indicator_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/macro_indicator_registry.yaml)（16 条中美指标发布纪律/修订政策/市场语义）
> - ✅ 组合构建模型：[`portfolio_model_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/portfolio_model_registry.yaml)（11 条：等权/打分加权/MVO/BL/风险平价/最小方差/HRP/Barra+核心-卫星/Kelly/组合优化三方法，OOS 跑不赢 1/N 不得晋升）
> - 备注：18 个注册表全部建成并登记 ROOR，状态以 ROOR `summary.total_registries` 为准

## RULE-SSOT：第五件事（真源分类铁律，防泛化错误，2026-07-09 加强）

> **写入任何数据前 MUST 先判定真源方向**——项目有两类数据真源，按数据类型机械判定，禁止凭记忆推断。规则真源：[`trae_062_ssot_classification.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml)。详见 §11.0.2。
>
> | 数据类型 | 真源 | 写入方式 |
> |---------|------|---------|
> | **规则数据**（trae_*.yaml/契约/门禁/词汇表/注册表） | **YAML 文件** | `sync_yaml_to_depgraph.py` 单向同步到 DB（DB 只读缓存） |
> | **架构数据**（depgraph.nodes/edges、decision_nodes/edges、dataflow 节点） | **PostgreSQL DB** | `apply_*.py` 直接写入 DB |
>
> **常见错误**：❌ 误以为"YAML 是真源"适用于所有数据（实际只适用规则数据，架构数据真源在 DB）。
> **判定流程**：拿到数据 → 先问"规则数据还是架构数据？" → 规则数据改 YAML→sync 到 DB；架构数据用 apply_*.py 直接写 DB。边界模糊查 §11.0.2。
>
> **翻译真源三层体系**（2026-08-01，#ARCH-SSOT-GLOSSARY-MERGE-001 补齐模块级）——生成器输出中英文标签时 MUST 通过对应 loader 读取翻译真源，禁止硬编码翻译字典。三层粒度互补不重叠：
>
> | 层级 | 真源 YAML | 加载器 | 粒度 | 示例 |
> |------|----------|--------|------|------|
> | 术语级 | `terminology_glossary.yaml` | `_shared/terminology_loader.py` | 图示术语 | edge_type→触发 |
> | 域级 | `functional_domain_registry.yaml` | `domain_name_mapping.py` | D_XXX 域 | D_GOV_RULE→规则治理 |
> | 模块级 | `module_translation_registry.yaml` | `_shared/module_translation_loader.py` | .py 文件 | gate_types.py→门禁类型定义 / Gate Types |
>
> 新增模块翻译：往 `module_translation_registry.yaml` 加条目（module_path/name_zh/name_en/desc_zh/desc_en），零代码改动。

## RULE-DATA-OPS：第六件事（数据库破坏性操作纪律，2026-07-16 事故治本，#ARCH-CH-020）

> **破坏性数据库操作（DELETE/REPLACE PARTITION/TRUNCATE/ALTER DELETE/OPTIMIZE FINAL/INSERT GROUP BY+REPLACE）执行前 MUST 完成三步验证**——必要性 + 真实性 + 可逆性。规则真源：[`trae_063_data_ops_discipline.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_063_data_ops_discipline.yaml)。
>
> **三步验证铁律**：
> 1. **必要性**——为什么需要此操作？根因是什么？能否用非破坏性方式（INSERT 补偿、UPDATE 标记）替代？
> 2. **真实性**——MUST 查看具体数据内容，禁止仅凭聚合数字判定。"重复"验证 MUST 按全字段 `GROUP BY HAVING count() > 1`。禁止用 `count() - uniqExact(排序键)` 算"重复"——排序键是 ReplacingMergeTree 去重键，不含全部业务字段，同排序键不同维度的有效记录会被误判。
> 3. **可逆性**——操作前 MUST 有备份/快照或可从数据源恢复。无备份 = 禁止执行。
>
> **标准化工具**：[`check_tick_duplication.py`](file:///d:/ZephyrAlpha/scripts/governance/data_quality/check_tick_duplication.py) `--month YYYYMM`（全字段 GROUP BY 查真重复）。
>
> **前缀合规检测**：[`check_indicator_prefix.py`](file:///d:/ZephyrAlpha/scripts/governance/data_quality/check_indicator_prefix.py) `--ci`（macro_data indicator_name 前缀合规检测，支持 `--fix` 生成修复 SQL）。
>
> **事故背景**（2026-07-16）：AI 用 `count() - uniqExact(排序键)` 算 tick_data "重复数"，把同时间戳不同价位的有效记录误判为"重复"，执行 INSERT GROUP BY + REPLACE PARTITION 删除 21 个月有效数据。根因：tick_data ORDER BY 不含 price（#ARCH-CH-020）。

## RULE-RULING：第七件事（裁定登记机制，2026-07-18 治本，裁定#20-A/#20-B/#20-D）

> **任何 `裁定#NNN` 引用必须先在裁定登记表登记**——禁止 grep-and-claim 占位（对标编号铁律#6 的 `#ARCH-XXX` 机制）。裁定真源：[`ruling_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml)（条目数以该文件 `entries` 为准——**勿在文档/AI 记忆中写死**，曾因硬编码"54"漂移至实际 56；裁定#20-A 建立，裁定#20-E/#20-F/#20-G 扩展）。配套门禁：[`ruling_reference_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/ruling_reference_gate.py)（priority=74，裁定#20-B 建立，裁定#20-G 启用 hard block）。
>
> **病根（第一性原理）**：项目中存在 493 处"裁定#NNN"引用、48 个不同编号，但无中央裁定登记表——新 AI 可不查 registry 就用未登记编号，违反铁律后只能靠人工审核发现。对标 `#ARCH-XXX` 议题登记机制（`architecture_issue_registry.yaml`，裁定#208 R6 建立）缺失对应物。治本：建立中央登记表 + commit gate 强制 + AGENTS.md 文档化三件套。
>
> **裁定编号分配铁律**（裁定#20-D）：
> 1. **连续分配**：裁定#NNN 按裁定时间顺序连续分配，禁止跳号
> 2. **不回收**：已分配编号永不回收，即使被废弃/superseded
> 3. **子裁定格式**：裁定#NNN-A/B/C 表示主裁定（裁定#NNN）的子项（如裁定#203 的子裁定 #203-B）
> 4. **status 四值**：active(生效中) / superseded(被新裁定取代) / deprecated(废弃态) / draft(草案)
> 5. **登记强制**：任何 裁定#NNN 引用必须在本注册表有对应条目，禁止 grep-and-claim 占位（裁定#20-A）
> 6. **同提交原子性**：新增 裁定#NNN 引用必须与 registry 同 commit 提交（裁定#20-B L2，阶段2 启用硬阻断）
> 7. **编号空洞检测**：WARNING 不阻断（如本项目编号缺口 #205/#212）
> 8. **跨表引用**：裁定可关联 `#ARCH-XXX` 议题（related_arch）与其他裁定（related_rulings），形成议题-裁定双向追溯链
>
> **RULING-REFERENCE gate 当前状态**：**阶段2 hard block 已启用**（裁定#20-G，2026-07-18，_MANUAL_STAGE=False）——新增未登记 裁定#NNN 引用直接阻断提交。阶段1 建立基线已完成（51 个裁定登记 + baseline 0 个悬空引用）。检测 staged 文件中新增的 裁定#NNN 引用是否在 registry 有对应条目，fail-closed——registry 缺失/git 异常时阻断；跳过 tests/ 豁免区；扫描 .py/.yaml/.yml/.md；L2 同提交原子性——新增引用必须与 registry 同 commit 提交。
>
> **新增裁定流程**：(1) 在 `ruling_registry.yaml` entries 末尾追加新条目（含 ruling_id/title/date/category/status/summary/affected_files/related_arch/related_rulings/superseded_by）；(2) 同 commit 提交 registry 与首次引用代码。

## RULE-CAPABILITY-LOOKUP：第八件事（能力反查强制 + 逃生通道治本，2026-07-19，裁定 #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD）

> **AI 施工前 MUST 调用能力反查**——写第一行 `src/zephyr/**/*.py` 业务代码（不含 `tests/` / `*.md` / `*.yaml` / `*.json`）前，必须先调用以下任一接口，让 AI 进入"零幻觉空间"：
> - **MCP 接口（首选，AI 自动可用）**：`rule_discovery.discover_applicable_rules(operation='file_write')` ——返回当前 session 适用规则清单 + 写入审计日志
> - **Python API（备选，用于脚本/调试）**：`capability_lookup.find(<keyword>)` ——按关键字反查能力 → 真源文件
>
> 配套门禁：[`capability_lookup_required_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/capability_lookup_required_gate.py)（priority=110，#ARCH-GOV-CONVERGENCE-META Phase 3.4a 建立）。规则真源：[`trae_065_capability_lookup_required.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_065_capability_lookup_required.yaml)。
>
> **病根（第一性原理，6 层闭环模型，TRAE-068 #ARCH-PREVENTABILITY-LAYER-001 正式化）**：100% AI 开发场景下，机制必须经 6 层闭环才能可靠工作——①**可知性**（AI 知道机制存在）②**可达性**（AI 能调用接口）③**可观察性**（调用结果有反馈）④**可逃生性**（紧急情况能 bypass）⑤**可追溯性**（bypass 留审计链）⑥**可预防性**（pre-commit 阻断 + 自适应学习，post-commit warn 无法挽回已入历史 commit）。规则真源：[`trae_068_preventability_layer.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_068_preventability_layer.yaml)。前 5 层断裂发现 7 个 Gap（G1-G7）：直接 commit 路径漏传 commit_message（G1）→ 逃生标记永远不触发；rule_discovery 未注册到 mcp.json（G2）→ AI 无法调用；capability_lookup.py 不写审计日志（G3）→ Phase 3.4a 半成品；AGENTS.md 无条款（G4，本节治本）；trae_*.yaml 无规则定义（G5）；`.runtime/lookup_audit/` 空目录（G6，铁证）；无启动 smoke test（G7）。第 6 层"可预防性"首批落地：`heartbeat_daemon`（stale session 90s 自动释放，#ARCH-HEARTBEAT-001）、`emergency_commit` 成本递增、pre-commit forgery gate（Phase 2 待立项）。
>
> **逃生通道（可逃生性，治本 G1/G4 后已可用）**：
> 1. **常规逃生**（推荐，留痕可追溯）：commit message 含 `[no-lookup:<reason>]` 标记——`<reason>` 必填非空（如 `[no-lookup:hotfix-xxx]`），由 [`capability_lookup_required_gate.py:91`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/capability_lookup_required_gate.py) `_BYPASS_MARKER_PREFIX = "[no-lookup:"` 检测。reason 持久化到 git commit log。
> 2. **紧急逃生**（不推荐，仅限故障）：环境变量 `ZEPHYR_BYPASS_LOOKUP=1`——绕过 gate 不留 commit 痕迹，须人工事后审计。**Phase 4 升级后**：同一 session 内超过 N 次 `ZEPHYR_BYPASS_LOOKUP=1` commit 强制升级为阻断（POST-COMMIT-GUARD 扩展）。
> 3. **自动豁免**：merge commit / `*.md`-only / `tests/`-only / 非 `src/zephyr/**/*.py` / 非 Zephyr 项目——gate 直接放行。
>
> **审计落盘（可追溯性，治本 G3/G6）**：MCP 接口 `rule_discovery.discover_applicable_rules` 调用时自动写入 JSONL 审计日志到 [`.runtime/lookup_audit/<session_id>.jsonl`](file:///d:/ZephyrAlpha/.runtime/lookup_audit/)，每条 entry 含 `session_id / timestamp / operation / found_rules / discoverer_version`。Phase 2 同步扩展 `capability_lookup.find` Python API 也写审计日志（与 MCP 接口对称）。gate 在 commit 时读取此目录——目录缺失 fail-closed，文件不存在/为空/JSON 损坏均阻断。
>
> **直接路径 vs worktree 路径对称性（治本 G1）**：
> - **直接路径**：`GitCommitGateway.commit()` → `_gate_registry.check_all(commit_message=message)` —— [`git_commit_gateway.py:831`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)（commit `dda0fbc127` 修复）
> - **worktree 路径**：`session_worktree._run_pre_commit_gates` → `_gate_registry.check_all(commit_message=message)` —— [`session_worktree.py:1174`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（原本正确）
>
> **配套启动 smoke test（治本 G7）**：`session_worktree_start` 健康度自检——检测 `capability_lookup_required_gate.py` 能否正常 import、`.runtime/lookup_audit/` 目录是否可写。失败时 AI MUST 上报（escalate）而非静默 workaround（对标 §11.0.3 #ARCH-TOOL-HEALTH-V1）。
>
> **裁定引用**：[`#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml)（P0 严重度，DESIGN-IMPLEMENTATION-GAP 类型，含子裁定 S1-S7 对应 7 个 Gap 治本）。
>
> **逃生场景分类（#ARCH-CAPABILITY-LOOKUP-SCENE-CLASSIFY-001，TRAE-077）**：gate-time 和 post-commit reconciler 均按白名单关键词区分合法/违规——合法 bypass（`scene=exempt`）豁免统计且 gate 放行，违规 bypass（`scene=violation`）gate **硬阻断** + reconciler 计入统计。critical_warn 只在违规 bypass 超 5 次时触发（合法 bypass 不触发）。规则真源：[`trae_077_capability_lookup_scene_classify.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_077_capability_lookup_scene_classify.yaml)（v2.0.0，`code_loaded_from_yaml`）。**策略共享模块**：[`capability_lookup_bypass_policy.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/capability_lookup_bypass_policy.py)（#ARCH-066 治本）——gate 和 reconciler 共用此模块加载白名单/阈值/标记前缀，消除双真源漂移。白名单关键词（reason 含任一即豁免，`is_exempt_reason()` 执行 `_`→`-` 归一化后子串匹配）：`gate-fix` / `test-fix` / `merge-prep` / `continuation`（已批准裁定续作）/ `investigated`（bug 修复已调研）/ `auto-fix` / `batch-treatment` / `batch-governance` / `architectural-refactor` / `sync` / `mechanical` / `completing` / `research` / `bugfix` / `root-cause` / `调研`。新增合法场景时 MUST 仅更新 [`trae_077`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_077_capability_lookup_scene_classify.yaml) YAML 的 `bypass_exempt_keywords` 列表——共享模块的 `load_bypass_policy()` 自动加载，无需改代码。病根：gate-time 零摩擦放行 vs post-commit reconciler 无牙警告的结构性不对称——治本后 gate 直接检查白名单，非白名单 reason 硬阻断。

## RULE-SCHEMA-TZ：第九件事（时区防线，schema 类型标准化铁律，#ARCH-CH-022，2026-07-24 治本）

> **全库 DateTime 列 MUST 使用 DateTime64(3) + 显式时区**——系统列用 `DateTime64(3, 'UTC')`，业务列用 `DateTime64(3, 'Asia/Shanghai')`。禁止裸 `DateTime`（无时区声明，歧义温床）。
>
> **病根（第一性原理）**：全库 DateTime 列存在 UTC/北京时间混存——业务时间戳（trade_time/timestamp 等）按北京墙钟写入但以 UTC epoch 存储（晚 8 小时），系统时间戳（ingest_ts/updated_at 用 `now()` 为真 UTC）。导致 `now()-trade_time` 等算术差 8 小时，schema 未声明时区（歧义）。迁移后：业务列 `toUnixTimestamp(trade_time)` 等于真实 UTC 瞬时；`toTimezone(trade_time,'Asia/Shanghai')` 显示北京墙钟；插入 naive 北京字符串（ch_writer `str()` 路径）自动按列时区解析为正确 epoch——无需改写入端代码。
>
> **迁移工具（已落地 production）**：[`apply_timezone_migration.py`](file:///d:/ZephyrAlpha/scripts/ch/apply_timezone_migration.py) ——五阶段执行：①system（125 列类型标注）②version-col（17 表 ReplacingMergeTree 版本列重建）③business（4 列 ALTER UPDATE -8h + MODIFY）④recreate（20 表键列重建）⑤tickdata（1 表 181GiB 分区批量重建）。`--dry-run`（全库扫描+策略输出+0写入）/ `--verify`（类型+epoch+行数对账）/ `--phase <name>`（分阶段执行）。
>
> **迁移完成状态（2026-07-24）**：全库 101 表迁移完成——125 系统列 + 28 业务列 + 17 版本列 + 20 键列表 + 1 tick_data(181GiB) 全部迁移，裸 DateTime 残留=0，tick_data 14.38B 行迁移无丢失。验证报告：[`data_consolidation_report.md`](file:///d:/ZephyrAlpha/docs/_working/data_consolidation_report.md)。
>
> **AI 合规**：新建表 DDL（`schemas/categories/*.py`）MUST 按上述时区类型声明 `DateTime64(3, '<tz>')`；已有表 schema 变更 MUST 同步更新 DDL 真源文件 + 运行 `apply_timezone_migration.py --verify` 确认无残留。

## RULE-SECRETS：第十件事（密钥管理可发现性，#ARCH-SECRETS-GOV-001，2026-08-04 治本）

> **密钥放 `.env` 文件（已 gitignore），用 `secrets.py` 接口读取，禁止裸 `os.getenv`。** 新 AI 冷启动**务必先读 [`SECRETS.md`](file:///d:/ZephyrAlpha/SECRETS.md)（密钥管理显性入口）**——它列出全部密钥文件分布、读取接口决策树、新增密钥三步流程。
>
> **病根（第一性原理）**：100% AI 开发场景下，AI 每次会话冷启动，无法像人类工程师记住"项目有哪些密钥、放哪里、怎么读"。原体系靠 `bare_getenv_gate` 事后拦截违规——AI 写错代码被拦才知道规则，是"事后惩罚"而非"事前引导"。治本三阶段（裁定 S-1/S-2/S-3/S-4）：
> - **可知性**（Phase 1）：[`SECRETS.md`](file:///d:/ZephyrAlpha/SECRETS.md) 显性文档 + [`config/secret_registry.yaml`](file:///d:/ZephyrAlpha/config/secret_registry.yaml) 结构化注册表 + `.env.example` 模板
> - **可达性**（Phase 2-S2）：[`secrets.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/security/secrets.py) 便捷接口 `get_required_secret` / `get_service_secret` / `get_secret_or_default`
> - **可审计性 + 纵深防御**（Phase 2-S3 / Phase 3）：三道 commit-time in-process gate 硬阻断
>
> **三道 gate 防线（commit 阶段硬阻断，`--no-verify` 无法绕过）**：
> | priority | gate_id | 检测 | 互补关系 |
> |---|---|---|---|
> | 81 | `NO-BARE-GETENV` | 裸 `os.getenv`/`os.environ.get`/`os.environ["KEY"]` 读密钥（diff-aware：新增+修改文件 added 行） | 读密钥**方式**违规 |
> | 127 | `SECRET-REGISTRY-CONSISTENCY` | `.env.example` ↔ `secret_registry.yaml` 的 KEY 不一致 | 新增密钥遗漏文档化/注册 |
> | 128 | `NO-SECRET-HARDCODE` | 硬编码密钥值（`sk-`/`AKIA`/`ghp_`/`KEY="value"`，扫 .py/.yaml/.yml/.json/.toml） | 密钥**值**硬编码 |
>
> **AI 合规**：①读 [`SECRETS.md`](file:///d:/ZephyrAlpha/SECRETS.md) 知全貌；②读密钥用 `from zephyr.shared.security.secrets import get_required_secret`（第三方 token）/ `get_service_secret("KEY", "postgres")`（基础设施凭证），**禁止裸 `os.getenv`**；③新增密钥三步走（加 KEY 到 .env → 更新 .env.example → 更新 config/secret_registry.yaml），缺任一步被 `SECRET-REGISTRY-CONSISTENCY` 阻断；④密钥值禁止硬编码到代码/配置，被 `NO-SECRET-HARDCODE` 阻断。

## RULE-CLONEGUARD：第十二件事（代码克隆检测四层防御，治 AI 重复造轮子，#ARCH-FORCE-MERGE-DEDUP-001，2026-08-07 Phase D 闭合）

> **AI 写新函数前 SHOULD 调 `clone_guard.check_before_write` 查重**（L0 源头预防，advisory 不阻断）；**L1 提交时 extract 级克隆（3+副本）由 `CAPABILITY-OVERLAP` 门禁硬阻断**（priority=200，无逃生通道）；**L2 周期审计事件触发**（`python scripts/clone_guard_audit.py`，非 cron，结果派生产物入 `.runtime/clone_guard_audit/` 不入 git）。与第八件事 RULE-CAPABILITY-LOOKUP 互补——前者**能力级**反查（capability token），本规则**代码级**检测（AST 哈希 + CodeSAGE 嵌入 + 语义相似度）。
>
> **病根（第一性原理）**：100% AI 开发 → AI 每会话冷启动无记忆 → 为已解决任务重复生成代码 → 功能重叠"AI Rot"累积 → 维护成本指数增长 + bug 传播。单靠能力反查（第八件事）堵不住函数/片段级语义克隆，须四层防御纵深。
>
> **四层防御（实现现状）**：
> | 层 | 触发 | 强度 | 实现 |
> |---|---|---|---|
> | L0 源头预防 | AI 写代码前 SHOULD 调 MCP | advisory（不阻断） | [`clone_guard.check_before_write`](file:///d:/ZephyrAlpha/src/zephyr/clone_guard/mcp_server.py)（L 只读，返回 findings + import_suggestion 引导复用）+ `search_functions`/`audit_status`/`health_check` |
> | L1 提交拦截 | `git commit` 经 GitCommitGateway | **extract 硬阻断** / review 警告 / acknowledged 跳过 | [`CAPABILITY-OVERLAP` gate](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/capability_overlap_gate.py)（priority=200，全引擎降级 warn-only 兜底，`tests/` 豁免） |
> | L2 周期审计 | 事件触发（手动/CI push） | 派生产物 + reconciler warn | [`orchestrator.audit()`](file:///d:/ZephyrAlpha/src/zephyr/clone_guard/orchestrator.py)（health_score A-F，`.runtime/clone_guard_audit/` 不入 git） |
> | L3 跨边界 | 按需手动 | 占位（vendetect 禁用） | `compare()`（redup + relate prescreen 已启用；vendetect 默认禁用按需触发）。注：`relate_prescreen` 同时驱动 L0 `search_functions`（MCP 按语义搜已有函数引导复用，`clone_guard.yml` 已开启） |
>
> **acknowledged 白名单纪律（合理重复标记，治本 #ARCH-ECHO-GUARD-YML-COMMENT-LOSS）**：经审慎确认的合理克隆（归档双实现/接口适配层），调 MCP [`clone_guard.resolve_finding`](file:///d:/ZephyrAlpha/src/zephyr/clone_guard/mcp_server.py)（`safety_level=M` 写操作）标记。`verdict=intentional`=保留两份（函数变化时重新浮现，非永久豁免）/`dismissed`=非重复（永久豁免）；`note` **强制非空**留痕防滥用。默认走 ruamel round-trip 写 [`echo-guard.yml`](file:///d:/ZephyrAlpha/echo-guard.yml) acknowledged 段（**保留注释**，禁用 echo-guard CLI 的 PyYAML 重写路径丢注释）。acknowledge 仅改工作区文件，**须经 GitCommitGateway 提交持久化**（未提交会被 post-commit restore-to-HEAD 恢复）。禁止用白名单消除当前不想处理的告警——属治理逃逸。
>
> **AI 合规**：①写新函数前调 `clone_guard.check_before_write`，见 `import_suggestion` 优先复用而非新建；②冷启动调 `clone_guard.audit_status` 看累积技术债（6层闭环·可达性）；③遇 extract 级克隆硬阻断时合并去重（**无逃生通道**，区别于第八件事的 `[no-lookup:]`）；④标记合理重复用 `resolve_finding`（intentional/dismissed + note），勿直接改 `echo-guard.yml`；⑤配置真源 [`echo-guard.yml`](file:///d:/ZephyrAlpha/echo-guard.yml) + [`clone_guard.yml`](file:///d:/ZephyrAlpha/clone_guard.yml)，蓝图 [`blueprint.md §6.1`](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/clone_guard/blueprint.md)；⑥**Tier 2 需 `pip install onnxscript`**（echo-guard 0.4.1 未声明，torch 2.13+ dynamo ONNX 导出器必需，缺则 Tier 2 静默降级为 Tier 1-only），详见蓝图 §8.1。

## RULE-GIT-SAFE：Git 安全铁律（2026-08-11 #ARCH-GIT-CLEAN-GUARD-FIX；2026-08-14 wrapper 层落地，65 号 Phase 1）

> **背景**：2026-08-11 灾难——AI 执行 git clean -fd 物理删除多个 untracked 文件。git alias 无法覆盖内置命令（git 2.48.1 Windows 实测确认），alias 拦截全部失效。2026-08-14 wrapper 层施工完成：[`scripts/git_safety_wrapper.ps1`](file:///d:/ZephyrAlpha/scripts/git_safety_wrapper.ps1)（函数集唯一真源）经 [`scripts/install_git_safety_wrapper.ps1`](file:///d:/ZephyrAlpha/scripts/install_git_safety_wrapper.ps1) 幂等安装进 `$PROFILE` 后，下列危险命令在 shell 层硬拦截并落审计（`~/.zephyr_audit/`）。

**所有 AI session MUST 遵守**：

1. **禁止的 git 命令**（阻断/放行边界见 65 号 memo §7.1.1 明细表）：`git clean -f/-fd/-fdx`；`git reset --hard/--merge`（用 `--soft`/`--mixed` 替代）；`git checkout -- <file>`/`HEAD -- <file>`/`checkout .`（切/建分支安全）；`git restore <file>`（`--staged` 安全）；`git stash`（`list`/`show` 只读安全）；`git rm <file>`（`--cached` 安全）；`git branch -D`（用 `-d`）；`git push --force`/`-f`（用 `--force-with-lease`）；`git filter-branch`/`filter-repo`/`reflog expire`/`gc --prune=now|all`（不可逆/抹证据）。
2. **每轮修改后立即 `git add <file>`**：staged 文件不会被 git clean 删除。
3. **修改文件前先加锁**：`python scripts/lock_files.py acquire <file> <session_id>`
4. **完成修改后释放锁**：`python scripts/lock_files.py release <file> <session_id>`
5. **如需执行危险命令**：必须先 commit 所有修改 + 经用户确认 + 用完整路径调用真实 git：`& 'C:\Program Files\Git\cmd\git.exe' clean -fd`
6. **禁止用 $HOME/$PID/$TRUE 等 PowerShell 只读自动变量名作变量名**（Codex `$home` 事故教训）。
7. **wrapper 状态自查**：wrapper 未安装时上述命令在 shell 层无拦截（ops_guard 仍在网关/工具层拦删除原语）——新会话可用 `Get-Command git` 自查（显示 `Function` 即已安装）；未安装报告用户跑 `powershell -File scripts/install_git_safety_wrapper.ps1`。

## 1. 项目概述

ZephyrAlpha 是一个 AI 治理框架。AutoRuntime Core 是其**系统大脑**——负责三层运行时编排、节律调度、健康监控、审计日志、工作编排、自动接入。

## 2. 终极目标

**接入项目里的所有模块、系统、脚本，能灵活运用所有东西。**

衡量标准：孤儿率 = 未接入模块数 / 总模块数 → 目标 = **0%**

## 3. 核心系统

| 系统 | 入口 | 职责 |
|------|------|------|
| AutoRuntime Core | `python -m zephyr.trading` | 系统大脑，调度所有 AI 运行时 |
| PipelineOrchestrator | `zephyr.integration.pipeline_orchestrator` | 管线编排（M1-M11） |
| AgentOrchestrator | `zephyr.trading.orchestrator` | Agent 生命周期管理 |
| TaskRepository | `zephyr.governance.task_repo` | 任务状态机（10 状态） |
| GitCommitGateway | `zephyr.gov_enforcement.rule_bridge.git_commit_gateway` | 全项目唯一合法 git commit 入口（串行锁+stash隔离+GW标记） |
| A2A Protocol | `zephyr.infrastructure.a2a_protocol` | Agent 间通信与冲突解决（MOD-INF-025） |
| LLM 安全网关（LSG） | `zephyr.security.llm_defense.llm_security.gateway` | L1-L8 十层纵深防御，所有 LLM 调用必经安检（RULE-LSG-001） |
| MCP Servers（11 个） | [`config/mcp.json`](file:///d:/ZephyrAlpha/config/mcp.json) | MCP 服务器注册表（含工具列表/安全等级/ACL/限流） |
| Trigger Router（6 触发器） | [`config/trigger_router.yaml`](file:///d:/ZephyrAlpha/config/trigger_router.yaml) | 事件驱动路由表（含 handler/优先级/重试策略） |
| Dashboard (Panel) | `src/zephyr/frontend/dashboard/app_panel.py` | Panel+HoloViz 仪表盘主入口（v3.1.0, #ARCH-047），10 Tab 治理+交易/回测；`panel serve app_panel.py --show --port 5006` |
| Data Source Integrator | `integrator` / `python -m zephyr.data` | 数据源集成器 CLI（MOD-L00-004 §8.4），7 子命令：`status`/`list`/`run`/`rerun-failed`/`pause <source>`/`resume <source>`/`start`；统一管理 8 源 61 任务的自动下载+断点续传+熔断 |
| IntradayRuntime（盘中运行时） | `python -m zephyr.runtime.intraday_main` | 盘中端到端编排器（tick→Redis→因子→H1）：单进程串起 tick_subscriber + IntradayFactorLoop + H1 Redis；启动顺序=tick订阅先(预热Redis)→因子循环后；停止反序(因子先停→订阅后停,保WAL flush)；交易日守卫(`is_trading_day`，`--force` 强制)；SIGINT/SIGTERM 优雅停止。依赖 QMT 终端先就绪，故 `[STARTUP] manual`（与 tick_subscriber 惯例一致）。真源：[`intraday_main.py`](file:///d:/ZephyrAlpha/src/zephyr/runtime/intraday_main.py) |

### 基础设施层（D_INFRA_RUNTIME / D_INFRA_RECOVERY / D_GOVERNANCE）

| 模块 | 入口 | 职责 |
|------|------|------|
| DatabaseService | `zephyr.infrastructure.database_service` | 业务数据库统一访问（ClickHouse/PostgreSQL），禁止裸 `duckdb.connect`。**唯一真源**（MOD-INF-002）；`governance/persistence/database_service.py` 已收敛为 re-export（AI-14 审计 P1 修复） |
| EventBus (M-07) | `zephyr.shared.event_bus` → `bus` 单例 | 事件总线背压控制器，`from zephyr.shared.event_bus import bus` |
| EventStore (RI-13) | `zephyr.infrastructure.event_store` | SQLite 不可篡改审计日志（WAL+SHA256 checksum） |
| CostTracker (RI-15) | `zephyr.infrastructure.cost_tracker` | Token/API 调用成本实时监控+日预算告警 |
| SLAMonitor | `zephyr.infrastructure.sla.sla_monitor` | RTO/RPO 自动记录（事件驱动：pipeline_failed→rollback_completed），目标见 `config/sla_targets.yaml` |
| HealthAggregator | `zephyr.infrastructure.system_telemetry.health_aggregator` | 12 系统三态探针（alive/ready/degraded），15s 轮询 |
| Notifier | `zephyr.infrastructure.observability.notifier` | 多渠道 Owner 通知（事件驱动：pipeline_failed/kill_switch_triggered） |
| RollbackBootIntegration | `zephyr.infrastructure.rollback.rollback_boot_integration` | WAL/Verifier 自动初始化+回滚完成后 WAL GC |
| FixScheduler | `zephyr.infrastructure.auto_fix_engine.fix_scheduler` | 自动修复调度（EVENT_DRIVEN 模式，CONTINUOUS 弃用） |
| KillSwitch (SSoT) | `zephyr.security.access_control.kill_switch` | 系统级熔断器（canonical），`get_kill_switch()` 单例 |
| A2A Protocol | `zephyr.infrastructure.a2a_protocol` | Agent 间三层协调（通信/冲突/治理），AgentCard 注册 |
| BaseMCPServer | `zephyr.integration.mcp._base_server` | JSON-RPC 2.0 over stdio MCP 基类（含工具版本化/废弃策略） |

> **永久系统四要素**：所有基础设施永久系统必须满足自动触发/自动运行/自动维护/自动关闭。禁止时间触发（cron/Timer/sleep-loop），所有 reconciler 必须事件触发。启动接线见 [`boot_hooks.py`](file:///d:/ZephyrAlpha/src/zephyr/trading/boot_hooks.py)（`register_boot_hooks()`）。

> **代码归类表（C 类边界显式化，2026-07-17 治本）**：审查 0.5 节改动分类时，按此表判定代码归属，禁止凭印象推断。C 类"永久系统/常驻服务"特指**有状态+需持续运行+需自动维护/关闭**的基础设施系统。

| 代码类型 | 归类 | 判定依据 |
|---------|------|---------|
| reconciler（post-commit 自动修复） | C 类·永久系统 | 有状态+持续运行+需自动维护/关闭 |
| scheduler/watchdog（常驻守护） | C 类·永久系统 | 有状态+常驻内存 |
| boot_hooks 事件钩子 | C 类·永久系统 | 永久注册+自动触发 |
| commit gate（pre-commit 检查函数） | B 类·事件触发无状态函数 | 无状态+事件触发+运行即结束，无"关闭"概念 |
| 一次性运维/诊断/迁移脚本 | A 类·非永久 | trae_060 §6 not_applies_to |
| 测试夹具/常量 | A 类·非规则数据 | trae_060 §6 not_applies_to |

> **常驻守护服务（watchdog 三服务 + 死人开关 + 工作区漂移看门狗，C 类·永久系统）**：五个 Task Scheduler 任务构成 7×24 守护体系（前四个=数据层，漂移看门狗=治理执行域），均经一次性脚本注册（前四个经 [`register_guard_tasks.ps1`](file:///d:/ZephyrAlpha/scripts/register_guard_tasks.ps1)，漂移看门狗经 register_drift_watchdog_task.ps1，AtLogOn 事件触发 + 5min repeat 兜底）。前 3 服务（watchdog 三服务）`MultipleInstances=Parallel`（#ARCH-BOOT-001 治本）：脚本级 PID 锁+心跳为单实例 SSoT，Task Scheduler 退化为无脑周期触发器（IgnoreNew 会阻断僵尸 guard 接管，导致 08-06/08-07 两交易日 intraday 停摆）。watchdog 的 5min repeat + 15s sleep 轮询属 **OS 进程监管时间退避例外**（非 reconciler 事件触发约束范围，对标 #ARCH-CH-PROBE-GUARD "5min repeat 属兜底"先例）。四层防御+心跳接管细节见 [`boot_autostart_architecture.md §3/§8`](file:///d:/ZephyrAlpha/docs/03_modules/_domain_data/boot_autostart_architecture.md)。
>
> | 服务 | Task Scheduler 任务名 | guard 脚本 | 说明 |
> |------|----------------------|-----------|------|
> | 数据调度器 | ZephyrAlpha_DataScheduler | [`start_scheduler.ps1`](file:///d:/ZephyrAlpha/scripts/start_scheduler.ps1) | 数据集成器调度（日频/增量任务编排） |
> | Tick 订阅器 | ZephyrAlpha_TickSubscriber | [`start_tick_subscriber.ps1`](file:///d:/ZephyrAlpha/scripts/start_tick_subscriber.ps1) | 实时行情订阅（盘中 tick→Redis/WAL） |
> | CH 健康探针 | ZephyrAlpha_CHHealthProbe | [`start_ch_health_probe.ps1`](file:///d:/ZephyrAlpha/scripts/start_ch_health_probe.ps1) | CH 连通性监控（3s TCP+HTTP 双通道探测） |
> | 死人开关 | ZephyrAlpha_DeadmanSwitch | [`deadman_switch.ps1`](file:///d:/ZephyrAlpha/scripts/deadman_switch.ps1) | 心跳陈旧监控（一次性任务，5min fire，任一 heartbeat >10min 飞书+EventLog 告警） |
> | 工作区漂移看门狗 | ZephyrAlpha_WorktreeDriftWatchdog | [`register_drift_watchdog_task.ps1`](file:///d:/ZephyrAlpha/scripts/register_drift_watchdog_task.ps1)（声明式注册；无 guard 脚本，pythonw 直起 daemon） | tracked 漂移周期扫描（#99② 退避治本：RestartCount=3+RestartInterval=10min 固化任务定义，单实例 SSoT=daemon 字节锁，双触发器 5min repeat） |
>
> **死人开关（#ARCH-BOOT-002 E，2026-08-08 治本）**：watchdog 三服务的四层防御闭合了 guard 级僵尸接管，但**未闭合系统级失效**——若 3 服务全死，心跳文件陈旧但无人读。治本：`deadman_switch.ps1` 是无状态一次性任务（非 while-true guard，无僵尸风险），每 5min fire 读 3 个心跳文件，任一陈旧 >10min 即飞书+EventLog+本地日志三通道告警（30min 冷却防刷屏）。独立性第一性原理：监控者不属被监控 3 服务之一，只读心跳；用 `.ps1` 而非 `.py`——若 Python 栈崩溃 `.py` 监控会跟着死。
>
> **CH 健康探针三层守护链（#ARCH-CH-PROBE-GUARD，2026-08-03 治本）**：① Task Scheduler（OS 级，AtLogOn+5min 兜底）→ ② guard 脚本（单实例锁+孤儿清理+while-true auto-restart，启动失败<10s 退避 30s）→ ③ probe 进程（3s 探测 CH TCP+HTTP，断连 6s 告警）。**启动/重启**：`schtasks /run /tn ZephyrAlpha_CHHealthProbe`（禁止从 IDE 终端 Start-Process，会随终端死亡）。**状态查询**：`schtasks /query /tn ZephyrAlpha_CHHealthProbe /fo LIST`。日志：probe→`logs/ch_health_probe.log`，guard→`tmp/ch_health_probe_guard.log`。治本背景：8/2 探针无 guard 保活，死后 13h 监控空窗。

> **reconcile_execution_log 自愈机制（#AUTO-ACK-HEALED-WARN + #RECONCILE-LOG-RETENTION，2026-07-23 治本）**：[`reconciliation_registry.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) 的 `_log_reconcile_results` 在插入 `clean` 记录时，自动回填同 gate 前置已愈合 `critical_warn` 的 `acknowledged_at`（EXISTS 子查询，与查询时 NOT EXISTS 自愈语义对称），消除"已愈合但永不 ack"的审计假阳性；超 50K 记录自动清理 180 天前旧记录（fail-open）。**datetime→sqlite3 适配器（#SQLITE-DATETIME-ADAPTER，2026-07-24 治本）**：[`time_utils.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/time_utils.py) 模块级注册 `sqlite3.register_adapter(datetime, str)`（Python 3.12 default adapter deprecated 治本），`now_utc()` 传给 sqlite3 自动适配为空格分隔 str（与默认 `isoformat(" ")` 零行为变更）。显式 str 时间戳用 `now_utc_str()`。

> **审查跳过条款真源引用铁律（2026-07-17 治本）**：审查报告 0.5 节跳过条款时，跳过理由 MUST 引用真源文件路径+稳定锚点（section/key/函数名）+原文摘录证明分类正确，禁止"仅 X 类，本次非 X 类"循环论证。合规格式示例：跳过 1.4-1.6（仅 C 类）——依据 [`trae_060` §3 事件驱动全自动](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml) "永久性系统/功能脚本"+ AGENTS.md 代码归类表，commit gate 属 B 类事件触发无状态函数，非 C 类。

> MCP 服务器完整定义（工具清单/角色权限/熔断配置）见 [`config/mcp.json`](file:///d:/ZephyrAlpha/config/mcp.json)。触发器路由表（6 触发器+处理器+安全等级）见 [`config/trigger_router.yaml`](file:///d:/ZephyrAlpha/config/trigger_router.yaml)。

### 因子信号域（D_FACTOR / D_ASHARE_SIGNAL / D_FUNDAMENTAL_SIGNAL / D_SIGQC，2026-07-06 AI-08 补登，2026-07-17 AI-08 补登 D_ASHARE_SIGNAL）

4 个平级信号子域（域注册表 `functional_domain_registry.yaml` 的 `D_SIGNAL`/`D_FACTOR` 等 domain 条目；D_FACTOR 见 `cross_layer_contracts.yaml`）。ARCH-045 裁定：D_SIGLEGACY 已删除，signal 层拆分为 3 个平级子域。

| 域 | ssot_path | 职责 | 关键入口 |
|----|-----------|------|----------|
| D_FACTOR | `src/zephyr/factor/` | 因子抽象 + 注册表 + 示例因子 | [`factor_base.py`](file:///d:/ZephyrAlpha/src/zephyr/factor/factor_base.py)（FactorBase/FactorRegistry，compute(data)→Series 协议） |
| D_ASHARE_SIGNAL | `src/zephyr/signal_ashare/` | A股特色信号（主力行为/量价/技术指标，planning stub） | [`__init__.py`](file:///d:/ZephyrAlpha/src/zephyr/signal_ashare/__init__.py)（MOD-INF-038，MATURITY=design，仅骨架占位） |
| D_FUNDAMENTAL_SIGNAL | `src/zephyr/signal_fundamental/` | 信号合成/聚合/资本分配管道 | [`pipeline.py`](file:///d:/ZephyrAlpha/src/zephyr/signal_fundamental/pipeline.py)（AlphaSignalPipeline，因子协议 compute(self)→list，非 FactorBase） |
| D_SIGQC | `src/zephyr/signal_quality/` | 信号质量评估/降级监视/过滤/冲洗监视 | [`degradation_monitor_base.py`](file:///d:/ZephyrAlpha/src/zephyr/signal_quality/degradation_monitor_base.py)（DegradationMonitorBase，2026-07-06 从 D_FUNDAMENTAL_SIGNAL 迁入） |

**关键契约**：CTR-ERR-003（SignalDegradationWarning，source_domain=D_SIGQC，[`cross_layer_contracts.yaml`](file:///d:/ZephyrAlpha/architecture_model/contracts/cross_layer_contracts.yaml) `id: CTR-ERR-003` 条目）。
**capability 反查**：`factor_base_abstraction` / `alpha_signal_pipeline` / `signal_synthesizer_base` / `degradation_monitor_base`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)）。新 AI 实现因子/信号/降级监视器前 MUST 反查此 4 项 capability，禁止重复造轮子。

### 执行模拟域（D_EX_CORE / D_EX_SOR / D_EXEC_SIM / D_CROSS_ASSET / D_DIGITAL_TWIN，2026-07-17 AI-05 补登）

5 个执行/模拟相关平级域（域注册表 `architecture_model/index.yaml` 的 `D_EX_CORE`/`D_EXEC_SIM`/`D_SIMULATION`/`D_SELL_DECISION` 等 `id` 条目）。**仅 D_EX_CORE 已施工**，其余 4 域为规划态占位（planning stub，无蓝图/无代码/无消费者）。

| 域 | ssot_path | 状态 | 关键入口 |
|----|-----------|------|----------|
| D_EX_CORE | `src/zephyr/ex_core/` | partially_implemented | [`execution_engine.py`](file:///d:/ZephyrAlpha/src/zephyr/ex_core/execution_engine.py)（ExecutionEngine，broker 选择+订单分发）/ [`order_manager.py`](file:///d:/ZephyrAlpha/src/zephyr/ex_core/order_manager.py)（OrderManager，订单状态机+撤单路由）/ [`adapters/miniqmt_broker.py`](file:///d:/ZephyrAlpha/src/zephyr/ex_core/adapters/miniqmt_broker.py)（MiniQmtBroker，迅投 xttrader 实盘适配器，threading.Lock 线程安全） |
| D_EX_SOR | `src/zephyr/ex_sor/` | design (planning stub) | 待施工：执行路由（SMART Order Routing） |
| D_EXEC_SIM | `src/zephyr/execution_simulation/` | design (planning stub) | 待施工：执行仿真 |
| D_CROSS_ASSET | `src/zephyr/cross_asset/` | design (planning stub) | 待施工：跨资产 |
| D_DIGITAL_TWIN | `src/zephyr/digital_twin/` | design (planning stub) | 待施工：数字孪生 |

**关键契约**：
- [`broker_interface.py`](file:///d:/ZephyrAlpha/src/zephyr/trading/trading_contracts/broker_interface.py)（BrokerInterface 抽象基类，canonical 路径 `src/zephyr/trading/trading_contracts/`，ARCH-GOV-SHIM-001 迁移）
- [`matching_logic.py`](file:///d:/ZephyrAlpha/src/zephyr/backtest/core/matching_logic.py)（MatchingLogic 共享模块，回测-实盘一致性 B 方案：MiniQmtBroker.submit_order 复用 match_market_order/match_limit_order 预校验）
- [`order.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/contracts/order.py)（Order dataclass，CTR-004 codegen，SSoT=cross_layer_contracts.yaml）
- 5 个核心数据契约（market_data/factor_signal/factor_monitor_report/macro_factor_signal/synthesized_signal）canonical 路径 `src/zephyr/shared/contracts/`（codegen SSoT，ARCH-DATA-SSOT-001 归一，详见 architecture_issue_registry.yaml）

**线程安全**：MiniQmtBroker 用 `threading.Lock` 保护所有 xttrader 调用与共享状态（`_connected`/`_xttrader`/`_account_id`）。新 AI 实现券商适配器 MUST 继承 BrokerInterface 并在所有 xttrader 调用点加锁。

**撤单路由治本（2026-07-17）**：OrderManager 维护 `_order_broker_map`（order_id→broker_id），submit_order/create_order 时记录，cancel_order 时精确路由。禁止硬编码 broker_id 或遍历反查。

**蓝图**：[`_domain_execution_core/blueprint.md`](file:///d:/ZephyrAlpha/docs/03_modules/_domain_execution_core/blueprint.md)（MOD-L06-001，version 2.2.1）/ [`_domain_simulation/blueprint.md`](file:///d:/ZephyrAlpha/docs/03_modules/_domain_simulation/blueprint.md)（MOD-L13-001）。4 个 planning stub 域无蓝图，施工前 MUST 先创建 blueprint.md。

### config/ 发现契约（ARCH-038 P2）

新 AI 需发现 `config/` 下有哪些配置文件、用途线索、消费者时，运行：

```bash
python scripts/governance/d1_structure/validate_config_integrity.py --list-configs
```

输出 YAML 清单（按需生成，不持久化），每个文件含：`path`（相对路径）、`type`（yaml/yml/json）、`size_bytes`、`top_keys`（YAML 顶层 keys，用途线索）、`protected_by`（CBAC 保护状态）、`consumers`（代码中引用此文件的位置，最多 5 个）。向内收逻辑：复用 L1 枚举，无持久化文件，无维护成本。

## 4. 发现可用服务

```python
from zephyr.trading.capability_registry import CapabilityRegistry
registry = CapabilityRegistry()
all_capabilities = registry.list_all()
inference_caps = registry.find_by_tags(["inference", "text"])
a2a_caps = registry.find_by_tags(["a2a", "coordination"])
```

### 4.1 Agent 间通信（A2A Protocol）

```python
from zephyr.infrastructure.a2a_protocol import a2a_card_registry
agents = a2a_card_registry.discover(capability="write")

from zephyr.infrastructure.a2a_protocol.layer2_communication.a2a_schemas import A2AMessage, A2AMessagePart, PartType
msg = A2AMessage(from_agent="your-id", to_agent="target-id", task_id="t-1")

from zephyr.infrastructure.a2a_protocol.layer3_coordination.conflict_detector import ConflictDetector, ChangeSet
from zephyr.infrastructure.a2a_protocol.layer3_coordination.arbitrator import Arbitrator, AgentMeta, AgentRole
```

### 4.2 LLM 安全网关（RULE-LSG-001：强制调用）

> **铁律：所有 LLM 调用必须经过 LSGSecurityGateway。禁止裸调任何 LLM API。**
> 违反此规则会被 GATE-20 pre-commit 门禁硬阻断。

```python
from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway
from zephyr.security.llm_defense.llm_security.protocol import SecurityDecision

gateway = LSGSecurityGateway()

# 输入扫描：用户输入给 LLM 前先过安检
result = await gateway.scan_input(user_text, metadata={"provider": "openai"})
if result.decision == SecurityDecision.DENY:
    raise ValueError(f"输入被拦截: {result.reason}")

# 输出扫描：LLM 返回内容给用户前先过安检
result = await gateway.scan_output(llm_response)
if result.decision == SecurityDecision.DENY:
    llm_response = "[内容被安全策略过滤]"

# 全量扫描：输入+输出流水线
result = await gateway.full_scan(user_text, llm_response)
```

**参考实现（带重试机制）**：`src/zephyr/autonomy_core/llm_gateway.py` 中的 `_lsg_scan_input_sync` / `_lsg_scan_output_sync` 模式。

**GATE-20**：`python scripts/governance/d7_code/detect_direct_llm_calls.py --ci` — AST 扫描 src/zephyr/ 下所有裸调，已导入 LSG 的放行，未导入的阻断。pre-commit 用 `--staged` 变更检测（只扫 staged .py，6.5s→亚秒），CI 用 `--ci` 全量。

#### 4.2.1 运行时 Gate（GATE-20 后备防线）

> **GATE-20 是 pre-commit 静态门禁，存在不可修复的静态分析上限**：当代码内容在运行时
> 从外部（文件/网络/数据库）获取再 `exec` 时，AST 层面不可见。运行时 Gate 作为后备防线，
> 在 Python 进程运行时拦截所有绕过 LSG 的裸调 LLM API 调用。

- **真源**：[runtime_interceptor.py](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py)
- **启动引导**：[sitecustomize.py](file:///d:/ZephyrAlpha/sitecustomize.py)（Python 解释器启动时自动 `install()`，零业务侵入）
- **机制（方案 A+B 融合）**：sitecustomize 自动引导 → `sys.meta_path` finder 拦截 openai/anthropic/litellm/langchain 导入 → 加载后 monkey-patch 核心调用方法（`chat.completions.create` / `messages.create` / `litellm.completion` 等）→ 调用时检查 LSG 放行令牌（`contextvar` + `threading.local` 混合存储，TTL 30s）→ 缺失令牌抛 `BareLLMCallError` 硬阻断
- **令牌颁发**：LSG 的 `scan_input` / `full_scan` / `scan_agent_action` 在返回 `ALLOW` 时自动调用 `grant_allowance()`（[gateway.py](file:///d:/ZephyrAlpha/src/zephyr/security/llm_defense/llm_security/gateway.py) 单点注入，业务代码无感知）
- **kill-switch**：`ZEPHYR_RUNTIME_GATE=0` 关闭（sitecustomize 层 + install() 层双重尊重）
- **部署说明**：cwd=repo root 时自动生效（`python -m pytest` / `python -c` / `python -m zephyr...` / repo root 脚本）。运行 `python scripts/sub/foo.py`（sys.path[0]=脚本目录）需 `PYTHONPATH=<repo_root>`
- **测试**：`pytest tests/llm_security/test_runtime_interceptor.py`（含红蓝对抗：`code = read_file("payload.txt"); exec(code)` 运行时被拦截）
- **能力注册**：`runtime_llm_call_interceptor`（capability_canonical_file_registry.yaml）

### 4.3 RULE-TWO 注册审计（孤儿检测防线 2）

> **防线 2**：注册表（`__all__` / `script-manifest.yaml` / `_registry.yaml`）+ 自动审计。
> 防线 1 是 GATE-20 运行时拦截（§4.2.1），防线 3 是 N-16 文件名唯一性。

- **真源**：[audit_registration.py](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/audit_registration.py)
- **机制**：扫描磁盘 `.py`/`.yaml` 对比三个注册表，检测孤儿文件 / 僵尸引用 / 缺 `__all__`
- **审计范围（单一真源 `_in_audit_scope`）**：仅 `src/zephyr/` 与 `scripts/` 下文件；其他目录（`tests/`/`docs/`/根级）不扫。`--incremental`、`--files`、post-commit reconciler 三处 scope 过滤统一委托该函数，勿重复实现
- **RULE-TWO 豁免**：被其他模块 `import` 的文件视为"已有自然发现机制"，不报为 ORPHAN。消费者地图由 `_batch_collect_imports()` 构建，扫描范围 `src/`+`scripts/`+`tests/`+**根级 `*.py`**（如 `sitecustomize.py` 是系统级消费者，漏扫根级会导致 RULE-TWO 豁免失效 → 误报 orphan）
  - **消费者地图构建（双路径回退）**：优先使用 `rg`（ripgrep，快速路径），`rg` 不可用时自动回退到 Python `ast` 解析（`_collect_imports_via_ast()`，零外部依赖，跨环境一致）。消除 `rg` 不在 PATH 时静默返回空 map → RULE-TWO 豁免失效 → 误报 orphan 的脆弱性
- **post-commit reconciler**：`make_registry_sync_reconciler`（AD-GOV-001 合并后，GATE-REGISTRY-SYNC 统一入口，见 [reconciliation_registry.py](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)）在 commit 后自动触发，用 `--files <committed_files>` 精确扫描本次提交文件
  - **触发条件**：committed_files 含 `src/zephyr/*.py` 或 `scripts/governance/*.py`（注意：比 audit scope 窄，仅 governance 相关 commit 触发）
  - **禁用 `--incremental`**：它会扫工作树全部 WIP（`git diff HEAD` + 未跟踪），把与本次 commit 无关的 WIP 误判为 NEW orphan（历史 Bug：`runtime_interceptor.py` 为 WIP 未提交却被扫到）
  - **scope 过滤单一真源**：reconciler 仅筛 `.py`，scope 过滤委托 audit 的 `_in_audit_scope`（不重复过滤，避免漂移）
- **基线差分**：`--baseline-aware` 对比基线分类 NEW/RESOLVED/PERSISTENT，仅 NEW 阻断（exit 1），PERSISTENT 降级告警（exit 0）
- **双基线系统（勿混淆，防误判漂移）**：
  - `audit_registration_baseline.jsonl` — 本审计独立基线，`meta_path=None`（**从不写** `baseline_meta.json`）
  - `current_baseline.jsonl` + `baseline_meta.json` — `manage_baseline.py` 的独立系统（追踪 `phase_e_full` 等全量基线）
  - 两者独立，`baseline_meta.json` 的 `finding_count` 与 `audit_registration_baseline.jsonl` 行数**无关**，勿误判为漂移

### 4.4 能力反查与符号发现（ARCH-031 局限2 文档化，2026-07-01）

新 AI 进入项目后，发现已有功能/符号有两个互补手段，职责边界明确：

- **能力发现（CapabilityLookup）**：查"某个能力是否存在 + canonical 真源在哪"。
  - 真源：[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)（已声明能力持续扩充——实时条目数以注册表为准，2026-08-15 时点 347 条）
  - 用法：`from zephyr.governance.capability_lookup import CapabilityLookup; CapabilityLookup().find("handoff")`
  - 覆盖范围：仅已声明 capability_id 的功能。子目录文件（如 `audit_trail/agent_signer.py`）默认未声明，查不到。
  - 何时用：新 AI 想做"X 功能"前，反查是否已有该能力的 canonical 实现。

- **符号发现（Grep）**：查"某个符号（函数名/类名/常量）定义在哪"。
  - 用法：`Grep "class AgentSigner"` 或 `Grep "def agent_signer"`
  - 覆盖范围：`src/zephyr/**/*.py` 全部文件（含未声明能力的子目录文件）。
  - 何时用：新 AI 知道符号名时，直接 Grep 即可唯一命中 canonical 位置。
  - 已验证：`agent_signer`、`changelog_manager`、`self_healer` 等 7 个子目录符号 Grep 均唯一命中 canonical。

- **为什么不在 YAML 声明所有子目录文件**：维护成本高（governance/ 子目录有 200+ 文件）且无必要——Grep 已能可靠发现符号，CapabilityLookup 重复实现符号发现会破坏职责边界（向内收原则①：能现成不创造）。
- **何时声明新 capability**：当某个功能有明确能力边界、可被复用、且新 AI 可能不知道已存在时（如 `agent_signer`、`self_healer`），才在 YAML 声明 capability 条目。
- **pipeline 模块 canonical 声明**（2026-07-02，消除 `integration/` 与 `infrastructure/pipeline/` dual source 镜像副本）：管线核心13模块（`model_router`/`cost_tracker`/`ct_pipe_routing`/`preemption_manager`/`pipeline_agent_bridge`/`llm_gateway`/`routing_plugins`/`pipeline_lock`/`dead_letter_queue`/`circuit_breaker_manager`/`backpressure_types`/`backpressure_manager`/`pipeline_models`）已登记 capability，canonical = [`src/zephyr/infrastructure/pipeline/`](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/pipeline/)（production/D_INFRA_RUNTIME）。原 `src/zephyr/integration/` 顶层镜像副本（prototype/D_INTEGRATION）已删除。`layer_router`/`layer_consumer_registry` 已于阶段1清除（14层概念废弃）。新 AI 想做"管线模型路由/成本追踪/背压管理/断路器"等前，CapabilityLookup 会反查到 canonical 在 `infrastructure/pipeline/`，勿在 `integration/` 重建。编排器 `PipelineOrchestrator` 例外，仍在 `integration/pipeline_orchestrator.py`（跨域集成入口，组合 infra.pipeline 组件）。
- **red_blue_validator re-export shim canonical 声明**（2026-07-18，裁定#18 + 表头修正治本，消除 `src/zephyr/red-blue-validator/` 连字符目录多真源副本）：保留 [`src/zephyr/red_blue_validator/__init__.py`](file:///d:/ZephyrAlpha/src/zephyr/red_blue_validator/__init__.py) re-export shim（极简，仅从 `zephyr.security.adversarial_validation` 重新导出 `RedBlueValidator`/`ConstitutionArticle`/`ConstitutionGuard`/`ConstitutionViolationError` 4 个符号）。shim 存在原因：测试契约 `test_audit_red_blue_e2e.TestSteadyStateE2E::test_import_time_real_measurement` 直接调用 `ss._import_time("zephyr.red_blue_validator")`，要求该包可导入。真源 = [`src/zephyr/security/adversarial_validation/`](file:///d:/ZephyrAlpha/src/zephyr/security/adversarial_validation/)（MOD-INF-030，D_SECURITY，production）。**禁止事项**：①禁止重建 `src/zephyr/red-blue-validator/` 连字符目录（已删，违反 snake_case 命名铁律）；②禁止修改 shim/真源文件的 `module_id`（统一为 MOD-INF-030，原表头错误值 MOD-INF-005 已于 2026-07-18 修正，原错误传播源头为 `_constitution_registry.yaml`/`_scenario-registry.yaml`/`attack_registry.py`/`__init__.py`/`constitution_guard.py` 5 文件）；③禁止混淆逻辑名（`red-blue-validator` 是 dependency 逻辑名 string key，合法）与物理路径（必须为下划线 `red_blue_validator`/`adversarial_validation`）。测试路径硬编码统一指向真源：`REPO_ROOT / "src" / "zephyr" / "security" / "adversarial_validation" / "_constitution_registry.yaml"`（4 处，分布在 `test_audit_red_blue_e2e.py` 的 `REPO_ROOT / ... / "_constitution_registry.yaml"` 路径硬编码行）。

### 4.5 根目录 vs 子目录同名文件门禁（ARCH-031 局限1 调研结论，2026-07-01）

governance/ 等包的根目录 vs 子目录同名文件（stale duplicate）有三层自动门禁：

- **GATE-SSOT 第1层（check_ssot_conflicts）**：检测同 [MODULE] module_path 冲突。
  - 新 AI 创建根目录文件且 [MODULE] 标注与子目录文件相同时**硬阻断**。
  - 真源：文件头部 [MODULE] 字段。
- **GATE-SSOT 第2层（check_capability_duplicates）**：检测 basename 撞 capability_id/alias。
  - 已注册能力的同名文件**硬阻断**（relation=conflicting/sibling）。
  - 真源：capability_canonical_file_registry.yaml + 磁盘扫描派生。
- **CREATE-GUARD**：新建 .py / .yaml / .md / .sh / .ps1 / .mmd / .json 文件必须登记 creation_token（全 7 格式覆盖，ARCH-TTL-DOC-001 阶段 2 治本）。
  - 强制 AI 声明创建意图 + 关联 capability，未登记则**硬阻断**。
  - .yaml 扩展（2026-07-01）：非 rules/ .yaml 亦需 token（.yaml 是 YAML→DB 单向同步真源，第二份配置真源漂移污染 9 个 readonly DB 表）；rules/ .yaml 走命名检查不走 token。
  - 全 7 格式扩展（2026-07-17，ARCH-TTL-DOC-001 阶段 2）：.md / .sh / .ps1 / .mmd / .json 亦需 token（防造第二文档/脚本/配置真源）；tests/ 豁免（测试非能力真源）。

**剩余缺口**：新 AI 创建根目录文件、[MODULE] 标注为根目录路径、文件名与子目录文件相同但未注册 capability 时，三层门禁均不触发。此缺口由本节提示 + governance/__init__.py docstring 文件归属规则提示兜底。

**N-16 扩展到 src/ 不可行**：src/zephyr/ 有 500 个同名 basename（含 499 个 __init__.py），豁免清单规模过大，维护成本高于收益。N-16 仍只覆盖 tests/ + docs/。

### 4.6 governance/ 根目录防平铺门禁（ARCH-031 P3 防复发，2026-07-02；2026-07-17 shim 消除同步）

`src/zephyr/governance/` 根目录**禁止新增 .py 文件**（含 rename 到根目录）。治本前根目录平铺 33 个 .py 文件，治本后迁移 24 文件到 12 功能子目录，仅保留高风险核心模块。2026-07-17 shim 消除治本（commit 213be2b5a3）进一步删除 `base.py`/`merkle_hourly.py`/`performance_attribution_report.py` 三个 re-export shim 文件，根 .py 文件数从 9 降至 6：

| 保留文件 | 原因 |
|----------|------|
| `__init__.py` | 包标记 |
| `capability_lookup.py` | 能力反查引擎（消费者 76+） |
| `depgraph_schema.py` | depgraph schema（消费者 156+） |
| `evidence_pack.py` | 审计证据包 |
| `integrity.py` | 完整性校验（消费者 119+） |
| `rule_patterns.py` | 治理规则正则 + 安全审计模式唯一真源（SSoT，被 create_guard / r5_digit_suffix_gate / validate_directory_structure / validate_rule_frontmatter + 三包 kb_gate/privacy 共同 import；含 PIICategory/POISONING_INDICATORS/PII_PATTERNS，原 security_patterns.py 已合并 ARCH-033） |

**门禁**：CREATE-GUARD 扩展检测（[`create_guard.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/create_guard.py)）——staged 新增(A) + rename(R) .py 文件路径匹配 `src/zephyr/governance/<name>.py`（`path.count("/")==3`）→ **硬阻断**。错误信息含 "ARCH-031 防复发" + "新模块 MUST 放入子目录"。

**新模块归属规则**：新 .py 文件 MUST 放入对应功能子目录（`audit/` `persistence/` `strategies/` `ops_governance/` `resilience_governance/` `context_governance/` `data_governance/` `engine/` `financial_governance/`）。不确定归属时 Grep `src/zephyr/governance/` 下已有子目录选择最匹配的。注：`commit_gates/`/`trading_contracts/`/`rule_enforcement/` 已分别迁移至 `gov_enforcement/commit_gates/`、`trading/trading_contracts/`、`gov_enforcement/rule_enforcement/`（ARCH-031 P2 + ARCH-GOV-SHIM-001）。

### 4.7 目录平铺容量+前缀簇合规门禁（GOV-DOC-018 ARCH-043 Risk 2-B，2026-07-03）

**痛点**：GOV-DOC-018 规定 T_hard=60/T_soft=120 阈值，>T_hard 的目录享 T_soft=120 需在 `__init__.py` 文档化命名前缀约定。但原 `validate_nested_flat_dirs.py` 只数文件数不检查前缀文档，新 AI 可绕过裁定添加不合规文件，或在未读注释情况下强制拆分已裁定合规的目录。

**门禁**：[`validate_nested_flat_dirs.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_nested_flat_dirs.py) `--check-prefix` 模式——检测 >T_hard(60) 目录的 `__init__.py` 是否文档化命名前缀约定（标记词：`命名规则`/`前缀簇`/`T_soft`/`GOV-DOC-018`/`模块地图`），无约定报 ERROR。

**自动触发**：注册为 `GATE-NESTED-FLAT-PREFIX` 到 [`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)，`src/zephyr/*.py` 变更时 pre-commit 自动运行（事件驱动，全自动，无需手工触发）。`--warn-only` 过渡期（9 个存量违规未清零：8 tests/ + src/zephyr/infrastructure/rollback，清零后转 `--ci` 硬阻断）。

**真源**：阈值 `thresholds.yaml` §directory_scalability（`src_py_warn: 60` / `src_py_error: 120`）；规则 `trae_028_doc_structure_naming.yaml` §directory_scalability。

## 5. 三层 AI 工作分配

- **L1 Trae**: 人在 IDE 交互时使用，免费，人在环
- **L2 Local**: 24/7 自动化，Ollama 本地推理（BGE-M3 + qwen3:8b），零成本
- **L3 API**: 夜班/高价值/不确定，DeepSeek V4 Pro / Claude，有成本

## 6. 关键路径

- `specs/auto_runtime_core/`: AutoRuntime Core 蓝图规范
- `src/zephyr/trading/`: AutoRuntime Core 实现
- `data/audit_logs/`: AI 行为审计日志
- `data/capability_cards/`: 能力卡片定义
- `data/work_dags/`: 工作 DAG 定义（待创建）
- `architecture_model/`（仓库根，单树，2026-06-30 治本合并）: 架构模型 YAML SSoT——72域清单（depgraph 派生）+ 跨层契约（`contracts/`）+ 不变量（`cross_cutting/`）+ `module_id_registry` + 领域事件（`events/`）+ DDD 模型（`domain/`）+ b_track 施工视图（`layers/b_*.yaml`）；72域是唯一物理分类（depgraph），4值（L0_infrastructure/L1_foundation/L2_domain/L3_application）是域的 `layer_id` 属性枚举（真源：`depgraph_schema.py` DB trigger）

### 6.1 目录生命周期（AI-03 审计 P10，2026-07-05）

临时+日志+工具区目录生命周期规则（`.gitignore` 已对齐）：

- **`tmp/`**：task_bound 一次性脚本退役区，运行时产物不入库（`.gitignore` 的 `tmp/*` 规则，仅保留 `tmp/.gitkeep`）。新 AI 在 `tmp/` 创建脚本完成使命后**禁止清理 git rm**（`.gitignore` 已自动忽略）；历史已跟踪脚本通过批量 `git rm --cached` 退役（commit `6846813fac` 退役 21 脚本，2026-07-05 AI-03 审计再次退役 90+ 脚本）。
- **`logs/`**：运行时日志，`.gitignore` 的 `logs/` 规则整目录忽略，禁止入库。
- **`session_logs/`**：Session Log 真源目录（snake_case），与 `session-logs/`（kebab-case，2026-07-05 AI-03 审计已删除）真源唯一；新 session yaml 落盘格式 `session_logs/YYYY/MM/session-YYYYMMDD-NNN.yaml`。
- **`_journals/`**：AI 行为日志（`skill_telemetry.jsonl` / `skill_transitions.jsonl`），`.gitignore` 的 `_journals/` 规则整目录忽略，运行时写入不入库。
- **根目录 `tmp_*` 文件/目录**：AI 会话临时产物（测试输出/调试残留），`.gitignore` `/tmp_*` 规则集全覆盖（文件 8 后缀 + `/tmp_*/` 目录，ARCH-TTL-DOC-001）。**pytest basetemp 已由 conftest.py `pytest_configure` 默认指向 `.runtime/tmp/pytest`**（绝对路径，cwd 无关；尊重 `--basetemp` CLI 覆盖），AI 无需也不应传 `--basetemp=` 或 `--junit-xml=` 根目录相对路径——根目录残留即使被 gitignore 也是可见性黑洞（2026-07-17 清理 12 个 `tmp_clean/tmp_extreme*/tmp_pytest*` 目录；2026-07-22 治本 #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001 清理 33 文件 + 5 ad-hoc 目录）。
- **测试隔离红线（ARCH-BENCH-LEAK-001）**：测试禁止写入生产路径（`data/model_profiles/` 等 `data/` 业务目录），输出目录一律用 `tmp_path` fixture 或 `tmp/` 下路径；含周期线程/后台线程的被测对象，测试结尾必须调 `shutdown()` 并断言线程引用已清空——线程泄漏会将测试行为放大为生产路径 1Hz 写盘循环（2026-07-17 清理 1911 个零字节 `benchmark_*.jsonl`）。
- **`data/models/`（ML 模型文件，ARCH-MODEL-LIFECYCLE-001，2026-08-03 治本）**：嵌入模型文件（bge-m3 2.2GB / bge-small-zh-v1.5 92MB / paraphrase-multilingual-MiniLM-L12-v2 465MB）**永不入库**——`.gitignore` 的 `data/models/` 规则整目录忽略（原 `models/` 规则误伤 27 个代码包已治本为 `/models/` + `data/models/`）。三阶段治本：①Phase 1 `git filter-repo` 从历史移除大模型对象；②Phase 2 `.gitignore` 排除 `data/models/` + `.gitattributes` 移除全部 LFS 死规则；③Phase 3 提供获取途径。**模型获取**：运行 [`scripts/ops/download_models.py`](file:///d:/ZephyrAlpha/scripts/ops/download_models.py)（`--list` 看状态 / `--verify` 验完整性 / `--dry-run` 预览 / `--force` 重下 / `--model <name>` 单模型）。**模型清单真源（SSoT）** = [`config/embedding_model_registry.yaml`](file:///d:/ZephyrAlpha/config/embedding_model_registry.yaml)（name/hf_repo_id/local_path/file_size_mb/required_files），脚本启动时动态加载、零硬编码——新增/移除模型只改 YAML。无 `local_path` 的模型（all-MiniLM-L6-v2、text2vec-base-chinese）由 sentence-transformers 首次使用时自动下载，不经本脚本。`.gitignore`/`.gitattributes` 已纳入 [IRN-010 受保护路径](file:///d:/ZephyrAlpha/scripts/governance/d6_security/check_protected_paths.py)，并发会话修改前会被拦截，须经 ARCH-MODEL-LIFECYCLE-001 流程审批（防批量重写副作用回退排除规则）。

### 6.2 临时文件分类存放铁律（ARCH-TEMP-FILE-PLACEMENT-001，2026-07-20 治本）

AI 创建任何临时文件前 MUST 查 [`trae_070_temporary_file_placement.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_070_temporary_file_placement.yaml) 的 `directory_purpose_classification` 表确定存放目录，禁止凭"方便"选择。5 铁律：

- **LAW-1**：任务文档类（.md/.csv/.yaml）必放 `docs/_working/`（temporary zone，auto_archive gate 保护，ttl=task_bound）
- **LAW-2**：运行时辅助脚本（.ps1/.py/.sh/.txt/.log）必放 `.runtime/tmp/`（neutral zone，无门禁——这是技术原因不是"可以乱放"的许可）
- **LAW-3**：AI session worktree 必放 `.worktrees/{session_id}/`（第二代机制，`scripts/session_worktree.py`，#ARCH-AICOLLAB-001；2026-08-14 裁定 canonical，#ARCH-WORKTREE-ENV-001）。`.aidrafts/{session_id}/` 为第一代机制（rule_bridge/session_worktree.py）——**冻结不新增**，存量逐步退役；两代并存期检测/锚定代码均已双兼容
- **LAW-4**：测试输出按类型分类（报告 .md → `docs/_working/reports/`，数据 .json/.csv → `tests/fixtures/`，临时输出 .log → `.runtime/tmp/`）
- **LAW-5**：禁止凭"方便"选择目录——必须按文件类型匹配 [`directory_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml) zone

**当前强制状态**：trae_070 v1.1.0 配对 GATE-DIRECTORY-CONTRACT（DCR-008 强制校验 file extension ↔ directory purpose_allowed_extensions，error 级阻断 commit）。DCR-008 治本前 `.runtime/` 整目录豁免所有 DCR 校验（AI 把任意文件放 `.runtime/` 不被拦截），治本后 `.runtime/tmp/` 显式声明 `purpose_allowed_extensions`，`.md/.csv/.yaml/.json` 在 `.runtime/tmp/` 即阻断。

### 6.3 静态清单自动生成铁律（GATE-21 自动化执行层）

任何"条目列表 + 计数"性质的清单文件**必须**由生成器自动产出（Type A：从代码/配置派生）或以 schema 为输入（Type B），**禁止手工维护条目**——手工维护必然与真源漂移。本铁律原以 §6.16 引用（断头引用，§6 下并不存在 §6.16），2026-07-17 治本补建为 §6.2 并收敛全部引用；2026-07-20 因新增 §6.2 临时文件分类存放铁律（ARCH-TEMP-FILE-PLACEMENT-001）顺延为 §6.3，全部引用同步收敛。

**覆盖清单（自动生成真源 → 派生缓存，单向）**：
- `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`（门禁登记表）—— 真源三源合并：`.pre-commit-config.yaml`（pre-commit hooks）+ `src/zephyr/gov_enforcement/commit_gates/*.py`（CommitGate GateSpec 声明）+ `MANUAL_GATES`（已合并/退役门禁重定向锚点）。生成器：[`scripts/governance/generators/generate_gate_registry.py`](file:///d:/ZephyrAlpha/scripts/governance/generators/generate_gate_registry.py)。`total_gates` 由 [`scripts/context/generate_architecture_context.py`](file:///d:/ZephyrAlpha/scripts/context/generate_architecture_context.py) 消费为 AI 架构上下文数据源。**post-commit 由 GATE-GATE-REGISTRY-SYNC reconciler 自动重生**（[`make_gate_registry_sync_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) priority=830，ARCH-GATE-REGISTRY-SYNC-001 治本，对标 GATE-MANIFEST reconciler；trigger 覆盖三源：commit_gates/*.py + .pre-commit-config.yaml + generate_gate_registry.py）。
- `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`（in-process gate 注册真源）—— **#ARCH-GATE-REGISTRY-AUTO-001 治本**（2026-07-21）：76 个 in-process gate 的注册真源（gate_id/module_path/factory_function/enabled）。病根：git_commit_gateway.py 76 个 gate 的 import+register 全部硬编码于单文件，违反开闭原则，多 session 并发修改冲突频发。治本：YAML 驱动自动注册——[`gate_auto_registrar.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/gate_auto_registrar.py) 从 YAML 动态 import+register（[`auto_register_gates`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/gate_auto_registrar.py)，fail-open 设计），替代 git_commit_gateway.py 中的 76 个显式 import+register（净减 154 行）。新增 gate 只需 YAML 追加条目，无需修改 git_commit_gateway.py。**post-commit 由 GATE-IN-PROCESS-REGISTRY-DRIFT reconciler 双向校验**（[`make_in_process_gate_registry_drift_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) priority=831，#ARCH-GATE-REGISTRY-AUTO-001 Phase 6；检测 YAML↔内存注册表漂移：yaml-only/in-memory-only gate_id 不匹配，warn-only 持久化到 reconcile_execution_log；trigger 三源：in_process_gate_registry.yaml + gate_auto_registrar.py + commit_gates/*.py）。
- `scripts/governance/script_manifest.yaml`（脚本清单）—— 真源：`scripts/**` 下 `.py` 文件头部 `[BLUEPRINT]`/`__manifest__` 块。生成器：[`scripts/governance/generators/generate_script_manifest.py`](file:///d:/ZephyrAlpha/scripts/governance/generators/generate_script_manifest.py)。post-commit 由 GATE-MANIFEST reconciler 自动重生。
- `docs/01_policies_and_standards/_registry/catalogs/terminology_glossary.yaml`（架构文档术语词汇表）—— 真源：YAML 文件（REG-TERMINOLOGY-001，237 条目 13 类别，英文→中文）。SSoT 分类铁律 TRAE-062：词汇表属规则数据，真源是 YAML。共享加载器：[`scripts/governance/_shared/terminology_loader.py`](file:///d:/ZephyrAlpha/scripts/governance/_shared/terminology_loader.py)（SH-TERM-001，三级降级：YAML→硬编码 fallback→空串），5 个生成器（decision/dataflow/data_acquisition/data_inventory/navigation_index）经 `get_category_map`/`get_flat_map` 读取，禁止硬编码中文字典。改术语改 YAML 即可，无需改生成器代码。

**自动化执行层**：[`scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py)（GATE-21）顺序运行全部生成器 `--check` 模式，自动生成版 vs 磁盘版任何不一致 → 硬阻断（exit 1）。生成器 `import zephyr.*` 需 `src/` 在 `PYTHONPATH`——validator 自举 `sys.path` 含 `src/` 并向子进程注入 `PYTHONPATH=src`，不依赖调用方环境。

**修复漂移**：运行对应生成器（不带 `--check`）重新生成，例如 `python scripts/governance/generators/generate_gate_registry.py`。

### 6.4 临时文件生命周期铁律（ARCH-TEMP-FILE-LIFECYCLE-001，2026-07-20 治本）

§6.2 trae_070 治理**空间维度**（文件类型 → 目录），本节 trae_071 治理**时间维度**（生命周期：创建 → 暂存 → promote/清理）——两者正交互补。背景：2026-07-20 上午"双策略共振选股"中间产物被写入 .runtime/strategy_screen/（免跟踪暂存区），成果文件 FINAL_resonance_rank.csv 在 11:58 生成后、12:06 前被其他会话/清理进程无声删除（无审计痕迹），暴露免跟踪暂存区无生命周期治理的问题。Owner 裁定三级分类替代"一刀切"：

| 层级 | 内容 | 去向 | 治理 |
|---|---|---|---|
| 成果层 | 分析报告、选股清单、工作文档 | docs/_working/ | git 跟踪 + 	tl/doc_type/completes_when 头 + 完成归档 docs/_archive/ |
| 暂存层 | 计算中间产物、缓存、调试脚本 | .runtime/sessions/<session_id>/staging/ | 免跟踪 + 会话结束自动清理 + 禁止直写 .runtime 根目录 |
| 系统层 | 锁/会话注册/审计/pid/heartbeat | .runtime/ 现有系统子目录 | 免跟踪 + 现有 reconciler 维护（不动） |

**5 铁律（详见 [	rae_071_temporary_file_lifecycle.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_071_temporary_file_lifecycle.yaml)）**：

- **LIFE-LAW-1**：禁止任何 AI 会话向 .runtime 根目录直写文件——必须落在 .runtime/sessions/<sid>/staging/（与 #ARCH-HEARTBEAT-001 系统文件目录隔离）
- **LIFE-LAW-2**：成果必须"提升"（promote）到 docs/_working/ 才算交付——留在 .runtime 的成果视为草稿、可被清理；promote 机制：shutil.copy + 写 front-matter（	tl=task_bound / doc_type=analysis_report / completes_when=...）+ 更新 [docs/_working/index.md](file:///d:/ZephyrAlpha/docs/_working/index.md)
- **LIFE-LAW-3**：暂存层会话级隔离——不同 session 的 staging 目录互不干扰（.runtime/sessions/<sid_A>/staging/ 与 .runtime/sessions/<sid_B>/staging/ 物理隔离）
- **LIFE-LAW-4**：暂存层 TTL=24h（事件驱动兜底）——主清理时机是 session_worktree_merge / session_worktree_abort 事件触发；post-commit reconciler make_session_staging_lifecycle_reconciler（priority=802, gate=GATE-SESSION-STAGING-LIFECYCLE，对标 make_stash_lifecycle_reconciler priority=801）兜底清理 >24h 的孤儿 staging 目录（禁止 cron/sleep-loop，事件驱动对齐 trae_060 向内收原则②）
- **LIFE-LAW-5**：系统层不干预——.runtime/heartbeat/ / .runtime/sessions/<sid>/heartbeat.jsonl 等系统文件由 #ARCH-HEARTBEAT-001 现有 reconciler 维护，本规则不触碰

**事故驱动**：2026-07-20 FINAL_resonance_rank.csv 无声删除事件 + 同目录数百个历史会话遗留垃圾（_*.py / pytest_tmp* / 	mp_* / 各种 .log/.txt，全部是各会话直写 .runtime 根目录造成）——本规则从源头禁止直写根目录 + 暂存层会话级隔离 + 事件驱动 TTL 兜底清理三层防御。

**当前落地状态**：
- 规则真源：[	rae_071_temporary_file_lifecycle.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_071_temporary_file_lifecycle.yaml)（v1.2.0，已 sync 到 DB）
- paired_gate_id=null（暂无 pre-commit gate，.runtime/ 免跟踪区无 commit-time 拦截点；治理依赖 AI 自觉 + 事件驱动 reconciler 兜底）
- reconciler 已落地（#ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001，2026-07-22）：`make_session_staging_lifecycle_reconciler`（priority=802）注册到 `git_commit_gateway.py::_register_default_reconcilers()`（实例级，非 boot_hooks.py）；merge 触发点复用 `_run_post_merge_reconcile`，abort 触发点在 `session_worktree_abort` 末尾补齐

### 6.5 根目录临时文件零容忍铁律（#ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001，2026-07-22 治本）

§6.2/§6.4 治理"临时文件放哪个目录 / 活多久"，本节治理"项目根目录零临时文件"——根目录是项目门面，任何临时文件（含 gitignored）都是可见性黑洞与清理责任悬空源。背景：2026-07-22 发现根目录堆积 33 个临时文件（`gw_commit_msg_*.txt`/`gw_pathspec_*.txt`/`tmp_*.txt`/`tmp_junit_*.xml`/`*.log`）+ 5 个 ad-hoc 测试目录，根因不是"策略缺失"而是"执行盲区"——策略层（trae_070/071 + directory_contract DCR-007）已完备，问题在①产生者写错位置（GitCommitGateway 硬编码 `dir=project_root`、AI 用相对路径调 pytest）②门禁对 gitignored 文件盲区（DCR-007 只看 staged，根目录临时文件全 gitignore→永不 staged→永远看不见）③无运行时 FS 扫描 reconciler。

**铁律**：AI 禁止在项目根目录（depth-0）创建任何临时文件。诊断脚本/测试输出/分析中间产物 MUST 放 `.runtime/tmp/`（.py/.sh/.ps1/.txt/.log）或 `.runtime/logs/`（.log/.jsonl）；任务文档 MUST 放 `docs/_working/`。GitCommitGateway 进程 IPC token（`gw_*`）非项目文件，归宿为 OS temp dir（真源唯一/责任唯一：进程临时文件规范真源是 OS temp，由 OS 管理生命周期）。

**三层防御（治本，不依赖 AI 自觉）**：
1. **源头改写产生者**：GitCommitGateway 去 `dir=project_root`（gw_*→OS temp，2 行改动零治理面）；pytest `cache_dir`/`basetemp`/`xmlpath` 默认归位 `.runtime/tmp/`（conftest.py `pytest_configure`，绝对路径 cwd 无关，尊重 CLI 覆盖）；`basetemp` 为 PID-unique（`.runtime/tmp/pytest_{pid}`）——#ARCH-XDIST-WORKER-CRASH-001 治本：静态 basetemp 被 xdist 崩溃 worker 留下锁定文件致下次 rm_rf PermissionError INTERNALERROR，PID-unique 彻底消除冲突；旧目录由 runtime_cleanup reconciler TTL+shutil.rmtree 整目录 + PID存活双判定回收。
2. **root-sweep reconciler 兜底**：`make_root_temp_sweep_reconciler`（priority=803，gate=GATE-ROOT-TEMP-SWEEP）post-commit FS 扫描根目录 depth-0 平铺文件，混合策略——进程 token（`gw_*`/`*.log`/`tmp_commit_msg`）mtime>10min 删除；疑似成果（`tmp_*.py/.txt/.xml/.json/.md/.csv`、`.tmp_*`）移到 `.runtime/tmp/` 隔离（7 天 TTL 由 make_tmp_cleanup_reconciler 清理）。**仅扫平铺文件，不删目录**（目录删除风险高，由源头改写 Phase 1b 阻止产生 + 人工清理）。
3. **DCR-007 第三道防线**：commit 时阻断 staged 根目录临时文件（已存在，目录契约 root_directory_whitelist）。

**裁定要点**：驳回"新建 `.runtime/gw_tmp/`"方案——gw_* 是进程内 IPC token（git `-F`/`--pathspec-from-file` 传递介质，零持久价值），新建目录=在项目内建平行真源违反真源唯一/责任唯一，正确修复=去掉 `dir=` 让 tempfile 用 OS 默认。不新建任何目录（trae_070/071 + directory_contract 已穷尽定义所有临时文件类型合法归宿）。

> **根目录辅助配置文件（合法白名单成员）**：`.traeignore`（Trae IDE 索引排除模式）/ `py.ini`（py launcher 启用 `pythonutf8=1` UTF-8 模式，呼应 §7 GATE-ENCODING 编码铁律）/ `MANIFEST.in`（setuptools sdist 打包清单）为自解释标准配置文件，纳入 [.gitignore](file:///d:/ZephyrAlpha/.gitignore) 根目录白名单（#ARCH-ROOT-TEMP-WHITELIST-001，22 项之一）。根目录合法文件完整清单真源为 .gitignore `!` 列表，AGENTS.md 仅引用真源以保持唯一。

## 7. 代码规范

- Python >=3.12, ruff lint, pydantic v2
- 所有新组件**必须**注册 CapabilityCard 到 CapabilityRegistry
- 所有 AI 行为**必须**写入 AiAuditLogger
- 详细编码约束见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)（四条铁律 + 写代码三条）和 [`trae_010_code_naming_organization.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml)（GOV-ENG-001）
- **.ps1 文件 MUST 纯 ASCII**——PowerShell 5.1 无 BOM 时按 ANSI codepage (GBK) 解码 .ps1，多字节 UTF-8 中文导致字节偏移→假语法错误；Edit 工具每次写入剥离 BOM 使"保留 BOM"方案不可行。**强制方式双层（F-05 防御断层治本，2026-07-17）**：① pre-commit hook **GATE-ENCODING**（[`check_encoding.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_encoding.py) INJ-007，检测 .ps1 非 ASCII 字节，FAIL 级阻断提交，但可被 `--no-verify` 绕过；pre-commit 用 `--staged` 变更检测只查 staged 文件 92s→亚秒，CI 用 `--dir .` 全量）；② **GitCommitGateway ENCODING-SAFETY gate**——[`encoding_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/encoding_gate.py)（gate_id="ENCODING-SAFETY", priority=42，subprocess 调 `check_encoding.py` 复用真源，gateway 内不复制检测逻辑），覆盖 `commit()` 和 `_commit_auto()` 路径——gateway 路径（用 `git commit --no-verify` 绕过 pre-commit 钩子）下编码校验不再失效（fail-open on env error：checker 缺失/超时/exit 2 时不阻断，裁定ARCH-TTL-DOC-001，与 pure_shim_gate/vocab_hardcode_gate 一致；exit 1 违规检出时硬阻断）。规则真源见 [project_rules.md Rule 8](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)
- **文件命名规范真源见 [`trae_028_doc_structure_naming.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)（GOV-DOC-003 §N-16）**——创建新文件前 MUST 先 `Grep` 检查项目内是否已存在同名 basename；**N-16 文件名项目内唯一性检测为硬阻断**（不受 GATE-NAMING `--warn-only` 过渡期影响），覆盖 `tests/` + `docs/` 目录，commit 时 pre-commit 钩子自动检测；同名文件导致 AI 无法确定真源产生漂移（如 `capability_heatmap.md` 曾存在两个不同内容同名文件，19315 vs 11966 字节）；**N-16 豁免清单（conftest.py/__init__.py/index.md 等）真源为 §gov_doc_003_filename_uniqueness.n16_config，`check_naming_convention.py` 从此动态加载（非硬编码），改 YAML 即生效，禁止改代码豁免清单**；**临时沙箱目录（`tests/_tmp_*` / `docs/_tmp_*`，如并发红蓝对抗沙箱 `tests/_tmp_redblue_f2/`）由 `n16_config.skip_dir_prefixes` 豁免（`os.walk` 按目录名前缀 `_tmp_` 剪枝），防沙箱文件与正式文件撞名误触发 N-16 硬阻断卡死并发 commit**
- **规则文件创建入口（ARCH-037，GOV-DOC-003 主题前缀条款）**——新建 `docs/.../rules/trae_XXX.yaml` MUST 经 `python scripts/scaffold.py rule <主题_描述>`（RULE-TWO 强制入口）。scaffold 检查1.5 强制文件名格式 `trae_NNN_<主题>_<描述>.yaml`——单段 name 阻断，新主题前缀仅警告。绕过 scaffold 直接 Write 规则文件 → 双层强制：① [`validate_rule_frontmatter.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/validate_rule_frontmatter.py) DIM-5 pre-commit 检测（可被 `--no-verify` 绕过）② [`create_guard.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/create_guard.py) commit-time 强制（ARCH-037 B 选项，扩展现有 CREATE-GUARD gate 检测范围，`--no-verify` 绕不过）→ 非 trae 命名 + 单段 name 硬阻断（含 rename 检测）。主题前缀集合由 `scaffold.py::_derive_rule_theme_prefixes` 从现有文件名自动派生（无独立词表真源，符合向内收）。
- **module_id/blueprint_id/domain_id/submodule_id 格式校验真源见 [`validate_module_id_naming.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/validate_module_id_naming.py)（裁定#208 双轨制 + R2 治本修订）**——双轨正则（layer-master 轨 MOD-{LAYER}-NNN / 派生轨 MOD-{DOMAIN_FRAGMENT}[-NNN] / 跨域共享轨 SH-{ABBR}-NNN）唯一责任点；`is_valid_module_id(bp_id)`、`is_valid_domain_id(domain_id)` 和 `is_valid_submodule_id(submodule_id)` 三个公共函数供 `check_naming_convention.py`（GATE-NAMING N-06）和 `apply_depgraph.py`（NR-002/cmd_rename_domain/cmd_insert_domain）import 复用；**禁止在代码中定义本地 module_id 正则（防真源分裂）**；capability 反查 alias=`validate_module_id_naming`（`capability_canonical_file_registry.yaml` 注册 13 个 aliases 覆盖中英文关键词）
  - **R2 治本修订（2026-07-05）**：D-XXX-NNN 弃用为 module_id 派生轨，重定义为 submodule_id 专用（蓝图内部子模块编号）。module_id 仅保留双轨：layer-master 轨（MOD-）+ domain-functional 派生轨（MOD-）。`is_valid_module_id("D-GOVERNANCE-001")` 现在 return `(False, "D-XXX-NNN 弃用...")`；蓝图内部子模块编号使用 `is_valid_submodule_id("D-FACTOR-01")` 校验（return `(True, "")`）。规则真源见 [trae_028 §gov_doc_009_submodule_id_convention](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)。
  - **submodule_id 作用域**：仅用于蓝图正文 §sections/§modules/§lifecycle 章节引用；**禁止**写入 blueprint frontmatter 的 `module_id` 字段；**禁止**作为 `depgraph.nodes.blueprint_id` 值。三种 ID 区分：`module_id=MOD-*/SH-*`（蓝图级）、`submodule_id=D-{DOMAIN}-NNN`（蓝图内部，连字符+序号）、`domain_id=D_{DOMAIN}`（域，下划线+无序号）。
- 治理决策方法论见 [`trae_024_methodology_diagnosis.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml)（PS-STD-011）——含MTH-006诊断反转验证：深挖后MUST回溯初始诊断，不一致时追问"为什么初始诊断错了？"
- 审计脚本质量见 [`quality_standard.md`](file:///d:/ZephyrAlpha/scripts/governance/quality_standard.md)（SCRIPT-QUALITY-001）
- 产出物规格化见 [`trae_030_doc_numbering_metadata.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)（GOV-DOC-011）——`.md` 文档 frontmatter 标准字段：`module_id, title, version, layer, depends_on, tags, **ttl（GATE-FRONTMATTER 强制校验）**`。**doc_type 合法值（v3.0.0，10 值）唯一真源见 [`doc_type_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml)**（非 trae_030）；doc_type↔rule_form 映射也在该词表中 per-value 定义。frontmatter 不可删字段完整清单见 [`onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)「绝对不可删的 15 类」
- **所有 `.md` 文档 frontmatter 和 `.py` 文件头部 MUST 含 `ttl` 字段**——2 个合法值：`permanent`（永久）/`task_bound`（任务绑定，完成即删）。判定方法：在永久区路径（`docs/01_policies/`、`docs/02_enterprise_architecture/`、`docs/03_modules/`、`docs/08_knowledge/`）→ `permanent`；否则 → `task_bound`（默认落 [`docs/_working/`](file:///d:/ZephyrAlpha/docs/_working/) 临时区）。详见 [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 的 `decision_tree`。
  - `.md` 用 D_md frontmatter（`ttl: permanent`），`.py` 用 A_full/A_test 注释行（`# [TTL] permanent`）。规则定义见 [`trae_047`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml)（A_full 15 字段 / A_test 7 字段）。
  - `.py` 文件 `# [TTL]` 在最后一个 `# [FIELD]` 行后插入；`__init__.py`/`conftest.py` 等无头部文件豁免。
- **生成器豁免区（generator-exempt-zones）**——`docs/02_enterprise_architecture/` 下 4 个子目录是生成器专用路径，生成器可自由创建/删除文件，**新文件跳过 `PROMOTION_BLOCKED` 门禁**（无需 `--allow-promote`）：`00_overview_entry/`、`01_global_architecture_diagram/`、`02_domain_architecture_docs/`、`03_governance_reports/`。真源：[`directory_contract.yaml directory_zones.permanent.exempt_subdirs`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)（FILE-PLACEMENT-TTL gate 动态加载，ARCH-049）+ [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) `outputs` 字段。**不含** `03_governance_reports/domain_id_hyphen_rename_taskcards/`（手工任务卡）和 `04_architecture_principles_decisions/`（手工架构决策目录）。约束：生成器是这些目录的唯一合法修改源（约定，非技术强制）；N-16 文件名唯一性检查仍生效（不豁免）。
- **TTL 校验统一拦截点（真源唯一 / 向内收）**——pre-commit hook **GATE-FRONTMATTER**（[`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py)）是 ttl 校验**唯一真源**（全格式路由：.md→`parse_frontmatter` / .py+.sh+.ps1+.mmd→`parse_py_header` / .yaml→`parse_byaml_anchor`（支持注释锚定块 + YAML 顶层字段两种子格式）/ .json→`parse_json_meta`；全格式校验 ttl 值合法性，doc_type 对 .md 校验）。**拦截范围**：pre-commit hook 触发时校验（`files: ^docs/.*\.md$` 限制为 docs/ 下 .md 增量触发；全量扫描 `--all-files` 覆盖 docs/+src/+scripts/+tests/ 全格式）。**GitCommitGateway TTL-METADATA gate**——[`ttl_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/ttl_gate.py)（gate_id="TTL-METADATA", priority=32，subprocess 调 `check_frontmatter_metadata.py` 复用真源，启用 `--strict-doctype` 使 doc_type 缺失/非法从 WARN 升级为 hard block（阶段 4 治本，ARCH-TTL-DOC-001）），覆盖 `commit()` 和 `_commit_auto()` 路径，gateway 路径（用 `--no-verify` 绕过 pre-commit）下 ttl 校验不再失效（fail-closed：checker 缺失/执行失败时阻断）。**GitCommitGateway FILE-PLACEMENT-TTL gate（ARCH-049，2026-07-05）**——[`file_placement_ttl_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/file_placement_ttl_gate.py)（gate_id="FILE-PLACEMENT-TTL", priority=33，in-process gate 动态加载 directory_contract.yaml + ttl_vocabulary.yaml），三重校验：①永久区新文件准入（PROMOTION_BLOCKED，需 `allow_promote=True`，exempt_subdirs 生成器输出豁免）②TTL↔zone 一致性（frontmatter.ttl=permanent 但在临时区→阻断；task_bound 但在永久区→阻断）③根目录子目录准入（第一级目录不在 directory_zones→阻断，防乱建子目录）。覆盖 `commit()` 和 `_commit_auto()` 路径（`_commit_auto` 传 `allow_promote=True`，reconciler 受信任）。**reconciler 路径**：`_commit_auto()` 跑 DCR gate + TTL-METADATA gate + FILE-PLACEMENT-TTL gate（三者均通过 `gate_registry.get` 复用，不复制检测逻辑）。
- **B_yaml 治理锚定一致性 CI 门禁（audit-02 引入，2026-08-02）**——与上述 TTL 校验（ttl **值**合法性）互补，本门禁校验 B_yaml 锚定块**结构一致性**。CI [`governance.yml`](file:///d:/ZephyrAlpha/.github/workflows/governance.yml) Tier 3 步骤 "YAML Anchor Consistency"（`continue-on-error: false` 硬阻断）调用 [`check_yaml_anchor_consistency.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_yaml_anchor_consistency.py) 全量扫描 `config/` + `architecture_model/` 下所有 YAML，检测 4 类问题：**P1** 残留 `[A_config]` 旧格式行（B_yaml 锚定块已取代，见 [trae_047](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml)）/ **P2** 锚定块 module_id ↔ body module_id 不一致 / **P3** 有 body module_id 缺 B_yaml 锚定块 / **P4** 锚定块缺 blueprint 字段；豁免 grafana/prometheus/docker-compose 第三方配置。退出码 `0`=无问题 / `1`=发现问题 / `2`=参数错误。**与 commit-time 门禁的分工**：commit-time `check_frontmatter_metadata.py`（GATE-FRONTMATTER + TTL-METADATA gate）增量校验 staged 文件 ttl 值；本 CI 门禁是 Layer 5 全量回归，兜底拦截裸 commit 绕过 gateway 的锚定块漂移（`[A_config]` 回退 / 锚定块↔body 漂移 / 字段缺失）。**防重复造轮子**：capability 反查已登记 `yaml_anchor_consistency_scanner`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)），新 AI 搜 "yaml anchor/锚定块/B_yaml 一致性" 可定位真源。
- **N-16 检查统一拦截点（真源唯一 / 向内收 v2）**——N-16 文件名唯一性检查逻辑唯一真源在 [`check_naming_convention.py::check_new_files_naming`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py)（增量检查：`git ls-files` 基线，只检测新文件引入的冲突，不阻断历史遗留）。GitCommitGateway 通过 subprocess 调用 `--check-new-full` 模式（subprocess 复用真源模式，同 DIRECTORY-CONTRACT gate 调 `check_directory_contract.py`），**不实现检查逻辑**。豁免清单真源在 trae_028.yaml §n16_config，由 check_naming_convention.py 模块级常量动态加载。fail-open：subprocess 失败/脚本不存在（exit≠0且≠1）时不阻断 commit。
- **config/ 平铺规则（ARCH-038，2026-07-01）**——`config/` 根目录**平铺所有配置 YAML/JSON**，禁止建模块归属子目录（如 `config/capacity/`、`config/compression/`）。**仅允许两个语义子目录**：`config/runtime/`（运行时状态文件）和 `config/infra/`（基础设施配置）。命名规则：小写+下划线，名字即责任（如 `capacity_slo.yaml` = 容量SLO，`compression_policy.yaml` = 压缩策略）。**根因**：按模块名建子目录导致同一功能域配置散在子目录和根两处，AI 找配置要猜位置；平铺后一眼看完所有配置，`config/<name>.yaml` 路径可预测。约束真源见 [directory_contract.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)。
- **REPO_ROOT 真源归一（SSoT）**——仓库根常量唯一真源：[`zephyr.shared.io.paths.REPO_ROOT`](file:///d:/ZephyrAlpha/src/zephyr/shared/io/paths.py)（由 `find_repo_root()` 基于 .git marker 向上搜索，文件移动不 break）。`src/zephyr/**` 包内消费者：`from zephyr.shared.io.paths import REPO_ROOT`；`scripts/**`/`tests/**` 包外消费者：仅允许一次性极简 sys.path bootstrap（N 值固定），随后必须 `from zephyr.shared.io.paths import REPO_ROOT`。**禁止** `Path(__file__).resolve().parents[N]`、`.parent.parent...`、`Path("D:/ZephyrAlpha")` 等任何变体推算仓库根。**唯一豁免**：sys.path bootstrap 上下文（鸡生蛋：需先设 sys.path 才能 import REPO_ROOT）。**强制方式**：REPO_ROOT 违规检测仅靠 pre-commit hook GATE-DD07（warn-only，被 gateway `--no-verify` 绕过）+ CI 兜底。**DB 路径硬编码禁令（P2 PG 迁移治本，2026-06-29）**——`sqlite3.connect("绝对路径.db")` 硬编码数据库连接违规，无 gateway 内置阻断。depgraph 连接入口 `get_depgraph_pg_connection()`，governance 连接入口 `get_governance_connection()`。**DB 写入脚本禁用 lock_files.py（P3 防复发门禁，2026-06-29）**——DB 写入用 PG MVCC 事务保护（文件锁对 PG 写无保护作用），无 gateway 内置阻断（靠 code review + CI 兜底）。规则真源见 [trae_054](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml) §mandatory + [trae_001](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) §db_write_protocol。
- **ZephyrBaseError 真源归一（SSoT）**——[`zephyr.shared.foundation.errors`](file:///d:/ZephyrAlpha/src/zephyr/shared/foundation/errors.py) 是 `ZephyrBaseError` 体系（13 个 Error 类）唯一真源。新增 Error 子类 MUST 改 `shared.foundation.errors`（唯一真源）；`shared` 层禁止 import `integration.*`（向下依赖原则）。
- **GATE-PURE-ASSERTION 纯陈述原则门禁（GOV-DOC-016）**——规则文档（`.trae/rules/*.md` + `AGENTS.md`）只含当前有效规则的肯定陈述句，禁止过渡文本（否定陈述句、历史对比描述、迁移标记等）。规则真源及违规词表见 [trae_030 §gov_doc_016_pure_assertion](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)（YAML key `gov_doc_016_pure_assertion`）。强制方式：GATE-PURE-ASSERTION（GitCommitGateway pre-commit 阻断门禁，priority=69，in-process 注册 `--no-verify` 绕不过；subprocess 调用 [check_pure_assertion.py --ci](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_pure_assertion.py) 检测 staged .md added 行，检出违规硬阻断 commit；checker 缺失/超时 fail-open）；[rules_integrity_reconciler](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（post-commit 全量扫描 .md）作为兜底。历史版本差异通过 git log 追踪，不写入正文。检测范围：staged .md 文件 added 行（增量检测，现存违规 grandfather）；全量扫描由 `check_pure_assertion.py --full-scan` 覆盖 docs/ 下所有 .md。
- **`docs/_working/` 新增 .md 文件 MUST 在 frontmatter 声明 `completes_when` 字段**（可验证的完成条件），GitCommitGateway commit 时自动拦截缺失该字段的新文档；规则真源见 [trae_028 §归档与废弃流程](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)。
  - 自动归档由 [GATE-DELETE-AUDIT reconciler（含原 WORKING-DOCS 功能）](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) post-commit 事件驱动（capability_id：`working_docs_ghost_ref_archiver`，反查用法见 §9）。
- **读取 `docs/_working/` 下任何 .md 前 MUST 验证文档引用的脚本/YAML/blueprint_id 是否仍存在**（防幽灵引用漂移），细则见 [GATE-DELETE-AUDIT reconciler（含原 WORKING-DOCS 功能）](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（`scan_and_archive_working_docs` 幽灵引用检测）。
- **归档区 `docs/_archive/`（永久保留历史文件）**——归档触发条件采用二分法判定树（禁止凭"感觉不再需要"归档），所有永久区(01/02/03/08)的文件归档统一归此：

  **判定树（按顺序回答，命中即归档；两个问题均答 NO 则保留原位）**：

  - **Q1 替换归档**：是否存在新文件 Y 承担与目标文件 X 相同的职责，且 Y 是 X 的真源继任者（典型场景：md 规则→yaml 规则重写、旧脚本→新脚本重写、模块拆分合并）？
    - **YES → 执行替换归档**：① `git mv X docs/_archive/`；② 扫描全库引用点（.md/.yaml/.json/.csv），所有指向 X 的引用 MUST 更新为指向 Y（新真源）；③ frontmatter `ttl: permanent` + `status: deprecated`。
    - **NO → 进入 Q2**。

  - **Q2 删除归档**：目标文件 X 是否属于下线资产（功能下线 / 模块移除 / 脚本停用，且全库无活跃引用点）？
    - **YES → 执行删除归档**：① `git mv X docs/_archive/`；② 扫描全库引用点（.md/.yaml/.json/.csv），所有指向 X 的引用 MUST 从源头删除（无继任真源，不指向新文件）；③ frontmatter `ttl: permanent` + `status: deprecated`。
    - **NO → 保留原位**（X 仍有活跃职责，不归档）。

  **核心原则**：真源唯一——文件有继任者时，目标文件保留在原地 = 双真源并存 = AI 漂移，MUST 移走。归档区在 [`directory_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml) `directory_zones.permanent.paths` 中（default_ttl=permanent），`validate_document_ttl.py --list-all-non-permanent` 不列为清理候选。**`docs/_archive/` 是唯一合法归档区**——禁止在 `docs/` 下创建其他归档目录。归档后引用断裂由 [GATE-FRONTMATTER/DOC-REF](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 门禁在 commit 时检测断链并阻断。
- **共享能力真源位置**——跨层共享能力（errors / paths / yaml_utils / infra 等）真源在 [`src/zephyr/shared/`](file:///d:/ZephyrAlpha/src/zephyr/shared/)。新增共享能力 MUST 直接在 `src/zephyr/shared/` 创建或扩展，**禁止在 `src/zephyr/integration/` 下创建 `shared_*` proxy 层**（CapabilityLookup 反查 `shared.foundation.errors` / `shared.io.paths` 等能力可定位真源，`check_capability_duplicates` 在 commit 时自动检测 basename 撞 capability_id/alias）。`src/zephyr/shared/` 禁止 import `integration.*`（向下依赖原则，详见 §7 ZephyrBaseError 真源归一）。
- **禁止纯 re-export shim 文件（GATE-SSOT-CODE/check_pure_shim，治本漏洞1，2026-06-29）**——禁止新建纯 re-export shim 文件（`from zephyr.shared.* import *` 无实质代码的 .py 文件）。纯 shim 是真源分裂温床——AI 看到两个 import 路径指向同一符号，无法确定真源产生漂移。pre-commit 用 `--staged` 变更检测只扫 staged .py（3.5s→亚秒），CI 用 `--ci` 全量。**判定标准**：AST 白名单分析，技术细节（哪些节点算实质代码、哪些不算）以 [`check_pure_shim.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_pure_shim.py) 的 `is_pure_reexport_shim()` 函数为**唯一真源**，本规则文档只描述"做什么"（禁止纯 shim），不重复描述"怎么做"（白名单判定逻辑），避免规则文档与代码分裂。**合法例外**：①`__init__.py` 包聚合 ②临时过渡 shim（文件头部含 `# [TTL] task_bound` + `# [DEPRECATED]` 标记，有 TTL 自动清理机制）。**强制方式**：双层防护——① [`check_pure_shim.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_pure_shim.py) GATE-SSOT-CODE pre-commit 钩子；② [`pure_shim_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/pure_shim_gate.py) in-process gate（PURE-SHIM，priority=68，P6 2026-07-09 治本——弥补 `--no-verify` 绕过 pre-commit hook 的缺口，subprocess 调 `check_pure_shim.py --ci` 保持 SSoT）。
- **禁止附带性 re-export（SSoT 治本 D1，2026-06-30）**——模块 import 符号仅供自身使用，禁止成为该符号的下游再导出点。例如 `from zephyr.shared.io.paths import REPO_ROOT` 后，其他模块 MUST 从 `zephyr.shared.io.paths`（真源）或 `_shared.constants`（sanctioned re-exporter）import，而非从本模块再 import。**唯一 sanctioned re-exporter**：[`_shared/constants.py`](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py)（scripts/ 域 SSoT 桥接层，re-export REPO_ROOT/DB_PATH 等常量给 scripts/ 域使用）。病根：模块为自身使用 import 常量后，下游从该模块 import 同一符号 → 多 import 路径 → AI 无法确定真源 → 漂移。与 GATE-SSOT-CODE/check_pure_shim 区别：纯 shim 是"文件只做 re-export 无实质代码"；附带性 re-export 是"文件有实质代码但意外成为 import 路径"。两者均违反真源唯一原则。
- **词表合法值加载规范** → 见 [trae_060 §2 唯一真源与直接消费](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml)（YAML section `§2 唯一真源与直接消费`）（向内收原则①+②；禁止硬编码/同步复制词表合法值，必须 yaml.safe_load 动态加载；GATE-VOCAB 门禁强制执行）。本节不复制规则文本，仅提供实现层用法示例。
  - **真源实现**（治本1 后）：`src/zephyr/shared/io/yaml_utils.py` 提供 `load_vocabulary_values()`、`load_vocabulary_entries()` 和 `load_vocabulary_deprecated_map()` 三个函数。`load_vocabulary_values` 返回 `set[str]`（只需值集合时用）；`load_vocabulary_entries` 返回 `list[dict]`（需要 value+definition 时用，如 schema.json 双向同步填充 description）；`load_vocabulary_deprecated_map` 返回废弃值映射。`strict=True` 默认 fail-fast，文件不存在抛 `FileNotFoundError`（消除静默失败 DoS 漂移）。
  - **scripts/ 侧用法**（重新导出，保持兼容）：
    ```python
    import sys
    from pathlib import Path
    _GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
    if _GOV_DIR not in sys.path:
        sys.path.insert(0, _GOV_DIR)
    from _shared.yaml_utils import load_vocabulary_values, load_vocabulary_deprecated_map
    VALID_STATUSES = load_vocabulary_values("status_vocabulary.yaml")
    DEPRECATED_MAP = load_vocabulary_deprecated_map("doc_type_vocabulary.yaml")
    ```
  - **src/zephyr/ 侧用法**（直接 import）：
    ```python
    from zephyr.shared.io.yaml_utils import load_vocabulary_values, load_vocabulary_deprecated_map
    VALID_DOC_TYPES = load_vocabulary_values("doc_type_vocabulary.yaml")
    ```
  - **配套门禁**：**GATE-VOCAB** 已接入 [`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) 的 pre-commit 钩子（`id: gate-vocab`，`--ci` 硬阻断模式，2026-06-26 违规清零后转），`src/zephyr/**/*.py` 或 `scripts/**/*.py` 变更时自动触发。AST 扫描检测 `VALID/ALLOWED/LEGAL/PERMITTED_*_VALUES/STATUSES/TYPES/LEVELS/LAYERS/TTL/CATEGORIES/CLASSIFICATIONS/LIST/SET` 模式的字面量硬编码（含 `dict()/list()/tuple()/"a,b".split()` 隐式字面量 + walrus 操作符）+ `load_vocabulary_values("xxx.yaml")` 引用文件存在性校验。例外：DDL 文件（`sqlite_schema.py` 等）走 DDL-as-Code 协议；`_archive/` 排除；**`# noqa: gate-vocab`** 内联豁免（带理由的诚实豁免，非偷偷绕过）。门禁真源见 [trae_060 §5 禁止清单](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml)（YAML section `§5 禁止清单`）。**注意**：§5 中 "23处(9词表)" 的 evidence 举例已过时（2026-06-26 审计确认所有举例文件已不存在或已修复，GATE-VOCAB 实时扫描 0 违规），审计报告见 [`docs/_working/trae_060_s5_evidence_audit.md`](file:///d:/ZephyrAlpha/docs/_working/trae_060_s5_evidence_audit.md)。新 AI 应以 GATE-VOCAB 实时扫描结果为准，而非 §5 的快照式列举。
  - **capability 反查注册表**已登记 2 条能力（`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`）：`vocabulary_values_loader`（canonical = `src/zephyr/shared/io/yaml_utils.py`）+ `vocab_hardcode_detector`（canonical = `scripts/governance/d3_metadata/check_vocab_hardcode.py`）。新 AI 创建词表加载器或硬编码检测器前，CapabilityLookup 会反查阻止重复造轮子。
- **配置 SSoT 真源归一**（2026-07-17 AI-02 审计 P2 治本，ARCH-SSOT-CONFIG）→ 历史教训：`immutable_core.py` 历史硬编码 24 个 ALWAYS_BLOCKED_OPERATIONS + 26 个 PROTECTED_PATHS 字面量（代码内 set/dict）；`ai_capability_guard.py` 历史硬编码 7 个 substring 路径模式。修改需改代码，AI 易遗漏 → 收敛为 YAML SSoT 真源动态加载：
  - **[config/immutable_core.yaml](file:///d:/ZephyrAlpha/config/immutable_core.yaml)**（safety_level=H，ai_autonomy=human_gated，ttl=permanent）：`ALWAYS_BLOCKED_OPERATIONS`（24 ops）+ `PROTECTED_PATHS`（26 paths）唯一真源。[`immutable_core.py`](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/immutable_core.py) 通过 `_load_immutable_core_config()` 动态加载，fail-safe 模式（YAML 缺失返回空 dict，由 `verify_protected_paths_exist` 检测报告 violation）。capability 已登记 `immutable_core_config`（creation_token=`auto-immutable-core-yaml-20260717`）。
  - **[config/ai_capability_matrix.yaml](file:///d:/ZephyrAlpha/config/ai_capability_matrix.yaml)**（safety_level=M，ai_autonomy=ai_modifiable，ttl=permanent）：`matrix.entries`（scope_pattern → CapabilityLevel）唯一真源。[`ai_capability_guard.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_enforcement/ai_capability_guard.py) 通过 `_load_capability_matrix_entries()` 动态加载，`_scope_to_substring()` 将 glob 转 substring 保持语义等价，`_legacy_check_file_level()` 作 YAML 加载失败时的 fail-safe 回退。
  - **新 AI 修改保护路径/禁止操作清单**：改 `config/immutable_core.yaml`（YAML 真源），禁止改 `immutable_core.py` 代码字面量；**新 AI 修改 AI 能力边界**：改 `config/ai_capability_matrix.yaml`（YAML 真源），禁止改 `ai_capability_guard.py` 代码 substring 模式。GATE-VOCAB 会检测代码侧硬编码字面量集合违规。
- **pre-commit hook id 唯一性门禁**（GATE-ID-UNIQ）→ 历史教训：commit a09e510ec6 中两个 SSoT 门禁同用 `id: gate-ssot`，后者覆盖前者导致 `src/zephyr/*.py` 检测静默失效。已加自动化门禁防止未来 AI 再造重复 id：
  - **pre-commit 阻断层**：[`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) `id: gate-id-uniq`，改 `.pre-commit-config.yaml` 时自动触发 [`check_precommit_id_uniqueness.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py) 扫描所有 `repos[].hooks[].id`，same-repo 重复 → hard block (exit 1)，cross-repo 重复 → warn。
  - **post-commit 兜底层**（治本改进点2）：[`reconciliation_registry.py` `make_precommit_id_uniqueness_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) priority=250，`--no-verify` 绕过 pre-commit 后，commit `.pre-commit-config.yaml` 时自动重校，违规报告落盘 `.runtime/reconcile_reports/id_uniqueness_<ts>.json`（非阻断，供追责）。
  - **capability 反查**已登记 `precommit_id_uniqueness_check`（canonical = `scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py`）。新 AI 想做"检测 yaml id 唯一性"前，CapabilityLookup 会反查到本脚本，提示"扩展本脚本（加 `--target` 参数），勿新建 checker"。
  - **脚本自篡改纵深防御**（A+C 双层，治脚本自篡改缺口）：检测脚本（如 `check_precommit_id_uniqueness.py`）的检测逻辑被 AI 直接删改时，pre-commit hook 和 reconciler 共用同一脚本，两层防线同时失效。本防御补此缺口：
    - **A 层（不复活）**：违反向内收原则，只防误删不防故意绕过，测试是更好的误删防线。[`capability_canonical_file_registry.yaml` `integrity_anchors`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 字段当前无代码消费者（死数据，仅保留 4 个仍存在的方法 anchor 供未来参考）。脚本篡改检测仅靠 C 层（pre-commit hook，被 gateway `--no-verify` 绕过）+ CI 层（GitHub Actions，事后兜底）。
    - **C 层（兜底）**：[`.pre-commit-config.yaml` `gate-rules-integrity`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) pre-commit 钩子，改 `AGENTS.md` 或 `scripts/governance/` 下文件时触发 [`validate_rules_integrity.py --check`](file:///d:/ZephyrAlpha/scripts/governance/meta/validate_rules_integrity.py) golden hash 校验（exit 2 硬阻断）。覆盖不走 gateway 的裸 commit 路径 + 检测"保留锚点名但篡改内部逻辑"的精细攻击。受保护文件清单：`RULES_MANIFEST`（validate_rules_integrity.py 内声明）。**基线自动同步**（红蓝发现1 治本）：`rules_integrity_db.json` 不被 git 跟踪，合法 commit 修改 RULES_MANIFEST 文件后基线不自动更新 → `--check` 误报 TAMPERED 阻断裸 commit。已加 [`make_integrity_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（AD-GOV-001 合并后含原 rules_integrity 功能，priority=800）post-commit 自动 `--register` 重注册基线（trigger 总是触发——第一性原理：--register 仅 hash RULES_MANIFEST 文件，毫秒级，不值得为省此开销引入路径假设；RULES_MANIFEST 真源在 validate_rules_integrity.py 内）。重注册的基线基于 git HEAD（见下条 register 基于 git HEAD），消除 WIP 篡改合法化风险。
    - **register 基于 git HEAD**（红蓝发现3 治本）：原 `register()` 基于工作树状态（`_hash_file`）注册基线——攻击者篡改受保护脚本后 commit 无关文件，post-commit `--register` 会把 WIP 篡改注册为新基线（合法化篡改）。已改为基于 `git show HEAD:<path>` hash（[`_hash_git_head`](file:///d:/ZephyrAlpha/scripts/governance/meta/validate_rules_integrity.py)），只注册已 commit 的 HEAD 状态；工作树 WIP 篡改不进基线。`check()` 仍用 `_hash_file` 基于工作树状态（检测 WIP 篡改）。新文件不在 git HEAD 时回退 `_hash_file`。
    - **--register 门禁**（红蓝发现4 治本）：`--register` 重置基线 = 合法化当前状态，是危险操作。原无门禁，可手动任意重置（合法化篡改）。已加环境变量门禁：`ZEPHYR_RECONCILER_MODE=1`（对标 `ZEPHYR_COMMIT_GATEWAY=1` 模式）。只有 [`make_integrity_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（AD-GOV-001 合并后含原 rules_integrity 功能）内部 `_reconcile_rules_integrity` 闭包调用时设置此令牌才允许 `--register`（元问题4治本后内联，无 `_make_old_*` 私有函数）；手动 `python validate_rules_integrity.py --register` 不设置 → `sys.exit(1)` 阻断。
    - **残留缺口（诚实记录）**：自指悖论——gateway 本身能被改，但改 gateway 触发 `gate-triple-align`/`gate-reg-bl` 等门禁且 `[SAFETY] M` 受保护；validate_rules_integrity.py 自身可被改，但它不在自身 RULES_MANIFEST 内（避免自指死锁）。这是可接受的架构权衡，非彻底治本。
    - **capability 反查**：`integrity_anchors` 字段在 `precommit_id_uniqueness_check` 能力条目下声明（注：A 层不复活，integrity_anchors 为死数据，保留供未来复活参考）。新增受保护脚本时：①`validate_rules_integrity.py` `RULES_MANIFEST` 加条目 ②YAML `integrity_anchors` + `canonical_override` 同步声明（供未来 A 层复活时直接复用）。

- **目录契约门禁**（GATE-DIRECTORY-CONTRACT）→ 文件放错目录 = AI 找不到 + 真源散落 + 规则无法自动执行。已加自动化门禁强制文件目录归属合规：
  - **pre-commit 阻断层**：[`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) `id: gate-directory-contract`，每次 `git commit` 自动触发，`--staged` 模式只校验暂存文件，`--ci` 硬阻断（exit 1 拒绝提交）。
  - **真源**：[`directory_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)（目录维度约束唯一真源：directory_zones + directory_extensions + root_directory_whitelist）+ [`doc_type_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml)（doc_type 的 allowed/forbidden_directories 真源）。消费者动态加载，路径变更只需改契约一处。
  - **检测内容**（DCR-001~007 全部已启用）：DCR-001 doc_type 的 allowed_directories 包含文件所在目录（error）；DCR-002 forbidden_directories 不包含文件所在目录（error）；DCR-003 永久区 .md 文件 ttl==permanent（error）；DCR-004 临时区 ttl==task_bound（warning）；DCR-005 扩展名在目录的 allowed 清单内（error）；DCR-006 扩展名不在 forbidden 清单内（error）；DCR-007 根目录文件在白名单内（error）。
  - **豁免区**（DCR-001/002 跳过）：`docs/_working/`（临时区）、`docs/_archive/`（归档区）、`.runtime/`（运行时归档区）、`.trae/`（IDE 工具区）、`docs/01_policies_and_standards/templates/`（模板区 TMP-EX-001——模板是 Class Definition，cookbook template 的 doc_type 取目标类型，不受目标类型的 allowed_directories 约束）。
  - **capability 反查**：已登记 `directory_contract_checker`（canonical = `scripts/governance/d1_structure/check_directory_contract.py`，aliases 含 `DCR_checker`/`directory_contract_validation`）。新 AI 想做"文件目录校验/目录归属检查"前，CapabilityLookup 会反查到本脚本，提示"扩展本脚本（加 DCR 规则），勿新建 checker"。
  - **新 AI 必读**：创建新文件前，先查 doc_type_vocabulary.yaml 的 allowed_directories 确认目标目录合法。违反将被 DCR-001 在 commit 时阻断——不是"建议"，是硬约束。
- **并发 session 文件冲突防护门禁**（SESSION-REQUIRED + HELD-OVERLAP + CLAIM-REQUIRED + WORKTREE-REQUIRED，2026-06-30 治本 + 2026-07-06 AI-11 三层化 + 2026-08-04 #ARCH-WORKTREE-GATE-001 四层化）→ 多 session 并发开发时，session A 修改的文件可能被 session B 的 commit 覆盖（回退）。四层门禁防护：
  - **SESSION-REQUIRED**（阻断）：[`session_required_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/session_required_gate.py) priority=30。AI 对话启动后第一件事 MUST 调用 `session_worktree_start(sid)` 注册合法 session_id；commit 时若 session_id 未在 SessionRegistry 中登记 → `SESSION_REQUIRED_VIOLATION` 阻断。病根：不 start session 可绕过 CLAIM-REQUIRED/HELD-OVERLAP（无 session_id 则无 claim/held 比对基准）。AI-11 审计 P0-9 修复：补齐 gate 到 GitCommitGateway._gate_registry 注册链路。
  - **CLAIM-REQUIRED**（阻断）：[`claim_required_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/claim_required_gate.py) priority=40。已注册 session commit 前必须先 `claim_files` 声明目标文件，未 claim → `CLAIM_REQUIRED_VIOLATION` 阻断。逃生通道：`--allow-overlap` 参数放行（特殊情况）。病根：不 claim 可绕过 HELD-OVERLAP（未声明 held_files 则无比对基准）。
  - **WORKTREE-REQUIRED**（阻断，#ARCH-WORKTREE-GATE-001 治本 2026-08-04 + #ARCH-RECONCILER-WORKTREE-RACE 治本 2026-08-09）：[`worktree_required_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/worktree_required_gate.py) priority=44。非 worktree + 有其他活跃 **user** session → `WORKTREE_VIOLATION` 阻断。reconciler worker session（`worker-{sha8}-{pid}` 前缀）排除出活跃 session 计数（#ARCH-RECONCILER-WORKTREE-RACE 治本）——worker 是 commit 下游产物，held_files 空，无搭便车风险。病根：`warn_non_worktree_commit` 只 WARN 不阻断，AI 把 WARN 当"通过"，在 100% AI 开发场景下君子协定系统性失效。分级阻断：worktree 内放行 / solo session 放行 / 并发非 worktree user session 阻断（worker 排除）。双逃生通道：`--allow-overlap`（通用）或 `--allow-non-worktree`（专用）。fail-open：`get_current_worktree`/`list_active` 异常时安全降级放行（基础设施故障不应卡死 commit）。
  - **HELD-OVERLAP**（阻断）：[`held_overlap_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/held_overlap_gate.py) priority=50。commit 中包含其他 session held（claim）的文件 → 阻断。防搭便车覆盖。
  - **capability 反查**：四者均已登记 `capability_canonical_file_registry.yaml`（`session_required_gate` + `claim_required_gate` + `worktree_required_gate` + `held_overlap_gate`）。新 AI 想做"文件冲突防护/file claim/session 注册强制/worktree 隔离强制"前，CapabilityLookup 会反查阻止重复造轮子。

- **新建 .py/.yaml CapabilityLookup 提示门禁**（CAPABILITY-OVERLAP，warn-only，2026-06-30 治本）→ commit 时 [`capability_overlap_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/capability_overlap_gate.py) priority=200 自动检测：①新建 .py 文件名是否与 `capability_canonical_file_registry.yaml` 已注册能力 aliases token 重叠 ②`_registry/` 下新增 .yaml/.yml 文件名是否与同目录现有 yaml token 重叠（≥2 token = 高置信度第二真源）。命中则 `logger.warning` 告警（**不阻断**）——文件名匹配是启发式，AI 看到 warning 后自行判断是扩展还是新建。检测范围覆盖 `_registry/` 所有子目录（contracts/vocabularies/catalogs/schemas/ + 未来新增），不硬编码子目录列表。病根：AGENTS.md §7 把"查 CapabilityLookup"列为 step 0，但仅靠文档约定——新 AI 跳过 AGENTS.md 即可重复造轮子，本 gate 补上代码层兜底。**capability 反查**已登记 `capability_overlap_gate`。新 AI 想做"重复造轮子检测/second source yaml"前，CapabilityLookup 会反查阻止重复造轮子。

- **post-commit 规则文件审计+ARCH引用查重 reconciler**（GATE-RULE-AUDIT + GATE-EXEMPT-ZONE-FM，warn-only，2026-06-30 治本 + 元问题2治本）→ 修改 5 个规则文件（directory_contract.yaml / doc_type_vocabulary.yaml / node_type_vocabulary.yaml / capability_canonical_file_registry.yaml / layer_vocabulary.yaml）会触发 `GATE-RULE-AUDIT`（[`reconciliation_registry.py` `make_rule_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) priority=710，3-way compose），落盘审计报告到 `.runtime/reconcile_reports/rule_file_audit_*.json`。**GATE-ARCH-REFS（priority=710，元问题2治本 2026-06-30）**扫描 committed_files 中所有 `#ARCH-XXX` 引用，检查是否在 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 的 `entries` 中有对应条目——病根：注册表铁律#6"任何 #ARCH-XXX 引用必须在本注册表有对应条目，禁止 grep-and-claim 占位"是君子协定，无技术强制（#ARCH-027 冲突就是 AI 占位而不查重导致）。检测到未登记的 `#ARCH-XXX` 引用→warn（非阻断，detail 列出未登记编号）。单独提交豁免区（`docs/_working/`等）下带 frontmatter 的文件会触发 `GATE-EXEMPT-ZONE-FM`（`make_exempt_zone_frontmatter_reconciler` priority=710），检测本应放正式目录却被塞进豁免区的文件。三者均 warn-only（不阻断），报告供人工审查。

- **文档引用完整性门禁**（GATE-FRONTMATTER/DOC-REF 子项）→ 调研发现 AI 在 .md/.csv/.yaml 中编造虚假文件引用（如 dom_gov_001 虚假审计闭环：index.md 列 22 张不存在的任务卡，move_plan.csv 引用 4 个不存在的文件）。已加自动化门禁防止未来 AI 再造虚假引用：
  - **pre-commit 阻断层**：[`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) `id: gate-frontmatter`（DOC-REF 子项，run_gate_chain 第4步），staged 的 .md/.csv/.yaml/.json 文件触发 [`audit_broken_links.py`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 扫描 markdown 链接 + 纯文本路径 + CSV 列值 + YAML 值 + frontmatter blueprint_id + index.md 清单 + audit_report 审计对象，`--ci` 硬阻断 + `--check-new` 历史豁免（仅阻断本次修改新引入的断链，对比 HEAD 版本，参考 N-16 模式）。
  - **检测范围**：.md（markdown 链接 + 纯文本路径 + frontmatter blueprint_id + index.md 清单 + audit_report 审计对象）/ .csv（列值路径）/ .yaml/.yml（值路径 + 纯文本）/ .json（纯文本路径）。跳过 http/https/ftp/mailto 锚点 URL。
  - **路径解析**：三重尝试——①先相对于文件目录（markdown 链接习惯）②再相对于项目根（CSV/YAML 项目根相对路径）③basename 全局搜索兜底（裸文件名如 blueprint.md 在项目其他目录存在）。注意：index.md 清单检测**禁用 basename 兜底**（本目录契约语义，兜底会掩盖幻觉）。
  - **capability 反查**已登记 `broken_link_detector`（canonical = `scripts/governance/d2_links/audit_broken_links.py`）。新 AI 想做"断链检测/ghost ref/phantom reference"前，CapabilityLookup 会反查到本脚本，提示"扩展本脚本（加提取器函数），勿新建 checker"。
  - **治本 GAP-1**：解决"非 .md 文件（.csv/.yaml/.json）中的路径引用无检测"防护缺口。真源：[`audit_broken_links.py` `_extract_csv_paths`/`_extract_text_paths`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-2**：解决"frontmatter.blueprint_id 引用的蓝图是否存在无检测"防护缺口。检测 .md frontmatter 的 blueprint_id 字段值是否在 `blueprint_registry.yaml` 中存在。**注**：该文件曾于 commit `303fb9c9b2` 被 KB 清理误删（导致 `_load_blueprint_registry_module_ids()` 返回空集、检测静默失效），已于 2026-08-01 恢复并同步至 57 条目，检测恢复生效（详见 #ARCH-BP-REGISTRY-DELETION-001）；漂移由 GATE-21 守护。空值跳过（合法，如 index.md 无归属蓝图）；格式非法跳过（交给 GATE-NAMING N-06 双轨制格式校验）。真源：[`audit_broken_links.py` `_check_blueprint_id_exists`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-3**：解决"index.md 列出的文件清单是否存在无检测"防护缺口。对名为 index.md 的文件做**严格本地解析**（仅相对 source.parent，禁 basename 兜底——本目录契约语义）。处理 markdown 链接 + `file:///D:/ZephyrAlpha/...` 绝对 URL 两种格式。真源：[`audit_broken_links.py` `_check_index_md_inventory`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。
  - **治本 GAP-4**：解决"audit_report 审计对象存在性无检测"防护缺口。对 doc_type=audit_report 的 .md 文件，校验三类引用：①frontmatter.blueprint_id ②frontmatter.module_id ③正文 MODULE_ID 匹配（MOD-XXX-NNN module_id / D-XXX-NNN submodule_id / SH-XXX-NNN module_id 双轨制+submodule_id）。自动生成 audit_report（无 blueprint_id 无 module_id）跳过。真源：[`audit_broken_links.py` `_check_audit_report_objects`](file:///d:/ZephyrAlpha/scripts/governance/d2_links/audit_broken_links.py) 函数。已检出幻觉：ai_12/17/18_report.md 引用不存在的 `MOD-DB_DEPGRAPH_PG`/`MOD-INF`。
  - **DOC-REF-BROKEN GitCommitGateway in-process 门禁**（与上述 GATE-FRONTMATTER/DOC-REF pre-commit hook 互补的第二层断链检测，2026-08-05 治本）：[`doc_ref_broken_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/doc_ref_broken_gate.py)（priority=91，GitCommitGateway `__init__` 自动注册）检测 staged 新增 .md 文件的 markdown 断链。两处治本：① `file:///d:/ZephyrAlpha/...` 绝对路径链接正确解析（`_resolve_file_url` 提取本地路径后 `os.path.exists` 检查，不当相对路径误判）；② **草稿/归档区豁免**——`_working`/`_archive`/`_backups`/`session_logs` 目录跳过扫描（对齐 N-16 `skip_dirs_docs` SSoT，从 [trae_028.yaml §n16_config.skip_dirs_docs](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml) 动态加载，fail-open 回退硬编码）。**语义**：草稿区（施工方案/评估报告/临时笔记）可能引用待创建文件，属正常前瞻性规划，不应被断链门禁扫描误伤不相关 commit；N-16 同样跳过这些目录，跨门禁语义一致。

- **tests/ 目录组织规范（向内收防回归，[#ARCH-029](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 治本）**——病根：tests/ 根曾平铺 1699 个 test_*.py（新 AI 无法定位 + 无分类指引），子目录粒度混合维度（unit/integration/e2e 按测试类型 vs governance/llm_security 按功能域 vs contract/contracts 按测试种类），contract/ 与 contracts/ 单复数歧义并存。治本约定（文档化防回归，无硬门禁——AD-GOV-001 收敛期不新增 gate）：
  - **单一维度=功能域**：tests/ 子目录按功能域归类（a2a/skill/trae_rules/kb/governance/llm_security/...），不混入测试类型维度（unit/integration/e2e）。新测试文件按文件名前缀归对应功能域子目录。
  - **根目录禁平铺**：tests/ 根目录禁止新增 test_*.py 平铺文件（根目录仅允许 conftest.py/__init__.py 等基础文件）。新增 test_*.py MUST 归功能域子目录。
  - **contracts/ 唯一**：契约测试唯一目录为 `contracts/`（单复数歧义已消除——原 `contract/` 元测试 5 文件已合并入 `contracts/_meta/`）。禁止再造 `contract/` 单数目录。
  - **目录名禁 test_ 前缀**：tests/ 下子目录名禁止 `test_` 前缀（`test_code_dedup_engine/` 已改名 `code_dedup_engine/`）。`test_` 前缀只用于文件名。
  - **迁移状态**：ARCH-029 全部治本完成——1699/1699 文件已迁移（100%），tests/ 根目录扁平 test_*.py 清零，84 个功能域子目录。session3 路线B 全量治本：批次1 commit 6fc3c755（471文件 governance/feedback/audit/llm_security）；批次2 commit 218a870a（291文件 34个子目录）。分类方法：AST import 自动匹配 533 + AI 语义分析 229（BLUEPRINT 优先）。维度混合清理（session4）：批次1 commit 556a845c 消除 6 个测试类型维度目录（integration/e2e/adversarial/red_blue/benchmarks/performance，96文件）；批次2+3 commit b25d9a46 消除 unit/ 目录（25子目录合并+132平铺文件分类迁移，548文件）。至此 tests/ 下 7 个测试类型维度目录全部消除，全部按功能域归类。漂移源 `validate_test_directory_structure.py` 与本条冲突+虚假引用 GOV-DOC-002，已删除（session3 commit）。
  - **强制方式**：文档约定（本条目）+ code review + **GATE-NO-TESTS-UNIT 硬阻断门禁**。
  - **自动化 guard**（ARCH-029 漂移种子防复发，2026-07-01 添加）：[`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) `id: gate-no-tests-unit`，pygrep hook 检测活跃代码/文档中 `tests/unit/` 旧路径重引入，检测到即 exit 1 拒绝提交。豁免：`_archive/`、`scripts/_archive/`、`scripts/.*/_archive/`、`session_logs/`、`data/`、`reports/`、历史规则文件(`trae_028/034`)、`.pre-commit-config.yaml`、`AGENTS.md` 自身（文档真源需描述旧路径）。每次 `git commit` 自动触发，无需手工干预。治本依据：并发 session 不知情回退已修复文件（commit 021c2274 后被回退为 tests/unit/），证明无 guard 时漂移会重新发生。

- **代码重复检测门禁**（GATE-DEDUP，2026-07-06 新增，阶段1 manual）→ 病根：`code_dedup` 引擎 64 文件（MOD-INF-017）有蓝图背书+测试覆盖+capability 登记，但生产侧去重管线未接通——`ct_deduplication.py` handler 引用不存在的 `zephyr.governance.scanner`，静默吞错返回空列表（P2-10 审计发现）。[ARCH-027 §3b](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 裁定"管线未接通"是合法保留理由，但必须三阶段强制接入，禁止永久 silent fail：
  - **阶段1（当前，manual）**：[`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) `id: gate-dedup`，`stages: [manual]`——手动 `pre-commit run gate-dedup` 可用，不阻断常规 commit。委托 [`verify_dedup.py`](file:///d:/ZephyrAlpha/scripts/pre_commit/verify_dedup.py) → [`zephyr.governance.code_dedup.cli verify`](file:///d:/ZephyrAlpha/src/zephyr/gov_code_quality/code_dedup/cli.py)，AST 级函数粒度重复检测（incremental/full scan mode）。退出码：0=PASS / 1=WARN / 2=ERROR。
  - **阶段2（待定，CI）**：`pre-commit run gate-dedup --all-files` 加入 CI pipeline，PR 时自动运行。
  - **阶段3（待定，commit 阻断）**：移除 `stages: [manual]`，commit 时自动阻断高严重度重复。
  - **handler 显式未接通标注**（P2-10-1 修复，**历史记录——check_types/ 已删除**）：原 `ct_deduplication.py` 的 `DeduplicationHandler.run()` 不再 try/except 静默吞错，显式返回 `"Deduplication pipeline not connected"` P2 违规——该 handler 连同整个 `check_types/` 目录已作为死代码删除（commit `efc31ce4ff`，CheckTypeHandler ABC + 33 ct_*.py 从未被 `_run_check` 调用，Phase 2 由 `_CHECK_DISPATCH` 替代）。
  - **capability 反查**：`rule_registry_collection.yaml` 已登记 `verify_dedup.py` 条目（`file: scripts/pre_commit/verify_dedup.py`）；`cross_module_dependency_registry.yaml` 已登记 GATE-DEDUP 引用（`description: GATE-DEDUP pre-commit 门禁判定逻辑`）。新 AI 想做"代码重复检测/dedup 检查"前，应反查本条目，扩展 `code_dedup` 引擎而非新建 checker。
- **错误消息风格规范（5.99.22 防复发，2026-07-07）**——`raise` 语句的错误消息文本 MUST 遵循统一风格：①**箭头符号用 ASCII `->`**（禁止 Unicode `→`，避免编辑器/终端显示差异）；②**中文消息不以句号 `。` 结尾**（错误消息是短语不是句子，与项目既有主流风格一致）。**强制方式**：code review + CI 兜底（无 AST 门禁，靠 AGENTS.md 规则约束新代码）。历史违规已由 5.99.22 第78轮修复清理（13处：7处 `→`→`->` + 6处句号去除）。
- **异步IO最佳实践（5.100 防复发，2026-07-07）**——`async def` 函数内禁止直接调用同步阻塞IO（文件读写/网络/DB），MUST 用以下标准API委托：①**同步函数调用**用 `await loop.run_in_executor(None, fn, *args)`（`loop = asyncio.get_running_loop()`）；②**同步IO操作**用 `await asyncio.to_thread(fn, *args)`（Python 3.9+，语义更清晰）。**典型场景**：`async def` 内调用 `_load_env_file()`/`handle_request()`/`sqlite3.connect()` 等同步函数。**强制方式**：code review + CI 兜底（无 AST 门禁，靠 AGENTS.md 规则约束新代码）。历史违规已由 5.100 第79轮修复清理（3处：secrets.py + 2个 _base_server.py）。
- **自定义 noqa 豁免机制（#ARCH-NOQA-GOV-001 治本，2026-07-17）**——项目使用7种自定义 `# noqa: <marker>` 标记豁免 M 系列指标检测与 gate 行级检测，7种标记的适用场景由 [noqa_exempt_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml) SSoT 定义。使用规则：
  - **SSoT**：[noqa_exempt_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml) 是合法标记清单唯一真源（规则数据，TRAE-062），检测器禁止硬编码标记字符串，MUST 从 registry 动态加载（派生缓存单向）
  - **7种合法标记**：`m02-manual`（per-file，manual-only 永久脚本豁免——CLI 启动的常驻服务）/`m03-duplicate`（per-file，重复簇函数豁免——AI 趋同演化非复制粘贴）/`m07-orphan`（per-file，死代码/orphan 模块豁免——动态引用无法被静态扫描发现）/`m10-time-trigger`（per-file，时间触发残留豁免——注释/枚举值/锁等待等非真实时间触发）/`gate-vocab`（per-file，GATE-VOCAB 词表硬编码豁免——DDL-as-Code 枚举/schema 合法值）/`MSG-EXPOSURE`（per-line，msg_exposure_gate 行级豁免——raise 语句异常消息含敏感变量名的合规特殊情况）/`MSG-STYLE`（per-line，msg_style_gate 行级豁免——raise 语句异常消息含 Unicode 箭头/中文句号的合规特殊情况）——详细适用场景见 registry `applicable_conditions` 字段
  - **格式要求**：`# noqa: <marker>  <METRIC>豁免: <理由>`（双空格分隔 marker 与理由，理由>=10字符）。示例：`# noqa: m10-time-trigger  M10豁免: while True+time.sleep是_GlobalCommitLock文件锁等待循环，非周期触发`
  - **门禁强制**：[noqa_validation_gate.py](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/noqa_validation_gate.py) priority=71 在 GitCommitGateway pre-commit 阶段硬阻断——校验 staged `.py` 文件中的自定义 noqa 标记 ①是否登记到 registry ②是否附理由（>=10字符）。ruff 标准码（正则 `^[A-Z]+\d+$`，如 `E402`/`BLE001`）跳过本 gate（由 ruff 自身校验，不重复）。**fail-open**：registry 加载失败时不阻断（避免门禁死锁，检测器降级为无校验）
  - **新标记流程**：①在 [noqa_exempt_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml) `markers` 列表登记（字段：marker/metric_id/description/applicable_conditions/reason_required/reason_format/reason_min_length/scope/created/created_by）→ ②直接使用（gate 下一 commit 起自动识别）→ ③如需 dashboard 配套检测，在 [architecture_health_dashboard.py](file:///d:/ZephyrAlpha/scripts/governance/architecture_health_dashboard.py) 用 `_has_noqa_exempt(source, "<marker>")` 调用
  - **运行时检测**：[architecture_health_dashboard.py](file:///d:/ZephyrAlpha/scripts/governance/architecture_health_dashboard.py) 的 `_has_noqa_exempt(source, marker)` helper 是统一抽象，替代4处 inline `if "# noqa: <marker>" in source: continue` 重复模式——标记合法性由 commit gate 强制，本函数只负责运行时检测字符串是否存在
  - **capability 反查**：新 AI 想做"noqa 标记校验/豁免管理"前，应反查 [capability_canonical_file_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 的 `noqa_validation_gate`（aliases: NOQA-VALIDATION/noqa-validation/make_noqa_validation_gate/noqa_marker_blocker/noqa_exempt_enforcer）与 `noqa_exempt_registry`（aliases: NOQA-EXEMPT-REGISTRY/noqa-exempt-registry/noqa_exempt_registry_yaml/noqa_marker_ssoT）两个 capability，扩展已有组件而非新建
- **DOMAIN_NAME_ZH 字典直接访问硬阻断（Step 2.5 遗留风险修复，2026-07-19）**——v2.3 治本将 `DOMAIN_NAME_ZH` 瘦身为纯测试域 fallback（73→10 entry）后，生产域中文名真源归 DB。但无门禁阻止新 AI 重新引入 `DOMAIN_NAME_ZH.get(...)` / `DOMAIN_NAME_ZH[...]` 等直接访问绕过 DB 优先级链——君子协定易被绕过。**门禁强制**：[`domain_name_zh_direct_access_gate.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/domain_name_zh_direct_access_gate.py) priority=72 在 GitCommitGateway pre-commit 阶段硬阻断——diff-based 检测 staged `.py` added 行中 `DOMAIN_NAME_ZH` 字典直接访问（正则 `\bDOMAIN_NAME_ZH\b\s*(?:\.|\[)`，覆盖 `.get/.pop/.items/.keys/.values/.update` + 下标访问），命中→硬阻断。**SSoT 定义文件豁免**：[`scripts/governance/d5_architecture/generators/domain_name_mapping.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/domain_name_mapping.py)（`DOMAIN_NAME_ZH` 字典定义位置）；**tests/ 豁免**；**import/注释/docstring 行豁免**（基于 `_diff_helpers._is_exempt_line`）。**fail-open**：git diff 不可达时 PASS（logger.warning）；**fail-closed**：检出违规则阻断（passed=False）。**正确用法**：所有生产代码改走 [`get_domain_name_zh(domain_id, fallback="")`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/domain_name_mapping.py) / [`get_domain_name_zh_strict(domain_id)`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/domain_name_mapping.py) helper——真源优先级链 DB→YAML→硬编码（测试域）→domain_id 4 层 fallback。**capability 反查**：已登记 `domain_name_zh_direct_access_gate`（[capability_canonical_file_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) aliases: NO-DOMAIN-NAME-ZH-DIRECT-ACCESS/domain_name_zh_direct_access/make_domain_name_zh_direct_access_gate）。新 AI 想做"DOMAIN_NAME_ZH 直接访问检测/中文域名映射"前，CapabilityLookup 会反查阻止重复造轮子。
- **测试断言 SSoT 派生规则（P1-1，2026-07-18）**——测试断言禁止硬编码"派生计数/派生集合/派生字面量"，MUST 从 SSoT 真源动态派生。**SSoT 真源识别**：枚举类 / YAML registry / depgraph DB 查询 / 模块级 `Final` 常量。**典型场景**：①成员数断言 `assert len(roles) == 7` → `assert len(roles) == len(RbacRole)`；②值断言 `assert role.value == "writer"` → `assert role.value == RbacRole.WRITER.value`；③集合断言 `assert set(names) == {"A","B","C"}` → `assert set(names) == {e.name for e in MyEnum}`。**强制方式**：code review + CI 兜底（无 AST 门禁，靠 AGENTS.md 规则约束新代码）。**合理例外**：①字面量本身是 SSoT（如 YAML 词表的合法值）；②回归测试固化历史行为（注释说明）。
- **架构健康度仪表盘（M01-M31 共 30 项自动化检测基线，#ARCH-HEALTH-DASHBOARD-001，2026-07-20 立项）**——项目唯一的架构健康度自动化检测系统，覆盖 5 个病根（SSoT 真源唯一性 / 永久系统触发 / 新 AI 可发现性 / DB 全景图深度 / 文档引用断裂）。**真源**：[`architecture_health_dashboard.py`](file:///d:/ZephyrAlpha/scripts/governance/architecture_health_dashboard.py) 的 `METRICS` 列表（30 项 metric 函数，M01-M31）。**触发**：post-commit reconciler `make_architecture_health_reconciler`（priority=300）在任何 `.py` 文件变更后自动调用 `architecture_health_dashboard.py --snapshot`，快照落盘 `data/architecture_health/dashboard_<ts>.json + latest.json`。**模式**：第0期 warn-only（exit 0 不阻断 commit，仅记录基线）；第1期升级路径转 pre-commit hard block（exit 1 阻断）。**指标分类**：①M01-M14 原始基线（已全部归零 2026-07-18）；②M15-M21 治本进度追踪；③M22-M29 P1 防复发 metric（docstring/asyncio/TODO/open/资源清理）；④M30-M31 P2 防复发 metric（ZEPHYR_ENV 直接访问 / MCP version 覆盖）。**扩展规则**：新增 metric MUST ①加入 `METRICS` 列表（id, name, callable 三元组）②实现 `metric_NN_xxx() -> dict` 函数（返回 `_make_metric(...)` 标准结构）③配测试（`tests/governance/test_architecture_health_dashboard_metrics*.py`）④同步 `trae_081_audit_dimensions_framework.yaml` 对应维度防复发列 M01-MNN ⑤复杂度≤15（超阈值用 Extract Method 提取辅助函数）。**capability 反查**：已登记 `architecture_health_dashboard`（[capability_canonical_file_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) aliases: ARCH-HEALTH/architecture_health/M11/metric_11）。新 AI 想做"架构健康度检测/违规计数/趋势监控/防复发检测"前，应反查本 capability 扩展现有 metric，**禁止新建重复检测脚本**。**描述漂移自动校验**：改 METRICS 列表后，[`metric_count_drift_reconciler`](file:///d:/ZephyrAlpha/scripts/governance/d8_doc_sync/metric_count_drift_reconciler.py)（post-commit，priority=220，#ARCH-HEALTH-DASHBOARD-001 阶段2治本）自动校验 4 个派生文件（dashboard.py 表头/docstring/manifest、reconciliation_registry.py 注释、script_manifest.yaml description、capability_canonical_file_registry.yaml description）的指标数描述与 len(METRICS) 一致性，漂移时 warn 写入 reconcile_execution_log。新 AI 改 METRICS 无需手工同步描述，reconciler 会替你盯着。

## 8. 永远不要做的事

> 完整禁止清单见 [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) 四条铁律。此处仅列项目宪法级禁令：

- 不要删除 `data/` 下的任何文件
- **数据真源唯一位置（data/ 目录，src/ 禁 data/ 子目录）**：`data/` 是运行态数据（brain passport / audit_logs / telemetry / capability_cards 等）唯一合法存放位置。**禁止在 `src/` 下创建 `data/` 子目录**——双真源漂移根因（历史教训：`src/data/brain/passports/` 与 `data/brain/passports/` 并存导致版本漂移，2026-06-27 清理 commit 36871193）。规则真源见 [trae_047 §gov_eng_002_directory_mapping](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml) 禁止规则；pre-commit 钩子 [`gate-src-no-data`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_src_no_data.py) 自动检测 staged 文件 `src/data/` 路径前缀，`--ci` 硬阻断；gateway 路径下 src/data/ 检测失效（靠 pre-commit gate-src-no-data + CI 兜底）。
- **文件清理操作规范（禁止只删工作区不 git rm）**：删除文件时必须用 `git rm <file>` 或通过 [`GitCommitGateway --files <deleted_file>`](file:///d:/ZephyrAlpha/scripts/git_commit.py) 提交删除——**禁止只 `rm`/`del` 工作区文件而不 git rm**（会产生 D 悬空文件污染 git status，历史教训：2026-06-27 清理 51 个 D 悬空文件 commit efc2d03b/5f2835bb）。正确流程：`git rm <file>` → GitCommitGateway 提交；或直接 `GitCommitGateway --files <file>` 传 D 状态文件（gateway 第 112-131 行识别 D 场景放行）。
- **临时文件命名规范（_tmp_/_debug_ 前缀 + 用完即删）**：一次性脚本必须用 `_tmp_` 前缀（如 `scripts/_tmp_scan.py`），调试测试必须用 `_debug_` 前缀（如 `tests/_debug_race.py`），任务完成后立即删除。**禁止创建 .bak/.baseline/.backup 备份文件**——用 `git stash`/`git diff` 替代。GATE-ZR [`detect_temp_files.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/detect_temp_files.py) 自动检测 `_tmp_`/`_debug_`/`.bak`/`.baseline` 等模式，`error` 级别硬阻断（`is_clean=False` 拒绝提交）。
- 不要跳过 `CapabilityRegistry.register()`
- 不要修改 `AiAuditLogger` 的已有日志
- 不要创建新模块而不注册到大脑
- **reconciler auto-commit 统一入口（2026-06-30 红蓝对抗治本修订）**：7 个 reconciler（manifest/rule_catalog/registry_index/working_docs/domain_doc/arch_model/vocab_change）的 auto-commit 统一经 [`_commit_auto()`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)，禁止裸调 [`_run_git(["git","commit",...])`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)。**DCR gate 真源复用**：`_commit_auto` 通过 `gate_registry.get("DIRECTORY-CONTRACT")` 获取已注册 GateSpec，调其 check 方法对 reconciler 提交的文件跑 DCR 等效校验（真源唯一在 [directory_contract_gate.py](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/directory_contract_gate.py) → [check_directory_contract.py](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py)），不复制检测逻辑。**只跑 DCR gate + TTL-METADATA gate**（不触发全部 gate，避免 CLAIM-REQUIRED/HELD-OVERLAP 等对 reconciler 无意义的 gate 误阻断）；**ttl 校验靠 TTL-METADATA gate**（gateway 内置，同 DCR gate 的 `gate_registry.get("TTL-METADATA")` 复用模式，subprocess 调 check_frontmatter_metadata.py 真源，见上方"TTL 校验统一拦截点"）。**arch_model reconciler 特例**：双树合并（2026-06-30）已完成，`_ARCH_MODEL_INDEX` 已指向根树 `architecture_model/index.yaml`，DCR gate 不再触发 NAMING_VIOLATION（保留 warn 降级作为防御纵深）。**新增 gate 同步评估**：新增 pre-commit gate 时 MUST 评估 `_commit_auto` 是否需要同步——新增 gate 若涉及机器生成文件的安全约束（如目录/扩展名/内容校验），MUST 在 `_commit_auto` 中同步加入（对标 DCR gate 的 `gate_registry.get` 复用模式）；若 gate 仅对人工提交有意义（如 claim/overlap/promote），则不同步（`_commit_auto` 无 session claim 语义）。判断标准：reconciler 是否会提交该 gate 关心的文件？
- **GitCommitGateway 僵尸锁自愈**：全局锁 `_GlobalCommitLock` 获取前先调 [`is_pid_alive(pid)`](file:///d:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py) 检查持有进程存活——进程崩溃时锁文件残留，PID 已死则立即清理（零窗口期），不靠 TTL 30min 过期。`is_pid_alive` 真源唯一在 [`process_pool.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/infra/process_pool.py)（红蓝对抗归一：曾三处分裂——gateway/ide_health_service/_concurrency 各自定义，现统一；语义最匹配：与 PooledProcess.is_alive / _reap_zombies 同属进程存活检测）。调用方 MUST `from zephyr.shared.infra.process_pool import is_pid_alive`，禁止重复定义（capability_id=process_liveness_detection）。
- **GitCommitGateway 中文 aliases 门禁**：CJK alias 约束仅靠 [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 头部注释文档约定 + code review（[`capability_overlap_gate`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/capability_overlap_gate.py) 只做文件名 token 重叠检测，不查 CJK）。
- **GitCommitGateway REPO_ROOT 门禁**：REPO_ROOT 违规检测仅靠 pre-commit hook GATE-DD07（warn-only，被 gateway `--no-verify` 绕过）+ CI 兜底。REPO_ROOT 真源归一约定见 §7。
- **GitCommitGateway rename fallback（方案 A 治本，红蓝审核 v2 内迁）**：[`_commit_with_file_message`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 是 commit 唯一真源入口，内置 rename 检测（[`_has_staged_renames`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)）+ staged 验证（[`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py)）。根因：`git commit --pathspec-from-file` 对 staged rename（R100）拆分为独立 add+delete，只提交 pathspec 匹配部分，破坏 rename。治本：pathspec 为默认（多 session 安全，pathspec 限制范围不捡拾其他 session WIP），检测到目标文件有 rename 时自动切换无 pathspec 模式 + staged 验证（防误提交其他 session WIP）。rename 检测逻辑内迁到 `_commit_with_file_message`（红蓝审核 v2 治本），`_commit_locked` 和 `_commit_auto` 无需重复调用 `_has_staged_renames`，reconciler 路径自动获得 rename 保护（原 `_commit_auto` 无 rename 保护是漏洞）。`_collect_non_target_rel` 已修复 rename 格式 `R old -> new` 的路径解析（提取新路径），确保其他 session 的 staged rename 能被正确 stash。**staging 区自动清理（ARCH-038 治本，2026-07-01）**：无 pathspec 模式下 `_verify_staged_is_clean` 检查失败时（staging 区有并发 session 污染的非目标文件），不再直接拒绝 commit，而是由 [`_unstage_non_target_files`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 自动 `git reset HEAD -- <非目标文件>` 清理后重新验证，通过则继续 commit。此前需调用方手动 unstage（反复出现 commit 卡死）。回归测试 [`test_rename_with_dirty_staged_auto_unstage`](file:///d:/ZephyrAlpha/tests/git/test_git_commit_gateway.py)。
- **GitCommitGateway staged delete 保护（gitignored 文件 no-pathspec commit，5 层纵深防御）**：[`_commit_locked`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 当目标含 gitignored 文件时（`len(normal_files) < len(files)`）传 `None` 作为 pathspec，用 no-pathspec commit。根因：`git commit -- <pathspec>` 提交**工作区状态**而非**暂存区状态**——对 gitignored 文件，工作区状态无法被 stage（gitignore 阻止），staged delete（`git rm --cached`）被静默跳过。历史教训：commit `32ead90e` 漏提交 5 个 egg_info 删除（staged delete 被吞，只提交了 3 个修改文件）。5 层纵深防御：① [`_is_staged_delete`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 显式识别 staged delete 状态（不在 index AND 在 HEAD），[`_stage_gitignored_tracked`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) existing 分支跳过此类文件，防 `git add -f` 撤销用户的 staged delete；② [`_should_use_no_pathspec`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 检测目标含 gitignored 文件时返回 True，[`_commit_locked`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 据此切换 no-pathspec commit + [`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 验证 staged 区只有目标文件（防误提交其他 session WIP）；③ [`_collect_non_target_rel`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) + [`_stash_other_files`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) + [`_verify_staged_is_clean`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 用 `os.path.normcase()` 大小写不敏感匹配——`Path.resolve()` 在文件不存在磁盘时无法归一化大小写，导致 staged delete 文件被误判为非目标 → 被 stash 走（Windows 大小写不敏感必须用 normcase）。回归测试 [`TestStagedDeleteGitignored`](file:///d:/ZephyrAlpha/tests/git/test_git_commit_gateway.py)。新 AI 勿误判 no-pathspec 分支或 `_is_staged_delete` 为冗余删掉——pathspec commit 对 gitignored staged delete 静默丢失是已验证 bug。
- **GATE-COMMIT-GW 裸 commit 检测门禁（OPS-2026062513 治本，RB-6 修复 2026-06-29）**：[`validate_commit_gateway.py`](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/validate_commit_gateway.py) 是 pre-commit hook（`.pre-commit-config.yaml` gate-commit-gw，`always_run: true`），强制所有 commit 走 GitCommitGateway。**检测逻辑（红蓝修复后）**：hook 运行本身=裸 commit（gateway 用 `--no-verify` 绕过 hook）→ 阻断 exit 1；合并提交（`.git/MERGE_HEAD` 存在）放行。**废除的旧逻辑**：env var `ZEPHYR_COMMIT_GATEWAY=1` 检查（RB-2：env var 在 shell 中持久存在，可绕过）和 commit message `[GW:...]` 标记检查（RB-6：伪造标记可绕过）。**唯一合法绕过**：`git commit --no-verify`（conscious bypass，由 GATE-INTEGRITY-AUDIT 审计 reconciler 追踪）。**纵深防御**：① 本 hook 拦截非 `--no-verify` 路径 ② post-commit 审计 reconciler 扫描最近 20 个 commit，标记无 `[GW:]` 的裸 commit ③ 过程纪律（code review）。
- **GATE-INTEGRITY-AUDIT post-commit 审计+引用检测 reconciler（含原 COMMIT-GW-AUDIT + 新增 AGENTS-MD-REFS，C级 缺口4 + 元问题1治本）**：[`make_integrity_audit_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（priority=810）3-way compose 合并三个检测：① GATE-RULES-INTEGRITY（priority=270）重注册 rules_integrity 基线 ② GATE-COMMIT-GW-AUDIT（priority=800）审计最近 20 个 commit 标记无 `[GW:` 标记的裸 commit（merge commit 跳过），报告落盘 `.runtime/reconcile_reports/commit_gateway_audit_<ts>.json` ③ **GATE-AGENTS-MD-REFS（priority=810，元问题1治本 2026-06-30）**检测 AGENTS.md 中引用的 `make_*_reconciler` 公共函数名是否在 `reconciliation_registry.__all__` 中——病根：AGENTS.md 硬编码函数名，reconciler 重命名/合并后 AGENTS.md 不会自动更新，新AI按失效指引造幻觉（如步骤1修复的 `_make_old_rules_integrity_reconciler` 失效引用）。检测到失效引用→warn（非阻断，detail 列出失效函数名供人工修正）。trigger：AGENTS.md 或 reconciliation_registry.py 变更时触发。非阻断（warn），供追责与修正。
- **AD-GOV-001 reconciler 合并策略（compose，2026-06-30 治理收敛）**：5 组职能重叠的 reconciler 已通过 [`_compose_reconcilers`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) 合并为 5 个新入口（16→11）。**compose 规则**：① trigger = 所有 spec trigger 的 OR（任一命中即执行）② reconcile = 串联执行全部 spec（按传入顺序），action 取较严重（severity: skip=0/clean=1/warn=2/auto_committed=2），detail 平铺拼接 ③ priority = max(所有 spec)。**`_compose_reconcilers` 支持 `*specs` 可变参数**（元问题1治本扩展 2026-06-30：原签名只支持 2 个 spec，GATE-INTEGRITY-AUDIT 3-way 合并需可变参数；向后兼容 2 参数，5 个现有调用点零回归）。**合并映射**：GATE-GHOST+GATE-WORKING-DOCS→GATE-DELETE-AUDIT；GATE-DOMAIN-DOC+GATE-ARCH-MODEL→GATE-REGENERATE；GATE-RULE-CATALOG+GATE-RULE-FILE-AUDIT→GATE-RULE-AUDIT；GATE-REGISTRY-INDEX+GATE-BASELINE-AWARE→GATE-REGISTRY-SYNC；GATE-RULES-INTEGRITY+GATE-COMMIT-GW-AUDIT+GATE-AGENTS-MD-REFS→GATE-INTEGRITY-AUDIT（3-way，元问题1治本）。**`_make_old_*` 私有函数已删除（2026-06-30 元问题4治本）**：原 `_make_old_*_reconciler` 私有函数已删除，reconcile 逻辑内联到 5 个 `make_*` compose 包装函数闭包中（Python 无真私有，保留等于留可 import 的绕过入口；内联后仅在闭包内可见）。测试规范见 [`test_integrity_audit_reconciler.py`](file:///d:/ZephyrAlpha/tests/governance/audit/test_integrity_audit_reconciler.py)——用公共 API + mock spec + 模块级函数 `_audit_commit_history` 测试。**AD-GOV-001 收敛期约束**：新增 reconciler 前 MUST 过 [trae_060 §4](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml) 元问题审查（该不该存在/能否合并进已有），教训登记 [#ARCH-028](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)。
- **废弃目录门禁 GATE-DEPRECATED-DIR（09_audit 治本加固，红蓝对抗修复）**：双层防御（①② 层均已于 2026-06-30 修复）——① [`directory_contract_gate`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/directory_contract_gate.py)（priority=30，注册制 gate）通过 subprocess 调用 [`check_directory_contract.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py)，`scan_files` 调用 [`check_deprecated_directory`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py) 检测提交文件是否位于 [`directory_contract.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml) §7 `deprecated_directories` 字段声明的废弃目录（当前含 `docs/09_audit/`），命中则阻断——gateway 内嵌注册制 gate，`--no-verify` 绕不过（2026-06-30 补全：原 `_check_deprecated_directories` 在 AD-001 阶段3 删除后 `scan_files` 漏检 deprecated_directories，新增 `check_deprecated_directory` 函数修复）；② [`make_deprecated_directory_reconciler`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（priority=600）post-commit **自动修复**（2026-06-30 治本：从 directory_contract.yaml §7 `deprecated_directories` 字段动态加载）：检测到废弃目录存在时自动迁移文件到 `docs/_working/audit/` + 删除空目录。报告落盘 `.runtime/reconcile_reports/deprecated_directory_<ts>.json`。
- **审计产物路径引导（09_audit 治本，新 AI 必读）**：审计报告 / session handoff / 安全 finding / 红蓝对抗报告等审计产物**统一写入 `docs/_working/audit/`**（子目录：`handoff/`、`findings/`、`reports/`、`STATE/`）。**禁止 `docs/09_audit/`**——该目录已合并入 `docs/_working/audit/`（[trae_047 gov_eng_002_directory_mapping](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml) YAML key `gov_eng_002_directory_mapping`）。`doc_type_vocabulary.yaml` 中 `audit_report` 的 `allowed_directories: ["_working/audit/"]`。新 AI 创建审计产物时按此路径引导，违反将被 GATE-DEPRECATED-DIR 阻断。
- **禁止手工创建 YAML tracker（漂移源治本，2026-06-29）**：禁止在 `docs/03_modules/` 下手工创建 `*_tracker.yaml`/`*_matrix.yaml`/`phase_plan.yaml`/`a2a_anomaly.yaml`/`adversarial_test_report.yaml`/`decomposition_completeness.yaml` 等过程态 YAML 文件——这些是漂移源和孤儿，违反真源唯一 + 向内收原则（tra_060）。**真源已在别处**：① 架构数据真源在 [`depgraph`](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py) PostgreSQL 数据库（通过 `apply_depgraph.py` 修改）② 模块版本真源在蓝图 frontmatter `version` 字段 ③ Python 模块状态真源在代码本身（如 `anomaly_detector.py` 是 canonical）④ 决策记录真源在 `git log` + `data/audit_logs/`。**历史教训**：2026-06-29 删除 11 个漂移/孤儿 YAML（commit `0f8fbe21`），它们用 `# ttl: permanent` 注释锚定（非 frontmatter）自欺永久，实际 0 代码消费 0 蓝图注册，内容与 depgraph/蓝图矛盾（如 `version_tracker.yaml` 声明 V1-V40 实际 V1-V5、`blind_spot_tracker.yaml` 157 vs 183 矛盾）。**注释锚定 ≠ frontmatter**：`# ttl: permanent` 注释不受 GATE-FRONTMATTER（[`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py)）校验保护——GATE-FRONTMATTER 解析 frontmatter `ttl:` 字段（YAML frontmatter / .py 头部 `# [TTL]` 字段），不解析散文注释 `# ttl:`，只有 frontmatter `ttl:` 字段才受校验。**新 AI 引导**：如需追踪过程态，扩展已有 Python 模块（向内收）或写入 `docs/_working/`（task_bound，`completes_when` 声明完成条件后自动归档），禁止创建手工 YAML tracker。
- **治本变更未提交前禁止并发 AI 对话（搭便车治本 codify，2026-06-30）**：治本变更（refactor/fix 涉及多文件）在工作区有未提交 WIP 时，禁止开启并发 AI 对话处理同文件——GitCommitGateway 文件级隔离无法分离同一文件内两个 session 的行级修改，后提交的 session 会把工作区全部修改（含前一个 session WIP）一并提交（"搭便车提交"/ghost commit），导致 commit message 与实际内容不符、回滚连带、审计断裂。**历史教训**：commit `abea0b219c`（GATE-ARCH-MODEL）搭便车带入模式6 代码。约束真源见 [parallel_session_coordination_policy.md §3.2](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md) 治本原理。
- **工作区回退风险（编辑阶段覆盖，2026-06-30 Phase D 治本指针）**：≥2 session 并发时，AI 用 IDE Edit/Write 工具直接编辑共享工作区文件——若 session A 已 commit `foo.py`，session B 的 Edit/Write 工具用旧版本覆盖 `foo.py` 工作区副本，session B 下次 commit 会带回退版本（"工作区回退事故"）。**根因**：AI 工具链不读 HEAD 比对，盲目覆盖磁盘。**Edit/Write 覆盖无法代码层治本**（IDE 工具不能 hook，Edit/Write 工作区固定为项目根，worktree 对 Edit/Write 不适用——但 worktree 对 RunCommand 操作适用，见下条 FP-ISO.4C 治本方案）。**治本路径**：≥2 session 并发时 MUST 走 StagingArea 草稿模式（[project_rules.md §claim 前移协议](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)，[onboarding_detail.md 模式 B](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)），禁止共享工作区直接 Edit/Write。**取消 B2（workspace_drift_reconciler）裁定**：post-commit reconciler 治不了编辑阶段回退（reconciler 在 commit 后触发，工作区回退发生在 Edit/Write 阶段，检测不到），违反第一性原理，不创造无价值代码（向内收原则①）。**指针**：StagingArea 实现见 [`staging_area.py`](file:///d:/ZephyrAlpha/src/zephyr/trading/staging_area.py)，并发协议见 [`parallel_session_coordination_policy.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md)。
**协议层治本补充（2026-06-30 第29轮调研）**：原裁定"代码层无法治本"成立的前提是 claim 必然在 commit 阶段。调研发现 claim 协议前移到 Edit 前（[`git_commit.py --claim-only`](file:///d:/ZephyrAlpha/scripts/git_commit.py)）+ [`pre_write_gate.py --session`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/pre_write_gate.py) 扩展 session_overlap 检测，可在不违反 AD-GOV-001 下显著降低 Edit 阶段覆盖风险（软约束，依赖 AI 自觉；IDE 不可 hook 是硬上限，无法技术强制）。复用 [`SessionRegistry`](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/session_concurrency.py) 已有 API（`find_session_by_file`/`other_held_files`），零新真源，符合向内收。详见 [project_rules.md RULE-ZERO claim 前移协议](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md)。StagingArea 仍为高风险场景的物理隔离兜底。
- **FP-ISO.4C worktree 物理隔离（并发工作丢失治本，2026-07-01，正式规则 2026-07-02 转正）**：41 个并发丢失案例分析结论——Mode A（git stash/reset/checkout 冲掉工作区）占 51%，Mode B（直接编辑同一文件覆盖）占 17%，Mode D（未 commit 被回收）占 7%。**唯一能同时治 A+B+D 的方案是 worktree 物理隔离**：每 AI 对话独占 `.aidrafts/{session_id}/` worktree（独立 git index），从物理层面消除共享工作目录冲突。**AI 对话启动时 MUST 调** [`session_worktree_start`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（返回 `worktree_path`）→ AI 可正常用 Edit/Write 编辑文件（写项目根，`session_worktree_commit` 会自动将改动同步到 worktree）→ 提交调 [`session_worktree_commit`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（自动同步文件项目根→worktree + worktree 内 git add+commit，独立 index 无需 GitCommitGateway，`--no-verify` 绕过 pre-commit hook）→ 完成调 [`session_worktree_merge`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（merge 回主分支 + 清理 worktree）→ 放弃调 [`session_worktree_abort`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（丢弃修改 + 清理）。**GATE-COMMIT-GW 放行**：[`validate_commit_gateway.py`](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/validate_commit_gateway.py) 检测 cwd 含 `.aidrafts/sess-` 时放行 worktree 内 commit（授权绕过 GitCommitGateway 全局锁，worktree 独立 index 无共享冲突）。**底层引擎** [`WorktreeManager`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/worktree_manager.py)（create/merge/cleanup + Windows 文件锁兜底 `_force_rmtree`）。**capability 反查**：已登记 `session_worktree_lifecycle`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)），新 AI 想做"并发隔离/worktree"前 CapabilityLookup 会反查到此。**测试**：[`test_session_worktree.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py)（6 个端到端测试，连续两遍通过）。**文档**：[blueprint §FP-ISO.4C](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md)。**正式规则状态（2026-07-02 转正）**：Trae IDE 不支持自动触发 worktree（无启动 hook、IDE 不可 hook、AI 不可改 cwd），走君子协定——AI 自觉调 start/commit/merge，对标 AI 自觉查锁。6 连续 PASS 已转正式（Round2-4 + Extreme A/B/C，覆盖 Edit tracked/Write 新文件/文件删除/abort 4 种代码路径，merge 首次成功率 3/3）。文件同步已实现（`session_worktree_commit` 内 `shutil.copy2` 项目根→worktree + 文件删除同步），AI 无需手动同步。**HELD-OVERLAP 加硬（2026-07-02，文件锁与 worktree 一样硬）**：`session_worktree_commit` 新增 `allow_overlap: bool = False` 参数，commit 前对每个文件调 `SessionRegistry.claim_file()`（原子 check-and-claim，内部加锁防 TOCTOU）——被其他活跃 session 持有则 `HELD_OVERLAP_VIOLATION` 硬阻断（回滚已 claim 文件，避免 dangling claim 阻塞其他 session）；未被持有则 claim 成功（session 级，不 per-commit 释放）。claim 在 merge/abort 时 `unregister` 自动释放。对标 GitCommitGateway 的 HELD-OVERLAP gate，使 worktree 模式下的文件锁一样硬。`allow_overlap=True` 逃生通道放行（对标 `--allow-overlap`）。**逃生通道（永久保留，非临时）**：HELD-OVERLAP 加硬消除了"两 session 编辑同一文件"的搭便车根因，但无法解决 git 固有 merge conflict（`allow_overlap=True` 强行覆盖时两分支改同一文件 git 无法自动合并）+ AI commit 后又编辑同一文件导致内容漂移（pre-merge auto-clean 跳过不一致文件）——此时 `session_worktree_abort` + 改用 GitCommitGateway（stash 隔离）作为兜底。测试：`test_worktree_commit_held_overlap_blocks`/`test_worktree_commit_allow_overlap`/`test_worktree_merge_releases_claims`（11/11 PASS）。**pre-merge gate 检查 + reconcile_verify 默认 True（2026-07-04，治本 merge 前 gate 漂移 + post-merge reconciler 缺失）**：[`session_worktree_merge`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 在 `_pre_merge_auto_clean` 后执行 `_pre_merge_gate_check`——用 `git reset --soft merge-base` 模拟 staged 状态运行 7 个 worktree-compatible gate（跳过 HELD-OVERLAP/CLAIM-REQUIRED，捕获 commit 后到 merge 前主分支更新的 gate 规则，如新 capability 登记），gate 阻断则 return `merged=False`，gate 异常降级为 warn 不阻断，HEAD 用 `git reset --soft orig_head` 恢复。`reconcile_verify` 默认值 False→True：merge 后自动触发 17 个 reconciler（`_run_reconcilers_after_merge`），补齐 post-merge 漂移修复（manifest/path_tree/path_ownership/depgraph_ops 等 auto_commit + warn-only）。治本 worktree commit 绕过 GitCommitGateway 的设计间隙——commit 时 gate 检查通过不代表 merge 时仍通过（主分支可能有新 commit），merge 后 reconciler 不触发则漂移无修复。**breaking_change 并发阻断（§9.7 治本，2026-07-04）**：codify 本文件 §391"治本变更未提交前禁止并发 AI 对话"——原为君子协定（靠 AI 自觉不并发），AI 不遵守就并发导致搭便车提交/工作区回退。[`session_worktree_start`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 新增 `breaking_change: bool = False` + `allow_concurrent: bool = False` 参数，在注册 session 之前执行双向阻断：① `breaking_change=True` 时检查是否有其他活跃 session → 有则返回 `BREAKING_CHANGE_CONCURRENCY_BLOCKED` 阻断（治本变更期间禁止并发）；② `breaking_change=False` 时检查是否有其他活跃 session 声明了 `breaking_change=True`（调 [`SessionRegistry.find_breaking_change_session`](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/session_concurrency.py)）→ 有则返回 `BREAKING_CHANGE_AVOIDANCE_BLOCKED` 阻断（避让治本变更）。`allow_concurrent=True` 逃生通道跳过阻断（对标 `allow_overlap`）。fail-open：并发检测异常不阻断 start（对标 held_overlap_gate fail-open）。**AI 使用指引**：refactor/fix 涉及多文件的治本变更会话 MUST 传 `breaking_change=True` 启动；普通会话默认 `breaking_change=False` 自动避让。**capability 反查**：已登记 `breaking_change_concurrency_blocker`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)），新 AI 搜 "breaking_change/治本变更并发/§9.7" 可定位真源。**测试**：`test_worktree_start_breaking_change_blocks_new_session`/`test_worktree_start_breaking_change_blocks_concurrent_breaking`/`test_worktree_start_breaking_change_allow_concurrent_escape`（3/3 PASS）。**自动触发条件**：Trae 原生支持 worktree（对标 VS Code 1.107）后激活自动 start。
- **FP-ISO.4C stale worktree on-demand 清理（治本遗留项#2，2026-07-17）**：`session_worktree_start` 内部调用私有 `_sweep_stale_worktrees` 清理过期残留——但该函数无公开入口，AI 累积 stale worktree（来自崩溃/放弃的 session）且无新 session 启动时，无 on-demand 清理 API，被迫误调私有函数传入 `Path` 对象导致 `AttributeError`。**治本**：① 新增公开函数 [`session_worktree_sweep`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（包装 `_sweep_stale_worktrees`，返回 `{"swept": int, "skipped": int, "warnings": list[str]}`）；② `_sweep_stale_worktrees` 新增 `isinstance(manager, WorktreeManager)` fail-closed 类型校验（误调返回 error dict 而非抛异常，对标本模块所有函数返回 dict 不抛异常的契约）；③ 新建 CLI [`scripts/governance/session_worktree_cli.py`](file:///d:/ZephyrAlpha/scripts/governance/session_worktree_cli.py)（`sweep`/`list` 子命令），兑现 `session_worktree.py` `[CONSUMERS]` 头部声明（此前声明本文件但本不存在=文档漂移）。**三重保护判据**（`_sweep_stale_worktrees` 实现，sweep 不改变）：目录 age > max_age_minutes（默认 30，太新的不动，防误清并发 AI 正在创建的）+ session 不在 active registry（活跃 session 不动）+ 分支 tip 在 HEAD 祖先或被取代（阶段2治本 2026-07-18：有未合并提交时调 [`_branch_commits_superseded`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 两维度检测——patch-id 等价 `git cherry` 标记 `-` + message 主体匹配 HEAD 近 200 条历史，全部被取代则安全清理，未全被取代则 warning 跳过提示人工处理）。**AI 使用指引**：发现 stale worktree 残留（如 `.aidrafts/` 下有非活跃 session 目录）时，调 `python scripts/governance/session_worktree_cli.py sweep` 清理，或 `python scripts/governance/session_worktree_cli.py list` 查看。**capability 反查**：已登记 `session_worktree_cli`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)）。**测试**：[`test_session_worktree.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py) `test_session_worktree_sweep_public_wrapper`/`test_sweep_type_validation_rejects_path` + [`test_session_worktree_cli.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree_cli.py)（4 个 CLI 测试）。**P2 事件驱动自动清理（治本"君子协定"缺口，2026-07-17）**：原 P1 仅在 `session_worktree_start` 内被动触发 sweep——当无新 session 启动时 stale worktree 永久堆积（违反"永久系统必须全自动"铁律）。**治本**：新增 reconciler `GATE-WORKTREE-LIFECYCLE`（[`reconciliation_registry.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) `make_worktree_lifecycle_reconciler`，priority=800），trigger=`bool(committed_files)`（任何有文件的 commit 都触发——commit 意味着 AI 活跃，是清理 stale 残留的合适时机），reconcile 调 `session_worktree_sweep`，action 语义：`swept>0`→clean / warnings 非空→warn / 异常→warn（降级不阻断）/ 无 stale→skip。**注册激活**：[`git_commit_gateway.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) `__init__` 中 `self._reconciliation_registry.register(make_worktree_lifecycle_reconciler(self))`。**触发覆盖**：① GitCommitGateway.commit 后（主工作区）；② `session_worktree_merge` 后经 `_run_reconcilers_after_merge` 创建临时 GitCommitGateway 实例触发（覆盖 worktree 路径）。**阶段2治本·未合并提交陷阱（#ARCH-WORKTREE-001 第三期，2026-07-18）**：原判据3 对有未合并提交的 worktree 一律跳过（"有未合并提交的不动"）——100% AI 开发场景下死 session 的未合并分支永久堆积（死 session 不会恢复，分支永不合并）。**治本**：[`_sweep_one_dir`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 判据3 扩展——分支 tip 不在 HEAD 祖先时调 [`_branch_commits_superseded`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 两维度取代判定：① patch-id 等价（`git cherry HEAD <branch>` 标记 `-`，diff 内容等价于 HEAD 中某提交）；② message 主体匹配（commit subject 在 HEAD 近 200 条历史中存在）。全部提交被取代时安全清理 worktree（修改已通过其他路径合并），未全被取代则 warning 跳过提示人工处理。**保守策略**：`git cherry` 失败/`head_subjects` 获取失败 → False（宁可保留不误清）。**测试**：[`test_session_worktree.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py) `test_branch_commits_superseded_*`（6 个场景：全 patch-id/混合/未全取代/cherry 失败/空分支/head_subjects 失败）。
- **FP-ISO.4C orphan draft script auto-cleanup（P3 流程治本，2026-07-17）**：AI 在调研/治本过程中常在 `.aidrafts/` 根目录创建 `_*` 一次性辅助脚本（如 `_commit_adp4_adp5.py`/`_merge_adp45.py`），用完未删则永久残留（P0 曾手工清理 3 个此类孤儿）。**病根**：「治本代码自身成为残留」的递归问题——AI→治本→残留→AI→治本。**治本**：[`session_worktree_start`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 在 `_sweep_stale_worktrees` 之后调用 [`_cleanup_orphan_draft_scripts`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（私有 helper，每次 start 自动执行），消除 API 完整性缺口——无需 AI 手工清理。**安全判据（三重，任一不满足则跳过）**：① 仅扫 `.aidrafts/` 根目录（非递归），仅匹配 `_*` 前缀**文件**（非 `sess-*` worktree 目录——worktree 由 `_sweep_stale_worktrees` 处理，非 `_*` 文件不动）；② 文件 age > max_age_seconds（默认 3600s=1h，太新的不动，防误清 AI 正在使用的）；③ OSError 静默跳过（清理失败不阻断 start，对标本模块所有函数返回 dict 不抛异常的契约）。**返回** `{"deleted": int, "skipped": int, "warnings": list[str]}`，deleted/warnings 非空时 logger.info 记录。**与 `_sweep_stale_worktrees` 区分**：`_sweep_stale_worktrees` 清理 `sess-*` worktree 目录（带 git worktree 注册/分支 tip 校验，公开入口 `session_worktree_sweep`）；`_cleanup_orphan_draft_scripts` 清理 `_*` 辅助脚本文件（仅文件 mtime 判定，无私有/公开区分，仅 start 时自动触发）。**测试**：[`test_session_worktree.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py) `test_cleanup_orphan_draft_scripts_*`（覆盖空目录/无 `_` 前缀/age 未到跳过/age 过期删除/OSError 静默跳过/`sess-*` 目录不动 6 个场景）。
- **FP-ISO.4C pre-merge 拓扑硬阻断 PRE-MERGE-TOPO-CHECK（治本遗留项#1 第二期，#ARCH-DEP-001，2026-07-17）**：L1 铁律"依赖关系先行"原为君子协定——`check_blueprint_code_alignment.py` 将 CODE_NOT_IN_DEPGRAPH 定级 LOW（暂态容忍），未登记依赖不硬阻断。**治本第二期**：[`session_worktree_merge`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) → `_pre_merge_gate_check` → [`_run_pre_merge_topo_check`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 在 commit gate 检查后额外执行拓扑硬阻断——subprocess 调 **MAIN 副本** [`check_blueprint_code_alignment.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py) `--json --scan-root <worktree>`（`config/.env.postgres` 被 gitignore，worktree 无 DB 配置，故运行 MAIN 副本 checker + `--scan-root` 仅重定向代码扫描；DB 配置/registries 留 main），扫描 session 分支 `src/zephyr`。**阻断规则**：HIGH drift（ORPHAN_MODULE_ID/MODULE_ID_DRIFT）阻断 merge，过滤到 session 变更文件（仅阻断 session 自身引入的 HIGH，不阻断预存漂移）；LOW（CODE_NOT_IN_DEPGRAPH）暂态容忍（post-merge reconciler 兜底）。**独立于 commit gate**：不受 gate 代码修改降级影响（topo checker 是独立脚本，非 `commit_gates/`，无「鸡生蛋」），即使 commit gate 降级为 warn-only，topo 检查仍执行。**降级策略**：checker 缺失 fail-closed 阻断；DB 不可用（`depgraph_module_ids==0`）/超时/JSON 解析失败/checker exit 2 fail-open 放行（DB 不可用时无法可靠拓扑检查，post-merge reconciler 兜底）。**checker 改动**：[`check_blueprint_code_alignment.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py) 新增 `--scan-root` 参数（向后兼容，默认 None 行为不变）。**测试**：[`test_session_worktree.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py) `test_pre_merge_topo_check_*`（10 个单元测试：clean/2×block/过滤/LOW不阻断/missing fail-closed/timeout/DB-down/JSON-parse/exit2）。第一期文档诚实化（L1 铁律原君子协定状态已在本节如实记录）；第三期 commit-time 轻量预检待定（可选长期）。
- **ARCH-FRONTMATTER-STATE-001 Phase 4 FRONTMATTER_STATE_STALE gate（2026-07-18）**：[`check_blueprint_code_alignment.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py) 新增 L3 frontmatter 缓存 vs L2 depgraph 状态一致性检测——扫描 `docs/03_modules/**/*.md` frontmatter（跳过 `index.md`），比较 `frontmatter.build_status` 与 depgraph 聚合 `build_status`（按 `blueprint_id, (path IS NULL), path` 排序后取第一个非空值，与 [`blueprint_frontmatter_reconciler`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/syncers/blueprint_frontmatter_reconciler.py) 语义对齐）。发现不一致报告 `FRONTMATTER_STATE_STALE`（severity=MEDIUM/WARN，不阻断提交，由 reconciler 在 merge 周期自动修复）。**存量修复**：`generate_project_depgraph.py --force` 全量重建 + `sync_panorama_module.py --all` 同步 169 个模块后，复跑 gate 报告 `FRONTMATTER_STATE_STALE=0`。**测试**：[`test_check_blueprint_code_alignment.py`](file:///d:/ZephyrAlpha/tests/governance/test_check_blueprint_code_alignment.py)（17 个测试覆盖聚合/检测/扫描逻辑）。**registry**：`architecture_issue_registry.yaml` `#ARCH-FRONTMATTER-STATE-001` status→resolved。
- **FP-ISO.4C worktree base 新鲜度检查（裁定#19-B，2026-07-18，治本搭便车提交 + ARCH-REFERENCE L2 误判）**：`session_worktree_commit` 在 [`_sync_files_to_worktree`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 之前调 [`_ensure_worktree_base_fresh`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)——检测 worktree HEAD vs 主工作区 HEAD 是否一致，落后则自动对齐。**病根**：`session_worktree_start` 创建 worktree 时 base = dev HEAD(T0)，并发 session merge 到 dev 后 dev HEAD 前进到 T1（引入新 #ARCH-NNN 引用等），AI 在主工作区 Edit 文件（主工作区文件 = dev T1 内容 + AI 改动），`_sync_files_to_worktree` copy2 主工作区文件到 worktree（base T0），worktree commit 内容 = (dev T1 + AI 改动) − (worktree base T0) = dev T0→T1 改动（搭便车）+ AI 改动。**后果**：① git 历史污染（dev 多 commit 被塞进 session commit，session 之间相互"窃取"工作）；② ARCH-REFERENCE L2 误判（dev 新 `#ARCH-NNN` 引用被算作本次 commit 新增，触发 `ARCH_ATOMICITY_VIOLATION` 硬阻断，要求 registry 同 commit 更新——abort+restart 循环浪费 AI tokens）。**治本**：`_ensure_worktree_base_fresh` 检测 worktree HEAD 是否落后于主工作区 HEAD，落后则：① 无 session commit（start 后第一次 commit）→ `git reset --hard <main HEAD>`（安全，worktree 无未提交工作可丢）；② 有 session commit → `git rebase <main HEAD>`（保留 session 工作，冲突 fail-loud 返回 `base_sync_failed=True` 阻断 + 详细修复指引）。**降级**：`git rev-parse HEAD` / `git merge-base` 失败时返回 None 放行（不阻断业务，对标本模块所有函数返回 dict 不抛异常的契约）。**测试**：[`test_session_worktree.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py)。**战略意义**：100% AI 开发下并发 AI 是常态，worktree base 过期是高频场景，本治本消除"搭便车提交 + 门禁误判"双重故障。
- **FP-ISO.4C worktree base 新鲜度全生命周期扩展（#ARCH-WORKTREE-BASE-FRESHNESS-001，2026-07-21，治本薛定谔的回退）**：裁定#19-B 只在 commit 时检测 base 新鲜度，且 fail-open 降级放行——2026-07-21 多次实时观察到**薛定谔的回退**（Schrödinger's rollback）：① 并发 session 的 merge 触发 `git reset --hard HEAD` 回退所有未提交的主工作区改动；② `session_worktree_merge` 报告 `merged=True` 但 git log 显示无 merge commit，session 分支被删除；③ cherry-pick 孤立 commit 到 dev 后才稳定落地。**病根**：① start/merge 时无 base freshness 检测（只有 commit 时有）；② `_ensure_worktree_base_fresh` 内部 git 命令失败时 fail-open（`return None` 降级放行）；③ `emergency_commit` 是 governance black hole（无一致性检查，无审计痕迹）；④ merge 是薛定谔的回退高发点但无检测。**治本（5 Phase，规则真源 [trae_074](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_074_worktree_base_freshness.yaml)）**：**Phase 1.1** [`session_worktree_start`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 增加 `_ensure_worktree_base_fresh(stage="start")` fail-open（warning + 遥测，不阻断 start）；**Phase 1.2** [`session_worktree_merge`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 增加 `_ensure_worktree_base_fresh(stage="merge")` fail-closed（P0 最关键，薛定谔的回退高发点）；**Phase 1.3** [`_ensure_worktree_base_fresh`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 5 个 fail-open 路径转 fail-closed（git rev-parse/merge-base/rev-list/reset/rebase 失败时返回错误 dict 而非 None）；**Phase 2.1** [`emergency_commit`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py) 主工作区 vs HEAD 一致性检查（warn-only，不阻断 emergency）；**Phase 2.2** emergency_commit reflog message 含 `[emergency_commit]` 标记供事后审计；**Phase 3** [`_log_base_freshness_event`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 遥测落盘 `.runtime/worktree_ops_log.jsonl`（pass / fail_closed / sync_reset / sync_rebase 事件）；**Phase 4** [`TestBaseFreshnessFullLifecycle`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py) 8 个测试。**重试退避设计**：原方案 `time.sleep(0.5 * 2^attempt)` 被 PERM-TRIGGER gate 误判（[TTL] permanent 文件 + time.sleep 被误判为永久系统时间触发）→ 改用 `threading.Event().wait()` 仍被误判（`.wait(timeout=` 也被检测）→ 最终方案 `time.monotonic()` 忙等（无时间触发模式，仅在 git 失败时触发，非热路径）。**逃生通道**：`session_worktree_merge(force=True)` 跳过可绕过类检测（WORKSPACE-CLEAN-CHECK / PRE-MERGE-TOPO-CHECK / commit gate），但**不可绕过** base freshness check（#ARCH-FORCE-MERGE-SAFETY-001 治本，2026-07-22：不可绕过类——无 post-merge 替代 + 跳过后不可挽回）。force=True 仍落审计（`_audit_force_merge_usage`）。**`_run_git_with_retry`** helper：3 次重试 + monotonic 忙等退避，替代散落的 `subprocess.run(..., timeout=10)` 调用。**capability 反查**：已登记 `worktree_base_freshness_check`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)）。
- **FP-ISO.4C worktree commit 持久性 + start fail-closed（#ARCH-WORKTREE-COMMIT-PERSISTENCE-001，2026-07-22，治本薛定谔的回退循环依赖）**：裁定#19-B + #ARCH-WORKTREE-BASE-FRESHNESS-001（TRAE-074）治本薛定谔的回退，但治本过程本身被薛定谔的回退阻击 3 次（commit 323df2fa11 / 105917c872 消失、807f0af9b1 被覆盖），暴露循环依赖：治本薛定谔的回退需用 session_worktree 机制，但 session_worktree 机制自身受薛定谔的回退影响。**病根（第一性原理）**：① session_worktree_commit 创建 commit 后，commit 只存在于 worktree 分支——AI 等待 merge 的窗口期，并发 session 的 sweep 可能删除 worktree + 分支，commit 随分支删除而消失；② session_worktree_start 时 fail-open warning 无效（100% AI 场景下 AI 忽略 warning 直接启动）。**治本（5 Phase，规则真源 [trae_076](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_076_worktree_commit_persistence.yaml)）**：**Phase 1** [`session_worktree_commit`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 成功后调 [`_write_commit_persisted_marker`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 写 `.runtime/locks/commit_persisted_<sid>.json`（含 commit_hash + timestamp，原子写入）；[`session_worktree_merge`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 成功后 / [`session_worktree_abort`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 后调 [`_clear_commit_persisted_marker`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 清标记。**Phase 2** [`_sweep_one_dir`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) 判据5——24h 内的持久性标记 → sweep 免疫（跳过，不删除 worktree + 分支）；超龄（>24h）→ 允许清理（可能 session 崩溃后遗留）。**Phase 3** [`session_worktree_merge`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) merge 前验证 commit 持久性——读取标记中的 commit_hash，验证仍存在于 session 分支 tip，不匹配则 fail-closed 返回 `SCHRODINGER_ROLLBACK_DETECTED`（commit 被 sweep 或并发 session 删除）。**Phase 4** [`session_worktree_start`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) fail-closed 阻断有真实代码残留的 start——100% AI 场景下 warn 无效（AI 忽略 warning 直接启动），必须 fail-closed 强制 AI 先处理残留；新增 `allow_workspace_drift: bool = False` 逃生通道参数（对标 `force=True` 语义）。**测试**：[`test_session_worktree_workspace_clean.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree_workspace_clean.py) 3 个 start 测试改为 fail-closed 断言 + [`test_session_worktree.py`](file:///d:/ZephyrAlpha/tests/governance/rule_bridge/test_session_worktree.py) 3 个 merge 测试加 start stub（101/101 PASS）。**逃生通道**：`session_worktree_merge(force=True)` **不可绕过** commit 持久性验证 + base freshness check（#ARCH-FORCE-MERGE-SAFETY-001 治本，2026-07-22：不可绕过类——无 post-merge 替代 + 跳过后不可挽回），仅跳过可绕过类检测（WORKSPACE-CLEAN-CHECK / PRE-MERGE-TOPO-CHECK / commit gate）；`session_worktree_start(allow_workspace_drift=True)` 跳过工作区残留 fail-closed。force=True 仍落审计（`_audit_force_merge_usage`）。**capability 反查**：已登记 `worktree_commit_persistence`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)）。**与现有裁定关系**：扩展 #ARCH-WORKTREE-BASE-FRESHNESS-001（TRAE-074，该裁定治本 base 新鲜度检测但未覆盖 commit 创建后如何保证不被删除——本裁定补）+ 扩展 #ARCH-WORKSPACE-DRIFT-SYSTEMIC-001（该裁定引入 WORKSPACE-CLEAN-CHECK 但 start 时 fail-open——本裁定将 start 改为 fail-closed）+ 遵循 #ARCH-PREVENTABILITY-LAYER-001（TRAE-068，100% AI 场景下 warn 无效必须 fail-closed）。
- **commit 前必须 claim_files 声明工作范围（搭便车防护前提，2026-06-30）**：AI session 通过 GitCommitGateway commit 前 MUST 先调 [`claim_files`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 声明本次修改的文件列表——held_files 阻断层（下条）依赖 claim_files 注册的文件归属数据，未 claim 的 session 无法被阻断层检测。CLI 封装 [`scripts/git_commit.py`](file:///d:/ZephyrAlpha/scripts/git_commit.py) 已内置 claim_files → commit → release_files 流程。
- **GitCommitGateway held_files 冲突阻断（搭便车治本，2026-06-30）**：[`commit()`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) 时 [`HeldOverlapGate`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/held_overlap_gate.py) 自动检测目标文件是否被其他**活跃** session 持有（通过 [`SessionRegistry.other_held_files`](file:///d:/ZephyrAlpha/src/zephyr/security/access_control/session_concurrency.py)），命中则返回 `HELD_OVERLAP_VIOLATION` 阻断（`--no-verify` 绕不过，在 gateway 内部非 pre-commit hook）。**逃生通道**：`commit(allow_overlap=True)` 或 CLI `--allow-overlap` 显式声明时放行，commit message 追加 `[GW:<sid>:overlap]` 标记供审计追踪。过期 session 的持有自动忽略（TTL=3600s + PID 存活检测）。约束真源见 [parallel_session_coordination_policy.md §3.2/§5.2](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md)。
- **GitCommitGateway 门禁注册制 CommitGateRegistry（架构债务 #AD-001 治本，2026-06-30）**：[`commit_gate_registry.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py) 把 `commit()` 方法体中硬编码的 `_check_*` 调用升级为声明式 registry——新增 pre-commit 门禁只需 `register(GateSpec)`，不改 `commit()` 方法体，消除多 session 频繁修改同一文件（git_commit_gateway.py 2500+ 行）的搭便车冲突源。设计参考 [`ReconciliationRegistry`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)（post-commit reconciler 注册表），纯 stdlib 解耦。gate 实现放 [`commit_gates/`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/) 子目录，每个 gate 一个文件 + `make_*_gate()` 工厂函数。**新 AI 添加门禁**：在 `commit_gates/` 下创建 `make_xxx_gate()` → 在 `GitCommitGateway.__init__` 中 `register`，禁止在 `commit()` 方法体硬编码 `_check_*` 调用。
- **GitCommitGateway DIRECTORY-CONTRACT gate（DCR-001~007 等效校验，--no-verify 补偿，2026-06-30 治本）**：[`make_directory_contract_gate`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/directory_contract_gate.py)（priority=30，在 CLAIM-REQUIRED(40)/HELD-OVERLAP(50) 之前执行）通过 subprocess 调用 [`check_directory_contract.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/check_directory_contract.py) 复用真源——DCR-001~007 校验逻辑唯一在 check_directory_contract.py，gateway 不复制检测代码（subprocess 复用真源模式）。**病根**：GitCommitGateway 用 `--no-verify` 绕过 pre-commit hook（GATE-DIRECTORY-CONTRACT），DCR-001~007 防御断层——新 AI 可在 gateway 路径创建违规文件（如根目录 .txt、docs/03_modules/.py）绕过目录契约。本 gate 在 gateway 内部注册制执行等效校验，`--no-verify` 绕不过。**fail-closed**：check_directory_contract.py 缺失/执行失败/超时（60s）时阻断 commit（防 checker 被删后静默放行）。文件数 >200 时改用 `--all-files` 全量扫描避免 WinError 206（Windows 命令行长度限制）。**reconciler 路径已覆盖**：`_commit_auto`（reconciler auto-commit 入口）通过 `gate_registry.get("DIRECTORY-CONTRACT")` 复用本 gate 的 GateSpec，调其 check 方法对 reconciler 提交的文件跑 DCR 等效校验（2026-06-30 红蓝对抗治本，见上方"reconciler auto-commit 统一入口"条目）。约束真源见 [directory_contract.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml)。
- **GitCommitGateway CREATE-GUARD 门禁（新建 .py 文件 creation_token 阻断，2026-06-30 治本）**：[`make_create_guard`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/create_guard.py)（priority=60，在 HELD-OVERLAP(50) 之后、CAPABILITY-OVERLAP(200) 之前执行）检测 staged 新增 .py 文件是否在 [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) 的 `creation_tokens` 字段登记。**病根（"造第二真源"根因）**：AI 新建 .py 文件时可能复制已有实现（违反 [trae_060 §2](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml) 唯一真源原则），现有缓解（GATE-SSOT module_path 冲突检测 + GATE-SSOT-SINGLESOURCE 文件名检测 + capability_overlap_gate warn-only）均在 commit 时检测，检测滞后于创建。本 gate 治本：强制 AI 在创建新 .py 文件前先在 `creation_tokens` 字段登记 token（声明创建意图 + 关联 capability），未登记则 commit 硬阻断——把检测点从"commit 时"前移到"创建前"。**files 参数过滤治本（2026-06-30）**：gateway 选择性提交（只提交 files_in_scope，其他 staged 文件 stash），create_guard 只检测 commit 文件中的新增 .py（通过 `os.path.relpath(f, project_root)` 过滤），不检测其他 session 的 staged WIP（防误判）。**tests/ 豁免**：测试文件不是能力真源（对标 capability_overlap_gate 设计），不要求登记 token。**fail-open（YAML 不可达）**：registry 缺失/解析失败时放行——registry 故障不应卡死 commit 工作流（对标 capability_overlap_gate 的 fail-open 设计）。**token 登记格式**：`- file: "<相对路径>"  token: "auto-xxx"  created_by: "session-xxx"  capability: "xxx"`（详见 [create_guard.py](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/create_guard.py) docstring）。约束真源见 [trae_060 §2 唯一真源与直接消费](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml)。**元问题3治本扩展（2026-06-30，AD-GOV-001 收敛约束技术强制）**：扩展检测范围——若 commit 包含 [`reconciliation_registry.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py)，用 AST 对比 staged 与 HEAD 版本的 `make_*_reconciler` 函数集，新增函数需在 def 前 5 行内添加 `# trae_060-reviewed: <审查结论>` 标记，否则硬阻断。**病根**：AD-GOV-001 约束"新增 reconciler 前 MUST 过 trae_060 §4 元问题审查"是君子协定，新 AI 可直接造新 reconciler 绕过审查。**递归陷阱规避**：若新增门禁强制此审查，门禁本身也是"新增"需过 §4 审查（无限递归）；治本是扩展已有 create_guard 检测范围，不新增门禁。**检测逻辑**：`commit_files_rel` 含 `src/zephyr/governance/audit/reconciliation_registry.py` 时触发 → `git show :path` 取 staged 源码 + `git show HEAD:path` 取 HEAD 源码 → `ast.parse` 提取 `make_*_reconciler` 函数集 → 新增函数（staged - HEAD）检查 def 前 5 行是否含 `trae_060-reviewed` 标记 → 无标记则阻断（detail 列出未标记函数名 + 修复指引）。**fail-open**：git show 失败/SyntaxError 时不阻断（避免误伤正常 commit，其他 gate 兜底语法检测）。**标记格式**：`# trae_060-reviewed: <审查结论>`（如 `# trae_060-reviewed: 该存在+可合并入GATE-X+治本`）。

- **GitCommitGateway ARCH-REFERENCE 门禁（#ARCH-NNN 悬空引用阻断，2026-07-01 治本）**：[`make_arch_reference_gate`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/arch_reference_gate.py)（priority=75，在 DANGLING-REFERENCE(70) 之后、CAPABILITY-OVERLAP(200) 之前执行）检测 staged 文件中新增的 `#ARCH-NNN` 引用是否在 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 中登记。**病根（编号铁律#6 代码强制）**：编号铁律#6"任何 #ARCH-XXX 引用必须在本注册表有对应条目，禁止 grep-and-claim 占位"原为文档约束（靠 AI 自觉查 registry），AI 不查就占位导致编号冲突（如 ARCH-027 误用冲突改 ARCH-028）。本 gate 治本：新 AI 不查 registry 就用未登记编号 → GitCommitGateway 硬阻断（exit=1）。**增量检测**：只检测 staged 文件中**新增的**引用（通过 `git show HEAD:<path>` 对比），不阻断历史悬空引用（防卡死工作流）。**fail-closed**：registry 缺失/git 异常时阻断（防门禁静默失效）。**tests/ 豁免**：测试文件不检测。**capability 反查**：已登记 `arch_reference_gate`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)）。新 AI 想做"#ARCH 编号引用检测/phantom arch id"前，CapabilityLookup 会反查阻止重复造轮子。**L1+L2 治本增强（2026-07-17）**：在原 ARCH-REFERENCE 基础上新增两层防护——**L1 编号空洞检测（ARCH_GAP_WARNING，不阻断）**：按域前缀分组（如 ARCH-CH-NNN / ARCH-MM-NNN）检测编号连续性，发现空洞（如 006/008 缺失）发 WARNING 提醒人工核查是否为已删除/合并条目；**L2 同提交原子性门禁（ARCH_ATOMICITY_VIOLATION，硬阻断）**：新引用不在 HEAD 版本 registry 时，要求 `architecture_issue_registry.yaml` 必须同 commit 提交，否则阻断——防止"引用了新编号但 registry 没同提交登记"导致 commit 后 HEAD registry 仍缺条目。L2 通过 `git rev-parse HEAD` 检查非 git 仓库（如测试 tmp_path）返回 None 跳过检测，避免误阻断。病根：原 ARCH-REFERENCE 只检测工作区 registry（commit 后新真源），但 HEAD registry 可能仍缺条目（AI 忘同 commit 登记），门禁自身读工作区版本能过但 HEAD 版本仍悬空。**正则多段式支持（2026-07-17 治本 ARCH-GOV-SHIM-001 漏检）**：正则 `#ARCH-([A-Z]+(?:-[A-Z]+)*-\d+|\d+)` 支持纯数字（`#ARCH-008`）、两段式域前缀（`#ARCH-CH-007`）、多段式域前缀（`#ARCH-GOV-SHIM-001`）——治本旧正则 `#ARCH-([A-Z]+-\d+|\d+)` 只匹配两段式导致三段式编号 `#ARCH-GOV-SHIM-001` 漏检可绕过门禁。**正则描述性 ID 支持（2026-08-05 治本 gate 正则盲区）**：正则升级为 `#ARCH-(\d+|[A-Z][A-Z0-9-]*[A-Z0-9])`，新增支持描述性 ID（无数字后缀，如 `#ARCH-DOC-REF-FILE-URL` / `#ARCH-IFIND-FAILOVER`）——治本旧正则要求末尾 `\d+` 数字导致全项目 67 个描述性 ARCH 引用 0% 被检出，逃逸门禁。**模板占位符过滤（2026-08-05）**：[`_is_template_ref`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/arch_reference_gate.py) 过滤 `#ARCH-NNN` / `#ARCH-XXX` / `#ARCH-CH-NNN` 等格式描述文本，新正则支持描述性 ID 后这些占位符需显式过滤防误报阻断合法 commit。**L3 新条目数字制检测（ARCH_NON_NUMERIC_WARNING，不阻断，2026-08-05 铁律#7 冻结条款）**：[`_is_numeric_suffix`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/arch_reference_gate.py) 判定 ARCH ID 末段是否为纯数字（数字制 = 末段 `isdigit()`，如 `008`/`CH-007`/`GOV-SHIM-001` → True；`DOC-REF-FILE-URL`/`EDB-EXPAND` → False）。L3 只在 `architecture_issue_registry.yaml` 在本次 commit 中时触发，对比工作区 registry 与 HEAD registry 的差集（`registered_nums - head_nums`），新增条目末段非数字 → WARNING 提醒改为数字制（如 `ARCH-EDB-EXPAND → ARCH-EDB-001`，示例非真实引用），不阻断 commit。**描述性 ID 历史遗留说明（2026-08-05 裁定，方案 C 冻结+渐进迁移）**：2026-08-05 前已登记的描述性 ARCH ID（无数字后缀，如 `#ARCH-DOC-REF-FILE-URL` / `#ARCH-EDB-EXPAND` / `#ARCH-IFIND-FAILOVER`）冻结保留，不强制迁移——因全项目有 67 处描述性引用分布在数十个文件中，一次性迁移成本高且易出错，改为在代码自然修改时逐步迁移为数字制。2026-08-05 起新登记 ARCH 条目强制使用数字制（issue_id 末段必须为纯数字），L3 检测（WARNING）强制执行此规则。存量描述性 ID 仍受 ARCH-REFERENCE L0 悬空引用检测保护（已登记即合法），L3 不对存量条目报 WARNING（只检测 `registered_nums - head_nums` 差集中的新增条目）。

- **GitCommitGateway NO-IMPORT-SIDE-EFFECT 门禁（S4-C 模块导入零副作用原则，2026-07-17 治本）**：[`make_no_import_side_effect_gate`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/no_import_side_effect_gate.py)（priority=103，在 TEST-SOURCE-CONSISTENCY(102) 之后执行）检测 staged src/ .py 文件**added 行**中的模块级副作用——违反"模块导入零副作用原则"（import 一个模块不应触发 I/O、网络、子进程、DB 连接或急切实例化）。**病根（S4-A 审计发现）**：`telemetry.py` 模块级 `TELEMETRY = InventorySelfMetrics()` 急切实例化（import 即创建单例）+ `rollback/__init__.py` 急切 `from . import (37 子模块)` 含 3 个 deprecated 子模块。S4-A 已修复（TELEMETRY 改 PEP 562 惰性 `__getattr__` + 移除废弃子模块急切导入）。本 gate 防止新 AI 制造同类债务。**检测两类**：① I/O/网络/subprocess/DB 调用（`open`/`urlopen`/`subprocess.run`/`requests.get`/`socket.socket`/`duckdb.connect`/`psycopg2.connect`/`sqlite3.connect` + `Path(...).read_text/write_text/unlink/...` 方法调用）；② 急切单例实例化（UPPER_SNAKE 目标 = Capitalized 调用，如 `TELEMETRY = InventorySelfMetrics()`；allowlist 纯构造 `TypeVar`/`NamedTuple`/`TypedDict`/`Enum`/`Path`）。**豁免**：tests/（`is_test_exempt`）+ `__main__.py`（入口点）+ `if __name__ == "__main__":` guard 块（import 时不触发）+ FunctionDef/ClassDef 体（非模块级）。**added-lines-only**：只检测新增行（grandfather 存量 2288 文件，对标 TEST-SOURCE-CONSISTENCY 只防新增策略）。**fail-open**：AST/git 异常放行（`logger.warning`）。**capability 反查**：已登记 `no_import_side_effect_gate`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)）。**测试**：[`test_no_import_side_effect_gate.py`](file:///d:/ZephyrAlpha/tests/governance/commit_gates/test_no_import_side_effect_gate.py)（74 单测，覆盖 gate 字段/AST 纯函数检测/`_check_file` 模块级检测/mock gateway 集成）。

- **5.96 维度防御门禁 GATE-DEBT-BRIDGE（架构债务防复发，R67 引入 2026-07-06，R68 三阶段全部落地 2026-07-06）**：[`scan_debt.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/scan_debt.py) 是 pre-commit hook（`.pre-commit-config.yaml` gate-debt-bridge，**阶段2 已转硬阻断——commit 时自动检测**）+ CI 全量扫描（`.github/workflows/governance.yml` Tier 5），检测 3 类 AI 易复发的代码异味（5.96 维度病根）。**3 条硬规则（违反即视为新债，需登记 architecture_issue_registry.yaml（#ARCH-XXX）后修复；commit 阶段 + CI 双重 hard block）**：
  - **DEBT-1 dataclass 布尔字段冗余**：`@dataclass` 含 `action: str`（或 `role`/`kind`/`type`/`category`）字段 + ≥2 个派生布尔字段（`should_*`/`is_*`/`has_*`/`can_*`/`allow_*`/`do_*` 或 `*_allowed`/`*_enabled`/`*_required`）→ MUST 改为 Enum + `@property` 派生（5.96.2 病根：TriggerDecision 原 `action: str` + `should_rollback: bool` + `retry_allowed: bool` + `forward_fix_allowed: bool` 三布尔完全由 action 决定，互斥动作的布尔组合可能不一致，R67 已修复为 ActionType enum + @property）。
  - **DEBT-2 函数布尔参数蔓延**：函数（含方法）含 ≥3 个 `bool` 位置参数（不含 `self`/`cls`，不含 keyword-only 参数）→ MUST 改为 `dict[str, bool]` 或 keyword-only 参数（5.96.3 病根：`_calculate_trust(git_ok, test_ok, audit_ok)` 三布尔参数顺序易传错，R67 已修复为 `_calculate_trust(checks: dict[str, bool])`）。**R68 修订**：[`scan_debt.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/scan_debt.py) `_check_function_args` 只检测位置参数（`posonlyargs + args`），不检测 `kwonlyargs`——keyword-only 已用 `*` 隔离，调用方必须写 `name=value`，不会传错顺序，不算蔓延。R68 据此修订后 13 处违规降到 7 处（hallucination_detector.should_trigger 等 6 处已 keyword-only 的不算违规），7 处位置参数违规已修复为 keyword-only。
  - **DEBT-3 class action+bool 共存**：任意 `class`（不限 `@dataclass`）含 `action: str` + `should_*`/`*_allowed: bool` 字段 → 同 DEBT-1 治本方案。
  **检测机制**：[`scan_debt.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/scan_debt.py) 纯 stdlib AST 扫描（不依赖 ruff/mypy 是否安装），3 段检测：① `_is_action_field` + `_is_bool_flag_field` 识别字段语义 ② `DebtScanner.visit_ClassDef` 检测 DEBT-1/3 ③ `DebtScanner._check_function_args` 检测 DEBT-2（R68 修订：只检测位置参数，kwonlyargs 豁免）。误报优先（宁可放过不可误伤 commit）。**阶段1（R67 完成 2026-07-06）**：`stages: [manual]` 不阻断常规 commit，手动 `pre-commit run gate-debt-bridge` 触发——R67 基线 DEBT-2=13（hallucination_detector.py:445 should_trigger 6 个 bool 等），强制阻断会卡死工作流。**阶段2（R68 完成 2026-07-06）**：存量违规清零（DEBT-2: 13→0，6 处已 keyword-only 豁免 + 7 处位置参数改 keyword-only），移除 `stages: [manual]`，commit 时自动阻断新增违规（hard block）。**阶段3（R68 完成 2026-07-06）**：CI 集成——[`.github/workflows/governance.yml`](file:///d:/ZephyrAlpha/.github/workflows/governance.yml) Tier 5 代码质量层新增 `Architecture Debt Scan (GATE-DEBT-BRIDGE)` step，`scan_debt.py --src src/zephyr --ci` 全量扫描，`continue-on-error: false` 硬阻断 push/PR。客户端 commit 漏过的违规 → CI 服务端最后防线拦截（对标 RULE-SEVEN 五层强制集成架构 Layer 5）。**使用**：`python scripts/governance/d7_code/scan_debt.py --src src/zephyr`（warn-only）/ `--ci`（hard block）。pre-commit 用 `--staged` 变更检测只扫 staged .py（5.1s→亚秒），CI 全量用 `--ci` 无 `--staged`。**R68 验证基线**：DEBT-1=0 / DEBT-2=0 / DEBT-3=0——存量违规清零，门闸进入 commit + CI 双重硬阻断模式。**capability 反查**：已登记 `architecture_debt_scanner`（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)，token=auto-scan-debt-20260706），新 AI 想做"代码异味检测/bool 参数扫描/dataclass 冗余"前 CapabilityLookup 会反查阻止重复造轮子。

- **UNSAFE-DICT-SPREAD 门禁（``**data`` 直接展开防复发，warn-only，R69 引入 2026-07-06）**：[`make_unsafe_dict_spread_gate`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/unsafe_dict_spread_gate.py)（priority=66，在 ssot_redefinition(65) 之后、dangling_reference(70) 之前，与 SSoT 符号检测同组）检测 staged .py 文件**新增行**中的 ``SomeClass(**varname)`` 直接展开模式。**病根（5.147.5 / 5.147.12 同族债务）**：``data`` 来自 ``json.loads`` / ``yaml.safe_load`` / DB row 时，schema 演进（字段新增/删除/重命名）会触发 ``TypeError``；Pydantic ``BASE_CONFIG`` 含 ``extra="forbid"`` 同样硬拒未知字段。5.147.12 已用 SSoT ``filter_dataclass_fields(cls, data)`` 修复 13 处存量债务，但新 AI 写新功能时若不自觉仍会制造同类债务 → 本 gate 持续盯防复发。**豁免清单**：① ``**kwargs`` / ``**kwds``（显式关键字参数透传，合法）② ``**filter_dataclass_fields(...)`` / ``**func(...)``（函数调用，正则不匹配——``**`` 后跟 ``(`` 非 ``)``）③ ``**{...}``（字典字面量，正则不匹配——``**`` 后跟 ``{`` 非 ``\w``）④ ``tests/`` 目录豁免 ⑤ import / 注释行豁免 ⑥ docstring 行豁免（多行 ``"""..."""`` 跟踪，避免 gate 自身 docstring 示例触发误报）。**warn 级不阻断**（passed 始终 True）：命中时 stderr + ``logger.warning`` 输出告警，detail 含违规文件:行号 + 修复指引（``filter_dataclass_fields(Cls, data)``），AI/人工 reviewer 判断是否需修复。**为什么 warn 不 block**：``dict(**a)`` / ``OrderedDict(**a)`` 等内置容器构造是合法的；``**kwargs`` 透传场景无法静态判断目标类是否 dataclass/Pydantic，误报阻断会卡死正常开发。**fail-open**：git diff 异常/YAML 不可达时放行（``logger.warning`` 记录检测器失效，不阻断 commit）。**capability 反查**：已登记 ``unsafe_dict_spread_gate``（[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)，token=auto-unsafe-dict-spread-gate-20260706），新 AI 想做"``**data`` 展开检测/schema 演进 TypeError 防护"前 CapabilityLookup 会反查阻止重复造轮子。**测试**：[`test_unsafe_dict_spread_gate.py`](file:///d:/ZephyrAlpha/tests/governance/commit_gates/test_unsafe_dict_spread_gate.py)（38 单测，覆盖 16 测试组：gate 字段/warn 命中/不阻断/kwargs 豁免/filter_dataclass_fields 豁免/字典字面量豁免/函数调用豁免/import 豁免/注释豁免/docstring 豁免含多行/tests 豁免/非 .py 豁免/空 staged/fail-open/多违规全报告/混合安全危险）。

- **5.145 维度防御门禁 GATE-ANY-ABUSE（类型注解 Any 滥用防复发，R70 引入 2026-07-06，#ARCH-ANY-GOVERNANCE-001 Phase 3 升级为 commit 阻断 2026-07-22）**：[`check_any_abuse.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_any_abuse.py) 是 pre-commit hook（`.pre-commit-config.yaml` gate-any-abuse，**Phase 3 commit 阻断——src/zephyr/*.py 变更时自动触发**），检测函数签名中的"裸 Any 滥用"——AI 偷懒写法的典型模式（5.145 维度病根）。**2 条检测规则**：
  - **ANY-1 参数裸 Any**：函数参数类型为裸 `Any`（非 `dict[str, Any]` 等容器型）→ MUST 替换为具体类型或 `Protocol`（5.145.10/11 病根：`detect_side_channel(timing_data: Any)` / `audit_logger: Any` 等，AI 偷懒不写具体类型 → 调用方无类型保障 → IDE/mypy 失去静态分析能力；R70 已修复 l6_observability.py + trigger_router.py + risk_validator_protocol.py，引入 `AuditLoggerProtocol` + `RiskLimits` SSoT 类型；Phase 2 commit `e494c72623` 清零 src/zephyr/ 全量 71 处裸 Any）。
  - **ANY-2 返回值裸 Any**：函数返回值类型为裸 `Any`（同上）→ MUST 替换为具体类型（`dict[str, Any]` 等容器型豁免——配置字典是合理用法）。
  **豁免规则（合理用法不报）**：① `dict[str, Any]` / `list[Any]` / `tuple[Any, ...]` 等容器型 Any ② `Callable[..., Any]`（回调返回值多变，合理）③ `TYPE_CHECKING` 块内的 Any（仅类型检查上下文）④ `**kwargs: Any` / `*args: Any`（兼容旧 API）⑤ dunder 方法（`__init__` 等无返回值注解不报）⑥ `.pyi` stub 文件 ⑦ **`# noqa: any-abuse  any-abuse豁免: <理由>` 行级标记（Phase 3：合理 Any 逃生通道，理由≥10字符，登记于 [`noqa_exempt_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml)）**——用于动态 Plugin 接口边界 / `runtime_checkable Protocol` 异构实现集 / 第三方 API 边界 / 桥接 API（同方法 isinstance 分派）/ 测试 fixture mock 注入点。**检测机制**：[`check_any_abuse.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/check_any_abuse.py) 纯 stdlib AST + 正则扫描（不依赖 ruff/mypy 是否安装），`_is_bare_any` 区分裸 Any vs 容器型 Any，`_scan_function` 扫描参数+返回值，`_collect_noqa_any_abuse_lines` 收集行级豁免标记并过滤违规。误报优先（宁可放过不可误伤 commit）。**阶段1（R70 完成 2026-07-06）**：`stages: [manual]` 不阻断常规 commit——R70 基线 ANY-1=462 / ANY-2=172 / 总计 634（5.145 维度存量债务），强制阻断会卡死工作流。**阶段2（#ARCH-ANY-GOVERNANCE-001 Phase 2 完成 2026-07-22，commit `e494c72623`）**：存量 634→0 清零（src/zephyr/ 全量扫描 0 处裸 Any，[`any_type_inferrer.py`](file:///d:/ZephyrAlpha/scripts/governance/d7_code/any_type_inferrer.py) 推断工具辅助）。**阶段3（#ARCH-ANY-GOVERNANCE-001 Phase 3 完成 2026-07-22）**：移除 `stages:[manual]` → commit 时自动阻断新增违规（hard block exit 1），新增 `# noqa: any-abuse` 行级豁免机制（合理 Any 可逃生，需附理由≥10字符）。**配套措施**：[`pyproject.toml`](file:///d:/ZephyrAlpha/pyproject.toml) mypy 配置加严（`disallow_any_generics = true` + `warn_any_explicit = true`，R70 引入）——IDE/mypy 运行时显式 Any 使用告警，配合 AST 门禁形成双重防线。**使用**：`python scripts/governance/d7_code/check_any_abuse.py --src src/zephyr`（warn-only）/ `--ci`（hard block）/ 传文件列表增量扫描。pre-commit 用 `--staged` 变更检测只扫 staged .py（3.8s→亚秒），CI 全量用 `--ci` 无 `--staged`。**修复指引**：裸 `Any` → 具体类型（如 `dict[str, float]`）/ `Protocol`（duck-typed 接口，对标 `AuditLoggerProtocol`）/ `TYPE_CHECKING` 导入（避免循环依赖）/ `# noqa: any-abuse  any-abuse豁免: <理由>`（合理 Any 逃生）。**战略裁定1**：新发现 Any 违规转化为 AST 门禁检测项，不再加规则文档——治本是自动化门禁，不是更多文档。

### 8.1 蓝图/模块删除价值判定（RULE-THREE + ARCH-027 + RULE-TWELVE）

> **新AI必读**：当你发现一个模块/蓝图"零消费者"或"看起来没用"时，**禁止直接删除**。必须按以下二元判定标准逐项审判。

**核心铁律**：零消费者 ≠ 无价值

- 真源：[ARCH-027 价值判定原则](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_017_arch_governance_order.yaml) + [RULE-THREE 删除前置确认](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) + [RULE-TWELVE 项目瘦身](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_052_cross_blueprint_change_cleanup.yaml)
- 禁止：仅凭"零消费者"判定删除（误删有价值的安全/治理组件）

**判定决策树**（按序执行，任一YES即保留）：

```
发现零消费者/疑似无价值模块时：
│
├─ STEP 0: 功能价值判定（ARCH-027 三维度，ANY为YES→保留并接通，不进入删除流程）
│   ├─ 3a 独立功能价值：该模块是否提供其他模块无法替代的独立功能？
│   │   YES → 保留，接通消费者管线（接入系统）
│   ├─ 3b 客观原因：零消费者是否有客观原因？
│   │   （管线未接通 / C轨业务层未施工 [ARCH-045 P0 已解除占位禁令，C轨blocked 历史状态退役] / 前置依赖未就绪 / 暂缓施工Suspended）
│   │   YES → 保留，待管线就绪后自然产生消费者
│   └─ 3c 重建成本：删除后若需要重建，成本是否高昂？
│       YES → 保留，重建成本高于维护成本
│
│   └─ ALL NO（三维度均为NO）→ 进入 RULE-THREE 三步审判
│
├─ RULE-THREE STEP 1: 登记检查
│   该文件在 manifest/registry/__init__.py 中被引用？
│   YES → 有价值，不能删
│
├─ RULE-THREE STEP 2: 重复检查
│   有另一个文件与它内容完全相同且已注册？
│   YES → 真正重复，可删
│
└─ RULE-THREE STEP 3: 逐行价值检查
    逐行检查代码/设计内容是否无价值？
    确认无价值 → 删除
│
└─ 删除后验证三步（RULE-TWELVE 强制）：
    1. audit_registration.py exit 0
    2. generate_project_path_tree.py --write
    3. generate_project_depgraph.py --max-workers 8
```

**执行器**：[`pre_delete_safety_check.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/pre_delete_safety_check.py)（5项机械检查：.py消费者 / .yaml消费者 / 注册表登记 / 重复内容 / 高价值标记，exit 0=SAFE 允许删除 / exit 1=BLOCKED 禁止删除）

```bash
# 删除前必须先跑执行器（--dry-run 不修改任何文件）
python scripts/governance/d5_architecture/pre_delete_safety_check.py <file_path> --dry-run
```

**P0模块特殊约束**（[trae_032 §MLC-003](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_032_module_lifecycle.yaml)）：P0模块禁止退役——必须先完成P1+等效替代并active≥30天。

## 9. 新模块接入规则

创建新模块时，必须：
0. **查 CapabilityLookup 确认能力是否已存在**（防止重复造轮子）：
   ```python
   from zephyr.governance.capability_lookup import CapabilityLookup
   reg = CapabilityLookup()              # 自动扫磁盘+派生 canonical
   hits = reg.find("rollback")            # 关键词搜（匹配 capability_id/aliases/description/canonical_file）
   hits = reg.find("session handoff")     # 多词短语也支持（token AND 匹配，词无需连续出现）
   cap = reg.get("rollback_executor")     # 按 capability_id 精确查
   reg.check_file_canonical("src/zephyr/xxx.py")  # 反查某文件是哪个能力的 canonical
   ```
   真源：[`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)（能力索引，仅声明 capability_id/aliases/description；canonical_file/duplicates/removed_duplicates 全部由 CapabilityLookup 从磁盘头部+git log 自动派生）。已存在的能力 → 扩展现有 canonical 文件，禁止新建重复实现。
   **aliases 只放英文标识符**（函数名/常量，如 `REPO_ROOT`/`load_blueprint_path`）；中文变体由 `find()` 的 token 包含匹配（CJK ≥3 字符公共子串）自然处理，**禁止在 YAML 堆中文同义词 alias**（反模式，见注册表顶部 alias 策略）。

   **commit 时自动检测能力重复**（事件驱动兜底，治本 2b）：即使 AI 忘记执行上方手动查重，GitCommitGateway 在 commit 时会自动调用 [`check_capability_duplicates`](file:///d:/ZephyrAlpha/src/zephyr/governance/capability_lookup.py) 检测新增 `.py` 文件是否参与"同能力多实现"：
   - 新文件 basename 撞已有 capability_id/alias（registry 派生标为 duplicate）→ commit 被 BLOCK，修复指令见报错信息。
   - L3 pre-commit hook（[`check_ssot_gate.py`](file:///d:/ZephyrAlpha/scripts/governance/check_ssot_gate.py)）作为双保险，绕过 gateway 直接 `git commit` 时同样阻断。
   - 检测逻辑唯一真源：`capability_lookup.check_capability_duplicates`（L2/L3 共用，避免两份实现漂移）。
1. 构造 CapabilityCard 并注册到 CapabilityRegistry
2. 在 `data/capability_cards/` 下创建对应的 YAML
3. 如果有自动化工作，创建 WorkDAG 并注册到 WorkOrchestrator
4. 写入 AiAuditLogger 记录注册事件

如果不注册，ModuleOnboardingScanner 会在扫描时发现并自动触发接入流程。

## 10. Git 命令封装约定（绕过 Trae 批准弹窗）

> **根因**：Trae 对 `git` 前缀命令有硬编码安全审查，settings.json 的 allowList/alwaysRun 对 git 无效，但对 `python` 前缀有效。直接用 `git xxx` 会弹出批准框，打断 AI 连续工作。

**强制规则**：所有 git 命令 MUST 通过 `python scripts/git_guard.py` 封装执行，禁止直接用 `git` 前缀。

| 场景 | ❌ 禁止（会弹窗） | ✅ 必须（不弹窗） |
|------|------|------|
| 暂存 | `git add <file>` | `python scripts/git_guard.py add <file>` |
| 提交 | `git commit -m "..."` | `python scripts/git_guard.py commit -m "..."` |
| 提交(文件) | `git commit -F <file>` | `python scripts/git_guard.py commit -F <file>` |
| 状态 | `git status` | `python scripts/git_guard.py status` |
| 日志 | `git log --oneline -5` | `python scripts/git_guard.py log --oneline -5` |
| 差异 | `git diff` | `python scripts/git_guard.py diff` |
| 推送 | `git push` | `python scripts/git_guard.py push` |
| 拉取 | `git pull` | `python scripts/git_guard.py pull` |

**复合命令**：禁止用 `;` 或 `&&` 串联多个 git 命令（RULE-SEVENTEEN），分多次 RunCommand 执行。

**git_guard.py 行为**：
- 非危险命令（add/commit/status/log/diff/push/pull 等）→ 直接透传给 git（[`git_guard.py`](file:///d:/ZephyrAlpha/scripts/git_guard.py) 的 `DANGEROUS_SUBCOMMANDS` 集合判定，不在集合内即 `_passthrough`）
- 危险命令（reset --hard/checkout/stash/revert/restore/mv）→ 检查 `.ailocks/` 锁冲突后透传

**示例**：用户要求 `git add src/x.py; git commit -F _tmp.txt --no-verify` 时，AI 应分两次执行：
1. `python scripts/git_guard.py add src/x.py`
2. `python scripts/git_guard.py commit -F _tmp.txt --no-verify`

### 10.0 改完立即入队铁律（66 号 v1.0.0，2026-08-12）

> **来源**：[66_commit_queue_serialization](docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/66_commit_queue_serialization.md) §4 裁定 6——用户已确认。
> **背景**：2026-08-12 23 会话并发事故证明"改完统一 add"在多会话 stash 周期下不保险（dangling blob 恢复实战）。队列方案落地后，会话提交 = 快照入队即返回，add 只是暂存保护、入队才是内容落袋。

**铁律**：AI 每完成一个文件的编辑（Edit/Write），**立即**将该文件入队（enqueue）到提交队列。不等"一批改完再统一入队"——多会话并发下，未入队的修改随时可能被其他会话的 stash/restore/read-tree 抹掉。

**过渡期纪律**（队列 MVP 落地前）：改完立即 `python scripts/git_guard.py add <file>`（staged 文件 git clean 不删，提供第一层保护）。队列 MVP 落地后，改完立即 `python scripts/commit_queue.py enqueue --session <sid> --files <file> --message <msg>`（快照落袋，工作区后续被冲无损）。

**禁止**：
- 禁止"一批改完再统一 add"——多会话下等价于裸奔（8-12 实证 6 文件被冲 2 次）
- 禁止全区恢复命令（`git restore .`/`git checkout -- .`/`git clean`/`git reset --hard`/`git stash`）——会清空其他会话未入队的修改

### 10.0.1 plumbing 命令禁止（66 号 v1.0.0 §4 裁定 7）

> **来源**：66 号 §4 裁定 7——事故 6（`git read-tree HEAD` 隐形重置共享 index）根因。

**铁律**：AI 禁止直接执行以下 git plumbing 命令（会操纵共享 index/对象库，绕过所有门禁）：
- `git read-tree` — 重置 index 到指定树（事故 6 根因，清空所有 staged 元数据）
- `git update-index` — 直接修改 index 条目
- `git write-tree` — 从 index 生成树对象
- `git hash-object` — 直接写入对象库

**例外**：Serializer 专用 worktree 内通过 `ZEPHYR_SERIALIZER_MODE=1` 环境变量白名单放行（66 号 §6.3）。

**注**：`git commit-tree`/`git update-ref` 不在此列——由 REFERENCE-TRANSACTION-GUARD（§10.1.1）专管，且 emergency_commit.py 合法使用 commit-tree 需保留通道。

### 10.1 POST-COMMIT-GUARD：--no-verify 的 post-commit 层闭环（#ARCH-050）

**病根**：`--no-verify` 绕过 pre-commit hook，导致 GitCommitGateway 的 in-process gates + pre-commit 检查全部被绕过，产生 non-GW commit（commit message 无 `[GW:` 标记）。`commit_gw_audit` reconciler 事后审计为 warn-only，不阻断，无法有效约束并发 AI 对话。

**治本**（2026-07-08 强化 session_id 真实性验证）：`--no-verify` 绕过 pre-commit，**但不绕过 post-commit**。在 post-commit 中执行两层验证：
1. **标记存在性**：commit message 是否含 `[GW:` 标记，不含且非 merge commit → 自动 `git reset --soft HEAD~1`（保留修改在 staging area），强制所有 commit 必须通过 GitCommitGateway。
2. **session_id 真实性**（强化）：解析 `[GW:{session_id}...]` 中的 session_id（要求 `sess-` 前缀，避免匹配描述文本误含的片段），验证其在 `.runtime/session_registry.json` 中已注册。未注册 → 伪造检测 → `git reset --soft HEAD~1`。**fail-open**：注册表不存在/解析失败 → 放行（不阻断正常流程）。

这闭环了"伪造 `[GW:fake-session]` 标记"的残余风险——只有真正的 GitCommitGateway/session_worktree_commit（产生真实 session_id 并注册到 SessionRegistry）的 commit 才被放行。

**生效条件**：`.git/hooks/post-commit` 调用 [`scripts/governance/git_hooks/post_commit_guard.sh`](file:///d:/ZephyrAlpha/scripts/governance/git_hooks/post_commit_guard.sh)。源文件被 git-tracked，hook 安装见脚本头部注释。

**合法标识**（4 种 GW 标记均放行）：
- `[GW:{session_id}]` — GitCommitGateway 常规 commit（[`git_commit_gateway.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py) `_GW_MARKER_FMT` 常量）
- `[GW:{session_id}:auto]` — GitCommitGateway auto-commit
- `[GW:{session_id}:worktree]` — `session_worktree_commit`
- `[GW:{session_id}:merge]` — `session_worktree_merge`

**豁免**：merge commit（subject 以 `merge ` 开头，大小写不敏感）。

**违规处置**：non-GW commit 被自动 `git reset --soft HEAD~1`，修改保留在 staging area。审计报告落盘 `.runtime/reconcile_reports/post_commit_guard_<timestamp>.json`。AI 应通过 GitCommitGateway 重新提交。

### 10.1.1 REFERENCE-TRANSACTION-GUARD：git commit-tree plumbing 绕过堵漏（Phase 4 治本，2026-07-19）

**病根（第一性原理）**：git 分两层——porcelain 命令（`git commit`/`git merge`/`git reset`）触发 hook；plumbing 命令（`git commit-tree`+`git update-ref`+`git write-tree`）**不触发任何 hook**。POST-COMMIT-GUARD 在 `post-commit` hook 中运行，能拦截 `git commit --no-verify`（`--no-verify` 跳 pre-commit，不跳 post-commit），但**完全无法拦截** `git commit-tree` + `git update-ref` 组合——这俩 plumbing 命令不触发任何 hook，POST-COMMIT-GUARD 永远不会运行。P2-1 落地的 `emergency_commit` 用 `commit-tree` 实现合法逃生通道，但同样路径可被 AI 用于绕过所有治理。

**治本**：`reference-transaction` 是 git 2.45+ 的 hook，在 ref 事务提交时触发：
- `prepared` 状态：事务即将提交，exit non-zero 回滚整个事务
- `committed` 状态：事务已提交（informational only）

本 hook 在 `prepared` 状态检查 `refs/heads/dev` 的 forward 更新：
1. 跳过 reset/rewind（old 不是 new 的祖先，如 POST-COMMIT-GUARD 的 `git reset --soft HEAD~1` 走这条路径）
2. 跳过 deletion/creation（OID 含全零）
3. 跳过 merge commit（2+ parents，已被 merge gate 校验）
4. 跳过含 `[GW:` 标记的 commit（GitCommitGateway / `session_worktree_commit` / `session_worktree_merge` / `emergency_commit` 的合法标识）
5. 其余 → **block**（exit 1，事务回滚，ref 不变）

**生效条件**：`.git/hooks/reference-transaction` 调用 [`scripts/governance/git_hooks/reference_transaction_guard.sh`](file:///d:/ZephyrAlpha/scripts/governance/git_hooks/reference_transaction_guard.sh)。源文件被 git-tracked，hook 安装见脚本头部注释。兼容性要求 git 2.45+（当前实测 git 2.48.1.windows.1）。

**合法标识**（5 种 GW 标记均放行，与 POST-COMMIT-GUARD 一致 + 新增 emergency）：
- `[GW:{session_id}]` — GitCommitGateway 常规 commit
- `[GW:{session_id}:auto]` — GitCommitGateway auto-commit
- `[GW:{session_id}:worktree]` — `session_worktree_commit`
- `[GW:{session_id}:merge]` — `session_worktree_merge`
- `[GW:{session_id}:emergency]` — `emergency_commit`（P2-1 落地，合法 commit-tree 逃生通道）

**豁免**（不含 [GW: 但放行）：
- merge commit（2+ parents）
- reset/rewind（backward ref 移动，POST-COMMIT-GUARD 的 reset 走这条路径）

**违规处置**：plumbing 绕过被 block，ref 不变（事务回滚）。审计报告落盘 `.runtime/reconcile_reports/reference_transaction_guard_<timestamp>.json`。AI 应通过 GitCommitGateway / `session_worktree_commit` / `emergency_commit` 重新提交。

**调试**：`REF_TX_GUARD_DEBUG=1` 环境变量启用调用日志（写 `.runtime/ref_tx_guard_debug.log`），用于排查 hook 是否被 git 调用。

**测试覆盖**（6 用例）：non-GW forward block / GW forward allow / merge allow / reset allow / session branch allow / committed state allow。真实环境验证：`git commit-tree` + `git update-ref` bypass 被 block（exit 128），`emergency_commit` 仍正常工作。

### 10.1.2 emergency commit 路径规范（2026-07-20，B1b 审计治本）

**铁律**：任何 `[GW:*:emergency]` 标记的 commit MUST 经 [`emergency_commit.py`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py) 生成。禁止手写 `[GW:*:emergency]` 标记走裸 `git commit` 或其他未设 `ZEPHYR_COMMIT_GATEWAY=1` 的路径——此类 commit 会被 POST-COMMIT-GUARD 判定为 forged_gw_marker 并 `git reset --soft HEAD~1`（B1b 审计实证：sess-27964-p0-emergency 两次被 reset）。

**为什么**：`emergency_commit.py` 用 `git commit-tree` plumbing 原子化提交并落审计（reconcile_execution_log + reconcile_reports），是唯一同时满足「绕过失效锁」与「治理可见性」的通道。手写标记的非标路径既触发 guard 回滚，又污染 forged_gw_marker 监控信号（伪造与误报不可区分=监控失效）。

**emergency session id**：`sess-em-*` / `sess-*-emergency` 不注册 SessionRegistry（emergency 前提是注册表/锁不可用），其 commit 合法性由审计落盘与 reference-transaction guard 的 `[GW:` 标记豁免共同保证。

### 10.2 代码内部 subprocess 调用与文件删除弹窗规避（Trae Shell Interception，2026-07-19）

**根因**：Trae 对 `git checkout` / `Remove-Item` 等高危命令有独立的 **Shell Interception 二次拦截层**，**不受「始终自动运行」设置控制**（官方博客 [Making AI Coding Safer](https://www.trae.ai/blog/engineering_thought_0108) 明确说明这是独立于沙箱/自动运行之外的安全网）。项目代码内部的 `subprocess.run(["git", "checkout", ...])` 和 AI 直接执行的 `Remove-Item` 都会触发弹窗，打断 AI 连续工作。改用语义等价但不被拦截的命令可消除弹窗。

**规则 1：代码内部 subprocess 调用禁止用 `git checkout`，MUST 用 `git restore`**

| 场景 | ❌ 禁止（Trae 二次拦截弹窗） | ✅ 必须（不弹窗，语义等价） | 保护层 |
|------|------|------|------|
| 丢弃工作区修改 | `git checkout -- <file>` | `git restore -- <file>` | `git_guard.py` 已支持 `restore` 拦截（DANGEROUS_SUBCOMMANDS 含 restore） |
| 从 stash/commit 恢复文件 | `git checkout <ref> -- <file>` | `git restore --source <ref> -- <file>` | 同上 |

**已治本**（2026-07-19，本提交）：
- [`session_worktree.py` `_recover_changes_from_stash`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) — `git checkout <stash> --` → `git restore --source <stash> --`
- [`self_healer.py` `_rollback`](file:///d:/ZephyrAlpha/src/zephyr/governance/semantic_audit/self_healer.py) — `git checkout --` → `git restore --`
- [`rollback_executor.py` discard](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/rollback/rollback_executor.py) — `git checkout --` → `git restore --`
- `session_worktree_abort` / `_execute_cleanups`（pre-merge auto-clean）已在 S3-B 治本（2026-07-17）改用 `git stash push`，不涉及 `git checkout`

**例外**：`git_bisector.py` 保留 `git checkout <commit>` / `git checkout -`（bisect 低频场景）。`git switch` 不被 `git_guard.py` 拦截保护，改造需先扩展 git_guard 支持 `switch` 子命令，超本次范围。

**规则 2：删除文件禁止用 `Remove-Item`，MUST 用 DeleteFile 工具或 Python os.remove**

`Remove-Item` 是 PowerShell 的 rm 等价命令，被 Trae Shell Interception 高危拦截（与 `rm`/`rmdir` 同级）。

| 场景 | ❌ 禁止（弹窗） | ✅ 必须（不弹窗） |
|------|------|------|
| AI 删除单个文件 | `Remove-Item <file> -Force` | 用内置 **DeleteFile 工具**（进回收站可恢复，最安全） |
| 代码内删标记/临时文件 | `Remove-Item xxx.flag -Force -ErrorAction SilentlyContinue` | `python -c "import os; os.path.exists('xxx.flag') and os.remove('xxx.flag')"` |
| 批量删除 | `Remove-Item xxx/*` | Python `pathlib.Path.unlink()` 循环 |

**诊断**：用户弹窗 `检测到高风险命令 Remove-Item "D:\ZephyrAlpha\data\databases\depgraph_dirty.flag"` 即违反本规则。删除 `.flag` 标记文件应改用 `os.remove`。

### 10.3 PRECOMMIT-OFFLINE：pre-commit hook 离线可运行纪律（#ARCH-PRECOMMIT-OFFLINE-001，2026-07-21）

**病根**：`.pre-commit-config.yaml` 曾引用外部 GitHub repo `pre-commit/pre-commit-hooks`（rev v4.6.0），pre-commit 工具在缓存失效/首次安装时会 `git fetch origin --tags` 拉取远程 repo——代理（127.0.0.1:10808）未启动或离线环境会卡死所有 commit。

**100% AI 场景下的定位**：GitCommitGateway 三层防御中，A 层（in-process gate 70+ 个）是主防线，永远用 `--no-verify` 绕过 pre-commit hook；C 层（pre-commit hook）仅在 AI 误用裸 `git commit` 时兜底。但 C 层依赖外部 repo 让"冗余防线"变成"单点故障"——防御措施本身成了攻击面。

**铁律**（真源 `trae_073_precommit_offline_discipline.yaml`，5 条）：

| # | 铁律 | 违反示例 |
|---|------|---------|
| 1 | 外部 repo 禁令：`.pre-commit-config.yaml` 禁止引用 `github.com/...` 等 external repo | `repo: https://github.com/pre-commit/pre-commit-hooks` ❌ |
| 2 | `language: system` 强制：禁止 `pygrep`/`rust`/`python` 等 pre-commit 内置语言 | `language: pygrep` ❌ → `language: system` ✅ |
| 3 | 纯 stdlib 实现：local hook entry 脚本 MUST 仅用 Python stdlib | `entry: python scripts/governance/d7_code/check_merge_conflict.py` ✅ |
| 4 | 删除冗余双防线：能力已被项目内 gate/hook 等价覆盖的 external hook 禁止重复登记 | ruff format 已覆盖 trailing-whitespace，禁止再登记 external hook ❌ |
| 5 | 逃生通道 `--no-verify`：GitCommitGateway 保留 `--no-verify` 绕过能力 | `gateway.commit(...)` 内部用 `--no-verify` ✅ |

**强制执行**：`GATE-PRECOMMIT-OFFLINE`（priority=111，A 层 in-process gate）检测 `.pre-commit-config.yaml` 中外部 repo 引用 + `language` 非 `system`，硬阻断 commit。

**替代脚本**（纯 stdlib，local hook entry）：`check_merge_conflict.py` / `detect_private_key.py` / `check_no_tests_unit.py`

**stage 名迁移记录**（2026-08-01 一次性维护）：pre-commit v3→v4 将弃用的 stage 名 `commit` 重命名为 `pre-commit`。本项目 5 个 hook（gate-c2 / gate-arch / gate-naming 等簇合并 hook）原用 `stages: [commit]` 或 `stages: [manual]`，已执行 `pre-commit migrate-config` 自动迁移为 `stages: [pre-commit]`。**约束**：新增/修改 hook 时 `stages` 字段 MUST 用 `pre-commit`（v4 名），禁用旧名 `commit`（v4 起静默失效，hook 不触发）。迁移已内联标注于 `.pre-commit-config.yaml` 各 hook 注释。

### 10.4 PRECOMMIT-INCREMENTAL：pre-commit hook 增量守门纪律（#ARCH-PRECOMMIT-INCREMENTAL，2026-08-06）

**病根**：pre-commit hook 原为全量扫描（`--scan` / `--all-files`），每次 commit 扫出 369 条历史 warn-only 违规 + 未跟踪 WIP，用与本次 commit 无关的问题卡死提交（eia_provider.py 事件：369"阻断性"违规实际真阻断只有 2 个 N-16）。

**铁律**（真源 `trae_084_precommit_incremental_discipline.yaml`，5 条）：

| # | 铁律 | 违反示例 |
|---|------|---------|
| 1 | 增量守门：commit 阶段 hook 只检查 staged 新增文件（`--check-new` / `--ci`） | `entry: ... --scan` 在 commit 阶段 ❌ |
| 2 | 审计分离：全仓扫描 hook 移 `stages:[manual]`，不卡日常 commit | 全量 hook 不设 `stages:[manual]` ❌ |
| 3 | 历史违规归档为技术债，走 CI/manual 清零 | 用历史违规阻断本次 staged 文件无关的 commit ❌ |
| 4 | 显示二元化：`actual_blocking` vs `warn_only_count`，显示与 exit code 一致 | warn-only 模式输出"阻断性违规"但 exit 0 ❌ |
| 5 | 双路径一致：GitCommitGateway 与 pre-commit 检测逻辑统一 | gateway 增量但 pre-commit 全量 ❌ |

**落地实例**：`gate-naming`（增量 `--check-new`）+ `gate-naming-audit`（全量 `manual`）；`gate-frontmatter`（增量 `--ci`）+ `gate-frontmatter-audit`（全量 `manual`）。历史违规基线见 `.runtime/gate_audit/precommit_incremental_baseline.json`（4 N-16 + 586 warn-only + 21 frontmatter）。

## 11. depgraph 使用指引（唯一全景真源）

> **三图正交声明（TRAE-061，2026-07-06）**：项目有三张架构图，正交分离，通过 `module_id` 关联：
> - **depgraph**（模块依赖图，静态）：模块间依赖关系。真源=代码 AST 扫描。表 `nodes`/`edges`/...。入口 `apply_depgraph.py`/`extract_depgraph.py`。写锁 `pg_advisory_lock(424242)`。
> - **dataflowgraph**（数据流图，动态）：Job/Dataset 数据流转。真源=`dataflow_graph_registry.yaml`。表 `dataflow_*`。入口 `apply_dataflowgraph.py`。写锁 `pg_advisory_lock(424243)`。
> - **decisiongraph**（决策流图，动态）：L0-L6 交易决策链。真源=`decision_graph_model.yaml`。表 `decision_*`。入口 `apply_decisiongraph.py`/`extract_decisiongraph.py`。写锁 `pg_advisory_lock(424244)`。
> 三图共库（localhost:5432），不同表前缀，不同写锁。禁止混用入口。详见 [governance blueprint §19](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/blueprint.md)。

### 11.0 真源方向决策表（唯一入口，新 AI 必读）

> 项目存在两个真源方向，按数据类型机械判定。**禁止凭记忆推断真源方向**——拿到数据先查此表。

| 数据类型 | 真源 | 修改入口 | 判定关键词 | DB 表 |
|---------|------|---------|-----------|-------|
| 架构全景图（域/模块/依赖/path_design/physical_files） | PostgreSQL depgraph | `apply_depgraph.py` | 实例态（磁盘上有什么） | nodes/edges/domains/domain_dependencies/domain_mapping 等 16+ 张可写表 |
| 规则/契约/门禁/词汇表 | YAML 文件 | 改 YAML → GATE-YAML-SYNC 自动同步 | 声明态（应该有什么） | gates/field_vocabularies/registries/cross_registry_rules/hard_boundaries/business_streams/infrastructure_components/model_capabilities（8 张 readonly 表，禁止手写） |
| 数据库清单 | `infrastructure_registry.yaml` | 改 YAML | INFRA-DB-* | infrastructure_components（与规则数据共享表，但真源是 YAML） |

> **判定规则**：拿到一个数据，先问"是实例态还是声明态？"——实例态（磁盘上有什么模块/文件/依赖）→ DB 真源（apply_depgraph.py）；声明态（规则/契约/词表应该有什么）→ YAML 真源（改 YAML，DB 自动同步）。边界模糊时查此表。
>
> **blueprint_links 特殊裁定（2026-07-02）**：`blueprint_links` 表是从 `nodes` 表派生的物化视图（非 YAML 真源），由 `sync_yaml_to_depgraph.py` 重建，但无 readonly 触发器保护，`apply_depgraph.py` 可直接写入。

### 11.0.1 数据库清单真源指针（新 AI 进入项目先读此段）

> **唯一真源**：[`docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml) 的 `infrastructure:` 段（`type` 含 `*_db` 的条目）。
>
> **铁律**：禁止在任何其它文档（蓝图/规则/onboarding/副本）同步数据库清单——所有引用 MUST 用纯指针指向上方真源，禁止摘抄数据库条目作为同步副本。新增/废弃数据库 MUST 先改 infrastructure_registry.yaml，再由 reconciler 派生，禁止反向。违反此铁律会导致 17+ 副本漂移重演（历史教训）。

**新 AI 发现路径**：
1. 想知道"项目有几个数据库/各负责什么" → 直接读 infrastructure_registry.yaml 的 `infrastructure:` 段，禁止凭记忆或其它文档推断。
2. 准备改 DB 连接/新增 DB → 先查真源确认当前状态，再按下方 §11 depgraph 流程或对应模块蓝图施工。
3. 写文档需要提"数据库清单" → 一律用纯指针引用真源，禁止复制条目。
4. ~~准备操作 market.duckdb~~ → **market.duckdb（原 INFRA-DB-005）已于 2026-07-01 彻底删除**（墓碑清理，见 ARCH-046 铁律3"删除即彻底删除"）。原 market_schema.py 同步删除（死代码）。业务行情数据迁移至 ClickHouse c1_market（INFRA-DB-006，status=connected），统一入口 `DatabaseService.get_clickhouse_conn()`（readonly=1），详见 [c1_market_clickhouse.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md)。**注意**：DuckDB OLAP 引擎（INFRA-DB-004，:memory: 内存模式只读挂载 governance.db）保留不变，与 market.duckdb 是两个独立实体。
5. **ARCH-046 数据库节点全景图登记三铁律**（2026-07-04 固化）：(1) 粒度铁律——数据库在全景图中有且仅有一个点（`infrastructure_components` 表），不展开内部表/schema；(2) 运营态/设计态语义铁律——数据库存在并使用=运营态（status=connected），不存在=设计态（status=planned），禁止 status 漂移；(3) 动态更新铁律——数据库节点随项目实况增删，不保留墓碑，生成器（generate_project_depgraph.py）MUST NOT 碰 `infrastructure_components` 表。详见 [ARCH-046](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)。

> **业务数据表清单**（2026-07-06）：想知道 ClickHouse c1_market/c3_fundamental 各业务表有什么数据、起止时间、标的数、新鲜度 → 读 [`docs/02_enterprise_architecture/05_dataflow_architecture/data_inventory.md`](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/05_dataflow_architecture/data_inventory.md)。生成器 [`scripts/governance/d5_architecture/generators/generate_data_inventory.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_data_inventory.py) 可随时运行刷新（`python scripts/governance/d5_architecture/generators/generate_data_inventory.py`）。禁止手工同步业务表清单到其它文档——一律用纯指针指向此文档。

### 11.0.2 ⚠️ YAML 真源 vs DB 真源分类铁律（SSoT Classification，2026-07-06）

> **铁律**：项目有两类数据真源，按数据类型机械判定，禁止凭记忆推断。AI 写入架构数据前 MUST 先查此表。规则真源文件：[`trae_062_ssot_classification.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml)。

| 数据类型 | 真源 | 写入方式 | 例子 |
|---------|------|---------|------|
| **规则数据**（trae_*.yaml、契约、门禁、词汇表、注册表） | **YAML 文件** | `sync_yaml_to_depgraph.py` 单向同步到 DB（DB 是只读缓存） | `trae_001_*.yaml` / `gate_registry.yaml` / `rule_catalog_registry.yaml` / `infrastructure_registry.yaml` |
| **架构数据**（depgraph.nodes/edges、decision_nodes/edges、dataflow 节点） | **PostgreSQL DB** | `apply_depgraph.py` / `apply_decisiongraph.py` / `apply_dataflowgraph.py` 直接写入 DB | 设计态决策节点、依赖关系、数据流节点 |

> **铁律清单（AI 操作前必读）**：
> - 架构数据（nodes/edges）的真源在 PostgreSQL DB，**不在 YAML**。
> - 禁止把架构数据写入 YAML 真源文件（如 `decision_graph_model.yaml` 的 `design_nodes` 字段）。
> - 禁止扩展 sync 脚本去同步架构数据 nodes/edges（`sync_yaml_to_depgraph.py` 只同步规则数据，不同步架构数据）。
> - 架构数据通过 `apply_*.py --batch` 直接写入 DB。
> - 生成器从 DB 读取，重新生成 MD 视图（设计态在 DB 里，所以重新生成不会丢失）。

> **常见错误（AI 容易犯）**：
> - ❌ 把决策节点写入 `decision_graph_model.yaml` 的 `design_nodes` 字段——架构数据真源在 DB。
> - ❌ 扩展 `generate_decision_graph.py` 新增 nodes 同步逻辑——该脚本只同步 schema 定义。
> - ❌ 误以为"YAML 是真源"适用于所有数据（实际只适用规则数据，架构数据真源在 DB）。

> **判定流程**：拿到一个数据 → 先问"是规则数据还是架构数据？"
> 1. 规则数据（声明态：规则/契约/词表应该有什么）→ 改 YAML 真源 → `sync_yaml_to_depgraph.py` 同步到 DB。
> 2. 架构数据（实例态：nodes/edges 实际有什么节点/边）→ 用 `apply_*.py` 直接写 DB → 生成器从 DB 重生 MD 视图。
> 3. 边界模糊时查上方表格，或查 [`trae_062_ssot_classification.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml)。

> **入职入口**：本机制是 RULE-DEPGRAPH / 五图对齐（第三件事）的执行细节，AI 施工前必读；规则真源 [`trae_080_panorama_alignment.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_080_panorama_alignment.yaml)。
>
> **ARCH-053 三图设计态保护 + 对齐检测（2026-07-06）**：
> - **设计态保护触发器**：dataflowgraph（3 表）+ decisiongraph（3 表）共 6 张表新增 BEFORE DELETE OR UPDATE 触发器，阻断 `design_maturity='design'` 行的删除或降级。逃生通道：`SET app.allow_design_maturity_delete = on`（仅 `apply_dataflowgraph.py` / `apply_decisiongraph.py` 设计态写入命令启用，对齐 depgraph `app.allow_delete_apply_depgraph_edges` 模式）。
> - **TRAE-082 治本（2026-08-02）trigger 语义重构**：原逻辑一刀切阻断 design 态行所有 maturity 变更（含合法 design→production 升级，错误信息"降级"一词 misleading）。现改为：① design→production 升级 → 放行（模块毕业，YAML 已 deliberate 改 production）；② production→design 降级 → 阻断（防 sync/人工误回退已上线 .py）；③ design→design 字段更新 → 放行。治本后 sync UPSERT design→production 无需逃生通道绕行。SQL 真源：[`03_create_dataflow_schema.sql`](file:///d:/ZephyrAlpha/scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql)。
> - **三图对齐检测器**：[`align_panoramas.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/align_panoramas.py)（只读，manual 启动）。从三图读取节点，用 `module_id` 作为对齐 key（depgraph 用 `blueprint_id` 派生），检测 4 类问题：孤儿（仅一图）/ 状态漂移（design_maturity 不一致）/ 域不一致（domain_id 不一致）/ 设计态孤立（design 仅一图）。输出 `docs/02_enterprise_architecture/03_governance_reports/panorama_alignment_report.md`。退出码：0=成功 / 1=错误 / 2=三图任一为空（检测无意义）。
> - **GATE-ARCH-DIAGRAM 触发器盲点修复**：`apply_dataflowgraph.py` 已加入 `_PG_WRITE_SCRIPTS` 触发列表，DB 写入后自动重生架构图。
> - **capability 反查入口**：`panorama_alignment_detection`（aliases: align_panoramas/panorama_alignment/three_panoramas_alignment/ARCH-053/design_maturity_alignment）+ `design_maturity_trigger_protection`（aliases: protect_design_maturity/design_maturity_delete_protection/allow_design_maturity_delete/ARCH-053-trigger）。
> - **ARCH-056 五图模块同步引擎 + 门禁阻断升级（2026-07-09）**：
>   - **同步引擎**：[`sync_panorama_module.py`](file:///d:/ZephyrAlpha/scripts/governance/sync_panorama_module.py) 从 depgraph.nodes 读取模块核心字段（module_id/domain_id/design_maturity/build_status），单向派生到 dataflow_jobs（占位 `entity_type='module_placeholder'`）+ decision_layers（占位 `track='placeholder'`）+ blueprint.md frontmatter。触发：`generate_project_depgraph.py`（sync_all）+ `apply_depgraph.py`（sync_module）执行后自动调用。
>   - **蓝图 frontmatter 对齐**：[`blueprint_frontmatter_reconciler.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/syncers/blueprint_frontmatter_reconciler.py) 只更新 4 个核心字段（module_id/responsibility_domain/design_maturity/build_status），文档内容不动，蓝图不存在则跳过。
>   - **门禁阻断升级**：`GATE-PANORAMA-ALIGNMENT`（priority=830）原 warn-only，现升级为 **domain_mismatches>0 阻断**（passed=False）；orphans/state_drifts 保持 warn-only。修复入口：`python scripts/governance/sync_panorama_module.py --all`。
>   - **capability 反查入口**：`panorama_module_sync`（aliases: sync_panorama_module/five_panoramas_sync/ARCH-056/module_panorama_sync）+ `panorama_module_sync_engine`（aliases: sync_panorama_module/panorama_sync/prune_orphans/ARCH-056/ARCH-058，2026-07-16 治本登记）。

> **ARCH-058 prune_orphans 责任边界治本（2026-07-16 AI-20 审计修复）**：
> - **问题**：Phase 2.2 过渡方案让 `prune_orphans` 绕道 `get_depgraph_pg_connection(read_only=False)` 写 dataflow_jobs 表，违反"dataflow 表操作走 dataflow 连接工厂"的责任边界原则。
> - **治本**：① 扩展 [`get_dataflowgraph_pg_connection`](file:///d:/ZephyrAlpha/src/zephyr/governance/persistence/dataflowgraph_schema.py) 原生支持 `read_only=False`（对齐 depgraph_schema 角色分级 READER/WRITER/superuser 三级模式）；② `prune_orphans` 改回走 dataflow 连接工厂 `get_dataflowgraph_pg_connection(read_only=False, autocommit=False, allow_design_delete=True)`；③ 新增 `acquire_dataflow_write_lock`/`release_dataflow_write_lock`（`pg_advisory_lock 424243`，session 级互斥）防止并发写冲突。commit 互斥不释放，需显式 unlock（finally 块保证）。
> - **capability 反查**：`panorama_module_sync_engine`（aliases 含 prune_orphans/ARCH-058）。

> depgraph 是唯一全景真源（PostgreSQL 16，localhost:5432），禁止创建派生 YAML 副本。连接配置见 `config/.env.postgres`，连接入口 `zephyr.governance.depgraph_schema.get_depgraph_pg_connection()`。遇到 depgraph 相关问题，直接问工具：

- **查 DB 数据** → `python scripts/governance/extract_depgraph.py --help`（场景速查表在 epilog）
- **改 DB 节点/路径** → `python scripts/governance/apply_depgraph.py --help`（35+ 子命令）
- **批量改 DB（多 op 原子事务）** → `python scripts/governance/apply_depgraph.py --batch changes.json`（先 `--dry-run` 预览）。op 清单运行 `--list-ops` 查看（从 `_DOMAIN_OPS`/`_NODE_OPS` 注册表自动派生，真源唯一——禁止手工同步到 docstring/AGENTS.md，§6.2 铁律）；所有 op 共享单一 PostgreSQL 事务，全部成功才 commit，任一失败全部 rollback。批量重命名域 ID 时**禁止**手写 `_tmp_batch_rename.py` 调 `--rename-domain` 单命令循环（失去原子性，部分失败留半成品数据）。
- **查哪些表不能手写** → `python scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py --list-readonly-tables`
- **修正 module_id/blueprint_id 合规** → `python scripts/governance/fix_depgraph_module_id.py --dry-run`（28 节点修正编排器，复用 apply_depgraph `--rename-blueprint-id`/`--set-blueprint-id` + fix_header_module_id 原语。`--file-sync-only` 模式仅补文件同步不碰 DB。新增 apply_depgraph `--clear-invalid-flag BLUEPRINT_ID`（清除 invalid 标志，mark-invalid 的逆操作）和 `--clear-blueprint-id PATH`（按 path 清空 blueprint_id，用于 infra_id 误存治理））
- **文件结构变更后同步 DB** → 自动完成（GitCommitGateway post-commit GATE-PATH-TREE reconciler，无需手动）
- **DB 变更后重生域文档** → 自动完成（GitCommitGateway post-commit GATE-REGENERATE reconciler（含原 DOMAIN-DOC 功能），无需手动）
- **文件删除后重生域文档** → 自动完成（GATE-REGENERATE trigger 已扩展：committed 文件不在磁盘 = 删除 commit 时也触发生成器重生。生成器内置 ghost 过滤，重生后的文档自动排除已删除文件的节点，无需手动 deprecate）
- **scripts/ 下 .py 增删后重生 manifest** → 自动完成（GitCommitGateway post-commit GATE-MANIFEST reconciler，priority=620，2026-07-01 新增。无需手动跑 generate_script_manifest.py）
- **铁律：架构文档（02_domain_architecture_docs/ + generated/domains/）由生成器自动产出，禁止手动编辑**。手动编辑会被下次生成器运行覆盖。如需修改内容，改 depgraph 或生成器代码，不要改输出文件。
- **改了 YAML 规则文件后同步 DB** → 自动完成（GitCommitGateway post-commit GATE-YAML-SYNC reconciler，无需手动）。手动调试可跑 `python scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py`
- **改了 rules/ 下规则文件后同步 catalog** → 自动完成（GitCommitGateway post-commit GATE-RULE-AUDIT reconciler（含原 RULE-CATALOG 功能），无需手动）。catalog 真源：`_registry/catalogs/rule_catalog_registry.yaml`（由 `scripts/governance/d3_metadata/generate_rule_catalog.py` 自动生成，60 条规则元数据；#ARCH-024 治本：原 `rules/_index.yaml` 手工索引已删除）
- **改了 infrastructure_registry.yaml 后同步 registry_master_index** → 自动完成（GitCommitGateway post-commit GATE-REGISTRY-SYNC reconciler（含原 REGISTRY-INDEX 功能），无需手动）
- **查 PG 运行时健康** → `python scripts/governance/d11_compliance/verify_schema_health.py --warn-only`（校验4：死锁/连接饱和/长事务，pre-commit 自动跑；`--skip-runtime` 可跳过）

> **GATE-SCHEMA-HEALTH 门禁（ARCH-016/017/018 治本，2026-06-26）**：depgraph (PostgreSQL) Schema 健康度校验，4 项校验（DDL 列一致性/只读触发器/Schema 版本/PG 运行时健康）。**门禁路由**：原独立 `gate-schema-health` 已于 ARCH-017 治本时合并到 **GATE-C2**（run_gate_chain 顺序执行 check_contract_code_drift + check_contract_physical_path + verify_schema_health），`.pre-commit-config.yaml` stages 从 manual 升级为 commit（--no-verify 绕不过 GitCommitGateway in-process gate）。**检测真源**：`scripts/governance/d11_compliance/verify_schema_health.py`（capability=schema_health_verification，aliases 含 GATE-SCHEMA-HEALTH/verify_schema_health/schema_health）。**重定向锚点**：gate_registry.yaml 保留 GATE-SCHEMA-HEALTH 条目（status=deprecated, redirect_to=GATE-C2）供历史引用可追溯。退出码：0=健康/1=漂移/2=脚本错误；模式：--ci 硬阻断（默认）/--warn-only 软警告/--skip-runtime 跳过校验4。

> 改 depgraph 前必须通过 `pg_dump` 或 apply_depgraph.py 内置物理备份（trae_054 STEP0）。DB↔磁盘一致性检查用 `python scripts/governance/d5_architecture/diagnose_depgraph.py`。

> **ghost 自动检测+自动清理（已实现，勿重复造）**：删除文件 commit 时，GitCommitGateway post-commit 的 `GATE-DELETE-AUDIT` reconciler（含原 GHOST 功能，priority=400）自动调用 `diagnose_depgraph.py` 检测 ghost node（磁盘已删但 DB 残留），报告落盘 `.runtime/reconcile_reports/ghost_*.json`。无需手动跑 diagnose 检测 ghost。**清理路径（2026-07-04 P1 治本，auto_clean 闭环）**：① ghost 数 ≤ 50 → reconciler 自动调 `apply_depgraph.py --cleanup-orphan-nodes` + `--cleanup-orphan-edges` 清理（备份先行：`_backup_depgraph_for_autoclean` 用 F1 裸 psycopg2 connection + copy_expert 导出 nodes/edges CSV 到 `tmp/pg_backups/ghost_autoclean_<ts>/`（.gitignored，与 backup_pg_architecture 标杆对齐；保留最近 10 个，`_cleanup_old_ghost_backups` 自动清理过期，ARCH-DEBT-BACKUP-CLEANUP 2026-07-08 治本），备份失败 fail-closed 不清理）；② ghost 数 > 50 或解析失败 → 走 warn 不清理（防批量误删），需人工 `apply_depgraph.py --cleanup-orphan-nodes`。阈值 `_GHOST_AUTO_CLEAN_THRESHOLD=50`（reconciliation_registry.py），与 generate_project_depgraph.py `_GHOST_WARNING_THRESHOLD=50` 对齐。trigger 仅覆盖"删除 commit"是 intentional（删除才会产生 ghost），勿扩展到 PG 写入脚本 commit（脚本 commit ≠ DB 内容变更，扩展会引入噪音）。

> **三层 ghost 防御（2026-07-01 ARCH-038 铁律，勿重复造）**：
> 1. **Layer 1（技术铁律）**：生成器（`generate_domain_doc.py`）内置 `_is_ghost()` 过滤——path 非空但磁盘不存在的节点自动排除。即使 depgraph 有 2774 个 ghost 节点，生成的文档也不会引用幽灵文件。**新 AI 不需要知道要跑 deprecate——不跑也不会有问题**。
> 2. **Layer 2（自动修复）**：GATE-REGENERATE trigger 已扩展——文件删除 commit 时自动触发生成器重生。GATE-MANIFEST（priority=620）自动重生 script-manifest.yaml。GitCommitGateway post-commit 全自动，无需人工触发。
> 3. **Layer 3（规则补充）**：本段 AGENTS.md 规则。禁止裸连数据库，必须通过 `apply_depgraph.py` 程序化访问（真源方向见 §11.0 决策表）。架构文档由生成器自动产出，禁止手动编辑。

> **命名规范（2026-06-30）**：本数据库的标准名字是 `depgraph (PostgreSQL)`——一眼可知引擎、区别于 SQLite 物理文件 `depgraph.db`。禁止使用以下变体：① 带括号缩写 `depgraph (PG)`/`PG（depgraph）`；② 带"数据库"后缀 `depgraph 数据库`；③ 无括号全称 `PostgreSQL depgraph`/`depgraph PostgreSQL`；④ 无括号缩写 `PG depgraph`/`depgraph PG`。物理标识符不改：`depgraph.db`（SQLite 文件名）、`localhost:5432/depgraph`（PG 连接 URL 中的 database 名）、`数据库名 \`depgraph\``（PG 物理 database 名）、函数名 `get_depgraph_pg_connection`。

### 11.0.3 ⚠️ 核心治理工具健康度铁律（Tool Health，2026-07-19，裁定 #ARCH-TOOL-HEALTH-V1）

> **新 AI 在调用 `apply_depgraph.py` / `apply_decisiongraph.py` / `apply_dataflowgraph.py` / `sync_yaml_to_depgraph.py` 等 L1/L2/L3 铁律执行工具前 MUST 先读本节。**
> 病根：commit `deb695006f` 批量重构 `sys.exit→EXIT_*` 时误删 `get_depgraph_pg_connection` import（替换整行而非追加），56 处调用保留但无导入，运行时 `NameError` 阻断 L1 铁律执行；5 层防线（ruff F821 / scripts_import_integrity_gate / 单测 / check_blueprint_code_alignment / AI 上报）全部失效——ruff 被 `--no-verify` 绕过；gate 在 bug 后 9h 才上线且只扫 staged；单测全 mock 不触达真实路径；check 直读 DB 不调 apply_depgraph；**AI 遇 NameError 默认 silently workaround 而非上报人类**，导致 LOW `CODE_NOT_IN_DEPGRAPH` drift 静默累积。
> 100% AI 开发场景下，AI 遇工具报错默认 silently workaround 是最大风险；必须有"启动健康度自检 + 强制上报"机制。

**4 条裁定条款**（真源：[`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `#ARCH-TOOL-HEALTH-V1`）：

1. **核心治理工具必须有 end-to-end smoke test**：`apply_depgraph.py` / `apply_decisiongraph.py` / `apply_dataflowgraph.py` / `sync_yaml_to_depgraph.py` 等必须真实调用 CLI + 真实 DB + 验证写入行；mock 单测不能替代 e2e smoke test（mock 路径下 NameError 类 bug 永远不暴露）。真源：`tests/governance/test_apply_depgraph_smoke.py`。
2. **导入完整性 gate 必须支持 baseline 全扫模式**：`scripts_import_integrity_gate` 当前只扫 staged 文件（incremental-only），gate 上线前的基线 bug 永远不会被扫到。必须新增 baseline 全扫模式作为 post-commit reconciler 定期跑全仓（`make_scripts_import_integrity_reconciler`，priority=210）。
3. **`--no-verify` 必须被审计**：POST-COMMIT-GUARD 当前对 `ZEPHYR_COMMIT_GATEWAY=1` 是 warn-only。必须新增"高基数 `--no-verify` commit"检测——同一 session 1 小时内超过 3 次 `--no-verify` commit 强制升级为 `reset --soft HEAD~1` 阻断（阈值 N=3，可配置）。
4. **AI session 启动 smoke test**：每个 AI session 启动时必须运行核心工具健康度 smoke test（`session_startup_health_check.py`），失败时 AI 必须输出 `[ESCALATION]` 标记上报人类而非静默 workaround。

**LLM 编辑模式固有缺陷警示**（治本铁律）：LLM 跨文件批量重构时对"形状相同语义不同"的 import 行有结构性误替换风险——LLM 倾向于重新生成整行而非局部追加。**涉及 import 行的修改必须用 Edit 工具（精确替换）而非 Write 工具（整文件覆写），且必须显示 diff 确认仅追加不替换**。deb695006f 就是用 sed 批量替换整行 import 导致的，治本方案是禁止整行覆写 import。

### 11.1 生成器发现指引与时间戳约定

> **新 AI 进入项目涉及"生成器"相关工作时，MUST 先读本节。**
> 病根：AI 跨域复刻生成器（wave_generator 4 份副本、index_generator 影子副本等），
> 根因是新 AI 不知道已有生成器存在。治本：发现指引 + P0 防再生门禁。

#### 11.1.0 生成器发现指引（RULE-EIGHT 生成器专项）

**创建新生成器前 MUST 执行以下 3 步查重**：

1. **关键词搜索**：`python -m zephyr.governance.capability_lookup --find <关键词>`
   - 搜索 capability_id / aliases / description / canonical_file / module_id
   - 例：`--find generator`、`--find path_tree`、`--find index`
2. **注册表匹配**：查 [`capability_canonical_file_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml)
   - `domain_architecture_generators` 条目列出全部 13 个架构生成器及其别名
   - `outputs` 字段列出生成器→输出目录映射
3. **复用决策**：命中已有 → 扩展已有生成器（RULE-EIGHT 扩展优先于新建）；未命中 → 通过 `scaffold.py` 创建（P0-5 create_guard 强制）

**已有生成器清单**（真源：`scripts/governance/d5_architecture/generators/`）：

| 生成器 | 输出目录 | 用途 |
|--------|----------|------|
| `generate_navigation_index.py` | `02_enterprise_architecture/00_overview_entry/` | 导航索引 |
| `generate_path_tree.py` | `01_global_architecture_diagram/` | 项目路径树 |
| `generate_cross_domain_matrix.py` | `01_global_architecture_diagram/` | 跨域矩阵 |
| `generate_integration_topology.py` | `01_global_architecture_diagram/` | 集成拓扑 |
| `generate_capability_heatmap.py` | `01_global_architecture_diagram/` | 能力热图 |
| `generate_domain_doc.py` | `02_domain_architecture_docs/` | 域架构文档 |
| `generate_module_algorithm_overview.py` | `02_enterprise_architecture/08_algorithm_overview/` | 模块核心算法纵览（跨域按 layer 拓扑，三档 code>blueprint>empty，离库派生；共享 code_algorithm_extractor.py） |
| `generate_domain_index.py` | `02_domain_architecture_docs/` | 域索引 |
| `generate_design_vs_production.py` | `03_governance_reports/` | 设计 vs 生产 |
| `generate_constraint_violations.py` | `03_governance_reports/` | 约束违规（读 PG 展示） |
| `detect_constraint_violations.py` | `03_governance_reports/` | 约束违规检测（写 PG，GATE-CONSTRAINT-DETECT） |
| `generate_capacity_report.py` | `03_governance_reports/` | 容量报告 |
| `generate_candidate_module_report.py` | `03_governance_reports/candidate_modules/` | 候选模块清单报告（分片：索引+按域） |
| `generate_panorama_registry.py` | `00_overview_entry/` | 全景图清单总表 |
| `generate_contracts.py` | `05_contracts/` | 契约文档 |

**候选模块治理工具**（候选池=储备未开发/过度工程模块的"点子池"，与depgraph设计态严格分离）：

| 工具 | 路径 | 用途 |
|------|------|------|
| `harvest_candidates_from_drafts.py` | `scripts/governance/` | 从场外草稿CSV抓取候选模块入候选库（`--all`全量44域/`--domain D_XXX`单域/`--dry-run`预览）|
| `generate_candidate_module_report.py` | `scripts/governance/d5_architecture/generators/` | 生成候选模块报告（按域分片：`candidate_modules/index.md`+37域文件）|

- **候选库真源**：[`candidate_module_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml)（5301条=18原始+5283harvest）
- **翻译真源**：[`module_translation_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml)（候选以`CAND-HARVEST-xxxx`为key，`plain_zh`字段存大白话解释）
- **节点标签简介质量**：`plain_zh` 须过三问法（是什么/干什么/解决什么问题），禁五类坏简介（①模板话 ②截断片段 ③消费者引用 ④术语堆砌 ⑤名称重复）。审计脚本 [`check_node_label_quality.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_node_label_quality.py)（warn-only pre-commit gate `GATE-NODE-LABEL-QUALITY`，与 TRANSLATION-COVERAGE 互补——后者管存在性，本 gate 管质量）；完整规范 + 人工补齐 SOP 见 [可视化视图模板 §十七](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/visualization_view_template.md)
- **翻译覆盖率门禁（TRANSLATION-COVERAGE）**：新建 .py 文件大白话简介覆盖率门禁，已从观察期（warn-only）转为**硬阻断**（fail-closed，`_OBSERVATION_PERIOD=False`，2026-08-02 drift 清零后转正）。检测 staged 新增 .py 文件（`src/zephyr/` + `scripts/` 下，`tests/`/`demos/`/`test_*.py`/`__init__.py`/`_archive/` 豁免）在翻译真源 [`module_translation_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml) 中有非空且非通用模板的 `plain_zh`（CJK≥8）。违规硬阻断 commit，提示运行 `python scripts/governance/d3_metadata/add_module_translation.py --path <file> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>` 写入简介。**四层防御体系**（canonical Layer 0/1/2/4）：Layer 0 [`add_module_translation.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/add_module_translation.py) 合规写入工具 → Layer 1 `apply_depgraph.py` 登记时 warn 提示 → Layer 2 本门禁提交时硬阻断（含 `is_generic` 质量检测）→ Layer 4 [`translation_coverage_reconciler.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/translation_coverage_reconciler.py) post-commit 存量对账（warn-only，漂移报告落盘 `.runtime/translation_coverage/drift_report.json`）。`priority=59`（NEW-FILE-DEPGRAPH-ENFORCEMENT(58) 之后、CREATE-GUARD(60) 之前——先确认 depgraph 结构登记，再要求翻译完整性）
- **幂等保证**：harvest脚本双注册表去重（`existing_harvest_keys`候选库+`existing_translation_keys`翻译真源+`max_harvest_seq`扫描双注册表防seq碰撞），重跑不会产生重复
- **设计准入一问标准**（裁定2026-08-04）：每条候选含`design_admission`字段（仅 q1 已实现/重复），原四问 q2需求驱动/q3域活着/q4 AI替代 因灰度无法二元化已废。q1"是"（已实现/重复）即不登记depgraph

**P0 防再生门禁**（2026-07-01 生成器治理治本）：
- P0-1：N-16 src/ basename 唯一门禁——同 basename 跨域 commit 阻断
- P0-2：GATE-SSOT 硬层3——同 module_id 多文件 commit 阻断
- P0-3：GATE-SSOT 硬层4——[MODULE] 声明域 ≠ 物理路径域 commit 阻断
- P0-4：scaffold 维度3b——同 basename 跨域创建阻断
- P0-5：scaffold 自动登记 creation_token——绕 scaffold 直接 Write .py → commit 阻断
- **P0-6：公共函数按需创建铁律**（#ARCH-STAGE4-PUBLIC-WRAPPER-DEAD-CODE-001，2026-08-02 治本）：公共函数（无 `_` 前缀）仅在存在**真实外部消费者**（其他模块 import 该符号）时创建，第一调用方必须是该消费者，**禁止预防性公共化**。默认模式：私有实现（`_xxx`）+ 测试 patch 私有缝。当且仅当外部模块需要 import 该符号时才升级为公共（届时公共为 canonical，旧私有可删或转薄包装）。**dual 公共/私有并存是临时迁移态，禁止作为终态留存**——零外部调用方的公共 wrapper = 死代码 = 必删。病根：2026-07-29 某 AI 会话误读"Stage 4 公共化"标注约定（仅 `full_project_tree_zh.md` 标签，非 TRAE-036 规则——TRAE-036 Stage 4 是阶段成熟度 scaffold→stable终态，非 API 公共化），预防性为 5 个私有函数新增公共 wrapper（`run_subprocess`/`log_reconcile_results`/`get_writer`×2/`run_dashboard`），零外部调用方，导致 25 新+8 旧测试 mock 未命中失败。治本：删 5 死 wrapper + 测试统一 patch 私有 + 本铁律防复发。正典先例：[`session_worktree_sweep`](file:///d:/ZephyrAlpha/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py)（FP-ISO.4C）按需公共化，第一调用方即 CLI 消费者。**防复发自动化**（已实现，2026-08-02）：post-commit reconciler `GATE-DEAD-PUBLIC-WRAPPER`（[`dead_public_wrapper_reconciler.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/dead_public_wrapper_reconciler.py)，priority=950，warn-only）AST 扫描 trivial wrapper（公共函数 body 仅 `return _foo()`）+ 多目录 regex 调用方计数，零外部调用方→warn，将死公共 wrapper 从手工发现转为持续自动检测

#### 11.1.1 时间戳约定

> 所有生成器（`scripts/governance/d5_architecture/generators/` 下的 `.py` 文件）输出的文档中，
> 日期字段 MUST 使用 `auto-generated`，最后更新时间 MUST 标注"最后更新以 git log 为准"。
> **禁止在生成器中使用 `datetime.now()` 或任何实时时间源**，否则每次修改 depgraph (PostgreSQL)
> 都会因时间戳变化产生非幂等噪音 auto-commit。

- **真源实现**：所有生成器 docstring `[INVARIANTS]` 声明"输出幂等(相同输入→相同输出);零时间戳"
- **时间真源**：文件修改时间唯一真源是 git log，生成器不引入独立时间源。幂等时间源公共助手：[`_common.idempotent_timestamp()`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/_common.py) / `idempotent_date()`（返回脚本最近 git commit 时间，相同 commit → 相同输出，正典先例：`generate_decision_diagram._git_commit_timestamp()`）
- **检测（pre-commit 硬阻断，2026-08-05 升级，治本 #ARCH-REGEN-NONIDEMPOTENT-001）**：[`gate-generator-no-realtime-time`](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/check_generator_no_realtime_time.py) pre-commit hook 二元阻断 `scripts/governance/d5_architecture/generators/*.py` 中的 `datetime.now()` / `time.time()` / `datetime.today()`。豁免：行尾加 `# noqa: arch-regen-nonidempotent`（需人工评估，日粒度 `datetime.now(UTC).strftime("%Y-%m-%d")` + `# noqa: m46-time` 自动豁免）。
- **自动触发**：GATE-REGENERATE reconciler（含原 DOMAIN-DOC 功能）在修改 depgraph 后自动调用 generate_domain_doc.py 重生域文档，生成器幂等性确保无噪音 auto-commit（2026-07-30 起 generate_domain_dependency_diagram.py 已下线，域依赖图内嵌于域文档）
- **按域编号生成器 --all 模式 MUST 调用 cleanup_stale_files**：生成"按域编号文件"（`NN_d_xxx.md`，域重命名/删除后旧编号会残留）的生成器，在 `--all` 模式下 MUST 调用 `_common.cleanup_stale_files()` 清理孤儿文件，治本"只增不删"。当前适用：`generate_domain_doc.py`（已调用）。单域模式不清理（避免误删）；生成单文件/非编号文件的生成器（导航索引、容量报告、集成拓扑等）不适用。真源：[`_common.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/_common.py)
- **检测**：对生成 `NN_d_xxx` 格式文件的生成器，`Select-String -Pattern "cleanup_stale_files"` 应返回至少 1 匹配（当前 1 个生成器通过）

#### 11.1.2 ARCH 引用校验门禁（Phase 4 防御性门禁，ARCH-033，2026-07-02）

> **新 AI 修改 `generate_project_depgraph.py` 中 `#ARCH-XXX` 引用时 MUST 先读本节。**
> 病根：AI 在脚本中随意写 `#ARCH-XXX` 引用但不在 [`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 登记，导致 grep-and-claim 占位（编号铁律#6 违规）。
> 治本：`generate_project_depgraph.py` 启动时自动校验本文件所有 `ARCH-XXX` 引用是否在 registry 有对应条目。

- **真源实现**：[`generate_project_depgraph.py`](file:///d:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py) `_validate_arch_references()` 函数
- **自动触发**：`generate_project_depgraph.py` 的 `main()` 中 `parse_args()` 后自动调用 `sync_all_panorama()`（从 `sync_panorama_module` import），无需手动触发
- **自动运行**：正则 `\bARCH-(\d+)` 扫描本文件源代码 → 提取所有 ARCH 编号 → 读取 registry → 比对差集；另用 `\bARCH-\d+`（IGNORECASE）检测小写 `arch-` 违规（标识符编号必须大写，trae_028 §标识符编号格式）
- **自动关闭**：校验完成后打印结果即返回；校验失败 sys.exit(1) 阻断运行（ERROR 级别）
- **校验范围**：仅校验 `generate_project_depgraph.py` 自身源码中的 ARCH 引用，不扫描其他文件
- **registry 真源**：[`architecture_issue_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) `entries[].issue_id` 字段
- **编号铁律#6**：任何 `#ARCH-XXX` 引用必须在本注册表有对应条目，禁止 grep-and-claim 占位
- **标识符编号大写**：ARCH 编号必须大写（`ARCH-033` 合规，`arch-033` 违规），小写引用触发 ERROR 阻断；规则真源见 [trae_028 §标识符编号格式](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml)
- **当前状态**：ERROR 阻断（校验失败 sys.exit(1)，2026-07-02 从 WARN 升级为 ERROR）

#### 11.1.3 生成器自动触发机制（generator_auto_trigger_pilot，2026-08-03）

> **新 AI 涉及"生成器/架构文档自动重生成/派生产物同步"工作时 MUST 先读本节。**
> 病根：23 个架构生成器需手动 `python generate_*.py` 运行，AI 忘记跑导致派生文档
> 与真源（DB/YAML）漂移。治本：注册表驱动统一编排器——apply 写 DB 后实时触发，
> boot_hooks 启动时 mtime 对比兜底。

**架构（注册表驱动·§3.1 能现成不创造）**：

| 组件 | 路径 | 角色 |
|------|------|------|
| **编排器** | [`reconcile_generators.py`](file:///d:/ZephyrAlpha/scripts/governance/reconcile_generators.py) | 统一入口，只读注册表，调度生成器执行 |
| **注册表** | [`generator_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml) | "生成器→触发源→输入/输出"映射唯一真源（TRAE-062 规则数据真源=YAML） |
| **触发点1** | `apply_depgraph.py` / `apply_dataflowgraph.py` / `apply_decisiongraph.py` / `apply_battle_map.py` | DB 真源写入后 `finally` 块调 `reconcile_async(source)` 实时触发 |
| **触发点2** | [`boot_hooks.py`](file:///d:/ZephyrAlpha/src/zephyr/trading/boot_hooks.py) `_subscribe_governance_regeneration()` | 启动时调 `reconcile_stale()` 按 mtime 对比兜底（YAML 变更无 apply 调用） |

**双路径调用**（免改造 23 个 main()-only 生成器）：
- **路径1·in-process**：注册表声明 `entry_function`（如 battle_map 的 `regenerate`）→ importlib 动态加载调用，返回 dict。快（无进程启动开销）
- **路径2·subprocess 回退**：无 `entry_function` → `python <script>` 子进程调 `main()`，按退出码判定（0/1=ok，2+=failed）。隔离（崩溃不影响编排器）

**触发源命名约定**：
- `<graph>_db` — apply_*.py 写 DB 后实时触发（如 `depgraph_db` / `dataflowgraph_db` / `decisiongraph_db` / `battle_map_db`）
- `<name>_yaml` — YAML 真源变更，boot_hooks 启动时 mtime 对比兜底触发

**新增生成器自动化**（无需改编排器代码）：
1. 在 [`generator_registry.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml) 加一条：`name` + `module_path` + `trigger_sources` + `input_sources` + `output_globs`
2. 若生成器有可调用入口函数（无参返回 dict），加 `entry_function` 字段走 in-process；否则留空走 subprocess 回退
3. 若 main() 需要参数（如 `--all`），加 `args` 字段

**逃生通道**：`ZEPHYR_SKIP_REGENERATE=1` 环境变量跳过自动重生成（批量操作时用，boot_hooks 启动时兜底补跑）

**异步生成**（`reconcile_async`）：depgraph 19 生成器同步运行 ~50s，blueprint_panorama --all ~145s，同步阻塞 apply 脚本 UX 不可接受。`reconcile_async` spawn detached subprocess 立即返回，日志写入 `.runtime/logs/regenerate_<source>_<timestamp>.log`，生成器幂等确保重复运行无副作用

**capability 反查入口**：`generator_auto_trigger`（aliases: reconcile_generators/reconcile/reconcile_async/reconcile_stale/generator_registry/生成器自动触发/生成器编排器）

**覆盖范围**（23 个生成器，按目录）：
- `00_overview_entry`：navigation_index、panorama_registry
- `01_global_architecture_diagram`：asset_catalog、capability_heatmap、contract_catalog、cross_domain_matrix、integration_topology、path_tree
- `02_domain_architecture_docs`：domain_doc、domain_index
- `03_governance_reports`：candidate_module_report、capacity_report、constraint_violations、design_vs_production
- `04_architecture_principles_decisions`：code_wiki_stats、blueprint_panorama
- `05_dataflow_architecture`：dataflow_diagram、data_acquisition_flow、data_inventory
- `06_decision_architecture`：decision_diagram
- `07_trading_decision_architecture/battle_map`：battle_map（试点，in-process entry_function）
- Codegen 管线：contracts、policies

#### 11.1.4 派生产物离库原则（#ARCH-GOV-BUDGET-001 / I-GOV-1，2026-08-05 治本）

> **新 AI 涉及"架构文档/生成器产物/git add 派生文件"时 MUST 先读本节。**
> 病根：派生产物（由生成器从 DB/源码派生的 .md 文档）入 git 是 post-commit reconciler
> 非收敛循环的数学根因。生成器任一非确定性（时间戳/SQL 排序/换行符）→ diff →
> auto-commit → 再次触发 reconciler → 跨 commit 永续循环。CONCURRENCY/CASCADE/NONIDEMPOTENT
> 三条裁定都是在补偿这个根因，但只要派生产物在库 + auto-commit 存在，补偿永无止境。
> 治本（第一性原理）：**源真源（DB + 生成器代码）已跟踪，派生产物离库，按需生成**。

- **不变量 I-GOV-1**：凡可由 DB/源码/YAML 经生成器重现的文档，**禁止入 git**。源真源已跟踪，派生产物是构建产物。**适用边界**：约束对象=生成器（generator_registry 登记）派生的 .md 文档；不含 ML 锁定基线数据（.jsonl 预测/评估集——LLM 推理产物非生成器派生、无 reconciler 关联，#ARCH-NLP-BASELINE-DERIVED-001）。
- **当前离库范围**（2026-08-05 落地）：
  - `docs/02_enterprise_architecture/02_domain_architecture_docs/*.md`（73 域文档，[`generate_domain_doc.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_domain_doc.py) 输出；`README.md` 例外）
  - `docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_*.md`（2 项目树，[`generate_path_tree.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_path_tree.py) 输出）
  - `.gitignore` 已配置上述路径；[`GATE-NO-COMMIT-DERIVED`](file:///d:/ZephyrAlpha/scripts/governance/d11_compliance/check_no_commit_derived.py) pre-commit hook 硬阻断 `git add` 派生产物
- **按需生成查看**：[`scripts/serve_docs.py`](file:///d:/ZephyrAlpha/scripts/serve_docs.py) 一键重生成 + 启动本地 HTTP 服务（`http://localhost:8765`），浏览器查看可缩放 Mermaid HTML
- **reconciler 行为变更**：派生产物离库后，`git diff` 不再检测到它们 → reconciler 的 drift-gate 返回空 → 不触发 auto-commit → 非收敛循环物理消失。reconciler 仍会跑生成器（写磁盘），但因产物被 `.gitignore`，不产生 git diff
- **新增生成器产物离库清单**：新生成器输出派生 .md 时，MUST 同步：(1) 加入本节清单；(2) 加 `.gitignore` 规则；(3) 加 `check_no_commit_derived.py` 的 `DERIVED_PATTERNS`；(4) 跑 `git rm --cached` 离库现有文件
- **禁止 `git add -f` 强制跟踪派生产物**：GATE-NO-COMMIT-DERIVED 会阻断。如确需跟踪某文件（非派生），先评估是否应改为源真源管理

### 11.2 P3 PostgreSQL 优化裁定记录（2026-06-28）

> **本节是 P3 相关工作的硬约束。** 任何 AI 在涉及 PostgreSQL 优化时必须先读本节。
> 真源：本节（P3方案文档已于 2026-06-30 归档删除，裁定记录内联于此作为唯一真源）

P3 原计划 4 个任务经第一性原理审查（38 个问题），裁定如下：

| 任务 | 裁定 | 理由 |
|------|------|------|
| P3-T1 pgvector | **改造**（不建 pgvector） | 项目已有 VMS（ChromaDB+BGE-M3+Hybrid+reranker），pgvector 是降级重复造轮子。治本：扩展 VMS code_context indexer |
| P3-T2 LISTEN/NOTIFY | **删除** | 100% AI 开发无常驻监听者，GitCommitGateway+ReconciliationRegistry 事件驱动对账已覆盖 |
| P3-T3 分区表 | **删除** | 24MB/6429行过度工程，edges 无 domain_id 无法分区 |
| P3-T4 监控告警 | **改造已实现** ✅ | 扩展 `verify_schema_health.py` 校验4 `check_pg_runtime_health()`，事件驱动替代违反 trae_053 的常驻 monitor_pg.py |

**禁止新建的文件/对象**（违反则为重复造轮子或伪需求）：
- `pgvector` 扩展、`code_embedding.py`、`nodes.embedding` 列 — VMS 已覆盖向量检索
- `pg_notify.py`、`depgraph_events` 表、LISTEN/NOTIFY 触发器 — GitCommitGateway 已覆盖事件协调
- `monitor_pg.py`、`config/pg_monitor.yaml` — verify_schema_health.py 校验4 已覆盖 PG 运行时监控
- 分区表（nodes/edges 按 domain_id HASH 分区）— 数据量不达标，过度工程

**P3-T4 已实现能力**：`verify_schema_health.py` 新增校验4，检查死锁（信息性）/连接饱和（>80%阻断）/长事务（>300s阻断），pre-commit 事件驱动。`--skip-runtime` 可跳过。

**CT-TEL-001~004 codegen 死代码治本约束**（SSoT 三重冗余修复后裁定，2026-06-28）：
- **真源唯一**：CT-TEL-001~004 的手工实现真源唯一为 [src/zephyr/infrastructure/system_telemetry/](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/) 下的对应文件（MOD-INF-015）：
  - CT-TEL-001 → `system_telemetry/contract_metrics.py`
  - CT-TEL-002 → `system_telemetry/logs/structured_sink.py`
  - CT-TEL-003 → `system_telemetry/traces/span_stub.py`
  - CT-TEL-004 → `system_telemetry/health_probes.py`
- **physical_path: null 不可恢复**：[cross_layer_contracts.yaml](file:///d:/ZephyrAlpha/architecture_model/contracts/cross_layer_contracts.yaml) 中 CT-TEL-001~004 的 `physical_path` 字段 MUST 保持 `null`，禁止改回路径——[`generate_contracts.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/generators/generate_contracts.py) 的 `if not physical: skipped_count += 1; continue` 逻辑会自动跳过生成。
- **禁止重建连字符目录**：`src/zephyr/system-telemetry/`（连字符）是历史 codegen 死代码目录，Python 无法 import 连字符目录名，MUST NOT 重建。新增 system_telemetry 相关模块 MUST 放在 `src/zephyr/infrastructure/system_telemetry/`（下划线）下。
- **pre-commit 阻断**：`gate-contract-physical-path` 钩子（[.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)）在 `cross_layer_contracts.yaml` 变更时触发 [`check_contract_physical_path.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_contract_physical_path.py)，检测 `physical_path` 指向连字符目录（如 `system-telemetry`）→ hard block (exit 1)。
- **capability 反查**：`capability_canonical_file_registry.yaml` 已登记 `system_telemetry_metrics_collector` / `system_telemetry_logs_sink` / `system_telemetry_traces_span` / `system_telemetry_health_probe` 四条能力，canonical 均指向 `src/zephyr/infrastructure/system_telemetry/` 下对应文件。新 AI 想做"遥测指标采集/日志持久化/链路追踪/健康探针"前，CapabilityLookup 会反查阻止重复造轮子。
- **observability/ 模块边界**：[src/zephyr/infrastructure/observability/](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/observability/) 仅含 `notifier` + `trace_decorator` 两个模块，不再有 `contract_metrics.py` / `health_probes.py`（已作为 codegen 死代码删除）。新 AI 不要在 observability/ 下重建这两个文件。

**路径命名约束（全仓库治本，2026-06-28）**：
- **下划线唯一合法**：`docs/02_enterprise_architecture/` 下的目录名 MUST 使用下划线：`architecture_model/`（不是连字符 `architecture-model/`）。
- **历史病根**：路径重命名（连字符→下划线）时漏改 48 个 .py 文件，导致 `gate-c2-contract-code-drift` 钩子空跑数月（找不到文件就 WARN 跳过返回 PASS），`check_contract_code_drift.py` 的 `_REPO_ROOT = parents[3]` 也少算一层。本次治本：48 文件机械替换 + `_REPO_ROOT` 改为 `from _shared.constants import REPO_ROOT` 真源常量 + 基线重新冻结。
- **pre-commit 防复发**：`gate-path-naming` 钩子（[.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)）用 pygrep 检测 .py 文件中含 `architecture-model` → hard block。新 AI 不要在 .py 文件中写连字符路径，MUST 用下划线 `architecture_model`。
- **REPO_ROOT 真源唯一**：scripts/ 下脚本 MUST `from _shared.constants import REPO_ROOT` 获取仓库根常量，禁止 `Path(__file__).resolve().parents[N]` 自行推算（易错且违反 SSoT）。

**P3 遗留项登记**（第二轮第一性原理审查 2026-06-28）：

> **本节是 P3 第二轮审查后的遗留项硬约束。** 任何 AI 在涉及 code_context indexer 或 health_probes 修复前必须先读本节。
> 真源：原 `docs/_working/p3_t1_code_context_indexer_task_card.md` + `docs/_working/health_probes_stub_disposition.md`（_working/ 临时任务卡，已按 TTL 清理；本节为唯一留存真源）

#### 遗留项-1：code_context indexer 暂缓施工

- **状态**：Suspended（暂缓施工，消费方为零）
- **前置条件**（满足任一方可重新评估）：
  1. CE 接入 VMS：[context_engine.py](file:///d:/ZephyrAlpha/src/zephyr/shared/context/context_engine.py) 从 stub 升级为真实接入 VMS/hybrid_retriever
  2. Agent 增加 code_search 工具：autonomy_core 的 Agent 工具集新增显式消费 code_context collection 的工具
- **施工硬约束**（解除暂缓后若施工必须遵守）：
  1. writer 路径必须用 `col.upsert + 确定性业务 id`，**禁用** [`collection_manager.py`](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/collection_manager.py) 的 `write_with_provenance()` 方法（`col.add + uuid` 路径，会制造 90 天重复垃圾）
  2. AST 分块必须扩展 [chunk_strategy_router.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/chunk_strategy_router.py) 的 `_ast_aware_chunk` 方法，**禁用**新建独立分块函数
  3. AST 解析必须复用 [symbol_index.py](file:///d:/ZephyrAlpha/src/zephyr/gov_code_quality/code_dedup/symbol_index.py) 的 `ast.parse + ast.walk` 模式
  4. GATE-CODE-CONTEXT reconciler 仅在消费方就绪后注册，避免死代码
- **替代方案**：L1 IDE 场景已由 trae `SearchCodebase` 工具覆盖（语义搜索 + 实时代码库索引，覆盖 src/zephyr/，零成本零维护）
- **新 AI 警告**：勿尝试"修复"或"实现"本 indexer——在消费方为零时建 indexer 是往黑洞灌数据，违反 RULE-THREE 功能价值审判

#### 遗留项-2：health_probes database 探针治本

- **状态**：务实搁置（stub 已降级 Maturity=prototype + 行内注释标记，不修不删）
- **诚实定位**：本搁置是**务实搁置（pragmatic deferral）非治本（root-cause fix）**。真正的治本需要修复 HealthAggregator 调用方 + 补 wal_checkpoint_lag 采集器 + 补 API 消费者
- **搁置理由**：P3-T4 裁定 PG 健康检查真源迁移至 `verify_schema_health.py` 校验4（事件驱动，pre-commit），完整修复 health_probes 会违反 trae_053 常驻监控禁令
- **触发条件**（满足任一可重新评估）：
  1. 项目部署到生产环境，需要常驻健康监控（trae_053 可能有例外条款）
  2. verify_schema_health.py 校验4 无法覆盖某些运行时场景（如 WAL 复制延迟）
  3. 出现 API 消费者需求（如 dashboard 展示健康状态）
- **新 AI 警告**：勿尝试"修复"此 stub——它是项目治理层选择事件驱动路线后留下的协议层化石，修复会违反 P3-T4 裁定。PG 健康检查真源在 `verify_schema_health.py` 校验4

#### 遗留项-3：write_with_provenance 治本（已治本，2026-06-28）

- **状态**：已治本（5 阶段全部完成，8 commits）
- **问题本质**：[`collection_manager.py`](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/collection_manager.py) 的 `write_with_provenance()` 方法 `col.add + uuid` doc_id 路径是 VMS 全局设计缺陷，影响所有 HOT collection（decisions/lessons/knowledge/rules/code_context）。同一内容 commit N 次堆 N 份重复 doc，TTL 到期才清理
- **正确范式**：原 KB 仓储层 `_upsert_vector`（`src/zephyr/intelligence/model_evaluation/`，已随 KB 系统于 2026-07 退役删除）的 `col.upsert + 确定性业务 id`（同 id 覆盖，零垃圾）
- **治本动作**（8 commits）：
  1. S1 `6797764c`：write_with_provenance 加 doc_id 入参 + col.add→col.upsert
  2. S2A `6eb1019c`：vector_bridge 5 处补确定性 doc_id
  3. S2B `fd80aaa5`：retrieval_feedback 2 份 + vms_memory_backend 补 doc_id
  4. S2C `dc7a9925`：mcp + infrastructure vector_memory_server 补 doc_id 透传
  5. S2D `2d513d37`：sync_engine + memory_writer + context_ingest 补 doc_id
  6. S3.0 `12c522e9`：integration 版缺陷修复（COLLECTION_ALIASES + datetime import + snapshot_backup 完整实现）
  7. S3.1 `306dbb2f`+`01377504`：governance/vector_memory 整包删除 + 91 处 import 重定向 + context_ingest 移植
  8. 风险B `548e8638`：write_failure_pattern 提取稳定 root_cause 作 pattern_text（治本内容哈希无效问题）
- **真源声明**：integration/vector_memory/ 是 VMS 唯一真源；governance/vector_memory/ 已删除（2026-06-28）
- **遗留子项**：已全部治本（2026-06-28 补充施工）——(1) faiss_collection_manager.write_with_provenance 死代码已删除（零调用方，FAISS 启用时按 CollectionManager 真源签名重新实现）；(2) test_vms_full_e2e.py 破损冗余测试已删除（VMS API 测试由 test_vms_lifecycle.py 22 测试覆盖，FAISS 测试由 benchmark_vms_e2e.py + benchmark_vms_v2.py 覆盖）；(3) 蓝图 `write_with_provenance` 签名已同步补 doc_id 参数
- **新 AI 警告**：
  1. 勿重建 governance/vector_memory/ 目录——它是已删除的漂移副本，integration/vector_memory/ 是唯一真源
  2. 勿补全 faiss_collection_manager.write_with_provenance——它是零调用方死代码，FAISS 启用时按 CollectionManager 真源签名重新实现（勿在 FAISS 未启用时提前补全）
- **pre-commit 防复发**：`gate-vms-ssot` 钩子（[.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml)）三重检测——① 检测 staged 文件路径前缀 `src/zephyr/governance/vector_memory/`（大小写不敏感）→ hard block (exit 1)，治本 SSoT 双向漂移防复发；② AST 扫描 `src/zephyr/integration/vector_memory/` 下 .py 防重建 snapshot 方法（详见遗留项-4）；③ AST 扫描防重建 `write_with_provenance` 方法（faiss_collection_manager.py 死代码防复发）

#### 遗留项-4：VMS 快照功能删除治本（已治本，2026-06-28）

- **状态**：已治本（snapshot 功能整体删除——从"修 bug"升级为"删功能"）
- **问题本质**：[index_health_monitor.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/index_health_monitor.py) `snapshot_backup` 三重缺陷叠加：(1) 目标路径在源路径内 → copytree 递归自复制 → 30GB 膨胀；(2) 无 max_snapshots 清理 → 无限堆积；(3) R4 风险被高估（chromadb 1.5.8 SQLite ACID+WAL 已应对断电，R4 审计 6 盲点 F1-F6 与数据损坏无关）
- **第一性原理裁定**：元问题"VMS 需要本地 snapshot 备份吗？"→ 不需要。R4 被 ChromaDB SQLite ACID+WAL 覆盖；snapshot 零消费方（只写不读，无 restore 实现）；死代码（vms_snapshot_backup.py import 断裂）；30GB 灾难根因
- **治本动作**（删除而非修复）：
  1. 删除 [index_health_monitor.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/index_health_monitor.py) 的 `snapshot_backup()`/`_cleanup_old_snapshots()`/`cleanup_snapshots()` 三方法 + unused imports（shutil/Path）
  2. 删除 [in_process_vector_memory.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/in_process_vector_memory.py) 维护线程的 `snapshot_backup()` 调用
  3. 删除死脚本 `scripts/governance/vms_snapshot_backup.py`（import 断裂）+ manifest/naming 白名单条目
  4. 更新蓝图 [blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_knowledge/vector_memory/blueprint.md) / 治理脚本 / 测试（移除所有 snapshot 声明，R4 缓解改为"ChromaDB SQLite ACID+WAL 防断电 + auto_repair()"，删除虚构的"完整性校验/幂等重建/回放重写"声明）
  5. 删除 `data/vector_db/_snapshots/` 30GB 递归垃圾（.NET `\\?\` 前缀瞬间清完 334 层嵌套）
  6. [in_process_vector_memory.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/in_process_vector_memory.py) `last_daily_ts` 初始化修正为 `datetime.now(UTC).timestamp()`（修启动即触发 bug，独立于 snapshot 删除）
- **新 AI 警告**：勿重建 snapshot 备份功能——R4 已被 ChromaDB SQLite ACID+WAL 覆盖，snapshot 是冗余的且是 30GB 灾难根因。数据损坏恢复靠 `auto_repair()` 尝试修复，不走 snapshot（`audit_chain 回放重写` 未实现，勿虚构）
- **门禁**：GATE-VMS-SSOT（[check_vms_ssot.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_vms_ssot.py)）已扩展 AST 检测——重建 `snapshot_backup`/`cleanup_snapshots`/`_cleanup_old_snapshots` 方法名即 hard block

### 11.3 012B 5 组件第一性原理裁定记录（2026-06-28）

> **本节是 012B 数据库 v3.0 组件相关工作的硬约束。** 任何 AI 在涉及 DualDBRouter/WriteBatcher/ScriptScheduler/ScriptRegistry/ScriptExecutionLogger 时必须先读本节。
> 真源：[database/blueprint.md §组件全景](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/blueprint.md)

blueprint.md §组件全景原列 5 个"待施工"组件，经第一性原理审查（19 个问题），裁定如下：

| # | 组件 | 裁定 | 理由 |
|---|------|------|------|
| 14 | DualDBRouter | **删除** | P2 迁移完成，过渡期前提消失；由 [`get_depgraph_pg_connection()`](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py)（PG）+ [`get_db_connection()`](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py)（SQLite）双入口覆盖（无路由器，见 §11.4） |
| 15 | WriteBatcher | **暂缓**（待 L 级） | 真问题（SQLite 单写锁）但 L 级（5000+脚本）需求，当前 S 级 571 脚本无写争抢实证 |
| 16 | ScriptScheduler | **删除** | [BulkheadExecutorV2](file:///d:/ZephyrAlpha/scripts/governance/meta/_concurrency.py)（四池+熔断）已覆盖；MOD-INF-005 已有同名组件 |
| 17 | ScriptRegistry | **已覆盖** ✅ | 已由 [_concurrency.py:1292](file:///d:/ZephyrAlpha/scripts/governance/meta/_concurrency.py) ScriptRegistry 类覆盖，CT-DB-005 契约对齐现有类 |
| 18 | ScriptExecutionLogger | **暂缓**（待 M-1 级） | 571 脚本已达 M-1 下限 500，纯新增低风险，待 JSONL 查询痛点实证后启动 |

**禁止新建的文件**（违反则为重复造轮子）：
- `dual_db_router.py` — P2 完成，由 `get_depgraph_pg_connection()`（PG）+ `get_db_connection()`（SQLite）双入口覆盖
- `script_scheduler.py`（012B 范畴）— 由 BulkheadExecutorV2 + MOD-INF-005 覆盖

**暂缓清单**（待规模达标启动，不得提前新建）：
- `write_batcher.py` — 待 L 级（5000+脚本）实证写争抢
- `script_execution_logger.py` — 待 M-1 级（500+脚本，当前 571 已达）JSONL 查询痛点实证

**已覆盖清单**（不新建，扩展现有）：
- `script_registry.py` — 已存在于 [_concurrency.py:1292](file:///d:/ZephyrAlpha/scripts/governance/meta/_concurrency.py)，CT-DB-005 契约对齐

**跨文档同步修改**（已完成的断链修复）：
- [audit_orchestrator/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md)：DualDBRouter 引用改为 get_depgraph_pg_connection()（PG）+ get_db_connection()（SQLite）双入口
- [shared_core/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/shared_core/blueprint.md)：WriteBatcher 标注"暂缓待 L 级"
- [governance_automation/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_governance/governance_automation/blueprint.md) §36.4/36.5：标注暂缓条件
- `blueprint_registry.yaml`：**误删已回滚**——commit `303fb9c9b2` KB 清理误删该派生文件（导致 20+ 消费者静默降级，GAP-2 检测失效），已于 2026-08-01 从 `303fb9c9b2^` 恢复并 `sync_registry_from_blueprints.py --write` 同步至 57 条目（v2.7.11）。真源=物理 `docs/03_modules/**/blueprint.md` frontmatter，派生文件禁止手改；漂移由 GATE-21（[`validate_static_manifest_drift.py`](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py) CHECKS 第3项 dry-run）守护。详见 #ARCH-BP-REGISTRY-DELETION-001

### 11.4 数据库连接函数真源冲突治本（2026-06-28）

> **本节是数据库连接函数的硬约束。** 任何 AI 在涉及 `get_db_connection` 或 `get_depgraph_pg_connection` 时必须先读本节。
> 真源：[depgraph_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) + [db_utils.py](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) + [sqlite_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/persistence/sqlite_schema.py) + [_shared/constants.py](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py)

**病根**：P2 迁移前 depgraph 是 SQLite，`depgraph_schema.get_db_connection` 命名合理。P2 迁移后变 PG，函数名没改，与 SQLite 的 2 个同名 `get_db_connection` 冲突。文档编造"路由器"语义合理化同名冲突，但实际无路由器。

**治本前的 9 个 import 入口**（3 真实定义 + 5 re-export + 1 wrapper）：

| 函数 | 位置 | 返回 | 目标 DB | 导入点 |
|------|------|------|---------|--------|
| F1 `get_depgraph_pg_connection`（原 `get_db_connection`） | [depgraph_schema.py:1169](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) | psycopg2.conn | **PG** (depgraph) | 42 |
| F2 `get_db_connection` | [sqlite_schema.py:465](file:///d:/ZephyrAlpha/src/zephyr/governance/persistence/sqlite_schema.py) | sqlite3.conn | SQLite (governance) | 70 |
| F3 `get_db_connection`（转发到 F2，治本 2026-06-30） | [db_utils.py:35](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) | sqlite3.conn | SQLite (governance) | 13 |
| F4 `get_depgraph_pg_connection` | [constants.py:97](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py) | PgConnExecuteWrapper | **PG** (包装 F1) | 29 |

**治本措施**：
1. F1 改名 `get_db_connection` → `get_depgraph_pg_connection`（消除与 SQLite 同名冲突），保留 deprecation 别名 `get_db_connection = get_depgraph_pg_connection`（向后兼容）
2. 16 个 import 文件更新为新名
3. 删除 [blueprint.md:125](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/blueprint.md) 虚假"路由器"语义，改为真实双入口数据流
4. 标注原 `sub_blueprints/mod_inf_012b_p2_postgresql_migration.md` 的 `db_type` 路由器设计稿为"未实现"（**该子蓝图已删除**，仅保留 `c1_market_clickhouse.md`）
5. 新增 F1/F2/F3 存在性断言测试

**新 AI 警告**：
- ❌ **勿按 `db_type` 路由器设计稿补全** F3——会破坏 83 处 SQLite 导入点隐式契约
- ❌ **勿用 SQLite 入口连 PG**——`db_utils.get_db_connection` / `sqlite_schema.get_db_connection` 返回 sqlite3.Connection，连 depgraph 会报 `no such table: nodes`
- ✅ **连 PG 用** `from zephyr.governance.depgraph_schema import get_depgraph_pg_connection`（src 包）或 `from _shared.constants import get_depgraph_pg_connection`（scripts 包，wrapper 兼容 sqlite3 接口）
- ✅ **连 SQLite 用** `from zephyr.shared.utils.db_utils import get_db_connection` 或 `from zephyr.governance.sqlite_schema import get_db_connection`
- ✅ F3 已转发到 F2（治本 2026-06-30，[`db_utils.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) 用 `importlib.import_module("zephyr.governance.sqlite_schema")` 转发 `get_db_connection = _mod.get_db_connection`），不再独立定义。F3 作为 shared/utils 公共 API 层保留（避免上层 trading/orchestrator 直接 import governance.sqlite_schema 层级倒置）。12 个 F3 调用点抽查确认用显式事务（BEGIN IMMEDIATE/COMMIT/ROLLBACK），与 F2 autocommit 兼容

#### 治本完成：F3 已转发到 F2（2026-06-30 治本）

- **状态**：已治本（F3 不再独立定义 `get_db_connection`，转发到 F2）
- **治本措施**（2026-06-30）：
  1. [`db_utils.py`](file:///d:/ZephyrAlpha/src/zephyr/shared/utils/db_utils.py) 用 `importlib.import_module("zephyr.governance.sqlite_schema")` 转发 `get_db_connection` / `init_db`
  2. F3 文件头 docstring 已标注真源声明（`get_db_connection` / `init_db` 真源为 `zephyr.governance.sqlite_schema`）
  3. F3 作为 `shared/utils` 公共 API 层保留，避免上层（trading/orchestrator 等）直接 import `governance.sqlite_schema`（层级倒置）
- **调用方兼容性验证**（2026-06-30 抽查）：
  - `circuit_breaker_repo.py`：用显式事务 `BEGIN IMMEDIATE`/`COMMIT`/`ROLLBACK`，与 F2 autocommit (`isolation_level=None`) 兼容
  - `file_task_mapper.py`：只读查询 + 显式事务，兼容
  - 其余 10 个调用方同模式（显式事务控制），F3 转发到 F2 后实际运行 F2 autocommit 行为，安全
- **capability 反查**：[capability_canonical_file_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) `sqlite_db_connection` 已更新（`canonical_override` 指向 F2 `sqlite_schema.py`，F3 标记为 `re_export` sanctioned 转发层）
- **新 AI 警告**：
  - ❌ **勿新建第三个 `get_db_connection`**——违反真源唯一
  - ❌ **勿在 `db_utils.py` 重新定义 `get_db_connection`**——会破坏 F3→F2 转发治本
  - ✅ **连 SQLite 用** `from zephyr.shared.utils.db_utils import get_db_connection`（公共 API 层）或 `from zephyr.governance.sqlite_schema import get_db_connection`（真源直连）

## §灾备备份系统（MOD-INF-043）

> v2.0（2026-07-28）：restic → robocopy /MIR + CH 增量。完整内容（位置组成/触发机制/备份内容/保留策略/恢复/注意事项）见 [`scripts/backup/README.md`](file:///d:/ZephyrAlpha/scripts/backup/README.md) + [蓝图](file:///d:/ZephyrAlpha/docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md) + `dr_runbook.md`（C 类派生细节，#ARCH-AGENTS-BUDGET-RECONCILE-001 离库）。
