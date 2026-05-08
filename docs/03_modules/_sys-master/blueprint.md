---
module_id: "SYS-MASTER-001"
title: "ZephyrAlpha 系统总蓝图 — 三级金字塔架构与全部子系统拓扑"
doc_type: blueprint
status: active
version: "0.13.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-04"
valid_from: "2026-05-04"
ttl: permanent
last_updated: "2026-05-08"
blueprint_level: system
summary: "ZephyrAlpha 系统级总蓝图（Level 0 System Master）——三级金字塔顶点：102章全覆盖。经过七轮深度诊断(64→84→102→122→142→160盲点全覆盖), 覆盖 §0.0 四黄金信号(11 SLI+SLO目标值) + §十二 成本架构(7模型路由+TCO) + §4 跨模块数据流与关键集成点 + §十六 FMEA(8项) + §十三 数据分类L1~L4 + §十四 启停6Phase + §十五 氛围编程施工方法论 + §十七 测试策略 + §十八 灾难恢复 + §十九 模型风险 + §二十 事故响应 + §二十一 部署策略 + §二十二 合规映射 + §二十三 安全纵深 + §二十四~§三十五(Session/环境/仪表板/性能/供应链/数据质量/知识/迁移/术语/反模式/离线自治/第三方) + §三十六~§三十九(人机带宽/模型漂移/SPOF消除/质量保障) + §四十~§四十七(市场数据管线+回测/订单执行+风控/量化ML工程/运维深化/氛围编程深层/架构契约/1人保障/合规法律) + §四十八~§六十(策略验证/执行算法/多策略/经纪商/可重现/实盘验证/审查深度/组合压力/波动目标/因子择时/交易日历/运维基础/AI质量SPC) + §六十一~§七十(PnL归因+TCA/日运营节奏+交易会话协议/容错模式深度/微结构防御+模拟保真度/因子治理/功能开关+部署安全网/AI自诊断修复+知识自动化/氛围编程确定性保障/Secrets生命周期+环境可重建/离线分级应急+全生命周期预算) + §七十一~§九十(Prompt全生命周期管理+回归测试/AI上下文窗口策略+幻觉防御体系/多模型共识+辩论协议/AI代码生成标准+脚手架+禁止模式/实盘五级Kill Switch+安全保障矩阵/模拟→实盘五阶段过渡+回退/订单执行质量监控+异常检测/知识连续性+断供因子/本地优先+离线自主/决策疲劳+优先级分流/What-If仿真+灵敏度+MonteCarlo/代码考古+文档自动化/数据源可靠性+智能切换/混沌工程+故障演练/经济体制+宏观因子/AI可解释性+模型卡/SBOM+依赖情报/状态机形式化/DORA指标/A/B实验框架) + 🆕 §九十一~§一百〇二(企业行为与参考数据管线:七类CA+盘前5项检查+回溯修复/热重启与盘中恢复:6步协议+健康检查/会话并发与文件完整性:文件锁ZephyrLock+冲突检测+预分配/硬件容灾与基础设施:SSD-RAM-电源-散热-磁盘五维+SMART面板/API生命周期与弃用治理:三阶段Active→Deprecated→Removed+第三方变更监控/数据全生命周期与自动清理:Hot→Warm→Cool→Cold→Purge五阶段+AutoHousekeep/时间同步与时钟纪律:NTP三源+偏差监控+ISO8601规范/实时流式数据架构:Stream vs Batch双轨+背压防御+乱序重组/静默故障聚合与级联风险:AFS聚合评分+五类静默故障+级联路径建模/增量审查与部分接受:Chunk级ACCEPT/REJECT/MODIFY+审查时间预算/基准完整性与生存偏差防御:PIT Universe+四维完整性+基准漂移检测/跨环境一致性与平台风险:Windows 11风险矩阵+WSL/Native差异+幂等setup脚本)。七轮累计: 33+31+20+18+20+20+18=160盲点全覆盖。AI agent 冷启动第一站。"
construction_progress: completed
belongs_to: "ROOT"
ai_role_instruction: >
  你是 ZephyrAlpha 系统总蓝图（SYS-MASTER-001），是整个蓝图三级金字塔的顶点。
  新 AI session 第一站——所有 agent 在开始任何任务前 MUST 读 §0 分派表定位自己负责的子系统，
  然后导航到对应的 Level 1/Level 2 蓝图。
  核心规则：(1)本项目采用三层蓝图体系——你定义"全局怎么排"，
  MOD-MASTER-001 定义"系统间怎么连"，模块蓝图定义"模块内怎么干"；
  (2)蓝图冲突裁决链：PS-STD-005 > SYS-MASTER-001 > MOD-MASTER-001 > 模块蓝图；
  (3)你不会生成代码——你定义系统边界和架构原则，实现由模块蓝图指引；
  (4)新 AI session 冷启动默认读 §0 即可（~400 tokens），按任务域升级到 §1-§4；
  (5)所有施工 MUST 通过G0-G7门禁(§2)——跳过门禁=拒绝合并；
  (6)跨模块变更 MUST 先读MOD-MASTER-001 集成契约(§45)；
  (7)新增模块 MUST 登记到blueprint-registry.yaml + 继承模板；
  (8)系统健康面板 MUST 在每个session开始前自检(§0.0)；
  (9)成本感知(MUST)——选择模型前评估Token预算(§十二)，拒绝无预算的任务请求；
  (10)每次施工后 MUST 运行WQA七维自检(§三十九)：测试增量/蓝图对齐/ruff 0 warning/Gate不新增失败/Owner不回退/Session完成率/Token效率；
  (11)MUST 遵守§4.1.1编排时序约束——超时/乱序=立即告警；
  (12)L1~L4数据 MUST 按§十三控制访问——无例外；
  (13)系统启动/停止 MUST 按§十四 6Phase拓扑执行；
  (14)氛围编程MUST 遵守§十五的MUST/SHOULD/MAY三级指令——所有施工执行前验证规则；
  (15)所有变更MUST 通过§十七测试金字塔(单元→集成→E2E)；
  (16)灾难恢复MUST 按§18.4演练日历执行——未演练的DR计划=无效；
  (17)任何模型上线前MUST 通过§十九模型风险清单(MR101-MR113)；
  (18)事故响应MUST 按§二十 L1-L5流程+Telemetry告警联动+Gate升级矩阵执行；
  (19)部署MUST 通过§二十一 Canary→G0-G7门禁→渐进式推广→自动回滚窗口(§21.2 1h)；
  (20)所有交易相关模块MUST 遵守§二十二合规矩阵——实时、强制、不可跳过；
  (21)MUST 遵守§二十三 L1-L6纵深防御——任何环节失败=阻断施工；
  (22)每次Session开始MUST 读取§二十四 Session生命周期 + 执行 SessionContinuity 冷启动序列(project_rules.md STEP 3)；
  (23)环境管理MUST 遵守§二十五——Supervisor-only指令/IDE间隔离/全局快捷键；
  (24)§0.0面板中的任一SLI突破SLO MUST 记录为事故+通知Owner(§0.0.4)；
  (25)AI 代码MUST 记录AI provenance(§四十四)——模型版本/Prompt hash/Session ID/Owner审查决定；
  (26)架构变更MUST 记录ADR(L1全球3份+L2本地10份)——无ADR"MERGE决策"拒绝合并；
  (27)跨模块假设MUST 由MOD-MASTER-001集成测试验证——"我觉得能连"≠真的能连；
  (28)Owner离线时系统MUST 有自主冻结能力(§三十四)——不能赌Owner"刚好在线"；
  (29)所有组合级策略MUST 定期接受压力测试(§五十五)——5压力场景全部通过才合格；
  (30)所有杠杆使用MUST 经过波动率目标控制器(§五十六)——Vol Target=15%为系统默认；
  (31)跨资产/因子配置MUST 考虑相关性矩阵和当前市场状态(§五十七)——不能只按回测权重；
  (32)所有定时操作(数据拉取/合约换月/结算) MUST 基于交易日历(§五十八)——不能依赖系统时钟的"每个周一"；
  (33)备份 MUST 定期验证可恢复性(§五十九)——未验证的备份=没有备份；
  (34)AI 施工质量 MUST 运行统计过程控制(§六十)——质量退化需早于Owner感知前检测到；
  (35)交易日 MUST 按日运营节奏执行(§六十二)——开盘前检查→盘中监控→收盘对账,不跳步骤；
  (36)每个策略的PnL MUST 按因子/行业/风格/TCA四维归因(§六十一)——不接受"今天赚了3%"的笼统报告；
  (37)系统容错 MUST 实现Bulkhead+Retry+Backoff+Jitter(§六十三)——不满足于只有断路器；
  (38)新因子进入前 MUST 通过因子治理流程(§六十五)——准入/正交化/去重/退役四阶段；
  (39)新功能上线 MUST 通过Feature Flag暗启动(§六十六)——部署≠启用,灰度≠全量；
  (40)Secrets(L4) MUST 有轮替计划(§六十九)——密钥不过期=定时炸弹；
  (41)开发环境 MUST 每日自动验证可重建性(§六十九)——换电脑clone→全量测试全绿,不等到DR演练；
  (42)AI MUST 对每次产出执行自诊断(§六十七)——检测问题→建议修复→Owner确认→可选自动修复；
  (43)跨Session Prompt一致性 MUST 定期验证(§六十八)——同一Prompt+同一任务,不同AI产出同一结果?；
  (44)Owner离线时 MUST 按分级决策树执行(§七十)——不同事故等级×不同离线时长=不同响应,不只是"冻结"。
  (45)Prompt MUST 有版本控制+回归测试(§七十一)——Prompt变更 MUST 经历史任务重放验证,3个以上任务退化→回滚；
  (46)AI 施工 MUST 遵守上下文预算分层(§七十二)——超大型任务(>300K)MUST 拆分;Token>70%时开始裁剪；
  (47)AI 产物 MUST 通过幻觉三级检测(§七十二)——API/库/函数存在性检查🔴阻断,参数签名🟡警告；
  (48)交易相关变更 MUST 经多模型统一共识(§七十三)——2/2同意才通过,分歧达关键级→🛑AI冻结；
  (49)AI 代码 MUST 通过脚手架模板+禁止模式检测(§七十四)——违反 import */裸except/可变默认参数→🔴阻断；
  (50)实盘交易 MUST 过五级Kill Switch+盘前8项检查(§七十五)——8/8☐→GO,<8→🛑NO-GO；
  (51)每交易日 MUST 执行收盘五步自动对账(§七十五)——持仓/成交/费用/PnL归因/审计日志；
  (52)新策略上线 MUST 过五阶段过渡协议(§七十六)——同一时间最多1个策略在过渡中；
  (53)订单执行 MUST 持续监控四维异常+经纪商质量评分(§七十七)——QualityScore<0.6→考虑切换；
  (54)断供因子 MUST 维持在≥2(§七十八)——每次架构变更后自动生成QUICKSTART.md；
  (55)系统 MUST 实现本地优先架构(§七十九)——L1-L2功能全离线可用,恢复后自动同步；
  (56)Owner决策 MUST 按四级分流(§八十)——D3重大决策≤3/天,交易时段零决策窗口；
  (57)上线策略 MUST 过参数灵敏度扫描+MonteCarlo破产概率检查(§八十一)——破产概率>0.01→调整；
  (58)MUST 定期故障注入演练(§八十四)——每周日非交易时段,MTTR恶化>20%→Owner审查；
  (59)宏观体制切换预警 MUST 触发策略权重重校准(§八十五)——3/4信号触发→减仓敏感资产；
  (60)每笔AI交易决策 MUST 附带完整解释链(§八十六)——无解释=无执行；
  (61)新依赖引入前 MUST 检查SBOM+许可证+已知漏洞(§八十七)——重复依赖/高危CVE→拒绝；
  (62)所有状态机 MUST 用统一YAML描述(§八十八)——自动生成转换测试+崩溃后状态协调；
  (63)MUST 追踪DORA四指标+AI接受率(§八十九)——月度速率报告自动生成；
  (64)策略变更 MUST 过A/B实验(§九十)——达统计显著前不能停止,所有实验归档不可删除。
  (65)企业行为 MUST 有独立管线(§九十一)——分红/拆分/并购/退市/代码变更七类不可跳过,无CA Pipeline→回测=不可信；
  (66)盘中故障后 MUST 按热重启六步协议(§九十二)恢复——≤30s;WAL≠经纪商状态→以经纪商为准；
  (67)AI Session 写入文件前 MUST acquire ZephyrLock(§九十三)——TTL 30min,超时自动释放;
  (68)硬件健康 MUST 每日SMART检+温度检+UPS检(§九十四)——任何FAIL→Owner即时通知;
  (69)API废除 MUST 有三阶段生命周期(§九十五)——Active→Deprecated≥90天→Removed,第三方API变更每周检测;
  (70)数据 MUST 自动化Hot→Warm→Cool→Cold→Purge五阶段生命周期(§九十六)——每日03:00 AutoHousekeep;
  (71)系统时钟 MUST 三源NTP偏差监控(§九十七)——delta>1s暂停交易;所有时间戳用ISO8601+时区;
  (72)实时行情 MUST 用Stream轨(§九十八)——WebSocket优先,REST fallback;断流>60s→暂停自动交易;
  (73)静默故障 MUST 聚合评分AFS(§九十九)——AFS≥5减仓+暂停,AFS≥10全冻结;
  (74)AI超50行产出 MUST Chunk级增量审查(§一百)——ACCEPT/REJECT/MODIFY三元态,审查后记录度量;
  (75)回测 Pool MUST Point-in-Time(§一百〇一)——每日成分股快照;退市≠删除;IPO date过滤;
  (76)环境 MUST 幂等可重建(§一百〇二)——setup_windows.ps1可重复运行;Windows Defender排除+自动更新禁止。
tags: [system-master, blueprint, three-tier-pyramid, architecture-topology, level0, ssoT, system-health, cost-architecture, token-budget, data-classification, fault-propagation, startup-shutdown-order, vibe-coding-methodology, fmea, sli-definition, golden-signals, slo-targets, testing-strategy, disaster-recovery, model-risk-management, incident-response, deployment-strategy, compliance-matrix, security-defense-in-depth, session-lifecycle, environment-management, observability-dashboard, performance-baseline, supply-chain-security, data-quality-governance, knowledge-management, migration-strategy, glossary, anti-patterns, offline-autonomy, third-party-dependencies, human-ai-bandwidth, model-drift-monitoring, spof-elimination, vibe-quality-assurance, prompt-library, emergency-runbook, market-data-pipeline, backtesting-framework, order-management-system, risk-controls, quant-ml-engineering, feature-store, regime-change-detection, operational-maturity, alert-fatigue, runbook-automation, ai-code-provenance, agent-debate-protocol, context-recycling, prompt-ab-testing, git-workflow-ai, inter-module-communication, idempotency, circuit-breaker, solo-dev-wellness, burnout-prevention, trade-reconstruction, best-execution, ai-legal-liability, strategy-validation, walk-forward, deflated-sharpe, multiple-testing-correction, execution-algorithms, market-microstructure, portfolio-construction, capacity-management, broker-resilience, emergency-liquidation, reproducibility, deterministic-builds, post-deployment-validation, code-review-depth-model, prompt-lifecycle-management, prompt-regression-testing, context-window-optimization, ai-hallucination-detection, multi-model-consensus, code-generation-standards, project-scaffolding, kill-switch-hierarchy, paper-to-live-transition, order-execution-quality, venue-analysis, knowledge-continuity, bus-factor, local-first-architecture, offline-resilience, decision-fatigue-management, priority-triage, what-if-simulation, sensitivity-analysis, monte-carlo, counterfactual-backtesting, ai-code-archaeology, dead-code-retirement, auto-documentation, sbom-generation, dependency-health, dependency-intelligence, state-machine-formalization, correctness-verification, chaos-engineering, fault-injection, automated-drill, dora-metrics, development-velocity, economic-regime-detection, macro-factor-overlay, ai-explainability, model-card, regulatory-audit, ab-experimentation-framework, statistical-rigor, corporate-actions-pipeline, reference-data-management, warm-restart-protocol, mid-session-recovery, session-concurrency, file-locking, hardware-resilience, infrastructure-failure-modes, api-lifecycle-governance, deprecation-management, data-lifecycle, automated-Housekeeping, time-synchronization, clock-discipline, real-time-streaming, event-driven-architecture, silent-failure-aggregation, cascading-risk-defense, incremental-review, partial-acceptance-protocol, benchmark-integrity, survivorship-bias-defense, cross-environment-consistency, windows-risk-matrix]
priority: P0
depends_on:
  - {target: "PS-STD-005", at: "全篇", why: "蓝图架构标准——定义三级金字塔规范与本蓝图的合法位置"}
  - {target: "MOD-MASTER-001", at: "§一-§十二", why: "12基础设施系统集成蓝图——本蓝图的 Level 1 子蓝图"}
  - {target: "architecture-model/_index.yaml", at: "全篇", why: "架构模型拓扑——C-track 14层 + B-track 12系统"}
---

# ZephyrAlpha 系统总蓝图

> **module_id**: SYS-MASTER-001 | **version**: 0.13.0 | **level**: SYSTEM | **layer**: cross_layer

> **位置**: 三级金字塔 **Level 0 顶点**——定义系统全景拓扑、架构原则与蓝图导航。
> **对标**: TOGAF Architecture Vision Document + K8s Cluster API + C4 System Context Diagram。

---

## 零、AI Agent 冷启动分派

### 0.0 系统健康面板——四黄金信号（11 SLI + SLO 目标值）

> **定位**：每个 AI session 开工前的强制自检视图。任一 SLI 突破 SLO → 记录事故 + 通知 Owner（§0.0.4）。
> **对标**：Google SRE 四黄金信号（Latency / Traffic / Errors / Saturation）+ Grafana Health Dashboard。

| # | 黄金信号 | SLI 指标 | SLO 目标 | 数据源 |
|:--:|------|------|:--:|------|
| 1 | **延迟** | E2E AI 请求延迟 (P50) | <3s | Telemetry (MOD-INF-015) |
| 2 | **延迟** | 蓝图读取耗时 (P95) | <500ms | Context Engine (MOD-INF-008) |
| 3 | **延迟** | 门禁执行总延迟 (P99) | <2s | Gate Engine (MOD-INF-007) |
| 4 | **流量** | AI Session 启动数/天 | ≤20 | SessionContinuity (§二十四) |
| 5 | **流量** | Script 执行吞吐量/min | ≥5 | Script System (MOD-INF-005) |
| 6 | **错误** | Gate 失败率 (G0-G7) | <10% | Gate Engine (MOD-INF-007) |
| 7 | **错误** | Script 执行错误率 | <5% | Script System (MOD-INF-005) |
| 8 | **错误** | 契约漂移检出率 | >95% | Drift Detector (MOD-INF-023) |
| 9 | **饱和度** | Token 预算利用率 | <80% | Budget Enforcer (MOD-INF-024) |
| 10 | **饱和度** | SQLite WAL 深度 | <1000 页 | Database (MOD-INF-012) |
| 11 | **饱和度** | Session 锁争用率 | <5% | Lock Files 协议 (RULE-ZERO) |

### 0.0.4 SLI 突破 SLO 处置流程

```
任一 SLI 突破 SLO (面板红)
  → ① 判断级别: 1 SLI 红=🟡告警 / 3+ SLI 红=🟠降级 / 5+ SLI 红=🔴事故
  → ② 🔴级: 立即通知 Owner + 暂停施工 / 🟠级: 限制施工范围 / 🟡级: 记录日志
  → ③ 写入事故记录 → §二十 事故响应联动
  → ④ 恢复后验证 SLI 全绿 → 继续施工
```

### 0.1 导航链

```
SYS-MASTER-001 (本蓝图, Level 0)
  ├── DOM-GOV-001 (Agent治理八件套集成蓝图, Level 1 域蓝图)
  │     ├── MOD-INF-018~025 (8个治理模块——agent_rbac/agent_spec/audit_trail/rollback/escalation/drift_detector/budget_enforcer/a2a)
  │     ├── G-CT-001~008 (8条跨模块集成契约)
  │     └── governance_server.py (MCP统一入口——8工具)
  ├── MOD-MASTER-001 (12基础设施集成, Level 1)
  │     ├── MOD-INF-001~028 基础设施系统 (29个,详见§1.3)
  │     ├── MOD-INF-013 (MCP Servers, 8 Server + Gateway, stdio协议)
  │     └── MOD-KB-001 知识库 (95%完整)
  └── L00-L13 业务层 (14层, 12蓝图已创建+4实现+12blocked)
```

### 0.2 AI Agent 分派表 (81域)

