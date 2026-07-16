---
module_id: MOD-L06-001
submodule_path: src/zephyr/ex_core
title: "Trade Execution Core 蓝图+施工图 — 交易执行引擎"
doc_type: blueprint
status: Active
version: "2.2.1"
layer: L2_domain
layer_name: trade_execution
functional_domain: execution
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
last_updated: "2026-07-17"
last_verified: "2026-07-17"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/ex_core/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
generation: 2
codification_level: L1
codification_at: "2026-05-15"
rule_form: structural
scope: module
stability: evolving
verifiability: manual
ssot_yaml: "docs/03_modules/_domain_execution_core/blueprint.md"
summary: "D_EXECUTION_CORE 交易执行层——BrokerInterface OCP-003 扩展点 + 订单状态机 + SOR 路由 + 算法执行 + MiniQMT实盘Broker(v2.2.0)。Phase 1 部分实现：执行引擎+订单管理+模拟券商；v2.2.0规划MiniQMT Broker适配器对接xttrader，与D_BACKTEST matching_engine共用撮合逻辑(回测=实盘一致性)。"
tags: [trade-execution, l06, phase-1-partial, execution-engine, order-management, sor-routing, miniqmt, real-trading]
priority: P0
runtime_plane: hot
depends_on:
  - target: "MOD-L05-001"
    at: "CTR-004"
    why: "消费 Order"
  - target: "MOD-L04-001"
    at: "CTR-ERR-004"
    why: "消费 RiskLimitViolationError"
  - target: "MOD-L00-001"
    at: "§16.7.1"
    why: "v2.2.0新增: MiniQMT Broker 与 D_DATA MiniQmtProvider 共用 xtquant/xttrader 通道"
  - target: "MOD-BT-001"
    at: "§16.7 matching_engine"
    why: "v2.2.0新增: 回测=实盘一致性, MiniQMT Broker 与 D_BACKTEST matching_engine 共用撮合逻辑"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_execution_core\\blueprint.md"
    section: "全篇"
    why: "本蓝图即SSoT"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_data\\blueprint.md"
    section: "§16.7.1"
    why: "MiniQMT Provider 规格(Tick+5档盘口), MiniQMT Broker 共用 xttrader 连接"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain_backtest\\blueprint.md"
    section: "§16.7"
    why: "matching_engine Tick级5档撮合规格, MiniQMT Broker 实盘撮合逻辑需保持一致"
responsibility_domain: 
design_maturity: design
build_status: generated
---

> module_id: MOD-L06-001 | version: 2.2.0 | status: Active | layer: l06
> actual_disk_path: src/zephyr/ex_core/ | generation: 2 | construction_progress: partially_implemented
> v2.2.0新增: MiniQMT实盘Broker适配器(对接xttrader), 与D_BACKTEST matching_engine共用撮合逻辑(回测=实盘一致性)

> ✅ **业务层已开放，可施工**：D_EXECUTION_CORE 属于 C 轨业务层，当前阶段基础设施尚未就绪。可以此蓝图为依据生成交易执行业务代码。开工触发条件：(a) MOD-MASTER_BLUEPRINT construction_progress >= implementation_phase；(b) Gate Engine 覆盖本层业务检查类型；(c) 至少一个 CT-* 契约从规划到部分实现。

# Trade Execution Core 蓝图+施工图 — 交易执行引擎

> **真源声明**：本蓝图是 ZephyrAlpha 交易执行层的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 交易执行层——它解决了订单从生成到成交的全生命周期管理问题。核心职责包括：多券商路由（SOR）、算法执行（TWAP/VWAP/冰山单）、订单状态机管理、成交回报处理与持仓快照维护。当前规模 1 个券商适配器（SimulationBroker）+ 3 种算法策略，目标容量 3+ 券商适配器 + 5+ 算法策略 + 100+ 并发订单。上游依赖 D_PORTFOLIO_CORE 组合构建层（CTR-004 Order）和 D_RISK 风控层（CTR-ERR-004），下游被 D_REPORTING 分析层和 D_ML_TRAIN ML 平台消费。

**v2.2.0 新增决策(2026-07-04)**：
1. **MiniQMT实盘Broker**: 新增 `adapters/miniqmt_broker.py`，对接国金证券MiniQMT的xttrader API，支持A股实盘交易(股票/ETF/可转债)
2. **回测=实盘一致性**: MiniQmtBroker的实盘撮合规则与D_BACKTEST matching_engine共用同一份撮合逻辑(避免回测-实盘偏差>30%告警)
3. **与D_DATA共用xtquant**: MiniQmtBroker(xttrader交易) 与 D_DATA MiniQmtProvider(xtdata行情) 共用miniQMT终端连接，单点登录
4. **5档盘口撮合**: 实盘下单基于5档盘口实时报价(askPrice/bidPrice)，与回测Tick级撮合逻辑一致
5. **幂等+断线重连**: 所有下单携带idempotency_key(INV-007), 支持断线重连后订单状态同步

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L06-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | `broker_interface.py` | §3.1 | BrokerInterface ABC + register_broker() | 已实现 |
| 2 | `execution_engine.py` | §3.1 | 算法执行 + SOR 路由 + 风控校验 | 已实现 |
| 3 | `order_manager.py` | §3.1 | 订单生命周期状态机 | 已实现 |
| 4 | `adapters/simulation_broker.py` | §3.1 | 模拟券商适配器 | 已实现 |
| 5 | `adapters/__init__.py` | §3.1 | 适配器注册 | 已实现 |
| 6 | `__init__.py` | §4.2 | CTR 声明 + 模块导出 | 已实现 |
| 7 | `adapters/miniqmt_broker.py` | §16.7.1 | **v2.2.0新增** MiniQMT实盘Broker(对接xttrader, A股实盘交易) | 已施工(部分: P0已修, P1余项见审计清单) |

