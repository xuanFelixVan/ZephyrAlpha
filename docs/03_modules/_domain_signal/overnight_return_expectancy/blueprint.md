---
blueprint_id: MOD-SIG-107
module_name: overnight_return_expectancy
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

# MOD-SIG-107 overnight_return_expectancy 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01464（模块13 隔夜收益预测与开仓期望值模型，裁定=做 P1）+ 候选注册表 CAND-TESTB-024。
> 代码：`src/zephyr/signal_ashare/overnight_return_expectancy.py`

## 0. 定位

场内对账（查重铁律②⑥探查在案）：

- next_day_probability_gate（MOD-SIG-104，P1W04 已建）= 决策链**第一道门**
  （动作分档概率门槛 P≥阈值才放行，管"概率够不够"）——本件为其下游
  **第二道经济门槛**（期望值 E>0 才参与，管"值不值得"），P1W04 蓝图 §3
  预留（"下游候选：模块13 隔夜收益期望值 B10-01464 消费本门为第一道校验"）；
- next_day_8state_forecast（MOD-SIG-037）/ conditional_density_predictor
  （MOD-SIG-043）= 概率与密度**生产方**（本件 P涨/E涨/E跌 鸭子类型注入，
  复用不重造）；
- expectation_governance（D_DATA_ENG，P0 已建）= 数据质量期望套件门控
  （数据域，语义正交）；
- **E[次日收益]=P涨×E涨−P跌×E跌 + E>0.5% 门槛 + 盈亏比>1.5 + 成本优势>2ATR
  + 踏空成本量化无实现**（深挖批 min_build_spec 明示缺口），本模块落地。

## 1. 接口

```python
@dataclass(frozen=True) class OvernightForecast   # p_up/E涨幅度/E跌幅度（密度/8态融合注入）
@dataclass(frozen=True) class EntryCostContext    # 开仓价/支撑位/ATR14（成本优势评估）
@dataclass(frozen=True) class ExpectancyConfig    # E门槛0.5%/盈亏比1.5/成本优势2ATR
@dataclass(frozen=True) class ExpectancyDecision  # expectancy+盈亏比+成本优势+踏空成本+passed+归因
class OvernightReturnExpectancy:
    def evaluate(self, forecast, cost=None, *, miss_probability=None,
                 expected_miss_gain_pct=None) -> ExpectancyDecision
```

- **期望值**（min_build_spec 既定）：E[次日收益] = p_up×E涨 − (1−p_up)×E跌。
- **三门槛与关系**：E>0.5% ∧ 盈亏比 E涨/E跌>1.5 ∧（cost 注入时）成本优势
  =(开仓价−支撑)/ATR>2.0；E 跌=0 且 E 涨>0 → 盈亏比=+inf（文档化 MVP）。
- **踏空成本量化**：miss_probability×expected_miss_gain_pct（注册表
  P(错过)×E(错过收益)），量化输出不参与门槛；缺省 None→0.0+note。
- **门语义非异常**：passed=False+reasons 全量归因（各门槛实际值 vs 阈值），
  不抛错；仅输入非法才 ValueError。

## 2. 纪律

- p_up 越界[0,1]/非有限/E涨E跌<0/开仓价≤0/支撑≤0/ATR≤0/miss_probability
  越界/非法配置 → ValueError（fail-closed）。
- cost=None → 成本优势门槛不评估（cost_advantage_atr=None+note，不阻断
  E 与盈亏比判定；生产装配层应恒注入）。
- frozen dataclass asdict JSON 可序列化；不生产概率（上游注入）、不做 Platt
  校准、不替代 MOD-SIG-104 第一道门、不荐股。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~106 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：MOD-SIG-037 8态/密度预测
  （MOD-SIG-043）融合出 p_up/E涨/E跌；MOD-SIG-104 概率门槛放行结果（第一
  道校验，TSV dependencies 在案：conditional_density_predictor;
  next_day_8state_forecast;模块29(B10-01415)）。
- 下游候选：开仓评估装配层（E>0 才参与，注册表归属 L3+模块29联动）。

## 4. 测试

`tests/signal_ashare/test_overnight_return_expectancy.py`：
期望值公式、E>0.5% 边界、盈亏比>1.5（含 E跌=0 退化）、成本优势>2ATR
（含 cost=None 降级）、踏空成本量化、多门槛归因、非法输入 fail-closed、
frozen/JSON 契约。
