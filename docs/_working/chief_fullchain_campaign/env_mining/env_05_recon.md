---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_05_recon.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-05 数据对账修复 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/data_supply_chain_map.yaml segments[S5_recon]；血肉卷=docs/_working/map_build/fig12_datachain/05_对账修复六环.md
- **职责一句话**：检测/任务级对账/回补/修复/互验/维护/自愈构成的反馈环
- **节点清单（11）**：DSC-13 完整性巡检+新鲜度哨兵(built)｜DSC-14 缺口回补三通道(partial)｜DSC-14D 第四通道事件自动回填(pending)｜DSC-15 日终三账对账(pending)｜DSC-16 坏数据修复与回补器族(partial)｜DSC-17 一致预期双向互验(built)｜DSC-18 CH 存储维护 OPTIMIZE(partial)｜DSC-19 破损 part 自愈探测器(partial)｜DSC-20 任务级对账(built)｜DSC-GAP-TERMINUS 域终点不可证(pending)｜DSC-GAP-RECDIFF 差异表0行(pending)
- **状态分布**：built=4 / partial=4 / pending=3（与 counts.segment_S5_recon=11 合）

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 全网/外部 | 判定 |
|---|---|---|---|
| ①上游 | 边：DSC-06→DSC-13（被检对象=在库数据）、DSC-13→DSC-20（同宿主两轴检核）、DSC-20→DSC-14（漏跑清单=catchup 唯一基准）、DSC-14→DSC-16（补不回转修复）、DSC-16→DSC-18（修复后 OPTIMIZE 逐位验证）、DSC-19→DSC-06/16（自愈反馈环）。触发面：23:00/06:50/07:10/23:30 特殊槽＋周度 OS 任务（ZephyrAlpha-CH-OptimizeMerge-Weekly）＋进程内 300s 常驻 | — | signal |
| ②下游 | 消费方：catchup_guard 基准+CLI status+告警件三族（图 consumers）；src/zephyr/data/integrity_checker.py:5 [CONSUMERS] scheduler.run_schedule("integrity_check")；catchup_guard.py:5 [CONSUMERS] "前端缺口对账卡片(二期)"。案卷实存：data/failures/20260924/0928/0929/0930_integrity_check_task_reconcile_*.json 四件（10-01 起国庆停＝节拍闭合旁证）。DSC-15 生产调用方精查：run_daily_reconciliation 全仓仅模块自身 __main__（recon_runner.py:31/:35）＋__all__(:101)＋生成器文案＝**未接线复核成立** | — | signal |
| ③算法机制 | 四计数算法在码：integrity_checker.py:285-305（should_run/succeeded/missing/failed）、案卷产出 :468；catchup_guard 三通道分派（catchup_guard.py:44 _WEEKLY_SCHEDULES/:46 daily 槽集/:52 _SKIP_SCHEDULES/:68 tmp/catchup_guard.lock，单批限量+trading_day_only 顺延+RUNNING 跳过）；DSC-19 CHECKSUM→STOP MERGES→DETACH→审计（scheduler.py:1264 _AUDIT_LOG=data/local_fallback/corrupted_parts_audit.jsonl、:1327 写审计函数——**审计件至今不存在（ls 无此文件）＝零触发+应建未建复核成立**）；DSC-17 disabled 服务闸（consensus_crosscheck.py:62/:287；data/runtime/consensus_crosscheck.disabled 不存在＝闸未挂在跑）；optimize_merge.py optimize_partition dry-run 幂等+失败 False 不中断批 | — | signal |
| ④后端代码 | src/：integrity_checker.py、supply_sentinel.py、calendar_coverage_checker.py、alerter.py、backfill_checker.py、catchup_guard.py、c4_history_repair.py、consensus_crosscheck.py、auto_backfiller.py、scheduler.py（DSC-19 宿主）、trading/recon_runner.py＋ex_core/eod_reconciliation.py（DSC-15 双件）。scripts/：ch/optimize_merge.py、data/repair_kline_degraded_pull.py（TRACKED）、data/backfill_tick_depth5.py（**UNTRACKED 在盘不在 VCS**，本批逐件核验坐实政策点名回补器仍有未纳管件）。tests/：integrity_checker/catchup_guard 有 [TESTS] 自锚（tests/zephyr/data/test_catchup_guard.py 等）；auto_backfiller 仅 tests/legacy_zephyr/data/test_auto_backfiller.py＋包级 re-export＝**零生产调用方复核成立（DSC-14D 死判维持）** | — | signal |
| ⑤前端呈现（只登记不施工） | src/zephyr/frontend/dashboard/api_server.py:1633-1634 检核器中文标签（"integrity_check 完整性巡检（23:00）"/"catchup_guard 错过补跑（05:30）"）；**:1638 自注缺陷"硬编码 catchup_guard 03:30 vs 真源 05:30 漂移 2 小时"**＝前端已有已知漂移在册（只登记） | — | signal（登记） |
| ⑥数据字段 | 台账/案卷面：known_data_gaps.yaml 状态全量分布（本批实数）＝open 19/accepted 19/resolved 13/completed 7/no_source 6/monitoring 5/mitigated 4/retired_quarantine 1——**open+monitoring=24 未了账**（图判词量化确认）；integrator_progress.db task_runs/task_progress、cross_validation_log（check_date 口径，禁用 check_time——09-21 起恒 epoch 在册）、reconciliation_differences 0 行、corrupted_parts_audit.jsonl 应建未建。DB 只读读数本批不直查＝实查待施工批 | — | signal/实查待施工批 |

