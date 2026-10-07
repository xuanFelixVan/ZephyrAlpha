---
created: "2026-10-07"
ttl: task_bound
title: "总包夜战 W1·业务块子册：基础设施（26 环节×子模块×上下游×本夜卡）"
session: st-mastertc-mine
---

# 0x_block：基础设施（I 段调度常驻(F76-F85)+J 段其余 AI 基座(F86/F89/F90/F92-F95)+L 段前端报告(F111-F115)+F118/F119/F122/F132）

> 环节行/职责/上下游/模块锚点全部复用 `docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（F01-F122）与 `docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`（F123-F132 定版新增）；状态轴复用 `docs/_working/night_sweep_20260929/00_skeleton_nightsweep.md`。本册只做块视图组装+本夜卡挂接，不重挖、不改真源。

## 一、环节清单（26 环节）

| 环节 | 名称 | 段 | 状态轴 | 基态 | 上游（谁供料）| 下游（谁消费）| 核心模块锚点 | 本夜卡 |
|---|---|---|---|---|---|---|---|---|
| F076 | Windows 计划任务群 | I | 已通 | built | — | 全链 | config/resource_profile_registry.yaml；scripts/register_*.ps1 | C152(L3)、C301(L8) |
| F077 | 数据调度常驻 | I | 已通 | built | F76 | F01 | src/zephyr/data/scheduler.py | — |
| F078 | belt daemon | I | 已通 | built | F76 | 提交链 | src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py | — |
| F079 | reaper 与水位监控 | I | 已通 | built | F76 | 全链安全 | src/zephyr/trading/process_reaper.py | — |
| F080 | 资源画像与排班 | I | 已通 | built | F76 | 全链 | MOD-RESCHED-PROFILE/SAMPLER/GATE/ALERT/VIEW | C102(L10) |
| F081 | 监控告警 | I | 已通 | built | 全链 | 值守 | src/zephyr/trading/health_monitor.py；REG-ATH-001 | — |
| F082 | 订单与结算常驻 | I | 开口 | partial | F57 | F63 | src/zephyr/trading/post_settlement_pipeline.py、night_shift_queue.py | — |
| F083 | 自动化班底 | I | 已通 | built | F76 | 全链 | sop/automation_sop/automation_crew_policy.md；docs/_working/cmd_ledger/automation | — |
| F084 | 反馈循环 FBL | I | 开口 | partial | F81 | 治理/演进 | src/zephyr/feedback_loop/（core.py、evolution_engine.py、error_budget.py 等） | — |
| F085 | 环境与启动链 | I | 等Owner | partial | F76 | 全链 | src/zephyr/trading/windows_service.py；scripts/register_desktop_shell_startup.ps1 | C394(L8) |
| F086 | AI 六族管线 | J | 开口 | partial | F96 | 演进闭环 | src/zephyr/ai_layer/{perceive,intake,cleaning,comparator,scheduling,switch_engin | C136(L8)、C314(L8) |
| F089 | 本地模型与嵌入 | J | 等Owner | built | F89 模型源 | F86/F16 | data/capability_cards/{ollama_chat,embedding_router,local_model_scheduler,rerank | C85(L8)、C183(L9) |
| F090 | Agent 编排与 A2A | J | 已通 | built | F90 | 全链 | src/zephyr/orchestrator/、autonomy_core/、integration/mcp/ | — |
| F092 | 原问题账本 | J | 开口 | partial | F35 | 研究闭环 | src/zephyr/governance/meta_question/（snapshot.py 机生） | — |
| F093 | PG 图书馆 | J | 已通 | built | F92 | 知识面 | src/zephyr/library/librarian.py、lookup.py；library_sop/blood_flesh_cataloging_sop | — |
| F094 | AI 层七段循环设计面 | J | 开口 | design | — | F86 施工 | docs/_working/ai_layer_vision/L1_perceive..L7_heredity/ 各 DESIGN.md | C96(L8) |
| F095 | OBJ 四对象线设计面 | J | 开口 | design | F94 | 施工批次 | docs/_working/ai_layer_vision/OBJ_{M_models,T_tools,S_perimeter,R_rules_standard | — |
| F111 | Panel 仪表盘 | L | 等Owner | built | F112 | Owner 值守 | src/zephyr/frontend/dashboard/app_panel.py | — |
| F112 | API server | L | 已通 | built | 全台账 | F111 | src/zephyr/frontend/dashboard/api_server.py | C10(L11) |
| F113 | 可视化渲染器 | L | 已通 | built | F112 | F111 | src/zephyr/frontend/graph_view_renderer.py 等 5 件 | — |
| F114 | 通知路由 | L | 已通 | built | F81 | F111 | src/zephyr/frontend/notification_router.py | — |
| F115 | 报告生成 | L | 开口 | partial | F102/F50 | Owner | src/zephyr/reporting/（attribution.py、ashare_performance_audit.py 等） | — |
| F118 | 四盘存储地图 | M | 已通 | built | — | F08/F09 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/stora | C28(L9)、C343(L9)、C36(L10)、C37(L10)、C38(L10)、C490(L10)、C410(L10) |
| F119 | 双引擎自动化总计划 | M | 等Owner | built | F83 | 排班 | docs/_working/cmd_ledger/automation_master_plan.md | C341(L4)、C398(L10) |
| F122 | 管线路由 M1-M11 | M | 开口 | partial | — | Agent 编排 | config/blueprint_routing.yaml；src/zephyr/integration/pipeline_orchestrator.py | C192(L4)、C400(L6)、C191(L6) |
| F132 | infra_ops 运维工程域(6 py) | 新环 | 等Owner | new(定版新增) | — | — | 处方卷=13_f132_infra_ops_engineering.md | — |

## 二、块内数据流与上下游（谁喂谁、谁消费谁——真源 DAG 摘录）

### I 段·运行时调度常驻链（F076-F085）

- **F076 Windows 计划任务群**：sch_*/ops_*/数据槽位/drill/event/manual/dynamic=96 实体。上游=—；下游=全链。本夜卡：C152、C301
- **F077 数据调度常驻**：integrator start 常驻+tick 订阅+槽位调度。上游=F76；下游=F01。本夜无卡
- **F078 belt daemon**：提交带 daemon+心跳线程化。上游=F76；下游=提交链。本夜无卡
- **F079 reaper 与水位监控**：进程收割+RAM/commit 水位+keep 白名单。上游=F76；下游=全链安全。本夜无卡
- **F080 资源画像与排班**：96 实体 18 字段+采样器/冲突闸/晨报/周历五模块。上游=F76；下游=全链。本夜卡：C102
- **F081 监控告警**：alert_threshold 38 条+health_monitor+status_dashboard+deadman。上游=全链；下游=值守。本夜无卡
- **F082 订单与结算常驻**：盘后管线/EOD/夜班队列/recon（order_daemon 建成未接线=M5 已记录缺口）。上游=F57；下游=F63。本夜无卡（开口，见总表 §五建议）
- **F083 自动化班底**：双引擎两班制（治理班×业务班）夜班 9 席+晨报插单。上游=F76；下游=全链。本夜无卡
- **F084 反馈循环 FBL**：collectors/detectors/diagnosers/actors+SLO+自动回滚。上游=F81；下游=治理/演进。本夜无卡（开口，见总表 §五建议）
- **F085 环境与启动链**：冷启动三步+windows_service+desktop shell+AI wrapper 注入。上游=F76；下游=全链。本夜卡：C394

### J 段·AI 层链（F086-F095）

- **F086 AI 六族管线**：L1 感知/L2 摄入/L3 清洗/L4 对比/L5 排产/L6 开关/L7 传承代码族。上游=F96；下游=演进闭环。本夜卡：C136、C314
- **F089 本地模型与嵌入**：ollama+嵌入路由+24/7 排程+reranker。上游=F89 模型源；下游=F86/F16。本夜卡：C85、C183
- **F090 Agent 编排与 A2A**：orchestrator+skills 60+/A2A/M1-M11 管线编排。上游=F90；下游=全链。本夜无卡
- **F092 原问题账本**：PG 三表全生命周期：入库闸五要素/一问一考/墓碑不复用。上游=F35；下游=研究闭环。本夜无卡（开口，见总表 §五建议）
- **F093 PG 图书馆**：librarian/lookup/collectors/relations+血肉编目 SOP。上游=F92；下游=知识面。本夜无卡
- **F094 AI 层七段循环设计面**：L1-L7 段卡+主文档 v2.0（三轴一具：引擎×对象×运营）。上游=—；下游=F86 施工。本夜卡：C96
- **F095 OBJ 四对象线设计面**：OBJ_M 模型/OBJ_T 工具/OBJ_S 红线自由域/OBJ_R 尺子升级流水线。上游=F94；下游=施工批次。本夜无卡（开口，见总表 §五建议）

### L 段·前端报告链（F111-F115）

- **F111 Panel 仪表盘**：app_panel 主面板+组件族+服务注册。上游=F112；下游=Owner 值守。本夜无卡
- **F112 API server**：dashboard/api_server+前端 API 代理。上游=全台账；下游=F111。本夜卡：C10
- **F113 可视化渲染器**：图谱/血缘/瀑布/价值流/域映射五视图。上游=F112；下游=F111。本夜无卡
- **F114 通知路由**：告警/事件分发到前端。上游=F81；下游=F111。本夜无卡
- **F115 报告生成**：投资/风险/合规三类报告生成分发。上游=F102/F50；下游=Owner。本夜无卡（开口，见总表 §五建议）

### M 段·全局横切段（F118-F122）

- **F118 四盘存储地图**：D 生产/F 冷储/G 备份/离场 3-2-1 布局真源。上游=—；下游=F08/F09。本夜卡：C28、C343、C36、C37、C38、C490、C410
- **F119 双引擎自动化总计划**：Qoder 白班×GLM 夜班×GPU 专道调度唯一真源 L0-L6。上游=F83；下游=排班。本夜卡：C341、C398
- **F122 管线路由 M1-M11**：blueprint_routing 30 条+pipeline_orchestrator 三层编排。上游=—；下游=Agent 编排。本夜卡：C192、C400、C191

## 三、本夜涉及卡（22 张，去重按主挂接）

| 卡号 | 车道 | 自审闸预判 | 卡面摘要（canonical）| night_sweep 机判交叉 |
|---|---|---|---|---|
| C152 | L3 | **GREEN** | A类① scheduled_task_reconcile.py InvariantCulture 时区修重落 | — |
| C301 | L8 | **WAIT** | R7 一次性计划任务删除清单 | — |
| C102 | L10 | **GREEN** | AI 排产拍板账本落 .runtime/ai_scheduling（TTL 可清区）durability 待裁 | — |
| C394 | L8 | **WAIT** | F85 windows_service.py 退役候选（零运行时消费者+SCM 未装实证） | 85 |
| C136 | L8 | **GREEN** | 波2 B 类技术收敛（B1-B11，含 W-168 点名 B5/B7/B9/B10 四簇）——部分收敛余量未完 | — |
| C314 | L8 | **GREEN** | 波2 落地 169 件+T2 排死袋+T3 终验（st-ailayer-final 成果） | — |
| C85 | L8 | **GREEN** | C6 消费端——八轨数据已落 config/model_routing_policy.yaml task_routes，但 washer.py:164 只读 ai_layer_routes 段且该段在 | — |
| C183 | L9 | **WAIT** | EC3-ollama serve 挂起 | — |
| C96 | L8 | **GREEN** | AI 层两层 HANDOFF 真源未入库——12 项批准凭据原文 HANDOFF_st_ailayer_final.md 全树 0 命中+HANDOFF_st_ailayer_sx_20260927. | — |
| C10 | L11 | **GREEN** | N2 api_server budget/schedulegate 路由注册移到守卫前（心跳清障件已落；路由段仍在 __main__ 守卫后，直跑模式永不注册） | — |
| C28 | L9 | **GREEN** | 镜像树 ~3309 件迁移——已裁定不整体迁移，先写者改造 W0 未做 | — |
| C343 | L9 | **GREEN** | 存储裁定"不搬PG"连同翻案条件写死在册 | — |
| C36 | L10 | **WAIT** | VM /root 两件施工残留处置（核验：timeout 25 python scripts/backup/ch_vm_ssh.py --cmd 'ls -d /root/macro_data_bro | — |
| C37 | L10 | **WAIT** | 两个 tmp 工具目录处置（.runtime/tmp/st-metaq-gc-20260924 与 st-pqmine-20260927；配方已沉淀可删，keep.txt 白名单行随删） | — |
| C38 | L10 | **GREEN** | D 盘容量长期策略（93%→审计时仍紧张；换小虚拟盘/加物理盘/车道清理三选一） | — |
| C490 | L10 | **GREEN** | 终局 Owner 菜单④件（FMS-HYGIENE 翻硬拦/8 候选净删/镜像树迁移/165GiB 归档豁免） | — |
| C410 | L10 | **WAIT** | 夜裁#6 清盘真删授权（乙方案：标记+隔离已做，真删列清单待勾选） | — |
| C341 | L4 | **GREEN** | 105项"编目有、排产无"补进波次（自称90进波次包/CITED=143缺口0） | — |
| C398 | L10 | **GREEN** | F119 双引擎真源二选一（10-08 继任窗） | 119 |
| C192 | L4 | **GREEN** | P3 九环节 57 条缺口 vs fullflow_mining 76 环节对账表 | 1、122 |
| C400 | L6 | **GREEN** | 未见销账的接线普查宽口径短板（自动化触发 34-94 环节未覆盖/工单面 39/132） | 123、132 |
| C191 | L6 | **GREEN** | P2 缺口立卡转施工（L02 G系/L03 b系/L06 卡族） | — |

## 四、处方指针（复用既有工单，不新开处方）

- 挖矿处方卷=docs/_working/fullconnect_campaign/ 各域 per-F 卷（总表夜战骨架处方指针列）；施工序列=docs/_working/fullconnect_campaign/00_workorders.md（S1-S5+§四下一战役）；分诊六态=docs/_working/final_delivery_campaign/workorders_{governance,commit_clean,data_exam_factory,docs_misc}.md。
- 本块开口环节中已有工单无卡者（如 F115'R1-R3 最薄一刀'）按总表 §五建议补卡挂接，工单不重写。
- Owner 门位卡（等Owner 状态轴/§五 保留）本夜只登记不施工；清单见总表 §四 WAIT 行。

## 五、复核命令

```bash
# 本块环节数与总表 §三 行一致；卡数与总表 §四 该块行数一致（主挂接口径）
grep -c '^| F' docs/_working/master_tc_night/01_skeleton/06_block_infrastructure.md
```
