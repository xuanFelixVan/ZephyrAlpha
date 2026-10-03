---
ttl: task_bound
title: "全环节骨架总册"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine
---

# 全环节骨架总册（122 环节 / 13 段）

> **一句话**：全项目"环节"只有一套骨架——**122 环节 / 13 段（F01-F122，结构轴）**；交易日时钟轴 44 环节（D13-01..44，四段）是同一批资产的时序投影，去重后**零新增环节**。全项目环节总数=**122**（时钟轴 44=同资产投影，不入总数）。
> **来源五处（全读，内收不发明）**：①docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md（F01-F122 唯一真源）②docs/_working/total_circulation_night/s5_skeleton.md（A5 三态核验簿，2026-09-30）③docs/_working/map_build/fig13_daycycle/00_skeleton.md（44 环节四段时钟轴）④config/trading_day_cycle_map.yaml（机生 48 节点）+trading_decision_map.yaml（TDM 182）+governance_operations_map.yaml（GOMAP 446）⑤调度面 schedule.yaml/tasks.yaml+resource_profile_registry.yaml+schtasks 实测。
> **状态符号**：✅=通（锚点在 HEAD 且有运行/消费实证）｜🔨=断（实件在但链断/停摆，P0-P2 断级）｜⬜=未建（登记态/设计态）。口径=A5 核验簿 2026-09-30。

## 一、环节总数结论

| 轴 | 清单 | 数 | 处置 |
|---|---|---|---|
| 结构轴（唯一环节骨架） | F01-F122 / 13 段 A-M | **122** | 本册主表，逐环节一档 |
| 时钟轴（交易日投影） | D13-01..44 / 四段 | 44 | 全部可挂 F 编号（§四对照），不另立环节 |
| 机生图缺口标记 | D13-G01..G04 | 4 | gap 节点非环节，不计 |
| 决策节点（环节下层判定单元） | TDM 182（E128/P18/X19/F13/C4） | 182 | 非"环节"，挂在 D 段各 F 环节下 |
| 治理模块（实现层） | GOMAP 446 模块 / 7 层（L0 孵化76·L1 监控139·L2 资源66·L3 熔断22·L4 收割42·L5 自愈97·L6 审计4；wired 246+15+91 / suspect_orphan 94） | 446 | 非"环节"，是 F 环节的实现模块 |
| 执行实体（调度面） | schedule.yaml **32 槽**（17 挂载/15 空槽）+tasks.yaml **272 任务**；resource_profile_registry **102 实体**（cron57/manual29/event15/dynamic1，机生 10-02）；schtasks Zephyr\* **65 个**（10-02 实测；10-04 复测 50=Ready39/Running7/Disabled4） | — | 非"环节"，是 F76/F77 的实体清单 |

**三态计数（A5 口径 2026-09-30；10-04 F73 翻账后）**：✅ 通 **97** ｜ 🔨 断 **19**（P0×2、P1×8、P2×9）｜ ⬜ 未建 **6**。

## 二、去重说明（多源命中合并记录）

1. **total_circulation_night/s5_skeleton.md 与 fullflow_mining/00_全环节总册.md**：同一套 F01-F122——前者是后者的三态判定+断链处方层，非第二骨架，合并为一套 F 编号。
2. **fig13 44 环节**：时钟轴投影，44 格逐一挂回 F 编号（例 D13-12/24→F72、D13-28/29→F57、D13-32→F71/F37、D13-21→F38、D13-42→F79/F81），本册不重复立档，只在 §四给对照。
3. **trading_day_cycle_map.yaml 48 节点** = 44 stage（D13 同构机生，wiring：wired 24/partial 14/unwired_no_caller 6/unwired_slot_hollow 4）+4 gap，不是新环节。
4. **调度面数字漂移顺带发现**：fig13 骨架时点（09-24）schedule=29 槽/271 任务 → 10-01 实测 **32 槽/272 任务**（新槽 cross_validation、lane_g_intake_sweep、pf_alloc_rebalance_check，三槽均零任务挂载=编排空槽）；resource_profile_registry 81（09-24）→101→**102 实体**（机生 total_entities=102，10-02：新增 sch_sim_bridge_execute）。时段数字以机生 registry 为准，勿背数。
5. **F70 口径修正**（A5）：模拟撮合与回测引擎是"同源旁路"（simulation 不 import backtest，同读 CH 直供），原 DAG"F65→F70"边作废。

