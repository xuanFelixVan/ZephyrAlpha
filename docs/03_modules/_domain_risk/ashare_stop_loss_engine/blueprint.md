---
module_id: MOD-RK-09
title: "A股止损规则引擎蓝图 — 6种止损模式 + 亏损限额三级"
doc_type: blueprint
status: Active
version: "0.1.1"
ttl: permanent
layer: L02_risk
layer_name: risk
functional_domain: risk
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: stable
---

# MOD-RK-09 A-Share Stop-Loss Rule Engine — A股止损规则引擎 蓝图

> **module_id**: MOD-RK-09 | **域**: D_RISK | **层**: L02 盘中实时监控
> **优先级**: P0 | **成熟度**: production | **对标能力**: C-004●
> **SSoT**: depgraph MOD-RK-09 | **设计真源**: D:\临时工作区\依赖图\11-D-RISK-风控域.md §1.2 RK-09, §6 决策记录(亏损限额三级), §1.4 INV-003

## 1. 定位

A股止损规则引擎——A股特色止损规则检测, 产出止损信号交由 RK-04 Stop Loss Engine 执行:
- 6种A股止损模式 (A股T+1制度+行为金融学特色)
- 亏损限额三级 (INV-003: 日2%/周5%/月10% + 强制停盘1-3天)
- 强制停盘 + 强制复盘

与 RK-04 的边界: RK-04 是通用止损执行引擎(fixed/trailing/ATR/time), RK-09 是 A股规则检测层, 产出 StopLossSignal 由 RK-04 消费执行。RK-09 不直接执行止损动作。

属 A 类基础设施(规则检测 + 阈值判定, 逻辑明确), 阈值为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 持仓(entry/current)+市场数据(support/vwap/sector)+竞价+亏损率 | — |
| 输出 | StopLossSignal[] / LossLimitAlert | → RK-04 执行, RK-03 告警 |
| 依赖 | RK-04 Stop Loss Engine (执行止损) | L1 依赖先行 |

## 3. 核心规则 (设计真源 §1.2 RK-09, §6, §1.4 INV-003)

### 3.1 6种A股止损模式

| 模式 | 触发条件 | 严重级别 |
|------|---------|---------|
| 1. 固定比例-7% | 持仓亏损 >= 7% (FIXED_PCT) | CRITICAL |
| 2. 关键支撑破位 | 价格 < 支撑位 (SUPPORT_BREAK) | CRITICAL |
| 3. 逻辑失效 | 买入逻辑不再成立 (LOGIC_INVALIDATION) | WARNING |
| 4. 竞价不及预期 | 开盘价低于预期 >= 2% (AUCTION_DISAPPOINT) | WARNING |
| 5. 分时破位 | 跌破分时均线/前低 >= 1% (INTRADAY_BREAK) | WARNING |
| 6. 板块退潮 | 板块动量 <= -2% (SECTOR_EBB) | WARNING |

### 3.2 亏损限额三级 (INV-003)

| 级别 | 限额 | 强制停盘天数 | 严重级别 |
|------|------|------------|---------|
| DAILY | 日亏 >= 2% | 1 天 | CRITICAL |
| WEEKLY | 周亏 >= 5% | 2 天 | CRITICAL |
| MONTHLY | 月亏 >= 10% | 3 天 | EMERGENCY |

- 三级递进: 取最高触发级别 (MONTHLY > WEEKLY > DAILY)
- 限额递增: 日(2%) < 周(5%) < 月(10%)
- 停盘天数递增: 日(1) <= 周(2) <= 月(3)

### 3.3 多模式同时触发

- 6种模式独立检测, 可同时触发多个
- 返回信号列表按严重级别降序 (EMERGENCY > CRITICAL > WARNING)
- 未提供输入的模式跳过检测 (不报错)

## 4. 关键不变量 (INVARIANTS)

- 6种止损模式互斥检测 (各自独立判定)
- 亏损限额三级递进: 日 < 周 < 月 (配置校验)
- 强制停盘天数随级别递增: 日 <= 周 <= 月 (配置校验)
- CRITICAL/EMERGENCY 级信号必须触发 RK-04 执行
- 亏损率以负数表示, 盈利不算亏损

## 5. 错误契约

- `InvalidStopLossInputError` (ZA-RK-0009): 输入非法(价格非正/符号空/限额非递进/停盘天数非递增)

## 6. 测试

- `tests/risk/test_ashare_stop_loss_engine.py` (38 用例)
- 覆盖: 6种模式各自触发/不触发、亏损限额三级、多模式同时触发排序、输入校验、自定义配置、信号属性

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: RK-04 Stop Loss Engine (执行止损), RK-03 Portfolio Risk Monitor (告警)
- 替代: 陈旧节点 MOD-RSK-009 (src/zephyr/risk/ashare_stop_loss_rule_engine.py, 文件不存在, 已软删除)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RK-09`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RK-09` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RK-09` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RK-09 | MOD-RK-09 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/risk/test_ashare_stop_loss_engine.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
