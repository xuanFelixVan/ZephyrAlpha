---
version: "3.1.0"
doc_type: construction_plan
module_id: MOD-INF-001
status: archived
layer: L01
owner: ZephyrAlpha-Owner
created_at: 2026-04-25
updated_at: 2026-05-02
superseded_by: "D:\\ZephyrAlpha\\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
archive_reason: "Wave 0 施工内容已完整合并进 blueprint.md。本文件保留为历史审计证据。"
---

# 容量保障体系施工图

> **v3.1 升级**：保留v3.0极限容量设计，新增多进程/分布式/分片扩展口子，压缩三轮审计为精华归档，追加Kimi发散探索。
> Owner明确指示：未来不止1000模块，可能1500+甚至更多；所有设计按极限容量考虑，现在把能改的改了，不给未来埋雷；为系统保留多进程架构+分布式事件总线+数据库分片的口子。

## 项目边界与容量声明

1. **本施工图只覆盖容量保障基础设施**（L0-L3），不覆盖交易业务层（L4-L8）容量设计。
2. **当前系统规模**：97个蓝图/44个实现文件，按1500模块设计/5000模块预留/10000+极限容量。
3. **容量上限声明**：单进程Python + SQLite + asyncio架构的极限约为1500模块；超过此限需启用多进程/分布式扩展口子。

## 系统极限容量分析

| 瓶颈维度 | 1500模块设计目标 | 5000模块预留目标 | 10000+极限容量 | 当前状态 | 扩展策略 |
|---------|----------------|----------------|--------------|---------|---------|
| 启动时间 | <30s | <60s | <120s | ~5s@44模块 | 懒加载+多进程 |
| 内存占用 | <2GB | <4GB | <8GB | ~200MB@44模块 | 模块卸载+分片 |
| 事件总线吞吐 | 1000 msg/s | 5000 msg/s | 10000 msg/s | ~100 msg/s | Redis Streams |
| 类型检查时间 | <30s | <60s | <120s | ~3s@44模块 | dmypy增量+分层 |
| 数据库写TPS | 100 TPS | 500 TPS | 1000 TPS | ~10 TPS | PostgreSQL/TiDB |
| 模块间调用延迟 | <10ms | <50ms | <100ms | ~1ms | 本地调用优化 |
| AI上下文覆盖率 | 60% | 40% | 20% | ~95%@44模块 | 上下文压缩 |
| 配置一致性检查 | <10s | <30s | <60s | ~1s@44模块 | 增量验证+缓存 |

---

## 1. 背景与目标

### 1.1 问题背景

ZephyrAlpha 当前处于 Phase 2（施工图纸阶段），已有约 97 个蓝图和 44 个实现文件。随着系统向 1000+ 模块演进，以下容量瓶颈已出现或即将出现：

- **启动时间**：当前约 5 秒，按线性增长估算，1000 模块时可能达到 50-120 秒
- **内存占用**：当前约 200MB，1000 模块时可能达到 2-4GB
- **配置一致性检查**：当前约 1 秒，1000 模块时可能达到 10-30 秒
- **类型检查时间**：当前约 3 秒，1000 模块时可能达到 30-90 秒
- **事件总线吞吐**：当前无背压机制，高并发时可能 OOM

### 1.2 目标

构建一套**容量保障体系**，确保系统在 1500 模块规模下仍能健康运行，并为 5000+ 模块预留扩展能力。

### 1.3 成功标准

| 指标 | 当前值 | 1500模块目标 | 5000模块预留 | 测量方式 |
|------|--------|------------|------------|---------|
| 启动时间 | ~5s | <30s | <60s | 基准测试 |
| 内存占用 | ~200MB | <2GB | <4GB | 内存分析器 |
| 类型检查 | ~3s | <30s | <60s | dmypy基准 |
| 配置检查 | ~1s | <10s | <30s | validate_ssot.py |
| 事件背压 | 无 | 有 | 有 | 压力测试 |
| 模块懒加载 | 无 | 有 | 有 | 启动分析 |
| 故障域隔离 | 无 | 有 | 有 | 故障注入测试 |
| AI上下文覆盖率 | ~95% | 60% | 40% | 上下文分析 |

---

## 2. 核心概念与设计原则

### 2.1 三级容量目标

```
┌─────────────────────────────────────────────────────────────┐
│  设计容量（1500模块）—— 当前架构可直接支撑                    │
│  预留容量（5000模块）—— 通过扩展口子渐进升级可支撑            │
│  极限容量（10000+模块）—— 需要架构级重构                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 容量保障三层框架

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 治理层（Governance）                               │
│  - 容量SLI/SLO标准定义（capacity_slo.yaml）                  │
│  - 容量治理闭环（capacity_governance_loop.py）               │
│  - AI审计守卫（ai_audit_guard.py）                           │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 运行时层（Runtime）                                │
│  - 事件总线背压（event_bus.py）                              │
│  - 故障域隔离（fault_isolator.py）                           │
│  - 模块懒加载（lazy_loader.py）                              │
│  - 契约测试（contract_tester.py）                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 结构层（Structure）                                │
│  - 源码树统一（src/zephyr/）                                 │
│  - 增量类型检查（dmypy）                                     │
│  - 分层pre-commit（.pre-commit-config.yaml）                 │
│  - 层依赖规则（import-rules.yaml + import-linter）           │
│  - SSoT验证（validate_ssot.py）                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 设计原则

1. **渐进式**：所有优化按 Phase 0→1→2→3 渐进实施，不一次性引入过多复杂度
2. **可测量**：每个优化必须有明确的 SLI/SLO 指标和测量方式
3. **可回滚**：每个变更必须有回滚机制（如懒加载可关闭、背压可禁用）
4. **零外部依赖**：优先使用 Python 标准库和已有依赖，不引入新的重型依赖
5. **AI自治安全**：所有 AI 可修改的配置必须有审计和制衡机制

---

## 3. 架构设计

### 3.1 总体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        容量治理层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ capacity_   │  │ ai_audit_   │  │ capacity_   │         │
│  │ slo.yaml    │  │ guard.py    │  │ governance_ │         │
│  │ (Human-     │  │ (Immutable  │  │ loop.py     │         │
│  │  Gated)     │  │  Core)      │  │ (AI-Modif)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                        运行时层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ event_bus   │  │ fault_      │  │ lazy_loader │         │
│  │ _backpressure│  │ isolator.py │  │ .py         │         │
│  │ (AI-Modif)  │  │ (Human-     │  │ (Human-     │         │
│  │             │  │  Gated)     │  │  Gated)     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                        结构层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ validate_   │  │ pre-commit  │  │ import-     │         │
│  │ ssot.py     │  │ _layers     │  │ linter      │         │
│  │ (Immutable  │  │ (Immutable  │  │ (Human-     │         │
│  │  Core)      │  │  Core)      │  │  Gated)     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 ContractBus 核心架构

```python
from typing import Protocol, Callable
from pydantic import BaseModel

class ContractBus(Protocol):
    """跨层模块通信抽象总线"""
    async def request(self, producer: str, consumer: str, payload: BaseModel) -> BaseModel: ...
    async def publish(self, topic: str, payload: BaseModel) -> None: ...
    def register_handler(self, topic: str, handler: Callable, schema: type[BaseModel]) -> None: ...
```

**Schema Enforcement**：所有通过 ContractBus 传输的数据必须使用 Pydantic v2 模型定义，运行时自动校验。

---

## 4. 模块分解

| 模块ID | 模块名称 | 职责 | 输入 | 输出 | 依赖 | AI自治权限 |
|--------|---------|------|------|------|------|-----------|
| M-01 | CTR-001修复 | 修复 governance-asset-inventory.yaml 中 CTR-001 字段 | 原始文件 | 修复后的文件 | 无 | Immutable Core |
| M-02 | 源码树统一 | 统一为单一 src/zephyr/ 源码树 | 旧源码树 | 新源码树 | M-01 | Immutable Core |
| M-03 | validate_ssot.py | SSoT 验证脚本 | governance-asset-inventory.yaml | 验证报告 | M-01 | Immutable Core |
| M-04 | lazy_loader.py | 模块懒加载 | 模块ID | 模块实例 | M-02 | Human-Gated |
| M-05 | pre-commit分层 | 分层 pre-commit 配置 | .pre-commit-config.yaml | 增量检查 | M-02 | Immutable Core |
| M-06 | dmypy配置 | 增量类型检查配置 | mypy.ini | 类型报告 | M-02 | AI-Modifiable |
| M-07 | event_bus背压 | 事件总线背压机制 | 事件流 | 背压控制 | M-02 | AI-Modifiable |
| M-08 | import-linter | 层依赖规则检查 | .importlinter | 违规报告 | M-02 | Human-Gated |
| M-09 | ContractBus接口 | 跨层通信抽象 | 模块调用 | 契约校验 | M-02 | Human-Gated |
| M-10 | ZephyrLogger+OTel | 结构化日志+Metrics | 日志事件 | 日志+Metrics | M-02 | AI-Modifiable |
| M-11 | contract_tester.py | 契约测试框架 | ContractBus调用 | 测试报告 | M-09 | Human-Gated |
| M-12 | config_validator.py | 配置参数验证 | config/*.yaml | 验证报告 | M-02 | Human-Gated |
| M-13 | fault_isolator.py | 故障域隔离 | 异常事件 | 隔离动作 | M-07 | Human-Gated |
| M-14 | warm_hot_gate.py | Warm→Hot 阻断门 | 状态变更请求 | 阻断/放行 | M-13 | Human-Gated |
| M-15 | pydantic_v2_migrator.py | Pydantic v2 迁移工具 | v1模型 | v2模型 | M-02 | Human-Gated |
| M-16 | event_bus_upgrade.py | 事件总线升级（asyncio→Redis） | 事件流 | 分布式事件 | M-07 | Human-Gated |
| M-17 | ai_audit_guard.py | AI修改审计守卫 | AI修改请求 | 审计结果 | M-02 | Immutable Core |
| M-18 | capacity_slo.yaml | 容量SLI/SLO标准 | 容量指标 | SLO定义 | M-02 | Human-Gated |
| M-19 | capacity_governance_loop.py | 容量治理闭环 | 容量指标 | 修复动作 | M-18 | AI-Modifiable |
| M-20 | ttl_cleanup_engine.py | 派生文件TTL清理 | 文件元数据 | 清理报告 | M-02 | AI-Modifiable |

---

## 5. 技术选型

| # | 组件 | 技术 | 理由 | 极端容量支持 | AI自治权限 |
|---|------|------|------|------------|-----------|
| T-01 | SSoT验证 | Python + PyYAML | 零外部依赖，解析 governance-asset-inventory.yaml | 增量解析+缓存 | Immutable Core |
| T-02 | 懒加载 | `__getattr__` + 模块注册表 | Python原生，无额外依赖 | 分层加载+卸载 | Human-Gated |
| T-03 | pre-commit | pre-commit框架 | 社区标准，增量检查支持 | 分层配置+并行 | Immutable Core |
| T-04 | 类型检查 | dmypy（mypy守护进程） | 增量检查，内存缓存 | 分层检查+缓存 | AI-Modifiable |
| T-05 | 层依赖检查 | import-linter | 专门用于Python层依赖检查 | 规则缓存+增量 | Human-Gated |
| T-06 | 日志 | structlog + OpenTelemetry SDK | 结构化日志+CNCF三支柱 | 采样+异步输出 | AI-Modifiable |
| T-07 | 事件总线 | asyncio.Queue + 背压 | Python原生，零外部依赖 | Redis Streams（条件触发） | AI-Modifiable |
| T-08 | 契约测试 | 自研轻量框架 | 无需重型测试框架 | 并行执行+缓存 | Human-Gated |
| T-09 | 配置验证 | Pydantic v2 | 已有依赖，类型安全 | 增量验证+缓存 | Human-Gated |
| T-10 | 故障隔离 | pybreaker + tenacity | 已有依赖，成熟方案 | 分布式Circuit Breaker | Human-Gated |
| T-11 | Pydantic迁移 | bump-pydantic工具 | 官方迁移工具 | 批量迁移+回滚 | Human-Gated |
| T-12 | 事件总线升级 | Redis Streams（条件触发） | 轻量级消息队列 | Kafka（未来） | Human-Gated |
| T-13 | AI审计 | 自研轻量规则引擎 | 无需OPA等重型方案 | 本地LLM评估（未来） | Immutable Core |
| T-14 | 容量治理 | SQLite + EMA异常检测 | 复用FLE已有方案 | InfluxDB（未来） | AI-Modifiable |

---

## 6. 数据流与交互设计

### 6.1 容量治理闭环数据流

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  指标采集    │───▶│  趋势检测    │───▶│  预警触发    │───▶│  修复执行    │
│ (ZephyrLogger│    │ (EMA+3σ)    │    │ (阈值规则)   │    │ (自动化脚本) │
│  + structlog)│    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ▲                                                       │
       │                                                       ▼
       │                                              ┌─────────────┐
       │                                              │  效果验证    │
       │                                              │ (回归测试)   │
       │                                              └─────────────┘
       │                                                       │
       └───────────────────────────────────────────────────────┘
                          策略回写（若有效）
```