| 任务域 | 先读 | 再读 | Token预算 |
|--------|------|------|:--:|
| 门禁/断路器 | 本蓝图 §2 | MOD-INF-007 blueprint | ~600 |
| 上下文注入 | 本蓝图 §2 | MOD-INF-008 blueprint | ~500 |
| 任务管线 | 本蓝图 §2 | MOD-INF-009 blueprint | ~500 |
| 反馈闭环 | 本蓝图 §2 | MOD-INF-010 blueprint | ~500 |
| 跨系统集成 | 本蓝图 §1-§3 | MOD-MASTER-001 CT-* | ~2000 |
| 新建模块 | PS-STD-005 §5 | blueprint-template.md | ~800 |
| 权限管控/Agent RBAC | MOD-INF-018 blueprint §1-§2 | rbac_roles.yaml + PermissionGuard API | ~600 |
| 架构审查 | 本文全文 | PS-STD-005 + blueprint-registry.yaml | ~4000 |
| 成本管理/预算 | 本蓝图 §十二 | MOD-INF-024 + §12.3 | ~800 |
| 数据分级/安全 | 本蓝图 §十三 | MOD-INF-014 + §13.3 | ~600 |
| 启动/运维 | 本蓝图 §十四 | MOD-INF-012 + §14.1 | ~500 |
| 施工方法论 | 本蓝图 §十五 | §15.1 + §15.2 | ~400 |
| 测试/质量保障 | 本蓝图 §十七 | MOD-INF-005 + §17.1 | ~800 |
| 灾难恢复 | 本蓝图 §十八 | MOD-INF-001 + §18.3 | ~600 |
| 模型风险管理 | 本蓝图 §十九 | MOD-INF-010 + SR11-7 | ~700 |
| 事故响应 | 本蓝图 §二十 | MOD-INF-022 + §20.3 | ~600 |
| 部署/发布 | 本蓝图 §二十一 | MOD-INF-009 + §21.1 | ~500 |
| 合规审查 | 本蓝图 §二十二 | MOD-INF-020 + §22.2 | ~700 |
| 安全纵深防御 | 本蓝图 §二十三 | MOD-INF-014 + §23.1 | ~600 |
| Session生命周期 | 本蓝图 §二十四 | SessionContinuity (project_rules.md STEP 3) | ~400 |
| 环境管理 | 本蓝图 §二十五 | IDE隔离 + 快捷键 | ~300 |
| 可观测性/仪表板 | 本蓝图 §二十六 | MOD-INF-015 + §0.0 | ~400 |
| 性能基线 | 本蓝图 §二十七 | MOD-INF-011 + §27.1 | ~400 |
| 供应链安全 | 本蓝图 §二十八 | pip-lock + audit | ~300 |
| 数据质量治理 | 本蓝图 §二十九 | MOD-INF-012 + §13 | ~400 |
| 知识管理 | 本蓝图 §三十 | MOD-KB-001 + AUTO-KB(§67) | ~400 |
| 迁移策略 | 本蓝图 §三十一 | MOD-INF-021 + §21 | ~300 |
| 术语/反模式 | 本蓝图 §三十二 + §三十三 | §15.2 + AGENTS.md | ~300 |
| Owner离线自治 | 本蓝图 §三十四 | §七十 分级决策 | ~400 |
| 第三方依赖 | 本蓝图 §三十五 | MOD-INF-024 + §28 | ~300 |
| 人机带宽 | 本蓝图 §三十六 | §十五 + §62 交易HCI | ~400 |
| 模型漂移监控 | 本蓝图 §三十七 | §六十 SPC + §42 ML | ~400 |
| SPOF消除 | 本蓝图 §三十八 | §1.3 + §45.1 | ~300 |
| 氛围编程质量 | 本蓝图 §三十九 | §六十 SPC + §15 | ~400 |
| 市场数据管线 | 本蓝图 §四十 | MOD-INF-012 + §29 | ~600 |
| 回测引擎 | 本蓝图 §四十 | MOD-INF-010 + §19 | ~700 |
| 订单执行/风控 | 本蓝图 §四十一 | MOD-INF-005 + §19 | ~600 |
| 量化ML工程 | 本蓝图 §四十二 | MOD-INF-011 + §27 | ~700 |
| 运维成熟度 | 本蓝图 §四十三 | MOD-INF-001 + §0.0 | ~500 |
| 氛围编程深层 | 本蓝图 §四十四 | §15.5 + MOD-INF-019 | ~600 |
| Agent Spec / Skill系统 | MOD-INF-019 blueprint §1-§2 | skill_registry.yaml → `progressive_load(skill_id)` | ~600 |
| Agent治理/八件套集成 | DOM-GOV-001 blueprint §1-§3 | 8模块G-CT-001~008八条跨模块契约 + governance_server.py MCP入口 | ~800 |
| 架构基础契约 | 本蓝图 §四十五 | MOD-MASTER-001 + §4.1 | ~600 |
| 1人运营保障 | 本蓝图 §四十六 | §三十六 + §三十四 | ~400 |
| 金融合规法律 | 本蓝图 §四十七 | §二十二 + §十九 | ~500 |
| 策略验证/统计 | 本蓝图 §四十八 | §四十二 + §十九 | ~600 |
| 执行算法/微结构 | 本蓝图 §四十九 | §四十一 + §四十 | ~500 |
| 多策略/容量管理 | 本蓝图 §五十 | §四十八 + §十九 | ~500 |
| 经纪商容灾 | 本蓝图 §五十一 | §三十五 + §十八 | ~400 |
| 可重现性保障 | 本蓝图 §五十二 | §二十八 + §四十五 | ~400 |
| 实盘后验证 | 本蓝图 §五十三 | §二十一 + §三十九 | ~400 |
| AI代码审查深度 | 本蓝图 §五十四 | §十五 + §四十四 | ~500 |
| 组合级风险管理 | 本蓝图 §五十五 | §五十 + §十九 | ~500 |
| 波动率目标/杠杆 | 本蓝图 §五十六 | §五十 + §四十一 | ~400 |
| 因子择时/跨资产 | 本蓝图 §五十七 | §四十二 + §四十八 | ~400 |
| 交易日历/合约 | 本蓝图 §五十八 | §四十 + §五十一 | ~300 |
| 运维基础保障 | 本蓝图 §五十九 | §十八 + §四十三 | ~400 |
| AI质量SPC | 本蓝图 §六十 | §三十九 + §三十七 | ~400 |
| PnL归因/TCA | 本蓝图 §六十一 | §五十 + L07 | ~500 |
| 日运营节奏/交易HCI | 本蓝图 §六十二 | §五十八 + §三十四 | ~500 |
| 系统容错模式 | 本蓝图 §六十三 | §四十五 + §二十一 | ~400 |
| 微结构防御/模拟保真度 | 本蓝图 §六十四 | §四十九 + §四十一 | ~400 |
| 因子治理/生命周期 | 本蓝图 §六十五 | §四十八 + §五十 | ~400 |
| 功能开关/部署安全网 | 本蓝图 §六十六 | §二十一 + §五十三 | ~400 |
| AI自诊断/知识自动化 | 本蓝图 §六十七 | §六十 + §三十 | ~400 |
| 氛围编程确定性保障 | 本蓝图 §六十八 | §五十二 + §四十四 | ~400 |
| Secrets生命周期/环境可重建 | 本蓝图 §六十九 | §十三 + §十八 | ~400 |
| 离线分级应急/全生命周期预算 | 本蓝图 §七十 | §三十四 + §四十八 | ~400 |
| Prompt工程/生命周期 | 本蓝图 §七十一 | §十五 + §四十四 + .zeph/prompts/ | ~400 |
| 上下文窗口/幻觉防御 | 本蓝图 §七十二 | §十二 + §六十七 | ~400 |
| 多模型共识/辩论协议 | 本蓝图 §七十三 | §四十四 + §五十四 | ~400 |
| 代码生成标准/脚手架 | 本蓝图 §七十四 | §十五 + §三十三 | ~300 |
| Kill Switch/安全保障 | 本蓝图 §七十五 | §二十 + §六十六 + §四十一 | ~500 |
| 模拟→实盘过渡 | 本蓝图 §七十六 | §五十三 + §六十四 + §五十六 | ~400 |
| 订单执行质量/异常检测 | 本蓝图 §七十七 | §四十一 + §六十一 + §六十四 | ~400 |
| 知识连续性/断供因子 | 本蓝图 §七十八 | §三十 + §六十七 + §四十六 | ~400 |
| 本地优先/离线运行 | 本蓝图 §七十九 | §二十五 + §三十四 + §七十 | ~300 |
| 决策疲劳/优先级分流 | 本蓝图 §八十 | §三十六 + §四十六 + §六十二 | ~400 |
| What-If仿真/灵敏度 | 本蓝图 §八十一 | §四十 + §五十五 + §四十二 | ~400 |
| 代码考古/文档自动化 | 本蓝图 §八十二 | §三十 + §五十二 + §三十一 | ~300 |
| 数据源可靠性/智能切换 | 本蓝图 §八十三 | §二十九 + §三十五 + §四十 | ~400 |
| 混沌工程/故障演练 | 本蓝图 §八十四 | §十八 + §六十三 + §十六 | ~400 |
| 经济体制/宏观覆盖 | 本蓝图 §八十五 | §四十二 + §五十七 + §五十五 | ~400 |
| AI可解释性/监管审计 | 本蓝图 §八十六 | §四十七 + §二十二 + §十九 | ~400 |
| SBOM/依赖情报 | 本蓝图 §八十七 | §二十八 + §三十五 + §六十九 | ~300 |
| 状态机形式化/验证 | 本蓝图 §八十八 | §四十一 + §四十五 + §六十六 | ~300 |
| DORA指标/开发速率 | 本蓝图 §八十九 | §三十九 + §六十 + §四十四 | ~300 |
| A/B实验框架 | 本蓝图 §九十 | §四十八 + L13 + §五十三 | ~400 |
| 企业行为/参考数据 | 本蓝图 §九十一 | §四十 + §六十五 + §四十二 | ~500 |
| 热重启/盘中恢复 | 本蓝图 §九十二 | §十四 + §八十八 + §六十三 | ~500 |
| 会话并发/文件完整性 | 本蓝图 §九十三 | §二十五 + §二十四 + §六十八 | ~400 |
| 硬件容灾/基础设施 | 本蓝图 §九十四 | §十六 + §六十三 + §七十 | ~400 |
| API生命周期/弃用 | 本蓝图 §九十五 | §四十五 + §八十七 + §三十五 | ~400 |
| 数据生命周期/清理 | 本蓝图 §九十六 | §五十九 + §八十二 + §八十三 | ~300 |
| 时间同步/时钟纪律 | 本蓝图 §九十七 | §七十五 + §五十二 + §四十五 | ~300 |
| 流式数据架构 | 本蓝图 §九十八 | §四十 + §八十三 + §四十一 | ~400 |
| 静默故障聚合/级联风险 | 本蓝图 §九十九 | §四十三 + §六十三 + §十六 | ~400 |
| 增量审查/部分接受 | 本蓝图 §一百 | §三十九 + §八十 + §五十四 | ~400 |
| 基准完整性/生存偏差 | 本蓝图 §一百〇一 | §四十八 + §九十一 + §四十二 | ~500 |
| 跨环境一致性/Windows风险 | 本蓝图 §一百〇二 | §二十五 + §六十九 + §五十二 | ~400 |
| MCP协议服务端/外部系统暴露 | MOD-INF-013 blueprint §1-§4 | tool_contracts.yaml + mcp-specialist skill | ~600 |
| 红白对抗验证/安全纵深 | MOD-INF-030 blueprint §1-§7 | _scenario_registry.yaml + _constitution_registry.yaml + red-blue-adversarial skill | ~800 |

### 0.3 令牌预算层级

| 层级 | 文档 | 首次读取Token | 触发条件 |
|------|------|:--:|------|
| 🔥 Hot Memory | AGENTS.md + 本蓝图 §0 | ~800 | 每个session |
| 📋 Domain Triggers | 对应模块蓝图 §1-§5 | ~2000 | path_pattern匹配 |
| 📚 Cold Memory | 模块蓝图全文 + MOD-MASTER-001 | ~8000 | 主动查询 |

---

## 一、系统全景拓扑

### 1.1 双轨架构

| 轨 | 计数 | 状态 | 职责 |
|:--|:--:|------|------|
| **C-Track** (业务层) | 14层 | 4实现/9骨架/1占位 | 量化交易业务——因子、信号、风控、执行 |
| **B-Track** (基础设施) | 12系统 | 12实现 | AI开发骨架——门禁、上下文、管线、反馈 |

### 1.2 C-Track 业务层（14层: 12蓝图已创建/9骨架/4实现/1占位）

| 层 | 名称 | 蓝图ID | 代码状态 | 说明 |
|:--|------|------|:--:|------|
| L00 | Data Source | MOD-L00-001 | skeleton | 外部数据摄取 — 蓝图已创建,blocked |
| L01 | Infrastructure | — | implemented | B轨基础设施层 — 已合并到B-Track |
| L02 | Alpha Factor | MOD-L02-001 | implemented | 因子计算引擎 — 蓝图已创建,blocked |
| L03 | Signal Generation | MOD-L03-001 | skeleton | 信号融合打分 — 蓝图已创建,blocked |
| L04 | Risk Management | MOD-L04-001 | implemented | 风控止损 — 蓝图已创建,blocked |
| L05 | Portfolio Construction | MOD-L05-001 | skeleton | 仓位分配 — 蓝图已创建,blocked |
| L06 | Trade Execution | MOD-L06-001 | skeleton | 订单路由 — 蓝图已创建,blocked |
| L07 | Post-Trade Analytics | MOD-L07-001 | skeleton | PnL归因 — 蓝图已创建,blocked |
| L08 | Human-AI Interface | MOD-L08-001 | implemented | Dashboard — 蓝图已创建,blocked |
| L09 | Research & Innovation | MOD-L09-001 | skeleton | 回测孵化 — 蓝图已创建,blocked |
| L10 | Compliance | MOD-L10-001 | skeleton | 合规校验 — 蓝图已创建,blocked |
| L11 | ML Platform | MOD-L11-001 | skeleton | ML生命周期 — 蓝图已创建,blocked |
| L12 | System Telemetry | — | implemented | 全系统遥测 — 已合并到B-Track |
| L13 | Experimentation | MOD-L13-001 | skeleton | A/B实验 — 蓝图已创建,blocked |

### 1.3 B-Track 基础设施层

| 系统 | 蓝图ID | 蓝图完整度 | 核心职责 |
|------|------|:--:|------|
| Capacity Assurance | MOD-INF-001 | 95% | 容量监控/SLI/SLO目标 |
| Runtime Integration | MOD-INF-002 | 95% | 跨层集成与缺口填补 |
| Script System | MOD-INF-005 | 95% | 脚本发现/执行/验证 |
| Task System | MOD-INF-006 | 95% | 任务卡全生命周期 |
| Gate Engine | MOD-INF-007 | 35% | G0-G7门禁+断路器 |
| Context Engine | MOD-INF-008 | 95% | 上下文四阶段流水线 |
| Pipeline | MOD-INF-009 | 95% | M1-M11双管线 |
| Feedback Loop | MOD-INF-010 | 95% | 系统自调节闭环 |
| Vector Memory | MOD-INF-011 | 95% | 向量化存储检索 |
| Database | MOD-INF-012 | 95% | SQLite+DuckDB双引擎元数据 |
| MCP Servers | MOD-INF-013 | 95% | MCP协议服务端 |
| LLM Security | MOD-INF-014 | 95% | L0-L8九层纵深防御 |
| System Telemetry | MOD-INF-015 | 95% | 全系统遥测采集 |
| Shared Core | MOD-INF-016 | **100%** | 跨层共享基础设施 |
| Code Dedup Engine | MOD-INF-017 | 95% | Monoculture免疫+全生命周期去重 |
| Agent RBAC | MOD-INF-018 | 95% | 七层纵深RBAC |
| Agent Spec | MOD-INF-019 | 95% | 蓝图→Skill升级引擎 |
| Audit Trail | MOD-INF-020 | 95% | 不可变动作审计+Provenance链 |
| Rollback System | MOD-INF-021 | **100%** | Git-native回滚/撤销 |
| Escalation Protocol | MOD-INF-022 | 35% | 规则驱动升级+自动委托 |
| Drift Detector | MOD-INF-023 | **100%** | Git-native漂移检测+对账 |
| Budget Enforcer | MOD-INF-024 | 35% | Token/Cost/Time三维预算执行 |
| A2A Protocol | MOD-INF-025 | 35% | Agent间通信+冲突解决 |
| Asset Inventory | MOD-INF-026 | 5% | 全量资产发现+统一登记 |
| Knowledge Base | MOD-KB-001 | 95% | 知识生命周期管理 |
| Audit Orchestrator | MOD-INF-027 | 0% | 全域审计调度编排 |
| Semantic Auditor | MOD-INF-028 | 0% | 语义级审计校验 |

### 1.4 运行时平面（正交视图）

| 平面 | 覆盖系统 | 职责 |
|------|------|------|
| 任务执行平面 | Orc + Pipeline + Script System | 任务调度执行 |
| 知识平面 | KB + VMS + Context Engine | 记忆检索注入 |
| 安全平面 | Gate Engine + LSG + Sandbox | 门禁校验沙箱 |
| 反馈平面 | Feedback Loop + Telemetry | 自调节监控 |
| 数据平面 | Database + Shared/Contracts | 持久化契约 |

---

## 二、架构原则

### 2.1 不可变核心

| 原则 | 陈述 | 来源 |
|------|------|------|
| P1: SSoT | 每个架构事实只有一个 canonical source | ADR-0001 |
| P2: YAML Schema | 结构化数据用YAML+JSON Schema，不用MD | ADR-0002 |
| P3: Dual AI | Writer+Reviewer双角色协作 | ADR-0003 |
| P4: OCP | 通过抽象基类扩展，不修改现有代码 | ADR-0004 |
| P5: Blueprint First | 任何代码变更前必须读对应蓝图（G6强制） | G6 |

### 2.2 蓝图体系铁律

| # | 铁律 | 执行者 |
|:--|------|------|
| 1 | 三级金字塔不可扁平化——Level 0/1/2 职责分明 | PS-STD-005 |
| 2 | belongs_to 必填——每个模块蓝图必须声明归属 | PS-STD-005 §5 |
| 3 | 蓝图与代码双向对齐——GATE-A (代码↔YAML) + GATE-B (YAML↔MD) | AGENTS.md §6.10 |
| 4 | G6 硬合规——AI 未读蓝图则代码变更 REJECT | g6_blueprint_compliance.yaml |
| 5 | blueprint_routing.yaml 是路由 SSoT——新模块必须登记 | MOD-INF-009 §8 |

---

## 三、关键架构决策索引

| ADR | 标题 | 决策 |
|------|------|------|
| ADR-0001 | Canonical SSoT | YAML=真源, MD=衍生视图 |
| ADR-0002 | 单Schema Phased Required Fields | 一个JSON Schema渐进式必填 |
| ADR-0003 | Dual AI Collaboration | Writer/Reviewer双角色 |
| ADR-0004 | OCP Extension Points | 开闭原则扩展点 |
| ADR-0015 | Context Engine | 四阶段流水线 |
| ADR-0016 | Vector Memory | ChromaDB+BGE-M3 |
| ADR-0017 | Agent Orchestrator | SQLite+asyncio |
| ADR-0018 | Agent Sandbox | Windows ACL |
| ADR-0019 | Feedback Loop | 三阶段闭环 |
| ADR-0020 | LLM Security | 四层防御 |
| R90 | 三级金字塔 | 本蓝图的架构基础 |

---

## 四、跨模块数据流

```
用户意图 → IntentParser → TriggerRouter → Orchestrator
  → ContextEngine(构建上下文) → GateEngine(G6检查→G1-G5门禁)
  → Pipeline(分配M1-M11) → ScriptSystem(执行脚本)
  → FeedbackLoop(收集结果) → VectorMemory(记忆更新)
  → Telemetry(遥测记录)
```

**关键集成点**:
- G6 gate 在 Pipeline 分配前运行——确保 AI 已读蓝图
- Context Engine 通过 `blueprint_routing.yaml` 确定上下文范围
- Feedback Loop 触发 AutoEvolution 调整蓝图索引权重

---

## 五、依赖关系

| 本蓝图依赖 | 关系 | 为什么 |
|------|:--:|------|
| PS-STD-005 | governs | 定义本蓝图的合法位置 |
| MOD-MASTER-001 | delegates_to | 12系统集成契约 |
| architecture-model/_index.yaml | reads_from | 拓扑数据 |
| blueprint-registry.yaml | monitors | 蓝图健康度 |

---

## 六、产出物存放目录

| 产出物 | 路径 |
|------|------|
| 本蓝图 | `docs/03_modules/_sys-master/blueprint.md` |
| 集成蓝图 | `docs/03_modules/_master-blueprint/blueprint.md` |
| 全部模块蓝图 | `docs/03_modules/l01_infrastructure/*/blueprint.md` + `_cross_layer/*/blueprint.md` |
| 架构标准 | `docs/01_policies_and_standards/meta/blueprint-architecture-standard.md` |
| 架构模型 | `architecture-model/layers/*.yaml` |
| 业务层代码 | `src/zephyr/l00_data_source/` ~ `l13_experimentation/` |
| 基础设施代码 | `src/zephyr/gates/`, `src/zephyr/context_engine/`, ... |
| 门禁定义 | `src/zephyr/gates/*.yaml` |

---

## 七、集成目标

| 目标 | 状态 | Phase |
|------|:--:|:--:|
| 三级金字塔全部就位 | SYS-MASTER-001 已创建，44模块完整登记 | beta ✓ |
| 蓝图完整度 ≥80% | 当前 **84.2%** (44模块均值) — **已达标** ✓ | beta ✓ |
| G6 硬合规 REJECT <10% | 当前 33.3% | beta-stable |
| C-Track 业务蓝图 (L00-L13) | 12/14 已创建 (L01/L12合并到B-Track，全blocked) | stable+ |
| Domain Expert Agent | Gate/Context/Pipeline 3个 | beta |

---

## 八、需要更新的相关内容

当本文变更时，同步更新：
1. `docs/03_modules/blueprint-registry.yaml` —— 新增 SYS-MASTER-001 登记行
2. `docs/01_policies_and_standards/meta/blueprint-architecture-standard.md` —— 若 Level 0 定义调整
3. `architecture-rationale-log.md` —— 追加 beta 相关决策

---

## 九、已知风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| SYS-MASTER → MOD-MASTER → 模块蓝图 三层不一致 | AI 读错蓝图 | GATE-A + GATE-B 对齐检查 |
| 本蓝图过长导致 AI 不读 | 冷启动失败 | §0 分派表 + 按需阅读设计 |
| C-Track 业务蓝图缺失 | 业务开发缺指引 | stable 创建 L02/L04/L08/L12 |
| SYS-MASTER 与 MOD-MASTER 边界模糊 | 契约重复定义 | 铁律：SYS-MASTER 定义"谁有什么"，MOD-MASTER 定义"之间怎么连" |

---

## 十、后果

- AI agent 现在有明确的 Level 0 入口——冷启动不再迷茫
- 蓝图冲突有明确裁决链——不再需要猜测谁的优先级更高
- C-Track 业务蓝图缺失被显式记录——可追踪的技术债务
- 三级金字塔从"只有概念"变成"有代码/文档载体"——PS-STD-005 的设计得到完整实现

---

## 十一、施工指引

| 步骤 | 说明 | Phase |
|------|------|:--:|
| 1 | 在 blueprint-registry.yaml 中登记 SYS-MASTER-001 | beta |
| 2 | 补齐所有 70 章蓝图中的 skeleton→骨架 | beta |
| 3 | 为 Gate/Context/Pipeline 创建 domain-expert agent spec | beta |
| 4 | 运行 beta 30 session 验证 | beta |
| 5 | 创建 C-Track 业务蓝图 | stable |
| 6 | 按氛围编程方法论 (§十五) 施工——门禁链不跳步 | 持续 |

---

## 十二、成本架构与Token预算

> **定位**：AI 大规模施工的核心约束不是代码质量——是 Token 成本。无预算 = 无法施工。本节定义 7 模型价格基准 + Session 成本估算 + 成本-质量路由矩阵 + TCO 模型。
> **对标**：K8s ResourceQuota + AWS Cost Explorer + FinOps。

### 12.1 模型价格基准 (per 1M token)

| 模型 | 输入价格 | 输出价格 | 适用场景 |
|------|:--:|:--:|------|
| DeepSeek-V3 | free | free | 默认主力——所有日常施工 |
| Claude Sonnet 4 | $3.00 | $15.00 | 架构决策/安全审计/复杂代码审查 |
| GPT-4o-mini | $0.15 | $0.60 | 批量、简单、重复任务 |
| DeepSeek-R1 | $0.14 | $2.19 | 深度推理、策略设计 |
| Claude Opus 4 | $15.00 | $75.00 | 极少用——关键ADR/终极审查 |

