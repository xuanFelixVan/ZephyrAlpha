---
ttl: task_bound
title: reconciler 事件触发链完整性挖矿（S11 治理侧上游）
session: st-qoder-t1a-20260915
date: 2026-09-17
parent: S11_assembled_backtest
lane: H
---

# 挖矿节点：reconciler 事件触发链完整性（父环节 S11 整装回测 / 治理侧上游）

> 挖矿日期：2026-09-17 ｜ 会话：`st-qoder-t1a-20260915` ｜ 车道：H ｜ 唯源骨架：`S11_assembled_backtest/nodes/`
> 本节点只回答一个问题：**这个仓库里叫「reconciler / 对账」的东西，究竟被什么事件触发、那条事件线有没有真接上、没接上时什么东西在无声变旧**。
> 方法：宪章 §6 六向寻路 + 只读现网取证（`reconcile_execution_log` 真库查询、`.runtime` 产物 mtime、Windows 计划任务只读查询、trigger 谓词纯函数实测）。
> 全部结论锚定 `file:line` 或现网数字；不可证处一律写「未实证 + 判决命令」。探测件（只读，零写入）在 `.runtime/tmp/mining_reconciler_20260917/`。
> **产出=数据，不是施工指令**；采纳与排期归主力会话（宪章 §9.11）。
> **明确不重复**：reconciler 头注入器（`src/zephyr/governance/audit/reconciliation_registry.py:3388 _module_id_inject_header`——重复 `[TTL]` 头 / 幻影 module_id / 落点槽写散文）为已在册开放项（`#ARCH-325` 邻位，登记于 `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml`），本节点仅在 §1.9 作为已知残余引用，不再取证、不提修法。

---

## 1 现状盘点

### 1.1 事件链拓扑（宣称的骨架，先立靶）

| 层 | 实现 | 锚点 | 实测状态 |
|---|---|---|---|
| 事件源 | `GitCommitGateway.commit()`（唯一合法提交入口）→ post-commit 挂点 | `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:2200`（调用 `_run_post_commit_reconcile`） | 活（36d 内 `post_commit` 629 行 + `post_commit_async` 40,312 行） |
| 事件载荷 | `committed_files` 谓词 `spec.trigger(files)`，按 `priority` 升序执行 | `reconciliation_registry.py:627-857`（`reconcile_for`）；排序 `:623` | 活，但**谓词入参口径不统一**（§1.5） |
| 执行体 | 默认异步：spawn 分离子进程 `python -m zephyr.governance.audit.reconcile_worker --payload <path>`；`ZEPHYR_RECONCILE_SYNC=1` 强制同步 | `git_commit_gateway.py:801`（async 默认）、`:816-826`、`reconcile_runner.py:724-757`（payload 原样落 `committed_files`） | 活 |
| 心跳/僵尸 | 每 gate 前 + 执行期每 120s 心跳；`_STALE_THRESHOLD_SECONDS=1800` 扫尸 | `reconciliation_registry.py:719-762`；`reconcile_runner.py:255,305,385` | 活（36d 内 330 条 `post_commit_async_stale` 扫尸记录） |
| 观测面 | `data/databases/governance.db` 表 `reconcile_execution_log`；两条横幅 + 一个 pre-commit gate | `:995 _log_reconcile_results`、`:1456-1496`、`:1555-1620`、`src/zephyr/gov_enforcement/commit_gates/reconciler_health_gate.py:8-13` | 活但**只覆盖 4 个动作中的 2 个**（§1.6） |
| 派生件旁路 | 生成器链（26 件）事件：`apply_*.py` 写库→`reconcile(source)`；`.git/hooks/post-commit` YAML 变更→`reconcile_stale`；`boot_hooks` 启动→`reconcile_stale` | `scripts/governance/reconcile_generators.py:4`（[CONSUMERS]）；`.git/hooks/post-commit` POST-COMMIT-YAML-REGEN 块；`src/zephyr/trading/boot_hooks.py:371-373` | 事件线**接通**，但下游恒失败（§1.7） |

宪章约束（本次验真的唯一尺子）：**永久系统四要素之「事件触发」——reconciler 必须由事件触发，禁 cron / Timer / sleep-loop**（`docs/_working/full-auto-chain/kimi_deep_mining_charter.md` 所属体系之宪章 §9 第 3 条）。机械执行面：`src/zephyr/gov_enforcement/commit_gates/perm_trigger_gate.py:8`——只硬阻断 **staged 新增（diff-filter=A）** 的 `.py` 且带 `[TTL] permanent` 且含时间触发模式且无事件订阅者；AST/读文件失败 fail-open。豁免词表：`# noqa: m10-time-trigger`（实测 **68** 处）、`# noqa: m11-perm-manual-legitimate`（实测 **122** 处），合计覆盖 **180** 个文件。

### 1.2 观测面真值（全库，测量时刻 2026-09-17 06:2x 本地）

表 `reconcile_execution_log`：**72,481 行**，时间跨度 **2026-08-11 20:15:03 → 2026-09-16 21:56:31（36 天）**，**62 个 distinct `gate_id`**。保留策略 `DEFAULT_RETENTION_DAYS = 180`（`:440`）⇒ **36 天是数据真实年龄，不是被清的结果**，故「从未触发」类结论一律限定在 36 天窗口内。

| 维度 | 实测分布 |
|---|---|
| action | clean 37,303 ｜ **critical_warn 19,656（27.1%）** ｜ warn 9,394 ｜ auto_committed 5,998 ｜ **error 127** ｜ emergency_commit 3 ｜ **block_next 0** |
| trigger_source | post_commit_async 40,312 ｜ **watchdog_daemon 31,024（42.8%）** ｜ post_commit 629 ｜ post_commit_async_stale 330 ｜ post_commit_worktree 151 ｜ pytest 10 ｜ pre_commit_gate 6 ｜ emergency_commit 3 |

**全链单批样本**（commit `6a0eca4700`，2026-09-16 21:52:17，改动 6 个 `src/**/*.py`）：status 文件 `reconcilers_total=34` → DB 落 **29 行**（差值 5 = `action=skip` 不落库，`:1033` 注释「skip 结果不记录」+ `:1086` 过滤码），执行尾端为 `GATE-WORKSPACE-HYGIENE(890) → GATE-REMEDIATION-PROGRESS(900) → RECONCILE-WORKER-BOOT`。**priority>900 的两个已注册 reconciler 一行都没有**（§1.5 给出机理）。

### 1.3 清点表 A：注册式 post-commit reconciler（治理面，抽样 24 个代表，其余按族归并）

列义：**真触发事件** = 谓词实际可满足的事件（不是文档宣称）；**最近实测运行** = 该 gate_id 在 `reconcile_execution_log` 的最大 `logged_at`（UTC）。