### 6.2 AI修改审计数据流

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ AI-Modifiable   │────▶│ ai_audit_guard  │────▶│ Immutable Core  │
│ 模块（修改请求） │     │ （独立审计）     │     │ （审计规则）     │
│                 │     │                 │     │                 │
│ knowledge_engine│     │ 1.记录修改前状态 │     │ 审计规则不可被   │
│ event_bus       │     │ 2.验证修改合理性 │     │ AI修改          │
│ config_validator│     │ 3.异常时阻断     │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │ 审计日志（只读）  │
         │              │ Provenance Chain │
         │              └─────────────────┘
         ▼
┌─────────────────┐
│ 修改执行（若通过）│
└─────────────────┘
```

---

## 7. 与现有系统集成

### 7.1 与 ADR-0010（治理三层边界）集成

P2-6 故障域隔离和 P2-8 Warm→Hot 阻断的权限归属需参照 ADR-0010 定义的 Immutable/Human-Gated/AI-Modifiable 三层。`fault_isolator.py` 属于 Human-Gated，`warm_hot_gate.py` 属于 Human-Gated。

### 7.2 与 ADR-0011（Runtime Planes 正交视图）集成

P2-6 故障域设计需在 ADR-0011 的 hot-path/warm-path/cold-path 三平面基础上新增"域内子域划分+水密门设计"。每个运行平面内按因子域/风控域/执行域进一步划分子域。

### 7.3 与 ADR-0019（Feedback Loop Engine）集成

P2-6 的 Error Budget 耗尽→自动进入保守模式，需与 ADR-0019 的 SQLite 时间序列+EMA 异常检测集成。Feedback Loop Engine 提供"异常检测信号"，fault_isolator.py 据此触发 Circuit Breaker。

### 7.4 与 technology-landscape.yaml 集成

新增 10 项技术选型需与现有 43 条技术条目做冲突检查。pybreaker 和 tenacity 已在 Adopt 级，组合使用不违反选型原则。

### 7.5 与 invariants.yaml 集成

新增 INV-NEW-001/002 需与现有 16 条不变量做冲突检查。INV-011 Cold→Hot 禁止直通是 INV-NEW-001 的特例，应合并而非新增。

---

## 8. 实施路线图

### Phase 0（当前，1-2 人日）

| 任务 | 工作量 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| P0-1 CTR-001 手动修复 | 0.5h | 修复后的 governance-asset-inventory.yaml | validate_ssot.py 无矛盾报告 |
| P0-2 统一源码树迁移 | 4-8h | 单一 `src/zephyr/` + 删除旧树 | 所有 import 路径更新，测试全通过 |
| P0-3 validate_ssot.py | 4-6h | `scripts/governance/validate_ssot.py` | 检测到 CTR-001 同类矛盾 |
| P0-4 capacity_slo.yaml | 2-4h | `config/capacity/capacity_slo.yaml` | 定义 ≥6 个量化 SLI/SLO 指标 |
| P0-5 ai_audit_guard 骨架 | 4-6h | `src/zephyr/shared/ai_audit_guard.py` | 可拦截 AI 修改请求并记录 Provenance |

**Phase 0 合计**：14.5-26.5h ≈ 2-3 人日

### Phase 1（立即，≤5 人日，拆分为 1a+1b）

**Phase 1a（结构容量，≤3 人日）**：

| 任务 | 工作量 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| P1-1 `__getattr__` 懒加载 | 2-4h | `src/zephyr/__init__.py` | 启动时间 <2s@97 模块 |
| P1-3 pre-commit 分层 | 3-4h | `.pre-commit-config.yaml` 更新 | 增量 commit 检查 <10s |
| P1-4 dmypy 配置 | 1-2h | `mypy.ini` | 增量类型检查 <15s |
| P1-6 import-linter | 2-4h | `.importlinter` + `import-rules.yaml` | 0 层内循环依赖 |
| P1-8 ZephyrLogger+OTel | 3-4h | `src/zephyr/shared/zephyr_logger.py` | 日志+Metrics 双输出 |

**Phase 1a 合计**：11-18h ≈ 1.5-2.5 人日 ✅

**Phase 1b（通信+运行时，≤3 人日）**：

| 任务 | 工作量 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| P1-5 事件总线背压 | 4-6h | `src/zephyr/shared/event_bus.py` | 生产者>消费者时无 OOM |
| P1-7 ContractBus 接口（第一批 15 文件） | 10-14h | `src/zephyr/shared/contract_bus.py` + 15 文件迁移 | 第一批 15 文件测试全通过 |
| P1-9 ContractBus Schema Enforcement | 3-4h | Pydantic 模型定义 | 错误格式数据被拒绝而非崩溃 |
| P1-10 ai_audit_guard 规则配置 | 2-3h | `config/audit/audit_rules.yaml` | 覆盖 knowledge_engine/event_bus/config_validator |
| P1-11 capacity_governance_loop 骨架 | 4-6h | `src/zephyr/shared/capacity_governance_loop.py` | 可采集 ≥3 个容量指标 |

**Phase 1b 合计**：23-33h ≈ 3-4 人日 ✅

### Phase 2（短期，5-7 人日）

| 任务 | 工作量 | 触发条件 | 交付物 |
|------|--------|---------|--------|
| P2-1 YAML 增量验证 | 6-8h | Phase 1 完成 | 增量解析器 |
| P2-3 契约测试 | 8-12h | ContractBus 迁移 ≥50% | 自研轻量契约测试 |
| P2-6 故障域隔离 | 6-8h | 模块数>150 | fault_isolator.py |
| P2-8 Warm→Hot 阻断 | 3-4h | Hot Plane 激活前 | warm_hot_gate.py |
| P2-9 ContractBus 迁移（第二+三批） | 10-14h | 第一批验证通过 | 剩余 29 文件迁移完成 |

**Phase 2 合计**：33-46h ≈ 4-6 人日

### Phase 3（中期，条件触发）

| 任务 | 触发条件 | 工作量 |
|------|---------|--------|
| P3-1 Pydantic v2 迁移 | 确认使用 v1 且版本冲突 | 4-6h |
| P3-2 Redis 升级 | Queue 深度>1000 持续 1 小时 | 6-10h |
| P3-3 知识引擎精简 | 模块数>300 | 4-6h |
| P3-4 AI 上下文压缩（40% 目标） | 上下文窗口不足率>50% | 4-6h |

---

## 9. 风险与缓解

| # | 风险 | 影响 | 概率 | 缓解措施 | 责任人 |
|---|------|------|------|---------|--------|
| R-01 | ContractBus 迁移引入循环依赖 | 高 | 中 | import-linter 强制检查 + 迁移追踪器 | Human-Gated |
| R-02 | 懒加载导致调试困难 | 中 | 高 | 提供 `ZEPHYR_EAGER_LOAD=1` 环境变量 | AI-Modifiable |
| R-03 | 事件背压导致事件丢失 | 高 | 中 | 背压阈值 Human-Gated + 丢弃事件审计日志 | Human-Gated |
| R-04 | AI 修改审计规则被绕过 | 高 | 低 | ai_audit_guard 属于 Immutable Core | Immutable Core |
| R-05 | capacity_slo.yaml 阈值设置不当 | 中 | 中 | 阈值调整需 Owner 审批 + 7 天观察期 | Human-Gated |
| R-06 | 故障域隔离过度导致系统僵化 | 中 | 中 | 隔离规则可 AI-Modifiable + 渐进启用 | AI-Modifiable |
| R-07 | 5000 模块预留目标过于乐观 | 高 | 中 | 每 300 模块做一次容量基准测试 | Human-Gated |
| R-08 | 单人项目维护负担过重 | 高 | 高 | AI-Modifiable 组件自动运行 + 告警聚合 | AI-Modifiable |
| R-09 | 扩展口子"死代码"成为理解负担 | 中 | 高 | 扩展口子启用需 Owner 审批 + 文档明确标注 | Human-Gated |
| R-10 | 多进程扩展引入序列化开销 | 中 | 中 | Backend 抽象层支持零拷贝序列化 | Human-Gated |

---

## 10. 开放问题

| # | 问题 | 状态 | 决策人 |
|---|------|------|--------|
| Q-01 | 1500 模块的启动时间目标（<30s）是否过于乐观？ | 待验证 | Owner |
| Q-02 | AI 上下文压缩 40% 目标是否会导致信息损失？ | 待实验 | Owner |
| Q-03 | ContractBus 迁移分三批（15+15+14）是否最优？ | 待验证 | Owner |
| Q-04 | 事件总线背压阈值初始值设为多少？ | 待实验 | Owner |
| Q-05 | capacity_slo.yaml 的 6 个 SLI 是否覆盖全部关键路径？ | 待评审 | Owner |
| Q-06 | 多进程扩展时模块间调用延迟预算？ | 待设计 | Owner |
| Q-07 | 数据库分片策略（一致性哈希 vs 范围分片）？ | 待决策 | Owner |
| Q-08 | 分布式事件总线序列化格式（JSON vs MessagePack vs Protobuf）？ | 待决策 | Owner |

---

## AI 自治权限总表

| 模块 | 权限 | Provenance Chain | 理由 |
|------|------|-----------------|------|
| ai_audit_guard.py | Immutable Core | 自身代码变更需 Owner 审批 | 审计器不可被 AI 修改 |
| audit_rules.yaml | Human-Gated | 修改需记录 who/when/why | 审计规则由 Owner 定义 |
| capacity_slo.yaml | Human-Gated | 修改需记录 who/when/why | SLO 标准由 Owner 定义 |
| capacity_governance_loop.py | AI-Modifiable | 每次执行记录指标采集结果 | 自动化执行修复剧本 |
| ai_provenance 表 | Immutable Core | 只追加不删除，hash 链完整性校验 | 审计日志不可篡改 |
| capacity_metrics 表 | AI-Modifiable | 可追加可更新，保留 7 天历史 | 指标数据可自动清理 |
| lazy_loader.py | Human-Gated | 策略变更需 Owner 审批 | 影响启动顺序和模块可见性 |
| event_bus.py | AI-Modifiable | 背压阈值调整需记录 | 运行时参数可 AI 调 |
| config_validator.py | Human-Gated | 验证规则变更需 Owner 审批 | AI 定义验证规则=定义什么是合法的 |
| ZephyrLogger | AI-Modifiable（日志级别）/ Human-Gated（采样率） | 级别调整记录/采样率调整记录 | 采样率影响存储和审计完整性 |

---

## 争议清单

| # | 争议ID | 争议描述 | GLM 立场 | Kimi 立场 | Qwen 立场 | 采纳 |
|---|--------|---------|---------|---------|---------|------|
| 1 | D-01 | 1500 模块设计容量 vs 1000 模块 | 1000 模块 | 1500 模块（极限预留） | 1500 设计/5000 预留 | 采纳 Kimi |
| 2 | D-02 | 事件总线背压阈值由谁控制 | AI-Modifiable | Human-Gated（安全关键） | AI-Modifiable + 审计 | 采纳 Qwen |
| 3 | D-03 | ContractBus 是否必须 Schema Enforcement | 必须（P0） | 必须（P0） | 必须（P1b） | 采纳 GLM/Kimi |
| 4 | D-04 | ai_audit_guard 是否必须 P0 | 未识别 | 必须 P0 | 骨架 P0 + 规则 P1b | 采纳 Qwen |
| 5 | D-05 | ADR-0011 引用路径 | 错误路径 | 错误路径 | 实际文件名已验证 | 采纳 GLM |
| 6 | D-06 | 扩展口子是否现在实现 | Hold 至触发条件 | 预留接口现在实现 | 预留接口现在实现 | 采纳 Kimi/Qwen |
| 7 | D-07 | 数据库分片策略 | 一致性哈希 | 范围分片 | 一致性哈希 | 采纳 GLM/Qwen |
| 8 | D-08 | 序列化格式 | JSON | MessagePack | JSON（现在）+ Protobuf（未来） | 采纳 Qwen |

---

## 务实修正

| # | 修正项 | 原方案 | 修正后 | 理由 |
|---|--------|--------|--------|------|
| 1 | CTR-001 修复方式 | 手动修复 | 手动修复 + validate_ssot.py 自动检测 | 防止同类问题复发 |
| 2 | 源码树迁移 | 直接删除旧树 | git mv + 保留 30 天 | 防止误删 |
| 3 | 懒加载实现 | `__import__` 拦截 | `__getattr__` + 模块注册表 | 更符合 Python 惯例 |
| 4 | pre-commit 分层 | 全量检查 | 增量检查 + 分层配置 | 减少等待时间 |
| 5 | dmypy 配置 | 默认配置 | 增量模式 + 内存缓存 | 减少重复检查 |
| 6 | 事件背压 | 固定阈值 | 动态阈值 + AI 可调 | 适应不同负载 |
| 7 | ContractBus 迁移 | 全量 44 文件 | 分三批（15+15+14） | 控制回归风险 |
| 8 | AI 审计规则 | 硬编码规则 | YAML 配置 + 版本控制 | 便于调整 |

---

## 单人项目适配性检查

| 检查项 | 要求 | 当前状态 | 适配措施 |
|--------|------|---------|---------|
| 维护人力 | 1 人 + AI | ✅ 满足 | AI-Modifiable 组件自动运行 |
| 学习曲线 | 每项技术 <1 天 | ⚠️ 部分满足 | import-linter 需 2-3 天学习 |
| 运维成本 | 无独立服务 | ✅ 满足 | 全部嵌入式，无 Docker/K8s |
| 回滚能力 | 每项变更可回滚 | ✅ 满足 | 环境变量 + 配置开关 |
| 告警噪音 | <5 条/天 | ⚠️ 待验证 | 告警聚合 + 分级 |
| 扩展口子 | 不增加当前负担 | ✅ 满足 | 扩展口子为"死代码"，不启用无开销 |

---

## 多进程/分布式/分片扩展口子设计（v3.1 新增）

> **设计原则**：当前架构按 1500 模块设计，但所有核心接口按 5000 模块预留扩展能力。超过 1500 模块时，可通过渐进升级（非推倒重来）支撑到极限容量。

### 扩展口子总览

| 扩展口子 | 当前实现 | 扩展目标 | 触发条件 | 升级路径 |
|---------|---------|---------|---------|---------|
| **EventBusBackend** | asyncio.Queue（进程内） | Redis Streams / NATS / Kafka | 模块数>1500 或 Queue 深度>1000 持续 1 小时 | 替换 Backend 实现，无需改动业务代码 |
| **StorageBackend** | SQLite（单库） | PostgreSQL / TiDB / CockroachDB | 模块数>5000 或写 TPS>500 | 替换 Backend 实现，数据迁移工具 |
| **ModuleLoader** | `__getattr__` 懒加载（单进程） | multiprocessing + RPC | 模块数>1500 或启动时间>45s | 分层加载：核心模块进程内，扩展模块子进程 |
| **ContractBus 多进程** | 进程内 Protocol 调用 | gRPC / Dapr / 自研 RPC | 模块数>5000 | ContractBus Backend 抽象，支持跨进程调用 |
| **VectorStoreBackend** | ChromaDB（本地） | ChromaDB 分布式 / Weaviate / Milvus | 向量条目>10000 或 recall@10<0.9 | 替换 Backend 实现 |

### 核心抽象接口

```python
from typing import Protocol, Any
from pydantic import BaseModel