### 12.2 Session 成本估算

| 任务强度 | 典型 Token | 成本 (DS-V3为主) | 成本 (Claude Sonnet混合) |
|------|:--:|:--:|:--:|
| Light (<50K tokens) | 40K | ~$0.00 | ~$0.50 |
| Medium (50-150K) | 100K | ~$0.00 | ~$1.50 |
| Heavy (150-500K) | 300K | ~$0.00 | ~$5.00 |

### 12.3 成本-质量路由矩阵

| 任务 | 默认模型 | 备用 | 触发升级条件 |
|------|------|------|------|
| 简单 CRUD | DeepSeek-V3 | — | — |
| 算法实现 | DeepSeek-V3 | R1 | 复杂度 > 100行 |
| 架构设计 | Claude Sonnet 4 | Opus 4 | 影响 > 3模块 |
| 安全审计 | Claude Sonnet 4 | — | — |
| 代码审查 | DeepSeek-V3 | Claude Sonnet 4 | 逻辑复杂度 > 中 |
| Prompt 优化 | Claude Sonnet 4 | — | — |
| Bug 修复 | DeepSeek-V3 | R1 | 3轮未修复 |

### 12.4 TCO 月度模型

| 成本项 | 月估算 | 占比 |
|------|:--:|:--:|
| API Token | $50–200 | 50–70% |
| 数据源 | $0–50 | 0–20% |
| 经纪商费用 | $0–30 | 0–10% |
| 电力/硬件折旧 | $5–15 | 5% |

---

## 十三、数据分类分级

> **定位**：系统处理多种数据——从公开行情到密钥。必须分级控制访问和泄露响应。
> **对标**：NIST SP 800-60 + AWS Data Classification + ISO 27001 A.8.2。

| 级别 | 描述 | 示例 | 访问控制 | 泄露响应 |
|:--:|------|------|------|------|
| L1 公开 | 公开可获取 | 历史行情、技术指标 | 无限制 | 无需响应 |
| L2 内部 | 系统运行数据 | 策略参数、回测结果 | Owner+AI | 内部审查 |
| L3 敏感 | 交易核心 | 信号、持仓、订单流 | Owner+Supervisor AI | 事故响应(§20) |
| L4 密钥 | 凭证/证书 | API Key、Token、密码 | Owner only | 即时轮替+吊销(§69) |

---

## 十四、系统启动/停止顺序

> **定位**：跨 12+进程的启动顺序和故障时的安全关机。乱序启动=数据竞争/死锁/不一致。
> **对标**：K8s Init Containers + systemd unit ordering。

### 14.1 启动拓扑 (6 Phase)

| Phase | 组件 | 依赖 | 超时 |
|:--:|------|------|:--:|
| P1 | Database (sqlite), Secrets | 无 | 5s |
| P2 | Context Engine, Gate Engine | P1 | 10s |
| P3 | Market Data Pipeline | P1 | 30s |
| P4 | Factor Engine, Signal Generator | P3 | 60s |
| P5 | OMS, Risk Controller | P4 | 30s |
| P6 | Dashboard, Telemetry | P5 | 10s |

### 14.2 安全关机 (逆序)

```
stop信号:  P6→P5→P4→P3→P2→P1 (每步10s grace, 总≤60s)
强制关机:  P6→P1 同时 kill ——保存pending状态到wal
```

---

## 十五、氛围编程施工方法论

> **定位**：100% AI 施工的核心方法——MUST/SHOULD/MAY 三级指令体系 + 词汇对齐 + Prompt Library。
> **对标**：Cursor Rules + Claude Code Instructions + Continue.dev Config。

### 15.1 三级指令体系

| Level | 标记 | 含义 | 违规后果 |
|:--:|------|------|------|
| MUST | `MUST` | 强制性——任何时候不可跳过 | 阻断门禁→施工不通过 |
| SHOULD | `SHOULD` | 强烈建议——需有充分理由才能跳过 | 写入决策日志 |
| MAY | `MAY` | 可选——AI自主判断 | 无后果 |

### 15.2 蓝图中文数字对照

| 写法 | 含义 | AI 映射 |
|------|------|------|
| §0 | 第零节 | section-0 |
| §0.0 | 第零节零子节 | section-0.0 |
| §十二 | 第十二节 | section-12 |

### 15.3 核心施工命令

| 命令 | 含义 |
|------|------|
| `<EXPLORE>` | AI 先探索代码库→不写代码→报告发现 |
| `<PLAN>` | AI 制定施工计划→不写代码 |
| `<BUILD>` | AI 按计划施工→写代码+测试+门禁 |
| `<REVIEW>` | Owner 审查|
| `<ACCEPT>` | Owner 确认 |
| `<REVERT>` | 回滚到变更前 |

### 15.4 Prompt Library

| Prompt ID | 用途 | Token预算 |
|------|------|:--:|
| P-FACTOR-NEW | 创建新因子 | ~2000 |
| P-STRATEGY-VALIDATE | 验证策略统计 | ~3000 |
| P-ARCH-REVIEW | 架构审查 | ~4000 |
| P-BUG-DIAGNOSE | Bug 诊断 | ~1500 |
| P-REFACTOR-PROPOSE | 重构建议 | ~2000 |

---

## 十六、FMEA 故障模式分析

> **定位**：预判系统"哪里最可能出错"→优先加固。
> **对标**：NASA FMEA + Google SRE Risk Analysis。

| ID | 故障模式 | 影响 | 检测方法 |
|------|------|------|------|
| F1 | 行情数据延迟>5s | 信号过期→错误交易 | 心跳超时检测 |
| F2 | 信号计算异常(WAL损坏) | 信号=噪声→随机交易 | 信号分布监控(§37) |
| F3 | 订单重复提交 | 错误加倍→损失×2 | 订单ID去重+幂等(§45) |
| F4 | 风控模块SQLite锁 | 止损不生效 | Health Panel(§0.0) |
| F5 | API 密钥过期 | 系统离线 | Secrets轮替日历(§69) |
| F6 | 喂入未来的数据(Look-ahead) | 回测虚高→实盘崩溃 | 逐日验证(§42.3) |
| F7 | 经纪商API 不可达 | 无法下单/撤单 | Heartbeat+Circuit Breaker |
| F8 | 灾难性遗忘(session断裂) | AI不知道过去决策 | §0分派表+SessionContinuity |

---

## 十七、测试策略

> **定位**：AI 生成的代码→必须有测试验证。测试金字塔：单元(70%)→集成(20%)→E2E(10%)。

| 层级 | 占比 | 工具 | 门禁要求 |
|------|:--:|------|------|
| 单元测试 | 70% | pytest | coverage≥80%, 全pass |
| 集成测试 | 20% | pytest | 跨模块关键路径全绿 |
| E2E测试 | 10% | 手动+脚本 | beta稳定后上线 |

---

## 十八、灾难恢复

> **定位**：系统故障→恢复能力。季度 DR 演练 + 每日可重建性验证。
> **对标**：AWS Well-Architected Reliability Pillar + Google SRE Ch.8。

| RPO/RTO | 目标 | 实现 |
|------|:--:|------|
| RPO (数据丢失窗口) | ≤1小时 | sqlite WAL + 备份(§59) |
| RTO (恢复时间) | ≤30分钟 | 启动拓扑(§14) + 回滚(§21) |

---

## 十九、模型风险管理

> **定位**：策略上线前的风险清单 (MR101-MR113)——OWASP LLM Top 10 + SR 11-7。
> **对标**：Fed SR 11-7 + OCC Model Risk Management。

关键检查项：数据泄漏、过拟合、市场状态偏差、幸存者偏差、样本外衰减、滑点模型准确度。

---

## 二十、事故响应

> **定位**：事故分级 L1-L5 + 升级矩阵 + Telemetry 告警联动。

| 等级 | 描述 | 响应时间 | 升级条件 |
|:--:|------|:--:|------|
| L1 | 瞬时故障 | <5min 自愈 | 3次/天升级L2 |
| L2 | 持续降级 | <30min | 影响PnL升级L3 |
| L3 | 部分功能丧失 | <2h | Owner离线升级L4 |
| L4 | 全系统故障 | <8h | >24h升级L5 |
| L5 | 灾难级 | — | 通知备用联系人 |

---

## 二十一、部署策略

> **定位**：Canary→G0-G7门禁→渐进式→自动回滚窗口(1h)。

```
部署管线:
  Build → Unit Test → Gate G0-G7 → Canary(1h) → 渐进(10%→50%→100%) 
  任一阶段失败→自动回滚(old commit)
```

---

## 二十二、合规映射

> **定位**：交易系统的监管要求——MiFID II Art.17(交易报告)、SEC Rule 613(审计追踪)、SR 11-7(模型风险)、GDPR(数据保护)。

---

## 二十三、安全纵深防御

> **定位**：L1-L6 六层防御——每层失败即阻断。

| 层 | 防御 | 工具 |
|:--:|------|------|
| L1 | 依赖审计 | pip-audit |
| L2 | 静态分析 | ruff + bandit |
| L3 | 沙箱隔离 | Docker/process isolation |
| L4 | Secrets | git-crypt + 1Password |
| L5 | 审计追踪 | MOD-INF-020 immutable log |
| L6 | 断路器 | Circuit Breaker (§45.4) |

---

## 二十四、Session 生命周期

> **定位**：每次 Session 从 Handover 读取→产出→Handover 写入的闭环。Lamport 时钟保证因果顺序。

---

## 二十五、环境管理

> **定位**：Supervisor-only 指令、IDE 之间隔离、全局快捷键——避免多IDE罢工。

| 规则 | 说明 |
|------|------|
| 全局指令 | Supervisor 广播到所有 IDE |
| 本地指令 | 每个IDE独立session |
| 快捷键 | `<C-s>`冻结所有IDE |
| IDE隔离 | 同一项目的多个IDE →不同session ID |

---

## 二十六、可观测性仪表板

> **定位**：系统运行状态的单一视图——集成本蓝图的 §0.0 健康面板。
> **对标**：Grafana + Prometheus + Google SRE Monitoring。

### 26.1 核心面板配置

| 面板 | 数据源 | 刷新率 | 告警 |
|------|------|:--:|------|
| 系统健康 (11 SLI) | MOD-INF-015 Telemetry | 10s | SLI>SLO |
| 成本仪表板 | Token Counter + Data APIs | 1h | 超预算20% |
| 订单流 | OMS (MOD-INF-005) | 实时 | 异常模式 |
| 模型漂移 | Drift Monitor (§37) | 1h | >阈值 |

---

## 二十七、性能基线

> **定位**：量化系统的性能度量——不只是快，是可靠。
> **对标**：Hudson River Trading E2E Latency SLA + K8s Resource Requests/Limits。

| 指标 | 目标 | P99上限 |
|------|:--:|:--:|
| 行情接收→信号 | <200ms | <500ms |
| 信号→风控判断 | <10ms | <50ms |
| 风控→订单发出 | <50ms | <200ms |
| E2E Total | <500ms | <1000ms |

---

## 二十八、供应链安全

> **定位**：所有第三方依赖——pip, npm, 数据API——的安全审计。
> **对标**：OWASP Top 10 + GitHub Dependabot + pip-audit。

```
依赖安全: pip-audit 每次 deploy 前——任何已知 CVE > 阻断
依赖锁定: requirements.locked.txt (commit), 不在安装时解析numpy版本
```

---

## 二十九、数据质量治理

> **定位**：脏数据 = 脏信号 = 脏交易。数据质量门控在管线入口。
> **对标**：dbt + Great Expectations + data quality SLA。

| 检查 | 方法 | 频率 |
|------|------|:--:|
| 完整性 | 缺行数 / 预期行数 < 0.1% | 每次入库 |
| 及时性 | 预期时间 ± 5min | 每次数据拉取 |
| 有效性 | 价/量 > 0 + 无 NaN | 每次解析 |
| 一致性 | 同一证券, 多源数据 agree | 每日交叉验证 |

---

## 三十、知识管理

> **定位**：从 Owner 脑内 → 结构化知识 → 自动提取。不等 Owner"有时间写"。
> **对标**：Obsidian PKM + MOD-KB-001 + AUTO-KB(§67)。

```
知识源: Owner决策 → Session Handover → 自动提取 → KB entries
知识槽: 未结构化的决策 —— Owner 待补充
```

---

## 三十一、迁移策略

> **定位**：系统演化时——数据迁移、API 迁移、平台迁移。
> **对标**：AWS Migration Hub + 12-Factor App Backing Services。

```
迁移原则: 所有迁移有 recoverable script → no data loss
```

---

## 三十二、术语表

> **定位**：消除 AI 歧义——统一中文/英文术语。
> **对标**：Ubiquitous Language (DDD)。

| 中文 | 英文 | 定义 |
|------|------|------|
| 因子 | Factor | 从市场数据提取的 Alpha 信号前身 |
| 信号 | Signal | 因子组合后的可执行信号 |
| 滑点 | Slippage | 决策价格 vs 执行价格之差 |
| 冲击成本 | Market Impact | 本交易本身引起的价格移动 |

---

## 三十三、反模式目录

> **定位**：AI 施工最容易犯的错——预录好→预防。
> **对标**：Google SRE Anti-Patterns + Cursor Rules Best Practices。

| 反模式 | 问题 | 正确做法 |
|------|------|------|
| 无测试 AI 产出 | 代码不可靠、不可维护 | 强制测试pytest覆盖(§17) |
| 长时间 session | 上下文溢出、幻觉 | 每~1h检查(§24) |
| 不读蓝图直接写代码 | 与架构冲突 | 先Read §0分派表(§0) |

---

## 三十四、Owner 离线自治

> **定位**：Owner 不在时系统仍能运转——不赌"刚好在线"。
> **对标**：Google SRE Unattended Ops + 分级决策树(§70)。

| 模式 | Owner在线 | Owner离线 |
|------|:--:|------|
| 全自动 | 信号→执行 | 🛑 全冻结——只读 |
| 半自动 | 信号→Owner OK→执行 | 信号生成→缓存→等待Owner |
| 手动 | Owner手动下单 | — |

---

## 三十五、第三方依赖管理

> **定位**：所有外部依赖——API、库、数据源——的生命周期。
> **对标**：12-Factor App Dependencies + Dependabot。

```
依赖分级:
  Tier1 (核心): 行情API + 经纪商API + DB → 双源冗余
  Tier2 (增强): LLM API → 多模型路由(§12.3)
  Tier3 (可选): 备用数据源 → best-effort, 不告警
```

---

## 三十六、人机带宽优化

> **定位**：1人+AI——Owner 时间是最大瓶颈。必须优化信息密度。
> **对标**：Pareto Principle + Slack Notification Design + Trading HCI(§62)。

```
Owner带宽分配目标:
  施工时段: 80% 决策+审查 + 20% 代码审查
  交易时段: 0% 施工 + 100% 监控+快速决策
```

---

## 三十七、模型漂移监控

> **定位**：量化策略的核心死亡方式——缓慢漂移到无效。需要自动检测。
> **对标**：MLOps Model Drift Detection + Qlib Rolling IC Monitor。

| 漂移类型 | 检测 | 响应 |
|------|------|------|
| 概念漂移 (Concept) | Factor IC 30日滚动均值下降 > 1σ | 因子审查(§65) |
| 数据漂移 (Data) | 市场数据分布变化(KL散度 > 阈值) | 重新训练 |
| 预测漂移 (Prediction) | Sharpe 30日 < 0 | 策略退役评估(§50) |

---

## 三十八、SPOF 消除

> **定位**：任何单点故障不导致全系统崩溃。
> **对标**：K8s HA + CockroachDB + 舱壁隔离(§63)。

| 原SPOF | 消除策略 |
|------|------|
| 单一经纪商API | 多经纪商备份 + 应急平仓(§51) |
| 单一数据源 | 双源交叉验证(§29) |
| 单一 LLM 模型 | 多模型路由 + Fallback(§12.3) |
| Owner 离线 | 冻结模式 + 分级响应(§70) |

---

## 三十九、氛围编程质量保障

> **定位**：100% AI 施工的质量度量——WQA 七维评分。
> **对标**：Google Test Certified + SWE-bench scoring。

```
WQA 七维加权评分 (每Session):

  W1: Test增量 (0.20):   新代码的新增测试覆盖率
  W2: 蓝图对齐 (0.15):  产出是否符合蓝图设计
  W3: ruff 0 warning (0.10):  Lint 基线检查
  W4: Gate不新增失败 (0.20):  G0-G7门禁全绿?
  W5: Owner不回退 (0.15): 是否被Owner revert
  W6: Session完成率 (0.10): (产出数)/(承诺数) × 100%
  W7: Token效率 (0.10): 消耗Token/产出实用性(§12)
```

---

## 四十、市场数据管线与回测引擎

> **定位**：数据从 API → 本地 DB → 因子计算 → 策略回测的完整路径。
> **对标**：Qlib DataHandler + VectorBT + Backtrader architecture。

### 40.1 市场数据管线

| 步骤 | 组件 | 职责 |
|:--:|------|------|
| 1 | AkshareProvider | 拉取A股日线/分钟线→sqlite |
| 2 | DataValidator | 完整性/及时性/有效性校验(§29) |
| 3 | FeatureStore | 因子计算+特征存储(§42.1) |

### 40.2 回测引擎

| 功能 | 要求 |
|------|------|
| 执行模拟 | 考虑滑点+佣金+冲击(§64.2) |
| 基准对比 | 沪深300/中证500/国债指数 |
| 输出 | 年化收益/MaxDD/Sharpe/Calmar + 逐日PnL + Turnover |

---

## 四十一、订单执行与风控

> **定位**：交易执行的第一个和最后一个防线——销前→定时→销后三层风控。
> **对标**：Interactive Brokers OMS + OCC Risk Controls + FIX Protocol。

### 41.1 三层风控时间线

| 时间点 | 检查 | 拒绝后果 |
|:--:|------|------|
| Pre-Trade | 仓位上限/风险敞口/资金充足/熔断暂停 | 拒绝下单 |
| At-Trade | 价格偏离度/秒级频率限制 | 撤单+ALARM |
| Post-Trade | PnL归因/TCA/累计滑点 追踪 | 写入日报(§61) |

### 41.2 Production Shadow

> 订单同时发往 实盘 + 虚拟盘 → 对比滑点 →跑时间为校准(§64)

### 41.3 OMS 状态机

```
[FIX_NewOrderSingle] → PENDING → ACK → PARTIAL_FILL → FILLED → [FIX_ExecutionReport]
任何→ REJECTED/CANCELLED → 自动重试 L2(§24.2)
```

---

## 四十二、量化 ML 工程

> **定位**：特征存储 + 数据泄漏防御 + 训练/推理管线。
> **对标**：Uber Michelangelo + Qlib + Tecton Feature Store。

### 42.1 特征存储

```
特征存储SQL:
  CREATE TABLE features (
    symbol TEXT, date TEXT, factor_name TEXT, value REAL,
    computed_at INTEGER,
    PRIMARY KEY (symbol, date, factor_name)
  )
```

### 42.2 训练/推理分离

```
Training Pipeline:  历史数据(2016-2024) → 因子计算→→ 模型训练
Inference Pipeline: 实时数据→→→→因子计算→→→模型预测
严禁: 训练时access ≥ inference dated; Look-ahead bias(§42.3)
```

### 42.3 数据泄漏六项检查

| # | 检查 | 通过标准 |
|:--:|------|------|
| 1 | 因子计算日期 > 行情日期? | 永不 |
| 2 | 训练/测试时序交错? | 训练 < 测试 |
| 3 | 未来数据可达 因子Store? | 不可达 |
| 4 | Factor analysis 用了未来IC? | 用历史IC only |
| 5 | 组内(年中)vs年reset 信号 提前? | 延后 1 日 |
| 6 | 财报/拆分日期 (ex-ante vs ex-post) | ex-ante only |

### 42.4 市场状态切换检测

> Markov Switching 模型→ HMM (隐状态=3: 牛市/震荡/熊市)——自动切换策略权重。

---

## 四十三、运维成熟度

> **定位**：从"能跑"→"跑得稳"。MTTD/MTTR, 告警疲劳, Runbook自动化。
> **对标**：Google SRE Maturity Model + Incident Command System。

### 43.1 MTTD/MTTR

| 指标 | 目标 |
|------|:--:|
| MTTD (Mean Time To Detect) | <5min (Telemetry) |
| MTTR (Mean Time To Resolve) | <30min (自修复L1+L2) |
| Alert-to-action 延迟 | <1min (Owner在线) |

### 43.2 告警疲劳防护

> 单告警 < 5次/天——合并同类型、去重、分级
> 告警级别: INFO→WARN→CRIT→EMERGE(Owner see only 3个)

### 43.3 Runbook 自文档化

> 每次事故→( AI→自动生成 runbook  )
> Owner离线24->,AI→自用runbook 响应

### 43.4 SLO 月度评审

> 每月 1 次: SLO是否需要调整(§20—— calm review)

---

## 四十四、氛围编程深层实践

> **定位**：AI 大规模施工的高级技巧。
> **对标**：Cursor Rules + Continue.dev AI Coding + Windsurf Cascade。

### 44.1 AI 代码溯源

```
每段 AI 代码的头部注释:
  # @ai: deepseek-v4-pro (2026-04-15)
  # @prompt-hash: sha256:abc123...
  # @session: session-20260505-001
  # @reviewed-by: Owner, L3 Review
  # @ticket: MOD-INF-005 / task-42
```

### 44.2 Multi-Agent 辩论

> 两个独立 AI(不同 model,不同 session) → 互相审查对方方案→ Owner审阅

### 44.3 Context 回收与重用

> 每个Session 结束时 → AI 总结 key findings → 写入 Session Handover → 下 Session 只用摘要 (~1500 tokens saved)

### 44.4 Prompt A/B 测试

> 两个 variant→ 各跑 3 次 →对比—产出质量, 一致性＋ 消耗 token → 选最佳

### 44.5 AI Git 工作流

```
      main ▲
           │ PR merge (only Gate ✅ )
      feature/ai-gen ────▶  PR ──AI────▶ (auto review)▶  Owner approve▶ Merge
```

### 44.6 AI 高效度量

```
AI Velocity:
  Commits/session, LOC/session, Cost per commit ($)
  Target:  ≥3 commits/session 
```

---

## 四十五、架构基础契约

> **定位**：模块之间的硬约定——比"约定"更强，"越界则系统崩"。
> **对标**：K8s v1 APIs Guarantee + gRPC protocol + 2PC/XA transactions。

### 45.1 模块间通信契约

