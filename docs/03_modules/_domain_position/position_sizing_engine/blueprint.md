---
module_id: MOD-POS-001
title: "仓位决策引擎蓝图 — 四轨融合+半Kelly+13约束+分阶段施工"
doc_type: blueprint
status: Active
version: "0.2.3"
design_maturity: production
ttl: permanent
layer: L03_position
layer_name: position
functional_domain: position
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P0
blueprint_level: module
responsibility_domain: 
---

# MOD-POS-001 Position Sizing Engine — 仓位决策引擎 蓝图

> **module_id**: MOD-POS-001 | **域**: D_POSITION | **层**: L03 仓位管理
> **优先级**: P0 | **成熟度**: production | **建设标记**: ✅可建
> **SSoT**: depgraph MOD-POS-001 | **设计真源**: D:\临时工作区\依赖图\07-D-POSITION-仓位管理域.md §1.1 POS-01, §7.1 四层架构, §7.2 四轨架构, §8 PositionPlan

## 1. 定位

仓位决策引擎——D-POSITION 域的**核心裁决器**，消费四轨输入(逻辑驱动+数据驱动+人工指令+应急保命)
+目标权重+策略分配+密度预测分布参数，综合 10+ 硬约束，产出最终仓位方案 `PositionPlan`。

属 **B 类核心业务模块**(多源融合+约束裁决+决策输出)，半 Kelly 系数/各类阈值为 C 类可调参数。

**边界**: 不执行交易(执行由 D-EX-CORE 承接)；不直接管理资金流水(由 POS-006 承接)；
不触发风控熔断(由 D-RISK stop_loss 承接)。本模块是"仓位方案的生产者"，不是"交易的执行者"。

## 2. 输入 / 输出

### 2.1 输入

| 方向 | 内容 | 契约/事件 | 来源 | 就绪 |
|------|------|-----------|------|:----:|
| 轨道1 | TargetPortfolio(目标权重) + 策略级仓位建议 | CTR-007 | D-PF-CORE | ❌待建 |
| 轨道1 | CapitalAllocationResult(策略分配) | CTR-P1-003 | D-PF-ALLOC | ❌待建 |
| 轨道1 | RiskLimits(风控约束) | CTR-003 | D-RISK risk_limits | ✅stable |
| 轨道2 | AIDiscoveryPosition(AI 发现轨仓位信号) | — | D-ML-SERVE | ❌待建 |
| 轨道2 | 密度预测输出(分布参数) | — | D-ML-SERVE | ❌待建 |
| 轨道3 | 人工调仓指令 | — | Trader | ✅外部 |
| 轨道4 | 应急模式标志 | — | D-RISK / Trader | ✅外部 |
| 公共 | CapitalCurveLimit(资金曲线仓位上限) | — | POS-007 | ✅stable |
| 公共 | CashConstraint(现金约束) | — | POS-006 | ✅stable |
| 公共 | CalendarPositionAlert(日历仓位约束) | — | POS-017 | ✅stable |
| 公共 | MarketRegime(市场状态仓位上限) | — | D-SIGNAL | ❌待建 |
| 公共 | PositionSnapshot(当前持仓) | CTR-006 | D-EX-CORE | ⚠️部分 |

### 2.2 输出

| 方向 | 内容 | 契约/事件 | 去往 |
|------|------|-----------|------|
| 输出 | PositionPlan(最终仓位方案) | CTR-POS-001 | D-EX-CORE |
| 事件 | PositionSized(仓位决策完成) | E-POS-01 | D-EX-CORE, D-PF-CORE |

### 2.3 PositionPlan 定义 (CTR-POS-001, 设计真源 §8)

| 字段 | 类型 | 说明 |
|------|------|------|
| plan_id | str | 仓位方案唯一标识 |
| strategy_id | str | 关联策略 ID |
| positions | dict[str, PositionTarget] | {symbol: {target_qty, current_qty, delta, reason}} |
| cash_reserve | float | 现金储备金额 |
| total_exposure | float | 总仓位暴露比例 |
| capital_curve_discount | float | 资金曲线缩放系数(回撤<1.0, 盈利>1.0) |
| calendar_constraint_active | bool | 日历约束是否激活 |
| volatility_adjustment | float | 波动率调整系数(正常1.0, 超2σ→0.5) |
| constraints_check | dict | 各约束层检查结果 |
| created_at | datetime | 创建时间 |
| idempotency_key | str | 幂等键 |
| schema_version | str | "1.0" |

