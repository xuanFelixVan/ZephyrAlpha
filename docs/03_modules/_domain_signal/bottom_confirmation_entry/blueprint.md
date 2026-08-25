---
blueprint_id: MOD-SIG-103
module_name: bottom_confirmation_entry
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

# MOD-SIG-103 bottom_confirmation_entry 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01414（模块17 多维度底部确认与右侧入场模型，裁定=做 P1）+ 候选注册表 CAND-TESTB-020。
> 代码：`src/zephyr/signal_ashare/bottom_confirmation_entry.py`

## 0. 定位

场内对账（查重铁律④分工在案，P1W03 fragment 预留）：
- extreme_sentiment_reversal_detector（MOD-SIG-099）= 极端情绪反转**事件检测器**
  （双冰点+Capitulation 打分卡+shakeout 区分，管"是不是恐慌底"）；
- wyckoff_accumulation_signal（MOD-SIG-094）= Wyckoff 评分上穿+CVD 确认买点
  （单一 Wyckoff 维度）；MOD-REGIME-002 wyckoff_engine = 阶段评分生产方；
- **五维底部确认整合+右侧入场触发（突破前日高）+ATR 止损联动无实现**
  （深挖批 min_build_spec 明示缺口），本模块落地——确认整合与入场触发层
  （管"什么时候进、止损放哪"），与 099 分工（多维确认整合 vs 事件检测）、
  与 094 分工（Wyckoff 仅为五维之一，不重写其评分）。

## 1. 接口

```python
BOTTOM_DIM_NAMES  # 五维封闭集（price_oversold/volume_rebound/smart_money_flow/sentiment_extreme/wyckoff_spring）
@dataclass(frozen=True) class BottomConfirmationConfig   # 五维参数+门限+权重（构造即校验）
@dataclass(frozen=True) class DimReading                 # 单维读数（hit/weight/present/detail）
@dataclass(frozen=True) class BottomConfirmationReport   # 确认数/确认/入场/止损/ATR/底部低/逐维
class BottomConfirmationEntry:
    def evaluate(self, symbol, opens, highs, lows, closes, volumes, *,
                 smart_money_flows=None, sentiment_scores=None,
                 wyckoff_springs=None) -> BottomConfirmationReport
```

- **五维判定**（最新根，PIT）：
  1. price_oversold：RSI14<30（Wilder 自算）或收盘≤布林下轨（20,2σ；
     零方差塌缩带无信息不判触轨）；
  2. volume_rebound：近 10 根（除今）均量<0.5×其前 20 根均量（萎缩）
     ∧ 今量≥1.5×前 20 均量 ∧ 收阳（放量反弹）；
  3. smart_money_flow：近 5 根净流入和>0 或今日逆势净流入（注入）；
  4. sentiment_extreme：情绪分≤扩展窗 22% 分位（恒定窗零方差无信息不判，
     MOD-SIG-101 零方差纪律同构；口径对齐 MOD-SIG-099）；
  5. wyckoff_spring：近 10 根内 Spring 标记（注入）。
- **确认**：命中维数≥min_confirmations（默认 3）→ bottom_confirmed；
  置信度=在场维加权命中占比（dim_weights 可注入，注册表"IC 加权"语义=
  权重外配注入位，默认等权）。
- **入场与止损**：确认 ∧ 今收>前日高 → entry_triggered（entry_price=今收）；
  止损=bottom_lookback（20）窗最低价−atr_stop_mult（1.0）×ATR14（Wilder 自算）。
- **降级**：资金流/情绪/Spring 序列缺失 → 该维 hit=False+present=False+notes，
  不阻断其余维。

## 2. 纪律

- 空 symbol/OHLCV 不等长/短于 min_history（默认 40，≥萎缩窗+基准窗+1）/非有限/
  非正价/负量/注入序列不对齐或非有限/未知维度权重/负权重/非法配置 → ValueError（fail-closed）。
- PIT：RSI/ATR/布林/均量/分位全部滚动窗≤当根；入场比较用前日高（highs[-2]）。
- frozen dataclass asdict JSON 可序列化；纯内存统计不直连 DB、不荐股。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~102 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：MOD-REGIME-002 wyckoff_engine
  （Spring/阶段）、MOD-SIG-025 market_sentiment_analyzer（情绪分）、
  MOD-SIG-093 intraday_volume_orderflow / 模块5 资金流（B10-01361，Smart Money 净流入）。

## 4. 测试

`tests/signal_ashare/test_bottom_confirmation_entry.py`（26 用例）：
配置/输入 fail-closed、五维逐维命中与缺失降级、≥3 确认、右侧入场触发/未突破不入场、
止损=底部低−ATR、加权置信度、frozen/JSON 契约。
