---
ttl: permanent
doc_type: architecture_view
title: 监控告警与复盘
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-17
topic: monitoring_review
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-15/16 第 5 批（会话 AI-MON-001，6 笔提交合并回 dev）落码三件套——MOD-RK-23 + MOD-RPT-009 + 阈值注册表 REG-ATH-001（施工时 32 条 active 阈值，2026-08-16 复核实测 33 条）；退役判据四条阈值经裁定转正（评审触发器而非自动关停——误触发成本远低于漏触发，风险优先取早触发侧）。
>
> **最终成果**：监控告警与复盘体系生产态；test_alert_threshold_consistency.py 机器锁定注册表↔代码双向一致性（32 条全量对账）；错误码 RK/RPT 两域全量补登。
>
> **未做事项及原因**：~~存量模块码内阈值统读改造（8 处）未做~~——**已于 2026-08-17 由 AI-THD-001 完工闭环（遗留 #87 销项）**：9 存量模块经共享加载器 shared/alerts/threshold_loader.py fail-closed 统读注册表，码内硬编码清零、数值零漂移、显式传参覆盖通道全保留；对账测试演化为接线校验+红队 fail-closed 36 用例全绿。
>
> **2026-08-19 复核补正（AI-NIGHT-001）**：§7"代码层新发现问题"第 3 条（Panel"实验历史"Tab 未施工）已过时——该 Tab 已由 51 号工作流 B 于 2026-08-16 建成（`frontend/dashboard/app_panel.py` v3.4.0 `_tab_experiment_history`，实证在位）；§3.4 偏离度量看板与之合并施工的选项仍成立。另：§6 四项暂缓（Email/WeChat sender 实发 / miniQMT 下单链路探针 / 偏离归因分解 H-A~D / 模板引擎固化）复核实证均未施工，均带重评条件属设计内延期，裁定=未来工程-小型。报告其余口径（三件套落码 / 33 条阈值 / 退役判据转正 / 统读闭环）与代码实证一致。

# 监控告警与复盘

> **性质**：决策备忘（G26）。核心立场：**复用优先，新造最少**——告警分级、回撤阈值、日终审计、日/周/月报告、发布归档均已 production，本文的决策重点是**编排与统编**，真正的新设计只有三块：实盘 vs 回测偏离度量、策略退役标准、复盘编排器+模板（§3.4-3.6）。
> **历史说明**：00_index 标本文"active v1.21.0"，磁盘仅存骨架——完整版曾丢失，本版按已施工代码 + 50/54 号设计依据重建为 1.0.0。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G26 监控告警与复盘 |
| 所属 | 跨作战地图 |
| 依赖 | G25（[54_reconciliation_attribution](54_reconciliation_attribution.md)，对账归因链路） |
| 对标 | 机构 PM 周报 / 风控周报 |
| 正交性 | ✅ 与 regime 正交 |
| 优先级 | P5 |
| 状态 | ✅ active v1.0.1（复用资产已 production；三块新设计标"待施工"） |

## 2. 背景

**项目处境**：54 号（G25）已建成"成交→对账→归因→报表"链路（10/12 环节 production）；50 号（回测可观测性）明文划界——"不做实时监控，实时监控是另一工程"，即本文范围。项目已有大量监控零件散落在 risk/reporting/shared/trading 各域，缺的是"把它们编排成一个人能用的监控-告警-复盘闭环"。

**核心问题**：个人系统没有风控团队盯盘，监控告警必须回答三个问题：①系统活着吗（数据/引擎/下单链路）？②策略还正常吗（实盘 vs 回测偏离）？③什么时候该让策略退役（连续跑输/逻辑失效）？且复盘产出必须落到"人可读"的文档，否则迭代无方向（54 号裁定：归因清晰度是生存项）。

**约束条件**：单机无热备、个人运维（RTO<5 分钟）——告警必须分级防风暴、复盘必须自动化产出（人只读周报复盘）；不能与 50 号（回测侧版本化）重复建设。

## 3. 决策

### 3.1 已施工设施盘点（复用资产，全部 production）

**A. 系统健康监控（要点①，大部分已施工）**

