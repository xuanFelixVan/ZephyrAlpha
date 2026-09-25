---
ttl: task_bound
completes_when: M0 骨架总册被总筹验收并入晨报后，随战役归档
---

# 全流通挖矿战役 · M0 骨架总册（00_skeleton_fullflow）

> 立册 2026-09-25 ｜ 车道 M0 ｜ 会话 st-commitspeed-tbl-20260924 ｜ 回答一个问题：**整个项目端到端到底有多少个环节**。
> 方法=七源交叉验证（禁凭记忆）：ROOR 76 册｜SOP README 12 族｜功能域册物理 94 条｜模块册物理 7776 条域分布｜能力卡片 44 张｜AGENTS §7 九系统｜自动化总计划册 L0-L6；辅证=资源画像册 96 实体（config/resource_profile_registry.yaml）、四盘存储地图 INFRA-STORE-003、链注册表 873 条、管线路由册 30 条、src/scripts 代码锚点。
> 环节编号三段式：段字母+序号（D 数据链/T 交易决策与执行/B 回测模拟/A AI 层/G 治理门禁/S 调度常驻/F 前端/X 全局横切）。

## 一、端到端环节总清单（76 环节）

### A. 数据链段（D1-D12，主归 M1）
| # | 环节 | 一句话 | 主入口 | 归属 |
|---|---|---|---|---|
| D1 | 多源采集调度 | 数据集成器 8 子命令+30 个数据槽位(data_slot_*)按交易日历灌水 | `python -m zephyr.data`（status/run/pause/resume/start/speed-test）；槽位清单=config/resource_profile_registry.yaml | M1 |
| D2 | 数据源接入生命周期 | 全网挖矿→报批→建表→接入→调度→验收三查→路由→退役 | sop/data_ops_sop/data_source_onboarding_sop | M1 |
| D3 | Provider 实现与源路由 | miniQMT/QMT桥/AKShare/Tushare/Baostock/CLS/东财/TDX/TickFlow/RSS 十源策略路由 | src/zephyr/data/implementations/miniqmt_provider.py、qmt_bridge_provider.py；SourcePolicy/PolicyRegistry | M1 |
| D4 | 清洗校验与坏数修复 | 跨源校验/回补检查/错误分类/tick 深度落盘；AI 清洗 L3 | src/zephyr/data/cross_source_validator.py、backfill_checker.py；data_ops_policy 三步验证 | M1 |
| D5 | 判重与数据审计 | tick 判重禁聚合数；产业链图谱数据审计修复循环 | check_tick_duplication.py；data_audit_sop/industry_chain_data_audit_policy | M1 |
| D6 | CH 热库落库 | ClickHouse 热层 DDL 应用/分区监控/配置 | src/zephyr/data/ch_config.py、ch_parts_monitor.py；scripts/ch/apply_*_ddl.py | M1 |
| D7 | PG 架构库 | depgraph 9148 节点+元数据底座（架构数据=DB 侧真源） | postgresql://localhost:5432/depgraph；generate_project_depgraph.py | M1 |
| D8 | 冷库归档运维 | F:/zephyr_cold Parquet 冷库 archive/restore 五重安全阀+清单 manifest | scripts/ch/archiver.py archive-range/list/stats/restore | **未归属** |
| D9 | 备份 3-2-1 双链 | 六阶段备份+CH vhdx 双链(F 主/G 二)+06:00 DailyBackup+离场月度 | scripts/backup/backup.ps1、backup_ch_vm.ps1、restore.ps1；手册=disaster_recovery_backup/storage_map.md | **未归属** |
| D10 | 行情订阅分发 | tick 订阅常驻+盘中实时/分钟/分时槽位 | sch_tick_subscriber、data_slot_intraday_realtime/minute（资源画像册） | M1 |
| D11 | TDM 交叉轴挂接 | 业务资产 16 表挂 TDM 交叉轴（_XREF_SPECS 表驱动），新库挂接义务 | src/zephyr/trading/decision_map.py（_XREF_SPECS）；alignment_checklist.md | M1 |
| D12 | 产业链图谱 | 873 条产业链(活跃/deprecated)图谱数据面 | docs/01.../catalogs/chain_registry.yaml | M1 |