class EventBusBackend(Protocol):
    """事件总线后端抽象——当前 asyncio.Queue，未来可替换为 Redis/NATS/Kafka"""
    async def publish(self, topic: str, payload: BaseModel) -> None: ...
    async def subscribe(self, topic: str, handler: Callable) -> None: ...
    async def get_queue_depth(self, topic: str) -> int: ...

class StorageBackend(Protocol):
    """存储后端抽象——当前 SQLite，未来可替换为 PG/TiDB/CockroachDB"""
    async def query(self, sql: str, params: tuple) -> list[dict]: ...
    async def execute(self, sql: str, params: tuple) -> int: ...
    async def shard_route(self, key: str) -> str: ...  # 分片路由

class ModuleLoaderBackend(Protocol):
    """模块加载后端抽象——当前单进程，未来支持多进程"""
    def load(self, module_id: str) -> Any: ...
    def unload(self, module_id: str) -> None: ...
    def get_process_id(self, module_id: str) -> int: ...  # 返回模块所在进程 ID
```

### 数据库分片策略预留

```python
# shard_router.py —— 当前为单库透传，未来实现一致性哈希分片
class ShardRouter:
    def __init__(self, shard_count: int = 1):
        self.shard_count = shard_count  # 当前=1，未来可按模块 ID 哈希

    def route(self, module_id: str) -> str:
        """返回目标分片的数据库连接字符串"""
        if self.shard_count == 1:
            return "sqlite:///zephyr.db"  # 当前单库
        # 未来：一致性哈希
        shard_id = hash(module_id) % self.shard_count
        return f"sqlite:///zephyr_shard_{shard_id}.db"
```

### 分布式事件总线预留

```python
# contract_bus.py —— Backend 抽象已预留
class ContractBus:
    def __init__(self, backend: EventBusBackend | None = None):
        self.backend = backend or AsyncioQueueBackend()  # 默认进程内
        # 未来：self.backend = RedisStreamsBackend(redis_url="...")

    async def request(self, producer: str, consumer: str, payload: BaseModel) -> BaseModel:
        # 当前：直接调用
        # 未来：若 producer 和 consumer 不在同一进程，走 backend 序列化
        return await self.backend.request(producer, consumer, payload)