| 设施 | 位置 | 功能/why |
|---|---|---|
| HealthMonitor（K8s 风格 Liveness/Readiness 探针 + 压力四级 + 自动重启≤3 次） | trading/health_monitor.py L85-446 | 回答"组件是否存活/可服务"；事件驱动无 daemon 轮询，适配单机 |
| MetricsRegistry（Counter/Gauge/Histogram，Prometheus 文本导出）+ /metrics HTTP 端点 | shared/observability/metrics.py L88-272, metrics_server.py | RED 方法论（Rate/Error/Duration）；label 低基数防爆炸 |
| 数据链路 6 条 Prometheus 告警规则（tick 丢弃/队列水位/WAL 容量/CH 写失败） | shared/observability/dashboard/alert_rules.py | 覆盖"数据链路"维度健康 |
| GPU/资源监控（nvidia-smi 优雅降级） | trading/gpu_monitor.py | RTX 3090 显存 <90% 硬上限的执行探头 |
| OTel tracing（未装降级 NoopSpan） | shared/observability/tracing.py | 分布式追踪按需启用 |

**B. 告警通知（要点③，机制已施工）**

| 设施 | 位置 | 功能/why |
|---|---|---|
| 三级告警分级：RED→{log,email,wechat} / ORANGE→{log,email} / YELLOW→{log} | risk/core/alert_generator.py L73-189 | 分级纯机制零参数；日志必达、外部通道 best-effort 不阻断 |
| 告警去重（同源同消息 5 分钟抑制） | 同上 L293-331 | 防告警风暴——个人运维没有值班团队消化重复告警 |
| 回撤三级阈值 5%/10%/15% + 事件去抖 | risk/core/drawdown_tracker.py L94-311 | 监控导向，仅级别变化时发射 |
| 告警升级链（300s 无人认领自动升级）+ 精确率/召回率自评估 | shared/alerts/alert_escalation.py, alert_precision_tracker.py | 防"狼来了"——告警质量本身被监控 |

**C. 复盘产出（要点④⑥，报告骨架已施工）**

| 设施 | 位置 | 功能/why |
|---|---|---|
| DailyAuditor 日终五件套（PnL 对账 0.1% 容差/归因偏差/限额合规/检查清单/自动登记 IssueRecord） | risk/core/daily_auditor.py L844-896 | 日级复盘核心引擎；幂等可重跑；"任一 FAIL→整体 FAIL" |
| 日/周/月四类风险报告（DailyRiskSummary/EventRiskFlash/WeeklyRiskDeep/MonthlyRiskGovernance） | reporting/risk_report_engine.py | 日/周/月节奏的产出物骨架已存在 |
| A 股绩效审计 5 类规则 + 自动改进建议 | reporting/ashare_performance_audit.py | 复盘中的"审计+建议"环节 |
| ReportPublisher 唯一出口（12 类源 + 哈希链归档防篡改） | reporting/report_publisher.py L64-95 | 复盘文档的归档与分发通道 |
| PLV 上线后验证规约（Paper vs Live 订单量 ±1% 等 5 项） | governance/lifecycle_governance/post_live_verification.py | 最接近"实盘 vs 模拟偏离"的已施工规约 |

### 3.2 决策一：系统健康监控 + 操作风险审计 = 编排现有资产，不新造

把 HealthMonitor（组件）+ MetricsRegistry/alert_rules（数据链路）+ alert_generator（风险）三路汇入统一"系统健康总览"看板（frontend/dashboard 持仓监控 Tab 旁扩展）。**缺口待施工**：miniQMT 下单链路专门探针（连接状态/下单延迟/回报延迟）——40_execution_broker P0 缺口清单已含断线重连，探针随其一并施工，不单独立项。

**操作风险审计扩展（BM-RC-08-E，design，v1.0.1 补）**：