## 三、环节总表（122 行，结构轴唯一账本）

### S01 A 段·数据供给链（F01-F12，✅12）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F01 | 多源采集调度 | ✅ | python -m zephyr.data；resource_profile_registry | 外部数据源 | F04/F06/F10 |
| F02 | 数据源接入生命周期 | ✅ | data_source_onboarding_sop.md | F31 胃情报 | F01（流水线串接仍欠） |
| F03 | Provider 源路由 | ✅ | src/zephyr/data/implementations/ | F02 | F01 |
| F04 | 清洗校验与坏数修复 | ✅ | cross_source_validator.py；d4670f14f9 判净站 13 件 | F01 | F06 备用库 |
| F05 | 判重与审计 | ✅ | check_tick_duplication.py | F01 | F12 |
| F06 | CH 热库落库 | ✅ | ch_config.py；tick 38.9 亿行 | F04 | 全部消费端 |
| F07 | PG 架构库 | ✅ | depgraph PG nodes=13108 | 生成器 | 全部治理端 |
| F08 | 冷库归档 | ✅ | scripts/ch/archiver.py（F 盘运行面未取证） | F06 | 长周期回测 |
| F09 | 备份双链 | ✅ | scripts/backup/backup.ps1；G:/backup | 全库 | 灾备 |
| F10 | 行情订阅分发 | ✅ | scheduler.py；tick 最新 15:42 | F01/券商 | 盘中决策链 |
| F11 | TDM 交叉轴 | ✅ | decision_map.py _XREF_SPECS 13 轴 | 各注册表 | TDM 全图 |
| F12 | 产业链图谱 | ✅ | chain_registry.yaml 873 条 | F05 | F18 车道 D |

### S02 B 段·策略工厂（F13-F29，✅10 🔨7）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F13 | E0 算力闸 | ✅ | MOD-BT-151；grid executor 17:08 | 日历/数据到达 | 全工厂重任务 |
| F14 | E1 进货编排 | ✅ | factory_intake_pipeline.py | F15-F20 | F21 |
| F15 | 车道A 社区 | ✅ | MOD-BT-035；597 条在库 | 社区源 | F14 |
| F16 | 车道B AI 生成 | 🔨P1 | MOD-BT-150 | LLM | F14（无今日产物） |
| F17 | 车道C 公式挖掘 | 🔨P1 | MOD-BT-155+158；sch 停 09-16 | F21 反哺 | F14 |
| F18 | 车道D 产业链三高 | 🔨P1 | MOD-BT-090 | F12 图谱 | F14 |
| F19 | 车道E 模型基线 | 🔨P2 | MOD-BT-084+194+195 | 行情库 | F14/F22 |
| F20 | 车道G 胃进货 | 🔨P1 | lane_g_stomach_intake.py；事件未挂 | F96 胃 | F14 |
| F21 | E2 假说预审 | ✅ | hypothesis_precheck 当日 13:37 | F14/F28/F50 回灌 | F22 |
| F22 | E3 构造翻译 | ✅ | scripts/backtest/translated/ | F21 | F23 |
| F23 | E4 考试咽喉 | ✅ | strategy_screen 当日 14:12 | F22 | F24（全厂唯一判定权） |
| F24 | E5 协同去重 | ✅ | MOD-BT-086 | F23 | F25 |
| F25 | E6 入库监控 | ✅ | MOD-BT-078；runs 台账 | F24 | F26/F14 反馈(FL2) |
| F26 | E7 模拟盘前哨 | ✅ | strategy_production_map:326 module_ref 16/16 已填 | F25 | F27/F72 |
| F27 | E8 组装与资金分配 | 🔨P0 | MOD-PA-002..024；alloc 停 09-28 | F26 | F74/F48 |
| F28 | E9 实盘归因 | 🔨P1 | MOD-PF-007；影子组合缺 | 实盘账本 | F50/F21 回灌(FL1) |
| F29 | 进货台账与出生证 | ✅ | data/strategy_intake/ | F14-F22 | 全工厂 |

