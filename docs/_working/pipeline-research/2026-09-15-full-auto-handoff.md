---
ttl: task_bound
---

# C6 全自动管线总交接——第一至五组全部施工（Owner 2026-09-15 03:37 令）

> Owner 原令要点：全部施工不停歇、不提问、自裁定、登记+跳过不可裁定项、红蓝对抗、
> 连续两次测试 0 问题才算过、GitCommitGateway 落地、临时文件清理、全部完成后才汇报。

## 任务一句话

按已圈定的 **A 方案**（Owner 2026-09-15 03:15 批复），完成 C6 全自动入库管线第一至五组全部施工，
使系统达到"新策略从及格到进模拟盘零人工，Owner 仅保留 sim→production 签字"的终态。

## 治理边界（已锁定，无需再裁定）

- **A 方案**：机器自动到 sim（预授权三条件：§8 双窗过 ∧ BH-FDR q≤0.10 ∧ 无未决衰减预警）；
  sim→production 仍 Owner 门（`OwnerTokenGuard` 已实装，机器流程不带 token 天然停门）。
- **写入路径 fail-closed**：`intake.py` 的注册表写入器目前抛 NotImplementedError——
  验收⑥历史批回放一致率 ≥5/6 达标后开启。Owner 已令不留裁定项 → **回放达标即视为 Owner 复核通过**，
  达标证据落盘留档即可开启，无需等待。
- KillSwitch 联动 / 月度审计 / 告警 = 人类回路，不阻塞流程，永久保留。

## 项目背景（30 秒版）

ZephyrAlpha=个人 A 股量化系统，100% AI 开发。策略管线=C1 海选→C2 粗筛→C3 翻译→C4 快筛批测→
C5 聚类去重→C6 转正入库→挂图→PP-001 配比。auto_mount（MOD-BT-171，挂图器）与 strategy_pipeline
（MOD-BT-187/188/189：BH-FDR 门/生命周期 FSM/intake 编排）已落地（commit 链：43f84d01d5→61b256e81f→
6b63c056db→5fb1b4c8dc→9c009b1542→6c3bf86b40），26+24 测试全绿。剩余=本清单第一至五组。

## 必读文件（完整路径，按优先级）

1. `D:\ZephyrAlpha\AGENTS.md` ← 宪法 L0（冷启动序列+硬规则，FIRST-READ）
2. `D:\ZephyrAlpha\docs\_working\pipeline-research\2026-09-15-full-auto-pipeline-research.md` ← 方案真源（挖矿六向+五段管线+验收七条）
3. `D:\ZephyrAlpha\docs\_working\pipeline-research\2026-09-15-full-auto-handoff.md` ← 本交接（任务清单+自裁定协议）
4. `D:\ZephyrAlpha\docs\_working\archive\2026-09\2026-09-15-auto-mount-construction.md` ← auto_mount 交底（坑五条+用法速记）
5. `C:\Users\fanzi\.zcode\cli\memories\projects\zephyralpha-88c39a4848e315f8\memory\automount-construction-20260915.md` ← 接班记忆
6. `D:\ZephyrAlpha\docs\01_policies_and_standards\sop\construction_sop\construction_workflow_policy.md` ← 15 步施工闭环 SOP
7. `D:\ZephyrAlpha\docs\01_policies_and_standards\sop\backtest_system_sop\sop_c_strategy_library_intake.md` ← SOP-C（§5 差异化/§6 挂图/§8 双窗土规）

## 核心工作文件（完整路径，全部已入库）

