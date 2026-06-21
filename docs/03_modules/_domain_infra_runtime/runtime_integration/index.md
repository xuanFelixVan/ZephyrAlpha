---
doc_type: index
status: Active
generated: '2026-05-02'
updated: '2026-05-05'
blueprint_id: DOM-GOV-001
title: Runtime Integration
module_id: MOD-INF-002
---

# Runtime Integration — 目录索引

## 责任声明（Single Responsibility）

本目录只存放：**infra_ops 层模块 — runtime integration**。

## 文件清单

| 文件 | 说明 |
|------|------|
| blueprint.md | 模块蓝图 v5.0.1——15 RI 模块 + 48 Cross-Layer 缺口填补 + 155+ 项总盲点（v3:49 + v4:55 + v5:50+）+ §13 终极取证审计（10项致命假设） |
| index.md | 目录索引（本文件） |

## 关联子蓝图/设计文档（本模块下属）

| RI 模块 | 路径 | Phase | MOD-INF-016 承载 | 说明 |
|---------|------|:--:|:--:|------|
| RI-01 EventBus | `blueprint.md §5.1` | 1b | `shared/observer.py` | 四级PriorityQueue + DeliverySemantics(AT_LEAST_ONCE) + DLQ SQLite持久化 + 背压传导链 + 消费者组 + Schema兼容 + SpeculativeExecution |
| RI-02 ModuleLifecycle | `blueprint.md §5.1` | 1a | `shared/lifecycle/hooks.py` | 拓扑排序/版本约束/优雅关闭协议(drain→force kill)/预热期/Crash-Only设计 |
| RI-03 ConfigCenter | `blueprint.md §5.1` | 1a | `shared/config/` | 热重载/Feature Flags(渐进推出1%→100%+交互矩阵+Kill Switch)/写入校验/Schema兼容性策略/配置审计/回滚 |
| RI-04 DependencyInjector | `blueprint.md §5.1` | 1a | `shared/production/di_container.py` | 构造注入 + ABC接口绑定 + 循环依赖检测——统一由MOD-INF-016承载 |
| RI-05 ResilienceGuard | `blueprint.md §5.1` | 2a | `shared/resilience/` | 七合一：CircuitBreaker+RateLimiter+Timeout+Bulkhead+LoadShedder+RetryBudget+自适应并发 |
| RI-06 IdempotencyGuard | `blueprint.md §5.1` | 2a | `shared/production/idempotency.py` | TTL分级：关键流ES expected_version天然去重/非关键流SQLite 24h TTL |
| RI-07 SecretsManager | `blueprint.md §5.1` | 2a | `shared/production/secrets.py` | AES-256-GCM加密 + ConfigCenter加密字段唯一后端 + 泄露检测 |
| RI-08 ErrorHandler | `blueprint.md §5.1` | 1a | `shared/errors.py` + `shared/logging.py` | SRE分类 + W3C Trace Context(traceparent) + OpenTelemetry兼容 |
| RI-09 HealthCheck | `blueprint.md §5.1` | 2a | `shared/health.py` | 三级状态 + 具体SLI阈值(CPU>80%→DEGRADED) + Reconciliation Loop持续对账 + TrustDecayTracker |
| RI-10 TelemetryCollector | `blueprint.md §5.1` | 1b | `shared/production/metrics.py` | per-module基数限制(500)+LRU淘汰 + PromptFingerprint + DeadModuleDetector |
| RI-11 CacheLayer | `blueprint.md §5.1` | 2a | `shared/production/cache.py` | LRU+VMS语义缓存+TTL分层 + DataAffinity |
| RI-12 AutoDiagnostics | `blueprint.md §5.1` | 2b | **独立落地** | Runbook→诊断→自愈→KB自动补充 + SelfLimiter(自限反馈) |
| RI-13 EventStore | `blueprint.md §5.1` | 3·触发 | **独立落地** | ES+CQRS+快照+时间旅行(写隔离) + Crypto-Shredding + SagaCoordinator(Phase 4触发) |
| RI-14 DryRunSimulator | `blueprint.md §5.1` | 2b | **独立落地** | sandbox预演 + 一致性验证套件 + CrossSessionLoopDetector + AI自预演(SelfSimulate) |
| RI-15 CostTracker | `blueprint.md §5.1` | 2b | **独立落地** | 全资源FinOps(LLM+CPU+内存+IO+PnL) + per-module费用归属 + MaintainabilityScore |

## 1人+AI 运维专项（v3→v4→v5 持续增强）