## 3. 四层决策架构 (设计真源 §7.1)

```
第一层：组合层 (Portfolio Level)
  ├─ 总仓位上限 = min(市场状态上限, 风控上限, 资金曲线上限, 日历约束上限)
  ├─ 风险预算总框 = D-PF-ALLOC 策略间分配方案
  └─ 现金约束 = POS-006 最低储备+机会储备+T+1+节假日
         │
         ▼
第二层：策略层 (Strategy Level)
  ├─ 策略内标的选择 = D-PF-CORE 目标权重
  ├─ 跨策略仓位合并 = POS-005 同标的多策略合并(sum/max)
  └─ 策略灰度发布 = 新策略 5%→20%→50%→100%
         │
         ▼
第三层：标层 (Symbol Level)  ← 核心裁决层
  ├─ Kelly 仓位 = p_i=∫₀^∞ f(r|X)dr, b_i=E[r⁺]/|E[r⁻]|, f*=(bp-q)/b
  ├─ 半 Kelly 约束 = w_kelly = min(0.5×f*, 单票上限)
  ├─ 分布感知调整 = 偏度/峰度/VaR/CVaR → 防御性只减不增
  ├─ 流动性检查 = 参与率>15%→否决 / 退出时间>3天→强制减仓
  └─ 波动率检查 = 超2σ→仓位减半 / 前瞻VaR/CVaR超限→仓位下调
         │
         ▼
第四层：动态层 (Dynamic Level)
  ├─ 持仓状态机 = POS-002 NONE→BUILDING→ACTIVE→OBSERVING→...
  ├─ 漂移监控 = POS-003 组合±2%/单标的±3%
  ├─ 再平衡决策 = POS-004 成本>2×收益→跳过
  └─ 资金曲线联动 = POS-007 回撤→降仓/盈利→扩张
```

## 4. 四轨融合架构 (设计真源 §7.2)

| 轨道 | 名称 | 输入来源 | 决策权重 |
|------|------|---------|---------|
| 轨道1 | 逻辑驱动 | 多策略共振仓位+因子直通(Kelly+风险预算直接决策) | 确认仓位 |
| 轨道2 | 数据驱动 | AI 发现轨仓位信号(RL策略→AI仓位建议) | 确认仓位 |
| 轨道3 | 人工指令 | 人工调仓指令→验证→执行 | 覆盖自动 |
| 轨道4 | 应急保命 | 应急模式→硬编码仓位上限(单标的≤10%/总仓位≤30%) | 硬上限不可逾越 |

**四轨融合规则**:
- 1+2 同向 → 确认仓位
- 单轨 → 保守仓位(×0.8)
- 冲突 → 取较小值
- 轨道3 覆盖自动(验证后执行)
- 轨道4 硬上限不可逾越(覆盖一切)

**四轨优先级**: 轨道4(应急) > 轨道3(人工) > 轨道1/2(自动)

## 5. 核心约束 (13 项, 设计真源 §1.1 POS-01)

### 5.1 约束清单与优先级

| # | 约束 | 触发条件 | 动作 | 优先级 | 阶段 |
|---|------|---------|------|:------:|:----:|
| C1 | 半 Kelly 硬上限 | w > 0.5×f* | 截断至 0.5×f* | P0 | 阶段1 |
| C2 | 风险配额内决策 | Kelly 超 risk_budget | 截断至 risk_budget | P0 | 阶段1 |
| C3 | 波动率超 2σ | vol > μ+2σ | 仓位减半(×0.5) | P0 | 阶段1 |
| C4 | 前瞻 95%VaR 超限 | VaR > var_threshold | 仓位上限下调 | P0 | 阶段1 |
| C5 | 前瞻 95%CVaR 超限 | CVaR > cvar_threshold | 进一步下调 | P0 | 阶段1 |
| C6 | 参与率否决 | participation > 15% 日成交量 | 否决该笔 | P0 | 阶段1 |
| C7 | 退出时间>3天 | exit_days > 3 | 强制减仓至可退出 | P0 | 阶段1 |
| C8 | 退出时间>1天 | exit_days > 1 | 仓位上限折扣 | P1 | 阶段1 |
| C9 | 策略容量预警 | capacity > AUM×80% | 预警; >AUM×100% 否决新资金 | P1 | 阶段1 |
| C10 | 分布感知 | 偏度<0(左偏) | 防御性只减不增; 正偏允许+10% | P1 | 阶段2 |
| C11 | 冲击成本否决 | impact_cost > 0.5% | 否决单笔大额 | P1 | 阶段1 |
| C12 | 单票上限 | w > 5%NAV | 截断至 5% | P0 | 阶段1 |
| C13 | 市场状态上限 | 见 §5.2 映射表 | 截断至状态上限 | P0 | 阶段1 |