- **定位**：L4 风控域 BM-RC-08 子环节，盘后/事件驱动触发；消费系统日志+操作记录+Agent 行为（D-INFRA / D-AUTONOMY）；数据流：系统日志+操作记录→系统故障检测+人为错误识别+Agent 失控检测+级联失败分析→操作风险报告 → BM-RES 策略迭代。代码映射：depgraph 无实现（设计态），本节为其补 why 层。
- **裁定**：**四类审计分类**（证据全部复用 §3.1 已盘点资产，不新造探头）——

  | 类别 | 覆盖 | 证据复用 |
  |---|---|---|
  | ①系统故障 | 数据链路中断/引擎崩溃/下单链路超时 | §3.1A HealthMonitor 压力四级+自动重启≤3 次记录、MetricsRegistry RED 指标、alert_rules 6 条数据链路告警 |
  | ②人为错误 | 手工干预/配置误改/阈值手工覆盖 | 告警升级链 alert_escalation 认领记录 + §3.3 阈值注册表变更审计 |
  | ③Agent 失控 | AI 生成指令越权/频率异常/目标漂移 | 53 号 §3.8 降级回退 5 态状态机触发记录 + kill switch 触发日志 |
  | ④级联失败 | 单点故障沿依赖链放大 | depgraph 依赖拓扑 + HealthMonitor 组件存活时序（传播路径回放） |

  **理由**：健康监控回答"现在活不活着"（实时探针），操作风险审计回答"过去为什么出事"（事后归因）——同一批资产双流复用，与本备忘"复用优先、新造最少"总立场一致。**降级**：审计未就绪→人工巡检（环节定义原口径）。**重评条件**：首批策略上线 + §3.3 阈值注册表施工后，评估四类分类的自动归规则（当前人工归类为主）。
- **契约/参数/接口**：审计报告产物 OperationalRiskReport `{report_id, period, category: system_fault | human_error | agent_runaway | cascade_failure, events: [...], root_cause, action_items}`——事件驱动即时产出 + 周度汇总走 ReportPublisher 归档，并入 §3.6 周复盘"偏离与告警事件"段。

### 3.2B 决策一扩展：模型风险审计（BM-RC-08-D，design，v1.0.1 补）

- **定位**：L4 风控域 BM-RC-08 子环节，盘后/定时触发；消费模型预测+实际收益（D-ML-SERVE / D-REPORTING）；数据流：模型预测+实际→SR 26-2 模型风险管理+5 类漂移检测（数据/概念/预测/标签/特征）+CUSUM 变点+过拟合检测+训练-服务一致性验证→模型风险报告 → BM-RES 策略迭代 / 因果链"模型漂移→降级"。代码映射：depgraph 无实现（设计态），本节为其补 why 层。
- **裁定**：**对标 SR 26-2（美联储模型风险管理框架）的轻量版**——三支柱裁剪为个人系统可承受口径，复用既有资产、不新建检测器栈：

  | 支柱 | 复用资产 | 防什么 |
  |---|---|---|
  | ①上线前验证 | [23_strategy_correlation_validation](23_strategy_correlation_validation.md) §3.3 过拟合检测引擎（参数稳定指数/PBO/CSCV） | 上线即过拟合 |
  | ②持续监控 | 23 号 §5.4 上线后漂移监控（CUSUM on rolling correlation + PSI 持续追踪）+ 本备忘 §3.4 实盘 vs 回测偏离度量 | 上线后漂移到过拟合 |
  | ③结果校准审计 | [36_var_es_monitoring](36_var_es_monitoring.md) §3.10 校准/重构/恢复子流程（Christoffersen 回测验证 + RECALIBRATE/REBUILD 动作链） | VaR 模型侧校准证据 |

  **5 类漂移体系统一口径与检测器分工**：

  | 漂移类 | 检测器 |
  |---|---|
  | 数据/特征漂移 | PSI（边际分布比较） |
  | 概念/标签漂移 | CUSUM（残差持续偏移） |
  | 预测漂移 | rolling IC/Sharpe 衰减（25 号衰减监控三层 + [61_lifecycle_multi_ai](61_lifecycle_multi_ai.md) §3.3 Drift Observatory 多方法组合） |

  阈值统一登记到本备忘 §3.3 阈值注册表（PSI>0.2 关注 / >0.4 高度，CUSUM h=4σ）。
  **理由**：把散落在 23/25/36/61 号的过拟合/漂移/校准资产**统编为一盘审计视图**——与 §3.2"编排不新造"同哲学；SR 26-2 机构全量形态（独立模型风险管理部门/年度审计）对个人系统是过度工程，轻量版保留"验证→监控→校准"三闭环即达生存需求。**降级**：审计未就绪→人工抽检（环节定义原口径）。**重评条件**：首批策略 3 个月 track record + 本备忘 §3.4 偏离度量施工后，5 类漂移阈值用实盘数据回归校准。