| reconciler（gate_id） | 真触发事件 | 触发生产者 file:line | 36d 行数 / 最近实测运行 | 写什么 | 它不跑时谁的读数坏 |
|---|---|---|---|---|---|
| `GATE-TMP-CLEANUP` | 任意 commit（宽谓词） | `git_commit_gateway.py:1275` 起注册批 | 1,771 / 09-16 21:54:57 | `tmp/` 删除 | TTL 台账；无直接下游读数 |
| `GATE-RUNTIME-CLEANUP` | 任意 commit | 同上 | 见 §1.2 | `.runtime/` 删除 | 同上 |
| `GATE-DEPGRAPH-OPS` | 任意 commit（10min 冷却 `:2374,2386`） | `reconciliation_registry.py:2374-2407` | 795 / 09-16 21:52:17 | depgraph PG 节点/边 | 全仓依赖查询（`SearchKnowledge`/gate 依赖面） |
| `GATE-BLUEPRINT-FRONTMATTER-SYNC` | blueprint/frontmatter 文件变更 | registry 工厂 + `:2644-2653` 冷却 | 802 / 09-16 21:52:17 | 自动提交头同步 | blueprint 检索、`[CONSUMERS]` 计数 |
| `GATE-BLUEPRINT-CODE-INDEX-SYNC` | 代码索引输入变更 | `:2820-2845` | 见批样本 | code-index | 架构查询 |
| `GATE-DRIFT-SCAN` / `GATE-DRIFT-FIX` | 任意 commit | registry 工厂 | 见批样本（warn） | 审计 findings 升级 | 治理看板 |
| `GATE-BLUEPRINT-ID-LEGACY` | 头文件变更 | registry 工厂 | 见批样本（warn 93 违规） | 报告 json | 蓝图 ID 三轨口径 |
| `GATE-PATH-TREE` | 目录结构变更 | `:5821` 合成族 | 1,359 / 09-16 21:54:57 | path-tree 派生文档 | EA 树 |
| `GATE-MODULE-ID-RECOMMEND` | 无头文件 | `:3474`（spec `:3537`，priority 160） | 1,004 / 09-16 21:52:17 | 推荐（曾 auto_committed） | module_id 台账 |
| `GATE-ASSET-INDEX` | 资产清册输入变更 | `:7071`（注释：原设计**无自动触发**，靠手动 bootstrap）+ `:7155` 子进程调用 | 675 / 09-16 21:52:17 | unified-asset-index | 资产口径消费方 |
| `GATE-REGISTRY-SYNC` | 注册表索引/基线变更 | `:6406` 合成 | 744 / 09-16 21:52:17 | registry_master_index | ROOR 一致性 |
| `SECRET-REGISTRY-DRIFT` | **恒真**（`.env` gitignored，`:1357-1359` 裁定#287 priority 216） | `git_commit_gateway.py:1357-1359` | 29 / **首行即 09-16 16:45:32**（新上线） | 不写文件，只告警 | 密钥登记台账 |
| `GATE-DELETE-AUDIT` | 删除类 commit | `:5417` 合成（2 子） | 1,714 / 09-16 21:54:57 | 删除审计 | ops_guard 追溯 |
| `GATE-REGENERATE` | 域文档/arch-model/manifest | `:5821` 合成（3 子） | 1,533 / 09-16 21:54:57 | 派生文档 auto-commit | S11 上游文档 |
| `GATE-RULE-AUDIT` | 规则目录/规则文件/ARCH 引用 | `:6206` 合成（3 子） | 1,721 / 09-16 21:54:57 | rule_catalog/perception_index | AI 感知索引 |
| `GATE-INTEGRITY-AUDIT` | 规则完整性/网关审计/AGENTS 引用 | `:6780` 合成（3 子） | 1,813 / 09-16 21:54:57 | 完整性基线 | 防篡改链 |
| `GATE-TTL-DRIFT-INCREMENTAL` | 文档 TTL 面 | registry 工厂（`:8` 头注记 #73 起自动） | 979 / 09-16 21:54:57 | TTL 增量校验 | 退役审计 |
| `GATE-WORKSPACE-HYGIENE` | 任意 commit（priority 890） | `git_commit_gateway.py:1378-1380` | 1,744 / 09-16 21:52:17 | `git restore` 还原 | 工作区洁净度 |
| `GATE-GIT-PERFORMANCE-MONITOR` | 任意 commit（870） | `:1370-1371` | 见批样本（warn 计时递增） | 无 | 性能趋势 |
| `GATE-COMMIT-GW-ABUSE-MONITOR` | 任意 commit（875） | `:1373-1374` | 见批样本（warn health_score=0.239） | `commit_gateway_abuse_monitor_*.json` | 网关滥用面 |
| `GATE-ERROR-PATTERN-CONSUMER` | 任意 commit（880） | `:1376-1377` | 见批样本（clean） | `.runtime/ai_error_patterns/aggregated_patterns.json` | 可防性分层 |
| `GATE-REMEDIATION-PROGRESS` | 任意 commit（900） | registry 工厂 | 1,813 / 09-16 21:54:57 | 清偿进度 | 欠账看板 |
| `GATE-YAML-SYNC` | YAML→depgraph 规则 | registry 工厂 | **709 行 / 其中 127 行 `action=error`**，最后 error 09-16 15:18:38 | depgraph 规则 | 规则→图一致性（§1.6-R） |
| `GATE-WORKTREE-DRIFT-WATCHDOG` | post-commit ensure-daemon **+ 60s Timer 自循环** | `git_commit_gateway.py:1393-1397`；`worktree_drift_watchdog.py:90`（`_SCAN_INTERVAL=60`）、`:1402 while True:`、`:1420 time.sleep`、`:17` m10 豁免 | 32,580 / 09-16 21:56:31（**其中 31,024 行来自 daemon 定时器，占全库 42.8%**） | 漂移快照 | 工作区陈旧覆写防线 |
| `RECONCILE-WORKER-BOOT` / `RECONCILE-WORKER-STALE` | worker 自检 | `reconcile_worker.py:46-50`；`reconcile_runner.py:255,305` | 1,783 / 09-16 21:55:05 与 330 / 09-16 20:47:43 | status 文件 | 链路自身可观测性 |

**36 天零行的已注册 gate（实测 3 个，全窗口 0 行）**

| gate_id | 注册点 | trigger 谓词 | 判定 |
|---|---|---|---|
| `GATE-DEAD-PUBLIC-WRAPPER`（priority 950） | `git_commit_gateway.py:1381-1383` | `dead_public_wrapper_reconciler.py:302-304` 裸 `f.startswith("src/")` | **谓词恒假**（§1.5 实证明）→ 死注册 |
| `TRANSLATION-COVERAGE`（priority 951） | `git_commit_gateway.py:1384-1386` | `translation_coverage_reconciler.py:341-343` 裸 `startswith("src/" 或 "scripts/")` | 同上 → 死注册 |
| `DEAD-QUEUE-RETIREMENT`（priority 795） | `git_commit_gateway.py:1400-1406` | `dead_queue_retirement_reconciler.py:47 + :286`，前缀含 `.runtime/commit_queue/`（gitignored）与本模块自身源码 | 绝对路径口径下恒假；即便相对口径也只剩「改自己才触发」的自指事件 |
| `GATE-VOCAB-CHANGE`（`reconciliation_registry.py:4014/4146`） | 注册在册 | `:4055-4063` 用 `_rel_path` 归一后精确匹配 `ttl_vocabulary.yaml` | 谓词**正确**；事件在窗口内不存在——该 YAML 最后一次 commit = **2026-07-23 23:08:50（1f172f3224）**，早于窗口起点 19 天 |
| `GATE-SESSION-LOG-INDEX`（`:7711/7841`） | 注册在册 | `:7764-7771` 归一后匹配 `session_logs/**/*.yaml` | 谓词正确；`session_logs/` 最后一次 commit = **2026-07-24 02:32（5f85fbff0d）**，全目录最新会话文件 = `2026/05/session-20260508-001.yaml` ⇒ 上游事件本身已断 4 个月（§1.7-D） |

### 1.4 清点表 B：钱路上的「对账件」——**没有事件生产者**（用户指定的 P0 自欺面）