> YAML SSoT 列出 `simulation_broker.py` 在根目录，实际磁盘位于 `adapters/` 子目录。

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☑ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☑ |
| actual_disk_path 与 §11 产出物路径一致 | 路径比对 | ☑ |
| YAML SSoT files 列表与磁盘文件一致 | 逐文件核对 | ☐ adapters/ 子目录待同步 |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | BrokerInterface, ExecutionEngine, OrderManager, SimulationBroker | RiskValidator ABC 注入, ExecutionReport 产出, 真实券商适配器 | 待实现 |
| v2.0.0 (模板v3.3重构) | 同 v1.0.0 + 章节结构重组 | 同 v1.0.0 | 结构重组，无功能变更 |
| v2.1.0 (模板v4.1回填) | 同 v2.0.0 | 同 v1.0.0 | 模板合规回填，无功能变更 |
| v2.2.0 (MiniQMT Broker规划) | 同 v2.1.0 | 同 v1.0.0 + adapters/miniqmt_broker.py(P0已修) | MiniQMT实盘Broker规格, 与D_BACKTEST/D_DATA协同, P0已修(P1余项见审计清单) |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 量化系统需要一个交易执行层，将 D_PORTFOLIO_CORE 组合构建层产出的 Order 转化为实际成交（Fill），同时维护持仓快照供 D_RISK/D_REPORTING/D_ML_TRAIN 消费。当前仅有 SimulationBroker 用于回测，真实券商接入需 OCP-003 扩展点支持。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 券商扩展点：BrokerInterface (OCP-003) 支持多券商适配器 | 新券商 MUST 继承 BrokerInterface，通过 register_broker() 注册 |
| 2 | ✅ 包含 | 订单生命周期：创建 → 风控校验 → 路由 → 状态跟踪 | VALID_TRANSITIONS 严格约束，非法转换 MUST 抛异常 |
| 3 | ✅ 包含 | 算法执行：TWAP / VWAP / 冰山单 | ExecutionEngine 支持 3 种算法策略 |
| 4 | ✅ 包含 | SOR 智能路由：基于成交质量评分选择最优经纪商 | 评分机制已实现，多券商路由待扩展 |
| 5 | ✅ 包含 | 持仓快照：CTR-006 PositionSnapshot → D_RISK/D_REPORTING/D_ML_TRAIN | PositionSnapshot 数据模型产出 |
| 6 | ✅ 包含 | **v2.2.0新增** MiniQMT实盘Broker：对接xttrader API | 国金证券MiniQMT A股实盘交易(股票/ETF/可转债), 5档盘口撮合, 与D_BACKTEST matching_engine共用撮合逻辑 |
| 7 | ❌ 排除 | 订单生成 | D_PORTFOLIO_CORE 组合构建层职责 |
| 8 | ❌ 排除 | 风控校验逻辑 | D_RISK 风控层职责 |
| 9 | ❌ 排除 | 信号生成 | D_SIGNAL 信号层职责 |
| 10 | ❌ 排除 | 行情订阅 | D_DATA MiniQmtProvider(xtdata) 职责, MiniQmtBroker 仅负责交易(xttrader) |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| D_EXECUTION_CORE 属于 C 轨 hot plane | 交易时段内必须低延迟响应 |
| 当前单线程模型 | 多线程场景需加锁，当前未实现 |
| SimulationBroker 成交即时无延迟 | 真实券商有延迟，集成测试需模拟 |
| BrokerInterface 是外部系统边界 | 适配器质量直接影响交易安全 |
| **v2.2.0新增**: MiniQMT仅Windows平台 | 部署服务器必须Windows, Linux容器化需远程调用方案 |
| **v2.2.0新增**: MiniQMT必须先启动XtMiniQmt.exe终端 | xttrader依赖本地终端进程, 终端关闭则交易失败 |
| **v2.2.0新增**: A股T+1锁定 | 当日买入股票次日才能卖出, MiniQmtBroker必须在OrderManager层校验 |
| **v2.2.0新增**: A股涨跌停限制 | 涨停板无法买入, 跌停板无法卖出, MiniQmtBroker需捕获xttrader拒绝错误 |
| **v2.2.0新增**: 5档盘口撮合流动性 | 大额订单需逐档消化, 单档成交量超限需拆单 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 + 券商接入审批 | 设计+施工 | 审批权限 |
| D_PORTFOLIO_CORE 组合构建 | Order 产出正确性 | 集成 | CTR-004 契约 |
| D_RISK 风控 | 风控阻断可靠性 | 集成 | CTR-ERR-004 契约 |
| D_REPORTING 分析 | Fill/ExecutionReport 数据完整性 | 集成 | CTR-005/CTR-P1-007 契约 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 券商适配器 | 1 (SimulationBroker) | 3+ (MiniQMT/富途/IB/模拟) | 缺真实券商适配器, **MiniQMT已施工(P0已修), 富途/IB待施工** | P1 |
| 并发订单 | 1 (单线程) | 100+ | 缺多线程+锁 | P1 |
| ExecutionReport | 无 | CTR-P1-007 产出 | 缺数据模型+产出逻辑 | P0 |
| RiskValidator 解耦 | 硬编码 DefaultRiskValidator | ABC 注入 | 缺解耦 | P0 |
| **v2.2.0新增**: 回测=实盘一致性 | 共用MatchingLogic(submit_order内置pre_trade_simulate) | 共用撮合逻辑 | 已施工 | ✅ |
| **v2.2.0新增**: A股特有约束 | T+1查持仓+涨跌停校验 | MiniQmtBroker内置校验 | 已施工 | ✅ |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 正常下单 | D_PORTFOLIO_CORE 产出 CTR-004 Order | OrderManager 创建订单 → ExecutionEngine 风控校验 → SOR 路由 → BrokerInterface 下单 → Fill 回调 | CTR-005 Fill + CTR-006 PositionSnapshot |
| 风控阻断 | D_RISK 风控校验失败 | ExecutionEngine 捕获 RiskLimitViolationError → 订单状态 REJECTED | CTR-ERR-005 ExecutionRejectionError |
| 算法拆单 | 大额订单需 TWAP 执行 | ExecutionEngine 按时间窗口拆分 → 逐笔提交 → 汇总 Fill | CTR-P1-007 ExecutionReport |
| 券商不可用 | BrokerInterface 连接超时 | 重试 3 次 → 标记 EXPIRED → 降级到 SimulationBroker | CTR-ERR-005 + 告警 |
| **v2.2.0新增**: MiniQMT实盘下单 | D_PORTFOLIO_CORE产出Order + broker_id="miniqmt" | OrderManager创建订单 → ExecutionEngine风控校验 → MiniQmtBroker.submit_order → xttrader.order_stock → 成交回调 → Fill | CTR-005 Fill + CTR-006 PositionSnapshot |
| **v2.2.0新增**: A股T+1锁定拦截 | 卖出当日买入股票 | MiniQmtBroker._check_t_plus_1 → 查询持仓available_quantity → 不足 → 抛出TPlusOneViolationError | CTR-ERR-005 ExecutionRejectionError |
| **v2.2.0新增**: 涨跌停拒绝 | 涨停板买入/跌停板卖出 | MiniQmtBroker.submit_order → xttrader返回错误码 → 转换为OrderRejectedError | CTR-ERR-005 + 订单状态REJECTED |
| **v2.2.0新增**: 断线重连 | xttrader连接断开 | MiniQmtBroker._reconnect → 重新connect() → 同步订单状态 → 恢复交易 | 日志告警 + 自动恢复 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 订单执行与路由 | 接收 D_PORTFOLIO_CORE Order → 风控校验 → SOR 路由 → 券商下发 | 本模块 |
| 2 | ✅ 包含 | 算法单（TWAP/VWAP） | ExecutionEngine 实现算法拆单策略 | 本模块 |
| 3 | ✅ 包含 | 成交回报处理 | 接收 Fill → 更新持仓 → 产出 PositionSnapshot | 本模块 |
| 4 | ✅ 包含 | 持仓快照维护 | CTR-006 PositionSnapshot → D_RISK/D_REPORTING/D_ML_TRAIN | 本模块 |
| 5 | ✅ 包含 | SOR 经纪商选择 | 基于成交质量评分选择最优经纪商 | 本模块 |
| 6 | ❌ 排除 | 订单生成 | D_PORTFOLIO_CORE 组合构建层职责 | D_PORTFOLIO_CORE |
| 7 | ❌ 排除 | 风控校验逻辑 | D_RISK 风控层职责 | D_RISK |
| 8 | ❌ 排除 | 信号生成 | D_SIGNAL 信号层职责 | D_SIGNAL |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | BrokerInterface | 券商扩展点 ABC | — | 子类继承 + register_broker() 注册 |
| 2 | ExecutionEngine | 算法执行 + SOR 路由 + 风控校验 | BrokerInterface, RiskValidator | 同步调用 |
| 3 | OrderManager | 订单生命周期状态机 | — | 同步调用 |
| 4 | SimulationBroker | 模拟券商适配器 | BrokerInterface | 继承实现 |
| 5 | DefaultRiskValidator | 内嵌风控校验 | — | 同步调用（待解耦为 ABC 注入） |
| 6 | **MiniQmtBroker** (v2.2.0) | MiniQMT实盘券商适配器 | BrokerInterface, xttrader, D_DATA MiniQmtProvider(共用xtquant连接) | 继承实现 + xttrader API同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | D_PORTFOLIO_CORE (CTR-004 Order) | OrderManager 创建订单 → ExecutionEngine 风控校验 + SOR 路由 → BrokerInterface 下单 | D_REPORTING (CTR-005 Fill) | Pydantic BaseModel |
| 2 | BrokerInterface 成交回调 | ExecutionEngine 处理 Fill → 更新持仓 | D_RISK/D_REPORTING/D_ML_TRAIN (CTR-006 PositionSnapshot) | Pydantic BaseModel |
| 3 | D_RISK (CTR-ERR-004 RiskLimitViolationError) | ExecutionEngine 捕获风控硬错误 → 阻断订单 | D_PORTFOLIO_CORE/D_REPORTING (CTR-ERR-005 ExecutionRejectionError) | Exception |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| PENDING | 风控校验通过 | SUBMITTED | RiskValidator 校验通过 |
| PENDING | 风控校验失败 | REJECTED | RiskLimitViolationError 抛出 |
| SUBMITTED | 券商确认 | ACCEPTED | BrokerInterface 返回确认 |
| SUBMITTED | 券商拒绝 | REJECTED | BrokerInterface 返回拒绝 |
| ACCEPTED | 部分成交 | PARTIALLY_FILLED | Fill 数量 < 订单数量 |
| ACCEPTED | 全部成交 | FILLED | Fill 数量 = 订单数量 |
| PARTIALLY_FILLED | 全部成交 | FILLED | 累计 Fill 数量 = 订单数量 |
| PARTIALLY_FILLED | 取消剩余 | CANCELLED | 用户/系统发起取消 |
| 任意非终态 | 超时/异常 | EXPIRED | 超时阈值触发 |

