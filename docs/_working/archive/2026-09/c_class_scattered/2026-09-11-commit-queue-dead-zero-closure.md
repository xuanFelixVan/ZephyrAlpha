---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（2 条，摘录）**
> - L49: 1. **PURGE 183 项**（明细 `.runtime/tmp/dead_disposition_v2.json`）：全部 auto 再生产物或门禁合法拦截，内容零丢失（已落地/在工作区/可再生）。批准确认后执行物理清理（dead/ 永不自动清理不变量不破——本项为 Owner gated 
> - L265: 3. index.html 导航文案纠偏——产业地图入口描述"产业链传导（待建设）"为陈旧文案（页面已建成），改"产业链传导：星系→链层→公司（族全景）"。
>
> **⚠️ 未完成（1 条，逐条摘录）**
> - L59: - P1⑤ A1 memoization + A2 checker 合并、P1⑥ 队列运营收尾（含交接新增观察：reconciler 子进程 `import scripts.governance` ModuleNotFoundError → 队列改道降级直提，gateway L2606 与本报告 §
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 3 个，其中判废弃 0、路径漂移 1）+ commit 提及 49 处。
> **路径漂移（非缺失，勿误判）**：`src/zephyr/infrastructure/hooks/__init__.py` 路径漂移→src/zephyr/__init__.py
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）





# commit_queue 死信清零收尾 + 死信率告警最小落地（st-perf-plan-20260910，2026-09-11）

续 [2026-09-10-commit-pipeline-perf-plan.md](2026-09-10-commit-pipeline-perf-plan.md) §2.4-4a（死信处置+可观测性）。
交接口径：933 项死信、全部可达零丢失；purge Owner gated；告警 Owner 已裁定要做。

## 1. 落盘管线二次排障（本夜新发现三连，处置后管线恢复实落）

交接时"根因已修"（serializer worktree 重建 + LandingEnvironmentError），但实测死信仍在新增（01:26-01:31 每分钟级）。三因叠加：

1. **陈旧 `index.lock`**：`D:/ZephyrAlpha/.git/worktrees/worktree/index.lock`（Sep 10 21:28 生成、0 字节、挂 4h+，无活体 git 进程）——每个 drain 项 `reset --hard` 撞锁 rc=128。git 官方口径手工清除。
2. **watchdog daemon 持旧代码**：drift watchdog daemon 21:45 启动，早于 23:48 的锁争用转环境专类修复（53916fd13b）——整夜用旧 landing 逻辑把撞锁项打死而非退回 pending（02:00 实证：114 项死信晚于 12:00）。处置：`schtasks /end + /run` 重启（新 PID 带新代码复活，派生同步与排空即恢复）。
3. **CLI 直跑 sys.modules 毒缓存（代码修复，53fa0b431a 残留）**：pywin32 的 `.pth` 把 `site-packages/win32` 注入 sys.path，其 `scripts/` 子目录可被裸 `import scripts` 解析为命名空间包；直跑进程一旦先命中该解析（如 `from scripts.ops_guard import` 失败回退路径），`sys.modules['scripts']` 即被缓存，事后补插 sys.path 无法翻转（submodule 搜索走已缓存 `__path__`）→ `_cmd_drain` 的 `scripts.governance` import 永久 ModuleNotFoundError。**53fa0b431a 修的是 path 层，此为模块缓存层**；其"验收 status 直跑跑通"未覆盖 drain 路径（status 不 import landing）。修复：模块级 repo 根入 path（真包优先于 win32 命名空间）+ `_purge_poisoned_scripts_package()` 按 `__path__` 校验清族重导 + 双文件重复 import 行清理。

验收：毒化探针（import scripts 后 runpy 直跑）+ 裸直跑双路 drain exit 0；试点 requeue 项 0477 实落 dev；health 快照实跑正常。

## 2. 死信全量甄别（处置时点 952 项，含 pilot 3 项已 requeue）