### B. 交易决策与执行段（T1-T12，大片未归属）
| # | 环节 | 一句话 | 主入口 | 归属 |
|---|---|---|---|---|
| T1 | TDM 决策地图本体 | 138 节点交易决策地图：逐层六步法+S1-S9 消费场合+四道前置检查 | docs/02.../07_trading_decision_architecture/；sop/trading_decision_map_sop 两政策 | **未归属** |
| T2 | Regime 状态判定 | HMM 四态/水温五档/CRISIS-RECOVERY-BREAKOUT 覆盖层；DAL 决策算法 27 条 | src/zephyr/regime/；decision_algo_registry.yaml | M2 |
| T3 | 预案引擎 | 明日操作边界/盘前约束加载/尾盘加减仓三件套 | src/zephyr/plan_engine/（MOD-PLAN-001~003） | **未归属** |
| T4 | 信号与策略族 | A股特色/基本面信号+信号质量+因子 175+策略 161+策略工厂 | src/zephyr/signal_ashare/、signal_fundamental/、factor/、strategy_factory/ | M2 |
| T5 | 组合构建 | 等权~Barra 8 模型权重分配（OOS 跑不赢 1/N 不晋升） | src/zephyr/pf_alloc/、pf_core/；portfolio_model_registry.yaml | **未归属** |
| T6 | 仓位管理 | 持仓跟踪/仓位计算/盈亏分析 | src/zephyr/position/ | **未归属** |
| T7 | 卖出决策 | 卖出信号生成/时机判断/退出策略 | src/zephyr/sell_decision/ | **未归属** |
| T8 | 执行核心(含打板族) | execution_engine+daban_* 打板六件套+async_fill_dispatcher | src/zephyr/ex_core/execution_engine.py、daban_*.py | **未归属** |
| T9 | 执行路由 SOR | 订单路由/智能拆单/场所选择+broker 适配管理 | src/zephyr/ex_sor/core/broker_adapter_manager.py | **未归属** |
| T10 | 实盘 QMT 桥 | miniQMT 通道+文件桥 broker/行情/集成+交易会话+链路探针 | src/zephyr/ex_core/adapters/miniqmt_broker.py、qmt_file_bridge_*.py、qmt_trading_session.py、broker_link_probe.py | **未归属** |
| T11 | 风控限额与 kill switch | risk_limit 117 条九类+交易级 trading_kill_switch/stop_gate/protection_index+容量/回滚级 kill switch | src/zephyr/risk/；trading/trading_contracts/risk/trading_kill_switch.py；security/access_control/kill_switch.py | **未归属** |
| T12 | 合规门与程序化报告 | 先报告后交易铁律 ReportGate C-002 拒单+硬边界 FeatureGate | src/zephyr/compliance/；compliance_report_registry.yaml、feature_adjudication_registry.yaml | **未归属** |