### 5.2 市场状态→仓位上限映射 (设计真源 §7.3 v8.1, 12 态+overlay, immutable)

| 市场状态 | 仓位上限 | 说明 |
|---------|:-------:|------|
| ①平稳牛市 | 80% | 高量能扩张≤90% |
| ②动量牛市 | 80% | 高量能-中扩张≤80% |
| ③恐慌反弹 | 60% | 中量能正常 |
| ④窄幅盘整 | 40% | 低量能收缩≤50% |
| ⑤宽幅震荡 | 50% | — |
| ⑥压缩突破 | 60% | 40%→70% |
| ⑦阴跌 | 30% | — |
| ⑧加速下跌 | 20% | — |
| ⑨恐慌崩盘 | 10% | — |
| ⑩CRISIS(危机) | 5% | 极端行情, 仅减仓不开新 |
| ⑪RECOVERY(复苏) | 50% | 回撤回补期, 逐步重建 |
| ⑫BREAKOUT(突破) | 70% | 趋势确立, 加仓 |

overlay 标志位(正交修饰, 不占 enum):
| 标志 | 效果 | 消费方 |
|------|------|--------|
| is_event_driven | 基础仓位×70% | POS-001 (total_cap×0.70) |
| is_sector_rotation | 行业集中度放宽至±15% | POS-010 (POS-001 透传不改 cap) |

> 状态→仓位映射为 immutable(不可 AI 修改), 调整需 Trader 审批
> 🆕v8.1 (2026-08-02): 12 态对齐 D-SIGNAL-04, 事件驱动/板块轮动转 overlay 标志位
> (样本量论证见设计真源 §7.3.1: overlay 不进 enum 避免 11×2×2=44 组合样本崩盘)

### 5.3 约束执行顺序

```
[0] 预筛阶段(基于保守上限, Kelly 前)
    ├─ C7/C8 退出时间检查(基于当前持仓, Kelly 前已知量)
    └─ 流动性预筛(用 max_qty = 单票上限×NAV/price 估算参与率/冲击成本上限)
       └─ 上限已超限 → 标记低流动性, Kelly 时强制限仓; 全否决 → 跳过该标的
         │
         ▼
[1] Kelly 计算 → C1半Kelly → C2风险配额 → C3波动率 → C4/C5 VaR/CVaR
→ C10分布感知 → C12单票上限 → C13市场状态上限
→ C6参与率否决(实际目标量) → C9策略容量预警 → C11冲击成本否决(实际目标量)
→ 四轨融合 → POS-007资金曲线缩放 → POS-006现金约束 → POS-017日历约束
→ 输出 PositionPlan
```

> **预筛设计原理**: C7/C8退出时间依赖当前持仓(Kelly 前已知), 可前置精确检查;
> C6参与率/C11冲击成本依赖目标量(Kelly 后才知), 预筛用保守上限 max_qty 做
> 快速排除——若最大可能仓位都已超限, 实际仓位必然超限, 跳过 Kelly 省计算。
> Kelly 后仍保留 C6/C11 精确否决闸, 防预筛放行但实际超限的边界情况。

### 5.4 关键参数定义

| 参数 | 定义 | 数据来源 | 阶段 |
|------|------|---------|:----:|
| 策略容量 (capacity) | 该策略历史最大持仓市值(滚动窗口, 默认 60 交易日) | PositionSnapshot 推导(持仓市值序列 max) | 阶段1 |
| AUM | 当前账户净值(可用资金+持仓市值) | POS-006 CashManager + 持仓快照 | 阶段1 |
| 参与率 | target_qty / 日成交量(20日均量) | target_qty(Kelly 产出) + D-DATA 行情 | 阶段1 |
| 退出时间 | 当前持仓 / 日成交量(天, A股 T+1) | PositionSnapshot + D-DATA 行情 | 阶段1 |
| 冲击成本 | f(target_qty, 日均量, 价差) — 线性冲击模型 | target_qty + D-DATA 行情 | 阶段1 |
| idempotency_key | `f"{strategy_id}:{trade_date}:{hash(sorted(target_weights.items()))[:8]}"` | 策略ID+交易日+目标权重哈希 | 阶段1 |

