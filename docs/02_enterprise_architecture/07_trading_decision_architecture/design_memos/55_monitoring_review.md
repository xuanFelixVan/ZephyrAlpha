---
ttl: permanent
doc_type: architecture_view
title: 监控告警与复盘
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-12
topic: monitoring_review
scope: 07_trading_decision_architecture
---

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
| 状态 | ✅ active v1.0.0（复用资产已 production；三块新设计标"待施工"） |

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

### 3.2 决策一：系统健康监控 = 编排现有资产，不新造

把 HealthMonitor（组件）+ MetricsRegistry/alert_rules（数据链路）+ alert_generator（风险）三路汇入统一"系统健康总览"看板（frontend/dashboard 持仓监控 Tab 旁扩展）。**缺口待施工**：miniQMT 下单链路专门探针（连接状态/下单延迟/回报延迟）——40_execution_broker P0 缺口清单已含断线重连，探针随其一并施工，不单独立项。

### 3.3 决策二：告警阈值统编为注册表，阈值不集中即不可审计

现状：阈值散落各模块（drawdown 5/10/15%、health 内存 70/80/90%、PLV ±1%……）。决策：建**告警阈值注册表**（YAML，随 12 业务注册表体系登记），各模块从注册表读阈值而非各自硬编码。why：个人系统唯一的"风控评审"就是复盘时看阈值清单——散落等于不可评审。Email/WeChat sender 当前 no-op 占位，待首批上线前注入实现（登记 §7）。

### 3.4 决策三（新设计·待施工）：策略偏离监控 = 实盘 vs 回测净值偏离度持续度量

已有零件（PLV 规约、position_drift_monitor 仓位内部漂移、daily_auditor 归因偏差）都不是"实盘 vs 回测"主线。决策：新建轻量偏离度量——每日收盘后计算实盘净值 vs 同期回测净值的两口径偏差（累计收益差 / 日收益相关），复用 decision_gate.monitor_backtest_live_deviation 的阈值体系（>30% 告警 / >50% 退役评估）；历史回测 run 由 experiment_tracking（50 号）供给基准。2026 年实证佐证该阈值区间：零售统计实盘低于回测 50% 即需结构性诊断（traderssecondbrain 2026-05），正常磨损为 10-20%。**标"待施工"**，随首批策略上线一并落地。

### 3.5 决策四（新设计·待施工）：策略退役标准 = 双判据 + 评审制

代码现状：仅因子级生命周期状态机有 retired 终态，model_drift_monitor 有一条静态登记"Sharpe 30 日<0→策略退役评估"。决策（标准值待裁定，见 §7）：
1. **连续跑输判据**——实盘滚动 N 日跑输基准超过阈值，或回测-实盘偏差 >50%（复用 decision_gate 阈值）；
2. **逻辑失效判据**——策略依赖的 alpha 信号被证伪（因子 IC 衰减退役联动 factor_registry decay_state，或打板生态结构性变化）；
3. **评审制**——退役不自动执行：判据触发 → 生成退役评估报告（ReportPublisher TRADING_REVIEW 源）→ 人工裁定。why 评审制：个人项目策略总数 ≤5，退役是重大资本重分配决策，自动化代价（误退役）远高于收益。

2026 年退役标准研究锚点（LuxAlgo 2026-08，与本判据体系一致，供裁定时参考）：滚动 expectancy 滑向 0、回撤漂移达历史最大回撤 1.5-2x、profit factor 滑向 1.0、WFA 持续失败、原始市场前提结构性失效；且这类阈值"是评审触发器，不是自动关停规则"——支持评审制。

### 3.6 决策五（新设计·待施工）：复盘编排器 + 复盘模板，频率裁剪为"日自动/周人工/月轻量"

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
- [x] ② **策略偏离监控**——🔨 决策已定（§3.4），**待施工**。待裁定：偏离度量的具体口径（累计收益差 vs 日收益相关，还是两者皆备）。
- [x] ③ **告警阈值与通知**——✅ 机制已施工；🔨 阈值注册表统编待施工（§3.3）。待裁定：注册表挂到哪个既有 registry 文件（risk_limit_registry 扩展还是独立 alert_threshold_registry）。
- [x] ④ **日/周/月复盘机制**——🔨 频率分层决策已定（§3.6），复盘编排器**待施工**。
- [x] ⑤ **策略退役标准**——🔨 双判据+评审制决策已定（§3.5）。**待裁定（需人决策）**：连续跑输判据的 N（滚动窗口天数）与阈值——建议候选：滚动 20 日跑输基准 >5%，或滚动 60 日 Sharpe<0，或回撤漂移达历史最大回撤 1.5-2x（2026 研究锚点）；待首批上线前裁定。
- [x] ⑥ **复盘文档模板**——🔨 四段式模板决策已定（§3.6），**待施工**（先人工维护）。

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
