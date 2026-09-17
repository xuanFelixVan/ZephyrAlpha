---
ttl: task_bound
---

# 资源排班 v2 战役 §6/§7 端到端验收证据（st-govmap-20260915）

> 方案真源=`resource_schedule_v2_construction_plan.md`（同目录）。本件=验收轮次的实测留痕：全部为 CLI/库直跑实证，非文档转述。复现入口均为仓内永久真源（.runtime/tmp 脚本已随清场删除）。

## 1. §6 三臂端到端（真实链路，零夹具）

| 臂 | 动作链 | 实测结果 |
|---|---|---|
| A 改真源→全链跟新 | `apply_resource_plan.py` 把 `sch_weekly_factor_eval` 窗改为 `30 5 * * *` → 再生 → 视图重渲 | 表/周历/告警三处同批跟新（slot 时刻=05:30）；臂毕恢复原窗，schedule.yaml 对账 CLEAN |
| B 排班方案→受闸写回 | 恒等方案（81 实体不改）跑 `apply_resource_plan.py --dry-run --skip-schtasks --report-json` | verdict=pass、new_blocks=0；实体定位覆盖 81/81（槽位 21+ps1 24+seed 33+drill 3）；noop 检测正常；方案 schema=裸 task_id 映射（包裹 `patches:` 会被判外来 task_id → rc=2 拒绝，属设计防御） |
| C OS 停用→告警→恢复 | `schtasks /change /disable` ZephyrAlpha_ResourceRegenCheck → 生成器 C-15 臂 | 出 `sched_task_disabled` finding（可送达告警桥）；`/enable` 后复检归零 |

OS 在册态（schtasks 实测，`MSYS2_ARG_CONV_EXCL='*'` 下核验）：ResourceMorningReport 每日 06:31、MeasureCalibration 周六 06:17、ResourceViewPublish 每日 05:50、ResourceRegenCheck 每小时、PatternMining/FactoryLaneC 按表——均 Ready。

## 2. 闸面现盘（提交闸同一代码路径）

- `run_all_checks(config/resource_profile_registry.yaml, now)` → **0 findings**（block=0 / warn=0）。
- `run_pool_concurrency_audit`（C-8）→ **block 0**，warn 1 条=13 个 R-F 同刻声明对（6 实体 `co_start_intent: true` + notes_zh 理由齐全，豁免走判据①）。
- 五源覆盖：ps1/slot/seed/drill/schtasks 全活；`--check` 无漂移（81 实体，generated_at 时间戳外零差异）。

## 3. §7 红蓝对抗（蓝 8 + 红 3 = 11 场景）

- 夹具注入、生产零写入；两轮均 **PASS 11 / FAIL 0 / SKIP 0**（第二轮=代码全部落地后复跑）。
- 测出真缺陷 1 项并已治本：**BLUE-1 退役幽灵池再生死锁**——`check_pool_vocabulary` 对 retired/orphaned_source 也出 block，而 merge_preserve 原样保留其旧池 → 一条退役幽灵池永久 rc=2 锁死全表再生。修复=生成器 :598-604 对不排班状态降级 warn（留痕可见不豁免），修复后双口径断言（活体幽灵=block+拒写零写入；退役幽灵=warn+rc=0 真写出）。
- 误报 3 项经直接读码证伪（C-4 api cron 单源已落 aba769181a；`--publish-alerts` 已接线 generate_resource_week_view.py:281-288 + regen 任务 ps1:67；model_capability_exam 空壳已退役 6a0eca4700）。
- 登记口径风险 2 条（设计使然，报告不修）：
  1. 判据①唯一豁免口=归因失败（非 git 通道写表时 `pileup=False` 只跑预算判据②）——兜底=每小时 `--check --publish-alerts` + 视图，提交时不拦。
  2. `expand_windows` 单表达式 64 触发上限 → 盘中级 cron 28 天只展开首 ~1 周（应 ~220 窗），第 2–4 周盘中同刻堆积不在扫描范围（量化边界已记）。

## 4. P5 实测校准两轮

- 机制批：p90 校准器（MOD-RESCHED-CALIB）+ L-9 晨报生成器（MOD-RESCHED-MORNING）落地并完成**首次执行**（两任务排上表+OS Ready）。
- 校正批（申报值 AI-in-the-loop 裁定）：flag 12→9；改 3（manual_factory_grid_executor 240→580min/4.0→2.7GB、manual_kronos_adapter 60→5/6.0→0.5、sch_process_reaper 1→6min）；HOLD 5（c4_exam/post_settlement/ollama_serve=脱管子进程树同源孤儿事故、factory_lane_c=尖刺采样相位、worktree_drift_watchdog=常驻寿命≠单次执行，理由入 notes_zh）。余 9=HOLD 项周复报提醒环，属设计。

## 5. 测试两轮 0 问题（§6-4 口径）

- 电池=13 个 resource_schedule 系测试文件 + capacity_budget 单元：`343 passed`（第一轮=红蓝缺陷治本+conftest sys.modules 快照迭代修复后；第二轮=全部代码落地后复跑），两轮连续 0 失败。
- 期间测出并修复 2 处陈旧钉（本战役自家改动导致）：gate 测试活体表臂按 R-F 口径改钉（6 声明实体+notes 非空+豁免对计数≥声明数）；api_server cron 月班测试改为**从活体表推导**期望时刻（钉死字面量会让未来合法改相连环红）。
- 另治本 1 处共享设施竞态：`tests/conftest.py` 污染哨兵 teardown 迭代 `sys.modules.items()` 无快照，他线程 import 时偶发 `RuntimeError: dictionary changed size during iteration` → `list()` 快照（两行）。

## 6. 残余登记（Owner 门位/禁写区交接，非本车道可闭）

- Windows 在册态改相：`--apply` 只动文本真源，OS 侧需重跑对应 `register_*.ps1`（工具 os_reconcile_note 已写明）；ops_daily/weekly_vm_backup 实为 06:00 同刻（R-D planned 不计账）时刻改动留 Owner。
- 外来孤儿任务 AltFxECB 挡 `--check`（现 `--skip-schtasks` 绕行）；4 个一次性实验任务+NightlySentiment 删除留 Owner。
- 禁写区交接：measure_calibration / resource_morning_report 两蓝图（docs/03_modules/** 待建，N-15 走 --skip-naming-check 豁免留痕）；L-6 map_node_id 灌数与 C-12 CONSUMERS 登记归注册表车道。
- C-11 声明反查缺口 7 条=warn 档（真源不点名，逐条可查 `--check` 输出）。
