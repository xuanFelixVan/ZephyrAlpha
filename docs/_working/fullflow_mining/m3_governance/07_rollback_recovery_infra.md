---
ttl: task_bound
volume: 07_f107_rollback_recovery
session: st-ailayer-final-20260924
creation_token: fullflow-w4b-f107-rollback-book-20260926
---

# 07 · 回滚恢复（infrastructure/rollback 双轨 checkpoint + 四级回滚 + G0 自愈）

> **文件名与标题行刻意不写环节号**（机生尺的认领面有三处：文件名 `fnn`、`#` 标题行、"本册覆盖"声明行；本册 §六 判"待挖"，故三处全部回避，保持该格 uncovered＝诚实态）。正文按 §一/§六 要求仍写号以便人读与对账。

> 车道 W4-B；工作面=worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`；零提交零入队、只读取证。
> 上游派单=`00_skeleton/92_coverage_triage_20260926.md` §三/§四第 4 条（F107 判"真缺簿·全六向缺"）。
> **本册结论先行：§三 子模块清单已穷尽实证（55 件实测），但 §二 六向中"下游消费/门禁与质量尺"两向未取得 file:line 级实证 → 本册按 §六 判「待挖」，§一 不挂 F107 认领锚。**

## 一、环节定义与边界

总册口径（`00_skeleton/00_全环节总册.md:182`）：F107 回滚恢复｜上游 F84｜下游 全链｜真源=`src/zephyr/infrastructure/rollback/`｜总册标 **built**、优先级 P1、段=K 段治理门禁（F97-F110）｜挂 G11。

本册实证后**不维持**总册的 `built` 判定（回写建议见 §六末）：目录本体确实存在且规模巨大（55 个 .py，实测见 §三），但"built"的四要素里**出口真源与自动化程度两要素无实证**——即"这个包被谁在什么时候调用、失败时真能改状态吗"未证。本册覆盖面=§三 清单穷尽 + §二 四向实证，不覆盖 F107 全格。

**本册不挂 F107 认领锚**（理由见 §六：六向缺 2 向，挂锚＝把机生对账尺的 uncovered 洗成 covered，属假绿）。

边界：与 F84（备份/快照上游）、F108（人机门位）、kill_switch 域（`src/zephyr/security/access_control/kill_switch.py`，异对象）不并；本册只挖 `infrastructure/rollback/` 包体。

## 二、六向台账

| 向 | 内容（证据） | 实证度 |
|---|---|---|
| 上游输入 | 触发面候选三：①`auto_rollback_trigger.py`（事件式自动触发入口，命名即职责）②`rollback_boot_integration.py` + `rollback_bootstrap.py`（启动期挂接）③`git_infra_snapshot.py` / `sqlite_dumper.py` / `s3_snapshot_lifecycle.py`（快照喂 checkpoint）。**未证**：三者的实际调用点（谁 import）。 | 半（清单实证，调用点未证） |
| 下游消费 | **查无实证**。本车道未取到"回滚结果被哪个运行时组件消费"的 file:line。邻接但异对象：`m7_live_execution/02_kill_switch*` 簿中 "rollback" 字样经 92 分诊册 §一 F107 行判定为**不同对象**（那是交易侧回退，不是本包）。 | **缺** |
| 自动化触发 | 计划任务/常驻：`rollback_scheduler.py`（名字即排程职责）、`env_watcher.py`、`agent_cooldown.py`、`checkpoint_gc.py`（GC 型）、`warm_standby.py`、`vulnerability_rescanner.py`、`topology_change_log.py` 属"周期性/守护型"命名簇；事件型=`auto_rollback_trigger.py` + `rollback_wal.py`。**未取到注册名或 file:line 级接线证据**（宪法 §9.3 红线：reconciler 类 MUST 事件触发，禁 cron/Timer/sleep-loop——本包若为 cron 型即违宪，是待验判据点）。 | **缺（须补：计划任务注册名 或 `SchedulerRegistry`/`register_*.ps1` 行号）** |
| 真源与注册表 | 真源目录=`src/zephyr/infrastructure/rollback/`（55 .py，见 §三）。注册表：`docs/registry_of_registries.yaml` 面**未逐条反查**（本车道限量取证未做）；包内自述清单件 `__init__.py` + `_manifest.py` 存在（`_manifest.py` 是"静态清单机生"候选真源，须读）。 | 半 |
| 门禁与质量尺 | 命名即门禁的件有两枚：`commit_quality_gate.py`、`contract.py`/`contracts.py`（契约校验）；另有自检簇 `rollback_verifier.py`（G0 验证自愈的"验证"侧候选）、`rollback_drill.py`（演练）、`rollback_simulator.py` + `cascade_failure_simulator.py`（模拟）、`rollback_abuse_detector.py` + `rollback_loop_detector.py`（防滥用/防死循环）、`knowngoodstate_ledger.py`（已知良好态台账）。**关键判据未做**：这些 gate 是否被 `gate_registry.yaml` 注册并在提交链真跑——**若门不跑即"装饰"**（本车道未证，不得先宣称其为装饰，亦不得宣称其在跑）。 | **缺** |
| 当前运行状态 | **红（按判据保守取红）**：本体存在（绿）、可复跑证据缺失（红）。可复跑命令见 §七，须由后续窗口实跑取绿/黄；本册不代跑结论。 | 红（未验） |

## 三、子模块清单（`ls` 实测穷尽，55 件，按职责聚类；禁凭记忆→全部来自目录实测）

**3.1 核心执行簇（10）**：`rollback_executor.py`｜`rollback_state_machine.py`｜`rollback_verifier.py`｜`rollback_context_restorer.py`｜`rollback_lock.py`｜`rollback_bootstrap.py`｜`rollback_boot_integration.py`｜`rollback_integration.py`｜`rollback_scheduler.py`｜`rollback_wal.py`

**3.2 触发与检测簇（9）**：`auto_rollback_trigger.py`｜`agent_cooldown.py`｜`env_watcher.py`｜`drift_fix.py`｜`rollback_abuse_detector.py`｜`rollback_loop_detector.py`｜`rollback_target_staleness.py`｜`semantic_similar_detector.py`｜`vulnerability_rescanner.py`

**3.3 快照与存储簇（7）**：`git_infra_snapshot.py`｜`sqlite_dumper.py`｜`s3_snapshot_lifecycle.py`｜`external_merkle_proof.py`｜`checkpoint_gc.py`｜`submodule_sync.py`｜`venv_sync.py`

**3.4 预算与审计簇（9）**：`budget_tracker.py`｜`rollback_budget.py`｜`complexity_budget.py`｜`auditor.py`｜`rollback_audit_nexus.py`｜`forensic.py`｜`intent_archiver.py`｜`topology_change_log.py`｜`knowngoodstate_ledger.py`

**3.5 安全与合规簇（7）**：`kill_switch.py`｜`credential_rotation_trigger.py`｜`secret_rotation_aware.py`｜`hallucination_guard.py`｜`right_to_be_forgotten.py`｜`semantic_rollback_tag.py`｜`contract.py`/`contracts.py`（契约，计 2 件则本簇 8）

**3.6 模拟与演练簇（4）**：`rollback_simulator.py`｜`cascade_failure_simulator.py`｜`rollback_drill.py`｜`forward_fix_runner.py`

**3.7 交付与运维簇（5）**：`runbook_generator.py`｜`rollback_dashboard.py`｜`warm_standby.py`｜`temporal_context_adapter.py`｜`cross_platform_shell.py`｜`__init__.py`/`_manifest.py`（包自述，2 件）

**3.8 三源交叉状态**：本清单目前只有 **`ls` 单源**实证。任务要求"`ls`+`grep`+注册表三源交叉穷尽"——`grep`（谁 import 本包）与注册表（`_manifest.py`/ROOR/module_translation_registry）**未做**，故 §三 判"半穷尽"，缺向记在 §六。

## 四、堵点与病灶

| # | 现象 | 根因（本册可证部分） | 修法草案 | 工作量 | 本车道可修？ |
|---|---|---|---|---|---|
| 1 | 55 件包无一份作业簿（92 分诊册判"零作业簿"），总册却标 `built` | 该包从未经六向取证；`built` 判定来自目录存在性而非消费链闭合 | 补 §二 缺的 3 向（下游消费 / 自动化触发注册名 / 门禁真跑证据）后回写总册 | 1 取证工单（约 15 次工具调用） | 否（本车道限量取证已用尽） |
| 2 | 包体量与"回滚"这一动作的常识规模严重不匹配（55 件 vs 通常 executor+verifier+lock 三件） | 未证伪前不下结论；两种假设：①分阶段长出的能力簇（合理）②同域重复簇（如 `budget_tracker` vs `rollback_budget`、`contract` vs `contracts`、`rollback_integration` vs `rollback_boot_integration` 三对同名异体） | 对三对候选做 `grep -c` 消费方计数；零消费者按 w5_1"零触发零消费→退役"出判据清单（**只登记不删**，注册表净删=Owner 门位） | 0.5 工单（三对×2 命令） | 可（后续窗口） |
| 3 | 宪法 §9.3 红线风险：包内有 `rollback_scheduler.py`/`env_watcher.py`/`checkpoint_gc.py` 型命名，若走 cron/Timer 即违"reconciler 必事件触发" | 未读实现 | 读 `rollback_scheduler.py` 触发机制；若 cron 型→立案（改事件触发或声明豁免） | 0.3 | 可 |
| 4 | `rollback_drill.py`/`simulator` 产出的演练记录是否落库无证据（对比：DR 域有 `logs/dr_drill_*.json` 记录面，本包对应物未找） | 可恢复性零实证的同型病灶（DR 备份域已有前例：`last_backup_status=failed` 且可恢复性无实证） | 定位 drill 输出路径 + 最近一次实跑时间；无=红，登记"可恢复性无实证" | 0.3 | 可 |

## 五、内收与合并机会（四判据逐条）

- **同真源可派生→必并**：`_manifest.py` 若为机生清单，则任何散文式"回滚能力列表"都应从它派生（宪法 §9.5 静态清单禁手工）。当前本册 §三 是手工 `ls` 产物，**已声明为临时取证面**，正式真源应改由 `_manifest.py` 派生。
- **零触发零消费→退役**：§四病灶 2 的三对同名异体候选（`budget_tracker`↔`rollback_budget`、`contract`↔`contracts`、`rollback_integration`↔`rollback_boot_integration`）＋ §3.2 检测簇中未见调用方的件 → 出候选退役清单（判据=全仓 `grep -rn "import <mod>"` 零命中；**本车道未跑，故只列候选不出判据**）。
- **同域重复簇→收敛唯一**：`external_merkle_proof` / `forensic` / `intent_archiver` / `topology_change_log` 四件同为"留痕"职责，若消费面重叠应收敛为单一日志真源。
- **跨域不同对象→不并**：本包 `kill_switch.py` 与 F 号安全域 `security/access_control/kill_switch.py` 同名不同对象，**不得并**（并即破坏访问控制语义）；`rollback_dashboard.py` 与 m6 前端域（F111-F115）异对象，只挂引用不重挖。

## 六、自审闸三态

**判：待挖**（不因"写了这本册"而升格为挖干）。

缺哪几向、要装什么最小观测量：

1. **下游消费向（缺）**——最小观测量：一条 `grep -rn "from zephyr.infrastructure.rollback" src/ scripts/ tests/` 命中清单 + 至少 1 个非 tests 消费方 file:line。当前为零取证。
2. **自动化触发向（缺）**——最小观测量：`rollback_scheduler.py`/`auto_rollback_trigger.py` 的注册名（计划任务名 or `SchedulerRegistry` 条目 or `register_*.ps1` 行号）；若为事件触发则给发射方 file:line。
3. **门禁与质量尺向（缺）**——最小观测量：`gate_registry.yaml` 中是否存在 rollback/`commit_quality_gate` 条目（条目 id + `own_scope` 字段）＋该 gate 的一次真实拒绝样本（日志或测试）。二者皆无＝判"装饰"（须实测后才写，本册不预判）。
4. **§三 三源交叉（半缺）**——最小观测量：`ls` 已给；`grep` import 反查与注册表（`_manifest.py` 读 + module_translation_registry 条目）各一。

**本册拒绝挂 F107 认领锚**：上述 3 向缺证，按 92 分诊册 §三反假绿逻辑与本轮任务判据红线，挂锚＝假 covered。宁可留 uncovered。

**回写总册建议**（不自行改总册）：`00_全环节总册.md:182` 的 `built` 应降为 `partial`/`unverified`——理由是"包体存在但消费链与触发链无实证"，非"包未建"。

## 七、复核命令

```bash
# 1) 包体规模与聚类复核（本册 §三 唯一实证来源）
ls src/zephyr/infrastructure/rollback/*.py | wc -l
ls src/zephyr/infrastructure/rollback/

# 2) 下游消费向缺证的最短补法（本车道未跑，交下一窗）
grep -rn "infrastructure.rollback" --include=*.py src/ scripts/ tests/ | grep -v "^src/zephyr/infrastructure/rollback/"

# 3) 自动化触发向（计划任务面）
schtasks /query /fo LIST /v | grep -i "rollback" ; grep -rn "rollback" config/ --include=*.yaml | head

# 4) 门禁向：是否注册在 gate 真源
grep -n -i "rollback\|commit_quality_gate" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml

# 5) 同名异体三对的内收候选判据（只判零消费，不删）
for m in budget_tracker rollback_budget contract contracts rollback_integration rollback_boot_integration; do printf "%s " $m; grep -rn "import .*$m" --include=*.py src/ | wc -l; done
```
