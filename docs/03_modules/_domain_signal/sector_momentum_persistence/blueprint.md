---
blueprint_id: MOD-SIG-098
module_name: sector_momentum_persistence
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

# MOD-SIG-098 sector_momentum_persistence 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01367（模块11 动量层级与板块持续性模型，
> 裁定=做 P1）+ 候选注册表 CAND-TESTB-013。
> 代码：`src/zephyr/signal_ashare/sector_momentum_persistence.py`

## 0. 定位

场内对账：mainline_probability（MOD-SIG-064）= 主线概率四因子合成评分（RRG 象限/
接力阶段/资金持续性/梯队完整度，管"谁是主线"）；**动量广度判定/连板梯队层级稳定性
CV/Momentum Persistence Score/分歧恢复速度/板块-指数共振度为缺口**（深挖批
min_build_spec+注册表 problem 明示，管"主线能持续多久"）。本模块为纯统计核：
板块日收益/资金流/连板梯队/指数收益全部鸭子类型注入，不直连 DB。

与既有件边界：
- MOD-SIG-064：主线"评分"（候选榜相对强弱）；本件"持续性度量"（时间轴维度），
  上下游候选关系（064 输出板块名单 → 本件度量其持续性），语义正交。
- sector_rotation_state/sector_divergence（MOD-SIG-060）：5 状态分类与分歧度
  横截面快照；本件为单板块时序持续分+市场动量广度二态，正交。
- 资金持续性子分公式对齐 MOD-SIG-064 F3 口径（0.6×正流入日占比+0.4×尾部连正占比），
  避免同域双口径。

## 1. 接口

```python
@dataclass(frozen=True) class SectorMomentumInput   # 板块窗输入（日收益/资金流/梯队/当日梯队分布）
@dataclass(frozen=True) class MomentumPersistenceConfig  # 阈值+权重（构造即校验，权重和=1）
@dataclass(frozen=True) class SectorPersistenceScore     # 单板块持续分输出
@dataclass(frozen=True) class MarketBreadthRegime        # 市场动量广度二态输出
class SectorMomentumPersistence:
    def score_sector(self, sector, index_returns) -> SectorPersistenceScore
    def market_breadth(self, sectors) -> MarketBreadthRegime
```

单板块五维持续分（缺维按可用权重重归一，同 MOD-SIG-064 缺维先例）：
- **MPS**（Momentum Persistence Score）= 窗口正收益日占比；≥0.7 → persistent 标记。
- **资金流持续性** = 0.6×正流入日占比 + 0.4×min(尾部连续正流入天数/3, 1)。
- **梯队层级稳定性**：日最高连板高度序列 CV=σ/μ；CV≤0.3→1.0 / ≤0.5→0.7 /
  ≤0.8→0.4 / >0.8→0.1（查表）；窗内零涨停（μ=0）→ 该腿降级 None。
- **板块-指数共振度** = Pearson ρ（板块日收益 vs 指数日收益）；零方差 → None。
- **分歧恢复速度**：窗内最近分歧日（日收益≤−2% 默认）后累计收益收复所需天数，
  1d→1.0 / 2d→0.8 / 3d→0.6 / 4-5d→0.4 / >5d 或未收复→0.1；窗内无分歧 → 该腿降级。

合成：composite = Σw_i·s_i / Σw_i(可用) × 100（默认权重 mps 0.30/资金 0.25/
梯队 0.20/共振 0.15/恢复 0.10，构造校验和=1）。

市场动量广度：窗口动量（复利窗收益）>0 的板块占比；≥0.6→mainline（主线生态），
≤0.3→speculative（投机生态），其间→balanced；空板块列表 → ValueError。

## 2. 纪律

- 输入等长/≥min_window/有限值校验；梯队高度≥0；非法 → ValueError（fail-closed）。
- 配置构造即校验：阈值∈(0,1)、min_window≥5、权重键封闭集且和=1（±1e-9）。
- 缺维腿重归一不出伪分；全腿缺 → composite=None+degraded=True。
- PIT：窗口序列全部为 ≤ 当日观测；frozen dataclass asdict JSON 可序列化；
  纯内存统计不直连 DB、不荐股。

## 3. 依赖

- import：标准库（math/statistics/dataclasses）——无 zephyr 内部 import 边。
- 上游注入：mainline_candidates（MOD-SIG-061）板块名单、data/market_breadth_collector
  广度数据、c1_market.money_flow 板块资金流（D_DATA 装配层）；下游候选：
  主线持续性页签/买入侧持续性门槛。
