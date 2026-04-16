---
module_id: ARCH_TECH_DECISION_RECORDS
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P0
---

# ZephyrAlpha 技术决策记录 (Architecture Decision Records)

> **用途**：记录重要的技术选型决策——为什么选 X 而不是 Y，决策背景、影响和替代方案。
> **格式**：每条 ADR 包含：决策标题、状态、日期、背景、决策内容、替代方案、后果。
> 引入新技术前必须检查本文件，确认是否有已有决策可参考。

---

## ADR-001：使用 structlog 而非 logging

| 字段 | 内容 |
|------|------|
| **状态** | Accepted |
| **日期** | 2026-04-16（回溯记录）|
| **决策者** | Project Owner |
| **背景** | 需要跨层追踪 layer/module/operation 上下文，标准 logging 不支持结构化 |
| **决策** | 使用 `structlog` 进行结构化日志记录，每条日志必须包含 `layer`、`module`、`operation` 上下文 |
| **替代方案** | Python 标准 `logging`（被否决：无结构化上下文支持）|
| **后果** | 所有模块日志格式一致，可直接解析为 JSON；学习曲线较低 |

---

## ADR-002：使用 tenacity 进行 API 重试

| 字段 | 内容 |
|------|------|
| **状态** | Accepted |
| **日期** | 2026-04-16（回溯记录）|
| **决策者** | Project Owner |
| **背景** | 外部 API（AKShare 等）存在偶发性失败，需要指数退避重试 |
| **决策** | 所有外部 API 调用使用 `tenacity` 库，配置 3 次重试 + 指数退避 |
| **替代方案** | 手动 while 循环（被否决：代码冗余，难以统一配置）|
| **后果** | 统一的重试行为；tenacity 装饰器语法简洁 |

---

## ADR-003：使用 Pydantic v2 进行数据验证

| 字段 | 内容 |
|------|------|
| **状态** | Accepted |
| **日期** | 2026-04-16（回溯记录）|
| **决策者** | Project Owner |
| **背景** | 需要对 OHLCV、信号、订单等数据进行类型安全的验证 |
| **决策** | 使用 Pydantic v2 定义所有数据模型（OHLCVBar、Signal、Order 等）|
| **替代方案** | dataclasses（被否决：验证能力弱）；attrs（被否决：生态系统小）|
| **后果** | 自动类型验证、序列化/反序列化、IDE 类型提示完整 |

---

## ADR-004：使用 ZephyrBaseError 异常层次

| 字段 | 内容 |
|------|------|
| **状态** | Accepted |
| **日期** | 2026-04-16（回溯记录）|
| **决策者** | Project Owner |
| **背景** | 需要统一的异常处理，便于上层系统判断错误类型 |
| **决策** | 所有模块抛出的异常继承自 `ZephyrBaseError`；禁止空的 `except:` 块 |
| **替代方案** | 使用标准异常（被否决：无法区分业务错误和系统错误）|

---

## ADR-005：数据存储使用 DuckDB + Parquet

| 字段 | 内容 |
|------|------|
| **状态** | Under Review |
| **日期** | 待确认 |
| **决策者** | TBD |
| **背景** | 需要高效存储和查询 OHLCV 时序数据及回测结果 |
| **候选方案** | DuckDB（本地）/ PostgreSQL / ClickHouse / TimescaleDB |
| **当前偏好** | DuckDB + Parquet（零配置，Python 原生，分析性能强）|
| **后果** | 本地开发友好；不适合高并发写入场景 |

---

## ADR-010：docs/ 目录编号体系重设计（治理基础设施 vs 业务内容两维分离）

| 字段 | 内容 |
|------|------|
| **状态** | Proposed |
| **日期** | 2026-04-16 |
| **决策者** | Project Owner（待批准）|
| **背景** | docs/ 一级目录存在 6 处同编号多义冲突（01_, 02_, 03_, 04_, 07_, 08_ 各有两个不同目录），根因是"Layer 编号对齐逻辑"与"治理/基础设施目录"抢占相同号段 |
| **决策** | 采用两维分离：`00–09` 保留给治理/基础设施域，`10–29` 给业务内容域（对应 Layer 编号）；7 个目录保留不动，13 个目录分 A/B/C 三批重命名 |
| **替代方案** | 保持现状接受冲突（否决：AI 导航错误、认知负担高）；高位号段治理域如 `80–89`（否决：治理文档需高优先级，低位更直观）|
| **后果** | 消除 6 处冲突；迁移 ~2559 个文件需分批执行；旧路径须在废弃路径表维护 ≥6 个月 |
| **方案文档** | `docs/11_STRATEGIC_DECISION/directory-numbering-redesign-plan.md` |
| **映射表** | `docs/01_GOVERNANCE/REGISTERS/directory-numbering-map-v1.yaml` |

---

## 待决策清单

| 编号 | 议题 | 背景 | 目标决策日期 |
|------|------|------|------------|
| ADR-006 | ML 框架：scikit-learn vs LightGBM 优先级 | L04 施工前 | Phase 2 施工图阶段 |
| ADR-007 | 回测框架：Backtrader vs 自研 vs Zipline | L05 施工前 | Phase 2 施工图阶段 |
| ADR-008 | LLM API 选型：OpenAI vs Claude vs 本地部署 | L07 施工前 | Phase 2 施工图阶段 |
| ADR-009 | 消息队列：是否引入（Kafka/Redis Streams） | 实时信号传递场景 | Phase 2 施工图阶段 |

---

## 变更历史

| 版本 | 日期 | 变更描述 | 变更人 |
|------|------|---------|--------|
| 1.0.0 | 2026-04-16 | 初始创建，补录既有决策 | AI |