| 设计 | 版本 | 路径 | 说明 |
|------|:--:|------|------|
| Owner 告警预算 | v3 | `§6.3` | 每日实时告警上限 N=10，超出→汇总为日报 |
| 五级通知分层 | v3 | `§6.3` | 💀CRITICAL立即飞书 / 🟡WARNING每小时 / 🟢INFO每日 / ⚪DEBUG仅Dashboard / ✨AI_SELF_HEALED日报 |
| 休假模式 | v3 | `§7` | Owner离线72h→熔断/预算/轮转全自动 |
| 睡眠时段协议 | v4 | `§5.3, §6.5` | 23:00-07:00；CRITICAL仅触发1次→5min无响应→自愈 |
| 认知负荷预算 | v4 | `§6.5` | 决策容量模型 C_max；超80%→轻负载日；超100%→认知超载保护 |
| 自动决策引擎 | v4 | `§5.3` | RPN<50+影响≤3模块+费用≤$0.10→自动执行 |
| 晨报推送 | v4 | `§6.5` | 07:00 Daily Briefing: 昨日指标+费用+自愈+待审批 |
| 弃用螺旋防护 | v4 | `§6.5` | 72h无Owner介入→降低告警频率30% |

## 金融/交易系统专项（v5.0.0 新增）

| 设计 | 路径 | 说明 |
|------|------|------|
| Trading Kill Switch | `§5.3` | 代码骨架——5步停止序列：取消订单+清空EventBus+切换READ_ONLY+审计 |
| 5级 TradingMode | `§5.8` | NORMAL/PAPER/BACKTEST/READ_ONLY/KILLED——全模式切换 |
| 确定性复现双骨干 | `§5.3` | SimulatedClock + DeterministicRandom——回测可复现保证 |
| 纸交易基础设施 | `§5.8` | AI新模块默认PAPER模式——无实盘风险 |
| Pre-Trade 风控管道 | `§2.1-K02` | 订单→仓位→资金→敞口→合规→交易所 6步检查链 |
| 订单状态机标准化 | `§2.1-K03` | FIX Protocol对齐——NEW→PENDING→PARTIAL→FILLED/CANCELLED/REJECTED |
| 交易对账 | `§2.1-K07` | 系统订单 vs 经纪商回执 vs 清算报告 三方diff |
| EOD 日终处理 | `§2.1-K09` | 持仓结算/PnL/保证金/归档自动化 |

## 模块通信模式目录（v5.0.0 新增）

| 模式 | 支持 | 路径 |
|------|:--:|------|
| Pub/Sub | ✅ | `shared/observer.py` |
| Request/Reply | ⚠️ | `§5.9` Phase 1b |
| Scatter/Gather | ❌ | `§5.9` Phase 2b |
| Pipeline/Chain | ❌ | `§5.9` |
| Content-Based Router | ❌ | `§5.9` Phase 1b |
| Message Filter | ❌ | `§5.9` Phase 1b |
| Aggregator | ❌ | `§5.9` Phase 2b |

## AI 施工模式库（v5.0.0 新增）

| 设计 | 路径 | 说明 |
|------|------|------|
| 模块模板系统 | `§5.3` | Jinja2 模板——新模块自动生成骨架 |
| 反模式目录 | `§2.1-O02` | "在这个系统中绝对不要做什么" |
| 设计决策树 | `§2.1-O03` | "用EventBus还是直接调用？"→决策流程 |
| AI 信心标注 | `§2.1-O07` | 代码级信心0-1→决定审查深度 |
| 渐进审查深度 | `§2.1-O08` | 3级：轻审(lint+safety)→中审(+contract)→重审(+full+Owner) |
| Code Ownership | `§2.1-O06` | AI生成% vs Owner修改% vs AI修复% |

## 蓝图质量

| 设计 | 版本 | 路径 | 说明 |
|------|:--:|------|------|
| 设计原则 | v3 | `§5.2` | Crash-Only / StructuredConcurrency / Fail-Closed / ImmutableEvents / ProgressiveDisclosure |
| FMEA | v3→v4→v5 | `§9` | 17项失效模式 RPN 分析 |
| 五视图体系 | v3 | `§6.4` | 静态拓扑/动态行为/故障传播/容量伸缩/Owner感知 |
| 55+盲点分类清单 | v4 | `§2.1` | A-J 十个维度系统化审计 |
| 50+盲点分类清单 | v5 | `§2.1` | K-O 五个新增维度 |

## 排除规则（不应放入本目录的内容）

- ❌ 其他模块文档 → `../`
- ❌ 各 RI 模块的独立施工文档 → 统一在 `blueprint.md §12`
- ❌ MOD-INF-016 Shared Core 的实现代码 → `../../../src/zephyr/shared/`

## 父级目录

- 父级：[infra_ops](../index.md)