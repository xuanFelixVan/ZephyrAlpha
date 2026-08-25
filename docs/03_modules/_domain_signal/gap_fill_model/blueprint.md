---
blueprint_id: MOD-SIG-092
module_name: gap_fill_model
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

# MOD-SIG-092 gap_fill_model 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01359（模块3 缺口回补概率模型，裁定=做 P1）+
> 候选注册表 CAND-TESTB-007。代码：`src/zephyr/signal_ashare/gap_fill_model.py`

## 0. 定位

场内无 gap_fill 实现（深挖对账：grep 仅命中 governance gap_analyzer 等无关项）。
本模块按 trading literature 缺口统计查表法纯统计落地：缺口按 ATR14 标准化分级，
查表输出回补概率/部分回补分布/回补时间分布，并给 MAE 止损参考价。

与既有件边界：
- ATR14 由 D_FACTOR 注入（与 risk/atr_stop_engine "ATR14 注入" 先例一致），
  本模块不 import 指标实现。
- MOD-SIG-091 unified_pattern_engine：图形识别引擎（双顶/中枢/趋势线），不管缺口
  统计口径；正交。
- 候选注册表 CAND-TESTB-007 状态曾被前置波次误翻 promoted→unified_pattern_engine
  （该件无缺口回补功能，P1W02  fragment 留主代理校正），本蓝图为该候选真实施工落点。

## 1. 接口

```python
class GapGrade(str, Enum)            # tiny/small/medium/large 四档封闭集
class GapDirection(str, Enum)        # up/down
@dataclass(frozen=True) class GapFillConfig      # 阈值+四张查表（构造即校验）
@dataclass(frozen=True) class GapFillForecast    # 单缺口预测输出（to_dict JSON 可序列化）
class GapFillProbabilityModel:
    def classify(self, gap_size_atr) -> GapGrade                       # 分级（边界归上档）
    def forecast(self, *, direction, gap_size_atr, prev_close,
                 open_price) -> GapFillForecast                        # 查表预测+MAE止损
    def detect(self, ohlc, atr14, *, min_gap_atr=0.1) -> pd.DataFrame  # 缺口事件识别
```

分级：Gap Size=(Open−Close_prev)/ATR_14；Tiny<0.3x/Small<0.6x/Medium<1.2x/Large≥1.2x。
默认回补概率：Tiny=77.8%/Small=55%/Medium=30%/Large=8.2%（可配置）。
部分回补分布：25/50/75/100% 四档（每档归一）；期望回补比例派生。
MAE 止损：fade 逆向 open ± mae_frac×|Open−Close_prev|（up 在上方，down 镜像）。

## 2. 纪律

- 四档分级/方向封闭集；非法方向/负缺口/非正价格/非正 ATR/缺列 → ValueError（fail-closed）。
- 配置构造即校验：阈值严格递增、概率∈[0,1]、部分回补分布每档归一、MAE 系数>0、
  回补时间≥1。
- detect PIT：仅用 prev_close（shift(1)），无未来信息；当日回补标记用当日 high/low
  （对已发生 K 线的观测，非预测）。
- frozen dataclass；纯内存统计，不直连 DB、不荐股。

## 3. 依赖

- import：pandas（无 zephyr 内部 import 边）。
- 上游：D_DATA OHLC 行情 + D_FACTOR ATR14（注入）；下游：精筛/买入侧装配层（候选消费）。
