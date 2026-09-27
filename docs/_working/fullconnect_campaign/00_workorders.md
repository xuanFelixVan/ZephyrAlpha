---
ttl: task_bound
title: "工单总表（挖矿缺口→施工序列）"
session: zc-chief-20260927
---

# 工单总表（00_workorders）

> 全部 122 环节（+10 新环 F123-F132）挖干封矿后，各矿道 P0/P1 缺口的施工序列。
> 三态：已落地 / 在飞待落 / 施工序列（本战役内做）与 Owner 门位（登记 99 台账）。

## 一、已落地（GitCommitGateway 实证哈希）

| 线 | 交付 | 哈希 |
|---|---|---|
| G | 撞号验证轨+registrar fail-closed 回归测试 | 26d1dfb752 |
| L | potential_consumers SQL 根修+shrink guard+68 重放+测试 | 973b03c3a4 + 64c0a09865 |
| P1 | str⧸date 共因 norm_boundary_date 覆三实例 | baee3850fd |
| P2 | l2_tick 真配置护栏测试（271 任务零 ERROR 判据） | fb9011eee5 |
| P3 | etf_benchmark date_col 声明修复 | b9c2a69005 |
| P4 | restricted_shares 前瞻值新鲜度上界 | 2d66c49156 |
| P5 | 反爬诊断台账+ALGO_FLOW 出仓 | cf9fa76e46 / dd49e5dba4 |

## 二、在飞待落（他会话施工完待落地/待首跑）

1. **Q 袋**（入队预检封旁路 3 文件 +455 行，91/91/29/29/70/70 绿）：被 FOLDER-CAPACITY-HARD-LIMIT 硬拦（scripts/ 150>120，他会话在飞件累积）。处方=待容量回落后 re-claim+重投（lane_q_notes.md）。
2. **F26 E7 前哨**：paper_outpost.py 396 行（MOD-BT-225）+18 测试绿+FAC-E7 diff（他会在飞 untracked）。四缺=提交/注册表登记/事件接线/首跑——归属其作者会话，总筹只登记催办。
3. **F34 L9 聚合器五件套**：st-chief4x-know 已落地（660L+DDL 部署器+schema+test+pipeline_events 挂接+TDM 回填）。收尾三步（DDL --apply/首跑/pf_alloc 消费）涉生产 DDL→Owner 门（99 #21）。

## 三、施工序列（本战役执行）

| 序 | 包 | 项 | 判定来源 |
|---|---|---|---|
| S1 | T 交易接线 | F39 L2 门接线（水位桥已批+batch2 五行）/ F40 候选池持久化 M-41+LK-04 通电（现成工单 L04-C01/C02）/ F41 L4-14 反馈环最后一米+九态映射桥 | e_decision_chain 03/04/05 卷 |
| S2 | K 风控熔断 | F60 liquidation_guard 编排接线 / F61 kill_switch rebuild 失忆窗接入+拒单演练 / PostSettlement 注册脚本 bc76efe3bf 坏形态修复（只修脚本不重注册） | g_backtest_gpu 03/04 卷 + h_sched_recovery F76/F82 卷 |
| S3 | V 治理红证 | F98 三账对账闭环（generate_gate_registry.py 扩三口径 diff，净零=替代人工周审计）/ F101 RULING-REFERENCE 红证 / F05 check_tick_duplication 配对红样 | j_ai_design_gates 05/08 卷 + a_data_foundation 05 卷 |
| S4 | F 工厂修复 | F21 E2 deferred SQL_ALREADY DISTINCT / F22 llm_error 幂等占坑排除 / F16 进货台账 11 行重建+对账校验器 | b_factory_inbound 09/10/04 卷 |
| S5 | Q 落地重试 | scripts/ 容量回落即 re-claim 重投（红蓝前置） | lane_q_notes.md |

## 四、下一战役序列（本战役不做，工单已挖干）

F42 体检编排（先考古）/ F43 做T统一调度 / F45 S1 扫描编排+X 流消融实弹 / F46-F47 离场执行编排 / F56 bridge-execute 断腿（M7 立案，最高优先）/ F53 Saga 编排+九态桥 / F02 上架编排器 onboarding_wizard / F04 清洗四引擎接线（Owner 晨报名单）/ F115 R1-R3 最薄一刀 / F74 触达铃铛 / F73 首位参赛者+league_judge / F75 词表对齐 / F92 ROOR 册页回填机制 / F30 登记一行案 / F05-F06 空壳表登记前置。

## 五、Owner 门位增量（已同步 99 台账）

F34 DDL --apply+首跑（#21）/ F88 usercustomize 运行时网（#22，本战役只做仓内安全子集=no usercustomize）/ F76 schtasks 写操作与 N/A 清理（#23）/ F68 T1 判卷三阻断（#24）/ F51 币圈空壳去留（#25）/ F111 宪法入口三方冲突（#26）/ F119 双引擎真源 10-08 继任（#27）/ F120/F121/F122 收编与边界三裁（#28）。