> VALID_TRANSITIONS 严格约束：非法状态转换 MUST 抛出异常。

---

## §4 接口契约

> 强制 **Pydantic V2 BaseModel**（KBG-0040），禁止 `@dataclass`。

### 4.1 公共 API

| 类 | 方法 | 输入 | 输出 | 核心逻辑 |
|---|------|------|------|---------|
| BrokerInterface | `submit_order(order)` | Order | str (broker_order_id) | 券商下单抽象方法 |
| BrokerInterface | `cancel_order(broker_order_id)` | str | bool | 券商撤单抽象方法 |
| BrokerInterface | `connect()` | — | bool | 建立连接 |
| BrokerInterface | `disconnect()` | — | None | 断开连接 |
| BrokerInterface | `query_order(broker_order_id)` | str | Optional[Order] | 查询委托状态 |
| BrokerInterface | `get_positions()` | — | PositionSnapshot | 查询当前持仓 |
| ExecutionEngine | `execute_order(order, algo, broker_id)` | Order, Optional[AlgoType], str | str | 风控校验 → SOR 路由 → 券商下单 |
| ExecutionEngine | `execute_batch(orders, algo)` | list[Order], Optional[AlgoType] | list[str] | 批量执行 |
| ExecutionEngine | `register_broker(name, broker)` | str, BrokerInterface | None | 注册券商适配器 |
| ExecutionEngine | `select_broker(order)` | Order | str | SOR 智能路由 |
| OrderManager | `create_order(params)` | dict | Order | 创建订单 + 状态初始化 |
| OrderManager | `submit_order(order_id, broker_id)` | str, str | str | 提交订单到券商 |
| OrderManager | `cancel_order(order_id)` | str | bool | 撤单 |
| OrderManager | `get_order(order_id)` | str | Optional[Order] | 查询订单状态 |

### 4.2 数据模型

| 契约 ID | 模型名 | 核心字段 | 来源/目标 |
|---------|--------|---------|----------|
| CTR-004 | Order | order_id, symbol, side, quantity, price, order_type | 消费：D_PORTFOLIO_CORE |
| CTR-005 | Fill | fill_id, order_id, symbol, side, quantity, price, timestamp | 产出：D_REPORTING |
| CTR-006 | PositionSnapshot | symbol, quantity, avg_price, unrealized_pnl, timestamp | 产出：D_RISK/D_REPORTING/D_ML_TRAIN |
| CTR-ERR-005 | ExecutionRejectionError | order_id, reason, timestamp | 产出：D_PORTFOLIO_CORE/D_REPORTING |
| CTR-P1-007 | ExecutionReport | order_id, status, fills, total_quantity, avg_price | 产出：D_REPORTING |

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `execute_order()` | Order (CTR-004) | ✅ | 必须通过 D_PORTFOLIO_CORE 产出，含 idempotency_key |
| `execute_order()` | RiskValidator | ✅ | MUST 通过构造函数注入，禁止硬编码依赖 |
| `register_broker()` | name | ✅ | 非空字符串，唯一标识券商 |
| `register_broker()` | broker | ✅ | MUST 继承 BrokerInterface |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `execute_order()` | CTR-005 Fill / CTR-P1-007 ExecutionReport | CTR-ERR-005 ExecutionRejectionError |
| `submit_order()` | CTR-005 Fill | BrokerTimeoutError / BrokerConnectionError |
| `cancel_order()` | bool (True=成功) | OrderNotFoundError / CancelRejectedError |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/方法 | ✅ 向后兼容 | 不影响已有消费者 |
| 删除/重命名字段/方法 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| 新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| BrokerInterface 新增方法 | ⚠️ 需通知 | 所有适配器需实现 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | OCP-003：BrokerInterface 为唯一券商扩展点 | 新券商 MUST 继承 BrokerInterface，禁止绕开 |
| 2 | INV-007：幂等键 | 所有跨层调用携带 idempotency_key |
| 3 | CODEGEN-GUARD：CTR 声明手动维护 | CTR-declarations-manual 不可自动重生成 |
| 4 | 订单状态机：VALID_TRANSITIONS 严格约束 | 非法状态转换 MUST 抛出异常 |
| 5 | 成交回调：FillCallback 异常不阻断主流程 | try/except 包裹，记录日志 |
| 6 | **v2.2.0**: 回测=实盘一致性 | MiniQmtBroker撮合规则与D_BACKTEST matching_engine MUST共用同一份撮合逻辑(共享模块), 禁止两套实现 |
| 7 | **v2.2.0**: A股T+1锁定 | MiniQmtBroker.submit_order MUST 在下单前校验available_quantity(扣除当日买入), 违规抛TPlusOneViolationError |
| 8 | **v2.2.0**: A股涨跌停限制 | MiniQmtBroker MUST 捕获xttrader涨跌停拒绝错误码, 转换为OrderRejectedError + 订单状态REJECTED |
| 9 | **v2.2.0**: MiniQMT终端依赖 | MiniQmtBroker.connect() MUST 检测XtMiniQmt.exe进程存在, 不存在则抛BrokerConnectionError |
| 10 | **v2.2.0**: xtquant版本约束 | Python 3.6/3.7/3.8 only, 国金证券xtquant库路径固定 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 券商适配器数 | 1 (SimulationBroker) | 4 (MiniQMT/富途/IB/模拟) | 无硬限制 | ✅ | register_broker() 动态注册; **MiniQMT已施工(P0已修), 富途/IB待施工** |
| 并发订单数 | 1 (单线程) | 100+ | 取决于线程模型 | ❌ | 多线程需加锁 + ThreadPoolExecutor |
| 算法策略数 | 3 (TWAP/VWAP/冰山) | 5+ | 无硬限制 | ✅ | 策略模式扩展 |
| **v2.2.0**: MiniQMT下单延迟 | — | <200ms (P95) | xttrader TCP往返 | 待验证 | 实盘测试后埋点测量 |

### 5.3 迁移/废弃方案

