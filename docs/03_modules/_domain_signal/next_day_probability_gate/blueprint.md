---
blueprint_id: MOD-SIG-104
module_name: next_day_probability_gate
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

# MOD-SIG-104 next_day_probability_gate 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01415（模块29 次日上涨概率统一门槛模块，裁定=做 P1）+ 候选注册表 CAND-TESTB-021。
> 代码：`src/zephyr/signal_ashare/next_day_probability_gate.py`

## 0. 定位

场内对账（查重铁律⑤探查在案）：
- next_day_8state_forecast（MOD-SIG-037）= 8 态概率分布生产方（只出概率不出信号）；
  conditional_density_predictor = 密度预测；plan_engine/brier_calibration = Brier 校准
  ——均为上游概率生产/校准方；
- expectation_governance（D_DATA_ENG）= 数据质量期望套件门控（数据域，语义正交）；
- 筛选漏斗族（MOD-SIG-086 骨架/MOD-SIG-046 一层）= 标的池排除与评分（非概率门槛）；
- **动作分档统一概率门槛（决策链第一道门）+牛熊量能动态偏移+拦截归因与统计回写
  无实现**（深挖批 min_build_spec 明示缺口），本模块落地。

## 1. 接口

```python
GATE_ACTIONS  # 动作分档封闭集（new_position/add_position/bottom_fishing/t_plus/t_minus）
@dataclass(frozen=True) class ProbabilityGateConfig  # 分档门槛+偏移+钳制（构造即校验）
@dataclass(frozen=True) class GateContext            # 牛熊/量能/事件标记（冲突 fail-closed）
@dataclass(frozen=True) class GateDecision           # 放行/拦截+归因
@dataclass(frozen=True) class ActionGateStats / GateStatsSnapshot
class NextDayProbabilityGate:
    def evaluate(self, action: str, p_up: float, context: GateContext | None = None) -> GateDecision
    def set_block_sink(self, sink) -> None       # 拦截回写 sink（鸭子类型）
    def stats_snapshot(self) -> GateStatsSnapshot
```

- **分档门槛**：新开仓≥0.65 / 加仓≥0.60 / 抄底≥0.70 / 正T≥0.55 /
  反T=P(跌)≥0.55（方向概率口径：多头动作=p_up，t_minus=1−p_up）。
- **动态偏移**（叠加求和，钳制 [0.50,0.95]）：牛−5% / 熊+5% / 放量−5% /
  缩量+10% / 利好落地前+10% / 黑天鹅+15% / 变盘日+5% / 情绪高位+5%。
- **拦截归因**：基准门槛+各偏移+调整后门槛+缺口全量入 reason（对标 Man Group
  裁定口径）；门语义非异常——拦截=passed=False，不抛错。
- **统计回写**：内存累计 total/blocked/block_rate/avg_shortfall（供回测门槛
  合理性），可选 sink 每拦截回写一次（生产 DB 接线留集成批）。

## 2. 纪律

- 未知动作/p_up 越界[0,1]或非有限/上下文冲突（牛熊同真、放量缩量同真）/
  非法配置 → ValueError（fail-closed）。
- 调整后门槛恒钳制 [floor,cap]（默认 [0.50,0.95]）。
- frozen dataclass asdict JSON 可序列化；不直连 DB、不荐股、不进 L2 后续链路。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~103 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：MOD-SIG-037 8 态概率 /
  conditional_density_predictor 密度积分 P(r>0) / plan_engine brier_calibration
  校准后概率——p_up 由装配层融合注入。
- 下游候选：模块13 隔夜收益期望值（B10-01464，W-P1-05）消费本门为第一道校验。

## 4. 测试

`tests/signal_ashare/test_next_day_probability_gate.py`（24 用例）：
配置/上下文/输入 fail-closed、五档门槛边界、反T 方向概率、八偏移叠加与钳制、
拦截归因文本、统计累计与 sink 回写、frozen/JSON 契约。
