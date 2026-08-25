---
blueprint_id: MOD-SIG-095
module_name: multi_indicator_divergence
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

# MOD-SIG-095 multi_indicator_divergence 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01363（模块7 多指标背离检测模型，裁定=做
> P1）+ 候选注册表 CAND-TESTB-010。
> 代码：`src/zephyr/signal_ashare/multi_indicator_divergence.py`

## 0. 定位

卖出侧量价背离已有（sell_signal_collector）；RSI/MACD/CVD 系统背离检测+
多级别级联为缺口。本模块落地峰谷对位背离检测器：指标核自算（RSI Wilder/
MACD DIF）+CVD 注入腿，背离程度量化，次数→反转概率与多级别级联概率查表，
并支持背离化解标记。

与既有件边界（查重裁定）：
- MOD-SELL sell_signal_collector：卖出侧量价背离聚合，非 RSI/MACD 系统化检测。
- sentiment_cycle 顶背离（情绪/炸板率口径）、t0_point_analyzer（做T 日内量价）、
  sector_divergence（板块间）、MOD-SIG-093 CVD 背离（本件 CVD 腿生产方，
  注入消费）——语义均正交或上下游关系。
- factor 指标库无 RSI/MACD 实现可查（grep 仅中 ml_train/meta_learning_rsi，
  D_ML_TRAIN 域专用），故指标核自算不 import。

## 1. 接口

```python
@dataclass(frozen=True) class DivergenceConfig      # 周期/lookback/两张概率表
@dataclass(frozen=True) class DivergenceEvent       # indicator/direction/magnitude/resolved
@dataclass(frozen=True) class DivergenceScanResult  # 全指标扫描+次数概率
@dataclass(frozen=True) class CascadeResult         # 级联对齐数+概率
class MultiIndicatorDivergenceDetector:
    def rsi(self, close, period=None) -> pd.Series               # Wilder
    def macd(self, close, fast=None, slow=None, signal=None)     # DIF/DEA/HIST
    def detect(self, close, indicator_series, *, indicator,
               lookback=None) -> list[DivergenceEvent]           # 峰谷对位
    def reversal_probability(self, count) -> float               # 次数查表
    def cascade_probability(self, directions_by_tf, *, direction) -> CascadeResult
    def scan(self, close, cvd=None) -> DivergenceScanResult      # 全指标扫描
```

峰谷对位：居中 lookback 窗口确认局部峰/谷（回溯检测语义），连续两峰/两谷
配对；magnitude=价格腿幅度+指标腿幅度（std 归一）。
默认概率表：次数 {1:35%/2:55%/3:72%}（3 次顶背离>70% 口径）；级联
{1:35%/2:50%/3:62%/4:70%}（满级≥60%）；次数越界钳制表尾。
化解：背离后指标反超前峰（bearish）/前谷（bullish）水平 → resolved=True。

## 2. 纪律

- 指标（rsi/macd/cvd）与方向（bullish/bearish）封闭集；未知指标/非法方向/
  短序列/内部非有限值/非法配置 → ValueError（fail-closed）。
- 概率表构造即校验：键≥1 整数、值∈[0,1]、随键非递减。
- RSI warmup NaN 仅允许头部（detect 跳过）；scan 计数剔除已化解事件。
- frozen dataclass、to_dict JSON 可序列化；不直连 DB、不荐股。

## 3. 依赖

- import：numpy、pandas（无 zephyr 内部 import 边）。
- 上游注入：D_DATA OHLC 行情、MOD-SIG-093 CVD 序列（鸭子类型）。
- 下游候选：买入/卖出侧装配层、MOD-SIG-086 漏斗骨架。
