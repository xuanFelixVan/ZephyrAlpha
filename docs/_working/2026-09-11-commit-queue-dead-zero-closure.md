---
ttl: task_bound
---
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

## 4. 报 Owner 裁定清单

1. **PURGE 183 项**（明细 `.runtime/tmp/dead_disposition_v2.json`）：全部 auto 再生产物或门禁合法拦截，内容零丢失（已落地/在工作区/可再生）。批准确认后执行物理清理（dead/ 永不自动清理不变量不破——本项为 Owner gated 手工清理）。
2. **REVIEW 5 项**：未覆盖源码/测试漂移（列见 §2 表），是死会话残留该落、还是活会话 WIP 该留——请裁定归属。
3. **政策冲突**：派生同步把 protected 路径 `architecture_model/index.yaml`（工作区现存漂移）打进批次 → 门禁一票拦全项 → 每轮同步复产生死信（本夜 +6）。二选一：①派生白名单剔除该路径（同步不再碰）②该路径解除 protected。当前按"不单方改门禁语义"搁置，靠告警通道可见。
4. requeue 失败 1 项（q-20260905-AI-00-AUDIT-20260905-0009，文件已不存在）建议并入 purge 批。

## 5. P1/P2 状态（承接交接，未动）

- P1④ own-scope 扩充：另派他会话执行中，本会话不碰。
- P1⑤ A1 memoization + A2 checker 合并、P1⑥ 队列运营收尾（含交接新增观察：reconciler 子进程 `import scripts.governance` ModuleNotFoundError → 队列改道降级直提，gateway L2606 与本报告 §1.3 同族第二处，本会话修的是 CLI 直跑处）、P2⑦⑧⑨：**均待 Owner 确认后执行**。

## 附：工具与证据文件（.runtime/tmp/，用完可清）

- `dead_disposition_v2.py` / `dead_disposition_v2.json`（终版分桶+清单）/ `dead_requeue_result.json`（执行回执）/ `dead_disposition_execute.log`（drain 轮次日志）
- `triage_dead_20260911.py` / `triage_dead_20260911.json`（初版全量甄别）
- `cq_probe.py`（毒缓存复现探针）、`commit_queue_dead_triage_20260910.md`（前夜诊断全录）、`pilot_qids.txt`（试点白名单）