| 件 | 头宣称（file:line） | 真实调用方（全仓检索） | 结论 |
|---|---|---|---|
| `src/zephyr/position/position_reconciler.py` | `:8` INVARIANTS「事件触发:ExecutionReport到达时自动对账(**禁止时间触发**)」；`:5 [CONSUMERS]` **空**；`:7 production`；`:16 permanent` | 事件入口 `handle_execution_report`（`:80`）**src 内零调用方**；仅 `tests/e/test_e_position_reconciler.py:16`、`tests/rollback/test_rollback_position_reconciler.py:13` | **宣称的事件生产者不存在**。执行回报到达时不会发生任何对账；`production`+`permanent` 标签与之并存 |
| `src/zephyr/ex_core/eod_reconciliation.py` | `:5 [CONSUMERS]`「运行时装配批(盘后 15:30 任务链/日终调度接线)」；`:7 evolving`；`:15 permanent`；无 `__main__` | **代码零引用**（仅 `capability_canonical_file_registry.yaml:5897`、`module_translation_registry.yaml:34`、`architecture_model/contracts/error_code_registry.yaml:2562-2563`、`docs/03_modules/_domain_execution_core/algo_flow/eod_reconciliation.yaml` 四处登记/文档） | 幻影消费者：宣称的装配批不存在，日终对账无可达入口 |
| `src/zephyr/trading/three_way_reconciliation.py` | `:5`「盘后三向对账调度 / 告警路由接线 / 未匹配台账跟进工作台」；`:6 imported`；`:7 production`；无 `__main__` | 零 import；仅 `config/governance_operations_map.yaml:2156-2157`、`config/trading_decision_map.yaml:2472,2476` | 同上（三向对账在生产链上不可达） |
| `src/zephyr/orchestrator/execution/reconciliation_loop.py` | `:13 [CONSUMERS]` 空；`:15 production` | 仅 `src/zephyr/orchestrator/execution/__init__.py:20` re-export | 「对账循环」无驱动者 |
| `src/zephyr/feedback_loop/gates/blueprint_code_reconciler.py` | `:5` 空；`:7 production` | 零 import | 同上 |
| `src/zephyr/trading/recon_runner.py` | `:6 [CONSUMERS]`「57号文日循环SOP（**人工/后续调度触发**）」；`:7 [STARTUP] manual`；`:8 production` | 自述即 manual | 诚实的 manual 件，但挂着 `production` |
| `src/zephyr/trading/post_settlement_pipeline.py` | `:22-23` 自述「本模块**不实际挂 APScheduler 生产任务**」；`:9` INVARIANTS「函数级注册不挂生产 APScheduler 任务」；`:44 POST_SETTLEMENT_CRON="30 15 * * *"` | `build_post_settlement_jobs()`（`:76-98`）唯一调用方 = `tests/trading/test_post_settlement_pipeline.py:37,45`；执行入口 `run_post_settlement_pipeline` 由 `scripts/run_post_settlement.py:87,481` 调 | 函数级声明无人消费；生产触发靠 **Windows 计划任务**（§1.4.1） |
| `src/zephyr/governance/architecture_governance/blueprint_reconciler.py` | `:5 [CONSUMERS] zephyr.infrastructure.escalation` | `src/zephyr/infrastructure/` 下无 `escalation*`（ls 实测为空） | **幻影消费者**（声明的模块不存在） |
| `src/zephyr/infrastructure/asset_inventory/reconciler.py` | `:5 [CONSUMERS]` 空；`:6 [STARTUP] manual`；`:7 production`；有 `__main__` | 头未更新，实际已被 `make_index_generator_reconciler` 事件化：`reconciliation_registry.py:7071`（注释「原设计无自动触发，依赖手动跑 python -m zephyr.infrastructure.asset_inventory bootstrap」）+ `:7155` 子进程调用 | **健康**（仅头陈旧，见 §附录 A 正面清单） |
| `src/zephyr/ex_core/position_reconciler.py`（同名不同物） | `:5 [CONSUMERS] zephyr.ex_core.trading_session; zephyr.governance.adapters.simulation_broker` | 实际 importers：`eod_reconciliation.py:47`、`risk_layer_orchestrator.py:143`、`recon_runner.py:78`、`scripts/start_paper_session.py:99` | 这才是活的那一个 ⇒ 与 §1.4 第一行构成**同名双件**（`position/` 死、`ex_core/` 活） |

#### 1.4.1 结算对账的 cron 触发器：**注册了，且每次都没进业务逻辑**（实测）

- 唯一生产触发：Windows 计划任务 `ZephyrAlpha_PostSettlement`，工作日 15:30。注册器 `scripts/register_post_settlement_task.ps1:42`；`config/resource_profile_registry.yaml:1485-1502` 登记 `task_id: sch_post_settlement`、`window_type: cron`、`window_expr: 30 15 * * 1,2,3,4,5`、`schedule_truth_source: scripts/register_post_settlement_task.ps1`。Owner 2026-09-15 全自动指令批准挂钟触发（ps1 `:11-16` 注释、`scripts/run_post_settlement.py:5`）。
- 现网只读取证：`Get-ScheduledTaskInfo -TaskName ZephyrAlpha_PostSettlement` → **`LastRunTime 2026/9/16 15:30:00`，`LastTaskResult 2`**，`NextRunTime 2026/9/17 15:30:00`；同机 38 个 `ZephyrAlpha*` 任务中，PostSettlement 是唯一结果为 `2` 的。
- 出口码语义冲突即证据：CLI 自述 exit code 矩阵只有 `0/1/3`（`scripts/run_post_settlement.py:407-413, 497`）⇒ **2 不可能由业务逻辑产生**，属 argparse 用法错误退出；`parse_args` 用严格 `parser.parse_args(argv)`（`:152-168`，`trade_date` 仅 1 个可选位置参数）。
- 机理性锚点：`register_post_settlement_task.ps1:36,40` 把重定向写进 `-Argument`——`'-u "<cli>" >> "<log>" 2>&1'`，而 Task Scheduler 不经过 shell，`>>` / 日志路径 / `2>&1` 成为 python 的**字面 argv** ⇒ argparse 报「unrecognized arguments」⇒ 2。
- 交叉验证（产物侧）：`data/runtime/post_settlement_last_run.log` **不存在**（`data/runtime/` 目录清单实测无此文件），与「从未成功产生输出」一致。
- 上一次**真实**结算对账读数只存在于旧包装日志 `.runtime/logs/post_settlement.log`（mtime 2026-09-14 15:30）：`trade_date: 2026-09-14 / reconcile_status: SKIPPED / audit_status: OK / [INFO] exit_code=0`，且同批打印「券商侧未比对——降级标注」。⇒ 实测意义上的盘后结算对账最后可信运行 = **2026-09-14**。
- 顺带（不施工，仅记档）：`scripts/run_post_settlement.py:467` 仍在打印「57 号文 §3 盘后结算管线，**手动触发未挂调度**」，与已挂调度互斥；`scripts/qmt_watchdog.ps1:1` 顶着 `# [BLUEPRINT] MOD-SCRIPT-run_post_settlement | scripts/run_post_settlement.py` 的头（头挂错文件）。

> **裁定式表述（对应用户判据）**：一个「reconciler」若没有事件生产者，它就是 P0 自欺面。本节点实测：**8 件钱路/治理对账件仅有 manual 或 cron 入口**，其中 **1 件（结算）的 cron 触发器自身从未成功执行过被调体**，**4 件的宣称消费者不存在或不存在于生产路径**。

### 1.5 触发口径审计（为什么注册了却永远不跑）——本节点最大新矿脉

三段独立证据闭合：

1. **入参口径 = 绝对路径（含反斜杠）**：`git_commit_gateway.py:1953-1954` `abs_files = [os.path.abspath(f) for f in files]` → `existing = self._filter_existing_files(abs_files)` → `:2200 self._run_post_commit_reconcile(existing, ...)`；异步路径把该列表原样写进 payload（`reconcile_runner.py:757 "committed_files": committed_files`），worker 再原样交给 `reconcile_for`（`git_commit_gateway.py:1886-1891`）。
2. **谓词按相对路径写死**：`dead_public_wrapper_reconciler.py:302-304`、`translation_coverage_reconciler.py:341-343`、`dead_queue_retirement_reconciler.py:47+286` 均对入参直接 `startswith("src/")` 之类比较，未经 `_rel_path`（归一器定义在 `reconciliation_registry.py:4687-4705`，注释自陈「34 处调用点」——即归一是全仓约定，非归一是例外）。
3. **谓词纯函数实测**（只调 trigger，绝不执行 reconcile；探测件 `.runtime/tmp/mining_reconciler_20260917/probe_trigger_pred.py`）：
   - 输入 `D:\ZephyrAlpha\src\zephyr\trading\three_way_reconciliation.py`（即生产口径）：三个 gate 的 trigger **全部 False**。
   - 输入相对 `src/zephyr/trading/three_way_reconciliation.py`：前两个 True、`DEAD-QUEUE-RETIREMENT` 仍 False（其前缀一条是 gitignored 的 `.runtime/commit_queue/`，另一条是其自身源码路径）。
   - 与 §1.3 表格「36d 全窗口 0 行」互证，且解释为何 `6a0eca4700` 批次（6 个 `src/**.py`）跑到 priority 900 就收尾。