- `D:\ZephyrAlpha\src\zephyr\strategy_pipeline\__init__.py`（包声明）
- `D:\ZephyrAlpha\src\zephyr\strategy_pipeline\bh_fdr.py`（MOD-BT-187，BH-FDR 纯函数门）
- `D:\ZephyrAlpha\src\zephyr\strategy_pipeline\lifecycle_fsm.py`（MOD-BT-188，candidate/sim/production/shelved/retired 五态 FSM+SimPromotionGuard+OwnerTokenGuard）
- `D:\ZephyrAlpha\src\zephyr\strategy_pipeline\intake.py`（MOD-BT-189，run_intake 编排：FDR→聚类→差异化→入册→挂图→sim；写入路径 fail-closed）
- `D:\ZephyrAlpha\scripts\backtest\auto_mount.py`（MOD-BT-171，挂图器 production；--plan/--apply/--replay/--audit）
- `D:\ZephyrAlpha\src\zephyr\shared\lifecycle\state_machine.py`（StateMachine 泛型基类，勿改）
- `D:\ZephyrAlpha\src\zephyr\data\scheduler.py`（DataScheduler：subscribe("task_completed")/emit_event，二期接线点）
- `D:\ZephyrAlpha\src\zephyr\shared\event_bus.py`（EventBus/EventType，管线事件类型扩展点）
- `D:\ZephyrAlpha\scripts\backtest\strategy_screen_query.py`（bothwin 子命令=及格判定，文件粒度键 sid+source_file）
- `D:\ZephyrAlpha\scripts\backtest\c4_batch_screen.py`（C4 批测入口，幂等四键）
- `D:\ZephyrAlpha\scripts\backtest\translated\_c4_engine.py`（run_backtest/daily_net_returns/Deflated Sharpe）
- `D:\ZephyrAlpha\config\trading_decision_map.yaml`（地图真源 4300+ 行，文本级手术 only-add）
- `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\strategy_registry.yaml`（注册表真源 157 条，STR-VREV-026 已带 family_redundancy 结构化块先例）
- `D:\ZephyrAlpha\src\zephyr\security\access_control\kill_switch.py`（KillSwitch，reset requires owner）
- `D:\ZephyrAlpha\src\zephyr\trading\validation\decay_watch.py`（run_decay_check 分档巡检）
- `D:\ZephyrAlpha\scripts\backtest\sim_paper_ledger.py`（模拟盘台账，验收⑥回放与第 15 项用）
- 测试：`D:\ZephyrAlpha\tests\strategy_pipeline\`（test_bh_fdr/test_lifecycle_fsm/test_intake，26 用例）、
  `D:\ZephyrAlpha\tests\backtest\test_auto_mount.py`（24 用例）、`D:\ZephyrAlpha\tests\trading\test_decision_map.py`（61+19 用例）

## 施工任务清单（第一至五组，按序执行）

### 第一组：C6 管线本体收尾
1. **二期接线**：DataScheduler C4 批测任务 `task_completed` 回调 → 调 `zephyr.strategy_pipeline.intake.run_intake`
   （新事件处理器注册在调度器侧；禁 cron/Timer；事件不丢=KillSwitch 激活时调用方重试语义落地）。
2. **验收⑥ 历史批回放**：用 2026-09-14 C5 批（及格 8 条，人工裁定=TSMALL/VAL/MOMTREND/VREV-026/DABAN-023
   转正+bluechip_ma/crash_dodge redundant）回放机器三轴论证，一致率 ≥5/6 达标 → 证据落盘
   `docs/_working/pipeline-research/acceptance6-replay.md` → 视为 Owner 复核通过。
3. **注册表写入器实装**：替换 intake.py 的 NotImplementedError——文本级手术追加 STR-* 条目
   （safe_write_text CAS+creation_token 管线化+编号递增，照抄 auto_mount 的 only-add 语义+块内唯一锚模式；
   family_redundancy 块同步写入）。
4. **挂图调用集成**：intake 在入册成功后实调 auto_mount（subprocess 或 import 复用 run 路径）→ 挂图报告落
   `docs/_working/auto-mount-reports/`。
5. **E2E 端到端联调**：模拟真实批测完成事件，实测验收①（≤10 分钟全链：事件→candidate→挂图→sim→报告）。
6. **收尾义务**：MOD-BT-187/188/189 depgraph 流转核验；SOP-C §5/§6.2 退役标注（净零声明兑现，
   E 类规则变更走规则册留痕）；construction_progress_tracker.md 登记。

### 第二组：上游供料自动化
7. **C4 批测自动触发**：翻译件落盘事件 → 自动批测（发现 `scripts/backtest/translated/c4_*.py` 新增/变更→触发 c4_batch_screen --only）。
8. **C2 粗筛接线**：strategy_screen_c2.py 串联进管线。
9. **C1 海选自动化**：lane_b/lane_c 生成器接数据落地事件自动出候选（矿脉已挖：wq-alpha-pipeline overnight 模式）。
10. **C3 翻译管道化论证**：最难项。LLM 翻译+机器质检流水线（知识生效日哨兵 D120 必须保留）；
    若论证结论=不宜全自动化，登记裁定书（按自裁定协议格式）+保持人工，不硬做。

### 第三组：监督与安全自动化
11. **月度审计自动挂载**：auto_mount --audit 挂 decay_watch 同节奏（事件化，非 cron）。
12. **告警通道实装**：管线关键节点（新 candidate/进 sim/审计异常）→ Alerter；推送渠道未定=先落面板+日志告警（已有通道），登记待 Owner 定渠道。
13. **KillSwitch 恢复续跑**：暂停期间事件持久化（task_progress 模式）→ 恢复自动重放。
14. **sim 绩效监控+转正建议书**：sim_paper_ledger → 自动生成转正评估报告（Owner 签字前最后一眼由机器备好）。

### 第四组：Owner 门日常形态（验证项，非施工项）
15. 演练一遍完整 Owner 体验：规则已批→全自动运转→仅 sim→production 需签字→月度扫报告。
    产出 `docs/_working/pipeline-research/owner-experience-runbook.md`。

### 第五组：长尾矿脉（登记即闭环，不施工）
16. LLM 生成策略入口（等评估能力，登记于方案 §1 噪音过滤）；wave-2 数据源（等数据）；
    模拟盘 A 阶段 2026-12-14 首评（**明令勿提前施工**）。

## 自裁定协议（Owner 原令，逐字）

> 遇到问题自己裁定，按照："你作为客观专业架构师，从第一性原理思维出发，长远期战略考虑，
> 针对项目依靠100%ai开发的情况，查看项目所有相关文档的内容，根据专业机构的实践方式，
> 量化社区和氛围编程社区的做法，github有没有合适的开源项目，你给出一个分析过程和裁定结果"。
> 无法裁定的 → 登记（`docs/_working/pipeline-research/pending-owner-rulings.md`）+ 跳过执行下一个任务；
> 堵塞无法跳过的 → 可以停止。

## 施工纪律（硬规则速记）

- 冷启动：`$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH` → `python --version`=3.12.x → `python scripts/lock_files.py cleanup` → reaper 状态确认。
- 施工前 capability_lookup 留审计（session_id 用 `st-autopipeline-20260915`）；新 MOD 号从 MOD-BT-190 起（187/188/189 已用）。
- 改前 `lock_files.py acquire <file> <sid>`；热文件写入必 safe_write_text CAS。
- 提交唯一正道：`python scripts/git_commit.py --session st-autopipeline-20260915 --files <清单> --message "<msg> [GW:st-autopipeline-20260915] no-lookup:continuation" --enqueue` → `python scripts/commit_queue.py drain` → `git log -1 --name-only` 核实归属 → 幻影删除 `git add` 回填。
- docs/_working/ 根目录 120 文件硬上限（FOLDER-CAPACITY-HARD-LIMIT 会拦）——新文档一律进
  `docs/_working/pipeline-research/` 或既有子目录；死了的队列项不 requeue（路径变更快照失效），直接重新 enqueue。
- pytest 姿势：`python -m pytest <文件> -q -o cache_dir=.runtime/tmp/pc`；循环验收=连续 2 轮 0 错误。
- 禁 cron/Timer/裸 git commit/裸 duckdb/裸 getenv；事件驱动 only。

## 完成标准（全部满足才停）

1. 第一至五组任务全部 done 或"登记+跳过"（登记清单见 pending-owner-rulings.md）。
2. 全量测试面（tests/strategy_pipeline + tests/backtest/test_auto_mount + tests/trading/test_decision_map
   + 受影响域）**连续两次运行 0 错误**。
3. **红蓝对抗测试**：对管线新代码做红队攻击（伪造事件重放/FSM 越权直跳/FDR 挑尾/并发双触发/
   KillSwitch 中途触发/注册表 CAS 冲突），蓝队验证全拦；发现即修复。
4. GitCommitGateway 全部落地（队列 done+归属核实+幻影回填+claim 释放）。
5. 临时文件清理：`.openclaw/tmp/*.py` 本班脚本、`.runtime/tmp` 本班产物清掉（staging 层由 reconciler 管）。
6. 最终汇报（Owner 醒来一次性看）：完成清单/裁定书/登记的待裁定项/测试证据/commit 链。
