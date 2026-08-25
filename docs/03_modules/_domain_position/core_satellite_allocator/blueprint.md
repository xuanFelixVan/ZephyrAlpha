---
blueprint_id: MOD-POS-025
module_name: core_satellite_allocator
domain: D_POSITION
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_POSITION
path: src/zephyr/position/core/core_satellite_allocator.py
granularity: file
---

# MOD-POS-025 core_satellite_allocator 蓝图（模块24 核心-卫星仓位管理模型）

> **module_id**: MOD-POS-025 | **域**: D_POSITION | **优先级**: P1
> **来源**: B10-01465（AUD-DRAFT-001-DIGEST P1 波 W-P1-20，CAND-POS-005，A1交易决策架构 §8模块24）
> 代码：`src/zephyr/position/core/core_satellite_allocator.py`

## 0. 定位

模块24 核心-卫星仓位管理模型：Core-Satellite 核心卫星组合结构（CFA Institute
推荐）。TSV 现状注记"无"——核心仓 Kelly 长期 + 卫星≤30% 帽 + 卫星做T/换仓
结构为仓位管理缺口（做T限已有底仓变相 T+0 不越硬边界）。

查重分工（W-P1-20 铁律③探查——**结构分配层缺口，非真源重叠**，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| position_sizing_engine | MOD-POS-001 | 标的层 Kelly+13 约束精裁（半Kelly硬上限） | 本件产**结构分配方案**（核心/卫星分组+目标权重带），精裁委托 sizing |
| position_adjudication_center | MOD-POS-024 | 四层裁决唯一入口（编排层） | 本件方案运行时交裁决中心统一裁决，不旁路 |
| t_trade_coordinator | MOD-SELL-018 | 单标的做T 计划器（两腿/成本/viable） | 本件只出**哪些卫星标的、何时触发**做T信号，执行计划委托 MOD-SELL-018 |
| strategy_book / firm_risk_aggregator | MOD-POS-020/021 | 策略层粗仓位 / 组合汇总 | 数据流上游，非核心-卫星结构 |

不做什么：不重造 Kelly 精裁（委托 MOD-POS-001）、不做做T 两腿计划（委托
MOD-SELL-018）、不直接下单（只出 CoreSatellitePlan 结构方案+信号）。

## 1. 规则（确定性，Fail-Closed）

- **核心-卫星分组**：候选按 kelly_fraction 降序，核心仓先配（每组总和≤
  core_budget=1−satellite_cap）；卫星组总权重硬帽 satellite_cap=0.30（超出
  等比截断并留痕 truncated=true）。
- **权重口径**：单标的权重=half-Kelly（kelly_fraction×0.5，对齐 MOD-POS-001
  半Kelly纪律），单标的不超过 single_name_cap。
- **止损参数分轨**：核心仓 ATR 止损 k=core_atr_k(默认3.5，区间3-4)；卫星仓
  k=satellite_atr_k(默认1.75，区间1.5-2)。
- **卫星做T信号**：price > vwap + t_band_atr×atr → SELL_PART；price < vwap −
  t_band_atr×atr → BUY_BACK；带内不动作。仅卫星仓触发（核心仓长期持有不做T），
  执行委托 MOD-SELL-018（T+1 内生约束由下游保证）。
- **RS 排名换仓触发**：卫星标的 rs_rank 跌出 rs_keep_rank（默认前30%分位口径，
  以候选池分位数判定）且有 rs_rank 更优的池外挑战者 → SwapTrigger
  （out=掉队卫星，in=挑战者，reason 留痕）。
- Fail-Closed：输入非法（权重∉[0,1]/cap 越界/空 symbol/负 atr）→
  CoreSatelliteError。

## 2. 接口

```python
class Sleeve(str, Enum): CORE / SATELLITE

@dataclass(frozen=True)
class CandidateAsset: symbol, kelly_fraction, rs_pct(0~1 分位), price, vwap, atr

@dataclass(frozen=True)
class CoreSatelliteConfig:
    satellite_cap=0.30, single_name_cap=0.20,
    core_atr_k=3.5, satellite_atr_k=1.75, t_band_atr=1.0, rs_keep_pct=0.30

@dataclass(frozen=True)
class AllocationLeg: symbol, sleeve, target_weight, stop_atr_k, truncated

@dataclass(frozen=True)
class TTradeSignal: symbol, action(SELL_PART/BUY_BACK), deviation_atr, reason

@dataclass(frozen=True)
class SwapTrigger: out_symbol, in_symbol, reason

@dataclass(frozen=True)
class CoreSatellitePlan: legs, satellite_weight, t_signals, swap_triggers, notes

class CoreSatelliteAllocator:
    allocate(candidates, config) -> CoreSatellitePlan
    satellite_t_signals(legs_quotes, config) -> tuple[TTradeSignal, ...]
    rs_swap_check(legs, challengers, config) -> tuple[SwapTrigger, ...]
```

## 3. 错误契约

- `CoreSatelliteError`（未登记错误码-申请中，占位 ZA-POS-UNREGISTERED-CORE-SATELLITE，
  建议号段 ZA-POS-0025 见 W-P1-20 fragment）

## 4. 测试

- `tests/position/test_core_satellite_allocator.py`
- 覆盖：分组与30%帽截断、half-Kelly口径、止损k分轨、做T三态信号、RS换仓触发、
  输入校验 Fail-Closed

## 5. 依赖

- `zephyr.shared.foundation.errors`（ZephyrBaseError）
- 委托件（运行时装配，不 import）：MOD-POS-001 精裁 / MOD-SELL-018 做T计划 /
  MOD-POS-024 裁决入口