同族疑疵（**不完全归因，标未实证**）：`GATE-SCRIPTS-IMPORT-BASELINE`（`:9029-9041`）、`GATE-UNDEFINED-NAME-BASELINE`（`:9157-9172`）、`GATE-CONSUMERS-ACCURACY-BASELINE`（`:9250` 附近）同样先 `f.replace("\\","/")` 再 `startswith("src/")` / `startswith("scripts/governance/")`——绝对路径下这些主分支同样恒假，它们的全部 5/4/3 次触发很可能只来自 `"<gate 文件名>" in normalized` 兜底子串分支；但 `committed_files_summary` 仅存前 20 个文件（`:1063-1067`）故截断使归因不完备。判决命令：
`python -c` 读 `reconcile_execution_log` 中这三个 gate 的**完整**批次文件列表（同 `session_id`+`logged_at` 分组）比对是否含 `<gate>.py`；或按 §4-RC1 的谓词单测直接判。

### 1.6 失败语义：raise 是可见还是被吞？横幅能不能变红？

**结论：单个 reconciler 的异常被吞成一行 `warn`（可见但不痛）；横幅只认两种动作；`error` 动作在观测面上是孤儿。**

| 事实 | 锚点 | 实测 |
|---|---|---|
| 契约级吞异常 | `reconciliation_registry.py:25 [ERROR_CONTRACT] reconcile_for 永不抛异常`；`:15 INVARIANTS` | 成立 |
| 通用 except | `:823 + :843-855 except (Exception, KeyboardInterrupt) → logger.warning + ReconcileResult(action="warn", detail="reconciler X raised: …")` | 全窗口该形态 **99 行**；样例行：`GATE-DELETE-AUDIT` 2026-09-15 18:52:23「No module named 'zephyr.governance.audit.doc_lifecycle'」、`GATE-TMP-CLEANUP` 2026-09-15 05:26:06「No module named 'scripts.ops_guard'」，且 `:653-678` 自陈该 import 病根造成 **150 条**失败（2026-08-14 起） |
| 超时（唯一升格路径） | `:800-821 except subprocess.TimeoutExpired → action="critical_warn"` | 成立，当前活跃告警主体即此类 |
| 删除阻断 | `:826-841 DeleteBlockedError → critical_warn` | 成立 |
| 其余静默降级 | `:694`（ops_guard 不可达）、`:720/:733-734`（心跳 pass）、`:746`（arity）、`:756`（上下文注入）、`:773`、`:780-789`（dict→warn） | 均为 `pass`/`logger.warning`，无观测面留痕 |
| CRITICAL 横幅**能红，且现在就是红的** | 打印点 `:1456-1496`（文案 `:1484 "!! CRITICAL RECONCILER FAILURES DETECTED (last 24h)"`），判定 SQL `:381-391` | 实测近 24h **未 ack 且无后续 clean 自愈**的活跃 critical_warn = **9 个 gate**：`SECRET-REGISTRY-DRIFT` 30 行、`GATE-DELETE-AUDIT` 22、`GATE-REGENERATE` 14、`GATE-RULE-AUDIT` 11、`GATE-REGISTRY-SYNC` 3、`GATE-PATH-OWNERSHIP` 2、`NEW-FILE-DEPGRAPH-ENFORCEMENT` 1、`DEPGRAPH-PRE-REGISTRATION` 1、`GATE-STASH-LIFECYCLE` 1 |
| BLOCKING 横幅**当前不可达** | `:1499-1552`、`:1555-1620`（`:1603`），SQL `:452` | 全 36d `action='block_next'` = **0 行** ⇒ 四级阶梯最高档在生产中无生产者（`reconciler_health_gate.py:8-13` 的硬阻断分支等于未测路） |
| 告警自消音（自愈静音） | `:381-391 NOT EXISTS(later clean for same gate_id)`、`:406-411 backfill_auto_ack_healed`、`:1623-1687 resolve_blocks`（DELETE）、`:440` 180d 保留 | 交替 clean/critical_warn 的 gate 会周期性自我消失；worker 侧同样：`RECONCILE-WORKER-STALE` 330 行**全部记 `action=clean`**，detail 形如「self-heal: orphaned worker reaped (dead pid=25816, died 2032s ago, threshold=1800s, commit_sha=817e6e33…)」（实测行 2026-09-16 20:47:43）；`RECONCILE-WORKER-BOOT` 1,783 行 detail 亦自述「auto-selfheal of prior RECONCILE-WORKER-BOOT critical_warn」 ⇒ **整批 reconciler 未跑（worker 被 reap）在观测面上表现为「干净」** |
| 读侧 fail-open | `:1450-1453`、`:1549-1552`（查询异常 → `return []`）；`reconcile_runner` [ERROR_CONTRACT] `query_reconcile_status` 失败 → `status=unknown`；`reconciler_health_gate.py:8`（governance.db 缺失/查询失败放行） | 三处均为「看不见就是健康」 |
| **`error` 是观测面孤儿** | 生产者 `:3808, :3836 action="error"`（`GATE-YAML-SYNC`）；横幅/ack/gate 的 SQL 只过 `critical_warn`（`:384,397,402,414,425`）与 `block_next`（`:452`） | 实测 `GATE-YAML-SYNC` 709 行中 **127 行 error**，跨 **2026-08-14 13:16 → 2026-09-16 15:18（34 天）**，detail 自述「yaml sync failed 36 times (max=3, error_class=unknown), **STOPPED retry. Manual fix needed**: CH 配置文件不存在: D:\ZephyrAlpha\.runtime\commit_queue\worktree\…」 ⇒ 一个已自认放弃、要求人工修的对账件，既不红灯也不阻断 |

> 按用户指令：**本节点不尝试修复任何当前失败**；红灯降噪归维护班（banner 协议）。上表只登记可见性事实。

### 1.7 新鲜度检测：有没有任何东西在断言「不能太旧」？

