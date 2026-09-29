---
created: 2026-09-30
ttl: task_bound
title: 提交链全流通·E8 reconciler/auto-commit 扇出
session: st-gate-rationalize-20260929
---

# E8 — reconciler / auto-commit 扇出（挖矿册）

> 环节定义：一笔提交 **成功落地后** 的对账扇出面——post-commit reconciler 链（detached worker）、
> BatchedAutoCommitter 批 auto-commit（重入全局锁）、衍生再生（reconcile_generators）、
> 提交传送带（belt_daemon）。上游=E5 git commit 成功（gateway:2848 派发）；本环节不阻断主提交。
> 种子知识行号漂移已核实：gateway 现为 4690 行，"2781"现为 OSError 兜底段，**真实派发点=gateway:2848**；
> "1108-1165"为 async wrapper 区（gateway:1147-1175），**58 处注册实际在 gateway:1662-1913**。

## §0 自审闸

**【挖干】**。六向齐：调度链（dispatcher→async spawn→worker 主循环→registry.reconcile_for→batcher.flush→_commit_auto 重入锁）逐件有锚；58 处注册逐一清点（grep 计数=58，含 6 个 d8_doc_sync 插件经 sys.path 注入）；耗时账有双实证（单 worker 459s/22 reconciler 状态文件 + 9/24 H5 衍生扇出 597-2800s 史账）；belt_daemon 现状已盘面核实（存活）。缺口=残差 123s/笔归因未定案（继承 deep_dive_r1 附.2，列 §4 移交）。

## §1 组件全清单

