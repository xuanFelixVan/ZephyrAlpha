---
blueprint_id: MOD-SIG-110
module_name: pead_event_model
domain: D_FUNDAMENTAL_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_FUNDAMENTAL_SIGNAL
path: src/zephyr/signal_fundamental/pead_event_model.py
granularity: file
---

# MOD-SIG-110 pead_event_model 蓝图（模块49 财报季事件驱动与PEAD模型）

> **module_id**: MOD-SIG-110 | **域**: D_FUNDAMENTAL_SIGNAL | **优先级**: P1
> **来源**: B10-01417（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-FUNDAMEN-001，A1交易决策架构 §4模块49）
> 代码：`src/zephyr/signal_fundamental/pead_event_model.py`

## 0. 定位

PEAD（Post-Earnings-Announcement Drift，Bernard & Thomas 1989 经典异象）
事件驱动件：**SUE 分档 + 漂移收益统计 + 财报季持仓标记**。

查重分工（W-P1-25 铁律①探查）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| financial_parser | MOD-DAT-FIN-PARSER | 财报 PDF/XBRL **解析面**（结构化三表） | 本件不解析财报原文，EPS/一致预期经注入序列消费 |
| announcement_provider | MOD-L00-004 | 公告/新闻 **采集面**（匿名源+去重写表） | 本件不采集公告，披露事件日期经入参消费 |
| calendar_event_derivations | MOD-L00-004 | 财报强制披露**截止日历**派生（4/30、8/31、10/31） | 本件复用其截止窗口语义做"财报季"判定（edge 10624669），不重算交易日 |
| ctr002 族（MOD-CON-001/002） | D_CONTRACTS | FactorSignal 生产/消费契约验证 | 本件产 PEAD 语义结果（dataclass），不直接产 FactorSignal（装配批桥接） |

TSV 裁定原文："财报截止日历已有；SUE计算+漂移收益统计为缺口（一致预期
须用免费源避免付费数据边界）"——施工形态=纯内存判定核心，一致预期/EPS/
价格序列全部 DI 注入（免费源绑定归运行时装配批，本件不触网）。

## 1. 规则（确定性，纯内存计算）

- **SUE**：`sue = (actual_eps − consensus_eps) / |consensus_eps|`；
  `|consensus_eps| < eps_floor`（默认 1e-6，零/近零预期防爆炸）→ 该事件
  `computable=False` 留痕不静默丢弃。
- **SUE 分档**（SueBand，阈值可配默认 strong_neg=−2.0 / neg=−0.5 /
  neutral=0.5 / pos=2.0，单位 σ 语义由调用方标准化后传入；原始口径按值
  直接分档）：STRONG_NEGATIVE / NEGATIVE / NEUTRAL / POSITIVE /
  STRONG_POSITIVE。
- **漂移收益统计**：事件日后 N 个交易日（默认 20）累计漂移收益
  `drift_return = close[t+N] / close[t] − 1`；价格序列长度不足 N+1 →
  `computable=False`。
- **财报季持仓标记**：披露截止窗口（4/30、8/31、10/31，遇非交易日前移，
  语义对齐 calendar_event_derivations.derive_earnings_deadline）前
  `pre_window`（默认 10）个日历日起至截止日为"财报季"；持仓标记 =
  持仓区间内与财报季窗口相交 → `earnings_season_exposure=True`。
- Fail-Closed：空 symbol / 非有限 EPS / 空价格序列 / 非正窗口参数 →
  PeadEventError；同输入必同输出（无墙钟/随机）。

## 2. 接口

```python
class SueBand(str, Enum): STRONG_NEGATIVE/NEGATIVE/NEUTRAL/POSITIVE/STRONG_POSITIVE
@dataclass(frozen=True) class EarningsEvent: symbol/announce_date/actual_eps/consensus_eps
@dataclass(frozen=True) class PeadResult: symbol/announce_date/sue/band/drift_return/drift_days/computable/detail
@dataclass(frozen=True) class EarningsSeasonMark: symbol/in_season/window_start/window_end/exposure

compute_sue(actual_eps, consensus_eps, *, eps_floor=1e-6) -> float | None
classify_sue(sue, *, thresholds=SueThresholds()) -> SueBand
compute_drift_return(closes: Sequence[float], event_index: int, *, days=20) -> float | None
evaluate_event(event: EarningsEvent, closes, event_index, *, days=20) -> PeadResult
earnings_season_window(year, month_day=(4,30)|(8,31)|(10,31), *, pre_window=10) -> EarningsSeasonMark
PeadEventError(ZephyrBaseError)  # 占位错误码 ZA-SIG-UNREGISTERED-PEAD（纪律⑦）
```

## 3. 依赖

- 设计边：`calendar_event_derivations`（node 10624669）——财报季截止窗口
  语义真源复用（不 import 重算，窗口口径注释对齐）。
- 运行时装配（非本件）：akshare 盈利预测免费接口→一致预期序列注入；
  c3 财务表实际 EPS→EarningsEvent 装配；CTR-002 FactorSignal 桥接。

## 4. 测试

`tests/signal_fundamental/test_pead_event_model.py`（[TTL] permanent）。