| 约束 | 要求 |
|------|------|
| 数据格式 | JSON→所有跨模块; only σ within file |
| 版本管理 | 所有 API→ version prefix (💻 v1/get_signal ) |
| 契约存档 | 变化→ CT-### contract in MOD-MASTER-001 |

### 45.2 同步/异步边界

```
同步调用( Critical ): 信号→风控 (must  <10ms)
异步(非关键): 研究任务, 日志 export, Deep dive analysis(>=50ms保证)
```

### 45.3 幂等性保证

```
订单幂等:  key = { client_order_id: "uuid4V4", timestamp: int64 } 指向唯一 交易
信号幂等:  key = { signal_id  + tick_ts_ms }——> 最多 1次  风控/ml

Implementation:
   UID dimension:
       generate→ hash(client_order_id + timestamp)  → checkpoint to DB
   Before dispatch:
       check db:   hash exist?  → REJECT
```

### 45.4 断路器 (Circuit Breaker)

```
状态机:  Closed (initial) 
        └─failures > 5/60s→  OPEN (1 minute)  → (close)→Half-Open
```

### 45.5 最终一致性

```
Eventual consistency:
  Use Lamport(happend_before) for cross-module events→ strong→
```

---

## 四十六、1人运营保障

> **定位**：单操作者的风险和行为健康——避免 burnout、决策疲劳、过度交易。
> **对标**：Solo DevOps Pattern + Burnout Prevention + Trading Psychology。

### 46.1 每日负荷上限

| 指标 | 上限 |
|------|:--:|
| Session 数量 | ≤4 天 |
| AI产出台评审 | ≤12 commits/天 |
| 施工+交易同天 | 🛑 禁止 (分时段) |
| 重大部署后观察期 | 48h 不部署 |

### 46.2 决策简约化

> 每个Session 最多3个关键决策——剩下由 AI 自主做

### 46.3 Burnout 早期预警

> 连续2天Session完成率<50% → Burnout Warning → 建议休息

### 46.4 强制休息节奏

| 频率 | 活动 |
|:--:|------|
| 每日 | 12h 离线休息 |
| 每周 | 1天 无码/无交易 |
| 每月 | 2天 完全离线 |

---

## 四十七、金融合规与法律

> **定位**：个人量化交易的合规边界——注册要求、AI决策的合法性、MiFID/SEC。
> **对标**：CFTC Rules + MiFID II Art.17 + SEC Rule 613 + SR 11-7。

### 47.1 交易重建能力

> 所有交易→immutable log(≥5年): tick,决策,订单,成交,修改
> 审计请求→ 5 business day 内产出

### 47.2 Best Execution (最优执行)

```
MIiFID II Art.27 Best Execution:
  Execution vs. Arrival Price < 10bps (Tier-1 Target)
  ＜验证每天; 违反→ 警报
```

### 47.3 AI 决策的法律责任

> AI 生成交易→ Owner 法律责任 (人永远是最后负责人)
> 不可将责任委派给 AI——这是法律基础(§2.3——Legal Liability; SEP/BCP/IT合规)

---

## 四十八、策略验证与统计严谨性

> **定位**：Walk-Forward Optimization + Deflated Sharpe Ratio + 多重测试校正。
> **对标**：Two Sigma Backtesting Framework + Lopez de Prado's Advances。

### 48.1 Walk-Forward 滑动验证

| 参数 | 值 |
|------|:--:|
| In-Sample (IS) | 5年滑动 |
| Out-of-Sample (OOS) | 3年 (前方) |
| 滑动步长 | 1年 |
| 最少OOS周期 | 3 |

### 48.2 Deflated Sharpe (DSR)

> 概率模型——在 N 次"发现"中, Sharpe≥2.0->→大概率是过拟合?
> DSR=p(最大发现>报告) < 0.05→上线标准

### 48.3 多重测试校正

| 方法 | 使用 |
|------|------|
| Bonferroni | 最保守→策略最少的上线 |
| Holm-Bonferroni |   比B更优力 |
| BH (Benjamini-Hochberg) | FDR——因子筛选 |

### 48.4 样本外衰减曲线

> OOS 3年 + 中 0 存活曲线→合理衰减(=回退平稳)直接判定 无效

---

## 四十九、智能执行与微观结构

> **定位**：TWAP/VWAP/Implementation Shortfall + Almgren-Chriss 模型 + FIX Protocol。
> **对标**：Hudson River/KCG Execution Engines + FIX 5.0。

### 49.1 五种执行算法

| 算法 | 场景 | 参数 |
|------|------|------|
| TWAP | 平均含拆 小单→ | 1–15min ping |
| VWAP | 跟随成交量分布→  | hist vol profile |
| IS (Implementation Shortfall) | 最优化冲击/风险   |risk_aversion (λ) |
| POV (PercentOfVolume) | 参与量= x% of 市场量 | x=10% |
| Adaptive | 实时条件选择 | 动态算法选择 |

### 49.2 Almgren-Chriss 冲击模型

```
Market Impact (元):  η·σ·(X/V)^γ + ε
   η (冲击系数)   = 0.14  | 
   γ (冲击指数)   = 0.6   |
   ε (固定成本)   = 0.01  |   SV→slip 基于 体积函数
   σ (波动率)     = 20天↓ 
```

### 49.3 FIX Protocol 映射

| FIX MsgType | 英文 | ZephyrAlpha |
|:--:|------|------|
| D | NewOrderSingle | 下单 |
| 8 | ExecutionReport | 成交/拒绝 |
| F | OrderCancelRequest | 撤单 |
| G | OrderReplaceRequest | 改单 |
| 4 | OrderCancelReject | 撤单拒绝 |
| 3 | Reject | 订单拒绝 |

---

## 五十、多策略组合与容量管理

> **定位**：相关性矩阵 + 资金分配 + 容量估计 + 退役标准。
> **对标**：Bridgewater All-Weather + AQR Portfolio Construction。

### 50.1 策略组合优化

| 方法 | 公式 | 场景 |
|------|------|------|
| 1/N (Equal Weight) | w_i = 1/N | baseline |
| Risk Parity | w_i ∝ 1/σ_i | 风险均衡 |
| Kelly Criterion | w_i ∝ (μ/σ²)_i | > growth |
| Max DD | w_i ∝ 1/MaxDD_i | 防守导向 |

### 50.2 容量估计 (C_max)

```
C_max = min(C_liquidity, C_impact)
   C_liquidity = ADV × max_participation_rate
   C_impact = (Max_acceptable_impact / η·σ)^(1/γ) × V
```

### 50.3 策略退役触发器

| 触发 | 条件 |
|------|------|
| 长期失效 | 连续12月Sharpe≤0 |
| 超衰 | 实盘/回测≤ Decay Budget (§70.1)→ |
| 容量饱和 | C_used > 0.8 × C_max |
| Owner判断 | Owner 主观标记无效 |

---

## 五十一、经纪商容灾与应急平仓

> **定位**：多经纪商+故障处理+应急平仓+资金隔离。
> **对标**：Interactive Brokers Multi-Account + Hedge Fund Prime Broker Setup。

### 51.1 三级经纪商

| 等级 | 用途 | 预算占比 |
|:--:|------|:--:|
| Primary | 主执行 | 80% |
| Secondary | 备份执行 | 20% |
| Emergency | 应急平仓 | 未用(按需) |

### 51.2 四类故障处理

| 故障 | 响应 |
|------|------|
| API 不可达 | 切换 Secondary |
| 订单拒绝 | 诊断原因→重新提交/切换 |
| 价格严重偏离 | 取消+ALARM |
| 经纪商破产 | 即时冻结+切换 Emergency |

### 51.3 应急平仓 4 步

```
Emergency Liquidation:
  Step 1: 按流动性优先级排序(最流动→最不流动)
  Step 2: 市价平仓(接受滑点→生命重于利润)
  Step 3: 全单发送→ 5min 内确认
  Step 4: 写入 Immutable Log (§47.1)
```

---

## 五十二、可重现性与确定性

> **定位**：6层确定性保证 + 审计重放 + 逐笔确定性。
> **对标**：NixOS Reproducible Builds + Bitcoin Core Determinsm。

### 52.1 六层确定性

| 层 | 措施 |
|:--:|------|
| Python | Virtualenv + pip-lock |
| 依赖 | requirements.locked.txt (versions pinned) |
| 随机种子 | random.seed(42) + np.seed(42) |
| 数据 | Data Version: CSV snapshots with hash |
| LLM | temperature=0 + Model version fixed |
| 时钟 | 使用historical timestamps,不依赖系统时钟 |

### 52.2 审计重放

```yaml
# .zeph/replay/session-20260505-001.yaml
replay:
  session_id: "session-20260505-001"
  model: "deepseek-v4-pro"
  temperature: 0
  input_hash: "sha256:abc123..."
  output_expected: "sha256:abc456..."
```

---

## 五十三、实盘后验证与持续优化

> **定位**：部署验证→A/B实盘对比→滑点回归→税务优化。
> **对标**：Jane Street Post-Deploy Validation + ITG TCA。

### 53.1 五维部署后验证

| 检查 | 时间窗口 |
|------|:--:|
| 信号一致性 | 1h |
| 滑点差异 | 1 session |
| Test Through Gate | 24h |
| Auto Rollback if Failure | 1h auto |
| Owner Review | 1 session |

### 53.2 A/B 实盘对比

> 30 日; PnL→ ρ(sim vs live)→R²(每日) 对抗对比

### 53.3 滑点回归

```
Slippage Model:
  Slip = β₀ + β₁·(订单量/ADV) + β₂·Spread + β₃·Volₒn + ε
  校准后用新β每 周  (滚动30天)
```

---

## 五十四、AI 代码审查深度模型

> **定位**：L0-L5 五层审查深度 + 准入标准 + 铁律。
> **对标**：Google Code Review Guidelines + SWE-bench Verified。

| 层级 | 深度 | 准入条件 | 时间 |
|:--:|------|------|:--:|
| L0 | 语法 (ruff) | 0 warning | <5s |
| L1 | 安全审计 | 无 CWE | < 30s |
| L2 | Logic+boundary | 无off-by-one/状态图 | <5min |
| L3 | 架构对齐 | 符合蓝图(§0) | <15min |
| L4 | 策略对齐 | WQA 7维通过(§39)+ Δ→ | <30min |
| L5 | 双 AI 辩论 | 2 AI→综合评分+ → | <1h |

审查铁律: ① AI+code → 人必Review( 不能 "自动合")
        ② 逻辑变更>50行 → L3 最低
        ③ 涉及交易→  前  Owner OL批准

---

## 五十五、组合级风险管理与压力测试

> **定位**：VaR/CVaR/Component VaR + 5 历史场景压力 + 危机相关性双重矩阵。
> **对标**：RiskMetrics + Basel III Stressed VaR + Bridgewater Risk Parity。

### 55.1 组合风险度量

| 度量 | 置信水平 | 计算 |
|------|:--:|------|
| VaR (Value at Risk) | 95%/99% | Historical (500天) |
| CVaR (Expected Shortfall) | 99% | E(loss \| loss > VaR_99) |
| Component VaR | — | 每个位置→ marginal VaR 贡献 |

### 55.2 五大压力场景

| 场景 | 实现 |
|------|------|
| GFC (2008) | 雷曼破产→global 急跌-50% |
| COVID Crash (2020-03) | -35% / 1 month+ volatility ×5 |
| Flash Crash (2010-05-06) | -10%/ intraday+ recovery(白天?) |
| Rate Shock (2022) | Fed 加息 (-30% Bond) — |
| Volmageddon (2018-02) | VIX spike +  -90% Inverse VIX |

### 55.3 危机相关性管理

```
Crisis Correlation Matrix (5×5):
  平时相关性→Inflate:  ρ_crisis = min( 2×ρ_正常, 0.95 )
  对策:
    1) 提前减仓→仅处理非零相关性
    2) 分散化资产类型(必需:多multi-asset)
    3) 动态风险映射(≥周回顾)
```

---

## 五十六、波动率目标与动态杠杆

> **定位**：Vol Target=15%框架 + 杠杆约束 + 模型信任度 Warm-up Ramp。
> **对标**：AQR/Two Sigma Vol Targeting + Risk Parity。

### 56.1 Vol Target 框架

| 参数 | 值 |
|------|:--:|
| Vol Target (σ_target) | 15% 年化 |
| Leverage = σ_target / σ_realized(60天) | — |
| Max Leverage | 2.0× |
| Min Leverage | 0.0 (全现金) |

### 56.2 杠杆约束

| 约束 | 上限 |
|------|:--:|
| 单一资产: Max | 25% of AUM/Notional |
| Sector 上限 | 40% (AUM) |
| Cash reserve | ≥5% of AUM |

### 56.3 Warm-up Ramp (4 阶段)

| 阶段 | Leverage Cap | 条件 |
|:--:|:--:|------|
| P1 | 0.25× | 前 30 天——学习阶段 |
| P2 | 0.50× | 30-60天——验证基础 |
| P3 | 0.75× | 60-90天——信任建立 |
| P4 | 1.00× | 90+天——完全信任 |

---

## 五十七、因子择时与跨资产配置

> **定位**：5 种市场状态→因子映射 + 6×6 跨资产相关性。
> **对标**：Two Sigma Factor Timing + AQR Macro Allocation。

### 57.1 市场状态识别 (HMM, 3 状态)

| 状态 | 特征 | 最优因子 |
|------|------|------|
| Bull (S1) | Trending →低Vol— | Momentum+ Growth |
| Sideways (S2) | Ranging→ | Mean Reversion+ Quality |
| Bear (S3) | High Vol→ | Low Vol + Value/Defense |

### 57.2 战略-战术分配

> 战略 (长期 60%):  60%分配于 LTerm Expected Return(Strategic weights)
> 战术 (短期 40%):  基于 HMM状态 / Rotate factor weights

### 57.3 6×6 跨资产相关

> Equities, Fixed Inc, Commodities, FX, Crypto, Cash——每月重算 ρ

---

## 五十八、交易日历与合约管理

> **定位**：3 交易所日历 + 期货换月规范 + 期权到期。
> **对标**：Bloomberg/Refinitiv Trading Calendars + CME Roll Schedules。

### 58.1 交易日历

| 交易所 | 时区 | key假日 |
|------|:--:|------|
| NYSE | ET | New Year, MLK, Prez, Good Fri, Mem, Indep, Labor, Thanks, Xmas |
| CME (期货) | ET | +  周一——(  shuffle)   Colin Day — |
| ICE (商品) | ET  | —| |

### 58.2 期货换月

| 合约 | Roll 规则 | 开始 |
|------|------|:--:|
| ES (S&P) |  从 前月 + → close >  5天 | rolls |
| CL (Crude) |  +  close> 3天 | roll → LT |
| GC ( Gold) | before close ——1~3天→ |
| ZN (10Yr NOTE) | Before First Delivery←  | 15天 |

### 58.3 期权到期

| 类型 | 到期 | action |
|------|:--:|------|
| Monthly (SPX) | 第3个Fri |  |
| Weekly | 每个Fri   |  roll→ close |
| Quarterly | 季末Fri   |

---

## 五十九、运维基础保障

> **定位**：备份验证 × 日志轮替 + 配置漂移 + 管线检查点 + 环境版本化。
> **对标**：SRE Workbook + Database Reliability Engineering。

### 59.1 四层备份验证

| 层 | 数据 | RPO | 验证频率 |
|------|------|:--:|:--:|
| DB Full | sqlite→tar.gz | 24h | 每周恢复测试 |
| DB WAL | WAL→ 连续 | 1h |  每日 auto 扫描 |
| Config | `.zeph/config/*.toml`→git | 实时 | 每个 commit |
| Secrets | 1Password Vault | 实时 | 按月  |

### 59.2 四类日志保留与轮替

| 类型 | 保留 | 轮替 |
|------|:--:|:--:|
| Session Logs |  1 year | 转移→cold storage |
| Trade Logs (immutable) | +>=5 year | No deletion  |
| Debug Logs | 30 d | 每天:auto Zip |
| Audit Logs | + > 7 years | No deletion→ cold |

### 59.3 配置漂移检测

> 每天  diff： 当前运行时Config  vs Git版本→≠→  ALARM

### 59.4 管线检查点

> 信号管线每步有 checkpoint hash→4 Stage Recover──
> 中断→从最近checkpoint继续→ 不重做前期

### 59.5 开发环境版本化

| 组件 | 版本锁定 |
|------|------|
| Python | 3.12 |
| pip + setuptools | pinned in .lock |
| ruff, pytest | pinned  |
| tree-sitter 版本 | pin  |

---

## 六十、AI 施工质量 SPC

> **定位**：统计过程控制(SPC)→ AI 质量指数。比 WQA 更量化。
> **对标**：Western Electric SPC Rules + SixSigma + ML Monitoring。

### 60.1 七维加权质量评分 (与 §39互补)

| 维 | 权重 | 测量 |
|------|:--:|------|
| Pass Rate | 0.20 | Gate G0-G7 通过率 |
| Revert Rate | 0.15 | Owner revoke % |
| Test Coverage Δ | 0.15 | Δ Coverage (− =fail)|
| Lint Health | 0.10 | ruff warnings count |
| 逻辑正确性 | 0.20 | SWE-bench scoring |
| 蓝图对齐 | 0.10 | AI→ vi  read §0 一致性 |
| 速度 | 0.10 | Time-to-complete |

### 60.2 Western Electric SPC 5 规则

```
WE1: 单点 >3σ → 异常(WQA<-2σ)
WE2: 连续2/3 >2σ→ 加速失控
WE3: 连续4/5 >1σ→发散的缓慢漂移——
WE4: 连续8点 = 一侧→  中位偏移 (Mood shift)
WE5: 明显趋势→(5+递增) —— Rate consistent problem
```

### 60.3 三级预警升级

| 预警 | SPC Rule | 动作 |
|:--:|------|------|
| 1级 (Notice) | WE3 (minor drift) | Owner 知悉——hint |
| 2级 (Warning) | WE2/WE4  | 暂停AI自主——Owner必需审查 |
| 3级 (Red) | WE1/WE5 | 🛑 AI Frozen—紧急动作 |

---

## 六十一、PnL 归因与交易成本分析

> **定位**：L07 Post-Trade Analytics 需要四维归因——因子/行业/风格/TCA。Two Sigma 在 PnL 归因上的投入超过信号研究本身。
> **对标**：Two Sigma Attribution Model + Brinson Attribution + ITG TCA。

### 61.1 四维归因框架

| 归因维度 | 方法 | 目的 |
|------|------|------|
| 因子归因 | R_t = ∑ β_i · F_i + ε_t | "赚了什么因子？" |
| 行业归因 | GICS 11部门 decompose | "赚在哪个行业？意外集中？" |
| 风格归因 | Fama-French 5因子+Momentum+Quality | "风格漂移了吗？" |
| TCA | Implement Shortfall + 佣金 + 冲击 | "滑点/冲击/佣金吃了多少？" |

### 61.2 每日 PnL 归因报告格式

```
{
  "total_pnl": "+2,450 USD",
  "factor_attribution": {"momentum_1y": +1200, "vol_30d": -300, ...},
  "tca": {"commission": -15, "impact": -60},
  "warnings": ["因子momentum_1y贡献>50%总PnL, 集中度危险"]
}
```

---

## 六十二、日运营节奏与交易会话协议

> **定位**：开盘前检查→盘中监控→收盘对账→批次处理的完整交易日流程。交易时段 Owner 需要短×快×无歧义指令——不是长篇 EXPLORE。
> **对标**：Two Sigma Trading Day SOP + Jane Street Trading Floor Protocol。

### 62.1 5 Phase 交易日流程 (ET)

| Phase | 时间 | 操作 | 执行者 |
|:--:|------|------|------|
| P1: 盘前 | 08:00-09:30 | 系统健康+行情连通+经纪商+日历+敞口确认 | AI+Owner确认 |
| P2: 盘中 | 09:30-16:00 | 信号生成+风控+执行+市场事件响应 | AI全自动 |
| P3: 收盘 | 16:00-16:30 | 未成交取消+持仓确认+日末PnL估算 | AI自动 |
| P4: 对账 | 16:30-17:30 | 经纪商对账+PnL归因+Daily Report | AI自动 |
| P5: 维护 | 17:30-18:00 | 持久化+备份+session handover | AI自动 |

### 62.2 交易时段快捷指令

| 指令 | 含义 | 响应时间 |
|------|------|:--:|
| `<STATUS>` | 当前状态(PnL/敞口/报警) | <2s |
| `<PAUSE>` | 冻结所有自动交易 | 即时 |
| `<RESUME>` | 恢复自动交易 | <5s |
| `<ALARM>` | 活跃报警列表 | <1s |

**禁止交易时段执行长 EXPLORE/PLAN/BUILD。**

---

## 六十三、系统容错模式深度

> **定位**：Google SRE 不止 Circuit Breaker——需要 Bulkhead(舱壁隔离)+Retry+Backoff+Jitter+Timeout Propagation+Shed Load+4层优雅降级。
> **对标**：Google SRE Ch.21-23 + Resilience4j + Armory。

### 63.1 四种核心模式

| 模式 | 故障场景 | ZephyrAlpha 实现 |
|------|------|------|
| Bulkhead | 模块A 吃满 CPU → 影响其他 | 4 Pool隔离: Signal(30%)/Exec(25%)/Research(25%)/System(20%) |
| Retry+Backoff+Jitter | API 瞬时抖动 | 10ms→100ms→1s→10s→30s (max 5次)+ ±25% jitter |
| Timeout Propagation | 链式调用僵死 | 每步传递剩余时间预算→总≤460ms(§66.3) |
| Shed Load | 请求突增 | 优先拒绝低优先级任务 →保留核心功能 |

### 63.2 优雅降级层级

| Tier | 行为 | 触发 |
|:--:|------|------|
| T0 | 全功能 | — |
| T1 | 信号更新 1min→5min | CPU>80% |
| T2 | 仅用核心因子 | 数据源异常 |
| T3 | 暂停执行——只风控——Hold现有仓位 | 经纪商API不可达 |
| T4 | 全系统logging——不动任何指令 | 行情+信号都不可用 |

---

## 六十四、微结构防御与模拟盘保真度

> **定位**：不是一个策略能赚钱而是怎么不被别人赚钱。量化新手99%亏损来源——被HFT抢先、被做市商吃spread、止损被扫。同时模拟盘需要量化保真度差距。
> **对标**：Optiver/Hudson River Trading Defence Patterns + IB Paper Trading Gap。

### 64.1 五大防御

| 威胁 | 防御 |
|------|------|
| HFT 抢先 | 订单切割+TWAP+不显示完整量 |
| 止损掠食 | 非整数位+Server端止损+动态 |
| 价差剥削 | 避宽Spread+中间价限价 |
| 盘口空洞 | 验证盘口深度(≤20%深度×Amount) |
| Gapping/跳空 | 止损+止损限价结合+风险事件前减仓 |

