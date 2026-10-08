---
created: 2026-10-08
session: st-t3c-ops
ttl: task_bound
completes_when: 停跑因诊断报告（根因+证据链）+低峰窗重启前后取证+心跳复核+16:05 复核判读落地（在线=09-30 补跑/仍败=升级呈报件）
---

# 车道C·调度器停跑诊断与重启 作业簿（st-t3c-ops）

> **Owner 已批裁定原文**：「③复市前低峰窗重启调度器+排查 10-05 后停跑因；①若 10-08 复核仍三连败→QMT 人工拉起观察一周（不自启），09-30 净值补跑在 QMT 在线窗」
> **任务**：①挖矿：调度器宿主形态（服务/计划任务/进程）+10-05 以来日志链逐日定位停跑因+automation-bf37505c 复核件路径与判读；②施工：停跑因诊断报告（根因+是否需代码修复——需修则小修带测试，他域大修登记呈总包）+低峰窗重启（前后各取证：重启前快照+重启后 15 分钟心跳）+10-08 16:05 复核判读（QMT 在线→跑 python scripts/run_post_settlement.py 2026-09-30；仍败→出升级呈报件，不自行拉起不自启）。
> **产出落点**：本目录全部报告+取证；仓库面仅前置诊断确需小修时才有。

## 1. 挖矿台账（六向，每向≥1 发现或"已查无"）

| 向 | 发现/已查无 | 证据锚 |
|---|---|---|
| ①上游（调度器宿主与登记处） | Windows 计划任务 \ZephyrAlpha_PostSettlement：现态 Enabled+Ready，MON~FRI 15:30，StartBoundary=2026-10-05T15:30（10-05 首修重注册日），StartWhenAvailable=true/IgnoreNew/30min 上限；上次运行 10-07 15:30 result=0（真实执行），下次=10-08 15:30 | 02_pre_restart_snapshot.txt（schtasks /v + XML）；scripts/tasks/register/register_post_settlement_task.ps1（FIX 2026-10-05/07 注释） |
| ②下游（被调度作业清单） | 单作业=run_post_settlement.py（结算+审计+VaR 归档+GAP-F-29 净值腿 ch_writer 正门）；脚本缺省结算日=最近交易日回推含今天 | scripts/run_post_settlement.py 头部 [DEPENDENCIES]/docstring |
| ③算法/机制（调度机制/依赖） | 断链机理=scripts 拆簇 a4b503a163（10-02 20:11）致注册 ps1 深三级 Join-Path '..' 失准→cmd 重定向打不开→python 从未拉起→LastTaskResult=0 假绿；修复=源码 a67d6922588（HEAD 祖先实证）+运行态重注册（XML Action 三要素本车道独立核验正位） | a4b503a163/a67d6922588；§2 独立复核 |
| ④后端（日志链/监控面） | 六块逐日链：09-24×3 成功（QMT 连接成功 L6）→09-28 成功+净值落库→09-29 三连败①（L86-88）→09-30 三连败②（L108-110）→10-07 15:30 三连败③（L130-132，mtime=10-07 15:30=真实执行铁证）；qmt_watchdog 止于 10-02 12:55；TaskScheduler 事件通道零事件（已查无） | data/runtime/post_settlement_last_run.log（行级锚=01 报告 §3）；qmt_watchdog.log；Get-WinEvent 实测 |
| ⑤前端（仪表盘可视面） | 本车道未动仪表盘；复核自动化 automation-bf37505c（ZCode 侧）今日 16:05 自动出三态判定——本车道不创建不改动 | 总包情报；api_server_desktop.log（只读旁证，未接线改动） |
| ⑥数据字段（停跑窗口逐日证据） | c1_market.account_nav_daily FINAL 全表=1 行（trade_date=2026-09-28，miniqmt_sim，ingest 09-29 09:07+08:00）→09-29/09-30 净值行缺失=「broker 离线净值腿整步不跑」不变式物证；reaper_kill.log grep QMT 零命中（非被 reap）；主机 LastBootUpTime=2026-10-05 16:05:20（10-05 15:30 触发点关机） | reader 通道实测（.runtime/tmp/tail3/ops_tmp/query_nav_reader.py）；reaper_kill.log；Win32_OperatingSystem |

挖干裁定（自审闸三态）：**挖干**——六向全落，根因两层均有行级证据锚；唯一残留=日志块⑤精确写入时刻不可考（日志无时间戳+事件通道未启用，已列 01 报告 §7，不影响结论）。

## 2. 施工记录

- [x] 停跑因诊断报告（根因=①触发链断[已修，a4b503a163 伤/a67d6922588 修+运行态重注册]②QMT 离线三连败[运维域待 16:05 复核窗]；需代码修复=**否**，本车道仓库面零修改）
- [x] 重启前快照取证（02，采集 2026-10-08 03:24:58 +0800）
- [x] 低峰窗重启执行→**判定免重启**：任务已 Enabled+Ready+触发链健康（他队已修+独立复核），取证「已是健康态」即裁定意图达成；禁 /RUN 已守；零任务定义改动
- [x] 重启后 15 分钟心跳取证（04_heartbeat_15min.txt，免重启口径=处置点[02 采集时刻]后 ≥15 分钟状态复核）
- [x] 16:05 复核判读=**总包自动化处置**（16:05 复核窗=总包自动化处置：automation-bf37505c 16:05 三态判定+总包 16:20 一次性自动化接管分支处置；本车道凌晨窗不代跑不等待。本车道旁证：QMT 当前离线——03:14 tasklist 零 xt 进程）
- [x] 09-30 补跑 / 升级呈报件→**待 16:05 复核窗处置**（离线不跑=裁定原文「补跑在 QMT 在线窗」；在线→python scripts/run_post_settlement.py 2026-09-30；仍败→升级呈报，QMT 人工拉起=Owner 明令禁止自行操作）