### C. 回测模拟段（B1-B8，全归 M2）
| # | 环节 | 一句话 | 主入口 | 归属 |
|---|---|---|---|---|
| B1 | 回测三件套 | universe 7/benchmark 9/cost_model 6 每次回测 MUST 指定 | docs/01.../catalogs/universe/benchmark/cost_model_registry.yaml | M2 |
| B2 | 回测引擎族 | 事件驱动引擎+CH tick replay+撮合逻辑+组合核算 | src/zephyr/backtest/core/matching_engine.py、ch_tick_replay.py | M2 |
| B3 | 回测预注册与七步循环 | backtest_backlog 137 对象跑前写死阈值；无注册不归档；E4 正考 | scripts/backtest/generate_backtest_backlog.py；sop/backtest_system_sop/sop_a、sop_b | M2 |
| B4 | 实验登记与档案 | experiment_registry 11 条 FallbackBackend 本地 JSON+Panel 实验 Tab | docs/01.../catalogs/experiment_registry.yaml | M2 |
| B5 | GPU 矩阵/工厂格子 | 35.33s/格×4640 格重排三案+gpu_consensus/gpu_monitor | src/zephyr/trading/gpu_consensus_scheduler.py、gpu_monitor.py；docs/_working/e2e_integration/LEDGER.md | M2 |
| B6 | T0/成本门/IBT | T0 成本模型+考试成本双口径门 exam_cost_gate+复权降级 | src/zephyr/backtest/regime_validation/exam_cost_gate.py | M2 |
| B7 | 模拟盘 | 模拟撮合+涨板队列+前视偏差检测+钱包 19:30 会话+sim bridge 执行 | src/zephyr/simulation/；sch_paper_session、sch_sim_bridge_execute | M2 |
| B8 | AutoRuntime Core | 三层运行时运营中心(系统大脑)：三层路由/节律调度/work DAG | `python -m zephyr.trading`→src/zephyr/trading/auto_runtime_core.py | M2 |

### D. AI 层段（A1-A8，归 M4）
| # | 环节 | 一句话 | 主入口 | 归属 |
|---|---|---|---|---|
| A1 | AI 六族管线 | 感知 L1/摄入 L2/清洗 L3/对比 L4/排产 L5/开关 L6/传承 L7 | src/zephyr/ai_layer/{perceive,intake,cleaning,comparator,scheduling,switch_engine,heritage}/ | M4 |
| A2 | AI 红线 | negative_list 负面清单/年审/会话环境守卫/严重度路由 | src/zephyr/ai_layer/redline/ | M4 |
| A3 | LSG 安全网关 | 全部 LLM 调用必经：五层防御+注入检测+行为审计 | src/zephyr/security/llm_defense/llm_security/gateway.py | M4 |
| A4 | 本地模型与嵌入 | ollama 服务+嵌入路由双维度+24/7 排程+reranker | data/capability_cards/{ollama_chat,embedding_router,local_model_scheduler,reranker}.yaml | M4 |
| A5 | Agent 编排与 A2A | orchestrator+autonomy skills 60+/A2A 协议+M1-M11 管线编排+三层运行时 | src/zephyr/orchestrator/、autonomy_core/、integration/mcp/ | M4 |
| A6 | 能力反查渐进披露 | capability 378 条 canonical+44 卡片+12 生成器别名 | src/zephyr/governance/capability_lookup.py；data/capability_cards/ | M4 |
| A7 | 原问题账本 meta_question | PG 三表全生命周期：入库闸五要素/一问一考/墓碑不复用 | src/zephyr/governance/meta_question/registry.py（MetaQuestionRegistry） | M4 |
| A8 | PG 图书馆 | librarian/lookup/collectors/relations+血肉编目 SOP+台账备份任务 | src/zephyr/library/librarian.py、lookup.py | M4（lane 表未点名，建议确认收编） |