聚合结论：**950 项 dead 全部是 auto 提交**（chore(derived)/chore(reconciler)/chore(integrity)，零人工功能提交——人工 commit 走直提从不入队）。逐项三态比对（blob 死亡时快照 vs 当前工作区 vs HEAD）+ B 类白名单（gate_tracked_write_allowlist.yaml class=B，7 exact+2 pattern）覆盖判定，分桶：

| 桶 | 数 | 判定依据 | 处置 |
|---|---|---|---|
| REQUEUE | 758 | env 死因 ∧ 无 protected 路径 ∧ 文件全∈{B 白名单盖住, ws==HEAD, integrity/manifest 再生产物} | 已执行 757 ok + 1 fail（`src/zephyr/infrastructure/hooks/__init__.py` 文件真缺失），统一诚实 message、--base-head 空（快进应用）、同会话 compaction 自动去重（758 → pending ~126） |
| PURGE | 183 | protected_path_reblock 166（`architecture_model/index.yaml` 门禁必再拦）/ gate_item_failure 11（CAS/快进/LOCK_TIMEOUT/TRACKED-DRIFT-READONLY，gate 语义正常）/ content_gone 6（hot.txt 族，ws+HEAD 双缺） | **报 Owner 批**（内容零丢失见 §4） |
| REVIEW | 5 | 含未覆盖源码/测试漂移路径（redteam 测试×4 文件、`feedback_loop/detectors/drift/__init__.py`、`test_registry_entry_counts.py`、`generate_trading_map_diagram.py`、`test_websearch_ingest.py`）——可能是他会话 WIP 残留，不代拍板 | **报 Owner 裁定** |
| ALREADY_HEAD | 3 | 全路径 ws==HEAD（requeue 必 NOTHING_TO_COMMIT 空转） | 证据性清账，不 requeue |

REQUEUE 零丢失机理：requeue 快照=**当前工作区内容**重建（66 号 §6.4 语义），blob 不含工作区之外的内容——purge/跳过的死信项内容均已在工作区或 HEAD（或属可再生产物，健康管线的新鲜同步会落当前真值）。

## 3. 死信率告警最小落地（Owner 已裁定项）

- `scripts/commit_queue.py`：`queue_health()`（只读快照：四态计数+死因三分类 env/item/other+最老 pending/processing 项龄，聚合口径复用 triage）+ `emit_dead_backlog_alert()`（drain 收尾事件触发：dead_total ≥ 阈值且过冷却 → task_board 专 task `T-QUEUE-DEADLETTER` 幂等自建+打 deadletter 标签，66 号 §6.4 既有通道）+ CLI `health` 子命令（`--no-alert` 纯观察）。
- 阈值唯一真源 REG-ATH-001 v1.4.0：`THD-ALERT-003`（死信积压 ≥50 项）/ `THD-ALERT-004`（告警冷却 6h——drain 自举每 enqueue 触发一次，无冷却必刷屏）。代码经 `threshold_loader` fail-closed 统读；告警旁路链路 fail-open（阈值不可读/板不可达仅降级记日志，绝不阻断排空——可观测性与核心业务阈值消费的语义分级，代码注释已声明）。
- `scripts/task_board.py`：`ensure_task()` 固定 id 幂等建 task（`_new_task_id` 随机分配不满足挂载点稳定 id 诉求）。
- 测试：test_commit_queue.py 68→77（+9：快照聚合/死因分类/阈值判定/冷却/挂载点自建/板不可达 fail-open/drain 接线/CLI 冒烟）；test_alert_threshold_consistency.py 36→38 条同步；87+23+21 全绿。

## 4. Owner 四裁定执行记录（2026-09-11 凌晨批复，同夜执行）

