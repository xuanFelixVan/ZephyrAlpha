---
ttl: task_bound
completes_when: 裁定建议并入转正批收尾报告后归档
title: W4-4 排班总排班视图 vs 图13 重叠判定（任务4）
owner: st-mapreg-20261003
---

# 图13 重叠判定报告（只读挖矿，零写入 except 本报告）

> 对象：W4-4「排班三表一入口」资源总视图（commit `1aa88be859`，2026-09-20，st-final3-20260919）。
> 比对基准：`config/trading_day_cycle_map.yaml`（HEAD 与工作树均实测 **48 节点**=44 业务 D13-01..44 + 4 缺口 D13-G01..04；总包令所记 53 未在盘面复现，如实记录）。

## 对象解剖（1aa88be859 产出物）

| 产出物 | 形态 | 内容 |
|---|---|---|
| `scripts/ops/schedule_overview.py`（528 行） | 读侧统一 CLI | ①周历视图=槽位×任务映射（三表 join 键=槽位名）②资源档位总览（泳道/workers/天花板/互斥组/实测覆盖率）③三表一致性检查（幽灵池/真源指针/findings 直通） |
| `src/zephyr/governance/audit/schedule_consistency_reconciler.py`（521 行） | 执法件 | check_tables 纯函数 + post-commit 事件触发 ReconcilerSpec 工厂 = **GATE-SCHEDULE-CONSISTENCY（priority=826）** |
| 配套 | 册/测 | blueprint 1 件 + 单测 11 例 + reconciliation_registry merge_external_specs 入口 |

三表= `config/resource_profile_registry.yaml` + `src/zephyr/data/config/tasks.yaml`（271 任务）+ `src/zephyr/data/config/schedule.yaml`（32 槽）。物理表不合并=Owner 裁定原文。

## 定量比对

**数据面（槽×任务）——高交集**：
- 图13 节点 `slot_refs` 挂载 **29/32 唯一槽（90.6%）**；未挂仅 lane_g_intake_sweep / cross_validation / pf_alloc_rebalance_check 三槽（+disabled 非真槽）。
- 271 任务中 **267（98.5%）** 落在被图13 挂载的槽内（仅 disabled 4 任务在外）；图13 另有 14 条 task 级 gap_refs 点名到具体任务。

**功能面（视图三块）——低交集**：
- 周历视图的数据面与图13 高重叠（即上述 29/32）；
- **资源档位总览：与图13 零交集**——图13 生成器 `generate_trading_day_cycle_map.py:187` 自带边界声明：「**不画资源争抢与内存天花板——归排班三表（resource_profile_registry + schedule_overview + …）**」；
- **三表一致性检查 + reconciler + gate 826：与图13 零交集**——post-commit 执法件，图13 无对应物也不应有。

**同源关系（关键定性）**：图13 机生层**直接消费三表**（generate_trading_day_cycle_map.py:133-139 声明 _SCHEDULE_REL/_TASKS_REL/_REGISTRY_REL 三真源；节点 machine_facts.slot_facts 即其投影）。即图13 是三表的「交易日循环投影」，排班视图是三表的「运维资源投影」——数据面高重叠是**同源共相**，不是重复建设。

## 裁定建议（一行）

**维持独立（排期族资源视图）**——数据面 90.6%/98.5% 高交集属三表同源双投影非工件重复，功能面（资源档位+一致性 reconciler+gate826）与图13 零交集且被图13 生成器 ：187 边界声明显式划归排班族；并入图13 会让图吸收自身数据源的读侧入口（循环依赖），建议关系=互挂引用不迁移（图13 节点 slot_refs 已回挂槽位，反向可在图13 doc_refs 增 schedule_overview 入口指针，随转正批可选）。
