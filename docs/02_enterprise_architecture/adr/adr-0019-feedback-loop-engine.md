---
module_id: ADR-0019
doc_type: adr
title: Feedback Loop Engine — SQLite 时间序列 + EMA 异常检测
version: 1.0.0
status: active
date: '2026-04-24'
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs:
- ADR-0015
- ADR-0016
- ADR-0017
- ADR-0020
- ADR-0021
priority: P0
phase: Phase-1
tech_refs:
- TECH-13
- TECH-14
layer: L12
classification: confidential
language: zh
created_by: agent
valid_from: '2026-04-24'
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions: []
tags: [adr, vibe-coding]
summary: "**Vibe Coding 2.0 核心服务** Feedback Loop Engine（SQLite 时序 + EMA + Protocol 单向依赖，修复 VG-07）| accepted"
---

# ADR-0019: Feedback Loop Engine — SQLite 时间序列 + EMA 异常检测

**状态**：Accepted
**日期**：2026-04-24
**决策者**：ZephyrAlpha-Owner
**优先级**：P0
**阶段**：Phase 1 首批上线

---

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-24
- **拍板日期**：2026-04-24

## 2. 背景与问题（Context）

### 2.1 问题陈述

`vibe-coding-audit-merged.md §Kimi 13.5.2` 识别出 **VG-07 反馈闭环缺口**：系统有大量指标（CE 压缩延迟 / VMS 检索质量 / Orc 任务成功率 / LSG 拦截率），但**没有统一的消费者**能基于这些指标**触发动作**（降级、限流、告警、策略调整）。

Vibe Coding 2.0 方法论的 **Generate → Validate → Analyze → Evolve** 循环中，Evolve 环节**零自动化**。

### 2.2 设计目标

- **指标入向**：6 大核心服务全部上报（VMS/CE/Orc/LSG 自报）
- **异常检测**：统计基线 + 实时偏离识别
- **动作出向**：通过 **Protocol 适配器** 调整其他服务（CE 降级 / Orc 限流 / 人工告警），**不强耦合**
- **零循环依赖**：FLE 单向通知其他服务，其他服务不 import FLE
- **持久化**：SQLite 时间序列 Phase 1 足够（日 < 100 万条）

### 2.3 参考真源

- `vibe-coding-audit-merged.md §Kimi 13.5.2 Feedback Loop Engine`
- `vibe-coding-audit-merged.md §Qwen 选型表 #13-14`
- `feedback-loop-engine-interface.md v1.0.0`（797 行，B-a-4）

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：SQLite 时间序列 + EMA + Protocol 动作分派 ✅

- **优点**：
  - SQLite WAL 日 < 100 万条性能 OK（实测同架构项目）
  - EMA（指数移动平均）简单、可解释、低计算量
  - Protocol 单向依赖（其他服务不 import FLE）零循环
  - Phase 1 无外部依赖
- **缺点**：
  - 数据量 > 100 万/天时性能退化
  - EMA 对突发异常响应稍慢（~3-5 个数据点）

### 方案 B：InfluxDB 2.x + Telegraf + Kapacitor

- **优点**：专用时序栈性能最佳
- **缺点**：
  - 独立服务，运维成本
  - Phase 1 数据量远未达瓶颈
- **结论**：**保留为 TECH-13 升级路径**

### 方案 C：Prometheus + Alertmanager

- **优点**：业界标准，生态完善
- **缺点**：
  - Pull 模型不适合单机嵌入式场景
  - 需独立进程 + 9090 端口
- **结论**：**否决 Phase 1**（Phase 2 升级 OpenTelemetry 栈再评估）

### 方案 D：SPC（Statistical Process Control）

- **优点**：经典质量管控算法，误报率低
- **缺点**：
  - 需 > 30 数据点建立基线（冷启动期不可用）
  - Phase 1 过早优化
- **结论**：**保留为 Phase 2 升级**（EMA 误报率 > 20% 触发）

---

## 4. 决策（Decision）

**最终选择：方案 A — SQLite 时间序列 + EMA 异常检测 + Protocol 动作分派**

### 4.1 关键决策点

| 决策点 | 首选 | 备选 | 升级触发 |
|-------|------|------|---------|
| **时间序列存储** | SQLite WAL 时间序列表 | InfluxDB 2.x | 日数据量 > 100 万（TECH-13）|
| **异常检测算法** | EMA + 3σ 阈值 | SPC（R̄/X̄ chart）| 误报率 > 20%（TECH-14）|
| **动作分派** | Protocol 单向适配器 | pub/sub 消息队列 | Phase 3+ 多订阅者 |
| **采集方式** | 服务主动 push (`fle.collect_metric()`) | OpenTelemetry pull | Phase 2 运维栈升级 |
| **并发原语** | `asyncio.Lock` + `filelock.FileLock` | — | — |
| **持久化路径** | `.runtime/sqlite/feedback.db` | — | — |

### 4.2 指标模型

```python
@dataclass
class Metric:
    service: str              # "vms" | "ce" | "orc" | "lsg" | "fle"
    name: str                 # "search_latency_p99"
    value: float              # 0.152（秒）
    tags: dict[str, str]      # {"collection": "decisions"}
    timestamp: datetime       # UTC
    # 可选聚合窗口
    window: Literal["1m", "5m", "1h"] = "1m"
```

