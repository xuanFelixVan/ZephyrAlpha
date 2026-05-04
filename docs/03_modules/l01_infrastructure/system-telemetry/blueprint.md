---
module_id: "MOD-INF-015"
title: "System Telemetry 蓝图 — 全系统可观测性：指标/日志/链路/AI行为/存档"
doc_type: blueprint
status: draft
version: "0.2.0"
layer: L12
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: phase_1_partial
summary: "ZephyrAlpha System Telemetry 蓝图——全系统可观测性平台：5个子系统(metrics/logs/traces/ai_behavior/archive)覆盖4大黄金信号(延迟/错误/流量/饱和度)。P2-1量化追踪落地：新增 `src/zephyr/telemetry/blueprint_metrics.py`（record_blueprint_read instrumentation）+ SLI表中新增 BLUEPRINT-READ-FREQ 和 BLUEPRINT-STALENESS 两项蓝图效能SLI。experimental T-V2-011。"
tags: [telemetry, system-telemetry, l12, metrics, logs, traces, ai-behavior, observability, infrastructure]
priority: P2
depends_on:
  - {target: "MOD-INF-010", at: "全篇", why: "Feedback Loop Engine——FLE消费metrics/logs做异常检测与自动派单"}
  - {target: "MOD-INF-012", at: "全篇", why: "Database——olap_engine持久化FLE时序分析结果"}
---

# System Telemetry 蓝图

> **module_id**: MOD-INF-015 | **version**: 0.1.0 | **status**: draft | **layer**: L12

> **真源声明**：本蓝图的 canonical SSoT 为 `src/zephyr/l12_system_telemetry/` 代码目录。
> 代码落位：`src/zephyr/l12_system_telemetry/`（5 子模块，当前骨架）。

> **对标**：Google SRE 4 Golden Signals + OpenTelemetry 规范 + RED Method (Rate/Errors/Duration).

---

## 1. 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-015 |
| 代码落位 | `src/zephyr/l12_system_telemetry/` |
| 核心职责 | 全系统可观测性——采集/存储/查询所有组件的运行时数据 |
| 设计原则 | 每个模块自上报→Telemetry聚合→FLE消费→自动派单 |

### 核心职能

System Telemetry 是 ZephyrAlpha 的**"神经系统"**——感知所有模块的健康状态，将原始信号转化为可操作的洞察。它与 FLE（Feedback Loop Engine）配合：**Telemetry 负责"看见"，FLE 负责"行动"**。

---

## 2. 四大黄金信号

对标 Google SRE 4 Golden Signals：

| 信号 | 维度 | 采集来源 | 阈值示例 |
|------|------|---------|---------|
| **Latency**（延迟） | LLM API 响应时间 / 脚本执行时长 / Pipeline 端到端耗时 | MCP servers / subprocess tracker | P95 > 30s → FLE 告警 |
| **Errors**（错误） | LLM 调用失败 / Gate 拒止 / 校验不通过 | Gate Engine / CE / Script System | 错误率 > 5% → FLE 自动降级 |
| **Traffic**（流量） | LLM 调用总量 / 任务卡生成速率 / API 请求 QPS | Pipeline / LSG / MCP | LLM QPS > 100 → Token Budget 预警 |
| **Saturation**（饱和度） | Context Engine Token 填充率 / VMS Collection 占用 / DB 连接池 | CE / VMS / Database | CE 填充 > 90% → 自动截断旧 Session |

---

## 3. 五子系统

```
src/zephyr/l12_system_telemetry/
├── metrics/       ← 数值指标：LLM调用次数 / Gate通过率 / 任务完成率
├── logs/          ← 结构化日志：JSON log→CE注入 / Gate审计 / Pipeline异常
├── traces/        ← 分布式链路：TaskCard全生命周期追踪（draft→pipeline→complete）
├── ai_behavior/   ← AI行为监控：模型选择频率 / Token消耗 / Gate命中率
└── archive/       ← 历史存档：冷数据压缩归档（>30天）
```