> [时态:临时] 执行完毕后删除（铁律#14）。

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | DefaultRiskValidator 硬编码依赖 | `D:\ZephyrAlpha\src\zephyr\ex_core\execution_engine.py` | 构造函数注入 RiskValidator ABC | 迁移+解耦 | Grep `DefaultRiskValidator` 引用 → 改为 RiskValidator ABC |

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 订单执行成功率 | ≥99.9% | 成功订单数/总订单数 | 执行成功率 | 99.9% | 每月允许≤0.1%失败 | <99.5%告警 |
| 延迟 | 订单提交延迟(P95) | <100ms | ExecutionEngine计时 | 提交延迟 | P95<100ms | — | P95>200ms告警 |
| 可维护性 | MTTR | <30min | 故障记录 | — | — | — | — |
| 可靠性 | 订单状态一致性 | 100% | VALID_TRANSITIONS校验 | 状态转换违规数 | 0 | 0 | >0告警 |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 绕开 BrokerInterface 直接调用券商 API | 继承 BrokerInterface + register_broker() | OCP-003 扩展点约束 |
| 2 | 编码模式 | 硬编码 RiskValidator 实现 | 构造函数注入 RiskValidator ABC | 解耦约束 |
| 3 | 编码模式 | 非法订单状态转换 | VALID_TRANSITIONS 严格校验 | 状态机完整性 |
| 4 | 导入源 | `from zephyr.risk.implementations.*` | `from zephyr.risk.contracts.*` | 分层约束——D_EXECUTION_CORE 不依赖 D_RISK 实现 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 订单状态非法转换 | VALID_TRANSITIONS 校验 | 抛出 InvalidStateTransitionError，订单保持原状态 | 当前订单 |
| 2 | 风控阻断（RiskLimitViolationError） | D_RISK 风控校验 | 订单状态 → REJECTED，产出 CTR-ERR-005 | D_PORTFOLIO_CORE/D_REPORTING |
| 3 | 成交回调异常（FillCallback） | try/except 包裹 | 记录日志，不阻断主流程 | 当前成交处理 |
| 4 | 券商连接超时 | 超时阈值检测 | 重试 3 次 → 标记 EXPIRED | 当前订单 |
| 5 | 券商返回拒绝 | BrokerInterface 返回 | 订单状态 → REJECTED，产出 CTR-ERR-005 | D_PORTFOLIO_CORE/D_REPORTING |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| ex_core_orders_total | Counter | 自动埋点 | — | — |
| ex_core_orders_rejected_total | Counter | 自动埋点 | >10/min | P1 |
| ex_core_fill_latency_ms | Histogram | 自动埋点 | P95>200ms | P2 |
| ex_core_broker_score | Gauge | 手动上报 | <0.5 | P2 |
| ex_core_position_snapshot_staleness_ms | Gauge | 自动埋点 | >5000ms | P1 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| BrokerInterface (真实券商) | SimulationBroker 模拟执行 | 真实交易 | 降级到模拟模式+告警 | 券商连接恢复 |
| RiskValidator | 订单提交（无风控） | 风控校验 | 默认拒绝策略（安全优先） | RiskValidator 恢复 |
| ExecutionEngine | 订单查询/撤单 | 新订单执行 | 只读模式 | 引擎恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | BrokerInterface 外部系统边界——恶意券商适配器 | 高 | BrokerInterface ABC 强制接口约束 + 适配器沙箱测试 | 集成测试验证适配器行为 |
| 2 | 订单状态机完整性——非法状态转换 | 高 | VALID_TRANSITIONS 严格约束 + 异常抛出 | 单元测试覆盖所有转换路径 |
| 3 | 幂等键缺失——重复执行 | 中 | INV-007 强制所有跨层调用携带 idempotency_key | 门禁检查 idempotency_key 字段 |
| 4 | 成交回调异常——主流程阻断 | 中 | FillCallback try/except 包裹 + 日志记录 | 异常注入测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | OrderManager 状态机 | 所有 VALID_TRANSITIONS 路径 + 非法转换拒绝 | 覆盖率 ≥ 90% |
| 2 | 单元测试 | ExecutionEngine 算法执行 | TWAP/VWAP/冰山单拆单逻辑 | 算法输出与预期一致 |
| 3 | 单元测试 | SimulationBroker 成交处理 | 滑点 + 佣金计算 + 持仓更新 | 数值精度 ±0.01 |
| 4 | 集成测试 | D_RISK/D_PORTFOLIO_CORE/D_REPORTING 交互 | Order → 风控校验 → 执行 → Fill 产出 | 端到端通过 |
| 5 | 集成测试 | RiskValidator 解耦 | ABC 注入后风控校验正常 | 替换实现不影响执行 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-L05-001 | 必须 | CTR-004 Order | v1.0.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\portfolio-core\blueprint.md` |
| MOD-L04-001 | 必须 | CTR-ERR-004 RiskLimitViolationError | v1.0.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` |
| MOD-L07-001 | 可选 | CTR-005 Fill / CTR-P1-007 ExecutionReport 消费 | v1.0.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_reporting\blueprint.md` |
| MOD-L11-001 | 可选 | CTR-006 PositionSnapshot 消费 | v1.0.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_machine_learning_train\blueprint.md` |
| **MOD-L00-001** (v2.2.0) | 必须 | D_DATA MiniQmtProvider共用xtquant连接 | v4.0.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_data\blueprint.md` |
| **MOD-BT-001** (v2.2.0) | 必须 | D_BACKTEST matching_engine共用撮合逻辑 | v1.1.0+ | `D:\ZephyrAlpha\docs\03_modules\_domain_backtest\blueprint.md` |
| EXT-001 | 可选 | Broker API (REST / FIX 4.2+) | — | 外部系统 |
| **EXT-xttrader** (v2.2.0) | 必须 | 国金证券MiniQMT xttrader Python API | 国金证券版本 | 外部系统(随XtMiniQmt终端分发) |

### 10.2 依赖图对齐声明

| 对齐项 | 对齐状态 | 说明 |
|--------|:---:|------|
| §10.1 依赖声明 ↔ dependency_path_panorama.md §3.9 | 已对齐 | D_EXECUTION_CORE 5子模块+仿真模式+风控/合规阻断点+契约均匹配 |
| §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 未对齐 | 待验证 |
| §10.1 依赖声明 ↔ 各依赖蓝图 §4 契约 | 未对齐 | 待验证 |

### 10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| broker_interface.py | order_manager.py | Fill 回调 | 函数回调 |
| order_manager.py | execution_engine.py | Order 状态变更 | 同步调用 |
| execution_engine.py | adapters/simulation_broker.py | Order 提交 | 同步调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 模块规模小，手动维护可行 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 是 | 防止契约漂移 | CI门禁 | validate_path_alignment.py | 无 | CI | PR提交时 |
| 3 | 临时时态内容自动清理 | 否 | 迁移项少 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | 代码质量保障 | pytest+mypy+ruff | pytest | 无 | CI | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` | 本文件（含设计和施工指引） |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\ex_core\` | Python 源码 |
| 券商适配器 | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\` | 适配器实现 |
| 契约 SSoT | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\` | 契约数据模型 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\ex_core\` | 测试用例 |
| 执行拒绝错误契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\errors\execution_rejection_error.py` | 执行拒绝异常（归属 MOD-INF-016） |
| 资金分配结果契约 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\capital_allocation_result.py` | 资金分配结果（归属 MOD-INF-016） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 | 状态 |
|------------|---------|--------|---------|:---:|
| D_PORTFOLIO_CORE 组合构建 | 消费接口 | ExecutionEngine.execute_order() 接收 CTR-004 Order | 端到端 Order→Fill 测试 | 部分集成 |
| D_RISK 风控 | 依赖注入 | ExecutionEngine 构造函数注入 RiskValidator ABC | 替换实现不影响执行 | 部分集成（待解耦） |
| D_REPORTING 分析 | 产出接口 | CTR-005 Fill / CTR-P1-007 ExecutionReport | D_REPORTING 消费 Fill 数据 | 待集成 |
| D_ML_TRAIN ML 平台 | 产出接口 | CTR-006 PositionSnapshot | D_ML_TRAIN 消费 PositionSnapshot 数据 | 待集成 |
| SimulationBroker | 适配器注册 | register_broker("simulation", SimulationBroker) | 模拟成交 + 滑点 + 佣金 + 持仓维护 | ✅ 完成 |
| SOR 智能路由 | 内部逻辑 | ExecutionEngine SOR 评分机制 | 评分机制已实现，多券商路由待扩展 | 骨架就位 |
| **MiniQmtBroker** (v2.2.0) | 适配器注册 | register_broker("miniqmt", MiniQmtBroker) | 实盘小资金(1万元)100股测试: T+1/涨跌停/幂等/断线重连 | 已施工(P0已修, P1余项见审计清单) |
| **D_DATA MiniQmtProvider** (v2.2.0) | 共享xtquant连接 | MiniQmtBroker构造函数注入shared_xtquant_conn | 单点登录miniQMT终端, 避免重复connect | 已施工(P1-4 shared_xtquant_conn连接复用) |
| **D_BACKTEST matching_engine** (v2.2.0) | 共享撮合逻辑 | MatchingLogic共享模块(从matching_engine抽取) | 回测=实盘撮合行为一致性测试 | 已施工(submit_order内置pre_trade_simulate) |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | ~~l06_trade_execution.yaml~~ | 已删除（迁移至35域架构） | — | 旧14层架构YAML已废弃 |
| 2 | blueprint_registry.yaml | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress 更新为 phase_1_partial | 进度同步 |
| 3 | cross_layer_contracts.yaml | `D:\ZephyrAlpha\src\zephyr\shared\contracts\cross_layer_contracts.yaml` | 确认 CTR-005/CTR-006/CTR-ERR-005/CTR-P1-007 状态 | 契约状态同步 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | ExecutionEngine 直接依赖 DefaultRiskValidator | 高 | 中 | 改为依赖 RiskValidator ABC，通过构造函数注入解耦 | 风险 |
| 2 | YAML 文件路径与磁盘不一致 | 高 | 低 | 以磁盘为准，YAML 待同步 | 风险 |
| 3 | SimulationBroker 成交即时无延迟 | 中 | 中 | 真实券商有延迟，需在集成测试中模拟 | 风险 |
| 4 | 订单状态机并发安全 | 中 | 高 | 当前单线程，多线程需加锁 | 风险 |
| 5 | D_REPORTING/D_RISK/D_ML_TRAIN 依赖本层产出（CTR-005/CTR-006） | — | 中 | 契约版本管理 + 变更通知 | 负面后果 |
| 6 | BrokerInterface 适配器质量影响交易安全 | — | 高 | 适配器沙箱测试 + ABC 接口约束 | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§10 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 4 | GOV-DOC-002 防幻觉路径映射已理解 | 能回答"某类文件该放哪" | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4 个 Phase |
| 施工模式 | 扩展（解耦 + 新增产出） |
| 核心风险 | RiskValidator 解耦可能影响现有 ExecutionEngine 行为 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板v4.1合规） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | D_PORTFOLIO_CORE CTR-004 Order 契约已定义 | hard | ✅ | ✅ |
| 2 | D_RISK CTR-ERR-004 RiskLimitViolationError 契约已定义 | hard | ✅ | ✅ |
| 3 | BrokerInterface (OCP-003) 已实现 | hard | ✅ | ✅ |
| 4 | OrderManager 状态机已实现 | hard | ✅ | ✅ |

### 16.3 实施步骤

#### 步骤 1：BrokerInterface (OCP-003) 定义

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 BrokerInterface |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\trading\trading_contracts\broker_interface.py` |
| 验收标准 | BrokerInterface ABC 定义完整，submit_order/cancel_order 抽象方法 |
| 验证命令 | `python -m pytest tests/ -k broker_interface -v` |
| G7 检查项 | 上游 D_PORTFOLIO_CORE Order 引用正确？下游 D_REPORTING Fill 产出路径精确？ |
| AI 自治范围 | human_gated——BrokerInterface 是 OCP-003 扩展点，修改需 Owner 审批 |
| 检查点 | broker_interface.py 存在且非空 |