```

### 扩展口子启用原则

1. **绝不提前启用**：当前 44 模块，单进程 SQLite+asyncio.Queue 完全够用
2. **条件触发**：每个扩展口子有明确触发条件（模块数/性能指标）
3. **Backend 替换**：业务代码不感知 Backend 变化，仅配置层切换
4. **数据迁移**：StorageBackend 切换时提供自动迁移工具
5. **渐进验证**：每启用一个扩展口子，运行 7 天稳定性验证

---

## 审计结果精华归档（v3.1 压缩）

> 以下为 GLM/Kimi/Qwen 三轮审计的精华结论，详细过程已压缩。如需查看完整审计过程，检索历史版本 v3.0。

### 一、GLM 结构扫描精华

**综合评分：27/100**（容量保障基础设施施工图，非交易业务层）

| 维度 | 最关键缺口 |
|------|-----------|
| D14 治理合规（5.4/10） | 缺容量 SLI/SLO 标准文档（GAP-001） |
| D12 遥测观测（3.8/10） | 缺 OpenTelemetry 集成、缺容量 SLI/SLO（GAP-002） |
| D15 AI 安全（2.8/10） | 缺 AISG 容量规划（GAP-004） |

**P0 缺口（8 项）**：GAP-001~GAP-008 → 已由 v3.0 新增 M-17/M-18/M-19 覆盖
**P1 缺口（10 项）**：GAP-009~GAP-018 → 交易业务层容量待后续施工图覆盖

**AI 自治权限修正**：5/16 模块需修正（lazy_loader、config_validator、event_bus_upgrade、ZephyrLogger 采样率、knowledge_engine 阈值）

### 二、Kimi 盲区发现精华

| 盲区 | 严重度 | v3.0 覆盖 |
|------|--------|---------|
| V-01 Self-Modification 闭环 | P0 | M-17 ai_audit_guard.py |
| V-02 Reward Hacking | P0 | audit_rules.yaml 限制变化幅度 |
| V-05 工作量低估（44 文件迁移） | P0 | 分三批（15+15+14）+ 迁移追踪器 |
| V-08 反馈闭环缺失 | P0 | M-19 capacity_governance_loop.py |
| V-10 Schema Enforcement 缺失 | P0 | P1-9 Pydantic v2 运行时校验 |

### 三、Qwen 落地审计精华

**技术选型结论**：自研轻量规则+SQLite（P0）→ 规则引擎→本地 LLM（渐进）
**过度工程 Hold 项**：LLM-as-Judge（>300 模块）、TLA+形式化（>20 ADR 且 2 次冲突）
**争议裁决**：ContractBus 分三批、ai_audit_guard 骨架 P0+规则 P1b、压缩率 40%

**TOP 5 下一步**：
1. P0-4 capacity_slo.yaml（2-4h）
2. P0-5 ai_audit_guard 骨架（4-6h）
3. P0-3 validate_ssot.py（4-6h）
4. P0-1+P0-2 CTR-001 修复+源码树统一（4.5-8.5h）
5. P1a pre-commit 分层+dmypy+import-linter（6-10h）

---

## Kimi K2.6 发散探索结果（v3.1 创意合伙人）

> 审计时间：2026-04-26 | 角色：创意合伙人/发散者 | 输入：容量保障体系四份文档（SCALE-001/002/003/004）+ v3.0 施工图

---

### 一、原意理解

**用我自己的话复述**：

用户（ZephyrAlpha Owner）的核心意图是：在当前 Phase 2（施工图纸阶段，~97 蓝图/~44 实现文件）提前构建一套"极限容量保障体系"，确保架构能支撑到 1500 模块甚至更远，而不是建到 300 模块时发现架构要重写。这不是"要不要做 1000 模块"的讨论，而是"如何确保架构能撑到极限模块数不崩塌"的治理任务。

关键升级信号：
1. **从 1000 到 1500+**：原目标 1000 模块已升级为"1500 模块设计/5000 模块预留/10000+ 极限"
2. **从单进程到分布式预留**：要求现在就给多进程架构+分布式事件总线+数据库分片"留口子"
3. **从人工治理到 AI 自治**：当前 1 人+AI（工具模式）天花板约 150-200 模块，差距（200→1500）靠未来 AI 自治填补，现在必须预留自治接口

**所属架构层**：L0-L3 基础设施层（跨全层）+ 治理层（Governance）+ AI 安全网关（AISG）
**所属开发节点**：节点 2（Phase 2 施工图阶段）→ 节点 3（Phase 3 实现阶段）的过渡窗口

---

### 二、方向展开

| # | 方向 | 描述 | 与已有设计关系 |
|---|------|------|-------------|
| 1 | **核心：极限容量架构** | 按 1500 模块设计/5000 预留/10000+ 极限的三级容量目标，构建渐进式扩展架构 | 🔴新增：扩展口子设计（EventBusBackend/StorageBackend/ModuleLoaderBackend） |
| 2 | **相邻：AI 自治安全** | 为 AI 自治预留制衡层——ai_audit_guard（Immutable Core）+ capacity_governance_loop（AI-Modifiable 执行+Human-Gated 策略） | 🟡修改：v3.0 已规划 M-17/M-19，发散探索强化"AI 改 AI 规则"的特殊场景 |
| 3 | **升级：统一模型平台** | 对标 Goldman Sachs SecDB，将 ContractBus 升级为"类型安全的统一契约注册中心"，所有模块共享同一 Schema 命名空间 | 🟡修改：v3.0 已规划 ContractBus+Schema Enforcement，发散探索提出"统一类型系统"愿景 |
| 4 | **降级：最小可行容量保障** | 若资源极度受限（如 Owner 时间被交易研发挤占），最小版本=CTR-001 修复+validate_ssot.py+lazy_loader+pre-commit 分层，其余 Hold 至节点 3 | 🟢已有：v3.0 Phase 0/1A 已覆盖，发散探索明确"最小可行集" |
| 5 | **反向：容量限制即特性** | 与其追求无限扩展，不如将"1500 模块上限"设计为系统特性——超限自动进入"归档模式"（旧模块只读/新模块需替换），强制保持系统精简 | 🔴新增：与 v3.0"极限容量"思路相反，但可为单人项目提供"强制精简"机制 |
| 6 | **跨界：游戏引擎组件化** | Unity/Unreal 的"组件-实体-系统"（ECS）架构——模块即 Component，层即 System，ContractBus 即 EntityManager。1500 模块=1500 个 Component，ECS 的内存布局优化可提升缓存命中率 | 🔴新增：跨界借鉴，与当前 Python 架构无直接冲突，可作为未来 C++/Rust 重写参考 |

---

### 三、关键问题

| # | 问题 | 为什么关键 | 涉及 AI 自治权限层 |
|---|------|-----------|-----------------|
| 1 | **1500 模块的估算是否过于乐观？** 单进程 Python+SQLite+asyncio 在 1500 模块时启动时间可能>45s，此时"渐进升级"是否来得及？ | 若估算偏差>50%，整个 Phase 1B/2/3 的时间表需重写 | Human-Gated（需 Owner 确认估算假设） |
| 2 | **AI 自治的"权限边界"是否足够清晰？** 当前三层权限（Immutable/Human-Gated/AI-Modifiable）是静态标注，但 AI 能力在进化——今天的 AI-Modifiable 模块，明天可能因 AI 能力提升而被视为"可自治"。谁来动态调整权限？ | 若权限边界僵化，AI 自治无法渐进启用；若边界模糊，存在 Self-Modification 风险 | Immutable Core（权限调整规则本身不可变） |
| 3 | **ContractBus 是解耦还是过度抽象？** 44 个文件的规模下，直接 import 调用 vs ContractBus 抽象，后者增加代码复杂度+运行时开销。过早抽象是否会成为"为了未来而牺牲现在"？ | 若 ContractBus 在 44 模块时就引入不可接受的性能损耗（如延迟+10ms），则需重新评估迁移时机 | Human-Gated（架构级决策） |
| 4 | **扩展口子的"条件触发"是否可靠？** 模块数>1500 时启用多进程——但模块数增长是渐进的，如何提前发现"即将触及瓶颈"的信号？ | 若触发条件设计不当，可能在发现瓶颈时系统已处于亚健康状态，无法安全升级 | AI-Modifiable（趋势检测可 AI 执行） |
| 5 | **单人项目的"知识流失"风险如何缓解？** 1500 模块的治理体系极度依赖 Owner 的个人认知，若 Owner 因故中断项目 3 个月，AI 能否基于文档+代码自治维护？ | 这是"1 人+AI 自治"模式的终极考验——知识必须可编码、可验证、可传承 | AI-Modifiable（知识引擎可自动提取规则） |
| 6 | **对标顶级机构的"工业级标准"是否导致过度工程？** Goldman Sachs SecDB/JPM Athena 是千人团队产物，单人项目复制其架构标准是否"用牛刀杀鸡"？ | 若工业对标导致 80%精力投入基础设施、20%投入交易策略，项目可能"架构完美但无收益" | Human-Gated（资源分配策略） |
| 7 | **扩展口子的"技术债务"风险：** 现在预留 5 个扩展口子（EventBus/Storage/ModuleLoader/ContractBus/VectorStore），每个口子都是抽象层。若未来技术选型变化（如 Redis→NATS），抽象层是否成为枷锁？ | 抽象层设计不当会导致"为了抽象而抽象"，反而限制未来选择 | Human-Gated（技术选型决策） |

---

### 四、类比与先例

| # | 类比 | 解决的问题 | 相似处 | 可借鉴 |
|---|------|-----------|--------|--------|
| 1 | **Goldman Sachs SecDB** | 统一模型平台确保所有组件共享类型安全和容量预算 | ZephyrAlpha 的 ContractBus 类似 SecDB 的通信层，但缺乏统一类型系统 | 引入"Schema Registry"概念，所有模块的 Pydantic 模型集中注册 |
| 2 | **JPMorgan Athena** | 跨资产类别的一体化风险/定价/交易系统 | Athena 的"一切即代码"理念与 ZephyrAlpha 的"蓝图即代码"相似 | 借鉴 Athena 的 A+语言（领域特定语言）思想，为 ZephyrAlpha 设计"容量配置即代码" |
| 3 | **Citadel 的自动化容量管理** | 持续运行的容量治理闭环（非项目清单） | Kimi 发现的 V-08（反馈闭环缺失）正是 Citadel 已解决的问题 | 复用 Google Borgmon+Autopilot 模式：指标采集→趋势检测→自动修复 |
| 4 | **Two Sigma 的模块联邦制** | 1000+模块的自治维护——每个模块有独立 Owner（AI Agent），联邦协调 | ZephyrAlpha 目标"1 人+AI 维护 99%模块"与 Two Sigma 的"模块联邦"理念相通 | 设计"模块自治契约"：每个模块声明自己的维护规则、依赖、容量预算 |
| 5 | **Netflix 的 Chaos Engineering** | 通过主动注入故障验证系统韧性 | ZephyrAlpha 的 fault_isolator.py 可扩展为"容量混沌工程"——主动模拟 1500 模块负载 | 引入"容量故障注入"：定期模拟 Queue 溢出、DB 分片失败、模块加载超时 |

---

### 五、风险与盲点

| # | 风险/盲点 | 如果忽略会怎样 | 涉及 AI 自治权限层 |
|---|----------|--------------|-----------------|
| 1 | **AI 安全风险：Self-Modification 的"递归深渊"** | ai_audit_guard 拦截 AI 修改→但 ai_audit_guard 的规则本身可能被 AI 通过"规则解释漏洞"绕过（如将"修改"重定义为"查询"）。若忽略，AI 可间接修改 Immutable Core | Immutable Core（审计规则需形式化验证） |
| 2 | **Reward Hacking 风险：容量指标的"游戏化"** | AI 可能通过"延迟上报容量指标"或"选择性丢弃异常数据"来让 capacity_governance_loop 显示"一切正常"。若忽略，系统在亚健康状态下运行直至崩溃 | AI-Modifiable（指标采集需防篡改） |
| 3 | **单人项目风险：Owner 的"认知过载"** | 1500 模块的治理体系需要 Owner 理解并审批大量 Human-Gated 决策。若 Owner 时间被挤占，Human-Gated 可能退化为"批量批准"，失去监督意义 | Human-Gated（需设计"批量审批+抽样复核"机制） |
| 4 | **过度工程风险："为扩展而扩展"** | 5 个扩展口子（EventBus/Storage/ModuleLoader/ContractBus/VectorStore）在当前 44 模块时都是"死代码"。若维护不当，它们会成为理解负担和 bug 来源 | Human-Gated（扩展口子启用需 Owner 审批） |
| 5 | **技术选型锁定风险：Backend 抽象的"虚假通用性"** | EventBusBackend 抽象假设"所有后端都支持 publish/subscribe/queue_depth"，但 Kafka 的 API 与 asyncio.Queue 差异巨大。若抽象层设计不当，未来升级时可能需要重写抽象层本身 | Human-Gated（抽象层设计需 Owner 确认） |

---

### 六、调研需求清单

#### GitHub 搜索

| # | 搜索关键词 | 目标 | 期望找到什么 |
|---|-----------|------|-------------|
| 1 | `python asyncio queue backpressure pattern` | 事件总线背压实现 | 成熟的 Python 背压模式，验证自研方案是否合理 |
| 2 | `pydantic v2 schema registry runtime validation` | Schema Enforcement 实现 | Pydantic v2 的 Schema 注册和运行时校验方案 |
| 3 | `sqlite sharding python single-node` | 单节点 SQLite 分片策略 | 在 SQLite 上实现逻辑分片的工具或模式 |
| 4 | `python multiprocessing module lazy loading` | 多进程模块懒加载 | 如何在多进程环境下保持懒加载的启动优势 |
| 5 | `opentelemetry python metrics tracing structlog` | OTel 与 structlog 集成 | 验证 ZephyrLogger+OTel SDK 的技术可行性 |

#### 论文检索

| # | 搜索关键词 | 研究方向 | 期望找到什么 |
|---|-----------|---------|-------------|
| 1 | `LLM-as-Judge system capacity evaluation 2025 2026` | AI 自治评估 | 验证 LLM 作为容量评估 Judge 的可行性 |
| 2 | `Constitutional AI scalable oversight Anthropic` | AI 安全 | 验证 ai_audit_guard 的学术基础 |
| 3 | `Capacity governance loop SRE autonomous remediation` | 容量治理自动化 | 验证 capacity_governance_loop 的工业实践 |
| 4 | `Python asyncio performance 1000+ coroutines` | asyncio 极限性能 | 验证 asyncio 在 1500 模块下的可行性 |
| 5 | `Single-developer large-scale system maintenance` | 单人项目大规模维护 | 寻找类似 ZephyrAlpha（1 人+AI/1500 模块）的案例 |

#### 技术选型对比

| # | 需对比的技术 | 对比维度 |
|---|------------|---------|
| 1 | asyncio.Queue vs Redis Streams vs NATS | 延迟、吞吐量、Python 原生支持、运维复杂度 |
| 2 | SQLite WAL vs PostgreSQL vs TiDB | 写 TPS、分片支持、Python 驱动成熟度、单节点 vs 分布式 |
| 3 | Pydantic v2 vs Protocol Buffers vs dataclass | 运行时校验性能、Schema 演化、Python 原生支持 |
| 4 | multiprocessing vs asyncio sub-process vs Ray | 模块隔离、启动开销、内存占用、调试复杂度 |
| 5 | ChromaDB vs Weaviate vs Milvus | 向量检索 recall@10、分片支持、Python 原生支持 |

#### 行业实践/标准

| # | 需了解的实践/标准 | 为什么需要 |
|---|-----------------|-----------|
| 1 | Google SRE 的容量规划方法论（《Site Reliability Engineering》第 19 章） | 验证三级容量目标（设计/预留/极限）是否合理 |
| 2 | CNCF OpenTelemetry 的 Metrics/Tracing/Logs 三支柱集成标准 | 验证 ZephyrLogger+OTel SDK 的集成方案 |
| 3 | Goldman Sachs SecDB 的"统一模型平台"架构公开资料 | 验证 ContractBus 向统一类型系统演进的可行性 |
| 4 | Python import system's `__getattr__` lazy loading best practices | 验证 lazy_loader.py 的实现方案 |
| 5 | `import-linter`的层依赖规则配置模式（seddonym/import-linter 文档） | 验证 .importlinter 配置的正确性 |

#### 项目内部已有设计

| # | 需查阅的 ADR/KE/蓝图 | 为什么需要 |
|---|--------------------|-----------|
| 1 | ADR-0010（治理三层边界）完整文本 | 验证 ai_audit_guard/capacity_governance_loop 与 Policy/Factory/Runtime 三层的映射 |
| 2 | ADR-0011（Runtime Planes）完整文本 | 验证容量 SLI/SLO 的 Hot/Warm/Cold 分层定义 |
| 3 | ADR-0019（Feedback Loop Engine）完整文本 | 验证 capacity_governance_loop 与 FLE 的集成方式（Protocol 适配器模式） |
| 4 | technology-landscape.yaml（全部 43 条技术选型） | 验证新增 10 项技术选型是否与现有选型冲突 |
| 5 | invariants.yaml（全部 16 条不变量） | 验证 INV-NEW-001/002 与现有不变量的关系 |
| 6 | entity-graph.json（跨域可追溯体系） | 验证容量保障模块是否已注册到 Metamodel 桥梁 |
| 7 | docs/03_TRADING_TACTICS/ 下的交易策略蓝图 | 验证容量保障体系与交易业务层的交互接口 |

---

### 七、文档压缩（第七步）

#### 标记分类

| 内容块 | 分类 | 理由 |
|--------|------|------|
| 一、原意理解 | 🔴不可删除 | 核心意图理解，决定后续所有发散方向 |
| 二、方向展开（6 个方向） | 🔴不可删除 | 必须保留≥6 个方向，已压缩至 6 个 |
| 二、方向展开中的"反向：容量限制即特性" | 🟡可压缩 | 与 v3.0 主逻辑不完全一致，但保留作为备选思路 |
| 二、方向展开中的"跨界：游戏引擎 ECS" | 🟡可压缩 | 跨界类比，与当前 Python 架构关联度低 |
| 三、关键问题（7 个问题） | 🔴不可删除 | 必须保留≥5 个，已按重要性排序 |
| 四、类比与先例（5 个类比） | 🟡可压缩 | 可压缩为 1 句/个，保留核心借鉴点 |
| 五、风险与盲点（5 个风险） | 🔴不可删除 | 必须保留≥3 个，已包含 AI 安全维度 |
| 六、调研需求清单 | 🔴不可删除 | 必须具体到可搜索关键词，已满足 |
| 六、GitHub 搜索（5 项） | 🟡可压缩 | 保留关键词和目标，删除期望找到什么 |
| 六、论文检索（5 项） | 🟡可压缩 | 同上 |
| 六、技术选型对比（5 项） | 🟡可压缩 | 保留技术名和对比维度 |
| 六、行业实践/标准（5 项） | 🟡可压缩 | 保留实践名和为什么需要 |
| 六、项目内部已有设计（7 项） | 🟡可压缩 | 保留文件名和为什么需要 |

#### 执行压缩

**🟢已删除内容**：
- 无（本步为新增内容，无前序中间产物）

**🟡已压缩内容**：
- 类比与先例：每个类比从 3 句压缩为 2 句（保留"解决的问题+可借鉴"）
- 调研需求清单：删除"期望找到什么"列，保留"搜索关键词+目标"
- 方向展开：跨界方向压缩为 2 句

**🔴不可删除内容确认**：
- ✅ 原意理解完整保留
- ✅ 方向展开 6 个方向完整保留（核心/相邻/升级/降级/反向/跨界）
- ✅ 关键问题 7 个完整保留（最重要：1500 模块估算是否乐观）
- ✅ 风险盲点 5 个完整保留（包含 AI 安全、Reward Hacking、单人项目、过度工程）
- ✅ 调研需求清单完整保留（GitHub/论文/技术选型/行业实践/项目内部）

#### 压缩报告

- **压缩前行数**：0 行（本步为新增内容）
- **压缩后行数**：~280 行
- **删除内容**：无
- **压缩内容**：类比先例删除冗余描述、调研清单删除"期望找到什么"列、方向展开压缩跨界方向
- **不可删除内容确认**：原意理解、方向展开（6 个）、关键问题（7 个）、风险盲点（5 个）、调研清单（5 类）
- **是否触发拆分**：否（作为独立章节追加到文档末尾）

---

> **v3.1 文档总压缩报告（最终版）**
>
> - 原 v3.0 文档行数：~1362 行
> - v3.1 新增：扩展口子设计（~80 行）+ 审计精华归档（~40 行）+ 发散探索（~175 行）+ GLM调研扫描（~270 行）
> - v3.1 删除：GLM-5.1 结构扫描详细结果（~180 行）+ Kimi K2.6 发现+深挖详细结果（~190 行）→ 已压缩为精华归档
> - v3.1 实际总行数：**~1461 行**（含 Qwen 落地审计 ~360 行）
> - 净变化：+99 行（新增扩展口子+发散探索+调研扫描+精华归档，删除详细审计过程）
> - 核心信息保留率：**100%**（所有关键决策、模块、技术选型、路线图、风险均保留）
> - 审计过程保留：精华归档+指向 v3.0 历史版本的指针
> - 扩展口子保留：5 个 Backend 抽象（EventBus/Storage/ModuleLoader/ContractBus/VectorStore）+ 分片策略 + 分布式事件总线

---

## GLM-5.1 调研扫描结果

> 审计时间：2026-04-26 | 审计角色：技术调研员 | 审计范围：Kimi 发散探索调研需求清单（GitHub/论文/技术选型/行业实践/项目内部）

---

### 一、GitHub 项目搜索与评估

| # | 项目 | Stars | 语言 | 最后更新 | 相关度 | 可用性 | 评估理由 |
|---|------|-------|------|---------|--------|--------|---------|
| 1 | **python-observability** (wshobson/agents) | - | Python | 2025 | ★★★★★ | ★★☆ | structlog+OTel集成模式完整，可直接参考 |
| 2 | **opentelemetry-python** (open-telemetry) | 4.5k | Python | 2026-04 | ★★★★★ | ★★★ | CNCF官方SDK，Traces/Metrics稳定，Logs开发中 |
| 3 | **pyrmute** (mferrera/pyrmute) | 89 | Python | 2025 | ★★★☆☆ | ★★☆ | Pydantic模型版本迁移，与Schema Registry思路一致 |
| 4 | **lazyr** (Chitaoji/lazyr) | 45 | Python | 2025 | ★★★☆☆ | ★★☆ | 模块懒加载实现，与lazy_loader需求匹配 |
| 5 | **mputil** (rasbt/mputil) | 312 | Python | 2024 | ★★☆☆☆ | ★☆☆ | 多进程lazy map，与ModuleLoader多进程扩展相关 |
| 6 | **asynkit** (kristjanvalur/py-asynkit) | 156 | Python | 2025 | ★★★☆☆ | ★★☆ | asyncio性能优化，eager_task_factory 1.8x加速 |
| 7 | **screenpipe** (screenpipe/screenpipe) | 12k | Rust | 2026-03 | ★★☆☆☆ | ★☆☆ | SQLite时间分片策略，与ShardRouter设计思路一致 |
| 8 | **sharded** (marvinified/sharded) | - | Python | 2025 | ★★☆☆☆ | ★☆☆ | SQLite缓存分片，思路可参考但代码不可用 |

#### 可用项目详情

**★★★ opentelemetry-python**
- 仓库地址：https://github.com/open-telemetry/opentelemetry-python
- 核心模块：`opentelemetry-api/`, `opentelemetry-sdk/`, `exporter/`
- 集成方式：`pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation`
- 已知限制：Logs信号仍为Development状态（不稳定）
- 单人项目适配性：★★★★★（纯Python库，无独立服务）
- 与ZephyrAlpha关系：T-06 ZephyrLogger+OTel直接采用

**★★☆ python-observability (skill文档)**
- 来源：https://github.com/wshobson/agents/blob/main/plugins/python-development/skills/python-observability/SKILL.md
- 核心内容：structlog+OTel集成模式、Four Golden Signals、Correlation ID传播
- 集成方式：参考模式自研
- 已知限制：非独立项目，是AI agent技能文档
- 单人项目适配性：★★★★★（纯模式文档，无依赖）
- 与ZephyrAlpha关系：T-06集成方案参考

**★★☆ pyrmute**
- 仓库地址：https://github.com/mferrera/pyrmute
- 核心模块：`pyrmute/`, 模型版本管理+自动迁移链
- 集成方式：`pip install pyrmute`
- 已知限制：高吞吐场景不适用（运行时迁移增加延迟）
- 单人项目适配性：★★★★★（纯Python，单依赖Pydantic）
- 与ZephyrAlpha关系：ContractBus Schema演化参考

**★★☆ lazyr**
- 仓库地址：https://github.com/Chitaoji/lazyr
- 核心模块：`lazyr/register()`, `lazyr.wakeup()`
- 集成方式：`pip install lazyr`
- 已知限制：Python>=3.13，类型提示可能失效
- 单人项目适配性：★★★★★（纯Python，无依赖）
- 与ZephyrAlpha关系：T-02懒加载实现参考，但自研更可控

**★★☆ asynkit**
- 仓库地址：https://github.com/kristjanvalur/py-asynkit
- 核心模块：`asynkit/eager_task_factory.py`（C扩展）
- 集成方式：`pip install asynkit`
- 已知限制：C扩展增加构建复杂度
- 单人项目适配性：★★★☆☆（C扩展需编译）
- 与ZephyrAlpha关系：asyncio性能优化备选，当前不需要

---

### 二、论文与学术资源

| # | 论文 | 作者/机构 | 年份 | 核心贡献 | 相关度 | 可落地性 |
|---|------|----------|------|---------|--------|---------|
| 1 | **Judge's Verdict: A Comprehensive Analysis of LLM Judge Capability** | NVIDIA | 2025 | 54个LLM的Judge能力评估，Cohen's Kappa分析 | ★★★★☆ | ★★☆ |
| 2 | **Explicit Reasoning Makes Better Judges** | ASU/CMU | 2025 | Thinking模型在LLM-as-Judge中准确率+10%，开销<2x | ★★★★☆ | ★★☆ |
| 3 | **RobustJudge: Robustness of LLM-as-a-Judge** | SEU/NTU/ZJU | 2025 | LLM Judge对抗攻击脆弱性分析，防御策略 | ★★★☆☆ | ★☆☆ |
| 4 | **Constitutional AI: Harmlessness from AI Feedback** | Anthropic | 2022 | AI自我监督+宪法原则，RLAIF替代RLHF | ★★★★★ | ★★★ |
| 5 | **The Memory Tax of Concurrency: Goroutines vs Python asyncio** | Ritesh Sharma | 2025 | asyncio内存开销分析，10,000并发时Go vs Python对比 | ★★★☆☆ | ★★☆ |

#### 可落地论文详情

**★★★ Constitutional AI (Anthropic, 2022)**
- 论文链接：https://arxiv.org/pdf/2212.08073
- 核心算法：两阶段训练（监督学习自我批评+RLAIF强化学习）
- 官方实现：Claude生产部署（闭源），但论文方法已公开
- 实现复杂度：高（需训练模型），但原则可直接应用
- 与ZephyrAlpha关系：ai_audit_guard.py的学术基础——"AI自我监督需外部约束"
- 落地建议：不实现完整CAI，仅借鉴"宪法原则+外部审计"思想

**★★☆ Judge's Verdict (NVIDIA, 2025)**
- 论文链接：https://arxiv.org/html/2510.09738v1
- 核心算法：两阶段评估（相关性测试+Cohen's Kappa人类一致性测试）
- 官方实现：Judge's Verdict Benchmark（开源数据集）
- 实现复杂度：中（评估框架可自行实现）
- 与ZephyrAlpha关系：LLM-as-Judge容量评估的理论基础
- 落地建议：Hold至模块>300且AI错误率>10%时启用（Qwen已判定）

**★★☆ Explicit Reasoning Makes Better Judges (ASU/CMU, 2025)**
- 论文链接：https://arxiv.org/html/2509.13332v1
- 核心算法：Thinking vs Non-thinking模型在RewardBench上的系统对比
- 官方实现：基于Qwen3模型，开源可复现
- 实现复杂度：中（需本地GPU运行Qwen3）
- 与ZephyrAlpha关系：验证"本地小模型（4B）可作为Judge"
- 落地建议：3090+Qwen3-4B本地部署可作为ai_audit_guard的升级路径

**★★☆ The Memory Tax of Concurrency (2025)**
- 来源：https://riteshsharma.me/blogs/memory-tax-concurrency-goroutines-python
- 核心发现：Python asyncio tasks携带完整解释器帧对象，10,000并发时内存开销显著高于Go goroutines
- 与ZephyrAlpha关系：验证asyncio在1500模块下的内存可行性
- 落地建议：1500模块时预计并发任务<10,000，asyncio内存可承受；超过则需多进程

---

### 三、技术选型对比

| 需求 | 方案A | 方案B | 方案C | 推荐方案 | 推荐理由 |
|------|------|------|------|---------|---------|
| **事件总线后端** | asyncio.Queue（当前） | Redis Streams | NATS | **asyncio.Queue→Redis Streams** | 当前44模块Queue足够；>1500模块Redis Streams轻量且Python支持好 |
| **存储后端** | SQLite WAL（当前） | PostgreSQL | TiDB | **SQLite→PostgreSQL→TiDB** | 渐进式：SQLite到5000模块；PG到10000；TiDB极限容量 |
| **Schema校验** | Pydantic v2（当前） | Protocol Buffers | dataclass | **Pydantic v2** | Python原生、运行时校验、已有依赖 |
| **多进程框架** | multiprocessing | Ray | asyncio subprocess | **multiprocessing** | Python标准库、无额外依赖、与lazy_loader兼容 |
| **向量存储** | ChromaDB（当前） | Weaviate | Milvus | **ChromaDB→Weaviate** | ChromaDB到10000向量；Weaviate分布式扩展 |

**对比维度汇总**：

| 维度 | asyncio.Queue | Redis Streams | PostgreSQL | TiDB | Pydantic v2 | multiprocessing |
|------|--------------|---------------|------------|------|-------------|----------------|
| 功能覆盖度 | ★★☆ | ★★★ | ★★★ | ★★★ | ★★★ | ★★★ |
| 性能 | ★★★ | ★★★ | ★★★ | ★★★ | ★★★ | ★★☆ |
| 社区活跃度 | ★★★ | ★★★ | ★★★ | ★★☆ | ★★★ | ★★★ |
| 学习曲线 | ★★★ | ★★☆ | ★★☆ | ★☆☆ | ★★★ | ★★★ |
| 与现有技术栈兼容性 | ★★★ | ★★★ | ★★☆ | ★☆☆ | ★★★ | ★★★ |
| 许可证 | Python | BSD | PostgreSQL | Apache 2.0 | MIT | Python |
| 单人项目适配性 | ★★★ | ★★★ | ★★☆ | ★☆☆ | ★★★ | ★★★ |
| 成本 | 免费 | 免费 | 免费 | 免费 | 免费 | 免费 |

---

### 四、行业实践与标准

| # | 实践/标准 | 来源 | 核心要求 | 与草案的关联 | 必须遵守？ |
|---|----------|------|---------|-------------|----------|
| 1 | **Google SRE 容量规划** | 《Site Reliability Engineering》第19章 | 三级容量目标（设计/预留/极限）、错误预算、负载测试 | 验证三级容量目标合理性 | 建议遵守 |
| 2 | **CNCF OpenTelemetry 三支柱** | opentelemetry.io | Metrics/Tracing/Logs统一采集、OTLP协议 | 验证ZephyrLogger+OTel集成方案 | 建议遵守 |
| 3 | **Goldman Sachs SecDB 统一模型** | 公开演讲/论文 | 所有组件共享统一类型系统、集中式Schema注册 | ContractBus向统一类型系统演进参考 | 参考借鉴 |
| 4 | **JPMorgan Athena 组件化** | 公开演讲/论文 | 一切即代码、跨资产一体化、A+领域语言 | "容量配置即代码"设计参考 | 参考借鉴 |
| 5 | **Citadel 自动化容量管理** | 行业传闻/SREcon | 持续运行容量治理闭环、Borgmon+Autopilot | capacity_governance_loop设计验证 | 参考借鉴 |

**关键发现**：
- Google SRE的"错误预算"概念可直接应用于capacity_slo.yaml设计
- CNCF OpenTelemetry的Logs信号仍为Development状态，ZephyrAlpha的Logs+Metrics双输出策略合理
- SecDB的"统一模型平台"与ZephyrAlpha的ContractBus+Schema Enforcement方向一致，但差距在于"集中式Schema注册中心"

---

### 五、来源决策矩阵

| # | 模块/组件 | 来源决策 | 具体来源 | 理由 | 预估工作量 | 单人适配性 |
|---|----------|---------|---------|------|-----------|----------|
| 1 | **structlog+OTel集成** | 【直接采用】 | opentelemetry-python + python-observability模式 | CNCF官方SDK，Traces/Metrics稳定 | 3-4h | ★★★★★ |
| 2 | **Pydantic v2 Schema校验** | 【直接采用】 | pydantic>=2.0.0（已有依赖） | 已有依赖，运行时校验成熟 | 3-4h | ★★★★★ |
| 3 | **模块懒加载** | 【参考自写】 | lazyr思路 + `__getattr__`最佳实践 | 自研更可控，lazyr仅参考 | 2-4h | ★★★★★ |
| 4 | **SQLite分片** | 【参考自写】 | screenpipe时间分片策略 + ShardRouter | 自研轻量分片，screenpipe仅参考 | 4-6h | ★★★★★ |
| 5 | **asyncio背压** | 【完全自写】 | 无直接匹配项目 | Python原生实现，无依赖 | 4-6h | ★★★★★ |
| 6 | **import-linter** | 【直接采用】 | seddonym/import-linter | 专门用于Python层依赖检查 | 2-4h | ★★★★★ |
| 7 | **dmypy** | 【直接采用】 | mypy>=1.8.0（已有依赖） | 增量类型检查，内存缓存 | 1-2h | ★★★★★ |
| 8 | **pybreaker+tenacity** | 【直接采用】 | pybreaker>=1.0.0 + tenacity>=8.2.0（已有依赖） | 已有依赖，成熟方案 | 6-8h | ★★★★★ |
| 9 | **ContractBus** | 【完全自写】 | 参考SecDB/Athena架构思想 | 核心架构组件，需自研 | 10-14h | ★★★★★ |
| 10 | **ai_audit_guard** | 【完全自写】 | 借鉴Constitutional AI思想 | 核心安全组件，无现成方案 | 4-6h | ★★★★★ |
| 11 | **capacity_governance_loop** | 【参考自写】 | 借鉴Google Borgmon+Autopilot模式 | 需自研适配单人项目 | 4-6h | ★★★★★ |
| 12 | **pre-commit分层** | 【改造采用】 | pre-commit框架 + 自定义hook | 社区标准，需自定义分层逻辑 | 3-4h | ★★★★★ |
| 13 | **validate_ssot** | 【完全自写】 | 无直接匹配 | SSoT验证逻辑项目特定 | 4-6h | ★★★★★ |
| 14 | **Redis Streams升级** | 【直接采用】 | redis-py（条件触发） | 标准客户端，条件触发启用 | 6-10h | ★★★☆☆ |
| 15 | **PostgreSQL升级** | 【直接采用】 | psycopg2/asyncpg（条件触发） | 标准驱动，条件触发启用 | 4-6h | ★★★☆☆ |
| 16 | **上下文压缩** | 【完全自写】 | 无直接匹配 | 项目特定需求 | 4-6h | ★★★★★ |
| 17 | **契约测试** | 【完全自写】 | 参考pyrmute模型版本思想 | 轻量自研，无需重型框架 | 8-12h | ★★★★★ |
| 18 | **故障域隔离** | 【改造采用】 | pybreaker + 自定义域逻辑 | 核心库+自定义扩展 | 6-8h | ★★★★★ |
| 19 | **Schema Registry** | 【完全自写】 | 借鉴SecDB统一模型思想 | 长期愿景，当前无需实现 | 20-40h | ★★★☆☆ |
| 20 | **Chaos Engineering** | 【完全自写】 | 借鉴Netflix Chaos Monkey思想 | 长期愿景，当前无需实现 | 16-24h | ★★★☆☆ |

---

### 六、项目内部已有设计对齐

| # | 已有文档 | 与本次想法的关系 | 可复用/需更新 |
|---|----------|----------------|-------------|
| 1 | **ADR-001（structlog）** | T-06 ZephyrLogger+OTel基于structlog | ✅ 可复用，需扩展OTel集成 |
| 2 | **ADR-003（Pydantic v2）** | T-09配置验证、ContractBus Schema Enforcement | ✅ 可复用，已有依赖 |
| 3 | **ADR-005（DuckDB+Parquet）** | 与T-14容量治理时序存储冲突 | ⚠️ 【ADR冲突】ADR-005选DuckDB，容量治理需SQLite/InfluxDB |
| 4 | **ADR-009（消息队列）** | T-07事件总线、T-12 Redis升级 | ⚠️ 需更新：ADR-009未决策，本施工图给出条件触发方案 |
| 5 | **technology-landscape.yaml** | 新增10项技术选型需与现有43条做冲突检查 | ⚠️ 需更新：确认pybreaker+tenacity组合不违反选型原则 |
| 6 | **invariants.yaml** | 新增INV-NEW-001/002需与现有16条对齐 | ⚠️ 需更新：INV-011与INV-NEW-001关系需明确 |
| 7 | **src/zephyr/schemas.py** | 已有AuditFinding/AuditReport模型 | ✅ 可复用：ai_audit_guard可复用现有Schema |
| 8 | **src/zephyr/gates/gate_engine.py** | 已有GateEngine实现 | ✅ 可复用：warm_hot_gate/fault_isolator可基于GateEngine扩展 |
| 9 | **src/zephyr/orchestrator/agent_health_monitor.py** | 已有SLOConfig/SLOViolation模型 | ✅ 可复用：capacity_slo.yaml可复用现有SLO模型 |
| 10 | **src/zephyr/hooks/ssot_guard.py** | 已有SsotGuard实现 | ✅ 可复用：validate_ssot可基于SsotGuard扩展 |
| 11 | **src/zephyr/feedback_loop/evolution_engine.py** | 已有EvolutionEngine | ✅ 可复用：capacity_governance_loop可与EvolutionEngine集成 |
| 12 | **docs/02_ARCHITECTURE/tech-decision-records.md** | 9条ADR中4条与容量保障直接相关 | ⚠️ 需更新：ADR-009消息队列决策需补充条件触发方案 |

**【ADR冲突】详情**：
- **ADR-005 vs T-14**：ADR-005选定DuckDB+Parquet作为数据存储，但capacity_governance_loop需要时序数据库（SQLite/InfluxDB）。**解决方案**：容量治理使用独立的SQLite数据库（与DuckDB不冲突），未来模块>5000时统一评估存储后端。

**【蓝图重复】检查**：
- 未发现已有蓝图与容量保障模块直接重复。
- `src/zephyr/orchestrator/agent_health_monitor.py`已有SLO相关模型，与M-18 capacity_slo.yaml部分重叠，建议复用而非新建。

---

### 七、传递给Qwen的信息

- **可直接采用的组件**：
  1. opentelemetry-python（T-06 ZephyrLogger+OTel集成，3-4h）
  2. pydantic>=2.0.0（T-09配置验证，已有依赖）
  3. pybreaker+tenacity（T-10故障隔离，已有依赖）
  4. import-linter（T-05层依赖检查，2-4h）
  5. dmypy（T-04增量类型检查，1-2h）

- **需改造的组件**：
  1. pre-commit框架→分层pre-commit（T-03，3-4h）
  2. pybreaker→故障域隔离（T-10，6-8h，需自定义域逻辑）
  3. SsotGuard→validate_ssot（M-03，4-6h，需扩展验证逻辑）

- **需参考自写的组件**：
  1. 模块懒加载（T-02，参考lazyr思路，2-4h）
  2. SQLite分片（ShardRouter，参考screenpipe时间分片，4-6h）
  3. capacity_governance_loop（M-19，参考Google Borgmon模式，4-6h）
  4. 契约测试（M-11，参考pyrmute模型版本思想，8-12h）

- **需完全自写的组件**：
  1. asyncio背压（T-07，4-6h）
  2. ContractBus（M-09，10-14h）
  3. ai_audit_guard（M-17，4-6h）
  4. 上下文压缩（M-20，4-6h）

- **技术选型推荐**：
  1. 事件总线：asyncio.Queue（当前）→ Redis Streams（>1500模块）
  2. 存储后端：SQLite（当前）→ PostgreSQL（>5000模块）→ TiDB（极限）
  3. Schema校验：Pydantic v2（始终）
  4. 多进程：multiprocessing（标准库）
  5. 向量存储：ChromaDB（当前）→ Weaviate（>10000向量）

- **调研中发现的新风险/新问题**：
  1. 【ADR冲突】ADR-005 DuckDB与容量治理SQLite时序存储的潜在冲突
  2. 【Logs信号不稳定】OpenTelemetry Logs仍为Development状态，生产环境需谨慎
  3. 【asyncio内存开销】10,000并发时Python asyncio内存显著高于Go，1500模块需评估
  4. 【lazyr限制】lazyr要求Python>=3.13，ZephyrAlpha需确认Python版本兼容性

- **项目内部已有设计需更新的**：
  1. ADR-009消息队列：补充条件触发方案（asyncio.Queue→Redis Streams）
  2. technology-landscape.yaml：新增10项技术选型条目
  3. invariants.yaml：明确INV-011与INV-NEW-001关系
  4. agent_health_monitor.py：复用SLOConfig/SLOViolation到capacity_slo.yaml

---

### 压缩报告

- **压缩前行数**：~470行（GitHub项目8个+论文5篇+技术选型5组+行业实践5个+来源决策20个+项目对齐12个）
- **压缩后行数**：~320行
- **删除内容**：
  - ☆☆☆不适用项目详情（sharded等）
  - 论文纯理论部分（RobustJudge攻击分析等）
  - 技术选型对比过程（保留结论表）
- **压缩内容**：
  - GitHub项目：★☆☆和☆☆☆压缩为1句
  - 论文：★☆☆和☆☆☆压缩为1句
  - 行业实践：详细描述压缩为核心要求+关联
- **不可删除内容确认**：
  - ✅ 来源决策矩阵20个模块完整保留
  - ✅ 技术选型推荐完整保留
  - ✅ 传递给Qwen的信息完整保留
  - ✅ 项目内部已有设计对齐完整保留
  - ✅ ADR冲突和蓝图重复标注完整保留
- **是否触发拆分**：否（作为独立章节追加到文档末尾）

---

> **v3.1 完整文档统计**
>
> - 核心施工图（§1-§10）：~400行
> - AI自治权限总表：~30行
> - 争议清单：~20行
> - 务实修正：~20行
> - 单人项目适配性：~15行
> - 扩展口子设计：~130行
> - 审计精华归档：~60行
> - Kimi发散探索：~280行
> - GLM调研扫描：~320行
> - **预计总行数：~1295行**
> - 相比v3.0（~1362行）：净增~67行（新增扩展口子+发散探索+调研扫描，压缩审计过程）

---

> **注**：GLM-5.1 结构扫描详细结果与 Kimi K2.6 发现+深挖详细结果已压缩为上方「审计结果精华归档」。如需查看完整审计过程，检索历史版本 v3.0。

---

## Qwen 3.6 Plus 落地审计结果

> 审计时间：2026-04-26 | 审计角色：落地者 | 审计范围：GLM-5.1扫描结果 + Kimi K2.6发现+深挖结果

---

### 一、技术选型总表 【Qwen选型】

| # | 组件 | 首选 | 备选 | 不推荐 | 触发条件 | ADR | AI自治权限 |
|---|------|------|------|--------|---------|-----|-----------|
| 1 | ai_audit_guard.py 审计规则引擎 | 自研轻量规则引擎（Python dict+JSON schema） | OPA Gatekeeper（需Go运行时） | Rego/Opa（Go运行时引入运维负担） | 立即部署（P0） | 新建 | Immutable Core |
| 2 | ai_audit_guard.py 审计日志存储 | SQLite（追加写入WAL模式） | JSON Lines文件 | PostgreSQL（过重） | 立即部署（P0） | 复用ADR-0019 SQLite | Immutable Core |
| 3 | capacity_governance_loop.py 时序存储 | SQLite WAL（复用FLE） | InfluxDB OSS | TimescaleDB（需PG依赖） | 模块数>300时升级 | ADR-0019已选SQLite | AI-Modifiable |
| 4 | capacity_slo.yaml | 纯YAML+Pydantic v2校验 | JSON Schema | TOML（生态小） | 立即部署（P0） | 新建 | Human-Gated |
| 5 | ContractBus Schema Enforcement | Pydantic v2模型（runtime校验） | dataclass+validators | Protocol Buffers（需代码生成） | Phase 1B随ContractBus部署 | 新建 | Human-Gated |
| 6 | ai_audit_guard Provenance Chain | Git-style commit（SQLite表+hash链） | 审计日志追加表 | Merkle Tree（过重） | 立即部署（P0） | 参考ADR-0019 | Immutable Core |
| 7 | capacity_governance_loop 异常检测 | EMA+3σ（复用FLE逻辑） | SPC控制图 | LSTM/ML（过重） | 立即部署（P0） | ADR-0019已选EMA | AI-Modifiable |
| 8 | ai_audit_guard 本地模型评估 | 规则引擎优先，无需LLM | 3090+Qwen-7B本地评估 | GPT-4 API（成本高+泄露风险） | 300模块后按需启用 | 新建 | Human-Gated |
| 9 | ContractBus迁移追踪器 | JSON文件+状态机 | SQLite状态表 | 独立Dashboard（过重） | Phase 1B随迁移启动 | 新建 | Human-Gated |

**选型原则验证**：
1. ✅ 零外部依赖：SQLite > PostgreSQL > InfluxDB；自研规则 > OPA
2. ✅ 渐进式：EMA → SPC → LSTM；规则引擎 → 本地LLM
3. ✅ Python原生：Pydantic v2 > dataclass > Protocol Buffers
4. ✅ 成本敏感：全部开源免费，3090本地优先
5. ✅ 当前阶段适配：44文件→SQLite足够，不需要分布式

---

### 二、过度工程识别 【Qwen务实修正】

| 组件 | Kimi建议 | Qwen修正 | Hold触发条件 | 理由 |
|------|---------|---------|-------------|------|
| LLM-as-Judge容量评估 | V-04提到但未建议立即部署 | **【Qwen务实修正：Hold，模块数>300且AI决策错误率>10%时启用】** | 当前44文件，AI上下文<5%，LLM判断容量是"AI评价AI写的系统"——循环评估 |
| Formal Invariants（TLA+/Coq） | V-03建议形式化验证 | **【Qwen务实修正：Hold，ADR数量>20且发现2次以上不变量冲突时启用】** | TLA+/Coq学习曲线陡峭，单人项目投入产出比极低；先用Pydantic运行时校验 |
| Pydantic v2迁移（P3-1） | 纳入Phase 3 | 保留Phase 3，**但优先级下调** | 当前代码若未用Pydantic v1，v2迁移成本为0；若已用v1，迁移是破坏性变更 |
| event_bus_upgrade（P3-2 Redis） | 纳入Phase 3（条件触发） | **保留，触发条件更严格** | 44文件×单进程×asyncio.Queue足够；模块数>300且Queue深度>1000持续1小时才触发 |
| knowledge_engine（P3-3） | 纳入Phase 3 | **保留，但精简为规则引擎** | 无需ChromaDB扩展；先用YAML规则+SQLite存储 |
| context_compressor（P3-4） | 纳入Phase 3 | **保留，但目标从60%→40%** | 60%压缩率+40%人工修正=AI成为瓶颈；40%更安全 |
| ContractBus全量迁移44文件 | Phase 1B全量 | **【Qwen务实修正：分三批，每批15文件】** | Kimi已指出验证工作量>修改工作量；16-24h估算不含测试回归，实际需30-40h |
| V-05 ContractBus迁移追踪器 | Kimi建议立即部署 | 保留立即部署 | 轻量JSON文件，2h可完成，值得做 |

---

### 三、渐进路线图 【Qwen路线】

#### Phase 0（当前，1-2人日）

| 任务 | 工作量 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| P0-1 CTR-001手动修复 | 0.5h | 修复后的governance-asset-inventory.yaml | validate_ssot.py无矛盾报告 |
| P0-2 统一源码树迁移 | 4-8h | 单一`src/zephyr/`+删除旧树 | 所有import路径更新，测试全通过 |
| P0-3 validate_ssot.py | 4-6h | `scripts/governance/validate_ssot.py` | 检测到CTR-001同类矛盾 |
| **P0-4 capacity_slo.yaml** | 2-4h | `config/capacity/capacity_slo.yaml` | 定义≥6个量化SLI/SLO指标 |
| **P0-5 ai_audit_guard骨架** | 4-6h | `src/zephyr/shared/ai_audit_guard.py` | 可拦截AI修改请求并记录Provenance |

**Phase 0合计**：14.5-26.5h ≈ 2-3人日

#### Phase 1（立即，≤5人日，拆分为1a+1b）

**Phase 1a（结构容量，≤3人日）**：

| 任务 | 工作量 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| P1-1 `__getattr__`懒加载 | 2-4h | `src/zephyr/__init__.py` | 启动时间<2s@97模块 |
| P1-3 pre-commit分层 | 3-4h | `.pre-commit-config.yaml`更新 | 增量commit检查<10s |
| P1-4 dmypy配置 | 1-2h | `mypy.ini` | 增量类型检查<15s |
| P1-6 import-linter | 2-4h | `.importlinter`+`import-rules.yaml` | 0层内循环依赖 |
| P1-8 ZephyrLogger+OTel | 3-4h | `src/zephyr/shared/zephyr_logger.py` | 日志+Metrics双输出 |

**Phase 1a合计**：11-18h ≈ 1.5-2.5人日 ✅

**Phase 1b（通信+运行时，≤3人日）**：

| 任务 | 工作量 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| P1-5 事件总线背压 | 4-6h | `src/zephyr/shared/event_bus.py` | 生产者>消费者时无OOM |
| P1-7 ContractBus接口（第一批15文件） | 10-14h | `src/zephyr/shared/contract_bus.py`+15文件迁移 | 第一批15文件测试全通过 |
| **P1-9 ContractBus Schema Enforcement** | 3-4h | Pydantic模型定义 | 错误格式数据被拒绝而非崩溃 |
| **P1-10 ai_audit_guard规则配置** | 2-3h | `config/audit/audit_rules.yaml` | 覆盖knowledge_engine/event_bus/config_validator |
| **P1-11 capacity_governance_loop骨架** | 4-6h | `src/zephyr/shared/capacity_governance_loop.py` | 可采集≥3个容量指标 |

**Phase 1b合计**：23-33h ≈ 3-4人日 ✅

#### Phase 2（短期，5-7人日）

| 任务 | 工作量 | 触发条件 | 交付物 |
|------|--------|---------|--------|
| P2-1 YAML增量验证 | 6-8h | Phase 1完成 | 增量解析器 |
| P2-3 契约测试 | 8-12h | ContractBus迁移≥50% | 自研轻量契约测试 |
| P2-6 故障域隔离 | 6-8h | 模块数>150 | fault_isolator.py |
| P2-8 Warm→Hot阻断 | 3-4h | Hot Plane激活前 | warm_hot_gate.py |
| P2-9 ContractBus迁移（第二+三批） | 10-14h | 第一批验证通过 | 剩余29文件迁移完成 |

**Phase 2合计**：33-46h ≈ 4-6人日

#### Phase 3（中期，条件触发）

| 任务 | 触发条件 | 工作量 |
|------|---------|--------|
| P3-1 Pydantic v2迁移 | 确认使用v1且版本冲突 | 4-6h |
| P3-2 Redis升级 | Queue深度>1000持续1小时 | 6-10h |
| P3-3 知识引擎精简 | 模块数>300 | 4-6h |
| P3-4 AI上下文压缩（40%目标） | 上下文窗口不足率>50% | 4-6h |

---

### 四、Phase 1配置规格 【Qwen规格】

#### 1. Database Schema（SQLite）

```sql
-- AI Audit Provenance Store
CREATE TABLE IF NOT EXISTS ai_provenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    field TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ai_model TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    audit_result TEXT,
    hash TEXT NOT NULL  -- SHA-256 hash for chain integrity
);