| 子系统 | 职责 | 数据格式 | 消费方 | 施工状态 |
|--------|------|---------|--------|:---:|
| **metrics** | SLI/SLO 与业务指标流 | `MetricPoint {name, value, timestamp, labels}` | FLE / Capacity Assurance | 🟡 骨架 |
| **logs** | 结构化日志聚合与检索 | JSON Lines（`event_id` + `module` + `level`） | Gate Engine / Audit | 🟡 骨架 |
| **traces** | TaskCard 全链路追踪 | Span（Root→M1→G2→Orc→Script→Complete） | Pipeline / Debug | 🟡 骨架 |
| **ai_behavior** | AI 模型行为画像 | 模型选择日志 / Token消耗 / Gate命中率时序 | FLE / Capacity Assurance | 🟡 骨架 |
| **archive** | 冷数据压缩归档 | gzip JSONL（30天后自动归档） | 审计回溯 | 🟡 骨架 |

---

## 4. metrics 子系统

```
metrics 采集流程:
  各模块调用 metrics.report(MetricPoint)
    → MetricPoint 进入环形缓冲区(容量 1000)
    → 每 60s 批量 flush 到 SQLite metrics 表
    → FLE 定时查询 metrics 表做异常检测
```

### MetricPoint Schema

```python
@dataclass
class MetricPoint:
    name: str          # 指标名称（如 "llm_api_latency_ms"）
    value: float       # 数值
    timestamp: float   # Unix 时间戳
    labels: dict       # 维度标签（module / version / model）
    type: str          # gauge / counter / histogram
```

### 关键 SLI

| SLI | 公式 | SLO |
|-----|------|:---:|
| LLM 可用性 | Successful_Calls / Total_Calls | ≥ 99.5% |
| Gate 通过率 | Passed_Tasks / Total_Tasks_at_Gate | ≥ 95% |
| Pipeline 完成率 | Completed_Tasks / Dispatched_Tasks | ≥ 90% |
| Token 效率 | Useful_Output_Tokens / Total_Input_Tokens | ≥ 0.3 |
| BLUEPRINT-READ-FREQ | COUNT(blueprint_reads WHERE blueprint_id=X) | ≥ 1 / session（目标）|
| BLUEPRINT-STALENESS | now() - MAX(blueprint.last_updated) | ≤ 30 days |

---

## 5. logs 子系统

```
logs 采集流程:
  各模块调用 structured_logger.info(event)
    → 格式化为 JSON Line（structlog 风格）
    → 写入 l12_system_telemetry/logs/{date}.jsonl
    → Gate Engine 定期扫描 ERROR/FATAL 日志触发升级
```

### 日志分级

| Level | 用途 | 示例 |
|-------|------|------|
| DEBUG | 开发调试信息 | Context Engine token count |
| INFO | 正常业务流程 | "Task T-001 dispatched to Pipeline A" |
| WARNING | 阈值预警 | "VMS tokens bucket usage > 80%" |
| ERROR | 可恢复错误 | "LLM API timeout, retry 3/5" |
| FATAL | 不可恢复，需人工介入 | "SQLite corruption detected" |

---

## 6. traces 子系统

```
TaskCard 全链路追踪:
  Root Span (TaskCard创建)
    ├── M1 Span (Context Engine build)
    │   └── inject Span (CE merge)
    ├── Gate Span (G0-G7 逐门禁)
    ├── Orc Span (Pipeline dispatch)
    │   ├── M6 Span (A区起草)
    │   └── M8 Span (B区审计)
    ├── Script Span (D1-D12 质量检查)
    └── Complete Span (写入知识库 / 交付记录)
```

**Trace 数据结构**：

```python
@dataclass
class Span:
    trace_id: str      # 整条链路 ID
    span_id: str       # 当前 Span ID
    parent_span_id: str  # 父 Span ID
    module: str        # 当前模块
    start_time: float
    end_time: float
    status: str        # ok / error / timeout
    metadata: dict     # 模块自定义元数据
```

---