### 2.1 提交排障台账（capability 册 stomper 战窗口，全仓已知战况见 HEAD ee30722678 自述）

| 批 | 内容 | 状态 |
|---|---|---|
| q-0001 | 注册表单项（04:16 入袋，快照=蒸发后无 token 版；报文误用内容批文案，实际 files=1） | **done=commit c1f8a0da8a** |
| q-0002 | token 先行袋：注册表快照 blob d967937b…（**5 条 tail3_ops token 已 blob 实证**） | pending（排队中，落地后 HEAD 即含 token） |
| 内容批 | ops 五件（00/01/02/03/04 .md） | 待 q-0002 落地后自动补投（HEAD token≥5 即 ENQUEUED，后台循环值守） |

## 3. 取证索引

| 件 | 路径/锚 | 状态 |
|---|---|---|
| 诊断报告 | docs/_working/tail3/ops/01_diagnosis_report.md | 已交付 |
| 重启前快照 | docs/_working/tail3/ops/02_pre_restart_snapshot.md | 2026-10-08 03:24:58 +0800 |
| 处置后快照 | docs/_working/tail3/ops/03_post_restart_snapshot.md | 免重启判定后复核（见件内时间戳） |
| 心跳复核 | docs/_working/tail3/ops/04_heartbeat_15min.md | 处置点后 ≥15 分钟（见件内时间戳） |
| DB 核数脚本 | .runtime/tmp/tail3/ops_tmp/query_nav_reader.py | reader 只读（readonly=1） |
| 事件查询脚本 | .runtime/tmp/tail3/ops_tmp/q_task_events.ps1 | 纯 ASCII |

## 4. OPEN_QUESTIONS

1. 09-29 净值行同缺（裁定仅点名 09-30）——是否一并补跑，留 16:05 复核窗/总包定夺（01 报告 §7 已注记）。
2. QMT 拉起/自启=Owner 明令禁止自行操作（留呈）；本车道未触碰 QMT。
3. capability 册 stomper 战（本车道 token 三度被蒸发，HEAD ee30722678 自证「落袋战争」为全仓已知战况）——本车道以「token 先行袋 q-0002（快照含 5 条 token 已 blob 实证）→内容批后投」队列出清，根治属维护班域。

## 5. 红蓝自检（两轮，≥3 检查点）

**第一轮（证据链三查，对抗视角：每结论找反例）**

| # | 检查点 | 结论 | 反例尝试 |
|---|---|---|---|
| ① | 诊断报告每根因结论有行级证据锚 | PASS | 触发链断=commit a4b503a163/a67d6922588+ps1 FIX 注释+XML StartBoundary 三角互证；三连败=日志 L86-88/L108-110/L130-132；净值缺行=DB FINAL count=1 实测；10-05 关机=LastBootUpTime。未找到无锚结论 |
| ② | 三快照时间线自洽 | PASS | 02@03:24:58→03@03:36:35→04@03:53:24 单调递进，三份任务态一致（Enabled/Ready/下次 15:30）；免重启语义下时间线无断层 |
| ③ | 任务定义语义等价 | PASS | 零改动（未 /change 未 /RUN 未 /delete）——语义等价平凡成立；02/03 两份 XML 逐段一致 |

**第二轮（运维面+合规面）**

| # | 检查点 | 结论 |
|---|---|---|
| ④ | DB 只读零写 | PASS——reader 通道 readonly=1，仅 SELECT/DESCRIBE；核数脚本落 .runtime/tmp（不入仓库） |
| ⑤ | QMT 零触碰 | PASS——未拉起未自启未登录；tasklist 只读探测两次（03:14/03:53 均零 xt 进程） |
| ⑥ | 09-30 未凌晨补跑=合规 | PASS——裁定原文「补跑在 QMT 在线窗」；离线不跑=照裁定；16:05=总包自动化处置 |
| ⑦ | 取证件合规 | PASS（含一次整改）——原 .txt 三件因 DCR-005/006（docs/_working 白名单无 .txt）改名 .md，内容字节仅 GBK→UTF-8 转码零语义变更；快照 schtasks 段为 GBK 控制台输出已转 UTF-8 存档 |
| ⑧ | 提交正门 | PASS（含排障披露）——六次预检被拦均走逃生处方整改（DIRECTORY-CONTRACT 改名/UTF-8 转码、CREATE-GUARD token 先行、WORKTREE-REQUIRED --allow-non-worktree、SESSION-REQUIRED 注册）；token 三度被 stomper 蒸发，终以先行袋 q-0002（blob sha d967937b…含 5 token 实证）+内容批后投出清 |

两轮循环检查零未决问题（⑧队列落地为时序待办非检查缺陷）。

## 16:05 复核判读（automation-c39f6c69 分支处置，16:21-16:3x）

- 三读数：①15:30 实跑 Result=0 ✓ ②尾块 MiniQMT 连接成功+净值落库+exit_code=0 ✓ ③DB 补跑前={09-28,10-08}、09-30 缺。
- 判定 **[SRC-1已恢复]**=分支 A：执行 09-30 补跑成功（MiniQMT 连接/audit PASS/净值落库 rows=1/exit_code=0），DB 终态三行连续（09-28/09-30/10-08）。
- 升级分支（QMT 人工拉起）不触发。详见 05_review_followup_report.md。
