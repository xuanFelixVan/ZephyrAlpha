---
module_id: KE-module_blu-3-005
title: 3. 九子系统
category: module_blueprint
---

# 3. 九子系统

3. 九子系统

> **契约兼容声明（B27）**：所有新定义的数据类（MetricPoint, AIBehaviorEvent, HealthReport, Span 等）是 `shared/contracts/telemetry_emitter.py`（CTR-P1-013 TelemetryEmitter）的合规实现。不得定义与 TelemetryEmitter 冲突的接口。**语义对齐声明（B44）**：AI 行为相关字段命名 MUST 可映射到 OTel GenAI + Agent Semantic Conventions（§2f）。

```
src/zephyr/l12_system_telemetry/
├── metrics/       ← 数值指标：LLM调用次数 / Gate通过率 / 任务完成率
├── logs/          ← 结构化日志：JSON log→CE注入 / Gate审计 / Pipeline异常
├── traces/        ← 分布式链路：TaskCard全生命周期追踪（draft→pipeline→complete）
├── ai_behavior/   ← AI行为监控：模型选择频率 / Token消耗 / Gate命中率 / 幻觉率
├── archive/       ← 历史存档：冷数据压缩归档（>30天）
├── profiles/      ← 🆕 连续性能剖析：CPU/内存火焰图 / 热点函数定位
├── health/        ← 🆕 自体监控：Telemetry自身健康 + 独立watchdog + 心跳
├── alerts/        ← 🆕 告警路由：Multi-window Burn Rate告警 + 通知通道 + 静默/聚合
└── schema/        ← 🆕 指标Schema注册表：统一指标定义 + 运行时校验 + 漂移检测
```

| 子系统 | 职责 | 数据格式 | 消费方 | 施工状态 |
|--------|------|---------|--------|:---:|
| **metrics** | SLI/SLO 与业务指标流 | `MetricPoint {name, value, timestamp, labels, type, exemplar}` | FLE / Capacity Assurance / Budget Enforcer | 🟡 骨架 |
| **logs** | 结构化日志聚合与检索 | JSON Lines（`event_id` + `module` + `level` + `trace_id` + `span_id`） | Gate Engine / Audit / FLE | 🟡 骨架 |
| **traces** | TaskCard 全链路追踪 + W3C TraceContext 传播 | Span（Root→M1→G2→Orc→Script→Complete） | Pipeline / Debug / FLE | 🟡 骨架 |
| **ai_behavior** | AI 模型行为画像（含成本） | 模型选择日志 / Token消耗 / Gate命中率 / $成本 / 幻觉评分时序 | FLE / Capacity Assurance / Budget Enforcer | 🟡 骨架 |
| **archive** | 冷数据压缩归档 | gzip JSONL（30天后自动归档，90天物理删除） | 审计回溯 | 🟡 骨架 |
| **profiles** | 🆕 CPU/内存连续性能剖析 | pprof / OTel Profiles over OTLP | FLE（性能回归检测） | ⚪ 待建 |
| **health** | 🆕 自体监控 + 独立 watchdog | HealthCheck {service, status, uptime, error_rate} | Watchdog进程 / FLE | ⚪ 待建 |
| **alerts** | 🆕 告警路由引擎 + 多通道通知 | AlertRule {SLI, burn_rate_window, threshold} + NotificationChannel | FLE → Feishu/钉钉/Email | ⚪ 待建 |
| **schema** | 🆕 指标 Schema 注册 + 漂移检测 | MetricSchema {name, type, labels, unit, owner} | 全模块（写入校验）+ 蓝图漂移检测 | ⚪ 待建 |

---