- **契约/参数/接口**：ModelRiskReport `{model_id, period, drift_findings: [{type, detector, value, threshold, verdict}], validation_ref（23 号过拟合报告）, calibration_ref（36 号 VaR 校准状态）, recommendation: continue | recalibrate | retrain_gate}`——`retrain_gate` 结论衔接 [54_reconciliation_attribution](54_reconciliation_attribution.md) §3.1.1 BM-REC-03-C 模型层反馈（重训练信号须过 C-003 回测门禁再回 BM-SEL-02），形成"审计→重训练→门禁→上线"链路。周度经 ReportPublisher 归档，并入 §3.6 周复盘议程。

### 3.3 决策二：告警阈值统编为注册表，阈值不集中即不可审计

**已施工**（2026-08-15 AI-MON-001，#ARCH-MON-001）：[alert_threshold_registry.yaml](../../01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml)（REG-ATH-001，11 类 35 条全代码锚点实证，ROOR 已登记）。

现状：阈值散落各模块（drawdown 5/10/15%、health 内存 70/80/90%、PLV ±1%……）。决策：建**告警阈值注册表**（YAML，随 12 业务注册表体系登记），各模块从注册表读阈值而非各自硬编码。why：个人系统唯一的"风控评审"就是复盘时看阈值清单——散落等于不可评审。Email/WeChat sender 当前 no-op 占位，待首批上线前注入实现（登记 §7）。

落地口径（施工裁定）：①挂法=独立注册表（§7③ 待裁定项的工程落地——阈值跨 11 类，risk_limit 9 类 limit_type 不覆盖运维类阈值；Owner 若裁定并表，YAML→YAML 迁移成本极低）；②本批新建模块（§3.4/§3.5）fail-closed 从注册表读阈值；③存量模块码内常量统读改造~~登记为后续治理项~~——**已完工（2026-08-17 AI-THD-001，tracker #87 销项）**：9 存量模块（drawdown_tracker/health_monitor/decision_gate/post_live_verification/alert_generator/alert_escalation/daily_auditor/risk_report_engine/operational_risk_monitor）经共享加载器 `src/zephyr/shared/alerts/threshold_loader.py`（MOD-INF-016 伞，ZA-SH-0050）fail-closed 统读，数值零漂移+显式传参覆盖通道保留+红队 36 用例全绿。

### 3.4 决策三（新设计）：策略偏离监控 = 实盘 vs 回测净值偏离度持续度量

**已施工**（2026-08-15 AI-MON-001）：`src/zephyr/risk/core/strategy_deviation_monitor.py`（MOD-RK-23，blueprint [_domain_risk/strategy_deviation_monitor](../../03_modules/_domain_risk/strategy_deviation_monitor/blueprint.md)，测试 44 项三件套全绿）。§7② 口径待裁定项落地=**两口径皆备**（累计收益相对偏差定 action / 日收益相关标注供周报复盘）。

已有零件（PLV 规约、position_drift_monitor 仓位内部漂移、daily_auditor 归因偏差）都不是"实盘 vs 回测"主线。决策：新建轻量偏离度量——每日收盘后计算实盘净值 vs 同期回测净值的两口径偏差（累计收益差 / 日收益相关），复用 decision_gate.monitor_backtest_live_deviation 的阈值体系（>30% 告警 / >50% 退役评估）；历史回测 run 由 experiment_tracking（50 号）供给基准。2026 年实证佐证该阈值区间：零售统计实盘低于回测 50% 即需结构性诊断（traderssecondbrain 2026-05），正常磨损为 10-20%。施工口径：事件去抖（仅级别变化发射）+ 样本不足只登记不判定 + 基准供给桥失败降级 None 不阻断；日收益相关下限 0.5 占位标 pending_adjudication（THD-DEVIATION-003，待首批上线数据回归校准）。

### 3.5 决策四（新设计）：策略退役标准 = 双判据 + 评审制

**已施工**（2026-08-15 AI-MON-001）：`src/zephyr/governance/lifecycle_governance/strategy_retirement_evaluator.py`（MOD-GOVERNANCE 伞，PLV 先例）。五判据执行体落地（滚动 20 日跑输 >5% / 滚动 60 日 Sharpe<0 / 回撤漂移 1.5×历史最大回撤 / 回测-实盘偏离 >50%（偏离值由 MOD-RK-23 供给不重算）/ 逻辑失效调用方供给）；标准值取 §7⑤ 候选默认并标 pending_adjudication（THD-RETIRE-001/002/003，待 Owner 裁定）；评审制铁律=判据触发只生成 RetirementEvaluationReport（ReportPublisher TRADING_REVIEW 源归档，status=pending_human_review），模块无策略状态写接口。

