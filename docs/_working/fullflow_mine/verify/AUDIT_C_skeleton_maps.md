---
ttl: task_bound
title: "骨架断链11项对照八图复审"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# 骨架断链 11 项对照八图复审（AUDIT-C，只读勘察）

> **一句话**：11 项中 **2 项已被施工覆盖翻账**（5-1 F73 判分件 st-c9-final 已投产、5-11 图队已登记待骨架回写）、**9 项仍需**且全部落在管线修复面；与图队（mapreg/gomap-chief/tdm-mount-flash/vm12e/vm12surg/fig13-chief/bm-reclass/map9 族）**零施工重叠**——他们做登记/血肉面，我修管线面，唯一需协调点是 5-4 D2/E2 补挂与 tdm-mount 车道同文件域。
> 实测时点：2026-10-04（盘面=dev HEAD 6eb3ab181b + 工作树）。

## 一、八图在建状态快照（10-03/10-04 落笔，git log 实证）

| 图 | 状态 | 图队近期动作 | 与本 11 项关系 |
|---|---|---|---|
| TDM（182 台） | 在册 | tdm-mount-flash：任务A 23域蓝图 frontmatter module_id 补齐 144（700ec0f387）+coverage ledger 生成器（b155bf2971/a2150befd9）；未触节点 module_ref | 5-4 零重叠；F38 实体未入 HEAD 前无从挂载 |
| 图9 策略工厂（339 节点） | 在册 | map9-chief 图例 12 条冻结+校验器 schema0.3（111f20c026/62b59093d0）；map9-f1 449 行挂载候选；map9-f3 330 台 facts 收官；vm12e 域主体统一（a80cce5da8） | 车道节点 FAC-E1B/C/D/E/G 结构全在、trigger_facts 全未挂（tf=False，F2 批已解锁未施工）→ 5-2 复活后车况归其 F2 批登记 |
| GOMAP 图10（446 模块） | 在册 | gomap-chief F1 四表重投（db2f9bd03b）：gap_matrix 7 环节全缺/orphan_ledger 94 台/facts 14 源/casebooks | 与 5-5/5-9 互为证据源，非施工冲突 |
| battle_map | **改横向**（裁定#483，99141078f4） | bm-reclass：纵改横·覆盖切片，环节表维持 08-12 冻结 | 与 11 项无涉；"八张纵图"实为 7 纵+1 横 |
| 图11 交付流水线 | 待转正 | mapreg 任务2 确认"11 张在册+2 张待转正（图11/图13）"（9da8856dba） | 无直接交集 |
| 图12 数据供给链 | **已转正在册**（schema 0.3，vm12surg 870ea6a543/62b59093d0/6e57b1f21c） | 挂图 SOP 升级+F1 四表（docs/_working/vmap12_flesh/）；A 段供给链+调度槽词汇表含 lane_g_intake_sweep/cross_validation/pf_alloc_rebalance_check 三空槽词 | **F16-20 车道不在图12**（主体在图9，仅 :651 指针 FAC-E1）→ 不构成对 5-2 的覆盖，5-2 不让位 |
| 图13 交易日循环（48 节点 64 边） | 待转正 | fig13-chief 挂血肉供料（6dd1028464）+总筹五裁；裁定#482 与排班总览独立互挂（e79d7189dd）；10-04 幂等重生（2ca2d2d5ed） | D13-20/44 诊断注记已在图；D13-39/07 归生成器手术批；**骨架回写清单三件已登记**（102 实体等） |
| 横切 | mapreg 任务2/3/5：alignment §3 轴标注+e36d 残留核查+九图 L0 缺口清单 | 只读普查类 | 无冲突 |

## 二、11 项逐项判定（实测证据）