> **幂等键规则**: 同策略同交易日同目标权重 = 同一决策(防重复)。任一维度变化 → 新 key → 新决策。
> **容量计算**: capacity 为历史最大值(非当前值), 避免减仓后容量虚降导致误预警。

## 6. 降级策略 (设计真源 §5)

| 上游缺失 | 降级模式 | 影响 |
|---------|---------|------|
| D-PF-CORE(目标权重) | 固定比例仓位(按市场状态查表) | 跳过 Kelly+策略分配 |
| D-PF-ALLOC(策略分配) | 等权分配 | 跳过策略间风险预算 |
| D-ML-SERVE(密度预测) | 正态分布假设 | 跳过分布感知(C10) |
| D-SIGNAL(市场状态) | 默认状态④(40%) | 保守仓位上限 |
| D-EX-CORE(持仓快照) | 跳过参与率/退出时间检查 | C6/C7/C8 降级 |

> **降级原则**: 任何上游缺失不阻塞仓位决策，降级模式产出保守仓位方案，标记 `constraints_check.degraded=true`

## 7. 分阶段施工里程碑

### 阶段1: 核心裁决层 (P0, 不依赖未建上游)

**目标**: 实现 Kelly 仓位 + 风险约束 + 流动性/容量检查, 可用降级模式运行

**范围**:
- 预筛阶段(退出时间检查 + 流动性上限预筛, §5.3 [0])
- Kelly 仓位计算(p_i, b_i, f*) + 半 Kelly 截断(C1)
- 风险配额约束(C2) — 消费 risk_limits
- 波动率检查(C3) + VaR/CVaR 下调(C4/C5) — 消费 risk_limits
- 单票上限(C12) + 市场状态上限(C13) — 市场状态用降级默认
- 参与率否决(C6) + 退出时间减仓(C7/C8) — 持仓快照用降级/桩
- 策略容量预警(C9) + 冲击成本否决(C11)
- 资金曲线缩放(消费 POS-007) + 现金约束(消费 POS-006) + 日历约束(消费 POS-017)
- PositionPlan 输出(CTR-POS-001)
- 降级模式(上游缺失时保守仓位)

**不包含**: 四轨融合(轨道2 AI 发现 / 轨道3 人工 / 轨道4 应急)、分布感知(C10)、跨策略合并(POS-005)

**预计**: ~500 行代码 + ~40 测试

### 阶段2: 四轨融合 + 高级约束 (P1, 依赖上游就绪)

**目标**: 完整四轨融合 + 分布感知 + 跨策略合并

**前置**: D-PF-CORE / D-PF-ALLOC / D-ML-SERVE 密度预测就绪

**范围**:
- 轨道2 AI 发现轨仓位信号融合
- 轨道3 人工指令验证+覆盖
- 轨道4 应急保命硬上限
- 分布感知(C10) — 偏度/峰度调整
- 跨策略仓位合并(POS-005 联动)
- 四轨融合规则(同向确认/单轨保守/冲突取小/覆盖/硬上限)

**预计**: ~300 行增量 + ~25 测试增量

### 阶段3: 生产化 (待阶段1/2 验证后)

**目标**: 状态晋升 production + 盘中联调

**范围**:
- 全约束集成测试
- 性能 SLA 验证(仓位裁决延迟 <100ms P50 / <500ms Warm / <1000ms P99)
- 盘中联调(QMT 实盘验证)
- depgraph build_status → stable, design_maturity → production

## 8. 关键不变量 (INVARIANTS)

- PositionPlan.positions 中每个 symbol 的 target_qty ≤ 单票上限 × NAV / price
- total_exposure ≤ min(市场状态上限, 风控上限, 资金曲线上限, 日历约束上限)
- w_kelly ≤ 0.5 × f* (半 Kelly 硬上限不可逾越)
- 参与率 > 15% 的标的不得出现在 PositionPlan.positions(否决而非截断)
- 应急模式下: 单标的 ≤ 10%, 总仓位 ≤ 30%(轨道4 硬上限)
- 降级模式必须标记 constraints_check.degraded=true(可追溯)
- PositionPlan 幂等(idempotency_key 防重复决策)