**状态**：✅ 完成

#### 步骤 2：OrderManager 订单生命周期状态机

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.3 状态生命周期 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ex_core\order_manager.py` |
| 验收标准 | VALID_TRANSITIONS 全部实现，非法转换抛异常 |
| 验证命令 | `python -m pytest tests/ -k order_manager -v` |
| G7 检查项 | 所有状态转换路径覆盖？非法转换异常正确？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | order_manager.py 存在且非空 |

**状态**：✅ 完成

#### 步骤 3：ExecutionEngine 算法执行 + SOR

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 ExecutionEngine |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ex_core\execution_engine.py` |
| 验收标准 | TWAP/VWAP/冰山单算法实现，SOR 评分机制实现 |
| 验证命令 | `python -m pytest tests/ -k execution_engine -v` |
| G7 检查项 | 算法输出正确？SOR 路由逻辑正确？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | execution_engine.py 存在且非空 |

**状态**：✅ 完成

#### 步骤 4：SimulationBroker 模拟券商

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 BrokerInterface 子类 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\simulation_broker.py` |
| 验收标准 | 模拟成交 + 滑点 + 佣金 + 持仓维护 |
| 验证命令 | `python -m pytest tests/ -k simulation_broker -v` |
| G7 检查项 | 滑点计算正确？佣金计算正确？持仓更新正确？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | simulation_broker.py 存在且非空 |

**状态**：✅ 完成

#### 步骤 5：RiskValidator 依赖解耦（ABC 注入）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 ExecutionEngine 构造函数注入 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ex_core\execution_engine.py` |
| 验收标准 | ExecutionEngine 接受 RiskValidator ABC 注入，DefaultRiskValidator 作为默认实现 |
| 验证命令 | `python -m pytest tests/ -k risk_validator -v` |
| G7 检查项 | 解耦后现有行为不变？ABC 接口完整？回滚方案可执行？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | RiskValidator ABC 定义 + ExecutionEngine 构造函数接受注入 |

**状态**：待实现

#### 步骤 6：CTR-P1-007 ExecutionReport 产出

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.2 数据模型 ExecutionReport |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\execution_report.py` |
| 验收标准 | ExecutionReport 数据模型定义 + ExecutionEngine 产出逻辑 |
| 验证命令 | `python -m pytest tests/ -k execution_report -v` |
| G7 检查项 | 数据模型字段完整？D_REPORTING 消费路径正确？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | execution_report.py 存在且非空 |

**状态**：待实现

#### 步骤 7：真实券商适配器（富途/IB）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 BrokerInterface 子类 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\` |
| 验收标准 | 继承 BrokerInterface，实现 submit_order/cancel_order |
| 验证命令 | `python -m pytest tests/ -k broker_adapter -v` |
| G7 检查项 | 适配器接口完整？外部 API 调用正确？ |
| AI 自治范围 | human_gated——真实券商接入需 Owner 审批 |
| 检查点 | 适配器文件存在且非空 |

**状态**：待实现

#### 步骤 7.5：MiniQMT实盘Broker适配器（v2.2.0新增）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 BrokerInterface 子类 + §16.7.1 MiniQmtBroker详细规格 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\miniqmt_broker.py` |
| 验收标准 | (a) 继承BrokerInterface, 实现submit_order/cancel_order/connect/disconnect/query_order/get_positions; (b) 对接xttrader API(order_stock/cancel_order_stock/query_stock_orders/query_stock_positions); (c) T+1锁定校验; (d) 涨跌停错误码捕获; (e) 幂等键(idempotency_key); (f) 断线重连; (g) 与D_BACKTEST matching_engine共用撮合逻辑(共享MatchingLogic模块) |
| 验证命令 | `python -m pytest tests/unit/ex_core/test_miniqmt_broker.py -v` (Mock xttrader) + 实盘小资金验证(100股测试) |
| G7 检查项 | (1) xttrader API调用正确? (2) T+1校验逻辑正确? (3) 涨跌停错误码映射完整? (4) 与matching_engine共用撮合逻辑(非复制粘贴)? (5) 断线重连后状态同步正确? (6) 与D_DATA MiniQmtProvider共用xtquant连接(非重复connect)? |
| AI 自治范围 | human_gated——实盘交易接入需Owner审批 + 小资金(1万元)灰度验证 |
| 检查点 | miniqmt_broker.py 存在且非空 + 单元测试通过 + Mock集成测试通过 |

**状态**：已施工(P0已修, P1余项见审计清单)

> **回测=实盘一致性约束**: MiniQmtBroker的撮合逻辑MUST从`backtest/core/matching_engine.py`抽取的共享MatchingLogic模块调用, 禁止在MiniQmtBroker内重新实现撮合规则。这保证回测与实盘的撮合行为完全一致(回测-实盘偏差监控>30%告警/>50%退役的基线)。