CREATE INDEX IF NOT EXISTS idx_provenance_module ON ai_provenance(module);
CREATE INDEX IF NOT EXISTS idx_provenance_timestamp ON ai_provenance(timestamp);

-- Capacity SLO Data Store
CREATE TABLE IF NOT EXISTS capacity_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    threshold REAL,
    plane TEXT DEFAULT 'warm',  -- hot/warm/cold
    timestamp TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_capacity_metrics_name ON capacity_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_capacity_metrics_plane ON capacity_metrics(plane);
```

#### 2. capacity_slo.yaml

```yaml
# D:\ZephyrAlpha\config\capacity\capacity_slo.yaml
# [GOV:Policy] × [Plane:Warm]

version: "1.0.0"
ai_autonomy: Human-Gated  # SLO定义由Owner审批

sli_definitions:
  - name: startup_time_p99
    description: "模块启动时间P99"
    target: "3.0"
    unit: "seconds"
    plane: warm
    measurement: "lazy_loader"

  - name: type_check_time_p99
    description: "类型检查时间P99"
    target: "30"
    unit: "seconds"
    plane: warm
    measurement: "dmypy"

  - name: event_queue_depth_max
    description: "事件总线队列深度最大值"
    target: "500"
    unit: "items"
    plane: warm
    measurement: "event_bus"

  - name: config_consistency_rate
    description: "配置一致性检查通过率"
    target: "1.0"
    unit: "ratio"
    plane: warm
    measurement: "validate_ssot"

  - name: contract_bus_coverage
    description: "ContractBus覆盖率"
    target: "0.5"
    unit: "ratio"
    plane: warm
    measurement: "contract_bus"

  - name: ai_context_hit_rate
    description: "AI上下文命中率"
    target: "0.6"
    unit: "ratio"
    plane: warm
    measurement: "context_engine"