- **生成器族：有，但是「代理指标」**。`_is_stale`（`scripts/governance/reconcile_generators.py:558-602`）：`yaml:` 前缀输入 → 比 mtime（`:590-601`）；纯 `db:` 输入 → 读 `.runtime/cache/gen_<name>.success` 标记（`:237-248` 写 `str(time.time())`，`OSError` 静默 `pass`；`:251-257` 读，异常返回 None），超过 `_DB_ONLY_STALE_THRESHOLD_SECONDS = 1800`（`:104`）判 stale。⇒ 对 db-only 件，**「30 分钟内有成功标记」替代了「产物与数据一致」**。
- **本次调真实 `_is_stale`（非自造比较）逐件跑 26 件**：`stale=2`（`battle_map`、`trading_decision_map`）、`output_up_to_date=4`、`db_only_fresh=19`（标记年龄 340–475 s）、**`no_input_sources=1`（`algo_flow_translation_sync`——按 `:580` 定义结构上永远「不过时」，即不可检）**。
- **事件线接通但下游恒失败（可观测、无人认领）**：`.git/hooks/post-commit` 的 POST-COMMIT-YAML-REGEN 块 → `scripts/governance/git_hooks/post_commit_regen_yaml.py`（`:200-260` spawn `reconcile_generators.py --stale`，日志落 `.runtime/logs/post_commit_regen_yaml_*.log`；`:13 [ERROR_CONTRACT] 任何异常→静默退出 0`）。实测：日志 92 份，最新 2026-09-17 04:29；其中 **81 份记录 `reconcile_stale: trading_decision_map FAILED (reason=input_newer_than_output)`**，最早 **2026-09-10 13:35:30**，成功 **0 次**，错误文本每次同一句：`in_process: ValueError: 节点未归入任何文件（检查 FILE_PLAN 前缀）: ['TDM-E-FLOW','TDM-E-L0','TDM-E-L0-01','TDM-E-L0-02','TDM-E-L0-03','TDM-E-L0-04']`。
- **具体可观测漂移（用户点名要的「生成件时间戳 vs 源最新提交」）**：`trading_decision_map` 输入 `config/trading_decision_map.yaml` mtime **2026-09-17T01:47:20**（其 9-17 当天有 3 次 commit：`dec1237903 00:08:16`、`6b44f342a1 00:18:11`、`74dc6d09ab 01:56:48`），产物族最早 mtime `docs/02_enterprise_architecture/10_trading_map/_zoomable_html/trading_map_00_panorama.html` = **2026-09-09T04:13:04** ⇒ **过时 7.9 天**；旁证：26 个 `.success` 标记里 `gen_trading_decision_map.success` **不存在**（其余 25 个在），产物目录最后一次 commit = **2026-09-08 00:12:53（caaffc56f8）**。**这是 S11 决策链直接消费的两张图之一。**
- **会话台账族：检测器存在但事件与路径都断了**。`GATE-SESSION-LOG-INDEX` 36d 0 行（§1.3）；`registry:7694` 自陈「派生脚本（`validate_session_log_index_integrity.py --generate`）**无自动触发机制**」；专职新鲜度检查器 `scripts/governance/d5_architecture/validators/session/validate_session_log_updated.py` 挂 `:7 [STARTUP] manual`（无事件生产者），且 `:62 SESSION_LOG_DIR = REPO_ROOT / ".runtime" / "session_logs"` —— 该目录**不存在**（`ls` 实测），真台账在被 git 跟踪的 `session_logs/`。实测漂移：`session_logs/index.yaml` `total_sessions: 29` / `last_updated: 2026-07-23`（磁盘提交态会话文件 **30** 件，`by_date` 索引会话键 **29** 个），未入册者 = `session_logs/2026/04/session_20260417_retrospective.yaml`；且 `session_logs/2026/` 只有 `04/05` 两个月目录（最新文件 2026-05-08）⇒ 2026-06 起 4 个月无会话台账，而唯一会把这件事亮出来的机制恰好没有事件。
- **注册式 reconciler 族：没有任何 max-age 断言**。全库无「某注册 gate_id 若 N 天未出现在日志即告警」的机制——`RECONCILER-HEALTH` gate 只看 block/critical_warn 近况（`reconciler_health_gate.py:8-13`），`GATE-REMEDIATION-PROGRESS` 看清偿维度。⇒ **「注册即死」在观测面上零成本**，这正是 §1.3 三件死注册能长期存活的结构性原因。

### 1.8 六向之外的两条口径澄清（避免误读）

- `post_commit_worktree` 151 行来自 worktree merge 路径，其文件列表**是相对 POSIX 路径**（`session_worktree.py:5538-5556 [git diff --name-only]`），但异步 worker 路径（占 95.2%）入参为绝对路径；且该 151 行所属批次的 26 个 distinct gate 中同样**没有** §1.3 的三个死 gate ⇒ 死注册在**所有已观测代码路径**上都成立。
- `trigger_source='pytest'` 10 行全部属于 `GATE-TEST-P4-1A`（测试自造 gate 混入生产观测表），量级可忽略但计入 62 distinct。

### 1.9 已知残余（引用，不重开）

头注入器（重复 `[TTL]` 头 / 幻影 module_id / 落点槽写散文）：`reconciliation_registry.py:3388 _module_id_inject_header`（邻件 `:3354`、`:3427`、`:3474`）。已在 `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml` 以 `#ARCH-325` 邻位登记。本节点仅补充一条**无害观察**：其推荐器 `GATE-MODULE-ID-RECOMMEND` 36d 内 1,004 行正常触发（最近 2026-09-16 21:52:17），即该残余属「内容质量问题」而非「不触发问题」——与本节点矿脉正交。

---

## 2 六向挖矿日志表

| 向 | 发现（内部锚点 / 外部 URL+年份） | 判定 |
|---|---|---|
| ①上游（该喂什么进来） | 事件源只有 git commit 一类：`git_commit_gateway.py:2200`。缺「DB 写入事件」「生成器失败事件」「计划任务出口码事件」三类上游——`sch_post_settlement` 出口码 2 与 `post_commit_regen_yaml` 的 81 次 FAILED 都没有回流为 reconciler 输入（§1.4.1/§1.7） | **signal** |
| ②下游（输出该喂给谁） | 观测面下游只有 2 个消费者：两条横幅（`:1456/:1555`）+ `RECONCILER-HEALTH` gate。`action=error`/`warn` 无下游（127 + 9,394 行无人读，§1.6）；死注册 gate 的「应存在下游」也无从推导 | **signal** |
| ③算法/机制（业界学界） | 见 §3 四闸对照：期望-实际调和的「控制器无周期 resync 即漏检」共识（Red Hat 2019）、GitOps 的 `OutOfSync` 显式状态机（Red Hat/OpenShift GitOps 文档，2025）、`dbt source fresheness` 的 warn/fail 双阈（dbt Labs，2026 更新）、Datadog 数据管道监控把 freshness 列为一等指标（Datadog，2026） | **signal** |
| ④后端（代码缺什么） | 缺：(a) trigger 入参口径单一化（或统一归一器）；(b) per-gate 存活断言（心跳只证明 worker 活着，不证明每个 gate 跑过）；(c) 连续失败计数升格（regen 81 次同错仍只是日志行）；(d) `_compose_reconcilers` 子件身份保留（`:4941-5009`，子件在日志中不可见，`:4986` 一个子件抛异常丢弃全部兄弟结果） | **signal** |
| ⑤前端（呈现，只登记） | 现呈现 = 终端横幅 + 需 SQL 的 DB 表。无任何「gate × 最近触发时刻」矩阵；§1.3 那张表能算出来却无处看，是本节点最便宜的一块补齐材料（登记，不施工） | signal |
| ⑥数据字段 | `reconcile_execution_log` 缺：`commit_sha`（只能靠 `session_id`+`logged_at` 反推批次）、`duration_ms`、`spec_priority`、`registered_vs_fired` 视图。列清单实测：log_id/logged_at/gate_id/session_id/trigger_source/action/detail/committed_files_summary/acknowledged_at/commit_message/error_pattern_id | **signal** |
| （补）噪音轮 | 首次生成器新鲜度探测把 `yaml:` 前缀当真实路径读 ⇒ 26 件全判「不过时」，与真 `_is_stale`（`:570-571` 剥前缀）结论相反；已推翻并用真实函数复测（§1.7） | noise（已自纠，记档） |

---

## 3 业界与开源对照（逐条过四闸）