代码现状：仅因子级生命周期状态机有 retired 终态，model_drift_monitor 有一条静态登记"Sharpe 30 日<0→策略退役评估"。决策（标准值待裁定，见 §7）：
1. **连续跑输判据**——实盘滚动 N 日跑输基准超过阈值，或回测-实盘偏差 >50%（复用 decision_gate 阈值）；
2. **逻辑失效判据**——策略依赖的 alpha 信号被证伪（因子 IC 衰减退役联动 factor_registry decay_state，或打板生态结构性变化）；
3. **评审制**——退役不自动执行：判据触发 → 生成退役评估报告（ReportPublisher TRADING_REVIEW 源）→ 人工裁定。why 评审制：个人项目策略总数 ≤5，退役是重大资本重分配决策，自动化代价（误退役）远高于收益。

2026 年退役标准研究锚点（LuxAlgo 2026-08，与本判据体系一致，供裁定时参考）：滚动 expectancy 滑向 0、回撤漂移达历史最大回撤 1.5-2x、profit factor 滑向 1.0、WFA 持续失败、原始市场前提结构性失效；且这类阈值"是评审触发器，不是自动关停规则"——支持评审制。

### 3.6 决策五（新设计）：复盘编排器 + 复盘模板，频率裁剪为"日自动/周人工/月轻量"

**已施工**（2026-08-15 AI-MON-001）：`src/zephyr/reporting/review_orchestrator.py`（MOD-RPT-009，blueprint [_domain_reporting/review_orchestrator](../../03_modules/_domain_reporting/review_orchestrator/blueprint.md)）。日/周/月三频串联 + ReportPublisher 归档（日报 RISK 源 / 周报·月报 TRADING_REVIEW 源）；四段式周报模板结构固化为 WEEKLY_REVIEW_SECTIONS 常量 + 人工维护模板资产 [weekly_review_template.md](../../03_modules/_domain_reporting/review_orchestrator/weekly_review_template.md)（§6 暂缓项口径：先人工维护，跑 12 期后再固化模板引擎）；事件驱动零定时器（run_daily/run_weekly/run_monthly 由日终/周末/月末事件触发）。

三频复盘对个人过重的担心，用**自动化分层**化解而非砍频率：
- **日复盘 = 机器自动**——DailyAuditor 日终五件套 + DailyRiskSummary，人只看 FAIL 项（告警驱动）；
- **周复盘 = 人读**——WeeklyRiskDeep + 偏离度量周报，复盘会唯一固定议程，产出 action items 进 IncidentManager/候选库；
- **月复盘 = 轻量治理汇总**——MonthlyRiskGovernance + 策略退役判据扫描，不新开分析。
决策：**复盘编排器**（待施工）定时串联 daily→weekly→monthly 链路并调 ReportPublisher 归档；**复盘模板**（待施工）固定四段：本周盈亏与归因（54 号供给）/ 偏离与告警事件 / 阈值与参数变更 / 下周 action items。

### 3.7 与 50/54 号的边界

50 号管"回测侧可观测"（每次回测版本化、MLflow 薄包装），本文管"实盘侧监控告警复盘"；桥是 experiment_tracking——实盘 vs 回测对比以历史 run 为基准。54 号管"钱对不对得上"（对账归因），本文管"系统/策略健不健康"；54 号的归因产出是本文周复盘的输入。

## 4. 考虑过的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 引入 Grafana+Prometheus 全家桶外部栈 | 拒绝——单机个人运维，现有 MetricsRegistry 已能 Prometheus 文本导出，需要可视化时用 frontend/dashboard 集成（用户偏好统一前端），不另起运维面 |
| 日/周/月三频全人工复盘 | 拒绝——个人精力不够；日/月自动化、周人工是可持续上限 |
| 策略退役全自动化（判据触发即下线） | 拒绝——策略 ≤5 个，误退役代价大；评审制成本可忽略（2026 研究亦主张触发器+评审而非自动关停） |
| 统一自研监控中台模块 | 拒绝——复用优先；零件已 production，缺的是编排不是平台 |