### 64.2 模拟盘保真度模型

| 维度 | 模拟 vs 实盘 | 保真度因子(FF) |
|------|------|:--:|
| 成交概率 | 100% → 85%–95% | 0.85 |
| 滑点 | Fix → Variable+冲击+延迟+泄露 | 0.30-0.60 |
| 盘口深度 | ∞ → real | 0.20-0.50 |
| 部分成交 | 全量→60%–90%填充 | — |
| **总 FF** | **预期实盘/模拟 = 40%–70%** | |

---

## 六十五、因子治理与策略生命周期深化

> **定位**：WorldQuant 的 Factor Review Board 做法——因子不是越多越好。100因子→500→失控。需要准入/去重/正交化/退役完整四阶段。
> **对标**：WorldQuant Factor Review Board + AQR Factor Zoo。

### 65.1 四阶段生命周期

| 阶段 | 要求 | 门控 |
|------|------|:--:|
| 准入门 (Admission) | 经济逻辑+WFO IS/OOS Sharpe≥0.3+DSR≤0.05+无泄漏 | GATE_NEWFACTOR |
| 去重/正交化 | 所有因子对 ρ——若>0.7→必须是horse race→保留好的 | 去重 |
| 监控 | IC均值+std+IC半衰期+最近3月IC>0占比 | 周/月 |
| 退役 | 12月IC<0.01 / σ>3σ / Sharpshooter / Owner主动标记 | →Cold Storage |

### 65.2 文法正交化管线

```
原始: [FA, FB, FC, FD, FE]
ρ_AB=0.82→cluster (FA,FB)→保留代表→非代表→Cold storage
结果: 50因子→12代表 预测能力不降
```

---

## 六十六、功能开关与部署安全网

> **定位**：Google Dark Launch = 部署≠启用。1人+AI最关键安全网——新代码先部署(暗)→验证→逐步灰度→Owner click ON。事故后自动验证5步。
> **对标**：Google Dark Launch + Facebook Gatekeeper + LaunchDarkly。

### 66.1 Feature Flag 体系

| Flag 类型 | 粒度 | 示例 |
|------|------|------|
| Release Flag | 系统级 | new_execution_path_v2 = OFF(部署时)→ ON(验证后) |
| Ops Flag | 运维级 | backup_to_s3_test = ON/OFF |
| Kill Switch | 全系统 | KILL_ALL_TRADES——Owner 1指令→全OFF |

### 66.2 暗启动流程

```
Step 1: Deploy (Flag=OFF) → Verify: ruff + test + gate
Step 2: Flag=30% ON → 对比 ON vs OFF (Error/Latency/PnL)
Step 3: Owner Review → OK→100% ON, FAIL→0% (revert Flag)
Step 4: 稳定后清理flag branching code
```

### 66.3 事故后五步自动验证

| 验证步骤 | 内容 |
|:--:|------|
| V1 | Code Hash 与回滚前 Old Commit 100%一致 |
| V2 | Config TOML 回滚后一致性 |
| V3 | SQLite Schema 回滚后无异变 |
| V4 | API REQ/RESP JSON schema match |
| V5 | System Health 全绿——10 tests |

---

## 六十七、AI 自诊断-自修复与知识自动化

> **定位**：SPC 检测退化+AI~全闭环自修复 + AUTO-KB从session自动提取知识。不等Owner"有时间写"OWNER_BRAIN_DUMP.md。
> **对标**：Continue.dev Auto-Debug + Claude Code Self-Correction + Windsurf Auto-Summarize。

### 67.1 三层自修复闭环

| 层级 | 范围 | 流程 |
|:--:|------|------|
| L1 (AI自主) | lint/whitespace/format | Auto Fix→ Commit+`[auto-fix]`→✅ |
| L2 (建议修复) | test fail/Gate失败/重复代码 | AI诊断+suggest≥2备选→Owner `<AutoFix>`→AI执行+验证 |
| L3 (手动修复) | 性能退化/逻辑错误/Security | AI深诊(scan+backtrace)→Owner手动→AI验证(regression test+health check) |

### 67.2 AUTO-KB 知识自动提取

```
分析源: Session决定(commits→decisions) + Owner注释(KB: tag) + 架构变更
生成: KB entries——date/reason/relatedDecision/source/confidence(0-100)
效果: Owner不必记得Follow-up→ Knowledge持续积累
```

---

## 六十八、氛围编程确定性保障

> **定位**：氛围编程最大的隐性问题——同一个Prompt，AI明天给你不同的答案。需整合CSCV验证+4层确定性保障+系统复杂度熵度量+复杂度超标时的强制反击。
> **对标**：Claude Code Determinism + CSCV Protocol + Cursor Controller。

### 68.1 跨会话一致性验证 (CSCV)

```
每10 Session:
  随机选上Session的prompt+task→重放
  对比(t_old vs t_new): Code行差/AST diff/Semantic等价/Prompt Interpret
  Consistency Score = avg(4维) ∈ [0,1]
  Score<0.7→⚠️, Score<0.5→🔴系统Prompt体系根本性故障
```

### 68.2 确定性四层保障

| L0 模型 | Temperature=0 + fixed model version |
| L1 上下文 | Same AGENTS.md + §0.1 词语表 + §15.2 指令词典 |
| L2 依赖 | random.seed(42) + numpy.seed(42) + pip-lock + tree-sitter |
| L3 验证 | CSCV 每10 session自动运行→写入Handover |

### 68.3 系统复杂度熵度量

```
System Entropy (每次commit计算):

  Modules (0.3/logN)+ cross_imports(0.2)+ LoC_bloat(0.15)
  + statefulness(0.10)+ duplication(0.15)+ test_cov(-0.10)

  0–2.0   ✅ 健康——1人可维护
  2.0–3.5 🟡 预警——规划偿还复杂度
  3.5–5.0 🔴 紧急——必须大规模简化
  >5.0    💀 不可维护
```

### 68.4 超标强制反击

```
熵 > 3.5 🔴:
  AI生成complexity_reduction_plan:
  合并模块Top3 + 去重代码Top5 + 退役因子
  Owner审批(2周内)→AI执行→验证全量test still green
  目标: 熵值回到<2.0
```

---

## 六十九、Secrets 生命周期与环境可重建性

> **定位**：不只是"加密存着"——密钥有完整的创建/分发/轮替/吊销/审计生命周期。每日自动验证"换电脑clone→全量测试全绿"。
> **对标**：HashiCorp Vault Lifecycle + AWS KMS Rotation + 12-Factor App Dev/Prod Parity。

### 69.1 Secrets 全生命周期

| 阶段 | 操作 | 频率 | 工具 |
|------|------|:--:|------|
| Create | 生成API key→L4 vault存储 | 按需 | 1Password CLI, .zeph/secrets/(gitignored+git-crypt) |
| Distribute | 传递到runtime (env var, 非hardcode) | 每次部署 | .env.local / 1Password ref |
| Rotate | 新密钥生成→验证→旧吊销 | 每90天或泄露时 | rotate_secrets.py |
| Revoke | 即时吊销泄露/过期密钥 | 泄露发现 | 立即revoke+verify API continuing |
| Audit | 谁有访问/上次轮替日/存在于何处 | 每月 | secrets_audit.md |

### 69.2 每日环境可重建性验证 (Auto-CLEAN-BUILD)

```
每日 06:00 UTC:

  1) Fresh Python venv → pip install -r requirements.locked.txt
  2) pytest tests/ --maxfail=10 -x
  3) ruff check . --exit-zero
  4) Gate G0-G4 自检
  5) Demo: 启动数据源→加载1天→因子→信号→1虚拟订单
  
  ALL ✅ → GREEN—系统无条件可重建
  ANY ❌ → YELLOW—Owner 12h内修复
  连续2天❌ → RED—Owner MUST NOW
```

---

## 七十、离线分级应急与全生命周期预算

> **定位**：不只是"冻结"——不同事故等级×不同离线时长=不同响应。同时回测完成时就预设衰减预算。E2E延迟全链路预算分配到每步。代码溯源到行级。
> **对标**：Google SRE Unattended Ops + Two Sigma Decay Budget + Hudson River Latency Budget + Jane Street Provenance。

### 70.1 离线分级应急决策树

```
响应矩阵 (TIF×Severity):
           S1(轻)      S2(中)       S3(重)
  TIF L1(0-30m)   AI自修复    Retry 3x    暂停新开仓
  TIF L2(30m-2h)  AI自修复    暂停新开仓   部分平仓
  TIF L3(2-8h)    Wait        部分平仓    全冻结
  TIF L4(8-24h)   Freeze      全冻结      全冻结
  TIF L5(>24h)    Freeze      全冻结      通知备用联系人+冻结
```

### 70.2 回测-实盘结构衰减预算

```
策略A: 回测 Sharpe=2.1 → 预计实盘=?
  
  老化衰减 (Look-ahead消除)              -0.2
  成本衰减 (冲击+佣金+滑点)              -0.3
  过拟合衰减(PURE OOS beyond WFO)        -0.15
  市场变迁衰减 (Regime change)           -0.1
  其他未建模                             -0.05
  ─────────────────────────────────────────
  预计实盘 Sharpe = 2.1 - 0.8 = 1.3 ✅ (>0.8 =上线)
  
  上线后实盘 Sharpe<1.0 → 触发策略审查
```

### 70.3 E2E 延迟预算

```
Segment               Budget      Alpha Decay / +100ms
Tick→接收              <50ms       negligible
因子计算(batch)        <100ms      -0.01 Sharpe
信号生成               <50ms       -0.005 Sharpe
Pre-trade风控          <10ms       (zero—blocking)
订单路由(API→Broker)   <50ms       -0.02 Sharpe
交易所确认→Fill报告    <200ms      (out of control)
───────────────────────────────────────────
Total                  <460ms      目标<500ms
P99 > 500ms → 切粗粒度因子(1min→5min update)
```

### 70.4 代码全溯源链 (行级)

```
.zeph/provenance/momentum_12m.py:
  lines: [10, 45]
  kind: "ai_generated"
  model: "deepseek-v4-pro"
  model_version: "2026-04-15"
  prompt_hash: "sha256:abc123..."
  session_id: "session-20260505-001"
  reviewed_by: "Owner"
  review_decision: "APPROVED (L3 Review, §五十四)"
```

## 七十一、Prompt 工程全生命周期管理

> **定位**：Prompt 是氛围编程的"源代码"——比 Python 代码更需要版本控制和质量保障。专业氛围编程团队会用 `.cursor/rules` 和 `.claude/instructions` 管理 prompt，但缺少系统性生命周期。
> **对标**：Cursor Rules + Claude Code Custom Instructions + PromptLayer + LangSmith Prompt Hub。

### 71.1 Prompt 版本控制

```
目录结构:
  .zeph/prompts/
    ├── base/                  # 基础提示词模板
    │   ├── system_base.prompt
    │   ├── coding_standard.prompt
    │   └── security_check.prompt
    ├── domain/               # 领域专用
    │   ├── quant_factor.prompt
    │   ├── quant_strategy.prompt
    │   └── trading_ops.prompt
    └── tasks/                # 任务级实例（从模板继承+参数化）
        ├── factor_new.prompt
        └── strategy_validate.prompt

版本规则:
  每个 .prompt 文件头部:
    # @prompt-version: 1.2.0
    # @parent: base/system_base.prompt@1.0.0
    # @last-validated: 2026-05-05
    # @validation-score: 0.87
```

### 71.2 Prompt 回归测试

| 触发条件 | 操作 |
|------|------|
| Prompt 变更 | 用历史任务重放→对比新旧产出 |
| 每30天 | 全量 Prompt 有效性重测 |
| 模型升级 | 所有 Prompt 在新模型上验证 |
| 产出质量 < WQA 0.7 | 回溯定位是否是 Prompt 退化 |

```
Prompt Regression:
  选最近20个已完成任务→回放prompt_at_time vs prompt_now
  比较: AST相似度(>0.85)/逻辑等价性/WQA评分差(<0.1)
  3个以上任务显著退化→ Prompt变更必须回滚
```

### 71.3 Prompt-Output 契约

```yaml
# .zeph/prompts/tasks/factor_new.prompt
contract:
  input_schema:
    required: [factor_description, market, frequency]
    optional: [lookback_window, normalization]
  output_schema:
    required: [factor_code, unit_tests, backtest_summary, leakage_check]
    format: "python_file + test_file + report.md"
  quality_gate:
    test_coverage: ">=80%"
    ruff_warnings: "0"
    leakage_check: "PASS"
```

### 71.4 Prompt 有效性评分 (PES)

| 维度 | 权重 | 测量方法 |
|------|:--:|------|
| 产出质量 | 0.40 | WQA 评分均值 (最近10次产出) |
| 一致性 | 0.25 | 同一任务3次产出的 AST 相似度 |
| Token 效率 | 0.15 | 产出价值 / 消耗 Token |
| 理解准确率 | 0.20 | Owner 人工抽查正确率 |
| **PES < 0.6** | — | Prompt 需要重写 |

---

## 七十二、AI 上下文窗口策略与幻觉防御

> **定位**：AI 施工最核心的硬约束是上下文窗口——超出则截断/遗忘/幻觉。需要精细的上下文预算管理和幻觉检测体系。
> **对标**：Anthropic Context Engineering Guide + Google Gemini Long-Context Best Practices + RAG 幻觉检测论文。

### 72.1 上下文预算分层

| 任务等级 | Token 预算 | 上下文分配策略 |
|------|:--:|------|
| 微型 (≤10K) | ~8K | 全部加载——无需优化 |
| 小型 (10–50K) | ~40K | 蓝图 §0 + 目标模块 §1-§3 + 相关代码 |
| 中型 (50–150K) | ~100K | 蓝图摘要 + 目标代码 + 增量加载依赖 |
| 大型 (150–300K) | ~200K | 四阶段增量: 蓝图→API→实现→测试 |
| 超大型 (>300K) | — | 🛑 必须拆分任务→多Session |

### 72.2 渐进式上下文加载

```
Phase 1: 蓝图路由 (§0, ~500 tokens)
Phase 2: 目标模块架构 (§1-§3 目标蓝图, ~1500 tokens)
Phase 3: API/接口定义 (目标模块 exports, ~2000 tokens)
Phase 4: 相关代码 (限3个文件, 每个 ≤500行, ~3000 tokens)
Phase 5: 测试+历史 (限时, ~2000 tokens)
Total: ~9000 tokens baseline, 剩余用于产出
```

### 72.3 上下文裁剪规则

| 裁剪优先级 | 何时裁剪 | 内容 |
|:--:|------|------|
| P1 | Token 使用 >70% | 移除已读完的蓝图全文→仅留摘要 |
| P2 | Token 使用 >80% | 移除非目标模块代码→仅留接口签名 |
| P3 | Token 使用 >90% | 移除长注释/日志/冗余变量声明 |
| P4 | — | 🛑 不再裁剪——强制结束当前Session |

### 72.4 AI 幻觉三级检测

| 检测类型 | 方法 | 阻断级别 |
|------|------|:--:|
| API/库存在性 | 验证所有 import 的包在 requirements.locked.txt 中存在 | 🔴 阻断 |
| 函数/类存在性 | AST 解析→验证所有调用的函数/类在代码库中真实存在 | 🔴 阻断 |
| 参数签名正确性 | 检查函数调用参数数量+类型是否匹配定义 | 🟡 警告 |
| 数据引用正确性 | 验证数据源名称/列名/表名存在 | 🔴 阻断 |
| 逻辑一致性 | 检测自相矛盾的断言或条件 | 🟡 警告 |

### 72.5 幻觉自动修复协议

```
检测到幻觉:
  L1 (API/库不存在): 自动搜索替代方案→替换→重测
  L2 (函数不存在): 搜索代码库中相似函数→建议纠正
  L3 (数据引用错误): 展示可用数据源→AI重新生成引用
  L4 (逻辑矛盾): 标记给Owner→不清除→等待人工判断
```

---

## 七十三、多模型共识与智能体辩论协议

> **定位**：§44.2 提到了 Multi-Agent 辩论，但缺乏具体协议。专业氛围编程需要量化的共识机制——不是"两个 AI 都觉得行"就行。
> **对标**：Anthropic Constitutional AI + DeepMind Sparrow Debate Protocol + SWE-bench Multi-Agent。

### 73.1 三种共识协议

| 协议 | 参与者 | 决策规则 | 适用场景 |
|------|:--:|------|------|
| 简单多数 (Simple Majority) | 3个不同模型 | ≥2同意 | 代码审查、重构建议 |
| 加权投票 (Weighted) | 2-3个模型 | 基于模型能力加权 | 架构决策、安全审计 |
| 统一共识 (Unanimous) | 2个模型 | 2/2必须同意 | 交易相关变更、密钥操作 |

### 73.2 结构化辩论格式

```
Round 1: 方案提出
  Agent-A (Writer):   生成方案 + 论据 (为什么这样做)
  Agent-B (Reviewer): 批判性审查 (至少指出2个风险/盲点)

Round 2: 反驳与修正
  Agent-A: 回应批评→修正方案或论证为什么原方案更好
  Agent-B: 二次审查→评价修改是否充分

Round 3: 综合裁决
  若2轮未达共识: Owner介入裁决
  若达成共识: 综合方案 = A方案 + B改进建议
```

### 73.3 模型能力图谱与加权

| 模型 | 代码生成 | 架构设计 | 安全审计 | 金融领域 | 综合权重 |
|------|:--:|:--:|:--:|:--:|:--:|
| Claude Sonnet 4 | 0.85 | 0.90 | 0.95 | 0.70 | 0.85 |
| DeepSeek-V4-Pro | 0.80 | 0.75 | 0.65 | 0.60 | 0.70 |
| DeepSeek-R1 | 0.65 | 0.80 | 0.55 | 0.65 | 0.66 |

```
加权得分 = Σ w_model × score_model
投票阈值: 加权分 > 0.70 → 通过
```

### 73.4 异议升级路径

| 异议严重性 | 模型分歧程度 | 行动 |
|:--:|------|------|
| 低 | 风格/命名差异 | Auto-merge——选高权重模型方案 |
| 中 | 实现路径不同但目标一致 | Owner 看一眼→选一个 |
| 高 | 架构/安全性根本分歧 | Owner 必须参与——不能 AI 自决 |
| 关键 | 触及交易逻辑/资金安全 | 🛑 AI 冻结——Owner 全面审查 |

---

## 七十四、AI 代码生成标准与项目脚手架

> **定位**：AI 生成代码最大的质量问题不是 bug——是风格不一致、命名混乱、导入随意。需要强制性脚手架和约定——AI 读到规则后自动纠正。
> **对标**：Google Style Guides + Black/Ruff Auto-format + Cookiecutter Templates。

### 74.1 文件级约定 (AI MUST 遵守)

```yaml
项目约定 (自动注入到每个 session):
  naming:
    files: "snake_case.py"         # 不是 kebab-case 或 camelCase
    classes: "PascalCase"          # 不是 snake_case
    functions: "snake_case"        # 不是 camelCase
    constants: "UPPER_SNAKE_CASE"  # 不是 PascalCase
  
  imports:
    order: ["stdlib", "third_party", "zephyr_internal"]
    style: "absolute_imports_only"  # 禁止相对导入 from . import
    forbidden: ["from module import *"]
  
  typing:
    all_public_functions: "MUST have type annotations"
    all_public_classes: "MUST have type annotations"
    return_type: "MUST be explicit (no -> None省略)"
```

### 74.2 模块脚手架模板

```
新模块创建时 AI 自动生成:
  src/zephyr/lXX_module_name/
    ├── __init__.py          # 模块导出声明
    ├── core.py              # 核心逻辑
    ├── models.py            # 数据模型 (dataclass/Pydantic)
    ├── config.py            # 配置参数
    ├── exceptions.py        # 自定义异常
    ├── utils.py             # 内部工具函数
    ├── tests/
    │   ├── __init__.py
    │   ├── test_core.py
    │   └── test_integration.py
    └── README.md            # (Optional) 模块自述
```

### 74.3 代码注释标准 (AI 生成代码头)

```
每个 AI 生成的文件头部:
  # -*- coding: utf-8 -*-
  # @ai-generated: true
  # @model: deepseek-v4-pro
  # @session: session-20260505-001
  # @prompt-ref: .zeph/prompts/tasks/factor_new.prompt@1.2.0
  # @review-level: L3 (§五十四)
```

### 74.4 禁止模式自动检测

| 禁止模式 | 检测工具 | 阻断 |
|------|------|:--:|
| `import *` | ruff F403/F405 | 🔴 |
| 裸 `except:` | ruff E722 | 🔴 |
| 未使用的 import | ruff F401 | 🟡 |
| 可变默认参数 `def f(x=[])` | ruff B006 | 🔴 |
| `print()` 用于日志 | ruff T201 | 🟡 |
| `os.system()` | bandit B605 | 🔴 |
| `eval()` / `exec()` | bandit B307 | 🔴 |

---

## 七十五、实盘交易五级 Kill Switch 与安全保障矩阵

> **定位**：§六十六 有 Feature Flag 和 Kill Switch，但部署安全 ≠ 交易安全。需要一个真正的五级 Kill Switch——从单仓位到全系统，每一级有不同的触发条件和恢复规则。
> **对标**：Two Sigma Kill Switch Hierarchy + Interactive Brokers Risk Controls + CME GC2 Global Circuit Breakers。

### 75.1 五级 Kill Switch

| 级别 | 范围 | 触发条件示例 | 恢复规则 |
|:--:|------|------|------|
| L1 | 单仓位 | ±3σ单笔滑点 / 单仓位亏>AUM×2% | Owner确认→手动恢复 |
| L2 | 单策略 | 策略30min内>5笔异常 / Sharpe(滚动)≤-1 | 策略审查(§65)→Owner恢复 |
| L3 | 单资产类 | 同资产3+策略异常 / 对应市场异常波动 | 资产类级别审查→恢复 |
| L4 | 全自动交易 | 账户日亏>5% / 2个以上L3触发 | Owner 24h冷静期→恢复 |
| L5 | 全系统(含手动) | 账户周亏>15% / 关键安全漏洞 | 需要ADR记录+外部审查 |

### 75.2 盘前安全检查清单 (每日 08:30 自动执行)

```
☐ V1: 所有数据源连通——行情/经纪商/日历
☐ V2: 无未处理的事故——§二十 L1-L5 Dashboard 清空
☐ V3: 经纪商余额确认——现金 ≥ 最低保证金+缓冲
☐ V4: 无强制平仓通知——保证金/风控指标
☐ V5: Feature Flag 状态确认——所有 Kill Switch: OFF
☐ V6: 交易日历确认——今天正常交易日?(§五十八)
☐ V7: 重要事件日历——FOMC/非农/财报(若适用)
☐ V8: 系统健康面板全绿——§0.0 全SLI在SLO内
结果: 8/8 ☐ → GO, <8 → 🛑 NO-GO + Owner评估
```