## 7. ai_behavior 子系统

> 监控 AI 模型的行为健康度——不是代码的 bug，是模型的"偏航"。

### 监测维度

| 维度 | 指标 | 告警阈值 |
|------|------|:---:|
| **模型选择偏差** | 各模型调用占比 | 单模型占比 > 80% → 路由异常 |
| **Token 消耗异常** | 每任务 token 消耗 | 超出基线 3σ → 模型"废话模式" |
| **Gate 命中率** | 各 Gate 拒绝比例 | G0 reject > 20% → 输入质量下降 |
| **输出一致性** | 同 prompt 重复输出差异 | 差异 > 50% → 幻觉风险 |

---

## 8. archive 子系统

```
归档策略:
  metrics 表 → 30天后压缩归档到 archive/metrics/
  logs/ → 30天后 gzip → archive/logs/
  traces/ → 7天后压缩归档（trace 数据量大）
  archive/ 下文件保留 90 天后物理删除
```

---

## 9. 施工进度

| 子系统 | 阶段 | 完成度 | 下一步 |
|--------|------|:---:|------|
| metrics | scaffold | ██ 20% | MetricPoint 数据类定义 + ring buffer |
| logs | scaffold | ██ 20% | structlog 配置 + JSONL writer |
| traces | scaffold | █░ 10% | Span 数据结构定义 |
| ai_behavior | scaffold | ░░ 5% | 概念设计完成，代码未开工 |
| archive | scaffold | ░░ 5% | gzip 归档脚本骨架 |

### 下一步施工

| 优先级 | 任务 | 预估工时 |
|:---:|------|:---:|
| P0 | `metrics/__init__.py` → MetricPoint + ring_buffer + flush | 4h |
| P0 | `logs/__init__.py` → structlog config + JSONL file writer | 3h |
| P1 | `traces/__init__.py` → Span + SpanContext + trace_id 生成 | 3h |
| P2 | `ai_behavior/__init__.py` → model_selector tracker | 2h |
| P2 | `archive/__init__.py` → gzip compressor + TTL reaper | 2h |

---

## 10. 施工指引

### 10.1 metrics 施工

```
1. 创建 MetricPoint 数据类（name/value/timestamp/labels/type）
2. 实现 RingBuffer（collections.deque, maxlen=1000）
3. 实现 flush() → SQLite metrics 表批量写入
4. 暴露 report(metric: MetricPoint) 接口供各模块调用
```

### 10.2 logs 施工

```
1. 配置 structlog（JSONRenderer + Timestamper）
2. 实现 JSONLFileWriter——按日轮转，文件名 {date}.jsonl
3. 暴露 get_logger(module_name) → BoundLogger
4. 集成 fail-closed：日志写入失败 → stderr fallback
```

### 10.3 测试清单

```
□ MetricPoint 序列化/反序列化
□ RingBuffer 满时自动丢弃最旧数据
□ flush() 批量写入 SQLite 原子性
□ JSONL 日志文件按日轮转
□ archive gzip 压缩后原文件删除
□ FLE 消费 metrics 延迟 < 1s (P99)
```

---

## 11. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 系统遥测——5子模块目录结构已建，代码全skeleton

### 11.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/telemetry/blueprint_metrics.py` | ✅ 已实现 | T-V2-011 experimental — `record_blueprint_read()` instrumentation |

### 11.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §11（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 12. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|------|
| 0.1.0 | 2026-05-03 | 初始创建——5子系统 skeleton + 4黄金信号 SLI |
| 0.1.1 | 2026-05-03 | 施工进度扩展——§11 路径索引 + 施工指引 |
| 0.2.0 | 2026-05-04 | P2-1 量化追踪落地——新增 BLUEPRINT-READ-FREQ / BLUEPRINT-STALENESS SLI 到 §3 metrics 子系统；新增 `src/zephyr/telemetry/blueprint_metrics.py`（`record_blueprint_read()` instrumentation 写入 JSONL）；§11.1 路径索引注册新文件。关联决策：R92。 |