## 5. 上限定义

**系统上限**：编排现有 production 零件 + 三块轻量新设计（偏离度量/退役双判据/复盘编排器），对个人系统已是上限。**演进路径**：告警阈值注册表先行（纯配置工作）→ 偏离度量随首批上线 → 退役评审在首批 3 个月 track record 后首次有真实输入。**为何是上限**：机构级监控中台（独立 SRE 团队、多账户聚合视图、容量规划）超出单人单账户硬边界（OE-002/003/006 已裁剪同族能力）。

## 6. 待裁定

| 暂缓项 | 暂缓理由 | 重评条件 |
|---|---|---|
| Email/WeChat sender 实现 | 当前 no-op 占位，日志通道必达已够开发期 | 首批策略实盘上线前必须注入 |
| miniQMT 下单链路探针 | 依赖 40_execution_broker 断线重连等 P0 施工 | 随 40 号缺口清单一并施工 |
| 偏离度量两口径之外加归因分解（H-A~D 四因子） | battle_map 明示为设计态，先总值报警器够用 | 偏离告警首次真实触发后按需补 |
| 复盘模板内容固化进代码（模板引擎） | 先人工维护模板，跑 3 个月稳定后再固化 | 周复盘跑满 12 期后 |

## 7. 待定问题（G26 六要点逐项裁定）

- [x] ① **系统健康监控**——✅ 大部分已施工（§3.1A）；缺口：miniQMT 下单链路探针（登记 §6）。
- [x] ② **策略偏离监控**——✅ 已施工（§3.4，MOD-RK-23）。口径裁定落地：两口径皆备（累计收益相对偏差定 action / 日收益相关标注供周报复盘）。
- [x] ③ **告警阈值与通知**——✅ 机制已施工；✅ 阈值注册表统编已施工（§3.3，REG-ATH-001 独立注册表）。**挂法裁定闭环（2026-08-15 Owner 裁定）**：维持独立注册表——阈值跨 11 类含运维类，risk_limit_registry 9 类 limit_type 管交易限额不覆盖运维阈值，并表会造异构 schema 违反 SSoT 分类铁律。遗留：存量模块码内常量统读改造~~（后续治理项）~~已闭环（2026-08-17 AI-THD-001，§3.3③）。
- [x] ④ **日/周/月复盘机制**——✅ 复盘编排器已施工（§3.6，MOD-RPT-009）。
- [x] ⑤ **策略退役标准**——✅ 双判据+评审制执行体已施工（§3.5）。**标准值裁定闭环（2026-08-15 Owner 裁定）**：候选值全部转正（滚动 20 日跑输 >5% / 滚动 60 日 Sharpe<0 / 回撤漂移 1.5x + THD-DEVIATION-003 相关下限 0.5，注册表 4 条 pending_adjudication→active）。裁定逻辑：判据=评审触发器非自动关停（评审制铁律），误触发成本=一份评估报告 ≪ 漏触发成本=僵尸策略持续亏钱，风险优先取早触发侧；校准点=首批上线数据回归（PLV 周期），改表即生效零代码改动。
- [x] ⑥ **复盘文档模板**——✅ 四段式模板已施工（§3.6，结构固化 + 人工维护模板资产）。

**代码层新发现问题**：
1. 54 号 §3.1 对 AsharePerformanceAudit 的能力描述（盘前信号验证/盘中 2σ 异常检测）超出实际代码（实际为 5 类绩效审计规则）——越界修正登记在此，不越界改 54 号。
2. shared/alerts 全组（alert_manager/dual_channel/escalation/precision_tracker/heartbeat_server）无测试——补测试列入工程 backlog。
3. 50 号规划的 Panel"实验历史"Tab（components/experiment_history.py）未施工——偏离度量看板可与其合并施工。
4. **00_index 同步（越界登记）**：00_index 标本文"active v1.21.0"，与本版 1.0.0 不一致，需同步（详见 33 号 §7 新发现 7 的统一登记）。

## 8. 引用