### E. 治理门禁段（G1-G14，主归 M3）
| # | 环节 | 一句话 | 主入口 | 归属 |
|---|---|---|---|---|
| G1 | commit 侧门禁链 | 23 环节/115 子环节——commit_speedup 战役已挖，本战役引用不重挖 | 提交链战役 00_skeleton | M3(引用) |
| G2 | GateEngine 运行时门禁 | 91 门禁 canonical+GatePipeline 编排+MAD 准入+进程内门禁 | src/zephyr/gov_enforcement/rule_enforcement/；in_process_gate_registry.yaml | M3 |
| G3 | 漂移检测 | 30 检测器注册调度+基线/增量/级联/金丝雀+双 watchdog 任务 | src/zephyr/gov_drift/；sch_drift_watchdog、sch_worktree_drift_watchdog | M3 |
| G4 | 红蓝对抗 | 攻击场景 53+宪法条款 44+red_blue_validator | src/zephyr/security/adversarial_validation/、red_blue_validator/ | M3 |
| G5 | 规则与裁定体系 | 86 trae_*.yaml+rule_catalog 256+ruling_registry 同 commit 原子 | docs/01_policies_and_standards/rules/；ruling_registry.yaml | M3 |
| G6 | 审计体系 | gov_audit 编排+语义/供应链/隐私审计+Merkle 小时链+AI-00~22 域审计 | src/zephyr/gov_audit/；根 audit_prompts_20_ai.md；docs/_working/audit_all/ | M3 |
| G7 | 代码质量与克隆守卫 | code_dedup+AST/micro-clone+extract 级克隆无逃生 | src/zephyr/gov_code_quality/、zephyr/clone_guard/ | M3 |
| G8 | 会话并发治理 | session_concurrency 注册+lock claim+worktree 四证+gateway/queue | src/zephyr/security/access_control/session_concurrency.py；scripts/git_commit.py | M3(引用 commit 链) |
| G9 | 密钥治理 | secrets.py 唯一通道+三道 gate+生命周期+外泄轮换裁决 | src/zephyr/shared/security/secrets.py、gov_enforcement/rule_enforcement/secrets_guard.py、security/access_control/secrets_lifecycle.py；SECRETS.md | **未归属** |
| G10 | 术语三层翻译体系 | 术语/域/模块三册 7776 条+i18n loader+覆盖 gate+reconciler | terminology_glossary.yaml 等；gov_enforcement/commit_gates/translation_coverage_gate.py | **未归属** |
| G11 | 回滚恢复 | 双轨 checkpoint+四级回滚+自动触发+G0 验证自愈 | src/zephyr/infrastructure/rollback/ | M3 |
| G12 | 人机门位 | 域风险分级 18 条→四类 Owner 门位；未列出默认 low | docs/01.../catalogs/risk_tier_registry.yaml | M3 |
| G13 | 注册表族治理 | ROOR 76 册+master_index 55+一致性契约 15 字段+净零审计 | docs/registry_of_registries.yaml；generate_registry_master_index.py | M3 |
| G14 | 契约冻结与错误码 | freeze_manifest 38 冻结契约+error_code 788 SSoT | src/zephyr/shared/contracts/freeze_manifest.yaml；architecture_model/contracts/error_code_registry.yaml | **未归属** |

### F. 调度常驻段（S1-S10，主归 M5）
| # | 环节 | 一句话 | 主入口 | 归属 |
|---|---|---|---|---|
| S1 | Windows 计划任务群 | sch_* 31 任务+ops_* 12+数据槽位 29+drill 3+event 3+manual 17+dynamic 1=96 实体 | config/resource_profile_registry.yaml；scripts/register_*.ps1 | M5 |
| S2 | 数据调度常驻 | integrator start 常驻进程+tick 订阅+槽位调度 | src/zephyr/data/scheduler.py | M5(调度面)与 M1(数据语义)共管 |
| S3 | belt daemon | 提交带 daemon+心跳线程化（长 drain 心跳不可达病根在修） | src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py；register_belt_daemon_task.ps1 | M5 |
| S4 | reaper 与水位监控 | 进程收割+RAM/commit 水位 breached+keep 白名单+ghosts | src/zephyr/trading/process_reaper.py（check_system_watermark 接线 :1065）；register_process_reaper_task.ps1 | M5 |
| S5 | 资源画像与排班 | 96 实体 18 字段画像+采样器/冲突闸/晨报/周历五模块 | config/resource_profile_registry.yaml；MOD-RESCHED-PROFILE/SAMPLER/GATE/ALERT/VIEW | M5 |
| S6 | 监控告警 | alert_threshold 38 条+health_monitor+status_dashboard+deadman+双 watchdog | src/zephyr/trading/health_monitor.py、status_dashboard.py；scripts/deadman_switch.ps1 | M5 |
| S7 | 订单与结算常驻 | 结算对账/三方核对/盘后管线/EOD/夜班队列/recon | src/zephyr/trading/settlement_reconciliation.py、three_way_reconciliation.py、post_settlement_pipeline.py、night_shift_queue.py；sch_post_settlement | M5 |
| S8 | 自动化班底 | 双引擎两班制(治理班×业务班)夜班 9 席+晨报插单协议 | sop/automation_sop/automation_crew_policy；docs/_working/cmd_ledger/automation_master_plan.md | M5 |
| S9 | 反馈循环 FBL | collectors/detectors/diagnosers/actors/SLO+验证门禁+自动回滚 | src/zephyr/feedback_loop/ | **未归属** |
| S10 | 环境与启动链 | 冷启动三步+windows_service+desktop shell+AI wrapper 注入 | src/zephyr/trading/windows_service.py；scripts/register_desktop_shell_startup.ps1、ensure_ai_wrapper_injection.ps1 | **未归属** |

