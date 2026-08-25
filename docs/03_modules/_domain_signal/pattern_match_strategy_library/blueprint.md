---
blueprint_id: MOD-SIG-105
module_name: pattern_match_strategy_library
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

# MOD-SIG-105 pattern_match_strategy_library 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01416（模块44 量化模式匹配与执行策略库，裁定=做 P1）+ 候选注册表 CAND-TESTB-022。
> 代码：`src/zephyr/signal_ashare/pattern_match_strategy_library.py`

## 0. 定位

场内对账（查重铁律④⑥探查在案）：

- unified_pattern_engine（MOD-SIG-091）= **图形识别库**（六类图形 PatternEvent：
  类型+置信度+关键点位+方向+历史胜率，管"图上是什么形态"）；
- intraday_buy_sell_point_analyzer（MOD-SIG-024）= 日内买卖点**实时检测引擎**
  （6买6卖+3重确认，管"现在是不是这个点"——突破/回调/竞价弱转强模式名与
  本件买点集有交集，但语义层不同：实时检测 vs 统计门控）；
- similar_day_inference（MOD-SIG-063）= 大盘 breadth 曲线族 KNN 相似日推演
  （Pearson 距离，三档情景概率，非个股买卖点模式库）；
- clone_guard DTW = 策略指纹雷同检测（TSV 在案：语义不同，非候选落点）；
- **买卖点执行模式特征向量库 + DTW 历史案例匹配 + 胜率>50% 与 IC>0.03 双门控
  无实现**（深挖批 min_build_spec 明示缺口：模式→执行策略映射，管"这个模式
  历史上赚不赚钱、值不值得启用"），本模块落地。

## 1. 接口

```python
BUY_PATTERNS   # 买点4模式封闭集（counter_trend_dip 逆势低吸 / breakout_volume 突破买入放量>1.5x
               # / pullback_entry 回踩买入 / auction_weak_to_strong 竞价弱转强）
SELL_PATTERNS  # 卖点3模式封闭集（cvd_divergence_exit CVD背离卖出 / atr_stop_execution ATR止损
               # 机械执行 / thesis_invalidation_exit 逻辑失效无条件执行）
@dataclass(frozen=True) class PatternSpec        # 模式规格（id/方向/特征维名/语义）
@dataclass(frozen=True) class HistoricalCase     # 历史案例（pattern_id+归一化序列+前瞻收益，注入）
@dataclass(frozen=True) class PatternMatchConfig # DTW阈值/最小胜率0.50/最小IC0.03/top_k/min_cases
@dataclass(frozen=True) class CaseMatch          # 案例匹配（case_id+distance）
@dataclass(frozen=True) class PatternGateResult  # 双门控裁定（eligible+win_rate+ic+归因）
class PatternMatchStrategyLibrary:
    def list_patterns(self, side: str | None = None) -> tuple[PatternSpec, ...]
    def dtw_distance(self, a: Sequence[float], b: Sequence[float]) -> float
    def match_cases(self, query, cases, top_k=None) -> tuple[CaseMatch, ...]
    def gate_pattern(self, pattern_id, cases, *, ic_value=None) -> PatternGateResult
```

- **特征向量库**：7 模式（4买+3卖）注册即封闭集，各模式特征维名固定；
  历史案例按鸭子类型注入（pattern_id + 归一化序列 + forward_return），
  本模块不直连案例库 DB（生产接线留集成批）。
- **DTW 匹配**：纯标准库 O(n·m) Sakoe-Chiba 带约束 DTW（默认带窗 25%），
  距离=路径累计成本/路径长开方；top_k 升序截取。
- **双门控**（min_build_spec 既定）：匹配案例数≥min_cases 且胜率
  （forward_return>0 占比）≥0.50 且 IC≥0.03 → eligible=True；缺 IC
  （None）按 fail-closed 不判合格（reason 留痕 ic_missing），门语义非异常。

## 2. 纪律

- 未知 pattern_id/空序列/非有限值/非法配置（阈值越界、top_k≤0）→ ValueError
  （fail-closed）；案例 pattern_id 与查询不符 → 该案例剔除计数不抛。
- 门语义非异常：不合格=eligible=False+reason，不抛错；仅输入非法才 ValueError。
- frozen dataclass asdict JSON 可序列化；不荐股、不做实时点位检测（MOD-SIG-024
  职责）、不做图形识别（MOD-SIG-091 职责）。

## 3. 依赖

- 无 zephyr import（纯函数核，与 MOD-SIG-089/092~104 同构纪律）。
- 语义上游（鸭子类型注入，生产接线留集成批）：factor/analysis/ic_ir_calc
  （MOD-L02-002，IC 验证语义）；历史案例库（前瞻收益样本装配层）。
- 下游候选：执行策略选择器装配层（模式 eligible 后才进入实时检测链路）。

## 4. 测试

`tests/signal_ashare/test_pattern_match_strategy_library.py`：
模式封闭集注册、DTW 距离（同型零距/平移放大/带窗截断/非法输入）、案例匹配
排序与 top_k、双门控全组合（胜率/IC/案例数/缺IC fail-closed）、异 pattern
案例剔除、frozen/JSON 契约。