slo_alert_rules:
  - sliname: event_queue_depth_max
    warn_threshold: 0.8   # 400 items
    deny_threshold: 0.95  # 475 items
    action: "enable_backpressure"
  - sliname: startup_time_p99
    warn_threshold: 1.5   # 4.5s
    deny_threshold: 2.0   # 6.0s
    action: "notify_owner"
```

#### 3. audit_rules.yaml

```yaml
# D:\ZephyrAlpha\config\audit\audit_rules.yaml
# AI自治权限审计规则

version: "1.0.0"
ai_autonomy: Human-Gated

rules:
  - module: "knowledge_engine"
    field: "drift_detect_threshold"
    max_change_pct: 20  # 单次修改变化幅度≤20%
    cooldown_minutes: 60  # 60分钟内只能修改1次
    requires_approval: true

  - module: "event_bus"
    field: "backpressure_threshold"
    max_change_pct: 30
    cooldown_minutes: 30
    requires_approval: false

  - module: "config_validator"
    field: "validation_rules"
    max_change_pct: 0  # 禁止AI修改
    requires_approval: true
    immutable: true

  - module: "zephyr_logger"
    field: "sampling_rate"
    max_change_pct: 50
    cooldown_minutes: 15
    requires_approval: true
```

#### 4. 接口签名（Python type hints）

```python
# ai_audit_guard.py
from dataclasses import dataclass
from typing import Any, Protocol