### G. 前端 API 段（F1-F5，主归 M6）
| # | 环节 | 一句话 | 主入口 | 归属 |
|---|---|---|---|---|
| F1 | Panel 仪表盘 | app_panel 主面板+组件族(qmt_bridge_health 等)+服务注册 | src/zephyr/frontend/dashboard/app_panel.py、services_registry.py | M6 |
| F2 | API server | dashboard/api_server+前端 API 代理+trading/api | src/zephyr/frontend/dashboard/api_server.py、frontend_api_proxy.py | M6 |
| F3 | 可视化渲染器 | 图谱/血缘/瀑布/价值流/域映射五视图渲染 | src/zephyr/frontend/{graph_view_renderer,lineage_view_renderer,trace_waterfall_view,value_stream_view,domain_mapping_view}.py | M6 |
| F4 | 通知路由 | notification_router 告警/事件分发到前端 | src/zephyr/frontend/notification_router.py | M6（lane 表未点名，建议确认收编） |
| F5 | 报告生成 | 投资/风险/合规三类报告生成与分发 | src/zephyr/reporting/ | **未归属** |

### H. 全局横切段（X1-X7）
| # | 环节 | 一句话 | 主入口 | 归属 |
|---|---|---|---|---|
| X1 | SOP 方法论族 | 12 族方法论真源（挖矿/施工/数据操作/回测/审查/运维/自动化/图书馆等） | docs/01_policies_and_standards/sop/README.md | **未归属**(总筹引用，禁重挖) |
| X2 | 文档资产体系 | 目录册 87+统一资产索引 33249+rule_catalog 256+模板册 | docs/01.../catalogs/directory_registry.yaml；data/asset_index/unified-asset-index.yaml | **未归属** |
| X3 | 四盘存储地图 | D 生产/F 冷储/G 备份/offsite 离场 3-2-1 布局真源 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/storage_map.md（INFRA-STORE-003） | **未归属**(与 D9 同件，建议同车道) |
| X4 | 双引擎自动化总计划 | Qoder 白班×GLM 夜班×GPU 专道调度唯一真源 L0-L6 | docs/_working/cmd_ledger/automation_master_plan.md | M5 |
| X5 | 研究性三域 | 数字孪生/跨资产/执行仿真（设计态，运行证据弱） | src/zephyr/{digital_twin,cross_asset,execution_simulation}/ | **未归属**(待裁) |
| X6 | 研究域 | 事件研究 sell-the-news+假设注册/证据链 | src/zephyr/research/ | **未归属**(待裁或 M2 扩) |
| X7 | 管线路由 M1-M11 | blueprint_routing 30 条路由+pipeline_orchestrator 三层编排 | config/blueprint_routing.yaml；data/capability_cards/pipeline_orchestrator.yaml | **未归属**(待裁，M4/M5 边界) |

## 二、车道覆盖面映射（M1-M6 各收编哪些编号）