| 外部做法（来源+年份） | A 股/本仓适配 | 判定 |
|---|---|---|
| 控制器「调和环」不指望纯事件，需周期性 resync 兜住漏事件（Red Hat《Kubernetes Operators Best Practices》2019-06）| 本仓走的是**纯事件**路线（宪章 §9.3 禁 cron/Timer），因此「漏事件」在治理面上不可被 resync 补偿 ⇒ §9.3 的代价必须有**替代物**：per-gate 存活断言。当前替代物**不存在** | 对等缺口（非立卡候选）：不是要引入 cron，而是要补「事件未发生」的可检测性 |
| GitOps 显式 `OutOfSync` 状态 + self-heal 可关可查（Red Hat OpenShift GitOps「Argo CD Applications」文档，2025-06/08 两版）| `GATE-REGENERATE`/`GATE-REGISTRY-SYNC` 的 `auto_committed` 即 self-heal；本仓已治过「buffer 成功但 flush 未提交」的假自愈（`reconciliation_registry.py:947-979`），但 `RECONCILE-WORKER-STALE` 把「整批没跑」记成 `clean` 是**另一类假自愈**：健康标签落在未执行体上 | 立卡候选（观测语义）：把「被 reap 的 worker」从 clean 升为 warn 以上 |
| 新鲜度以显式阈值声明并分级 warn/fail（dbt `freshness` 资源属性，docs.getdbt.com，2026 更新；Datadog 数据管道监控把 freshness/completeness 并列，2026-08）| 本仓唯一显式阈值是 db-only 标记年龄 1800s（`reconcile_generators.py:104`）——**它约束的是「多久没跑」，不约束「产物多旧」**；`trading_decision_map` 7.9 天旧正因如此（yaml 型只有相对 mtime 比较，无绝对上限） | 对等已有（机制存在）+ 阈值缺口（无 max-age 绝对上限、无 fail 档） |
| 「声明式注册但从未执行」的外部解法是控制器启动期打印/上报 registered-vs-reconciled 差集（controller-runtime 事件谓词文档，待验证：本次未取到可引 URL，仅由 §1.5 内部证据支撑结论）| 本仓差集**可算但没人算**（62 logged vs 注册全量，见 RC-1） | **待验证**（单来源；不作为结论承重墙） |

交叉验证满足度：§1.5 的口径缺陷由**三条独立内部证据**（代码 + 谓词实测 + 36d 零行）闭合；§1.7 的 regen 恒失败由 81 份日志 + 标记缺失 + 产物 mtime 三源闭合；§1.4.1 由计划任务出口码 + CLI 出口矩阵 + 日志文件缺失三源闭合。

---

## 4 堵点与欠账清单（RC-*；级别按后果定，验收标准必须可机械断言）