#### 步骤 8：与 D_RISK/D_REPORTING 集成测试

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §12 集成目标 |
| 产出位置 | `D:\ZephyrAlpha\tests\unit\ex_core\` |
| 验收标准 | D_RISK 风控 + D_REPORTING 分析端到端测试通过 |
| 验证命令 | `python -m pytest tests/ -k integration -v` |
| G7 检查项 | D_RISK 风控阻断正确？D_REPORTING Fill 消费正确？ |
| AI 自治范围 | ai_modifiable |
| 检查点 | 集成测试通过 |

**状态**：待实现

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 5 | RiskValidator 解耦后行为变化 | 恢复 DefaultRiskValidator 硬编码，回退 execution_engine.py |
| 6 | ExecutionReport 产出异常 | 移除 ExecutionReport 产出逻辑，回退到仅 Fill 产出 |
| 7 | 真实券商适配器连接失败 | 移除适配器注册，回退到 SimulationBroker |
| 8 | 集成测试失败 | 逐模块排查，回退到上一个通过状态 |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | broker_interface.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 2 | execution_engine.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 3 | order_manager.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 4 | simulation_broker.py 存在 | `ls` exit 0 | 完成 | ✅ |
| 5 | SLO 已定义且可测量 | §5.4 每项 SLI 有测量方式 | 就绪 | ☐ |
| 6 | 监控指标已埋点 | §6.1 每项指标有采集实现 | 就绪 | ☐ |
| 7 | 退化策略已实现 | §6.2 每个组件有降级逻辑 | 就绪 | ☐ |
| 8 | 回滚方案已验证 | §16.4 回滚操作可执行 | 就绪 | ☐ |
| 9 | 集成测试已通过 | §12 每个集成点有测试 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | in_progress | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | yes | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | 订单状态机转换规则 | 算法 | PENDING→{SUBMITTED,CANCELLED}; SUBMITTED→{PARTIAL,FILLED,CANCELLED,REJECTED}; PARTIAL→{FILLED,CANCELLED,REJECTED}; FILLED/CANCELLED/REJECTED→∅ | `order_manager.py` |
| 2 | SOR 评分衰减公式 | 算法 | `score = current * 0.9 + fill_quality * 0.1` | `execution_engine.py` |
| 3 | 滑点计算 | 算法 | BUY: `fill_price = price * (1 + slippage_bps/10000)`; SELL: `fill_price = price * (1 - slippage_bps/10000)` | `simulation_broker.py` |
| 4 | **MiniQmtBroker撮合逻辑(v2.2.0)** | 协议 | 实盘撮合MUST调用D_BACKTEST matching_engine抽取的共享MatchingLogic模块(回测=实盘一致性), 禁止在本适配器内重新实现撮合规则 | `adapters/miniqmt_broker.py`(已施工: submit_order内置pre_trade_simulate预校验) |

### §16.7.1 MiniQmtBroker 详细规格（v2.2.0新增）

> **真源声明**：本规格是 MiniQMT 实盘 Broker 适配器的唯一真源。代码实现 MUST 严格遵循本规格。

#### A. 适配器元数据

| 字段 | 值 | 说明 |
|------|-----|------|
| broker_id | "miniqmt" | register_broker("miniqmt", MiniQmtBroker) |
| broker_name | "国金证券MiniQMT实盘" | 显示名称 |
| supports_realtime | True | 实盘交易 |
| asset_classes | ["stock", "etf", "convertible_bond"] | A股股票/ETF/可转债 |
| market | "A_SHARE" | A股市场 |
| t_plus | 1 | T+1锁定 |
| price_limits | True | 涨跌停限制(主板±10%/创业板±20%/ST±5%) |
| min_order_qty | 100 | A股最小1手=100股 |
| price_tick | 0.01 | 最小价格变动单位 |

#### B. xttrader API 映射表

| BrokerInterface 方法 | xttrader API | 说明 |
|---------------------|-------------|------|
| connect() | XtQuantTrader.connect() + 创建XtQuantTrader(path, session_id) | 建立TCP连接, 必须先启动XtMiniQmt.exe终端 |
| disconnect() | XtQuantTrader.stop() | 断开连接 |
| submit_order(order) | XtQuantTrader.order_stock(account, stock_code, order_type, volume, price_type, price, strategy_name, order_remark) | 下单, order_remark存idempotency_key |
| cancel_order(broker_order_id) | XtQuantTrader.cancel_order_stock(account, account_id, order_id) | 撤单 |
| query_order(broker_order_id) | XtQuantTrader.query_stock_orders(account) → 过滤order_id | 查询委托状态 |
| get_positions() | XtQuantTrader.query_stock_positions(account) → 转换为PositionSnapshot | 查询持仓 |
| — (回调) | XtQuantTrader.register_callback(MiniQmtCallback) | 注册成交回调, on_stock_order/on_stock_trade |

#### C. xttrader 错误码映射

| xttrader错误码 | 含义 | MiniQmtBroker处理 |
|---------------|------|------------------|
| 0 | 成功 | 返回broker_order_id |
| -1 | 连接失败 | 抛BrokerConnectionError |
| -2 | 未就绪 | 重试3次后抛BrokerNotReadyError |
| -3 | 订单号重复 | 幂等键冲突, 抛DuplicateOrderError |
| 50 | 涨停限制 | 抛OrderRejectedError(reason="涨停限制") |
| 51 | 跌停限制 | 抛OrderRejectedError(reason="跌停限制") |
| 52 | 委托数量不合法(非100股整数倍) | 抛InvalidOrderQuantityError |
| 53 | 委托价格不合法(超出涨跌停范围) | 抛InvalidOrderPriceError |
| 54 | 资金不足 | 抛InsufficientFundsError |
| 55 | 持仓不足(T+1或无持仓) | 抛InsufficientPositionError, 区分T+1 vs 真无持仓 |

#### D. MiniQmtBroker 类规格

```python
class MiniQmtBroker(BrokerInterface):
    """MiniQMT实盘券商适配器(v2.2.0)
    
    对接国金证券MiniQMT的xttrader API, 支持A股实盘交易(股票/ETF/可转债)。
    与D_BACKTEST matching_engine共用撮合逻辑(回测=实盘一致性)。
    与D_DATA MiniQmtProvider共用xtquant连接(单点登录miniQMT终端)。
    """
    
    def __init__(self, path: str, session_id: int, account: str, 
                 shared_xtquant_conn=None, matching_logic=None):
        """
        Args:
            path: XtMiniQmt.exe数据目录路径
            session_id: 会话ID(整数, 用于xttrader连接标识)
            account: 资金账号
            shared_xtquant_conn: 共享的xtquant连接(与D_DATA MiniQmtProvider共用, 避免重复connect)
            matching_logic: 共享撮合逻辑模块(从D_BACKTEST matching_engine抽取), MUST为MatchingLogic实例
        """
        ...
    
    def connect(self) -> bool:
        """连接miniQMT终端. MUST检测XtMiniQmt.exe进程存在."""
        ...
    
    def submit_order(self, order: Order) -> str:
        """下单. 
        Pre-checks: (1) T+1锁定校验(卖出时); (2) 涨跌停校验; (3) 幂等键校验.
        撮合逻辑: 调用self._matching_logic.match(order, order_book) (共享模块).
        """
        ...
    
    def _check_t_plus_1(self, order: Order) -> None:
        """T+1锁定校验. 查询available_quantity(扣除当日买入), 不足则抛TPlusOneViolationError."""
        ...
    
    def _check_price_limit(self, order: Order) -> None:
        """涨跌停校验. 查询当前最新价±涨跌停范围, 超出则抛OrderRejectedError."""
        ...
    
    def _reconnect(self) -> bool:
        """断线重连. 重新connect() + 同步订单状态(查询所有未完成订单) + 恢复交易."""
        ...