| 组件 | 功能 | 锚点 file:line | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|---|
| run_post_commit_reconcile 调度器 | post-commit 总入口：非 OK 即返；ZEPHYR_RECONCILE_WORKER=1 直接返（防递归）；SYNC=1→同步；pytest→跳过；否则异步 spawn | git_commit_gateway.py:1188-1216 | commit() 成功后 gateway:2848 调用 | 调度本身≈0（async 即返） | 自动（事件触发） |
| run_post_commit_reconcile_async 公共 wrapper | sha 缺失/launch 失败→回退 sync（fail-open） | git_commit_gateway.py:1147-1175 | 同上（Stage 4 公共化入口） | 同上 | 自动 |
| launch_reconcile_async | 清死 worker（sweep）→launch 文件锁临界区→spawn | reconcile_runner.py:670-717 | 每笔成功提交 | sweep+锁≈ms 级 | 自动 |
| _launch_worker_locked | 并发上限 MAX_CONCURRENT_WORKERS=1（reconcile_runner.py:124）超限 skip；写 payload（读后自删）→pending status→spawn | reconcile_runner.py:720-766（skip 734-749） | 同上 | spawn≈100ms | 自动 |
| sanitized_spawn_env + 双 env 标记 | 剔除 GATEWAY/FORCE 授权变量（#ARCH-279 A2）；注入 ZEPHYR_RECONCILE_SYNC=1（阻断递归 spawn）+ ZEPHYR_RECONCILE_WORKER=1（阻断链重跑） | reconcile_runner.py:786-810 | spawn 前 | - | 自动 |
| worker 孵化（incubator） | 统一孵化入口登记父 PID/预期寿命 1800s/reaper 可收割；BELOW_NORMAL 降载；stdio 落 .runtime/logs/reconcile_worker_<sha>.log（S3 观测层） | reconcile_runner.py:819-848 | spawn 时 | - | 自动 |
| reconcile_worker 主流程 | detached 子进程：读 payload 即焚→status=running→构造 gateway→sync_worker 主循环→done/failed+DB 持久化 | reconcile_worker.py:66-130（模块头契约 18-52） | 被 runner spawn | **实测 459s**（22 reconciler，reconcile_status_d2446aff…json: started 1790719988/finished 1790720447） | 自动 |
| _run_post_commit_reconcile_sync / _sync_worker | 同步执行 reconciler 链（sync 回退路径/worker 主循环两态；worker 态含 batcher flush 结果核验） | git_commit_gateway.py:2379-2470 / 2472-2525 | SYNC=1 或 worker 内 | 见 H5 史账（下） | 自动 |
| ReconciliationRegistry | reconciler 声明式注册表：register/reconcile_for（trigger 匹配+priority 串行）+ _log_reconcile_results 落 DB | reconciliation_registry.py:690/740/772 | worker 主循环 | DB 写逐 reconciler 一行 | 自动 |
| _register_default_reconcilers（58 台） | 注册默认 post-commit reconciler：主体 44 台直注（gateway:1664-1795）+ backup（1797-1809）+ 6 个 d8_doc_sync sys.path 插件（readme_version 1811-1826 / requirements 1828-1843 / metric_count 1845-1860 / algo_flow 1862-1877 / agents_cheatsheet 1879-1894 / algo_flow_reverse_orphan 1896-1913） | git_commit_gateway.py:1662-1913 | gateway __init__（每进程一次，gateway:1128） | 注册≈0；运行按 trigger 子集（实证 22/58 触发） | 自动 |
| BatchedAutoCommitter | auto-commit 批量化拦截（squash N→1）：buffer 拦截 _commit_auto 返合成 OK；flush 去重+合 message 单次真提交 | batched_auto_committer.py:122-142（buffer 225-271 / flush 275-352） | reconcile_for 期间 enable，块退出自动 flush | flush 单次 git commit（走全 gate 链+锁） | 自动 |
| _commit_auto 重入全局锁 | **放大环主体**：flush→gateway._commit_auto（gateway:4235）→commit()→GlobalCommitLock 排队——worker 的衍生提交与落地主链互抢锁（deep_dive_r1 §B 候选1：32 次 lock 获取失败实证） | batched_auto_committer.py:324-334 → git_commit_gateway.py:4235 | flush 时 | 锁等待=deep_dive residual 未解释 123s/笔 主候选 | 自动 |
| F1 integrity 折批 | flush 前 rules_integrity 用 --fold 并入同批，消除独立尾笔（史账 31 笔/13.1% 死信源）；C148：DB 出库后整段跳过防回灌 | git_commit_gateway.py:2152-2228（C148 跳过 2183-2198） | flush 前 | --fold 子进程 timeout 30s | 自动 |
| commit_queue_serializer 改道 | flag ON：_commit_auto 改道 commit_queue 入队（dev 单写者不变量），2026-08-22 Owner 裁定翻开 | config/flags.yaml:94-97 | auto-commit 时 | 入队即返 | flag 门控 |
| 衍生再生 reconcile_generators | 生成器编排器：apply_*.py 实时 reconcile(source)+boot/stale 兜底；regen 全局锁（TTL 1800s，reconcile_generators.py:163-164）串行跨 source；尾事件 pending_rerun 异步补跑（795-819）；并行度 ZEPHYR_REGENERATE_WORKERS=4（:73） | scripts/governance/reconcile_generators.py:19-58/805-819 | reconciler（regenerate/drift_scan/index_generator 等）间接触发 | **史账 H5：--stale 串行扇出 597-2800s/件**（9/24 报告:229）；出窗化后为锁外/尾事件 | 自动（事件触发） |
| regen_scope 旗标 | any_worktree=出厂（spawn 照旧、锁/账/产物根钉主区）；main_only=worktree 语境只记账不 spawn（未翻） | config/flags.yaml:48-56 | regen 编排判定 | - | flag 门控（Owner 门位） |
| commit_belt_daemon | 队列常驻消费端：watchdog RDCW 事件驱动（禁轮询豁免注释 :18）、单例锁 PID+TTL600s（:85-102）、drain 经 bootstrap_drain_with_landing（k=4 池化）、心跳 30s（W5）+离线缺口检查、堵点本 3 kind 记账+告警冷却 30min | commit_belt_daemon.py:8-9/18/60-78/112-120 | pending/ 目录文件创建+租约释放事件 | drain=落地窗主体（E7 边界） | 常驻守护（事件触发，M10 豁免） |
| **belt_daemon 现状核实** | seed"ModuleNotFoundError 半瘫"为史（deep_dive_r1 §E.5/未尽.4：`ModuleNotFoundError: scripts.governance` 半瘫） | deep_dive_r1.md:140/175 | - | **盘面实证：已恢复存活**——.runtime/commit_queue/belt_daemon.heartbeat 2026-09-30 06:39 新鲜（pid 17336，30s 心跳窗） | 常驻 |
| worktree_status_snapshots | commit 成功后 worktree status 快照（best-effort，cap 200 dirty 行） | git_commit_gateway.py:2115-2150 | 每笔成功提交 | +git status 一次 | 自动 |
| 派生写入归属台账（R-04） | 每笔派生写入钉回触发会话（producer 溯源），lookup 供 CLAIM/FOREIGN-CHANGE 区分匿名外来 | git_commit_gateway.py:249-294（lookup 297-322） | auto-commit/re-register/reconciler 写入时 | 追加 1 行 | 自动 |

## §2 六向台账（按组件群）

**① reconciler 链（dispatcher→worker→registry）**
- 上游触发：commit 成功（gateway:2848）；merge finalize 同源。
- 下游消费：reconcile_execution_log 表（DB）、status 文件（.runtime/reconcile_reports/，实测 779 文件/89 status）、worker 日志（.runtime/logs/reconcile_worker_<sha>.log）、RECONCILER-HEALTH 探针。
- 输入面：payload{commit_sha/session/committed_files/message}（reconcile_worker.py:29-40）；generator_registry/各注册表真源。
- 输出面：衍生文件写盘+auto-commit buffer；warn/critical 结果落 DB+status errors。
- 真源锚：本册 §1 各行；声明框架=Ruling:100PCT-AI-GOVERNANCE P2-3（gateway:1181 docstring）。
- 耗时账：worker 全程 459s（22 台触发子集）；9/24 前 sync 时代=链在落地窗内 597-2800s/件。