### 75.3 盘中异常自动响应矩阵

| 异常事件 | 响应 | 延迟 |
|------|------|:--:|
| 单笔成交价格偏差 >2% | <PAUSE> 策略 + <ALARM> | <500ms |
| 30秒内 >5笔异常 | <PAUSE> 资产类 | <1s |
| 经纪商连接断开 | 切换Secondary(§51) + <ALARM> | <5s |
| 行情数据断流 >10s | 🛑 全暂停+等待恢复 | <1s |
| 系统内存/CPU >95% | Shed Load(§63.1)→T3降级 | <1s |
| 检测到疑似AI幻觉代码执行 | 🛑 L4级全冻结 | 即时 |

### 75.4 收盘后自动对账五步

```
Step 1: 经纪商持仓 vs 系统记录 → diff=0?
Step 2: 成交明细 vs 订单指令 → 无遗漏/无幽灵单?
Step 3: 佣金/费用核对 → 与预期偏差<10%?
Step 4: PnL 归因四维(§61.1) → 无"无法解释"PnL?
Step 5: Immutable Audit Log 写入 → 当日全部操作完整?
```

---

## 七十六、模拟盘→实盘过渡与资金渐进协议

> **定位**：模拟盘到实盘不是一次开关——是分阶段逐步建立信任的过程。每一步可回退。
> **对标**：Two Sigma Graduated Launch + D.E. Shaw Strategy Promotion + IB Paper→Live Best Practices。

### 76.1 五阶段过渡协议

| 阶段 | 时长 | 资金 | 行为 | 晋级条件 |
|:--:|:--:|:--:|------|------|
| S1: 纯回测 | ≥3月OOS | $0 | 回测验证(§四十八)——WFO+DSR+无泄漏 | OOS Sharpe≥1.0 + DSR<0.05 |
| S2: 模拟盘影子 | ≥1月 | $0 | 虚拟实时跟跑——逐日对比模拟vs实盘(§53) | ρ(模拟, 实盘日PnL)≥0.7 |
| S3: 微型实盘 | ≥2周 | 0.5% AUM | 1×杠杆(§56.3 Warm-up P1)——仅最流动品种 | 模拟-实盘FF(§64.2)≥0.5 |
| S4: 部分实盘 | ≥1月 | 10% AUM | 0.5×杠杆(P2)——扩展至策略全集合 | 滚动30日Sharpe≥0.5 |
| S5: 全量实盘 | 稳定期 | Target AUM% | 按Vol Target(§56)正常运行 | 持续监控 |

### 76.2 过渡回退触发器

| 在任何阶段: | 触发条件 | 回退到 |
|------|------|:--:|
| 模拟-实盘 ρ < 0.3 | 模拟盘与实盘严重背离 | S1——重新验证回测 |
| 实盘 Sharpe < -0.5 (滚动7日) | 实盘严重亏损 | S2——回到模拟盘观察 |
| S3 实盘滑点是模拟 ×3 | 交易成本模型严重低估 | S1——重新校准滑点模型 |
| Owner 主观中止 | 任何原因 | 前一阶段 |

### 76.3 跨策略上线互斥规则

```
MUST: 同一时间最多1个策略在 S3/S4 过渡中
      必须等上一个策略到 S5 稳定运行≥30天后
      才能启动下一个策略的过渡流程
原因: 1人+AI 无法同时监控多个过渡中的策略
```

---

## 七十七、订单执行质量监控与异常检测

> **定位**：不只是"订单发出去了"——需要 AI 自动检测异常成交模式(价格异常/部分成交异常/延迟异常)并对执行场所进行量化评分。
> **对标**：ITG/Abel Noser TCA + Hudson River Execution Quality + Interactive Brokers SmartRouting Analytics。

### 77.1 四维执行异常检测 (ML+规则混合)

| 异常类型 | 检测方法 | 阈值 |
|------|------|:--:|
| 成交价格异常 | Z-score = (fill_price − expected_range_center) / σ_range | \|Z\|>3→异常 |
| 部分成交率异常 | 实际填充率 < 历史平均 2σ 以下 | <40% and >2σ |
| 延迟异常 | 订单发送→首次ACK延迟 > P95历史+2σ | >95%ile×1.5 |
| 拒绝率突增 | 最近30min拒绝率 > 历史基线×3 | >15%→冻结策略 |

### 77.2 执行场所/经纪商质量评分

| 评分维度 | 权重 | 计算 |
|------|:--:|------|
| 成交率 | 0.25 | 成交量/发送量——滑点调整(true fill) |
| 价格改善 | 0.25 | (VWAP−avg_fill)/VWAP, 正=改善 |
| 延迟 | 0.20 | avg/P99 订单→成交延迟 |
| 拒绝率 | 0.15 | 拒绝/发送 |
| 费用效益 | 0.15 | 佣金+费用/PnL |
| **Quality Score < 0.6** | — | 考虑切换经纪商(§51) |

### 77.3 结算监控

```
T日结算: 成交→T+1 确认→T+2 资金到账(股票)
T日检查:
  ☐ T-2成交, T日是否已到账?
  ☐ 是否有 pending settlement >5天?
  ☐ 是否有 settlement failure 记录?
```

---

## 七十八、知识连续性与断供因子防护

> **定位**：1个人也可能会摔倒/生病/断网/遗忘。系统必须在没有 Owner 的情况下仍能被另一个人接手。断供因子(Bus Factor)应该在系统启动时就设计进去。
> **对标**：Bus Factor Risk Assessment + GitLab TeamOps + Apache Software Foundation Governance。

### 78.1 断供因子度量

```
Bus Factor = min(关键知识仅1人掌握的组件数, 5)
当前预估: Bus Factor = 1 (危险——所有知识在1人脑中)

目标: Bus Factor ≥ 3
  - 至少3个人/实体能在48h内接手系统
  - 在1人场景下: 1人 + 完整AI文档 + 1个备份联系人
```

### 78.2 AI 自动生成接手手册 (AUTO_ONBOARD)

```
触发: 每次重大架构变更后自动生成
输出: .zeph/onboarding/QUICKSTART.md

内容:
  1. 系统概览 (1页——这是什么系统?)
  2. 启动步骤 (从 git clone 到全量测试全绿)
  3. 关键决策记录 (最近10个 ADR)
  4. 当前运行状态 (什么在跑, 用什么资金)
  5. 紧急联系人/操作 (券商/数据源/银行)
  6. 90天维护日志 (最近做了什么?)
```

### 78.3 知识资产清单

| 知识资产 | 类型 | 存储位置 | 谁可读 | 过期风险 |
|------|------|------|------|:--:|
| 系统架构原理 | 蓝图体系 | docs/ | AI+Owner | 低——蓝图自动维护 |
| ADR 决策推理 | ADR 文件 | architecture-rationale-log.md | AI+Owner | 中——需要及时记录 |
| 调试经验/坑 | Session Handover | sessions/ | AI+Owner | 高——需要从 session 提取 |
| API 密钥/凭证 | Secrets | 1Password(§69) | Owner only | 低——有轮替 |
| 联系人/账号 | Vendor list | .zeph/contacts.yaml | Owner only | 中——需手动维护 |
| Owner 脑中隐性知识 | 脑内 | ⚠️ 无记录 | 只有 Owner | 🔴 最高风险 |

### 78.4 Owner 隐性知识提取计划

```
每周 1 次: 15分钟 "Brain Dump Session"
  AI 提问: "这周有没有做了蓝图里没写的决策?"
  "有没有发现什么需要注意的坑?"
  "有没有什么你懂但AI不知道的市场逻辑?"
  → AI 自动转换为 KB entries + ADR (如需要)
```

---

## 七十九、本地优先架构与离线自主运行

> **定位**：100% AI 施工可以离线；交易监控应该离线可运行。不能因为 DSL 断了就停摆。本地数据应该完整自给。
> **对标**：Local-First Software Manifesto + CouchDB/PouchDB + Google Docs Offline Mode。

### 79.1 离线能力五级

| 级别 | 功能 | 离线状态 |
|:--:|------|:--:|
| L1 | AI 辅助代码开发 (读蓝图+生成代码+测试) | ✅ 全离线——本地模型或缓存 |
| L2 | 回测/因子研究 (本地历史数据充足) | ✅ 全离线——数据已同步 |
| L3 | 模拟交易 (使用本地历史行情回放) | ✅ 全离线——Clock用历史时间 |
| L4 | 实盘监控 (只读——查看持仓/PnL) | ❌ 需要行情/经纪商连接 |
| L5 | 实盘交易 (下单/撤单/风控) | ❌ 必须在线 |

### 79.2 离线恢复同步协议

```
恢复连接后:
  1) 比对本地产出 vs 远程状态——识别离线期变更
  2) 合并冲突: 远程状态优先(交易安全)
  3) 补同步: 离线期生成的因子/回测结果→推送到DB
  4) 日志补齐: 离线期 telemetry→批量上报
```

### 79.3 数据本地化要求

```
MUST:
  所有 L1 公开数据(§十三): 本地完整副本
  所有 L2 内部数据: 本地完整副本+WAL
  所有代码+蓝图+测试: 本地(本就如此)
  所有依赖(pip包): 本地cache

SHOULD:
  最近30天 L3 敏感数据: 本地加密副本(紧急查看)

FORBIDDEN:
  L4 密钥数据: 永远不缓存本地明文
```

---

## 八十、决策疲劳管理与 Owner 优先级分流

> **定位**：1个人每天能做的优质决策有限(心理学研究: ≈3-5个重大决策/天)。AI 必须承担分流——把 Owner 从"每件事都要想"中解放出来。§四十六 覆盖了 Burnout 预防，但未覆盖决策质量本身。
> **对标**：Daniel Kahneman Decision Fatigue + Barack Obama Decision Simplification + MakeTime Framework。

### 80.1 决策四级分流

| 等级 | 描述 | 谁决策 | 每日期望数量 |
|:--:|------|:--:|:--:|
| D1: AI 自主 | 格式/命名/简单重构/测试生成 | AI 自动 | ≤30 |
| D2: AI 建议→Owner 扫一眼 | 中等重构/架构微调/因子参数 | AI→Owner确认 | ≤8 |
| D3: Owner 主决策 | 策略上线/架构变更/安全审查 | Owner | ≤3 |
| D4: 延迟决策 | 非紧急大型决策 | 标记→周度Review | ≤3/周 |

### 80.2 AI 决策预摘要卡片

```
每个需要 Owner 决策的事项:
  ┌────────────────────────────────
  │ Decision Card #DC-2026-0505-01
  │ 问题: 是否上线因子 momentum_12m_v2?
  │ 影响: 策略 Sharpe (回测 +0.15)
  │ 风险: 过拟合可能(DSR=0.04——borderline)
  │ AI建议: 推迟至2周OOS验证后上线
  │ 紧急度: Low (下一决策窗口: 周五)
  │ [APPROVE] [REJECT] [DEFER] [ASK]
  └────────────────────────────────
```

### 80.3 决策时间窗口

```
交易日:
  08:30-09:00: 盘前检查决策(D2+D3)
  09:30-16:00: 仅交易快决策(<PAUSE>/<RESUME>/<ALARM>——D1)
  16:00-17:00: 零决策——让大脑休息
  17:00-18:00: 盘后决策窗口(D2+D3, 最多1个D3)

非交易日:
  上午: D3 重大决策窗口 (10:00-12:00, 2h黄金时段)
  下午: D2 批量确认 (批量扫一眼——连续确认)
```

### 80.4 决策日志与模式检测

```
每周: AI 分析 Owner 决策模式
  检测: 是否总是 APPROVE? (过度信任)
        是否总是 REJECT? (过度保守)
        是否有决策后悔? (REVERT后分析原因)
        决策是否遵循了蓝图原则?
```

---

## 八十一、What-If 仿真与灵敏度分析引擎

> **定位**：回测是"从过去看未来"——仿真引擎是"如果X变了会怎样"。Two Sigma 大量使用 Monte Carlo 和应力仿真来理解策略的边界条件。
> **对标**：Two Sigma Scenario Engine + Bloomberg MARS + RiskMetrics Stress Testing。

### 81.1 参数灵敏度扫描

```
灵敏度分析 (每个上线策略 MUST):
  滑动每个参数 ±20%, 步长5%
  
  Parameter         -20%    -15%    ...    0%    ...    +15%    +20%
  ───────────────────────────────────────────────────────────────
  lookback_window   Shar=1.1  Shar=1.3  Shar=1.5  Shar=1.6  Shar=1.5
  entry_threshold   Shar=1.8  Shar=1.7  Shar=1.5  Shar=1.0  Shar=0.5
  stop_loss_pct     Shar=1.6  Shar=1.5  Shar=1.5  Shar=1.4  Shar=0.3
  
  判定:
    lookback_window: Robust (Sharpe波动小)
    entry_threshold: 🔴 高度敏感——参数选择极关键
    stop_loss_pct:  Moderate
  
  敏感参数: 必须做额外OOS验证
```

### 81.2 Monte Carlo 路径生成

```
基于历史分布特征生成10000条合成路径:
  输入: 历史收益率分布的μ/σ/偏度/峰度+相关性矩阵
  方法: Cholesky分解→相关随机序列→合成价格路径
  输出:
    - VaR/CVaR 置信区间
    - MaxDD 分布 (不是单一值, 是分布!)
    - 破产概率 (Path中AUM≤0的概率)
    
  阀值: 破产概率 > 0.01 → 策略需要调整
```

### 81.3 反事实回测

```
Counterfactual Analysis:
  "如果当时没做这笔交易会怎样?"
  "如果当时杠杆是0.5x而不是1x?"
  "如果当时止盈更早/更晚?"

  用途: 不只是看"赚了多少"——看"赚对了没有"
```

---

## 八十二、AI 辅助代码考古与文档自动化

> **定位**：随着系统增长(70章→90章, 代码行数指数级增长), 任何人(包括Owner)都无法记住所有决策。AI必须能自动回答"这段代码为什么这样写"。
> **对标**：Google Code Search + Sourcegraph Cody + GitLens + GitHub Copilot Chat。

### 82.1 代码考古四问

```
对任何代码段, AI 应能在 <10s 内回答:
  Q1: "为什么这段代码存在?" → Git blame + commit message + linked ADR
  Q2: "什么时候创建的?" → first commit date + 上下文
  Q3: "谁/哪个AI写的?" → AI provenance header(§74.3)
  Q4: "有没有相关的讨论/ADR?" → commit message 关联 ADR/task
```

### 82.2 AUTO-DOC 自动文档生成

```
每次 merge 到 main:
  1) AI 自动生成: CHANGELOG.md 条目 (从 commits 摘要)
  2) AI 自动生成: API docs (从 type annotations + docstrings)
  3) AI 自动生成: 模块依赖图更新
  4) AI 自动检测: 死代码 (import 但从未调用/类从未实例化)
```

### 82.3 死代码退役流程

```
检测到死代码:
  1) AI 标记: @deprecated + 指向替代方案
  2) 等待期: 30天(确保不是"以后会用到")
  3) AI 自动: 生成 PR 移除死代码
  4) Owner: APPROVE→merge
```

---

## 八十三、市场数据源可靠性评分与智能切换

> **定位**：§二十九 定义了数据质量检查(完整性/及时性/有效性/一致性), 但缺少"数据源本身的信用评级"——这个源历史表现如何? 是否在衰退?
> **对标**：Bloomberg Data Quality Scoring + Morningstar Data Reliability + Exchange Data Certification。

### 83.1 数据源可靠性五维评分

| 评分维度 | 权重 | 测量 |
|------|:--:|------|
| 可用性 Uptime | 0.25 | 过去90天可用率 |
| 准确性 Accuracy | 0.30 | 与可信基准源交叉验证 |
| 及时性 Timeliness | 0.20 | 数据延迟 vs 预期 |
| 完整性 Completeness | 0.15 | 缺数据比例 |
| 一致性 Consistency | 0.10 | 同字段值的历史稳定性 |
| **Reliability Score** | — | 加权总分 ∈ [0, 1] |

### 83.2 源衰退预警

```
检测: Reliability Score 连续30天下降 >0.1
      或单次大幅跳降 >0.2

响应:
  🟡 预警: 源质量衰退——开始准备切换
  🔴 紧急: 源质量 <0.6——立即切换+Offline Data补齐
```

### 83.3 智能源切换决策

```
切换逻辑:
  IF current_source.reliability < 0.7 THEN
    查看备选源: backup_source.reliability > current + 0.1?
    YES → 平滑切换(双源并行3天→切)
    NO → 保持当前源 + Owner通知

数据补齐:
  切换导致的数据缺口:
    优先用 cross-validation 填补(另一源交叉验证)
    其次用 interpolation(时间序列插值)
    最后标记为 `ESTIMATED`——不能无声填充
```

---

## 八十四、混沌工程与自动故障演练

> **定位**：不等事故来测试系统——主动注入故障来验证韧性。专业量化机构会定期做"宕机演练"。
> **对标**：Netflix Chaos Monkey/Chaos Kong + AWS Fault Injection Simulator + Gremlin。

### 84.1 五类故障注入

| 故障类型 | 注入方式 | 频率 |
|------|------|:--:|
| 网络: 数据源断连 | 临时 iptables/Windows Firewall 阻断 | 每周 1次 |
| 网络: 经纪商 API 超时 | 代理延迟/超时注入 | 每周 1次 |
| 资源: CPU 超载 | 启动 CPU 压力进程→占80% | 每月 1次 |
| 资源: 磁盘满 | 创建大文件→磁盘填充 >90% | 每月 1次 |
| 数据: 行情数据损坏 | 注入 NaN/异常值/未来日期 | 每月 2次 |

### 84.2 自动故障演练日历

```
每周日 14:00 UTC (非交易时段):
  1) 启动沙箱环境 (不是实盘!)
  2) 逐项演练 5类故障
  3) 记录: detect_time / response_time / recovery_time
  4) 对比基线: 本周 MTTR vs 上周 MTTR
  5) 恶化: MTTR 上升 >20%→Owner审查
```

### 84.3 演练失败升级

```
演练中检测到系统未按预期响应:
  - 断路器未触发
  - 告警未发送
  - 降级策略未生效
  - 数据切换超时>2×SLO

  → 生成 FMEA 补充条目(§十六)
  → Owner 审查+加固
  → 下次演练重复验证
```

---

## 八十五、经济体制检测与宏观因子覆盖

> **定位**：量化策略的最大杀手不是技术故障——是市场体制变化(Regime Change)。§四十二 有 HMM 状态检测但仅限3个内部状态。需要独立的外部宏观因子体系。
> **对标**：Bridgewater Economic Regime Model + AQR Macro Factor Suite + Two Sigma Alternative Data。

### 85.1 五维宏观因子框架

| 宏观因子 | 代理指标 | 更新频率 |
|------|------|:--:|
| 经济增长 | PMI, GDP nowcast, 工业用电 | 月度+日度 nowcast |
| 货币政策 | Fed Funds Rate, 央行资产负债表, 利率期货隐含概率 | 日度 |
| 通胀 | CPI/PCE + TIPS 盈亏平衡通胀 + 商品指数 | 月度+日度 |
| 信用条件 | HY-OAS 信用利差, IG spread, CDX | 日度 |
| 风险偏好 | VIX term structure, SKEW, 资金流动 | 日度 |

### 85.2 宏观体制映射

| 宏观体制 | 条件组合 | 偏好的因子/策略 |
|------|------|------|
| 扩张(Expansion) | 增长↑/通胀稳/信用宽/风险偏好↑ | Momentum+Growth+SmallCap |
| 滞胀(Stagflation) | 增长↓/通胀↑/信用紧 | Commodities+Quality+LowVol |
| 紧缩(Tightening) | 货币政策紧/信用收窄 | Cash+ShortDuration+Defense |
| 危机(Crisis) | 信用爆/风险偏好↓/波动↑ | Cash+Gold+Volatility long |

### 85.3 体制切换预警

```
Pre-Regime Change Signals (提前1-4周):
  ☐ 信用利差开始扩大 (≥ +1σ)
  ☐ VIX 期货升水转贴水 (term structure inversion)
  ☐ 国债期限利差倒挂或变陡
  ☐ 央行发言转向
  
  3/4 触发 → 体制切换预警 → 
    ① 策略权重重新校准
    ② 减仓敏感资产
    ③ Owner 通知
```

---

## 八十六、AI 决策可解释性与监管审计深度

> **定位**：当 AI 生成了一笔交易决策，Owner 和(理论上的)监管机构需要理解"为什么"。不仅是合规要求，更是信任和调试的基础。
> **对标**：D.E. Shaw Model Documentation + MiFID II Algorithmic Trading Disclosure + EU AI Act。

### 86.1 AI 交易决策解释链

```
每笔 AI 生成的交易决策 MUST 附带:
  {
    "trade_id": "TRD-20260505-0042",
    "decision": "BUY 1000 AAPL @ LIMIT 185.50",
    "ai_reasoning": {
      "primary_signal": "momentum_1m score=0.78 (threshold=0.70)",
      "contributing_factors": ["vol_30d=-0.3σ", "RSI=42(oversold)"],
      "regime_context": "Bull(probability=0.85)",
      "risk_constraints": "Position=12%<25% max, VaR=1.2%<2% limit",
      "timestamp": "2026-05-05T10:23:45.123Z"
    }
  }
```

### 86.2 模型卡自动生成

```yaml
# 每个上线模型 MUST 有 MODEL_CARD.yaml
model_id: "momentum_1m_v2"
type: "alpha_factor"
owner: "ZephyrAlpha-Owner"
intended_use: "A股日频选股——动量因子"
training_data: "2016-01-01 to 2024-12-31, CSI800成分股"
limitations:
  - "小盘股(市值<50亿)表现差"
  - "高波动市场中信号延迟"
  - "牛市表现远好于熊市"
fairness_considerations: "N/A (非个人化决策)"
last_reviewed: "2026-05-05"
review_cadence: "每季或体制切换后"
```

### 86.3 监管审计就绪

```
Audit Readiness Check (每季):
  ☐ 所有交易有完整审计追踪? (§47.1)
  ☐ 所有 AI 策略有 MODEL_CARD?
  ☐ 所有 AI 代码有 provenance? (§74.3)
  ☐ 最近事故有完整 RCA? (§二十)
  ☐ 第三方数据源有合规记录?
  ☐ 系统安全扫描结果存档?
```

---

## 八十七、SBOM 生成与依赖情报

