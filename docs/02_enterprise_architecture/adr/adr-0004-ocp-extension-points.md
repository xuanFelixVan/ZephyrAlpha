---
module_id: ADR-0004
title: OCP 扩展点机制作为架构终局锚点（因子 / 策略 / 券商三层注册机制）
doc_type: adr
status: active
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-18
superseded_by: null
supersedes: null
related_rationale: R29, R30
related_open_questions: []
tags:
- adr
- ocp
- extension-points
- factor-registry
- strategy-registry
- broker-interface
- sprint2
summary: 决定在 L02（Alpha Factor）、L05（Portfolio Construction）、L06（Trade Execution）三层引入
  OCP 扩展点机制（基类 + 注册表 + 插件自动发现）。核心理由：ZephyrAlpha 2.0 需要支撑 AI 自主迭代几百个因子/策略/券商适配器，OCP
  机制是唯一能在"只写新文件、不改旧代码"约束下实现此目标的架构选择。
date: '2026-04-22'
ttl: permanent
---

# ADR-0004: OCP 扩展点机制作为架构终局锚点

---

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-18
- **拍板日期**：2026-04-18
- **被谁取代**：无
- **取代了谁**：无（新增决策）

---

## 2. 背景与问题（Context）

### 2.1 问题陈述

ZephyrAlpha 2.0 的核心愿景是**AI 自主迭代**：AI 协作者（Kimi + Claude）能在无需人工干预的情况下，持续向系统添加新因子、新策略、新券商适配器。

当前（2026-04-18）架构中，L02 / L05 / L06 三层没有正式的扩展机制：

- 添加新因子需要修改因子计算流水线的调用代码
- 添加新策略需要修改组合构建调度逻辑
- 接入新券商需要修改执行层路由代码

这意味着每次扩展都会**破坏已有代码**，引入回归风险，且 AI 协作者无法安全地"只写新文件"来完成扩展。

### 2.2 为什么必须做决策

- **AI 自主迭代的前提**：AI 协作者在 Cursor / Trae 中每次只能操作有限上下文。"修改现有调用代码"需要 AI 理解整个调用链，出错风险高；"只写新文件 + 注册"是 AI 安全操作的上限。
- **扩展规模预期**：未来 3-5 年预期因子数量 100+、策略数量 50+、券商 3-5 家。每次都改核心代码不可持续。
- **架构终局锚点需要现在确定**：如果等到因子/策略数量增多后再重构，迁移成本将指数级增长。

### 2.3 相关讨论来源

- 2026-04-17 会话 04：用户提出"AI 自我迭代几百策略"架构需求
- `rationale-log.md` R29（演进式架构）、R30（OCP 扩展点）
- Sprint 1 实施验证：B1-B4 已完成，本 ADR 为事后正式记录

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：OCP 注册表机制（**本次选择**）

在 L02 / L05 / L06 各引入一套"基类 + 注册表 + 自动发现"三件套：

```
基类（抽象接口）← 扩展者实现
注册表（装饰器）← 扩展者用 @Registry.register 自动注册
自动发现器     ← 流水线启动时扫描实现目录，无需手工配置
```

- **优点**：
  - 添加新因子/策略/券商只需新建一个文件，**不修改任何现有代码**（Open-Closed Principle）
  - AI 协作者可以安全、批量地创建扩展，无回归风险
  - 注册表提供全局索引，支持按 ID 查询、按域过滤、元数据管理
  - 自动发现器（`autodiscover_factors()`）无需手工维护列表
  - 机构案例：QuantLib（因子插件）、Zipline（策略注册）、各家量化框架均采用此模式
- **缺点**：
  - 引入装饰器魔法，调试时栈追踪稍复杂
  - 需要维护基类契约（但这正是我们希望锁定的架构锚点）

### 方案 B：工厂函数 + 显式注册字典

用 `dict` 维护 `{"factor_id": FactorClass}` 映射，添加新因子时手动往字典里加一行。

- **优点**：简单直接，无装饰器魔法
- **缺点**：
  - 每次添加新因子都需要修改工厂字典——违反 Open-Closed Principle
  - AI 协作者需要修改现有文件，引入回归风险
  - 字典规模增大后维护成本线性增长

### 方案 C：动态 `import` + 命名约定（约定优于配置）

约定 `factors/` 目录下所有文件都是因子，通过目录扫描 + `importlib` 动态加载，无需注册。

- **优点**：零配置，纯约定驱动
- **缺点**：
  - 无中央注册表，无法按 ID / 域查询因子元数据
  - 缺少类型化元数据（因子 ID、版本、域分类），不支持 KMS 知识管理
  - 加载失败时静默忽略，不易发现问题

### 方案 D：微服务 / 插件 DLL 模式

每个因子/策略打包为独立微服务或动态库，通过 RPC 调用。

- **优点**：完全隔离，语言无关
- **缺点**：
  - 当前系统规模远未到微服务合理点（单开发者、单进程）
  - 引入跨进程通信成本，违背"当前阶段不引入不必要复杂性"原则
  - 与 Python 量化生态不兼容（NumPy/Pandas 跨进程传输成本高）

---

## 4. 决策（Decision）

**最终选择：方案 A — OCP 注册表机制**

选择理由：

