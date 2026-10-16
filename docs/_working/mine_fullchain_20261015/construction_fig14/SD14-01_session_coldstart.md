---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-01
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-0-session-冷启动前置必做 + 附录 D 锚块
---

# SD14-01 Session 冷启动（policy Step 0）

## 1. 定义

任何新 AI session 开始施工前的强制前置段：守护进程启动 + 必看文件加载 + Session Continuity 恢复 + Phase Manager 检查 + LifecycleManager boot_sequence + boot_hooks 自动钩子确认。就绪判据实体在图11 D11-S01（门控引擎+会话注册表），本段只作交接（role=handoff，handoff_to=D11-S01/D11-S02/D11-S09）。通过判据=守护进程 running / 必看文件加载 / Session 状态恢复 / boot_sequence 11 步全 PASS。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 施工任务令；AGENTS.md §0 冷启动序列；上一班 handoff 交接包（含 pending_tasks/warnings，MUST 读） | `AGENTS.md` §0；`.runtime/handoffs/handoff_<sid>.json`（政策 Step 0 行 162 指认）；`docs/01_policies_and_standards/policies/parallel_session_coordination_policy.md` |
| 输出面 | Session 就绪状态（无结构留痕面；就绪结论按 fallback 人工核） | 图 YAML `config/construction_workflow_map.yaml#D14-01`（anchor_kind=handoff, exec_source=null）；fallback 条款"逐项人工核，不阻塞进 D14-02" |
| SSOT 真源 | 政策 Step 0 节 + 附录 D 机读锚块 step_anchors[0]；宪法 AGENTS.md §0 冷启动序列（并行真源，两处口径并存） | `docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md` L106-172；同文件 L1095-1143 锚块；`AGENTS.md` §0 |
| 代码模块 | 实测可跑入口=`scripts/governance/meta/session_startup_check.py`（--json/--phase，本批实跑有输出）；锁清理=`scripts/lock_files.py`；boot 链=`src/zephyr/trading/lifecycle_manager.py`（§boot_sequence 11 步）、`src/zephyr/trading/boot_hooks.py`（§register_boot_hooks 18 钩子）、`src/zephyr/governance/ops_governance/event_hook.py`（§HookRegistry）。**幽灵件**=`scripts/ide_health_service.py`（全仓不存在，本批 ls 复证） | 上述文件均实存核验（2026-10-15）；幽灵件证据=D14-G01 |
| 门禁约束 | ABS-01~08 全流程红线（trae_018）；SECRETS.md 密钥纪律（bare_getenv_gate 拦裸 getenv）；RULE-GUARDIAN（reaper 计划任务存活是写操作前提） | `docs/01_policies_and_standards/rules/trae_018_behavior_code_prohibition.yaml`；`SECRETS.md`；`AGENTS.md` §0.2；`scripts/register_process_reaper_task.ps1` |
| 自动化触发 | LifecycleManager.boot_sequence() 11 步系统级自动 boot（任一步失败 break）；boot_hooks 18 个后台钩子（任务 6+事件 6+永久系统 6）；triple_alignment_on_verified 在任务 VERIFIED 时自动触发三方对齐；heartbeat daemon 每 30s 刷活性 | `src/zephyr/trading/lifecycle_manager.py`；`src/zephyr/trading/boot_hooks.py`；`src/zephyr/gov_enforcement/rule_bridge/session_worktree.py`（heartbeat_daemon） |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 任务令/冷启动序列/handoff 包三路输入路径全在册 |
| 输出面 | warn | 就绪状态无结构留痕面（exec_source=null），靠 fallback 人工核兜底 |
| SSOT 真源 | pass | 政策锚块 D14-01 在册（附录 D 实读），宪法并行真源在册 |
| 代码模块 | fail | 政策点名守护件 `scripts/ide_health_service.py` 全仓零命中（D14-G01/G02 引用面 41 文件 89 处），实测可跑入口未被政策指认——政策-实现漂移未收口 |
| 门禁约束 | pass | ABS/SECRETS/RULE-GUARDIAN 三层约束件全在盘 |
| 自动化触发 | pass | boot_sequence/boot_hooks/heartbeat 三条自动化链实盘在跑（本批 process_reaper --status 实跑 source=live） |

## 4. 缺口与建议

- 缺口1（D14-G01/G02，红）：政策 Step 0 两行命令的守护件不存在；ghost 引用面实测 41 文件/89 处（catalogs 册内 7 文件 15 处在册可证）。建议：政策改指认 `session_startup_check.py` 为冷启动可机验锚（政策文 L118-119 已有 2026-10-04 更正注记，但 Step 0 命令块仍列幽灵件——改版未彻底），并按净删门位清理 41 处幽灵引用。
- 缺口2：政策称 phase_manager gate_* 唯一名 46，实扫 58（图 evidence 在案）——散文计数违规（宪法 §4.4 计数用字段）。建议：政策删死数改指运行时。
- 缺口3：本段与 AGENTS.md §0 冷启动序列是同一动作的两套真源（政策 Step 0 vs 宪法 §0），R-02 在案。建议：总包裁定唯一编排真源，另一方纯引用。