### S03 C 段·知识供给线（F30-F36，✅3 🔨3 ⬜1）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F30 | L9 行情基本面源线 | ⬜ | TDM-E-L9-A01..A16（module_ref 多 null） | A 段 | F34 |
| F31 | L9 另类源线 | 🔨P2 | TDM-E-L9-B/C；news 线通 | 外部 | F34/F96 |
| F32 | L9 图谱谱系 | ✅ | PG edges=26580；equity_penetration.py | F12 | F34/F18 |
| F33 | L9 状态快照 | ✅ | regime_state_anchored 当日 09:20 | F38 | F34 |
| F34 | L9 知识汇聚 | ✅ | trading_decision_map.yaml:5131（翻绿） | F30-F33 | F35/D 段 |
| F35 | L9 一问一考 | 🔨P1 | TDM-E-L9-D/E；D2/E2 null | F34 | F23/回灌 |
| F36 | L9 治理横切 | 🔨P2 | TDM-E-L9-Z；metaq reconcile 停 09-26→已复：ZephyrAlpha_MetaqAuditReconcile 每日 03:50 result=0（10-04 实测） | 全 L9 | 治理层 |

### S04 D 段·TDM 消费链（F37-F52，✅14 🔨1 ⬜1）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F37 | L0 盘前作战计划 | ✅ | daily_warroom_pipeline.py 等 4 件 | F33/F50 | F38-F41 |
| F38 | L1 大盘总闸+六传感器 | ✅ | regime_detector/anchored_state_machine（宏观缺件见 S04 断链） | A 段行情 | F39-F41 |
| F39 | L2 板块选择 | ✅ | signal_ashare/sector/ 全族 | F38 | F40/F41 |
| F40 | L3 个股选择 | ✅ | selection_funnel/negative_veto | F39 | F41 |
| F41 | L4 买卖点与执行 | ✅ | ex_core/、ex_sor/ | F40 | F53-F58 |
| F42 | P1 持仓体检 | ✅ | position/core/ 全族 | F57 对账 | F43/F45 |
| F43 | P2 做T加减仓 | ✅ | t_trade_coordinator.py | F42 | F44/F46 |
| F44 | P3 加仓决策 | ✅ | pyramiding_rules.py | F42 | F41 |
| F45 | S1 卖出信号 | ✅ | sell_signal_* 族 | F42/F38 | F46 |
| F46 | S2 离场执行 | ✅ | sell_execution_planner.py | F45 | F53-F57 |
| F47 | R1 应急保命 | ✅ | kill_switch×3+drawdown_state_machine | F59/F60 | 全流横切 |
| F48 | C1 预算切分 | 🔨P0 | multi_strategy_capital_allocator；alloc 停 09-28（与 F27 同根） | F27/F71 | F49 |
| F49 | C2 组合聚合 | ✅ | firm_risk_aggregator.py | F48 | F50 |
| F50 | C3 绩效归因反馈 | ✅ | sim_attribution_daily 当日 13:10 | F49/F28 | F37/F21 回灌 |
| F51 | 币圈骨架 | ⬜ | TDM-C-L1..L4（module_ref 全空） | — | — |
| F52 | 验证方法学+决策算法库 | ✅ | validation_method/decision_algo 两册 | — | F23/F35/F66 |

### S05 E 段·执行基建链（F53-F58，✅5 🔨1）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F53 | 订单生命周期与预检 | ✅ | order_manager.py+ReportGate 注入实证 | F41/F46 | F56/F57 |
| F54 | 打板执行族 | ✅ | daban_* 六件套 | F41 | F53 |
| F55 | SOR 路由 | ✅ | algo_execution_selector.py | F41/F46 | F53 |
| F56 | QMT/miniQMT 桥 | ✅ | 裁定#339：实盘退役、模拟供数继续 | F53 | 券商→F57 |
| F57 | 结算对账与三方核对 | ✅ | post_settlement 当日 00:18 | F56 | F42/F63 |
| F58 | 执行成本反馈 | 🔨P2 | execution_quality_scorer.py（回写无实证） | F57 | F55/F28 |

### S06 F 段·风控合规链（F59-F63，✅5）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F59 | 限额与止损引擎 | ✅ | risk_manager/atr_stop_engine；risk_limit 117 条 | REG-RLM-001 | F47/F41 |
| F60 | 回撤状态机与熔断 | ✅ | drawdown_state_machine 三件 | F63 NAV | F47 |
| F61 | KillSwitch 三实例 | ✅ | 三套 kill_switch（持久化待裁在案） | F47/F59 | 全交易面 |
| F62 | 合规门 ReportGate | ✅ | 已注入 order_manager/qmt_trading_session | REG-CMP-REPORT-001 | F53 拒单 |
| F63 | 仓位对账 | ✅ | position_reconciler.py | F57 | F42/F60 |

