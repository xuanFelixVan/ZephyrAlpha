---
module_id: MOD-INF-002
title: 运行时集成与 Cross-Layer 缺口填补蓝图（B2 · Phase 0-2）
doc_type: blueprint
status: approved
version: 1.0.1
layer: L01
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.1
valid_from: 2026-05-01
ttl: permanent
construction_progress: merged
dependencies:
  - MOD-INF-001
priority: P0
tags:
  - runtime-integration
  - cross-layer
  - ri-modules
  - event-bus
  - infrastructure
  - phase-0
summary: ZephyrAlpha 运行时集成 6 核心 RI 模块 + Cross-Layer 缺口填补蓝图。覆盖事件总线、模块生命周期、配置中心、错误处理、健康检查、Telemetry 等标准化跨层横切能力。Phase 0-2 渐进落地，所有设计按 1500 模块极限容量考虑。
---

# 运行时集成与 Cross-Layer 缺口填补蓝图（B2 · Phase 0-2）

> **真源声明**：本蓝图是 ZephyrAlpha 运行时集成体系的唯一真源。原始施工图文档 `construction-plan-runtime-integration-and-cl-gaps.md` 经历 Wave 0 三轮审计 + Claude-Opus-4.7 终审，本文档承载终审裁定后的最终方案。

---

## 1. 核心概念

运行时集成（Runtime Integration）是 ZephyrAlpha 基础设施层的**横切能力集合**，解决 14 层模块的跨层协同问题：

| RI 模块 | 名称 | 核心职责 | 权限 |
|---------|------|---------|------|
| **RI-01** | EventBus | 异步事件分发（pub/sub），最多 500 订阅者/事件 | Immutable Core |
| **RI-02** | ModuleLifecycle | 模块 init/start/stop/health 统一生命周期 | Immutable Core |
| **RI-03** | ConfigCenter | 分层配置 (system/module/runtime)，YAML + 环境变量覆盖 | Human-Gated |
| **RI-04** | ErrorHandler | 统一异常分类 + 错误响应 Protocol | Immutable Core |
| **RI-05** | HealthCheck | 模块健康探针 + 依赖健康传导 | Human-Gated |
| **RI-06** | TelemetryCollector | 多 Plane 指标聚合，预聚合 + 10s 推送 | AI-Modifiable |

**设计容量**：所有模块数 × 14 层 = 1500 模块，RI 各组件不漏不崩。

---

## 2. 到需要做什么（回顾大盘 + 用户原意）

**Owner 指示**：
- 所有 Cross-Layer 缺口必须在 Phase 1 填平，不给未来埋雷
- "Layer 之间怎么通信？配置怎么统一管？错误怎么统一处理？"
- RL-001 : 缺事件总线 → 引入 RI-01
- RL-002 : 缺模块管理 → 引入 RI-02
- RL-004 : 97 模块厌氧测试 CI 时间 12 分钟 → 引入 RI-05/06 监控

**Cross-Layer 缺口清单**（来源于架构自检 RL-001 ~ RL-009），本蓝图只列需由 RI 填补的缺口：

| 缺口 ID | 描述 | 填补方案 |
|---------|------|---------|
| RL-001 | 缺跨层通信用事件总线 | RI-01 EventBus |
| RL-002 | 缺统一模块生命周期管理 | RI-02 ModuleLifecycle |
| RL-003 | 缺分层配置中心 | RI-03 ConfigCenter |
| RL-004 | 缺统一 Telemetry 聚合 | RI-06 TelemetryCollector |
| RL-005 | 缺跨模块健康传导 | RI-05 HealthCheck |
| RL-006 | 缺类型安全事件契约 | RI-01 EventBus 类型化事件 |
| RL-007 | 缺模块依赖可视化 | RI-02 ModuleGraph |
| RL-008 | 缺配置漂移自动告警 | RI-03 ConfigValidator |
| RL-009 | 缺跨层错误传播链追踪 | RI-04 ErrorTracer |

---

## 3. 边界

### 3.1 覆盖

- RI-01 ~ RI-06 模块的设计 + 实现
- Cross-Layer 缺口 RL-001 ~ RL-009 填补
- EventBus / ModuleLifecycle / ConfigCenter / ErrorHandler / HealthCheck / TelemetryCollector 的完整生命周期

