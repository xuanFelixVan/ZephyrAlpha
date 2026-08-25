---
blueprint_id: MOD-SIG-109
module_name: strategy_cross_vote_funnel
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

# MOD-SIG-109 strategy_cross_vote_funnel 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01504（筛选漏斗第五层：多策略交叉（60秒级，→~30），裁定=做 P1）+ 候选注册表 CAND-TESTB-026。
> 代码：`src/zephyr/signal_ashare/strategy_cross_vote_funnel.py`

## 0. 定位（R4 双视图裁定在案）

同名"第五层"双视图（W-P1-19 fragment 裁定=异→分工，各自 canonical）：

- strategy_cpcv_matrix（MOD-BT-028，D_BACKTEST，P1W19 已建）= **离线验证层**
  （CPCV 策略级打分矩阵→稳健交集，方法论面）；
- **本件 = 在线信号层**（D_ASHARE_SIGNAL，60 秒级漏斗第五层多策略交叉投票
  信号合成）——数据平面与方法论均不同，勿重复离线面。

场内对账（查重铁律①⑥探查在案）：

- 漏斗一~四层已有：MOD-SIG-086 骨架/MOD-SIG-046 一层/MOD-SIG-048 三层精筛/
  MOD-SIG-049 四层事件驱动（~50→~30 容量链上游）；**第五层多策略交叉投票
  无实现**（深挖批 min_build_spec 明示缺口），本模块落地；
- fine_scoring_engine / event_driven_screener = 上游生产方（候选池与事件
  读数注入，TSV dependencies 在案）；market_state_sensor（MOD-SIG-036，
  C-021）= 市场状态**否决门**读数上游（其自身不输出择时买卖信号，本件
  消费其 allow_buy 语义）。

## 1. 接口

```python
CORE_SEAT_WEIGHTS  # 三席封闭集（value 策略A 0.30 / momentum 策略B 0.25 / event 策略C 0.20）
EXTRA_VOTER_WEIGHTS  # 额外投票方（c034_inference C-034推演 0.10 / c036_synergy C-036合力 0.10）
VoteValue          # YES=1 / ABSTAIN=0 / NO=-1
@dataclass(frozen=True) class StrategyVote        # voter+vote（+可选 weight 覆盖）
@dataclass(frozen=True) class MarketStateClearance # C-021 鸭子类型（allow_buy+state_label）
@dataclass(frozen=True) class CrossVoteConfig     # 通过阈>0.0/容量~30/否决开关
@dataclass(frozen=True) class CrossVoteEntryResult # 单标的裁定（approved/vote_score/vetoed/归因）
@dataclass(frozen=True) class CrossVoteFunnelResult # kept/excluded/容量截断/degraded/notes
class StrategyCrossVoteFunnel:
    def evaluate_symbol(self, symbol, votes, market_state=None) -> CrossVoteEntryResult
    def run(self, candidates, votes_by_symbol, market_state=None) -> CrossVoteFunnelResult
```

- **加权投票**（注册表既定）：vote_score=Σw_i×vote_i/Σ(w_i·非弃权)，
  score>0 → approved；三席 YES/NO + C-034/C-036 额外投票方；弃权不计入
  分母（全弃权→score=0 不通过+留痕）。
- **市场状态否决门**（C-021）：allow_buy=False → vetoed=True 且 approved=False
  （一票否决，不论投票结果）；market_state=None → 否决门降级直通
  （degraded=True+note，与漏斗族降级哲学同构）。
- **容量收敛**：kept 按 vote_score 降序（同分 symbol 字典序）截断
  capacity_target（→~30，60 秒级在线运行）。

## 2. 纪律

- 未知 voter/重复 voter/非法 vote 值/权重越界/capacity≤0/空 symbol → ValueError
  （fail-closed）；候选无投票记录 → excluded（reason=no_votes）不抛。
- 门语义非异常：否决/不通过经返回值表达，不抛错；仅输入非法才 ValueError。
- kept ⊆ 输入（漏斗单调收敛不变式）；frozen dataclass asdict JSON 可序列化；
  不做离线 CPCV 验证（MOD-BT-028 职责）、不做市场状态判定（MOD-SIG-036 职责）、
  不荐股。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~108 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：fine_scoring_engine
  （MOD-SIG-048）/ event_driven_screener（MOD-SIG-049）候选池；各策略信号
  （策略A价值/B动量/C事件+C-034 推演/C-036 合力生产方）投票注入；
  market_state_sensor（MOD-SIG-036）C-021 否决读数。
- 下游候选：sleeve 排序/第六层组合优化（B10-01505，W-P1-21）输入。

## 4. 测试

`tests/signal_ashare/test_strategy_cross_vote_funnel.py`：
三席+额外投票方权重封闭集、加权投票通过与否决、弃权口径（含全弃权）、
C-021 否决门（含降级直通）、容量截断排序（~30）、无投票剔除、非法输入
fail-closed、frozen/JSON 契约。