## 9. 错误契约

- `InvalidPositionInputError` (ZA-POS-0001): 目标权重为空/负值、AUM≤0、持仓快照缺失(非降级模式)
- `KellyEstimationError` (ZA-POS-0002): f* 计算异常(p≤0 或 b≤0)、密度预测分布参数非法
- `ConstraintViolationError` (ZA-POS-0003): 约束执行后仓位仍超限(不变量被破坏, 需告警)

## 10. 测试规划

### 阶段1 测试 (~42)
- 预筛阶段: 退出时间前置检查/流动性上限预筛命中跳过/预筛放行后精确否决
- Kelly 计算: 正态分布/经验分布/退化场景
- 半 Kelly 截断: 边界值/超限截断
- 风险配额: 配额内/超限截断
- 波动率: 正常/超2σ减半
- VaR/CVaR: 阈值边界/下调幅度
- 参与率: 15%边界/否决
- 退出时间: 1天/3天边界/减仓比例
- 策略容量: 80%预警/100%否决
- 冲击成本: 0.5%边界/否决
- 单票上限: 5%NAV 截断
- 市场状态: 12种状态→仓位上限映射 + overlay 标志位(is_event_driven/is_sector_rotation)
- 降级模式: 各上游缺失场景
- PositionPlan 输出: 字段完整性/幂等性

### 阶段2 测试 (~25)
- 四轨融合: 同向确认/单轨保守/冲突取小/人工覆盖/应急硬上限
- 分布感知: 左偏减仓/正偏+10%
- 跨策略合并: sum≤单票上限/卖出优先

## 11. 依赖

### 11.1 已就绪 (阶段1 可用)
- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- `zephyr.position.core.capital_curve_manager` (POS-007, CapitalCurveLimit) — stable
- `zephyr.position.core.cash_manager` (POS-006, CashConstraint) — stable
- `zephyr.position.core.calendar_position_constraint` (POS-017, CalendarPositionAlert) — stable
- `zephyr.position.core.drawdown_controller` (POS-008, DrawdownResponse) — stable
- `zephyr.risk.risk_limits` (D-RISK, RiskLimits/VarCvarMetrics) — stable

### 11.2 待建 (阶段2 前置)
- D-PF-CORE (TargetPortfolio, CTR-007) — ❌待建
- D-PF-ALLOC (CapitalAllocationResult, CTR-P1-003) — ❌待建
- D-ML-SERVE (密度预测分布参数) — ❌待建
- D-SIGNAL (MarketRegime 市场状态) — ❌待建
- D-EX-CORE (PositionSnapshot, CTR-006) — ⚠️部分

### 11.3 消费者
- D-EX-CORE (执行 PositionPlan, CTR-POS-001)
- D-PF-CORE (消费 E-POS-01 PositionSized 事件反馈)

## 12. 设计决策记录

| 决策 | 理由 |
|------|------|
| 半 Kelly 为硬上限(非全 Kelly) | 全 Kelly 估计误差下过度下注 → 半 Kelly 防过度下注 |
| 分阶段施工(非一次性) | 上游未建, 阶段1 用降级模式落地 P0 核心, 阶段2 补四轨 |
| 参与率否决(非截断) | 参与率>15% 意味着无法退出, 截断仍危险 → 否决 |
| 退出时间>3天强制减仓 | A 股 T+1, 3天无法退出的仓位是流动性陷阱 |
| 市场状态映射 immutable | 防止 AI 自行放宽仓位上限 → 需 Trader 审批 |
| 降级模式标记 degraded | 可追溯降级决策, 便于事后审计 |
| 四轨优先级 应急>人工>自动 | 保命 > 人意 > 算法, 应急模式硬上限不可逾越 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-POS-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-POS-001` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-POS-001` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-POS-001 | MOD-POS-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 13. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 13.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/position/core/__init__.py` | ✅ 已实现 | |
| `src/zephyr/position/core/position_sizing_engine.py` | ✅ 已实现 | |

### 13.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §13（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