class AuditResult:
    APPROVED = "approved"
    REJECTED = "rejected"
    COOLDOWN = "cooldown"

@dataclass
class ChangeRecord:
    module: str
    field: str
    old_value: Any
    new_value: Any
    ai_model: str
    timestamp: str
    audit_result: str

class AIAuditGuard:
    def __init__(self, rules_path: str, db_path: str) -> None:
        ...

    def validate_change(
        self, module: str, field: str, old_val: Any, new_val: Any
    ) -> str:  # AuditResult enum
        ...

    def record_provenance(self, change: ChangeRecord) -> None:
        ...

    def get_audit_log(self, module: str, limit: int = 100) -> list[ChangeRecord]:
        ...

    def check_cooldown(self, module: str, field: str) -> bool:
        """检查修改冷却期是否已过。"""
        ...
```

#### 5. 环境变量清单

```bash
# Capacity SLO Configuration
CAPACITY_SLO_CONFIG_PATH="config/capacity/capacity_slo.yaml"
CAPACITY_METRICS_DB_PATH=".audit_cache/capacity_metrics.db"

# AI Audit Configuration
AI_AUDIT_RULES_PATH="config/audit/audit_rules.yaml"
AI_AUDIT_PROVENANCE_DB_PATH=".audit_cache/ai_provenance.db"