### S07 G 段·回测模拟链（F64-F71，✅8）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F64 | 回测三件套 | ✅ | universe/benchmark/cost_model 三册 | REG 三册 | F65/F66 |
| F65 | 回测引擎族 | ✅ | matching_engine/ch_tick_replay | F06/F64 | F66 |
| F66 | 回测预注册七步循环 | ✅ | backtest_backlog 137 对象 | F64 | F25/F67 |
| F67 | 实验登记与档案 | ✅ | experiment_registry 11 条 | F66 | F50 |
| F68 | GPU 矩阵/工厂格子 | ✅ | factory_grid_executor 今日 17:08 | F13 | F66 |
| F69 | T0/成本门/IBT | ✅ | exam_cost_gate.py | F64 | F66 |
| F70 | 模拟撮合与偏差检测 | ✅ | look_ahead_bias_detector 等（同源旁路口径） | F65 同源 CH | F72 |
| F71 | AutoRuntime Core | ✅ | python -m zephyr.trading | 全链 | 全链 |

### S08 H 段·模拟盘→转正链（F72-F75，✅4）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F72 | 模拟盘日跑四件 | ✅ | sch_paper_session 13:15+sim 三表当日写 | F25/F70 | F73/F74 |
| F73 | A/B 联赛分仓 | ✅ | league_judge（msprt+BHY，3992e4b0）；judgment-2026-09/10 两期判分书实跑产出 10-01；残留=eliminate 踢馆首轮月度实跑证据 | F72 | F74 |
| F74 | 转正汇总器 | ✅ | promotion_advisory.py（MOD-BT-199 全量；**全链唯一人工门**） | F72/F73 | Owner 门位→实盘 |
| F75 | 生命周期 FSM | ✅ | lifecycle_fsm/intake/registry_writer | F23-F27 | REG-STR-001 |

### S09 I 段·调度常驻链（F76-F85，✅7 🔨3）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F76 | Windows 计划任务群 | ✅ | schtasks 65 个（10-02 实测）+registry 102 实体 | — | 全链 |
| F77 | 数据调度常驻 | ✅ | scheduler.py；当日灌水 | F76 | F01 |
| F78 | belt daemon | ✅ | commit_belt_daemon（registry:1534） | F76 | 提交链 |
| F79 | reaper 水位监控 | ✅ | process_reaper 23:46 样本 | F76 | 全链安全 |
| F80 | 资源画像与排班 | ✅ | MOD-RESCHED-PROFILE 五模块 | F76 | 全链 |
| F81 | 监控告警 | ✅ | health_monitor+alert_threshold 38 条 | 全链 | 值守 |
| F82 | 订单与结算常驻 | 🔨P0 | order_daemon 全仓无生产 spawn 点 | F57 | F63 |
| F83 | 自动化班底 | ✅ | automation_crew_policy 双引擎两班制 | F76 | 全链 |
| F84 | 反馈循环 FBL | 🔨P1 | feedback_loop/（运行证据弱） | F81 | 治理/演进 |
| F85 | 环境与启动链 | 🔨P1 | windows_service+启动链（运行面未取证） | F76 | 全链 |

### S10 J 段·AI 层链（F86-F96，✅7 🔨2 ⬜2）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F86 | AI 六族管线 | ✅ | ai_layer/ 七目录（L3 接线实证） | F96 | 演进闭环 |
| F87 | AI 红线 | ✅ | ai_layer/redline/ | 治理层 | F86 |
| F88 | LSG 安全网关 | ✅ | llm_security/gateway.py（purity 正门实证） | — | 全部 LLM 面 |
| F89 | 本地模型与嵌入 | ✅ | ollama_serve 23:46+四能力卡 | 模型源 | F86/F16 |
| F90 | Agent 编排 A2A | ✅ | orchestrator/autonomy_core/mcp | F90 | 全链 |
| F91 | 能力反查渐进披露 | ✅ | capability_lookup+44 卡片 | — | 施工前置 |
| F92 | 原问题账本 | 🔨P1 | meta_question 三表 entry_count=0 空转 | F35 | 研究闭环 |
| F93 | PG 图书馆 | ✅ | librarian/lookup；lib_events=293,979 在灌 | F92 | 知识面 |
| F94 | 七段循环设计面 | ⬜ | ai_layer_vision/L1-L7 DESIGN（全 design_done） | — | F86 施工 |
| F95 | OBJ 四对象线 | ⬜ | OBJ_M/T/S/R DESIGN 31 项待裁 | F94 | 施工批次 |
| F96 | 胃·全网搜索消化 | 🔨P1 | automation inbox（升级工单在案） | F31 | F20/F02 |