| 车道 | 收编环节 | 计 |
|---|---|---|
| M1 数据链 | D1-D7、D10-D12（D8/D9 漏） | 10 |
| M2 回测模拟 | T2、T4、B1-B8（TDM 本体/预案/组合/仓位/卖出/执行族漏） | 10 |
| M3 治理门禁 | G1-G8、G11-G13（secrets/术语/契约冻结漏） | 11 |
| M4 AI 层 | A1-A8（A8 图书馆为扩展建议） | 8 |
| M5 调度常驻 | S1-S8、X4（FBL/启动链/备份运维漏） | 9 |
| M6 前端 API | F1-F4（F4 为扩展建议；F5 报告漏） | 4 |
| **未归属** | D8、D9、T1、T3、T5-T12、G9、G10、G14、S9、S10、F5、X1、X2、X3、X5、X6、X7 | **24** |

## 三、漏项清单与归属建议（逐个，24 项）

| # | 漏项 | 证据锚点 | 归属建议 |
|---|---|---|---|
| 1 | 实盘 QMT 桥 | ex_core/adapters/qmt_file_bridge_broker.py 等 5 件+qmt_trading_session+broker_link_probe+ops_qmt_watchdog | **新开 M7 实盘执行链**（T8-T12 一并收编）；M5 只管 watchdog 常驻 |
| 2 | 风控 kill switch（交易级/容量级/回滚级三实例族） | trading_contracts/risk/trading_kill_switch.py+kill_switch_state_store；infrastructure/capacity_assurance/kill_switch.py；rollback/kill_switch.py；security/access_control/kill_switch.py | 交易级→M7；治理注册表面（kill_switch 限额 62 条）→M3 |
| 3 | 备份冷储运维（3-2-1 双链+离场月度） | scripts/backup/backup.ps1 六阶段+storage_map INFRA-STORE-003+ops_daily_backup/ops_weekly_vm_backup | M5 扩（自动化面）或并入 M7 基建运维 |
| 4 | 冷库归档运维 | scripts/ch/archiver.py（五重安全阀 v1.3.0 契约） | M1 扩（数据链尾端）或 M7 |
| 5 | PG 图书馆 librarian/lookup | src/zephyr/library/（M4 lane 表只点名 meta_question 未点名图书馆） | M4 显式收编确认 |
| 6 | 术语三层翻译体系 | 三册 7776 条+translation_coverage_gate+translation_coverage_reconciler | M3 扩 |
| 7 | 密钥治理 secrets | shared/security/secrets.py+secrets_guard+secrets_lifecycle+SECRETS.md+总计划 §7-3 轮换裁决 | M3 扩 |
| 8 | 性能水位监控 | process_reaper check_system_watermark（watermark/ram/commit breached 字段）+alert_threshold_registry 38 条 | M5 已可覆盖（S4/S6），要求显式列入台账 |
| 9 | TDM 决策地图本体（138 节点） | docs/02.../07_trading_decision_architecture/+tdm_consumption_policy S1-S9 | M2 扩或专列 TDM 车道（消费侧与 B 段强耦合） |
| 10 | 预案引擎 plan_engine | src/zephyr/plan_engine/ 三件套 | M2 扩（回测→预案衔接） |
| 11 | 组合构建 pf_alloc/pf_core | portfolio_model_registry 8 模型 | M2 扩 |
| 12 | 仓位管理 position | src/zephyr/position/ | M2 或 M7 |
| 13 | 卖出决策 sell_decision | src/zephyr/sell_decision/ | M2 或 M7 |
| 14 | 执行核心 ex_core（打板族） | execution_engine+daban_* 六件套 | M7 |
| 15 | 执行路由 ex_sor | broker_adapter_manager+broker_api_connector | M7 |
| 16 | 合规门与程序化交易报告 | compliance/ ReportGate+compliance_report_registry（先报告后交易铁律） | M7（实盘前置闸） |
| 17 | 反馈循环 FBL | src/zephyr/feedback_loop/ 四件套+SLO | M5 扩（监控自动化） |
| 18 | 环境与启动链 | windows_service+desktop shell+AI wrapper 注入 | M5 扩（四要素"自动触发/自动运行"前置） |
| 19 | 报告生成 reporting | src/zephyr/reporting/ | M6 扩 |
| 20 | SOP 方法论 12 族 | sop/README.md | 总筹引用不重挖（口径：方法论=挖干判据输入，非施工环节） |
| 21 | 文档资产体系 | directory_registry 87+unified-asset-index 33249 | M3 扩（注册表族） |
| 22 | 研究性三域（数字孪生/跨资产/执行仿真） | src/zephyr/{digital_twin,cross_asset,execution_simulation}/ | 待裁：设计态无运行证据，建议挂起不入车道 |
| 23 | 研究域 research | src/zephyr/research/（事件研究/假设注册） | 待裁：或 M2 扩 |
| 24 | 管线路由 M1-M11 | config/blueprint_routing.yaml 30 条+pipeline_orchestrator | 待裁：M4（Agent 编排）或 M5（调度）边界 |