| # | 级别 | 病灶类 | 堵点（现状 + 锚点） | 可施工验收标准（可断言） |
|---|---|---|---|---|
| **RC-1** | **P0** | 静默失效（假健康） | 三个已注册 reconciler 的 trigger 在**生产入参口径下恒假**，注册即死：`dead_public_wrapper_reconciler.py:302-304`、`translation_coverage_reconciler.py:341-343`、`dead_queue_retirement_reconciler.py:47+286`；口径由 `git_commit_gateway.py:1953-1954` 决定 | ①新增参数化单测：对 `gateway._reconciliation_registry.list_gate_ids()`（`reconciliation_registry.py:865-867`）的**每个** spec，用 `os.path.abspath` 与相对两种口径各喂一份含 `src/**/*.py` 与 `session_logs/*.yaml` 的夹具，断言两口径结论一致；②DB 断言：`SELECT count(*)=0 FROM … WHERE gate_id IN (注册集全量) AND logged_at > now-14d` 必须为空（首批应暴露上述 3 件） |
| **RC-2** | **P0** | 假接线（自欺面） | 钱路对账件无事件生产者：`position/position_reconciler.py:8`（宣称 ExecutionReport 事件，入口 `:80` 零调用方）、`ex_core/eod_reconciliation.py:5`、`trading/three_way_reconciliation.py:5`、`orchestrator/…/reconciliation_loop.py:13`、`feedback_loop/gates/blueprint_code_reconciler.py:5`、`blueprint_reconciler.py:5`（幻影消费者） | 逐件二选一并可 grep 断言：接线（`grep -rn "handle_execution_report" src/ \| grep -v tests` 命中 ≥1）或降级标注（`[MATURITY] incubating` + `[CONSUMERS]` 非空即须可 import）。验收命令即该行 grep，返回非空为过 |
| **RC-3** | **P0** | 触发器自身死亡 + 无人读出口码 | 结算 cron 每次未进入业务体：`LastTaskResult=2`（09-16 15:30），出口码集合 `0/1/3`（`run_post_settlement.py:407-413,497`）不含 2；根因是重定向被当作 argv（`register_post_settlement_task.ps1:36,40`）；产物日志 `data/runtime/post_settlement_last_run.log` 不存在 | `Get-ScheduledTaskInfo ZephyrAlpha_PostSettlement` 的 `LastTaskResult -eq 0` **且** `Test-Path data/runtime/post_settlement_last_run.log` 为 True **且**该文件末行匹配 `exit_code=[013]\b`；另加一条治理断言：`resource_profile_registry.yaml` 中 `window_type: cron` 的任务须有 `last_exit_code` 回流字段（当前无） |
| **RC-4** | **P0** | 派生件恒过时（S11 直读） | `trading_decision_map` 事件线接通但生成连续失败 81 次、跨度 ≥7 天、0 成功；产物过时 7.9 天（§1.7）；错误 `FILE_PLAN 前缀`未随 YAML 新增 `TDM-E-FLOW/TDM-E-L0*` 节点更新 | ①`.runtime/cache/gen_trading_decision_map.success` 存在；②真实 `_is_stale(entry)` 对该件返回 `(False,'output_up_to_date')`；③`docs/02_enterprise_architecture/10_trading_map/**` 全部产物 mtime > `config/trading_decision_map.yaml` mtime；④失败升格：`reconcile_stale` 对同一生成器连续 ≥3 次失败必须产生一行 `critical_warn` 到 `reconcile_execution_log`（现状只 `_LOGGER.warning`，`reconcile_generators.py:650-655`） |
| **RC-5** | **P1** | 观测语义错位（假自愈） | 被 reap 的 worker（= 整批 reconciler 没跑）记 `action=clean`：330 行 `trigger_source='post_commit_async_stale'` 全为 clean（`reconcile_runner.py:255,305` + 实测 detail 文本）；boot 亦以「auto-selfheal of prior … critical_warn」自我消音 | 断言：扫尸事件写 `warn`（或更高）且**不进入** `NOT EXISTS(later clean)` 消音集；报表项「日 lost-batch 数」可查（当前 36d 有 330 次、无从统计） |
| **RC-6** | **P1** | 观测面孤儿动作 | `action='error'` 不在横幅/ack/健康 gate 任何 SQL 条件里（`:384,397,402,414,425,452`），却由 `:3808,3836` 持续产生：`GATE-YAML-SYNC` 34 天 127 行、detail 自述「STOPPED retry. Manual fix needed」 | 断言：`SELECT count(*) FROM reconcile_execution_log WHERE action NOT IN ('clean','warn','auto_committed','critical_warn','block_next','skip','emergency_commit')` = 0；或将 `error` 并入 `_check_recent_*` 族后，`GATE-YAML-SYNC` 必须出现在横幅（可复跑同 SQL 验证） |
| **RC-7** | **P1** | 档位阶梯有一档空转 | `block_next` 全 36d = 0 行 ⇒ 「最高档硬阻断」在生产中无生产者，`reconciler_health_gate.py` 的阻断分支为未测路 | 断言：至少 1 个已注册 spec 在受控夹具下能返回 `block_next` 并被 `_check_recent_blocks` 读到（现只有 `DeleteBlockedError→critical_warn`，`:826-841`）；否则应在文档/宪章侧删除该档宣称 |
| **RC-8** | **P1** | 身份塌缩（子件不可审计） | `_compose_reconcilers`（`:4941-5009`）把 N 个子 spec 塌成 1 个 gate_id（`:5002`），子件（`GATE-GHOST`/`GATE-DOMAIN-DOC`/`GATE-RULE-CATALOG`/`GATE-REGISTRY-INDEX`/`GATE-RULES-INTEGRITY`）36d 各 0 行；且 `:4986` 一个子件抛异常即丢弃全部兄弟结果并终止该合成件。5 个合成点：`:5417/:5821/:6206/:6406/:6780` | 断言：合成件在 detail 内**逐子件**留痕（现仅 `GATE-RULE-AUDIT` 类有 `[clean]… \| [warn]…` 拼接），使「子件触发率」可 SQL 计算；并加一条夹具测试：子件 A raise 时子件 B 的结果仍在 |
| **RC-9** | **P1** | 宪法口径与最大流量矛盾 | 宪章 §9.3 禁 Timer，但全库 42.8% 的 reconciler 行来自 60s 定时循环（`worktree_drift_watchdog.py:90,1402,1420`，靠 `:17` 的 `m10-time-trigger` 豁免存活）；豁免词表面实测 68+122 处 / 180 文件 | 断言（只读可查）：豁免文件清单 + 每处豁免必须绑定一条「替代事件源」说明字段，否则 `PERM-TRIGGER`（当前仅扫 staged 新增 `.py`，`perm_trigger_gate.py:8`）扩面到 ps1/计划任务面并报告 `sch_*` cron 清单（当前该 gate 对 Windows 计划任务零覆盖） |
| **RC-10** | **P2** | 导出的死工厂 | 3 个刻意未注册的工厂仍在 `__all__`：`reconciliation_registry.py:142/145/151`（对应 `GATE-ID-UNIQ:3884`、`GATE-EXEMPT-ZONE-FM:4780`、`GATE-MODULE-ID-CONSISTENCY:6798`；去注记见 `git_commit_gateway.py:1291-1293`）⇒ 以 `__all__` 为清点依据的审计会多算 3 件（也直接干扰宪章 §4.2 退役审计） | 断言：`set(__all__) ∩ 工厂名` 与 `_register_default_reconcilers` 实际注册集相等，或在 `__all__` 行内加 `[DEPRECATED-NOT-REGISTERED]` 标记并被某 gate 读取 |
| **RC-11** | **P2** | 新鲜度检测器自身无事件且看错目录 | `validate_session_log_updated.py:7 [STARTUP] manual`，`:62` 指向不存在的 `.runtime/session_logs/`；同时 `session_logs/` 自 2026-05-08 无新台账、索引 30 vs 29 漂移（§1.7） | 断言：该 validator 扫描路径改为 `session_logs/` 后跑一次退出码=1（存在未入册件）；再加 max-age：`max(session_logs/**/*.yaml mtime)` 距今 ≤ 7 天，否则 warn |
| **RC-12** | **P2** | 静默注册失败面 | 5 处 `try: … except ImportError as e: logger.warning(...)` 的 sys.path 注入式注册（`git_commit_gateway.py:1408-1418, 1423-1493`：backup/readme_version_sync/requirements_version_sync/metric_count_drift/algo_flow_translation/agents_cheatsheet）⇒ 插件缺失即整件消失，且只进 log 不进 DB（BACKUP-RECONCILER 实测 173 行说明它**当前活着**，其余件需按 RC-1 差集逐一核） | 断言：注册失败的 ImportError 必须写一行 `critical_warn`（gate_id=`RECONCILE-REGISTRATION-<name>`），使「注册失败」与「未触发」在观测面上可区分 |
| **RC-13** | **P2** | 观测表混入测试件 | `trigger_source='pytest'` 10 行全为 `GATE-TEST-P4-1A` 写入生产库 | 断言：生产表零 `pytest` 源行（测试写 tmp 库；`_governance_db_path:871-895` 的 `anchor_main_root` 判定已有先例） |
| **RC-14** | **P1** | 头注入器自造不可账实面 | `_module_id_inject_header`（`reconciliation_registry.py:3388`）四处缺陷：①只看 `content[:500]` 有无 `[BLUEPRINT]` 便整块前置注入；②模板恒带 `# [TTL] permanent` ⇒ 已有 TTL 的文件出现**重复头**（HEAD 469 个带标记文件，抽样前 200 中 106 个重复）；③`[MODULE]` 槽填散文 "(auto-injected by S4 reconciler)"，不可账实核验；④module_id 由目录前缀反查**猜**出，实测把 MOD-ALT-001（alt_data 情绪族）安到治理测试、把全仓零声明的幻影 MOD-D5_ARCH_TOOLS 安到 d5 同步器测试 | ①夹具：对已含 `[TTL] limited` 的文件跑注入，断言 `count("# [TTL]")==1` 且原值保留；②注入块各槽只允许真源解析值，散文落点改 `unknown` 并计数告警；③module_id 反查失败即跳过注入（禁猜），断言 MOD-D5_ARCH_TOOLS 这类零声明 id 不再出现在任何文件头；④全仓扫描 `grep -c "\[TTL\]"` >1 的文件数归零。**暂不改的理由（2026-09-17 读码复核后修正）**：只剩一条真的——**HELD-OVERLAP**：被 13 个他会话草稿引用（`.aidrafts/*/src/zephyr/governance/audit/reconciliation_registry.py`，覆盖 st-auditfix/st-auditkey/st-dbgap-fix/st-govops/st-qalpha/st-resource/st-tdmbe/st-tickdrain/st-ailayer/st-dabanre/st-igalpha/st-maint/st-orchbp），按宪章 §3.4 owner 责任制不代修；自家两件受害测试已另批清偿。**原并列的第二条理由经读码证伪**：`NO-HIGH-COMPLEXITY` 并不"扫整文件"——`high_complexity_gate.py:168-186`（裁定#214）只罚 `node.lineno ∈ added_lines` **且** `node.name ∉ HEAD 函数名集合` 的真新增函数，改存量函数（`reconcile_for`=29 等）不触发，故存量复杂度不是施工阻断（该门禁确无 noqa 通道，存量由全量扫描脚本兜，非本门禁职责）。此误记本身已登记为 `gate_self_deception_mining.md` **GT-16**（"把门禁能力写强/写反"=文档侧自欺骗：宣称门禁管不到的地方管得到，会让后续施工据此放弃正当修法）。
| **RC-15** | **P1** | 清退无观测面：未提交内容被静默还原且不留可恢复对象 | `session_worktree.py` 的 pre-merge 清理把主区改动 `git stash push` 移走并写 `.runtime/workspace_alerts/stash_notice.json`（宪章 §2.8 已把该件写成「编辑消失先看这里」的救济通道）。但本车道 `framework_composer.py` 的未提交内容**两次**（09-16、09-17）被整文件还原到 HEAD，notices 里**零条**指向它、现存 4 个 stash 亦零命中（逐 ref `git show` 核实）⇒ notice 只覆盖 stash 这一条腿，另有一条还原路径（reset/checkout/quarantine 或 reconciler 直写）不留痕、不进任何 git 可恢复对象，唯一救生索是编辑器 file-history | ①夹具：改一个 tracked 文件后分别走 stash 与 reset/checkout 两条还原路，断言**各**产出一条可归属 notice，字段含 `session_id + mechanism ∈ {stash,reset,checkout,quarantine,reconciler}` + 文件清单 + 还原前后 sha256；②「notice 条数 ≥ 实际还原次数」进 `reconcile_for` 同款账实核验（notice 只留最近 N 条是既有设计，但每轮还原都必须在 DB 留一行）；③新增反查：`git stash list` 与 notices 双向差集非空即 WARN（有还原无留痕 / 有留痕无还原） |

**优先级裁定建议（采纳权在主力会话）**：RC-1/RC-2/RC-3/RC-4 为「全自动终局」的证伪面——它们不是效果差，而是**宣称的自动触发不存在或不执行**；RC-14 同属证伪面（**头注入器自造不可账实的账实证据面**，且直接污染本表所有下游判定）；RC-5/RC-6/RC-9 与 RC-15 是让它们长期不可见的观测面原因（RC-15 是其中唯一会造成**真实工作丢失**的一条）；其余为清册卫生。

---

## 5 子节点清单（挖出的新矿脉，交主力会话排批）