### 3.2 不覆盖（→ 去哪）

- AI 审计守卫 → MOD-INF-001（capacity-assurance）
- 安全网关（LSG）→ MOD-INF-004（vibe-coding-pipelines）
- 因子计算逻辑 → L02-L03 业务层

---

## 4. 输入 / 基于此设计

| 输入 | 来源 |
|------|------|
| Owner 架构提问 | "Layer 间怎么通信？配置怎么统一管？" |
| Cross-Layer 缺口审计（RL-001~009）| Wave 0 架构自检 |
| Wave 0 终审 | Claude-Opus-4.7 裁决 |
| 原始草稿 | `19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/` |

---

## 5. 架构决策

### 5.1 终选技术栈

| 组件 | 终选 | 理由 |
|------|------|------|
| RI-01 EventBus | **asyncio.Queue + Pydantic 类型化事件** | 零依赖，"够了就别加"原则 |
| RI-02 ModuleLifecycle | **ABC + register/unregister** | 极简，500 模块初始化 < 2s |
| RI-03 ConfigCenter | **YAML + os.environ 覆盖 + Pydantic 校验** | 零依赖配置分层 |
| RI-04 ErrorHandler | **Enum + Protocol** | 异常分类体系，零依赖 |
| RI-05 HealthCheck | **async 探针 + 依赖传导** | 轻量级，可被 OTel 集成 |
| RI-06 TelemetryCollector | **structlog 聚合 + 10s 推送** | 预聚合降低 I/O 压力 |

**零依赖原则**：RI-01 ~ RI-04 纯 Python stdlib + Pydantic，不加 Redis/Kafka 等重量级依赖。Phase 3 服务化时 RI-01 可切换 Kafka/RabbitMQ（口子已保留）。

### 5.2 关键代码骨架

**EventBus**：
```python
# src/zephyr/l01_infrastructure/event_bus.py
class EventBus:
    _subscriptions: dict[str, list[asyncio.Queue]] = {}
    _MAX_PUBLISHERS = 500

    async def publish(self, event_type: str, payload: BaseModel):
        for queue in self._subscriptions.get(event_type, []):
            await queue.put(payload)

    def subscribe(self, event_type: str) -> asyncio.Queue: ...
```

**ModuleLifecycle**：
```python
# src/zephyr/l01_infrastructure/module_lifecycle.py
class BaseModule(ABC):
    module_id: str
    dependencies: list[str] = []

    async def init(self, config: dict) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def health(self) -> HealthStatus: ...
```

### 5.3 RL-001 ~ RL-009 填补方案

| 缺口 | 方案 | Phase | 验收 |
|------|------|-------|------|
| RL-001 跨层通信 | EventBus pub/sub | Phase 1b | 跨层消息延迟 P99 < 100ms |
| RL-002 模块管理 | BaseModule ABC 注册 | Phase 1a | 500 模块 init < 2s |
| RL-003 配置分层 | ConfigCente YAML+env | Phase 1a | 配置漂移检测 + 告警 |
| RL-004 Telemetry | structlog 聚合 | Phase 1b | 预聚合准确率 100% |
| RL-005 健康传导 | HealthCheck 依赖树 | Phase 2 | 故障域隔离 ≥3 域 |
| RL-006 事件类型 | Pydantic 类型化事件 | Phase 1b | mypy 100% |
| RL-007 依赖可视化 | ModuleGraph JSON 导出 | Phase 2 | D3.js 前端可视化 |
| RL-008 配置漂移 | ConfigValidator 定时比对 | Phase 1b | 漂移告警延时 < 30s |
| RL-009 错误传播链 | ErrorTracer trace_id 传递 | Phase 2 | 跨 3 层 trace_id 完整 |

---

## 6. 架构视图

### 6.1 Phase 路线图

| Phase | 名称 | 人日 | 关键交付物 |
|-------|------|:--:|---------|
| **1a** | 骨架上线 | 5-7 | RL-002 ModuleLifecycle + RL-003 ConfigCenter + 空模块注册 |
| **1b** | 核心运行时 | 5-7 | RL-001 EventBus + RL-004 Telemetry + RL-006 类型化事件 + RL-008 ConfigValidator |
| **2** | 完善集成 | 5-7 | RL-005 HealthCheck + RL-007 ModuleGraph + RL-009 ErrorTracer |