**核心建议**：新开 **M7 实盘执行与基建链** 车道，一次收编漏项 1/2(交易面)/3 或 4/12-16/18/22 共约 10 环节——这是 M1-M6 覆盖面外最大连续空洞；余下为既有车道扩展确认（M3×4、M5×2、M6×1、M4×1、M2 扩×3）。

## 四、环节计数与覆盖率自审（三态结论）

- 环节总数：**76**（D12+T12+B8+A8+G14+S10+F5+X7；不含 commit 链已挖的 23 环节/115 子环节——按总筹册 §四 引用不重挖）。
- 归属分布：M1=10 ｜ M2=10 ｜ M3=11 ｜ M4=8 ｜ M5=9 ｜ M6=4 ｜ **未归属=24**（含 3 项待裁）。
- 覆盖率：M1-M6 现口径覆盖 52/76 = **68.4%**；若采纳 M7+扩展建议则 75/76 = 98.7%（仅 X1 SOP 族按口径挂总筹）。
- **三态结论：待挖（骨架本体已挖干，覆盖面未闭合）**——本册七源交叉验证完成、76 环节每行有主入口锚点=骨架级挖干；但 24 环节无车道收编（其中实盘执行链 7 环节连续无主），M7 裁定前不得宣称全链路覆盖。总筹裁 M7 与各扩展项后翻"挖干可施工"。

## 五、顺带发现的登记口径漂移（移交 M3，不在本册修）

1. 功能域册物理 94 条 vs ROOR REG-FUNC-DOMAIN-001 entry_count=83（漂移 11）。
2. 模块册物理 7776 条 vs 口径"7775 条"（漂移 1）；其中 UNKNOWN 域 2110 条（26.9%）无域归属。
3. SOP README 实为 12 族（11 文件夹+根 audit_prompts）vs AGENTS.md §6 "九族索引"表述过期。
4. ROOR 自身 summary.total_registries=76 与 by_tier 12+30+34=76 一致（本次实测无漂移）。

## 六、复核命令（10 分钟口径）

```bash
# 1. 四源计数对账
grep -c "registry_id:" docs/registry_of_registries.yaml
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml',encoding='utf-8'));print(len(d['entries']))"   # 94
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml',encoding='utf-8'));print(len(d['entries']))"  # 7776
ls data/capability_cards/ | wc -l                                          # 44
python -c "import yaml;d=yaml.safe_load(open('config/resource_profile_registry.yaml',encoding='utf-8'));print(len(d['entities']))"  # 96
# 2. 关键漏项锚点存在性
ls src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py src/zephyr/security/access_control/kill_switch.py src/zephyr/shared/security/secrets.py scripts/backup/backup.ps1 src/zephyr/library/librarian.py src/zephyr/feedback_loop/
```