1. **AI 自主迭代可行性**：方案 A 是唯一能让 AI 协作者"只写新文件"完成扩展的方案，直接支撑 ZephyrAlpha 2.0 的核心愿景。
2. **Open-Closed Principle 完全实现**：注册表机制在 Python 量化生态中是经过时间验证的成熟模式，无技术风险。
3. **元数据丰富性**：`FactorMeta` / `StrategyMeta` 提供结构化元数据（ID、版本、域分类、依赖），是后续 KMS 知识管理和因子评估体系的基础数据。
4. **方案 B 被排除**：违反 OCP，每次扩展都改现有文件，AI 协作无法安全执行。
5. **方案 C 被排除**：缺少元数据管理，无法支撑因子注册表查询。
6. **方案 D 被排除**：当前规模不适合微服务，引入不必要复杂性。

**决策范围**：

| 扩展点 | 层 | 基类 | 注册表 | 自动发现 | 扩展目录 |
|--------|----|----|-------|---------|---------|
| 因子扩展点 | L02 | `FactorBase` | `FactorRegistry` | `autodiscover_factors()` | `l02/factors/` |
| 策略扩展点 | L05 | `StrategyBase` | `StrategyRegistry` | `autodiscover_strategies()`（待实现） | `l05/strategies/` |
| 券商扩展点 | L06 | `BrokerInterface` | 配置驱动加载（`broker_id`） | 配置文件指定 | `l06/adapters/` |

**不在本 ADR 范围内**（不锁死）：
- 具体因子实现（`factors/` 目录内容）
- 具体策略实现（`strategies/` 目录内容）
- 具体券商适配器实现（`adapters/` 目录内容）
- `autodiscover_strategies()` 的具体实现时机

---

## 5. 后果（Consequences）

### 正面后果

- **AI 协作安全边界**：AI 协作者可以放心创建 `factors/xxx.py`、`strategies/xxx.py`、`adapters/xxx.py`，绝不触碰已锁定的基类 / 注册表文件
- **无限扩展，零回归风险**：注册第 1 个因子和注册第 237 个因子的代价相同，且不会影响已有因子
- **因子/策略索引**：`FactorRegistry.list_all()` / `list_by_domain()` 使系统可以内省所有已注册能力，为 KMS 分析提供基础数据
- **架构稳定性**：基类 + 注册表文件被标记为 `🔒`（锁死），任何变更必须先建 ADR，防止意外破坏

### 负面后果 / 权衡

- **装饰器理解门槛**：新开发者（或首次接触此模式的 AI）需要理解 `@FactorRegistry.register` 装饰器的工作原理
  - 缓解措施：`architecture-model/contracts/cross-layer-contracts.yaml` 有完整使用示例
- **注册表全局状态**：`FactorRegistry` 是全局单例，测试时需要注意隔离（可用 `registry.clear()` 方法在测试后清理）
- **序列化挑战**：注册表中存储的是类引用，不可直接序列化，分布式场景需另行设计
  - 当前影响：无（单进程架构）

### 未来需要重新审视的触发条件

满足以下条件时，本 ADR 应被重新评估：

- 系统迁移到多进程 / 微服务架构（因子计算需要跨进程传递注册信息）
- 因子库规模超过 500 个（注册表扫描性能可能成为瓶颈）
- 需要支持动态热加载（不重启进程而更新因子）

---

## 6. 落地动作（Implementation）

本决策的落地动作已在 `architecture-finalization-taskbook.md` Sprint 1 完成（B1-B4）：

- ✅ B1：`FactorBase` + `FactorRegistry` + `autodiscover_factors()` 接口签名定义（`architecture-model/contracts/cross-layer-contracts.yaml`）
- ✅ B2：`StrategyBase` + `StrategyRegistry` 接口签名定义（`architecture-model/contracts/cross-layer-contracts.yaml`）
- ✅ B3：`BrokerInterface` 接口签名定义（`architecture-model/contracts/cross-layer-contracts.yaml`）
- ✅ B4：整合到 `03-application-architecture.md §4.4`
- **本 ADR（B5）**：正式架构决策记录

待办（升格后）：

- [x] `adr-drafts/ADR-DRAFT-0004-ocp-extension-points.md` → `adr/adr-0004-ocp-extension-points.md`（评审通过后）（Sprint 6 G1 完成）
- [x] 在 `adr/index.md` 追加本 ADR 条目（Sprint 6 G1 完成）

---

## 7. 参考

- 相关 ADR：
  - `adr/adr-0003-dual-ai-collaboration-workflow.md`（双 AI 协作工作流）
- 相关架构文档：
  - `target-architecture/03-application-architecture.md §4.4`（OCP 扩展点设计）
  - `target-architecture/architecture-model/contracts/cross-layer-contracts.yaml`（扩展点接口签名）
  - `target-architecture/diagrams/dataflow-terminal.mmd`（全链路数据流，含 OCP 节点标注）
- 外部参考：
  - Martin Fowler, *Refactoring*: Plugin 模式与 Registry 模式
  - Zipline（Quantopian）策略注册机制
  - QuantLib 因子插件体系
  - SOLID Principles — Open/Closed Principle（Bertrand Meyer, 1988）

---

## 8. 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-18 | v1.0.0 | Sprint 2 产出 B5。记录 OCP 扩展点机制决策（方案 A 注册表机制），对比四个备选方案，明确三层扩展点范围与不锁死内容。引用 Sprint 1 已完成的实施产出（B1-B4）。 |
| 2026-04-18 | v1.1.0 | Sprint 6 G1 升格：草稿状态 proposed → accepted，正式移入 adr/ 目录，拍板日期确认为 2026-04-18。 |