| 子节点 | 为什么值得挖 | 建议投喂材料 |
|---|---|---|
| `reconciler-observability-schema` | 观测表缺 `commit_sha/duration/priority/registered-set` 四要素，导致本节点所有「最近一次运行」都要靠 `session_id`+`logged_at` 反推（§1.8）；此面一通，RC-1/RC-12 的断言可一条 SQL 完成 | `reconciliation_registry.py:205-260`（建表 SQL 族）、`:995-1120`（写入器）、`cleanup_reconcile_log:1805` |
| `money-path-trigger-lineage` | 钱路上「执行回报 → 持仓对账 → 三向 → 结算 → 日终」五段只有最后一段有（坏掉的）触发器（§1.4）；逐段画事件线是全自动终局的主闸 | `src/zephyr/ex_core/fill_handler.py`、`src/zephyr/ex_core/position_reconciler.py`（活件）、`src/zephyr/trading/settlement_reconciliation.py`、`src/zephyr/risk/core/daily_auditor.py` |
| `scheduler-vs-event-inventory` | 现网 38 个 `ZephyrAlpha*` 计划任务 vs 宪章 §9.3 的覆盖情况，以及 `resource_profile_registry.yaml` 的 `window_type` 真值性（本次已见 1 例注册即失效） | `config/resource_profile_registry.yaml` 全量、`scripts/register_*.ps1` 族、`Get-ScheduledTask`/`Get-ScheduledTaskInfo` 只读采集脚本 |
| `generator-max-age-policy` | 26 件派生物无一条 max-age 绝对上限；db-only 用标记年龄代理，yaml 型用相对 mtime 比较（`reconcile_generators.py:104,590-601`），`no_input_sources` 结构上永不过时（`:580`） | `generator_registry.yaml`（26 件 + `:19-20` 字段语义 + `:29-35` 禁注清单）、`boot_hooks.py:355-373` |
| `session-ledger-discipline` | 4 个月无会话台账 + 索引冻结 2026-07-23 + 检查器看错目录（RC-11）；治理可追溯性的根部 | `session_logs/index.yaml`、`docs/01_policies_and_standards/…/session-log-schema.yaml`(GOV-AI-007)、`validate_session_log_index_integrity.py --generate` |

---

## 6 封矿判定

**本节点矿脉（「reconciler 事件触发链完整性」）判定：已枯竭可封，但下挂 5 条活脉（§5）移交。**

- 六向：①-⑥ **全部有 signal 产出**，无一向「已查无」，故不存在「未查向」。
- 已尽面：注册式全量（62 logged gate + 3 死注册 + 5 合成子件 + 3 死工厂，逐条带行数与最近时刻）、派生件全量（26 件逐件真实 `_is_stale` 结论）、钱路对账件全量（§1.4 十行，逐行给出宣称与实际调用方）、失败语义（except 站点 12 处逐一锚定）、新鲜度（三族逐一判有无 max-age）。
- 枯脉证据：对「是否还有第 4 个死注册 reconciler」的穷举已收敛——`make_*_reconciler` 工厂可解析 gate_id 共 **57** 个，其中零行者 13 个，13 个已 100% 归因（3 死注册 / 5 合成子件 / 3 去注工厂 / 2 谓词正确但窗口内无事件）。
- **未枯竭的下游**（不属于本节点矿脉，属 §5 子节点）：钱路事件线重建、观测面 schema、调度器普查、生成器 max-age、会话台账。

---

## 附录 A 正面清单（查过且健康，写给后续矿工当前提）

1. 异步 worker + 心跳 + 扫尸这套机制本身在跑且有留痕：`RECONCILE-WORKER-BOOT` 1,783 行（最近 2026-09-16 21:55:05），worker 全程 ~979 s 完成 34 件（status `6a0eca4700`）。
2. `flush` 失败降级 `auto_committed → warn` 的假自愈已治：`reconciliation_registry.py:947-979`。
3. 高价值 reconciler 确在按事件运行：`GATE-MODULE-ID-RECOMMEND` 1,004 行、`GATE-REGENERATE` 1,533 行、`GATE-INTEGRITY-AUDIT` 1,813 行、`GATE-RULE-AUDIT` 1,721 行、`GATE-TTL-DRIFT-INCREMENTAL` 979 行，最近运行全部落在 09-16 21:5x 同批。
4. `GATE-ASSET-INDEX`：头写 `[STARTUP] manual` 但已被事件化（`reconciliation_registry.py:7071/7155`），675 行实证——**头陈旧 ≠ 死件**，后续矿工勿误判。
5. 归一器 `_rel_path`（`:4687-4705`）自带跨盘兜底，注册式多数 trigger 已正确使用它；RC-1 是「例外」不是「通例」。
6. 生成器事件线本身接通：92 份 `post_commit_regen_yaml_*.log`，且同批 25/26 件正常 `ok`——失败被精确隔离在单件。

## 附录 B 本会话落盘面（自证，便于回滚）

**唯一被创建/修改的仓内文件**：`docs/_working/full-auto-chain/S11_assembled_backtest/nodes/reconciler_event_trigger_chain_mining.md`（本文件）。
探测件（只读脚本 + 其 JSON 输出）全部落在 TTL 区 `.runtime/tmp/mining_reconciler_20260917/`：`probe_exec_log.py`、`probe_exec_log2.py`、`probe_triggers.py`、`probe_trigger_pred.py`、`probe_alerts.py`、`probe_sess_index.py`、`probe_gens.py`、`probe_gens2.py`、`probe_specs.py` 及 `specs.json`、`exec_log.json`、`db_gate_ids.json`、`gen_freshness.json`、`trigger_style.json`、`never_logged.json`。
**未做**：任何 git 写操作（无 add/commit/stash/checkout）、任何 `data/` 写入、任何 DB 写（全部 `get_governance_conn(read_only=True)`）、任何 ClickHouse 查询（本节点不需要）、被挖文件的任何修改、任何 reconciler/计划任务的施工。

## 附录 C 未实证清单（附判决命令，禁把猜测当结论）

| 未实证项 | 为什么会卡住 | 判决命令（只读） |
|---|---|---|
| `GATE-SCRIPTS-IMPORT-BASELINE` / `GATE-UNDEFINED-NAME-BASELINE` / `GATE-CONSUMERS-ACCURACY-BASELINE` 的 5/4/3 次触发是否**全部**来自子串兜底分支 | `committed_files_summary` 只存前 20 个文件（`:1063-1067`）致截断归因不完备 | 同 RC-1 的谓词单测；或按 `session_id`+`logged_at` 取该批全量文件列表再判 |
| `ZephyrAlpha_PostSettlement` 自 2026-09-15 注册以来是否**每天**都是 2（只有最近一次出口码） | Task Scheduler 只保留 `LastTaskResult` | `schtasks /Query /TN ZephyrAlpha_PostSettlement /XML` 看 `NumberOfMissedRuns/LastRunTime` 序列，或连续两日只读复采 |
| 5 个合成件之外的合成子件是否有独立触发率 | 身份塌缩（RC-8） | RC-8 ①（detail 逐子件留痕）落地后 SQL 计数 |
| `battle_map` 的 `input_newer_than_output`（§1.7 判 stale）是否已在 09-17 05:19 那次成功重生成后转新鲜 | 快照时刻差异：`gen_battle_map.success` mtime 2026-09-17T05:19:22 与产物同刻 | `python -c "import sys;sys.path[:0]=['scripts/governance','src'];import reconcile_generators as g,yaml,pathlib;e=[x for x in yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml',encoding='utf-8'))['generators'] if x['name']=='battle_map'][0];print(g._is_stale(e))"` |
| 38 个 `ZephyrAlpha*` 计划任务中除 PostSettlement 外是否还有「注册了但每次非 0 且无人读」的 | 本节点只对 PostSettlement 深查 | `Get-ScheduledTask \| ? TaskName -like 'ZephyrAlpha*' \| Get-ScheduledTaskInfo \| ? LastTaskResult -ne 0` |
| `algo_flow_translation_sync`（`no_input_sources`）是真无输入还是注册表填漏 | `_is_stale:580` 对该情形直接返回「不过时」 | `python -c "import yaml,pathlib;print([g for g in yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml',encoding='utf-8'))['generators'] if g['name']=='algo_flow_translation_sync'])"` |

---

*节点结束。产出=数据。红灯降噪与维修归属维护班；本节点未尝试修复任何当前失败。*