```

#### E. 共享撮合逻辑抽取方案（回测=实盘一致性）

**问题**: D_BACKTEST `matching_engine.py` 和 D_EX_CORE `miniqmt_broker.py` 各自实现撮合规则会导致行为不一致, 违反"回测=实盘一致性"约束。

**方案**: 从 `backtest/core/matching_engine.py` 抽取纯撮合逻辑为独立模块 `backtest/core/matching_logic.py`, 同时被 matching_engine(回测) 和 MiniQmtBroker(实盘) 调用。

```
backtest/core/matching_logic.py (新建, 共享撮合逻辑)
├── class MatchingLogic:
│   ├── match_market_order(order, order_book) → Fill  # 市价单撮合
│   ├── match_limit_order(order, order_book) → Fill   # 限价单撮合
│   ├── match_tick_order(order, tick_data) → Fill     # Tick级5档撮合(实盘+回测共用)
│   └── _apply_slippage(price, side, slippage_bps) → float  # 滑点
│
backtest/core/matching_engine.py (重构, 仅保留回测编排逻辑)
├── class MatchingEngine:
│   └── self._logic = MatchingLogic()  # 委托共享逻辑
│
ex_core/adapters/miniqmt_broker.py (新建, 实盘Broker)
├── class MiniQmtBroker(BrokerInterface):
│   └── self._matching_logic = MatchingLogic()  # 委托共享逻辑
```

> **约束**: MatchingLogic MUST为纯函数式实现(无副作用, 无状态), 输入(order, order_book/tick_data)输出(Fill), 禁止访问外部状态。这保证回测与实盘的撮合行为完全一致。

#### F. 与D_DATA/D_BACKTEST/D_FRONTEND协同

| 协同方 | 协同点 | 协同方式 |
|-------|-------|---------|
| D_DATA MiniQmtProvider | 共用xtquant连接 | MiniQmtBroker构造函数注入shared_xtquant_conn, 避免重复connect到miniQMT终端 |
| D_BACKTEST matching_engine | 共用撮合逻辑 | 共享MatchingLogic模块(见§16.7.1 E), 回测=实盘一致性 |
| D_BACKTEST tick_replay | Tick回放驱动实盘模拟 | tick_replay可驱动MiniQmtBroker做"实盘模拟"(用历史Tick数据驱动真实下单逻辑, 但不实际成交) |
| D_FRONTEND trade_panel | 实盘交易面板 | D_FRONTEND调用ExecutionEngine.execute_order(order, broker_id="miniqmt")触发实盘下单 |
| D_FRONTEND position_monitor | 实盘持仓监控 | D_FRONTEND调用MiniQmtBroker.get_positions()实时展示持仓 |

#### G. 部署约束

| 约束 | 说明 |
|------|------|
| 操作系统 | Windows only (miniQMT终端仅Windows) |
| Python版本 | 3.6/3.7/3.8 (xtquant库兼容性, 国金证券文档) |
| XtMiniQmt.exe | MUST先启动并登录, MiniQmtBroker.connect()检测进程存在 |
| xtquant库路径 | 国金证券安装目录下的site-packages, 需手动拷贝到Python环境或sys.path.insert |
| 资金账号 | 必须已开通A股交易权限, 国金证券10万门槛已满足 |
| 实盘灰度 | 首次部署MUST用小资金(1万元)做100股测试, 验证成交回报/持仓更新/T+1校验正确后再放量 |

#### H. 已知限制

| 限制 | 影响 | 缓解方案 |
|------|------|---------|
| 仅支持A股(股票/ETF/可转债) | 期货/期权需另接CTP | 未来新增ctp_broker.py适配器 |
| 仅Windows | Linux服务器无法直接部署 | 方案1: Windows服务器; 方案2: Linux容器通过gRPC调用Windows侧MiniQmtBroker |
| Level-1行情(5档盘口) | 大额订单撮合精度低于Level-2 | 当前做T足够, 未来开通Level-2后升级MatchingLogic |
| xttrader非线程安全 | 多线程并发下单需加锁 | MiniQmtBroker内置threading.Lock保护所有xttrader调用 |
| 实盘延迟未验证 | 回测=实盘偏差待实测 | 上线后埋点测量P95延迟, 监控回测-实盘偏差(>30%告警/>50%退役) |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/ -v` | 运行 D_EXECUTION_CORE 全部测试 | — | exit 0 = 通过 |
| 2 | 配置 | `ExecutionConfig` → `default_algo` | 默认算法策略 | `AlgoType`: TWAP/VWAP/MARKET | 默认 TWAP |
| 3 | 配置 | `ExecutionConfig` → `twap_window_minutes` | TWAP 时间窗口 | `int`: 分钟 | 默认 30 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | RiskValidator 解耦失败 | 解耦后测试不通过 | 逐用例排查差异 | 恢复硬编码 | pytest exit 0 |
| 2 | 运行 | 券商连接超时 | BrokerInterface 超时 | 检查网络+重试3次 | 标记EXPIRED | 降级到SimulationBroker |
| 3 | 运行 | 风控阻断异常 | RiskLimitViolationError | 检查D_RISK风控规则 | 订单REJECTED | 人工review |
| 4 | 运行 | 紧急冻结 | 安全事件 | 冻结写入+只读 | — | 威胁解除 |
| 5 | 运行 | 紧急旁路 | 模块阻塞 | 降级到SimulationBroker | — | 模块恢复 |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同一订单并发状态变更 | OrderManager 内部锁 | 后写者重试 | 最后写入胜出 |
| 同一券商并发下单 | BrokerInterface 队列 | FIFO 排队 | 按提交顺序 |
| 多 AI Session 同时注册券商 | register_broker() 原子操作 | 后注册覆盖 | 最后注册胜出 |

> 当前单线程模型，并发场景为未来扩展预留。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 券商适配器数 | 1 | `len(_brokers)` |
| 算法策略数 | 3 | ExecutionEngine 策略注册数 |
| 并发订单处理 | 1 (单线程) | 线程模型 |
| 订单状态数 | 7 | OrderStatus 枚举值数 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L06-001 | 单线程订单处理 | 多线程 + 锁 + ThreadPoolExecutor | P1 | 并发订单 > 10 | v2.1.0 | 待施工 |
| GAP-L06-002 | 仅 SimulationBroker | 新增MiniQMT/富途/IB 适配器 | P1 | 需要实盘交易 | v2.2.0 | **MiniQMT已施工(P0已修), 富途/IB待施工** |
| GAP-L06-003 | 无 ExecutionReport | 新增 CTR-P1-007 产出 | P0 | D_REPORTING 需要执行报告 | v2.0.1 | 待施工 |
| **GAP-L06-004** (v2.2.0) | 回测≠实盘(撮合逻辑各实现一套) | 抽取MatchingLogic共享模块 | P0 | 回测-实盘偏差>30% | v2.2.0 | 已施工(submit_order内置pre_trade_simulate, MatchingLogic共享) |
| **GAP-L06-005** (v2.2.0) | 无A股T+1/涨跌停校验 | MiniQmtBroker内置校验 | P0 | 实盘接入 | v2.2.0 | 已施工(T+1查持仓available_quantity, 涨跌停基于prev_close) |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | BrokerInterface + ExecutionEngine + OrderManager + SimulationBroker | ⚠️ |
| v2.0.0 | 2 | 模板v3.3重构 | 章节重排+新增概述+标准锚点+§0版本映射更新 | ⚠️ |
| v2.1.0 | 2 | 模板v4.1合规 | 回填缺失章节+压缩+依赖图对齐 | ⚠️ |
| v2.2.0 | 2 | MiniQMT Broker规划 | 新增MiniQmtBroker适配器规格(§16.7.1)+回测=实盘一致性约束+MatchingLogic共享模块抽取方案 | ✅(P0已修, P1余项见审计清单) |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| RiskValidator ABC | GAP-L06-001 | execution_engine.py | Phase 2 | 待施工 |
| ExecutionReport | GAP-L06-003 | execution_report.py | Phase 2 | 待施工 |
| **MiniQmtBroker** | GAP-L06-002/005 | adapters/miniqmt_broker.py | Phase 1.5 | 已施工(P0已修, P1余项见审计清单) |
| **MatchingLogic共享模块** | GAP-L06-004 | backtest/core/matching_logic.py | Phase 1.5 | 已施工(submit_order内置pre_trade_simulate) |
| 富途/IB 适配器 | GAP-L06-002 | adapters/futu_broker.py | Phase 3 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L06-01 | 券商扩展点设计 | A: 硬编码 / B: ABC+注册模式 | B | OCP-003 开闭原则，新券商不需修改现有代码 | 2026-05-05 |
| 2 | D-L06-02 | 订单状态机设计 | A: 自由状态 / B: VALID_TRANSITIONS 严格约束 | B | 防止非法状态转换导致交易事故 | 2026-05-05 |
| 3 | D-L06-03 | SOR 评分机制 | A: 静态权重 / B: 动态衰减评分 | B | 基于成交质量自适应调整，更贴近实际 | 2026-05-05 |
| 4 | D-L06-04 | 模板v4.1升级 | A: 保持v3.3 / B: 按v4.1升级 | B | v4.1模板合规；§0前移+§7/§15删除+§10拆分+铁律扩展 | 2026-05-15 |
| 5 | D-L06-05 | 回测-实盘一致性架构选型 | A: 顶级机构做法(同一份代码+feature flag) / B: MatchingLogic共享模块(撮合逻辑共享) / C: 完全分离(回测一套实盘一套) | B | A需"团队规模+C++低延迟事件循环+独立SimBroker+SRE对账"四件套支撑，个人开发者用不起；xttrader非线程安全+同步阻塞+回调驱动，强行统一事件循环会让回测慢3-10倍；A股T+1/涨跌停硬校验会反向污染回测逻辑(需模拟xttrader错误码行为)；C是回测-实盘偏差>30%告警根源；B消除>80%偏差源(撮合规则一致)且保留回测/实盘各自优化空间，是个人开发者匹配资源的最优解而非妥协。详见 §16.7.1-E MatchingLogic共享模块抽取方案 | 2026-07-04 |
| 6 | D-L06-06 | 顶级机构一致性升级触发条件 | A: 永不升级 / B: 3信号同时出现时升级(模拟实盘环境) / C: 立即升级 | B | 3升级信号：①MatchingLogic共享上线后回测-实盘偏差仍>5%且定位不到原因 ②策略迭代速度成为瓶颈(每次改策略要改两套代码) ③有"模拟实盘环境"需求(历史Tick回放驱动MiniQmtBroker实盘代码)；B是轻量升级路径(在MatchingLogic共享基础上加ReplayMode，不推翻现有架构)，v2.3+考虑；C在MiniQMT Provider/Broker/Tick回放5组件未施工前是空中楼阁 | 2026-07-04 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| SOR | Smart Order Router——基于成交质量评分选择最优经纪商 | 路由 | SOR 特指券商选择路由，非网络路由 |
| OCP-003 | BrokerInterface 扩展点——新券商通过继承+注册接入 | 适配器 | OCP-003 是扩展点定义，适配器是实现 |
| Fill | 成交回报——订单被券商执行后的确认记录 | Order | Order 是委托指令，Fill 是执行结果 |
| PositionSnapshot | 持仓快照——某时刻的持仓状态 | Portfolio | PositionSnapshot 是 D_EXECUTION_CORE 产出，Portfolio 是 D_PORTFOLIO_CORE 管理 |
| TWAP | Time-Weighted Average Price——按时间均分下单 | VWAP | TWAP 按时间均分，VWAP 按成交量加权 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | DefaultRiskValidator 硬编码 | 高 | 初始实现未考虑解耦 | 步骤5 RiskValidator ABC 注入 | §5.1 #2 | 待解决 |
| 2 | YAML SSoT 路径与磁盘不一致 | 中 | adapters/ 子目录未同步 | §13 #1 更新 YAML | §0.1 | 待解决 |
| 3 | 无 ExecutionReport 产出 | 高 | CTR-P1-007 未实现 | 步骤6 实现 | §4.2 | 待解决 |
| 4 | 订单状态机缺 EXPIRED 状态 | 中 | 代码中 VALID_TRANSITIONS 无 EXPIRED | 步骤5 补充 | §3.3 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ✅ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | RiskValidator 解耦后升级 | BrokerInterface OCP-003 已验证 |
| 接口契约 | evolving | 中 | CTR-P1-007 实现后升级 | ExecutionReport 待实现 |
| 数据模型 | stable | 高 | 新增契约模型后升级 | CTR-004/005/006 已实现 |
| 施工步骤 | evolving | 中 | 步骤5-8完成后升级 | 4/8 步骤已完成 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v1.0.0 | BrokerInterface + ExecutionEngine + OrderManager + SimulationBroker | — | 已完成 |
| v2.0.0 | 模板v3.3重构 | v1.0.0 | 已完成 |
| v2.1.0 | 模板v4.1合规+回填+压缩+对齐 | v2.0.0 | 已完成 |
| v2.2.0 | RiskValidator ABC 解耦 + ExecutionReport | v2.1.0 | 待施工 |
| v3.0.0 | 多线程 + 真实券商适配器 | v2.2.0 | 待施工 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略——即使与前序文档重复也必须完整列出 | 关键信息缺失 |
| 3 | 蓝图必须是最终设计结果——不记录决策过程、不保存未选方案 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含——关键信息不能只写"详见XX" | 上下文缺失 |
| 10 | 删除文件必须遵守安全删除协议——禁止直接删除任何文件 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 蓝图与代码漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责混淆 |
| 16 | 术语表不可省略——每个蓝图 MUST 包含术语表 | 术语理解漂移 |
| 17 | 参考实现规格 vs 已实现代码重复——接口契约无法表达的逻辑规格 MUST 保留在 §16.7 | 关键逻辑实现错误 |
| 18 | 对标验证表格 vs 对标散文——结构化对标表格保留，散文删除 | 噪音淹没信息 |
| 19 | SLO 必须定义——§5.4 服务水平目标不可省略 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略——§6.1 可观测性规格不可省略 | 故障无法发现 |
| 21 | 退化矩阵必须声明——§6.2 退化矩阵不可省略 | 部分失败时行为不可预测 |

