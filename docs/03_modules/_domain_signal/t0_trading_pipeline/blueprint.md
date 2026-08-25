---
blueprint_id: MOD-SIG-090
module_name: t0_trading_pipeline
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: H
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
---

# MOD-SIG-090 t0_trading_pipeline 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B1-00191（C-012 做T日内套利，裁定=做 P1）+
> 候选注册表 CAND-TESTB-005。代码：`src/zephyr/signal_ashare/t0_trading_pipeline.py`

## 0. 定位

做T信号点（MOD-SIG-068 t0_point_analyzer）与 t_trade_coordinator（MOD-SELL-018）
在，独立做T信号管线与盘中即时反应决策引擎未收口（深挖裁定理由）。本模块落
**做T全链路管线**：

    信号（MOD-SIG-068 复用）→ 决策（底仓/价差/次数硬约束过滤）
    → 执行（注入 executor，生产侧由集成批接 MOD-SELL-018）
    → 当日复盘（轮次价差/命中/延迟留痕）

- **硬约束**：底仓自平衡（单轮买量=卖量、当日净持仓变动=0）、单腿股数手数对齐、
  当日轮次上限、单轮最小价差、信号置信度下限。
- **延迟预算**：全链路累计延迟超预算→不再开新轮（轮内平衡腿仍须闭合，
  平衡不变量优先于预算，违例留 notes）。
- **失败回滚**：平衡腿执行失败→反向腿回滚恢复底仓；回滚再失败→升级 notes
  （fail-closed 留痕，不静默）。
- **尾盘强制平衡**：EOD 未闭合轮按末 bar 价强制闭合，保底仓不变量。

与既有件边界：MOD-SIG-068 只做点位信号与回验（非交易执行）；MOD-SELL-018
t_trade_coordinator 是单腿计划件，本模块经 **executor 注入契约**挂接（生产接线
留集成批，本模块不 import 跨域 sell_decision——signal_ashare→sell_decision
无 import 先例，保持域方向纪律）。

## 1. 接口

```python
@dataclass(frozen=True) class T0PipelineConfig   # 底仓/价差/次数/手数/延迟预算
@dataclass(frozen=True) class T0OrderIntent      # 执行意图（symbol/side/volume/price）
@dataclass(frozen=True) class T0Fill             # 执行回报（filled/price/latency_ms）
@dataclass(frozen=True) class T0RoundResult      # 单轮结果（含回滚标记）
@dataclass(frozen=True) class T0DayReport        # 当日复盘
class T0TradingPipeline:
    def __init__(self, config, executor: Callable[[T0OrderIntent], T0Fill])
    def run_day(self, bars, context, analyzer_config=None) -> T0DayReport
```

## 2. 纪律

- 底仓自平衡为最高不变量：任何路径（含失败/EOD/超预算）结束时当日净腿量=0，
  破坏即升级 notes。
- 配置校验 fail-closed：单腿股数≤底仓、手数对齐、轮次≥1、价差阈值>0、预算>0。
- frozen dataclass、to_dict JSON 可序列化；本模块为决策编排非券商直连，
  成交成本口径归执行层/宪章§3约束一。