### 6.2 验收标准（Phase 2 综合）

| 维度 | 指标 | 目标 |
|------|------|------|
| 性能 | 500 模块 init() 总时间 P99 | ≤2s |
| 性能 | 跨层消息延迟 P99 | ≤100ms |
| 架构 | 模块依赖图 DAG 完整性 | 100%（无孤立节点） |
| 架构 | 配置漂移告警延时 | ≤30s |
| 错误处理 | 跨 3 层错误 trace_id 完整性 | 100% |
| AI | Telemetry 预聚合准确率 | 100% |

---

## 7. 触发条件与扩展路径

| 条件 | 动作 |
|------|------|
| 模块 > 300 | Phase 3 RI-01 切 Kafka/RabbitMQ |
| pub/sub 消费者 > 500/事件 | 触发 EventBus 分片 |
| 配置项 > 1000 | ConfigCenter 加本地缓存层 |
| 并发 Agent > 20 | TelemetryCollector 远程化 |

**EventBus 演进路径**（零断链）：

```
Phase 1b: asyncio.Queue（本地）
Phase 3:   Kafka/RabbitMQ（远程）── 通过 EventBus Protocol 抽象层无缝切换
```

---

## 8. 风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| asyncio.Queue 在 500 模块下内存暴增 | 低 | `_MAX_PUBLISHERS = 500` 硬限制 + 背压机制 |
| ConfigCenter YAML 解析冲突 | 低 | 严格加载顺序：default.yaml → module.yaml → env |
| HealthCheck 依赖传导形成死循环 | 低 | ModuleGraph DAG 拓扑排序，检测 → 死循环告警阻断 |

---

## 9. 关键关联

| 关联文档 | 说明 |
|---------|------|
| `capacity-assurance/blueprint.md` | 容量 SLO + RI 能力协同 |
| `vibe-coding-pipelines/blueprint.md` | RI 模块产自双管线 Wave 0 |
| Cross-Layer 缺口审计 `RL-001~009` | 本蓝图填补方案的真源 |

> **历史溯源**：原始施工图 Wave 0 终审产出（2026-04-27），三轮审计 GLM/Kimi/Qwen + Opus-4.7 终审裁决。2026-05-01 迁入 `03_modules/l01_infrastructure/runtime-integration/blueprint.md`，内容保留，结构按蓝图模板重组。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 运行时集成——orchestrator 9文件已实现

### 10.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/orchestrator/agent_health_monitor.py` | ✅ 已实现 | |
| `src/zephyr/orchestrator/agent_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/orchestrator/deferred_queue.py` | ✅ 已实现 | |
| `src/zephyr/orchestrator/file_task_mapper.py` | ✅ 已实现 | |
| `src/zephyr/orchestrator/hallucination_detector.py` | ✅ 已实现 | |
| `src/zephyr/orchestrator/rollback_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestrator/state_synchronizer.py` | ✅ 已实现 | |
| `src/zephyr/orchestrator/trigger_router.py` | ✅ 已实现 | |
| `src/zephyr/orchestrator/wave_generator.py` | ✅ 已实现 | |

### 10.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_agent_orchestrator.py` | ✅ 已实现 | |
| `tests/unit/test_agent_health_monitor.py` | ✅ 已实现 | |
| `tests/unit/test_hallucination_detector.py` | ✅ 已实现 | |
| `tests/unit/test_rollback_manager.py` | ✅ 已实现 | |
| `tests/unit/test_state_synchronizer.py` | ✅ 已实现 | |
| `tests/unit/test_trigger_router.py` | ✅ 已实现 | |
| `tests/unit/test_file_task_mapper.py` | ✅ 已实现 | |
| `tests/unit/test_wave_generator.py` | ✅ 已实现 | |
| `tests/unit/test_deferred_queue.py` | ❌ 未实现 | |
| `tests/integration/test_agent_e2e.py` | ✅ 已实现 | |

### 10.3 配置文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `config/trigger_router.yaml` | ✅ 已实现 | |
| `config/capabilities.yaml` | ✅ 已实现 | |
| `config/session_state_machine.yaml` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
