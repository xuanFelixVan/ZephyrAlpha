---
ttl: task_bound
---

# M3 分册 02 · reconciler 族（post-commit 对账注册表）

> 挖掘 2026-09-25 ｜ 车道 M3 ｜ 只读挖矿，零 commit。
> 真源：`src/zephyr/governance/audit/reconciliation_registry.py`（11126 行）+
> `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1547`（_register_default_reconcilers）。

## 一、环节定义与边界

一句话：commit 落库后的事件触发对账族——registry 按 priority 升序遍历 specs，trigger(committed_files)
命中即执行 reconcile，异常降级 warn 不阻断。供料方=GitCommitGateway commit/merge 完成事件；
消费方=governance.db reconcile_execution_log、`.runtime/reconcile_reports/`、各真源册。

## 二、六向台账

| 向 | 内容 |
|---|---|
| 上游输入 | committed_files+session_id+commit_message；各 make_*_reconciler 闭包捕获的 gateway/project_root |
| 下游消费 | governance.db（reconcile_execution_log/emergency/abuse 计数）、docs 报告、block_next 阻断位（下次 commit 前 _check_recent_blocks 消费） |
| 自动化触发 | **全部事件触发**（commit/merge/queue landing/emergency 补偿）；唯一常跑例外=worktree_drift_watchdog ensure-daemon（60s 全扫+10s 热扫，M10 豁免在案）；另有 ruling #354 每日 03:30 fulltree gate 审计计划任务（**显式声明非 reconciler**，S9.3 不适用） |
| 真源与注册表 | ReconciliationRegistry（实例级，每 gateway 一个，非模块单例）；外部规格清单 `_EXTERNAL_SPEC_MODULES`（reconciliation_registry.py:648） |
| 门禁与质量尺 | file_ops 声明制（T1①）+ ops_guard contextvar 注入；timeout→critical_warn；DeleteBlockedError→critical_warn |
| 当前运行状态 | 绿（结构完整；名册数见 §三，与 C1 卷宗 E5"名册不同步"发现一致仍在） |

## 三、子模块清单：组合与计数

### 3.1 注册总数
- **静态注册 58**：git_commit_gateway.py:1549-1796 无条件 51 + try/except 条件 7
  （backup_reconciler、readme_version_sync、requirements_version_sync、metric_count_drift、
  algo_flow_translation、agents_cheatsheet_drift、algo_flow_reverse_orphan——ImportError 时 warn 跳过）。
- **外部运行时注册 2**（W4-4 路径，reconciliation_registry.py:648-651）：
  schedule_consistency_reconciler（GATE-SCHEDULE-CONSISTENCY）、library_regen_reconciler（LIBRARY-REGEN）。
- **合计上限 60**（条件注册失败时 <60）。
- **死工厂 3**（已升级为 pre-commit gate，定义在 reconciliation_registry.py 但**不再注册**）：
  make_precommit_id_uniqueness_reconciler(GATE-ID-UNIQ)、make_exempt_zone_frontmatter_reconciler(GATE-EXEMPT-ZONE-FM)、
  make_module_id_consistency_reconciler(GATE-MODULE-ID-CONSISTENCY)（gateway 注册段注释"Phase 3 收敛"1570-1572 行可证）。

### 3.2 reconcile_for 语义（reconciliation_registry.py:770）
- priority 升序遍历；trigger 命中→执行前刷新心跳（执行期间 daemon 线程每 120s 续命，防 STALE 误判）；
  arity≥3 的 reconciler 收 commit_message；file_ops contextvar 注入/复位；异常/超时降级不阻断。
- **action 词表六值**：`skip | clean | auto_committed | warn | critical_warn | block_next`（:541-577）。
  block_next 最重（下次 commit/merge 硬阻断，需 resolve_blocks 清除）；**无 "defer" action**。

### 3.3 触发条件分类（逐 _trigger 实证）
| 类 | reconciler（gate_id） | 证据行 |
|---|---|---|
| **每 commit 恒真**（9） | GATE-RULES-INTEGRITY(:6741 "总是触发")、GATE-COMMIT-GW-AUDIT(:6875 "审计始终运行")、GATE-RUNTIME-CLEANUP(:7719)、GATE-TMP-CLEANUP(:9144)、root_temp_sweep(:10746)、session_staging_lifecycle(:11024)、stash_lifecycle(:9848 任何有文件)、worktree_lifecycle(:9273 任何有文件)、GATE-WORKING-DOCS(:5612 状态机每 post-commit 推进) + secret_registry_drift（gateway 注册注释"trigger 恒真"，.env gitignored） | — |
| **运行时写入型** | GATE-DOMAIN-DOC(:5791 "DB 写入不产生 git commit，原 trigger 永不 fire" 已改) | — |
| 文件模式命中（主体） | manifest/path_tree/path_ownership/depgraph_ops/blueprint_*/drift_*/yaml_sync/vocab/ttl/deprecated/delete_audit/regenerate/rule_audit/registry_sync/integrity_audit/index_generator/arch_*/gate_*_sync/scripts_import/undefined_name/consumers_accuracy/capability_lookup_health/blueprint_id_legacy 等 | 各 make_* 内 _trigger |
| 全 .py 命中 | scripts_import_integrity(:9373)、undefined_name_baseline(:9501)、blueprint_id_legacy(:10074)、capability_lookup_health(:10361 src/zephyr/**/*.py) | — |

