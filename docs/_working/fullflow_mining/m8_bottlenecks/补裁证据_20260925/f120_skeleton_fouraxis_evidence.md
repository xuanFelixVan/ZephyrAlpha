---
ttl: task_bound
session: st-ailayer-fullflow-frxc
date: 2026-09-25
---

# M8 补裁证据 · F120 业务层四轴+底板骨架（design 态裁前证据，只列证据与选项，不裁）

> 挖矿会话 st-ailayer-fullflow-frxc ｜ 2026-09-25 ｜ 只读挖矿+本目录零 commit。
> 待裁命题：F120＝"决策权/时间节拍/产线工段 8+1/生命周期"四轴+治理底板（标准库+红线库）骨架，总册标 design、工单队列 P0-P2 在案——本册回答：**该设计册的工单到底被谁消化了、还剩什么、框架本体收编还是结案**。
> 真源：docs/_working/automation/20260917_fullauto_skeleton_v1.md（125 行，v1.1）+ 20260917_decision_skeleton_mining_report_v1.md（41 行）+ docs/_working/automation/campaign/CAMPAIGN_LEDGER.md。

## 一、骨架声明面（design 本体）
- §6 骨架封顶声明：四轴（①决策权 L1-L5"另一 AI"②时间节拍 T1-T4"另一 AI"③产线工段 8+1④生命周期）+治理底板（§8 标准库+§9 红线库）；"不会再有第五条轴；再往下拆全是血肉"。
- §4 工单队列：P0×2（③数据源上架流水线/⑧转正建议书汇总器）｜P1×7（搜索设备 v0/⑥号车道/⑨骨架体检/A-B 联赛编排/标准库/实盘红线执行器）｜P2×2（④AI 判净站/WeeklyRest）｜已立 GPU-01~04。
- frontmatter completes_when："8+1 工段缺口全部立卡施工完毕且 Owner 驳回本骨架，或被 v2 替代"。
- 决策骨架报告三拍板项：①骨锁肉动裁定认可②每周休息窗认可③搜索设备 v0 开工确认——**ruling_registry grep 零命中**（仅 :5187 一处 WeeklyRest 时序提及），三拍板项无正式裁定记录。

## 二、证据 A 方——"工单已被施工批消化，可收编结案"
| 工单 | 落地证据（git ls-files/盘面实测） |
|---|---|
| P0 ③上架流水线 | scripts/data/onboard_source.py（+blueprint 卡）；CAMPAIGN_LEDGER §1.5"六件在 71257b59b2 一批落地" |
| P0 ⑧转正汇总器 | src/zephyr/strategy_pipeline/promotion_advisory.py（40ca90eb88；M6 02 册 :4329 已投影；台账自证"勿重建"，真缺口=组合门打分器+一页报告） |
| P1 搜索设备 v0 | scripts/automation/intel_harvester.py；docs/_working/automation/inbox/（intel-20260916.md 在盘） |
| P1 ⑨骨架体检 | scripts/governance/generators/generate_skeleton_health.py+tests/governance/test_generate_skeleton_health.py |
| P1 §8 标准库 | scripts/governance/standards/standards_lib.py（消费方=scripts/backtest/league_registry.py+2 校验器）；考纲预注册纪律=built（M2 F66 backtest_backlog+config/exam_scale_cost_gate.yaml 预注册冻结，m2 05 册 5.3 绿） |
| P1 §9 红线执行器 | src/zephyr/ex_sor/risk_redline.py（71257b59b2 批） |
| P2 WeeklyRest | scripts/ops/weekly_rest_guard.ps1+registry ops_weekly_rest 条目——notes_zh"实测周日 05:00 关机；Owner 2026-09-17 全批点头"（拍板项②已事实批准） |
| §11 nightly_sentiment 双真源 | 已落地：ZephyrAlpha_NightlySentiment 计划任务 **Disabled**（m5 01 册 :61"已由 schedule.yaml nightly_sentiment 槽替代"），08:20 槽位在跑（m5 02 册 :46） |
| GPU-01~04 | M2 车道收编（GPU T1 在跑禁中动） |
| ⑥号车道/胃 | scripts/backtest/lane_g_stomach_intake.py 在盘（12KB，09-17） |

