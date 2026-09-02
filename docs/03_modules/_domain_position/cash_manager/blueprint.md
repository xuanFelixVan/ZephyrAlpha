---
module_id: MOD-POS-006
title: "资金管理器蓝图 — T+1约束+储备计算"
doc_type: blueprint
status: Active
version: "0.2.1"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-25"
priority: P1
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-006 Cash Manager — 资金管理器 蓝图

> **module_id**: MOD-POS-006 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P1 | **成熟度**: L1 🔵 骨架 → production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-006 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.1 POS-06

## 1. 定位

资金管理器——管理资金流水与结算状态, 在 A 股 T+1 结算约束下计算可用资金头寸,
维护最低储备金/机会储备/节假日储备, 产出现金约束反馈 POS-01 (仓位决策引擎)。

属 A 类基础设施(资金流水记账+T+1结算+储备计算, 逻辑明确), 储备比例为 C 类可调参数。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 资金流水(存取/买卖) + 结算状态 | 来自 D-EX-CORE 成交回报 |
| 输出 | CashState (可用资金+储备+max_investable) | 联动 POS-01 |

## 3. 核心规则 (设计真源 §1.1 POS-06)

### 3.1 T+1 结算约束 (A股)

- 买入: 当日扣减可用资金 (立即生效)
- 卖出: 当日不计入可用资金, 进入 pending_settlement, 次交易日 settle() 后可用

### 3.2 储备金体系

| 储备类型 | 计算 | 说明 |
|----------|------|------|
| 最低储备金 | 绝对金额 min_reserve | 现金储备 ≥ 最低阈值 |
| 机会储备 | opportunity_reserve_ratio × available | 机会储备 X% |
| 节假日储备 | holiday_reserve_ratio × available (holiday_mode) | 节前2天+节后1天提高现金比例 |

### 3.3 可投资上限

- max_investable = max(0, available_cash − min_reserve − opportunity_reserve − holiday_reserve)
- POS-01 据此约束新开仓资金

### 3.4 节假日持币规划

- 节前 2 天 + 节后 1 天提高现金比例 5-15% (由 holiday_mode 标志驱动, 日历判断由上层)

### 3.5 逆回购收益增强 (W-P1-20 扩展, B10-01307/CAND-POS-003)

- 逆回购标的池 DEFAULT_REVERSE_REPO_POOL: 沪深 1/2/3/4/7 天期 (GC001~GC007/R-001~R-007)
- plan_reverse_repo: 金额 = max_investable × max_ratio (0<ratio≤1, C 类参数); 无可投资资金 → None
- 计息天数: 非节假日=term_days; 节假日模式 1 天期计息 1+holiday_extra_days (节前买 1 天期享假期连息)
- 选品: 预期利息最高; 同息取期限最短 (流动性优先)
- 执行委托券商通道 (ex_core/adapters/miniqmt_broker.py, 运行时装配, 本模块不 import)

### 3.6 出入金台账 (W-P1-20 扩展, B10-01307/CAND-POS-003)

- FundTransferLedger 仅登记 DEPOSIT/WITHDRAWAL (BUY/SELL 属交易流水由 record 管辖), amount>0
- 台账不改变 total_cash (入账仍以 record 为准); 供 projected_available 做 T+N 可用资金规划
- projected_available(target_date) = available_cash + Σ生效入金 − Σ生效出金 (未生效条目不计)

## 4. 关键不变量 (INVARIANTS)

- available_cash = total_cash − pending_settlement (T+1)
- pending_settlement ≥ 0; settle() 后归零
- max_investable ≥ 0 (储备不超过可用)
- total_cash = Σ 所有已记账流水 (deposits+ / withdrawals− / buys− / sells+)

## 5. 错误契约

- `InvalidCashFlowError` (ZA-POS-0006): 流水金额非正(存取)/非正(买卖)、类型非法

## 6. 测试

- `tests/position/test_cash_manager.py`
- 覆盖: T+1结算(卖出当日不可用/次日可用)、三类储备、max_investable、节假日模式、settle滚动、输入校验

## 7. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 消费者: MOD-POS-001 (Position Sizing Engine)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-006`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-006` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-006` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-006 | MOD-POS-006 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 8. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/position/__init__.py` | ⚠️ 骨架 | |

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