1. **PURGE 184 项已执行删除**（183 + requeue 失败 1 项）。逐项审计留痕 `.runtime/commit_queue/purge_audit_20260911.jsonl`（qid/死因/会话/blob 引用）；blob 全为共享内容零误删（内容寻址去重，无孤立回收必要）；dead/ 978→794（余项均为已处置留痕或在飞项）。
2. **REVIEW 5 项按 [merge_conflict_resolution_sop](../../01_policies_and_standards/sop/merge_conflict_resolution_sop.md) 冲突三分法结案：全为 B 类迭代型（取新版）**。实证：5 个路径（红队测试×4/`feedback_loop/detectors/drift/__init__.py`/`test_registry_entry_counts.py`/`generate_trading_map_diagram.py`/`test_websearch_ingest.py`）的工作区 vs HEAD diff 已全部归零——甄别时点的漂移已被属主会话随后的提交迭代取代（HEAD=严格新版），死信 blob 无内容价值，无 A 类合并面、无 C 类升级面。零丢失（内容全在 dev）。
3. **保护路径死循环治本（选 A）两处落地**：①`commit_derived_sync.py` `_DERIVED_PATTERNS` 删除 `architecture_model/index.yaml`（收口白名单不再触碰）；②`commit_queue_landing.py` reroute 增 `split_auto_commit_snapshot()`——auto-commit 批次内的保护文件（真源=check_protected_paths.PROTECTED_PATTERNS，零复制复用）入队前剔除，漂移留工作区归属主手动处理，门禁语义零改动（manual 直提照旧全量拦截），**队列侧永不再产生"保护文件整批陪葬"死信**。回归测试+2（改道过滤/纯单元）。
4. P1⑤⑥/P2⑦⑧⑨ Owner 批准全部执行——见 §6 施工记录。

## 5. 报 Owner 裁定清单（已全部批复并执行，本节留档）

1. **PURGE 183 项**（明细 `.runtime/tmp/dead_disposition_v2.json`）：全部 auto 再生产物或门禁合法拦截，内容零丢失（已落地/在工作区/可再生）。批准确认后执行物理清理（dead/ 永不自动清理不变量不破——本项为 Owner gated 手工清理）。
2. **REVIEW 5 项**：未覆盖源码/测试漂移（列见 §2 表），是死会话残留该落、还是活会话 WIP 该留——请裁定归属。
3. **政策冲突**：派生同步把 protected 路径 `architecture_model/index.yaml`（工作区现存漂移）打进批次 → 门禁一票拦全项 → 每轮同步复产生死信（本夜 +6）。二选一：①派生白名单剔除该路径（同步不再碰）②该路径解除 protected。当前按"不单方改门禁语义"搁置，靠告警通道可见。
4. requeue 失败 1 项（q-20260905-AI-00-AUDIT-20260905-0009，文件已不存在）建议并入 purge 批。

## 6. P1/P2 施工记录（Owner 2026-09-11 批准全部执行）

全部落地（commit 见 git log st-perf-plan-20260910 链）：P1⑥ `_ensure_scripts_package_importable`（reconciler 子进程改道 import 补齐+毒缓存清洗，3 测）；P1⑤ A1 `_git_read_cache` 门禁链窗口式读缓存（2 测）+ A2 `checker_supervisor.py` 持久 worker 消 spawn 税（6 测，异常回退直 spawn，env 可回滚）；P2⑦⑧ `gate_cache_preflight.py`（保守白名单 10 gate+五元组指纹+TTL 10min 缓存+预跑采信，13 测，flag OFF）；P2⑨ `--enqueue`（flag OFF fail-closed 拒绝）。三 flag 登记 flags.yaml 全部出厂 OFF。方案 §7 总账已同步。

- P1④ own-scope 扩充：另派他会话执行中，本会话不碰。
- P1⑤ A1 memoization + A2 checker 合并、P1⑥ 队列运营收尾（含交接新增观察：reconciler 子进程 `import scripts.governance` ModuleNotFoundError → 队列改道降级直提，gateway L2606 与本报告 §1.3 同族第二处，本会话修的是 CLI 直跑处）、P2⑦⑧⑨：**均待 Owner 确认后执行**。

## 附：工具与证据文件（.runtime/tmp/，用完可清）