> **定位**：§二十八 有供应链安全但不够系统化。专业实践需要完整的 SBOM(Software Bill of Materials)、依赖健康评分和自动化升级建议。
> **对标**：CycloneDX/SPDX SBOM Standard + Dependabot + Snyk + OpenSSF Scorecard。

### 87.1 SBOM 自动生成

```yaml
# .zeph/sbom/sbom-2026-05-05.cdx.json (CycloneDX 格式)
生成频率: 每次 pip install 变更后自动生成
内容:
  - 所有直接+传递依赖列表
  - 每个依赖的版本+许可证+hash
  - 已知漏洞(CVE)关联
  
AI MUST 在添加新依赖前:
  1) 检查 SBOM 中是否已有类似功能依赖(避免重复)
  2) 评估许可证兼容性
  3) 检查已知漏洞
  4) Owner 知悉(新依赖=新风险)
```

### 87.2 依赖健康五维评分

| 维度 | 权重 | 评分标准 |
|------|:--:|------|
| 维护活跃度 | 0.30 | 最近commit <30天? issue响应<7天? |
| 安全记录 | 0.25 | 最近1年CVE数量+严重程度 |
| 社区规模 | 0.15 | GitHub stars/contributors/downloads |
| 许可证兼容 | 0.20 | MIT/Apache2/BSD ✓, GPL ⚠️, 无许可证 🔴 |
| 版本稳定性 | 0.10 | v1.0+ & 无breaking change频繁 |

### 87.3 依赖升级自动化

```
每周: AI 扫描所有依赖
  有更新 → AI 生成 PR + changelog 分析 + 测试全跑
  
  自动合并条件:
    patch 版本 (1.0.x→1.0.y): 测试全绿 → Auto-merge
    minor 版本 (1.x→1.y): 测试全绿 + Owner扫一眼 → merge
    major 版本 (x.0→y.0): 绝不自合并 → Owner审查
```

---

## 八十八、状态机形式化与正确性验证

> **定位**：多处提到状态机(OMS §41.3, 断路器 §45.4, FeatureFlag §66.1, KillSwitch §75.1)但缺少统一的描述标准和验证方法。
> **对标**：UML Statecharts + TLA+ Formal Verification + AWS Step Functions + XState。

### 88.1 统一状态机描述规范

```yaml
# zephyr-standard state machine format
statemachine:
  id: "oms_order_lifecycle"
  version: "1.0.0"
  states: [PENDING, ACK, PARTIAL_FILL, FILLED, REJECTED, CANCELLED]
  initial: PENDING
  terminal: [FILLED, REJECTED, CANCELLED]
  transitions:
    - {from: PENDING, to: ACK, on: "broker_ack"}
    - {from: ACK, to: PARTIAL_FILL, on: "partial_execution"}
    - {from: PARTIAL_FILL, to: FILLED, on: "remaining_executed"}
    - {from: PENDING, to: REJECTED, on: "broker_reject"}
    - {from: [PENDING, ACK, PARTIAL_FILL], to: CANCELLED, on: "cancel_request"}
  invariants:
    - "max one transition per event"
    - "no transition from terminal states"
    - "order_id unique across all live states"
```

### 88.2 状态转换测试自动生成

```
从 YAML spec 自动生成测试:
  for each transition:
    test_CAN_transition_<from>_to_<to>_on_<event>()
  
  for each invalid transition:
    test_CANNOT_transition_<from>_to_<to>

  边界:
    test_no_transition_from_<terminal_state>()
```

### 88.3 崩溃后状态协调

```
系统崩溃恢复后:
  1) 读取 WAL/Journal——最后已知合法状态
  2) 查询外部源：经纪商回执→真实状态
  3) 对比: WAL_state vs broker_state
     一致 → 恢复运行
     不一致 → broker_state 为准 + 写入事故日志(§二十)
  4) 检查所有活跃实体的状态一致性
```

---

## 八十九、DORA 指标与开发速率度量

> **定位**：不能只度量 AI(WQA §39, SPC §60)——也需要度量整个系统开发流水线的健康度。DORA 四指标是行业标准。
> **对标**：Google DORA Metrics + Accelerate State of DevOps + LinearB + Waydev。

### 89.1 DORA 四指标 + AI 特有指标

| 指标 | 目标(精英级) | 测量方法 |
|------|:--:|------|
| 部署频率 (DF) | ≥1次/天 | 每日 main 分支 merge 次数 |
| 变更前置时间 (LT) | <1小时 | commit→production 时间 |
| 变更失败率 (CFR) | <5% | (需要回滚的部署)/(总部署) |
| 失败恢复时间 (MTTR) | <1小时 | 从检测到恢复的分钟数 |

### 89.2 AI 特有开发速率指标

| 指标 | 目标 | 说明 |
|------|:--:|------|
| AI Velocity | ≥3 commits/session | 每 session 有效产出 |
| AI Acceptance Rate | ≥70% | Owner APPROVE / AI 总提交 |
| AI Rework Rate | <20% | Owner 要求修改的比例 |
| Session Efficiency | >0.6 | WQA 综合评分(§39) |

### 89.3 速率健康面板

```
月度速率报告 (自动生成):
  ┌────────────────────────────────────
  │ 2026年5月 开发速率报告
  │
  │ 部署: 22次 (↓5% vs上月)
  │ 新增代码: 3,420行 AI生成 + 180行人工
  │ AI Accept: 78% (↑3%)
  │ 回滚: 2次(9%) ← ⚠️ 接近5%红线
  │ 平均 Cycle Time: 3.2h
  │
  │ 瓶颈分析: 代码审查环节——Owner审查延迟中位数=4h
  └────────────────────────────────────
```

---

## 九十、A/B 实验框架与统计严谨性

> **定位**：§四十八 有策略验证的统计严谨性, L13 标记了 Experimentation 但只是骨架。需要一个完整的 A/B 实验框架——不只是回测，是"策略 A vs 策略 B"的科学比较。
> **对标**：Google/Amazon A/B Testing Framework + Optimizely + Evidently AI。

### 90.1 实验设计模板

```yaml
experiment:
  id: "EXP-2026-0505-01"
  hypothesis: "将动量因子 lookback 从12月调整为6月可提升 Sharpe 0.15"
  variants:
    control: "momentum_12m (当前线上)"
    treatment: "momentum_6m (实验)"
  metrics:
    primary: "Sharpe ratio (rolling 30d)"
    secondary: ["MaxDD", "Turnover", "PnL/Market correlation"]
  duration: "≥30个交易日'或'统计显著'"
  sample_size_requirement: "min 200 signals per variant"
```

### 90.2 统计显著性计算

```
参数:
  α = 0.05 (Type I error)
  β = 0.20 (80% power = 1-β)
  MDE = 0.15 Sharpe (最小可检测效应)

所需样本:
  n ≈ 2(Z_α/2 + Z_β)²·σ² / MDE²
  
规则:
  达到所需样本前: 🛑 不能停止——防止偷窥(peeking)
  达到统计显著(p<0.05): 可提前结束
  达到最大时长(60天)未显著: 接受原假设——无差异
```

### 90.3 实验结果记录

```
每次实验 MUST 记录:
  ☐ 实验设计 (hypothesis/methods/metrics)
  ☐ 原始数据 (daily PnL per variant)
  ☐ 统计检验结果 (p-value/置信区间/效应大小)
  ☐ 结论 + 是否上线
  ☐ 事后跟踪 (上线后30d实际 vs 预期?)

所有实验存档到: .zeph/experiments/EXP-YYYY-MMDD-NN.yaml
  不可删除——防止"只有成功的实验被记住"
```

---
---
## 九十一、企业行为与参考数据管线

> **定位**：拆分、分红、并购、退市、更名、代码变更——企业行为是量化系统最容易被忽视、但出错后果最严重的数据域。一次未处理的分红=因子计算错误=信号失真=回测无效=实盘亏损。专业量化机构有专门的 Corporate Actions 团队。
> **对标**：Bloomberg CAES/Corporate Actions + SEC EDGAR + JP Morgan Reference Data + S&P GICS Change Tracking。

### 91.1 七类企业行为必须处理

| 企业行为 | 影响 | 处理方式 | 优先级 |
|------|------|------|:--:|
| 现金分红 | 价格除权→return误算 | 复权价格(前复权/后复权)+累计分红因子 | 🔴 P0 |
| 股票拆分/合股 | 价格×N→量÷N——所有历史价格移位 | 调整因子(adjustment_factor)统一 | 🔴 P0 |
| 送股/配股 | 股本增加→价格稀释+仓位被动变化 | 除权价计算+股数调整 | 🔴 P0 |
| 并购/收购 | 标的不复存在→持仓突然消失 | 现金/换股比例→模拟平仓价格 | 🟡 P1 |
| 退市 | 无法交易→隐含损失=100% | 检测+告警+Owner确认处理 | 🟡 P1 |
| 代码变更 | TS代码→因子指向失效→静默数据丢失 | 代码映射表(symbol_map)+自动redirect | 🔴 P0 |
| 行业分类变更 | GICS变化→行业归因错位 | 日级GICS code tracking(§61.1) | 🟡 P1 |

### 91.2 企业行为数据管线

```
Pipeline:
  Source: akshare/baostock → 企业行为事件(raw)
  ↓
  Validator: 事件完整性(是否漏了分红日?) + 交叉验证(多源比对)
  ↓
  Transform: 复权因子(bwd_adj_factor / fwd_adj_factor) → time series
  ↓
  Apply: 所有价格列×adj_factor → 因子重算 → 特征存储更新(§42.1)
  ↓
  Verify: 随机10只股票×5次行为→价格是否正确?
```

### 91.3 每日自动检查

```
盘前 (08:00):
  ☐ 今日是否有除权除息事件? → 列表→预加载adj_factor
  ☐ 今日是否有代码变更? → 更新 symbol_map
  ☐ 昨日是否有退市公告? → Owner notification
  ☐ 本月是否有股东大会(关联并购)? → Owner notes
  ☐ adj_factor 序列连续性(无跳跃)? → PctChg<50% day-over-day
```

### 91.4 回溯修复协议

```
发现企业行为数据错误(<T-7以内):
  1) 修复源数据
  2) 重算受影响区间(≥T-7→T today)的复权因子
  3) 全部受影响因子+信号重跑
  4) 回测结果重新计算+对比前版本→Δ报告→Owner审阅
```

---

## 九十二、热重启与盘中故障恢复协议

> **定位**：§十四 定义了冷启动6Phase拓扑，但盘中故障——系统崩溃、进程僵死、强制重启——需要完全不同的恢复策略。冷启动=一切从零初始化；热重启=保留盘中状态+最小化数据丢失+快速恢复交易能力。
> **对标**：Jane Street In-Flight Recovery + K8s CrashLoopBackOff + PostgreSQL WAL Recovery。

### 92.1 冷启动 vs 热重启

| 维度 | 冷启动 (§十四) | 热重启 (本节) |
|------|------|------|
| 触发 | 每日首次启动、系统完全停机 | 盘中崩溃/进程僵死/强制kill |
| 已有状态 | 无 (从零开始) | 有——持仓/订单/信号缓存 |
| 时间容忍 | ≤60s 总启动 | ≤30s 恢复交易能力 |
| 数据来源 | 数据库全量读取 | WAL+检查点+外部源同步 |
| 最大风险 | 数据源连接失败 | 状态不一致——WAL≠真实世界 |

### 92.2 热重启六步协议

```
Step 1: Freeze Check (<2s)
  读取崩溃前最后 checkpoint hash → 验证完整; corrupt? → 前一个checkpoint

Step 2: State Reconciliation (<5s)
  WAL最后状态 : broker当前状态
  不一致 → broker为准 (§88.3)
  标记: 崩溃时 in-flight 的订单 → [UNCERTAIN] → 人工确认

Step 3: Connection Recovery (<10s)
  重新建立 行情+经纪商+数据库 连接
  fail → 降级启动(T2/T3, §63.2)

Step 4: Position Sync (<5s)
  经纪商持仓 = 系统记录的未平仓?
  不一致 → Log+Owner通知→broker为准→系统记录更新

Step 5: Fast Forward (<5s)
  补做 crash 期间的: 行情→因子→信号 (batch从最近checkpoint→now)
  不做: 下单——offline期间错过的不追

Step 6: Resume (<3s)
  断路器状态→HALF_OPEN (§45.4)
  Owner确认→CLOSED (恢复交易)
  或 Owner不确认→保持OPEN (手动接管)
```

### 92.3 热重启健康检查

```
Resume 前必须全部通过:
  ☐ 行情数据流正常 (≤2s delay)
  ☐ 经纪商连接正常 (API responsive)
  ☐ 持仓匹配 (broker_positions == system_positions ± 0)
  ☐ 无 UNCERTAIN 订单 (>0 → Owner MUST confirm)
  ☐ 未触发日内亏损限制 (§75.1 L4: 日亏>5%)
```

---

## 九十三、会话并发与文件完整性防御

> **定位**：§二十五 定义了 IDE 间隔离，但这只保证 metadata 级别不冲突。两个 AI session 同时修改同一个 .py 文件→编辑器未 reload→一方的更改会覆盖另一方。需要文件级并发控制和写入冲突检测。
> **对标**：VS Code File Locking + Git Merge Conflict Detection + SQLite WAL Concurrency + Vim Swap Files。

### 93.1 四种并发冲突场景

| 场景 | 风险 | 后果 |
|------|------|------|
| 两 session 改同一文件 | 后写入覆盖先写入 → A的改动丢失 | 代码回退+逻辑缺失 |
| Session-A 改了 imports → Session-B 移除了依赖 | import 失败→构建断裂 | 运行时错误 |
| Session-A 重构函数签名 → Session-B 用旧签名调 | 调用失败 | 运行时崩溃 |
| Session-A 改蓝图 → Session-B 按旧蓝图施工 | 代码与蓝图不一致 | GATE-A 失败 |

### 93.2 文件锁机制 (ZephyrLock)

```yaml
# .zeph/locks/file_locks.yaml (每次 touch file 前检查)
locks:
  - file: "src/zephyr/l02_alpha_factor/core.py"
    holder: "session-20260505-001"
    acquired_at: "2026-05-05T10:23:45+08:00"
    ttl: "30min"  # 超时自动释放——防止 session 僵死锁文件
    mode: "EXCLUSIVE"  # 或 READ_ONLY

规则:
  - 写入前 MUST acquire EXCLUSIVE lock
  - 读取前 MAY acquire READ_ONLY lock (避免读到半成品)
  - Lock TTL 30min → 超时自动释放 + session通知
  - Owner 有 force_unlock 权限 (紧急情况)
```

### 93.3 冲突检测与自动解决

```
每次 AI session 保存文件前:
  1) 检查: 磁盘上的文件 mtime > 我上次读取的 mtime?
     YES → 文件已被其他session修改
  2) 策略:
     同一语义域 (同一模块): 自动合并 (git merge-file 风格)
     不同语义域: 暂停当前session → Owner通知 → 决定合并策略
  3) 自动合并失败: 🛑 两个 session 都暂停 → Owner 手动解决

After merge:
  测试全绿 + lint通过 → 合并成功
  否则 → 回滚一方→ Owner分配写权限
```

### 93.4 预分配策略 (冲突避免)

```
Session 启动时:
  AI 声明 → "本次 session 将修改: [l02_alpha_factor/core.py, l02_alpha_factor/models.py]"
  调度器检查: 这些文件是否有活跃锁?
  NO → 立即分配 → 其他 session 知道这些文件被占用
  YES → 排队等待 或 拒绝该 session (告知Owner)
```

---

## 九十四、硬件容灾与基础设施故障模式

> **定位**：1人+AI 的场景下，硬件故障=可能数天无法恢复。SSD 磨损、RAM 错误、电源故障、散热失效——每一个都是 SPOF。FMEA(§十六)只覆盖了软件故障模式，没有覆盖硬件层面。
> **对标**：Backblaze Drive Stats + Google Disk Failure Study + NAS/SAN Best Practices + APC UPS Sizing。

### 94.1 硬件故障五类

| 故障类型 | 检测 | 概率 (年) | 恢复时间 | 预防 |
|------|------|:--:|:--:|------|
| SSD/NVMe 渐死 | SMART (ReallocatedSectorCt/MediaWearout) | ~1-3% | 4-24h (换盘+恢复) | SMART监控+自动告警+备用SSD |
| 内存单比特错误 | Windows Memory Diagnostic / memtest86 | ~8% (非ECC) | 2-48h (换内存条+恢复) | 月检+备用内存条 |
| 电源故障 | 无预兆——突然断电 | ~2-5% | 4h-3天 (换电源) | UPS≥30min续航+自动关机(§14.2) |
| 散热失效 | CPU/GPU温度骤升→降频 | ~1-2% | 1-4h (清灰/换风扇) | 温度监控+告警(≥85°C) |
| 磁盘空间耗尽 | df -h → >90% | 100% (一定发生) | 15-60min (清理或加盘) | 磁盘监控+自动清理(§96) |

### 94.2 硬件健康面板 (每日自检)

```
每天 06:30 自动运行:

  SSD:
    ☐ SMART Status: OK
    ☐ Reallocated Sectors: 0 (关注增长趋势)
    ☐ Wear Level: <80% (寿命消耗)
    ☐ Temperature: <60°C
  
  RAM:
    ☐ 最近一次 memtest: <30天 & PASS
    ☐ 可用内存: >20% (非 error——这个是资源监控)
  
  Power:  
    ☐ UPS 连接: Yes
    ☐ UPS 电池: >80% capacity
    ☐ UPS 预估续航: >15min
  
  Thermal:
    ☐ CPU Temp: <80°C
    ☐ GPU Temp: <80°C (如有)
    ☐ 所有风扇: RPM > 0

任何 **☐ FAIL** → Owner 即时通知 (SMS/Email, §85提到但未系统化→§九十八)
```

### 94.3 硬件故障应急操作

```
SSD 濒死 (SMART warning):
  1) 即时全量备份 (§59.1) → 外部硬盘+云存储
  2) 非必要进程停止——只保留实时监控
  3) 下单备用 SSD → 到货后 dd clone 或 重建环境(§69.2)
  4) Owner 收到物理行动指令: "买新SSD——型号: Samsung 990 Pro 2TB"
```

---

## 九十五、API 生命周期与弃用治理

> **定位**：任何活得足够久的系统都会面临 API 演化问题。AI 生成的代码调用了 v1 的接口，但 v1 被废弃了→运行错误。需要管理向内(模块间)和向外(第三方 API)两个方向的 API 生命周期。
> **对标**：Google API Design Guide + Kubernetes API Deprecation Policy + Stripe API Versioning。

### 95.1 内部 API 三阶段生命周期

| 阶段 | 标记 | 行为 | 持续 |
|:--:|------|------|:--:|
| Active | `@api(version="v2", status="active")` | 全部调用正常——推荐使用 | ∞ (或直到 v3 发布) |
| Deprecated | `@api(version="v1", status="deprecated", sunset="YYYY-MM-DD")` | 仍可用→每次调用发出 DeprecationWarning→写入 LOG | ≥3 月 |
| Removed | 代码中完全删除 | 调用→ ImportError / AttributeError → 错误日志+建议替代 API | — |

### 95.2 AI 自动适配弃用

```
当 AI 施工调用 Deprecated API:
  1) ruff 自定义规则: 检测 deprecated import→block (🔴)
  2) AI 上下文注入: 所有 deprecated APIs 列表→"Do NOT use these"
  3) AUTO-FIX: 若 1:1 映射 (get_price→fetch_price) → AI 自动改
```

### 95.3 第三方 API 变更监控

```
监控项:
  ☐ 所有第三方API 文档变更检测 (每周扫码)
  ☐ 新弃用通知: 经纪商API/SDK changelog → AI总结 → Owner
  ☐ Price变更: Data API订阅费变化 → 成本仪表板更新(§12.4)
  ☐ 已知 API EOL (End-of-Life)日期追踪 → 倒计时提醒

代码适配流程:
  第三方 API 弃用通知 → 
    AI 生成impact_analysis: 哪些模块受影响? 
    → AI 生成 migration plan: 新API调用方式+测试
    → Owner批准→AI执行迁移→测试全绿→合并
```

---

## 九十六、数据全生命周期与自动化清理

> **定位**：不回缩的日志、不清理的缓存、不复位的临时表——系统终将填满磁盘。§五十九·2 做了日志轮替，§八十二·3 做了死代码退役，但缺少系统性的数据生命周期管理。数据应该有出生、衰老、死亡。
> **对标**：AWS S3 Lifecycle Policies + Postgres VACUUM + Redis Eviction Policy + Google Cloud Data Lifecycle。

### 96.1 数据生命周期五阶段

| 阶段 | 描述 | 典型数据 | 时长 |
|:--:|------|------|:--:|
| Hot (内存) | 实时读写——毫秒级访问 | 当前信号缓存、活跃订单状态 | ≤1天 |
| Warm (SSD主库) | 频繁查询——秒级访问 | 最近30天行情/因子/回测结果 | ≤30天 |
| Cool (SSD存档) | 偶尔查询——分钟级访问 | 31天~1年的历史行情/日志 | ≤1年 |
| Cold (外部备份) | 极少访问——小时级访问 | 1~5年的交易/审计/合规记录 | ≤7年 |
| Purge (删除) | 永久销毁 | 过期日志、临时分析结果、已废弃因子 | — |

### 96.2 自动清理调度 (AutoHousekeep)

```
每天 03:00 UTC (非活跃时段):

  ☐ 清理 tmp_* 表 (创建>7天): DROP
  ☐ 清理 stalled_* 锁 (TTL expired): DELETE
  ☐ 清理 orphaned 特征 (symbol 已退市/无行情>90天): DELETE→cold备份
  ☐ 清理 stale 缓存 (策略参数缓存>版本update + 7天): DELETE
  ☐ Compact WAL: VACUUM sqlite → 回收已删除行空间
  ☐ 磁盘检查: df -h + AI→检查最占空间的文件TOP10

Any disk >85% → 立即清理+Tier迁移加速+Owner通知
```

### 96.3 数据遗忘权 (Regulatory Purge)

```
数据必须可销毁:
  ☐ 每季度检查: 有无超过法规要求留存期的L3/L4数据?
  ☐ Purge protocol: 不只删除文件——安全擦除(3-pass overwrite)
  ☐ Purge log: 日期+操作人+数据范围+擦除方法 +不可篡改
```

---

## 九十七、时间同步与时钟纪律

> **定位**：分布式系统最危险的不是错误——是"大家都对，但时间不一样"。行情时间戳、订单时间戳、日志时间戳必须基于同一时钟。1秒的时钟偏差能导致复盘时事件排序完全错乱。
> **对标**：NIST Time Service + PTP (Precision Time Protocol) + Google TrueTime (Spanner)。