### S11 K 段·治理门禁链（F97-F110，✅14）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F97 | commit 侧门禁链 | ✅ | git_commit.py:101 gateway；4 天 569 commits | — | 提交链 |
| F98 | GateEngine 运行时门禁 | ✅ | rule_enforcement/ 91 门禁 | 规则 | 全链 |
| F99 | 漂移检测 | ✅ | gov_drift/ 30 检测器+双 watchdog | F98 | 告警 |
| F100 | 红蓝对抗 | ✅ | adversarial_validation/ 53 场景 | — | F98 |
| F101 | 规则与裁定体系 | ✅ | 86 trae_*.yaml+ruling_registry（#456/458/459 当夜落地） | Owner 门 | 全链 |
| F102 | 审计体系 | ✅ | gov_audit/+Merkle 小时链 | 全链 | 报告 |
| F103 | 克隆守卫 | ✅ | clone_guard/ | F98 | 施工 |
| F104 | 会话并发治理 | ✅ | session_concurrency+worktree 四证 | — | 提交链 |
| F105 | 密钥治理 | ✅ | secrets.py 三道 gate | — | 全链 |
| F106 | 术语三层翻译 | ✅ | 三册 7686 条+i18n loader | 模块册 | 生成器 |
| F107 | 回滚恢复 | ✅ | rollback/ 双轨四级 | F84 | 全链 |
| F108 | 人机门位 | ✅ | risk_tier_registry 18 条 | REG-RISK-TIER-001 | 全链门位 |
| F109 | 注册表族治理 | ✅ | ROOR 76 册+净零审计 | 全注册表 | 全链 |
| F110 | 契约冻结与错误码 | ✅ | freeze_manifest 38+error_code 788 | — | 全链 |

### S12 L 段·前端报告链（F111-F115，✅4 🔨1）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F111 | Panel 仪表盘 | ✅ | frontend/dashboard/app_panel.py | F112 | Owner 值守 |
| F112 | API server | ✅ | api_server.py services_registry 读 CH 实证 | 全台账 | F111 |
| F113 | 可视化渲染器 | ✅ | graph_view_renderer 等 5 件 | F112 | F111 |
| F114 | 通知路由 | ✅ | notification_router.py | F81 | F111 |
| F115 | 报告生成 | 🔨P2 | reporting/（运行面未取证） | F102/F50 | Owner |

### S13 M 段·全局横切段（F116-F122，✅4 🔨1 ⬜2）
| # | 环节 | 态 | 来源锚 | 消费←上游 | 产出→下游 |
|---|---|---|---|---|---|
| F116 | SOP 方法论族 | ✅ | sop/ 九族 12 目录 | — | 全链方法论 |
| F117 | 文档资产体系 | ✅ | directory_registry+unified-asset-index 33249 | — | 治理面 |
| F118 | 四盘存储地图 | ✅ | INFRA-STORE-003 storage_map | — | F08/F09 |
| F119 | 双引擎自动化总计划 | ✅ | automation_master_plan L0-L6 | F83 | 排班 |
| F120 | 业务四轴+底板骨架 | ⬜ | 20260917_fullauto_skeleton_v1（设计态） | — | F72-F75/F73 |
| F121 | 研究性三域+研究域 | ⬜ | digital_twin/cross_asset/execution_simulation/research | — | 待裁 |
| F122 | 管线路由 M1-M11 | 🔨P2 | blueprint_routing 30 条+pipeline_orchestrator | — | Agent 编排 |

## 四、四大段（时钟轴）↔ 13 段（结构轴）对照

