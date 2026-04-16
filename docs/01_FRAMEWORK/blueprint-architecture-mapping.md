---
module_id: BLUEPRINT_ARCHITECTURE_MAPPING
version: 1.0.0
status: Active
priority: P0
created_date: 2026-04-13
last_updated: 2026-04-13
owner: 首席文档架构师
layer: layer_01
responsibility: 01_FRAMEWORK
standard_type: 架构映射文档
applicable_scope: 业务时间框架与 Layer 0-11 技术流水线对照
compliance_level: 专业标准
parent_document: ./ARCHITECTURE.md
---
# 蓝图与架构映射（BLUEPRINT_ARCHITECTURE_MAPPING）







> **核心职责**：说明 **三级时间框架（业务决策）** 与 **Layer 0～11（技术流水线）** 的对应关系。  



> **权威顺序**：与 ARCHITECTURE.md 冲突时，**以 ARCHITECTURE.md 为准**。  



> **职责边界**：回测链上因子 / 策略 / 引擎分工见 MODULE_RESPONSIBILITY_BOUNDARIES.md。







```
```---
```







## 接口与契约（蓝图终稿）







- 全库 API 与事件约定真源：`API_Contract.md`。本文件仅做“架构映射”，但若映射中引用到对外能力（如数据查询、信号下发、执行指令、风控拦截、审计查询），其最终契约口径以该真源为准。







## 验收标准（可检查）







- 能从本文件第 2 节表格中，逐行核对“业务视角 → Layer 编号”映射，并与 `ARCHITECTURE.md` 的 Layer 定义保持一致（出现冲突时能定位到冲突点并以 `ARCHITECTURE.md` 为准）。



- 本文件中出现的所有相对链接应可点击跳转（Markdown link 可解析），并且不引入新的无效链接。



- 若新增映射项，需至少在本文件或 `ARCHITECTURE.md` 的“相关文档”中提供一个可点击入口，保证读者能从映射回到权威说明或模块蓝图。







## 已知限制







- 本文件是“映射层”文档，不负责定义具体模块的接口字段、事件载荷与异常码；这些细节应在 `API_Contract.md` 与各模块蓝图/技术规格书中闭合。







## 1. 双重架构体系







| 类型 | 文档 | 用途 |



|------|------|------|



| 业务架构 | PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE.md | 宏观 / 中观 / 微观决策与策略划分 |



| 技术架构 | ARCHITECTURE.md | Layer 0～11、数据流、模块分层 |







### 1.1 场景选型







| 场景 | 优先阅读 |



|------|----------|



| 策略与时间框架划分 | 三级时间框架架构 |



| Layer 编号、数据流、顶层模块 | ARCHITECTURE.md |



| 因子库 / 策略引擎 / 回测引擎谁做什么 | MODULE_RESPONSIBILITY_BOUNDARIES.md |







```
```---
```







## 2. 时间框架 ↔ Layer 对照摘要







| 业务视角（示意） | 主要 Layer | 说明 |



|------------------|------------|------|



| 数据与预处理 | Layer 0～1 | 数据源、清洗、对齐 |



| Alpha 与特征 | Layer 2 | 因子计算与因子库 |



| 舆情与事件 | Layer 3 | 情感 / 事件信号（通常由 Layer 5 策略消费） |



| 机器学习 | Layer 4 | ML / AI 因子与预测 |



| 策略与执行 | Layer 5 | 策略逻辑、信号、下单路径 |



| 组合优化 | Layer 6 | 权重、约束、优化 |



| 报告与交互 | Layer 7～8 | AI 报告、人机协同 |



| 研究 / 治理 / 战略 | Layer 9～11 | 见 ARCHITECTURE 与各层主蓝图 |







```
```---
```







## 3. 技术规格书入口（示例）







| 主题 | 文档 |



|------|------|



| 智能执行 | SMART_EXECUTION_ENGINE_TECHNICAL_SPECIFICATION.md |



| 市场冲击 | MARKET_IMPACT_MODEL_TECHNICAL_SPECIFICATION.md |



| QMT 数据接口 | QMT_DATA_INTERFACE_TECHNICAL_SPECIFICATION.md |







```
```---
```







## 4. 治理与同步







- **实施侧蓝图全目录索引**（机器维护）：[`01_BLUEPRINTS/INDEX.md`](../05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md)（运行 `python scripts/generate_01_blueprints_index.py` 更新）。  



- 新增或重命名蓝图 / 规格书后，应在本文件或 ARCHITECTURE.md 「相关文档」中 **至少一处** 可点击到达。  



- 架构级缺口与矛盾登记：ARCH_MODULE_GAP_REGISTER_20260408.md。  



- 执行方案：ARCHITECTURE_MODULE_AUDIT_AND_GAP_PLAN_20260408.md。







```
```---
```







**版本**: v1.1 | **更新**: 2026-04-08 | **状态**: Active



