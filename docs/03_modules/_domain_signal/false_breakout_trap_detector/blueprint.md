---
blueprint_id: MOD-SIG-100
module_name: false_breakout_trap_detector
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
---

# MOD-SIG-100 false_breakout_trap_detector 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01370（模块15 假突破与诱多检测模型，
> 裁定=做 P1）+ 候选注册表 CAND-TESTB-015。
> 代码：`src/zephyr/signal_ashare/false_breakout_trap_detector.py`

## 0. 定位

场内对账（查重铁律④分工在案）：
- breakout_failure_detector（MOD-SELL-003，D_SELL_DECISION）= 卖出侧单次挑战成败
  检测（压力位×当前价×历史挑战次数，管"持仓该不该卖"，K≥3 失败强平）；
- unified_pattern_engine（MOD-SIG-091）= 图形识别库（双顶/中枢/趋势线模板）；
- **假突破判定（N=3 日回落）/失败速度/诱多三特征评分（缩量+CVD 背离+尾盘）/
  假突破率滚动统计（A股基线 40-50%）供买入侧防伪均无实现**（深挖批
  min_build_spec 明示缺口）。本模块为买入侧独立检测器（信号域）：
  与图形库是"统计检测器 vs 图形模板"分工，与 SELL-003 是"买入侧防伪 vs 卖出侧
  止损"分工，均正交。
- CVD 腿消费 MOD-SIG-093（intraday_volume_orderflow）CVD 序列契约（鸭子类型注入，
  不 import，P1W02 fragment 既定计划）。

## 1. 接口

```python
@dataclass(frozen=True) class Bar                     # 单根 OHLCV（open/high/low/close/volume）
@dataclass(frozen=True) class BreakoutEvent           # 历史已评估事件（false_breakout: bool）
@dataclass(frozen=True) class FalseBreakoutConfig     # 阈值配置（构造即校验）
@dataclass(frozen=True) class TrapFeatureScore        # 诱多三特征（缩量/CVD背离/尾盘+总分+suspected）
@dataclass(frozen=True) class BreakoutEvaluation      # 单事件评估（确认/假突破/失败速度/诱多/pending）
@dataclass(frozen=True) class FalseBreakoutStats      # 滚动统计（false_rate/基线比较/elevated/sufficient）
class FalseBreakoutTrapDetector:
    def evaluate(self, bars, resistance, breakout_index, *,
                 cvd=None, breakout_minute=None) -> BreakoutEvaluation
    def rolling_stats(self, events) -> FalseBreakoutStats
```

- **突破确认**：close>resistance 为突破；量 ≥1.5×前 20 根均量 → confirmed（放量确认）。
- **假突破判定（N=3 日回落）**：突破根后逐根检查，首根 close<resistance →
  false_breakout=True，fail_speed_days=距突破根根数（1=次日即回落=极弱）；
  3 根内未回落 → False；后续根数不足 → pending=True（未决不出伪判定）。
- **诱多三特征评分**（0-100，≥60 suspected）：缩量突破（突破根量<前 20 均量）40
  + CVD 背离（突破根 CVD < 前 lookback 内前高对应 CVD；cvd=None → 该腿 0 分降级
  + notes）35 + 尾盘突破（突破分钟 ≥270，自 9:30 起，即 14:30 后；None → 0 分降级）25。
- **假突破率滚动统计**：取最近 stats_window（默认 20）个已决事件，
  false_rate=falses/total；>0.50 → elevated（高于 A 股基线上沿），<0.40 →
  below_baseline；total<min_events（默认 5）→ sufficient=False 显式降级。

## 2. 纪律

- resistance>0、价格>0、量≥0、breakout_index∈[0,len)、配置阈值范围校验；
  非法 → ValueError（fail-closed）。
- 均量窗前视（仅突破根之前，PIT）；CVD/尾盘腿缺数据 → 0 分降级+notes 不炸。
- 未决事件（pending）不进滚动统计（调用方契约，events 仅收已决）。
- frozen dataclass asdict JSON 可序列化；纯内存统计不直连 DB、不荐股。

## 3. 依赖

- import：标准库（math/statistics/dataclasses）——无 zephyr 内部 import 边。
- 上游注入：D_DATA OHLCV 日K、D_FACTOR 压力位、MOD-SIG-093 CVD 序列、
  突破时间戳（分钟级装配层）；下游候选：买入侧防伪门槛/突破质量卡。