## 三、证据 B 方——"design 未结，框架与残项仍在"
1. **risk_redline.py 零消费**：全仓 grep 无生产消费方——与 M7"合规门全家族码成闸空零注入"同款（码成、闸空）；§9 红线分级表 v0/黑天鹅缓冲仲裁/赚太多三查无代码件（m7 各册 grep "SR 11-7/黑天鹅/赚太多"零命中）。
2. **generate_skeleton_health / intel_harvester 未入 resource_profile_registry**（grep 零命中）——无常驻/计划任务触发，"自动触发"四要素缺一=登记态运行。
3. **m1-m8 与骨架从未对账**：M0 总册 F120 行标"design（工单队列 P0-P2 在案）"，但其工单落点全在 automation campaign（早于挖矿波 8 天），M1-M8 各册独立重挖了同批缺口（F02 上架流水线=M1、F74 汇总器=PR 待派、F96 胃、F20 事件接线）——两本台账互不引用，"工单已被消化"的知识只存在于 CAMPAIGN_LEDGER。
4. **框架归属悬空**：四轴声明与 S0 总册 13 段 122 环节的映射关系未登记（决策权轴→F38-F41/TD 组、节拍轴→同、工段轴→F01-F29/F72-F75、生命周期轴→F75 lifecycle_fsm partial、底板→F66+F59/F60+F101）——任何一轴出问题无人回改骨架册。
5. **completes_when 未达**：缺口未全部立卡施工完毕（risk_redline 接线/打分器/体检常态化缺），也未被 v2 替代、未被 Owner 驳回——按其自声明仍=在册 active design。
6. **口径漂移 2 处**：休息窗 04:00（骨架 §3）vs 05:00（registry notes+pool_vocabulary 注释）；registry ops_weekly_rest status=**planned** vs notes"实测已关机"（登记口径与运行事实矛盾）。

## 四、裁定选项（并排陈列，本组不裁）
- **选项 A·收编结案**：认定工单已由 campaign 施工批+M2（考纲）消化，骨架册转 archived/已吸收，四轴映射表一次性写入总册 F120 行；残项（risk_redline 接线、打分器）移交 M7/PR 车道工单，不再以"骨架"名义挂账。代价：loses 封顶声明的框架约束力。
- **选项 B·升格框架真源**：F120 四轴+底板立为总册 M 段的组织框架（13 段↔四轴对账表登记入册），骨架册保持 active 至 completes_when 达成；先补 §三.6 两处口径漂移。代价：与总册/分工册三本册并行维护，漂移面扩大。
- **选项 C·部分收编+残项清单（折中）**：工单队列逐行销账（§二表为准）回写骨架册 §4 状态列；框架降级为"历史设计出处"引用（同 20260913-strategy-factory-pipeline-discussion 模式）；三拍板项转 Owner 晨报正式裁定化（骨锁肉动/休息窗已事实批准→补登记、搜索设备 v0 确认）。代价：需一次骨架册编辑（热文件 CAS）。

## 五、复核命令（10 分钟）
```bash
# 1. 六件交付在库复现（各应≥1 命中）
git ls-files | grep -E "onboard_source|intel_harvester|generate_skeleton_health|standards_lib|risk_redline" | head -8
# 2. risk_redline 零消费复现（应无输出）
grep -rln "risk_redline\|RiskRedline" src scripts --include="*.py" | grep -v "ex_sor/risk_redline"
# 3. 体检/采集件未入排班复现（应无输出）
grep -n "skeleton_health\|intel_harvester" config/resource_profile_registry.yaml
# 4. nightly_sentiment 22:30 已退役复现（应 Disabled+替代说明）
sed -n '61p' docs/_working/fullflow_mining/m5_scheduling/01_windows_schedtasks.md
# 5. 三拍板项无裁定复现（应仅 1 行时序提及）
grep -c "骨锁肉动\|骨锁肉动裁定" docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
# 6. WeeklyRest 口径双值复现
grep -n "05:00\|04:00" docs/_working/automation/20260917_fullauto_skeleton_v1.md | head -2
grep -n "weekly_rest 周日 05:00" config/resource_profile_registry.yaml | head -1
```
