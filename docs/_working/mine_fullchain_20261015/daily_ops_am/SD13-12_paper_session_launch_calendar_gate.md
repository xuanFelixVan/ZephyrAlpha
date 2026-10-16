---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-12
segment: fig13-A 盘前
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-12 模拟盘会话拉起 + 交易日历闸

## 1. 定义

交易日 09:25（Windows 计划任务 ZephyrAlpha_PaperSession，Daily 触发非 AtLogOn）经包装脚本拉起常驻模拟盘适配器；日历闸在包装层而非槽层（自带 is_trading_day 查），拉起前另查 QMT（XtMiniQmt）。三态留痕：正常 START / 非交易日 SKIP(is_trading_day=False) / QMT 未开 SKIP。决策问题：09:25 会话拉起来了吗？非交易日与 QMT 未开各算哪种 SKIP？

地图在册态：wiring=wired、build=built、skeleton ✅。地图 admission 注记：本格拉起腿自带 QMT 与日历双查，只代管 D13-09 门 C1 一条腿与「开不开市」判定，门体本身零在位。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 计划任务触发 + 包装脚本双查（is_trading_day + XtMiniQmt 进程） | `scripts/tasks/register/register_paper_session_task.ps1:67`（触发器声明面）；`scripts/start_paper_session_daily.ps1`（包装层双查，D13-09 锚 :61） |
| 输出面 | 常驻适配器进程 + .runtime/logs/paper_session.log 三态留痕（当日 09:25:03 起 + 两类 SKIP 各在案） | `.runtime/logs/paper_session.log`（exec_evidence 复跑记录）；`src/zephyr/ex_core/live_strategy_adapter.py` |
| SSOT 真源 | 图13 节点契约（行 995-1070）+ 注册脚本声明面 | `config/trading_day_cycle_map.yaml#D13-12`；`scripts/tasks/register/register_paper_session_task.ps1` |
| 代码模块 | 注册 ps1 + 包装 ps1 + 常驻适配器（MOD-L06-001） | `scripts/tasks/register/register_paper_session_task.ps1:67`；`scripts/start_paper_session_daily.ps1`；`src/zephyr/ex_core/live_strategy_adapter.py` |
| 门禁约束 | 日历闸语义=is_trading_day 查在包装层（非槽层）；fallback=D13-42 三路守护心跳腿（陈旧则 schtasks 重跑）；.ps1 纯 ASCII 铁律 | `config/trading_day_cycle_map.yaml#D13-12` note_zh/fallback；feedback_loops D13-42→D13-12 边；`AGENTS.md` §9.7 |
| 自动化触发 | mechanism=B_windows_task，交易日 09:25 每日一次拉起；trigger_facts last_run=2026-10-08T09:25:01；schtasks registered=true+declared_in_register_scripts=true 机生双证 | `config/trading_day_cycle_map.yaml#D13-12` trigger_facts/machine_facts.schtasks_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 双查（日历+QMT）在包装层实存 |
| 输出面 | pass | 三态留痕各在案（START/非交易日 SKIP/QMT 未开 SKIP） |
| SSOT 真源 | pass | 节点契约+注册声明面+机生 schtasks 双证 |
| 代码模块 | pass | 注册/包装/适配器三层实存实核 |
| 门禁约束 | pass | 日历闸与守护心跳接缝（feedback 边）在册 |
| 自动化触发 | pass | 交易日每日 09:25 拉起留痕连续 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无；本格是 admission_edges 第一条（D13-09→D13-12）的下游——现行只被 C1 代管，门体施工后应改为读裁定行。
- gap_refs 空。
- 建议：D13-09 施工波落地后，本格拉起前查改为消费就绪门裁定产物（避免 QMT 双查口径与门 C1 永久分叉——进程名 XtItClient vs XtMiniQmt 分裂已由地图点名）。