### 4.3 Protocol 适配器模式（关键创新）

**防止循环依赖**：FLE 定义 `FeedbackAction` Protocol，不 import 其他服务；其他服务实现适配器注册给 FLE：

```python
class FeedbackAction(Protocol):
    async def adjust_context_strategy(self, task_id: str, anomaly_type: str) -> None: ...
    async def throttle_orchestrator(self, rate_limit: float) -> None: ...
    async def raise_alert(self, severity: str, message: str) -> None: ...

# Context Engine 侧：
class ContextEngineFeedbackAdapter(FeedbackAction):
    def __init__(self, ce: ContextEngine): self.ce = ce
    async def adjust_context_strategy(self, task_id, anomaly_type):
        self.ce.set_compression_strategy("rule_based")  # 降级

# Orchestrator 侧同理
```

FLE 启动时注册 adapters，**自己对 CE/Orc/LSG 零 import**。

### 4.4 Phase 1 监测的关键指标（24 项）

基于 `08-operations-architecture.md §4.2` SLI/SLO 表 + `technology-landscape.yaml upgrade_watchboard`：

| 服务 | 关键指标数 | 阈值示例 |
|------|:---------:|---------|
| VMS | 5 | `search_latency_p99 > 200ms` |
| CE  | 4 | `build_latency_p99 > 500ms` |
| Orc | 6 | `queued_task_wait_p99 > 5s` |
| LSG | 4 | `fail_closed_rate > 0.1%/day` |
| FLE | 5 | `self_monitoring_lag > 30s` |

---

## 5. 后果（Consequences）

### 5.1 正面后果

- **VG-07 缺口修复**：Evolve 环节首次自动化
- **Protocol 零循环依赖**：架构纯净可测
- **Phase 1 快速落地**：2-3 人日 MVP
- **可观测性基础设施**：08-operations §4.2 SLI/SLO 有了消费者

### 5.2 负面后果

- **EMA 冷启动延迟**：前 10-20 数据点误差高
- **SQLite 上限**：日 100 万数据点后退化
- **手动阈值配置**：Phase 1 阈值需人工调参（Phase 2 引入 ML 自学习）
- **单点故障**：FLE 挂了其他服务不受影响（单向依赖），但失去反馈能力

### 5.3 未来重新评估触发条件

- **TECH-13**：日数据量 > 100 万 → InfluxDB 2.x
- **TECH-14**：EMA 误报率 > 20% → SPC 或 LSTM-based 异常检测
- Phase 3 多订阅者需求 → Protocol → pub/sub（NATS JetStream）
- 接入真实资金 → 加入 P&L 相关指标 + 合规告警

---

## 6. 落地动作（Implementation）

| # | 动作 | 物理位置 | 估时 |
|---|------|---------|:----:|
| 1 | `FeedbackLoopProtocol` + `FeedbackAction` Protocol | `src/zephyr/feedback_loop/protocol.py` | 0.5 天 |
| 2 | SQLite 时序 schema + DAO | `src/zephyr/feedback_loop/storage.py` | 0.5 天 |
| 3 | `InProcessFeedbackLoop` 主循环 | `src/zephyr/feedback_loop/in_process.py` | 1 天 |
| 4 | EMA 检测器 | `src/zephyr/feedback_loop/ema_detector.py` | 0.5 天 |
| 5 | 动作适配器（CE / Orc / LSG 各一） | `src/zephyr/feedback_loop/adapters/` | 1 天 |
| 6 | 24 项指标订阅配置 | `src/zephyr/feedback_loop/metrics_config.yaml` | 0.5 天 |
| 7 | 飞书 Bot 告警通道 | `src/zephyr/feedback_loop/alerting/feishu.py` | 0.5 天 |
| 8 | P0 测试组（异常注入 + 动作验证）| `tests/feedback_loop/test_p0.py` | 1 天 |

**总工时**：约 5 人日

---

## 7. 参考

- **真源**：`vibe-coding-audit-merged.md §Kimi 13.5.2` + `§Qwen 选型表 #13-14`
- **接口规范**：[`feedback-loop-engine-interface.md v1.0.0`](../../03_modules/_b_track_interfaces/feedback-loop-engine-interface.md)
- **消费关系**：[`08-operations-architecture.md §4.2 SLI/SLO + §8A.3 降级矩阵`](../target-architecture/08-operations-architecture.md)
- **技术选型**：[`technology-landscape.yaml TECH-13/14`](../target-architecture/architecture-model/technology/technology-landscape.yaml)
- **相关 ADR**：ADR-0015（CE 被通知方）/ ADR-0016（VMS 被通知方）/ ADR-0017（Orc 被通知方）/ ADR-0020（LSG 被通知方）/ ADR-0021（SSoT 前置）
- **外部**：[SQLite WAL docs](https://www.sqlite.org/wal.html) / [EMA 原理（Wikipedia）](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average)

---

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-24 | v1.0.0 初版：SQLite 时序 + EMA 异常 + Protocol 单向依赖；修复 VG-07；B-e-6 产出。 |