### 97.1 时间源三级

| 级别 | 源 | 精度 | 使用场景 |
|:--:|------|:--:|------|
| L1: NTP | pool.ntp.org + ntp.aliyun.com + time.windows.com (3源交叉验证) | ±50ms | 系统日志、文件mtime、部署时间 |
| L2: 交易所时钟 | 交易所 WebSocket 返回的 ServerTime | ±10ms | 行情时间戳——以交易所为准 |
| L3: 经纪商时钟 | 经纪商 API 返回的 timestamp | ±100ms | 订单确认时间——以经纪商为准 |

### 97.2 时钟偏差监控

```
Clock Monitor (每分钟):
  1) 系统时钟 vs NTP (3源中位数) → delta > 100ms?
  2) 系统时钟 vs 交易所时钟 → delta > 500ms?
  3) 连续3次 delta 增长 → 时钟在漂移——不是瞬时spike

Delta > 1s:
  🛑 自动交易暂停——不可靠的时间戳=不可靠的信号时效性
  Owner通知 + ntpdate -u 强制同步
```

### 97.3 时间戳规范

```yaml
# 所有时间戳 MUST 遵循:
format: "ISO 8601 with timezone: 2026-05-05T10:23:45.123+08:00"
precision: 毫秒
source: "MUST annotate: system | exchange | broker | ntp"

Forbidden:
  - 无时区的时间戳 (2026-05-05 10:23:45 —— 什么时区?)
  - 使用本地时间不做 tz 转换
  - 混用不同粒度 (秒 vs 毫秒) 在同一个 log stream
```

---

## 九十八、实时流式数据架构

> **定位**：§四十 描述了市场数据批处理管线，但在实盘场景中，行情是持续流，不是"每5分钟拉一次"。T+0 或高频策略需要毫秒级的 WebSocket/streaming 处理，而不是 REST 轮询。
> **对标**：Interactive Brokers TWS API (reqMktData) + Alpaca/Polygon WebSocket + Kafka Streams + Flink。

### 98.1 两轨数据架构

| 轨 | 模式 | 用途 | 延迟 |
|:--:|------|------|:--:|
| Batch (T+1) | REST 日终拉取→DB→因子批跑 | 回测、因子研究、收盘对账 | ≤ N/A ——盘后 |
| Stream (T+0) | WebSocket 实时推送→内存环形缓冲→因子增量计算→信号即时生成 | 实盘信号、实时风控 | ≤100ms (end-to-end) |

### 98.2 Stream 处理管线

```
WebSocket Listener (多连接——多交易所)
  ↓ JSON event → parse → validate (check NaN/gap)
  ↓ 写入 Ring Buffer (CAPACITY=3600 × 最新1h 全tick)
  ↓ 增量因子计算 (不重算全量——只算新到达的 tick)
  ↓ Signal Re-eval (上次signal→本次signal? changed? → 交易决策)
  ↓ Pre-trade Risk (§41.1: 价格偏离/频率/仓位)
  ↓ Order dispatch → FIX/API → Broker

如果 stream 断开:
  ≥2s: reconnect attempt ≤ 3次
  ≥10s: fallback to REST polling (1min interval) + alert
  ≥60s: 🛑 暂停自动交易 → 切换到T+1模式
```

### 98.3 连接池管理

```
WebSocket 连接池:
  max_connections: 10 (操作系统+内存限制)
  连接复用: 同一交易所 → 一个连接上多路订阅
  心跳: 每30s→pong, 超时15s→重连
  断线重连: exp backoff (1s→2s→4s→8s→15s→30s→...→max 60s)
```

---

## 九十九、静默故障聚合与级联风险防御

> **定位**：最危险的故障不发出告警——静默累积。10个L1故障叠加=1个L3的效果，但每个单独都低于告警阈值。需要聚合评分和级联风险建模，否则系统在"全部正常"中慢慢死去。
> **对标**：Netflix Atlas Aggregation + AWS Composite Alarms + SLO-based Alerting。

### 99.1 静默故障五类

| 静默故障 | 典型表现 | 单独时危害 | 聚合后危害 |
|------|------|:--:|:--:|
| 因子精度退化 | IC 从 0.05 → 0.03 (低于1σ但趋势向下) | 低 | 高一3因子同时→信号=噪声 |
| 滑点模型偏差 | 实盘滑点=1.5×模型 (不到×3阈值) | 低 | 实盘PnL被蚕食20% |
| 数据延迟增大 | 行情延迟150ms→200ms (不到ALARM阈值) | 低 | 高—所有信号都用了过期数据 |
| 内存泄漏 | 每session +50MB (可用>20%→不告警) | 低 | 2天后→OOM→全系统crash |
| 依赖库版本老化 | pip包落后3个minor→无breaking change | 低 | 高—安全漏洞未被patch→入侵风险 |

### 99.2 聚合故障评分 (AFS)

```
Aggregate Failure Score:
  AFS = Σ(failure_i × severity_i × persistence_i) / N_active_modules

  failure_i:  单个故障的 severity (0-10)
  severity_i: 故障类型系数 (润滑偏差1.0 / 数据质量2.0 / 安全5.0)
  persistence_i: 持续时长系数 (0-1h:0.5 / 1-24h:1.0 / >24h:2.0)
  
  AFS < 2.0:  ✅ 正常运转
  AFS 2.0-5.0: 🟡 聚合风险——Owner 评估
  AFS 5.0-10.0: 🔴 级联风险——减仓+暂停新开仓
  AFS > 10.0: 🛑 紧急——全冻结+全面诊断
```

### 99.3 级联路径建模

```
级联模型 (自动构建——每月更新):
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ 行情延迟  │◄───│ 信号陈旧  │◄───│ 误交易    │
  │  +200ms   │    │  -0.1Sharpe│    │  PnL损失  │
  └──────────┘    └──────────┘    └──────────┘
                        ▲
  ┌──────────┐          │
  │ 内存泄漏  │──────────┘
  │  CPU≥95% │
  └──────────┘

活跃级联链 >2: 🔴 任意一环断裂→干预
最脆弱环节 → AI weekly 自动识别+优先加固
```

---

## 一百、增量审查与部分接受协议

> **定位**：氛围编程最大的实践问题——AI 产出一个500行的变更，Owner 只有2分钟时间审查。全盘接受(ACCEPT)→有风险；全盘拒绝(REVERT)→浪费AI产能。实际上AI经常80%对+20%需要改。需要一个"接受这部分，拒绝那部分"的增量审查协议。
> **对标**：GitHub Pull Request Line Comments + Code Review Partial Approvals + Cursor Inline Edits。

### 100.1 芯片级审查标记

```
每个 AI 产出被自动切分为 Logical Chunks:

Chunk #1 (lines 10-45): 新增函数 calculate_momentum → [ACCEPT] [REJECT] [MODIFY]
Chunk #2 (lines 46-89): 修改参数默认值      → [ACCEPT] [REJECT] [MODIFY]  
Chunk #3 (lines 90-120): 新增type hints      → [ACCEPT] [REJECT] [MODIFY]
Chunk #4 (lines 121-150): 注释更新           → [ACCEPT] [REJECT] [MODIFY]

Owner 操作:
  - 快速模式: 一键ACCEPT全部 Chunks (≤10s)
  - 审查模式: 逐 Chunk 标记 → AI 自动 merge ACCEPT + fix REJECT/MODIFY
  - 修改模式: MODIFY Chunk → Owner 写一行注释 → AI 根据注释修正 → 重审

标记为 REJECT 的 Chunk:
  - AI 自动从产出中移除 → 保持剩余 Chunk 的完整性
  - REJECT 原因记录 → KB entries(§67.2) → 未来 Prompt 优化
```

### 100.2 审查时间预算

| AI 产出规模 | Owner 审查时间 | 审查策略 |
|------|:--:|------|
| ≤50行 | ≤30s | 全量审——逐行看 |
| 50-200行 | ≤2min | Chunk审——只审逻辑Chunk (跳过格式/导入/typing) |
| 200-500行 | ≤5min | 关键Chunk审——只审架构变更+安全敏感+逻辑核心 |
| >500行 | 分批复审 | AI 拆分为2+个提交——每个独立审 |

### 100.3 增量审查质量度量

```
每次增量审查后记录:
  - 总 Chunks / ACCEPT% / REJECT% / MODIFY%
  - 审查耗时 (秒)  
  - 审查后 WQA 评分(§39)

Weekly pattern:
  REJECT% 升高 → Prompt 有问题? → Prompt 审查(§71)
  审查耗时增长 → Owner 疲劳? → 建议休息(§46.3)
  审查后WQA < 审查前 → AI修正质量不够 → Model/路由调整
```

---

## 一百〇一、基准完整性与样本生存偏差防御

> **定位**：回测依赖于"当时能交易什么"——但在历史中，CSI300 的成分股一直在变。用今天知道的成分股去交易2018年的市场=前视偏差+生存偏差。业界称为"Survivorship Bias"，是回测虚高最大的单一来源(可虚高2-4%年化)。
> **对标**：CRSP Survivorship Bias Free + Compustat Point-in-Time + WRDS。

### 101.1 基准四维完整性

| 维度 | 问题 | 解决方案 |
|------|------|------|
| 成分股变更 | 回测用了"今天在指数中"的票——2018年可能根本没有 | 每日成分股快照+历史变更记录 |
| 退市票缺失 | 退市的票从DB删了→回测只看到"活下来的" | 退市≠删除;标记 status=DELISTED +退市价格+退市日 |
| 新上市票前视 | 2023年上市的票出现在2020年的回测池中 | IPO日期记录+pool 日级过滤(上市<date→排除) |
| 停牌处理 | 停牌期间因子=stale→实际不可交易 | 停牌日历+停牌期间标记为不可交易+因子用NaN而非假值 |

### 101.2 点对点基准重构

```
Point-in-Time Universe:
  每天: 系统存储当日可交易全集(symbol_list + tradeable=true)
  
  回测时: 
    for day in 2016-01-01..2024-12-31:
      pool = get_universe(day)  // 只用当天的成分股
      factors = calculate(pool, day)
      signals = generate(factors)
      trades = execute(signals, pool)
    
  NOT:
    pool = get_universe(TODAY)  // ❌ 前视——用今天知道的成分股
    for day in history: ...
```

### 101.3 基准健康检查

```
每月:
  ☐ 成分股变更记录完整? (gap ≤ 1 天)
  ☐ 退市票全部保留? (≠ 删除)
  ☐ 有 ∆ Universe 超过 5%/月 → 审查——是否合理?(非数据错误)
  ☐ 基准收益 vs 实际指数收益: tracking error < 0.1% (验证基准复现正确)
```

---

## 一百〇二、跨环境一致性与平台风险矩阵

> **定位**：开发环境(Windows 11 + Python 3.12)和生产环境(可能同一台机器)的隐性差异——Windows Update 重启、防病毒扫描、WSL vs Native、路径分隔符——这些是非功能性但能杀死系统的问题。1人+1台机器:环境=不可替代。
> **对标**：12-Factor App Dev/Prod Parity + Docker Multi-Platform + Windows Subsystem for Linux。

### 102.1 跨环境四维差异

| 维度 | Windows 原生 | WSL2 | Linux 云服务器 |
|------|------|------|------|
| 路径分隔符 | `\` | `/` (Linux路径) | `/` |
| 文件锁行为 | 排他锁(其他进程不可读) | POSIX advisory(其他进程可读) | POSIX advisory |
| 进程优先级 | Windows Priority Class | Linux nice | Linux nice |
| 定时任务 | Task Scheduler / 自写 | cron | cron |
| 最大打开文件数 | 高 (默认 16M handles) | 低 (ulimit -n) | 低 (ulimit -n) |
| 字符编码 | UTF-16 (内核), UTF-8 (Python) | UTF-8 | UTF-8 |

### 102.2 Windows 特定风险矩阵

| 风险 | 影响 | 缓解 |
|------|------|------|
| Windows Update 强制重启 | 交易时段重启→全系统停摆 | Active Hours 设为交易时间;暂停自动更新(组策略) |
| Windows Defender 全盘扫描 | CPU 被占→延迟峰值→信号过期 | 排除 ZephyrAlpha 目录+Python 进程 |
| 休眠/睡眠 | 所有连接断开→恢复后状态混乱 | 禁止休眠(powercfg -h off)——只锁屏 |
| 区域/语言设置变更 | 日期格式变动→CSV解析失败 | 锁定格式: ISO 8601, . 为小数点, utf-8 |
| 第三方软件干扰 | VPN/DNS/代理→网络结构变化 | 最小化安装——只有必要的软件+Python |

### 102.3 环境重现性幂等脚本

```powershell
# .zeph/scripts/setup_windows.ps1 (idempotent——可重复运行)
1) 检查Python 3.12 已安装 → YES: skip → NO: winget install python3.12
2) 设置时区: tzutil /s "China Standard Time"
3) 配置NTP: w32tm /config /manualpeerlist:...
4) 禁止休眠: powercfg -h off
5) 禁止自动重启: 组策略 (Windows Update→No auto-restart)
6) Windows Defender 排除: Add-MpPreference -ExclusionPath "D:\ZephyrAlpha"
7) 创建 venv + pip install -r requirements.locked.txt
8) 运行全量测试: pytest tests/ -x
9) 输出: 环境就绪 ✅ 或 问题清单 ❌
```

---

---

## 一百〇三、变更记录

| 版本 | 日期 | 变更内容 |
|------|------|------|
| 0.13.0 | 2026-05-08 | 🔧 v0.13.0——审计修复轮（6 项内部一致性问题）。修复: ①新增 §0.0 系统健康面板(四黄金信号+11 SLI SLO目标值+§0.0.4 突破SLO处置流程)——修复6条ai_role_instruction规则+§二十六+§七十五等8处悬空引用；②§7 模块数 25→44 (module-registry.yaml实有44模块)；③B-Track §1.3 表补全 MOD-INF-027(Audit Orchestrator)+MOD-INF-028(Semantic Auditor) 两行缺失条目；④frontmatter摘要 §4 "三线数据流+时序约束"→"跨模块数据流与关键集成点"对齐实际内容+拆分§十六FMEA；⑤REG-MOD-001 entry_count 41→44；⑥导航链 B-Track 条目数 25个→29个(MOD-INF-001~026→001~028)；⑦last_updated+施工落盘日期同步至2026-05-08。蓝图102章不变。 |
| 0.12.0 | 2026-05-06 | 🎉 v0.12.0——第七轮深度诊断18盲点全注入(实际新增12个章节+6个AI规则=18个主题)。AI规则: 64→76条(+企业行为独立管线/热重启六步协议/ZephyrLock文件锁/每日SMART+温度+UPS硬检/API三阶段生命周期Active→Deprecated→Removed/数据Hot→Warm→Cool→Cold→Purge五阶段生命周期+每日AutoHousekeep/三源NTP时钟偏差监控+ISO8601时间戳/Stream轨WebSocket优先+断流60s暂停/静默故障AFS聚合评分级联防御/Chunk级增量审查三元态/回测Pool Point-in-Time+退市≠删除/环境幂等可重建+Win11风险矩阵)；分派表: 69→81域(+企业行为/热重启/会话并发/硬件容灾/API生命周期/数据生命周期/时间同步/流式数据/静默故障/增量审查/基准完整性/跨环境一致性)。新增: §九十一 企业行为与参考数据管线(七类CA处理+除权除息日模式+每日5项检查+回溯修复协议) + §九十二 热重启与盘中故障恢复协议(冷启动vs热重启对比+六步恢复协议+健康检查) + §九十三 会话并发与文件完整性防御(四种冲突场景+ZephyrLock文件锁机制+冲突检测预分配) + §九十四 硬件容灾与基础设施故障模式(SSD/RAM/电源/散热五类故障+SMART面板+断电/电力恢复四步+硬件容灾预算) + §九十五 API生命周期与弃用治理(内部API三阶段+AI自动适配+第三方变更监控+代码适配流程) + §九十六 数据全生命周期与自动化清理(Hot→Warm→Cool→Cold→Purge五阶段+AutoHousekeep调度+数据遗忘权) + §九十七 时间同步与时钟纪律(NTP三源+偏差监控+ISO8601时间戳规范+禁止模式) + §九十八 实时流式数据架构(Batch/Stream双轨+WebSocket连接池+背压防御+乱序事件重组) + §九十九 静默故障聚合与级联风险防御(五类静默故障+AFS聚合评分+级联路径建模) + §一百 增量审查与部分接受协议(Chunk级三元态ACCEPT/REJECT/MODIFY+审查时间预算+增量质量度量) + §一百〇一 基准完整性与样本生存偏差防御(PIT Universe+四维完整性+基准健康月度检查) + §一百〇二 跨环境一致性与Windows平台风险矩阵(Win11 vs WSL2四维差异+6项Win风险缓解+幂等环境setup脚本)。蓝图: 90章→102章。七轮累计: 33+31+20+18+20+20+18=160盲点全覆盖。 |
| 0.11.0 | 2026-05-06 | 🎉 v0.11.0——第六轮深度诊断20盲点全注入。AI规则: 44→64条(+Prompt版本控制+回归测试/上下文预算+幻觉检测/多模型共识/代码脚手架+禁止模式/KillSwitch五级+盘前检查+收盘对账/模拟→实盘五阶段过渡/订单执行质量+经纪商评分/断供因子+隐性知识提取/本地优先+离线五级/决策四级分流+时间窗口/参数灵敏度+MonteCarlo破产概率/混沌工程+故障注入演练/宏观体制切换/交易决策解释链/SBOM+依赖健康/状态机形式化/DORA四指标+AI速率/A/B实验框架)；分派表: 49→69域(+Prompt工程/上下文窗口+幻觉/多模型共识/代码生成标准/Kill Switch/模拟→实盘/订单执行质量/知识连续性/本地优先/决策疲劳/What-If仿真/代码考古/数据源可靠性/混沌工程/经济体制/AI可解释性/SBOM/状态机/DORA指标/A/B实验)。新增: §七十一 Prompt全生命周期管理(Prompt版本控制+回归测试+Output契约+PES评分) + §七十二 AI上下文窗口策略与幻觉防御(五级预算+渐进式加载+裁剪规则+三级幻觉检测+自动修复) + §七十三 多模型共识与智能体辩论协议(三种共识协议+结构化辩论格式+模型能力加权+异议升级) + §七十四 AI代码生成标准与项目脚手架(文件级约定+模块模板+代码头标准+禁止模式检测) + §七十五 实盘交易五级Kill Switch与安全保障矩阵(五级开关+盘前8项检查+盘中异常响应+收盘五步对账) + §七十六 模拟→实盘过渡与资金渐进协议(五阶段过渡+回退触发器+跨策略互斥) + §七十七 订单执行质量监控与异常检测(四维异常+经纪商评分+结算监控) + §七十八 知识连续性与断供因子防护(BusFactor度量+自动接手手册+知识资产清单+脑Dump计划) + §七十九 本地优先架构与离线自主运行(五级离线能力+恢复同步+数据本地化) + §八十 决策疲劳管理与Owner优先级分流(四级分流+决策卡片+时间窗口+决策模式检测) + §八十一 What-If仿真与灵敏度分析引擎(参数扫描+MonteCarlo+破产概率+反事实回测) + §八十二 AI辅助代码考古与文档自动化(考古四问+AUTO-DOC+死代码退役) + §八十三 市场数据源可靠性评分与智能切换(五维评分+源衰退预警+智能切换+数据补齐) + §八十四 混沌工程与自动故障演练(五类故障注入+演练日历+失败升级) + §八十五 经济体制检测与宏观因子覆盖(五维宏观因子+体制映射+切换预警) + §八十六 AI决策可解释性与监管审计深度(解释链+模型卡+审计就绪) + §八十七 SBOM生成与依赖情报(自动SBOM+依赖健康五维评分+升级自动化) + §八十八 状态机形式化与正确性验证(统一YAML规范+自动测试生成+崩溃协调) + §八十九 DORA指标与开发速率度量(四指标+AI特有+速率健康面板) + §九十 A/B实验框架与统计严谨性(实验模板+显著性计算+结果归档)。蓝图: 70章→90章, ~1600→~2600+行。六轮累计: 33+31+20+18+20+20=142盲点全覆盖。 |
| 0.10.0 | 2026-05-05 | 🎉 v0.10.0——第五轮深度诊断20盲点全注入。AI规则: 34→44条(+日运营节奏/PnL归因/容错模式Bulkhead+Backoff+Jitter/因子治理/FeatureFlag暗启动/Secrets轮替/每日环境可重建/AI自诊断修复/跨会话Prompt一致性/离线分级决策)；分派表: 39→49域(+PnL归因/日运营节奏/系统容错模式/微结构防御+模拟保真度/因子治理/功能开关+部署安全网/AI自诊断+知识自动化/氛围编程确定性/Secrets生命周期+环境可重建/离线分级应急+全生命周期预算)。新增: §六十一 PnL归因与TCA(4维归因:因子/行业/风格/TCA+每日报告格式) + §六十二 日运营节奏与交易会话协议(5Phase交易日流程+快捷指令+禁止交易时段长EXPLORE) + §六十三 系统容错模式深度(Bulkhead+Retry+Backoff+Jitter+Timeout+ShedLoad+4层优雅降级) + §六十四 微结构防御与模拟盘保真度(5大防御+保真度因子FF模型) + §六十五 因子治理与策略生命周期深化(4阶段:准入→去重→监控→退役+正交化管线) + §六十六 功能开关与部署安全网(3类Flag+暗启动4步+事故后5步自动验证) + §六十七 AI自诊断-自修复与知识自动化(3层自修复闭环+AUTO-KB知识提取) + §六十八 氛围编程确定性保障(CSCV验证+4层确定性+复杂度熵度量+强制反击) + §六十九 Secrets生命周期与环境可重建性(5阶段密钥生命周期+90天轮替日历+每日Auto-CLEAN-BUILD) + §七十 离线分级应急与全生命周期预算(5×3决策矩阵+衰减结构预算+E2E延迟预算+行级代码溯源)。蓝图: 16章→70章, ~290→~1600+行。五轮累计: 33+31+20+18+20=122盲点全覆盖。 |
| 0.1.0 | 2026-05-04 | beta 创建——系统总蓝图初版。三级金字塔顶点就位：系统全景拓扑（14C+12B）、架构原则（5项+5铁律）、ADR索引、跨模块数据流、蓝图导航链、令牌预算层级、运行时平面视图。 |


---

## 施工落盘确认（2026-05-08 审计）

| 维度 | 状态 |
|------|------|
| construction_progress | completed（文档层面） |
| 文档路径 | docs/03_modules/_sys-master/blueprint.md (本文档自身) |
| 说明 | 架构/集成文档——定义跨模块契约与集成标准 |