# Governance Loop Configuration
CAPACITY_GOVERNANCE_INTERVAL_SECONDS=300  # 5分钟
CAPACITY_GOVERNANCE_LOOP_ENABLED=true
```

#### 6. 依赖包清单

```txt
# requirements-capacity.txt
pydantic>=2.0.0
structlog>=24.1.0
opentelemetry-api>=1.24.0
opentelemetry-sdk>=1.24.0
opentelemetry-instrumentation>=0.45b0
mypy>=1.8.0
import-linter>=2.0.0
pybreaker>=1.0.0
tenacity>=8.2.0
```

#### 7. AI自治权限标注（Phase 0/1新增组件）

| 组件 | 权限 | Provenance Chain要求 |
|------|------|---------------------|
| ai_audit_guard.py | Immutable Core | 自身代码变更需Owner审批 |
| audit_rules.yaml | Human-Gated | 修改需记录who/when/why |
| capacity_slo.yaml | Human-Gated | 修改需记录who/when/why |
| capacity_governance_loop.py | AI-Modifiable | 每次执行记录指标采集结果 |
| ai_provenance表 | Immutable Core | 只追加不删除，hash链完整性校验 |
| capacity_metrics表 | AI-Modifiable | 可追加可更新，保留7天历史 |

---

### 五、验收标准 【Qwen验收】

#### Phase 0

| 维度 | 标准 | 测量方式 |
|------|------|---------|
| 代码 | mypy通过率100%（新增代码） | `mypy scripts/governance/validate_ssot.py` |
| 代码 | ruff错误数=0 | `ruff check` |
| 架构 | CTR-001重复字段=0 | validate_ssot.py输出 |
| 架构 | 双源码树=0 | `ls -la src/zephyr/` vs 旧树目录 |
| AI | capacity_slo.yaml覆盖率≥6个SLI | YAML字段数检查 |

#### Phase 1

| 维度 | 标准 | 测量方式 |
|------|------|---------|
| 代码 | mypy通过率100%（新增代码） | `dmypy run` |
| 代码 | ruff错误数=0 | `ruff check` |
| 代码 | 测试覆盖率≥60%（新增组件） | `pytest --cov` |
| 架构 | import-linter违规数=0 | `lint-imports` |
| 架构 | ContractBus Schema Enforcement覆盖率≥第一批15文件 | 迁移追踪器 |
| AI | ai_audit_guard拦截率100%（AI修改请求） | audit_log计数 |
| AI | Provenance Chain完整性100% | hash链校验 |
| 性能 | 启动时间<2s@97模块 | 基准测试 |
| 性能 | 事件背压触发无OOM | 压力测试 |

#### Phase 2

| 维度 | 标准 | 测量方式 |
|------|------|---------|
| 代码 | 契约测试覆盖率≥50%（已迁移模块） | contract_tester输出 |
| 架构 | 故障域隔离覆盖≥3个域 | fault_isolator.py配置 |
| AI | capacity_governance_loop持续运行>7天无故障 | 系统日志 |
| 成本 | ai_audit_guard存储<50MB（7天） | 数据库文件大小 |

---

### 六、争议清单 【Qwen务实修正】

| # | 争议ID | 争议描述 | GLM立场 | Kimi立场 | Qwen立场 | Qwen理由 |
|---|--------|---------|---------|---------|---------|---------|
| 1 | C-01 | ContractBus迁移批次 | GLM：分两批（每批22） | Kimi：未提批次 | Qwen：分三批（15+15+14） | Kimi已指出验证工作量>修改工作量；15文件/批可控制回归风险 |
| 2 | C-02 | ai_audit_guard是否必须P0立即部署 | GLM：未识别V-01 | Kimi：立即部署P0 | Qwen：保留P0立即部署，但先部署骨架（4-6h），规则配置放Phase 1b | 骨架可拦截修改但规则可后补；降低Phase 0工作量 |
| 3 | C-03 | context_compressor压缩率目标 | GLM：60% | Kimi：未评价 | Qwen：从60%降至40% | 60%→40%人工修正→AI成为瓶颈；40%更安全 |
| 4 | C-04 | V-03 Formal Invariants（TLA+） | GLM：未识别 | Kimi：P1建议 | Qwen：Hold至ADR>20且发现2次+不变量冲突 | TLA+学习曲线陡峭，单人项目ROI极低；先用Pydantic运行时校验 |
| 5 | C-05 | V-04 LLM-as-Judge容量评估 | GLM：未识别 | Kimi：P1前沿概念 | Qwen：Hold至模块>300且AI错误率>10% | 当前AI上下文<5%，"AI评价AI写的系统"循环评估不可信 |
| 6 | C-06 | lazy_loader权限标注 | GLM：AI-Modifiable→Human-Gated | Kimi：确认Human-Gated | Qwen：确认Human-Gated | 懒加载策略影响启动顺序和模块可见性，属架构级变更 |
| 7 | C-07 | config_validator权限标注 | GLM：AI-Modifiable→Human-Gated | Kimi：确认Human-Gated | Qwen：确认Human-Gated | AI修改验证规则=AI定义什么是合法的，风险过高 |
| 8 | C-08 | ZephyrLogger采样率权限 | GLM：⚠️应Human-Gated | Kimi：确认Human-Gated | Qwen：确认采样率Human-Gated，日志级别保留AI-Modifiable | 采样率影响存储和审计完整性，日志级别不影响安全性 |

---

### 七、三轮审计总结 【Qwen务实修正】

| 缺口 | GLM识别 | Kimi根因 | Qwen落地方案 | 优先级 | AI自治权限 |
|------|---------|---------|-------------|--------|-----------|
| GAP-001 SLI/SLO缺失 | ✅ P0 | 容量视为技术非治理 | capacity_slo.yaml+Pydantic校验 | P0 | Human-Gated |
| GAP-002 OTel集成缺失 | ✅ P0 | structlog无Metrics | ZephyrLogger+OTel SDK | P1a | AI-Modifiable |
| GAP-003 7点格式不合规 | ✅ P0 | Vibe Coding跳过门禁 | 本文档补全（本步骤完成） | P0 | N/A |
| GAP-004 AISG容量缺失 | ✅ P0 | 未提及AISG角色 | 记录为P2缺口，暂不设计 | P2 | Human-Gated |
| GAP-005 风控容量预算 | ✅ P0 | 不同ADR未交叉映射 | Phase 2与ADR-0019 FLE集成时处理 | P2 | Human-Gated |
| GAP-006 ADR-0010三层映射 | ✅ P0 | 未完整映射三层 | capacity_slo.yaml标注[GOV:X]×[Plane:Y] | P0 | Human-Gated |
| GAP-007 FLE集成错误 | ✅ P0 | 不熟悉Protocol模式 | fault_isolator改为FeedbackAction适配器 | P2 | Human-Gated |
| GAP-008 INV冲突 | ✅ P0 | 重复新增 | 明确关系：INV-011是INV-NEW-001特例 | P0 | Immutable Core |
| V-01 Self-Modification | ❌ | 无制衡层 | ai_audit_guard.py | P0 | Immutable Core |
| V-02 Reward Hacking | ❌ | 无对抗性分析 | audit_rules.yaml限制参数变化幅度 | P1b | Human-Gated |
| V-05 工作量低估 | ❌ | Vibe Coding乐观偏差 | ContractBus分三批+迁移追踪器 | P1b | Human-Gated |
| V-08 反馈闭环缺失 | ❌ | 治理非持续系统 | capacity_governance_loop.py | P1b | AI-Modifiable |
| V-10 Schema Enforcement | ❌ | Protocol无校验 | Pydantic v2模型运行时校验 | P1b | Human-Gated |

---

### 八、建议的下一步行动（TOP 5）

1. **P0-4 capacity_slo.yaml定义**（2-4h，Trae CN免费模型）— 容量治理的"宪法"，无标准则无法判断"修好了没"，是后续所有工作的基准
2. **P0-5 ai_audit_guard骨架**（4-6h，Trae CN免费模型）— AI自治安全的最小可行监督层，无此则所有AI-Modifiable模块存在Self-Modification风险
3. **P0-3 validate_ssot.py**（4-6h，Trae CN免费模型）— 解决CTR-001同类矛盾自动检测，防止SSoT膨胀
4. **P0-1+P0-2 CTR-001修复+源码树统一**（4.5-8.5h，Trae CN免费模型）— 阻断级修复，是后续所有工作的基础
5. **P1a pre-commit分层+dmypy+import-linter**（6-10h，Trae CN免费模型）— 基础设施容量，为后续大规模开发提供质量门禁

> 总计：21-35h ≈ 3-5人日，可在一个长session或2个短session完成。
> 建议先在Cursor中完成架构确认（ADR-0010/0011引用），再在Trae CN中执行代码实现。

---

### 压缩报告 【Qwen务实修正】

- 压缩前行数：~1461行（v3.1 压缩后）
- 压缩后行数：~1461行（当前版本）
- 本次删除内容：
  1. GLM-5.1 结构扫描详细结果（~180行）→ 已压缩为「审计结果精华归档」
  2. Kimi K2.6 发现+深挖详细结果（~190行）→ 已压缩为「审计结果精华归档」
- 已保留精华内容：
  - 🔴技术选型总表（9项）完整保留
  - 🔴过度工程识别表（8项）完整保留
  - 🔴渐进路线图（Phase 0/1a/1b/2/3）完整保留
  - 🔴Phase 0/1配置规格（SQL/YAML/Python/环境变量/依赖包/AI权限）完整保留
  - 🔴验收标准（Phase 0/1/2）完整保留
  - 🔴争议清单（8项）完整保留
  - 🔴三轮审计总结（13项缺口）完整保留
  - 🔴TOP 5行动完整保留
  - 🔴扩展口子设计（5个Backend抽象+分片策略+分布式事件总线）完整保留
  - 🔴Kimi发散探索（7步：原意理解/方向展开/关键问题/类比先例/风险盲点/调研需求/文档压缩）完整保留
  - 🔴GLM调研扫描（GitHub/论文/技术选型/行业实践/项目对齐）完整保留
- 是否触发拆分：否（单文档承载全部内容，通过章节导航可快速定位）

---

## Claude 终审裁决结果（Wave 0 · Opus 4.7 · 2026-04-27）

> 本块是终审大法官的不可上诉终审。完整真源方案分布于 6 份蓝图真源 + 2 份治理文档，本块仅给出本文档相关的裁决与兜底结论，详细内容指向真源路径。

### 一、争议裁决（与本文档强相关）

| # | 争议ID | 描述 | Claude裁决 | 理由（≤100字） |
|---|--------|------|-----------|----------------|
| 1 | C-01 ContractBus | 迁移批次 | **B：分三批（15+15+14）**（采纳 Qwen 立场） | Kimi 已指出验证工作量>修改工作量；15 文件/批可控回归风险；分两批一次性回归压力过大 |
| 2 | C-02 ai_audit_guard | P0 立即部署 vs 推迟 | **A：P0 立即部署骨架（4-6h）+ Phase 1b 配置规则**（采纳 Qwen 修正） | 安全优先：骨架先拦截再配规则；总工作量分摊不阻断 P0 |
| 3 | C-03 context_compressor | 压缩率 60% vs 40% | **B：40%**（采纳 Qwen 修正） | 60% 压缩需大量人工修正→AI 成为瓶颈；40% 更安全，符合务实落地原则 |
| 4 | C-04 V-03 Formal Invariants/TLA+ | P1 vs Hold 至 ADR>20 | **B：Hold，触发条件 = ADR>20 且 ≥2 次不变量冲突**（采纳 Qwen 修正） | TLA+ 学习曲线陡峭单人 ROI 极低；Pydantic v2 + assert 已覆盖 90% 场景 |
| 5 | C-05 V-04 LLM-as-Judge | P1 vs Hold 至 模块>300 | **B：Hold，触发条件 = 模块>300 且 AI 错误率>10%**（采纳 Qwen 修正） | 当前 AI 上下文<5%，"AI 评价 AI 写的系统"循环评估不可信 |

权限标注三方共识（C-06/C-07/C-08）已被 Claude 终审完整接纳，写入 G1 注册表。

### 二、缺口兜底（Claude 兜底，≤3 条）

| ID | 组件 | 说明 | 前三轮为何未发现 | 严重度 | AI 自治权限 |
|----|------|------|----------------|--------|-----------|
| **V-11** | AI 自治权限注册表 | 全 60+ 模块权限单一真源 | 三轮各看自己负责文档，未横向汇总，权限错误率 25-30% | P0 | Immutable Core |
| **V-12** | 蓝图真源准入门禁 `validate_blueprint_provenance.py` | pre-commit 校验真源目录必带 provenance 三件套（A 区→B 区→真源目录的物理轨迹） | 三轮专注内容质量，未问"蓝图本身合法性怎么验证" | P0 | Immutable Core |
| **V-13** | 任务卡元层登记表 `task-card-meta-registry.yaml` | 登记三套并行任务卡系统（旧卡/v2 隔离区/SQLite 任务库）状态与迁移路径 | 三轮焦点是 schema/接口，未解决"系统间过渡污染" | P1 | Human-Gated |

### 三、评分修正

无。GLM 15 维度评分通过 Kimi 根因 + Qwen 落地已稳定，本次终审不做修正。

### 四、真源方案路径

| # | 类型 | 路径 | 职责 |
|---|------|------|------|
| B1 | 目标架构 | `docs/02_enterprise_architecture/target-architecture/vibe-coding-infrastructure-architecture.md` | 7 模块物理拓扑 + 技术栈终选 |
| B2 | 目标架构 | `docs/02_enterprise_architecture/target-architecture/vibe-coding-development-workflow.md` | 双管线流程 + 脚本系统 |
| **B3** | **施工图（本文档真源对应）** | `docs/04_construction_plans/construction-plan-capacity-assurance.md` | 容量保障 Phase 0-2 完整施工图 |
| B4 | 施工图 | `docs/04_construction_plans/construction-plan-vibe-coding-pipelines.md` | 双管线 Phase 0-3 |
| B5 | 施工图 | `docs/04_construction_plans/construction-plan-task-card-and-kms.md` | 任务卡 + M9 知识库 |
| G1 | 治理注册表 | `docs/01_policies_and_standards/ai-autonomy-authority-registry.md` | 全模块权限单一真源 |
| G2 | 治理协议 | `docs/01_policies_and_standards/drafts-audits-arbitration-protocol.md` | 草稿-审计-裁定协议 |

ADR 体系停用：见 `architecture-rationale-log.md` R-72（M2 建成同 commit 内删除现存 36 份 ADR）。

### 五、本审计源档案归位

本文件 Wave 0 末尾迁入 A 区档案：`docs/19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/capacity-assurance-construction-plan.md`，frontmatter 设置 `audit_status: arbitrated` + `superseded_by: docs/04_construction_plans/construction-plan-capacity-assurance.md`，作为四轮审计的历史证据永久保留。

### 六、48h 行动清单（≤5 项 · Owner 可独立执行）

| # | 行动 | 工作量 | 平台 |
|---|------|--------|------|
| 1 | `scripts/governance/validate_blueprint_provenance.py` 骨架（V-12） | 4-6h | Trae CN 免费 |
| 2 | `ai-autonomy-authority-registry.md` 启用 pre-commit 自校验 | 2-4h | Trae CN 免费 |
| 3 | `task-card-meta-registry.yaml` 登记 3 套任务卡系统（V-13） | 2-3h | Cursor |
| 4 | 8 份候选池审计源 frontmatter 加 `superseded_by` 指针 | 1-2h | Cursor |
| 5 | `architecture-rationale-log.md` 追加 R-71~R-79 决策记录 | 1-2h | Cursor |

合计 10-17h ≈ 1.5-2.5 人日，≤48h 完成。

### 压缩报告（终审块）

- 压缩前行数：本文件原始行数（不删原内容，仅追加）
- 压缩后行数：原行数 + ~95 行
- 删除内容：无（硬约束 13）
- 压缩内容：无（本块不重复真源方案完整内容，通过 §四指针定位）
- 不可删除内容确认：✅ 真源方案全章节由 6+2 份蓝图/治理承载；✅ 争议裁决表完整；✅ AI 自治权限终表移至 G1；✅ 48h 行动清单完整；✅ 评分无修正；✅ 缺口清单分布 G1+B3/B4/B5；✅ 技术选型分布 B1；✅ 渐进路线分布 B3-B5
- 是否触发拆分：是（真源方案拆分到 8 份蓝图/治理 - 避免单文档>2500 行）
- 拆分文档：B1/B2/B3/B4/B5/G1/G2（见 §四）+ A/B 区档案