| # | 项 | 实测（10-04） | 判定 | 施工方式/责任面 |
|---|---|---|---|---|
| 5-1 | F73 联赛判分/踢馆件 | league_judge.py+4 配套在 HEAD（st-c9-final 3992e4b024，09-30 07:28）；pipeline_events.py:477/875 league_judge_due 月度档接线；**judgment-2026-09/10 两期判分书已产出**（data/backtest_artifacts/league/judgments/，10-01 07:24） | **判分已完✅（st-c9-f73→st-c9-final）** | 残留：eliminate 踢馆动作与喂 F74 的首轮月度实跑证据；骨架 F73 行🔨P0 已过时→随 5-11 回写批翻账 |
| 5-2 | 五进货车道复活 | lane_b/lane_c/three_high(D) candidates 10-01 05:34 一次性批量；FactoryLaneC schtask 已启用（周中 20:00），上次运行 10-02 20:00 **退出码 3=失败**；lane_g_seen_urls 停 09-23（11 天）；lane_e 无产品文件 | 仍需 | 改调度为主（我）：lane_c 查退出码 3 病因；F20 绑 lane_g_intake_sweep 槽任务（=5-10 同根同修）；F19/E 挂最小批次。车况登记让图9 F2 批 |
| 5-3 | F38 宏观两实体入 HEAD+摘 noqa | macro_regime_sensor.py=**untracked**（git status ??，全分支零历史）；macro_indicator_series_map.yaml 不在 HEAD（盘面件+campaign_trash 抢救件在）→ **w3h 未 merge，前提不满足** | 仍需（前置缺失） | 改码（我）：两实体按 token 落地 commit；llm_premarket_analysis.py:584 noqa **必须保留**至 merge 后。TDM/图12 均未挂此二实体，无冲突；merge 本身非任何在途车道职责 |
| 5-4 | F35 module_ref 补挂 | TDM E-L9：**D2/E2 仍双 null**（182 台实测）；A01..A16 16 null（F30 另案）。tdm-mount 只补了蓝图 frontmatter module_id，未触 TDM 节点 | 仍需 | 架构数据走 DB 正门（TDM 机生，commit 700ec0f387 实证 regenerator 会回写 YAML，禁手改）；同文件域与 tdm-mount 车道需错峰（见 §四） |
| 5-5 | F84/F85 运行证据 | feedback_audit_trail 目录空；ZephyrAlpha 交易服务未安装（sc 1060） | 仍需 | 改码/改调度（我）：挂 health_monitor 探针出证；GOMAP orphan_ledger 可作旁证 |
| 5-6 | D13-20 竞价窗闸错位 | fig13 节点注记已载"只被 16:45 圈调用→自动圈下恒在窗外=结构性失效"+fig13-chief 旁证（AUCTION_WINDOW 全仓单引用）；锚 daily_loop_master_switch.py:294 | 仍需 | 改码（我）：dloop 圈窗参数；图面诊断 fig13 已完成，图侧不再动 |
| 5-7 | D13-44 日界交接断供 | fig13 节点注记已载"三班制交接件面向连续市场不覆盖 A 股日界"；盘面未寻得 09-28 后 forecast 产物（断供延续旁证） | 仍需 | 改码（我）：next_day_forecaster/dloop 日界交接适配；登记面已由 fig13 完成 |
| 5-8 | 未建 6（F30/F51/F94/F95/F120/F121） | TDM-C-L1..L4 module_ref 全 null、L9-A 16 null 实测；F94/F95 DESIGN、F120/F121 设计态均未变 | 维持⬜ | 挂起不入车道，移交总包裁定（骨架原判维持）；gomap 表1 gap_matrix 属模块轴可作旁证 |
| 5-9 | P2 弱运行 7 件 | F36 **已改善**：MetaqAuditReconcile 每日 03:50 运行、10-04 result=0、metaq registers 10-03 活跃；F115 morning_digest 10-01 在产；F31 news 线活（news_slow 2 任务+event_driven 11 任务绑定）；F28/F58/F96/F122 仍弱（F58 无回写件、F96 inbox 未复活） | 1 项改善，4 项仍需 | 改调度（我）：F28/F58/F96/F122 各挂最小观测点；F36 残留=三表 entry_count 回填核验 |
| 5-10 | 三个空调度槽 | cross_validation/lane_g_intake_sweep/pf_alloc_rebalance_check：schedule+registry（data_slot_*）均在册、tasks.yaml **零绑定**（32 槽 17 挂载/15 空维持骨架口径）；新发现=registry dow 2-6 vs schedule 1-5 分歧 | 仍需 | 改编排（我）：逐槽绑任务（lane_g 槽即 5-2/F20 通道）；dow 真源分歧 fig13-chief 已登记→归排班班 |
| 5-11 | resource_profile 81→101 漂移 | registry 本体健康：total_entities=**102**=actual（机生 10-02 11:24Z，cron57/manual29/event15/dynamic1，新增 sch_sim_bridge_execute）；漂移在骨架散文（写死 101/56cron）+schtasks 49→实测 **65** | 登记已完（fig13-chief 总筹 c 条"骨架回写清单三件"），**回写仍需** | 改册（我）：00_skeleton.md §一/§二.4 回写 102/57cron/65 任务+5-1 翻账；全 102 台 module_id/map_node_id 双 null 是排班族挂图面（非本批） |

## 三、汇总

- **已完/被覆盖（2）**：5-1 判分件（st-c9-final，判分书 09/10 两期在产，踢馆实跑证据待月度首轮）；5-11 登记面（fig13-chief，回写动作仍归骨架方）。
- **仍需（9）**：5-2 五车道（改调度）、5-3 两实体入 HEAD（改码，前置 w3h merge 缺）、5-4 D2/E2 补挂（DB 正门）、5-5 F84/F85 探针（改码/调度）、5-6 D13-20 圈窗（改码）、5-7 D13-44 日界交接（改码）、5-9 中 F28/F58/F96/F122 四件观测点（改调度）、5-10 三槽绑任务（改编排）、5-11 骨架册回写（改册）。
- **维持不动（1 类）**：5-8 未建 6 环节=移交总包裁定，不入车道。

## 四、横纵对齐裁定（每项施工落点责任唯一）

1. **管线面（唯一=骨架方/本侧）**：一切"让链路重新产数"的修复——5-2/5-3/5-4/5-5/5-6/5-7/5-9(4 件)/5-10。图队对所有这些项只做登记/诊断已到位（fig13 注记、map9 facts、GOMAP orphan_ledger），不修管线，无双写风险。
2. **图登记面（唯一=各图车道）**：车况血肉→图9 F2 批；D13 时钟轴诊断与注记→fig13；挂载状态三分类→tdm-mount coverage ledger；模块孤儿→GOMAP F1；battle_map 已改横退出纵图序列。复活/修复落地后由对应车道**事后**登记，时序单向不冲突。
3. **骨架册回写（唯一=骨架方）**：5-11 数字漂移+F73 翻账+F36 改善+schtasks 65，随下一骨架批一次落（fig13-chief 回写清单三件已点名）。
4. **唯一协调点=5-4**：tdm-mount 车道若后续批扩展到"节点 module_ref 补挂"，D2/E2 应让位随其 coverage ledger 的 unmounted_orphan 分类顺路带（同文件域）；若仍归骨架方，必须走 DB 正门并与其车道错峰（regenerator 会回写 YAML，并发写有前科）。
5. **外部前置**：5-3 的 w3h merge 非任何在途车道职责，须 w3h 会话收尾或总包直派；merge 前 noqa 保留，勿提前摘除。

> 复核命令同 00_skeleton.md §六；本报告只读勘察产出，唯一写入=本文件（CREATE-GUARD token 未登记，受"只写一个报告文件"任务约束，移交总包补登）。