---

## 蓝图拆分判定标准

### 判定流程

| 步骤 | 判定问题 | 判定结果 | 行动 |
|------|---------|---------|------|
| 1 | 拟新增/修改的内容与当前蓝图的职责是否相同？ | 相同 → 继续；不同 → 步骤 2 | 职责相同→原地升级 |
| 2 | 不同职责的内容是否有独立的上游/下游依赖链？ | 有 → 步骤 3；无 → 原地升级 | 无独立依赖→原地升级 |
| 3 | 拆分后两个蓝图是否各自自包含（接口/依赖/施工）？ | 是 → 拆分；否 → 原地升级 | 自包含→拆分独立蓝图 |

### 判定示例

| 场景 | 职责相同？ | 独立依赖链？ | 各自自包含？ | 判定 |
|------|:---:|:---:|:---:|------|
| D_EXECUTION_CORE 新增 TWAP 算法策略 | ✅ 相同 | — | — | 原地升级（同属交易执行） |
| D_EXECUTION_CORE 新增回测引擎 | ❌ 不同 | ✅ 有 | ✅ 是 | 拆分独立蓝图（回测≠执行） |
| D_EXECUTION_CORE 新增风控计算逻辑 | ❌ 不同 | ✅ 有 | ✅ 是 | 拆分独立蓝图（D_RISK 已覆盖） |

---

## ⚠️ 安全删除协议

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| — | 无 | — | — | — | 本蓝图不涉及文件废弃/迁移/删除（§5.3 迁移项为代码重构，非文件删除） |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持1个Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表、frontmatter模板 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 涌现式设计 + MTH-013 路径合规创建 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 本蓝图 | — | — | `D:\ZephyrAlpha\docs\03_modules\_domain_execution_core\blueprint.md` | 本蓝图即SSoT |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| — | 无 | — | — | D_EXECUTION_CORE 是唯一交易执行层，无重叠模块 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | broker_interface.py | `D:\ZephyrAlpha\src\zephyr\trading\trading_contracts\broker_interface.py` | 修改 | RiskValidator ABC 注入解耦 |
| 2 | execution_engine.py | `D:\ZephyrAlpha\src\zephyr\ex_core\execution_engine.py` | 修改 | ExecutionReport 产出 + RiskValidator 解耦 |
| 3 | order_manager.py | `D:\ZephyrAlpha\src\zephyr\ex_core\order_manager.py` | 读取 | 订单状态机参考 |
| 4 | adapters/simulation_broker.py | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\simulation_broker.py` | 读取 | 模拟券商参考 |
| 5 | adapters/__init__.py | `D:\ZephyrAlpha\src\zephyr\ex_core\adapters\__init__.py` | 修改 | 新增适配器注册 |
| 6 | __init__.py | `D:\ZephyrAlpha\src\zephyr\ex_core\__init__.py` | 修改 | CTR 声明更新 |
| 7 | 契约目录 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\execution\` | 修改 | CTR-P1-007 ExecutionReport 新增 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| D_EXECUTION_CORE 架构设计 | **本文档 §1-§10** | 旧版占位蓝图 |
| D_EXECUTION_CORE 施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| D_EXECUTION_CORE 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_reporting\blueprint.md` | §4 接口契约（CTR-005 Fill, CTR-P1-007 ExecutionReport） |
| Tier 1 | `D:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` | §4 接口契约（CTR-006 PositionSnapshot） |
| Tier 2 | `D:\ZephyrAlpha\docs\03_modules\_domain_machine_learning_train\blueprint.md` | §4 接口契约（CTR-006 PositionSnapshot） |
| Tier 3 | `D:\ZephyrAlpha\src\zephyr\ex_core\` | §4 数据模型、§11 产出物路径 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步 | Tier 2 同步 |
|---------|---------|-----------|-----------|
| 接口契约新增/修改（§4） | 需 Owner 审批 + 通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需 Owner 审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需 §0 对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 | — | — |
| 容量升级方案新增（§17） | 需 Owner 审批 | 下游评估影响 | 更新容量预算 |