时钟轴四段：**A 盘前 12（D13-01..12）｜B 盘中 12（D13-13..24）｜C 盘后 11（D13-25..35）｜D 夜窗与贯穿 9（D13-36..44）**，状态 ✅14/🔨27/⬜3（fig13 09-24 口径）。与结构轴是**同资产不同轴**（fig13 §0 判定①窄域+三条硬让渡：时刻值不搬家/决策内容不进图/管线内部不重画）。

| 时钟段 | D13 环节 → 挂靠 F 环节（段） |
|---|---|
| A 盘前 | D13-01/02/03→F77/F81(I)·D13-04/05/06/10/11→F01/F10(A)·D13-07→F56(E)/F81(I)·D13-08→F81(I)·D13-09→F37(D)⬜·D13-12→F72(H) |
| B 盘中 | D13-13/14/15/16/17/18/19→F10/F01(A)·D13-20→F37(D)🔨·D13-21/22/23→F38/F33(D)·D13-24→F72(H) |
| C 盘后 | D13-25/26/30/35→F01/F06(A)·D13-27→F63(F)·D13-28/29→F57(E)·D13-31→F66(G)⬜·D13-32/33/34→F71(G)/F37(D) |
| D 夜窗贯穿 | D13-36/37/39/40/41→F01/F05(A)·D13-38→F81(I)/F05(A)·D13-42→F79/F81(I)·D13-43→F76/F77(I)·D13-44→F37(D)🔨断供 |

时钟轴特有断链（结构轴不照出的洞）：D13-20 竞价命中 10:00-10:30 窗闸在 16:45 自动圈下恒 skipped；D13-44 日界交接 judgment_next_day_forecast 断供；D13-06 suspend 子源 0 行；D13-10/25 板块状态双槽滞后；周批 dow 口径同文件互斥两处。

## 五、断链点总清单（P0→P2，A5 处方+时钟轴补充）

| 级 | 环节 | 断因→最小处方（摘要） |
|---|---|---|
| P0-1 | F82 order_daemon | 全仓无 spawn→pipeline_events 挂 evolution_winner_due 事件消费（禁 cron） |
| P0-2 | F27+F48 E8/C1 | alloc_budget_daily 停 09-28→补日历驱动任务+补跑 09-29/30 |
| P0-3 | F73 A/B 联赛 | ✅已翻账（10-04）：league_judge 3992e4b0 落地+judgment-2026-09/10 判分书实跑产出；残留=eliminate 踢馆首轮月度实跑证据（转月度档观察） |
| P1-4 | F16/F17/F18/F20 车道 | 五车道停摆→逐车道挂回 resource_profile；F20 挂 intel inbox 事件 |
| P1-5 | F92 原问题账本 | entry_count=0→F35 产物接入库闸+恢复 sch_metaq_audit_reconcile |
| P1-6 | F38 宏观传感器 | macro_regime_sensor+macro_indicator_series_map 两实体不在 HEAD→按 token 落地 |
| P1-7 | F35 一问一考 | D2/E2 module_ref null→补验证方案登记+回传接线 |
| P1-8 | F84/F85 FBL+启动链 | 运行证据弱→挂 health_monitor 探针出证 |
| P2-9 | F28/F58/F96/F115/F122/F36/F31/F19 | 运行面弱/低频停→各挂最小观测点 |
| 时钟轴 | D13-20/44、D13-06 suspend、D13-10/25 双槽、D13-41 dow 口径 | 窗闸恒 skipped/断供 2 日/子源 0 行/滞后 1-2 日/同文件互斥两处——归 fig13 作业簿 01-10 |

⬜ 未建 6（F30/F51/F94/F95/F120/F121）=登记态/设计态，挂起不入车道，移交总包裁定。

## 六、复核命令

```bash
python -c "import yaml;d=yaml.safe_load(open('config/trading_decision_map.yaml',encoding='utf-8'));print(len(d['nodes']))"   # 182
python -c "import yaml;d=yaml.safe_load(open('config/trading_day_cycle_map.yaml',encoding='utf-8'));print(d['counts'])"      # 48 nodes/44 stage
python -c "import yaml;d=yaml.safe_load(open('config/resource_profile_registry.yaml',encoding='utf-8'));print(d['total_entities'])"  # 101
python -c "import yaml;print(len(yaml.safe_load(open('src/zephyr/data/config/schedule.yaml',encoding='utf-8'))['schedules']))"       # 32
```
