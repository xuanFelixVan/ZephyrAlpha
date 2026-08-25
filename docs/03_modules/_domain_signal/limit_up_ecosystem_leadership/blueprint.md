---
blueprint_id: MOD-SIG-097
module_name: limit_up_ecosystem_leadership
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

# MOD-SIG-097 limit_up_ecosystem_leadership 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01366（模块10 动量领导因子与涨停板生态模型，
> 裁定=做 P1）+ 候选注册表 CAND-TESTB-012。
> 代码：`src/zephyr/signal_ashare/limit_up_ecosystem_leadership.py`

## 0. 定位

场内对账：limit_up_followthrough（MOD-SIG-078）已覆盖炸板率+昨涨停今表现、
lhb_premium_analyzer（MOD-SIG-057）已覆盖龙虎榜溢价；**连板高度因子/封板时间因子/
梯队断层检测/Granger 领导-跟随系数为缺口**（深挖批 min_build_spec 明示）。
本模块为纯统计核：上游连板梯队快照与个股收益序列鸭子类型注入，不直连 DB。

与既有件边界：
- MOD-SIG-078：双池（封板/炸板）次日表现统计——管"昨天涨停的今天怎样"；
  本件管"今天涨停板生态结构"（梯队高度/封板时间/断层）+ 个股间领导-跟随，正交。
- MOD-SIG-057：席位溢价（谁在买→次日溢价系数），正交。
- cross_market_conduction_sensor：跨市场指数间 Granger 传导；本件为个股对个股
  领导-跟随 Granger，粒度与语义正交。
- Granger F 检验右尾 p 值纯 Python 正则化不完全贝塔实现——零 scipy
  （pyproject 幽灵依赖纪律，#ARCH-235 在案，与 MOD-SIG-094 同构）。

## 1. 接口

```python
@dataclass(frozen=True) class LimitUpStock          # 单票快照（symbol/consec_limit/first_seal_minute/amount）
@dataclass(frozen=True) class LadderEcosystemConfig # 阈值+查表（构造即校验）
@dataclass(frozen=True) class LadderSnapshot        # 梯队生态输出（高度/分布/断层/封板时间统计）
@dataclass(frozen=True) class LeadershipCoefficient # 领导-跟随系数输出（granger_f/p/leadership/方向）
class LimitUpEcosystemLeadership:
    def ecosystem_snapshot(self, stocks, *, trade_date=None) -> LadderSnapshot
    def leadership(self, leader_returns, follower_returns, *, max_lag=5) -> LeadershipCoefficient
```

梯队生态：
- 连板高度 = max(consec_limit)；梯队分布 = 各连板高度计数（1板/2板/…/≥height_cap板归并）。
- 梯队断层：高度≥2 的梯队中某层计数=0 而其上仍有更高层 → fault 层清单；
  断层严重度 = 断层层数/(max_height−1)。
- 封板时间因子：first_seal_minute（自 9:30 起分钟数）分布——均值/中位/
  早盘封板占比（≤seal_early_minute，默认 60 分钟即 10:30 前）；越早越强。
- 晋级成功率查表：从相邻两日梯队分布推 h→h+1 晋级率（2进3 成功率<30% → 断层预警，
  阈值可配置）；单日快照无相邻日 → promotion_rates=None 显式降级。

领导-跟随系数：
- Δleader/Δfollower 收益序列滞后 OLS F 检验（max_lag 默认 5，PIT：仅 leader 滞后项
  解释 follower 当期，无未来信息）；F 右尾 p<significance（默认 0.05）且
  leadership=Σ|β_lag|>threshold（默认 0.3）→ 领导关系成立。
- 样本 < min_samples（默认 30）→ checked=False 显式降级不阻断。

## 2. 纪律

- 梯队高度/断层层/封板分钟非法（负值/非单调）→ ValueError（fail-closed）；
  配置构造即校验（阈值>0、概率∈[0,1]、cap≥2）。
- 空梯队（当日零涨停）→ 合法空快照（max_height=0/degraded=True+notes）。
- frozen dataclass asdict JSON 可序列化；纯内存统计，不直连 DB、不荐股。

## 3. 依赖

- import：标准库（math/statistics/dataclasses）——无 zephyr 内部 import 边
  （MOD-SIG-089/092~096 同构纪律）。
- 上游注入：c1_market.limit_up_down 连板梯队快照（D_DATA 装配层）、个股收益序列
  （D_DATA/D_FACTOR）；下游候选：买入侧信号装配层/情绪页生态卡。