## §2 挖干自评

- **三扫收敛?** 收敛。三轮后新发现两项均为登记滞后/精确化（DSC-16 未纳管件坐实到具体文件；前端 03:30/05:30 漂移注释），无新病灶。
- **未挖长尾清单**：(a) supply_sentinel 阈值配置逐条（data_supply_sentinel.yaml 未逐条展开）；(b) alerter webhook 外发通道的 CRITICAL 名单；(c) optimize_merge 空串假成功（:138 原判）是否已在 10 月维修窗修复＝待验证（本批仅读到 dry-run 段，未见 exit 1 兑现证据）；(d) 19 个 open 缺口逐条 vs DSC-20 漏跑清单交叉分诊。
- **🌑不可得清点**：①今日 task_runs 台账读数与 catchup 末次打卡（DB 只读面）；②DSC-17 互验 coverage 从 27 项缩到 4 项的意图性（05 簿 P-7，实测不可判）；③DSC-18 schtasks 今日运行态（未复核）。

## §3 挖后自审闸三态裁定

**施工（两项 P0）＋ 挂起排期（两项）＋ 方案封矿（两项）**

- **施工①（P0）**：DSC-15 接线——run_daily_reconciliation 挂入 scheduler 15:40 分派分支（槽 eod_reconciliation 已在 schedule.yaml，属 hollow_slots 两槽之一）。终局量尺：域终点"对账 PASS"是本图宣称的终点语义，今天无人问这一问＝DSC-GAP-TERMINUS 的唯一解锁路径；接线后差异表 append-only 幂等键（run_id/upsert）同批补齐，防重跑双计。接线属反馈环闭环，消灭"回测 vs 柜台对不上要人肉发现"的人工位。
- **施工②**：DSC-19 探测口径扩容——0 字节部件族+装载期错误码纳入扫描（invalidation 条款图内已预告），落地即 GAP-MACRO 事故闭环＋审计件 corrupted_parts_audit.jsonl 首建。终局量尺：部件级损坏"谁先知道"必须无人值守。
- **挂起排期①**：DSC-18 假成功修复——解锁条件=维修窗（第二链日检 4e719ff 系列）收口后复核 :138 缺陷现状，若仍在则小改（空串判失败+exit 1 兑现）。
- **挂起排期②**：DSC-16 回补器 UNTRACKED 件纳管（backfill_tick_depth5.py 实证在盘不在 VCS）——解锁条件=登记+gate+测试三件套补齐，按施工批走 GitCommitGateway 入库。
- **方案封矿①**：DSC-14D auto_backfiller——零生产实例化+零消费（consumers=[]）+wiring_registry 以 pure_library/exempt 合法绕过=内收判据 w5_1"零触发零消费→退役"的教科书例；建议退役评估排季度合并审计窗，不做接线施工（接线=给死件续命，与三活通道功能重叠）。
- **方案封矿②**：检测面 DSC-13/17/20（built 三件）——检测/互验/任务级对账已全自动且 trigger_facts alive（案卷四件节拍闭合），终局无新增位置；detect_only 无自动补跑的 residual 已由施工①/②与 DSC-14 通道承接，不另设环。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：S5 十一节点+edges 反馈环全集（map:2576-3494, 3620-3775） | signal | 三通道口径互斥/第四通道死判/TERMINUS 终点改写条款全录 |
| 2 | 代码轮：integrity 四计数/catchup 分派/探测器审计路径/recon_runner 调用面行号核验 | signal | DSC-15 未接线复核成立（仅 __main__）；DSC-19 审计件应建未建复核成立；catchup lock/槽集在码 |
| 3 | 消费方轮：data/failures 案卷 ls＋known_data_gaps 状态实数＋前端标签 grep＋修复器 VCS 逐件 | signal | 案卷四件节拍闭合；open+monitoring=24 未了账实数；backfill_tick_depth5.py UNTRACKED 坐实；前端 03:30/05:30 漂移自注登记 |
| 4 | 复核轮：auto_backfiller 引用面＋optimize_merge 缺陷现状 | signal/受阻 | auto_backfiller 零生产调用方维持死判（封矿候选）；optimize_merge 现状证据不足标待验证，不断言 |
