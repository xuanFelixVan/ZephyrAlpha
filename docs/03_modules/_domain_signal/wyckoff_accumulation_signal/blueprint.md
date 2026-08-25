---
blueprint_id: MOD-SIG-094
module_name: wyckoff_accumulation_signal
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

# MOD-SIG-094 wyckoff_accumulation_signal 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01362（模块6 Wyckoff 吸筹阶段与底部确认
> 模型，裁定=做 P1）+ 候选注册表 CAND-TESTB-009。
> 代码：`src/zephyr/signal_ashare/wyckoff_accumulation_signal.py`

## 0. 定位

吸筹六阶段 FSM+评分已有（MOD-REGIME-002 wyckoff_engine，score∈[0,100]）；
信号化买入确认（CVD）+Granger 因果自检为缺口。本模块消费 wyckoff 阶段评分
叠加 CVD 确认生成吸筹买点，并做 Granger 因果防倒置。

与既有件边界（查重裁定）：
- MOD-REGIME-002 wyckoff_engine：阶段识别+评分生产方。域方向纪律
  regime→signal_ashare（signal_ashare 不 import regime），本件按鸭子类型
  注入评分序列，零跨域 import。
- MOD-SIG-093 intraday_volume_orderflow：CVD 序列生产契约（注入消费）。
- sentiment_cycle 顶背离（情绪口径）/t0_point_analyzer 日内量价背离（做T）：
  语义正交。
- 对标：民生金工 WSS Wyckoff 吸筹量化（候选注册表 problem 陈述）。

## 1. 接口

```python
@dataclass(frozen=True) class WyckoffAccumulationConfig  # 门槛/窗口/Granger 参数
@dataclass(frozen=True) class AccumulationSignal         # 单条买点
@dataclass(frozen=True) class GrangerResult              # F/p/lag/significant
@dataclass(frozen=True) class AccumulationResult         # signals+计数+Granger三态
class WyckoffAccumulationSignal:
    def granger_causality(self, x, y, max_lag=None) -> GrangerResult   # x→y F 检验
    def generate(self, wyckoff_score, cvd) -> AccumulationResult       # 买点批量
```

买点 = 评分上穿门槛（默认 60，对齐 wyckoff_engine S2 confirm）+ 上穿点 CVD
高于 cvd_rise_window 根前；置信度=评分/100。
Granger 防倒置：ΔCVD→Δ评分 滞后 OLS F 检验显著才放行；不显著→候选全阻断；
样本不足 granger_min_obs → checked=False 显式降级不阻断。

## 2. 纪律

- 不等长/过短/NaN/评分越界[0,100]/非法配置 → ValueError（fail-closed）。
- F 分布右尾 p 值由纯 Python 正则化不完全贝塔（连分式）实现——零 scipy
  依赖（pyproject 幽灵依赖纪律，scipy 未声明，同 python-dotenv 案禁令）。
- Granger 三态（checked/passed/blocked）落档可追溯，降级不静默。
- frozen dataclass、to_dict JSON 可序列化；不直连 DB、不荐股。

## 3. 依赖

- import：numpy、pandas（无 zephyr 内部 import 边）。
- 上游注入：MOD-REGIME-002 wyckoff 评分（装配层 shift(1) PIT 隔离后注入）、
  MOD-SIG-093 CVD 序列；下游候选：买入侧装配层/MOD-SIG-086 漏斗。