- `dead_disposition_v2.py` / `dead_disposition_v2.json`（终版分桶+清单）/ `dead_requeue_result.json`（执行回执）/ `dead_disposition_execute.log`（drain 轮次日志）
- `triage_dead_20260911.py` / `triage_dead_20260911.json`（初版全量甄别）
- `cq_probe.py`（毒缓存复现探针）、`commit_queue_dead_triage_20260910.md`（前夜诊断全录）、`pilot_qids.txt`（试点白名单）

## 7. purge 执行审计明细（184 项，Owner 批准 2026-09-11）

原始 jsonl=.runtime/commit_queue/purge_audit_20260911.jsonl（gitignored，此处内联留痕）。

| qid | 处置理由 | 会话 | 死因摘录 |
|---|---|---|---|
| q-20260831-ai-19596-20260829161740-0003 | gate_item_failure:item | ai-19596-20260829161740 | 冲突：dev CAS 竞态——7b8052cc0df2..ed2886e0ea4d 间同路径 ['docs/01_pol |
| q-20260901-ai-4c-20260901003332-0001 | protected_path_reblock | ai-4c-20260901003332 | 网关落盘失败（LOCK_TIMEOUT）: internal error |
| q-20260901-ai-4c-20260901003332-0002 | gate_item_failure:item | ai-4c-20260901003332 | 网关落盘失败（COMMIT_FAILED）: 门禁 SESSION-REQUIRED 阻断: session 'ai-4 |
| q-20260901-ai-agents-20260831220859-0001 | protected_path_reblock | ai-agents-20260831220859 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-ai-ds12-20260901120704-0001 | protected_path_reblock | ai-ds12-20260901120704 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-ai-fehb-20260831221647-0001 | protected_path_reblock | ai-fehb-20260831221647 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-ai-pc007-20260901123651-0001 | protected_path_reblock | ai-pc007-20260901123651 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-ai-smoke-20260901001516-0001 | protected_path_reblock | ai-smoke-20260901001516 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-ai-smoke-20260901001516-0002 | gate_item_failure:item | ai-smoke-20260901001516 | 冲突：入队基底 53bdb4b69bd5 之后 dev 已推进且触及同路径 ['scripts/governance/m |
| q-20260901-bt-pipeline-001-0001 | protected_path_reblock | bt-pipeline-001 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-free-llm-keys-20260901-0001 | protected_path_reblock | free-llm-keys-20260901 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-sop-v110-update-0001 | protected_path_reblock | sop-v110-update | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-sq-pos-bridge-20260901-0001 | protected_path_reblock | sq-pos-bridge-20260901 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-sq-pos-pct-20260901-0001 | protected_path_reblock | sq-pos-pct-20260901 | 网关落盘失败（LOCK_TIMEOUT）: internal error |
| q-20260901-sq-search-box-20260901-0001 | protected_path_reblock | sq-search-box-20260901 | 网关落盘失败（LOCK_TIMEOUT）: internal error |
| q-20260901-sq-search-box-20260901-0002 | gate_item_failure:item | sq-search-box-20260901 | 网关落盘失败（CLAIM_REQUIRED_VIOLATION）: session 'sq-search-box-202 |
| q-20260901-sq-stock-header-20260901-0001 | protected_path_reblock | sq-stock-header-20260901 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260901-sq-stock-header-20260901-0002 | gate_item_failure:item | sq-stock-header-20260901 | 网关落盘失败（COMMIT_FAILED）: 门禁 SESSION-REQUIRED 阻断: session 'sq-s |
| q-20260901-theme-placeholder-20260901-0001 | protected_path_reblock | theme-placeholder-20260901 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260902-bt-pipeline-001-0002 | protected_path_reblock | bt-pipeline-001 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260902-bt-pipeline-001-0003 | protected_path_reblock | bt-pipeline-001 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260902-freeze-gw-0002 | gate_item_failure:item | freeze-gw | 网关落盘失败（LOCK_TIMEOUT）: internal error |
| q-20260902-freeze-gw-0003 | gate_item_failure:item | freeze-gw | 冲突：dev CAS 竞态——5c92b3dfdf4f..e25de124286a 间同路径 ['data/asset_ |
| q-20260902-solo-20260902-services-gate-0001 | gate_item_failure:item | solo-20260902-services-gate | 网关落盘失败（COMMIT_SCOPE_VIOLATION）: commit 跨越多个功能域（COMMIT_SCOPE_ |
| q-20260903-auto-derived-sync-0001 | content_gone_ws_and_head | auto-derived-sync | 网关落盘失败（COMMIT_FAILED）: git commit failed: Author identity un |
| q-20260903-auto-derived-sync-0002 | content_gone_ws_and_head | auto-derived-sync | 网关落盘失败（COMMIT_FAILED）: git commit failed: Author identity un |
| q-20260903-auto-derived-sync-0003 | content_gone_ws_and_head | auto-derived-sync | 网关落盘失败（COMMIT_FAILED）: git commit failed: Author identity un |
| q-20260903-auto-derived-sync-0004 | content_gone_ws_and_head | auto-derived-sync | 网关落盘失败（COMMIT_FAILED）: git commit failed: Author identity un |
| q-20260903-auto-derived-sync-0005 | content_gone_ws_and_head | auto-derived-sync | 网关落盘失败（COMMIT_FAILED）: git commit failed: Author identity un |
| q-20260903-auto-derived-sync-0006 | content_gone_ws_and_head | auto-derived-sync | 网关落盘失败（COMMIT_FAILED）: git commit failed: Author identity un |
| q-20260903-data-backfill-0903-0001 | protected_path_reblock | data-backfill-0903 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260903-session-20260903-igsop-0001 | protected_path_reblock | session-20260903-igsop | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260903-solo-20260902-services-gate-0003 | protected_path_reblock | solo-20260902-services-gate | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260903-solo-20260902-services-gate-0005 | protected_path_reblock | solo-20260902-services-gate | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260904-AI-DSREG-112-0001 | protected_path_reblock | AI-DSREG-112 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-AI-DSREG-112-0003 | protected_path_reblock | AI-DSREG-112 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-data-backfill-0903-0003 | protected_path_reblock | data-backfill-0903 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-perf-swr-allpages-20260903-0001 | protected_path_reblock | perf-swr-allpages-20260903 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260902-services-gate-0011 | protected_path_reblock | solo-20260902-services-gate | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260902-services-gate-0013 | protected_path_reblock | solo-20260902-services-gate | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260902-services-gate-0015 | protected_path_reblock | solo-20260902-services-gate | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260902-services-gate-0017 | protected_path_reblock | solo-20260902-services-gate | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260902-services-gate-0019 | protected_path_reblock | solo-20260902-services-gate | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260902-services-gate-0021 | protected_path_reblock | solo-20260902-services-gate | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260902-services-gate-0023 | protected_path_reblock | solo-20260902-services-gate | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260903-twopane-0001 | protected_path_reblock | solo-20260903-twopane | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260903-twopane-0003 | protected_path_reblock | solo-20260903-twopane | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260903-twopane-0005 | protected_path_reblock | solo-20260903-twopane | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260903-twopane-0007 | protected_path_reblock | solo-20260903-twopane | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260903-twopane-0009 | protected_path_reblock | solo-20260903-twopane | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260903-twopane-0011 | protected_path_reblock | solo-20260903-twopane | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-eqw-alla-0001 | protected_path_reblock | solo-20260904-eqw-alla | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-governance-fixes-0001 | protected_path_reblock | solo-20260904-governance-fixes | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0001 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0003 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0005 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0007 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0009 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0011 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0013 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0015 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260904-solo-20260904-truth-source-0017 | protected_path_reblock | solo-20260904-truth-source | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260905-AI-00-AUDIT-20260905-0009 | requeue_fail_file_missing | AI-00-AUDIT-20260905 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260905-solo-20260904-decision-map-r7-0001 | protected_path_reblock | solo-20260904-decision-map-r7 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260905-solo-20260904-decision-map-r7-0003 | protected_path_reblock | solo-20260904-decision-map-r7 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260906-STEWARD-20260905-001-0008 | protected_path_reblock | STEWARD-20260905-001 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260906-solo-20260905-decision-map-v122-0005 | protected_path_reblock | solo-20260905-decision-map-v122 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260906-solo-20260905-decision-map-v122-0006 | protected_path_reblock | solo-20260905-decision-map-v122 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260906-solo-20260905-decision-map-v122-0007 | protected_path_reblock | solo-20260905-decision-map-v122 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260907-d34-crossindex-0001 | protected_path_reblock | d34-crossindex | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260907-d36-xref-axes-0001 | protected_path_reblock | d36-xref-axes | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260907-d38-adv-0001 | protected_path_reblock | d38-adv | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260907-d38-frontend-bus-0001 | protected_path_reblock | d38-frontend-bus | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260908-NODE-CARDS-V18-0001 | protected_path_reblock | NODE-CARDS-V18 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260908-sess-st-10pct-recalib-20260907-0001 | protected_path_reblock | sess-st-10pct-recalib-20260907 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-closeout-20260909-ig-quality-0001 | protected_path_reblock | closeout-20260909-ig-quality | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-greatwall-20260909-0001 | protected_path_reblock | greatwall-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-greatwall-20260909-0020-0001 | protected_path_reblock | greatwall-20260909-0020 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-greatwall-20260909-0020-0003 | protected_path_reblock | greatwall-20260909-0020 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-sess-chainmap-a2-20260909-0001 | protected_path_reblock | sess-chainmap-a2-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-solo-20260903-twopane-0013 | protected_path_reblock | solo-20260903-twopane | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-solo-20260909-qmt-night-0001 | protected_path_reblock | solo-20260909-qmt-night | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-solo-20260909-qmt-night-0003 | protected_path_reblock | solo-20260909-qmt-night | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-solo-20260909-qmt-night-0005 | protected_path_reblock | solo-20260909-qmt-night | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-ig-quality-engine-20260909-0001 | protected_path_reblock | st-ig-quality-engine-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-ig-quality-engine-20260909-0003 | protected_path_reblock | st-ig-quality-engine-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-ig-quality-engine-20260909-0005 | protected_path_reblock | st-ig-quality-engine-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-ig-quality-engine-20260909-0007 | protected_path_reblock | st-ig-quality-engine-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-ig-quality-engine-20260909-0009 | protected_path_reblock | st-ig-quality-engine-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-nodebt-night-20260909-0001 | protected_path_reblock | st-nodebt-night-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-nodebt-night-20260909-0003 | protected_path_reblock | st-nodebt-night-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-nodebt-night-20260909-0005 | protected_path_reblock | st-nodebt-night-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-nodebt-night-20260909-0007 | protected_path_reblock | st-nodebt-night-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-nodebt-night-20260909-0009 | protected_path_reblock | st-nodebt-night-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-nodebt-night-20260909-0011 | protected_path_reblock | st-nodebt-night-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdm-canvas-20260908-0003 | protected_path_reblock | st-tdm-canvas-20260908 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdm-canvas-20260908-0005 | protected_path_reblock | st-tdm-canvas-20260908 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdm-canvas-20260908-0007 | protected_path_reblock | st-tdm-canvas-20260908 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmbe-20260909-0001 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmbe-20260909-0003 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmbe-20260909-0005 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmbe-20260909-0007 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmbe-20260909-0009 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmbe-20260909-0011 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmbe-20260909-0013 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmbe-20260909-0015 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmfe-20260909-0001 | protected_path_reblock | st-tdmfe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmfe-20260909-0003 | protected_path_reblock | st-tdmfe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmfe-20260909-0005 | protected_path_reblock | st-tdmfe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-tdmfe-20260909-0007 | protected_path_reblock | st-tdmfe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-xflow-20260910-0001 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-xflow-20260910-0003 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-xflow-20260910-0005 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-xflow-20260910-0007 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-xflow-20260910-0009 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-xflow-20260910-0011 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-xflow-20260910-0013 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-st-xflow-20260910-0015 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-ths-profile-20260909-0001 | protected_path_reblock | ths-profile-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260909-trae-20260909-desktop-zombie-fix-0001 | protected_path_reblock | trae-20260909-desktop-zombie-fix | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-gw-tdm-20260909-0001 | protected_path_reblock | gw-tdm-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-gw-tdm-20260909-0003 | protected_path_reblock | gw-tdm-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-gw-tdm-20260909-0005 | protected_path_reblock | gw-tdm-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-gw-tdm-20260909-0007 | protected_path_reblock | gw-tdm-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-gw-tdm-20260909-0009 | protected_path_reblock | gw-tdm-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-gw-tdm-20260909-0011 | protected_path_reblock | gw-tdm-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-gw-tdm-20260909-0013 | protected_path_reblock | gw-tdm-20260909 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260910-qmt-day-20260909-0001 | protected_path_reblock | qmt-day-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-qmt-day-20260909-0003 | protected_path_reblock | qmt-day-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-sess-19872-20260909154331-0001 | protected_path_reblock | sess-19872-20260909154331 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-sess-30316-20260910022453-0001 | protected_path_reblock | sess-30316-20260910022453 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-sess-30316-20260910022453-0003 | protected_path_reblock | sess-30316-20260910022453 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-sess-30316-20260910022453-0005 | protected_path_reblock | sess-30316-20260910022453 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-sess-30316-20260910022453-0007 | protected_path_reblock | sess-30316-20260910022453 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260910-solo-20260910-daily-fix-0001 | protected_path_reblock | solo-20260910-daily-fix | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-solo-20260910-daily-fix-0003 | protected_path_reblock | solo-20260910-daily-fix | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-solo-20260910-daily-fix-0005 | protected_path_reblock | solo-20260910-daily-fix | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-solo-20260910-daily-fix-0007 | protected_path_reblock | solo-20260910-daily-fix | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-solo-20260910-daily-fix-0009 | protected_path_reblock | solo-20260910-daily-fix | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260910-st-btfw3-20260910-0001 | protected_path_reblock | st-btfw3-20260910 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260910-st-chainfe-20260910a-0001 | protected_path_reblock | st-chainfe-20260910a | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-chainfe-20260910a-0003 | protected_path_reblock | st-chainfe-20260910a | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-chainfe-20260910a-0005 | protected_path_reblock | st-chainfe-20260910a | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-chainfe-20260910a-0007 | protected_path_reblock | st-chainfe-20260910a | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-chainfe-20260910b-0001 | protected_path_reblock | st-chainfe-20260910b | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-clearance-night-0001 | protected_path_reblock | st-clearance-night | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-clearance-night-0003 | protected_path_reblock | st-clearance-night | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-igbe-20260910-0001 | protected_path_reblock | st-igbe-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-igfe-20260910-0001 | protected_path_reblock | st-igfe-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-igfe-20260910-0003 | protected_path_reblock | st-igfe-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-igfe-20260910-0005 | protected_path_reblock | st-igfe-20260910 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260910-st-igfe-20260910-0007 | protected_path_reblock | st-igfe-20260910 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260910-st-igfe-20260910-0009 | protected_path_reblock | st-igfe-20260910 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260910-st-legacy-clear-20260910-0001 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0003 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0005 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0007 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0009 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0011 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0013 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0015 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0017 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0019 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0021 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0023 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-legacy-clear-20260910-0025 | protected_path_reblock | st-legacy-clear-20260910 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260910-st-tdmbe-20260909-0017 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-tdmbe-20260909-0019 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-tdmbe-20260909-0021 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-tdmbe-20260909-0023 | protected_path_reblock | st-tdmbe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-tdmfe-20260909-0009 | protected_path_reblock | st-tdmfe-20260909 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260910-st-xflow-20260910-0017 | protected_path_reblock | st-xflow-20260910 | landing 异常: RuntimeError: git rev-parse --show-toplevel -> r |
| q-20260911-night-pathfinding-2300-0003 | protected_path_reblock | night-pathfinding-2300 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260911-night-pathfinding-2300-0005 | protected_path_reblock | night-pathfinding-2300 | 冲突：入队基底 ed296132cf00 之后 dev 已推进且触及同路径 ['docs/01_policies_and |
| q-20260911-night-pathfinding-2300-0006 | gate_item_failure:item | night-pathfinding-2300 | 冲突：入队基底 ed296132cf00 之后 dev 已推进且触及同路径 ['scripts/governance/m |
| q-20260911-night-pathfinding-2300-0007 | protected_path_reblock | night-pathfinding-2300 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260911-night-pathfinding-2300-0008 | gate_item_failure:item | night-pathfinding-2300 | 网关落盘失败（COMMIT_FAILED）: 门禁 TRACKED-DRIFT-READONLY 阻断: gate 链执 |
| q-20260911-solo-20260910-daily-fix-0013 | protected_path_reblock | solo-20260910-daily-fix | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260911-solo-20260910-daily-fix-0015 | protected_path_reblock | solo-20260910-daily-fix | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260911-st-asset-v2-0003 | protected_path_reblock | st-asset-v2 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260911-st-asset-v2-0005 | protected_path_reblock | st-asset-v2 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |
| q-20260911-st-asset-v2-0006 | gate_item_failure:item | st-asset-v2 | 网关落盘失败（COMMIT_FAILED）: 门禁 TRACKED-DRIFT-READONLY 阻断: gate 链执 |
| q-20260911-st-igfe-20260910-0011 | protected_path_reblock | st-igfe-20260910 | landing 异常: RuntimeError: git‑reset --hard refs/heads/dev -> |
| q-20260911-st-igfe-20260910-0013 | protected_path_reblock | st-igfe-20260910 | 网关落盘失败（COMMIT_FAILED）: 门禁 PROTECTED-PATHS 阻断: PROTECTED-PATH |

## 8. 产业链全景图体检与修复（同夜，Owner 令"数据正确+前端无问题"）

体检结论（全绿基线）：数据侧 galaxy/cluster/node/search 四端点对账一致（44 簇/599 链/852 边；cn 档 74 簇/574 链、global 6 簇/25 链随档独立聚类=设计）；前端 ZK_BUILD 即最新提交、smoke 6 绿、frontend_map fail=0、静态资源 6×200、Playwright 真浏览器 L1 3D 星系（44 族/599 链全渲染）+L2 链层下钻（面包屑三级/自动聚焦/重心布局/真源标注）全通、console/page errors=0。

本夜修复三件（playwright 机断回归 0 错误）：
1. chainmap-cluster.js 死 render 删除——文件内两个 render() 声明（函数声明后者胜出，前者为退役单链视图版死代码且引用不存在的 renderFocused，调用即 ReferenceError 的地雷）；删后单 render 全仓唯一。
2. drawView 布局前置——svg width/height 取自 layout() 计算的 worldW/worldH，但原顺序先设尺寸后布局，首画必 undefined（console 双告警）；改为先 layout 后定尺寸（纯计算重排零行为差异）。
3. index.html 导航文案纠偏——产业地图入口描述"产业链传导（待建设）"为陈旧文案（页面已建成），改"产业链传导：星系→链层→公司（族全景）"。

登记不修（归属他进程/Owner-gated）：文章词链名 2 条（环氧丙烷供需格局/节水装备发展现状，e3c41e5550 存量登记，逐簇梳理射程）；新闻标题式环节名 1 条（硝酸铵出口传导，同上）；C02 软件开发簇混入金融概念链（海外基金/AMC/跨境资产配置，聚类按公司重叠自动归属，逐簇梳理射程）；S21 断链字段/child_chain_id 下钻/aliases/facilities（等后端字段）；B8 作战池 HOLD；浅色主题挂起。
# 告警通道验证标记 2026-09-12T12:46