### 3.4 defer 面（三类，均非独立 action）
1. **batcher 后置 defer**：GATE-RULES-INTEGRITY 在 batcher 启用时 defer 到 post-flush，读 post-flush HEAD=最终状态
   （:6763-6772 "rules_integrity --register deferred to post-flush"）；gateway:2251 注释同源。
2. **remediation_progress 的 deferred 状态**：status 五值含 `deferred`，completed/deferred 豁免 >90 天新鲜度 block_next
   （remediation_progress_reconciler.py:8/31/145）——defer 是被登记的合法停泊态。
3. **全链异步时延**：默认 launch_reconcile_async spawn detached worker（gateway:1043-1045，P2-3 治本），
   `ZEPHYR_RECONCILE_SYNC=1` 强制同步；worker 结果写 status file+execution_log，STALE 阈值 1800s
   （reconcile_worker.py:201）。emergency_commit 的 trigger_reconcilers=False 是显式跳过（速度优先）。

### 3.5 事件 vs 恒跑分布
- **事件触发**：60 个 reconciler 全体（commit/merge/landing/emergency 五类入口）。
- **常跑 daemon**：worktree_drift_watchdog（60s 全量+热文件 10s 双频节拍；idle 1800s 自退；
  `#ARCH-264` critical_warn 唯一写者=daemon，网关即时扫 observe-only；`#ARCH-308` A1/A2 死会话保守清扫；
  M10 豁免 noqa 在文件头）。heartbeat_daemon/commit_belt_daemon 属 commit 链（引用 commit_speedup，不重挖）。
- **计划任务**：ZephyrAlpha_GateFullTreeAudit 每日 03:30（ruling #354 Owner 批准，脚本注释显式声明"NOT a reconciler"）。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|------|------|---------|--------|-----------|
| R1 | 名册与实际注册数无机械核对面（C1-E5 遗留：模块数/在册数/链内计时名三口径） | spec_count 只在测试消费；无"注册清单落盘对账" | reconcile_for 首跑时把 list_gate_ids() 落盘 `.runtime/reconcile_reports/registry_manifest.json`，GATE-INVENTORY-SYNC 交叉消费 | S | 是 |
| R2 | 9 个恒真 trigger 意味着每笔 commit 全量跑 9 台清理/审计（提速面） | 清理类天然与 commit 正相关 | 恒真台已四台降档异步（C1 采纳项）；剩余 5 台评估合并入同一 FS-sweep 单台 | M | 施工归 commit_speedup 批次 |
| R3 | 死工厂 3 个留在真源文件（11126 行内） | 升级 gate 后未清定义 | 退役候选登记（净零铁律：替代已声明，删除待 Owner 窗口） | S | 待裁（净删门位） |
| R4 | 条件注册 7 台 ImportError 静默 warn → 同一 registry 实例数可变（60/59/58...） | sys.path 注入脆弱（reconcile_for 入口清洗已治 `scripts.ops_guard` 病，:800-826） | 把 7 台 d8_doc_sync 插件收编进 _EXTERNAL_SPEC_MODULES 统一装载 | M | 是 |

## 五、提速与合并机会
1. R4 收编后，外部规格路径（W4-4）成为新 reconciler 唯一入口，gateway 注册段冻结不再增长——**已部分落地**（_EXTERNAL_SPEC_MODULES 注释即此意图），把 7 台插件迁完即闭环。
2. 恒真 FS-sweep 类 4 台（runtime_cleanup/tmp_cleanup/staging/root_temp_sweep）扫的目录不同但节拍相同，可合并单 pass 多目录（需保留各自 gate_id 报表口径）。

## 六、自审闸三态
**挖干可施工**（组合/触发/defer/事件分布四向全实证；R1/R4 本车道可出修法草案，R2 归 commit_speedup，R3 待裁）。

## 七、复核命令
```bash
grep -c "self._reconciliation_registry.register" src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py   # 静态注册数
grep -n "_EXTERNAL_SPEC_MODULES" src/zephyr/governance/audit/reconciliation_registry.py | head -2
sed -n '541,577p' src/zephyr/governance/audit/reconciliation_registry.py   # action 词表
grep -n "return True  #" src/zephyr/governance/audit/reconciliation_registry.py   # 恒真 trigger
```
