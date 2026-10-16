---
working_doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: GOMAP-L4
excavated: 2026-10-15
ttl: task_bound
---

# GOMAP-L4 收割族（治理运行七族之五，39 模块）

## 1. 定义

"垃圾要有人收"（legend reaper_duty）——孤儿/僵尸/幽灵进程收割、残留清理。
SSOT：`config/governance_operations_map.yaml#families.L4_reap`（机生禁手改，generated_at=2026-10-09）。
实读数据：39 模块 = wired 22 + wired_dynamic 2 + wired_by_header 8 + suspect_orphan 7；零触发 2 件。

## 2. 六向台账

### 2.1 输入面
- pipeline GOM-L4"收割清理"；mounts 3 件全实存核验（2026-10-15）：
  `src/zephyr/trading/process_reaper.py`、`src/zephyr/trading/orphan_detector.py`、`src/zephyr/gov_drift/orphan_scanner.py`。
- 输入事件：L3 熔断指令/L1 告警/OS 计划任务心跳（10min）。

### 2.2 输出面
- 收割动作 → L5 自愈族；whitelist 误杀防护=`data/runtime/process_reaper_keep.txt`（宪法 §0 RULE-GUARDIAN 口径）。
- casebooks：AP#域四、SV#底数（指针制）。

### 2.3 SSOT 真源
- `config/governance_operations_map.yaml#families.L4_reap`。
- 注册入口真源：`scripts/register_process_reaper_task.ps1`（宪法 RULE-GUARDIAN 真源指针）。
- ROOR REG-MAP-GOMAP-001 450/94 漂移（族共性）。

### 2.4 代码模块
- 活体实证（2026-10-15 21:27 实跑）：`python -m zephyr.trading.process_reaper --status` → source=live、
  scan_mode=live_dryrun（零杀）、scanned=8、whitelist_hits=7、ghosts=0、drift stash=1/worktree=5010、
  watermark degraded=False——收割主件在岗。
- 孤儿 7 件：`scripts.fix_orphan_all`、`scripts.governance.check_wiring_orphan`、`scripts.governance.cleanup_stash`、
  `scripts.governance.d1_structure.detect_orphan_py`、`scripts.governance.governance.d9_knowledge.detect_orphan_documents`、
  `scripts.governance.meta.benchmark.test_fixtures.orphan_file_without_module_registration`、
  `zephyr.feedback_loop.diagnosers.reliability.zombie_fle_detector`。
- 数据质量缺陷实证：孤儿清单中 `scripts.governance.governance.d9_knowledge.detect_orphan_documents` 为双写
  "governance." 段的畸变模块号——真实文件=`scripts/governance/d9_knowledge/detect_orphan_documents.py`（实存核验），
  即机扫层 path→module_id 推导在该条目产出了不存在于磁盘的标识符。
- 零触发 2 件（files=0 口径=源缺口）。

### 2.5 门禁约束
- 无专属 gate；生成器重建守护。RULE-GUARDIAN：reaper 计划任务存活是写操作前提（宪法硬规则 2）。

### 2.6 自动化触发
- OS 计划任务 10min 心跳（BRK-066 链路）；process_reaper_keep.txt 长批登记防误杀。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 3 mounts 实存+心跳链路 |
| 输出面 | pass | L5 交接+keep 白名单闭环 |
| SSOT 真源 | warn | ROOR 450/94 vs 429/64 漂移（族共性） |
| 代码模块 | warn | 孤儿 7 件中 1 件模块号畸变（governance.governance 双写）——机生层标识符推导缺陷；实文件在但地图标识失真 |
| 门禁约束 | pass | RULE-GUARDIAN 硬规则覆盖 |
| 自动化触发 | pass | reaper 实跑 live（本日 21:27） |

## 4. 缺口与建议

- 模块号畸变条目建议修因：generate_governance_map.py 的 path→module_id 推导对 `scripts/governance/` 前缀拼接疑似重复计数，修后 `--force` 重建对拍。
- reaper 当前 live_dryrun 模式零杀：与宪法"收割在岗"不冲突（守护语义=存在性），但建议在 GOMAP 侧注记 scan_mode 语义，防读图者误判收割不动作。