**② auto-commit 批通道（batcher→_commit_auto→锁）**
- 上游：任何 reconciler 调 gateway._commit_auto。
- 下游：真 git commit（走 DCR/TTL/FPT gate+GlobalCommitLock）；flag ON 时改道队列。
- 输入：buffered files（跨 reconciler 去重保序）；输出：合并 message 单提交。
- 真源锚：batched_auto_committer.py:122-352；flags.yaml:94-97。
- 耗时账：一次 flush=一次全 gate 链+一次锁排队（重入放大环=deep_dive §B 候选1/4）。

**③ 衍生再生扇出**
- 上游：apply_* 写 DB / reconciler 触发 / boot 兜底。
- 下游：generate_*.py 产物+auto-commit。
- 真源锚：generator_registry.yaml（只读真源）；reconcile_generators.py:19-58。
- 耗时账：H5 史账 597-2800s/件（串行时代）；现=锁外+4 并行+尾事件。

**④ belt_daemon**
- 上游：pending/ 文件创建、serializer.lease 释放事件。
- 下游：bootstrap_drain_with_landing（E7）、bottleneck_ledger 记账行。
- 真源锚：commit_belt_daemon.py:8-9（MODIFY-GUARD 观察目录集）。
- 耗时账：drain 单波=k 池化落地窗；心跳 30s 线程。

## §3 缺陷与已修

1. **#ARCH-REGEN-CASCADE-001**（2026-08-05 CPU 99% 爆炸）：worker 内 auto-commit 同步递归重跑 32 reconciler→N×编排器并发→blueprint_panorama 全 300s 超时正反馈。已修：ZEPHYR_RECONCILE_WORKER=1 跳链重跑（gateway:1184-1192 + reconcile_runner.py:804-810）。
2. **递归 spawn 环**：worker 内 commit 默认 async→无限 spawn。已修：worker env 强制 SYNC=1（reconcile_runner.py:799-803）。
3. **#ARCH-279 授权变量广播**：worker 进程树带 GATEWAY/FORCE 标记。已修：sanitized_spawn_env（reconcile_runner.py:786-793）。
4. **CAND-GOVSEC-001④ launch TOCTOU**：并发计数与 spawn 之间缝隙。已修：launch 临界区文件锁+锁内写 pending status（reconcile_runner.py:712-733）。
5. **#ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001**：日志说已重生实际未重生（buffer 合成 OK 被 workspace_hygiene git restore）。已修：buffered_files()（batched_auto_committer.py:195-221）+ worker flush 结果核验。
6. **F1 独立尾笔**：post-flush re-register 31 笔/13.1% 死信源。已修：--fold 折批（gateway:2152-2228）；C148 出库后跳过防回灌（2183-2198）。
7. **pytest 僵尸 worker**（B1/R1，实测挂起残留 2h+/8 僵尸）：pytest 体内不 spawn。已修 gateway:1198-1204。
8. **worker 启动失败无 DB 痕**（#ARCH-PRE-EXISTING-DEBT-001）：已修 reconcile_worker.py:82-130 失败也持久化 RECONCILE-WORKER-BOOT。
9. **belt_daemon ModuleNotFoundError 半瘫**（deep_dive_r1 §E.5，drain 依赖坏）：**现状已恢复**（heartbeat 新鲜实证）；同段 32 次 global lock 获取失败属锁竞争，非缺陷，归 E7 串行语义。
10. **现存未修（实证 2026-09-30）**：衍生 flush 被 M1.2 reroute 预检拦截→batch 记 COMMIT_FAILED 且 buffer 清空（reconcile_status_d2446aff…json errors 两条 flush_status=COMMIT_FAILED 实证）——衍生变更滞留工作区，靠下一轮 reconciler 重试；语义可接受但死信面需观察。

## §4 待办移交

1. residual ~123s/笔 归因定案：全局锁等待 vs 对账扇出，需落地侧逐相位插桩（deep_dive_r1.md:172 附.2）——插桩后潜在回收 ~120min/天（:160）。
2. regen_scope 仍出厂 any_worktree：main_only 翻转属 Owner 门位（flags.yaml:48-56），建议 main_only 实弹评估。
3. 衍生批 flush 被 reroute 预检拦截的观察项：统计 flush_status=COMMIT_FAILED 频率（status errors 字段），若成常态需给衍生批专用准入。
4. worktree_status_snapshots.jsonl 已 25.2MB（gate_audit），append_audit_jsonl 50MB 轮转阈值将首触，验证轮转段检索路径。
5. belt_daemon 修复后吞吐复测（deep_dive_r1.md:175 附.4）：对比专窗 10.7 笔/h 基线。
6. reconciler 名册 58 台中 6 台 d8_doc_sync 插件为 ImportError 兜底注册——插件目录改名会静默缺员，仅 warning（gateway:1808-1913 各 except），建议纳入名册漂移 reconciler 触发面。