- [00_index_trading_decision](00_index_trading_decision.md) §3 G26
- [54_reconciliation_attribution](54_reconciliation_attribution.md)（G25 依赖：对账归因链路）
- [50_backtest_observability_workplan](50_backtest_observability_workplan.md)（回测侧划界："实时监控是另一工程"=本文）
- 07_d_infra_telemetry（可观测性域：experiment_tracking 定位——只管回测版本化，不做实时监控）
- 代码：trading/health_monitor.py、risk/core/alert_generator.py、risk/core/daily_auditor.py、reporting/risk_report_engine.py、reporting/report_publisher.py

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G26 讨论要点占位，待讨论填空 |
| 2026-08-12 | 1.0.0 | 骨架→active：回填已施工监控/告警/报告设施盘点；定五项决策（复用编排/阈值统编/偏离度量/退役双判据/复盘分层）；六要点逐项对齐；补 2026 研究锚点 | 完整版（v1.21.0）曾丢失，按已施工代码重建；新设计限最小三块并全标"待施工"；不擅自定参数，阈值候选入 §7 待人裁定 |
| 2026-08-12 | 1.0.1 | 作战地图全覆盖补丁——闭合 BM-RC-08-E / BM-RC-08-D：①§3.2 扩展为"系统健康+操作风险审计"（BM-RC-08-E design：四类审计分类——系统故障/人为错误/Agent 失控/级联失败 + OperationalRiskReport 产物，证据复用 §3.1 已盘点 HealthMonitor/MetricsRegistry/告警链/审计链资产，不新造探头）；②新增 §3.2B 模型风险审计（BM-RC-08-D design：对标 SR 26-2 轻量版"验证→监控→校准"三闭环 + 5 类漂移体系统一口径与检测器分工，串联 23 号 §3.3 过拟合检测 / 23 号 §5.4 CUSUM-PSI 漂移监控 / 36 号 §3.10 VaR 校准审计，recommendation=retrain_gate 衔接 54 号 §3.1.1 BM-REC-03-C 的 C-003 回测门禁链路） | 风控域两个 design 环节（depgraph 无实现）补 why 层，按"定位 → 裁定（理由+重评条件）→ 契约/参数/接口"格式回填；延续"复用优先、新造最少"总立场 |
| 2026-08-15 | 1.0.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-11）。§3.2/§3.2B 两段超长裁定散文（>300 字单段）表格化：四类审计分类→4 行表，SR 26-2 三支柱→3 行表，5 类漂移检测器分工→3 行表 | 单段超长纯散文表格化；参数/阈值/契约/链接/降级与重评条件逐字保留，零实质改动 |
| 2026-08-15 | 1.1.0 | 四项决策施工落地（AI-MON-001，#ARCH-MON-001）：§3.3 告警阈值注册表（REG-ATH-001，11 类 35 条全代码锚点）；§3.4 偏离度量（MOD-RK-23 双口径+事件去抖+experiment_tracking 基准桥）；§3.5 退役双判据评审制执行体（五判据，标准值 pending_adjudication）；§3.6 复盘编排器（MOD-RPT-009 三频+四段周报模板） | 三块"待施工"新设计+阈值注册表全闭合；§7 六要点逐项更新；施工裁定留痕（独立注册表挂法/两口径皆备/候选默认值占位待 Owner 裁定）；存量模块阈值统读改造登记后续治理项 |
| 2026-08-15 | 1.1.1 | §7 两项待裁定闭环（Owner 裁定，#ARCH-MON-001 遗留项批）：③挂法=维持独立 REG-ATH-001（异构 schema 违反 SSoT 分类铁律）；⑤退役判据标准值 4 条 pending_adjudication→active（评审触发器非自动关停，误触发成本≪漏触发成本，风险优先取早触发侧）；配套：error_code_registry 补登 RK/RPT 两域 23 条（含 6 新码）+ ZA-RPT-0003 重码改号 0007；AGENTS.md 速查表补 REG-ATH-001；新立 #ARCH-ERRCODE-001（15 处存量重码+全域补登）/#ARCH-DRIFT-AUTH-001（watchdog 授权通道缺口）两专项 | 遗留项全调研后逐项裁定；观察项实证修正（DRIFT-WATCHDOG 非误报=捕获真实乒乓写事件并自愈；GATE-RULE-AUDIT 超时已由 AI-TMO-001 闭环 60→180s）。注：tracker 登记编号原为 #75-81，与第四统筹/COMP 批既有编号撞号，已按"撞号重编"先例重编为 #85-92（commit 3f13a77d 消息中 #75-81 为旧号） |
